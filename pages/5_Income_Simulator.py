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
    layout="wide",
    initial_sidebar_state="expanded"
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
padding: 30px 20px;
background: linear-gradient(180deg, rgba(139, 92, 246, 0.15) 0%, rgba(139, 92, 246, 0.05) 100%);
border-radius: 20px;
border: 1px solid rgba(139, 92, 246, 0.3);
margin-bottom: 20px;
box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
height: auto;
min-height: 300px;
}
.metric-value-large {
font-size: 4rem;
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
    'Bangladesh': {'base': 25, 'education_weight': 0.32, 'urban_bonus': 8},
    'Bhutan': {'base': 23, 'education_weight': 0.30, 'urban_bonus': 7},
    'India': {'base': 22, 'education_weight': 0.35, 'urban_bonus': 12},
    'Maldives': {'base': 28, 'education_weight': 0.33, 'urban_bonus': 14},
    'Nepal': {'base': 22, 'education_weight': 0.32, 'urban_bonus': 7},
    'Pakistan': {'base': 20, 'education_weight': 0.30, 'urban_bonus': 10},
    'Sri Lanka': {'base': 25, 'education_weight': 0.32, 'urban_bonus': 11},
    'Afghanistan': {'base': 18, 'education_weight': 0.28, 'urban_bonus': 8}
}

@st.cache_data(ttl=3600)
def get_historical_data_efficiently():
    """Helper to load main data once for simulator use"""
    return load_inequality_data()

