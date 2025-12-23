import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import json
from datetime import datetime

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.loaders import load_inequality_data
from utils.insights import generate_insights, format_insights_text  # keep your existing rules

# ---- Optional: OpenAI (AI narrative layer) ----
OPENAI_AVAILABLE = True
try:
    from openai import OpenAI
except Exception:
    OPENAI_AVAILABLE = False


# -------------------------
# Page config
# -------------------------
st.set_page_config(
    page_title="Auto Insights",
    page_icon="💡",
    layout="wide"
)

# Load CSS (optional)
try:
    with open("assets/dashboard.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass


# -------------------------
# Helpers
# -------------------------
def ensure_public_analysis(df: pd.DataFrame) -> None:
    """
    Open-access default: if user didn't configure anything (or didn't visit Home),
    create a sensible public analysis config so the page always works.
    """
    if "analysis_config" not in st.session_state or st.session_state.analysis_config is None:
        countries = sorted(df["country"].dropna().unique().tolist())
        indicators = sorted(df["indicator"].dropna().unique().tolist())

        min_year = int(df["year"].min())
        max_year = int(df["year"].max())

        default_indicator = "GINI" if "GINI" in indicators else (indicators[0] if indicators else None)
        default_year_range = (max(min_year, max_year - 20), max_year)

        st.session_state.analysis_config = {
            "countries": countries if len(countries) <= 8 else countries[:5],
            "indicator": default_indicator,
            "year_range": default_year_range,
            "color_scale": "Viridis",
            "timestamp": pd.Timestamp.now(),
        }


def safe_float(x):
    try:
        return float(x)
    except Exception:
        return None


def compute_facts(df: pd.DataFrame, config: dict) -> dict:
    """
    Compute hard facts ONLY in Python.
    AI will only rewrite/interpret these facts, not invent numbers.
    """
    countries = config["countries"]
    indicator = config["indicator"]
    y0, y1 = config["year_range"]

    d = df[
        (df["country"].isin(countries)) &
        (df["indicator"] == indicator) &
        (df["year"].between(y0, y1))
    ].copy()

    d["year"] = pd.to_numeric(d["year"], errors="coerce")
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    d = d.dropna(subset=["country", "year", "value"])

    facts = {
        "scope": {
            "countries": countries,
            "indicator": indicator,
            "year_start": int(y0),
            "year_end": int(y1),
            "rows_used": int(len(d)),
        },
        "data_quality": {},
        "country_trends": [],
        "ranking": {},
        "regional_summary": {},
        "anomalies": [],
        "notes": []
    }

    if d.empty:
        facts["notes"].append("No usable rows after filtering. Check missing values or indicator availability.")
        return facts

    # Data completeness (within selected period)
    years_expected = (int(y1) - int(y0) + 1)
    per_country_counts = d.groupby("country")["year"].nunique().to_dict()
    completeness = {c: round((per_country_counts.get(c, 0) / years_expected) * 100, 1) for c in countries}
    facts["data_quality"]["completeness_pct_by_country"] = completeness
    facts["data_quality"]["expected_years"] = years_expected

    # Country trends: first/last value + % change + volatility
    for c in countries:
        dc = d[d["country"] == c].sort_values("year")
        if dc.empty:
            facts["country_trends"].append({
                "country": c,
                "available": False,
                "reason": "No data in selected range"
            })
            continue

        first_row = dc.iloc[0]
        last_row = dc.iloc[-1]
        v0 = safe_float(first_row["value"])
        v1 = safe_float(last_row["value"])

        pct_change = None
        if v0 is not None and v1 is not None and v0 != 0:
            pct_change = round(((v1 - v0) / abs(v0)) * 100, 2)

        volatility = None
        if len(dc) >= 3:
            volatility = round(float(dc["value"].std(ddof=0)), 3)

        facts["country_trends"].append({
            "country": c,
            "available": True,
            "first_year": int(first_row["year"]),
            "first_value": round(v0, 4) if v0 is not None else None,
            "last_year": int(last_row["year"]),
            "last_value": round(v1, 4) if v1 is not None else None,
            "pct_change": pct_change,
            "volatility_std": volatility
        })

    # Ranking by most recent year in range
    latest_year = int(d["year"].max())
    latest = d[d["year"] == latest_year].groupby("country")["value"].mean().reset_index()
    latest = latest.sort_values("value", ascending=False)

    facts["ranking"]["year"] = latest_year
    facts["ranking"]["highest_country"] = latest.iloc[0]["country"] if len(latest) else None
    facts["ranking"]["highest_value"] = round(float(latest.iloc[0]["value"]), 4) if len(latest) else None
    facts["ranking"]["lowest_country"] = latest.iloc[-1]["country"] if len(latest) else None
    facts["ranking"]["lowest_value"] = round(float(latest.iloc[-1]["value"]), 4) if len(latest) else None

    # Regional summary (simple average across selected countries)
    yearly_avg = d.groupby("year")["value"].mean().reset_index()
    facts["regional_summary"]["avg_first_year"] = int(yearly_avg.iloc[0]["year"])
    facts["regional_summary"]["avg_first_value"] = round(float(yearly_avg.iloc[0]["value"]), 4)
    facts["regional_summary"]["avg_last_year"] = int(yearly_avg.iloc[-1]["year"])
    facts["regional_summary"]["avg_last_value"] = round(float(yearly_avg.iloc[-1]["value"]), 4)
    if facts["regional_summary"]["avg_first_value"] != 0:
        facts["regional_summary"]["avg_pct_change"] = round(
            ((facts["regional_summary"]["avg_last_value"] - facts["regional_summary"]["avg_first_value"])
             / abs(facts["regional_summary"]["avg_first_value"])) * 100,
            2
        )
    else:
        facts["regional_summary"]["avg_pct_change"] = None

    # Simple anomaly detection using z-score within each country series
    for c in countries:
        dc = d[d["country"] == c].sort_values("year")
        if len(dc) < 6:
            continue
        vals = dc["value"].astype(float)
        z = (vals - vals.mean()) / (vals.std(ddof=0) + 1e-9)
        dc2 = dc.assign(z=z.values)
        # Flag |z| >= 2.5 as anomaly
        anom = dc2[np.abs(dc2["z"]) >= 2.5]
        for _, r in anom.iterrows():
            facts["anomalies"].append({
                "country": c,
                "year": int(r["year"]),
                "value": round(float(r["value"]), 4),
                "z_score": round(float(r["z"]), 2)
            })

    return facts


def ai_generate_insights(facts: dict, rule_insights: list, tone: str, n_items: int) -> dict:
    """
    Uses OpenAI Responses API with Structured Outputs (JSON schema).
    AI must only use provided facts and rule insights.
    """
    if not OPENAI_AVAILABLE:
        raise RuntimeError("openai package not installed. Run: pip install openai")

    api_key = None
    # Prefer Streamlit secrets, fallback to env var
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
    else:
        api_key = None

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not found in st.secrets. Add it to .streamlit/secrets.toml")

    client = OpenAI(api_key=api_key)

    schema = {
        "name": "insight_pack",
        "schema": {
            "type": "object",
            "properties": {
                "insights": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "bullet": {"type": "string"},
                            "evidence": {"type": "string"}
                        },
                        "required": ["title", "bullet", "evidence"]
                    }
                },
                "policy_summary": {"type": "string"},
                "limitations": {"type": "string"},
                "next_questions": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["insights", "policy_summary", "limitations", "next_questions"]
        }
    }

    system = (
        "You are a careful data analyst for a public inequality research platform.\n"
        "Rules:\n"
        "1) Use ONLY the provided FACTS and RULE_INSIGHTS. Do not invent numbers, years, causes, or claims.\n"
        "2) Never imply causation (correlation ≠ causation).\n"
        "3) Keep writing concise and readable.\n"
        "4) If data is missing/low completeness, mention it in Limitations.\n"
        "Output must follow the JSON schema.\n"
    )

    user = {
        "tone": tone,
        "target_number_of_insights": n_items,
        "FACTS": facts,
        "RULE_INSIGHTS": rule_insights
    }

    # Responses API create endpoint (recommended) :contentReference[oaicite:2]{index=2}
    # Structured Outputs via text.format json_schema :contentReference[oaicite:3]{index=3}
    resp = client.responses.create(
        model="gpt-5.2-mini",
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)}
        ],
        text={
            "format": {
                "type": "json_schema",
                "json_schema": schema
            }
        },
        store=False  # Responses are stored by default; disable for app privacy :contentReference[oaicite:4]{index=4}
    )

    # Python SDK returns output_text for convenience; parse JSON
    result = json.loads(resp.output_text)
    return result


