import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.loaders import load_inequality_data
from utils.insights import generate_insights, generate_multimode_insights, format_insights_as_text



# ═══════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Auto Insights",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern dark theme CSS (matching dashboard)
st.markdown("""
<style>
    /* Main dark gradient background */
    .main {
        background: linear-gradient(180deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
    }
    
    /* Remove padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 800 !important;
    }
    
    /* Mode selector buttons */
    div[data-testid="column"] button {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(236, 72, 153, 0.1)) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        padding: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="column"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 32px rgba(139, 92, 246, 0.4) !important;
        border-color: rgba(139, 92, 246, 0.6) !important;
    }
    
    /* Insight cards */
    .insight-card {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(236, 72, 153, 0.05));
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }
    
    .insight-card-green {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.05));
        border-color: rgba(16, 185, 129, 0.4);
    }
    
    .insight-card-red {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(239, 68, 68, 0.05));
        border-color: rgba(239, 68, 68, 0.4);
    }
    
    .insight-card-yellow {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.05));
        border-color: rgba(245, 158, 11, 0.4);
    }
    
    /* Text colors */
    p, label, .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    /* Metric styling */
    div[data-testid="metric-container"] {
        background: rgba(15, 20, 25, 0.6);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 12px;
        padding: 1rem;
    }
    
    div[data-testid="metric-container"] label {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
    }
    
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.8rem !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(15, 20, 25, 0.6);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 12px;
        color: #e2e8f0 !important;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background: rgba(15, 20, 25, 0.8) !important;
        border: 1px solid rgba(139, 92, 246, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def ensure_public_analysis(df: pd.DataFrame) -> None:
    """Create default config if none exists - open access"""
    if "analysis_config" not in st.session_state or st.session_state.analysis_config is None:
        countries = sorted(df["country"].dropna().unique().tolist())
        indicators = sorted(df["indicator"].dropna().unique().tolist())
        min_year = int(df["year"].min())
        max_year = int(df["year"].max())
        default_indicator = "gini_index" if "gini_index" in indicators else (indicators[0] if indicators else None)
        
        st.session_state.analysis_config = {
            "countries": countries,
            "indicator": default_indicator,
            "year_range": (max(min_year, max_year - 20), max_year),
            "color_scale": "Viridis",
            "timestamp": pd.Timestamp.now(),
        }


# ═══════════════════════════════════════════════════════════════════
# LOAD DATA
# ═══════════════════════════════════════════════════════════════════

df = load_inequality_data()

if df.empty:
    st.error("❌ No data available. Please check your processed dataset.")
    st.stop()

ensure_public_analysis(df)
config = st.session_state.analysis_config

# ═══════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<div style="margin-bottom: 2rem;">
    <h1 style="font-size: 2.5rem; margin: 0; background: linear-gradient(90deg, #8b5cf6 0%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
        💡 Auto-Generated Insights
    </h1>
    <p style="color: #94a3b8; font-size: 1rem; margin-top: 0.5rem;">
        Intelligent analysis adapts to your audience - policymakers, researchers, or both
    </p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# MODE SELECTOR
# ═══════════════════════════════════════════════════════════════════

st.markdown("### 🎯 Choose Your View")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📖 Simple\n\nPlain language for policymakers", key="btn_simple", use_container_width=True):
        st.session_state.insight_mode = 'simple'

with col2:
    if st.button("🔬 Technical\n\nStatistical details for researchers", key="btn_technical", use_container_width=True):
        st.session_state.insight_mode = 'technical'

with col3:
    if st.button("📊 Complete\n\nComprehensive hybrid report", key="btn_complete", use_container_width=True):
        st.session_state.insight_mode = 'complete'

# Default mode
if 'insight_mode' not in st.session_state:
    st.session_state.insight_mode = 'simple'

# Show current mode with description
mode_info = {
    'simple': {
        'label': "📖 Simple Explanations",
        'desc': "Plain language, visual indicators, real-world context",
        'audience': "For: Government officials, NGO managers, journalists, general public",
        'color': "#8b5cf6"
    },
    'technical': {
        'label': "🔬 Technical Analysis",
        'desc': "Statistical metrics, methodology notes, confidence levels",
        'audience': "For: Researchers, economists, data scientists, policy analysts",
        'color': "#ec4899"
    },
    'complete': {
        'label': "📊 Complete Report",
        'desc': "Executive summary + statistical details + policy implications",
        'audience': "For: Mixed audiences, presentations, published reports",
        'color': "#06b6d4"
    }
}

current_mode = mode_info[st.session_state.insight_mode]

st.markdown(f"""
<div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(236, 72, 153, 0.05)); border: 1px solid {current_mode['color']}66; border-radius: 12px; padding: 1rem; margin: 1rem 0;">
    <div style="color: {current_mode['color']}; font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem;">
        {current_mode['label']}
    </div>
    <div style="color: #e2e8f0; font-size: 0.9rem; margin-bottom: 0.3rem;">
        {current_mode['desc']}
    </div>
    <div style="color: #94a3b8; font-size: 0.85rem;">
        {current_mode['audience']}
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ═══════════════════════════════════════════════════════════════════
# SIDEBAR - CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.header("🎛️ Analysis Configuration")
    
    st.subheader("Current Selection")
    
    num_countries = len(config['countries'])
    country_display = ', '.join(config['countries'][:3])
    if num_countries > 3:
        country_display += f" (+{num_countries - 3} more)"
    
    st.markdown(f"""
    **Countries:** {country_display}  
    **Total:** {num_countries} countries
    
    **Indicator:** {config['indicator'].replace('_', ' ').title()}
    
    **Years:** {config['year_range'][0]}–{config['year_range'][1]}  
    **Span:** {config['year_range'][1] - config['year_range'][0]} years
    """)
    
    st.divider()
    
    st.subheader("💡 Mode Guide")
    
    with st.expander("📖 Simple Mode"):
        st.markdown("""
        **What you get:**
        - Plain language summaries
        - Emoji status indicators
        - Real-world interpretation
        - Color-coded cards
        - No statistical jargon
        
        **Best for:**
        - Quick briefings
        - Non-technical stakeholders
        - Executive summaries
        """)
    
    with st.expander("🔬 Technical Mode"):
        st.markdown("""
        **What you get:**
        - Statistical test results
        - R², p-values, confidence levels
        - Methodology notes
        - Data quality metrics
        - Precise numbers
        
        **Best for:**
        - Academic papers
        - Peer review
        - Technical reports
        """)
    
    with st.expander("📊 Complete Mode"):
        st.markdown("""
        **What you get:**
        - Executive summary
        - Statistical details
        - Policy implications
        - Caveats and limitations
        - Everything combined
        
        **Best for:**
        - Comprehensive reports
        - Mixed audiences
        - Thesis documentation
        """)
    
    st.divider()
    
    if st.button("🔄 Refresh Insights", use_container_width=True):
        st.rerun()

