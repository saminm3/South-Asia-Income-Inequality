import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.loaders import load_inequality_data
from utils.utils import human_indicator

# Page config
st.set_page_config(
    page_title="Temporal Comparison",
    page_icon="📊",
    layout="wide"
)

# Load custom CSS
try:
    with open('assets/dashboard.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.title("📊 Temporal Comparison: Then vs Now")
st.markdown("### Compare inequality indicators across two time periods")

# Check if analysis config exists
if 'analysis_config' not in st.session_state or st.session_state.analysis_config is None:
    st.warning("⚠️ No analysis configured. Please configure your analysis on the Home page.")
    st.info("Click 'home' in the sidebar to configure your analysis")
    st.stop()

# Get configuration
config = st.session_state.analysis_config

# Load data
df = load_inequality_data()

if df.empty:
    st.error("❌ No data available")
    st.stop()

# Filter for selected countries and indicator
filtered = df[
    (df['country'].isin(config['countries'])) &
    (df['indicator'] == config['indicator'])
].copy()

if filtered.empty:
    st.warning("⚠️ No data available for selected filters")
    st.stop()

# Year selection
st.subheader("📅 Select Time Periods to Compare")

col1, col2 = st.columns(2)

available_years = sorted(filtered['year'].unique())

with col1:
    year_then = st.selectbox(
        "Then (Earlier Year)",
        options=available_years,
        index=0,
        help="Select the earlier time period"
    )

with col2:
    year_now = st.selectbox(
        "Now (Recent Year)",
        options=available_years,
        index=len(available_years)-1,
        help="Select the more recent time period"
    )

if year_then >= year_now:
    st.error("⚠️ 'Then' year must be earlier than 'Now' year")
    st.stop()

# Filter data for selected years
comparison_data = filtered[filtered['year'].isin([year_then, year_now])].copy()

if comparison_data.empty:
    st.warning(f"⚠️ No data available for years {year_then} and {year_now}")
    st.stop()

# Pivot for comparison
pivot = comparison_data.pivot_table(
    index='country',
    columns='year',
    values='value'
).reset_index()

# Calculate change
if year_then in pivot.columns and year_now in pivot.columns:
    pivot['Change'] = pivot[year_now] - pivot[year_then]
    pivot['Change %'] = ((pivot[year_now] - pivot[year_then]) / pivot[year_then] * 100).round(1)
    pivot['Direction'] = pivot['Change'].apply(lambda x: '📈 Increased' if x > 0 else ('📉 Decreased' if x < 0 else '➡️ No Change'))

st.divider()

# Side-by-side comparison
st.subheader("📊 Side-by-Side Comparison")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"### 📅 {year_then}")
    
    if year_then in pivot.columns:
        then_data = pivot[['country', year_then]].copy()
        then_data.columns = ['Country', human_indicator(config['indicator'])]
        then_data = then_data.sort_values(human_indicator(config['indicator']), ascending=False)
        then_data['Rank'] = range(1, len(then_data) + 1)
        then_data = then_data[['Rank', 'Country', human_indicator(config['indicator'])]]
        
        st.dataframe(then_data, use_container_width=True, hide_index=True)
        
        # Bar chart
        fig_then = px.bar(
            then_data,
            x='Country',
            y=human_indicator(config['indicator']),
            title=f"{human_indicator(config['indicator'])} - {year_then}",
            color=human_indicator(config['indicator']),
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_then, use_container_width=True)

with col2:
    st.markdown(f"### 📅 {year_now}")
    
    if year_now in pivot.columns:
        now_data = pivot[['country', year_now]].copy()
        now_data.columns = ['Country', human_indicator(config['indicator'])]
        now_data = now_data.sort_values(human_indicator(config['indicator']), ascending=False)
        now_data['Rank'] = range(1, len(now_data) + 1)
        now_data = now_data[['Rank', 'Country', human_indicator(config['indicator'])]]
        
        st.dataframe(now_data, use_container_width=True, hide_index=True)
        
        # Bar chart
        fig_now = px.bar(
            now_data,
            x='Country',
            y=human_indicator(config['indicator']),
            title=f"{human_indicator(config['indicator'])} - {year_now}",
            color=human_indicator(config['indicator']),
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_now, use_container_width=True)

