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

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Smart Search",
    page_icon="🔍",
    layout="wide"
)
render_help_button("search")
# Load custom CSS
try:
    with open('assets/dashboard.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Custom CSS for search enhancement
st.markdown("""
<style>
    /* Search box styling */
    .stTextInput > div > div > input {
        font-size: 18px;
        padding: 12px;
        border-radius: 8px;
    }
    
    /* Command result cards */
    .command-card {
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        background-color: rgba(31, 119, 180, 0.1);
        margin: 10px 0;
    }
    
    /* Keyboard shortcut hint */
    .kbd-hint {
        display: inline-block;
        padding: 3px 8px;
        font-size: 12px;
        background-color: #f0f0f0;
        border: 1px solid #ccc;
        border-radius: 4px;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Initialize session state for search history
# --------------------------------------------------
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# --------------------------------------------------
# Main Title
# --------------------------------------------------
st.title("🔍 Smart Search & Navigation Hub")
st.caption("Quick access to data, insights, and navigation — keyboard-friendly!")

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
    st.metric("📍 Countries", df['country'].nunique())
with col2:
    st.metric("📊 Indicators", df['indicator'].nunique())
with col3:
    st.metric("📅 Years", f"{int(df['year'].min())}–{int(df['year'].max())}")
with col4:
    st.metric("🔢 Total Records", f"{len(df):,}")

st.divider()

# --------------------------------------------------
# SECTION 1: Smart Search Command Palette
# --------------------------------------------------
st.subheader("⌨️ Quick Search Command Palette")

# Keyboard shortcut hint
st.markdown("""
<div style='background-color: rgba(100,100,100,0.1); padding: 10px; border-radius: 5px; margin-bottom: 15px;'>
    💡 <b>Tip:</b> Type to search countries, indicators, years, or commands. 
    <span class='kbd-hint'>Ctrl</span> + <span class='kbd-hint'>K</span> in your browser to focus search.
</div>
""", unsafe_allow_html=True)

# Main search input
search_query = st.text_input(
    "🔍 Type your search query",
    placeholder="Try: 'Bangladesh', 'GINI', '2020', 'high inequality', 'export'...",
    key="main_search_input",
    label_visibility="collapsed"
)

# --------------------------------------------------
# Search Processing Function
# --------------------------------------------------
def smart_search(query, dataframe):
    """
    Advanced search across multiple dimensions
    Returns categorized results
    """
    if not query:
        return None
    
    query = query.lower().strip()
    results = {
        'countries': [],
        'indicators': [],
        'years': [],
        'commands': [],
        'filters': [],
        'data_rows': []
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
                'latest_year': int(country_data['year'].max())
            })
    
    # 2. Search Indicators
    matching_indicators = dataframe[
        dataframe['indicator'].str.lower().str.contains(query, na=False)
    ]['indicator'].unique()
    
    if len(matching_indicators) > 0:
        for indicator in matching_indicators:
            ind_data = dataframe[dataframe['indicator'] == indicator]
            results['indicators'].append({
                'name': indicator,
                'human_name': human_indicator(indicator),
                'countries_available': ind_data['country'].nunique(),
                'latest_value': ind_data[ind_data['year'] == ind_data['year'].max()]['value'].mean()
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
        'export': {
            'name': '💾 Export Data',
            'description': 'Download data in CSV, Excel, or JSON format',
            'page': 'Any page → look for download buttons'
        },
        'map': {
            'name': '🗺️ Geographic Map',
            'description': 'View choropleth map analysis',
            'page': 'Navigate to Map Analysis page'
        },
        'correlation': {
            'name': '🔗 Correlation Explorer',
            'description': 'Analyze relationships between indicators',
            'page': 'Navigate to Correlations page'
        },
        'dashboard': {
            'name': '📊 Multi-Dimensional Dashboard',
            'description': 'View comprehensive statistics and trends',
            'page': 'Navigate to Dashboard page'
        },
        'temporal': {
            'name': '📈 Temporal Comparison',
            'description': 'Compare data across time periods',
            'page': 'Navigate to Temporal Compare page'
        },
        'quality': {
            'name': '✅ Data Quality',
            'description': 'Check data completeness and reliability',
            'page': 'Navigate to Data Quality page'
        },
        'help': {
            'name': '❓ Help & Documentation',
            'description': 'User guide and tutorials',
            'page': 'Navigate to Help page'
        }
    }
    
    for keyword, cmd_info in command_keywords.items():
        if keyword in query:
            results['commands'].append(cmd_info)
    
    # 5. Smart Filters (natural language patterns)
    if 'high' in query and 'inequality' in query:
        results['filters'].append({
            'name': '🔴 High Inequality Filter',
            'description': 'Countries with GINI > 40',
            'query': "GINI index > 40"
        })
    
    if 'low' in query and 'inequality' in query:
        results['filters'].append({
            'name': '🟢 Low Inequality Filter',
            'description': 'Countries with GINI < 30',
            'query': "GINI index < 30"
        })
    
    if 'improving' in query or 'better' in query:
        results['filters'].append({
            'name': '📈 Improving Trends',
            'description': 'Countries showing positive development',
            'query': "Trends with decreasing GINI or increasing HDI"
        })
    
    if 'declining' in query or 'worse' in query:
        results['filters'].append({
            'name': '📉 Declining Trends',
            'description': 'Countries showing concerning patterns',
            'query': "Trends with increasing inequality"
        })
    
    # 6. Direct Data Search (sample matching rows)
    if len(query) > 3:  # Only for substantial queries
        mask = (
            dataframe['country'].str.lower().str.contains(query, na=False) |
            dataframe['indicator'].str.lower().str.contains(query, na=False)
        )
        matching_rows = dataframe[mask].head(10)
        if not matching_rows.empty:
            results['data_rows'] = matching_rows.to_dict('records')
    
    return results

# --------------------------------------------------
# Display Search Results
# --------------------------------------------------
if search_query:
    # Add to history
    if search_query not in st.session_state.search_history:
        st.session_state.search_history.insert(0, search_query)
        st.session_state.search_history = st.session_state.search_history[:10]  # Keep last 10
    
    with st.spinner("🔍 Searching..."):
        results = smart_search(search_query, df)
    
    if results:
        # Count total results
        total_results = (
            len(results['countries']) + 
            len(results['indicators']) + 
            len(results['years']) + 
            len(results['commands']) +
            len(results['filters'])
        )
        
        if total_results == 0 and len(results['data_rows']) == 0:
            st.warning(f"No results found for '{search_query}'. Try different keywords.")
        else:
            st.success(f"✅ Found {total_results} matches for '{search_query}'")
            
            # Display results in tabs
            tabs = []
            tab_contents = []
            
            if results['countries']:
                tabs.append(f"🌍 Countries ({len(results['countries'])})")
                tab_contents.append(('countries', results['countries']))
            
            if results['indicators']:
                tabs.append(f"📊 Indicators ({len(results['indicators'])})")
                tab_contents.append(('indicators', results['indicators']))
            
            if results['years']:
                tabs.append(f"📅 Years ({len(results['years'])})")
                tab_contents.append(('years', results['years']))
            
            if results['commands']:
                tabs.append(f"⚡ Commands ({len(results['commands'])})")
                tab_contents.append(('commands', results['commands']))
            
            if results['filters']:
                tabs.append(f"🎯 Smart Filters ({len(results['filters'])})")
                tab_contents.append(('filters', results['filters']))
            
            if results['data_rows']:
                tabs.append(f"📋 Data ({len(results['data_rows'])})")
                tab_contents.append(('data_rows', results['data_rows']))
            
            # Create tabs
            if tabs:
                tab_objects = st.tabs(tabs)
                
                for tab_obj, (result_type, items) in zip(tab_objects, tab_contents):
                    with tab_obj:
                        if result_type == 'countries':
                            for country in items:
                                st.markdown(f"""
                                <div class='command-card'>
                                    <h4>🌍 {country['name']}</h4>
                                    <p>
                                        <b>Indicators Available:</b> {country['indicators_available']}<br>
                                        <b>Years Covered:</b> {country['years_covered']}<br>
                                        <b>Latest Data:</b> {country['latest_year']}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Quick action button
                                if st.button(f"View {country['name']} Data", key=f"country_{country['name']}"):
                                    st.info(f"💡 **Next step:** Go to Dashboard and filter by {country['name']}")
                        
                        elif result_type == 'indicators':
                            for indicator in items:
                                st.markdown(f"""
                                <div class='command-card'>
                                    <h4>📊 {indicator['human_name']}</h4>
                                    <p>
                                        <b>Technical Name:</b> {indicator['name']}<br>
                                        <b>Countries Available:</b> {indicator['countries_available']}<br>
                                        <b>Latest Regional Avg:</b> {format_value(indicator['latest_value'])}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if st.button(f"Explore {indicator['human_name']}", key=f"ind_{indicator['name'][:20]}"):
                                    st.info(f"💡 **Next step:** Go to Dashboard and select '{indicator['human_name']}'")
                        
                        elif result_type == 'years':
                            for year_info in items:
                                st.markdown(f"""
                                <div class='command-card'>
                                    <h4>📅 Year {year_info['year']}</h4>
                                    <p>
                                        <b>Data Records:</b> {year_info['records']}<br>
                                        <b>Countries:</b> {year_info['countries']}<br>
                                        <b>Indicators:</b> {year_info['indicators']}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if st.button(f"View {year_info['year']} Data", key=f"year_{year_info['year']}"):
                                    st.info(f"💡 **Next step:** Go to Map Analysis and select year {year_info['year']}")
                        
                        elif result_type == 'commands':
                            for cmd in items:
                                st.markdown(f"""
                                <div class='command-card'>
                                    <h4>{cmd['name']}</h4>
                                    <p>
                                        <b>Description:</b> {cmd['description']}<br>
                                        <b>Location:</b> {cmd['page']}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        elif result_type == 'filters':
                            for filter_info in items:
                                st.markdown(f"""
                                <div class='command-card'>
                                    <h4>{filter_info['name']}</h4>
                                    <p>
                                        <b>Description:</b> {filter_info['description']}<br>
                                        <b>Query:</b> <code>{filter_info['query']}</code>
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if st.button(f"Apply Filter", key=f"filter_{filter_info['name'][:20]}"):
                                    st.info("💡 **Next step:** This filter can be applied on Dashboard or Map Analysis pages")
                        
                        elif result_type == 'data_rows':
                            st.dataframe(
                                pd.DataFrame(items)[['country', 'year', 'indicator', 'value']],
                                use_container_width=True,
                                hide_index=True
                            )

st.divider()

# --------------------------------------------------
# SECTION 2: Quick Action Shortcuts
# --------------------------------------------------
st.subheader("⚡ Quick Action Shortcuts")
st.caption("One-click access to common tasks")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📊 Latest Dashboard", use_container_width=True):
        st.info("💡 Navigate to **Dashboard** page from sidebar")
        
with col2:
    if st.button("🗺️ Regional Map", use_container_width=True):
        st.info("💡 Navigate to **Map Analysis** page from sidebar")

with col3:
    if st.button("🔗 Correlations", use_container_width=True):
        st.info("💡 Navigate to **Correlations** page from sidebar")

with col4:
    if st.button("📈 Time Trends", use_container_width=True):
        st.info("💡 Navigate to **Temporal Compare** page from sidebar")

st.divider()

# --------------------------------------------------
# SECTION 3: Bookmarked Views / Saved Queries
# --------------------------------------------------
st.subheader("⭐ Quick Access Bookmarks")
st.caption("Pre-configured views for common analysis needs")

bookmarks = {
    "🔴 High Inequality Countries (GINI > 40)": {
        "description": "Countries with severe income inequality",
        "filter": "GINI index > 40",
        "page": "Dashboard or Map Analysis"
    },
    "🟢 Low Inequality Countries (GINI < 30)": {
        "description": "Countries with more equitable income distribution",
        "filter": "GINI index < 30",
        "page": "Dashboard or Map Analysis"
    },
    "📈 Improving Trends (2010-2020)": {
        "description": "Countries showing positive development",
        "filter": "Compare 2010 vs 2020",
        "page": "Temporal Comparison"
    },
    "💰 GDP vs Inequality Correlation": {
        "description": "Relationship between economic growth and inequality",
        "filter": "GDP_Total vs GINI",
        "page": "Correlations"
    },
    "🎓 Education Impact Analysis": {
        "description": "How education relates to inequality",
        "filter": "education_index vs GINI",
        "page": "Correlations"
    },
    "🌍 Regional Comparison (All Countries)": {
        "description": "Compare all South Asian countries side by side",
        "filter": "All countries, latest year",
        "page": "Dashboard or Sunburst"
    }
}

selected_bookmark = st.selectbox(
    "Choose a bookmarked view:",
    list(bookmarks.keys())
)

bookmark_info = bookmarks[selected_bookmark]

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"""
    **Description:** {bookmark_info['description']}  
    **Filter:** `{bookmark_info['filter']}`  
    **Recommended Page:** {bookmark_info['page']}
    """)

with col2:
    if st.button("Go to View →", use_container_width=True):
        st.success(f"✅ Navigate to **{bookmark_info['page']}** and apply the filter")

st.divider()

# --------------------------------------------------
# SECTION 4: Search History
# --------------------------------------------------
if st.session_state.search_history:
    st.subheader("🕐 Recent Searches")
    
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
with st.expander("💡 Search Tips & Examples"):
    st.markdown("""
    ### How to Use Smart Search
    
    **1. Search by Country:**
    - Type: `Bangladesh`, `India`, `Pakistan`, etc.
    - Get: Country statistics, available indicators, data coverage
    
    **2. Search by Indicator:**
    - Type: `GINI`, `HDI`, `GDP`, `education`, `poverty`
    - Get: Indicator details, countries covered, latest values
    
    **3. Search by Year:**
    - Type: `2020`, `2015`, `2010`
    - Get: All data available for that year
    
    **4. Search by Command:**
    - Type: `export`, `map`, `correlation`, `dashboard`
    - Get: Navigation shortcuts and page information
    
    **5. Natural Language Filters:**
    - Type: `high inequality`, `improving trends`, `declining`
    - Get: Smart filter suggestions and relevant data
    
    ### Keyboard Shortcuts
    - **Ctrl+K** or **Cmd+K**: Focus search box (in browser)
    - **Tab**: Navigate between buttons
    - **Enter**: Execute search or action
    
    ### Pro Tips
    - ✅ Combine terms: `Bangladesh 2020` for specific data
    - ✅ Use partial matches: `gin` finds GINI-related indicators
    - ✅ Check history: Re-run previous searches quickly
    - ✅ Use bookmarks: Fastest access to common views
    """)

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.divider()
st.caption("🔍 Smart Search & Navigation Hub | South Asia Inequality Analysis Platform")
st.caption("💡 Tip: Use the sidebar to navigate between analysis pages after finding your data")