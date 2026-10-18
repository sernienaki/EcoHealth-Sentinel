import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium import FeatureGroup
from streamlit_folium import st_folium
import plotly.graph_objects as go
import json
from datetime import datetime

# ==============================================================================
# 1. HIGH-END UI & TIMES NEW ROMAN FONT INJECTION
# ==============================================================================
st.set_page_config(page_title="EcoHealth Sentinel: Tanzania & EAC", layout="wide", initial_sidebar_state="expanded")

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
    button[data-baseweb="tab"] { font-size: 14px !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. DATA STRUCTURES: TANZANIA (REGIONS) vs EAC (NATIONAL MOCKUP)
# ==============================================================================
# Detailed Tanzanian Regional Data
TANZANIA_REGIONS = {
    "Dar es Salaam": {"lat": -6.7924, "lon": 39.2083, "mal": 15, "cholera": 450, "mmr": 85, "fic": 82, "oop": 32, "htn": 31.2, "poverty": 12, "schools": 450, "markets": 120},
    "Dodoma": {"lat": -6.1630, "lon": 35.7516, "mal": 45, "cholera": 80, "mmr": 115, "fic": 75, "oop": 35, "htn": 22.0, "poverty": 28, "schools": 320, "markets": 85},
    "Mwanza": {"lat": -2.5164, "lon": 32.9175, "mal": 210, "cholera": 210, "mmr": 130, "fic": 70, "oop": 30, "htn": 20.5, "poverty": 25, "schools": 280, "markets": 60},
    "Arusha": {"lat": -3.3869, "lon": 36.6830, "mal": 35, "cholera": 40, "mmr": 95, "fic": 85, "oop": 28, "htn": 26.0, "poverty": 18, "schools": 310, "markets": 75},
    "Kilimanjaro": {"lat": -3.3488, "lon": 37.3407, "mal": 20, "cholera": 30, "mmr": 70, "fic": 88, "oop": 25, "htn": 24.0, "poverty": 15, "schools": 290, "markets": 65},
    "Tanga": {"lat": -5.0689, "lon": 39.0989, "mal": 60, "cholera": 150, "mmr": 105, "fic": 78, "oop": 31, "htn": 23.0, "poverty": 22, "schools": 260, "markets": 55},
    "Morogoro": {"lat": -6.8235, "lon": 37.6612, "mal": 80, "cholera": 120, "mmr": 110, "fic": 76, "oop": 33, "htn": 21.0, "poverty": 26, "schools": 300, "markets": 70},
    "Kigoma": {"lat": -4.8761, "lon": 29.6267, "mal": 100, "cholera": 200, "mmr": 125, "fic": 72, "oop": 36, "htn": 19.0, "poverty": 32, "schools": 250, "markets": 55},
    "Shinyanga": {"lat": -3.6667, "lon": 33.4167, "mal": 110, "cholera": 130, "mmr": 118, "fic": 73, "oop": 31, "htn": 20.0, "poverty": 27, "schools": 260, "markets": 58},
    "Mara": {"lat": -1.5000, "lon": 34.0000, "mal": 140, "cholera": 190, "mmr": 138, "fic": 67, "oop": 35, "htn": 20.0, "poverty": 28, "schools": 220, "markets": 52},
    "Geita": {"lat": -2.8667, "lon": 32.2167, "mal": 130, "cholera": 180, "mmr": 135, "fic": 68, "oop": 36, "htn": 18.0, "poverty": 30, "schools": 210, "markets": 48},
    "Zanzibar": {"lat": -6.1659, "lon": 39.2022, "mal": 8, "cholera": 300, "mmr": 78, "fic": 85, "oop": 25, "htn": 28.0, "poverty": 14, "schools": 180, "markets": 40}
}

# General EAC National Mockup Data (Keys fixed to match dropdown exactly)
EAC_NATIONAL = {
    "Kenya 🇰🇪": {"lat": -0.0236, "lon": 37.9062, "mal": 45, "cholera": 90, "mmr": 342, "fic": 80, "oop": 25, "htn": 27.0, "poverty": 22, "schools": 12000, "markets": 3500},
    "Uganda 🇺🇬": {"lat": 1.3733, "lon": 32.2903, "mal": 120, "cholera": 110, "mmr": 336, "fic": 76, "oop": 32, "htn": 26.0, "poverty": 31, "schools": 9500, "markets": 2800},
    "Rwanda 🇷🇼": {"lat": -1.9403, "lon": 29.8739, "mal": 35, "cholera": 20, "mmr": 248, "fic": 92, "oop": 12, "htn": 21.0, "poverty": 16, "schools": 4200, "markets": 1100},
    "Burundi 🇧🇮": {"lat": -3.3731, "lon": 29.9189, "mal": 250, "cholera": 180, "mmr": 548, "fic": 71, "oop": 18, "htn": 18.0, "poverty": 45, "schools": 3800, "markets": 950},
    "South Sudan 🇸": {"lat": 6.8770, "lon": 31.3070, "mal": 310, "cholera": 220, "mmr": 1150, "fic": 55, "oop": 45, "htn": 16.0, "poverty": 62, "schools": 2100, "markets": 600}
}

# ==============================================================================
# 3. AUTHENTICATION & SUBSCRIPTION SYSTEM
# ==============================================================================
if 'user' not in st.session_state: st.session_state.user = None
if 'auth_step' not in st.session_state: st.session_state.auth_step = 'login'

st.sidebar.title("🌍 EcoHealth Sentinel")

if st.session_state.user is None:
    if st.session_state.auth_step == 'login':
        st.sidebar.header(" Sign In")
        email = st.sidebar.text_input("Email Address", placeholder="name@hospital.go.tz")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Log In", use_container_width=True) and email and password:
            st.session_state.user = {"email": email, "name": email.split('@')[0].capitalize(), "role": "Verified Professional", "org": "Ministry of Health"}
            st.rerun()
        st.sidebar.markdown("---")
        st.sidebar.write("New to EcoHealth Sentinel?")
        if st.sidebar.button("Create Account", use_container_width=True):
            st.session_state.auth_step = 'signup'; st.rerun()
            
    elif st.session_state.auth_step == 'signup':
        st.sidebar.header("📝 Create Account")
        name = st.sidebar.text_input("Full Name")
        email = st.sidebar.text_input("Email Address")
        org = st.sidebar.selectbox("Organization", ["Ministry of Health", "NGO", "Research", "CHW"])
        password = st.sidebar.text_input("Create Password", type="password")
        confirm = st.sidebar.text_input("Confirm Password", type="password")
        
        if st.sidebar.button("Sign Up & Send Verification", use_container_width=True):
            if password == confirm and len(password) > 5:
                st.session_state.pending_user = {"name": name, "email": email, "org": org}
                st.session_state.auth_step = 'verify'; st.rerun()
            else: st.sidebar.error("Passwords do not match or too short.")
        if st.sidebar.button("Back to Login", use_container_width=True):
            st.session_state.auth_step = 'login'; st.rerun()
            
    elif st.session_state.auth_step == 'verify':
        st.sidebar.header("📧 Verify Email")
        st.sidebar.success(f"Code sent to {st.session_state.pending_user['email']}")
        code = st.sidebar.text_input("Enter 6-digit code", placeholder="123456")
        if st.sidebar.button("Verify Account", use_container_width=True):
            if code == "123456": 
                st.session_state.user = st.session_state.pending_user
                st.session_state.user["role"] = "Verified Professional"
                st.session_state.auth_step = 'login'; st.rerun()
            else: st.sidebar.error("Invalid code. Try 123456.")
else:
    st.sidebar.header(f"👤 Welcome, {st.session_state.user['name']}!")
    st.sidebar.success(f"✅ {st.session_state.user['role']}")
    st.sidebar.info(f" {st.session_state.user.get('org', 'Tanzania MoH')}")
    st.sidebar.markdown("---")
    st.sidebar.subheader("🌟 Premium Subscription")
    st.sidebar.write("Unlock Advanced AI, Bulk DHIS2 Exports, and Offline CHW Mode.")
    st.sidebar.link_button("💳 Subscribe for $1/month", "https://buymeacoffee.com/ecohealth", use_container_width=True)
    st.sidebar.markdown("---")
    st.sidebar.subheader("♻️ Green AI Impact")
    st.sidebar.metric("CO2 Saved", "0.045 kg/prediction", delta="-99% vs LLMs")
    if st.sidebar.button(" Log Out", use_container_width=True): 
        st.session_state.user = None; st.session_state.auth_step = 'login'; st.rerun()

# ==============================================================================
# 4. APP SETTINGS & NAVIGATION
# ==============================================================================
st.sidebar.header("⚙️ Settings")
country = st.sidebar.selectbox("Select Country", ["Tanzania 🇹", "Kenya 🇰🇪", "Uganda 🇺🇬", "Rwanda 🇷🇼", "Burundi 🇧🇮", "South Sudan 🇸"])

# Dynamic Region Selector
if country == "Tanzania 🇹":
    region = st.sidebar.selectbox("Select Region (Tanzania)", list(TANZANIA_REGIONS.keys()))
    data = TANZANIA_REGIONS[region]
    policy_text = "HSSP V, Vision 2050 & PDPA 2022"
else:
    region = "National Overview"
    data = EAC_NATIONAL[country]
    policy_text = "National Health Strategy & EAC Protocol"

st.title(f"EcoHealth Sentinel: {region}, {country}")
st.info(f"🛡️ Policy: {policy_text} | ITU ML Pipeline Compliant")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Executive Dashboard", "🌍 Socio-Ecological & Services", "🤖 AI, FHIR & USSD", "📄 Policy Brief"
])

