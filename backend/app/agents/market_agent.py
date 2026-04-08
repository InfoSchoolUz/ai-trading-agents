from __future__ import annotations

from app.schemas.trade import MarketAnalysis
from app.services.data_provider import DataProvider


class MarketAgent:
    """Technical analysis agent with weighted scoring and explicit signals."""

    def analyze(self, symbol: str, period: str = "3mo", interval: str = "1d") -> MarketAnalysis:
        snap = DataProvider.fetch_market_data(symbol=symbol, period=period, interval=interval)

        score = 0
        signals: list[str] = []

        if snap.sma_5 > snap.sma_10:
            score += 2
            signals.append(f"Short-term crossover bullish: SMA5 {snap.sma_5} > SMA10 {snap.sma_10}")
        else:
            score -= 2
            signals.append(f"Short-term crossover bearish: SMA5 {snap.sma_5} < SMA10 {snap.sma_10}")

        if snap.current_price > snap.sma_20:
            score += 2
            signals.append(f"Price {snap.current_price} trades above SMA20 {snap.sma_20}")
        else:
            score -= 2
            signals.append(f"Price {snap.current_price} trades below SMA20 {snap.sma_20}")

        if snap.momentum_pct >= 2:
            score += 2
            signals.append(f"Momentum strong at +{snap.momentum_pct}% over the last 5 bars")
        elif snap.momentum_pct > 0:
            score += 1
            signals.append(f"Momentum mildly positive at +{snap.momentum_pct}%")
        elif snap.momentum_pct <= -2:
            score -= 2
            signals.append(f"Momentum weak at {snap.momentum_pct}% over the last 5 bars")
        else:
            score -= 1
            signals.append(f"Momentum mildly negative at {snap.momentum_pct}%")

        if snap.rsi_14 >= 70:
            score -= 1
            signals.append(f"RSI {snap.rsi_14} is overbought; upside may be crowded")
        elif snap.rsi_14 <= 30:
            score += 1
            signals.append(f"RSI {snap.rsi_14} is oversold; reversal odds improved")
        elif snap.rsi_14 >= 55:
            score += 1
            signals.append(f"RSI {snap.rsi_14} confirms bullish momentum")
        elif snap.rsi_14 <= 45:
            score -= 1
            signals.append(f"RSI {snap.rsi_14} confirms bearish momentum")
        else:
            signals.append(f"RSI {snap.rsi_14} is neutral")

        if snap.macd > snap.macd_signal:
            score += 1
            signals.append(f"MACD {snap.macd} is above signal {snap.macd_signal}")
        else:
            score -= 1
            signals.append(f"MACD {snap.macd} is below signal {snap.macd_signal}")

        if score >= 3:
            trend = "BULLISH"
        elif score <= -3:
            trend = "BEARISH"
        else:
            trend = "SIDEWAYS"

        summary = (
            f"{trend.title()} setup with score {score:+d}. "
            f"Volatility {snap.volatility_pct:.2f}% annualised, drawdown {snap.drawdown_pct:.2f}%, "
            f"support {snap.support_level}, resistance {snap.resistance_level}. "
            f"Source: {snap.source}."
        )

        return MarketAnalysis(
            symbol=snap.symbol,
            current_price=snap.current_price,
            sma_5=snap.sma_5,
            sma_10=snap.sma_10,
            sma_20=snap.sma_20,
            rsi_14=snap.rsi_14,
            macd=snap.macd,
            macd_signal=snap.macd_signal,
            momentum_pct=snap.momentum_pct,
            volatility_pct=snap.volatility_pct,
            drawdown_pct=snap.drawdown_pct,
            support_level=snap.support_level,
            resistance_level=snap.resistance_level,
            trend=trend,
            signal_score=score,
            summary=summary,
            signals=signals,
            prices=snap.close_prices,
            source=snap.source,
        )
