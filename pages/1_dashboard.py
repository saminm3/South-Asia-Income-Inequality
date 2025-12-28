import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
from pathlib import Path
import numpy as np

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.loaders import load_inequality_data
from utils.utils import human_indicator, format_value
from utils.exports import export_data_menu, export_plot_menu

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════════
# GOOGLE ANALYTICS INSPIRED DARK THEME
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* Main background - Dark navy matching the screenshot */
    .main {
        background: #1a1f3a;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 100%;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Metric cards - matching screenshot style */
    div[data-testid="metric-container"] {
        background: #0f1419;
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }
    
    div[data-testid="metric-container"] > label {
        color: #94a3b8 !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    div[data-testid="metric-container"] > div {
        color: #ffffff !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-size: 0.875rem !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Selectbox styling */
    div[data-baseweb="select"] {
        background: rgba(20, 25, 45, 0.6) !important;
        border-radius: 8px !important;
    }
    
    /* Text color */
    p, span, div {
        color: #e2e8f0;
    }
    
    /* Chart containers */
    .chart-container {
        background: #0f1419;
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 20, 25, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(100, 116, 139, 0.5);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(100, 116, 139, 0.8);
    }
    
    /* Custom card styles */
    .stat-card {
        background: #0f1419;
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        margin: 10px 0;
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }
    
    .trend-positive {
        color: #10b981;
    }
    
    .trend-negative {
        color: #ef4444;
    }
    
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
        margin: 30px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(100, 116, 139, 0.2);
    }
</style>
""", unsafe_allow_html=True)

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
# KEY METRICS ROW (Google Analytics inspired)
# ═══════════════════════════════════════════════════════════════════

latest_year = int(filtered_df['year'].max())
latest_data = filtered_df[filtered_df['year'] == latest_year].copy()
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

# Best and worst performers
best_country = latest_data.loc[latest_data['value'].idxmin(), 'country'] if not latest_data.empty else "N/A"
worst_country = latest_data.loc[latest_data['value'].idxmax(), 'country'] if not latest_data.empty else "N/A"
data_coverage = (filtered_df.notna().sum()['value'] / len(filtered_df) * 100)

col1, col2, col3, col4, col5= st.columns(5)

with col1:
    # Regional Average - clean style
    delta_color = "#10b981" if yoy_pct < 0 else "#ef4444"
    delta_symbol = "↓" if yoy_pct < 0 else "↑"
    
    st.metric(
        label="Regional Average",
        value=f"{regional_avg:.1f}",
        delta=f"{delta_symbol} {abs(yoy_pct):.1f}%"
    )

with col2:
    # Best Performer - clean style
    best_value = latest_data['value'].min() if not latest_data.empty else 0
    
    st.metric(
        label="Best Performer",
        value=best_country,
        delta=f"↑ {best_value:.1f}"
    )

with col3:
    # Needs Attention - clean style
    worst_value = latest_data['value'].max() if not latest_data.empty else 0
    
    st.metric(
        label="Needs Attention",
        value=worst_country,
        delta=f"↑ {worst_value:.1f}",
        delta_color="inverse"
    )

with col4:
    # Data Coverage - clean style
    st.metric(
        label="Data Coverage",
        value=f"{data_coverage:.0f}%",
        delta=f"↑ {int(data_coverage - 50)} points" if data_coverage > 50 else f"↓ {int(50 - data_coverage)} points"
    )

with col5:
    st.metric(
        label="Data Range",
        value=f"{config['year_range'][1] - config['year_range'][0] + 1} Years"
    )
# ═══════════════════════════════════════════════════════════════════
# MAIN VISUALIZATION SECTION
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<div style="margin: 40px 0 20px 0;">
    <h2 style="font-size: 1rem; font-weight: 700; color: #ffffff; text-transform: uppercase; letter-spacing: 1px;">
        Inequality Trends Over Time
    </h2>
</div>
""", unsafe_allow_html=True)

