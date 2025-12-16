import streamlit as st
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.loaders import load_inequality_data
from utils.insights import generate_insights, format_insights_text

# Page config
st.set_page_config(
    page_title="Auto Insights",
    page_icon="💡",
    layout="wide"
)

# Load custom CSS
try:
    with open('assets/dashboard.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.title("💡 Auto-Generated Insights")
st.markdown("### Natural language summaries and discoveries from your data")

# Check if analysis config exists
if 'analysis_config' not in st.session_state or st.session_state.analysis_config is None:
    st.warning("⚠️ No analysis configured. Please configure your analysis on the Home page.")
    st.info("Click 'home' in the sidebar to configure your analysis")
    st.stop()

# Get configuration
config = st.session_state.analysis_config

st.info(f"**Analyzing:** {', '.join(config['countries'])} | {config['indicator']} | {config['year_range'][0]}-{config['year_range'][1]}")

# Load data
with st.spinner("Loading data and generating insights..."):
    df = load_inequality_data()
    
    if df.empty:
        st.error("❌ No data available")
        st.stop()
    
    # Generate insights
    insights = generate_insights(
        df,
        config['indicator'],
        config['countries'],
        config['year_range']
    )

# Display insights
st.divider()
st.subheader("📊 Key Findings")

if not insights or len(insights) == 0:
    st.warning("No insights generated. Try selecting different parameters.")
else:
    # Group insights by type
    trend_insights = [i for i in insights if '📈' in i or '📉' in i]
    ranking_insights = [i for i in insights if '🏆' in i or '🔴' in i or '🟢' in i]
    statistical_insights = [i for i in insights if '📊' in i or '📏' in i]
    quality_insights = [i for i in insights if '⚠️' in i or '⚡' in i]
    
    # Tabs for organized view
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 All Insights", "📈 Trends", "🏆 Rankings", "📊 Statistics"])
    
    with tab1:
        st.markdown("### Complete Analysis")
        for i, insight in enumerate(insights, 1):
            st.markdown(f"{i}. {insight}")
    
    with tab2:
        st.markdown("### Trend Analysis")
        if trend_insights:
            for insight in trend_insights:
                st.markdown(f"• {insight}")
        else:
            st.info("No trend insights available")
    
    with tab3:
        st.markdown("### Rankings & Thresholds")
        if ranking_insights:
            for insight in ranking_insights:
                st.markdown(f"• {insight}")
        else:
            st.info("No ranking insights available")
    
    with tab4:
        st.markdown("### Statistical Findings")
        stats_to_show = statistical_insights + quality_insights
        if stats_to_show:
            for insight in stats_to_show:
                st.markdown(f"• {insight}")
        else:
            st.info("No statistical insights available")

# Export functionality
st.divider()
st.subheader("📥 Export Insights")

col1, col2 = st.columns(2)

with col1:
    # Export as formatted text
    insights_text = format_insights_text(insights)
    st.download_button(
        "📥 Download Insights (TXT)",
        data=insights_text,
        file_name=f"insights_{config['indicator']}_{config['year_range'][0]}-{config['year_range'][1]}.txt",
        mime="text/plain",
        use_container_width=True
    )

with col2:
    # Export as markdown
    insights_md = "\n\n".join([f"{i}. {ins}" for i, ins in enumerate(insights, 1)])
    st.download_button(
        "📥 Download Insights (MD)",
        data=insights_md,
        file_name=f"insights_{config['indicator']}.md",
        mime="text/markdown",
        use_container_width=True
    )

# Methodology note
st.divider()
st.subheader("ℹ️ About Auto-Insights")

with st.expander("How are insights generated?"):
    st.markdown("""
    **Auto-insights are generated using statistical analysis:**
    
    1. **Trend Analysis**: Calculates percentage changes over time
    2. **Rankings**: Compares countries at latest year
    3. **Regional Statistics**: Computes averages, medians, ranges
    4. **Volatility Analysis**: Uses coefficient of variation (CV)
    5. **Anomaly Detection**: Identifies unusual values using Z-scores
    6. **Threshold Analysis**: Compares against standard thresholds (e.g., GINI > 40 = high inequality)
    7. **Data Quality Assessment**: Evaluates completeness
    
    **Limitations:**
    - Insights are statistical observations, not policy recommendations
    - Correlation does not imply causation
    - Missing data may affect accuracy
    - Thresholds are general guidelines, not absolute rules
    
    **Tip:** Use these insights as a starting point for deeper analysis!
    """)

# Footer
st.divider()
st.caption("Auto-Generated Insights | South Asia Inequality Analysis Platform")
st.caption("💡 These insights are generated automatically from data patterns and should be validated")