"""
data_pipeline.py
================
Enterprise-grade data cleaning, feature engineering, and KPI computation
for the Google Play Store Analytics Platform.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")


# ─────────────────────────────────────────────
# 1. LOADING
# ─────────────────────────────────────────────

def load_raw_data(apps_path: str, reviews_path: str) -> tuple:
    """Load raw CSVs and return (apps_df, reviews_df)."""
    apps = pd.read_csv(apps_path)
    reviews = pd.read_csv(reviews_path)
    return apps, reviews


# ─────────────────────────────────────────────
# 2. CLEANING
# ─────────────────────────────────────────────

def clean_apps(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full professional cleaning pipeline for the apps dataset.

    Steps
    -----
    1. Drop junk rows (Category == '1.9')
    2. Remove duplicates (keep highest-reviews version)
    3. Type conversion: Reviews, Installs, Price, Rating, Last Updated
    4. Size → numeric MB
    5. Missing value imputation (median / mode / group-wise)
    6. Outlier clipping on Rating
    7. Feature engineering
    """
    df = df.copy()

    # ── 2.1 Drop rows where Category is a numeric artefact ──
    df = df[df["Category"] != "1.9"].reset_index(drop=True)

    # ── 2.2 Fix the single '0' Type row ──
    df.loc[df["Type"] == "0", "Type"] = "Free"

    # ── 2.3 Deduplicate: keep the record with the most reviews ──
    df["Reviews"] = pd.to_numeric(df["Reviews"], errors="coerce")
    df = df.sort_values("Reviews", ascending=False)
    df = df.drop_duplicates(subset="App", keep="first").reset_index(drop=True)

    # ── 2.4 Installs → int ──
    df["Installs"] = (
        df["Installs"]
        .str.replace(",", "", regex=False)
        .str.replace("+", "", regex=False)
        .str.strip()
    )
    df["Installs"] = pd.to_numeric(df["Installs"], errors="coerce")

    # ── 2.5 Price → float ──
    df["Price"] = (
        df["Price"]
        .str.replace("$", "", regex=False)
        .str.strip()
    )
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce").fillna(0.0)

    # ── 2.6 Rating → float, clip to [1, 5] ──
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    df["Rating"] = df["Rating"].clip(1.0, 5.0)

    # ── 2.7 Size → MB float ──
    def parse_size(s):
        s = str(s).strip()
        if s in ("Varies with device", "nan", ""):
            return np.nan
        if s.endswith("M"):
            return float(s[:-1])
        if s.endswith("k"):
            return float(s[:-1]) / 1024
        return np.nan

    df["Size_MB"] = df["Size"].apply(parse_size)

    # ── 2.8 Last Updated → datetime ──
    df["Last Updated"] = pd.to_datetime(df["Last Updated"], errors="coerce")

    # ── 2.9 Missing value imputation ──
    # Rating: group-wise median by Category (best proxy for similar apps)
    df["Rating"] = df.groupby("Category")["Rating"].transform(
        lambda x: x.fillna(x.median())
    )
    # Fallback global median for categories with all-NaN rating
    df["Rating"] = df["Rating"].fillna(df["Rating"].median())

    # Reviews: median by Category
    df["Reviews"] = df.groupby("Category")["Reviews"].transform(
        lambda x: x.fillna(x.median())
    )
    df["Reviews"] = df["Reviews"].fillna(df["Reviews"].median())

    # Installs: median by Category
    df["Installs"] = df.groupby("Category")["Installs"].transform(
        lambda x: x.fillna(x.median())
    )
    df["Installs"] = df["Installs"].fillna(df["Installs"].median())

    # Size_MB: median by Category
    df["Size_MB"] = df.groupby("Category")["Size_MB"].transform(
        lambda x: x.fillna(x.median())
    )
    df["Size_MB"] = df["Size_MB"].fillna(df["Size_MB"].median())

    # Type: mode
    df["Type"] = df["Type"].fillna(df["Type"].mode()[0])

    # Content Rating: mode
    df["Content Rating"] = df["Content Rating"].fillna(df["Content Rating"].mode()[0])

    # ── 2.10 Cast Reviews & Installs to int ──
    df["Reviews"] = df["Reviews"].astype(int)
    df["Installs"] = df["Installs"].astype(int)

    return df


