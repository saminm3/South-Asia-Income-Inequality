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
from utils.utils import human_indicator

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
st.markdown("Explore statistical relationships between indicators (Correlation ≠ Causation).")
st.warning("⚠️ **CORRELATION ≠ CAUSATION**: Correlation does not imply causal relationship.")

# Load data
df = load_all_indicators()
if df.empty:
    st.error("❌ No data available")
    st.stop()

# Filter years >= 2000
df = df[df["year"] >= 2000].copy()

# Sidebar
st.sidebar.header("Correlation Settings")
all_indicators = sorted(df["indicator"].dropna().unique())

# Use Home config indicator as default (does NOT change Home/Dashboard)
default_inds = None
if "analysis_config" in st.session_state and st.session_state.analysis_config:
    cfg = st.session_state.analysis_config
    if "indicator" in cfg and cfg["indicator"] in all_indicators:
        default_inds = [cfg["indicator"]]

if default_inds is None:
    default_inds = all_indicators[:4] if len(all_indicators) >= 4 else all_indicators

selected_indicators = st.sidebar.multiselect(
    "Select Indicators (2+)",
    options=all_indicators,
    default=default_inds
)

colorscale = st.sidebar.selectbox(
    "Heatmap Color Theme",
    options=["RdBu (clean)", "Viridis", "Plasma", "Cividis"],
    index=0
)

show_only_significant = st.sidebar.checkbox(
    "Dim non-significant cells (p ≥ 0.05)",
    value=False
)

if len(selected_indicators) < 2:
    st.info("Select at least **2 indicators** to build a correlation matrix.")
    st.stop()

# Pivot to wide
corr_df = df.pivot_table(
    index=["country", "year"],
    columns="indicator",
    values="value"
).reset_index()

numeric_cols = [col for col in selected_indicators if col in corr_df.columns]
if len(numeric_cols) < 2:
    st.error("Not enough data for selected indicators.")
    st.stop()

corr_data = corr_df[numeric_cols].copy()

tab1, tab2, tab3 = st.tabs(["🔥 Heatmap", "📈 Pair Scatter", "📊 Statistics"])

