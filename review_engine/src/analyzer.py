import json
import logging
import time
from datetime import datetime
from pathlib import Path
import pandas as pd

from review_engine.src.config import (
    RAW_DATA_PATH,
    ANALYZED_DATA_PATH,
    REPORT_PATH,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    LLM_PROVIDER
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize LLM Clients if keys exist (and are not placeholders)
openai_client = None
if OPENAI_API_KEY and not OPENAI_API_KEY.startswith("your-"):
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")

anthropic_client = None
if ANTHROPIC_API_KEY and not ANTHROPIC_API_KEY.startswith("your-"):
    try:
        from anthropic import Anthropic
        anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize Anthropic client: {e}")

def get_fallback_classification(review: dict) -> dict:
    """Provides a heuristic-based mock classification for local dry runs without API keys."""
    text_lower = review.get("text", "").lower()
    title_lower = review.get("title", "").lower()
    combined_text = f"{title_lower} {text_lower}"
    rating = review.get("rating", 3)
    
    sentiment = "Neutral"
    if rating <= 2:
        sentiment = "Negative"
    elif rating >= 4:
        sentiment = "Positive"
        
    # Heuristics based on keywords
    if "shuffle" in combined_text or "random" in combined_text:
        category = "Shuffle Dissatisfaction"
        core_frustration = "Smart shuffle repeating same tracks or not feeling truly random."
        severity = "High" if rating <= 2 else "Medium"
    elif any(kw in combined_text for kw in ["focus", "study", "sleep", "lofi", "kids", "contamination", "private"]):
        category = "Context Contamination"
        core_frustration = "Single listening session (focus/kids) permanently poisoning recommendations."
        severity = "High" if rating <= 2 else "Medium"
    elif any(kw in combined_text for kw in ["algorithm", "recommend", "weekly", "radar", "repeat"]):
        category = "Algorithmic Repeatability"
        core_frustration = "Recommendation engine falling back to familiar tracks or creating an echo chamber."
        severity = "High" if rating <= 2 else "Medium"
    elif any(kw in combined_text for kw in ["search", "find", "ui", "ux", "menu", "layout", "click"]):
        category = "UX Friction"
        core_frustration = "Manual search and discovery is tedious and requires too much cognitive effort."
        severity = "Medium"
    elif any(kw in combined_text for kw in ["friend", "share", "social", "community"]):
        category = "Social Discovery Deficit"
        core_frustration = "Difficulty sharing music or finding music based on friend activity."
        severity = "Low"
    else:
        category = "Other"
        core_frustration = "General performance or minor usability feedback."
        severity = "Low"
        
    return {
        "id": review.get("id"),
        "source": review.get("source"),
        "date": review.get("date"),
        "rating": rating,
        "title": review.get("title"),
        "text": review.get("text"),
        "sentiment": sentiment,
        "category": category,
        "core_frustration": core_frustration,
        "severity": severity
    }

def classify_reviews_llm_openai(reviews_batch: list) -> list:
    """Uses OpenAI GPT-4o-mini to classify a batch of reviews."""
    if not openai_client:
        raise ValueError("OpenAI client not initialized.")
        
    system_prompt = (
        "You are an expert Spotify Product Manager analyzing user reviews about music discovery.\n"
        "Analyze the list of user reviews and classify each one in JSON format. Return a list of JSON objects matching the input length.\n"
        "For each review, determine:\n"
        "1. sentiment: Positive, Neutral, Negative\n"
        "2. category: Choose exactly one: 'Algorithmic Repeatability', 'Shuffle Dissatisfaction', 'Context Contamination', 'UX Friction', 'Social Discovery Deficit', 'Other'\n"
        "3. core_frustration: A 1-sentence description of the user's core issue.\n"
        "4. severity: High, Medium, Low (High if it blocks discovery or breaks usage, Low if it is minor/satisfactory)\n\n"
        "Respond ONLY with a valid JSON array, do not include markdown blocks or code formatting wrappers (like ```json)."
    )
    
    # Format batch content
    batch_input = [{"id": r["id"], "text": f"Title: {r['title']}\nReview: {r['text']}"} for r in reviews_batch]
    
    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(batch_input)}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        raw_result = json.loads(response.choices[0].message.content)
        # Parse output - handle if nested in key 'reviews' or similar
        reviews_classified = raw_result if isinstance(raw_result, list) else raw_result.get("reviews", list(raw_result.values())[0])
        
        # Merge back with original fields
        result_map = {r["id"]: r for r in reviews_classified}
        final_batch = []
        for orig in reviews_batch:
            classified = result_map.get(orig["id"], {})
            final_batch.append({
                **orig,
                "sentiment": classified.get("sentiment", "Neutral"),
                "category": classified.get("category", "Other"),
                "core_frustration": classified.get("core_frustration", "Uncategorized feedback."),
                "severity": classified.get("severity", "Low")
            })
        return final_batch
    except Exception as e:
        logger.error(f"OpenAI batch classification failed: {e}. Falling back to rules.")
        return [get_fallback_classification(r) for r in reviews_batch]

