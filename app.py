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
# 1. TRANSLATION DICTIONARY (ENGLISH / KISWAHILI)
# ==============================================================================
T = {
    'en': {
        'title': "EcoHealth Sentinel",
        'welcome': "Welcome",
        'verified': "Verified Professional",
        'settings': "⚙️ Settings",
        'country': "Select Country",
        'region': "Select Region (Tanzania)",
        'role': "Your Role / Jukumu Lako",
        'lang': "Language / Lugha",
        'theme': "Theme / Mandhari",
        'tab1': "📊 Executive Dashboard",
        'tab2': "🌍 Socio-Ecological & Services",
        'tab3': "🤖 AI, FHIR & USSD",
        'tab4': "📄 Policy Brief",
        'policy': "Policy: HSSP V, Vision 2050 & PDPA 2022 | ITU ML Pipeline Compliant",
        'surveillance': "Comprehensive Public Health Surveillance",
        'malaria': "Malaria (per 1k)",
        'cholera': "Cholera Cases",
        'mmr': "Maternal Mortality",
        'fic': "Vaccination (FIC %)",
        'oop': "Out-of-Pocket (%)",
        'sdg': "SDG Progress: Maternal Mortality",
        'mmr_target': "MMR per 100k (Target <70)",
        'immunity': "Immunization Coverage",
        'vaccine_retention': "Vaccine Retention (%)",
        'social': "Social & Economic Indicators",
        'poverty': "Poverty Index",
        'hypertension': "Hypertension Prevalence",
        'schools': "Schools",
        'markets': "Markets",
        'map_guide': "How to Read This Map",
        'map_guide_text': "**Red Pins:** Health Facilities\n**Blue Circles:** WASH Points\n**Green Squares:** Schools\n**Orange Triangles:** Markets\n*Toggle layers using the icon on the top right.*",
        'interactive_map': "Interactive Service Map",
        'ai_header': "AI Agent & Interoperability",
        'chat_input': "Ask about health risks",
        'ussd_header': "Africa's Talking USSD Integration Demo",
        'ussd_desc': "Simulated USSD session flow for Community Health Workers via Africa's Talking API",
        'ussd_start': "Start USSD Session Demo",
        'ussd_session': "USSD Session Flow",
        'ussd_payload': "Africa's Talking API Payload",
        'brief_header': "Policy Brief Generator",
        'download': "📥 Download Brief",
        'preview': "Preview",
        'roles': ["Policymaker", "Community Health Worker (CHW)", "Student/Researcher", "NGO Partner"],
        'languages': ["English", "Kiswahili"],
        'themes': ["Light Mode", "Dark Mode"],
        'green_ai': "♻️ Green AI Impact",
        'co2_saved': "CO2 Saved",
        'co2_delta': "-99% vs LLMs",
        'premium': "🌟 Premium Subscription",
        'premium_desc': "Unlock Advanced AI, Bulk DHIS2 Exports, and Offline CHW Mode.",
        'subscribe': "💳 Subscribe for $1/month",
        'logout': "🚪 Log Out",
        'login': "👤 Sign In",
        'email': "Email Address",
        'password': "Password",
        'login_btn': "Log In",
        'new_user': "New to EcoHealth Sentinel?",
        'create_account': "Create Account",
        'signup_header': "📝 Create Account",
        'full_name': "Full Name",
        'organization': "Organization",
        'create_pass': "Create Password",
        'confirm_pass': "Confirm Password",
        'signup_btn': "Sign Up & Send Verification",
        'back_login': "Back to Login",
        'verify_header': "📧 Verify Email",
        'code_sent': "Code sent to",
        'enter_code': "Enter 6-digit code",
        'verify_btn': "Verify Account",
        'invalid_code': "Invalid code. Try 123456.",
        'pass_error': "Passwords do not match or too short.",
        'orgs': ["Ministry of Health", "NGO", "Research Institute", "Community Health Worker", "Other"],
        'chat_placeholder': "Ask about health risks in {region}",
        'alert_malaria': " **Alert for {region}:** High risk detected. Malaria: {mal}/1k, Cholera: {cholera} cases. Recommend immediate WASH intervention and LLIN distribution.",
        'alert_vaccine': "💉 **Immunization in {region}:** FIC is at {fic}%. Below target. Recommend mop-up campaigns in rural wards.",
        'summary': "📊 **Summary for {region}:** MMR is {mmr}. Hypertension is {htn}%. Poverty index is {poverty}%.",
        'fhir_title': "GoTHoMIS FHIR Payload",
        'ussd_title': "USSD Alert Payload (Africa's Talking)",
    },
    'sw': {
        'title': "EcoHealth Sentinel",
        'welcome': "Karibu",
        'verified': "Mtaalamu Aliyethibitishwa",
        'settings': "⚙️ Mipangilio",
        'country': "Chagua Nchi",
        'region': "Chagua Mkoa (Tanzania)",
        'role': "Jukumu Lako / Your Role",
        'lang': "Lugha / Language",
        'theme': "Mandhari / Theme",
        'tab1': "📊 Dashibodi Kuu",
        'tab2': "🌍 Jamii na Huduma",
        'tab3': "🤖 AI, FHIR na USSD",
        'tab4': "📄 Hati ya Sera",
        'policy': "Sera: HSSP V, Vision 2050 na PDPA 2022 | ITU ML Pipeline",
        'surveillance': "Ufuatiliaji wa Afya ya Umma",
        'malaria': "Malaria (kwa 1k)",
        'cholera': "Visa vya Kipindupindu",
        'mmr': "Vifo vya Mama",
        'fic': "Chanjo (FIC %)",
        'oop': "Gharama ya Mfukoni (%)",
        'sdg': "Maendeleo ya SDG: Vifo vya Mama",
        'mmr_target': "MMR kwa 100k (Lengo <70)",
        'immunity': "Ufunikaji wa Chanjo",
        'vaccine_retention': "Udumifu wa Chanjo (%)",
        'social': "Viashiria vya Kijamii na Kiuchumi",
        'poverty': "Kiwango cha Umaskini",
        'hypertension': "Udalili wa Shinikizo la Damu",
        'schools': "Shule",
        'markets': "Masoko",
        'map_guide': "Jinsi ya Kusoma Ramani",
        'map_guide_text': "**Vipini Vyekundu:** Vituo vya Afya\n**Vidudu vya Bluu:** Vyanzo vya Maji\n**Mraba wa Kijani:** Shule\n**Pembetatu ya Chungwa:** Masoko\n*Badilisha tabaka kwa kutumia ikoni juu kulia.*",
        'interactive_map': "Ramani ya Huduma",
        'ai_header': "Wakala wa AI na Uunganishaji",
        'chat_input': "Uliza kuhusu hatari za afya",
        'ussd_header': "Maonyesho ya USSD ya Africa's Talking",
        'ussd_desc': "Mtiririko wa USSD kwa Wahudumu wa Afya wa Jamii kupitia API ya Africa's Talking",
        'ussd_start': "Anza Maonyesho ya USSD",
        'ussd_session': "Mtiririko wa USSD",
        'ussd_payload': "Mzigo wa API ya Africa's Talking",
        'brief_header': "Kizalishaji cha Hati ya Sera",
        'download': "📥 Pakua Hati",
        'preview': "Hakiki",
        'roles': ["Mtunga Sera", "Mhudumu wa Afya wa Jamii (CHW)", "Mwanafunzi/Mtafiti", "Mshirika wa NGO"],
        'languages': ["English", "Kiswahili"],
        'themes': ["Hali ya Mwanga", "Hali ya Giza"],
        'green_ai': "♻️ Athari ya AI ya Kijani",
        'co2_saved': "CO2 Iliyookolewa",
        'co2_delta': "-99% ikilinganishwa na LLM",
        'premium': "🌟 Uanachama wa Premium",
        'premium_desc': "Fungua AI ya Hali ya Juu, Usafirishaji wa DHIS2, na Hali ya Nje ya Mtandao.",
        'subscribe': "💳 Jiandikishe kwa $1/mwezi",
        'logout': "🚪 Toka",
        'login': "👤 Ingia",
        'email': "Barua Pepe",
        'password': "Nenosiri",
        'login_btn': "Ingia",
        'new_user': "Mgeni kwenye EcoHealth Sentinel?",
        'create_account': "Fungua Akaunti",
        'signup_header': "📝 Fungua Akaunti",
        'full_name': "Jina Kamili",
        'organization': "Mashirika",
        'create_pass': "Unda Nenosiri",
        'confirm_pass': "Thibitisha Nenosiri",
        'signup_btn': "Jiandikishe na Tuma Uthibitisho",
        'back_login': "Rudi Kuingia",
        'verify_header': "📧 Thibitisha Barua Pepe",
        'code_sent': "Msimbo umetumwa kwa",
        'enter_code': "Weka msimbo wa tarakimu 6",
        'verify_btn': "Thibitisha Akaunti",
        'invalid_code': "Msimbo si sahihi. Jaribu 123456.",
        'pass_error': "Manenosiri hayalingani au ni mafupi.",
        'orgs': ["Wizara ya Afya", "NGO", "Taasisi ya Utafiti", "Mhudumu wa Afya wa Jamii", "Nyingine"],
        'chat_placeholder': "Uliza kuhusu hatari za afya katika {region}",
        'alert_malaria': "🚨 **Tahadhari kwa {region}:** Hatari kubwa imegunduliwa. Malaria: {mal}/1k, Kipindupindu: {cholera} visa. Tunapendekeza kuingilia kati haraka.",
        'alert_vaccine': "💉 **Chanjo katika {region}:** FIC iko {fic}%. Chini ya lengo. Tunapendekeza kampeni za kufikia maeneo ya vijijini.",
        'summary': "📊 **Muhtasari wa {region}:** MMR ni {mmr}. Shinikizo la damu ni {htn}%. Umaskini ni {poverty}%.",
        'fhir_title': "Mzigo wa GoTHoMIS FHIR",
        'ussd_title': "Mzigo wa USSD (Africa's Talking)",
    }
}

