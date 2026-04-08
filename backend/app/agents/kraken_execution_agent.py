from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.schemas.trade import ExecutionDecision, RiskAnalysis
from app.services.kraken_service import KrakenService


class KrakenExecutionAgent:
    """Execute BUY/SELL decisions through Kraken CLI paper/live mode."""

    def __init__(self) -> None:
        self.mode = settings.KRAKEN_MODE.lower()
        self.enabled = settings.ENABLE_EXECUTION

    def _build_note(self, executed: bool, action: str) -> str:
        if action == "HOLD":
            return "No order was placed because the decision was HOLD."
        if not self.enabled:
            return "Execution disabled by configuration. Set ENABLE_EXECUTION=true to send Kraken CLI orders."
        if self.mode == "paper":
            return "Trade executed through Kraken CLI paper mode." if executed else "Kraken CLI paper order failed."
        return "Trade executed through Kraken CLI live mode." if executed else "Kraken CLI live order failed."

    def execute(
        self,
        decision: ExecutionDecision,
        risk: RiskAnalysis,
        symbol: str,
        starting_balance: float = 10_000.0,
    ) -> dict[str, Any]:
        action = decision.action
        if action == "HOLD":
            return {
                "executed": False,
                "mode": self.mode,
                "action": action,
                "symbol": symbol,
                "volume": 0.0,
                "order_result": None,
                "status": None,
                "error": None,
                "note": self._build_note(False, action),
            }

        if not self.enabled:
            return {
                "executed": False,
                "mode": self.mode,
                "action": action,
                "symbol": symbol,
                "volume": 0.0,
                "order_result": None,
                "status": None,
                "error": "Execution disabled in settings",
                "note": self._build_note(False, action),
            }

        if not KrakenService.is_available():
            return {
                "executed": False,
                "mode": self.mode,
                "action": action,
                "symbol": symbol,
                "volume": 0.0,
                "order_result": None,
                "status": None,
                "error": "Kraken CLI not found on PATH",
                "note": "Install Kraken CLI and ensure the binary is available on PATH.",
            }

        price = decision.entry_price or 0.0
        fraction = max(0.01, min(1.0, settings.EXECUTION_CASH_FRACTION))
        volume = KrakenService.volume_from_cash(
            cash=starting_balance,
            price=price,
            fraction=fraction,
        )
        if volume <= 0:
            return {
                "executed": False,
                "mode": self.mode,
                "action": action,
                "symbol": symbol,
                "volume": 0.0,
                "order_result": None,
                "status": None,
                "error": "Unable to derive order volume from current price",
                "note": "Execution skipped because order size could not be calculated.",
            }

        try:
            if self.mode == "live":
                raise RuntimeError(
                    "Live Kraken CLI execution is not implemented in this codebase. Use paper mode for the hackathon demo or extend the service for live credentials."
                )

            order_result = (
                KrakenService.paper_buy(symbol, volume)
                if action == "BUY"
                else KrakenService.paper_sell(symbol, volume)
            )
            status = KrakenService.paper_status()
            return {
                "executed": True,
                "mode": self.mode,
                "action": action,
                "symbol": symbol,
                "volume": volume,
                "order_result": order_result,
                "status": status,
                "error": None,
                "note": self._build_note(True, action),
            }
        except Exception as exc:
            return {
                "executed": False,
                "mode": self.mode,
                "action": action,
                "symbol": symbol,
                "volume": volume,
                "order_result": None,
                "status": None,
                "error": str(exc),
                "note": self._build_note(False, action),
            }
