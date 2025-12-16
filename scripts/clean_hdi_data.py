import pandas as pd

# Read with latin-1 encoding
df = pd.read_csv('data/raw/HDR25_Statistical_Annex_HDI_Table.csv', skiprows=5, encoding='latin-1')

print("First 10 rows:")
print(df.head(10))
print("\nColumn names:")
print(df.columns.tolist())

# South Asian countries to look for
sa_countries = ['Bangladesh', 'India', 'Pakistan', 'Nepal', 'Sri Lanka']

# Filter for South Asian countries - country is usually in second column
country_col = df.columns[1]
df_sa = df[df[country_col].isin(sa_countries)].copy()

print(f"\nFound {len(df_sa)} South Asian countries")
print(df_sa)