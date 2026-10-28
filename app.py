import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium import FeatureGroup
import streamlit.components.v1 as components
import plotly.graph_objects as go
import json
import html
from datetime import datetime
from agents import render_agents_tab, tab_label
from evals import render_harness_panel
from viz import render_bullets, render_heatmap, render_risk_map, render_trend
from rag import get_index, render_policy_library
from outbreak import render_outbreak_tab, banner_lines, tab_label as outbreak_tab_label
from packs import load_pack, context, available_packs, render_country_panel, BANNER
from event_response import render_event_response_tab
from outbreak_trends import render_outbreak_trends_tab

# Minimal, responsive digital-health visual system.
st.markdown("""
<style>
:root {
  --eco-ink: #172b2b;
  --eco-muted: #647777;
  --eco-line: #e3eae8;
  --eco-surface: #f7faf9;
  --eco-accent: #176b5b;
}
.block-container { max-width: 1440px; padding-top: 1.6rem; padding-bottom: 3rem; }
h1, h2, h3 { color: var(--eco-ink); letter-spacing: -0.025em; }
h1 { font-weight: 700; }
[data-testid="stMetric"] {
  background: var(--eco-surface);
  border: 1px solid var(--eco-line);
  padding: 1rem 1.1rem;
  border-radius: 14px;
}
[data-testid="stMetricLabel"] { color: var(--eco-muted); }
[data-testid="stTabs"] button { font-weight: 600; }
[data-testid="stTabs"] button[aria-selected="true"] {
  color: var(--eco-accent);
  border-bottom-color: var(--eco-accent);
}
div[data-testid="stExpander"] {
  border: 1px solid var(--eco-line);
  border-radius: 12px;
  overflow: hidden;
}
.stButton > button, .stDownloadButton > button {
  border-radius: 10px;
  font-weight: 600;
  min-height: 2.6rem;
}
div[data-testid="stAlert"] { border-radius: 12px; }
small, .stCaption { color: var(--eco-muted); }
@media (max-width: 700px) {
  .block-container { padding-left: 1rem; padding-right: 1rem; }
  [data-testid="stMetric"] { padding: .7rem; }
}
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 1. TRANSLATION DICTIONARY (ENGLISH / KISWAHILI)
# ==============================================================================
T = {
    'en': {
        'title': "EcoHealth Sentinel", 'welcome': "Welcome", 'verified': "Verified Professional", 'settings': "⚙️ Settings",
        'country': "Select Country", 'region': "Select Region (Tanzania)", 'role': "Your Role / Jukumu Lako",
        'lang': "Language / Lugha", 'theme': "Theme / Mandhari",
        'tab1': "📊 Executive Dashboard", 'tab2': " Socio-Ecological & Services", 'tab3': "🤖 AI, FHIR & USSD", 'tab4': "📄 Policy Brief",
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
        'ai_header': "AI Agent & Voice Assistant",
        'chat_placeholder': "Ask about health risks in {region}",
        'ussd_header': "📱 EcoHealth USSD Services", 'ussd_subheader': "Access on any mobile phone (No smartphone required)",
        'ussd_start': "View USSD Menu Flow", 'ussd_session': "USSD Session Flow",
        'network_codes': "Network Subscription Shortcodes (Tanzania)",
        'network_desc': "Dial the code below on your respective network to access EcoHealth USSD services:",
        'how_it_works': "**How it works:**\n1. Dial the shortcode for your network.\n2. Navigate the menu using numbers (1, 2, 3...).\n3. Reports are sent directly to the District Medical Officer.\n4. Standard USSD rates apply (approx. 50 TZS per session).",
        'brief_header': "Policy Brief Generator", 'download': " Download Brief", 'preview': "Preview",
        # Roles and themes use fixed codes; only the display labels are translated
        'roles': {'policymaker': "Policymaker", 'chw': "Community Health Worker (CHW)", 'researcher': "Student/Researcher", 'ngo': "NGO Partner"},
        'themes': {'light': "Light Mode", 'dark': "Dark Mode"},
        'green_ai': "♻️ Green AI Impact", 'co2_saved': "CO2 Saved", 'co2_delta': "-99% vs LLMs",
        'premium': "🌟 Premium Subscription", 'premium_desc': "Unlock Advanced AI, Bulk DHIS2 Exports, and Offline CHW Mode.",
        'subscribe': "💳 Subscribe for $1/month", 'logout': "🚪 Log Out", 'login': " Sign In",
        'email': "Email Address", 'password': "Password", 'login_btn': "Log In",
        'new_user': "New to EcoHealth Sentinel?", 'create_account': "Create Account",
        'signup_header': "📝 Create Account", 'full_name': "Full Name", 'organization': "Organization",
        'create_pass': "Create Password", 'confirm_pass': "Confirm Password",
        'signup_btn': "Sign Up & Send Verification", 'back_login': "Back to Login",
        'verify_header': "📧 Verify Email", 'code_sent': "Code sent to", 'enter_code': "Enter 6-digit code",
        'verify_btn': "Verify Account", 'invalid_code': "Invalid code. Try 123456.", 'pass_error': "Passwords do not match or too short.",
        'orgs': ["Ministry of Health", "NGO", "Research Institute", "Community Health Worker", "Other"],
        'alert_malaria': " **Alert for {region}:** High risk detected. Malaria: {mal}/1k, Cholera: {cholera} cases. Recommend immediate WASH intervention and LLIN distribution.",
        'alert_vaccine': "💉 **Immunization in {region}:** FIC is at {fic}%. Below target. Recommend mop-up campaigns in rural wards.",
        'summary': "📊 **Summary for {region}:** MMR is {mmr}. Hypertension is {htn}%. Poverty index is {poverty}%.",
        'fhir_title': "GoTHoMIS FHIR Payload",
        # Demo labels
        'demo_banner': "DEMO VERSION: All figures, map points, and the assistant are illustrative samples, not live DHIS2 data. Do not use for clinical or policy decisions.",
        'demo_login': "Demo login: any email and password is accepted.",
        'demo_verify': "Demo only: no email is sent. Use code 123456.",
        'demo_premium': "Coming soon: premium features are not yet available.",
        'demo_green': "Illustrative estimate, not measured.",
        'demo_map': "Sample markers only, not real facility locations.",
        'demo_ai': "Rule based demo assistant, not a clinical AI.",
        'demo_ussd': "Demo only: these shortcodes are not live. Do not dial them.",
        'demo_brief': "Illustrative data. Verify with official DHIS2 figures before sharing.",
        'demo_tag': "DEMO DRAFT, ILLUSTRATIVE DATA",
    },
    'sw': {
        'title': "EcoHealth Sentinel", 'welcome': "Karibu", 'verified': "Mtaalamu Aliyethibitishwa", 'settings': "⚙️ Mipangilio",
        'country': "Chagua Nchi", 'region': "Chagua Mkoa (Tanzania)", 'role': "Jukumu Lako / Your Role",
        'lang': "Lugha / Language", 'theme': "Mandhari / Theme",
        'tab1': "📊 Dashibodi Kuu", 'tab2': "🌍 Jamii na Huduma", 'tab3': "🤖 AI, FHIR na USSD", 'tab4': "📄 Hati ya Sera",
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
        'ai_header': "Wakala wa AI na Msaidizi wa Sauti",
        'chat_placeholder': "Uliza kuhusu hatari za afya katika {region}",
        'ussd_header': "📱 Huduma za USSD za EcoHealth", 'ussd_subheader': "Tumia simu yoyote (Haitajani smartphone)",
        'ussd_start': "Tazama Mtiririko wa Menyu ya USSD", 'ussd_session': "Mtiririko wa USSD",
        'network_codes': "Namba za Ufupishi za Mitandao (Tanzania)",
        'network_desc': "Piga namba hizi kwenye mtandao wako kufikia huduma za USSD za EcoHealth:",
        'how_it_works': "**Jinsi inavyofanya kazi:**\n1. Piga namba ya ufupishi ya mtandao wako.\n2. Tumia namba (1, 2, 3...) kusogeza menyu.\n3. Ripoti zinatumwa moja kwa moja kwa Mganga Mkuu wa Wilaya.\n4. Gharama za kawaida za USSD zinatumika (takriban 50 TZS).",
        'brief_header': "Kizalishaji cha Hati ya Sera", 'download': "📥 Pakua Hati", 'preview': "Hakiki",
        'roles': {'policymaker': "Mtunga Sera", 'chw': "Mhudumu wa Afya wa Jamii (CHW)", 'researcher': "Mwanafunzi/Mtafiti", 'ngo': "Mshirika wa NGO"},
        'themes': {'light': "Hali ya Mwanga", 'dark': "Hali ya Giza"},
        'green_ai': "♻️ Athari ya AI ya Kijani", 'co2_saved': "CO2 Iliyookolewa", 'co2_delta': "-99% ikilinganishwa na LLM",
        'premium': "🌟 Uanachama wa Premium", 'premium_desc': "Fungua AI ya Hali ya Juu, Usafirishaji wa DHIS2, na Hali ya Nje ya Mtandao.",
        'subscribe': "💳 Jiandikishe kwa $1/mwezi", 'logout': " Toka", 'login': "👤 Ingia",
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
        # Demo labels
        'demo_banner': "TOLEO LA MAJARIBIO: Takwimu zote, alama za ramani, na msaidizi ni mifano ya kuonyesha, si data hai ya DHIS2. Usitumie kwa maamuzi ya kitabibu au ya sera.",
        'demo_login': "Kuingia kwa majaribio: barua pepe na nenosiri lolote vinakubaliwa.",
        'demo_verify': "Majaribio tu: hakuna barua pepe inayotumwa. Tumia msimbo 123456.",
        'demo_premium': "Inakuja hivi karibuni: huduma za premium bado hazipatikani.",
        'demo_green': "Makadirio ya mfano, hayajapimwa.",
        'demo_map': "Alama za mfano tu, si maeneo halisi ya vituo.",
        'demo_ai': "Msaidizi wa majaribio unaotumia kanuni, si AI ya kitabibu.",
        'demo_ussd': "Majaribio tu: namba hizi hazifanyi kazi. Usizipige.",
        'demo_brief': "Data ya mfano. Thibitisha na takwimu rasmi za DHIS2 kabla ya kushiriki.",
        'demo_tag': "DRAFTI YA MAJARIBIO, DATA YA MFANO",
    }
}

ROLE_CODES = ['policymaker', 'chw', 'researcher', 'ngo']
THEME_CODES = ['light', 'dark']
LANG_CODES = ['en', 'sw']
LANG_LABELS = {'en': "English", 'sw': "Kiswahili"}

# ==============================================================================
# 2. SAFE UI & THEME CSS (Prevents Icon Smudging)
# ==============================================================================
st.set_page_config(page_title="EcoHealth Sentinel: Tanzania & EAC", layout="wide", initial_sidebar_state="expanded")

# Widget keys 'lang' and 'theme' hold fixed codes, so choices survive language changes
if 'theme' not in st.session_state: st.session_state.theme = 'light'
if 'lang' not in st.session_state: st.session_state.lang = 'en'

def get_theme_css(theme):
    if theme == 'dark':
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Times+New+Roman&display=swap');
        
        /* Only apply font to text elements, NOT icons or layout divs */
        h1, h2, h3, h4, p, label, button, 
        [data-testid="stMetricLabel"], 
        [data-testid="stMetricValue"], 
        [data-testid="stMetricDelta"],
        .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
            font-family: 'Times New Roman', Times, serif !important;
        }
        
        .stApp { background-color: #0e1117; color: #fafafa; }
        .stSidebar { background-color: #1a1d24; }
        
        [data-testid="stMetric"] {
            background-color: #262730; padding: 15px; border-radius: 8px; 
            border-left: 5px solid #4da6ff; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        [data-testid="stMetricLabel"], [data-testid="stMetricValue"], [data-testid="stMetricDelta"] { 
            color: #fafafa !important; 
        }
        
        button[data-baseweb="tab"] { font-size: 14px !important; font-weight: bold !important; }
        .stTabs [data-baseweb="tab-list"] { background-color: #1a1d24; }
        .stTextInput > div > div > input, .stSelectbox > div > div > div, .stRadio > label { color: #fafafa !important; }
        </style>
        """
    else:
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Times+New+Roman&display=swap');
        
        /* Only apply font to text elements, NOT icons or layout divs */
        h1, h2, h3, h4, p, label, button, 
        [data-testid="stMetricLabel"], 
        [data-testid="stMetricValue"], 
        [data-testid="stMetricDelta"],
        .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
            font-family: 'Times New Roman', Times, serif !important;
        }
        
        [data-testid="stMetric"] {
            background-color: #f8f9fa; padding: 15px; border-radius: 8px; 
            border-left: 5px solid #0066cc; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        button[data-baseweb="tab"] { font-size: 14px !important; font-weight: bold !important; }
        </style>
        """

st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)

# ==============================================================================
# 3. DATA STRUCTURES (ALL 20 DHIS2 INDICATORS) - ILLUSTRATIVE SAMPLE DATA
# ==============================================================================
# Tanzania and Kenya data now live in pack_tz.json and pack_ke.json (country packs)

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
# 4b. READ ALOUD HELPER (one place instead of two copies)
# ==============================================================================
def render_read_aloud(content):
    """Render browser-native speech controls in an isolated Streamlit HTML component."""
    import hashlib
    import json

    # Stable, safe identifier; Python's built-in hash changes between processes.
    msg_id = "msg_" + hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]
    plain_text = content.replace("**", "").replace("```json", "").replace("```", " ")
    plain_text = " ".join(plain_text.split())
    safe_text = json.dumps(plain_text, ensure_ascii=False)
    lang_code = "sw-TZ" if st.session_state.lang == "sw" else "en-US"

    html = f"""
    <div style="font-family: Arial, sans-serif; display:flex; gap:8px; align-items:center;">
      <button id="play_{msg_id}" type="button"
        style="background:#0066cc;color:white;border:0;border-radius:6px;padding:8px 14px;cursor:pointer;">
        🔊 Read Aloud
      </button>
      <button id="stop_{msg_id}" type="button"
        style="background:#e74c3c;color:white;border:0;border-radius:6px;padding:8px 14px;cursor:pointer;">
        ⏹ Stop
      </button>
      <span id="status_{msg_id}" role="status" aria-live="polite"
        style="font-size:12px;color:#555;"></span>
    </div>
    <script>
      (() => {{
        const text = {safe_text};
        const play = document.getElementById("play_{msg_id}");
        const stop = document.getElementById("stop_{msg_id}");
        const status = document.getElementById("status_{msg_id}");
        const lang = {json.dumps(lang_code)};

        play.addEventListener("click", () => {{
          if (!("speechSynthesis" in window) || !("SpeechSynthesisUtterance" in window)) {{
            status.textContent = "Read Aloud is not supported in this browser.";
            return;
          }}
          window.speechSynthesis.cancel();
          const utterance = new SpeechSynthesisUtterance(text);
          utterance.lang = lang;
          utterance.rate = 0.9;
          utterance.pitch = 1.0;
          utterance.volume = 1.0;
          utterance.onstart = () => {{ status.textContent = "Playing…"; }};
          utterance.onend = () => {{ status.textContent = "Finished."; }};
          utterance.onerror = (event) => {{
            status.textContent = event.error === "canceled" ? "" : "Audio could not play. Check browser sound and voice settings.";
          }};
          window.speechSynthesis.speak(utterance);
        }});

        stop.addEventListener("click", () => {{
          if ("speechSynthesis" in window) window.speechSynthesis.cancel();
          status.textContent = "Stopped.";
        }});
      }})();
    </script>
    """
    components.html(html, height=54, scrolling=False)

# ==============================================================================
# 5. AUTHENTICATION SYSTEM (DEMO ONLY)
# ==============================================================================
if 'user' not in st.session_state: st.session_state.user = None
if 'auth_step' not in st.session_state: st.session_state.auth_step = 'login'

L = T[st.session_state.lang]
st.sidebar.title(f"🌍 {L['title']}")

if st.session_state.user is None:
    if st.session_state.auth_step == 'login':
        st.sidebar.header(L['login'])
        st.sidebar.caption(f"🧪 {L['demo_login']}")
        email = st.sidebar.text_input(L['email'], placeholder="name@hospital.go.tz", key="login_email")
        password = st.sidebar.text_input(L['password'], type="password", key="login_password")
        if st.sidebar.button(L['login_btn'], use_container_width=True) and email and password:
            st.session_state.user = {"email": email, "name": email.split('@')[0].capitalize(), "role": L['verified'], "org": "Ministry of Health"}
            st.rerun()
        st.sidebar.markdown("---")
        st.sidebar.write(L['new_user'])
        if st.sidebar.button(L['create_account'], use_container_width=True):
            st.session_state.auth_step = 'signup'; st.rerun()
    elif st.session_state.auth_step == 'signup':
        st.sidebar.header(L['signup_header'])
        name = st.sidebar.text_input(L['full_name'], key="signup_name")
        email = st.sidebar.text_input(L['email'], key="signup_email")
        org_index = st.sidebar.selectbox(L['organization'], range(len(L['orgs'])), format_func=lambda i: L['orgs'][i], key="signup_org")
        org = L['orgs'][org_index]
        password = st.sidebar.text_input(L['create_pass'], type="password", key="signup_password")
        confirm = st.sidebar.text_input(L['confirm_pass'], type="password", key="signup_confirm")
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
        st.sidebar.caption(f"🧪 {L['demo_verify']}")
        code = st.sidebar.text_input(L['enter_code'], placeholder="123456", key="verify_code")
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
    st.sidebar.caption(f"🧪 {L['demo_premium']}")
    st.sidebar.link_button(L['subscribe'], "https://buymeacoffee.com/ecohealth", use_container_width=True)
    st.sidebar.markdown("---")
    st.sidebar.subheader(L['green_ai'])
    st.sidebar.metric(L['co2_saved'], "0.045 kg/prediction", delta=L['co2_delta'])
    st.sidebar.caption(f"🧪 {L['demo_green']}")
    st.sidebar.caption("Lightweight heuristic models used instead of energy-intensive LLMs. Compliant with Sustainable AI principles (Ueda et al., 2024).")
    st.sidebar.markdown("---")
    if st.sidebar.button(L['logout'], use_container_width=True): 
        st.session_state.user = None; st.session_state.auth_step = 'login'; st.rerun()

# ==============================================================================
# 6. APP SETTINGS (fixed codes + widget keys fix the Kiswahili crash and theme loop)
# ==============================================================================
st.sidebar.header(L['settings'])
st.sidebar.radio(L['lang'], LANG_CODES, format_func=lambda c: LANG_LABELS[c], key='lang')
st.sidebar.radio(L['theme'], THEME_CODES, format_func=lambda c: L['themes'][c], key='theme')

PACK_BY_NAME = {name: load_pack(code) for code, name in available_packs()}
LEGACY = [c for c in EAC_NATIONAL if c not in PACK_BY_NAME]
country = st.sidebar.selectbox(L['country'], list(PACK_BY_NAME) + LEGACY, key='country')
pack = PACK_BY_NAME.get(country)
TARGET_KEYS = {'mal_target': 'mal', 'pos_target': 'mal_pos', 'chol_target': 'cholera', 'tb_target': 'tb', 'llin_target': 'llin',
               'mmr_target': 'mmr', 'imr_target': 'imr', 'anc_target': 'anc4', 'sba_target': 'sba', 'sam_target': 'sam',
               'fic_target': 'fic', 'drop_target': 'penta_drop', 'htn_target': 'htn', 'dm_target': 'dm', 'cerv_target': 'cervical',
               'tob_target': 'tobacco', 'stock_target': 'stockout', 'hw_target': 'hw', 'oop_target': 'oop'}
if pack:
    ctx = context(pack)
    _idx = get_index(pack['code'])
    if _idx is not None:
        ctx = {**ctx, 'index': _idx}
    _pend = st.session_state.pop('_pending_region', None)
    if _pend in pack['regions']:
        st.session_state[f"region_{pack['code']}"] = _pend
    region = st.sidebar.selectbox(pack['region_label'][st.session_state.lang], list(pack['regions']), key=f"region_{pack['code']}")
    data = pack['regions'][region]
    policy_text = pack['policy_text'][st.session_state.lang]
    eval_regions = pack['regions']
    refs = ", ".join(pack['references'])
    L = dict(L)
    for tk, ik in TARGET_KEYS.items():
        L[tk] = pack['targets'][ik][0]
else:
    ctx = None
    region = "National Overview"
    data = EAC_NATIONAL[country]
    policy_text = "National Health Strategy & EAC Protocol (no country pack yet)"
    eval_regions = {region: data}
    refs = "WHO Guidelines"

role = st.sidebar.selectbox(L['role'], ROLE_CODES, format_func=lambda c: L['roles'][c], key='role')
role_label = L['roles'][role]

logo_path = "assets/ecohealth-sentinel-logo.svg"
try:
    with open(logo_path, "rb") as logo_file:
        st.image(logo_file.read(), use_container_width=True)
except OSError:
    st.markdown("## EcoHealth Sentinel")

st.title(f"{L['title']}: {region}, {country}")
st.warning(f"🧪 {L['demo_banner']}")
if pack and pack.get('data_status') == 'placeholder':
    st.error(f"🚧 {BANNER[st.session_state.lang]}")
if pack:
    for _line in banner_lines(pack, region, st.session_state.lang, st.session_state)[:2]:
        st.error(f"🛰️ {_line}")
st.info(f"🛡️ {policy_text}")

role_messages = {
    'en': {'policymaker': "👔 Viewing as Policymaker: Focus on KPIs, funding gaps, and population-level trends.", 'chw': "📱 Viewing as CHW: Focus on actionable tasks, USSD alerts, and community-level data.", 'researcher': "🎓 Viewing as Researcher: Focus on raw data, correlations, and downloadable datasets.", 'ngo': " Viewing as NGO: Focus on funding gaps, partnership opportunities, and impact metrics."},
    'sw': {'policymaker': "👔 Unatazama kama Mtunga Sera: Lengo ni viashiria vya msingi, mapungufu ya fedha, na mwenendo.", 'chw': "📱 Unatazama kama CHW: Lengo ni kazi zinazofanyika, tahadhari za USSD, na data ya jamii.", 'researcher': " Unatazama kama Mtafiti: Lengo ni data ghafi, uhusiano, na datasets zinazopakuliwa.", 'ngo': "🤝 Unatazama kama NGO: Lengo ni mapungufu ya ufadhili, fursa za ushirikiano, na viashiria vya athari."}
}
st.success(role_messages[st.session_state.lang][role])

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([L['tab1'], L['tab2'], L['tab3'], L['tab4'], tab_label(st.session_state.lang), outbreak_tab_label(st.session_state.lang), "🚨 Event & Response" if st.session_state.lang == "en" else "🚨 Matukio na Majibu", "📈 Outbreak Trends" if st.session_state.lang == "en" else "📈 Mwenendo wa Milipuko"])

# ==============================================================================
# TAB 1: EXECUTIVE DASHBOARD (CLEAN LAYOUT)
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
        row1 = st.columns(3)
        row1[0].metric(L['malaria'], data['mal'], help=f"Target: <{L['mal_target']}")
        row1[1].metric(L['mal_pos'], f"{data['mal_pos']}%", help=f"Target: <{L['pos_target']}%")
        row1[2].metric(L['cholera'], data['cholera'], help=f"Target: {L['chol_target']}")
        
        row2 = st.columns(2)
        row2[0].metric(L['tb'], data['tb'], help=f"Target: <{L['tb_target']}")
        row2[1].metric(L['llin'], f"{data['llin']}%", help=f"Target: >{L['llin_target']}%")

    # Category 2: MNCH & Immunization (3 per row)
    with st.expander(L['cat_mnch'], expanded=True):
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
        row1 = st.columns(2)
        row1[0].metric(L['htn'], f"{data['htn']}%", help=f"Target: >{L['htn_target']}%")
        row1[1].metric(L['dm'], f"{data['dm']}%", help=f"Target: >{L['dm_target']}%")
        
        row2 = st.columns(2)
        row2[0].metric(L['cervical'], f"{data['cervical']}%", help=f"Target: >{L['cerv_target']}%")
        row2[1].metric(L['tobacco'], f"{data['tobacco']}%", help=f"Target: <{L['tob_target']}%")

    # Category 4: Health Systems & UHC (3 per row)
    with st.expander(L['cat_sys'], expanded=True):
        row1 = st.columns(3)
        row1[0].metric(L['stockout'], f"{data['stockout']}%", help=f"Target: <{L['stock_target']}%")
        row1[1].metric(L['hw'], data['hw'], help=f"Target: >{L['hw_target']}")
        row1[2].metric(L['oop'], f"{data['oop']}%", help=f"Target: <{L['oop_target']}%")

    st.markdown("---")
    
    # Comprehensive Visualization: Target vs Actual
    st.subheader(L['target_chart'])
    render_bullets(L, st.session_state.lang, region, data, ctx, st.session_state.theme)
    st.markdown("---")
    render_heatmap(L, st.session_state.lang, eval_regions, ctx, region, st.session_state.theme)
    st.markdown("---")
    render_trend(L, st.session_state.lang, pack, ctx, region, data, st.session_state.theme)

# ==============================================================================
# TAB 2: SOCIO-ECOLOGICAL & SERVICES MAP
# ==============================================================================
with tab2:
    st.header("🌍 Socio-Ecological Determinants & Social Services")
    render_risk_map(L, st.session_state.lang, pack, eval_regions, ctx, region, st.session_state.theme)
    st.markdown("---")
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
        st.caption(f"🧪 {L['demo_map']}")
        zoom_level = 9 if pack else 6
        
        m = folium.Map(location=[data['lat'], data['lon']], zoom_start=zoom_level, tiles="OpenStreetMap")
        
        hosp_group = FeatureGroup(name=' Health Facilities')
        for i in range(5):
            folium.Marker(location=[data['lat'] + np.random.uniform(-0.1, 0.1), data['lon'] + np.random.uniform(-0.1, 0.1)], popup=f"<b>Sample Health Facility {i+1}</b>", icon=folium.Icon(color='red', icon='plus', prefix='fa')).add_to(hosp_group)
        hosp_group.add_to(m)
        
        wash_group = FeatureGroup(name='💧 WASH Points')
        for i in range(8):
            folium.CircleMarker(location=[data['lat'] + np.random.uniform(-0.15, 0.15), data['lon'] + np.random.uniform(-0.15, 0.15)], radius=8, color='blue', fill=True, fill_opacity=0.7, popup=f"<b>Sample Water Point {i+1}</b>").add_to(wash_group)
        wash_group.add_to(m)
        
        school_group = FeatureGroup(name='🏫 Schools')
        for i in range(6):
            folium.RegularPolygonMarker(location=[data['lat'] + np.random.uniform(-0.12, 0.12), data['lon'] + np.random.uniform(-0.12, 0.12)], number_of_sides=4, radius=10, color='green', fill=True, fill_opacity=0.7, popup=f"<b>Sample School {i+1}</b>").add_to(school_group)
        school_group.add_to(m)
        
        market_group = FeatureGroup(name=' Markets')
        for i in range(4):
            folium.RegularPolygonMarker(location=[data['lat'] + np.random.uniform(-0.08, 0.08), data['lon'] + np.random.uniform(-0.08, 0.08)], number_of_sides=3, radius=10, color='orange', fill=True, fill_opacity=0.7, popup=f"<b>Sample Market {i+1}</b>").add_to(market_group)
        market_group.add_to(m)
        
        folium.LayerControl(collapsed=False).add_to(m)
        components.html(m._repr_html_(), height=600, scrolling=False)

    
    st.markdown("---")
    st.subheader("Health Facility Registry | Import & Preview")
    st.caption(
        "Import an authorized Ministry of Health Master Facility List or another permitted "
        "facility dataset. The HFR screenshots shared during development are visual references, "
        "not a downloadable dataset; their values are not treated as verified live data."
    )
    facility_file = st.file_uploader(
        "Upload facility list (CSV or Excel)",
        type=["csv", "xlsx"],
        key="eco_facility_registry_upload",
        help="Use a file you are authorized to access. Avoid patient-level or otherwise sensitive data."
    )
    if facility_file is not None:
        try:
            if facility_file.name.lower().endswith(".csv"):
                facility_df = pd.read_csv(facility_file)
            else:
                facility_df = pd.read_excel(facility_file)
            facility_df.columns = [str(col).strip() for col in facility_df.columns]
            st.success(f"Loaded {len(facility_df):,} rows and {len(facility_df.columns)} columns.")
            st.dataframe(facility_df.head(100), use_container_width=True, hide_index=True)
            st.caption("Preview limited to the first 100 rows. Original source values are not modified.")

            lower_columns = {str(col).strip().lower(): col for col in facility_df.columns}
            type_candidates = ["facility_type", "facility type", "type", "facility_level", "level"]
            type_col = next((lower_columns[name] for name in type_candidates if name in lower_columns), None)
            name_candidates = ["facility_name", "facility name", "name", "facility"]
            name_col = next((lower_columns[name] for name in name_candidates if name in lower_columns), None)
            lat_candidates = ["latitude", "lat", "y"]
            lon_candidates = ["longitude", "lon", "lng", "long", "x"]
            lat_col = next((lower_columns[name] for name in lat_candidates if name in lower_columns), None)
            lon_col = next((lower_columns[name] for name in lon_candidates if name in lower_columns), None)

            m1, m2, m3 = st.columns(3)
            m1.metric("Rows loaded", f"{len(facility_df):,}")
            m2.metric("Facility types", str(facility_df[type_col].nunique()) if type_col else "Not detected")
            m3.metric("Coordinate fields", "Detected" if lat_col and lon_col else "Not detected")

            if type_col:
                type_counts = (
                    facility_df[type_col].fillna("Unknown").astype(str)
                    .value_counts().rename_axis("Facility type").reset_index(name="Records")
                )
                st.markdown("**Records by facility type**")
                st.bar_chart(type_counts.set_index("Facility type"))
            else:
                st.info("Facility type column not detected automatically. Review the column names before analysis.")

            if lat_col and lon_col:
                st.info(
                    "Coordinate columns were detected by name only. Validate their coordinate reference system, "
                    "units, and values before mapping."
                )
                try:
                    points = facility_df[[lat_col, lon_col]].copy()
                    points[lat_col] = pd.to_numeric(points[lat_col], errors="coerce")
                    points[lon_col] = pd.to_numeric(points[lon_col], errors="coerce")
                    valid = points[
                        points[lat_col].between(-90, 90) & points[lon_col].between(-180, 180)
                    ].dropna()
                    st.caption(f"Rows with numeric coordinates in geographic ranges: {len(valid):,} of {len(facility_df):,}")
                    if not valid.empty:
                        st.map(valid.rename(columns={lat_col: "latitude", lon_col: "longitude"}))
                except Exception as map_error:
                    st.warning(f"Could not prepare a coordinate preview: {map_error}")
            else:
                st.warning(
                    "No obvious latitude/longitude columns were detected. This file can be inspected, "
                    "but it cannot be mapped as points until valid coordinates or spatial geometry are available."
                )
            st.download_button(
                "Download unchanged copy as CSV",
                data=facility_df.to_csv(index=False).encode("utf-8"),
                file_name="ecohealth_facility_list_preview.csv",
                mime="text/csv",
            )
        except Exception as facility_error:
            st.error(f"Could not read this file: {facility_error}")
            st.caption("Check that the file is a valid CSV or Excel workbook.")

# ==============================================================================
# TAB 3: AI, FHIR & USSD
# ==============================================================================
with tab3:
    st.header(L['ai_header'])
    st.caption(f"🧪 {L['demo_ai']}")
    
    # Initialize chat history
    if "messages" not in st.session_state: 
        st.session_state.messages = []
    
    # Display chat messages with Read Aloud buttons
    for message in st.session_state.messages:
        with st.chat_message(message["role"]): 
            st.markdown(message["content"])
            if message["role"] == "assistant":
                render_read_aloud(message["content"])
    
    # Voice Input Instructions
    st.info("""
    ### 🎙️ **Voice Input**
    **To speak your question:** 
    1. Click the microphone icon 🎙️ on your keyboard (next to spacebar on mobile, or in the chat input on desktop)
    2. Speak your question in **English** or **Kiswahili**
    3. Press Enter to send
    
    **To hear the response:** Click the **🔊 Read Aloud** button below any AI message.
    """)
    
    # Chat input
    prompt = st.chat_input(L['chat_placeholder'].format(region=region))
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): 
            st.markdown(prompt)
        
        # AI Logic (keyword rules, not a trained model)
        if "malaria" in prompt.lower() or "cholera" in prompt.lower():
            response = L['alert_malaria'].format(region=region, mal=data['mal'], cholera=data['cholera'])
        elif "vaccine" in prompt.lower() or "fic" in prompt.lower():
            response = L['alert_vaccine'].format(region=region, fic=data['fic'])
        else:
            response = L['summary'].format(region=region, mmr=data['mmr'], htn=data['htn'], poverty=data['poverty'])
        
        fhir_payload = {"resourceType": "Bundle", "type": "transaction", "entry": [{"resource": {"resourceType": "CarePlan", "status": "active", "intent": "plan", "title": f"Intervention for {region}", "subject": {"reference": f"Location/TZ-{region}"}}}]}
        full_response = f"{response}\n\n**{L['fhir_title']}:**\n```json\n{json.dumps(fhir_payload, indent=2)}\n```"
        
        with st.chat_message("assistant"): 
            st.markdown(full_response)
            render_read_aloud(full_response)
            
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    st.markdown("---")
    
    # USSD DEMO SECTION
    st.subheader(L['ussd_header'])
    st.caption(L['ussd_subheader'])
    st.caption(f"🧪 {L['demo_ussd']}")
    
    if st.button(f" {L['ussd_start']}", use_container_width=True):
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
        st.warning(f"🧪 {L['demo_ussd']}")
        
        nets = (pack or {}).get('ussd', [])
        if nets:
            for col, n in zip(st.columns(len(nets)), nets):
                col.metric(n['network'], n['code'])
        else:
            st.info("No country pack yet: USSD shortcodes are not configured.")
        
        st.markdown("---")
        st.info(L['how_it_works'])

# ==============================================================================
# TAB 4: POLICY BRIEF
# ==============================================================================
with tab4:
    st.header(L['brief_header'])
    st.caption(f"🧪 {L['demo_brief']}")
    brief = f"""
*** {T['en']['demo_tag']} ***

POLICY BRIEF: EcoHealth Sentinel
Region: {region}, {country}
Role Focus: {role_label}
Date: {datetime.now().strftime('%B %d, %Y')}

1. EXECUTIVE SUMMARY
{region} faces a double burden of disease. Malaria incidence is {data['mal']} per 1,000, and Cholera cases are at {data['cholera']}. Maternal Mortality is {data['mmr']} per 100,000. Immediate action is required.

2. KEY FINDINGS (20 Core DHIS2 Indicators)
- Communicable: Malaria ({data['mal']}/1k), Cholera ({data['cholera']}), TB ({data['tb']}/100k).
- MNCH: MMR ({data['mmr']}), IMR ({data['imr']}), FIC ({data['fic']}%).
- NCDs: Hypertension ({data['htn']}%), Diabetes ({data['dm']}%).
- Health Systems: Stockout ({data['stockout']}%), OOP ({data['oop']}%).

3. RECOMMENDATIONS (Tailored for {role_label})
1. Deploy OCV and WASH interventions for Cholera.
2. Distribute LLINs and RDTs for Malaria.
3. Scale up ANC and SBA services to reduce MMR.
4. Integrate NCD screening into community outreach.

4. MONITORING
- Reduce Cholera cases by 20% in 30 days.
- Increase FIC to >{L['fic_target']}% in 6 months.
- Maintain medicine stockout rate below {L['stock_target']}%.

References: {policy_text}, {refs}.

NOTE: All figures above are illustrative samples. Verify with official DHIS2 data before sharing.
"""
    st.text_area(L['preview'], brief, height=400)
    st.download_button(L['download'], brief, file_name=f"Brief_{region}_{country}.txt")

# ==============================================================================
# TAB 5: AGENTS AND ITU Y.3172 PIPELINE
# ==============================================================================
with tab5:
    render_agents_tab(st.session_state.lang, region, data)
    st.markdown("---")
    
    # Build the evaluation set from the available country packs and EAC demo entries.
    # The selected country's eval_regions is already defined above; this adds all pack regions
    # without relying on the undefined legacy TANZANIA_REGIONS constant.
    all_pack_regions = {
        region_name: region_data
        for pack_code, _pack_name in available_packs()
        for region_name, region_data in load_pack(pack_code).get('regions', {}).items()
    }
    eval_regions = {**all_pack_regions, **EAC_NATIONAL}
    render_harness_panel(st.session_state.lang, region, eval_regions)
# ==============================================================================
# TAB 6: OUTBREAK WATCH (threat board, signal triage, readiness, countdown, climate)
# ==============================================================================
with tab6:
    render_outbreak_tab(st.session_state.lang, pack, region, eval_regions, ctx)

# ==============================================================================
# TAB 7: EVENT & RESPONSE MANAGEMENT (synthetic sandbox; not connected to live systems)
# ==============================================================================
with tab7:
    render_event_response_tab(st.session_state.lang, region)

# ==============================================================================
# TAB 8: OUTBREAK TREND MONITORING (no automated alerts; provenance required)
# ==============================================================================
with tab8:
    render_outbreak_trends_tab(st.session_state.lang)
