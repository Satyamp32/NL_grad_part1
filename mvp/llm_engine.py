"""
LLM Engine for Spotify Discovery MVP
Handles mood → audio feature translation and track explanation generation.
Falls back to keyword heuristics when no LLM key is available.
"""
import json
import logging

logger = logging.getLogger(__name__)

# ─── Heuristic Keyword → Audio Feature Mapping ────────────────────────────
# Each entry: keyword → {valence, energy, danceability, acousticness, instrumentalness}
MOOD_FEATURES: dict[str, dict] = {
    "happy":      {"valence": 0.82, "energy": 0.72, "danceability": 0.73, "acousticness": 0.25, "instrumentalness": 0.05},
    "sad":        {"valence": 0.18, "energy": 0.28, "danceability": 0.30, "acousticness": 0.68, "instrumentalness": 0.20},
    "energetic":  {"valence": 0.74, "energy": 0.91, "danceability": 0.82, "acousticness": 0.08, "instrumentalness": 0.05},
    "calm":       {"valence": 0.52, "energy": 0.18, "danceability": 0.26, "acousticness": 0.72, "instrumentalness": 0.42},
    "chill":      {"valence": 0.56, "energy": 0.32, "danceability": 0.48, "acousticness": 0.58, "instrumentalness": 0.28},
    "focus":      {"valence": 0.44, "energy": 0.38, "danceability": 0.22, "acousticness": 0.50, "instrumentalness": 0.72},
    "study":      {"valence": 0.42, "energy": 0.30, "danceability": 0.20, "acousticness": 0.55, "instrumentalness": 0.68},
    "workout":    {"valence": 0.72, "energy": 0.92, "danceability": 0.86, "acousticness": 0.06, "instrumentalness": 0.04},
    "gym":        {"valence": 0.72, "energy": 0.92, "danceability": 0.86, "acousticness": 0.06, "instrumentalness": 0.04},
    "party":      {"valence": 0.82, "energy": 0.91, "danceability": 0.90, "acousticness": 0.04, "instrumentalness": 0.03},
    "romantic":   {"valence": 0.62, "energy": 0.38, "danceability": 0.47, "acousticness": 0.62, "instrumentalness": 0.15},
    "love":       {"valence": 0.68, "energy": 0.42, "danceability": 0.50, "acousticness": 0.55, "instrumentalness": 0.12},
    "angry":      {"valence": 0.26, "energy": 0.88, "danceability": 0.62, "acousticness": 0.08, "instrumentalness": 0.10},
    "melancholy": {"valence": 0.22, "energy": 0.30, "danceability": 0.28, "acousticness": 0.64, "instrumentalness": 0.28},
    "peaceful":   {"valence": 0.62, "energy": 0.14, "danceability": 0.22, "acousticness": 0.78, "instrumentalness": 0.52},
    "morning":    {"valence": 0.65, "energy": 0.52, "danceability": 0.52, "acousticness": 0.42, "instrumentalness": 0.18},
    "night":      {"valence": 0.42, "energy": 0.52, "danceability": 0.62, "acousticness": 0.38, "instrumentalness": 0.25},
    "late":       {"valence": 0.40, "energy": 0.50, "danceability": 0.58, "acousticness": 0.40, "instrumentalness": 0.30},
    "rainy":      {"valence": 0.32, "energy": 0.22, "danceability": 0.30, "acousticness": 0.72, "instrumentalness": 0.40},
    "rain":       {"valence": 0.32, "energy": 0.22, "danceability": 0.30, "acousticness": 0.72, "instrumentalness": 0.40},
    "summer":     {"valence": 0.80, "energy": 0.74, "danceability": 0.76, "acousticness": 0.28, "instrumentalness": 0.08},
    "nostalgic":  {"valence": 0.50, "energy": 0.36, "danceability": 0.40, "acousticness": 0.58, "instrumentalness": 0.22},
    "nostalgia":  {"valence": 0.50, "energy": 0.36, "danceability": 0.40, "acousticness": 0.58, "instrumentalness": 0.22},
    "ambient":    {"valence": 0.40, "energy": 0.14, "danceability": 0.18, "acousticness": 0.70, "instrumentalness": 0.82},
    "jazz":       {"valence": 0.60, "energy": 0.40, "danceability": 0.52, "acousticness": 0.72, "instrumentalness": 0.55},
    "lofi":       {"valence": 0.46, "energy": 0.28, "danceability": 0.42, "acousticness": 0.62, "instrumentalness": 0.62},
    "lo-fi":      {"valence": 0.46, "energy": 0.28, "danceability": 0.42, "acousticness": 0.62, "instrumentalness": 0.62},
    "sleep":      {"valence": 0.42, "energy": 0.08, "danceability": 0.10, "acousticness": 0.82, "instrumentalness": 0.65},
    "excited":    {"valence": 0.86, "energy": 0.86, "danceability": 0.82, "acousticness": 0.06, "instrumentalness": 0.04},
    "driving":    {"valence": 0.70, "energy": 0.72, "danceability": 0.68, "acousticness": 0.18, "instrumentalness": 0.12},
    "drive":      {"valence": 0.70, "energy": 0.72, "danceability": 0.68, "acousticness": 0.18, "instrumentalness": 0.12},
    "heartbreak": {"valence": 0.15, "energy": 0.35, "danceability": 0.32, "acousticness": 0.60, "instrumentalness": 0.15},
    "hopeful":    {"valence": 0.70, "energy": 0.55, "danceability": 0.58, "acousticness": 0.42, "instrumentalness": 0.12},
    "dark":       {"valence": 0.20, "energy": 0.65, "danceability": 0.48, "acousticness": 0.25, "instrumentalness": 0.30},
    "bright":     {"valence": 0.78, "energy": 0.70, "danceability": 0.68, "acousticness": 0.30, "instrumentalness": 0.08},
    "acoustic":   {"valence": 0.55, "energy": 0.38, "danceability": 0.42, "acousticness": 0.85, "instrumentalness": 0.20},
    "electronic": {"valence": 0.60, "energy": 0.78, "danceability": 0.78, "acousticness": 0.05, "instrumentalness": 0.45},
    "indie":      {"valence": 0.55, "energy": 0.52, "danceability": 0.56, "acousticness": 0.50, "instrumentalness": 0.18},
    "coffee":     {"valence": 0.58, "energy": 0.28, "danceability": 0.40, "acousticness": 0.65, "instrumentalness": 0.35},
    "dinner":     {"valence": 0.60, "energy": 0.30, "danceability": 0.38, "acousticness": 0.60, "instrumentalness": 0.40},
    "city":       {"valence": 0.55, "energy": 0.62, "danceability": 0.65, "acousticness": 0.20, "instrumentalness": 0.25},
    "neon":       {"valence": 0.50, "energy": 0.72, "danceability": 0.70, "acousticness": 0.10, "instrumentalness": 0.40},
    "retro":      {"valence": 0.62, "energy": 0.58, "danceability": 0.65, "acousticness": 0.42, "instrumentalness": 0.20},
    "cozy":       {"valence": 0.60, "energy": 0.25, "danceability": 0.35, "acousticness": 0.70, "instrumentalness": 0.38},
    "upbeat":     {"valence": 0.80, "energy": 0.80, "danceability": 0.78, "acousticness": 0.12, "instrumentalness": 0.05},
    "slow":       {"valence": 0.45, "energy": 0.22, "danceability": 0.30, "acousticness": 0.65, "instrumentalness": 0.30},
    "fast":       {"valence": 0.68, "energy": 0.84, "danceability": 0.80, "acousticness": 0.08, "instrumentalness": 0.08},
    "sad":        {"valence": 0.18, "energy": 0.28, "danceability": 0.30, "acousticness": 0.68, "instrumentalness": 0.20},
    "fun":        {"valence": 0.82, "energy": 0.80, "danceability": 0.82, "acousticness": 0.10, "instrumentalness": 0.04},
    "pump":       {"valence": 0.74, "energy": 0.92, "danceability": 0.84, "acousticness": 0.05, "instrumentalness": 0.05},
    "sunset":     {"valence": 0.65, "energy": 0.42, "danceability": 0.50, "acousticness": 0.52, "instrumentalness": 0.28},
    "melancholic":{"valence": 0.22, "energy": 0.30, "danceability": 0.28, "acousticness": 0.64, "instrumentalness": 0.28},
    "bittersweet":{"valence": 0.40, "energy": 0.38, "danceability": 0.38, "acousticness": 0.55, "instrumentalness": 0.22},
}

