"""
Orchestrator Pipeline.
Coordinates Feed Collection -> Full-Text Extraction -> Gemini Analysis -> Telegram Dispatch.
"""
import logging
from typing import Dict, List
from src import config
from src.collectors.feed_collector import FeedCollector
from src.extractors.article_scraper import ArticleScraper
from src.summarizers.llm_analyzer import LLMAnalyzer, AnalyzedArticle
from src.notifiers.telegram_sender import TelegramSender

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("NewsIntelligencePipeline")


def run_pipeline() -> Dict[str, List[AnalyzedArticle]]:
    logger.info("=== Starting Daily AI News Intelligence Pipeline ===")

    # 1. Collect candidate feeds
    collector = FeedCollector(
        feeds=config.NEWS_FEEDS,
        max_per_cat=config.MAX_ARTICLES_PER_CATEGORY
    )
    raw_articles_by_cat = collector.collect()

    # 2. Extract full article text to prevent hallucination
    scraper = ArticleScraper(
        timeout=config.EXTRACTION_TIMEOUT_SECONDS,
        max_chars=config.MAX_FULL_TEXT_CHARS
    )
    
    extracted_by_cat = {}
    for cat, raw_list in raw_articles_by_cat.items():
        logger.info(f"Extracting full body text for category '{cat}' ({len(raw_list)} articles)...")
        extracted_by_cat[cat] = []
        for item in raw_list:
            full_text = scraper.fetch_full_text(item.url, fallback_snippet=item.summary_snippet)
            extracted_by_cat[cat].append({
                "title": item.title,
                "url": item.url,
                "full_text": full_text
            })

    # 3. LLM AI Analysis & Summarization
    analyzer = LLMAnalyzer(
        api_key=config.GEMINI_API_KEY,
        model_name=config.GEMINI_MODEL
    )
    
    all_analyzed: Dict[str, List[AnalyzedArticle]] = {}
    for cat, articles in extracted_by_cat.items():
        logger.info(f"Synthesizing & scoring with Gemini LLM for '{cat}'...")
        all_analyzed[cat] = analyzer.analyze_category(cat, articles)

    # 4. Dispatch to Telegram
    sender = TelegramSender(
        bot_token=config.TELEGRAM_BOT_TOKEN,
        chat_id=config.TELEGRAM_CHAT_ID
    )
    sender.send_briefing(all_analyzed)

    logger.info("=== Daily AI News Intelligence Pipeline Completed Successfully ===")
    return all_analyzed
