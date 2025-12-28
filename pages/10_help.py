import streamlit as st

st.set_page_config(
    page_title="Help & Documentation",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide sidebar navigation
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* Main styling */
    .main {
        background: linear-gradient(180deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Typography */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    p, span, div, label {
        color: #e2e8f0;
    }
    
    /* Hero section */
    .hero-section {
        text-align: center;
        padding: 60px 20px 80px 20px;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(59, 130, 246, 0.1));
        border-radius: 16px;
        margin-bottom: 60px;
        border: 1px solid rgba(139, 92, 246, 0.3);
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #8b5cf6, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 16px;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: #94a3b8;
        max-width: 700px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    /* Category sections */
    .category-header {
        font-size: 1.75rem;
        font-weight: 700;
        color: #ffffff;
        margin: 48px 0 24px 0;
        padding-bottom: 12px;
        border-bottom: 2px solid rgba(59, 130, 246, 0.3);
    }
    
    /* Help cards */
    .help-card {
        background: linear-gradient(135deg, #0f1419, #1a1f2e);
        border: 1px solid rgba(100, 116, 139, 0.3);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .help-card:hover {
        border-color: rgba(59, 130, 246, 0.6);
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.2);
        transform: translateY(-2px);
    }
    
    .card-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        margin-bottom: 16px;
    }
    
    .card-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 8px;
    }
    
    .card-description {
        font-size: 0.95rem;
        color: #94a3b8;
        line-height: 1.6;
    }
    
    /* Feature list */
    .feature-list {
        list-style: none;
        padding: 0;
        margin: 16px 0;
    }
    
    .feature-item {
        padding: 8px 0;
        color: #e2e8f0;
        font-size: 0.95rem;
    }
    
    .feature-item:before {
        content: "→";
        color: #3b82f6;
        font-weight: bold;
        margin-right: 12px;
    }
    
    /* Info boxes */
    .info-box {
        background: rgba(59, 130, 246, 0.1);
        border-left: 4px solid #3b82f6;
        padding: 16px 20px;
        border-radius: 8px;
        margin: 20px 0;
    }
    
    .warning-box {
        background: rgba(245, 158, 11, 0.1);
        border-left: 4px solid #f59e0b;
        padding: 16px 20px;
        border-radius: 8px;
        margin: 20px 0;
    }
    
    .success-box {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
        padding: 16px 20px;
        border-radius: 8px;
        margin: 20px 0;
    }
    
    /* Quick links */
    .quick-link {
        display: inline-block;
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 8px 16px;
        border-radius: 8px;
        margin: 4px;
        color: #3b82f6;
        font-weight: 600;
        font-size: 0.9rem;
        text-decoration: none;
        transition: all 0.3s ease;
    }
    
    .quick-link:hover {
        background: rgba(59, 130, 246, 0.2);
        border-color: rgba(59, 130, 246, 0.5);
    }
    
    /* Code blocks */
    .code-block {
        background: #0a0e27;
        border: 1px solid rgba(100, 116, 139, 0.3);
        border-radius: 8px;
        padding: 16px;
        font-family: monospace;
        font-size: 0.9rem;
        color: #e2e8f0;
        margin: 16px 0;
        overflow-x: auto;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1));
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #3b82f6;
        margin-bottom: 8px;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #94a3b8;
    }
    
    /* Contact section */
    .contact-card {
        background: linear-gradient(135deg, #1a1f2e, #0f1419);
        border: 1px solid rgba(139, 92, 246, 0.4);
        border-radius: 16px;
        padding: 32px;
        margin-top: 48px;
        text-align: center;
    }
    
    .contact-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 16px;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(15, 20, 25, 0.6);
        border: 1px solid rgba(100, 116, 139, 0.3);
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 600;
        padding: 12px 24px;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(59, 130, 246, 0.1);
        border-color: rgba(59, 130, 246, 0.5);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(139, 92, 246, 0.2));
        border-color: #3b82f6;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# Top Navigation
col1, col2, col3 = st.columns([6, 1, 1])

with col2:
    if st.button("Home", use_container_width=True):
        st.switch_page("home.py")