MOOD_GENRES: dict[str, list] = {
    "happy":      ["pop", "indie-pop", "dance"],
    "sad":        ["indie", "alternative", "singer-songwriter"],
    "energetic":  ["rock", "electronic", "hip-hop"],
    "calm":       ["ambient", "acoustic", "folk"],
    "chill":      ["chill", "indie", "lo-fi"],
    "focus":      ["ambient", "classical", "electronic"],
    "study":      ["ambient", "classical", "jazz"],
    "workout":    ["hip-hop", "electronic", "rock"],
    "gym":        ["hip-hop", "electronic", "rock"],
    "party":      ["pop", "dance", "hip-hop"],
    "romantic":   ["r-n-b", "soul", "singer-songwriter"],
    "love":       ["r-n-b", "soul", "pop"],
    "angry":      ["rock", "metal", "hip-hop"],
    "melancholy": ["indie", "alternative", "folk"],
    "peaceful":   ["ambient", "classical", "acoustic"],
    "morning":    ["pop", "indie-pop", "acoustic"],
    "night":      ["electronic", "r-n-b", "indie"],
    "rainy":      ["indie", "acoustic", "ambient"],
    "summer":     ["pop", "dance", "indie-pop"],
    "nostalgic":  ["indie", "alternative", "folk"],
    "ambient":    ["ambient", "electronic", "classical"],
    "jazz":       ["jazz", "soul", "blues"],
    "lofi":       ["chill", "jazz", "ambient"],
    "sleep":      ["ambient", "classical", "acoustic"],
    "excited":    ["pop", "dance", "hip-hop"],
    "driving":    ["rock", "pop", "hip-hop"],
    "coffee":     ["jazz", "acoustic", "indie"],
    "dinner":     ["jazz", "soul", "acoustic"],
    "indie":      ["indie", "alternative", "indie-pop"],
    "electronic": ["electronic", "dance", "ambient"],
    "acoustic":   ["acoustic", "folk", "singer-songwriter"],
    "city":       ["electronic", "hip-hop", "indie"],
    "retro":      ["pop", "indie", "funk"],
    "cozy":       ["acoustic", "folk", "indie"],
    "dark":       ["electronic", "alternative", "gothic"],
    "heartbreak": ["singer-songwriter", "indie", "soul"],
    "fun":        ["pop", "dance", "indie-pop"],
    "upbeat":     ["pop", "dance", "indie-pop"],
    "sunset":     ["indie", "ambient", "chillout"],
    "melancholic":["indie", "alternative", "folk"],
    "bittersweet":["indie", "alternative", "singer-songwriter"],
}

