# agents/api_agent/api_service.py

from pydantic import BaseModel
from fastapi import FastAPI, Query
from api_fetcher import get_stock_info
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API Agent", description="Fetches real-time stock data using yfinance")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StockRequest(BaseModel):
    symbol: str


@app.post("/stock_data")
def stock_data(request: StockRequest):
    result = get_stock_info(request.symbol)
    return result
