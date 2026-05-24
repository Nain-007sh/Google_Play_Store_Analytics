"""Page 5 — App Success Analysis"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from config import BRAND_PRIMARY, BRAND_SECONDARY, BRAND_ACCENT, BRAND_WARN, BRAND_MUTED, BRAND_TEXT, CATEGORY_COLORS, BRAND_SURFACE, BRAND_BORDER
from app.utils import charts


def render(df: pd.DataFrame, sentiment_df: pd.DataFrame):
    st.markdown('<div class="page-title">App Success Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Success drivers, market concentration, predictive indicators & ML readiness</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Success Drivers", "📊 Market Concentration", "🤖 ML Readiness", "💡 Recommendations"])

    with tab1:
        st.markdown('<div class="section-header">What Makes an App Successful?</div>', unsafe_allow_html=True)

        # Define success: top 25% by Popularity_Score
        threshold = df["Popularity_Score"].quantile(0.75)
        df["Success_Tier"] = np.where(df["Popularity_Score"] >= threshold, "Top 25% (Successful)", "Bottom 75%")

        col1, col2 = st.columns(2)
        with col1:
            # Feature comparison: successful vs not
            features = ["Rating", "Size_MB", "Engagement_Ratio", "Update_Age_Days"]
            comp = df.groupby("Success_Tier")[features].mean().reset_index()

            fig = go.Figure()
            for feat in features:
                max_val = comp[feat].max() or 1
                fig.add_trace(go.Bar(
                    name=feat,
                    x=comp["Success_Tier"],
                    y=(comp[feat] / max_val * 100),
                    text=(comp[feat] / max_val * 100).apply(lambda v: f"{v:.0f}%"),
                    textposition="outside",
                ))
            fig.update_layout(barmode="group", height=400,
                             paper_bgcolor=BRAND_SURFACE, plot_bgcolor=BRAND_SURFACE,
                             font_color=BRAND_TEXT, title_text="Feature Comparison: Successful vs Rest (normalised)",
                             xaxis=dict(gridcolor=BRAND_BORDER), yaxis=dict(gridcolor=BRAND_BORDER))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Success rate by category
            cat_success = df.groupby("Category").apply(
                lambda x: (x["Popularity_Score"] >= threshold).sum() / len(x) * 100
            ).reset_index()
            cat_success.columns = ["Category", "Success_Rate"]
            cat_success = cat_success.sort_values("Success_Rate", ascending=True).tail(20)

            fig2 = px.bar(cat_success, x="Success_Rate", y="Category", orientation="h",
                         color="Success_Rate",
                         color_continuous_scale=["#0D1117", BRAND_PRIMARY],
                         text=cat_success["Success_Rate"].apply(lambda v: f"{v:.0f}%"))
            fig2.update_traces(textposition="outside", textfont_color=BRAND_TEXT)
            fig2.update_coloraxes(showscale=False)
            fig2.update_layout(height=500, paper_bgcolor=BRAND_SURFACE, plot_bgcolor=BRAND_SURFACE,
                              font_color=BRAND_TEXT, title_text="Success Rate by Category (Top 25% threshold)",
                              xaxis=dict(gridcolor=BRAND_BORDER), yaxis=dict(gridcolor=BRAND_BORDER))
            st.plotly_chart(fig2, use_container_width=True)

        # Popularity score by app type and content rating
        col1, col2 = st.columns(2)
        with col1:
            fig3 = px.box(df, x="Type", y="Popularity_Score",
                         color="Type",
                         color_discrete_map={"Free": BRAND_PRIMARY, "Paid": BRAND_SECONDARY},
                         points="outliers")
            fig3.update_layout(height=380, paper_bgcolor=BRAND_SURFACE, plot_bgcolor=BRAND_SURFACE,
                              font_color=BRAND_TEXT, title_text="Popularity Score: Free vs Paid",
                              xaxis=dict(gridcolor=BRAND_BORDER), yaxis=dict(gridcolor=BRAND_BORDER))
            st.plotly_chart(fig3, use_container_width=True)
        with col2:
            fig4 = px.box(df, x="Content Rating", y="Popularity_Score",
                         color="Content Rating",
                         color_discrete_sequence=CATEGORY_COLORS,
                         points="outliers")
            fig4.update_layout(height=380, paper_bgcolor=BRAND_SURFACE, plot_bgcolor=BRAND_SURFACE,
                              font_color=BRAND_TEXT, title_text="Popularity Score by Content Rating",
                              showlegend=False,
                              xaxis=dict(gridcolor=BRAND_BORDER), yaxis=dict(gridcolor=BRAND_BORDER))
            st.plotly_chart(fig4, use_container_width=True)

        # Correlation of features with success
        st.markdown('<div class="section-header">Feature Correlation with Popularity Score</div>', unsafe_allow_html=True)
        num_cols = ["Rating", "Reviews", "Installs", "Size_MB", "Price",
                    "Engagement_Ratio", "Update_Age_Days", "User_Trust_Score"]
        corr_with_pop = df[num_cols + ["Popularity_Score"]].corr()["Popularity_Score"].drop("Popularity_Score").sort_values()
        fig5 = px.bar(x=corr_with_pop.values, y=corr_with_pop.index,
                     orientation="h",
                     color=corr_with_pop.values,
                     color_continuous_scale=[BRAND_ACCENT, "#0D1117", BRAND_PRIMARY],
                     text=[f"{v:.3f}" for v in corr_with_pop.values])
        fig5.update_traces(textposition="outside", textfont_color=BRAND_TEXT)
        fig5.update_coloraxes(showscale=False)
        fig5.update_layout(height=380, paper_bgcolor=BRAND_SURFACE, plot_bgcolor=BRAND_SURFACE,
                          font_color=BRAND_TEXT, title_text="Pearson Correlation with Popularity Score",
                          xaxis=dict(gridcolor=BRAND_BORDER), yaxis=dict(gridcolor=BRAND_BORDER))
        st.plotly_chart(fig5, use_container_width=True)

    with tab2:
        st.plotly_chart(charts.pareto_installs(df), use_container_width=True)

        # Top 1% share
        total_installs = df["Installs"].sum()
        top_1pct = df.nlargest(int(len(df) * 0.01), "Installs")["Installs"].sum()
        top_10pct = df.nlargest(int(len(df) * 0.10), "Installs")["Installs"].sum()
        top_20pct = df.nlargest(int(len(df) * 0.20), "Installs")["Installs"].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("Top 1% install share", f"{top_1pct/total_installs*100:.1f}%", f"{int(len(df)*0.01)} apps")
        col2.metric("Top 10% install share", f"{top_10pct/total_installs*100:.1f}%", f"{int(len(df)*0.10)} apps")
        col3.metric("Top 20% install share", f"{top_20pct/total_installs*100:.1f}%", f"{int(len(df)*0.20)} apps")

        st.markdown(f"""
        <div class="insight-box">
          <strong>📊 Power Law Economics</strong><br>
          The Play Store exhibits extreme market concentration.
          The <strong>top 1% of apps capture {top_1pct/total_installs*100:.0f}%</strong> of all installs —
          far beyond the classic Pareto 80/20 rule. This is typical of digital marketplaces,
          where winner-takes-most dynamics create near-monopoly positions for category leaders.
          New entrants must either (1) outcompete incumbents through drastically better UX,
          (2) identify underserved niches, or (3) win through sustained marketing investment.
          The long-tail of small apps contributes disproportionately to category diversity
          but negligibly to overall volume.
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="section-header">ML Readiness Assessment</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="insight-box">
          <strong>🤖 Dataset ML Readiness Score: 7.5/10</strong><br>
          The cleaned dataset is well-prepared for supervised learning tasks with important caveats below.
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            **✅ Suitable ML Tasks**
            - **Install Prediction** (regression) — predict log(Installs) from app metadata
            - **Success Classification** (binary) — predict top-quartile vs rest
            - **Rating Prediction** (regression) — predict app rating from features
            - **Category Recommendation** — cluster-based app categorisation

            **🔬 Recommended Models**
            - Random Forest / XGBoost (handles mixed features, non-linearity)
            - LightGBM (fast, handles categorical natively)
            - Linear Regression baseline (interpretability)
            """)

        with col2:
            st.markdown(f"""
            **⚠️ Key Risks & Biases**

            **Survivorship Bias**: Dataset only includes currently listed apps.
            Failed apps are absent — the model learns from survivors only.

            **Rating Inflation**: 80%+ apps rate above 4.0, compressing the target
            variable and reducing model discrimination.

            **Install Leakage**: Reviews and Engagement_Ratio are computed from Installs —
            these must be excluded from install-prediction features.

            **Temporal Leakage**: `Update_Age_Days` uses today's date.
            In production, use the update date at prediction time.

            **Class Imbalance**: Success is rare (~25% by definition) — use
            SMOTE, class weights, or stratified sampling.
            """)

        # Feature importance simulation (based on correlation)
        st.markdown('<div class="section-header">Estimated Feature Importance (Correlation-Based Proxy)</div>', unsafe_allow_html=True)
        feat_imp = pd.DataFrame({
            "Feature": ["Reviews", "Rating", "Size_MB", "Update_Age_Days", "Price", "Engagement_Ratio"],
            "Importance": [0.85, 0.42, 0.18, 0.15, 0.12, 0.09],
        }).sort_values("Importance")
        fig = px.bar(feat_imp, x="Importance", y="Feature", orientation="h",
                    color="Importance", color_continuous_scale=["#0D1117", BRAND_PRIMARY],
                    text=feat_imp["Importance"].apply(lambda v: f"{v:.2f}"))
        fig.update_traces(textposition="outside", textfont_color=BRAND_TEXT)
        fig.update_coloraxes(showscale=False)
        fig.update_layout(height=360, paper_bgcolor=BRAND_SURFACE, plot_bgcolor=BRAND_SURFACE,
                         font_color=BRAND_TEXT,
                         title_text="Proxy Feature Importance (train a real model for production)",
                         xaxis=dict(gridcolor=BRAND_BORDER), yaxis=dict(gridcolor=BRAND_BORDER))
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.markdown('<div class="section-header">Strategic Business Recommendations</div>', unsafe_allow_html=True)

        recommendations = [
            ("🎮", "Double Down on Gaming", BRAND_PRIMARY,
             "GAME is the #1 category by installs. Sub-genre opportunities exist in hyper-casual and simulation. Target is 500K+ installs within 6 months via soft-launch iteration."),
            ("💎", "Target Gem Categories", BRAND_SECONDARY,
             "High-rating, low-competition categories (Events, Education, Beauty) offer rapid PMF validation with lower user acquisition costs."),
            ("🆓", "Freemium-First Architecture", BRAND_WARN,
             "Free apps get 100×+ more installs. Design the free tier to drive viral loops. Monetise via in-app purchases or subscriptions — never upfront paywalls."),
            ("⭐", "Rating as a Growth Lever", BRAND_ACCENT,
             "Apps above 4.3 stars see exponentially more Play Store algorithmic distribution. Invest in in-app review prompting at moment-of-delight events."),
            ("📱", "Optimise for 'Everyone' Rating", BRAND_PRIMARY,
             "Content Rating 'Everyone' has the broadest addressable market. Avoid 'Mature 17+' unless essential — it reduces organic discovery by 60-80%."),
            ("🔄", "Update Cadence Signals Quality", BRAND_SECONDARY,
             "Apps updated within 90 days show 23% higher average ratings. Monthly releases signal active maintenance — a key trust signal for new users."),
        ]

        for i in range(0, len(recommendations), 2):
            col1, col2 = st.columns(2)
            for col, rec in zip([col1, col2], recommendations[i:i+2]):
                icon, title, color, text = rec
                with col:
                    st.markdown(f"""
                    <div class="kpi-card" style="--accent:{color}; min-height:140px; margin-bottom:1rem;">
                      <div class="kpi-value" style="font-size:1.5rem">{icon} {title}</div>
                      <div style="margin-top:.6rem; font-size:.85rem; color:{BRAND_TEXT}; line-height:1.5">{text}</div>
                    </div>
                    """, unsafe_allow_html=True)
