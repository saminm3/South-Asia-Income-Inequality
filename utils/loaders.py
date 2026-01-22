import pandas as pd
import streamlit as st
import json
from pathlib import Path

# Data directories
DATA_DIR = Path(__file__).parent.parent / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'
GEO_DIR = DATA_DIR / 'geo'

# Removed cache to force data reload
def load_inequality_data():
    """Load the curated inequality dataset (12 focused indicators)"""
    try:
        # Load curated data (contains only the 12 indicators requested by user)
        csv_path = PROCESSED_DIR / "curated_indicators.csv"
        
        if not csv_path.exists():
            st.error(f"❌ Curated data file not found: {csv_path}")
            st.info("Please run the curation script: scripts/curate_indicator_dataset.py")
            return pd.DataFrame()
        
        df = pd.read_csv(csv_path)
        
        # Validate required columns
        required_cols = ['country', 'year', 'indicator', 'value']
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            st.error(f"Missing required columns: {missing_cols}")
            return pd.DataFrame()
        
        # Ensure correct data types
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        
        # Remove rows with missing critical data
        df = df.dropna(subset=['country', 'year', 'indicator', 'value'])
        
        # Clean country codes if they exist
        if 'country_code' in df.columns:
            df['country_code'] = df['country_code'].str.upper().str.strip()
            
        # Filter for year range 2000-2024
        df = df[(df['year'] >= 2000) & (df['year'] <= 2024)]
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error loading curated data: {str(e)}")
        return pd.DataFrame()


# Removed cache for data sync
def load_all_indicators():
    """Load all indicators (redirected to curated set for consistency)"""
    return load_inequality_data()

@st.cache_data(ttl=3600)
def load_quality_audit():
    """Load data quality audit"""
    try:
        df = pd.read_csv(PROCESSED_DIR / "quality_audit.csv")
        return df
    except FileNotFoundError:
        st.warning("Quality audit file not found")
        return pd.DataFrame()
    except Exception as e:
        st.warning(f"Error loading quality audit: {str(e)}")
        return pd.DataFrame()

@st.cache_resource
def load_geojson():
    """Load GeoJSON file for South Asian countries"""
    try:
        file_path = GEO_DIR / 'sa_countries.geojson'
        
        if not file_path.exists():
            st.error(f"❌ GeoJSON file not found at {file_path}")
            st.info("Please ensure sa_countries.geojson exists in data/geo/")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            geojson = json.load(f)
        
        # Validate GeoJSON structure
        if 'features' not in geojson:
            st.error("Invalid GeoJSON format: missing 'features'")
            return None
        
        return geojson
        
    except json.JSONDecodeError:
        st.error("❌ Invalid JSON in GeoJSON file")
        return None
    except Exception as e:
        st.error(f"❌ Error loading GeoJSON: {str(e)}")
        return None

def merge_geo_data(df, geojson):
    """Merge inequality data with geographic boundaries"""
    if geojson is None:
        return df
    
    try:
        # Extract country codes from GeoJSON
        geo_codes = []
        for feature in geojson['features']:
            props = feature['properties']
            code = props.get('ISO_A3') or props.get('iso_a3') or props.get('ISO3') or props.get('ADM0_A3')
            if code:
                geo_codes.append(code)
        
        # Filter data to only include countries in the GeoJSON
        if 'country_code' in df.columns:
            df_merged = df[df['country_code'].isin(geo_codes)].copy()
        else:
            df_merged = df.copy()
        
        return df_merged
        
    except Exception as e:
        st.warning(f"Error merging geographic data: {str(e)}")
        return df
    
    
    
    
