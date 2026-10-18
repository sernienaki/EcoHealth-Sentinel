import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium import FeatureGroup
import streamlit.components.v1 as components
import plotly.graph_objects as go
import json
from datetime import datetime

# ==============================================================================
# 1. TRANSLATION DICTIONARY (ENGLISH / KISWAHILI) - UPDATED WITH 20 INDICATORS
# ==============================================================================
T = {
    'en': {
        'title': "EcoHealth Sentinel",
        'welcome': "Welcome", 'verified': "Verified Professional", 'settings': "⚙️ Settings",
        'country': "Select Country", 'region': "Select Region (Tanzania)", 'role': "Your Role / Jukumu Lako",
        'lang': "Language / Lugha", 'theme': "Theme / Mandhari",
        'tab1': "📊 Executive Dashboard", 'tab2': "🌍 Socio-Ecological & Services", 'tab3': "🤖 AI, FHIR & USSD", 'tab4': " Policy Brief",
        'policy': "Policy: HSSP V, Vision 2050 & PDPA 2022 | ITU ML Pipeline Compliant",
        'surveillance': "Comprehensive Public Health Surveillance",
        'dhis2_header': "20 Core DHIS2 Indicators (WHO & HSSP V Aligned)",
        'cat_comm': "1. Communicable Diseases & Climate",
        'cat_mnch': "2. Maternal, Newborn & Child Health (MNCH)",
        'cat_ncd': "3. Non-Communicable Diseases (NCDs) & Risk Factors",
        'cat_sys': "4. Health Systems Strengthening & UHC",
        'target_chart': "DHIS2 Indicator Performance: Current vs. National Target",
        # 20 Indicators
        'malaria': "Malaria Incidence (per 1k)", 'mal_target': 50,
        'mal_pos': "Malaria Test Positivity (%)", 'pos_target': 20,
        'cholera': "Cholera Cases", 'chol_target': 0,
        'tb': "TB Notification (per 100k)", 'tb_target': 150,
        'llin': "LLIN Utilization (%)", 'llin_target': 80,
        'mmr': "Maternal Mortality (per 100k)", 'mmr_target': 70,
        'imr': "Infant Mortality Rate (per 1k)", 'imr_target': 12,
        'anc4': "ANC 4+ Coverage (%)", 'anc_target': 80,
        'sba': "Skilled Birth Attendance (%)", 'sba_target': 90,
        'sam': "Severe Acute Malnutrition (%)", 'sam_target': 2,
        'fic': "Fully Immunized Children (%)", 'fic_target': 90,
        'penta_drop': "Penta3 Dropout Rate (%)", 'drop_target': 5,
        'htn': "Hypertension Screening (%)", 'htn_target': 60,
        'dm': "Diabetes Screening (%)", 'dm_target': 50,
        'cervical': "Cervical Cancer Screening (%)", 'cerv_target': 70,
        'tobacco': "Tobacco Use Prevalence (%)", 'tob_target': 10,
        'stockout': "Essential Meds Stockout (%)", 'stock_target': 5,
        'hw': "Health Worker Density (per 1k)", 'hw_target': 0.45,
        'oop': "Out-of-Pocket Expenditure (%)", 'oop_target': 15,
        'poverty': "Poverty Index", 'schools': "Schools", 'markets': "Markets",
        'social': "Social & Economic Indicators",
        'map_guide': "How to Read This Map",
        'map_guide_text': "**Red Pins:** Health Facilities\n**Blue Circles:** WASH Points\n**Green Squares:** Schools\n**Orange Triangles:** Markets\n*Toggle layers using the icon on the top right.*",
        'interactive_map': "Interactive Service Map",
        'ai_header': "AI Agent & Interoperability",
        'chat_placeholder': "Ask about health risks in {region}",
        'ussd_header': "📱 EcoHealth USSD Services", 'ussd_subheader': "Access on any mobile phone (No smartphone required)",
        'ussd_start': "View USSD Menu Flow", 'ussd_session': "USSD Session Flow",
        'network_codes': "Network Subscription Shortcodes (Tanzania)",
        'network_desc': "Dial the code below on your respective network to access EcoHealth USSD services:",
        'how_it_works': "**How it works:**\n1. Dial the shortcode for your network.\n2. Navigate the menu using numbers (1, 2, 3...).\n3. Reports are sent directly to the District Medical Officer.\n4. Standard USSD rates apply (approx. 50 TZS per session).",
        'brief_header': "Policy Brief Generator", 'download': "📥 Download Brief", 'preview': "Preview",
        'roles': ["Policymaker", "Community Health Worker (CHW)", "Student/Researcher", "NGO Partner"],
        'languages': ["English", "Kiswahili"], 'themes': ["Light Mode", "Dark Mode"],
        'green_ai': "♻️ Green AI Impact", 'co2_saved': "CO2 Saved", 'co2_delta': "-99% vs LLMs",
        'premium': "🌟 Premium Subscription", 'premium_desc': "Unlock Advanced AI, Bulk DHIS2 Exports, and Offline CHW Mode.",
        'subscribe': "💳 Subscribe for $1/month", 'logout': "🚪 Log Out", 'login': "👤 Sign In",
        'email': "Email Address", 'password': "Password", 'login_btn': "Log In",
        'new_user': "New to EcoHealth Sentinel?", 'create_account': "Create Account",
        'signup_header': "📝 Create Account", 'full_name': "Full Name", 'organization': "Organization",
        'create_pass': "Create Password", 'confirm_pass': "Confirm Password",
        'signup_btn': "Sign Up & Send Verification", 'back_login': "Back to Login",
        'verify_header': "📧 Verify Email", 'code_sent': "Code sent to", 'enter_code': "Enter 6-digit code",
        'verify_btn': "Verify Account", 'invalid_code': "Invalid code. Try 123456.", 'pass_error': "Passwords do not match or too short.",
        'orgs': ["Ministry of Health", "NGO", "Research Institute", "Community Health Worker", "Other"],
        'alert_malaria': "🚨 **Alert for {region}:** High risk detected. Malaria: {mal}/1k, Cholera: {cholera} cases. Recommend immediate WASH intervention and LLIN distribution.",
        'alert_vaccine': "💉 **Immunization in {region}:** FIC is at {fic}%. Below target. Recommend mop-up campaigns in rural wards.",
        'summary': "📊 **Summary for {region}:** MMR is {mmr}. Hypertension is {htn}%. Poverty index is {poverty}%.",
        'fhir_title': "GoTHoMIS FHIR Payload",
    },
    'sw': {
        'title': "EcoHealth Sentinel",
        'welcome': "Karibu", 'verified': "Mtaalamu Aliyethibitishwa", 'settings': "⚙️ Mipangilio",
        'country': "Chagua Nchi", 'region': "Chagua Mkoa (Tanzania)", 'role': "Jukumu Lako / Your Role",
        'lang': "Lugha / Language", 'theme': "Mandhari / Theme",
        'tab1': " Dashibodi Kuu", 'tab2': "🌍 Jamii na Huduma", 'tab3': "🤖 AI, FHIR na USSD", 'tab4': "📄 Hati ya Sera",
        'policy': "Sera: HSSP V, Vision 2050 na PDPA 2022 | ITU ML Pipeline",
        'surveillance': "Ufuatiliaji wa Afya ya Umma",
        'dhis2_header': "Viashiria 20 vya Msingi vya DHIS2 (WHO na HSSP V)",
        'cat_comm': "1. Magonjwa ya Kuambukiza na Hali ya Hewa",
        'cat_mnch': "2. Afya ya Mama, Mtoto na Chanjo (MNCH)",
        'cat_ncd': "3. Magonjwa Yasiyoambukiza (NCD) na Hatari",
        'cat_sys': "4. Uimarishaji wa Mfumo wa Afya na UHC",
        'target_chart': "Utendaji wa Viashiria vya DHIS2: Sasa dhidi ya Lengo la Taifa",
        # 20 Indicators
        'malaria': "Mripuko wa Malaria (kwa 1k)", 'mal_target': 50,
        'mal_pos': "Uchunguzi Chanya wa Malaria (%)", 'pos_target': 20,
        'cholera': "Visa vya Kipindupindu", 'chol_target': 0,
        'tb': "Visa vya TB (kwa 100k)", 'tb_target': 150,
        'llin': "Matumizi ya Vyandarua (%)", 'llin_target': 80,
        'mmr': "Vifo vya Mama (kwa 100k)", 'mmr_target': 70,
        'imr': "Vifo vya Watoto (kwa 1k)", 'imr_target': 12,
        'anc4': "Huduma ya ANC 4+ (%)", 'anc_target': 80,
        'sba': "Kuzaliwa na Mtaalamu (%)", 'sba_target': 90,
        'sam': "Ukosefu Mkubwa wa Lishe (%)", 'sam_target': 2,
        'fic': "Watoto Waliochanjika Kamili (%)", 'fic_target': 90,
        'penta_drop': "Kushuka kwa Chanjo ya Penta3 (%)", 'drop_target': 5,
        'htn': "Uchunguzi wa Shinikizo (%)", 'htn_target': 60,
        'dm': "Uchunguzi wa Kisukari (%)", 'dm_target': 50,
        'cervical': "Uchunguzi wa Saratani ya Shingo ya Mkojo (%)", 'cerv_target': 70,
        'tobacco': "Matumizi ya Tumbaku (%)", 'tob_target': 10,
        'stockout': "Uhaba wa Dawa Muhimu (%)", 'stock_target': 5,
        'hw': "Msongamano wa Watumishi wa Afya", 'hw_target': 0.45,
        'oop': "Gharama ya Mfukoni (%)", 'oop_target': 15,
        'poverty': "Kiwango cha Umaskini", 'schools': "Shule", 'markets': "Masoko",
        'social': "Viashiria vya Kijamii na Kiuchumi", 
        'map_guide': "Jinsi ya Kusoma Ramani",
        'map_guide_text': "**Vipini Vyekundu:** Vituo vya Afya\n**Vidudu vya Bluu:** Vyanzo vya Maji\n**Mraba wa Kijani:** Shule\n**Pembetatu ya Chungwa:** Masoko\n*Badilisha tabaka kwa kutumia ikoni juu kulia.*",
        'interactive_map': "Ramani ya Huduma",
        'ai_header': "Wakala wa AI na Uunganishaji",
        'chat_placeholder': "Uliza kuhusu hatari za afya katika {region}",
        'ussd_header': " Huduma za USSD za EcoHealth", 'ussd_subheader': "Tumia simu yoyote (Haitajani smartphone)",
        'ussd_start': "Tazama Mtiririko wa Menyu ya USSD", 'ussd_session': "Mtiririko wa USSD",
        'network_codes': "Namba za Ufupishi za Mitandao (Tanzania)",
        'network_desc': "Piga namba hizi kwenye mtandao wako kufikia huduma za USSD za EcoHealth:",
        'how_it_works': "**Jinsi inavyofanya kazi:**\n1. Piga namba ya ufupishi ya mtandao wako.\n2. Tumia namba (1, 2, 3...) kusogeza menyu.\n3. Ripoti zinatumwa moja kwa moja kwa Mganga Mkuu wa Wilaya.\n4. Gharama za kawaida za USSD zinatumika (takriban 50 TZS).",
        'brief_header': "Kizalishaji cha Hati ya Sera", 'download': "📥 Pakua Hati", 'preview': "Hakiki",
        'roles': ["Mtunga Sera", "Mhudumu wa Afya wa Jamii (CHW)", "Mwanafunzi/Mtafiti", "Mshirika wa NGO"],
        'languages': ["English", "Kiswahili"], 'themes': ["Hali ya Mwanga", "Hali ya Giza"],
        'green_ai': "♻️ Athari ya AI ya Kijani", 'co2_saved': "CO2 Iliyookolewa", 'co2_delta': "-99% ikilinganishwa na LLM",
        'premium': "🌟 Uanachama wa Premium", 'premium_desc': "Fungua AI ya Hali ya Juu, Usafirishaji wa DHIS2, na Hali ya Nje ya Mtandao.",
        'subscribe': "💳 Jiandikishe kwa $1/mwezi", 'logout': "🚪 Toka", 'login': "👤 Ingia",
        'email': "Barua Pepe", 'password': "Nenosiri", 'login_btn': "Ingia",
        'new_user': "Mgeni kwenye EcoHealth Sentinel?", 'create_account': "Fungua Akaunti",
        'signup_header': "📝 Fungua Akaunti", 'full_name': "Jina Kamili", 'organization': "Mashirika",
        'create_pass': "Unda Nenosiri", 'confirm_pass': "Thibitisha Nenosiri",
        'signup_btn': "Jiandikishe na Tuma Uthibitisho", 'back_login': "Rudi Kuingia",
        'verify_header': "📧 Thibitisha Barua Pepe", 'code_sent': "Msimbo umetumwa kwa", 'enter_code': "Weka msimbo wa tarakimu 6",
        'verify_btn': "Thibitisha Akaunti", 'invalid_code': "Msimbo si sahihi. Jaribu 123456.", 'pass_error': "Manenosiri hayalingani au ni mafupi.",
        'orgs': ["Wizara ya Afya", "NGO", "Taasisi ya Utafiti", "Mhudumu wa Afya wa Jamii", "Nyingine"],
        'alert_malaria': "🚨 **Tahadhari kwa {region}:** Hatari kubwa imegunduliwa. Malaria: {mal}/1k, Kipindupindu: {cholera} visa. Tunapendekeza kuingilia kati haraka.",
        'alert_vaccine': "💉 **Chanjo katika {region}:** FIC iko {fic}%. Chini ya lengo. Tunapendekeza kampeni za kufikia maeneo ya vijijini.",
        'summary': "📊 **Muhtasari wa {region}:** MMR ni {mmr}. Shinikizo la damu ni {htn}%. Umaskini ni {poverty}%.",
        'fhir_title': "Mzigo wa GoTHoMIS FHIR",
    }
}

