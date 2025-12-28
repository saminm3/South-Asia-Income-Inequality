import pandas as pd
import numpy as np

def human_indicator(indicator):
    """Convert indicator codes to human-readable names"""
    if not indicator:
        return ""
    
    # Enhanced mapping for better display
    indicator_mapping = {
        'GINI': 'GINI Coefficient',
        'HDI': 'Human Development Index',
        'GDP_Total': 'GDP (Total)',
        'Labor_Force_Total': 'Labor Force (Total)',
        'GDP_Per_Capita': 'GDP per Capita',
        'Unemployment_Rate': 'Unemployment Rate',
        'Poverty_Rate': 'Poverty Rate',
        'education_index': 'Education Index',
        'Income_Index': 'Income Index',
        'Life_Expectancy': 'Life Expectancy',
        'Mean_Years_School': 'Mean Years of Schooling'
    }
    
    return indicator_mapping.get(indicator, indicator.replace("_", " ").title())

def format_value(val):
    """Format numeric values nicely"""
    try:
        val = float(val)
        if val >= 1e9:
            return f"{val/1e9:.2f}B"
        elif val >= 1e6:
            return f"{val/1e6:.2f}M"
        elif val >= 1000:
            return f"{val:,.2f}"
        else:
            return f"{val:.2f}"
    except:
        return str(val)

def get_color_scale(indicator):
    """Return appropriate color scale for indicator"""
    # Color scales based on indicator meaning
    # Red = bad (higher is worse)
    # Green = good (higher is better)
    # Blue = neutral
    
    color_scales = {
        # Inequality indicators (higher = worse)
        'GINI': 'Reds',
        'Poverty_Rate': 'Reds',
        'Unemployment_Rate': 'Reds',
        
        # Development indicators (higher = better)
        'HDI': 'Greens',
        'education_index': 'Greens',
        'Income_Index': 'Greens',
        'Life_Expectancy': 'Greens',
        'Mean_Years_School': 'Greens',
        
        # Economic indicators (neutral)
        'GDP_Total': 'Blues',
        'GDP_Per_Capita': 'Blues',
        'Labor_Force_Total': 'Purples',
    }
    
    return color_scales.get(indicator, "Viridis")

def handle_missing_data(df):
    """
    Handle missing data properly
    FIXED: Changed from fillna(0) to dropna() to preserve data integrity
    """
    # Drop rows with missing critical values
    # DO NOT fill with 0 as it distorts inequality measures
    return df.dropna(subset=['value'])

def validate_dataframe(df, required_columns):
    """Validate that dataframe has required columns"""
    if df.empty:
        return False, "DataFrame is empty"
    
    missing_cols = set(required_columns) - set(df.columns)
    if missing_cols:
        return False, f"Missing columns: {missing_cols}"
    
    return True, "Valid"

def get_country_code(country_name):
    """Get ISO3 country code from country name"""
    country_codes = {
        'Bangladesh': 'BGD',
        'India': 'IND',
        'Pakistan': 'PAK',
        'Nepal': 'NPL',
        'Sri Lanka': 'LKA',
        'Afghanistan': 'AFG',
        'Bhutan': 'BTN',
        'Maldives': 'MDV'
    }
    return country_codes.get(country_name, country_name[:3].upper())

def calculate_statistics(series):
    """Calculate summary statistics for a series"""
    try:
        return {
            'mean': series.mean(),
            'median': series.median(),
            'std': series.std(),
            'min': series.min(),
            'max': series.max(),
            'count': series.count()
        }
    except:
        return None

def format_percentage(value):
    """Format value as percentage"""
    try:
        return f"{float(value):.1f}%"
    except:
        return str(value)

def safe_divide(numerator, denominator):
    """Safely divide two numbers, return None if denominator is 0"""
    try:
        if denominator == 0:
            return None
        return numerator / denominator
    except:
        return None