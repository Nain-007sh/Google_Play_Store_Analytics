"""Page 6 — Data Quality Dashboard"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from config import BRAND_PRIMARY, BRAND_SECONDARY, BRAND_ACCENT, BRAND_WARN, BRAND_MUTED, BRAND_TEXT, BRAND_SURFACE, BRAND_BORDER
from app.utils import charts


def render(raw_df: pd.DataFrame, cleaned_df: pd.DataFrame):
    st.markdown('<div class="page-title">Data Quality Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Transparency report — raw data issues, cleaning decisions, and quality metrics</div>', unsafe_allow_html=True)

    # Summary KPIs
    raw_rows = len(raw_df)
    clean_rows = len(cleaned_df)
    removed = raw_rows - clean_rows
    missing_before = raw_df.isnull().sum().sum()
    missing_after = cleaned_df[raw_df.columns.intersection(cleaned_df.columns)].isnull().sum().sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Raw Rows", f"{raw_rows:,}")
    c2.metric("Clean Rows", f"{clean_rows:,}", f"-{removed} removed")
    c3.metric("Missing Before", f"{missing_before:,}")
    c4.metric("Missing After (raw cols)", f"{missing_after:,}", f"-{missing_before - missing_after} filled")
    c5.metric("Data Retention", f"{clean_rows/raw_rows*100:.1f}%")

    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Missing Values", "🗂️ Duplicates", "📐 Distributions", "📋 Cleaning Log"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Raw Dataset — Missing Values**")
            st.plotly_chart(charts.missing_values_bar(raw_df), use_container_width=True)
        with col2:
            st.markdown("**Cleaned Dataset — Missing Values (raw columns)**")
            shared = raw_df.columns.intersection(cleaned_df.columns)
            st.plotly_chart(charts.missing_values_bar(cleaned_df[shared]), use_container_width=True)

        # Missing value detail table
        st.markdown('<div class="section-header">Missing Value Detail</div>', unsafe_allow_html=True)
        mv_detail = []
        for col in raw_df.columns:
            before = raw_df[col].isnull().sum()
            after = cleaned_df[col].isnull().sum() if col in cleaned_df.columns else 0
            if before > 0:
                method_map = {
                    "Rating": "Group-wise median by Category",
                    "Reviews": "Group-wise median by Category",
                    "Size": "Converted to MB; group-wise median",
                    "Type": "Mode imputation",
                    "Content Rating": "Mode imputation",
                    "Current Ver": "Left as-is (not used in analysis)",
                    "Android Ver": "Left as-is (not used in analysis)",
                }
                mv_detail.append({
                    "Column": col,
                    "Missing Before": before,
                    "% Before": f"{before/raw_rows*100:.2f}%",
                    "Missing After": after,
                    "Strategy": method_map.get(col, "N/A"),
                })
        st.dataframe(pd.DataFrame(mv_detail), use_container_width=True)

    with tab2:
        raw_dups = raw_df.duplicated().sum()
        app_dups = raw_df.duplicated(subset="App").sum()
        clean_dups = cleaned_df.duplicated(subset="App").sum()

        c1, c2, c3 = st.columns(3)
        c1.metric("Exact Duplicates", f"{raw_dups:,}", "full-row")
        c2.metric("App Name Duplicates", f"{app_dups:,}", "same app name")
        c3.metric("Post-Cleaning Duplicates", f"{clean_dups:,}", "should be 0")

        st.markdown('<div class="section-header">Top Duplicated Apps (Raw)</div>', unsafe_allow_html=True)
        dup_apps = (raw_df.groupby("App").size()
                   .reset_index(name="occurrences")
                   .sort_values("occurrences", ascending=False)
                   .head(20))
        fig = px.bar(dup_apps, x="occurrences", y="App", orientation="h",
                    color="occurrences", color_continuous_scale=["#0D1117", BRAND_ACCENT],
                    text="occurrences")
        fig.update_traces(textposition="outside", textfont_color=BRAND_TEXT)
        fig.update_coloraxes(showscale=False)
        fig.update_layout(height=450, paper_bgcolor=BRAND_SURFACE, plot_bgcolor=BRAND_SURFACE,
                         font_color=BRAND_TEXT, title_text="Top 20 Apps by Duplicate Count (raw)",
                         xaxis=dict(gridcolor=BRAND_BORDER), yaxis=dict(gridcolor=BRAND_BORDER))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"""
        <div class="insight-box">
          <strong>🔧 Deduplication Strategy</strong><br>
          When the same app appeared multiple times, we retained the record with the
          <strong>highest review count</strong> — the most informative snapshot.
          Pure row-level duplicates were removed first. This approach preserves data richness
          while ensuring each app appears exactly once. Apps with conflicting metadata
          (different ratings/categories across duplicates) were resolved by the review-count rule.
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="section-header">Outlier Analysis</div>', unsafe_allow_html=True)

        num_cols = ["Rating", "Reviews", "Installs", "Size_MB", "Price"]
        available = [c for c in num_cols if c in cleaned_df.columns]

        col1, col2 = st.columns(2)
        with col1:
            selected_col = st.selectbox("Select column for outlier analysis", available)
        with col2:
            pct_clip = st.slider("Clip percentile for display", 90, 100, 99)

        col_data = cleaned_df[selected_col].dropna()
        clip_val = col_data.quantile(pct_clip / 100)
        clipped = col_data[col_data <= clip_val]

        fig = px.box(clipped, y=selected_col if selected_col in cleaned_df.columns else "value",
                    points="outliers",
                    color_discrete_sequence=[BRAND_PRIMARY])
        fig.update_layout(height=350, paper_bgcolor=BRAND_SURFACE, plot_bgcolor=BRAND_SURFACE,
                         font_color=BRAND_TEXT, title_text=f"Box Plot — {selected_col} (≤{pct_clip}th pct)",
                         yaxis=dict(gridcolor=BRAND_BORDER))
        st.plotly_chart(fig, use_container_width=True)

        # IQR stats
        Q1, Q3 = col_data.quantile(0.25), col_data.quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outliers = ((col_data < lower) | (col_data > upper)).sum()

        stat_df = pd.DataFrame([{
            "Metric": "Count", "Value": f"{len(col_data):,}",
        }, {
            "Metric": "Mean", "Value": f"{col_data.mean():.2f}",
        }, {
            "Metric": "Median", "Value": f"{col_data.median():.2f}",
        }, {
            "Metric": "Std Dev", "Value": f"{col_data.std():.2f}",
        }, {
            "Metric": "Q1", "Value": f"{Q1:.2f}",
        }, {
            "Metric": "Q3", "Value": f"{Q3:.2f}",
        }, {
            "Metric": "IQR", "Value": f"{IQR:.2f}",
        }, {
            "Metric": "IQR Outliers", "Value": f"{outliers:,} ({outliers/len(col_data)*100:.1f}%)",
        }])
        st.dataframe(stat_df, use_container_width=True, hide_index=True)

    with tab4:
        st.markdown('<div class="section-header">End-to-End Cleaning Log</div>', unsafe_allow_html=True)

        log = [
            ("1", "Junk row removal", "Removed rows where Category == '1.9'", "1 row", "Data artefact"),
            ("2", "Type fix", "Replaced Type == '0' with 'Free'", "1 row", "Encoding error"),
            ("3", "Deduplication", "Kept highest-review version per app name", "~1,180 rows", "Business rule"),
            ("4", "Reviews → int", "pd.to_numeric coercion, NaN → category median", "0 residual NaN", "Type conversion"),
            ("5", "Installs → int", "Removed '+' and ',' separators, numeric cast", "0 residual NaN", "Type conversion"),
            ("6", "Price → float", "Removed '$' prefix, numeric cast", "0 residual NaN", "Type conversion"),
            ("7", "Rating clip", "Clipped to [1.0, 5.0]", "0 anomalies remain", "Domain constraint"),
            ("8", "Size → MB float", "Parsed 'M'/'k' suffixes; 'Varies' → NaN → median", "0 residual NaN", "Unit normalisation"),
            ("9", "Last Updated → datetime", "pd.to_datetime with errors='coerce'", "Parseable dates", "Type conversion"),
            ("10", "Rating imputation", "Group-wise median by Category", "1,474 → 0 NaN", "Statistical imputation"),
            ("11", "Content Rating imputation", "Mode fill", "1 → 0 NaN", "Mode imputation"),
            ("12", "Feature engineering", "12 new analytical features generated", "+12 columns", "Domain-driven"),
        ]

        log_df = pd.DataFrame(log, columns=["Step", "Action", "Method", "Impact", "Reason"])
        st.dataframe(log_df, use_container_width=True, hide_index=True)

        st.markdown("""
        <div class="insight-box">
          <strong>📋 Data Quality Verdict</strong><br>
          The raw dataset had moderate quality issues — primarily type encoding problems, string-formatted
          numerics, and 13.6% missing ratings. After pipeline processing, the cleaned dataset is
          <strong>production-ready for analytics and ML</strong>. No records were arbitrarily removed;
          all imputation methods are documented and reproducible. The pipeline is idempotent —
          running it twice produces identical output.
        </div>
        """, unsafe_allow_html=True)

        # Schema comparison
        st.markdown('<div class="section-header">Schema: Raw vs Cleaned</div>', unsafe_allow_html=True)
        schema = []
        for col in raw_df.columns:
            schema.append({
                "Column": col,
                "Raw Dtype": str(raw_df[col].dtype),
                "Clean Dtype": str(cleaned_df[col].dtype) if col in cleaned_df.columns else "—",
                "Missing Raw": f"{raw_df[col].isnull().sum():,}",
                "Missing Clean": f"{cleaned_df[col].isnull().sum():,}" if col in cleaned_df.columns else "—",
            })
        st.dataframe(pd.DataFrame(schema), use_container_width=True, hide_index=True)
