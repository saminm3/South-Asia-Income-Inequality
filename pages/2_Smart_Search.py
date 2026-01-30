import streamlit as st
import pandas as pd
import sys
import re
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
    page_icon="search",
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
    
    /* METRIC CARDS: Much more purple glow theme */
    div[data-testid="stMetric"], div[data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.25) 0%, rgba(99, 102, 241, 0.2) 100%) !important;
        border: 1px solid rgba(139, 92, 246, 0.5) !important;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.25), 0 0 40px rgba(139, 92, 246, 0.1) !important;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover, div[data-testid="metric-container"]:hover {
        border-color: rgba(139, 92, 246, 0.8) !important;
        box-shadow: 0 4px 30px rgba(139, 92, 246, 0.45), 0 0 50px rgba(139, 92, 246, 0.25) !important;
        transform: translateY(-2px);
    }
    
    div[data-testid="stMetricLabel"] {
        color: #a78bfa !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    div[data-testid="stMetricDelta"] {
        font-size: 0.875rem !important;
    }
    
    /* Button styling to match sidebar - Reduced intensity but visible */
    .stButton > button {
        background: rgba(139, 92, 246, 0.15);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 8px;
        color: #ffffff;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: rgba(139, 92, 246, 0.3);
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
st.title("Smart Search & Navigation Hub")
st.caption("Quick access to data, insights, and navigation")

st.markdown("""
<div style='background: rgba(139, 92, 246, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #8b5cf6; margin-bottom: 20px;'>
    <div style='color: #e2e8f0; font-size: 0.9rem;'>
        <strong style='color: #a78bfa;'>How it works:</strong><br>
        • <strong>Search</strong> for countries, indicators, or years<br>
        • <strong>Commands</strong> for instant navigation (map, dashboard, simulator, etc.)<br>
        • <strong>Comparisons</strong> using natural language (compare India Pakistan)<br>
        • <strong>Time filters</strong> like "recent", "last decade", "2015-2023"<br>
        • <strong>Bookmarks</strong> for one-click access to common views
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
    st.error("Failed to load data. Please ensure data files exist.")
    st.stop()

if df_main.empty and df_all.empty:
    st.error("No data available for search.")
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
    st.metric("Indicators", df['indicator'].nunique())
with col3:
    st.metric("Years", f"{int(df['year'].min())}–{int(df['year'].max())}")
with col4:
    st.metric("Total Records", f"{len(df):,}")

st.divider()

# --------------------------------------------------
# ENHANCED COMMAND DEFINITIONS
# --------------------------------------------------

# Navigation commands - expanded
COMMAND_KEYWORDS = {
    # Core pages
    'map': 'pages/3_Map_Analysis.py',
    'correlation': 'pages/4_Correlations.py',
    'dashboard': 'pages/1_Dashboard.py',
    'simulator': 'pages/5_Income_Simulator.py',
    'temporal': 'pages/8_Temporal_Comparison.py',
    'quality': 'pages/6_Data_Quality.py',
    'insights': 'pages/7_Indicator_Insights.py',
    'help': 'pages/9_Help.py',
    'home': 'home.py',
    
    # Aliases
    'income': 'pages/5_Income_Simulator.py',
    'compare': 'pages/8_Temporal_Comparison.py',
    'data': 'pages/6_Data_Quality.py',
    'sunburst': 'pages/7_Indicator_Insights.py',
    'overview': 'pages/1_Dashboard.py',
    'summary': 'pages/1_Dashboard.py',
}

# Time range shortcuts
def get_time_range(keyword, max_year, min_year):
    """Get time range based on keyword"""
    time_ranges = {
        'recent': (max_year - 4, max_year),
        'last 5 years': (max_year - 4, max_year),
        'last decade': (max_year - 9, max_year),
        'last 10 years': (max_year - 9, max_year),
        '2020s': (2020, max_year),
        '2010s': (2010, 2019),
        '2000s': (2000, 2009),
        'all time': (min_year, max_year),
        'full range': (min_year, max_year),
        'complete': (min_year, max_year),
    }
    
    for key, range_tuple in time_ranges.items():
        if key in keyword.lower():
            return range_tuple
    
    return None

# Category keywords
CATEGORY_KEYWORDS = {
    'poverty': 'Poverty',
    'inequality': 'Income Inequality',
    'income': 'Income & Growth',
    'education': 'Education',
    'employment': 'Employment',
    'infrastructure': 'Infrastructure',
    'health': 'Health',
    'economic': 'Income & Growth',
    'labor': 'Employment',
}

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
    navigate_with_filter('pages/1_Dashboard.py', config)

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
    navigate_with_filter('pages/1_Dashboard.py', config)

def get_gini_indicator():
    """Detect GINI indicator name from actual data"""
    indicators = df['indicator'].unique().tolist()
    
    # Try exact match first
    if 'gini_index' in indicators:
        return 'gini_index'
    
    # Try variations
    for ind in indicators:
        if 'gini' in ind.lower():
            return ind
    
    # Fallback to first indicator
    return indicators[0] if indicators else 'gini_index'

# --------------------------------------------------
# ENHANCED SEARCH PARSER
# --------------------------------------------------

def detect_comparison_command(query, df):
    """Detect country comparison requests like 'compare India Pakistan'"""
    query_lower = query.lower()
    countries = df['country'].unique().tolist()
    
    # Check for comparison keywords
    if any(word in query_lower for word in ['compare', 'vs', 'versus', 'versus']):
        # Extract country names
        found_countries = []
        for country in countries:
            if country.lower() in query_lower:
                found_countries.append(country)
        
        if len(found_countries) >= 2:
            return {
                'type': 'comparison',
                'countries': found_countries,
                'action': 'navigate',
                'page': 'pages/1_Dashboard.py'
            }
    
    return None

def detect_time_range_command(query, max_year, min_year):
    """Detect time range commands like 'recent', 'last decade', '2015-2023'"""
    query_lower = query.lower()
    
    # Check predefined keywords
    time_range = get_time_range(query_lower, max_year, min_year)
    if time_range:
        return time_range
    
    # Detect year ranges like "2015-2023" or "2015 to 2023"
    year_pattern = r'(\d{4})\s*[-–to]+\s*(\d{4})'
    match = re.search(year_pattern, query)
    if match:
        start_year = int(match.group(1))
        end_year = int(match.group(2))
        if min_year <= start_year <= max_year and min_year <= end_year <= max_year:
            return (start_year, end_year)
    
    return None

def detect_category_command(query):
    """Detect category filter commands like 'poverty indicators'"""
    query_lower = query.lower()
    
    for keyword, category in CATEGORY_KEYWORDS.items():
        if keyword in query_lower:
            return category
    
    return None

def detect_help_command(query):
    """Detect help requests like 'what is gini' or 'how to export'"""
    query_lower = query.lower()
    
    help_keywords = ['how to', 'what is', 'explain', 'help', 'tutorial']
    
    if any(keyword in query_lower for keyword in help_keywords):
        return {
            'type': 'help',
            'query': query,
            'page': 'pages/9_Help.py'
        }
    
    return None

def detect_export_command(query):
    """Detect export/download requests"""
    query_lower = query.lower()
    
    export_keywords = ['export', 'download', 'save']
    
    if any(keyword in query_lower for keyword in export_keywords):
        return {
            'type': 'export',
            'message': 'Navigate to Dashboard or Map page, then use the download buttons for PNG, SVG, HTML, or JSON export.'
        }
    
    return None

def detect_ranking_command(query):
    """Detect ranking requests like 'top 5', 'rank by poverty'"""
    query_lower = query.lower()
    
    ranking_keywords = ['top', 'bottom', 'best', 'worst', 'rank', 'highest', 'lowest']
    
    if any(keyword in query_lower for keyword in ranking_keywords):
        return {
            'type': 'ranking',
            'query': query,
            'message': 'Navigate to Dashboard for country rankings and comparisons.'
        }
    
    return None

def parse_smart_search(query, df):
    """
    Master search parser - detects intent and extracts entities
    Returns: dict with 'type' and relevant data
    """
    query_lower = query.lower().strip()
    
    if not query_lower:
        return None
    
    max_year = int(df['year'].max())
    min_year = int(df['year'].min())
    countries = df['country'].unique().tolist()
    indicators = df['indicator'].unique().tolist()
    
    # Priority 1: Help commands
    help_result = detect_help_command(query_lower)
    if help_result:
        return help_result
    
    # Priority 2: Navigation commands
    for keyword, page in COMMAND_KEYWORDS.items():
        if keyword in query_lower:
            return {
                'type': 'navigation',
                'page': page,
                'keyword': keyword
            }
    
    # Priority 3: Comparison commands
    comparison_result = detect_comparison_command(query_lower, df)
    if comparison_result:
        return comparison_result
    
    # Priority 4: Export commands
    export_result = detect_export_command(query_lower)
    if export_result:
        return export_result
    
    # Priority 5: Ranking commands
    ranking_result = detect_ranking_command(query_lower)
    if ranking_result:
        return ranking_result
    
    # Priority 6: Time range detection
    time_range = detect_time_range_command(query_lower, max_year, min_year)
    
    # Priority 7: Category detection
    category = detect_category_command(query_lower)
    
    # Priority 8: Country search
    found_countries = [c for c in countries if c.lower() in query_lower]
    
    # Priority 9: Indicator search
    found_indicators = []
    for ind in indicators:
        # Check if query matches indicator name
        if query_lower in ind.lower():
            found_indicators.append(ind)
        # Also check human-readable name
        try:
            human_name = human_indicator(ind).lower()
            if query_lower in human_name:
                found_indicators.append(ind)
        except:
            pass
    
    # Remove duplicates
    found_indicators = list(set(found_indicators))
    
    # Priority 10: Year search
    year_matches = re.findall(r'\b(19|20)\d{2}\b', query)
    found_years = [int(y) for y in year_matches if min_year <= int(y) <= max_year]
    
    # Build comprehensive result
    return {
        'type': 'multi_search',
        'countries': found_countries,
        'indicators': found_indicators,
        'years': found_years,
        'time_range': time_range,
        'category': category,
        'query': query
    }

# --------------------------------------------------
# SECTION 1: Main Search Interface
# --------------------------------------------------
st.subheader("Search & Command Center")

search_query = st.text_input(
    "Search or enter command...",
    key="main_search_input",
    placeholder="Try: 'compare India Pakistan', 'recent data', 'map', 'poverty trends', '2015-2023'...",
    label_visibility="collapsed"
)

if search_query:
    # Add to history
    if search_query not in st.session_state.search_history:
        st.session_state.search_history.insert(0, search_query)
        st.session_state.search_history = st.session_state.search_history[:10]
    
    # Parse search
    result = parse_smart_search(search_query, df)
    
    if result:
        st.markdown("---")
        st.subheader("Search Results")
        
        # Handle different result types
        if result['type'] == 'navigation':
            st.success(f"Command detected: {result['keyword']}")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"Navigate to: **{result['keyword'].title()}** page")
            with col2:
                if st.button(f"Go to {result['keyword'].title()}", type="primary", key="nav_btn"):
                    st.switch_page(result['page'])
        
        elif result['type'] == 'comparison':
            st.success(f"Comparison request: {' vs '.join(result['countries'])}")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"Will compare **{len(result['countries'])} countries** on Dashboard")
            with col2:
                if st.button("View Comparison", type="primary", key="comp_btn"):
                    max_year = int(df['year'].max())
                    config = {
                        'countries': result['countries'],
                        'indicator': get_gini_indicator(),
                        'year_range': (max_year - 10, max_year),
                        'color_scale': 'Viridis'
                    }
                    navigate_with_filter(result['page'], config)
        
        elif result['type'] == 'help':
            st.info(f"Help request: {result['query']}")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write("The Help page contains comprehensive documentation and guides.")
            with col2:
                if st.button("Open Help", type="primary", key="help_btn"):
                    st.switch_page(result['page'])
        
        elif result['type'] == 'export':
            st.info("Export/Download request")
            st.markdown(f"""
            <div style='background: rgba(139, 92, 246, 0.1); padding: 15px; border-radius: 8px;'>
                <strong>How to export:</strong><br>
                1. Navigate to Dashboard or Map Analysis page<br>
                2. Configure your visualization<br>
                3. Use the download buttons for PNG, SVG, HTML, or JSON export
            </div>
            """, unsafe_allow_html=True)
        
        elif result['type'] == 'ranking':
            st.info(f"Ranking request: {result['query']}")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write("The Dashboard page shows country rankings and performance comparisons.")
            with col2:
                if st.button("View Rankings", type="primary", key="rank_btn"):
                    st.switch_page("pages/1_Dashboard.py")
        
        elif result['type'] == 'multi_search':
            # Display all found entities
            results_found = False
            
            if result['countries']:
                results_found = True
                st.markdown("**Countries found:**")
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(', '.join(result['countries']))
                with col2:
                    if st.button("Analyze Countries", type="primary", key="country_btn"):
                        config = {
                            'countries': result['countries'],
                            'indicator': result['indicators'][0] if result['indicators'] else get_gini_indicator(),
                            'year_range': result['time_range'] or (int(df['year'].max()) - 10, int(df['year'].max())),
                            'color_scale': 'Viridis'
                        }
                        navigate_with_filter("pages/1_Dashboard.py", config)
            
            if result['indicators']:
                results_found = True
                st.markdown("**Indicators found:**")
                col1, col2 = st.columns([3, 1])
                with col1:
                    # Show first 5 indicators
                    display_indicators = result['indicators'][:5]
                    for ind in display_indicators:
                        try:
                            st.write(f"- {human_indicator(ind)}")
                        except:
                            st.write(f"- {ind}")
                    if len(result['indicators']) > 5:
                        st.caption(f"... and {len(result['indicators']) - 5} more")
                with col2:
                    if st.button("Analyze Indicator", type="primary", key="indicator_btn"):
                        config = {
                            'countries': result['countries'] if result['countries'] else df['country'].unique().tolist(),
                            'indicator': result['indicators'][0],
                            'year_range': result['time_range'] or (int(df['year'].max()) - 10, int(df['year'].max())),
                            'color_scale': 'Viridis'
                        }
                        navigate_with_filter("pages/1_Dashboard.py", config)
            
            if result['years']:
                results_found = True
                st.markdown("**Years found:**")
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(', '.join(map(str, result['years'])))
                with col2:
                    if st.button("View on Map", type="primary", key="year_btn"):
                        selected_year = result['years'][0]
                        config = {
                            'countries': df['country'].unique().tolist(),
                            'indicator': get_gini_indicator(),
                            'year_range': (selected_year, selected_year),
                            'color_scale': 'Viridis'
                        }
                        navigate_with_filter("pages/3_Map_Analysis.py", config)
            
            if result['time_range']:
                results_found = True
                st.markdown("**Time range:**")
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"{result['time_range'][0]} to {result['time_range'][1]}")
                with col2:
                    if st.button("Apply Time Filter", type="primary", key="time_btn"):
                        config = {
                            'countries': result['countries'] if result['countries'] else df['country'].unique().tolist(),
                            'indicator': result['indicators'][0] if result['indicators'] else get_gini_indicator(),
                            'year_range': result['time_range'],
                            'color_scale': 'Viridis'
                        }
                        navigate_with_filter("pages/1_Dashboard.py", config)
            
            if result['category']:
                results_found = True
                st.markdown("**Category:**")
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(result['category'])
                with col2:
                    if st.button("View Category", type="primary", key="cat_btn"):
                        # Navigate to dashboard with category filter
                        st.info(f"Category filtering: Select '{result['category']}' indicators on Dashboard")
                        st.switch_page("pages/1_Dashboard.py")
            
            if not results_found:
                st.warning("No results found. Try refining your search.")

st.divider()

# --------------------------------------------------
# SECTION 2: Popular Queries
# --------------------------------------------------
st.subheader("Popular Queries")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Quick Navigation**")
    if st.button("Dashboard", use_container_width=True, key="pop_dashboard"):
        st.switch_page("pages/1_Dashboard.py")
    if st.button("Map Analysis", use_container_width=True, key="pop_map"):
        st.switch_page("pages/3_Map_Analysis.py")
    if st.button("Correlation Explorer", use_container_width=True, key="pop_corr"):
        st.switch_page("pages/4_Correlations.py")

with col2:
    st.markdown("**Data Views**")
    if st.button("Recent Data (Last 5 Years)", use_container_width=True, key="pop_recent"):
        max_year = int(df['year'].max())
        config = {
            'countries': df['country'].unique().tolist(),
            'indicator': get_gini_indicator(),
            'year_range': (max_year - 4, max_year),
            'color_scale': 'Viridis'
        }
        navigate_with_filter("pages/1_Dashboard.py", config)
    
    if st.button("Complete Timeline (2000-2024)", use_container_width=True, key="pop_full"):
        config = {
            'countries': df['country'].unique().tolist(),
            'indicator': get_gini_indicator(),
            'year_range': (int(df['year'].min()), int(df['year'].max())),
            'color_scale': 'Viridis'
        }
        navigate_with_filter("pages/1_Dashboard.py", config)

with col3:
    st.markdown("**Analysis Tools**")
    if st.button("Income Simulator", use_container_width=True, key="pop_sim"):
        st.switch_page("pages/5_Income_Simulator.py")
    if st.button("Data Quality Check", use_container_width=True, key="pop_quality"):
        st.switch_page("pages/6_Data_Quality.py")
    if st.button("Temporal Comparison", use_container_width=True, key="pop_temporal"):
        st.switch_page("pages/8_Temporal_Comparison.py")

st.divider()

# --------------------------------------------------
# SECTION 3: Enhanced Bookmarks
# --------------------------------------------------
st.subheader("Bookmarked Views")

# Helper functions for safe data access
def get_high_inequality_countries(threshold=40):
    """Get countries with average GINI > threshold, with fallback"""
    try:
        gini_indicator = get_gini_indicator()
        gini_data = df[df['indicator'] == gini_indicator]
        
        if gini_data.empty:
            return df['country'].unique().tolist()
        
        avg_gini = gini_data.groupby('country')['value'].mean()
        high_countries = avg_gini[avg_gini > threshold].index.tolist()
        
        if not high_countries:
            high_countries = avg_gini[avg_gini > 35].index.tolist()
            if not high_countries:
                return df['country'].unique().tolist()
        
        return high_countries
    except Exception as e:
        return df['country'].unique().tolist()

def get_low_inequality_countries(threshold=30):
    """Get countries with average GINI < threshold, with fallback"""
    try:
        gini_indicator = get_gini_indicator()
        gini_data = df[df['indicator'] == gini_indicator]
        
        if gini_data.empty:
            return df['country'].unique().tolist()
        
        avg_gini = gini_data.groupby('country')['value'].mean()
        low_countries = avg_gini[avg_gini < threshold].index.tolist()
        
        if not low_countries:
            low_countries = avg_gini[avg_gini < 35].index.tolist()
            if not low_countries:
                return df['country'].unique().tolist()
        
        return low_countries
    except Exception as e:
        return df['country'].unique().tolist()

detected_gini_indicator = get_gini_indicator()
max_year = int(df['year'].max())
min_year = int(df['year'].min())

# Enhanced bookmarks
bookmarks = {
    "All Countries Overview": {
        "description": "Dashboard view with all countries, GINI index, last 10 years",
        "countries": df['country'].unique().tolist(),
        "indicator": detected_gini_indicator,
        "year_range": (max(min_year, max_year - 9), max_year),
        "page": "pages/1_Dashboard.py"
    },
    "High Inequality Focus": {
        "description": "Countries with GINI > 40 (severe inequality)",
        "countries": get_high_inequality_countries(40),
        "indicator": detected_gini_indicator,
        "year_range": (max(min_year, max_year - 9), max_year),
        "page": "pages/1_Dashboard.py"
    },
    "Low Inequality Focus": {
        "description": "Countries with GINI < 30 (more equitable distribution)",
        "countries": get_low_inequality_countries(30),
        "indicator": detected_gini_indicator,
        "year_range": (max(min_year, max_year - 9), max_year),
        "page": "pages/1_Dashboard.py"
    },
    "Recent Analysis (2020-2024)": {
        "description": "Focus on most recent 5 years of data",
        "countries": df['country'].unique().tolist(),
        "indicator": detected_gini_indicator,
        "year_range": (max(2020, min_year), max_year),
        "page": "pages/1_Dashboard.py"
    },
    "Last Decade (2015-2024)": {
        "description": "Ten-year analysis of inequality trends",
        "countries": df['country'].unique().tolist(),
        "indicator": detected_gini_indicator,
        "year_range": (max(2015, min_year), max_year),
        "page": "pages/1_Dashboard.py"
    },
    "Complete Timeline (2000-2024)": {
        "description": "Full 24-year historical analysis",
        "countries": df['country'].unique().tolist(),
        "indicator": detected_gini_indicator,
        "year_range": (min_year, max_year),
        "page": "pages/1_Dashboard.py"
    },
    "Geographic Visualization": {
        "description": "Latest year choropleth map view",
        "countries": df['country'].unique().tolist(),
        "indicator": detected_gini_indicator,
        "year_range": (max_year, max_year),
        "page": "pages/3_Map_Analysis.py"
    },
    "Correlation Analysis": {
        "description": "Explore relationships between inequality and drivers",
        "page": "pages/4_Correlations.py"
    },
    "Indicator Insights (Sunburst)": {
        "description": "Multi-dimensional indicator dominance patterns",
        "countries": df['country'].unique().tolist(),
        "page": "pages/7_Indicator_Insights.py"
    },
    "Temporal Comparison Tool": {
        "description": "Compare different time periods side-by-side",
        "countries": df['country'].unique().tolist(),
        "indicator": detected_gini_indicator,
        "page": "pages/8_Temporal_Comparison.py"
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
        st.caption(f"Filters: {len(bookmark_info['countries'])} countries")

with col_action:
    st.write("")  # Spacing
    st.write("")  # Spacing
    if st.button("Execute Bookmark", use_container_width=True, type="primary", key="execute_bookmark"):
        # Build config if needed
        if 'countries' in bookmark_info:
            # Validate that we have countries
            if not bookmark_info['countries']:
                st.error("No countries match this filter. Please try a different bookmark.")
                st.stop()
            
            config = {
                'countries': bookmark_info['countries'],
                'indicator': bookmark_info.get('indicator', detected_gini_indicator),
                'year_range': bookmark_info.get('year_range', (min_year, max_year)),
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
    st.subheader("Recent Searches")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.caption("Click to search again")
    with col2:
        if st.button("Clear History", key="clear_history"):
            st.session_state.search_history = []
            st.rerun()
    
    # Display history as clickable buttons
    cols = st.columns(5)
    for idx, query in enumerate(st.session_state.search_history[:10]):
        with cols[idx % 5]:
            if st.button(f"{query}", key=f"history_{idx}", use_container_width=True):
                st.session_state.main_search_input = query
                st.rerun()

st.divider()

# --------------------------------------------------
# SECTION 5: Search Tips & Help
# --------------------------------------------------
with st.expander("Search Tips & Command Reference"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Search Capabilities
        
        **By Country:**
        - Type: `Bangladesh`, `India`, `Pakistan`
        - Click "Analyze" to view in dashboard
        
        **By Indicator:**
        - Type: `GINI`, `HDI`, `GDP`, `poverty`
        - Click "Analyze" to view trends
        
        **By Year:**
        - Type: `2020`, `2015`, `2010`
        - Click "View Map" for geographic view
        
        **By Command:**
        - Type: `map`, `dashboard`, `simulator`, `correlation`
        - Instant navigation to pages
        
        **Time Ranges:**
        - `recent` - Last 5 years
        - `last decade` - Last 10 years
        - `2015-2023` - Custom range
        - `all time` - Complete timeline
        """)
    
    with col2:
        st.markdown("""
        ### Advanced Features
        
        **Comparisons:**
        - `compare India Pakistan` - Multi-country analysis
        - `India vs Bangladesh` - Side-by-side comparison
        
        **Categories:**
        - `poverty indicators` - Filter by category
        - `education data` - Category-specific view
        
        **Commands List:**
        - `dashboard` - Main dashboard
        - `map` - Geographic visualization
        - `correlation` - Correlation explorer
        - `simulator` - Income simulator
        - `temporal` - Time comparison
        - `quality` - Data quality check
        - `insights` - Sunburst visualization
        - `help` - Documentation
        
        **Export:**
        - Type `export` or `download` for instructions
        """)

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.divider()
st.markdown("""
<div style='text-align: center; color: #94a3b8; font-size: 0.85rem;'>
    <p><strong>Smart Search & Navigation Hub</strong> | South Asia Inequality Analysis Platform</p>
    <p>Enhanced with natural language commands, time filters, comparisons, and intelligent parsing</p>
</div>
""", unsafe_allow_html=True)

# -----------------
# Navigation
# -----------------
from utils.navigation_ui import bottom_nav_layout
bottom_nav_layout(__file__)