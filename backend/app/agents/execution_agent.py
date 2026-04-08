from __future__ import annotations

from app.schemas.trade import ExecutionDecision, MarketAnalysis, NewsAnalysis, RiskAnalysis


class ExecutionAgent:
    """Convert market, news, and risk signals into a concrete trade decision."""

    def decide(
        self,
        market: MarketAnalysis,
        news: NewsAnalysis,
        risk: RiskAnalysis,
    ) -> ExecutionDecision:
        confidence = 50.0
        thesis: list[str] = []
        warnings: list[str] = []

        if market.trend == "BULLISH":
            confidence += 20
            thesis.append("Technical regime is bullish.")
        elif market.trend == "BEARISH":
            confidence -= 20
            warnings.append("Technical regime is bearish.")
        else:
            warnings.append("Market structure is sideways; edge is weaker.")

        confidence += max(-10.0, min(10.0, market.signal_score * 2.0))
        if market.signal_score >= 3:
            thesis.append(f"Signal stack is strong at {market.signal_score:+d}.")
        elif market.signal_score <= -3:
            warnings.append(f"Signal stack is weak at {market.signal_score:+d}.")

        if news.sentiment_score >= 0.25:
            confidence += 10
            thesis.append(f"News sentiment is supportive at {news.sentiment_score:+.2f}.")
        elif news.sentiment_score <= -0.25:
            confidence -= 10
            warnings.append(f"News sentiment is adverse at {news.sentiment_score:+.2f}.")

        if risk.risk_level == "HIGH":
            confidence -= 15
            warnings.append("Risk engine marked the setup as HIGH risk.")
        elif risk.risk_level == "LOW":
            confidence += 5
            thesis.append("Risk engine marked the setup as LOW risk.")

        if market.rsi_14 >= 70:
            confidence -= 10
            warnings.append(f"RSI {market.rsi_14:.2f} is overbought.")
        elif market.rsi_14 <= 30:
            confidence += 10
            thesis.append(f"RSI {market.rsi_14:.2f} is oversold.")

        if market.macd > market.macd_signal:
            confidence += 5
            thesis.append("MACD is above its signal line.")
        else:
            confidence -= 5
            warnings.append("MACD is below its signal line.")

        if market.current_price >= market.resistance_level * 0.995:
            warnings.append("Price is trading close to resistance.")
        if market.current_price <= market.support_level * 1.005:
            thesis.append("Price is trading near support.")

        confidence = max(0.0, min(100.0, confidence))

        if confidence >= 65:
            action = "BUY"
        elif confidence <= 35:
            action = "SELL"
        else:
            action = "HOLD"
            warnings.append("Signal mix is not strong enough for execution.")

        explanation = (
            f"Action {action} with {confidence:.1f}% confidence. "
            f"Trend={market.trend}, sentiment={news.sentiment_label}, risk={risk.risk_level}."
        )

        return ExecutionDecision(
            action=action,
            confidence=round(confidence, 2),
            explanation=explanation,
            entry_price=market.current_price,
            thesis=thesis,
            warnings=warnings,
            strategy_name="multi_factor_kraken_strategy",
        )
