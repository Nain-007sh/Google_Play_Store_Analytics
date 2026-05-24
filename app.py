"""
app.py — Main entry point for the Google Play Store Analytics Platform
Run:  streamlit run app.py
"""
import streamlit as st
import pandas as pd
import sys, os

# ── Path setup ────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    APPS_RAW_PATH, REVIEWS_RAW_PATH, APPS_CLEAN_PATH, SENTIMENT_PATH,
    APP_TITLE, APP_ICON, LAYOUT,
    BRAND_BG, BRAND_SURFACE, BRAND_BORDER, BRAND_TEXT, BRAND_MUTED,
    BRAND_PRIMARY, BRAND_SECONDARY, BRAND_ACCENT, BRAND_WARN,
)
from app.utils.data_pipeline import run_pipeline

# ── Page config ───────────────────────────────────────────────────────
st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout=LAYOUT)

# ── Custom CSS ────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;700&display=swap');

  html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    background-color: {BRAND_BG};
    color: {BRAND_TEXT};
  }}

  /* Sidebar */
  section[data-testid="stSidebar"] {{
    background-color: {BRAND_SURFACE} !important;
    border-right: 1px solid {BRAND_BORDER};
  }}
  section[data-testid="stSidebar"] .css-1d391kg {{ padding-top: 2rem; }}

  /* Sidebar logo area */
  .sidebar-logo {{
    padding: 1rem 1.25rem 1.5rem;
    border-bottom: 1px solid {BRAND_BORDER};
    margin-bottom: 1rem;
  }}
  .sidebar-logo h1 {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: {BRAND_PRIMARY};
    margin: 0;
    letter-spacing: -0.3px;
  }}
  .sidebar-logo p {{
    font-size: 0.72rem;
    color: {BRAND_MUTED};
    margin: 0;
    margin-top: 2px;
  }}

  /* KPI Cards */
  .kpi-grid {{ display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; }}
  .kpi-card {{
    background: {BRAND_SURFACE};
    border: 1px solid {BRAND_BORDER};
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    flex: 1;
    min-width: 160px;
    position: relative;
    overflow: hidden;
    transition: border-color .2s;
  }}
  .kpi-card:hover {{ border-color: {BRAND_PRIMARY}; }}
  .kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--accent, {BRAND_PRIMARY});
    border-radius: 12px 12px 0 0;
  }}
  .kpi-label {{
    font-size: 0.72rem;
    color: {BRAND_MUTED};
    text-transform: uppercase;
    letter-spacing: .8px;
    margin-bottom: .35rem;
  }}
  .kpi-value {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: {BRAND_TEXT};
    line-height: 1;
  }}
  .kpi-delta {{
    font-size: 0.72rem;
    color: {BRAND_MUTED};
    margin-top: .3rem;
  }}
  .kpi-delta.up   {{ color: {BRAND_PRIMARY}; }}
  .kpi-delta.down {{ color: {BRAND_ACCENT};  }}

  /* Section headers */
  .section-header {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.15rem;
    font-weight: 600;
    color: {BRAND_TEXT};
    border-left: 3px solid {BRAND_PRIMARY};
    padding-left: .75rem;
    margin: 1.8rem 0 1rem;
  }}

  /* Page title */
  .page-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: {BRAND_TEXT};
    margin-bottom: .25rem;
  }}
  .page-subtitle {{
    font-size: .88rem;
    color: {BRAND_MUTED};
    margin-bottom: 1.5rem;
  }}

  /* Insight box */
  .insight-box {{
    background: rgba(0,212,170,.07);
    border: 1px solid rgba(0,212,170,.25);
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin: 1rem 0;
    font-size: .88rem;
    line-height: 1.6;
  }}
  .insight-box strong {{ color: {BRAND_PRIMARY}; }}

  /* Warning insight */
  .insight-box.warn {{
    background: rgba(255,107,107,.07);
    border-color: rgba(255,107,107,.25);
  }}
  .insight-box.warn strong {{ color: {BRAND_ACCENT}; }}

  /* Nav pills in sidebar */
  div[data-testid="stRadio"] > label {{
    display: block;
    padding: .55rem .9rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: .88rem;
    color: {BRAND_MUTED};
    margin-bottom: 2px;
    transition: background .15s, color .15s;
  }}
  div[data-testid="stRadio"] > label:hover {{ background:{BRAND_BORDER}; color:{BRAND_TEXT}; }}

  /* Hide default streamlit header */
  #MainMenu, footer, header {{ visibility: hidden; }}

  /* DataFrame table */
  .dataframe {{ background: {BRAND_SURFACE} !important; color: {BRAND_TEXT} !important; }}

  /* Metric delta */
  [data-testid="stMetricDelta"] {{ font-size: .78rem; }}

  /* Tab styling */
  .stTabs [data-baseweb="tab-list"] {{
    background: {BRAND_SURFACE};
    border-radius: 12px;
    padding: 6px 10px;
    gap: 12px;
    border: 1px solid {BRAND_BORDER};
  }}
  .stTabs [data-baseweb="tab"] {{
    color: {BRAND_MUTED};
    border-radius: 8px;
    font-size: .85rem;
    padding: 8px 22px !important;
    border: 1px solid transparent;
    transition: all .2s;
  }}
  .stTabs [data-baseweb="tab"]:hover {{
    background: {BRAND_BORDER} !important;
    color: {BRAND_TEXT} !important;
  }}
  .stTabs [aria-selected="true"] {{
    background: {BRAND_PRIMARY}22 !important;
    color: {BRAND_PRIMARY} !important;
    border-color: {BRAND_PRIMARY}55 !important;
    font-weight: 600;
  }}
