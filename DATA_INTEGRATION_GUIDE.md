# Data Integration Guide

## Overview
This guide explains how to use the newly integrated datasets in your South Asia Income Inequality project.

## 📊 Available Datasets

### 1. **Education Statistics** (2000-2020)
- **Source**: World Bank Education Statistics
- **Coverage**: 7 South Asian countries
- **Records**: 401
- **Indicators**: 4
- **Key Metrics**:
  - Government expenditure on education (% of GDP)
  - Gross enrolment ratio (primary, female %)
  - Gross enrolment ratio (primary, gender parity index)
  - Out-of-school children (primary school age)

### 2. **Jobs & Employment Data** (2000-2016)
- **Source**: World Bank Jobs Database
- **Coverage**: 8 South Asian countries
- **Records**: 16,620
- **Indicators**: 165
- **Key Metrics**:
  - Employment by sector (agriculture, industry, services)
  - Labor force participation rates
  - Unemployment rates
  - Wage and salary workers
  - Self-employment rates
  - Vulnerable employment

### 3. **World Development Indicators** (2000-2024)
- **Source**: World Bank WDI
- **Coverage**: 7 South Asian countries
- **Records**: 7,158
- **Indicators**: 52
- **Key Metrics**:
  - GDP per capita
  - Poverty rates
  - Life expectancy
  - Fertility rates
  - Access to electricity
  - Internet usage
  - Foreign direct investment
  - Government expenditure

### 4. **Inequality Data** (2000-2024)
- **Source**: World Inequality Database (WID)
- **Coverage**: 6 South Asian countries
- **Records**: 750
- **Indicators**: Income share by percentile
- **Key Metrics**:
  - Pre-tax national income by percentile
  - Income shares for different population groups
  - Bottom 50%, Middle 40%, Top 10%, Top 1%

## 🚀 How to Use the Data

### Basic Usage

```python
from utils.data_loader import SouthAsiaDataLoader

# Initialize the loader
loader = SouthAsiaDataLoader()

# Load complete datasets
education_df = loader.load_education_data()
jobs_df = loader.load_jobs_data()
wdi_df = loader.load_wdi_data()
inequality_df = loader.load_inequality_data()
```

### Filtered Queries

```python
# Get data for specific country
india_data = loader.load_wdi_data(country='India')

# Get data for multiple countries
sa_core = loader.load_jobs_data(country=['India', 'Pakistan', 'Bangladesh'])

# Get data for specific time period
recent_data = loader.load_education_data(year_range=(2015, 2020))

# Combine filters
india_edu_recent = loader.load_education_data(
    country='India',
    year_range=(2015, 2020)
)
```

### Get Specific Indicators

```python
# List available indicators for a dataset
indicators = loader.get_available_indicators('wdi')
print(indicators)

# Get specific indicator data
gdp_data = loader.get_indicator_data(
    dataset='wdi',
    indicator_name_or_code='GDP per capita (current US$)',
    country='India',
    year_range=(2010, 2020)
)
```

### Inequality Data with Percentiles

```python
# Get inequality data for bottom 50%
bottom_50 = loader.load_inequality_data(percentile='p0p50')

# Multiple percentiles
top_groups = loader.load_inequality_data(
    percentile=['p90p100', 'p99p100'],
    country=['India', 'Bangladesh'],
    year_range=(2010, 2020)
)
```

## 📈 Integration Examples for Streamlit Pages

### Example 1: Education Dashboard

```python
import streamlit as st
from utils.data_loader import load_education_data
import plotly.express as px

st.title("Education Statistics Dashboard")

# Load data
df = load_education_data(year_range=(2010, 2020))

# Filter for gender parity index
gpi_data = df[df['Series Code'] == 'SE.ENR.PRIM.FM.ZS']

# Create visualization
fig = px.line(
    gpi_data,
    x='Year',
    y='Value',
    color='Country',
    title='Primary Education Gender Parity Index (2010-2020)'
)

st.plotly_chart(fig)
```

### Example 2: Employment Trends

```python
import streamlit as st
from utils.data_loader import load_jobs_data
import plotly.express as px

st.title("Employment Trends")

# Load jobs data
df = load_jobs_data(country=['India', 'Pakistan', 'Bangladesh'])

# Let user select indicator
indicators = df['Series Name'].unique()
selected = st.selectbox("Select Indicator", indicators)

# Filter and visualize
filtered = df[df['Series Name'] == selected]
fig = px.line(filtered, x='Year', y='Value', color='Country')
st.plotly_chart(fig)
```

### Example 3: Inequality Comparison

```python
import streamlit as st
from utils.data_loader import load_inequality_data
import plotly.graph_objects as go

st.title("Income Inequality Comparison")

# Load inequality data
df = load_inequality_data(year_range=(2010, 2020))

# Create grouped bar chart
countries = df['Country'].unique()
years = sorted(df['Year'].unique())

fig = go.Figure()
for country in countries:
    country_data = df[df['Country'] == country]
    fig.add_trace(go.Bar(
        name=country,
        x=country_data['Year'],
        y=country_data['Value']
    ))

fig.update_layout(title='Income Share of Bottom 50%')
st.plotly_chart(fig)
```

### Example 4: Multi-Dataset Dashboard

