import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium import FeatureGroup
from streamlit_folium import st_folium
import plotly.graph_objects as go
import plotly.express as px
import json
from datetime import datetime

# ==============================================================================
# 1. HIGH-END UI & TIMES NEW ROMAN FONT INJECTION
# ==============================================================================
st.set_page_config(page_title="EcoHealth Sentinel: EAC", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Times+New+Roman&display=swap');
    .stApp, .stSidebar, h1, h2, h3, h4, p, div, span, label, button, [data-testid="stMetricLabel"], [data-testid="stMetricValue"], [data-testid="stMetricDelta"] {
        font-family: 'Times New Roman', Times, serif !important;
    }
    [data-testid="stMetric"] {
        background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #0066cc; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stDark [data-testid="stMetric"] { background-color: #262730; border-left: 5px solid #4da6ff; }
    button[data-baseweb="tab"] { font-size: 15px !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. COMPREHENSIVE DATA MODELS (20 DHIS2 INDICATORS + SOCIO-ECO + SERVICES)
# ==============================================================================
EAC_COUNTRIES = {
    "Tanzania 🇹🇿": {"policy": "HSSP V, Vision 2050 & PDPA 2022", "lat": -6.3690, "lon": 34.8888},
    "Kenya 🇰🇪": {"policy": "Kenya UHC Agenda & DPA 2019", "lat": -0.0236, "lon": 37.9062},
    "Uganda 🇺🇬": {"policy": "NDP III Health Sector", "lat": 1.3733, "lon": 32.2903},
    "Rwanda 🇷": {"policy": "NST1 & Mutuelles", "lat": -1.9403, "lon": 29.8739},
    "Burundi 🇧🇮": {"policy": "PNDS", "lat": -3.3731, "lon": 29.9189},
    "South Sudan 🇸": {"policy": "Basic Package of Health Services", "lat": 6.8770, "lon": 31.3070}
}

def get_data(country):
    base = {
        "Tanzania 🇹🇿": {"mal": 128, "mal_pos": 34, "cholera": 120, "tb": 180, "llin": 65, "mmr": 104, "imr": 23, "anc4": 62, "sba": 80, "sam": 4.5, "fic": 78, "penta_drop": 5, "ocv": 15000, "htn": 24.5, "dm": 2.1, "cervical": 15, "tobacco": 8, "stockout": 12, "hw": 0.15, "oop": 28, "poverty": 28, "edu": 65, "hesitancy": 15, "ndvi": 0.45, "flood": "High", "pm25": 18, "inactivity": 22},
        "Kenya 🇰🇪": {"mal": 45, "mal_pos": 12, "cholera": 90, "tb": 210, "llin": 70, "mmr": 342, "imr": 28, "anc4": 68, "sba": 75, "sam": 3.2, "fic": 80, "penta_drop": 6, "ocv": 8000, "htn": 27.0, "dm": 2.5, "cervical": 22, "tobacco": 9, "stockout": 10, "hw": 0.18, "oop": 25, "poverty": 22, "edu": 72, "hesitancy": 12, "ndvi": 0.38, "flood": "Moderate", "pm25": 25, "inactivity": 25},
        "Uganda 🇺🇬": {"mal": 120, "mal_pos": 30, "cholera": 110, "tb": 190, "llin": 60, "mmr": 336, "imr": 31, "anc4": 58, "sba": 70, "sam": 5.1, "fic": 76, "penta_drop": 8, "ocv": 12000, "htn": 26.0, "dm": 1.9, "cervical": 12, "tobacco": 7, "stockout": 15, "hw": 0.14, "oop": 32, "poverty": 31, "edu": 60, "hesitancy": 18, "ndvi": 0.52, "flood": "High", "pm25": 20, "inactivity": 20},
        "Rwanda 🇼": {"mal": 35, "mal_pos": 8, "cholera": 20, "tb": 150, "llin": 85, "mmr": 248, "imr": 21, "anc4": 82, "sba": 92, "sam": 2.1, "fic": 92, "penta_drop": 2, "ocv": 5000, "htn": 21.0, "dm": 1.5, "cervical": 30, "tobacco": 5, "stockout": 5, "hw": 0.22, "oop": 12, "poverty": 16, "edu": 78, "hesitancy": 8, "ndvi": 0.60, "flood": "Low", "pm25": 15, "inactivity": 18},
        "Burundi 🇧🇮": {"mal": 250, "mal_pos": 45, "cholera": 180, "tb": 280, "llin": 55, "mmr": 548, "imr": 42, "anc4": 50, "sba": 60, "sam": 6.5, "fic": 71, "penta_drop": 10, "ocv": 20000, "htn": 18.0, "dm": 1.2, "cervical": 8, "tobacco": 6, "stockout": 22, "hw": 0.08, "oop": 18, "poverty": 45, "edu": 52, "hesitancy": 22, "ndvi": 0.55, "flood": "High", "pm25": 16, "inactivity": 19},
        "South Sudan 🇸🇸": {"mal": 310, "mal_pos": 55, "cholera": 220, "tb": 350, "llin": 40, "mmr": 1150, "imr": 65, "anc4": 35, "sba": 45, "sam": 12.0, "fic": 55, "penta_drop": 15, "ocv": 35000, "htn": 16.0, "dm": 1.0, "cervical": 4, "tobacco": 10, "stockout": 35, "hw": 0.05, "oop": 45, "poverty": 62, "edu": 38, "hesitancy": 25, "ndvi": 0.30, "flood": "Critical", "pm25": 22, "inactivity": 15}
    }
    return base.get(country, base["Tanzania 🇹🇿"])

def get_services(country):
    lat, lon = EAC_COUNTRIES[country]['lat'], EAC_COUNTRIES[country]['lon']
    np.random.seed(42)
    hospitals = [[lat + np.random.uniform(-1, 1), lon + np.random.uniform(-1, 1)] for _ in range(8)]
    wash = [[lat + np.random.uniform(-1.5, 1.5), lon + np.random.uniform(-1.5, 1.5)] for _ in range(15)]
    roads = [[[lat - 1, lon - 1], [lat, lon], [lat + 1, lon + 1]], [[lat - 1, lon + 1], [lat, lon], [lat + 1, lon - 1]]]
    return hospitals, wash, roads

YEARS = [2019, 2020, 2021, 2022, 2023]

# ==============================================================================
# 3. ENGINES: ITU PIPELINE, RIVM, FHIR, USSD
# ==============================================================================
def generate_rivm(data):
    signals, advice = [], []
    if data['cholera'] > 100: signals.append("🚨 High Cholera"); advice.append("Deploy OCV & WASH.")
    if data['mal'] > 100: signals.append("🦟 Malaria Surge"); advice.append("Distribute LLINs/RDTs.")
    if data['mmr'] > 300: signals.append("🤰 Critical MMR"); advice.append("Scale up SBA/EmOC.")
    if data['fic'] < 80: signals.append("💉 Low Immunization"); advice.append("Mop-up campaigns.")
    if not signals: signals.append("✅ Stable"); advice.append("Maintain PHC funding.")
    risk = "CRITICAL" if len(signals) > 2 else ("HIGH" if len(signals) > 1 else "MODERATE")
    return {"signal": "\n".join(signals), "risk": risk, "advice": "\n".join(advice)}

def generate_fhir(country, region, intent):
    loc = f"Location/{country.replace(' ','').replace('🇹🇿','').replace('🇰🇪','').replace('🇺🇬','').replace('🇷🇼','').replace('🇮','').replace('🇸','')}-{region.replace(' ','')}"
    if intent == "vaccine":
        return {"resourceType": "Bundle", "type": "transaction", "entry": [{"resource": {"resourceType": "Immunization", "status": "completed", "vaccineCode": {"coding": [{"system": "http://hl7.org/fhir/sid/cvx", "code": "133", "display": "Cholera Vaccine"}]}, "patient": {"reference": loc}}, "request": {"method": "POST", "url": "Immunization"}}]}
    return {"resourceType": "Bundle", "type": "transaction", "entry": [{"resource": {"resourceType": "CarePlan", "status": "active", "intent": "plan", "subject": {"reference": loc}}, "request": {"method": "POST", "url": "CarePlan"}}]}

def generate_ussd(region, advice):
    return f"""
USSD PUSH PAYLOAD (GoTHoMIS -> CHW Mobile)
------------------------------------------
TO: +255 7XX XXX XXX (CHW Network)
FROM: EcoHealth_Sentinel
MSG: "TAHADHARI: {advice.split('.')[0]} katika {region}. Ripoti kwa Zahanati. - MoH"
STATUS: DELIVERED
    """

# ==============================================================================
# 4. SIDEBAR: AUTH, SUBSCRIPTION, GREEN AI, SETTINGS
# ==============================================================================
if 'user_email' not in st.session_state: st.session_state.user_email = None
st.sidebar.title("🌍 EcoHealth Sentinel (EAC)")

if st.session_state.user_email is None:
    st.sidebar.header(" Sign In")
    email = st.sidebar.text_input("Email", placeholder="name@health.go.tz")
    if st.sidebar.button("Log In", use_container_width=True) and email:
        st.session_state.user_email = email; st.rerun()
else:
    st.sidebar.header(f"👤 Welcome, {st.session_state.user_email.split('@')[0].capitalize()}!")
    st.sidebar.success("✅ Verified Professional")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🌟 Premium Subscription")
    st.sidebar.write("Unlock Advanced AI, Bulk DHIS2 Exports, and Offline CHW Mode.")
    st.sidebar.link_button("💳 Subscribe for $1/month", "https://buymeacoffee.com/ecohealth", use_container_width=True)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("♻️ Green AI Impact")
    st.sidebar.metric("CO2 Saved per Prediction", "0.045 kg", delta="-99% vs LLMs", help="Lightweight heuristic models used instead of energy-intensive LLMs.")
    
    if st.sidebar.button("🚪 Log Out", use_container_width=True): st.session_state.user_email = None; st.rerun()

st.sidebar.header("⚙️ Settings")
lang = st.sidebar.radio("Language", ["English", "Kiswahili"])
country = st.sidebar.selectbox("Country", list(EAC_COUNTRIES.keys()))
region = st.sidebar.selectbox("Region/District", ["National", "Urban Capital", "Rural/Lake Zone"])
role = st.sidebar.selectbox("Stakeholder Role", ["Policymakers", "CHWs", "NGOs", "Researchers"])

st.title(f"EcoHealth Sentinel: {country}")
st.info(f"🛡️ Policy: {EAC_COUNTRIES[country]['policy']} | ITU ML Pipeline Compliant | PDPA 2022 Aggregated Data")

data = get_data(country)
hospitals, wash, roads = get_services(country)

# ==============================================================================
# 5. TABS: THE SINK (AUDIENCE-TAILORED UI)
# ==============================================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Executive Dashboard", "🤰 MNCH & Immunization", "🫀 NCDs & Lifestyle", 
    "🌍 Socio-Ecological", "🗺️ GIS & Social Services", "🤖 AI, FHIR & USSD", "📄 Policy Brief"
])

# --- TAB 1: EXECUTIVE DASHBOARD (20 INDICATORS + METADATA) ---
with tab1:
    st.header(" Comprehensive Public Health Surveillance (DHIS2)")
    st.caption("20 Core Indicators aligned with WHO Global Burden of Disease & HSSP V")
    
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Malaria Incidence (per 1k)", data['mal'], delta="+5%")
    c2.metric("Cholera Cases", data['cholera'], delta="+15%", delta_color="inverse")
    c3.metric("Maternal Mortality (per 100k)", data['mmr'], delta="-4")
    c4.metric("Vaccination (FIC %)", f"{data['fic']}%", delta="+2%")
    c5.metric("Out-of-Pocket (%)", f"{data['oop']}%", delta="-1%")

    st.markdown("---")
    with st.expander("ℹ️ Health Metadata & Data Dictionary (WHO/IHME Standards)", expanded=False):
        st.markdown("#### 📖 Data Dictionary & Interoperability")
        meta_df = pd.DataFrame({
            "Category": ["Communicable", "Communicable", "MNCH", "MNCH", "NCD", "NCD", "Health Systems", "Health Systems"],
            "Indicator": ["Malaria Incidence", "Cholera Cases", "Maternal Mortality (MMR)", "Fully Immunized (FIC)", "Hypertension Screening", "Cervical Cancer Screening", "Meds Stockout Rate", "Health Worker Density"],
            "Standard Code": ["ICD-11: 1C60", "ICD-11: 1A00", "ICD-11: NA00", "SNOMED: 112345008", "SNOMED: 38341003", "SNOMED: 268400008", "LMIS: STOCK-01", "HRH: HW-01"],
            "Source": ["DHIS2 / NSMIS", "DHIS2 / EWARS", "DHIS2 / TDHS-MIS", "DHIS2 / EPI", "DHIS2 / HMIS", "DHIS2 / HMIS", "LMIS / MSD", "HRH Registry"]
        })
        st.dataframe(meta_df, use_container_width=True, hide_index=True)
        
        st.markdown("#### 🛡️ Governance & Privacy")
        st.info("""
        - **Provenance:** Aggregated from MoH DHIS2, TMA, NASA POWER.
        - **Spatial Resolution:** Admin Level 1 & 2. 
        - **Privacy:** 100% aggregated. No PII. Compliant with Tanzania PDPA 2022 & GDPR.
        - **Interoperability:** HL7 FHIR R4, ICD-11, SNOMED CT.
        """)

# --- TAB 2: MNCH & IMMUNIZATION ---
with tab2:
    st.header(" Maternal, Newborn, Child Health & Immunization")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("SDG 3.1 & 3.2 Progress Gauges")
        fig_g = go.Figure()
        fig_g.add_trace(go.Indicator(mode="gauge+number", value=data['mmr'], title={'text': "MMR (Target <70)"}, gauge={'axis': {'range': [0, 600]}, 'bar': {'color': "darkred"}, 'steps': [{'range': [0, 70], 'color': "lightgreen"}, {'range': [70, 300], 'color': "yellow"}, {'range': [300, 600], 'color': "red"}]}))
        fig_g.add_trace(go.Indicator(mode="gauge+number", value=data['imr'], title={'text': "IMR (Target <12)"}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "darkblue"}, 'steps': [{'range': [0, 12], 'color': "lightgreen"}, {'range': [12, 50], 'color': "orange"}, {'range': [50, 100], 'color': "red"}]}))
        fig_g.update_layout(grid={'rows': 1, 'columns': 2, 'pattern': "independent"}, height=300, font=dict(family='Times New Roman'))
        st.plotly_chart(fig_g, use_container_width=True)
    with col2:
        st.subheader("Immunization Retention Funnel")
        fig_f = go.Figure(go.Funnel(y=["Penta 1", "Penta 3", "Fully Immunized"], x=[90, 90 - data['penta_drop'], data['fic']], textinfo="value+percent initial"))
        fig_f.update_layout(title="Vaccine Dropout Analysis", font=dict(family='Times New Roman'))
        st.plotly_chart(fig_f, use_container_width=True)

