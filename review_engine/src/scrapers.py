import json
import logging
from datetime import datetime
from google_play_scraper import reviews, Sort
import pandas as pd
import requests
import praw

from review_engine.src.config import (
    RAW_DATA_PATH,
    SEED_REDDIT_PATH,
    SPOTIFY_PLAY_STORE_ID,
    SPOTIFY_APP_STORE_ID,
    DISCOVERY_KEYWORDS,
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def contains_keywords(text: str) -> bool:
    """Checks if the text contains any music discovery-related keywords."""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in DISCOVERY_KEYWORDS)

def scrape_google_play(limit=100) -> list:
    """Scrapes Spotify reviews from the Google Play Store."""
    logger.info(f"Starting Google Play Store scraping (limit={limit})...")
    scraped_reviews = []
    
    # We scrape in batches of 100, targeting lower ratings (1-3 stars)
    try:
        # We perform scrapes sorting by both NEWEST and RELEVANCY
        for sort_order in [Sort.NEWEST, Sort.MOST_RELEVANT]:
            result, _ = reviews(
                SPOTIFY_PLAY_STORE_ID,
                lang='en',
                country='us',
                sort=sort_order,
                count=limit // 2,
                filter_score_with=None # get all scores, we will filter manually or accept them
            )
            for r in result:
                text = r.get("content", "")
                score = r.get("score", 0)
                # Filter for low ratings (friction) or containing discovery keywords
                if score <= 3 or contains_keywords(text):
                    scraped_reviews.append({
                        "id": f"play_store_{r.get('reviewId')}",
                        "source": "Play Store",
                        "date": r.get("at").strftime("%Y-%m-%d") if isinstance(r.get("at"), datetime) else str(r.get("at"))[:10],
                        "rating": score,
                        "title": "Google Play Review",
                        "text": text
                    })
        
        logger.info(f"Scraped {len(scraped_reviews)} relevant Google Play Store reviews.")
    except Exception as e:
        logger.error(f"Error scraping Google Play Store: {e}")
        
    return scraped_reviews

