import pandas as pd
import numpy as np
from scipy import stats

def generate_insights(df, countries, indicator, year_range):
    """
    Generate auto-insights using Natural Language Generation
    Returns list of insight strings
    """
    insights = []
    
    try:
        # Filter data
        mask = (df['country'].isin(countries)) & \
               (df['indicator'] == indicator) & \
               (df['year'] >= year_range[0]) & \
               (df['year'] <= year_range[1])
        data = df[mask].copy()
        
        if data.empty:
            return ["⚠️ No data available for analysis"]
        
        # 1. TREND ANALYSIS
        for country in countries:
            country_data = data[data['country'] == country].sort_values('year')
            if len(country_data) >= 2:
                first_val = country_data.iloc[0]['value']
                last_val = country_data.iloc[-1]['value']
                change_pct = ((last_val - first_val) / first_val) * 100
                
                if abs(change_pct) > 5:
                    direction = "increased" if change_pct > 0 else "decreased"
                    insights.append(f"📈 **{country}**: {indicator} {direction} by {abs(change_pct):.1f}% from {int(country_data.iloc[0]['year'])} to {int(country_data.iloc[-1]['year'])}")
        
        # 2. REGIONAL RANKING
        latest_year = data['year'].max()
        latest_data = data[data['year'] == latest_year].sort_values('value', ascending=False)
        
        if len(latest_data) > 1:
            top_country = latest_data.iloc[0]
            bottom_country = latest_data.iloc[-1]
            insights.append(f"🏆 **Rankings ({int(latest_year)})**: {top_country['country']} highest ({top_country['value']:.2f}), {bottom_country['country']} lowest ({bottom_country['value']:.2f})")
        
        # 3. REGIONAL COMPARISON
        regional_avg = data.groupby('year')['value'].mean()
        for country in countries:
            country_data = data[data['country'] == country]
            if not country_data.empty:
                country_latest = country_data[country_data['year'] == latest_year]['value'].values
                if len(country_latest) > 0:
                    regional_latest = regional_avg.loc[latest_year]
                    diff_pct = ((country_latest[0] - regional_latest) / regional_latest) * 100
                    if abs(diff_pct) > 10:
                        direction = "above" if diff_pct > 0 else "below"
                        insights.append(f"📊 **{country}**: {abs(diff_pct):.1f}% {direction} regional average")
        
        # 4. VOLATILITY ASSESSMENT
        for country in countries:
            country_data = data[data['country'] == country]['value']
            if len(country_data) > 3:
                volatility = country_data.std()
                mean_val = country_data.mean()
                cv = (volatility / mean_val) * 100 if mean_val != 0 else 0
                
                if cv < 5:
                    insights.append(f"📉 **{country}**: Low volatility (stable, CV={cv:.1f}%)")
                elif cv > 15:
                    insights.append(f"📈 **{country}**: High volatility (fluctuates, CV={cv:.1f}%)")
        
        # 5. ANOMALY DETECTION
        for country in countries:
            country_data = data[data['country'] == country].sort_values('year')
            if len(country_data) > 5:
                z_scores = np.abs(stats.zscore(country_data['value']))
                anomalies = country_data[z_scores > 2]
                if len(anomalies) > 0:
                    for _, anomaly in anomalies.head(1).iterrows():
                        insights.append(f"⚠️ **{country}**: Unusual spike in {int(anomaly['year'])} (value: {anomaly['value']:.2f})")
        
        # 6. MILESTONE THRESHOLDS
        if indicator == 'GINI':
            for country in countries:
                country_latest = data[(data['country'] == country) & (data['year'] == latest_year)]['value'].values
                if len(country_latest) > 0:
                    val = country_latest[0]
                    if val < 30:
                        insights.append(f"✅ **{country}**: GINI < 30 indicates relatively equal society")
                    elif val > 40:
                        insights.append(f"⚠️ **{country}**: GINI > 40 indicates high inequality")
        
        # 7. DATA QUALITY CHECK
        completeness = (data.groupby('country')['value'].count() / len(range(year_range[0], year_range[1] + 1))) * 100
        for country in countries:
            if country in completeness.index:
                comp = completeness[country]
                if comp < 70:
                    insights.append(f"⚠️ **{country}**: Data {comp:.0f}% complete (interpret with caution)")
        
        if not insights:
            insights.append("ℹ️ No significant patterns detected")
        
        return insights[:7]  # Max 7 insights
        
    except Exception as e:
        return [f"⚠️ Error generating insights: {str(e)}"]