def calculate_percentile(country, edu, digital, gender, urban, occupation="Services", credit=False, age="Adult", api_data=None, un_data=None, poverty_data=None, live_context=None):
    """Calculate economic percentile with detailed live component breakdown"""
    
    # Backward compatibility for old calls signature if needed, or just unify
    if live_context is None:
        live_context = {}
        # Try to populate from legacy args if they exist
        if api_data is not None and not api_data.empty:
            gdp_val = api_data[api_data['indicator'].str.contains('GDP')]['value'].mean() if any(api_data['indicator'].str.contains('GDP')) else None
            if gdp_val: live_context['gdp'] = gdp_val
            
        if un_data is not None and not un_data.empty:
            live_context['gii'] = un_data['value'].iloc[0]
            
        if poverty_data is not None and not poverty_data.empty:
            live_context['poverty_rate'] = poverty_data['value'].iloc[0]
            
    data = COUNTRY_DATA.get(country, COUNTRY_DATA['India'])
    
    # 1. BASE VALUE (GDP-Driven)
    if 'gdp' in live_context:
        # Base value calibrated to GDP per capita
        # Log scale: $2000 -> Base 22, $400 -> Base 16
        base = 15 + (np.log10(max(live_context['gdp'], 100)/100) * 5)
    else:
        base = data['base']
    
    # Re-normalize base if migration is high (brain drain or influx)
    if 'net_migration' in live_context and live_context['net_migration'] < -500000:
        base -= 1 # Penalty for massive brain drain
        
    weight = data['education_weight']
    
    # 2. OCCUPATION & EMPLOYMENT QUALITY
    sector_scores = {"Agriculture": 0, "Industry": 8, "Services": 12, "Public Sector": 15, "Unemployed": -5}
    
    # Unemployment penalty dynamism
    if occupation == "Unemployed":
        # Base penalty
        occ_val = -5
        
        # 1. Adjust for Youth Unemployment if Age is Youth
        if age == "Youth (<25)" and 'unemp_youth' in live_context:
            u_youth = live_context['unemp_youth']
            # If youth unemployment is rampant (30%), the stigma/penalty is lower (structural)
            if u_youth > 20: occ_val += 2 
            
        # 2. Adjust for Education Level (Paradox of Educated Unemployment)
        # In South Asia, often higher education = higher unemployment rate
        if edu > 12:
            if 'unemp_advanced' in live_context:
                u_adv = live_context['unemp_advanced']
                if u_adv > 15: occ_val += 1 # "Waiting for white collar job" phenomenon
        elif edu >= 6:
            if 'unemp_intermediate' in live_context:
                # Same logic
                pass
                
        # 3. National Rate Context
        if 'unemployment_rate' in live_context:
            u_rate = live_context['unemployment_rate']
            occ_val += (u_rate / 10) # Higher national rate softens personal penalty
            
    else:
        # EMPLOYED SECTOR LOGIC
        if 'sector_shares' in live_context:
            shares = live_context['sector_shares']
            current_share = shares.get(occupation, 30)
            scarcity_factor = max(0.8, 1.5 - (current_share / 100))
            
            # Vulnerability Penalty
            vuln_penalty = 0
            if 'vulnerable_emp' in live_context:
                vuln_penalty = (live_context['vulnerable_emp'] / 100) * 3
            
            # Wage Worker Bonus
            wage_bonus = 0
            if 'wage_worker' in live_context:
                 wage_bonus = (live_context['wage_worker'] / 100) * 2
            
            # Agriculture Value Added (Ag Productivity)
            ag_bonus = 0
            if occupation == "Agriculture" and 'ag_value_added_gdp' in live_context:
                ag_val = live_context['ag_value_added_gdp']
                # If Ag value added is high (e.g. 20%) but employment is low -> High productivity
                # If Ag value added is low (15%) but employment high (40%) -> Low productivity
                # We already use share for scarcity. Let's use this for "Sector Health".
                if ag_val > 15: ag_bonus = 1
            
            base_score = sector_scores.get(occupation, 10)
            occ_val = (base_score * scarcity_factor) - vuln_penalty + wage_bonus + ag_bonus
            
            # Employers/Contributing Family adjustment
            # If "Self-employed" was an option (mapped to Services/Ind usually), we'd use 'employers_share'
            # Here we assume Services/Industry might include entrepreneurs.
            if occupation in ["Services", "Industry"] and 'employers_share' in live_context:
                emp_share = live_context['employers_share']
                # If high entrepreneurial density -> higher potential ceiling
                occ_val += (emp_share / 5)
                
        else:
            occ_val = sector_scores.get(occupation, 10)

    # 3. FINANCIAL ACCESS (Multi-dimensional Banking Infrastructure)
    if credit:
        credit_val = 6
        
        # A. FINANCIAL DEPTH - How developed is the credit market?
        if 'credit_depth' in live_context:
             # Domestic credit to private sector (% of GDP). Range: 10-100%+
             credit_val += min(3, live_context['credit_depth'] / 30) # Cap at +3 for strong markets
             
        if 'financial_sector_credit' in live_context:
            # Total domestic credit by financial sector (broader than private)
            # If this is significantly higher than private credit, implies govt borrowing
            # Use as a secondary depth indicator
            fin_cred = live_context['financial_sector_credit']
            if fin_cred > 50: credit_val += 0.5
        
        # B. BANKING PENETRATION - Actual access to banking services
        if 'borrowers_density' in live_context:
            # Borrowers from commercial banks per 1,000 adults
            # High value (200+) = widespread access, Low (20) = elite only
            borrowers = live_context['borrowers_density']
            if borrowers > 100:
                credit_val += 2  # Highly banked population
            elif borrowers > 50:
                credit_val += 1  # Moderate access
            # Low borrowers (<50) gets no bonus - having an account is rare/elite
                
        # C. CREDIT INFORMATION INFRASTRUCTURE
        if 'credit_info_depth' in live_context:
            # Depth of credit information index (0-8)
            # Strong credit bureaus enable better lending
            info_depth = live_context['credit_info_depth']
            credit_val += (info_depth / 8) * 1.5  # Up to +1.5 for perfect (8)
            
        if 'private_credit_bureau' in live_context:
            # Private credit bureau coverage (% of adults)
            # High coverage = mature credit ecosystem
            bureau_cov = live_context['private_credit_bureau']
            if bureau_cov > 30: credit_val += 1
            
        if 'public_credit_registry' in live_context:
            # Public credit registry coverage (% of adults)
            registry = live_context['public_credit_registry']
            if registry > 10: credit_val += 0.5
        
        # D. FINANCIAL SECTOR QUALITY (Policy & Regulation)
        if 'financial_sector_rating' in live_context:
            # CPIA financial sector rating (1=low to 6=high)
            # Strong institutions = better protection, lower interest rates
            rating = live_context['financial_sector_rating']
            credit_val += ((rating - 2) / 4) * 2  # Scale 2-6 to 0-2 bonus
        
        # E. PHYSICAL INFRASTRUCTURE (ATMs)
        if 'atm_density' in live_context:
            density = live_context['atm_density']  # per 100,000 adults
            # Scarcity bonus: Low ATM density makes physical access elite
            if density < 20:  # Very low
                credit_val += 2  # Having access is rare
            elif density < 50:
                credit_val += 1
            # High density (100+) = no bonus, access is common
            
        # F. ECONOMIC INTEGRATION (Remittances & Business Ecosystem)
        if 'remittances_gdp' in live_context and live_context['remittances_gdp'] > 5:
            # High remittances = banking is critical for receiving funds
            credit_val += min(2, live_context['remittances_gdp'] / 10)
            
        if 'business_density' in live_context:
            # High business density makes credit more useful for entrepreneurship
            bd = live_context['business_density']  # per 1000 people
            if bd > 5: credit_val += 1.5
            elif bd > 2: credit_val += 0.5
            
    else:
        credit_val = 0
    
    age_map = {"Youth (<25)": -4, "Adult (25-60)": 6, "Senior (>60)": 2}
    age_val = age_map.get(age, 4)
    
    # 4. EDUCATION (Quality & Scarcity Adjusted)
    # Base contribution from years
    edu_contrib = (edu/20)*40*weight
    
    # DYNAMIC ENROLLMENT & GPI LOGIC
    # Primary (Years 1-5)
    if 'primary_enrollment' in live_context:
        # If gross enrollment > 100%, basic education is universal -> lower scarcity bonus
        p_enrol = live_context['primary_enrollment']
        if p_enrol < 90: edu_contrib += 2 # Scarcity bonus
        
    if 'primary_gender_enrollment' in live_context:
        # If specific gender enrollment is low, educated person of that gender gets higher elite score
        pg_enrol = live_context['primary_gender_enrollment']
        if pg_enrol < 85: edu_contrib += 1.5
    
    # Secondary (Years 6-12)
    if edu >= 6:
        if 'secondary_enrollment' in live_context:
            s_enrol = live_context['secondary_enrollment']
            # Scarcity Multiplier: If only 40% enrolled, secondary ed is worth 1.2x more
            s_mult = max(1.0, 1.5 - (s_enrol/100))
            edu_contrib *= s_mult
            
        if 'secondary_gender_enrollment' in live_context:
            sg_enrol = live_context['secondary_gender_enrollment']
            # If my gender only has 30% enrollment, my degree is very rare
            if sg_enrol < 50: edu_contrib += 3
            
        if 'secondary_gpi' in live_context and gender == 1: # Female
            gpi = live_context['secondary_gpi']
            if gpi < 0.9: edu_contrib += 2 # Overcoming systemic barrier bonus
    
    # Tertiary (Years 13+)
    if edu > 12: 
        if 'tertiary_enrollment' in live_context:
             t_enrol = live_context['tertiary_enrollment']
             # Tertiary Scarcity: Low enrollment (15%) -> High Premium (2.5x). High (80%) -> Low Premium.
             t_mult = max(1.0, 3.0 - (t_enrol/40))
             edu_contrib *= t_mult
             
        if 'tertiary_gender_enrollment' in live_context:
            tg_enrol = live_context['tertiary_gender_enrollment']
            if tg_enrol < 20: edu_contrib += 5 # Status Symbol Bonus
            
        if 'tertiary_gpi' in live_context and gender == 1: # Female
            gpi = live_context['tertiary_gpi']
            if gpi < 0.8: edu_contrib += 3 # Breaking the glass ceiling bonus
             
    # Adjust for Primary Quality (Completion rate)
    if 'primary_completion' in live_context:
         comp = live_context['primary_completion']
         if comp < 80:
             edu_contrib += 2 # Scarcity bonus for finishing basic schooling
             
    # 5. DIGITAL SKILLS (Mobile + Internet)
    digital_contrib = (digital/100)*15
    if 'mobile_subs' in live_context:
        # If mobile density is high (>100), digital skills are assumed baseline?
        # Actually maybe if mobile subs are high, intermediate skills are needed to stand out.
        pass

    # 6. GENDER IMPACT
    if 'gii' in live_context:
        gender_penalty = live_context['gii'] * 18
    else:
        gender_penalty = 8
    gender_contrib = gender*(-gender_penalty)

    # 7. LOCATION (Urban Scarcity Driven)
    if 'urban_pct' in live_context:
        # Urban Pct 20% -> Bonus 16. Urban Pct 40% -> Bonus 12.
        u_pct = live_context['urban_pct']
        urban_bonus = 20 * (1 - (u_pct/100))
        
        # If rural, maybe check net migration? If high out-migration, rural is depressed.
    else:
        urban_bonus = data['urban_bonus']
        
    urban_contrib = urban*urban_bonus
    
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
    
    # 8. POVERTY BENCHMARKING
    poverty_bench = None
    if 'poverty_rate' in live_context:
        pov_rate = live_context['poverty_rate']
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

