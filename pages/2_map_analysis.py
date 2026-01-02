
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.loaders import load_inequality_data, load_geojson
from utils.utils import human_indicator

# --------------------------------------------------
# Page config
# --------------------------------------------------
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

# --------------------------------------------------
# Check analysis configuration
# --------------------------------------------------
if 'analysis_config' not in st.session_state or st.session_state.analysis_config is None:
    st.warning("⚠️ No analysis configured. Please configure your analysis on the Home page.")
    st.stop()

config = st.session_state.analysis_config

st.title("🗺️ Animated Choropleth Map Analysis")
st.markdown(f"**Geographic visualization of {human_indicator(config['indicator'])} across South Asia**")

# --------------------------------------------------
# Load data
# --------------------------------------------------
df = load_inequality_data()
geojson = load_geojson()

if df.empty or geojson is None:
    st.error("❌ Failed to load data or map boundaries")
    st.stop()

# --------------------------------------------------
# Extended country metadata
# --------------------------------------------------
country_metadata = {
    "Bangladesh": {"iso": "BGD", "population": "171 million", "gdp": "$460B", "income_group": "Lower-middle income", "region": "South Asia"},
    "India": {"iso": "IND", "population": "1.43 billion", "gdp": "$3.7T", "income_group": "Lower-middle income", "region": "South Asia"},
    "Pakistan": {"iso": "PAK", "population": "231 million", "gdp": "$375B", "income_group": "Lower-middle income", "region": "South Asia"},
    "Nepal": {"iso": "NPL", "population": "30 million", "gdp": "$41B", "income_group": "Lower-middle income", "region": "South Asia"},
    "Sri Lanka": {"iso": "LKA", "population": "22 million", "gdp": "$75B", "income_group": "Lower-middle income", "region": "South Asia"}
}

# --------------------------------------------------
# Sidebar controls
# --------------------------------------------------
with st.sidebar:
    st.subheader("🎛️ Map Settings")

    show_animation = st.checkbox("Enable Animation", value=True, help="Play through years automatically")

    animation_speed = st.slider(
        "Animation Speed (ms)",
        min_value=200,
        max_value=2000,
        value=800,
        step=100,
        help="Lower = faster animation"
    )

    color_scale = st.selectbox(
        "Color Scheme",
        options=['Reds', 'Blues', 'Viridis', 'Plasma', 'Greens', 'YlOrRd', 'RdYlGn_r'],
        index=0
    )

    projection = st.selectbox(
        "Map Projection",
        options=["natural earth", "mercator", "orthographic", "equirectangular", "robinson"],
        index=0,
        help="Choose different map projections for better visualization"
    )

    st.divider()
    st.subheader("🎯 Highlight Countries")
    highlight_countries = st.multiselect(
        "Select countries to highlight",
        options=config['countries'],
        default=[]
    )

    st.divider()
    st.subheader("📊 Display Options")
    show_rankings = st.checkbox("Show Rankings Table", value=True)

    if show_rankings:
        max_countries = len(config['countries'])
        top_n = st.slider(
            "Top N Countries in Rankings",
            min_value=1,
            max_value=max_countries,
            value=min(5, max_countries),
            help="Filter rankings table to show top N countries"
        )

# --------------------------------------------------
# Filter data
# --------------------------------------------------
filtered_df = df[
    (df['country'].isin(config['countries'])) &
    (df['year'] >= config['year_range'][0]) &
    (df['year'] <= config['year_range'][1]) &
    (df['indicator'] == config['indicator'])
].copy()

if filtered_df.empty:
    st.warning("⚠️ No data available for selected filters")
    st.stop()

# --------------------------------------------------
# ISO mapping
# --------------------------------------------------
def get_iso_code(country_name):
    if country_name in country_metadata:
        return country_metadata[country_name]['iso']
    return None

filtered_df['country_code'] = filtered_df['country'].apply(get_iso_code)

# --------------------------------------------------
# Derived metrics
# --------------------------------------------------
filtered_df['regional_avg'] = filtered_df.groupby('year')['value'].transform('mean')
filtered_df['rank'] = filtered_df.groupby('year')['value'].rank(ascending=False, method='min').astype(int)
filtered_df = filtered_df.sort_values(['country','year'])
filtered_df['change_from_prev'] = filtered_df.groupby('country')['value'].diff()

