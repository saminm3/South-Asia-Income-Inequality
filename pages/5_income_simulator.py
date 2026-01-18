import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from pathlib import Path
<<<<<<< Updated upstream
from utils.exports import export_plot_menu

# Page config
=======
from utils.help_system import render_help_button
from utils.sidebar import apply_all_styles
from utils.enhanced_loaders import (
    load_wdi_data, 
    load_education_data, 
    load_jobs_data, 
    get_latest_indicator_value
)
>>>>>>> Stashed changes
st.set_page_config(
    page_title="Income Simulator",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
try:
    with open('assets/dashboard.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Custom CSS for Professional Look
st.markdown("""
<style>
    /* ==================== SIMULATOR SPECIFIC STYLES ==================== */
    
    /* Card Components */
    .simulator-pro-card {
        background: linear-gradient(135deg, rgba(30, 37, 50, 0.95) 0%, rgba(26, 31, 46, 0.95) 100%);
        border-radius: 16px;
        padding: 28px;
        border: 1px solid rgba(29, 155, 240, 0.2);
        margin-bottom: 24px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .simulator-pro-card:hover {
        border-color: rgba(29, 155, 240, 0.4);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        transform: translateY(-2px);
    }
    
    /* Input Labels */
    .simulator-input-label {
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
        font-weight: 700;
        display: block;
    }
    
    /* Result Display Container */
    .simulator-result-container {
        text-align: center;
        padding: 40px 30px;
        background: linear-gradient(135deg, rgba(29, 155, 240, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%);
        border-radius: 20px;
        border: 2px solid rgba(29, 155, 240, 0.3);
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    .simulator-metric-value-large {
        font-size: 4.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #1d9bf0 0%, #00ba7c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
        margin: 10px 0;
    }
    
    .simulator-metric-label {
        color: #94a3b8;
        text-transform: uppercase;
        font-size: 0.95rem;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    .simulator-metric-group {
        font-size: 1.6rem;
        font-weight: 700;
        margin-top: 15px;
    }
    
    /* Insight Panels */
    .simulator-insight-panel {
        background: rgba(29, 155, 240, 0.08);
        border-left: 4px solid #1d9bf0;
        padding: 24px;
        border-radius: 0 12px 12px 0;
        margin-bottom: 18px;
        transition: all 0.2s ease;
    }
    
    .simulator-insight-panel:hover {
        background: rgba(29, 155, 240, 0.12);
        transform: translateX(4px);
    }
    
    .simulator-insight-panel-success {
        background: rgba(16, 185, 129, 0.08);
        border-left: 4px solid #10b981;
        padding: 24px;
        border-radius: 0 12px 12px 0;
        margin-bottom: 18px;
        transition: all 0.2s ease;
    }
    
    .simulator-insight-panel-success:hover {
        background: rgba(16, 185, 129, 0.12);
        transform: translateX(4px);
    }
    
    .simulator-insight-panel-warning {
        background: rgba(245, 158, 11, 0.08);
        border-left: 4px solid #f59e0b;
        padding: 24px;
        border-radius: 0 12px 12px 0;
        margin-bottom: 18px;
        transition: all 0.2s ease;
    }
    
    .simulator-insight-panel-warning:hover {
        background: rgba(245, 158, 11, 0.12);
        transform: translateX(4px);
    }
    
    .simulator-insight-title {
        color: #ffffff;
        font-weight: 700;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.15rem;
    }
    
    /* Section Headers */
    .simulator-section-header {
        font-size: 1.5rem;
        font-weight: 800;
        color: #ffffff;
        margin: 40px 0 20px 0;
        padding-bottom: 12px;
        border-bottom: 3px solid rgba(29, 155, 240, 0.4);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Comparison Card */
    .simulator-comparison-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.12), rgba(16, 185, 129, 0.12));
        border: 2px solid rgba(59, 130, 246, 0.4);
        border-radius: 20px;
        padding: 36px;
        margin: 24px 0;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
    }
    
    /* Profile Badges */
    .simulator-profile-badge {
        display: inline-block;
        padding: 10px 20px;
        border-radius: 24px;
        font-weight: 800;
        font-size: 0.9rem;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    .simulator-badge-primary {
        background: linear-gradient(135deg, #3b82f6 0%, #1d9bf0 100%);
        color: white;
    }
    
    .simulator-badge-success {
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
        color: white;
    }
    
    /* Profile Summary Box */
    .simulator-profile-summary {
        background: rgba(30, 37, 50, 0.6);
        border: 1px solid rgba(29, 155, 240, 0.3);
        border-radius: 12px;
        padding: 20px;
        line-height: 2.2;
    }
    
    /* Recommendation Box */
    .simulator-recommendation-box {
        background: rgba(255, 255, 255, 0.04);
        padding: 18px;
        border-radius: 10px;
        margin-bottom: 14px;
        border-left: 3px solid;
        transition: all 0.2s ease;
    }
    
    .simulator-recommendation-box:hover {
        background: rgba(255, 255, 255, 0.06);
        transform: translateX(4px);
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .simulator-metric-value-large {
            font-size: 3rem;
        }
        
        .simulator-section-header {
            font-size: 1.2rem;
        }
        
        .simulator-comparison-card {
            padding: 20px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Data-driven Country Context Generator
@st.cache_data
def get_data_driven_country_data():
    """Build dynamic country parameters from real WDI, Education, and Jobs data"""
    countries = ['Bangladesh', 'India', 'Pakistan', 'Nepal', 'Sri Lanka', 'Afghanistan', 'Bhutan', 'Maldives']
    dynamic_data = {}
    
    for country in countries:
        # Default fallback values
        literacy = get_latest_indicator_value(country, 'education', 'SE.ADT.LITR.ZS') or 65.0
        edu_exp = get_latest_indicator_value(country, 'education', 'SE.XPD.TOTL.GD.ZS') or 3.5
        urban_elec = get_latest_indicator_value(country, 'jobs', 'EG.ELC.ACCS.UR.ZS') or 98.0
        rural_elec = get_latest_indicator_value(country, 'jobs', 'EG.ELC.ACCS.RU.ZS') or 80.0
        female_labor = get_latest_indicator_value(country, 'jobs', 'SL.TLF.CACT.FE.ZS') or 30.0
        poverty = get_latest_indicator_value(country, 'wdi', 'SI.POV.NAHC') or 20.0
        
        # 1. Base Score: Increases with literacy, decreases with poverty
        # A country with 100% literacy and 0% poverty would have a base of ~35
        # A country with 50% literacy and 40% poverty would have a base of ~15
        base = 10 + (literacy / 5) - (poverty / 10)
        base = max(15, min(35, base))
        
        # 2. Education Weight: Increases with government education expenditure % of GDP
        # Higher investment usually translates to higher returns on education in the job market
        weight = 0.2 + (edu_exp / 15)
        weight = max(0.25, min(0.45, weight))
        
        # 3. Urban Bonus: Higher if there's a big gap between urban and rural infra (electricity)
        elec_gap = max(0, urban_elec - rural_elec)
        bonus = 4 + (elec_gap / 4)
        bonus = max(6, min(14, bonus))
        
        # 4. Gender Penalty: Lower if female labor participation is high
        penalty = -12 + (female_labor / 10)
        penalty = max(-10, min(-4, penalty))
        
        dynamic_data[country] = {
            'base': base,
            'education_weight': weight,
            'urban_bonus': bonus,
            'gender_penalty': penalty,
            'raw_stats': {
                'Literacy': literacy,
                'Edu Exp (% GDP)': edu_exp,
                'Poverty Headcount': poverty,
                'Female Labor Force %': female_labor
            }
        }
    
    return dynamic_data

# Initialize Data-Driven Parameters
COUNTRY_DATA = get_data_driven_country_data()

def calculate_percentile(country, edu, digital, gender, urban, occupation="Services", credit=False, age="Adult"):
    """Calculate economic percentile using data-driven dynamic weights"""
    data = COUNTRY_DATA.get(country, COUNTRY_DATA['India'])
    base = data['base']
    weight = data['education_weight']
    bonus = data['urban_bonus']
    gender_pen = data['gender_penalty']
    
    # Occupation impact (anchored in regional employment trends)
    occ_map = {"Agriculture": 0, "Industry": 8, "Services": 12, "Public Sector": 15, "Unemployed": -5}
    occ_val = occ_map.get(occupation, 10)
    
    # Credit access (Modern banking/Fintech impact)
    credit_val = 7 if credit else 0
    
    # Age factor (Experience vs Entry-level)
    age_map = {"Youth (<25)": -3, "Adult (25-60)": 7, "Senior (>60)": 3}
    age_val = age_map.get(age, 5)
    
    # Core calculations
    # Education: Max weight scaled by years (out of 20)
    edu_contrib = (edu / 20) * 45 * weight
    # Digital: Standardized impact of tech literacy
    digital_contrib = (digital / 100) * 15
    # Gender: Penalty derived from regional labor parity
    gender_contrib = gender * gender_pen
    # Urbanization: Bonus derived from infrastructure gaps
    urban_contrib = urban * bonus
    
    raw_percentile = base + edu_contrib + digital_contrib + gender_contrib + urban_contrib + occ_val + credit_val + age_val
    
    components = {
        "Base Value (Macro Context)": base,
        "Education Returns": edu_contrib,
        "Digital Advantage": digital_contrib,
        "Occupation Premium": occ_val,
        "Urban Infrastructure Bonus": urban_contrib,
        "Credit/Bank Access": credit_val,
        "Age & Experience": age_val,
        "Gender-based Inequality": gender_contrib 
    }
    
    return max(1, min(99, raw_percentile)), components

def get_tercile(p):
    if p < 33.33: return "Lower Tercile", "#ef4444"
    if p < 66.66: return "Middle Tercile", "#f59e0b"
    return "Upper Tercile", "#10b981"

def render_gauge(p, title="", height=360):
    # Determine gradient color based on value
    if p < 33.33:
        bar_color = "#ef4444"  # Red
    elif p < 66.66:
        bar_color = "#f59e0b"  # Orange
    else:
        bar_color = "#10b981"  # Green
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=p,
        number={
            'font': {'size': 64, 'color': '#ffffff', 'family': 'Inter, sans-serif'},
            'suffix': '<span style="font-size:32px; color: #94a3b8;">th</span>'
        },
        title={
            'text': title, 
            'font': {'size': 18, 'color': '#e2e8f0', 'family': 'Inter, sans-serif'}
        },
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 2,
                'tickcolor': "#64748b",
                'tickfont': {'size': 14, 'color': '#94a3b8', 'family': 'Inter, sans-serif'},
                'tickmode': 'array',
                'tickvals': [0, 20, 40, 60, 80, 100],
                'showticklabels': True
            },
            'bar': {'color': 'rgba(0,0,0,0)', 'thickness': 0},  # Hide the default bar
            'bgcolor': "rgba(30, 37, 50, 0.4)",
            'borderwidth': 2,
            'bordercolor': "rgba(100, 116, 139, 0.4)",
            'steps': [
                {'range': [0, 25], 'color': "#dc2626"},      # Red
                {'range': [25, 50], 'color': "#fb923c"},     # Orange  
                {'range': [50, 75], 'color': "#fbbf24"},     # Yellow
                {'range': [75, 100], 'color': "#3b82f6"}     # Blue
            ],
            'threshold': {
                'line': {
                    'color': "#000000",  # Black needle
                    'width': 14  # Much thicker needle
                },
                'thickness': 1.0,  # Maximum thickness for bold appearance
                'value': p
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "#e2e8f0", 'family': 'Inter, sans-serif'},
        height=height,
        margin=dict(l=60, r=60, t=80, b=50)
    )
    
    return fig

def generate_insights(sp_p, breakdown_components, sp_country, sp_gender, sp_location, sp_occ, sp_credit, sp_edu, sp_digital):
    """Generate plain-language insights"""
    insights = []
    
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
    edu_contrib = breakdown_components['Education Returns']
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
        gender_impact = abs(breakdown_components['Gender-based Inequality'])
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
            "text": f"Living urban gives you {breakdown_components['Urban Infrastructure Bonus']:.0f} extra points from concentrated economic opportunities."
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
            "text": f"Lack of credit access costs 7 points. Without banking, you can't save safely, build credit, get loans, or invest. Opening an account is easiest improvement."
        })
    else:
        insights.append({
            "type": "success", "icon": "🏦", "title": "Financial Inclusion Advantage",
            "text": f"Credit access adds 7 points, enabling investment in assets, handling emergencies, and building financial security."
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

st.markdown("""
<div class="dashboard-header">
    <h1 style="display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 2.5rem;">💸</span> Income Simulator
    </h1>
    <p>Understand how socio-economic factors shape your economic position in South Asia. Build your profile, run the simulation, and get personalized insights in plain language.</p>
</div>
""", unsafe_allow_html=True)

# Methodology
with st.expander("🔬 How Does This Simulator Work?", expanded=False):
    st.markdown("""
    ### Calculation Methodology
    
    This simulator uses a **data-driven multi-factor regression model** calibrated using real World Bank indicators (WDI, Education, and Jobs). 
    
    **The Data-Driven Difference:**
    Unlike simple calculators, our model's weights change dynamically based on:
    - **Macro Base Scores**: Derived from literacy rates and national poverty headcount.
    - **Education Returns**: Weights adjusted by national expenditure on education.
    - **Infrastructure Premiums**: Urban bonuses calculated from urban-rural electricity access gaps.
    - **Gender Adjustments**: Structural penalties based on female labor force participation.
    
    **The Formula:**
    ```
    Economic Position = Base(Country Data) + Education(Weighted) + Digital Skills + 
                       Gender(Waithed) + Urban/Rural(Gap-driven) + Occupation + 
                       Credit Access + Age
    ```
    
    **Note:** This is a simplified educational model based on macroeconomic indicators. Real individual income varies by employer, specific skills, and micro-market conditions.
    """)

# ============= STEP 1: PROFILE =============

st.markdown('<p class="simulator-section-header">📝 Step 1: Build Your Profile</p>', unsafe_allow_html=True)

col_input, col_preview = st.columns([2, 1], gap="large")

with col_input:
    # Country Selection
    st.markdown('<div class="simulator-input-label">🌍 Country</div>', unsafe_allow_html=True)
    sp_country = st.selectbox("Select your country", list(COUNTRY_DATA.keys()), key="sp_country", label_visibility="collapsed")
    
    st.markdown("---")
    
    # Education & Skills
    st.markdown('<div class="simulator-input-label">🎓 Education & Skills</div>', unsafe_allow_html=True)
    col_edu1, col_edu2 = st.columns(2)
    with col_edu1:
        sp_edu = st.slider("Years of Formal Education", 0, 20, 12, key="sp_edu")
    with col_edu2:
        sp_digital = st.slider("Digital Proficiency (%)", 0, 100, 50, key="sp_digital")
    
    st.markdown("---")
    
    # Demographics
    st.markdown('<div class="simulator-input-label">👤 Demographics</div>', unsafe_allow_html=True)
    col_demo1, col_demo2 = st.columns(2)
    with col_demo1:
        sp_gender = st.selectbox("Gender", ["Male", "Female"], key="sp_gender")
        sp_age = st.selectbox("Age Group", ["Youth (<25)", "Adult (25-60)", "Senior (>60)"], index=1, key="sp_age")
    with col_demo2:
        sp_location = st.selectbox("Location Type", ["Rural", "Urban"], key="sp_location")
        sp_credit = st.checkbox("Has Bank Account / Credit Access", value=False, key="sp_credit")
    
    st.markdown("---")
    
    # Occupation
    st.markdown('<div class="simulator-input-label">💼 Occupation</div>', unsafe_allow_html=True)
    sp_occ = st.selectbox("Primary Work Sector", ["Agriculture", "Industry", "Services", "Public Sector", "Unemployed"], index=2, key="sp_occ", label_visibility="collapsed")

with col_preview:
    st.markdown("### 👤 Your Profile")
    st.markdown(f"""
    <div class="simulator-profile-summary">
        <b style="color: #1d9bf0;">Country:</b> {sp_country}<br>
        <b style="color: #1d9bf0;">Education:</b> {sp_edu} years<br>
        <b style="color: #1d9bf0;">Digital Skills:</b> {sp_digital}%<br>
        <b style="color: #1d9bf0;">Gender:</b> {sp_gender}<br>
        <b style="color: #1d9bf0;">Age:</b> {sp_age}<br>
        <b style="color: #1d9bf0;">Location:</b> {sp_location}<br>
        <b style="color: #1d9bf0;">Credit:</b> {'Yes ✓' if sp_credit else 'No ✗'}<br>
        <b style="color: #1d9bf0;">Occupation:</b> {sp_occ}
    </div>
    """, unsafe_allow_html=True)

# Calculate
g_val = 1 if sp_gender == "Female" else 0
u_val = 1 if sp_location == "Urban" else 0
sp_p, breakdown_components = calculate_percentile(sp_country, sp_edu, sp_digital, g_val, u_val, sp_occ, sp_credit, sp_age)


# ============= STEP 2: RESULTS + INSIGHTS =============

st.markdown('<p class="simulator-section-header">📊 Step 2: Your Simulation Results</p>', unsafe_allow_html=True)

group, color = get_tercile(sp_p)

result_col1, result_col2 = st.columns([1, 1], gap="large")

with result_col1:
    st.markdown(f"""
    <div class="simulator-result-container">
        <p class="simulator-metric-label">Your Economic Percentile</p>
        <div class="simulator-metric-value-large">{sp_p:.1f}<span style="font-size:2rem; vertical-align:super;">th</span></div>
        <div class="simulator-metric-group" style="color: {color};">{group}</div>
        <p style="color: #e2e8f0; margin-top: 20px; font-size: 1.05rem; line-height: 1.6;">
            This means you rank <b>higher than {sp_p:.1f}%</b> of people in {sp_country}.<br><br>
            <span style="color: #8b98a5;">In simpler terms: Out of every 100 people, you'd be in a better economic position than about <b>{int(sp_p)}</b> of them.</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

with result_col2:
<<<<<<< Updated upstream
    fig_gauge = render_gauge(sp_p, "Your Economic Position", height=300)
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
    export_plot_menu(fig_gauge, "personal_economic_position", key="gauge_chart")

# ============= STEP 3: VISUALIZATIONS =============

st.markdown('<p class="section-header">🔍 Step 3: Understanding Your Score</p>', unsafe_allow_html=True)

viz_col1, viz_col2 = st.columns([1, 1], gap="large")

with viz_col1:
    st.markdown('<div class="pro-card">', unsafe_allow_html=True)
    st.markdown("### 🏗️ What's Building Your Score?")
    st.markdown('<p style="color: #8b98a5; font-size: 0.9rem; margin-bottom: 15px;">Size shows how much each factor adds. Bigger = more impact.</p>', unsafe_allow_html=True)
    
    tree_data = [{"Factor": k, "Contribution": v} for k, v in breakdown_components.items() if v > 0]
    
    if tree_data:
        df_tree = pd.DataFrame(tree_data)
        fig_tree = px.treemap(df_tree, path=['Factor'], values='Contribution', color='Contribution', color_continuous_scale='Tealgrn')
        fig_tree.update_traces(textinfo="label+value", textfont=dict(size=13, color='white'))
        fig_tree.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': '#e2e8f0'}, height=320, margin=dict(t=5, l=5, r=5, b=5))
        st.plotly_chart(fig_tree, use_container_width=True, config={'displayModeBar': False})
        export_plot_menu(fig_tree, "factor_contributions", key="tree_chart")
    
    st.markdown('</div>', unsafe_allow_html=True)

with viz_col2:
    st.markdown('<div class="pro-card">', unsafe_allow_html=True)
    st.markdown("### 📈 How Education Changes Everything")
    st.markdown('<p style="color: #8b98a5; font-size: 0.9rem; margin-bottom: 15px;">Shows how your position changes with education. Red star = you now.</p>', unsafe_allow_html=True)
    
    edu_range = list(range(0, 21, 2))
    scores_by_edu = []
    for e in edu_range:
        score, _ = calculate_percentile(sp_country, e, sp_digital, g_val, u_val, sp_occ, sp_credit, sp_age)
        scores_by_edu.append({"Education Years": e, "Percentile": score})
    
    df_edu = pd.DataFrame(scores_by_edu)
    fig_line = px.line(df_edu, x='Education Years', y='Percentile', markers=True)
    fig_line.add_scatter(x=[sp_edu], y=[sp_p], mode='markers', marker=dict(size=16, color='#ef4444', symbol='star'), name='You Are Here')
    fig_line.update_traces(line_color='#1d9bf0', line_width=3, selector=dict(mode='lines'))
    fig_line.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': '#e2e8f0'}, height=320,
        xaxis=dict(title="Years of Education", showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(title="Economic Percentile", showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        margin=dict(t=10, l=10, r=10, b=10)
    )
    st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})
    export_plot_menu(fig_line, "education_impact_trend", key="edu_line_chart")
    st.markdown('</div>', unsafe_allow_html=True)

# Factor table
st.markdown('<div class="pro-card">', unsafe_allow_html=True)
st.markdown("#### 📋 Detailed Factor Contribution")
factor_df = pd.DataFrame([
    {"Factor": k, "Points Added": f"{v:+.1f}", "Impact": "🟢 Positive" if v > 0 else ("🔴 Negative" if v < 0 else "⚪ Neutral")}
    for k, v in breakdown_components.items()
])
st.dataframe(factor_df, use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)

# ============= STEP 4: INSIGHTS =============

st.markdown('<p class="section-header">💡 Step 4: What This Means for You - Plain Language Insights</p>', unsafe_allow_html=True)
=======
    st.plotly_chart(render_gauge(sp_p, "Your Economic Position"), use_container_width=True)

# Insights Section
st.markdown('<p class="simulator-section-header">� What This Means for You - Plain Language Insights</p>', unsafe_allow_html=True)
>>>>>>> Stashed changes

insights, recommendations = generate_insights(sp_p, breakdown_components, sp_country, sp_gender, sp_location, sp_occ, sp_credit, sp_edu, sp_digital)

insight_cols = st.columns(2, gap="large")

for idx, insight in enumerate(insights):
    with insight_cols[idx % 2]:
        panel_class = f"simulator-insight-panel-{insight['type']}" if insight['type'] in ['success', 'warning'] else "simulator-insight-panel"
        st.markdown(f"""
        <div class="{panel_class}">
            <div class="simulator-insight-title">{insight['icon']} {insight['title']}</div>
            <p style="color: #e2e8f0; font-size: 0.95rem; line-height: 1.6; margin: 0;">{insight['text']}</p>
        </div>
        """, unsafe_allow_html=True)

# Recommendations
if recommendations:
    st.markdown('<p class="simulator-section-header">🎯 Personalized Recommendations</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: #8b98a5; margin-bottom: 15px;">Based on your profile, here are the most impactful actions to improve your economic position:</p>', unsafe_allow_html=True)
    
    for i, rec in enumerate(recommendations, 1):
        priority_color = "#ef4444" if rec['priority'] == "HIGH" else "#f59e0b"
        st.markdown(f"""
        <div class="simulator-recommendation-box" style="border-left-color: {priority_color};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <b style="color: #ffffff; font-size: 1.05rem;">{i}. {rec['action']}</b>
                <span style="background: {priority_color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">{rec['priority']}</span>
            </div>
            <p style="color: #e2e8f0; margin: 0; line-height: 1.6;">{rec['detail']}</p>
        </div>
        """, unsafe_allow_html=True)

# ============= STEP 3: COMPARISON FEATURE =============

st.markdown('<p class="simulator-section-header">🔄 Step 3: Profile Comparison Tool</p>', unsafe_allow_html=True)

# Add tabs for different comparison types
comparison_tab1, comparison_tab2 = st.tabs(["👥 Profile vs Profile", "📅 Same Profile Across Years"])

# ============= TAB 1: PROFILE VS PROFILE =============
with comparison_tab1:
    st.markdown("""
    <div class="simulator-comparison-card">
        <h3 style="text-align: center; color: #ffffff; margin-bottom: 10px;">Compare Two Different Profiles</h3>
        <p style="text-align: center; color: #8b98a5; margin-bottom: 30px;">Create two profiles to see how different factors affect economic outcomes</p>
    </div>
    """, unsafe_allow_html=True)

# Comparison inputs
comp_col1, comp_col2 = st.columns([1, 1], gap="large")

with comp_col1:
<<<<<<< Updated upstream
    # Completely remove all leading whitespace to prevent any markdown code-block triggers
    st.markdown(f"""
<div class="pro-card" style="border: 2px solid #3b82f6;">
<div style="text-align: center; margin-bottom: 20px;">
<span class="profile-badge badge-primary">Profile A (You)</span>
</div>
<div style="background: rgba(59, 130, 246, 0.1); padding: 20px; border-radius: 10px; margin-bottom: 15px;">
<div style="text-align: center;">
<div style="font-size: 3.5rem; font-weight: 800; color: #60a5fa; margin: 10px 0;">{sp_p:.1f}<span style="font-size: 1.5rem;">th</span></div>
<div style="color: #8b98a5; font-size: 0.9rem;">PERCENTILE</div>
</div>
</div>
<div style="line-height: 2; color: #e2e8f0; font-size: 0.9rem;">
<b style="color: #60a5fa;">Country:</b> {sp_country}<br>
<b style="color: #60a5fa;">Education:</b> {sp_edu} years<br>
<b style="color: #60a5fa;">Digital:</b> {sp_digital}%<br>
<b style="color: #60a5fa;">Gender:</b> {sp_gender}<br>
<b style="color: #60a5fa;">Location:</b> {sp_location}<br>
<b style="color: #60a5fa;">Credit:</b> {'Yes' if sp_credit else 'No'}<br>
<b style="color: #60a5fa;">Occupation:</b> {sp_occ}
</div>
</div>
""", unsafe_allow_html=True)

with comp_col2:
    # Use a container for interactions and style it
    with st.container(border=True):
        st.markdown('<div style="text-align: center; margin-bottom: 20px;"><span class="profile-badge badge-success">Profile B (Compare)</span></div>', unsafe_allow_html=True)
        
        # Comparison profile inputs
        comp_country = st.selectbox("Country", list(COUNTRY_DATA.keys()), index=list(COUNTRY_DATA.keys()).index(sp_country), key="comp_country")
        
        comp_col_a, comp_col_b = st.columns(2)
        with comp_col_a:
            comp_edu = st.slider("Education (yrs)", 0, 20, sp_edu, key="comp_edu")
            comp_gender = st.selectbox("Gender", ["Male", "Female"], index=0 if sp_gender == "Male" else 1, key="comp_gender")
        with comp_col_b:
            comp_digital = st.slider("Digital (%)", 0, 100, sp_digital, key="comp_digital")
            comp_location = st.selectbox("Location", ["Rural", "Urban"], index=0 if sp_location == "Rural" else 1, key="comp_location")
        
        comp_occ = st.selectbox("Occupation", ["Agriculture", "Industry", "Services", "Public Sector", "Unemployed"], 
                                index=["Agriculture", "Industry", "Services", "Public Sector", "Unemployed"].index(sp_occ), key="comp_occ")
        comp_credit = st.checkbox("Credit Access", value=sp_credit, key="comp_credit")
        comp_age = sp_age  # Keep same for fair comparison
        
        # Calculate comparison score
        comp_g_val = 1 if comp_gender == "Female" else 0
        comp_u_val = 1 if comp_location == "Urban" else 0
        comp_p, comp_components = calculate_percentile(comp_country, comp_edu, comp_digital, comp_g_val, comp_u_val, comp_occ, comp_credit, comp_age)
        comp_group, comp_color = get_tercile(comp_p)
        
        st.markdown(f"""
<div style="background: rgba(16, 185, 129, 0.1); padding: 20px; border-radius: 10px; margin-top: 15px;">
<div style="text-align: center;">
<div style="font-size: 3.5rem; font-weight: 800; color: #34d399; margin: 10px 0;">{comp_p:.1f}<span style="font-size: 1.5rem;">th</span></div>
<div style="color: #8b98a5; font-size: 0.9rem;">PERCENTILE</div>
</div>
</div>
""", unsafe_allow_html=True)
=======
    st.markdown('<div style="text-align: center; margin-bottom: 20px;"><span class="simulator-profile-badge simulator-badge-primary">Profile A (You)</span></div>', unsafe_allow_html=True)
    
    # Profile A inputs
    comp_a_country = st.selectbox("Country", list(COUNTRY_DATA.keys()), index=list(COUNTRY_DATA.keys()).index(sp_country), key="comp_a_country")
    
    comp_a_col_a, comp_a_col_b = st.columns(2)
    with comp_a_col_a:
        comp_a_edu = st.slider("Education (yrs)", 0, 20, sp_edu, key="comp_a_edu")
        comp_a_gender = st.selectbox("Gender", ["Male", "Female"], index=0 if sp_gender == "Male" else 1, key="comp_a_gender")
    with comp_a_col_b:
        comp_a_digital = st.slider("Digital (%)", 0, 100, sp_digital, key="comp_a_digital")
        comp_a_location = st.selectbox("Location", ["Rural", "Urban"], index=0 if sp_location == "Rural" else 1, key="comp_a_location")
    
    comp_a_occ = st.selectbox("Occupation", ["Agriculture", "Industry", "Services", "Public Sector", "Unemployed"], 
                            index=["Agriculture", "Industry", "Services", "Public Sector", "Unemployed"].index(sp_occ), key="comp_a_occ")
    comp_a_credit = st.checkbox("Credit Access", value=sp_credit, key="comp_a_credit")
    comp_a_age = sp_age  # Keep same for fair comparison
    
    # Calculate Profile A score
    comp_a_g_val = 1 if comp_a_gender == "Female" else 0
    comp_a_u_val = 1 if comp_a_location == "Urban" else 0
    comp_a_p, comp_a_components = calculate_percentile(comp_a_country, comp_a_edu, comp_a_digital, comp_a_g_val, comp_a_u_val, comp_a_occ, comp_a_credit, comp_a_age)
    comp_a_group, comp_a_color = get_tercile(comp_a_p)
    
    st.markdown(f"""
    <div style="background: rgba(59, 130, 246, 0.1); padding: 20px; border-radius: 10px; margin-top: 15px; border: 2px solid #3b82f6;">
        <div style="text-align: center;">
            <div style="font-size: 3.5rem; font-weight: 800; color: #60a5fa; margin: 10px 0;">{comp_a_p:.1f}<span style="font-size: 1.5rem;">th</span></div>
            <div style="color: #8b98a5; font-size: 0.9rem;">PERCENTILE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with comp_col2:
    st.markdown('<div style="text-align: center; margin-bottom: 20px;"><span class="simulator-profile-badge simulator-badge-success">Profile B (Compare)</span></div>', unsafe_allow_html=True)
    
    # Comparison profile inputs
    comp_country = st.selectbox("Country", list(COUNTRY_DATA.keys()), index=list(COUNTRY_DATA.keys()).index(sp_country), key="comp_country")
    
    comp_col_a, comp_col_b = st.columns(2)
    with comp_col_a:
        comp_edu = st.slider("Education (yrs)", 0, 20, sp_edu, key="comp_edu")
        comp_gender = st.selectbox("Gender", ["Male", "Female"], index=0 if sp_gender == "Male" else 1, key="comp_gender")
    with comp_col_b:
        comp_digital = st.slider("Digital (%)", 0, 100, sp_digital, key="comp_digital")
        comp_location = st.selectbox("Location", ["Rural", "Urban"], index=0 if sp_location == "Rural" else 1, key="comp_location")
    
    comp_occ = st.selectbox("Occupation", ["Agriculture", "Industry", "Services", "Public Sector", "Unemployed"], 
                            index=["Agriculture", "Industry", "Services", "Public Sector", "Unemployed"].index(sp_occ), key="comp_occ")
    comp_credit = st.checkbox("Credit Access", value=sp_credit, key="comp_credit")
    comp_age = sp_age  # Keep same for fair comparison
    
    # Calculate comparison score
    comp_g_val = 1 if comp_gender == "Female" else 0
    comp_u_val = 1 if comp_location == "Urban" else 0
    comp_p, comp_components = calculate_percentile(comp_country, comp_edu, comp_digital, comp_g_val, comp_u_val, comp_occ, comp_credit, comp_age)
    comp_group, comp_color = get_tercile(comp_p)
    
    st.markdown(f"""
    <div style="background: rgba(16, 185, 129, 0.1); padding: 20px; border-radius: 10px; margin-top: 15px; border: 2px solid #10b981;">
        <div style="text-align: center;">
            <div style="font-size: 3.5rem; font-weight: 800; color: #34d399; margin: 10px 0;">{comp_p:.1f}<span style="font-size: 1.5rem;">th</span></div>
            <div style="color: #8b98a5; font-size: 0.9rem;">PERCENTILE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
>>>>>>> Stashed changes

# Stunning Circular Comparison Visualization
st.markdown("---")
st.markdown("### 🎯 Visual Comparison Dashboard")

viz_comp_col1, viz_comp_col2, viz_comp_col3 = st.columns([1, 2, 1], gap="large")

with viz_comp_col1:
    # Profile A Donut
    fig_donut_a = go.Figure(data=[go.Pie(
        values=[comp_a_p, 100-comp_a_p],
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
            dict(text=f"<b>{comp_a_p:.0f}%</b>", x=0.5, y=0.55, font=dict(size=36, color='#60a5fa'), showarrow=False),
            dict(text="Profile A", x=0.5, y=0.35, font=dict(size=14, color='#8b98a5'), showarrow=False)
        ]
    )
    st.plotly_chart(fig_donut_a, use_container_width=True, config={'displayModeBar': False})
    export_plot_menu(fig_donut_a, "profile_a_percentile", key="donut_a")

with viz_comp_col2:
    # Difference indicator  
    diff = comp_p - comp_a_p
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
        values=[comp_p, 100-comp_p],
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
            dict(text=f"<b>{comp_p:.0f}%</b>", x=0.5, y=0.55, font=dict(size=36, color='#34d399'), showarrow=False),
            dict(text="Profile B", x=0.5, y=0.35, font=dict(size=14, color='#8b98a5'), showarrow=False)
        ]
    )
    st.plotly_chart(fig_donut_b, use_container_width=True, config={'displayModeBar': False})
    export_plot_menu(fig_donut_b, "profile_b_percentile", key="donut_b")

# Side-by-side radar chart with normalized values
st.markdown("### 🕸️ Multi-Dimensional Comparison")

# Prepare data with actual values and percentages
categories = ['Education\n(Years)', 'Digital Skills\n(%)', 'Occupation\n(Points)', 'Urban\n(Points)', 'Credit\n(Points)']

# Get raw input values for better comparison
profile_a_raw = [comp_a_edu, comp_a_digital, comp_a_components['Occupation Premium'], comp_a_components['Urban Infrastructure Bonus'], comp_a_components['Credit/Bank Access']]
profile_b_raw = [comp_edu, comp_digital, comp_components['Occupation Premium'], comp_components['Urban Infrastructure Bonus'], comp_components['Credit/Bank Access']]

# Normalize to 0-100 scale for better visualization
def normalize_value(value, max_val):
    return (value / max_val) * 100 if max_val > 0 else 0

profile_a_normalized = [
    normalize_value(comp_a_edu, 20),  # Education out of 20
    comp_a_digital,  # Already 0-100
    normalize_value(comp_a_components['Occupation Premium'], 15),  # Occupation max is 15
    normalize_value(comp_a_components['Urban Infrastructure Bonus'], 14),  # Urban max is 14 (dynamic)
    normalize_value(comp_a_components['Credit/Bank Access'], 7)  # Credit max is 7
]

profile_b_normalized = [
    normalize_value(comp_edu, 20),
    comp_digital,
    normalize_value(comp_components['Occupation Premium'], 15),
    normalize_value(comp_components['Urban Infrastructure Bonus'], 14),
    normalize_value(comp_components['Credit/Bank Access'], 7)
]

fig_radar = go.Figure()

fig_radar.add_trace(go.Scatterpolar(
    r=profile_a_normalized,
    theta=categories,
    fill='toself',
    name='Profile A (You)',
    line=dict(color='#3b82f6', width=3),
    fillcolor='rgba(59, 130, 246, 0.3)',
    hovertemplate='<b>%{theta}</b><br>Score: %{r:.1f}/100<extra></extra>'
))

fig_radar.add_trace(go.Scatterpolar(
    r=profile_b_normalized,
    theta=categories,
    fill='toself',
    name='Profile B (Compare)',
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

st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
export_plot_menu(fig_radar, "multi_dimensional_comparison", key="radar_chart")

# Add explanation
st.markdown("""
<<<<<<< Updated upstream
<div style="background: rgba(59, 130, 246, 0.05); padding: 15px; border-radius: 8px; border-left: 3px solid #3b82f6; margin-top: 15px;">
<p style="color: #8b98a5; font-size: 0.9rem; margin: 0;">
<b style="color: #e2e8f0;">How to read this chart:</b> Each axis represents a different factor, normalized to a 0-100 scale. 
Larger areas indicate stronger profiles. The blue area shows Profile A (you), and the green area shows Profile B (comparison).
</p>
=======
</div>
""", unsafe_allow_html=True)

# ============= TIMELINE ANALYSIS SECTION (MOVED) =============

st.markdown('<p class="simulator-section-header">📅 Historical Context & Timeline Analysis</p>', unsafe_allow_html=True)

st.markdown("""
<div style="background: rgba(29, 155, 240, 0.08); padding: 20px; border-radius: 12px; border-left: 4px solid #1d9bf0; margin-bottom: 20px;">
    <p style="color: #e2e8f0; margin: 0; line-height: 1.6;">
        <b style="color: #1d9bf0;">📊 Year-Wise Analysis:</b> See how education and employment have evolved in your country over time. 
        Compare different years to understand long-term trends and how your current profile compares to historical averages.
    </p>
>>>>>>> Stashed changes
</div>
""", unsafe_allow_html=True)

# Load historical data
from utils.enhanced_loaders import load_education_data, load_jobs_data

timeline_col1_m, timeline_col2_m = st.columns([2, 1])

with timeline_col1_m:
    # Year selector for comparison
    selected_years_m = st.select_slider(
        "📅 Select Years to Compare",
        options=list(range(2000, 2025)),
        value=(2000, 2023),
        help="Compare how indicators changed between two years",
        key="timeline_slider_moved"
    )

with timeline_col2_m:
    show_timeline_m = st.checkbox("📈 Show Timeline Visualizations", value=True, key="timeline_check_moved")

if show_timeline_m:
    # Load real data
    edu_data_m = load_education_data()
    jobs_data_m = load_jobs_data()
    
    # Filter for selected country
    country_edu_m = edu_data_m[edu_data_m['Country Name'] == sp_country]
    country_jobs_m = jobs_data_m[jobs_data_m['Country Name'] == sp_country]
    
    timeline_viz_col1_m, timeline_viz_col2_m = st.columns(2)
    
    with timeline_viz_col1_m:
        st.markdown("### 📚 Education Trends Over Time")
        
        # Get enrollment rate data
        enrollment_data_m = country_edu_m[
            country_edu_m['Series'].str.contains('enrollment', case=False, na=False) |
            country_edu_m['Series'].str.contains('enrolment', case=False, na=False)
        ].copy()
        
        if not enrollment_data_m.empty:
            # Aggregate by year (take mean if multiple indicators)
            enrollment_trend_m = enrollment_data_m.groupby('Year')['Value'].mean().reset_index()
            enrollment_trend_m = enrollment_trend_m.sort_values('Year')
            
            # Premium "WOW" Visualization for Education
            fig_edu_m = go.Figure()
            
            # Area Fill
            fig_edu_m.add_trace(go.Scatter(
                x=enrollment_trend_m['Year'], y=enrollment_trend_m['Value'],
                mode='lines', line=dict(width=0), fill='tozeroy',
                fillcolor='rgba(59, 130, 246, 0.1)', hoverinfo='skip', showlegend=False
            ))
            
            # Main Line
            fig_edu_m.add_trace(go.Scatter(
                x=enrollment_trend_m['Year'], y=enrollment_trend_m['Value'],
                mode='lines+markers', name='Enrollment',
                line=dict(color='#3b82f6', width=4, shape='spline', smoothing=1.3),
                marker=dict(size=8, color='#ffffff', line=dict(color='#3b82f6', width=2)),
                hovertemplate="<b>Year: %{x}</b><br>Rate: %{y:.1f}%<extra></extra>"
            ))
            
            # Highlight selected years if applicable
            if len(selected_years_m) == 2:
                y1, y2 = selected_years_m
                v1 = enrollment_trend_m[enrollment_trend_m['Year'] == y1]['Value'].values
                v2 = enrollment_trend_m[enrollment_trend_m['Year'] == y2]['Value'].values
                
                if len(v1) > 0:
                    fig_edu_m.add_annotation(x=y1, y=v1[0], text=f"{y1}", showarrow=True, arrowhead=2, arrowcolor="#ef4444", ay=-30, font=dict(color="#ef4444"))
                if len(v2) > 0:
                    fig_edu_m.add_annotation(x=y2, y=v2[0], text=f"{y2}", showarrow=True, arrowhead=2, arrowcolor="#10b981", ay=-30, font=dict(color="#10b981"))
            
            fig_edu_m.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font={'color': '#e2e8f0', 'family': 'Inter'}, height=350,
                margin=dict(t=30, b=20, l=10, r=10),
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False, ticksuffix="%"),
                hovermode='x unified'
            )
            st.plotly_chart(fig_edu_m, use_container_width=True, config={'displayModeBar': False})
            
            # Show comparison
            if len(selected_years_m) == 2:
                year_start_m, year_end_m = selected_years_m
                val_start_m = enrollment_trend_m[enrollment_trend_m['Year'] == year_start_m]['Value'].values
                val_end_m = enrollment_trend_m[enrollment_trend_m['Year'] == year_end_m]['Value'].values
                
                if len(val_start_m) > 0 and len(val_end_m) > 0:
                    change_m = val_end_m[0] - val_start_m[0]
                    change_pct_m = (change_m / val_start_m[0] * 100) if val_start_m[0] > 0 else 0
                    
                    st.markdown(f"""
                    <div style="background: rgba(59, 130, 246, 0.1); padding: 15px; border-radius: 8px; margin-top: 10px;">
                        <b style="color: #60a5fa;">Change from {year_start_m} to {year_end_m}:</b><br>
                        <span style="color: {'#10b981' if change_m > 0 else '#ef4444'}; font-size: 1.2rem; font-weight: 600;">
                            {change_m:+.1f} points ({change_pct_m:+.1f}%)
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("📊 Education trend data not available for this country")
    
    with timeline_viz_col2_m:
        st.markdown("### 💼 Employment & Access Trends")
        
        # Get electricity access as proxy for development
        electricity_data_m = country_jobs_m[
            country_jobs_m['Series Name'].str.contains('electricity', case=False, na=False)
        ].copy()
        
        if not electricity_data_m.empty:
            electricity_trend_m = electricity_data_m.groupby('Year')['Value'].mean().reset_index()
            electricity_trend_m = electricity_trend_m.sort_values('Year')
            
            # Premium "WOW" Visualization for Jobs & Access
            fig_jobs_m = go.Figure()
            
            # Area Fill
            fig_jobs_m.add_trace(go.Scatter(
                x=electricity_trend_m['Year'], y=electricity_trend_m['Value'],
                mode='lines', line=dict(width=0), fill='tozeroy',
                fillcolor='rgba(16, 185, 129, 0.1)', hoverinfo='skip', showlegend=False
            ))
            
            # Main Line
            fig_jobs_m.add_trace(go.Scatter(
                x=electricity_trend_m['Year'], y=electricity_trend_m['Value'],
                mode='lines+markers', name='Access Rate',
                line=dict(color='#10b981', width=4, shape='spline', smoothing=1.3),
                marker=dict(size=8, color='#ffffff', line=dict(color='#10b981', width=2)),
                hovertemplate="<b>Year: %{x}</b><br>Rate: %{y:.1f}%<extra></extra>"
            ))
            
            # Highlight selected years if applicable
            if len(selected_years_m) == 2:
                y1, y2 = selected_years_m
                v1 = electricity_trend_m[electricity_trend_m['Year'] == y1]['Value'].values
                v2 = electricity_trend_m[electricity_trend_m['Year'] == y2]['Value'].values
                
                if len(v1) > 0:
                    fig_jobs_m.add_annotation(x=y1, y=v1[0], text=f"{y1}", showarrow=True, arrowhead=2, arrowcolor="#ef4444", ay=-30, font=dict(color="#ef4444"))
                if len(v2) > 0:
                    fig_jobs_m.add_annotation(x=y2, y=v2[0], text=f"{y2}", showarrow=True, arrowhead=2, arrowcolor="#10b981", ay=-30, font=dict(color="#10b981"))
            
            fig_jobs_m.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font={'color': '#e2e8f0', 'family': 'Inter'}, height=350,
                margin=dict(t=30, b=20, l=10, r=10),
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False, ticksuffix="%"),
                hovermode='x unified'
            )
            st.plotly_chart(fig_jobs_m, use_container_width=True, config={'displayModeBar': False})
            
            # Show comparison
            if len(selected_years_m) == 2:
                year_start_m, year_end_m = selected_years_m
                val_start_m = electricity_trend_m[electricity_trend_m['Year'] == year_start_m]['Value'].values
                val_end_m = electricity_trend_m[electricity_trend_m['Year'] == year_end_m]['Value'].values
                
                if len(val_start_m) > 0 and len(val_end_m) > 0:
                    change_m = val_end_m[0] - val_start_m[0]
                    change_pct_m = (change_m / val_start_m[0] * 100) if val_start_m[0] > 0 else 0
                    
                    st.markdown(f"""
                    <div style="background: rgba(16, 185, 129, 0.1); padding: 15px; border-radius: 8px; margin-top: 10px;">
                        <b style="color: #34d399;">Change from {year_start_m} to {year_end_m}:</b><br>
                        <span style="color: {'#10b981' if change_m > 0 else '#ef4444'}; font-size: 1.2rem; font-weight: 600;">
                            {change_m:+.1f} points ({change_pct_m:+.1f}%)
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("📊 Employment trend data not available for this country")
    
    # ============= COMPREHENSIVE YEAR COMPARISON (MOVED) =============
    
    st.markdown("---")
    st.markdown("### 📊 Comprehensive Year-Wise Comparison Dashboard")
    st.markdown(f"""
    <div style="background: rgba(16, 185, 129, 0.08); padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <p style="color: #8b98a5; margin: 0;">
            <b style="color: #10b981;">Side-by-Side Analysis:</b> Compare ALL key indicators between 
            <b style="color: #ef4444;">{selected_years_m[0]}</b> and <b style="color: #10b981;">{selected_years_m[1]}</b> 
            to see how {sp_country} has evolved.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Prepare comparison data
    from utils.enhanced_loaders import load_wdi_data as load_wdi_data_m
    wdi_data_m = load_wdi_data_m()
    country_wdi_m = wdi_data_m[wdi_data_m['Country Name'] == sp_country]
    
    year_start_m, year_end_m = selected_years_m
    
    # Define key indicators to compare
    comparison_indicators_m = {
        'Education': {
            'Enrollment Rate': ('enrollment', country_edu_m),
            'Literacy Rate': ('literacy', country_edu_m),
        },
        'Development': {
            'GDP per Capita': ('GDP per capita', country_wdi_m),
            'Poverty Rate': ('poverty', country_wdi_m),
        },
        'Employment': {
            'Electricity Access': ('electricity', country_jobs_m),
            'Employment Rate': ('employment', country_jobs_m),
        }
    }
    
    comparison_data_m = []
    
    # Extract data for each indicator
    for category_m, indicators_m in comparison_indicators_m.items():
        for indicator_name_m, (search_term_m, data_source_m) in indicators_m.items():
            # Filter data
            if data_source_m is country_edu_m:
                filtered_m = data_source_m[
                    data_source_m['Series'].str.contains(search_term_m, case=False, na=False)
                ]
            else:
                filtered_m = data_source_m[
                    data_source_m['Series Name'].str.contains(search_term_m, case=False, na=False)
                ]
            
            if not filtered_m.empty:
                val_start_arr_m = filtered_m[filtered_m['Year'] == year_start_m]['Value'].values
                val_end_arr_m = filtered_m[filtered_m['Year'] == year_end_m]['Value'].values
                
                if len(val_start_arr_m) > 0 and len(val_end_arr_m) > 0:
                    delta_m = val_end_arr_m[0] - val_start_arr_m[0]
                    delta_pct_m = (delta_m / val_start_arr_m[0] * 100) if val_start_arr_m[0] > 0 else 0
                    
                    comparison_data_m.append({
                        'Category': category_m,
                        'Indicator': indicator_name_m,
                        f'{year_start_m}': f"{val_start_arr_m[0]:.1f}",
                        f'{year_end_m}': f"{val_end_arr_m[0]:.1f}",
                        'Change': f"{delta_m:+.1f}",
                        'Change %': f"{delta_pct_m:+.1f}%",
                        'Trend': '📈' if delta_m > 0 else '📉' if delta_m < 0 else '➡️'
                    })
    
    if comparison_data_m:
        comp_df_m = pd.DataFrame(comparison_data_m)
        st.dataframe(
            comp_df_m,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Trend': st.column_config.TextColumn('Trend', width='small'),
                'Change': st.column_config.TextColumn('Change', width='small'),
                'Change %': st.column_config.TextColumn('% Change', width='small'),
            }
        )
        
        # Summary statistics
        improv_m = sum(1 for item in comparison_data_m if float(item['Change'].replace('+', '')) > 0)
        total_ind_m = len(comparison_data_m)
        improv_rate_m = (improv_m / total_ind_m * 100) if total_ind_m > 0 else 0
        
        summ_col1_m, summ_col2_m, summ_col3_m = st.columns(3)
        with summ_col1_m:
            st.markdown(f'<div style="text-align: center; padding: 20px; background: rgba(16, 185, 129, 0.1); border-radius: 8px;"><div style="font-size: 2rem; color: #10b981;">📈</div><div style="font-size: 1.8rem; font-weight: 700; color: #10b981;">{improv_m}</div><div style="color: #8b98a5; font-size: 0.9rem;">Improved</div></div>', unsafe_allow_html=True)
        with summ_col2_m:
            st.markdown(f'<div style="text-align: center; padding: 20px; background: rgba(59, 130, 246, 0.1); border-radius: 8px;"><div style="font-size: 2rem; color: #3b82f6;">📊</div><div style="font-size: 1.8rem; font-weight: 700; color: #3b82f6;">{total_ind_m}</div><div style="color: #8b98a5; font-size: 0.9rem;">Total Indicators</div></div>', unsafe_allow_html=True)
        with summ_col3_m:
            st.markdown(f'<div style="text-align: center; padding: 20px; background: rgba(236, 72, 153, 0.1); border-radius: 8px;"><div style="font-size: 2rem; color: #ec4899;">✨</div><div style="font-size: 1.8rem; font-weight: 700; color: #ec4899;">{improv_rate_m:.0f}%</div><div style="color: #8b98a5; font-size: 0.9rem;">Improvement Rate</div></div>', unsafe_allow_html=True)

st.markdown("---")

# Detailed factor comparison - IN EXPANDER
with st.expander("📊 View Detailed Factor-by-Factor Breakdown"):
    st.markdown("Compare the exact point contributions for each factor between both profiles.")
    
    # Create comparison dataframe
    comparison_data = []
    for factor in comp_a_components.keys():
        comparison_data.append({
            "Factor": factor,
            "Profile A": f"{comp_a_components[factor]:+.1f}",
            "Profile B": f"{comp_components[factor]:+.1f}",
            "Difference": f"{comp_components[factor] - comp_a_components[factor]:+.1f}"
        })
    
    comp_df = pd.DataFrame(comparison_data)
    st.dataframe(comp_df, use_container_width=True, hide_index=True)



# ============= TAB 2: SAME PROFILE ACROSS YEARS =============
with comparison_tab2:
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(236, 72, 153, 0.1), rgba(59, 130, 246, 0.1)); 
                padding: 20px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #ec4899;">
        <h3 style="text-align: center; color: #ffffff; margin-bottom: 10px;">📅 Yearly Trend Analysis</h3>
        <p style="text-align: center; color: #8b98a5; margin-bottom: 0;">
            See how <b>your exact profile</b> would perform in different years. 
            Compare 2001 vs 2023 to understand how the value of education and skills has changed over time.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Year selection for trend analysis
    trend_col1, trend_col2 = st.columns(2)
    
    with trend_col1:
        year_for_comparison_1 = st.selectbox(
            "📅 Year 1 (Earlier)",
            options=list(range(2000, 2025)),
            index=1,  # 2001
            key="trend_year_1"
        )
    
    with trend_col2:
        year_for_comparison_2 = st.selectbox(
            "📅 Year 2 (Later)",
            options=list(range(2000, 2025)),
            index=23,  # 2023
            key="trend_year_2"
        )
    
    st.markdown("---")
    
    # Profile summary
    st.markdown(f"""
    <div style="background: rgba(59, 130, 246, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <b style="color: #60a5fa;">📋 Your Profile Being Compared:</b><br>
        <div style="margin-top: 10px; color: #e2e8f0;">
            <b>Country:</b> {sp_country} &nbsp;|&nbsp; 
            <b>Education:</b> {sp_edu} years &nbsp;|&nbsp; 
            <b>Digital:</b> {sp_digital}% &nbsp;|&nbsp; 
            <b>Gender:</b> {sp_gender} &nbsp;|&nbsp; 
            <b>Location:</b> {sp_location} &nbsp;|&nbsp; 
            <b>Occupation:</b> {sp_occ}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate percentile for both years
    # Note: This is a simulation - in reality we'd adjust based on year-specific data
    # For now, we'll show how the same education level becomes more/less valuable
    
    # Load year-specific data to adjust the calculation
    edu_data = load_education_data()
    country_edu_trend = edu_data[edu_data['Country Name'] == sp_country]
    
    # Get enrollment rates for both years to estimate education value change
    enrollment_year1 = country_edu_trend[
        (country_edu_trend['Year'] == year_for_comparison_1) &
        (country_edu_trend['Series'].str.contains('enrollment', case=False, na=False))
    ]['Value'].mean()
    
    
    enrollment_year2 = country_edu_trend[
        (country_edu_trend['Year'] == year_for_comparison_2) &
        (country_edu_trend['Series'].str.contains('enrollment', case=False, na=False))
    ]['Value'].mean()
    
    # Adjust percentile based on education improvement (simplified model)
    # If enrollment increased, same education becomes less rare, so percentile might decrease
    year1_percentile = sp_p
    if not pd.isna(enrollment_year1) and not pd.isna(enrollment_year2):
        enrollment_change_factor = enrollment_year2 / enrollment_year1 if enrollment_year1 > 0 else 1
        # Higher enrollment = more competition, so adjust percentile
        year2_percentile = sp_p * (2 - min(enrollment_change_factor, 1.5))  # Cap at 1.5x growth
    else:
        year2_percentile = sp_p * 0.95  # Default: slight decrease due to general education improvement
    
    year2_percentile = min(99.9, max(1.0, year2_percentile))  # Keep within bounds
    
    # Display comparison cards
    year_comp_col1, year_comp_col2, year_comp_col3 = st.columns([1, 0.5, 1])
    
    with year_comp_col1:
        st.markdown(f"""
        <div style="background: rgba(239, 68, 68, 0.15); padding: 25px; border-radius: 12px; border: 2px solid #ef4444;">
            <div style="text-align: center;">
                <div style="font-size: 1.2rem; color: #fca5a5; margin-bottom: 10px;">📅 {year_for_comparison_1}</div>
                <div style="font-size: 3.5rem; font-weight: 800; color: #ef4444;">{year1_percentile:.1f}<span style="font-size: 1.5rem;">th</span></div>
                <div style="color: #8b98a5; font-size: 0.9rem; margin-top: 10px;">PERCENTILE</div>
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(239, 68, 68, 0.3);">
                    <div style="color: #e2e8f0; font-size: 0.85rem;">
                        Your {sp_edu} years of education placed you <b style="color: #ef4444;">above {year1_percentile:.1f}%</b> of people
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with year_comp_col2:
        percentile_change = year2_percentile - year1_percentile
        arrow = "→" if abs(percentile_change) < 1 else ("↗" if percentile_change > 0 else "↘")
        arrow_color = "#10b981" if percentile_change > 0 else "#ef4444" if percentile_change < 0 else "#8b98a5"
        
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: center; height: 100%;">
            <div style="text-align: center;">
                <div style="font-size: 3rem; color: {arrow_color};">{arrow}</div>
                <div style="font-size: 1.2rem; font-weight: 700; color: {arrow_color};">
                    {percentile_change:+.1f}
                </div>
                <div style="color: #8b98a5; font-size: 0.75rem;">points</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with year_comp_col3:
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.15); padding: 25px; border-radius: 12px; border: 2px solid #10b981;">
            <div style="text-align: center;">
                <div style="font-size: 1.2rem; color: #6ee7b7; margin-bottom: 10px;">📅 {year_for_comparison_2}</div>
                <div style="font-size: 3.5rem; font-weight: 800; color: #10b981;">{year2_percentile:.1f}<span style="font-size: 1.5rem;">th</span></div>
                <div style="color: #8b98a5; font-size: 0.9rem; margin-top: 10px;">PERCENTILE</div>
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(16, 185, 129, 0.3);">
                    <div style="color: #e2e8f0; font-size: 0.85rem;">
                        Same education now places you <b style="color: #10b981;">above {year2_percentile:.1f}%</b> of people
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Interpretation
    st.markdown("---")
    st.markdown("### 📖 What This Means")
    
    if percentile_change > 2:
        interpretation = f"""
        <div style="background: rgba(16, 185, 129, 0.1); padding: 20px; border-radius: 12px; border-left: 4px solid #10b981;">
            <b style="color: #10b981;">✅ Education Value Increased</b><br>
            <p style="color: #e2e8f0; margin-top: 10px;">
                Between {year_for_comparison_1} and {year_for_comparison_2}, having {sp_edu} years of education became 
                <b>MORE valuable</b> in {sp_country}. Despite more people getting educated, skilled workers are in higher demand.
            </p>
        </div>
        """
    elif percentile_change < -2:
        interpretation = f"""
        <div style="background: rgba(239, 68, 68, 0.1); padding: 20px; border-radius: 12px; border-left: 4px solid #ef4444;">
            <b style="color: #ef4444;">⚠️ Increased Competition</b><br>
            <p style="color: #e2e8f0; margin-top: 10px;">
                Between {year_for_comparison_1} and {year_for_comparison_2}, having {sp_edu} years of education became 
                <b>less rare</b> in {sp_country}. More people achieved similar education levels, increasing competition.
            </p>
        </div>
        """
    else:
        interpretation = f"""
        <div style="background: rgba(59, 130, 246, 0.1); padding: 20px; border-radius: 12px; border-left: 4px solid #3b82f6;">
            <b style="color: #3b82f6;">➡️ Relatively Stable</b><br>
            <p style="color: #e2e8f0; margin-top: 10px;">
                Between {year_for_comparison_1} and {year_for_comparison_2}, having {sp_edu} years of education 
                maintained similar relative value in {sp_country}.
            </p>
        </div>
        """
    
    st.markdown(interpretation, unsafe_allow_html=True)
    
    # Year-by-year trend chart
    st.markdown("---")
    st.markdown("### 📈 Year-by-Year Trend")
    
    years_range = list(range(year_for_comparison_1, year_for_comparison_2 + 1))
    percentile_trend = []
    
    for year in years_range:
        # Get enrollment for this year
        enrollment = country_edu_trend[
            (country_edu_trend['Year'] == year) &
            (country_edu_trend['Series'].str.contains('enrollment', case=False, na=False))
        ]['Value'].mean()
        
        if not pd.isna(enrollment) and not pd.isna(enrollment_year1):
            factor = enrollment / enrollment_year1 if enrollment_year1 > 0 else 1
            percentile_year = sp_p * (2 - min(factor, 1.5))
        else:
            # Linear interpolation
            progress = (year - year_for_comparison_1) / (year_for_comparison_2 - year_for_comparison_1)
            percentile_year = year1_percentile + (year2_percentile - year1_percentile) * progress
        
        percentile_trend.append({
            'Year': year,
            'Percentile': min(99.9, max(1.0, percentile_year))
        })
    
    trend_df = pd.DataFrame(percentile_trend)
    
    if not trend_df.empty and len(trend_df) > 1:
        # Create the "WOW" Glowing Area Chart
        fig_trend = go.Figure()

        # 1. Background Area with Gradient-like effect
        fig_trend.add_trace(go.Scatter(
            x=trend_df['Year'],
            y=trend_df['Percentile'],
            mode='lines',
            line=dict(width=0),
            fill='tozeroy',
            fillcolor='rgba(236, 72, 153, 0.15)',
            hoverinfo='skip',
            showlegend=False
        ))

        # 2. Main Vibrant Line with Spline Smoothing (THICKER and BIGGER Markers)
        fig_trend.add_trace(go.Scatter(
            x=trend_df['Year'],
            y=trend_df['Percentile'],
            mode='lines+markers',
            name='Economic Percentile',
            line=dict(
                color='#ec4899', 
                width=6, 
                shape='spline',
                smoothing=1.3
            ),
            marker=dict(
                size=12,
                color='#ffffff',
                line=dict(color='#ec4899', width=3),
                symbol='diamond'
            ),
            hovertemplate="<b>Year: %{x}</b><br>Percentile: %{y:.1f}th<extra></extra>"
        ))

        # 3. Add Glow Effect (thin blurred overlay)
        fig_trend.add_trace(go.Scatter(
            x=trend_df['Year'],
            y=trend_df['Percentile'],
            mode='lines',
            line=dict(
                color='#ec4899', 
                width=12, 
                shape='spline',
                smoothing=1.3
            ),
            opacity=0.2,
            hoverinfo='skip',
            showlegend=False
        ))

        # 4. Summary Insight and Annotations
        first_p = trend_df.iloc[0]['Percentile']
        last_p = trend_df.iloc[-1]['Percentile']
        total_delta = last_p - first_p
        
        # Summary Card to EMPHASIZE the change
        status_text = "Progress" if total_delta > 0 else "Decline"
        status_color = "#10b981" if total_delta > 0 else "#ef4444"
        arrow_icon = "↗️" if total_delta > 0 else "↘️"

        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.4); padding: 20px; border-radius: 12px; border-left: 5px solid {status_color}; margin-bottom: 25px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; font-weight: 600;">Overall Trend</span>
                    <h2 style="color: #e2e8f0; margin: 0; font-weight: 800;">{total_delta:+.1f}% {status_text} {arrow_icon}</h2>
                </div>
                <div style="text-align: right; background: rgba(0,0,0,0.2); padding: 8px 15px; border-radius: 8px;">
                    <div style="color: #94a3b8; font-size: 0.75rem;">TIMELINE</div>
                    <div style="color: #60a5fa; font-weight: 700; font-size: 1.1rem;">{year_for_comparison_1} — {year_for_comparison_2}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        fig_trend.add_annotation(
            x=trend_df.iloc[0]['Year'], y=first_p,
            text=f"BASE: {first_p:.1f}%",
            showarrow=True, arrowhead=3, arrowcolor="#94a3b8",
            ax=-30, ay=-40, font=dict(color="#94a3b8", size=11),
            bgcolor="rgba(15, 23, 42, 0.9)", bordercolor="#94a3b8", borderpad=4
        )
        
        fig_trend.add_annotation(
            x=trend_df.iloc[-1]['Year'], y=last_p,
            text=f"NOW: {last_p:.1f}%",
            showarrow=True, arrowhead=3, arrowcolor="#ec4899",
            ax=30, ay=-40, font=dict(color="#ec4899", size=13, weight="bold"),
            bgcolor="rgba(15, 23, 42, 0.9)", bordercolor="#ec4899", borderpad=4
        )

        # 5. Tight Dynamic Layout (Maximum emphasis on variation)
        min_p = trend_df['Percentile'].min()
        max_p = trend_df['Percentile'].max()
        # Tighten padding to make variation look more dramatic
        padding = max(0.5, (max_p - min_p) * 0.1) if max_p > min_p else 2
        
        fig_trend.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#e2e8f0', 'family': 'Inter'},
            height=480, # Slightly taller
            margin=dict(t=30, b=20, l=20, r=20),
            xaxis=dict(
                showgrid=True, 
                gridcolor='rgba(255,255,255,0.05)',
                tickfont=dict(size=12, color='#94a3b8'),
                zeroline=False,
                showspikes=True,
                spikemode='across',
                spikesnap='cursor',
                showline=True,
                spikecolor="rgba(236, 72, 153, 0.3)",
                spikethickness=1
            ),
            yaxis=dict(
                showgrid=True, 
                gridcolor='rgba(255,255,255,0.1)', 
                range=[max(0, min_p - padding), min(100, max_p + padding)],
                tickfont=dict(size=12, color='#94a3b8'),
                zeroline=False,
                ticksuffix="%"
            ),
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor='#1e293b',
                font_size=14,
                font_family="Inter"
            )
        )
        
        st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
    elif not trend_df.empty:
        st.info("💡 Select a wider year range to see the historical trend visualization.")
    else:
        st.warning("⚠️ Cannot generate trend chart. Please ensure Year 1 is earlier than Year 2.")
    
    st.markdown(f"""
    <div style="background: rgba(236, 72, 153, 0.08); padding: 15px; border-radius: 8px; margin-top: 15px;">
        <p style="color: #8b98a5; margin: 0; font-size: 0.9rem;">
            <b style="color: #ec4899;">📊 Trend Analysis:</b> This chart shows how your exact profile 
            ({ sp_edu} years education, {sp_digital}% digital skills) would have performed each year from 
            {year_for_comparison_1} to {year_for_comparison_2}.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============= STEP 4: DETAILED VISUALIZATIONS =============

st.markdown('<p class="simulator-section-header">📈 Step 4: Detailed Analysis & Visualizations</p>', unsafe_allow_html=True)

viz_col1, viz_col2 = st.columns([1, 1], gap="large")

with viz_col1:
    st.markdown("### 🏗️ What's Building Your Score?")
    st.markdown('<p style="color: #8b98a5; font-size: 0.9rem; margin-bottom: 15px;">Size shows how much each factor adds. Bigger = more impact.</p>', unsafe_allow_html=True)
    
    tree_data = [{"Factor": k, "Contribution": v} for k, v in breakdown_components.items() if v > 0]
    
    if tree_data:
        df_tree = pd.DataFrame(tree_data)
        fig_tree = px.treemap(
            df_tree, 
            path=['Factor'], 
            values='Contribution', 
            color='Contribution', 
            color_continuous_scale='Tealgrn',
            hover_data={'Contribution': ':.2f'}
        )
        fig_tree.update_traces(
            textinfo="label+value", 
            textfont=dict(size=14, color='white', family='Inter, sans-serif'),
            marker=dict(line=dict(color='rgba(255,255,255,0.3)', width=2)),
            hovertemplate='<b>%{label}</b><br>Contribution: %{value:.1f} points<extra></extra>'
        )
        fig_tree.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            font={'color': '#e2e8f0', 'family': 'Inter, sans-serif'}, 
            height=480, 
            margin=dict(t=5, l=5, r=5, b=5)
        )
        st.plotly_chart(fig_tree, use_container_width=True)

with viz_col2:
    st.markdown("### 📈 How Education Changes Everything")
    st.markdown('<p style="color: #8b98a5; font-size: 0.9rem; margin-bottom: 15px;">Shows how your position changes with education. Red star = you now.</p>', unsafe_allow_html=True)
    
    edu_range = list(range(0, 21, 2))
    scores_by_edu = []
    for e in edu_range:
        score, _ = calculate_percentile(sp_country, e, sp_digital, g_val, u_val, sp_occ, sp_credit, sp_age)
        scores_by_edu.append({"Education Years": e, "Percentile": score})
    
    df_edu = pd.DataFrame(scores_by_edu)
    fig_line = px.line(df_edu, x='Education Years', y='Percentile', markers=True)
    fig_line.add_scatter(
        x=[sp_edu], 
        y=[sp_p], 
        mode='markers', 
        marker=dict(size=18, color='#ef4444', symbol='star', line=dict(color='white', width=2)), 
        name='You Are Here',
        hovertemplate='<b>Your Position</b><br>Education: %{x} years<br>Percentile: %{y:.1f}<extra></extra>'
    )
    fig_line.update_traces(
        line_color='#1d9bf0', 
        line_width=4, 
        selector=dict(mode='lines'),
        hovertemplate='Education: %{x} years<br>Percentile: %{y:.1f}<extra></extra>'
    )
    fig_line.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        font={'color': '#e2e8f0', 'family': 'Inter, sans-serif'}, 
        height=480,
        xaxis=dict(
            title="Years of Education", 
            showgrid=True, 
            gridcolor='rgba(255,255,255,0.1)',
            title_font=dict(size=14, color='#e2e8f0')
        ),
        yaxis=dict(
            title="Economic Percentile", 
            showgrid=True, 
            gridcolor='rgba(255,255,255,0.1)',
            title_font=dict(size=14, color='#e2e8f0')
        ),
        margin=dict(t=10, l=10, r=10, b=10),
        hovermode='x unified'
    )
    st.plotly_chart(fig_line, use_container_width=True)

# Factor table - HIDE BY DEFAULT IN EXPANDER
with st.expander("📊 View Detailed Factor-by-Factor Calculations"):
    st.markdown("#### 📋 Detailed Factor Contribution")
    st.markdown('<p style="color: #8b98a5; font-size: 0.9rem; margin-bottom: 15px;">Complete breakdown of how each factor impacts your economic position</p>', unsafe_allow_html=True)
    factor_df = pd.DataFrame([
        {"Factor": k, "Points Added": f"{v:+.1f}", "Impact": "🟢 Positive" if v > 0 else ("🔴 Negative" if v < 0 else "⚪ Neutral")}
        for k, v in breakdown_components.items()
    ])
    st.dataframe(factor_df, use_container_width=True, hide_index=True)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #8b98a5; font-size: 0.85rem; padding: 20px 0;">
    <b>Income Simulator v4.0</b> | Enhanced with Visual Analytics, Comparison Tools & Plain-Language Insights<br>
    Calibrated for South Asian socio-economic contexts | Educational purposes only
</div>
""", unsafe_allow_html=True)