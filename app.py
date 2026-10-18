import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="EcoHealth Sentinel: Tanzania", page_icon="🇿", layout="wide")

# ==============================================================================
# 1. COMPREHENSIVE DATA STORE (UHC, PHC, NCDs, Nutrition, Climate)
# ==============================================================================
REGIONS_DATA = {
    "National Average": {"lat": -6.3690, "lon": 34.8888, "mmr": 104, "malaria_inc": 128, "htn_prev": 24.5, "dm_prev": 2.1, "pm25": 18, "stunting": 26.0, "obesity": 8.5, "inactivity": 22.0, "oop_exp": 28.0, "hw_density": 0.15},
    "Dar es Salaam": {"lat": -6.7924, "lon": 39.2083, "mmr": 85, "malaria_inc": 15, "htn_prev": 31.2, "dm_prev": 3.8, "pm25": 42, "stunting": 12.0, "obesity": 14.5, "inactivity": 35.0, "oop_exp": 32.0, "hw_density": 0.25},
    "Dodoma": {"lat": -6.1630, "lon": 35.7516, "mmr": 115, "malaria_inc": 45, "htn_prev": 22.0, "dm_prev": 1.9, "pm25": 22, "stunting": 32.0, "obesity": 6.0, "inactivity": 18.0, "oop_exp": 35.0, "hw_density": 0.10},
    "Mwanza": {"lat": -2.5164, "lon": 32.9175, "mmr": 130, "malaria_inc": 210, "htn_prev": 20.5, "dm_prev": 1.5, "pm25": 15, "stunting": 28.0, "obesity": 5.5, "inactivity": 15.0, "oop_exp": 30.0, "hw_density": 0.12},
    "Arusha": {"lat": -3.3869, "lon": 36.6830, "mmr": 95, "malaria_inc": 35, "htn_prev": 26.0, "dm_prev": 2.5, "pm25": 19, "stunting": 21.0, "obesity": 9.0, "inactivity": 20.0, "oop_exp": 29.0, "hw_density": 0.18},
    "Zanzibar": {"lat": -6.1659, "lon": 39.2022, "mmr": 78, "malaria_inc": 8, "htn_prev": 28.0, "dm_prev": 3.2, "pm25": 14, "stunting": 15.0, "obesity": 11.0, "inactivity": 25.0, "oop_exp": 25.0, "hw_density": 0.20}
}

DHIS2_INDICATORS = {
    "mmr": {"name": "Maternal Mortality (per 100k)", "value": 104, "target": 70},
    "htn_prev": {"name": "Hypertension Prevalence", "value": 24.5, "target": 15},
    "stunting": {"name": "Child Stunting (Under 5)", "value": 26.0, "target": 15}, # Nutrition
    "obesity": {"name": "Adult Obesity (BMI >30)", "value": 8.5, "target": 5}, # Nutrition
    "inactivity": {"name": "Physical Inactivity (Adults)", "value": 22.0, "target": 10}, # Physio/WHO
    "oop_exp": {"name": "Out-of-Pocket Health Expenditure (%)", "value": 28.0, "target": 15}, # UHC Financial Protection
    "hw_density": {"name": "Health Worker Density (per 1000)", "value": 0.15, "target": 0.45} # PHC Equity
}

TREND_DATA = pd.DataFrame({
    'Year': [2019, 2020, 2021, 2022, 2023],
    'Stunting (%)': [30, 29, 28, 27, 26],
    'Obesity (%)': [6.5, 7.0, 7.5, 8.0, 8.5],
    'Physical Inactivity (%)': [19, 20, 20.5, 21.5, 22.0],
    'Out-of-Pocket Exp (%)': [32, 31, 30, 29, 28]
})

