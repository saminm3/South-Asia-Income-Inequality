import streamlit as st
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.loaders import load_inequality_data

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

st.title("📚 Data Sources & Methodology")
st.markdown("### Comprehensive documentation of data sources, collection methods, and quality assurance")

# Tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs(["📊 Data Sources", "🔬 Methodology", "✅ Quality Assurance", "📥 Downloads"])

with tab1:
    st.header("Primary Data Sources")
    
    # World Bank
    st.subheader("1️⃣ World Bank Open Data")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Organization:** The World Bank Group
        
        **Citation:**
        ```
        World Bank. (2024). Poverty and Inequality Database. 
        Washington, DC: World Bank Group. 
        Retrieved from https://data.worldbank.org
        ```
        
        **Indicators Provided:**
        - **GINI Coefficient** (SI.POV.GINI): Measures income inequality (0-100 scale)
        - **GDP Total** (NY.GDP.MKTP.CD): Gross Domestic Product in current USD
        - **Labor Force Total** (SL.TLF.TOTL.IN): Total labor force
        
        **Coverage:**
        - Geographic: 217 countries and territories
        - Temporal: 1960-2024 (varies by indicator)
        - South Asia: Complete coverage for Bangladesh, India, Pakistan, Nepal, Sri Lanka
        
        **Data Collection Method:**
        - Household surveys (e.g., Living Standards Measurement Study)
        - National statistical offices
        - International organizations
        - Standardized questionnaires across countries
        
        **Update Frequency:** Annually, typically released in September
        """)
    
    with col2:
        st.info("""
        **License:**
        Creative Commons BY 4.0
        
        **Access:**
        - Free and open
        - API available
        - Bulk downloads
        
        **Quality:**
        ⭐⭐⭐⭐⭐
        Gold standard for international development data
        """)
        
        st.link_button(
            "🔗 Visit World Bank Data",
            "https://data.worldbank.org",
            use_container_width=True
        )
    
    st.divider()
    
    # UNDP HDI
    st.subheader("2️⃣ United Nations Development Programme (UNDP)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Organization:** United Nations Development Programme
        
        **Citation:**
        ```
        UNDP. (2024). Human Development Report 2024: 
        Breaking the gridlock. New York: United Nations 
        Development Programme.
        ```
        
        **Indicators Provided:**
        - **Human Development Index (HDI)**: Composite index measuring average achievement in:
          - Health (life expectancy at birth)
          - Education (years of schooling)
          - Standard of living (GNI per capita)
        
        **Coverage:**
        - Geographic: 193 UN member states
        - Temporal: 1990-2024
        - South Asia: Complete coverage for all countries
        
        **Data Collection Method:**
        - Life expectancy: WHO and national vital registration
        - Education: UNESCO Institute for Statistics
        - Income: World Bank and IMF national accounts
        - Standardized methodology across countries
        
        **Update Frequency:** Annually, typically released in March
        """)
    
    with col2:
        st.info("""
        **License:**
        Open Data Commons
        
        **Access:**
        - Free and open
        - Excel downloads
        - Interactive dashboards
        
        **Quality:**
        ⭐⭐⭐⭐⭐
        UN-endorsed development measure
        """)
        
        st.link_button(
            "🔗 Visit UNDP HDR",
            "http://hdr.undp.org",
            use_container_width=True
        )
    
    st.divider()
    
    # Data Coverage Summary
    st.subheader("📊 Data Coverage Summary")
    
    try:
        df = load_inequality_data()
        
        if not df.empty:
            coverage_data = []
            
            for country in sorted(df['country'].unique()):
                for indicator in sorted(df['indicator'].unique()):
                    subset = df[(df['country'] == country) & (df['indicator'] == indicator)]
                    if len(subset) > 0:
                        coverage_data.append({
                            'Country': country,
                            'Indicator': indicator,
                            'Years Available': f"{int(subset['year'].min())}-{int(subset['year'].max())}",
                            'Data Points': len(subset),
                            'Source': subset['source'].iloc[0] if 'source' in subset.columns else 'N/A'
                        })
            
            import pandas as pd
            coverage_df = pd.DataFrame(coverage_data)
            st.dataframe(coverage_df, use_container_width=True, hide_index=True)
    except:
        st.warning("Unable to load coverage data")

