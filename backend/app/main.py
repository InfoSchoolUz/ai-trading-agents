import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.orchestrator.trading_brain import TradingBrain
from app.schemas.trade import AnalyzeRequest, OrchestratorResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

brain: TradingBrain | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global brain
    logger.info("Starting TradingBrain...")
    brain = TradingBrain()
    yield
    logger.info("Stopping TradingBrain...")


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception on %s: %s", request.url, exc, exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "status": "ok",
        "env": settings.APP_ENV,
        "market_data": "live",
        "news_data": "live_public_rss",
        "trade_execution": f"kraken_cli_{settings.KRAKEN_MODE.lower()}" if settings.ENABLE_EXECUTION else "disabled",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "brain_ready": brain is not None,
        "market_data_source": settings.MARKET_DATA_SOURCE,
        "news_data_source": settings.NEWS_DATA_SOURCE,
        "execution_enabled": settings.ENABLE_EXECUTION,
        "execution_mode": settings.KRAKEN_MODE.lower(),
        "execution_cli_path": settings.KRAKEN_CLI_PATH,
    }


@app.post("/analyze", response_model=OrchestratorResponse)
def analyze_trade(req: AnalyzeRequest):
    if brain is None:
        raise HTTPException(status_code=503, detail="Trading engine is not ready yet.")
    try:
        return brain.run(symbol=req.symbol, period=req.period, interval=req.interval)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Analysis failed for %s: %s", req.symbol, exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed due to an internal error.") from exc
