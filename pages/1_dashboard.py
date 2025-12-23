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
from utils.utils import human_indicator

# Page config
st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ultra-modern dark theme CSS (Google Analytics style)
st.markdown("""
<style>
    /* Main dark gradient background */
    .main {
        background: linear-gradient(180deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
    }
    
    /* Remove padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 100%;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom metric cards with gradient */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(236, 72, 153, 0.1) 100%);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(10px);
    }
    
    /* Metric labels */
    div[data-testid="metric-container"] label {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    /* Metric values */
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        text-shadow: 0 2px 10px rgba(139, 92, 246, 0.3);
    }
    
    /* Delta values */
    div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-size: 1rem !important;
        font-weight: 600 !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }
    
    /* Section headers */
    .section-header {
        color: #e2e8f0;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 1rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 20, 25, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(139, 92, 246, 0.5);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(139, 92, 246, 0.8);
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
    st.error("No data available")
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
    st.warning("No data available")
    st.stop()

# ═══════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<div style="margin-bottom: 2rem;">
    <h1 style="font-size: 2.5rem; margin: 0; background: linear-gradient(90deg, #8b5cf6 0%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
        South Asia Inequality Analytics
    </h1>
    <p style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.5rem;">Real-time inequality monitoring & insights</p>
</div>
""", unsafe_allow_html=True)

# Calculate metrics
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

# ═══════════════════════════════════════════════════════════════════
# TOP METRICS ROW (Google Analytics style)
# ═══════════════════════════════════════════════════════════════════

col1, col2, col3, col4 = st.columns(4)

with col1:
    # Create mini sparkline for trend
    recent_trend = filtered_df.groupby('year')['value'].mean().tail(10)
    
    fig_spark1 = go.Figure()
    fig_spark1.add_trace(go.Scatter(
        x=recent_trend.index,
        y=recent_trend.values,
        mode='lines',
        fill='tozeroy',
        line=dict(color='#8b5cf6', width=2),
        fillcolor='rgba(139, 92, 246, 0.3)',
        showlegend=False
    ))
    fig_spark1.update_layout(
        height=80,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    
    st.metric(
        label="Regional Average",
        value=f"{regional_avg:.1f}",
        delta=f"{yoy_pct:+.1f}%"
    )
    st.plotly_chart(fig_spark1, use_container_width=True, config={'displayModeBar': False})

with col2:
    best_country = latest_data.loc[latest_data['value'].idxmin(), 'country']
    best_value = latest_data['value'].min()
    
    st.metric(
        label="Best Performer",
        value=best_country,
        delta=f"{best_value:.1f}"
    )
    st.markdown(f"""
    <div style="height: 80px; display: flex; align-items: center; justify-content: center;">
        <div style="font-size: 4rem; opacity: 0.3;">🏆</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    worst_country = latest_data.loc[latest_data['value'].idxmax(), 'country']
    worst_value = latest_data['value'].max()
    
    st.metric(
        label="Needs Attention",
        value=worst_country,
        delta=f"{worst_value:.1f}",
        delta_color="inverse"
    )
    st.markdown(f"""
    <div style="height: 80px; display: flex; align-items: center; justify-content: center;">
        <div style="font-size: 4rem; opacity: 0.3;">⚠️</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    data_points = len(filtered_df)
    coverage = (len(filtered_df) / (len(config['countries']) * (config['year_range'][1] - config['year_range'][0] + 1)) * 100)
    
    st.metric(
        label="Data Coverage",
        value=f"{coverage:.0f}%",
        delta=f"{data_points} points"
    )
    
    # Coverage gauge (FIXED - removed invalid font size)
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge",  # Removed "+number" since we don't want to show it
        value=coverage,
        gauge={
            'axis': {'range': [0, 100], 'visible': False},
            'bar': {'color': "#ec4899", 'thickness': 0.3},
            'bgcolor': "rgba(255,255,255,0.1)",
            'borderwidth': 0
        }
    ))
    fig_gauge.update_layout(
        height=80,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# STREAMGRAPH (Main visualization - Google Analytics style)
# ═══════════════════════════════════════════════════════════════════

st.markdown('<p class="section-header">Inequality Trends Over Time</p>', unsafe_allow_html=True)

# Prepare streamgraph data
stream_pivot = filtered_df.pivot_table(
    index='year',
    columns='country',
    values='value',
    aggfunc='mean'
).fillna(method='ffill').fillna(method='bfill')

# Gradient color palette (Google Analytics style)
stream_colors = [
    '#8b5cf6',  # Purple
    '#ec4899',  # Pink
    '#06b6d4',  # Cyan
    '#f59e0b',  # Amber
    '#10b981',  # Emerald
    '#6366f1',  # Indigo
    '#f43f5e',  # Rose
]

fig_stream = go.Figure()

# Add streamgraph layers
for i, country in enumerate(stream_pivot.columns):
    fig_stream.add_trace(go.Scatter(
        x=stream_pivot.index,
        y=stream_pivot[country],
        name=country,
        mode='lines',
        line=dict(width=0, color=stream_colors[i % len(stream_colors)]),
        fillcolor=stream_colors[i % len(stream_colors)],
        fill='tonexty' if i > 0 else 'tozeroy',
        stackgroup='one',
        opacity=0.85,
        hovertemplate=f'<b>{country}</b><br>Year: %{{x}}<br>Value: %{{y:.2f}}<extra></extra>'
    ))

fig_stream.update_layout(
    height=280,
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#94a3b8', size=11),
    xaxis=dict(
        showgrid=True,
        gridcolor='rgba(148, 163, 184, 0.1)',
        gridwidth=1,
        color='#94a3b8',
        title=None,
        showline=False
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='rgba(148, 163, 184, 0.1)',
        gridwidth=1,
        color='#94a3b8',
        title=None,
        showline=False
    ),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.15,
        xanchor="center",
        x=0.5,
        font=dict(color='#e2e8f0', size=10),
        bgcolor='rgba(0,0,0,0)'
    ),
    hovermode='x unified',
    hoverlabel=dict(
        bgcolor='rgba(15, 20, 25, 0.95)',
        font_size=11,
        font_color='#ffffff',
        bordercolor='rgba(139, 92, 246, 0.5)'
    )
)

