import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from utils.loaders import load_inequality_data
from utils.utils import human_indicator, get_color_scale

st.set_page_config(
    page_title="...",
    page_icon="...",
    layout="wide",
    initial_sidebar_state="collapsed"  # ADD THIS LINE
)


st.markdown("""
<style>
    /* Hide the Streamlit sidebar navigation */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Hide sidebar toggle button */
    [data-testid="collapsedControl"] {
        display: none;
    }
    
    /* Expand main content to full width */
    .main {
        margin-left: 0 !important;
    }
    
    /* Remove extra padding */
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)



# Modern dark theme CSS 
st.markdown("""
<style>
    /* Main dark gradient background */
    .main {
        background: linear-gradient(180deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
    }
    
    /* Remove padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 800 !important;
    }
    
    /* Form styling */
    .stForm {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(236, 72, 153, 0.05) 100%);
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #8b5cf6 0%, #ec4899 100%);
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        box-shadow: 0 6px 30px rgba(139, 92, 246, 0.6);
        transform: translateY(-2px);
    }
    
    /* Selectbox and multiselect styling */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: rgba(15, 20, 25, 0.6);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 8px;
        color: #ffffff;
    }
    
    /* Slider styling */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #8b5cf6 0%, #ec4899 100%);
    }
    
    /* Info/success boxes */
    .stAlert {
        background: rgba(15, 20, 25, 0.6);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 12px;
        color: #e2e8f0;
    }
    
    /* Text colors */
    p, label, .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    /* Caption text */
    .css-16huue1 {
        color: #94a3b8 !important;
    }
    
    /* Navigation cards */
    .nav-card {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(236, 72, 153, 0.05) 100%);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }
    
    .nav-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 32px rgba(139, 92, 246, 0.4);
        border-color: rgba(139, 92, 246, 0.5);
    }
    
    /* Style navigation buttons to look like cards */
    div[data-testid="column"] > div > div > button {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(236, 72, 153, 0.05) 100%) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 16px !important;
        padding: 2rem 1.5rem !important;
        height: auto !important;
        min-height: 140px !important;
        color: #e2e8f0 !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        white-space: pre-line !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
        line-height: 1.6 !important;
    }
    
    div[data-testid="column"] > div > div > button:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 8px 32px rgba(139, 92, 246, 0.4) !important;
        border-color: rgba(139, 92, 246, 0.5) !important;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(236, 72, 153, 0.08) 100%) !important;
    }
    
    div[data-testid="column"] > div > div > button:active {
        transform: translateY(-2px) !important;
    }
