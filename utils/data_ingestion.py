import pandas as pd
import requests
import os
from pathlib import Path
import time

def fetch_wb_data(indicator_code, country_codes):
    """Fetch data for a specific indicator and list of countries from World Bank API"""
    all_data = []
    for country in country_codes:
        print(f"  📥 Fetching {indicator_code} for {country}...")
        url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator_code}?format=json&per_page=100"
        try:
            response = requests.get(url, timeout=20)
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1 and data[1]:
                    # Extract values
                    for item in data[1]:
                        if item['value'] is not None:
                            all_data.append({
                                'Country': item['country']['value'],
                                'Country Code': item['countryiso3code'],
                                'Indicator Name': item['indicator']['value'],
                                'Indicator Code': item['indicator']['id'],
                                'Year': item['date'],
                                'Value': item['value']
                            })
            time.sleep(0.2) # Be nice to API
        except Exception as e:
            print(f"    ❌ Error: {e}")
    return all_data

def hydrate_datasets():
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # Countries in South Asia
    sa_countries = ['AFG', 'BGD', 'BTN', 'IND', 'MDV', 'NPL', 'PAK', 'LKA']
    
    # Higher-Value Indicators to boost "Data Points"
    indicators = [
        'SI.POV.GINI', 'SI.POV.DDAY', 'NY.GDP.PCAP.PP.CD', 'SL.UEM.TOTL.ZS',
        'SE.ADT.LITR.ZS', 'SH.DYN.MORT', 'IT.NET.USER.ZS', 'EN.ATM.CO2E.PC',
        'SP.POP.TOTL', 'SP.DYN.LE00.IN', 'EG.ELC.ACCS.ZS', 'SE.PRM.ENRR',
        'SL.TLF.CACT.FE.ZS', 'SH.H2O.BASW.ZS', 'BN.CAB.XOKA.GD.ZS'
    ]
    
    print(f"🚀 Starting Deep Hydration for South Asia...")
    bulk_data = []
    for indicator in indicators:
        bulk_data.extend(fetch_wb_data(indicator, sa_countries))
    
    if bulk_data:
        df_bulk = pd.DataFrame(bulk_data)
        target_path = raw_dir / "world_bank_bulk_sa.csv"
        df_bulk.to_csv(target_path, index=False)
        print(f"✅ Deep Hydration Complete! Saved {len(df_bulk)} core data points to {target_path}")
    
    # MPI Trends
    mpi_trends_url = "https://data.humdata.org/dataset/42b16840-3a56-4a20-9314-7aa171f1136c/resource/7c131db3-a172-4280-b37a-85f678192fbe/download/global_mpi_trends.csv"
    print(f"⏳ Downloading Global MPI Trends...")
    try:
        response = requests.get(mpi_trends_url, timeout=30)
        with open(raw_dir / "global_mpi_trends.csv", 'wb') as f:
            f.write(response.content)
        print(f"✅ MPI Trends Hydrated.")
    except Exception as e:
        print(f"❌ MPI Trends Error: {e}")

if __name__ == "__main__":
    hydrate_datasets()
