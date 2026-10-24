"""Outbreak Watch for EcoHealth Sentinel.

Modelled on how real surveillance systems work: IDSR priority diseases and alert rules, event based surveillance
(signal triage), IHR style readiness checklists, Go.Data and SORMAS style countdown clocks, and climate informed early warning.
Everything here is decision support for a demo. Use the national case definitions and guidance for real decisions.
"""
import os
import json
import datetime
from packs import HERE
from agents import DEFAULT_CTX
from viz import severity, SEV_NAME

LEVEL_LABEL = {"en": {4: "IN REGION", 3: "HIGH", 2: "MEDIUM", 1: "LOW", 0: "UNKNOWN", -1: "NONE"},
               "sw": {4: "KATIKA MKOA", 3: "JUU", 2: "WASTANI", 1: "CHINI", 0: "HAIJULIKANI", -1: "HAKUNA"}}
EMOJI = {"CRITICAL": "🟥", "HIGH": "🟧", "MEDIUM": "🟨", "LOW": "🟩", "UNKNOWN": "⬜", "NONE": "⬜"}


def load_threats():
    with open(os.path.join(HERE, "threats.json"), encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------ exposure and rapid risk
def exposure(threat, pack, region):
    """Likelihood of exposure for one region: 4 in region, 3 high, 2 medium, 1 low, 0 unknown, -1 no active outbreak."""
    if not threat.get("active", False):
        return -1, "No active outbreak reported. Keep watching for spillover."
    aff = set(threat.get("countries", []))
    if not aff:
        return 0, "No affected countries are listed for this threat. Add them to threats.json."
    c, ep = pack["name"], pack.get("entry_points", {}).get(region, {})
    if region in threat.get("locations", {}).get(c, []):
        return 4, "Cases are reported in this region."
    if c in aff:
        return 3, "Cases are reported elsewhere in this country."
    shared = set(ep.get("borders", [])) & aff
    if shared:
        return 3, "Shares a border or lake with " + ", ".join(sorted(shared)) + ", where cases are reported."
    near = set(pack.get("neighbors", [])) & aff
    if near:
        return 2, "A neighboring country has cases: " + ", ".join(sorted(near)) + "."
    if ep.get("airport"):
        return 2, "International travel link while the threat is active in Africa."
    return 1, "No direct link found. The threat is active elsewhere in Africa."


def rapid_risk(threat, pack, region, readiness=None):
    """Likelihood times impact. Impact is the threat severity, raised by one when readiness is below 50%."""
    level, reason = exposure(threat, pack, region)
    if level < 1:
        return {"category": "NONE" if level == -1 else "UNKNOWN", "likelihood": level, "impact": 0, "score": 0, "reason": reason}
    impact = min(4, threat.get("severity", 2) + (1 if readiness is not None and readiness < 0.5 else 0))
    score = level * impact
    cat = "CRITICAL" if score >= 12 else "HIGH" if score >= 8 else "MEDIUM" if score >= 4 else "LOW"
    return {"category": cat, "likelihood": level, "impact": impact, "score": score, "reason": reason}


def banner_lines(pack, region, lang, state=None):
    T = load_threats()
    ready = readiness_from_state(state or {}, pack["code"], region)
    out = []
    for t in T["threats"]:
        if t["type"] == "disease":
            rr = rapid_risk(t, pack, region, ready)
            if rr["likelihood"] >= 3:
                out.append(f"{t['disease']}: {LEVEL_LABEL[lang][rr['likelihood']]} ({region}). {rr['reason']}")
    return out


# ------------------------------------------------------------------ signal triage (event based surveillance style)
SYM = {"fever": {"en": "Fever", "sw": "Homa"}, "bleeding": {"en": "Unexplained bleeding", "sw": "Kutokwa damu bila sababu"},
       "headache": {"en": "Severe headache", "sw": "Maumivu makali ya kichwa"}, "vomiting": {"en": "Vomiting", "sw": "Kutapika"},
       "diarrhea": {"en": "Diarrhea", "sw": "Kuhara"}, "muscle": {"en": "Muscle pain or severe fatigue", "sw": "Maumivu ya misuli au uchovu mkali"},
       "rash": {"en": "Skin rash or lesions", "sw": "Vipele au vidonda vya ngozi"}, "nodes": {"en": "Swollen lymph nodes", "sw": "Matezi yaliyovimba"},
       "watery": {"en": "Severe watery diarrhea", "sw": "Kuhara maji mengi sana"}}
EXPO = {"contact_case": {"en": "Contact with a suspected or confirmed case", "sw": "Kukutana na mgonjwa mtuhumiwa au aliyethibitishwa"},
        "funeral": {"en": "Attended a funeral or handled a body", "sw": "Kuhudhuria mazishi au kushika mwili wa marehemu"},
        "travel": {"en": "Travel to or from an affected area in the last 21 days", "sw": "Kusafiri kwenda au kutoka eneo lililoathirika ndani ya siku 21"},
        "hcw": {"en": "Cared for a suspected case as a health worker", "sw": "Kumhudumia mtuhumiwa kama mhudumu wa afya"},
        "animal": {"en": "Contact with bats, wildlife or sick animals", "sw": "Kukutana na popo, wanyamapori au wanyama wagonjwa"},
        "contact_rash": {"en": "Close contact with a person with a rash", "sw": "Kuwa karibu na mtu mwenye vipele"}}
SYNDROME = {"vhf": {"en": "Viral haemorrhagic fever (Ebola, Marburg and others)", "sw": "Homa ya virusi vya kutokwa damu (Ebola, Marburg na nyingine)"},
            "mpox": {"en": "Suspected mpox", "sw": "Mtuhumiwa wa mpox"}, "cholera": {"en": "Suspected cholera", "sw": "Mtuhumiwa wa kipindupindu"}}
STEPS = {"vhf": {"en": "Isolate the patient in a separate room. Staff wear gloves, a gown, a mask and eye protection. Do not touch blood or body fluids. Notify the District Medical Officer immediately. List everyone who had contact.",
                 "sw": "Mtenge mgonjwa kwenye chumba tofauti. Wahudumu wavae glavu, gauni, barakoa na kinga ya macho. Usiguse damu au majimaji ya mwili. Mjulishe Mganga Mkuu wa Wilaya mara moja. Orodhesha kila aliyekuwa karibu naye."},
         "mpox": {"en": "Cover skin lesions and separate the patient from others. Avoid shared bedding and towels. Notify the District Medical Officer within 24 hours and arrange a sample.",
                  "sw": "Funika vidonda vya ngozi na mtenge mgonjwa. Epuka kushiriki shuka na taulo. Mjulishe Mganga Mkuu wa Wilaya ndani ya saa 24 na panga kuchukua sampuli."},
         "cholera": {"en": "Start oral rehydration. Keep soiled items apart. Notify the District Medical Officer within 24 hours, collect a stool sample and wash hands with soap and chlorinated water.",
                     "sw": "Anza maji ya kurudisha maji mwilini (ORS). Tenganisha vitu vilivyochafuka. Mjulishe Mganga Mkuu wa Wilaya ndani ya saa 24, chukua sampuli ya kinyesi na osha mikono kwa sabuni na maji yenye klorini."}}
TRIAGE_LEVEL = {3: {"en": "IMMEDIATE ALERT", "sw": "TAHADHARI YA HARAKA"}, 2: {"en": "NOTIFY WITHIN 24 HOURS", "sw": "TOA TAARIFA NDANI YA SAA 24"},
                0: {"en": "Does not meet alert criteria. Continue routine IDSR reporting.", "sw": "Haikidhi vigezo vya tahadhari. Endelea na kuripoti kwa IDSR ya kawaida."}}


def triage(symptoms, exposures):
    """Rule based alert levels: 3 immediate alert, 2 notify within 24 hours, 0 routine. Not a diagnosis."""
    s, e = set(symptoms), set(exposures)
    group = len(s & {"headache", "vomiting", "diarrhea", "muscle"})
    out = []
    if "fever" in s and ("bleeding" in s or (group >= 3 and e & {"contact_case", "funeral", "travel", "hcw", "animal"})):
        out.append(("vhf", 3))
    elif "fever" in s and group >= 3:
        out.append(("vhf", 2))
    if "rash" in s and s & {"fever", "nodes"}:
        out.append(("mpox", 3 if e & {"contact_rash", "contact_case"} else 2))
    if "watery" in s:
        out.append(("cholera", 2))
    top = max(out, key=lambda m: m[1]) if out else None
    return {"matches": out, "level": top[1] if top else 0, "syndrome": top[0] if top else None}


# ------------------------------------------------------------------ readiness checklist (IHR style)
def _it(i, en, sw):
    return {"id": i, "en": en, "sw": sw}


DOMAINS = [
    {"id": "surv", "en": "Surveillance", "sw": "Ufuatiliaji", "items": [
        _it("defs", "Case definitions for Ebola, Marburg, mpox and cholera are displayed in facilities", "Fasili za kesi za Ebola, Marburg, mpox na kipindupindu zimebandikwa vituoni"),
        _it("idsr", "Weekly IDSR reports reach the district on time", "Ripoti za IDSR za kila wiki zinafika wilayani kwa wakati")]},
    {"id": "lab", "en": "Laboratory", "sw": "Maabara", "items": [
        _it("samp", "Sample collection and safe transport to a reference laboratory are arranged", "Ukusanyaji wa sampuli na usafirishaji salama hadi maabara ya rufaa umepangwa"),
        _it("tat", "Result turnaround time is tracked", "Muda wa kupata majibu unafuatiliwa")]},
    {"id": "case", "en": "Case management", "sw": "Matibabu ya wagonjwa", "items": [
        _it("iso", "An isolation area is identified at the referral hospital", "Eneo la kutenga wagonjwa limeainishwa hospitali ya rufaa"),
        _it("train", "Staff are trained in clinical care of viral haemorrhagic fever", "Watumishi wamefunzwa huduma ya kitabibu ya homa za virusi vya kutokwa damu")]},
    {"id": "ipc", "en": "Infection prevention", "sw": "Kinga ya maambukizi", "items": [
        _it("ppe", "Personal protective equipment is in stock and checked monthly", "Vifaa vya kinga binafsi vipo na vinakaguliwa kila mwezi"),
        _it("wash", "Hand washing and chlorine are available at facility entrances", "Maji ya kunawa na klorini vinapatikana milangoni mwa vituo")]},
    {"id": "rrt", "en": "Rapid response", "sw": "Kukabiliana haraka", "items": [
        _it("team", "A trained rapid response team is on call", "Timu ya kukabiliana haraka iliyofunzwa ipo kwa wito"),
        _it("trace", "Contact tracing staff or volunteers are trained", "Wafuatiliaji wa waliokutana na wagonjwa wamefunzwa")]},
    {"id": "comm", "en": "Community and risk communication", "sw": "Jamii na mawasiliano ya hatari", "items": [
        _it("chw", "CHWs know how to report rumors and signals", "Wahudumu wa afya jamii wanajua kuripoti uvumi na ishara"),
        _it("burial", "A safe and dignified burial team is identified", "Timu ya mazishi salama na yenye heshima imeainishwa")]},
    {"id": "poe", "en": "Points of entry", "sw": "Maeneo ya kuingilia nchini", "items": [
        _it("screen", "Border and airport health staff have a screening and referral procedure", "Wahudumu wa afya wa mipakani na viwanja vya ndege wana utaratibu wa uchunguzi na rufaa"),
        _it("transport", "A transport plan exists for suspected cases", "Mpango wa usafiri wa wagonjwa watuhumiwa upo")]},
    {"id": "coord", "en": "Coordination and funding", "sw": "Uratibu na fedha", "items": [
        _it("meet", "An emergency coordination meeting is scheduled", "Mkutano wa uratibu wa dharura umepangwa"),
        _it("fund", "Funds or a budget line exist for outbreak response", "Fedha au bajeti ya kukabiliana na milipuko ipo")]}]
ITEM_IDS = [(d["id"], i["id"]) for d in DOMAINS for i in d["items"]]


def item_key(code, region, domain_id, item_id):
    return f"rd_{code}_{region}_{domain_id}_{item_id}"


def readiness_scores(answers):
    """answers maps 'domain.item' to True or False. Returns overall fraction, domain fractions and the list of gaps."""
    dom, gaps = {}, []
    for d in DOMAINS:
        vals = [bool(answers.get(f"{d['id']}.{i['id']}", False)) for i in d["items"]]
        dom[d["id"]] = sum(vals) / len(vals)
        gaps += [f"{d['id']}.{i['id']}" for i, v in zip(d["items"], vals) if not v]
    total = sum(bool(answers.get(f"{d}.{i}", False)) for d, i in ITEM_IDS)
    return total / len(ITEM_IDS), dom, gaps


def readiness_from_state(state, code, region):
    """Overall readiness for a region, or None when nothing has been ticked yet."""
    answers = {f"{d}.{i}": bool(state.get(item_key(code, region, d, i), False)) for d, i in ITEM_IDS}
    return readiness_scores(answers)[0] if any(answers.values()) else None


def readiness_label(f, lang):
    en = "Ready" if f >= 0.8 else "Partly ready" if f >= 0.5 else "Not ready"
    sw = {"Ready": "Tayari", "Partly ready": "Tayari kiasi", "Not ready": "Haijawa tayari"}[en]
    return en if lang == "en" else sw


# ------------------------------------------------------------------ countdown clocks
def countdown(last_event, today, days):
    elapsed = (today - last_event).days
    return {"elapsed": elapsed, "remaining": max(0, days - elapsed), "end_date": last_event + datetime.timedelta(days=days), "complete": elapsed >= days, "future": elapsed < 0}


# ------------------------------------------------------------------ climate context
def climate_rows(regions, ctx, threats):
    ctx = ctx or DEFAULT_CTX
    enso = next((t for t in threats["threats"] if t["type"] == "climate"), None)
    rows = []
    for name, row in regions.items():
        c = severity("cholera", float(row["cholera"]), *ctx["targets"]["cholera"], ctx["cholera_alert"])
        m = severity("mal", float(row["mal"]), *ctx["targets"]["mal"], ctx["cholera_alert"])
        rows.append({"region": name, "cholera": c, "malaria": m, "double": bool(enso and enso.get("active") and max(c, m) >= 2)})
    return rows


TXT = {
    "en": {"tab": "🛰️ Outbreak Watch", "h": "Outbreak preparedness and surveillance", "cap": "Demo decision support. Use national case definitions and Ministry of Health guidance for real decisions.",
           "nopack": "Outbreak Watch needs a country pack.", "s1": "1. Threat board", "asof": "Checked on", "threat": "Threat", "status": "Status", "exposure": "Exposure", "priority": "Priority",
           "why": "Why this exposure", "region": "Region", "srcs": "Sources", "incub": "Incubation", "spread": "Spread", "allreg": "All regions",
           "s2": "2. Signal triage", "triage_warn": "Do not enter names or phone numbers. This is a demo rule set and not a diagnosis.", "symptoms": "Signs reported", "exposures": "Exposure history",
           "assess": "Assess signal", "save": "Save to signal inbox", "inbox": "Signal inbox", "dl": "Download CSV", "steps": "What to do now",
           "s3": "3. Readiness checklist", "overall": "Overall readiness", "gaps": "Biggest gaps", "unrated": "Tick the items that are in place for this region.",
           "s4": "4. Countdown clocks", "custom": "Custom date", "pick": "Start from", "last": "Date of last confirmed case", "days42": "days since the last case (42 day rule)", "elapsed": "Days elapsed",
           "remain": "Days remaining", "end": "Earliest end date", "rule": "An outbreak is usually declared over 42 days after the last case, which is two incubation periods. Confirm the criteria with national guidance.",
           "future": "That date is in the future.", "contact": "Contact follow up (21 days)", "exp_date": "Date of last exposure", "ended": "Ended outbreaks",
           "s5": "5. Climate context", "clim": "El Niño tends to bring above normal short rains to parts of East Africa from October to December. Past events were linked to floods and to more cholera, malaria and Rift Valley fever. This is an association from past events and not a forecast for your region. Check ICPAC for the national outlook.",
           "double": "Climate plus existing pressure", "cholera": "Cholera", "malaria": "Malaria", "yes": "Yes", "no": "No"},
    "sw": {"tab": "🛰️ Ufuatiliaji wa Milipuko", "h": "Maandalizi na ufuatiliaji wa milipuko", "cap": "Msaada wa maamuzi wa majaribio. Tumia fasili za kitaifa na mwongozo wa Wizara ya Afya kwa maamuzi halisi.",
           "nopack": "Ufuatiliaji wa Milipuko unahitaji kifurushi cha nchi.", "s1": "1. Ubao wa vitisho", "asof": "Imekaguliwa tarehe", "threat": "Tishio", "status": "Hali", "exposure": "Mfiduo", "priority": "Kipaumbele",
           "why": "Sababu ya mfiduo huu", "region": "Mkoa", "srcs": "Vyanzo", "incub": "Kipindi cha incubation", "spread": "Kuenea", "allreg": "Mikoa yote",
           "s2": "2. Uchambuzi wa ishara", "triage_warn": "Usiweke majina wala namba za simu. Hii ni kanuni za majaribio na si utambuzi.", "symptoms": "Dalili zilizoripotiwa", "exposures": "Historia ya kukutana",
           "assess": "Chambua ishara", "save": "Hifadhi kwenye sanduku la ishara", "inbox": "Sanduku la ishara", "dl": "Pakua CSV", "steps": "Cha kufanya sasa",
           "s3": "3. Orodha ya utayari", "overall": "Utayari wa jumla", "gaps": "Mapengo makubwa", "unrated": "Weka alama kwenye vitu vilivyopo kwa mkoa huu.",
           "s4": "4. Saa za kuhesabu siku", "custom": "Tarehe nyingine", "pick": "Anzia kwenye", "last": "Tarehe ya mgonjwa wa mwisho aliyethibitishwa", "days42": "siku tangu mgonjwa wa mwisho (kanuni ya siku 42)", "elapsed": "Siku zilizopita",
           "remain": "Siku zilizobaki", "end": "Tarehe ya mapema ya kuisha", "rule": "Mlipuko kwa kawaida hutangazwa kuisha siku 42 baada ya mgonjwa wa mwisho, ambazo ni vipindi viwili vya incubation. Thibitisha vigezo na mwongozo wa kitaifa.",
           "future": "Tarehe hiyo iko mbele.", "contact": "Ufuatiliaji wa waliokutana na wagonjwa (siku 21)", "exp_date": "Tarehe ya mwisho ya kukutana", "ended": "Milipuko iliyoisha",
           "s5": "5. Hali ya hewa", "clim": "El Niño huelekea kuleta mvua za vuli zaidi ya kawaida katika baadhi ya maeneo ya Afrika Mashariki kuanzia Oktoba hadi Desemba. Matukio ya zamani yalihusishwa na mafuriko na ongezeko la kipindupindu, malaria na homa ya bonde la ufa. Huu ni uhusiano kutoka matukio ya zamani na si utabiri wa mkoa wako. Angalia ICPAC kwa makadirio ya kitaifa.",
           "double": "Hali ya hewa pamoja na shinikizo lililopo", "cholera": "Kipindupindu", "malaria": "Malaria", "yes": "Ndiyo", "no": "Hapana"},
}


def tab_label(lang):
    return TXT[lang]["tab"]


def render_outbreak_tab(lang, pack, region, regions, ctx=None):
    import streamlit as st
    import pandas as pd
    x, T = TXT[lang], load_threats()
    st.header(f"🛰️ {x['h']}")
    st.caption(f"🧪 {x['cap']}")
    if not pack:
        st.info(x["nopack"])
        return
    code = pack["code"]
    ss = st.session_state
    diseases = [t for t in T["threats"] if t["type"] == "disease"]

    # 1. threat board
    st.subheader(x["s1"])
    st.caption(f"{x['asof']} {T['as_of']}. {T['disclaimer']}")
    ready = readiness_from_state(ss, code, region)
    board = []
    for t in diseases:
        rr = rapid_risk(t, pack, region, ready)
        board.append({x["threat"]: t["disease"], x["exposure"]: LEVEL_LABEL[lang][rr["likelihood"]], x["priority"]: f"{EMOJI[rr['category']]} {rr['category']}"})
    st.dataframe(pd.DataFrame(board), use_container_width=True, hide_index=True)
    for t in diseases:
        rr = rapid_risk(t, pack, region, ready)
        with st.expander(f"{EMOJI[rr['category']]} {t['disease']}"):
            st.write(f"**{x['status']}:** {t['status']}")
            st.write(t["figures"])
            if t.get("note"):
                st.caption(t["note"])
            st.write(f"**{x['why']} ({region}):** {rr['reason']}")
            if t.get("profile"):
                st.caption(f"{x['incub']}: {t['profile']['incubation']}. {x['spread']}: {t['profile']['spread']} ({t['profile']['source']})")
            rows = []
            for name in regions:
                r2 = rapid_risk(t, pack, name, readiness_from_state(ss, code, name))
                rows.append({x["region"]: name, x["exposure"]: LEVEL_LABEL[lang][r2["likelihood"]], x["priority"]: f"{EMOJI[r2['category']]} {r2['category']}"})
            st.write(f"**{x['allreg']}**")
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            st.write(f"**{x['srcs']}**")
            for s in t["sources"]:
                st.markdown(f"- [{s['title']}]({s['url']}) ({s['date']}, {s['type']})")

    # 2. signal triage
    st.markdown("---")
    st.subheader(x["s2"])
    st.warning(x["triage_warn"])
    sym = st.multiselect(x["symptoms"], list(SYM), format_func=lambda k: SYM[k][lang], key=f"tri_sym_{code}")
    exp = st.multiselect(x["exposures"], list(EXPO), format_func=lambda k: EXPO[k][lang], key=f"tri_exp_{code}")
    if st.button(x["assess"], use_container_width=True, key=f"tri_go_{code}"):
        ss[f"tri_res_{code}"] = {**triage(sym, exp), "sym": list(sym), "exp": list(exp)}
    res = ss.get(f"tri_res_{code}")
    if res:
        label = TRIAGE_LEVEL[res["level"]][lang]
        if res["level"] == 3:
            st.error(f"🚨 {label}: {SYNDROME[res['syndrome']][lang]}")
        elif res["level"] == 2:
            st.warning(f"⚠️ {label}: {SYNDROME[res['syndrome']][lang]}")
        else:
            st.success(label)
        for syn, _ in res["matches"]:
            st.write(f"**{SYNDROME[syn][lang]}.** {x['steps']}: {STEPS[syn][lang]}")
        if st.button(x["save"], use_container_width=True, key=f"tri_save_{code}"):
            ss.setdefault(f"inbox_{code}", []).append({"time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "region": region, "syndrome": res["syndrome"] or "none",
                                                      "level": res["level"], "signs": ",".join(res["sym"]), "exposures": ",".join(res["exp"])})
    inbox = ss.get(f"inbox_{code}", [])
    if inbox:
        st.write(f"**{x['inbox']}**")
        df = pd.DataFrame(inbox)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(x["dl"], df.to_csv(index=False), file_name="signal_inbox.csv", key=f"tri_dl_{code}")

    # 3. readiness
    st.markdown("---")
    st.subheader(f"{x['s3']}: {region}")
    st.caption(x["unrated"])
    for d in DOMAINS:
        with st.expander(d[lang]):
            for i in d["items"]:
                st.checkbox(i[lang], key=item_key(code, region, d["id"], i["id"]))
    answers = {f"{d}.{i}": bool(ss.get(item_key(code, region, d, i), False)) for d, i in ITEM_IDS}
    overall, dom, gaps = readiness_scores(answers)
    st.metric(x["overall"], f"{round(100 * overall)}%", delta=readiness_label(overall, lang), delta_color="off")
    st.dataframe(pd.DataFrame([{"domain": d[lang], "%": round(100 * dom[d["id"]])} for d in DOMAINS]), use_container_width=True, hide_index=True)
    if gaps and any(answers.values()):
        names = {f"{d['id']}.{i['id']}": i[lang] for d in DOMAINS for i in d["items"]}
        st.write(f"**{x['gaps']}**")
        for g in gaps[:5]:
            st.write(f"- {names[g]}")
    st.download_button(x["dl"], pd.DataFrame([{"item": k, "in_place": v} for k, v in answers.items()]).to_csv(index=False), file_name=f"readiness_{code}_{region}.csv", key=f"rd_dl_{code}")

    # 4. countdown clocks
    st.markdown("---")
    st.subheader(x["s4"])
    opts = [(t["disease"], c, d) for t in diseases for c, d in t.get("last_case", {}).items()]
    pick = st.selectbox(x["pick"], ["custom"] + [f"{a}: {b}" for a, b, _ in opts], format_func=lambda v: x["custom"] if v == "custom" else v, key=f"cd_pick_{code}")
    default = datetime.date.today() - datetime.timedelta(days=7)
    for a, b, d in opts:
        if pick == f"{a}: {b}":
            default = datetime.date.fromisoformat(d)
    last = st.date_input(x["last"], value=default, key=f"cd_date_{code}_{pick}")
    cd = countdown(last, datetime.date.today(), 42)
    if cd["future"]:
        st.error(x["future"])
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric(x["elapsed"], cd["elapsed"])
        c2.metric(x["remain"], cd["remaining"])
        c3.metric(x["end"], str(cd["end_date"]))
        st.progress(min(1.0, cd["elapsed"] / 42), text=f"{min(cd['elapsed'], 42)} / 42 {x['days42']}")
    st.caption(x["rule"])
    exp_date = st.date_input(x["exp_date"], value=datetime.date.today() - datetime.timedelta(days=3), key=f"cf_date_{code}")
    cf = countdown(exp_date, datetime.date.today(), 21)
    if not cf["future"]:
        st.write(f"**{x['contact']}:** {x['remain']} {cf['remaining']}, {x['end']} {cf['end_date']}")
    for t in diseases:
        for c, d in t.get("ended", {}).items():
            st.caption(f"{x['ended']}: {t['disease']}, {c}, {d}")

    # 5. climate
    st.markdown("---")
    st.subheader(x["s5"])
    enso = next((t for t in T["threats"] if t["type"] == "climate"), None)
    if enso:
        st.info(f"**{enso['disease']}:** {enso['status']}\n\n{enso['figures']}")
        st.caption(enso.get("note", ""))
        for s in enso["sources"]:
            st.markdown(f"- [{s['title']}]({s['url']}) ({s['date']})")
    st.write(x["clim"])
    crow = climate_rows(regions, ctx, T)
    st.dataframe(pd.DataFrame([{x["region"]: r["region"], x["cholera"]: SEV_NAME[lang][r["cholera"]], x["malaria"]: SEV_NAME[lang][r["malaria"]],
                                x["double"]: (x["yes"] if r["double"] else x["no"])} for r in crow]), use_container_width=True, hide_index=True)
