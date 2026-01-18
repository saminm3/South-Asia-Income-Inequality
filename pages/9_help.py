import streamlit as st
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))


from utils.help_content import HELP_CONTENT
from utils.sidebar import apply_all_styles


st.set_page_config(
    page_title="Help & Documentation | SA Inequality Analytics",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

apply_all_styles()

# Custom CSS for help page
st.markdown("""
<style>
    /* Hero section */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 60px 40px;
        border-radius: 20px;
        margin-bottom: 40px;
        text-align: center;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .hero-title {
        font-size: 3.5em;
        font-weight: 800;
        color: white;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .hero-subtitle {
        font-size: 1.3em;
        color: rgba(255,255,255,0.95);
        margin-bottom: 30px;
    }
    
    /* Quick nav buttons */
    .quick-nav {
        display: flex;
        gap: 15px;
        justify-content: center;
        flex-wrap: wrap;
        margin-top: 30px;
    }
    
    .nav-button {
        background: rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.3);
        padding: 12px 24px;
        border-radius: 30px;
        color: white;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.3s;
    }
    
    .nav-button:hover {
        background: rgba(255,255,255,0.3);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    
    /* Section cards */
    .help-card {
        background: linear-gradient(180deg, #1a1f3a 0%, #0f1419 100%);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 15px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    .help-card h2 {
        color: #8b5cf6;
        margin-bottom: 15px;
        font-size: 1.8em;
    }
    
    .help-card h3 {
        color: #ec4899;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    
    .help-card ul {
        color: #e2e8f0;
        line-height: 1.8;
    }
    
    .help-card li {
        margin-bottom: 10px;
    }
    
    /* Feature boxes */
    .feature-box {
        background: rgba(139, 92, 246, 0.1);
        border-left: 4px solid #8b5cf6;
        padding: 15px;
        margin: 15px 0;
        border-radius: 8px;
    }
    
    .feature-box strong {
        color: #a78bfa;
    }
    
    /* Tip boxes */
    .tip-box {
        background: rgba(236, 72, 153, 0.1);
        border-left: 4px solid #ec4899;
        padding: 15px;
        margin: 15px 0;
        border-radius: 8px;
    }
    
    /* Issue boxes */
    .issue-box {
        background: rgba(245, 158, 11, 0.1);
        border-left: 4px solid #f59e0b;
        padding: 15px;
        margin: 15px 0;
        border-radius: 8px;
    }
    
    /* Step numbers */
    .step-number {
        display: inline-block;
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        text-align: center;
        line-height: 30px;
        font-weight: bold;
        margin-right: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class='hero-section'>
    <div class='hero-title'>Help & Documentation</div>
    <div class='hero-subtitle'>
        Your comprehensive guide to analyzing income inequality across South Asia
    </div>
    <p style='color: rgba(255,255,255,0.9); font-size: 1.1em;'>
        Learn how to use every feature, discover pro tips, and troubleshoot common issues
    </p>
</div>
""", unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Quick Start", 
    "Features Guide", 
    "Troubleshooting",
    "Data Sources & Methodology"
])

