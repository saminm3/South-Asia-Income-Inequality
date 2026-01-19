# 🚀 Quick Reference Card - South Asia Data Integration

## One-Line Data Access

```python
from utils.data_loader import load_education_data, load_jobs_data, load_wdi_data, load_inequality_data
```

## Common Use Cases

### 1. Load All Data for a Country

```python
from utils.data_loader import SouthAsiaDataLoader
loader = SouthAsiaDataLoader()

india_edu = loader.load_education_data(country='India')
india_jobs = loader.load_jobs_data(country='India')
india_wdi = loader.load_wdi_data(country='India')
india_inequality = loader.load_inequality_data(country='India')
```

### 2. Get Recent Data

```python
recent_edu = load_education_data(year_range=(2015, 2020))
recent_jobs = load_jobs_data(year_range=(2015, 2020))
```

### 3. Compare Multiple Countries

```python
sa_core = load_wdi_data(country=['India', 'Pakistan', 'Bangladesh'])
```

### 4. Get Specific Indicator

```python
loader = SouthAsiaDataLoader()
gdp = loader.get_indicator_data(
    dataset='wdi',
    indicator_name_or_code='GDP per capita (current US$)',
    country='India',
    year_range=(2010, 2024)
)
```

### 5. List Available Indicators

```python
edu_indicators = loader.get_available_indicators('education')
jobs_indicators = loader.get_available_indicators('jobs')
wdi_indicators = loader.get_available_indicators('wdi')
```

## Streamlit Integration Template

```python
import streamlit as st
from utils.data_loader import SouthAsiaDataLoader
import plotly.express as px

@st.cache_data  # Cache for performance!
def load_data():
    loader = SouthAsiaDataLoader()
    return loader.load_wdi_data()

# Load and filter
df = load_data()
indicators = df['Series Name'].unique()

# User selection
selected_indicator = st.selectbox("Indicator", indicators)
selected_countries = st.multiselect("Countries", df['Country'].unique())

# Filter
filtered = df[
    (df['Series Name'] == selected_indicator) &
    (df['Country'].isin(selected_countries))
]

# Visualize
fig = px.line(filtered, x='Year', y='Value', color='Country')
st.plotly_chart(fig)
```

## Dataset Quick Stats

| Dataset | Records | Countries | Indicators | Years |
|---------|---------|-----------|------------|-------|
| Education | 401 | 7 | 4 | 2000-2020 |
| Jobs | 16,620 | 8 | 165 | 2000-2016 |
| WDI | 7,158 | 7 | 52 | 2000-2024 |
| Inequality | 750 | 6 | 5+ | 2000-2024 |

## Countries Available

🇦🇫 Afghanistan • 🇧🇩 Bangladesh • 🇧🇹 Bhutan • 🇮🇳 India • 🇲🇻 Maldives • 🇳🇵 Nepal • 🇵🇰 Pakistan • 🇱🇰 Sri Lanka

## File Locations

- **Cleaned Data**: `data/cleaned/cleaned_*.csv`
- **Indicators List**: `data/cleaned/indicators_*.csv`
- **Summary Report**: `data/cleaned/cleaning_summary_report.csv`
- **Data Loader**: `utils/data_loader.py`
- **Cleaning Pipeline**: `scripts/data_cleaning_pipeline.py`
- **Demo Page**: `pages/6_data_explorer.py`

## Update Pipeline

```bash
# Re-clean data (if raw files updated)
python scripts/data_cleaning_pipeline.py

# Test data loader
python utils/data_loader.py

# View demo page
# Navigate to "Data Explorer" in Streamlit sidebar
```

## Pro Tips

✅ **Always cache** in Streamlit: `@st.cache_data`  
✅ **Filter early**: Load only what you need  
✅ **Check for empty**: `if df.empty:` before visualizing  
✅ **Use year_range**: More efficient than filtering after  
✅ **Explore first**: Check `6_data_explorer.py` for inspiration  

## Need Help?

📚 Read: `DATA_INTEGRATION_GUIDE.md`  
📊 View: `data/cleaned/README.md`  
🔍 Explore: Run `pages/6_data_explorer.py`  
🧪 Test: Run `python utils/data_loader.py`  

---

**Your project now has 24,929+ data points ready to use! 🎉**
