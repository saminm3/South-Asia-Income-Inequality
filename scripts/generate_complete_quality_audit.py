import pandas as pd
from datetime import datetime

# Read cleaned data
data = pd.read_csv('data/processed/all_indicators_cleaned.csv')

# Calculate completeness for each country-indicator pair
target_years = 24  # 2000-2023
quality_records = []

for country in data['country'].unique():
    for indicator in data['indicator'].unique():
        subset = data[(data['country'] == country) & (data['indicator'] == indicator)]
        
        if len(subset) > 0:
            available_years = len(subset)
            completeness = (available_years / target_years) * 100
            
            min_year = subset['year'].min()
            max_year = subset['year'].max()
            year_range = f"{min_year}-{max_year}"
            
            source = subset['source'].iloc[0]
            
            # Determine issues
            if completeness >= 80:
                issues = "Complete or near-complete"
            elif completeness >= 60:
                issues = "Some years missing"
            elif completeness >= 40:
                issues = "Significant data gaps"
            elif completeness >= 20:
                issues = "Major data gaps"
            else:
                issues = "Critically incomplete"
            
            quality_records.append({
                'country': country,
                'indicator': indicator,
                'year_range': year_range,
                'completeness': round(completeness, 1),
                'source': source,
                'issues': issues,
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            })

# Create DataFrame and sort
quality_audit = pd.DataFrame(quality_records)
quality_audit = quality_audit.sort_values(['country', 'indicator'])

# Save
quality_audit.to_csv('data/processed/quality_audit.csv', index=False)

print("Complete quality audit generated:")
print(quality_audit)
print(f"\nTotal audit entries: {len(quality_audit)}")
print(f"Saved to: data/processed/quality_audit.csv")