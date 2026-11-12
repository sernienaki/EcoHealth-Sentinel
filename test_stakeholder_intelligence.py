"""Tests for stakeholder intelligence and structural diagnostics."""
import pandas as pd
from data_quality import assess_observations
from indicator_interpretation import describe_indicator
from policy_evidence import build_evidence_note


def sample():
    return pd.DataFrame([
        {"entity_dcid":"country/TZA","variable_dcid":"Count_Person","date":"2021","value":60,"facet_id":"f1","unit":"person","provenance_url":"https://example.org/a"},
        {"entity_dcid":"country/TZA","variable_dcid":"Count_Person","date":"2022","value":62,"facet_id":"f1","unit":"person","provenance_url":"https://example.org/a"},
    ])


def test_quality_reports_structure_not_score():
    q = assess_observations(sample())
    assert q["row_count"] == 2
    assert q["facet_count"] == 1
    assert q["required_field_completeness_pct"] == 100.0
    assert "not a validation" in q["quality_scope"]


def test_quality_detects_missing_columns_and_duplicate_keys():
    frame = pd.concat([sample(), sample().iloc[[0]]], ignore_index=True)
    q = assess_observations(frame.drop(columns=["unit"]))
    assert q["duplicate_key_rows"] == 2
    assert "unit" not in q["missing_required_columns"]


def test_indicator_summary_is_descriptive():
    result = describe_indicator(sample(), "country/TZA", "Count_Person")
    assert result["status"] == "descriptive_only"
    assert result["latest_value"] == 62
    assert result["absolute_change_first_to_last"] == 2
    assert "does not establish causality" in result["message"]


def test_evidence_note_does_not_invent_findings():
    note = build_evidence_note(None, "Tanzania", "Moshi")
    assert "none loaded" in note
    assert "No source-backed statistical finding" in note
