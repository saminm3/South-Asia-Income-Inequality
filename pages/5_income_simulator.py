import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import textwrap
from utils.help_system import render_help_button
from utils.sidebar import apply_all_styles
from utils.data_loader import SouthAsiaDataLoader
from utils.loaders import load_inequality_data
from utils.api_loader import get_api_loader
from utils.un_data_loader import get_un_loader
from utils.imf_api_loader import get_imf_loader

st.set_page_config(
    page_title="Income Simulator",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

api_loader = get_api_loader()
un_loader = get_un_loader()
imf_loader = get_imf_loader()
render_help_button("simulator")
apply_all_styles()
# Load custom CSS
try:
    with open('assets/dashboard.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Custom CSS for Professional Look
st.markdown("""<style>
.pro-card {
background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(139, 92, 246, 0.05));
border-radius: 16px;
padding: 24px;
border: 1px solid rgba(139, 92, 246, 0.2);
margin-bottom: 20px;
box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
backdrop-filter: blur(8px);
}
.input-group-label {
font-size: 0.85rem;
color: #94a3b8;
text-transform: uppercase;
font-weight: 700;
letter-spacing: 1px;
margin-bottom: 12px;
}
.result-container {
text-align: center;
padding: 40px;
background: linear-gradient(180deg, rgba(139, 92, 246, 0.15) 0%, rgba(139, 92, 246, 0.05) 100%);
border-radius: 20px;
border: 1px solid rgba(139, 92, 246, 0.3);
margin-bottom: 30px;
box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
}
.metric-value-large {
font-size: 5rem;
font-weight: 800;
background: linear-gradient(90deg, #8b5cf6 0%, #ec4899 50%, #06b6d4 100%);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
line-height: 1.1;
margin: 10px 0;
}
.metric-label {
color: #94a3b8;
text-transform: uppercase;
font-size: 1rem;
letter-spacing: 2px;
font-weight: 600;
}
.metric-group {
font-size: 1.6rem;
font-weight: 700;
margin-top: 15px;
color: #ffffff;
}
.section-header {
font-size: 1.5rem;
font-weight: 800;
color: #ffffff;
margin: 40px 0 20px 0;
padding-bottom: 12px;
border-bottom: 2px solid rgba(6, 182, 212, 0.4);
display: flex;
align-items: center;
gap: 12px;
}
.comparison-card {
background: linear-gradient(135deg, rgba(139, 92, 246, 0.12), rgba(6, 182, 212, 0.08));
border: 2px solid rgba(139, 92, 246, 0.3);
border-radius: 20px;
padding: 35px;
margin: 25px 0;
box-shadow: 0 15px 45px rgba(0, 0, 0, 0.4);
}
.profile-badge {
display: inline-block;
padding: 10px 20px;
border-radius: 25px;
font-weight: 800;
font-size: 0.9rem;
letter-spacing: 1.5px;
text-transform: uppercase;
box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}
.badge-primary { background: linear-gradient(135deg, #8b5cf6, #ec4899); color: white; border: 1px solid rgba(255, 255, 255, 0.2); }
.badge-success { background: linear-gradient(135deg, #10b981, #06b6d4); color: white; border: 1px solid rgba(255, 255, 255, 0.2); }
.insight-panel {
background: rgba(139, 92, 246, 0.08);
border-left: 4px solid #8b5cf6;
padding: 24px;
border-radius: 0 12px 12px 0;
margin-bottom: 20px;
border-top: 1px solid rgba(139, 92, 246, 0.1);
border-right: 1px solid rgba(139, 92, 246, 0.1);
border-bottom: 1px solid rgba(139, 92, 246, 0.1);
}
.insight-panel-success {
background: rgba(16, 185, 129, 0.08);
border-left: 4px solid #10b981;
padding: 24px;
border-radius: 0 12px 12px 0;
margin-bottom: 20px;
}
.insight-panel-warning {
background: rgba(245, 158, 11, 0.08);
border-left: 4px solid #f59e0b;
padding: 24px;
border-radius: 0 12px 12px 0;
margin-bottom: 20px;
}
.insight-title {
color: #ffffff;
font-weight: 700;
margin-bottom: 14px;
display: flex;
align-items: center;
gap: 10px;
font-size: 1.15rem;
}
.historical-card {
background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(239, 68, 68, 0.05));
border: 1px solid rgba(245, 158, 11, 0.3);
border-radius: 16px;
padding: 25px;
margin: 20px 0;
backdrop-filter: blur(8px);
}
.delta-badge {
padding: 6px 14px;
border-radius: 8px;
font-weight: 800;
font-size: 0.95rem;
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
.delta-up { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }
.delta-down { background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }
</style>""", unsafe_allow_html=True)

# HERO SECTION - ALIGNED WITH HOME.PY
st.markdown("""<div style="text-align: center; margin-bottom: 3rem; padding-top: 1rem;">
<h1 style="font-size: 3.5rem; margin-bottom: 1rem; background: linear-gradient(90deg, #8b5cf6 0%, #ec4899 50%, #06b6d4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-weight: 800;">
Interactive Income Simulator
</h1>
<p style="font-size: 1.3rem; color: #94a3b8; margin-top: 0; font-weight: 500;">
Personalized Economic Modeling & Comparative Analytics
</p>
<div style="width: 80px; height: 4px; background: linear-gradient(90deg, #8b5cf6, #ec4899); margin: 20px auto; border-radius: 2px;"></div>
</div>""", unsafe_allow_html=True)

# Country data
COUNTRY_DATA = {
    'Afghanistan': {'base': 18, 'education_weight': 0.28, 'urban_bonus': 8},
    'Bangladesh': {'base': 25, 'education_weight': 0.32, 'urban_bonus': 8},
    'Bhutan': {'base': 23, 'education_weight': 0.30, 'urban_bonus': 7},
    'India': {'base': 22, 'education_weight': 0.35, 'urban_bonus': 12},
    'Maldives': {'base': 28, 'education_weight': 0.33, 'urban_bonus': 14},
    'Nepal': {'base': 22, 'education_weight': 0.32, 'urban_bonus': 7},
    'Pakistan': {'base': 20, 'education_weight': 0.30, 'urban_bonus': 10},
    'Sri Lanka': {'base': 25, 'education_weight': 0.32, 'urban_bonus': 11}
}

@st.cache_data(ttl=3600)
def get_historical_data_efficiently():
    """Helper to load main data once for simulator use"""
    return load_inequality_data()

def calculate_percentile(country, edu, digital, gender, urban, occupation="Services", credit=False, age="Adult", api_data=None, un_data=None, poverty_data=None):
    """Calculate economic percentile with detailed component breakdown"""
    data = COUNTRY_DATA.get(country, COUNTRY_DATA['India'])
    
    # Use API data for base if provided (Live Sync)
    if api_data is not None and not api_data.empty:
        # Base value calibrated to GDP per capita relative to regional average
        gdp_val = api_data[api_data['indicator'].str.contains('GDP')]['value'].mean() if any(api_data['indicator'].str.contains('GDP')) else 2000
        base = 15 + (np.log10(gdp_val/100) * 5)
    else:
        base = data['base']
        
    weight = data['education_weight']
    bonus = data['urban_bonus']
    
    occ_map = {"Agriculture": 0, "Industry": 8, "Services": 12, "Public Sector": 15, "Unemployed": -5}
    occ_val = occ_map.get(occupation, 10)
    
    credit_val = 6 if credit else 0
    
    age_map = {"Youth (<25)": -4, "Adult (25-60)": 6, "Senior (>60)": 2}
    age_val = age_map.get(age, 4)
    
    edu_contrib = (edu/20)*40*weight
    digital_contrib = (digital/100)*15
    
    # DYNAMIC GENDER IMPACT (API-DRIVEN)
    if un_data is not None and not un_data.empty:
        # Scale penalty based on GII (0.1 to 0.7)
        # Low GII (0.2) = ~4pt penalty | High GII (0.6) = ~12pt penalty
        gii_val = un_data['value'].iloc[0]
        gender_penalty = gii_val * 18 
    else:
        gender_penalty = 8 # Default fallback
        
    gender_contrib = gender*(-gender_penalty)
    urban_contrib = urban*bonus
    
    raw_percentile = base + edu_contrib + digital_contrib + gender_contrib + urban_contrib + occ_val + credit_val + age_val
    
    components = {
        "Base Value": base,
        "Education": edu_contrib,
        "Digital Skills": digital_contrib,
        "Occupation": occ_val,
        "Urban Advantage": urban_contrib,
        "Credit Access": credit_val,
        "Age Factor": age_val,
        "Gender Impact": gender_contrib 
    }
    
    # POVERTY BENCHMARKING (#4 IMPROVEMENT)
    poverty_bench = None
    if poverty_data is not None and not poverty_data.empty:
        pov_rate = poverty_data['value'].iloc[0] # % of population below poverty line
        # If pov_rate is 20%, then anyone below 20th percentile is 'Below Poverty Line'
        dist = raw_percentile - pov_rate
        poverty_bench = {
            "rate": pov_rate,
            "distance": dist,
            "status": "Below Poverty Line" if dist < 0 else ("Near Poverty Line" if dist < 15 else "Above Poverty Line")
        }
    
    return max(0, min(100, raw_percentile)), components, poverty_bench

def calculate_historical_percentile(country, year, edu, digital, gender, urban, occupation="Services", credit=False, age="Adult"):
    """
    Data-driven historical percentile calculation.
    Adjusts weights based on real-world indicators for that specific year.
    Uses south_asia_indicators.csv as the source of truth.
    """
    all_data = get_historical_data_efficiently()
    country_data = all_data[all_data['country'] == country]
    
    def get_val(indicator_name, default_val):
        # Try exact year
        val_df = country_data[(country_data['indicator'] == indicator_name) & (country_data['year'] == year)]
        if not val_df.empty:
            return val_df['value'].values[0]
        
        # Try closest year within 5 years
        proximity_df = country_data[country_data['indicator'] == indicator_name].copy()
        if proximity_df.empty:
            return default_val
        
        proximity_df['dist'] = abs(proximity_df['year'] - year)
        closest = proximity_df[proximity_df['dist'] <= 5].sort_values('dist')
        if not closest.empty:
            return closest['value'].values[0]
        
        return default_val

    # FETCH DATA
    internet_val = get_val('Individuals using the Internet (% of population)', 0.1 if year < 2005 else 10.0)
    edu_completion = get_val('Completion rate, primary education (%)', 60.0 if year < 2005 else 80.0)
    gdp_pc = get_val('GDP per capita (current US$)', 500.0 if year < 2005 else 2000.0)
    gini_val = get_val('Gini index', 35.0)

    # DYNAMIC WEIGHTS - Continuous Scaling for higher sensitivity
    # 1. Digital Skills weight: Exclusive eliteness factor
    # Scaled from 3.0x (at 0% internet) down to 1.0x (at 40% internet)
    digital_mult = max(1.0, 3.0 - (internet_val / 20.0))
    digital_weight = 15.0 * digital_mult
    
    # 2. Education weight: Scarcity value of formal schooling
    # Scaled from 1.8x (at 40% completion) down to 1.0x (at 95% completion)
    edu_mult = max(1.0, 1.8 - ((edu_completion - 40) / 55.0 * 0.8)) if edu_completion > 40 else 1.8
    base_edu_weight = COUNTRY_DATA.get(country, COUNTRY_DATA['India'])['education_weight']
    adjusted_edu_weight = base_edu_weight * edu_mult
    
    # 3. Base Value: Absolute economic floor calibrated to GDP growth
    # We use a log scale to reflect that a $2k economy provides a much higher "floor" than a $400 economy
    gdp_floor = np.log2(max(1, gdp_pc / 100)) * 4
    base_val = 10.0 + gdp_floor - (gini_val / 5)
    
    # Standard components
    occ_map = {"Agriculture": 0, "Industry": 8, "Services": 12, "Public Sector": 15, "Unemployed": -5}
    occ_val = occ_map.get(occupation, 10)
    credit_val = 6 if credit else 0
    age_map = {"Youth (<25)": -4, "Adult (25-60)": 6, "Senior (>60)": 2}
    age_val = age_map.get(age, 4)
    
    edu_contrib = (edu/20)*40*adjusted_edu_weight
    digital_contrib = (digital/100)*digital_weight
    gender_contrib = gender*(-8)
    urban_contrib = urban*COUNTRY_DATA.get(country, COUNTRY_DATA['India'])['urban_bonus']
    
    raw_p = base_val + edu_contrib + digital_contrib + gender_contrib + urban_contrib + occ_val + credit_val + age_val
    
    components = {
        "Base Economic Strength": base_val,
        "Education Prestige": edu_contrib,
        "Digital Edge Factor": digital_contrib,
        "Occupation Sector": occ_val,
        "Social Access Factors": urban_contrib + gender_contrib + credit_val + age_val
    }
    
    return max(0, min(100, raw_p)), components

def get_tercile(p):
    if p < 33.33: return "Lower Tercile", "#ef4444"
    if p < 66.66: return "Middle Tercile", "#f59e0b"
    return "Upper Tercile", "#10b981"

def render_gauge(p, title="", height=250):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=p,
        title={'text': title, 'font': {'size': 18, 'color': '#e2e8f0'}},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#8b98a5"},
            'bar': {'color': "#ffffff"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 33.33], 'color': "rgba(239, 68, 68, 0.3)"},
                {'range': [33.33, 66.66], 'color': "rgba(245, 158, 11, 0.3)"},
                {'range': [66.66, 100], 'color': "rgba(16, 185, 129, 0.3)"}
            ],
            'threshold': {'line': {'color': "#fff", 'width': 4}, 'thickness': 0.75, 'value': p}
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "#e2e8f0"},
        height=height,
        margin=dict(l=30, r=30, t=50, b=20)
    )
    return fig

