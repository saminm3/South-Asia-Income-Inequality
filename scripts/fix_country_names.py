import pandas as pd

IN_PATH  = "data/processed/south_asia_indicators_clean.csv"
OUT_PATH = "data/processed/south_asia_indicators_clean.csv"  # overwrite same file

df = pd.read_csv(IN_PATH)

# --- Fix Pakistan issues ---
df.loc[df["country"].astype(str).str.strip().eq("PAK"), "country"] = "Pakistan"
df.loc[df["country"].astype(str).str.strip().eq("Pakistan"), "country_code"] = "PAK"

# Remove invalid country codes (also removes 'NAN')
valid_codes = {"AFG", "BGD", "BTN", "IND", "LKA", "MDV", "NPL", "PAK"}
df = df[df["country_code"].astype(str).str.strip().isin(valid_codes)].copy()

# Clean whitespace
df["country"] = df["country"].astype(str).str.strip()
df["country_code"] = df["country_code"].astype(str).str.strip()

# Save
df.to_csv(OUT_PATH, index=False)

print("✅ Saved:", OUT_PATH)
print("Countries:", sorted(df["country"].unique()))
print("Country codes:", sorted(df["country_code"].unique()))
print("Country count:", df["country_code"].nunique())
