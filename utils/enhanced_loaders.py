"""
Enhanced Data Loaders for New Datasets
Integrates World Bank Education, Jobs, WDI, and WID data
"""

import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path

# Base paths
DATA_RAW = Path("data/raw")
DATA_PROCESSED = Path("data/processed")

@st.cache_data
def load_education_data():
    """
    Load World Bank Education Statistics
    Returns: DataFrame with education indicators by country and year (2000-2025)
    """
    try:
        edu_file = DATA_RAW / "P_Data_Extract_From_Education_Statistics_-_All_Indicators" / "31eb65da-cd5b-4684-ae89-dc70eb60007f_Data.csv"
        df = pd.read_csv(edu_file)
        
        # Melt the wide format to long format
        year_cols = [col for col in df.columns if '[YR' in col]
        id_cols = ['Country Name', 'Country Code', 'Series', 'Series Code']
        
        df_long = df.melt(id_vars=id_cols, value_vars=year_cols, 
                          var_name='Year', value_name='Value')
        
        # Extract year from column name like "2020 [YR2020]"
        df_long['Year'] = df_long['Year'].str.extract(r'(\d{4})').astype(float)
        
        # **FILTER: 2000-2025 ONLY**
        df_long = df_long[(df_long['Year'] >= 2000) & (df_long['Year'] <= 2025)]
        
        # Convert value to numeric
        df_long['Value'] = pd.to_numeric(df_long['Value'], errors='coerce')
        
        # Filter for South Asian countries
        south_asia = ['Bangladesh', 'India', 'Pakistan', 'Sri Lanka', 'Nepal', 
                      'Afghanistan', 'Bhutan', 'Maldives']
        df_long = df_long[df_long['Country Name'].isin(south_asia)]
        
        # Remove null values
        df_long = df_long.dropna(subset=['Value'])
        
        return df_long
    except Exception as e:
        print(f"Error loading education data: {e}")
        return pd.DataFrame()



@st.cache_data
def load_jobs_data():
    """
    Load World Bank Jobs/Employment Data
    Returns: DataFrame with employment indicators by country and year (2000-2025)
    """
    try:
        jobs_file = DATA_RAW / "P_Data_Extract_From_Jobs" / "50b84243-4489-4d54-8c8e-719385d0e88e_Data.csv"
        df = pd.read_csv(jobs_file)
        
        # Melt to long format
        year_cols = [col for col in df.columns if '[YR' in col]
        id_cols = ['Country Name', 'Country Code', 'Series Name', 'Series Code']
        
        df_long = df.melt(id_vars=id_cols, value_vars=year_cols,
                          var_name='Year', value_name='Value')
        
        df_long['Year'] = df_long['Year'].str.extract(r'(\d{4})').astype(float)
        
        # **FILTER: 2000-2025 ONLY**
        df_long = df_long[(df_long['Year'] >= 2000) & (df_long['Year'] <= 2025)]
        
        df_long['Value'] = pd.to_numeric(df_long['Value'], errors='coerce')
        
        # Filter for South Asian countries
        south_asia = ['Bangladesh', 'India', 'Pakistan', 'Sri Lanka', 'Nepal',
                      'Afghanistan', 'Bhutan', 'Maldives']
        df_long = df_long[df_long['Country Name'].isin(south_asia)]
        
        # Remove null values
        df_long = df_long.dropna(subset=['Value'])
        
        return df_long
    except Exception as e:
        print(f"Error loading jobs data: {e}")
        return pd.DataFrame()


@st.cache_data
def load_wdi_data():
    """
    Load World Development Indicators
    Returns: DataFrame with WDI indicators by country and year (2000-2025)
    """
    try:
        wdi_file = DATA_RAW / "P_Data_Extract_From_World_Development_Indicators" / "d05a5752-a39e-4091-82ba-be7ef61e6e9c_Data.csv"
        df = pd.read_csv(wdi_file)
        
        # Melt to long format
        year_cols = [col for col in df.columns if '[YR' in col]
        id_cols = ['Country Name', 'Country Code', 'Series Name', 'Series Code']
        
        df_long = df.melt(id_vars=id_cols, value_vars=year_cols,
                          var_name='Year', value_name='Value')
        
        df_long['Year'] = df_long['Year'].str.extract(r'(\d{4})').astype(float)
        
        # **FILTER: 2000-2025 ONLY**
        df_long = df_long[(df_long['Year'] >= 2000) & (df_long['Year'] <= 2025)]
        
        df_long['Value'] = pd.to_numeric(df_long['Value'], errors='coerce')
        
        # Filter for South Asian countries
        south_asia = ['Bangladesh', 'India', 'Pakistan', 'Sri Lanka', 'Nepal',
                      'Afghanistan', 'Bhutan', 'Maldives']
        df_long = df_long[df_long['Country Name'].isin(south_asia)]
        
        # Remove null values
        df_long = df_long.dropna(subset=['Value'])
        
        return df_long
    except Exception as e:
        print(f"Error loading WDI data: {e}")
        return pd.DataFrame()


