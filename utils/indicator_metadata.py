"""
Indicator Metadata and Categorization System
Provides user-friendly organization and descriptions for inequality indicators
"""

import pandas as pd
from pathlib import Path
import streamlit as st

# ═══════════════════════════════════════════════════════════════════
# CURATED INDICATOR CATEGORIES (Like WID.world)
# ═══════════════════════════════════════════════════════════════════

INDICATOR_CATEGORIES = {
    "💵 Average & Total Income": {
        "description": "National income, GDP, and average income metrics",
        "indicators": [
            "Average Income - Post-tax national income average",
            "GDP (current US$)",
            "GDP per capita (current US$)",
            "GNI per capita (current US$)",
            "Average Income (p0p100)",  # Average for full population
        ]
    },
    
    "📉 Income Inequality": {
        "description": "Income distribution and inequality measures",
        "indicators": [
            "Income Inequality (Gini)",
            "Gini index",
            "Top 10% share (Income)",
            "Top 1% share (Income)",
            "Bottom 50% share (Income)",
            "Income share held by highest 10%",
            "Income share held by highest 20%",
            "Income share held by lowest 10%",
            "Income share held by lowest 20%",
            "Income Inequality - Post-tax disposable income Gini",
            "Income Inequality - Pre-tax national income share",
        ]
    },
    
    "💰 Average Wealth": {
        "description": "Net wealth and wealth accumulation metrics",
        "indicators": [
            "Average Wealth (p0p100)",  # Average wealth for full population
            "Wealth per adult",
            "Average net personal wealth",
        ]
    },
    
    "🏛️ Wealth Inequality": {
        "description": "Wealth distribution and concentration",
        "indicators": [
            "Wealth Inequality (Gini)",
            "Top 10% share (Wealth)",
            "Top 1% share (Wealth)",
            "Bottom 50% share (Wealth)",
        ]
    },
    
    "🌿 Carbon Inequality": {
        "description": "Environmental footprint and emissions",
        "indicators": [
            "Carbon Inequality (Gini)",
            "Top 10% carbon emitters",
            "CO2 emissions (metric tons per capita)",
        ]
    },
    
    "♀️ Gender Inequality": {
        "description": "Gender gaps and women's economic participation",
        "indicators": [
            "Female labor income share",
            "Female labor force participation rate (%)",
            "Ratio of female to male labor force participation rate (%)",
        ]
    },
    
    "🎓 Education & Skills": {
        "description": "Educational attainment and literacy",
        "indicators": [
            "Literacy rate, adult total (% of people ages 15 and above)",
            "School enrollment, primary (% gross)",
            "School enrollment, secondary (% gross)",
            "School enrollment, tertiary (% gross)",
            "Completion rate, primary education (%)",
            "Educational attainment, at least completed primary",
        ]
    },
    
    "🏥 Health & Social": {
        "description": "Health outcomes and social indicators",
        "indicators": [
            "Life expectancy at birth, total (years)",
            "Mortality rate, under-5 (per 1,000 live births)",
            "Maternal mortality ratio (per 100,000 live births)",
            "Immunization, DPT (% of children ages 12-23 months)",
        ]
    },
    
    "📈 Other Economic Indicators": {
        "description": "Poverty, employment, and macroeconomic metrics",
        "indicators": [
            "Poverty headcount ratio at $2.15 a day (2017 PPP) (% of population)",
            "Poverty headcount ratio at national poverty lines (% of population)",
            "Unemployment, total (% of total labor force)",
            "Inflation, consumer prices (annual %)",
        ]
    }
}


# ═══════════════════════════════════════════════════════════════════
# INDICATOR DESCRIPTIONS (Plain English)
# ═══════════════════════════════════════════════════════════════════

