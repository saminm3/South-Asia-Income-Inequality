import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Income Simulation",
    page_icon="💰",
    layout="wide"
)

# Load custom CSS
try:
    with open('assets/dashboard.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Country-specific factors (based on regional data)
COUNTRY_DATA = {
    'Bangladesh': {'base': 28, 'education_weight': 0.32, 'urban_bonus': 8},
    'India': {'base': 25, 'education_weight': 0.35, 'urban_bonus': 12},
    'Pakistan': {'base': 30, 'education_weight': 0.28, 'urban_bonus': 10},
    'Nepal': {'base': 32, 'education_weight': 0.30, 'urban_bonus': 7},
    'Sri Lanka': {'base': 35, 'education_weight': 0.30, 'urban_bonus': 11}
}

def calculate_percentile(country, education, digital_access, gender_value, urban_value):
    """
    Calculate income percentile based on various factors
    
    Args:
        country: Selected country
        education: Years of education (0-20)
        digital_access: Digital access percentage (0-100)
        gender_value: 0 for male, 1 for female
        urban_value: 0 for rural, 1 for urban
    
    Returns:
        Estimated income percentile (1-99)
    """
    base = COUNTRY_DATA[country]['base']
    edu_weight = COUNTRY_DATA[country]['education_weight']
    country_urban = COUNTRY_DATA[country]['urban_bonus']
    
    # Calculate contributions
    education_contrib = (education / 20) * 100 * edu_weight
    digital_contrib = (digital_access / 100) * 20
    gender_penalty = gender_value * -10  # Gender pay gap
    urban_bonus = urban_value * country_urban
    
    percentile = base + education_contrib + digital_contrib + gender_penalty + urban_bonus
    
    # Clamp to valid range
    return max(1, min(99, percentile))

# Title and description
st.title("💰 Income Inequality Simulator")
st.markdown("""
Model how different factors affect income position within a country. This tool helps understand 
the impact of education, digital access, gender, and location on economic inequality.

⚠️ **Disclaimer:** This is an educational tool using simplified assumptions, not a predictive model for individual cases.
""")

# Mode selection
mode = st.radio(
    "Select Mode:",
    ["Single Profile", "Compare Scenarios"],
    horizontal=True,
    help="Single Profile: Analyze one person's factors. Compare: See multiple profiles side-by-side"
)

if mode == "Single Profile":
    # ========== SINGLE PROFILE MODE ==========
    
    st.sidebar.header("👤 Adjust Profile Factors")
    
    country = st.sidebar.selectbox("Country", list(COUNTRY_DATA.keys()))
    education = st.sidebar.slider("Years of Education", 0, 20, 10, help="Formal years of schooling")
    digital_access = st.sidebar.slider("Digital Access (%)", 0, 100, 50, help="Access to internet and digital tools")
    gender = st.sidebar.selectbox("Gender", ["Male", "Female"])
    location = st.sidebar.selectbox("Location", ["Rural", "Urban"])
    
    # Convert to numeric values
    gender_value = 1 if gender == "Female" else 0
    urban_value = 1 if location == "Urban" else 0
    
    # Calculate percentile
    percentile = calculate_percentile(country, education, digital_access, gender_value, urban_value)
    
    # Display result
    st.subheader(f"📊 Estimated Income Percentile in {country}")
    
    # Gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentile,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Income Percentile", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 33], 'color': "lightcoral"},
                {'range': [33, 66], 'color': "lightyellow"},
                {'range': [66, 100], 'color': "lightgreen"}
            ],
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 50}
        }
    ))
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Interpretation
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Percentile", f"{percentile:.1f}")
    
    with col2:
        if percentile < 33:
            group = "Lower Income"
            emoji = "🔴"
        elif percentile < 66:
            group = "Middle Income"
            emoji = "🟡"
        else:
            group = "Upper Income"
            emoji = "🟢"
        st.metric("Income Group", f"{emoji} {group}")
    
    with col3:
        position = f"Top {100-percentile:.0f}%" if percentile > 50 else f"Bottom {percentile:.0f}%"
        st.metric("Position", position)
    
    # Detailed interpretation
    st.divider()
    st.subheader("📝 Interpretation")
    
    if percentile < 33:
        st.error(f"""
        **Lower Income Group** - This profile falls in the bottom third of income distribution in {country}.
        
        Factors contributing to this position:
        - Education: {education} years (regional average: ~12 years)
        - Digital access: {digital_access}% (regional average: ~60%)
        - Location: {location} (urban areas typically have {COUNTRY_DATA[country]['urban_bonus']}% income boost)
        - Gender: {gender} (gender pay gap exists across South Asia)
        """)
    elif percentile < 66:
        st.warning(f"""
        **Middle Income Group** - This profile falls in the middle third of income distribution in {country}.
        
        This represents a moderate economic position with room for improvement through:
        - Increased education and skills training
        - Better digital access and technology adoption
        - Career advancement opportunities
        """)
    else:
        st.success(f"""
        **Upper Income Group** - This profile falls in the top third of income distribution in {country}.
        
        This advantaged position is typically associated with:
        - Higher education levels: {education} years
        - Good digital access: {digital_access}%
        - Urban location benefits (where applicable)
        - Access to better employment opportunities
        """)