# ═══════════════════════════════════════════════════════════════════
# GENERATE INSIGHTS
# ═══════════════════════════════════════════════════════════════════

with st.spinner("🔍 Computing insights..."):
    insights = generate_multimode_insights(
        df,
        config['countries'],
        config['indicator'],
        config['year_range']
    )

# ═══════════════════════════════════════════════════════════════════
# DISPLAY INSIGHTS
# ═══════════════════════════════════════════════════════════════════

mode = st.session_state.insight_mode

if mode == 'simple':
    # ═══════════════════════════════════════════════════════════════
    # SIMPLE MODE DISPLAY
    # ═══════════════════════════════════════════════════════════════
    
    st.markdown("### 📋 Key Findings")
    
    if not insights['simple']:
        st.warning("No insights available for current selection.")
    else:
        for insight in insights['simple']:
            if insight['type'] == 'warning':
                st.warning(f"⚠️ {insight['message']}")
                continue
            
            # Determine card color
            card_class = f"insight-card-{insight['color']}"
            
            # Create card HTML
            st.markdown(f"""
            <div class="insight-card {card_class}">
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                    <div style="font-size: 3rem;">{insight['emoji']}</div>
                    <div>
                        <div style="font-size: 1.5rem; font-weight: 800; color: #ffffff; margin-bottom: 0.3rem;">
                            {insight['headline']}
                        </div>
                        <div style="font-size: 0.85rem; color: #94a3b8;">
                            {config['indicator'].replace('_', ' ').title()}
                        </div>
                    </div>
                </div>
                
                <div style="color: #e2e8f0; font-size: 1rem; margin-bottom: 1rem; line-height: 1.6;">
                    <strong>What's happening:</strong> {insight['summary']}
                </div>
                
                <div style="color: #e2e8f0; font-size: 0.95rem; margin-bottom: 1rem;">
                    {'✅' if insight['sentiment'] == 'positive' else '🔴' if insight['sentiment'] == 'negative' else 'ℹ️'} 
                    <strong>{'Good news:' if insight['sentiment'] == 'positive' else 'Concern:' if insight['sentiment'] == 'negative' else 'Status:'}</strong> 
                    {insight['context']}
                </div>
                
                <div style="background: rgba(0, 0, 0, 0.3); border-radius: 8px; padding: 0.8rem; color: #e2e8f0; font-size: 0.9rem;">
                    📊 <strong>Current level:</strong> {insight['current_level']}
                </div>
                
                <div style="margin-top: 1rem; display: flex; gap: 1rem; font-size: 0.85rem; color: #94a3b8;">
                    <span>📈 {insight['first_value']:.1f} ({config['year_range'][0]}) → {insight['last_value']:.1f} ({config['year_range'][1]})</span>
                    <span>|</span>
                    <span>Change: {abs(insight['change_pct']):.1f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif mode == 'technical':
    # ═══════════════════════════════════════════════════════════════
    # TECHNICAL MODE DISPLAY
    # ═══════════════════════════════════════════════════════════════
    
    st.markdown("### 🔬 Statistical Analysis")
    
    if not insights['technical']:
        st.warning("No insights available for current selection.")
    else:
        for insight in insights['technical']:
            st.markdown(f"#### {insight['country'].upper()}: {insight['indicator'].replace('_', ' ').title()}")
            
            # Summary metrics row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Change",
                    f"{insight['change_relative']:+.1f}%",
                    f"{insight['change_absolute']:+.2f} pts"
                )
            
            with col2:
                st.metric(
                    "Trend Strength",
                    insight['trend_strength'],
                    f"R² = {insight['r_squared']:.3f}"
                )
            
            with col3:
                st.metric(
                    "Volatility",
                    insight['volatility_level'],
                    f"CV = {insight['cv']:.1f}%"
                )
            
            with col4:
                st.metric(
                    "Data Quality",
                    f"{insight['completeness_pct']:.0f}%",
                    insight['confidence']
                )
            
            # Detailed statistics in expandable
            with st.expander("📊 Detailed Statistics", expanded=False):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown("**Core Statistics:**")
                    st.write(f"- First value ({insight['first_year']}): **{insight['first_value']:.2f}**")
                    st.write(f"- Last value ({insight['last_year']}): **{insight['last_value']:.2f}**")
                    st.write(f"- Absolute change: **{insight['change_absolute']:+.2f}** points")
                    st.write(f"- Relative change: **{insight['change_relative']:+.1f}%**")
                    st.write(f"- Annual rate: **{insight['annual_rate']:+.3f}** points/year")
                    
                    st.markdown("**Trend Analysis:**")
                    st.write(f"- Linear regression R²: **{insight['r_squared']:.3f}**")
                    st.write(f"- Slope coefficient: **{insight['slope']:.4f}**")
                    st.write(f"- p-value: **{insight['p_value']:.4f}**")
                    st.write(f"- Significance: **{insight['significance']}**")
                    st.write(f"- Trend strength: **{insight['trend_strength']}**")
                
                with col_b:
                    st.markdown("**Variability:**")
                    st.write(f"- Standard deviation: **{insight['std_dev']:.3f}**")
                    st.write(f"- Coefficient of variation: **{insight['cv']:.1f}%**")
                    st.write(f"- Volatility level: **{insight['volatility_level']}**")
                    
                    st.markdown("**Data Quality:**")
                    st.write(f"- Completeness: **{insight['completeness_pct']:.0f}%**")
                    st.write(f"- Observations: **{insight['observations']}/{insight['expected_obs']}** years")
                    st.write(f"- Confidence rating: **{insight['confidence']}**")
                    
                    st.markdown("**Regional Position:**")
                    st.write(f"- Current rank: **{insight['current_rank']} of {insight['total_countries']}**")
                    percentile = ((insight['total_countries'] - insight['current_rank'] + 1) / insight['total_countries'] * 100)
                    st.write(f"- Percentile: **{percentile:.0f}th**")
                
                st.markdown("**Methodology Note:**")
                st.caption(
                    "Trend calculated using ordinary least squares (OLS) linear regression. "
                    "Volatility measured as coefficient of variation (Yitzhaki 1982). "
                    "Statistical significance tested at α = 0.05 level. "
                    "Data completeness calculated as proportion of expected annual observations."
                )
            
            st.divider()

else:  # complete mode
    # ═══════════════════════════════════════════════════════════════
    # COMPLETE MODE DISPLAY
    # ═══════════════════════════════════════════════════════════════
    
    st.markdown("### 📊 Comprehensive Analysis")
    
    if not insights['complete']:
        st.warning("No insights available for current selection.")
    else:
        for idx, insight in enumerate(insights['complete'], 1):
            country = insight['simple']['country']
            
            with st.expander(f"**{idx}. {country.upper()}** - Full Report", expanded=(idx == 1)):
                # Executive summary
                st.markdown("#### 🎯 Executive Summary")
                
                if insight['simple']['sentiment'] == 'positive':
                    st.success(insight['simple']['summary'])
                elif insight['simple']['sentiment'] == 'negative':
                    st.error(insight['simple']['summary'])
                else:
                    st.info(insight['simple']['summary'])
                
                # Synthesis
                st.markdown("#### 📖 Comprehensive Analysis")
                st.markdown(insight['synthesis'])
                
                # Key metrics
                st.markdown("#### 📊 Key Metrics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                tech = insight['technical']
                
                with col1:
                    st.metric(
                        "Total Change",
                        f"{tech['change_relative']:+.1f}%",
                        f"{tech['change_absolute']:+.2f} points"
                    )
                
                with col2:
                    st.metric(
                        "Statistical Fit",
                        f"R² = {tech['r_squared']:.3f}",
                        tech['trend_strength']
                    )
                
                with col3:
                    st.metric(
                        "Significance",
                        "Yes" if tech['p_value'] < 0.05 else "No",
                        tech['significance']
                    )
                
                with col4:
                    st.metric(
                        "Rank",
                        f"#{tech['current_rank']}",
                        f"of {tech['total_countries']}"
                    )
                
                # Caveats
                st.markdown("#### ⚠️ Important Caveats")
                for caveat in insight['caveats']:
                    st.markdown(caveat)
                
                # Policy implications
                st.markdown("#### 💡 Policy Implications")
                st.info(insight['policy_implications'])
                
                # Technical details (collapsed)
                with st.expander("🔬 Full Statistical Details"):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.markdown("**Values & Changes:**")
                        st.write(f"- {tech['first_year']}: {tech['first_value']:.2f}")
                        st.write(f"- {tech['last_year']}: {tech['last_value']:.2f}")
                        st.write(f"- Absolute: {tech['change_absolute']:+.2f}")
                        st.write(f"- Relative: {tech['change_relative']:+.1f}%")
                        st.write(f"- Annual: {tech['annual_rate']:+.3f}/year")
                        
                        st.markdown("**Trend:**")
                        st.write(f"- R²: {tech['r_squared']:.4f}")
                        st.write(f"- Slope: {tech['slope']:.4f}")
                        st.write(f"- p-value: {tech['p_value']:.4f}")
                    
                    with col_b:
                        st.markdown("**Volatility:**")
                        st.write(f"- σ: {tech['std_dev']:.3f}")
                        st.write(f"- CV: {tech['cv']:.1f}%")
                        st.write(f"- Level: {tech['volatility_level']}")
                        
                        st.markdown("**Data:**")
                        st.write(f"- Complete: {tech['completeness_pct']:.0f}%")
                        st.write(f"- N: {tech['observations']}/{tech['expected_obs']}")
                        st.write(f"- Quality: {tech['confidence']}")

# ═══════════════════════════════════════════════════════════════════
# EXPORT SECTION
# ═══════════════════════════════════════════════════════════════════

st.divider()
st.markdown("### 📥 Export Insights")

col1, col2, col3 = st.columns(3)

with col1:
    txt_content = format_insights_as_text(insights, mode)
    st.download_button(
        label="📄 Download as TXT",
        data=txt_content,
        file_name=f"insights_{mode}_{config['indicator']}_{config['year_range'][0]}-{config['year_range'][1]}.txt",
        mime="text/plain",
        use_container_width=True
    )

with col2:
    # Markdown format
    md_content = txt_content.replace("=", "#")
    st.download_button(
        label="📝 Download as Markdown",
        data=md_content,
        file_name=f"insights_{mode}_{config['indicator']}_{config['year_range'][0]}-{config['year_range'][1]}.md",
        mime="text/markdown",
        use_container_width=True
    )

with col3:
    if st.button("📋 Copy to Clipboard", use_container_width=True):
        st.code(txt_content, language="text")
        st.success("✅ Text shown above - use your browser's copy function")

# ═══════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════

st.divider()

st.markdown("""
<div style="text-align: center; padding: 2rem 0; border-top: 1px solid rgba(148, 163, 184, 0.1);">
    <p style="color: #64748b; font-size: 0.85rem; margin: 0;">
        <strong style="color: #8b5cf6;">Multi-Mode Insights Engine</strong> • 100% Reliable • Zero AI Dependencies
    </p>
    <p style="color: #475569; font-size: 0.75rem; margin-top: 0.5rem;">
        Pure Python statistical analysis • Adapts to your audience • Always available
    </p>
</div>
""", unsafe_allow_html=True)