_DEFAULTS = {
    "features": {"valence": 0.5, "energy": 0.5, "danceability": 0.5, "acousticness": 0.4, "instrumentalness": 0.1},
    "genres": ["pop", "indie", "alternative"],
    "mood_summary": "a balanced, open listening session",
}


def _heuristic_parse(mood_text: str, exploration_level: int) -> dict:
    """Keyword-matching fallback when no LLM key is available."""
    tokens = mood_text.lower().split()
    # Also check multi-word combos like "lo-fi"
    full_text = mood_text.lower()

    matched_features = []
    matched_genres = []

    for keyword, features in MOOD_FEATURES.items():
        if keyword in full_text:
            matched_features.append(features)
    for keyword, genres in MOOD_GENRES.items():
        if keyword in full_text:
            matched_genres.extend(genres)

    if not matched_features:
        avg_features = _DEFAULTS["features"].copy()
    else:
        avg_features = {}
        for key in _DEFAULTS["features"]:
            avg_features[key] = round(sum(f[key] for f in matched_features) / len(matched_features), 3)

    # Blend exploration level into the features
    # High exploration (10) = lower instrumentalness ceiling, higher popularity_max handled externally
    exploration_ratio = exploration_level / 10.0

    # Deduplicate genres, prefer first seen (most confident), cap at 3
    seen = set()
    unique_genres = []
    for g in matched_genres:
        if g not in seen:
            seen.add(g)
            unique_genres.append(g)
        if len(unique_genres) == 3:
            break
    if not unique_genres:
        unique_genres = _DEFAULTS["genres"]

    return {
        "features": avg_features,
        "genres": unique_genres,
        "mood_summary": f"a {mood_text.strip()[:60]} vibe",
        "mode": "heuristic",
        "exploration_ratio": exploration_ratio,
    }


