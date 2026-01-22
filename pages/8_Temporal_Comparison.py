import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.stats import ttest_rel
import sys
from pathlib import Path
import numpy as np
import json 

# --------------------------------------------------
# Path setup
# --------------------------------------------------
sys.path.append(str(Path(__file__).parent.parent))
from utils.help_system import render_help_button
from utils.sidebar import apply_all_styles
from utils.loaders import load_inequality_data, load_geojson
from utils.utils import (
    human_indicator,
    get_color_scale,
    handle_missing_data,
    validate_dataframe,
    format_value,
    safe_divide
)
from utils.indicator_metadata import (
    get_available_indicators_by_category,
    get_indicator_description
)

# --------------------------------------------------
# CONSTANTS
# --------------------------------------------------
MIN_STATISTICAL_TEST_SIZE = 5
TIER_THRESHOLD = 6  # Use 3 tiers if <= 6 countries, 4 tiers if more

# Eurostat-style color palette
EUROSTAT_COLORS = {
    'diverging': [
        [0.0, "#160216"],
        [0.25, "#5A3C5A"],
        [0.5, "#FAFAFB"],
        [0.75, "#1C91C8"],
        [1.0, "#1F4F82"]
    ]
}

# ADD THIS NEW HELPER FUNCTION
def add_country_labels_to_map(fig, data, geojson):
    """Add country name labels to choropleth map."""
    for _, row in data.iterrows():
        iso = row['country_code']
        country_feature = next(
            (f for f in geojson['features'] if f['properties']['ISO_A3'] == iso), 
            None
        )
        
        if not country_feature:
            continue
            
        coords = country_feature['geometry']['coordinates']
        
        if country_feature['geometry']['type'] == 'Polygon':
            lons = [c[0] for c in coords[0]]
            lats = [c[1] for c in coords[0]]
        elif country_feature['geometry']['type'] == 'MultiPolygon':
            lons = [c[0] for c in coords[0][0]]
            lats = [c[1] for c in coords[0][0]]
        else:
            continue
        
        center_lon = sum(lons) / len(lons)
        center_lat = sum(lats) / len(lats)
        
        fig.add_scattergeo(
            lon=[center_lon],
            lat=[center_lat],
            text=row['country'],
            mode='text',
            textfont=dict(size=10, color='black', family='Arial'),
            showlegend=False,
            hoverinfo='skip'
        )
    
    return fig
def style_choropleth_map(fig):
    """Apply consistent styling to choropleth maps."""
    
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        showcountries=True,
        countrycolor='#bdc3c7',
        countrywidth=1.5,
        coastlinecolor='#34495e',
        coastlinewidth=1,
        landcolor='#ecf0f1',
        oceancolor='#d6eaf8',
        showocean=True,
        showlakes=False,
        bgcolor='#e8f4f8',
        scope='world'
    )
    
    fig.update_layout(
        paper_bgcolor="rgba(52, 26, 87, 0.28)",
        plot_bgcolor="#ffffff",
        margin={'r': 10, 't': 30, 'l': 10, 'b': 10},
        font=dict(family='Arial, sans-serif')
    )
    
    return fig
# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Temporal Comparison",
    layout="wide"
)
render_help_button("temporal")
apply_all_styles()
st.title("Temporal Comparison")
st.caption("Temporal, spatial, and statistical comparison of inequality indicators")

