import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.loaders import load_inequality_data
from utils.filters import sidebar_filters
from utils.utils import human_indicator

# Page config
st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load custom CSS
try:
    with open('assets/dashboard.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Check if analysis config exists
if 'analysis_config' not in st.session_state or st.session_state.analysis_config is None:
    st.warning("⚠️ No analysis configured. Please configure your analysis on the Home page.")
    st.info("Click 'home' in the sidebar to configure your analysis")
    st.stop()

# Get configuration
config = st.session_state.analysis_config

st.title("📊 Multi-Dimensional Dashboard")
st.markdown(f"**Analysis:** {', '.join(config['countries'])} | {config['year_range'][0]}-{config['year_range'][1]} | {human_indicator(config['indicator'])}")

# Load data
df = load_inequality_data()

if df.empty:
    st.error("❌ No data available")
    st.stop()

# Filter data
filtered_df = df[
    (df['country'].isin(config['countries'])) &
    (df['year'] >= config['year_range'][0]) &
    (df['year'] <= config['year_range'][1]) &
    (df['indicator'] == config['indicator'])
].copy()

if filtered_df.empty:
    st.warning("⚠️ No data available for selected filters")
    st.stop()

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Trends", "🔍 Comparison", "📋 Data Table"])

with tab1:
    st.subheader("Key Metrics Summary")
    
    # Calculate metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        latest_year = filtered_df['year'].max()
        latest_data = filtered_df[filtered_df['year'] == latest_year]
        avg_value = latest_data['value'].mean()
        st.metric(
            f"Average {config['indicator']} ({latest_year})",
            f"{avg_value:.2f}"
        )
    
    with col2:
        min_country = latest_data.loc[latest_data['value'].idxmin(), 'country']
        min_value = latest_data['value'].min()
        st.metric(
            "Lowest",
            f"{min_value:.2f}",
            delta=f"{min_country}",
            delta_color="off"
        )
    
    with col3:
        max_country = latest_data.loc[latest_data['value'].idxmax(), 'country']
        max_value = latest_data['value'].max()
        st.metric(
            "Highest",
            f"{max_value:.2f}",
            delta=f"{max_country}",
            delta_color="off"
        )
    
    with col4:
        range_value = max_value - min_value
        st.metric(
            "Range",
            f"{range_value:.2f}",
            delta=f"{(range_value/avg_value*100):.1f}% of avg",
            delta_color="off"
        )
    
    st.divider()
    
    # Distribution chart
    st.subheader("Distribution Analysis")
    
    fig_dist = px.histogram(
        latest_data,
        x='value',
        nbins=10,
        title=f"{human_indicator(config['indicator'])} Distribution ({latest_year})",
        labels={'value': human_indicator(config['indicator']), 'count': 'Frequency'}
    )
    st.plotly_chart(fig_dist, use_container_width=True)
    
    # Export
    col1, col2 = st.columns(2)
    with col1:
        img_bytes = fig_dist.to_image(format="png", width=1200, height=600)
        st.download_button(
            "📥 Download Chart (PNG)",
            data=img_bytes,
            file_name=f"distribution_{config['indicator']}.png",
            mime="image/png",
            use_container_width=True
        )
    with col2:
        csv = latest_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Data (CSV)",
            data=csv,
            file_name=f"distribution_data.csv",
            mime="text/csv",
            use_container_width=True
        )

with tab2:
    st.subheader("Temporal Trends")
    
    # Line chart
    fig_trend = px.line(
        filtered_df,
        x='year',
        y='value',
        color='country',
        markers=True,
        title=f"{human_indicator(config['indicator'])} Trends Over Time",
        labels={'value': human_indicator(config['indicator']), 'year': 'Year'}
    )
    
    fig_trend.update_layout(
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Change analysis
    st.subheader("Change Analysis")
    
    change_data = []
    for country in config['countries']:
        country_data = filtered_df[filtered_df['country'] == country].sort_values('year')
        if len(country_data) >= 2:
            start_value = country_data.iloc[0]['value']
            end_value = country_data.iloc[-1]['value']
            change = end_value - start_value
            pct_change = (change / start_value * 100) if start_value != 0 else 0
            
            change_data.append({
                'Country': country,
                'Start Value': f"{start_value:.2f}",
                'End Value': f"{end_value:.2f}",
                'Change': f"{change:+.2f}",
                'Change %': f"{pct_change:+.1f}%"
            })
    
    if change_data:
        change_df = pd.DataFrame(change_data)
        st.dataframe(change_df, use_container_width=True, hide_index=True)
    
    # Export
    col1, col2 = st.columns(2)
    with col1:
        img_bytes = fig_trend.to_image(format="png", width=1200, height=600)
        st.download_button(
            "📥 Download Chart (PNG)",
            data=img_bytes,
            file_name=f"trends_{config['indicator']}.png",
            mime="image/png",
            use_container_width=True
        )
    with col2:
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Trend Data (CSV)",
            data=csv,
            file_name=f"trend_data.csv",
            mime="text/csv",
            use_container_width=True
        )

with tab3:
    st.subheader("Country Comparison")
    
    # Bar chart - latest year
    latest_comp = filtered_df[filtered_df['year'] == filtered_df['year'].max()].sort_values('value', ascending=False)
    
    fig_comp = px.bar(
        latest_comp,
        x='country',
        y='value',
        color='value',
        color_continuous_scale=config.get('color_scale', 'Reds'),
        title=f"{human_indicator(config['indicator'])} Comparison ({latest_comp['year'].iloc[0]})",
        labels={'value': human_indicator(config['indicator']), 'country': 'Country'}
    )
    
    st.plotly_chart(fig_comp, use_container_width=True)
    
    # Rankings
    st.subheader("Rankings")
    
    rankings = latest_comp[['country', 'value']].copy()
    rankings['Rank'] = range(1, len(rankings) + 1)
    rankings = rankings[['Rank', 'country', 'value']]
    rankings.columns = ['Rank', 'Country', human_indicator(config['indicator'])]
    
    st.dataframe(rankings, use_container_width=True, hide_index=True)
    
    # Export
    col1, col2 = st.columns(2)
    with col1:
        img_bytes = fig_comp.to_image(format="png", width=1200, height=600)
        st.download_button(
            "📥 Download Chart (PNG)",
            data=img_bytes,
            file_name=f"comparison_{config['indicator']}.png",
            mime="image/png",
            use_container_width=True
        )
    with col2:
        csv = rankings.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Rankings (CSV)",
            data=csv,
            file_name=f"rankings.csv",
            mime="text/csv",
            use_container_width=True
        )

with tab4:
    st.subheader("Complete Data Table")
    
    # Pivot table for better readability
    pivot_df = filtered_df.pivot_table(
        index='year',
        columns='country',
        values='value',
        aggfunc='first'
    ).reset_index()
    
    st.dataframe(pivot_df, use_container_width=True, hide_index=True)
    
    # Summary statistics
    st.subheader("Summary Statistics")
    
    summary = filtered_df.groupby('country')['value'].agg([
        ('Mean', 'mean'),
        ('Median', 'median'),
        ('Std Dev', 'std'),
        ('Min', 'min'),
        ('Max', 'max')
    ]).round(2)
    
    st.dataframe(summary, use_container_width=True)
    
    # Export
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Complete Data (CSV)",
        data=csv,
        file_name=f"complete_data_{config['indicator']}.csv",
        mime="text/csv",
        use_container_width=True
    )

# Footer
st.divider()
st.caption("Dashboard | South Asia Inequality Analysis Platform")