def generate_insights(sp_p, breakdown_components, sp_country, sp_gender, sp_location, sp_occ, sp_credit, sp_edu, sp_digital, sp_poverty=None):
    """Generate plain-language insights"""
    insights = []
    
    # Poverty Benchmark Insight
    if sp_poverty:
        color_type = "success" if sp_poverty['status'] == "Above Poverty Line" else ("warning" if sp_poverty['status'] == "Near Poverty Line" else "warning")
        insights.append({
            "type": color_type, "icon": "📉", "title": f"Poverty Benchmark: {sp_poverty['status']}",
            "text": f"Based on live World Bank data, your profile is <b>{abs(sp_poverty['distance']):.1f}%</b> {'above' if sp_poverty['distance'] > 0 else 'below'} the national poverty line for {sp_country}."
        })
    
    # Overall position
    if sp_p >= 66.66:
        insights.append({
            "type": "success", "icon": "🎯", "title": "Strong Economic Position",
            "text": f"Your profile places you in the top third of earners in {sp_country}. You're doing better than roughly {sp_p:.0f} out of every 100 people."
        })
    elif sp_p >= 33.33:
        insights.append({
            "type": "info", "icon": "📊", "title": "Middle Income Bracket",
            "text": f"You're in the middle income group in {sp_country}. You're ahead of about {sp_p:.0f}% of people, but there's room to climb with the right opportunities."
        })
    else:
        insights.append({
            "type": "warning", "icon": "⚠️", "title": "Lower Income Position",
            "text": f"Your profile suggests you're facing economic challenges. While you're ahead of {sp_p:.0f}% of people, structural barriers may be limiting opportunities."
        })
    
    # Education
    edu_contrib = breakdown_components['Education']
    if sp_edu < 10:
        potential_gain = (12-sp_edu) * 2
        insights.append({
            "type": "warning", "icon": "🎓", "title": "Education Gap Detected",
            "text": f"With only {sp_edu} years of education, you're missing significant opportunities. Completing 12 years could boost your position by approximately {potential_gain:.0f} points."
        })
    elif sp_edu >= 16:
        insights.append({
            "type": "success", "icon": "🎓", "title": "Strong Educational Foundation",
            "text": f"Your {sp_edu} years of education is a major advantage, adding {edu_contrib:.1f} points. This opens doors to professional roles and higher-paying sectors."
        })
    
    # Gender
    if sp_gender == "Female":
        gender_impact = abs(breakdown_components['Gender Impact'])
        insights.append({
            "type": "warning", "icon": "⚖️", "title": "Gender Wage Gap Impact",
            "text": f"As a woman in {sp_country}, you face a structural disadvantage of about {gender_impact:.0f} points. This reflects real-world wage gaps and labor participation barriers."
        })
    
    # Digital
    if sp_digital < 40:
        potential = (75-sp_digital) * 0.15
        insights.append({
            "type": "warning", "icon": "💻", "title": "Digital Skills Gap",
            "text": f"Your {sp_digital}% digital proficiency is limiting opportunities. Improving to 75%+ could add {potential:.1f} points—access to jobs paying 2-3x more."
        })
    elif sp_digital >= 75:
        insights.append({
            "type": "success", "icon": "💻", "title": "Digital Economy Ready",
            "text": f"Your {sp_digital}% digital proficiency is excellent! You're positioned for modern service jobs, remote work, and tech-enabled roles."
        })
    
    # Location
    if sp_location == "Rural":
        urban_bonus = COUNTRY_DATA[sp_country]['urban_bonus']
        insights.append({
            "type": "info", "icon": "🏘️", "title": "Rural Location Trade-off",
            "text": f"Living rurally means missing the urban premium of {urban_bonus} points. Cities offer more jobs and higher wages, but also higher costs."
        })
    else:
        insights.append({
            "type": "success", "icon": "🏙️", "title": "Urban Location Advantage",
            "text": f"Living urban gives you {breakdown_components['Urban Advantage']:.0f} extra points from concentrated economic opportunities."
        })
    
    # Occupation
    occ_values = {"Agriculture": 0, "Industry": 8, "Services": 12, "Public Sector": 15, "Unemployed": -5}
    if sp_occ == "Agriculture":
        insights.append({
            "type": "warning", "icon": "🌾", "title": "Agricultural Sector Limitations",
            "text": f"Agriculture offers lowest incomes. Transitioning to services/public sector could boost position by 12-15 points—earning 2-3x more."
        })
    elif sp_occ == "Public Sector":
        insights.append({
            "type": "success", "icon": "🏛️", "title": "Public Sector Advantage",
            "text": f"Public sector employment contributes {occ_values[sp_occ]} points—highest of any sector. Job security, regular wages, and benefits."
        })
    
    # Credit
    if not sp_credit:
        insights.append({
            "type": "warning", "icon": "🏦", "title": "Financial Exclusion Barrier",
            "text": f"Lack of credit access costs 6 points. Without banking, you can't save safely, build credit, get loans, or invest. Opening an account is easiest improvement."
        })
    else:
        insights.append({
            "type": "success", "icon": "🏦", "title": "Financial Inclusion Advantage",
            "text": f"Credit access adds 6 points, enabling investment in assets, handling emergencies, and building financial security."
        })
    
    # Recommendations
    recommendations = []
    if sp_edu < 12:
        recommendations.append({"priority": "HIGH", "action": "Complete Basic Education", 
            "detail": f"Finish 12 years of schooling. Each year adds 2-3 points. Most important foundation for mobility."})
    if sp_digital < 60:
        recommendations.append({"priority": "HIGH", "action": "Build Digital Skills",
            "detail": f"Learn computer/internet basics. Target 75%+. Free resources like YouTube can help. Opens modern economy jobs."})
    if not sp_credit:
        recommendations.append({"priority": "MEDIUM", "action": "Get Financial Access",
            "detail": f"Open bank account. Start saving, even small amounts. Foundational for security."})
    if sp_occ in ["Agriculture", "Unemployed"]:
        recommendations.append({"priority": "HIGH", "action": "Explore Career Transition",
            "detail": f"With {sp_edu} years education, consider vocational training or services/industry entry positions. Could double income."})
    if sp_location == "Rural" and sp_edu >= 12:
        recommendations.append({"priority": "MEDIUM", "action": "Consider Urban Migration",
            "detail": f"Your education could unlock better city opportunities. Could add {COUNTRY_DATA[sp_country]['urban_bonus']} points. Weigh against family ties and urban costs."})
    
    return insights, recommendations

