import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
from pathlib import Path
import numpy as np
from datetime import datetime
import io

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.loaders import load_inequality_data
from utils.utils import human_indicator, format_value
from utils.exports import export_data_menu
from utils.help_system import render_help_button
from utils.sidebar import apply_all_styles
from utils.api_loader import get_api_loader
from utils.imf_api_loader import get_imf_loader
from utils.un_data_loader import get_un_loader


st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize API loaders after page config
api_loader = get_api_loader()
imf_loader = get_imf_loader()
un_loader = get_un_loader()

render_help_button("dashboard")
apply_all_styles()
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* SIDEBAR: 200px width */
    /* SIDEBAR: Default width */
    [data-testid="stSidebar"] {
        /* Allow natural width */
    }
    
    /* Main background - Dark navy matching the screenshot */
    .main {
        background: linear-gradient(135deg, #3d2352 0%, #2a1a47 50%, #1a1230 100%);
        background-attachment: fixed;
    }
    
    /* Block container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 100%;
        background: transparent;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* header {visibility: hidden;} */
    
    /* METRIC CARDS: Much more purple glow theme */
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
    
    /* HEADERS: White with glow */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
        text-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
    }
    
    /* SELECTBOX: More purple theme */
    div[data-baseweb="select"] {
        background: rgba(139, 92, 246, 0.15) !important;
        border: 1px solid rgba(139, 92, 246, 0.4) !important;
        border-radius: 8px !important;
    }
    
    div[data-baseweb="select"]:hover {
        border-color: rgba(139, 92, 246, 0.6) !important;
        box-shadow: 0 0 15px rgba(139, 92, 246, 0.2) !important;
    }
    
    /* TEXT COLORS */
    p, span, div {
        color: #e2e8f0;
    }
    
    /* SCROLLBAR: Purple theme */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(30, 25, 56, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(139, 92, 246, 0.5);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(139, 92, 246, 0.8);
    }
    
    /* CUSTOM CARD STYLES: Much more purple glow */
    .stat-card {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(99, 102, 241, 0.1) 100%);
        border: 1px solid rgba(139, 92, 246, 0.4);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.25);
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }
    
    .stat-card:hover {
        border-color: rgba(139, 92, 246, 0.6);
        box-shadow: 0 4px 30px rgba(139, 92, 246, 0.35);
    }
    
    /* SECTION HEADER: Purple accent */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #ffffff;
        margin: 30px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid rgba(139, 92, 246, 0.3);
        text-shadow: 0 0 15px rgba(139, 92, 246, 0.3);
    }
    
    /* BREADCRUMB: Purple links */
    .breadcrumb {
        padding: 0.5rem 0;
        margin-bottom: 1rem;
        font-size: 0.875rem;
    }
    
    .breadcrumb a {
        color: #8b5cf6;
        text-decoration: none;
        transition: color 0.2s;
    }
    
    .breadcrumb a:hover {
        color: #a78bfa;
        text-shadow: 0 0 10px rgba(139, 92, 246, 0.5);
    }
    
    /* BUTTONS: More purple theme */
    .stButton > button {
        background: rgba(139, 92, 246, 0.25);
        border: 1px solid rgba(139, 92, 246, 0.4);
        color: #ffffff;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: rgba(139, 92, 246, 0.45);
        border-color: #8b5cf6;
        box-shadow: 0 0 25px rgba(139, 92, 246, 0.5);
    }
    
    /* DIVIDER: Purple */
    hr {
        border-color: rgba(139, 92, 246, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# INLINE EXPORT FUNCTION FOR PLOTS 
# ═══════════════════════════════════════════════════════════════════

def ensure_public_analysis(df):
    """Create default config if none exists"""
    if "analysis_config" not in st.session_state or st.session_state.analysis_config is None:
        countries = sorted(df["country"].dropna().unique().tolist())
        indicators = sorted(df["indicator"].dropna().unique().tolist())
        min_year = int(df["year"].min())
        max_year = int(df["year"].max())
        default_indicator = "gini_index" if "gini_index" in indicators else (indicators[0] if indicators else None)
        
        st.session_state.analysis_config = {
            "countries": countries,
            "indicator": default_indicator,
            "year_range": (max(min_year, max_year - 20), max_year),
            "color_scale": "Viridis",
        }

# Load data
df = load_inequality_data()

if df.empty:
    st.error("⚠️ No data available")
    st.stop()

ensure_public_analysis(df)
config = st.session_state.analysis_config

# Filter data
filtered_df = df[
    (df['country'].isin(config['countries'])) &
    (df['year'] >= config['year_range'][0]) &
    (df['year'] <= config['year_range'][1]) &
    (df['indicator'] == config['indicator'])
].copy()

if filtered_df.empty:
    st.warning("⚠️ No data available for selected filters")
    st.stop()

# FIX: Remove duplicates and scale values
# Remove duplicate country-year rows by averaging
filtered_df = filtered_df.groupby(['country', 'year', 'indicator']).agg({
    'value': 'mean'
}).reset_index()

# Auto-scaling logic removed to preserve data integrity


# ═══════════════════════════════════════════════════════════════════
# API ENRICHMENT SECTION
# ═══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("---")
    st.markdown("### 🌐 Live Data Enrichment")
    use_api_enrichment = st.toggle("Enable API Data Overlay", value=False,
                                    help="Overlay live World Bank API data on plots for comparison")
    
    if use_api_enrichment:
        st.success("✓ API Active")
        
        # Select which metric to fetch live
        api_metric = st.selectbox(
            "Live Metric",
            ["Gini Index", "GDP per Capita", "Poverty Rate"],
            help="Choose which live indicator to overlay"
        )
        
        # Mapping to World Bank codes
        metric_mapping = {
            "Gini Index": "SI.POV.GINI",
            "GDP per Capita": "NY.GDP.PCAP.CD",
            "Poverty Rate": "SI.POV.NAHC"
        }
        
        api_indicator_code = metric_mapping[api_metric]
        
        # Show live status
        with st.spinner("Fetching live data..."):
            try:
                # Get latest year's data for all countries
                latest_year_data = []
                for country in config['countries']:
                    api_data = api_loader.fetch_indicator(
                        api_indicator_code,
                        countries=country,
                        date_range=f"{config['year_range'][1]-2}:{config['year_range'][1]}"
                    )
                    if not api_data.empty and 'date' in api_data.columns:
                        latest_api_year = api_data['date'].max()
                        latest_year_data.append((country, latest_api_year))
                
                if latest_year_data:
                    st.info(f"📅 Latest API: {max([y for _, y in latest_year_data])}")
                    
                    # Check if API has newer data than local
                    api_max_year = max([y for _, y in latest_year_data])
                    local_max_year = int(filtered_df['year'].max())
                    
                    if api_max_year > local_max_year:
                        years_behind = api_max_year - local_max_year
                        st.warning(f"⚠️ Local data is {years_behind} year(s) behind API")
                    else:
                        st.success("✓ Data is current")
                        
            except Exception as e:
                st.error(f"API Error: {str(e)[:40]}...")
        
        # Exchange rates info
        rates = api_loader.get_exchange_rates()
        if rates:
            st.caption("**Live FX Rates:**")
            st.caption(f"🇧🇩 {rates.get('BDT', 'N/A')} | 🇮🇳 {rates.get('INR', 'N/A')}")
    else:
        st.info("Enable to overlay live World Bank data")
    
    # Economic APIs Section
    st.markdown("---")
    st.markdown("### 📈 Economic Forecasts & Social Indicators")
    
    use_economic_apis = st.toggle("Enable Economic APIs", value=False,
                                   help="Add IMF forecasts and UN social indicators")
    
    if use_economic_apis:
        st.success("✓ Economic APIs Active")
        
        # IMF Forecasts
        use_imf = st.checkbox("IMF Forecasts", value=True, help="GDP growth and inflation projections")
        
        # UN Indicators
        use_un = st.checkbox("UN Social Indicators", value=True, help="HDI, Gender Inequality, Education")
        
        if use_imf:
            st.caption("📊 GDP Growth & Inflation")
        if use_un:
            st.caption("🌍 HDI & Social Metrics")
    else:
        st.info("Enable for economic forecasts and social data")

# Store API enrichment state for use in visualizations
if 'api_enrichment' not in st.session_state:
    st.session_state.api_enrichment = {}

st.session_state.api_enrichment['enabled'] = use_api_enrichment
if use_api_enrichment:
    st.session_state.api_enrichment['metric'] = api_metric
    st.session_state.api_enrichment['code'] = api_indicator_code

# Store economic APIs state
if 'economic_apis' not in st.session_state:
    st.session_state.economic_apis = {}

st.session_state.economic_apis['enabled'] = use_economic_apis
if use_economic_apis:
    st.session_state.economic_apis['use_imf'] = use_imf
    st.session_state.economic_apis['use_un'] = use_un


# ═══════════════════════════════════════════════════════════════════
# REQUIREMENT #6: BREADCRUMB NAVIGATION (NO BACK BUTTON)
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<div class="breadcrumb">
    <a href="/">Home</a> 
    <span style="color: #64748b;"> / </span>
    <span style="color: #e2e8f0; font-weight: 600;">Dashboard</span>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# HEADER SECTION
# ═══════════════════════════════════════════════════════════════════

st.markdown(f"""
<div style="margin-bottom: 1.5rem;">
    <h1 style="font-size: 2rem; margin: 0; color: #ffffff; font-weight: 600;">
        {human_indicator(config['indicator'])}
    </h1>
    <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 0.5rem;">
        {config['year_range'][0]} - {config['year_range'][1]} • {len(config['countries'])} Countries
    </p>
</div>
""", unsafe_allow_html=True)



# ═══════════════════════════════════════════════════════════════════
# KEY METRICS ROW 
# ═══════════════════════════════════════════════════════════════════

latest_year = int(filtered_df['year'].max())
latest_data = filtered_df[filtered_df['year'] == latest_year].groupby('country').agg({
    'value': 'mean',
    'year': 'first',
    'indicator': 'first'
}).reset_index()
prev_year = latest_year - 1
prev_data = filtered_df[filtered_df['year'] == prev_year]

regional_avg = latest_data['value'].mean()
if not prev_data.empty:
    prev_avg = prev_data['value'].mean()
    yoy_change = regional_avg - prev_avg
    yoy_pct = (yoy_change / prev_avg * 100) if prev_avg != 0 else 0
else:
    yoy_change = 0
    yoy_pct = 0

# ═══════════════════════════════════════════════════════════════════
# SMART BEST/WORST DETECTION

#  SMART INDICATOR TYPE DETECTION
indicator_name = config['indicator'].lower()
negative_terms = [
    # Current - Core inequality & poverty
    'gini', 'inequality', 'poverty', 'disparity', 'gap', 
    'unemployment', 'mortality', 'malnutrition', 'deficit',
    
    # Economic/Financial (negative)
    'debt', 'inflation', 
    
    # Labor (negative)
    'vulnerable', 'child labor', 'contributing family',
    
    # Health/Environment (negative)
    'underweight', 'hiv', 'pollution', 'pm2.5',
    
    # Social/Governance (negative)
    'dependency', 'informal payment', 'out-of-school',
    
    # Time-based bureaucracy (negative - longer = worse)
    'time required', 'time to',

    # Concentration metrics (negative - higher = worse)
    'share held by top', 'concentration', 'top 1% income', 'top 10% income'
]
is_negative_indicator = any(term in indicator_name for term in negative_terms)
is_positive_indicator = not is_negative_indicator

# Detect single-country scenario
num_countries = latest_data['country'].nunique()
is_single_country = num_countries == 1

if is_single_country:
    # Single country view - show the country but no best/worst comparison
    single_country_name = latest_data['country'].iloc[0] if not latest_data.empty else "N/A"
    single_country_value = latest_data['value'].iloc[0] if not latest_data.empty else 0
    best_country = single_country_name
    worst_country = "N/A"  # No comparison possible
    best_value = single_country_value
    worst_value = 0
elif is_positive_indicator:
    # For INCOME: HIGHER = BETTER
    best_country = latest_data.loc[latest_data['value'].idxmax(), 'country'] if not latest_data.empty else "N/A"
    worst_country = latest_data.loc[latest_data['value'].idxmin(), 'country'] if not latest_data.empty else "N/A"
    best_value = latest_data['value'].max() if not latest_data.empty else 0
    worst_value = latest_data['value'].min() if not latest_data.empty else 0
else:
    # For INEQUALITY: LOWER = BETTER
    best_country = latest_data.loc[latest_data['value'].idxmin(), 'country'] if not latest_data.empty else "N/A"
    worst_country = latest_data.loc[latest_data['value'].idxmax(), 'country'] if not latest_data.empty else "N/A"
    best_value = latest_data['value'].min() if not latest_data.empty else 0
    worst_value = latest_data['value'].max() if not latest_data.empty else 0 

# Calculate data coverage
data_coverage = (filtered_df.notna().sum()['value'] / len(filtered_df) * 100)

# ✅ FIX #4: METRIC CARDS WITH STORYTELLING CONTEXT
col1, col2, col3, col4, col5= st.columns(5)

with col1:
    delta_symbol = "↓" if yoy_pct < 0 else "↑"
    metric_label = "Current Value" if is_single_country else "Regional Average"
    st.metric(
        label=metric_label,
        value=f"{regional_avg:.1f}",
        delta=f"{delta_symbol} {abs(yoy_pct):.1f}%"
    )
    # Context text
    if is_single_country:
        context = f"{best_country} latest data"
    elif is_positive_indicator:
        if regional_avg > 70:
            context = "Strong regional performance"
        elif regional_avg > 40:
            context = "Moderate regional performance"
        else:
            context = "Low regional performance"
    else:
        if regional_avg < 30:
            context = "Low regional inequality"
        elif regional_avg < 40:
            context = "Moderate regional inequality"
        else:
            context = "High regional inequality"
    st.markdown(f'<p class="metric-context">{context}</p>', unsafe_allow_html=True)

with col2:
    if is_single_country:
        st.metric(
            label="Selected Country",
            value=best_country,
            delta=f"{best_value:.1f}"
        )
        context = "Single country analysis"
    else:
        st.metric(
            label="Best Performer",
            value=best_country,
            delta=f"{best_value:.1f}"
        )
        # Context text
        if is_positive_indicator:
            context = "Highest value achieved"
        else:
            context = "Most equitable distribution"
    st.markdown(f'<p class="metric-context">{context}</p>', unsafe_allow_html=True)

with col3:
    if is_single_country:
        st.metric(
            label="Comparison",
            value="N/A",
            delta="Single country view"
        )
        context = "Add more countries to compare"
    else:
        st.metric(
            label="Needs Attention",
            value=worst_country,
            delta=f"{worst_value:.1f}",
            delta_color="inverse"
        )
        # Context text
        if is_positive_indicator:
            context = "Requires improvement focus"
        else:
            context = "Highest inequality gap"
    st.markdown(f'<p class="metric-context">{context}</p>', unsafe_allow_html=True)

with col4:
    st.metric(
        label="Data Coverage",
        value=f"{data_coverage:.0f}%",
        delta=f"↑ {int(data_coverage - 50)} points" if data_coverage > 50 else f"↓ {int(50 - data_coverage)} points"
    )
    # Context text
    if data_coverage >= 90:
        context = "Excellent data availability"
    elif data_coverage >= 70:
        context = "Good data availability"
    else:
        context = "Limited data availability"
    st.markdown(f'<p class="metric-context">{context}</p>', unsafe_allow_html=True)

with col5:
    st.metric(
        label="Data Range",
        value=f"{config['year_range'][1] - config['year_range'][0] + 1} Years",
        delta=f"{config['year_range'][0]} - {config['year_range'][1]}",
        delta_color="off"
    )
    # Context text
    years_span = config['year_range'][1] - config['year_range'][0] + 1
    context = f"{years_span}-year analysis period"
    st.markdown(f'<p class="metric-context">{context}</p>', unsafe_allow_html=True)
    
    


# ═══════════════════════════════════════════════════════════════════
# API-DRIVEN INSIGHTS (APPEARS WHEN API ENRICHMENT IS ENABLED)
# ═══════════════════════════════════════════════════════════════════

if use_api_enrichment:
    st.markdown("---")
    st.markdown("### 🤖 Live API-Driven Insights")
    
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(16, 185, 129, 0.1)); 
                    padding: 20px; border-radius: 12px; border-left: 4px solid #3b82f6;">
            <h4 style="color: #ffffff; margin-top: 0;">📊 Real-Time Data Status</h4>
        """, unsafe_allow_html=True)
        
        # Fetch and display live comparison
        try:
            with st.spinner("Analyzing live data..."):
                # Get live data for best performer
                if best_country != "N/A":
                    live_best = api_loader.fetch_indicator(
                        api_indicator_code,
                        countries=best_country,
                        date_range=f"{latest_year-1}:{latest_year}"
                    )
                    
                    if not live_best.empty and 'value' in live_best.columns:
                        live_value = live_best['value'].iloc[-1]
                        local_value = best_value
                        difference = abs(live_value - local_value)
                        
                        if difference < 1.0:
                            st.success(f"✅ {best_country}: Local & API data match (Δ {difference:.2f})")
                        else:
                            st.warning(f"⚠️ {best_country}: {difference:.2f} point discrepancy detected")
                    else:
                        st.info(f"ℹ️ No recent API data for {best_country}")
        except Exception as e:
            st.error(f"Error fetching live comparison: {str(e)[:50]}...")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with insights_col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(239, 68, 68, 0.1)); 
                    padding: 20px; border-radius: 12px; border-left: 4px solid #f59e0b;">
            <h4 style="color: #ffffff; margin-top: 0;">💡 AI-Powered Recommendations</h4>
        """, unsafe_allow_html=True)
        
        # Generate insights based on data
        if yoy_pct < -2:
            st.success(f"🎯 Positive trend: {abs(yoy_pct):.1f}% improvement year-over-year")
        elif yoy_pct > 2:
            st.warning(f"⚠️ Concerning: {yoy_pct:.1f}% increase in inequality")
        else:
            st.info(f"📊 Stable: {abs(yoy_pct):.1f}% change - monitoring recommended")
        
        # Data quality recommendation
        if data_coverage < 70:
            st.warning(f"⚠️ Data coverage at {data_coverage:.0f}% - consider refreshing from API")
        else:
            st.success(f"✅ Good coverage at {data_coverage:.0f}%")
        
        st.markdown("</div>", unsafe_allow_html=True)

