"""Plain-language bilingual glossary for common public-health indicator concepts.

Definitions are educational explanations, not replacements for each source's
official metadata. Indicator-specific values and definitions must be loaded
from the source record where available.
"""
GLOSSARY = {
 "malaria_incidence": {
  "name_en":"Malaria incidence", "name_sw":"Matukio mapya ya malaria",
  "simple_en":"How many new malaria cases were recorded in a population during a stated period. The rate is often shown per 1,000 people at risk.",
  "simple_sw":"Idadi ya wagonjwa wapya wa malaria waliorekodiwa katika kundi la watu kwa kipindi maalumu. Kiwango kinaweza kuonyeshwa kwa kila watu 1,000 walio katika hatari.",
  "example_en":"If 50 new cases occur among 1,000 people at risk during one year, the rate is 50 per 1,000 for that period.",
  "example_sw":"Ikiwa wagonjwa wapya 50 wanatokea kati ya watu 1,000 walio katika hatari ndani ya mwaka mmoja, kiwango ni 50 kwa kila watu 1,000 katika kipindi hicho.",
  "why_en":"It helps describe the frequency of new reported malaria cases. It does not by itself explain why cases changed.",
  "why_sw":"Husaidia kueleza mara ngapi visa vipya vya malaria viliripotiwa. Kiashiria hiki pekee hakielezi kwa nini visa vilibadilika.",
  "limit_en":"Check the case definition, reporting completeness, population denominator, period and whether the source measures confirmed or estimated cases.",
  "limit_sw":"Kagua ufafanuzi wa kisa, ukamilifu wa taarifa, idadi ya watu iliyotumika, kipindi na kama chanzo kinapima visa vilivyothibitishwa au vilivyokadiriwa."
 },
 "maternal_mortality_ratio": {
  "name_en":"Maternal mortality ratio", "name_sw":"Uwiano wa vifo vya wajawazito na kina mama",
  "simple_en":"The number of maternal deaths related to pregnancy or childbirth per 100,000 live births in a stated period.",
  "simple_sw":"Idadi ya vifo vya kina mama vinavyohusiana na ujauzito au kujifungua kwa kila vizazi hai 100,000 katika kipindi maalumu.",
  "example_en":"A ratio of 200 means 200 maternal deaths for every 100,000 live births, according to the source's definition and estimation method.",
  "example_sw":"Uwiano wa 200 unamaanisha vifo 200 vya kina mama kwa kila vizazi hai 100,000, kulingana na ufafanuzi na njia ya makadirio ya chanzo.",
  "why_en":"It is used to understand maternal health and the wider conditions around pregnancy and childbirth.",
  "why_sw":"Hutumika kuelewa afya ya mama na hali pana zinazohusiana na ujauzito na kujifungua.",
  "limit_en":"It is often an estimate, not a simple count. Check uncertainty intervals, method, reference years and live-birth denominator.",
  "limit_sw":"Mara nyingi ni makadirio, si hesabu rahisi. Kagua viwango vya kutokuwa na uhakika, mbinu, miaka husika na idadi ya vizazi hai."
 },
 "under_five_mortality": {
  "name_en":"Under-five mortality rate", "name_sw":"Kiwango cha vifo vya watoto chini ya miaka mitano",
  "simple_en":"The probability of a child dying before reaching their fifth birthday, usually expressed per 1,000 live births.",
  "simple_sw":"Uwezekano wa mtoto kufariki kabla ya kufikisha miaka mitano, kwa kawaida huonyeshwa kwa kila vizazi hai 1,000.",
  "example_en":"A rate of 40 per 1,000 means an estimated 40 children would die before age five for every 1,000 live births under the stated measure.",
  "example_sw":"Kiwango cha 40 kwa kila 1,000 kinamaanisha makadirio ya watoto 40 kufariki kabla ya miaka mitano kwa kila vizazi hai 1,000 kwa kipimo hicho.",
  "why_en":"It is a broad measure of child survival and living conditions.",
  "why_sw":"Ni kipimo kipana cha uhai wa watoto na hali ya maisha.",
  "limit_en":"Check whether the source reports a probability, an estimate or observed deaths, and note the reference period.",
  "limit_sw":"Kagua kama chanzo kinatoa uwezekano, makadirio au vifo vilivyorekodiwa, na zingatia kipindi husika."
 },
 "immunisation_coverage": {
  "name_en":"Immunisation coverage", "name_sw":"Wigo wa chanjo",
  "simple_en":"The percentage of the target group that received a specified vaccine dose during the period or by the recommended age.",
  "simple_sw":"Asilimia ya kundi lengwa lililopokea dozi maalumu ya chanjo ndani ya kipindi au kufikia umri uliopendekezwa.",
  "example_en":"Coverage of 85% means 85 out of every 100 people in the defined target group were recorded as having received that dose.",
  "example_sw":"Wigo wa 85% unamaanisha watu 85 kati ya kila 100 katika kundi lengwa lililofafanuliwa walirekodiwa kupokea dozi hiyo.",
  "why_en":"It helps monitor whether vaccination services are reaching the intended population.",
  "why_sw":"Husaidia kufuatilia kama huduma za chanjo zinafikia watu waliolengwa.",
  "limit_en":"Check numerator, denominator, age group, dose, reporting completeness and whether the value is administrative or survey-based.",
  "limit_sw":"Kagua idadi iliyopata chanjo, jumla ya kundi lengwa, umri, dozi, ukamilifu wa taarifa na kama thamani imetokana na taarifa za huduma au utafiti."
 },
 "basic_drinking_water": {
  "name_en":"At least basic drinking-water service", "name_sw":"Huduma ya maji ya kunywa angalau ya kiwango cha msingi",
  "simple_en":"A household drinking-water service that meets the source's basic-service definition. Under the JMP ladder, this generally means an improved source with a collection time of no more than 30 minutes for a round trip.",
  "simple_sw":"Huduma ya maji ya kunywa ya kaya inayokidhi ufafanuzi wa kiwango cha msingi wa chanzo. Katika kipimo cha JMP, kwa kawaida ni chanzo kilichoboreshwa ambacho kuchota maji na kurudi hakuzidi dakika 30.",
  "example_en":"If 72% is reported, about 72 out of every 100 people are estimated to use a service meeting that definition.",
  "example_sw":"Ikiwa 72% imeripotiwa, takribani watu 72 kati ya kila 100 wanakadiriwa kutumia huduma inayokidhi ufafanuzi huo.",
  "why_en":"Water access is important for health, dignity and daily life.",
  "why_sw":"Upatikanaji wa maji ni muhimu kwa afya, utu na maisha ya kila siku.",
  "limit_en":"Basic service does not automatically mean water is free from contamination, available continuously or available inside the home. Check the exact JMP definition and estimate year.",
  "limit_sw":"Huduma ya msingi haimaanishi moja kwa moja kuwa maji hayana uchafuzi, yanapatikana muda wote au yapo ndani ya nyumba. Kagua ufafanuzi halisi wa JMP na mwaka wa makadirio."
 },
 "sanitation_service": {
  "name_en":"Sanitation service level", "name_sw":"Kiwango cha huduma ya usafi wa mazingira",
  "simple_en":"Describes the type of sanitation facility people use and, depending on the category, how safely waste is managed.",
  "simple_sw":"Hueleza aina ya choo au huduma ya usafi inayotumiwa na watu na, kulingana na kundi, namna taka zinavyosimamiwa kwa usalama.",
  "example_en":"A safely managed service has stricter requirements than simply having access to an improved toilet.",
  "example_sw":"Huduma inayosimamiwa kwa usalama ina masharti makali zaidi kuliko kuwa na choo kilichoboreshwa pekee.",
  "why_en":"Safe sanitation helps reduce exposure to faecal contamination and supports public health.",
  "why_sw":"Usafi wa mazingira unaosimamiwa kwa usalama husaidia kupunguza kukutana na uchafu wa kinyesi na kulinda afya ya umma.",
  "limit_en":"Check the service ladder category, shared-facility rules and whether waste is safely treated or disposed.",
  "limit_sw":"Kagua kundi la huduma, masharti ya vyoo vya pamoja na kama taka zinatibiwa au kutupwa kwa usalama."
 },
 "poverty_headcount": {
  "name_en":"Poverty headcount ratio", "name_sw":"Asilimia ya watu walio chini ya mstari wa umaskini",
  "simple_en":"The percentage of people living in households whose measured resources are below a defined poverty line.",
  "simple_sw":"Asilimia ya watu wanaoishi katika kaya ambazo rasilimali zilizopimwa ziko chini ya mstari maalumu wa umaskini.",
  "example_en":"A headcount of 25% means 25 out of every 100 people are classified below the stated poverty line.",
  "example_sw":"Kiwango cha 25% kinamaanisha watu 25 kati ya kila 100 wameainishwa kuwa chini ya mstari huo wa umaskini.",
  "why_en":"Poverty can shape access to food, housing, education and health services.",
  "why_sw":"Umaskini unaweza kuathiri upatikanaji wa chakula, makazi, elimu na huduma za afya.",
  "limit_en":"Check the poverty line, price basis, survey year, household measure and whether the statistic is national or subnational.",
  "limit_sw":"Kagua mstari wa umaskini, msingi wa bei, mwaka wa utafiti, kipimo cha kaya na kama takwimu ni za kitaifa au za eneo dogo."
 },
 "health_worker_density": {
  "name_en":"Health-worker density", "name_sw":"Msongamano wa watumishi wa afya",
  "simple_en":"The number of specified health workers relative to a population, often expressed per 10,000 people.",
  "simple_sw":"Idadi ya watumishi wa afya wa kada zilizotajwa ikilinganishwa na idadi ya watu, mara nyingi kwa kila watu 10,000.",
  "example_en":"A density of 10 per 10,000 means there are 10 workers in the defined categories for every 10,000 people.",
  "example_sw":"Msongamano wa 10 kwa kila watu 10,000 unamaanisha kuna watumishi 10 wa kada zilizofafanuliwa kwa kila watu 10,000.",
  "why_en":"It gives a broad picture of the health workforce available relative to population size.",
  "why_sw":"Hutoa picha ya jumla ya watumishi wa afya waliopo ikilinganishwa na ukubwa wa idadi ya watu.",
  "limit_en":"Check which professions are counted, whether counts are headcount or full-time equivalent, and the population denominator.",
  "limit_sw":"Kagua kada zilizohesabiwa, kama ni idadi ya watu au sawa na wafanyakazi wa muda wote, na jumla ya watu iliyotumika."
 }
}

