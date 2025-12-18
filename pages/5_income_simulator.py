import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from scipy.stats import norm

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
    'Bangladesh': {'base': 20, 'education_weight': 0.35, 'urban_bonus': 8, 'std': 15},
    'India': {'base': 18, 'education_weight': 0.38, 'urban_bonus': 12, 'std': 18},
    'Pakistan': {'base': 22, 'education_weight': 0.30, 'urban_bonus': 10, 'std': 16},
    'Nepal': {'base': 25, 'education_weight': 0.32, 'urban_bonus': 7, 'std': 14},
    'Sri Lanka': {'base': 28, 'education_weight': 0.32, 'urban_bonus': 11, 'std': 15}
}

OCCUPATION_DATA = {
    'Unskilled Labor': {'bonus': 0, 'desc': 'Basic manual labor'},
    'Agriculture/Farming': {'bonus': 2, 'desc': 'Small scale farming'},
    'Service/Retail': {'bonus': 5, 'desc': 'Service sector jobs'},
    'Skilled Trade/Technical': {'bonus': 10, 'desc': 'Electricians, mechanics, etc.'},
    'Clerical/Office': {'bonus': 12, 'desc': 'Admin and support roles'},
    'Professional/Academic': {'bonus': 20, 'desc': 'Teachers, doctors, engineers'},
    'Managerial/Business': {'bonus': 25, 'desc': 'Management roles'},
    'Executive/High Tech': {'bonus': 35, 'desc': 'Senior leadership, tech specialists'}
}

def calculate_percentile(country, education, digital_access, gender_value, urban_value, occupation_bonus):
    """
    Calculate income percentile based on various factors
    """
    base = COUNTRY_DATA[country]['base']
    edu_weight = COUNTRY_DATA[country]['education_weight']
    country_urban = COUNTRY_DATA[country]['urban_bonus']
    
    # Calculate contributions
    education_contrib = (education / 20) * 100 * edu_weight
    digital_contrib = (digital_access / 100) * 15
    gender_penalty = gender_value * -10  # Gender pay gap
    urban_bonus = urban_value * country_urban
    
    percentile = base + education_contrib + digital_contrib + gender_penalty + urban_bonus + occupation_bonus
    
    # Add some randomness for simulation "feel" if needed, but keeping deterministic for now
    
    return max(1, min(99, percentile))

def plot_bell_curve(percentile, country):
    """Plot the user's position on a bell curve"""
    # Generate data for the bell curve
    x = np.linspace(0, 100, 1000)
    # Using a standard normal distribution roughly mapped to 0-100 scale
    # Typically, income is log-normal, but for percentile ranks, it's uniform 0-100 technically.
    # HOWEVER, for the "Income Distribution" visual, we often show a bell curve of *income levels*,
    # but here we are plotting the *percentile* itself? 
    # Actually, let's visualize the "Density of Population" vs "Income Level" and place the user.
    # But since we only have a calculated 'Percentile' (0-100), navigating back to exact income is hard without real data.
    # So we will visualize it as a relative standing visualization.
    
    # Let's create a stylized distribution curve representing "Frequency" vs "Economic Status"
    mean = 50
    std_dev = 20
    y = norm.pdf(x, mean, std_dev)
    
    fig = go.Figure()
    
    # Add the bell curve
    fig.add_trace(go.Scatter(
        x=x, y=y, 
        mode='lines', 
        name='Population',
        fill='tozeroy',
        line=dict(color='rgba(100, 100, 100, 0.2)'),
        fillcolor='rgba(100, 100, 100, 0.1)'
    ))
    
    # Add user position
    user_y = norm.pdf(percentile, mean, std_dev)
    
    fig.add_trace(go.Scatter(
        x=[percentile], 
        y=[user_y],
        mode='markers+text',
        name='You',
        marker=dict(color='#FF4B4B', size=15, symbol='diamond'),
        text=['You'],
        textposition="top center",
        textfont=dict(size=14, color='#FF4B4B')
    ))
    
    # Add regions
    fig.add_vline(x=33, line_width=1, line_dash="dash", line_color="gray")
    fig.add_vline(x=66, line_width=1, line_dash="dash", line_color="gray")
    
    fig.add_annotation(x=16.5, y=0.002, text="Lower Income", showarrow=False, font=dict(size=10, color="gray"))
    fig.add_annotation(x=50, y=0.002, text="Middle Income", showarrow=False, font=dict(size=10, color="gray"))
    fig.add_annotation(x=83.5, y=0.002, text="Upper Income", showarrow=False, font=dict(size=10, color="gray"))
    
    fig.update_layout(
        title="👥 Your Position in Population Distribution",
        xaxis_title="Relative Economic Status (Percentile)",
        yaxis_title="Population Density",
        showlegend=False,
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, range=[0, 100]),
        yaxis=dict(showticklabels=False, showgrid=False)
    )
    
    return fig

