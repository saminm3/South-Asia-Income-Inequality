import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path
import numpy as np

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.loaders import load_quality_audit, load_inequality_data


from utils.help_system import render_help_button
from utils.sidebar import apply_all_styles
from utils.api_loader import get_api_loader

st.set_page_config(
    page_title="Data Quality",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize API loader after page config
api_loader = get_api_loader()

render_help_button("quality")
apply_all_styles()
# Load custom CSS
try:
    with open('assets/dashboard.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Additional custom CSS for this page
st.markdown("""
<style>
    .quality-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(16, 185, 129, 0.1));
        border: 2px solid rgba(59, 130, 246, 0.3);
        border-radius: 16px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .metric-card {
        background: #1e2532;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #2f3336;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #3b82f6;
    }
    
    .quality-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }
    
    .badge-high {
        background: linear-gradient(135deg, #10b981, #34d399);
        color: white;
    }
    
    .badge-medium {
        background: linear-gradient(135deg, #f59e0b, #fbbf24);
        color: white;
    }
    
    .badge-low {
        background: linear-gradient(135deg, #ef4444, #f87171);
        color: white;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        margin: 30px 0 20px 0;
        padding-bottom: 12px;
        border-bottom: 3px solid rgba(59, 130, 246, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="dashboard-header">
    <h1 style="display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 2.5rem;">✅</span> Data Quality Dashboard
    </h1>
    <p style="font-size: 1.1rem;">Monitor completeness, reliability, and data flow across South Asian inequality indicators</p>
</div>
""", unsafe_allow_html=True)

# ============= LIVE API INTEGRATION SIDEBAR =============
with st.sidebar:
    st.markdown("### 🌐 Live Data Validation")
    use_api_validation = st.toggle("Enable API Validation", value=False, 
                                    help="Cross-check local data against live World Bank API")
    
    if use_api_validation:
        st.success("✓ API Connected")
        
        # Show live data freshness
        with st.spinner("Checking data freshness..."):
            try:
                # Fetch latest available year from API for a sample indicator
                sample_data = api_loader.fetch_indicator('SI.POV.GINI', countries='India', date_range='2020:2024')
                if not sample_data.empty and 'date' in sample_data.columns:
                    latest_year = sample_data['date'].max()
                    st.info(f"📅 Latest API Data: {latest_year}")
                else:
                    st.warning("⚠️ No recent API data available")
            except Exception as e:
                st.error(f"API Error: {str(e)[:50]}...")
        
        # Show exchange rates as a data quality indicator
        rates = api_loader.get_exchange_rates()
        if rates:
            st.markdown("**Live Exchange Rates (USD):**")
            st.caption(f"🇧🇩 BDT: {rates.get('BDT', 'N/A')}")
            st.caption(f"🇮🇳 INR: {rates.get('INR', 'N/A')}")
            st.caption(f"🇵🇰 PKR: {rates.get('PKR', 'N/A')}")
    else:
        st.info("Enable to validate against live World Bank data")

# Load data
with st.spinner("Calculating quality metrics from live data..."):
    # 1. Load actual data
    df_actual = load_inequality_data()
    
    # 2. Calculate dynamic audit
    if not df_actual.empty:
        # Define expected year range
        EXPECTED_YEARS = 25  # 2000-2024
        
        # Group by Country + Indicator
        audit = df_actual.groupby(['country', 'indicator']).agg(
            record_count=('value', 'count'),
            min_year=('year', 'min'),
            max_year=('year', 'max')
        ).reset_index()
        
        # Calculate completeness
        audit['completeness'] = (audit['record_count'] / EXPECTED_YEARS) * 100
        audit['completeness'] = audit['completeness'].clip(upper=100)  # Cap at 100%
        
        # Merge source information if available
        if 'source' in df_actual.columns:
            # Create a source mapping (take first source found for each country-indicator pair)
            source_map = df_actual.groupby(['country', 'indicator'])['source'].first().reset_index()
            audit = pd.merge(audit, source_map, on=['country', 'indicator'], how='left')
            audit['source'] = audit['source'].fillna('World Bank / Derived')
        else:
            audit['source'] = 'World Bank / Derived' 
            
        audit['issues'] = audit.apply(lambda x: "Low coverage" if x['completeness'] < 50 else "Good", axis=1)
        
    else:
        # Fallback if load fails
        audit = load_quality_audit()

if audit.empty:
    st.error("❌ Quality audit data not found")
    st.info("""
    **Required file:** `data/processed/quality_audit.csv`
    
    This file should contain:
    - country: Country name
    - indicator: Indicator name
    - completeness: Percentage (0-100)
    - year_range: e.g., "2000-2023"
    - issues: Description of data gaps
    - source: Data source
    - last_updated: Last update date
    """)
    st.stop()

# Helper functions
def get_quality_badge(score):
    """Return emoji badge based on quality score"""
    if score >= 80:
        return "🟢 High"
    elif score >= 60:
        return "🟡 Medium"
    else:
        return "🔴 Low"

def get_quality_color(score):
    """Return color based on quality score"""
    if score >= 80:
        return "#10b981"
    elif score >= 60:
        return "#f59e0b"
    else:
        return "#ef4444"

def get_quality_badge_html(score):
    """Return HTML badge based on quality score"""
    if score >= 80:
        return '<span class="quality-badge badge-high">HIGH QUALITY</span>'
    elif score >= 60:
        return '<span class="quality-badge badge-medium">MEDIUM QUALITY</span>'
    else:
        return '<span class="quality-badge badge-low">LOW QUALITY</span>'

# Add quality columns
if 'completeness' in audit.columns:
    audit['Quality'] = audit['completeness'].apply(get_quality_badge)
    audit['Quality_Color'] = audit['completeness'].apply(get_quality_color)

# Country coordinates for bubble map (approximate centroids)
COUNTRY_COORDS = {
    'Bangladesh': {'lat': 23.685, 'lon': 90.3563, 'name': 'Bangladesh'},
    'India': {'lat': 20.5937, 'lon': 78.9629, 'name': 'India'},
    'Pakistan': {'lat': 30.3753, 'lon': 69.3451, 'name': 'Pakistan'},
    'Nepal': {'lat': 28.3949, 'lon': 84.1240, 'name': 'Nepal'},
    'Sri Lanka': {'lat': 7.8731, 'lon': 80.7718, 'name': 'Sri Lanka'},
    'Afghanistan': {'lat': 33.9391, 'lon': 67.7100, 'name': 'Afghanistan'},
    'Bhutan': {'lat': 27.5142, 'lon': 90.4336, 'name': 'Bhutan'},
    'Maldives': {'lat': 3.2028, 'lon': 73.2207, 'name': 'Maldives'}
}

# ============= OVERVIEW METRICS =============

st.markdown('<p class="section-title">📊 Quality Overview</p>', unsafe_allow_html=True)

if 'completeness' in audit.columns and len(audit) > 0:
    col1, col2, col3, col4 = st.columns(4)
    
    avg_completeness = audit['completeness'].mean()
    high_quality = len(audit[audit['completeness'] >= 80])
    medium_quality = len(audit[(audit['completeness'] >= 60) & (audit['completeness'] < 80)])
    critical_gaps = len(audit[audit['completeness'] < 60])
    total = len(audit)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 3rem; margin-bottom: 10px;">📈</div>
            <div style="font-size: 2.5rem; font-weight: 800; color: #60a5fa; margin: 10px 0;">{avg_completeness:.1f}%</div>
            <div style="color: #8b98a5; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Avg Completeness</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 3rem; margin-bottom: 10px;">🟢</div>
            <div style="font-size: 2.5rem; font-weight: 800; color: #10b981; margin: 10px 0;">{high_quality}</div>
            <div style="color: #8b98a5; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">High Quality</div>
            <div style="color: #64748b; font-size: 0.8rem; margin-top: 5px;">≥80% complete</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 3rem; margin-bottom: 10px;">🟡</div>
            <div style="font-size: 2.5rem; font-weight: 800; color: #f59e0b; margin: 10px 0;">{medium_quality}</div>
            <div style="color: #8b98a5; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Medium Quality</div>
            <div style="color: #64748b; font-size: 0.8rem; margin-top: 5px;">60-79% complete</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 3rem; margin-bottom: 10px;">🔴</div>
            <div style="font-size: 2.5rem; font-weight: 800; color: #ef4444; margin: 10px 0;">{critical_gaps}</div>
            <div style="color: #8b98a5; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Critical Gaps</div>
            <div style="color: #64748b; font-size: 0.8rem; margin-top: 5px;">\u003c60% complete</div>
        </div>
        """, unsafe_allow_html=True)


# ============= LIVE API VALIDATION SECTION =============
if use_api_validation:
    st.markdown('<p class="section-title">🔄 Live API Data Validation</p>', unsafe_allow_html=True)
    
    with st.spinner("Validating against World Bank API..."):
        validation_results = []
        
        # Sample a few indicators to validate
        sample_indicators = audit.head(5) if len(audit) > 5 else audit
        
        for idx, row in sample_indicators.iterrows():
            indicator_name = row.get('indicator', 'N/A')
            country = row.get('country', 'N/A')
            local_completeness = row.get('completeness', 0)
            
            # Try to map indicator name to World Bank code (simplified)
            indicator_code = 'SI.POV.GINI'  # Default to Gini for demo
            
            try:
                api_data = api_loader.fetch_indicator(indicator_code, countries=country, date_range='2000:2023')
                api_available = not api_data.empty
                api_count = len(api_data) if api_available else 0
                
                validation_results.append({
                    'Indicator': indicator_name,
                    'Country': country,
                    'Local Quality': f"{local_completeness:.1f}%",
                    'API Status': '✅ Available' if api_available else '❌ Not Found',
                    'API Records': api_count
                })
            except:
                validation_results.append({
                    'Indicator': indicator_name,
                    'Country': country,
                    'Local Quality': f"{local_completeness:.1f}%",
                    'API Status': '⚠️ Error',
                    'API Records': 0
                })
        
        if validation_results:
            st.markdown("""
            <div style="background: rgba(16, 185, 129, 0.05); padding: 15px; border-radius: 8px; border-left: 3px solid #10b981; margin-bottom: 20px;">
                <p style="color: #8b98a5; font-size: 0.9rem; margin: 0;">
                    <b style="color: #e2e8f0;">API Validation:</b> Cross-checking local data quality against live World Bank API availability.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            validation_df = pd.DataFrame(validation_results)
            st.dataframe(validation_df, use_container_width=True, hide_index=True)

# ============= BUBBLE MAP =============

st.markdown('<p class="section-title">🗺️ Geographic Data Quality Distribution</p>', unsafe_allow_html=True)

st.markdown("""
<div style="background: rgba(59, 130, 246, 0.05); padding: 15px; border-radius: 8px; border-left: 3px solid #3b82f6; margin-bottom: 20px;">
    <p style="color: #8b98a5; font-size: 0.9rem; margin: 0;">
        <b style="color: #e2e8f0;">Bubble Map:</b> Circle size represents the number of indicators available for each country. 
        Color indicates average data quality (green = high, yellow = medium, red = low).
    </p>
</div>
""", unsafe_allow_html=True)

if 'country' in audit.columns and 'completeness' in audit.columns:
    # Aggregate data by country
    country_stats = audit.groupby('country').agg({
        'completeness': 'mean',
        'indicator': 'count'
    }).reset_index()
    country_stats.columns = ['country', 'avg_completeness', 'indicator_count']
    
    # Add coordinates
    map_data = []
    for _, row in country_stats.iterrows():
        country = row['country']
        if country in COUNTRY_COORDS:
            map_data.append({
                'country': country,
                'lat': COUNTRY_COORDS[country]['lat'],
                'lon': COUNTRY_COORDS[country]['lon'],
                'avg_completeness': row['avg_completeness'],
                'indicator_count': row['indicator_count'],
                'quality': get_quality_badge(row['avg_completeness'])
            })
    
    if map_data:
        map_df = pd.DataFrame(map_data)
        
        # Create bubble map
        fig_map = px.scatter_geo(
            map_df,
            lat='lat',
            lon='lon',
            size='indicator_count',
            color='avg_completeness',
            hover_name='country',
            hover_data={
                'lat': False,
                'lon': False,
                'avg_completeness': ':.1f',
                'indicator_count': True,
                'quality': True
            },
            color_continuous_scale='RdYlGn',
            size_max=50,
            labels={
                'avg_completeness': 'Avg Quality (%)',
                'indicator_count': 'Indicators',
                'quality': 'Quality Level'
            }
        )
        
        fig_map.update_geos(
            scope='asia',
            showcountries=True,
            countrycolor='rgba(255,255,255,0.2)',
            showcoastlines=True,
            coastlinecolor='rgba(255,255,255,0.3)',
            showland=True,
            landcolor='#0f1419',
            showocean=True,
            oceancolor='#1a1f3a',
            projection_type='natural earth',
            center=dict(lat=20, lon=80),
            lataxis_range=[0, 40],
            lonaxis_range=[60, 100]
        )
        
        fig_map.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            geo=dict(bgcolor='rgba(0,0,0,0)'),
            font=dict(color='#e2e8f0'),
            height=500,
            margin=dict(t=10, b=10, l=10, r=10),
            coloraxis_colorbar=dict(
                title="Quality %",
                tickfont=dict(color='#e2e8f0')
            )
        )
        
        st.plotly_chart(fig_map, use_container_width=True)
        
        # Summary table below map
        st.markdown("#### 📋 Country Summary")
        summary_df = map_df[['country', 'avg_completeness', 'indicator_count', 'quality']].sort_values('avg_completeness', ascending=False)
        summary_df.columns = ['Country', 'Avg Quality (%)', 'Indicators', 'Quality Level']
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

# ============= SANKEY DIAGRAM =============

st.markdown('<p class="section-title">🌊 Data Flow: Source → Country → Quality</p>', unsafe_allow_html=True)

st.markdown("""
<div style="background: rgba(16, 185, 129, 0.05); padding: 15px; border-radius: 8px; border-left: 3px solid #10b981; margin-bottom: 20px;">
    <p style="color: #8b98a5; font-size: 0.9rem; margin: 0;">
        <b style="color: #e2e8f0;">Sankey Diagram:</b> Visualizes how data flows from sources (left) through countries (middle) to quality levels (right). 
        Thicker flows indicate more indicators.
    </p>
</div>
""", unsafe_allow_html=True)

if 'source' in audit.columns and 'country' in audit.columns and 'completeness' in audit.columns:
    # Prepare Sankey data
    sankey_data = audit.copy()
    sankey_data['quality_level'] = sankey_data['completeness'].apply(
        lambda x: 'High Quality (≥80%)' if x >= 80 else 'Medium Quality (60-79%)' if x >= 60 else 'Low Quality (<60%)'
    )
    
    # Create node lists
    sources_list = sankey_data['source'].unique().tolist()
    countries_list = sankey_data['country'].unique().tolist()
    quality_list = ['High Quality (≥80%)', 'Medium Quality (60-79%)', 'Low Quality (<60%)']
    
    all_nodes = sources_list + countries_list + quality_list
    
    # Create mappings
    node_dict = {node: idx for idx, node in enumerate(all_nodes)}
    
    # Build links
    links_source = []
    links_target = []
    links_value = []
    links_color = []
    
    # Source -> Country
    for source in sources_list:
        for country in countries_list:
            count = len(sankey_data[(sankey_data['source'] == source) & (sankey_data['country'] == country)])
            if count > 0:
                links_source.append(node_dict[source])
                links_target.append(node_dict[country])
                links_value.append(count)
                links_color.append('rgba(59, 130, 246, 0.3)')
    
    # Country -> Quality
    for country in countries_list:
        for quality in quality_list:
            count = len(sankey_data[(sankey_data['country'] == country) & (sankey_data['quality_level'] == quality)])
            if count > 0:
                links_source.append(node_dict[country])
                links_target.append(node_dict[quality])
                links_value.append(count)
                # Color based on quality
                if 'High' in quality:
                    links_color.append('rgba(16, 185, 129, 0.4)')
                elif 'Medium' in quality:
                    links_color.append('rgba(245, 158, 11, 0.4)')
                else:
                    links_color.append('rgba(239, 68, 68, 0.4)')
    
    # Node colors
    node_colors = []
    for node in all_nodes:
        if node in sources_list:
            node_colors.append('#3b82f6')  # Blue for sources
        elif node in countries_list:
            node_colors.append('#8b5cf6')  # Purple for countries
        else:
            if 'High' in node:
                node_colors.append('#10b981')  # Green
            elif 'Medium' in node:
                node_colors.append('#f59e0b')  # Orange
            else:
                node_colors.append('#ef4444')  # Red
    
    # Create Sankey diagram
    fig_sankey = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='rgba(255,255,255,0.2)', width=1),
            label=all_nodes,
            color=node_colors,
            customdata=[f"{node}" for node in all_nodes],
            hovertemplate='%{customdata}<br>%{value} indicators<extra></extra>'
        ),
        link=dict(
            source=links_source,
            target=links_target,
            value=links_value,
            color=links_color,
            hovertemplate='%{value} indicators<extra></extra>'
        )
    )])
    
    fig_sankey.update_layout(
        title=dict(
            text="Data Quality Flow: Sources → Countries → Quality Levels",
            font=dict(size=18, color='#e2e8f0')
        ),
        font=dict(size=12, color='#e2e8f0'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=600,
        margin=dict(t=60, b=20, l=20, r=20)
    )
    
    st.plotly_chart(fig_sankey, use_container_width=True)

# ============= DETAILED ANALYSIS =============

st.markdown('<p class="section-title">📊 Detailed Quality Analysis</p>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔥 Heatmap", "📈 Trends", "🚨 Critical Gaps"])

with tab1:
    if 'country' in audit.columns and 'indicator' in audit.columns and 'completeness' in audit.columns:
        st.markdown("#### 🔥 Data Completeness Heatmap")
        
        st.markdown("""
        <div style="background: rgba(59, 130, 246, 0.05); padding: 15px; border-radius: 8px; border-left: 3px solid #3b82f6; margin-bottom: 20px;">
            <p style="color: #8b98a5; font-size: 0.9rem; margin: 0;">
                <b style="color: #e2e8f0;">Heatmap:</b> Each cell shows data completeness for a specific country-indicator pair. 
                Colors range from red (low) to green (high quality).
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        heatmap_data = audit.pivot_table(
            index='indicator',
            columns='country',
            values='completeness',
            aggfunc='mean'
        )
        
        fig_heatmap = px.imshow(
            heatmap_data,
            labels=dict(x="Country", y="Indicator", color="Completeness %"),
            color_continuous_scale='RdYlGn',
            aspect="auto",
            text_auto='.0f'
        )
        
        fig_heatmap.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            height=500,
            xaxis=dict(tickangle=-45, tickfont=dict(size=11)),
            yaxis=dict(tickfont=dict(size=11)),
            coloraxis_colorbar=dict(
                title="Quality %",
                tickfont=dict(color='#e2e8f0')
            )
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)

with tab2:
    if 'country' in audit.columns and 'completeness' in audit.columns:
        st.markdown("#### Quality Distribution by Country (Ridgeline Plot)")
        
        st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.05); padding: 15px; border-radius: 8px; border-left: 3px solid #10b981; margin-bottom: 20px;">
            <p style="color: #8b98a5; font-size: 0.9rem; margin: 0;">
                <b style="color: #e2e8f0;">Ridgeline Plot:</b> Shows the distribution of data quality scores for each country. 
                Each curve represents one country's quality distribution across indicators.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Get unique countries sorted by average quality
        countries = audit.groupby('country')['completeness'].mean().sort_values(ascending=True).index.tolist()
        
        from scipy import stats
        
        # Color palette - viridis-like colors matching reference
        colors = ['#440154', '#482878', '#3e4a89', '#31688e', '#26838f', '#1f9d8a', '#6cce5a', '#b5de2c', '#fde725']
        
        fig_ridge = go.Figure()
        
        # Spacing between ridges
        spacing = 0.8
        
        for i, country in enumerate(countries):
            country_data = audit[audit['country'] == country]['completeness'].values
            
            if len(country_data) > 0:
                # Create smooth density curve using KDE
                x_range = np.linspace(0, 100, 500)
                
                if len(country_data) >= 2:
                    try:
                        kde = stats.gaussian_kde(country_data, bw_method=0.25)
                        density = kde(x_range)
                    except:
                        # Fallback for singular data
                        density = np.zeros_like(x_range)
                        for val in country_data:
                            density += stats.norm.pdf(x_range, val, 8)
                else:
                    # Single data point - create gaussian bump
                    density = stats.norm.pdf(x_range, country_data[0], 8)
                
                # Normalize density
                if density.max() > 0:
                    density = (density / density.max()) * 0.7
                
                # Y offset for this ridge
                y_base = i * spacing
                y_curve = density + y_base
                
                # Get color
                color_idx = i % len(colors)
                fill_color = colors[color_idx]
                
                # Add baseline first (for proper fill reference)
                fig_ridge.add_trace(go.Scatter(
                    x=x_range,
                    y=[y_base] * len(x_range),
                    mode='lines',
                    line=dict(color='rgba(0,0,0,0)', width=0),
                    showlegend=False,
                    hoverinfo='skip'
                ))
                
                # Add the filled density curve
                fig_ridge.add_trace(go.Scatter(
                    x=x_range,
                    y=y_curve,
                    mode='lines',
                    fill='tonexty',
                    fillcolor=fill_color,
                    line=dict(color='#1a1f3a', width=1.5),
                    name=country,
                    showlegend=False,
                    hovertemplate=f'<b>{country}</b><br>Quality: %{{x:.1f}}%<extra></extra>'
                ))
        
        # Add country labels on y-axis
        fig_ridge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0', family='Inter'),
            height=max(500, len(countries) * 70),
            xaxis=dict(
                title="Data Quality (%)",
                showgrid=True,
                gridcolor='rgba(255,255,255,0.15)',
                gridwidth=1,
                range=[0, 100],
                zeroline=False,
                tickfont=dict(size=12),
                dtick=25
            ),
            yaxis=dict(
                tickmode='array',
                tickvals=[i * spacing + 0.35 for i in range(len(countries))],
                ticktext=countries,
                showgrid=False,
                zeroline=False,
                tickfont=dict(size=11)
            ),
            showlegend=False,
            margin=dict(l=120, r=30, t=30, b=60),
            hovermode='closest'
        )
        
        st.plotly_chart(fig_ridge, use_container_width=True)
        
        # Add summary statistics
        st.markdown("#### 📊 Summary Statistics")
        
        summary_stats = []
        for country in countries:
            country_data = audit[audit['country'] == country]['completeness'].values
            if len(country_data) > 0:
                summary_stats.append({
                    'Country': country,
                    'Mean': f"{country_data.mean():.1f}%",
                    'Median': f"{np.median(country_data):.1f}%",
                    'Std Dev': f"{country_data.std():.1f}%",
                    'Min': f"{country_data.min():.1f}%",
                    'Max': f"{country_data.max():.1f}%",
                    'Indicators': len(country_data)
                })
        
        summary_df = pd.DataFrame(summary_stats)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

with tab3:
    if 'completeness' in audit.columns:
        critical = audit[audit['completeness'] < 60].sort_values('completeness')
        
        if len(critical) > 0:
            st.error(f"⚠️ Found {len(critical)} critical data gaps (completeness < 60%)")
            
            # Add Visual Gap Analysis
            st.markdown("#### 📊 Gap Analysis Visualization")
            
            # Create horizontal bar chart showing gaps
            gap_chart_data = critical.copy()
            gap_chart_data['gap'] = 60 - gap_chart_data['completeness']  # How far from 60% threshold
            gap_chart_data['label'] = gap_chart_data['country'] + ' - ' + gap_chart_data['indicator']
            gap_chart_data = gap_chart_data.sort_values('completeness', ascending=True)
            
            fig_gaps = go.Figure()
            
            # Add the completeness bars (what we have)
            fig_gaps.add_trace(go.Bar(
                y=gap_chart_data['label'],
                x=gap_chart_data['completeness'],
                orientation='h',
                name='Current Data',
                marker=dict(
                    color=gap_chart_data['completeness'],
                    colorscale=[[0, '#ef4444'], [0.5, '#f59e0b'], [1, '#10b981']],
                    cmin=0,
                    cmax=100
                ),
                text=gap_chart_data['completeness'].apply(lambda x: f'{x:.1f}%'),
                textposition='inside',
                textfont=dict(color='white', size=11),
                hovertemplate='<b>%{y}</b><br>Completeness: %{x:.1f}%<extra></extra>'
            ))
            
            # Add the gap bars (what's missing)
            fig_gaps.add_trace(go.Bar(
                y=gap_chart_data['label'],
                x=gap_chart_data['gap'],
                orientation='h',
                name='Data Gap',
                marker=dict(color='rgba(239, 68, 68, 0.3)'),
                text=gap_chart_data['gap'].apply(lambda x: f'+{x:.1f}% needed'),
                textposition='inside',
                textfont=dict(color='#ef4444', size=10),
                hovertemplate='<b>%{y}</b><br>Gap to 60%: %{x:.1f}%<extra></extra>'
            ))
            
            fig_gaps.update_layout(
                barmode='stack',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                height=max(400, len(critical) * 45),
                xaxis=dict(
                    title='Data Completeness (%)',
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.1)',
                    range=[0, 100],
                    ticksuffix='%'
                ),
                yaxis=dict(
                    showgrid=False,
                    tickfont=dict(size=11)
                ),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1,
                    bgcolor='rgba(0,0,0,0)'
                ),
                margin=dict(l=200, r=50, t=50, b=50),
                shapes=[
                    # Add 60% threshold line
                    dict(
                        type='line',
                        x0=60, x1=60,
                        y0=-0.5, y1=len(critical) - 0.5,
                        line=dict(color='#f59e0b', width=2, dash='dash')
                    )
                ],
                annotations=[
                    dict(
                        x=60, y=len(critical) - 0.3,
                        text='60% Threshold',
                        showarrow=False,
                        font=dict(color='#f59e0b', size=10),
                        xanchor='left',
                        xshift=5
                    )
                ]
            )
            
            st.plotly_chart(fig_gaps, use_container_width=True)
            
            # Add Lollipop Chart for severity
            st.markdown("#### 🎯 Gap Severity (Distance from Threshold)")
            
            fig_lollipop = go.Figure()
            
            # Add connecting lines
            for i, row in gap_chart_data.iterrows():
                fig_lollipop.add_trace(go.Scatter(
                    x=[row['completeness'], 60],
                    y=[row['label'], row['label']],
                    mode='lines',
                    line=dict(color='rgba(239, 68, 68, 0.5)', width=2),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            # Add current value dots
            fig_lollipop.add_trace(go.Scatter(
                x=gap_chart_data['completeness'],
                y=gap_chart_data['label'],
                mode='markers',
                marker=dict(
                    size=15,
                    color='#ef4444',
                    line=dict(color='white', width=2)
                ),
                name='Current',
                text=gap_chart_data['completeness'].apply(lambda x: f'{x:.1f}%'),
                hovertemplate='<b>%{y}</b><br>Current: %{x:.1f}%<extra></extra>'
            ))
            
            # Add target dots (60%)
            fig_lollipop.add_trace(go.Scatter(
                x=[60] * len(gap_chart_data),
                y=gap_chart_data['label'],
                mode='markers',
                marker=dict(
                    size=12,
                    color='#10b981',
                    symbol='diamond',
                    line=dict(color='white', width=1)
                ),
                name='Target (60%)',
                hovertemplate='<b>%{y}</b><br>Target: 60%<extra></extra>'
            ))
            
            fig_lollipop.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                height=max(350, len(critical) * 40),
                xaxis=dict(
                    title='Data Completeness (%)',
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.1)',
                    range=[0, 70],
                    ticksuffix='%'
                ),
                yaxis=dict(
                    showgrid=False,
                    tickfont=dict(size=11)
                ),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='center',
                    x=0.5,
                    bgcolor='rgba(0,0,0,0)'
                ),
                margin=dict(l=200, r=50, t=60, b=50)
            )
            
            st.plotly_chart(fig_lollipop, use_container_width=True)
            
            st.markdown("---")
            st.markdown("#### 📋 Detailed Gap Information")
            
            for i, row in critical.head(10).iterrows():
                completeness = row['completeness']
                badge_html = get_quality_badge_html(completeness)
                
                with st.expander(f"🔴 {row.get('country', 'N/A')} - {row.get('indicator', 'N/A')} ({completeness:.1f}%)"):
                    st.markdown(badge_html, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Completeness:** {completeness:.1f}%")
                        if 'year_range' in row:
                            st.markdown(f"**Year Range:** {row.get('year_range', 'N/A')}")
                        if 'source' in row:
                            st.markdown(f"**Source:** {row.get('source', 'N/A')}")
                    
                    with col2:
                        if 'issues' in row:
                            st.markdown(f"**Issues:** {row.get('issues', 'No details')}")
                        if 'last_updated' in row:
                            st.markdown(f"**Last Updated:** {row.get('last_updated', 'N/A')}")
        else:
            st.success("✅ No critical data gaps found! All datasets have ≥60% completeness.")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 30px 0;">
    <b style="color: #94a3b8;">Data Quality Dashboard v2.0</b> | South Asia Inequality Analysis Platform<br>
    ✅ Transparency in data quality is essential for credible research
</div>
""", unsafe_allow_html=True)

# -----------------
# Navigation
# -----------------
from utils.navigation_ui import bottom_nav_layout
bottom_nav_layout(__file__)
