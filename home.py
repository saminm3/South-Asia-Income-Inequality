import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from utils.loaders import load_inequality_data
from utils.data_loader import SouthAsiaDataLoader
from utils.utils import human_indicator, get_color_scale
from utils.help_system import render_help_button
from utils.sidebar import apply_all_styles
from utils.user_manager import UserManager
import time
import os 
from utils.api_loader import get_api_loader


st.set_page_config(
    page_title="South Asia Inequality Analytics",
    page_icon="🌏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------
# Sidebar
# ----------------------------
with st.sidebar:
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", width=50)
    
    st.subheader("Navigation")
    
    # Load Profile Feature
    with st.expander("📂 Load Saved Profile"):
        load_email = st.text_input("Enter your email", key="load_email_input")
        if st.button("Load Configuration", use_container_width=True):
            if load_email:
                if 'user_manager' not in st.session_state:
                    st.session_state.user_manager = UserManager()
                
                with st.spinner("Searching..."):
                    saved_config = st.session_state.user_manager.get_user_config(load_email)
                    
                if saved_config:
                    st.session_state.analysis_config = saved_config
                    st.success("✅ Configuration loaded!")
                    time.sleep(1)
                    st.switch_page("pages/1_Dashboard.py")
                else:
                    st.error("No profile found.")
            else:
                st.warning("Enter email to load.")
    
    st.markdown("---")


apply_all_styles()

render_help_button("home")

# Load Curated Data for the Platform stats
df = load_inequality_data()
if df.empty:
    st.error("Data not found. Please ensure processed/curated_indicators.csv exists.")
    st.stop()

# Calculate stats from curated data
total_records = len(df)
total_indicators = df['indicator'].nunique()
total_countries = df['country'].nunique()
year_min = int(df['year'].min())
year_max = int(df['year'].max())
year_span = f"{year_min}-{year_max}"

# Fetch additional API Stats if they exist
api_loader = get_api_loader()
api_stats = api_loader.get_api_summary_v2()

# Final stats for display
display_data_points = total_records + api_stats['total_records']
display_indicators = total_indicators + api_stats['indicators']

# HERO SECTION
st.markdown("""
<div style="text-align: center; margin-bottom: 3rem;">
    <h1 style="font-size: 3.5rem; margin-bottom: 1rem; background: linear-gradient(90deg, #8b5cf6 0%, #ec4899 50%, #06b6d4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
        South Asia Inequality Analytics
    </h1>
    <p style="font-size: 1.3rem; color: #94a3b8; margin-top: 0;">
        Professional Data Visualization & Analysis Platform
    </p>
    <p style="font-size: 1rem; color: #64748b; margin-top: 1rem;">
         Advanced analytics •  Automated insights
    </p>
</div>
""", unsafe_allow_html=True)

# QUICK STATS ROW
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
        <div style="font-size: 2.5rem; font-weight: 800; color: #ec4899; margin-bottom: 0.5rem;">{display_indicators}</div>
        <div style="color: #94a3b8; font-size: 0.9rem;">Total Indicators</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 1.5rem; background: linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(6, 182, 212, 0.05)); border: 1px solid rgba(6, 182, 212, 0.3); border-radius: 12px; height: 200px; display: flex; flex-direction: column; justify-content: center;">
        <div style="font-size: 3rem; margin-bottom: 1rem;"></div>
        <div style="font-size: 2rem; font-weight: 800; color: #06b6d4; margin-bottom: 0.5rem;">{year_span}</div>
        <div style="color: #94a3b8; font-size: 0.9rem;">Years of Data</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 1.5rem; background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.05)); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; height: 200px; display: flex; flex-direction: column; justify-content: center;">
        <div style="font-size: 3rem; margin-bottom: 1rem;"></div>
        <div style="font-size: 2.5rem; font-weight: 800; color: #10b981; margin-bottom: 0.5rem;">{display_data_points:,}</div>
        <div style="color: #94a3b8; font-size: 0.9rem;">Total Data Points</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# CONFIGURATION SECTION

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
    # Prioritize Top 10% Income Share, then Gini, then first available
    if 'Top 10% Income Share' in all_indicators:
        default_indicator = 'Top 10% Income Share'
    elif 'gini_index' in all_indicators:
        default_indicator = 'gini_index'
    else:
        default_indicator = all_indicators[0] if all_indicators else None
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
    <h2 style="font-size: 2rem; color: #ffffff;">Customize Analysis</h2>
    <p style="color: #94a3b8;">Settings update automatically when you make changes</p>