# Title and description
st.title("💰 Income Inequality Simulator")
st.markdown("""
Model how different factors affect income position within a country. This tool helps understand 
the impact of education, digital access, gender, location, and occupation on economic inequality.

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
    
    st.sidebar.header("� Adjust Profile Factors")
    
    # Input groups
    with st.sidebar.expander("🌍 Demographics", expanded=True):
        country = st.selectbox("Country", list(COUNTRY_DATA.keys()))
        gender = st.selectbox("Gender", ["Male", "Female"])
        location = st.selectbox("Location", ["Rural", "Urban"])
        
    with st.sidebar.expander("🎓 Education & Work", expanded=True):
        education = st.slider("Years of Education", 0, 20, 10, help="Formal years of schooling")
        occupation = st.selectbox("Occupation Type", list(OCCUPATION_DATA.keys()), index=2)
        st.caption(f"_{OCCUPATION_DATA[occupation]['desc']}_")
        
    with st.sidebar.expander("📱 Technology", expanded=True):
        digital_access = st.slider("Digital Access (%)", 0, 100, 50, help="Access to internet and digital tools")
    
    # Calculate values
    gender_value = 1 if gender == "Female" else 0
    urban_value = 1 if location == "Urban" else 0
    occ_bonus = OCCUPATION_DATA[occupation]['bonus']
    
    # Main Calculation
    percentile = calculate_percentile(country, education, digital_access, gender_value, urban_value, occ_bonus)
    
    # --- Main Dashboard Area ---
    
    # 1. Headline Stats
    st.subheader(f"📊 Analysis for {country}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Estimated Percentile", f"{percentile:.1f}", help="0=Lowest, 100=Highest")
    
    with col2:
        if percentile < 33:
            group = "Lower Income"
            color = "red"
        elif percentile < 66:
            group = "Middle Income"
            color = "orange"
        else:
            group = "Upper Income"
            color = "green"
        st.markdown(f"**Economic Group:**")
        st.markdown(f"<h3 style='color:{color}; margin-top:-10px'>{group}</h3>", unsafe_allow_html=True)
    
    with col3:
        position = f"Top {100-percentile:.0f}%" if percentile > 50 else f"Bottom {percentile:.0f}%"
        st.metric("Relative Position", position)
        
    # 2. Visualizations
    c1, c2 = st.columns([1, 1])
    
    with c1:
        # Gauge chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=percentile,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 33], 'color': "lightcoral"},
                    {'range': [33, 66], 'color': "lightyellow"},
                    {'range': [66, 100], 'color': "lightgreen"}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': percentile}
            }
        ))
        fig_gauge.update_layout(height=300, margin=dict(t=30, b=10, l=30, r=30))
        st.plotly_chart(fig_gauge, use_container_width=True)
        
    with c2:
        # Distribution Plot
        fig_dist = plot_bell_curve(percentile, country)
        st.plotly_chart(fig_dist, use_container_width=True)

    # 3. Growth Potential Analysis
    st.divider()
    st.subheader("� Growth Potential: What if?")
    st.markdown("See how changes in your profile could potentially increase your economic standing:")
    
    cols = st.columns(4)
    
    # Scenario 1: +EDUCATION
    if education < 18:
        new_edu = min(20, education + 2)
        p_edu = calculate_percentile(country, new_edu, digital_access, gender_value, urban_value, occ_bonus)
        growth = p_edu - percentile
        with cols[0]:
            st.info(f"**+2 Years Education**\n\nPercentile: {p_edu:.1f}\n\n**+{growth:.1f} pts** 📈")
    
    # Scenario 2: +DIGITAL
    if digital_access < 90:
        new_dig = min(100, digital_access + 20)
        p_dig = calculate_percentile(country, education, new_dig, gender_value, urban_value, occ_bonus)
        growth = p_dig - percentile
        with cols[1]:
            st.info(f"**+20% Digital Skills**\n\nPercentile: {p_dig:.1f}\n\n**+{growth:.1f} pts** 📈")
            
    # Scenario 3: URBAN MIGRATION
    if urban_value == 0:
        p_urb = calculate_percentile(country, education, digital_access, gender_value, 1, occ_bonus)
        growth = p_urb - percentile
        with cols[2]:
            st.info(f"**Move to Urban Area**\n\nPercentile: {p_urb:.1f}\n\n**+{growth:.1f} pts** 📈")
            
    # Scenario 4: BETTER JOB
    curr_occ_idx = list(OCCUPATION_DATA.keys()).index(occupation)
    if curr_occ_idx < len(OCCUPATION_DATA) - 1:
        next_occ = list(OCCUPATION_DATA.keys())[curr_occ_idx + 2] if curr_occ_idx + 2 < len(OCCUPATION_DATA) else list(OCCUPATION_DATA.keys())[-1]
        next_bonus = OCCUPATION_DATA[next_occ]['bonus']
        p_job = calculate_percentile(country, education, digital_access, gender_value, urban_value, next_bonus)
        growth = p_job - percentile
        with cols[3]:
            st.info(f"**Better Role**\n\n({next_occ})\n\n**+{growth:.1f} pts** 📈")

    # 4. Impact Breakdown
    st.divider()
    st.subheader("🧩 Factor Breakdown")
    
    impact_data = {
        'Factor': ['Base Level', 'Education Years', 'Occupation', 'Digital Access', 'Gender Gap', 'Location'],
        'Contribution': [
            COUNTRY_DATA[country]['base'],
            (education / 20) * 100 * COUNTRY_DATA[country]['education_weight'],
            occ_bonus,
            (digital_access / 100) * 15,
            gender_value * -10,
            urban_value * COUNTRY_DATA[country]['urban_bonus']
        ]
    }
    df_impact = pd.DataFrame(impact_data)
    
    fig_bar = px.bar(
        df_impact, 
        x='Contribution', 
        y='Factor', 
        orientation='h',
        title="Impact of Each Factor on Your Score",
        color='Contribution',
        color_continuous_scale='Blues'
    )
    fig_bar.update_layout(height=400)
    import plotly.express as px # Re-importing locally to ensure it's available for this block if needed
    st.plotly_chart(fig_bar, use_container_width=True)

else:
    # ========== COMPARISON MODE ==========
    
    st.subheader("� Compare Multiple Profiles Side-by-Side")
    
    num_scenarios = st.slider("Number of profiles to compare:", 2, 4, 2)
    
    cols = st.columns(num_scenarios)
    scenarios = []
    
    # Create profile inputs
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"### 👤 Profile {i+1}")
            with st.container(border=True):
                country = st.selectbox(f"Country", list(COUNTRY_DATA.keys()), key=f"country_{i}")
                occupation = st.selectbox(
                    f"Occupation", 
                    list(OCCUPATION_DATA.keys()), 
                    index=2 if i==0 else 5, # Different defaults
                    key=f"occ_{i}"
                )
                education = st.slider(f"Education", 0, 20, 10 if i==0 else 16, key=f"edu_{i}")
                digital = st.slider(f"Digital Access", 0, 100, 50, key=f"digital_{i}")
                gender = st.selectbox(f"Gender", ["Male", "Female"], key=f"gender_{i}")
                location = st.selectbox(f"Location", ["Rural", "Urban"], key=f"loc_{i}")
                
                gender_val = 1 if gender == "Female" else 0
                urban_val = 1 if location == "Urban" else 0
                occ_bonus = OCCUPATION_DATA[occupation]['bonus']
                
                percentile = calculate_percentile(country, education, digital, gender_val, urban_val, occ_bonus)
                
                scenarios.append({
                    'name': f"Profile {i+1}",
                    'country': country,
                    'education': education,
                    'occupation': occupation,
                    'digital': digital,
                    'gender': gender,
                    'location': location,
                    'percentile': percentile
                })
                
                st.metric("Resulting Percentile", f"{percentile:.1f}")
    
    # Comparison Visuals
    st.divider()
    
    fig_comp = go.Figure()
    
    for s in scenarios:
        fig_comp.add_trace(go.Bar(
            name=s['name'],
            x=[s['name']],
            y=[s['percentile']],
            text=[f"{s['percentile']:.1f}"],
            textposition='auto'
        ))
        
    fig_comp.update_layout(
        title="Compare Percentiles",
        yaxis_range=[0, 100],
        height=400
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    # DataFrame comparison
    st.caption("Detailed Comparison Matrix")
    df_comp = pd.DataFrame(scenarios).drop('name', axis=1)
    df_comp.index = [s['name'] for s in scenarios]
    st.dataframe(df_comp, use_container_width=True)

# Footer
st.divider()
st.caption("Income Inequality Simulator | South Asia Inequality Analysis Platform")
st.caption("💡 Educational tool - Not for individual income prediction")