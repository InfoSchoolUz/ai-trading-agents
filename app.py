import streamlit as st
import requests
import pandas as pd

# 🔗 BACKEND URL (sening Railway API)
API_URL = "https://ai-trading-agents-production.up.railway.app/analyze"

st.set_page_config(
    page_title="AI Trading Agent",
    page_icon="📈",
    layout="centered"
)

# 🎨 HEADER
st.title("📈 AI Trading Agent")
st.markdown("Analyze market trends using AI-powered signals")

# 📥 INPUTS
symbol = st.text_input("Symbol", "BTC-USD")
interval = st.selectbox("Interval", ["1d", "1h", "15m"])
period = st.selectbox("Period", ["1mo", "3mo", "6mo"])

# 🚀 BUTTON
if st.button("Analyze 🚀"):

    payload = {
        "symbol": symbol,
        "interval": interval,
        "period": period
    }

    with st.spinner("Analyzing market..."):

        try:
            res = requests.post(API_URL, json=payload, timeout=30)
            data = res.json()

            # ✅ SUCCESS
            if res.status_code == 200:

                st.success("Analysis Complete ✅")

                market = data.get("market", {})
                trend = data.get("trend", "UNKNOWN")

                # 📊 METRICS
                col1, col2, col3 = st.columns(3)

                col1.metric("Price", f"{market.get('current_price', 'N/A')}")
                col2.metric("RSI", f"{market.get('rsi_14', 'N/A')}")
                col3.metric("MACD", f"{market.get('macd', 'N/A')}")

                st.divider()

                # 📈 TREND
                if trend == "BULLISH":
                    st.success(f"🔥 Trend: {trend}")
                elif trend == "BEARISH":
                    st.error(f"📉 Trend: {trend}")
                else:
                    st.warning(f"⚖️ Trend: {trend}")

                # 📊 INDICATORS TABLE
                st.subheader("📊 Indicators")

                indicators = {
                    "SMA 5": market.get("sma_5"),
                    "SMA 10": market.get("sma_10"),
                    "SMA 20": market.get("sma_20"),
                    "Momentum %": market.get("momentum_pct"),
                    "Volatility %": market.get("volatility_pct"),
                    "Support": market.get("support"),
                    "Resistance": market.get("resistance"),
                }

                df = pd.DataFrame(
                    indicators.items(), columns=["Indicator", "Value"]
                )

                st.table(df)

            # ❌ ERROR FROM API
            else:
                st.error("API Error ❌")
                st.write(data)

        # ❌ CONNECTION ERROR
        except Exception as e:
            st.error("Connection Error 🚨")
            st.write(str(e))

# 📌 FOOTER
st.markdown("---")
st.markdown("🚀 Powered by AI Trading Agents")
