"""Agent computer interface (ACI) for EcoHealth Sentinel.

Design rules, in the spirit of SWE-agent:
1. Few tools, one per decision (6 tools, each does a whole job).
2. Forgiving inputs: region and scenario are normalised, and near misses are corrected with a note.
3. Short outputs: capped lists, snippets instead of full text, ids that can be opened on demand.
4. Structured errors: every failure has a code, the valid options and a fix, so an agent can recover without guessing.
5. A linter on the final answer: risk must match the tool result and every citation must have been retrieved.
6. Read only, aggregate only: no tool can reach personal data.
"""
import re
import json
import difflib
from agents import SCENARIOS, DEFAULT_CTX, retrieve, parse_intent, epi_agent, dpa_agent, dmo_agent

PII = re.compile(r"(\+?\d[\d\s\-]{8,}\d)|([\w.]+@[\w.]+\.\w+)")
STATUSES = ["ok", "needs_clarification", "escalate"]
ACI_SYSTEM = ("You are the EcoHealth Sentinel agent for district health teams. Work in this order: identify_situation, get_indicators, search_policy, "
              "get_response_plan, final_answer. Follow the hint in each result. Cite only passage ids returned by search_policy or open_passage. "
              "If search finds nothing, finish with status escalate. If the request is unclear, finish with status needs_clarification. "
              "Never include personal data. Reply in the language of the request.")


