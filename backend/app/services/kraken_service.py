"""
KrakenService — wraps the official Kraken CLI binary for public market data,
paper trading, and live spot execution.

Supported modes in this codebase:
  - Public market data: no credentials required
  - Paper trading: no credentials required
  - Live spot trading: requires KRAKEN_API_KEY and KRAKEN_API_SECRET

The binary is expected to be on PATH as `kraken` unless KRAKEN_CLI_PATH is set.
Reference: https://github.com/krakenfx/kraken-cli
"""
from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from dotenv import dotenv_values

logger = logging.getLogger(__name__)

# Kraken CLI uses its own pair names (e.g. XBTUSD not BTC-USD)
_SYMBOL_MAP: dict[str, str] = {
    "BTC-USD": "XBTUSD",
    "ETH-USD": "ETHUSD",
    "SOL-USD": "SOLUSD",
    "XRP-USD": "XRPUSD",
    "ADA-USD": "ADAUSD",
    "DOGE-USD": "DOGEUSD",
    "LTC-USD": "LTCUSD",
    "DOT-USD": "DOTUSD",
    "AVAX-USD": "AVAXUSD",
    "MATIC-USD": "MATICUSD",
    "LINK-USD": "LINKUSD",
}


def _to_kraken_pair(symbol: str) -> str:
    """Convert yfinance symbol (BTC-USD) to Kraken pair (XBTUSD)."""
    return _SYMBOL_MAP.get(symbol.upper(), symbol.replace("-", "").upper())


def _discover_env_file() -> str | None:
    """Best-effort discovery of a nearby .env file for subprocess auth propagation."""
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parents[2] / ".env",  # backend/.env
        Path(__file__).resolve().parents[3] / ".env",  # repo root fallback
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def _build_subprocess_env() -> dict[str, str]:
    """Merge current environment with values from .env so Kraken CLI sees credentials."""
    env = dict(os.environ)
    env_file = _discover_env_file()
    if env_file:
        for key, value in dotenv_values(env_file).items():
            if value is not None and key not in env:
                env[key] = value
    return env


def _kraken_binary() -> str:
    requested = os.getenv("KRAKEN_CLI_PATH", "kraken").strip() or "kraken"
    if requested != "kraken" and Path(requested).exists():
        return requested
    resolved = shutil.which(requested) or shutil.which("kraken")
    if not resolved:
        raise RuntimeError(
            "Kraken CLI not found on PATH. "
            "Download from https://github.com/krakenfx/kraken-cli/releases "
            "and place the binary in your PATH."
        )
    return resolved


def _run(args: list[str], timeout: int = 20) -> dict[str, Any]:
    """
    Run Kraken CLI and return parsed JSON.
    Raises RuntimeError if the CLI is not found or returns an error.
    """
    binary = _kraken_binary()
    cmd = [binary] + args + ["-o", "json"]
    env = _build_subprocess_env()
    logger.info("KrakenCLI: %s", " ".join(cmd))
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"Kraken CLI timed out after {timeout}s") from exc

    raw = (result.stdout or "").strip() or (result.stderr or "").strip()
    logger.debug("KrakenCLI raw: %s", raw[:500])

    if not raw:
        raise RuntimeError("Kraken CLI returned no output.")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Kraken CLI returned non-JSON: {raw[:300]}") from exc

    # CLI errors are often returned as {"error": ...} or {"success": false, ...}
    if isinstance(data, dict):
        if data.get("error"):
            raise RuntimeError(f"Kraken CLI error: {data['error']}")
        if data.get("success") is False:
            message = data.get("message") or data.get("detail") or raw[:300]
            raise RuntimeError(f"Kraken CLI failure: {message}")

    return data


