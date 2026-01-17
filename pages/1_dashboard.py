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


st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)
render_help_button("dashboard")
apply_all_styles()
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



# ═══════════════════════════════════════════════════════════════════
# KEY METRICS ROW 
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

st.markdown('<div class="section-header">Inequality Trends Over Time</div>', unsafe_allow_html=True)

# Main area chart - 
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

# Download options in top-right corner
col_spacer, col_downloads = st.columns([10, 1])
with col_downloads:
    with st.popover("⬇️", help="Download in multiple formats"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # HTML
        st.download_button("🌐 HTML", fig_area.to_html(include_plotlyjs='cdn'), f"temporal_trends_{timestamp}.html", "text/html", key="area_html", use_container_width=True)
        
        # JSON
        st.download_button("📊 JSON", fig_area.to_json(), f"temporal_trends_{timestamp}.json", "application/json", key="area_json", use_container_width=True)
        
        # SVG
        try:
            svg_bytes = fig_area.to_image(format="svg", width=1400, height=1000)
            st.download_button("🎨 SVG", svg_bytes, f"temporal_trends_{timestamp}.svg", "image/svg+xml", key="area_svg", use_container_width=True)
        except:
            st.button("🎨 SVG", disabled=True, key="area_svg", use_container_width=True)


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
        margin=dict(l=100, r=120, t=40, b=50),  # Increased right margin for values
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
            
            st.download_button("🌐 HTML", fig_bars.to_html(include_plotlyjs='cdn'), f"country_avg_{timestamp}.html", "text/html", key="bar_html", use_container_width=True)
            st.download_button("📊 JSON", fig_bars.to_json(), f"country_avg_{timestamp}.json", "application/json", key="bar_json", use_container_width=True)
            
            try:
                svg_bytes = fig_bars.to_image(format="svg", width=1400, height=1000)
                st.download_button("🎨 SVG", svg_bytes, f"country_avg_{timestamp}.svg", "image/svg+xml", key="bar_svg", use_container_width=True)
            except:
                st.button("🎨 SVG", disabled=True, key="bar_svg", use_container_width=True)
    
    st.plotly_chart(fig_bars, use_container_width=True, config={
        'displayModeBar': 'hover',
        'displaylogo': False,
        'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'autoScale2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': f'average_by_country_{config["indicator"]}',
            'height': 1000,
            'width': 1400,
            'scale': 2
        }
    })

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
    
    # Define consistent color mapping (green=good, red=bad)
    color_map = {
        'Low Inequality': '#10b981',    # Green (GOOD)
        'Moderate': '#f59e0b',          # Yellow/Orange (OK)
        'High Inequality': '#ef4444'    # Red (BAD)
    }
    
    # Ensure consistent order and colors
    ordered_categories = ['Low Inequality', 'Moderate', 'High Inequality']
    ordered_values = [category_counts.get(cat, 0) for cat in ordered_categories]
    ordered_colors = [color_map[cat] for cat in ordered_categories]
    
    fig_donut = go.Figure(data=[go.Pie(
        labels=ordered_categories,
        values=ordered_values,
        hole=0.6,
        marker=dict(
            colors=ordered_colors,
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
    
    # Download options
    col_spacer3, col_downloads3 = st.columns([10, 1])
    with col_downloads3:
        with st.popover("⬇️", help="Download in multiple formats"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            st.download_button("🌐 HTML", fig_donut.to_html(include_plotlyjs='cdn'), f"distribution_{timestamp}.html", "text/html", key="donut_html", use_container_width=True)
            st.download_button("📊 JSON", fig_donut.to_json(), f"distribution_{timestamp}.json", "application/json", key="donut_json", use_container_width=True)
            
            try:
                svg_bytes = fig_donut.to_image(format="svg", width=1400, height=1000)
                st.download_button("🎨 SVG", svg_bytes, f"distribution_{timestamp}.svg", "image/svg+xml", key="donut_svg", use_container_width=True)
            except:
                st.button("🎨 SVG", disabled=True, key="donut_svg", use_container_width=True)
    
    st.plotly_chart(fig_donut, use_container_width=True, config={
        'displayModeBar': 'hover',
        'displaylogo': False,
        'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'autoScale2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'distribution_breakdown',
            'height': 1000,
            'width': 1400,
            'scale': 2
        }
    })

# Color scheme legend for both charts
st.markdown("""
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
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# GEOGRAPHIC ARC MAP - COUNTRY CONNECTIONS
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown('<div class="section-header">Country Relationship Network</div>', unsafe_allow_html=True)

st.markdown("""
<div style="background: rgba(59, 130, 246, 0.05); padding: 15px; border-radius: 8px; border-left: 3px solid #3b82f6; margin-bottom: 20px;">
    <p style="color: #8b98a5; font-size: 0.9rem; margin: 0;">
        <b style="color: #e2e8f0;">Geographic Connection Map:</b> This map shows correlation relationships between South Asian countries. 
        Curved arcs connect countries with similar inequality patterns - thicker arcs indicate stronger correlations.
    </p>
</div>
""", unsafe_allow_html=True)

# Calculate correlation matrix
country_trends = filtered_df.pivot_table(values='value', index='year', columns='country')
correlation_matrix = country_trends.corr()

# Country coordinates (latitude, longitude) for South Asia
country_coords = {
    'Afghanistan': (33.9391, 67.7100),
    'Bangladesh': (23.6850, 90.3563),
    'Bhutan': (27.5142, 90.4336),
    'India': (20.5937, 78.9629),
    'Maldives': (3.2028, 73.2207),
    'Nepal': (28.3949, 84.1240),
    'Pakistan': (30.3753, 69.3451),
    'Sri Lanka': (7.8731, 80.7718)
}

# Get countries in dataset
countries_in_data = list(correlation_matrix.columns)

# Calculate average GINI for colors
avg_gini = {country: country_trends[country].mean() for country in countries_in_data if country in country_coords}

# Create base map
fig_arc_map = go.Figure()

# Add country markers with GINI-based colors
for country in countries_in_data:
    if country in country_coords:
        lat, lon = country_coords[country]
        gini_val = avg_gini[country]
        
        # Determine color based on GINI
        if gini_val < 30:
            color = '#10b981'  # Green
        elif gini_val < 35:
            color = '#34d399'  # Light green
        elif gini_val < 40:
            color = '#f59e0b'  # Yellow
        else:
            color = '#ef4444'  # Red
        
        # Add marker
        fig_arc_map.add_trace(go.Scattergeo(
            lon=[lon],
            lat=[lat],
            mode='markers+text',
            marker=dict(size=15, color=color, line=dict(width=2, color='#1e293b')),
            text=country,
            textposition='top center',
            textfont=dict(size=11, color='#ffffff', family='Arial Black'),
            name=country,
            hovertemplate=f'<b>{country}</b><br>Avg GINI: {gini_val:.2f}<br>Lat: {lat:.2f}, Lon: {lon:.2f}<extra></extra>',
            showlegend=False
        ))

# Add arcs for strong correlations
threshold = 0.7
arc_count = 0

for i, country1 in enumerate(countries_in_data):
    for j, country2 in enumerate(countries_in_data):
        if i < j and country1 in country_coords and country2 in country_coords:
            corr_value = correlation_matrix.loc[country1, country2]
            
            if abs(corr_value) > threshold:
                lat1, lon1 = country_coords[country1]
                lat2, lon2 = country_coords[country2]
                
                # Create arc using great circle approximation
                num_points = 50
                lats = []
                lons = []
                
                for k in range(num_points + 1):
                    t = k / num_points
                    # Simple arc (could be improved with proper great circle calculation)
                    lat = lat1 + t * (lat2 - lat1)
                    lon = lon1 + t * (lon2 - lon1)
                    
                    # Add curvature (push midpoint up/down based on position)
                    if 0.2 < t < 0.8:
                        curve_height = 5 * (1 - abs(2*t - 1))  # Peak at midpoint
                        lat += curve_height
                    
                    lats.append(lat)
                    lons.append(lon)
                
                # Line color and width based on correlation
                if corr_value > 0:
                    line_color = f'rgba(16, 185, 129, {abs(corr_value) * 0.7})'
                else:
                    line_color = f'rgba(239, 68, 68, {abs(corr_value) * 0.7})'
                
                line_width = abs(corr_value) * 3
                
                fig_arc_map.add_trace(go.Scattergeo(
                    lon=lons,
                    lat=lats,
                    mode='lines',
                    line=dict(width=line_width, color=line_color),
                    hovertemplate=f'<b>{country1} ↔ {country2}</b><br>Correlation: {corr_value:.3f}<extra></extra>',
                    showlegend=False
                ))
                arc_count += 1

# Update map layout
fig_arc_map.update_geos(
    projection_type='natural earth',
    showcountries=True,
    countrycolor='rgba(100, 116, 139, 0.3)',
    showland=True,
    landcolor='#0a0e27',
    showocean=True,
    oceancolor='#050810',
    showlakes=True,
    lakecolor='#050810',
    coastlinecolor='rgba(100, 116, 139, 0.5)',
    coastlinewidth=1,
    center=dict(lat=20, lon=78),  # Center on South Asia
    lataxis_range=[0, 40],
    lonaxis_range=[60, 100],
    bgcolor='rgba(0,0,0,0)'
)

fig_arc_map.update_layout(
    height=600,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#ffffff'),
    margin=dict(l=0, r=0, t=40, b=0),
    title=dict(
        text=f'Geographic Connection Map - {arc_count} Strong Correlations',
        font=dict(size=16, color='#ffffff'),
        x=0.5,
        xanchor='center'
    )
)

# Download options
col_spacer_arc, col_downloads_arc = st.columns([10, 1])
with col_downloads_arc:
    with st.popover("⬇️", help="Download in multiple formats"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        st.download_button("🌐 HTML", fig_arc_map.to_html(include_plotlyjs='cdn'), f"arc_map_{timestamp}.html", "text/html", key="arc_html", use_container_width=True)
        st.download_button("📊 JSON", fig_arc_map.to_json(), f"arc_map_{timestamp}.json", "application/json", key="arc_json", use_container_width=True)
        
        try:
            svg_bytes = fig_arc_map.to_image(format="svg", width=1400, height=1000)
            st.download_button("🎨 SVG", svg_bytes, f"arc_map_{timestamp}.svg", "image/svg+xml", key="arc_svg", use_container_width=True)
        except:
            st.button("🎨 SVG", disabled=True, key="arc_svg", use_container_width=True)

st.plotly_chart(fig_arc_map, use_container_width=True, config={
    'displayModeBar': 'hover',
    'displaylogo': False,
    'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
    'toImageButtonOptions': {
        'format': 'png',
        'filename': 'arc_map',
        'height': 1000,
        'width': 1400,
        'scale': 2
    }
})

# Legend for arc map
col_arc1, col_arc2, col_arc3 = st.columns(3)

with col_arc1:
    st.markdown("""
    <div style="background: #0f1419; padding: 1rem; border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.3);">
        <div style="color: #10b981; font-weight: 600; margin-bottom: 0.5rem;">🟢 Country Markers</div>
        <div style="color: #94a3b8; font-size: 0.85rem;">Green = Low inequality<br>Yellow = Moderate<br>Red = High inequality</div>
    </div>
    """, unsafe_allow_html=True)

with col_arc2:
    st.markdown("""
    <div style="background: #0f1419; padding: 1rem; border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.3);">
        <div style="color: #10b981; font-weight: 600; margin-bottom: 0.5rem;">━━ Green Arcs</div>
        <div style="color: #94a3b8; font-size: 0.85rem;">Positive correlation<br>Similar patterns</div>
    </div>
    """, unsafe_allow_html=True)

with col_arc3:
    st.markdown("""
    <div style="background: #0f1419; padding: 1rem; border-radius: 8px; border: 1px solid rgba(239, 68, 68, 0.3);">
        <div style="color: #ef4444; font-weight: 600; margin-bottom: 0.5rem;">━━ Red Arcs</div>
        <div style="color: #94a3b8; font-size: 0.85rem;">Negative correlation<br>Opposite trends</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="background: rgba(59, 130, 246, 0.1); padding: 1rem; border-radius: 8px; margin-top: 1rem; border-left: 3px solid #3b82f6;">
    <div style="color: #e2e8f0; font-size: 0.9rem;">
        <strong style="color: #60a5fa;">💡 Key Insights:</strong><br>
        • <strong>Arc thickness</strong> shows correlation strength - thicker arcs mean stronger relationships<br>
        • <strong>Geographic proximity</strong> can be compared with correlation patterns<br>
        • <strong>Green arcs</strong> connect countries with similar inequality trends over time<br>
        • <strong>Red arcs</strong> show countries moving in opposite directions<br>
        • Hover over arcs or markers to see detailed statistics
    </div>
</div>
""", unsafe_allow_html=True)

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
    
    # Download options
    col_spacer4, col_downloads4 = st.columns([10, 1])
    with col_downloads4:
        with st.popover("⬇️", help="Download in multiple formats"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            st.download_button("🌐 HTML", fig_lines.to_html(include_plotlyjs='cdn'), f"individual_trends_{timestamp}.html", "text/html", key="line_html", use_container_width=True)
            st.download_button("📊 JSON", fig_lines.to_json(), f"individual_trends_{timestamp}.json", "application/json", key="line_json", use_container_width=True)
            
            try:
                svg_bytes = fig_lines.to_image(format="svg", width=1400, height=1000)
                st.download_button("🎨 SVG", svg_bytes, f"individual_trends_{timestamp}.svg", "image/svg+xml", key="line_svg", use_container_width=True)
            except:
                st.button("🎨 SVG", disabled=True, key="line_svg", use_container_width=True)
    
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


# ═══════════════════════════════════════════════════════════════════
# FOOTER INSIGHTS 
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")
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
    export_data_menu(filtered_df, "dashboard_data_export", key="dashboard_data")

st.markdown("---")
st.caption("Dashboard | South Asia Inequality Analysis Platform")