# ==============================================================================
# 2. HIGH-END UI & THEME CSS
# ==============================================================================
st.set_page_config(page_title="EcoHealth Sentinel: Tanzania & EAC", layout="wide", initial_sidebar_state="expanded")

if 'theme' not in st.session_state: st.session_state.theme = 'Light Mode'

def get_theme_css(theme):
    if theme == 'Dark Mode':
        return """<style>@import url('https://fonts.googleapis.com/css2?family=Times+New+Roman&display=swap');.stApp, .stSidebar, h1, h2, h3, h4, p, div, span, label, button, [data-testid="stMetricLabel"], [data-testid="stMetricValue"], [data-testid="stMetricDelta"] {font-family: 'Times New Roman', Times, serif !important;}.stApp { background-color: #0e1117; color: #fafafa; }.stSidebar { background-color: #1a1d24; }[data-testid="stMetric"] {background-color: #262730; padding: 15px; border-radius: 8px; border-left: 5px solid #4da6ff; box-shadow: 0 4px 6px rgba(0,0,0,0.3);}[data-testid="stMetricLabel"], [data-testid="stMetricValue"], [data-testid="stMetricDelta"] { color: #fafafa !important; }button[data-baseweb="tab"] { font-size: 14px !important; font-weight: bold !important; }.stTabs [data-baseweb="tab-list"] { background-color: #1a1d24; }.stTextInput > div > div > input, .stSelectbox > div > div > div, .stRadio > label { color: #fafafa !important; }</style>"""
    else:
        return """<style>@import url('https://fonts.googleapis.com/css2?family=Times+New+Roman&display=swap');.stApp, .stSidebar, h1, h2, h3, h4, p, div, span, label, button, [data-testid="stMetricLabel"], [data-testid="stMetricValue"], [data-testid="stMetricDelta"] {font-family: 'Times New Roman', Times, serif !important;}[data-testid="stMetric"] {background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #0066cc; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}button[data-baseweb="tab"] { font-size: 14px !important; font-weight: bold !important; }</style>"""