def render_percentile_distribution(p, title="Your Relative Standing"):
    """
    Renders a distribution plot with a High-Contrast Cyberpunk / Neon theme.
    """
    # 1. Simulate Income Distribution (Log-Normal)
    mean = 10.0
    sigma = 0.6
    
    # Generate distribution
    x = np.linspace(0, 30, 500)
    pdf = np.zeros_like(x)
    mask = x > 0
    pdf[mask] = (1 / (x[mask] * sigma * np.sqrt(2 * np.pi))) * np.exp(-((np.log(x[mask]) - mean/4) ** 2) / (2 * sigma ** 2))
    pdf = pdf / pdf.max()
    
    # 2. Determine User's Position
    sample = np.random.lognormal(mean=mean/4, sigma=sigma, size=100000)
    x_user = np.percentile(sample, p)
    y_user = np.interp(x_user, x, pdf)
    
    # 3. Build Plot
    fig = go.Figure()
    
    # A. The Population Curve (Cyberpunk Area)
    # Use a gradient-like fill by layering or just a solid neon fill with transparency
    fig.add_trace(go.Scatter(
        x=x, y=pdf,
        fill='tozeroy',
        mode='lines',
        line=dict(color='#00f3ff', width=3, shape='spline'), # Neon Cyan Line
        fillcolor='rgba(0, 243, 255, 0.15)', # Subtle Cyan Glow
        name='Population',
        hoverinfo='skip'
    ))
    
    # B. User's Position Line (Laser Beam)
    fig.add_trace(go.Scatter(
        x=[x_user, x_user],
        y=[0, y_user * 1.15],
        mode='lines',
        line=dict(color='#ff00ff', width=4, dash='solid'), # Neon Pink Beam
        name='YOU',
        hoverinfo='skip'
    ))
    
    # C. User Marker (Glowing Node)
    fig.add_trace(go.Scatter(
        x=[x_user],
        y=[y_user * 1.20], # Pushed higher to clear the marker
        mode='markers+text',
        marker=dict(
            color='#ff00ff', 
            size=10, 
            symbol='diamond', 
            line=dict(color='#ffffff', width=1)
        ),
        text=[f"<b>YOU</b><br><span style='font-size:12px; color:#ffffff;'>{p:.1f}th %</span>"],
        textposition="top right", # Offset to the side of the vertical line
        textfont=dict(color='#ff00ff', size=14, family="Courier New, monospace"),
        name='Your Standing'
    ))

    # Styling for "Cyberpunk Card" look
    # Update the marker trace text position logic
    if p > 80:
        fig.data[2].textposition = "top left"
    elif p < 20:
        fig.data[2].textposition = "top right"
    else:
        fig.data[2].textposition = "top right" # Default to right to avoid the vertical line
    
    fig.update_layout(
        title=dict(
            text=f"<b>{title.upper()}</b>", 
            font=dict(size=14, color='#00f3ff', family="Courier New, monospace"),
            x=0.03, y=0.92
        ),
        paper_bgcolor='rgba(9, 9, 11, 0.8)', # Dark card background
        plot_bgcolor='rgba(0,0,0,0)',
        height=300, # EXACT MATCH to updated left card min-height
        margin=dict(l=20, r=30, t=50, b=30), # Increased r margin for text
        xaxis=dict(
            title=dict(text="RELATIVE INCOME SCALE (POOR → RICH)", font=dict(color='#94a3b8', size=10)),
            showgrid=True, 
            gridcolor='rgba(0, 243, 255, 0.1)', # Faint generic grid
            gridwidth=1,
            showticklabels=False, 
            zeroline=False,
            range=[0, 20] # Zoomed in to make curve look fuller
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='rgba(0, 243, 255, 0.1)',
            showticklabels=False, 
            zeroline=False,
            range=[0, 1.5] # Increased headroom for the marker (was 1.3)
        ),
        showlegend=False
    )
    
    # Allow marker to render outside plot area if needed
    fig.update_traces(cliponaxis=False)

    
    return fig

