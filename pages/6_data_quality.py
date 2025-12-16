import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.loaders import load_quality_audit

# Page config
st.set_page_config(
    page_title="Data Quality",
    page_icon="✅",
    layout="wide"
)

# Load custom CSS
try:
    with open('assets/dashboard.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.title("✅ Data Quality Dashboard")
st.markdown("### Monitor completeness and reliability of inequality data across South Asia")

# Load data
with st.spinner("Loading quality audit data..."):
    audit = load_quality_audit()

if audit.empty:
    st.error("❌ Quality audit data not found")
    st.info("""
    **Required file:** `data/processed/quality_audit.csv`
    
    This file should contain:
    - country: Country name
    - indicator: Indicator name
    - completeness: Percentage (0-100)
    - year_range: e.g., "2000-2023"
    - issues: Description of data gaps
    - source: Data source
    - last_updated: Last update date
    """)
    st.stop()

# Color coding function
def get_quality_badge(score):
    """Return emoji badge based on quality score"""
    if score >= 80:
        return "🟢 High"
    elif score >= 60:
        return "🟡 Medium"
    else:
        return "🔴 Low"

def get_quality_color(score):
    """Return color based on quality score"""
    if score >= 80:
        return "green"
    elif score >= 60:
        return "orange"
    else:
        return "red"

# Add quality badge column
if 'completeness' in audit.columns:
    audit['Quality'] = audit['completeness'].apply(get_quality_badge)
    audit['Quality_Color'] = audit['completeness'].apply(get_quality_color)

# Sidebar filters
st.sidebar.header("🔍 Filters")

if 'country' in audit.columns:
    selected_countries = st.sidebar.multiselect(
        "Countries", 
        options=sorted(audit['country'].unique()),
        default=sorted(audit['country'].unique())
    )
else:
    selected_countries = []

if 'indicator' in audit.columns:
    selected_indicators = st.sidebar.multiselect(
        "Indicators",
        options=sorted(audit['indicator'].unique()),
        default=sorted(audit['indicator'].unique())
    )
else:
    selected_indicators = []

# Quality threshold filter
min_quality = st.sidebar.slider(
    "Minimum Quality (%)",
    0, 100, 0,
    help="Filter to show only datasets above this quality threshold"
)

# Filter data
filtered = audit.copy()

if selected_countries and 'country' in filtered.columns:
    filtered = filtered[filtered['country'].isin(selected_countries)]

if selected_indicators and 'indicator' in filtered.columns:
    filtered = filtered[filtered['indicator'].isin(selected_indicators)]

if 'completeness' in filtered.columns:
    filtered = filtered[filtered['completeness'] >= min_quality]

# Display summary metrics
st.subheader("📊 Quality Summary")

col1, col2, col3, col4 = st.columns(4)

if 'completeness' in filtered.columns and len(filtered) > 0:
    with col1:
        avg_completeness = filtered['completeness'].mean()
        st.metric("Average Completeness", f"{avg_completeness:.1f}%")
    
    with col2:
        high_quality = len(filtered[filtered['completeness'] >= 80])
        total = len(filtered)
        st.metric("High Quality Datasets", f"{high_quality}/{total}")
    
    with col3:
        medium_quality = len(filtered[(filtered['completeness'] >= 60) & (filtered['completeness'] < 80)])
        st.metric("Medium Quality", f"{medium_quality}/{total}")
    
    with col4:
        critical_gaps = len(filtered[filtered['completeness'] < 60])
        st.metric("Critical Gaps", critical_gaps, delta="Needs attention" if critical_gaps > 0 else "None")
else:
    st.warning("No data available for quality metrics")

# Visualizations
st.divider()

tab1, tab2, tab3 = st.tabs(["📋 Data Table", "📊 Visualizations", "🚨 Critical Gaps"])

with tab1:
    st.subheader("Data Quality by Country and Indicator")
    
    # Display columns based on what's available
    display_cols = ['country', 'indicator']
    if 'year_range' in filtered.columns:
        display_cols.append('year_range')
    if 'Quality' in filtered.columns:
        display_cols.append('Quality')
    if 'completeness' in filtered.columns:
        display_cols.append('completeness')
    if 'issues' in filtered.columns:
        display_cols.append('issues')
    if 'source' in filtered.columns:
        display_cols.append('source')
    if 'last_updated' in filtered.columns:
        display_cols.append('last_updated')
    
    # Filter to only existing columns
    display_cols = [col for col in display_cols if col in filtered.columns]
    
    if display_cols:
        display_df = filtered[display_cols].sort_values('completeness', ascending=False) if 'completeness' in filtered.columns else filtered[display_cols]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.dataframe(filtered, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Quality Visualizations")
    
    if 'completeness' in filtered.columns and len(filtered) > 0:
        # Heatmap by country and indicator
        if 'country' in filtered.columns and 'indicator' in filtered.columns:
            st.markdown("#### 🔥 Completeness Heatmap")
            
            heatmap_data = filtered.pivot_table(
                index='indicator',
                columns='country',
                values='completeness',
                aggfunc='mean'
            )
            
            fig_heatmap = px.imshow(
                heatmap_data,
                labels=dict(x="Country", y="Indicator", color="Completeness %"),
                color_continuous_scale='RdYlGn',
                aspect="auto",
                text_auto='.0f'
            )
            
            fig_heatmap.update_layout(height=500)
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Bar chart by country
        if 'country' in filtered.columns:
            st.markdown("#### 📊 Average Completeness by Country")
            
            country_avg = filtered.groupby('country')['completeness'].mean().sort_values(ascending=False)
            
            fig_country = go.Figure(go.Bar(
                x=country_avg.index,
                y=country_avg.values,
                marker_color=country_avg.apply(get_quality_color).values,
                text=country_avg.apply(lambda x: f"{x:.1f}%").values,
                textposition='auto'
            ))
            
            fig_country.update_layout(
                xaxis_title="Country",
                yaxis_title="Average Completeness (%)",
                yaxis_range=[0, 100],
                height=400
            )
            
            st.plotly_chart(fig_country, use_container_width=True)
        
        # Bar chart by indicator
        if 'indicator' in filtered.columns:
            st.markdown("#### 📈 Average Completeness by Indicator")
            
            indicator_avg = filtered.groupby('indicator')['completeness'].mean().sort_values(ascending=False)
            
            fig_indicator = go.Figure(go.Bar(
                x=indicator_avg.index,
                y=indicator_avg.values,
                marker_color=indicator_avg.apply(get_quality_color).values,
                text=indicator_avg.apply(lambda x: f"{x:.1f}%").values,
                textposition='auto'
            ))
            
            fig_indicator.update_layout(
                xaxis_title="Indicator",
                yaxis_title="Average Completeness (%)",
                yaxis_range=[0, 100],
                height=400
            )
            
            st.plotly_chart(fig_indicator, use_container_width=True)
        
        # Distribution chart
        st.markdown("#### 📊 Quality Distribution")
        
        quality_dist = filtered['Quality'].value_counts() if 'Quality' in filtered.columns else pd.Series()
        
        if len(quality_dist) > 0:
            fig_dist = px.pie(
                values=quality_dist.values,
                names=quality_dist.index,
                title="Distribution of Data Quality Levels",
                color=quality_dist.index,
                color_discrete_map={'🟢 High': 'green', '🟡 Medium': 'orange', '🔴 Low': 'red'}
            )
            
            st.plotly_chart(fig_dist, use_container_width=True)

with tab3:
    st.subheader("🚨 Critical Data Gaps")
    
    if 'completeness' in filtered.columns:
        critical = filtered[filtered['completeness'] < 60].sort_values('completeness')
        
        if len(critical) > 0:
            st.error(f"Found {len(critical)} critical data gaps (completeness < 60%)")
            
            for i, row in critical.head(10).iterrows():
                with st.expander(f"⚠️ {row.get('country', 'N/A')} - {row.get('indicator', 'N/A')} ({row['completeness']:.1f}%)"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Completeness:** {row['completeness']:.1f}%")
                        if 'year_range' in row:
                            st.markdown(f"**Year Range:** {row.get('year_range', 'N/A')}")
                        if 'source' in row:
                            st.markdown(f"**Source:** {row.get('source', 'N/A')}")
                    
                    with col2:
                        if 'issues' in row:
                            st.markdown(f"**Issues:** {row.get('issues', 'No details')}")
                        if 'last_updated' in row:
                            st.markdown(f"**Last Updated:** {row.get('last_updated', 'N/A')}")
        else:
            st.success("✅ No critical data gaps found! All datasets have ≥60% completeness.")
    else:
        st.info("Completeness data not available")

# Data sources breakdown
if 'source' in filtered.columns:
    st.divider()
    st.subheader("📚 Data Sources Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sources = filtered['source'].value_counts()
        st.markdown("**Number of Datasets by Source:**")
        for source, count in sources.items():
            st.markdown(f"- **{source}:** {count} datasets")
    
    with col2:
        if len(sources) > 0:
            fig_sources = px.bar(
                x=sources.values,
                y=sources.index,
                orientation='h',
                labels={'x': 'Number of Datasets', 'y': 'Source'},
                title="Datasets by Source"
            )
            st.plotly_chart(fig_sources, use_container_width=True)

# Export functionality
st.divider()
st.subheader("📥 Export Quality Report")

col1, col2 = st.columns(2)

with col1:
    # Export full audit
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Quality Report (CSV)",
        data=csv,
        file_name="data_quality_report.csv",
        mime="text/csv",
        help="Download complete quality audit report",
        use_container_width=True
    )

with col2:
    # Export critical gaps only
    if 'completeness' in filtered.columns:
        critical_only = filtered[filtered['completeness'] < 60]
        if len(critical_only) > 0:
            critical_csv = critical_only.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Critical Gaps (CSV)",
                data=critical_csv,
                file_name="critical_gaps_report.csv",
                mime="text/csv",
                help="Download only critical gaps (<60% completeness)",
                use_container_width=True
            )

# Recommendations
st.divider()
st.subheader("💡 Recommendations")

if 'completeness' in filtered.columns and len(filtered) > 0:
    avg_comp = filtered['completeness'].mean()
    
    if avg_comp >= 80:
        st.success("""
        ✅ **Excellent Data Quality**
        
        Your dataset has high completeness across most indicators. Continue monitoring for:
        - Annual updates from source organizations
        - New data releases
        - Potential methodology changes
        """)
    elif avg_comp >= 60:
        st.warning("""
        ⚠️ **Good Quality with Room for Improvement**
        
        Consider:
        - Identifying patterns in missing data
        - Exploring alternative data sources for gaps
        - Documenting known limitations
        """)
    else:
        st.error("""
        🔴 **Significant Data Gaps**
        
        Priority actions:
        - Review critical gaps in the table above
        - Consider if analysis is valid with current completeness
        - Explore supplementary data sources
        - Document limitations prominently in reports
        """)

# Footer
st.divider()
st.caption("Data Quality Dashboard | South Asia Inequality Analysis Platform")
st.caption("✅ Transparency in data quality is essential for credible research")