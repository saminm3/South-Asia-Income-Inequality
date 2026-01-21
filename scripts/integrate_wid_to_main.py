"""
Integrate WID v2 Data into Main Indicators Dataset

This script appends WID v2 inequality indicators to the main south_asia_indicators.csv file,
making them available in the home page indicator dropdown.
"""

import pandas as pd
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def integrate_wid_to_main_indicators():
    """Integrate WID v2 data into the main indicators file."""
    
    # Paths
    project_root = Path(__file__).parent.parent
    wid_file = project_root / 'data' / 'cleaned' / 'cleaned_wid_v2.csv'
    main_indicators_file = project_root / 'data' / 'processed' / 'south_asia_indicators.csv'
    
    logger.info(f"Loading WID v2 data from: {wid_file}")
    logger.info(f"Loading main indicators from: {main_indicators_file}")
    
    # Load WID v2 data
    try:
        wid_df = pd.read_csv(wid_file)
        logger.info(f"Loaded {len(wid_df):,} WID v2 records")
    except Exception as e:
        logger.error(f"Failed to load WID v2 data: {e}")
        return False
    
    # Load main indicators
    try:
        main_df = pd.read_csv(main_indicators_file)
        logger.info(f"Loaded {len(main_df):,} existing indicator records")
    except Exception as e:
        logger.error(f"Failed to load main indicators: {e}")
        return False
    
    # Remove old WID data if it exists (to avoid duplicates on re-run)
    original_count = len(main_df)
    main_df = main_df[main_df['source'] != 'World Inequality Database'].copy()
    removed_count = original_count - len(main_df)
    if removed_count > 0:
        logger.info(f"Removed {removed_count:,} existing WID records")
    
    # Map country codes (WID uses 2-letter codes, we need 3-letter ISO codes)
    country_code_mapping = {
        'AF': 'AFG',  # Afghanistan
        'BD': 'BGD',  # Bangladesh
        'BT': 'BTN',  # Bhutan
        'IN': 'IND',  # India
        'MV': 'MDV',  # Maldives
        'NP': 'NPL',  # Nepal
        'PK': 'PAK',  # Pakistan
        'LK': 'LKA'   # Sri Lanka
    }
    
    # Transform WID data to match main indicators schema
    logger.info("Transforming WID data to match main indicators schema...")
    
    def get_percentile_description(percentile_code):
        """Convert percentile code to human-readable description."""
        # Common percentile groups with meaningful descriptions
        predefined = {
            'p0p1': 'the Poorest 1%',
            'p0p10': 'the Bottom 10% (Poorest Tenth)',
            'p0p50': 'the Bottom Half of Population (Poorest 50%)',
            'p50p90': 'the Middle Class (40% between median and top 10%)',
            'p90p100': 'the Richest 10% (Top Tenth)',
            'p99p100': 'the Top 1% (Ultra-Wealthy)',
            'p95p100': 'the Top 5% (Very Wealthy)',
            'p0p100': 'All Population (Everyone)',
            'p0p20': 'the Bottom 20% (Poorest Fifth)',
            'p20p40': 'the Second Poorest 20%',
            'p40p60': 'the Middle 20%',
            'p60p80': 'the Second Richest 20%',
            'p80p100': 'the Top 20% (Richest Fifth)',
        }
        
        if percentile_code in predefined:
            return predefined[percentile_code]
        
        # For granular percentiles, create numeric description
        # Format: p0p23 means "from 0th to 23rd percentile"
        if percentile_code.startswith('p') and 'p' in percentile_code[1:]:
            parts = percentile_code[1:].split('p')
            if len(parts) == 2:
                try:
                    start, end = int(parts[0]), int(parts[1])
                    if start == 0:
                        return f"the Bottom {end}% of Population"
                    elif end == 100:
                        return f"the Top {100-start}% of Population"
                    else:
                        return f"the {start}th-{end}th Percentile"
                except ValueError:
                    pass
        
        # Fallback
        return percentile_code
    
    wid_records = []
    
    # Process WID data - create human-readable indicator names
    for _, row in wid_df.iterrows():
        # Skip if country not in mapping
        if row['Country_Code'] not in country_code_mapping:
            continue
        
        # Create indicator name based on user's specific request
        indicator_name = None
        
        # 1. Income Inequality - Handle Gini coefficients separately
        if row['Indicator_Category'] == 'Income Inequality':
            # Gini coefficients
            if row['Variable_Code'].startswith('gptinc') and row['Percentile'] == 'p0p100':
                indicator_name = "Income Inequality (Gini)"
            # Income shares
            elif 'sptinc' in row['Variable_Code']:
                if row['Percentile'] == 'p90p100': 
                    indicator_name = "Top 10% share (Income)"
                elif row['Percentile'] == 'p0p50': 
                    indicator_name = "Bottom 50% share (Income)"
                elif row['Percentile'] == 'p99p100': 
                    indicator_name = "Top 1% share (Income)"
                
        # 2. Average Income
        elif row['Indicator_Category'] == 'Average Income':
            if row['Percentile'] == 'p0p100':
                if 'aptinc' in row['Variable_Code']: 
                    indicator_name = "Per capita national income"
                elif 'anninc' in row['Variable_Code']: 
                    indicator_name = "Per capita national income"
                elif 'nngdp' in row['Variable_Code']: 
                    indicator_name = "Per capita GDP"
            else:
                indicator_name = f"Average Income ({get_percentile_description(row['Percentile'])})"

        # 3. Wealth Inequality
        elif row['Indicator_Category'] == 'Wealth Inequality':
            # Gini coefficients for wealth
            if row['Variable_Code'].startswith('ghweal') and row['Percentile'] == 'p0p100':
                indicator_name = "Wealth Inequality (Gini)"
            # Wealth shares
            elif 'shweal' in row['Variable_Code']:
                if row['Percentile'] == 'p90p100': 
                    indicator_name = "Top 10% share (Wealth)"
                elif row['Percentile'] == 'p0p50': 
                    indicator_name = "Bottom 50% share (Wealth)"
                elif row['Percentile'] == 'p99p100': 
                    indicator_name = "Top 1% share (Wealth)"
                
        # 4. Average Wealth
        elif row['Indicator_Category'] == 'Average Wealth':
            if row['Percentile'] == 'p0p100':
                indicator_name = "Per adult national wealth"
            
        # 5. Carbon Inequality
        elif row['Indicator_Category'] == 'Carbon Inequality':
            if 'enfghg' in row['Variable_Code']: 
                indicator_name = "National carbon footprint"
            elif row['Percentile'] == 'p90p100' and 'scarb' in row['Variable_Code']: 
                indicator_name = "Top 10% carbon emitters"
            
        # 6. Gender Inequality
        elif row['Indicator_Category'] == 'Gender Inequality':
            if 'fmlinc' in row['Variable_Code']:
                indicator_name = "Female labor income share"

        # Fallback for other important WID variables not explicitly requested but useful
        if not indicator_name:
            if row['Percentile'] == 'p0p100':
                indicator_name = f"{row['Indicator_Category']} - {row['Indicator_Description']}"
            else:
                # Keep original descriptive logic for others but keep it short
                desc = get_percentile_description(row['Percentile'])
                indicator_name = f"{row['Indicator_Category']} ({desc})"

        # Create a record
        record = {
            'country': row['Country'],
            'country_code': country_code_mapping[row['Country_Code']],
            'year': row['Year'],
            'indicator': indicator_name,
            'value': row['Value'],
            'source': 'World Inequality Database'
        }
        
        wid_records.append(record)
    
    # Convert to DataFrame
    wid_transformed = pd.DataFrame(wid_records)
    logger.info(f"Transformed {len(wid_transformed):,} WID records")
    
    # Show sample of indicators being added
    logger.info("Sample WID indicators being added:")
    for indicator in sorted(wid_transformed['indicator'].unique())[:10]:
        logger.info(f"  - {indicator}")
    
    # Combined dataframe for final processing
    combined_df = pd.concat([main_df, wid_transformed], ignore_index=True)
    
    # --- PHASE 2: REFINEMENT ---
    logger.info("Refining dataset for professional deployment...")
    
    # 1. Filter for strictly South Asian countries (already handled by mapping, but let's be sure)
    sa_countries = ['Afghanistan', 'Bangladesh', 'Bhutan', 'India', 'Maldives', 'Nepal', 'Pakistan', 'Sri Lanka']
    combined_df = combined_df[combined_df['country'].isin(sa_countries)].copy()
    
    # 2. Filter for year range 2000-2025
    combined_df = combined_df[(combined_df['year'] >= 2000) & (combined_df['year'] <= 2025)].copy()
    logger.info(f"Filtered for years 2000-2025. Remaining records: {len(combined_df):,}")
    
    # 3. Filter for data density (>= 3 countries per indicator)
    indicator_counts = combined_df.groupby('indicator')['country'].nunique()
    valid_indicators = indicator_counts[indicator_counts >= 3].index.tolist()
    
    combined_df = combined_df[combined_df['indicator'].isin(valid_indicators)].copy()
    logger.info(f"Filtered for indicators with >= 3 countries. Remaining indicators: {len(valid_indicators)}")
    
    # 4. Sort and clean
    combined_df = combined_df.sort_values(['country', 'year', 'indicator']).reset_index(drop=True)
    
    # Save back to main indicators file
    logger.info(f"Saving refined dataset to: {main_indicators_file}")
    combined_df.to_csv(main_indicators_file, index=False)
    
    logger.info(f"\n{'='*60}")
    logger.info("INTEGRATION & REFINEMENT SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total records in final set: {len(combined_df):,}")
    logger.info(f"Total unique indicators: {combined_df['indicator'].nunique()}")
    logger.info(f"Year range: {combined_df['year'].min()} - {combined_df['year'].max()}")
    logger.info(f"{'='*60}")
    
    return True


def main():
    """Main entry point."""
    logger.info("Starting WID v2 integration into main indicators...")
    
    success = integrate_wid_to_main_indicators()
    
    if success:
        logger.info("✓ Integration completed successfully")
        logger.info("WID indicators are now available in the home page dropdown!")
        return 0
    else:
        logger.error("✗ Integration failed")
        return 1


if __name__ == '__main__':
    exit(main())
