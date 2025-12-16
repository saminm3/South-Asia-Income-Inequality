import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from scipy.stats import pearsonr
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.loaders import load_all_indicators

# Page config
st.set_page_config(
    page_title="Correlation Analysis",
    page_icon="🔗",
    layout="wide"
)

# Load custom CSS
try:
    with open('assets/dashboard.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.title("🔗 Correlation Analysis")
st.markdown("Explore statistical relationships between inequality indicators")

# CRITICAL WARNING
st.error("⚠️ **CORRELATION ≠ CAUSATION**: Statistical correlation does not imply causal relationship.")

# Load data
df = load_all_indicators()

if df.empty:
    st.error("No data available")
    st.stop()

# Filter years >= 2000
df = df[df['year'] >= 2000].copy()

# Sidebar - indicator selection
st.sidebar.header("Correlation Settings")
all_indicators = sorted(df['indicator'].dropna().unique())
selected_indicators = st.sidebar.multiselect(
    "Select Indicators",
    options=all_indicators,
    default=all_indicators[:4] if len(all_indicators) >= 4 else all_indicators
)

if len(selected_indicators) < 2:
    st.warning("Please select at least 2 indicators for correlation analysis")
    st.stop()

# Pivot to have indicators as columns
corr_df = df.pivot_table(
    index=['country', 'year'], 
    columns='indicator', 
    values='value'
).reset_index()

# Select numeric indicators
numeric_cols = [col for col in selected_indicators if col in corr_df.columns]

if len(numeric_cols) < 2:
    st.error("Not enough data for selected indicators")
    st.stop()

# Calculate correlation data
corr_data = corr_df[numeric_cols]

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["🔥 Heatmap", "📈 Scatter Plots", "📊 Statistics"])

with tab1:
    st.subheader("Correlation Matrix Heatmap")
    
    # Calculate correlation matrix
    corr_matrix = corr_data.corr(method='pearson', min_periods=10)
    
    # Create annotations with correlation values and p-values
    annotations = []
    for i, row_ind in enumerate(corr_matrix.index):
        for j, col_ind in enumerate(corr_matrix.columns):
            if i != j:
                r = corr_matrix.loc[row_ind, col_ind]
                
                # Calculate p-value
                try:
                    x = corr_data[row_ind].dropna()
                    y = corr_data[col_ind].dropna()
                    
                    common_idx = x.index.intersection(y.index)
                    if len(common_idx) > 2:
                        _, p_value = pearsonr(x.loc[common_idx], y.loc[common_idx])
                        
                        color = 'green' if p_value < 0.05 else 'red'
                        text = f"{r:.3f}<br>p={p_value:.4f}"
                    else:
                        color = 'gray'
                        text = f"{r:.3f}<br>N/A"
                except:
                    color = 'gray'
                    text = f"{r:.3f}<br>N/A"
            else:
                text = "1.000"
                color = 'black'
            
            annotations.append(
                dict(
                    x=j, y=i,
                    text=text,
                    showarrow=False,
                    font=dict(color=color, size=10)
                )
            )
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        colorscale='RdBu_r',
        zmid=0,
        zmin=-1,
        zmax=1,
        colorbar=dict(title="Correlation"),
        hovertemplate='%{y} vs %{x}<br>Correlation: %{z:.3f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Correlation Matrix with P-Values (Green: p<0.05, Red: p≥0.05)",
        annotations=annotations,
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Legend
    col1, col2 = st.columns(2)
    with col1:
        st.success("🟢 **Green**: Statistically significant (p < 0.05)")
    with col2:
        st.error("🔴 **Red**: Not statistically significant (p ≥ 0.05)")
    
    # Export
    col1, col2 = st.columns(2)
    with col1:
        img_bytes = fig.to_image(format="png", width=1200, height=800)
        st.download_button(
            "📥 Download Heatmap (PNG)",
            data=img_bytes,
            file_name="correlation_heatmap.png",
            mime="image/png",
            use_container_width=True
        )
    with col2:
        csv = corr_matrix.to_csv().encode('utf-8')
        st.download_button(
            "📥 Download Matrix (CSV)",
            data=csv,
            file_name="correlation_matrix.csv",
            mime="text/csv",
            use_container_width=True
        )