# -------------------------
# UI
# -------------------------
st.title("💡 Automated Insights (AI-assisted)")
st.caption("This page generates key findings from the selected indicator and time range. AI (optional) rewrites facts into a clearer narrative.")

# Load data
df = load_inequality_data()
if df.empty:
    st.error("❌ No data available. Please check your processed dataset.")
    st.stop()

# Open-access: ensure defaults exist even if Home not visited
ensure_public_analysis(df)
config = st.session_state.analysis_config

# Sidebar controls
with st.sidebar:
    st.header("Insight Settings")

    use_ai = st.toggle("Use AI narrative", value=False, help="If enabled, AI will rewrite computed facts into a clean insight pack.")

    tone = st.selectbox(
        "Writing style",
        options=["research", "policy", "journalist", "student-friendly"],
        index=1
    )

    n_items = st.slider("Number of insights", min_value=3, max_value=10, value=6)

    st.divider()

    st.subheader("Current analysis")
    st.write(f"**Countries:** {', '.join(config['countries'])}")
    st.write(f"**Indicator:** {config['indicator']}")
    st.write(f"**Years:** {config['year_range'][0]}–{config['year_range'][1]}")

# Compute rule-based insights (your existing engine)
with st.spinner("Computing insights..."):
    rule_insights = generate_insights(
        df,
        config["countries"],
        config["indicator"],
        config["year_range"]
    )

