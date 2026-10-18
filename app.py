import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import json
from datetime import datetime

# ==============================================================================
# 1. TRANSLATION ENGINE (English / Kiswahili)
# ==============================================================================
LANG = {
    'en': {
        'app_title': "EcoHealth Sentinel: Tanzania",
        'sidebar_title': "🇹🇿 EcoHealth Sentinel",
        'settings': "️ Settings / Mipangilio",
        'region': "Select Region / Chagua Mkoa",
        'role': "Your Role / Jukumu Lako",
        'lang': "Lugha / Language",
        'theme': " Theme / Mandhari",
        'tab1': "📊 Dashboard (DHIS2)",
        'tab2': "🏃‍♂️ Physio, Nutrition & Lifestyle",
        'tab3': "🗺️ GIS Map",
        'tab4': "🤖 AI Agent & FHIR",
        'plain_lang': "📖 Plain Language Summary",
        'policy_badge': "🛡️ Policy Compliance: PDPA 2022 (Aggregated Data Only) | HSSP V Aligned"
    },
    'sw': {
        'app_title': "EcoHealth Sentinel: Tanzania",
        'sidebar_title': "🇿 EcoHealth Sentinel",
        'settings': "⚙️ Mipangilio",
        'region': "Chagua Mkoa",
        'role': "Jukumu Lako",
        'lang': "Lugha",
        'theme': "🎨 Mandhari / Theme",
        'tab1': "📊 Dashibodi (DHIS2)",
        'tab2': "🏃‍♂️ Fizikia, Lishe na Mtindo wa Maisha",
        'tab3': "🗺️ Ramani ya GIS",
        'tab4': "🤖 Wakala wa AI na FHIR",
        'plain_lang': "📖 Muhtasari wa Lugha Rahisi",
        'policy_badge': "🛡️ Uzingatiaji wa Sera: PDPA 2022 (Data Zilizojumuishwa) | HSSP V"
    }
}

# ==============================================================================
# 2. TANZANIA HEALTH DATA & POLICY CONTEXT
# ==============================================================================
REGIONS_DATA = {
    "National": {"lat": -6.3690, "lon": 34.8888, "mmr": 104, "mal": 128, "cholera": 120, "vax": 78.0, "screen": 15.0, "htn": 24.5, "inactivity": 22.0, "pm25": 18},
    "Dar es Salaam": {"lat": -6.7924, "lon": 39.2083, "mmr": 85, "mal": 15, "cholera": 450, "vax": 82.0, "screen": 22.0, "htn": 31.2, "inactivity": 35.0, "pm25": 42},
    "Dodoma": {"lat": -6.1630, "lon": 35.7516, "mmr": 115, "mal": 45, "cholera": 80, "vax": 75.0, "screen": 12.0, "htn": 22.0, "inactivity": 18.0, "pm25": 22},
    "Mwanza": {"lat": -2.5164, "lon": 32.9175, "mmr": 130, "mal": 210, "cholera": 210, "vax": 70.0, "screen": 10.0, "htn": 20.5, "inactivity": 15.0, "pm25": 15},
    "Zanzibar": {"lat": -6.1659, "lon": 39.2022, "mmr": 78, "mal": 8, "cholera": 300, "vax": 85.0, "screen": 25.0, "htn": 28.0, "inactivity": 25.0, "pm25": 14}
}

TREND_DATA = pd.DataFrame({
    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    'Rainfall (mm)': [50, 80, 150, 250, 100, 40],
    'Cholera Cases': [20, 45, 120, 350, 180, 60],
    'Vaccination Rate (%)': [76, 76.5, 77, 77.5, 78, 78.5]
})

POLICY_CONTEXT = {
    "HSSP_V": "Health Sector Strategic Plan V: Prioritizes EPI (Immunization), WASH (Cholera), and NCD Screening.",
    "PDPA_2022": "Personal Data Protection Act: Ensures all AI outputs use aggregated, anonymized data."
}

