"""EcoHealth Sentinel: multi agent demo and ITU Y.3172 pipeline view.

Knowledge base entries below are short PLACEHOLDER paraphrases.
Replace them with text taken from the official documents before submission.
"""
import time
import json
import numpy as np

# ------------------------------------------------------------------
# Knowledge base (replace text with official passages, keep the ids)
# ------------------------------------------------------------------
from packs import load_pack, context

DEFAULT_CTX = context(load_pack("tz"))
KB = DEFAULT_CTX["kb"]  # default knowledge base (Tanzania pack)


def retrieve(query, k=3, kb=None, index=None):
    if index is not None:
        return index.search(query, k), index.method
    kb = kb or KB
    """Vector search over the knowledge base. Falls back to keyword overlap."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        vec = TfidfVectorizer(stop_words="english")
        m = vec.fit_transform([d["text"] for d in kb] + [query])
        sims = cosine_similarity(m[-1], m[:-1]).ravel()
        method = "TF-IDF vectors with cosine similarity"
    except Exception:
        q = set(query.lower().split())
        sims = np.array([len(q & set(d["text"].lower().split())) / (len(q) or 1) for d in kb])
        method = "keyword overlap (add scikit-learn for vector search)"
    idx = np.argsort(-sims)[:k]
    return [dict(kb[i], score=round(float(sims[i]), 2)) for i in idx if sims[i] > 0], method


# ------------------------------------------------------------------
# Scenarios
# ------------------------------------------------------------------
SCENARIOS = {
    "cholera": {"en": "Cholera spike", "sw": "Mlipuko wa kipindupindu", "query": "cholera outbreak response water sanitation report district", "rag_query": "cholera outbreak response", "personal": True,
                "checks": [("cholera", "Cholera cases", 0, "lower"), ("mal", "Malaria per 1k", 50, "lower")],
                "actions": ["Notify the District Medical Officer within 24 hours", "Open treatment points and distribute chlorine", "Deploy WASH teams and community messaging", "Assess oral cholera vaccine need"]},
    "immunization": {"en": "Immunization gap", "sw": "Pengo la chanjo", "query": "immunization coverage gap outreach campaign", "rag_query": "immunization coverage", "personal": False,
                     "checks": [("fic", "Fully immunized %", 90, "higher"), ("penta_drop", "Penta3 dropout %", 5, "lower")],
                     "actions": ["List low coverage wards from DHIS2", "Plan mop up outreach with CHWs", "Check vaccine cold chain stock"]},
    "stockout": {"en": "Medicine stockout", "sw": "Uhaba wa dawa", "query": "essential medicine stockout escalate regional store", "rag_query": "essential medicines availability", "personal": False,
                 "checks": [("stockout", "Stockout %", 5, "lower"), ("hw", "Health workers per 1k", 0.45, "higher")],
                 "actions": ["Escalate to the regional medical store", "Redistribute stock between facilities", "Agree a replenishment date"]},
    "maternal": {"en": "Maternal emergency", "sw": "Dharura ya uzazi", "query": "maternal emergency referral skilled birth", "rag_query": "maternal health skilled birth attendance", "personal": True,
                 "checks": [("mmr", "Maternal mortality per 100k", 70, "lower"), ("sba", "Skilled birth %", 90, "higher"), ("anc4", "ANC 4+ %", 80, "higher")],
                 "actions": ["Activate referral and ambulance transport", "Alert the referral hospital obstetric team", "Reinforce ANC follow up in weak wards"]},
}

INTENT_WORDS = {"cholera": ["cholera", "kipindupindu"], "immunization": ["vaccine", "immun", "chanjo"],
                "stockout": ["stock", "medicine", "dawa"], "maternal": ["maternal", "birth", "mama", "uzazi"]}


def parse_intent(text):
    t = (text or "").lower()
    for key, words in INTENT_WORDS.items():
        if any(w in t for w in words):
            return key
    return None


TOLERANCE = 0.05  # a value within 5% of its target still counts as on target


def _off(val, target, direction):
    if direction == "lower":
        return val > target * (1 + TOLERANCE)
    return val < target * (1 - TOLERANCE)


def _missed(val, target, direction):
    return val > target if direction == "lower" else val < target


CHOLERA_ALERT = 100  # demo alert level: replace with the national cholera alert definition


def assess(checks, values, alert=None):
    """Shared risk rule used by the agents and the pipeline."""
    alert = CHOLERA_ALERT if alert is None else alert
    items, off = [], 0
    for key, label, target, direction in checks:
        v = values[key]
        bad = _off(v, target, direction)
        off += bad
        state = "OFF TARGET" if bad else ("within 5% tolerance" if _missed(v, target, direction) else "on target")
        items.append({"key": key, "label": label, "value": v, "target": target, "direction": direction, "state": state})
    n = len(checks)
    share = off / n if n else 0
    level = "LOW" if share < 0.25 else "MEDIUM" if share < 0.6 else "HIGH"
    override = any(k == "cholera" for k, *_ in checks) and values["cholera"] > alert
    if override:
        level = "HIGH"
    return {"level": level, "off": off, "n": n, "items": items, "override": override, "alert": alert}


# ------------------------------------------------------------------
# Agents: each returns visible reasoning steps plus a stance
# ------------------------------------------------------------------
def checks_for(sc, ctx=None):
    """Scenario checks with the country pack targets applied."""
    t = (ctx or DEFAULT_CTX)["targets"]
    out = []
    for key, label, target, direction in SCENARIOS[sc]["checks"]:
        if key in t:
            target, direction = t[key]
        out.append((key, label, target, direction))
    return out


def pipe_checks(ctx=None):
    seen, out = set(), []
    for sc in SCENARIOS:
        for c in checks_for(sc, ctx):
            if c[0] not in seen:
                seen.add(c[0])
                out.append(c)
    return out


def epi_agent(sc, data, ctx=None):
    a = assess(checks_for(sc, ctx), data, (ctx or DEFAULT_CTX)["cholera_alert"])
    sign = {"lower": "<=", "higher": ">="}
    steps = [f"{i['label']}: {i['value']} against target {sign[i['direction']]} {i['target']}, {i['state']}" for i in a["items"]]
    if a["override"]:
        steps.append(f"Cholera cases are above the alert level of {a['alert']} (demo value), so risk is raised to HIGH")
    risk = a["level"]
    steps.append(f"{a['off']} indicator(s) off target, so epidemiological risk is {risk}")
    wants = "Case level reporting for fast tracing" if SCENARIOS[sc]["personal"] and risk != "LOW" else "Aggregated ward level reporting"
    return {"agent": "Epidemiology agent", "steps": steps, "stance": wants, "risk": risk, "cites": []}


def policy_agent(sc, data, ctx=None):
    c = ctx or DEFAULT_CTX
    q = SCENARIOS[sc]["rag_query"] if c.get("index") is not None else SCENARIOS[sc]["query"]
    hits, method = retrieve(q, kb=c["kb"], index=c.get("index"))
    steps = [f"Query: {q}", f"Method: {method}"]
    steps += [f"Match {h['id']} ({h['source']}), score {h['score']}" for h in hits] or ["No matching passage found"]
    stance = "Follow national response and reporting rules" if hits else "No policy basis found, escalate to a human adviser"
    return {"agent": "Policy and legal adviser", "steps": steps, "stance": stance, "risk": "n/a", "cites": hits}


def dpa_agent(sc, data, ctx=None):
    hits, _ = retrieve("personal data lawful basis sharing third parties", k=2, kb=(ctx or DEFAULT_CTX)["kb"], index=(ctx or DEFAULT_CTX).get("index"))
    personal = SCENARIOS[sc]["personal"]
    steps = [f"Scenario needs personal data: {personal}"] + [f"Checked {h['id']} ({h['source']})" for h in hits]
    if personal:
        steps.append("Rule: personal data only with a lawful basis, minimum fields, no third party sharing")
        stance, risk = "Allow line lists only with lawful basis and minimum fields, share aggregates beyond the district", "MEDIUM"
    else:
        steps.append("Aggregated data is enough, so no personal data is needed")
        stance, risk = "Aggregated data only", "LOW"
    return {"agent": "Data protection authority agent", "steps": steps, "stance": stance, "risk": risk, "cites": hits}


def dmo_agent(sc, data, epi, dpa):
    steps = [f"Read epidemiology risk: {epi['risk']}", f"Read privacy constraint: {dpa['stance']}"]
    plan = list(SCENARIOS[sc]["actions"])
    if epi["risk"] == "LOW":
        plan = ["Keep routine monitoring"] + plan[:1]
        steps.append("Risk is low, so only routine monitoring is proposed")
    else:
        steps.append(f"Risk is {epi['risk']}, so the full action plan is proposed")
    return {"agent": "District Medical Officer (institutional agent)", "steps": steps, "stance": "; ".join(plan), "risk": epi["risk"], "cites": [], "plan": plan}


def orchestrate(sc, data, ctx=None):
    """Orchestrator (MLFO role): run agents in order and reconcile their stances."""
    epi = epi_agent(sc, data, ctx)
    pol = policy_agent(sc, data, ctx)
    dpa = dpa_agent(sc, data, ctx)
    dmo = dmo_agent(sc, data, epi, dpa)
    tensions = []
    if "Case level" in epi["stance"] and "Allow line lists" in dpa["stance"]:
        tensions.append("Speed versus privacy: the epidemiology agent wants case level data, the data protection agent limits it. Resolution: line lists stay inside the district, only aggregates move up.")
    if not pol["cites"]:
        tensions.append("No policy passage found. A human adviser must confirm the legal basis.")
    final = {"risk": epi["risk"], "plan": dmo["plan"], "tensions": tensions,
             "sources": sorted({h["id"] for a in (pol, dpa) for h in a["cites"]})}
    return [epi, pol, dpa, dmo], final


# ------------------------------------------------------------------
# ITU Y.3172 style pipeline: SRC, C, PP, M, P, D, SINK
# ------------------------------------------------------------------
PIPE_CHECKS = pipe_checks()

STAGES = [("SRC", "Source of data", "DHIS2 indicators for the selected region"),
          ("C", "Collector", "Collects indicator values (sample values in this demo)"),
          ("PP", "Pre-producer", "Compares each value with its target using the 5% tolerance"),
          ("M", "Model", "Scores overall regional risk with the shared rule"),
          ("P", "Policy", "Applies privacy and alert rules to the output"),
          ("D", "Distributor", "Builds dashboard text, USSD message and FHIR bundle"),
          ("SINK", "Target of ML output", "Community health worker and District Medical Officer")]


def run_pipeline(data, region, mode, ctx=None):
    sandbox = mode == "sandbox"
    pc = pipe_checks(ctx)
    rng = np.random.default_rng(7)
    vals = {k: float(data[k]) * (1 + (rng.normal(0, 0.1) if sandbox else 0)) for k, *_ in pc}
    underlay = "Simulated ML underlay network (synthetic noise added)" if sandbox else "ML underlay network (production path)"
    a = assess(pc, vals, (ctx or DEFAULT_CTX)["cholera_alert"])
    level = a["level"]
    detail = f"{a['off']} of {a['n']} indicators off target"
    msg = f"{region}: overall risk {level}. {detail}."
    fhir = {"resourceType": "Bundle", "type": "transaction", "entry": [{"resource": {"resourceType": "CarePlan", "status": "draft" if sandbox else "active", "intent": "plan", "title": f"Overall risk {level} for {region}"}}]}
    logs = [f"Read {a['n']} indicators for {region}", f"Via {underlay}: {a['n']} values collected",
            "Against target: " + ", ".join(f"{i['key']} {i['state']}" for i in a["items"]),
            f"{detail}, so overall regional risk is {level}" + (" (cholera alert level exceeded)" if a["override"] else ""),
            "Rules: aggregates only leave the district, HIGH risk notifies the District Medical Officer within 24 hours",
            f"USSD text: {msg}", "Delivered to CHW by USSD and to District Medical Officer by FHIR" + (" (simulated, nothing is sent)" if sandbox else "")]
    out = [{"code": c, "name": n, "what": w, "log": logs[i]} for i, (c, n, w) in enumerate(STAGES)]
    return {"mode": mode, "level": level, "score": detail, "stages": out, "fhir": fhir, "ussd": msg}


def pipeline_dot():
    def lane(p, title, under, color):
        nodes = "".join(f'{p}{c} [label="{c}\\n{n}"]; ' for c, n, _ in STAGES)
        edges = " -> ".join(f"{p}{c}" for c, _, _ in STAGES)
        return (f'subgraph cluster_{p} {{ label="{title}"; style=dashed; {nodes} {edges}; '
                f'{p}U [label="{under}", fillcolor="{color}"]; {p}SINK -> {p}U [style=dashed]; {p}U -> {p}SRC [style=dashed]; }}')
    return ('digraph { rankdir=TB; node [shape=box, style="rounded,filled", fillcolor="#cfe2ff", fontsize=11]; '
            'Intent [label="ML intent\\n(user prompt)", shape=note, fillcolor="#e2e3e5"]; MLFO [label="MLFO\\nOrchestrator agent", fillcolor="#d1e7dd"]; '
            'Intent -> MLFO; MLFO -> sSRC; MLFO -> pSRC; '
            + lane("s", "ML sandbox (synthetic data)", "Simulated ML underlay networks", "#fff3cd")
            + lane("p", "ML pipeline (production path)", "ML underlay networks", "#f8d7da") + " }")


# ------------------------------------------------------------------
# Streamlit tab
# ------------------------------------------------------------------
TXT = {
    "en": {"tab": "🧠 Agents & Pipeline", "h": "Multi Agent Reasoning and ITU Y.3172 Pipeline",
           "demo": "Demo: rule based agents and placeholder knowledge base. Replace with official documents before submission.",
           "intent": "Type an intent (optional)", "scenario": "Or choose a scenario", "run": "Run agents", "parsed": "Intent understood as",
           "final": "Orchestrator decision", "risk": "Risk", "overall": "overall regional risk", "scen": "Scenario risk", "plan": "Action plan", "tension": "Where agents disagree", "src": "Sources used",
           "ph": "Pipeline view", "runp": "Run sandbox and production pipeline", "sb": "Sandbox", "pr": "Production path", "stage": "Stage"},
    "sw": {"tab": "🧠 Mawakala na Mtiririko", "h": "Hoja za Mawakala Wengi na Mtiririko wa ITU Y.3172",
           "demo": "Majaribio: mawakala wa kanuni na msingi wa maarifa wa mfano. Badilisha na nyaraka rasmi kabla ya kuwasilisha.",
           "intent": "Andika nia yako (hiari)", "scenario": "Au chagua tukio", "run": "Endesha mawakala", "parsed": "Nia imeeleweka kama",
           "final": "Uamuzi wa msimamizi", "risk": "Hatari", "overall": "hatari ya jumla ya mkoa", "scen": "Hatari ya tukio", "plan": "Mpango wa hatua", "tension": "Mawakala wasipokubaliana", "src": "Vyanzo vilivyotumika",
           "ph": "Mwonekano wa mtiririko", "runp": "Endesha mtiririko wa sandbox na uzalishaji", "sb": "Sandbox", "pr": "Njia ya uzalishaji", "stage": "Hatua"},
}


def tab_label(lang):
    return TXT[lang]["tab"]


def render_agents_tab(lang, region, data, ctx=None):
    import streamlit as st
    x = TXT[lang]
    key = ((ctx or DEFAULT_CTX)["code"], region)
    st.header(x["h"])
    st.caption(f"🧪 {x['demo']}")

    text = st.text_input(x["intent"], key="agent_intent", placeholder="Cholera cases rising in " + region)
    keys = list(SCENARIOS)
    chosen = st.selectbox(x["scenario"], keys, format_func=lambda k: SCENARIOS[k][lang], key="agent_scenario")
    sc = parse_intent(text) or chosen
    if text:
        st.caption(f"{x['parsed']}: {SCENARIOS[sc][lang]}")

    if st.button(x["run"], use_container_width=True, key="agent_run_btn"):
        with st.status("MLFO orchestrator running...", expanded=True) as status:
            for name in ["Epidemiology agent", "Policy and legal adviser", "Data protection authority agent", "District Medical Officer"]:
                st.write(f"Running {name}")
                time.sleep(0.3)
            status.update(label="All agents finished", state="complete")
        st.session_state["agent_result"] = orchestrate(sc, data, ctx) + (sc, key)

    res = st.session_state.get("agent_result")
    if res and res[3] == key:
        agents, final, sc_done, _ = res
        for a in agents:
            with st.expander(f"{a['agent']}  |  {a['stance'][:60]}", expanded=False):
                for i, s in enumerate(a["steps"], 1):
                    st.write(f"{i}. {s}")
                st.write(f"**Stance:** {a['stance']}")
                for h in a["cites"]:
                    st.caption(f"{h['id']}: {h['text']}")
        st.subheader(x["final"])
        st.metric(x["scen"], final["risk"])
        st.write(f"**{x['plan']}**")
        for p in final["plan"]:
            st.write(f"- {p}")
        for t in final["tensions"]:
            st.warning(f"**{x['tension']}:** {t}")
        if final["sources"]:
            st.caption(f"{x['src']}: {', '.join(final['sources'])}")

    st.markdown("---")
    st.subheader(x["ph"])
    st.graphviz_chart(pipeline_dot(), use_container_width=True)
    if st.button(x["runp"], use_container_width=True, key="pipe_run_btn"):
        st.session_state["pipe_result"] = (run_pipeline(data, region, "sandbox", ctx), run_pipeline(data, region, "production", ctx), key)
    pr = st.session_state.get("pipe_result")
    if pr and pr[2] == key:
        sb, prod, _ = pr
        c1, c2 = st.columns(2)
        c1.metric(f"{x['sb']}: {x['overall']}", sb["level"], delta=sb["score"], delta_color="off")
        c2.metric(f"{x['pr']}: {x['overall']}", prod["level"], delta=prod["score"], delta_color="off")
        for tab, r in zip(st.tabs([x["sb"], x["pr"]]), (sb, prod)):
            with tab:
                for s in r["stages"]:
                    with st.expander(f"{s['code']}: {s['name']}"):
                        st.write(s["what"])
                        st.code(s["log"], language="text")
                st.code(json.dumps(r["fhir"], indent=2), language="json")
