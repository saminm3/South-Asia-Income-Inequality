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

# Tabs for different views (removed redundant Comparison tab)
tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Trends", "📋 Data Table"])

with tab1:
    st.subheader("Key Metrics Summary")
    
    # Calculate metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        latest_year = filtered_df['year'].max()
        latest_data = filtered_df[filtered_df['year'] == latest_year].copy()
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
            delta=f"↓ {min_country}",
            delta_color="off"
        )
    
    with col3:
        max_country = latest_data.loc[latest_data['value'].idxmax(), 'country']
        max_value = latest_data['value'].max()
        st.metric(
            "Highest",
            f"{max_value:.2f}",
            delta=f"↑ {max_country}",
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
    
    # ═══════════════════════════════════════════════════════════════════
    # ✨ ULTRA-VISUAL DISTRIBUTION ANALYSIS ✨
    # ═══════════════════════════════════════════════════════════════════
    
    st.subheader("🎨 Distribution Analysis")
    
    # Country flag emojis for South Asia
    country_flags = {
        'Afghanistan': '🇦🇫',
        'Bangladesh': '🇧🇩',
        'India': '🇮🇳',
        'Pakistan': '🇵🇰',
        'Nepal': '🇳🇵',
        'Sri Lanka': '🇱🇰'
    }
    
    # Add flags to data
    latest_data['flag'] = latest_data['country'].map(country_flags).fillna('🌏')
    latest_data['country_display'] = latest_data.apply(lambda x: f"{x['flag']} {x['country']}", axis=1)
    
    # Calculate statistics
    avg_val = latest_data['value'].mean()
    min_val = latest_data['value'].min()
    max_val = latest_data['value'].max()
    data_range = max_val - min_val
    
    # Create tabs for different visualizations
    viz_tab1, viz_tab2, viz_tab3 = st.tabs(["🎯 Radial View", "💎 Premium Cards", "📊 Comparison"])
    
    # ═══════════════════════════════════════════════════════════
    # TAB 1: RADIAL BAR CHART (Most Visual)
    # ═══════════════════════════════════════════════════════════
    with viz_tab1:
        st.markdown("### 🎯 Radial Distribution")
        
        # Create radial bar chart (polar chart)
        fig_radial = go.Figure()
        
        # Add radial bars
        fig_radial.add_trace(go.Barpolar(
            r=latest_data['value'].tolist(),
            theta=latest_data['country_display'].tolist(),
            marker=dict(
                color=latest_data['value'].tolist(),
                colorscale='Viridis',
                line=dict(color='white', width=2),
                cmin=min_val,
                cmax=max_val
            ),
            text=[f"{v:.2f}" for v in latest_data['value']],
            hovertemplate='<b>%{theta}</b><br>Value: %{r:.2f}<extra></extra>',
            showlegend=False
        ))
        
        fig_radial.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max_val * 1.2],
                    showticklabels=True,
                    tickfont=dict(size=12, color='white'),
                    gridcolor='rgba(255,255,255,0.2)'
                ),
                angularaxis=dict(
                    tickfont=dict(size=14, color='white'),
                    rotation=90,
                    direction='clockwise'
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title=dict(
                text=f"{human_indicator(config['indicator'])} - Radial Distribution ({latest_year})",
                x=0.5,
                font=dict(size=18, color='white')
            ),
            height=550,
            showlegend=False
        )
        
        st.plotly_chart(fig_radial, use_container_width=True)
        
        # Quick stats below radial chart
        cols = st.columns(4)
        with cols[0]:
            st.metric("🌍 Countries", len(latest_data))
        with cols[1]:
            st.metric("📊 Average", f"{avg_val:.2f}")
        with cols[2]:
            st.metric("⬇️ Lowest", f"{min_val:.2f}")
        with cols[3]:
            st.metric("⬆️ Highest", f"{max_val:.2f}")
    
    # ═══════════════════════════════════════════════════════════
    # TAB 2: PREMIUM GRADIENT CARDS (Most Beautiful)
    # ═══════════════════════════════════════════════════════════
    with viz_tab2:
        st.markdown("### 💎 Premium Country Cards")
        
        # Sort by value for better visualization
        sorted_data = latest_data.sort_values('value', ascending=False).reset_index(drop=True)
        
        # Create cards
        for idx, row in sorted_data.iterrows():
            # Calculate color intensity based on value
            if max_val > min_val:
                intensity = (row['value'] - min_val) / (max_val - min_val)
            else:
                intensity = 0.5
            
            # Rank
            rank = idx + 1
            rank_emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
            
            # Delta from average
            delta = row['value'] - avg_val
            delta_emoji = "📈" if delta > 0 else "📉" if delta < 0 else "➡️"
            
            # Color gradient based on value (green = high, red = low)
            if intensity > 0.66:
                gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"  # Purple
            elif intensity > 0.33:
                gradient = "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"  # Pink
            else:
                gradient = "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"  # Blue
            
            # Create premium card with HTML/CSS
            st.markdown(f"""
            <div style="
                background: {gradient};
                padding: 25px;
                border-radius: 15px;
                margin-bottom: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                border: 2px solid rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex: 1;">
                        <div style="font-size: 2.5em; margin-bottom: 5px;">{row['flag']}</div>
                        <div style="font-size: 1.5em; font-weight: bold; color: white; margin-bottom: 10px;">
                            {row['country']}
                        </div>
                        <div style="font-size: 0.9em; color: rgba(255,255,255,0.8);">
                            {human_indicator(config['indicator'])}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 3em; font-weight: bold; color: white; margin-bottom: 5px;">
                            {row['value']:.2f}
                        </div>
                        <div style="font-size: 1.2em; color: rgba(255,255,255,0.9); margin-bottom: 5px;">
                            {rank_emoji} Rank {rank}
                        </div>
                        <div style="font-size: 1em; color: rgba(255,255,255,0.8);">
                            {delta_emoji} {delta:+.2f} vs avg
                        </div>
                    </div>
                </div>
                <div style="margin-top: 15px; background: rgba(255,255,255,0.2); height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="background: white; height: 100%; width: {intensity*100}%; border-radius: 4px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Summary statistics
        st.markdown("---")
        st.markdown("### 📈 Summary Statistics")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Average", f"{avg_val:.2f}")
        with col2:
            st.metric("Median", f"{latest_data['value'].median():.2f}")
        with col3:
            st.metric("Std Dev", f"{latest_data['value'].std():.2f}")
        with col4:
            st.metric("Range", f"{data_range:.2f}")
        with col5:
            cv = (latest_data['value'].std()/avg_val*100) if avg_val != 0 else 0
            st.metric("CV", f"{cv:.1f}%")
    
    # ═══════════════════════════════════════════════════════════
    # TAB 3: COMPARISON CHART (Most Detailed)
    # ═══════════════════════════════════════════════════════════
    with viz_tab3:
        st.markdown("### 📊 Detailed Comparison")
        
        # Create horizontal bar chart with gradient
        sorted_data = latest_data.sort_values('value', ascending=True)
        
        fig_compare = go.Figure()
        
        # Add bars with gradient colors
        fig_compare.add_trace(go.Bar(
            y=sorted_data['country_display'],
            x=sorted_data['value'],
            orientation='h',
            marker=dict(
                color=sorted_data['value'],
                colorscale='Turbo',
                line=dict(color='white', width=2),
                cmin=min_val,
                cmax=max_val
            ),
            text=[f"<b>{v:.2f}</b>" for v in sorted_data['value']],
            textposition='outside',
            textfont=dict(size=14, color='white'),
            hovertemplate='<b>%{y}</b><br>Value: %{x:.2f}<br><extra></extra>',
            showlegend=False
        ))
        
        # Add average line
        fig_compare.add_vline(
            x=avg_val, 
            line_dash="dash", 
            line_color="yellow",
            line_width=2,
            annotation_text=f"Average: {avg_val:.2f}",
            annotation_position="top right",
            annotation_font_color="yellow"
        )
        
        fig_compare.update_layout(
            title=dict(
                text=f"{human_indicator(config['indicator'])} Comparison ({latest_year})",
                font=dict(size=18, color='white'),
                x=0.5
            ),
            xaxis=dict(
                title=human_indicator(config['indicator']),
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                titlefont=dict(color='white'),
                tickfont=dict(color='white')
            ),
            yaxis=dict(
                title='',
                tickfont=dict(size=14, color='white')
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=max(400, len(sorted_data) * 80),
            margin=dict(l=20, r=100, t=80, b=50)
        )
        
        st.plotly_chart(fig_compare, use_container_width=True)
        
        # Ranking table
        st.markdown("### 🏆 Rankings")
        ranking_data = latest_data.sort_values('value', ascending=False).reset_index(drop=True)
        ranking_data['Rank'] = range(1, len(ranking_data) + 1)
        ranking_data['Difference from Avg'] = ranking_data['value'] - avg_val
        ranking_data['Percentile'] = ranking_data['value'].rank(pct=True) * 100
        
        ranking_display = ranking_data[['Rank', 'country_display', 'value', 'Difference from Avg', 'Percentile']].copy()
        ranking_display.columns = ['🏅 Rank', '🌍 Country', '📊 Value', '📈 vs Average', '📍 Percentile']
        ranking_display['📊 Value'] = ranking_display['📊 Value'].apply(lambda x: f"{x:.2f}")
        ranking_display['📈 vs Average'] = ranking_display['📈 vs Average'].apply(lambda x: f"{x:+.2f}")
        ranking_display['📍 Percentile'] = ranking_display['📍 Percentile'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(ranking_display, use_container_width=True, hide_index=True)
    
    # ═══════════════════════════════════════════════════════════
    # BONUS: Mini Sparklines
    # ═══════════════════════════════════════════════════════════
    st.divider()
    st.markdown("### ✨ Quick Overview")
    cols = st.columns(len(latest_data))
    for i, row in enumerate(latest_data.sort_values('value', ascending=False).itertuples()):
        with cols[i]:
            # Calculate position relative to range
            if max_val > min_val:
                position = (row.value - min_val) / (max_val - min_val) * 100
            else:
                position = 50
            
            # Create mini gauge using HTML/CSS
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; background: rgba(255,255,255,0.05); border-radius: 10px;">
                <div style="font-size: 2em; margin-bottom: 8px;">{row.flag}</div>
                <div style="font-size: 0.9em; color: rgba(255,255,255,0.7); margin-bottom: 8px;">{row.country}</div>
                <div style="font-size: 1.8em; font-weight: bold; color: #4fc3f7; margin-bottom: 8px;">{row.value:.2f}</div>
                <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 3px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #4fc3f7, #29b6f6); height: 100%; width: {position}%; border-radius: 3px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════
    # END OF ULTRA-VISUAL DISTRIBUTION
    # ═══════════════════════════════════════════════════════════
    
    st.divider()
    
    # Export buttons
    st.subheader("📥 Export Distribution Data")
    col1, col2 = st.columns(2)
    with col1:
        # Export the comparison chart
        img_bytes = fig_compare.to_image(format="png", width=1200, height=800)
        st.download_button(
            "📥 Download Chart (PNG)",
            data=img_bytes,
            file_name=f"distribution_{config['indicator']}.png",
            mime="image/png",
            use_container_width=True
        )
    with col2:
        csv = latest_data[['country', 'value']].to_csv(index=False).encode('utf-8')
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