# ==============================================================================
# 2. SMART AI AGENT (Holistic PHC, Nutrition & Physio Focus)
# ==============================================================================
class SmartEcoHealthAgent:
    def __init__(self):
        self.context_db = {
            "physio_activity": {
                "en": f"🏃‍♂️ **Physical Activity & Rehab (WHO GAPPA):** Physical inactivity is at **{DHIS2_INDICATORS['inactivity']['value']}%** nationally, exceeding the 10% target. \n\n️ **PHC Integration:** Lack of exercise drives 30% of the Hypertension and Diabetes burden. \n\n💡 **Physio/PHC Action:** Implement 'Exercise is Medicine' social prescribing at the dispensary level. Train Community Health Workers (CHWs) to lead community walking groups and basic rehabilitative exercises for stroke/chronic pain patients (Task-shifting).",
                "sw": f"🏃♂️ **Mazoezi na Urehabilitesheni (WHO GAPPA):** Ukosefu wa mazoezi uko kwa **{DHIS2_INDICATORS['inactivity']['value']}%** kitaifa, ukizidi lengo la 10%. \n\n️ **Ujumuishaji wa PHC:** Ukosefu wa mazoezi unasababisha 30% ya mzigo wa Shinikizo la Damu na Kisukari. \n\n💡 **Hatua ya Fizioterapia/PHC:** Tekeleza 'Mazoezi ni Dawa' katika zahanati. Wafunze Wahudumu wa Jamii (CHWs) kuongoza vikundi vya kutembea na mazoezi ya urehabilitesheni ya msingi kwa wagonjwa wa stroko/maumivu ya muda mrefu."
            },
            "nutrition": {
                "en": f"🍎 **Nutrition Double Burden (Tanzania NMNAP):** We face a dual crisis: Child Stunting is **{DHIS2_INDICATORS['stunting']['value']}%**, while Adult Obesity is rising to **{DHIS2_INDICATORS['obesity']['value']}%**. \n\n⚠️ **Climate Link:** El Niño droughts reduce crop yields, driving up the cost of fresh vegetables and forcing reliance on cheap, processed carbohydrates. \n\n💡 **PHC Action:** Integrate nutrition counseling into every ANC and NCD visit. Promote community gardens and bio-fortified crops to combat hidden hunger.",
                "sw": f" **Mzigo Mbili wa Lishe (NMNAP Tanzania):** Tunakabiliwa na janga mbili: Ufupisho wa Watoto ni **{DHIS2_INDICATORS['stunting']['value']}%**, huku Unene wa Kupindukia wa Watu Wazima ukifikia **{DHIS2_INDICATORS['obesity']['value']}%**. \n\n⚠️ **Uhusiano wa Hali ya Hewa:** Ukame wa El Niño hupunguza mavuno, kuongeza bei ya mboga mboga na kulazimisha kutumia wanga wa bei nafuu. \n\n💡 **Hatua ya PHC:** Jumuisha ushauri wa lishe katika kila ziara ya ANC na NCD. Kuzusha bustani za jamii na mazao yaliyoimarishwa kibiolojia."
            },
            "uhc_phc": {
                "en": f"🏥 **UHC & PHC Principles (Astana Declaration):** Out-of-Pocket expenditure is **{DHIS2_INDICATORS['oop_exp']['value']}%**, risking financial catastrophe for the poor. Health worker density is **{DHIS2_INDICATORS['hw_density']['value']} per 1,000** (Target: 0.45). \n\n⚠️ **Equity Gap:** Rural areas lack access to essential NCD and Rehab services. \n\n💡 **Action:** Scale up the Community Health Fund (CHF) to ensure financial protection. Deploy mobile PHC clinics and utilize tele-rehabilitation to reach underserved wards.",
                "sw": f"🏥 **Kanuni za UHC & PHC (Astana):** Matumizi ya Mfukoni ni **{DHIS2_INDICATORS['oop_exp']['value']}%**, yakitishia umasikini. Msongamano wa watumishi wa afya ni **{DHIS2_INDICATORS['hw_density']['value']} kwa 1,000** (Lengo: 0.45). \n\n⚠️ **Pengufu wa Haki:** Maeneo ya vijijini yana upungufu wa huduma za NCD na Urehabilitesheni. \n\n💡 **Hatua:** Kuzusha Mfuko wa Afya ya Jamii (CHF) kulinda kifedha. Peleka kliniki za sima za PHC na tumia tele-rehabilitesheni kufikia kata zilizonyimwa."
            }
        }

    def process_prompt(self, user_prompt, selected_role, language, selected_region):
        prompt_lower = user_prompt.lower()
        lang = 'sw' if language == 'Kiswahili' else 'en'
        region_data = REGIONS_DATA.get(selected_region, REGIONS_DATA["National Average"])
        
        # Keyword Routing
        if any(word in prompt_lower for word in ["exercise", "physical activity", "mazoezi", "physio", "rehab", "urehabilitesheni"]):
            base_response = self.context_db["physio_activity"][lang].replace("22.0%", f"{region_data['inactivity']}% in {selected_region}")
        elif any(word in prompt_lower for word in ["nutrition", "diet", "lishe", "stunting", "ufupisho", "obesity", "unene"]):
            base_response = self.context_db["nutrition"][lang].replace("26.0%", f"{region_data['stunting']}%").replace("8.5%", f"{region_data['obesity']}%")
        elif any(word in prompt_lower for word in ["uhc", "phc", "financial", "fedha", "access", "ufikiaji"]):
            base_response = self.context_db["uhc_phc"][lang].replace("28.0%", f"{region_data['oop_exp']}%").replace("0.15", f"{region_data['hw_density']}")
        else:
            base_response = f"Ask me about Physical Activity, Nutrition, UHC, or PHC in {selected_region}! / Niulize kuhusu Mazoezi, Lishe, UHC, au PHC katika {selected_region}!"

        return f"**Insight for {selected_region}:** {base_response}"

