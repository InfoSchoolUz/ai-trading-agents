from __future__ import annotations

import os
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(
    page_title="AI Trading Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEFAULT_BACKEND_URL = "http://127.0.0.1:8000"

POPULAR_TICKERS = {
    "Crypto": {
        "Bitcoin": "BTC-USD",
        "Ethereum": "ETH-USD",
        "Solana": "SOL-USD",
        "BNB": "BNB-USD",
        "Dogecoin": "DOGE-USD",
        "XRP": "XRP-USD",
    },
    "Stocks": {
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "NVIDIA": "NVDA",
        "Tesla": "TSLA",
        "Google": "GOOGL",
        "Amazon": "AMZN",
    },
    "Indexes": {
        "S&P 500": "^GSPC",
        "Dow Jones": "^DJI",
        "Nasdaq": "^IXIC",
        "VIX": "^VIX",
    },
    "Forex": {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "USDJPY=X",
    },
    "Commodities": {
        "Gold": "GC=F",
        "Silver": "SI=F",
        "Oil": "CL=F",
    },
    "Custom": {
        "Manual input": "__custom__",
    },
}

PERIODS = ["1mo", "3mo", "6mo", "1y"]
INTERVALS = ["1d", "1wk", "1mo"]


def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background: #0b1220;
            color: #f8fafc;
        }

        .block-container {
            max-width: 1400px;
            padding-top: 4.5rem;
            padding-bottom: 2rem;
        }

        [data-testid="stSidebar"] {
            background: #0f172a;
            border-right: 1px solid rgba(148,163,184,0.12);
        }

        [data-testid="stSidebar"] * {
            color: #e5e7eb !important;
        }

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {
            background: #111827 !important;
            border: 1px solid rgba(148,163,184,0.16) !important;
            border-radius: 12px !important;
            color: white !important;
        }

        label, .stSelectbox label, .stTextInput label {
            color: #cbd5e1 !important;
            font-weight: 600 !important;
        }

        div.stButton > button {
            width: 100%;
            border: 0;
            border-radius: 12px;
            padding: 0.85rem 1rem;
            font-weight: 700;
            color: white;
            background: #2563eb;
        }

        div.stButton > button:hover {
            background: #1d4ed8;
        }

        .page-title {
            font-size: 2rem;
            font-weight: 800;
            color: #f8fafc;
            margin-bottom: 0.25rem;
             margin-bottom: 0.35rem;
             line-height: 1.15;
        }

        .page-subtitle {
            color: #94a3b8;
            font-size: 1rem;
            margin-bottom: 1.5rem;
            line-height: 1.6;
        }

        .empty-state {
            border: 1px solid rgba(148,163,184,0.12);
            border-radius: 18px;
            background: #0f172a;
            padding: 56px 28px;
            text-align: center;
            margin-top: 12px;
        }

        .empty-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 10px;
        }

        .empty-subtitle {
            font-size: 1rem;
            color: #94a3b8;
            line-height: 1.7;
        }

        .hero-card,
        .content-card,
        .info-card,
        .metric-card {
            border: 1px solid rgba(148,163,184,0.12);
            border-radius: 18px;
            background: #0f172a;
            box-shadow: none;
        }

        .hero-card {
            padding: 22px;
            margin-bottom: 16px;
        }

        .content-card,
        .info-card {
            padding: 18px;
            margin-bottom: 16px;
        }

        .metric-card {
            padding: 18px;
        }

        .metric-label {
            font-size: 0.78rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .metric-value {
            font-size: 1.8rem;
            font-weight: 800;
            color: #f8fafc;
            line-height: 1.05;
        }

        .metric-sub {
            margin-top: 8px;
            color: #94a3b8;
            font-size: 0.9rem;
        }

        .section-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #f8fafc;
            margin: 6px 0 12px 0;
        }

        .signal-box {
            border: 1px solid rgba(148,163,184,0.12);
            border-radius: 18px;
            background: #111827;
            padding: 18px;
        }

        .signal-action {
            font-size: 2rem;
            font-weight: 800;
            color: #f8fafc;
            margin-bottom: 6px;
        }

        .signal-meta {
            color: #94a3b8;
            font-size: 0.96rem;
            line-height: 1.6;
        }

        .signal-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-top: 14px;
        }

        .signal-mini {
            border: 1px solid rgba(148,163,184,0.12);
            border-radius: 14px;
            background: #0b1324;
            padding: 12px;
        }

        .signal-mini-label {
            font-size: 0.72rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 700;
            margin-bottom: 6px;
        }

        .signal-mini-value {
            font-size: 1rem;
            color: #f8fafc;
            font-weight: 700;
        }

        .reason-step {
            border: 1px solid rgba(148,163,184,0.10);
            border-radius: 12px;
            background: #111827;
            padding: 12px;
            color: #e5e7eb;
            margin-bottom: 10px;
        }

        .news-item {
            border-bottom: 1px solid rgba(148,163,184,0.10);
            padding: 12px 0;
        }

        .news-item:last-child {
            border-bottom: none;
        }

        .news-title {
            font-size: 0.98rem;
            font-weight: 600;
            color: #f8fafc;
            margin-bottom: 4px;
        }

        .news-meta {
            color: #94a3b8;
            font-size: 0.9rem;
        }

        .footer-note {
            color: #64748b;
            text-align: center;
            margin-top: 14px;
            font-size: 0.9rem;
        }

        .execution-status-ok {
            color: #22c55e;
            font-weight: 700;
        }

        .execution-status-warn {
            color: #f59e0b;
            font-weight: 700;
        }

        .execution-status-bad {
            color: #ef4444;
            font-weight: 700;
        }

        .workflow-step {
            border: 1px solid rgba(148,163,184,0.10);
            border-radius: 12px;
            background: #111827;
            padding: 12px;
            color: #e5e7eb;
            margin-bottom: 10px;
        }

        .workflow-step-title {
            font-size: 0.82rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 700;
            margin-bottom: 6px;
        }

        .workflow-step-value {
            font-size: 0.98rem;
            color: #f8fafc;
            font-weight: 600;
            line-height: 1.5;
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
        raise RuntimeError(f"Backend xatosi: {detail}")

    return response.json()


def render_metric_card(label: str, value: str, sub: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_price_chart(prices: list[float], symbol: str) -> None:
    if not prices:
        st.info("Narx ma'lumotlari topilmadi.")
        return

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(range(1, len(prices) + 1)),
            y=prices,
            mode="lines",
            name=symbol,
            line=dict(width=2),
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.12)",
        )
    )
    fig.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0b1324",
        font=dict(color="#e5e7eb"),
        showlegend=False,
        xaxis=dict(showgrid=True, gridcolor="rgba(148,163,184,0.08)", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(148,163,184,0.08)", zeroline=False),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_confidence_gauge(confidence: float) -> None:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=confidence,
            number={"suffix": "%", "font": {"size": 34, "color": "#f8fafc"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#94a3b8"},
                "bar": {"color": "#2563eb"},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 1,
                "bordercolor": "rgba(148,163,184,0.14)",
                "steps": [
                    {"range": [0, 35], "color": "rgba(239,68,68,0.20)"},
                    {"range": [35, 65], "color": "rgba(250,204,21,0.18)"},
                    {"range": [65, 100], "color": "rgba(34,197,94,0.18)"},
                ],
            },
            title={"text": "Confidence", "font": {"size": 18, "color": "#cbd5e1"}},
        )
    )
    fig.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)


