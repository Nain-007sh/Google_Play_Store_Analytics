"""Page 2 — Category Intelligence"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from config import BRAND_PRIMARY, BRAND_SECONDARY, BRAND_ACCENT, BRAND_WARN, BRAND_MUTED, BRAND_TEXT, CATEGORY_COLORS, BRAND_SURFACE, BRAND_BORDER
from app.utils import charts


def render(df: pd.DataFrame):
    st.markdown('<div class="page-title">Category Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Competitive landscape, category performance, and market gap analysis</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Landscape", "📊 Rankings", "🔥 Heatmap", "🫧 Bubble"])

    with tab1:
        # Treemap
        st.plotly_chart(charts.treemap_category(df), use_container_width=True)

        # Market opportunity matrix
        st.markdown('<div class="section-header">Market Opportunity Matrix</div>', unsafe_allow_html=True)
        cat_summary = df.groupby("Category").agg(
            Apps=("App", "count"),
            Avg_Rating=("Rating", "mean"),
            Total_Installs=("Installs", "sum"),
            Avg_Engagement=("Engagement_Ratio", "mean"),
        ).reset_index()

        # Classify quadrants based on median splits
        med_installs = cat_summary["Total_Installs"].median()
        med_rating = cat_summary["Avg_Rating"].median()

        def quadrant(row):
            hi_rating = row["Avg_Rating"] >= med_rating
            hi_installs = row["Total_Installs"] >= med_installs
            if hi_rating and hi_installs:
                return "⭐ Stars (High Quality + High Volume)"
            elif hi_rating and not hi_installs:
                return "💎 Gems (High Quality, Untapped)"
            elif not hi_rating and hi_installs:
                return "🏗️ Cash Cows (High Volume, Needs Quality)"
            else:
                return "⚠️ Question Marks (Low Quality + Low Volume)"

        cat_summary["Quadrant"] = cat_summary.apply(quadrant, axis=1)

        color_map = {
            "⭐ Stars (High Quality + High Volume)": BRAND_PRIMARY,
            "💎 Gems (High Quality, Untapped)": BRAND_SECONDARY,
            "🏗️ Cash Cows (High Volume, Needs Quality)": BRAND_WARN,
            "⚠️ Question Marks (Low Quality + Low Volume)": BRAND_ACCENT,
        }
        fig = px.scatter(
            cat_summary, x="Avg_Rating", y="Total_Installs",
            color="Quadrant", size="Apps",
            color_discrete_map=color_map,
            hover_name="Category",
            log_y=True, size_max=50,
            text="Category",
            labels={"Total_Installs": "Total Installs (log scale)", "Avg_Rating": "Avg Rating"},
        )
        fig.update_traces(textposition="top center", textfont_color=BRAND_MUTED, textfont_size=9)
        fig.update_layout(
            height=520,
            paper_bgcolor=BRAND_SURFACE, plot_bgcolor=BRAND_SURFACE,
            font_color=BRAND_TEXT,
            xaxis=dict(gridcolor=BRAND_BORDER),
            yaxis=dict(gridcolor=BRAND_BORDER),
            title_text="Category Opportunity Matrix — Strategic Positioning",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"""
        <div class="insight-box">
          <strong>🔍 Strategic Insight</strong><br>
          The <strong>💎 Gems quadrant</strong> represents high-quality categories with below-median install volumes —
          these are underserved markets with validated product-market fit. Entering these categories with strong
          marketing and user acquisition spend offers the highest risk-adjusted return.
          <strong>🏗️ Cash Cows</strong> have volume but quality issues — a well-polished new entrant can
          rapidly capture market share from incumbents.
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            # Top categories by installs
            data = (df.groupby("Category")["Installs"].sum()
                    .reset_index().sort_values("Installs", ascending=True).tail(20))
            fig = px.bar(data, x="Installs", y="Category", orientation="h",
                        color="Installs", color_continuous_scale=["#0D1117", BRAND_PRIMARY],
                        text=data["Installs"].apply(lambda v: f"{v/1e9:.1f}B" if v >= 1e9 else f"{v/1e6:.0f}M"))
            fig.update_traces(textposition="outside", textfont_color=BRAND_TEXT)
            fig.update_coloraxes(showscale=False)
            fig.update_layout(height=550, paper_bgcolor=BRAND_SURFACE, plot_bgcolor=BRAND_SURFACE,
                            font_color=BRAND_TEXT, title_text="Top 20 Categories — Total Installs",
                            xaxis=dict(gridcolor=BRAND_BORDER), yaxis=dict(gridcolor=BRAND_BORDER))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            # Top categories by avg rating
            data2 = (df.groupby("Category")["Rating"].mean()
                     .reset_index().sort_values("Rating", ascending=True).tail(20))
            fig2 = px.bar(data2, x="Rating", y="Category", orientation="h",
                         color="Rating", color_continuous_scale=["#0D1117", BRAND_WARN],
                         text=data2["Rating"].apply(lambda v: f"{v:.2f}"))
            fig2.update_traces(textposition="outside", textfont_color=BRAND_TEXT)
            fig2.update_coloraxes(showscale=False)
            fig2.update_layout(height=550, paper_bgcolor=BRAND_SURFACE, plot_bgcolor=BRAND_SURFACE,
                             font_color=BRAND_TEXT, title_text="Top 20 Categories — Avg Rating",
                             xaxis=dict(gridcolor=BRAND_BORDER), yaxis=dict(gridcolor=BRAND_BORDER))
            st.plotly_chart(fig2, use_container_width=True)

        # App count per category
        st.markdown('<div class="section-header">Category Saturation (App Count)</div>', unsafe_allow_html=True)
        app_count = df["Category"].value_counts().reset_index()
        app_count.columns = ["Category", "App_Count"]
        fig3 = px.bar(app_count.sort_values("App_Count", ascending=False),
                      x="Category", y="App_Count",
                      color="App_Count", color_continuous_scale=["#0D1117", BRAND_SECONDARY],
                      text="App_Count")
        fig3.update_traces(textposition="outside", textfont_color=BRAND_TEXT)
        fig3.update_coloraxes(showscale=False)
        fig3.update_layout(height=400, paper_bgcolor=BRAND_SURFACE, plot_bgcolor=BRAND_SURFACE,
                          font_color=BRAND_TEXT, xaxis_tickangle=-45,
                          xaxis=dict(gridcolor=BRAND_BORDER), yaxis=dict(gridcolor=BRAND_BORDER))
        st.plotly_chart(fig3, use_container_width=True)

    with tab3:
        st.plotly_chart(charts.heatmap_category_rating(df), use_container_width=True)

        # Correlation heatmap
        st.markdown('<div class="section-header">Numeric Feature Correlation Matrix</div>', unsafe_allow_html=True)
        num_cols = ["Rating", "Reviews", "Installs", "Size_MB", "Price",
                    "Engagement_Ratio", "Popularity_Score", "User_Trust_Score"]
        corr = df[num_cols].corr().round(2)
        fig_corr = px.imshow(corr, text_auto=True, aspect="auto",
                            color_continuous_scale=["#FF6B6B", "#0D1117", "#00D4AA"],
                            zmin=-1, zmax=1)
        fig_corr.update_layout(height=450, paper_bgcolor=BRAND_SURFACE,
                              font_color=BRAND_TEXT, title_text="Pearson Correlation — Key Metrics")
        st.plotly_chart(fig_corr, use_container_width=True)

    with tab4:
        st.plotly_chart(charts.bubble_category_metrics(df), use_container_width=True)

        # Category summary table
        st.markdown('<div class="section-header">Full Category Summary Table</div>', unsafe_allow_html=True)
        summary = df.groupby("Category").agg(
            Apps=("App", "count"),
            Total_Installs=("Installs", "sum"),
            Avg_Rating=("Rating", "mean"),
            Avg_Reviews=("Reviews", "mean"),
            Avg_Engagement=("Engagement_Ratio", "mean"),
            Free_Pct=("Type", lambda x: (x == "Free").sum() / len(x) * 100),
        ).round(2).reset_index().sort_values("Total_Installs", ascending=False)

        summary["Total_Installs"] = summary["Total_Installs"].apply(lambda v: f"{v:,.0f}")
        summary["Avg_Installs"] = ""
        summary["Avg_Rating"] = summary["Avg_Rating"].apply(lambda v: f"{v:.2f} ⭐")
        summary["Free_Pct"] = summary["Free_Pct"].apply(lambda v: f"{v:.0f}%")
        st.dataframe(summary, use_container_width=True, height=450)