# ==============================================================================
# 2. HIGH-END UI & THEME CSS
# ==============================================================================
st.set_page_config(page_title="EcoHealth Sentinel: Tanzania & EAC", layout="wide", initial_sidebar_state="expanded")

if 'theme' not in st.session_state:
    st.session_state.theme = 'Light Mode'

def get_theme_css(theme):
    if theme == 'Dark Mode':
        return """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Times+New+Roman&display=swap');
            .stApp, .stSidebar, h1, h2, h3, h4, p, div, span, label, button, [data-testid="stMetricLabel"], [data-testid="stMetricValue"], [data-testid="stMetricDelta"] {
                font-family: 'Times New Roman', Times, serif !important;
            }
            .stApp { background-color: #0e1117; color: #fafafa; }
            .stSidebar { background-color: #1a1d24; }
            [data-testid="stMetric"] {
                background-color: #262730; padding: 15px; border-radius: 8px; border-left: 5px solid #4da6ff; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            }
            [data-testid="stMetricLabel"] { color: #fafafa !important; }
            [data-testid="stMetricValue"] { color: #fafafa !important; }
            [data-testid="stMetricDelta"] { color: #fafafa !important; }
            button[data-baseweb="tab"] { font-size: 14px !important; font-weight: bold !important; }
            .stTabs [data-baseweb="tab-list"] { background-color: #1a1d24; }
            .stTextInput > div > div > input, .stSelectbox > div > div > div, .stRadio > label { color: #fafafa !important; }
        </style>
        """
    else:
        return """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Times+New+Roman&display=swap');
            .stApp, .stSidebar, h1, h2, h3, h4, p, div, span, label, button, [data-testid="stMetricLabel"], [data-testid="stMetricValue"], [data-testid="stMetricDelta"] {
                font-family: 'Times New Roman', Times, serif !important;
            }
            [data-testid="stMetric"] {
                background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #0066cc; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            button[data-baseweb="tab"] { font-size: 14px !important; font-weight: bold !important; }
        </style>
        """

