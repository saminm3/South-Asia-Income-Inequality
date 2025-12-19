import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Income Simulator",
    page_icon="💸",
    layout="wide"
)

# Load custom CSS
try:
    with open('assets/dashboard.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Standardized COUNTRY_DATA with specifically requested coefficients
COUNTRY_DATA = {
    'Bangladesh': {'base': 25, 'education_weight': 0.32, 'urban_bonus': 8},
    'India': {'base': 22, 'education_weight': 0.35, 'urban_bonus': 12},
    'Pakistan': {'base': 20, 'education_weight': 0.30, 'urban_bonus': 10},
    'Nepal': {'base': 22, 'education_weight': 0.32, 'urban_bonus': 7},
    'Sri Lanka': {'base': 25, 'education_weight': 0.32, 'urban_bonus': 11}
}

def calculate_percentile(country, edu, digital, gender, urban, occupation="Services", credit=False, age="Adult"):
    """
    Enhanced Multi-Factor Formula:
    p = base + (edu/20)*40*weight + (digital/100)*15 + gender*(-8) + urban*bonus + occ_val + credit_val + age_val
    """
    data = COUNTRY_DATA.get(country, COUNTRY_DATA['India'])
    base = data['base']
    weight = data['education_weight']
    bonus = data['urban_bonus']
    
    # Factor Mappings
    occ_map = {"Agriculture": 0, "Industry": 8, "Services": 12, "Public Sector": 15, "Unemployed": -5}
    occ_val = occ_map.get(occupation, 10)
    
    credit_val = 6 if credit else 0
    
    age_map = {"Youth (<25)": -4, "Adult (25-60)": 6, "Senior (>60)": 2}
    age_val = age_map.get(age, 4)
    
    percentile = base + (edu/20)*40*weight + (digital/100)*15 + gender*(-8) + urban*bonus + occ_val + credit_val + age_val
    return max(0, min(100, percentile))

def get_tercile(p):
    if p < 33.33: return "Lower Tercile", "#ef4444"
    if p < 66.66: return "Middle Tercile", "#f59e0b"
    return "Upper Tercile", "#10b981"

def render_gauge(p, title="", height=250):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=p,
        title={'text': title, 'font': {'size': 18, 'color': 'white'}},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "white"},
            'bgcolor': "rgba(0,0,0,0)",
            'steps': [
                {'range': [0, 33.33], 'color': "rgba(239, 68, 68, 0.2)"},
                {'range': [33.33, 66.66], 'color': "rgba(245, 158, 11, 0.2)"},
                {'range': [66.66, 100], 'color': "rgba(16, 185, 129, 0.2)"}
            ],
            'threshold': {
                'line': {'color': "#fff", 'width': 4},
                'thickness': 0.75,
                'value': p
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "white", 'family': "Inter"},
        height=height,
        margin=dict(l=30, r=30, t=50, b=20)
    )
    return fig

# Title and description
st.title("💸 Income Simulator")
st.markdown("""
### Explore how socio-economic factors determine economic standing in South Asia.
Adjust parameters like education, digital access, and location to see their impact on income percentile position.
""")

# --- ELABORATED EXPLANATIONS & METHODOLOGY ---

# 1. Methodology Section (Expandable)
with st.expander("🔬 Core Methodology & Calculation Logic", expanded=False):
    st.markdown("""
    ### How is your Economic Percentile Calculated?
    The simulation uses a multi-factor regression model tailored for the South Asian context. 
    It doesn't just look at income; it looks at **opportunity drivers**.
    
    #### 📐 The Mathematical Formula:
    `percentile = Base + (Education Factor) + (Digital Premium) + (Gender Variance) + (Urban Bonus) + (Occupation Weight) + (Access to Credit) + (Age Adjustment)`
    
    1. **Base Standing**: Each country starts with a baseline representing the 'Floor' of its productive capacity.
    2. **Education (Weighting)**: Every year of schooling acts as a multiplier of competitive potential.
    3. **Digital Premium**: Represents the 'Tech-Multiplier'. Digital access opens higher-paying modern service-sector roles.
    4. **Gender Gap**: Accounts for the structural 'wage penalty' and labor force participation gap.
    5. **Urban Advantage**: Reflects the concentration of economic activity and high-density markets in cities.
    6. **Occupation Sector**: Weighs the stability and income ceiling of different industries (Services/Public Sector vs. Agriculture).
    7. **Financial Inclusion**: Access to credit acts as a leverage for asset building and income smoothing.
    """)

