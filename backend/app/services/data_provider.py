from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Any, Iterable

import pandas as pd
import yfinance as yf

from app.services.kraken_service import KrakenService


@dataclass
class MarketSnapshot:
    symbol: str
    current_price: float
    sma_5: float
    sma_10: float
    sma_20: float
    rsi_14: float
    macd: float
    macd_signal: float
    momentum_pct: float
    volatility_pct: float
    drawdown_pct: float
    support_level: float
    resistance_level: float
    close_prices: list[float]
    source: str


class DataProvider:
    @staticmethod
    def _calc_rsi(series: pd.Series, period: int = 14) -> float:
        if len(series) < period + 1:
            return 50.0
        delta = series.diff()
        gain = delta.clip(lower=0).rolling(period).mean()
        loss = (-delta.clip(upper=0)).rolling(period).mean()
        rs = gain / loss.replace(0, pd.NA)
        rsi = 100 - (100 / (1 + rs))
        val = rsi.iloc[-1]
        return round(float(val), 2) if pd.notna(val) else 50.0

    @staticmethod
    def _calc_macd(series: pd.Series) -> tuple[float, float]:
        ema12 = series.ewm(span=12, adjust=False).mean()
        ema26 = series.ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        return round(float(macd_line.iloc[-1]), 4), round(float(signal_line.iloc[-1]), 4)

    @staticmethod
    def _build_snapshot(symbol: str, close_series: pd.Series, source: str) -> MarketSnapshot:
        close_series = pd.to_numeric(close_series, errors="coerce").dropna()
        if len(close_series) < 20:
            raise ValueError(f"Not enough data to analyse {symbol}. Need at least 20 rows, got {len(close_series)}.")

        current_price = round(float(close_series.iloc[-1]), 2)
        sma_5 = round(float(close_series.tail(5).mean()), 2)
        sma_10 = round(float(close_series.tail(10).mean()), 2)
        sma_20 = round(float(close_series.tail(20).mean()), 2)

        base_idx = -6 if len(close_series) >= 6 else -2
        ref_price = float(close_series.iloc[base_idx])
        momentum_pct = round(((current_price - ref_price) / ref_price) * 100, 2) if ref_price else 0.0

        returns = close_series.pct_change().dropna()
        volatility_pct = round(float(returns.std() * math.sqrt(252) * 100), 2) if not returns.empty else 0.0

        rolling_max = close_series.cummax()
        drawdown_series = (close_series / rolling_max - 1.0) * 100
        drawdown_pct = round(abs(float(drawdown_series.min())), 2)

        recent_window = close_series.tail(min(20, len(close_series)))
        support_level = round(float(recent_window.min()), 2)
        resistance_level = round(float(recent_window.max()), 2)

        rsi_14 = DataProvider._calc_rsi(close_series)
        macd, macd_signal = DataProvider._calc_macd(close_series)
        close_prices = [round(float(x), 2) for x in close_series.tail(60).tolist()]

        return MarketSnapshot(
            symbol=symbol.upper(),
            current_price=current_price,
            sma_5=sma_5,
            sma_10=sma_10,
            sma_20=sma_20,
            rsi_14=rsi_14,
            macd=macd,
            macd_signal=macd_signal,
            momentum_pct=momentum_pct,
            volatility_pct=volatility_pct,
            drawdown_pct=drawdown_pct,
            support_level=support_level,
            resistance_level=resistance_level,
            close_prices=close_prices,
            source=source,
        )

    @staticmethod
    def _extract_numeric(value: Any) -> float | None:
        try:
            if value is None or value == "":
                return None
            return float(value)
        except Exception:
            return None

    @staticmethod
    def _walk(obj: Any) -> Iterable[Any]:
        if isinstance(obj, dict):
            for value in obj.values():
                yield value
                yield from DataProvider._walk(value)
        elif isinstance(obj, list):
            for value in obj:
                yield value
                yield from DataProvider._walk(value)

    @staticmethod
    def _extract_close_series_from_kraken(payload: Any) -> list[float]:
        candidates: list[list[float]] = []

        for node in DataProvider._walk(payload):
            if isinstance(node, list) and node:
                closes: list[float] = []
                for row in node:
                    close_val: float | None = None
                    if isinstance(row, (list, tuple)) and len(row) >= 5:
                        close_val = DataProvider._extract_numeric(row[4])
                    elif isinstance(row, dict):
                        for key in ("close", "c", "last", "price"):
                            close_val = DataProvider._extract_numeric(row.get(key))
                            if close_val is not None:
                                break

                    if close_val is not None:
                        closes.append(close_val)

                if len(closes) >= 20:
                    candidates.append(closes)

        if not candidates:
            raise ValueError("Kraken CLI OHLC output did not contain enough close prices.")

        return max(candidates, key=len)

    @staticmethod
    def _fetch_market_data_from_kraken(symbol: str) -> MarketSnapshot:
        payload = KrakenService.ohlc(symbol, interval_minutes=1440)
        closes = DataProvider._extract_close_series_from_kraken(payload)
        close_series = pd.Series(closes[-180:])
        return DataProvider._build_snapshot(symbol, close_series, source="kraken_cli")

    @staticmethod
    def _fetch_market_data_from_yfinance(symbol: str, period: str = "3mo", interval: str = "1d") -> MarketSnapshot:
        try:
            df = yf.download(
                tickers=symbol,
                period=period,
                interval=interval,
                auto_adjust=True,
                progress=False,
                group_by="column",
                threads=False,
            )
        except Exception as exc:
            raise ValueError(f"Failed to download market data for {symbol}: {exc}") from exc

        if df is None or df.empty:
            raise ValueError(f"No market data returned for symbol: {symbol}")
        if "Close" not in df.columns:
            raise ValueError(f"'Close' column not found for symbol: {symbol}")

        close_data = df["Close"]
        close_series = close_data.iloc[:, 0] if isinstance(close_data, pd.DataFrame) else close_data
        return DataProvider._build_snapshot(symbol, close_series, source="yfinance")

    @staticmethod
    def fetch_market_data(symbol: str, period: str = "3mo", interval: str = "1d") -> MarketSnapshot:
        preferred_source = (os.getenv("MARKET_DATA_SOURCE", "auto") or "auto").lower()

        if preferred_source in {"auto", "kraken_cli"} and KrakenService.is_available():
            try:
                return DataProvider._fetch_market_data_from_kraken(symbol)
            except Exception:
                if preferred_source == "kraken_cli":
                    raise

        return DataProvider._fetch_market_data_from_yfinance(symbol=symbol, period=period, interval=interval)
