from __future__ import annotations

from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AI Trading Agents API"
    APP_ENV: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ]

    REQUEST_TIMEOUT_SECONDS: float = 12.0
    NEWS_MAX_ARTICLES: int = 8
    ENABLE_LLM_EXPLANATIONS: bool = False

    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    MARKET_DATA_SOURCE: str = "auto"
    NEWS_DATA_SOURCE: str = "rss"

    KRAKEN_CLI_PATH: str = "kraken"
    KRAKEN_MODE: str = "paper"
    ENABLE_EXECUTION: bool = False
    DEFAULT_SYMBOL: str = "BTC-USD"
    DEFAULT_USD_SIZE: float = 10.0
    EXECUTION_CASH_FRACTION: float = 0.10
    RECEIPT_LOG_PATH: str = "backend/data/decision_receipts.jsonl"

    NEWS_FEEDS: List[str] = Field(
        default_factory=lambda: [
            "https://finance.yahoo.com/rss/headline?s={symbol}",
            "https://news.google.com/rss/search?q={query}",
            "https://www.investing.com/rss/news_25.rss",
            "https://cointelegraph.com/rss",
            "https://decrypt.co/feed",
        ]
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