# --- TAB 1: EXECUTIVE DASHBOARD ---
with tab1:
    st.header("Comprehensive Public Health Surveillance")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Malaria (per 1k)", data['mal'], delta="+5%")
    c2.metric("Cholera Cases", data['cholera'], delta="+15%", delta_color="inverse")
    c3.metric("Maternal Mortality", data['mmr'], delta="-4")
    c4.metric("Vaccination (FIC %)", f"{data['fic']}%", delta="+2%")
    c5.metric("Out-of-Pocket (%)", f"{data['oop']}%", delta="-1%")

    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("SDG Progress: Maternal Mortality")
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number", value=data['mmr'],
            title={'text': "MMR per 100k (Target <70)", 'font': {'size': 16}},
            number={'font': {'size': 24}},
            gauge={'axis': {'range': [0, 200], 'tickwidth': 1, 'tickcolor': "darkblue"},
                   'bar': {'color': "darkred"}, 'bgcolor': "white", 'borderwidth': 2, 'bordercolor': "gray",
                   'steps': [{'range': [0, 70], 'color': 'lightgreen'}, {'range': [70, 120], 'color': 'yellow'}, {'range': [120, 200], 'color': 'red'}]}
        ))
        fig_g.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20), font=dict(family='Times New Roman'))
        st.plotly_chart(fig_g, use_container_width=True)

    with col2:
        st.subheader("Immunization Coverage")
        fig_b = go.Figure(data=[
            go.Bar(name='Penta 1', x=['Coverage'], y=[90], marker_color='lightblue'),
            go.Bar(name='Penta 3', x=['Coverage'], y=[85], marker_color='blue'),
            go.Bar(name='Fully Immunized', x=['Coverage'], y=[data['fic']], marker_color='darkblue')
        ])
        fig_b.update_layout(title="Vaccine Retention (%)", yaxis=dict(range=[0, 100], title="Percentage"), plot_bgcolor='white', font=dict(family='Times New Roman'))
        st.plotly_chart(fig_b, use_container_width=True)