st.plotly_chart(fig_stream, use_container_width=True, config={'displayModeBar': False})

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# MIDDLE ROW: Country Rankings & Browser/Device breakdown style
# ═══════════════════════════════════════════════════════════════════

col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown('<p class="section-header">Country by Inequality Level</p>', unsafe_allow_html=True)
    
    # Create stacked horizontal bars (Desktop/Mobile style from GA)
    ranked = latest_data.sort_values('value', ascending=False)
    
    fig_h_bars = go.Figure()
    
    for idx, (_, row) in enumerate(ranked.iterrows()):
        # Create two segments to mimic the Desktop/Mobile split
        value = row['value']
        segment1 = value * 0.6  # "Desktop"
        segment2 = value * 0.4  # "Mobile"
        
        # Segment 1 (darker)
        fig_h_bars.add_trace(go.Bar(
            y=[row['country']],
            x=[segment1],
            orientation='h',
            marker=dict(
                color=stream_colors[idx % len(stream_colors)],
                opacity=1
            ),
            name='Primary',
            text=f"{segment1:.1f}",
            textposition='inside',
            textfont=dict(color='white', size=11),
            hovertemplate=f"<b>{row['country']}</b><br>Primary: {segment1:.2f}<extra></extra>",
            showlegend=False
        ))
        
        # Segment 2 (lighter)
        fig_h_bars.add_trace(go.Bar(
            y=[row['country']],
            x=[segment2],
            orientation='h',
            marker=dict(
                color=stream_colors[idx % len(stream_colors)],
                opacity=0.6
            ),
            name='Secondary',
            text=f"{segment2:.1f}",
            textposition='inside',
            textfont=dict(color='white', size=11),
            hovertemplate=f"<b>{row['country']}</b><br>Secondary: {segment2:.2f}<extra></extra>",
            showlegend=False
        ))
    
    fig_h_bars.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', size=11),
        barmode='stack',
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(148, 163, 184, 0.1)',
            color='#94a3b8',
            title=None,
            showline=False,
            tickformat='.0f'
        ),
        yaxis=dict(
            showgrid=False,
            color='#e2e8f0',
            showline=False
        ),
        bargap=0.3
    )
    
    st.plotly_chart(fig_h_bars, use_container_width=True, config={'displayModeBar': False})

