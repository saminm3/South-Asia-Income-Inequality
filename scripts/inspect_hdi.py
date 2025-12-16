import pandas as pd

# Try different encodings
encodings = ['utf-8', 'latin-1', 'ISO-8859-1', 'cp1252']

for encoding in encodings:
    try:
        print(f"\nTrying encoding: {encoding}")
        df = pd.read_csv('data/raw/HDR25_Statistical_Annex_HDI_Table.csv', encoding=encoding, nrows=10)
        print(f"Success! Columns: {list(df.columns)}")
        print(df.head())
        break
    except Exception as e:
        print(f"Failed: {e}")