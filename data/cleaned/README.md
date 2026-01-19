# Cleaned Data Directory

## 📁 Contents

This directory contains cleaned and standardized datasets for South Asian countries (2000-2025).

### Files Overview

| File | Description | Records | Countries | Indicators | Years |
|------|-------------|---------|-----------|------------|-------|
| `cleaned_education_statistics.csv` | Education metrics from World Bank | 401 | 7 | 4 | 2000-2020 |
| `cleaned_jobs_data.csv` | Employment and labor market data | 16,620 | 8 | 165 | 2000-2016 |
| `cleaned_world_development_indicators.csv` | Development indicators from WDI | 7,158 | 7 | 52 | 2000-2024 |
| `cleaned_wid_inequality_data.csv` | Income inequality data from WID | 750 | 6 | 5 | 2000-2024 |
| `cleaning_summary_report.csv` | Summary report of all datasets | - | - | - | - |
| `indicators_*.csv` | List of available indicators for each dataset | - | - | - | - |

## 🌏 Country Coverage

- 🇦🇫 Afghanistan
- 🇧🇩 Bangladesh  
- 🇧🇹 Bhutan
- 🇮🇳 India
- 🇲🇻 Maldives
- 🇳🇵 Nepal
- 🇵🇰 Pakistan
- 🇱🇰 Sri Lanka

*Note: Not all datasets include all countries*

## 📊 Data Structure

All datasets follow a standardized long-format structure for easy analysis:

### Standard Format (Education, Jobs, WDI)

```csv
Country,Country Code,Year,Series Name,Series Code,Value
India,IND,2020,GDP per capita (current US$),NY.GDP.PCAP.CD,1927.71
```

### Inequality Format (WID)

```csv
Country,Country_Code,Year,Percentile,Indicator,Value
India,IN,2020,p0p50,sptinc_z,15.2
```

## 🔍 Key Indicators by Dataset

### Education Statistics

- Government expenditure on education as % of GDP
- Gross enrolment ratio, primary, female (%)
- Gross enrolment ratio, primary, gender parity index (GPI)
- Out-of-school children of primary school age

### Jobs & Employment

- Employment in agriculture/industry/services (% of total)
- Labor force participation rate (by gender, age)
- Unemployment rate (total, youth, by gender)
- Wage and salary workers (% of total)
- Self-employed workers (% of total)
- Vulnerable employment (% of total)
- And 160+ more indicators...

### World Development Indicators

- Poverty headcount ratio
- GDP per capita (current US$)
- Life expectancy at birth
- Mortality rates
- Access to electricity
- Internet usage
- Fertility rates
- Foreign direct investment
- Government expenditure
- And 45+ more indicators...

### Inequality Data (WID)

Income shares by percentile groups:

- p0p50: Bottom 50%
- p50p90: Middle 40%
- p90p100: Top 10%
- p99p100: Top 1%
- And more percentile breakdowns...

## 📝 Data Quality Notes

### Completeness

- All datasets filtered for years 2000-2025
- Missing values removed during cleaning
- Some indicators may not be available for all countries/years

### Data Sources

- **World Bank**: Education Statistics, Jobs Database, World Development Indicators
- **WID**: World Inequality Database (income inequality metrics)

### Last Updated

- Cleaning pipeline run: 2026-01-18
- Raw data sources: Various (see DATA_INTEGRATION_GUIDE.md)

## 🚀 Usage

### Quick Start

```python
from utils.data_loader import SouthAsiaDataLoader

loader = SouthAsiaDataLoader()

# Load datasets
education = loader.load_education_data()
jobs = loader.load_jobs_data()
wdi = loader.load_wdi_data()
inequality = loader.load_inequality_data()
```

### Advanced Filtering

```python
# Country-specific data
india_edu = loader.load_education_data(country='India')

# Time range
recent_jobs = loader.load_jobs_data(year_range=(2010, 2016))

# Specific indicator
gdp_data = loader.get_indicator_data(
    dataset='wdi',
    indicator_name_or_code='GDP per capita (current US$)',
    country=['India', 'Bangladesh'],
    year_range=(2015, 2024)
)
```

## 📖 Documentation

For complete usage guide and integration examples, see:

- **DATA_INTEGRATION_GUIDE.md** - Comprehensive integration guide
- **utils/data_loader.py** - Data loader implementation with examples

## 🔄 Updating Data

To re-clean data with updated raw files:

```bash
python scripts/data_cleaning_pipeline.py
```

Ensure raw data files are in: `/Users/shaierasultanaoishe/Downloads/raw`

## ⚠️ Important Notes

1. **Year Range**: Data is filtered for 2000-2025, but not all datasets cover all years
2. **Missing Data**: Some country-indicator-year combinations may not have data
3. **Data Types**: All numeric values are stored as float, use appropriate rounding for display
4. **Country Names**: Standardized to full names (e.g., 'India' not 'IND')
5. **Caching**: Use caching when loading data repeatedly in Streamlit apps

## 📞 Support

For questions or issues:

1. Check the cleaning summary report: `cleaning_summary_report.csv`
2. Review available indicators: `indicators_*.csv` files
3. Consult the integration guide: `DATA_INTEGRATION_GUIDE.md`
4. Test with the data loader: `python utils/data_loader.py`

## 📊 Statistics Summary

```
Total Records: 24,929
Total Countries: 8 (coverage varies by dataset)
Total Indicators: 221
Time Coverage: 2000-2025 (varies by dataset)
File Size: ~2.4 MB total
```

---

**Generated by South Asia Income Inequality Data Cleaning Pipeline**
