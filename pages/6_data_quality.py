import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
from pathlib import Path
from datetime import datetime

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.loaders import load_quality_audit, load_inequality_data

# Page config
st.set_page_config(
    page_title="Data Quality Audit",
    page_icon="🛡️",
    layout="wide"
)

# Load custom CSS
try:
    with open('assets/dashboard.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.title("🛡️ Data Quality & Integrity")
st.markdown("### Transparent audit of data completeness, freshness, and reliability")

# Load data
with st.spinner("Running quality diagnostics..."):
    audit = load_quality_audit()
    data = load_inequality_data()

if audit.empty or data.empty:
    st.error("❌ Critical Error: Unable to load datasets for audit.")
    st.stop()

# --- Logic: Data Freshness & Outliers ---

def check_outliers(df):
    """Detect statistical outliers using Z-score per country-indicator"""
    outliers = []
    
    for country in df['country'].unique():
        for ind in df['indicator'].unique():
            subset = df[(df['country'] == country) & (df['indicator'] == ind)].copy()
            if len(subset) > 3: # Need minimum data points
                subset['z_score'] = np.abs((subset['value'] - subset['value'].mean()) / subset['value'].std())
                # Flag anything > 2.5 std devs
                anom = subset[subset['z_score'] > 2.5]
                for _, row in anom.iterrows():
                    outliers.append({
                        'country': country,
                        'indicator': ind,
                        'year': row['year'],
                        'value': row['value'],
                        'z_score': row['z_score']
                    })
    return pd.DataFrame(outliers)

def calculate_freshness(df):
    """Calculate how recent the data is"""
    latest_years = df.groupby(['country', 'indicator'])['year'].max().reset_index()
    current_year = datetime.now().year
    latest_years['lag'] = current_year - latest_years['year']
    return latest_years

# Perform calculations
outliers_df = check_outliers(data)
freshness_df = calculate_freshness(data)

# Overall Metrics
avg_completeness = audit['completeness'].mean() if 'completeness' in audit.columns else 0
avg_lag = freshness_df['lag'].mean()
total_records = len(data)
total_outliers = len(outliers_df)

# --- UI Layout ---

# Top level stats in glass panels
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
    <div class="glass-panel" style="text-align: center; padding: 1rem;">
        <h3 style="margin:0; color:var(--text-secondary)">Data Health</h3>
        <h1 style="margin:0; font-size: 2.5rem; color: #4CAF50;">{:.1f}%</h1>
        <p style="margin:0; font-size: 0.8rem;">Completeness Score</p>
    </div>
    """.format(avg_completeness), unsafe_allow_html=True)

with c2:
    freshness_color = "#4CAF50" if avg_lag < 5 else "#FFC107" if avg_lag < 10 else "#FF4B4B"
    st.markdown("""
    <div class="glass-panel" style="text-align: center; padding: 1rem;">
        <h3 style="margin:0; color:var(--text-secondary)">Freshness</h3>
        <h1 style="margin:0; font-size: 2.5rem; color: {};">{:.0f} yrs</h1>
        <p style="margin:0; font-size: 0.8rem;">Avg. Time Lag</p>
    </div>
    """.format(freshness_color, avg_lag), unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="glass-panel" style="text-align: center; padding: 1rem;">
        <h3 style="margin:0; color:var(--text-secondary)">Volume</h3>
        <h1 style="margin:0; font-size: 2.5rem; color: #2196F3;">{}</h1>
        <p style="margin:0; font-size: 0.8rem;">Total Data Points</p>
    </div>
    """.format(total_records), unsafe_allow_html=True)

with c4:
    outlier_color = "#4CAF50" if total_outliers == 0 else "#FFC107" if total_outliers < 5 else "#FF4B4B"
    st.markdown("""
    <div class="glass-panel" style="text-align: center; padding: 1rem;">
        <h3 style="margin:0; color:var(--text-secondary)">Anomalies</h3>
        <h1 style="margin:0; font-size: 2.5rem; color: {};">{}</h1>
        <p style="margin:0; font-size: 0.8rem;">Statistical Outliers Detected</p>
    </div>
    """.format(outlier_color, total_outliers), unsafe_allow_html=True)

st.divider()

# --- Main Content Tabs ---
tab1, tab2, tab3 = st.tabs(["📊 Diagnostic Charts", "⚠️ Outlier Detection", "📋 Full Audit Log"])