# Change analysis
st.divider()
st.subheader("📈 Change Analysis")

if 'Change' in pivot.columns:
    change_display = pivot[['country', year_then, year_now, 'Change', 'Change %', 'Direction']].copy()
    change_display.columns = ['Country', f'{year_then}', f'{year_now}', 'Absolute Change', 'Percentage Change', 'Direction']
    change_display = change_display.sort_values('Absolute Change', ascending=False)
    
    st.dataframe(change_display, use_container_width=True, hide_index=True)
    
    # Change visualization
    fig_change = go.Figure()
    
    for _, row in change_display.iterrows():
        color = 'red' if row['Absolute Change'] > 0 else 'green'
        fig_change.add_trace(go.Bar(
            x=[row['Country']],
            y=[row['Absolute Change']],
            name=row['Country'],
            marker_color=color,
            showlegend=False
        ))
    
    fig_change.update_layout(
        title=f"Change in {human_indicator(config['indicator'])} ({year_then} → {year_now})",
        xaxis_title="Country",
        yaxis_title="Change",
        height=400
    )
    
    st.plotly_chart(fig_change, use_container_width=True)

# Ranking shifts
st.divider()
st.subheader("🔄 Ranking Shifts")

if year_then in pivot.columns and year_now in pivot.columns:
    rank_then = pivot[[' country', year_then]].copy()
    rank_then['Rank_Then'] = rank_then[year_then].rank(ascending=True, method='min').astype(int)
    
    rank_now = pivot[['country', year_now]].copy()
    rank_now['Rank_Now'] = rank_now[year_now].rank(ascending=True, method='min').astype(int)
    
    rank_comparison = pd.merge(rank_then, rank_now, on='country')
    rank_comparison['Rank_Change'] = rank_comparison['Rank_Now'] - rank_comparison['Rank_Then']
    rank_comparison['Movement'] = rank_comparison['Rank_Change'].apply(
        lambda x: f'⬆️ Up {abs(x)} positions' if x < 0 else (f'⬇️ Down {abs(x)} positions' if x > 0 else '➡️ No change')
    )
    
    rank_display = rank_comparison[['country', 'Rank_Then', 'Rank_Now', 'Movement']].copy()
    rank_display.columns = ['Country', f'Rank ({year_then})', f'Rank ({year_now})', 'Movement']
    
    st.dataframe(rank_display, use_container_width=True, hide_index=True)

# Key insights
st.divider()
st.subheader("🔑 Key Insights")

if 'Change %' in pivot.columns:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        biggest_increase = pivot.loc[pivot['Change %'].idxmax()]
        st.metric(
            "Biggest Increase",
            f"{biggest_increase['country']}",
            f"+{biggest_increase['Change %']:.1f}%"
        )
    
    with col2:
        biggest_decrease = pivot.loc[pivot['Change %'].idxmin()]
        st.metric(
            "Biggest Decrease",
            f"{biggest_decrease['country']}",
            f"{biggest_decrease['Change %']:.1f}%"
        )
    
    with col3:
        avg_change = pivot['Change %'].mean()
        st.metric(
            "Average Change",
            f"{avg_change:.1f}%",
            delta_color="off"
        )

# Export
st.divider()
st.subheader("📥 Export Comparison")

col1, col2 = st.columns(2)

with col1:
    if 'Change' in pivot.columns:
        csv = change_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Comparison (CSV)",
            data=csv,
            file_name=f"temporal_comparison_{year_then}_vs_{year_now}.csv",
            mime="text/csv",
            use_container_width=True
        )

with col2:
    if 'fig_change' in locals():
        img_bytes = fig_change.to_image(format="png", width=1200, height=600)
        st.download_button(
            "📥 Download Change Chart (PNG)",
            data=img_bytes,
            file_name=f"change_chart_{year_then}_vs_{year_now}.png",
            mime="image/png",
            use_container_width=True
        )

# Footer
st.divider()
st.caption("Temporal Comparison | South Asia Inequality Analysis Platform")
st.caption(f"📊 Comparing {human_indicator(config['indicator'])} between {year_then} and {year_now}")