st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)

# ==============================================================================
# 3. DATA STRUCTURES (NO EMOJIS IN KEYS TO PREVENT KEYERROR)
# ==============================================================================
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

EAC_NATIONAL = {
    "Kenya": {"lat": -0.0236, "lon": 37.9062, "mal": 45, "cholera": 90, "mmr": 342, "fic": 80, "oop": 25, "htn": 27.0, "poverty": 22, "schools": 12000, "markets": 3500},
    "Uganda": {"lat": 1.3733, "lon": 32.2903, "mal": 120, "cholera": 110, "mmr": 336, "fic": 76, "oop": 32, "htn": 26.0, "poverty": 31, "schools": 9500, "markets": 2800},
    "Rwanda": {"lat": -1.9403, "lon": 29.8739, "mal": 35, "cholera": 20, "mmr": 248, "fic": 92, "oop": 12, "htn": 21.0, "poverty": 16, "schools": 4200, "markets": 1100},
    "Burundi": {"lat": -3.3731, "lon": 29.9189, "mal": 250, "cholera": 180, "mmr": 548, "fic": 71, "oop": 18, "htn": 18.0, "poverty": 45, "schools": 3800, "markets": 950},
    "South Sudan": {"lat": 6.8770, "lon": 31.3070, "mal": 310, "cholera": 220, "mmr": 1150, "fic": 55, "oop": 45, "htn": 16.0, "poverty": 62, "schools": 2100, "markets": 600}
}

