import streamlit as st

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

st.title("❓ Help & Glossary")
st.markdown("### Quick reference guide for using the platform and understanding inequality metrics")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📖 User Guide", "📚 Glossary", "❓ FAQ", "🆘 Troubleshooting"])

with tab1:
    st.header("User Guide")
    
    st.subheader("🚀 Getting Started")
    st.markdown("""
    1. **Configure Analysis (Home Page)**
       - Select countries you want to analyze
       - Choose time period (2000-2024)
       - Pick primary indicator (GINI, HDI, etc.)
       - Click "Analyze Data"
    
    2. **Explore Visualizations**
       - Use sidebar to navigate between pages
       - Each page shows different perspective on data
       - Hover over charts for detailed information
    
    3. **Export Results**
       - Download charts as PNG images
       - Export data as CSV files
       - Generate PDF reports
    """)
    
    st.divider()
    
    st.subheader("📊 Page-by-Page Guide")
    
    with st.expander("🏠 Home - Analysis Configuration"):
        st.markdown("""
        **Purpose:** Configure your analysis parameters
        
        **Features:**
        - Select up to 5 countries
        - Choose year range (max 50 years)
        - Pick primary indicator
        - Enable/disable features
        - Quick Search for fast analysis
        
        **Tips:**
        - Start with 2-3 countries for clearer comparisons
        - Use recent years (2010-2024) for most complete data
        - Try different indicators to see various dimensions of inequality
        """)
    
    with st.expander("🗺️ Map Analysis - Animated Choropleth"):
        st.markdown("""
        **Purpose:** Visualize geographic distribution of inequality
        
        **Features:**
        - Animated map showing changes over time
        - Click ▶ to play animation
        - Drag slider to jump to specific year
        - Hover over country for details
        - Toggle animation on/off
        - Change color scheme
        
        **Tips:**
        - Enable animation to see trends unfold
        - Use color scale that works best for your data range
        - Check country rankings table below map
        """)
    
    with st.expander("📊 Dashboard - Multi-Metric Overview"):
        st.markdown("""
        **Purpose:** Get comprehensive overview with multiple charts
        
        **Features:**
        - Key metrics summary
        - Trend analysis charts
        - Country comparison bars
        - Distribution analysis
        - Raw data table
        
        **Tips:**
        - Check summary metrics first for quick insights
        - Use tabs to switch between different views
        - Download data table for offline analysis
        """)
    
    with st.expander("🔗 Correlations - Statistical Analysis"):
        st.markdown("""
        **Purpose:** Explore relationships between indicators
        
        **Features:**
        - Correlation matrix heatmap
        - Scatter plots with regression lines
        - P-values and confidence intervals
        - Statistical significance testing
        
        **Tips:**
        - Green values = statistically significant (p < 0.05)
        - Red values = not significant
        - Strong correlation > 0.7
        - Remember: Correlation ≠ Causation!
        """)
    
    with st.expander("💰 Income Simulator - Policy Scenarios"):
        st.markdown("""
        **Purpose:** Model impact of different factors on income distribution
        
        **Features:**
        - Adjust education levels
        - Change digital access
        - Compare gender impacts
        - Test urban vs rural
        - Compare multiple scenarios
        
        **Tips:**
        - Use "Compare Scenarios" mode for side-by-side analysis
        - This is a simplified model for educational purposes
        - Not for individual predictions
        """)
    
    with st.expander("✅ Data Quality - Completeness Check"):
        st.markdown("""
        **Purpose:** Assess data availability and reliability
        
        **Features:**
        - Completeness percentages
        - Data gaps identification
        - Source information
        - Update dates
        
        **Tips:**
        - High quality = 80%+ completeness
        - Check gaps before drawing conclusions
        - Use quality dashboard to explain limitations
        """)

