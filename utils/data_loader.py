"""
Data Loader for Cleaned South Asia Income Inequality Datasets
Provides easy-to-use functions to load and filter cleaned data
"""

import pandas as pd
from pathlib import Path
from functools import lru_cache


class SouthAsiaDataLoader:
    """
    Centralized data loader for all cleaned South Asian datasets
    """
    
    def __init__(self, data_dir=None):
        if data_dir is None:
            # Default to the cleaned data directory
            self.data_dir = Path(__file__).parent.parent / "data" / "cleaned"
        else:
            self.data_dir = Path(data_dir)
        
        # Available datasets
        self.datasets = {
            'education': 'cleaned_education_statistics.csv',
            'jobs': 'cleaned_jobs_data.csv',
            'wdi': 'cleaned_world_development_indicators.csv',
            'inequality': 'cleaned_wid_inequality_data.csv'
        }
    
    @lru_cache(maxsize=10)
    def load_education_data(self, country=None, year_range=None):
        """
        Load education statistics
        
        Parameters:
        -----------
        country : str or list, optional
            Filter by country name(s)
        year_range : tuple, optional
            (start_year, end_year) to filter data
        
        Returns:
        --------
        pd.DataFrame
        """
        file_path = self.data_dir / self.datasets['education']
        df = pd.read_csv(file_path)
        
        return self._apply_filters(df, country, year_range)
    
    @lru_cache(maxsize=10)
    def load_jobs_data(self, country=None, year_range=None):
        """
        Load jobs and employment data
        
        Parameters:
        -----------
        country : str or list, optional
            Filter by country name(s)
        year_range : tuple, optional
            (start_year, end_year) to filter data
        
        Returns:
        --------
        pd.DataFrame
        """
        file_path = self.data_dir / self.datasets['jobs']
        df = pd.read_csv(file_path)
        
        return self._apply_filters(df, country, year_range)
    
    @lru_cache(maxsize=10)
    def load_wdi_data(self, country=None, year_range=None):
        """
        Load World Development Indicators
        
        Parameters:
        -----------
        country : str or list, optional
            Filter by country name(s)
        year_range : tuple, optional
            (start_year, end_year) to filter data
        
        Returns:
        --------
        pd.DataFrame
        """
        file_path = self.data_dir / self.datasets['wdi']
        df = pd.read_csv(file_path)
        
        return self._apply_filters(df, country, year_range)
    
    @lru_cache(maxsize=10)
    def load_inequality_data(self, country=None, year_range=None, percentile=None):
        """
        Load World Inequality Database data
        
        Parameters:
        -----------
        country : str or list, optional
            Filter by country name(s)
        year_range : tuple, optional
            (start_year, end_year) to filter data
        percentile : str or list, optional
            Filter by percentile group(s)
        
        Returns:
        --------
        pd.DataFrame
        """
        file_path = self.data_dir / self.datasets['inequality']
        df = pd.read_csv(file_path)
        
        df = self._apply_filters(df, country, year_range)
        
        if percentile is not None:
            if isinstance(percentile, str):
                percentile = [percentile]
            df = df[df['Percentile'].isin(percentile)]
        
        return df
    
    def _apply_filters(self, df, country=None, year_range=None):
        """Apply common filters to dataframe"""
        if country is not None:
            if isinstance(country, str):
                country = [country]
            df = df[df['Country'].isin(country)]
        
        if year_range is not None:
            start_year, end_year = year_range
            df = df[(df['Year'] >= start_year) & (df['Year'] <= end_year)]
        
        return df
    
    def get_available_indicators(self, dataset='wdi'):
        """
        Get list of available indicators for a dataset
        
        Parameters:
        -----------
        dataset : str
            One of: 'education', 'jobs', 'wdi'
        
        Returns:
        --------
        pd.DataFrame with indicator names and codes
        """
        indicator_files = {
            'education': 'indicators_education_statistics.csv',
            'jobs': 'indicators_jobs_data.csv',
            'wdi': 'indicators_world_development_indicators.csv'
        }
        
        if dataset not in indicator_files:
            raise ValueError(f"Dataset must be one of: {list(indicator_files.keys())}")
        
        file_path = self.data_dir / indicator_files[dataset]
        return pd.read_csv(file_path)
    
    def get_indicator_data(self, dataset, indicator_name_or_code, country=None, year_range=None):
        """
        Get data for a specific indicator
        
        Parameters:
        -----------
        dataset : str
            One of: 'education', 'jobs', 'wdi'
        indicator_name_or_code : str
            Indicator name or series code
        country : str or list, optional
            Filter by country
        year_range : tuple, optional
            (start_year, end_year)
        
        Returns:
        --------
        pd.DataFrame
        """
        # Load the appropriate dataset
        if dataset == 'education':
            df = self.load_education_data()
        elif dataset == 'jobs':
            df = self.load_jobs_data()
        elif dataset == 'wdi':
            df = self.load_wdi_data()
        else:
            raise ValueError(f"Dataset must be one of: education, jobs, wdi")
        
        # Filter by indicator
        df = df[
            (df['Series Name'] == indicator_name_or_code) | 
            (df['Series Code'] == indicator_name_or_code)
        ]
        
        # Apply additional filters
        return self._apply_filters(df, country, year_range)
    
    def get_summary_stats(self):
        """Get summary statistics for all datasets"""
        summary = []
        
        for name, filename in self.datasets.items():
            try:
                file_path = self.data_dir / filename
                if file_path.exists():
                    df = pd.read_csv(file_path)
                    
                    stats = {
                        'Dataset': name,
                        'Total Records': len(df),
                        'Countries': df['Country'].nunique() if 'Country' in df.columns else 0,
                        'Year Range': f"{df['Year'].min():.0f}-{df['Year'].max():.0f}" if 'Year' in df.columns else 'N/A'
                    }
                    
                    if 'Series Name' in df.columns:
                        stats['Indicators'] = df['Series Name'].nunique()
                    elif 'Indicator' in df.columns:
                        stats['Indicators'] = df['Indicator'].nunique()
                    else:
                        stats['Indicators'] = 0
                    
                    summary.append(stats)
            except Exception as e:
                print(f"Error loading {name}: {e}")
        
        return pd.DataFrame(summary)


