import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.loaders import load_all_indicators
from utils.utils import format_value
from utils.help_system import render_help_button
from utils.sidebar import apply_all_styles
st.set_page_config(
    page_title="Sunburst Explorer",
    page_icon="🌟",
    layout="wide"
)
render_help_button("sunburst")
apply_all_styles()
# Load custom CSS
try:
    with open('assets/dashboard.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.title("Sunburst Explorer")
st.markdown("### Hierarchical view of indicators across South Asia (dominance view)")

# ✅ Use Home config if available (NO extra country selection here)
config = st.session_state.get("analysis_config", None)
home_countries = config.get("countries", []) if config else []
home_year_range = config.get("year_range", None) if config else None

# Load data
with st.spinner("Loading data..."):
    df = load_all_indicators()

if df.empty:
    st.error("No data available")
    st.stop()

# Clean basic
df = df.dropna(subset=["country", "year", "indicator", "value"]).copy()
df["year"] = pd.to_numeric(df["year"], errors="coerce")
df["value"] = pd.to_numeric(df["value"], errors="coerce")
df = df.dropna(subset=["year", "value"])

# Sidebar: Year + Color only (NO country selection)
with st.sidebar:
    st.subheader("⚙️ Sunburst Settings")

    # year range from home (if exists)
    if home_year_range:
        df_yr = df[(df["year"] >= home_year_range[0]) & (df["year"] <= home_year_range[1])]
        if not df_yr.empty:
            df = df_yr

    available_years = sorted(df["year"].unique(), reverse=True)
    if not available_years:
        st.error("No valid years found.")
        st.stop()

    # choose best year (most coverage)
    year_coverage = df.groupby("year").agg(value_count=("value", "count"), ind_count=("indicator", "nunique"))
    year_coverage["score"] = year_coverage["value_count"] * year_coverage["ind_count"]
    best_year = int(year_coverage["score"].idxmax())

    selected_year = st.selectbox(
        "Select Year",
        options=available_years,
        index=available_years.index(best_year) if best_year in available_years else 0
    )

    color_scheme = st.selectbox(
        "Color Scheme",
        options=["Plasma", "Viridis", "Inferno", "Magma", "Cividis", "Turbo"],
        index=0
    )

    st.divider()
    st.caption("This chart shows **indicator dominance** after normalization (0–100 per indicator).")

# Filter year
year_df = df[df["year"] == selected_year].copy()
if year_df.empty:
    st.warning(f"No data for year {selected_year}")
    st.stop()

# Filter to home countries if set (NO new selection)
if home_countries:
    year_df = year_df[year_df["country"].isin(home_countries)].copy()

if year_df.empty:
    st.warning("No data after applying Home selected countries.")
    st.stop()

# Normalize per indicator for fair sunburst sizing
sunburst_df = year_df[["country", "indicator", "value"]].copy()
sunburst_df = sunburst_df.dropna(subset=["value"])
sunburst_df = sunburst_df[sunburst_df["value"] != 0]

sunburst_df["normalized_value"] = 0.0
for ind in sunburst_df["indicator"].unique():
    m = sunburst_df["indicator"] == ind
    vals = sunburst_df.loc[m, "value"]

    if vals.isna().all() or (vals == 0).all():
        continue

    # Handle special scales
    if ind.strip().lower() in ["gini", "gini index"]:
        # keep as-is (already comparable scale-ish)
        sunburst_df.loc[m, "normalized_value"] = vals
    elif ind.strip().lower() == "hdi":
        # make it 0-100-ish
        sunburst_df.loc[m, "normalized_value"] = vals * 100
    else:
        vmin, vmax = vals.min(), vals.max()
        if pd.notna(vmin) and pd.notna(vmax) and vmax > vmin:
            sunburst_df.loc[m, "normalized_value"] = ((vals - vmin) / (vmax - vmin)) * 100
        else:
            sunburst_df.loc[m, "normalized_value"] = 50.0

sunburst_df = sunburst_df.dropna(subset=["normalized_value"])
sunburst_df = sunburst_df[sunburst_df["normalized_value"] > 0]

if sunburst_df.empty or sunburst_df["normalized_value"].sum() == 0:
    st.error("Sunburst cannot render because normalized values sum to 0. Try a different year.")
    st.stop()

# Add region
sunburst_df["Region"] = "South Asia"

# Pretty value for hover
def fmt(val):
    try:
        return format_value(val)
    except:
        return str(val)

sunburst_df["formatted_value"] = sunburst_df["value"].apply(fmt)

# ---------------- Sunburst ----------------
fig = px.sunburst(
    sunburst_df,
    path=["Region", "country", "indicator"],
    values="normalized_value",
    color="normalized_value",
    color_continuous_scale=color_scheme,
    hover_data=["formatted_value"]
)

fig.update_traces(
    textinfo="label+percent parent",
    hovertemplate="<b>%{label}</b><br>Actual: %{customdata[0]}<br>Dominance (normalized): %{value:.1f}/100<extra></extra>",
    marker=dict(line=dict(color="white", width=2))
)

fig.update_layout(
    title=f"Indicator Dominance Breakdown ({selected_year})",
    title_x=0.5,
    height=850
)

st.plotly_chart(fig, use_container_width=True)

# --- IMPORTANT clarification to avoid confusion ---
st.info(
    " **Important:** Sunburst slice sizes show **indicator dominance after normalization**, "
    "not direct inequality level and not causation. We use dominance of inequality-related indicators "
    "(Gini / income-share / unemployment / poverty) to build a simple **inequality signal**."
)

# ============================================================
# ✅ NEW: EASY COUNTRY-WISE “VISUALIZATION STORY” (NO AVG CHART)
# ============================================================
st.divider()
st.header("Visualization Story (Country-wise)")

countries_in_view = sorted(sunburst_df["country"].unique())
if home_countries:
    countries_in_view = [c for c in home_countries if c in countries_in_view]

# --- Build a simple inequality-signal score from dominance (NOT causation) ---
# We score only *inequality-related* indicators when they are present.
def norm_name(s: str) -> str:
    return str(s).strip().lower()

INEQ_KEYWORDS = [
    "gini", "gini index",
    "income share held by highest 10", "income share held by highest 20",
    "income share held by lowest 10",
    "poverty", "unemployment"
]

def is_ineq_indicator(ind: str) -> bool:
    t = norm_name(ind)
    return any(k in t for k in INEQ_KEYWORDS)

# For each country: score = sum of normalized dominance for ineq indicators (capped to be stable)
scores = []
drivers_map = {}

for c in countries_in_view:
    cdf = sunburst_df[sunburst_df["country"] == c].copy()
    cdf["is_ineq"] = cdf["indicator"].apply(is_ineq_indicator)

    ineq_part = cdf[cdf["is_ineq"]].copy()
    score = float(ineq_part["normalized_value"].sum()) if not ineq_part.empty else 0.0

    # top drivers (ineq-related first; fallback to overall)
    if not ineq_part.empty:
        top_drivers = ineq_part.sort_values("normalized_value", ascending=False).head(3)["indicator"].tolist()
    else:
        top_drivers = cdf.sort_values("normalized_value", ascending=False).head(3)["indicator"].tolist()

    drivers_map[c] = top_drivers
    scores.append({"country": c, "score": score})

scores_df = pd.DataFrame(scores).sort_values("score", ascending=False).reset_index(drop=True)

# Assign High/Moderate/Lower RELATIVE to selected countries
# (If 1 country only -> Moderate)
levels = {}
if len(scores_df) <= 1:
    for c in countries_in_view:
        levels[c] = "Moderate"
else:
    # rank-based split
    for i, row in scores_df.iterrows():
        if i == 0:
            levels[row["country"]] = "High"
        elif i == len(scores_df) - 1:
            levels[row["country"]] = "Lower"
        else:
            levels[row["country"]] = "Moderate"

# Show a tiny summary line first (simple for non-technical)
st.markdown(f"**For {selected_year}, among the selected countries:**")
for c in countries_in_view:
    lvl = levels.get(c, "Moderate")
    emoji = "🔴" if lvl == "High" else ("🟠" if lvl == "Moderate" else "🟢")
    st.write(f"- {emoji} **{lvl} inequality signal:** {c}")

st.caption("(This is a simple indicator-dominance signal using Gini / income-share / poverty / unemployment patterns — not causation.)")

# Expandable story per country (arrow click)
for c in countries_in_view:
    lvl = levels.get(c, "Moderate")
    emoji = "🔴" if lvl == "High" else ("🟠" if lvl == "Moderate" else "🟢")

    top_drivers = drivers_map.get(c, [])
    driver_text = ", ".join(top_drivers) if top_drivers else "available indicators"

    # one-line insight (country name included)
    if lvl == "High":
        one_line = f"**{c} shows a HIGH inequality signal** because inequality-related indicators dominate the visualization ({driver_text}) despite development/economic indicators being present."
    elif lvl == "Moderate":
        one_line = f"**{c} shows a MODERATE inequality signal** mainly due to visible concentration indicators ({driver_text}), while other welfare indicators also contribute."
    else:
        one_line = f"**{c} shows a LOWER inequality signal (relative)** because inequality-related dominance is weaker; the visualization is driven more by non-distribution indicators ({driver_text})."

    with st.expander(f"{emoji} {c} — {lvl.upper()} inequality signal (click to read why)"):
        st.markdown("**Why (from the sunburst dominance):**")
        if top_drivers:
            for d in top_drivers:
                st.write(f"- Prominent slice: **{d}**")
        else:
            st.write("- No clear inequality-related indicators available for this country-year in the dataset.")

        st.markdown("**One-line insight:**")
        st.write(one_line)

        st.caption("Note: dominance = what stands out after normalization; it helps explain patterns but does not prove inequality or causation by itself.")

# ============================================================
# ⭐ COUNTRY SPOTLIGHT (Story Mode)
# ============================================================
st.divider()
st.header("Country Spotlight (Story Mode)")

if not countries_in_view:
    st.warning("No countries available for Spotlight.")
    st.stop()

# Session state for spotlight index
if "spotlight_idx" not in st.session_state:
    st.session_state.spotlight_idx = 0

colA, colB, colC = st.columns([1, 2, 1])
with colA:
    if st.button("⬅️ Previous"):
        st.session_state.spotlight_idx = (st.session_state.spotlight_idx - 1) % len(countries_in_view)
with colC:
    if st.button("Next ➡️"):
        st.session_state.spotlight_idx = (st.session_state.spotlight_idx + 1) % len(countries_in_view)

spot_country = countries_in_view[st.session_state.spotlight_idx]

with colB:
    lvl = levels.get(spot_country, "Moderate")
    emoji = "🔴" if lvl == "High" else ("🟠" if lvl == "Moderate" else "🟢")
    st.subheader(f"Spotlight: {spot_country} ({selected_year}) — {emoji} {lvl} signal")
    st.caption("Use Previous/Next to explore — this uses Home selection automatically.")

c_df = sunburst_df[sunburst_df["country"] == spot_country].copy()
if c_df.empty:
    st.warning("No data for spotlight country.")
    st.stop()

# Bubble chart: indicator bubbles sized by normalized dominance, colored by dominance
bubble_df = c_df.sort_values("normalized_value", ascending=False).copy()
bubble_df["indicator_short"] = bubble_df["indicator"].astype(str).str.slice(0, 45)

fig_bubble = px.scatter(
    bubble_df,
    x="normalized_value",
    y="indicator_short",
    size="normalized_value",
    color="normalized_value",
    color_continuous_scale=color_scheme,
    hover_data=["formatted_value"],
    title="🫧 Indicator Bubble View (size = normalized dominance)"
)
fig_bubble.update_layout(height=540, xaxis_title="Normalized dominance (0–100)", yaxis_title="")
st.plotly_chart(fig_bubble, use_container_width=True)

# ✅ Explanation under bubble view (simple)
st.info(
    "How to read the bubble chart: **bigger bubble = more dominant indicator** for this country (after normalization). "
    "It highlights what stands out most (e.g., income-share / Gini / unemployment), which we use to form a simple inequality signal."
)

# Underlying data (optional)
with st.expander("View underlying data (for this country)"):
    view = c_df[["indicator", "formatted_value", "normalized_value"]].copy()
    view.columns = ["Indicator", "Actual Value", "Dominance (0-100)"]
    view["Dominance (0-100)"] = view["Dominance (0-100)"].round(1)
    st.dataframe(view, use_container_width=True, hide_index=True)

st.divider()
st.caption("Sunburst Explorer | South Asia Inequality Analysis Platform")
