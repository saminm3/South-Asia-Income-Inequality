from utils.api_loader import get_api_loader
import pandas as pd
import time

print("Initializing API Loader...")
loader = get_api_loader()

print("Fetching API Summary directly...")
start_time = time.time()
summary = loader.get_api_summary_v2()
end_time = time.time()

print(f"Time taken: {end_time - start_time:.2f} seconds")
print("\n--- API Summary Result ---")
print(f"Total Records: {summary['total_records']}")
print(f"Indicators Found: {summary['indicators']}")
print(f"Source: {summary['source']}")

print("\n--- Testing Individual New Indicator ---")
# Test one of the new indicators to see if it works
test_ind = 'central_govt_debt' # GC.DOD.TOTL.GD.ZS
print(f"Fetching {test_ind}...")
try:
    code = loader.INDICATORS[test_ind]
    df = loader.fetch_indicator(code)
    print(f"Result shape: {df.shape}")
    if not df.empty:
        print(df.head())
    else:
        print("Returned empty DataFrame")
except Exception as e:
    print(f"Error fetching {test_ind}: {e}")
