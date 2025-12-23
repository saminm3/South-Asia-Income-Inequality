import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from utils.loaders import load_inequality_data
from utils.utils import human_indicator, get_color_scale

# Page config - MUST BE FIRST
st.set_page_config(
    page_title="South Asia Inequality Analysis",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
try:
    with open('assets/dashboard.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Load data
df = load_inequality_data()
if df.empty:
    st.error("❌ Data not found. Please ensure processed dataset exists.")
    st.stop()

# Title
st.title("South Asia Income Inequality Analysis Platform")
st.markdown("### Interactive Data Visualization & Analysis Tool")

# Introduction
st.markdown("""
Welcome to the **South Asia Income Inequality Analysis Platform** - a comprehensive web application 
for exploring and analyzing inequality data across South Asia.

**Features:**
- Interactive visualizations (maps, charts, dashboards)
- Statistical analysis with significance indicators
- Auto-generated insights and temporal comparisons
- Data quality monitoring and source transparency

✅ This is an **open-access platform**: Every page works immediately with sensible defaults.
""")

st.divider()

# Initialize session state with PUBLIC DEFAULTS
if 'analysis_config' not in st.session_state:
    st.session_state.analysis_config = None

# Get available options
all_countries = sorted(df['country'].unique())
all_indicators = sorted(df['indicator'].unique())
min_year = int(df['year'].min())
max_year = int(df['year'].max())

# ✅ DEFAULT PUBLIC ANALYSIS (Open-access experience)
# Create sensible defaults so every page works immediately
if st.session_state.analysis_config is None:
    default_indicator = 'GINI' if 'GINI' in all_indicators else (all_indicators[0] if all_indicators else None)
    default_year_start = max(min_year, max_year - 20)  # Last ~20 years by default
    default_year_range = (default_year_start, max_year)
    
    # Use ALL countries by default for true open access
    default_countries = all_countries
    
    st.session_state.analysis_config = {
        'countries': default_countries,
        'year_range': default_year_range,
        'indicator': default_indicator,
        'color_scale': get_color_scale(default_indicator) if default_indicator else 'Viridis',
        'timestamp': pd.Timestamp.now()
    }

# Helpful note for users
st.info("💡 **Tip:** All pages work with default settings. Use this page to customize your analysis.")

# Configuration form
with st.form("analysis_config_form"):
    st.subheader("🎛️ Customize Your Analysis (Optional)")

    # Multiselect for countries
    st.markdown("### Step 1: Select Countries")
    selected_countries = st.multiselect(
        "Select one or more countries (no limit)",
        options=all_countries,
        default=st.session_state.analysis_config['countries'],
        help="Select as many countries as you need. Click inside the box to see checkboxes.",
        key="country_multiselect"
    )

    st.caption("""
**How to select countries:**
1. Click inside the selection box
2. Check/uncheck countries from the dropdown
3. Selected countries appear as pills with X buttons
4. Select 1-50+ countries based on your needs
""")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Step 2: Select Main Indicator")
        selected_indicator = st.selectbox(
            "Indicator",
            options=all_indicators,
            index=(all_indicators.index(st.session_state.analysis_config['indicator'])
                   if st.session_state.analysis_config.get('indicator') in all_indicators else 0),
            help="Primary inequality indicator to analyze"
        )

    with col2:
        st.markdown("### Step 3: Select Color Scheme")
        color_options = ['Reds', 'Blues', 'Greens', 'Viridis', 'Plasma', 'YlOrRd']
        color_scale = st.selectbox(
            "Color Scheme",
            options=color_options,
            index=(color_options.index(st.session_state.analysis_config.get('color_scale'))
                   if st.session_state.analysis_config.get('color_scale') in color_options else 0),
            help="Visual color theme used across charts and maps"
        )

    st.markdown("### Step 4: Select Time Range")
    year_range = st.slider(
        "Year Range",
        min_value=min_year,
        max_value=max_year,
        value=st.session_state.analysis_config['year_range'],
        help="Select time period for analysis"
    )

    st.divider()

    # Submit button
    submitted = st.form_submit_button("Apply Configuration", use_container_width=True, type="primary")

    if submitted:
        # Validation
        errors = []

        if not selected_countries:
            errors.append("❌ Please select at least one country")

        # REMOVED COUNTRY LIMIT - No maximum restriction

        if year_range[0] >= year_range[1]:
            errors.append("❌ Start year must be before end year")

        if year_range[1] - year_range[0] > 100:
            errors.append("❌ Year range too large (maximum 100 years)")

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

            st.success("✅ Configuration saved! Navigate to any analysis page to see your customized view.")
            st.info(f"""
**Active Configuration:**
- **Countries:** {', '.join(selected_countries)} ({len(selected_countries)} selected)
- **Years:** {year_range[0]}-{year_range[1]}
- **Indicator:** {human_indicator(selected_indicator)}
- **Color Scheme:** {color_scale}
""")
            st.rerun()

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

    quick_submit = st.form_submit_button("Quick Analyze")

    if quick_submit and quick_country and quick_indicator:
        st.session_state.analysis_config = {
            'countries': [quick_country],
            'year_range': (min_year, max_year),
            'indicator': quick_indicator,
            'color_scale': get_color_scale(quick_indicator),
            'timestamp': pd.Timestamp.now()
        }
        st.sidebar.success(f"✅ Analyzing {quick_country} - {human_indicator(quick_indicator)}")
        st.rerun()

# Current Configuration Display
if st.session_state.analysis_config is not None:
    st.sidebar.divider()
    st.sidebar.subheader("📊 Current Configuration")
    config = st.session_state.analysis_config
    
    num_countries = len(config['countries'])
    country_display = ', '.join(config['countries'][:3])
    if num_countries > 3:
        country_display += f" (+{num_countries - 3} more)"
    
    st.sidebar.markdown(f"""
    **Countries:** {country_display}  
    **Count:** {num_countries} countries  
    **Years:** {config['year_range'][0]}-{config['year_range'][1]}  
    **Indicator:** {human_indicator(config['indicator'])}  
    **Color:** {config['color_scale']}
    """)