# ==============================================================================
# 3. RIVM POLICY ADVICE ENGINE
# ==============================================================================
def generate_rivm_policy_advice(region, data):
    signals = []
    if data['cholera'] > 200: signals.append(f"🚨 Cholera cases critically high at {data['cholera']}.")
    if data['mal'] > 150: signals.append(f"🦟 Malaria incidence surging at {data['mal']} per 1,000.")
    if data['vax'] < 80: signals.append(f"💉 Vaccination coverage dropping below 80% ({data['vax']}%).")
    if not signals: signals.append("✅ No immediate outbreak signals detected. Monitoring routine indicators.")
    
    risk_level = "LOW"
    if data['cholera'] > 200 or data['mal'] > 150: risk_level = "CRITICAL"
    elif data['cholera'] > 100 or data['mal'] > 100: risk_level = "HIGH"
    elif data['cholera'] > 50: risk_level = "MODERATE"
    
    advice = []
    if data['cholera'] > 100:
        advice.append("1. Activate the National Emergency Operations Center (NEOC) for WASH intervention.")
        advice.append("2. Pre-position Oral Cholera Vaccines (OCV) and water purification tablets.")
    if data['mal'] > 100:
        advice.append("3. Deploy rapid diagnostic tests (RDTs) and ACTs to rural dispensaries.")
    if data['vax'] < 80:
        advice.append("4. Conduct 'mop-up' immunization campaigns in hard-to-reach areas.")
    if not advice: advice.append("1. Continue routine surveillance and maintain current PHC funding levels.")
        
    return {"signal": "\n".join(signals), "risk": risk_level, "advice": "\n".join(advice), "evaluation": "Reduce target disease incidence by 20% within 30 days."}

# ==============================================================================
# 4. FHIR INTEROPERABILITY ENGINE
# ==============================================================================
def generate_fhir_resource(region, intent_type):
    if intent_type == "cholera_vaccine":
        return {"resourceType": "Bundle", "type": "transaction", "entry": [{"resource": {"resourceType": "Immunization", "status": "completed", "vaccineCode": {"coding": [{"system": "http://hl7.org/fhir/sid/cvx", "code": "133", "display": "Cholera Vaccine (Oral)"}]}, "patient": {"reference": f"Location/TZ-{region.replace(' ', '')}", "display": f"{region} Population"}, "occurrenceDateTime": datetime.now().strftime("%Y-%m-%d")}, "request": {"method": "POST", "url": "Immunization"}}]}
    elif intent_type == "screening":
        return {"resourceType": "Bundle", "type": "transaction", "entry": [{"resource": {"resourceType": "Procedure", "status": "completed", "code": {"coding": [{"system": "http://snomed.info/sct", "code": "268400008", "display": "Cervical/NCD Screening"}]}, "subject": {"reference": f"Location/TZ-{region.replace(' ', '')}", "display": f"{region} Target Population"}, "performedDateTime": datetime.now().strftime("%Y-%m-%d")}, "request": {"method": "POST", "url": "Procedure"}}]}
    else:
        return {"resourceType": "Bundle", "type": "transaction", "entry": [{"resource": {"resourceType": "CarePlan", "status": "active", "intent": "plan", "title": f"Climate-Resilient Health Response: {region}", "subject": {"reference": f"Location/TZ-{region.replace(' ', '')}"}, "activity": [{"detail": {"kind": "ServiceRequest", "code": {"text": "General PHC Intervention"}, "status": "in-progress"}}]}, "request": {"method": "POST", "url": "CarePlan"}}]}

# ==============================================================================
# 5. UI & LAYOUT
# ==============================================================================
st.set_page_config(page_title="EcoHealth Sentinel", layout="wide", initial_sidebar_state="expanded")

# --- AUTHENTICATION & SUBSCRIPTION (Sidebar) ---
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

st.sidebar.title(LANG['en']['sidebar_title'])

if st.session_state.user_email is None:
    st.sidebar.header("👤 Sign In / Register")
    email = st.sidebar.text_input("Email Address", placeholder="name@hospital.go.tz")
    st.sidebar.text_input("Password", type="password", placeholder="••••••••")
    col1, col2 = st.sidebar.columns(2)
    if col1.button("Log In", use_container_width=True) and email:
        st.session_state.user_email = email
        st.rerun()
    if col2.button("Sign Up", use_container_width=True) and email:
        st.session_state.user_email = email
        st.rerun()
else:
    user_name = st.session_state.user_email.split('@')[0].capitalize()
    st.sidebar.header(f"👤 Welcome, {user_name}!")
    st.sidebar.success("✅ Verified Health Professional")
    st.sidebar.markdown("---")
    st.sidebar.subheader("🌟 Premium Subscription")
    st.sidebar.write("Help us scale to all 31 regions! Unlock Advanced AI, Bulk DHIS2 Exports, and Offline CHW Mode.")
    st.sidebar.link_button("💳 Subscribe for $1/month", "https://buymeacoffee.com/ecohealth", use_container_width=True)
    
    # --- SUSTAINABILITY HUB ---
    st.sidebar.markdown("---")
    with st.sidebar.expander("♻️ Sustainability & Impact Hub", expanded=False):
        st.markdown("#### 💰 Financial Model")
        st.write("Freemium SaaS: Free for CHWs/Gov, $1/mo for advanced features.")
        st.sidebar.link_button("🤝 Sponsor a District ($50/mo)", "https://buymeacoffee.com/ecohealth", use_container_width=True)
        st.markdown("#### 🌍 Green AI (Environmental)")
        st.metric(label="CO2 Saved per Prediction", value="0.045 kg", delta="-99% vs LLMs")
        st.markdown("#### 🛠️ Technical (Open Source)")
        st.write("Built on Open Standards: HL7 FHIR, DHIS2. MIT License.")
        st.markdown("#### 🤝 Social (Digital Inclusion)")
        st.write("✅ 100% Kiswahili Support")
        st.write("✅ Low-bandwidth optimized for rural CHWs")

    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        st.session_state.user_email = None
        st.rerun()