# ==============================================================================
# 4. CACHED MAP BUILDER (Fixes Blinking Issue)
# ==============================================================================
@st.cache_resource
def build_map(lat, lon, zoom):
    m = folium.Map(location=[lat, lon], zoom_start=zoom, tiles="OpenStreetMap")
    
    hosp_group = FeatureGroup(name='🏥 Health Facilities')
    for i in range(5):
        folium.Marker(location=[lat + np.random.uniform(-0.1, 0.1), lon + np.random.uniform(-0.1, 0.1)], popup=f"<b>Health Facility {i+1}</b>", icon=folium.Icon(color='red', icon='plus', prefix='fa')).add_to(hosp_group)
    hosp_group.add_to(m)
    
    wash_group = FeatureGroup(name='💧 WASH Points')
    for i in range(8):
        folium.CircleMarker(location=[lat + np.random.uniform(-0.15, 0.15), lon + np.random.uniform(-0.15, 0.15)], radius=8, color='blue', fill=True, fill_opacity=0.7, popup=f"<b>Water Point {i+1}</b>").add_to(wash_group)
    wash_group.add_to(m)
    
    school_group = FeatureGroup(name='🏫 Schools')
    for i in range(6):
        folium.RegularPolygonMarker(location=[lat + np.random.uniform(-0.12, 0.12), lon + np.random.uniform(-0.12, 0.12)], number_of_sides=4, radius=10, color='green', fill=True, fill_opacity=0.7, popup=f"<b>School {i+1}</b>").add_to(school_group)
    school_group.add_to(m)
    
    market_group = FeatureGroup(name='🛒 Markets')
    for i in range(4):
        folium.RegularPolygonMarker(location=[lat + np.random.uniform(-0.08, 0.08), lon + np.random.uniform(-0.08, 0.08)], number_of_sides=3, radius=10, color='orange', fill=True, fill_opacity=0.7, popup=f"<b>Market {i+1}</b>").add_to(market_group)
    market_group.add_to(m)
    
    folium.LayerControl(collapsed=False).add_to(m)
    return m

