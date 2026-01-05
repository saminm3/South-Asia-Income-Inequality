"""
utils/insights.py - Oracle-Inspired Auto-Insights Engine v2.0

INSPIRED BY: Oracle Analytics Server Auto Insights
- Insight ranking by "probability of interest"
- Multiple insight types with user toggles
- Column focusing for deeper analysis
- Progressive disclosure
- Statistical rigor + smart narratives

New Features:
✓ Insight scoring and ranking
✓ Indexed trend comparison (normalize to baseline 1.0)
✓ Contribution analysis (who drove regional change)
✓ Top N + "rest average" comparison
✓ Simple forecasting
✓ 80/20 analysis
✓ Categorized output with metadata
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import pandas as pd
from scipy import stats


YearRange = Tuple[int, int]


# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

INSIGHT_TYPES = {
    'trends': 'Temporal Trends',
    'indexed_trends': 'Indexed Comparison',
    'rankings': 'Rankings & Leaders',
    'comparisons': 'Regional Comparisons',
    'contribution': 'Contribution Analysis',
    'forecast': 'Forecasting',
    'anomalies': 'Anomaly Detection',
    'pareto': '80/20 Analysis',
    'statistics': 'Statistical Metrics',
    'quality': 'Data Quality'
}


# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def _to_numeric_series(df: pd.DataFrame) -> pd.DataFrame:
    """Convert to numeric and clean data"""
    d = df.copy()
    d["year"] = pd.to_numeric(d["year"], errors="coerce")
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    return d.dropna(subset=["country", "indicator", "year", "value"])


def _filter(df: pd.DataFrame, countries: List[str], indicator: str, year_range: YearRange) -> pd.DataFrame:
    """Filter dataframe by countries, indicator, and year range"""
    y0, y1 = year_range
    d = _to_numeric_series(df)
    d = d[
        (d["country"].isin(countries)) &
        (d["indicator"] == indicator) &
        (d["year"].between(int(y0), int(y1)))
    ].copy()
    d["year"] = d["year"].astype(int)
    return d


def _linear_regression(years: np.ndarray, values: np.ndarray) -> Optional[Dict[str, float]]:
    """Perform linear regression and return statistics"""
    if len(years) < 3:
        return None
    
    try:
        slope, intercept, r_value, p_value, std_err = stats.linregress(years, values)
        return {
            'slope': float(slope),
            'r_squared': float(r_value ** 2),
            'p_value': float(p_value),
            'intercept': float(intercept),
            'std_err': float(std_err)
        }
    except Exception:
        return None


def _forecast_simple(years: np.ndarray, values: np.ndarray, periods_ahead: int = 5) -> Optional[Dict[str, Any]]:
    """Simple linear forecast"""
    reg = _linear_regression(years, values)
    if not reg:
        return None
    
    last_year = int(years[-1])
    future_years = np.arange(last_year + 1, last_year + periods_ahead + 1)
    forecast_values = reg['slope'] * future_years + reg['intercept']
    
    # Simple confidence interval (±2 std errors)
    std_err = reg['std_err']
    ci_lower = forecast_values - (2 * std_err * np.sqrt(1 + 1/len(years)))
    ci_upper = forecast_values + (2 * std_err * np.sqrt(1 + 1/len(years)))
    
    return {
        'years': future_years.tolist(),
        'values': forecast_values.tolist(),
        'ci_lower': ci_lower.tolist(),
        'ci_upper': ci_upper.tolist(),
        'confidence': 'high' if reg['r_squared'] > 0.7 else 'medium' if reg['r_squared'] > 0.4 else 'low'
    }


def _zscore_anomalies(series: pd.Series, z_thresh: float = 2.0) -> List[Tuple[int, float, float]]:
    """Detect anomalies using Z-score. Returns list of (index, value, z_score)"""
    if series.size < 6:
        return []
    
    vals = series.astype(float).to_numpy()
    mu = float(np.mean(vals))
    sd = float(np.std(vals, ddof=1))
    
    if sd == 0:
        return []
    
    z_scores = (vals - mu) / sd
    anomalies = []
    
    for i, (val, z) in enumerate(zip(vals, z_scores)):
        if abs(z) >= z_thresh:
            anomalies.append((i, float(val), float(z)))
    
    return anomalies


def _score_insight(insight: Dict, insight_type: str) -> float:
    """
    Oracle-inspired: Score insights by "probability of interest"
    
    Scoring criteria:
    - Statistical significance: +5
    - Large magnitude change: +4
    - Anomaly present: +4
    - High data quality: +2
    - Recent trend change: +3
    - Strong R²: +3
    """
    score = 0.0
    
    # Base score by type (some types inherently more interesting)
    type_scores = {
        'anomalies': 4,
        'contribution': 4,
        'indexed_trends': 3,
        'forecast': 3,
        'trends': 2,
        'rankings': 2,
        'comparisons': 1,
        'pareto': 3,
        'statistics': 1,
        'quality': 0
    }
    score += type_scores.get(insight_type, 1)
    
    # Statistical significance
    if insight.get('p_value', 1) < 0.05:
        score += 5
    
    # Large magnitude
    change = abs(insight.get('change_relative', 0))
    if change > 20:
        score += 4
    elif change > 10:
        score += 2
    
    # Anomalies detected
    if insight.get('anomalies') and len(insight.get('anomalies', [])) > 0:
        score += 4
    
    # High data quality
    completeness = insight.get('completeness_pct', 0)
    if completeness > 80:
        score += 2
    elif completeness > 60:
        score += 1
    
    # Strong R²
    r_squared = insight.get('r_squared', 0)
    if r_squared > 0.7:
        score += 3
    elif r_squared > 0.5:
        score += 1
    
    # Extreme values (very high or very low)
    if insight.get('is_best') or insight.get('is_worst'):
        score += 3
    
    return score


# ═══════════════════════════════════════════════════════════════════
# NEW ORACLE-INSPIRED INSIGHT GENERATORS
# ═══════════════════════════════════════════════════════════════════

def _generate_indexed_trends(d: pd.DataFrame, countries: List[str]) -> List[Dict]:
    """
    Oracle's Indexed Trending - Normalize all countries to index 1.0 at start
    Shows RELATIVE growth, not absolute values
    """
    insights = []
    
    baseline_data = {}
    indexed_data = {}
    
    for country in countries:
        dc = d[d["country"] == country].sort_values("year")
        if dc.empty or len(dc) < 2:
            continue
        
        baseline = float(dc.iloc[0]["value"])
        if baseline == 0:
            continue
        
        # Index to baseline (1.0 at start)
        indexed = (dc["value"] / baseline).tolist()
        
        baseline_data[country] = baseline
        indexed_data[country] = {
            'years': dc["year"].tolist(),
            'indexed_values': indexed,
            'final_index': indexed[-1],
            'relative_change_pct': (indexed[-1] - 1.0) * 100
        }
    
    if len(indexed_data) >= 2:
        # Find best and worst relative performers
        ranked = sorted(indexed_data.items(), key=lambda x: x[1]['relative_change_pct'])
        
        best = ranked[0]
        worst = ranked[-1]
        
        insights.append({
            'type': 'indexed_comparison',
            'title': 'Relative Performance Comparison',
            'best_performer': best[0],
            'best_change': best[1]['relative_change_pct'],
            'worst_performer': worst[0],
            'worst_change': worst[1]['relative_change_pct'],
            'all_indexed': indexed_data,
            'baselines': baseline_data,
            'narrative': f"When normalized to baseline 1.0, {best[0]} showed strongest relative improvement ({best[1]['relative_change_pct']:+.1f}%), while {worst[0]} showed weakest performance ({worst[1]['relative_change_pct']:+.1f}%)."
        })
    
    return insights


def _generate_contribution_analysis(d: pd.DataFrame, countries: List[str], year_range: YearRange) -> List[Dict]:
    """
    Oracle's Contribution Bridge - Who drove regional change?
    Waterfall chart showing attribution
    """
    insights = []
    
    y0, y1 = year_range
    
    # Get regional totals at start and end
    start_data = d[d["year"] == y0].groupby("country")["value"].mean()
    end_data = d[d["year"] == y1].groupby("country")["value"].mean()
    
    if len(start_data) < 2 or len(end_data) < 2:
        return insights
    
    # Calculate each country's contribution to regional change
    contributions = {}
    for country in countries:
        if country in start_data.index and country in end_data.index:
            contribution = float(end_data[country] - start_data[country])
            contributions[country] = contribution
    
    if not contributions:
        return insights
    
    total_change = sum(contributions.values())
    
    # Sort by contribution
    sorted_contrib = sorted(contributions.items(), key=lambda x: x[1])
    
    insights.append({
        'type': 'contribution',
        'title': 'Regional Change Attribution',
        'total_change': total_change,
        'contributions': contributions,
        'sorted_contributions': sorted_contrib,
        'narrative': f"Regional change of {total_change:+.2f} points driven by: " + 
                    ", ".join([f"{c} ({v:+.2f})" for c, v in sorted_contrib[:3]])
    })
    
    return insights


def _generate_top_n_with_rest(d: pd.DataFrame, countries: List[str], n: int = 5) -> List[Dict]:
    """
    Oracle's Top 10 + Average of Rest
    Shows gap between leaders and average
    """
    insights = []
    
    latest_year = int(d["year"].max())
    latest = d[d["year"] == latest_year].groupby("country")["value"].mean().sort_values()
    
    if len(latest) < n + 1:
        return insights
    
    top_n = latest.iloc[:n]
    rest = latest.iloc[n:]
    rest_avg = float(rest.mean())
    
    insights.append({
        'type': 'top_n_comparison',
        'title': f'Top {n} vs Rest',
        'top_n': top_n.to_dict(),
        'rest_average': rest_avg,
        'gap': float(top_n.iloc[-1] - rest_avg),
        'narrative': f"Top {n} performers average {top_n.mean():.2f}, while remaining countries average {rest_avg:.2f} (gap: {abs(top_n.mean() - rest_avg):.2f} points)"
    })
    
    return insights


def _generate_pareto_80_20(d: pd.DataFrame, countries: List[str]) -> List[Dict]:
    """
    Oracle's 80/20 Analysis
    Top 20% of countries account for X% of total change
    """
    insights = []
    
    # Calculate total change for each country
    country_changes = {}
    for country in countries:
        dc = d[d["country"] == country].sort_values("year")
        if len(dc) >= 2:
            change = abs(float(dc.iloc[-1]["value"] - dc.iloc[0]["value"]))
            country_changes[country] = change
    
    if len(country_changes) < 3:
        return insights
    
    # Sort by change (descending)
    sorted_changes = sorted(country_changes.items(), key=lambda x: x[1], reverse=True)
    total_change = sum(country_changes.values())
    
    # Get top 20%
    top_20_count = max(1, int(len(sorted_changes) * 0.2))
    top_20 = sorted_changes[:top_20_count]
    top_20_contribution = sum([c[1] for c in top_20])
    top_20_pct = (top_20_contribution / total_change * 100) if total_change > 0 else 0
    
    insights.append({
        'type': 'pareto_80_20',
        'title': '80/20 Analysis',
        'top_20_percent': [c[0] for c in top_20],
        'top_20_contribution_pct': top_20_pct,
        'all_contributions': sorted_changes,
        'narrative': f"Top {top_20_count} country(ies) ({top_20_count/len(countries)*100:.0f}%) account for {top_20_pct:.1f}% of total change"
    })
    
    return insights


# ═══════════════════════════════════════════════════════════════════
# MAIN INSIGHT GENERATION WITH RANKING
# ═══════════════════════════════════════════════════════════════════

def generate_ranked_insights(
    df: pd.DataFrame,
    countries: List[str],
    indicator: str,
    year_range: YearRange,
    enabled_types: Optional[List[str]] = None,
    max_insights: int = 15,
    focus_mode: bool = False
) -> Dict[str, Any]:
    """
    Oracle-inspired: Generate and rank insights by probability of interest
    
    Args:
        df: Data
        countries: Countries to analyze
        indicator: Metric to analyze
        year_range: Year range
        enabled_types: Which insight types to generate (None = all)
        max_insights: Maximum insights to return
        focus_mode: If True, deep analysis on fewer countries (2-3)
    
    Returns:
        {
            'ranked_insights': [...],  # Top N insights ranked by score
            'all_insights': [...],     # All insights organized by category
            'metadata': {...},         # Analysis metadata
            'settings': {...}          # Settings used
        }
    """
    
    # Default to all types
    if enabled_types is None:
        enabled_types = list(INSIGHT_TYPES.keys())
    
    # Focus mode: limit to 2-3 countries for deeper analysis
    if focus_mode and len(countries) > 3:
        # Select top 3 by data completeness
        completeness = {}
        for c in countries:
            dc = df[(df["country"] == c) & (df["indicator"] == indicator)]
            completeness[c] = len(dc)
        top_countries = sorted(completeness.items(), key=lambda x: x[1], reverse=True)[:3]
        countries = [c[0] for c in top_countries]
    
    # Filter data
    d = _filter(df, countries, indicator, year_range)
    
    if d.empty:
        return {
            'ranked_insights': [],
            'all_insights': {},
            'metadata': {'error': 'No data available'},
            'settings': {'enabled_types': enabled_types, 'focus_mode': focus_mode}
        }
    
    all_insights = []
    y0, y1 = year_range
    
    # ═══════════════════════════════════════════════════════════════
    # GENERATE INSIGHTS BY TYPE
    # ═══════════════════════════════════════════════════════════════
    
    # 1. INDEXED TRENDS (Oracle-inspired)
    if 'indexed_trends' in enabled_types:
        indexed = _generate_indexed_trends(d, countries)
        for ins in indexed:
            ins['insight_type'] = 'indexed_trends'
            ins['score'] = _score_insight(ins, 'indexed_trends')
            all_insights.append(ins)
    
    # 2. CONTRIBUTION ANALYSIS (Oracle-inspired)
    if 'contribution' in enabled_types:
        contrib = _generate_contribution_analysis(d, countries, year_range)
        for ins in contrib:
            ins['insight_type'] = 'contribution'
            ins['score'] = _score_insight(ins, 'contribution')
            all_insights.append(ins)
    
    # 3. TOP N + REST (Oracle-inspired)
    if 'rankings' in enabled_types:
        top_n = _generate_top_n_with_rest(d, countries, n=min(5, len(countries)-1))
        for ins in top_n:
            ins['insight_type'] = 'rankings'
            ins['score'] = _score_insight(ins, 'rankings')
            all_insights.append(ins)
    
    # 4. PARETO 80/20 (Oracle-inspired)
    if 'pareto' in enabled_types:
        pareto = _generate_pareto_80_20(d, countries)
        for ins in pareto:
            ins['insight_type'] = 'pareto'
            ins['score'] = _score_insight(ins, 'pareto')
            all_insights.append(ins)
    
    # 5. FORECASTING (Oracle-inspired)
    if 'forecast' in enabled_types:
        for country in countries:
            dc = d[d["country"] == country].sort_values("year")
            if len(dc) >= 5:
                years = dc["year"].to_numpy()
                values = dc["value"].to_numpy()
                forecast = _forecast_simple(years, values, periods_ahead=5)
                
                if forecast:
                    ins = {
                        'type': 'forecast',
                        'insight_type': 'forecast',
                        'title': f'{country} Forecast',
                        'country': country,
                        'forecast_data': forecast,
                        'narrative': f"If current trend continues, {country} will reach {forecast['values'][-1]:.2f} by {forecast['years'][-1]} (confidence: {forecast['confidence']})"
                    }
                    ins['score'] = _score_insight(ins, 'forecast')
                    all_insights.append(ins)
    
    # 6. STANDARD TRENDS
    if 'trends' in enabled_types:
        for country in countries:
            dc = d[d["country"] == country].sort_values("year")
            if len(dc) >= 2:
                v0 = float(dc.iloc[0]["value"])
                v1 = float(dc.iloc[-1]["value"])
                change_pct = ((v1 - v0) / v0 * 100) if v0 != 0 else 0
                
                reg = _linear_regression(dc["year"].to_numpy(), dc["value"].to_numpy())
                
                ins = {
                    'type': 'trend',
                    'insight_type': 'trends',
                    'title': f'{country} Trend',
                    'country': country,
                    'change_relative': change_pct,
                    'change_absolute': v1 - v0,
                    'first_value': v0,
                    'last_value': v1,
                    'p_value': reg['p_value'] if reg else 1,
                    'r_squared': reg['r_squared'] if reg else 0,
                    'narrative': f"{country} changed {change_pct:+.1f}% over the period"
                }
                ins['score'] = _score_insight(ins, 'trends')
                all_insights.append(ins)
    
    # 7. ANOMALIES
    if 'anomalies' in enabled_types:
        for country in countries:
            dc = d[d["country"] == country].sort_values("year")
            if len(dc) >= 6:
                anomalies = _zscore_anomalies(dc["value"])
                if anomalies:
                    for idx, val, z in anomalies[:2]:  # Top 2 anomalies
                        year = int(dc.iloc[idx]["year"])
                        ins = {
                            'type': 'anomaly',
                            'insight_type': 'anomalies',
                            'title': f'{country} Anomaly in {year}',
                            'country': country,
                            'year': year,
                            'value': val,
                            'z_score': z,
                            'anomalies': [(idx, val, z)],
                            'narrative': f"{country} showed unusual value in {year} (Z-score: {z:.2f})"
                        }
                        ins['score'] = _score_insight(ins, 'anomalies')
                        all_insights.append(ins)
    
    # ═══════════════════════════════════════════════════════════════
    # RANK AND ORGANIZE
    # ═══════════════════════════════════════════════════════════════
    
    # Sort by score (descending)
    ranked = sorted(all_insights, key=lambda x: x.get('score', 0), reverse=True)
    
    # Organize by category
    by_category = {}
    for insight_type in INSIGHT_TYPES.keys():
        by_category[insight_type] = [ins for ins in ranked if ins.get('insight_type') == insight_type]
    
    # Metadata
    metadata = {
        'total_generated': len(all_insights),
        'total_shown': min(max_insights, len(ranked)),
        'countries_analyzed': len(countries),
        'indicator': indicator,
        'year_range': year_range,
        'focus_mode': focus_mode,
        'enabled_types': enabled_types
    }
    
    return {
        'ranked_insights': ranked[:max_insights],
        'all_insights': by_category,
        'metadata': metadata,
        'settings': {
            'enabled_types': enabled_types,
            'focus_mode': focus_mode,
            'max_insights': max_insights
        }
    }


# ═══════════════════════════════════════════════════════════════════
# BACKWARDS COMPATIBILITY
# ═══════════════════════════════════════════════════════════════════

def generate_multimode_insights(
    df: pd.DataFrame,
    countries: List[str],
    indicator: str,
    year_range: YearRange,
    max_insights: int = 15
) -> Dict[str, Any]:
    """Backwards compatible wrapper"""
    result = generate_ranked_insights(df, countries, indicator, year_range, max_insights=max_insights)
    
    # Convert to old format for existing UI
    return {
        'summary': {
            'narrative': f"Analysis complete. Generated {result['metadata']['total_generated']} insights, showing top {result['metadata']['total_shown']}."
        },
        'simple': result['ranked_insights'],
        'technical': result['ranked_insights'],
        'complete': result['ranked_insights'],
        'categories': result['all_insights']
    }


def format_insights_as_text(insights: Dict, mode: str = 'simple') -> str:
    """Format insights as plain text for export"""
    lines = []
    lines.append("=" * 70)
    lines.append("AUTO-GENERATED INSIGHTS REPORT")
    lines.append("Oracle-Inspired Analysis Engine v2.0")
    lines.append("=" * 70)
    lines.append("")
    
    if 'metadata' in insights:
        meta = insights['metadata']
        lines.append(f"Total Insights Generated: {meta.get('total_generated', 0)}")
        lines.append(f"Showing Top: {meta.get('total_shown', 0)}")
        lines.append(f"Countries Analyzed: {meta.get('countries_analyzed', 0)}")
        lines.append(f"Focus Mode: {'Enabled' if meta.get('focus_mode') else 'Disabled'}")
        lines.append("")
    
    ranked = insights.get('ranked_insights', [])
    for idx, insight in enumerate(ranked, 1):
        lines.append(f"{idx}. {insight.get('title', 'Insight')} (Score: {insight.get('score', 0):.1f})")
        lines.append(f"   {insight.get('narrative', 'No description')}")
        lines.append("")
    
    lines.append("=" * 70)
    return "\n".join(lines)