def clean_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the user-reviews dataset."""
    df = df.copy()
    df = df.dropna(subset=["Sentiment"]).reset_index(drop=True)
    df["Sentiment_Polarity"] = pd.to_numeric(df["Sentiment_Polarity"], errors="coerce")
    df["Sentiment_Subjectivity"] = pd.to_numeric(df["Sentiment_Subjectivity"], errors="coerce")
    df["Sentiment_Polarity"] = df["Sentiment_Polarity"].fillna(0.0)
    df["Sentiment_Subjectivity"] = df["Sentiment_Subjectivity"].fillna(0.5)
    return df


# ─────────────────────────────────────────────
# 3. FEATURE ENGINEERING
# ─────────────────────────────────────────────

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create analytics-ready features on the cleaned apps DataFrame.

    New columns
    -----------
    Revenue_Estimate, Engagement_Ratio, Install_Bucket, Rating_Bucket,
    App_Age_Days, Update_Age_Days, Popularity_Score, Price_Category,
    Market_Share_Pct, User_Trust_Score, Log_Installs, Log_Reviews
    """
    df = df.copy()
    now = pd.Timestamp.now()

    # Revenue estimate (paid apps only: price × installs × 0.7 for store cut)
    df["Revenue_Estimate"] = np.where(
        df["Type"] == "Paid",
        df["Price"] * df["Installs"] * 0.70,
        0.0
    )

    # Engagement ratio: reviews per install (proxy for vocal user base)
    df["Engagement_Ratio"] = np.where(
        df["Installs"] > 0,
        df["Reviews"] / df["Installs"],
        0.0
    )

    # Install buckets
    install_bins = [0, 1_000, 10_000, 100_000, 1_000_000, 10_000_000, np.inf]
    install_labels = ["<1K", "1K–10K", "10K–100K", "100K–1M", "1M–10M", "10M+"]
    df["Install_Bucket"] = pd.cut(
        df["Installs"], bins=install_bins, labels=install_labels, right=False
    )

    # Rating buckets
    rating_bins = [0, 2.5, 3.5, 4.0, 4.5, 5.01]
    rating_labels = ["Poor (<2.5)", "Below Avg (2.5–3.5)", "Good (3.5–4.0)",
                     "Great (4.0–4.5)", "Excellent (4.5+)"]
    df["Rating_Bucket"] = pd.cut(
        df["Rating"], bins=rating_bins, labels=rating_labels, right=False
    )

    # App age (days since last update)
    df["Update_Age_Days"] = (now - df["Last Updated"]).dt.days.fillna(365)

    # Popularity score: log-normalised composite
    log_installs = np.log1p(df["Installs"])
    log_reviews = np.log1p(df["Reviews"])
    max_log_i = log_installs.max() or 1
    max_log_r = log_reviews.max() or 1
    df["Popularity_Score"] = (
        0.6 * (log_installs / max_log_i) +
        0.25 * (df["Rating"] / 5.0) +
        0.15 * (log_reviews / max_log_r)
    ).round(4) * 100

    # Price category
    price_bins = [-0.01, 0.001, 0.99, 2.99, 4.99, np.inf]
    price_labels = ["Free", "$0.01–$0.99", "$1–$2.99", "$3–$4.99", "$5+"]
    df["Price_Category"] = pd.cut(
        df["Price"], bins=price_bins, labels=price_labels, right=True
    )

    # Market share % within category
    cat_installs = df.groupby("Category")["Installs"].transform("sum")
    df["Market_Share_Pct"] = np.where(
        cat_installs > 0,
        (df["Installs"] / cat_installs * 100).round(4),
        0.0
    )

    # User Trust Score: rating × log(reviews+1) normalised 0–100
    trust_raw = df["Rating"] * np.log1p(df["Reviews"])
    max_trust = trust_raw.max() or 1
    df["User_Trust_Score"] = (trust_raw / max_trust * 100).round(2)

    # Log transforms (useful for scatter plots and ML)
    df["Log_Installs"] = np.log1p(df["Installs"])
    df["Log_Reviews"] = np.log1p(df["Reviews"])

    return df


