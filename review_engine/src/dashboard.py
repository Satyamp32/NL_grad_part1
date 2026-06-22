import json
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Streamlit Page Setup
st.set_page_config(
    page_title="Spotify Discovery Feedback Engine",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling (Spotify/Dark Aesthetic)
st.markdown("""
<style>
    /* Main container background */
    .stApp {
        background-color: #121212;
        color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #040404 !important;
        border-right: 1px solid #282828;
    }
    
    /* Metrics panel cards styling */
    div[data-testid="metric-container"] {
        background-color: #181818;
        border: 1px solid #282828;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        border-color: #1DB954;
    }
    
    /* Metric text colors */
    div[data-testid="stMetricValue"] {
        color: #1DB954 !important;
        font-weight: 700;
    }
    div[data-testid="stMetricLabel"] {
        color: #b3b3b3 !important;
    }
    
    /* Tab headers */
    div[data-testid="stTabBar"] button {
        color: #b3b3b3 !important;
        font-weight: 600;
        font-size: 16px;
        border-bottom: 2px solid transparent;
        padding: 10px 20px;
    }
    div[data-testid="stTabBar"] button[aria-selected="true"] {
        color: #ffffff !important;
        border-bottom: 2px solid #1DB954 !important;
    }
    
    /* Buttons */
    div.stButton > button {
        background-color: #1DB954 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 500px !important;
        padding: 10px 24px !important;
        font-weight: bold !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: background-color 0.2s ease, transform 0.1s ease !important;
    }
    div.stButton > button:hover {
        background-color: #1ed760 !important;
        transform: scale(1.03);
    }
    
    /* Card headers & dividers */
    hr {
        border-color: #282828 !important;
    }
    
    /* AI synthesized section background */
    .insight-card {
        background-color: #181818;
        border-left: 5px solid #1DB954;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }
    
    .insight-title {
        color: #ffffff;
        font-size: 1.15rem;
        font-weight: bold;
        margin-bottom: 8px;
    }
    
    .insight-body {
        color: #b3b3b3;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Status pills */
    .pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .pill-high { background-color: #e22134; color: white; }
    .pill-medium { background-color: #e28a21; color: white; }
    .pill-low { background-color: #2196f3; color: white; }
</style>
""", unsafe_allow_html=True)

# Data paths relative to this file
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_PATH = BASE_DIR / "data" / "raw_reviews.json"
ANALYZED_PATH = BASE_DIR / "data" / "analyzed_reviews.json"
REPORT_PATH = BASE_DIR / "data" / "synthesis_report.json"

# Loader functions
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

# Sidebar - Brand & Control
st.sidebar.markdown("""
<div style="display: flex; align-items: center; margin-bottom: 20px;">
    <span style="font-size: 32px; margin-right: 12px;">🎵</span>
    <h2 style="color: #ffffff; margin: 0; font-weight: 800; letter-spacing: -0.5px;">Spotify PM Discovery Engine</h2>
</div>
""", unsafe_allow_html=True)

st.sidebar.write("### Project Phase 1")
st.sidebar.write("This engine processes App Store, Play Store, and Reddit user feedback using LLM analysis to map Spotify’s music discovery challenges.")

# Sync Button in Dashboard Sidebar
st.sidebar.write("---")
st.sidebar.write("### Data Sync Control")
if st.sidebar.button("🔄 Sync Feedback Data", help="Scrapes latest reviews and updates classifications"):
    # We run the pipeline programmatically
    status_text = st.sidebar.empty()
    try:
        status_text.info("📡 Scraping Play Store & App Store feeds...")
        from review_engine.src.scrapers import scrape_all_and_save
        # Fast sync (100 reviews per platform) to avoid browser timeouts
        scrape_all_and_save(play_limit=100, app_limit=100, reddit_limit=10)
        
        status_text.info("🧠 Running sentiment & thematic analysis...")
        from review_engine.src.analyzer import run_classification, generate_synthesis_report
        analyzed = run_classification()
        generate_synthesis_report(analyzed)
        
        status_text.success("✅ Sync completed successfully!")
        st.cache_data.clear()  # Clear streamlit cache to read fresh files
        st.rerun()
    except Exception as e:
        status_text.error(f"❌ Sync failed: {e}")

# Load datasets
df = load_data()
report = load_report()

if df is None:
    st.sidebar.error("❌ No analyzed data found.")
    st.sidebar.write("Please run the scraper and analyzer first in the terminal:")
    st.sidebar.code("python review_engine/run.py scrape\npython review_engine/run.py analyze")
    
    st.markdown("""
    # Welcome to the Spotify Discovery Engine
    To visualize results, you need to collect and analyze user reviews. 
    1. Open your terminal.
    2. Activate the python virtual environment: `source .venv/bin/activate`
    3. Run `python review_engine/run.py scrape` to pull data.
    4. Run `python review_engine/run.py analyze` to run LLM tagging.
    5. Refresh this dashboard page!
    """)
else:
    # Sidebar Filters
    st.sidebar.write("---")
    st.sidebar.write("### Data Filters")
    
    sources = st.sidebar.multiselect("Source", options=df["source"].unique(), default=df["source"].unique())
    categories = st.sidebar.multiselect("Category", options=df["category"].unique(), default=df["category"].unique())
    sentiments = st.sidebar.multiselect("Sentiment", options=df["sentiment"].unique(), default=df["sentiment"].unique())
    
    # Filter dataset
    filtered_df = df[
        df["source"].isin(sources) &
        df["category"].isin(categories) &
        df["sentiment"].isin(sentiments)
    ]
    
    st.sidebar.write("---")
    st.sidebar.info(f"Showing **{len(filtered_df)}** of **{len(df)}** reviews.")
    
    # Header Banner
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1DB954 0%, #191414 100%); padding: 30px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
        <h1 style="color: #ffffff; margin: 0; font-size: 2.2rem; font-weight: 800;">AI-Powered Discovery Feedback Engine</h1>
        <p style="color: #e0e0e0; margin-top: 10px; margin-bottom: 0; font-size: 1.1rem;">Analyzing Spotify reviews at scale to solve algorithmic repetition and discovery fatigue.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main Tabs
    tab_dashboard, tab_insights, tab_explorer = st.tabs([
        "📊 Executive Dashboard", 
        "🧠 PM Insights & Synthesis", 
        "🔍 Raw Data Explorer"
    ])
    
    # ------------------ TAB 1: EXECUTIVE DASHBOARD ------------------
    with tab_dashboard:
        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Reviews Analyzed", len(df))
        with col2:
            neg_pct = (df["sentiment"] == "Negative").sum() / len(df) * 100 if len(df) > 0 else 0
            st.metric("Frustration Rate (Negative Sentiment)", f"{neg_pct:.1f}%")
        with col3:
            high_sev = (df["severity"] == "High").sum()
            st.metric("High-Severity Friction Points", high_sev)
        with col4:
            primary_cat = df["category"].mode()[0] if not df.empty else "N/A"
            st.metric("Top Complaint Area", primary_cat)
            
        st.write("---")
        
        # Plots Row 1
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("### 🏷️ Friction Categories Distribution")
            cat_counts = filtered_df["category"].value_counts().reset_index()
            cat_counts.columns = ["Category", "Count"]
            
            fig_cat = px.bar(
                cat_counts,
                x="Count",
                y="Category",
                orientation='h',
                color="Category",
                color_discrete_sequence=["#1DB954", "#3b82f6", "#ef4444", "#f59e0b", "#8b5cf6", "#6b7280"],
                text="Count"
            )
            fig_cat.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#ffffff",
                showlegend=False,
                xaxis=dict(showgrid=True, gridcolor="#282828"),
                yaxis=dict(autorange="reversed"),
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_cat, use_container_width=True)
            
        with col_right:
            st.markdown("### 🎭 Sentiment Distribution")
            sent_counts = filtered_df["sentiment"].value_counts().reset_index()
            sent_counts.columns = ["Sentiment", "Count"]
            
            fig_sent = px.pie(
                sent_counts,
                values="Count",
                names="Sentiment",
                color="Sentiment",
                color_discrete_map={"Negative": "#ef4444", "Neutral": "#6b7280", "Positive": "#1DB954"},
                hole=0.4
            )
            fig_sent.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#ffffff",
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_sent, use_container_width=True)
            
        st.write("---")
        
        # Plots Row 2 (Source and Severity comparison)
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("### 🔌 Source Volume")
            src_counts = filtered_df["source"].value_counts().reset_index()
            src_counts.columns = ["Source", "Count"]
            fig_src = px.bar(
                src_counts,
                x="Source",
                y="Count",
                color="Source",
                color_discrete_sequence=["#10b981", "#3b82f6", "#f43f5e"]
            )
            fig_src.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#ffffff",
                showlegend=False,
                yaxis=dict(showgrid=True, gridcolor="#282828"),
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_src, use_container_width=True)
            
        with col_s2:
            st.markdown("### ⚠️ Severity Distribution")
            sev_counts = filtered_df["severity"].value_counts().reset_index()
            sev_counts.columns = ["Severity", "Count"]
            fig_sev = px.bar(
                sev_counts,
                x="Severity",
                y="Count",
                color="Severity",
                color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#3b82f6"}
            )
            fig_sev.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#ffffff",
                showlegend=False,
                yaxis=dict(showgrid=True, gridcolor="#282828"),
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_sev, use_container_width=True)

    # ------------------ TAB 2: PM INSIGHTS & SYNTHESIS ------------------
    with tab_insights:
        if report is None:
            st.warning("⚠️ No PM synthesis report generated yet. Run: python review_engine/run.py analyze")
        else:
            meta = report.get("metadata", {})
            st.markdown(f"**Generated At:** `{meta.get('generated_at')}` | **LLM Analyzed:** `{meta.get('llm_synthesized')}`")
            st.write("---")
            
            # Layout the answers
            answers = report.get("answers", {})
            
            def display_insight(title, content):
                st.markdown(f"""
                <div class="insight-card">
                    <div class="insight-title">{title}</div>
                    <div class="insight-body">{content.replace(chr(10), '<br>')}</div>
                </div>
                """, unsafe_allow_html=True)
                
            col_in1, col_in2 = st.columns(2)
            with col_in1:
                display_insight("🎯 Why do users struggle to discover new music?", answers.get("why_discovery_struggle", "N/A"))
                display_insight("🔥 What are the most common frustrations with recommendations?", answers.get("common_frustrations", "N/A"))
                display_insight("🧭 What listening behaviors are users trying to achieve?", answers.get("intended_behaviors", "N/A"))
            with col_in2:
                display_insight("🔄 What causes users to repeatedly listen to the same content?", answers.get("repetition_causes", "N/A"))
                display_insight("👥 Which user segments experience different discovery challenges?", answers.get("user_segments", "N/A"))
                display_insight("💡 What unmet needs emerge consistently across reviews?", answers.get("unmet_needs", "N/A"))

    # ------------------ TAB 3: RAW DATA EXPLORER ------------------
    with tab_explorer:
        st.markdown("### 📋 Feed Reader & Text Explorer")
        st.write("Examine individual reviews. Filter them using the sidebar controls.")
        
        if filtered_df.empty:
            st.info("No reviews match the selected filters.")
        else:
            for idx, row in filtered_df.iterrows():
                # Format severity pill
                sev = row.get('severity', 'Low')
                pill_class = "pill-low"
                if sev == "High":
                    pill_class = "pill-high"
                elif sev == "Medium":
                    pill_class = "pill-medium"
                    
                st.markdown(f"""
                <div style="background-color: #181818; padding: 15px; border-radius: 8px; margin-bottom: 12px; border: 1px solid #282828;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-weight: bold; color: #ffffff; font-size: 1.1rem;">{row.get('title', 'No Title')}</span>
                        <div>
                            <span class="pill {pill_class}">{sev}</span>
                            <span style="background-color: #282828; color: #b3b3b3; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; margin-left: 8px;">{row.get('source')}</span>
                            <span style="background-color: #282828; color: #b3b3b3; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; margin-left: 8px;">Rating: {row.get('rating')}/5</span>
                        </div>
                    </div>
                    <p style="color: #b3b3b3; font-size: 0.95rem; line-height: 1.5; margin-bottom: 10px;">{row.get('text')}</p>
                    <div style="display: flex; gap: 20px; font-size: 12px; color: #1DB954;">
                        <span>📂 <b>Category:</b> {row.get('category')}</span>
                        <span>🎭 <b>Sentiment:</b> {row.get('sentiment')}</span>
                        <span style="color: #888;">📅 Date: {row.get('date')}</span>
                    </div>
                    <div style="margin-top: 8px; font-size: 12px; color: #b3b3b3; border-top: 1px solid #222; padding-top: 6px;">
                        💡 <b>Core Frustration:</b> {row.get('core_frustration', 'N/A')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
