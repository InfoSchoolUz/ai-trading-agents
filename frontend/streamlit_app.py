from __future__ import annotations

import os
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(
    page_title="AI Trading Agents",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
# Local development uchun (kompyuterda ishlaganda)
# DEFAULT_BACKEND_URL = "http://127.0.0.1:8000"

# Production (Railway backend)
DEFAULT_BACKEND_URL = "https://ai-trading-agents-production.up.railway.app"

POPULAR_TICKERS = {
    "🪙 Crypto — Top 20": {
        "Bitcoin": "BTC-USD",
        "Ethereum": "ETH-USD",
        "Solana": "SOL-USD",
        "BNB (Binance Coin)": "BNB-USD",
        "XRP (Ripple)": "XRP-USD",
        "Dogecoin": "DOGE-USD",
        "Cardano": "ADA-USD",
        "Avalanche": "AVAX-USD",
        "Chainlink": "LINK-USD",
        "Polkadot": "DOT-USD",
        "Litecoin": "LTC-USD",
        "Uniswap": "UNI-USD",
        "Polygon": "MATIC-USD",
        "Toncoin": "TON-USD",
        "Shiba Inu": "SHIB-USD",
        "Bitcoin Cash": "BCH-USD",
        "Stellar": "XLM-USD",
        "Monero": "XMR-USD",
        "Cosmos": "ATOM-USD",
        "Filecoin": "FIL-USD",
    },
    "💻 Tech Stocks": {
        "Apple (iPhone, Mac)": "AAPL",
        "Microsoft (Windows, Azure)": "MSFT",
        "NVIDIA (AI Chips)": "NVDA",
        "Tesla (Electric Cars)": "TSLA",
        "Google (Alphabet)": "GOOGL",
        "Amazon (AWS, Shopping)": "AMZN",
        "Meta (Facebook, Instagram)": "META",
        "Netflix (Streaming)": "NFLX",
        "AMD (Processors)": "AMD",
        "Intel (Processors)": "INTC",
        "Adobe (Creative Software)": "ADBE",
        "Salesforce (CRM Software)": "CRM",
        "Oracle (Database)": "ORCL",
        "Cisco (Networking)": "CSCO",
        "IBM (Enterprise Tech)": "IBM",
        "Qualcomm (Mobile Chips)": "QCOM",
        "Broadcom (Semiconductors)": "AVGO",
        "Spotify (Music Streaming)": "SPOT",
        "Uber (Ride Sharing)": "UBER",
        "Airbnb (Travel)": "ABNB",
    },
    "🏦 Finance Stocks": {
        "JPMorgan Chase (Largest US Bank)": "JPM",
        "Goldman Sachs (Investment Bank)": "GS",
        "Bank of America": "BAC",
        "Wells Fargo": "WFC",
        "Morgan Stanley (Investment Bank)": "MS",
        "Visa (Payment Network)": "V",
        "Mastercard (Payment Network)": "MA",
        "PayPal (Online Payments)": "PYPL",
        "Coinbase (Crypto Exchange)": "COIN",
        "BlackRock (Asset Management)": "BLK",
        "American Express (Credit Cards)": "AXP",
        "Charles Schwab (Brokerage)": "SCHW",
    },
    "🏥 Healthcare Stocks": {
        "Johnson & Johnson (Pharma)": "JNJ",
        "Pfizer (Vaccines, Drugs)": "PFE",
        "Moderna (mRNA Vaccines)": "MRNA",
        "AbbVie (Biologics)": "ABBV",
        "Merck (Pharma)": "MRK",
        "UnitedHealth (Health Insurance)": "UNH",
        "CVS Health (Pharmacy)": "CVS",
        "Eli Lilly (Diabetes, Weight Loss)": "LLY",
    },
    "🛒 Consumer Stocks": {
        "Walmart (Retail Giant)": "WMT",
        "Coca-Cola (Beverages)": "KO",
        "PepsiCo (Beverages & Snacks)": "PEP",
        "McDonald's (Fast Food)": "MCD",
        "Nike (Sportswear)": "NKE",
        "Disney (Entertainment)": "DIS",
        "Starbucks (Coffee)": "SBUX",
        "Procter & Gamble (Household)": "PG",
        "Target (Retail)": "TGT",
        "Home Depot (Home Improvement)": "HD",
    },
    "⚡ Energy Stocks": {
        "ExxonMobil (Oil & Gas)": "XOM",
        "Chevron (Oil & Gas)": "CVX",
        "Shell (Oil & Gas)": "SHEL",
        "BP (Oil & Gas)": "BP",
        "ConocoPhillips (Oil & Gas)": "COP",
        "Schlumberger (Oilfield Services)": "SLB",
        "NextEra Energy (Renewable)": "NEE",
    },
    "📊 Indexes": {
        "S&P 500 (Top 500 US Companies)": "^GSPC",
        "Dow Jones (Top 30 US Companies)": "^DJI",
        "Nasdaq 100 (Top 100 Tech)": "^NDX",
        "Russell 2000 (Small US Companies)": "^RUT",
        "FTSE 100 (Top 100 UK Companies)": "^FTSE",
        "DAX (Top 40 German Companies)": "^GDAXI",
        "Nikkei 225 (Top 225 Japan)": "^N225",
        "Hang Seng (Top Hong Kong)": "^HSI",
        "CAC 40 (Top 40 French Companies)": "^FCHI",
        "ASX 200 (Top 200 Australia)": "^AXJO",
    },
    "💱 Forex": {
        "Euro → US Dollar": "EURUSD=X",
        "British Pound → US Dollar": "GBPUSD=X",
        "US Dollar → Japanese Yen": "USDJPY=X",
        "US Dollar → Swiss Franc": "USDCHF=X",
        "Australian Dollar → US Dollar": "AUDUSD=X",
        "US Dollar → Canadian Dollar": "USDCAD=X",
        "New Zealand Dollar → US Dollar": "NZDUSD=X",
        "US Dollar → Chinese Yuan": "USDCNY=X",
        "US Dollar → Hong Kong Dollar": "USDHKD=X",
        "US Dollar → Singapore Dollar": "USDSGD=X",
        "US Dollar → South Korean Won": "USDKRW=X",
        "US Dollar → Indian Rupee": "USDINR=X",
        "US Dollar → Mexican Peso": "USDMXN=X",
        "US Dollar → Brazilian Real": "USDBRL=X",
        "US Dollar → Turkish Lira": "USDTRY=X",
        "US Dollar → South African Rand": "USDZAR=X",
        "US Dollar → Swedish Krona": "USDSEK=X",
        "Euro → British Pound": "EURGBP=X",
        "Euro → Japanese Yen": "EURJPY=X",
        "British Pound → Japanese Yen": "GBPJPY=X",
        "US Dollar → Uzbek Som": "USDUZS=X",
    },
    "🥇 Metals": {
        "Gold (Safe Haven Asset)": "GC=F",
        "Silver (Industrial & Investment)": "SI=F",
        "Platinum (Auto Catalysts)": "PL=F",
        "Palladium (Auto Catalysts)": "PA=F",
        "Copper (Industrial Metal)": "HG=F",
        "Aluminum (Industrial Metal)": "ALI=F",
    },
    "🛢️ Energy Commodities": {
        "Crude Oil WTI (US Benchmark)": "CL=F",
        "Brent Oil (Global Benchmark)": "BZ=F",
        "Natural Gas (Heating & Power)": "NG=F",
        "Gasoline (Motor Fuel)": "RB=F",
        "Heating Oil (Winter Fuel)": "HO=F",
    },
    "🌾 Agriculture": {
        "Wheat (Bread & Pasta)": "ZW=F",
        "Corn (Food & Ethanol)": "ZC=F",
        "Soybeans (Food & Feed)": "ZS=F",
        "Sugar (Food Industry)": "SB=F",
        "Coffee (Beverages)": "KC=F",
        "Cocoa (Chocolate)": "CC=F",
        "Cotton (Textile)": "CT=F",
        "Rice (Staple Food)": "ZR=F",
    },
    "📦 ETFs (Funds)": {
        "S&P 500 Index Fund (SPY)": "SPY",
        "Nasdaq 100 Index Fund (QQQ)": "QQQ",
        "Gold Fund (GLD)": "GLD",
        "Oil Fund (USO)": "USO",
        "US Bond Fund (TLT)": "TLT",
        "Emerging Markets Fund (EEM)": "EEM",
        "Bitcoin Spot ETF (IBIT)": "IBIT",
        "Ethereum Spot ETF (ETHA)": "ETHA",
    },
    "✏️ Custom": {
        "Manual input": "__custom__",
    },
}

PERIODS = ["1mo", "3mo", "6mo", "1y"]
INTERVALS = ["1d", "1wk", "1mo"]


def inject_css() -> None:
    st.markdown(
        """
        <style>
        html, body, [class*="css"] {
            font-family: Arial, Helvetica, sans-serif;
        }

        .stApp {
            background-color: #080c14;
            color: #e2e8f0;
        }

        .block-container {
            max-width: 1440px;
            padding-top: 5rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            background-color: #0c1220;
            border-right: 1px solid rgba(99,179,237,0.08);
        }

        [data-testid="stSidebar"] * {
            color: #cbd5e1 !important;
        }

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {
            background-color: #0f1928 !important;
            border: 1px solid rgba(99,179,237,0.15) !important;
            border-radius: 10px !important;
            color: #e2e8f0 !important;
            font-family: Arial, Helvetica, sans-serif !important;
        }

        label, .stSelectbox label, .stTextInput label {
            color: #94a3b8 !important;
            font-weight: 600 !important;
            font-size: 0.78rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
        }

        div.stButton > button {
            width: 100%;
            border: 1px solid rgba(99,179,237,0.25);
            border-radius: 10px;
            padding: 0.75rem 1rem;
            font-weight: 700;
            font-family: Arial, Helvetica, sans-serif;
            color: #e2e8f0;
            background: linear-gradient(135deg, #1a3a5c 0%, #0f2440 100%);
            transition: all 0.2s;
            letter-spacing: 0.04em;
        }

        div.stButton > button:hover {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            border-color: rgba(99,179,237,0.5);
            color: white;
        }

        .page-title {
            font-size: 3.2rem;   /* ⬅️ KATTALASHDI */
            font-weight: 800;    /* ⬅️ YANADA QALIN */
            color: #f1f5f9;
            letter-spacing: -0.03em;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
            line-height: 1.1;
        }

        .page-title span {
            color: #3b82f6;
        }

        .page-subtitle {
            color: #64748b;
            font-size: 0.95rem;
            margin-bottom: 1.8rem;
        }

        .card {
            border: 1px solid rgba(99,179,237,0.1);
            border-radius: 16px;
            background-color: #0c1828;
            padding: 20px;
            margin-bottom: 14px;
        }

        .card-sm {
            border: 1px solid rgba(99,179,237,0.1);
            border-radius: 14px;
            background-color: #0c1828;
            padding: 16px;
            margin-bottom: 12px;
        }

        .section-label {
            font-size: 0.72rem;
            color: #3b82f6;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-weight: 700;
            margin-bottom: 10px;
        }

        .metric-value {
            font-size: 1.9rem;
            font-weight: 700;
            color: #f1f5f9;
            line-height: 1;
        }

        .metric-label {
            font-size: 0.72rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 600;
            margin-bottom: 6px;
        }

        .metric-sub {
            font-size: 0.82rem;
            color: #475569;
            margin-top: 6px;
        }

        .signal-action {
            font-size: 2.8rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            line-height: 1;
            margin-bottom: 8px;
        }

        .signal-action.buy { color: #22c55e; }
        .signal-action.sell { color: #ef4444; }
        .signal-action.hold { color: #f59e0b; }

        .signal-meta {
            color: #94a3b8;
            font-size: 0.92rem;
            line-height: 1.6;
            margin-bottom: 14px;
        }

        .signal-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
        }

        .signal-mini {
            background-color: #080c14;
            border: 1px solid rgba(99,179,237,0.08);
            border-radius: 10px;
            padding: 12px;
        }

        .signal-mini-label {
            font-size: 0.68rem;
            color: #475569;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .signal-mini-value {
            font-size: 0.95rem;
            font-weight: 700;
            color: #e2e8f0;
        }

        .workflow-step {
            display: flex;
            gap: 12px;
            align-items: flex-start;
            padding: 10px 0;
            border-bottom: 1px solid rgba(99,179,237,0.06);
        }

        .workflow-step:last-child {
            border-bottom: none;
        }

        .workflow-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #3b82f6;
            margin-top: 6px;
            flex-shrink: 0;
        }

        .workflow-title {
            font-size: 0.75rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 700;
            margin-bottom: 3px;
        }

        .workflow-value {
            font-size: 0.9rem;
            color: #cbd5e1;
            line-height: 1.5;
        }

        .reason-step {
            background-color: #080c14;
            border: 1px solid rgba(99,179,237,0.08);
            border-radius: 10px;
            padding: 12px 14px;
            margin-bottom: 8px;
            color: #cbd5e1;
            font-size: 0.92rem;
            line-height: 1.6;
        }

        .reason-step b {
            color: #3b82f6;
        }

        .news-item {
            padding: 12px 0;
            border-bottom: 1px solid rgba(99,179,237,0.06);
        }

        .news-item:last-child {
            border-bottom: none;
        }

        .news-title {
            font-size: 0.95rem;
            font-weight: 600;
            color: #e2e8f0;
            margin-bottom: 5px;
            line-height: 1.4;
        }

        .news-title a {
            color: #e2e8f0;
            text-decoration: none;
        }

        .news-title a:hover {
            color: #3b82f6;
        }

        .news-meta {
            font-size: 0.8rem;
            color: #475569;
        }

        .sentiment-pos { color: #22c55e; }
        .sentiment-neg { color: #ef4444; }
        .sentiment-neu { color: #94a3b8; }

        .risk-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(99,179,237,0.06);
            font-size: 0.9rem;
        }

        .risk-row:last-child {
            border-bottom: none;
        }

        .risk-key {
            color: #64748b;
            font-weight: 600;
        }

        .risk-val {
            color: #e2e8f0;
        }

        .status-ok { color: #22c55e; font-weight: 700; }
        .status-warn { color: #f59e0b; font-weight: 700; }
        .status-bad { color: #ef4444; font-weight: 700; }

        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            border: 1px solid rgba(99,179,237,0.2);
            background-color: rgba(99,179,237,0.08);
        }

        .badge-live {
            color: #22c55e;
            border-color: rgba(34,197,94,0.3);
            background-color: rgba(34,197,94,0.08);
        }

        .badge-fallback {
            color: #f59e0b;
            border-color: rgba(245,158,11,0.3);
            background-color: rgba(245,158,11,0.08);
        }

        .empty-state {
            border: 1px dashed rgba(99,179,237,0.15);
            border-radius: 20px;
            background-color: #0c1220;
            padding: 64px 28px;
            text-align: center;
            margin-top: 16px;
        }

        .empty-icon {
            font-size: 3rem;
            margin-bottom: 16px;
        }

        .empty-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: 10px;
        }

        .empty-subtitle {
            font-size: 0.95rem;
            color: #475569;
            line-height: 1.7;
            max-width: 400px;
            margin: 0 auto;
        }

        .sidebar-logo {
            font-size: 1.1rem;
            font-weight: 700;
            color: #f1f5f9;
            letter-spacing: -0.01em;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid rgba(99,179,237,0.1);
        }

        .sidebar-logo span {
            color: #3b82f6;
        }

        @media (max-width: 900px) {
            .block-container {
                padding-top: 3.5rem;
            }

            .signal-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .page-title {
                font-size: 1.8rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_backend_url() -> str:
    try:
        secret_url = st.secrets.get("BACKEND_URL", "")
    except Exception:
        secret_url = ""
    env_url = os.getenv("BACKEND_URL", "")
    return (secret_url or env_url or DEFAULT_BACKEND_URL).strip().rstrip("/")


@st.cache_data(ttl=15)
def get_health(base_url: str) -> dict[str, Any]:
    response = requests.get(f"{base_url}/health", timeout=10)
    response.raise_for_status()
    return response.json()


def analyze_symbol(base_url: str, symbol: str, period: str, interval: str) -> dict[str, Any]:
    payload = {"symbol": symbol, "period": period, "interval": interval}
    response = requests.post(f"{base_url}/analyze", json=payload, timeout=120)

    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise RuntimeError(f"Backend error: {detail}")

    return response.json()


def render_metric_card(label: str, value: str, sub: str = "") -> None:
    st.markdown(
        f"""
        <div class="card-sm">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_price_chart(prices: list[float], symbol: str) -> None:
    if not prices:
        st.info("No price data available.")
        return

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(range(1, len(prices) + 1)),
            y=prices,
            mode="lines",
            name=symbol,
            line=dict(width=2, color="#3b82f6"),
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.08)",
        )
    )
    fig.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#080c14",
        font=dict(color="#64748b", family="JetBrains Mono"),
        showlegend=False,
        xaxis=dict(showgrid=True, gridcolor="rgba(99,179,237,0.05)", zeroline=False, tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor="rgba(99,179,237,0.05)", zeroline=False, tickfont=dict(size=10)),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_confidence_gauge(confidence: float) -> None:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=confidence,
            number={"suffix": "%", "font": {"size": 32, "color": "#f1f5f9", "family": "JetBrains Mono"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#475569", "tickfont": {"size": 10}},
                "bar": {"color": "#3b82f6"},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 1,
                "bordercolor": "rgba(99,179,237,0.1)",
                "steps": [
                    {"range": [0, 35], "color": "rgba(239,68,68,0.15)"},
                    {"range": [35, 65], "color": "rgba(250,204,21,0.12)"},
                    {"range": [65, 100], "color": "rgba(34,197,94,0.15)"},
                ],
            },
            title={"text": "Decision Confidence", "font": {"size": 13, "color": "#64748b"}},
        )
    )
    fig.update_layout(height=230, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)


