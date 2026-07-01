# 🛠️ Phase 4: AI-Native MVP — Build Documentation
### Spotify Contextual Discovery Engine
**Status: Built & pushed to GitHub · Pending Streamlit Cloud deployment**

---

## 4.1 What Was Built

The MVP is a standalone Streamlit application (`mvp/app.py`) that directly addresses the **intent gap** identified in Phase 3:

> *There is no mechanism for Spotify users to express their discovery intent — the emotional, contextual, or novelty-seeking goal of a listening session.*

This MVP gives users a natural language interface to express exactly what they want to feel, bypassing the algorithm's exploitation default.

---

## 4.2 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  SPOTIFY USER SESSION                    │
│         (Authenticated via OAuth2 — spotipy)            │
└───────────────────────────┬─────────────────────────────┘
                            │
              User types mood in natural language
              "music like driving through a neon city at 3AM"
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│               LLM ENGINE  (mvp/llm_engine.py)           │
│                                                         │
│  Supports: OpenAI gpt-4o-mini / Anthropic claude-haiku  │
│  Fallback: Keyword heuristic (50+ mood → feature map)   │
│                                                         │
│  Output: {valence, energy, danceability, acousticness,  │
│           instrumentalness, seed_genres, mood_summary}  │
└───────────────────────────┬─────────────────────────────┘
                            │
              Audio features + genre seeds passed to Spotify
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│          SPOTIFY RECOMMENDATIONS API                     │
│                                                         │
│  Inputs: target_valence, target_energy, seed_genres,    │
│          min_popularity, max_popularity (from dial)     │
│                                                         │
│  Discovery Dial controls popularity ceiling:            │
│    Familiar (1–3): pop 30–100, seeds from user history  │
│    Balanced (4–6): pop 15–75, mixed seeds               │
│    Explorer (7–10): pop 0–45, genre-only seeds          │
└───────────────────────────┬─────────────────────────────┘
                            │
              15 tracks returned
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│         CONTEXTUAL BRIEFING (LLM explanation layer)     │
│                                                         │
│  For each track: "Why this song fits your described     │
│  mood" — poetic, specific, max 15 words per track       │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  DYNAMIC CURATED OUTPUT                  │
│                                                         │
│  • Track cards with album art, name, artist, duration   │
│  • AI explanation per track                             │
│  • Audio feature summary (mood signature)               │
│  • One-click save to Spotify as private playlist        │
└─────────────────────────────────────────────────────────┘
```

---

## 4.3 File Structure

```
mvp/
├── app.py           — Main Streamlit app (OAuth, UI, routing)
├── llm_engine.py    — Mood parsing + track explanation generation
├── requirements.txt — Dependencies
└── .env.example     — Credential template
```

---

## 4.4 Key Features

### Natural Language Mood Input
Users describe any feeling, setting, or abstract context:
- *"Music that feels like driving through a neon-lit city at 2AM in a retro-futuristic movie"*
- *"Quiet Sunday morning with coffee and soft rain"*
- *"Pre-workout energy — aggressive but not metal"*
- *"Bittersweet nostalgia for a place I've never been"*

### Discovery Dial (Familiar ↔ Explorer)
Controls how deeply the algorithm ventures outside the user's history:

| Level | Seeds | Popularity Range | Effect |
|-------|-------|-----------------|--------|
| 1–3 (Familiar) | User's top 2 artists + 1 genre | 30–100 | Songs similar to what you already love |
| 4–6 (Balanced) | 1 user artist + 2 genres | 15–75 | Mix of familiar and fresh |
| 7–10 (Explorer) | Genre-only (3 genres) | 0–45 | Underground tracks, zero user history |

**Why this addresses the root cause:** The popularity ceiling directly overrides Spotify's default optimization (favoring high-confidence, mainstream tracks). At Explorer=10, the algorithm is forced to surface tracks the user has provably never heard.

### LLM Mode vs. Heuristic Mode

| Mode | When Active | Quality |
|------|------------|---------|
| 🤖 LLM (OpenAI gpt-4o-mini) | `OPENAI_API_KEY` set | Semantic, contextual, nuanced |
| 🤖 LLM (Anthropic claude-haiku) | `ANTHROPIC_API_KEY` set | Semantic, contextual, nuanced |
| 📐 Heuristic | No LLM key | Keyword matching across 50+ moods |

The heuristic fallback maps keywords like "neon", "night", "driving", "melancholy" to specific `{valence, energy, danceability, acousticness, instrumentalness}` values, producing reasonable results without any API cost.

### Per-Track AI Explanations
For each recommended track, the LLM generates a specific, poetic explanation:
> *"Chosen for its 'late night city drive' vibe — this track's dark synths and steady pulse match the cinematic momentum you described."*

This builds **algorithmic trust** — users can see exactly why a track was chosen, not just that it was recommended.

### Save to Spotify
One-click playlist creation:
- Creates a private playlist in the user's Spotify account
- Names it with the mood description
- Adds all 15 tracks in order

---

## 4.5 Spotify Developer Setup (Required for Deployment)

### Step 1: Create Spotify Developer App
1. Go to https://developer.spotify.com/dashboard
2. Create a new app (any name, e.g., "AI Discovery MVP")
3. Copy `Client ID` and `Client Secret`

### Step 2: Configure Redirect URI
In your Spotify app settings → Edit → Redirect URIs, add:
- For Streamlit Cloud: `https://your-mvp-app.streamlit.app/`
- For local dev: `http://localhost:8502/`