class Aci:
    def __init__(self, regions, ctx=None, max_steps=8):
        self.regions, self.ctx, self.max, self.n = regions, ctx or DEFAULT_CTX, max_steps, 0
        self.s = {"scenario": None, "region": None, "risk": None, "retrieved": [], "queries": set(), "searched": False}
        idx = self.ctx.get("index")
        if idx is not None:
            self.lookup = {c["id"]: {"source": f"{c['title']}, page {c['page']}", "text": c["text"]} for c in idx.chunks}
        else:
            self.lookup = {p["id"]: {"source": p["source"], "text": p["text"]} for p in self.ctx["kb"]}
        self.tools = {"identify_situation": self._identify, "get_indicators": self._indicators, "search_policy": self._search,
                      "open_passage": self._open, "get_response_plan": self._plan, "final_answer": self._final}

    # ---------------------------------------------------------------- envelopes
    @staticmethod
    def _ok(result, hint=None, note=None):
        out = {"ok": True, "result": result}
        if hint:
            out["hint"] = hint
        if note:
            out["note"] = note
        return out

    @staticmethod
    def _err(error, code, valid=None, fix=None):
        out = {"ok": False, "error": error, "code": code}
        if valid is not None:
            out["valid"] = valid
        if fix:
            out["fix"] = fix
        return out

    def call(self, name, args):
        self.n += 1
        left = self.max - self.n
        fn = self.tools.get(name)
        if fn is None:
            out = self._err(f"Unknown tool {name}.", "unknown_tool", valid=list(self.tools), fix="Call one of the valid tools.")
        else:
            try:
                out = fn(**(args or {}))
            except TypeError as e:
                out = self._err(f"Bad arguments: {e}", "bad_args", fix="Check the tool description for the required fields.")
        out["steps_left"] = left
        if left <= 1 and name != "final_answer" and out.get("ok"):
            out["hint"] = (out.get("hint", "") + " Few steps left: call final_answer now.").strip()
        return out

    def schemas(self):
        regions = list(self.regions)
        sc = list(SCENARIOS)
        obj = lambda props, req: {"type": "object", "properties": props, "required": req}
        return [
            {"name": "identify_situation", "description": "Use first. Map the user's request to one situation: cholera, immunization, stockout or maternal.",
             "input_schema": obj({"text": {"type": "string"}}, ["text"])},
            {"name": "get_indicators", "description": "Use second. Aggregate indicator status against national targets and the risk level for one region and situation.",
             "input_schema": obj({"region": {"type": "string", "enum": regions}, "scenario": {"type": "string", "enum": sc}}, ["region", "scenario"])},
            {"name": "search_policy", "description": "Search the policy documents with a short query of 2 to 4 words. Returns up to 5 snippets with ids. Do not paste the whole request.",
             "input_schema": obj({"query": {"type": "string"}, "k": {"type": "integer", "minimum": 1, "maximum": 5}}, ["query"])},
            {"name": "open_passage", "description": "Read one passage in full by id. Use only when a snippet is not enough.",
             "input_schema": obj({"id": {"type": "string"}}, ["id"])},
            {"name": "get_response_plan", "description": "Get the action plan and the privacy limits for one region and situation.",
             "input_schema": obj({"region": {"type": "string", "enum": regions}, "scenario": {"type": "string", "enum": sc}}, ["region", "scenario"])},
            {"name": "final_answer", "description": "Finish. Risk must match get_indicators. Sources must be ids you retrieved. Use status escalate if no passage was found.",
             "input_schema": obj({"status": {"type": "string", "enum": STATUSES}, "risk": {"type": "string"}, "plan": {"type": "array", "items": {"type": "string"}},
                                  "sources": {"type": "array", "items": {"type": "string"}}, "privacy": {"type": "string"}, "summary": {"type": "string"}}, ["status", "summary"])}]

    # ---------------------------------------------------------------- normalisation
    def _region(self, region):
        key = str(region or "").strip()
        if key in self.regions:
            return key, None
        low = {n.lower(): n for n in self.regions}
        if key.lower() in low:
            return low[key.lower()], f"Interpreted '{region}' as '{low[key.lower()]}'."
        close = difflib.get_close_matches(key.lower(), list(low), n=1, cutoff=0.8)
        return (low[close[0]], f"Interpreted '{region}' as '{low[close[0]]}'.") if close else (None, None)

    @staticmethod
    def _scenario(value):
        key = str(value or "").strip().lower()
        if key in SCENARIOS:
            return key, None
        alias = parse_intent(key)
        if alias:
            return alias, f"Interpreted '{value}' as '{alias}'."
        close = difflib.get_close_matches(key, list(SCENARIOS), n=1, cutoff=0.7)
        return (close[0], f"Interpreted '{value}' as '{close[0]}'.") if close else (None, None)

    def _resolve(self, region, scenario):
        r, n1 = self._region(region)
        if r is None:
            return None, None, None, self._err(f"Unknown region '{region}'.", "bad_region", valid=list(self.regions), fix="Use one of the valid regions.")
        s, n2 = self._scenario(scenario)
        if s is None:
            return None, None, None, self._err(f"Unknown situation '{scenario}'.", "bad_scenario", valid=list(SCENARIOS), fix="Use one of the valid situations.")
        return r, s, " ".join(x for x in (n1, n2) if x) or None, None

    # ---------------------------------------------------------------- tools
    def _identify(self, text):
        sc = parse_intent(text)
        if not sc:
            return self._err("No health situation recognised in the request.", "no_situation", valid=list(SCENARIOS),
                             fix="Ask the user to name one situation, or call final_answer with status needs_clarification.")
        self.s["scenario"] = sc
        return self._ok({"scenario": sc, "label": SCENARIOS[sc]["en"]}, hint="Next: get_indicators(region, scenario).")

    def _indicators(self, region, scenario):
        r, s, note, err = self._resolve(region, scenario)
        if err:
            return err
        epi = epi_agent(s, self.regions[r], self.ctx)
        self.s.update(region=r, scenario=s, risk=epi["risk"])
        return self._ok({"region": r, "scenario": s, "risk": epi["risk"], "checks": epi["steps"][:-1][:6]},
                        hint="Next: search_policy with a short query, for example '" + SCENARIOS[s]["rag_query"] + "'.", note=note)

    def _search(self, query, k=3):
        q = str(query or "").strip()
        if not q:
            return self._err("Empty query.", "bad_query", fix="Give 2 to 4 keywords, for example 'cholera outbreak response'.")
        k = max(1, min(5, int(k or 3)))
        repeat = q.lower() in self.s["queries"]
        self.s["queries"].add(q.lower())
        self.s["searched"] = True
        hits, _ = retrieve(q, k, kb=self.ctx["kb"], index=self.ctx.get("index"))
        passages = []
        for h in hits[:k]:
            if h["id"] not in self.s["retrieved"]:
                self.s["retrieved"].append(h["id"])
            snip = h["text"][:220].rsplit(" ", 1)[0] + ("..." if len(h["text"]) > 220 else "")
            passages.append({"id": h["id"], "source": h["source"], "snippet": snip, "score": h["score"]})
        if not passages:
            return self._ok({"passages": []}, hint="Nothing matched. Try 2 to 3 different keywords, or call final_answer with status escalate.")
        hint = "Already searched this query. Move on to get_response_plan." if repeat else "Next: get_response_plan. Use open_passage(id) only if a snippet is not enough."
        return self._ok({"passages": passages}, hint=hint)

    def _open(self, id):
        p = self.lookup.get(str(id))
        if p is None:
            return self._err(f"No passage with id '{id}'.", "bad_id", valid=self.s["retrieved"][:5], fix="Use an id returned by search_policy.")
        if id not in self.s["retrieved"]:
            self.s["retrieved"].append(id)
        return self._ok({"id": id, "source": p["source"], "text": p["text"][:1200]})

    def _plan(self, region, scenario):
        r, s, note, err = self._resolve(region, scenario)
        if err:
            return err
        d = self.regions[r]
        epi, dpa = epi_agent(s, d, self.ctx), dpa_agent(s, d, self.ctx)
        plan = dmo_agent(s, d, epi, dpa)["plan"][:5]
        return self._ok({"plan": plan, "privacy": dpa["stance"], "risk": epi["risk"]},
                        hint="Next: final_answer(status='ok', risk, plan, sources=ids from search_policy, privacy, summary).", note=note)

    def _final(self, status="", summary="", risk=None, plan=None, sources=None, privacy="", **_):
        if status not in STATUSES:
            return self._err(f"Invalid status '{status}'.", "bad_status", valid=STATUSES, fix="Choose one of the valid statuses.")
        plan = [plan] if isinstance(plan, str) else list(plan or [])
        sources = [sources] if isinstance(sources, str) else list(sources or [])
        out = {"status": status, "summary": str(summary)[:400], "risk": risk, "plan": [str(p)[:200] for p in plan[:6]], "sources": sources, "privacy": str(privacy)[:300]}
        if PII.search(json.dumps(out)):
            return self._err("The answer contains something that looks like personal data.", "pii", fix="Remove it and resubmit aggregate information only.")
        if status != "ok":
            return self._ok(out)
        if not self.s["risk"]:
            return self._err("Indicators were never checked.", "missing_step", fix="Call get_indicators first, then resubmit.")
        if risk != self.s["risk"]:
            return self._err(f"Risk '{risk}' does not match the tool result.", "risk_mismatch", valid=[self.s["risk"]], fix=f"Use risk {self.s['risk']}.")
        if not sources:
            if self.s["searched"]:
                return self._err("No passage was retrieved to support the answer.", "no_evidence", fix="Use status escalate.")
            return self._err("No policy evidence was gathered.", "missing_step", fix="Call search_policy first, then cite the ids it returns.")
        bad = [x for x in sources if x not in self.s["retrieved"]]
        if bad:
            return self._err(f"These sources were never retrieved: {', '.join(bad)}.", "bad_source", valid=self.s["retrieved"][:5],
                             fix="Cite only ids returned by search_policy or open_passage.")
        if not out["plan"]:
            return self._err("The plan is empty.", "missing_step", fix="Call get_response_plan and include its plan.")
        return self._ok(out)


