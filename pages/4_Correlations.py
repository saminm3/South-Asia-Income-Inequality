import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from scipy.stats import pearsonr
import sys
from pathlib import Path

# ----------------------------
# Add utils to path
# ----------------------------
sys.path.append(str(Path(__file__).parent.parent))
from utils.loaders import load_all_indicators
from utils.utils import human_indicator
from utils.help_system import render_help_button
from utils.sidebar import apply_all_styles
from utils.indicator_metadata import get_available_indicators_by_category, INDICATOR_CATEGORIES

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Inequality Drivers (Correlation)",
    page_icon="🔗",
    layout="wide"
)
render_help_button("correlations")
apply_all_styles()

# ----------------------------
# Load custom CSS
# ----------------------------
try:
    with open("assets/dashboard.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Professional text styling + correlation page-only styling
st.markdown("""
<style>
.story-text {
    font-size: 0.95rem;
    line-height: 1.6;
    color: #e5e7eb;
}
.story-text strong { color: #ffffff; }
.story-text .muted {
    color: #9ca3af;
    font-size: 0.85rem;
}

/* Correlation page alert box */
.correlation-alert {
    border-radius: 18px;
    border: 1px solid rgba(139, 92, 246, 0.6);
    background: linear-gradient(
        90deg,
        rgba(88, 28, 135, 0.45),
        rgba(30, 41, 59, 0.40)
    );
    padding: 18px 20px;
    margin-bottom: 20px;
    color: #e5e7eb;
    font-size: 0.95rem;
}

/* Key statistics metric cards */
div[data-testid="stMetric"] {
    border-radius: 16px;
    border: 1px solid rgba(139, 92, 246, 0.35);
    background: linear-gradient(
        180deg,
        rgba(88, 28, 135, 0.28),
        rgba(17, 24, 39, 0.28)
    );
    padding: 14px 14px;
}

div[data-testid="stMetricLabel"] {
    color: #cbd5e1 !important;
    font-size: 0.90rem;
}

div[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 700;
}

div[data-testid="stMetricDelta"] {
    color: #a78bfa !important;
}

/* Dataframe styling (correlation page only) */
div[data-testid="stDataFrame"] {
    border-radius: 16px;
    border: 1px solid rgba(139, 92, 246, 0.35);
    background: linear-gradient(
        180deg,
        rgba(88, 28, 135, 0.18),
        rgba(17, 24, 39, 0.25)
    );
    padding: 10px;
}

/* ---- Styled expander (excluded years) ---- */
div[data-testid="stExpander"] {
    border-radius: 16px;
    border: 1px solid rgba(139, 92, 246, 0.45);
    background: linear-gradient(
        180deg,
        rgba(88, 28, 135, 0.22),
        rgba(17, 24, 39, 0.30)
    );
    margin-top: 10px;
}
div[data-testid="stExpander"] summary {
    font-weight: 600;
    color: #e5e7eb;
    padding: 12px 16px;
}
div[data-testid="stExpander"] summary svg {
    color: #a78bfa !important;
}
div[data-testid="stExpander"] div[role="region"] {
    padding: 10px 18px 16px 18px;
    color: #e5e7eb;
}
div[data-testid="stExpander"] strong { color: #ffffff; }

/* Table header */
div[data-testid="stDataFrame"] thead tr th {
    background-color: rgba(88, 28, 135, 0.55) !important;
    color: #ffffff !important;
    font-weight: 600;
    border-bottom: 1px solid rgba(139, 92, 246, 0.4) !important;
}

/* Table body cells */
div[data-testid="stDataFrame"] tbody tr td {
    background-color: rgba(17, 24, 39, 0.35) !important;
    color: #e5e7eb !important;
    border-bottom: 1px solid rgba(139, 92, 246, 0.15) !important;
}

/* Hover effect */
div[data-testid="stDataFrame"] tbody tr:hover td {
    background-color: rgba(139, 92, 246, 0.15) !important;
}

/* Plotly chart container */
div[data-testid="stPlotlyChart"] {
    border-radius: 18px;
    border: 1px solid rgba(139, 92, 246, 0.22);
    background: linear-gradient(180deg, rgba(88, 28, 135, 0.08), rgba(17, 24, 39, 0.14));
    padding: 10px 12px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Page header
# ----------------------------
st.title("Correlation Explorer")
st.caption(
    "Explore how inequality indicators relate to potential drivers across countries. "
    "Patterns are observational and do not imply causation."
)

# ----------------------------
# Home config (ONLY source)
# ----------------------------
config = st.session_state.get("analysis_config", {})
home_countries = config.get("countries", [])
home_year_range = config.get("year_range", None)

# ----------------------------
# Load & clean data
# ----------------------------
df = load_all_indicators()
if df.empty:
    st.error("No data available.")
    st.stop()

df = df.dropna(subset=["country", "year", "indicator", "value"]).copy()
df["year"] = pd.to_numeric(df["year"], errors="coerce")
df = df.dropna(subset=["year"])
df["year"] = df["year"].astype(int)

df["value"] = pd.to_numeric(df["value"], errors="coerce")
df = df.dropna(subset=["value"])

if home_countries:
    df = df[df["country"].isin(home_countries)]

if home_year_range:
    df = df[
        (df["year"] >= home_year_range[0]) &
        (df["year"] <= home_year_range[1])
    ]

if df.empty:
    st.error("No data after applying Home page filters.")
    st.stop()

# ----------------------------
# Indicator classification using metadata system
# ----------------------------

# Get available indicators organized by category
available_categories = get_available_indicators_by_category(df)

# Define which categories are for inequality (Y-axis)
INEQUALITY_CATEGORIES = [
    "📉 Income Inequality",
    "🆘 Poverty Metrics"
]

# Define which categories are for drivers (X-axis)
DRIVER_CATEGORIES = [
    "💵 Income & Growth",
    "🎓 Education",
    "💼 Employment & Labor",
    "⚡ Infrastructure & Digital",
    "📊 Other Metrics"
]

# Collect inequality indicators
ineq_candidates = []
for cat_name in INEQUALITY_CATEGORIES:
    if cat_name in available_categories:
        ineq_candidates.extend(available_categories[cat_name]['indicators'])

# Collect driver indicators
driver_candidates = []
for cat_name in DRIVER_CATEGORIES:
    if cat_name in available_categories:
        driver_candidates.extend(available_categories[cat_name]['indicators'])

# Remove duplicates while preserving order
ineq_candidates = list(dict.fromkeys(ineq_candidates))
driver_candidates = list(dict.fromkeys(driver_candidates))

# ----------------------------
# Sidebar (clean & focused with categories)
# ----------------------------
with st.sidebar:
    # st.write("Avail Cats:", list(available_categories.keys()))
    st.subheader("Settings")
    
    # Y-axis (Inequality) selection
    st.markdown("#### Inequality Indicator (Y-axis)")
    
    # Get categories that have indicators
    available_ineq_categories = [cat for cat in INEQUALITY_CATEGORIES if cat in available_categories]
    
    if available_ineq_categories:
        y_category = st.selectbox(
            "Category",
            options=available_ineq_categories,
            key="y_category",
            help="Choose the type of inequality to analyze"
        )
        
        y_indicators_in_cat = available_categories[y_category]['indicators']
        y_indicator = st.selectbox(
            "Specific indicator",
            options=y_indicators_in_cat,
            key="y_indicator",
            help=available_categories[y_category]['description']
        )
    else:
        st.error("No inequality indicators available")
        st.stop()
    
    st.markdown("---")
    
    # X-axis (Driver) selection
    st.markdown("#### Driver Factor (X-axis)")
    
    available_driver_categories = [cat for cat in DRIVER_CATEGORIES if cat in available_categories]
    
    if available_driver_categories:
        x_category = st.selectbox(
            "Category",
            options=available_driver_categories,
            key="x_category",
            help="Choose the potential driver to correlate with inequality"
        )
        
        x_indicators_in_cat = available_categories[x_category]['indicators']
        # Exclude the Y indicator if it happens to be in this category
        x_indicators_filtered = [i for i in x_indicators_in_cat if i != y_indicator]
        
        if x_indicators_filtered:
            x_indicator = st.selectbox(
                "Specific indicator",
                options=x_indicators_filtered,
                key="x_indicator",
                help=available_categories[x_category]['description']
            )
        else:
            st.error(f"No available indicators in {x_category} (excluding Y-axis selection)")
            st.stop()
    else:
        st.error("No driver indicators available")
        st.stop()

    st.markdown("---")
    show_trend = st.checkbox("Show trend line", value=True)

    st.markdown("---")
    if home_countries:
        st.success(f"✓ Using {len(home_countries)} selected countries")
    else:
        st.info("Using all available countries")

# ----------------------------
# Pivot data
# ----------------------------
wide = df.pivot_table(
    index=["country", "year"],
    columns="indicator",
    values="value",
    aggfunc="mean"
).reset_index()

plot_df = wide[["country", "year", x_indicator, y_indicator]].dropna()

coverage = plot_df.groupby("country").size()
countries_present = list(coverage.index)

excluded_countries = []
if home_countries:
    excluded_countries = sorted(list(set(home_countries) - set(countries_present)))

if excluded_countries:
    excluded_list = ", ".join(sorted(excluded_countries))
    st.markdown(
        f"""
        <div class="correlation-alert">
            <strong>Some selected countries are excluded</strong> because there is no overlapping data for the chosen
            X and Y indicators within the selected year range.<br><br>
            <strong>Excluded countries:</strong> {excluded_list}
        </div>
        """,
        unsafe_allow_html=True
    )

if plot_df.empty:
    st.error("No overlapping data available for the selected indicators and filters.")
    st.stop()

# ----------------------------
# Correlation
# ----------------------------
x = plot_df[x_indicator].values
y = plot_df[y_indicator].values

r, p = pearsonr(x, y)

def strength_label(rv):
    if abs(rv) >= 0.7:
        return "Strong"
    if abs(rv) >= 0.4:
        return "Moderate"
    return "Weak"

strength = strength_label(r)
direction = "Positive" if r > 0 else "Negative"

# ----------------------------
# Layout
# ----------------------------
left, right = st.columns([2.2, 1])

with left:
    st.subheader("Scatter view (year-wise observations)")

    if home_year_range:
        st.caption(
            f"Analysis window: {home_year_range[0]}–{home_year_range[1]}. "
            "Only years with overlapping data for the selected X and Y indicators are included."
        )
        full_years = set(range(home_year_range[0], home_year_range[1] + 1))
        used_years = set(plot_df["year"].unique())
        excluded_years = sorted(list(full_years - used_years))

        with st.expander("View excluded years (due to missing data)"):
            if excluded_years:
                st.write("The following years are excluded because one or both indicators are missing:")
                st.write(", ".join(map(str, excluded_years)))
            else:
                st.write("No years are excluded within the selected range.")

    fig = px.scatter(
        plot_df,
        x=x_indicator,
        y=y_indicator,
        color="country",
        opacity=0.85,
        title=f"{human_indicator(y_indicator)} vs {human_indicator(x_indicator)}"
    )

    if show_trend:
        z = np.polyfit(x, y, 1)
        xs = np.linspace(x.min(), x.max(), 120)
        fig.add_scatter(
            x=xs,
            y=np.poly1d(z)(xs),
            mode="lines",
            name="Trend"
        )

    fig.update_traces(marker=dict(size=9, line=dict(width=0.5, color="white")))
    fig.update_layout(height=650)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "toImageButtonOptions": {
                "format": "png",
                "filename": "inequality_correlation",
                "scale": 2
            }
        }
    )

with right:
    st.subheader("Key statistics")
    st.metric("Correlation (r)", f"{r:.3f}")
    st.metric("Strength", strength)
    st.metric("Direction", direction)
    st.metric("Data points", len(plot_df))
    st.metric("Countries shown", len(countries_present))

    st.caption(
        "Strength indicates how closely X and Y move together. "
        "Direction shows whether they move in the same or opposite direction. "
        "Correlation does not imply causation."
    )

# ----------------------------
# Scatter summary
# ----------------------------
st.markdown("---")
st.subheader("Scatter View Summary")

hx = human_indicator(x_indicator)
hy = human_indicator(y_indicator)

st.markdown(
    f"""
    <div class="story-text">
        Each point represents a country in a given year.
        The relationship between <strong>{hx}</strong> and <strong>{hy}</strong>
        appears <em>{strength.lower()} and {direction.lower()}</em>
        <span class="muted">(r = {r:.2f})</span>.
        This shows how a potential driver aligns with inequality patterns over time,
        without implying cause–effect.
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# Country ranking
# ----------------------------
st.markdown("---")
st.subheader("Inequality level snapshot (country ranking)")

ranked = (
    plot_df.groupby("country")[y_indicator]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

ranked.columns = ["Country", "Average value"]
ranked["Average value"] = ranked["Average value"].round(3)

st.dataframe(ranked, use_container_width=True, hide_index=True)

# ----------------------------
# Inequality trend and dispersion
# ----------------------------
st.markdown("---")
st.subheader("Inequality trend and dispersion (2000–2023)")

trend_rows = []
total_years = None
if home_year_range:
    total_years = (home_year_range[1] - home_year_range[0] + 1)

for c in sorted(countries_present):
    sub = plot_df[plot_df["country"] == c].sort_values("year")
    vals = sub[y_indicator].values
    years = sub["year"].values

    avg_val = float(np.mean(vals))
    min_val = float(np.min(vals))
    max_val = float(np.max(vals))
    rng = max_val - min_val

    slope = np.nan
    trend_label = "Stable"
    if len(sub) >= 2:
        slope = float(np.polyfit(years, vals, 1)[0])
        if slope > 0.0001:
            trend_label = "Increasing"
        elif slope < -0.0001:
            trend_label = "Decreasing"

    data_points = int(len(sub))

    if total_years:
        coverage_pct = (data_points / total_years) * 100.0
    else:
        coverage_pct = np.nan

    if data_points >= 18:
        reliability = "High"
    elif data_points >= 10:
        reliability = "Medium"
    else:
        reliability = "Low"

    trend_rows.append({
        "Country": c,
        "Average value": round(avg_val, 3),
        "Minimum": round(min_val, 3),
        "Maximum": round(max_val, 3),
        "Range": round(rng, 3),
        "Trend slope (per year)": round(slope, 4) if not np.isnan(slope) else np.nan,
        "Data points": data_points,
        "Trend": trend_label,
        "Coverage (%)": round(coverage_pct, 1) if not np.isnan(coverage_pct) else np.nan,
        "Data reliability": reliability
    })

trend_df = pd.DataFrame(trend_rows)
st.dataframe(trend_df, use_container_width=True, hide_index=True)

# ----------------------------
# Missing countries explanation
# ----------------------------
st.markdown("---")
with st.expander("Why some countries are not shown"):
    st.write(
        "Countries appear only when both selected indicators (X and Y) are available in the same years. "
        "If a country has missing values for either indicator, it is excluded from the correlation plot to avoid "
        "misleading results."
    )

    total_years_label = ""
    if home_year_range:
        total_years_label = f"Total years in selected range: {home_year_range[0]}–{home_year_range[1]}"

    if total_years_label:
        st.caption(total_years_label)

    availability_rows = []
    if home_year_range:
        total_years = (home_year_range[1] - home_year_range[0] + 1)
    else:
        total_years = None

    all_country_list = sorted(df["country"].unique())
    if home_countries:
        all_country_list = sorted(home_countries)

    for c in all_country_list:
        sub_all = wide[wide["country"] == c][["year", x_indicator, y_indicator]].copy()
        sub_all = sub_all.dropna(subset=[x_indicator, y_indicator])

        dp = int(len(sub_all))
        cov = (dp / total_years * 100.0) if total_years else np.nan

        if dp >= 18:
            reliability = "High"
        elif dp >= 10:
            reliability = "Medium"
        else:
            reliability = "Low"

        availability_rows.append({
            "Country": c,
            "Data points": dp,
            "Coverage (%)": round(cov, 1) if not np.isnan(cov) else np.nan,
            "Data reliability": reliability
        })

    availability_df = pd.DataFrame(availability_rows)
    st.write("Data availability by country (based on the selected X and Y indicators)")
    st.dataframe(availability_df, use_container_width=True, hide_index=True)

    st.markdown("Interpretation guidance")
    st.markdown(
        """
        - Coverage indicates the share of years with usable values for both indicators.
        - Low coverage means correlations may be unstable and should be interpreted with caution.
        """
    )

st.caption(" Correlation Explorer | South Asia Inequality Analysis Platform")


# -----------------
# Navigation
# -----------------
from utils.navigation_ui import bottom_nav_layout
bottom_nav_layout(__file__)