def generate_insights(sp_p, breakdown_components, sp_country, sp_gender, sp_location, sp_occ, sp_credit, sp_edu, sp_digital, sp_poverty=None):
    """Generate plain-language, highly elaborated insights"""
    insights = []
    
    # Poverty Benchmark Insight
    if sp_poverty:
        color_type = "success" if sp_poverty['status'] == "Above Poverty Line" else ("warning" if sp_poverty['status'] == "Near Poverty Line" else "warning")
        insights.append({
            "type": color_type, "icon": "📉", "title": f"Poverty Benchmark: {sp_poverty['status']}",
            "text": f"Based on live World Bank data, your profile is currently positioned <b>{abs(sp_poverty['distance']):.1f}%</b> {'above' if sp_poverty['distance'] > 0 else 'below'} the national poverty line for {sp_country}. This benchmark is critical—falling below it often means struggling with basic necessities like food security and healthcare access, while being significantly above it indicates a level of economic resilience against minor shocks."
        })
    
    # Overall position explanation
    if sp_p >= 66.66:
        insights.append({
            "type": "success", "icon": "🎯", "title": "Strong Economic Standing",
            "text": f"Your profile places you in the <b>top third</b> of earners in {sp_country}. You are performing better than approximately <b>{sp_p:.0f} out of every 100 people</b>. This status likely affords you discretionary income, access to private healthcare/education, and the ability to invest in assets. Your main goal now should be <b>wealth preservation</b> and capitalized growth."
        })
    elif sp_p >= 33.33:
        insights.append({
            "type": "info", "icon": "📊", "title": "Middle Income Reality",
            "text": f"You sit squarely in the <b>middle income bracket</b> of {sp_country}, ahead of about {sp_p:.0f}% of the population. While you aren't in immediate poverty, you may still be vulnerable to economic downturns or health emergencies. The path to the upper tier typically requires <b>specialized skill acquisition</b> or <b>asset accumulation</b> (like property or business equity) to break the ceiling."
        })
    else:
        insights.append({
            "type": "warning", "icon": "⚠️", "title": "Economic Vulnerability Detected",
            "text": f"Your current profile suggests you are in the <b>lower income bracket</b>, facing significant economic headwinds. You are ahead of only {sp_p:.0f}% of the population. This position often correlates with high volatility—income may be irregular or dependent on daily labor. The immediate priority is <b>stabilization</b> through consistent employment or social safety nets."
        })
    
    # Education Insight - Deep Dive
    edu_contrib = breakdown_components['Education']
    if sp_edu < 10:
        potential_gain = (12-sp_edu) * 2
        insights.append({
            "type": "warning", "icon": "🎓", "title": "Critical Education Gap",
            "text": f"Education is the single strongest driver of mobility. With {sp_edu} years, you are likely locked out of the formal job market. Completing secondary education (12 years) is often the minimum requirement for entry-level stable jobs. Bridging this gap could theoretically boost your score by ~{potential_gain:.0f} points—representing a potential <b>doubling of lifetime earnings</b>."
        })
    elif sp_edu >= 16:
        insights.append({
            "type": "success", "icon": "🎓", "title": "Educational Elite Status",
            "text": f"Having {sp_edu} years of education puts you in an elite bracket in South Asia. This contributes a massive <b>{edu_contrib:.1f} points</b> to your score. In an economy where manual labor is abundant but intellectual capital is scarce, your degree is a powerful lever. Ensure you are leveraging this by working in <b>high-skill sectors</b> (Tech, Finance, specialized Services) rather than general administration."
        })
    
    # Gender Context
    if sp_gender == "Female":
        gender_impact = abs(breakdown_components['Gender Impact'])
        insights.append({
            "type": "warning", "icon": "⚖️", "title": "Systemic Gender Disparity",
            "text": f"Our model applies a structural penalty of <b>{gender_impact:.0f} points</b> to reflect the reality of being a woman in the {sp_country} economy. This isn't about your capability—it quantifies the <b>gender wage gap</b>, lower labor force participation rates, and unpaid care work burden. Overcoming this often requires <b>twice the effort</b> in education and networking to achieve parity with male counterparts in the same sector."
        })
    
    # Digital Skills - The Modern Multiplier
    if sp_digital < 40:
        potential = (75-sp_digital) * 0.15
        insights.append({
            "type": "warning", "icon": "💻", "title": "Digital Divide Risk",
            "text": f"Your digital proficiency ({sp_digital}%) is a bottleneck. In the modern economy, digital literacy is as important as reading. You are essentially cut off from the <b>remote work revolution</b> and high-efficiency tools. Improving this to just 75% could unlock <b>{potential:.1f} extra points</b> and access to a global job market that pays in stronger currencies."
        })
    elif sp_digital >= 75:
        insights.append({
            "type": "success", "icon": "💻", "title": "Digital Economy Native",
            "text": f"Your high digital score ({sp_digital}%) acts as a <b>force multiplier</b>. It suggests you can work efficiently, access global information, and potentially work remotely for foreign clients. This skill effectively <b>decouples</b> your earning potential from local physical infrastructure limitations."
        })
    
    # Location Dynamics
    if sp_location == "Rural":
        urban_bonus = COUNTRY_DATA[sp_country]['urban_bonus']
        insights.append({
            "type": "info", "icon": "🏘️", "title": "Rural Economy Constraints",
            "text": f"Living rurally creates a 'distance penalty' of about <b>{urban_bonus} points</b>. Rural markets in {sp_country} are typically smaller, less diverse, and have slower money velocity. While cost of living is lower, <b>earning ceilings are much lower</b> too. Unless you are a large landowner or have remote digital income, upward mobility is structurally harder here."
        })
    
    # Occupation Analysis
    occ_values = {"Agriculture": 0, "Industry": 8, "Services": 12, "Public Sector": 15, "Unemployed": -5}
    if sp_occ == "Agriculture":
        insights.append({
            "type": "warning", "icon": "🌾", "title": "Agricultural Subsistence Trap",
            "text": f"Agriculture involves high risk (climate, crop prices) and historically low returns in this region. It contributes <b>0 points</b> to your mobility score. Transitioning even to low-skill <b>Service sector jobs</b> (transport, retail) often immediately raises income stability and predictability."
        })
    elif sp_occ == "Public Sector":
        insights.append({
            "type": "success", "icon": "🏛️", "title": "The Public Sector Premium",
            "text": f"You hold the 'Golden Ticket' of South Asian employment. Public sector jobs provide unmatched <b>job security</b>, <b>pensions</b>, and <b>social status</b>, contributing a massive <b>15 points</b>. In volatility-prone economies, this stability is often valued higher than raw salary."
        })
    
    # Financial Access
    if not sp_credit:
        insights.append({
            "type": "warning", "icon": "🏦", "title": "Financial Exclusion Penalty",
            "text": f"You are operating in the <b>cash economy</b>. This is expensive and risky. Without a bank account (credit access), you cannot safely save large amounts, you have no verified financial history for loans, and you cannot easily receive digital payments. This costs you significant points because it forces you to rely on informal, often predatory, lending sources."
        })
    else:
        credit_contrib = breakdown_components['Credit Access']
        insights.append({
            "type": "success", "icon": "🏦", "title": "Financial Inclusion Advantage",
            "text": f"You are part of the formal financial system, adding <b>{credit_contrib:.1f} points</b>. This score reflects the comprehensive banking infrastructure available to you—ATM access, credit bureau coverage, and bank density. This access allows you to <b>leverage capital</b> (borrowing to invest) rather than just saving labor income, which is the key to moving to the upper class."
        })
    
    # ================= RECOMMENDATIONS =================
    recommendations = []
    
    if sp_edu < 12:
        recommendations.append({
            "priority": "HIGH", 
            "action": "Complete Secondary Education (Grade 12)", 
            "detail": f"<b>Why:</b> It is the minimum barrier to entry for the formal economy. <br><b>Impact:</b> Each year adds 2-3 points to your score. <br><b>Action:</b> Enroll in open schooling or adult education programs immediately. The ROI on this is higher than any investment."
        })
        
    if sp_digital < 60:
        recommendations.append({
            "priority": "HIGH", 
            "action": "Aggressively Build Digital Literacy",
            "detail": f"<b>Why:</b> Digital skills are the new literacy. <br><b>Impact:</b> Moving from beginner to intermediate can boost your potential by 15%+. <br><b>Action:</b> Master the basics: Typing, Office Suites (Docs/Excel), and safe Internet browsing. Use free resources like YouTube or local library courses."
        })
        
    if not sp_credit:
        recommendations.append({
            "priority": "MEDIUM", 
            "action": "Establish Formal Financial Identity",
            "detail": f"<b>Why:</b> You need a track record to access capital later. <br><b>Impact:</b> Unlocks 6+ points immediately. <br><b>Action:</b> 1. Open a zero-balance savings account. 2. Deposit small amounts regularly to create a history. 3. Avoid informal moneylenders."
        })
        
    if sp_occ in ["Agriculture", "Unemployed"]:
        recommendations.append({
            "priority": "HIGH", 
            "action": "Strategic Sector Switch",
            "detail": f"<b>Why:</b> Agriculture has a low income ceiling. <br><b>Impact:</b> Moving to 'Services' or 'Industry' can double your base score. <br><b>Action:</b> With your {sp_edu} years of education, look for roles in <b>Retail</b>, <b>Transport</b>, or <b>Basic Admin</b>. These sectors have faster wage growth."
        })
        
    if sp_location == "Rural" and sp_edu >= 12:
        recommendations.append({
            "priority": "MEDIUM", 
            "action": "Evaluate Urban Migration",
            "detail": f"<b>Why:</b> Your education is being underutilized in a rural setting. <br><b>Impact:</b> Immediate access to the 'Urban Premium' (approx {COUNTRY_DATA[sp_country]['urban_bonus']} points). <br><b>Action:</b> Look for jobs in the nearest Tier-2 city where living costs are manageable but opportunities are denser."
        })

    if sp_gender == "Female" and sp_occ in ["Agriculture", "Unemployed"]:
         recommendations.append({
            "priority": "HIGH", 
            "action": "Enter the Formal Workforce",
            "detail": f"<b>Why:</b> Women are disproportionately trapped in unpaid care work or subsistence farming. <br><b>Impact:</b> Earning an independent income is the strongest buffer against gender-based vulnerability. <br><b>Action:</b> Look for <b>wage-employment</b> specifically, rather than self-employment, to ensure income regularity."
        })

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
    
    **The Formula (Data-Driven Weighting):**
    ```
    Economic Position = Base (GDP) + Education (Enrollment + GPI) + Digital Skills + 
                       Gender (GII) + Urban/Rural (Urban %) + Occupation (Sector Shares) + 
                       Credit (Multi-dimensional Banking) + Age
    ```
    **Credit Access** is now scored across 6 dimensions:
    1. **Financial Depth** - Credit market size (domestic credit % GDP)
    2. **Banking Penetration** - Borrowers from commercial banks per 1,000 adults
    3. **Credit Infrastructure** - Bureau coverage & credit information depth index
    4. **Sector Quality** - CPIA financial sector rating (1-6)
    5. **Physical Access** - ATM density per 100,000 adults
    6. **Economic Integration** - Remittances & business ecosystem
    
    *When "Data-Driven Simulation" is enabled, every factor is weighted dynamically based on real country data from your curated indicators dataset.*
    """)

# ============= DATA MODE TOGGLE (PROMINENT) =============
st.markdown("### Data & Calibration Mode")
use_live_data = st.toggle("✅ Enable Data-Driven Simulation (Recommended)", value=True, help="When enabled, the simulator uses over 20+ real-world indicators (GDP, Employment, Education stats) from your curated dataset to weight the score. If disabled, it uses generic estimates.")

if use_live_data:
    st.markdown("""<div style="background: rgba(16, 185, 129, 0.1); padding: 10px; border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.2); margin-bottom: 20px;">
    <span style="color: #10b981; font-weight: 700;">✓ ACTIVE:</span> Using real economic data from curated dataset.
    </div>""", unsafe_allow_html=True)
else:
    st.markdown("""<div style="background: rgba(245, 158, 11, 0.1); padding: 10px; border-radius: 8px; border: 1px solid rgba(245, 158, 11, 0.2); margin-bottom: 20px;">
    <span style="color: #f59e0b; font-weight: 700;">⚠ INACTIVE:</span> Using static baseline estimates. Enable for higher accuracy.
    </div>""", unsafe_allow_html=True)



# ============= MODE SELECTION =============
st.markdown('<p class="section-header">Step 1: Choose Your Simulator Mode</p>', unsafe_allow_html=True)

mode_options = ["Individual Profile Simulator", "Profile Comparison Simulator", "Historical Snapshot Comparison"]
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
    
    st.markdown('<p class="section-header">Step 2: Build Your Profile</p>', unsafe_allow_html=True)

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
    
    context_data = {}
    
    if use_live_data:
        with st.spinner("Integrating Local Curated Data & Live Feeds..."):
            # Load Local Data
            local_df = get_historical_data_efficiently()
            
            def get_val(ind_name, fallback=None):
                """Get latest local value"""
                try:
                    row = local_df[(local_df['country'] == sp_country) & (local_df['indicator'] == ind_name)]
                    if row.empty: return fallback
                    return row.sort_values('year', ascending=False)['value'].iloc[0]
                except:
                    return fallback

            # 1. Base GDP
            # Prefer 2005 Constant for consistency in simulation base, or Current for perception?
            # Model uses log scale, so either works, but consistent is better.
            gdp_val = get_val('GDP per capita (constant 2005 US$)')
            if gdp_val: context_data['gdp'] = gdp_val
            
            # 2. Poverty
            pov_val = get_val('Poverty headcount ratio at $1.90 a day (2011 PPP) (% of population)')
            if pov_val: context_data['poverty_rate'] = pov_val

            # 3. Employment & Occupation (Gender Specific)
            # User specifically asked for gender breakdowns
            gender_suffix = ", female" if sp_gender == "Female" else ", male"
            gender_suffix_b = "female" if sp_gender == "Female" else "male" # For some indicator formats
            
            # Agriculture
            ag_share = get_val(f'Employment in agriculture{gender_suffix} (% of {gender_suffix_b} employment) (modeled ILO estimate)')
            if not ag_share: ag_share = get_val('Employment in agriculture (% of total employment) (modeled ILO estimate)', 40)
            
            # Industry
            ind_share = get_val(f'Employment in industry{gender_suffix} (% of {gender_suffix_b} employment) (modeled ILO estimate)')
            if not ind_share: ind_share = get_val('Employment in industry (% of total employment) (modeled ILO estimate)', 20)
            
            # Services
            srv_share = get_val(f'Employment in services{gender_suffix} (% of {gender_suffix_b} employment) (modeled ILO estimate)')
            if not srv_share: srv_share = get_val('Employment in services (% of total employment) (modeled ILO estimate)', 40)
            
            context_data['sector_shares'] = {
                "Agriculture": ag_share,
                "Industry": ind_share,
                "Services": srv_share,
                "Public Sector": 5 # Fixed low base for elite public jobs
            }
            
            # Quality & Vulnerability
            # Vulnerable employment
            vuln_ind = f'Vulnerable employment, {gender_suffix_b} (% of {gender_suffix_b} employment) (modeled ILO estimate)'
            vuln_val = get_val(vuln_ind)
            if not vuln_val: vuln_val = get_val('Vulnerable employment, total (% of total employment) (modeled ILO estimate)')
            if vuln_val: context_data['vulnerable_emp'] = vuln_val
            
            # Self-employed
            self_ind = f'Self-employed, {gender_suffix_b} (% of {gender_suffix_b} employment) (modeled ILO estimate)'
            self_val = get_val(self_ind)
            if not self_val: self_val = get_val('Self-employed, total (% of total employment) (modeled ILO estimate)')
            if self_val: context_data['self_emp'] = self_val

            # Wage Workers
            wage_ind = f'Wage and salaried workers, {gender_suffix_b} (% of {gender_suffix_b} employment) (modeled ILO estimate)'
            wage_val = get_val(wage_ind)
            if not wage_val: wage_val = get_val('Wage and salaried workers, total (% of total employment) (modeled ILO estimate)')
            if wage_val: context_data['wage_worker'] = wage_val
            
            # Unemployment Rate for Context
            unemp_ind = f'Unemployment, {gender_suffix_b} (% of {gender_suffix_b} labor force) (modeled ILO estimate)'
            unemp_val = get_val(unemp_ind)
            if not unemp_val: unemp_val = get_val('Unemployment, total (% of total labor force) (modeled ILO estimate)')
            if unemp_val: context_data['unemployment_rate'] = unemp_val

            # Unemployment with Education Breakdown (New Request)
            # Advanced Education
            unemp_adv_ind = f'Unemployment with advanced education, {gender_suffix_b} (% of {gender_suffix_b} labor force with advanced education)'
            unemp_adv_val = get_val(unemp_adv_ind)
            if not unemp_adv_val: unemp_adv_val = get_val('Unemployment with advanced education (% of total labor force with advanced education)')
            if unemp_adv_val: context_data['unemp_advanced'] = unemp_adv_val
            
            # Intermediate Education
            unemp_int_ind = f'Unemployment with intermediate education, {gender_suffix_b} (% of {gender_suffix_b} labor force with intermediate education)'
            unemp_int_val = get_val(unemp_int_ind)
            if not unemp_int_val: unemp_int_val = get_val('Unemployment with intermediate education (% of total labor force with intermediate education)')
            if unemp_int_val: context_data['unemp_intermediate'] = unemp_int_val

            # Youth Unemployment (New Request)
            unemp_youth_ind = f'Unemployment, youth {gender_suffix_b} (% of {gender_suffix_b} labor force ages 15-24) (modeled ILO estimate)'
            unemp_youth_val = get_val(unemp_youth_ind)
            if not unemp_youth_val: unemp_youth_val = get_val('Unemployment, youth total (% of total labor force ages 15-24) (modeled ILO estimate)')
            if unemp_youth_val: context_data['unemp_youth'] = unemp_youth_val

            # Business & Economic Context (New Request)
            aid_val = get_val('Net official development assistance and official aid received (current US$)')
            # Normalize aid by GDP if possible, or use raw for magnitude check (small economies rely more)
            if aid_val and 'gdp' in context_data: 
                # Very rough proxy as gdp is per capita constant 2005. 
                # Better to use GDP current if we fetched it. We did fetch it for remittances calculation.
                pass 
            
            bus_dens = get_val('New business density (new registrations per 1,000 people ages 15-64)')
            if bus_dens: context_data['business_density'] = bus_dens
            
            new_biz = get_val('New businesses registered (number)')
            if new_biz: context_data['total_new_businesses'] = new_biz
            
            rd_techs = get_val('Technicians in R&D (per million people)')
            if rd_techs: context_data['rd_technicians'] = rd_techs
            
            # Agriculture Value Added (New Request)
            ag_gdp = get_val('Agriculture, forestry, and fishing, value added (% of GDP)')
            if not ag_gdp: ag_gdp = get_val('Agriculture, value added (% of GDP)')
            if ag_gdp: context_data['ag_value_added_gdp'] = ag_gdp
            
            # Employment Class Status (Contributing Family / Employers)
            fam_work_ind = f'Contributing family workers, {gender_suffix_b} (% of {gender_suffix_b} employment) (modeled ILO estimate)'
            fam_work_val = get_val(fam_work_ind)
            if not fam_work_val: fam_work_val = get_val('Contributing family workers, total (% of total employment) (modeled ILO estimate)')
            if fam_work_val: context_data['contributing_family_workers'] = fam_work_val
            
            employer_ind = f'Employers, {gender_suffix_b} (% of {gender_suffix_b} employment) (modeled ILO estimate)'
            employer_val = get_val(employer_ind)
            if not employer_val: employer_val = get_val('Employers, total (% of total employment) (modeled ILO estimate)')
            if employer_val: context_data['employers_share'] = employer_val # High employers share = more entrepreneurship opportunities?
            
            # 4. Urban & Migration
            urb_val = get_val('Urban population (% of total)')
            if urb_val: context_data['urban_pct'] = urb_val
            
            mig_val = get_val('Net migration')
            if mig_val: context_data['net_migration'] = mig_val

            # 5. Financial & Remittances (Comprehensive Banking Infrastructure)
            # A. Credit Market Depth
            cred_val = get_val('Domestic credit to private sector (% of GDP)')
            if cred_val: context_data['credit_depth'] = cred_val
            
            # Also fetch broader financial sector credit
            fin_sec_cred = get_val('Domestic credit provided by financial sector (% of GDP)')
            if fin_sec_cred: context_data['financial_sector_credit'] = fin_sec_cred
            
            # B. Banking Penetration
            borrowers = get_val('Borrowers from commercial banks (per 1,000 adults)')
            if borrowers: context_data['borrowers_density'] = borrowers
            
            # C. Credit Information Infrastructure
            credit_info = get_val('Depth of credit information index (0=low to 8=high)')
            if credit_info: context_data['credit_info_depth'] = credit_info
            
            private_bureau = get_val('Private credit bureau coverage (% of adults)')
            if private_bureau: context_data['private_credit_bureau'] = private_bureau
            
            public_registry = get_val('Public credit registry coverage (% of adults)')
            if public_registry: context_data['public_credit_registry'] = public_registry
            
            # D. Financial Sector Quality
            fin_rating = get_val('CPIA financial sector rating (1=low to 6=high)')
            if fin_rating: context_data['financial_sector_rating'] = fin_rating
            
            # E. ATM Infrastructure
            atm_val = get_val('Automated teller machines (ATMs) (per 100,000 adults)')
            if atm_val: context_data['atm_density'] = atm_val
            
            # F. Remittances (Calculated as % of GDP if possible)
            remit_abs = get_val('Personal remittances, received (current US$)')
            gdp_curr = get_val('GDP (current US$)')
            if remit_abs and gdp_curr and gdp_curr > 0:
                context_data['remittances_gdp'] = (remit_abs / gdp_curr) * 100
            
            # 6. Education Advanced (Expanded as Requested)
            # Primary
            prim_gross = get_val('School enrollment, primary (% gross)')
            prim_gpi = get_val('School enrollment, primary and secondary (gross), gender parity index (GPI)')
            prim_f = get_val('School enrollment, primary, female (% gross)')
            prim_m = get_val('School enrollment, primary, male (% gross)') # Added
            
            if prim_gross: context_data['primary_enrollment'] = prim_gross
            if prim_gpi: context_data['primary_secondary_gpi'] = prim_gpi
            if prim_f and sp_gender == "Female": context_data['primary_gender_enrollment'] = prim_f
            elif prim_m and sp_gender == "Male": context_data['primary_gender_enrollment'] = prim_m
            
            # Secondary
            sec_gross = get_val('School enrollment, secondary (% gross)')
            sec_gpi = get_val('School enrollment, secondary (gross), gender parity index (GPI)')
            sec_f = get_val('School enrollment, secondary, female (% gross)')
            sec_m = get_val('School enrollment, secondary, male (% gross)')
            
            if sec_gross: context_data['secondary_enrollment'] = sec_gross
            if sec_gpi: context_data['secondary_gpi'] = sec_gpi
            if sec_f and sp_gender == "Female": context_data['secondary_gender_enrollment'] = sec_f
            elif sec_m and sp_gender == "Male": context_data['secondary_gender_enrollment'] = sec_m
            
            # Tertiary
            tert_gross = get_val('School enrollment, tertiary (% gross)')
            tert_gpi = get_val('School enrollment, tertiary (gross), gender parity index (GPI)')
            tert_f = get_val('School enrollment, tertiary, female (% gross)')
            tert_m = get_val('School enrollment, tertiary, male (% gross)')
            
            if tert_gross: context_data['tertiary_enrollment'] = tert_gross
            if tert_gpi: context_data['tertiary_gpi'] = tert_gpi
            if tert_f and sp_gender == "Female": context_data['tertiary_gender_enrollment'] = tert_f
            elif tert_m and sp_gender == "Male": context_data['tertiary_gender_enrollment'] = tert_m
            
            comp_val = get_val('Primary completion rate, total (% of relevant age group)')
            if comp_val: context_data['primary_completion'] = comp_val
            
            # Labor force advanced (Keep this as Outcome metric)
            lab_adv_val = get_val(f'Labor force with advanced education, {gender_suffix_b} (% of {gender_suffix_b} working-age population with advanced education)')
            if not lab_adv_val: lab_adv_val = get_val('Labor force with advanced education (% of total working-age population with advanced education)')
            if lab_adv_val: context_data['labor_force_adv'] = lab_adv_val
            
            # 7. Gender (GII usually from UN, assume API fallback or local proxies)
            # Local Proxy: We can use 'CPIA gender equality rating' if available, but GII is better.
            # We'll stick to the UN Loader for GII as it's specialized, or check local.
            # But let's check local 'CPIA gender equality rating (1=low to 6=high)'
            cpia_gen = get_val('CPIA gender equality rating (1=low to 6=high)')
            if cpia_gen:
                # Map 1-6 to GII-like penalty scale. Low score = High Penalty.
                # GII: 0 (Good) to 1 (Bad). CPIA: 1 (Bad) to 6 (Good).
                # Invert: (6 - CPIA) / 5 approx GII scale?
                context_data['gii'] = (6 - cpia_gen) / 6.0 # Crude proxy
            else:
                 un_live_data = un_loader.get_gender_inequality_index([sp_country])
                 if un_live_data is not None and not un_live_data.empty:
                    context_data['gii'] = un_live_data['value'].iloc[0]

            # 8. Digital
            mob_val = get_val('Mobile cellular subscriptions (per 100 people)')
            if mob_val: context_data['mobile_subs'] = mob_val
            
            int_val = get_val('Individuals using the Internet (% of population)')
            if int_val: context_data['internet_usage'] = int_val
            # (Calculation logic uses 'mobile_subs' context if available)

    sp_p, breakdown_components, sp_poverty = calculate_percentile(
        sp_country, sp_edu, sp_digital, g_val, u_val, sp_occ, sp_credit, sp_age, 
        live_context=context_data
    )

    # ============= STEP 2: RESULTS =============

    st.markdown('<p class="section-header">Step 3: Your Simulation Results</p>', unsafe_allow_html=True)

    group, color = get_tercile(sp_p)

    result_col1, result_col2 = st.columns([1, 1], gap="large")
    # Updated Layout: Side-by-Side Cards, then Chart below
    stats_c1, stats_c2 = st.columns(2, gap="medium")

    with stats_c1:
        # Create flat HTML string to avoid markdown indentation issues
        res_html = f"""<div class="result-container" style="min-height: 250px; display: flex; flex-direction: column; justify-content: center;">