# ------------------------------------------------------------------ scripted brain that follows the ACI and recovers from structured errors
class AciBrain:
    """Deterministic planner for the ACI. `fault` injects one realistic agent mistake so recovery can be tested."""

    def __init__(self, fault=None):
        self.fault = fault

    def start(self, intent, region):
        self.intent, self.region, self.k, self.m, self.retried, self.tries, self.faulted = intent, region, 0, {}, False, 0, False

    def _final(self, status, summary):
        self.k = 99
        return {"thought": summary, "action": "final_answer", "args": {"status": status, "summary": summary}}

    def _submit(self):
        m = self.m
        risk, sources = m["risk"], list(m.get("sources", []))
        if not self.faulted:
            if self.fault == "fake_citation":
                sources = ["FAKE-1"]
            if self.fault == "wrong_risk":
                risk = "LOW" if risk != "LOW" else "HIGH"
            self.faulted = True
        self.k = 5
        return {"thought": "Submit the answer", "action": "final_answer",
                "args": {"status": "ok", "risk": risk, "plan": m["plan"], "sources": sources, "privacy": m["privacy"],
                         "summary": f"{self.region}: risk {m['risk']}. {len(m.get('sources', []))} policy source(s). Privacy: {m['privacy']}."[:400]}}

    def _indicators_call(self, region, scenario):
        self.k = 2
        return {"thought": "Check indicators against targets", "action": "get_indicators", "args": {"region": region, "scenario": scenario}}

    def next(self, obs):
        m, k = self.m, self.k
        if k == 0:
            self.k = 1
            return {"thought": "Work out which situation the request describes", "action": "identify_situation", "args": {"text": self.intent}}
        if k == 1:
            if not obs.get("ok"):
                return self._final("needs_clarification", "I could not tell which situation you mean. Name cholera, immunization, medicine stockout or maternal emergency.")
            m["sc"] = obs["result"]["scenario"]
            region = self.region.lower() + " " if self.fault == "bad_region" else self.region
            scenario = SCENARIOS[m["sc"]]["en"] + " outbreak" if self.fault == "wrong_scenario" else m["sc"]
            return self._indicators_call(region, scenario)
        if k == 2:
            if not obs.get("ok"):
                valid = obs.get("valid") or []
                if not self.retried and valid and obs.get("code") in ("bad_region", "bad_scenario"):
                    self.retried = True
                    want = self.region if obs["code"] == "bad_region" else m["sc"]
                    pick = difflib.get_close_matches(str(want).lower(), [v.lower() for v in valid], n=1, cutoff=0.75)
                    if pick:
                        value = next(v for v in valid if v.lower() == pick[0])
                        return self._indicators_call(value if obs["code"] == "bad_region" else self.region, m["sc"] if obs["code"] == "bad_region" else value)
                return self._final("needs_clarification", f"{obs.get('error', 'Data problem.')} Valid options: {', '.join(valid[:8])}.")
            m["risk"] = obs["result"]["risk"]
            self.region = obs["result"]["region"]
            if self.fault == "skip_search":
                self.k = 4
                return {"thought": "Get the plan", "action": "get_response_plan", "args": {"region": self.region, "scenario": m["sc"]}}
            self.k = 3
            q = SCENARIOS[m["sc"]]["rag_query" if getattr(self, "use_rag", False) else "query"]
            return {"thought": "Find the policy basis", "action": "search_policy", "args": {"query": q}}
        if k == 3:
            m["sources"] = [p["id"] for p in (obs.get("result") or {}).get("passages", [])]
            if "plan" in m:
                return self._submit()
            self.k = 4
            return {"thought": "Get the plan", "action": "get_response_plan", "args": {"region": self.region, "scenario": m["sc"]}}
        if k == 4:
            m["plan"] = obs["result"]["plan"]
            m["privacy"] = obs["result"]["privacy"]
            return self._submit()
        if k == 5:  # the final answer was rejected: read the structured error and repair
            self.tries += 1
            code = obs.get("code")
            if self.tries > 2:
                return self._final("escalate", "Could not produce a valid answer.")
            if code == "bad_source":
                m["sources"] = obs.get("valid", [])[:3]
                return self._submit()
            if code == "risk_mismatch":
                m["risk"] = obs["valid"][0]
                return self._submit()
            if code == "missing_step":
                self.k = 3
                q = SCENARIOS[m["sc"]]["rag_query" if getattr(self, "use_rag", False) else "query"]
                return {"thought": "Gather the missing evidence", "action": "search_policy", "args": {"query": q}}
            return self._final("escalate", obs.get("fix") or "Could not produce a valid answer.")
        return self._final("escalate", "Planner state error.")