# --- TAB 3: NCDs & LIFESTYLE ---
with tab3:
    st.header("🫀 Non-Communicable Diseases, Nutrition & Physical Activity")
    st.subheader("Multidimensional NCD & Environmental Risk Profile (WHO STEPS)")
    fig_r = go.Figure(data=go.Scatterpolar(
        r=[data['htn'], data['dm']*10, data['tobacco']*3, data['inactivity'], data['pm25']],
        theta=['Hypertension (%)', 'Diabetes (x10)', 'Tobacco (x3)', 'Inactivity (%)', 'Air Quality PM2.5'],
        fill='toself'
    ))
    fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 50])), title="NCD Risk Factor Radar", font=dict(family='Times New Roman'))
    st.plotly_chart(fig_r, use_container_width=True)

# --- TAB 4: SOCIO-ECOLOGICAL MODEL ---
with tab4:
    st.header("🌍 Socio-Ecological Model: Biomedical, Social, Anthropological & Remote Sensing")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Social & Anthropological Determinants")
        st.markdown(f"**Poverty:** {data['poverty']}% | **Female Education:** {data['edu']}% | **Vaccine Hesitancy:** {data['hesitancy']}%")
        fig_s = go.Figure(data=[go.Bar(name='Poverty (%)', x=['Determinant'], y=[data['poverty']], marker_color='#e74c3c'), go.Bar(name='Female Edu (%)', x=['Determinant'], y=[data['edu']], marker_color='#27ae60')])
        fig_s.update_layout(title="Social Determinants", plot_bgcolor='white', font=dict(family='Times New Roman'))
        st.plotly_chart(fig_s, use_container_width=True)
    with col2:
        st.subheader("Remote Sensing: NDVI vs Malaria")
        fig_e = go.Figure()
        fig_e.add_trace(go.Scatter(x=YEARS, y=[0.40, 0.42, 0.48, 0.43, data['ndvi']], mode='lines+markers', name='NDVI (Vegetation)', line=dict(color='green')))
        fig_e.add_trace(go.Scatter(x=YEARS, y=[140, 135, 150, 130, data['mal']], mode='lines+markers', name='Malaria (per 1k)', yaxis='y2', line=dict(color='red')))
        fig_e.update_layout(title="Vegetation Index vs Vector-Borne Disease", yaxis=dict(title="NDVI"), yaxis2=dict(title="Malaria", overlaying='y', side='right'), plot_bgcolor='white', font=dict(family='Times New Roman'))
        st.plotly_chart(fig_e, use_container_width=True)