</style>
""", unsafe_allow_html=True)

# Load data
df = load_inequality_data()
if df.empty:
    st.error("❌ Data not found. Please ensure processed dataset exists.")
    st.stop()

# ═══════════════════════════════════════════════════════════════════
# HERO SECTION
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<div style="text-align: center; margin-bottom: 3rem;">
    <h1 style="font-size: 3.5rem; margin-bottom: 1rem; background: linear-gradient(90deg, #8b5cf6 0%, #ec4899 50%, #06b6d4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
        South Asia Inequality Analytics
    </h1>
    <p style="font-size: 1.3rem; color: #94a3b8; margin-top: 0;">
        Professional Data Visualization & Analysis Platform
    </p>
    <p style="font-size: 1rem; color: #64748b; margin-top: 1rem;">
         Advanced analytics •  AI-powered insights
    </p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# QUICK STATS ROW
# ═══════════════════════════════════════════════════════════════════

st.markdown('<p style="text-align: center; color: #94a3b8; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 1rem;">Platform Overview</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 1.5rem; background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(139, 92, 246, 0.05)); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 12px; height: 200px; display: flex; flex-direction: column; justify-content: center;">
        <div style="font-size: 3rem; margin-bottom: 1rem;"></div>
        <div style="font-size: 2.5rem; font-weight: 800; color: #8b5cf6; margin-bottom: 0.5rem;">{len(df['country'].unique())}</div>
        <div style="color: #94a3b8; font-size: 0.9rem;">Countries</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 1.5rem; background: linear-gradient(135deg, rgba(236, 72, 153, 0.15), rgba(236, 72, 153, 0.05)); border: 1px solid rgba(236, 72, 153, 0.3); border-radius: 12px; height: 200px; display: flex; flex-direction: column; justify-content: center;">
        <div style="font-size: 3rem; margin-bottom: 1rem;"></div>
        <div style="font-size: 2.5rem; font-weight: 800; color: #ec4899; margin-bottom: 0.5rem;">{len(df['indicator'].unique())}</div>
        <div style="color: #94a3b8; font-size: 0.9rem;">Indicators</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    years_span = int(df['year'].max() - df['year'].min())
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 1.5rem; background: linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(6, 182, 212, 0.05)); border: 1px solid rgba(6, 182, 212, 0.3); border-radius: 12px; height: 200px; display: flex; flex-direction: column; justify-content: center;">
        <div style="font-size: 3rem; margin-bottom: 1rem;"></div>
        <div style="font-size: 2.5rem; font-weight: 800; color: #06b6d4; margin-bottom: 0.5rem;">{years_span}</div>
        <div style="color: #94a3b8; font-size: 0.9rem;">Years of Data</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 1.5rem; background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.05)); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; height: 200px; display: flex; flex-direction: column; justify-content: center;">
        <div style="font-size: 3rem; margin-bottom: 1rem;"></div>
        <div style="font-size: 2.5rem; font-weight: 800; color: #10b981; margin-bottom: 0.5rem;">{len(df):,}</div>
        <div style="color: #94a3b8; font-size: 0.9rem;">Data Points</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# NAVIGATION CARDS (Quick Access)
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h2 style="font-size: 2rem; color: #ffffff;"> Quick Access</h2>
    <p style="color: #94a3b8;">Jump directly to any analysis tool</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("\n\nDashboard\n\nReal-time KPIs & streamgraph", key="nav_dashboard", use_container_width=True):
        st.switch_page("pages/1_dashboard.py")
    
    if st.button("🔗\n\nCorrelations\n\nMulti-indicator analysis", key="nav_correlations", use_container_width=True):
        st.switch_page("pages/3_correlations.py")

with col2:
    if st.button("\n\nMap Analysis\n\nGeographic visualization", key="nav_map", use_container_width=True):
        st.switch_page("pages/2_map_analysis.py")
    
    if st.button("\n\nTemporal Compare\n\nThen vs Now analysis", key="nav_temporal", use_container_width=True):
        st.switch_page("pages/9_temporal_compare.py")

with col3:
    if st.button("\n\nAuto Insights\n\nAI-generated discoveries", key="nav_insights", use_container_width=True):
        st.switch_page("pages/8_auto_insights.py")
    
    if st.button("\n\nPolicy Simulator\n\nScenario modeling", key="nav_simulator", use_container_width=True):
        st.switch_page("pages/5_income_simulator.py")

st.markdown("<br><br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION SECTION
# ═══════════════════════════════════════════════════════════════════

# Initialize session state
if 'analysis_config' not in st.session_state:
    st.session_state.analysis_config = None

# Get available options
all_countries = sorted(df['country'].unique())
all_indicators = sorted(df['indicator'].unique())
min_year = int(df['year'].min())
max_year = int(df['year'].max())

# Create defaults if none exist
if st.session_state.analysis_config is None:
    default_indicator = 'gini_index' if 'gini_index' in all_indicators else (all_indicators[0] if all_indicators else None)
    default_year_start = max(min_year, max_year - 20)
    default_year_range = (default_year_start, max_year)
    
    st.session_state.analysis_config = {
        'countries': all_countries,
        'year_range': default_year_range,
        'indicator': default_indicator,
        'color_scale': get_color_scale(default_indicator) if default_indicator else 'Viridis',
        'timestamp': pd.Timestamp.now()
    }

st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h2 style="font-size: 2rem; color: #ffffff;"> Customize Analysis</h2>
    <p style="color: #94a3b8;">Fine-tune your analysis parameters (optional)</p>
</div>
""", unsafe_allow_html=True)

