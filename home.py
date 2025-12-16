import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from utils.loaders import load_inequality_data
from utils.utils import human_indicator

# Page config - MUST BE FIRST
st.set_page_config(
    page_title="South Asia Inequality Analysis",
    page_icon="🌏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clear any old cache
if st.button("🔄 Clear Cache (click if having issues)", key="clear_cache_btn"):
    st.cache_data.clear()
    st.rerun()

# Load custom CSS
try:
    with open('assets/dashboard.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Title
st.title("🌏 South Asia Income Inequality Analysis Platform")
st.markdown("### Interactive Data Visualization & Analysis Tool")

# Introduction
st.markdown("""
Welcome to the **South Asia Income Inequality Analysis Platform** - a comprehensive web application 
for exploring and analyzing inequality data across Bangladesh, India, Pakistan, Nepal, and Sri Lanka.

**Features:**
- 📊 Interactive visualizations (maps, charts, dashboards)
- 📈 Statistical analysis with significance testing
- 💡 Auto-generated insights using NLG
- 📥 Export functionality (PNG, CSV, PDF)
- 🔗 Shareable analysis URLs
- 📚 Comprehensive data sources & methodology
""")

# Load data to check availability
with st.spinner("Loading data..."):
    df = load_inequality_data()

if df.empty:
    st.error("""
    ❌ **No data found!**
    
    Please ensure the following files exist:
    - `data/processed/inequality_long.csv`
    - `data/processed/all_indicators_cleaned.csv`
    - `data/geo/sa_countries.geojson`
    
    See README.md for setup instructions.
    """)
    st.stop()

# Success message
st.success(f"✅ Data loaded successfully! ({len(df)} records)")

# Data overview
with st.expander("📊 Dataset Overview"):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        n_countries = df['country'].nunique()
        st.metric("Countries", n_countries)
    
    with col2:
        year_range = f"{int(df['year'].min())}-{int(df['year'].max())}"
        st.metric("Year Range", year_range)
    
    with col3:
        n_indicators = df['indicator'].nunique()
        st.metric("Indicators", n_indicators)
    
    with col4:
        n_records = len(df)
        st.metric("Data Points", f"{n_records:,}")

# Analysis Configuration
st.divider()
st.header("⚙️ Configure Your Analysis")

st.info("""
💡 **How to select multiple countries:**
1. Click INSIDE the "Countries" box below
2. A dropdown will appear with checkboxes
3. Click checkboxes to select/unselect countries
4. Selected countries will show as pills with X buttons
5. You can select 1-5 countries at once
""")

# Initialize session state
if 'analysis_config' not in st.session_state:
    st.session_state.analysis_config = None

# Get available options
all_countries = sorted(df['country'].unique())
all_indicators = sorted(df['indicator'].unique())
min_year = int(df['year'].min())
max_year = int(df['year'].max())

# Configuration form
with st.form("analysis_config_form"):
    st.subheader("Select Analysis Parameters")
    
    # CRITICAL: Multiselect for countries (allows multiple)
    st.markdown("### 1️⃣ Select Countries (Multiple Allowed)")
    selected_countries = st.multiselect(
        "Click inside box to see dropdown with checkboxes ↓",
        options=all_countries,
        default=all_countries[:2] if len(all_countries) >= 2 else all_countries,
        help="✅ You can select MULTIPLE countries. Click inside the box, then check the boxes that appear.",
        key="country_multiselect"
    )
    
    # Show what's selected
    if selected_countries:
        st.success(f"✅ **Selected {len(selected_countries)} countries:** {', '.join(selected_countries)}")
    else:
        st.warning("⚠️ Please select at least one country")
    
    st.divider()
    
    # Other selections
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 2️⃣ Select Indicator")
        selected_indicator = st.selectbox(
            "Indicator",
            options=all_indicators,
            help="Primary inequality indicator to analyze"
        )
    
    with col2:
        st.markdown("### 3️⃣ Select Color Scheme")
        color_scale = st.selectbox(
            "Color Scheme",
            options=['Reds', 'Blues', 'Greens', 'Viridis', 'Plasma', 'YlOrRd'],
            help="Color palette for visualizations"
        )
    
    st.markdown("### 4️⃣ Select Year Range")
    year_range = st.slider(
        "Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        help="Select time period for analysis"
    )
    
    st.divider()
    
    # Submit button
    submitted = st.form_submit_button("✅ Apply Configuration", use_container_width=True, type="primary")
    
    if submitted:
        # Validation
        errors = []
        
        if not selected_countries:
            errors.append("⚠️ Please select at least one country")
        
        if len(selected_countries) > 5:
            errors.append("⚠️ Maximum 5 countries allowed for optimal visualization")
        
        if year_range[0] >= year_range[1]:
            errors.append("⚠️ Start year must be before end year")
        
        if year_range[1] - year_range[0] > 50:
            errors.append("⚠️ Year range too large (maximum 50 years)")
        
        if errors:
            for error in errors:
                st.error(error)
        else:
            # Save configuration
            st.session_state.analysis_config = {
                'countries': selected_countries,
                'year_range': year_range,
                'indicator': selected_indicator,
                'color_scale': color_scale,
                'timestamp': pd.Timestamp.now()
            }
            
            st.success("✅ Configuration saved! You can now navigate to any analysis page.")
            
            # Display configuration
            st.balloons()
            
            st.info(f"""
            **✅ Active Configuration:**
            - **Countries:** {', '.join(selected_countries)} ({len(selected_countries)} selected)
            - **Years:** {year_range[0]}-{year_range[1]}
            - **Indicator:** {human_indicator(selected_indicator)}
            - **Color Scheme:** {color_scale}
            """)

# Quick Search Sidebar
st.sidebar.header("🔍 Quick Search")
st.sidebar.markdown("Fast-track your analysis")

with st.sidebar.form("quick_search"):
    quick_country = st.selectbox(
        "Country",
        options=[''] + sorted(df['country'].unique()),
        help="Select a country"
    )
    
    quick_indicator = st.selectbox(
        "Indicator",
        options=[''] + sorted(df['indicator'].unique()),
        help="Select an indicator"
    )
    
    quick_submit = st.form_submit_button("⚡ Quick Analyze")
    
    if quick_submit and quick_country and quick_indicator:
        st.session_state.analysis_config = {
            'countries': [quick_country],
            'year_range': (min_year, max_year),
            'indicator': quick_indicator,
            'color_scale': 'Reds',
            'timestamp': pd.Timestamp.now()
        }
        st.sidebar.success(f"✅ Analyzing {quick_country} - {human_indicator(quick_indicator)}")
        st.rerun()

# Current Configuration Display
if st.session_state.analysis_config is not None:
    st.sidebar.divider()
    st.sidebar.subheader("📋 Current Configuration")
    config = st.session_state.analysis_config
    st.sidebar.markdown(f"""
    **Countries:** {', '.join(config['countries'])}  
    **Count:** {len(config['countries'])} countries  
    **Years:** {config['year_range'][0]}-{config['year_range'][1]}  
    **Indicator:** {human_indicator(config['indicator'])}  
    **Color:** {config['color_scale']}
    """)

# Navigation Guide
st.divider()
st.header("🧭 Navigation Guide")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 📊 Core Visualizations
    - **Dashboard** - Multi-metric overview
    - **Map Analysis** - Animated choropleth
    - **Correlations** - Statistical relationships
    - **Sunburst** - Hierarchical breakdown
    """)

with col2:
    st.markdown("""
    ### 🔬 Analysis Tools
    - **Income Simulator** - Policy scenarios
    - **Data Quality** - Completeness check
    - **Auto-Insights** - NLG summaries
    - **Temporal Compare** - Then vs Now
    """)

with col3:
    st.markdown("""
    ### 📚 Resources
    - **Data Sources** - Citations & methodology
    - **Help & Glossary** - User guide
    """)

# Troubleshooting
with st.expander("❓ Troubleshooting - Can't select multiple countries?"):
    st.markdown("""
    ### If you can't select multiple countries, try:
    
    **1. Clear browser cache:**
    - Press `Ctrl + Shift + R` (Windows/Linux)
    - Press `Cmd + Shift + R` (Mac)
    
    **2. Click the Clear Cache button at the top of this page**
    
    **3. Restart Streamlit:**
    ```bash
    # Press Ctrl+C to stop
    # Then run again:
    streamlit run Home.py
    ```
    
    **4. Check Streamlit version:**
    ```bash
    streamlit --version
    # Should be 1.28.0 or higher
    ```
    
    **5. Upgrade Streamlit if needed:**
    ```bash
    pip install --upgrade streamlit
    ```
    
    ### How multiselect SHOULD work:
    1. Click inside the "Countries" box
    2. Dropdown appears with checkboxes
    3. Click multiple checkboxes
    4. Selected countries show as pills: Bangladesh X India X Pakistan X
    5. Click X on any pill to remove that country
    """)

# Share & Cite
st.divider()
st.header("📖 Share & Cite")

st.markdown("""
**Citation:**
```
Mehzabeen, S., Asma, Tabassum, & Samin. (2025). 
South Asia Income Inequality Analysis Platform. 
BRAC University, Department of Computer Science and Engineering.
```

**Data Sources:**
- World Bank Poverty and Inequality Database
- UNDP Human Development Reports (2024)

See **Data Sources** page for complete citations.
""")

# Footer
st.divider()
st.caption("South Asia Income Inequality Analysis Platform | BRAC University CSE Thesis Project 2025")
st.caption("Built with Streamlit • Data from World Bank & UNDP")