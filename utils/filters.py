import streamlit as st

def sidebar_filters(df):
    """Main sidebar filters for the dashboard"""
    
    if df.empty:
        st.sidebar.warning("No data available for filters")
        return [], (2000, 2024), None
    
    # Countries
    countries = st.sidebar.multiselect(
        "Countries",
        sorted(df["country"].dropna().unique()),
        default=sorted(df["country"].dropna().unique())
    )
    
    # Years
    try:
        y0, y1 = int(df["year"].min()), int(df["year"].max())
        years = st.sidebar.slider("Years", y0, y1, (y0, y1))
    except:
        years = (2000, 2024)
    
    # Indicator
    indicators = sorted(df["indicator"].dropna().unique())
    if len(indicators) > 0:
        indicator = st.sidebar.selectbox("Indicator", indicators)
    else:
        indicator = None
    
    return countries, years, indicator

def indicator_dropdown(indicators):
    """Sidebar dropdown for selecting an indicator"""
    if not indicators or len(indicators) == 0:
        st.sidebar.warning("No indicators available")
        return None
    
    selected = st.sidebar.selectbox(
        "Select Indicator",
        options=indicators
    )
    return selected

def year_slider(min_year, max_year):
    """Sidebar slider for selecting year"""
    try:
        selected_year = st.sidebar.slider(
            "Select Year",
            min_value=int(min_year),
            max_value=int(max_year),
            value=int(max_year)  # default to latest year
        )
        return selected_year
    except:
        st.sidebar.error("Invalid year range")
        return max_year

def country_multiselect(df, default_all=False):
    """Multiselect for countries with optional select all"""
    countries = sorted(df["country"].dropna().unique())
    
    if default_all:
        default = countries
    else:
        default = countries[:3] if len(countries) >= 3 else countries
    
    selected = st.sidebar.multiselect(
        "Select Countries",
        options=countries,
        default=default
    )
    
    return selected

def year_range_slider(df):
    """Year range slider"""
    try:
        min_year = int(df['year'].min())
        max_year = int(df['year'].max())
        
        year_range = st.sidebar.slider(
            "Year Range",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year)
        )
        
        return year_range
    except:
        return (2000, 2024)