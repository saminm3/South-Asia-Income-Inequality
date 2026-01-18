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

# Professional text styling
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
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Page header
# ----------------------------
st.title("Inequality Drivers — Visual Correlation Explorer")
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
df["year"] = pd.to_numeric(df["year"], errors="coerce").astype(int)
df["value"] = pd.to_numeric(df["value"], errors="coerce")
df = df.dropna(subset=["year", "value"])

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
# Indicator classification
# ----------------------------
def _norm(s: str) -> str:
    return str(s).lower().strip()

INEQ_KEYWORDS = [
    "gini",
    "income share held by highest",
    "income share held by lowest",
    "poverty",
    "unemployment"
]

DRIVER_KEYWORDS = [
    "gdp",
    "inflation",
    "hdi",
    "schooling",
    "internet",
    "labor force",
    "population"
]

all_indicators = sorted(df["indicator"].unique())
ineq_candidates = [i for i in all_indicators if any(k in _norm(i) for k in INEQ_KEYWORDS)]
driver_candidates = [i for i in all_indicators if any(k in _norm(i) for k in DRIVER_KEYWORDS)]

# ----------------------------
# Sidebar (clean & focused)
# ----------------------------
with st.sidebar:
    st.subheader("Settings")

    y_indicator = st.selectbox(
        "Inequality indicator (Y-axis)",
        options=ineq_candidates
    )

    x_indicator = st.selectbox(
        "Driver factor (X-axis)",
        options=[i for i in driver_candidates if i != y_indicator]
    )

    show_trend = st.checkbox("Show trend line", value=True)

    st.markdown("---")
    if home_countries:
        st.info("Using Home-selected countries")
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

# ----------------------------
# Correlation
# ----------------------------
x = plot_df[x_indicator].values
y = plot_df[y_indicator].values
r, p = pearsonr(x, y)

def strength_label(rv):
    if abs(rv) >= 0.7: return "Strong"
    if abs(rv) >= 0.4: return "Moderate"
    return "Weak"

strength = strength_label(r)
direction = "Positive" if r > 0 else "Negative"

# ----------------------------
# Layout
# ----------------------------
left, right = st.columns([2.2, 1])

with left:
    st.subheader("Scatter view (animated by year)")

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
        fig.add_scatter(
            x=np.linspace(x.min(), x.max(), 120),
            y=np.poly1d(z)(np.linspace(x.min(), x.max(), 120)),
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
                "format": "png",   # user can change to svg/jpeg/webp
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
# Missing countries explanation
# ----------------------------
with st.expander("Why some countries are not shown"):
    st.write(
        "A country appears only if both selected indicators (X and Y) "
        "are available for the same years. Missing data removes the country "
        "to preserve analytical accuracy."
    )
    st.dataframe(coverage.rename("Data points").reset_index(), hide_index=True)

st.caption("Inequality Drivers — Correlation Explorer | South Asia Inequality Analysis Platform")