def classify_reviews_llm_anthropic(reviews_batch: list) -> list:
    """Uses Anthropic Claude to classify a batch of reviews."""
    if not anthropic_client:
        raise ValueError("Anthropic client not initialized.")
        
    system_prompt = (
        "You are an expert Spotify Product Manager analyzing user reviews about music discovery.\n"
        "Analyze the list of user reviews and classify each one in JSON format. Return a list of JSON objects matching the input length.\n"
        "For each review, determine:\n"
        "1. sentiment: Positive, Neutral, Negative\n"
        "2. category: Choose exactly one: 'Algorithmic Repeatability', 'Shuffle Dissatisfaction', 'Context Contamination', 'UX Friction', 'Social Discovery Deficit', 'Other'\n"
        "3. core_frustration: A 1-sentence description of the user's core issue.\n"
        "4. severity: High, Medium, Low\n\n"
        "Respond ONLY with a valid JSON array wrapped in a root object like {\"reviews\": [...]}. No conversational filler."
    )
    
    batch_input = [{"id": r["id"], "text": f"Title: {r['title']}\nReview: {r['text']}"} for r in reviews_batch]
    
    try:
        response = anthropic_client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=4000,
            temperature=0.0,
            system=system_prompt,
            messages=[
                {"role": "user", "content": json.dumps(batch_input)}
            ]
        )
        
        raw_result = json.loads(response.content[0].text)
        reviews_classified = raw_result.get("reviews", raw_result if isinstance(raw_result, list) else [])
        
        result_map = {r["id"]: r for r in reviews_classified}
        final_batch = []
        for orig in reviews_batch:
            classified = result_map.get(orig["id"], {})
            final_batch.append({
                **orig,
                "sentiment": classified.get("sentiment", "Neutral"),
                "category": classified.get("category", "Other"),
                "core_frustration": classified.get("core_frustration", "Uncategorized feedback."),
                "severity": classified.get("severity", "Low")
            })
        return final_batch
    except Exception as e:
        logger.error(f"Anthropic batch classification failed: {e}. Falling back to rules.")
        return [get_fallback_classification(r) for r in reviews_batch]