with col3:
    if st.button("Dashboard", use_container_width=True):
        st.switch_page("pages/1_dashboard.py")

# Hero Section
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">Help & Documentation</h1>
    <p class="hero-subtitle">
        Comprehensive guide to analyzing South Asia income inequality data, 
        understanding metrics, and using our analytical tools effectively
    </p>
</div>
""", unsafe_allow_html=True)

# Quick Stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">8</div>
        <div class="metric-label">Countries Analyzed</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">20+</div>
        <div class="metric-label">Years of Data</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">10+</div>
        <div class="metric-label">Indicators</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">5</div>
        <div class="metric-label">Analysis Tools</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Main Content
tab1, tab2, tab3, tab4 = st.tabs(["Getting Started", "Core Metrics", "Analysis Tools", "Data & Methods"])

with tab1:
    st.markdown('<h2 class="category-header">Platform Overview</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="help-card">
            <div class="card-icon">1</div>
            <div class="card-title">What This Platform Does</div>
            <div class="card-description">
                Analyzes income inequality across South Asian countries using authoritative data from 
                World Bank and UNDP. Provides interactive visualizations, statistical insights, and 
                comparative analysis tools for researchers, policymakers, and students.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="help-card">
            <div class="card-icon">3</div>
            <div class="card-title">Explore Visualizations</div>
            <div class="card-description">
                Navigate through different analytical views:
            </div>
            <ul class="feature-list">
                <li class="feature-item">Auto Insights: Pattern detection</li>
                <li class="feature-item">Dashboard: Multi-metric overview</li>
                <li class="feature-item">Map Analysis: Geographic distributions</li>
                <li class="feature-item">Correlations: Statistical relationships</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="help-card">
            <div class="card-icon">2</div>
            <div class="card-title">How to Get Started</div>
            <ul class="feature-list">
                <li class="feature-item">Open any analysis page directly (works with defaults)</li>
                <li class="feature-item">Or configure on Home page for custom analysis</li>
                <li class="feature-item">Select countries, years, and indicators</li>
                <li class="feature-item">Explore insights and export results</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="help-card">
            <div class="card-icon">4</div>
            <div class="card-title">Export & Share</div>
            <div class="card-description">
                Download your findings in multiple formats:
            </div>
            <ul class="feature-list">
                <li class="feature-item">TXT: Plain text reports</li>
                <li class="feature-item">Markdown: Technical documentation</li>
                <li class="feature-item">CSV: Spreadsheet analysis</li>
                <li class="feature-item">Charts: High-resolution images</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<h2 class="category-header">Quick Tips</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>For Best Results:</strong><br>
        Start with 2-3 countries for clearer comparisons. Use the period 2010-2024 for most complete data. 
        Enable statistical details in Auto Insights for deeper analysis. Check Data Quality page to understand limitations.
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown('<h2 class="category-header">Understanding Inequality Metrics</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="help-card">
            <div class="card-title">GINI Coefficient</div>
            <div class="card-description">
                <strong style="color: #ffffff;">What it measures:</strong> Income inequality within a population
                <br><br>
                <strong style="color: #ffffff;">Scale:</strong> 0 to 100 (or 0 to 1)
            </div>
            <ul class="feature-list">
                <li class="feature-item">0 = Perfect equality (everyone has same income)</li>
                <li class="feature-item">100 = Perfect inequality (one person has everything)</li>
            </ul>
            <div class="card-description">
                <strong style="color: #ffffff;">Interpretation:</strong>
            </div>
            <ul class="feature-list">
                <li class="feature-item">Below 30: Low inequality (Nordic countries)</li>
                <li class="feature-item">30-35: Moderate (most developed countries)</li>
                <li class="feature-item">35-40: Medium-high</li>
                <li class="feature-item">40-50: High (most South Asian countries)</li>
                <li class="feature-item">Above 50: Very high (South Africa, Brazil)</li>
            </ul>
            <div class="card-description">
                <strong style="color: #ffffff;">Example:</strong> Bangladesh GINI of 32.4 means moderate inequality - income is more evenly distributed than in India (35.7) but less equal than Sri Lanka (30.1).
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="help-card">
            <div class="card-title">GDP & GDP per Capita</div>
            <div class="card-description">
                <strong style="color: #ffffff;">GDP (Gross Domestic Product):</strong> Total value of all goods and services produced. Measured in current US dollars.
                <br><br>
                <strong style="color: #ffffff;">GDP per Capita:</strong> GDP divided by population. Average income per person.
                <br><br>
                <strong style="color: #ffffff;">Important:</strong> High GDP doesn't mean low inequality. A country can be wealthy overall but have high inequality (e.g., United States).
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="help-card">
            <div class="card-title">Human Development Index (HDI)</div>
            <div class="card-description">
                <strong style="color: #ffffff;">What it measures:</strong> Overall human development across 3 dimensions
                <br><br>
                <strong style="color: #ffffff;">Components:</strong>
            </div>
            <ul class="feature-list">
                <li class="feature-item">Health: Life expectancy at birth</li>
                <li class="feature-item">Education: Expected & mean years of schooling</li>
                <li class="feature-item">Standard of living: GNI per capita</li>
            </ul>
            <div class="card-description">
                <strong style="color: #ffffff;">Scale:</strong> 0.0 to 1.0
            </div>
            <ul class="feature-list">
                <li class="feature-item">Below 0.550: Low development</li>
                <li class="feature-item">0.550-0.699: Medium development</li>
                <li class="feature-item">0.700-0.799: High development</li>
                <li class="feature-item">0.800+: Very high development</li>
            </ul>
            <div class="card-description">
                <strong style="color: #ffffff;">Key Insight:</strong> HDI shows development level, GINI shows inequality. A country can be highly developed but still have high inequality.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="help-card">
            <div class="card-title">Poverty Headcount</div>
            <div class="card-description">
                <strong style="color: #ffffff;">Definition:</strong> Percentage of population living below poverty line
                <br><br>
                <strong style="color: #ffffff;">Common thresholds:</strong>
            </div>
            <ul class="feature-list">
                <li class="feature-item">$2.15/day: Extreme poverty (World Bank)</li>
                <li class="feature-item">$3.65/day: Lower-middle income poverty</li>
                <li class="feature-item">$6.85/day: Upper-middle income poverty</li>
            </ul>
            <div class="card-description">
                <strong style="color: #ffffff;">Note:</strong> Complementary to GINI. A country can have low poverty but high inequality (e.g., China).
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<h2 class="category-header">Statistical Concepts</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="help-card">
            <div class="card-title">Correlation</div>
            <div class="card-description">
                Measures relationship between two variables.
                <br><br>
                <strong style="color: #ffffff;">Range:</strong> -1 to +1
            </div>
            <ul class="feature-list">
                <li class="feature-item">-1: Perfect negative</li>
                <li class="feature-item">0: No relationship</li>
                <li class="feature-item">+1: Perfect positive</li>
            </ul>
            <div class="card-description">
                <strong style="color: #ffffff;">Strength:</strong>
            </div>
            <ul class="feature-list">
                <li class="feature-item">0.7-1.0: Strong</li>
                <li class="feature-item">0.4-0.7: Moderate</li>
                <li class="feature-item">0.0-0.4: Weak</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="help-card">
            <div class="card-title">P-Value</div>
            <div class="card-description">
                Probability results occurred by chance.
                <br><br>
                <strong style="color: #ffffff;">Interpretation:</strong>
            </div>
            <ul class="feature-list">
                <li class="feature-item">p < 0.05: Statistically significant</li>
                <li class="feature-item">p ≥ 0.05: Not significant</li>
            </ul>
            <div class="card-description">
                <strong style="color: #ffffff;">Example:</strong> p = 0.03 means only 3% chance the correlation is random.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="help-card">
            <div class="card-title">R-Squared (R²)</div>
            <div class="card-description">
                How well data fits a trend line.
                <br><br>
                <strong style="color: #ffffff;">Range:</strong> 0 to 1
            </div>
            <ul class="feature-list">
                <li class="feature-item">0.7-1.0: Strong fit</li>
                <li class="feature-item">0.4-0.7: Moderate fit</li>
                <li class="feature-item">0.0-0.4: Weak fit</li>
            </ul>
            <div class="card-description">
                Higher R² = more predictable relationship.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="warning-box">
        <strong>Critical Reminder:</strong> Correlation does NOT equal causation. 
        Just because two variables move together doesn't mean one causes the other. 
        Always consider alternative explanations and confounding factors.
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.markdown('<h2 class="category-header">Analysis Tools & Features</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="help-card">
        <div class="card-title">Auto Insights Pro</div>
        <div class="card-description">
            <strong>Purpose:</strong> Pattern detection and statistical analysis<br><br>
            <strong>Key Features:</strong>
        </div>
        <ul class="feature-list">
            <li class="feature-item">Automated insight generation ranked by statistical importance (0-25 score)</li>
            <li class="feature-item">Trend analysis with regression lines and confidence bands</li>
            <li class="feature-item">Country rankings with year-over-year changes</li>
            <li class="feature-item">Distribution analysis across inequality categories</li>
            <li class="feature-item">Anomaly detection using Z-score analysis (threshold: 2.0)</li>
            <li class="feature-item">Forecasting based on historical trends</li>
        </ul>
        <div class="card-description">
            <strong>Sidebar Controls:</strong><br>
            • Analysis Depth: Quick (8), Detailed (15), Expert (25) insights<br>
            • Insight Types: Filter by trends, rankings, anomalies, statistics, etc.<br>
            • Focus Mode: Deep dive on 2-3 countries with best data quality<br>
            • Display Options: Toggle statistical details and confidence indicators
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="help-card">
            <div class="card-title">Dashboard</div>
            <div class="card-description">
                <strong>Purpose:</strong> Comprehensive multi-metric overview<br><br>
                <strong>Features:</strong>
            </div>
            <ul class="feature-list">
                <li class="feature-item">Summary metrics with trend indicators</li>
                <li class="feature-item">Temporal trends (line charts, area charts)</li>
                <li class="feature-item">Country comparisons (bar charts, rankings)</li>
                <li class="feature-item">Distribution analysis (histograms, box plots)</li>
                <li class="feature-item">Raw data tables with sorting and filtering</li>
            </ul>
            <div class="card-description">
                <strong>Best For:</strong> Getting a comprehensive overview of all selected metrics at once.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="help-card">
            <div class="card-title">Correlation Analysis</div>
            <div class="card-description">
                <strong>Purpose:</strong> Explore statistical relationships between indicators<br><br>
                <strong>Features:</strong>
            </div>
            <ul class="feature-list">
                <li class="feature-item">Correlation matrix heatmap with color coding</li>
                <li class="feature-item">Scatter plots with regression lines</li>
                <li class="feature-item">P-values for significance testing</li>
                <li class="feature-item">R² values for model fit assessment</li>
            </ul>
            <div class="card-description">
                <strong>Interpretation:</strong><br>
                Green cells (p < 0.05) = statistically significant<br>
                Red cells = not significant, may be random
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="help-card">
            <div class="card-title">Map Analysis</div>
            <div class="card-description">
                <strong>Purpose:</strong> Visualize geographic distribution and patterns<br><br>
                <strong>Features:</strong>
            </div>
            <ul class="feature-list">
                <li class="feature-item">Animated choropleth maps showing changes over time</li>
                <li class="feature-item">Interactive timeline slider</li>
                <li class="feature-item">Hover for country-specific details</li>
                <li class="feature-item">Color scales indicating inequality levels</li>
                <li class="feature-item">Geographic clustering identification</li>
            </ul>
            <div class="card-description">
                <strong>Tips:</strong> Use animation to see temporal evolution. 
                Look for regional patterns and cross-border similarities.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="help-card">
            <div class="card-title">Data Quality Dashboard</div>
            <div class="card-description">
                <strong>Purpose:</strong> Assess data availability and reliability<br><br>
                <strong>Features:</strong>
            </div>
            <ul class="feature-list">
                <li class="feature-item">Completeness percentages by country and indicator</li>
                <li class="feature-item">Missing data visualization (gap identification)</li>
                <li class="feature-item">Source information and update dates</li>
                <li class="feature-item">Quality scores and reliability indicators</li>
            </ul>
            <div class="card-description">
                <strong>When to Use:</strong> Before making conclusions, check data quality. 
                High quality = 80%+ completeness. Note any gaps in your analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>Pro Tip:</strong> Use Auto Insights for quick patterns, Dashboard for comprehensive overview, 
        Correlations for relationships, and Map for geographic context. Each tool complements the others.
    </div>
    """, unsafe_allow_html=True)

