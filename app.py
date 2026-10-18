import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import json
from datetime import datetime

# ==============================================================================
# 1. TANZANIA HEALTH DATA (Updated with Cholera, Vaccines, Screening)
# ==============================================================================
REGIONS_DATA = {
    "National": {"lat": -6.3690, "lon": 34.8888, "mmr": 104, "mal": 128, "cholera": 120, "vaccination": 78.0, "screening": 15.0, "htn": 24.5},
    "Dar es Salaam": {"lat": -6.7924, "lon": 39.2083, "mmr": 85, "mal": 15, "cholera": 450, "vaccination": 82.0, "screening": 22.0, "htn": 31.2}, # High cholera risk
    "Dodoma": {"lat": -6.1630, "lon": 35.7516, "mmr": 115, "mal": 45, "cholera": 80, "vaccination": 75.0, "screening": 12.0, "htn": 22.0},
    "Mwanza": {"lat": -2.5164, "lon": 32.9175, "mmr": 130, "mal": 210, "cholera": 210, "vaccination": 70.0, "screening": 10.0, "htn": 20.5}, # Lake zone risk
    "Zanzibar": {"lat": -6.1659, "lon": 39.2022, "mmr": 78, "mal": 8, "cholera": 300, "vaccination": 85.0, "screening": 25.0, "htn": 28.0} # Coastal risk
}

# Historical Trends (Cholera spikes during El Niño/Rainy seasons)
TREND_DATA = pd.DataFrame({
    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    'Rainfall (mm)': [50, 80, 150, 250, 100, 40], # El Niño peak in April
    'Cholera Cases': [20, 45, 120, 350, 180, 60], # Lag effect after rain
    'Vaccination Rate (%)': [76, 76.5, 77, 77.5, 78, 78.5]
})

# Policy Context
POLICY_CONTEXT = {
    "HSSP_V": "Health Sector Strategic Plan V: Prioritizes EPI (Immunization), WASH (Cholera prevention), and NCD Screening.",
    "PDPA_2022": "Personal Data Protection Act: Ensures all AI outputs use aggregated, anonymized data."
}

# ==============================================================================
# 2. FHIR INTEROPERABILITY ENGINE (Updated for Vaccines & Screening)
# ==============================================================================
def generate_fhir_resource(region, intent_type, language):
    """Generates valid HL7 FHIR R4 resources based on AI intent."""
    
    if intent_type == "cholera_vaccine":
        # FHIR Immunization Resource
        return {
            "resourceType": "Bundle", "type": "transaction",
            "entry": [{"resource": {
                "resourceType": "Immunization", "status": "completed",
                "vaccineCode": {"coding": [{"system": "http://hl7.org/fhir/sid/cvx", "code": "133", "display": "Cholera Vaccine (Oral)"}]},
                "patient": {"reference": f"Location/TZ-{region.replace(' ', '')}", "display": f"{region} Population"},
                "occurrenceDateTime": datetime.now().strftime("%Y-%m-%d"),
                "primarySource": True,
                "note": [{"text": "Emergency OCV campaign due to El Niño flood risk."}]
            }, "request": {"method": "POST", "url": "Immunization"}}]
        }
    elif intent_type == "screening":
        # FHIR Procedure Resource (Cervical/NCD Screening)
        return {
            "resourceType": "Bundle", "type": "transaction",
            "entry": [{"resource": {
                "resourceType": "Procedure", "status": "completed",
                "code": {"coding": [{"system": "http://snomed.info/sct", "code": "268400008", "display": "Cervical Cancer Screening"}]},
                "subject": {"reference": f"Location/TZ-{region.replace(' ', '')}", "display": f"{region} Women (30-49 yrs)"},
                "performedDateTime": datetime.now().strftime("%Y-%m-%d"),
                "note": [{"text": "PHC screening initiative to detect early-stage NCDs/Cancer."}]
            }, "request": {"method": "POST", "url": "Procedure"}}]
        }
    else:
        # Default CarePlan
        return {
            "resourceType": "Bundle", "type": "transaction",
            "entry": [{"resource": {
                "resourceType": "CarePlan", "status": "active", "intent": "plan",
                "title": f"Climate-Resilient Health Response: {region}",
                "subject": {"reference": f"Location/TZ-{region.replace(' ', '')}"},
                "activity": [{"detail": {"kind": "ServiceRequest", "code": {"text": "General PHC Intervention"}, "status": "in-progress"}}]
            }, "request": {"method": "POST", "url": "CarePlan"}}]
        }

# ==============================================================================
# 3. UI & LAYOUT
# ==============================================================================
st.set_page_config(page_title="EcoHealth Sentinel", layout="wide")
st.sidebar.title("🇿 EcoHealth Sentinel")
st.sidebar.header("Settings")
region = st.sidebar.selectbox("Select Region", list(REGIONS_DATA.keys()))
role = st.sidebar.selectbox("Your Role", ["Policymakers", "CHWs", "Researchers"])

st.title(f"National Health Resilience Platform: {region}")
st.info(f"🛡️ Policy Compliance: PDPA 2022 (Aggregated Data) | HSSP V Aligned")

tab1, tab2, tab3 = st.tabs(["📊 Dashboard (DHIS2)", "🗺️ GIS Map", "🤖 AI Agent & FHIR"])