def render_reasoning(steps: list[str]) -> None:
    if not steps:
        st.info("No reasoning steps available.")
        return
    for idx, step in enumerate(steps, start=1):
        st.markdown(
            f'<div class="reason-step"><b>#{idx}</b> {step}</div>',
            unsafe_allow_html=True,
        )


def render_articles(articles: list[dict[str, Any]]) -> None:
    if not articles:
        st.info("No news articles found.")
        return

    for article in articles:
        title = article.get("title", "Untitled")
        link = article.get("link", "")
        publisher = article.get("publisher", "Unknown")
        published = article.get("published_at") or "Unknown time"
        sentiment = float(article.get("sentiment_score", 0.0))

        sent_class = "sentiment-pos" if sentiment > 0.1 else "sentiment-neg" if sentiment < -0.1 else "sentiment-neu"
        sent_arrow = "▲" if sentiment > 0.1 else "▼" if sentiment < -0.1 else "●"

        title_html = (
            f'<a href="{link}" target="_blank">{title}</a>'
            if link else title
        )

        st.markdown(
            f"""
            <div class="news-item">
                <div class="news-title">{title_html}</div>
                <div class="news-meta">
                    {publisher} · {published}
                    &nbsp;·&nbsp;
                    <span class="{sent_class}">{sent_arrow} {sentiment:+.2f}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def build_ai_insight(news: dict[str, Any], decision: dict[str, Any], risk: dict[str, Any], market: dict[str, Any]) -> str:
    llm_text = str(news.get("llm_explanation") or news.get("summary") or "").strip()
    if llm_text:
        return llm_text

    sentiment_label = str(news.get("sentiment_label", "NEUTRAL")).upper()
    sentiment_score = float(news.get("sentiment_score", 0.0) or 0.0)
    action = str(decision.get("action", "HOLD")).upper()
    confidence = float(decision.get("confidence", 0.0) or 0.0)
    risk_level = str(risk.get("risk_level", "HIGH")).upper()
    trend = str(market.get("trend", "SIDEWAYS")).upper()
    current_price = float(market.get("current_price", 0.0) or 0.0)
    momentum = float(market.get("momentum_pct", 0.0) or 0.0)
    volatility = float(market.get("volatility_pct", 0.0) or 0.0)

    direction = "bullish" if sentiment_score > 0.15 else "bearish" if sentiment_score < -0.15 else "mixed"
    return (
        f"Market trend is {trend} with current price at ${current_price:,.2f}. "
        f"Momentum is {momentum:+.2f}% and annualized volatility is {volatility:.2f}%. "
        f"News sentiment is {sentiment_label} ({sentiment_score:+.2f}), indicating a {direction} outlook. "
        f"System decision: {action} with {confidence:.1f}% confidence under {risk_level} risk conditions."
    )


def render_ai_insight(ai_summary: str, used_backend_ai: bool) -> None:
    badge_class = "badge-live" if used_backend_ai else "badge-fallback"
    badge_text = "LIVE AI" if used_backend_ai else "UI FALLBACK"

    st.markdown(
        f"""
        <div class="card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                <div class="section-label">AI Market Narrative</div>
                <div class="badge {badge_class}">{badge_text}</div>
            </div>
            <div style="color:#cbd5e1; line-height:1.8; font-size:0.95rem;">
                {ai_summary}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_execution_status(kraken_trade: dict[str, Any] | None) -> tuple[str, str]:
    if not kraken_trade:
        return "Unknown", "status-warn"
    if kraken_trade.get("executed"):
        return "Executed", "status-ok"
    if kraken_trade.get("error"):
        return "Failed", "status-bad"
    return "Skipped", "status-warn"


def build_agent_workflow(
    market: dict[str, Any],
    news: dict[str, Any],
    risk: dict[str, Any],
    decision: dict[str, Any],
    kraken_trade: dict[str, Any] | None,
) -> list[tuple[str, str]]:
    trend = market.get("trend", "Unknown")
    sentiment_label = news.get("sentiment_label", "Unknown")
    sentiment_score = float(news.get("sentiment_score", 0.0) or 0.0)
    risk_level = risk.get("risk_level", "Unknown")
    risk_score = risk.get("risk_score", "Unknown")
    action = decision.get("action", "Unknown")
    confidence = float(decision.get("confidence", 0.0) or 0.0)
    exec_status, _ = get_execution_status(kraken_trade)
    exec_mode = kraken_trade.get("mode", "-") if kraken_trade else "-"
    exec_note = kraken_trade.get("note", "-") if kraken_trade else "-"

    return [
        ("Market Agent", f"Collected market data. Trend: {trend}."),
        ("News Agent", f"Sentiment: {sentiment_label} ({sentiment_score:+.2f})."),
        ("Risk Agent", f"Risk level: {risk_level}. Score: {risk_score}."),
        ("Decision Agent", f"Action: {action} with {confidence:.1f}% confidence."),
        ("Execution Agent", f"Status: {exec_status}. Mode: {exec_mode}."),
        ("Receipt Logger", str(exec_note)),
    ]


def render_agent_workflow(
    market: dict[str, Any],
    news: dict[str, Any],
    risk: dict[str, Any],
    decision: dict[str, Any],
    kraken_trade: dict[str, Any] | None,
) -> None:
    workflow = build_agent_workflow(market, news, risk, decision, kraken_trade)
    for title, value in workflow:
        st.markdown(
            f"""
            <div class="workflow-step">
                <div class="workflow-dot"></div>
                <div>
                    <div class="workflow-title">{title}</div>
                    <div class="workflow-value">{value}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_execution_panel(kraken_trade: dict[str, Any] | None) -> None:
    status, status_class = get_execution_status(kraken_trade)

    if not kraken_trade:
        st.markdown(
            f'<div class="card-sm"><div class="risk-row"><span class="risk-key">Status</span><span class="{status_class}">{status}</span></div></div>',
            unsafe_allow_html=True,
        )
        return

    mode = kraken_trade.get("mode", "-")
    action = kraken_trade.get("action", "-")
    volume = kraken_trade.get("volume", 0)
    note = kraken_trade.get("note", "-")
    error = kraken_trade.get("error")

    rows = [
        ("Status", f'<span class="{status_class}">{status}</span>'),
        ("Mode", mode),
        ("Action", action),
        ("Volume", str(volume)),
        ("Note", note),
    ]
    if error:
        rows.append(("Error", f'<span class="status-bad">{error}</span>'))

    rows_html = "".join(
        f'<div class="risk-row"><span class="risk-key">{k}</span><span class="risk-val">{v}</span></div>'
        for k, v in rows
    )
    st.markdown(f'<div class="card-sm">{rows_html}</div>', unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────────
for key in ("analyzed", "result", "last_error"):
    if key not in st.session_state:
        st.session_state[key] = False if key == "analyzed" else None

inject_css()
backend_url = get_backend_url()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="sidebar-logo">⬡ AI <span>Trading</span> Agents</div>',
        unsafe_allow_html=True,
    )

    category = st.selectbox("Category", list(POPULAR_TICKERS.keys()), index=0)
    asset_name = st.selectbox("Asset", list(POPULAR_TICKERS[category].keys()))
    asset_value = POPULAR_TICKERS[category][asset_name]

    if asset_value == "__custom__":
        symbol = st.text_input("Custom symbol", value="BTC-USD").strip().upper()
    else:
        symbol = asset_value

    period = st.selectbox("Period", PERIODS, index=1)
    interval = st.selectbox("Interval", INTERVALS, index=0)

    st.markdown("<br>", unsafe_allow_html=True)
    analyze_clicked = st.button("▶ Run Analysis", use_container_width=True)
    reset_clicked = st.button("↺ Reset", use_container_width=True)

if reset_clicked:
    st.session_state.analyzed = False
    st.session_state.result = None
    st.session_state.last_error = None
    st.rerun()

# ── Health check ───────────────────────────────────────────────────────────────
try:
    _ = get_health(backend_url)
except Exception as exc:
    st.error(f"Cannot connect to backend: {exc}")
    st.stop()

# ── Run analysis ───────────────────────────────────────────────────────────────
if analyze_clicked:
    try:
        with st.spinner(f"Analyzing {symbol}..."):
            result = analyze_symbol(backend_url, symbol, period, interval)
        st.session_state.result = result
        st.session_state.analyzed = True
        st.session_state.last_error = None
        st.rerun()
    except Exception as exc:
        st.session_state.last_error = str(exc)
        st.session_state.result = None
        st.session_state.analyzed = False

if st.session_state.last_error:
    st.error(st.session_state.last_error)

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="page-title">AI <span>Trading</span> Agents</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="page-subtitle">Autonomous multi-agent market analysis & decision support</div>',
    unsafe_allow_html=True,
)

# ── Empty state ────────────────────────────────────────────────────────────────
if not st.session_state.analyzed or not st.session_state.result:
    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-icon">📊</div>
            <div class="empty-title">Select an asset and run analysis</div>
            <div class="empty-subtitle">
                Choose a category and asset from the sidebar, set your period and interval,
                then click <strong>Run Analysis</strong> to get AI-powered insights.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ── Data extraction ────────────────────────────────────────────────────────────
result = st.session_state.result
market = result.get("market", {})
news = result.get("news", {})
risk = result.get("risk", {})
decision = result.get("decision", {})
portfolio = result.get("portfolio", {})
kraken_trade = result.get("kraken_trade", {})
receipt = result.get("receipt", {})
data_sources = result.get("data_sources", {})
generated_at = result.get("generated_at")
reasoning_steps = result.get("reasoning_steps", [])
trade_history = result.get("trade_history", [])

action = str(decision.get("action", "HOLD")).upper()
trend = str(market.get("trend", "SIDEWAYS")).upper()
risk_level = str(risk.get("risk_level", "HIGH")).upper()
confidence = float(decision.get("confidence", 0.0))
current_price = float(market.get("current_price", 0.0))

backend_ai_text = str(news.get("llm_explanation") or news.get("summary") or "").strip()
used_backend_ai = bool(backend_ai_text)
ai_summary = build_ai_insight(news, decision, risk, market)

action_class = action.lower() if action in ("BUY", "SELL", "HOLD") else "hold"

# ── Signal hero ────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="card">
        <div class="section-label">Trading Signal</div>
        <div class="signal-action {action_class}">{action}</div>
        <div class="signal-meta">{decision.get("explanation", "No explanation provided.")}</div>
        <div class="signal-grid">
            <div class="signal-mini">
                <div class="signal-mini-label">Trend</div>
                <div class="signal-mini-value">{trend}</div>
            </div>
            <div class="signal-mini">
                <div class="signal-mini-label">Risk</div>
                <div class="signal-mini-value">{risk_level}</div>
            </div>
            <div class="signal-mini">
                <div class="signal-mini-label">Confidence</div>
                <div class="signal-mini-value">{confidence:.1f}%</div>
            </div>
            <div class="signal-mini">
                <div class="signal-mini-label">Entry Price</div>
                <div class="signal-mini-value">${float(decision.get("entry_price", current_price) or 0):,.2f}</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

render_ai_insight(ai_summary, used_backend_ai)

# ── Key metrics ────────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
with m1:
    render_metric_card("Current Price", f"${current_price:,.2f}", "Latest market price")
with m2:
    render_metric_card("Momentum", f"{float(market.get('momentum_pct', 0)):+.2f}%", "Directional pressure")
with m3:
    render_metric_card("Volatility", f"{float(market.get('volatility_pct', 0)):.2f}%", "Annualized movement")
with m4:
    render_metric_card("Risk Score", f"{int(risk.get('risk_score', 0))}/100", "Model risk score")

# ── Main layout ────────────────────────────────────────────────────────────────
left, right = st.columns([1.8, 1])

with left:
    st.markdown('<div class="section-label">Price Action</div>', unsafe_allow_html=True)
    st.markdown('<div class="card" style="padding:16px;">', unsafe_allow_html=True)
    render_price_chart(market.get("prices", []), result.get("symbol", symbol))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-label">Agent Workflow</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    render_agent_workflow(market, news, risk, decision, kraken_trade)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-label">Reasoning Steps</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    render_reasoning(reasoning_steps)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-label">Confidence</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-sm">', unsafe_allow_html=True)
    render_confidence_gauge(confidence)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-label">Execution</div>', unsafe_allow_html=True)
    render_execution_panel(kraken_trade)

    st.markdown('<div class="section-label">Risk Parameters</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="card-sm">
            <div class="risk-row"><span class="risk-key">Risk Level</span><span class="risk-val">{risk_level}</span></div>
            <div class="risk-row"><span class="risk-key">Position Size</span><span class="risk-val">{risk.get("position_size_pct", "-")}%</span></div>
            <div class="risk-row"><span class="risk-key">Stop Loss</span><span class="risk-val">{risk.get("stop_loss_pct", "-")}%</span></div>
            <div class="risk-row"><span class="risk-key">Take Profit</span><span class="risk-val">{risk.get("take_profit_pct", "-")}%</span></div>
            <div class="risk-row"><span class="risk-key">Risk Score</span><span class="risk-val">{risk.get("risk_score", "-")}/100</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">Portfolio</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="card-sm">
            <div class="risk-row"><span class="risk-key">Value</span><span class="risk-val">${float(portfolio.get("ending_portfolio_value", 0)):,.2f}</span></div>
            <div class="risk-row"><span class="risk-key">PnL</span><span class="risk-val">${float(portfolio.get("pnl_value", 0)):,.2f}</span></div>
            <div class="risk-row"><span class="risk-key">PnL %</span><span class="risk-val">{float(portfolio.get("pnl_pct", 0)):+.2f}%</span></div>
            <div class="risk-row"><span class="risk-key">Max Drawdown</span><span class="risk-val">{float(portfolio.get("max_drawdown_pct", 0)):.2f}%</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── News ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Live News</div>', unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)
render_articles(news.get("articles", []))
st.markdown("</div>", unsafe_allow_html=True)

# ── Expandable sections ────────────────────────────────────────────────────────
with st.expander("Trade History", expanded=False):
    if trade_history:
        st.dataframe(pd.DataFrame(trade_history), use_container_width=True, hide_index=True)
    else:
        st.info("No trade history available.")

with st.expander("Execution Raw Data", expanded=False):
    st.json(kraken_trade or {})

with st.expander("Decision Receipt", expanded=False):
    if receipt:
        st.json(receipt)
    else:
        st.info("No receipt available.")

with st.expander("System Info", expanded=False):
    st.json({
        "generated_at": generated_at,
        "data_sources": data_sources,
        "backend_ai_available": used_backend_ai,
        "news_summary": news.get("summary"),
    })
