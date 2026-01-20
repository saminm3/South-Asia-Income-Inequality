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
from utils.help_system import render_help_button
from utils.sidebar import apply_all_styles




# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="...",
    page_icon="...",
    layout="wide",
    initial_sidebar_state="expanded"  # Sidebar visible by default
)
render_help_button("map")
apply_all_styles()

# Load custom CSS
try:
    with open('assets/dashboard.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

# --------------------------------------------------
# Check analysis configuration

config = st.session_state.get("analysis_config")
if config is None:
    st.error("❌ Analysis configuration missing.")
    st.info("Please configure the analysis on the Home page first.")
    st.stop()

config = st.session_state.analysis_config

st.title("Animated Choropleth Map Analysis")
st.markdown(f"**Geographic visualization of {human_indicator(config['indicator'])} across South Asia**")

config = st.session_state.get("analysis_config")

# if config is None:
#     st.error("❌ Analysis configuration missing.")
#     st.info("Please configure the analysis on the Home page first.")
#     st.stop()

# ---------------------------
# Fixed visualization settings
# ---------------------------
show_animation = True                   # Animation always on
animation_speed = 800                   # Default speed
color_scale = config.get('color_scale', 'Reds')  # Use color_scale from Home page
projection = 'natural earth'            # Fixed projection
highlight_countries = []                # No highlights
show_rankings = True                    # Always show rankings
top_n = len(config['countries'])        # Show all countries

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
    "Afghanistan": {"iso": "AFG", "population": "41 million", "gdp": "$94B", "income_group": "Low income", "region": "South Asia"},
    "Bangladesh": {"iso": "BGD", "population": "171 million", "gdp": "$460B", "income_group": "Lower-middle income", "region": "South Asia"},
    "Bhutan": {"iso": "BTN", "population": "0.8 million", "gdp": "$3B", "income_group": "Lower-middle income", "region": "South Asia"},
    "India": {"iso": "IND", "population": "1.43 billion", "gdp": "$3.7T", "income_group": "Lower-middle income", "region": "South Asia"},
    "Maldives": {"iso": "MDV", "population": "0.6 million", "gdp": "$6B", "income_group": "Upper-middle income", "region": "South Asia"},
    "Nepal": {"iso": "NPL", "population": "30 million", "gdp": "$41B", "income_group": "Lower-middle income", "region": "South Asia"},
    "Pakistan": {"iso": "PAK", "population": "231 million", "gdp": "$375B", "income_group": "Lower-middle income", "region": "South Asia"},
    "Sri Lanka": {"iso": "LKA", "population": "22 million", "gdp": "$75B", "income_group": "Lower-middle income", "region": "South Asia"}
}

# Country flags
country_flags = {
    "Bangladesh": "🇧🇩",
    "India": "🇮🇳",
    "Pakistan": "🇵🇰",
    "Nepal": "🇳🇵",
    "Sri Lanka": "🇱🇰",
    "Afghanistan": "🇦🇫",
    "Bhutan": "🇧🇹",
    "Maldives": "🇲🇻",

}


indicator_to_use = str(config['indicator']).strip().lower()

filtered_df = df[
    (df['country'].isin(config['countries'])) &
    (df['year'] >= config['year_range'][0]) &
    (df['year'] <= config['year_range'][1]) &
    (df['indicator'].str.strip().str.lower() == indicator_to_use)
].copy()

# Ensure 'year' is integer for correct chronological animation
filtered_df['year'] = filtered_df['year'].astype(int)

# Sort by country and year for consistent ranking and animation
filtered_df = filtered_df.sort_values(['country', 'year'])

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
#filtered_df['rank'] = filtered_df.groupby('year')['value'].rank(ascending=False, method='min').astype(int)
filtered_df['rank'] = filtered_df.groupby('year')['value'].rank(ascending=True, method='min').astype(int)

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

# Helper function for heat intensity
def get_heat_intensity(value, min_val, max_val):
    range_val = max_val - min_val
    normalized = (value - min_val) / range_val if range_val > 0 else 0

    if normalized < 0.25:
        return "Low", "#27ae60"
    elif normalized < 0.50:
        return "Moderate", "#f39c12"
    elif normalized < 0.75:
        return "High", "#e67e22"
    else:
        return "Critical", "#e74c3c"

# Helper function for trend with percentage
def get_trend_with_percentage(change):
    if pd.isna(change):
        return "➡️ No change", 0
    elif change > 0.5:
        return f"⬆️ +{change:.1f}%", change
    elif change < -0.5:
        return f"⬇️ {change:.1f}%", change
    else:
        return "➡️ Stable", change

