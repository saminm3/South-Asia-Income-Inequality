"""
Data Cleaning Pipeline for South Asia Income Inequality Project
This script cleans and processes raw datasets from World Bank and WID
Focus: South Asian countries, Years 2000-2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# South Asian countries mapping
SOUTH_ASIA_COUNTRIES = {
    'BGD': 'Bangladesh',
    'IND': 'India',
    'PAK': 'Pakistan',
    'NPL': 'Nepal',
    'LKA': 'Sri Lanka',
    'AFG': 'Afghanistan',
    'BTN': 'Bhutan',
    'MDV': 'Maldives'
}

# Year range
START_YEAR = 2000
END_YEAR = 2025

class DataCleaner:
    def __init__(self, raw_data_dir, output_dir):
        self.raw_data_dir = Path(raw_data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def clean_world_bank_format(self, file_path, dataset_name):
        """Clean World Bank format datasets (year columns format)"""
        print(f"\n{'='*60}")
        print(f"Cleaning {dataset_name}...")
        print(f"{'='*60}")
        
        try:
            # Read the CSV
            df = pd.read_csv(file_path)
            print(f"Original shape: {df.shape}")
            
            # Filter for South Asian countries only
            df = df[df['Country Code'].isin(SOUTH_ASIA_COUNTRIES.keys())]
            print(f"After filtering South Asian countries: {df.shape}")
            
            if df.empty:
                print("⚠️ No South Asian countries found in this dataset")
                return None
            
            # Identify year columns
            year_cols = [col for col in df.columns if col.startswith(('19', '20')) or '[YR' in col]
            
            if not year_cols:
                print("⚠️ No year columns found")
                return None
            
            # Extract year from column names (handle both '2000' and '2000 [YR2000]' formats)
            year_mapping = {}
            for col in year_cols:
                # Extract year number
                if '[YR' in col:
                    year = int(col.split('[YR')[1].split(']')[0])
                else:
                    year = int(col.split()[0]) if ' ' in col else int(col)
                
                if START_YEAR <= year <= END_YEAR:
                    year_mapping[col] = year
            
            if not year_mapping:
                print(f"⚠️ No years between {START_YEAR}-{END_YEAR} found")
                return None
            
            # Select relevant columns (handle both 'Series' and 'Series Name')
            series_col = 'Series Name' if 'Series Name' in df.columns else 'Series'
            meta_cols = ['Country Name', 'Country Code', series_col, 'Series Code']
            selected_cols = meta_cols + list(year_mapping.keys())
            df = df[selected_cols]
            
            # Rename to standardize
            if series_col != 'Series Name':
                df = df.rename(columns={series_col: 'Series Name'})
                meta_cols = ['Country Name', 'Country Code', 'Series Name', 'Series Code']
            
            # Melt the dataframe to long format
            df_melted = df.melt(
                id_vars=meta_cols,
                value_vars=list(year_mapping.keys()),
                var_name='Year_Column',
                value_name='Value'
            )
            
            # Map year column to actual year
            df_melted['Year'] = df_melted['Year_Column'].map(year_mapping)
            df_melted = df_melted.drop('Year_Column', axis=1)
            
            # Clean the values
            df_melted['Value'] = pd.to_numeric(df_melted['Value'], errors='coerce')
            
            # Remove rows with missing values
            initial_rows = len(df_melted)
            df_melted = df_melted.dropna(subset=['Value'])
            print(f"Removed {initial_rows - len(df_melted)} rows with missing values")
            
            # Map country codes to names
            df_melted['Country'] = df_melted['Country Code'].map(SOUTH_ASIA_COUNTRIES)
            
            # Reorder columns
            df_melted = df_melted[['Country', 'Country Code', 'Year', 'Series Name', 'Series Code', 'Value']]
            
            # Sort
            df_melted = df_melted.sort_values(['Country', 'Series Name', 'Year']).reset_index(drop=True)
            
            print(f"Final shape: {df_melted.shape}")
            print(f"Year range: {df_melted['Year'].min()} - {df_melted['Year'].max()}")
            print(f"Countries: {df_melted['Country'].unique().tolist()}")
            print(f"Indicators: {df_melted['Series Name'].nunique()}")
            
            # Save cleaned data
            output_file = self.output_dir / f"cleaned_{dataset_name}.csv"
            df_melted.to_csv(output_file, index=False)
            print(f"✅ Saved to: {output_file}")
            
            # Save metadata (indicator list)
            indicators = df_melted[['Series Name', 'Series Code']].drop_duplicates()
            indicators_file = self.output_dir / f"indicators_{dataset_name}.csv"
            indicators.to_csv(indicators_file, index=False)
            print(f"✅ Saved indicators list to: {indicators_file}")
            
            return df_melted
            
        except Exception as e:
            print(f"❌ Error cleaning {dataset_name}: {str(e)}")
            return None
    
    def clean_wid_data(self, file_path):
        """Clean World Inequality Database format"""
        print(f"\n{'='*60}")
        print(f"Cleaning WID Data...")
        print(f"{'='*60}")
        
        try:
            # Read WID data (skip first row which is metadata)
            df = pd.read_csv(file_path, skiprows=1, sep=';')
            print(f"Original shape: {df.shape}")
            
            # Clean column names - remove leading/trailing spaces
            df.columns = df.columns.str.strip()
            
            # The first two columns are Percentile and Year
            percentile_col = df.columns[0]
            year_col = df.columns[1]
            
            # Rename for clarity
            df = df.rename(columns={percentile_col: 'Percentile', year_col: 'Year'})
            
            # Extract country information from column headers
            country_cols = []
            for col in df.columns[2:]:  # Skip Percentile and Year
                if any(code in col for code in ['_AF', '_BD', '_IN', '_PK', '_NP', '_LK']):
                    country_cols.append(col)
            
            if not country_cols:
                print("⚠️ No South Asian country data found in WID dataset")
                return None
            
            # Select only relevant columns
            df = df[['Percentile', 'Year'] + country_cols]
            
            # Convert Year to numeric and filter for our time range
            df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
            df = df[(df['Year'] >= START_YEAR) & (df['Year'] <= END_YEAR)]
            
            # Melt the dataframe
            df_melted = df.melt(
                id_vars=['Percentile', 'Year'],
                value_vars=country_cols,
                var_name='Indicator_Country',
                value_name='Value'
            )
            
            # Extract country code and indicator info from column name
            country_mapping = {
                'AF': 'Afghanistan',
                'BD': 'Bangladesh',
                'IN': 'India',
                'PK': 'Pakistan',
                'NP': 'Nepal',
                'LK': 'Sri Lanka'
            }
            
            def extract_country(col_name):
                for code, name in country_mapping.items():
                    if f'_{code}' in col_name:
                        return name, code
                return None, None
            
            df_melted[['Country', 'Country_Code']] = df_melted['Indicator_Country'].apply(
                lambda x: pd.Series(extract_country(x))
            )
            
            # Extract indicator name (before country code)
            df_melted['Indicator'] = df_melted['Indicator_Country'].str.split('_').str[0]
            
            # Clean up
            df_melted = df_melted.drop('Indicator_Country', axis=1)
            df_melted['Value'] = pd.to_numeric(df_melted['Value'], errors='coerce')
            df_melted = df_melted.dropna(subset=['Value', 'Country'])
            
            # Reorder columns
            df_melted = df_melted[['Country', 'Country_Code', 'Year', 'Percentile', 'Indicator', 'Value']]
            df_melted = df_melted.sort_values(['Country', 'Year', 'Percentile']).reset_index(drop=True)
            
            print(f"Final shape: {df_melted.shape}")
            print(f"Year range: {df_melted['Year'].min():.0f} - {df_melted['Year'].max():.0f}")
            print(f"Countries: {df_melted['Country'].unique().tolist()}")
            
            # Save cleaned data
            output_file = self.output_dir / "cleaned_wid_inequality_data.csv"
            df_melted.to_csv(output_file, index=False)
            print(f"✅ Saved to: {output_file}")
            
            return df_melted
            
        except Exception as e:
            print(f"❌ Error cleaning WID data: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_summary_report(self):
        """Generate a summary report of all cleaned datasets"""
        print(f"\n{'='*60}")
        print("GENERATING SUMMARY REPORT")
        print(f"{'='*60}")
        
        summary_data = []
        
        for file in self.output_dir.glob("cleaned_*.csv"):
            try:
                df = pd.read_csv(file)
                summary_data.append({
                    'Dataset': file.stem.replace('cleaned_', ''),
                    'Total Records': len(df),
                    'Countries': df['Country'].nunique() if 'Country' in df.columns else 0,
                    'Indicators': df['Series Name'].nunique() if 'Series Name' in df.columns else 0,
                    'Year Range': f"{df['Year'].min()}-{df['Year'].max()}" if 'Year' in df.columns else 'N/A',
                    'File Size (KB)': f"{file.stat().st_size / 1024:.1f}"
                })
            except Exception as e:
                print(f"⚠️ Could not process {file.name}: {str(e)}")
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            summary_file = self.output_dir / "cleaning_summary_report.csv"
            summary_df.to_csv(summary_file, index=False)
            print("\n" + summary_df.to_string(index=False))
            print(f"\n✅ Summary report saved to: {summary_file}")
        
    def run_full_pipeline(self):
        """Run the complete data cleaning pipeline"""
        print("\n" + "="*80)
        print("SOUTH ASIA INCOME INEQUALITY - DATA CLEANING PIPELINE")
        print("="*80)
        print(f"Target Year Range: {START_YEAR} - {END_YEAR}")
        print(f"Target Countries: {', '.join(SOUTH_ASIA_COUNTRIES.values())}")
        print("="*80)
        
        # 1. Clean Education Statistics
        education_file = self.raw_data_dir / "P_Data_Extract_From_Education_Statistics_-_All_Indicators" / "31eb65da-cd5b-4684-ae89-dc70eb60007f_Data.csv"
        if education_file.exists():
            self.clean_world_bank_format(education_file, "education_statistics")
        
        # 2. Clean Jobs Data
        jobs_file = self.raw_data_dir / "P_Data_Extract_From_Jobs" / "50b84243-4489-4d54-8c8e-719385d0e88e_Data.csv"
        if jobs_file.exists():
            self.clean_world_bank_format(jobs_file, "jobs_data")
        
        # 3. Clean World Development Indicators
        wdi_file = self.raw_data_dir / "P_Data_Extract_From_World_Development_Indicators" / "d05a5752-a39e-4091-82ba-be7ef61e6e9c_Data.csv"
        if wdi_file.exists():
            self.clean_world_bank_format(wdi_file, "world_development_indicators")
        
        # 4. Clean WID Data
        wid_file = self.raw_data_dir / "WID_Data_Metadata" / "WID_Data_31122025-094739.csv"
        if wid_file.exists():
            self.clean_wid_data(wid_file)
        
        # 5. Generate summary report
        self.generate_summary_report()
        
        print("\n" + "="*80)
        print("✅ DATA CLEANING PIPELINE COMPLETED!")
        print("="*80)
        print(f"\nCleaned data saved to: {self.output_dir.absolute()}")
        print("\nNext steps:")
        print("1. Review the cleaned datasets in the 'data/cleaned/' directory")
        print("2. Check 'cleaning_summary_report.csv' for overview")
        print("3. Review indicator lists to see available metrics")
        print("4. Integrate cleaned data into your Streamlit dashboards")


if __name__ == "__main__":
    # Setup paths
    raw_data_dir = "/Users/shaierasultanaoishe/Downloads/raw"
    output_dir = "/Users/shaierasultanaoishe/Desktop/South-Asia-Income-Inequality/data/cleaned"
    
    # Run pipeline
    cleaner = DataCleaner(raw_data_dir, output_dir)
    cleaner.run_full_pipeline()
