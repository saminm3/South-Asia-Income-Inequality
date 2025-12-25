import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.loaders import load_all_indicators
from utils.utils import format_value

st.set_page_config(
    page_title="...",
    page_icon="...",
    layout="wide",
    initial_sidebar_state="collapsed"  # ADD THIS LINE
)
# Load custom CSS
try:
    with open('assets/dashboard.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.title("🌟 Sunburst Hierarchical Breakdown")
st.markdown("### Interactive hierarchical visualization of inequality indicators across South Asia")

# Load data
with st.spinner("Loading data..."):
    df = load_all_indicators()

if df.empty:
    st.error("❌ No data available")
    st.stop()

# Sidebar controls
with st.sidebar:
    st.subheader("Sunburst Settings")
    
    # Year selection
    available_years = sorted(df['year'].unique(), reverse=True)
    
    # Find year with most complete data
    year_coverage = df.groupby('year').agg({'value': 'count', 'indicator': 'nunique'})
    year_coverage['score'] = year_coverage['value'] * year_coverage['indicator']
    best_year = int(year_coverage['score'].idxmax())
    
    selected_year = st.selectbox(
        "Select Year",
        options=available_years,
        index=available_years.index(best_year) if best_year in available_years else 0,
        help="Year with most complete data is pre-selected"
    )
    
    # Color scheme
    color_scheme = st.selectbox(
        "Color Scheme",
        options=['Plasma', 'Viridis', 'Inferno', 'Magma', 'Cividis', 'Turbo'],
        index=0
    )
    
    st.info(f"💡 Using {selected_year} - year with most complete data coverage")

# Filter for selected year
sunburst_df = df[df['year'] == selected_year][['country', 'indicator', 'value']].copy()

if sunburst_df.empty:
    st.warning(f"⚠️ No data available for year {selected_year}")
    st.stop()

# Remove rows with NaN or zero values
sunburst_df = sunburst_df.dropna(subset=['value'])
sunburst_df = sunburst_df[sunburst_df['value'] != 0]

if sunburst_df.empty:
    st.warning(f"⚠️ No valid data available for year {selected_year} (all values are zero or missing)")
    st.stop()

st.info(f"📊 Visualizing {len(sunburst_df)} data points across {sunburst_df['country'].nunique()} countries and {sunburst_df['indicator'].nunique()} indicators")

# CRITICAL: Normalize each indicator to 0-100 scale for fair comparison
sunburst_df['normalized_value'] = 0.0

for indicator in sunburst_df['indicator'].unique():
    mask = sunburst_df['indicator'] == indicator
    values = sunburst_df.loc[mask, 'value']
    
    # Skip if all values are NaN or zero
    if values.isna().all() or (values == 0).all():
        continue
    
    if indicator == 'GINI':
        # GINI is already 0-100, keep as is
        sunburst_df.loc[mask, 'normalized_value'] = values
    elif indicator == 'HDI':
        # HDI is 0-1, convert to 0-100
        sunburst_df.loc[mask, 'normalized_value'] = values * 100
    else:
        # Normalize everything else to 0-100 scale within that indicator
        min_val, max_val = values.min(), values.max()
        if max_val > min_val and not pd.isna(max_val) and not pd.isna(min_val):
            sunburst_df.loc[mask, 'normalized_value'] = ((values - min_val) / (max_val - min_val)) * 100
        else:
            # If all values are the same, use the value itself as normalized
            # This prevents division by zero
            sunburst_df.loc[mask, 'normalized_value'] = 50.0

# Remove any rows where normalized_value is still 0 or NaN
sunburst_df = sunburst_df[sunburst_df['normalized_value'] > 0]
sunburst_df = sunburst_df.dropna(subset=['normalized_value'])

# Final check: ensure we have valid data
if sunburst_df.empty or sunburst_df['normalized_value'].sum() == 0:
    st.error(f"""
    ❌ **Cannot create sunburst chart for year {selected_year}**
    
    **Issue:** All normalized values sum to zero. This can happen when:
    - All values for the selected year are zero
    - Data is incomplete or missing
    - Normalization failed due to invalid values
    
    **Solution:** Try selecting a different year with more complete data.
    """)
    
    # Show available years with data
    valid_years = []
    for year in available_years:
        year_data = df[df['year'] == year]['value'].dropna()
        if len(year_data) > 0 and year_data.sum() > 0:
            valid_years.append(year)
    
    if valid_years:
        st.info(f"**Years with valid data:** {', '.join(map(str, valid_years[:10]))}")
    
    st.stop()

# Format actual values for display
def format_val(val):
    if pd.isna(val):
        return "N/A"
    elif val > 1e9:
        return f"{val/1e9:.2f}B"
    elif val > 1e6:
        return f"{val/1e6:.2f}M"
    elif val > 1000:
        return f"{val:,.0f}"
    else:
        return f"{val:.2f}"

sunburst_df['formatted_value'] = sunburst_df['value'].apply(format_val)

# Add region for proper hierarchy: Region > Country > Indicator
sunburst_df['Region'] = 'South Asia'

# Create sunburst with NORMALIZED values
try:
    fig = px.sunburst(
        sunburst_df,
        path=['Region', 'country', 'indicator'],
        values='normalized_value',  # Use normalized values for fair sizing
        color='normalized_value',
        color_continuous_scale=color_scheme,
        title=f'Inequality Indicators Breakdown - South Asia ({selected_year})',
        hover_data=['formatted_value']
    )
    
    # Update hover template to show actual values
    fig.update_traces(
        textinfo="label+percent parent",
        hovertemplate='<b>%{label}</b><br>Actual Value: %{customdata[0]}<br>Normalized: %{value:.1f}/100<extra></extra>',
        marker=dict(line=dict(color='white', width=2))
    )
    
    fig.update_layout(
        width=1000, 
        height=900, 
        font=dict(size=13), 
        title_x=0.5,
        title_font_size=18
    )
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Instructions
    st.info("""
    **How to interact:**
    - 🖱️ **Click** segments to zoom in/out
    - 👆 **Hover** for actual values
    - 📏 All indicators normalized to 0-100 scale for fair comparison
    - 🔄 **Click center** to zoom back out
    """)

except Exception as e:
    st.error(f"""
    ❌ **Error creating sunburst chart**
    
    **Error:** {str(e)}
    
    **Possible causes:**
    - Data quality issues for year {selected_year}
    - All values are zero or missing
    - Normalization failed
    
    **Solution:** Try selecting a different year or check your data files.
    """)
    st.stop()

# Detailed breakdown table
st.divider()
st.subheader("📋 Detailed Breakdown")

# Create detailed table
detail_table = sunburst_df.copy()
detail_table = detail_table[['country', 'indicator', 'formatted_value', 'normalized_value']].sort_values(['country', 'indicator'])
detail_table.columns = ['Country', 'Indicator', 'Actual Value', 'Normalized (0-100)']
detail_table['Normalized (0-100)'] = detail_table['Normalized (0-100)'].apply(lambda x: f"{x:.1f}")

st.dataframe(detail_table, use_container_width=True, hide_index=True)

# Summary by country
st.divider()
st.subheader("🌍 Country-wise Summary")

for country in sorted(sunburst_df['country'].unique()):
    with st.expander(f"📊 {country}"):
        country_data = sunburst_df[sunburst_df['country'] == country].sort_values('indicator')
        
        if country_data.empty:
            st.warning(f"No data available for {country}")
            continue
        
        for _, row in country_data.iterrows():
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**{row['indicator']}**")
            with col2:
                st.metric("Value", row['formatted_value'])
            with col3:
                st.metric("Normalized", f"{row['normalized_value']:.1f}/100")

# Export functionality
st.divider()
st.subheader("📥 Export Options")

col1, col2 = st.columns(2)

with col1:
    try:
        # Download chart as image
        img_bytes = fig.to_image(format="png", width=1400, height=1200)
        st.download_button(
            "📥 Download Chart (PNG)",
            data=img_bytes,
            file_name=f"sunburst_{selected_year}.png",
            mime="image/png",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")

with col2:
    # Download data as CSV
    csv = detail_table.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Data (CSV)",
        data=csv,
        file_name=f"sunburst_data_{selected_year}.csv",
        mime="text/csv",
        use_container_width=True
    )

# Methodology note
st.divider()
st.info("""
**📌 Note on Normalization:**

Different indicators have different scales:
- **GINI**: 0-100 (already normalized)
- **HDI**: 0-1 (multiplied by 100)
- **GDP, Labor Force**: Very large numbers (min-max normalized to 0-100)

All indicators are normalized to 0-100 scale to enable fair comparison in the sunburst chart. 
The "Actual Value" column shows the original, un-normalized values.

**Note:** Zero values and missing data are excluded from the visualization.
""")

# Footer
st.divider()
st.caption("Sunburst Hierarchical Breakdown | South Asia Inequality Analysis Platform")
st.caption(f"📊 Showing {len(sunburst_df)} indicators across {sunburst_df['country'].nunique()} countries for year {selected_year}")