"""
News Feed Collector.
Parses multi-category RSS & Google News feeds with deduplication.
"""
import logging
from typing import Dict, List
import feedparser
from pydantic import BaseModel, HttpUrl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RawArticle(BaseModel):
    title: str
    url: str
    category: str
    published: str = ""
    summary_snippet: str = ""


class FeedCollector:
    def __init__(self, feeds: Dict[str, List[str]], max_per_cat: int = 3):
        self.feeds = feeds
        self.max_per_cat = max_per_cat

    def collect(self) -> Dict[str, List[RawArticle]]:
        """Collects raw article links per category."""
        collected: Dict[str, List[RawArticle]] = {}
        seen_urls = set()

        for category, feed_urls in self.feeds.items():
            collected[category] = []
            logger.info(f"Scanning feeds for category: {category}")

            for feed_url in feed_urls:
                if len(collected[category]) >= self.max_per_cat:
                    break

                try:
                    parsed = feedparser.parse(feed_url)
                    for entry in parsed.entries:
                        link = getattr(entry, "link", "")
                        title = getattr(entry, "title", "")
                        if not link or not title:
                            continue

                        # Clean & deduplicate URL
                        clean_url = link.split("?")[0].strip()
                        if clean_url in seen_urls:
                            continue

                        seen_urls.add(clean_url)
                        published = getattr(entry, "published", getattr(entry, "updated", ""))
                        summary = getattr(entry, "summary", "")

                        collected[category].append(
                            RawArticle(
                                title=title.strip(),
                                url=link.strip(),
                                category=category,
                                published=published,
                                summary_snippet=summary.strip()
                            )
                        )

                        if len(collected[category]) >= self.max_per_cat:
                            break
                except Exception as e:
                    logger.warning(f"Error parsing feed {feed_url}: {e}")

            logger.info(f"Retrieved {len(collected[category])} candidate articles for '{category}'.")

        return collected
