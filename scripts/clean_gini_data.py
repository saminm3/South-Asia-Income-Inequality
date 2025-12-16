import pandas as pd

# Read the World Bank GINI data (skip first 4 rows which are metadata)
df = pd.read_csv('data/raw/API_SI.POV.GINI_DS2_en_csv_v2_1210691.csv', skiprows=4)

# South Asian countries and their codes
south_asia = {
    'BGD': 'Bangladesh',
    'IND': 'India',
    'PAK': 'Pakistan',
    'NPL': 'Nepal',
    'LKA': 'Sri Lanka'
}

# Filter for South Asian countries only
df_sa = df[df['Country Code'].isin(south_asia.keys())].copy()

# Get year columns (they're named '1960', '1961', '2000', etc.)
year_columns = [col for col in df_sa.columns if col.isdigit()]

# Reshape from wide to long format
records = []
for _, row in df_sa.iterrows():
    country_code = row['Country Code']
    country_name = south_asia[country_code]
    
    for year in year_columns:
        value = row[year]
        if pd.notna(value):  # Only include if data exists (not NaN)
            records.append({
                'country': country_name,
                'country_code': country_code,
                'year': int(year),
                'indicator': 'GINI',
                'value': value,
                'source': 'World Bank'
            })

# Create DataFrame
gini_long = pd.DataFrame(records)

# Filter for years 2000 onwards only
gini_long = gini_long[gini_long['year'] >= 2000]

# Sort by country and year
gini_long = gini_long.sort_values(['country', 'year'])

# Save cleaned data
gini_long.to_csv('data/processed/gini_cleaned.csv', index=False)

print(f"Cleaned GINI data saved to data/processed/gini_cleaned.csv")
print(f"Total records: {len(gini_long)}\n")

print("Data coverage by country (2000-2023):")
print(gini_long.groupby('country')['year'].agg(['min', 'max', 'count']))