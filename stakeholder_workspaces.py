"""Stakeholder-oriented views over existing EcoHealth Sentinel context.

This module adds a presentation layer only. It does not alter source records,
country packs, risk rules, authentication or existing dashboards.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st
from policy_evidence import build_evidence_note
from research_laboratory import render_data_quality_panel, render_research_laboratory


ROLE_COPY = {
    "en": {
        "policymaker": ("Policy and planning", "Focus on national context, indicator provenance, reference periods and evidence gaps."),
        "chw": ("District and community operations", "Use the selected geography as context only. Confirm local facility and community data through authorised systems."),
        "researcher": ("Research and analysis", "Inspect definitions, facets, missingness, units and reproducible extracts before analysis."),
        "ngo": ("Programme and civil-society view", "Review contextual needs and evidence gaps. Do not infer beneficiary counts or programme impact from aggregate indicators."),
    },
    "sw": {
        "policymaker": ("Sera na mipango", "Zingatia muktadha wa kitaifa, chanzo cha kiashiria, kipindi na mapungufu ya ushahidi."),
        "chw": ("Uendeshaji wa wilaya na jamii", "Tumia eneo lililochaguliwa kama muktadha tu. Hakiki data za vituo na jamii kupitia mifumo iliyoidhinishwa."),
        "researcher": ("Utafiti na uchambuzi", "Kagua ufafanuzi, vyanzo, data zinazokosekana, vipimo na data zinazoweza kurudiwa."),
        "ngo": ("Programu na mashirika ya kiraia", "Kagua mahitaji ya muktadha na mapungufu ya ushahidi. Usikadirie wanufaika au athari kutokana na takwimu za jumla."),
    },
}


def render_stakeholder_workspaces(lang: str, role: str, country: str, region: str, data: dict, frame: pd.DataFrame | None = None) -> None:
    sw = lang == "sw"
    tr = lambda en, sw_text: sw_text if sw else en
    st.header(tr("Stakeholder intelligence workspace", "Eneo la Taarifa kwa Wadau"))
    st.caption(tr("Integrated public-health intelligence for government, researchers, health workers and civil-society organisations.", "Taarifa jumuishi za afya ya umma kwa serikali, watafiti, wahudumu wa afya na mashirika ya kiraia."))
    title, description = ROLE_COPY.get(lang, ROLE_COPY["en"]).get(role, ROLE_COPY["en"]["researcher"])
    st.subheader(title)
    st.write(description)
    st.caption(tr(f"Current context: {region}, {country}. Existing country-pack values remain demonstration data unless separately verified.", f"Muktadha: {region}, {country}. Thamani za country pack ni za majaribio isipokuwa zithibitishwe kando."))
    st.warning(tr("Do not use the existing illustrative dashboard values for operational decisions. The authentication and role selector are prototype controls, not production access control.", "Usitumie thamani za mfano kwenye dashibodi kwa maamuzi ya uendeshaji. Uthibitishaji na uchaguzi wa jukumu ni wa mfano, si udhibiti halisi wa ruhusa."))
    a, b, c = st.tabs([tr("Decision support", "Msaada wa maamuzi"), tr("Data quality", "Ubora wa data"), tr("Research workspace", "Eneo la utafiti")])
    with a:
        st.subheader(tr("Current indicator context", "Muktadha wa viashiria"))
        keys = ["mal", "mal_pos", "cholera", "tb", "fic", "anc4", "mmr", "htn", "dm", "stockout", "oop"]
        rows = [{"indicator_key": key, "display_value": data.get(key), "status": "DEMO / UNVERIFIED"} for key in keys if key in data]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.info(tr("This panel does not assign performance status or compare values with policy targets. A verified indicator definition, source, unit, period and target are required first.", "Sehemu hii haitoi alama ya utendaji wala kulinganisha na malengo. Ufafanuzi, chanzo, kipimo, kipindi na lengo lililothibitishwa vinahitajika kwanza."))
        st.markdown("**Evidence note / Dokezo la ushahidi**")
        st.text(build_evidence_note(frame, country, region))
    with b:
        render_data_quality_panel(frame, lang)
    with c:
        render_research_laboratory(frame, lang)
