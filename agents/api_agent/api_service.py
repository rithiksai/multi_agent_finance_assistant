# agents/api_agent/api_service.py

from pydantic import BaseModel
from fastapi import FastAPI, Query
from api_fetcher import get_stock_info

app = FastAPI(title="API Agent", description="Fetches real-time stock data using yfinance")

class StockRequest(BaseModel):
    symbol: str


@app.post("/stock_data")
def stock_data(request: StockRequest):
    result = get_stock_info(request.symbol)
    return result
