import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from pathlib import Path

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
    .pro-card {
        background: #1e2532;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #2f3336;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .input-group-label {
        font-size: 0.85rem;
        color: #8b98a5;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
        font-weight: 600;
    }
    
    .result-container {
        text-align: center;
        padding: 30px;
        background: linear-gradient(180deg, rgba(30, 37, 50, 0.8) 0%, rgba(30, 37, 50, 0.4) 100%);
        border-radius: 16px;
        border: 1px solid #2f3336;
        margin-bottom: 20px;
    }
    .metric-value-large {
        font-size: 4rem;
        font-weight: 800;
        background: -webkit-linear-gradient(0deg, #1d9bf0, #00ba7c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.1;
    }
    .metric-label {
        color: #8b98a5;
        text-transform: uppercase;
        font-size: 0.9rem;
        letter-spacing: 1px;
    }
    .metric-group {
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 10px;
    }
    
    .insight-panel {
        background: rgba(29, 155, 240, 0.05);
        border-left: 4px solid #1d9bf0;
        padding: 20px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 15px;
    }
    
    .insight-panel-success {
        background: rgba(16, 185, 129, 0.05);
        border-left: 4px solid #10b981;
        padding: 20px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 15px;
    }
    
    .insight-panel-warning {
        background: rgba(245, 158, 11, 0.05);
        border-left: 4px solid #f59e0b;
        padding: 20px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 15px;
    }
    
    .insight-title {
        color: #ffffff;
        font-weight: 600;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1.1rem;
    }
    
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #ffffff;
        margin: 30px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid rgba(29, 155, 240, 0.3);
    }
    
    .comparison-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(16, 185, 129, 0.1));
        border: 2px solid rgba(59, 130, 246, 0.3);
        border-radius: 16px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .profile-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    .badge-primary {
        background: linear-gradient(135deg, #3b82f6, #1d9bf0);
        color: white;
    }
    
    .badge-success {
        background: linear-gradient(135deg, #10b981, #34d399);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Country data
COUNTRY_DATA = {
    'Bangladesh': {'base': 25, 'education_weight': 0.32, 'urban_bonus': 8},
    'India': {'base': 22, 'education_weight': 0.35, 'urban_bonus': 12},
    'Pakistan': {'base': 20, 'education_weight': 0.30, 'urban_bonus': 10},
    'Nepal': {'base': 22, 'education_weight': 0.32, 'urban_bonus': 7},
    'Sri Lanka': {'base': 25, 'education_weight': 0.32, 'urban_bonus': 11}
}

def calculate_percentile(country, edu, digital, gender, urban, occupation="Services", credit=False, age="Adult"):
    """Calculate economic percentile with detailed component breakdown"""
    data = COUNTRY_DATA.get(country, COUNTRY_DATA['India'])
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
    gender_contrib = gender*(-8)
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
    
    return max(0, min(100, raw_percentile)), components

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
    
    This simulator uses a **multi-factor regression model** calibrated for South Asian economies. It shows your **relative economic position** compared to others in your country, not exact income.
    
    **The Formula:**
    ```
    Economic Position = Base + Education + Digital Skills + Gender + 
                       Urban/Rural + Occupation + Credit Access + Age
    ```
    
    ### What Each Factor Means:
    
    - **Base Value**: Starting point based on country's economic development
    - **Education**: Each year of schooling increases earning potential
    - **Digital Skills**: Tech proficiency opening access to higher-paying modern jobs
    - **Gender**: Accounts for structural wage gaps and labor participation barriers
    - **Urban/Rural**: Cities concentrate opportunities and offer higher wages
    - **Occupation**: Different sectors have different income ceilings
    - **Credit Access**: Financial inclusion enables investment and asset building
    - **Age**: Career stage affects current earning potential
    
    **Note:** This is a simplified educational model. Real income depends on many more factors including specific skills, location, employers, market conditions, and personal circumstances.
    """)

# ============= STEP 1: PROFILE =============

st.markdown('<p class="section-header">📝 Step 1: Build Your Profile</p>', unsafe_allow_html=True)

col_input, col_preview = st.columns([2, 1], gap="large")

with col_input:
    st.markdown('<div class="pro-card">', unsafe_allow_html=True)
    
    st.markdown('<div class="input-group-label">🌍 Country</div>', unsafe_allow_html=True)
    sp_country = st.selectbox("Select your country", list(COUNTRY_DATA.keys()), key="sp_country", label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown('<div class="input-group-label">🎓 Education & Skills</div>', unsafe_allow_html=True)
    
    col_edu1, col_edu2 = st.columns(2)
    with col_edu1:
        sp_edu = st.slider("Years of Formal Education", 0, 20, 12, key="sp_edu")
    with col_edu2:
        sp_digital = st.slider("Digital Proficiency (%)", 0, 100, 50, key="sp_digital")
    
    st.markdown("---")
    st.markdown('<div class="input-group-label">👤 Demographics</div>', unsafe_allow_html=True)
    
    col_demo1, col_demo2 = st.columns(2)
    with col_demo1:
        sp_gender = st.selectbox("Gender", ["Male", "Female"], key="sp_gender")
        sp_age = st.selectbox("Age Group", ["Youth (<25)", "Adult (25-60)", "Senior (>60)"], index=1, key="sp_age")
    with col_demo2:
        sp_location = st.selectbox("Location Type", ["Rural", "Urban"], key="sp_location")
        sp_credit = st.checkbox("Has Bank Account / Credit Access", value=False, key="sp_credit")
    
    st.markdown("---")
    st.markdown('<div class="input-group-label">💼 Occupation</div>', unsafe_allow_html=True)
    sp_occ = st.selectbox("Primary Work Sector", ["Agriculture", "Industry", "Services", "Public Sector", "Unemployed"], index=2, key="sp_occ", label_visibility="collapsed")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_preview:
    st.markdown('<div class="pro-card">', unsafe_allow_html=True)
    st.markdown("### 👤 Your Profile")
    st.markdown(f"""
    <div style="line-height: 2.2; color: #e2e8f0; font-size: 0.95rem;">
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
    st.markdown('</div>', unsafe_allow_html=True)

# Calculate
g_val = 1 if sp_gender == "Female" else 0
u_val = 1 if sp_location == "Urban" else 0
sp_p, breakdown_components = calculate_percentile(sp_country, sp_edu, sp_digital, g_val, u_val, sp_occ, sp_credit, sp_age)

# ============= STEP 2: RESULTS =============

st.markdown('<p class="section-header">📊 Step 2: Your Simulation Results</p>', unsafe_allow_html=True)

group, color = get_tercile(sp_p)

result_col1, result_col2 = st.columns([1, 1], gap="large")

with result_col1:
    st.markdown(f"""
    <div class="result-container">
        <p class="metric-label">Your Economic Percentile</p>
        <div class="metric-value-large">{sp_p:.1f}<span style="font-size:2rem; vertical-align:super;">th</span></div>
        <div class="metric-group" style="color: {color};">{group}</div>
        <p style="color: #e2e8f0; margin-top: 20px; font-size: 1.05rem; line-height: 1.6;">
            This means you rank <b>higher than {sp_p:.1f}%</b> of people in {sp_country}.<br><br>
            <span style="color: #8b98a5;">In simpler terms: Out of every 100 people, you'd be in a better economic position than about <b>{int(sp_p)}</b> of them.</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

with result_col2:
    st.plotly_chart(render_gauge(sp_p, "Your Economic Position", height=300), use_container_width=True)

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
        st.plotly_chart(fig_tree, use_container_width=True)
    
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
    st.plotly_chart(fig_line, use_container_width=True)
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

insights, recommendations = generate_insights(sp_p, breakdown_components, sp_country, sp_gender, sp_location, sp_occ, sp_credit, sp_edu, sp_digital)

insight_cols = st.columns(2, gap="large")

for idx, insight in enumerate(insights):
    with insight_cols[idx % 2]:
        panel_class = f"insight-panel-{insight['type']}" if insight['type'] in ['success', 'warning'] else "insight-panel"
        st.markdown(f"""
        <div class="{panel_class}">
            <div class="insight-title">{insight['icon']} {insight['title']}</div>
            <p style="color: #e2e8f0; font-size: 0.95rem; line-height: 1.6; margin: 0;">{insight['text']}</p>
        </div>
        """, unsafe_allow_html=True)

# Recommendations
if recommendations:
    st.markdown('<p class="section-header">🎯 Personalized Recommendations</p>', unsafe_allow_html=True)
    st.markdown('<div class="pro-card">', unsafe_allow_html=True)
    st.markdown('<p style="color: #8b98a5; margin-bottom: 15px;">Based on your profile, here are the most impactful actions to improve your economic position:</p>', unsafe_allow_html=True)
    
    for i, rec in enumerate(recommendations, 1):
        priority_color = "#ef4444" if rec['priority'] == "HIGH" else "#f59e0b"
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px; margin-bottom: 12px; border-left: 3px solid {priority_color};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <b style="color: #ffffff; font-size: 1.05rem;">{i}. {rec['action']}</b>
                <span style="background: {priority_color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">{rec['priority']}</span>
            </div>
            <p style="color: #e2e8f0; margin: 0; line-height: 1.6;">{rec['detail']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============= COMPARISON FEATURE =============

st.markdown('<p class="section-header">🔄 Step 5: Compare with Another Profile</p>', unsafe_allow_html=True)

st.markdown("""
<div class="comparison-card">
    <h3 style="text-align: center; color: #ffffff; margin-bottom: 10px;">Profile Comparison Tool</h3>
    <p style="text-align: center; color: #8b98a5; margin-bottom: 30px;">Create a second profile with the same attributes to see how different factors affect economic outcomes</p>
</div>
""", unsafe_allow_html=True)

# Comparison inputs
comp_col1, comp_col2 = st.columns([1, 1], gap="large")

with comp_col1:
    st.markdown('<div class="pro-card" style="border: 2px solid #3b82f6;">', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; margin-bottom: 20px;"><span class="profile-badge badge-primary">Profile A (You)</span></div>', unsafe_allow_html=True)
    
    st.markdown(f"""
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
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with comp_col2:
    st.markdown('<div class="pro-card" style="border: 2px solid #10b981;">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)

# Stunning Circular Comparison Visualization
st.markdown("---")
st.markdown("### 🎯 Visual Comparison Dashboard")

viz_comp_col1, viz_comp_col2, viz_comp_col3 = st.columns([1, 2, 1], gap="large")

with viz_comp_col1:
    # Profile A Donut
    fig_donut_a = go.Figure(data=[go.Pie(
        values=[sp_p, 100-sp_p],
        hole=0.7,
        marker=dict(colors=['#3b82f6', 'rgba(59, 130, 246, 0.1)'], line=dict(color='#0f1419', width=2)),
        textinfo='none',
        hoverinfo='skip',
        showlegend=False
    )])
    fig_donut_a.add_annotation(
        text=f"<b>{sp_p:.0f}%</b>",
        x=0.5, y=0.5,
        font=dict(size=40, color='#60a5fa', family='Inter'),
        showarrow=False
    )
    fig_donut_a.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        height=250,
        margin=dict(t=10, b=10, l=10, r=10),
        annotations=[
            dict(text=f"<b>{sp_p:.0f}%</b>", x=0.5, y=0.55, font=dict(size=36, color='#60a5fa'), showarrow=False),
            dict(text="Profile A", x=0.5, y=0.35, font=dict(size=14, color='#8b98a5'), showarrow=False)
        ]
    )
    st.plotly_chart(fig_donut_a, use_container_width=True)

with viz_comp_col2:
    # Difference indicator
    diff = comp_p - sp_p
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
    st.plotly_chart(fig_donut_b, use_container_width=True)

# Detailed factor comparison
st.markdown("### 📊 Factor-by-Factor Breakdown")

# Create comparison dataframe
comparison_data = []
for factor in breakdown_components.keys():
    comparison_data.append({
        "Factor": factor,
        "Profile A": f"{breakdown_components[factor]:+.1f}",
        "Profile B": f"{comp_components[factor]:+.1f}",
        "Difference": f"{comp_components[factor] - breakdown_components[factor]:+.1f}"
    })

comp_df = pd.DataFrame(comparison_data)
st.dataframe(comp_df, use_container_width=True, hide_index=True)

# Side-by-side radar chart with normalized values
st.markdown("### 🕸️ Multi-Dimensional Comparison")

# Prepare data with actual values and percentages
categories = ['Education\n(Years)', 'Digital Skills\n(%)', 'Occupation\n(Points)', 'Urban\n(Points)', 'Credit\n(Points)']

# Get raw input values for better comparison
profile_a_raw = [sp_edu, sp_digital, breakdown_components['Occupation'], breakdown_components['Urban Advantage'], breakdown_components['Credit Access']]
profile_b_raw = [comp_edu, comp_digital, comp_components['Occupation'], comp_components['Urban Advantage'], comp_components['Credit Access']]

# Normalize to 0-100 scale for better visualization
def normalize_value(value, max_val):
    return (value / max_val) * 100 if max_val > 0 else 0

profile_a_normalized = [
    normalize_value(sp_edu, 20),  # Education out of 20
    sp_digital,  # Already 0-100
    normalize_value(breakdown_components['Occupation'], 15),  # Occupation max is 15
    normalize_value(breakdown_components['Urban Advantage'], 12),  # Urban max is 12
    normalize_value(breakdown_components['Credit Access'], 6)  # Credit max is 6
]

profile_b_normalized = [
    normalize_value(comp_edu, 20),
    comp_digital,
    normalize_value(comp_components['Occupation'], 15),
    normalize_value(comp_components['Urban Advantage'], 12),
    normalize_value(comp_components['Credit Access'], 6)
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

st.plotly_chart(fig_radar, use_container_width=True)

# Add explanation
st.markdown("""
<div style="background: rgba(59, 130, 246, 0.05); padding: 15px; border-radius: 8px; border-left: 3px solid #3b82f6; margin-top: 15px;">
    <p style="color: #8b98a5; font-size: 0.9rem; margin: 0;">
        <b style="color: #e2e8f0;">How to read this chart:</b> Each axis represents a different factor, normalized to a 0-100 scale. 
        Larger areas indicate stronger profiles. The blue area shows Profile A (you), and the green area shows Profile B (comparison).
    </p>
</div>
""", unsafe_allow_html=True)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #8b98a5; font-size: 0.85rem; padding: 20px 0;">
    <b>Income Simulator v4.0</b> | Enhanced with Visual Analytics, Comparison Tools & Plain-Language Insights<br>
    Calibrated for South Asian socio-economic contexts | Educational purposes only
</div>
""", unsafe_allow_html=True)