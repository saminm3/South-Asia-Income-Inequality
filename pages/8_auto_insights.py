import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

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
# PAGE CONFIG - SIDEBAR ENABLED
# ═══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Auto Insights | South Asia Inequality",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════
# THEME & STYLING
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    .main {background: #1a1f3a;}
    .block-container {padding-top: 2rem; padding-bottom: 2rem; padding-left: 3rem; padding-right: 3rem; max-width: 100%;}
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    h1, h2, h3, h4 {color: #ffffff !important; font-weight: 600 !important;}
    p, span, div, label {color: #e2e8f0;}
    
    /* Insight cards */
    .insight-card {
        background: #0f1419;
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }
    
    .insight-card-high {
        border-color: rgba(16, 185, 129, 0.6);
        border-width: 2px;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), #0f1419);
    }
    
    .insight-card-medium {
        border-color: rgba(59, 130, 246, 0.6);
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), #0f1419);
    }
    
    /* Chart container */
    .chart-container {
        background: #0f1419;
        border: 1px solid rgba(100, 116, 139, 0.3);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
    }
    
    /* Priority badge */
    .priority-high {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
    }
    
    .priority-medium {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
    }
    
    .priority-low {
        background: linear-gradient(135deg, #6b7280, #4b5563);
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
    }
    
    /* Section headers */
    .section-header {
        color: #3b82f6;
        font-weight: 700;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
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

ensure_config(df)
config = st.session_state.analysis_config

# Initialize insight settings
if 'insight_settings' not in st.session_state:
    st.session_state.insight_settings = {
        'enabled_types': list(INSIGHT_TYPES.keys()) if INSIGHT_TYPES else [],
        'focus_mode': False,
        'max_insights': 15,
        'analysis_depth': 'Detailed Analysis'
    }

# ═══════════════════════════════════════════════════════════════════
# SIDEBAR - CONTROLS
# ═══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("# Analysis Controls")
    st.markdown("---")
    
    settings = st.session_state.insight_settings
    
    # Analysis Depth
    st.markdown("### Analysis Depth")
    depth = st.radio(
        "How detailed should the analysis be?",
        ["Quick Overview", "Detailed Analysis", "Expert Mode"],
        index=1
    )
    settings['analysis_depth'] = depth
    
    if depth == "Quick Overview":
        settings['max_insights'] = 8
        st.info("Top 8 insights, simple explanations")
    elif depth == "Detailed Analysis":
        settings['max_insights'] = 15
        st.info("Top 15 insights, balanced detail")
    else:
        settings['max_insights'] = 25
        st.info("Top 25 insights, full technical depth")
    
    st.markdown("---")
    
    # Insight Type Filters
    st.markdown("### Insight Types")
    st.caption("Filter by insight category")
    
    available_types = list(INSIGHT_TYPES.keys()) if INSIGHT_TYPES else ['trends', 'rankings', 'anomalies']
    
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
    st.markdown("### Focus Mode")
    focus_mode = st.checkbox(
        "Deep dive (2-3 countries only)",
        value=settings.get('focus_mode', False),
        help="Analyze fewer countries in greater depth"
    )
    settings['focus_mode'] = focus_mode
    
    if focus_mode:
        st.success("Deep analysis mode active")
    
    st.markdown("---")
    
    # Reset button
    if st.button("Reset All Settings", use_container_width=True):
        st.session_state.insight_settings = {
            'enabled_types': available_types,
            'focus_mode': False,
            'max_insights': 15,
            'analysis_depth': 'Detailed Analysis'
        }
        st.rerun()

# ═══════════════════════════════════════════════════════════════════
# TOP NAVIGATION
# ═══════════════════════════════════════════════════════════════════

col_nav1, col_nav2, col_nav3 = st.columns([6, 1, 1])

with col_nav2:
    if st.button("Home", use_container_width=True):
        st.switch_page("home.py")

with col_nav3:
    if st.button("Dashboard", use_container_width=True):
        st.switch_page("pages/1_dashboard.py")

# ═══════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<div style="margin-bottom: 2rem;">
    <h1 style="font-size: 2.5rem; margin: 0; background: linear-gradient(135deg, #8b5cf6, #3b82f6); 
               -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        Auto Insights Pro
    </h1>
    <p style="color: #94a3b8; font-size: 1rem; margin-top: 0.5rem;">
        AI-powered analysis with visualizations and statistical insights
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

# ═══════════════════════════════════════════════════════════════════
# SUMMARY METRICS
# ═══════════════════════════════════════════════════════════════════

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Insights Generated", metadata.get('total_generated', 0))

with col2:
    st.metric("Showing Top", metadata.get('total_shown', 0))

with col3:
    st.metric("Countries Analyzed", metadata.get('countries_analyzed', 0))

with col4:
    high_priority = len([i for i in ranked_insights if i.get('score', 0) >= 15])
    st.metric("High Priority", high_priority)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# VISUALIZATION 1: INEQUALITY TRENDS (with insights)
# ═══════════════════════════════════════════════════════════════════

st.markdown("## Inequality Trends Over Time")

col_chart1, col_insights1 = st.columns([1.2, 1])

with col_chart1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    # Create streamgraph
    fig_trends = go.Figure()
    
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
                hovertemplate='<b>%{fullData.name}</b><br>Year: %{x}<br>Value: %{y:.2f}<extra></extra>'
            ))
    
    fig_trends.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 116, 139, 0.2)',
            title='Year'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 116, 139, 0.2)',
            title=human_indicator(config['indicator'])
        ),
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        margin=dict(l=0, r=150, t=20, b=0)
    )
    
    st.plotly_chart(fig_trends, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # How to read
    with st.expander("How to Read This Chart"):
        st.markdown("""
        **Stacked Area Chart (Streamgraph)**
        
        - **Each colored layer** represents one country
        - **Width of layer** shows the magnitude of inequality
        - **Overall height** shows regional total/average
        - **Upward trend** indicates worsening inequality
        - **Downward trend** indicates improving equality
        
        **What to Look For:**
        - Layers crossing (countries changing positions)
        - Wide gaps (high divergence between countries)
        - Converging layers (regional convergence)
        - Sudden spikes (policy changes, crises)
        """)

with col_insights1:
    st.markdown('<div class="section-header">Key Insights from This Chart</div>', unsafe_allow_html=True)
    
    # Filter insights relevant to trends
    trend_insights = [i for i in ranked_insights if i.get('insight_type') in ['trends', 'indexed_trends']]
    
    for idx, insight in enumerate(trend_insights[:4], 1):
        score = insight.get('score', 0)
        priority = "HIGH" if score >= 15 else "MEDIUM" if score >= 8 else "LOW"
        priority_class = f"priority-{priority.lower()}"
        color = "#10b981" if priority == "HIGH" else "#3b82f6" if priority == "MEDIUM" else "#6b7280"
        
        st.markdown(f"""
        <div class="insight-card insight-card-{priority.lower()}">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span class="{priority_class}">{priority} PRIORITY</span>
                <span style="color: #94a3b8; font-size: 0.75rem;">Score: {score:.1f}</span>
            </div>
            <div style="color: #ffffff; font-weight: 600; margin-bottom: 6px; font-size: 1.05rem;">
                {insight.get('title', 'Insight')}
            </div>
            <div style="color: #e2e8f0; font-size: 0.9rem; line-height: 1.5;">
                {insight.get('narrative', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if not trend_insights:
        st.info("No trend insights generated for current settings")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# VISUALIZATION 2: COUNTRY RANKINGS (with insights)
# ═══════════════════════════════════════════════════════════════════

st.markdown("## Country Rankings (Latest Year)")

col_chart2, col_insights2 = st.columns([1.2, 1])

with col_chart2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    # Get latest year data
    latest_year = config['year_range'][1]
    latest_data = filtered_df[filtered_df['year'] == latest_year].sort_values('value')
    
    # Create horizontal bar chart
    fig_ranking = go.Figure(go.Bar(
        y=latest_data['country'],
        x=latest_data['value'],
        orientation='h',
        marker=dict(
            color=latest_data['value'],
            colorscale='RdYlGn_r',
            showscale=False
        ),
        hovertemplate='<b>%{y}</b><br>Value: %{x:.2f}<extra></extra>'
    ))
    
    fig_ranking.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 116, 139, 0.2)',
            title=human_indicator(config['indicator'])
        ),
        yaxis=dict(
            showgrid=False,
            title=''
        ),
        margin=dict(l=0, r=0, t=20, b=0)
    )
    
    st.plotly_chart(fig_ranking, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # How to read
    with st.expander("How to Read This Chart"):
        st.markdown("""
        **Horizontal Bar Chart (Rankings)**
        
        - **Each bar** represents one country
        - **Length of bar** shows the value of the metric
        - **Sorted** from best to worst performers
        - **Color gradient** helps distinguish values
        
        **For GINI Index (Lower is Better):**
        - Shorter bars = Lower inequality (GOOD)
        - Longer bars = Higher inequality (NEEDS ATTENTION)
        - Gaps between bars show magnitude of differences
        
        **Benchmarks:**
        - Below 30: Very equal
        - 30-35: Equal (Low inequality)
        - 35-40: Moderate inequality
        - 40-45: High inequality
        - Above 45: Very high inequality
        """)

with col_insights2:
    st.markdown('<div class="section-header">Key Insights from This Chart</div>', unsafe_allow_html=True)
    
    # Filter insights relevant to rankings
    ranking_insights = [i for i in ranked_insights if i.get('insight_type') in ['rankings', 'comparisons']]
    
    for idx, insight in enumerate(ranking_insights[:4], 1):
        score = insight.get('score', 0)
        priority = "HIGH" if score >= 15 else "MEDIUM" if score >= 8 else "LOW"
        priority_class = f"priority-{priority.lower()}"
        
        st.markdown(f"""
        <div class="insight-card insight-card-{priority.lower()}">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span class="{priority_class}">{priority} PRIORITY</span>
                <span style="color: #94a3b8; font-size: 0.75rem;">Score: {score:.1f}</span>
            </div>
            <div style="color: #ffffff; font-weight: 600; margin-bottom: 6px; font-size: 1.05rem;">
                {insight.get('title', 'Insight')}
            </div>
            <div style="color: #e2e8f0; font-size: 0.9rem; line-height: 1.5;">
                {insight.get('narrative', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if not ranking_insights:
        st.info("No ranking insights generated for current settings")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# VISUALIZATION 3: DISTRIBUTION ANALYSIS (with insights)
# ═══════════════════════════════════════════════════════════════════

st.markdown("## Distribution Analysis")

col_chart3, col_insights3 = st.columns([1.2, 1])

with col_chart3:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    # Categorize countries by inequality level
    latest_data = filtered_df[filtered_df['year'] == latest_year].copy()
    
    def categorize_gini(value):
        if value < 35:
            return "Low Inequality"
        elif value < 40:
            return "Medium Inequality"
        else:
            return "High Inequality"
    
    latest_data['category'] = latest_data['value'].apply(categorize_gini)
    distribution = latest_data['category'].value_counts()
    
    # Create donut chart
    fig_dist = go.Figure(go.Pie(
        labels=distribution.index,
        values=distribution.values,
        hole=0.5,
        marker=dict(colors=['#10b981', '#f59e0b', '#ef4444']),
        hovertemplate='<b>%{label}</b><br>Countries: %{value}<br>Percentage: %{percent}<extra></extra>'
    ))
    
    fig_dist.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=0, r=0, t=20, b=80)
    )
    
    st.plotly_chart(fig_dist, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # How to read
    with st.expander("How to Read This Chart"):
        st.markdown("""
        **Donut Chart (Distribution)**
        
        - **Each slice** represents one category
        - **Slice size** shows number of countries
        - **Center hole** emphasizes proportions
        - **Colors** indicate severity levels
        
        **Categories (for GINI):**
        - **Green (Low)**: Below 35 - Relatively equal societies
        - **Yellow (Medium)**: 35-40 - Moderate inequality
        - **Red (High)**: Above 40 - High inequality, action needed
        
        **What to Look For:**
        - Which category has most countries?
        - Is the region mostly low, medium, or high?
        - Any countries in extreme categories?
        """)

with col_insights3:
    st.markdown('<div class="section-header">Key Insights from This Chart</div>', unsafe_allow_html=True)
    
    # Filter insights relevant to distribution
    dist_insights = [i for i in ranked_insights if i.get('insight_type') in ['pareto', 'statistics', 'comparisons']]
    
    for idx, insight in enumerate(dist_insights[:4], 1):
        score = insight.get('score', 0)
        priority = "HIGH" if score >= 15 else "MEDIUM" if score >= 8 else "LOW"
        priority_class = f"priority-{priority.lower()}"
        
        st.markdown(f"""
        <div class="insight-card insight-card-{priority.lower()}">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span class="{priority_class}">{priority} PRIORITY</span>
                <span style="color: #94a3b8; font-size: 0.75rem;">Score: {score:.1f}</span>
            </div>
            <div style="color: #ffffff; font-weight: 600; margin-bottom: 6px; font-size: 1.05rem;">
                {insight.get('title', 'Insight')}
            </div>
            <div style="color: #e2e8f0; font-size: 0.9rem; line-height: 1.5;">
                {insight.get('narrative', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if not dist_insights:
        st.info("No distribution insights generated for current settings")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# ALL INSIGHTS SECTION
# ═══════════════════════════════════════════════════════════════════

st.markdown("## All Generated Insights")

if not ranked_insights:
    st.warning("No insights generated. Try adjusting your filters in the sidebar.")
else:
    # Group by priority
    high_priority_insights = [i for i in ranked_insights if i.get('score', 0) >= 15]
    medium_priority_insights = [i for i in ranked_insights if 8 <= i.get('score', 0) < 15]
    low_priority_insights = [i for i in ranked_insights if i.get('score', 0) < 8]
    
    tab1, tab2, tab3, tab4 = st.tabs(["High Priority", "Medium Priority", "Low Priority", "Export"])
    
    with tab1:
        if high_priority_insights:
            for idx, insight in enumerate(high_priority_insights, 1):
                score = insight.get('score', 0)
                st.markdown(f"""
                <div class="insight-card insight-card-high">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span class="priority-high">HIGH PRIORITY #{idx}</span>
                        <span style="color: #94a3b8; font-size: 0.75rem;">Score: {score:.1f}</span>
                    </div>
                    <div style="color: #ffffff; font-weight: 600; margin-bottom: 6px; font-size: 1.1rem;">
                        {insight.get('title', 'Insight')}
                    </div>
                    <div style="color: #e2e8f0; font-size: 0.95rem; line-height: 1.6;">
                        {insight.get('narrative', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No high priority insights found")
    
    with tab2:
        if medium_priority_insights:
            for idx, insight in enumerate(medium_priority_insights, 1):
                score = insight.get('score', 0)
                st.markdown(f"""
                <div class="insight-card insight-card-medium">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span class="priority-medium">MEDIUM PRIORITY #{idx}</span>
                        <span style="color: #94a3b8; font-size: 0.75rem;">Score: {score:.1f}</span>
                    </div>
                    <div style="color: #ffffff; font-weight: 600; margin-bottom: 6px; font-size: 1.05rem;">
                        {insight.get('title', 'Insight')}
                    </div>
                    <div style="color: #e2e8f0; font-size: 0.9rem; line-height: 1.5;">
                        {insight.get('narrative', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No medium priority insights found")
    
    with tab3:
        if low_priority_insights:
            for idx, insight in enumerate(low_priority_insights, 1):
                score = insight.get('score', 0)
                st.markdown(f"""
                <div class="insight-card">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span class="priority-low">LOW PRIORITY #{idx}</span>
                        <span style="color: #94a3b8; font-size: 0.75rem;">Score: {score:.1f}</span>
                    </div>
                    <div style="color: #ffffff; font-weight: 600; margin-bottom: 6px;">
                        {insight.get('title', 'Insight')}
                    </div>
                    <div style="color: #e2e8f0; font-size: 0.9rem;">
                        {insight.get('narrative', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No low priority insights found")
    
    with tab4:
        st.markdown("### Export Options")
        
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        
        with col_exp1:
            export_text = format_insights_as_text(result, mode='ranked')
            st.download_button(
                label="Download as TXT",
                data=export_text,
                file_name=f"inequality_insights_{config['indicator']}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col_exp2:
            export_md = export_text.replace("=", "#")
            st.download_button(
                label="Download as Markdown",
                data=export_md,
                file_name=f"inequality_insights_{config['indicator']}.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        with col_exp3:
            if ranked_insights:
                insights_df = pd.DataFrame([{
                    'Priority': "HIGH" if i.get('score', 0) >= 15 else "MEDIUM" if i.get('score', 0) >= 8 else "LOW",
                    'Score': i.get('score', 0),
                    'Title': i.get('title', ''),
                    'Description': i.get('narrative', ''),
                    'Type': i.get('insight_type', '')
                } for i in ranked_insights])
                
                csv = insights_df.to_csv(index=False)
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name=f"inequality_insights_{config['indicator']}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

# ═══════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════

st.divider()

st.markdown("""
<div style="padding: 16px; background: #0f1419; border-radius: 8px; border-left: 3px solid #8b5cf6;">
    <p style="color: #e2e8f0; font-size: 0.85rem; margin: 0; line-height: 1.5;">
        <strong>AI-Powered Analysis:</strong> Insights are automatically generated using statistical algorithms 
        (linear regression, Z-score analysis, coefficient of variation) and ranked by probability of interest. 
        Scoring considers: statistical significance (p < 0.05), magnitude (>20% change), data quality (>80% complete), 
        anomalies (Z-score > 2.0), and recency.
    </p>
</div>
""", unsafe_allow_html=True)