def scrape_app_store(limit=500) -> list:
    """Scrapes Spotify reviews from the iOS App Store via the iTunes RSS feed across multiple regions."""
    countries = ["us", "gb", "ca", "au", "in"]
    logger.info(f"Starting iOS App Store scraping via iTunes RSS feed across regions: {countries} (limit={limit})...")
    scraped_reviews = []
    
    # Divide the total limit among the countries
    limit_per_country = max(50, limit // len(countries))
    pages_per_country = (limit_per_country // 50) + (1 if limit_per_country % 50 > 0 else 0)
    pages_per_country = max(1, min(pages_per_country, 10))  # Apple caps RSS feeds at 10 pages (500 reviews)
    
    for country in countries:
        logger.info(f"Scraping region '{country}' (pages={pages_per_country})...")
        country_reviews_count = 0
        for page in range(1, pages_per_country + 1):
            url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={SPOTIFY_APP_STORE_ID}/sortby=mostrecent/json"
            try:
                response = requests.get(url, timeout=10)
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch App Store page {page} for region '{country}': {response.status_code}")
                    break
                    
                data = response.json()
                entries = data.get("feed", {}).get("entry", [])
                
                # If only one review is returned, entry might be a dict instead of a list
                if isinstance(entries, dict):
                    entries = [entries]
                    
                for entry in entries:
                    if "id" not in entry or "im:rating" not in entry:
                        continue
                        
                    review_id = entry.get("id", {}).get("label")
                    title = entry.get("title", {}).get("label", "iOS Review")
                    rating = int(entry.get("im:rating", {}).get("label", "0"))
                    content = entry.get("content", {}).get("label", "")
                    
                    if not content:
                        continue
                        
                    date_val = entry.get("updated", {}).get("label", "")[:10]  # Format: YYYY-MM-DD
                    
                    if rating <= 3 or contains_keywords(content):
                        scraped_reviews.append({
                            "id": f"app_store_{country}_{review_id}",
                            "source": "App Store",
                            "date": date_val,
                            "rating": rating,
                            "title": title,
                            "text": content
                        })
                        country_reviews_count += 1
                        
            except Exception as e:
                logger.error(f"Error scraping App Store page {page} for region '{country}': {e}")
                break
        logger.info(f"Scraped {country_reviews_count} relevant reviews from region '{country}'.")
        
    logger.info(f"Scraped a total of {len(scraped_reviews)} relevant App Store reviews across all regions.")
    return scraped_reviews



def scrape_reddit(limit=50) -> list:
    """Scrapes Reddit discussions from r/spotify or falls back to seed data."""
    logger.info("Starting Reddit scraping...")
    
    # Check if credentials are set
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        logger.warning("Reddit API credentials missing in .env. Falling back to preloaded seed data...")
        return load_seed_reddit()
        
    scraped_posts = []
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        
        subreddit = reddit.subreddit("spotify")
        
        # Search r/spotify for discovery keywords
        for keyword in ["shuffle", "recommendations", "recommend", "discovery", "repeat songs"]:
            search_limit = max(10, limit // 5)
            for submission in subreddit.search(keyword, sort="relevance", time_filter="year", limit=search_limit):
                text_content = f"{submission.title}\n{submission.selftext}"
                
                # Fetch a couple of top comments to capture community reactions
                submission.comment_sort = "top"
                submission.comments.replace_more(limit=0)
                comments_text = []
                for i, comment in enumerate(submission.comments[:3]):
                    comments_text.append(f"Comment {i+1}: {comment.body}")
                
                full_text = text_content + "\n" + "\n".join(comments_text)
                
                date_str = datetime.fromtimestamp(submission.created_utc).strftime("%Y-%m-%d")
                
                scraped_posts.append({
                    "id": f"reddit_{submission.id}",
                    "source": "Reddit",
                    "date": date_str,
                    "rating": 2,  # Reddit posts are mapped to rating 2 (Neutral/Negative frustration)
                    "title": submission.title,
                    "text": full_text
                })
                
        logger.info(f"Successfully scraped {len(scraped_posts)} posts from Reddit.")
        
        # If scraper returned nothing, use fallback
        if not scraped_posts:
            logger.info("No Reddit posts found matching keywords. Loading seed data...")
            return load_seed_reddit()
            
    except Exception as e:
        logger.error(f"Error scraping Reddit: {e}. Falling back to seed data.")
        return load_seed_reddit()
        
    return scraped_posts

def load_seed_reddit() -> list:
    """Loads fallback seed Reddit data from data/seed_reddit.json."""
    if SEED_REDDIT_PATH.exists():
        try:
            with open(SEED_REDDIT_PATH, 'r') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} high-fidelity Reddit complaints from seed file.")
                return data
        except Exception as e:
            logger.error(f"Error loading seed Reddit data: {e}")
    else:
        logger.warning(f"Seed Reddit file not found at {SEED_REDDIT_PATH}")
    return []

def scrape_all_and_save(play_limit=100, app_limit=100, reddit_limit=50):
    """Orchestrates all scrapers, merges with existing data, and saves to raw_reviews.json.

    IMPORTANT: This function MERGES new reviews with the existing corpus rather than
    overwriting it. Deduplication is performed by review `id` so repeat syncs never
    shrink the dataset.
    """
    newly_scraped = []

    # 1. Google Play Store
    play_data = scrape_google_play(play_limit)
    newly_scraped.extend(play_data)

    # 2. iOS App Store
    app_data = scrape_app_store(app_limit)
    newly_scraped.extend(app_data)

    # 3. Reddit
    reddit_data = scrape_reddit(reddit_limit)
    newly_scraped.extend(reddit_data)

    # ── Load existing corpus to merge into ──────────────────────────────────
    existing_data = []
    if RAW_DATA_PATH.exists():
        try:
            with open(RAW_DATA_PATH, 'r') as f:
                existing_data = json.load(f)
            logger.info(f"Loaded {len(existing_data)} existing reviews from {RAW_DATA_PATH}")
        except Exception as e:
            logger.warning(f"Could not load existing raw reviews (will start fresh): {e}")

    # ── Merge: existing first, then newly scraped ───────────────────────────
    all_data = existing_data + newly_scraped

    if not all_data:
        logger.warning("No reviews available from any source!")
        all_data = load_seed_reddit()

    # ── Deduplicate by review id (primary), then by cleaned text (secondary) ─
    df = pd.DataFrame(all_data)
    df = df.drop_duplicates(subset=["id"])
    df["text_clean"] = df["text"].str.strip().str.lower()
    df = df.drop_duplicates(subset=["text_clean"])
    df = df.drop(columns=["text_clean"])

    combined_data = df.to_dict(orient="records")

    # ── Save merged corpus ──────────────────────────────────────────────────
    with open(RAW_DATA_PATH, 'w') as f:
        json.dump(combined_data, f, indent=2)

    new_count = len(combined_data) - len(existing_data)
    logger.info(
        f"Sync complete. Corpus: {len(combined_data)} total unique reviews "
        f"(+{max(new_count, 0)} new) saved to {RAW_DATA_PATH}"
    )

    stats = df["source"].value_counts().to_dict()
    logger.info(f"Source distribution: {stats}")
    return combined_data

if __name__ == "__main__":
    scrape_all_and_save()
