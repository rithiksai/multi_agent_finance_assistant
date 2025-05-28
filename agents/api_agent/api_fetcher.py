# agents/api_agent/api_fetcher.py
import yfinance as yf

def get_stock_info(symbol: str) -> dict:
    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        return {
            "symbol": symbol.upper(),
            "current_price": info.get("currentPrice"),
            "previous_close": info.get("previousClose"),
            "change": round(((info.get("currentPrice") - info.get("previousClose")) / info.get("previousClose")) * 100, 2) if info.get("currentPrice") and info.get("previousClose") else None,
            "volume": info.get("volume"),
            "market_cap": info.get("marketCap"),
            "currency": info.get("currency"),
        }
    except Exception as e:
        return {"error": str(e)}
