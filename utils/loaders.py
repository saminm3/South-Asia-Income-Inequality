import pandas as pd
import streamlit as st
import json
from pathlib import Path

# Data directories
DATA_DIR = Path(__file__).parent.parent / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'
GEO_DIR = DATA_DIR / 'geo'

@st.cache_data(ttl=3600)
def load_inequality_data():
    """Load the main inequality dataset with validation"""
    try:
        df = pd.read_csv(PROCESSED_DIR / "south_asia_indicators.csv")
        
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
        
        # Validate year range
        if df['year'].min() < 1900 or df['year'].max() > 2030:
            st.warning("⚠️ Unusual year values detected in data")
        
        return df
        
    except FileNotFoundError:
        st.error(f"❌ Data file not found: {PROCESSED_DIR / 'inequality_long.csv'}")
        st.info("Please ensure inequality_long.csv exists in data/processed/")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_all_indicators():
    """Load all indicators dataset"""
    try:
        df = pd.read_csv(PROCESSED_DIR / "south_asia_indicators.csv")
        
        # Ensure correct data types
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        
        # Remove invalid rows
        df = df.dropna(subset=['country', 'year', 'indicator', 'value'])
        
        return df
        
    except FileNotFoundError:
        st.warning("All indicators file not found, using main dataset")
        return load_inequality_data()
    except Exception as e:
        st.warning(f"Error loading all indicators: {str(e)}")
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
    
    
    
    
