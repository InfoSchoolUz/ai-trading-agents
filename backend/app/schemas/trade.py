from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

ActionType = Literal["BUY", "SELL", "HOLD"]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH"]
TrendType = Literal["BULLISH", "BEARISH", "SIDEWAYS"]


class AnalyzeRequest(BaseModel):
    symbol: str = Field(..., examples=["BTC-USD"])
    interval: str = Field(default="1d", examples=["1d"])
    period: str = Field(default="3mo", examples=["3mo"])


class MarketAnalysis(BaseModel):
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
    drawdown_pct: float = 0.0
    support_level: float = 0.0
    resistance_level: float = 0.0
    trend: TrendType
    signal_score: int = 0
    summary: str
    signals: List[str] = Field(default_factory=list)
    prices: List[float] = Field(default_factory=list)
    source: str = "unknown"


class NewsItem(BaseModel):
    title: str
    publisher: str = "Unknown"
    published_at: Optional[str] = None
    link: str = ""
    sentiment_score: float = 0.0


class NewsAnalysis(BaseModel):
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    sentiment_label: str
    summary: str
    catalysts: List[str] = Field(default_factory=list)
    article_count: int = 0
    articles: List[NewsItem] = Field(default_factory=list)
    source: str = "unknown"
    llm_explanation: str = ""


class RiskAnalysis(BaseModel):
    risk_level: RiskLevel
    risk_score: int = Field(..., ge=0, le=100)
    position_size_pct: float
    stop_loss_pct: float
    take_profit_pct: float
    max_drawdown_limit_pct: float
    summary: str
    flags: List[str] = Field(default_factory=list)


class ExecutionDecision(BaseModel):
    action: ActionType
    confidence: float = Field(..., ge=0.0, le=100.0)
    explanation: str
    entry_price: Optional[float] = None
    thesis: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    strategy_name: str = "multi_factor_kraken_strategy"


class TradeRecord(BaseModel):
    step: int
    action: ActionType
    price: float
    units: float
    cash_after: float
    asset_units_after: float
    portfolio_value_after: float


class PortfolioSummary(BaseModel):
    starting_cash: float
    ending_cash: float
    asset_units: float
    ending_portfolio_value: float
    pnl_value: float
    pnl_pct: float
    max_drawdown_pct: float = 0.0


class KrakenTradeResult(BaseModel):
    executed: bool
    mode: str
    action: ActionType
    symbol: str
    volume: float
    order_result: Optional[Dict[str, Any]] = None
    status: Optional[Dict[str, Any] | List[Any]] = None
    error: Optional[str] = None
    note: str


class DataSourceStatus(BaseModel):
    market: str
    news: str
    execution: str
    live_market_data: bool = True
    live_news_data: bool = True
    live_trade_execution: bool = False
    execution_via_cli: bool = False


class DecisionReceipt(BaseModel):
    receipt_id: str
    created_at: str
    strategy_name: str
    market_source: str
    news_source: str
    execution_mode: str
    inputs_checksum: str
    decision_checksum: str
    storage_path: str


class OrchestratorResponse(BaseModel):
    symbol: str
    market: MarketAnalysis
    news: NewsAnalysis
    risk: RiskAnalysis
    decision: ExecutionDecision
    reasoning_steps: List[str]
    portfolio: PortfolioSummary
    trade_history: List[TradeRecord]
    kraken_trade: Optional[KrakenTradeResult] = None
    data_sources: DataSourceStatus
    receipt: DecisionReceipt
    generated_at: str