INDICATOR_DESCRIPTIONS = {
    # Income Inequality
    "Income Inequality (Gini)": "Overall measure of income inequality. 0 = perfect equality, 100 = maximum inequality",
    "Gini index": "Income inequality index ranging from 0 (everyone has same income) to 100 (one person has all income)",
    "Top 10% share (Income)": "Percentage of total income earned by the richest 10% of the population",
    "Top 1% share (Income)": "Percentage of total income earned by the richest 1% of the population",
    "Bottom 50% share (Income)": "Percentage of total income earned by the poorest 50% of the population",
    
    # Wealth Inequality
    "Wealth Inequality (Gini)": "Overall measure of wealth inequality. 0 = perfect equality, 100 = maximum inequality",
    "Top 10% share (Wealth)": "Percentage of total wealth owned by the richest 10% of the population",
    "Top 1% share (Wealth)": "Percentage of total wealth owned by the richest 1% of the population",
    "Bottom 50% share (Wealth)": "Percentage of total wealth owned by the poorest 50% of the population",
    
    # Income Metrics
    "GDP (current US$)": "Total economic output of a country in current US dollars",
    "GDP per capita (current US$)": "Average economic output per person in current US dollars",
    "Average Income - Post-tax national income average": "Average income per person after taxes",
    
    # Gender
    "Female labor income share": "Percentage of total labor income earned by women",
    
    # Carbon
    "Carbon Inequality (Gini)": "Measure of inequality in carbon emissions across population",
    "Top 10% carbon emitters": "Share of emissions from the highest 10% of emitters",
    
    # Education
    "Literacy rate, adult total (% of people ages 15 and above)": "Percentage of adults who can read and write",
    "Completion rate, primary education (%)": "Percentage of students who complete primary school",
    
    # Health
    "Life expectancy at birth, total (years)": "Average number of years a newborn is expected to live",
    "Mortality rate, under-5 (per 1,000 live births)": "Number of children who die before age 5 per 1,000 births",
}


# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def get_available_indicators_by_category(df=None):
    """
    Get indicators organized by category, filtered to only show those with actual data
    
    Parameters:
    -----------
    df : pd.DataFrame, optional
        The full dataset to check for available indicators
    
    Returns:
    --------
    dict : Category -> list of available indicators
    """
    if df is None:
        # Load data to check availability
        from utils.loaders import load_inequality_data
        df = load_inequality_data()
    
    available_indicators = set(df['indicator'].unique())
    
    filtered_categories = {}
    
    for category, info in INDICATOR_CATEGORIES.items():
        # Find which indicators from this category actually exist in data
        available_in_category = [
            ind for ind in info['indicators'] 
            if ind in available_indicators
        ]
        
        if available_in_category:
            filtered_categories[category] = {
                'description': info['description'],
                'indicators': available_in_category
            }
    
    return filtered_categories


def get_indicator_description(indicator_name):
    """Get plain-English description for an indicator"""
    return INDICATOR_DESCRIPTIONS.get(indicator_name, f"Data for {indicator_name}")


def get_all_curated_indicators():
    """Get flat list of all curated indicators across all categories"""
    all_indicators = []
    for category_info in INDICATOR_CATEGORIES.values():
        all_indicators.extend(category_info['indicators'])
    return all_indicators


def get_category_for_indicator(indicator_name):
    """Find which category an indicator belongs to"""
    for category, info in INDICATOR_CATEGORIES.items():
        if indicator_name in info['indicators']:
            return category
    return "📊 Other"


def filter_high_quality_indicators(df, min_countries=3, year_range=(2000, 2025)):
    """
    Filter dataset to only include high-quality indicators
    
    Parameters:
    -----------
    df : pd.DataFrame
        Full dataset
    min_countries : int
        Minimum number of countries that must have data
    year_range : tuple
        (start_year, end_year) to filter by
    
    Returns:
    --------
    pd.DataFrame : Filtered dataset with only high-quality indicators
    """
    # Filter by year range
    df_filtered = df[
        (df['year'] >= year_range[0]) & 
        (df['year'] <= year_range[1])
    ].copy()
    
    # Count countries per indicator
    indicator_coverage = df_filtered.groupby('indicator')['country'].nunique()
    
    # Keep only indicators with sufficient coverage
    good_indicators = indicator_coverage[indicator_coverage >= min_countries].index.tolist()
    
    return df_filtered[df_filtered['indicator'].isin(good_indicators)]


# ═══════════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 80)
    print("INDICATOR METADATA SYSTEM")
    print("=" * 80)
    
    print("\nTotal curated indicator categories:", len(INDICATOR_CATEGORIES))
    print("Total curated indicators:", len(get_all_curated_indicators()))
    
    print("\n" + "=" * 80)
    print("CATEGORIES:")
    print("=" * 80)
    
    for category, info in INDICATOR_CATEGORIES.items():
        print(f"\n{category}")
        print(f"  Description: {info['description']}")
        print(f"  Indicators: {len(info['indicators'])}")
        for ind in info['indicators'][:3]:
            print(f"    • {ind}")
        if len(info['indicators']) > 3:
            print(f"    ... and {len(info['indicators']) - 3} more")