with col_right:
    st.markdown('<p class="section-header">Trend Status</p>', unsafe_allow_html=True)
    
    # Calculate trend categories
    improving = 0
    worsening = 0
    stable = 0
    
    for country in config['countries']:
        country_data = filtered_df[filtered_df['country'] == country].sort_values('year')
        if len(country_data) >= 2:
            change = country_data.iloc[-1]['value'] - country_data.iloc[0]['value']
            if change < -0.5:
                improving += 1
            elif change > 0.5:
                worsening += 1
            else:
                stable += 1
    
    # Donut chart (Google Analytics style)
    fig_donut = go.Figure(data=[go.Pie(
        labels=['Improving', 'Stable', 'Worsening'],
        values=[improving, stable, worsening],
        hole=0.6,
        marker=dict(
            colors=['#10b981', '#f59e0b', '#ef4444'],
            line=dict(color='rgba(15, 20, 25, 1)', width=2)
        ),
        textfont=dict(color='#ffffff', size=13),
        textposition='outside',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
    )])
    
    fig_donut.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.1,
            font=dict(color='#e2e8f0', size=11),
            bgcolor='rgba(0,0,0,0)'
        ),
        annotations=[dict(
            text=f'<b>{improving + stable + worsening}</b><br><span style="font-size:11px; color: #94a3b8;">COUNTRIES</span>',
            x=0.5, y=0.5,
            font=dict(size=20, color='#ffffff'),
            showarrow=False
        )]
    )
    
    st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# BOTTOM ROW: Rankings & Distribution
# ═══════════════════════════════════════════════════════════════════

col_left2, col_right2 = st.columns([2, 3])

with col_left2:
    st.markdown('<p class="section-header">Latest Rankings</p>', unsafe_allow_html=True)
    
    # Create ranking table (Google Analytics style)
    ranked_list = latest_data.sort_values('value').reset_index(drop=True)
    
    ranking_html = '<div style="background: rgba(15, 20, 25, 0.5); border-radius: 12px; padding: 1rem; border: 1px solid rgba(139, 92, 246, 0.2);">'
    
    for idx, row in ranked_list.iterrows():
        rank = idx + 1
        color = stream_colors[idx % len(stream_colors)]
        
        # Calculate bar width (0-100%)
        bar_width = (row['value'] / ranked_list['value'].max() * 100)
        
        ranking_html += f'''
        <div style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: #64748b; font-size: 0.85rem; font-weight: 600;">#{rank}</span>
                    <span style="color: #e2e8f0; font-weight: 600;">{row['country']}</span>
                </div>
                <span style="color: #ffffff; font-weight: 700; font-size: 1.1rem;">{row['value']:.1f}</span>
            </div>
            <div style="background: rgba(100, 116, 139, 0.2); height: 6px; border-radius: 3px; overflow: hidden;">
                <div style="background: linear-gradient(90deg, {color}, {color}CC); width: {bar_width}%; height: 100%; border-radius: 3px;"></div>
            </div>
        </div>
        '''
    
    ranking_html += '</div>'
    st.markdown(ranking_html, unsafe_allow_html=True)

with col_right2:
    st.markdown('<p class="section-header">Distribution Analysis</p>', unsafe_allow_html=True)
    
    # Area chart distribution
    hist_values, bins = np.histogram(latest_data['value'], bins=15)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    
    fig_area = go.Figure()
    
    # Add area trace
    fig_area.add_trace(go.Scatter(
        x=bin_centers,
        y=hist_values,
        fill='tozeroy',
        fillcolor='rgba(139, 92, 246, 0.4)',
        line=dict(color='#8b5cf6', width=3),
        mode='lines',
        name='Distribution',
        hovertemplate='Value: %{x:.1f}<br>Count: %{y}<extra></extra>'
    ))
    
    # Add mean line
    fig_area.add_vline(
        x=latest_data['value'].mean(),
        line_dash="dash",
        line_color="#ec4899",
        line_width=2,
        annotation_text="Mean",
        annotation_position="top",
        annotation_font_color="#ec4899"
    )
    
    fig_area.update_layout(
        height=280,
        margin=dict(l=0, r=0, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8', size=11),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(148, 163, 184, 0.1)',
            color='#94a3b8',
            title=human_indicator(config['indicator']),
            showline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(148, 163, 184, 0.1)',
            color='#94a3b8',
            title="Frequency",
            showline=False
        ),
        showlegend=False
    )
    
    st.plotly_chart(fig_area, use_container_width=True, config={'displayModeBar': False})

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 2rem 0; border-top: 1px solid rgba(148, 163, 184, 0.1);">
    <p style="color: #64748b; font-size: 0.85rem; margin: 0;">
        <strong style="color: #8b5cf6;">South Asia Inequality Analytics</strong> • Real-time Dashboard
    </p>
    <p style="color: #475569; font-size: 0.75rem; margin-top: 0.5rem;">
        Powered by Streamlit & Plotly • Data: World Bank, UNDP, ADB
    </p>
</div>
""", unsafe_allow_html=True)