else:
    # ========== COMPARISON MODE ==========
    
    st.subheader("🔍 Compare Multiple Profiles Side-by-Side")
    
    num_scenarios = st.slider("Number of profiles to compare:", 2, 3, 2)
    
    cols = st.columns(num_scenarios)
    scenarios = []
    
    # Create profile inputs
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"### 👤 Profile {i+1}")
            country = st.selectbox(f"Country", list(COUNTRY_DATA.keys()), key=f"country_{i}")
            education = st.slider(f"Education (years)", 0, 20, 10, key=f"edu_{i}")
            digital = st.slider(f"Digital Access (%)", 0, 100, 50, key=f"digital_{i}")
            gender = st.selectbox(f"Gender", ["Male", "Female"], key=f"gender_{i}")
            location = st.selectbox(f"Location", ["Rural", "Urban"], key=f"loc_{i}")
            
            gender_val = 1 if gender == "Female" else 0
            urban_val = 1 if location == "Urban" else 0
            
            percentile = calculate_percentile(country, education, digital, gender_val, urban_val)
            
            scenarios.append({
                'name': f"Profile {i+1}",
                'country': country,
                'education': education,
                'digital': digital,
                'gender': gender,
                'location': location,
                'percentile': percentile
            })
    
    # Display comparison gauges
    st.divider()
    st.subheader("📊 Comparison Results")
    
    gauge_cols = st.columns(num_scenarios)
    for i, (gauge_col, scenario) in enumerate(zip(gauge_cols, scenarios)):
        with gauge_col:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=scenario['percentile'],
                title={'text': scenario['name']},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 33], 'color': "lightcoral"},
                        {'range': [33, 66], 'color': "lightyellow"},
                        {'range': [66, 100], 'color': "lightgreen"}
                    ]
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            st.caption(f"{scenario['country']} | {scenario['education']}y edu | {scenario['gender']} | {scenario['location']}")
    
    # Comparison table
    st.divider()
    st.subheader("📋 Side-by-Side Comparison")
    
    comparison_df = pd.DataFrame([
        {
            'Profile': s['name'],
            'Country': s['country'],
            'Education': f"{s['education']} years",
            'Digital Access': f"{s['digital']}%",
            'Gender': s['gender'],
            'Location': s['location'],
            'Percentile': f"{s['percentile']:.1f}"
        }
        for s in scenarios
    ])
    
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    # Bar chart comparison
    st.subheader("📊 Percentile Comparison")
    
    fig_bar = go.Figure(go.Bar(
        x=[s['name'] for s in scenarios],
        y=[s['percentile'] for s in scenarios],
        text=[f"{s['percentile']:.1f}" for s in scenarios],
        textposition='auto',
        marker_color=[
            'lightcoral' if s['percentile'] < 33 
            else 'lightyellow' if s['percentile'] < 66 
            else 'lightgreen' 
            for s in scenarios
        ]
    ))
    
    fig_bar.update_layout(
        yaxis_title="Income Percentile",
        yaxis_range=[0, 100],
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Key differences
    st.subheader("🔍 Key Differences")
    
    max_profile = max(scenarios, key=lambda x: x['percentile'])
    min_profile = min(scenarios, key=lambda x: x['percentile'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success(f"""
        **Highest Percentile:** {max_profile['name']}
        - Percentile: {max_profile['percentile']:.1f}
        - Country: {max_profile['country']}
        - Education: {max_profile['education']} years
        """)
    
    with col2:
        st.error(f"""
        **Lowest Percentile:** {min_profile['name']}
        - Percentile: {min_profile['percentile']:.1f}
        - Country: {min_profile['country']}
        - Education: {min_profile['education']} years
        """)
    
    diff = max_profile['percentile'] - min_profile['percentile']
    st.info(f"**Inequality Gap:** {diff:.1f} percentile points between highest and lowest profiles")

# Export functionality
st.divider()
st.subheader("📥 Export Results")

col1, col2 = st.columns(2)

with col1:
    # Export chart
    if 'fig' in locals():
        img_bytes = fig.to_image(format="png", width=1200, height=600)
        st.download_button(
            "📥 Download Chart (PNG)",
            data=img_bytes,
            file_name="income_simulation.png",
            mime="image/png",
            use_container_width=True
        )

with col2:
    # Export comparison data if in comparison mode
    if mode == "Compare Scenarios" and 'comparison_df' in locals():
        csv = comparison_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Comparison (CSV)",
            data=csv,
            file_name="income_comparison.csv",
            mime="text/csv",
            use_container_width=True
        )
    elif mode == "Single Profile":
        # Create single profile data
        profile_data = pd.DataFrame([{
            'Country': country,
            'Education (years)': education,
            'Digital Access (%)': digital_access,
            'Gender': gender,
            'Location': location,
            'Income Percentile': f"{percentile:.1f}"
        }])
        csv = profile_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Profile (CSV)",
            data=csv,
            file_name="income_profile.csv",
            mime="text/csv",
            use_container_width=True
        )

# Methodology explanation
st.divider()
with st.expander("ℹ️ How This Simulation Works"):
    st.markdown("""
    ### Calculation Formula
    
    ```
    Income Percentile = Base + (Education × Weight) + (Digital × 0.20) + (Gender × -10) + (Urban × Bonus)
    ```
    
    ### Country-Specific Parameters
    
    Each country has different baseline inequality levels and education impact weights:
    
    | Country | Base Percentile | Education Weight | Urban Bonus |
    |---------|----------------|------------------|-------------|
    | Bangladesh | 28 | 0.32 | +8% |
    | India | 25 | 0.35 | +12% |
    | Pakistan | 30 | 0.28 | +10% |
    | Nepal | 32 | 0.30 | +7% |
    | Sri Lanka | 35 | 0.30 | +11% |
    
    ### Factors Explained
    
    1. **Education (0-20 years):** More education typically correlates with higher income
    2. **Digital Access (0-100%):** Access to internet and digital tools creates economic opportunities
    3. **Gender:** Gender pay gap exists across South Asia (-10 percentile points for females)
    4. **Location:** Urban areas offer more employment opportunities and higher wages
    
    ### Important Notes
    
    - ⚠️ **Simplified model:** This is an educational tool, not a precise predictor
    - 📊 **Regional averages:** Parameters based on aggregate regional data
    - 🚫 **Not for individual prediction:** Cannot predict specific individual outcomes
    - 📚 **Educational purpose:** Designed to illustrate factors affecting inequality
    
    ### Data Sources
    
    Parameters derived from:
    - World Bank inequality data
    - UNDP Human Development Reports
    - Regional wage and employment studies
    """)

# Footer
st.divider()
st.caption("Income Inequality Simulator | South Asia Inequality Analysis Platform")
st.caption("💡 Educational tool - Not for individual income prediction")