# --- TAB 2: SOCIO-ECOLOGICAL & SERVICES MAP ---
with tab2:
    st.header("🌍 Socio-Ecological Determinants & Social Services")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Social & Economic Indicators")
        st.metric("Poverty Index", f"{data['poverty']}%")
        st.metric("Hypertension Prevalence", f"{data['htn']}%")
        st.metric("Schools", data['schools'])
        st.metric("Markets", data['markets'])
        st.markdown("---")
        st.subheader("How to Read This Map")
        st.info("""
        **Red Pins:** Health Facilities
        **Blue Circles:** WASH Points
        **Green Squares:** Schools
        **Orange Triangles:** Markets
        *Toggle layers using the icon on the top right.*
        """)

    with col2:
        st.subheader(f"Interactive Service Map: {region}")
        zoom_level = 9 if country == "Tanzania 🇹" else 6
        m = folium.Map(location=[data['lat'], data['lon']], zoom_start=zoom_level, tiles="OpenStreetMap")
        
        hosp_group = FeatureGroup(name='🏥 Health Facilities')
        for i in range(5):
            lat = data['lat'] + np.random.uniform(-0.1, 0.1)
            lon = data['lon'] + np.random.uniform(-0.1, 0.1)
            folium.Marker(location=[lat, lon], popup=f"<b>Health Facility {i+1}</b>", icon=folium.Icon(color='red', icon='plus', prefix='fa')).add_to(hosp_group)
        hosp_group.add_to(m)
        
        wash_group = FeatureGroup(name='💧 WASH Points')
        for i in range(8):
            lat = data['lat'] + np.random.uniform(-0.15, 0.15)
            lon = data['lon'] + np.random.uniform(-0.15, 0.15)
            folium.CircleMarker(location=[lat, lon], radius=8, color='blue', fill=True, fill_opacity=0.7, popup=f"<b>Water Point {i+1}</b>").add_to(wash_group)
        wash_group.add_to(m)
        
        school_group = FeatureGroup(name='🏫 Schools')
        for i in range(6):
            lat = data['lat'] + np.random.uniform(-0.12, 0.12)
            lon = data['lon'] + np.random.uniform(-0.12, 0.12)
            folium.RegularPolygonMarker(location=[lat, lon], number_of_sides=4, radius=10, color='green', fill=True, fill_opacity=0.7, popup=f"<b>School {i+1}</b>").add_to(school_group)
        school_group.add_to(m)
        
        market_group = FeatureGroup(name='🛒 Markets')
        for i in range(4):
            lat = data['lat'] + np.random.uniform(-0.08, 0.08)
            lon = data['lon'] + np.random.uniform(-0.08, 0.08)
            folium.RegularPolygonMarker(location=[lat, lon], number_of_sides=3, radius=10, color='orange', fill=True, fill_opacity=0.7, popup=f"<b>Market {i+1}</b>").add_to(market_group)
        market_group.add_to(m)
        
        folium.LayerControl(collapsed=False).add_to(m)
        st_folium(m, width=800, height=600)

