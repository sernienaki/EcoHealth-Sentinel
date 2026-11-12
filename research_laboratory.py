"""Research-facing exploration and export for UN aggregate observations."""
from __future__ import annotations

import pandas as pd
import streamlit as st
import plotly.express as px
from data_quality import assess_observations
from indicator_interpretation import describe_indicator


def render_research_laboratory(frame: pd.DataFrame | None, lang: str = "en") -> None:
    sw = lang == "sw"
    tr = lambda en, sw_text: sw_text if sw else en
    st.subheader(tr("Research & data laboratory", "Maabara ya Utafiti na Takwimu"))
    if frame is None or frame.empty:
        st.info(tr("Retrieve observations in the UN Data Intelligence tab first. This workspace does not create data.", "Pata takwimu kwanza kwenye kichupo cha UN Data Intelligence. Sehemu hii haitengenezi data."))
        return
    st.caption(tr("Explore the retrieved aggregate observations. The source response remains unchanged.", "Chunguza takwimu za jumla zilizopatikana. Majibu ya chanzo hayabadilishwi."))
    view = frame.copy()
    facets = view["facet_id"].dropna().astype(str).unique().tolist() if "facet_id" in view else []
    selected_facets = st.multiselect(tr("Filter source facets", "Chuja vyanzo"), facets, default=facets[:1] if facets else [])
    if selected_facets and "facet_id" in view:
        view = view[view["facet_id"].astype(str).isin(selected_facets)]
    st.metric(tr("Rows in current view", "Idadi ya rekodi"), f"{len(view):,}")
    st.dataframe(view, use_container_width=True, hide_index=True)
    quality = assess_observations(view)
    with st.expander(tr("Structural data diagnostics", "Ukaguzi wa muundo wa data"), expanded=True):
        st.json(quality)
    if {"date", "value"}.issubset(view.columns):
        chart = view.copy()
        chart["value"] = pd.to_numeric(chart["value"], errors="coerce")
        chart = chart.dropna(subset=["value"])
        if not chart.empty:
            st.plotly_chart(px.line(chart.sort_values("date"), x="date", y="value", color="facet_id" if chart["facet_id"].nunique() > 1 else None, markers=True, title=tr("Observed values by period", "Thamani zilizoripotiwa kwa kipindi")), use_container_width=True)
    if {"entity_dcid", "variable_dcid"}.issubset(view.columns):
        entities = view["entity_dcid"].dropna().astype(str).unique().tolist()
        variables = view["variable_dcid"].dropna().astype(str).unique().tolist()
        if entities and variables:
            entity = st.selectbox(tr("Entity", "Eneo"), entities, key="research_entity")
            variable = st.selectbox(tr("Variable", "Kiashiria"), variables, key="research_variable")
            summary = describe_indicator(view, entity, variable)
            st.markdown(tr("Descriptive summary", "Muhtasari wa maelezo"))
            st.json(summary)
    st.download_button(tr("Download current view (CSV)", "Pakua data (CSV)"), view.to_csv(index=False).encode("utf-8"), file_name="ecohealth_research_extract.csv", mime="text/csv")


def render_data_quality_panel(frame: pd.DataFrame | None, lang: str = "en") -> None:
    tr = (lambda en, sw_text: sw_text if lang == "sw" else en)
    st.subheader(tr("Data quality & trust centre", "Kituo cha Ubora na Uaminifu wa Data"))
    if frame is None or frame.empty:
        st.info(tr("No UN observations are loaded in this session.", "Hakuna takwimu za UN zilizopakiwa kwenye kipindi hiki."))
        return
    q = assess_observations(frame)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(tr("Observation rows", "Rekodi"), q["row_count"])
    c2.metric(tr("Source facets", "Vyanzo"), q["facet_count"])
    c3.metric(tr("Duplicate-key rows", "Rekodi rudufu"), q["duplicate_key_rows"])
    c4.metric(tr("Required-field completeness", "Ukamilifu wa sehemu muhimu"), f'{q["required_field_completeness_pct"]}%' if q["required_field_completeness_pct"] is not None else "N/A")
    st.json(q)
    st.warning(tr("These are structural checks, not an accuracy score. Confirm source, definition, reference period, geographic level, unit and methodology before using the observations.", "Huu ni ukaguzi wa muundo tu, si alama ya usahihi. Hakiki chanzo, ufafanuzi, kipindi, eneo, kipimo na mbinu kabla ya kutumia takwimu."))
