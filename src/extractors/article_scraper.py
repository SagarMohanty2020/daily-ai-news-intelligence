"""
Full-Text Article Extractor.
Fetches full web pages and extracts clean content using trafilatura and BeautifulSoup
to eliminate AI hallucination by providing ground truth context.
"""
import logging
import requests
import trafilatura
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"


class ArticleScraper:
    def __init__(self, timeout: int = 10, max_chars: int = 6000):
        self.timeout = timeout
        self.max_chars = max_chars
        self.headers = {"User-Agent": USER_AGENT}

    def fetch_full_text(self, url: str, fallback_snippet: str = "") -> str:
        """
        Fetches web page and extracts primary textual body.
        Falls back to BeautifulSoup or snippet if trafilatura extraction fails.
        """
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                extracted = trafilatura.extract(
                    downloaded,
                    include_comments=False,
                    include_tables=True,
                    no_fallback=False
                )
                if extracted and len(extracted.strip()) > 150:
                    return extracted.strip()[: self.max_chars]

            # Fallback with requests and BeautifulSoup
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    tag.decompose()
                paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 30]
                text = "\n\n".join(paragraphs)
                if len(text) > 150:
                    return text[: self.max_chars]

        except Exception as e:
            logger.warning(f"Failed to fetch full text from {url}: {e}")

        # Return snippet as last resort
        clean_fallback = BeautifulSoup(fallback_snippet, "html.parser").get_text().strip()
        return clean_fallback if clean_fallback else "Full text unavailable; relied on headline context."