#  ═══════════════════════════════════════════════════════════════════
# ECONOMIC FORECASTS & SOCIAL INDICATORS (NEW SECTION)
# ═══════════════════════════════════════════════════════════════════

if use_economic_apis:
    st.markdown("---")
    st.markdown("### 📈 Economic Forecasts & Social Indicators")
    
    forecast_col1, forecast_col2 = st.columns(2)
    
    # IMF Forecasts
    if use_imf:
        with forecast_col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(251, 146, 60, 0.1)); 
                        padding: 20px; border-radius: 12px; border-left: 4px solid #f59e0b;">
                <h4 style="color: #ffffff; margin-top: 0;">📊 Historical GDP Growth (2000-2023)</h4>
            """, unsafe_allow_html=True)
            
            with st.spinner("Fetching historical growth data..."):
                try:
                    # Fetch GDP growth historical data
                    gdp_forecasts = imf_loader.get_gdp_growth(
                        countries=config['countries'],
                        start_year=2000,
                        end_year=2023
                    )
                    
                    if not gdp_forecasts.empty:
                        # Create trend chart
                        fig_forecast = go.Figure()
                        
                        for country in gdp_forecasts['country'].unique():
                            country_data = gdp_forecasts[gdp_forecasts['country'] == country]
                            fig_forecast.add_trace(go.Scatter(
                                x=country_data['year'],
                                y=country_data['value'],
                                mode='lines+markers',
                                name=country,
                                line=dict(width=3),
                                marker=dict(size=8)
                            ))
                        
                        fig_forecast.update_layout(
                            title="GDP Growth Trends (%)",
                            xaxis_title="Year",
                            yaxis_title="GDP Growth Rate (%)",
                            height=350,  # Increased height
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#e2e8f0'),
                            legend=dict(orientation="h", y=-0.3),  # Moved legend lower
                            margin=dict(l=40, r=40, t=40, b=80),  # Increased bottom margin
                            xaxis=dict(
                                dtick=5,  # Show tick every 5 years
                                tickangle=-45,  # Rotate labels to prevent overlap
                                tickfont=dict(size=11)
                            )
                        )
                        
                        st.plotly_chart(fig_forecast, use_container_width=True)
                        
                        # Summary statistics
                        latest_avail_year = gdp_forecasts['year'].max()
                        avg_growth_latest = gdp_forecasts[gdp_forecasts['year'] == latest_avail_year]['value'].mean()
                        if not pd.isna(avg_growth_latest):
                            st.info(f"💡 **Regional Avg ({latest_avail_year}):** {avg_growth_latest:.1f}% GDP Growth")
                    else:
                        st.warning("ℹ️ IMF forecast data unavailable")
                        
                except Exception as e:
                    st.error(f"Error loading IMF data: {str(e)[:50]}...")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # UN Social Indicators
    if use_un:
        with forecast_col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(96, 165, 250, 0.1)); 
                        padding: 20px; border-radius: 12px; border-left: 4px solid #3b82f6;">
                <h4 style="color: #ffffff; margin-top: 0;">🌍 UN Social Indicators (2023)</h4>
            """, unsafe_allow_html=True)
            
            try:
                # Fetch HDI data
                hdi_data = un_loader.get_hdi_data(config['countries'])
                
                if not hdi_data.empty:
                    # Create HDI bar chart
                    hdi_sorted = hdi_data.sort_values('value', ascending=True)
                    
                    fig_hdi = go.Figure(go.Bar(
                        x=hdi_sorted['value'],
                        y=hdi_sorted['country'],
                        orientation='h',
                        marker=dict(
                            color=hdi_sorted['value'],
                            colorscale='Viridis',
                            showscale=False
                        ),
                        text=hdi_sorted['value'].apply(lambda x: f"{x:.3f}"),
                        textposition='outside'
                    ))
                    
                    fig_hdi.update_layout(
                        title="Human Development Index (HDI)",
                        xaxis_title="HDI Value",
                        yaxis_title="",
                        height=300,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#e2e8f0'),
                        margin=dict(l=100, r=80, t=40, b=40),
                        xaxis=dict(range=[0, 1])
                    )
                    
                    st.plotly_chart(fig_hdi, use_container_width=True)
                    
                    # HDI Categories
                    categories = hdi_data['category'].value_counts()
                    category_text = " | ".join([f"{cat}: {count}" for cat, count in categories.items()])
                    st.info(f"📊 **Categories:** {category_text}")
                else:
                    st.warning("ℹ️ UN HDI data unavailable")
                    
            except Exception as e:
                st.error(f"Error loading UN data: {str(e)[:50]}...")
            
            st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# MAIN VISUALIZATION SECTION
