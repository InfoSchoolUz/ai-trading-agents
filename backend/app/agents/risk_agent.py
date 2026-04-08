from __future__ import annotations

from app.schemas.trade import MarketAnalysis, NewsAnalysis, RiskAnalysis


class RiskAgent:
    """Risk engine with dynamic scoring, flags, and sizing."""

    def analyze(self, market: MarketAnalysis, news: NewsAnalysis) -> RiskAnalysis:
        score = 20
        flags: list[str] = []

        if market.volatility_pct >= 45:
            score += 35
            flags.append(f"extreme volatility ({market.volatility_pct:.2f}% annualised)")
        elif market.volatility_pct >= 25:
            score += 20
            flags.append(f"elevated volatility ({market.volatility_pct:.2f}% annualised)")
        elif market.volatility_pct >= 15:
            score += 10
            flags.append(f"moderate volatility ({market.volatility_pct:.2f}% annualised)")

        if market.drawdown_pct >= 20:
            score += 20
            flags.append(f"deep drawdown ({market.drawdown_pct:.2f}%)")
        elif market.drawdown_pct >= 10:
            score += 10
            flags.append(f"recent drawdown pressure ({market.drawdown_pct:.2f}%)")

        if market.trend == "BEARISH":
            score += 15
            flags.append("bearish technical regime")
        elif market.trend == "SIDEWAYS":
            score += 5
            flags.append("choppy/sideways market")

        if market.rsi_14 >= 75:
            score += 10
            flags.append(f"RSI overbought ({market.rsi_14})")
        elif market.rsi_14 <= 25:
            score += 5
            flags.append(f"RSI oversold ({market.rsi_14}) — reversal risk still high")

        if news.sentiment_score <= -0.5:
            score += 15
            flags.append(f"strongly negative sentiment ({news.sentiment_score:+.2f})")
        elif news.sentiment_score < 0:
            score += 8
            flags.append(f"negative sentiment ({news.sentiment_score:+.2f})")
        elif news.sentiment_score > 0.4:
            score -= 5

        score = max(0, min(100, score))

        if score >= 65:
            risk_level = "HIGH"
            position_size = 4.0
            stop_loss = 2.0
            take_profit = 4.5
            max_dd = 6.0
        elif score >= 40:
            risk_level = "MEDIUM"
            position_size = 8.0
            stop_loss = 3.0
            take_profit = 6.0
            max_dd = 8.0
        else:
            risk_level = "LOW"
            position_size = 12.0
            stop_loss = 4.0
            take_profit = 8.0
            max_dd = 10.0

        summary = (
            f"{risk_level} risk with score {score}/100. "
            f"Use {position_size:.1f}% position size, stop-loss {stop_loss:.1f}%, take-profit {take_profit:.1f}%."
        )
        if flags:
            summary += " Main risk flags: " + ", ".join(flags[:4]) + "."

        return RiskAnalysis(
            risk_level=risk_level,
            risk_score=score,
            position_size_pct=position_size,
            stop_loss_pct=stop_loss,
            take_profit_pct=take_profit,
            max_drawdown_limit_pct=max_dd,
            summary=summary,
            flags=flags,
        )