</style>
""", unsafe_allow_html=True)


# ── Data loading with caching ─────────────────────────────────────────
@st.cache_data(show_spinner="⚙️  Running data pipeline…")
def load_data():
    result = run_pipeline(APPS_RAW_PATH, REVIEWS_RAW_PATH)
    return result["apps"], result["reviews"], result["sentiment"], result["kpis"]


apps_df, reviews_df, sentiment_df, kpis = load_data()

# Also load raw for data quality page
@st.cache_data(show_spinner=False)
def load_raw():
    return pd.read_csv(APPS_RAW_PATH)

raw_df = load_raw()

# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
      <h1>📊 Play Store IQ</h1>
      <p>Market Intelligence Platform v1.0</p>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        options=[
            "🏠  Executive Overview",
            "🗂️  Category Intelligence",
            "💬  User Engagement",
            "💰  Monetization Analytics",
            "🚀  App Success Analysis",
            "🔍  Data Quality",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Global filters
    st.markdown("#### ⚙️ Global Filters")
    selected_type = st.multiselect(
        "App Type", options=["Free", "Paid"], default=["Free", "Paid"]
    )
    all_cats = sorted(apps_df["Category"].unique())
    selected_cats = st.multiselect(
        "Categories", options=all_cats,
        default=all_cats,
        max_selections=33,
    )
    min_rating, max_rating = st.slider(
        "Rating Range", 1.0, 5.0, (1.0, 5.0), 0.1
    )
    min_installs = st.select_slider(
        "Min Installs",
        options=[0, 1000, 10000, 100000, 1_000_000, 10_000_000],
        value=0,
        format_func=lambda v: f"{v:,}" if v < 1_000_000 else f"{v//1_000_000}M",
    )

    st.markdown("---")
    st.markdown(f"<p style='font-size:.72rem;color:{BRAND_MUTED}'>Dataset: 9,659 apps · 64K reviews</p>", unsafe_allow_html=True)


# ── Filtered DataFrame ────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def filter_df(_df, types, cats, rmin, rmax, min_inst):
    mask = (
        _df["Type"].isin(types) &
        _df["Category"].isin(cats) &
        _df["Rating"].between(rmin, rmax) &
        (_df["Installs"] >= min_inst)
    )
    return _df[mask].copy()

filtered = filter_df(apps_df, tuple(selected_type), tuple(selected_cats),
                     min_rating, max_rating, min_installs)


# ── Page rendering ────────────────────────────────────────────────────
from app.pages import (
    page_overview, page_category, page_engagement,
    page_monetization, page_success, page_quality,
)

if "Executive" in page:
    page_overview.render(filtered, kpis, apps_df)
elif "Category" in page:
    page_category.render(filtered)
elif "Engagement" in page:
    page_engagement.render(filtered, sentiment_df)
elif "Monetization" in page:
    page_monetization.render(filtered)
elif "Success" in page:
    page_success.render(filtered, sentiment_df)
elif "Quality" in page:
    page_quality.render(raw_df, apps_df)