def get_explanation(key: str, lang: str = "en") -> dict:
    item = GLOSSARY.get(key)
    if not item:
        return {}
    suffix = "sw" if lang == "sw" else "en"
    return {
        "name": item.get(f"name_{suffix}", item["name_en"]),
        "simple_explanation": item.get(f"simple_{suffix}", item["simple_en"]),
        "example": item.get(f"example_{suffix}", item["example_en"]),
        "why_it_matters": item.get(f"why_{suffix}", item["why_en"]),
        "limitations": item.get(f"limit_{suffix}", item["limit_en"]),
        "official_definition_required": True,
    }

def render_glossary(lang: str = "en") -> None:
    import streamlit as st
    sw = lang == "sw"
    tr = lambda en, kis: kis if sw else en
    st.subheader(tr("Understand a health indicator", "Elewa kiashiria cha afya"))
    labels = {v["name_sw" if sw else "name_en"]: k for k,v in GLOSSARY.items()}
    key = labels[st.selectbox(tr("Choose an indicator concept", "Chagua aina ya kiashiria"), list(labels), key="plain_glossary")]
    item = get_explanation(key, lang)
    st.markdown(f"### {item['name']}")
    for heading, field in [
        (tr("In simple words","Kwa lugha rahisi"),"simple_explanation"),
        (tr("Example","Mfano"),"example"),
        (tr("Why it matters","Kwa nini ni muhimu"),"why_it_matters"),
        (tr("What this number cannot tell us","Kile ambacho namba hii haiwezi kutuambia"),"limitations"),
    ]:
        st.markdown(f"**{heading}**")
        st.write(item[field])
    st.caption(tr("Educational glossary only. Always check the selected dataset's official definition, unit, year and geographic coverage.", "Kamusi hii ni kwa elimu tu. Hakiki ufafanuzi rasmi wa seti ya data, kipimo, mwaka na eneo."))

