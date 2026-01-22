import pandas as pd

df = pd.read_csv('data/processed/inequality_long.csv')
print(f'Total rows: {len(df)}')
print(f'Unique indicators: {df["indicator"].nunique()}')
print('\nIndicators:')
for ind in sorted(df['indicator'].unique()):
    print(f'  - {ind}')