# Display current configuration from home page
if 'analysis_config' in st.session_state and st.session_state.analysis_config:
    config = st.session_state.analysis_config

    st.markdown(
        f"Period: **{config['year_range'][0]}–{config['year_range'][1]}** | "
        f"Countries: **{len(config['countries'])}** selected"
    )

    with st.expander("View Full Configuration"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Selected Countries:**")
            st.write(", ".join(config['countries']))
        with col2:
            st.write("**Indicator:**", human_indicator(config['indicator']))
            st.write("**Year Range:**", f"{config['year_range'][0]} - {config['year_range'][1]}")
            st.write("**Color Scheme:**", config['color_scale'])

def render_visualization_help(viz_type: str):
    """
    Render specific help for visualization types in temporal comparison
    """
    
    viz_help = {
        "Map": {
            "title": "How to Read Side-by-Side Choropleth Maps",
            "content": """
            **What you're seeing:**
            - **Left map (THEN):** Shows the earlier time period's values
            - **Right map (NOW):** Shows the later time period's values
            - **Color intensity:** Based on your selected color scheme
            - **Country labels:** Visible on the map for easy identification
            
            **How to interpret:**
            - Compare the same country across both maps to see changes
            - Color changes indicate whether values increased or decreased
            - Hover over countries to see exact values and changes
            - Geographic patterns show regional trends
            
            **Color scales:**
            Your selected color scheme from the home page configuration is applied to all visualizations for consistency.
            
            **Best for:**
            - Understanding geographic shifts in patterns
            - Seeing which regions improved vs. declined
            - Visual storytelling about temporal change
            - Identifying spatial clusters
            """
        },
        "Bar Chart": {
            "title": "How to Read the Comparison Bar Chart",
            "content": """
            **What you're seeing:**
            - Two separate bar charts side-by-side
            - **Left chart:** THEN period values (all countries)
            - **Right chart:** NOW period values (all countries)
            - Countries sorted by value magnitude
            
            **How to interpret:**
            - Find the same country in both charts to compare
            - Color intensity indicates value magnitude
            - Chart uses same color scale for consistency
            - Bars are ordered independently in each period
            
            **What to look for:**
            - Countries that changed position significantly
            - Overall distribution shifts (more/less inequality)
            - Extreme values (top and bottom performers)
            
            **Best for:**
            - Quickly comparing magnitudes across countries
            - Identifying rank changes between periods
            - Spotting outliers or exceptional cases
            - Understanding overall distribution changes
            """
        },
        "Scatter Plot": {
            "title": "How to Read the Scatter Plot",
            "content": """
            **What you're seeing:**
            - **X-axis:** THEN period values
            - **Y-axis:** NOW period values
            - **Red diagonal line:** Line of no change
            - **Point color:** Represents the absolute change (NOW - THEN)
            - Each point represents one country
            
            **How to interpret:**
            - Points **below the diagonal** = values decreased
            - Points **above the diagonal** = values increased
            - Points **on the diagonal** = no change
            - Distance from line = magnitude of change
            - Color intensity shows change magnitude
            
            **For inequality indicators (lower is better):**
            - Below diagonal = improved (inequality decreased)
            - Above diagonal = worsened (inequality increased)
            
            **For positive indicators (higher is better):**
            - Above diagonal = improved (values increased)
            - Below diagonal = worsened (values decreased)
            
            **Best for:**
            - Seeing correlation between past and present
            - Identifying countries that bucked trends
            - Understanding if high-value countries changed more/less
            - Spotting outliers visually
            """
        },
        "Ranking Shift": {
            "title": "How to Read Ranking Changes Scatter Plot",
            "content": """
            **What you're seeing:**
            - **X-axis:** Rank in THEN period (reversed scale)
            - **Y-axis:** Rank in NOW period (reversed scale)
            - **Red diagonal line:** Line of no rank change
            - **Point color:** Rank improvement (negative of rank change)
            - Each point represents one country
            
            **How to interpret:**
            - Points **below the diagonal** = improved ranking (moved to better/lower rank number)
            - Points **above the diagonal** = worsened ranking (moved to worse/higher rank number)
            - Points **on the diagonal** = maintained same rank
            - Both axes are reversed so better ranks (1, 2, 3) appear at top/left
            
            **Important notes:**
            - Rankings are **relative**, not absolute
            - A country can worsen in absolute terms but improve in rank if others worsened more
            - Rank improvement is calculated as: THEN rank - NOW rank
            - Positive rank improvement = moved to a better (lower) rank number
            
            **Best for:**
            - Understanding competitive positioning
            - Tracking relative progress among peers
            - Identifying which countries moved up/down in rankings
            - Comparing relative vs. absolute performance
            """
        },
        "Distribution": {
            "title": "How to Read Distribution Comparison",
            "content": """
            **What you're seeing:**
            - Box plots showing data distribution for THEN and NOW periods
            - **Box** = middle 50% of values (interquartile range)
            - **Line in box** = median value
            - **Whiskers** = extend to min/max within 1.5× IQR
            - **Individual dots** = all country data points
            - Hover over dots to see which country
            
            **Color scheme:**
            Your selected color scheme from the home page is used consistently across both periods for direct comparison.
            
            **Statistics table shows:**
            - **Mean:** Average value across all countries
            - **Median:** Middle value (50th percentile)
            - **Std Dev:** How spread out the values are
            - **Min/Max:** Extreme values
            - **Range:** Difference between max and min
            
            **How to interpret:**
            - **Vertical position:** Overall level (higher = larger values)
            - **Box width:** Spread of middle 50% of countries
            - **Box shift:** If NOW box is lower = overall improvement (for inequality)
            - **Narrower box:** Countries converging (less dispersion)
            - **Wider box:** Countries diverging (more dispersion)
            
            **Key insights:**
            - Compare medians to see if typical country improved
            - Compare ranges to see if extremes changed
            - Look at outlier dots to identify exceptional countries
            
            **Best for:**
            - Understanding regional inequality trends
            - Seeing if countries are converging or diverging
            - Identifying outliers and extreme cases
            - Statistical overview of changes
            """
        },
        "Delta Map": {
            "title": "How to Read Delta (Change) Map",
            "content": """
            **What you're seeing:**
            - Single choropleth map showing **change** between periods (NOW - THEN)
            - Uses your selected color scheme from home page configuration
            - Country labels for significant changes (top/bottom 20%)
            
            **Color interpretation:**
            The color scale you selected on the home page is applied to show changes:
            - **For diverging scales:** Center color = no change, extremes = large changes
            - **For sequential scales:** Darker = larger absolute change
            - **Color direction depends on indicator type:**
              - Inequality indicators: Negative change (decrease) = improvement
              - Positive indicators: Positive change (increase) = improvement
            
            **Hover information shows:**
            - Value in THEN period
            - Value in NOW period
            - Absolute change (NOW - THEN)
            - Percentage change
            
            **Summary metrics below map:**
            - **Biggest Increase:** Country with largest positive change
            - **Biggest Decrease:** Country with largest negative change
            - **Average Change:** Mean change across all countries
            - **Median Change:** Middle value (more robust to outliers)
            
            **Best for:**
            - Quickly identifying winners and losers
            - Seeing geographic patterns of improvement/decline
            - Identifying regional clusters of change
            - Presentations and reports (single clear visual)
            - Highlighting significant changes only
            """
        },
        "Sankey": {
            "title": "How to Read Sankey Diagram (Rank Flow)",
            "content": """
            **What you're seeing:**
            - **Left side:** Performance tiers in THEN period
            - **Right side:** Performance tiers in NOW period
            - **Flowing ribbons:** Show how many countries moved between tiers
            - Width of ribbon = number of countries making that transition
            
            **Tier definitions:**
            - **For small datasets (< 8 countries):** 3 tiers
              - Top Tier, Middle Tier, Bottom Tier
            - **For larger datasets (≥ 8 countries):** 4 quartiles
              - Top 25%, Upper Middle, Lower Middle, Bottom 25%
            
            **Flow color coding:**
            - **Green flows** = Countries improved (moved to better tier)
            - **Red flows** = Countries declined (moved to worse tier)
            - **Gray flows** = Countries stayed in same tier
            
            **Flow width meaning:**
            - Wider ribbon = more countries made that transition
            - Narrow ribbon = fewer countries
            - No flow = no countries made that transition
            
            **How to interpret:**
            - Lots of green flows = many countries improving tiers
            - Lots of red flows = many countries declining tiers
            - Thick gray flows = stable tier membership (low mobility)
            - Thin flows everywhere = high tier mobility
            
            **Expandable details:**
            - Click "Individual Country Movements" to see specifics
            - Shows each country's tier transitions
            - Includes rank changes and movement direction
            - Categorizes as: Improved, Worsened, or Stayed Same
            
            **Important notes:**
            - Tiers are **relative rankings**, not absolute thresholds
            - Even if all countries improved absolutely, some must still be in bottom tier
            - Movement shows relative performance changes
            
            **Best for:**
            - Visualizing mobility between performance groups
            - Understanding tier stability vs. movement
            - Seeing overall direction of change (upward/downward mobility)
            - Explaining changes to non-technical audiences
            - Group-level analysis rather than individual countries
            """
        },
        "Heatmap": {
            "title": "How to Read Heatmap Matrix",
            "content": """
            **What you're seeing:**
            - Three heatmaps stacked vertically
            - **Rows** = Countries (sorted alphabetically)
            - **Columns** = Selected indicators
            - **Colors** = Values (intensity shows magnitude)
            - **Numbers in cells** = Exact values (formatted to 2 decimals)
            
            **First heatmap (Side-by-side, left):**
            - Shows THEN period values
            - Uses your selected color scheme from home page
            - Color intensity indicates value magnitude
            - Consistent scale with NOW period for comparison
            
            **Second heatmap (Side-by-side, right):**
            - Shows NOW period values
            - Uses same color scheme as THEN period
            - Same scale range for direct comparison
            - Color intensity shows value magnitude
            
            **Third heatmap (Full width below):**
            - Shows **change** (NOW - THEN)
            - Uses diverging color scale
            - Numbers show change amount (can be positive or negative)
            
            **How to interpret:**
            - **Vertical patterns** (same column) = how countries compare on one indicator
            - **Horizontal patterns** (same row) = one country's profile across indicators
            - **Diagonal patterns** = potentially correlated indicators
            - **Color blocks** = country/indicator clusters
            
            **Using the change heatmap:**
            - For inequality indicators (lower is better):
              - Red cells = good (decreased inequality)
              - Blue cells = bad (increased inequality)
            - For positive indicators (higher is better):
              - Blue cells = good (increased)
              - Red cells = bad (decreased)
            
            **Interactive features:**
            - Hover over cells to see exact values
            - Column headers at top for easier reading
            - Rows maintain alphabetical order
            
            **Best for:**
            - Comprehensive multi-indicator, multi-country analysis
            - Spotting patterns and clusters across indicators
            - Identifying which indicators changed most
            - Finding countries with unusual profiles
            - Data exploration and hypothesis generation
            - Detailed analysis (not presentations - too much info)
            
            **Tips:**
            - Select 3-8 indicators for best readability
            - Look for color blocks (systematic patterns)
            - Compare first two heatmaps to third to validate changes
            - Use for detailed analysis sessions
            - Export data table for numerical analysis
            """
        }
    }
    
    help_info = viz_help.get(viz_type)
    if not help_info:
        return
    
    with st.expander(f"❓ {help_info['title']}", expanded=False):
        st.markdown(help_info['content'])

# --------------------------------------------------
# Detect theme
# --------------------------------------------------
theme_base = st.get_option("theme.base") or "light"
IS_DARK = theme_base.lower() == "dark"

# --------------------------------------------------
# Load & validate data
# --------------------------------------------------
try:
    df = handle_missing_data(load_inequality_data())
    geojson = load_geojson()
except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    st.stop()

ok, msg = validate_dataframe(
    df,
    ["country", "country_code", "year", "indicator", "value"]
)

if not ok:
    st.error(f"❌ Data validation error: {msg}")
    st.stop()

if geojson is None:
    st.error("❌ GeoJSON data could not be loaded.")
    st.stop()

# --------------------------------------------------
# Indicator configuration (FIXED: More comprehensive mapping)
# --------------------------------------------------
# Replace the INDICATOR_CONFIG section with this:

INDICATOR_CONFIG = {
    # Lower is better indicators - use flexible keyword matching
    "gini": {"lower_is_better": True, "improved_direction": "decreased"},
    "poverty": {"lower_is_better": True, "improved_direction": "decreased"},
    "unemployment": {"lower_is_better": True, "improved_direction": "decreased"},
    "infant": {"lower_is_better": True, "improved_direction": "decreased"},
    "mortality": {"lower_is_better": True, "improved_direction": "decreased"},
    "inequality": {"lower_is_better": True, "improved_direction": "decreased"},
    "crime": {"lower_is_better": True, "improved_direction": "decreased"},
    "inflation": {"lower_is_better": True, "improved_direction": "decreased"},
    "highest 10%": {"lower_is_better": True, "improved_direction": "decreased"},
    "highest 20%": {"lower_is_better": True, "improved_direction": "decreased"},
    
    # Higher is better indicators
    "gdp": {"lower_is_better": False, "improved_direction": "increased"},
    "income": {"lower_is_better": False, "improved_direction": "increased"},
    "education": {"lower_is_better": False, "improved_direction": "increased"},
    "literacy": {"lower_is_better": False, "improved_direction": "increased"},
    "life expectancy": {"lower_is_better": False, "improved_direction": "increased"},
    "health": {"lower_is_better": False, "improved_direction": "increased"},
    "growth": {"lower_is_better": False, "improved_direction": "increased"},
    "hdi": {"lower_is_better": False, "improved_direction": "increased"},
    "internet": {"lower_is_better": False, "improved_direction": "increased"},
    "labor force": {"lower_is_better": False, "improved_direction": "increased"},
    "population": {"lower_is_better": False, "improved_direction": "increased"},
    "completion rate": {"lower_is_better": False, "improved_direction": "increased"},
    "lowest 10%": {"lower_is_better": False, "improved_direction": "increased"},
    "lowest 20%": {"lower_is_better": False, "improved_direction": "increased"},
    "years of schooling": {"lower_is_better": False, "improved_direction": "increased"},
}

def get_indicator_config(indicator_name):
    """Get configuration for an indicator with smart detection"""
    indicator_lower = indicator_name.lower()
    
    # Check for keyword matches (order matters - check specific terms first)
    for key, config in INDICATOR_CONFIG.items():
        if key in indicator_lower:
            return config
    
    # Default to higher is better for unknown indicators
    return {"lower_is_better": False, "improved_direction": "increased"}

# --------------------------------------------------
# Get indicator from home page configuration
# --------------------------------------------------
if 'analysis_config' not in st.session_state or st.session_state.analysis_config is None:
    st.warning("⚠️ No configuration found. Please configure your analysis on the Home page first.")
    if st.button("Go to Home Page"):
        st.switch_page("home.py")
    st.stop()

# Use indicator from home page configuration
indicator = st.session_state.analysis_config.get('indicator')

if not indicator:
    st.error("❌ No indicator configured. Please select an indicator on the Home page.")
    if st.button("Go to Home Page"):
        st.switch_page("home.py")
    st.stop()

# Verify indicator exists in dataset
available_indicators = sorted(df["indicator"].unique())
if indicator not in available_indicators:
    st.error(f"❌ Configured indicator '{indicator}' not found in dataset.")
    st.info(f"Available indicators: {', '.join(available_indicators)}")
    if st.button("Go to Home Page to Reconfigure"):
        st.switch_page("home.py")
    st.stop()

# Get indicator configuration
indicator_config = get_indicator_config(indicator)
ascending = indicator_config["lower_is_better"]
improved_direction = indicator_config["improved_direction"]

# Filter data for selected indicator
idf = df[df["indicator"] == indicator].copy()

# Remove any rows with null values
idf = idf.dropna(subset=["value"])

if idf.empty:
    st.error(f"❌ No valid data available for {human_indicator(indicator)}")
    st.stop()

years = sorted(idf["year"].unique())

if len(years) < 2:
    st.warning(f"Not enough years for temporal comparison. Only {len(years)} year(s) available.")
    st.stop()

# Show data availability info
with st.expander("Data Availability"):
    st.write(f"**Years available:** {min(years)} - {max(years)}")
    st.write(f"**Total years:** {len(years)}")
    st.write(f"**Countries with data:** {idf['country'].nunique()}")
    st.write(f"**Total observations:** {len(idf)}")
    st.write(f"**Indicator type:** {'Lower is better' if ascending else 'Higher is better'}")

# --------------------------------------------------
# Color Mode Selector
# --------------------------------------------------
color_mode = st.radio(
    "Choose color scheme",
    [
        "Semantic (Default)",
        "Sequential",
        "Diverging",
        "Grayscale",
        "Vision-Accessible (Perceptually Uniform)"
    ],
    horizontal=True
)

if color_mode == "Semantic (Default)":
    color_scale = get_color_scale(indicator)
elif color_mode == "Sequential":
    color_scale = "Viridis" if not IS_DARK else "Plasma"
elif color_mode == "Diverging":
    color_scale = "RdBu" if not IS_DARK else "PuOr"
elif color_mode == "Grayscale":
    color_scale = "Greys"
else:
    color_scale = "Cividis"

# --------------------------------------------------
# Comparison Mode
# --------------------------------------------------
mode = st.radio(
    "Comparison Mode",
    ["Point-to-Point (Then vs Now)", "Range-to-Range (Averaged)"],
    horizontal=True
)

try:
    if mode.startswith("Point"):
        then_year, now_year = st.select_slider(
            "Select THEN and NOW years",
            options=years,
            value=(years[0], years[-1])
        )
        if then_year >= now_year:
            st.error("❌ THEN year must be earlier than NOW year.")
            st.stop()

        df_then = idf[idf["year"] == then_year].copy()
        df_now = idf[idf["year"] == now_year].copy()
        
        period_then = str(then_year)
        period_now = str(now_year)
    else:
        # Range to Range mode
        mid_point = len(years) // 2
        third_point = len(years) // 3
        
        early_range = st.select_slider(
            "Early Period",
            options=years,
            value=(years[0], years[third_point] if third_point > 0 else years[0])
        )
        late_range = st.select_slider(
            "Later Period",
            options=years,
            value=(years[mid_point] if mid_point < len(years) else years[-1], years[-1])
        )
        
        if early_range[1] >= late_range[0]:
            st.warning("⚠️ Early period should end before late period begins for clearer comparison.")
        
        df_then = idf[idf["year"].between(*early_range)].groupby(
            ["country", "country_code"], as_index=False
        )["value"].mean()
        df_now = idf[idf["year"].between(*late_range)].groupby(
            ["country", "country_code"], as_index=False
        )["value"].mean()
        
        period_then = f"{early_range[0]}–{early_range[1]}"
        period_now = f"{late_range[0]}–{late_range[1]}"
        
except Exception as e:
    st.error(f"❌ Error in period selection: {str(e)}")
    st.stop()

# --------------------------------------------------
# Keep common countries and validate
# --------------------------------------------------
common = set(df_then["country_code"]) & set(df_now["country_code"])

if len(common) == 0:
    st.error("❌ No overlapping countries between the two periods.")
    st.stop()

df_then = df_then[df_then["country_code"].isin(common)].copy()
df_now = df_now[df_now["country_code"].isin(common)].copy()

# Additional validation
df_then = df_then.dropna(subset=["value"])
df_now = df_now.dropna(subset=["value"])

if df_then.empty or df_now.empty:
    st.error("❌ No valid data available for comparison after filtering.")
    st.stop()
# --------------------------------------------------
# Ranking
# --------------------------------------------------
try:
    df_then["rank_then"] = df_then["value"].rank(ascending=ascending, method='min')
    df_now["rank_now"] = df_now["value"].rank(ascending=ascending, method='min')
except Exception as e:
    st.error(f"❌ Error calculating rankings: {str(e)}")
    st.stop()

# --------------------------------------------------
# Merge & compute changes (FIXED: Better null handling)
# --------------------------------------------------
try:
    cmp = df_then.merge(
        df_now, 
        on=["country", "country_code"], 
        suffixes=("_then", "_now"),
        how="inner"
    )
    
    if cmp.empty:
        st.error("❌ No data available after merging periods.")
        st.stop()
    
    # Calculate absolute change
    cmp["abs_change"] = cmp["value_now"] - cmp["value_then"]
    
    # Calculate percentage change with proper null handling
    cmp["pct_change"] = cmp.apply(
        lambda r: safe_divide(r["abs_change"], r["value_then"]) * 100 
        if pd.notna(r["value_then"]) and r["value_then"] != 0 
        else None,
        axis=1
    )
    
    # Calculate rank change
    cmp["rank_change"] = cmp["rank_then"] - cmp["rank_now"]
    
    # Determine improvement (FIXED: Based on indicator type)
    if ascending:  # Lower is better
        cmp["improved"] = cmp["abs_change"] < 0
    else:  # Higher is better
        cmp["improved"] = cmp["abs_change"] > 0
    
except Exception as e:
    st.error(f"❌ Error computing changes: {str(e)}")
    st.stop()

# --------------------------------------------------
# Statistical test (FIXED: Better error handling)
# --------------------------------------------------
try:
    if len(cmp) >= 3:  # Need at least 3 pairs for meaningful test
        t_stat, p_value = ttest_rel(cmp["value_then"], cmp["value_now"])
        test_valid = True
    else:
        t_stat, p_value = None, None
        test_valid = False
        st.warning("⚠️ Not enough data points for statistical test (need at least 3 countries)")
except Exception as e:
    st.warning(f"⚠️ Could not perform statistical test: {str(e)}")
    t_stat, p_value = None, None
    test_valid = False

# --------------------------------------------------
# Visualization selector
# --------------------------------------------------
viz_option = st.selectbox(
    "Select Visualization Tool",
    [
        "Choropleth Map", 
        "Bar Chart", 
        "Scatter Plot", 
        "Ranking Shift", 
        "Distribution Comparison",
        "Delta Map (Change Visualization)",         
        "Sankey Diagram (Rank Flow)", 
        "Heatmap Matrix"
    ]
)

# Calculate shared range for consistent color scaling
vmin = min(cmp["value_then"].min(), cmp["value_now"].min())
vmax = max(cmp["value_then"].max(), cmp["value_now"].max())

# Handle edge case where all values are the same
if vmin == vmax:
    vmin = vmin - 0.1
    vmax = vmax + 0.1

# --------------------------------------------------
# Side-by-side visualizations
# --------------------------------------------------
try:
# Calculate global min/max for consistent color scaling
    vmin = min(df_then["value"].min(), df_now["value"].min())
    vmax = max(df_then["value"].max(), df_now["value"].max())
    
    if viz_option == "Choropleth Map":
        c1, c2 = st.columns(2)
        
        with c1:
            fig_then = px.choropleth(
                df_then,
                geojson=geojson,
                locations="country_code",
                featureidkey="properties.ISO_A3",
                color="value",
                range_color=[vmin, vmax],
                color_continuous_scale=color_scale,
                title=f"{human_indicator(indicator)} — THEN ({period_then})",
                hover_data={"country": True, "value": ":.2f"}
            )
            
            # With only 8 countries, label all of them
            fig_then = add_country_labels_to_map(fig_then, df_then, geojson)
            fig_then = style_choropleth_map(fig_then)
            fig_then.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
            st.plotly_chart(fig_then, use_container_width=True)

        with c2:
            fig_now = px.choropleth(
                df_now,
                geojson=geojson,
                locations="country_code",
                featureidkey="properties.ISO_A3",
                color="value",
                range_color=[vmin, vmax],
                color_continuous_scale=color_scale,
                title=f"{human_indicator(indicator)} — NOW ({period_now})",
                hover_data={"country": True, "value": ":.2f"}
            )
            
            # With only 8 countries, label all of them
            fig_now = add_country_labels_to_map(fig_now, df_now, geojson)
            fig_now = style_choropleth_map(fig_now)
            fig_now.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
            st.plotly_chart(fig_now, use_container_width=True)

    elif viz_option == "Bar Chart":
        c1, c2 = st.columns(2)
        
        with c1:
            df_then_sorted = df_then.sort_values("value", ascending=False)
            fig_then = px.bar(
                df_then_sorted,
                x="value", 
                y="country", 
                color="value",
                color_continuous_scale=color_scale,
                range_color=[vmin, vmax],
                orientation='h',
                title=f"All Countries - THEN ({period_then})"
            )
            fig_then.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_then, use_container_width=True)
            
        with c2:
            df_now_sorted = df_now.sort_values("value", ascending=False)
            fig_now = px.bar(
                df_now_sorted,
                x="value", 
                y="country", 
                color="value",
                color_continuous_scale=color_scale,
                range_color=[vmin, vmax],
                orientation='h',
                title=f"All Countries - NOW ({period_now})"
            )
            fig_now.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_now, use_container_width=True)

    elif viz_option == "Scatter Plot": 
        # Calculate min/max for diagonal line
        vmin = min(cmp["value_then"].min(), cmp["value_now"].min())
        vmax = max(cmp["value_then"].max(), cmp["value_now"].max())
        
        fig_scatter = px.scatter(
            cmp, 
            x="value_then", 
            y="value_now", 
            hover_name="country",
            color="abs_change",
            color_continuous_scale=color_scale,
            title=f"Value Comparison: {period_then} vs {period_now}",
            labels={
                "value_then": f"Value in {period_then}",
                "value_now": f"Value in {period_now}",
                "abs_change": "Change (Now - Then)"
            },
            hover_data={
                "value_then": ":.2f",
                "value_now": ":.2f", 
                "abs_change": ":.2f"
            }
        )
        fig_scatter.add_shape(
            type="line", 
            x0=vmin, y0=vmin, 
            x1=vmax, y1=vmax,
            line=dict(color="red", dash="dash", width=2),
            name="No change"
        )
        # Increase marker size for better visibility
        fig_scatter.update_traces(marker=dict(size=12))
        st.plotly_chart(fig_scatter, use_container_width=True)

    elif viz_option == "Ranking Shift":
        # Calculate rank improvement (negative rank_change = improvement)
        cmp["rank_improvement"] = -cmp["rank_change"]
        
        # Calculate min/max for diagonal line
        rank_min = min(cmp["rank_then"].min(), cmp["rank_now"].min())
        rank_max = max(cmp["rank_then"].max(), cmp["rank_now"].max())
        
        fig_rank = px.scatter(
            cmp, 
            x="rank_then", 
            y="rank_now", 
            hover_name="country", 
            color="rank_improvement",
            color_continuous_scale=color_scale,
            title=f"Ranking Changes: {period_then} vs {period_now}",
            labels={
                "rank_then": f"Rank in {period_then}",
                "rank_now": f"Rank in {period_now}",
                "rank_improvement": "Rank Improvement"
            },
            hover_data={
                "rank_then": True,
                "rank_now": True,
                "rank_improvement": ":.0f",
                "rank_change": ":.0f"
            }
        )
        fig_rank.add_shape(
            type="line",
            x0=rank_min, y0=rank_min,
            x1=rank_max, y1=rank_max,
            line=dict(color="red", dash="dash", width=2)
        )
        fig_rank.update_traces(marker=dict(size=12))
        fig_rank.update_yaxes(autorange="reversed")
        fig_rank.update_xaxes(autorange="reversed")
        st.plotly_chart(fig_rank, use_container_width=True)
        
        # Add explanation
        st.caption("ℹ️ Positive rank improvement = moved to a better (lower) rank number. Points below the red line improved their ranking.")

    elif viz_option == "Distribution Comparison":
        dist_data = pd.DataFrame([
            {
                'Period': f'THEN ({period_then})',
                'Value': val,
                'Country': country
            }
            for country, val in zip(df_then['country'], df_then['value'])
        ] + [
            {
                'Period': f'NOW ({period_now})',
                'Value': val,
                'Country': country
            }
            for country, val in zip(df_now['country'], df_now['value'])
        ])
        
        # Create comparison plot
        fig_box = px.box(
            dist_data,
            x='Period',
            y='Value',
            color='Period',
            points='all',
            hover_data=['Country'],
            title=f"Distribution Comparison: {human_indicator(indicator)}",
            labels={'Value': human_indicator(indicator)},
            color_discrete_map={
                f'THEN ({period_then})': "#6104ae",
                f'NOW ({period_now})': "#dcaca6"
            }
        )
        fig_box.update_layout(
            showlegend=True, 
            height=600,
            hovermode='closest'
        )
        st.plotly_chart(fig_box, use_container_width=True)
        
        # Distribution statistics
        st.subheader("Distribution Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**THEN ({period_then})**")
            then_stats = df_then['value'].describe()
            stats_df_then = pd.DataFrame({
                'Metric': ['Mean', 'Median', 'Std Dev', 'Min', 'Max', 'Range'],
                'Value': [
                    f"{then_stats['mean']:.2f}",
                    f"{then_stats['50%']:.2f}",
                    f"{then_stats['std']:.2f}",
                    f"{then_stats['min']:.2f}",
                    f"{then_stats['max']:.2f}",
                    f"{then_stats['max'] - then_stats['min']:.2f}"
                ]
            })
            st.dataframe(stats_df_then, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown(f"**NOW ({period_now})**")
            now_stats = df_now['value'].describe()
            stats_df_now = pd.DataFrame({
                'Metric': ['Mean', 'Median', 'Std Dev', 'Min', 'Max', 'Range'],
                'Value': [
                    f"{now_stats['mean']:.2f}",
                    f"{now_stats['50%']:.2f}",
                    f"{now_stats['std']:.2f}",
                    f"{now_stats['min']:.2f}",
                    f"{now_stats['max']:.2f}",
                    f"{now_stats['max'] - now_stats['min']:.2f}"
                ]
            })
            st.dataframe(stats_df_now, use_container_width=True, hide_index=True)

    elif viz_option == "Delta Map (Change Visualization)":
        # Create a single map showing the CHANGE between periods
        delta_data = cmp.copy()
        
        # Calculate symmetric range for diverging color scales
        max_abs_change = delta_data['abs_change'].abs().max()
        
        # Determine if we should use symmetric or asymmetric range
        min_change = delta_data['abs_change'].min()
        max_change = delta_data['abs_change'].max()
        
        # Use symmetric range for diverging scales, asymmetric for sequential
        if color_mode in ["Diverging", "Semantic (Default)"]:
            color_range = [-max_abs_change, max_abs_change]
        else:
            color_range = [min_change, max_change]
        
        fig_delta = px.choropleth(
            delta_data,
            geojson=geojson,
            locations="country_code",
            featureidkey="properties.ISO_A3",
            color="abs_change",
            range_color=color_range,
            color_continuous_scale=color_scale,  # Use user-selected color scale
            title=f"Change in {human_indicator(indicator)}: {period_then} → {period_now}",
            hover_data={
                'country': True,
                'value_then': ':.2f',
                'value_now': ':.2f',
                'abs_change': ':.2f',
                'pct_change': ':.1f'
            },
            labels={
                'abs_change': 'Change',
                'value_then': f'Value ({period_then})',
                'value_now': f'Value ({period_now})',
                'pct_change': '% Change'
            }
        )
        
        # Add labels only for countries with significant changes (performance optimization)
        # Define "significant" as top/bottom 20% of changes
        threshold = delta_data['abs_change'].abs().quantile(0.80)
        significant_changes = delta_data[delta_data['abs_change'].abs() >= threshold]
        
        fig_delta = add_country_labels_to_map(fig_delta, significant_changes, geojson)
        fig_delta = style_choropleth_map(fig_delta)
            
        fig_delta.update_layout(
            margin={"r":0,"t":50,"l":0,"b":0},
            height=600
        )
        
        st.plotly_chart(fig_delta, use_container_width=True)
        
        # Summary metrics - CORRECTED LOGIC
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Filter for actual increases (positive changes)
            increases = delta_data[delta_data['abs_change'] > 0]
            if len(increases) > 0:
                biggest_increase = increases.loc[increases['abs_change'].idxmax()]
                st.metric(
                    "Biggest Increase",
                    biggest_increase['country'],
                    f"+{biggest_increase['abs_change']:.2f}"
                )
            else:
                st.metric("Biggest Increase", "N/A", "—")
        
        with col2:
            # Filter for actual decreases (negative changes)
            decreases = delta_data[delta_data['abs_change'] < 0]
            if len(decreases) > 0:
                biggest_decrease = decreases.loc[decreases['abs_change'].idxmin()]
                st.metric(
                    "Biggest Decrease",
                    biggest_decrease['country'],
                    f"{biggest_decrease['abs_change']:.2f}"
                )
            else:
                st.metric("Biggest Decrease", "N/A", "—")
        
        with col3:
            avg_change = delta_data['abs_change'].mean()
            st.metric(
                "Average Change",
                format_value(avg_change),
                f"{delta_data['pct_change'].mean():.1f}%"
            )
        
        with col4:
            # Add median change for robustness
            median_change = delta_data['abs_change'].median()
            st.metric(
                "Median Change",
                format_value(median_change),
                f"{delta_data['pct_change'].median():.1f}%"
            )

        
    elif viz_option == "Sankey Diagram (Rank Flow)":
        st.info("Shows how countries moved between performance tiers")
        num_countries = len(cmp)

        if num_countries < 8:
            num_tiers = 3
            labels_list = ['Top Tier', 'Middle Tier', 'Bottom Tier']
        else:
            num_tiers = 4
            labels_list = ['Top 25%', 'Upper Middle', 'Lower Middle', 'Bottom 25%']
    

        try:
            cmp['tier_then'] = pd.qcut(
                cmp['rank_then'], 
                q=num_tiers, 
                labels=labels_list,
                duplicates='drop'
            )
            cmp['tier_now'] = pd.qcut(
                cmp['rank_now'], 
                q=num_tiers, 
                labels=labels_list,
                duplicates='drop'
            )
        except ValueError:
            # Fallback to manual binning if qcut fails
            st.warning("⚠️ Using manual tier assignment due to data distribution")
            max_rank = max(cmp['rank_then'].max(), cmp['rank_now'].max())
            bins = [0] + [max_rank * (i+1) / num_tiers for i in range(num_tiers)]
        
            cmp['tier_then'] = pd.cut(
                cmp['rank_then'],
                bins=bins,
                labels=labels_list,
                include_lowest=True
            )
            cmp['tier_now'] = pd.cut(
                cmp['rank_now'],
                bins=bins,
                labels=labels_list,
                include_lowest=True
            )
    
    # Build Sankey data
        import plotly.graph_objects as go
    
        sankey_data = cmp.groupby(['tier_then', 'tier_now']).size().reset_index(name='count')
    
        # Create node labels
        source_labels = [f"{tier} (THEN)" for tier in labels_list]
        target_labels = [f"{tier} (NOW)" for tier in labels_list]
        all_labels = source_labels + target_labels
        label_to_idx = {label: idx for idx, label in enumerate(all_labels)}
    
        sources = []
        targets = []
        values = []
        colors = []
    
        for _, row in sankey_data.iterrows():
            source_label = f"{row['tier_then']} (THEN)"
            target_label = f"{row['tier_now']} (NOW)"
        
            if source_label in label_to_idx and target_label in label_to_idx:
                sources.append(label_to_idx[source_label])
                targets.append(label_to_idx[target_label])
                values.append(row['count'])
            
                # FIXED: Color based on movement (lower index = better tier)
                src_idx = label_to_idx[source_label] % len(labels_list)
                tgt_idx = (label_to_idx[target_label] - len(labels_list)) % len(labels_list)
            
                if src_idx == tgt_idx:
                    colors.append('rgba(150, 150, 150, 0.3)')  # Gray - no change
                elif tgt_idx > src_idx:
                    colors.append('rgba(231, 76, 60, 0.5)')  # Red - WORSENED (moved to worse tier)
                else:
                    colors.append('rgba(46, 204, 113, 0.5)')  # Green - IMPROVED (moved to better tier)
    
        # Node colors
        node_colors = ["#240b47"] * len(labels_list) + ["#e089c9"] * len(labels_list)

        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=20,
                thickness=25,
                line=dict(color="white", width=2),
                label=all_labels,
                color=node_colors
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=colors
            )
        )])
    
        fig_sankey.update_layout(
            title=f"Performance Tier Transitions: {period_then} → {period_now}",
            height=500,
            font=dict(size=14)
        )
    
        st.plotly_chart(fig_sankey, use_container_width=True)
    
        # FIXED: Country movement details
        with st.expander("Individual Country Movements"):
            movement_df = cmp[['country', 'tier_then', 'tier_now', 'rank_change']].copy()
        
            # Corrected movement logic
            def determine_movement(row):
                if row['tier_then'] == row['tier_now']:
                    return '➡️ Stayed in Same Tier'
                elif row['rank_change'] > 0:
                    return '⬆️ Improved (Better Rank)'
                else:
                    return '⬇️ Worsened (Worse Rank)'
        
            movement_df['Movement'] = movement_df.apply(determine_movement, axis=1)
            st.dataframe(movement_df, use_container_width=True, hide_index=True)

    elif viz_option == "Heatmap Matrix":
        st.markdown("#### Indicators")

        # Get only indicators that actually exist in the dataset
        available_categories = get_available_indicators_by_category(df)

        # Category selector
        category_names = list(available_categories.keys())
        selected_category = st.selectbox(
            "Indicator category",
            category_names,
            help="Choose the indicator group"
        )

        # Indicators inside chosen category
        category_indicators = available_categories[selected_category]['indicators']

        # Multi-select indicators (heatmap needs multiple)
        selected_indicators = st.multiselect(
            "Select indicators",
            options=category_indicators,
            default=category_indicators[:min(5, len(category_indicators))],
            format_func=human_indicator
        )
    
        heatmap_data_then = []
        heatmap_data_now = []

        for country_code in common:
            country_name = cmp[cmp['country_code'] == country_code]['country'].iloc[0]
    
            row_then = {'Country': country_name}
            row_now = {'Country': country_name}
        
            for ind in selected_indicators:
                indicator_df = df[
                    (df['indicator'] == ind) & 
                    (df['country_code'] == country_code)
                ]
        
                if mode.startswith("Point"):
                    then_val = indicator_df[indicator_df['year'] == then_year]['value']
                    now_val = indicator_df[indicator_df['year'] == now_year]['value']
            
                    row_then[human_indicator(ind)] = then_val.iloc[0] if len(then_val) > 0 else np.nan
                    row_now[human_indicator(ind)] = now_val.iloc[0] if len(now_val) > 0 else np.nan
                else:
                    then_val = indicator_df[indicator_df['year'].between(*early_range)]['value'].mean()
                    now_val = indicator_df[indicator_df['year'].between(*late_range)]['value'].mean()
            
                    row_then[human_indicator(ind)] = then_val if pd.notna(then_val) else np.nan
                    row_now[human_indicator(ind)] = now_val if pd.notna(now_val) else np.nan
    
            heatmap_data_then.append(row_then)
            heatmap_data_now.append(row_now)

        df_heatmap_then = pd.DataFrame(heatmap_data_then).set_index('Country')
        df_heatmap_now = pd.DataFrame(heatmap_data_now).set_index('Country')

        # Ensure both dataframes have identical structure
        df_heatmap_then = df_heatmap_then.sort_index().sort_index(axis=1)
        df_heatmap_now = df_heatmap_now.sort_index().sort_index(axis=1)

        # Calculate global min/max for consistent color scaling
        global_min = min(df_heatmap_then.min().min(), df_heatmap_now.min().min())
        global_max = max(df_heatmap_then.max().max(), df_heatmap_now.max().max())

        # Side-by-side heatmaps
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"### THEN ({period_then})")
            fig_heat_then = px.imshow(
                df_heatmap_then,
                labels=dict(x="Indicator", y="Country", color="Value"),
                aspect="auto",
                color_continuous_scale=color_scale,  # Use user's color choice
                zmin=global_min,
                zmax=global_max,
                text_auto='.2f'
            )
            fig_heat_then.update_layout(height=max(350, len(df_heatmap_then) * 50))
            fig_heat_then.update_xaxes(side="top")
            st.plotly_chart(fig_heat_then, use_container_width=True)

        with col2:
            st.markdown(f"### NOW ({period_now})")
            fig_heat_now = px.imshow(
                df_heatmap_now,
                labels=dict(x="Indicator", y="Country", color="Value"),
                aspect="auto",
                color_continuous_scale=color_scale,  # Use user's color choice
                zmin=global_min,
                zmax=global_max,
                text_auto='.2f'
            )
            fig_heat_now.update_layout(height=max(350, len(df_heatmap_now) * 50))
            fig_heat_now.update_xaxes(side="top")
            st.plotly_chart(fig_heat_now, use_container_width=True)

        st.markdown("---")
        st.markdown("### Change Heatmap (NOW - THEN)")
   
        # Calculate difference with proper alignment
        df_heatmap_diff = df_heatmap_now - df_heatmap_then

        # Get max absolute change for symmetric color scale
        max_diff = df_heatmap_diff.abs().max().max()
        if pd.isna(max_diff) or max_diff == 0:
            st.warning("⚠️ No changes detected between periods")
            max_diff = 1  # Prevent division by zero

        # Use diverging color scale for difference (always makes sense for +/- changes)
        if color_mode == "Diverging" or color_mode == "Semantic (Default)":
            diff_color_scale = color_scale
        else:
            # Force diverging for difference visualization
            diff_color_scale = "RdBu_r"  # Red=negative, Blue=positive
    
        fig_heat_diff = px.imshow(
            df_heatmap_diff,
            labels=dict(x="Indicator", y="Country", color="Change"),
            aspect="auto",
            color_continuous_scale=diff_color_scale,
            color_continuous_midpoint=0,
            zmin=-max_diff,
            zmax=max_diff,
            text_auto='.2f'
        )
        fig_heat_diff.update_layout(height=max(350, len(df_heatmap_diff) * 50))
        fig_heat_diff.update_xaxes(side="top")
        st.plotly_chart(fig_heat_diff, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error creating visualization: {str(e)}")
    st.write("Debug info:", str(e))

# Map visualization options to help keys
viz_help_mapping = {
    "Choropleth Map": "Map",
    "Bar Chart": "Bar Chart",
    "Scatter Plot": "Scatter Plot",
    "Ranking Shift": "Ranking Shift",
    "Distribution Comparison": "Distribution",
    "Delta Map (Change Visualization)": "Delta Map",
    "Sankey Diagram (Rank Flow)": "Sankey",
    "Radar Chart (Performance Profile)": "Radar Chart",
    "Heatmap Matrix": "Heatmap",
    "Country Table": "Data Table"
}

# Show help for the selected visualization
if viz_option in viz_help_mapping:
    render_visualization_help(viz_help_mapping[viz_option])
# --------------------------------------------------
# Insights (FIXED: Better logic and null handling)
# --------------------------------------------------
st.subheader("Summary")

try:
    # Determine if lower is better for this indicator
    # Add your logic here based on indicator type
    lower_is_better_indicators = ['unemployment_rate', 'inflation_rate', 'poverty_rate', 'crime_rate']
    ascending = indicator in lower_is_better_indicators
    
    # Calculate metrics safely
    mean_change = cmp["abs_change"].mean()
    median_change = cmp["abs_change"].median()
    num_improved = cmp["improved"].sum()
    num_worsened = (~cmp["improved"]).sum()
    
    # Determine overall trend
    if ascending:  # Lower is better
        trend = "improved" if mean_change < 0 else "worsened"
    else:  # Higher is better
        trend = "improved" if mean_change > 0 else "worsened"
    
    # Statistical significance
    if test_valid:
        sig = "statistically significant" if p_value < 0.05 else "not statistically significant"
        confidence = "95%" if p_value < 0.05 else "less than 95%"
    else:
        sig = "unable to determine"
        confidence = "N/A"
    
    # Find biggest changes - CORRECTED LOGIC
    if ascending:  # Lower is better
        # Biggest improver = most negative change
        biggest_improver_idx = cmp["abs_change"].idxmin()
        # Biggest decliner = most positive change
        biggest_decliner_idx = cmp["abs_change"].idxmax()
    else:  # Higher is better
        # Biggest improver = most positive change
        biggest_improver_idx = cmp["abs_change"].idxmax()
        # Biggest decliner = most negative change
        biggest_decliner_idx = cmp["abs_change"].idxmin()
    
    biggest_improver = cmp.loc[biggest_improver_idx]
    biggest_decliner = cmp.loc[biggest_decliner_idx]
    
    # Create summary columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Overall Trend", 
            trend.title(),
            f"{format_value(mean_change)} avg change"
        )
    
    with col2:
        st.metric(
            "Countries Improved",
            f"{num_improved}/{len(cmp)}",
            f"{(num_improved/len(cmp)*100):.1f}%"
        )
    
    with col3:
        if test_valid:
            st.metric(
                "Statistical Significance",
                "Yes ✓" if p_value < 0.05 else "No ✗",
                f"p = {p_value:.4f}"
            )
        else:
            st.metric(
                "Statistical Test",
                "N/A",
                "Insufficient data"
            )
    
    # Detailed summary
    st.markdown(f"""
    ### Detailed Analysis
    
    **Period Comparison:** {period_then} → {period_now}
    
    **Overall Performance:**
    - On average, **{human_indicator(indicator)}** has **{trend}** across the region
    - Mean change: **{format_value(mean_change)}**
    - Median change: **{format_value(median_change)}**
    - {num_improved} countries improved, {num_worsened} countries worsened
    
    **Statistical Confidence:**
    {f"- Paired t-test: **p = {p_value:.4f}** (t = {t_stat:.2f})" if test_valid else "- Statistical test could not be performed"}
    {f"- The change is **{sig}** at {confidence} confidence level" if test_valid else ""}
    
    **Notable Changes:**
    - 🏆 **Best Performer:** {biggest_improver['country']} 
      - Change: {format_value(biggest_improver['abs_change'])} ({biggest_improver['pct_change']:.1f}% change)
    - ⚠️ **Biggest Decline:** {biggest_decliner['country']}
      - Change: {format_value(biggest_decliner['abs_change'])} ({biggest_decliner['pct_change']:.1f}% change)
    """)
    
