"""
LLM News Analyzer.
Uses Google Gemini (google-genai SDK) for zero-hallucination, structured synthesis,
sentiment assessment, and impact scoring based strictly on full extracted text.
"""
import json
import logging
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyzedArticle(BaseModel):
    title: str
    source_url: str
    category: str
    bullet_summary: List[str] = Field(description="2-3 crisp bullet points summarizing key facts.")
    key_takeaway: str = Field(description="One-sentence strategic/financial takeaway.")
    sentiment: str = Field(description="Bullish / Bearish / Neutral / Critical")
    impact_level: str = Field(description="High / Medium / Low")


class LLMAnalyzer:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = genai.Client(api_key=api_key) if api_key else None

    def analyze_category(
        self, category: str, articles_with_text: List[Dict[str, str]]
    ) -> List[AnalyzedArticle]:
        """
        Analyzes a batch of full-text articles for a category using structured schema output.
        """
        if not self.client:
            logger.warning("No GEMINI_API_KEY provided. Generating fallback mock analysis.")
            return self._generate_fallback(category, articles_with_text)

        if not articles_with_text:
            return []

        prompt_payload = []
        for idx, art in enumerate(articles_with_text, 1):
            prompt_payload.append(
                f"### Article {idx}:\n"
                f"Title: {art['title']}\n"
                f"URL: {art['url']}\n"
                f"Full Extracted Content:\n{art['full_text']}\n"
            )

        combined_input = "\n\n".join(prompt_payload)

        system_instruction = (
            "You are a Senior Intelligence & Financial Analyst for an executive daily news briefing. "
            "Analyze the provided articles strictly using ONLY the provided text to eliminate any hallucinations. "
            "Do not invent facts, quotes, or numbers. "
            "For each article, generate:\n"
            "- 2 to 3 crisp, informative bullet points summarizing the core event\n"
            "- One sharp key takeaway\n"
            "- Sentiment (Bullish, Bearish, Neutral, or Critical)\n"
            "- Impact level (High, Medium, Low)\n"
            "Respond strictly according to the structured JSON schema."
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=f"Category: {category}\n\nArticles:\n{combined_input}",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=list[AnalyzedArticle],
                    temperature=0.2,
                ),
            )
            
            if response.text:
                results_data = json.loads(response.text)
                return [AnalyzedArticle(**item) for item in results_data]

        except Exception as e:
            logger.error(f"Error during Gemini LLM analysis for {category}: {e}")

        return self._generate_fallback(category, articles_with_text)

    def _generate_fallback(
        self, category: str, articles_with_text: List[Dict[str, str]]
    ) -> List[AnalyzedArticle]:
        results = []
        for art in articles_with_text:
            results.append(
                AnalyzedArticle(
                    title=art["title"],
                    source_url=art["url"],
                    category=category,
                    bullet_summary=[
                        f"Reported event: {art['title']}",
                        f"Details extracted from {art['url'][:40]}..."
                    ],
                    key_takeaway="Automated baseline digest (LLM API key not configured).",
                    sentiment="Neutral",
                    impact_level="Medium"
                )
            )
        return results
