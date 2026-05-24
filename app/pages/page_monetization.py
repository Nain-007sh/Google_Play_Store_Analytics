"""Page 4 — Monetization Analytics"""
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
    st.markdown('<div class="page-title">Monetization Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Revenue intelligence, pricing strategy, and paid-vs-free economics</div>', unsafe_allow_html=True)

    free_df = df[df["Type"] == "Free"]
    paid_df = df[df["Type"] == "Paid"]

    # KPIs
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Rev. Estimate", f"${df['Revenue_Estimate'].sum()/1e6:.1f}M", "paid apps (70% net)")
    c2.metric("Paid Apps", f"{len(paid_df):,}", f"{len(paid_df)/len(df)*100:.1f}% of portfolio")
    c3.metric("Avg Paid Price", f"${paid_df['Price'].mean():.2f}" if len(paid_df) else "N/A")
    c4.metric("Free Avg Installs", f"{free_df['Installs'].mean()/1e6:.1f}M" if len(free_df) else "N/A")
    c5.metric("Paid Avg Installs", f"{paid_df['Installs'].mean()/1e3:.0f}K" if len(paid_df) else "N/A")

    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["💸 Revenue", "🏷️ Pricing", "⚖️ Free vs Paid", "📐 Strategy"])

    with tab1:
        if len(paid_df) > 0:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(charts.bar_revenue_by_category(df, 12), use_container_width=True)
            with col2:
                # Revenue by price category
                rev_price = df.groupby("Price_Category", observed=True)["Revenue_Estimate"].sum().reset_index()
                rev_price = rev_price[rev_price["Revenue_Estimate"] > 0]
                fig = px.pie(rev_price, names="Price_Category", values="Revenue_Estimate",
                            hole=0.5, color_discrete_sequence=CATEGORY_COLORS)
                fig.update_traces(textfont_color=BRAND_TEXT)
                fig.update_layout(height=400, paper_bgcolor=BRAND_SURFACE, font_color=BRAND_TEXT,
                                 title_text="Revenue Share by Price Tier")
                st.plotly_chart(fig, use_container_width=True)

            # Top revenue-generating apps
            st.markdown('<div class="section-header">Top 20 Revenue Generating Apps</div>', unsafe_allow_html=True)
            top_rev = (paid_df.nlargest(20, "Revenue_Estimate")
                      [["App", "Category", "Price", "Installs", "Revenue_Estimate", "Rating"]]
                      .copy())
            top_rev["Revenue_Estimate"] = top_rev["Revenue_Estimate"].apply(lambda v: f"${v:,.0f}")
            top_rev["Installs"] = top_rev["Installs"].apply(lambda v: f"{v:,}")
            top_rev["Price"] = top_rev["Price"].apply(lambda v: f"${v:.2f}")
            st.dataframe(top_rev.reset_index(drop=True), use_container_width=True)
        else:
            st.info("No paid apps in current filter.")

    with tab2:
        if len(paid_df) > 0:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(charts.box_price_rating(df), use_container_width=True)
            with col2:
                # Price distribution for paid apps
                paid_clip = paid_df[paid_df["Price"] <= 30]
                fig = px.histogram(paid_clip, x="Price", nbins=40,
                                  color_discrete_sequence=[BRAND_SECONDARY])
                fig.update_traces(marker_line_color="#0D1117", marker_line_width=0.3)
                fig.update_layout(height=400, paper_bgcolor=BRAND_SURFACE, plot_bgcolor=BRAND_SURFACE,
                                 font_color=BRAND_TEXT, title_text="Paid App Price Distribution (≤$30)",
                                 xaxis=dict(gridcolor=BRAND_BORDER), yaxis=dict(gridcolor=BRAND_BORDER))
                st.plotly_chart(fig, use_container_width=True)

            # Price vs installs scatter
            _paid_clip = paid_df[paid_df["Price"] <= 30]
            paid_sample = _paid_clip.sample(min(500, len(_paid_clip)), random_state=42)
            fig2 = px.scatter(paid_sample, x="Price", y="Installs",
                             color="Rating", size="Reviews",
                             hover_name="App", log_y=True,
                             color_continuous_scale=["#0D1117", BRAND_WARN, BRAND_PRIMARY],
                             size_max=20, opacity=0.75,
                             labels={"Installs": "Installs (log)"},
                            )
            fig2.update_layout(height=420, paper_bgcolor=BRAND_SURFACE, plot_bgcolor=BRAND_SURFACE,
                              font_color=BRAND_TEXT, title_text="Price vs Installs (Paid Apps, ≤$30)",
                              xaxis=dict(gridcolor=BRAND_BORDER), yaxis=dict(gridcolor=BRAND_BORDER))
            st.plotly_chart(fig2, use_container_width=True)

            # Price band summary
            st.markdown('<div class="section-header">Pricing Strategy Summary</div>', unsafe_allow_html=True)
            price_summary = paid_df.groupby("Price_Category", observed=True).agg(
                App_Count=("App", "count"),
                Avg_Installs=("Installs", "mean"),
                Avg_Rating=("Rating", "mean"),
                Total_Revenue=("Revenue_Estimate", "sum"),
                Avg_Revenue_Per_App=("Revenue_Estimate", "mean"),
            ).round(2).reset_index()
            price_summary["Total_Revenue"] = price_summary["Total_Revenue"].apply(lambda v: f"${v:,.0f}")
            price_summary["Avg_Installs"] = price_summary["Avg_Installs"].apply(lambda v: f"{v:,.0f}")
            price_summary["Avg_Revenue_Per_App"] = price_summary["Avg_Revenue_Per_App"].apply(lambda v: f"${v:,.0f}")
            st.dataframe(price_summary, use_container_width=True)
        else:
            st.info("No paid apps in current filter.")

    with tab3:
        # Side-by-side comparison
        col1, col2 = st.columns(2)
        with col1:
            # Install distribution comparison
            fig = go.Figure()
            for app_type, color in [("Free", BRAND_PRIMARY), ("Paid", BRAND_SECONDARY)]:
                subset = df[df["Type"] == app_type]["Log_Installs"]
                fig.add_trace(go.Violin(y=subset, name=app_type, fillcolor=color,
                                       line_color=color, opacity=0.7, box_visible=True,
                                       meanline_visible=True))
            fig.update_layout(height=420, paper_bgcolor=BRAND_SURFACE, plot_bgcolor=BRAND_SURFACE,
                             font_color=BRAND_TEXT, title_text="Install Distribution: Free vs Paid (log)",
                             xaxis=dict(gridcolor=BRAND_BORDER), yaxis=dict(gridcolor=BRAND_BORDER))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            # Rating comparison
            fig2 = go.Figure()
            for app_type, color in [("Free", BRAND_PRIMARY), ("Paid", BRAND_SECONDARY)]:
                subset = df[df["Type"] == app_type]["Rating"]
                fig2.add_trace(go.Box(y=subset, name=app_type, marker_color=color,
                                     boxpoints="outliers"))
            fig2.update_layout(height=420, paper_bgcolor=BRAND_SURFACE, plot_bgcolor=BRAND_SURFACE,
                              font_color=BRAND_TEXT, title_text="Rating Distribution: Free vs Paid",
                              xaxis=dict(gridcolor=BRAND_BORDER), yaxis=dict(gridcolor=BRAND_BORDER))
            st.plotly_chart(fig2, use_container_width=True)

        # Metrics comparison table
        comparison = []
        for t in ["Free", "Paid"]:
            sub = df[df["Type"] == t]
            if len(sub) == 0:
                continue
            comparison.append({
                "Type": t,
                "Count": f"{len(sub):,}",
                "Avg Installs": f"{sub['Installs'].mean():,.0f}",
                "Median Installs": f"{sub['Installs'].median():,.0f}",
                "Avg Rating": f"{sub['Rating'].mean():.2f}",
                "Avg Reviews": f"{sub['Reviews'].mean():,.0f}",
                "Avg Engagement": f"{sub['Engagement_Ratio'].mean()*100:.2f}%",
                "Avg Trust Score": f"{sub['User_Trust_Score'].mean():.1f}",
            })
        st.dataframe(pd.DataFrame(comparison), use_container_width=True)

        free_avg = free_df["Installs"].mean() if len(free_df) else 0
        paid_avg = paid_df["Installs"].mean() if len(paid_df) else 0
        multiplier = free_avg / paid_avg if paid_avg > 0 else 0
        st.markdown(f"""
        <div class="insight-box warn">
          <strong>⚠️ Freemium Reality Check</strong><br>
          Free apps achieve <strong>{multiplier:.0f}× more installs</strong> than paid apps on average.
          The data strongly validates the <strong>freemium model</strong> as the dominant
          monetisation strategy for user acquisition. Paid apps are only viable for:
          (1) utility tools with clear ROI, (2) niche professional audiences,
          (3) apps with strong brand recognition. For consumer apps targeting mass market,
          the <strong>free → in-app purchase</strong> funnel is the evidence-backed path.
        </div>
        """, unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="section-header">Monetization Strategy Framework</div>', unsafe_allow_html=True)
        st.markdown("""
        Based on the dataset analysis, here is the evidence-backed monetisation framework:
        """)

        strategies = [
            ("🆓 Freemium", "Free core + paid upgrades",
             f"Avg {free_df['Installs'].mean()/1e6:.1f}M installs",
             "Mass market apps, games, productivity tools", BRAND_PRIMARY),
            ("💳 One-Time Purchase", "$0.99–$4.99 sweet spot",
             f"{len(paid_df[paid_df['Price'] <= 4.99]):} apps in range",
             "Utility tools, niche B2B, premium productivity", BRAND_SECONDARY),
            ("💰 Premium Tier", "$5+ pricing",
             f"{len(paid_df[paid_df['Price'] > 5]):} apps",
             "Professional tools, security, enterprise", BRAND_WARN),
        ]

        cols = st.columns(3)
        for i, (name, model, stat, use_case, color) in enumerate(strategies):
            with cols[i]:
                st.markdown(f"""
                <div class="kpi-card" style="--accent:{color}; min-height:200px;">
                  <div class="kpi-label">Strategy</div>
                  <div class="kpi-value" style="font-size:1.2rem">{name}</div>
                  <div style="margin-top:.5rem; font-size:.85rem; color: {BRAND_TEXT}">{model}</div>
                  <div style="margin-top:.3rem; font-size:.78rem; color: {color}">{stat}</div>
                  <div style="margin-top:.5rem; font-size:.78rem; color: {BRAND_MUTED}">Best for: {use_case}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">Revenue by Content Rating</div>', unsafe_allow_html=True)
        rev_content = df.groupby("Content Rating")["Revenue_Estimate"].sum().reset_index()
        fig = px.bar(rev_content.sort_values("Revenue_Estimate", ascending=False),
                    x="Content Rating", y="Revenue_Estimate",
                    color="Revenue_Estimate", color_continuous_scale=["#0D1117", BRAND_PRIMARY],
                    text=rev_content["Revenue_Estimate"].apply(lambda v: f"${v/1e6:.1f}M"))
        fig.update_traces(textposition="outside", textfont_color=BRAND_TEXT)
        fig.update_coloraxes(showscale=False)
        fig.update_layout(height=380, paper_bgcolor=BRAND_SURFACE, plot_bgcolor=BRAND_SURFACE,
                         font_color=BRAND_TEXT,
                         xaxis=dict(gridcolor=BRAND_BORDER), yaxis=dict(gridcolor=BRAND_BORDER))
        st.plotly_chart(fig, use_container_width=True)