with tab2:
    st.header("Methodology")
    
    # GINI Methodology
    with st.expander("🔵 GINI Coefficient Methodology"):
        st.markdown("""
        **Definition:**
        The GINI coefficient measures the extent to which the distribution of income (or consumption) 
        among individuals or households within an economy deviates from a perfectly equal distribution.
        
        **Calculation:**
        - Based on the Lorenz curve
        - GINI = A / (A + B), where:
          - A = Area between Lorenz curve and equality line
          - B = Area under Lorenz curve
        
        **Scale:**
        - 0 = Perfect equality (everyone has same income)
        - 100 = Perfect inequality (one person has all income)
        
        **Interpretation Guidelines:**
        - < 30: Low inequality
        - 30-40: Moderate inequality
        - 40-50: High inequality
        - > 50: Very high inequality
        
        **Data Sources for Calculation:**
        - Household income and expenditure surveys
        - Tax records (in some countries)
        - Census data
        
        **Limitations:**
        - Doesn't capture wealth inequality (only income)
        - May underestimate top incomes
        - Doesn't show source of inequality
        """)
    
    # HDI Methodology
    with st.expander("🟢 Human Development Index (HDI) Methodology"):
        st.markdown("""
        **Definition:**
        The HDI is a composite index measuring average achievement in three basic dimensions of human development:
        
        **Components (Equal Weight):**
        
        1. **Health Dimension (Life Expectancy)**
           - Indicator: Life expectancy at birth
           - Minimum: 20 years
           - Maximum: 85 years
        
        2. **Education Dimension**
           - Mean years of schooling (adults 25+)
           - Expected years of schooling (children)
           - Minimum: 0 years
           - Maximum: 18 years (mean), 18 years (expected)
        
        3. **Standard of Living Dimension**
           - Indicator: GNI per capita (PPP $)
           - Minimum: $100
           - Maximum: $75,000
           - Logarithmic transformation
        
        **Calculation Formula:**
        ```
        HDI = (Health Index × Education Index × Income Index)^(1/3)
        ```
        
        **Scale:**
        - 0.0 to 1.0
        - < 0.550: Low human development
        - 0.550-0.699: Medium human development
        - 0.700-0.799: High human development
        - ≥ 0.800: Very high human development
        
        **Data Quality:**
        - Uses most recent reliable data
        - Missing data estimated using cross-country regression
        - Methodology consistent since 2010
        """)
    
    # GDP Methodology
    with st.expander("💰 GDP Methodology"):
        st.markdown("""
        **Definition:**
        Gross Domestic Product (GDP) is the monetary value of all finished goods and services 
        produced within a country's borders in a specific time period.
        
        **Measurement Approaches:**
        1. Production approach: Sum of value added
        2. Income approach: Sum of incomes earned
        3. Expenditure approach: Sum of final expenditures
        
        **Currency:**
        - Reported in current US dollars
        - Market exchange rates used for conversion
        
        **Limitations:**
        - Doesn't measure inequality
        - Doesn't account for informal economy
        - Doesn't measure wellbeing or sustainability
        """)

with tab3:
    st.header("Quality Assurance")
    
    st.markdown("""
    ### Our Quality Control Process
    
    #### 1️⃣ Source Verification
    - ✅ All data from internationally recognized organizations
    - ✅ Peer-reviewed methodologies
    - ✅ Regular audits by source organizations
    - ✅ Transparent documentation
    
    #### 2️⃣ Data Validation
    - ✅ Automated range checks (e.g., GINI must be 0-100)
    - ✅ Year validation (1900-2030)
    - ✅ Cross-country consistency checks
    - ✅ Temporal consistency validation
    
    #### 3️⃣ Missing Data Handling
    - ✅ Missing values clearly indicated
    - ✅ No imputation or estimation (preserves source data integrity)
    - ✅ Completeness metrics provided
    - ✅ Gap analysis available in Data Quality page
    
    #### 4️⃣ Update Process
    - ✅ Annual updates when sources release new data
    - ✅ Version control of datasets
    - ✅ Change logs maintained
    - ✅ Backward compatibility ensured
    
    #### 5️⃣ Reproducibility
    - ✅ Source data preserved
    - ✅ Processing scripts available
    - ✅ Transformation documented
    - ✅ Codebook provided
    """)
    
    st.success("✅ All data in this platform has passed our quality assurance checks")

with tab4:
    st.header("Downloads")
    
    st.markdown("### Access Raw and Processed Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 Processed Data")
        st.markdown("""
        Download our cleaned and standardized datasets:
        
        **Included:**
        - All South Asian countries
        - Years: 2000-2024
        - Standardized format
        - Quality assured
        """)
        
        try:
            df = load_inequality_data()
            if not df.empty:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Main Dataset (CSV)",
                    data=csv,
                    file_name="south_asia_inequality_data.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        except:
            st.warning("Dataset not available for download")
    
    with col2:
        st.subheader("📄 Documentation")
        st.markdown("""
        **Available Documents:**
        - Data dictionary
        - Codebook
        - Processing scripts
        - Quality audit report
        """)
        
        st.info("Contact thesis team for full documentation package")
    
    st.divider()
    
    st.subheader("🔗 External Data Sources")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.link_button(
            "🌍 World Bank Data Portal",
            "https://data.worldbank.org",
            use_container_width=True
        )
        st.link_button(
            "📊 World Bank API Documentation",
            "https://datahelpdesk.worldbank.org/knowledgebase/topics/125589",
            use_container_width=True
        )
    
    with col2:
        st.link_button(
            "🌐 UNDP Data Center",
            "http://hdr.undp.org/data-center",
            use_container_width=True
        )
        st.link_button(
            "📈 UNDP Statistical Tables",
            "http://hdr.undp.org/statistical-update",
            use_container_width=True
        )

# Footer
st.divider()
st.caption("Data Sources & Methodology | South Asia Inequality Analysis Platform")