mode = st.tabs(["👤 Single Profile Analysis", "👥 Comparative Analysis"])

with mode[0]:
    # --- SINGLE PROFILE MODE ---
    col_input, col_result = st.columns([1, 2])
    
    with col_input:
        st.subheader("Profile Definition")
        st.info("Adjust the sliders below to build a hypothetical citizen profile.")
        sp_country = st.selectbox("Assign Nationality", list(COUNTRY_DATA.keys()), key="sp_country")
        
        c1, c2 = st.columns(2)
        with c1:
            sp_edu = st.slider("Years of Formal Education", 0, 20, 12, key="sp_edu")
            sp_gender = st.selectbox("Identify Gender", ["Male", "Female"], key="sp_gender")
            sp_age = st.selectbox("Age Group", ["Youth (<25)", "Adult (25-60)", "Senior (>60)"], index=1, key="sp_age")
        with c2:
            sp_digital = st.slider("Digital Proficiency (%)", 0, 100, 75, key="sp_digital")
            sp_location = st.selectbox("Setting", ["Rural", "Urban"], key="sp_location")
            sp_credit = st.checkbox("Access to Formal Credit?", value=True, key="sp_credit")
            
        sp_occ = st.selectbox("Primary Occupation Sector", ["Agriculture", "Industry", "Services", "Public Sector", "Unemployed"], index=2, key="sp_occ")
        
        g_val = 1 if sp_gender == "Female" else 0
        u_val = 1 if sp_location == "Urban" else 0
        sp_p = calculate_percentile(sp_country, sp_edu, sp_digital, g_val, u_val, sp_occ, sp_credit, sp_age)
        
    with col_result:
        group, color = get_tercile(sp_p)
        
        st.html(f"""
        <div class='glass-panel' style='text-align: center; padding: 2rem; border-top: 4px solid {color};'>
            <p style='color: var(--text-secondary); text-transform: uppercase; margin-bottom: 0;'>Estimated Standing</p>
            <h1 style='margin-top: 0; font-size: 3.5rem;'>{sp_p:.1f}th</h1>
            <p style='color: {color}; font-weight: bold; font-size: 1.4rem;'>{group}</p>
        </div>
        """)
        
        st.plotly_chart(render_gauge(sp_p, "Position in Income Distribution"), use_container_width=True)
        
        st.subheader("📝 Elaborated Result Interpretation")
        
        def generate_sp_narrative():
            c_data = COUNTRY_DATA[sp_country]
            edu_contrib = (sp_edu/20)*40*c_data['education_weight']
            
            narrative = f"""
            ### Understanding the {sp_p:.1f}th Percentile Result
            
            **1. What This Means for {sp_country}:**
            Being in the **{group}** suggests that this profile earns more than **{sp_p:.0f}%** 
            of the population in {sp_country}. This person likely represents the {'modern professional class' if sp_p > 75 else 'core middle class' if sp_p > 40 else 'working class or vulnerable population'}.

            **2. The New Multifaceted Drivers:**
            - **Education & Skills**: Contributes **{edu_contrib:.1f} points**. Formal education remains the strongest predictor of high-income bracket placement.
            - **Industry Premium**: Working in the **{sp_occ}** sector provides a specific 'stability weight' to your standing.
            - **The Finance Factor**: Having **{'access to credit' if sp_credit else 'no credit access'}** significantly impacts the ability to leverage opportunities and withstand shocks.
            
            **3. Demographic Landscape:**
            The result accounts for being a **{sp_age} {sp_gender}** in an **{sp_location}** setting. 
            In many South Asian countries, these structural factors can shift an individual's standing by over 30 percentile points, 
            underscoring the **deep-seated systemic gaps** between different demographic groups.
            """
            return narrative

        st.markdown(generate_sp_narrative())

