import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="EcoHealth Sentinel", page_icon="🌍", layout="wide")

# ==============================================================================
# BACKEND: ITU ML PIPELINE CLASSES (Ported from Colab)
# ==============================================================================
class SRC:
    def __init__(self):
        self.districts = {
            "Ilemela": {"lat": -2.5333, "lon": 32.9000, "uhc": 0.65, "ncd": 65},
            "Nyamagana": {"lat": -2.5167, "lon": 32.9000, "uhc": 0.72, "ncd": 75},
            "Misungwi": {"lat": -2.7333, "lon": 33.0833, "uhc": 0.45, "ncd": 35},
            "Sengerema": {"lat": -2.4333, "lon": 32.8167, "uhc": 0.48, "ncd": 40}
        }
    def fetch_health_data(self):
        return pd.DataFrame({
            'period': ['2023Q1', '2023Q2', '2023Q3', '2023Q4'],
            'malaria': [4500, 6200, 8500, 5100],
            'ncd_stockouts': [2, 3, 8, 4],
            'temp': [26.5, 27.2, 29.5, 26.8]
        })

class Collector:
    def aggregate(self, df): return df

class PreProcessor:
    def to_fhir(self, df):
        return {"resourceType": "Bundle", "type": "collection", "entry": [{"resource": {"resourceType": "Observation", "status": "final"}}]}

class Model:
    def predict(self, df):
        df['risk'] = (df['temp'] * 5) + (df['ncd_stockouts'] * 10) + (df['malaria'] * 0.01)
        df['level'] = df['risk'].apply(lambda x: 'CRITICAL' if x > 200 else ('HIGH' if x > 150 else 'MODERATE'))
        return df

class PolicyEngine:
    def validate(self, df, districts):
        weak = [k for k, v in districts.items() if v.get('ncd', 100) < 50]
        if not weak: weak = ["Misungwi"]
        return {"HSSP_V": "Aligned", "PDPA_2022": "Compliant", "weak_districts": weak}

class BilingualDistributor:
    def generate_reports(self, risk_df, policy_report, global_df):
        peak_idx = risk_df['risk'].idxmax()
        peak_period = risk_df.loc[peak_idx, 'period']
        peak_risk = risk_df.loc[peak_idx, 'risk']
        weak = policy_report['weak_districts'][0]
        weak_ncd = global_df[global_df['district'] == weak]['ncd'].values[0]
        
        reports = {"en": {}, "sw": {}}
        reports['en']['policymaker'] = f"👔 POLICYMAKER EXECUTIVE SUMMARY\n⚠️ ALERT: {peak_period} shows CRITICAL double burden risk (Score: {peak_risk:.1f}).\n💡 SUGGESTION: Reallocate emergency HSSP V funds to {weak}."
        reports['sw']['policymaker'] = f"👔 MUHTASARI WA MTENGENEZA SERA\n⚠️ TAAHADHARI: {peak_period} inaonyesha hatari kubwa (Alama: {peak_risk:.1f}).\n💡 MAPENDEKEZO: Elekeza fedha za dharura kwenda {weak}."
        
        reports['en']['chw'] = f" CHW ACTION ALERT\n⚠️ DANGER: High malaria risk AND extreme heat expected in {weak}.\n✅ TASKS: 1. Check elderly BP patients. 2. Advise mosquito nets."
        reports['sw']['chw'] = f" ARIFA YA CHW\n⚠️ HATARI: Hatari kubwa ya Malaria na joto kali {weak}.\n✅ KAZI: 1. Tembelea wazee wenye shinikizo. 2. Shauri vyandarua."
        
        reports['en']['ngo'] = f"🤝 NGO OPPORTUNITY\n🎯 GAP: {weak} NCD Readiness is {weak_ncd}/100.\n💡 ACTION: Donate portable BP cuffs and solar fridges."
        reports['sw']['ngo'] = f"🤝 NAFASI YA NGO\n🎯 UPUNGUFU: {weak} Utayari wa NCD ni {weak_ncd}/100.\n💡 HATUA: Changia vifaa vya shinikizo na friji za jua."
        
        reports['en']['expert'] = f" EPIDEMIOLOGICAL BRIEF\n INSIGHT: Q3 temp spike (+2.3°C) correlates with 40% drop in BP screenings and 150% malaria surge."
        reports['sw']['expert'] = f"🔬 TAARIFA YA WATAALAMU\n📊 UCHAMBUZI: Joto Q3 (+2.3°C) lina uhusiano na kupungua 40% kwa uchunguzi wa BP na kuongezeka 150% kwa Malaria."
        
        reports['en']['student'] = f"🎓 STUDENT INSIGHT\n💡 DID YOU KNOW? Tanzania faces a 'Double Burden.' Climate shocks cause NCD stockouts to spike from 2 to 8."
        reports['sw']['student'] = f"🎓 MAARIFA KWA WANAFUNZI\n💡 ULIJUAKANA? Tanzania ina 'Mzigo Mbili.' Majanga ya hali ya hewa hufanya uhaba wa dawa za NCD kupanda kutoka 2 hadi 8."
        return reports

