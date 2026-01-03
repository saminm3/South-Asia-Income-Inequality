import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
from pathlib import Path
import numpy as np
import io
from datetime import datetime

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.loaders import load_inequality_data
from utils.utils import human_indicator, format_value

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════════
# GOOGLE ANALYTICS INSPIRED DARK THEME + SUPERVISOR FIXES
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* REQUIREMENT #2: Resize sidebar to 200px */
    [data-testid="stSidebar"] {
        width: 200px !important;
        min-width: 200px !important;
        max-width: 200px !important;
    }
    
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
    
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
        margin: 30px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(100, 116, 139, 0.2);
    }
    
    /* REQUIREMENT #6: Breadcrumb styling */
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
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# INLINE EXPORT FUNCTION FOR PLOTS (REPLACING export_plot_menu)
# ═══════════════════════════════════════════════════════════════════

def export_plot_inline(fig, filename_base, key):
    """Inline plot export functionality - creates download buttons for each chart"""
    st.markdown(f'<p style="color: #94a3b8; font-size: 0.85rem; margin-top: 0.5rem; margin-bottom: 0.25rem;">Download:</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col_spacer = st.columns([0.8, 0.8, 0.8, 4.6])
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with col1:
        # PNG export
        try:
            img_bytes = fig.to_image(format="png", width=1200, height=800)
            st.download_button(
                label="PNG",
                data=img_bytes,
                file_name=f"{filename_base}_{timestamp}.png",
                mime="image/png",
                key=f"{key}_png",
                use_container_width=True
            )
        except:
            st.button("PNG", disabled=True, use_container_width=True, 
                     help="Install kaleido: pip install kaleido", key=f"{key}_png")
    
    with col2:
        # HTML export
        html_str = fig.to_html(include_plotlyjs='cdn')
        st.download_button(
            label="HTML",
            data=html_str,
            file_name=f"{filename_base}_{timestamp}.html",
            mime="text/html",
            key=f"{key}_html",
            use_container_width=True
        )
    
    with col3:
        # JSON export
        json_str = fig.to_json()
        st.download_button(
            label="JSON",
            data=json_str,
            file_name=f"{filename_base}_{timestamp}.json",
            mime="application/json",
            key=f"{key}_json",
            use_container_width=True
        )

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



with st.expander("ℹ️ How to Read This Dashboard"): 
    
    # ← User clicks to open/close
    col_guide1, col_guide2 = st.columns(2)
    
    with col_guide1:
        st.markdown("""
        **Understanding GINI Index**
        - **Lower = Better** (more equality)
        - 0-25: Excellent (Nordic countries)
        - 25-35: Good (well-performing)
        - 35-45: Concerning (needs action)
        - 45+: Critical (urgent intervention)
        
        **Color Guide**
        - 🟢 Green: Low inequality (good)
        - 🔵 Blue: Moderate (acceptable)
        - 🟠 Orange: High (concerning)
        - 🔴 Red: Very high (critical)
        """)
    
    with col_guide2:
        st.markdown("""
        **What Each Chart Shows**
        1. **Stacked Area:** Trends over time
        2. **Bar Chart:** Country rankings
        3. **Donut:** Distribution by category
        
        **Download Options**
        - **PNG:** For presentations (recommended)
        - **HTML:** Interactive version
        - **JSON:** For developers
        """)
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
    delta_symbol = "↓" if yoy_pct < 0 else "↑"
    st.metric(
        label="Regional Average",
        value=f"{regional_avg:.1f}",
        delta=f"{delta_symbol} {abs(yoy_pct):.1f}%"
    )

with col2:
    best_value = latest_data['value'].min() if not latest_data.empty else 0
    st.metric(
        label="Best Performer",
        value=best_country,
        delta=f"{best_value:.1f}"
    )

with col3:
    worst_value = latest_data['value'].max() if not latest_data.empty else 0
    st.metric(
        label="Needs Attention",
        value=worst_country,
        delta=f"{worst_value:.1f}",
        delta_color="inverse"
    )

with col4:
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

# Get indicator name and create shorter version for Y-axis
indicator_name = human_indicator(config["indicator"])
# Create shorter Y-axis label to prevent crowding
y_label_short = indicator_name.split('(')[0].strip() if '(' in indicator_name else indicator_name

# REQUIREMENT #5: PROPER AXIS LABELS (FIXED SPACING)
fig_area.update_layout(
    height=400,
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
    margin=dict(l=80, r=20, t=60, b=50),  # Increased left margin for Y-axis label
    hovermode='x unified',
    title=dict(
        text=f'Stacked {indicator_name} Trends by Country ({config["year_range"][0]}-{config["year_range"][1]})',
        font=dict(size=15, color='#ffffff'),
        x=0,
        y=0.98
    )
)

st.plotly_chart(fig_area, use_container_width=True, config={'displayModeBar': False})

# CHART 1 EXPORT BUTTONS
export_plot_inline(fig_area, f"temporal_trends_{config['indicator']}", "area_chart")

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
            colorscale='RdYlGn_r',
            showscale=False,
            line=dict(width=0)
        ),
        text=[f'{v:.2f}' for v in country_avg.values],
        textposition='outside',
        textfont=dict(color='#ffffff', size=11),
        hovertemplate='<b>%{y}</b><br>Average: %{x:.2f}<extra></extra>'
    ))
    
    # REQUIREMENT #5: PROPER AXIS LABELS (FIXED SPACING)
    fig_bars.update_layout(
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', size=12),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 116, 139, 0.2)',
            title=dict(
                text=f'<b>Average {y_label_short}</b>',  # Shorter label
                font=dict(size=13, color='#94a3b8')
            ),
            color='#94a3b8'
        ),
        yaxis=dict(
            showgrid=False,
            title=dict(
                text='<b>Country</b>',
                font=dict(size=13, color='#94a3b8')
            ),
            color='#e2e8f0'
        ),
        margin=dict(l=100, r=60, t=40, b=50),
        title=dict(
            text=f'Average by Country ({config["year_range"][0]}-{config["year_range"][1]})',
            font=dict(size=14, color='#ffffff'),
            x=0
        )
    )
    
    st.plotly_chart(fig_bars, use_container_width=True, config={'displayModeBar': False})
    
    # CHART 2 EXPORT BUTTONS
    export_plot_inline(fig_bars, f"average_by_country_{config['indicator']}", "bar_chart")