def render_reasoning(steps: list[str]) -> None:
    if not steps:
        st.info("Reasoning ma'lumotlari topilmadi.")
        return
    for idx, step in enumerate(steps, start=1):
        st.markdown(
            f'<div class="reason-step"><b>Step {idx}:</b> {step}</div>',
            unsafe_allow_html=True,
        )


def render_articles(articles: list[dict[str, Any]]) -> None:
    if not articles:
        st.info("Yangiliklar topilmadi.")
        return

    for article in articles:
        title = article.get("title", "Untitled")
        link = article.get("link", "")
        publisher = article.get("publisher", "Unknown")
        published = article.get("published_at") or "Unknown time"
        sentiment = float(article.get("sentiment_score", 0.0))

        title_html = (
            f'<a href="{link}" target="_blank" style="color:#f8fafc;text-decoration:none;">{title}</a>'
            if link else title
        )

        st.markdown(
            f"""
            <div class="news-item">
                <div class="news-title">{title_html}</div>
                <div class="news-meta">{publisher} · {published} · sentiment {sentiment:+.2f}</div>
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
        f"AI summary is unavailable from the backend, so this fallback insight was generated in the UI. "
        f"Market trend is {trend}, current price is ${current_price:,.2f}, momentum is {momentum:+.2f}% and volatility is {volatility:.2f}%. "
        f"News sentiment is {sentiment_label} ({sentiment_score:+.2f}), which looks {direction}. "
        f"The system decision is {action} with {confidence:.1f}% confidence under {risk_level} risk conditions."
    )


def render_ai_insight(ai_summary: str, used_backend_ai: bool) -> None:
    badge = "LIVE AI" if used_backend_ai else "UI FALLBACK"
    badge_color = "#22c55e" if used_backend_ai else "#f59e0b"

    st.markdown('<div class="section-title">AI Insight</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="content-card">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:10px;">
                <div style="font-size:1.05rem;font-weight:700;color:#f8fafc;">Market Narrative</div>
                <div style="padding:6px 10px;border-radius:999px;background:rgba(148,163,184,0.10);border:1px solid rgba(148,163,184,0.14);color:{badge_color};font-size:0.78rem;font-weight:800;letter-spacing:0.06em;">{badge}</div>
            </div>
            <div style="color:#e5e7eb; line-height:1.75; font-size:1rem;">
                {ai_summary}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_execution_status(kraken_trade: dict[str, Any] | None) -> tuple[str, str]:
    if not kraken_trade:
        return "Unknown", "execution-status-warn"

    if kraken_trade.get("executed"):
        return "Executed", "execution-status-ok"

    if kraken_trade.get("error"):
        return "Failed", "execution-status-bad"

    return "Skipped", "execution-status-warn"


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
    exec_action = kraken_trade.get("action", action) if kraken_trade else action

    return [
        ("Observed market", f"Market data collected. Trend detected: {trend}."),
        ("Analyzed sentiment", f"News sentiment: {sentiment_label} ({sentiment_score:+.2f})."),
        ("Assessed risk", f"Risk level: {risk_level}. Risk score: {risk_score}."),
        ("Made decision", f"Decision: {action} with {confidence:.1f}% confidence."),
        ("Attempted execution", f"Execution status: {exec_status}. Mode: {exec_mode}. Action: {exec_action}."),
        ("Logged outcome", str(exec_note)),
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
                <div class="workflow-step-title">{title}</div>
                <div class="workflow-step-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_execution_panel(kraken_trade: dict[str, Any] | None) -> None:
    status, status_class = get_execution_status(kraken_trade)

    if not kraken_trade:
        st.markdown(
            """
            <div class="info-card">
                <div><b>Status:</b> <span class="execution-status-warn">Unknown</span></div>
                <div style="margin-top:8px;">Execution data topilmadi.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    mode = kraken_trade.get("mode", "-")
    action = kraken_trade.get("action", "-")
    volume = kraken_trade.get("volume", 0)
    note = kraken_trade.get("note", "-")
    error = kraken_trade.get("error")

    html = f"""
    <div class="info-card">
        <div><b>Status:</b> <span class="{status_class}">{status}</span></div>
        <div style="margin-top:8px;"><b>Mode:</b> {mode}</div>
        <div style="margin-top:8px;"><b>Action:</b> {action}</div>
        <div style="margin-top:8px;"><b>Volume:</b> {volume}</div>
        <div style="margin-top:8px;"><b>Note:</b> {note}</div>
    """

    if error:
        html += f'<div style="margin-top:8px;"><b>Error:</b> {error}</div>'

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


if "analyzed" not in st.session_state:
    st.session_state.analyzed = False

if "result" not in st.session_state:
    st.session_state.result = None

if "last_error" not in st.session_state:
    st.session_state.last_error = None

inject_css()
backend_url = get_backend_url()

with st.sidebar:
    st.markdown("## AI Trading Terminal")

    category = st.selectbox("Category", list(POPULAR_TICKERS.keys()), index=0)
    asset_name = st.selectbox("Asset", list(POPULAR_TICKERS[category].keys()))
    asset_value = POPULAR_TICKERS[category][asset_name]

    if asset_value == "__custom__":
        symbol = st.text_input("Custom symbol", value="BTC-USD").strip().upper()
    else:
        symbol = asset_value

    period = st.selectbox("Period", PERIODS, index=1)
    interval = st.selectbox("Interval", INTERVALS, index=0)

    analyze_clicked = st.button("Analyze", use_container_width=True)
    reset_clicked = st.button("Reset", use_container_width=True)

if reset_clicked:
    st.session_state.analyzed = False
    st.session_state.result = None
    st.session_state.last_error = None
    st.rerun()

try:
    _ = get_health(backend_url)
except Exception as exc:
    st.error(f"Backend bilan ulanishda xato: {exc}")
    st.stop()

if analyze_clicked:
    try:
        with st.spinner(f"{symbol} bo‘yicha tahlil ishlayapti..."):
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

st.markdown('<div class="page-title">AI Trading Terminal</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Market analysis and decision support</div>', unsafe_allow_html=True)

if not st.session_state.analyzed or not st.session_state.result:
    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-title">Choose an asset and run analysis</div>
            <div class="empty-subtitle">
                Chap tomondan asset, period va interval tanlang. Natijalar analizdan keyin shu sahifada chiqadi.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

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

st.markdown(
    f"""
    <div class="hero-card">
        <div class="section-title">Signal</div>
        <div class="signal-box">
            <div class="signal-action">{action}</div>
            <div class="signal-meta">{decision.get("explanation", "-")}</div>
            <div class="signal-row">
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
                    <div class="signal-mini-label">Entry</div>
                    <div class="signal-mini-value">${float(decision.get("entry_price", current_price) or 0):,.2f}</div>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

render_ai_insight(ai_summary, used_backend_ai)

m1, m2, m3, m4 = st.columns(4)
with m1:
    render_metric_card("Current Price", f"${current_price:,.2f}", "Latest market price")
with m2:
    render_metric_card("Momentum", f"{float(market.get('momentum_pct', 0)):+.2f}%", "Directional pressure")
with m3:
    render_metric_card("Volatility", f"{float(market.get('volatility_pct', 0)):.2f}%", "Annualized movement")
with m4:
    render_metric_card("Risk Score", f"{int(risk.get('risk_score', 0))}", "Model score")

left, right = st.columns([1.8, 1])

with left:
    st.markdown('<div class="section-title">Price Action</div>', unsafe_allow_html=True)
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    render_price_chart(market.get("prices", []), result.get("symbol", symbol))
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Agent Workflow</div>', unsafe_allow_html=True)
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    render_agent_workflow(market, news, risk, decision, kraken_trade)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Reasoning</div>', unsafe_allow_html=True)
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    render_reasoning(reasoning_steps)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-title">Confidence</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    render_confidence_gauge(confidence)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Execution</div>', unsafe_allow_html=True)
    render_execution_panel(kraken_trade)

    st.markdown('<div class="section-title">Risk</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="info-card">
            <div><b>Level:</b> {risk_level}</div>
            <div><b>Position Size:</b> {risk.get("position_size_pct", "-")}%</div>
            <div><b>Stop Loss:</b> {risk.get("stop_loss_pct", "-")}%</div>
            <div><b>Take Profit:</b> {risk.get("take_profit_pct", "-")}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">Portfolio</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="info-card">
            <div><b>Portfolio Value:</b> ${float(portfolio.get("ending_portfolio_value", 0)):,.2f}</div>
            <div><b>PNL:</b> ${float(portfolio.get("pnl_value", 0)):,.2f}</div>
            <div><b>PNL %:</b> {float(portfolio.get("pnl_pct", 0)):+.2f}%</div>
            <div><b>Max Drawdown:</b> {float(portfolio.get("max_drawdown_pct", 0)):.2f}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="section-title">News</div>', unsafe_allow_html=True)
st.markdown('<div class="content-card">', unsafe_allow_html=True)
render_articles(news.get("articles", []))
st.markdown('</div>', unsafe_allow_html=True)

with st.expander("Trade history", expanded=False):
    if trade_history:
        st.dataframe(pd.DataFrame(trade_history), use_container_width=True, hide_index=True)
    else:
        st.info("Trade history topilmadi.")

with st.expander("Execution raw", expanded=False):
    st.json(kraken_trade or {})

with st.expander("Decision receipt", expanded=False):
    if receipt:
        st.json(receipt)

with st.expander("System details", expanded=False):
    st.json(
        {
            "generated_at": generated_at,
            "data_sources": data_sources,
            "kraken_trade": kraken_trade,
            "backend_ai_available": used_backend_ai,
            "news_summary": news.get("summary"),
            "news_llm_explanation": news.get("llm_explanation"),
        }
    )

st.markdown('<div class="footer-note">AI Trading Terminal</div>', unsafe_allow_html=True)