# --- TAB 3: AI, FHIR & USSD ---
with tab3:
    st.header("🤖 AI Agent & Interoperability")
    if "messages" not in st.session_state: st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]): st.markdown(message["content"])
            
    prompt = st.chat_input(f"Ask about health risks in {region}")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        if "malaria" in prompt.lower() or "cholera" in prompt.lower():
            response = f" **Alert for {region}:** High risk detected. Malaria: {data['mal']}/1k, Cholera: {data['cholera']} cases. Recommend immediate WASH intervention and LLIN distribution."
        elif "vaccine" in prompt.lower() or "fic" in prompt.lower():
            response = f"💉 **Immunization in {region}:** FIC is at {data['fic']}%. Below target. Recommend mop-up campaigns in rural wards."
        else:
            response = f"📊 **Summary for {region}:** MMR is {data['mmr']}. Hypertension is {data['htn']}%. Poverty index is {data['poverty']}%."
        
        fhir_payload = {"resourceType": "Bundle", "type": "transaction", "entry": [{"resource": {"resourceType": "CarePlan", "status": "active", "intent": "plan", "title": f"Intervention for {region}", "subject": {"reference": f"Location/TZ-{region}"}}}]}
        ussd_payload = f"TO: CHW Network\nMSG: 'TAHADHARI: Risk high in {region}. Report to Zahanati.' - MoH"
        
        full_response = f"{response}\n\n**GoTHoMIS FHIR Payload:**\n```json\n{json.dumps(fhir_payload, indent=2)}\n```\n\n**USSD Alert Payload:**\n```text\n{ussd_payload}\n```"
        
        with st.chat_message("assistant"): st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- TAB 4: POLICY BRIEF ---
with tab4:
    st.header("📄 Policy Brief Generator")
    brief = f"""
POLICY BRIEF: EcoHealth Sentinel
Region: {region}, {country}
Date: {datetime.now().strftime('%B %d, %Y')}

1. EXECUTIVE SUMMARY
{region} faces a double burden of disease. Malaria incidence is {data['mal']} per 1,000, and Cholera cases are at {data['cholera']}. Maternal Mortality is {data['mmr']} per 100,000. Immediate action is required.

2. KEY FINDINGS
- Malaria: {data['mal']} per 1,000 population.
- Cholera: {data['cholera']} suspected cases.
- Vaccination (FIC): {data['fic']}% (Target >80%).
- Poverty Index: {data['poverty']}%.

3. RECOMMENDATIONS
1. Deploy OCV and WASH interventions for Cholera.
2. Distribute LLINs and RDTs for Malaria.
3. Scale up ANC and SBA services to reduce MMR.

4. MONITORING
- Reduce Cholera cases by 20% in 30 days.
- Increase FIC to >80% in 6 months.

References: {policy_text}, WHO Guidelines.
"""
    st.text_area("Preview", brief, height=400)
    st.download_button("📥 Download Brief", brief, file_name=f"Brief_{region}_{country}.txt")
