import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Project Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw_reviews.json"
ANALYZED_DATA_PATH = DATA_DIR / "analyzed_reviews.json"
REPORT_PATH = DATA_DIR / "synthesis_report.json"
SEED_REDDIT_PATH = DATA_DIR / "seed_reddit.json"

# Create directories if they do not exist
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Spotify Identifiers for Scrapers
SPOTIFY_PLAY_STORE_ID = "com.spotify.music"
SPOTIFY_APP_STORE_ID = 324684580  # App Store ID for Spotify

# Search Keywords for filtering
DISCOVERY_KEYWORDS = [
    "recommend", "discovery", "recommendation", "algorithm", "shuffle",
    "repeat", "boring", "same songs", "stuck", "discover weekly",
    "smart shuffle", "dj", "daily mix", "feedback loop", "echo chamber"
]

# API Keys & Configurations
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

# Preferred LLM Provider (openai or anthropic)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

# Reddit Credentials (optional)
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "spotify-pm-project:v1.0 (by /u/username)")
