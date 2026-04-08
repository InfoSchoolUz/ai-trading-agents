from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any

from app.agents.market_agent import MarketAgent
from app.agents.news_agent import NewsAgent
from app.agents.risk_agent import RiskAgent
from app.core.config import settings
from app.schemas.trade import (
    DataSourceStatus,
    DecisionReceipt,
    ExecutionDecision,
    KrakenTradeResult,
    NewsAnalysis,
    OrchestratorResponse,
    PortfolioSummary,
    RiskAnalysis,
    TradeRecord,
)
from app.services.kraken_service import KrakenService
from app.services.receipt_store import ReceiptStore

STARTING_CASH = 10_000.0


class TradingBrain:
    def __init__(self) -> None:
        self.market_agent = MarketAgent()
        self.news_agent = NewsAgent()
        self.risk_agent = RiskAgent()
        self.kraken = KrakenService()

    def _build_real_data_scenario(
        self,
        prices: list[float],
        final_action: str,
        position_size_pct: float,
    ) -> tuple[PortfolioSummary, list[TradeRecord]]:
        if not prices:
            return PortfolioSummary(
                starting_cash=STARTING_CASH,
                ending_cash=STARTING_CASH,
                asset_units=0.0,
                ending_portfolio_value=STARTING_CASH,
                pnl_value=0.0,
                pnl_pct=0.0,
                max_drawdown_pct=0.0,
            ), []

        first_price = float(prices[0])
        last_price = float(prices[-1])
        invest_fraction = max(0.0, min(1.0, position_size_pct / 100.0))

        if final_action != "BUY":
            summary = PortfolioSummary(
                starting_cash=STARTING_CASH,
                ending_cash=STARTING_CASH,
                asset_units=0.0,
                ending_portfolio_value=STARTING_CASH,
                pnl_value=0.0,
                pnl_pct=0.0,
                max_drawdown_pct=0.0,
            )
            history = [
                TradeRecord(
                    step=1,
                    action="HOLD",
                    price=round(last_price, 2),
                    units=0.0,
                    cash_after=STARTING_CASH,
                    asset_units_after=0.0,
                    portfolio_value_after=STARTING_CASH,
                )
            ]
            return summary, history

        allocated_cash = STARTING_CASH * invest_fraction
        reserve_cash = STARTING_CASH - allocated_cash
        asset_units = allocated_cash / first_price if first_price > 0 else 0.0

        peak_value = STARTING_CASH
        max_drawdown_pct = 0.0
        history: list[TradeRecord] = []

        for idx, price in enumerate(prices, start=1):
            portfolio_value = reserve_cash + asset_units * float(price)
            peak_value = max(peak_value, portfolio_value)
            drawdown = ((peak_value - portfolio_value) / peak_value) * 100 if peak_value else 0.0
            max_drawdown_pct = max(max_drawdown_pct, drawdown)

            action = "BUY" if idx == 1 else "HOLD"
            units = round(asset_units, 6) if idx == 1 else 0.0

            history.append(
                TradeRecord(
                    step=idx,
                    action=action,
                    price=round(float(price), 2),
                    units=units,
                    cash_after=round(reserve_cash, 2),
                    asset_units_after=round(asset_units, 6),
                    portfolio_value_after=round(portfolio_value, 2),
                )
            )

        ending_portfolio_value = reserve_cash + asset_units * last_price
        pnl_value = ending_portfolio_value - STARTING_CASH
        pnl_pct = (pnl_value / STARTING_CASH) * 100 if STARTING_CASH else 0.0

        summary = PortfolioSummary(
            starting_cash=STARTING_CASH,
            ending_cash=round(reserve_cash, 2),
            asset_units=round(asset_units, 6),
            ending_portfolio_value=round(ending_portfolio_value, 2),
            pnl_value=round(pnl_value, 2),
            pnl_pct=round(pnl_pct, 2),
            max_drawdown_pct=round(max_drawdown_pct, 2),
        )
        return summary, history

    def _decide_execution(self, market: Any, news: NewsAnalysis, risk: RiskAnalysis) -> ExecutionDecision:
        thesis: list[str] = []
        warnings: list[str] = []
        score = market.signal_score
        confidence = 50.0

        if market.trend == "BULLISH":
            thesis.append("Trend regime is bullish.")
            confidence += 10
        elif market.trend == "BEARISH":
            warnings.append("Trend regime is bearish.")
            confidence -= 10
        else:
            warnings.append("Market is sideways; edge is weaker.")
            confidence -= 5

        if market.momentum_pct > 0:
            thesis.append(f"Momentum remains positive at {market.momentum_pct:+.2f}%.")
            confidence += min(8.0, abs(market.momentum_pct))
        else:
            warnings.append(f"Momentum is negative at {market.momentum_pct:+.2f}%.")
            confidence -= min(8.0, abs(market.momentum_pct))

        if news.sentiment_score > 0.20:
            thesis.append(f"News sentiment is supportive at {news.sentiment_score:+.2f}.")
            confidence += 6
        elif news.sentiment_score < -0.20:
            warnings.append(f"News sentiment is adverse at {news.sentiment_score:+.2f}.")
            confidence -= 6
        else:
            warnings.append("News sentiment is mixed.")

        if risk.risk_level == "HIGH":
            warnings.append("Risk engine marked this setup HIGH risk.")
            confidence -= 18
        elif risk.risk_level == "MEDIUM":
            warnings.append("Risk engine marked this setup MEDIUM risk.")
            confidence -= 8
        else:
            thesis.append("Risk engine allows relatively larger sizing.")
            confidence += 5

        if score >= 3 and news.sentiment_score >= -0.15 and risk.risk_score < 70:
            action = "BUY"
        elif score <= -3 or (news.sentiment_score < -0.45 and risk.risk_score >= 65):
            action = "SELL"
        else:
            action = "HOLD"

        if action == "HOLD":
            confidence = min(confidence, 62.0)
        elif action == "SELL":
            thesis.append("Capital protection takes priority over chasing upside.")
        else:
            thesis.append("Technical and sentiment stack is strong enough for a long entry.")

        confidence = max(5.0, min(95.0, round(confidence, 1)))
        explanation = (
            f"Decision={action}. score={score:+d}, trend={market.trend}, "
            f"sentiment={news.sentiment_score:+.2f}, risk={risk.risk_score}/100."
        )

        return ExecutionDecision(
            action=action,
            confidence=confidence,
            explanation=explanation,
            entry_price=market.current_price,
            thesis=thesis[:5],
            warnings=warnings[:5],
        )

    def _build_trustless_receipt(
        self,
        *,
        symbol: str,
        decision: ExecutionDecision,
        risk: RiskAnalysis,
        market: Any,
        news: NewsAnalysis,
        mode: str,
        volume: float,
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        chain_id = int(os.getenv("CHAIN_ID", "11155111"))
        operator = os.getenv("AGENT_OPERATOR", "local-operator")
        agent_wallet = os.getenv("AGENT_WALLET", "0xLOCAL_SIMULATED_AGENT")
        pair = KrakenService.normalize_pair(symbol)

        typed_intent = {
            "types": {
                "TradeIntent": [
                    {"name": "symbol", "type": "string"},
                    {"name": "pair", "type": "string"},
                    {"name": "action", "type": "string"},
                    {"name": "volume", "type": "string"},
                    {"name": "entryPrice", "type": "string"},
                    {"name": "riskScore", "type": "uint256"},
                    {"name": "timestamp", "type": "string"},
                    {"name": "mode", "type": "string"},
                ]
            },
            "domain": {
                "name": "AITradingAgent",
                "version": "1",
                "chainId": chain_id,
            },
            "primaryType": "TradeIntent",
            "message": {
                "symbol": symbol,
                "pair": pair,
                "action": decision.action,
                "volume": f"{volume:.6f}",
                "entryPrice": f"{market.current_price:.2f}",
                "riskScore": risk.risk_score,
                "timestamp": now,
                "mode": mode,
            },
        }

        raw_checkpoint = {
            "standard": "erc8004-inspired-checkpoint",
            "agentIdentity": {
                "operator": operator,
                "agentWallet": agent_wallet,
                "capabilities": ["analysis", "trading", "kraken-cli", "checkpointing"],
            },
            "tradeIntent": typed_intent,
            "evidence": {
                "marketTrend": market.trend,
                "signalScore": market.signal_score,
                "sentimentScore": news.sentiment_score,
                "riskLevel": risk.risk_level,
                "riskScore": risk.risk_score,
            },
            "createdAt": now,
        }

        payload = json.dumps(raw_checkpoint, sort_keys=True).encode("utf-8")
        raw_checkpoint["checkpointHash"] = hashlib.sha256(payload).hexdigest()
        raw_checkpoint["signature"] = (
            "simulated:"
            + hashlib.sha256((raw_checkpoint["checkpointHash"] + agent_wallet).encode("utf-8")).hexdigest()
        )
        return raw_checkpoint

    def _build_decision_receipt(
        self,
        *,
        symbol: str,
        period: str,
        interval: str,
        market: Any,
        news: NewsAnalysis,
        risk: RiskAnalysis,
        decision: ExecutionDecision,
        kraken_trade: KrakenTradeResult,
    ) -> DecisionReceipt:
        created_at = datetime.now(timezone.utc).isoformat()

        inputs_payload = {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "market_price": market.current_price,
            "market_trend": market.trend,
            "market_score": market.signal_score,
            "news_score": news.sentiment_score,
            "risk_score": risk.risk_score,
            "risk_level": risk.risk_level,
        }
        decision_payload = {
            "action": decision.action,
            "confidence": decision.confidence,
            "entry_price": decision.entry_price,
            "execution_mode": kraken_trade.mode,
            "executed": kraken_trade.executed,
            "volume": kraken_trade.volume,
            "note": kraken_trade.note,
            "error": kraken_trade.error,
        }

        inputs_checksum = hashlib.sha256(
            json.dumps(inputs_payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        decision_checksum = hashlib.sha256(
            json.dumps(decision_payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()

        receipt_id = hashlib.sha256(
            f"{created_at}|{symbol}|{decision_checksum}".encode("utf-8")
        ).hexdigest()[:20]

        store_payload = {
            "receipt_id": receipt_id,
            "created_at": created_at,
            "strategy_name": decision.strategy_name,
            "market_source": market.source,
            "news_source": news.source,
            "execution_mode": kraken_trade.mode,
            "inputs_checksum": inputs_checksum,
            "decision_checksum": decision_checksum,
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "decision": decision.model_dump(),
            "risk": risk.model_dump(),
            "kraken_trade": kraken_trade.model_dump(),
        }
        storage_path = ReceiptStore.save(store_payload)

        return DecisionReceipt(
            receipt_id=receipt_id,
            created_at=created_at,
            strategy_name=decision.strategy_name,
            market_source=market.source,
            news_source=news.source,
            execution_mode=kraken_trade.mode,
            inputs_checksum=inputs_checksum,
            decision_checksum=decision_checksum,
            storage_path=storage_path,
        )

    def _execute_trade(
        self,
        *,
        symbol: str,
        decision: ExecutionDecision,
        risk: RiskAnalysis,
        market: Any,
        news: NewsAnalysis,
    ) -> dict[str, Any]:
        mode = settings.KRAKEN_MODE.lower()
        action = decision.action

        if action == "HOLD":
            receipt = self._build_trustless_receipt(
                symbol=symbol,
                decision=decision,
                risk=risk,
                market=market,
                news=news,
                mode=mode,
                volume=0.0,
            )
            return {
                "executed": False,
                "mode": mode,
                "action": action,
                "symbol": symbol,
                "volume": 0.0,
                "order_result": {"trustless_receipt": receipt},
                "status": None,
                "error": None,
                "note": "No order was placed because the decision was HOLD.",
            }

        if not settings.ENABLE_EXECUTION:
            return {
                "executed": False,
                "mode": mode,
                "action": action,
                "symbol": symbol,
                "volume": 0.0,
                "order_result": None,
                "status": None,
                "error": "Execution disabled in settings",
                "note": "Execution disabled by configuration.",
            }

        if not self.kraken.is_available():
            return {
                "executed": False,
                "mode": mode,
                "action": action,
                "symbol": symbol,
                "volume": 0.0,
                "order_result": None,
                "status": None,
                "error": "Kraken CLI not found on PATH",
                "note": "Install Kraken CLI and make sure the binary is available on PATH.",
            }

        volume = self.kraken.volume_from_cash(
            cash=STARTING_CASH,
            price=decision.entry_price or market.current_price,
            fraction=max(0.01, min(1.0, settings.EXECUTION_CASH_FRACTION)),
        )
        if volume <= 0:
            return {
                "executed": False,
                "mode": mode,
                "action": action,
                "symbol": symbol,
                "volume": 0.0,
                "order_result": None,
                "status": None,
                "error": "Unable to derive order volume from current price",
                "note": "Execution skipped because order size could not be calculated.",
            }

        receipt = self._build_trustless_receipt(
            symbol=symbol,
            decision=decision,
            risk=risk,
            market=market,
            news=news,
            mode=mode,
            volume=volume,
        )

        try:
            if mode == "live":
                if not self.kraken.has_live_credentials():
                    return {
                        "executed": False,
                        "mode": mode,
                        "action": action,
                        "symbol": symbol,
                        "volume": volume,
                        "order_result": {"trustless_receipt": receipt},
                        "status": None,
                        "error": "Missing KRAKEN_API_KEY/KRAKEN_API_SECRET for live mode",
                        "note": "Live mode selected, but credentials are missing.",
                    }

                order_result = (
                    self.kraken.live_buy(symbol, volume, order_type="market")
                    if action == "BUY"
                    else self.kraken.live_sell(symbol, volume, order_type="market")
                )
                status = {
                    "balance": self.kraken.balance(),
                    "open_orders": self.kraken.open_orders(),
                }
                note = "Trade executed through Kraken CLI live mode."
            else:
                order_result = (
                    self.kraken.paper_buy(symbol, volume)
                    if action == "BUY"
                    else self.kraken.paper_sell(symbol, volume)
                )
                status = self.kraken.paper_status()
                note = "Trade executed through Kraken CLI paper mode."

            if isinstance(order_result, dict):
                order_result.setdefault("trustless_receipt", receipt)

            return {
                "executed": True,
                "mode": mode,
                "action": action,
                "symbol": symbol,
                "volume": volume,
                "order_result": order_result,
                "status": status,
                "error": None,
                "note": note,
            }
        except Exception as exc:
            return {
                "executed": False,
                "mode": mode,
                "action": action,
                "symbol": symbol,
                "volume": volume,
                "order_result": {"trustless_receipt": receipt},
                "status": None,
                "error": str(exc),
                "note": f"Kraken CLI {mode} order failed.",
            }

    def run(self, symbol: str, period: str = "3mo", interval: str = "1d") -> OrchestratorResponse:
        symbol = symbol.strip().upper()

        market = self.market_agent.analyze(symbol=symbol, period=period, interval=interval)
        news = self.news_agent.analyze(symbol)
        risk = self.risk_agent.analyze(market=market, news=news)
        decision = self._decide_execution(market=market, news=news, risk=risk)

        portfolio, trade_history = self._build_real_data_scenario(
            prices=market.prices,
            final_action=decision.action,
            position_size_pct=risk.position_size_pct,
        )

        kraken_raw = self._execute_trade(
            symbol=symbol,
            decision=decision,
            risk=risk,
            market=market,
            news=news,
        )
        kraken_trade = KrakenTradeResult(**kraken_raw)

        order_result = kraken_raw.get("order_result") or {}
        trustless_receipt = order_result.get("trustless_receipt") if isinstance(order_result, dict) else None
        checkpoint_hash = trustless_receipt.get("checkpointHash") if isinstance(trustless_receipt, dict) else "n/a"

        execution_label = f"kraken_cli_{kraken_trade.mode}" if settings.ENABLE_EXECUTION else "disabled"
        live_trade_execution = kraken_trade.mode == "live" and kraken_trade.executed

        receipt = self._build_decision_receipt(
            symbol=symbol,
            period=period,
            interval=interval,
            market=market,
            news=news,
            risk=risk,
            decision=decision,
            kraken_trade=kraken_trade,
        )

        reasoning_steps = [
            f"MarketAgent scored {market.signal_score:+d}: {market.summary}",
            f"Top technical signals: {' | '.join(market.signals[:3])}",
            f"NewsAgent processed {news.article_count} live headlines; sentiment {news.sentiment_label} ({news.sentiment_score:+.2f}).",
            f"RiskAgent assigned {risk.risk_level} risk ({risk.risk_score}/100); flags: {', '.join(risk.flags[:3]) or 'none'}.",
            f"Decision engine chose {decision.action} at {decision.confidence:.0f}% confidence. Thesis: {', '.join(decision.thesis[:3]) or 'limited edge'}.",
            f"Warnings: {', '.join(decision.warnings[:3]) or 'none'}.",
            f"Scenario uses real historical prices from the requested window; resulting PnL is {portfolio.pnl_pct:+.2f}% with max drawdown {portfolio.max_drawdown_pct:.2f}%.",
            f"Kraken CLI mode: {kraken_trade.mode}; executed={kraken_trade.executed}; note={kraken_trade.note}",
            f"Trustless checkpoint hash: {checkpoint_hash}",
            f"Decision receipt saved: {receipt.receipt_id}",
        ]

        return OrchestratorResponse(
            symbol=symbol,
            market=market,
            news=news,
            risk=risk,
            decision=decision,
            reasoning_steps=reasoning_steps,
            portfolio=portfolio,
            trade_history=trade_history,
            kraken_trade=kraken_trade,
            data_sources=DataSourceStatus(
                market=market.source,
                news=news.source,
                execution=execution_label,
                live_market_data=market.source in {"kraken_cli", "yfinance"},
                live_news_data=news.article_count > 0,
                live_trade_execution=live_trade_execution,
                execution_via_cli=self.kraken.is_available(),
            ),
            receipt=receipt,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )
