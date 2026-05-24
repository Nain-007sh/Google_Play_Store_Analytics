"""
config.py — centralised project configuration
"""
import os

# ── Paths ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DATA_CLEAN_DIR = os.path.join(BASE_DIR, "data", "cleaned")

APPS_RAW_PATH = os.path.join(DATA_RAW_DIR, "googleplaystore.csv")
REVIEWS_RAW_PATH = os.path.join(DATA_RAW_DIR, "googleplaystore_user_reviews.csv")
APPS_CLEAN_PATH = os.path.join(DATA_CLEAN_DIR, "apps_cleaned.csv")
SENTIMENT_PATH = os.path.join(DATA_CLEAN_DIR, "sentiment.csv")

# ── Colour palette ─────────────────────────────────────────────────────
BRAND_PRIMARY   = "#00D4AA"   # teal-green
BRAND_SECONDARY = "#7B61FF"   # violet
BRAND_ACCENT    = "#FF6B6B"   # coral
BRAND_WARN      = "#FFD93D"   # amber
BRAND_BG        = "#0D1117"   # near-black
BRAND_SURFACE   = "#161B22"   # card surface
BRAND_BORDER    = "#30363D"   # subtle border
BRAND_TEXT      = "#E6EDF3"   # primary text
BRAND_MUTED     = "#8B949E"   # muted text

# Plotly-compatible continuous colour scale
COLOR_SCALE = [
    [0.0,  "#0D1117"],
    [0.25, "#1A4A3C"],
    [0.5,  "#00875A"],
    [0.75, "#00D4AA"],
    [1.0,  "#7FFFD4"],
]

CATEGORY_COLORS = [
    "#00D4AA", "#7B61FF", "#FF6B6B", "#FFD93D", "#4ECDC4",
    "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD", "#98D8C8",
    "#F7DC6F", "#BB8FCE", "#85C1E9", "#82E0AA", "#F0B27A",
    "#AED6F1", "#A9DFBF", "#F9E79F", "#D7DBDD", "#FAD7A0",
]

# ── Dashboard settings ─────────────────────────────────────────────────
APP_TITLE = "Google Play Store · Market Intelligence Platform"
APP_ICON = "📊"
LAYOUT = "wide"