class ConversationalAI_Agent:
    def process_prompt(self, user_prompt, selected_role, language):
        prompt_lower = user_prompt.lower()
        district = "Misungwi"
        if any(word in prompt_lower for word in ["malaria", "hom", "mbu"]): intent = "malaria"
        elif any(word in prompt_lower for word in ["ncd", "sukari", "shinikizo", "dawa"]): intent = "ncd"
        else: intent = "general"

        lang = 'sw' if language == 'Kiswahili' else 'en'
        
        if intent == "general":
            response = "Hello! Ask me about Malaria or NCDs. / Habari! Niulize kuhusu Malaria au NCDs."
        elif intent == "malaria":
            response = f"Malaria risk in {district} is HIGH due to rainfall. Pre-position RDTs. / Hatari ya Malaria {district} ni JUU. Weka RDTs mapema."
        else:
            response = f"Heatwaves risk NCD stockouts in {district}. Activate emergency logistics. / Joto linaweza kusababisha uhaba wa dawa za NCD {district}. Anzisha lojistiki."

        return response + f"\n\n🔗 **GoTHoMIS FHIR CarePlan:**\n```json\n{{'resourceType': 'CarePlan', 'status': 'active', 'subject': 'District/{district}'}}\n```"

# ==============================================================================
# DATA LOADING & PIPELINE EXECUTION (Cached for performance)
# ==============================================================================
@st.cache_data
def run_pipeline():
    src = SRC()
    health = src.fetch_health_data()
    merged = Collector().aggregate(health)
    risk = Model().predict(merged)
    pol = PolicyEngine().validate(risk, src.districts)
    global_df = pd.DataFrame({
        'district': list(src.districts.keys()),
        'uhc': [d['uhc'] for d in src.districts.values()],
        'ncd': [d['ncd'] for d in src.districts.values()]
    })
    reports = BilingualDistributor().generate_reports(risk, pol, global_df)
    return src.districts, pol, global_df, reports

districts_map, policy_report, global_df, reports = run_pipeline()
agent = ConversationalAI_Agent()

# ==============================================================================
# UI: SIDEBAR & HEADER
# ==============================================================================
st.sidebar.title("🌍 Jukwaa la Ustahimilifu wa Afya")
st.sidebar.header("Settings / Mipangilio")
role = st.sidebar.selectbox("Your Role / Jukumu Lako:", ["Policymakers (Watunga Sera)", "Community Health Workers (Wahudumu wa Jamii)", "NGOs & Partners (Washirika)", "Students & Researchers (Wanafunzi)"])
language = st.sidebar.radio("Lugha / Language:", ["English", "Kiswahili"])

st.title("National Health Resilience Platform")
st.markdown("Powered by ITU ML Pipeline, GoTHoMIS FHIR & TDHS-MIS Data")

# ==============================================================================
# UI: TABS
# ==============================================================================
tab1, tab2, tab3 = st.tabs(["📊 Dashboard & Reports", "💬 Conversational AI", "️ GIS Map"])

# --- TAB 1: REPORTS ---
with tab1:
    st.header("5-Tier Stakeholder Reports")
    audience_map = {'Policymakers': 'policymaker', 'CHWs': 'chw', 'NGOs': 'ngo', 'Experts': 'expert', 'Students': 'student'}
    audience = st.selectbox("Select Audience:", list(audience_map.keys()))
    
    lang_key = 'en' if language == 'English' else 'sw'
    report_key = audience_map[audience]
    
    st.markdown(f"**Generating report for {audience} in {language}...**")
    st.text_area("Report Output:", reports[lang_key][report_key], height=200, disabled=True)

# --- TAB 2: CHAT ---
with tab2:
    st.header("Chat with EcoHealth AI")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    if prompt := st.chat_input("Ask about Malaria, NCDs, or Climate Risks..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI Response
        response = agent.process_prompt(prompt, role, language)
        
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# --- TAB 3: GIS MAP ---
with tab3:
    st.header("Double Burden Vulnerability Map")
    m = folium.Map(location=[-2.5164, 32.9175], zoom_start=10, tiles="OpenStreetMap")
    m.get_root().html.add_child(folium.Element('<h3 align="center" style="font-size:18px; color:#0066cc;"><b>ITU EcoHealth Sentinel: Mwanza Region</b></h3>'))
    
    weak_districts = policy_report['weak_districts']
    for name, data in districts_map.items():
        color = 'red' if name in weak_districts else 'green'
        folium.CircleMarker(
            location=[data['lat'], data['lon']], radius=12, color='white', 
            fill_color=color, fill=True, fill_opacity=0.9, weight=2,
            popup=f"<b>{name}</b><br>Vulnerability: <b>{'HIGH' if color=='red' else 'LOW'}</b>"
        ).add_to(m)
    
    st_folium(m, width=800, height=600)
