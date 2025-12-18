import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys
import time

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from utils.loaders import load_inequality_data
from utils.utils import human_indicator
from utils.db_manager import init_db, create_user, get_user, update_user_visit

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="South Asia Inequality Explorer",
    page_icon="🌏",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize DB
init_db()

# -----------------------------------------------------------------------------
# STATE MANAGEMENT
# -----------------------------------------------------------------------------
if 'page' not in st.session_state:
    st.session_state.page = 'landing' # landing, survey, dashboard
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

# Load Custom CSS
def load_css():
    try:
        with open('assets/dashboard.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css()

# -----------------------------------------------------------------------------
# VIEW: LANDING PAGE
# -----------------------------------------------------------------------------
def render_landing():
    # Hero Section with Animations
    st.html("""
<div class="hero-bg-animated">
    <div class="decor-circle decor-1"></div>
    <div class="decor-circle decor-2"></div>
    
    <div class="hero-content">
        <div class="animate-slide-up">
            <h1 class="hero-title">South Asia Inequality Explorer</h1>
        </div>
        <div class="animate-slide-up delay-200">
            <p class="hero-subtitle">
                Explore 25 Years of Development Data Across Bangladesh, India, Pakistan, Nepal, and Sri Lanka.
                Analyze trends, compare nations, and discover insights.
            </p>
        </div>
    </div>
</div>
    """)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
<<<<<<< Updated upstream
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
=======
        st.markdown('<div class="cta-button-container animate-slide-up delay-300">', unsafe_allow_html=True)
        if st.button("🚀 Start Exploring", use_container_width=True):
            st.session_state.page = 'survey'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown(
            """
            <div class="animate-fade-in delay-500" style="display: flex; justify-content: center; gap: 1rem; margin-top: 1rem;">
                <button class="secondary-btn floating" style="border:none; background:none; color:var(--text-secondary); cursor:pointer;">
                    📊 View Sample Dashboard
                </button>
            </div>
            """, 
            unsafe_allow_html=True
>>>>>>> Stashed changes
        )

# -----------------------------------------------------------------------------
# VIEW: SURVEY PAGE
# -----------------------------------------------------------------------------
def render_survey():
    st.markdown('<h2 class="survey-title">👋 Welcome to the Explorer</h2>', unsafe_allow_html=True)
    
    col_main, _ = st.columns([2, 1]) # Limit width for better form reading
    
    with st.container():
        st.html("""
<div class="glass-panel" style="max-width: 600px; margin: 0 auto;">
    <p style="text-align: center; color: var(--text-secondary); margin-bottom: 2rem;">
        Help us improve the platform with this 30-second survey.
    </p>
        """)
        
        with st.form("user_survey"):
            c1, c2 = st.columns(2)
            with c1:
                age = st.selectbox("Age Range *", ["Select...", "18-24", "25-34", "35-44", "45-54", "55+"])
                occupation = st.selectbox("Occupation *", [
                    "Select...", 
                    "Student (Undergraduate)", "Graduate Student / Researcher", 
                    "Academic / Professor", "Policy Maker / Government",
                    "NGO / Development Worker", "Journalist / Media",
                    "Private Sector / Consultant", "General Public", "Other"
                ])
            
            with c2:
                gender = st.selectbox("Gender *", ["Select...", "Male", "Female", "Non-binary", "Prefer not to say"])
                region = st.selectbox("Country/Region *", [
                    "Select...", "Bangladesh", "India", "Pakistan", "Nepal", "Sri Lanka", "Other South Asia", "Rest of World"
                ])
            
            email = st.text_input("Email (Optional - for updates)")
            
            st.markdown("---")
            
            submitted = st.form_submit_button("Continue to Dashboard ➔", use_container_width=True)
            
            if submitted:
                errors = []
                if age == "Select..." or gender == "Select...": errors.append("Please complete all required fields.")
                if occupation == "Select..." or region == "Select...": errors.append("Please complete all required fields.")
                
                if errors:
                    st.error(errors[0])
                else:
                    # Save User
                    user_info = {
                        "age_range": age,
                        "gender": gender,
                        "occupation": occupation,
                        "region": region,
                        "email": email
                    }
                    user_id = create_user(user_info)
                    
                    st.session_state.user_id = user_id
                    st.session_state.user_data = user_info
                    st.session_state.page = 'dashboard'
                    st.balloons()
                    time.sleep(1) # Show balloons
                    st.rerun()

        if st.button("Skip for now", key="skip_btn"):
            st.session_state.user_id = "GUEST"
            st.session_state.user_data = {"occupation": "Guest User", "region": "Global"}
            st.session_state.page = 'dashboard'
            st.rerun()
            
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# VIEW: DASHBOARD (Refactored Existing Logic)
# -----------------------------------------------------------------------------
def render_dashboard_content():
    # Load Data
    df = load_inequality_data()
    if df.empty:
        st.error("No data found! Check data files.")
        st.stop()
        
    # --- Custom Top Bar ---
    user_role = st.session_state.user_data.get('occupation', 'Guest') if st.session_state.user_data else 'Guest'
    user_loc = st.session_state.user_data.get('region', '') if st.session_state.user_data else ''
    user_display = f"{user_role}" + (f", {user_loc}" if user_loc else "")
    
    st.html(f"""
<div class="custom-navbar">
    <div class="nav-brand">
        <span>🌏</span> SA Inequality Explorer
    </div>
    <div class="nav-search">
        <input type="text" placeholder="🔍 Search indicators, countries (Demo)...">
    </div>
    <div class="nav-profile">
        <div class="user-pill">
            <span>👤</span> {user_display}
        </div>
        <div class="user-pill">
            <span>⚙️</span>
        </div>
    </div>
</div>
    """)
    
    # --- Main Dashboard Logic (From original home.py) ---
    
    # Data stats
    with st.expander("📊 Dataset Overview", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Countries", df['country'].nunique())
        c2.metric("Years", f"{int(df['year'].min())}-{int(df['year'].max())}")
        c3.metric("Indicators", df['indicator'].nunique())
        c4.metric("Records", len(df))

    st.markdown("### ⚙️ Configure Analysis")
    
    # Initialize config in session state if needed
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
            default=[],  # Start with NO countries selected
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
                st.switch_page("pages/1_dashboard.py")

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

# -----------------------------------------------------------------------------
# MAIN APP ROUTER
# -----------------------------------------------------------------------------
def app():
    if st.session_state.page == 'landing':
        render_landing()
    elif st.session_state.page == 'survey':
        render_survey()
    elif st.session_state.page == 'dashboard':
        # Sidebar remains accessible in dashboard
        with st.sidebar:
            st.html("""
            <style>
                [data-testid="stSidebarNav"] {display: none;}
            </style>
            """)
            st.title("Explorer Menu")
            st.page_link("home.py", label="Home", icon="🏠")
            st.page_link("pages/1_dashboard.py", label="Dashboard", icon="📊")
            st.page_link("pages/2_map_analysis.py", label="Map Analysis", icon="🗺️")
            st.page_link("pages/3_correlations.py", label="Correlations", icon="📈")
            st.page_link("pages/4_sunburst.py", label="Sunburst View", icon="🏵️")
            st.page_link("pages/9_temporal_compare.py", label="Temporal Compare", icon="⏳")
            
            st.divider()
            st.subheader("Tools")
            st.page_link("pages/5_income_simulator.py", label="Income Simulator", icon="💸")
            st.page_link("pages/8_auto_insights.py", label="Auto Insights", icon="🤖")
            
            st.divider()
            st.subheader("Data & Help")
            st.page_link("pages/6_data_quality.py", label="Data Quality", icon="✅")
            st.page_link("pages/7_data_sources.py", label="Data Sources", icon="📚")
            st.page_link("pages/10_help.py", label="Help & Docs", icon="📖")
            
            st.divider()
            if st.button("Logout / Reset", use_container_width=True):
                st.session_state.clear()
                st.switch_page("home.py")
                
        render_dashboard_content()

if __name__ == "__main__":
    app()