# agents/scraping_agent/scraping_service.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from .scraper import SECScrapingAgent

app = FastAPI(title="Scraping Agent", description="Downloads and processes SEC filings")

# Initialize the scraping agent
scraper = SECScrapingAgent()

class FilingRequest(BaseModel):
    ticker: str
    filing_type: str = "10-K"

class FilingResponse(BaseModel):
    status: str
    ticker: str
    filing_type: str
    summary: Optional[str] = None
    chunks: Optional[List[Dict]] = None
    message: Optional[str] = None

@app.get("/")
async def root():
    return {
        "agent": "SEC Scraping Agent",
        "version": "1.0.0",
        "endpoints": [
            "/process - Process filing and return summary + chunks"
        ]
    }

@app.post("/process", response_model=FilingResponse)
async def process_filing(request: FilingRequest):
    """
    Process SEC filing: extract insights and prepare chunks
    Returns both LLM summary and chunks for vector DB
    """
    try:
        # Extract insights (this also downloads if needed)
        result = scraper.extract_insights(request.ticker, request.filing_type)
        
        if result["status"] != "success":
            return FilingResponse(
                status="error",
                ticker=request.ticker,
                filing_type=request.filing_type,
                message=result.get("message", "Failed to extract insights")
            )
        
        # Read the summary for LLM
        with open(result["summary_path"], 'r', encoding='utf-8') as f:
            summary_text = f.read()
        
        # Prepare chunks for vector DB
        chunks = scraper.prepare_for_vector_db(request.ticker, request.filing_type)
        
        return FilingResponse(
            status="success",
            ticker=request.ticker,
            filing_type=request.filing_type,
            summary=summary_text,
            chunks=chunks
        )
        
    except Exception as e:
        return FilingResponse(
            status="error",
            ticker=request.ticker,
            filing_type=request.filing_type,
            message=str(e)
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "scraping"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)