# ==============================================================================
# 5. AFRICA'S TALKING USSD DEMO ENGINE
# ==============================================================================
def simulate_africas_talking_ussd(region, data, lang):
    ussd_menu = {'session_id': f"ATSim_{datetime.now().strftime('%Y%m%d%H%M%S')}", 'service_code': "*384*27#", 'phone_number': "+255712345678"}
    screens = [
        {'step': 1, 'title': "USSD Menu - Home", 'display': "EcoHealth Sentinel\n1. Report Disease Case\n2. Check Medicine Stock\n3. View Regional Alerts\n0. Exit", 'api_text': ""},
        {'step': 2, 'title': "USSD Menu - Report Case", 'display': "Report Disease Case:\n1. Malaria\n2. Cholera\n3. Maternal Emergency\n4. NCD\n9. Back", 'api_text': "1"},
        {'step': 3, 'title': "USSD Menu - Malaria Report", 'display': f"Malaria Report - {region}\nEnter number of cases:\n[Input Field]\n0. Cancel", 'api_text': "1"},
        {'step': 4, 'title': "USSD - Confirmation", 'display': f"✅ Report Submitted!\nRegion: {region}\nCases: 5\nAlert sent to District MO.\nReference: ECO-{datetime.now().strftime('%Y%m%d')}\n0. Exit", 'api_text': "5"}
    ]
    api_payload = {"sessionId": ussd_menu['session_id'], "serviceCode": ussd_menu['service_code'], "phoneNumber": ussd_menu['phone_number'], "text": "1\n1\n5"}
    at_response = {"status": "success", "message": "USSD session processed", "responses": [{"CON EcoHealth Sentinel\n1. Report Case\n2. Check Stock\n3. Alerts\n0. Exit"}, {"CON Report Case:\n1. Malaria\n2. Cholera\n9. Back"}, {"CON Enter cases for Malaria:"}, {"END ✅ Report submitted! Ref: ECO-2026. Alert sent to MO."}]}
    return screens, api_payload, at_response

# ==============================================================================
# 6. AUTHENTICATION SYSTEM
# ==============================================================================
if 'user' not in st.session_state: st.session_state.user = None
if 'auth_step' not in st.session_state: st.session_state.auth_step = 'login'
if 'lang' not in st.session_state: st.session_state.lang = 'en'

L = T[st.session_state.lang]
st.sidebar.title(f"🌍 {L['title']}")

if st.session_state.user is None:
    if st.session_state.auth_step == 'login':
        st.sidebar.header(L['login'])
        email = st.sidebar.text_input(L['email'], placeholder="name@hospital.go.tz")
        password = st.sidebar.text_input(L['password'], type="password")
        if st.sidebar.button(L['login_btn'], use_container_width=True) and email and password:
            st.session_state.user = {"email": email, "name": email.split('@')[0].capitalize(), "role": L['verified'], "org": "Ministry of Health"}
            st.rerun()
        st.sidebar.markdown("---")
        st.sidebar.write(L['new_user'])
        if st.sidebar.button(L['create_account'], use_container_width=True):
            st.session_state.auth_step = 'signup'; st.rerun()
            
    elif st.session_state.auth_step == 'signup':
        st.sidebar.header(L['signup_header'])
        name = st.sidebar.text_input(L['full_name'])
        email = st.sidebar.text_input(L['email'])
        org = st.sidebar.selectbox(L['organization'], L['orgs'])
        password = st.sidebar.text_input(L['create_pass'], type="password")
        confirm = st.sidebar.text_input(L['confirm_pass'], type="password")
        
        if st.sidebar.button(L['signup_btn'], use_container_width=True):
            if password == confirm and len(password) > 5:
                st.session_state.pending_user = {"name": name, "email": email, "org": org}
                st.session_state.auth_step = 'verify'; st.rerun()
            else: st.sidebar.error(L['pass_error'])
        if st.sidebar.button(L['back_login'], use_container_width=True):
            st.session_state.auth_step = 'login'; st.rerun()
            
    elif st.session_state.auth_step == 'verify':
        st.sidebar.header(L['verify_header'])
        st.sidebar.success(f"{L['code_sent']} {st.session_state.pending_user['email']}")
        code = st.sidebar.text_input(L['enter_code'], placeholder="123456")
        if st.sidebar.button(L['verify_btn'], use_container_width=True):
            if code == "123456": 
                st.session_state.user = st.session_state.pending_user
                st.session_state.user["role"] = L['verified']
                st.session_state.auth_step = 'login'; st.rerun()
            else: st.sidebar.error(L['invalid_code'])
