# agents/llm_agent/llm_service.py

from fastapi import FastAPI
from pydantic import BaseModel
from llm_logic import generate_contextual_brief,extract_ticker

app = FastAPI(title="Language Agent", description="LLM-powered narrative generator")

class TickerRequest(BaseModel):
    query: str
    mode: str = "extraction"  # Optional, supports orchestrator's format


# This is a schema to parse the incoming json into a python object and also validates the data (data model)
class BriefContextRequest(BaseModel):
    query: str
    ticker: str
    stock_data: dict
    filing_summary: str
    filing_type: str
    data_source: str

@app.post("/generate_brief")
def get_comprehensive_brief(data: BriefContextRequest):
    result = generate_contextual_brief(data)
    return {"brief": result}


@app.post("/extract_ticker")
def extract_ticker_route(req: TickerRequest):
    ticker = extract_ticker(req.query)
    return {"ticker": ticker}