# Compute hard facts used for AI
facts = compute_facts(df, config)

st.divider()
st.subheader("📌 Key Findings")

# If rule insights empty, warn and still show facts
if not rule_insights:
    st.warning("No rule-based insights were generated for this selection. Showing computed facts instead.")

# Optionally call AI
ai_result = None
ai_error = None

if use_ai:
    if not OPENAI_AVAILABLE:
        ai_error = "openai package not installed. Run: pip install openai"
    else:
        try:
            with st.spinner("Generating AI narrative (safe mode)..."):
                ai_result = ai_generate_insights(facts, rule_insights, tone=tone, n_items=n_items)
        except Exception as e:
            ai_error = str(e)

if ai_error:
    st.warning(f"AI narrative unavailable: {ai_error}")
    st.info("Falling back to rule-based insights only.")

# ---- Display AI result if available ----
if ai_result:
    # Insights cards
    for item in ai_result.get("insights", [])[:n_items]:
        with st.container():
            st.markdown(f"### {item.get('title','Insight')}")
            st.write(item.get("bullet", ""))
            st.caption(f"Evidence: {item.get('evidence','')}")
            st.divider()

    st.subheader("🧾 Summary")
    st.write(ai_result.get("policy_summary", ""))

    st.subheader("⚠️ Limitations")
    st.write(ai_result.get("limitations", ""))

    st.subheader("🔎 Next Questions")
    for q in ai_result.get("next_questions", []):
        st.write(f"- {q}")

else:
    # ---- Display rule-based insights (existing behavior) ----
    if rule_insights:
        # Group insights by type (your logic)
        trend_insights = [i for i in rule_insights if '📈' in i or '📉' in i]
        ranking_insights = [i for i in rule_insights if '🏆' in i or '🔴' in i or '🟢' in i]
        statistical_insights = [i for i in rule_insights if '📊' in i or '📏' in i]
        quality_insights = [i for i in rule_insights if '⚠️' in i or '✅' in i or '🟡' in i]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📈 Trends")
            if trend_insights:
                for i in trend_insights:
                    st.write(i)
            else:
                st.write("No trend insights available.")

            st.markdown("### 🏆 Rankings")
            if ranking_insights:
                for i in ranking_insights:
                    st.write(i)
            else:
                st.write("No ranking insights available.")

        with col2:
            st.markdown("### 📊 Statistics")
            if statistical_insights:
                for i in statistical_insights:
                    st.write(i)
            else:
                st.write("No statistical insights available.")

            st.markdown("### ✅ Data Quality")
            if quality_insights:
                for i in quality_insights:
                    st.write(i)
            else:
                st.write("No data quality insights available.")

        st.divider()
        st.subheader("📄 Copy-ready Insight Text")
        st.code(format_insights_text(rule_insights), language="text")

    # Always show computed facts for transparency (defense-friendly)
    with st.expander("Show computed facts (transparency)"):
        st.json(facts)

st.divider()
st.caption(
    "Implementation note: AI (if enabled) only rewrites facts computed in Python and does not compute numbers. "
    "This reduces hallucination risk and strengthens academic credibility."
)