else:
    st.sidebar.header(f"👤 {L['welcome']}, {st.session_state.user['name']}!")
    st.sidebar.success(f"✅ {st.session_state.user['role']}")
    st.sidebar.info(f"🏢 {st.session_state.user.get('org', 'Tanzania MoH')}")
    st.sidebar.markdown("---")
    st.sidebar.subheader(L['premium'])
    st.sidebar.write(L['premium_desc'])
    st.sidebar.link_button(L['subscribe'], "https://buymeacoffee.com/ecohealth", use_container_width=True)
    st.sidebar.markdown("---")
    st.sidebar.subheader(L['green_ai'])
    st.sidebar.metric(L['co2_saved'], "0.045 kg/prediction", delta=L['co2_delta'])
    st.sidebar.caption("Lightweight heuristic models used instead of energy-intensive LLMs. Compliant with Sustainable AI principles (Ueda et al., 2024).")
    st.sidebar.markdown("---")
    if st.sidebar.button(L['logout'], use_container_width=True): 
        st.session_state.user = None; st.session_state.auth_step = 'login'; st.rerun()

# ==============================================================================
# 7. APP SETTINGS (Country, Region, Role, Language, Theme)
# ==============================================================================
st.sidebar.header(L['settings'])

lang_choice = st.sidebar.radio(L['lang'], L['languages'])
if lang_choice == "Kiswahili":
    st.session_state.lang = 'sw'
    L = T['sw']
else:
    st.session_state.lang = 'en'
    L = T['en']

theme_choice = st.sidebar.radio(L['theme'], L['themes'])
if theme_choice != st.session_state.theme:
    st.session_state.theme = theme_choice
    st.rerun()

# Country & Region (Exact string matching to prevent KeyError)
country = st.sidebar.selectbox(L['country'], ["Tanzania", "Kenya", "Uganda", "Rwanda", "Burundi", "South Sudan"])

if country == "Tanzania":
    region = st.sidebar.selectbox(L['region'], list(TANZANIA_REGIONS.keys()))
    data = TANZANIA_REGIONS[region]
    policy_text = L['policy']
else:
    region = "National Overview"
    data = EAC_NATIONAL[country]
    policy_text = "National Health Strategy & EAC Protocol"

role = st.sidebar.selectbox(L['role'], L['roles'])

st.title(f"{L['title']}: {region}, {country}")
st.info(f"🛡️ {policy_text}")

role_messages = {
    'en': {
        'Policymaker': "👔 Viewing as Policymaker: Focus on KPIs, funding gaps, and population-level trends.",
        'Community Health Worker (CHW)': " Viewing as CHW: Focus on actionable tasks, USSD alerts, and community-level data.",
        'Student/Researcher': "🎓 Viewing as Researcher: Focus on raw data, correlations, and downloadable datasets.",
        'NGO Partner': "🤝 Viewing as NGO: Focus on funding gaps, partnership opportunities, and impact metrics."
    },
    'sw': {
        'Policymaker': "👔 Unatazama kama Mtunga Sera: Lengo ni viashiria vya msingi, mapungufu ya fedha, na mwenendo.",
        'Community Health Worker (CHW)': "📱 Unatazama kama CHW: Lengo ni kazi zinazofanyika, tahadhari za USSD, na data ya jamii.",
        'Student/Researcher': "🎓 Unatazama kama Mtafiti: Lengo ni data ghafi, uhusiano, na datasets zinazopakuliwa.",
        'NGO Partner': "🤝 Unatazama kama NGO: Lengo ni mapungufu ya ufadhili, fursa za ushirikiano, na viashiria vya athari."
    }
}
st.success(role_messages[st.session_state.lang][role])

