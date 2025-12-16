import streamlit as st

def sidebar_filters(df):
    """Main sidebar filters for the dashboard"""
    countries = st.sidebar.multiselect(
        "Countries",
        sorted(df["country"].dropna().unique()),
        default=sorted(df["country"].dropna().unique())
    )
    y0, y1 = int(df["year"].min()), int(df["year"].max())
    years = st.sidebar.slider("Years", y0, y1, (y0, y1))
    indicator = st.sidebar.selectbox("Indicator", sorted(df["indicator"].dropna().unique()))
    return countries, years, indicator

def indicator_dropdown(indicators):
    """Sidebar dropdown for selecting an indicator"""
    selected = st.sidebar.selectbox(
        "Select Indicator",
        options=indicators
    )
    return selected

def year_slider(min_year, max_year):
    """Sidebar slider for selecting year"""
    selected_year = st.sidebar.slider(
        "Select Year",
        min_value=min_year,
        max_value=max_year,
        value=max_year
    )
    return selected_year