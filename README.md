# 📊 Google Play Store Market Intelligence Platform

> **Production-grade analytics platform** built on 9,659 apps and 64K user reviews from the Google Play Store ecosystem. Delivers executive-level market intelligence through a fully interactive multi-page Streamlit dashboard.

---

## 🎯 Business Problem

The Google Play Store hosts 3M+ apps. Developers, product teams, and investors lack a structured way to answer:

- What makes apps reach 10M+ installs?
- Which categories are over-saturated vs. underserved?
- Does rating actually drive downloads?
- Are paid apps economically viable?
- Where are the highest-ROI opportunities?

This platform answers all of these with data.

---

## 📁 Project Structure

```
Google_Play_Store_Analytics/
├── data/
│   ├── raw/                   # Original CSVs (gitignored)
│   └── cleaned/               # Pipeline outputs
├── app/
│   ├── pages/                 # One file per dashboard page
│   │   ├── page_overview.py
│   │   ├── page_category.py
│   │   ├── page_engagement.py
│   │   ├── page_monetization.py
│   │   ├── page_success.py
│   │   └── page_quality.py
│   └── utils/
│       ├── data_pipeline.py   # Full ETL pipeline
│       └── charts.py          # Plotly chart factory
├── app.py                     # Streamlit entry point
├── config.py                  # Paths, colours, constants
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

```bash
# 1. Clone / unzip the project
cd Google_Play_Store_Analytics

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Place raw CSVs in data/raw/
#    - googleplaystore.csv
#    - googleplaystore_user_reviews.csv

# 5. Launch the dashboard
streamlit run app.py
```

The pipeline runs automatically on first launch and caches results.

---

## 📊 Dashboard Pages

| Page                       | Description                                                          |
| -------------------------- | -------------------------------------------------------------------- |
| 🏠 Executive Overview      | KPI cards, install funnel, top categories, market snapshot           |
| 🗂️ Category Intelligence | Treemap, opportunity matrix, saturation analysis, heatmap            |
| 💬 User Engagement         | Review behaviour, sentiment analysis, engagement leaderboard         |
| 💰 Monetization Analytics  | Revenue by category, price strategy, free vs paid economics          |
| 🚀 App Success Analysis    | Success drivers, Pareto analysis, ML readiness, recommendations      |
| 🔍 Data Quality            | Missing values, deduplication log, outlier analysis, cleaning report |

---

## 📐 Engineered KPIs & Features

| Feature              | Description                                                |
| -------------------- | ---------------------------------------------------------- |
| `Revenue_Estimate` | Price × Installs × 0.70 (after 30% store cut)            |
| `Engagement_Ratio` | Reviews / Installs — vocal user proxy                     |
| `Popularity_Score` | Composite: 60% log-installs + 25% rating + 15% log-reviews |
| `User_Trust_Score` | Rating × log(Reviews+1), normalised 0–100                |
| `Install_Bucket`   | 6-tier segmentation: <1K to 10M+                           |
| `Rating_Bucket`    | Poor → Excellent quality tiers                            |
| `Update_Age_Days`  | Days since last update — maintenance signal               |
| `Market_Share_Pct` | App installs ÷ category total installs                    |

---

## 🔑 Key Findings

1. **GAME dominates** — 25%+ of all installs originate from the Games category
2. **Free × 100** — Free apps receive ~100× more installs than paid equivalents
3. **80% rate above 4.0** — Rating inflation is severe; algorithm favours 4.3+
4. **Top 1% capture ~60% of installs** — Power-law concentration in digital markets
5. **2% engagement baseline** — Only 1 in 50 users leaves a review
6. **Events & Education = untapped gems** — High ratings, low competition

---

## 🛠️ Tech Stack

- **Python 3.10+** — core language
- **Pandas / NumPy** — data manipulation
- **Plotly** — all interactive visualisations
- **Streamlit** — dashboard framework
- **Scikit-learn** — ML readiness features

---

## ☁️ Deployment

**Streamlit Community Cloud (recommended)**

1. Push to GitHub (exclude `data/raw/` via .gitignore — re-add CSVs or use cloud storage)
2. Connect repo at [share.streamlit.io](https://share.streamlit.io)
3. Set main file: `app.py`
4. Deploy

**Local / Docker**

```bash
streamlit run app.py --server.port 8501 --server.headless true
```

---

## 🔮 Future Improvements

- Live Play Store scraping via PlayScraper
- Time-series tracking with a PostgreSQL backend
- XGBoost install prediction model (notebook-ready)
- A/B test simulator for pricing strategy
- Category-level competitive intelligence alerts

---

## 👤 Author

Built as a portfolio-grade analytics project demonstrating end-to-end data engineering, EDA, and BI dashboard development.

*Dataset: [Kaggle — Google Play Store Apps](https://www.kaggle.com/datasets/lava18/google-play-store-apps)*
