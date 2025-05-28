# agents/llm_agent/llm_service.py

from fastapi import FastAPI
from pydantic import BaseModel
from .llm_logic import generate_brief

app = FastAPI(title="Language Agent", description="LLM-powered narrative generator")

# This is a schema to parse the incoming json into a python object and also valisates the data (data model)
class BriefRequest(BaseModel):
    exposure: str
    earnings: str
    sentiment: str

@app.post("/generate_brief")
def get_market_brief(data: BriefRequest):
    result = generate_brief(data.exposure, data.earnings, data.sentiment)
    return {"brief": result}
