"""
utils/insights.py

Pure utility module (NO Streamlit UI code).
Provides insight generation functions used by pages/8_auto_insights.py and utils/__init__.py.

Fixes circular import by:
- NOT importing from utils.insights inside this file
- NOT importing Streamlit
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import math
import numpy as np
import pandas as pd


YearRange = Tuple[int, int]


def _to_numeric_series(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["year"] = pd.to_numeric(d["year"], errors="coerce")
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    return d.dropna(subset=["country", "indicator", "year", "value"])


def _filter(df: pd.DataFrame, countries: List[str], indicator: str, year_range: YearRange) -> pd.DataFrame:
    y0, y1 = year_range
    d = _to_numeric_series(df)
    d = d[
        (d["country"].isin(countries)) &
        (d["indicator"] == indicator) &
        (d["year"].between(int(y0), int(y1)))
    ].copy()
    d["year"] = d["year"].astype(int)
    return d


def _linear_trend_slope(years: np.ndarray, values: np.ndarray) -> Optional[float]:
    if len(years) < 3:
        return None
    # simple linear regression slope via polyfit
    try:
        slope = float(np.polyfit(years.astype(float), values.astype(float), 1)[0])
        return slope
    except Exception:
        return None


def _pct_change(v0: float, v1: float) -> Optional[float]:
    if v0 is None or v1 is None:
        return None
    if v0 == 0:
        return None
    return ((v1 - v0) / abs(v0)) * 100.0


def _zscore_anomalies(series: pd.Series, z_thresh: float = 2.5) -> List[int]:
    if series.size < 6:
        return []
    vals = series.astype(float).to_numpy()
    mu = float(np.mean(vals))
    sd = float(np.std(vals, ddof=0))
    if sd == 0:
        return []
    z = (vals - mu) / sd
    idx = np.where(np.abs(z) >= z_thresh)[0]
    return idx.tolist()


def _interpret_strength(r: float) -> str:
    ar = abs(r)
    if ar < 0.3:
        return "weak"
    if ar < 0.6:
        return "moderate"
    return "strong"


def generate_multimode_insights(
    df: pd.DataFrame,
    countries: List[str],
    indicator: str,
    year_range: YearRange,
    max_insights: int = 10
) -> Dict[str, List[str]]:
    """
    Returns insights grouped by category so your page can render sections.

    Keys:
    - trends
    - ranking
    - comparison
    - anomalies
    - statistics
    - quality
    - notes
    """
    out: Dict[str, List[str]] = {
        "trends": [],
        "ranking": [],
        "comparison": [],
        "anomalies": [],
        "statistics": [],
        "quality": [],
        "notes": [],
    }

    if not countries or not indicator:
        out["notes"].append("⚠️ Please select at least one country and an indicator.")
        return out

    d = _filter(df, countries, indicator, year_range)

    if d.empty:
        out["notes"].append("⚠️ No data available for the current selection.")
        return out

    y0, y1 = year_range
    expected_years = int(y1) - int(y0) + 1

    # ----- Data quality -----
    avail_years = d.groupby("country")["year"].nunique().to_dict()
    completeness = {c: round((avail_years.get(c, 0) / expected_years) * 100.0, 1) for c in countries}
    avg_comp = round(float(np.mean(list(completeness.values()))), 1) if completeness else 0.0

    badge = "🟢" if avg_comp >= 80 else ("🟡" if avg_comp >= 60 else "🔴")
    out["quality"].append(f"{badge} Data completeness across selected countries: {avg_comp}% (expected {expected_years} years).")

    low = [c for c, p in completeness.items() if p < 60]
    if low:
        out["quality"].append(f"⚠️ Low coverage (<60%) for: {', '.join(low)}. Interpret cautiously.")

    # ----- Regional summary trend -----
    regional = d.groupby("year")["value"].mean().reset_index()
    regional = regional.sort_values("year")
    rv0 = float(regional.iloc[0]["value"])
    rv1 = float(regional.iloc[-1]["value"])
    rchg = _pct_change(rv0, rv1)
    rslope = _linear_trend_slope(regional["year"].to_numpy(), regional["value"].to_numpy())

    if rchg is not None:
        arrow = "📉" if rchg < 0 else "📈"
        out["trends"].append(f"{arrow} Regional average {indicator} changed {rchg:.2f}% from {regional.iloc[0]['year']} to {regional.iloc[-1]['year']}.")

    if rslope is not None:
        direction = "decreasing" if rslope < 0 else "increasing"
        out["statistics"].append(f"📏 Overall trend is {direction} (slope ≈ {rslope:.4f} per year).")

    # ----- Country trends -----
    for c in countries:
        dc = d[d["country"] == c].sort_values("year")
        if dc.empty:
            out["quality"].append(f"🔴 {c}: no data in selected range.")
            continue

        v0 = float(dc.iloc[0]["value"])
        v1 = float(dc.iloc[-1]["value"])
        chg = _pct_change(v0, v1)
        slope = _linear_trend_slope(dc["year"].to_numpy(), dc["value"].to_numpy())
        vol = float(np.std(dc["value"].to_numpy(), ddof=0)) if len(dc) >= 3 else None

        if chg is not None:
            arrow = "📉" if chg < 0 else "📈"
            out["trends"].append(f"{arrow} {c}: {indicator} changed {chg:.2f}% ({dc.iloc[0]['year']}→{dc.iloc[-1]['year']}).")

        if vol is not None:
            out["statistics"].append(f"📊 {c}: volatility σ={vol:.3f} over selected years.")

        # Anomalies
        anom_idx = _zscore_anomalies(dc["value"])
        for i in anom_idx[:2]:  # keep it short
            yr = int(dc.iloc[i]["year"])
            val = float(dc.iloc[i]["value"])
            out["anomalies"].append(f"⚠️ {c}: unusual value in {yr} (≈ {val:.3f}).")

    # ----- Ranking latest year -----
    latest_year = int(d["year"].max())
    latest = d[d["year"] == latest_year].groupby("country")["value"].mean().reset_index()
    latest = latest.sort_values("value", ascending=False)

    if len(latest) >= 2:
        hi_c = latest.iloc[0]["country"]
        hi_v = float(latest.iloc[0]["value"])
        lo_c = latest.iloc[-1]["country"]
        lo_v = float(latest.iloc[-1]["value"])
        out["ranking"].append(f"🏆 {latest_year} ranking: Highest {indicator} = {hi_c} ({hi_v:.3f}), Lowest = {lo_c} ({lo_v:.3f}).")
    else:
        out["ranking"].append(f"🏆 {latest_year}: not enough countries with data to rank.")

    # ----- Comparison vs regional average (latest year) -----
    regional_latest = float(latest["value"].mean()) if not latest.empty else None
    if regional_latest is not None:
        for _, row in latest.iterrows():
            c = row["country"]
            v = float(row["value"])
            diff = v - regional_latest
            sign = "above" if diff > 0 else "below"
            out["comparison"].append(f"📌 {c} is {abs(diff):.3f} {sign} regional avg in {latest_year}.")

    # Limit output volume
    # (Dashboard/pages can still show all categories, but keep each category from exploding)
    for k in out:
        out[k] = out[k][:max(1, max_insights)]
    
    return out


def generate_insights(
    df: pd.DataFrame,
    countries: List[str],
    indicator: str,
    year_range: YearRange,
    max_insights: int = 10
) -> List[str]:
    """
    Flat list (backward compatible with your earlier implementation).
    Your pages can still split by emoji.
    """
    grouped = generate_multimode_insights(df, countries, indicator, year_range, max_insights=max_insights)

    # Flatten in a sensible order
    order = ["trends", "ranking", "comparison", "anomalies", "statistics", "quality", "notes"]
    flat: List[str] = []
    for k in order:
        flat.extend(grouped.get(k, []))

    # Deduplicate while preserving order
    seen = set()
    dedup = []
    for s in flat:
        if s not in seen:
            dedup.append(s)
            seen.add(s)

    return dedup[:max_insights]


def format_insights_text(insights: List[str]) -> str:
    """
    Copy-ready block of text.
    """
    if not insights:
        return "No insights available for the current selection."
    return "\n".join(f"- {i}" for i in insights)


# Backward-compatible alias (your broken file referenced this name)
def format_insights_as_text(insights: List[str]) -> str:
    return format_insights_text(insights)