with tab4:
    st.markdown('<h2 class="category-header">Data Sources & Methodology</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="help-card">
            <div class="card-title">Primary Data Sources</div>
            <div class="card-description">
                <p style="color: #ffffff; font-weight: 600; margin-bottom: 8px;">World Bank</p>
                <ul class="feature-list">
                    <li class="feature-item">Poverty and Inequality Database</li>
                    <li class="feature-item">World Development Indicators</li>
                    <li class="feature-item">Updated annually (1-2 year lag)</li>
                    <li class="feature-item">Peer-reviewed and internationally recognized</li>
                </ul>
                <p style="color: #ffffff; font-weight: 600; margin-bottom: 8px; margin-top: 16px;">United Nations Development Programme (UNDP)</p>
                <ul class="feature-list">
                    <li class="feature-item">Human Development Report</li>
                    <li class="feature-item">Published annually in March</li>
                    <li class="feature-item">Composite indices (HDI, GII, MPI)</li>
                    <li class="feature-item">Global coverage with methodological notes</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="help-card">
            <div class="card-title">Data Processing</div>
            <div class="card-description">
                <p style="color: #ffffff; font-weight: 600; margin-bottom: 8px;">What We Do:</p>
            </div>
            <ul class="feature-list">
                <li class="feature-item">Aggregate data from authoritative sources</li>
                <li class="feature-item">Standardize units and formats</li>
                <li class="feature-item">Validate consistency across years</li>
                <li class="feature-item">Calculate derived metrics (per capita, growth rates)</li>
            </ul>
            <div class="card-description">
                <p style="color: #ffffff; font-weight: 600; margin-bottom: 8px; margin-top: 16px;">What We Don't Do:</p>
                <ul class="feature-list">
                    <li class="feature-item">Estimate or impute missing data</li>
                    <li class="feature-item">Adjust for methodology changes</li>
                    <li class="feature-item">Modify original values</li>
                </ul>
                <p style="color: #e2e8f0; margin-top: 12px;">All gaps represent actual data unavailability to preserve integrity.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="help-card">
            <div class="card-title">Coverage & Limitations</div>
            <div class="card-description">
                <p style="color: #ffffff; font-weight: 600; margin-bottom: 8px;">Geographic Coverage:</p>
                <p style="color: #e2e8f0; margin-bottom: 16px;">
                    8 South Asian countries (Bangladesh, Bhutan, India, Maldives, Nepal, Pakistan, Sri Lanka, Afghanistan)
                </p>
                <p style="color: #ffffff; font-weight: 600; margin-bottom: 8px;">Temporal Coverage:</p>
                <p style="color: #e2e8f0; margin-bottom: 16px;">
                    2000-2024, with varying completeness by indicator
                </p>
                <p style="color: #ffffff; font-weight: 600; margin-bottom: 8px;">Data Gaps:</p>
                <ul class="feature-list">
                    <li class="feature-item">Not all countries conduct surveys annually</li>
                    <li class="feature-item">Some indicators require expensive national surveys</li>
                    <li class="feature-item">Political instability disrupts collection</li>
                    <li class="feature-item">Methodology changes create discontinuities</li>
                </ul>
            </div>
            <div class="info-box" style="margin: 16px 24px 24px 24px;">
                <strong>Always check Data Quality page before drawing conclusions.</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="help-card">
            <div class="card-title">Statistical Methods</div>
            <div class="card-description">
                <p style="color: #ffffff; font-weight: 600; margin-bottom: 8px;">Auto Insights Engine:</p>
                <ul class="feature-list">
                    <li class="feature-item">Linear regression (scipy.stats.linregress)</li>
                    <li class="feature-item">Z-score anomaly detection (threshold: 2.0 standard deviations)</li>
                    <li class="feature-item">Confidence intervals (95% level)</li>
                    <li class="feature-item">Trend strength classification by R²</li>
                    <li class="feature-item">P-value significance testing (α = 0.05)</li>
                </ul>
                <p style="color: #ffffff; font-weight: 600; margin-bottom: 8px; margin-top: 16px;">Scoring Algorithm:</p>
                <p style="color: #e2e8f0; margin-bottom: 8px;">Multi-factor scoring (0-25 points):</p>
                <ul class="feature-list">
                    <li class="feature-item">Statistical significance (p < 0.05): +5</li>
                    <li class="feature-item">Large magnitude (>20% change): +4</li>
                    <li class="feature-item">Anomaly detected: +4</li>
                    <li class="feature-item">High data quality (>80%): +2</li>
                    <li class="feature-item">Strong R² (>0.7): +3</li>
                    <li class="feature-item">Additional factors: +1-4 per type</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<h2 class="category-header">Using This Platform for Research</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="success-box">
        <strong>This platform is designed for academic and policy research.</strong> You may use it for 
        theses, dissertations, research papers, policy briefs, and educational purposes.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="help-card">
        <div class="card-title">Citation Format</div>
        <div class="code-block">
Mehzabeen, S., Sultana, S., Mayami, A,&  Mafiz, T. (2025). 
South Asia Income Inequality Analysis Platform. 
BRAC University, Department of Computer Science and Engineering.

Data Sources:
• World Bank. (2024). Poverty and Inequality Database. 
  https://pip.worldbank.org/
• UNDP. (2024). Human Development Report 2024. 
  https://hdr.undp.org/
        </div>
        <div class="card-description">
            <strong>Important:</strong> Also cite the original data sources (World Bank, UNDP) 
            in your bibliography. This platform is a visualization tool, not the primary source.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="help-card">
            <div class="card-title">Best Practices</div>
            <ul class="feature-list">
                <li class="feature-item">Check Data Quality page before analysis</li>
                <li class="feature-item">Note data gaps and limitations in your work</li>
                <li class="feature-item">Use multiple indicators for comprehensive view</li>
                <li class="feature-item">Compare with other regional contexts</li>
                <li class="feature-item">Consider socio-political context</li>
                <li class="feature-item">Verify findings with primary sources</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="help-card">
            <div class="card-title">License & Usage</div>
            <div class="card-description">
                <p style="color: #ffffff; font-weight: 600; margin-bottom: 8px;">Data License:</p>
                <ul class="feature-list">
                    <li class="feature-item">World Bank: CC BY 4.0</li>
                    <li class="feature-item">UNDP: Open Data Commons</li>
                    <li class="feature-item">Free to use with attribution</li>
                </ul>
                <p style="color: #ffffff; font-weight: 600; margin-bottom: 8px; margin-top: 16px;">Platform Code:</p>
                <ul class="feature-list">
                    <li class="feature-item">Educational/research use permitted</li>
                    <li class="feature-item">Attribution required</li>
                    <li class="feature-item">Commercial use: Contact authors</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Contact Section
st.markdown("""
<div class="contact-card">
    <h2 class="contact-title">Need Additional Support?</h2>
    <p style="color: #94a3b8; font-size: 1.05rem; margin-bottom: 24px;">
        This platform is a thesis project by Computer Science & Engineering students at BRAC University
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="help-card">
        <div class="card-title">Technical Issues</div>
        <div class="card-description">
            Check Data Quality page for coverage information. 
            Most issues are due to actual data gaps, not technical errors.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="help-card">
        <div class="card-title">Research Questions</div>
        <div class="card-description">
            Refer to methodology section above. For deeper questions, 
            consult original sources (World Bank, UNDP documentation).
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="help-card">
        <div class="card-title">Feature Requests</div>
        <div class="card-description">
            This is an academic project. Features are frozen for thesis submission. 
            Future updates may be considered post-defense.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.divider()
st.caption("Help & Documentation | South Asia Income Inequality Analysis Platform | ")