import pandas as pd
import streamlit as st
import json
from pathlib import Path

# Data directories
DATA_DIR = Path(__file__).parent.parent / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'
GEO_DIR = DATA_DIR / 'geo'

@st.cache_data(ttl=3600)
def load_long():
    """Load the main inequality dataset"""
    try:
        df = pd.read_csv(PROCESSED_DIR / "inequality_long.csv")
        
        # Ensure correct data types
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        
        # Remove rows with missing critical data
        df = df.dropna(subset=['country', 'year', 'indicator', 'value'])
        
        # Clean country codes
        if 'country_code' in df.columns:
            df['country_code'] = df['country_code'].str.upper().str.strip()
        
        return df
        
    except Exception as e:
        st.error(f"Error loading main dataset: {str(e)}")
        return pd.DataFrame()

# Alias
load_inequality_data = load_long

@st.cache_data
def load_geojson():
    """Load GeoJSON file for South Asian countries"""
    try:
        file_path = GEO_DIR / 'sa_countries.geojson'
        
        if not file_path.exists():
            st.warning(f"GeoJSON file not found at {file_path}")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            geojson = json.load(f)
        
        return geojson
    except Exception as e:
        st.warning(f"Error loading GeoJSON: {str(e)}")
        return None

def merge_geo_data(df, geojson):
    """Merge inequality data with geographic boundaries"""
    if geojson is None:
        return df
    
    try:
        geo_codes = []
        for feature in geojson['features']:
            props = feature['properties']
            code = props.get('ISO_A3') or props.get('iso_a3') or props.get('ISO3') or props.get('ADM0_A3')
            if code:
                geo_codes.append(code)
        
        if 'country_code' in df.columns:
            df_merged = df[df['country_code'].isin(geo_codes)].copy()
        else:
            df_merged = df.copy()
        
        return df_merged
    except Exception as e:
        st.warning(f"Error merging geographic data: {str(e)}")
        return df

@st.cache_data
def load_quality_audit():
    """Load data quality audit file"""
    try:
        df = pd.read_csv(PROCESSED_DIR / "quality_audit.csv")
        return df
    except Exception as e:
        st.warning(f"Error loading quality audit: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_all_indicators():
    """Load all indicators cleaned dataset"""
    try:
        df = pd.read_csv(PROCESSED_DIR / "all_indicators_cleaned.csv")
        return df
    except Exception as e:
        st.warning(f"Error loading all indicators: {str(e)}")
        return pd.DataFrame()