st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)

# ==============================================================================
# 3. DATA STRUCTURES (UPDATED WITH ALL 20 DHIS2 INDICATORS)
# ==============================================================================
TANZANIA_REGIONS = {
    "Dar es Salaam": {"lat": -6.7924, "lon": 39.2083, "mal": 15, "mal_pos": 12, "cholera": 450, "tb": 210, "llin": 70, "mmr": 85, "imr": 19, "anc4": 68, "sba": 85, "sam": 2.5, "fic": 82, "penta_drop": 4, "htn": 31.2, "dm": 3.5, "cervical": 25, "tobacco": 9, "stockout": 8, "hw": 0.25, "oop": 32, "poverty": 12, "schools": 450, "markets": 120},
    "Dodoma": {"lat": -6.1630, "lon": 35.7516, "mal": 45, "mal_pos": 22, "cholera": 80, "tb": 180, "llin": 65, "mmr": 115, "imr": 26, "anc4": 58, "sba": 75, "sam": 4.0, "fic": 75, "penta_drop": 6, "htn": 22.0, "dm": 2.1, "cervical": 15, "tobacco": 7, "stockout": 12, "hw": 0.10, "oop": 35, "poverty": 28, "schools": 320, "markets": 85},
    "Mwanza": {"lat": -2.5164, "lon": 32.9175, "mal": 210, "mal_pos": 38, "cholera": 210, "tb": 250, "llin": 60, "mmr": 130, "imr": 28, "anc4": 55, "sba": 70, "sam": 5.5, "fic": 70, "penta_drop": 8, "htn": 20.5, "dm": 1.8, "cervical": 12, "tobacco": 6, "stockout": 15, "hw": 0.12, "oop": 30, "poverty": 25, "schools": 280, "markets": 60},
    "Arusha": {"lat": -3.3869, "lon": 36.6830, "mal": 35, "mal_pos": 15, "cholera": 40, "tb": 160, "llin": 75, "mmr": 95, "imr": 21, "anc4": 72, "sba": 88, "sam": 3.0, "fic": 85, "penta_drop": 3, "htn": 26.0, "dm": 2.8, "cervical": 22, "tobacco": 8, "stockout": 7, "hw": 0.18, "oop": 28, "poverty": 18, "schools": 310, "markets": 75},
    "Kilimanjaro": {"lat": -3.3488, "lon": 37.3407, "mal": 20, "mal_pos": 10, "cholera": 30, "tb": 140, "llin": 80, "mmr": 70, "imr": 18, "anc4": 78, "sba": 92, "sam": 2.0, "fic": 88, "penta_drop": 2, "htn": 24.0, "dm": 2.5, "cervical": 28, "tobacco": 7, "stockout": 5, "hw": 0.22, "oop": 25, "poverty": 15, "schools": 290, "markets": 65},
    "Zanzibar": {"lat": -6.1659, "lon": 39.2022, "mal": 8, "mal_pos": 5, "cholera": 300, "tb": 120, "llin": 85, "mmr": 78, "imr": 18, "anc4": 80, "sba": 90, "sam": 2.2, "fic": 85, "penta_drop": 3, "htn": 28.0, "dm": 3.2, "cervical": 30, "tobacco": 5, "stockout": 6, "hw": 0.20, "oop": 25, "poverty": 14, "schools": 180, "markets": 40}
}

