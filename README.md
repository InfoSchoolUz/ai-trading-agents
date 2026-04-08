# 📈 AI Trading Agents

An AI-powered trading analysis system that combines market data, news sentiment, risk modeling, and Google Gemini AI to generate actionable trading insights.

---

## 🚀 Features

* 📊 Market analysis (trend, price, volatility)
* 📰 News sentiment analysis from live headlines
* 🤖 AI-powered insights using Google Gemini
* ⚖️ Risk management (position sizing, stop-loss, take-profit)
* 🧠 Decision engine (BUY / SELL / HOLD)
* 📉 Portfolio tracking (PNL, drawdown)
* 🔁 Trade execution simulation (paper trading)
* 🎨 Modern dashboard UI (Streamlit)

---

## 🧠 How It Works

Multi-agent architecture:

Market Data → News Analysis → Risk Assessment → Decision Engine → Execution

### Agents:

* **Market Agent** → analyzes price & trend
* **News Agent** → extracts sentiment from news
* **Risk Agent** → calculates risk & position sizing
* **Trading Brain** → makes final decision

---

## 🤖 AI Integration

Uses Google Gemini API to generate:

* AI trading insights
* Market sentiment explanation

If AI is disabled, system automatically falls back to standard logic.

---

## 🛠️ Tech Stack

* Backend: FastAPI
* Frontend: Streamlit
* AI: Google Gemini (google-generativeai)
* Data: yfinance, RSS feeds
* Visualization: Plotly
* Language: Python

---

## ⚙️ Installation

### 1. Clone repo

```bash
git clone https://github.com/YOUR_USERNAME/ai-trading-agents.git
cd ai-trading-agents
```

---

### 2. Create virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Setup

Create `backend/.env` file:

```env
GOOGLE_API_KEY=your_api_key
ENABLE_LLM_EXPLANATIONS=true
GEMINI_MODEL=gemini-2.5-flash

ALLOWED_ORIGINS=["http://localhost:8501","http://127.0.0.1:8501"]

REQUEST_TIMEOUT_SECONDS=12
NEWS_MAX_ARTICLES=8

KRAKEN_MODE=paper
ENABLE_EXECUTION=true

DEFAULT_SYMBOL=BTCUSD
DEFAULT_USD_SIZE=10
EXECUTION_CASH_FRACTION=0.10
```

---

## ▶️ Run Application

### Start backend

```bash
cd backend
uvicorn app.main:app --reload
```

---

### Start frontend

```bash
streamlit run streamlit_app_ai_ready.py
```

---

## 🌐 Access

* Frontend: http://localhost:8501
* Backend: http://127.0.0.1:8000
* Health: http://127.0.0.1:8000/health

---

## 📊 Output

* Trading signal (BUY / SELL / HOLD)
* Confidence score
* AI-generated explanation
* News sentiment
* Risk analysis
* Portfolio metrics

---

## ⚠️ Notes

* AI requires valid Google API key
* System works without AI (fallback mode)
* Trading runs in paper mode by default

---

## 📁 Project Structure

```
backend/
  app/
    agents/
    services/
    schemas/
    core/
    orchestrator/

frontend/
  streamlit_app.py
```

---

## 👨‍💻 Author

Azamat Madrimov

---

## 🚀 Future Plans

* AI chat assistant
* Real-time AI streaming
* Advanced strategies
* Multi-exchange support
* Cloud deployment

---
