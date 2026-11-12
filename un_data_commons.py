"""UN System Data Commons REST API client and Streamlit panel.

The UN deployment is a Custom Data Commons instance. Its documented REST V2
base URL ends in /core/api/v2/ and does not require the public API key.
"""
from __future__ import annotations

import os
from typing import Any, Iterable

import pandas as pd
import requests
import streamlit as st
import plotly.express as px

DEFAULT_BASE_URL = (
    "https://unsd-datacommons.gcp.un-icc.cloud/core/api/v2"
)
BASE_URL = os.getenv("UN_DATA_COMMONS_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
TIMEOUT_SECONDS = 30


class UNDataCommonsError(RuntimeError):
    """Raised when the UN System Data Commons API cannot be queried."""


def _get_json(endpoint: str, params: Iterable[tuple[str, str]]) -> dict[str, Any]:
    """Perform a bounded GET request against the configured custom instance."""
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    try:
        response = requests.get(
            url,
            params=list(params),
            timeout=TIMEOUT_SECONDS,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise UNDataCommonsError(f"UN Data Commons request failed: {exc}") from exc
    except ValueError as exc:
        raise UNDataCommonsError("UN Data Commons returned invalid JSON.") from exc

    if not isinstance(payload, dict):
        raise UNDataCommonsError("UN Data Commons returned an unexpected response.")
    return payload


def resolve_indicators(query: str) -> list[dict[str, Any]]:
    """Search statistical variables using the documented indicator resolver."""
    query = (query or "").strip()
    if not query:
        return []
    payload = _get_json(
        "resolve",
        [("nodes", query), ("resolver", "indicator")],
    )
    candidates: list[dict[str, Any]] = []
    for entity in payload.get("entities", []):
        for candidate in entity.get("candidates", []):
            types = candidate.get("typeOf", [])
            if "StatisticalVariable" in types or not types:
                candidates.append({
                    "query": entity.get("node", query),
                    "dcid": candidate.get("dcid", ""),
                    "description": candidate.get("metadata", {}).get("sentence", ""),
                    "score": candidate.get("metadata", {}).get("score"),
                    "type_of": types,
                })
    return [item for item in candidates if item["dcid"]]


def fetch_observations(
    entity_dcid: str,
    variable_dcids: str | list[str],
    date: str = "LATEST",
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Fetch observations and retain facet-level source provenance.

    Multiple facets are kept as separate rows. Callers must not sum or combine
    them unless they first select a compatible source/methodology.
    """
    entity_dcid = (entity_dcid or "").strip()
    if not entity_dcid:
        raise ValueError("An entity DCID is required.")

    if isinstance(variable_dcids, str):
        variables = [variable_dcids.strip()]
    else:
        variables = [str(value).strip() for value in variable_dcids]
    variables = [value for value in variables if value]
    if not variables:
        raise ValueError("At least one variable DCID is required.")

    selected_date = (date or "LATEST").strip().upper()
    if selected_date not in {"LATEST", "ALL"}:
        # Data Commons accepts ISO date strings for the target variable's
        # date granularity; preserve user-supplied values such as 2022 or 2022-12.
        selected_date = (date or "").strip()

    params: list[tuple[str, str]] = [
        ("entity.dcids", entity_dcid),
        ("select", "date"),
        ("select", "value"),
        ("select", "entity"),
        ("select", "variable"),
        ("select", "facet"),
    ]
    params.extend(("variable.dcids", variable) for variable in variables)
    if selected_date:
        params.append(("date", "" if selected_date == "ALL" else selected_date))

    payload = _get_json("observation", params)
    facets = payload.get("facets", {}) or {}
    records: list[dict[str, Any]] = []

    for variable_dcid, variable_data in (payload.get("byVariable", {}) or {}).items():
        for entity_id, entity_data in (variable_data.get("byEntity", {}) or {}).items():
            for facet in entity_data.get("orderedFacets", []) or []:
                facet_id = str(facet.get("facetId", ""))
                facet_meta = facets.get(facet_id, {}) or {}
                for observation in facet.get("observations", []) or []:
                    records.append({
                        "entity_dcid": entity_id,
                        "variable_dcid": variable_dcid,
                        "date": observation.get("date"),
                        "value": observation.get("value"),
                        "facet_id": facet_id,
                        "dataset": facet_meta.get("importName"),
                        "provenance_url": facet_meta.get("provenanceUrl"),
                        "unit": facet_meta.get("unit"),
                        "measurement_method": facet_meta.get("measurementMethod"),
                        "observation_period": facet_meta.get("observationPeriod"),
                        "scaling_factor": facet_meta.get("scalingFactor"),
                        "is_dc_aggregate": facet_meta.get("isDcAggregate"),
                    })

    frame = pd.DataFrame(records)
    if not frame.empty:
        frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
        frame["date"] = frame["date"].astype(str)
    return frame, payload


def render_un_data_intelligence(lang: str = "en") -> None:
    """Render the bilingual UN Data Intelligence tab."""
    sw = lang == "sw"
    tr = lambda en, kis: kis if sw else en

    st.header(tr("UN Data Intelligence", "Taarifa za Takwimu za Umoja wa Mataifa"))
    st.caption(tr(
        "Explore official statistical observations from the UN System Data Commons. "
        "This is a contextual statistics source, not a live DHIS2 feed.",
        "Chunguza takwimu rasmi kutoka UN System Data Commons. Hii ni chanzo cha "
        "takwimu za muktadha, si mtiririko wa moja kwa moja wa DHIS2.",
    ))
    st.info(tr(
        "Values are shown by source facet. Different datasets or methods may produce "
        "different values for the same variable. Select and interpret sources before comparison.",
        "Thamani zinaonyeshwa kwa kila chanzo. Seti au mbinu tofauti zinaweza kutoa "
        "thamani tofauti kwa kiashiria kilekile. Chagua na tathmini chanzo kabla ya kulinganisha.",
    ))

    col1, col2 = st.columns(2)
    with col1:
        entity_dcid = st.text_input(
            tr("Geographic entity DCID", "DCID ya eneo"),
            value="country/TZA",
            help=tr("Tanzania is represented as country/TZA.", "Tanzania inawakilishwa kama country/TZA."),
            key="un_dc_entity",
        )
    with col2:
        variable_query = st.text_input(
            tr("Search for an indicator", "Tafuta kiashiria"),
            value="population",
            key="un_dc_variable_query",
        )

    if st.button(tr("Search variables", "Tafuta viashiria"), key="un_dc_search"):
        try:
            st.session_state["un_dc_candidates"] = resolve_indicators(variable_query)
            st.session_state["un_dc_search_error"] = ""
        except (UNDataCommonsError, ValueError) as exc:
            st.session_state["un_dc_candidates"] = []
            st.session_state["un_dc_search_error"] = str(exc)

    if st.session_state.get("un_dc_search_error"):
        st.error(st.session_state["un_dc_search_error"])

    candidates = st.session_state.get("un_dc_candidates", [])
    if not candidates:
        st.caption(tr(
            "Search for a variable to discover its DCID. Verify its definition and coverage before querying.",
            "Tafuta kiashiria ili kupata DCID yake. Hakiki ufafanuzi na upatikanaji kabla ya kuuliza.",
        ))
        return

    labels = {
        f"{item['description'] or item['dcid']} — {item['dcid']}": item["dcid"]
        for item in candidates
    }
    selected_label = st.selectbox(
        tr("Select a statistical variable", "Chagua kiashiria cha takwimu"),
        list(labels),
        key="un_dc_selected_variable",
    )
    selected_variable = labels[selected_label]
    date_choice = st.selectbox(
        tr("Observation period", "Kipindi cha takwimu"),
        ["LATEST", "ALL"],
        format_func=lambda value: tr("Latest available", "Takwimu za karibuni") if value == "LATEST"
        else tr("All available years", "Miaka yote inayopatikana"),
        key="un_dc_date_choice",
    )

    if st.button(tr("Retrieve observations", "Pata takwimu"), key="un_dc_fetch"):
        try:
            frame, raw = fetch_observations(entity_dcid, selected_variable, date_choice)
            st.session_state["un_dc_frame"] = frame
            st.session_state["un_dc_raw"] = raw
            st.session_state["un_dc_fetch_error"] = ""
        except (UNDataCommonsError, ValueError) as exc:
            st.session_state["un_dc_fetch_error"] = str(exc)
            st.session_state.pop("un_dc_frame", None)

    if st.session_state.get("un_dc_fetch_error"):
        st.error(st.session_state["un_dc_fetch_error"])

    frame = st.session_state.get("un_dc_frame")
    if frame is None:
        return
    if frame.empty:
        st.warning(tr(
            "No observations were returned for this entity and variable. Check the DCIDs and available coverage.",
            "Hakuna takwimu zilizorejeshwa kwa eneo na kiashiria hiki. Hakiki DCID na upatikanaji.",
        ))
        return

    st.success(tr(
        f"Retrieved {len(frame):,} observation(s).",
        f"Imepatikana rekodi {len(frame):,} za takwimu.",
    ))
    st.dataframe(frame, use_container_width=True, hide_index=True)

    available_facets = frame["facet_id"].dropna().unique().tolist()
    if len(available_facets) > 1:
        st.warning(tr(
            "Multiple source facets were returned. They are not combined. Filter to one facet for a consistent series.",
            "Vyanzo vingi vimerudishwa. Havijaunganishwa. Chuja chanzo kimoja kwa mfululizo unaolingana.",
        ))
        facet_options = ["All facets"] + available_facets
        chosen_facet = st.selectbox(
            tr("Source facet", "Chanzo cha takwimu"),
            facet_options,
            key="un_dc_facet",
        )
        chart_frame = frame if chosen_facet == "All facets" else frame[frame["facet_id"] == chosen_facet]
    else:
        chart_frame = frame

    if not chart_frame.empty and chart_frame["date"].nunique() > 1:
        chart_frame = chart_frame.sort_values("date")
        fig = px.line(
            chart_frame,
            x="date",
            y="value",
            color="facet_id" if chart_frame["facet_id"].nunique() > 1 else None,
            markers=True,
            title=tr("Observed values over time", "Mwenendo wa takwimu kwa muda"),
        )
        fig.update_layout(xaxis_title=tr("Reference period", "Kipindi"), yaxis_title=tr("Reported value", "Thamani"))
        st.plotly_chart(fig, use_container_width=True)

    csv = frame.to_csv(index=False).encode("utf-8")
    st.download_button(
        tr("Download observations (CSV)", "Pakua takwimu (CSV)"),
        data=csv,
        file_name="un_data_commons_observations.csv",
        mime="text/csv",
        key="un_dc_download",
    )
    st.caption(tr(
        "Source: UN System Data Commons. Review dataset, provenance URL, unit, measurement method and reference period before policy use.",
        "Chanzo: UN System Data Commons. Kagua seti ya data, URL ya chanzo, kipimo, mbinu na kipindi kabla ya matumizi ya sera.",
    ))
