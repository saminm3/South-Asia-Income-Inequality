"""
Process New WID Data for South Asian Countries

This script consolidates WID (World Inequality Database) data from individual
country files into a unified dataset for South Asian countries.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WIDDataProcessor:
    """Process and consolidate WID data for South Asian countries."""
    
    def __init__(self, wid_data_dir, output_dir):
        """
        Initialize the processor.
        
        Args:
            wid_data_dir: Path to directory containing WID data files
            output_dir: Path to directory where processed data will be saved
        """
        self.wid_data_dir = Path(wid_data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # South Asian countries and their codes
        self.south_asian_countries = {
            'AF': 'Afghanistan',
            'BD': 'Bangladesh',
            'BT': 'Bhutan',
            'IN': 'India',
            'MV': 'Maldives',
            'NP': 'Nepal',
            'PK': 'Pakistan',
            'LK': 'Sri Lanka'
        }
        
        # Key inequality indicators to extract
        # Format: variable_prefix: (description, category)
        self.key_indicators = {
            # Income - Pre-tax
            'sptinc': ('Pre-tax national income share', 'Income Inequality'),
            'aptinc': ('Pre-tax national income average', 'Average Income'),
            'gptinc': ('Pre-tax national income Gini', 'Income Inequality'),
            
            # Income - Post-tax
            'sdiinc': ('Post-tax disposable income share', 'Income Inequality'),
            'adiinc': ('Post-tax national income average', 'Average Income'),
            'gdiinc': ('Post-tax disposable income Gini', 'Income Inequality'),
            
            # Wealth
            'shweal': ('Net personal wealth share', 'Wealth Inequality'),
            'ahweal': ('Net personal wealth average', 'Average Wealth'),
            'ghweal': ('Net personal wealth Gini', 'Wealth Inequality'),
            
            # Carbon
            'scarb': ('Carbon emissions share', 'Carbon Inequality'),
            'acarb': ('Carbon emissions average', 'Carbon Inequality'),
            'enfghg': ('National carbon footprint', 'Carbon Inequality'), # National level
            
            # Gender
            'fmlinc': ('Female labor income share', 'Gender Inequality'),
            
            # National Accounts Aggregates
            'anninc': ('National income', 'Average Income'),
            'nngdp': ('GDP', 'Average Income'),
        }
        
    def load_country_mapping(self):
        """Load the WID countries mapping file."""
        countries_file = self.wid_data_dir / 'WID_countries.csv'
        logger.info(f"Loading country mapping from {countries_file}")
        
        df = pd.read_csv(countries_file, sep=';')
        return df
    
    def load_country_metadata(self, country_code):
        """
        Load metadata for a specific country.
        
        Args:
            country_code: Two-letter country code (e.g., 'BD')
            
        Returns:
            DataFrame with metadata or None if file doesn't exist
        """
        metadata_file = self.wid_data_dir / f'WID_metadata_{country_code}.csv'
        
        if not metadata_file.exists():
            logger.warning(f"Metadata file not found: {metadata_file}")
            return None
        
        try:
            df = pd.read_csv(metadata_file, sep=';', low_memory=False)
            logger.info(f"Loaded metadata for {country_code}: {len(df)} variables")
            return df
        except Exception as e:
            logger.error(f"Error loading metadata for {country_code}: {e}")
            return None
    
    def load_country_data(self, country_code):
        """
        Load WID data for a specific country.
        
        Args:
            country_code: Two-letter country code (e.g., 'BD')
            
        Returns:
            DataFrame with country data or None if file doesn't exist
        """
        data_file = self.wid_data_dir / f'WID_data_{country_code}.csv'
        
        if not data_file.exists():
            logger.warning(f"Data file not found: {data_file}")
            return None
        
        try:
            df = pd.read_csv(data_file, sep=';', low_memory=False)
            logger.info(f"Loaded data for {country_code}: {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Error loading data for {country_code}: {e}")
            return None
    
    def extract_indicator_type(self, variable_code):
        """
        Extract the indicator type from a variable code.
        
        Args:
            variable_code: WID variable code (e.g., 'sptincj992')
            
        Returns:
            Tuple of (indicator_type, description) or (None, None)
        """
        for prefix, (description, category) in self.key_indicators.items():
            if variable_code.startswith(prefix):
                return category, description
        return None, None
    
    def process_country(self, country_code, country_name):
        """
        Process data for a single country.
        
        Args:
            country_code: Two-letter country code
            country_name: Full country name
            
        Returns:
            DataFrame with processed data or None
        """
        logger.info(f"Processing {country_name} ({country_code})")
        
        # Load country data
        data = self.load_country_data(country_code)
        if data is None:
            return None
        
        # Load metadata for indicator descriptions
        metadata = self.load_country_metadata(country_code)
        
        # Filter for key inequality indicators
        indicator_prefixes = list(self.key_indicators.keys())
        pattern = '|'.join([f'^{prefix}' for prefix in indicator_prefixes])
        
        filtered_data = data[data['variable'].str.match(pattern, na=False)].copy()
        logger.info(f"Filtered to {len(filtered_data)} rows for key indicators")
        
        if len(filtered_data) == 0:
            logger.warning(f"No inequality indicators found for {country_name}")
            return None
        
        # Add country information
        filtered_data['Country'] = country_name
        filtered_data['Country_Code'] = country_code
        
        # Extract indicator category and description
        filtered_data['Indicator_Category'], filtered_data['Indicator_Description'] = zip(
            *filtered_data['variable'].apply(self.extract_indicator_type)
        )
        
        # Add detailed description from metadata if available
        if metadata is not None:
            # Create a mapping of variable to shortname
            metadata_map = metadata.set_index('variable')['shortname'].to_dict()
            filtered_data['Indicator_Full_Name'] = filtered_data['variable'].map(metadata_map)
        else:
            filtered_data['Indicator_Full_Name'] = filtered_data['Indicator_Description']
        
        # Rename columns to match target schema
        filtered_data = filtered_data.rename(columns={
            'year': 'Year',
            'percentile': 'Percentile',
            'value': 'Value',
            'variable': 'Variable_Code'
        })
        
        # Select and order columns
        columns = [
            'Country', 'Country_Code', 'Year', 'Variable_Code',
            'Indicator_Category', 'Indicator_Description', 'Indicator_Full_Name',
            'Percentile', 'Value', 'age', 'pop'
        ]
        
        return filtered_data[columns]
    
    def process_all_countries(self):
        """
        Process data for all South Asian countries.
        
        Returns:
            Consolidated DataFrame
        """
        all_data = []
        
        for country_code, country_name in self.south_asian_countries.items():
            country_data = self.process_country(country_code, country_name)
            
            if country_data is not None:
                all_data.append(country_data)
        
        if not all_data:
            logger.error("No data was processed for any country!")
            return None
        
        # Concatenate all country data
        consolidated = pd.concat(all_data, ignore_index=True)
        logger.info(f"Consolidated data: {len(consolidated)} total rows")
        
        return consolidated
    
    def save_processed_data(self, data, filename='cleaned_wid_v2.csv'):
        """
        Save the processed data to CSV.
        
        Args:
            data: DataFrame to save
            filename: Output filename
        """
        output_path = self.output_dir / filename
        data.to_csv(output_path, index=False)
        logger.info(f"Saved processed data to {output_path}")
        
        # Print summary statistics
        logger.info("\n" + "="*60)
        logger.info("PROCESSING SUMMARY")
        logger.info("="*60)
        logger.info(f"Total rows: {len(data):,}")
        logger.info(f"Countries: {data['Country'].nunique()}")
        logger.info(f"Year range: {data['Year'].min():.0f} - {data['Year'].max():.0f}")
        logger.info(f"Indicators: {data['Variable_Code'].nunique()}")
        logger.info("\nCountry breakdown:")
        for country, count in data['Country'].value_counts().items():
            logger.info(f"  {country}: {count:,} rows")
        logger.info("\nIndicator category breakdown:")
        for category, count in data['Indicator_Category'].value_counts().items():
            logger.info(f"  {category}: {count:,} rows")
        logger.info("="*60)
    
    def run(self):
        """Run the full processing pipeline."""
        logger.info("Starting WID data processing")
        logger.info(f"Data directory: {self.wid_data_dir}")
        logger.info(f"Output directory: {self.output_dir}")
        
        # Process all countries
        consolidated_data = self.process_all_countries()
        
        if consolidated_data is None:
            logger.error("Processing failed - no data generated")
            return False
        
        # Save the processed data
        self.save_processed_data(consolidated_data)
        
        logger.info("WID data processing completed successfully!")
        return True


def main():
    """Main entry point for the script."""
    # Set paths
    wid_data_dir = '/Users/shaierasultanaoishe/Documents/wid_all_data'
    output_dir = '/Users/shaierasultanaoishe/Documents/South-Asia-Income-Inequality/data/cleaned'
    
    # Create processor and run
    processor = WIDDataProcessor(wid_data_dir, output_dir)
    success = processor.run()
    
    if success:
        logger.info("✓ Processing completed successfully")
    else:
        logger.error("✗ Processing failed")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