# ----------------------------
# TAB 1: HEATMAP + TOP RELATIONSHIPS
# ----------------------------
with tab1:
    st.subheader("Correlation Matrix Heatmap")

    corr_matrix = corr_data.corr(method="pearson", min_periods=10)

    # Better color mapping
    plotly_scale = "RdBu" if colorscale.startswith("RdBu") else colorscale.lower()

    # Build p-value matrix
    pvals = pd.DataFrame(np.nan, index=corr_matrix.index, columns=corr_matrix.columns)
    nobs = pd.DataFrame(0, index=corr_matrix.index, columns=corr_matrix.columns)

    for i in corr_matrix.index:
        for j in corr_matrix.columns:
            if i == j:
                pvals.loc[i, j] = 0.0
                nobs.loc[i, j] = 0
                continue
            x = corr_data[i]
            y = corr_data[j]
            valid = x.notna() & y.notna()
            n = int(valid.sum())
            nobs.loc[i, j] = n
            if n >= 3:
                try:
                    _, p = pearsonr(x[valid], y[valid])
                    pvals.loc[i, j] = p
                except:
                    pvals.loc[i, j] = np.nan

    # IMPORTANT FIX: don't set to 0 (it makes heatmap misleading/ugly)
    # Instead: dim non-significant cells by shrinking them towards 0 (visual dim)
    display_z = corr_matrix.copy()
    if show_only_significant:
        mask = (pvals >= 0.05) & pvals.notna()
        display_z = display_z.where(~mask, other=display_z * 0.20)

    # Annotations: r + p colored
    annotations = []
    for r_i, row_ind in enumerate(corr_matrix.index):
        for c_j, col_ind in enumerate(corr_matrix.columns):
            if row_ind == col_ind:
                txt = "1.00"
                col = "white"
            else:
                r = corr_matrix.loc[row_ind, col_ind]
                p = pvals.loc[row_ind, col_ind]
                n = nobs.loc[row_ind, col_ind]
                if pd.isna(r) or pd.isna(p) or n < 3:
                    txt = "N/A"
                    col = "gray"
                else:
                    sig = p < 0.05
                    col = "lime" if sig else "red"
                    txt = f"{r:.2f}<br>p={p:.3f}"
            annotations.append(dict(
                x=c_j, y=r_i, text=txt, showarrow=False,
                font=dict(size=11, color=col)
            ))

    fig = go.Figure(data=go.Heatmap(
        z=display_z.values,
        x=[human_indicator(c) for c in display_z.columns],
        y=[human_indicator(r) for r in display_z.index],
        colorscale=plotly_scale,
        zmin=-1,
        zmax=1,
        zmid=0,
        colorbar=dict(title="r"),
        hovertemplate="%{y} vs %{x}<br>r=%{z:.3f}<extra></extra>"
    ))

    fig.update_layout(
        height=680,
        title="Correlation Matrix (lime = p<0.05, red = p≥0.05)",
        annotations=annotations,
        margin=dict(l=40, r=40, t=90, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.success("🟢 Lime text = statistically significant (p < 0.05)")
    with c2:
        st.error("🔴 Red text = not significant (p ≥ 0.05)")

    # ✅ UNIQUE ADD: Top Relationships (Auto)
    st.divider()
    st.subheader("🏆 Top Relationships (Auto Spotlight)")

    pairs = []
    for i in range(len(numeric_cols)):
        for j in range(i + 1, len(numeric_cols)):
            a = numeric_cols[i]
            b = numeric_cols[j]

            x = corr_data[a]
            y = corr_data[b]
            valid = x.notna() & y.notna()
            n = int(valid.sum())
            if n < 3:
                continue

            try:
                r, p = pearsonr(x[valid], y[valid])
            except:
                continue

            pairs.append((a, b, r, p, n))

    pairs = sorted(pairs, key=lambda t: abs(t[2]), reverse=True)[:8]

    def strength_label(r):
        ar = abs(r)
        if ar >= 0.7:
            return "Strong"
        if ar >= 0.4:
            return "Moderate"
        return "Weak"

    if not pairs:
        st.info("No valid pairs found for the selected indicators.")
    else:
        cols = st.columns(2)
        for idx, (a, b, r, p, n) in enumerate(pairs):
            with cols[idx % 2]:
                sig = "✅ Significant" if p < 0.05 else "❌ Not significant"
                direction = "Positive 📈" if r > 0 else "Negative 📉"
                st.markdown(f"### {idx+1}. {human_indicator(a)} ↔ {human_indicator(b)}")
                st.metric(
                    "Correlation (r)",
                    f"{r:.3f}",
                    delta=f"{strength_label(r)} | {direction}",
                    delta_color="off"
                )
                st.caption(f"{sig} • p={p:.4f} • N={n}")
                st.info(
                    f"Meaning: **{strength_label(r)} {('positive' if r > 0 else 'negative')} association** "
                    f"between these two indicators across the available country-year points."
                )

# ----------------------------
# TAB 2: SCATTER
# ----------------------------
with tab2:
    st.subheader("Scatter Plots (pairs)")
    max_pairs = st.slider("Max pairs to show", 1, 30, 10)

    pairs = []
    for i in range(len(numeric_cols)):
        for j in range(i + 1, len(numeric_cols)):
            pairs.append((numeric_cols[i], numeric_cols[j]))

    shown = 0
    for x_var, y_var in pairs:
        if shown >= max_pairs:
            break

        plot_data = corr_df[[x_var, y_var, "country", "year"]].dropna()
        if len(plot_data) < 5:
            continue

        x_vals = plot_data[x_var].values
        y_vals = plot_data[y_var].values

        try:
            corr_val, p_value = pearsonr(x_vals, y_vals)
        except:
            continue

        # regression
        z = np.polyfit(x_vals, y_vals, 1)
        poly = np.poly1d(z)
        x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
        y_line = poly(x_line)

        sig_status = "✅ Significant" if p_value < 0.05 else "❌ Not Significant"

        fig_scatter = go.Figure()

        # Color by country (looks better)
        for c in sorted(plot_data["country"].unique()):
            sub = plot_data[plot_data["country"] == c]
            fig_scatter.add_trace(go.Scatter(
                x=sub[x_var],
                y=sub[y_var],
                mode="markers",
                marker=dict(size=9, opacity=0.75),
                name=c,
                hovertemplate="Country: %{text}<br>x=%{x}<br>y=%{y}<extra></extra>",
                text=[c] * len(sub)
            ))

        fig_scatter.add_trace(go.Scatter(
            x=x_line, y=y_line, mode="lines",
            line=dict(width=3),
            name="Trend"
        ))

        fig_scatter.update_layout(
            height=520,
            title=f"{human_indicator(y_var)} vs {human_indicator(x_var)} | r={corr_val:.3f}, p={p_value:.4f} {sig_status}",
            xaxis_title=human_indicator(x_var),
            yaxis_title=human_indicator(y_var),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
        )

        st.plotly_chart(fig_scatter, use_container_width=True)
        shown += 1

    if shown == 0:
        st.info("Not enough overlapping data for the selected indicators.")

# ----------------------------
# TAB 3: STATS TABLE
# ----------------------------
with tab3:
    st.subheader("Statistics Table (r, p, CI)")

    stats_rows = []
    for i in range(len(numeric_cols)):
        for j in range(i + 1, len(numeric_cols)):
            a = numeric_cols[i]
            b = numeric_cols[j]

            x = corr_data[a]
            y = corr_data[b]
            valid = x.notna() & y.notna()
            n = int(valid.sum())
            if n < 3:
                continue

            try:
                r, pval = pearsonr(x[valid], y[valid])
            except:
                continue

            # Fisher z CI
            if abs(r) < 1 and n > 3:
                z = np.arctanh(r)
                se = 1 / np.sqrt(n - 3)
                ci_low = np.tanh(z - 1.96 * se)
                ci_high = np.tanh(z + 1.96 * se)
            else:
                ci_low, ci_high = np.nan, np.nan

            strength = "Strong" if abs(r) > 0.7 else ("Moderate" if abs(r) > 0.4 else "Weak")
            direction = "Positive" if r > 0 else "Negative"

            stats_rows.append({
                "Indicator 1": human_indicator(a),
                "Indicator 2": human_indicator(b),
                "r": round(r, 4),
                "p": round(pval, 4),
                "Significant (p<0.05)": "Yes" if pval < 0.05 else "No",
                "95% CI": f"[{ci_low:.3f}, {ci_high:.3f}]" if pd.notna(ci_low) else "N/A",
                "Strength": strength,
                "Direction": direction,
                "N": n
            })

    if not stats_rows:
        st.info("No valid pairs to compute statistics.")
    else:
        stats_df = pd.DataFrame(stats_rows)
        stats_df = stats_df.sort_values(["Significant (p<0.05)", "Strength"], ascending=[False, True])
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

        csv = stats_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Statistics (CSV)",
            data=csv,
            file_name="correlation_statistics.csv",
            mime="text/csv"
        )

st.divider()
st.caption("Correlation Analysis | South Asia Inequality Analysis Platform")
