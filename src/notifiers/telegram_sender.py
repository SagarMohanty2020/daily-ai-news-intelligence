"""
Telegram Dispatcher.
Formats categorized news into clean HTML messages and posts to Telegram channel
with automatic message chunking (4096-character limit) and rate-limiting safeguards.
"""
import datetime
import logging
import time
from typing import Dict, List
import requests
from src.summarizers.llm_analyzer import AnalyzedArticle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CATEGORY_ICONS = {
    "Financial & Markets": "??",
    "Technology & AI": "??",
    "Geopolitics & World": "??",
    "Pharma & Healthcare": "??",
    "Social & Governance": "???"
}

SENTIMENT_ICONS = {
    "Bullish": "?? Bullish",
    "Bearish": "?? Bearish",
    "Neutral": "? Neutral",
    "Critical": "?? Critical"
}


class TelegramSender:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        # Telegram channel username requires leading @ if not an ID
        self.chat_id = f"@{chat_id}" if not chat_id.startswith(("@", "-")) and not chat_id.lstrip("-").isdigit() else chat_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def format_briefing(self, all_analyzed: Dict[str, List[AnalyzedArticle]]) -> List[str]:
        """
        Formats all analyzed articles into structured executive briefing messages (chunks < 4000 chars).
        """
        today_str = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p IST")
        
        messages = []
        header = (
            f"?? <b>SM_DNA_Auto | Daily AI News Intelligence</b>\n"
            f"?? <i>{today_str}</i>\n"
            f"?????????????????????\n\n"
        )
        
        current_chunk = header

        for category, articles in all_analyzed.items():
            if not articles:
                continue

            icon = CATEGORY_ICONS.get(category, "??")
            cat_block = f"<b>{icon} {category.upper()}</b>\n"

            for art in articles:
                sentiment_str = SENTIMENT_ICONS.get(art.sentiment, art.sentiment)
                bullet_points = "\n".join([f"  • {b}" for b in art.bullet_summary])
                
                art_block = (
                    f"\n?? <b><a href='{art.source_url}'>{art.title}</a></b>\n"
                    f"{bullet_points}\n"
                    f"?? <i>Takeaway:</i> {art.key_takeaway}\n"
                    f"?? <b>Sentiment:</b> {sentiment_str} | <b>Impact:</b> {art.impact_level}\n"
                )
                cat_block += art_block

            cat_block += "\n---------------------\n\n"

            # Check chunk size limit (Telegram max is 4096, target 3800 for safety)
            if len(current_chunk) + len(cat_block) > 3800:
                messages.append(current_chunk)
                current_chunk = cat_block
            else:
                current_chunk += cat_block

        if current_chunk.strip():
            messages.append(current_chunk)

        return messages

    def send_briefing(self, all_analyzed: Dict[str, List[AnalyzedArticle]]) -> bool:
        """Sends briefing chunks sequentially to Telegram."""
        if not self.bot_token:
            logger.error("? TELEGRAM_BOT_TOKEN secret is empty!")
            raise ValueError("TELEGRAM_BOT_TOKEN is missing in environment variables.")

        if not self.chat_id:
            logger.error("? TELEGRAM_CHAT_ID is empty!")
            raise ValueError("TELEGRAM_CHAT_ID is missing in environment variables.")

        chunks = self.format_briefing(all_analyzed)
        logger.info(f"Targeting Telegram Chat: {self.chat_id}")

        for idx, chunk in enumerate(chunks, 1):
            logger.info(f"Dispatching Telegram message chunk {idx}/{len(chunks)} to {self.chat_id}...")
            payload = {
                "chat_id": self.chat_id,
                "text": chunk,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }

            resp = requests.post(self.base_url, json=payload, timeout=15)
            if resp.status_code != 200:
                logger.error(f"? Telegram API Error: HTTP {resp.status_code} - {resp.text}")
                raise RuntimeError(f"Telegram dispatch failed: {resp.status_code} - {resp.text}")
            
            logger.info(f"? Chunk {idx} successfully posted to Telegram.")
            time.sleep(1)

        return True