</div>
""", unsafe_allow_html=True)

# Auto-updating configuration (no form/apply button needed)
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Countries")
    selected_countries = st.multiselect(
        "Select countries to analyze",
        options=all_countries,
        default=st.session_state.analysis_config['countries'][:5] if len(st.session_state.analysis_config['countries']) > 5 else st.session_state.analysis_config['countries'],
        help="Select one or more countries",
        key="country_multiselect"
    )
    
    st.markdown("#### Indicator")
    
    # Import the new indicator metadata system
    from utils.indicator_metadata import (
        get_available_indicators_by_category, 
        get_indicator_description,
        INDICATOR_CATEGORIES
    )
    
    # Get categorized indicators that are available in the data
    available_categories = get_available_indicators_by_category(df)
    
    # Step 1: Select Category
    category_names = list(available_categories.keys())
    
    # Find current category for the selected indicator
    current_category = None
    current_indicator = st.session_state.analysis_config.get('indicator')
    
    for cat_name, cat_info in available_categories.items():
        if current_indicator in cat_info['indicators']:
            current_category = cat_name
            break
    
    if current_category is None and category_names:
        current_category = category_names[0]
    
    selected_category = st.selectbox(
        "Category",
        options=category_names,
        index=category_names.index(current_category) if current_category in category_names else 0,
        help="Choose the type of inequality metric",
        key="indicator_category"
    )
    
    # Step 2: Select Indicator within Category
    indicators_in_category = available_categories[selected_category]['indicators']
    
    # Find default indicator
    if current_indicator in indicators_in_category:
        default_idx = indicators_in_category.index(current_indicator)
    else:
        default_idx = 0
    
    selected_indicator = st.selectbox(
        "Primary inequality metric",
        options=indicators_in_category,
        index=default_idx,
        help=available_categories[selected_category]['description'],
        key="indicator_selector"
    )
    
    # Show description for selected indicator
    description = get_indicator_description(selected_indicator)
    if description:
        st.caption(f"ℹ️ {description}")

with col2:
    st.markdown("#### Time Period")
    year_range = st.slider(
        "Select year range",
        min_value=min_year,
        max_value=max_year,
        value=st.session_state.analysis_config['year_range'],
        help="Choose time period for analysis"
    )
    
    st.markdown("#### Color Scheme")
    color_options = ['Reds', 'Blues', 'Greens', 'Viridis', 'Plasma', 'YlOrRd', 'Purples']
    color_scale = st.selectbox(
        "Visual theme",
        options=color_options,
        index=(color_options.index(st.session_state.analysis_config.get('color_scale'))
               if st.session_state.analysis_config.get('color_scale') in color_options else 0),
        help="Color palette for charts and maps"
    )


# Store temporary selections (not applied until confirmed)
if 'temp_config' not in st.session_state:
    st.session_state.temp_config = {
        'countries': selected_countries,
        'year_range': year_range,
        'indicator': selected_indicator,
        'color_scale': color_scale
    }

# Update temp config with current selections
temp_config = {
    'countries': selected_countries,
    'year_range': year_range,
    'indicator': selected_indicator,
    'color_scale': color_scale
}

# Check if configuration has changed from the applied one
config_changed = (
    st.session_state.analysis_config['countries'] != selected_countries or
    st.session_state.analysis_config['year_range'] != year_range or
    st.session_state.analysis_config['indicator'] != selected_indicator or
    st.session_state.analysis_config.get('color_scale') != color_scale
)

# Confirm Configuration Button
st.markdown("<br>", unsafe_allow_html=True)

# Initialize User Manager
if 'user_manager' not in st.session_state:
    st.session_state.user_manager = UserManager()

# Dialog logic replacement (compatible with older Streamlit)
if 'show_save_options' not in st.session_state:
    st.session_state.show_save_options = False

col_btn = st.columns([1, 2, 1])
with col_btn[1]:
    if selected_countries:
        if config_changed:
            if st.button(
                "Confirm Configuration",
                use_container_width=True,
                type="primary",
                help="Apply these settings to all analysis pages"
            ):
                st.session_state.show_save_options = True
                
        else:
            if st.button("View Dashboard", use_container_width=True, type="primary"):
                st.switch_page("pages/1_Dashboard.py")
            st.info("✓ Configuration is up to date")
            st.session_state.show_save_options = False
    else:
        st.warning("Please select at least one country")

# Show save options if triggered
if st.session_state.get('show_save_options'):
    st.markdown("---")
    st.info("Do you want to save this configuration for future visits?")
    
    col_save_1, col_save_2 = st.columns(2)
    
    with col_save_1:
        if st.button("Yes, Save for Future", use_container_width=True):
            st.session_state.save_choice = 'yes'
            
    with col_save_2:
        if st.button("No, Just for Now", use_container_width=True):
            new_config = {
                'countries': selected_countries,
                'year_range': year_range,
                'indicator': selected_indicator,
                'color_scale': color_scale,
                'timestamp': pd.Timestamp.now()
            }
            st.session_state.analysis_config = new_config
            st.session_state.show_save_options = False
            st.success("Configuration applied for this session.")
            time.sleep(1)
            st.switch_page("pages/1_Dashboard.py")

    # If user chose to save
    if st.session_state.get('save_choice') == 'yes':
        st.markdown("##### User Profile")
        with st.container():
            email = st.text_input("Email Address", placeholder="name@example.com")
            col_inp1, col_inp2 = st.columns(2)
            with col_inp1:
                age_group = st.selectbox("Age Group", ["Under 18", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"])
            with col_inp2:
                occupation = st.text_input("Occupation", placeholder="Researcher")
            
            if st.button("Save & Apply Profile", type="primary", use_container_width=True):
                if email and occupation:
                    new_config = {
                        'countries': selected_countries,
                        'year_range': year_range,
                        'indicator': selected_indicator,
                        'color_scale': color_scale,
                        'timestamp': pd.Timestamp.now()
                    }
                    
                    with st.spinner("Saving profile..."):
                        success = st.session_state.user_manager.save_user_profile(
                            email, age_group, occupation, new_config
                        )
                        
                        if success:
                            st.session_state.analysis_config = new_config
                            st.session_state.show_save_options = False
                            st.session_state.save_choice = None
                            st.success("Profile saved! Configuration applied.")
                            time.sleep(1)
                            st.switch_page("pages/1_Dashboard.py")
                        else:
                            st.error("Failed to connect to database. Check API keys.")
                else:
                    st.warning("Please fill in email and occupation.")


# CURRENT CONFIGURATION DISPLAY

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

# HELP & DOCUMENTATION SECTION 

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
    if st.button("Open Help & Documentation", use_container_width=True, type="primary"):
        st.switch_page("pages/9_help.py")

# DEVELOPER ACCESS INFORMATION




# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 2rem 0; border-top: 1px solid rgba(148, 163, 184, 0.1);">
    <p style="color: #64748b; font-size: 0.85rem; margin: 0;">
        <strong style="color: #8b5cf6;">South Asia Inequality Analytics Platform</strong>
    </p>
    <p style="color: #475569; font-size: 0.7rem; margin-top: 0.5rem;">
        Built with  for data-driven policy making
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------
# Navigation
# -----------------
from utils.navigation_ui import bottom_nav_layout
bottom_nav_layout(__file__)


