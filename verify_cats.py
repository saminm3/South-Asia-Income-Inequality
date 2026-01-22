
import sys
import pandas as pd
from pathlib import Path

# Add project root to path
root = Path.cwd()
sys.path.append(str(root))

from utils.indicator_metadata import get_available_indicators_by_category
from utils.loaders import load_inequality_data

print("Loading data...")
df = load_inequality_data()
print(f"Data loaded: {len(df)} rows")

print("Categorizing...")
cats = get_available_indicators_by_category(df)

print("\nAvailable Categories:")
for c in cats.keys():
    print(f"- {c}")
    for ind in cats[c]['indicators']:
        print(f"  * {ind}")