with mode[1]:
    # --- COMPARISON MODE ---
    st.subheader("👥 Comparative Structural Scenario Analysis")
    st.markdown("""
    Compare different profiles to visualize how systemic factors create divergence.
    """)
    
    num_p = st.number_input("Select profiles to compare:", 2, 3, 2, key="num_p_comp")
    comp_cols = st.columns(num_p)
    profiles = []
    
    for i in range(num_p):
        with comp_cols[i]:
            st.html(f"<div style='padding:1rem; background:rgba(255,255,255,0.03); border-radius:10px;'>")
            st.markdown(f"#### Profile {i+1}")
            c_country = st.selectbox("Country", list(COUNTRY_DATA.keys()), key=f"c_country_{i}")
            c_edu = st.slider("Education yrs", 0, 20, 8 + (i*4), key=f"c_edu_{i}")
            c_occ = st.selectbox("Sector", ["Agriculture", "Industry", "Services", "Public Sector", "Unemployed"], index=i+1 if i<4 else 2, key=f"c_occ_{i}")
            c_gender = st.selectbox("Gender", ["Male", "Female"], index=i%2, key=f"c_gender_{i}")
            c_credit = st.checkbox("Credit Access", value=True if i==0 else False, key=f"c_credit_{i}")
            
            cg_val = 1 if c_gender == "Female" else 0
            # Constants for simplified comparison
            c_p = calculate_percentile(c_country, c_edu, 50, cg_val, 1, c_occ, c_credit, "Adult (25-60)")
            
            profiles.append({
                "Profile": f"Profile {i+1}", "Country": c_country, "Edu": c_edu,
                "Sector": c_occ, "Gender": c_gender, "Credit": "Yes" if c_credit else "No", "Percentile": round(c_p, 2)
            })
            
            st.plotly_chart(render_gauge(c_p, f"P{i+1}: {round(c_p, 1)}%", height=180), use_container_width=True)
            st.html("</div>")

    # Comparison Graphics
    st.divider()
    c_left, c_right = st.columns([1, 1])
    df_comp = pd.DataFrame(profiles)
    
    with c_left:
        st.markdown("### 📊 Comparison Matrix")
        st.dataframe(df_comp, use_container_width=True, hide_index=True)
        st.download_button("📥 Export Analysis CSV", df_comp.to_csv(index=False).encode('utf-8'), "comp_export.csv", "text/csv")
        
    with c_right:
        st.markdown("### 📈 Visual Divergence")
        fig_bar = px.bar(df_comp, x="Profile", y="Percentile", color="Profile", text="Percentile",
                         color_discrete_sequence=px.colors.qualitative.G10)
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=350)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Elaborated Comparative Analysis
    st.markdown("---")
    st.subheader("🔬 Comparative Logic & Findings")
    
    if num_p >= 2:
        p1, p2 = profiles[0], profiles[1]
        gap = abs(p1['Percentile'] - p2['Percentile'])
        
        st.markdown(f"""
        ### The 'Inequality Gap' Analysis
        
        This comparison reveals a **{gap:.1f} percentage point gap** in economic standing. 
        Notice how differences in **Occupation Sector** and **Credit Access** can often outweigh years of 
        formal education in determining an individual's actual ability to move up the income ladder.
        
        **Systemic Insight**: When a profile with high education (like Profile 2) stays in a lower percentile than Profile 1, 
        it usually indicates that **Structural Barriers** (like Lack of Credit or Gender Bias) are neutralizing their human capital investment.
        """)

# Footer
st.divider()
st.caption("Income Simulator v2.2 | Multi-Factor Dynamic Accuracy Engine")
st.caption("Powered by regional development data. Factors calibrated based on South Asian labor market volatility.")