with tab1:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Data Completeness Matrix")
        if 'completeness' in audit.columns:
            # Pivot for heatmap
            pivot_comp = audit.pivot_table(index='indicator', columns='country', values='completeness', aggfunc='first')
            
            fig = px.imshow(
                pivot_comp,
                labels=dict(x="", y="", color="Score"),
                color_continuous_scale="RdYlGn",
                zmin=0, zmax=100
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=20, b=20, l=20, r=20),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
    with col_b:
        st.subheader("Temporal Coverage")
        # Show min/max years per country
        coverage = data.groupby('country')['year'].agg(['min', 'max', 'count']).reset_index()
        coverage['duration'] = coverage['max'] - coverage['min']
        
        fig_timeline = go.Figure()
        for idx, row in coverage.iterrows():
            fig_timeline.add_trace(go.Bar(
                y=[row['country']],
                x=[row['duration']],
                base=[row['min']],
                orientation='h',
                name=row['country'],
                text=f"{int(row['min'])}-{int(row['max'])}",
                textposition='auto',
                marker=dict(color='rgba(50, 100, 250, 0.6)', line=dict(color='rgba(50, 100, 250, 1.0)', width=1))
            ))
        
        fig_timeline.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title="Year", gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(title=""),
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig_timeline, use_container_width=True)

with tab2:
    st.subheader("🔍 Statistical Anomaly Detection")
    st.markdown("""
    This system flags data points that deviate significantly from the trend (Z-Score > 2.5). 
    These could be **data entry errors** OR **real economic shocks**.
    """)
    
    if not outliers_df.empty:
        # Sort by severity
        outliers_df = outliers_df.sort_values('z_score', ascending=False)
        
        c_1, c_2 = st.columns([2, 1])
        
        with c_1:
            st.dataframe(
                outliers_df.style.format({'value': '{:.2f}', 'z_score': '{:.2f}'})
                .background_gradient(subset=['z_score'], cmap='Reds'),
                use_container_width=True,
                height=300
            )
        
        with c_2:
            st.info("ℹ️ **Interpretation**")
            st.markdown(f"""
            Found **{len(outliers_df)}** statistical anomalies.
            
            **Top Outlier:**
            - **{outliers_df.iloc[0]['country']}** ({outliers_df.iloc[0]['year']})
            - Indicator: {outliers_df.iloc[0]['indicator']}
            - Value: {outliers_df.iloc[0]['value']}
            - Deviation: {outliers_df.iloc[0]['z_score']:.1f}x Std Dev
            """)
            
            # Visualize the top outlier context
            top_out = outliers_df.iloc[0]
            subset = data[(data['country'] == top_out['country']) & (data['indicator'] == top_out['indicator'])]
            
            fig_out = px.line(subset, x='year', y='value', title=f"Context: {top_out['country']} - {top_out['indicator']}")
            fig_out.add_trace(go.Scatter(
                x=[top_out['year']], y=[top_out['value']],
                mode='markers', marker=dict(color='red', size=10, symbol='x'), name='Outlier'
            ))
            fig_out.update_layout(height=250, margin=dict(t=30, b=0, l=0, r=0), showlegend=False)
            st.plotly_chart(fig_out, use_container_width=True)
            
    else:
        st.success("✅ No statistical outliers detected. Time series appear smooth within acceptable bounds.")

with tab3:
    st.subheader("📋 Dataset Registry & Completeness Audit")
    
    # Filter functionality
    c_search, c_filter = st.columns([3, 1])
    with c_search:
        search_term = st.text_input("🔍 Search audit logs...", placeholder="Type country or indicator name")
    with c_filter:
        threshold = st.slider("Min Completeness", 0, 100, 0)
    
    filtered_audit = audit[audit['completeness'] >= threshold]
    if search_term:
        filtered_audit = filtered_audit[
            filtered_audit['country'].str.contains(search_term, case=False) | 
            filtered_audit['indicator'].str.contains(search_term, case=False)
        ]
    
    # Styled dataframe
    st.dataframe(
        filtered_audit,
        use_container_width=True,
        column_config={
            "completeness": st.column_config.ProgressColumn(
                "Completeness",
                help="Percent of years with valid data",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
             "source": st.column_config.LinkColumn("Source URL") 
        },
        hide_index=True
    )
    
    csv_dl = filtered_audit.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Report", csv_dl, "data_quality_full.csv", "text/csv")

# Footer
st.divider()
st.caption("Auto-generated quality report | Refreshed on " + datetime.now().strftime("%Y-%m-%d"))