import pytest
from src.collectors.feed_collector import RawArticle
from src.summarizers.llm_analyzer import AnalyzedArticle, LLMAnalyzer
from src.notifiers.telegram_sender import TelegramSender


def test_telegram_formatting():
    sender = TelegramSender(bot_token="test_token", chat_id="SM_DNA_Auto")
    
    mock_articles = {
        "Financial & Markets": [
            AnalyzedArticle(
                title="RBI Keeps Repo Rate Unchanged",
                source_url="https://example.com/rbi-rate",
                category="Financial & Markets",
                bullet_summary=[
                    "Monetary Policy Committee votes to maintain benchmark rate.",
                    "Inflation forecast retained with growth target at 7%."
                ],
                key_takeaway="Stability in lending rates expected across banking sector.",
                sentiment="Bullish",
                impact_level="High"
            )
        ]
    }
    
    chunks = sender.format_briefing(mock_articles)
    assert len(chunks) >= 1
    assert "SM_DNA_Auto" in chunks[0]
    assert "RBI Keeps Repo Rate Unchanged" in chunks[0]
    assert "Bullish" in chunks[0]


def test_llm_analyzer_fallback():
    analyzer = LLMAnalyzer(api_key="")  # No key triggers fallback mode
    articles = [{"title": "Sample News", "url": "https://example.com", "full_text": "Sample content"}]
    results = analyzer.analyze_category("Technology & AI", articles)
    
    assert len(results) == 1
    assert results[0].title == "Sample News"
    assert results[0].sentiment == "Neutral"
