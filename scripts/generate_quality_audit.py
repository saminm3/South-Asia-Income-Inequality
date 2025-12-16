import pandas as pd
from datetime import datetime

# Read the cleaned GINI data
gini_data = pd.read_csv('data/processed/gini_cleaned.csv')

# Calculate completeness for each country
target_years = 24  # 2000-2023
quality_records = []

for country in gini_data['country'].unique():
    country_data = gini_data[gini_data['country'] == country]
    
    available_years = len(country_data)
    completeness = (available_years / target_years) * 100
    
    # Get year range
    min_year = country_data['year'].min()
    max_year = country_data['year'].max()
    year_range = f"{min_year}-{max_year}"
    
    # Determine issues based on completeness
    if completeness >= 80:
        issues = "Complete or near-complete"
    elif completeness >= 60:
        issues = "Some years missing"
    elif completeness >= 40:
        issues = "Significant data gaps"
    elif completeness >= 20:
        issues = "Major data gaps, sporadic collection"
    else:
        issues = "Critically incomplete, very limited data"
    
    quality_records.append({
        'country': country,
        'indicator': 'GINI',
        'year_range': year_range,
        'completeness': round(completeness, 1),
        'source': 'World Bank',
        'issues': issues,
        'last_updated': datetime.now().strftime('%Y-%m-%d')
    })

# Create DataFrame
quality_audit = pd.DataFrame(quality_records)

# Save
quality_audit.to_csv('data/processed/quality_audit.csv', index=False)

print("Real quality audit generated from actual GINI data:")
print(quality_audit)
print(f"\nSaved to: data/processed/quality_audit.csv")