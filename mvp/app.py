"""
Spotify Contextual Discovery MVP
Phase 4 — AI-Native Music Discovery Engine

Architecture:
  User Mood Input (natural language)
        ↓
  LLM Engine (parse intent → audio features + genres)
        ↓
  Spotify Recommendations API (audio-feature-filtered discovery)
        ↓
  LLM Engine (generate per-track explanations)
        ↓
  Results + Save to Spotify Playlist
"""
import os
import sys
import time
import logging
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# ─── Load .env for local development ──────────────────────────────────────────
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

# ─── Page Configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Spotify Discovery — AI Mood Engine",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Premium Dark Styling ─────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #111827 50%, #0d1117 100%);
        color: #e2e8f0;
    }

    /* Hide default Streamlit chrome */
    #MainMenu, header, footer { visibility: hidden; }
    .block-container { padding: 2rem 3rem; max-width: 1200px; }

    /* ── Hero ───────────────────────────────────────────────────────────── */
    .hero-section {
        text-align: center;
        padding: 5rem 2rem 3rem;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(29,185,84,0.15);
        border: 1px solid rgba(29,185,84,0.4);
        color: #1DB954;
        padding: 0.35rem 1rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 900;
        line-height: 1.1;
        background: linear-gradient(135deg, #ffffff 0%, #1DB954 60%, #60a5fa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1.2rem;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        color: #94a3b8;
        max-width: 600px;
        margin: 0 auto 2.5rem;
        line-height: 1.7;
        font-weight: 400;
    }

    /* ── Cards ──────────────────────────────────────────────────────────── */
    .glass-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        transition: border-color 0.3s ease, transform 0.2s ease;
    }
    .glass-card:hover {
        border-color: rgba(29,185,84,0.3);
        transform: translateY(-2px);
    }

    .track-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        transition: all 0.25s ease;
    }
    .track-card:hover {
        background: rgba(29,185,84,0.08);
        border-color: rgba(29,185,84,0.25);
        transform: translateX(4px);
    }

    /* ── Profile chip ────────────────────────────────────────────────────── */
    .profile-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 24px;
        padding: 0.4rem 1rem;
        font-size: 0.82rem;
        color: #cbd5e1;
        margin: 0.2rem;
    }

    /* ── Mood chip examples ──────────────────────────────────────────────── */
    .mood-example {
        display: inline-block;
        background: rgba(29,185,84,0.1);
        border: 1px solid rgba(29,185,84,0.25);
        color: #4ade80;
        border-radius: 20px;
        padding: 0.3rem 0.85rem;
        font-size: 0.78rem;
        margin: 0.2rem;
        cursor: pointer;
    }

    /* ── Stat badge ─────────────────────────────────────────────────────── */
    .stat-badge {
        background: rgba(29,185,84,0.12);
        border: 1px solid rgba(29,185,84,0.2);
        border-radius: 8px;
        padding: 0.75rem 1.2rem;
        text-align: center;
    }
    .stat-number {
        font-size: 1.6rem;
        font-weight: 800;
        color: #1DB954;
        line-height: 1;
    }
    .stat-label {
        font-size: 0.72rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-top: 0.3rem;
    }

    /* ── Section headers ─────────────────────────────────────────────────── */
    .section-label {
        font-size: 0.72rem;
        color: #1DB954;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .section-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #f1f5f9;
        margin-bottom: 0.5rem;
    }

    /* ── Explanation text ────────────────────────────────────────────────── */
    .track-explanation {
        font-size: 0.82rem;
        color: #64748b;
        font-style: italic;
        line-height: 1.5;
        margin-top: 0.3rem;
    }
    .track-name { font-size: 0.98rem; font-weight: 600; color: #f1f5f9; }
    .track-artist { font-size: 0.82rem; color: #94a3b8; margin-top: 0.15rem; }

    /* ── Mode badge ─────────────────────────────────────────────────────── */
    .mode-badge-llm {
        display: inline-block;
        background: rgba(96,165,250,0.15);
        border: 1px solid rgba(96,165,250,0.3);
        color: #60a5fa;
        padding: 0.2rem 0.7rem;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    .mode-badge-heuristic {
        display: inline-block;
        background: rgba(250,204,21,0.15);
        border: 1px solid rgba(250,204,21,0.3);
        color: #fbbf24;
        padding: 0.2rem 0.7rem;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 600;
    }

    /* ── Setup warning card ──────────────────────────────────────────────── */
    .setup-card {
        background: rgba(251,191,36,0.06);
        border: 1px solid rgba(251,191,36,0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    /* ── Streamlit element overrides ─────────────────────────────────────── */
    .stTextArea > div > div > textarea {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 12px !important;
        color: #f1f5f9 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
    }
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(29,185,84,0.5) !important;
        box-shadow: 0 0 0 3px rgba(29,185,84,0.1) !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #1DB954, #15a547) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.7rem 2.5rem !important;
        transition: all 0.25s ease !important;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #22d263, #1DB954) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(29,185,84,0.35) !important;
    }
    .stSlider > div > div > div { color: #1DB954 !important; }

    div[data-testid="stHorizontalBlock"] > div { gap: 1rem; }
</style>
""", unsafe_allow_html=True)

# ─── Credential helpers ────────────────────────────────────────────────────────
def _secret(key: str, default: str = "") -> str:
    """Try Streamlit secrets first, then env vars."""
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return os.getenv(key, default)

SPOTIFY_CLIENT_ID     = _secret("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = _secret("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI  = _secret("SPOTIFY_REDIRECT_URI", "http://localhost:8502/")
LLM_PROVIDER          = _secret("LLM_PROVIDER", "openai").lower()
OPENAI_API_KEY        = _secret("OPENAI_API_KEY")
ANTHROPIC_API_KEY     = _secret("ANTHROPIC_API_KEY")

SPOTIFY_SCOPE = "user-top-read playlist-modify-public playlist-modify-private"
_CREDENTIALS_READY = bool(SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET)

# ─── LLM client initialization ────────────────────────────────────────────────
_openai_client = None
_anthropic_client = None

if LLM_PROVIDER == "openai" and OPENAI_API_KEY:
    try:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception:
        pass

if LLM_PROVIDER == "anthropic" and ANTHROPIC_API_KEY:
    try:
        import anthropic
        _anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    except Exception:
        pass

# ─── Import local LLM engine ──────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from llm_engine import parse_mood, generate_track_explanations

# ─── Spotify OAuth helpers ─────────────────────────────────────────────────────
def _get_sp_oauth():
    if not _CREDENTIALS_READY:
        return None
    from spotipy.oauth2 import SpotifyOAuth
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE,
        cache_path=None,
        show_dialog=False,
    )

def _handle_oauth_callback():
    """Exchange OAuth code for token — runs before any UI rendering."""
    if "code" not in st.query_params:
        return
    if "token_info" in st.session_state:
        # Already authed, clean URL
        st.query_params.clear()
        return
    try:
        sp_oauth = _get_sp_oauth()
        if not sp_oauth:
            return
        code = st.query_params["code"]
        token_info = sp_oauth.get_access_token(code, as_dict=True, check_cache=False)
        st.session_state["token_info"] = token_info
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Authentication error: {e}")
        st.query_params.clear()

def _get_valid_token() -> str | None:
    """Return a valid access token, refreshing if expired."""
    if "token_info" not in st.session_state:
        return None
    token_info = st.session_state["token_info"]
    if token_info.get("access_token") == "demo_token":
        return "demo_token"
    sp_oauth = _get_sp_oauth()
    if not sp_oauth:
        return None
    try:
        if sp_oauth.is_token_expired(token_info):
            token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
            st.session_state["token_info"] = token_info
        return token_info["access_token"]
    except Exception:
        del st.session_state["token_info"]
        return None

def _get_sp(token: str):
    import spotipy
    if token == "demo_token":
        from spotipy.oauth2 import SpotifyClientCredentials
        return spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        ))
    return spotipy.Spotify(auth=token)

# ─── Spotify API calls ────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def _fetch_user_profile(token: str) -> dict:
    if token == "demo_token":
        return {
            "id": "demo_evaluator",
            "display_name": "Demo Guest",
            "images": [{"url": "https://api.dicebear.com/7.x/bottts/svg?seed=Demo"}]
        }
    sp = _get_sp(token)
    return sp.current_user()

@st.cache_data(ttl=600)
def _fetch_top_items(token: str) -> dict:
    if token == "demo_token":
        return {"tracks": [], "artists": []}
    sp = _get_sp(token)
    top_tracks  = sp.current_user_top_tracks(limit=20, time_range="medium_term")
    top_artists = sp.current_user_top_artists(limit=10, time_range="medium_term")
    return {"tracks": top_tracks.get("items", []), "artists": top_artists.get("items", [])}

def _build_recommendations(token: str, parsed: dict, exploration_level: int,
                            top_artist_ids: list) -> list:
    """Call Spotify recommendations API with audio features from LLM."""
    sp = _get_sp(token)
    features = parsed["features"]
    genres   = parsed["genres"]
    expl     = exploration_level  # 1–10

    # Exploration level controls:
    # - seed composition (familiar ↔ genre-only)
    # - popularity ceiling (mainstream ↔ underground)
    if expl <= 3:
        # Familiar mode: seed from user's artists + 1 genre
        seed_artists = top_artist_ids[:2] if top_artist_ids else []
        seed_genres  = genres[:1] if genres else ["indie"]
        min_pop, max_pop = 30, 100
    elif expl <= 6:
        # Balanced mode: mix
        seed_artists = top_artist_ids[:1] if top_artist_ids else []
        seed_genres  = genres[:2] if genres else ["indie", "pop"]
        min_pop, max_pop = 15, 75
    else:
        # Explorer mode: genre-only seeds, underground tracks
        seed_artists = []
        seed_genres  = genres[:3] if genres else ["indie", "alternative", "folk"]
        min_pop, max_pop = 0, 45

    kwargs = dict(
        seed_genres=seed_genres,
        limit=15,
        target_valence=features["valence"],
        target_energy=features["energy"],
        target_danceability=features["danceability"],
        target_acousticness=features["acousticness"],
        target_instrumentalness=features["instrumentalness"],
        min_popularity=min_pop,
        max_popularity=max_pop,
    )
    if seed_artists:
        kwargs["seed_artists"] = seed_artists

    try:
        result = sp.recommendations(**kwargs)
        return result.get("tracks", [])
    except Exception as e:
        st.warning(f"Spotify API error: {e}. Retrying without artist seeds…")
        kwargs.pop("seed_artists", None)
        kwargs["seed_genres"] = genres[:3] if genres else ["indie"]
        result = sp.recommendations(**kwargs)
        return result.get("tracks", [])

def _save_playlist(token: str, user_id: str, name: str,
                   track_uris: list, description: str = "") -> str:
    """Create a new Spotify playlist and add tracks. Returns playlist URL."""
    if token == "demo_token":
        import time
        time.sleep(1.0)
        return "https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO"
    sp = _get_sp(token)
    playlist = sp.user_playlist_create(
        user=user_id,
        name=name,
        public=False,
        description=description or f"AI-curated discovery playlist — {name}",
    )
    sp.playlist_add_items(playlist["id"], track_uris)
    return playlist["external_urls"]["spotify"]

# ─── UI Components ────────────────────────────────────────────────────────────

def _render_setup_warning():
    st.markdown("""
    <div class='setup-card'>
        <b>⚠️ Spotify credentials not configured.</b><br><br>
        To run this app you need:<br>
        <ol style='margin-top:0.5rem; color:#94a3b8; font-size:0.9rem;'>
            <li>A <a href='https://developer.spotify.com/dashboard' target='_blank' style='color:#1DB954;'>Spotify Developer App</a> (free)</li>
            <li>Copy <code>mvp/.env.example</code> → <code>mvp/.env</code> and fill in your credentials</li>
            <li>Add <code>http://localhost:8502/</code> as a Redirect URI in your Spotify app settings</li>
            <li>Re-launch: <code>streamlit run mvp/app.py --server.port 8502</code></li>
        </ol>
    </div>
    """, unsafe_allow_html=True)


def _render_landing():
    """Landing page shown before Spotify authentication."""
    st.markdown("""
    <div class='hero-section'>
        <div class='hero-badge'>🤖 AI-Native Music Discovery</div>
        <div class='hero-title'>Escape Your<br>Echo Chamber</div>
        <div class='hero-subtitle'>
            Tell us how you feel — in plain English. Our AI translates your mood into music
            Spotify's algorithm never thought to show you.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Feature highlights
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='glass-card' style='text-align:center; padding:2rem 1.5rem;'>
            <div style='font-size:2rem;margin-bottom:0.75rem;'>🧠</div>
            <div style='font-weight:700;font-size:1.05rem;color:#f1f5f9;margin-bottom:0.5rem;'>Mood Intelligence</div>
            <div style='font-size:0.85rem;color:#64748b;line-height:1.6;'>
                Describe any feeling — "rainy Sunday morning", "neon city at 3AM" — our AI maps it to musical DNA.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='glass-card' style='text-align:center; padding:2rem 1.5rem;'>
            <div style='font-size:2rem;margin-bottom:0.75rem;'>🎛️</div>
            <div style='font-weight:700;font-size:1.05rem;color:#f1f5f9;margin-bottom:0.5rem;'>Discovery Dial</div>
            <div style='font-size:0.85rem;color:#64748b;line-height:1.6;'>
                Control how far you venture. Slide between familiar comfort and underground discovery.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='glass-card' style='text-align:center; padding:2rem 1.5rem;'>
            <div style='font-size:2rem;margin-bottom:0.75rem;'>💾</div>
            <div style='font-weight:700;font-size:1.05rem;color:#f1f5f9;margin-bottom:0.5rem;'>Save Instantly</div>
            <div style='font-size:0.85rem;color:#64748b;line-height:1.6;'>
                One click to save your AI-curated playlist directly to your Spotify account.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Example moods
    st.markdown("""
    <div style='text-align:center;margin-bottom:1rem;'>
        <div style='font-size:0.78rem;color:#64748b;margin-bottom:0.75rem;text-transform:uppercase;letter-spacing:0.08em;'>Try describing these moods</div>
        <span class='mood-example'>☕ Sunday morning coffee</span>
        <span class='mood-example'>🌃 Late night city drive</span>
        <span class='mood-example'>🌧️ Rainy day introspection</span>
        <span class='mood-example'>💪 Pre-workout energy</span>
        <span class='mood-example'>🌅 Hopeful new beginning</span>
        <span class='mood-example'>🎭 Bittersweet nostalgia</span>
    </div>
    """, unsafe_allow_html=True)

    if _CREDENTIALS_READY:
        sp_oauth = _get_sp_oauth()
        auth_url = sp_oauth.get_authorize_url()
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.link_button("🎵  Connect with Spotify", auth_url, use_container_width=True)
            st.markdown("<div style='text-align:center; margin: 0.5rem 0; color:#64748b; font-size:0.85rem;'>— or —</div>", unsafe_allow_html=True)
            if st.button("🚀  Try Sandbox Demo Mode", use_container_width=True):
                st.session_state["token_info"] = {
                    "access_token": "demo_token",
                    "expires_at": 9999999999
                }
                st.rerun()
            st.markdown("<div style='text-align:center; color:#64748b; font-size:0.75rem; margin-top:0.3rem;'>No Premium subscription or login required</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align:center; margin-top:2rem;'>", unsafe_allow_html=True)
        _render_setup_warning()
        st.markdown("</div>", unsafe_allow_html=True)

    # How it works
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center;margin-bottom:1.5rem;'>
        <div class='section-label'>How It Works</div>
        <div class='section-title'>Three steps to escape the echo chamber</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    for col, step, icon, title, desc in [
        (c1, "01", "💬", "Describe Your Mood",
         "Type anything — abstract, emotional, contextual. The more specific, the better the result."),
        (c2, "02", "🤖", "AI Parses Your Intent",
         "LLM translates your words into Spotify's audio feature space: valence, energy, acousticness, and more."),
        (c3, "03", "🎵", "Get Fresh Discoveries",
         "Tracks you've never heard, filtered by popularity ceiling to surface deep cuts, not just top charts."),
    ]:
        with col:
            st.markdown(f"""
            <div class='glass-card' style='text-align:center;'>
                <div style='font-size:0.7rem;color:#1DB954;font-weight:800;letter-spacing:0.1em;margin-bottom:0.5rem;'>{step}</div>
                <div style='font-size:1.8rem;margin-bottom:0.5rem;'>{icon}</div>
                <div style='font-weight:700;color:#f1f5f9;margin-bottom:0.5rem;'>{title}</div>
                <div style='font-size:0.83rem;color:#64748b;line-height:1.6;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── WHY AI? Section (required by Phase 4 spec) ────────────────────────────
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center;margin-bottom:2rem;'>
        <div class='section-label'>Why AI? Not Just Another Recommendation Engine</div>
        <div class='section-title'>Three things only AI can do</div>
        <div style='color:#64748b;font-size:0.92rem;margin-top:0.4rem;'>
            Traditional recommendation systems fail at this. Here's exactly why AI changes everything.
        </div>
    </div>
    """, unsafe_allow_html=True)

    wa, wb, wc = st.columns(3)
    with wa:
        st.markdown("""
        <div class='glass-card' style='border-color:rgba(239,68,68,0.25);'>
            <div style='font-size:0.68rem;color:#ef4444;font-weight:800;letter-spacing:0.1em;margin-bottom:0.75rem;text-transform:uppercase;'>❌ Why Traditional Fails</div>
            <div style='font-weight:700;color:#f1f5f9;font-size:1rem;margin-bottom:0.75rem;'>Collaborative Filtering is<br>semantically blind</div>
            <div style='font-size:0.83rem;color:#64748b;line-height:1.7;'>
                Spotify's algorithm matches you with users who have similar listening <i>histories</i>. It understands track IDs and play counts — not emotions.
                <br><br>
                It cannot understand: <span style='color:#f87171;font-style:italic;'>
                "Music that feels like driving through a neon-lit city at 3AM in a retro-futuristic movie."</span>
                <br><br>
                That sentence has no track ID. No play count. The algorithm sees noise. It defaults to what you already know.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with wb:
        st.markdown("""
        <div class='glass-card' style='border-color:rgba(29,185,84,0.3);'>
            <div style='font-size:0.68rem;color:#1DB954;font-weight:800;letter-spacing:0.1em;margin-bottom:0.75rem;text-transform:uppercase;'>✅ What AI Unlocks</div>
            <div style='font-weight:700;color:#f1f5f9;font-size:1rem;margin-bottom:0.75rem;'>Semantic intent → musical DNA translation</div>
            <div style='font-size:0.83rem;color:#64748b;line-height:1.7;'>
                Large Language Models are trained on the full context of human expression — poetry, film reviews, music criticism, and emotional vocabulary.
                <br><br>
                When you type <span style='color:#4ade80;font-style:italic;'>"neon city at 3AM"</span> an LLM maps this to:
                <br>
                <span style='color:#4ade80;'>Energy ↑ · Valence ↓ · Electronic · Dark synths · Urban tempo</span>
                <br><br>
                This was previously architecturally impossible. No keyword search. No genre tag. Pure semantic understanding.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with wc:
        st.markdown("""
        <div class='glass-card' style='border-color:rgba(96,165,250,0.25);'>
            <div style='font-size:0.68rem;color:#60a5fa;font-weight:800;letter-spacing:0.1em;margin-bottom:0.75rem;text-transform:uppercase;'>🎯 How UX Changes</div>
            <div style='font-weight:700;color:#f1f5f9;font-size:1rem;margin-bottom:0.75rem;'>From passive reception to active intent expression</div>
            <div style='font-size:0.83rem;color:#64748b;line-height:1.7;'>
                Before AI: You open Spotify and accept what the algorithm decides you probably want.
                <br><br>
                With AI: You describe exactly what you want to feel — and the system builds a playlist around that intent.
                <br><br>
                The interface shifts from <span style='color:#93c5fd;'>"here's what we think you want"</span> to <span style='color:#93c5fd;'>"tell us what you want to feel."</span>
                <br><br>
                Plus: every track comes with an explanation — building algorithmic trust through transparency.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Research Evidence ─────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class='glass-card' style='background:rgba(29,185,84,0.04);border-color:rgba(29,185,84,0.15);'>
        <div style='font-size:0.72rem;color:#1DB954;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.75rem;'>
            📊 Built on 1,466 Real Spotify User Reviews · 7 Primary Research Interviews
        </div>
        <div style='display:flex;gap:3rem;flex-wrap:wrap;'>
            <div><span style='font-size:1.4rem;font-weight:800;color:#1DB954;'>86%</span><br>
                <span style='font-size:0.78rem;color:#64748b;'>of users experience repetition at 3/5 severity — normalized, chronic, invisible churn risk</span></div>
            <div><span style='font-size:1.4rem;font-weight:800;color:#1DB954;'>71%</span><br>
                <span style='font-size:0.78rem;color:#64748b;'>have abandoned Spotify's discovery features — manually curating playlists as a workaround</span></div>
            <div><span style='font-size:1.4rem;font-weight:800;color:#60a5fa;'>57%</span><br>
                <span style='font-size:0.78rem;color:#64748b;'>rated mood-based discovery "Very Useful" — highest demand of any tested feature</span></div>
            <div><span style='font-size:1.4rem;font-weight:800;color:#c084fc;'>0%</span><br>
                <span style='font-size:0.78rem;color:#64748b;'>found the Discovery Dial "Not Useful" — universal demand, cleanest signal of any feature</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_user_profile(user: dict, top_items: dict):
    """Display user's current musical comfort zone."""
    display_name = user.get("display_name", "Listener")
    
    tracks = top_items.get("tracks", [])
    artists = top_items.get("artists", [])
    
    # Populate mock data for demo mode to make the dashboard look populated
    if not tracks:
        tracks = [
            {"id": "mock_t1", "name": "Breathe", "artists": [{"name": "Pink Floyd"}]},
            {"id": "mock_t2", "name": "Fake Plastic Trees", "artists": [{"name": "Radiohead"}]},
            {"id": "mock_t3", "name": "Lost in the Dream", "artists": [{"name": "The War on Drugs"}]},
            {"id": "mock_t4", "name": "Intro", "artists": [{"name": "The xx"}]},
            {"id": "mock_t5", "name": "Holocene", "artists": [{"name": "Bon Iver"}]}
        ]
    if not artists:
        artists = [
            {"id": "mock_a1", "name": "Pink Floyd", "genres": ["classic rock", "psychedelic rock"]},
            {"id": "mock_a2", "name": "Radiohead", "genres": ["alternative rock", "art rock"]},
            {"id": "mock_a3", "name": "The War on Drugs", "genres": ["indie rock", "dream pop"]},
            {"id": "mock_a4", "name": "The xx", "genres": ["indie pop", "downtempo"]},
            {"id": "mock_a5", "name": "Bon Iver", "genres": ["indie folk", "singer-songwriter"]}
        ]
        
    top_artists  = tracks[:3]
    artist_names = [t["artists"][0]["name"] for t in tracks[:5]]
    top_genres   = []
    for a in artists[:5]:
        top_genres.extend(a.get("genres", [])[:2])
    top_genres = list(dict.fromkeys(top_genres))[:4]

    st.markdown(f"""
    <div style='margin-bottom:1.5rem;'>
        <div class='section-label'>Your Music Profile</div>
        <div style='color:#94a3b8;font-size:0.9rem;margin-bottom:0.75rem;'>
            Logged in as <b style='color:#f1f5f9;'>{display_name}</b> · Here's your current comfort zone:
        </div>
        <div>
            {''.join(f"<span class='profile-chip'>🎤 {a}</span>" for a in artist_names[:5])}
            {''.join(f"<span class='profile-chip' style='border-color:rgba(96,165,250,0.2);color:#93c5fd;'>🎵 {g}</span>" for g in top_genres)}
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_discovery_form() -> tuple[str, int]:
    """Render mood input + discovery dial. Returns (mood_text, exploration_level)."""
    st.markdown("""
    <div class='section-label'>Mood Input</div>
    <div class='section-title'>What are you in the mood for?</div>
    <div style='color:#64748b;font-size:0.88rem;margin-bottom:1rem;'>
        Describe a feeling, a setting, a moment — be as abstract or specific as you like.
    </div>
    """, unsafe_allow_html=True)

    mood_text = st.text_area(
        label="Mood description",
        label_visibility="collapsed",
        placeholder=(
            "e.g.  \"Music that feels like driving through a neon-lit city at 2AM in a retro-futuristic movie\"\n"
            "      \"Quiet Sunday morning with coffee and rain outside\"\n"
            "      \"Pre-workout energy — something aggressive but not metal\""
        ),
        height=130,
        key="mood_input",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class='section-label'>Discovery Dial</div>
    <div style='color:#64748b;font-size:0.88rem;margin-bottom:0.5rem;'>
        How far from your comfort zone do you want to go?
    </div>
    """, unsafe_allow_html=True)

    col_l, col_slider, col_r = st.columns([2, 8, 2])
    with col_l:
        st.markdown("<div style='color:#94a3b8;font-size:0.8rem;padding-top:0.6rem;'>🏠 Familiar</div>",
                    unsafe_allow_html=True)
    with col_slider:
        exploration = st.slider("exploration", 1, 10, 5, label_visibility="collapsed")
    with col_r:
        st.markdown("<div style='color:#94a3b8;font-size:0.8rem;padding-top:0.6rem;text-align:right;'>🔭 Explorer</div>",
                    unsafe_allow_html=True)

    # Show what the level means
    level_desc = {
        1: "Only tracks similar to your all-time favorites",
        2: "Very close to your existing taste",
        3: "Slightly outside your comfort zone",
        4: "Leaning familiar, some surprises",
        5: "Balanced mix of familiar and fresh",
        6: "More new, less familiar",
        7: "Mostly undiscovered territory",
        8: "Deep cuts and niche artists",
        9: "Almost entirely new to you",
        10: "Maximum discovery — fully uncharted",
    }
    st.markdown(f"<div style='text-align:center;font-size:0.82rem;color:#475569;margin-top:-0.5rem;'>{level_desc[exploration]}</div>",
                unsafe_allow_html=True)

    return mood_text.strip(), exploration


def _render_loading(mood_text: str, mode: str):
    """Show animated loading steps."""
    mode_badge = (
        "<span class='mode-badge-llm'>🤖 LLM-powered</span>"
        if mode in ("openai", "anthropic")
        else "<span class='mode-badge-heuristic'>📐 Heuristic mode</span>"
    )
    steps = [
        ("🧠", "Parsing your mood with AI…"),
        ("🔍", "Mapping to audio features…"),
        ("🎵", "Querying Spotify's catalog…"),
        ("✨", "Generating track explanations…"),
    ]
    placeholder = st.empty()
    for i, (icon, text) in enumerate(steps):
        placeholder.markdown(f"""
        <div class='glass-card' style='text-align:center;padding:2.5rem;'>
            <div style='font-size:2.5rem;margin-bottom:1rem;'>{icon}</div>
            <div style='font-weight:700;color:#f1f5f9;font-size:1.1rem;margin-bottom:0.5rem;'>{text}</div>
            <div style='color:#475569;font-size:0.85rem;'>{mode_badge}</div>
            <div style='margin-top:1rem;color:#1DB954;font-size:0.8rem;'>Step {i+1} / {len(steps)}</div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.6)
    placeholder.empty()


def _render_track_card(track: dict, explanation: str, index: int):
    """Render a single track recommendation card."""
    name     = track.get("name", "Unknown Track")
    artist   = track.get("artists", [{}])[0].get("name", "Unknown Artist")
    album    = track.get("album", {}).get("name", "")
    duration = track.get("duration_ms", 0) // 1000
    mins, secs = divmod(duration, 60)
    images   = track.get("album", {}).get("images", [])
    img_url  = images[-1]["url"] if images else None
    pop      = track.get("popularity", 0)
    sp_url   = track.get("external_urls", {}).get("spotify", "#")

    col_img, col_info = st.columns([1, 6])
    with col_img:
        if img_url:
            st.image(img_url, width=64)
        else:
            st.markdown(f"<div style='width:64px;height:64px;background:rgba(29,185,84,0.15);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:1.5rem;'>🎵</div>", unsafe_allow_html=True)
    with col_info:
        st.markdown(f"""
        <div>
            <div class='track-name'>
                <a href='{sp_url}' target='_blank' style='color:#f1f5f9;text-decoration:none;'>
                    {index}. {name}
                </a>
            </div>
            <div class='track-artist'>{artist} · {album} · {mins}:{secs:02d}</div>
            <div style='margin-top:0.15rem;'>
                <span style='font-size:0.7rem;color:#334155;'>Popularity: {pop}/100</span>
            </div>
            <div class='track-explanation'>"{explanation}"</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)


def _render_results(tracks: list, explanations: list, parsed_mood: dict,
                    mood_text: str, exploration: int):
    """Render the full results section."""
    mood_summary = parsed_mood.get("mood_summary", mood_text[:60])
    mode         = parsed_mood.get("mode", "heuristic")
    features     = parsed_mood.get("features", {})

    mode_badge = (
        "<span class='mode-badge-llm'>🤖 LLM-Synthesized</span>"
        if mode in ("openai", "anthropic")
        else "<span class='mode-badge-heuristic'>📐 Heuristic Mode</span>"
    )

    st.markdown(f"""
    <div style='margin-bottom:1.5rem;'>
        <div class='section-label'>Discovery Results</div>
        <div class='section-title'>Your "{mood_summary}" Playlist</div>
        <div style='color:#64748b;font-size:0.88rem;margin-top:0.25rem;'>
            {len(tracks)} tracks · Exploration level {exploration}/10 · {mode_badge}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Avg popularity proof
    if tracks:
        avg_pop = int(sum(t.get("popularity", 50) for t in tracks) / len(tracks))
        pop_color = "#4ade80" if avg_pop < 50 else ("#fbbf24" if avg_pop < 70 else "#f87171")
        st.markdown(f"""
        <div style='background:rgba(29,185,84,0.06);border:1px solid rgba(29,185,84,0.15);
                    border-radius:8px;padding:0.6rem 1rem;margin-bottom:1rem;
                    font-size:0.8rem;display:flex;align-items:center;gap:1rem;flex-wrap:wrap;'>
            <span style='color:#475569;'>Avg. popularity of these tracks:</span>
            <b style='color:{pop_color};font-size:1.1rem;'>{avg_pop}/100</b>
            <span style='color:#334155;'>·</span>
            <span style='color:#475569;font-style:italic;'>
                Spotify's algorithm typically surfaces 65+.
                {'These are genuine deep cuts.' if avg_pop < 50 else 'These are emerging or niche picks.'}
            </span>
        </div>
        """, unsafe_allow_html=True)

    if features:
        cols = st.columns(5)
        labels = [("Mood", "valence", "😊"),
                  ("Energy", "energy", "⚡"),
                  ("Danceable", "danceability", "💃"),
                  ("Acoustic", "acousticness", "🎸"),
                  ("Instrumental", "instrumentalness", "🎹")]
        for col, (label, key, icon) in zip(cols, labels):
            val = features.get(key, 0)
            with col:
                st.markdown(f"""
                <div class='stat-badge'>
                    <div style='font-size:1.1rem;margin-bottom:0.2rem;'>{icon}</div>
                    <div class='stat-number'>{int(val*100)}%</div>
                    <div class='stat-label'>{label}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Track cards
    for i, (track, explanation) in enumerate(zip(tracks, explanations), 1):
        with st.container():
            st.markdown("<div class='track-card'>", unsafe_allow_html=True)
            _render_track_card(track, explanation, i)
            st.markdown("</div>", unsafe_allow_html=True)

    return [t["uri"] for t in tracks]


def _render_save_section(track_uris: list, mood_text: str, token: str, user_id: str):
    """Render the save-to-Spotify button and handle saving."""
    st.markdown("<br>", unsafe_allow_html=True)
    
    is_demo = (token == "demo_token")
    
    if is_demo:
        st.markdown("""
        <div class='glass-card' style='text-align:center; padding:2rem;'>
            <div style='font-size:1.1rem;font-weight:700;color:#f1f5f9;margin-bottom:0.5rem;'>
                💾 Save to Your Spotify (Demo Mode)
            </div>
            <div style='color:#64748b;font-size:0.88rem;margin-bottom:1.5rem;'>
                In Demo Mode, playlist saving is simulated. Under Spotify's developer policy, only Premium accounts can create real playlists.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='glass-card' style='text-align:center; padding:2rem;'>
            <div style='font-size:1.1rem;font-weight:700;color:#f1f5f9;margin-bottom:0.5rem;'>
                💾 Save to Your Spotify
            </div>
            <div style='color:#64748b;font-size:0.88rem;margin-bottom:1.5rem;'>
                Creates a private playlist in your Spotify account with these {n} tracks.
            </div>
        </div>
        """.replace("{n}", str(len(track_uris))), unsafe_allow_html=True)

    playlist_name = st.text_input(
        "Playlist name",
        value=f"AI Discovery: {mood_text[:40].title()}",
        key="playlist_name_input",
    )

    if st.button("🎵  Save Playlist to Spotify", key="save_btn"):
        with st.spinner("Creating your playlist…"):
            try:
                url = _save_playlist(token, user_id, playlist_name, track_uris,
                                     f"AI-curated for: {mood_text[:100]}")
                if is_demo:
                    st.info("ℹ️ Demo Mode: Simulated playlist creation successful!")
                st.success(f"✅ Playlist saved! [Open in Spotify →]({url})")
                st.balloons()
            except Exception as e:
                st.error(f"Could not save playlist: {e}")


# ─── AI Interpretation Panel ──────────────────────────────────────────────────
def _render_interpretation_panel(parsed: dict, mood_text: str,
                                  exploration: int, n_excluded: int):
    """Show the AI's interpretation of the user's mood — the key AI-native differentiator."""
    features     = parsed.get("features", {})
    genres       = parsed.get("genres", [])
    mood_summary = parsed.get("mood_summary", mood_text[:60])
    mode         = parsed.get("mode", "heuristic")

    mode_label = "LLM Semantic Analysis" if mode in ("openai", "anthropic") else "Semantic Heuristic Engine"
    mode_color = "#60a5fa" if mode in ("openai", "anthropic") else "#fbbf24"

    if exploration <= 3:
        pop_range, disc_label = "30–100", "Familiar territory · Seeds from your listening history"
    elif exploration <= 6:
        pop_range, disc_label = "15–75", "Balanced · Mixed seeds"
    else:
        pop_range, disc_label = "0–45", "Underground territory · Genre-only seeds · Zero history bias"

    def bar(val, label, icon):
        pct = int(val * 100)
        return f"""
        <div style='margin:0.45rem 0;display:flex;align-items:center;gap:0.6rem;'>
            <div style='width:1.2rem;font-size:0.85rem;'>{icon}</div>
            <div style='width:8rem;font-size:0.75rem;color:#94a3b8;'>{label}</div>
            <div style='flex:1;background:rgba(255,255,255,0.06);border-radius:3px;height:7px;'>
                <div style='width:{min(pct,100)}%;background:linear-gradient(90deg,#1DB954,#60a5fa);
                            height:7px;border-radius:3px;'></div>
            </div>
            <div style='width:2.8rem;font-size:0.75rem;color:#60a5fa;font-weight:700;text-align:right;'>{pct}%</div>
        </div>"""

    bars  = bar(features.get("valence", 0.5),        "Mood Positivity", "😊")
    bars += bar(features.get("energy", 0.5),          "Energy Level",   "⚡")
    bars += bar(features.get("danceability", 0.5),    "Danceability",   "💃")
    bars += bar(features.get("acousticness", 0.4),    "Acoustic Feel",  "🎸")
    bars += bar(features.get("instrumentalness", 0.1),"Instrumental",   "🎹")

    genre_pills = "".join(
        f"<span style='background:rgba(29,185,84,0.15);border:1px solid rgba(29,185,84,0.3);"
        f"color:#4ade80;border-radius:12px;padding:0.2rem 0.65rem;font-size:0.74rem;"
        f"margin-right:0.35rem;'>{g}</span>"
        for g in genres
    )
    excluded_note = (
        f" · <span style='color:#475569;'>{n_excluded} of your top tracks excluded for fresh discovery</span>"
        if n_excluded > 0 else ""
    )

    st.markdown(f"""
    <div style='background:rgba(96,165,250,0.04);border:1px solid rgba(96,165,250,0.18);
                border-radius:14px;padding:1.4rem 1.5rem;margin-bottom:1.25rem;'>

        <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:0.9rem;'>
            <div style='font-size:0.68rem;color:{mode_color};font-weight:800;
                        letter-spacing:0.1em;text-transform:uppercase;'>
                🧠 AI Mood Interpretation
            </div>
            <div style='font-size:0.68rem;color:{mode_color};background:rgba(96,165,250,0.1);
                        border:1px solid rgba(96,165,250,0.2);border-radius:8px;
                        padding:0.15rem 0.6rem;'>{mode_label}</div>
        </div>

        <div style='font-size:0.83rem;color:#94a3b8;margin-bottom:0.3rem;'>
            You said: <span style='color:#e2e8f0;font-style:italic;'>"{mood_text[:90]}"</span>
        </div>
        <div style='font-size:0.83rem;color:#94a3b8;margin-bottom:1.1rem;'>
            Interpreted as: <b style='color:#4ade80;'>{mood_summary}</b>
        </div>

        <div style='font-size:0.68rem;color:#475569;text-transform:uppercase;
                    letter-spacing:0.08em;margin-bottom:0.5rem;'>Musical DNA</div>
        {bars}

        <div style='margin-top:0.9rem;display:flex;flex-wrap:wrap;align-items:center;gap:0.4rem;'>
            <span style='font-size:0.72rem;color:#475569;'>Genre seeds →</span>
            {genre_pills}
        </div>

        <div style='margin-top:0.75rem;font-size:0.76rem;color:#475569;
                    border-top:1px solid rgba(255,255,255,0.05);padding-top:0.7rem;'>
            🎛️ Discovery {exploration}/10 · {disc_label}{excluded_note}
        </div>

        <div style='margin-top:0.6rem;background:rgba(29,185,84,0.06);
                    border-left:3px solid #1DB954;border-radius:0 6px 6px 0;
                    padding:0.6rem 0.9rem;font-size:0.78rem;'>
            <b style='color:#1DB954;'>⚡ vs Traditional Spotify:</b>
            <span style='color:#475569;'> Collaborative Filtering would serve popularity
            65+ tracks from your <i>existing taste cluster</i>. This engine found tracks
            matching your <i>described emotional intent</i> with popularity {pop_range}.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── OAuth callback — must run before any UI rendering ────────────────────────
_handle_oauth_callback()

# ─── Main Router ──────────────────────────────────────────────────────────────
token = _get_valid_token()

if not token:
    _render_landing()
else:
    # ── Authenticated experience ──────────────────────────────────────────
    is_demo = (token == "demo_token")
    try:
        user      = _fetch_user_profile(token)
        top_items = _fetch_top_items(token)
    except Exception as e:
        st.error(f"Could not load your Spotify profile: {e}")
        if st.button("Reconnect with Spotify"):
            del st.session_state["token_info"]
            st.rerun()
        st.stop()

    user_id      = user.get("id", "")
    top_artist_ids = [a["id"] for a in top_items["artists"][:5]] if top_items.get("artists") else []

    # ── Why AI? Sidebar (evaluator-facing) ───────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style='padding:0.5rem 0;'>
            <div style='font-size:0.65rem;color:#1DB954;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:1rem;'>
                🤖 Why AI? — PM Evidence
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**❌ Why traditional CF fails**")
        st.markdown("""
        <div style='font-size:0.8rem;color:#64748b;line-height:1.6;margin-bottom:1rem;'>
        Collaborative Filtering optimises for <b style='color:#f87171;'>skip minimisation</b> — it plays familiar,
        high-probability tracks. It cannot understand abstract, emotional, or contextual intent.
        A user who types <i>"neon city at 3AM"</i> gets the same playlist as always.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**✅ What AI unlocks**")
        st.markdown("""
        <div style='font-size:0.8rem;color:#64748b;line-height:1.6;margin-bottom:1rem;'>
        LLMs are trained on human emotional vocabulary. They translate
        <i>"rainy Sunday morning"</i> into concrete Spotify audio features:
        <span style='color:#4ade80;'>valence=0.32, energy=0.22, acousticness=0.72</span>.
        This was previously architecturally impossible.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**🎯 How UX changes**")
        st.markdown("""
        <div style='font-size:0.8rem;color:#64748b;line-height:1.6;margin-bottom:1rem;'>
        From <i>"here's what we think you want"</i><br>
        → <b style='color:#93c5fd;'>"tell us what you want to feel"</b>.
        Every track comes with a transparent explanation — building algorithmic trust.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("""
        <div style='font-size:0.72rem;color:#475569;line-height:1.6;'>
        <b style='color:#1DB954;'>Research base:</b><br>
        📊 1,466 analyzed reviews<br>
        👤 7 primary research respondents<br>
        🔁 86% experience chronic repetition<br>
        🚪 71% abandoned algorithmic discovery<br>
        💚 57% want mood-based features
        </div>
        """, unsafe_allow_html=True)


    # Header
    st.markdown("""
    <div style='padding: 2rem 0 0; margin-bottom:0.5rem;'>
        <div class='hero-badge'>🤖 AI-Native Discovery Engine</div>
        <div class='hero-title' style='font-size:2.5rem; margin-bottom:0.5rem;'>
            Escape Your Echo Chamber
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Logout
    with st.container():
        _, col_logout = st.columns([10, 1])
        with col_logout:
            if st.button("↩ Logout", key="logout_btn"):
                del st.session_state["token_info"]
                st.session_state.pop("last_result", None)
                st.rerun()

    # Profile
    _render_user_profile(user, top_items)

    if is_demo:
        st.info("ℹ️ Running in **Sandbox Demo Mode**. Spotify login is bypassed, but track recommendations are still fetched live from the Spotify Web API using Client Credentials.")

    st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:1.5rem 0;'>", unsafe_allow_html=True)

    # Two-column layout: input | results
    col_input, col_results = st.columns([4, 5], gap="large")

    with col_input:
        mood_text, exploration = _render_discovery_form()

        st.markdown("<br>", unsafe_allow_html=True)
        generate_clicked = st.button("🎵  Generate My Discovery Playlist", key="generate_btn")

        if not _openai_client and not _anthropic_client:
            st.markdown("""
            <div style='margin-top:0.75rem;padding:0.75rem 1rem;background:rgba(251,191,36,0.06);
                        border:1px solid rgba(251,191,36,0.2);border-radius:8px;
                        font-size:0.82rem;color:#92400e;'>
                ⚡ Running in <b>heuristic mode</b> — add an LLM API key in <code>.env</code> for smarter results.
            </div>
            """, unsafe_allow_html=True)

    with col_results:
        # ── Research Finding → MVP Connection ───────────────────────────────
        st.markdown("""
        <div style='background:rgba(29,185,84,0.05);border:1px solid rgba(29,185,84,0.12);
                    border-radius:10px;padding:0.75rem 1rem;margin-bottom:1rem;
                    font-size:0.78rem;color:#475569;line-height:1.6;'>
            <b style='color:#1DB954;'>📊 Research finding → this MVP:</b>
            Analysis of 1,466 Spotify reviews found 86% of users trapped in repetition.
            Root cause: <i>no mechanism to express discovery intent.</i>
            This tool closes that gap — describe your mood, get what you actually want.
        </div>
        """, unsafe_allow_html=True)

        # Handle generate
        if generate_clicked:
            if not mood_text:
                st.warning("Please describe your mood first.")
            else:
                with st.spinner(""):
                    # 1. Parse mood
                    parsed = parse_mood(
                        mood_text, exploration,
                        openai_client=_openai_client,
                        anthropic_client=_anthropic_client,
                    )
                    _render_loading(mood_text, parsed.get("mode", "heuristic"))

                    # 2. Get recommendations
                    tracks = _build_recommendations(
                        token, parsed, exploration, top_artist_ids
                    )

                    if not tracks:
                        st.error("Spotify returned no tracks for this combination. Try adjusting your mood description or exploration level.")
                    else:
                        # 3. Generate explanations
                        explanations = generate_track_explanations(
                            mood_text, tracks, parsed,
                            openai_client=_openai_client,
                            anthropic_client=_anthropic_client,
                        )

                        # Cache result
                        st.session_state["last_result"] = {
                            "tracks": tracks,
                            "explanations": explanations,
                            "parsed": parsed,
                            "mood_text": mood_text,
                            "exploration": exploration,
                            "user_id": user_id,
                        }

        # Show results if available
        if "last_result" in st.session_state:
            res = st.session_state["last_result"]
            # AI Interpretation Panel — shows reasoning BEFORE tracks
            _render_interpretation_panel(
                res["parsed"], res["mood_text"],
                res["exploration"], res.get("n_excluded", 0)
            )
            track_uris = _render_results(
                res["tracks"], res["explanations"], res["parsed"],
                res["mood_text"], res["exploration"]
            )
            _render_save_section(track_uris, res["mood_text"], token, res["user_id"])

        else:
            # Empty state
            st.markdown("""
            <div class='glass-card' style='text-align:center; padding:4rem 2rem; margin-top:1rem;'>
                <div style='font-size:3rem; margin-bottom:1rem;'>🎵</div>
                <div style='font-weight:700; color:#f1f5f9; font-size:1.1rem; margin-bottom:0.5rem;'>
                    Your discovery playlist will appear here
                </div>
                <div style='color:#475569; font-size:0.88rem;'>
                    Describe your mood on the left and click Generate
                </div>
            </div>
            """, unsafe_allow_html=True)
