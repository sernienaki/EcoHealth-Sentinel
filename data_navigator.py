"""Plain-language UN data navigation and source discovery UI."""
from __future__ import annotations
import streamlit as st
from indicator_glossary import render_glossary
from un_sdg_api import render_sdg_explorer
from un_data_sources import SOURCE_REGISTRY

def render_data_navigator(lang: str = "en") -> None:
    sw = lang == "sw"
    tr = lambda en, kis: kis if sw else en
    st.header(tr("UN Data Navigator", "Mwongozo wa Takwimu za UN"))
    st.caption(tr("Find data, understand what it means, and see what it cannot tell you.", "Tafuta takwimu, elewa maana yake na mipaka yake."))
    st.info(tr("This tool explains statistics in everyday language. It does not replace official definitions or create missing data.", "Zana hii inaeleza takwimu kwa lugha rahisi. Haichukui nafasi ya ufafanuzi rasmi wala kutengeneza data ambazo hazipo."))
    tabs = st.tabs([tr("SDG data explorer", "Chunguza data za SDG"), tr("Understand indicators", "Elewa viashiria"), tr("UN data sources", "Vyanzo vya data za UN")])
    with tabs[0]:
        render_sdg_explorer(lang)
    with tabs[1]:
        render_glossary(lang)
    with tabs[2]:
        st.write(tr("Connector status tells you what is technically connected. A source listed as discovery-only is not yet connected to the application.", "Hali ya kiunganishi inaonyesha kilichounganishwa kiteknolojia. Chanzo kilichoandikwa discovery-only bado hakijaunganishwa na programu."))
        for source in SOURCE_REGISTRY:
            with st.expander(source["name"] + " — " + source["status"]):
                st.write(source["domain"])
                st.write(source["coverage_note"])
                st.warning(source["caveat"])
                st.markdown(f"[{tr('Open official source', 'Fungua chanzo rasmi')}]({source['url']})")
