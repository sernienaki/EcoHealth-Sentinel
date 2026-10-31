"""Unit tests: run with pytest -q."""
from policy_deliberation import Scenario, EvidenceItem, build_deliberation, retrieve_evidence, AGENT_PROFILES

def test_scenario_requires_specific_question():
    try: Scenario(question="short")
    except Exception: return
    raise AssertionError("Short policy questions must be rejected")

def test_expected_agent_perspectives_and_human_review():
    report = build_deliberation(Scenario(question="How should a district prioritise cholera response?"), [])
    assert {a.agent_id for a in report.arguments} == set(AGENT_PROFILES)
    assert report.human_review_required is True
    assert report.mode == "deterministic_prototype"

def test_empty_evidence_is_explicit():
    report = build_deliberation(Scenario(question="How should a district prioritise cholera response?"), [])
    assert report.evidence_gaps
    assert "No relevant indexed passages" in report.arguments[0].rationale

def test_evidence_provenance_is_retained():
    evidence = [EvidenceItem(evidence_id="doc-1-4-0", source="Guideline, page 4", excerpt="Example", page=4)]
    report = build_deliberation(Scenario(question="How should a district prioritise cholera response?"), evidence)
    assert report.arguments[0].supporting_evidence[0].page == 4
    assert report.arguments[0].supporting_evidence[0].evidence_id == "doc-1-4-0"

def test_retrieval_abstains_without_index():
    assert retrieve_evidence("cholera response", index=None) == []