# ═══════════════════════════════════════════════════════════════════

st.markdown('<div class="section-header">Inequality Trends Over Time</div>', unsafe_allow_html=True)

# Main area chart -
yearly_data = filtered_df.pivot_table(
    values='value',
    index='year',
    columns='country',
    aggfunc='mean'
).ffill()

fig_area = go.Figure()

# Color palette similar to Google Analytics
colors = ['#3b82f6', '#ec4899', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#6366f1']

for i, country in enumerate(yearly_data.columns):
    fig_area.add_trace(go.Scatter(
        x=yearly_data.index,
        y=yearly_data[country],
        mode='lines',
        name=country,
        line=dict(width=2.5, color=colors[i % len(colors)]),
        fill='tonexty' if i > 0 else 'tozeroy',
        fillcolor=f'rgba({int(colors[i % len(colors)][1:3], 16)}, {int(colors[i % len(colors)][3:5], 16)}, {int(colors[i % len(colors)][5:7], 16)}, 0.5)',
        stackgroup='one',
        hovertemplate='<b>%{fullData.name}</b><br>Year: %{x}<br>Value: %{y:.2f}<extra></extra>'
    ))

# Get indicator name and create shorter version for Y-axis
indicator_name = human_indicator(config["indicator"])
# Create shorter Y-axis label to prevent crowding
y_label_short = indicator_name.split('(')[0].strip() if '(' in indicator_name else indicator_name

# REQUIREMENT #5: PROPER AXIS LABELS (FIXED SPACING)
fig_area.update_layout(
    height=450,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#e2e8f0', size=12),
    xaxis=dict(
        showgrid=True,
        gridcolor='rgba(100, 116, 139, 0.2)',
        title=dict(
            text=f'<b>Year ({config["year_range"][0]}-{config["year_range"][1]})</b>',
            font=dict(size=13, color='#94a3b8')
        ),
        color='#94a3b8'
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='rgba(100, 116, 139, 0.2)',
        title=dict(
            text=f'<b>{y_label_short}<br>(Index Value)</b>',  # Use <br> for line break
            font=dict(size=12, color='#94a3b8')
        ),
        color='#94a3b8'
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', size=11)
    ),
    margin=dict(l=80, r=20, t=130, b=50),  # Increased top margin for tooltip
    hovermode='x unified',
    title=dict(
        text=f'Regional Cumulative Trends: {indicator_name} ({config["year_range"][0]}-{config["year_range"][1]})',
        font=dict(size=15, color='#ffffff'),
        x=0,
        y=0.98
    )
)



# Download options in top-right corner
col_spacer, col_downloads = st.columns([10, 1])
with col_downloads:
    with st.popover("⬇️", help="Download in multiple formats"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # PNG
        try:
            png_bytes = fig_area.to_image(format="png", width=1400, height=1000)
            st.download_button("PNG", png_bytes, f"temporal_trends_{timestamp}.png", "image/png", key="area_png", use_container_width=True)
        except:
            st.button("PNG", disabled=True, key="area_png", use_container_width=True)

        # JPG
        try:
            jpg_bytes = fig_area.to_image(format="jpeg", width=1400, height=1000)
            st.download_button("JPG", jpg_bytes, f"temporal_trends_{timestamp}.jpg", "image/jpeg", key="area_jpg", use_container_width=True)
        except:
            st.button("JPG", disabled=True, key="area_jpg", use_container_width=True)

        # JPEG
        try:
            jpeg_bytes = fig_area.to_image(format="jpeg", width=1400, height=1000)
            st.download_button("JPEG", jpeg_bytes, f"temporal_trends_{timestamp}.jpeg", "image/jpeg", key="area_jpeg", use_container_width=True)
        except:
            st.button("JPEG", disabled=True, key="area_jpeg", use_container_width=True)


st.plotly_chart(fig_area, use_container_width=True, config={
    'displayModeBar': 'hover',
    'displaylogo': False,
    'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'autoScale2d'],
    'toImageButtonOptions': {
        'format': 'png',
        'filename': f'temporal_trends_{config["indicator"]}',
        'height': 1000,
        'width': 1400,
        'scale': 2
    }
})

# STORYTELLING: Inequality Trends
st.markdown(f"""
<div style="background-color: rgba(30, 41, 59, 0.5); padding: 15px; border-radius: 5px; border-left: 3px solid #3b82f6; margin-top: 10px; margin-bottom: 20px;">
    <h5 style="margin: 0 0 8px 0; color: #e0e7ff; font-size: 0.9rem; font-weight: 600;">How to read this chart</h5>
    <p style="margin: 0; color: #cbd5e1; font-size: 0.85rem; line-height: 1.5;">
        This <b>Stacked Area Chart</b> shows the total regional volume of <b>{indicator_name}</b> while displaying individual country contributions. 
        <br>• The <b>height of the stack</b> represents the cumulative sum of all countries combined.
        <br>• The <b>thickness of each colored band</b> shows that specific country's value for that year.
        <br>• <b>Steeper slopes</b> indicate periods of rapid change in the metric.
    </p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# SECONDARY VISUALIZATIONS ROW
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown('<div class="section-header">Country Comparison & Distribution</div>', unsafe_allow_html=True)

col_viz1, col_viz2 = st.columns([1.5, 1], gap="large")  # ✅ FIX: Added gap="large"

with col_viz1:
    # Horizontal bar chart
    country_avg = filtered_df.groupby('country')['value'].mean().sort_values(ascending=True)
    
    # Calculate thresholds
    q1 = country_avg.quantile(0.33)
    q3 = country_avg.quantile(0.67)
    
    # ✅ FIX: Correct color logic
    bar_colors = []
    for val in country_avg.values:
        if is_positive_indicator:
            # For POSITIVE (income, electricity, etc): HIGH = GREEN (good), LOW = RED (bad)
            if val >= q3:
                bar_colors.append('#10b981')  # Green - High value (GOOD)
            elif val >= q1:
                bar_colors.append('#f59e0b')  # Yellow - Moderate
            else:
                bar_colors.append('#ef4444')  # Red - Low value (BAD)
        else:
            # For INEQUALITY: LOW = GREEN (good), HIGH = RED (bad)
            if val <= q1:
                bar_colors.append('#10b981')  # Green - Low inequality (GOOD)
            elif val <= q3:
                bar_colors.append('#f59e0b')  # Yellow - Moderate
            else:
                bar_colors.append('#ef4444')  # Red - High inequality (BAD)
    
    # Format text
    if country_avg.max() > 1000:
        text_values = [f'{v:,.0f}' for v in country_avg.values]
    elif country_avg.max() > 100:
        text_values = [f'{v:.1f}' for v in country_avg.values]
    else:
        text_values = [f'{v:.2f}' for v in country_avg.values]
    
    fig_bars = go.Figure()
    fig_bars.add_trace(go.Bar(
        y=country_avg.index,
        x=country_avg.values,
        orientation='h',
        marker=dict(color=bar_colors, showscale=False, line=dict(width=0)),
        text=text_values,
        textposition='outside',
        textfont=dict(color='#ffffff', size=12, family='Arial'),
        hovertemplate='<b>%{y}</b><br>Value: %{x:.2f}<extra></extra>',
        cliponaxis=False
    ))
    
    fig_bars.update_layout(
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', size=12),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 116, 139, 0.2)',
            title=dict(text=f'<b>{y_label_short}</b>', font=dict(size=13, color='#94a3b8')),
            color='#94a3b8'
        ),
        yaxis=dict(
            showgrid=False,
            title=dict(text='<b>Country</b>', font=dict(size=13, color='#94a3b8')),
            color='#e2e8f0'
        ),
        margin=dict(l=120, r=180, t=40, b=50),
        title=dict(
            text=f'Average by Country ({config["year_range"][0]}-{config["year_range"][1]})',
            font=dict(size=14, color='#ffffff'),
            x=0
        )
    )
    
    # Download options
    col_spacer2, col_downloads2 = st.columns([10, 1])
    with col_downloads2:
        with st.popover("⬇️", help="Download in multiple formats"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # PNG
            try:
                png_bytes = fig_bars.to_image(format="png", width=1400, height=1000)
                st.download_button("PNG", png_bytes, f"country_avg_{timestamp}.png", "image/png", key="bar_png", use_container_width=True)
            except:
                st.button("PNG", disabled=True, key="bar_png", use_container_width=True)

            # JPG
            try:
                jpg_bytes = fig_bars.to_image(format="jpeg", width=1400, height=1000)
                st.download_button("JPG", jpg_bytes, f"country_avg_{timestamp}.jpg", "image/jpeg", key="bar_jpg", use_container_width=True)
            except:
                st.button("JPG", disabled=True, key="bar_jpg", use_container_width=True)

            # JPEG
            try:
                jpeg_bytes = fig_bars.to_image(format="jpeg", width=1400, height=1000)
                st.download_button("JPEG", jpeg_bytes, f"country_avg_{timestamp}.jpeg", "image/jpeg", key="bar_jpeg", use_container_width=True)
            except:
                st.button("JPEG", disabled=True, key="bar_jpeg", use_container_width=True)
    
    st.plotly_chart(fig_bars, use_container_width=True, config={
        'displayModeBar': 'hover',
        'displaylogo': False,
        'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'autoScale2d'],
        'toImageButtonOptions': {'format': 'png', 'filename': f'average_by_country_{config["indicator"]}', 'height': 1000, 'width': 1400, 'scale': 2}
    })
    
    # STORYTELLING: Bar Chart
    st.markdown(f"""
    <div style="background-color: rgba(30, 41, 59, 0.5); padding: 12px; border-radius: 5px; border-left: 3px solid #10b981; margin-top: 15px;">
        <p style="margin: 0; color: #cbd5e1; font-size: 0.85rem; line-height: 1.4;">
            <strong style="color: #e0e7ff;">Insight:</strong> This compares the <b>average performance</b> over the entire {years_span}-year period. 
            It helps identify long-term structural leaders (Green) versus those facing persistent challenges (Red), mostly ignoring short-term fluctuations.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_viz2:
    # Title section - removed spacer to move up
    
    # Prepare data
    country_latest = latest_data[['country', 'value']].copy()
    # Sort based on indicator type: best performers first
    if is_positive_indicator:
        country_latest = country_latest.sort_values('value', ascending=False)
    else:
        country_latest = country_latest.sort_values('value', ascending=True)
    country_latest = country_latest.set_index('country')['value']
    country_latest = country_latest.fillna(country_latest.mean())

    
    # Normalize to 0-100
    max_val = country_latest.max()
    min_val = country_latest.min()
    if max_val != min_val:
        normalized = ((country_latest - min_val) / (max_val - min_val) * 100).values
    else:
        normalized = [50] * len(country_latest)
    
    # ✅ FIX: Correct color assignment
    q1_radial = country_latest.quantile(0.33)
    q3_radial = country_latest.quantile(0.67)
    
    bar_colors_radial = []
    for val in country_latest.values:
        if is_positive_indicator:
            # For POSITIVE: HIGH = GREEN (good), LOW = RED (bad)
            if val >= q3_radial:
                bar_colors_radial.append('#10b981')  # Green - High value (GOOD)
            elif val >= q1_radial:
                bar_colors_radial.append('#f59e0b')  # Yellow - Moderate
            else:
                bar_colors_radial.append('#ef4444')  # Red - Low value (BAD)
        else:
            # For INEQUALITY: LOW = GREEN (good), HIGH = RED (bad)
            if val <= q1_radial:
                bar_colors_radial.append('#10b981')  # Green - Low inequality
            elif val <= q3_radial:
                bar_colors_radial.append('#f59e0b')  # Yellow - Moderate
            else:
                bar_colors_radial.append('#ef4444')  # Red - High inequality
    
    # Create radial chart
    fig_radial = go.Figure()
    
    fig_radial.add_trace(go.Barpolar(
        r=normalized,
        theta=country_latest.index,
        marker=dict(color=bar_colors_radial, line=dict(color='#0a0e27', width=2)),
        hovertemplate='<b>%{theta}</b><br>Actual: %{customdata:.2f}<br>Score: %{r:.0f}/100<extra></extra>',
        customdata=country_latest.values,
        opacity=0.9
    ))
    
    fig_radial.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=True,
                tickfont=dict(size=9, color='#94a3b8'),
                gridcolor='rgba(100, 116, 139, 0.3)',
                tickmode='linear',
                tick0=0,
                dtick=25
            ),
            angularaxis=dict(
                gridcolor='rgba(100, 116, 139, 0.3)',
                linecolor='rgba(100, 116, 139, 0.5)',
                showticklabels=True,
                tickfont=dict(size=10, color='#ffffff', family='Arial Black')
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        height=380,
        margin=dict(l=80, r=80, t=40, b=40),  # Reduced top margin slightly
        showlegend=False,
        title=dict(
            text=f'Latest Year Snapshot ({latest_year})',
            font=dict(size=14, color='#ffffff'),
            x=0.5,
            xanchor='center',
            y=0.98  # Position title higher
        )
    )
    # Download options
    col_spacer3, col_downloads3 = st.columns([5, 1])
    with col_downloads3:
        with st.popover("⬇️", help="Download in multiple formats"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # PNG
            try:
                png_bytes = fig_radial.to_image(format="png", width=1400, height=1400)
                st.download_button("PNG", png_bytes, f"radial_{timestamp}.png", "image/png", key="radial_png", use_container_width=True)
            except:
                st.button("PNG", disabled=True, key="radial_png", use_container_width=True)

            # JPG
            try:
                jpg_bytes = fig_radial.to_image(format="jpeg", width=1400, height=1400)
                st.download_button("JPG", jpg_bytes, f"radial_{timestamp}.jpg", "image/jpeg", key="radial_jpg", use_container_width=True)
            except:
                st.button("JPG", disabled=True, key="radial_jpg", use_container_width=True)

            # JPEG
            try:
                jpeg_bytes = fig_radial.to_image(format="jpeg", width=1400, height=1400)
                st.download_button("JPEG", jpeg_bytes, f"radial_{timestamp}.jpeg", "image/jpeg", key="radial_jpeg", use_container_width=True)
            except:
                st.button("JPEG", disabled=True, key="radial_jpeg", use_container_width=True)
    
    st.plotly_chart(fig_radial, use_container_width=True, config={
        'displayModeBar': 'hover',
        'displaylogo': False,
        'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
        'toImageButtonOptions': {'format': 'png', 'filename': 'radial_comparison', 'height': 1400, 'width': 1400, 'scale': 2}
    })
    
    
# ✅ FIX: DYNAMIC LEGEND (adapts to indicator type)
if is_positive_indicator:
    legend_html = """
    <div style="background: rgba(59, 130, 246, 0.05); padding: 12px; border-radius: 8px; margin-top: 1rem; border-left: 3px solid #3b82f6;">
        <div style="display: flex; justify-content: center; gap: 2rem; align-items: center; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 20px; height: 20px; background: #10b981; border-radius: 4px;"></div>
                <span style="color: #e2e8f0; font-size: 0.9rem;"><strong>Green</strong> = High Performance (Good)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 20px; height: 20px; background: #f59e0b; border-radius: 4px;"></div>
                <span style="color: #e2e8f0; font-size: 0.9rem;"><strong>Yellow</strong> = Moderate Performance</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 20px; height: 20px; background: #ef4444; border-radius: 4px;"></div>
                <span style="color: #e2e8f0; font-size: 0.9rem;"><strong>Red</strong> = Low Performance (Needs Attention)</span>
            </div>
        </div>
    </div>
    """
else:
    legend_html = """
    <div style="background: rgba(59, 130, 246, 0.05); padding: 12px; border-radius: 8px; margin-top: 1rem; border-left: 3px solid #3b82f6;">
        <div style="display: flex; justify-content: center; gap: 2rem; align-items: center; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 20px; height: 20px; background: #10b981; border-radius: 4px;"></div>
                <span style="color: #e2e8f0; font-size: 0.9rem;"><strong>Green</strong> = Low Inequality (Good)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 20px; height: 20px; background: #f59e0b; border-radius: 4px;"></div>
                <span style="color: #e2e8f0; font-size: 0.9rem;"><strong>Yellow</strong> = Moderate Inequality</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 20px; height: 20px; background: #ef4444; border-radius: 4px;"></div>
                <span style="color: #e2e8f0; font-size: 0.9rem;"><strong>Red</strong> = High Inequality (Needs Attention)</span>
            </div>
        </div>
    </div>
    """

st.markdown(legend_html, unsafe_allow_html=True)

# HEATMAP 

# ═══════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown('<div class="section-header" style="font-size: 1.5rem;">Country Correlation Analysis</div>', unsafe_allow_html=True)

st.markdown("""
<div style="background: rgba(59, 130, 246, 0.05); padding: 15px; border-radius: 8px; border-left: 3px solid #3b82f6; margin-bottom: 20px;">
    <p style="color: #8b98a5; font-size: 0.9rem; margin: 0;">
        <b style="color: #e2e8f0;">Correlation Matrix:</b> Shows how strongly inequality patterns are related between countries. 
        Values range from -1 (opposite trends) to +1 (similar trends). Warmer colors indicate stronger positive correlations.
    </p>
</div>
""", unsafe_allow_html=True)

# ✅ FIX #1 & #5: SMART CORRELATION CALCULATION WITH DATA OVERLAP CHECKING
country_trends = filtered_df.pivot_table(values='value', index='year', columns='country')

# Check data quality for correlation analysis
total_years = len(country_trends)
min_required_years = max(10, int(total_years * 0.5))  # At least 10 years or 50% of data

# Calculate data availability for each country
data_availability = {}
for country in country_trends.columns:
    non_null_count = country_trends[country].notna().sum()
    data_availability[country] = non_null_count

# Check if we have sufficient overlapping data
sufficient_data = all(count >= min_required_years for count in data_availability.values())

# Calculate pairwise overlaps
pairwise_overlaps = {}
for i, country1 in enumerate(country_trends.columns):
    for j, country2 in enumerate(country_trends.columns):
        if i < j:
            # Count years where both countries have data
            overlap = (country_trends[country1].notna() & country_trends[country2].notna()).sum()
            pairwise_overlaps[(country1, country2)] = overlap

# Calculate average pairwise overlap
avg_overlap = np.mean(list(pairwise_overlaps.values())) if pairwise_overlaps else 0
min_overlap = min(pairwise_overlaps.values()) if pairwise_overlaps else 0

# Decide if we can show correlation
show_correlation = sufficient_data and avg_overlap >= min_required_years

if show_correlation:
    # Calculate correlation matrix normally
    correlation_matrix = country_trends.corr()
    
    # Replace NaN correlations with 0 for countries with insufficient overlap
    for (country1, country2), overlap in pairwise_overlaps.items():
        if overlap < min_required_years:
            i = list(correlation_matrix.index).index(country1)
            j = list(correlation_matrix.columns).index(country2)
            correlation_matrix.iloc[i, j] = np.nan
            correlation_matrix.iloc[j, i] = np.nan
else:
    correlation_matrix = None

# ✅ FIX #3: CONDITIONAL HEATMAP DISPLAY
if show_correlation and correlation_matrix is not None:
    # Show data quality information
    #  CONTROLS - Only color scheme selector
    # ═══════════════════════════════════════════════════════════════════
    
    color_scheme = st.selectbox(
        "Color Scheme",
        ["RdBu_r", "RdYlGn", "Viridis", "Spectral", "PiYG"],
        help="Color palette for the heatmap (RdBu_r is recommended for academic papers)"
    )
    
    # ═══════════════════════════════════════════════════════════════════
    # CREATE HEATMAP - ALWAYS WITH VALUES
    # ═══════════════════════════════════════════════════════════════════
    
    fig_corr = go.Figure()
    
    # Add heatmap trace - ALWAYS showing values
    fig_corr.add_trace(go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.index,
        colorscale=color_scheme,
        zmid=0,  # Center colorscale at 0
        zmin=-1,
        zmax=1,
        text=correlation_matrix.values.round(3),  # Always show values
        texttemplate='%{text}',  # Always display text
        textfont=dict(size=11, color='#000000'),
        hovertemplate='<b>%{y} ↔ %{x}</b><br>Correlation: %{z:.3f}<extra></extra>',
        colorbar=dict(
            title='Correlation',
            tickmode='linear',
            tick0=-1,
            dtick=0.25,
            len=0.7,
            thickness=15,
            tickfont=dict(size=10)
        )
    ))
    
    # Update layout
    fig_corr.update_layout(
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', size=11),
        xaxis=dict(
            side='bottom',
            tickangle=-45,
            tickfont=dict(size=11),
            showgrid=False
        ),
        yaxis=dict(
            tickfont=dict(size=11),
            showgrid=False,
            autorange='reversed'  # Match typical correlation matrix layout
        ),
        title=dict(
            text=f'Country Inequality Correlation Matrix ({config["year_range"][0]}-{config["year_range"][1]})',
            font=dict(size=15, color='#ffffff'),
            x=0.5,
            xanchor='center'
        ),
        margin=dict(l=120, r=120, t=80, b=120)
    )
    
    # ═══════════════════════════════════════════════════════════════════
    # DOWNLOAD OPTIONS
    # ═══════════════════════════════════════════════════════════════════
    
    col_spacer_corr, col_downloads_corr = st.columns([10, 1])
    with col_downloads_corr:
        with st.popover("⬇️", help="Download correlation matrix"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # PNG
            try:
                png_bytes = fig_corr.to_image(format="png", width=1400, height=1400)
                st.download_button(
                    "PNG",
                    png_bytes,
                    f"correlation_matrix_{timestamp}.png",
                    "image/png",
                    key="corr_png",
                    use_container_width=True
                )
            except:
                st.button("PNG", disabled=True, key="corr_png", use_container_width=True)

            # JPG
            try:
                jpg_bytes = fig_corr.to_image(format="jpeg", width=1400, height=1400)
                st.download_button(
                    "JPG",
                    jpg_bytes,
                    f"correlation_matrix_{timestamp}.jpg",
                    "image/jpeg",
                    key="corr_jpg",
                    use_container_width=True
                )
            except:
                st.button("JPG", disabled=True, key="corr_jpg", use_container_width=True)

            # JPEG
            try:
                jpeg_bytes = fig_corr.to_image(format="jpeg", width=1400, height=1400)
                st.download_button(
                    "JPEG",
                    jpeg_bytes,
                    f"correlation_matrix_{timestamp}.jpeg",
                    "image/jpeg",
                    key="corr_jpeg",
                    use_container_width=True
                )
            except:
                st.button("JPEG", disabled=True, key="corr_jpeg", use_container_width=True)

    # Display the chart
    st.plotly_chart(fig_corr, use_container_width=True, config={
        'displayModeBar': 'hover',
        'displaylogo': False,
        'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'correlation_matrix',
            'height': 1400,
            'width': 1400,
            'scale': 2
        }
    })

else:
    # Show insufficient data message
    st.markdown(f"""
    <div style="background: rgba(239, 68, 68, 0.1); padding: 30px; border-radius: 12px; margin: 20px 0; border-left: 4px solid #ef4444; text-align: center;">
        <div style="font-size: 3rem; margin-bottom: 15px;">📊</div>
        <h3 style="color: #ffffff; margin-bottom: 15px;">Insufficient Data for Correlation Analysis</h3>
        <p style="color: #94a3b8; font-size: 1rem; line-height: 1.6; margin-bottom: 20px;">
            Correlation analysis requires overlapping data points between countries.<br>
            Current data availability is insufficient for reliable correlation calculation.
        </p>
        <div style="background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 8px; margin-top: 15px;">
            <div style="color: #e2e8f0; font-size: 0.9rem;">
                <b>Data Quality Metrics:</b><br>
                Total years available: <b>{total_years}</b><br>
                Minimum required: <b>{min_required_years} years</b><br>
                Average overlap: <b>{avg_overlap:.0f} years</b>
            </div>
        </div>
        <div style="margin-top: 20px; padding: 15px; background: rgba(59, 130, 246, 0.1); border-radius: 8px;">
            <p style="color: #60a5fa; font-size: 0.85rem; margin: 0;">
                💡 <b>Tip:</b> Try selecting a broader year range or different indicator with more complete data coverage.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show data availability matrix
    st.markdown("### Data Availability by Country")
    
    availability_df = pd.DataFrame({
        'Country': list(data_availability.keys()),
        'Years with Data': list(data_availability.values()),
        'Coverage %': [f"{(count/total_years)*100:.1f}%" for count in data_availability.values()]
    })
    
    st.dataframe(availability_df, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════
# CORRELATION INSIGHTS - Key Statistics (Only shown if correlation is available)
# ═══════════════════════════════════════════════════════════════════

if show_correlation and correlation_matrix is not None:
    st.markdown("### Key Correlation Insights")
    
    col_insight1, col_insight2, col_insight3 = st.columns(3)
    
    # Calculate statistics - safely handle NaN values
    mask = np.ones(correlation_matrix.shape, dtype=bool)
    np.fill_diagonal(mask, False)
    
    # Get correlation values excluding diagonal and NaN
    corr_values = correlation_matrix.values[mask]
    corr_values = corr_values[~np.isnan(corr_values)]  # Remove NaN values
    
    if len(corr_values) > 0:
        # Find max correlation
        max_corr_idx = np.unravel_index(
            np.nanargmax(np.where(mask, correlation_matrix.values, -np.inf)), 
            correlation_matrix.shape
        )
        max_corr_countries = (
            correlation_matrix.index[max_corr_idx[0]], 
            correlation_matrix.columns[max_corr_idx[1]]
        )
        max_corr_value = correlation_matrix.iloc[max_corr_idx[0], max_corr_idx[1]]
        
        # Find min correlation
        min_corr_idx = np.unravel_index(
            np.nanargmin(np.where(mask, correlation_matrix.values, np.inf)), 
            correlation_matrix.shape
        )
        min_corr_value = correlation_matrix.iloc[min_corr_idx[0], min_corr_idx[1]]
        
        # Calculate average
        avg_corr = np.nanmean(corr_values)
        
        # Display statistics
        with col_insight1:
            st.markdown(f"""
            <div class="stat-card" style="min-height: 180px;">
                <div style="font-size: 0.875rem; color: #94a3b8; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">STRONGEST CORRELATION</div>
                <div style="font-size: 1.5rem; color: #10b981; font-weight: 600; margin: 12px 0;">
                    {max_corr_value:.3f}
                </div>
                <div style="font-size: 0.9rem; color: #94a3b8; margin-top: 12px; line-height: 1.4;">
                    {max_corr_countries[0]} ↔ {max_corr_countries[1]}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_insight2:
            st.markdown(f"""
            <div class="stat-card" style="min-height: 180px;">
                <div style="font-size: 0.875rem; color: #94a3b8; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">AVERAGE CORRELATION</div>
                <div style="font-size: 1.5rem; color: #ffffff; font-weight: 600; margin: 12px 0;">
                    {avg_corr:.3f}
                </div>
                <div style="font-size: 0.9rem; color: #94a3b8; margin-top: 12px; line-height: 1.4;">
                    Overall regional similarity
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_insight3:
            if not np.isnan(min_corr_value):
                if min_corr_value < 0:
                    min_corr_countries = (
                        correlation_matrix.index[min_corr_idx[0]], 
                        correlation_matrix.columns[min_corr_idx[1]]
                    )
                    label_text = "MOST DIVERGENT"
                    color = "#ef4444"
                    desc = f"{min_corr_countries[0]} ↔ {min_corr_countries[1]}"
                else:
                    label_text = "WEAKEST CORRELATION"
                    color = "#f59e0b"
                    min_corr_countries = (
                        correlation_matrix.index[min_corr_idx[0]], 
                        correlation_matrix.columns[min_corr_idx[1]]
                    )
                    desc = f"{min_corr_countries[0]} ↔ {min_corr_countries[1]}"
                
                st.markdown(f"""
                <div class="stat-card" style="min-height: 180px;">
                    <div style="font-size: 0.875rem; color: #94a3b8; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">{label_text}</div>
                    <div style="font-size: 1.5rem; color: {color}; font-weight: 600; margin: 12px 0;">
                        {min_corr_value:.3f}
                    </div>
                    <div style="font-size: 0.9rem; color: #94a3b8; margin-top: 12px; line-height: 1.4;">
                        {desc}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        # No valid correlation values
        st.warning("⚠️ Insufficient overlapping data to calculate meaningful correlations.")
    
# STORYTELLING: Correlation Context
if show_correlation and correlation_matrix is not None:
    st.markdown(f"""
    <div style="background-color: rgba(30, 41, 59, 0.5); padding: 15px; border-radius: 5px; border-left: 3px solid #8b5cf6; margin-top: 20px;">
        <p style="margin: 0; color: #cbd5e1; font-size: 0.85rem; line-height: 1.4;">
            <strong style="color: #e0e7ff;">Efficiency Note:</strong> A high average correlation ({avg_corr:.2f}) suggests that economic policies affecting one country likely mirror trends in neighbors, implying a highly integrated regional economic cycle for {indicator_name}.
        </p>
    </div>
    """, unsafe_allow_html=True)
# ═══════════════════════════════════════════════════════════════════
# INTERPRETATION GUIDE (Only shown if correlation is available)
# ═══════════════════════════════════════════════════════════════════

if show_correlation and correlation_matrix is not None:
    st.markdown("""
    <div style="background: rgba(59, 130, 246, 0.1); padding: 1rem; border-radius: 8px; margin-top: 1rem; border-left: 3px solid #3b82f6;">
        <div style="color: #e2e8f0; font-size: 0.9rem;">
            <strong style="color: #60a5fa;">💡 How to Interpret This Matrix:</strong><br>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 0.5rem;">
                <div>
                    • <strong>+1.0</strong> = Perfect positive correlation (countries move together)<br>
                    • <strong>0.8 to 1.0</strong> = Very strong correlation<br>
                    • <strong>0.6 to 0.8</strong> = Strong correlation<br>
                    • <strong>0.4 to 0.6</strong> = Moderate correlation
                </div>
                <div>
                    • <strong>0.2 to 0.4</strong> = Weak correlation<br>
                    • <strong>0.0</strong> = No correlation (independent patterns)<br>
                    • <strong>Negative values</strong> = Opposite trends<br>
                    • <strong>Diagonal</strong> = Always 1.0 (country vs itself)
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Optional: Show top correlations table
    with st.expander("📊 View Top Correlation Pairs"):
        # Get all pairwise correlations (excluding diagonal)
        pairs = []
        for i in range(len(correlation_matrix)):
            for j in range(i+1, len(correlation_matrix)):
                corr_val = correlation_matrix.iloc[i, j]
                if not np.isnan(corr_val):  # Only include valid correlations
                    pairs.append({
                        'Country 1': correlation_matrix.index[i],
                        'Country 2': correlation_matrix.columns[j],
                        'Correlation': corr_val
                    })
        
        if pairs:
            # Sort by absolute correlation
            pairs_df = pd.DataFrame(pairs)
            pairs_df['Abs Correlation'] = pairs_df['Correlation'].abs()
            pairs_df = pairs_df.sort_values('Abs Correlation', ascending=False)
            
            # Display top 10
            st.dataframe(
                pairs_df[['Country 1', 'Country 2', 'Correlation']].head(10),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No valid correlation pairs available with current data.")
# ═══════════════════════════════════════════════════════════════════
# BOTTOM SECTION: Rankings & Timeline
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown('<div class="section-header">Detailed Rankings & Individual Trends</div>', unsafe_allow_html=True)

col_bottom1, col_bottom2 = st.columns([1, 1.5])

with col_bottom1:
    st.markdown("""
    <div style="margin-bottom: 15px;">
        <h3 style="font-size: 1rem; color: #ffffff; font-weight: 600; margin: 0;">
            Current Rankings (Latest Year)
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    rankings = latest_data.groupby('country')['value'].mean().reset_index()
    # Sort based on indicator type: for positive indicators, highest is best (rank #1)
    if is_positive_indicator:
        rankings = rankings.sort_values('value', ascending=False).reset_index(drop=True)
    else:
        rankings = rankings.sort_values('value', ascending=True).reset_index(drop=True)
    
    for idx, row in rankings.iterrows():
        rank = idx + 1
        country = row['country']
        value = row['value']
        
        # Calculate bar width based on indicator type
        # For positive indicators: higher value = fuller bar
        # For negative indicators: lower value = fuller bar (inverted)
        if is_positive_indicator:
            pct_of_max = (value / rankings['value'].max()) * 100
        else:
            # Invert for negative indicators so rank #1 (lowest) has fullest bar
            max_val = rankings['value'].max()
            min_val = rankings['value'].min()
            if max_val != min_val:
                # Normalize inversely: best (min) = 100%, worst (max) = smallest %
                pct_of_max = ((max_val - value) / (max_val - min_val)) * 100
            else:
                pct_of_max = 100  # All equal
        
        # Color based on rank (NO EMOJIS)
        if rank == 1:
            bar_color = '#10b981'
            rank_icon = '#1'
        elif rank == 2:
            bar_color = '#3b82f6'
            rank_icon = '#2'
        elif rank == 3:
            bar_color = '#8b5cf6'
            rank_icon = '#3'
        else:
            bar_color = '#64748b'
            rank_icon = f'#{rank}'
        
        st.markdown(f"""
        <div style="margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: #e2e8f0; font-size: 0.9rem; font-weight: 500;">
                    {rank_icon} {country}
                </span>
                <span style="color: #ffffff; font-weight: 600; font-size: 0.9rem;">
                    {value:.2f}
                </span>
            </div>
            <div style="background: rgba(100, 116, 139, 0.2); border-radius: 4px; height: 6px; overflow: hidden;">
                <div style="background: {bar_color}; height: 100%; width: {pct_of_max}%; border-radius: 4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_bottom2:
    st.markdown("""
    <div style="margin-bottom: 15px;">
        <h3 style="font-size: 1rem; color: #ffffff; font-weight: 600; margin: 0;">
            Comparative Trends (Non-Stacked)
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    fig_lines = go.Figure()
    
    for i, country in enumerate(filtered_df['country'].unique()):
        country_data = filtered_df[filtered_df['country'] == country].sort_values('year')
        
        fig_lines.add_trace(go.Scatter(
            x=country_data['year'],
            y=country_data['value'],
            mode='lines+markers',
            name=country,
            line=dict(width=2.5, color=colors[i % len(colors)]),
            marker=dict(size=6, color=colors[i % len(colors)]),
            hovertemplate='<b>%{fullData.name}</b><br>Year: %{x}<br>Value: %{y:.2f}<extra></extra>'
        ))
    
    # REQUIREMENT #5: PROPER AXIS LABELS (FIXED SPACING)
    fig_lines.update_layout(
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', size=12),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 116, 139, 0.2)',
            title=dict(
                text=f'<b>Year ({config["year_range"][0]}-{config["year_range"][1]})</b>',
                font=dict(size=13, color='#94a3b8')
            ),
            color='#94a3b8'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 116, 139, 0.2)',
            title=dict(
                text=f'<b>{y_label_short}<br>(Index Value)</b>',  # Use <br> for line break
                font=dict(size=12, color='#94a3b8')
            ),
            color='#94a3b8'
        ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.01,
            bgcolor='#0f1419',
            bordercolor='rgba(59, 130, 246, 0.3)',
            borderwidth=1,
            font=dict(color='#e2e8f0', size=10),
            title=dict(text='<b>Countries</b>', font=dict(size=11, color='#e2e8f0'))
        ),
        margin=dict(l=80, r=150, t=40, b=50),  # Increased left margin
        hovermode='x unified'
    )
    
    # Download options
    col_spacer4, col_downloads4 = st.columns([10, 1])
    with col_downloads4:
        with st.popover("⬇️", help="Download in multiple formats"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # PNG
            try:
                png_bytes = fig_lines.to_image(format="png", width=1400, height=1000)
                st.download_button("PNG", png_bytes, f"individual_trends_{timestamp}.png", "image/png", key="line_png", use_container_width=True)
            except:
                st.button("PNG", disabled=True, key="line_png", use_container_width=True)

            # JPG
            try:
                jpg_bytes = fig_lines.to_image(format="jpeg", width=1400, height=1000)
                st.download_button("JPG", jpg_bytes, f"individual_trends_{timestamp}.jpg", "image/jpeg", key="line_jpg", use_container_width=True)
            except:
                st.button("JPG", disabled=True, key="line_jpg", use_container_width=True)

            # JPEG
            try:
                jpeg_bytes = fig_lines.to_image(format="jpeg", width=1400, height=1000)
                st.download_button("JPEG", jpeg_bytes, f"individual_trends_{timestamp}.jpeg", "image/jpeg", key="line_jpeg", use_container_width=True)
            except:
                st.button("JPEG", disabled=True, key="line_jpeg", use_container_width=True)
    
    st.plotly_chart(fig_lines, use_container_width=True, config={
        'displayModeBar': 'hover',
        'displaylogo': False,
        'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'autoScale2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'individual_trends',
            'height': 1000,
            'width': 1400,
            'scale': 2
        }
    })

    # STORYTELLING: Detailed Trends (MOVED BELOW CHART)
    st.markdown(f"""
    <div style="background-color: rgba(30, 41, 59, 0.5); padding: 15px; border-radius: 5px; border-left: 3px solid #f59e0b; margin-top: 20px;">
        <p style="margin: 0; color: #cbd5e1; font-size: 0.85rem; line-height: 1.4;">
            <strong style="color: #e0e7ff;">Trend Analysis:</strong> Use this detailed line chart to spot divergent paths. 
            Countries with lines crossing others or moving against the general "cluster" are outliers worth investigating.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# FOOTER INSIGHTS 
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown('<div class="section-header">Key Insights & Raw Data</div>', unsafe_allow_html=True)

col_insight1, col_insight2, col_insight3 = st.columns(3)

with col_insight1:
    # Trend direction based on indicator type
    if is_negative_indicator:
        trend_direction = "improving" if yoy_pct < 0 else "worsening"
    else:
        trend_direction = "improving" if yoy_pct > 0 else "worsening"

    # Dynamic label based on indicator and country count
    metric_label = indicator_name.split('(')[0].strip() if '(' in indicator_name else indicator_name
    trend_label = "COUNTRY TREND" if is_single_country else "REGIONAL TREND"

    st.markdown(f"""
    <div class="stat-card">
        <div style="font-size: 0.875rem; color: #94a3b8; margin-bottom: 8px;">{trend_label}</div>
        <div style="font-size: 1.1rem; color: #ffffff; font-weight: 600;">
            {trend_direction.capitalize()}
        </div>
        <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 8px;">
            {abs(yoy_pct):.1f}% change year-over-year
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_insight2:
    volatility = filtered_df.groupby('country')['value'].std().mean()
    
    st.markdown(f"""
    <div class="stat-card">
        <div style="font-size: 0.875rem; color: #94a3b8; margin-bottom: 8px;">VOLATILITY</div>
        <div style="font-size: 1.1rem; color: #ffffff; font-weight: 600;">
            {volatility:.2f} avg std dev
        </div>
        <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 8px;">
            Data stability indicator
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_insight3:
    gap = latest_data['value'].max() - latest_data['value'].min()

    if is_single_country:
        gap_label = "DATA POINTS"
        gap_value = f"{len(filtered_df)}"
        gap_desc = "Total records analyzed"
    else:
        gap_label = "REGIONAL GAP"
        gap_value = f"{gap:.2f} points"
        gap_desc = "Between best and worst"

    st.markdown(f"""
    <div class="stat-card">
        <div style="font-size: 0.875rem; color: #94a3b8; margin-bottom: 8px;">{gap_label}</div>
        <div style="font-size: 1.1rem; color: #ffffff; font-weight: 600;">
            {gap_value}
        </div>
        <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 8px;">
            {gap_desc}
        </div>
    </div>
    """, unsafe_allow_html=True)

# STORYTELLING: Key Insights Context
# Dynamic explanation based on indicator type and country count
if is_negative_indicator:
    trend_explanation = '"Improving" means the metric is decreasing (good), "Worsening" means it\'s increasing.'
else:
    trend_explanation = '"Improving" means the metric is increasing (good), "Worsening" means it\'s decreasing.'

if is_single_country:
    trend_label_text = "Country Trend"
    gap_explanation = f"<b>Data Points:</b> Total number of records available for {best_country} in the selected time range."
else:
    trend_label_text = "Regional Trend"
    gap_explanation = "<b>Regional Gap:</b> The distance between the best and worst performing countries. A smaller gap suggests regional cohesion."

st.markdown(f"""
<div style="background-color: rgba(30, 41, 59, 0.5); padding: 15px; border-radius: 5px; border-left: 3px solid #10b981; margin-top: 20px;">
    <h5 style="margin: 0 0 8px 0; color: #e0e7ff; font-size: 0.9rem; font-weight: 600;">How to interpret these metrics</h5>
    <ul style="margin: 0; padding-left: 20px; color: #cbd5e1; font-size: 0.85rem; line-height: 1.5;">
        <li><b>{trend_label_text}:</b> Indicates the overall direction. {trend_explanation}</li>
        <li><b>Volatility:</b> Measures stability. Lower values mean steady progress; higher values indicate erratic economic shocks or inconsistent data.</li>
        <li>{gap_explanation}</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# REQUIREMENT #7: DATA EXPORT FUNCTIONALITY
# ═══════════════════════════════════════════════════════════════════

with st.expander("View Raw Data & Export Options"):
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    export_data_menu(filtered_df, "dashboard_data_export", key="dashboard_data")

st.markdown("---")
st.caption("Dashboard | South Asia Inequality Analysis Platform")

# -----------------
# Navigation
# -----------------
from utils.navigation_ui import bottom_nav_layout
bottom_nav_layout(__file__)