# Helper function for achievement badges
def get_achievement_badge(country, year_data):
    badges = []

    # Best performer
    if country == year_data.loc[year_data['value'].idxmin(), 'country']:
        badges.append("Best Performer")

    # Worst performer
    if country == year_data.loc[year_data['value'].idxmax(), 'country']:
        badges.append("⚠️ Needs Attention")

    # Most improved
    year_data_with_change = year_data[year_data['change_from_prev'].notna()]
    if not year_data_with_change.empty:
        if country == year_data_with_change.loc[year_data_with_change['change_from_prev'].idxmin(), 'country']:
            badges.append("Most Improved")
        if country == year_data_with_change.loc[year_data_with_change['change_from_prev'].idxmax(), 'country']:
            badges.append("Most Declined")

    return badges


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
    filtered_df.sort_values('year'),
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

# --------------------------------------------------
# Enhanced colorbar styling with better readability
# --------------------------------------------------
# Calculate tick values dynamically based on data range
value_min = filtered_df['value'].min()
value_max = filtered_df['value'].max()
value_range = value_max - value_min

# Create 7 tick marks across the range
tick_values = [value_min + (i * value_range / 6) for i in range(7)]


fig.update_layout(
    # Title styling
    title=dict(
        text=f"<b>{human_indicator(config['indicator'])} Across South Asia</b>",
        font=dict(size=24, color='#2c3e50', family='Arial Black'),
        x=0.5,
        y=0.95,
        xanchor='center'
    ),

    # Paper and plot background
    paper_bgcolor='#f8f9fa',
    plot_bgcolor='#ffffff',

    # Colorbar configuration
    coloraxis=dict(
        cmin=value_min,
        cmax=value_max,
        colorbar=dict(
            title=dict(
                text=f"<b>{human_indicator(config['indicator'])}</b>",
                font=dict(size=16, color='#2c3e50', family='Arial'),
                side='right'
            ),
            tickfont=dict(size=13, color='#34495e', family='Arial'),
            tickmode='array',
            tickvals=tick_values,
            ticktext=[f"{val:.1f}" for val in tick_values],
            thickness=30,
            len=0.8,
            x=1.02,
            xpad=15,
            outlinewidth=2,
            outlinecolor='#95a5a6',
            bgcolor='rgba(255,255,255,0.95)',
            borderwidth=0,

            # Add tick marks
            ticks='outside',
            ticklen=8,
            tickwidth=2,
            tickcolor='#7f8c8d'
        ),
        colorscale=color_scale
    ),

    # Overall layout dimensions
    height=800,
    margin={'r': 120, 't': 70, 'l': 30, 'b': 30},
    font=dict(family='Arial, sans-serif')
)

# Grey out countries without data
# for feature in geojson['features']:
#     iso = feature['properties']['ISO_A3']
#     if iso not in filtered_df['country_code'].values:
#         fig.add_trace(go.Choropleth(
#             geojson={'type':'FeatureCollection','features':[feature]},
#             locations=[iso],
#             featureidkey='properties.ISO_A3',
#             z=[0],
#             colorscale=[[0,"rgba(200,200,200,0.3)"],[1,"rgba(200,200,200,0.3)"]],
#             showscale=False,
#             hoverinfo='skip',
#             geo='geo'
#         ))

marker_line_width = 5

if highlight_countries:
    for country in highlight_countries:
        iso = get_iso_code(country)
        if iso:
            country_feature = next((f for f in geojson['features'] if f['properties']['ISO_A3'] == iso), None)
            if country_feature:
                fig.add_trace(go.Choropleth(
                    geojson={'type': 'FeatureCollection', 'features': [country_feature]},
                    locations=[iso],
                    featureidkey='properties.ISO_A3',
                    z=[0],
                    colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
                    showscale=False,
                    marker=dict(
                        line=dict(
                            color='#c0392b',  # Deep red
                            width=marker_line_width
                        )
                    ),
                    hoverinfo='skip',
                    geo='geo'
                ))

fig.update_geos(
    fitbounds='locations',
    visible=False,
    #projection_scale=1.2,
    projection_type=projection,
    showcountries=True,
    countrycolor='#bdc3c7',
    countrywidth=1.5,
    coastlinecolor='#34495e',
    coastlinewidth=1,
    landcolor='#ecf0f1',
    oceancolor='#d6eaf8',
    showocean=True,
    showlakes=False,
    bgcolor='#e8f4f8'
)

# --------------------------------------------------
# Enhanced country borders on choropleth
# --------------------------------------------------
fig.update_traces(
    marker_line_color='white',
    marker_line_width=2,
    selector=dict(type='choropleth')
)
for feature in geojson['features']:
    iso = feature['properties']['ISO_A3']
    if iso not in filtered_df['country_code'].values:
        fig.add_trace(go.Choropleth(
            geojson={'type': 'FeatureCollection', 'features': [feature]},
            locations=[iso],
            featureidkey='properties.ISO_A3',
            z=[0],
            colorscale=[[0, "rgba(220,220,220,0.4)"], [1, "rgba(220,220,220,0.4)"]],
            showscale=False,
            hoverinfo='skip',
            geo='geo',
            marker_line_color='#95a5a6',
            marker_line_width=1
        ))


