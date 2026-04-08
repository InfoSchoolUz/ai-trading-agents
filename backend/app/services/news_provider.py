from __future__ import annotations

import html
import logging
import re
from collections import Counter
from email.utils import parsedate_to_datetime
from typing import Any

import feedparser

from app.core.config import settings

logger = logging.getLogger(__name__)


class NewsProvider:
    """Public RSS-based provider with deterministic sentiment scoring."""

    POSITIVE_WORDS = {
        "surge", "rally", "gain", "growth", "bullish", "rise", "strong", "beats",
        "approval", "adoption", "expand", "record", "breakout", "upside", "rebound",
        "upgrade", "profit", "optimism", "boost", "recovery", "inflow",
    }
    NEGATIVE_WORDS = {
        "drop", "fall", "loss", "bearish", "weak", "down", "risk", "crash", "miss",
        "hack", "lawsuit", "ban", "outflow", "liquidation", "selloff", "fear",
        "downgrade", "fraud", "decline", "recession", "warning",
    }

    STOPWORDS = {
        "with", "from", "this", "that", "their", "after", "before", "about",
        "into", "over", "under", "while", "amid", "against", "crypto", "stock",
        "market", "markets", "price", "shares",
    }

    def __init__(self, max_articles: int = 8) -> None:
        self.max_articles = max_articles
        self.feed_templates = settings.NEWS_FEEDS

    @staticmethod
    def _symbol_to_query(symbol: str) -> str:
        normalized = symbol.upper().strip()

        aliases = {
            "BTC-USD": "Bitcoin BTC crypto",
            "ETH-USD": "Ethereum ETH crypto",
            "SOL-USD": "Solana SOL crypto",
            "XRP-USD": "XRP Ripple crypto",
            "ADA-USD": "Cardano ADA crypto",
            "DOGE-USD": "Dogecoin DOGE crypto",
            "LINK-USD": "Chainlink LINK crypto",
            "AVAX-USD": "Avalanche AVAX crypto",
            "LTC-USD": "Litecoin LTC crypto",
            "DOT-USD": "Polkadot DOT crypto",
            "AAPL": "Apple stock",
            "MSFT": "Microsoft stock",
            "NVDA": "NVIDIA stock",
            "GC=F": "Gold futures",
            "CL=F": "Crude oil futures",
            "EURUSD=X": "EUR USD forex",
        }
        if normalized in aliases:
            return aliases[normalized]

        base = normalized.replace("-USD", "").replace("USD", "").replace("=X", "").replace("=F", "")
        return base

    @staticmethod
    def _clean_text(value: str) -> str:
        text = html.unescape(value or "")
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def _normalize_published(entry: Any) -> str | None:
        raw = getattr(entry, "published", "") or getattr(entry, "updated", "")
        raw = str(raw).strip()
        if not raw:
            return None
        try:
            return parsedate_to_datetime(raw).isoformat()
        except Exception:
            return raw

    @staticmethod
    def _publisher_from_entry(entry: Any, fallback: str) -> str:
        source = getattr(entry, "source", None)
        if isinstance(source, dict):
            return str(source.get("title") or fallback)
        if hasattr(source, "get"):
            try:
                return str(source.get("title") or fallback)
            except Exception:
                pass
        if source:
            return str(source)
        return fallback

    def fetch(self, symbol: str) -> list[dict[str, Any]]:
        articles: list[dict[str, Any]] = []
        seen: set[str] = set()
        query = self._symbol_to_query(symbol)

        for raw_feed in self.feed_templates:
            feed_url = raw_feed.format(symbol=symbol, query=query.replace(" ", "+"))
            try:
                parsed = feedparser.parse(feed_url)
            except Exception as exc:
                logger.warning("Failed to parse RSS feed %s: %s", feed_url, exc)
                continue

            source_title = getattr(parsed.feed, "title", "RSS Feed") or "RSS Feed"

            for entry in parsed.entries:
                title = self._clean_text(getattr(entry, "title", ""))
                link = str(getattr(entry, "link", "")).strip()
                if not title or not link:
                    continue

                unique_key = f"{title}|{link}"
                if unique_key in seen:
                    continue
                seen.add(unique_key)

                summary = self._clean_text(getattr(entry, "summary", ""))
                article = {
                    "title": title,
                    "publisher": self._publisher_from_entry(entry, source_title),
                    "published_at": self._normalize_published(entry),
                    "link": link,
                    "summary": summary,
                }
                articles.append(article)

                if len(articles) >= self.max_articles:
                    return articles

        return articles

    def summarize_sentiment(self, articles: list[dict[str, Any]], symbol: str) -> dict[str, Any]:
        token_counter: Counter[str] = Counter()
        article_scores: list[float] = []

        for article in articles:
            text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
            tokens = re.findall(r"[a-zA-Z]{3,}", text)
            token_counter.update(tokens)

            pos_hits = sum(1 for token in tokens if token in self.POSITIVE_WORDS)
            neg_hits = sum(1 for token in tokens if token in self.NEGATIVE_WORDS)
            total_hits = pos_hits + neg_hits

            score = 0.0 if total_hits == 0 else (pos_hits - neg_hits) / total_hits
            score = max(-1.0, min(1.0, score))

            article["sentiment_score"] = round(score, 2)
            article_scores.append(score)

        sentiment_score = round(sum(article_scores) / len(article_scores), 2) if article_scores else 0.0

        if sentiment_score >= 0.2:
            sentiment_label = "Positive"
        elif sentiment_score <= -0.2:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Neutral"

        catalysts = [
            token.title()
            for token, _ in token_counter.most_common(20)
            if token not in self.STOPWORDS
        ][:4]

        summary = (
            f"{sentiment_label} headline flow from {len(articles)} live articles for {symbol}. "
            f"Average sentiment score {sentiment_score:+.2f}."
        )
        if catalysts:
            summary += f" Main catalysts: {', '.join(catalysts)}."

        return {
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label,
            "summary": summary,
            "catalysts": catalysts,
            "article_count": len(articles),
            "articles": articles,
            "source": "public_rss",
        }
