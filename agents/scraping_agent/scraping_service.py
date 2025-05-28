from fastapi import FastAPI
from .models import ScrapeRequest, ScrapeResponse
from .scraper import scrape_company_info

app = FastAPI(title="Scraping Agent", description="Fetches structured info from filings or news")

@app.post("/scrape", response_model=ScrapeResponse)
def scrape(req: ScrapeRequest):
    data = scrape_company_info(req.ticker)
    return ScrapeResponse(**data)