# ─────────────────────────────────────────────
# 4. KPI COMPUTATION
# ─────────────────────────────────────────────

def compute_kpis(df: pd.DataFrame) -> dict:
    """Return a flat dict of executive-level KPIs."""
    total = len(df)
    paid = df[df["Type"] == "Paid"]
    free = df[df["Type"] == "Free"]

    kpis = {
        # Market
        "total_apps": total,
        "total_installs": int(df["Installs"].sum()),
        "avg_rating": round(df["Rating"].mean(), 2),
        "avg_reviews": int(df["Reviews"].mean()),
        "total_reviews": int(df["Reviews"].sum()),
        "total_categories": df["Category"].nunique(),
        "free_pct": round(len(free) / total * 100, 1),
        "paid_pct": round(len(paid) / total * 100, 1),
        "top_category": df.groupby("Category")["Installs"].sum().idxmax(),
        "avg_size_mb": round(df["Size_MB"].mean(), 1),

        # Quality
        "high_rated_pct": round((df["Rating"] >= 4.0).sum() / total * 100, 1),
        "avg_trust_score": round(df["User_Trust_Score"].mean(), 1),
        "top_rated_category": df.groupby("Category")["Rating"].mean().idxmax(),

        # Engagement
        "avg_engagement_ratio": round(df["Engagement_Ratio"].mean(), 5),
        "median_engagement_ratio": round(df["Engagement_Ratio"].median(), 5),

        # Monetization
        "total_revenue_est": round(df["Revenue_Estimate"].sum(), 0),
        "avg_price_paid": round(paid["Price"].mean(), 2) if len(paid) else 0,
        "paid_avg_installs": int(paid["Installs"].mean()) if len(paid) else 0,
        "free_avg_installs": int(free["Installs"].mean()) if len(free) else 0,

        # Growth / opportunity
        "avg_popularity_score": round(df["Popularity_Score"].mean(), 1),
        "median_installs": int(df["Installs"].median()),
    }
    return kpis


# ─────────────────────────────────────────────
# 5. SENTIMENT AGGREGATION
# ─────────────────────────────────────────────

def aggregate_sentiment(reviews: pd.DataFrame) -> pd.DataFrame:
    """
    Return per-app sentiment summary.
    Columns: App, pos_pct, neg_pct, neu_pct, avg_polarity, avg_subjectivity, review_count
    """
    grp = reviews.groupby("App").agg(
        review_count=("Sentiment", "count"),
        pos_count=("Sentiment", lambda x: (x == "Positive").sum()),
        neg_count=("Sentiment", lambda x: (x == "Negative").sum()),
        neu_count=("Sentiment", lambda x: (x == "Neutral").sum()),
        avg_polarity=("Sentiment_Polarity", "mean"),
        avg_subjectivity=("Sentiment_Subjectivity", "mean"),
    ).reset_index()

    grp["pos_pct"] = (grp["pos_count"] / grp["review_count"] * 100).round(1)
    grp["neg_pct"] = (grp["neg_count"] / grp["review_count"] * 100).round(1)
    grp["neu_pct"] = (grp["neu_count"] / grp["review_count"] * 100).round(1)

    return grp.drop(columns=["pos_count", "neg_count", "neu_count"])


# ─────────────────────────────────────────────
# 6. FULL PIPELINE ENTRY POINT
# ─────────────────────────────────────────────

def run_pipeline(apps_path: str, reviews_path: str) -> dict:
    """
    Execute the full ETL pipeline.

    Returns
    -------
    dict with keys: apps, reviews, sentiment, kpis
    """
    raw_apps, raw_reviews = load_raw_data(apps_path, reviews_path)

    cleaned_apps = clean_apps(raw_apps)
    cleaned_apps = engineer_features(cleaned_apps)

    cleaned_reviews = clean_reviews(raw_reviews)
    sentiment = aggregate_sentiment(cleaned_reviews)

    kpis = compute_kpis(cleaned_apps)

    return {
        "apps": cleaned_apps,
        "reviews": cleaned_reviews,
        "sentiment": sentiment,
        "kpis": kpis,
    }
