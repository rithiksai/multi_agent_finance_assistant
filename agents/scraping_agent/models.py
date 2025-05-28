from pydantic import BaseModel

class ScrapeRequest(BaseModel):
    ticker: str

class ScrapeResponse(BaseModel):
    earnings: str
    exposure: str
    sentiment: str