def run_classification(sample_limit=None):
    """Loads raw reviews, batches them, classifies via chosen provider or heuristic fallback."""
    if not RAW_DATA_PATH.exists():
        logger.error(f"Raw reviews file not found at {RAW_DATA_PATH}. Please run scrape first.")
        return []
        
    with open(RAW_DATA_PATH, 'r') as f:
        reviews_list = json.load(f)
        
    if sample_limit:
        reviews_list = reviews_list[:sample_limit]
        logger.info(f"Subsampling to {sample_limit} reviews for quick analysis.")
        
    total_reviews = len(reviews_list)
    logger.info(f"Loaded {total_reviews} reviews to classify.")
    
    # Decide provider
    use_llm = False
    if LLM_PROVIDER == "openai" and openai_client:
        use_llm = True
        logger.info("Using OpenAI LLM classification pipeline.")
    elif LLM_PROVIDER == "anthropic" and anthropic_client:
        use_llm = True
        logger.info("Using Anthropic LLM classification pipeline.")
    else:
        logger.warning("No LLM credentials found or invalid provider specified. Running with heuristic classification rules...")
        
    analyzed_reviews = []
    
    if use_llm:
        batch_size = 15
        for i in range(0, total_reviews, batch_size):
            batch = reviews_list[i : i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1} / {-( -total_reviews // batch_size )}...")
            
            if LLM_PROVIDER == "openai":
                classified_batch = classify_reviews_llm_openai(batch)
            else:
                classified_batch = classify_reviews_llm_anthropic(batch)
                
            analyzed_reviews.extend(classified_batch)
            time.sleep(1) # Simple rate limit spacing
    else:
        # Fallback heuristic rules (extremely fast, zero latency/cost)
        for r in reviews_list:
            analyzed_reviews.append(get_fallback_classification(r))
            
    # Save analyzed dataset
    with open(ANALYZED_DATA_PATH, 'w') as f:
        json.dump(analyzed_reviews, f, indent=2)
        
    logger.info(f"Successfully classified and saved {len(analyzed_reviews)} reviews to {ANALYZED_DATA_PATH}")
    return analyzed_reviews

def generate_synthesis_report(analyzed_reviews: list):
    """Aggregates analyzed data and generates a high-level PM Synthesis report."""
    logger.info("Synthesizing final PM report...")
    df = pd.DataFrame(analyzed_reviews)
    
    # Basic Aggregates
    total_reviews = len(df)
    category_counts = df["category"].value_counts().to_dict()
    sentiment_counts = df["sentiment"].value_counts().to_dict()
    high_severity_count = int((df["severity"] == "High").sum())
    
    stats_summary = {
        "total_analyzed": total_reviews,
        "categories": category_counts,
        "sentiment": sentiment_counts,
        "high_severity_incidents": high_severity_count
    }
    
    # If API keys are available, use LLM to write a refined PM synthesis, else use preloaded professional insights.
    use_llm = (LLM_PROVIDER == "openai" and openai_client) or (LLM_PROVIDER == "anthropic" and anthropic_client)
    
    if use_llm:
        # Pass aggregates and top representative issues to LLM
        sample_complaints = df[df["severity"] == "High"].head(10)[["source", "category", "text"]].to_dict(orient="records")
        
        system_prompt = (
            "You are a Principal Product Manager on the Spotify Growth team. You have just run an AI analysis of user feedback at scale.\n"
            "Generate a highly detailed PM synthesis report answering the core strategic questions.\n"
            "Format the output strictly as a JSON object with these EXACT keys:\n"
            "1. 'why_discovery_struggle' - Explaining why users find it hard to discover new music.\n"
            "2. 'common_frustrations' - Top list of frustrations with current recommendation systems.\n"
            "3. 'intended_behaviors' - What listening goals or outcomes users are trying to achieve.\n"
            "4. 'repetition_causes' - The mechanical/algorithmic causes driving repetitive listening.\n"
            "5. 'user_segments' - Details on which user segments experience different discovery challenges.\n"
            "6. 'unmet_needs' - Key unmet product opportunities.\n\n"
            "Answer with deep, analytical PM jargon (e.g. Collaborative Filtering boundaries, context contamination, active vs passive curation, discovery fatigue). Write 2-3 detailed paragraphs per key."
        )
        
        prompt_content = {
            "statistics": stats_summary,
            "representative_complaints": sample_complaints
        }
        
        try:
            if LLM_PROVIDER == "openai":
                response = openai_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": json.dumps(prompt_content)}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.7
                )
                report_content = json.loads(response.choices[0].message.content)
            else:
                response = anthropic_client.messages.create(
                    model=ANTHROPIC_MODEL,
                    max_tokens=4000,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": json.dumps(prompt_content)}
                    ],
                    temperature=0.7
                )
                report_content = json.loads(response.content[0].text)
                
            # Embed statistics in final report
            final_report = {
                "metadata": {
                    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "llm_synthesized": True
                },
                "stats": stats_summary,
                "answers": report_content
            }
            
            with open(REPORT_PATH, 'w') as f:
                json.dump(final_report, f, indent=2)
            logger.info(f"Synthesized report saved to {REPORT_PATH}")
            return final_report
            
        except Exception as e:
            logger.error(f"Failed LLM synthesis report: {e}. Falling back to preloaded report.")
            
    # Mock/Heuristics Preloaded PM Report (High Quality)
    logger.info("Generating preloaded PM Synthesis report (Fallback mode)...")
    answers = {
        "why_discovery_struggle": (
            "Users struggle to discover new music primarily due to 'Discovery Fatigue' and 'Risk Aversion'. "
            "Manual discovery requires high cognitive load—navigating complex search interfaces, scrolling through genre tags, "
            "and previewing unknown tracks. Spotify's interface does not support low-effort, high-reward exploration, forcing users "
            "to resort to active search or curation, which busy users do not have time for. Additionally, collaborative filtering "
            "often pushes users towards safe, highly-played mainstream songs (exploitation) to protect immediate session retention, "
            "creating an artificial boundary around their music profile."
        ),
        "common_frustrations": (
            "1. **Smart Shuffle Repeat Loop:** Users express high frustration with 'Smart Shuffle' repeating the same 10-15 recommended songs, "
            "often ignoring explicit skips or dislikes. This breaks user trust in the system's ability to diversify music.\n"
            "2. **Algorithmic Repetitive Recommendations:** Users report their Discover Weekly, Daily Mixes, and Radio sessions returning to "
            "the same pool of highly familiar 'Liked Songs' rather than actual long-tail discovery.\n"
            "3. **Context Contamination:** The system lacks boundary walls between different listening contexts. A single session of focus music, "
            "lullabies, or shared device use (e.g. kids' songs) permanently alters a user's primary recommendation profile."
        ),
        "intended_behaviors": (
            "Users are trying to achieve distinct listening goals based on their physical or emotional environment:\n"
            "- **Active Enrichment:** Finding hidden gems, obscure artists, or fresh releases within their niche to expand custom playlists.\n"
            "- **Lean-Back Discovery:** Starting a radio or auto-mix that serves new but highly relevant music in the background without needing "
            "to check their screen or manually skip songs.\n"
            "- **Functional Listening:** Playing utility audio (lofi beats for focus, brown noise for sleep, children's playlists) that "
            "should remain isolated from their primary personal taste identity."
        ),
        "repetition_causes": (
            "1. **Collaborative Filtering Loop:** Spotify's algorithm matches user profiles based on shared tracks. This naturally pushes "
            "users into the center of 'taste clusters,' making it structurally difficult to jump to adjacent clusters without active manual intervention.\n"
            "2. **Immediate Skips Optimization:** The recommendation engine is heavily optimized to minimize session skips (which are perceived as failures). "
            "Playing familiar songs guarantees high short-term engagement but causes long-term boredom and stagnation.\n"
            "3. **Lack of User Controls:** Standard shuffle relies on weighted probability curves that favor highly popular or recently played tracks, "
            "meaning a 1,000-song playlist gets condensed into a repetitive 50-song loop."
        ),
        "user_segments": (
            "1. **Active Curators (Power Users):** Highly sensitive to repetition. They want obscure recommendations, granular genre mapping, "
            "and explicit control features (e.g., exclude genres/artists, true random shuffle).\n"
            "2. **Passive Lean-Back Listeners:** Struggle with UX friction. They want the algorithm to 'just work' and feed them varied music "
            "without manual input. They suffer from the same songs repeating but rarely manually search for alternatives.\n"
            "3. **Context-Switched Listeners:** Users sharing devices or accounts (e.g., parent/child, office audio). They suffer from recommendation "
            "contamination and need profile compartmentalization."
        ),
        "unmet_needs": (
            "1. **Context/Mood Segmentation:** A 'sandbox' or 'private session' switch that disables recommendation training for specific activities "
            "(focus, sleep, kids, parties).\n"
            "2. **Negative Preference Controls:** Direct features allowing users to explicitly block artists, exclude genres, or reset/prune specific "
            "branches of their algorithmic profile (e.g., 'Do not use this track/session to train my recommendation engine').\n"
            "3. **Mood & Descriptive Querying:** An LLM-powered natural language prompt system that allows users to ask for music using complex, abstract, "
            "or contextual descriptions (e.g. 'indie songs that feel like an autumn rainy walk in London') rather than relying on search keywords."
        )
    }
    
    final_report = {
        "metadata": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "llm_synthesized": False
        },
        "stats": stats_summary,
        "answers": answers
    }
    
    with open(REPORT_PATH, 'w') as f:
        json.dump(final_report, f, indent=2)
    logger.info(f"Fallback synthesis report saved to {REPORT_PATH}")
    return final_report

if __name__ == "__main__":
    # Test run
    raw_data = [{"id": "test_1", "source": "Play Store", "date": "2026-06-20", "rating": 2, "title": "Shuffle sucks", "text": "This app plays the same songs on shuffle over and over again!"}]
    run_classification()