# Calculate the initial frame (latest year)
available_years_for_map = sorted(filtered_df['year'].unique())
latest_year_index = len(available_years_for_map) - 1

if show_animation and fig.layout.updatemenus:
    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = animation_speed
    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 300

    # Style the animation buttons and sliders with visible text and better positioning
    fig.update_layout(
        updatemenus=[dict(
            type='buttons',
            showactive=True,
            bgcolor='#ecf0f1',
            bordercolor='#95a5a6',
            borderwidth=2,
            font=dict(size=12, color='#2c3e50'),
            x=0.18,  # Move buttons more to the left
            y=0.05,  # Lower position
            xanchor='left',
            yanchor='bottom'
        )],
        sliders=[dict(
            active=latest_year_index,  # Start at the latest year
            yanchor='bottom',
            y=0.01,  # Lower position to match buttons
            xanchor='left',
            x=0.25,  # Move slider to the right to avoid overlap
            currentvalue=dict(
                prefix='Year: ',
                visible=True,
                font=dict(size=16, color='#2c3e50', family='Arial Black'),
                xanchor='left'
            ),
            pad=dict(b=10, t=50),
            len=0.65,  # Slightly shorter to fit better
            font=dict(size=12, color='#2c3e50'),
            bgcolor='#ecf0f1',
            bordercolor='#95a5a6',
            borderwidth=2,
            tickcolor='#34495e',
            ticklen=8
        )]
    )
else:
    fig.update_layout(updatemenus=[])

# # Display the map
st.plotly_chart(fig, use_container_width=True, theme=None)
# st.plotly_chart(fig, width='stretch', config={'displayModeBar': True})

def create_tiny_country_map(iso_code, geojson):
    feature = next(
        (f for f in geojson['features'] if f['properties']['ISO_A3'] == iso_code),
        None
    )
    if feature is None:
        return None

    fig = go.Figure(go.Choropleth(
        geojson={'type': 'FeatureCollection', 'features': [feature]},
        locations=[iso_code],
        featureidkey='properties.ISO_A3',
        z=[1],
        colorscale=[[0, '#2c7fb8'], [1, '#2c7fb8']],
        showscale=False,
        marker_line_color='black',
        marker_line_width=0.4
    ))

    fig.update_geos(
        fitbounds="locations",
        visible=False,
        bgcolor="rgba(0,0,0,0)"
    )

    fig.update_layout(
        height=65,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)"
    )

    return fig
st.markdown(
    "<h4 style='margin-top:8px; margin-bottom:6px;'>Country Key</h4>",
    unsafe_allow_html=True
)

countries_in_map = sorted(config['countries'])

cols_per_row = 8  # more compact
rows = [countries_in_map[i:i + cols_per_row]
        for i in range(0, len(countries_in_map), cols_per_row)]

for row in rows:
    cols = st.columns(len(row))
    for col, country in zip(cols, row):
        iso = country_metadata.get(country, {}).get("iso")
        #flag = country_flags.get(country, "🏳️")

        with col:
            mini_fig = create_tiny_country_map(iso, geojson)

            if mini_fig:
                # Fit map tightly and set white backgrounds
                mini_fig.update_geos(
                    fitbounds="locations",
                    visible=False,
                    bgcolor= "#87C1E5" 
                )

                mini_fig.update_layout(
                    height=80,
                    margin=dict(l=0, r=0, t=0, b=0),
                    paper_bgcolor="black"  # figure background white
                )

                st.plotly_chart(
                    mini_fig,
                    use_container_width=True,
                    #width='stretch',
                    config={"displayModeBar": False}
                    #config={'displayModeBar': False, 'staticPlot': True} 
                )
                # Add country name below the map
                st.markdown(
                    f"<p style='text-align:center; font-size:10px; margin-top:-10px; color:#ffffff;'><b>{country}</b></p>",
                    unsafe_allow_html=True
                )

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
        "Select Year for Detailed Insights",
        min_value=int(available_years[0]),
        max_value=int(available_years[-1]),
        value=int(available_years[-1])
    )

# --------------------------------------------------
# Enhanced Storytelling with Visual Indicators
# --------------------------------------------------
st.markdown("---")

# Get data for selected year
year_data = filtered_df[filtered_df['year'] == selected_year].copy()

if not year_data.empty:
    # Calculate key statistics
    best_country = year_data.loc[year_data['value'].idxmin(), 'country']
    best_value = year_data['value'].min()
    worst_country = year_data.loc[year_data['value'].idxmax(), 'country']
    worst_value = year_data['value'].max()
    avg_value = year_data['value'].mean()
    value_range = worst_value - best_value

    # Get flags
    best_flag = country_flags.get(best_country)
    worst_flag = country_flags.get(worst_country)


    # Heat intensity for region
    regional_heat, regional_color = get_heat_intensity(avg_value, value_min, value_max)

    # Calculate year-over-year change if available
    if selected_year > available_years[0]:
        prev_year_data = filtered_df[filtered_df['year'] == selected_year - 1]
        if not prev_year_data.empty:
            prev_avg = prev_year_data['value'].mean()
            regional_change = avg_value - prev_avg
            trend_text = "increased" if regional_change > 0 else "decreased"
            trend_arrow = "📈" if regional_change < 0 else "📉"
            has_comparison = True
        else:
            has_comparison = False
    else:
        has_comparison = False