**Important:** The redirect URI must match EXACTLY (including trailing slash).

### Step 3: Set Credentials
For Streamlit Cloud (App Settings → Secrets):
```toml
SPOTIFY_CLIENT_ID = "your_client_id"
SPOTIFY_CLIENT_SECRET = "your_client_secret"
SPOTIFY_REDIRECT_URI = "https://your-mvp-app.streamlit.app/"
LLM_PROVIDER = "openai"
OPENAI_API_KEY = "your_openai_key"
```

For local development (`mvp/.env`):
```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8502/
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_key
```

### Step 4: Deploy to Streamlit Cloud
1. Go to https://share.streamlit.io
2. New app → Select repo `NL_grad_part1` → Branch `main` → Main file: `mvp/app.py`
3. Add secrets (Step 3 above)
4. Deploy

**Run locally:**
```bash
cd NL_Graduation_Project
source .venv/bin/activate
pip install -r mvp/requirements.txt
streamlit run mvp/app.py --server.port 8502
```

---

## 4.6 Why AI is Uniquely Suited (Fellowship Argument)

Traditional Spotify recommendation (Collaborative Filtering):
- Input: track/artist IDs, play history
- Process: find users with similar histories, recommend what they played
- **Cannot understand:** "driving through a neon city at 3AM"

This MVP (LLM-enhanced):
- Input: free-form natural language description of desired feeling
- LLM process: semantic parsing → audio feature space translation
  - Understands "neon city" → high energy, electronic, urban
  - Understands "3AM" → darker valence, lower tempo, introspective
  - Understands "retro-futuristic" → synth-heavy, 80s-influenced aesthetics
- Output: Spotify API call with precise audio feature parameters

**This is what AI unlocks that was previously architecturally impossible** — mapping abstract human emotional language to the mathematical space of music.

---

## 4.7 Validation Plan

### Manual Testing (Pre-deployment)
- [ ] OAuth flow: click Connect → Spotify auth page → redirect back with token
- [ ] Profile loads: user name, top artists, top genres displayed correctly
- [ ] Heuristic mode: enter "rainy day chill" → genres include ambient/indie → reasonable features
- [ ] LLM mode (if key available): enter abstract prompt → semantically accurate features
- [ ] Discovery Dial: Explorer=10 results should have avg popularity < 45
- [ ] Save playlist: creates playlist in Spotify with correct tracks and name
- [ ] Logout: clears session, returns to landing page

### User Testing (Phase 4.3 spec)
Per Phase_Wise_Implementation.md Step 5:
> "MVP Testing Confirms 80% User Success Rate in Escaping Repetitive Playlists"

Metric: Out of 5 test sessions, how many produce ≥1 track the user immediately saves?
Target: ≥4/5 sessions (80%)

---

## 4.8 Phase 5 Deck Integration

This MVP provides visual assets for:
- **Slide 6**: Conceptual overview of the MVP (architecture diagram above)
- **Slide 7**: Screenshots of the deployed interface
  - Landing page (Connect with Spotify)
  - Mood input + Discovery Dial
  - Track results with AI explanations
  - Playlist saved confirmation
- **Slide 8**: Technical architecture (data flow diagram above)
- **Slide 9**: Validation results from user testing

---

*Phase 4 completed: 23 June 2026*
*Repository: github.com/Satyamp32/NL_grad_part1 branch main*
*MVP code: mvp/ directory (pushed to GitHub for Streamlit Cloud deployment)*
*Next: Phase 5 — Pitch Deck (10 slides)*
