"""EcoHealth Sentinel agent harness.

The harness is the loop around the model: it gives the brain a fixed set of tools,
runs the tool it picks, feeds the result back, enforces guardrails, and records a trace.
Two brains plug in: RuleBrain (offline, deterministic) and LLMBrain (needs an API key, untested here).
"""
import json
import re
from aci import Aci, AciBrain, PII, ACI_SYSTEM
from agents import SCENARIOS, DEFAULT_CTX, retrieve, parse_intent, epi_agent, dpa_agent, dmo_agent

BLOCK_PRIVACY = ["patient name", "names of patients", "names and phone", "phone number", "home address", "list of patients",
                 "who are the patients", "majina ya wagonjwa", "namba ya simu"]
BLOCK_INJECTION = ["ignore previous", "ignore all instructions", "ignore your instructions", "reveal your prompt", "system prompt"]

SYSTEM = ("You are the EcoHealth Sentinel agent for district health teams in Tanzania. Use only tool results. "
          "Call parse_intent first, then get_indicators, search_policy, check_privacy and draft_plan, then final_answer. "
          "Cite policy passage ids in sources. Never output personal data. If the request is unclear or no policy source is found, "
          "use status needs_clarification or escalate. Reply in the language of the request.")


def input_guard(text):
    t = (text or "").lower()
    if any(p in t for p in BLOCK_PRIVACY):
        return "privacy", "Request refused: it asks for personal patient data. This system only returns aggregated information."
    if any(p in t for p in BLOCK_INJECTION):
        return "injection", "Request refused: instructions that override the safety rules are not accepted."
    return None, None


def output_guard(final):
    if final.get("status") == "ok":
        if not final.get("sources"):
            return {**final, "status": "escalate", "summary": "No policy source found. A human adviser must confirm the legal basis."}
        if final.get("risk") not in ("LOW", "MEDIUM", "HIGH"):
            return {**final, "status": "escalate", "summary": "Risk level could not be established. Escalate to a human adviser."}
    if PII.search(json.dumps(final, default=str)):
        return {"status": "blocked", "summary": "Output blocked: it contained something that looks like personal data."}
    return final


class RuleBrain:
    """Deterministic planner: same tool order every time, branches on tool results."""
    def __init__(self, fault=None):
        self.fault = fault

    def start(self, intent, region):
        self.intent, self.region, self.k, self.m = intent, region, 0, {}

    def _final(self, status, summary, **kw):
        self.k = 99
        return {"thought": summary, "action": "final_answer", "args": {"status": status, "summary": summary, **kw}}

    def next(self, obs):
        m, k = self.m, self.k
        if k == 0:
            self.k = 1
            return {"thought": "Work out which situation the request describes", "action": "parse_intent", "args": {"text": self.intent}}
        if k == 1:
            m["sc"] = (obs or {}).get("scenario")
            if not m["sc"]:
                return self._final("needs_clarification", "I could not tell which health situation you mean. Name cholera, immunization, medicine stockout or maternal emergency.")
            self.k = 2
            return {"thought": "Check indicators against targets", "action": "get_indicators", "args": {"region": (self.region.lower() + " ") if self.fault == "bad_region" else self.region,
                                                                                                 "scenario": (SCENARIOS[m["sc"]]["en"] + " outbreak") if self.fault == "wrong_scenario" else m["sc"]}}
        if k == 2:
            if "error" in obs:
                return self._final("needs_clarification", f"Data problem: {obs['error']}")
            m["risk"] = obs["risk"]
            if self.fault == "skip_search":
                m["sources"] = []
                self.k = 4
                return {"thought": "Check privacy limits", "action": "check_privacy", "args": {"region": self.region, "scenario": m["sc"]}}
            self.k = 3
            return {"thought": "Find the policy basis", "action": "search_policy", "args": {"query": SCENARIOS[m["sc"]]["rag_query" if getattr(self, "use_rag", False) else "query"]}}
        if k == 3:
            m["sources"] = [h["id"] for h in obs.get("hits", [])]
            self.k = 4
            return {"thought": "Check privacy limits", "action": "check_privacy", "args": {"region": self.region, "scenario": m["sc"]}}
        if k == 4:
            m["privacy"] = obs.get("stance", "")
            self.k = 5
            return {"thought": "Draft the action plan", "action": "draft_plan", "args": {"region": self.region, "scenario": m["sc"]}}
        if k == 5:
            m["plan"] = obs.get("plan", [])
            self.k = 99
            summary = f"{self.region}: risk {m['risk']}. {len(m['sources'])} policy source(s) cited. Privacy: {m['privacy']}."
            if self.fault == "fake_citation":
                m["sources"] = ["FAKE-1"]
            if self.fault == "wrong_risk":
                m["risk"] = "LOW" if m["risk"] != "LOW" else "HIGH"
            return {"thought": "All evidence gathered, answer now", "action": "final_answer",
                    "args": {"status": "ok", "risk": m["risk"], "plan": m["plan"], "sources": m["sources"], "privacy": m["privacy"], "summary": summary}}
        return self._final("escalate", "Planner state error.")