EAC_NATIONAL = {
    "Kenya": {"lat": -0.0236, "lon": 37.9062, "mal": 45, "mal_pos": 18, "cholera": 90, "tb": 200, "llin": 70, "mmr": 342, "imr": 28, "anc4": 68, "sba": 75, "sam": 3.2, "fic": 80, "penta_drop": 6, "htn": 27.0, "dm": 2.5, "cervical": 22, "tobacco": 9, "stockout": 10, "hw": 0.18, "oop": 25, "poverty": 22, "schools": 12000, "markets": 3500},
    "Uganda": {"lat": 1.3733, "lon": 32.2903, "mal": 120, "mal_pos": 30, "cholera": 110, "tb": 190, "llin": 60, "mmr": 336, "imr": 31, "anc4": 58, "sba": 70, "sam": 5.1, "fic": 76, "penta_drop": 8, "htn": 26.0, "dm": 1.9, "cervical": 12, "tobacco": 7, "stockout": 15, "hw": 0.14, "oop": 32, "poverty": 31, "schools": 9500, "markets": 2800},
    "Rwanda": {"lat": -1.9403, "lon": 29.8739, "mal": 35, "mal_pos": 12, "cholera": 20, "tb": 150, "llin": 85, "mmr": 248, "imr": 21, "anc4": 82, "sba": 92, "sam": 2.1, "fic": 92, "penta_drop": 2, "htn": 21.0, "dm": 1.5, "cervical": 30, "tobacco": 5, "stockout": 5, "hw": 0.22, "oop": 12, "poverty": 16, "schools": 4200, "markets": 1100},
    "Burundi": {"lat": -3.3731, "lon": 29.9189, "mal": 250, "mal_pos": 42, "cholera": 180, "tb": 280, "llin": 55, "mmr": 548, "imr": 42, "anc4": 50, "sba": 60, "sam": 6.5, "fic": 71, "penta_drop": 10, "htn": 18.0, "dm": 1.2, "cervical": 8, "tobacco": 6, "stockout": 22, "hw": 0.08, "oop": 18, "poverty": 45, "schools": 3800, "markets": 950},
    "South Sudan": {"lat": 6.8770, "lon": 31.3070, "mal": 310, "mal_pos": 50, "cholera": 220, "tb": 350, "llin": 40, "mmr": 1150, "imr": 65, "anc4": 35, "sba": 45, "sam": 12.0, "fic": 55, "penta_drop": 15, "htn": 16.0, "dm": 1.0, "cervical": 4, "tobacco": 10, "stockout": 35, "hw": 0.05, "oop": 45, "poverty": 62, "schools": 2100, "markets": 600}
}