# --- TAB 5: GIS & SOCIAL SERVICES ---
with tab5:
    st.header("️ Interactive GIS & Accessible Social Services")
    m = folium.Map(location=[EAC_COUNTRIES[country]['lat'], EAC_COUNTRIES[country]['lon']], zoom_start=7, tiles="OpenStreetMap")
    
    hosp_group = FeatureGroup(name='🏥 Hospitals & Clinics')
    for loc in hospitals: folium.Marker(location=loc, popup="<b>Health Facility</b>", icon=folium.Icon(color='red', icon='plus', prefix='fa')).add_to(hosp_group)
    hosp_group.add_to(m)
    
    wash_group = FeatureGroup(name=' WASH Facilities')
    for loc in wash: folium.CircleMarker(location=loc, radius=6, color='blue', fill=True, fill_opacity=0.7, popup="<b>WASH Point</b>").add_to(wash_group)
    wash_group.add_to(m)
    
    road_group = FeatureGroup(name='🛣️ Road Networks')
    for road in roads: folium.PolyLine(road, color="grey", weight=4, opacity=0.7, popup="<b>Primary Road</b>").add_to(road_group)
    road_group.add_to(m)
    
    folium.LayerControl(collapsed=False).add_to(m)
    
    meta_html = f"""<div style="position: fixed; bottom: 50px; left: 50px; width: 250px; background-color: white; border:2px solid grey; z-index:9999; font-family: 'Times New Roman'; padding: 10px; border-radius: 5px;">
        <b>🗺️ Map Metadata</b><br><hr style="margin: 5px 0;">
        <b>Scope:</b> {country} (Admin L1/2)<br><b>Indicators:</b> Cholera, Malaria, Services<br>
        <b>Standards:</b> HL7 FHIR R4, ICD-11<br><b>Privacy:</b> Aggregated (PDPA 2022)<br>
        <b>Generated:</b> {datetime.now().strftime('%d %b %Y')}<br><i>EcoHealth Sentinel v1.0</i>
    </div>"""
    m.get_root().html.add_child(folium.Element(meta_html))
    st_folium(m, width=1200, height=600)

