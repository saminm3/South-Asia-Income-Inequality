import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from scipy.stats import pearsonr
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.loaders import load_all_indicators
from utils.utils import human_indicator

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Inequality Drivers (Correlation)",
    page_icon="🔗",
    layout="wide"
)

# Load custom CSS
try:
    with open("assets/dashboard.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.title("🔗 Inequality Drivers — Visual Correlation Explorer")
st.caption("Pick an inequality measure (Y) and a potential driver (X). The chart shows patterns across selected countries over a year range.")

# ----------------------------
# Home config (NO new selection)
# ----------------------------
config = st.session_state.get("analysis_config", None)
home_countries = config.get("countries", []) if config else []
home_year_range = config.get("year_range", None) if config else None

# ----------------------------
# Load + clean data
# ----------------------------
df = load_all_indicators()
if df.empty:
    st.error("❌ No data available")
    st.stop()

df = df.dropna(subset=["country", "year", "indicator", "value"]).copy()
df["year"] = pd.to_numeric(df["year"], errors="coerce")
df["value"] = pd.to_numeric(df["value"], errors="coerce")
df = df.dropna(subset=["year", "value"]).copy()
df["year"] = df["year"].astype(int)

# Apply Home selections
if home_countries:
    df = df[df["country"].isin(home_countries)].copy()

if home_year_range:
    df = df[(df["year"] >= int(home_year_range[0])) & (df["year"] <= int(home_year_range[1]))].copy()

if df.empty:
    st.error("❌ No data left after applying Home page filters (countries/year).")
    st.stop()

# ----------------------------
# Indicator lists (short + focused)
# ----------------------------
def _norm(s: str) -> str:
    return str(s).strip().lower()

INEQ_KEYWORDS = [
    "gini",
    "income share held by highest",
    "income share held by lowest",
    "poverty headcount",
    "unemployment",
]

DRIVER_KEYWORDS = [
    "gdp per capita",
    "gdp (current",
    "inflation",
    "hdi",
    "mean years of schooling",
    "expected years of schooling",
    "completion rate",
    "individuals using the internet",
    "labor force",
    "population",
]

all_indicators = sorted(df["indicator"].dropna().unique())

ineq_candidates = [i for i in all_indicators if any(k in _norm(i) for k in INEQ_KEYWORDS)]
driver_candidates = [i for i in all_indicators if any(k in _norm(i) for k in DRIVER_KEYWORDS)]

# Fallback (just in case dataset naming differs)
if not ineq_candidates:
    ineq_candidates = all_indicators[:10]
if not driver_candidates:
    driver_candidates = all_indicators

# ----------------------------
# Sidebar (ONLY what you wanted)
# ----------------------------
with st.sidebar:
    st.subheader("⚙️ Settings")

    years = sorted(df["year"].unique())
    min_year, max_year = int(min(years)), int(max(years))

    year_range = st.slider(
        "Year range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )

    # Defaults
    default_y = "Gini index" if "Gini index" in ineq_candidates else ineq_candidates[0]
    y_indicator = st.selectbox(
        "Inequality indicator (Y-axis)",
        options=ineq_candidates,
        index=ineq_candidates.index(default_y) if default_y in ineq_candidates else 0
    )

    x_options = [i for i in driver_candidates if i != y_indicator]
    if not x_options:
        x_options = [i for i in all_indicators if i != y_indicator]

    preferred = None
    for cand in ["GDP per capita (current US$)", "HDI", "Inflation, consumer prices (annual %)", "Expected years of schooling"]:
        if cand in x_options:
            preferred = cand
            break

    x_indicator = st.selectbox(
        "Driver factor (X-axis)",
        options=x_options,
        index=x_options.index(preferred) if preferred in x_options else 0
    )

    show_trend = st.checkbox("Show trend line", value=True)

    st.markdown("---")
    if home_countries:
        st.success("Using Home countries:\n\n" + ", ".join(home_countries))
    else:
        st.info("No Home countries selected → using all countries in dataset.")

# Apply year range filter
df = df[(df["year"] >= int(year_range[0])) & (df["year"] <= int(year_range[1]))].copy()

# ----------------------------
# Pivot to align X & Y per (country,year)
# ----------------------------
wide = df.pivot_table(
    index=["country", "year"],
    columns="indicator",
    values="value",
    aggfunc="mean"
).reset_index()

if x_indicator not in wide.columns or y_indicator not in wide.columns:
    st.error("❌ Selected indicators are not available together in this year range.")
    st.stop()

plot_df = wide[["country", "year", x_indicator, y_indicator]].dropna().copy()

# Coverage check (explains why sometimes fewer countries appear)
coverage = plot_df.groupby("country").size().sort_values(ascending=False)
countries_present = list(coverage.index)

if len(plot_df) < 5:
    st.warning("⚠️ Not enough overlapping points for this pair in the selected year range. Try a wider range or different indicators.")
    with st.expander("See why (data coverage)"):
        st.write("A country appears only when it has **both** X and Y values in the chosen year range.")
        st.dataframe(coverage.rename("points").reset_index(), use_container_width=True, hide_index=True)
    st.stop()

# ----------------------------
# Correlation stats
# ----------------------------
x = plot_df[x_indicator].values
y = plot_df[y_indicator].values

try:
    r, p = pearsonr(x, y)
except Exception:
    st.error("❌ Could not compute correlation.")
    st.stop()

def strength_label(rv: float) -> str:
    a = abs(rv)
    if a >= 0.7: return "Strong"
    if a >= 0.4: return "Moderate"
    return "Weak"

strength = strength_label(r)
direction = "Positive" if r > 0 else "Negative"
sig = (p < 0.05)

# ----------------------------
# Inequality meaning rules (for “solid” inequality narrative)
# ----------------------------
y_norm = _norm(y_indicator)

# Most inequality indicators: higher = worse inequality
# Exception: “income share held by lowest 10%” higher = better (less inequality)
higher_y_is_worse = True
if "income share held by lowest" in y_norm:
    higher_y_is_worse = False

def inequality_label_from_rank(rank_idx: int, total: int) -> str:
    # top third = High, middle = Moderate, bottom = Lower
    if total <= 2:
        return "Higher" if rank_idx == 0 else "Lower"
    third = max(1, total // 3)
    if rank_idx < third:
        return "High"
    if rank_idx < 2 * third:
        return "Moderate"
    return "Lower"

# Country inequality snapshot: use mean of Y in selected range
country_y = plot_df.groupby("country")[y_indicator].mean().sort_values(ascending=not higher_y_is_worse)
# If higher is worse, we sort descending (so highest values first)
# If higher is better (lowest 10% share), we invert meaning:
# We'll rank by "inequality pressure" where lower lowest10share = worse
if not higher_y_is_worse:
    # inequality pressure = negative of lowest10share
    country_y = plot_df.groupby("country")[y_indicator].mean().sort_values(ascending=True)

ranked = country_y.reset_index()
ranked.columns = ["Country", "Avg_Y"]

# drivers list for the narrative (simple)
def short_name(s: str) -> str:
    return human_indicator(s)

# ----------------------------
# Layout
# ----------------------------
left, right = st.columns([2.2, 1])

with left:
    st.subheader("📌 Scatter view")
    title = f"{short_name(y_indicator)} (Y) vs {short_name(x_indicator)} (X) — {year_range[0]}–{year_range[1]}"

    fig = px.scatter(
        plot_df,
        x=x_indicator,
        y=y_indicator,
        color="country",
        hover_data={"country": True, "year": True},
        opacity=0.8,
        title=title
    )

    if show_trend:
        z = np.polyfit(x, y, 1)
        line = np.poly1d(z)
        x_line = np.linspace(np.min(x), np.max(x), 120)
        y_line = line(x_line)
        fig.add_scatter(x=x_line, y=y_line, mode="lines", name="Trend")

    fig.update_layout(
        height=650,
        legend_title="Country",
        hovermode="closest",
        xaxis_title=short_name(x_indicator),
        yaxis_title=short_name(y_indicator),
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("📊 Key stats")
    st.metric("Correlation (r)", f"{r:.3f}")
    st.metric("Strength", strength)
    st.metric("Direction", direction)
    st.metric("Data points", f"{len(plot_df)}")
    st.metric("Countries shown", f"{len(countries_present)}")

    # Professional significance text (small)
    if sig:
        st.success("Statistically reliable pattern (p < 0.05)")
    else:
        st.info("Pattern not statistically reliable (p ≥ 0.05)")

# ----------------------------
# Professional inequality insight (NOT messy blue box)
# ----------------------------
st.markdown("---")
st.subheader("📈 Scatter View Story (What the chart shows)")

# Interpret the relation in inequality words
hx = short_name(x_indicator)
hy = short_name(y_indicator)

if r > 0:
    rel_text = f"Across {year_range[0]}–{year_range[1]}, higher **{hx}** tends to come with higher **{hy}**."
else:
    rel_text = f"Across {year_range[0]}–{year_range[1]}, higher **{hx}** tends to come with lower **{hy}**."

# Convert to inequality pressure
if higher_y_is_worse:
    if r > 0:
        ineq_text = f"That means inequality pressure may **rise** when {hx} increases (based on {hy})."
    else:
        ineq_text = f"That means inequality pressure may **ease** when {hx} increases (based on {hy})."
else:
    # lowest 10% share: higher is good
    if r > 0:
        ineq_text = f"That suggests the **bottom-share improves** as {hx} increases (lower inequality pressure)."
    else:
        ineq_text = f"That suggests the **bottom-share shrinks** as {hx} increases (higher inequality pressure)."

# Clean “one paragraph” narrative
st.markdown(
    f"Each point in the chart represents a country in a given year between "
    f"**{year_range[0]}–{year_range[1]}**. "
    f"The pattern between **{hx}** and **{hy}** is **{strength.lower()} and {direction.lower()}** "
    f"(r = {r:.2f}). {rel_text} {ineq_text}"
)



st.caption("This chart highlights patterns observed in the data. It does not claim direct cause–effect relationships.")

# ----------------------------
# Inequality ranking (THIS is the “solid inequality” part)
# ----------------------------
st.markdown("---")
st.subheader("🏷️ Inequality level snapshot (country ranking from Y)")

st.caption(
    f"This ranks the selected countries by the average of **{hy}** over {year_range[0]}–{year_range[1]}. "
    f"It is a **signal** from the chosen inequality indicator (not a full inequality index)."
)

# Add label column
total = len(ranked)
labels = []
for i in range(total):
    labels.append(inequality_label_from_rank(i, total))
ranked["Level"] = labels

# Make numbers nicer
ranked["Avg_Y"] = ranked["Avg_Y"].round(3)

# Show as table (simple and professional)
st.dataframe(ranked, use_container_width=True, hide_index=True)

# Optional: quick sentence
if total >= 1:
    top_country = ranked.iloc[0]["Country"]
    top_level = ranked.iloc[0]["Level"]
    st.markdown(
        f"**Quick takeaway:** In this range, **{top_country}** shows the **{top_level} inequality signal** under the selected measure (**{hy}**)."
    )

# Explain missing countries (professional)
with st.expander("Why some selected Home countries may not appear"):
    st.write(
        "A country shows up only if it has **both** selected indicators (X and Y) available in the chosen year range. "
        "If values are missing for either indicator, it will disappear from the scatter."
    )
    st.dataframe(coverage.rename("points").reset_index(), use_container_width=True, hide_index=True)

st.caption("Inequality Drivers — Correlation Explorer | South Asia Inequality Analysis Platform")