# ============= MAIN APP =============

# Removed old header section as it's replaced by the new HERO SECTION above

# Track simulator mode in session state
if 'simulator_mode' not in st.session_state:
    st.session_state.simulator_mode = "individual"

# Methodology
with st.expander("🔬 How Does This Simulator Work?", expanded=False):
    st.markdown("""
    ### Calculation Methodology
    
    This simulator uses a **multi-factor regression model** calibrated for South Asian economies. It shows your **relative economic position** compared to others in your country, not exact income.
    
    **The Formula:**
    ```
    Economic Position = Base + Education + Digital Skills + Gender + 
                       Urban/Rural + Occupation + Credit Access + Age
    ```
    """)

# ============= LIVE DATA SYNC (DENSE DATA INTEGRATION) =============
with st.sidebar:
    st.markdown("### 🌐 Live Data Integration")
    use_live_data = st.toggle("Enable Live API Sync", value=False, help="Pull real-time GDP and Gini data from World Bank for calibration")
    
    if use_live_data:
        st.success("API: World Bank Connected")
        rates = api_loader.get_exchange_rates()
        st.info(f"Exchange Rates (Live): 1 USD = {rates.get('BDT', 110)} BDT | {rates.get('INR', 83)} INR")

# ============= MODE SELECTION =============
st.markdown('<p class="section-header">🎯 Step 1: Choose Your Simulator Mode</p>', unsafe_allow_html=True)

mode_options = ["📊 Individual Profile Simulator", "🔄 Profile Comparison Simulator", "🗓️ Historical Snapshot Comparison"]
current_mode_idx = 0
if st.session_state.simulator_mode == "comparison": current_mode_idx = 1
elif st.session_state.simulator_mode == "historical": current_mode_idx = 2

mode = st.radio(
    "Select Simulation Mode:",
    mode_options,
    index=current_mode_idx,
    horizontal=True,
    label_visibility="collapsed"
)

# Update state based on radio selection
if "Individual" in mode:
    st.session_state.simulator_mode = "individual"
elif "Historical Snapshot" in mode:
    st.session_state.simulator_mode = "historical"
else:
    st.session_state.simulator_mode = "comparison"

mode_display = {
    "individual": "📊 Individual Profile",
    "comparison": "🔄 Profile Comparison",
    "historical": "🗓️ Historical Snapshot"
}

# Display selected mode info
st.markdown(f"""<div style="text-align: center; margin: 20px 0; padding: 15px; background: rgba(139, 92, 246, 0.1); border-radius: 12px; border: 1px solid rgba(139, 92, 246, 0.3);">
<span style="color: #ffffff; font-weight: 700; font-size: 1.1rem; letter-spacing: 0.5px;">
<span style="color: #8b5cf6;">ACTIVE MODE:</span> {mode_display.get(st.session_state.simulator_mode).upper()}
</span>
</div>""", unsafe_allow_html=True)

st.markdown("---")

# ============= CONDITIONAL RENDERING BASED ON MODE =============