# ------------------------------------------------------------------ contract tests: does the interface behave as designed?
def aci_selftests(regions, ctx=None):
    ctx = ctx or DEFAULT_CTX
    reg = next(iter(regions))
    rows = []

    def check(name, cond):
        rows.append({"test": name, "pass": bool(cond)})

    a = Aci(regions, ctx)
    r = a.call("get_indicators", {"region": f"  {reg.lower()} ", "scenario": "cholera"})
    check("Region is normalised and the correction is reported", r["ok"] and r["result"]["region"] == reg and "note" in r)
    r = a.call("get_indicators", {"region": reg + "x", "scenario": "cholera"})
    check("A near miss region is corrected", r["ok"] and r["result"]["region"] == reg)
    r = a.call("get_indicators", {"region": "Atlantis", "scenario": "cholera"})
    check("An unknown region returns the valid options", (not r["ok"]) and r["code"] == "bad_region" and reg in r["valid"])
    r = a.call("get_indicators", {"region": reg, "scenario": "kipindupindu"})
    check("A Kiswahili scenario name is understood", r["ok"] and r["result"]["scenario"] == "cholera")
    r = a.call("search_policy", {"query": "cholera outbreak response", "k": 99})
    check("Search is capped at 5 short snippets", r["ok"] and len(r["result"]["passages"]) <= 5 and all(len(p["snippet"]) <= 225 for p in r["result"]["passages"]))
    r2 = a.call("search_policy", {"query": "cholera outbreak response"})
    check("A repeated search gets a hint to move on", "Already searched" in r2.get("hint", ""))
    r = a.call("final_answer", {"status": "ok", "risk": a.s["risk"], "plan": ["x"], "sources": ["FAKE-1"], "summary": "s"})
    check("A final answer citing an unretrieved source is rejected", (not r["ok"]) and r["code"] == "bad_source")
    wrong = "LOW" if a.s["risk"] != "LOW" else "HIGH"
    r = a.call("final_answer", {"status": "ok", "risk": wrong, "plan": ["x"], "sources": a.s["retrieved"][:1], "summary": "s"})
    check("A final answer with the wrong risk is rejected", (not r["ok"]) and r["code"] == "risk_mismatch")
    r = a.call("final_answer", {"status": "ok", "risk": a.s["risk"], "plan": ["x"], "sources": a.s["retrieved"][:1], "summary": "call +255 766 849 993"})
    check("A final answer with a phone number is rejected", (not r["ok"]) and r["code"] == "pii")
    b = Aci(regions, ctx, max_steps=3)
    b.call("identify_situation", {"text": "cholera"})
    r = b.call("get_indicators", {"region": reg, "scenario": "cholera"})
    check("A low step budget adds a hint to finish", "Few steps left" in r.get("hint", ""))
    r = Aci(regions, ctx).call("delete_database", {})
    check("An unknown tool returns the valid tool list", (not r["ok"]) and r["code"] == "unknown_tool")
    check("No tool name can reach personal data", not any(w in t for t in a.tools for w in ("patient", "phone", "name", "address")))
    return rows