with tab2:
    st.subheader("Scatter Plots with Regression Lines")
    
    # Create scatter plots for each pair
    n_indicators = len(numeric_cols)
    
    for i in range(n_indicators):
        for j in range(i+1, n_indicators):
            x_var = numeric_cols[i]
            y_var = numeric_cols[j]
            
            # Get clean data
            plot_data = corr_df[[x_var, y_var]].dropna()
            
            if len(plot_data) > 1:
                x_vals = plot_data[x_var].values
                y_vals = plot_data[y_var].values
                
                # Calculate regression
                z = np.polyfit(x_vals, y_vals, 1)
                p = np.poly1d(z)
                
                # Calculate R²
                y_pred = p(x_vals)
                ss_res = np.sum((y_vals - y_pred) ** 2)
                ss_tot = np.sum((y_vals - np.mean(y_vals)) ** 2)
                r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                
                # Calculate correlation and p-value
                corr_val, p_value = pearsonr(x_vals, y_vals)
                
                # Create scatter plot
                fig_scatter = go.Figure()
                
                fig_scatter.add_trace(go.Scatter(
                    x=x_vals,
                    y=y_vals,
                    mode='markers',
                    marker=dict(size=10, color='blue', opacity=0.6),
                    name='Data Points'
                ))
                
                # Add regression line
                x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
                y_line = p(x_line)
                
                fig_scatter.add_trace(go.Scatter(
                    x=x_line,
                    y=y_line,
                    mode='lines',
                    line=dict(color='red', width=3),
                    name='Regression Line'
                ))
                
                sig_status = "✅ Significant" if p_value < 0.05 else "❌ Not Significant"
                fig_scatter.update_layout(
                    title=f"{y_var} vs {x_var}<br>r={corr_val:.3f}, R²={r2:.3f}, p={p_value:.4f} {sig_status}",
                    xaxis_title=x_var,
                    yaxis_title=y_var,
                    height=500,
                    showlegend=True
                )
                
                st.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    st.subheader("Statistical Summary")
    
    # Create detailed statistics table
    stats_data = []
    
    for i, row_ind in enumerate(corr_matrix.index):
        for j, col_ind in enumerate(corr_matrix.columns):
            if i < j:
                r = corr_matrix.loc[row_ind, col_ind]
                
                try:
                    x = corr_data[row_ind].dropna()
                    y = corr_data[col_ind].dropna()
                    
                    common_idx = x.index.intersection(y.index)
                    if len(common_idx) > 2:
                        corr_val, p_value = pearsonr(x.loc[common_idx], y.loc[common_idx])
                        
                        n = len(common_idx)
                        z = np.arctanh(corr_val)
                        se = 1 / np.sqrt(n - 3)
                        ci_lower = np.tanh(z - 1.96 * se)
                        ci_upper = np.tanh(z + 1.96 * se)
                        
                        strength = "Strong" if abs(corr_val) > 0.7 else ("Moderate" if abs(corr_val) > 0.4 else "Weak")
                        direction = "Positive" if corr_val > 0 else "Negative"
                        significant = "Yes ✅" if p_value < 0.05 else "No ❌"
                        
                        stats_data.append({
                            'Indicator 1': row_ind,
                            'Indicator 2': col_ind,
                            'Correlation (r)': f"{corr_val:.4f}",
                            'P-Value': f"{p_value:.4f}",
                            'Significant': significant,
                            '95% CI': f"[{ci_lower:.3f}, {ci_upper:.3f}]",
                            'Strength': strength,
                            'Direction': direction,
                            'Sample Size': n
                        })
                except Exception as e:
                    pass
    
    if stats_data:
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
        
        # Download button
        csv = stats_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Statistics (CSV)",
            data=csv,
            file_name="correlation_statistics.csv",
            mime="text/csv"
        )

# Footer
st.divider()
st.caption("Correlation Analysis | South Asia Inequality Analysis Platform")