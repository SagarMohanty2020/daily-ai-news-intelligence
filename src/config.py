"""
Configuration module for Daily AI-Powered News Analysis pipeline.
Defines categories, RSS feeds, environment variables, and operational thresholds.
"""
import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

# API Keys & Secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Execution settings - using standard gemini-1.5-flash
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
MAX_ARTICLES_PER_CATEGORY = int(os.getenv("MAX_ARTICLES_PER_CATEGORY", "3"))
EXTRACTION_TIMEOUT_SECONDS = int(os.getenv("EXTRACTION_TIMEOUT_SECONDS", "10"))
MAX_FULL_TEXT_CHARS = int(os.getenv("MAX_FULL_TEXT_CHARS", "6000"))

# Curated High-Authority News Feeds across Domains
NEWS_FEEDS: Dict[str, List[str]] = {
    "Financial & Markets": [
        "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "https://www.livemint.com/rss/markets",
        "https://www.moneycontrol.com/rss/latestnews.xml",
        "https://feeds.content.dowjones.io/public/rss/mw_topstories"
    ],
    "Technology & AI": [
        "https://techcrunch.com/feed/",
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://www.theverge.com/rss/index.xml",
        "https://news.ycombinator.com/rss"
    ],
    "Geopolitics & World": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-US&gl=US&ceid=US:en"
    ],
    "Pharma & Healthcare": [
        "https://www.fiercepharma.com/rss/xml",
        "https://www.biopharmadive.com/feeds/news/",
        "https://www.medicalnewstoday.com/feed"
    ],
    "Social & Governance": [
        "https://www.thehindu.com/news/national/feeder/default.rss",
        "https://indianexpress.com/section/india/feed/",
        "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZxYUdjU0FtVnVHZ0pWVXlnQVAB?hl=en-IN&gl=IN&ceid=IN:en"
    ]
}
