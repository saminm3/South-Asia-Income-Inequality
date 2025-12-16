
import pandas as pd
import numpy as np

south_asia = {
    'BGD': 'Bangladesh',
    'IND': 'India',
    'PAK': 'Pakistan',
    'NPL': 'Nepal',
    'LKA': 'Sri Lanka',
    
}


all_records = []

# ===== 1. CLEAN GINI DATA (already done, but include for completeness) =====
print("Processing GINI data...")
df_gini = pd.read_csv('data/raw/API_SI.POV.GINI_DS2_en_csv_v2_1210691.csv', skiprows=4)
df_gini_sa = df_gini[df_gini['Country Code'].isin(south_asia.keys())].copy()
year_columns = [col for col in df_gini_sa.columns if col.isdigit()]

for _, row in df_gini_sa.iterrows():
    country_code = row['Country Code']
    country_name = south_asia[country_code]
    for year in year_columns:
        value = row[year]
        if pd.notna(value) and int(year) >= 2000:
            all_records.append({
                'country': country_name,
                'country_code': country_code,
                'year': int(year),
                'indicator': 'GINI',
                'value': value,
                'source': 'World Bank'
            })

# ===== 2. CLEAN GDP DATA =====
print("Processing GDP data...")
df_gdp = pd.read_csv('data/raw/API_NY.GDP.MKTP.CD_DS2_en_csv_v2_1210757.csv', skiprows=4)
df_gdp_sa = df_gdp[df_gdp['Country Code'].isin(south_asia.keys())].copy()

for _, row in df_gdp_sa.iterrows():
    country_code = row['Country Code']
    country_name = south_asia[country_code]
    for year in year_columns:
        value = row[year]
        if pd.notna(value) and int(year) >= 2000:
            all_records.append({
                'country': country_name,
                'country_code': country_code,
                'year': int(year),
                'indicator': 'GDP_Total',
                'value': value,
                'source': 'World Bank'
            })

# ===== 3. CLEAN LABOR FORCE DATA =====
print("Processing Labor Force data...")
df_labor = pd.read_csv('data/raw/API_SL.TLF.TOTL.IN_DS2_en_csv_v2_1192047.csv', skiprows=4)
df_labor_sa = df_labor[df_labor['Country Code'].isin(south_asia.keys())].copy()

for _, row in df_labor_sa.iterrows():
    country_code = row['Country Code']
    country_name = south_asia[country_code]
    for year in year_columns:
        value = row[year]
        if pd.notna(value) and int(year) >= 2000:
            all_records.append({
                'country': country_name,
                'country_code': country_code,
                'year': int(year),
                'indicator': 'Labor_Force_Total',
                'value': value,
                'source': 'World Bank'
            })

# ===== 4. CLEAN HDI DATA =====
# ===== 4. CLEAN HDI DATA =====
# ===== 4. CLEAN HDI DATA =====
print("Processing HDI data...")
try:
    # Load the HDI CSV with correct path and encoding
    df_hdi = pd.read_csv(
        r"C:\Users\MAHIN\Documents\SouthAsia_Inequality\data\raw\UNDP_HDI.csv",
        skiprows=5,  # adjust if your header row is different
        encoding='latin-1'
    )
    
    # Select only the relevant columns: Country and Value
    df_hdi_sa = df_hdi.iloc[:, [1, 2]].copy()  # usually column 1 = Country, column 2 = Value
    df_hdi_sa.columns = ['Country', 'Value']
    
    # List of 5 South Asian countries only
    sa_country_names = ['Bangladesh', 'India', 'Pakistan', 'Nepal', 'Sri Lanka']
    
    # Filter for these countries
    df_hdi_sa = df_hdi_sa[df_hdi_sa['Country'].isin(sa_country_names)].copy()
    
    # Append HDI values to all_records
    for _, row in df_hdi_sa.iterrows():
        country_name = row['Country']
        hdi_value = row['Value']
        if pd.notna(hdi_value):
            all_records.append({
                'country': country_name,
                'country_code': [k for k, v in south_asia.items() if v == country_name][0],
                'year': 2023,  # HDI data year
                'indicator': 'HDI',
                'value': hdi_value,
                'source': 'UNDP'
            })
    
    print(f"HDI records added: {len([r for r in all_records if r['indicator'] == 'HDI'])}")
except Exception as e:
    print(f"Could not process HDI data: {e}")


    
# ===== SAVE COMBINED DATA =====
combined_df = pd.DataFrame(all_records)
combined_df = combined_df.sort_values(['country', 'indicator', 'year'])
combined_df.to_csv('data/processed/all_indicators_cleaned.csv', index=False)

print(f"\nTotal records: {len(combined_df)}")
print("\nRecords by indicator:")
print(combined_df.groupby('indicator').size())
print("\nRecords by country:")
print(combined_df.groupby('country').size())