if st.session_state.simulator_mode == "individual":
    # ============= INDIVIDUAL MODE - STEP 1: PROFILE =============
    
    st.markdown('<p class="section-header">📝 Step 2: Build Your Profile</p>', unsafe_allow_html=True)

    col_input, col_preview = st.columns([2, 1], gap="large")

    with col_input:
        st.markdown('<div class="input-group-label">🌍 Country</div>', unsafe_allow_html=True)
        sp_country = st.selectbox("Select your country", list(COUNTRY_DATA.keys()), key="sp_country", label_visibility="collapsed")
        
        st.markdown('<div class="input-group-label" style="margin-top: 25px;">🎓 Education & Skills</div>', unsafe_allow_html=True)
        
        col_edu1, col_edu2 = st.columns(2)
        with col_edu1:
            sp_edu = st.slider("Years of Formal Education", 0, 20, 12, key="sp_edu")
        with col_edu2:
            sp_digital = st.slider("Digital Proficiency (%)", 0, 100, 50, key="sp_digital")
        
        st.markdown('<div class="input-group-label" style="margin-top: 25px;">👤 Demographics</div>', unsafe_allow_html=True)
        
        col_demo1, col_demo2 = st.columns(2)
        with col_demo1:
            sp_gender = st.selectbox("Gender", ["Male", "Female"], key="sp_gender")
            sp_age = st.selectbox("Age Group", ["Youth (<25)", "Adult (25-60)", "Senior (>60)"], index=1, key="sp_age")
        with col_demo2:
            sp_location = st.selectbox("Location Type", ["Rural", "Urban"], key="sp_location")
            sp_credit = st.checkbox("Has Bank Account / Credit Access", value=False, key="sp_credit")
        
        st.markdown('<div class="input-group-label" style="margin-top: 25px;">💼 Occupation</div>', unsafe_allow_html=True)
        sp_occ = st.selectbox("Primary Work Sector", ["Agriculture", "Industry", "Services", "Public Sector", "Unemployed"], index=2, key="sp_occ", label_visibility="collapsed")

    with col_preview:
        # Profile Preview Card - Flattened
        st.markdown(f"""<div class="pro-card" style="border: 2px solid rgba(139, 92, 246, 0.4);">
<div class="input-group-label" style="text-align: center; margin-bottom: 20px; color: #8b5cf6;">👤 Profile Preview</div>
<div style="line-height: 2.2; color: #e2e8f0; font-size: 0.95rem;">
<b style="color: #8b5cf6; font-weight: 700;">Country:</b> {sp_country}<br>
<b style="color: #8b5cf6; font-weight: 700;">Education:</b> {sp_edu} yrs<br>
<b style="color: #8b5cf6; font-weight: 700;">Skills:</b> {sp_digital}% proficiency<br>
<b style="color: #8b5cf6; font-weight: 700;">Gender:</b> {sp_gender}<br>
<b style="color: #8b5cf6; font-weight: 700;">Location:</b> {sp_location}<br>
<b style="color: #8b5cf6; font-weight: 700;">Credit:</b> {'Yes' if sp_credit else 'No'}<br>
<b style="color: #8b5cf6; font-weight: 700;">Occupation:</b> {sp_occ}
</div>
</div>""", unsafe_allow_html=True)

    # Calculate
    g_val = 1 if sp_gender == "Female" else 0
    u_val = 1 if sp_location == "Urban" else 0
    
    live_indicators = None
    un_live_data = None
    poverty_live = None
    if use_live_data:
        with st.spinner("Fetching live economic benchmarks..."):
            live_indicators = api_loader.fetch_indicator('NY.GDP.PCAP.CD', countries=sp_country, date_range="2022:2023")
            un_live_data = un_loader.get_gender_inequality_index([sp_country])
            poverty_live = api_loader.fetch_indicator('SI.POV.DDAY', countries=sp_country, date_range="2018:2023")
        
    sp_p, breakdown_components, sp_poverty = calculate_percentile(sp_country, sp_edu, sp_digital, g_val, u_val, sp_occ, sp_credit, sp_age, api_data=live_indicators, un_data=un_live_data, poverty_data=poverty_live)

    # ============= STEP 2: RESULTS =============

    st.markdown('<p class="section-header">📊 Step 3: Your Simulation Results</p>', unsafe_allow_html=True)

    group, color = get_tercile(sp_p)

    result_col1, result_col2 = st.columns([1, 1], gap="large")

    with result_col1:
        # Create flat HTML string to avoid markdown indentation issues
        res_html = f"""<div class="result-container">
<p class="metric-label">Your Economic Percentile</p>
<div class="metric-value-large">{sp_p:.1f}<span style="font-size: 2rem;">th</span></div>
<div class="metric-group" style="color: {color};">{group.upper()}</div>
<p style="color: #94a3b8; margin-top: 25px; font-size: 1.1rem; line-height: 1.7; max-width: 600px; margin-left: auto; margin-right: auto;">
This means you rank <b>higher than {sp_p:.1f}%</b> of people in {sp_country}. Out of every 100 people, your profile indicates a better economic position than about <b>{int(sp_p)}</b> of them.
</p>
</div>"""
        if sp_poverty:
            res_html += f"""
<div style="background: rgba(239, 68, 68, 0.1); padding: 25px; border-radius: 16px; border: 1px solid rgba(239, 68, 68, 0.3); margin-bottom: 30px; text-align: center;">
<p style="color: #fca5a5; font-size: 0.9rem; margin: 0; text-transform: uppercase; font-weight: 700; letter-spacing: 1.5px;">Live Poverty Benchmark</p>
<h2 style="color: #ffffff; margin: 10px 0; font-weight: 800;">{sp_poverty['status']}</h2>
<p style="color: #e2e8f0; font-size: 1.05rem;">Positioned <b>{abs(sp_poverty['distance']):.1f}%</b> {'above' if sp_poverty['distance'] > 0 else 'below'} the national poverty line.</p>
</div>"""
        st.markdown(res_html, unsafe_allow_html=True)
        
        # LIVE CURRENCY CONVERTER (DENSE DATA FEATURE)
        currencies = {"Bangladesh": "BDT", "India": "INR", "Pakistan": "PKR", "Sri Lanka": "LKR", "Nepal": "NPR"}
        curr_code = currencies.get(sp_country, "USD")
        rates = api_loader.get_exchange_rates()
        rate = rates.get(curr_code, 1.0 if curr_code == "USD" else 100.0)
        
        # Estimate a nominal 'relative monthly income' for visualization
        # This is strictly illustrative to show the power of the API
        base_ppp = 400 # Base monthly USD for 50th percentile
        est_usd = base_ppp * (1.2 ** ((sp_p - 50)/10))
        est_local = est_usd * rate
        
        st.markdown(f"""<div style="background: rgba(29, 155, 240, 0.05); padding: 15px; border-radius: 12px; border: 1px dashed #1d9bf0;">
<p style="color: #8b98a5; font-size: 0.8rem; margin: 0;">Relative Standing Monthly Estimate (Live {curr_code})</p>
<h4 style="color: #1d9bf0; margin: 5px 0;">{est_local:,.0f} {curr_code}</h4>
<p style="color: #5c6d7e; font-size: 0.75rem;">Converted via Live API 1 USD ≈ {rate:.1f} {curr_code}</p>
</div>""", unsafe_allow_html=True)

    with result_col2:
        st.plotly_chart(render_gauge(sp_p, "Your Economic Position", height=300), use_container_width=True)

    # ============= STEP 3: INSIGHTS =============

    st.markdown('<p class="section-header">💡 Step 4: What This Means for You - Plain Language Insights</p>', unsafe_allow_html=True)

    insights, recommendations = generate_insights(sp_p, breakdown_components, sp_country, sp_gender, sp_location, sp_occ, sp_credit, sp_edu, sp_digital, sp_poverty=sp_poverty)

    insight_cols = st.columns(2, gap="large")

    for idx, insight in enumerate(insights):
        with insight_cols[idx % 2]:
            panel_class = f"insight-panel-{insight['type']}" if insight['type'] in ['success', 'warning'] else "insight-panel"
            st.markdown(f"""<div class="{panel_class}">
<div class="insight-title">{insight['icon']} {insight['title']}</div>
<p style="color: #e2e8f0; font-size: 0.95rem; line-height: 1.6; margin: 0;">{insight['text']}</p>
</div>""", unsafe_allow_html=True)

    # Recommendations
    if recommendations:
        st.markdown('<p class="section-header" style="margin-top: 50px;">🎯 Personalized Recommendations</p>', unsafe_allow_html=True)
        st.markdown('<p style="color: #94a3b8; font-size: 1.1rem; margin-bottom: 25px;">Based on your profile, here are the most impactful actions to improve your economic position:</p>', unsafe_allow_html=True)
        
        for i, rec in enumerate(recommendations, 1):
            priority_color = "#ef4444" if rec['priority'] == "HIGH" else "#f59e0b"
            st.markdown(f"""<div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 12px; margin-bottom: 15px; border-left: 4px solid {priority_color}; border: 1px solid rgba(255,255,255,0.05); border-left-width: 4px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
<b style="color: #ffffff; font-size: 1.1rem;">{i}. {rec['action']}</b>
<span style="background: {priority_color}; color: white; padding: 5px 15px; border-radius: 20px; font-size: 0.8rem; font-weight: 700;">{rec['priority']}</span>
</div>
<p style="color: #cbd5e1; margin: 0; line-height: 1.7; font-size: 1rem;">{rec['detail']}</p>
</div>""", unsafe_allow_html=True)

    # ============= STEP 4: VISUALIZATIONS =============

    st.markdown('<p class="section-header" style="margin-top: 50px;">🔍 Step 5: Understanding Your Score</p>', unsafe_allow_html=True)

    viz_col1, viz_col2 = st.columns([1, 1], gap="large")

    with viz_col1:
        st.markdown("### 🏗️ What's Building Your Score?")
        st.markdown('<p style="color: #94a3b8; font-size: 1rem; margin-bottom: 20px;">The size of each block indicates its contribution to your final percentile.</p>', unsafe_allow_html=True)
        
        tree_data = [{"Factor": k, "Contribution": v} for k, v in breakdown_components.items() if v > 0]
        
        if tree_data:
            df_tree = pd.DataFrame(tree_data)
            fig_tree = px.treemap(df_tree, path=['Factor'], values='Contribution', color='Contribution', color_continuous_scale='Purples')
            fig_tree.update_traces(textinfo="label+value", textfont=dict(size=14, color='white'))
            fig_tree.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': '#e2e8f0'}, height=350, margin=dict(t=5, l=5, r=5, b=5))
            st.plotly_chart(fig_tree, use_container_width=True)

    with viz_col2:
        st.markdown("### 📈 The Education Lever")
        st.markdown('<p style="color: #94a3b8; font-size: 1rem; margin-bottom: 20px;">Visualizing how increasing your years of education shifts your economic standing.</p>', unsafe_allow_html=True)
        
        edu_range = list(range(0, 21, 2))
        scores_by_edu = []
        for e in edu_range:
            score, _, _ = calculate_percentile(sp_country, e, sp_digital, g_val, u_val, sp_occ, sp_credit, sp_age)
            scores_by_edu.append({"Years": e, "Percentile": score})
        
        df_edu = pd.DataFrame(scores_by_edu)
        fig_line = px.line(df_edu, x='Years', y='Percentile', markers=True)
        fig_line.add_scatter(x=[sp_edu], y=[sp_p], mode='markers', marker=dict(size=18, color='#ec4899', symbol='star', line=dict(color='white', width=2)), name='Current State')
        fig_line.update_traces(line_color='#8b5cf6', line_width=4, selector=dict(mode='lines'))
        fig_line.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': '#e2e8f0'}, height=350,
            xaxis=dict(title="Years of Education", showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(title="Economic Percentile", showgrid=True, gridcolor='rgba(255,255,255,0.05)', range=[0, 100]),
            margin=dict(t=10, l=10, r=10, b=10),
            showlegend=False
        )
        st.plotly_chart(fig_line, use_container_width=True)

    # Factor table
    st.markdown('<p class="section-header" style="margin-top: 50px;">📋 Detailed Factor Contribution</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94a3b8; font-size: 1.1rem; margin-bottom: 25px;">A granular look at how each attribute influenced your final simulation result.</p>', unsafe_allow_html=True)
    
    factor_df = pd.DataFrame([
        {"Factor": k, "Points Added": f"{v:+.1f}", "Impact": "🟢 Positive" if v > 0 else ("🔴 Negative" if v < 0 else "⚪ Neutral")}
        for k, v in breakdown_components.items()
    ])
    st.dataframe(factor_df, use_container_width=True, hide_index=True)