def _llm_parse_openai(mood_text: str, exploration_level: int, client) -> dict:
    """Parse mood using OpenAI GPT."""
    prompt = f"""You are a music curation AI. A user described their mood as:
"{mood_text}"
Their exploration preference is {exploration_level}/10 (1=very familiar music, 10=maximum new discovery).

Respond ONLY with a valid JSON object (no markdown) with these exact keys:
{{
  "genres": ["genre1", "genre2", "genre3"],   // 2-3 valid Spotify genre seeds from: pop, indie, rock, hip-hop, r-n-b, jazz, classical, electronic, dance, ambient, alternative, chill, folk, soul, blues, country, metal, singer-songwriter, acoustic, lo-fi
  "valence": 0.0-1.0,        // 0=very sad, 1=very happy
  "energy": 0.0-1.0,         // 0=calm/quiet, 1=intense/loud
  "danceability": 0.0-1.0,   // 0=not danceable, 1=very danceable
  "acousticness": 0.0-1.0,   // 0=electronic, 1=fully acoustic
  "instrumentalness": 0.0-1.0, // 0=has vocals, 1=purely instrumental
  "mood_summary": "one short phrase describing the vibe (max 8 words)"
}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=300,
    )
    raw = response.choices[0].message.content.strip()
    data = json.loads(raw)
    exploration_ratio = exploration_level / 10.0
    return {
        "features": {
            "valence": float(data["valence"]),
            "energy": float(data["energy"]),
            "danceability": float(data["danceability"]),
            "acousticness": float(data["acousticness"]),
            "instrumentalness": float(data["instrumentalness"]),
        },
        "genres": data["genres"][:3],
        "mood_summary": data.get("mood_summary", mood_text[:60]),
        "mode": "openai",
        "exploration_ratio": exploration_ratio,
    }


def _llm_parse_anthropic(mood_text: str, exploration_level: int, client) -> dict:
    """Parse mood using Anthropic Claude."""
    prompt = f"""You are a music curation AI. A user described their mood as:
"{mood_text}"
Their exploration preference is {exploration_level}/10 (1=very familiar music, 10=maximum new discovery).

Respond ONLY with a valid JSON object (no markdown, no explanation) with these exact keys:
{{
  "genres": ["genre1", "genre2"],
  "valence": 0.55,
  "energy": 0.60,
  "danceability": 0.55,
  "acousticness": 0.40,
  "instrumentalness": 0.10,
  "mood_summary": "short vibe phrase"
}}