# --------------------------------------------------
# Interactive Country Spotlight Cards
# --------------------------------------------------
st.markdown("---")
st.markdown("### Country Spotlight")

# Country selector
selected_country_spotlight = st.selectbox(
    "Choose a country to spotlight:",
    options=['-- Select a country --'] + sorted(config['countries']),
    key='spotlight_selector'
)

if selected_country_spotlight != '-- Select a country --':
    country_year_data = year_data[year_data['country'] == selected_country_spotlight]

    if not country_year_data.empty:
        country_info = country_year_data.iloc[0]
        flag = country_flags.get(selected_country_spotlight)

        # Create spotlight card with custom styling
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 30px; border-radius: 15px; color: white; margin: 20px 0;">
            <h2 style="margin: 0; font-size: 2.5em;">{flag} {selected_country_spotlight}</h2>
            <p style="opacity: 0.9; margin-top: 10px;">Year {selected_year} Performance Analysis</p>
        </div>
        """, unsafe_allow_html=True)

        # Key metrics in colorful boxes
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            heat_label, heat_color = get_heat_intensity(
                country_info['value'],
                year_data['value'].min(),
                year_data['value'].max()
            )
            st.markdown(f"""
            <div style="background: {heat_color}; padding: 20px; border-radius: 10px; text-align: center;">
                <h3 style="color: white; margin: 0;">Intensity</h3>
                <p style="color: white; font-size: 1.5em; margin: 10px 0;">{heat_label}</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.metric(
                "Current Value",
                f"{country_info['value']:.2f}",
                delta=f"{country_info['change_from_prev']:.2f}" if pd.notna(country_info['change_from_prev']) else "N/A",
                delta_color='inverse'
            )

        with col3:
            rank_total = len(year_data)
            st.metric(
                "Regional Rank",
                f"#{int(country_info['rank'])}",
                delta=f"of {rank_total} countries"
            )

        with col4:
            diff_from_avg = country_info['value'] - country_info['regional_avg']
            st.metric(
                "vs Regional Avg",
                f"{diff_from_avg:+.2f}",
                delta="Above" if diff_from_avg > 0 else "Below",
                delta_color='inverse'
            )

        # Achievement badges
        badges = get_achievement_badge(selected_country_spotlight, year_data)
        if badges:
            st.markdown("**Achievements:**")
            badge_cols = st.columns(len(badges))
            for i, badge in enumerate(badges):
                with badge_cols[i]:
                    st.info(badge)

        # Mini sparkline chart
        country_history = filtered_df[filtered_df['country'] == selected_country_spotlight].sort_values('year')

        if len(country_history) > 1:
            st.markdown("**Historical Trend:**")

            sparkline_fig = go.Figure()

            sparkline_fig.add_trace(go.Scatter(
                x=country_history['year'],
                y=country_history['value'],
                mode='lines+markers',
                name=selected_country_spotlight,
                line=dict(color='#667eea', width=3),
                marker=dict(size=10, color='#764ba2'),
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.2)'
            ))

            # Add regional average line
            regional_trend = filtered_df.groupby('year')['value'].mean().reset_index()
            sparkline_fig.add_trace(go.Scatter(
                x=regional_trend['year'],
                y=regional_trend['value'],
                mode='lines',
                name='Regional Average',
                line=dict(color='#95a5a6', width=2, dash='dash')
            ))

            sparkline_fig.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=30, b=0),
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
            )

            st.plotly_chart(sparkline_fig, use_container_width=True , config={'displayModeBar': False}, key="country_sparkline_chart")  #use_container_width=True

        # Quick comparison to regional average
        st.markdown("**Quick Comparison:**")
        comparison_text = ""

        if diff_from_avg > 5:
            comparison_text = f"⚠️ {selected_country_spotlight} is **{abs(diff_from_avg):.2f} points above** the regional average, indicating higher inequality than most countries in the region."
        elif diff_from_avg < -5:
            comparison_text = f"{selected_country_spotlight} is **{abs(diff_from_avg):.2f} points below** the regional average, performing better than most countries in the region."
        else:
            comparison_text = f"{selected_country_spotlight} is **near the regional average**, with a difference of only {abs(diff_from_avg):.2f} points."

        st.info(comparison_text)

    else:
        st.warning(f"⚠️ No data available for {selected_country_spotlight} in {selected_year}")

