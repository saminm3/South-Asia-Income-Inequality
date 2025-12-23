import pandas as pd

df = pd.read_csv("data/processed/south_asia_indicators.csv")

print("Shape:", df.shape)
print("Columns:", df.columns.tolist())
print("\nIndicators:", df["indicator"].nunique())
print("Countries:", df["country"].nunique())
print("Years:", df["year"].min(), "-", df["year"].max())

print("\nSample:")
print(df.head())

print("\nCountry codes:")
print(sorted(df["country_code"].unique()))

print("\nCountries:")
print(sorted(df["country"].unique()))

print("\nCountry count:", df["country_code"].nunique())

print("\nRandom sample:")
print(df.sample(10))