# ==============================================================================
# 4. USSD DEMO ENGINE
# ==============================================================================
def simulate_ussd(region, data, lang):
    screens = [
        {'step': 1, 'title': "EcoHealth USSD - Home", 'display': "EcoHealth Sentinel\n1. Report Disease Case\n2. Check Medicine Stock\n3. View Regional Alerts\n0. Exit", 'api_text': ""},
        {'step': 2, 'title': "EcoHealth USSD - Report Case", 'display': "Report Disease Case:\n1. Malaria\n2. Cholera\n3. Maternal Emergency\n4. NCD\n9. Back", 'api_text': "1"},
        {'step': 3, 'title': "EcoHealth USSD - Malaria Report", 'display': f"Malaria Report - {region}\nEnter number of cases:\n[Input Field]\n0. Cancel", 'api_text': "1"},
        {'step': 4, 'title': "EcoHealth USSD - Confirmation", 'display': f"✅ Report Submitted!\nRegion: {region}\nCases: 5\nAlert sent to District MO.\nReference: ECO-{datetime.now().strftime('%Y%m%d')}\n0. Exit", 'api_text': "5"}
    ]
    return screens

# ==============================================================================
# 5. AUTHENTICATION SYSTEM
# ==============================================================================
if 'user' not in st.session_state: st.session_state.user = None
if 'auth_step' not in st.session_state: st.session_state.auth_step = 'login'
if 'lang' not in st.session_state: st.session_state.lang = 'en'

