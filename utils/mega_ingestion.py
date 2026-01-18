import pandas as pd
import requests
import os
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor

def get_indicator_ids(topic_ids):
    all_ids = []
    for topic in topic_ids:
        url = f"https://api.worldbank.org/v2/topic/{topic}/indicator?format=json&per_page=300"
        try:
            r = requests.get(url, timeout=15)
            data = r.json()
            if len(data) > 1:
                all_ids.extend([item['id'] for item in data[1]])
        except:
            pass
    return list(set(all_ids))[:1000] # Limit to 1000 for extreme scale

def fetch_single_indicator(args):
    indicator_code, country = args
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator_code}?format=json&per_page=100"
    results = []
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1 and data[1]:
                for item in data[1]:
                    if item['value'] is not None:
                        results.append({
                            'Country': item['country']['value'],
                            'Country Code': item['countryiso3code'],
                            'Indicator Name': item['indicator']['value'],
                            'Indicator Code': item['indicator']['id'],
                            'Year': item['date'],
                            'Value': item['value']
                        })
    except:
        pass
    return results

def mega_hydration():
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    sa_countries = ['AFG', 'BGD', 'BTN', 'IND', 'MDV', 'NPL', 'PAK', 'LKA']
    
    print("🔍 Discovering key indicators in Poverty, Education, and Labor...")
    # Topic 11: Poverty, Topic 4: Education, Topic 10: Public Sector, Topic 3: Economy
    indicator_ids = get_indicator_ids([11, 4, 10, 3])
    print(f"📊 Found {len(indicator_ids)} indicators to hydrate across 8 countries...")
    
    tasks = []
    for indicator in indicator_ids:
        for country in sa_countries:
            tasks.append((indicator, country))
    
    bulk_data = []
    print(f"⚡ Starting Parallel Ingestion of {len(tasks)} requests...")
    
    with ThreadPoolExecutor(max_workers=30) as executor: # Even faster
        results = list(executor.map(fetch_single_indicator, tasks))
        for res in results:
            bulk_data.extend(res)
    
    if bulk_data:
        df_bulk = pd.DataFrame(bulk_data)
        target_path = raw_dir / "world_bank_bulk_sa.csv"
        df_bulk.to_csv(target_path, index=False)
        print(f"🔥 MEGA HYDRATION COMPLETE!")
        print(f"📈 Added {len(df_bulk)} total data points across {len(df_bulk['Indicator Code'].unique())} indicators.")
    
    # Also fetch MPI Trends
    mpi_trends_url = "https://data.humdata.org/dataset/42b16840-3a56-4a20-9314-7aa171f1136c/resource/7c131db3-a172-4280-b37a-85f678192fbe/download/global_mpi_trends.csv"
    try:
        r = requests.get(mpi_trends_url)
        with open(raw_dir / "global_mpi_trends.csv", 'wb') as f:
            f.write(r.content)
    except:
        pass

if __name__ == "__main__":
    mega_hydration()