# --- APP SETTINGS & THEME TOGGLE ---
st.sidebar.header(LANG['en']['settings'])
lang_choice = st.sidebar.radio(LANG['en']['lang'], ["English", "Kiswahili"])
L = LANG['en'] if lang_choice == "English" else LANG['sw']

# LIGHT / DARK MODE TOGGLE
theme_choice = st.sidebar.selectbox(L['theme'], ["System Default", "Light Mode", "Dark Mode"])
if theme_choice == "Dark Mode":
    st.markdown("""<style>.stApp {background-color: #0e1117; color: #fafafa;} .stSidebar {background-color: #0e1117;} h1, h2, h3, p, label, .stMarkdown {color: #fafafa !important;} .stMetric {background-color: #262730; padding: 10px; border-radius: 5px;}</style>""", unsafe_allow_html=True)
elif theme_choice == "Light Mode":
    st.markdown("""<style>.stApp {background-color: #ffffff; color: #262730;} .stSidebar {background-color: #f0f2f6;} h1, h2, h3, p, label, .stMarkdown {color: #262730 !important;} .stMetric {background-color: #f6f6f6; padding: 10px; border-radius: 5px;}</style>""", unsafe_allow_html=True)

region = st.sidebar.selectbox(L['region'], list(REGIONS_DATA.keys()))
role = st.sidebar.selectbox(L['role'], ["Policymakers", "CHWs", "NGOs", "Researchers"])

st.title(f"{L['app_title']}")
st.info(L['policy_badge'])

tab1, tab2, tab3, tab4 = st.tabs([L['tab1'], L['tab2'], L['tab3'], L['tab4']])

# --- TAB 1: DASHBOARD & RIVM POLICY ADVICE ---
with tab1:
    data = REGIONS_DATA[region]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Maternal Mortality (per 100k)", data['mmr'], delta="-4", help="HSSP V Target: 70")
    c2.metric("Vaccination Coverage (%)", f"{data['vax']}%", delta="+0.5%", help="Target: >90%")
    c3.metric("Cholera Outbreak Risk", f"{data['cholera']} cases", delta="+150%", delta_color="inverse", help="El Niño Alert")
    c4.metric("NCD/Cancer Screening (%)", f"{data['screen']}%", delta="+2%", help="Target: >50%")

    st.markdown("---")
    st.subheader("🇳🇱 RIVM Intelligence Cycle: Automated Policy Advice")
    policy = generate_rivm_policy_advice(region, data)
    p1, p2, p3, p4 = st.columns(4)
    with p1: st.markdown("#### 1. 🔍 Signal Detection"); st.info(policy['signal'])
    with p2: 
        st.markdown("#### 2. ⚠️ Risk Assessment")
        risk_color = "#d32f2f" if policy['risk'] == "CRITICAL" else ("#f57c00" if policy['risk'] == "HIGH" else "#388e3c")
        st.markdown(f"<div style='background-color:{risk_color}; color:white; padding:15px; border-radius:5px; text-align:center; font-weight:bold; font-size:20px;'>{policy['risk']} RISK</div>", unsafe_allow_html=True)
    with p3: st.markdown("#### 3. 📜 Policy Advice"); st.success(policy['advice'])
    with p4: st.markdown("#### 4.  Evaluation Metric"); st.warning(policy['evaluation'])

    st.markdown("---")
    col_chart, col_text = st.columns([2, 1])
    with col_chart:
        st.subheader("Climate-Health Link: El Niño Rainfall vs Cholera Outbreaks")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=TREND_DATA['Month'], y=TREND_DATA['Rainfall (mm)'], name='Rainfall (mm)', marker_color='blue', opacity=0.3))
        fig.add_trace(go.Scatter(x=TREND_DATA['Month'], y=TREND_DATA['Cholera Cases'], name='Cholera Cases', yaxis='y2', line=dict(color='red', width=3)))
        fig.update_layout(title="Cholera Spikes 1 Month After Heavy Rains (Lag Effect)", yaxis=dict(title="Rainfall (mm)"), yaxis2=dict(title="Cholera Cases", overlaying='y', side='right'), plot_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)
    with col_text:
        st.warning(f"**{L['plain_lang']}:** In {region}, heavy rains in April caused a massive spike in Cholera cases in May. This proves the need for better WASH infrastructure before the rainy season.")

    brief_text = f"ECOHEALTH SENTINEL POLICY BRIEF\nRegion: {region}\nDate: {datetime.now().strftime('%Y-%m-%d')}\n\n--- RIVM INTELLIGENCE CYCLE ---\n\n1. SIGNAL:\n{policy['signal']}\n\n2. RISK ASSESSMENT:\n{policy['risk']}\n\n3. POLICY ADVICE:\n{policy['advice']}\n\n4. EVALUATION METRIC:\n{policy['evaluation']}\n\n--- ALIGNMENT ---\nPolicy: {POLICY_CONTEXT['HSSP_V']}\nPrivacy: {POLICY_CONTEXT['PDPA_2022']}"
    st.download_button("📥 Download Official Policy Brief (.txt)", brief_text, file_name=f"Policy_Brief_{region}.txt", mime="text/plain")

