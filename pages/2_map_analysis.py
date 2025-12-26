import streamlit as st
import pandas as pd
import plotly.express as px
import json
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.loaders import load_inequality_data, load_geojson
from utils.utils import human_indicator

st.set_page_config(
    page_title="...",
    page_icon="...",
    layout="wide",
    initial_sidebar_state="collapsed"  # ADD THIS LINE
)

# Load custom CSS
try:
    with open('assets/dashboard.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Check if analysis config exists
if 'analysis_config' not in st.session_state or st.session_state.analysis_config is None:
    st.warning("⚠️ No analysis configured. Please configure your analysis on the Home page.")
    st.info("Click 'home' in the sidebar to configure your analysis")
    st.stop()

# Get configuration
config = st.session_state.analysis_config

st.title("🗺️ Animated Choropleth Map Analysis")
st.markdown(f"**Geographic visualization of {human_indicator(config['indicator'])} across South Asia**")

# Load data
df = load_inequality_data()
geojson = load_geojson()

if df.empty or geojson is None:
    st.error("❌ Failed to load data or map boundaries")
    st.stop()

# Sidebar controls
with st.sidebar:
    st.subheader("Map Settings")
    
    show_animation = st.checkbox("Enable Animation", value=True, help="Play through years automatically")
    
    color_scale = st.selectbox(
        "Color Scheme",
        options=['Reds', 'Blues', 'Viridis', 'Plasma', 'Greens', 'YlOrRd', 'RdYlGn_r'],
        index=0
    )
    
    show_rankings = st.checkbox("Show Rankings Table", value=True)

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

# Add country codes for geojson matching
country_codes = {
    'Bangladesh': 'BGD',
    'India': 'IND',
    'Pakistan': 'PAK',
    'Nepal': 'NPL',
    'Sri Lanka': 'LKA'
}

filtered_df['country_code'] = filtered_df['country'].map(country_codes)

# Calculate additional data for enhanced tooltips
filtered_df['regional_avg'] = filtered_df.groupby('year')['value'].transform('mean')
filtered_df['rank'] = filtered_df.groupby('year')['value'].rank(ascending=False, method='min').astype(int)

# Calculate change from previous year
filtered_df = filtered_df.sort_values(['country', 'year'])
filtered_df['change_from_prev'] = filtered_df.groupby('country')['value'].diff()

# Create choropleth map with ENHANCED TOOLTIPS
fig = px.choropleth(
    filtered_df,
    geojson=geojson,
    locations='country_code',
    featureidkey='properties.ISO_A3',
    color='value',
    animation_frame='year' if show_animation else None,
    hover_name='country',
    hover_data={
        'country_code': False,  # Hide country code
        'value': ':.2f',
        'rank': True,  # Show rank
        'regional_avg': ':.2f',  # Show regional average
        'change_from_prev': ':.2f',  # Show change from previous year
        'source': True if 'source' in filtered_df.columns else False
    },
    color_continuous_scale=color_scale,
    labels={
        'value': human_indicator(config['indicator']),
        'rank': 'Rank',
        'regional_avg': 'Regional Avg',
        'change_from_prev': 'Change from Prev Year',
        'source': 'Data Source'
    },
    title=f"{human_indicator(config['indicator'])} Across South Asia"
)

# Update map layout
fig.update_geos(
    fitbounds="locations",
    visible=False,
    projection_type="natural earth"
)

# Update animation speed if enabled
if show_animation:
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 800
    fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 300

fig.update_layout(
    height=600,
    margin={"r":0,"t":50,"l":0,"b":0}
)

# Display map
st.plotly_chart(fig, use_container_width=True)

# Export map
col1, col2 = st.columns(2)
with col1:
    img_bytes = fig.to_image(format="png", width=1400, height=800)
    st.download_button(
        "📥 Download Map (PNG)",
        data=img_bytes,
        file_name=f"map_{config['indicator']}.png",
        mime="image/png",
        use_container_width=True
    )
with col2:
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Data (CSV)",
        data=csv,
        file_name=f"map_data.csv",
        mime="text/csv",
        use_container_width=True
    )

