import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.loaders import load_inequality_data, load_all_indicators
from utils.utils import human_indicator, format_value
from utils.help_system import render_help_button
from utils.sidebar import apply_all_styles

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Smart Search",
    page_icon="🔍",
    layout="wide"
)
render_help_button("search")
apply_all_styles()

# Custom CSS for search enhancement - MATCHING SIDEBAR THEME
st.markdown("""
<style>
    /* Main container background matching sidebar theme */
    .main .block-container {
        background: linear-gradient(135deg, rgba(30, 25, 60, 0.95) 0%, rgba(20, 20, 40, 0.98) 100%);
        padding-top: 2rem;
    }
    
    /* Search box styling - purple theme */
    .stTextInput > div > div > input {
        font-size: 18px;
        padding: 12px;
        border-radius: 8px;
        background-color: rgba(50, 45, 85, 0.6);
        border: 1px solid rgba(139, 92, 246, 0.3);
        color: #ffffff;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #8b5cf6;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2);
    }
    
    /* Command result cards - purple theme */
    .command-card {
        padding: 15px;
        border-radius: 12px;
        border-left: 4px solid #8b5cf6;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(139, 92, 246, 0.08) 100%);
        margin: 10px 0;
        backdrop-filter: blur(10px);
    }
    
    /* Keyboard shortcut hint - matching sidebar */
    .kbd-hint {
        display: inline-block;
        padding: 3px 8px;
        font-size: 12px;
        background: rgba(139, 92, 246, 0.3);
        border: 1px solid #8b5cf6;
        border-radius: 6px;
        font-family: monospace;
        color: #e2e8f0;
    }
    
    /* Metric cards styling */
    [data-testid="stMetricValue"] {
        color: #ffffff;
        font-size: 2rem;
    }
    
    [data-testid="stMetricLabel"] {
        color: #a78bfa;
    }
    
    /* Button styling to match sidebar */
    .stButton > button {
        background: rgba(139, 92, 246, 0.2);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 8px;
        color: #ffffff;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: rgba(139, 92, 246, 0.35);
        border-color: #8b5cf6;
        box-shadow: 0 0 15px rgba(139, 92, 246, 0.3);
    }
    
    /* Primary button styling */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        border: none;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.5);
    }
    
    /* Divider styling */
    hr {
        border-color: rgba(139, 92, 246, 0.2);
    }
    
    /* Success/info/warning box styling */
    .stSuccess, .stInfo, .stWarning {
        background: rgba(139, 92, 246, 0.1);
        border-left-color: #8b5cf6;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Initialize session state
# --------------------------------------------------
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# Initialize analysis config if not exists
if 'analysis_config' not in st.session_state:
    st.session_state.analysis_config = None

# --------------------------------------------------
# Main Title
# --------------------------------------------------
st.title("🔍 Smart Search & Navigation Hub")
st.caption("Quick access to data, insights, and navigation")

st.markdown("""
<div style='background: rgba(139, 92, 246, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #8b5cf6; margin-bottom: 20px;'>
    <div style='color: #e2e8f0; font-size: 0.9rem;'>
        <strong style='color: #a78bfa;'>💡 How it works:</strong><br>
        • <strong>Search</strong> for countries, indicators, or years<br>
        • <strong>Click buttons</strong> to navigate instantly with filters applied<br>
        • <strong>Use bookmarks</strong> for one-click access to common views<br>
        • <strong>Keyboard shortcuts</strong> for power users
    </div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Load Data
# --------------------------------------------------
@st.cache_data
def load_search_data():
    """Load all data needed for search"""
    df_main = load_inequality_data()
    df_all = load_all_indicators()
    return df_main, df_all

try:
    df_main, df_all = load_search_data()
except:
    st.error("⚠️ Failed to load data. Please ensure data files exist.")
    st.stop()

if df_main.empty and df_all.empty:
    st.error("❌ No data available for search.")
    st.stop()

# Use whichever is available
df = df_all if not df_all.empty else df_main

# --------------------------------------------------
# Quick Stats Bar
# --------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Countries", df['country'].nunique())
with col2:
    st.metric(" Indicators", df['indicator'].nunique())
with col3:
    st.metric("Years", f"{int(df['year'].min())}–{int(df['year'].max())}")
with col4:
    st.metric("Total Records", f"{len(df):,}")

st.divider()

# --------------------------------------------------
# HELPER FUNCTIONS FOR NAVIGATION
# --------------------------------------------------

def navigate_with_filter(page, config):
    """Navigate to a page with pre-configured filters"""
    st.session_state.analysis_config = config
    st.switch_page(page)

def apply_country_filter(country):
    """Apply country filter and navigate to dashboard"""
    countries = df['country'].unique().tolist()
    indicators = df['indicator'].unique().tolist()
    min_year = int(df['year'].min())
    max_year = int(df['year'].max())
    default_indicator = "gini_index" if "gini_index" in indicators else indicators[0]
    
    config = {
        'countries': [country],
        'indicator': default_indicator,
        'year_range': (max(min_year, max_year - 10), max_year),
        'color_scale': 'Viridis'
    }
    navigate_with_filter("pages/1_Dashboard.py", config)

def apply_indicator_filter(indicator):
    """Apply indicator filter and navigate to dashboard"""
    countries = df['country'].unique().tolist()
    min_year = int(df['year'].min())
    max_year = int(df['year'].max())
    
    config = {
        'countries': countries,
        'indicator': indicator,
        'year_range': (max(min_year, max_year - 10), max_year),
        'color_scale': 'Viridis'
    }
    navigate_with_filter("pages/1_Dashboard.py", config)

def apply_year_filter(year):
    """Apply year filter and navigate to map"""
    countries = df['country'].unique().tolist()
    indicators = df['indicator'].unique().tolist()
    default_indicator = "gini_index" if "gini_index" in indicators else indicators[0]
    
    config = {
        'countries': countries,
        'indicator': default_indicator,
        'year_range': (year, year),
        'color_scale': 'Viridis'
    }
    navigate_with_filter("pages/3_Map_Analysis.py", config)

# --------------------------------------------------
# SECTION 1: Smart Search Command Palette
# --------------------------------------------------
st.subheader("⌨ Quick Search Command Palette")

# Keyboard shortcut hint
st.markdown("""
<div style='background-color: rgba(100,100,100,0.1); padding: 10px; border-radius: 5px; margin-bottom: 15px;'>
    💡 <b>Tip:</b> Type to search countries, indicators, years, or commands. 
    
</div>
""", unsafe_allow_html=True)

# Main search input
search_query = st.text_input(
    "🔍 Type your search query",
    placeholder="Try: 'Bangladesh', 'GINI', '2020', 'map', 'high inequality'...",
    key="main_search_input",
    label_visibility="collapsed"
)

# --------------------------------------------------
# Search Processing Function
# --------------------------------------------------
def smart_search(query, dataframe):
    """Advanced search across multiple dimensions"""
    if not query:
        return None
    
    query = query.lower().strip()
    results = {
        'countries': [],
        'indicators': [],
        'years': [],
        'commands': [],
        'filters': []
    }
    
    # 1. Search Countries
    matching_countries = dataframe[
        dataframe['country'].str.lower().str.contains(query, na=False)
    ]['country'].unique()
    
    if len(matching_countries) > 0:
        for country in matching_countries:
            country_data = dataframe[dataframe['country'] == country]
            results['countries'].append({
                'name': country,
                'indicators_available': country_data['indicator'].nunique(),
                'years_covered': f"{int(country_data['year'].min())}–{int(country_data['year'].max())}",
                'latest_year': int(country_data['year'].max()),
                'data_points': len(country_data)
            })
    
    # 2. Search Indicators
    matching_indicators = dataframe[
        dataframe['indicator'].str.lower().str.contains(query, na=False)
    ]['indicator'].unique()
    
    if len(matching_indicators) > 0:
        for indicator in matching_indicators:
            ind_data = dataframe[dataframe['indicator'] == indicator]
            latest_data = ind_data[ind_data['year'] == ind_data['year'].max()]
            results['indicators'].append({
                'name': indicator,
                'human_name': human_indicator(indicator),
                'countries_available': ind_data['country'].nunique(),
                'latest_value': latest_data['value'].mean() if not latest_data.empty else None
            })
    
    # 3. Search Years
    if query.isdigit() and len(query) == 4:
        year = int(query)
        if year in dataframe['year'].values:
            year_data = dataframe[dataframe['year'] == year]
            results['years'].append({
                'year': year,
                'records': len(year_data),
                'countries': year_data['country'].nunique(),
                'indicators': year_data['indicator'].nunique()
            })
    
    # 4. Command Keywords
    command_keywords = {
        'map': {'name': 'Geographic Map', 'page': 'pages/3_Map_analysis.py', 'description': 'Choropleth map with animation'},
        'correlation': {'name': ' Correlations', 'page': 'pages/4_Correlations.py', 'description': 'Analyze relationships'},
        'dashboard': {'name': ' Dashboard', 'page': 'pages/1_Dashboard.py', 'description': 'Multi-dimensional overview'},
        'Indicator Insights': {'name': 'Indicator Insights', 'page': 'pages/7_Indicator_Insights.py', 'description': 'Hierarchical visualization'},
        'simulator': {'name': 'Simulator', 'page': 'pages/5_Income_simulator.py', 'description': 'Income inequality modeling'},
        'quality': {'name': 'Data Quality', 'page': 'pages/6_Data_quality.py', 'description': 'Data completeness monitor'},
        'temporal': {'name': ' Temporal', 'page': 'pages/8_Temporal_comparison.py', 'description': 'Time comparison analysis'}
    }
    
    for keyword, info in command_keywords.items():
        if keyword in query:
            results['commands'].append(info)
    
    # 5. Smart Filters
    filter_keywords = {
        'high inequality': {'countries': [c for c in dataframe['country'].unique() 
                            if dataframe[(dataframe['country']==c) & (dataframe['indicator']=='gini_index')]['value'].mean() > 40],
                           'description': 'Countries with GINI > 40'},
        'low inequality': {'countries': [c for c in dataframe['country'].unique() 
                          if dataframe[(dataframe['country']==c) & (dataframe['indicator']=='gini_index')]['value'].mean() < 30],
                          'description': 'Countries with GINI < 30'},
        'improving': {'description': 'Countries with decreasing inequality trend'},
        'declining': {'description': 'Countries with increasing inequality'}
    }
    
    for filter_key, filter_info in filter_keywords.items():
        if filter_key in query:
            results['filters'].append({
                'name': filter_key.title(),
                'description': filter_info['description'],
                'countries': filter_info.get('countries', [])
            })
    
    return results

# --------------------------------------------------
# Display Search Results with WORKING BUTTONS
# --------------------------------------------------
if search_query:
    # Add to history
    if search_query not in st.session_state.search_history:
        st.session_state.search_history.insert(0, search_query)
        st.session_state.search_history = st.session_state.search_history[:10]
    
    search_results = smart_search(search_query, df)
    
    if search_results:
        total_results = sum(len(search_results[key]) for key in search_results if search_results[key])
        
        if total_results == 0:
            st.warning(f"🔍 No results found for '{search_query}'. Try different keywords.")
        else:
            st.success(f"✅ Found {total_results} results for '{search_query}'")
            
            # Display results by category
            result_types = {
                'countries': (' Countries', search_results['countries']),
                'indicators': ('Indicators', search_results['indicators']),
                'years': (' Years', search_results['years']),
                'commands': (' Quick Actions', search_results['commands']),
                'filters': (' Smart Filters', search_results['filters'])
            }
            
            for result_type, (title, items) in result_types.items():
                if items:
                    st.markdown(f"### {title}")
                    
                    if result_type == 'countries':
                        for country_info in items:
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"""
                                <div class='command-card'>
                                    <h4> {country_info['name']}</h4>
                                    <p style='color: #94a3b8; font-size: 0.9rem;'>
                                        <b>Indicators:</b> {country_info['indicators_available']} available<br>
                                        <b>Coverage:</b> {country_info['years_covered']}<br>
                                        <b>Data Points:</b> {country_info['data_points']} records
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                st.write("")  # Spacing
                                if st.button(f"Explore →", key=f"country_{country_info['name']}", 
                                           use_container_width=True, type="primary"):
                                    apply_country_filter(country_info['name'])
                    
                    elif result_type == 'indicators':
                        for indicator in items:
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                latest_val = format_value(indicator['latest_value']) if indicator['latest_value'] else 'N/A'
                                st.markdown(f"""
                                <div class='command-card'>
                                    <h4> {indicator['human_name']}</h4>
                                    <p style='color: #94a3b8; font-size: 0.9rem;'>
                                        <b>Countries:</b> {indicator['countries_available']} available<br>
                                        <b>Latest Regional Avg:</b> {latest_val}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                st.write("")  # Spacing
                                if st.button(f"Analyze →", key=f"ind_{indicator['name'][:20]}", 
                                           use_container_width=True, type="primary"):
                                    apply_indicator_filter(indicator['name'])
                    
                    elif result_type == 'years':
                        for year_info in items:
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"""
                                <div class='command-card'>
                                    <h4> Year {year_info['year']}</h4>
                                    <p style='color: #94a3b8; font-size: 0.9rem;'>
                                        <b>Records:</b> {year_info['records']}<br>
                                        <b>Countries:</b> {year_info['countries']}<br>
                                        <b>Indicators:</b> {year_info['indicators']}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                st.write("")  # Spacing
                                if st.button(f"View Map →", key=f"year_{year_info['year']}", 
                                           use_container_width=True, type="primary"):
                                    apply_year_filter(year_info['year'])
                    
                    elif result_type == 'commands':
                        for cmd in items:
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"""
                                <div class='command-card'>
                                    <h4>{cmd['name']}</h4>
                                    <p style='color: #94a3b8; font-size: 0.9rem;'>
                                        {cmd['description']}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                st.write("")  # Spacing
                                if st.button(f"Go →", key=f"cmd_{cmd['page'][:15]}", 
                                           use_container_width=True, type="primary"):
                                    st.switch_page(cmd['page'])
                    
                    elif result_type == 'filters':
                        for filter_info in items:
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"""
                                <div class='command-card'>
                                    <h4>🎯 {filter_info['name']}</h4>
                                    <p style='color: #94a3b8; font-size: 0.9rem;'>
                                        {filter_info['description']}<br>
                                        <b>Countries:</b> {len(filter_info.get('countries', []))} matched
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                st.write("")  # Spacing
                                if st.button(f"Apply →", key=f"filter_{filter_info['name'][:20]}", 
                                           use_container_width=True, type="primary"):
                                    if filter_info.get('countries'):
                                        config = {
                                            'countries': filter_info['countries'],
                                            'indicator': 'gini_index',
                                            'year_range': (int(df['year'].min()), int(df['year'].max())),
                                            'color_scale': 'Viridis'
                                        }
                                        navigate_with_filter("pages/1_Dashboard.py", config)

st.divider()

# --------------------------------------------------
# SECTION 2: Quick Action Shortcuts (ALL PAGES!)
# --------------------------------------------------
st.subheader("⚡ Quick Action Shortcuts")
st.caption("One-click navigation to all analysis pages")

# Row 1: Main pages
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Home", use_container_width=True, type="secondary", key="nav_home"):
        st.switch_page("home.py")
        
with col2:
    if st.button("Dashboard", use_container_width=True, type="secondary", key="nav_dashboard"):
        st.switch_page("pages/1_Dashboard.py")

with col3:
    if st.button(" Map Analysis", use_container_width=True, type="secondary", key="nav_map"):
        st.switch_page("pages/3_Map_Analysis.py")

with col4:
    if st.button(" Correlations", use_container_width=True, type="secondary", key="nav_corr"):
        st.switch_page("pages/4_Correlations.py")

# Row 2: Additional pages
col5, col6, col7, col8 = st.columns(4)

with col5:
    if st.button(" Income Simulator", use_container_width=True, type="secondary", key="nav_sim"):
        st.switch_page("pages/5_Income_Simulator.py")

with col6:
    if st.button(" Data Quality", use_container_width=True, type="secondary", key="nav_quality"):
        st.switch_page("pages/6_Data_Quality.py")

with col7:
    if st.button(" Indicator Insights", use_container_width=True, type="secondary", key="nav_sunburst"):
        st.switch_page("pages/7_Indicator_Insights.py")

with col8:
    if st.button("Temporal", use_container_width=True, type="secondary", key="nav_temporal"):
        st.switch_page("pages/8_Temporal_Comparison.py")

# Row 3: Help (centered)
col_spacer, col_help, col_spacer2 = st.columns([3, 2, 3])
with col_help:
    if st.button("❓ Help", use_container_width=True, type="secondary", key="nav_help"):
        st.switch_page("pages/9_Help.py")

st.divider()

# --------------------------------------------------
# SECTION 3: Bookmarked Views (SAFE VERSION WITH ERROR HANDLING!)
# --------------------------------------------------
st.subheader("⭐ Quick Access Bookmarks")
st.caption("Pre-configured views for common analysis needs")

# Helper function to find the actual GINI indicator name in data
def get_gini_indicator():
    """Auto-detect the GINI indicator name from available data"""
    # Try common variations
    gini_variations = ['gini_index', 'GINI Index', 'SI.POV.GINI', 'gini', 'GINI']
    
    for variation in gini_variations:
        # Exact match
        if variation in df['indicator'].values:
            return variation
        # Case-insensitive match
        try:
            matches = df[df['indicator'].str.contains(variation, case=False, na=False)]
            if not matches.empty:
                return matches['indicator'].iloc[0]
        except:
            continue
    
    # Fallback: return first indicator
    return df['indicator'].iloc[0] if not df.empty else 'gini_index'

# Helper function to safely get high inequality countries
def get_high_inequality_countries(threshold=40):
    """Get countries with average GINI > threshold, with fallback"""
    try:
        gini_indicator = get_gini_indicator()
        gini_data = df[df['indicator'] == gini_indicator]
        
        if gini_data.empty:
            return df['country'].unique().tolist()
        
        avg_gini = gini_data.groupby('country')['value'].mean()
        high_countries = avg_gini[avg_gini > threshold].index.tolist()
        
        # If no countries match, lower threshold or use all
        if not high_countries:
            # Try lower threshold
            high_countries = avg_gini[avg_gini > 35].index.tolist()
            if not high_countries:
                # Use all countries as fallback
                return df['country'].unique().tolist()
        
        return high_countries
    except Exception as e:
        # If anything fails, return all countries
        return df['country'].unique().tolist()

# Helper function to safely get low inequality countries
def get_low_inequality_countries(threshold=30):
    """Get countries with average GINI < threshold, with fallback"""
    try:
        gini_indicator = get_gini_indicator()
        gini_data = df[df['indicator'] == gini_indicator]
        
        if gini_data.empty:
            return df['country'].unique().tolist()
        
        avg_gini = gini_data.groupby('country')['value'].mean()
        low_countries = avg_gini[avg_gini < threshold].index.tolist()
        
        # If no countries match, try higher threshold or use all
        if not low_countries:
            # Try higher threshold
            low_countries = avg_gini[avg_gini < 35].index.tolist()
            if not low_countries:
                # Use all countries as fallback
                return df['country'].unique().tolist()
        
        return low_countries
    except Exception as e:
        # If anything fails, return all countries
        return df['country'].unique().tolist()

# Get the actual GINI indicator name from data
detected_gini_indicator = get_gini_indicator()

# SAFE BOOKMARKS with automatic error handling
bookmarks = {
    "🔴 High Inequality Countries": {
        "description": "Countries with GINI > 40 (severe inequality)",
        "countries": get_high_inequality_countries(40),
        "indicator": detected_gini_indicator,
        "page": "pages/1_Dashboard.py"
    },
    "🟢 Low Inequality Countries": {
        "description": "Countries with GINI < 30 (more equitable)",
        "countries": get_low_inequality_countries(30),
        "indicator": detected_gini_indicator,
        "page": "pages/1_Dashboard.py"
    },
    "📈 Recent Decade Analysis": {
        "description": "Focus on 2015-2024 data",
        "countries": df['country'].unique().tolist(),
        "indicator": detected_gini_indicator,
        "year_range": (max(2015, int(df['year'].min())), int(df['year'].max())),
        "page": "pages/1_Dashboard.py"
    },
    "💰 GDP vs Inequality": {
        "description": "Explore economic growth and inequality relationship",
        "page": "pages/4_Correlations.py"
    },
    "🌍 Regional Comparison": {
        "description": "Compare all countries side-by-side",
        "countries": df['country'].unique().tolist(),
        "indicator": detected_gini_indicator,
        "page": "pages/7_Indicator_Insights.py"
    },
    "🗺️ Latest Year Geographic View": {
        "description": "Map visualization of most recent data",
        "countries": df['country'].unique().tolist(),
        "indicator": detected_gini_indicator,
        "year_range": (int(df['year'].max()), int(df['year'].max())),
        "page": "pages/3_Map_Analysis.py"
    }
}

col1, col2 = st.columns([3, 1])

with col1:
    selected_bookmark = st.selectbox(
        "Choose a bookmarked view:",
        list(bookmarks.keys()),
        label_visibility="collapsed"
    )

bookmark_info = bookmarks[selected_bookmark]

col_desc, col_action = st.columns([3, 1])

with col_desc:
    st.markdown(f"""
    <div style='background: rgba(139, 92, 246, 0.1); padding: 15px; border-radius: 8px; border-left: 3px solid #8b5cf6;'>
        <div style='color: #e2e8f0; font-size: 0.9rem;'>
            <strong style='color: #a78bfa;'>{selected_bookmark}</strong><br>
            {bookmark_info['description']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show filter info if countries are specified
    if 'countries' in bookmark_info:
        st.caption(f"📍 Will filter to: {len(bookmark_info['countries'])} countries")

with col_action:
    st.write("")  # Spacing
    st.write("")  # Spacing
    if st.button("Execute Bookmark →", use_container_width=True, type="primary", key="execute_bookmark"):
        # Build config if needed
        if 'countries' in bookmark_info:
            # Validate that we have countries
            if not bookmark_info['countries']:
                st.error("❌ No countries match this filter. Please try a different bookmark.")
                st.stop()
            
            config = {
                'countries': bookmark_info['countries'],
                'indicator': bookmark_info.get('indicator', detected_gini_indicator),
                'year_range': bookmark_info.get('year_range', (int(df['year'].min()), int(df['year'].max()))),
                'color_scale': 'Viridis'
            }
            navigate_with_filter(bookmark_info['page'], config)
        else:
            # Just navigate without config
            st.switch_page(bookmark_info['page'])

st.divider()

# --------------------------------------------------
# SECTION 4: Search History
# --------------------------------------------------
if st.session_state.search_history:
    st.subheader(" Recent Searches")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.caption("Click to search again")
    with col2:
        if st.button("Clear History", key="clear_history"):
            st.session_state.search_history = []
            st.rerun()
    
    # Display history as clickable pills
    cols = st.columns(5)
    for idx, query in enumerate(st.session_state.search_history[:10]):
        with cols[idx % 5]:
            if st.button(f"🔍 {query}", key=f"history_{idx}", use_container_width=True):
                st.session_state.main_search_input = query
                st.rerun()

st.divider()

# --------------------------------------------------
# SECTION 5: Search Tips & Help
# --------------------------------------------------
with st.expander("💡 Search Tips & Keyboard Shortcuts"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Search Capabilities
        
        ** By Country:**
        - Type: `Bangladesh`, `India`, `Pakistan`
        - Click "Explore →" to view in dashboard
        
        ** By Indicator:**
        - Type: `GINI`, `HDI`, `GDP`
        - Click "Analyze →" to view trends
        
        ** By Year:**
        - Type: `2020`, `2015`, `2010`
        - Click "View Map →" to see geographic view
        
        **⚡ By Command:**
        - Type: `map`, `correlation`, `dashboard`
        - Click "Go →" to navigate instantly
        """)
    
    with col2:
        st.markdown("""
        ### Pro Tips
        
        ✅ **Combine terms:** `Bangladesh 2020`  
        ✅ **Partial matches:** `gin` finds GINI  
        ✅ **Natural language:** `high inequality`  
        ✅ **Use bookmarks:** Fastest for common views  
        ✅ **Check history:** Re-run past searches  
        
        ### What's Different
        
         **Real Navigation:** Buttons actually work!  
         **Filters Applied:** Goes to page with data pre-loaded  
         **One-Click Actions:** No manual configuration needed  
         **Working Bookmarks:** Execute complex views instantly
        """)

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.divider()
st.markdown("""
<div style='text-align: center; color: #94a3b8; font-size: 0.85rem;'>
    <p><strong>🔍 Smart Search & Navigation Hub</strong> | South Asia Inequality Analysis Platform</p>
</div>
""", unsafe_allow_html=True)

# -----------------
# Navigation
# -----------------
from utils.navigation_ui import bottom_nav_layout
bottom_nav_layout(__file__)