genres must be from: pop, indie, rock, hip-hop, r-n-b, jazz, classical, electronic, dance, ambient, alternative, chill, folk, soul, blues, singer-songwriter, acoustic"""

    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    data = json.loads(raw)
    exploration_ratio = exploration_level / 10.0
    return {
        "features": {
            "valence": float(data["valence"]),
            "energy": float(data["energy"]),
            "danceability": float(data["danceability"]),
            "acousticness": float(data["acousticness"]),
            "instrumentalness": float(data["instrumentalness"]),
        },
        "genres": data["genres"][:3],
        "mood_summary": data.get("mood_summary", mood_text[:60]),
        "mode": "anthropic",
        "exploration_ratio": exploration_ratio,
    }


def parse_mood(mood_text: str, exploration_level: int = 5,
               openai_client=None, anthropic_client=None) -> dict:
    """
    Main entry point. Tries LLM first, falls back to heuristics.
    Returns a dict with: features, genres, mood_summary, mode, exploration_ratio
    """
    if openai_client:
        try:
            return _llm_parse_openai(mood_text, exploration_level, openai_client)
        except Exception as e:
            logger.warning(f"OpenAI mood parse failed ({e}), falling back to heuristic")

    if anthropic_client:
        try:
            return _llm_parse_anthropic(mood_text, exploration_level, anthropic_client)
        except Exception as e:
            logger.warning(f"Anthropic mood parse failed ({e}), falling back to heuristic")

    return _heuristic_parse(mood_text, exploration_level)


def generate_track_explanations(mood_text: str, tracks: list,
                                 parsed_mood: dict,
                                 openai_client=None, anthropic_client=None) -> list[str]:
    """
    Generate a one-sentence explanation for each track explaining why it fits the mood.
    Falls back to template-based explanations.
    """
    if not tracks:
        return []

    # Template fallback — references actual audio features for credibility
    def template_explanation(track: dict, mood_summary: str) -> str:
        pop         = track.get("popularity")
        pop         = pop if pop is not None else 50
        features    = parsed_mood.get("features", {})
        energy      = features.get("energy", 0.5)
        valence     = features.get("valence", 0.5)
        acousticness= features.get("acousticness", 0.4)

        e_w  = "high-energy" if energy > 0.65 else ("mellow" if energy < 0.35 else "mid-tempo")
        t_w  = "uplifting"   if valence > 0.62 else ("melancholic" if valence < 0.35 else "emotionally layered")
        x_w  = "acoustic"    if acousticness > 0.62 else ("electronic" if acousticness < 0.25 else "hybrid")
        d_note = "likely new to you" if pop < 40 else ("a niche pick" if pop < 58 else "a resonant find")

        return f"Fits your '{mood_summary}' — {e_w}, {t_w}, {x_w} texture. Popularity {pop}/100 — {d_note}."

    # Build track list for LLM
    track_lines = "\n".join(
        f"{i+1}. \"{t['name']}\" by {t['artists'][0]['name']}"
        for i, t in enumerate(tracks[:10])
    )
    mood_summary = parsed_mood.get("mood_summary", mood_text[:60])

    prompt = f"""A user said they want music for: "{mood_text}" (vibe: {mood_summary})

The following tracks were recommended. Write one SHORT sentence (max 15 words) per track explaining WHY it fits this specific mood. Be poetic and specific, not generic.

Tracks:
{track_lines}

Respond ONLY as a JSON array of strings, one per track, same order:
["explanation 1", "explanation 2", ...]"""

    if openai_client:
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=600,
            )
            explanations = json.loads(response.choices[0].message.content.strip())
            if isinstance(explanations, list) and len(explanations) >= len(tracks[:10]):
                return explanations[:len(tracks)]
        except Exception as e:
            logger.warning(f"OpenAI explanation generation failed: {e}")

    if anthropic_client:
        try:
            response = anthropic_client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}],
            )
            explanations = json.loads(response.content[0].text.strip())
            if isinstance(explanations, list) and len(explanations) >= len(tracks[:10]):
                return explanations[:len(tracks)]
        except Exception as e:
            logger.warning(f"Anthropic explanation generation failed: {e}")

    # Fallback
    return [template_explanation(t, mood_summary) for t in tracks]
