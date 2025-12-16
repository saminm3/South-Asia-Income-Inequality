"""
Auto-Insights Generation Module
Generates natural language insights from inequality data
"""

import pandas as pd
import numpy as np

def generate_insights(df, indicator, countries, year_range):
    """
    Generate natural language insights from filtered data
    
    Args:
        df: Main dataset
        indicator: Selected indicator
        countries: List of countries
        year_range: Tuple (start_year, end_year)
    
    Returns:
        List of insight strings
    """
    
    insights = []
    
    try:
        # Filter data
        filtered = df[
            (df['indicator'] == indicator) &
            (df['country'].isin(countries)) &
            (df['year'] >= year_range[0]) &
            (df['year'] <= year_range[1])
        ].copy()
        
        if filtered.empty:
            return ["⚠️ No data available for generating insights"]
        
        # 1. TREND ANALYSIS
        for country in countries:
            country_data = filtered[filtered['country'] == country].sort_values('year')
            if len(country_data) >= 2:
                start_val = country_data.iloc[0]['value']
                end_val = country_data.iloc[-1]['value']
                start_year = int(country_data.iloc[0]['year'])
                end_year = int(country_data.iloc[-1]['year'])
                
                if start_val != 0:
                    change = ((end_val - start_val) / start_val * 100)
                    trend = "increased" if change > 0 else "decreased"
                    insights.append(
                        f"📈 **{country}**: {indicator} {trend} by **{abs(change):.1f}%** "
                        f"from {start_year} ({start_val:.2f}) to {end_year} ({end_val:.2f})"
                    )
        
        # 2. LATEST RANKINGS
        latest_year = int(filtered['year'].max())
        latest_data = filtered[filtered['year'] == latest_year].sort_values('value')
        
        if len(latest_data) >= 2:
            best = latest_data.iloc[0]
            worst = latest_data.iloc[-1]
            insights.append(
                f"🏆 **{latest_year} Rankings**: Lowest {indicator} is **{best['country']}** ({best['value']:.2f}), "
                f"highest is **{worst['country']}** ({worst['value']:.2f})"
            )
        
        # 3. REGIONAL AVERAGE
        if len(latest_data) > 0:
            avg = latest_data['value'].mean()
            median = latest_data['value'].median()
            insights.append(
                f"📊 **Regional Statistics ({latest_year})**: Average = {avg:.2f}, Median = {median:.2f}"
            )
        
        # 4. COMPARISON INSIGHTS
        if len(latest_data) >= 2:
            range_val = latest_data['value'].max() - latest_data['value'].min()
            avg_val = latest_data['value'].mean()
            range_pct = (range_val / avg_val * 100) if avg_val != 0 else 0
            insights.append(
                f"📏 **Disparity**: Range between countries is {range_val:.2f} ({range_pct:.1f}% of average)"
            )
        
        # 5. VOLATILITY ANALYSIS
        for country in countries:
            country_data = filtered[filtered['country'] == country]
            if len(country_data) >= 3:
                std_dev = country_data['value'].std()
                mean_val = country_data['value'].mean()
                cv = (std_dev / mean_val * 100) if mean_val != 0 else 0
                
                if cv > 10:
                    insights.append(
                        f"📉 **{country}**: High variability in {indicator} (CV = {cv:.1f}%)"
                    )
                elif cv < 3:
                    insights.append(
                        f"📊 **{country}**: Stable {indicator} over time (CV = {cv:.1f}%)"
                    )
        
        # 6. ANOMALY DETECTION
        if len(filtered) >= 10:
            overall_mean = filtered['value'].mean()
            overall_std = filtered['value'].std()
            
            for country in countries:
                country_data = filtered[filtered['country'] == country]
                for _, row in country_data.iterrows():
                    z_score = abs((row['value'] - overall_mean) / overall_std) if overall_std != 0 else 0
                    if z_score > 2:
                        insights.append(
                            f"⚡ **Anomaly Detected**: {row['country']} had unusual {indicator} "
                            f"value of {row['value']:.2f} in {int(row['year'])} (Z-score: {z_score:.2f})"
                        )
        
        # 7. THRESHOLD ANALYSIS
        if indicator == 'GINI':
            for country in countries:
                latest_country = latest_data[latest_data['country'] == country]
                if len(latest_country) > 0:
                    gini_val = latest_country.iloc[0]['value']
                    if gini_val > 40:
                        insights.append(
                            f"🔴 **{country}**: High inequality (GINI = {gini_val:.2f}) - Above 40 threshold"
                        )
                    elif gini_val < 30:
                        insights.append(
                            f"🟢 **{country}**: Low inequality (GINI = {gini_val:.2f}) - Below 30 threshold"
                        )
        
        elif indicator == 'HDI':
            for country in countries:
                latest_country = latest_data[latest_data['country'] == country]
                if len(latest_country) > 0:
                    hdi_val = latest_country.iloc[0]['value']
                    if hdi_val >= 0.8:
                        cat = "Very High"
                    elif hdi_val >= 0.7:
                        cat = "High"
                    elif hdi_val >= 0.55:
                        cat = "Medium"
                    else:
                        cat = "Low"
                    insights.append(
                        f"📈 **{country}**: {cat} Human Development (HDI = {hdi_val:.3f})"
                    )
        
        # 8. DATA QUALITY NOTE
        completeness = (len(filtered) / (len(countries) * (year_range[1] - year_range[0] + 1))) * 100
        if completeness < 70:
            insights.append(
                f"⚠️ **Data Quality**: Only {completeness:.0f}% data completeness. "
                f"Some years/countries may have missing data."
            )
        
    except Exception as e:
        insights.append(f"❌ Error generating insights: {str(e)}")
    
    # Limit to most important insights
    return insights[:15] if len(insights) <= 15 else insights[:15] + [f"... and {len(insights)-15} more insights"]

def format_insights_text(insights):
    """Format insights as plain text for export"""
    text = "AUTO-GENERATED INSIGHTS\n"
    text += "=" * 60 + "\n\n"
    
    for i, insight in enumerate(insights, 1):
        # Remove markdown formatting for plain text
        clean_insight = insight.replace('**', '').replace('`', '')
        text += f"{i}. {clean_insight}\n\n"
    
    text += "=" * 60 + "\n"
    text += "Generated by South Asia Inequality Analysis Platform\n"
    text += "Data Sources: World Bank, UNDP\n"
    
    return text