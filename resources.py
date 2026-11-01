"""Link-based public Resource Library, separate from RAG indexing."""
from pathlib import Path
import json
import streamlit as st

CATALOGUE_PATH = Path(__file__).with_name("resource_catalogue.json")

LABELS = {
    "en": {"title":"Public Resource Library", "intro":"Browse official policies, strategies, legislation, surveillance guidance and public health resources. Documents remain hosted by their original publishers.", "search":"Search titles, publishers or keywords", "category":"Category", "all":"All categories", "language":"Language", "all_languages":"All languages", "count":"Resources listed", "view":"View resource", "pdf":"Open / download PDF", "no_pdf":"A direct PDF link has not been confirmed. Use the resource page.", "empty":"No resources match these filters.", "publisher":"Publisher", "year":"Publication year", "format":"Format", "source":"Source", "status":"Catalogue note", "not_stated":"Not stated / not confirmed", "notice":"External links are maintained by their publishers. Availability and download behaviour may change."},
    "sw": {"title":"Maktaba ya Rasilimali za Umma", "intro":"Vinjari sera rasmi, mikakati, sheria, miongozo ya ufuatiliaji na rasilimali za afya ya umma. Nyaraka zinahifadhiwa kwenye tovuti za wachapishaji wake.", "search":"Tafuta mada, wachapishaji au maneno muhimu", "category":"Aina ya rasilimali", "all":"Aina zote", "language":"Lugha", "all_languages":"Lugha zote", "count":"Rasilimali zilizoorodheshwa", "view":"Angalia rasilimali", "pdf":"Fungua / pakua PDF", "no_pdf":"Kiungo cha moja kwa moja cha PDF hakijathibitishwa. Tumia ukurasa wa rasilimali.", "empty":"Hakuna rasilimali zinazolingana na vichujio hivi.", "publisher":"Mchapishaji", "year":"Mwaka wa uchapishaji", "format":"Muundo", "source":"Chanzo", "status":"Maelezo ya katalogi", "not_stated":"Haujaelezwa / haujathibitishwa", "notice":"Viungo vya nje vinasimamiwa na wachapishaji wake. Upatikanaji na namna ya kupakua vinaweza kubadilika."}
}

def load_resources():
    with CATALOGUE_PATH.open("r", encoding="utf-8") as f:
        records = json.load(f)
    required = {"id", "title", "publisher", "country", "category", "language", "format", "url"}
    seen, valid = set(), []
    for item in records:
        if required.issubset(item) and item["id"] not in seen and str(item["url"]).startswith("https://"):
            seen.add(item["id"])
            valid.append(item)
    return valid

def render_resource_library(lang="en"):
    x = LABELS.get(lang, LABELS["en"])
    resources = load_resources()
    st.header("📚 " + x["title"])
    st.caption(x["intro"])
    st.caption(x["notice"])
    categories = sorted({r["category"] for r in resources})
    languages = sorted({r["language"] for r in resources})
    c1, c2, c3 = st.columns([2, 1, 1])
    query = c1.text_input(x["search"], key="public_resource_search")
    category = c2.selectbox(x["category"], [x["all"]] + categories, key="public_resource_category")
    language = c3.selectbox(x["language"], [x["all_languages"]] + languages, key="public_resource_language")
    q = query.strip().casefold()
    filtered = []
    for item in resources:
        haystack = " ".join(str(item.get(k, "")) for k in ("title", "subtitle", "publisher", "category", "description", "country", "source")).casefold()
        if q and q not in haystack: continue
        if category != x["all"] and item["category"] != category: continue
        if language != x["all_languages"] and item["language"] != language: continue
        filtered.append(item)
    st.metric(x["count"], len(filtered))
    if not filtered:
        st.info(x["empty"])
        return
    for item in filtered:
        with st.container(border=True):
            st.subheader(item["title"])
            if item.get("subtitle"): st.caption(item["subtitle"])
            st.write(item.get("description_sw" if lang == "sw" else "description", item.get("description", "")))
            st.caption(f"{x['publisher']}: {item['publisher']} · {x['year']}: {item.get('year') or x['not_stated']}")
            st.caption(f"{x['category']}: {item['category']} · {x['language']}: {item['language']} · {x['format']}: {item['format']}")
            left, right = st.columns(2)
            left.link_button(x["view"], item["url"], use_container_width=True)
            if item.get("direct_pdf_url"):
                right.link_button(x["pdf"], item["direct_pdf_url"], use_container_width=True)
            else:
                right.caption(x["no_pdf"])
            if item.get("status"): st.caption(f"{x['status']}: {item['status']}")
            st.caption(f"{x['source']}: {item.get('source', item['publisher'])}")