# ============= COMPARISON MODE =============
elif st.session_state.simulator_mode == "comparison":
    st.markdown('<p class="section-header">📝 Step 2: Build Both Profiles</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="comparison-card">
        <h3 style="text-align: center; color: #ffffff; margin-bottom: 10px;">Profile Comparison Tool</h3>
        <p style="text-align: center; color: #8b98a5; margin-bottom: 20px;">Create two independent profiles to see how different factors affect economic outcomes</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Profile A and B inputs side by side - BOTH INDEPENDENT
    profile_col1, profile_col2 = st.columns([1, 1], gap="large")
    
    with profile_col1:
        st.markdown('<div class="input-group-label" style="text-align: center; margin-bottom: 20px; color: #8b5cf6;">🔹 Profile A Settings</div>', unsafe_allow_html=True)
        
        # PROFILE A INPUTS
        st.markdown('<div class="input-group-label">🌍 Country</div>', unsafe_allow_html=True)
        profile_a_country = st.selectbox("Country", list(COUNTRY_DATA.keys()), key="profile_a_country", label_visibility="collapsed")
        
        st.markdown('<div class="input-group-label" style="margin-top: 25px;">🎓 Education & Skills</div>', unsafe_allow_html=True)
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            profile_a_edu = st.slider("Education (yrs)", 0, 20, 12, key="profile_a_edu")
        with col_a2:
            profile_a_digital = st.slider("Digital (%)", 0, 100, 50, key="profile_a_digital")
        
        st.markdown('<div class="input-group-label" style="margin-top: 25px;">👤 Demographics</div>', unsafe_allow_html=True)
        col_a3, col_a4 = st.columns(2)
        with col_a3:
            profile_a_gender = st.selectbox("Gender", ["Male", "Female"], key="profile_a_gender")
            profile_a_age = st.selectbox("Age", ["Youth (<25)", "Adult (25-60)", "Senior (>60)"], index=1, key="profile_a_age")
        with col_a4:
            profile_a_location = st.selectbox("Location", ["Rural", "Urban"], key="profile_a_location")
            profile_a_credit = st.checkbox("Credit Access", value=False, key="profile_a_credit")
        
        st.markdown('<div class="input-group-label" style="margin-top: 25px;">💼 Occupation</div>', unsafe_allow_html=True)
        profile_a_occ = st.selectbox("Work Sector", ["Agriculture", "Industry", "Services", "Public Sector", "Unemployed"], index=2, key="profile_a_occ", label_visibility="collapsed")
    
    with profile_col2:
        st.markdown('<div class="input-group-label" style="text-align: center; margin-bottom: 20px; color: #10b981;">🔸 Profile B Settings</div>', unsafe_allow_html=True)
        
        # PROFILE B INPUTS - COMPLETELY INDEPENDENT
        st.markdown('<div class="input-group-label">🌍 Country</div>', unsafe_allow_html=True)
        profile_b_country = st.selectbox("Country", list(COUNTRY_DATA.keys()), key="profile_b_country", label_visibility="collapsed")
        
        st.markdown('<div class="input-group-label" style="margin-top: 25px;">🎓 Education & Skills</div>', unsafe_allow_html=True)
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            profile_b_edu = st.slider("Education (yrs)", 0, 20, 12, key="profile_b_edu")
        with col_b2:
            profile_b_digital = st.slider("Digital (%)", 0, 100, 50, key="profile_b_digital")
        
        st.markdown('<div class="input-group-label" style="margin-top: 25px;">👤 Demographics</div>', unsafe_allow_html=True)
        col_b3, col_b4 = st.columns(2)
        with col_b3:
            profile_b_gender = st.selectbox("Gender", ["Male", "Female"], key="profile_b_gender")
            profile_b_age = st.selectbox("Age", ["Youth (<25)", "Adult (25-60)", "Senior (>60)"], index=1, key="profile_b_age")
        with col_b4:
            profile_b_location = st.selectbox("Location", ["Rural", "Urban"], key="profile_b_location")
            profile_b_credit = st.checkbox("Credit Access", value=False, key="profile_b_credit")
        
        st.markdown('<div class="input-group-label" style="margin-top: 25px;">💼 Occupation</div>', unsafe_allow_html=True)
        profile_b_occ = st.selectbox("Work Sector", ["Agriculture", "Industry", "Services", "Public Sector", "Unemployed"], index=2, key="profile_b_occ", label_visibility="collapsed")
    
    # Calculate both profiles with Live API Data support
    live_a = None
    un_a = None
    pov_a = None
    live_b = None
    un_b = None
    pov_b = None
    
    if use_live_data:
        live_a = api_loader.fetch_indicator('NY.GDP.PCAP.CD', countries=profile_a_country, date_range="2022:2023")
        un_a = un_loader.get_gender_inequality_index([profile_a_country])
        pov_a = api_loader.fetch_indicator('SI.POV.DDAY', countries=profile_a_country, date_range="2018:2023")
        
        live_b = api_loader.fetch_indicator('NY.GDP.PCAP.CD', countries=profile_b_country, date_range="2022:2023")
        un_b = un_loader.get_gender_inequality_index([profile_b_country])
        pov_b = api_loader.fetch_indicator('SI.POV.DDAY', countries=profile_b_country, date_range="2018:2023")

    profile_a_g_val = 1 if profile_a_gender == "Female" else 0
    profile_a_u_val = 1 if profile_a_location == "Urban" else 0
    profile_a_p, profile_a_components, profile_a_pov = calculate_percentile(
        profile_a_country, profile_a_edu, profile_a_digital, 
        profile_a_g_val, profile_a_u_val, profile_a_occ, profile_a_credit, profile_a_age,
        api_data=live_a, un_data=un_a, poverty_data=pov_a
    )
    
    profile_b_g_val = 1 if profile_b_gender == "Female" else 0
    profile_b_u_val = 1 if profile_b_location == "Urban" else 0
    profile_b_p, profile_b_components, profile_b_pov = calculate_percentile(
        profile_b_country, profile_b_edu, profile_b_digital, 
        profile_b_g_val, profile_b_u_val, profile_b_occ, profile_b_credit, profile_b_age,
        api_data=live_b, un_data=un_b, poverty_data=pov_b
    )
    
    #  ============= COMPARISON RESULTS =============
    st.markdown('<p class="section-header">📊 Step 3: Comparison Results</p>', unsafe_allow_html=True)
    
    # Display both profile summaries with scores
    summary_col1, summary_col2 = st.columns([1, 1], gap="large")
    
    with summary_col1:
        card_a = f"""<div class="pro-card" style="border: 2px solid rgba(139, 92, 246, 0.4);">
<div style="text-align: center; margin-bottom: 25px;"><span class="profile-badge badge-primary">Profile A Results</span></div>
<div style="background: rgba(139, 92, 246, 0.15); padding: 25px; border-radius: 12px; margin-bottom: 20px; text-align: center; border: 1px solid rgba(139, 92, 246, 0.2);">
<div style="font-size: 4rem; font-weight: 800; color: #ffffff; margin: 10px 0; background: linear-gradient(90deg, #8b5cf6, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{profile_a_p:.1f}<span style="font-size: 1.5rem;">th</span></div>
<div style="color: #94a3b8; font-size: 0.95rem; font-weight: 700; letter-spacing: 1px;">PERCENTILE</div>
</div>"""
        if profile_a_pov:
            card_a += f"""<div style='text-align: center; background: rgba(239, 68, 68, 0.1); padding: 10px; border-radius: 20px; border: 1px solid rgba(239, 68, 68, 0.3); margin-bottom: 20px;'><span style='color: #fca5a5; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;'>Live: {profile_a_pov['status']}</span></div>"""
        card_a += f"""<div style="line-height: 2.2; color: #e2e8f0; font-size: 0.95rem;">
<b style="color: #8b5cf6; font-weight: 700;">Country:</b> {profile_a_country}<br>
<b style="color: #8b5cf6; font-weight: 700;">Education:</b> {profile_a_edu} years<br>
<b style="color: #8b5cf6; font-weight: 700;">Digital:</b> {profile_a_digital}%<br>
<b style="color: #8b5cf6; font-weight: 700;">Gender:</b> {profile_a_gender}<br>
<b style="color: #8b5cf6; font-weight: 700;">Location:</b> {profile_a_location}<br>
<b style="color: #8b5cf6; font-weight: 700;">Credit:</b> {'Yes' if profile_a_credit else 'No'}<br>
<b style="color: #8b5cf6; font-weight: 700;">Occupation:</b> {profile_a_occ}
</div>
</div>"""
        st.markdown(card_a, unsafe_allow_html=True)
    
    with summary_col2:
        card_b = f"""<div class="pro-card" style="border: 2px solid rgba(6, 182, 212, 0.4);">
<div style="text-align: center; margin-bottom: 25px;"><span class="profile-badge badge-success">Profile B Results</span></div>
<div style="background: rgba(6, 182, 212, 0.15); padding: 25px; border-radius: 12px; margin-bottom: 20px; text-align: center; border: 1px solid rgba(6, 182, 212, 0.2);">
<div style="font-size: 4rem; font-weight: 800; color: #ffffff; margin: 10px 0; background: linear-gradient(90deg, #10b981, #06b6d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{profile_b_p:.1f}<span style="font-size: 1.5rem;">th</span></div>
<div style="color: #94a3b8; font-size: 0.95rem; font-weight: 700; letter-spacing: 1px;">PERCENTILE</div>
</div>"""
        if profile_b_pov:
            card_b += f"""<div style='text-align: center; background: rgba(16, 185, 129, 0.1); padding: 10px; border-radius: 20px; border: 1px solid rgba(16, 185, 129, 0.3); margin-bottom: 20px;'><span style='color: #34d399; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;'>Live: {profile_b_pov['status']}</span></div>"""
        card_b += f"""<div style="line-height: 2.2; color: #e2e8f0; font-size: 0.95rem;">
<b style="color: #10b981; font-weight: 700;">Country:</b> {profile_b_country}<br>
<b style="color: #10b981; font-weight: 700;">Education:</b> {profile_b_edu} years<br>
<b style="color: #10b981; font-weight: 700;">Digital:</b> {profile_b_digital}%<br>
<b style="color: #10b981; font-weight: 700;">Gender:</b> {profile_b_gender}<br>
<b style="color: #10b981; font-weight: 700;">Location:</b> {profile_b_location}<br>
<b style="color: #10b981; font-weight: 700;">Credit:</b> {'Yes' if profile_b_credit else 'No'}<br>
<b style="color: #10b981; font-weight: 700;">Occupation:</b> {profile_b_occ}
</div>
</div>"""
        st.markdown(card_b, unsafe_allow_html=True)
    
    # Visual Comparison Dashboard
    st.markdown("---")
    st.markdown("### 🎯 Visual Comparison Dashboard")
    
    viz_comp_col1, viz_comp_col2, viz_comp_col3 = st.columns([1, 2, 1], gap="large")
    
    with viz_comp_col1:
        # Profile A Donut
        fig_donut_a = go.Figure(data=[go.Pie(
            values=[profile_a_p, 100-profile_a_p],
            hole=0.7,
            marker=dict(colors=['#3b82f6', 'rgba(59, 130, 246, 0.1)'], line=dict(color='#0f1419', width=2)),
            textinfo='none',
            hoverinfo='skip',
            showlegend=False
        )])
        fig_donut_a.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            height=250,
            margin=dict(t=10, b=10, l=10, r=10),
            annotations=[
                dict(text=f"<b>{profile_a_p:.0f}%</b>", x=0.5, y=0.55, font=dict(size=36, color='#60a5fa'), showarrow=False),
                dict(text="Profile A", x=0.5, y=0.35, font=dict(size=14, color='#8b98a5'), showarrow=False)
            ]
        )
        st.plotly_chart(fig_donut_a, use_container_width=True)
    
    with viz_comp_col2:
        # Difference indicator
        diff = profile_b_p - profile_a_p
        diff_color = "#10b981" if diff > 0 else "#ef4444" if diff < 0 else "#8b98a5"
        diff_icon = "📈" if diff > 0 else "📉" if diff < 0 else "➡️"
        diff_text = "Better" if diff > 0 else "Worse" if diff < 0 else "Same"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 40px; background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(16, 185, 129, 0.1)); border-radius: 16px; border: 2px solid {diff_color};">
            <div style="font-size: 4rem; margin-bottom: 15px;">{diff_icon}</div>
            <div style="font-size: 3rem; font-weight: 900; color: {diff_color}; margin: 15px 0;">
                {'+' if diff > 0 else ''}{diff:.1f}
            </div>
            <div style="color: #8b98a5; font-size: 1rem; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px;">Percentile Points</div>
            <div style="color: #e2e8f0; font-size: 1.3rem; font-weight: 600;">Profile B is {diff_text}</div>
            <div style="color: #8b98a5; font-size: 0.9rem; margin-top: 15px;">
                {f"Profile B ranks {abs(diff):.1f} points higher" if diff > 0 else f"Profile A ranks {abs(diff):.1f} points higher" if diff < 0 else "Both profiles are equal"}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with viz_comp_col3:
        # Profile B Donut
        fig_donut_b = go.Figure(data=[go.Pie(
            values=[profile_b_p, 100-profile_b_p],
            hole=0.7,
            marker=dict(colors=['#10b981', 'rgba(16, 185, 129, 0.1)'], line=dict(color='#0f1419', width=2)),
            textinfo='none',
            hoverinfo='skip',
            showlegend=False
        )])
        fig_donut_b.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            height=250,
            margin=dict(t=10, b=10, l=10, r=10),
            annotations=[
                dict(text=f"<b>{profile_b_p:.0f}%</b>", x=0.5, y=0.55, font=dict(size=36, color='#34d399'), showarrow=False),
                dict(text="Profile B", x=0.5, y=0.35, font=dict(size=14, color='#8b98a5'), showarrow=False)
            ]
        )
        st.plotly_chart(fig_donut_b, use_container_width=True)
    
    # Detailed factor comparison
    st.markdown('<p class="section-header" style="margin-top: 50px;">📋 Detailed Factor-by-Factor Breakdown</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94a3b8; font-size: 1.1rem; margin-bottom: 25px;">Comparing the specific weight of each attribute across both simulated profiles.</p>', unsafe_allow_html=True)
    
    # Create comparison dataframe
    comparison_data = []
    for factor in profile_a_components.keys():
        comparison_data.append({
            "Factor": factor,
            "Profile A": f"{profile_a_components[factor]:+.1f}",
            "Profile B": f"{profile_b_components[factor]:+.1f}",
            "Difference": f"{profile_b_components[factor] - profile_a_components[factor]:+.1f}"
        })
    
    comp_df = pd.DataFrame(comparison_data)
    st.dataframe(comp_df, use_container_width=True, hide_index=True)
    
    # Multi-dimensional radar chart comparison
    st.markdown('<p class="section-header" style="margin-top: 50px;">🕸️ Multi-Dimensional Score Comparison</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94a3b8; font-size: 1.1rem; margin-bottom: 25px;">Visualizing the relative strengths and trade-offs of both profiles across five key dimensions.</p>', unsafe_allow_html=True)
    
    categories = ['Education\n(Years)', 'Digital Skills\n(%)', 'Occupation\n(Points)', 'Urban\n(Points)', 'Credit\n(Points)']
    
    # Normalize to 0-100 scale for better visualization
    def normalize_value(value, max_val):
        return (value / max_val) * 100 if max_val > 0 else 0
    
    profile_a_normalized = [
        normalize_value(profile_a_edu, 20),  # Education out of 20
        profile_a_digital,  # Already 0-100
        normalize_value(profile_a_components['Occupation'], 15),  # Occupation max is 15
        normalize_value(profile_a_components['Urban Advantage'], 12),  # Urban max is 12
        normalize_value(profile_a_components['Credit Access'], 6)  # Credit max is 6
    ]
    
    profile_b_normalized = [
        normalize_value(profile_b_edu, 20),
        profile_b_digital,
        normalize_value(profile_b_components['Occupation'], 15),
        normalize_value(profile_b_components['Urban Advantage'], 12),
        normalize_value(profile_b_components['Credit Access'], 6)
    ]
    
    fig_radar = go.Figure()
    
    fig_radar.add_trace(go.Scatterpolar(
        r=profile_a_normalized,
        theta=categories,
        fill='toself',
        name='Profile A',
        line=dict(color='#3b82f6', width=3),
        fillcolor='rgba(59, 130, 246, 0.3)',
        hovertemplate='<b>%{theta}</b><br>Score: %{r:.1f}/100<extra></extra>'
    ))
    
    fig_radar.add_trace(go.Scatterpolar(
        r=profile_b_normalized,
        theta=categories,
        fill='toself',
        name='Profile B',
        line=dict(color='#10b981', width=3),
        fillcolor='rgba(16, 185, 129, 0.3)',
        hovertemplate='<b>%{theta}</b><br>Score: %{r:.1f}/100<extra></extra>'
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 100],
                tickmode='linear',
                tick0=0,
                dtick=20,
                gridcolor='rgba(255,255,255,0.15)',
                tickfont=dict(size=11, color='#8b98a5')
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.15)',
                tickfont=dict(size=12, color='#e2e8f0')
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', family='Inter'),
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=-0.15, 
            xanchor="center", 
            x=0.5,
            bgcolor='rgba(30, 37, 50, 0.8)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1,
            font=dict(size=13)
        ),
        margin=dict(t=40, b=80, l=80, r=80)
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)
    