# Rankings table
if show_rankings:
    st.divider()
    st.subheader("📊 Country Rankings")
    
    # Create tabs for different years
    years = sorted(filtered_df['year'].unique(), reverse=True)
    year_tabs = st.tabs([str(year) for year in years[:5]])  # Show last 5 years
    
    for i, year in enumerate(years[:5]):
        with year_tabs[i]:
            year_data = filtered_df[filtered_df['year'] == year].sort_values('value', ascending=False)
            
            rankings_df = year_data[['rank', 'country', 'value', 'regional_avg']].copy()
            rankings_df.columns = ['Rank', 'Country', human_indicator(config['indicator']), 'Regional Average']
            rankings_df['Difference from Avg'] = (rankings_df[human_indicator(config['indicator'])] - rankings_df['Regional Average']).round(2)
            
            # Add emoji indicators
            def add_indicator(row):
                if row['Difference from Avg'] > 5:
                    return '🔴 Above avg'
                elif row['Difference from Avg'] < -5:
                    return '🟢 Below avg'
                else:
                    return '🟡 Near avg'
            
            rankings_df['Status'] = rankings_df.apply(add_indicator, axis=1)
            
            st.dataframe(rankings_df, use_container_width=True, hide_index=True)

# Trend Analysis
st.divider()
st.subheader("📈 Trend Analysis")

# Create trend lines for each country
fig_trends = px.line(
    filtered_df,
    x='year',
    y='value',
    color='country',
    markers=True,
    title=f"{human_indicator(config['indicator'])} Trends",
    labels={'value': human_indicator(config['indicator']), 'year': 'Year'}
)

# Add regional average line
avg_by_year = filtered_df.groupby('year')['value'].mean().reset_index()
avg_by_year['country'] = 'Regional Average'

fig_trends.add_scatter(
    x=avg_by_year['year'],
    y=avg_by_year['value'],
    mode='lines',
    name='Regional Average',
    line=dict(dash='dash', color='gray', width=3)
)

fig_trends.update_layout(
    hovermode='x unified',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig_trends, use_container_width=True)

# Export trends
col1, col2 = st.columns(2)
with col1:
    img_bytes = fig_trends.to_image(format="png", width=1200, height=600)
    st.download_button(
        "📥 Download Trends Chart (PNG)",
        data=img_bytes,
        file_name=f"trends_{config['indicator']}.png",
        mime="image/png",
        use_container_width=True
    )
with col2:
    trend_csv = filtered_df[['country', 'year', 'value', 'regional_avg', 'rank']].to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Trend Data (CSV)",
        data=trend_csv,
        file_name=f"trend_data.csv",
        mime="text/csv",
        use_container_width=True
    )

# Key Insights
st.divider()
st.subheader("🔑 Key Insights")

latest_year = filtered_df['year'].max()
latest_data = filtered_df[filtered_df['year'] == latest_year]

col1, col2, col3 = st.columns(3)

with col1:
    best_country = latest_data.loc[latest_data['value'].idxmin(), 'country']
    best_value = latest_data['value'].min()
    st.success(f"**Lowest {config['indicator']}:** {best_country} ({best_value:.2f})")

with col2:
    worst_country = latest_data.loc[latest_data['value'].idxmax(), 'country']
    worst_value = latest_data['value'].max()
    st.error(f"**Highest {config['indicator']}:** {worst_country} ({worst_value:.2f})")

with col3:
    avg_value = latest_data['value'].mean()
    st.info(f"**Regional Average:** {avg_value:.2f}")

# Footer
st.divider()
st.caption("Map Analysis | South Asia Inequality Analysis Platform")
st.caption("📊 Data sources: World Bank, UNDP | 🗺️ Map boundaries: Natural Earth")