import argparse
import sys
import os
import subprocess
from pathlib import Path

# Add project root to path so we can import src modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from review_engine.src.scrapers import scrape_all_and_save
from review_engine.src.analyzer import run_classification, generate_synthesis_report

def main():
    parser = argparse.ArgumentParser(
        description="Spotify Review Discovery Engine CLI - Phase 1"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape reviews from app stores and Reddit")
    scrape_parser.add_argument("--play-limit", type=int, default=100, help="Max Google Play reviews to scrape")
    scrape_parser.add_argument("--app-limit", type=int, default=100, help="Max App Store reviews to scrape")
    scrape_parser.add_argument("--reddit-limit", type=int, default=50, help="Max Reddit posts to scrape")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze scraped reviews using LLM or rule-based heuristics")
    analyze_parser.add_argument("--sample", type=int, default=None, help="Limit analysis to a sample of reviews")
    
    # Dashboard command
    subparsers.add_parser("dashboard", help="Start the Streamlit visualization dashboard")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    if args.command == "scrape":
        print("🚀 Executing Scrapers (Play Store, App Store, Reddit)...")
        scrape_all_and_save(
            play_limit=args.play_limit,
            app_limit=args.app_limit,
            reddit_limit=args.reddit_limit
        )
        print("✅ Scraping complete.")
        
    elif args.command == "analyze":
        print("🧠 Running AI-Powered Sentiment and Thematic Analysis...")
        analyzed_reviews = run_classification(sample_limit=args.sample)
        if analyzed_reviews:
            generate_synthesis_report(analyzed_reviews)
            print("✅ Analysis and PM synthesis complete.")
        else:
            print("❌ Classification returned no results. Make sure you have raw scraped data first by running: python review_engine/run.py scrape")
            
    elif args.command == "dashboard":
        print("📊 Starting Streamlit Dashboard...")
        dashboard_path = Path(__file__).resolve().parent / "src" / "dashboard.py"
        
        # Detect if we are inside a virtual environment to call the correct python/streamlit binary
        venv_path = Path(__file__).resolve().parent.parent / ".venv"
        
        if os.name == "nt":
            streamlit_bin = venv_path / "Scripts" / "streamlit.exe"
        else:
            streamlit_bin = venv_path / "bin" / "streamlit"
            
        cmd = [str(streamlit_bin) if streamlit_bin.exists() else "streamlit", "run", str(dashboard_path)]
        
        try:
            subprocess.run(cmd, check=True)
        except KeyboardInterrupt:
            print("\n👋 Dashboard stopped.")
        except Exception as e:
            print(f"❌ Failed to run dashboard: {e}")
            print("Make sure your virtual environment is activated and requirements are installed.")

if __name__ == "__main__":
    main()