# Main area chart - Google Analytics style
yearly_data = filtered_df.pivot_table(
    values='value',
    index='year',
    columns='country',
    aggfunc='mean'
).fillna(method='ffill')

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
        fillcolor=f'rgba({int(colors[i % len(colors)][1:3], 16)}, {int(colors[i % len(colors)][3:5], 16)}, {int(colors[i % len(colors)][5:7], 16)}, 0.2)',
        stackgroup='one',
        hovertemplate='<b>%{fullData.name}</b><br>Year: %{x}<br>Value: %{y:.2f}<extra></extra>'
    ))

fig_area.update_layout(
    height=400,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#e2e8f0', size=12),
    xaxis=dict(
        showgrid=True,
        gridcolor='rgba(100, 116, 139, 0.2)',
        title='Year',
        color='#94a3b8'
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='rgba(100, 116, 139, 0.2)',
        title='Value',
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
    margin=dict(l=60, r=20, t=60, b=40),
    hovermode='x unified'
)

st.plotly_chart(fig_area, use_container_width=True, config={'displayModeBar': False})
export_plot_menu(fig_area, f"temporal_trends_{config['indicator']}", key="area_chart")

# ═══════════════════════════════════════════════════════════════════
# SECONDARY VISUALIZATIONS ROW
# ═══════════════════════════════════════════════════════════════════

st.markdown('<div class="section-header">Country Comparison & Distribution</div>', unsafe_allow_html=True)

col_viz1, col_viz2 = st.columns([1.5, 1])

with col_viz1:
    # Horizontal bar chart - Browser breakdown style
    country_avg = filtered_df.groupby('country')['value'].mean().sort_values(ascending=True)
    
    fig_bars = go.Figure()
    
    fig_bars.add_trace(go.Bar(
        y=country_avg.index,
        x=country_avg.values,
        orientation='h',
        marker=dict(
            color=country_avg.values,
            colorscale='RdYlGn_r',  # Red (bad) to Green (good) reversed
            showscale=False,
            line=dict(width=0)
        ),
        text=[f'{v:.2f}' for v in country_avg.values],
        textposition='outside',
        textfont=dict(color='#ffffff', size=11),
        hovertemplate='<b>%{y}</b><br>Average: %{x:.2f}<extra></extra>'
    ))
    
    fig_bars.update_layout(
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', size=12),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 116, 139, 0.2)',
            title='Average Value',
            color='#94a3b8'
        ),
        yaxis=dict(
            showgrid=False,
            title='Country',
            color='#e2e8f0'
        ),
        margin=dict(l=100, r=60, t=20, b=40),
        title=dict(
            text='Average by Country',
            font=dict(size=14, color='#ffffff'),
            x=0
        )
    )
    
    st.plotly_chart(fig_bars, use_container_width=True, config={'displayModeBar': False})
    export_plot_menu(fig_bars, f"average_by_country_{config['indicator']}", key="bar_chart")

with col_viz2:
    # Donut chart - Traffic source style
    # Categorize countries by performance
    median_val = latest_data['value'].median()
    q1 = latest_data['value'].quantile(0.33)
    q3 = latest_data['value'].quantile(0.67)
    
    categories = []
    for val in latest_data['value']:
        if val <= q1:
            categories.append('Low Inequality')
        elif val <= q3:
            categories.append('Moderate')
        else:
            categories.append('High Inequality')
    
    category_counts = pd.Series(categories).value_counts()
    
    fig_donut = go.Figure(data=[go.Pie(
        labels=category_counts.index,
        values=category_counts.values,
        hole=0.6,
        marker=dict(
            colors=['#10b981', '#f59e0b', '#ef4444'],
            line=dict(color='#0a0e27', width=2)
        ),
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(color='#ffffff', size=11),
        hovertemplate='<b>%{label}</b><br>Countries: %{value}<br>%{percent}<extra></extra>'
    )])
    
    fig_donut.update_layout(
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
        title=dict(
            text='Distribution',
            font=dict(size=14, color='#ffffff'),
            x=0.5,
            xanchor='center'
        ),
        annotations=[dict(
            text=f'<b>{len(latest_data)}</b><br>Countries',
            x=0.5, y=0.5,
            font=dict(size=16, color='#ffffff'),
            showarrow=False
        )]
    )
    
    st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})
    export_plot_menu(fig_donut, "distribution_breakdown", key="donut_chart")

