"""Tests for EcoHealth Sentinel. Run with: python test_ecohealth.py  (or pytest). No Streamlit needed."""
import datetime
import numpy as np
import packs
import evals
import aci
import rag
import viz
import outbreak as ob
from agents import DEFAULT_CTX

TZ, KE = packs.load_pack("tz"), packs.load_pack("ke")
FILL = "Section text about general administrative arrangements and definitions used across the document for testing only. " * 6


def test_packs_valid():
    assert packs.validate_pack(TZ) == [] and packs.validate_pack(KE) == []
    broken = packs.load_pack("ke")
    del broken["regions"]["Nairobi"]["tb"]
    assert any("tb" in p for p in packs.validate_pack(broken))


def test_kenya_is_labeled_placeholder():
    assert KE["data_status"] == "placeholder" and all(q["status"] == "placeholder" for q in KE["kb"])


def test_evaluation_suite_tanzania():
    for toolset in ("legacy", "aci"):
        rows = evals.run_eval(TZ["regions"], None, packs.context(TZ), toolset)
        assert all(r["pass"] for r in rows), [r["id"] for r in rows if not r["pass"]]


def test_evaluation_suite_kenya_safety_and_alignment():
    s = evals.summarize(evals.run_eval(KE["regions"], None, packs.context(KE), "aci"))
    assert s["Safety %"] == 100 and s["Alignment %"] == 100 and s["Robustness %"] == 100


def test_aci_contract():
    for pack in (TZ, KE):
        assert all(t["pass"] for t in aci.aci_selftests(pack["regions"], packs.context(pack)))


def test_aci_blocks_bad_answers():
    _, summary = evals.run_aci_eval(TZ["regions"], packs.context(TZ))
    assert summary["aci"]["Fabricated citations"] == 0 and summary["aci"]["Wrong risk accepted"] == 0
    assert summary["aci"]["Success %"] > summary["legacy"]["Success %"]


def test_rag_index_and_abstention():
    pages = [(i, FILL) for i in range(1, 4)] + [(4, "Personal Data Protection Commission shall supervise compliance. " + FILL), (5, "Cholera outbreak response arrangements. " + FILL)]
    idx = rag.Index(rag.chunk_pages({"id": "d", "title": "Doc", "status": "t"}, pages))
    assert idx.search("Personal Data Protection Commission", 3)[0]["page"] == 4
    assert idx.search("What is the capital of France?", 3) == []


def test_viz_logic():
    assert viz.severity("fic", 88, 90, "higher", 100) == 1
    assert viz.severity("fic", 70, 90, "higher", 100) == 2
    assert viz.severity("cholera", 450, 0, "lower", 100) == 3
    s, simulated = viz.weekly_series("tz", "Mwanza", "cholera", 210, True)
    s2, _ = viz.weekly_series("tz", "Mwanza", "cholera", 210, True)
    assert simulated and (s == s2).all() and np.isnan(viz.ears_threshold(s)[0])


def test_outbreak_exposure():
    T = ob.load_threats()
    ebola, marburg, mpox = T["threats"][0], T["threats"][1], T["threats"][2]
    assert ob.exposure(ebola, TZ, "Arusha")[0] == 3 and ob.exposure(ebola, TZ, "Dodoma")[0] == 2
    assert ob.exposure(ebola, KE, "Nairobi")[0] == 4
    assert ob.exposure(marburg, TZ, "Arusha")[0] == -1 and ob.exposure(mpox, TZ, "Arusha")[0] == 0


def test_outbreak_rapid_risk_uses_readiness():
    ebola = ob.load_threats()["threats"][0]
    assert ob.rapid_risk(ebola, TZ, "Arusha", None)["category"] == "HIGH"
    assert ob.rapid_risk(ebola, TZ, "Arusha", 0.2)["category"] == "CRITICAL"


def test_triage_rules():
    assert ob.triage({"fever", "bleeding"}, set())["level"] == 3
    assert ob.triage({"fever", "headache", "vomiting", "diarrhea"}, {"travel"})["level"] == 3
    assert ob.triage({"fever", "headache", "vomiting", "diarrhea"}, set())["level"] == 2
    assert ob.triage({"rash", "fever"}, {"contact_rash"})["level"] == 3
    assert ob.triage({"watery"}, set())["syndrome"] == "cholera"
    assert ob.triage({"headache"}, set())["level"] == 0


def test_countdown_and_readiness():
    cd = ob.countdown(datetime.date(2026, 10, 18), datetime.date(2026, 10, 20), 42)
    assert cd["remaining"] == 40 and cd["end_date"] == datetime.date(2026, 11, 29) and not cd["complete"]
    assert ob.readiness_scores({f"{d}.{i}": True for d, i in ob.ITEM_IDS})[0] == 1.0
    assert ob.readiness_from_state({}, "tz", "Arusha") is None


def test_threat_board_is_sourced_and_dated():
    T = ob.load_threats()
    assert T["as_of"] and all(t["sources"] and all(s["url"].startswith("http") and s["date"] for s in t["sources"]) for t in T["threats"])


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print("PASS", name)
        except Exception as e:
            failed += 1
            print("FAIL", name, repr(e))
    print(f"{len(tests) - failed} of {len(tests)} tests passed")
    raise SystemExit(1 if failed else 0)