# ==============================================================================
# 3. UI & LAYOUT
# ==============================================================================
st.sidebar.title("🇹🇿 EcoHealth Sentinel")
st.sidebar.header("Settings / Mipangilio")
selected_region = st.sidebar.selectbox("Select Region / Chagua Mkoa:", list(REGIONS_DATA.keys()))
role = st.sidebar.selectbox("Your Role / Jukumu Lako:", ["Policymakers", "Physiotherapists/CHWs", "NGOs", "Researchers"])
language = st.sidebar.radio("Lugha / Language:", ["English", "Kiswahili"])

st.title(f"National Health Resilience Platform: {selected_region}")
st.markdown("Powered by ITU ML Pipeline | Integrating UHC, PHC, Nutrition & Active Living")

tab1, tab2, tab3, tab4 = st.tabs(["📊 UHC & National Dashboard", "🏃‍️ Physio, Nutrition & Lifestyle", "️ Tanzania GIS Map", "🤖 AI Assistant"])

# --- TAB 1: UHC & NATIONAL DASHBOARD ---
with tab1:
    st.header(f"UHC & PHC Core Indicators: {selected_region}")
    region_data = REGIONS_DATA[selected_region]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Maternal Mortality (per 100k)", value=f"{region_data['mmr']}", delta="-4", help="SDG 3.1 Target: 70")
    col2.metric(label="Out-of-Pocket Expenditure (%)", value=f"{region_data['oop_exp']}%", delta="-1%", help="UHC Financial Protection Target: <15%")
    col3.metric(label="Health Worker Density (per 1000)", value=f"{region_data['hw_density']}", delta="+0.02", help="PHC Equity Target: 0.45")
    col4.metric(label="Malaria Incidence (per 1k)", value=f"{region_data['malaria_inc']}", delta="+7", delta_color="inverse")

    st.divider()
    st.subheader("UHC Financial Protection & PHC Access Trends (2019-2023)")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=TREND_DATA['Year'], y=TREND_DATA['Out-of-Pocket Exp (%)'], mode='lines+markers', name='Out-of-Pocket Exp (%)', line=dict(color='#e74c3c')))
    fig1.add_trace(go.Scatter(x=TREND_DATA['Year'], y=TREND_DATA['Physical Inactivity (%)'], mode='lines+markers', name='Physical Inactivity (%)', yaxis='y2', line=dict(color='#3498db')))
    fig1.update_layout(title='Financial Risk Protection vs Lifestyle Risk Trends', yaxis=dict(title='Out-of-Pocket %'), yaxis2=dict(title='Inactivity %', overlaying='y', side='right'))
    st.plotly_chart(fig1, use_container_width=True)

