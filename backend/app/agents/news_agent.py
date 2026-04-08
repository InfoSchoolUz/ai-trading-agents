from __future__ import annotations

import os

from app.schemas.trade import NewsAnalysis, NewsItem
from app.services.llm_service import LLMService
from app.services.news_provider import NewsProvider


class NewsAgent:
    """Normalize live RSS headlines into a scored news signal."""

    def __init__(self) -> None:
        self.max_articles = int(os.getenv("NEWS_MAX_ARTICLES", "8"))
        self.provider = NewsProvider(max_articles=self.max_articles)
        self.llm = LLMService()

    def analyze(self, symbol: str = "BTC-USD") -> NewsAnalysis:
        articles = self.provider.fetch(symbol)
        sentiment = self.provider.summarize_sentiment(articles, symbol)

        llm_explanation = ""

        if articles:
            prompt = (
                f"You are a trading assistant.\n"
                f"Analyze the current news sentiment for {symbol} based only on the headlines below.\n"
                f"Write one short, clear paragraph in plain English.\n"
                f"Focus on trading bias, market mood, and likely short-term implication.\n"
                f"Do not use bullet points.\n\n"
            )

            for idx, article in enumerate(articles, start=1):
                title = article.get("title", "").strip()
                if title:
                    prompt += f"{idx}. {title}\n"

            if self.llm.is_available():
                explanation = self.llm.explain(prompt)
                llm_explanation = explanation.get("text", "").strip()

        summary = llm_explanation or sentiment.get("summary", "")

        return NewsAnalysis(
            sentiment_score=sentiment["sentiment_score"],
            sentiment_label=sentiment["sentiment_label"],
            summary=summary,
            catalysts=sentiment["catalysts"],
            article_count=sentiment["article_count"],
            articles=[NewsItem(**article) for article in sentiment["articles"]],
            source=sentiment["source"],
            llm_explanation=llm_explanation,
        )