def render_data_navigator(lang: str = "en") -> None:
    import streamlit as st
    from un_data_commons import render_un_data_intelligence
    from research_laboratory import render_research_laboratory
    sw = lang == "sw"
    tr = lambda en, kis: kis if sw else en
    st.header(tr("UN Data Navigator", "Mwongozo wa Takwimu za UN"))
    st.caption(tr("Find trusted data, understand what it means, and see what it cannot tell you.", "Tafuta takwimu zenye chanzo, elewa maana yake na mipaka yake."))
    st.info(tr("This navigator explains data in everyday language. It does not replace official definitions or create missing statistics.", "Mwongozo huu unaeleza takwimu kwa lugha rahisi. Hauchukui nafasi ya ufafanuzi rasmi wala kutengeneza takwimu ambazo hazipo."))
    tabs = st.tabs([tr("Explore UN data","Chunguza data za UN"),tr("Understand indicators","Elewa viashiria"),tr("Available sources","Vyanzo vinavyopatikana")])
    with tabs[0]:
        st.markdown(tr("### Start with the question, not the database name", "### Anza na swali, si jina la hifadhidata"))
        st.write(tr("Choose a topic in the UN Data Intelligence tab to search and retrieve a statistical observation. The current connector is read-only.", "Chagua mada kwenye kichupo cha UN Data Intelligence ili kutafuta na kupata takwimu. Kiunganishi cha sasa kinasoma data pekee."))
        st.link_button(tr("Open UN Data Intelligence","Fungua Taarifa za Takwimu za UN"), "https://data.un.org/undatacommons/docs/getting-started")
        st.markdown("#### " + tr("UN SDG statistics","Takwimu za SDG za UN"))
        render_sdg_explorer(lang)
    with tabs[1]:
        render_glossary(lang)
    with tabs[2]:
        from un_data_sources import SOURCE_REGISTRY
        for source in SOURCE_REGISTRY:
            with st.expander(source["name"] + " — " + source["status"]):
                st.write(source["domain"])
                st.write(source["coverage_note"])
                st.warning(source["caveat"])
                st.markdown(f"[{tr('Open official source','Fungua chanzo rasmi')}]({source['url']})")
                st.caption(tr("Registry status indicates integration state, not endorsement or validation.", "Hali ya usajili inaonyesha kiwango cha muunganisho, si uthibitisho au idhini."))