with tab2:
    st.header("Glossary of Terms")
    
    # Inequality Metrics
    st.subheader("📊 Inequality Metrics")
    
    with st.expander("GINI Coefficient"):
        st.markdown("""
        **Definition:** Statistical measure of income or wealth inequality within a population
        
        **Scale:** 0-100 (or 0-1 in some datasets)
        - 0 = Perfect equality
        - 100 = Perfect inequality
        
        **Interpretation:**
        - < 30: Low inequality (e.g., Scandinavian countries)
        - 30-40: Moderate inequality
        - 40-50: High inequality
        - > 50: Very high inequality (e.g., South Africa)
        
        **Example:** Bangladesh GINI of 32.4 means moderate inequality
        
        **Limitations:**
        - Doesn't capture wealth inequality
        - May miss top 1% income
        - Doesn't explain causes
        """)
    
    with st.expander("Human Development Index (HDI)"):
        st.markdown("""
        **Definition:** Composite measure of average achievement in three dimensions:
        1. Health (life expectancy)
        2. Education (years of schooling)
        3. Standard of living (GNI per capita)
        
        **Scale:** 0.0 to 1.0
        - < 0.550: Low development
        - 0.550-0.699: Medium development
        - 0.700-0.799: High development
        - ≥ 0.800: Very high development
        
        **Example:** India's HDI of 0.644 means medium development
        
        **Formula:** HDI = (Health Index × Education Index × Income Index)^(1/3)
        """)
    
    with st.expander("GDP (Gross Domestic Product)"):
        st.markdown("""
        **Definition:** Monetary value of all finished goods and services produced within a country
        
        **Unit:** Current US dollars (USD)
        
        **Interpretation:**
        - Higher GDP = Larger economy
        - Does NOT measure inequality
        - Does NOT measure wellbeing
        
        **GDP per Capita:** GDP ÷ Population (average income per person)
        
        **Limitations:**
        - Doesn't show distribution
        - Ignores informal economy
        - Doesn't measure sustainability
        """)
    
    # Statistical Terms
    st.subheader("📈 Statistical Terms")
    
    with st.expander("Correlation"):
        st.markdown("""
        **Definition:** Measure of relationship between two variables
        
        **Range:** -1 to +1
        - -1: Perfect negative correlation
        - 0: No correlation
        - +1: Perfect positive correlation
        
        **Interpretation:**
        - 0.7 to 1.0: Strong correlation
        - 0.4 to 0.7: Moderate correlation
        - 0.0 to 0.4: Weak correlation
        
        **Warning:** ⚠️ Correlation ≠ Causation
        """)
    
    with st.expander("P-Value"):
        st.markdown("""
        **Definition:** Probability that results occurred by chance
        
        **Interpretation:**
        - p < 0.05: Statistically significant (< 5% chance of being random)
        - p ≥ 0.05: Not statistically significant
        
        **Common Thresholds:**
        - p < 0.001: Highly significant (***)
        - p < 0.01: Very significant (**)
        - p < 0.05: Significant (*)
        - p ≥ 0.05: Not significant (ns)
        
        **Example:** If p = 0.03, there's only 3% chance the correlation is random
        """)
    
    with st.expander("Standard Deviation"):
        st.markdown("""
        **Definition:** Measure of how spread out numbers are
        
        **Interpretation:**
        - Low SD: Data points close to mean (consistent)
        - High SD: Data points spread out (variable)
        
        **Example:** GINI SD of 5.2 means most countries are within ±5.2 of average
        """)
    
    # Regional Terms
    st.subheader("🌏 Regional Terms")
    
    with st.expander("South Asia"):
        st.markdown("""
        **Definition:** Geographic region in southern part of Asia
        
        **Countries in this platform:**
        - 🇧🇩 Bangladesh
        - 🇮🇳 India
        - 🇵🇰 Pakistan
        - 🇳🇵 Nepal
        - 🇱🇰 Sri Lanka
        
        **Note:** Sometimes includes Afghanistan, Bhutan, Maldives (SAARC definition)
        
        **Population:** ~1.9 billion (25% of world)
        """)