# --- TAB 2: PHYSIO, NUTRITION & LIFESTYLE (The Physiotherapist's Domain) ---
with tab2:
    st.header(f"Primary Health Care: Lifestyle, Nutrition & Active Living in {selected_region}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🍎 The Nutrition Double Burden")
        nutrition_data = pd.DataFrame({
            'Indicator': ['Child Stunting (%)', 'Adult Obesity (%)'],
            'Prevalence': [region_data['stunting'], region_data['obesity']]
        })
        fig2 = px.bar(nutrition_data, x='Indicator', y='Prevalence', color='Indicator', title='Malnutrition vs Overnutrition')
        fig2.update_layout(yaxis=dict(title='Percentage (%)', range=[0, 40]))
        st.plotly_chart(fig2, use_container_width=True)
        st.info(f"💡 **PHC Action:** {selected_region} has a stunting rate of **{region_data['stunting']}%**. Integrate nutrition counseling into all ANC and NCD visits.")
        
    with col2:
        st.subheader("🏃‍♂️ Physical Activity & NCD Prevention")
        lifestyle_data = pd.DataFrame({
            'Risk Factor': ['Physical Inactivity (%)', 'Hypertension (%)', 'Diabetes (%)'],
            'Prevalence': [region_data['inactivity'], region_data['htn_prev'], region_data['dm_prev']]
        })
        fig3 = px.bar(lifestyle_data, x='Risk Factor', y='Prevalence', color='Risk Factor', title='Lifestyle NCD Risk Factors')
        st.plotly_chart(fig3, use_container_width=True)
        st.info(f"💡 **Physio Action:** Inactivity is at **{region_data['inactivity']}%**. Implement 'Exercise is Medicine' social prescribing at the dispensary level.")

# --- TAB 3: GIS MAP ---
with tab3:
    st.header("Tanzania National PHC & UHC Vulnerability Map")
    m = folium.Map(location=[-6.3690, 34.8888], zoom_start=6, tiles="OpenStreetMap")
    
    for name, data in REGIONS_DATA.items():
        # Composite risk: High Out-of-Pocket + Low Health Workers + High Inactivity
        risk_score = (data['oop_exp'] / 10) + (0.45 - data['hw_density'])*10 + (data['inactivity']/5)
        color = 'red' if risk_score > 6 else ('orange' if risk_score > 4 else 'green')
        
        folium.CircleMarker(
            location=[data['lat'], data['lon']], radius=15, color='white', 
            fill_color=color, fill=True, fill_opacity=0.9, weight=2,
            popup=f"<b>{name}</b><br>Out-of-Pocket: {data['oop_exp']}%<br>Health Workers: {data['hw_density']}/1000<br>Inactivity: {data['inactivity']}%"
        ).add_to(m)
    
    st_folium(m, width=1000, height=600)

# --- TAB 4: AI ASSISTANT ---
with tab4:
    st.header("Chat with EcoHealth AI (PHC, UHC, Physio & Nutrition Expert)")
    st.caption("Try asking: 'How can we improve physical activity?', 'Je, hali ya lishe ni how?', or 'What is the UHC financial protection status?'")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    agent = SmartEcoHealthAgent()
    if prompt := st.chat_input("Ask about UHC, PHC, Nutrition, or Physical Activity..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        response = agent.process_prompt(prompt, role, language, selected_region)
        
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