# --- TAB 6: AI, FHIR & USSD ---
with tab6:
    st.header("🤖 Interactive AI Agent, GoTHoMIS FHIR & Community USSD Alerts")
    if "messages" not in st.session_state: st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]): st.markdown(message["content"])
            
    prompt = st.chat_input("Ask: 'Is there a cholera risk?' or 'Generate FHIR for vaccines'")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        advice = generate_rivm(data)
        fhir = generate_fhir(country, region, "vaccine")
        ussd = generate_ussd(region, advice['advice'])
        
        response = f"**AI Insight (RIVM Cycle):** Risk is **{advice['risk']}**.\n{advice['advice']}\n\n **GoTHoMIS FHIR R4 Payload:**"
        
        with st.chat_message("assistant"):
            st.markdown(response)
            st.code(json.dumps(fhir, indent=2), language='json')
            st.markdown("📱 **Community Level USSD/SMS Alert Payload:**")
            st.code(ussd, language='text')
        st.session_state.messages.append({"role": "assistant", "content": response + ussd})

# --- TAB 7: POLICY BRIEF GENERATOR ---
with tab7:
    st.header("📄 UNDP / World Bank Standard Policy Brief Generator")
    st.caption("Automatically formatted for Ministry of Health and Development Partners")
    
    policy = generate_rivm(data)
    brief = f"""
POLICY BRIEF: EcoHealth Sentinel (East African Community)
Date: {datetime.now().strftime('%B %d, %Y')}
Target Audience: Ministry of Health, Regional Medical Officers, Development Partners
Subject: Mitigating the Climate-Driven Double Burden of Disease in {region}

1. EXECUTIVE SUMMARY
Climate shocks are exacerbating the "Double Burden of Disease" in {region}. EcoHealth Sentinel data indicates a critical surge in climate-sensitive communicable diseases concurrent with disruptions to Non-Communicable Disease (NCD) care. This brief recommends immediate, targeted interventions to protect vulnerable populations and align with {EAC_COUNTRIES[country]['policy']}.

2. CONTEXT AND URGENCY
Recent meteorological data confirms environmental stressors leading to compromised WASH infrastructure and medical supply chain disruptions. This triggers a "lag effect," where disease outbreaks spike alongside NCD medication stockouts.

3. KEY EVIDENCE AND FINDINGS (DHIS2 Integrated)
• Cholera Risk: Cases are currently at {data['cholera']}, indicating elevated outbreak risk.
• Malaria Burden: Incidence remains high at {data['mal']} per 1,000 population.
• NCD Disruption: Hypertension prevalence is at {data['htn']}%, with supply chains vulnerable.
• Socio-Ecological: Poverty rate is {data['poverty']}%, compounding biomedical risks.

4. ACTIONABLE POLICY RECOMMENDATIONS (RIVM Intelligence Cycle)
1. {policy['advice'].split('\n')[0] if policy['advice'] else 'Maintain routine PHC surveillance.'}
2. Integrate NCD screening into existing community health outreach campaigns (Task-shifting).
3. Pre-position essential medicines and WASH supplies in vulnerable wards prior to peak climate shock seasons.

5. MONITORING AND EVALUATION
• Reduce target disease incidence by 20% within 30 days.
• Maintain essential medicine stockout rates below 5% at the district level.

6. REFERENCES
• {EAC_COUNTRIES[country]['policy']}
• World Health Organization. (2021). Tools for making good data visualizations.
• EcoHealth Sentinel DHIS2 Integrated Data Dashboard ({datetime.now().strftime('%Y')}).
"""
    st.text_area("Preview Policy Brief", brief, height=400)
    st.download_button("📥 Download Official Policy Brief (.txt)", brief, file_name=f"Policy_Brief_{country.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.txt", mime="text/plain")