# ============= HISTORICAL SNAPSHOT MODE =============
else:
    st.markdown('<p class="section-header">⏳ Step 2: Configure Historical Comparison</p>', unsafe_allow_html=True)
    
    st.markdown("""<div class="historical-card">
<h3 style="text-align: center; color: #f59e0b; margin-bottom: 10px;">🗓️ Historical Evolution Tool</h3>
<p style="text-align: center; color: #8b98a5; margin-bottom: 20px;">Observe how the <b>same profile attributes</b> would result in different social standings across two distinct time periods.</p>
</div>""", unsafe_allow_html=True)

    # SHARED ATTRIBUTES FOR BOTH YEARS
    st.markdown("#### 🛠️ Fixed Profile Attributes")
    col_attr1, col_attr2 = st.columns([2, 1], gap="large")
    
    with col_attr1:
        st.markdown('<div class="input-group-label">🌍 Country Selection</div>', unsafe_allow_html=True)
        h_country = st.selectbox("Compare data for:", list(COUNTRY_DATA.keys()), key="h_country", label_visibility="collapsed")
        
        st.markdown('<div class="input-group-label" style="margin-top: 25px;">🛠️ Profile Attributes</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            h_edu = st.slider("Education (yrs)", 0, 20, 12, key="h_edu")
            h_gender = st.selectbox("Gender", ["Male", "Female"], key="h_gender")
        with c2:
            h_digital = st.slider("Digital Skills (%)", 0, 100, 50, key="h_digital")
            h_loc = st.selectbox("Location", ["Rural", "Urban"], key="h_loc")
        
        st.markdown('<div class="input-group-label" style="margin-top: 25px;">💼 Primary Sector</div>', unsafe_allow_html=True)
        h_occ = st.selectbox("Occupation", ["Agriculture", "Industry", "Services", "Public Sector", "Unemployed"], index=2, key="h_occ", label_visibility="collapsed")

    with col_attr2:
        st.markdown(f"""
        <div class="pro-card" style="border: 1px solid rgba(245, 158, 11, 0.3);">
            <div class="input-group-label" style="text-align: center; margin-bottom: 20px; color: #f59e0b;">⏳ Select Eras</div>
            <div style="line-height: 2.5; color: #e2e8f0; font-size: 0.95rem;">
                <b style="color: #f59e0b; font-weight: 700;">Start Year:</b> 2000 (Base)<br>
                <b style="color: #f59e0b; font-weight: 700;">End Year:</b> 2023 (Current)
            </div>
            <p style="font-size: 0.85rem; color: #94a3b8; margin-top: 15px;">The simulator compares your profile across these two distinct economic eras.</p>
        </div>
        """, unsafe_allow_html=True)
        # Get year range from data
        year_1 = st.selectbox("Select Year 1 (Baseline)", list(range(2000, 2024)), index=1, key="year_1")
        year_2 = st.selectbox("Select Year 2 (Comparison)", list(range(2000, 2024)), index=23, key="year_2")
        
        st.markdown(f"""
        <div style="margin-top: 30px; padding: 15px; background: rgba(245, 158, 11, 0.1); border-radius: 8px; border-left: 4px solid #f59e0b;">
            <p style="font-size: 0.9rem; color: #e2e8f0; margin: 0;">
                Comparing <b>{h_country}</b> in <b>{year_1}</b> vs <b>{year_2}</b>.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # CALCULATIONS
    h_g_val = 1 if h_gender == "Female" else 0
    h_u_val = 1 if h_loc == "Urban" else 0
    
    p1, comp1 = calculate_historical_percentile(h_country, year_1, h_edu, h_digital, h_g_val, h_u_val, h_occ, False, "Adult")
    p2, comp2 = calculate_historical_percentile(h_country, year_2, h_edu, h_digital, h_g_val, h_u_val, h_occ, False, "Adult")
    
    # RESULTS
    st.markdown('<p class="section-header">📊 Step 3: Social Standing Evolution</p>', unsafe_allow_html=True)
    
    res_col1, res_col2 = st.columns(2, gap="large")
    
    with res_col1:
        st.markdown(f'<div style="text-align: center; color: #8b98a5; margin-bottom: 10px;">POSITION IN {year_1}</div>', unsafe_allow_html=True)
        st.plotly_chart(render_gauge(p1, f"Standing in {year_1}", height=280), use_container_width=True)
        
    with res_col2:
        st.markdown(f'<div style="text-align: center; color: #8b98a5; margin-bottom: 10px;">POSITION IN {year_2}</div>', unsafe_allow_html=True)
        st.plotly_chart(render_gauge(p2, f"Standing in {year_2}", height=280), use_container_width=True)

    # EVOLUTION DASHBOARD
    evol_diff = p2 - p1
    evol_color = "#10b981" if evol_diff > 0 else "#ef4444" if evol_diff < 0 else "#8b98a5"
    evol_trend = "Social Mobility ↑" if evol_diff > 0 else "Standing Declined ↓" if evol_diff < 0 else "Stagnant ➡️"
    
    st.markdown(f"""
    <div style="background: rgba(30, 37, 50, 0.6); padding: 30px; border-radius: 16px; border: 1px solid #2f3336; text-align: center; margin: 20px 0;">
        <div style="font-size: 1.2rem; color: #8b98a5; text-transform: uppercase; letter-spacing: 2px;">Change in Percentile Ranking</div>
        <div style="font-size: 4.5rem; font-weight: 800; color: {evol_color}; margin: 10px 0;">{evol_diff:+.1f}</div>
        <div style="font-size: 1.5rem; font-weight: 600; color: {evol_color};">{evol_trend}</div>
        <p style="color: #94a3b8; max-width: 600px; margin: 20px auto 0 auto;">
            A change of <b>{abs(evol_diff):.1f} percentile points</b> suggests that having these specific attributes 
            in {year_2} makes you relatively <b>{"better" if evol_diff > 0 else "worse"} off</b> compared to others in 
            {h_country} than it did in {year_1}.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # WATERFALL CHART FOR DECOMPOSITION
    st.markdown("### 🌊 Why did your ranking change?")
    st.markdown(f'<p style="color: #8b98a5; font-size: 0.9rem; margin-bottom: 20px;">This waterfall chart breaks down how shifting economic conditions in {h_country} changed the "value" of your specific profile from {year_1} to {year_2}.</p>', unsafe_allow_html=True)
    
    waterfall_factors = list(comp1.keys())
    waterfall_diffs = [comp2[f] - comp1[f] for f in waterfall_factors]
    
    fig_waterfall = go.Figure(go.Waterfall(
        name="Social Shift", orientation="v",
        measure=["absolute"] + ["relative"] * len(waterfall_factors) + ["total"],
        x=[f"Position in {year_1}"] + waterfall_factors + [f"Position in {year_2}"],
        textposition="outside",
        text=[f"{p1:.1f}"] + [f"{d:+.1f}" for d in waterfall_diffs] + [f"{p2:.1f}"],
        y=[p1] + waterfall_diffs + [0],
        connector={"line": {"color": "rgba(139, 152, 165, 0.5)", "width": 1, "dash": "dot"}},
        increasing={"marker": {"color": "#10b981"}},
        decreasing={"marker": {"color": "#ef4444"}},
        totals={"marker": {"color": "#3b82f6"}}
    ))

    fig_waterfall.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', family='Inter'),
        height=500,
        margin=dict(t=40, b=20, l=20, r=20),
        yaxis=dict(title="Percentile Ranking", showgrid=True, gridcolor='rgba(255,255,255,0.05)', range=[0, 100]),
        showlegend=False
    )
    
    st.plotly_chart(fig_waterfall, use_container_width=True)

    # LINE CHART FOR HISTORICAL TREND
    st.markdown("### 📈 Social Standing Evolution (2000 - 2023)")
    st.markdown(f'<p style="color: #8b98a5; font-size: 0.9rem; margin-bottom: 20px;">Tracking how the <b>exact same profile</b> would have ranked in {h_country} across two decades of economic change.</p>', unsafe_allow_html=True)
    
    # Calculate trend data
    trend_years = list(range(2000, 2024))
    trend_scores = []
    for y in trend_years:
        score, _ = calculate_historical_percentile(h_country, y, h_edu, h_digital, 1 if h_gender == "Female" else 0, 1 if h_loc == "Urban" else 0, h_occ)
        trend_scores.append(score)
    
    df_trend = pd.DataFrame({"Year": trend_years, "Percentile": trend_scores})
    
    fig_trend = px.line(df_trend, x="Year", y="Percentile", markers=False)
    
    # Highlight Year 1 and Year 2
    highlight_years = [year_1, year_2]
    highlight_scores = [p1, p2]
    
    fig_trend.add_scatter(
        x=highlight_years, 
        y=highlight_scores,
        mode='markers+text',
        marker=dict(size=14, color=[evol_color if y == year_2 else "#3b82f6" for y in highlight_years], symbol='circle', line=dict(width=2, color='white')),
        text=[f"{y}" for y in highlight_years],
        textposition="top center",
        name="Selected Eras",
        hovertemplate="<b>%{x}</b><br>Percentile: %{y:.1f}<extra></extra>"
    )

    fig_trend.update_traces(line=dict(width=4, color='#8b5cf6', shape='spline'))
    
    fig_trend.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', family='Inter'),
        height=450,
        margin=dict(t=20, b=20, l=20, r=20),
        xaxis=dict(
            title="Year", 
            showgrid=True, 
            gridcolor='rgba(255,255,255,0.05)',
            dtick=2
        ),
        yaxis=dict(
            title="Relative Economic Percentile", 
            showgrid=True, 
            gridcolor='rgba(255,255,255,0.1)',
            range=[0, 100]
        ),
        showlegend=False
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)


    
    st.info(f"💡 **Analysis:** Between {year_1} and {year_2}, {h_country}'s economic landscape transformed significantly. In {year_1}, with lower internet penetration and schooling rates, your profile attributes were far more 'exclusive', granting a higher relative bonus. By {year_2}, as these resources became more common, the 'scarcity premium' for basic education and digital access declined, but the overall economic floor (Base Strength) rose due to GDP growth.")
    
    # ERA COMPARISON TABLE
    st.markdown('<p class="section-header" style="margin-top: 50px;">🏛️ Deep Era Analysis</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94a3b8; font-size: 1.1rem; margin-bottom: 25px;">Comparing the socio-economic reality of the selected profile across two distinct points in time.</p>', unsafe_allow_html=True)
    era_col1, era_col2 = st.columns(2)
    
    with era_col1:
        st.markdown(f"""<div style="background: rgba(139, 92, 246, 0.08); padding: 20px; border-radius: 12px; border: 1px solid rgba(139, 92, 246, 0.3);">
<h5 style="color: #8b5cf6; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">The {year_1} Context</h5>
<p style="font-size: 0.9rem; color: #94a3b8;">
In this era, a person with your profile was an <b>outlier</b>. Low national averages meant your education and skills placed you in an elite bracket. 
Economic opportunities were concentrated, making your "scarcity value" exceptionally high.
</p>
</div>""", unsafe_allow_html=True)
        
    with era_col2:
        st.markdown(f"""<div style="background: rgba(16, 185, 129, 0.08); padding: 20px; border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.3);">
<h5 style="color: #10b981; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">The {year_2} Progress</h5>
<p style="font-size: 0.9rem; color: #94a3b8;">
By {year_2}, the middle class had expanded. Your skills are now more <b>standardized</b>. While the country is wealthier (higher base), 
you face more competition from others with similar profiles, requiring higher specialization to maintain the same relative lead.
</p>
</div>""", unsafe_allow_html=True)

# Footer
st.divider()
st.markdown(textwrap.dedent("""
<div style="text-align: center; color: #8b98a5; font-size: 0.85rem; padding: 20px 0;">
    <b>Income Simulator v5.0</b> | Modernized with Mode Selection, Independent Profile Inputs & Enhanced Comparison Tools<br>
    Calibrated for South Asian socio-economic contexts | Educational purposes only
</div>
"""), unsafe_allow_html=True)