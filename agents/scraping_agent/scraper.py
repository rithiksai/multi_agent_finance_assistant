def scrape_company_info(ticker: str) -> dict:
    # TODO: Real scraping logic for SEC filings or news articles
    return {
        "earnings": f"{ticker} reported quarterly earnings of $2.15/share.",
        "exposure": f"{ticker} has high exposure to the Asian market.",
        "sentiment": f"Recent news articles reflect a positive sentiment about {ticker}."
    }