with tab3:
    st.header("Frequently Asked Questions")
    
    with st.expander("❓ How recent is the data?"):
        st.markdown("""
        **Answer:** Data is updated annually:
        - World Bank data: Latest available (usually 1-2 years behind)
        - UNDP HDI: Latest report (released annually in March)
        
        Most indicators have data through 2022-2023, with some gaps for certain countries.
        
        Check the **Data Quality** page to see specific coverage for each indicator.
        """)
    
    with st.expander("❓ Can I upload my own data?"):
        st.markdown("""
        **Answer:** No, this platform only visualizes authoritative data from:
        - World Bank
        - United Nations Development Programme (UNDP)
        
        **Why?** To ensure credibility and quality. All data is peer-reviewed and internationally recognized.
        
        **Alternative:** You can download our processed data and analyze it with your own tools.
        """)
    
    with st.expander("❓ Why is there missing data for some countries/years?"):
        st.markdown("""
        **Answer:** Data availability varies because:
        - Not all countries conduct surveys every year
        - Some indicators require expensive national surveys
        - Political instability can disrupt data collection
        - Methodology changes may create gaps
        
        **Solution:** Check the **Data Quality** page to see completeness percentages.
        
        We do NOT estimate or impute missing data to preserve integrity.
        """)
    
    with st.expander("❓ How do I cite this platform in my research?"):
        st.markdown("""
        **Answer:** Use this citation format:
        
        ```
        Mehzabeen, S., Asma, Tabassum, & Samin. (2025). 
        South Asia Income Inequality Analysis Platform. 
        BRAC University, Department of Computer Science and Engineering.
        
        Data Sources:
        - World Bank. (2024). Poverty and Inequality Database.
        - UNDP. (2024). Human Development Report 2024.
        ```
        
        Also available on the **Home** page.
        """)
    
    with st.expander("❓ Can I use this for my thesis/research?"):
        st.markdown("""
        **Answer:** Yes! This platform is designed for:
        - Academic research
        - Policy analysis
        - Student assignments
        - Data journalism
        
        **Requirements:**
        - Cite the platform (see citation format)
        - Cite original data sources (World Bank, UNDP)
        - Note any limitations (see Data Quality page)
        
        **License:** Data is open under CC BY 4.0 (World Bank) and Open Data Commons (UNDP)
        """)
    
    with st.expander("❓ What's the difference between GINI and HDI?"):
        st.markdown("""
        **GINI Coefficient:**
        - Measures income **inequality**
        - Lower = more equal
        - Range: 0-100
        - Only looks at income distribution
        
        **HDI (Human Development Index):**
        - Measures overall **development**
        - Higher = more developed
        - Range: 0-1
        - Includes health, education, and income
        
        **Key Difference:** GINI shows how unequal, HDI shows how developed
        
        **Example:** A country can have high HDI but also high GINI (developed but unequal)
        """)

with tab4:
    st.header("Troubleshooting")
    
    with st.expander("🐛 Charts not loading"):
        st.markdown("""
        **Try these solutions:**
        
        1. **Refresh the page** (F5 or Cmd+R)
        2. **Check your selection:**
           - At least one country selected?
           - Valid year range?
           - Indicator selected?
        3. **Clear browser cache** (Ctrl+Shift+Delete)
        4. **Try different browser** (Chrome recommended)
        5. **Check internet connection**
        
        If problem persists, contact support.
        """)
    
    with st.expander("📊 'No data available' message"):
        st.markdown("""
        **This means:**
        - Selected countries don't have data for this indicator/year
        
        **Solutions:**
        1. Try different years (2010-2020 has most complete data)
        2. Select different countries
        3. Try different indicator
        4. Check **Data Quality** page for coverage information
        
        **Note:** We don't estimate missing data - gaps are real.
        """)
    
    with st.expander("💾 Export not working"):
        st.markdown("""
        **For PNG/PDF downloads:**
        1. Ensure popup blockers are disabled
        2. Check browser download permissions
        3. Try right-click → "Save as"
        
        **For CSV downloads:**
        1. Should download automatically
        2. Check your Downloads folder
        3. If blocked, check browser settings
        
        **Alternative:** Take screenshot (Cmd+Shift+4 on Mac, Win+Shift+S on Windows)
        """)
    
    with st.expander("🔍 Quick Search not working"):
        st.markdown("""
        **Requirements:**
        - Must select both country AND indicator
        - Click "Quick Analyze" button
        
        **If still not working:**
        - Use main configuration form on Home page instead
        - Refresh page and try again
        """)

# Contact
st.divider()
st.subheader("📧 Still Need Help?")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Contact the Team:**
    - BRAC University
    - Department of CSE
    - Thesis Project 2025
    """)

with col2:
    st.info("""
    **For Technical Issues:**
    - Check Data Quality page
    - Review this Help guide
    - Try Troubleshooting section
    """)

# Footer
st.divider()
st.caption("Help & Glossary | South Asia Inequality Analysis Platform")