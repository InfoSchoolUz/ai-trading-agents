from __future__ import annotations

import os
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ================= CONFIG =================

st.set_page_config(
    page_title="AI Trading Agents",
    page_icon="📈",
    layout="wide"
)

# Auto refresh (10 sekund)
st_autorefresh(interval=10000, key="refresh")

# Local dev (comment)
# DEFAULT_BACKEND_URL = "http://127.0.0.1:8000"

# Production
DEFAULT_BACKEND_URL = "https://ai-trading-agents-production.up.railway.app"


def get_backend_url():
    return os.getenv("BACKEND_URL", DEFAULT_BACKEND_URL)


# ================= SIDEBAR =================

with st.sidebar:
    st.markdown(
        """
        <div style="font-size:20px; font-weight:700;">
            ⬡ AI <span style="color:#3b82f6;">Trading</span> Agents
        </div>
        <div style="font-size:12px; color:#64748b; margin-top:6px;">
            👨‍💻 Developed by <b>Azamat Madrimov</b>
        </div>
        <hr>
        """,
        unsafe_allow_html=True
    )

    symbol = st.text_input("Symbol", "BTC-USD")
    period = st.selectbox("Period", ["1mo", "3mo", "6mo"])
    interval = st.selectbox("Interval", ["1d", "1h"])

    run = st.button("▶ Run Analysis")


# ================= MAIN =================

st.title("📈 AI Trading Dashboard")

if run:

    try:
        with st.spinner("Analyzing..."):

            response = requests.post(
                f"{get_backend_url()}/analyze",
                json={
                    "symbol": symbol,
                    "period": period,
                    "interval": interval
                },
                timeout=60
            )

            if response.status_code != 200:
                st.error(response.text)
                st.stop()

            data = response.json()

    except Exception as e:
        st.error(f"Connection error: {e}")
        st.stop()

    # ================= DATA =================

    market = data.get("market", {})
    decision = data.get("decision", {})
    risk = data.get("risk", {})

    price = market.get("current_price", 0)
    trend = market.get("trend", "UNKNOWN")
    rsi = market.get("rsi_14", 0)
    macd = market.get("macd", 0)

    action = decision.get("action", "HOLD")
    confidence = decision.get("confidence", 0)

    # ================= UI =================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Price", f"${price:,.2f}")
    col2.metric("RSI", f"{rsi}")
    col3.metric("MACD", f"{macd}")
    col4.metric("Confidence", f"{confidence:.1f}%")

    st.divider()

    # SIGNAL
    if action == "BUY":
        st.success(f"🔥 BUY SIGNAL")
    elif action == "SELL":
        st.error(f"📉 SELL SIGNAL")
    else:
        st.warning(f"⚖️ HOLD")

    st.write(f"Trend: {trend}")

    # RISK
    st.subheader("Risk")
    st.write(risk)

    # RAW DATA
    with st.expander("Full Data"):
        st.json(data)

else:
    st.info("Select asset and click Run Analysis")