# Configuration form
with st.form("analysis_config_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("####  Countries")
        selected_countries = st.multiselect(
            "Select countries to analyze",
            options=all_countries,
            default=st.session_state.analysis_config['countries'][:5] if len(st.session_state.analysis_config['countries']) > 5 else st.session_state.analysis_config['countries'],
            help="Select one or more countries. No limit!",
            key="country_multiselect"
        )
        
        st.markdown("####  Indicator")
        selected_indicator = st.selectbox(
            "Primary inequality metric",
            options=all_indicators,
            index=(all_indicators.index(st.session_state.analysis_config['indicator'])
                   if st.session_state.analysis_config.get('indicator') in all_indicators else 0),
            help="Main indicator for analysis"
        )
    
    with col2:
        st.markdown("####  Time Period")
        year_range = st.slider(
            "Select year range",
            min_value=min_year,
            max_value=max_year,
            value=st.session_state.analysis_config['year_range'],
            help="Choose time period for analysis"
        )
        
        st.markdown("#### 🎨 Color Scheme")
        color_options = ['Reds', 'Blues', 'Greens', 'Viridis', 'Plasma', 'YlOrRd', 'Purples']
        color_scale = st.selectbox(
            "Visual theme",
            options=color_options,
            index=(color_options.index(st.session_state.analysis_config.get('color_scale'))
                   if st.session_state.analysis_config.get('color_scale') in color_options else 0),
            help="Color palette for charts and maps"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submitted = st.form_submit_button(
            "🚀 Apply Configuration",
            use_container_width=True,
            type="primary"
        )
    
    if submitted:
        # Validation
        errors = []
        
        if not selected_countries:
            errors.append("❌ Please select at least one country")
        
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
            
            st.success("✅ Configuration saved successfully!")
            st.info(f"""
**Active Configuration:**
- **Countries:** {', '.join(selected_countries[:3])}{'...' if len(selected_countries) > 3 else ''} ({len(selected_countries)} total)
- **Years:** {year_range[0]}-{year_range[1]}
- **Indicator:** {human_indicator(selected_indicator)}
- **Color Scheme:** {color_scale}
            
🚀 Navigate to any analysis page to see your customized view!
""")
            st.rerun()

# ═══════════════════════════════════════════════════════════════════
# CURRENT CONFIGURATION DISPLAY
# ═══════════════════════════════════════════════════════════════════

if st.session_state.analysis_config is not None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1rem;">
        <h3 style="font-size: 1.5rem; color: #ffffff;"> Current Configuration</h3>
    </div>
    """, unsafe_allow_html=True)
    
    config = st.session_state.analysis_config
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem 1rem; background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 12px; height: 140px; display: flex; flex-direction: column; justify-content: center;">
            <div style="color: #8b5cf6; font-size: 0.85rem; margin-bottom: 0.5rem; font-weight: 600;">COUNTRIES</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #ffffff; margin-bottom: 0.5rem;">{len(config['countries'])}</div>
            <div style="color: #94a3b8; font-size: 0.75rem;">selected</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem 1rem; background: rgba(236, 72, 153, 0.1); border: 1px solid rgba(236, 72, 153, 0.3); border-radius: 12px; height: 140px; display: flex; flex-direction: column; justify-content: center;">
            <div style="color: #ec4899; font-size: 0.85rem; margin-bottom: 0.5rem; font-weight: 600;">INDICATOR</div>
            <div style="font-size: 1rem; font-weight: 700; color: #ffffff; margin-bottom: 0.5rem;">{config['indicator'].upper()}</div>
            <div style="color: #94a3b8; font-size: 0.75rem;">primary metric</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        years_span = config['year_range'][1] - config['year_range'][0]
        st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem 1rem; background: rgba(6, 182, 212, 0.1); border: 1px solid rgba(6, 182, 212, 0.3); border-radius: 12px; height: 140px; display: flex; flex-direction: column; justify-content: center;">
            <div style="color: #06b6d4; font-size: 0.85rem; margin-bottom: 0.5rem; font-weight: 600;">TIME SPAN</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #ffffff; margin-bottom: 0.5rem;">{years_span}</div>
            <div style="color: #94a3b8; font-size: 0.75rem;">years</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem 1rem; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; height: 140px; display: flex; flex-direction: column; justify-content: center;">
            <div style="color: #10b981; font-size: 0.85rem; margin-bottom: 0.5rem; font-weight: 600;">COLOR</div>
            <div style="font-size: 1rem; font-weight: 700; color: #ffffff; margin-bottom: 0.5rem;">{config['color_scale']}</div>
            <div style="color: #94a3b8; font-size: 0.75rem;">theme</div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# HELP & DOCUMENTATION SECTION 
# ═══════════════════════════════════════════════════════════════════

st.divider()

st.markdown("""
<div style="text-align: center; margin: 60px 0 40px 0;">
    <h2 style="color: #ffffff; font-size: 2rem; font-weight: 600; margin-bottom: 12px;">
        Need Help?
    </h2>
    <p style="color: #94a3b8; font-size: 1rem; margin-bottom: 32px;">
        Access comprehensive documentation, metric explanations, and methodology details
    </p>
</div>
""", unsafe_allow_html=True)

# Centered Help Button
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button("📚 Open Help & Documentation", use_container_width=True, type="primary"):
        st.switch_page("pages/10_help.py")



# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 2rem 0; border-top: 1px solid rgba(148, 163, 184, 0.1);">
    <p style="color: #64748b; font-size: 0.85rem; margin: 0;">
        <strong style="color: #8b5cf6;">South Asia Inequality Analytics Platform</strong>
    </p>
    <p style="color: #475569; font-size: 0.75rem; margin-top: 0.5rem;">
        Powered by Streamlit & Plotly • Data: World Bank, UNDP, ADB
    </p>
    <p style="color: #475569; font-size: 0.7rem; margin-top: 0.5rem;">
        Built with  for data-driven policy making
    </p>
</div>
""", unsafe_allow_html=True)