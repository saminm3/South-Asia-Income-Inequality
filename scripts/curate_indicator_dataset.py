
import pandas as pd
import os

def curate():
    # Paths
    WID_CLEANED = 'data/cleaned/cleaned_wid_v2.csv'
    WB_CLEANED = 'data/cleaned/cleaned_world_development_indicators.csv'
    JOBS_CLEANED = 'data/cleaned/cleaned_jobs_data.csv'
    EDU_CLEANED = 'data/cleaned/cleaned_education_statistics.csv'
    MAIN_DATA = 'data/processed/south_asia_indicators.csv'
    OUTPUT = 'data/processed/curated_indicators.csv'
    
    print("Starting data curation...")
    
    curated_parts = []
    
    # SA countries to filter for
    sa_countries = ['Afghanistan', 'Bangladesh', 'Bhutan', 'India', 'Maldives', 'Nepal', 'Pakistan', 'Sri Lanka']

    # 1. Load Main Data (as base) - This often contains the merged Gini and basic GDP
    if os.path.exists(MAIN_DATA):
        print(f"Loading main data from {MAIN_DATA}...")
        df_main = pd.read_csv(MAIN_DATA)
        
        # Mapping for core inequality/income indicators specifically requested by user
        main_mapping = {
            'Gini index': 'GINI Coefficient',
            'Income Inequality (Gini)': 'GINI Coefficient',
            'Top 10% share (Income)': 'Top 10% Income Share',
            'Top 1% share (Income)': 'Top 1% Income Share',
            'Bottom 50% share (Income)': 'Bottom 50% Income Share',
            'Average Income - Post-tax national income average': 'Mean Income',
            'GDP per capita (current US$)': 'GDP Per Capita',
            'gdp_per_capita': 'GDP Per Capita'
        }
        
        df_found = df_main[df_main['indicator'].isin(main_mapping.keys())].copy()
        df_found['indicator'] = df_found['indicator'].map(main_mapping)
        curated_parts.append(df_found)
    
    # 2. Extract specific WID indicators (Shares + Median) 
    # (User asked to curate WID because it's "huge", so we only take these)
    if os.path.exists(WID_CLEANED):
        print(f"Extracting curated WID metrics from {WID_CLEANED}...")
        df_wid = pd.read_csv(WID_CLEANED)
        
        # Middle 40% (p50p90 share)
        m40 = df_wid[(df_wid['Percentile'] == 'p50p90') & (df_wid['Indicator_Category'] == 'Income Inequality')].copy()
        if not m40.empty:
            m40 = m40[['Country', 'Country_Code', 'Year', 'Value']]
            m40.columns = ['country', 'country_code', 'year', 'value']
            m40['indicator'] = 'Middle 40% Income Share'
            m40['source'] = 'World Inequality Database'
            curated_parts.append(m40)
            
        # Median Income (p50p51 average income)
        median = df_wid[(df_wid['Percentile'] == 'p50p51') & (df_wid['Indicator_Category'] == 'Average Income')].copy()
        if not median.empty:
            median = median[['Country', 'Country_Code', 'Year', 'Value']]
            median.columns = ['country', 'country_code', 'year', 'value']
            median['indicator'] = 'Median Income'
            median['source'] = 'World Inequality Database'
            curated_parts.append(median)

    # 3. Bring back ALL indicators from Education, Jobs, and WDI datasets (within years 2000-2024)
    # This addresses the user's request for more data points.
    other_datasets = {
        'Education': EDU_CLEANED,
        'Jobs/Development': JOBS_CLEANED,
        'World Bank Indicators': WB_CLEANED
    }
    
    for name, path in other_datasets.items():
        if os.path.exists(path):
            print(f"Bringing back ALL indicators from {name} ({path})...")
            # Files have slightly different formats, let's try to detect columns
            df_temp = pd.read_csv(path)
            
            # Standardize columns to [country, country_code, year, indicator, value]
            cols = df_temp.columns.tolist()
            # Try to identify columns by index/name patterns
            country_col = next((c for c in cols if 'country' in c.lower()), cols[0])
            code_col = next((c for c in cols if 'code' in c.lower()), cols[1])
            year_col = next((c for c in cols if 'year' in c.lower()), cols[2])
            val_col = next((c for c in cols if 'value' in c.lower()), cols[-1])
            
            # For indicator name, look for 'indicator', 'series', or 'name'
            ind_col = next((c for c in cols if any(x in c.lower() for x in ['indicator', 'series', 'name'])), cols[3])
            
            subset = df_temp[[country_col, code_col, year_col, ind_col, val_col]].copy()
            subset.columns = ['country', 'country_code', 'year', 'indicator', 'value']
            subset['source'] = name
            curated_parts.append(subset)
            
    # 4. Final Merge & Filter
    if curated_parts:
        df_final = pd.concat(curated_parts, ignore_index=True)
        
        # Clean up
        df_final = df_final.dropna(subset=['value'])
        # Filter for year range 2000-2024
        df_final['year'] = pd.to_numeric(df_final['year'], errors='coerce')
        df_final = df_final[(df_final['year'] >= 2000) & (df_final['year'] <= 2024)]
        
        # Standardize country names to match SA list
        df_final = df_final[df_final['country'].isin(sa_countries)]
        
        # Remove duplicates
        df_final = df_final.drop_duplicates(subset=['country', 'year', 'indicator'], keep='first')
        
        # Sort
        df_final = df_final.sort_values(['country', 'indicator', 'year'])
        
        df_final.to_csv(OUTPUT, index=False)
        print(f"\nSUCCESS: Curated dataset saved to {OUTPUT}")
        print(f"Total records: {len(df_final)}")
        print(f"Total indicators: {df_final['indicator'].nunique()}")
    else:
        print("ERROR: No data found to curate.")

if __name__ == "__main__":
    curate()
