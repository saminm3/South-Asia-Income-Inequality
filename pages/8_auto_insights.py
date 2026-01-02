import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from scipy import stats

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.loaders import load_inequality_data
from utils.utils import human_indicator

# Try new version first, fallback to old version
try:
    from utils.insights import generate_ranked_insights, format_insights_as_text, INSIGHT_TYPES
except ImportError:
    from utils.insights import generate_multimode_insights, format_insights_as_text
    INSIGHT_TYPES = {
        'trends': 'Trends',
        'rankings': 'Rankings', 
        'comparisons': 'Comparisons',
        'anomalies': 'Anomalies',
        'statistics': 'Statistics',
        'quality': 'Quality'
    }
    def generate_ranked_insights(df, countries, indicator, year_range, 
                                 enabled_types=None, max_insights=15, focus_mode=False):
        result = generate_multimode_insights(df, countries, indicator, year_range, max_insights)
        return {
            'ranked_insights': result.get('simple', []),
            'all_insights': result.get('categories', {}),
            'metadata': {
                'total_generated': len(result.get('simple', [])),
                'total_shown': min(max_insights, len(result.get('simple', []))),
                'countries_analyzed': len(countries),
                'indicator': indicator,
                'year_range': year_range,
                'focus_mode': focus_mode,
                'enabled_types': enabled_types or []
            },
            'settings': {
                'enabled_types': enabled_types or [],
                'focus_mode': focus_mode,
                'max_insights': max_insights
            }
        }