_RS = {"region": {"type": "string"}, "scenario": {"type": "string", "enum": list(SCENARIOS)}}
TOOL_SCHEMAS = [
    {"name": "parse_intent", "description": "Identify the health situation in the request: cholera, immunization, stockout or maternal. Returns null if none.",
     "input_schema": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}},
    {"name": "get_indicators", "description": "Aggregate indicator values, off target flags and risk for a region and scenario.",
     "input_schema": {"type": "object", "properties": _RS, "required": ["region", "scenario"]}},
    {"name": "search_policy", "description": "Search the policy knowledge base. Returns passages with ids.",
     "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "check_privacy", "description": "Data protection stance for this scenario.",
     "input_schema": {"type": "object", "properties": _RS, "required": ["region", "scenario"]}},
    {"name": "draft_plan", "description": "Draft the district action plan for this scenario.",
     "input_schema": {"type": "object", "properties": _RS, "required": ["region", "scenario"]}},
    {"name": "final_answer", "description": "Give the final answer and stop.",
     "input_schema": {"type": "object", "properties": {"status": {"type": "string", "enum": ["ok", "needs_clarification", "escalate"]},
                      "risk": {"type": "string"}, "plan": {"type": "array", "items": {"type": "string"}},
                      "sources": {"type": "array", "items": {"type": "string"}}, "privacy": {"type": "string"}, "summary": {"type": "string"}},
                      "required": ["status", "summary"]}},
]


class LLMBrain:
    """Language model planner using Anthropic tool use. Not tested in the build environment."""
    def __init__(self, api_key, model="claude-sonnet-5-5"):
        import anthropic
        self.client, self.model = anthropic.Anthropic(api_key=api_key), model
        self.schemas, self.system = TOOL_SCHEMAS, SYSTEM

    def set_tools(self, schemas, system):
        self.schemas, self.system = schemas, system

    def start(self, intent, region):
        self.messages, self.pending = [{"role": "user", "content": f"Region: {region}. Request: {intent}"}], None

    def next(self, obs):
        if self.pending:
            self.messages.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": self.pending, "content": json.dumps(obs, default=str)}]})
        r = self.client.messages.create(model=self.model, max_tokens=800, system=self.system, tools=self.schemas, messages=self.messages,
                                        tool_choice={"type": "auto", "disable_parallel_tool_use": True})
        self.messages.append({"role": "assistant", "content": r.content})
        thought = " ".join(b.text for b in r.content if b.type == "text")
        for b in r.content:
            if b.type == "tool_use":
                self.pending = b.id
                return {"thought": thought, "action": b.name, "args": dict(b.input)}
        self.pending = None
        return {"thought": thought, "action": "final_answer", "args": {"status": "escalate", "summary": thought or "No answer produced."}}


class Harness:
    def __init__(self, regions, ctx=None, toolset="legacy"):
        self.toolset = toolset
        self.regions = regions
        self.ctx = ctx or DEFAULT_CTX
        self.tools = {"parse_intent": self.t_parse, "get_indicators": self.t_ind, "search_policy": self.t_search,
                      "check_privacy": self.t_priv, "draft_plan": self.t_plan}

    def _data(self, region):
        if region not in self.regions:
            raise KeyError(f"unknown region {region}")
        return self.regions[region]

    @staticmethod
    def _sc(scenario):
        if scenario not in SCENARIOS:
            raise KeyError(f"unknown scenario {scenario}")
        return scenario

    def t_parse(self, text): return {"scenario": parse_intent(text)}
    def t_search(self, query): return {"hits": retrieve(query, kb=self.ctx["kb"], index=self.ctx.get("index"))[0]}

    def t_ind(self, region, scenario):
        epi = epi_agent(self._sc(scenario), self._data(region), self.ctx)
        return {"scenario": scenario, "checks": epi["steps"][:-1], "risk": epi["risk"]}

    def t_priv(self, region, scenario):
        dpa = dpa_agent(self._sc(scenario), self._data(region), self.ctx)
        return {"stance": dpa["stance"], "privacy_risk": dpa["risk"]}

    def t_plan(self, region, scenario):
        d, sc = self._data(region), self._sc(scenario)
        return {"plan": dmo_agent(sc, d, epi_agent(sc, d, self.ctx), dpa_agent(sc, d, self.ctx))["plan"]}

    def run(self, intent, region, brain=None, max_steps=8):
        trace = []
        kind, msg = input_guard(intent)
        if kind:
            return {"status": "refused", "summary": msg, "guard": kind, "trace": trace, "steps": 0}
        aci = Aci(self.regions, self.ctx, max_steps) if self.toolset == "aci" else None
        brain = brain or (AciBrain() if aci else RuleBrain())
        if aci and hasattr(brain, "set_tools"):
            brain.set_tools(aci.schemas(), ACI_SYSTEM)
        brain.use_rag = self.ctx.get("index") is not None
        brain.start(intent, region)
        obs, final = None, None
        for i in range(1, max_steps + 1):
            try:
                d = brain.next(obs)
            except Exception as e:
                final = {"status": "escalate", "summary": f"Brain error: {e}"}
                break
            entry = {"step": i, "thought": d.get("thought", ""), "action": d["action"], "args": d["args"], "observation": None}
            trace.append(entry)
            if aci:
                obs = entry["observation"] = aci.call(d["action"], d["args"])
                if d["action"] == "final_answer" and obs.get("ok"):
                    final = obs["result"]
                    break
                continue
            if d["action"] == "final_answer":
                final = d["args"]
                break
            tool = self.tools.get(d["action"])
            try:
                obs = tool(**d["args"]) if tool else {"error": f"unknown tool {d['action']}"}
            except Exception as e:
                obs = {"error": str(e)}
            entry["observation"] = obs
        if final is None:
            final = {"status": "escalate", "summary": f"Stopped after {max_steps} steps without an answer."}
        final = output_guard(final)
        return {**final, "trace": trace, "steps": len(trace)}
