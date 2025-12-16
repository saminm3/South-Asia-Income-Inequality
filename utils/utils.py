def human_indicator(indicator):
    """Convert indicator codes to human-readable names"""
    if not indicator:
        return ""
    
    indicator_mapping = {
        'GINI': 'GINI Coefficient',
        'HDI': 'Human Development Index',
        'GDP_Total': 'GDP (Total)',
        'Labor_Force_Total': 'Labor Force (Total)',
        'GDP_Per_Capita': 'GDP per Capita',
        'Unemployment_Rate': 'Unemployment Rate',
        'Poverty_Rate': 'Poverty Rate',
        'education_index': 'Education Index'
    }
    
    return indicator_mapping.get(indicator, indicator.replace("_", " ").title())

def format_value(val):
    """Format numeric values nicely"""
    try:
        return f"{val:,.2f}"
    except:
        return val

def get_color_scale(indicator):
    """Return a color scale for a given indicator"""
    color_scales = {
        'GINI': 'Reds',
        'HDI': 'Greens',
        'GDP_Total': 'Blues',
        'Labor_Force_Total': 'Purples',
        'Unemployment_Rate': 'Reds',
        'Poverty_Rate': 'Reds',
        'education_index': 'Greens'
    }
    
    return color_scales.get(indicator, "Viridis")

def handle_missing_data(df):
    """
    Remove missing data instead of filling with zeros
    FIXED: Changed from fillna(0) to dropna()
    """
    return df.dropna(subset=['value'])