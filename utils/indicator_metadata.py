"""
Indicator Metadata and Categorization System (Expanded Curated Version)
Provides user-friendly organization and descriptions for the curated indicators
including Inequality, Education, Jobs, and Digital access.
"""

import pandas as pd
from pathlib import Path
import streamlit as st

# ═══════════════════════════════════════════════════════════════════
# CURATED INDICATOR CATEGORIES
# ═══════════════════════════════════════════════════════════════════

INDICATOR_CATEGORIES = {
    "📉 Income Inequality": {
        "description": "Distribution of income across population segments",
        "patterns": ["Gini", "Income Share", "Share held by"],
        "indicators": [
            "GINI Coefficient",
            "Top 10% Income Share",
            "Top 1% Income Share",
            "Middle 40% Income Share",
            "Bottom 50% Income Share",
            "Gini index",
            "Income share held by highest 10%",
            "Income share held by lowest 20%"
        ]
    },
    
    "💵 Income & Growth": {
        "description": "National income levels and economic growth metrics",
        "patterns": ["GDP", "Income", "GNI", "Growth"],
        "indicators": [
            "Mean Income",
            "Median Income",
            "GDP Per Capita",
            "GDP Growth Rate",
            "GDP per capita (current US$)",
            "GDP growth (annual %)",
            "GNI per capita, Atlas method (current US$)"
        ]
    },
    
    "🎓 Education": {
        "description": "Educational attainment and literacy metrics",
        "patterns": ["Education", "Literacy", "School", "Enrolment"],
        "indicators": [
            "Adult Literacy Rate",
            "Female Literacy Rate",
            "Education Expenditure (% of GDP)",
            "Government expenditure on education, total (% of GDP)",
            "Primary completion rate, total (% of relevant age group)",
            "School enrollment, primary (% gross)"
        ]
    },
    
    "💼 Employment & Labor": {
        "description": "Labor force participation and employment statistics",
        "patterns": ["Unemployment", "Labor Force", "Employment", "Job"],
        "indicators": [
            "Unemployment Rate",
            "Labor Force Participation",
            "Employment Ratio",
            "Unemployment, total (% of total labor force) (modeled ILO estimate)",
            "Labor force participation rate, total (% of total population ages 15+) (modeled ILO estimate)",
            "Employment to population ratio, 15+, total (%) (modeled ILO estimate)"
        ]
    },
    
    "⚡ Infrastructure & Digital": {
        "description": "Access to electricity and digital technology",
        "patterns": ["Internet", "Mobile", "Cellular", "Electricity", "Power"],
        "indicators": [
            "Internet Access (% of Population)",
            "Mobile Subscriptions",
            "Electricity Access (% of Population)",
            "Individuals using the Internet (% of population)",
            "Mobile cellular subscriptions (per 100 people)",
            "Access to electricity (% of population)",
            "Electric power consumption (kWh per capita)"
        ]
    },
    
    "🆘 Poverty Metrics": {
        "description": "Poverty headcount and gap indicators",
        "patterns": ["Poverty", "Headcount", "Gap"],
        "indicators": [
            "Poverty Headcount $2.15/day",
            "Poverty Headcount $3.65/day",
            "Poverty Headcount (National)",
            "Poverty Gap",
            "Poverty headcount ratio at national poverty lines (% of population)",
            "Poverty headcount ratio at $2.15 a day",
            "Poverty headcount ratio at $3.65 a day"
        ]
    }
}


# ═══════════════════════════════════════════════════════════════════
# INDICATOR DESCRIPTIONS (Plain English)
# ═══════════════════════════════════════════════════════════════════

INDICATOR_DESCRIPTIONS = {
    # Custom names
    "GINI Coefficient": "Overall measure of income inequality. 0 = perfect equality, 100 = maximum inequality.",
    "Top 10% Income Share": "The share of total national income earned by the richest 10% of the population.",
    "Top 1% Income Share": "The share of total national income earned by the richest 1% of the population.",
    "Middle 40% Income Share": "The share of income earned by the middle 40% (between the bottom 50% and top 10%).",
    "Bottom 50% Income Share": "The share of total national income earned by the poorest 50% of the population.",
    "Mean Income": "The average income per person in the country.",
    "Median Income": "The income level that divides the population into two equal groups (50th percentile).",
    "GDP Per Capita": "Total economic output (GDP) divided by the total population.",
    "GDP Growth Rate": "Annual percentage growth rate of GDP at market prices.",
    
    # Raw Names
    "Gini index": "Overall measure of income inequality. 0 = perfect equality, 100 = maximum inequality.",
    "GDP per capita (current US$)": "Total economic output (GDP) divided by the total population.",
    "Individuals using the Internet (% of population)": "The percentage of individuals using the Internet.",
    "Mobile cellular subscriptions (per 100 people)": "The number of mobile cellular subscriptions per 100 people.",
    "Access to electricity (% of population)": "The percentage of the population with access to electricity.",
    "Unemployment, total (% of total labor force) (modeled ILO estimate)": "The share of the labor force that is jobless.",
}


# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

# Removed cache to ensure data sync
def get_available_indicators_by_category(df=None):
    """
    Get indicators organized by category, filtered to only show those with actual data.
    Now uses both explicit lists and pattern matching.
    """
    if df is None:
        from utils.loaders import load_inequality_data
        df = load_inequality_data()
    
    available_indicators = set(df['indicator'].unique())
    
    filtered_categories = {}
    mapped_indicators = set()
    
    for category, info in INDICATOR_CATEGORIES.items():
        # 1. Exact matches from the indicators list
        indicator_list = info.get('indicators', [])
        found_exact = [ind for ind in indicator_list if ind in available_indicators]
        
        # 2. Pattern matches for raw names
        patterns = info.get('patterns', [])
        found_patterns = []
        for ind in available_indicators:
            if ind not in indicator_list: # Don't double count
                if any(p.lower() in str(ind).lower() for p in patterns):
                    found_patterns.append(ind)
        
        # Combine
        all_found = sorted(list(set(found_exact + found_patterns)))
        
        if all_found:
            filtered_categories[category] = {
                'description': info['description'],
                'indicators': all_found
            }
            mapped_indicators.update(all_found)
    
    # Fallback for unmapped indicators
    unmapped = available_indicators - mapped_indicators
    if unmapped:
        filtered_categories["📊 Other Metrics"] = {
            'description': "Additional indicators and metrics",
            'indicators': sorted(list(unmapped))
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
        if any(p.lower() in str(indicator_name).lower() for p in info.get('patterns', [])):
            return category
    return "📊 Other"