#Storytelling narrative with visual elements
st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 30px; border-radius: 15px; color: white; margin-bottom: 30px;">
        <h2 style="margin: 0;">South Asia in {selected_year}: A Story of Inequality</h2>
        <p style="opacity: 0.9; margin-top: 10px; font-size: 1.1em;">
            Regional Intensity: {regional_heat}
        </p>
    </div>
    """, unsafe_allow_html=True)

    #The Overview
st.markdown(f"Summary of **{human_indicator(config['indicator']).lower()}**")
st.markdown(f"""
    In **{selected_year}**, the landscape of **{human_indicator(config['indicator']).lower()}** across South Asia
    painted a complex picture of regional disparities. Among the **{len(year_data)} countries** analyzed,
    the gap between the best and worst performers stood at **{value_range:.2f} points** — a stark reminder
    of the diverse economic realities within the region.
    """)

    # Visual indicator boxes
col1, col2, col3 = st.columns(3)

with col1:
        st.markdown(f"""
        <div style="background: #4B5BD5; padding: 15px; border-radius: 10px; text-align: center;">
            <h3 style="color: white; margin: 0;"> Country with Highest Value </h3>
            <p style="color: white; font-size: 1.5em; margin: 10px 0;">{best_country}</p>
            <p style="color: white; margin: 5px 0;">{best_value:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

with col2:
        st.markdown(f"""
        <div style="background: #8B5CF6; padding: 15px; border-radius: 10px; text-align: center;">
            <h3 style="color: white; margin: 0;">Regional Avg</h3>
            <p style="color: white; font-size: 1.5em; margin: 10px 0;">{avg_value:.2f}</p>
            <p style="color: white; margin: 5px 0;">{regional_heat.split()[1] if len(regional_heat.split()) > 1 else regional_heat}</p>
        </div>
        """, unsafe_allow_html=True)

with col3:
        st.markdown(f"""
        <div style="background: #F472B6; padding: 15px; border-radius: 10px; text-align: center;">
            <h3 style="color: white; margin: 0;">Country with Lowest Value</h3>
            <p style="color: white; font-size: 1.5em; margin: 10px 0;">{worst_country}</p>
            <p style="color: white; margin: 5px 0;">{worst_value:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


#     # Chapter 5: The Dynamics
# year_data_with_change = year_data[year_data['change_from_prev'].notna()]
# if not year_data_with_change.empty:
#         most_improved = year_data_with_change.loc[year_data_with_change['change_from_prev'].idxmin()]
#         most_declined = year_data_with_change.loc[year_data_with_change['change_from_prev'].idxmax()]

#         improved_flag = country_flags.get(most_improved['country'])
#         declined_flag = country_flags.get(most_declined['country'])

#         st.markdown("### Biggest Changes: Progress and Setbacks")

#         col1, col2 = st.columns(2)

#         with col1:
#             st.markdown(f"""
#             <div style="background: linear-gradient(135deg, #27ae60, #2ecc71);
#                         padding: 20px; border-radius: 10px; color: white;">
#                 <h4 style="margin: 0;">Most Improved</h4>
#                 <p style="font-size: 2em; margin: 10px 0;">{improved_flag} {most_improved['country']}</p>
#                 <p style="font-size: 1.5em; margin: 0;">⬇️ {abs(most_improved['change_from_prev']):.2f} points</p>
#             </div>
#             """, unsafe_allow_html=True)

#         with col2:
#             st.markdown(f"""
#             <div style="background: linear-gradient(135deg, #e74c3c, #c0392b);
#                         padding: 20px; border-radius: 10px; color: white;">
#                 <h4 style="margin: 0;">Most Declined</h4>
#                 <p style="font-size: 2em; margin: 10px 0;">{declined_flag} {most_declined['country']}</p>
#                 <p style="font-size: 1.5em; margin: 0;">⬆️ +{most_declined['change_from_prev']:.2f} points</p>
#             </div>
#             """, unsafe_allow_html=True)

#         st.markdown("<br>", unsafe_allow_html=True)

#         st.markdown(f"""
#         These movements underscore the fluid nature of economic inequality and the varying policy effectiveness across the region.
#         """)


    # Find most improved and most declined if data exists
year_data_with_change = year_data[year_data['change_from_prev'].notna()]
if not year_data_with_change.empty:
        most_improved = year_data_with_change.loc[year_data_with_change['change_from_prev'].idxmin()]
        most_declined = year_data_with_change.loc[year_data_with_change['change_from_prev'].idxmax()]

        st.markdown(f"""
        **Year-over-year dynamics** revealed interesting shifts: **{most_improved['country']}** showed the most
        improvement, reducing inequality by **{abs(most_improved['change_from_prev']):.2f} points**, while
        **{most_declined['country']}** experienced a setback with an increase of **{most_declined['change_from_prev']:.2f} points**.
        These movements underscore the fluid nature of economic inequality and the varying policy effectiveness across the region.
        """)

if show_rankings:
    st.divider()
    st.subheader("Country Rankings")

    # --- UPDATED: show rankings from 2000 to latest year at 2-year intervals ---
    all_years = sorted(filtered_df['year'].unique())
    start_year = 2000
    latest_year = max(all_years)

    years = [y for y in all_years if y >= start_year and y % 2 == 0]

    # Ensure latest year is included even if it's not an even year
    if latest_year not in years:
        years.append(latest_year)

    years = sorted(years, reverse=True)

    tabs = st.tabs([str(y) for y in years])

    for tab, year in zip(tabs, years):
        with tab:
            year_df = filtered_df[filtered_df['year'] == year].sort_values('value', ascending=False).head(top_n)

            rankings_df = year_df[['rank','country','value','regional_avg','change_from_prev','trend_arrow']].copy()
            rankings_df.columns = [
                'Rank','Country',human_indicator(config['indicator']),'Regional Average','Change from Prev Year','Trend'
            ]


            rankings_df['Difference from Avg'] = (rankings_df[human_indicator(config['indicator'])] - rankings_df['Regional Average']).round(2)
            rankings_df['Status'] = rankings_df['Difference from Avg'].apply(
                lambda x: 'Above avg' if x>5 else 'Below avg' if x<-5 else 'Near avg'
            )
            st.dataframe(rankings_df, use_container_width=True, hide_index=True) # use_container_width=True
# --------------------------------------------------
# Export Section - Add this at the end of your code
# --------------------------------------------------
st.divider()
st.markdown("### Export Options")

try:
    # Create tabs for different export types
    export_tab1, export_tab2 = st.tabs(["Data Export", "Visualization Export"])
    
    with export_tab1:
        st.markdown("### Download Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Data export options
            export_format = st.selectbox(
                "Select data format",
                ["CSV", "Excel (XLSX)", "JSON", "TSV"]
            )
        
        with col2:
            # Data selection
            data_selection = st.selectbox(
                "Select dataset",
                [
                    "Current Year Data",
                    "Full Time Series",
                    "Rankings (Current Year)",
                    "Complete Dataset (All Years + Metadata)"
                ]
            )
        
        # Prepare different datasets based on selection
        if data_selection == "Current Year Data":
            export_df = year_data[[
                'country', 'country_code', 'value', 'rank', 'regional_avg', 
                'change_from_prev', 'trend_arrow', 'population', 'gdp', 'income_group'
            ]].copy()
            export_df.columns = [
                'Country', 'Code', human_indicator(config['indicator']), 
                'Rank', 'Regional Avg', 'YoY Change', 'Trend', 
                'Population', 'GDP', 'Income Group'
            ]
            filename_base = f"Data_{config['indicator']}_{selected_year}".replace(" ", "_")
            
        elif data_selection == "Full Time Series":
            export_df = filtered_df[[
                'country', 'country_code', 'year', 'value', 'rank', 
                'regional_avg', 'change_from_prev'
            ]].copy()
            export_df.columns = [
                'Country', 'Code', 'Year', human_indicator(config['indicator']), 
                'Rank', 'Regional Avg', 'Change'
            ]
            filename_base = f"TimeSeries_{config['indicator']}_{config['year_range'][0]}-{config['year_range'][1]}".replace(" ", "_")
            
        elif data_selection == "Rankings (Current Year)":
            export_df = year_data.sort_values('rank')[[
                'rank', 'country', 'value', 'regional_avg', 'change_from_prev'
            ]].copy()
            export_df.columns = [
                'Rank', 'Country', human_indicator(config['indicator']), 
                'Regional Avg', 'YoY Change'
            ]
            export_df['Difference from Avg'] = (
                export_df[human_indicator(config['indicator'])] - export_df['Regional Avg']
            ).round(2)
            filename_base = f"Rankings_{config['indicator']}_{selected_year}".replace(" ", "_")
            
        else:  # Complete Dataset
            export_df = filtered_df.copy()
            filename_base = f"Complete_{config['indicator']}_Dataset".replace(" ", "_")
        
        # Add metadata
        metadata = {
            "Indicator": config['indicator'],
            "Selected_Year": selected_year,
            "Year_Range": f"{config['year_range'][0]}-{config['year_range'][1]}",
            "Countries": len(config['countries']),
            "Export_Date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Color_Scale": color_scale
        }
        
        # Display preview
        with st.expander("Preview data", expanded=False):
            st.dataframe(export_df.head(10), use_container_width=True) #use_container_width=True
            st.caption(f"Showing first 10 of {len(export_df)} rows")
        
        # Export based on format
        if export_format == "CSV":
            csv_data = export_df.to_csv(index=False)
            st.download_button(
                label=f"⬇Download as CSV",
                data=csv_data,
                file_name=f"{filename_base}.csv",
                mime="text/csv",
                #width='stretch',
                use_container_width=True
            )
            
        elif export_format == "Excel (XLSX)":
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Sheet 1: Main Data
                export_df.to_excel(writer, sheet_name='Data', index=False)
                
                # Sheet 2: Summary Statistics (if current year)
                if data_selection == "Current Year Data":
                    summary_df = pd.DataFrame({
                        'Metric': [
                            'Best Performer',
                            'Best Value',
                            'Worst Performer',
                            'Worst Value',
                            'Regional Average',
                            'Standard Deviation',
                            'Value Range',
                            'Countries Analyzed'
                        ],
                        'Value': [
                            year_data.loc[year_data['value'].idxmin(), 'country'],
                            f"{year_data['value'].min():.2f}",
                            year_data.loc[year_data['value'].idxmax(), 'country'],
                            f"{year_data['value'].max():.2f}",
                            f"{year_data['value'].mean():.2f}",
                            f"{year_data['value'].std():.2f}",
                            f"{year_data['value'].max() - year_data['value'].min():.2f}",
                            len(year_data)
                        ]
                    })
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Sheet 3: Year-over-Year Changes (if time series)
                if data_selection == "Full Time Series":
                    yoy_changes = filtered_df.groupby('country').agg({
                        'change_from_prev': ['mean', 'std', 'min', 'max']
                    }).round(2)
                    yoy_changes.columns = ['Avg Change', 'Std Dev', 'Min Change', 'Max Change']
                    yoy_changes.reset_index().to_excel(writer, sheet_name='YoY_Changes', index=False)
                
                # Sheet 4: Metadata
                metadata_df = pd.DataFrame([metadata])
                metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
                
                # Sheet 5: Country Metadata
                country_meta_list = []
                for country in config['countries']:
                    if country in country_metadata:
                        meta = country_metadata[country]
                        country_meta_list.append({
                            'Country': country,
                            'ISO Code': meta['iso'],
                            'Population': meta['population'],
                            'GDP': meta['gdp'],
                            'Income Group': meta['income_group'],
                            'Region': meta['region']
                        })
                if country_meta_list:
                    country_meta_df = pd.DataFrame(country_meta_list)
                    country_meta_df.to_excel(writer, sheet_name='Country_Info', index=False)
            
            output.seek(0)
            st.download_button(
                label=f"Download as Excel",
                data=output,
                file_name=f"{filename_base}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                #width='stretch',
                use_container_width=True
            )
            st.caption("Contains multiple sheets: Data, Summary, Metadata, and Country Info")
            
        elif export_format == "JSON":
            json_data = export_df.to_json(orient='records', indent=2)
            st.download_button(
                label=f"Download as JSON",
                data=json_data,
                file_name=f"{filename_base}.json",
                mime="application/json",
                #width='stretch',
                use_container_width=True
            )
            
        else:  # TSV
            tsv_data = export_df.to_csv(index=False, sep='\t')
            st.download_button(
                label=f"⬇Download as TSV",
                data=tsv_data,
                file_name=f"{filename_base}.tsv",
                mime="text/tab-separated-values",
                #width='stretch',
                use_container_width=True
            )
    
    with export_tab2:
        st.markdown("### Download Visualization")
        
        col1, col2 = st.columns(2)
        
        with col1:
            viz_format = st.selectbox(
                "Select image format",
                ["PNG (High Quality)", "SVG (Vector)", "PDF", "HTML (Interactive)", "JPEG"]
            )
        
        with col2:
            viz_size = st.selectbox(
                "Select size/resolution",
                ["Standard (1200x800)", "Large (1920x1080)", "Extra Large (2560x1440)", "Print Quality (3840x2160)"]
            )
        
        # Parse size
        size_map = {
            "Standard (1200x800)": (1200, 800),
            "Large (1920x1080)": (1920, 1080),
            "Extra Large (2560x1440)": (2560, 1440),
            "Print Quality (3840x2160)": (3840, 2160)
        }
        width, height = size_map[viz_size]
        
        st.info(f"Current visualization: **Animated Choropleth Map - Year {selected_year}**")
        
        # Note about format compatibility
        if viz_format in ["PNG (High Quality)", "JPEG"]:
            st.caption(f"Static image - {width}x{height}px - good for presentations and documents")
        elif viz_format == "SVG (Vector)":
            st.caption("Vector format - scalable without quality loss, ideal for publications")
        elif viz_format == "PDF":
            st.caption("PDF format - ideal for reports and printing")
        else:
            st.caption("Interactive HTML - preserves hover effects, animation, and interactivity")
        
        # Generate filename
        viz_filename = f"Map_{config['indicator']}_{selected_year}".replace(" ", "_")
        
        # Format-specific download buttons
        if viz_format == "HTML (Interactive)":
            try:
                html_bytes = fig.to_html(include_plotlyjs='cdn').encode('utf-8')
                st.download_button(
                    "⬇Download HTML",
                    data=html_bytes,
                    file_name=f"{viz_filename}.html",
                    mime="text/html",
                    #width='stretch',
                    use_container_width=True
                )
                st.success("HTML export ready - includes full animation and interactivity")
            except Exception as e:
                st.error(f"❌ HTML export failed: {str(e)}")
            
        elif viz_format == "SVG (Vector)":
            try:
                img_bytes_svg = fig.to_image(format='svg', width=width, height=height)
                st.download_button(
                    "Download SVG",
                    data=img_bytes_svg,
                    file_name=f"{viz_filename}.svg",
                    mime="image/svg+xml",
                    #width='stretch'
                    use_container_width=True
                )
                st.success("SVG export ready - editable in vector software")
            except Exception as e:
                st.error("Image export unavailable. Install Kaleido: `pip install kaleido`")
                st.caption("Run: `pip install kaleido` in your terminal")
            
        elif viz_format == "PDF":
            try:
                pdf_bytes = fig.to_image(format='pdf', width=width, height=height)
                st.download_button(
                    "Download PDF",
                    data=pdf_bytes,
                    file_name=f"{viz_filename}.pdf",
                    mime="application/pdf",
                    #width='stretch',
                    use_container_width=True
                )
                st.success("PDF export ready - ideal for reports")
            except Exception as e:
                st.error("❌ Image export unavailable. Install Kaleido: `pip install kaleido`")
                st.caption("Run: `pip install kaleido` in your terminal")
            
        elif viz_format == "PNG (High Quality)":
            try:
                img_bytes_png = fig.to_image(format='png', width=width, height=height)
                st.download_button(
                    "⬇Download PNG",
                    data=img_bytes_png,
                    file_name=f"{viz_filename}.png",
                    mime="image/png",
                    #width='stretch',
                    use_container_width=True
                )
                st.success(f"PNG export ready - {width}x{height}px")
            except Exception as e:
                st.error("❌ Image export unavailable. Install Kaleido: `pip install kaleido`")
                st.caption("Run: `pip install kaleido` in your terminal")
        
        else:  # JPEG
            try:
                img_bytes_jpg = fig.to_image(format='jpeg', width=width, height=height)
                st.download_button(
                    "Download JPEG",
                    data=img_bytes_jpg,
                    file_name=f"{viz_filename}.jpg",
                    mime="image/jpeg",
                    #width='stretch',
                    use_container_width=True
                )
                st.success(f"JPEG export ready - {width}x{height}px")
            except Exception as e:
                st.error("❌ Image export unavailable. Install Kaleido: `pip install kaleido`")
                st.caption("Run: `pip install kaleido` in your terminal")
        # Bulk export section
        st.markdown("---")
        st.markdown("###Bulk Export Options")
        
        if st.checkbox("Export complete package (All formats + Data)"):
            st.warning("⚠️ This will generate multiple files. Make sure you have enough storage space.")
            
            bulk_formats = st.multiselect(
                "Select formats for bulk export",
                ["PNG", "HTML", "CSV Data", "Excel Summary"],
                default=["PNG", "CSV Data"]
            )
            
            if st.button("Generate Bulk Export Package", use_container_width=True): #use_container_width=True
                with st.spinner("Generating export package..."):
                    try:
                        # Create ZIP file with multiple exports
                        from io import BytesIO
                        import zipfile
                        
                        zip_buffer = BytesIO()
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                            # Add selected formats
                            if "PNG" in bulk_formats:
                                try:
                                    png_data = fig.to_image(format='png', width=1920, height=1080)
                                    zip_file.writestr(f"{viz_filename}.png", png_data)
                                except:
                                    pass
                            
                            if "HTML" in bulk_formats:
                                html_data = fig.to_html(include_plotlyjs='cdn')
                                zip_file.writestr(f"{viz_filename}.html", html_data)
                            
                            if "CSV Data" in bulk_formats:
                                csv_data = export_df.to_csv(index=False)
                                zip_file.writestr(f"{filename_base}.csv", csv_data)
                            
                            if "Excel Summary" in bulk_formats:
                                excel_buffer = BytesIO()
                                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                                    export_df.to_excel(writer, sheet_name='Data', index=False)
                                    metadata_df = pd.DataFrame([metadata])
                                    metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
                                zip_file.writestr(f"{filename_base}.xlsx", excel_buffer.getvalue())
                        
                        zip_buffer.seek(0)
                        st.download_button(
                            "Download Complete Package (ZIP)",
                            data=zip_buffer,
                            file_name=f"Export_Package_{config['indicator']}_{selected_year}.zip",
                            mime="application/zip",
                            #width='stretch',
                            use_container_width=True
                        )
                        st.success("Export package ready for download!")
                    except Exception as e:
                        st.error(f"❌ Error creating export package: {str(e)}")
                        st.info("Try exporting files individually instead")

except Exception as e:
    st.error(f"❌ Error in export section: {str(e)}")
    st.caption("Please try a different export format or contact support if the issue persists.")
# --------------------------------------------------
# Footer
# --------------------------------------------------
st.divider()
st.caption("Map Analysis | South Asia Inequality Analysis Platform")
st.caption("Data sources: World Bank, UNDP | Map boundaries: Natural Earth")
st.caption("Enhanced with dynamic insights, country highlighting, projections, and advanced filtering")