with col_viz2:
    # Donut chart
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
        margin=dict(l=20, r=20, t=40, b=60),
        showlegend=False,
        title=dict(
            text=f'Distribution by Category ({latest_year})',
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
    
    # CHART 3 EXPORT BUTTONS (inside column with compact layout)
    st.markdown('<p style="color: #94a3b8; font-size: 0.85rem; margin-top: 0.3rem; margin-bottom: 0.2rem;">Download:</p>', unsafe_allow_html=True)
    col_d1, col_d2, col_d3 = st.columns(3)
    
    timestamp_donut = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with col_d1:
        try:
            img_bytes = fig_donut.to_image(format="png", width=1200, height=800)
            st.download_button("PNG", img_bytes, f"distribution_{timestamp_donut}.png", "image/png", key="donut_png", use_container_width=True)
        except:
            st.button("PNG", disabled=True, use_container_width=True, help="Install kaleido", key="donut_png")
    
    with col_d2:
        html_str = fig_donut.to_html(include_plotlyjs='cdn')
        st.download_button("HTML", html_str, f"distribution_{timestamp_donut}.html", "text/html", key="donut_html", use_container_width=True)
    
    with col_d3:
        json_str = fig_donut.to_json()
        st.download_button("JSON", json_str, f"distribution_{timestamp_donut}.json", "application/json", key="donut_json", use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# BOTTOM SECTION: Rankings & Timeline
# ═══════════════════════════════════════════════════════════════════

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
    
    rankings = latest_data.sort_values('value').reset_index(drop=True)
    
    for idx, row in rankings.iterrows():
        rank = idx + 1
        country = row['country']
        value = row['value']
        pct_of_max = (value / rankings['value'].max()) * 100
        
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
        hovermode='x unified',
        title=dict(
            text=f'Individual Country Trends Over Time',
            font=dict(size=14, color='#ffffff'),
            x=0
        )
    )
    
    st.plotly_chart(fig_lines, use_container_width=True, config={'displayModeBar': False})
    
    # CHART 4 EXPORT BUTTONS
    export_plot_inline(fig_lines, "individual_trends", "line_chart")

# ═══════════════════════════════════════════════════════════════════
# FOOTER INSIGHTS (NO EMOJIS)
# ═══════════════════════════════════════════════════════════════════

st.markdown('<div class="section-header">Key Insights & Raw Data</div>', unsafe_allow_html=True)

col_insight1, col_insight2, col_insight3 = st.columns(3)

with col_insight1:
    trend_direction = "improving" if yoy_pct < 0 else "worsening"
    
    st.markdown(f"""
    <div class="stat-card">
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
        <div style="font-size: 0.875rem; color: #94a3b8; margin-bottom: 8px;">REGIONAL GAP</div>
        <div style="font-size: 1.1rem; color: #ffffff; font-weight: 600;">
            {gap:.2f} points
        </div>
        <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 8px;">
            Between best and worst
        </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# REQUIREMENT #7: DATA EXPORT FUNCTIONALITY
# ═══════════════════════════════════════════════════════════════════

with st.expander("View Raw Data & Export Options"):
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    st.markdown("### Export Data")
    col_exp1, col_exp2, col_exp3, col_exp4 = st.columns(4)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with col_exp1:
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="CSV",
            data=csv_data,
            file_name=f"dashboard_{config['indicator']}_{timestamp}.csv",
            mime="text/csv",
            use_container_width=True,
            key="data_csv"
        )
    
    with col_exp2:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='Data')
        st.download_button(
            label="Excel",
            data=buffer.getvalue(),
            file_name=f"dashboard_{config['indicator']}_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="data_excel"
        )
    
    with col_exp3:
        json_data = filtered_df.to_json(orient='records', indent=2)
        st.download_button(
            label="JSON",
            data=json_data,
            file_name=f"dashboard_{config['indicator']}_{timestamp}.json",
            mime="application/json",
            use_container_width=True,
            key="data_json"
        )
    
    with col_exp4:
        st.button(
            "PDF",
            disabled=True,
            use_container_width=True,
            help="PDF export available with reportlab: pip install reportlab",
            key="data_pdf"
        )

st.markdown("---")
st.caption("Dashboard | South Asia Inequality Analysis Platform")