# ═══════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Auto Insights Pro | SA Inequality Analytics",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════
# ENHANCED STYLING - HIDE NAVIGATION, KEEP SIDEBAR CONTROLS
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* Hide only the navigation links, keep sidebar for controls */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* Main background with gradient */
    .main {
        background: linear-gradient(180deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
    }
    
    /* Container spacing */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100%;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Typography */
    h1, h2, h3, h4 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    p, span, div, label {
        color: #e2e8f0;
    }
    
    /* Enhanced metric cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        border-color: rgba(59, 130, 246, 0.6);
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
        transform: translateY(-2px);
    }
    
    /* Chart containers with enhanced styling */
    .chart-container {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
        border: 1px solid rgba(100, 116, 139, 0.3);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    
    .chart-container:hover {
        border-color: rgba(100, 116, 139, 0.5);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.5);
    }
    
    /* Insight cards - HIGH PRIORITY */
    .insight-card-high {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), #0f1419);
        border: 2px solid rgba(16, 185, 129, 0.6);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.2);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .insight-card-high::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #10b981, #059669);
    }
    
    .insight-card-high:hover {
        border-color: rgba(16, 185, 129, 0.8);
        box-shadow: 0 8px 32px rgba(16, 185, 129, 0.3);
        transform: translateX(4px);
    }
    
    /* Insight cards - MEDIUM PRIORITY */
    .insight-card-medium {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), #0f1419);
        border: 1.5px solid rgba(59, 130, 246, 0.5);
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.15);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .insight-card-medium::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #3b82f6, #2563eb);
    }
    
    .insight-card-medium:hover {
        border-color: rgba(59, 130, 246, 0.7);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.25);
        transform: translateX(4px);
    }
    
    /* Insight cards - LOW PRIORITY */
    .insight-card-low {
        background: linear-gradient(135deg, rgba(100, 116, 139, 0.08), #0f1419);
        border: 1px solid rgba(100, 116, 139, 0.4);
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .insight-card-low:hover {
        border-color: rgba(100, 116, 139, 0.6);
        transform: translateX(2px);
    }
    
    /* Priority badges with enhanced styling */
    .priority-high {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 6px 14px;
        border-radius: 14px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
    }
    
    .priority-medium {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        padding: 6px 14px;
        border-radius: 14px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
    }
    
    .priority-low {
        background: linear-gradient(135deg, #6b7280, #4b5563);
        color: white;
        padding: 5px 12px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Score badge */
    .score-badge {
        background: rgba(59, 130, 246, 0.2);
        border: 1px solid rgba(59, 130, 246, 0.4);
        color: #60a5fa;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 600;
        display: inline-block;
    }
    
    /* Section headers with gradient underline */
    .section-header {
        color: #3b82f6;
        font-weight: 700;
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(59, 130, 246, 0.3);
        background: linear-gradient(90deg, rgba(59, 130, 246, 0.1), transparent);
        padding-left: 12px;
    }
    
    /* Statistical detail boxes */
    .stat-box {
        background: rgba(59, 130, 246, 0.05);
        border-left: 3px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 12px 0;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    /* Info boxes */
    .info-box {
        background: rgba(139, 92, 246, 0.1);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 12px;
        padding: 16px;
        margin: 16px 0;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #0f1419;
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: 1px solid rgba(100, 116, 139, 0.3);
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 600;
        padding: 12px 24px;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(59, 130, 246, 0.1);
        border-color: rgba(59, 130, 246, 0.5);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(139, 92, 246, 0.2));
        border-color: #3b82f6;
        color: #ffffff;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(59, 130, 246, 0.05);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 8px;
        font-weight: 600;
        color: #e2e8f0 !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(59, 130, 246, 0.1);
        border-color: rgba(59, 130, 246, 0.4);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# LOAD DATA & CONFIG
# ═══════════════════════════════════════════════════════════════════

df = load_inequality_data()

if df.empty:
    st.error("No data available")
    st.stop()

def ensure_config(df):
    """Ensure analysis config exists with sensible defaults - works standalone without home page config"""
    if "analysis_config" not in st.session_state or st.session_state.analysis_config is None:
        countries = sorted(df["country"].dropna().unique().tolist())
        indicators = sorted(df["indicator"].dropna().unique().tolist())
        min_year = int(df["year"].min())
        max_year = int(df["year"].max())
        default_indicator = "gini_index" if "gini_index" in indicators else (indicators[0] if indicators else None)
        
        # Use ALL countries by default (open access platform)
        st.session_state.analysis_config = {
            "countries": countries,  # All countries
            "indicator": default_indicator,
            "year_range": (max(min_year, max_year - 20), max_year),  # Last 20 years
            "color_scale": "Viridis",
        }
    
    # Validate config has necessary fields
    if 'countries' not in st.session_state.analysis_config or not st.session_state.analysis_config['countries']:
        st.session_state.analysis_config['countries'] = sorted(df["country"].dropna().unique().tolist())
    
    if 'indicator' not in st.session_state.analysis_config:
        indicators = sorted(df["indicator"].dropna().unique().tolist())
        st.session_state.analysis_config['indicator'] = "gini_index" if "gini_index" in indicators else indicators[0]
    
    if 'year_range' not in st.session_state.analysis_config:
        min_year = int(df["year"].min())
        max_year = int(df["year"].max())
        st.session_state.analysis_config['year_range'] = (max(min_year, max_year - 20), max_year)

ensure_config(df)
config = st.session_state.analysis_config

# Initialize insight settings
if 'insight_settings' not in st.session_state:
    st.session_state.insight_settings = {
        'enabled_types': list(INSIGHT_TYPES.keys()) if INSIGHT_TYPES else [],
        'focus_mode': False,
        'max_insights': 15,
        'analysis_depth': 'Detailed Analysis',
        'show_statistics': True,
        'show_confidence': True
    }

# ═══════════════════════════════════════════════════════════════════
# SIDEBAR - ENHANCED CONTROLS
# ═══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("# Analysis Controls")
    st.markdown("---")
    
    settings = st.session_state.insight_settings
    
    # Analysis Depth
    st.markdown("### Analysis Depth")
    depth = st.radio(
        "Select detail level:",
        ["Quick Overview", "Detailed Analysis", "Expert Mode"],
        index=1,
        help="Controls the number and depth of insights generated"
    )
    settings['analysis_depth'] = depth
    
    if depth == "Quick Overview":
        settings['max_insights'] = 8
        st.info("Top 8 insights with simple explanations")
    elif depth == "Detailed Analysis":
        settings['max_insights'] = 15
        st.info("Top 15 insights with balanced technical detail")
    else:
        settings['max_insights'] = 25
        st.info("Top 25 insights with full statistical depth")
    
    st.markdown("---")
    
    # Display Options
    st.markdown("### Display Options")
    settings['show_statistics'] = st.checkbox("Show Statistical Details", value=True,
                                               help="Display p-values, R², confidence intervals")
    settings['show_confidence'] = st.checkbox("Show Confidence Indicators", value=True,
                                              help="Display reliability scores and data quality")
    
    st.markdown("---")
    
    # Insight Type Filters
    st.markdown("### Insight Categories")
    st.caption("Select types of insights to generate")
    
    available_types = list(INSIGHT_TYPES.keys()) if INSIGHT_TYPES else ['trends', 'rankings', 'anomalies']
    
    # Select/Deselect All
    col_all1, col_all2 = st.columns(2)
    with col_all1:
        if st.button("Select All", use_container_width=True):
            for t in available_types:
                st.session_state[f"filter_{t}"] = True
            st.rerun()
    with col_all2:
        if st.button("Clear All", use_container_width=True):
            for t in available_types:
                st.session_state[f"filter_{t}"] = False
            st.rerun()
    
    st.markdown("")
    
    type_cols = st.columns(2)
    enabled_types = []
    
    for idx, insight_type in enumerate(available_types):
        col = type_cols[idx % 2]
        with col:
            label = INSIGHT_TYPES.get(insight_type, insight_type).replace('_', ' ').title() if INSIGHT_TYPES else insight_type
            if st.checkbox(label, value=True, key=f"filter_{insight_type}"):
                enabled_types.append(insight_type)
    
    settings['enabled_types'] = enabled_types if enabled_types else available_types
    
    st.markdown("---")
    
    # Focus Mode
    st.markdown("### Advanced Settings")
    focus_mode = st.checkbox(
        "Focus Mode",
        value=settings.get('focus_mode', False),
        help="Deep dive analysis on 2-3 countries with highest data quality"
    )
    settings['focus_mode'] = focus_mode
    
    if focus_mode:
        st.success("Deep analysis mode: Analyzing top 3 countries")
    
    st.markdown("---")
    
    # Reset button
    if st.button("Reset to Defaults", use_container_width=True):
        st.session_state.insight_settings = {
            'enabled_types': available_types,
            'focus_mode': False,
            'max_insights': 15,
            'analysis_depth': 'Detailed Analysis',
            'show_statistics': True,
            'show_confidence': True
        }
        st.rerun()

# ═══════════════════════════════════════════════════════════════════
# TOP NAVIGATION
# ═══════════════════════════════════════════════════════════════════

nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([5, 1, 1, 1])

with nav_col2:
    if st.button("Home", use_container_width=True):
        st.switch_page("home.py")

with nav_col3:
    if st.button("Dashboard", use_container_width=True):
        st.switch_page("pages/1_dashboard.py")

with nav_col4:
    if st.button("Help", use_container_width=True):
        st.switch_page("pages/10_help.py")

# ═══════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<div style="margin-bottom: 2rem; margin-top: 1rem;">
    <h1 style="font-size: 2.8rem; margin: 0; background: linear-gradient(135deg, #8b5cf6, #3b82f6, #06b6d4); 
               -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700;">
        Auto Insights Pro
    </h1>
    <p style="color: #94a3b8; font-size: 1.05rem; margin-top: 0.75rem; font-weight: 500;">
         Statistical Analysis with Interactive Visualizations and Detailed Insights
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ═══════════════════════════════════════════════════════════════════
# GENERATE INSIGHTS
# ═══════════════════════════════════════════════════════════════════

with st.spinner("Analyzing data and generating insights..."):
    analysis_countries = config['countries']
    
    result = generate_ranked_insights(
        df,
        analysis_countries,
        config['indicator'],
        config['year_range'],
        enabled_types=settings['enabled_types'],
        max_insights=settings['max_insights'],
        focus_mode=settings['focus_mode']
    )

ranked_insights = result.get('ranked_insights', [])
metadata = result.get('metadata', {})

# Filter data for visualizations
filtered_df = df[
    (df['country'].isin(config['countries'])) &
    (df['year'] >= config['year_range'][0]) &
    (df['year'] <= config['year_range'][1]) &
    (df['indicator'] == config['indicator'])
].copy()

# Check if we have data
if filtered_df.empty:
    st.warning("No data available for the selected configuration. Please adjust the settings or check your data source.")
    st.info("Try adjusting the year range or selecting different countries in the home page configuration.")
    st.stop()

# Calculate regional statistics
regional_stats = filtered_df.groupby('year')['value'].agg(['mean', 'std', 'min', 'max']).reset_index()

# ═══════════════════════════════════════════════════════════════════
# ENHANCED SUMMARY METRICS
# ═══════════════════════════════════════════════════════════════════

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Insights", 
              metadata.get('total_generated', 0),
              help="Total number of insights generated from analysis")

with col2:
    st.metric("Displaying", 
              metadata.get('total_shown', 0),
              help="Top insights ranked by statistical importance")

with col3:
    st.metric("Countries", 
              metadata.get('countries_analyzed', 0),
              help="Number of countries included in analysis")

with col4:
    high_priority = len([i for i in ranked_insights if i.get('score', 0) >= 15])
    st.metric("High Priority", 
              high_priority,
              delta="Critical",
              help="Insights requiring immediate attention (score >= 15)")

with col5:
    # Calculate average data quality
    total_points = len(filtered_df)
    possible_points = len(config['countries']) * (config['year_range'][1] - config['year_range'][0] + 1)
    quality_pct = (total_points / possible_points * 100) if possible_points > 0 else 0
    st.metric("Data Quality", 
              f"{quality_pct:.1f}%",
              help="Completeness of data across countries and years")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# VISUALIZATION 1: ENHANCED INEQUALITY TRENDS
# ═══════════════════════════════════════════════════════════════════

st.markdown("## Temporal Trend Analysis")
st.caption("Evolution of inequality over time with statistical trend lines")

col_chart1, col_insights1 = st.columns([1.3, 1])

with col_chart1:
    # Chart container removed to prevent empty box
    
    # Create enhanced streamgraph with trend lines
    fig_trends = go.Figure()
    
    # Add area traces for each country
    for country in config['countries']:
        country_data = filtered_df[filtered_df['country'] == country].sort_values('year')
        if not country_data.empty:
            fig_trends.add_trace(go.Scatter(
                x=country_data['year'],
                y=country_data['value'],
                name=country,
                mode='lines',
                stackgroup='one',
                line=dict(width=0.5),
                fillcolor='rgba(0,0,0,0)',
                hovertemplate='<b>%{fullData.name}</b><br>Year: %{x}<br>Value: %{y:.2f}<extra></extra>'
            ))
    
    # Add regional average line
    fig_trends.add_trace(go.Scatter(
        x=regional_stats['year'],
        y=regional_stats['mean'],
        name='Regional Average',
        mode='lines',
        line=dict(color='rgba(255, 255, 255, 0.8)', width=3, dash='dash'),
        hovertemplate='<b>Regional Average</b><br>Year: %{x}<br>Value: %{y:.2f}<extra></extra>'
    ))
    
    # Add confidence band
    fig_trends.add_trace(go.Scatter(
        x=regional_stats['year'].tolist() + regional_stats['year'].tolist()[::-1],
        y=(regional_stats['mean'] + regional_stats['std']).tolist() + 
          (regional_stats['mean'] - regional_stats['std']).tolist()[::-1],
        fill='toself',
        fillcolor='rgba(255, 255, 255, 0.1)',
        line=dict(color='rgba(0,0,0,0)'),
        showlegend=False,
        name='Confidence Band',
        hoverinfo='skip'
    ))
    
    fig_trends.update_layout(
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', size=11),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 116, 139, 0.15)',
            title=dict(text='Year', font=dict(size=13)),
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 116, 139, 0.15)',
            title=dict(text=human_indicator(config['indicator']), font=dict(size=13)),
            tickfont=dict(size=11)
        ),
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=1.02,
            bgcolor='rgba(15, 20, 25, 0.8)',
            bordercolor='rgba(100, 116, 139, 0.3)',
            borderwidth=1,
            font=dict(size=10)
        ),
        margin=dict(l=10, r=160, t=10, b=10)
    )
    
    st.plotly_chart(fig_trends, use_container_width=True, config={'displayModeBar': False})
    
    # Chart container closing div removed
    
    # Statistical summary below chart
    if settings.get('show_statistics'):
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        
        # Calculate overall trend
        years = regional_stats['year'].values
        values = regional_stats['mean'].values
        if len(years) >= 3:
            slope, intercept, r_value, p_value, std_err = stats.linregress(years, values)
            
            trend_direction = "decreasing" if slope < 0 else "increasing"
            trend_strength = "strong" if abs(r_value) > 0.7 else "moderate" if abs(r_value) > 0.4 else "weak"
            significance = "statistically significant" if p_value < 0.05 else "not statistically significant"
            
            st.markdown(f"""
            **Regional Trend Analysis:**
            - Overall trend: {trend_direction} ({slope:.3f} per year)
            - Correlation strength: {trend_strength} (R² = {r_value**2:.3f})
            - Statistical significance: {significance} (p = {p_value:.4f})
            - Current regional average: {values[-1]:.2f}
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # How to read
    with st.expander("How to Interpret This Visualization"):
        st.markdown("""
        **Stacked Area Chart with Trend Analysis**
        
        **Visual Elements:**
        - **Colored layers**: Each represents one country's contribution
        - **White dashed line**: Regional average across all countries
        - **Gray shaded area**: ±1 standard deviation confidence band
        - **Layer width**: Magnitude of inequality for that country
        
        **Interpretation Guide:**
        - **Upward trends**: Worsening inequality (increasing GINI)
        - **Downward trends**: Improving equality (decreasing GINI)
        - **Layers crossing**: Countries changing relative positions
        - **Wide confidence band**: High variation between countries
        - **Narrow band**: Countries converging toward similar levels
        
        **Key Patterns to Identify:**
        1. Is the regional average trending up or down?
        2. Are countries converging (narrowing band) or diverging (widening)?
        3. Which countries consistently perform above/below average?
        4. Any sudden changes indicating policy impacts or crises?
        """)

with col_insights1:
    st.markdown('<div class="section-header">Key Findings from Trend Analysis</div>', unsafe_allow_html=True)
    
    # Filter insights relevant to trends
    trend_insights = [i for i in ranked_insights if i.get('insight_type') in ['trends', 'indexed_trends', 'forecast']]
    
    if trend_insights:
        for idx, insight in enumerate(trend_insights[:5], 1):
            score = insight.get('score', 0)
            priority = "HIGH" if score >= 15 else "MEDIUM" if score >= 8 else "LOW"
            priority_class = f"insight-card-{priority.lower()}"
            badge_class = f"priority-{priority.lower()}"
            
            # Build confidence indicator
            confidence_html = ""
            if settings.get('show_confidence'):
                p_val = insight.get('p_value', 1)
                r_sq = insight.get('r_squared', 0)
                if p_val < 0.05 and r_sq > 0.5:
                    confidence_html = '<span style="color: #10b981; font-size: 0.75rem;">● High Confidence</span>'
                elif p_val < 0.1:
                    confidence_html = '<span style="color: #f59e0b; font-size: 0.75rem;">● Medium Confidence</span>'
                else:
                    confidence_html = '<span style="color: #6b7280; font-size: 0.75rem;">● Low Confidence</span>'
            
            # Build statistical details
            stat_details = ""
            if settings.get('show_statistics'):
                p_val = insight.get('p_value')
                r_sq = insight.get('r_squared')
                if p_val is not None and r_sq is not None:
                    stat_details = f'<div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(100,116,139,0.2); font-size: 0.8rem; color: #94a3b8;">p-value: {p_val:.4f} | R²: {r_sq:.3f}</div>'
            
            st.markdown(f"""
            <div class="{priority_class}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span class="{badge_class}">#{idx} {priority}</span>
                    <span class="score-badge">Score: {score:.1f}</span>
                </div>
                <div style="color: #ffffff; font-weight: 600; margin-bottom: 8px; font-size: 1.05rem; line-height: 1.4;">
                    {insight.get('title', 'Insight')}
                </div>
                <div style="color: #e2e8f0; font-size: 0.92rem; line-height: 1.6; margin-bottom: 6px;">
                    {insight.get('narrative', '')}
                </div>
                {confidence_html}
                {stat_details}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No trend insights generated. Adjust filters in sidebar to see more insights.")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# VISUALIZATION 2: ENHANCED COUNTRY RANKINGS
# ═══════════════════════════════════════════════════════════════════

st.markdown("## Comparative Country Rankings")
st.caption("Current inequality levels ranked from best to worst performing")

col_chart2, col_insights2 = st.columns([1.3, 1])

with col_chart2:
    # Chart container removed to prevent empty box
    
    # Get latest year data and calculate change from previous year
    latest_year = config['year_range'][1]
    prev_year = latest_year - 1
    
    latest_data = filtered_df[filtered_df['year'] == latest_year].sort_values('value')
    prev_data = filtered_df[filtered_df['year'] == prev_year][['country', 'value']].rename(columns={'value': 'prev_value'})
    
    # Merge to get change
    ranking_data = latest_data.merge(prev_data, on='country', how='left')
    ranking_data['change'] = ranking_data['value'] - ranking_data['prev_value']
    ranking_data['change_pct'] = (ranking_data['change'] / ranking_data['prev_value'] * 100).fillna(0)
    
    # Check if we have ranking data
    if ranking_data.empty:
        st.warning(f"No data available for year {latest_year}. Showing available data...")
        # Use latest available year
        latest_available = filtered_df['year'].max()
        ranking_data = filtered_df[filtered_df['year'] == latest_available].sort_values('value')
        ranking_data['change'] = 0
        ranking_data['change_pct'] = 0
    
    # Create enhanced horizontal bar chart with change indicators
    fig_ranking = go.Figure()
    
    # Color based on performance level
    colors = []
    for val in ranking_data['value']:
        if val < 30:
            colors.append('#10b981')  # Green - Low inequality
        elif val < 35:
            colors.append('#3b82f6')  # Blue - Moderate
        elif val < 40:
            colors.append('#f59e0b')  # Orange - Medium-high
        else:
            colors.append('#ef4444')  # Red - High inequality
    
    fig_ranking.add_trace(go.Bar(
        y=ranking_data['country'],
        x=ranking_data['value'],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(255,255,255,0.3)', width=1)
        ),
        text=ranking_data['value'].round(2),
        textposition='outside',
        textfont=dict(size=11, color='#e2e8f0'),
        hovertemplate='<b>%{y}</b><br>Value: %{x:.2f}<br>Change: %{customdata:.2f}%<extra></extra>',
        customdata=ranking_data['change_pct']
    ))
    
    # Add vertical lines for thresholds
    fig_ranking.add_vline(x=30, line_dash="dot", line_color="rgba(16, 185, 129, 0.5)", 
                          annotation_text="Low Inequality", annotation_position="top")
    fig_ranking.add_vline(x=35, line_dash="dot", line_color="rgba(59, 130, 246, 0.5)",
                          annotation_text="Moderate", annotation_position="top")
    fig_ranking.add_vline(x=40, line_dash="dot", line_color="rgba(245, 158, 11, 0.5)",
                          annotation_text="High", annotation_position="top")
    
    fig_ranking.update_layout(
        height=max(350, len(ranking_data) * 45),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', size=11),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 116, 139, 0.15)',
            title=dict(text=human_indicator(config['indicator']), font=dict(size=13)),
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            showgrid=False,
            title='',
            tickfont=dict(size=11)
        ),
        margin=dict(l=10, r=80, t=40, b=10),
        showlegend=False
    )
    
    st.plotly_chart(fig_ranking, use_container_width=True, config={'displayModeBar': False})
    
    # Chart container closing div removed
    
    # Ranking table with changes
    if settings.get('show_statistics'):
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.markdown(f"**Detailed Rankings for {latest_year}:**")
        
        # Create ranking table
        rank_table = ranking_data[['country', 'value', 'change', 'change_pct']].copy()
        rank_table['Rank'] = range(1, len(rank_table) + 1)
        rank_table = rank_table[['Rank', 'country', 'value', 'change', 'change_pct']]
        rank_table.columns = ['Rank', 'Country', 'Current Value', 'YoY Change', 'Change %']
        
        # Format for display
        rank_table['Current Value'] = rank_table['Current Value'].round(2)
        rank_table['YoY Change'] = rank_table['YoY Change'].round(2)
        rank_table['Change %'] = rank_table['Change %'].round(1).astype(str) + '%'
        
        st.dataframe(rank_table, hide_index=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # How to read
    with st.expander("How to Interpret This Visualization"):
        st.markdown("""
        **Horizontal Bar Chart with Performance Thresholds**
        
        **Visual Elements:**
        - **Bar length**: Magnitude of inequality (GINI index)
        - **Bar color**: Performance category
          - Green: Low inequality (< 30) - Nordic levels
          - Blue: Moderate (30-35) - Well-performing
          - Orange: Medium-high (35-40) - Needs attention
          - Red: High inequality (> 40) - Critical levels
        - **Vertical dashed lines**: Category thresholds
        - **Numbers on bars**: Exact GINI values
        
        **Ranking Interpretation:**
        - **Top positions** (shorter bars): Best performers, more equal societies
        - **Bottom positions** (longer bars): Highest inequality, need intervention
        - **Year-over-year change**: Shows improvement (+) or deterioration (-)
        
        **Benchmark Interpretation:**
        - < 30: Very equal (comparable to Nordic countries)
        - 30-35: Equal (low inequality, sustainable)
        - 35-40: Moderate inequality (action recommended)
        - 40-45: High inequality (intervention needed)
        - > 45: Very high inequality (critical situation)
        """)

with col_insights2:
    st.markdown('<div class="section-header">Key Findings from Rankings</div>', unsafe_allow_html=True)
    
    # Filter insights relevant to rankings
    ranking_insights = [i for i in ranked_insights if i.get('insight_type') in ['rankings', 'comparisons', 'pareto']]
    
    if ranking_insights:
        for idx, insight in enumerate(ranking_insights[:5], 1):
            score = insight.get('score', 0)
            priority = "HIGH" if score >= 15 else "MEDIUM" if score >= 8 else "LOW"
            priority_class = f"insight-card-{priority.lower()}"
            badge_class = f"priority-{priority.lower()}"
            
            # Build confidence indicator
            confidence_html = ""
            if settings.get('show_confidence'):
                # For rankings, confidence is based on data quality
                completeness = insight.get('completeness_pct', 100)
                if completeness > 90:
                    confidence_html = '<span style="color: #10b981; font-size: 0.75rem;">● High Data Quality</span>'
                elif completeness > 70:
                    confidence_html = '<span style="color: #f59e0b; font-size: 0.75rem;">● Medium Quality</span>'
                else:
                    confidence_html = '<span style="color: #6b7280; font-size: 0.75rem;">● Limited Data</span>'
            
            st.markdown(f"""
            <div class="{priority_class}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span class="{badge_class}">#{idx} {priority}</span>
                    <span class="score-badge">Score: {score:.1f}</span>
                </div>
                <div style="color: #ffffff; font-weight: 600; margin-bottom: 8px; font-size: 1.05rem; line-height: 1.4;">
                    {insight.get('title', 'Insight')}
                </div>
                <div style="color: #e2e8f0; font-size: 0.92rem; line-height: 1.6; margin-bottom: 6px;">
                    {insight.get('narrative', '')}
                </div>
                {confidence_html}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No ranking insights generated. Adjust filters in sidebar to see more insights.")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# VISUALIZATION 3: ENHANCED DISTRIBUTION ANALYSIS
# ═══════════════════════════════════════════════════════════════════

st.markdown("## Distribution & Categorization Analysis")
st.caption("How countries are distributed across inequality categories")

col_chart3, col_insights3 = st.columns([1.3, 1])

with col_chart3:
    # Chart container removed to prevent empty box
    
    # Categorize countries
    latest_data = filtered_df[filtered_df['year'] == latest_year].copy()
    
    def categorize_detailed(value):
        if value < 30:
            return "Very Low (<30)"
        elif value < 35:
            return "Low (30-35)"
        elif value < 40:
            return "Moderate (35-40)"
        elif value < 45:
            return "High (40-45)"
        else:
            return "Very High (>45)"
    
    latest_data['category'] = latest_data['value'].apply(categorize_detailed)
    distribution = latest_data.groupby('category').agg({
        'country': 'count',
        'value': 'mean'
    }).reset_index()
    distribution.columns = ['Category', 'Count', 'Avg Value']
    
    # Create enhanced donut chart with two subplots
    from plotly.subplots import make_subplots
    
    fig_dist = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Distribution by Category', 'Average Values by Category'),
        specs=[[{'type': 'pie'}, {'type': 'bar'}]]
    )
    
    # Donut chart
    fig_dist.add_trace(go.Pie(
        labels=distribution['Category'],
        values=distribution['Count'],
        hole=0.5,
        marker=dict(colors=['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#991b1b']),
        textinfo='label+percent',
        textfont=dict(size=11),
        hovertemplate='<b>%{label}</b><br>Countries: %{value}<br>Percentage: %{percent}<extra></extra>'
    ), row=1, col=1)
    
    # Bar chart
    fig_dist.add_trace(go.Bar(
        x=distribution['Category'],
        y=distribution['Avg Value'],
        marker=dict(color=['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#991b1b']),
        text=distribution['Avg Value'].round(2),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Avg Value: %{y:.2f}<extra></extra>'
    ), row=1, col=2)
    
    fig_dist.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', size=10),
        showlegend=False,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    
    fig_dist.update_xaxes(tickangle=45, row=1, col=2)
    fig_dist.update_yaxes(title_text="Average GINI", row=1, col=2)
    
    st.plotly_chart(fig_dist, use_container_width=True, config={'displayModeBar': False})
    
    # Chart container closing div removed
    
    # Distribution statistics
    if settings.get('show_statistics') and len(distribution) > 0:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.markdown("**Distribution Statistics:**")
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            modal_category = distribution.loc[distribution['Count'].idxmax(), 'Category'] if len(distribution) > 0 else "N/A"
            st.metric("Modal Category", 
                     modal_category,
                     help="Most common category")
        with col_stat2:
            low_count = distribution[distribution['Category'].str.contains('Low|Very Low', na=False)]['Count'].sum() if len(distribution) > 0 else 0
            st.metric("Low Inequality", 
                     f"{int(low_count)} countries",
                     help="Countries with GINI < 35")
        with col_stat3:
            high_count = distribution[distribution['Category'].str.contains('High|Very High', na=False)]['Count'].sum() if len(distribution) > 0 else 0
            st.metric("High Inequality", 
                     f"{int(high_count)} countries",
                     delta="Needs Action",
                     help="Countries with GINI > 40")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # How to read
    with st.expander("How to Interpret This Visualization"):
        st.markdown("""
        **Dual Visualization: Distribution + Averages**
        
        **Left: Donut Chart (Distribution)**
        - **Slice size**: Number of countries in each category
        - **Colors**: Severity indicator
          - Green: Very Low/Low inequality (good)
          - Blue: Moderate (acceptable)
          - Orange: High (concerning)
          - Red/Dark Red: Very High (critical)
        - **Percentages**: Proportion of total countries
        
        **Right: Bar Chart (Category Averages)**
        - **Bar height**: Average GINI value for that category
        - **Colors**: Match donut chart categories
        - **Shows**: Typical value within each category
        
        **Interpretation:**
        - **Ideal distribution**: Most countries in green/blue categories
        - **Concerning pattern**: Most countries in orange/red
        - **Regional health**: Percentage in low inequality categories
        - **Inequality concentration**: Are values clustered or spread out?
        
        **Policy Implications:**
        - High % in red/orange → Regional intervention needed
        - Movement between categories → Track over time for progress
        - Outliers → Specific countries needing targeted support
        """)

with col_insights3:
    st.markdown('<div class="section-header">Key Findings from Distribution</div>', unsafe_allow_html=True)
    
    # Filter insights relevant to distribution
    dist_insights = [i for i in ranked_insights if i.get('insight_type') in ['statistics', 'anomalies']]
    
    if dist_insights:
        for idx, insight in enumerate(dist_insights[:5], 1):
            score = insight.get('score', 0)
            priority = "HIGH" if score >= 15 else "MEDIUM" if score >= 8 else "LOW"
            priority_class = f"insight-card-{priority.lower()}"
            badge_class = f"priority-{priority.lower()}"
            
            # Build confidence/anomaly indicator
            confidence_html = ""
            if insight.get('insight_type') == 'anomalies' and settings.get('show_statistics'):
                z_score = insight.get('z_score', 0)
                if abs(z_score) > 3:
                    confidence_html = '<span style="color: #ef4444; font-size: 0.75rem;">● Extreme Anomaly</span>'
                elif abs(z_score) > 2:
                    confidence_html = '<span style="color: #f59e0b; font-size: 0.75rem;">● Significant Anomaly</span>'
            
            st.markdown(f"""
            <div class="{priority_class}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span class="{badge_class}">#{idx} {priority}</span>
                    <span class="score-badge">Score: {score:.1f}</span>
                </div>
                <div style="color: #ffffff; font-weight: 600; margin-bottom: 8px; font-size: 1.05rem; line-height: 1.4;">
                    {insight.get('title', 'Insight')}
                </div>
                <div style="color: #e2e8f0; font-size: 0.92rem; line-height: 1.6; margin-bottom: 6px;">
                    {insight.get('narrative', '')}
                </div>
                {confidence_html}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No distribution insights generated. Adjust filters in sidebar to see more insights.")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# ALL INSIGHTS - TABBED INTERFACE
# ═══════════════════════════════════════════════════════════════════

st.markdown("## Complete Insights Repository")
st.caption("All generated insights organized by priority level")

if not ranked_insights:
    st.warning("No insights generated. Please enable insight types in the sidebar or adjust analysis settings.")
else:
    # Group by priority
    high_priority_insights = [i for i in ranked_insights if i.get('score', 0) >= 15]
    medium_priority_insights = [i for i in ranked_insights if 8 <= i.get('score', 0) < 15]
    low_priority_insights = [i for i in ranked_insights if i.get('score', 0) < 8]
    
    tab1, tab2, tab3, tab4 = st.tabs([
        f"Critical Priority ({len(high_priority_insights)})",
        f"Important Priority ({len(medium_priority_insights)})",
        f"Notable Patterns ({len(low_priority_insights)})",
        "Export & Reports"
    ])
    
    with tab1:
        st.markdown("### Critical Priority Insights")
        st.caption("These insights require immediate attention (Statistical significance + High magnitude)")
        
        if high_priority_insights:
            for idx, insight in enumerate(high_priority_insights, 1):
                score = insight.get('score', 0)
                
                # Enhanced statistical details
                stat_section = ""
                if settings.get('show_statistics'):
                    details = []
                    if insight.get('p_value') is not None:
                        details.append(f"p-value: {insight['p_value']:.4f}")
                    if insight.get('r_squared') is not None:
                        details.append(f"R²: {insight['r_squared']:.3f}")
                    if insight.get('change_relative') is not None:
                        details.append(f"Change: {insight['change_relative']:.1f}%")
                    if details:
                        stat_section = f'<div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(100,116,139,0.3); font-size: 0.85rem; color: #94a3b8;">{" | ".join(details)}</div>'
                
                st.markdown(f"""
                <div class="insight-card-high">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <span class="priority-high">CRITICAL #{idx}</span>
                        <span class="score-badge">Score: {score:.1f}/25</span>
                    </div>
                    <div style="color: #ffffff; font-weight: 700; margin-bottom: 10px; font-size: 1.15rem; line-height: 1.4;">
                        {insight.get('title', 'Insight')}
                    </div>
                    <div style="color: #e2e8f0; font-size: 0.95rem; line-height: 1.7; margin-bottom: 8px;">
                        {insight.get('narrative', '')}
                    </div>
                    {stat_section}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No critical priority insights found. This indicates generally stable conditions or limited variance in the data.")
    
    with tab2:
        st.markdown("### Important Priority Insights")
        st.caption("Significant patterns worth monitoring and consideration")
        
        if medium_priority_insights:
            for idx, insight in enumerate(medium_priority_insights, 1):
                score = insight.get('score', 0)
                
                stat_section = ""
                if settings.get('show_statistics'):
                    details = []
                    if insight.get('p_value') is not None:
                        details.append(f"p-value: {insight['p_value']:.4f}")
                    if insight.get('r_squared') is not None:
                        details.append(f"R²: {insight['r_squared']:.3f}")
                    if details:
                        stat_section = f'<div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(100,116,139,0.2); font-size: 0.82rem; color: #94a3b8;">{" | ".join(details)}</div>'
                
                st.markdown(f"""
                <div class="insight-card-medium">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span class="priority-medium">IMPORTANT #{idx}</span>
                        <span class="score-badge">Score: {score:.1f}/25</span>
                    </div>
                    <div style="color: #ffffff; font-weight: 600; margin-bottom: 8px; font-size: 1.05rem; line-height: 1.4;">
                        {insight.get('title', 'Insight')}
                    </div>
                    <div style="color: #e2e8f0; font-size: 0.92rem; line-height: 1.6; margin-bottom: 6px;">
                        {insight.get('narrative', '')}
                    </div>
                    {stat_section}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No important priority insights found.")
    
    with tab3:
        st.markdown("### Notable Patterns")
        st.caption("Additional observations and contextual information")
        
        if low_priority_insights:
            for idx, insight in enumerate(low_priority_insights, 1):
                score = insight.get('score', 0)
                
                st.markdown(f"""
                <div class="insight-card-low">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span class="priority-low">NOTABLE #{idx}</span>
                        <span class="score-badge">Score: {score:.1f}/25</span>
                    </div>
                    <div style="color: #ffffff; font-weight: 600; margin-bottom: 6px; font-size: 0.98rem;">
                        {insight.get('title', 'Insight')}
                    </div>
                    <div style="color: #e2e8f0; font-size: 0.88rem; line-height: 1.5;">
                        {insight.get('narrative', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No low priority insights found.")
    
    with tab4:
        st.markdown("### Export Analysis Reports")
        st.caption("Download insights in various formats for external use")
        
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("""
        **Export Options:**
        - **TXT**: Plain text format for basic documentation
        - **Markdown**: Formatted text for technical documentation
        - **CSV**: Structured data for spreadsheet analysis
        
        All exports include metadata, priority rankings, and statistical details.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        
        with col_exp1:
            export_text = format_insights_as_text(result, mode='ranked')
            st.download_button(
                label="Download Text Report",
                data=export_text,
                file_name=f"inequality_insights_{config['indicator']}_{latest_year}.txt",
                mime="text/plain",
                use_container_width=True,
                help="Plain text format with all insights"
            )
        
        with col_exp2:
            export_md = export_text.replace("=", "#")
            st.download_button(
                label="Download Markdown",
                data=export_md,
                file_name=f"inequality_insights_{config['indicator']}_{latest_year}.md",
                mime="text/markdown",
                use_container_width=True,
                help="Markdown format for documentation"
            )
        
        with col_exp3:
            if ranked_insights:
                insights_df = pd.DataFrame([{
                    'Priority': "CRITICAL" if i.get('score', 0) >= 15 else "IMPORTANT" if i.get('score', 0) >= 8 else "NOTABLE",
                    'Score': round(i.get('score', 0), 2),
                    'Title': i.get('title', ''),
                    'Description': i.get('narrative', ''),
                    'Type': i.get('insight_type', ''),
                    'P-Value': round(i.get('p_value', 1), 4) if i.get('p_value') is not None else 'N/A',
                    'R-Squared': round(i.get('r_squared', 0), 3) if i.get('r_squared') is not None else 'N/A'
                } for i in ranked_insights])
                
                csv = insights_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV Data",
                    data=csv,
                    file_name=f"inequality_insights_{config['indicator']}_{latest_year}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    help="CSV format for spreadsheet analysis"
                )
        
        st.markdown("")
        
        # Export summary
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.markdown(f"""
        **Export Summary:**
        - Analysis period: {config['year_range'][0]} - {config['year_range'][1]}
        - Countries analyzed: {metadata.get('countries_analyzed', 0)}
        - Total insights: {metadata.get('total_generated', 0)}
        - Critical priority: {len(high_priority_insights)}
        - Important priority: {len(medium_priority_insights)}
        - Notable patterns: {len(low_priority_insights)}
        - Analysis mode: {settings.get('analysis_depth', 'Unknown')}
        - Focus mode: {"Enabled" if settings.get('focus_mode') else "Disabled"}
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# ENHANCED FOOTER
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")

st.markdown("""
<div style="margin-top: 24px; padding: 20px; background: linear-gradient(135deg, #0f1419, #1a1f2e); 
            border-radius: 12px; border-left: 4px solid #8b5cf6;">
    <h4 style="color: #8b5cf6; margin-top: 0; margin-bottom: 12px; font-size: 1.1rem;">About This Analysis</h4>
    <p style="color: #e2e8f0; font-size: 0.9rem; margin: 0; line-height: 1.7;">
        <strong>Statistical Engine:</strong> Insights are automatically generated using advanced statistical 
        algorithms including linear regression, Z-score anomaly detection, coefficient of variation analysis, and 
        trend decomposition. Each insight is scored (0-25 points) based on multiple factors: statistical significance 
        (p < 0.05), magnitude of change (>20%), data quality (>80% completeness), model fit (R² > 0.7), and temporal recency.
    </p>
    <p style="color: #94a3b8; font-size: 0.85rem; margin: 12px 0 0 0; line-height: 1.6;">
        <strong>Confidence Indicators:</strong> High confidence requires p < 0.05 and R² > 0.5. Medium confidence requires 
        p < 0.1. All statistical tests use 95% confidence intervals. Trend analysis employs ordinary least squares regression. 
        Anomalies detected using Z-score > 2.0 threshold (2 standard deviations).
    </p>
    <p style="color: #94a3b8; font-size: 0.85rem; margin: 8px 0 0 0;">
        <strong>Customization:</strong> Use sidebar controls to adjust analysis depth, filter insight types, enable focus 
        mode for deep dives, and toggle statistical details. Priority rankings dynamically update based on your selections.
    </p>
</div>
""", unsafe_allow_html=True)