tab1, tab2, tab3, tab4 = st.tabs([L['tab1'], L['tab2'], L['tab3'], L['tab4']])

# ==============================================================================
# TAB 1: EXECUTIVE DASHBOARD
# ==============================================================================
with tab1:
    st.header(L['surveillance'])
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(L['malaria'], data['mal'], delta="+5%")
    c2.metric(L['cholera'], data['cholera'], delta="+15%", delta_color="inverse")
    c3.metric(L['mmr'], data['mmr'], delta="-4")
    c4.metric(L['fic'], f"{data['fic']}%", delta="+2%")
    c5.metric(L['oop'], f"{data['oop']}%", delta="-1%")

    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(L['sdg'])
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number", value=data['mmr'],
            title={'text': L['mmr_target'], 'font': {'size': 16}},
            number={'font': {'size': 24}},
            gauge={'axis': {'range': [0, 200], 'tickwidth': 1, 'tickcolor': "darkblue"},
                   'bar': {'color': "darkred"}, 'bgcolor': "white", 'borderwidth': 2, 'bordercolor': "gray",
                   'steps': [{'range': [0, 70], 'color': 'lightgreen'}, {'range': [70, 120], 'color': 'yellow'}, {'range': [120, 200], 'color': 'red'}]}
        ))
        fig_g.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20), font=dict(family='Times New Roman'))
        st.plotly_chart(fig_g, use_container_width=True)

    with col2:
        st.subheader(L['immunity'])
        fig_b = go.Figure(data=[
            go.Bar(name='Penta 1', x=['Coverage'], y=[90], marker_color='lightblue'),
            go.Bar(name='Penta 3', x=['Coverage'], y=[85], marker_color='blue'),
            go.Bar(name='Fully Immunized', x=['Coverage'], y=[data['fic']], marker_color='darkblue')
        ])
        fig_b.update_layout(title=L['vaccine_retention'], yaxis=dict(range=[0, 100], title="Percentage"), plot_bgcolor='white', font=dict(family='Times New Roman'))
        st.plotly_chart(fig_b, use_container_width=True)

# ==============================================================================
# TAB 2: SOCIO-ECOLOGICAL & SERVICES MAP (FIXED BLINKING)
# ==============================================================================
with tab2:
    st.header("🌍 Socio-Ecological Determinants & Social Services")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader(L['social'])
        st.metric(L['poverty'], f"{data['poverty']}%")
        st.metric(L['hypertension'], f"{data['htn']}%")
        st.metric(L['schools'], data['schools'])
        st.metric(L['markets'], data['markets'])
        st.markdown("---")
        st.subheader(L['map_guide'])
        st.info(L['map_guide_text'])

    with col2:
        st.subheader(f"{L['interactive_map']}: {region}")
        zoom_level = 9 if country == "Tanzania" else 6
        cached_map = build_map(data['lat'], data['lon'], zoom_level)
        st_folium(cached_map, width=800, height=600, key="main_map")