def get_trend_arrow(change):
    if pd.isna(change):
        return "➡️"
    elif change > 0.5:
        return "⬆️"
    elif change < -0.5:
        return "⬇️"
    else:
        return "➡️"

filtered_df['trend_arrow'] = filtered_df['change_from_prev'].apply(get_trend_arrow)

# Add metadata to hover
for country in filtered_df['country'].unique():
    if country in country_metadata:
        meta = country_metadata[country]
        filtered_df.loc[filtered_df['country'] == country, 'population'] = meta['population']
        filtered_df.loc[filtered_df['country'] == country, 'gdp'] = meta['gdp']
        filtered_df.loc[filtered_df['country'] == country, 'income_group'] = meta['income_group']

# --------------------------------------------------
# Insights function
# --------------------------------------------------
def calculate_year_insights(df, year):
    year_df = df[df['year'] == year]
    if len(year_df)==0:
        return None
    insights = {
        'highest': year_df.loc[year_df['value'].idxmax()],
        'lowest': year_df.loc[year_df['value'].idxmin()],
        'regional_avg': year_df['value'].mean()
    }
    if year>df['year'].min():
        prev_year = year-1
        for country in year_df['country'].unique():
            curr_val = year_df[year_df['country']==country]['value'].values
            prev_val = df[(df['country']==country)&(df['year']==prev_year)]['value'].values
            if len(curr_val)>0 and len(prev_val)>0:
                year_df.loc[year_df['country']==country,'yearly_change'] = curr_val[0]-prev_val[0]
        if 'yearly_change' in year_df.columns:
            insights['most_improved'] = year_df.loc[year_df['yearly_change'].idxmin()]
            insights['most_declined'] = year_df.loc[year_df['yearly_change'].idxmax()]
    return insights

# --------------------------------------------------
# Choropleth map
# --------------------------------------------------
hover_data_dict = {
    'country_code': False,
    'value': ':.2f',
    'rank': True,
    'regional_avg': ':.2f',
    'change_from_prev': ':.2f',
    'trend_arrow': True,
    'population': True,
    'gdp': True,
    'income_group': True
}

fig = px.choropleth(
    filtered_df,
    geojson=geojson,
    locations='country_code',
    featureidkey='properties.ISO_A3',
    color='value',
    animation_frame='year' if show_animation else None,
    hover_name='country',
    hover_data=hover_data_dict,
    color_continuous_scale=color_scale,
    labels={
        'value': human_indicator(config['indicator']),
        'rank': 'Rank',
        'regional_avg': 'Regional Avg',
        'change_from_prev': 'Change',
        'trend_arrow': 'Trend',
        'population': 'Population',
        'gdp': 'GDP',
        'income_group': 'Income Group'
    },
    title=f"{human_indicator(config['indicator'])} Across South Asia"
)

# Grey out countries without data
for feature in geojson['features']:
    iso = feature['properties']['ISO_A3']
    if iso not in filtered_df['country_code'].values:
        fig.add_trace(go.Choropleth(
            geojson={'type':'FeatureCollection','features':[feature]},
            locations=[iso],
            featureidkey='properties.ISO_A3',
            z=[0],
            colorscale=[[0,"rgba(200,200,200,0.3)"],[1,"rgba(200,200,200,0.3)"]],
            showscale=False,
            hoverinfo='skip',
            geo='geo'
        ))

# Highlight selected countries
if highlight_countries:
    for country in highlight_countries:
        iso = get_iso_code(country)
        if iso:
            country_feature = next((f for f in geojson['features'] if f['properties']['ISO_A3']==iso), None)
            if country_feature:
                fig.add_trace(go.Choropleth(
                    geojson={'type':'FeatureCollection','features':[country_feature]},
                    locations=[iso],
                    featureidkey='properties.ISO_A3',
                    z=[0],
                    colorscale=[[0,"rgba(0,0,0,0)"],[1,"rgba(0,0,0,0)"]],
                    showscale=False,
                    marker=dict(line=dict(color='red', width=3)),
                    hoverinfo='skip',
                    geo='geo'
                ))