class KrakenService:
    """Stateless wrapper around Kraken CLI for paper and live spot execution."""

    @staticmethod
    def is_available() -> bool:
        try:
            _kraken_binary()
            return True
        except Exception:
            return False

    @staticmethod
    def has_live_credentials() -> bool:
        env = _build_subprocess_env()
        return bool(env.get("KRAKEN_API_KEY") and env.get("KRAKEN_API_SECRET"))

    @staticmethod
    def normalize_pair(symbol: str) -> str:
        return _to_kraken_pair(symbol)

    # ── Public market data ──────────────────────────────────────────────────

    @staticmethod
    def ticker(symbol: str) -> dict[str, Any]:
        pair = _to_kraken_pair(symbol)
        return _run(["ticker", pair])

    @staticmethod
    def ohlc(symbol: str, interval_minutes: int = 60) -> dict[str, Any]:
        pair = _to_kraken_pair(symbol)
        return _run(["ohlc", pair, "--interval", str(interval_minutes)])

    # ── Private account data ───────────────────────────────────────────────

    @staticmethod
    def balance() -> dict[str, Any]:
        return _run(["balance"])

    @staticmethod
    def open_orders() -> dict[str, Any]:
        return _run(["open-orders"])

    @staticmethod
    def closed_orders() -> dict[str, Any]:
        return _run(["closed-orders", "--without-count"])

    # ── Paper portfolio helpers ────────────────────────────────────────────

    @staticmethod
    def paper_init(balance: float = 10_000.0, currency: str = "USD") -> dict[str, Any]:
        return _run(["paper", "init", "--balance", str(balance), "--currency", currency])

    @staticmethod
    def paper_status() -> dict[str, Any]:
        return _run(["paper", "status"])

    @staticmethod
    def paper_balance() -> dict[str, Any]:
        return _run(["paper", "balance"])

    @staticmethod
    def paper_orders() -> dict[str, Any]:
        return _run(["paper", "orders"])

    @staticmethod
    def paper_history() -> dict[str, Any]:
        return _run(["paper", "history"])

    @staticmethod
    def paper_reset() -> dict[str, Any]:
        return _run(["paper", "reset"])

    @staticmethod
    def paper_cancel(order_id: str) -> dict[str, Any]:
        return _run(["paper", "cancel", order_id])

    # ── Spot order execution ───────────────────────────────────────────────

    @staticmethod
    def _spot_order_args(
        side: str,
        symbol: str,
        volume: float,
        *,
        order_type: str = "market",
        price: float | None = None,
        validate: bool = False,
    ) -> list[str]:
        pair = _to_kraken_pair(symbol)
        args = ["order", side.lower(), pair, str(volume)]
        if order_type:
            args += ["--type", order_type]
        if order_type == "limit":
            if price is None or price <= 0:
                raise ValueError("Limit order requires a positive price.")
            args += ["--price", str(price)]
        if validate:
            args += ["--validate"]
        return args

    @staticmethod
    def live_buy(
        symbol: str,
        volume: float,
        *,
        order_type: str = "market",
        price: float | None = None,
        validate: bool = False,
    ) -> dict[str, Any]:
        if not KrakenService.has_live_credentials():
            raise RuntimeError("Live mode requires KRAKEN_API_KEY and KRAKEN_API_SECRET.")
        return _run(KrakenService._spot_order_args("buy", symbol, volume, order_type=order_type, price=price, validate=validate))

    @staticmethod
    def live_sell(
        symbol: str,
        volume: float,
        *,
        order_type: str = "market",
        price: float | None = None,
        validate: bool = False,
    ) -> dict[str, Any]:
        if not KrakenService.has_live_credentials():
            raise RuntimeError("Live mode requires KRAKEN_API_KEY and KRAKEN_API_SECRET.")
        return _run(KrakenService._spot_order_args("sell", symbol, volume, order_type=order_type, price=price, validate=validate))

    @staticmethod
    def paper_buy(symbol: str, volume: float) -> dict[str, Any]:
        pair = _to_kraken_pair(symbol)
        return _run(["paper", "buy", pair, str(volume)])

    @staticmethod
    def paper_sell(symbol: str, volume: float) -> dict[str, Any]:
        pair = _to_kraken_pair(symbol)
        return _run(["paper", "sell", pair, str(volume)])

    @staticmethod
    def paper_limit_buy(symbol: str, volume: float, price: float) -> dict[str, Any]:
        pair = _to_kraken_pair(symbol)
        return _run(["paper", "buy", pair, str(volume), "--type", "limit", "--price", str(price)])

    @staticmethod
    def paper_limit_sell(symbol: str, volume: float, price: float) -> dict[str, Any]:
        pair = _to_kraken_pair(symbol)
        return _run(["paper", "sell", pair, str(volume), "--type", "limit", "--price", str(price)])

    # ── Convenience: compute volume from cash ──────────────────────────────

    @staticmethod
    def volume_from_cash(cash: float, price: float, fraction: float = 0.10) -> float:
        if price <= 0:
            return 0.0
        raw = (cash * fraction) / price
        return max(round(raw, 6), 0.0001)