# ==============================================================================
# TAB 3: AI, FHIR & USSD (WITH AFRICA'S TALKING DEMO)
# ==============================================================================
with tab3:
    st.header(L['ai_header'])
    
    if "messages" not in st.session_state: st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]): st.markdown(message["content"])
            
    prompt = st.chat_input(L['chat_placeholder'].format(region=region))
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        if "malaria" in prompt.lower() or "cholera" in prompt.lower():
            response = L['alert_malaria'].format(region=region, mal=data['mal'], cholera=data['cholera'])
        elif "vaccine" in prompt.lower() or "fic" in prompt.lower():
            response = L['alert_vaccine'].format(region=region, fic=data['fic'])
        else:
            response = L['summary'].format(region=region, mmr=data['mmr'], htn=data['htn'], poverty=data['poverty'])
        
        fhir_payload = {"resourceType": "Bundle", "type": "transaction", "entry": [{"resource": {"resourceType": "CarePlan", "status": "active", "intent": "plan", "title": f"Intervention for {region}", "subject": {"reference": f"Location/TZ-{region}"}}}]}
        full_response = f"{response}\n\n**{L['fhir_title']}:**\n```json\n{json.dumps(fhir_payload, indent=2)}\n```"
        
        with st.chat_message("assistant"): st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    st.markdown("---")
    st.subheader(L['ussd_header'])
    st.caption(L['ussd_desc'])
    
    if st.button(f"📱 {L['ussd_start']}", use_container_width=True):
        screens, api_payload, at_response = simulate_africas_talking_ussd(region, data, st.session_state.lang)
        st.markdown("### " + L['ussd_session'])
        cols = st.columns(4)
        for i, screen in enumerate(screens):
            with cols[i]:
                st.markdown(f"**Step {screen['step']}: {screen['title']}**")
                st.code(screen['display'], language='text')
                if screen['api_text']:
                    st.markdown(f"*User input: `{screen['api_text']}`*")
        
        st.markdown("---")
        col_api1, col_api2 = st.columns(2)
        with col_api1:
            st.markdown("### 📤 " + L['ussd_payload'] + " (Request)")
            st.code(json.dumps(api_payload, indent=2), language='json')
            st.caption("POST to: https://api.africastalking.com/version1/ussd")
        with col_api2:
            st.markdown("### 📥 Africa's Talking Response")
            st.code(json.dumps(at_response, indent=2), language='json')
            st.caption("CON = Continue session, END = Terminate session")
        
        st.markdown("---")
        st.info("""
        **🔗 Integration Architecture:**
        1. CHW dials `*384*27#` on any mobile phone (no smartphone required)
        2. Request routed through **Africa's Talking USSD Gateway**
        3. Webhook sends session data to **EcoHealth Sentinel Backend**
        4. Backend processes request, updates DHIS2, generates FHIR payload
        5. Response sent back via Africa's Talking to CHW's phone
        6. **Cost:** ~$0.01 per session (billed to MoH account)
        """)

# ==============================================================================
# TAB 4: POLICY BRIEF
# ==============================================================================
with tab4:
    st.header(L['brief_header'])
    brief = f"""
POLICY BRIEF: EcoHealth Sentinel
Region: {region}, {country}
Role Focus: {role}
Date: {datetime.now().strftime('%B %d, %Y')}

1. EXECUTIVE SUMMARY
{region} faces a double burden of disease. Malaria incidence is {data['mal']} per 1,000, and Cholera cases are at {data['cholera']}. Maternal Mortality is {data['mmr']} per 100,000. Immediate action is required.

2. KEY FINDINGS
- Malaria: {data['mal']} per 1,000 population.
- Cholera: {data['cholera']} suspected cases.
- Vaccination (FIC): {data['fic']}% (Target >80%).
- Poverty Index: {data['poverty']}%.
- Hypertension: {data['htn']}%.

3. RECOMMENDATIONS (Tailored for {role})
1. Deploy OCV and WASH interventions for Cholera.
2. Distribute LLINs and RDTs for Malaria.
3. Scale up ANC and SBA services to reduce MMR.
4. Integrate NCD screening into community outreach.

4. MONITORING
- Reduce Cholera cases by 20% in 30 days.
- Increase FIC to >80% in 6 months.
- Maintain medicine stockout rate below 5%.

References: {policy_text}, WHO Guidelines, HSSP V, Vision 2050.
"""
    st.text_area(L['preview'], brief, height=400)
    st.download_button(L['download'], brief, file_name=f"Brief_{region}_{country}.txt")
