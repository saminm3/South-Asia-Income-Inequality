
import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.stats import ttest_rel
import sys
from pathlib import Path

# --------------------------------------------------
# Path setup
# --------------------------------------------------
sys.path.append(str(Path(__file__).parent.parent))
from utils.loaders import load_all_indicators
from utils.utils import human_indicator, format_value
from utils.exports import export_data_menu, export_plot_menu

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Temporal Comparison",
    page_icon="🕰️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🕰️ Temporal Comparison")
st.caption("Temporal, spatial, and statistical comparison of inequality indicators")

# --------------------------------------------------
# Detect theme
# --------------------------------------------------
theme_base = st.get_option("theme.base") or "light"
IS_DARK = theme_base.lower() == "dark"

# --------------------------------------------------
# Load & validate data
# --------------------------------------------------
df = handle_missing_data(load_inequality_data())
geojson = load_geojson()

ok, msg = validate_dataframe(
    df,
    ["country", "country_code", "year", "indicator", "value"]
)

if not ok or geojson is None:
    st.error("❌ Data loading error.")
    st.stop()

# --------------------------------------------------
# Indicator selection
# --------------------------------------------------
indicator = st.selectbox(
    "Select Indicator",
    sorted(df["indicator"].unique()),
    format_func=human_indicator
)

idf = df[df["indicator"] == indicator].copy()
years = sorted(idf["year"].unique())

