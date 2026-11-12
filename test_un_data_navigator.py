"""Tests for the UN SDG connector and plain-language glossary."""
import pandas as pd
import pytest
import un_sdg_api
from indicator_glossary import get_explanation
from data_quality import assess_observations


def test_tanzania_m49_default():
    assert un_sdg_api.TANZANIA_M49 == "834"


def test_series_data_slice_normalises_records(monkeypatch):
    monkeypatch.setattr(un_sdg_api, "_get_json", lambda path: [
        {"series":"A", "geoAreaCode":"834", "timePeriodStart":2020, "value":"73.5"}
    ])
    frame = un_sdg_api.fetch_series_for_area("SERIES_A")
    assert frame.loc[0, "geoAreaCode"] == "834"
    assert frame.loc[0, "value_numeric"] == 73.5


def test_invalid_series_code_rejected_before_request(monkeypatch):
    called = []
    monkeypatch.setattr(un_sdg_api, "_get_json", lambda *a, **k: called.append(True))
    with pytest.raises(ValueError):
        un_sdg_api.fetch_series_for_area("../invalid")
    assert called == []


def test_empty_sdg_response_is_valid_empty_frame(monkeypatch):
    monkeypatch.setattr(un_sdg_api, "_get_json", lambda path: [])
    assert un_sdg_api.fetch_series_for_area("SERIES_A").empty


def test_glossary_has_english_and_swahili_explanations():
    en = get_explanation("basic_drinking_water", "en")
    sw = get_explanation("basic_drinking_water", "sw")
    assert en["simple_explanation"]
    assert sw["simple_explanation"]
    assert en["official_definition_required"] is True


def test_source_registry_marks_unimplemented_sources_as_discovery_only():
    from un_data_sources import SOURCE_REGISTRY
    by_id = {item["id"]: item for item in SOURCE_REGISTRY}
    assert by_id["unsd_sdg_api"]["status"] == "implemented_pr24"
    assert by_id["who_gho"]["status"] == "discovery_only"
    assert by_id["unicef_data"]["status"] == "discovery_only"


def test_goals_api_requires_list_response(monkeypatch):
    monkeypatch.setattr(un_sdg_api, "_get_json", lambda path, params=None: {"unexpected": []})
    with pytest.raises(un_sdg_api.UNSDGAPIError):
        un_sdg_api.list_goals()


def test_geo_code_must_be_numeric(monkeypatch):
    called = []
    monkeypatch.setattr(un_sdg_api, "_get_json", lambda *a, **k: called.append(True))
    with pytest.raises(ValueError):
        un_sdg_api.fetch_series_for_area("SERIES_A", "TZA")
    assert called == []