L = T[st.session_state.lang]
st.sidebar.title(f" {L['title']}")

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
    st.sidebar.header(f" {L['welcome']}, {st.session_state.user['name']}!")
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
# 6. APP SETTINGS
# ==============================================================================
st.sidebar.header(L['settings'])
lang_choice = st.sidebar.radio(L['lang'], L['languages'])
if lang_choice == "Kiswahili": st.session_state.lang = 'sw'; L = T['sw']
else: st.session_state.lang = 'en'; L = T['en']

theme_choice = st.sidebar.radio(L['theme'], L['themes'])
if theme_choice != st.session_state.theme: st.session_state.theme = theme_choice; st.rerun()

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
    'en': {'Policymaker': "👔 Viewing as Policymaker: Focus on KPIs, funding gaps, and population-level trends.", 'Community Health Worker (CHW)': "📱 Viewing as CHW: Focus on actionable tasks, USSD alerts, and community-level data.", 'Student/Researcher': "🎓 Viewing as Researcher: Focus on raw data, correlations, and downloadable datasets.", 'NGO Partner': "🤝 Viewing as NGO: Focus on funding gaps, partnership opportunities, and impact metrics."},
    'sw': {'Policymaker': "👔 Unatazama kama Mtunga Sera: Lengo ni viashiria vya msingi, mapungufu ya fedha, na mwenendo.", 'Community Health Worker (CHW)': "📱 Unatazama kama CHW: Lengo ni kazi zinazofanyika, tahadhari za USSD, na data ya jamii.", 'Student/Researcher': "🎓 Unatazama kama Mtafiti: Lengo ni data ghafi, uhusiano, na datasets zinazopakuliwa.", 'NGO Partner': "🤝 Unatazama kama NGO: Lengo ni mapungufu ya ufadhili, fursa za ushirikiano, na viashiria vya athari."}
}
st.success(role_messages[st.session_state.lang][role])

tab1, tab2, tab3, tab4 = st.tabs([L['tab1'], L['tab2'], L['tab3'], L['tab4']])

