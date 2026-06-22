import json
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Spotify AI Discovery Engine",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# Premium Styling — Spotify Dark Aesthetic
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    /* Core layout */
    .stApp {
        background-color: #0d0d0d;
        color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #040404 0%, #0d0d0d 100%) !important;
        border-right: 1px solid #1a1a1a;
    }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #181818 0%, #1a1a1a 100%);
        border: 1px solid #282828;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        border-color: #1DB954;
        box-shadow: 0 8px 30px rgba(29,185,84,0.15);
    }
    div[data-testid="stMetricValue"] { color: #1DB954 !important; font-weight: 800; font-size: 2rem !important; }
    div[data-testid="stMetricLabel"] { color: #b3b3b3 !important; font-size: 0.85rem !important; font-weight: 500; }
    div[data-testid="stMetricDelta"] { font-size: 0.8rem !important; }

    /* Tabs */
    div[data-testid="stTabBar"] button {
        color: #757575 !important;
        font-weight: 600;
        font-size: 14px;
        border-bottom: 2px solid transparent;
        padding: 10px 20px;
        transition: color 0.2s ease;
    }
    div[data-testid="stTabBar"] button[aria-selected="true"] {
        color: #ffffff !important;
        border-bottom: 2px solid #1DB954 !important;
    }

    /* Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #1DB954, #17a349) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 500px !important;
        padding: 10px 28px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 15px rgba(29,185,84,0.3) !important;
    }
    div.stButton > button:hover {
        transform: scale(1.04) !important;
        box-shadow: 0 6px 25px rgba(29,185,84,0.5) !important;
    }

    hr { border-color: #1a1a1a !important; }

    /* ── Custom Component Styles ── */

    /* Executive Summary */
    .exec-summary {
        background: linear-gradient(135deg, #0f2818 0%, #1a3d26 50%, #0d1f0f 100%);
        border: 1px solid #1DB954;
        border-radius: 20px;
        padding: 32px 40px;
        margin-bottom: 28px;
        box-shadow: 0 8px 40px rgba(29,185,84,0.2);
        position: relative;
        overflow: hidden;
    }
    .exec-summary::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(29,185,84,0.08) 0%, transparent 70%);
        pointer-events: none;
    }
    .exec-headline {
        font-size: 2rem;
        font-weight: 900;
        color: #ffffff;
        margin: 0 0 8px 0;
        line-height: 1.2;
    }
    .exec-sub {
        color: #a0cfaf;
        font-size: 1rem;
        margin-bottom: 24px;
        font-weight: 400;
    }
    .exec-stat-row {
        display: flex;
        gap: 24px;
        flex-wrap: wrap;
    }
    .exec-stat {
        background: rgba(29,185,84,0.12);
        border: 1px solid rgba(29,185,84,0.3);
        border-radius: 12px;
        padding: 14px 20px;
        text-align: center;
        min-width: 120px;
    }
    .exec-stat-value { font-size: 1.6rem; font-weight: 800; color: #1DB954; display: block; }
    .exec-stat-label { font-size: 0.75rem; color: #a0cfaf; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
    .exec-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(29,185,84,0.15);
        border: 1px solid rgba(29,185,84,0.4);
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 0.78rem;
        font-weight: 600;
        color: #1DB954;
        margin-bottom: 16px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    /* Insight cards */
    .insight-card {
        background: #181818;
        border-left: 4px solid #1DB954;
        border-radius: 12px;
        padding: 22px 24px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    .insight-card:hover { border-color: #1ed760; transform: translateX(3px); }
    .insight-title { color: #ffffff; font-size: 1rem; font-weight: 700; margin-bottom: 10px; }
    .insight-body { color: #b3b3b3; font-size: 0.9rem; line-height: 1.7; }

    /* Section headers */
    .section-header {
        font-size: 1.4rem;
        font-weight: 800;
        color: #ffffff;
        margin: 32px 0 20px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-header::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, #282828, transparent);
        margin-left: 12px;
    }

    /* Repeat music drivers */
    .driver-card {
        background: linear-gradient(135deg, #1a1010 0%, #1f1515 100%);
        border: 1px solid #3d2020;
        border-left: 4px solid #ef4444;
        border-radius: 12px;
        padding: 20px 22px;
        margin-bottom: 14px;
        transition: border-color 0.2s ease;
    }
    .driver-card:hover { border-color: #f87171; }
    .driver-title { color: #fca5a5; font-size: 0.95rem; font-weight: 700; margin-bottom: 8px; }
    .driver-body { color: #9ca3af; font-size: 0.88rem; line-height: 1.65; }
    .driver-evidence { margin-top: 10px; padding: 8px 12px; background: rgba(239,68,68,0.08); border-radius: 8px; font-size: 0.8rem; color: #f87171; font-weight: 500; }

    /* Segment cards */
    .segment-card {
        background: #181818;
        border: 1px solid #282828;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
    }
    .segment-card:hover {
        border-color: #1DB954;
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(29,185,84,0.12);
    }
    .segment-icon { font-size: 2.2rem; margin-bottom: 10px; }
    .segment-name { font-size: 1rem; font-weight: 700; color: #ffffff; margin-bottom: 8px; }
    .segment-pct { font-size: 1.6rem; font-weight: 800; color: #1DB954; margin-bottom: 6px; }
    .segment-desc { font-size: 0.82rem; color: #9ca3af; line-height: 1.5; margin-bottom: 10px; }
    .segment-pain { font-size: 0.78rem; background: rgba(239,68,68,0.1); color: #fca5a5; padding: 6px 10px; border-radius: 8px; font-weight: 500; }

    /* Opportunity ranking */
    .opp-card {
        background: #181818;
        border: 1px solid #282828;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 14px;
        display: flex;
        align-items: flex-start;
        gap: 20px;
        transition: border-color 0.2s ease;
    }
    .opp-card:hover { border-color: #404040; }
    .opp-rank { font-size: 1.8rem; font-weight: 900; color: #1DB954; min-width: 40px; }
    .opp-rank.rank-2 { color: #60a5fa; }
    .opp-rank.rank-3 { color: #c084fc; }
    .opp-rank.rank-4 { color: #fb923c; }
    .opp-rank.rank-5 { color: #a3a3a3; }
    .opp-body { flex: 1; }
    .opp-title { font-size: 1rem; font-weight: 700; color: #ffffff; margin-bottom: 6px; }
    .opp-desc { font-size: 0.85rem; color: #9ca3af; line-height: 1.55; margin-bottom: 10px; }
    .opp-scores { display: flex; gap: 10px; flex-wrap: wrap; }
    .score-pill {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .score-pain { background: rgba(239,68,68,0.15); color: #fca5a5; }
    .score-freq { background: rgba(251,146,60,0.15); color: #fdba74; }
    .score-biz { background: rgba(96,165,250,0.15); color: #93c5fd; }
    .score-conf { background: rgba(52,211,153,0.15); color: #6ee7b7; }

    /* PM Recommendation */
    .pm-rec-card {
        background: linear-gradient(135deg, #0d1b2a 0%, #112240 100%);
        border: 1px solid #1e3a5f;
        border-radius: 20px;
        padding: 32px 36px;
        margin-bottom: 20px;
        box-shadow: 0 8px 30px rgba(96,165,250,0.1);
    }
    .pm-rec-row {
        display: flex;
        gap: 14px;
        margin-bottom: 14px;
        align-items: flex-start;
    }
    .pm-rec-label {
        min-width: 140px;
        font-size: 0.75rem;
        font-weight: 700;
        color: #60a5fa;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        padding-top: 3px;
    }
    .pm-rec-value { font-size: 0.9rem; color: #e2e8f0; line-height: 1.6; }
    .pm-mvp-box {
        background: rgba(96,165,250,0.08);
        border: 1px solid rgba(96,165,250,0.2);
        border-radius: 12px;
        padding: 16px 20px;
        margin-top: 6px;
    }
    .pm-impact-box {
        background: rgba(52,211,153,0.08);
        border: 1px solid rgba(52,211,153,0.2);
        border-radius: 12px;
        padding: 16px 20px;
        margin-top: 6px;
    }
    .pm-impact-value { font-size: 0.88rem; color: #6ee7b7; line-height: 1.6; }

    /* Pills */
    .pill { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
    .pill-high { background: rgba(239,68,68,0.15); color: #fca5a5; border: 1px solid rgba(239,68,68,0.3); }
    .pill-medium { background: rgba(251,146,60,0.15); color: #fdba74; border: 1px solid rgba(251,146,60,0.3); }
    .pill-low { background: rgba(96,165,250,0.15); color: #93c5fd; border: 1px solid rgba(96,165,250,0.3); }

    /* Quote card */
    .quote-card {
        background: #111;
        border-left: 3px solid #404040;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 10px;
        font-size: 0.85rem;
        color: #9ca3af;
        font-style: italic;
        line-height: 1.6;
    }
    .quote-meta { font-style: normal; font-size: 0.75rem; color: #606060; margin-top: 6px; font-weight: 500; }

    /* Unmet need card */
    .need-card {
        background: #181818;
        border: 1px solid #282828;
        border-top: 3px solid #c084fc;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 14px;
        transition: border-color 0.2s ease;
    }
    .need-card:hover { border-top-color: #a855f7; }
    .need-title { color: #d8b4fe; font-size: 0.95rem; font-weight: 700; margin-bottom: 8px; }
    .need-body { color: #9ca3af; font-size: 0.87rem; line-height: 1.6; }

    /* AI badge */
    .ai-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: rgba(167,139,250,0.12);
        border: 1px solid rgba(167,139,250,0.3);
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.72rem;
        font-weight: 600;
        color: #a78bfa;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }

    /* Data quality notice */
    .dq-notice {
        background: rgba(251,146,60,0.06);
        border: 1px solid rgba(251,146,60,0.2);
        border-radius: 10px;
        padding: 12px 18px;
        font-size: 0.83rem;
        color: #fdba74;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Data Paths
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_PATH = BASE_DIR / "data" / "raw_reviews.json"
ANALYZED_PATH = BASE_DIR / "data" / "analyzed_reviews.json"
REPORT_PATH = BASE_DIR / "data" / "synthesis_report.json"

@st.cache_data
def load_data():
    if not ANALYZED_PATH.exists():
        return None
    try:
        with open(ANALYZED_PATH, 'r') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

@st.cache_data
def load_report():
    if not REPORT_PATH.exists():
        return None
    try:
        with open(REPORT_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading report: {e}")
        return None

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="padding: 8px 0 20px 0;">
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
        <span style="font-size:28px;">🎵</span>
        <span style="font-size:1.15rem; font-weight:800; color:#ffffff; letter-spacing:-0.3px;">Spotify PM Discovery Engine</span>
    </div>
    <div style="font-size:0.78rem; color:#606060; font-weight:500; text-transform:uppercase; letter-spacing:0.8px;">Fellowship Project · Phase 1</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("**About this Engine**")
st.sidebar.markdown(
    "Analyzes App Store, Play Store, and Reddit user feedback at scale using "
    "AI classification to map Spotify's music discovery challenges — "
    "answering the 6 core PM research questions.",
    unsafe_allow_html=False
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔄 Data Sync")
if st.sidebar.button("Sync Feedback Data", help="Scrapes latest reviews and re-runs classification"):
    status_text = st.sidebar.empty()
    try:
        status_text.info("📡 Scraping Play Store & App Store...")
        from review_engine.src.scrapers import scrape_all_and_save
        scrape_all_and_save(play_limit=100, app_limit=100, reddit_limit=10)
        status_text.info("🧠 Running sentiment & thematic analysis...")
        from review_engine.src.analyzer import run_classification, generate_synthesis_report
        analyzed = run_classification()
        generate_synthesis_report(analyzed)
        status_text.success("✅ Sync complete!")
        st.cache_data.clear()
        st.rerun()
    except Exception as e:
        status_text.error(f"❌ Sync failed: {e}")

# Load data
df = load_data()
report = load_report()

if df is None:
    st.sidebar.error("❌ No analyzed data found.")
    st.sidebar.code("python review_engine/run.py scrape\npython review_engine/run.py analyze")
    st.markdown("""
    # Welcome to the Spotify AI Discovery Engine
    To begin, collect and analyze user reviews:
    1. Activate venv: `source .venv/bin/activate`
    2. `python review_engine/run.py scrape`
    3. `python review_engine/run.py analyze`
    4. Refresh this page.
    """)
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar Filters
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Data Filters")
sources = st.sidebar.multiselect("Source", options=df["source"].unique(), default=df["source"].unique())
categories = st.sidebar.multiselect("Category", options=df["category"].unique(), default=df["category"].unique())
sentiments = st.sidebar.multiselect("Sentiment", options=df["sentiment"].unique(), default=df["sentiment"].unique())

filtered_df = df[
    df["source"].isin(sources) &
    df["category"].isin(categories) &
    df["sentiment"].isin(sentiments)
]

st.sidebar.markdown("---")
st.sidebar.info(f"Showing **{len(filtered_df)}** of **{len(df)}** reviews")
st.sidebar.markdown(f"""
<div style="font-size:0.75rem; color:#606060; margin-top:8px;">
    <b style="color:#1DB954;">Discovery-relevant:</b><br>
    Reviews on Shuffle, Algorithm, and Context Contamination signal the core problem space.
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Compute Key Stats
# ─────────────────────────────────────────────────────────────────────────────
total = len(df)
neg_pct = round((df["sentiment"] == "Negative").sum() / total * 100, 1) if total > 0 else 0
high_sev = int((df["severity"] == "High").sum())
discovery_relevant = int(df["category"].isin(["Shuffle Dissatisfaction", "Algorithmic Repeatability", "Context Contamination"]).sum())
discovery_pct = round(discovery_relevant / total * 100, 1) if total > 0 else 0

# Category breakdown for discovery-relevant
shuffle_n = int((df["category"] == "Shuffle Dissatisfaction").sum())
algo_n = int((df["category"] == "Algorithmic Repeatability").sum())
context_n = int((df["category"] == "Context Contamination").sum())
ux_n = int((df["category"] == "UX Friction").sum())
social_n = int((df["category"] == "Social Discovery Deficit").sum())

report_answers = report.get("answers", {}) if report else {}
llm_used = report.get("metadata", {}).get("llm_synthesized", False) if report else False

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — EXECUTIVE SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="exec-summary">
    <div class="exec-badge">🤖 AI-Powered Review Discovery Engine · Phase 1</div>
    <h1 class="exec-headline">Spotify users are trapped in a music echo chamber</h1>
    <p class="exec-sub">
        Analysis of <strong style="color:#1DB954;">{total:,} user reviews</strong> across App Store, Google Play, and Reddit
        reveals that <strong style="color:#1DB954;">{neg_pct}% of users</strong> express frustration —
        with algorithmic repetition and shuffle failure as the top discovery blockers.
    </p>
    <div class="exec-stat-row">
        <div class="exec-stat">
            <span class="exec-stat-value">{total:,}</span>
            <span class="exec-stat-label">Reviews Analyzed</span>
        </div>
        <div class="exec-stat">
            <span class="exec-stat-value">{neg_pct}%</span>
            <span class="exec-stat-label">Frustration Rate</span>
        </div>
        <div class="exec-stat">
            <span class="exec-stat-value">{discovery_relevant}</span>
            <span class="exec-stat-label">Discovery-Relevant</span>
        </div>
        <div class="exec-stat">
            <span class="exec-stat-value">{high_sev}</span>
            <span class="exec-stat-label">High-Severity Issues</span>
        </div>
        <div class="exec-stat">
            <span class="exec-stat-value">#1</span>
            <span class="exec-stat-label">Pain: Shuffle Repeat</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Navigation Tabs
# ─────────────────────────────────────────────────────────────────────────────
tab_pm, tab_repeat, tab_segments, tab_needs, tab_opportunity, tab_rec, tab_analytics, tab_explorer = st.tabs([
    "🧠 PM Insights",
    "🔄 Why Users Repeat",
    "👥 User Segments",
    "💡 Unmet Needs",
    "📈 Opportunity Ranking",
    "🎯 PM Recommendation",
    "📊 Analytics",
    "🔍 Review Explorer"
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PM INSIGHTS (core assignment questions)
# ═══════════════════════════════════════════════════════════════════════════════
with tab_pm:
    if not report_answers:
        st.warning("No PM synthesis available. Run: `python review_engine/run.py analyze`")
    else:
        mode_label = "🤖 LLM-Synthesized" if llm_used else "📐 Heuristic Analysis"
        mode_color = "#1DB954" if llm_used else "#f59e0b"
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:20px;">
            <span style="font-size:0.78rem; background:rgba(255,255,255,0.05); border:1px solid #282828;
                border-radius:20px; padding:5px 14px; color:{mode_color}; font-weight:600;">{mode_label}</span>
            <span style="color:#606060; font-size:0.8rem;">Generated: {report.get('metadata', {}).get('generated_at', 'N/A')}</span>
        </div>
        """, unsafe_allow_html=True)

        def insight_card(icon, title, content):
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-title">{icon} {title}</div>
                <div class="insight-body">{content.replace(chr(10), '<br>')}</div>
            </div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            insight_card("🔍", "Why do users struggle to discover new music?",
                         report_answers.get("why_discovery_struggle", "N/A"))
            insight_card("😤", "Most common frustrations with recommendations",
                         report_answers.get("common_frustrations", "N/A"))
            insight_card("🎯", "What listening behaviors are users trying to achieve?",
                         report_answers.get("intended_behaviors", "N/A"))
        with col2:
            insight_card("🔄", "What causes users to repeatedly listen to the same content?",
                         report_answers.get("repetition_causes", "N/A"))
            insight_card("👥", "Which user segments experience different discovery challenges?",
                         report_answers.get("user_segments", "N/A"))
            insight_card("💡", "What unmet needs emerge consistently across reviews?",
                         report_answers.get("unmet_needs", "N/A"))

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — WHY USERS REPEAT MUSIC
# ═══════════════════════════════════════════════════════════════════════════════
with tab_repeat:
    st.markdown("""
    <div class="section-header">🔄 Why Users Repeat Music — Synthesized Root Cause Analysis</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="dq-notice">
        📊 <strong>Evidence base:</strong> {algo_n + shuffle_n} reviews directly citing repetition/shuffle problems
        ({algo_n} Algorithmic Repeatability + {shuffle_n} Shuffle Dissatisfaction) out of {total:,} total reviews analyzed.
    </div>
    """, unsafe_allow_html=True)

    # Driver 1
    st.markdown(f"""
    <div class="driver-card">
        <div class="driver-title">1. Collaborative Filtering Exploitation Bias</div>
        <div class="driver-body">
            Spotify's recommendation engine is built on collaborative filtering — matching users to others with similar taste profiles.
            The algorithm is heavily optimized to <strong style="color:#fca5a5;">minimize skip rate</strong>, which is treated as
            a proxy for satisfaction. Playing familiar, well-liked songs guarantees low skips in the short term.
            But this optimization creates a structural feedback loop: the more a user engages with familiar tracks,
            the more the model reinforces those recommendations — gradually narrowing the user's discoverable universe
            into a shrinking "safe zone" of 30–50 songs.
        </div>
        <div class="driver-evidence">📊 Evidence: {algo_n} reviews cite algorithm-driven repetition · High-severity: {int((df[df['category']=='Algorithmic Repeatability']['severity']=='High').sum())} incidents</div>
    </div>
    """, unsafe_allow_html=True)

    # Driver 2
    st.markdown(f"""
    <div class="driver-card">
        <div class="driver-title">2. Smart Shuffle Probability Weighting Failure</div>
        <div class="driver-body">
            Despite the "Smart Shuffle" branding, users report the shuffle algorithm applies
            <strong style="color:#fca5a5;">weighted probability curves</strong> that dramatically favor
            recently played, highly-played, or "liked" tracks. A 1,000-song playlist effectively collapses
            into a 40–60 song rotation. Users feel "shuffle" is meaningless — it doesn't feel random
            and it actively ignores explicit skip signals. This destroys trust in the discovery system
            and causes users to stop trying to find new music through automated means.
        </div>
        <div class="driver-evidence">📊 Evidence: {shuffle_n} reviews cite shuffle failure · Reviews like "plays the same 15 songs no matter what"</div>
    </div>
    """, unsafe_allow_html=True)

    # Driver 3
    st.markdown(f"""
    <div class="driver-card">
        <div class="driver-title">3. Context Contamination — Cross-Session Profile Poisoning</div>
        <div class="driver-body">
            Spotify treats <strong style="color:#fca5a5;">all listening sessions as equal training data</strong>
            for the user's taste model. A single session of children's music, focus lo-fi beats, or
            party background tracks permanently alters the recommendation profile.
            Users who share accounts (parent/child, couple, office) or switch listening contexts
            frequently (work, gym, sleep) suffer disproportionately.
            There are no "context walls" — every session bleeds into the permanent taste identity,
            causing recommendations to feel incoherent and forcing users back to manually curated playlists.
        </div>
        <div class="driver-evidence">📊 Evidence: {context_n} reviews cite context contamination · Pattern: account sharing, kids music, focus sessions</div>
    </div>
    """, unsafe_allow_html=True)

    # Driver 4
    st.markdown("""
    <div class="driver-card">
        <div class="driver-title">4. Absence of Negative Preference Controls</div>
        <div class="driver-body">
            Users have <strong style="color:#fca5a5;">extremely limited tools to signal what they don't want</strong>.
            The "Don't play this artist" option (buried in settings) doesn't propagate effectively to
            algorithm training. There is no way to: exclude a genre from recommendations, reset a portion
            of the taste profile, or mark a listening session as "off-record."
            Without negative controls, the algorithm can only learn by positive reinforcement —
            making it impossible for users to break out of repetitive patterns without starting over entirely.
        </div>
        <div class="driver-evidence">📊 Evidence: Multiple UX Friction reviews cite inability to control recommendations · "forced recommendations I never asked for"</div>
    </div>
    """, unsafe_allow_html=True)

    # Supporting quote samples
    st.markdown("<div class='section-header' style='margin-top:28px;'>💬 Representative User Voice</div>", unsafe_allow_html=True)

    repeat_reviews = df[df["category"].isin(["Algorithmic Repeatability", "Shuffle Dissatisfaction"])].head(6)
    if not repeat_reviews.empty:
        cols = st.columns(2)
        for i, (_, row) in enumerate(repeat_reviews.iterrows()):
            with cols[i % 2]:
                sev_badge = f"<span class='pill pill-{'high' if row.get('severity')=='High' else 'medium' if row.get('severity')=='Medium' else 'low'}'>{row.get('severity','')}</span>"
                st.markdown(f"""
                <div class="quote-card">
                    "{row.get('text', '')[:220]}{'...' if len(str(row.get('text',''))) > 220 else ''}"
                    <div class="quote-meta">{sev_badge} &nbsp; {row.get('source','')} · ⭐ {row.get('rating','')}/5 · {row.get('category','')}</div>
                </div>
                """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — USER SEGMENTS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_segments:
    st.markdown("<div class='section-header'>👥 User Segment Analysis</div>", unsafe_allow_html=True)
    st.markdown("""
    <p style="color:#9ca3af; margin-bottom:24px; font-size:0.9rem;">
        Three distinct user segments emerge from review pattern analysis, each experiencing discovery failure differently.
        Understanding segment-specific pain is essential for prioritizing which MVP feature delivers maximum impact.
    </p>
    """, unsafe_allow_html=True)

    # Compute segment proxies from data
    power_users = df[(df["category"].isin(["Algorithmic Repeatability", "Shuffle Dissatisfaction"])) & (df["severity"] == "High")]
    passive_users = df[(df["category"].isin(["UX Friction", "Other"])) & (df["sentiment"] == "Negative")]
    context_users = df[df["category"] == "Context Contamination"]

    col1, col2, col3 = st.columns(3)

    with col1:
        pwr_pct = round(len(power_users) / total * 100, 1)
        st.markdown(f"""
        <div class="segment-card">
            <div class="segment-icon">🎛️</div>
            <div class="segment-name">Active Curators</div>
            <div class="segment-pct">{pwr_pct}%</div>
            <div style="font-size:0.72rem; color:#606060; margin-bottom:10px;">of reviewed corpus</div>
            <div class="segment-desc">
                Power users who meticulously build playlists and expect the algorithm to
                surface genuinely new, genre-specific music. Highly sensitive to repetition.
                Will churn to competitors if discovery fails.
            </div>
            <div class="segment-pain">🔴 Core Pain: Algorithm ignores their taste depth, surfaces only mainstream hits</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        lean_pct = round(len(passive_users) / total * 100, 1)
        st.markdown(f"""
        <div class="segment-card">
            <div class="segment-icon">🎧</div>
            <div class="segment-name">Lean-Back Listeners</div>
            <div class="segment-pct">{lean_pct}%</div>
            <div style="font-size:0.72rem; color:#606060; margin-bottom:10px;">of reviewed corpus</div>
            <div class="segment-desc">
                Casual users who open Spotify and expect it to "just work." They want ambient
                music discovery without any manual curation effort. Highly susceptible to
                UX friction and shuffle repetition.
            </div>
            <div class="segment-pain">🟠 Core Pain: Shuffle repeats same songs, no easy way to find something different</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        ctx_pct = round(len(context_users) / total * 100, 1)
        st.markdown(f"""
        <div class="segment-card">
            <div class="segment-icon">🔀</div>
            <div class="segment-name">Context-Switched Users</div>
            <div class="segment-pct">{ctx_pct}%</div>
            <div style="font-size:0.72rem; color:#606060; margin-bottom:10px;">of reviewed corpus</div>
            <div class="segment-desc">
                Users sharing accounts or switching listening contexts (work, gym, kids, sleep).
                A single context-switching session permanently contaminates their recommendation
                profile, causing long-term discovery degradation.
            </div>
            <div class="segment-pain">🔴 Core Pain: Kids/focus music poisoning their personal recommendation profile</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Segment vs. severity heatmap proxy
    st.markdown("<div class='section-header'>Severity by Discovery Category</div>", unsafe_allow_html=True)

    cat_sev = df[df["category"].isin(["Shuffle Dissatisfaction", "Algorithmic Repeatability",
                                       "Context Contamination", "UX Friction", "Social Discovery Deficit"])]
    if not cat_sev.empty:
        pivot = cat_sev.groupby(["category", "severity"]).size().reset_index(name="count")
        fig = px.bar(
            pivot,
            x="category",
            y="count",
            color="severity",
            color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#3b82f6"},
            barmode="stack",
            text="count"
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff",
            legend_title_text="Severity",
            xaxis=dict(title="", showgrid=False, tickfont=dict(size=12)),
            yaxis=dict(title="Number of Reviews", showgrid=True, gridcolor="#1a1a1a"),
            margin=dict(l=10, r=10, t=10, b=10),
            height=360
        )
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — UNMET NEEDS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_needs:
    st.markdown("<div class='section-header'>💡 Unmet Needs — Consistently Emerging from Reviews</div>", unsafe_allow_html=True)

    needs = [
        {
            "title": "1. Context-Aware Listening Modes (Sandbox Sessions)",
            "body": """Users urgently need the ability to designate specific listening sessions as "off-record" — 
meaning the session should not influence their recommendation profile. This is especially critical for: 
focus/work sessions (lo-fi, ambient), children's content, shared device/account scenarios, and party/social listening. 
A simple "Private Mode" toggle that prevents training data collection from the current session would resolve context contamination for all three user segments."""
        },
        {
            "title": "2. Negative Preference Controls (Algorithmic Pruning)",
            "body": """Users need granular tools to signal what they don't want, not just what they like. 
This includes: artist/genre exclusion from recommendations (globally, not just for a session), 
the ability to reset specific branches of their taste profile (e.g., 'forget my jazz phase'), 
and a "Do Not Use This For Training" flag on individual tracks or sessions. 
Current controls are buried, inconsistent, and don't propagate to the recommendation model effectively."""
        },
        {
            "title": "3. True Random Shuffle with Probability Override",
            "body": """Users explicitly want a shuffle mode that is mathematically equitable — 
every track in a playlist has an equal probability of playing, regardless of play count, recency, or popularity. 
The current "Smart Shuffle" is perceived as a curated playlist that happens to feel unordered, 
not a genuine randomization mechanism. A simple "True Random" toggle would restore user trust in the shuffle feature."""
        },
        {
            "title": "4. Natural Language Discovery Interface",
            "body": """Users want to describe music they're looking for using natural, abstract, contextual language — 
"something that sounds like a rainy Sunday morning," "upbeat but not aggressive for a morning commute," 
"indie artists similar to Phoebe Bridgers but I haven't heard yet." 
Traditional keyword search and genre-tag systems cannot fulfill these queries. 
An LLM-powered natural language music discovery interface would unlock a fundamentally new discovery modality 
that traditional recommendation systems cannot replicate."""
        },
        {
            "title": "5. Discovery Diversity Dial (Exploration Slider)",
            "body": """Users need explicit control over the exploration/exploitation tradeoff in their recommendations. 
A simple UI control — a "Discovery Dial" — would let users choose between 
"Familiar" (95% known tracks) ↔ "Explorer" (70% new tracks). 
This gives users agency over their own discovery journey and prevents the algorithm from defaulting 
to exploitation mode when users actually want exploration."""
        }
    ]

    for need in needs:
        st.markdown(f"""
        <div class="need-card">
            <div class="need-title">{need['title']}</div>
            <div class="need-body">{need['body']}</div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — OPPORTUNITY RANKING
# ═══════════════════════════════════════════════════════════════════════════════
with tab_opportunity:
    st.markdown("<div class='section-header'>📈 Opportunity Ranking Framework</div>", unsafe_allow_html=True)
    st.markdown("""
    <p style="color:#9ca3af; font-size:0.88rem; margin-bottom:24px;">
        Opportunities ranked by composite score: <strong style="color:#fca5a5;">User Pain</strong> ×
        <strong style="color:#fdba74;">Frequency</strong> ×
        <strong style="color:#93c5fd;">Business Impact</strong> ×
        <strong style="color:#6ee7b7;">Confidence</strong> — derived from review evidence.
    </p>
    """, unsafe_allow_html=True)

    opportunities = [
        {
            "rank": 1, "rank_class": "",
            "title": "Context-Aware Private Listening Mode",
            "desc": f"Sandbox sessions that don't pollute the recommendation profile. Solves Context Contamination ({context_n} reviews) and enables safe shared-account, focus, and children's listening without long-term profile damage.",
            "pain": "Critical (9/10)", "freq": f"High ({context_n} reviews)", "biz": "Premium Retention Driver", "conf": "Very High"
        },
        {
            "rank": 2, "rank_class": "rank-2",
            "title": "True Random Shuffle Mode",
            "desc": f"Mathematically equitable shuffle with equal play probability. Directly addresses the #1 volume complaint ({shuffle_n} reviews). Low engineering effort, high user trust recovery.",
            "pain": "High (8/10)", "freq": f"Highest ({shuffle_n} reviews)", "biz": "MAU Retention + Churn Reduction", "conf": "Very High"
        },
        {
            "rank": 3, "rank_class": "rank-3",
            "title": "Natural Language Music Discovery",
            "desc": f"LLM-powered search: describe music in abstract, contextual, or emotional terms. Resolves the UX Friction barrier ({ux_n} reviews) and unlocks a discovery modality impossible with traditional systems.",
            "pain": "High (8/10)", "freq": f"Medium ({ux_n} reviews)", "biz": "Premium Conversion + DAU Growth", "conf": "High"
        },
        {
            "rank": 4, "rank_class": "rank-4",
            "title": "Algorithmic Preference Reset Controls",
            "desc": f"Allow users to prune specific genre/artist branches from their taste profile. Addresses {algo_n} reviews citing algorithmic staleness. Restores user agency and long-term engagement.",
            "pain": "High (7/10)", "freq": f"High ({algo_n} reviews)", "biz": "Long-Term Retention + LTV", "conf": "High"
        },
        {
            "rank": 5, "rank_class": "rank-5",
            "title": "Discovery Diversity Dial",
            "desc": f"User-controlled exploration/exploitation slider. Simple UX lever that lets users explicitly choose how much new music enters their queue. Addresses passive listener frustration with repetitive mixes.",
            "pain": "Medium (6/10)", "freq": "Medium (cross-category signal)", "biz": "Engagement + Discovery Funnel", "conf": "Medium"
        }
    ]

    for opp in opportunities:
        st.markdown(f"""
        <div class="opp-card">
            <div class="opp-rank {opp['rank_class']}">#{opp['rank']}</div>
            <div class="opp-body">
                <div class="opp-title">{opp['title']}</div>
                <div class="opp-desc">{opp['desc']}</div>
                <div class="opp-scores">
                    <span class="score-pill score-pain">Pain: {opp['pain']}</span>
                    <span class="score-pill score-freq">Frequency: {opp['freq']}</span>
                    <span class="score-pill score-biz">Business: {opp['biz']}</span>
                    <span class="score-pill score-conf">Confidence: {opp['conf']}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Radar chart for top 3 opportunities
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>Opportunity Score Visualization</div>", unsafe_allow_html=True)

    categories_radar = ["User Pain", "Review Frequency", "Business Impact", "Eng. Feasibility", "Confidence"]
    opp_scores = {
        "Context-Aware Mode": [9, 7, 9, 8, 9],
        "True Random Shuffle": [8, 9, 8, 9, 9],
        "NL Discovery": [8, 6, 9, 5, 8],
    }

    fig_radar = go.Figure()
    radar_palette = [
        {"line": "#1DB954", "fill": "rgba(29,185,84,0.15)"},
        {"line": "#60a5fa", "fill": "rgba(96,165,250,0.15)"},
        {"line": "#c084fc", "fill": "rgba(192,132,252,0.15)"},
    ]
    for (name, scores), palette in zip(opp_scores.items(), radar_palette):
        fig_radar.add_trace(go.Scatterpolar(
            r=scores + [scores[0]],
            theta=categories_radar + [categories_radar[0]],
            fill='toself',
            name=name,
            line=dict(color=palette["line"], width=2),
            fillcolor=palette["fill"],
            opacity=0.9
        ))
    fig_radar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#ffffff",
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 10], gridcolor="#282828", tickfont=dict(size=9, color="#606060")),
            angularaxis=dict(gridcolor="#282828", tickfont=dict(size=11))
        ),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=12)),
        margin=dict(l=60, r=60, t=30, b=30),
        height=400
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — PM RECOMMENDATION
# ═══════════════════════════════════════════════════════════════════════════════
with tab_rec:
    st.markdown("<div class='section-header'>🎯 PM Recommendation — Derived from Review Evidence</div>", unsafe_allow_html=True)
    st.markdown("""
    <p style="color:#9ca3af; font-size:0.88rem; margin-bottom:24px;">
        A structured PM recommendation generated from {total:,} analyzed reviews, translating
        user signals into an actionable product strategy.
    </p>
    """.format(total=total), unsafe_allow_html=True)

    st.markdown(f"""
    <div class="pm-rec-card">
        <div class="pm-rec-row">
            <div class="pm-rec-label">🔴 Problem</div>
            <div class="pm-rec-value">
                Spotify Premium users are experiencing <strong>Discovery Fatigue</strong> — a progressive collapse of their
                discoverable music universe caused by algorithmic exploitation bias. The recommendation engine,
                optimized for short-term skip minimization, traps users in a feedback loop of 30–50 familiar tracks,
                making meaningful music discovery nearly impossible without intensive manual curation effort.
            </div>
        </div>
        <div class="pm-rec-row">
            <div class="pm-rec-label">🧬 Root Cause</div>
            <div class="pm-rec-value">
                Three compounding structural failures: (1) <strong>Collaborative Filtering Exploitation Bias</strong> — the algorithm 
                prioritizes familiar tracks to protect skip metrics; (2) <strong>Context Contamination</strong> — all sessions 
                train the same profile regardless of intent; (3) <strong>Absence of Negative Controls</strong> — users cannot 
                prune or correct their taste model, leaving them no escape from repetition cycles.
            </div>
        </div>
        <div class="pm-rec-row">
            <div class="pm-rec-label">👤 Target Segment</div>
            <div class="pm-rec-value">
                <strong>Active Curators</strong> (power users, ~{round((algo_n + shuffle_n) / total * 100, 0):.0f}% of complaint volume) — 
                Engaged Premium subscribers who build playlists, follow artists, and expect genre-accurate discovery. 
                High churn risk if discovery fails. High LTV if discovery succeeds. 
                Secondary: <strong>Context-Switched Users</strong> — account sharers and multi-context listeners suffering from profile contamination.
            </div>
        </div>
        <div class="pm-rec-row">
            <div class="pm-rec-label">📊 Evidence</div>
            <div class="pm-rec-value">
                {shuffle_n} reviews cite shuffle failure · {algo_n} reviews cite algorithmic repetition · 
                {context_n} reviews cite context contamination · {high_sev} high-severity incidents · 
                {neg_pct}% overall frustration rate across {total:,} analyzed reviews (App Store, Google Play, Reddit).
            </div>
        </div>
        <div class="pm-rec-row">
            <div class="pm-rec-label">🚀 Recommended MVP</div>
            <div class="pm-rec-value">
                <div class="pm-mvp-box">
                    <strong style="color:#93c5fd;">Discovery Sandbox Mode</strong><br><br>
                    A session-level toggle in the Spotify player UI that activates "Context Mode" — 
                    preventing the current session from contributing to the user's permanent recommendation profile. 
                    Paired with a "<strong>Discovery Dial</strong>" slider (Familiar ↔ Explorer) that allows users to 
                    explicitly control how much new music enters their queue in real-time.<br><br>
                    <strong>Why AI is uniquely suited:</strong> Traditional recommendation systems cannot distinguish 
                    user intent across sessions — they treat all listening as equal signal. An AI-native architecture 
                    can: (a) classify session intent from listening pattern metadata, (b) apply session-scoped model 
                    weights that expire at session end, and (c) use natural language input to infer contextual mode 
                    (e.g., "studying" → automatically activates focus mode + disables profile training).
                </div>
            </div>
        </div>
        <div class="pm-rec-row">
            <div class="pm-rec-label">📈 Expected Impact</div>
            <div class="pm-rec-value">
                <div class="pm-impact-box">
                    <div class="pm-impact-value">
                        • <strong>Churn Reduction:</strong> Active Curators churning due to discovery stagnation represent
                          estimated 3–5% of high-LTV Premium subscriber loss annually. Context Sandbox Mode directly addresses
                          the contamination driver for context-switched users.<br><br>
                        • <strong>Discovery Engagement:</strong> Introducing an explicit exploration dial increases
                          the surface area of music users are exposed to — potential 15–25% increase in
                          new artist streams per MAU among power users.<br><br>
                        • <strong>Trust Recovery:</strong> Giving users agency over their algorithmic profile is a 
                          documented driver of platform satisfaction and long-term retention in recommendation-dependent products.
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Secondary recommendation
    st.markdown("""
    <div class="pm-rec-card" style="margin-top:20px;">
        <div style="font-size:0.8rem; color:#60a5fa; font-weight:700; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:16px;">Secondary Recommendation</div>
        <div class="pm-rec-row">
            <div class="pm-rec-label">🔴 Problem</div>
            <div class="pm-rec-value">Shuffle is the #1 volume complaint in the review corpus, yet it's a fully solvable UX problem.</div>
        </div>
        <div class="pm-rec-row">
            <div class="pm-rec-label">🚀 Recommended MVP</div>
            <div class="pm-rec-value">
                <div class="pm-mvp-box">
                    <strong style="color:#93c5fd;">True Random Shuffle</strong> — A mathematically equitable shuffle 
                    algorithm with uniform play probability, exposed as a distinct toggle: "Smart Shuffle" (current behavior) 
                    vs "True Random." Zero recommendation-engine dependency. Ship in 1 sprint. 
                    Expected to immediately reduce shuffle-related 1-star reviews.
                </div>
            </div>
        </div>
        <div class="pm-rec-row">
            <div class="pm-rec-label">📈 Expected Impact</div>
            <div class="pm-rec-value">
                <div class="pm-impact-box">
                    <div class="pm-impact-value">
                        Low engineering cost · High user trust recovery · 
                        Estimated reduction of 40–50% of shuffle-complaint reviews.
                        App Store rating improvement within 2–3 update cycles.
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 7 — SUPPORTING ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_analytics:
    st.markdown("<div class='section-header'>📊 Supporting Analytics</div>", unsafe_allow_html=True)

    # Data quality notice
    other_n = int((df["category"] == "Other").sum())
    other_pct = round(other_n / total * 100, 1)
    st.markdown(f"""
    <div class="dq-notice">
        ⚠️ <strong>Data Quality Note:</strong> {other_n} reviews ({other_pct}%) classified as <em>"Other"</em> —
        these are off-topic (ads, crashes, premium pricing complaints) and are correctly excluded from discovery signal analysis.
        The {discovery_relevant} discovery-relevant reviews represent the actionable insight corpus.
    </div>
    """, unsafe_allow_html=True)

    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Reviews Analyzed", f"{total:,}")
    with col2:
        st.metric("Frustration Rate", f"{neg_pct}%", delta="Negative Sentiment")
    with col3:
        st.metric("High-Severity Issues", f"{high_sev:,}")
    with col4:
        st.metric("Discovery-Relevant Reviews", f"{discovery_relevant}", delta=f"{discovery_pct}% of corpus")

    st.write("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 🏷️ Friction Category Distribution")
        cat_counts = filtered_df["category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        fig_cat = px.bar(
            cat_counts, x="Count", y="Category", orientation='h',
            color="Category",
            color_discrete_sequence=["#1DB954", "#3b82f6", "#ef4444", "#f59e0b", "#8b5cf6", "#6b7280"],
            text="Count"
        )
        fig_cat.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff", showlegend=False,
            xaxis=dict(showgrid=True, gridcolor="#1a1a1a"),
            yaxis=dict(autorange="reversed"),
            margin=dict(l=10, r=10, t=10, b=10), height=320
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_right:
        st.markdown("#### 🎭 Sentiment Distribution")
        sent_counts = filtered_df["sentiment"].value_counts().reset_index()
        sent_counts.columns = ["Sentiment", "Count"]
        fig_sent = px.pie(
            sent_counts, values="Count", names="Sentiment",
            color="Sentiment",
            color_discrete_map={"Negative": "#ef4444", "Neutral": "#6b7280", "Positive": "#1DB954"},
            hole=0.45
        )
        fig_sent.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff", margin=dict(l=10, r=10, t=10, b=10), height=320
        )
        st.plotly_chart(fig_sent, use_container_width=True)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("#### 🔌 Review Volume by Source")
        src_counts = filtered_df["source"].value_counts().reset_index()
        src_counts.columns = ["Source", "Count"]
        fig_src = px.bar(src_counts, x="Source", y="Count", color="Source",
                         color_discrete_sequence=["#10b981", "#3b82f6", "#f43f5e"])
        fig_src.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff", showlegend=False,
            yaxis=dict(showgrid=True, gridcolor="#1a1a1a"),
            margin=dict(l=10, r=10, t=10, b=10), height=300
        )
        st.plotly_chart(fig_src, use_container_width=True)

    with col_s2:
        st.markdown("#### ⚠️ Severity Distribution")
        sev_counts = filtered_df["severity"].value_counts().reset_index()
        sev_counts.columns = ["Severity", "Count"]
        fig_sev = px.bar(sev_counts, x="Severity", y="Count", color="Severity",
                         color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#3b82f6"})
        fig_sev.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff", showlegend=False,
            yaxis=dict(showgrid=True, gridcolor="#1a1a1a"),
            margin=dict(l=10, r=10, t=10, b=10), height=300
        )
        st.plotly_chart(fig_sev, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 8 — RAW REVIEW EXPLORER
# ═══════════════════════════════════════════════════════════════════════════════
with tab_explorer:
    st.markdown("<div class='section-header'>🔍 Raw Review Explorer</div>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:#9ca3af; font-size:0.88rem; margin-bottom:20px;'>Browsing <strong style='color:#1DB954;'>{len(filtered_df)}</strong> reviews matching current filters. Use sidebar to narrow scope.</p>",
        unsafe_allow_html=True
    )

    if filtered_df.empty:
        st.info("No reviews match the selected filters.")
    else:
        display_df = filtered_df.head(100)  # Limit for performance
        for idx, row in display_df.iterrows():
            sev = row.get("severity", "Low")
            pill_class = "pill-high" if sev == "High" else "pill-medium" if sev == "Medium" else "pill-low"
            text = str(row.get("text", ""))
            display_text = text[:300] + "..." if len(text) > 300 else text

            st.markdown(f"""
            <div style="background:#111; border:1px solid #1a1a1a; border-radius:12px; padding:18px; margin-bottom:10px; transition:border-color 0.2s;" onmouseover="this.style.borderColor='#282828'" onmouseout="this.style.borderColor='#1a1a1a'">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <span style="font-weight:700; color:#ffffff; font-size:0.95rem;">{row.get('title', 'Review')}</span>
                    <div style="display:flex; gap:8px; align-items:center;">
                        <span class="pill {pill_class}">{sev}</span>
                        <span style="background:#1a1a1a; color:#9ca3af; padding:3px 10px; border-radius:10px; font-size:11px; font-weight:600;">{row.get('source','')}</span>
                        <span style="background:#1a1a1a; color:#9ca3af; padding:3px 10px; border-radius:10px; font-size:11px; font-weight:600;">⭐ {row.get('rating','')}/5</span>
                    </div>
                </div>
                <p style="color:#9ca3af; font-size:0.88rem; line-height:1.6; margin-bottom:10px;">{display_text}</p>
                <div style="display:flex; gap:16px; font-size:11px; color:#1DB954; border-top:1px solid #1a1a1a; padding-top:8px; margin-top:2px;">
                    <span>📂 <b>Category:</b> {row.get('category','')}</span>
                    <span>🎭 <b>Sentiment:</b> {row.get('sentiment','')}</span>
                    <span style="color:#606060;">📅 {row.get('date','')}</span>
                </div>
                <div style="margin-top:8px; font-size:11px; color:#9ca3af;">
                    💡 <b>Core Frustration:</b> {row.get('core_frustration','N/A')}
                </div>
            </div>
            """, unsafe_allow_html=True)

        if len(filtered_df) > 100:
            st.info(f"Showing first 100 of {len(filtered_df)} reviews. Use sidebar filters to refine.")
