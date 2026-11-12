"""Read-only connector for the UN Statistics Division SDG API.

Only documented GET endpoints are used. API response fields are preserved where
possible; this connector does not claim the returned value is current or locally
representative. Tanzania's UN M49 area code is 834.
"""
from __future__ import annotations
import os
from typing import Any
import requests
import pandas as pd

DEFAULT_BASE_URL = "https://unstats.un.org/SDGAPI"
BASE_URL = os.getenv("UN_SDG_API_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
TIMEOUT_SECONDS = 25
TANZANIA_M49 = "834"

class UNSDGAPIError(RuntimeError):
    """Raised for SDG API transport or response errors."""

def _get_json(path: str, params: dict[str, Any] | None = None) -> Any:
    try:
        response = requests.get(
            f"{BASE_URL}/{path.lstrip('/')}",
            params=params or {},
            timeout=TIMEOUT_SECONDS,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise UNSDGAPIError(f"UN SDG API request failed: {exc}") from exc
    except ValueError as exc:
        raise UNSDGAPIError("UN SDG API returned invalid JSON.") from exc

def list_goals() -> list[dict[str, Any]]:
    payload = _get_json("v1/sdg/Goal/List", {"includechildren": "true"})
    if not isinstance(payload, list):
        raise UNSDGAPIError("Unexpected SDG goals response format.")
    return payload

def list_indicators() -> list[dict[str, Any]]:
    payload = _get_json("v1/sdg/Indicator/List")
    if not isinstance(payload, list):
        raise UNSDGAPIError("Unexpected SDG indicator response format.")
    return payload

def list_series_for_indicator(indicator_code: str) -> list[dict[str, Any]]:
    code = (indicator_code or "").strip()
    if not code or "/" in code or ".." in code:
        raise ValueError("A valid indicator code is required.")
    payload = _get_json(f"v1/sdg/Indicator/{code}/Series/List")
    if not isinstance(payload, list):
        raise UNSDGAPIError("Unexpected SDG series response format.")
    return payload

def fetch_series_for_area(series_code: str, area_code: str = TANZANIA_M49) -> pd.DataFrame:
    """Fetch the documented country/region time-series slice for one SDG series."""
    code = (series_code or "").strip()
    area = (area_code or "").strip()
    if not code or "/" in code or ".." in code:
        raise ValueError("A valid SDG series code is required.")
    if not area.isdigit():
        raise ValueError("Geography code must be numeric (UN M49).")
    payload = _get_json(f"v1/sdg/Series/{code}/GeoArea/{area}/DataSlice")
    if isinstance(payload, dict):
        rows = payload.get("data", [])
    elif isinstance(payload, list):
        rows = payload
    else:
        raise UNSDGAPIError("Unexpected SDG observations response format.")
    if not isinstance(rows, list):
        raise UNSDGAPIError("SDG observations are not returned as a list.")
    frame = pd.DataFrame(rows)
    if not frame.empty and "value" in frame:
        frame["value_numeric"] = pd.to_numeric(frame["value"], errors="coerce")
    return frame

def render_sdg_explorer(lang: str = "en") -> None:
    import streamlit as st
    sw = lang == "sw"
    tr = lambda en, kis: kis if sw else en
    st.subheader(tr("UN Sustainable Development Goals data", "Takwimu za Malengo ya Maendeleo Endelevu ya UN"))
    st.caption(tr("Browse official SDG indicators and observations reported by custodian agencies.", "Chunguza viashiria rasmi vya SDG na takwimu zilizoripotiwa na taasisi husika."))
    area = st.text_input(tr("UN M49 geography code", "Msimbo wa eneo wa UN M49"), value=TANZANIA_M49, key="sdg_area_code")
    try:
        goals = list_goals()
    except UNSDGAPIError as exc:
        st.error(str(exc))
        st.caption(tr("The SDG service may be temporarily unavailable. Existing EcoHealth Sentinel modules remain usable.", "Huduma ya SDG huenda haipatikani kwa muda. Vipengele vingine vya EcoHealth Sentinel vinaendelea kupatikana."))
        return
    if not goals:
        st.info(tr("No goals were returned by the API.", "API haikurudisha malengo."))
        return
    goal_labels = {f"{g.get('code','')} — {g.get('title','')}": g for g in goals}
    selected_goal_label = st.selectbox(tr("Choose a development goal", "Chagua lengo la maendeleo"), list(goal_labels), key="sdg_goal")
    goal = goal_labels[selected_goal_label]
    indicators = []
    for target in goal.get("targets", []) or []:
        indicators.extend(target.get("indicators", []) or [])
    if not indicators:
        st.info(tr("The API did not return indicator details for this goal. Use the official metadata link.", "API haikurudisha maelezo ya viashiria vya lengo hili. Tumia kiungo rasmi cha metadata."))
        st.link_button(tr("Open official SDG metadata", "Fungua metadata rasmi za SDG"), "https://unstats.un.org/sdgs/metadata/")
        return
    options = []
    for ind in indicators:
        for serie in ind.get("series", []) or []:
            options.append((f"{ind.get('code','')} | {ind.get('description','')} | {serie.get('code','')} | {serie.get('description','')}", serie.get("code",""), ind, serie))
    if not options:
        st.info(tr("No series are listed for this goal in the current API response.", "Hakuna mfululizo wa data uliorejeshwa kwa lengo hili."))
        return
    selected = st.selectbox(tr("Select an indicator series", "Chagua mfululizo wa kiashiria"), options, format_func=lambda x: x[0], key="sdg_series")
    _, series_code, indicator, series = selected
    st.markdown(f"**{tr('Official description','Maelezo rasmi')}:** {series.get('description') or indicator.get('description') or 'Not supplied'}")
    st.caption(tr("A series is a specific measurable version of an indicator. Different series may use different populations or breakdowns.", "Mfululizo ni namna maalumu ya kupima kiashiria. Mifululizo tofauti inaweza kutumia makundi au vipimo tofauti."))
    if st.button(tr("Retrieve Tanzania observations", "Pata takwimu za Tanzania"), key="sdg_fetch"):
        try:
            st.session_state["sdg_observations"] = fetch_series_for_area(series_code, area)
            st.session_state["sdg_fetch_error"] = ""
            st.session_state["sdg_selected_meta"] = {"goal": goal.get("title"), "indicator": indicator, "series": series, "area_code": area}
        except (UNSDGAPIError, ValueError) as exc:
            st.session_state["sdg_fetch_error"] = str(exc)
            st.session_state.pop("sdg_observations", None)
    if st.session_state.get("sdg_fetch_error"):
        st.error(st.session_state["sdg_fetch_error"])
    frame = st.session_state.get("sdg_observations")
    if frame is not None:
        if frame.empty:
            st.warning(tr("No observations were returned for this series and geography.", "Hakuna takwimu zilizorejeshwa kwa kiashiria na eneo hili."))
        else:
            st.dataframe(frame, use_container_width=True, hide_index=True)
            st.download_button(tr("Download SDG observations (CSV)", "Pakua takwimu za SDG (CSV)"), frame.to_csv(index=False).encode("utf-8"), "unsd_sdg_tanzania.csv", "text/csv")
            st.info(tr("Check the year, unit, disaggregation, source and footnotes before interpreting this result. The selected geography is the M49 code you entered.", "Kagua mwaka, kipimo, mgawanyo, chanzo na maelezo kabla ya kutafsiri. Eneo lililochaguliwa ni msimbo wa M49 ulioingiza."))