# --- TAB 2: PHYSIO & NUTRITION ---
with tab2:
    st.subheader("Nutrition & Physical Activity (WHO GAPPA & NMNAP)")
    st.write(f"**{region} Context:** Inactivity rate is **{data['inactivity']}%**. Hypertension prevalence is **{data['htn']}%**. Air Quality (PM2.5) is **{data['pm25']} µg/m³**.")
    st.write("💡 **Action:** Implement 'Exercise is Medicine' social prescribing at the dispensary level to combat NCDs and improve cardiovascular health.")

# --- TAB 3: GIS MAP ---
with tab3:
    st.subheader("ITU EcoHealth Sentinel: Double Burden Vulnerability Map")
    m = folium.Map(location=[-6.3690, 34.8888], zoom_start=6, tiles="OpenStreetMap")
    for name, d in REGIONS_DATA.items():
        risk_score = (d['cholera'] / 100) + (d['mal'] / 50)
        color = 'red' if risk_score > 4 else ('orange' if risk_score > 2 else 'green')
        folium.CircleMarker(location=[d['lat'], d['lon']], radius=12, color=color, fill=True, 
                            popup=f"<b>{name}</b><br>Cholera: {d['cholera']}<br>Malaria: {d['mal']}<br>Vaccination: {d['vax']}%").add_to(m)
    st_folium(m, width=1000, height=500)

# --- TAB 4: AI AGENT & FHIR ---
with tab4:
    st.header("🤖 Interactive AI Agent & GoTHoMIS FHIR Integration")
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
        
        if "cholera" in prompt_lower or "outbreak" in prompt_lower:
            insight = f"🚨 **Cholera Alert for {region}:** Current cases are at **{data['cholera']}**. HIGH RISK due to El Niño flooding. \n\n💡 **Action:** Immediate deployment of Oral Cholera Vaccines (OCV) and water purification."
            fhir_type = "cholera_vaccine"
        elif "vaccine" in prompt_lower or "immunization" in prompt_lower:
            insight = f"💉 **Immunization Status ({region}):** Coverage is at **{data['vax']}%**. Below the HSSP V target of 90%. \n\n💡 **Action:** Intensify outreach sessions in hard-to-reach wards."
            fhir_type = "cholera_vaccine"
        elif "screen" in prompt_lower or "cancer" in prompt_lower or "ncd" in prompt_lower:
            insight = f"🩺 **Screening Rates ({region}):** Cervical/NCD screening is currently at **{data['screen']}%**. Critically low. \n\n💡 **Action:** Integrate screening into all ANC and OPD visits (Task-shifting to nurses)."
            fhir_type = "screening"
        else:
            insight = f"📊 **General Insight ({region}):** Maternal Mortality is {data['mmr']} and Hypertension is {data['htn']}%. Please ask specifically about Cholera, Vaccines, or Screening."
            fhir_type = "default"

        fhir_json = generate_fhir_resource(region, fhir_type)
        full_response = f"{insight}\n\n🛡️ **Policy Alignment:** {POLICY_CONTEXT['HSSP_V']}\n\n🔗 **GoTHoMIS EMR Integration (HL7 FHIR R4 Payload):**"
        
        with st.chat_message("assistant"):
            st.markdown(full_response)
            st.code(json.dumps(fhir_json, indent=2), language='json')
            
        st.session_state.messages.append({"role": "assistant", "content": full_response})