@st.cache_data
def load_wid_data():
    """
    Load World Inequality Database (WID) Data
    This contains REAL income percentile data!
    Returns: DataFrame with income percentiles by country and year
    """
    try:
        wid_file = DATA_RAW / "WID_Data_Metadata" / "WID_Data_31122025-094739.csv"
        
        # Read WID file (skip the header row)
        df = pd.read_csv(wid_file, skiprows=1, sep=';')
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        return df
    except Exception as e:
        print(f"Error loading WID data: {e}")
        return pd.DataFrame()


@st.cache_data
def load_mpi_data():
    """
    Load Global Multidimensional Poverty Index (MPI) Data
    Returns: DataFrame with subnational MPI indicators for South Asia
    """
    try:
        mpi_file = DATA_RAW / "global_mpi_2024.csv"
        if not mpi_file.exists():
            return pd.DataFrame()
            
        # Read file, skipping the HXL tag row (second row)
        df = pd.read_csv(mpi_file)
        df = df.iloc[1:].copy() # Remove the #country+code row
        
        # Clean numeric columns
        num_cols = ['MPI', 'Headcount Ratio', 'Intensity of Deprivation', 'Vulnerable to Poverty', 'In Severe Poverty']
        for col in num_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # Mapping ISO3 to Country Names
        iso_map = {
            'AFG': 'Afghanistan',
            'BGD': 'Bangladesh',
            'BTN': 'Bhutan',
            'IND': 'India',
            'MDV': 'Maldives',
            'NPL': 'Nepal',
            'PAK': 'Pakistan',
            'LKA': 'Sri Lanka'
        }
        
        df['Country Name'] = df['Country ISO3'].map(iso_map)
        
        # Filter for South Asia
        df = df[df['Country ISO3'].isin(iso_map.keys())]
        
        return df
    except Exception as e:
        print(f"Error loading MPI data: {e}")
        return pd.DataFrame()


@st.cache_data
def load_mpi_trends():
    """Load MPI trends over time"""
    try:
        trends_file = DATA_RAW / "global_mpi_trends.csv"
        if not trends_file.exists():
            return pd.DataFrame()
        df = pd.read_csv(trends_file)
        # Filter for South Asia
        sa_isos = ['AFG', 'BGD', 'BTN', 'IND', 'MDV', 'NPL', 'PAK', 'LKA']
        df = df[df['Country ISO3'].isin(sa_isos)]
        return df
    except Exception as e:
        print(f"Error loading MPI trends: {e}")
        return pd.DataFrame()


@st.cache_data
def load_bulk_wb_data():
    """Load the bulk World Bank indicators dataset"""
    try:
        bulk_file = DATA_RAW / "world_bank_bulk_sa.csv"
        if not bulk_file.exists():
            return pd.DataFrame()
        return pd.read_csv(bulk_file)
    except Exception as e:
        print(f"Error loading Bulk WB data: {e}")
        return pd.DataFrame()


def get_education_stats_for_country(country_name, indicator='SE.PRM.ENRR'):
    """
    Get specific education statistic for a country
    
    Args:
        country_name: Country name (e.g., 'Bangladesh')
        indicator: Series code (default: primary enrollment rate)
    
    Returns: DataFrame with year and value
    """
    df = load_education_data()
    if df.empty:
        return pd.DataFrame()
    
    filtered = df[(df['Country Name'] == country_name) & 
                  (df['Series Code'] == indicator)]
    
    return filtered[['Year', 'Value']].dropna().sort_values('Year')


def get_latest_indicator_value(country_name, data_source='education', indicator=None):
    """
    Get the most recent value for an indicator
    
    Args:
        country_name: Country name
        data_source: 'education', 'jobs', or 'wdi'
        indicator: Specific indicator code
    
    Returns: Latest value or None
    """
    if data_source == 'education':
        df = load_education_data()
    elif data_source == 'jobs':
        df = load_jobs_data()
    elif data_source == 'wdi':
        df = load_wdi_data()
    else:
        return None
    
    if df.empty:
        return None
    
    filtered = df[df['Country Name'] == country_name]
    
    if indicator:
        filtered = filtered[filtered['Series Code'] == indicator]
    
    # Get most recent non-null value
    latest = filtered.dropna(subset=['Value']).sort_values('Year', ascending=False)
    
    if not latest.empty:
        return latest.iloc[0]['Value']
    
    return None


def create_integrated_country_profile(country_name):
    """
    Create a comprehensive country profile using all datasets
    
    Returns: Dictionary with key indicators
    """
    profile = {
        'country': country_name,
        'education': {},
        'employment': {},
        'development': {}
    }
    
    # Education stats
    profile['education']['enrollment_rate'] = get_latest_indicator_value(
        country_name, 'education', 'SE.PRM.ENRR')
    profile['education']['govt_expenditure'] = get_latest_indicator_value(
        country_name, 'education', 'SE.XPD.TOTL.GD.ZS')
    
    # Employment stats
    profile['employment']['electricity_access'] = get_latest_indicator_value(
        country_name, 'jobs', 'EG.ELC.ACCS.ZS')
    
    # Development indicators
    profile['development']['gdp_per_capita'] = get_latest_indicator_value(
        country_name, 'wdi', 'NY.GDP.PCAP.CD')
    
    return profile
