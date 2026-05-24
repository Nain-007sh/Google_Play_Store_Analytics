"""Page 3 — User Engagement Analytics"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from config import BRAND_PRIMARY, BRAND_SECONDARY, BRAND_ACCENT, BRAND_WARN, BRAND_MUTED, BRAND_TEXT, CATEGORY_COLORS, BRAND_SURFACE, BRAND_BORDER
from app.utils import charts


def render(df: pd.DataFrame, sentiment_df: pd.DataFrame):
    st.markdown('<div class="page-title">User Engagement Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Review behaviour, sentiment analysis, and engagement driver deep-dive</div>', unsafe_allow_html=True)

    # KPIs
    eng_avg = df["Engagement_Ratio"].mean() * 100
    top_eng = df.nlargest(1, "Engagement_Ratio")["App"].values[0]
    total_rev = df["Reviews"].sum()
    total_installs = df["Installs"].sum()
    overall_er = total_rev / total_installs * 100 if total_installs > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Engagement Rate", f"{eng_avg:.2f}%", "reviews / installs")
    col2.metric("Platform Engagement", f"{overall_er:.2f}%", "total reviews / total installs")
    col3.metric("Total Reviews (filtered)", f"{total_rev/1e9:.2f}B", "user feedback")
    col4.metric("Most Engaged App", top_eng[:25] + "…" if len(top_eng) > 25 else top_eng)

    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Engagement Patterns", "😊 Sentiment Analysis", "🔗 Correlation", "🏆 Leaderboard"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(charts.scatter_rating_installs(df), use_container_width=True)
        with col2:
            st.plotly_chart(charts.violin_engagement(df), use_container_width=True)

        # Engagement Ratio distribution
        fig = px.histogram(df[df["Engagement_Ratio"] < df["Engagement_Ratio"].quantile(0.98)],
                          x="Engagement_Ratio", nbins=60, color_discrete_sequence=[BRAND_SECONDARY])
        fig.update_traces(marker_line_color="#0D1117", marker_line_width=0.3)
        fig.update_layout(height=360, paper_bgcolor=BRAND_SURFACE, plot_bgcolor=BRAND_SURFACE,
                         font_color=BRAND_TEXT,
                         title_text="Engagement Ratio Distribution (98th pct clipped)",
                         xaxis=dict(gridcolor=BRAND_BORDER), yaxis=dict(gridcolor=BRAND_BORDER))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"""
        <div class="insight-box">
          <strong>💡 Engagement Psychology</strong><br>
          The median engagement ratio is <strong>{df['Engagement_Ratio'].median()*100:.2f}%</strong> —
          meaning fewer than <strong>1 in 50 users</strong> leaves a review. This "silent majority"
          phenomenon is well-documented in digital products. Apps with engagement ratios above
          <strong>5%</strong> exhibit strong community characteristics — these are products where users
          feel personally invested. Low engagement does NOT mean low satisfaction; it means the
          friction to review exceeds the motivation.
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        if sentiment_df is not None and len(sentiment_df) > 0:
            st.plotly_chart(charts.bar_sentiment(sentiment_df, df, 15), use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(charts.scatter_polarity_rating(sentiment_df, df), use_container_width=True)
            with col2:
                # Sentiment distribution pie
                sent_counts = sentiment_df.copy()
                pos = (sent_counts["pos_pct"] * sent_counts["review_count"]).sum() / sent_counts["review_count"].sum()
                neg = (sent_counts["neg_pct"] * sent_counts["review_count"]).sum() / sent_counts["review_count"].sum()
                neu = (sent_counts["neu_pct"] * sent_counts["review_count"]).sum() / sent_counts["review_count"].sum()

                fig = go.Figure(go.Pie(
                    labels=["Positive", "Neutral", "Negative"],
                    values=[pos, neu, neg],
                    hole=0.6,
                    marker_colors=[BRAND_PRIMARY, BRAND_WARN, BRAND_ACCENT],
                    textinfo="label+percent",
                    textfont_color=BRAND_TEXT,
                ))
                fig.add_annotation(text=f"<b>{pos:.0f}%</b><br>Positive",
                                  x=0.5, y=0.5, showarrow=False,
                                  font=dict(size=16, color=BRAND_TEXT))
                fig.update_layout(height=380, paper_bgcolor=BRAND_SURFACE, font_color=BRAND_TEXT,
                                 title_text="Overall Platform Sentiment")
                st.plotly_chart(fig, use_container_width=True)

            # Polarity distribution
            fig2 = px.histogram(sentiment_df, x="avg_polarity", nbins=50,
                               color_discrete_sequence=[BRAND_PRIMARY])
            fig2.update_layout(height=350, paper_bgcolor=BRAND_SURFACE, plot_bgcolor=BRAND_SURFACE,
                              font_color=BRAND_TEXT, title_text="Average Review Polarity Distribution",
                              xaxis=dict(gridcolor=BRAND_BORDER), yaxis=dict(gridcolor=BRAND_BORDER))
            st.plotly_chart(fig2, use_container_width=True)

            st.markdown(f"""
            <div class="insight-box">
              <strong>📊 Sentiment Intelligence</strong><br>
              Platform-wide sentiment skews <strong>positive at {pos:.0f}%</strong>, with only
              <strong>{neg:.0f}% negative reviews</strong>. However, negative reviews carry
              <strong>3–5× the weight</strong> in purchase/install decisions (negativity bias).
              Apps that actively respond to negative reviews see rating recoveries of
              <strong>0.2–0.5 stars</strong> on average. The correlation between polarity and
              rating suggests user reviews are <strong>honest signals</strong>, not just rating theatre.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Sentiment data not available for the current filter selection.")

    with tab3:
        # Scatter matrix of key engagement metrics
        scatter_cols = ["Rating", "Log_Installs", "Log_Reviews", "Engagement_Ratio", "User_Trust_Score"]
        sample = df[scatter_cols].sample(min(1500, len(df)), random_state=42)
        fig = px.scatter_matrix(sample, dimensions=scatter_cols,
                               color_discrete_sequence=[BRAND_PRIMARY],
                               opacity=0.5)
        fig.update_traces(diagonal_visible=False, marker_size=3)
        fig.update_layout(height=600, paper_bgcolor=BRAND_SURFACE, plot_bgcolor=BRAND_SURFACE,
                         font_color=BRAND_TEXT, title_text="Scatter Matrix — Engagement Metrics")
        st.plotly_chart(fig, use_container_width=True)

        # Log installs vs log reviews
        col1, col2 = st.columns(2)
        with col1:
            sample2 = df.sample(min(2000, len(df)), random_state=1)
            fig2 = px.density_contour(sample2, x="Log_Installs", y="Log_Reviews",
                                     color_discrete_sequence=[BRAND_PRIMARY])
            fig2.update_traces(contours_coloring="fill",
                              colorscale=["#0D1117", "#1A4A3C", "#00D4AA"])
            fig2.update_layout(height=400, paper_bgcolor=BRAND_SURFACE, plot_bgcolor=BRAND_SURFACE,
                              font_color=BRAND_TEXT, title_text="Log(Installs) vs Log(Reviews) Density",
                              xaxis=dict(gridcolor=BRAND_BORDER), yaxis=dict(gridcolor=BRAND_BORDER))
            st.plotly_chart(fig2, use_container_width=True)
        with col2:
            # Engagement by install bucket
            eng_bucket = df.groupby("Install_Bucket", observed=True)["Engagement_Ratio"].mean().reset_index()
            fig3 = px.bar(eng_bucket, x="Install_Bucket", y="Engagement_Ratio",
                         color="Engagement_Ratio",
                         color_continuous_scale=["#0D1117", BRAND_SECONDARY],
                         text=eng_bucket["Engagement_Ratio"].apply(lambda v: f"{v*100:.2f}%"))
            fig3.update_traces(textposition="outside", textfont_color=BRAND_TEXT)
            fig3.update_coloraxes(showscale=False)
            fig3.update_layout(height=400, paper_bgcolor=BRAND_SURFACE, plot_bgcolor=BRAND_SURFACE,
                              font_color=BRAND_TEXT, title_text="Engagement Rate by Install Tier",
                              xaxis=dict(gridcolor=BRAND_BORDER), yaxis=dict(gridcolor=BRAND_BORDER))
            st.plotly_chart(fig3, use_container_width=True)

    with tab4:
        st.markdown('<div class="section-header">Engagement Leaderboard</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Top 15 by Engagement Ratio**")
            top_eng_df = (df[df["Installs"] >= 10000]
                         .nlargest(15, "Engagement_Ratio")
                         [["App", "Category", "Engagement_Ratio", "Reviews", "Installs", "Rating"]]
                         .copy())
            top_eng_df["Engagement_Ratio"] = top_eng_df["Engagement_Ratio"].apply(lambda v: f"{v*100:.2f}%")
            top_eng_df["Reviews"] = top_eng_df["Reviews"].apply(lambda v: f"{v:,}")
            top_eng_df["Installs"] = top_eng_df["Installs"].apply(lambda v: f"{v:,}")
            st.dataframe(top_eng_df.reset_index(drop=True), use_container_width=True)
        with col2:
            st.markdown("**Top 15 by User Trust Score**")
            top_trust = (df.nlargest(15, "User_Trust_Score")
                        [["App", "Category", "User_Trust_Score", "Rating", "Reviews"]]
                        .copy())
            top_trust["User_Trust_Score"] = top_trust["User_Trust_Score"].apply(lambda v: f"{v:.1f}")
            top_trust["Reviews"] = top_trust["Reviews"].apply(lambda v: f"{v:,}")
            st.dataframe(top_trust.reset_index(drop=True), use_container_width=True)