# ═══════════════════════════════════════════════════════════════════
# BOTTOM SECTION: Rankings & Timeline
# ═══════════════════════════════════════════════════════════════════

st.markdown('<div class="section-header">Detailed Rankings & Individual Trends</div>', unsafe_allow_html=True)

col_bottom1, col_bottom2 = st.columns([1, 1.5])

with col_bottom1:
    # Rankings list with gradient bars
    st.markdown("""
    <div style="margin-bottom: 15px;">
        <h3 style="font-size: 1rem; color: #ffffff; font-weight: 600; margin: 0;">
            Current Rankings (Latest Year)
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    rankings = latest_data.sort_values('value').reset_index(drop=True)
    
    for idx, row in rankings.iterrows():
        rank = idx + 1
        country = row['country']
        value = row['value']
        pct_of_max = (value / rankings['value'].max()) * 100
        
        # Color based on rank
        if rank == 1:
            bar_color = '#10b981'  # Green
            rank_icon = '🥇'
        elif rank == 2:
            bar_color = '#3b82f6'  # Blue
            rank_icon = '🥈'
        elif rank == 3:
            bar_color = '#8b5cf6'  # Purple
            rank_icon = '🥉'
        else:
            bar_color = '#64748b'  # Gray
            rank_icon = f'{rank}.'
        
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
    # Individual country trends
    st.markdown("""
    <div style="margin-bottom: 15px;">
        <h3 style="font-size: 1rem; color: #ffffff; font-weight: 600; margin: 0;">
            Individual Country Trends
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
    
    fig_lines.update_layout(
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', size=12),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 116, 139, 0.2)',
            title='Year',
            color='#94a3b8'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 116, 139, 0.2)',
            title=human_indicator(config['indicator']),
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
            font=dict(color='#e2e8f0', size=10)
        ),
        margin=dict(l=60, r=120, t=20, b=40),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_lines, use_container_width=True, config={'displayModeBar': False})
    export_plot_menu(fig_lines, "individual_trends", key="line_chart")

# ═══════════════════════════════════════════════════════════════════
# FOOTER INSIGHTS
# ═══════════════════════════════════════════════════════════════════

st.markdown('<div class="section-header">Key Insights & Raw Data</div>', unsafe_allow_html=True)

col_insight1, col_insight2, col_insight3 = st.columns(3)

with col_insight1:
    trend_direction = "improving" if yoy_pct < 0 else "worsening"
    trend_icon = "📉" if yoy_pct < 0 else "📈"
    
    st.markdown(f"""
    <div class="stat-card">
        <div style="font-size: 2rem; margin-bottom: 10px;">{trend_icon}</div>
        <div style="font-size: 0.875rem; color: #94a3b8; margin-bottom: 8px;">REGIONAL TREND</div>
        <div style="font-size: 1.1rem; color: #ffffff; font-weight: 600;">
            Inequality is {trend_direction}
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
        <div style="font-size: 2rem; margin-bottom: 10px;">📊</div>
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
    
    st.markdown(f"""
    <div class="stat-card">
        <div style="font-size: 2rem; margin-bottom: 10px;">🌓</div>
        <div style="font-size: 0.875rem; color: #94a3b8; margin-bottom: 8px;">REGIONAL GAP</div>
        <div style="font-size: 1.1rem; color: #ffffff; font-weight: 600;">
            {gap:.2f} points
        </div>
        <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 8px;">
            Between best and worst
        </div>
    </div>
    """, unsafe_allow_html=True)

# Raw data and export
with st.expander("📝 View Raw Data & Export Options"):
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    export_data_menu(filtered_df, "dashboard_data_export", key="dashboard_data")

st.markdown("---")
st.caption("Dashboard | South Asia Inequality Analysis Platform")