except Exception as e:
    st.error(f"❌ Error generating summary: {str(e)}")

# --------------------------------------------------
# Export Section (Enhanced with multiple options)
# --------------------------------------------------
st.markdown("---")
st.subheader("📥 Export Data")

try:
    st.markdown("### Download Comparison Data")
    
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
                "Comparison Results (All Metrics)",
                "THEN Period Data Only",
                "NOW Period Data Only",
                "Change Data Only (Delta)",
                "Full Dataset (All Indicators)"
            ]
        )
    
    # Prepare different datasets based on selection
    if data_selection == "Comparison Results (All Metrics)":
        export_df = cmp[[
            "country", "country_code",
            "value_then", "value_now", 
            "abs_change", "pct_change",
            "rank_then", "rank_now", "rank_change",
            "improved"
        ]].rename(columns={
            "value_then": f"Value_{period_then}",
            "value_now": f"Value_{period_now}",
            "abs_change": "Absolute_Change",
            "pct_change": "Percentage_Change",
            "rank_then": f"Rank_{period_then}",
            "rank_now": f"Rank_{period_now}",
            "rank_change": "Rank_Change",
            "improved": "Improved"
        })
        filename_base = f"Comparison_{indicator}_{period_then}_vs_{period_now}"
        
    elif data_selection == "THEN Period Data Only":
        export_df = df_then[["country", "country_code", "value"]].rename(columns={
            "value": f"Value_{period_then}"
        })
        filename_base = f"Data_{indicator}_{period_then}"
        
    elif data_selection == "NOW Period Data Only":
        export_df = df_now[["country", "country_code", "value"]].rename(columns={
            "value": f"Value_{period_now}"
        })
        filename_base = f"Data_{indicator}_{period_now}"
        
    elif data_selection == "Change Data Only (Delta)":
        export_df = cmp[["country", "country_code", "abs_change", "pct_change"]].rename(columns={
            "abs_change": "Absolute_Change",
            "pct_change": "Percentage_Change"
        })
        filename_base = f"Changes_{indicator}_{period_then}_to_{period_now}"
        
    else:  # Full Dataset
        export_df = df[df['indicator'] == indicator].copy()
        filename_base = f"Full_Data_{indicator}"
    
    # Add metadata
    metadata = {
        "Indicator": indicator,
        "Period_THEN": period_then,
        "Period_NOW": period_now,
        "Countries": len(common),
        "Export_Date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Display preview
    with st.expander("Preview data", expanded=False):
        st.dataframe(export_df.head(10), use_container_width=True)
        st.caption(f"Showing first 10 of {len(export_df)} rows")
    
    # Export based on format
    if export_format == "CSV":
        # Add metadata as comment lines
        metadata_lines = "\n".join([f"# {k}: {v}" for k, v in metadata.items()])
        csv_data = metadata_lines + "\n" + export_df.to_csv(index=False)
        
        st.download_button(
            label=f"⬇️ Download as CSV",
            data=csv_data,
            file_name=f"{filename_base}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    elif export_format == "Excel (XLSX)":
        try:
            from io import BytesIO
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                export_df.to_excel(writer, sheet_name='Data', index=False)
                
                # Add metadata sheet
                metadata_df = pd.DataFrame([metadata])
                metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
                
                # Add summary statistics if comparison data
                if data_selection == "Comparison Results (All Metrics)":
                    summary_df = pd.DataFrame({
                        'Metric': ['Mean Change', 'Median Change', 'Std Dev', 'Countries Improved', 'Countries Worsened'],
                        'Value': [
                            cmp['abs_change'].mean(),
                            cmp['abs_change'].median(),
                            cmp['abs_change'].std(),
                            cmp['improved'].sum(),
                            (~cmp['improved']).sum()
                        ]
                    })
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            output.seek(0)
            st.download_button(
                label=f"⬇️ Download as Excel",
                data=output,
                file_name=f"{filename_base}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except ImportError:
            st.error("❌ Excel export requires 'openpyxl'. Install it with: pip install openpyxl")
        
    elif export_format == "JSON":
        # Include metadata in JSON
        json_output = {
            "metadata": metadata,
            "data": export_df.to_dict(orient='records')
        }
        json_data = json.dumps(json_output, indent=2)
        
        st.download_button(
            label=f"⬇️ Download as JSON",
            data=json_data,
            file_name=f"{filename_base}.json",
            mime="application/json",
            use_container_width=True
        )
        
    else:  # TSV
        # Add metadata as comment lines
        metadata_lines = "\n".join([f"# {k}: {v}" for k, v in metadata.items()])
        tsv_data = metadata_lines + "\n" + export_df.to_csv(index=False, sep='\t')
        
        st.download_button(
            label=f"⬇️ Download as TSV",
            data=tsv_data,
            file_name=f"{filename_base}.tsv",
            mime="text/tab-separated-values",
            use_container_width=True
        )
    
    # Visualization export instructions
    if 'fig' not in locals():
        st.warning("⚠️ No visualization available to export")
        st.stop()

    st.markdown("---")
    st.markdown("### Export Visualizations")

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

    size_map = {
        "Standard (1200x800)": (1200, 800),
        "Large (1920x1080)": (1920, 1080),
        "Extra Large (2560x1440)": (2560, 1440),
        "Print Quality (3840x2160)": (3840, 2160)
        }

    width, height = size_map.get(viz_size, (1200, 800))
    viz_filename = f"Comparison_{indicator}_{period_then}_vs_{period_now}".replace(" ", "_")

    if viz_format == "HTML (Interactive)":
        html_bytes = fig.to_html(include_plotlyjs="cdn").encode("utf-8")
        st.download_button(
            "Download HTML",
            data=html_bytes,
            file_name=f"{viz_filename}.html",
            mime="text/html",
            use_container_width=True
        )
    else:
        fmt_map = {
            "PNG (High Quality)": "png",
            "SVG (Vector)": "svg",
            "PDF": "pdf",
            "JPEG": "jpeg"
        }
        fmt = fmt_map[viz_format]
        try:
            img_bytes = fig.to_image(format=fmt, width=width, height=height)
            st.download_button(
                f"Download {viz_format}",
                data=img_bytes,
            file_name=f"{viz_filename}.{fmt}",
            use_container_width=True
            )
        except Exception:
            st.error("❌ Image export unavailable. Install Kaleido: pip install kaleido")


except Exception as e:
    st.error(f"❌ Error in export section: {str(e)}")
    st.caption("Please try a different export format or contact support if the issue persists.")