# ========================================
# TAB 1: QUICK START
# ========================================
with tab1:
    st.markdown("<div class='help-card'>", unsafe_allow_html=True)
    st.markdown("## Getting Started in 3 Steps")
    
    st.markdown("""
    <div class='feature-box'>
        <span class='step-number'>1</span>
        <strong>Configure Your Analysis</strong><br>
        Go to the <strong>Home</strong> page and select:
        <ul>
            <li>Countries you want to analyze (e.g., Bangladesh, India, Pakistan)</li>
            <li>Year range (recommended: last 10-15 years for better data quality)</li>
            <li>Primary indicator (GINI index is the most common inequality measure)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-box'>
        <span class='step-number'>2</span>
        <strong>Explore Visualizations</strong><br>
        Navigate through pages using the sidebar:
        <ul>
            <li><strong>Dashboard:</strong> Overall trends and statistics</li>
            <li><strong>Map Analysis:</strong> Geographic patterns and animations</li>
            <li><strong>Correlations:</strong> Relationships between indicators</li>
            <li><strong>Other pages:</strong> Specialized analysis tools</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-box'>
        <span class='step-number'>3</span>
        <strong>Export & Share</strong><br>
        Download your findings:
        <ul>
            <li>Charts as PNG/SVG images</li>
            <li>Data as CSV/Excel files</li>
            <li>Full reports for presentations</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Navigation Tips
    st.markdown("<div class='help-card'>", unsafe_allow_html=True)
    st.markdown("## Navigation Tips")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='tip-box'>
            <strong> Keyboard Shortcuts</strong><br>
            • Click the ❓ help button on any page<br>
            • Use Smart Search (Ctrl+K) for quick navigation<br>
            • Sidebar collapses for more screen space
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='tip-box'>
            <strong> Best Practices</strong><br>
            • Start with 3-5 countries for clear visuals<br>
            • Check Data Quality page before deep analysis<br>
            • Export data early to avoid losing work
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ========================================
# TAB 2: FEATURES GUIDE
# ========================================
with tab2:
    st.markdown("## Page-by-Page Feature Guide")
    
    # List of pages to document
    pages_to_document = [
        ("home", "Home"),
        ("dashboard", "Dashboard"),
        ("map", "Map Analysis"),
        ("correlations", "Correlations"),
        ("sunburst", "Sunburst"),
        ("simulator", "Income Simulator"),
        ("quality", "Data Quality"),
        ("search", "Smart Search"),
        ("temporal", "Temporal Compare")
    ]
    
    for page_key, page_title in pages_to_document:
        page_data = HELP_CONTENT.get(page_key)
        if not page_data:
            continue
            
        with st.expander(f"### {page_title}", expanded=False):
            st.markdown(f"<div class='help-card'>", unsafe_allow_html=True)
            
            # Overview
            st.markdown(f"**Overview:** {page_data['overview']}")
            
            # Features
            if page_data.get('features'):
                st.markdown("#### Key Features")
                for feature in page_data['features']:
                    st.markdown(f"""
                    <div class='feature-box'>
                        <strong>{feature['name']}</strong><br>
                        {feature['description']}
                    </div>
                    """, unsafe_allow_html=True)
            
            # How to use
            if page_data.get('how_to_use'):
                st.markdown("#### How to Use")
                for i, step in enumerate(page_data['how_to_use'], 1):
                    st.markdown(f"{i}. {step}")
            
            # Tips
            if page_data.get('tips'):
                st.markdown("#### 💡 Pro Tips")
                for tip in page_data['tips']:
                    st.markdown(f"""
                    <div class='tip-box'>
                        💡 {tip}
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

# ========================================
# TAB 3: TROUBLESHOOTING
# ========================================
with tab3:
    st.markdown("## Troubleshooting Guide")
    
    st.markdown("<div class='help-card'>", unsafe_allow_html=True)
    st.markdown("### Common Issues & Solutions")
    
    # Collect all issues from all pages
    all_issues = []
    for page_key, page_data in HELP_CONTENT.items():
        if page_data.get('common_issues'):
            for issue in page_data['common_issues']:
                all_issues.append({
                    'page': page_key,
                    'problem': issue['problem'],
                    'solution': issue['solution']
                })
    
    # Display issues
    if all_issues:
        for i, issue in enumerate(all_issues):
            st.markdown(f"""
            <div class='issue-box'>
                <strong>❓ {issue['problem']}</strong><br>
                <span style='color: #10b981;'>✓ Solution:</span> {issue['solution']}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # General Troubleshooting
    st.markdown("<div class='help-card'>", unsafe_allow_html=True)
    st.markdown("### General Troubleshooting Steps")
    
    st.markdown("""
    <div class='feature-box'>
        <strong>1. Check Your Configuration</strong><br>
        • Go to Home page<br>
        • Verify countries are selected<br>
        • Ensure year range has data (check Data Quality page)
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-box'>
        <strong>2. Refresh the Page</strong><br>
        • Press F5 or click browser refresh<br>
        • This clears cached data and reloads visualizations
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-box'>
        <strong>3. Check Browser Compatibility</strong><br>
        • Use Chrome, Firefox, or Safari (latest versions)<br>
        • Enable JavaScript<br>
        • Clear browser cache if issues persist
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-box'>
        <strong>4. Data Quality Issues</strong><br>
        • Visit the Data Quality page<br>
        • Check completeness for your selected countries/indicators<br>
        • Gray areas on maps = missing data
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ========================================
# TAB 4: DATA SOURCES & METHODOLOGY
# ========================================
with tab4:
    st.markdown("## Data Sources & Methodology")
    
    st.markdown("<div class='help-card'>", unsafe_allow_html=True)
    st.markdown("### Primary Data Sources")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='feature-box'>
            <strong>🌍 World Bank Open Data</strong><br>
            • GDP per capita (current USD)<br>
            • Labor force participation rates<br>
            • Education indicators<br>
            • Updated: Quarterly
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='feature-box'>
            <strong>🌐 Natural Earth</strong><br>
            • Geographic boundaries (GeoJSON)<br>
            • Country polygons for mapping<br>
            • Version: 5.1.1
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='feature-box'>
            <strong>UNDP Human Development Reports</strong><br>
            • Human Development Index (HDI)<br>
            • Income inequality (GINI index)<br>
            • Education & health metrics<br>
            • Updated: Annually
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='feature-box'>
            <strong> National Statistical Agencies</strong><br>
            • Country-specific data<br>
            • Household surveys<br>
            • Census data
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Indicator Definitions
    st.markdown("<div class='help-card'>", unsafe_allow_html=True)
    st.markdown("### Indicator Definitions")
    
    st.markdown("""
    <div class='feature-box'>
        <strong>GINI Index (Income Inequality)</strong><br>
        • Ranges from 0 (perfect equality) to 100 (perfect inequality)<br>
        • Higher values = more inequality<br>
        • Based on household income/consumption surveys<br>
        • Updated every 3-5 years (expensive to measure)
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-box'>
        <strong>Human Development Index (HDI)</strong><br>
        • Composite index: life expectancy, education, income<br>
        • Ranges from 0 to 1 (higher is better)<br>
        • Published annually by UNDP
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-box'>
        <strong>GDP per Capita</strong><br>
        • Gross Domestic Product divided by population<br>
        • Measured in current USD<br>
        • Does not account for purchasing power parity (PPP)
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-box'>
        <strong>Labor Force Participation Rate</strong><br>
        • Percentage of working-age population in labor force<br>
        • Includes employed and actively seeking employment<br>
        • Reported by ILO and national agencies
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Data Processing
    st.markdown("<div class='help-card'>", unsafe_allow_html=True)
    st.markdown("### Data Processing & Integrity")
    
    st.markdown("""
    <div class='tip-box'>
        <strong>✅ What We Do:</strong><br>
        • Validate data types and ranges<br>
        • Merge datasets from multiple sources<br>
        • Standardize country names and codes<br>
        • Track data completeness and quality<br>
        • Update datasets quarterly
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='issue-box'>
        <strong>❌ What We DON'T Do:</strong><br>
        • Fill missing data with estimates or interpolation<br>
        • Adjust historical data retroactively<br>
        • Make assumptions about future trends<br>
        • Cherry-pick favorable data points
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Coverage Information
    st.markdown("<div class='help-card'>", unsafe_allow_html=True)
    st.markdown("### Coverage & Limitations")
    
    st.markdown("""
    **Countries Covered:**
    - Afghanistan, Bangladesh, Bhutan, India, Maldives, Nepal, Pakistan, Sri Lanka
    
    **Time Period:**
    - 2000-2024 (availability varies by country and indicator)
    
    **Known Limitations:**
    - GINI data has gaps (surveys are expensive and infrequent)
    - Some countries have limited historical data
    - Pandemic period (2020-2021) has data collection challenges
    - Afghanistan data limited due to conflict
    
    **Data Quality:**
    - Visit the Data Quality page for detailed completeness reports
    - Green badges (80%+) indicate reliable coverage
    - Yellow badges (60-79%) suggest caution
    - Red badges (<60%) mean insufficient data for robust analysis
    """)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 30px; color: #94a3b8;'>
    <p style='font-size: 1.1em; margin-bottom: 10px;'>
        <strong>Need More Help?</strong>
    </p>
    <p>
        • Click the <strong>❓ Quick Help</strong> button on any page for page-specific tips<br>
        • Use <strong>Smart Search</strong> for quick navigation and answers<br>
        • Check the <strong>Data Quality</strong> page to understand data limitations
    </p>

</div>
""", unsafe_allow_html=True)