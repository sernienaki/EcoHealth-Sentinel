"""Country packs for EcoHealth Sentinel.

A country pack is one JSON file named pack_<code>.json placed beside app.py.
It holds regions, indicator targets, languages, USSD networks, legal references and the policy knowledge base.
Adding a country means adding one file. Nothing in the code changes.
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
INDICATORS = ["mal", "mal_pos", "cholera", "tb", "llin", "mmr", "imr", "anc4", "sba", "sam", "fic", "penta_drop",
              "htn", "dm", "cervical", "tobacco", "stockout", "hw", "oop"]
REGION_KEYS = INDICATORS + ["lat", "lon", "poverty", "schools", "markets"]
TOPICS = ["cholera_report", "cholera_wash", "privacy", "sharing", "immunization", "stockout", "maternal", "ussd", "digital"]
TOP_KEYS = ["code", "name", "languages", "region_label", "policy_text", "references", "regulator", "data_law",
            "health_information_system", "data_status", "cholera_alert", "targets", "ussd", "regions", "kb"]

BANNER = {"en": "PLACEHOLDER COUNTRY PACK: the data and legal passages for this country are placeholders, not real. Do not use them for decisions.",
          "sw": "KIFURUSHI CHA NCHI CHA MFANO: data na vifungu vya sheria vya nchi hii ni vya mfano, si halisi. Usivitumie kwa maamuzi."}


def available_packs():
    out = []
    for path in sorted(glob.glob(os.path.join(HERE, "pack_*.json"))):
        try:
            p = json.load(open(path, encoding="utf-8"))
            out.append((p["code"], p["name"]))
        except Exception:
            continue
    return out


def load_pack(code):
    with open(os.path.join(HERE, f"pack_{code}.json"), encoding="utf-8") as f:
        return json.load(f)


def context(pack):
    """What the agents and the harness need from a pack."""
    return {"code": pack["code"], "kb": pack["kb"],
            "targets": {k: tuple(v) for k, v in pack["targets"].items()},
            "cholera_alert": pack["cholera_alert"]}


def validate_pack(p):
    """Return a list of problems. An empty list means the pack is complete."""
    bad = [f"Missing top level field: {k}" for k in TOP_KEYS if k not in p]
    if bad:
        return bad
    for k in INDICATORS:
        t = p["targets"].get(k)
        if not (isinstance(t, list) and len(t) == 2 and t[1] in ("lower", "higher")):
            bad.append(f"Target for {k} must be [value, 'lower' or 'higher']")
    for name, row in p["regions"].items():
        miss = [k for k in REGION_KEYS if k not in row]
        if miss:
            bad.append(f"Region {name} is missing: {', '.join(miss)}")
    if not p["regions"]:
        bad.append("No regions defined")
    seen = set()
    for q in p["kb"]:
        for k in ("id", "topic", "source", "text", "status"):
            if k not in q:
                bad.append(f"Knowledge base passage missing {k}: {q.get('id', '?')}")
        if q.get("id") in seen:
            bad.append(f"Duplicate passage id {q.get('id')}")
        seen.add(q.get("id"))
    for t in TOPICS:
        if not any(q.get("topic") == t for q in p["kb"]):
            bad.append(f"No knowledge base passage for topic: {t}")
    for k in ("en", "sw"):
        if k not in p["policy_text"] or k not in p["region_label"]:
            bad.append(f"policy_text and region_label need both en and sw ({k} missing)")
    return bad


def template_pack():
    t = {k: None for k in TOP_KEYS}
    t.update({"code": "xx", "name": "Country name", "languages": ["en"], "region_label": {"en": "Select Region", "sw": "Chagua Mkoa"},
              "policy_text": {"en": "Policy: ...", "sw": "Sera: ..."}, "references": [], "data_status": "placeholder",
              "cholera_alert": 100, "targets": {k: [0, "lower"] for k in INDICATORS},
              "ussd": [{"network": "Network", "code": "PLACEHOLDER"}],
              "regions": {"Region name": {k: 0 for k in REGION_KEYS}},
              "kb": [{"id": f"XX{i}", "topic": tp, "source": "Document name (placeholder)", "text": "Passage text", "status": "placeholder"}
                     for i, tp in enumerate(TOPICS, 1)]})
    return t


TXT = {
    "en": {"h": "Country Pack", "none": "No country pack for this country yet. The app uses Tanzania defaults. Add a pack_<code>.json file to onboard it.",
           "status": "Data status", "reg": "Regions", "kb": "Policy passages", "ph": "placeholders", "law": "Data law", "regu": "Regulator",
           "his": "Health information system", "ok": "Pack is complete and valid.", "bad": "Pack has problems",
           "up": "Check a new country pack (JSON)", "tpl": "Download blank pack template", "valid": "Valid pack", "langs": "Languages"},
    "sw": {"h": "Kifurushi cha Nchi", "none": "Hakuna kifurushi cha nchi hii bado. Programu inatumia chaguo-msingi za Tanzania. Ongeza faili pack_<code>.json.",
           "status": "Hali ya data", "reg": "Mikoa", "kb": "Vifungu vya sera", "ph": "vya mfano", "law": "Sheria ya data", "regu": "Mdhibiti",
           "his": "Mfumo wa taarifa za afya", "ok": "Kifurushi kimekamilika na ni sahihi.", "bad": "Kifurushi kina matatizo",
           "up": "Kagua kifurushi kipya cha nchi (JSON)", "tpl": "Pakua kiolezo tupu", "valid": "Kifurushi sahihi", "langs": "Lugha"},
}


def render_country_panel(pack, lang):
    import streamlit as st
    x = TXT[lang]
    st.header(f"🌍 {x['h']}")
    if not pack:
        st.info(x["none"])
    else:
        n_ph = sum(q.get("status") == "placeholder" for q in pack["kb"])
        c = st.columns(3)
        c[0].metric(x["status"], pack["data_status"])
        c[1].metric(x["reg"], len(pack["regions"]))
        c[2].metric(x["kb"], f"{len(pack['kb'])} ({n_ph} {x['ph']})")
        st.caption(f"{x['langs']}: {', '.join(pack['languages'])} | {x['law']}: {pack['data_law']} | {x['regu']}: {pack['regulator']} | {x['his']}: {pack['health_information_system']}")
        if pack.get("data_note"):
            st.caption(f"🧪 {pack['data_note']}")
        problems = validate_pack(pack)
        (st.success if not problems else st.error)(x["ok"] if not problems else f"{x['bad']}: {'; '.join(problems[:3])}")
    up = st.file_uploader(x["up"], type="json", key="pack_upload")
    if up is not None:
        try:
            p = json.load(up)
            probs = validate_pack(p)
            if probs:
                st.error(f"{x['bad']} ({len(probs)})")
                for q in probs[:15]:
                    st.write(f"- {q}")
            else:
                st.success(f"{x['valid']}: {p['name']}, {len(p['regions'])} {x['reg'].lower()}, {len(p['kb'])} {x['kb'].lower()}")
        except Exception as e:
            st.error(f"Could not read the file: {e}")
    st.download_button(x["tpl"], json.dumps(template_pack(), indent=1), file_name="pack_template.json", key="pack_tpl")