# --- TAB 1: DASHBOARD ---
with tab1:
    data = REGIONS_DATA[region]
    
    # KPI Metrics (Traffic Light System)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Maternal Mortality (per 100k)", data['mmr'], delta="-4", help="Target: 70")
    c2.metric("Vaccination Coverage (%)", f"{data['vaccination']}%", delta="+0.5%", help="Target: >90%")
    c3.metric("Cholera Outbreak Risk", f"{data['cholera']} cases", delta="+150%", delta_color="inverse", help="El Niño Alert")
    c4.metric("NCD/Cancer Screening (%)", f"{data['screening']}%", delta="+2%", help="Target: >50%")

    st.markdown("---")
    
    # Chart: Cholera vs Rainfall (Climate Link)
    col_chart, col_text = st.columns([2, 1])
    with col_chart:
        st.subheader("Climate-Health Link: El Niño Rainfall vs Cholera Outbreaks")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=TREND_DATA['Month'], y=TREND_DATA['Rainfall (mm)'], name='Rainfall (mm)', marker_color='blue', opacity=0.3))
        fig.add_trace(go.Scatter(x=TREND_DATA['Month'], y=TREND_DATA['Cholera Cases'], name='Cholera Cases', yaxis='y2', line=dict(color='red', width=3)))
        fig.update_layout(
            title="Cholera Spikes 1 Month After Heavy Rains (Lag Effect)",
            yaxis=dict(title="Rainfall (mm)"),
            yaxis2=dict(title="Cholera Cases", overlaying='y', side='right'),
            plot_bgcolor='white'
        )
        st.plotly_chart(fig, use_container_width=True)
    with col_text:
        st.warning(f"**Plain Language Summary:** In {region}, heavy rains in April caused a massive spike in Cholera cases in May. This proves the need for better WASH (Water, Sanitation, Hygiene) infrastructure before the rainy season.")

# --- TAB 2: GIS MAP ---
with tab2:
    st.subheader("Tanzania Vulnerability Map (Cholera & Malaria)")
    m = folium.Map(location=[-6.3690, 34.8888], zoom_start=6, tiles="OpenStreetMap")
    for name, d in REGIONS_DATA.items():
        # Color based on Cholera + Malaria risk
        risk_score = (d['cholera'] / 100) + (d['mal'] / 50)
        color = 'red' if risk_score > 4 else ('orange' if risk_score > 2 else 'green')
        folium.CircleMarker(location=[d['lat'], d['lon']], radius=12, color=color, fill=True, 
                            popup=f"<b>{name}</b><br>Cholera: {d['cholera']}<br>Malaria: {d['mal']}<br>Vaccination: {d['vaccination']}%").add_to(m)
    st_folium(m, width=1000, height=500)

# --- TAB 3: AI AGENT & FHIR ---
with tab3:
    st.header(" Interactive AI Agent & GoTHoMIS FHIR Integration")
    st.caption("Ask about Cholera, Vaccines, or Screening. The AI will generate policy-aligned insights and FHIR resources.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    prompt = st.chat_input("Ask: 'Is there a cholera risk?', 'What is the vaccination rate?', or 'How is cancer screening?'")
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        data = REGIONS_DATA[region]
        prompt_lower = prompt.lower()
        
        # AI Logic Routing
        if "cholera" in prompt_lower or "outbreak" in prompt_lower:
            insight = f"️ **Cholera Alert for {region}:** Current cases are at **{data['cholera']}**. This is a **HIGH RISK** zone due to recent El Niño flooding compromising water sources. \n\n💡 **Action:** Immediate deployment of Oral Cholera Vaccines (OCV) and water purification tablets is required."
            fhir_type = "cholera_vaccine"
        elif "vaccine" in prompt_lower or "immunization" in prompt_lower:
            insight = f"💉 **Immunization Status ({region}):** Coverage is at **{data['vaccination']}%**. While improving, we are below the HSSP V target of 90%. \n\n💡 **Action:** Intensify outreach sessions in hard-to-reach wards to close the equity gap."
            fhir_type = "cholera_vaccine" # Using vaccine resource
        elif "screen" in prompt_lower or "cancer" in prompt_lower or "ncd" in prompt_lower:
            insight = f"🩺 **Screening Rates ({region}):** Cervical/NCD screening is currently at **{data['screening']}%**. This is critically low. \n\n💡 **Action:** Integrate screening into all ANC and OPD visits (Task-shifting to nurses)."
            fhir_type = "screening"
        else:
            insight = f"📊 **General Insight ({region}):** Maternal Mortality is {data['mmr']} and Hypertension is {data['htn']}%. Please ask specifically about Cholera, Vaccines, or Screening for detailed FHIR plans."
            fhir_type = "default"

        # Generate FHIR
        fhir_json = generate_fhir_resource(region, fhir_type, "en")
        
        full_response = f"{insight}\n\n🛡️ **Policy Alignment:** {POLICY_CONTEXT['HSSP_V']}\n\n🔗 **GoTHoMIS EMR Integration (HL7 FHIR R4 Payload):**"
        
        with st.chat_message("assistant"):
            st.markdown(full_response)
            st.code(json.dumps(fhir_json, indent=2), language='json')
            
        st.session_state.messages.append({"role": "assistant", "content": full_response})