fig.update_geos(
    fitbounds='locations',
    visible=False,
    projection_type=projection,
    showcountries=True,
    countrycolor='lightgray'
)

if show_animation and fig.layout.updatemenus:
    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = animation_speed
    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 300
else:
    fig.update_layout(updatemenus=[])

fig.update_layout(height=600, margin={'r':0,'t':50,'l':0,'b':0})
st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# Year slider for insights
# --------------------------------------------------
available_years = sorted(filtered_df['year'].unique())
if len(available_years)==0:
    st.warning("No data available for the selected filters.")
    st.stop()
elif len(available_years)==1:
    selected_year = available_years[0]
else:
    selected_year = st.slider(
        "📅 Select Year for Detailed Insights",
        min_value=int(available_years[0]),
        max_value=int(available_years[-1]),
        value=int(available_years[-1])
    )

# --------------------------------------------------
# Dynamic insights
# --------------------------------------------------
st.subheader(f"🔑 Key Findings for {selected_year}")
insights = calculate_year_insights(filtered_df, selected_year)
if insights:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🟢 Lowest (Best)", insights['lowest']['country'], f"{insights['lowest']['value']:.2f}")
    with col2:
        st.metric("🔴 Highest (Worst)", insights['highest']['country'], f"{insights['highest']['value']:.2f}")
    with col3:
        st.metric("📊 Regional Average", f"{insights['regional_avg']:.2f}")
    with col4:
        if 'most_improved' in insights:
            change = insights['most_improved']['yearly_change']
            st.metric("⭐ Most Improved", insights['most_improved']['country'], f"{change:.2f}", delta_color='inverse')
    if 'most_declined' in insights:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            change = insights['most_declined']['yearly_change']
            st.metric("⚠️ Most Declined", insights['most_declined']['country'], f"{change:.2f}", delta_color='inverse')

# --------------------------------------------------
# Export section
# --------------------------------------------------
st.divider()
col1, col2 = st.columns(2)
with col1:
    try:
        img_bytes = fig.to_image(format='png', width=1400, height=800)
        st.download_button(
            "📥 Download Map (PNG)",
            data=img_bytes,
            file_name=f"map_{config['indicator']}_{selected_year}.png",
            mime="image/png",
            use_container_width=True
        )
    except Exception:
        st.info("ℹ️ Image export unavailable (Kaleido not installed).")
with col2:
    csv_bytes = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Data (CSV)",
        data=csv_bytes,
        file_name=f"map_data_{selected_year}.csv",
        mime="text/csv",
        use_container_width=True
    )

# --------------------------------------------------
# Enhanced rankings table
# --------------------------------------------------
if show_rankings:
    st.divider()
    st.subheader("📊 Country Rankings")

    years = sorted(filtered_df['year'].unique(), reverse=True)[:5]
    tabs = st.tabs([str(y) for y in years])

    for tab, year in zip(tabs, years):
        with tab:
            year_df = filtered_df[filtered_df['year']==year].sort_values('value', ascending=False).head(top_n)

            rankings_df = year_df[['rank','country','value','regional_avg','change_from_prev','trend_arrow']].copy()
            rankings_df.columns = [
                'Rank','Country',human_indicator(config['indicator']),'Regional Average','Change from Prev Year','Trend'
            ]
            rankings_df['Difference from Avg'] = (rankings_df[human_indicator(config['indicator'])] - rankings_df['Regional Average']).round(2)
            rankings_df['Status'] = rankings_df['Difference from Avg'].apply(
                lambda x: '🔴 Above avg' if x>5 else '🟢 Below avg' if x<-5 else '🟡 Near avg'
            )
            st.dataframe(rankings_df, use_container_width=True, hide_index=True)

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.divider()
st.caption("Map Analysis | South Asia Inequality Analysis Platform")
st.caption("📊 Data sources: World Bank, UNDP | 🗺️ Map boundaries: Natural Earth")
st.caption("✨ Enhanced with dynamic insights, country highlighting, projections, and advanced filtering")