```python
import streamlit as st
from utils.data_loader import SouthAsiaDataLoader

loader = SouthAsiaDataLoader()

# User selects country
country = st.selectbox("Select Country", 
    ['India', 'Pakistan', 'Bangladesh', 'Nepal', 'Sri Lanka'])

# Load multiple datasets
col1, col2 = st.columns(2)

with col1:
    st.subheader("Education Metrics")
    edu_data = loader.load_education_data(country=country)
    st.dataframe(edu_data)

with col2:
    st.subheader("Employment Metrics")
    jobs_data = loader.load_jobs_data(country=country)
    st.dataframe(jobs_data)

# WDI Overview
st.subheader("Development Indicators")
wdi_data = loader.load_wdi_data(country=country, year_range=(2015, 2020))
st.dataframe(wdi_data)
```

## 🗂️ Data Structure

All cleaned datasets follow this standardized structure:

### Standard Datasets (Education, Jobs, WDI)
```
Country        | Country Code | Year | Series Name           | Series Code    | Value
India          | IND          | 2020 | GDP per capita       | NY.GDP.PCAP.CD | 1927.71
Bangladesh     | BGD          | 2020 | Unemployment rate    | SL.UEM.TOTL.ZS | 5.3
```

### Inequality Dataset (WID)
```
Country    | Country_Code | Year | Percentile | Indicator  | Value
India      | IN           | 2020 | p0p50      | sptinc_z   | 15.2
Bangladesh | BD           | 2020 | p90p100    | sptinc_z   | 42.8
```

## 📝 Common Use Cases

### 1. Time Series Analysis
```python
# Track a metric over time
gdp_trend = loader.get_indicator_data(
    dataset='wdi',
    indicator_name_or_code='GDP per capita (current US$)',
    country='India',
    year_range=(2000, 2023)
)
```

### 2. Cross-Country Comparison
```python
# Compare countries for recent year
recent_edu = loader.load_education_data(year_range=(2020, 2020))
pivot = recent_edu.pivot_table(
    values='Value',
    index='Series Name',
    columns='Country'
)
```

### 3. Correlation Analysis
```python
# Get multiple indicators for correlation
loader = SouthAsiaDataLoader()

# GDP and education spending
gdp = loader.get_indicator_data('wdi', 'GDP per capita (current US$)')
edu_spend = loader.get_education_data()

# Merge and analyze
combined = pd.merge(gdp, edu_spend, on=['Country', 'Year'])
```

## 🎯 Best Practices

1. **Cache your data loads** in Streamlit:
```python
@st.cache_data
def load_cached_data():
    loader = SouthAsiaDataLoader()
    return loader.load_wdi_data()
```

2. **Filter early** - Apply country and year filters when loading to reduce memory:
```python
# Good
df = loader.load_jobs_data(country='India', year_range=(2015, 2020))

# Less efficient
df = loader.load_jobs_data()
df = df[df['Country'] == 'India']
```

3. **Check data availability** before visualizing:
```python
df = loader.load_education_data(country='Bhutan')
if df.empty:
    st.warning("No data available for selected filters")
else:
    # Create visualization
    pass
```

## 📚 Available Indicators by Dataset

To see full list of indicators:
```python
# Education indicators
edu_indicators = loader.get_available_indicators('education')

# Jobs indicators  
jobs_indicators = loader.get_available_indicators('jobs')

# WDI indicators
wdi_indicators = loader.get_available_indicators('wdi')
```

Or check the files in `data/cleaned/`:
- `indicators_education_statistics.csv`
- `indicators_jobs_data.csv`
- `indicators_world_development_indicators.csv`

## 🔄 Updating the Data

To re-run the data cleaning pipeline with updated raw files:

```bash
python scripts/data_cleaning_pipeline.py
```

This will:
1. Read raw data from `/Users/shaierasultanaoishe/Downloads/raw`
2. Filter for South Asian countries
3. Filter for years 2000-2025
4. Clean and standardize the data
5. Save to `data/cleaned/`
6. Generate summary report

## 🆘 Troubleshooting

**Q: Data loader can't find files**
```python
# Specify custom data directory
loader = SouthAsiaDataLoader(data_dir='/path/to/cleaned/data')
```

**Q: Missing countries in results**
- Some datasets don't have all 8 countries
- Check `cleaning_summary_report.csv` for dataset coverage

**Q: Getting empty results**
- Verify year range exists in the dataset
- Check indicator name/code spelling
- Use `get_available_indicators()` to see what's available

## 📊 Next Steps

1. Integrate these datasets into existing pages:
   - Update `1_dashboard.py` with WDI metrics
   - Enhance `5_income_simulator.py` with real jobs/education data
   - Create new inequality analysis page with WID data

2. Create new visualizations:
   - Education progress tracking
   - Employment sector shifts
   - Inequality trends over time
   - Multi-indicator comparisons

3. Add interactivity:
   - Dynamic indicator selection
   - Country comparison tools
   - Year range sliders
   - Export functionality

## 📞 Support

For issues or questions about the data:
- Check `data/cleaned/cleaning_summary_report.csv` for dataset overview
- Review `indicators_*.csv` files for available metrics
- Examine sample data using `utils/data_loader.py` examples
