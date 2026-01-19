
import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.stats import ttest_rel
import sys
from pathlib import Path
import numpy as np

# --------------------------------------------------
# Path setup
# --------------------------------------------------
sys.path.append(str(Path(__file__).parent.parent))
from utils.loaders import load_inequality_data, load_geojson
from utils.utils import (
    human_indicator,
    get_color_scale,
    handle_missing_data,
    validate_dataframe,
    format_value,
    safe_divide
)
from utils.help_system import render_help_button
from utils.sidebar import apply_all_styles

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

def render_visualization_help(viz_type: str):
    """
    Render specific help for visualization types in temporal comparison
    """
    
    viz_help = {
        "Map": {
            "title": "How to Read Side-by-Side Maps",
            "content": """
            **What you're seeing:**
            - **Left map (THEN):** Shows the earlier time period's values
            - **Right map (NOW):** Shows the later time period's values
            - **Color intensity:** Darker = higher values (meaning varies by indicator)
            
            **How to interpret:**
            - Compare the same country across both maps to see if it got darker or lighter
            - Darker to lighter = improvement (for inequality indicators)
            - Lighter to darker = worsening situation
            - Hover over countries to see exact values and changes
            
            **Best for:**
            - Understanding geographic shifts in patterns
            - Seeing which regions improved vs. declined
            - Visual storytelling about temporal change
            """
        },
        "Bar Chart": {
            "title": "How to Read the Comparison Bar Chart",
            "content": """
            **What you're seeing:**
            - Each country has two bars side-by-side
            - **First bar (darker):** THEN period value
            - **Second bar (lighter):** NOW period value
            
            **How to interpret:**
            - If NOW bar is shorter than THEN bar = improvement (values decreased)
            - If NOW bar is taller than THEN bar = worsening (values increased)
            - Hover to see exact values and percentage change
            
            **Best for:**
            - Quickly comparing magnitudes across countries
            - Identifying which countries changed the most
            - Spotting outliers or exceptional cases
            """
        },
        "Scatter Plot": {
            "title": "How to Read the Scatter Plot",
            "content": """
            **What you're seeing:**
            - X-axis = THEN period values
            - Y-axis = NOW period values
            - **Diagonal line** = line of no change
            - Each point represents one country
            
            **How to interpret:**
            - Points **below the diagonal** = improved (decreased inequality)
            - Points **above the diagonal** = worsened (increased inequality)
            - Points **on the diagonal** = no change
            - Distance from line = magnitude of change
            
            **Best for:**
            - Seeing correlation between past and present
            - Identifying countries that bucked regional trends
            - Understanding if high-inequality countries improved more/less
            """
        },
        "Ranking Shift": {
            "title": "How to Read Ranking Changes",
            "content": """
            **What you're seeing:**
            - Each country's rank position in THEN vs NOW
            - Lines connect the same country across time periods
            - **Green lines** = moved up in rankings (improved relative position)
            - **Red lines** = moved down in rankings (worsened relative position)
            
            **How to interpret:**
            - Upward slopes (left-to-right) = worsening rank
            - Downward slopes = improving rank
            - Steep lines = major rank shifts
            - Flat/horizontal = maintained position
            
            **Important note:**
            - Rankings are **relative**, not absolute
            - A country can worsen in absolute terms but improve in rank if others worsened more
            
            **Best for:**
            - Understanding competitive positioning
            - Tracking relative progress among peers
            - Identifying regional leaders vs. laggards
            """
        },
        "Distribution": {
            "title": "How to Read Distribution Comparison",
            "content": """
            **What you're seeing:**
            - Box plots showing data distribution for THEN and NOW periods
            - **Box** = middle 50/%/ of values (interquartile range)
            - **Line in box** = median value
            - **Whiskers** = extend to min/max within 1.5× IQR
            - **Dots** = individual country data points
            
            **How to interpret:**
            - Wider box = more inequality/variance among countries
            - Box shift up/down = overall regional trend
            - Dots outside whiskers = outlier countries
            - Hover over dots to see which country
            
            **Statistics table shows:**
            - **Mean:** Average value across all countries
            - **Median:** Middle value (50th percentile)
            - **Std Dev:** How spread out the values are
            - **Min/Max:** Extreme values
            - **Range:** Difference between max and min
            
            **Key insights:**
            - If NOW box is narrower = countries converging (less dispersion)
            - If NOW box is wider = countries diverging (more dispersion)
            - Compare medians to see if typical country improved
            
            **Best for:**
            - Understanding regional inequality trends
            - Seeing if countries are converging or diverging
            - Identifying outliers and extreme cases
            """
        },
        "Delta Map": {
            "title": "How to Read Delta (Change) Map",
            "content": """
            **What you're seeing:**
            - Single map showing **change** between periods (NOW - THEN)
            - Uses Eurostat-style diverging color scale
            
            **Color guide:**
            - 🟣 **Dark Purple (#160216)** = Large negative change (large decrease)  
            - 🟣 **Medium Purple (#5A3C5A)** = Moderate negative change  
            - ⚪ **Off-White (#FAFAFB)** = Little or no change / neutral  
            - 🔵 **Light Blue (#1C91C8)** = Moderate positive change  
            - 🔵 **Dark Blue (#1F4F82)** = Large positive change (large increase)
            
            **How to interpret:**
            - For inequality indicators (lower is better):
              - **Blue = worsened** (inequality increased)
              - **Red = improved** (inequality decreased)
            - For positive indicators (higher is better):
              - **Blue = improved**
              - **Red = worsened**
            
            **Hover information shows:**
            - THEN value
            - NOW value
            - Absolute change
            - Percentage change
            
            **Summary metrics below map:**
            - **Biggest Increase:** Country with largest positive change
            - **Biggest Decrease:** Country with largest negative change
            - **Average Change:** Mean change across all countries
            
            **Best for:**
            - Quickly identifying winners and losers
            - Geographic patterns of improvement/decline
            - Seeing regional clusters of change
            - Presentations and reports (single clear visual)
            """
        },
        "Sankey": {
            "title": "How to Read Sankey Diagram (Rank Flow)",
            "content": """
            **What you're seeing:**
            - **Left side (Blue):** Performance tiers in THEN period
            - **Right side (Red):** Performance tiers in NOW period
            - **Flows (ribbons):** Show how many countries moved between tiers
            
            **Tier definitions:**
            - For small datasets (≤6 countries): 3 tiers (Top, Middle, Bottom)
            - For larger datasets: 4 quartiles (Top 25%, Upper Middle, Lower Middle, Bottom 25%)
            
            **Color coding:**
            - **Green flows** = Countries improved (moved to better tier)
            - **Red flows** = Countries declined (moved to worse tier)
            - **Gray flows** = Countries stayed in same tier
            
            **Flow width:**
            - Wider ribbon = more countries made that transition
            - Narrow ribbon = fewer countries
            
            **How to interpret:**
            - Lots of green = many countries improving
            - Lots of red = many countries declining
            - Thick gray flows = stable tier membership
            
            **Expandable details:**
            - Click "Individual Country Movements" to see which specific countries moved
            - Shows tier transitions and rank changes for each country
            
            **Best for:**
            - Visualizing mobility between performance groups
            - Understanding tier stability vs. movement
            - Seeing overall direction of change (upward/downward mobility)
            - Presentations (easy to explain to non-technical audiences)
            
            **Note:**
            - Tiers are **relative rankings**, not absolute thresholds
            - Even if all countries improved, some must still be in bottom tier
            """
        },
        "Radar Chart": {
            "title": "How to Read Radar Chart (Performance Profile)",
            "content": """
            **What you're seeing:**
            - **Left chart:** THEN period performance profiles
            - **Right chart:** NOW period performance profiles
            - Each axis = one indicator (3-8 indicators recommended)
            - Colored polygons = individual countries
            
            **How to interpret:**
            - **Larger polygon area** = better overall performance
            - **Polygon shape** = performance pattern across indicators
            - Distance from center = value magnitude
            - **Outer edge** = higher values, **center** = lower values
            
            **Comparing THEN vs NOW:**
            - Same color represents same country in both periods
            - Expanded polygon (THEN→NOW) = overall improvement
            - Contracted polygon = overall decline
            - Shape changes = shifts in performance pattern
            
            **Pattern recognition:**
            - **Circular/balanced polygon** = consistent performance across indicators
            - **Star-shaped** = uneven performance (strong in some, weak in others)
            - **Similar shapes** = countries with similar development patterns
            
            **Best for:**
            - Multi-dimensional country comparisons
            - Seeing holistic performance (not just one metric)
            - Identifying countries with balanced vs. unbalanced development
            - Understanding which indicators drive overall change
            
            **Tips:**
            - Select 1-4 countries for clarity (more gets messy)
            - Choose 3-8 indicators (too few = less informative, too many = cluttered)
            - Look for countries that shift from star to circle (becoming more balanced)
            - Compare polygon areas visually for quick overall assessment
            
            **Limitation:**
            - Different indicators may have different scales, making direct comparison tricky
            - Useful for patterns, less for precise values
            """
        },
        "Heatmap": {
            "title": "How to Read Heatmap Matrix",
            "content": """
            **What you're seeing:**
            - Three heatmaps stacked vertically
            - **Rows** = Countries
            - **Columns** = Indicators
            - **Colors** = Values (darker = higher)
            
            **First heatmap (Blue):**
            - Shows THEN period values
            - Darker blue = higher value
            - Lighter blue = lower value
            - Numbers show exact values
            
            **Second heatmap (Red):**
            - Shows NOW period values
            - Darker red = higher value
            - Lighter red = lower value
            - Numbers show exact values
            
            **Third heatmap (Red-Blue diverging):**
            - Shows **change** (NOW - THEN)
            - 🔵 **Blue** = Value increased
            - ⚪ **White** = No change
            - 🔴 **Red** = Value decreased
            - Numbers show change amount
            
            **How to interpret:**
            - **Vertical patterns** (same column) = how countries compare on one indicator
            - **Horizontal patterns** (same row) = one country's profile across indicators
            - **Diagonal patterns** = correlated indicators
            
            **Using the change heatmap:**
            - For inequality (lower is better):
              - Red cells = good (decreased)
              - Blue cells = bad (increased)
            - For positive indicators (higher is better):
              - Blue cells = good (increased)
              - Red cells = bad (decreased)
            
            **Best for:**
            - Comprehensive multi-indicator, multi-country analysis
            - Spotting patterns and clusters
            - Identifying which indicators changed most
            - Finding countries with unusual profiles
            - Data exploration and hypothesis generation
            
            **Tips:**
            - Click column headers to sort
            - Look for blocks of color (country/indicator clusters)
            - Compare first two heatmaps to third to validate changes
            - Use for detailed analysis, not presentations (too much info)
            
            **Interactive features:**
            - Hover over cells to see exact values
            - Axis labels show at top for easier reading
            """
        },
        "Data Table": {
            "title": "How to Read the Data Table",
            "content": """
            **Column explanations:**
            - **Country:** Country name with flag emoji
            - **Value (THEN):** Indicator value in earlier period
            - **Value (NOW):** Indicator value in later period
            - **Absolute Change:** NOW - THEN (negative = improvement for inequality)
            - **Percentage Change:** ((NOW - THEN) / THEN) × 100
            - **Rank Change:** Change in regional ranking position
            - **Trend:** Visual indicator of direction
            
            **Trend icons:**
            - 📈 = Improved (value increased) - for positive indicators
            - 📉 = Improved (value decreased) - for inequality indicators
            - ⚠️ = Worsened (value increased) - for inequality indicators
            - ⚠️ = Worsened (value decreased) - for positive indicators
            - ➡️ = No significant change
            
            **How to use:**
            - **Click column headers** to sort (find top/bottom performers)
            - **Absolute change** = real-world impact magnitude
            - **Percentage change** = normalized comparison (accounts for different starting points)
            - **Rank change** = relative position shift
            
            **Interpreting changes:**
            - Large absolute change + small /%/ change = started from high baseline
            - Small absolute change + large %/ change = started from low baseline
            - Positive rank change = improved relative to peers
            - Negative rank change = fell behind peers
            
            **Best for:**
            - Precise numerical analysis
            - Finding specific country statistics
            - Sorting and filtering data
            - Exporting for external analysis (Excel, etc.)
            - Creating custom reports
            - Fact-checking and verification
            
            **Tips:**
            - Sort by "Rank Change" to see who moved up/down most
            - Sort by "Percentage Change" to normalize for starting values
            - Use absolute change for real-world impact assessment
            - Export table and use Excel pivot tables for deeper analysis
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
# Indicator selection
# --------------------------------------------------
available_indicators = sorted(df["indicator"].unique())

if len(available_indicators) == 0:
    st.error("❌ No indicators found in the dataset.")
    st.stop()

indicator = st.selectbox(
    "Select Indicator",
    available_indicators,
    format_func=human_indicator
)

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

st.info(f"Comparing {len(common)} countries across selected periods")

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
        "Radar Chart (Performance Profile)",
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
            # For fig_then:
            for idx, row in df_then.iterrows():
                iso = row['country_code']
                country_feature = next((f for f in geojson['features'] if f['properties']['ISO_A3'] == iso), None)
                if country_feature:
                    coords = country_feature['geometry']['coordinates']
                    if country_feature['geometry']['type'] == 'Polygon':
                        lons = [c[0] for c in coords[0]]
                        lats = [c[1] for c in coords[0]]
                    elif country_feature['geometry']['type'] == 'MultiPolygon':
                        lons = [c[0] for c in coords[0][0]]
                        lats = [c[1] for c in coords[0][0]]
        
                    center_lon = sum(lons) / len(lons)
                    center_lat = sum(lats) / len(lats)
        
                    fig_then.add_scattergeo(
                        lon=[center_lon],
                        lat=[center_lat],
                        text=row['country'],
                        mode='text',
                        textfont=dict(size=10, color='black', family='Arial'),
                        showlegend=False,
                        hoverinfo='skip'
                    )
            fig_then.update_geos(
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
            for idx, row in df_now.iterrows():
                iso = row['country_code']
                country_feature = next((f for f in geojson['features'] if f['properties']['ISO_A3'] == iso), None)
                if country_feature:
                    coords = country_feature['geometry']['coordinates']
                    if country_feature['geometry']['type'] == 'Polygon':
                        lons = [c[0] for c in coords[0]]
                        lats = [c[1] for c in coords[0]]
                    elif country_feature['geometry']['type'] == 'MultiPolygon':
                        lons = [c[0] for c in coords[0][0]]
                        lats = [c[1] for c in coords[0][0]]
        
                    center_lon = sum(lons) / len(lons)
                    center_lat = sum(lats) / len(lats)
        
                    fig_now.add_scattergeo(
                        lon=[center_lon],
                        lat=[center_lat],
                        text=row['country'],
                        mode='text',
                        textfont=dict(size=10, color='black', family='Arial'),
                        showlegend=False,
                        hoverinfo='skip'
                    )
            fig_now.update_geos(
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
            
            fig_now.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
            st.plotly_chart(fig_now, use_container_width=True)

    elif viz_option == "Bar Chart":
        c1, c2 = st.columns(2)
        
        with c1:
            df_then_sorted = df_then.sort_values("value", ascending=ascending).head(20)
            fig_then = px.bar(
                df_then_sorted,
                x="value", 
                y="country", 
                color="value",
                color_continuous_scale=color_scale,
                orientation='h',
                title=f"Top Countries - THEN ({period_then})"
            )
            fig_then.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_then, use_container_width=True)
            
        with c2:
            df_now_sorted = df_now.sort_values("value", ascending=ascending).head(8)
            fig_now = px.bar(
                df_now_sorted,
                x="value", 
                y="country", 
                color="value",
                color_continuous_scale=color_scale,
                orientation='h',
                title=f"Top 20 Countries - NOW ({period_now})"
            )
            fig_now.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_now, use_container_width=True)

    elif viz_option == "Scatter Plot":
        fig_scatter = px.scatter(
            cmp, 
            x="value_then", 
            y="value_now", 
            text="country", 
            color="abs_change",
            color_continuous_scale=color_scale,
            title=f"Value Comparison: {period_then} vs {period_now}",
            labels={
                "value_then": f"Value in {period_then}",
                "value_now": f"Value in {period_now}",
                "abs_change": "Absolute Change"
            }
        )
        fig_scatter.add_shape(
            type="line", 
            x0=vmin, y0=vmin, 
            x1=vmax, y1=vmax,
            line=dict(color="red", dash="dash", width=2),
            name="No change"
        )
        fig_scatter.update_traces(textposition='top center')
        st.plotly_chart(fig_scatter, use_container_width=True)

    elif viz_option == "Ranking Shift":
        fig_rank = px.scatter(
            cmp, 
            x="rank_then", 
            y="rank_now", 
            text="country", 
            color="rank_change",
            color_continuous_scale=color_scale,
            title=f"Ranking Changes: {period_then} vs {period_now}",
            labels={
                "rank_then": f"Rank in {period_then}",
                "rank_now": f"Rank in {period_now}",
                "rank_change": "Rank Change"
            }
        )
        rank_min = min(cmp["rank_then"].min(), cmp["rank_now"].min())
        rank_max = max(cmp["rank_then"].max(), cmp["rank_now"].max())
        fig_rank.add_shape(
            type="line",
            x0=rank_min, y0=rank_min,
            x1=rank_max, y1=rank_max,
            line=dict(color="black", dash="dash", width=2)
        )
        fig_rank.update_traces(textposition='top center')
        fig_rank.update_yaxes(autorange="reversed")
        fig_rank.update_xaxes(autorange="reversed")
        st.plotly_chart(fig_rank, use_container_width=True)

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
        fig_box.update_layout(showlegend=True, height=500)
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
        
        # Use Eurostat-style diverging colors
        # Blue = positive change, Orange/Red = negative change
        max_abs_change = delta_data['abs_change'].abs().max()
        
        fig_delta = px.choropleth(
            delta_data,
            geojson=geojson,
            locations="country_code",
            featureidkey="properties.ISO_A3",
            color="abs_change",
            range_color=[-max_abs_change, max_abs_change],
            color_continuous_scale=[
                [0.0, "#160216"],    # Dark red (large negative)
                [0.25, "#5A3C5A"],   # Light red
                [0.5, "#FAFAFB"],    # Yellow (neutral)
                [0.75, "#1C91C8"],   # Light blue
                [1.0, "#1F4F82"]     # Dark blue (large positive)
            ],
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
        for idx, row in delta_data.iterrows():
                iso = row['country_code']
                country_feature = next((f for f in geojson['features'] if f['properties']['ISO_A3'] == iso), None)
                if country_feature:
                    coords = country_feature['geometry']['coordinates']
                    if country_feature['geometry']['type'] == 'Polygon':
                        lons = [c[0] for c in coords[0]]
                        lats = [c[1] for c in coords[0]]
                    elif country_feature['geometry']['type'] == 'MultiPolygon':
                        lons = [c[0] for c in coords[0][0]]
                        lats = [c[1] for c in coords[0][0]]
        
                    center_lon = sum(lons) / len(lons)
                    center_lat = sum(lats) / len(lats)
        
                    fig_delta.add_scattergeo(
                        lon=[center_lon],
                        lat=[center_lat],
                        text=row['country'],
                        mode='text',
                        textfont=dict(size=10, color='black', family='Arial'),
                        showlegend=False,
                        hoverinfo='skip'
                    )
        
        fig_delta.update_geos(
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
            
        fig_delta.update_layout(
            margin={"r":0,"t":50,"l":0,"b":0},
            height=600
        )
        
        st.plotly_chart(fig_delta, use_container_width=True)
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            biggest_increase = delta_data.loc[delta_data['abs_change'].idxmax()]
            st.metric(
                "Biggest Increase",
                biggest_increase['country'],
                f"+{biggest_increase['abs_change']:.2f}"
            )
        with col2:
            biggest_decrease = delta_data.loc[delta_data['abs_change'].idxmin()]
            st.metric(
                "Biggest Decrease",
                biggest_decrease['country'],
                f"{biggest_decrease['abs_change']:.2f}"
            )
        with col3:
            st.metric(
                "Average Change",
                format_value(delta_data['abs_change'].mean()),
                f"{delta_data['pct_change'].mean():.1f}%"
            )

        
    elif viz_option == "Sankey Diagram (Rank Flow)":
        st.info("Shows how countries moved between performance tiers")
        
        # For 8 countries, use tertiles instead of quartiles
        num_countries = len(cmp)
        
        if num_countries <= 6:
            # Use 3 groups for small datasets
            labels_list = ['Top Tier', 'Middle Tier', 'Bottom Tier']
            cmp['tier_then'] = pd.qcut(
                cmp['rank_then'], 
                q=3, 
                labels=labels_list,
                duplicates='drop'
            )
            cmp['tier_now'] = pd.qcut(
                cmp['rank_now'], 
                q=3, 
                labels=labels_list,
                duplicates='drop'
            )
        else:
            # Use quartiles for larger datasets
            labels_list = ['Top 25%', 'Upper Middle', 'Lower Middle', 'Bottom 25%']
            cmp['tier_then'] = pd.qcut(
                cmp['rank_then'], 
                q=4, 
                labels=labels_list,
                duplicates='drop'
            )
            cmp['tier_now'] = pd.qcut(
                cmp['rank_now'], 
                q=4, 
                labels=labels_list,
                duplicates='drop'
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
                
                # Color based on movement
                src_idx = label_to_idx[source_label] % len(labels_list)
                tgt_idx = (label_to_idx[target_label] - len(labels_list)) % len(labels_list)
                
                if src_idx == tgt_idx:
                    colors.append('rgba(150, 150, 150, 0.3)')  # Gray
                elif tgt_idx < src_idx:
                    colors.append('rgba(46, 204, 113, 0.5)')  # Green
                else:
                    colors.append('rgba(231, 76, 60, 0.5)')  # Red
        
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
        
        # Country movement details
        with st.expander("Individual Country Movements"):
            movement_df = cmp[['country', 'tier_then', 'tier_now', 'rank_change']].copy()
            movement_df['Movement'] = movement_df.apply(
                lambda row: '⬆️ Moved Up' if row['tier_then'] != row['tier_now'] and row['rank_change'] > 0
                else ('⬇️ Moved Down' if row['tier_then'] != row['tier_now'] and row['rank_change'] < 0
                else '➡️ Stayed in Tier'),
                axis=1
            )
            st.dataframe(movement_df, use_container_width=True, hide_index=True)
    

    elif viz_option == "Radar Chart (Performance Profile)":
        st.info("Compare country performance profiles across indicators")
        available_indicators = df['indicator'].unique()
    
        selected_indicators = st.multiselect(
            "Select 3-8 indicators",
            available_indicators,
            default=list(available_indicators[:min(5, len(available_indicators))]),
            format_func=human_indicator
        )
        
        if len(selected_indicators) < 3:
            st.warning("⚠️ Select at least 3 indicators")
            st.stop()
        country_options = sorted(cmp['country'].unique())
        selected_countries = st.multiselect(
            "Select countries (1-4 recommended)",
            country_options,
            default=list(country_options[:min(3, len(country_options))])
        )
        
        if len(selected_countries) == 0:
            st.warning("⚠️ Select at least one country")
            st.stop()
        
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        from sklearn.preprocessing import MinMaxScaler

        all_data_then = []
        all_data_now = []
        
        for country in selected_countries:
            for indicator_name in selected_indicators:
                indicator_df = df[
                    (df['indicator'] == indicator_name) & 
                    (df['country'] == country)
                ]
            
                if mode.startswith("Point"):
                    then_val = indicator_df[indicator_df['year'] == then_year]['value']
                    now_val = indicator_df[indicator_df['year'] == now_year]['value']
                
                    then_v = then_val.iloc[0] if len(then_val) > 0 else np.nan
                    now_v = now_val.iloc[0] if len(now_val) > 0 else np.nan
                else:
                    then_v = indicator_df[indicator_df['year'].between(*early_range)]['value'].mean()
                    now_v = indicator_df[indicator_df['year'].between(*late_range)]['value'].mean()
            
                all_data_then.append({'indicator': indicator_name, 'country': country, 'value': then_v})
                all_data_now.append({'indicator': indicator_name, 'country': country, 'value': now_v})


        df_all_then = pd.DataFrame(all_data_then)
        df_all_now = pd.DataFrame(all_data_now) 
        # Normalize each indicator to 0-100 scale
        normalized_then = {}
        normalized_now = {}
    
        for indicator_name in selected_indicators:
            # Get all values for this indicator across all countries
            then_vals = df_all_then[df_all_then['indicator'] == indicator_name]['value'].values
            now_vals = df_all_now[df_all_now['indicator'] == indicator_name]['value'].values
        
            # Combine to get min/max range
            all_vals = np.concatenate([then_vals, now_vals])
            all_vals = all_vals[~np.isnan(all_vals)]
        
            if len(all_vals) > 0:
                val_min = all_vals.min()
                val_max = all_vals.max()
                val_range = val_max - val_min
                if val_range > 0:
                    for country in selected_countries:
                        then_val = df_all_then[
                            (df_all_then['indicator'] == indicator_name) & 
                            (df_all_then['country'] == country)
                        ]['value'].iloc[0]
                    
                        if pd.notna(then_val):
                            normalized_then[(country, indicator_name)] = ((then_val - val_min) / val_range) * 100
                        else:
                            normalized_then[(country, indicator_name)] = 0
                    
                    # NOW
                        now_val = df_all_now[
                            (df_all_now['indicator'] == indicator_name) & 
                            (df_all_now['country'] == country)
                        ]['value'].iloc[0]
                    
                        if pd.notna(now_val):
                            normalized_now[(country, indicator_name)] = ((now_val - val_min) / val_range) * 100
                        else:
                            normalized_now[(country, indicator_name)] = 0

                else:
                    for country in selected_countries:
                        normalized_then[(country, indicator_name)] = 50
                        normalized_now[(country, indicator_name)] = 50
            
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=(f'THEN ({period_then})', f'NOW ({period_now})'),
            specs=[[{'type': 'polar'}, {'type': 'polar'}]]
        )
        

        
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
        indicator_labels = [human_indicator(ind) for ind in selected_indicators]
        for country_idx, country in enumerate(selected_countries):
            values_then = [normalized_then.get((country, ind), 0) for ind in selected_indicators]
            values_now = [normalized_now.get((country, ind), 0) for ind in selected_indicators]
            color = colors[country_idx % len(colors)]
            # THEN
            fig.add_trace(go.Scatterpolar(
                r=values_then,
                theta=indicator_labels,
                fill='toself',
                name=country,
                line=dict(color=color, width=2),
                fillcolor=color,
                opacity=0.3
            ), row=1, col=1)
        
        # NOW
            fig.add_trace(go.Scatterpolar(
                r=values_now,
                theta=indicator_labels,
                fill='toself',
                name=country,
                line=dict(color=color, width=2),
                fillcolor=color,
                opacity=0.3,
                showlegend=False
            ), row=1, col=2)           
        fig.update_layout(
            height=600,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
            polar=dict(radialaxis=dict(range=[0, 100], showticklabels=True)),
            polar2=dict(radialaxis=dict(range=[0, 100], showticklabels=True))
        )
        st.plotly_chart(fig, use_container_width=True)

    elif viz_option == "Heatmap Matrix":
        st.info("Multi-indicator heatmap comparison")
        available_indicators = df['indicator'].unique()
        selected_indicators = st.multiselect(
            "Select indicators",
            available_indicators,
            default=list(available_indicators[:min(5, len(available_indicators))]),
            format_func=human_indicator
        )
    
        if len(selected_indicators) == 0:
            st.warning("⚠️ Select at least one indicator")
            st.stop()

        heatmap_data_then = []
        heatmap_data_now = []
    
        for country_code in common:
            country_name = cmp[cmp['country_code'] == country_code]['country'].iloc[0]
        
            row_then = {'Country': country_name}
            row_now = {'Country': country_name}
            for indicator_name in selected_indicators:
                indicator_df = df[
                    (df['indicator'] == indicator_name) & 
                    (df['country_code'] == country_code)
                ]
            
                if mode.startswith("Point"):
                    then_val = indicator_df[indicator_df['year'] == then_year]['value']
                    now_val = indicator_df[indicator_df['year'] == now_year]['value']
                
                    row_then[human_indicator(indicator_name)] = then_val.iloc[0] if len(then_val) > 0 else np.nan
                    row_now[human_indicator(indicator_name)] = now_val.iloc[0] if len(now_val) > 0 else np.nan
                else:
                    then_val = indicator_df[indicator_df['year'].between(*early_range)]['value'].mean()
                    now_val = indicator_df[indicator_df['year'].between(*late_range)]['value'].mean()
                
                    row_then[human_indicator(indicator_name)] = then_val if pd.notna(then_val) else np.nan
                    row_now[human_indicator(indicator_name)] = now_val if pd.notna(now_val) else np.nan
        
            heatmap_data_then.append(row_then)
            heatmap_data_now.append(row_now)
    
        df_heatmap_then = pd.DataFrame(heatmap_data_then).set_index('Country')
        df_heatmap_now = pd.DataFrame(heatmap_data_now).set_index('Country')
    
    # CRITICAL FIX: Ensure both dataframes have identical structure
        df_heatmap_then = df_heatmap_then.sort_index().sort_index(axis=1)
        df_heatmap_now = df_heatmap_now.sort_index().sort_index(axis=1)
    
    # Side-by-side heatmaps
        col1, col2 = st.columns(2)
    
        with col1:
            st.markdown(f"### THEN ({period_then})")
            fig_heat_then = px.imshow(
                df_heatmap_then,
                labels=dict(x="Indicator", y="Country", color="Value"),
                aspect="auto",
                color_continuous_scale=["#5A3C5A", "#CF9ECF", "#FAFAFB"],
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
                color_continuous_scale=["#1F4F82", "#8CC6E1", "#FAFAFB"],
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
    
        fig_heat_diff = px.imshow(
            df_heatmap_diff,
            labels=dict(x="Indicator", y="Country", color="Change"),
            aspect="auto",
            color_continuous_scale= ["#160216", "#5A3C5A", "#FAFAFB", "#89CFF0", "#2B6CB0"],
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
    
    # Find biggest changes
    biggest_improver_idx = cmp["abs_change"].idxmax() if not ascending else cmp["abs_change"].idxmin()
    biggest_decliner_idx = cmp["abs_change"].idxmin() if not ascending else cmp["abs_change"].idxmax()
    
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
    - **Best Performer:** {biggest_improver['country']} 
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
st.subheader("📥 Export Data & Visualizations")

try:
    # Create tabs for different export types
    export_tab1, export_tab2 = st.tabs(["Data Export", "Visualization Export"])
    
    with export_tab1:
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
        
        # Add metadata row
        metadata = {
            "Indicator": indicator,
            "Period_THEN": period_then,
            "Period_NOW": period_now,
            "Countries": len(common),
            "Export_Date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Display preview
        with st.expander("📋 Preview data", expanded=False):
            st.dataframe(export_df.head(10), use_container_width=True)
            st.caption(f"Showing first 10 of {len(export_df)} rows")
        
        # Export based on format
        if export_format == "CSV":
            csv_data = export_df.to_csv(index=False)
            st.download_button(
                label=f"⬇️ Download as CSV",
                data=csv_data,
                file_name=f"{filename_base}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        elif export_format == "Excel (XLSX)":
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
            
        elif export_format == "JSON":
            json_data = export_df.to_json(orient='records', indent=2)
            st.download_button(
                label=f"⬇️ Download as JSON",
                data=json_data,
                file_name=f"{filename_base}.json",
                mime="application/json",
                use_container_width=True
            )
            
        else:  # TSV
            tsv_data = export_df.to_csv(index=False, sep='\t')
            st.download_button(
                label=f"⬇️ Download as TSV",
                data=tsv_data,
                file_name=f"{filename_base}.tsv",
                mime="text/tab-separated-values",
                use_container_width=True
            )
    
    with export_tab2:
        st.markdown("### Download Current Visualization")
        
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
        
        st.info(f"💡 Current visualization: **{viz_option}**")
        
        # Note about format compatibility
        if viz_format in ["PNG (High Quality)", "JPEG"]:
            st.caption("📸 Static image - good for presentations and documents")
        elif viz_format == "SVG (Vector)":
            st.caption("Vector format - scalable without quality loss, ideal for publications")
        elif viz_format == "PDF":
            st.caption("PDF format - ideal for reports and printing")
        else:
            st.caption("Interactive HTML - preserves hover effects and interactivity")
        
        # Generate filename
        viz_filename = f"{viz_option.replace(' ', '_')}_{indicator}_{period_then}_vs_{period_now}"
        
        # Download button with instructions
        st.markdown("""
        **To download visualization:**
        1. The current visualization shown above will be exported
        2. Click the download button below
        3. The file will be saved in your selected format
        """)
        
        # Format-specific download logic
        if viz_format == "HTML (Interactive)":
            st.info("ℹ️ For HTML export: Right-click on the visualization above → 'Save as' or use the Plotly camera icon → 'Download plot as HTML'")
            st.caption("HTML files preserve all interactive features like hover, zoom, and pan")
            
        elif viz_format == "SVG (Vector)":
            st.info("ℹ️ For SVG export: Click the camera icon 📷 in the top-right of the visualization → Select 'Download plot as a svg'")
            st.caption("SVG files can be edited in vector graphics software like Adobe Illustrator or Inkscape")
            
        elif viz_format == "PDF":
            st.info("ℹ️ For PDF export: Click the camera icon 📷 in the top-right of the visualization → Select 'Download plot as a pdf'")
            st.caption("PDF files are ideal for reports and can be printed at any size")
            
        else:  # PNG or JPEG
            st.info(f"ℹ️ For {viz_format} export: Click the camera icon 📷 in the top-right of the visualization → Select 'Download plot as a png'")
            st.caption(f"Resolution: {width}x{height} pixels")
        
        # Additional export options
        st.markdown("---")
        st.markdown("### Bulk Export Options")
        
        if st.checkbox("Export all visualizations for this comparison"):
            st.warning("⚠️ This will generate multiple files. Make sure you have enough storage space.")
            
            bulk_formats = st.multiselect(
                "Select formats for bulk export",
                ["PNG", "CSV Data", "Excel Summary"],
                default=["PNG", "CSV Data"]
            )
            
            if st.button("Generate Bulk Export Package", use_container_width=True):
                st.info("Bulk export would generate files for all visualization types. For now, please export visualizations individually using the camera icon on each chart.")
                st.caption("Tip: You can switch between visualization types using the dropdown above and export each one.")

except Exception as e:
    st.error(f"❌ Error in export section: {str(e)}")
    st.caption("Please try a different export format or contact support if the issue persists.")