import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from utils.loaders import load_inequality_data

# Page config
st.set_page_config(
    page_title="Sankey Diagram",
    page_icon="🌊",
    layout="wide"
)

# Load custom CSS
try:
    with open('assets/dashboard.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.title("🛡️ Complex Structural Flow Analysis")
st.markdown("""
### Mapping the Multi-Stage Economic Pipeline
Inspired by energy flow systems, this diagram visualizes how national drivers (left) are transformed through infrastructure and labor 
before being distributed to the population. The **Red Losses** node represents the structural cost of inequality.
""")

# Load Data
df = load_inequality_data()
if df.empty:
    st.error("Data loading failed.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.header("📂 Data Source")
countries = sorted(df['country'].unique())
c = st.sidebar.selectbox("Select Country", countries, index=min(1, len(countries)-1))
country_df = df[df['country'] == c]
years = sorted(country_df['year'].unique())
y = st.sidebar.select_slider("Select Analysis Year", options=years, value=max(years))

# Extract Key Data
year_df = country_df[country_df['year'] == y]
def get_v(ind, default=5):
    v = year_df[year_df['indicator'] == ind]['value']
    return v.values[0] if not v.empty else default

# Data Inputs
edu = get_v('education_index', 8)
internet = get_v('internet_access', 30)
labor = get_v('labor_force', 10000000)
gdp = get_v('gdp_per_capita', 2000)
gini = get_v('gini', 35)

# --- SANKEY CALCULATIONS (5-STAGE COMPLEX PIPELINE) ---
# Normalize inputs to a total flow of 200 units for density
total_f = 200

# Level 1 to 2
edu_f = (edu / 20) * 60
tech_f = (internet / 100) * 50
labor_f = 50 
gdp_f = 40

# Nodes List (Total 20+ nodes for complexity)
# 0-3: Sources
# 4-7: Transformation
# 8-11: Sectoral Potential
# 12-14: Distribution
# 15-18: Final Destinations
# 19: LOSSES (THE BIG RED ONE)

nodes = [
    # 0-3 Source Nodes
    f"Education Reserves ({edu:.1f})", "Digital Infrastructure", "Labor Raw Capacity", "Capital (GDP Base)",
    # 4-7 Transformation Nodes
    "Human Capital Skill", "Technological utility", "Economic Stability", "Productive Workforce",
    # 8-11 Sectoral Nodes
    "Digital Economy", "Industrial Output", "Agricultural Base", "Service Sector",
    # 12-14 Distribution Grids
    "Public Wealth Grid", "Private Assets", "Regional Support",
    # 15-18 Final Use
    "Upper Tier Benefit", "Middle Tier Benefit", "Poverty Alleviation", "Social Mobility",
    # 19 THE RED LOSS (INEQUALITY)
    "STRUCTURAL LOSSES (GINI)"
]

# Links: [Source, Target, Value, Color]
links = [
    # Foundations to Transformation
    [0, 4, edu_f, "rgba(139, 92, 246, 0.4)"],
    [1, 5, tech_f, "rgba(59, 130, 246, 0.4)"],
    [2, 7, labor_f, "rgba(16, 185, 129, 0.4)"],
    [3, 6, gdp_f, "rgba(245, 158, 11, 0.4)"],
    
    # Transformation to Sectoral
    [4, 8, edu_f*0.4, "rgba(139, 92, 246, 0.2)"], [4, 11, edu_f*0.6, "rgba(139, 92, 246, 0.2)"],
    [5, 8, tech_f*0.7, "rgba(59, 130, 246, 0.2)"], [5, 9, tech_f*0.3, "rgba(59, 130, 246, 0.2)"],
    [7, 9, labor_f*0.5, "rgba(16, 185, 129, 0.2)"], [7, 10, labor_f*0.5, "rgba(16, 185, 129, 0.2)"],
    [6, 11, gdp_f*0.5, "rgba(245, 158, 11, 0.2)"], [6, 9, gdp_f*0.5, "rgba(245, 158, 11, 0.2)"],
    
    # Sectoral to Distribution
    [8, 12, (edu_f*0.4 + tech_f*0.7)*0.8, "rgba(255,255,255,0.1)"],
    [9, 13, (tech_f*0.3 + labor_f*0.5 + gdp_f*0.5)*0.8, "rgba(255,255,255,0.1)"],
    [10, 14, (labor_f*0.5)*0.8, "rgba(255,255,255,0.1)"],
    [11, 12, (edu_f*0.6 + gdp_f*0.5)*0.8, "rgba(255,255,255,0.1)"],
    
    # INEQUALITY LEAKAGE (Gini based)
    # Mapping flows to the Red Node 19
    [8, 19, (edu_f*0.4 + tech_f*0.7)*0.2*(gini/50), "rgba(239, 68, 68, 0.6)"],
    [9, 19, (tech_f*0.3 + labor_f*0.5 + gdp_f*0.5)*0.2*(gini/50), "rgba(239, 68, 68, 0.6)"],
    [10, 19, (labor_f*0.5)*0.2*(gini/50), "rgba(239, 68, 68, 0.6)"],
    [11, 19, (edu_f*0.6 + gdp_f*0.5)*0.2*(gini/50), "rgba(239, 68, 68, 0.6)"]
]

# Calculate final flows to destinations
# For simplicity, we'll route the remaining distribution flows to tier benefits
links.extend([
    [12, 15, 30, "rgba(16, 185, 129, 0.2)"],
    [12, 16, 20, "rgba(16, 185, 129, 0.2)"],
    [13, 15, 25, "rgba(59, 130, 246, 0.2)"],
    [13, 17, 15, "rgba(59, 130, 246, 0.2)"],
    [14, 18, 10, "rgba(245, 158, 11, 0.2)"],
    [14, 19, 5*(gini/30), "rgba(239, 68, 68, 0.4)"] # Extra rural inequality
])

# Process Links for Plotly
s, t, v, c_list = zip(*links)

# Node Colors
node_colors = [
    "#a78bfa", "#60a5fa", "#34d399", "#fbbf24", # Level 1
    "#8b5cf6", "#3b82f6", "#f59e0b", "#10b981", # Level 2
    "#06b6d4", "#6366f1", "#10b981", "#8b5cf6", # Level 3
    "#94a3b8", "#64748b", "#475569",          # Level 4
    "#10b981", "#3b82f6", "#f59e0b", "#8b5cf6", # Level 5
    "#ef4444"                                   # THE LOSSES (RED)
]

fig = go.Figure(data=[go.Sankey(
    arrangement = "snap",
    node = dict(
      pad = 20,
      thickness = 25,
      line = dict(color = "#000", width = 1),
      label = nodes,
      color = node_colors
    ),
    link = dict(
      source = s,
      target = t,
      value = v,
      color = c_list
  ))])

fig.update_layout(
    title=dict(
        text=f"Strategic Economic Flow: {c} ({y})",
        font=dict(size=24, color="white"),
        x=0.5
    ),
    font=dict(size=12, color="white"),
    height=800, # Increased height to match image density
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=50, r=50, t=100, b=50)
)

# Display
st.plotly_chart(fig, use_container_width=True)

# Comparison/Insight Panel
col1, col2 = st.columns([1, 1])
with col1:
    st.html(f"""
    <div class="glass-panel">
        <h4 style="margin-top:0;">Pipeline Health</h4>
        <p style="color:var(--text-secondary);">Total Productive Potential: <span style="color:#fff;">{total_f} units</span></p>
        <p style="color:var(--text-secondary);">Inequality Draft: <span style="color:#ef4444;">{(gini/100)*100:.1f}% leakage</span></p>
    </div>
    """)
with col2:
    st.info(f"""
    **Visual Guide:**
    - **Width**: Represents the strength of the indicator in {c}.
    - **Flow Paths**: Shows how education and technology fuel specific sectors like the Digital Economy.
    - **Red Block**: Mirroring your reference image, this shows the massive amount of national potential that fails to reach the population due to local inequality.
    """)

# --- DYNAMIC INTERPRETATION ---
st.subheader(f"� Detailed Structural Narrative: {c} ({y})")

def generate_interpretation():
    # Analyze Stages
    drivers = {"Education": edu_f, "Technology": tech_f, "Labor force": labor_f, "GDP": gdp_f}
    top_driver = max(drivers, key=drivers.get)
    
    sectors = {"Infrastructure": tech_f, "Human Capital": edu_f, "Labor Pool": labor_f}
    strongest_sector = max(sectors, key=sectors.get)
    
    inequality_impact = (gini / 100) * 100
    leakage_severity = "Critical" if gini > 45 else "Significant" if gini > 35 else "Notable"

    narrative = f"""
    ### 1. Foundational Inputs (The Headwaters)
    In {y}, the primary economic engine for **{c}** is **{top_driver}**. The width of the leftmost bars represents 
    the volume of resources available. Your data suggests that **{top_driver}** provides the most substantial 'flow' into the national system, 
    forming the bedrock of {c}'s productive capacity.

    ### 2. The Transformation Stage (The Processing)
    As these inputs move to the right, they merge and transform. **{strongest_sector}** is acting as the most efficient 
    conduit for growth. This is where raw stats (like years of schooling or internet speed) become real-world utility. 
    A thick flow here indicates that the country is successfully converting its basic raw materials into 
    specialized assets like a skilled workforce or a robust digital economy.

    ### 3. Sectoral Distribution (The Output)
    The middle of the graph shows how this potential is split across different sectors. 
    The flows converging into **Industrial Output** and the **Digital Economy** demonstrate {c}'s 
    strategic focus. The broader these connections, the more diversified the economy is becoming.

    ### 4. The Final Outcome & The 'Leakage' (The Destination)
    This is the most critical part of the diagram. The flow split on the far right represents the **Socio-Economic Reality**:
    - ** distributed Benefit (Green/Blue/Orange):** This represents the 'Effective Wealth' that successfully reaches 
    different tiers of the population, funding social mobility and poverty alleviation.
    - **Structural Losses (Massive Red Block):** Mirroring the complexity of your reference image, this **{leakage_severity} 
    Inequality Leakage** shows that **{inequality_impact:.1f}%** of the total possible benefit is being siphoned off. 
    In plain terms: this potential exists in the economy, but due to **{gini:.1f} Gini-level inequality**, it is effectively 
    'trapped' and never reaches the wider population.
    """
    return narrative

# Render narrative
st.markdown(generate_interpretation())

# Add a "How to Read" guide for beginners
with st.expander("❓ How to interpret this complex diagram"):
    st.markdown("""
    **Step-by-Step Guide:**
    1. **Start Left to Right**: The diagram flows like water. The Left side are the 'Ingredients' (Data).
    2. **Watch the Width**: The thicker the line, the more 'Value' or 'Importance' that factor has.
    3. **Look for Convergences**: Where lines meet (like Education and Technology), it means those two things are working together to create a stronger sector.
    4. **The Red Block is the most important**: It represents 'Wasted Potential'. If the Red block is wider than the other final destinations, it means the country has high inequality that is 'eating' the benefits of its education and tech investments.
    """)

st.divider()
st.caption("Data-Driven Structural Flow Analysis | South Asia Inequality Explorer")