# ==============================================================================
# TAB 1: EXECUTIVE DASHBOARD (WITH 20 DHIS2 INDICATORS)
# ==============================================================================
with tab1:
    st.header(L['surveillance'])
    
    # Top 5 Hero Metrics
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(L['malaria'], data['mal'], delta="+5%")
    c2.metric(L['cholera'], data['cholera'], delta="+15%", delta_color="inverse")
    c3.metric(L['mmr'], data['mmr'], delta="-4")
    c4.metric(L['fic'], f"{data['fic']}%", delta="+2%")
    c5.metric(L['oop'], f"{data['oop']}%", delta="-1%")

    st.markdown("---")
    st.subheader(L['dhis2_header'])
    
        # Category 1: Communicable Diseases (3 per row)
    with st.expander(L['cat_comm'], expanded=True):
        st.markdown("#### Communicable Diseases & Climate")
        row1 = st.columns(3)
        row1[0].metric(L['malaria'], data['mal'], help=f"Target: <{L['mal_target']}")
        row1[1].metric(L['mal_pos'], f"{data['mal_pos']}%", help=f"Target: <{L['pos_target']}%")
        row1[2].metric(L['cholera'], data['cholera'], help=f"Target: {L['chol_target']}")
        
        row2 = st.columns(2)
        row2[0].metric(L['tb'], data['tb'], help=f"Target: <{L['tb_target']}")
        row2[1].metric(L['llin'], f"{data['llin']}%", help=f"Target: >{L['llin_target']}%")

    # Category 2: MNCH & Immunization (3 per row)
    with st.expander(L['cat_mnch'], expanded=True):
        st.markdown("#### Maternal, Newborn & Child Health")
        row1 = st.columns(3)
        row1[0].metric(L['mmr'], data['mmr'], help=f"Target: <{L['mmr_target']}")
        row1[1].metric(L['imr'], data['imr'], help=f"Target: <{L['imr_target']}")
        row1[2].metric(L['anc4'], f"{data['anc4']}%", help=f"Target: >{L['anc_target']}%")
        
        row2 = st.columns(4)
        row2[0].metric(L['sba'], f"{data['sba']}%", help=f"Target: >{L['sba_target']}%")
        row2[1].metric(L['sam'], f"{data['sam']}%", help=f"Target: <{L['sam_target']}%")
        row2[2].metric(L['fic'], f"{data['fic']}%", help=f"Target: >{L['fic_target']}%")
        row2[3].metric(L['penta_drop'], f"{data['penta_drop']}%", help=f"Target: <{L['drop_target']}%")

    # Category 3: NCDs & Risk Factors (2 per row)
    with st.expander(L['cat_ncd'], expanded=True):
        st.markdown("#### Non-Communicable Diseases & Risk Factors")
        row1 = st.columns(2)
        row1[0].metric(L['htn'], f"{data['htn']}%", help=f"Target: >{L['htn_target']}%")
        row1[1].metric(L['dm'], f"{data['dm']}%", help=f"Target: >{L['dm_target']}%")
        
        row2 = st.columns(2)
        row2[0].metric(L['cervical'], f"{data['cervical']}%", help=f"Target: >{L['cerv_target']}%")
        row2[1].metric(L['tobacco'], f"{data['tobacco']}%", help=f"Target: <{L['tob_target']}%")

    # Category 4: Health Systems & UHC (3 per row)
    with st.expander(L['cat_sys'], expanded=True):
        st.markdown("#### Health Systems Strengthening & UHC")
        row1 = st.columns(3)
        row1[0].metric(L['stockout'], f"{data['stockout']}%", help=f"Target: <{L['stock_target']}%")
        row1[1].metric(L['hw'], data['hw'], help=f"Target: >{L['hw_target']}")
        row1[2].metric(L['oop'], f"{data['oop']}%", help=f"Target: <{L['oop_target']}%")
    st.markdown("---")
    
    # Comprehensive Visualization: Target vs Actual
    st.subheader(L['target_chart'])
    
    indicators = [
        (L['malaria'], data['mal'], L['mal_target']),
        (L['mal_pos'], data['mal_pos'], L['pos_target']),
        (L['llin'], data['llin'], L['llin_target']),
        (L['mmr'], data['mmr'], L['mmr_target']),
        (L['imr'], data['imr'], L['imr_target']),
        (L['anc4'], data['anc4'], L['anc_target']),
        (L['sba'], data['sba'], L['sba_target']),
        (L['fic'], data['fic'], L['fic_target']),
        (L['htn'], data['htn'], L['htn_target']),
        (L['stockout'], data['stockout'], L['stock_target']),
        (L['oop'], data['oop'], L['oop_target'])
    ]
    
    names = [i[0] for i in indicators]
    current_vals = [i[1] for i in indicators]
    target_vals = [i[2] for i in indicators]
    
    fig_target = go.Figure()
    fig_target.add_trace(go.Bar(name='Current Value', y=names, x=current_vals, orientation='h', marker_color='#0066cc'))
    fig_target.add_trace(go.Bar(name='National Target', y=names, x=target_vals, orientation='h', marker_color='#e74c3c', opacity=0.5))
    fig_target.update_layout(
        barmode='group', height=500, yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor='white', font=dict(family='Times New Roman', size=12),
        xaxis_title="Value", legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    st.plotly_chart(fig_target, use_container_width=True)

# ==============================================================================
# TAB 2: SOCIO-ECOLOGICAL & SERVICES MAP (GLITCH-FIXED)
# ==============================================================================
with tab2:
    st.header("🌍 Socio-Ecological Determinants & Social Services")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader(L['social'])
        st.metric(L['poverty'], f"{data['poverty']}%")
        st.metric(L['htn'], f"{data['htn']}%")
        st.metric(L['schools'], data['schools'])
        st.metric(L['markets'], data['markets'])
        st.markdown("---")
        st.subheader(L['map_guide'])
        st.info(L['map_guide_text'])

    with col2:
        st.subheader(f"{L['interactive_map']}: {region}")
        zoom_level = 9 if country == "Tanzania" else 6
        
        m = folium.Map(location=[data['lat'], data['lon']], zoom_start=zoom_level, tiles="OpenStreetMap")
        
        hosp_group = FeatureGroup(name=' Health Facilities')
        for i in range(5):
            folium.Marker(location=[data['lat'] + np.random.uniform(-0.1, 0.1), data['lon'] + np.random.uniform(-0.1, 0.1)], popup=f"<b>Health Facility {i+1}</b>", icon=folium.Icon(color='red', icon='plus', prefix='fa')).add_to(hosp_group)
        hosp_group.add_to(m)
        
        wash_group = FeatureGroup(name='💧 WASH Points')
        for i in range(8):
            folium.CircleMarker(location=[data['lat'] + np.random.uniform(-0.15, 0.15), data['lon'] + np.random.uniform(-0.15, 0.15)], radius=8, color='blue', fill=True, fill_opacity=0.7, popup=f"<b>Water Point {i+1}</b>").add_to(wash_group)
        wash_group.add_to(m)
        
        school_group = FeatureGroup(name='🏫 Schools')
        for i in range(6):
            folium.RegularPolygonMarker(location=[data['lat'] + np.random.uniform(-0.12, 0.12), data['lon'] + np.random.uniform(-0.12, 0.12)], number_of_sides=4, radius=10, color='green', fill=True, fill_opacity=0.7, popup=f"<b>School {i+1}</b>").add_to(school_group)
        school_group.add_to(m)
        
        market_group = FeatureGroup(name='🛒 Markets')
        for i in range(4):
            folium.RegularPolygonMarker(location=[data['lat'] + np.random.uniform(-0.08, 0.08), data['lon'] + np.random.uniform(-0.08, 0.08)], number_of_sides=3, radius=10, color='orange', fill=True, fill_opacity=0.7, popup=f"<b>Market {i+1}</b>").add_to(market_group)
        market_group.add_to(m)
        
        folium.LayerControl(collapsed=False).add_to(m)
        components.html(m._repr_html_(), height=600, scrolling=False)

# ==============================================================================
# TAB 3: AI, FHIR & USSD
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
    st.caption(L['ussd_subheader'])
    
    if st.button(f"📱 {L['ussd_start']}", use_container_width=True):
        screens = simulate_ussd(region, data, st.session_state.lang)
        st.markdown("### " + L['ussd_session'])
        cols = st.columns(4)
        for i, screen in enumerate(screens):
            with cols[i]:
                st.markdown(f"**Step {screen['step']}: {screen['title']}**")
                st.code(screen['display'], language='text')
                if screen['api_text']:
                    st.markdown(f"*User input: `{screen['api_text']}`*")
        
        st.markdown("---")
        st.subheader(L['network_codes'])
        st.write(L['network_desc'])
        
        col_vod, col_tigo, col_air, col_ttcl = st.columns(4)
        col_vod.metric("Vodacom", "*149*27#")
        col_tigo.metric("Tigo (Yas)", "*150*00*27#")
        col_air.metric("Airtel", "*150*27#")
        col_ttcl.metric("TTCL / Halotel", "*149*27#")
        
        st.markdown("---")
        st.info(L['how_it_works'])

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

2. KEY FINDINGS (20 Core DHIS2 Indicators)
- Communicable: Malaria ({data['mal']}/1k), Cholera ({data['cholera']}), TB ({data['tb']}/100k).
- MNCH: MMR ({data['mmr']}), IMR ({data['imr']}), FIC ({data['fic']}%).
- NCDs: Hypertension ({data['htn']}%), Diabetes ({data['dm']}%).
- Health Systems: Stockout ({data['stockout']}%), OOP ({data['oop']}%).

3. RECOMMENDATIONS (Tailored for {role})
1. Deploy OCV and WASH interventions for Cholera.
2. Distribute LLINs and RDTs for Malaria.
3. Scale up ANC and SBA services to reduce MMR.
4. Integrate NCD screening into community outreach.

4. MONITORING
- Reduce Cholera cases by 20% in 30 days.
- Increase FIC to >{L['fic_target']}% in 6 months.
- Maintain medicine stockout rate below {L['stock_target']}%.

References: {policy_text}, WHO Guidelines, HSSP V, Vision 2050.
"""
    st.text_area(L['preview'], brief, height=400)
    st.download_button(L['download'], brief, file_name=f"Brief_{region}_{country}.txt")
