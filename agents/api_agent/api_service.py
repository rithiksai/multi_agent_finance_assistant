# agents/api_agent/api_service.py

from fastapi import FastAPI, Query
from .api_fetcher import get_stock_info

app = FastAPI(title="API Agent", description="Fetches real-time stock data using yfinance")

@app.get("/stock_data")
def stock_data(symbol: str = Query(..., description="Ticker symbol like AAPL, TSMC")):
    result = get_stock_info(symbol)
    return result