<p class="metric-label">Your Economic Percentile</p>
<div class="metric-value-large">{sp_p:.1f}<span style="font-size: 2rem;">th</span></div>
<div class="metric-group" style="color: {color};">{group.upper()}</div>
<p style="color: #94a3b8; margin-top: 15px; font-size: 0.9rem; line-height: 1.5;">
Rank higher than <b>{sp_p:.1f}%</b> of {sp_country}. Out of 100 people, you surpass <b>{int(sp_p)}</b> of them.
</p>
</div>"""
        st.markdown(res_html, unsafe_allow_html=True)

    with stats_c2:
        if sp_poverty:
            pov_html = f"""
<div class="result-container" style="min-height: 250px; background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); display: flex; flex-direction: column; justify-content: center;">
<p style="color: #fca5a5; font-size: 1rem; margin: 0; text-transform: uppercase; font-weight: 700; letter-spacing: 1.5px;">Live Poverty Benchmark</p>
<h2 style="color: #ffffff; font-size: 2.5rem; margin: 15px 0; font-weight: 800;">{sp_poverty['status']}</h2>
<p style="color: #e2e8f0; font-size: 1.1rem;">Positioned <b>{abs(sp_poverty['distance']):.1f}%</b> {'above' if sp_poverty['distance'] > 0 else 'below'} the line.</p>
</div>"""
            st.markdown(pov_html, unsafe_allow_html=True)
        else:
             st.info("Poverty data not available for this selection.")

    # Chart takes full width below
    st.markdown("<br>", unsafe_allow_html=True)
    st.plotly_chart(render_percentile_distribution(sp_p, "Your Economic Standing"), use_container_width=True)

    # ============= STEP 3: INSIGHTS =============

    st.markdown('<p class="section-header">Step 4: What This Means for You - Plain Language Insights</p>', unsafe_allow_html=True)

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
        st.markdown('<p class="section-header" style="margin-top: 50px;">Personalized Recommendations</p>', unsafe_allow_html=True)
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





# ============= COMPARISON MODE =============
elif st.session_state.simulator_mode == "comparison":
    st.markdown('<p class="section-header">Step 2: Build Both Profiles</p>', unsafe_allow_html=True)
    
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
    st.markdown('<p class="section-header">Step 3: Comparison Results</p>', unsafe_allow_html=True)
    
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
    st.markdown("### Visual Comparison Dashboard")
    
    viz_comp_col1, viz_comp_col2, viz_comp_col3 = st.columns([1, 2, 1], gap="large")
    
    with viz_comp_col1:
        # Profile A Gauge
        fig_gauge_a = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = profile_a_p,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Profile A Percentile", 'font': {'size': 16, 'color': '#8b98a5'}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#8b98a5"},
                'bar': {'color': "#3b82f6"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "#2f3336",
                'steps': [
                    {'range': [0, 33], 'color': 'rgba(239, 68, 68, 0.1)'},
                    {'range': [33, 66], 'color': 'rgba(245, 158, 11, 0.1)'},
                    {'range': [66, 100], 'color': 'rgba(16, 185, 129, 0.1)'}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': profile_a_p
                }
            }
        ))
        fig_gauge_a.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': "#60a5fa", 'family': "Inter"},
            height=250,
            margin=dict(t=50, b=20, l=30, r=30)
        )
        st.plotly_chart(fig_gauge_a, use_container_width=True)
    
    with viz_comp_col2:
        # Difference indicator
        diff = profile_b_p - profile_a_p
        diff_color = "#10b981" if diff > 0 else "#ef4444" if diff < 0 else "#8b98a5"
        diff_text = "Better" if diff > 0 else "Worse" if diff < 0 else "Same"
        
        # Calculate main driver
        # We'll compare the component differences
        comp_diffs = {}
        for k in profile_a_components.keys():
            comp_diffs[k] = profile_b_components.get(k, 0) - profile_a_components.get(k, 0)
        
        # Identify the driver with the largest absolute impact
        if abs(diff) > 0.1:
            main_driver_key = max(comp_diffs, key=lambda k: abs(comp_diffs[k]))
            impact_val = comp_diffs[main_driver_key]
            
            if impact_val > 0:
                driver_explanation = f"Profile B's {main_driver_key} is a major positive factor."
            elif impact_val < 0:
                driver_explanation = f"Profile A's {main_driver_key} gives it an advantage."
            else:
                driver_explanation = "The profiles are economically differentiated across multiple factors."
        else:
            driver_explanation = "Both profiles have nearly identical economic standings."

        st.markdown(f"""
        <div style="text-align: center; padding: 40px; background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(16, 185, 129, 0.1)); border-radius: 16px; border: 2px solid {diff_color};">
            <div style="font-size: 3rem; font-weight: 900; color: {diff_color}; margin: 15px 0;">
                {'+' if diff > 0 else ''}{diff:.1f}
            </div>
            <div style="color: #8b98a5; font-size: 1rem; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px;">Percentile Points</div>
            <div style="color: #e2e8f0; font-size: 1.3rem; font-weight: 600;">Profile B is {diff_text}</div>
            <div style="color: #8b98a5; font-size: 0.95rem; margin-top: 20px; font-style: italic;">
                {driver_explanation}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with viz_comp_col3:
        # Profile B Gauge
        fig_gauge_b = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = profile_b_p,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Profile B Percentile", 'font': {'size': 16, 'color': '#8b98a5'}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#8b98a5"},
                'bar': {'color': "#10b981"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "#2f3336",
                'steps': [
                    {'range': [0, 33], 'color': 'rgba(239, 68, 68, 0.1)'},
                    {'range': [33, 66], 'color': 'rgba(245, 158, 11, 0.1)'},
                    {'range': [66, 100], 'color': 'rgba(16, 185, 129, 0.1)'}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': profile_b_p
                }
            }
        ))
        fig_gauge_b.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': "#34d399", 'family': "Inter"},
            height=250,
            margin=dict(t=50, b=20, l=30, r=30)
        )
        st.plotly_chart(fig_gauge_b, use_container_width=True)

    # Side-by-Side Profile Storytelling Comparison
    st.markdown("#### The Economic Journey: A Tale of Two Profiles")
    
    # Narrative Logic
    better_profile = "Profile B" if diff > 0 else "Profile A" if diff < 0 else "both profiles"
    gap_desc = f"a significant lead of {abs(diff):.1f} percentile points" if abs(diff) > 10 else f"a slight edge of {abs(diff):.1f} percentile points" if abs(diff) > 0 else "identical standing"
    
    story_col1, story_col2 = st.columns(2, gap="large")
    
    with story_col1:
        # Profile A Story
        a_narrative = f"Living in <b>{profile_a_country}</b>, Profile A navigates an economy where "
        if profile_a_edu > 12:
            a_narrative += "their advanced education serves as a powerful shield against economic volatility. "
        elif profile_a_edu > 6:
            a_narrative += "their secondary schooling provides a solid foundation for stability. "
        else:
            a_narrative += "limited formal schooling presents a steep climb for upward mobility. "
            
        if profile_a_digital > 70:
            a_narrative += "Armed with elite digital skills, they are well-positioned for the modern labor market. "
        elif profile_a_digital > 30:
            a_narrative += "They possess the basic digital tools needed to participate in the growing tech economy. "
            
        if profile_a_location == "Urban":
            a_narrative += f"The urban environment of {profile_a_country} offers them a 'density' of opportunities, especially in the <b>{profile_a_occ}</b> sector. "
        else:
            a_narrative += f"As a rural resident, they face different constraints, but their role in <b>{profile_a_occ}</b> defines their daily economic reality. "
            
        if profile_a_credit:
            a_narrative += "Access to formal credit acts as a critical multiplier for their potential investments."
            
        st.markdown(f"""
        <div class="insight-panel" style="border-left-color: #3b82f6; min-height: 280px;">
            <div class="insight-title" style="color: #60a5fa;">Profile A's Context</div>
            <p style="color: #e2e8f0; font-size: 1rem; line-height: 1.7; padding: 5px;">{a_narrative}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with story_col2:
        # Profile B Story
        b_narrative = f"Meanwhile, in <b>{profile_b_country}</b>, Profile B's journey follows a different path. "
        if profile_b_edu > profile_a_edu:
            b_narrative += f"With <b>{profile_b_edu - profile_a_edu} more years of education</b> than Profile A, they've unlocked access to higher-tiered social circles. "
        elif profile_b_edu < profile_a_edu:
            b_narrative += f"Having {profile_a_edu - profile_b_edu} fewer years of schooling than Profile A, they must rely more on practical experience and networking. "
            
        if profile_b_digital > profile_a_digital:
            b_narrative += f"Their superior digital proficiency ({profile_b_digital}% vs {profile_a_digital}%) acts as a modern-day 'literacy' that gives them an edge. "
            
        if profile_b_location != profile_a_location:
            b_narrative += f"The shift from {profile_a_location} to <b>{profile_b_location}</b> living drastically alters their access to infrastructure and high-paying jobs. "
            
        if profile_b_credit and not profile_a_credit:
            b_narrative += "Unlike Profile A, their access to formal banking provides a safety net and a bridge to future growth. "
        elif not profile_b_credit and profile_a_credit:
            b_narrative += "Lacking the formal credit access that Profile A enjoys, they face more barriers to scaling their economic activities. "

        st.markdown(f"""
        <div class="insight-panel-success" style="border-left-color: #10b981; min-height: 280px;">
            <div class="insight-title" style="color: #34d399;">Profile B's Context</div>
            <p style="color: #e2e8f0; font-size: 1rem; line-height: 1.7; padding: 5px;">{b_narrative}</p>
        </div>
        """, unsafe_allow_html=True)

    # The "Why" - Final Narrative Synthesis
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, rgba(59, 130, 246, 0.1), rgba(16, 185, 129, 0.1)); padding: 25px; border-radius: 16px; border: 1px solid rgba(139, 92, 246, 0.2); margin-top: 20px;">
        <h5 style="color: #ffffff; margin-top: 0;">Why is {better_profile} ahead?</h5>
        <p style="color: #e2e8f0; font-size: 1.05rem; line-height: 1.6;">
            The data reveals that {better_profile} holds {gap_desc}. This isn't just about single attributes, but how they interact with the national environment. 
            For instance, <b>{max(comp_diffs, key=lambda k: abs(comp_diffs[k]))}</b> emerges as the pivotal differentiator in this comparison. 
            In the context of {profile_a_country if diff < 0 else profile_b_country}, this attribute provides disproportionate leverage, shifting {better_profile} into a more exclusive economic tier.
        </p>
    </div>
    """, unsafe_allow_html=True)
    

    
    # Multi-dimensional radar chart comparison
    st.markdown('<p class="section-header" style="margin-top: 50px;">Multi-Dimensional Score Comparison</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94a3b8; font-size: 1.1rem; margin-bottom: 25px;">Relative strengths and trade-offs of both profiles across five key dimensions.</p>', unsafe_allow_html=True)
    
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
    st.markdown('<p class="section-header">Step 2: Configure Historical Comparison</p>', unsafe_allow_html=True)
    
    st.markdown("""<div class="historical-card">
<h3 style="text-align: center; color: #f59e0b; margin-bottom: 10px;">Historical Evolution Tool</h3>
<p style="text-align: center; color: #8b98a5; margin-bottom: 20px;">Observe how the <b>same profile attributes</b> would result in different social standings across two distinct time periods.</p>
</div>""", unsafe_allow_html=True)

    # SHARED ATTRIBUTES FOR BOTH YEARS
    st.markdown("#### Fixed Profile Attributes")
    col_attr1, col_attr2 = st.columns([2, 1], gap="large")
    
    with col_attr1:
        st.markdown('<div class="input-group-label">Country Selection</div>', unsafe_allow_html=True)
        h_country = st.selectbox("Compare data for:", list(COUNTRY_DATA.keys()), key="h_country", label_visibility="collapsed")
        
        st.markdown('<div class="input-group-label" style="margin-top: 25px;">Profile Attributes</div>', unsafe_allow_html=True)
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
    st.markdown('<p class="section-header">Step 3: Social Standing Evolution</p>', unsafe_allow_html=True)
    
    res_col1, res_col2 = st.columns(2, gap="large")
    
    with res_col1:
        st.markdown(f'<div style="text-align: center; color: #8b98a5; margin-bottom: 10px;">POSITION IN {year_1}</div>', unsafe_allow_html=True)
        st.plotly_chart(render_percentile_distribution(p1, f"Standing in {year_1}"), use_container_width=True)
        
    with res_col2:
        st.markdown(f'<div style="text-align: center; color: #8b98a5; margin-bottom: 10px;">POSITION IN {year_2}</div>', unsafe_allow_html=True)
        st.plotly_chart(render_percentile_distribution(p2, f"Standing in {year_2}"), use_container_width=True)

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
    st.markdown('<p class="section-header" style="margin-top: 50px;">Deep Era Analysis</p>', unsafe_allow_html=True)
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

# -----------------
# Navigation
# -----------------
from utils.navigation_ui import bottom_nav_layout
bottom_nav_layout(__file__)
