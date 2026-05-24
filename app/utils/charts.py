"""
charts.py — reusable Plotly chart factory with consistent dark-mode styling
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config import (
    BRAND_BG, BRAND_SURFACE, BRAND_BORDER, BRAND_TEXT, BRAND_MUTED,
    BRAND_PRIMARY, BRAND_SECONDARY, BRAND_ACCENT, BRAND_WARN,
    CATEGORY_COLORS, COLOR_SCALE,
)

# ── Base layout template ───────────────────────────────────────────────

def _base_layout(**kwargs) -> dict:
    defaults = dict(
        paper_bgcolor=BRAND_SURFACE,
        plot_bgcolor=BRAND_SURFACE,
        font=dict(family="'DM Sans', sans-serif", color=BRAND_TEXT, size=13),
        title_font=dict(size=17, color=BRAND_TEXT, family="'DM Sans', sans-serif"),
        margin=dict(t=55, b=40, l=50, r=20),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=BRAND_BORDER,
            font=dict(color=BRAND_TEXT),
        ),
        xaxis=dict(
            gridcolor=BRAND_BORDER,
            zerolinecolor=BRAND_BORDER,
            tickfont=dict(color=BRAND_MUTED),
        ),
        yaxis=dict(
            gridcolor=BRAND_BORDER,
            zerolinecolor=BRAND_BORDER,
            tickfont=dict(color=BRAND_MUTED),
        ),
    )
    defaults.update(kwargs)
    return defaults


def style(fig: go.Figure, title: str = "", height: int = 420) -> go.Figure:
    """Apply consistent dark-mode styling to any Plotly figure."""
    fig.update_layout(
        height=height,
        title_text=title,
        **_base_layout(),
    )
    return fig


# ── Individual chart factories ─────────────────────────────────────────

def bar_category_installs(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    data = (
        df.groupby("Category")["Installs"].sum()
        .nlargest(top_n)
        .reset_index()
        .rename(columns={"Installs": "Total Installs"})
    )
    fig = px.bar(
        data, x="Total Installs", y="Category", orientation="h",
        color="Total Installs", color_continuous_scale=COLOR_SCALE,
        text=data["Total Installs"].apply(lambda v: f"{v/1e9:.1f}B" if v >= 1e9 else f"{v/1e6:.0f}M"),
    )
    fig.update_traces(textposition="outside", textfont_color=BRAND_TEXT)
    fig.update_coloraxes(showscale=False)
    return style(fig, f"Top {top_n} Categories by Total Installs", height=460)


def donut_free_paid(df: pd.DataFrame) -> go.Figure:
    counts = df["Type"].value_counts().reset_index()
    counts.columns = ["Type", "Count"]
    fig = go.Figure(go.Pie(
        labels=counts["Type"],
        values=counts["Count"],
        hole=0.62,
        marker_colors=[BRAND_PRIMARY, BRAND_SECONDARY],
        textinfo="label+percent",
        textfont_color=BRAND_TEXT,
    ))
    total = counts["Count"].sum()
    fig.add_annotation(
        text=f"<b>{total:,}</b><br>Apps",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color=BRAND_TEXT),
    )
    return style(fig, "Free vs Paid Distribution", height=360)


def histogram_ratings(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(
        df, x="Rating", nbins=40,
        color_discrete_sequence=[BRAND_PRIMARY],
    )
    fig.update_traces(marker_line_color=BRAND_BG, marker_line_width=0.5)
    fig.add_vline(
        x=df["Rating"].mean(), line_dash="dash",
        line_color=BRAND_WARN,
        annotation_text=f"Mean {df['Rating'].mean():.2f}",
        annotation_font_color=BRAND_WARN,
    )
    return style(fig, "Rating Distribution Across All Apps", height=360)


def treemap_category(df: pd.DataFrame) -> go.Figure:
    data = (
        df.groupby("Category").agg(
            Apps=("App", "count"),
            Installs=("Installs", "sum"),
            Avg_Rating=("Rating", "mean"),
        ).reset_index()
    )
    fig = px.treemap(
        data, path=["Category"], values="Apps",
        color="Avg_Rating",
        color_continuous_scale=["#0D1117", BRAND_PRIMARY, BRAND_WARN],
        hover_data={"Installs": ":,.0f", "Avg_Rating": ":.2f"},
    )
    fig.update_traces(textfont_color="white", textfont_size=13)
    return style(fig, "Category Landscape — Size = App Count, Colour = Avg Rating", height=500)


def scatter_rating_installs(df: pd.DataFrame) -> go.Figure:
    sample = df.sample(min(2000, len(df)), random_state=42)
    fig = px.scatter(
        sample, x="Rating", y="Log_Installs",
        color="Type", size="User_Trust_Score",
        color_discrete_map={"Free": BRAND_PRIMARY, "Paid": BRAND_SECONDARY},
        hover_name="App",
        hover_data={"Rating": True, "Installs": ":,", "Type": True},
        opacity=0.7,
        size_max=18,
    )
    return style(fig, "Rating vs. Log(Installs) — Quality ≠ Popularity", height=460)


def heatmap_category_rating(df: pd.DataFrame) -> go.Figure:
    pivot = (
        df.groupby(["Category", "Rating_Bucket"])["App"]
        .count()
        .unstack(fill_value=0)
    )
    fig = px.imshow(
        pivot,
        color_continuous_scale=["#0D1117", BRAND_PRIMARY],
        aspect="auto",
        text_auto=True,
    )
    fig.update_traces(textfont_size=10)
    return style(fig, "App Count Heatmap — Category × Rating Bucket", height=600)


def bubble_category_metrics(df: pd.DataFrame) -> go.Figure:
    data = (
        df.groupby("Category").agg(
            Apps=("App", "count"),
            Avg_Rating=("Rating", "mean"),
            Total_Installs=("Installs", "sum"),
            Avg_Engagement=("Engagement_Ratio", "mean"),
        ).reset_index()
    )
    fig = px.scatter(
        data, x="Avg_Rating", y="Total_Installs",
        size="Apps", color="Avg_Engagement",
        hover_name="Category",
        color_continuous_scale=["#0D1117", BRAND_PRIMARY, BRAND_WARN],
        size_max=60, log_y=True,
        labels={"Total_Installs": "Total Installs (log)", "Avg_Rating": "Avg Rating"},
    )
    return style(fig, "Category Bubble Chart — Rating vs Installs, Size=Apps, Colour=Engagement", height=500)


def box_price_rating(df: pd.DataFrame) -> go.Figure:
    paid = df[(df["Type"] == "Paid") & (df["Price"] > 0) & (df["Price"] <= 50)]
    fig = px.box(
        paid, x="Price_Category", y="Rating",
        color="Price_Category",
        color_discrete_sequence=CATEGORY_COLORS,
        points="outliers",
    )
    return style(fig, "Rating Distribution by Price Tier (Paid Apps)", height=420)


def bar_revenue_by_category(df: pd.DataFrame, top_n: int = 12) -> go.Figure:
    data = (
        df[df["Type"] == "Paid"]
        .groupby("Category")["Revenue_Estimate"]
        .sum()
        .nlargest(top_n)
        .reset_index()
    )
    fig = px.bar(
        data, x="Category", y="Revenue_Estimate",
        color="Revenue_Estimate",
        color_continuous_scale=["#0D1117", BRAND_SECONDARY, BRAND_PRIMARY],
        text=data["Revenue_Estimate"].apply(lambda v: f"${v/1e6:.1f}M"),
    )
    fig.update_traces(textposition="outside", textfont_color=BRAND_TEXT)
    fig.update_coloraxes(showscale=False)
    return style(fig, f"Top {top_n} Categories by Estimated Revenue (Paid Apps)", height=420)


def violin_engagement(df: pd.DataFrame) -> go.Figure:
    top_cats = df["Category"].value_counts().head(10).index.tolist()
    sub = df[df["Category"].isin(top_cats)]
    fig = px.violin(
        sub, x="Category", y="Engagement_Ratio",
        color="Category", box=True,
        color_discrete_sequence=CATEGORY_COLORS,
    )
    fig.update_layout(showlegend=False)
    return style(fig, "Engagement Ratio Distribution by Top 10 Categories", height=460)


def pareto_installs(df: pd.DataFrame) -> go.Figure:
    sorted_df = df.sort_values("Installs", ascending=False).reset_index(drop=True)
    sorted_df["cumulative_pct"] = sorted_df["Installs"].cumsum() / sorted_df["Installs"].sum() * 100
    sorted_df["app_pct"] = (sorted_df.index + 1) / len(sorted_df) * 100

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=sorted_df["app_pct"], y=sorted_df["Installs"],
               name="Installs", marker_color=BRAND_PRIMARY, opacity=0.6),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=sorted_df["app_pct"], y=sorted_df["cumulative_pct"],
                   name="Cumulative %", line=dict(color=BRAND_ACCENT, width=2)),
        secondary_y=True,
    )
    fig.add_hline(y=80, line_dash="dash", line_color=BRAND_WARN,
                  annotation_text="80% threshold", secondary_y=True,
                  annotation_font_color=BRAND_WARN)
    fig.update_yaxes(title_text="Installs", secondary_y=False,
                     gridcolor=BRAND_BORDER, tickfont_color=BRAND_MUTED)
    fig.update_yaxes(title_text="Cumulative %", secondary_y=True,
                     gridcolor=BRAND_BORDER, tickfont_color=BRAND_MUTED)
    fig.update_xaxes(title_text="Top X% of Apps", gridcolor=BRAND_BORDER)
    return style(fig, "Pareto Analysis — Market Concentration of Installs", height=420)


def bar_sentiment(sentiment_df: pd.DataFrame, apps_df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    merged = sentiment_df.merge(
        apps_df[["App", "Installs"]].drop_duplicates("App"), on="App", how="inner"
    )
    top = merged.nlargest(top_n, "review_count")
    fig = go.Figure()
    for col, label, color in [
        ("pos_pct", "Positive", BRAND_PRIMARY),
        ("neu_pct", "Neutral", BRAND_WARN),
        ("neg_pct", "Negative", BRAND_ACCENT),
    ]:
        fig.add_trace(go.Bar(
            y=top["App"], x=top[col], name=label,
            orientation="h", marker_color=color,
        ))
    fig.update_layout(barmode="stack")
    return style(fig, f"Sentiment Breakdown — Top {top_n} Most Reviewed Apps", height=500)


def scatter_polarity_rating(sentiment_df: pd.DataFrame, apps_df: pd.DataFrame) -> go.Figure:
    merged = sentiment_df.merge(
        apps_df[["App", "Rating", "Installs", "Category"]].drop_duplicates("App"),
        on="App", how="inner",
    )
    fig = px.scatter(
        merged, x="avg_polarity", y="Rating",
        color="Category", size="review_count",
        color_discrete_sequence=CATEGORY_COLORS,
        hover_name="App",
        opacity=0.7, size_max=20,
    )
    return style(fig, "Sentiment Polarity vs. App Rating", height=460)


def bar_content_rating(df: pd.DataFrame) -> go.Figure:
    data = df["Content Rating"].value_counts().reset_index()
    data.columns = ["Content Rating", "Count"]
    fig = px.bar(
        data, x="Content Rating", y="Count",
        color="Count", color_continuous_scale=["#0D1117", BRAND_PRIMARY],
        text="Count",
    )
    fig.update_traces(textposition="outside")
    fig.update_coloraxes(showscale=False)
    return style(fig, "Apps by Content Rating (Audience)", height=380)


def missing_values_bar(raw_df: pd.DataFrame) -> go.Figure:
    mv = raw_df.isnull().sum().reset_index()
    mv.columns = ["Column", "Missing"]
    mv["Pct"] = (mv["Missing"] / len(raw_df) * 100).round(2)
    mv = mv[mv["Missing"] > 0].sort_values("Missing", ascending=True)
    fig = px.bar(
        mv, x="Pct", y="Column", orientation="h",
        color="Pct", color_continuous_scale=["#0D1117", BRAND_ACCENT],
        text=mv["Pct"].apply(lambda v: f"{v:.1f}%"),
    )
    fig.update_traces(textposition="outside")
    fig.update_coloraxes(showscale=False)
    return style(fig, "Missing Values by Column (%)", height=350)