# Convenience functions for quick access
def load_education_data(country=None, year_range=None):
    """Quick access to education data"""
    loader = SouthAsiaDataLoader()
    return loader.load_education_data(country, year_range)


def load_jobs_data(country=None, year_range=None):
    """Quick access to jobs data"""
    loader = SouthAsiaDataLoader()
    return loader.load_jobs_data(country, year_range)


def load_wdi_data(country=None, year_range=None):
    """Quick access to World Development Indicators"""
    loader = SouthAsiaDataLoader()
    return loader.load_wdi_data(country, year_range)


def load_inequality_data(country=None, year_range=None, percentile=None):
    """Quick access to inequality data"""
    loader = SouthAsiaDataLoader()
    return loader.load_inequality_data(country, year_range, percentile)


def get_available_indicators(dataset='wdi'):
    """Quick access to available indicators"""
    loader = SouthAsiaDataLoader()
    return loader.get_available_indicators(dataset)


# Example usage
if __name__ == "__main__":
    # Initialize loader
    loader = SouthAsiaDataLoader()
    
    # Print summary
    print("\n" + "="*80)
    print("SOUTH ASIA DATA LOADER - SUMMARY")
    print("="*80)
    summary = loader.get_summary_stats()
    print(summary.to_string(index=False))
    
    # Example: Load education data for India from 2010-2020
    print("\n" + "="*80)
    print("EXAMPLE: Education Data for India (2010-2020)")
    print("="*80)
    india_edu = loader.load_education_data(country='India', year_range=(2010, 2020))
    print(india_edu.head(10))
    
    # Example: Get available WDI indicators
    print("\n" + "="*80)
    print("AVAILABLE WDI INDICATORS (First 10)")
    print("="*80)
    indicators = loader.get_available_indicators('wdi')
    print(indicators.head(10).to_string(index=False))
    
    # Example: Get specific indicator data
    print("\n" + "="*80)
    print("EXAMPLE: GDP per capita for all countries (2015-2020)")
    print("="*80)
    gdp_data = loader.get_indicator_data(
        dataset='wdi',
        indicator_name_or_code='GDP per capita (current US$)',
        year_range=(2015, 2020)
    )
    print(gdp_data.head(20))
