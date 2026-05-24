"""Page 1 — Executive Overview"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from config import BRAND_PRIMARY, BRAND_SECONDARY, BRAND_ACCENT, BRAND_WARN, BRAND_MUTED, BRAND_TEXT, CATEGORY_COLORS
from app.utils import charts


def kpi_card(label, value, delta=None, accent=None, delta_dir="up"):
    accent = accent or BRAND_PRIMARY
    delta_html = ""
    if delta:
        cls = "up" if delta_dir == "up" else "down"
        delta_html = f'<div class="kpi-delta {cls}">{delta}</div>'
    return f"""
    <div class="kpi-card" style="--accent:{accent}">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      {delta_html}
    </div>"""


def render(df: pd.DataFrame, kpis: dict, full_df: pd.DataFrame):
    st.markdown('<div class="page-title">Executive Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">High-level market snapshot — Google Play Store ecosystem intelligence</div>', unsafe_allow_html=True)

    # ── Row 1: Core KPIs ─────────────────────────────────────────────
    st.markdown('<div class="section-header">Market Snapshot</div>', unsafe_allow_html=True)
    c1 = kpi_card("Total Apps", f"{len(df):,}", "in filtered view", BRAND_PRIMARY)
    c2 = kpi_card("Total Installs", f"{df['Installs'].sum()/1e9:.1f}B", "cumulative", BRAND_SECONDARY)
    c3 = kpi_card("Avg Rating", f"{df['Rating'].mean():.2f}", "out of 5.0", BRAND_WARN)
    c4 = kpi_card("Total Reviews", f"{df['Reviews'].sum()/1e9:.2f}B", "user feedback", BRAND_ACCENT)
    c5 = kpi_card("Categories", f"{df['Category'].nunique()}", "distinct verticals", BRAND_PRIMARY)
    c6 = kpi_card("Free Apps", f"{(df['Type']=='Free').sum()/len(df)*100:.1f}%", "of portfolio", BRAND_SECONDARY)
    st.markdown(f'<div class="kpi-grid">{c1}{c2}{c3}{c4}{c5}{c6}</div>', unsafe_allow_html=True)

    # ── Row 2: Charts ─────────────────────────────────────────────────
    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(charts.bar_category_installs(df, 15), use_container_width=True)
    with col2:
        st.plotly_chart(charts.donut_free_paid(df), use_container_width=True)

    # ── Row 3: Rating + Content ───────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts.histogram_ratings(df), use_container_width=True)
    with col2:
        st.plotly_chart(charts.bar_content_rating(df), use_container_width=True)

    # ── Insight box ───────────────────────────────────────────────────
    top_cat = df.groupby("Category")["Installs"].sum().idxmax()
    top_cat_installs = df.groupby("Category")["Installs"].sum().max()
    free_install_avg = df[df["Type"] == "Free"]["Installs"].mean()
    paid_install_avg = df[df["Type"] == "Paid"]["Installs"].mean() if (df["Type"] == "Paid").any() else 0
    multiplier = free_install_avg / paid_install_avg if paid_install_avg > 0 else 0

    st.markdown(f"""
    <div class="insight-box">
      <strong>📌 Executive Summary</strong><br>
      The filtered dataset contains <strong>{len(df):,} apps</strong> generating
      <strong>{df['Installs'].sum()/1e9:.1f}B cumulative installs</strong>.
      <strong>{top_cat.replace('_',' ').title()}</strong> dominates with
      <strong>{top_cat_installs/1e9:.1f}B installs</strong> — the undisputed install engine of the platform.
      Free apps average <strong>{free_install_avg/1e6:.1f}M installs</strong> versus
      <strong>{paid_install_avg/1e3:.0f}K for paid</strong> — a
      <strong>{multiplier:.0f}× gap</strong> that underscores freemium dominance.
      The average rating of <strong>{df['Rating'].mean():.2f}</strong> reflects rating inflation
      — apps below 4.0 face severe discovery penalties in the Play Store algorithm.
    </div>
    """, unsafe_allow_html=True)

    # ── Install Bucket Distribution ───────────────────────────────────
    st.markdown('<div class="section-header">Install Tier Distribution</div>', unsafe_allow_html=True)
    bucket_data = df["Install_Bucket"].value_counts().reset_index()
    bucket_data.columns = ["Bucket", "Count"]
    ordered = ["<1K", "1K–10K", "10K–100K", "100K–1M", "1M–10M", "10M+"]
    bucket_data["Bucket"] = pd.Categorical(bucket_data["Bucket"], categories=ordered, ordered=True)
    bucket_data = bucket_data.sort_values("Bucket")

    fig = px.funnel(bucket_data, x="Count", y="Bucket",
                    color_discrete_sequence=[BRAND_PRIMARY])
    fig.update_layout(
        paper_bgcolor="#161B22", plot_bgcolor="#161B22",
        font_color=BRAND_TEXT, height=360,
        margin=dict(t=40, b=20),
        title_text="App Install Funnel — Volume by Tier",
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Top 20 Apps table ─────────────────────────────────────────────
    st.markdown('<div class="section-header">Top 20 Apps by Installs</div>', unsafe_allow_html=True)
    top20 = (df.nlargest(20, "Installs")
             [["App", "Category", "Rating", "Installs", "Reviews", "Type", "Popularity_Score"]]
             .copy())
    top20["Installs"] = top20["Installs"].apply(lambda v: f"{v:,.0f}")
    top20["Reviews"] = top20["Reviews"].apply(lambda v: f"{v:,.0f}")
    top20["Rating"] = top20["Rating"].apply(lambda v: f"{v:.1f} ⭐")
    top20["Popularity_Score"] = top20["Popularity_Score"].apply(lambda v: f"{v:.1f}")
    st.dataframe(top20.reset_index(drop=True), use_container_width=True, height=480)

    # ── CSV Export ────────────────────────────────────────────────────
    st.download_button(
        "⬇️  Export Filtered Data (CSV)",
        data=df.to_csv(index=False),
        file_name="playstore_filtered.csv",
        mime="text/csv",
    )