if len(years) < 2:
    st.warning("Not enough years for temporal comparison.")
    st.stop()

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
else:
    early_range = st.select_slider(
        "Early Period",
        options=years,
        value=(years[0], years[len(years)//3])
    )
    late_range = st.select_slider(
        "Later Period",
        options=years,
        value=(years[len(years)//2], years[-1])
    )
    df_then = idf[idf["year"].between(*early_range)].groupby(
        ["country", "country_code"], as_index=False
    )["value"].mean()
    df_now = idf[idf["year"].between(*late_range)].groupby(
        ["country", "country_code"], as_index=False
    )["value"].mean()
    then_year = f"{early_range[0]}–{early_range[1]}"
    now_year = f"{late_range[0]}–{late_range[1]}"

# --------------------------------------------------
# Keep common countries
# --------------------------------------------------
common = set(df_then["country_code"]) & set(df_now["country_code"])
df_then = df_then[df_then["country_code"].isin(common)].copy()
df_now = df_now[df_now["country_code"].isin(common)].copy()

if df_then.empty or df_now.empty:
    st.warning("No overlapping countries available.")
    st.stop()

# --------------------------------------------------
# Ranking
# --------------------------------------------------
LOWER_IS_BETTER = ["gini", "poverty", "unemployment"]
ascending = any(x in indicator.lower() for x in LOWER_IS_BETTER)
df_then["rank_then"] = df_then["value"].rank(ascending=ascending)
df_now["rank_now"] = df_now["value"].rank(ascending=ascending)

# --------------------------------------------------
# Merge & compute changes
# --------------------------------------------------
cmp = df_then.merge(df_now, on=["country", "country_code"], suffixes=("_then", "_now"))
cmp["abs_change"] = cmp["value_now"] - cmp["value_then"]
cmp["pct_change"] = cmp.apply(
    lambda r: safe_divide(r["abs_change"], r["value_then"]) * 100 if r["value_then"] != 0 else None,
    axis=1
)
cmp["rank_change"] = cmp["rank_then"] - cmp["rank_now"]

# Statistical test
t_stat, p_value = ttest_rel(cmp["value_then"], cmp["value_now"])

# --------------------------------------------------
# Visualization selector
# --------------------------------------------------
viz_option = st.selectbox(
    "Select Visualization Tool",
    ["Choropleth Map", "Bar Chart", "Scatter Plot", "Ranking Shift", "Country Table"]
)

vmin = min(cmp["value_then"].min(), cmp["value_now"].min())
vmax = max(cmp["value_then"].max(), cmp["value_now"].max())

# --------------------------------------------------
# Side-by-side visualizations
# --------------------------------------------------
c1, c2 = st.columns(2)

if viz_option == "Choropleth Map":
    with c1:
        fig_then = px.choropleth(
            df_then,
            geojson=geojson,
            locations="country_code",
            featureidkey="properties.ISO_A3",
            color="value",
            range_color=[vmin, vmax],
            color_continuous_scale=color_scale,
            title=f"{human_indicator(indicator)} — THEN ({then_year})"
        )
        fig_then.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig_then, use_container_width=True, config={'displayModeBar': False})
        export_plot_menu(fig_then, f"temporal_{indicator}_then_{then_year}", key="temp_map_then")

    with c2:
        fig_now = px.choropleth(
            df_now,
            geojson=geojson,
            locations="country_code",
            featureidkey="properties.ISO_A3",
            color="value",
            range_color=[vmin, vmax],
            color_continuous_scale=color_scale,
            title=f"{human_indicator(indicator)} — NOW ({now_year})"
        )
        fig_now.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig_now, use_container_width=True, config={'displayModeBar': False})
        export_plot_menu(fig_now, f"temporal_{indicator}_now_{now_year}", key="temp_map_now")

elif viz_option == "Bar Chart":
    with c1:
        fig_then = px.bar(df_then.sort_values("value", ascending=ascending),
                          x="country", y="value", color="value",
                          color_continuous_scale=color_scale)
        st.plotly_chart(fig_then, use_container_width=True, config={'displayModeBar': False})
        export_plot_menu(fig_then, f"temporal_bar_{indicator}_then_{then_year}", key="temp_bar_then")
    with c2:
        fig_now = px.bar(df_now.sort_values("value", ascending=ascending),
                         x="country", y="value", color="value",
                         color_continuous_scale=color_scale)
        st.plotly_chart(fig_now, use_container_width=True, config={'displayModeBar': False})
        export_plot_menu(fig_now, f"temporal_bar_{indicator}_now_{now_year}", key="temp_bar_now")

elif viz_option == "Scatter Plot":
    fig_scatter = px.scatter(
        cmp, x="value_then", y="value_now", text="country", color="abs_change",
        color_continuous_scale=color_scale, range_color=[vmin, vmax]
    )
    fig_scatter.add_shape(
        type="line", x0=vmin, y0=vmin, x1=vmax, y1=vmax,
        line=dict(color="red", dash="dash")
    )
    st.plotly_chart(fig_scatter, use_container_width=True, config={'displayModeBar': False})
    export_plot_menu(fig_scatter, "temporal_scatter", key="temp_scatter")

elif viz_option == "Ranking Shift":
    fig_rank = px.scatter(
        cmp, x="rank_then", y="rank_now", text="country", color="abs_change",
        color_continuous_scale=color_scale
    )
    fig_rank.add_shape(
        type="line",
        x0=cmp["rank_then"].min(), y0=cmp["rank_then"].min(),
        x1=cmp["rank_then"].max(), y1=cmp["rank_then"].max(),
        line=dict(color="black", dash="dash")
    )
    st.plotly_chart(fig_rank, use_container_width=True, config={'displayModeBar': False})
    export_plot_menu(fig_rank, "ranking_shift", key="rank_shift")

elif viz_option == "Country Table":
    tbl = cmp.copy()
    tbl["value_then"] = tbl["value_then"].apply(format_value)
    tbl["value_now"] = tbl["value_now"].apply(format_value)
    tbl["abs_change"] = tbl["abs_change"].apply(format_value)
    tbl["pct_change"] = tbl["pct_change"].apply(lambda x: f"{x:.1f}%" if x is not None else "—")
    def change_icon(x):
        if x > 0: return "📈"
        elif x < 0: return "📉"
        else: return "➡️"
    tbl["trend"] = cmp["abs_change"].apply(change_icon)
    st.dataframe(
        tbl[["country", "value_then", "value_now", "abs_change", "pct_change", "rank_change", "trend"]],
        use_container_width=True
    )

# --------------------------------------------------
# Insights
# --------------------------------------------------
st.subheader("Summary")
trend = "improved" if cmp["abs_change"].mean() < 0 else "deteriorated"
sig = "statistically significant" if p_value < 0.05 else "not statistically significant"

biggest_increase = cmp.loc[cmp["abs_change"].idxmax()]
biggest_decrease = cmp.loc[cmp["abs_change"].idxmin()]

st.markdown(f"""
**Overall Trend:**
Between **{then_year}** and **{now_year}**,
**{human_indicator(indicator)}** has **{trend}** across South Asia.

**Statistical Test:**
Paired t-test: **p = {p_value:.4f}**, indicating the change is **{sig}**.

**Biggest Improver:** {biggest_increase['country']} ({format_value(biggest_increase['abs_change'])})
**Biggest Decliner:** {biggest_decrease['country']} ({format_value(biggest_decrease['abs_change'])})
""")

# --------------------------------------------------
# Export
# --------------------------------------------------
export_data_menu(cmp, "temporal_comparison_results", key="temp_comp_data")
