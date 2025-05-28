# agent_controller.py
import os
import httpx


API_AGENT_URL = os.getenv("API_AGENT_URL", "http://localhost:8001") + "/stock_data"
LLM_AGENT_URL = os.getenv("LLM_AGENT_URL", "http://localhost:8003") + "/generate_brief"

async def process_query(query: str) -> str:
    # Example logic: if the query has a ticker, fetch stock info, then ask LLM to summarize
    ticker = "AAPL"  # 🔧 For now hardcoded; can extract dynamically later

    async with httpx.AsyncClient() as client:
        # Step 1: Get stock info
        
        stock_resp = await client.post(API_AGENT_URL, json={"symbol": ticker})
        stock_data = stock_resp.json()
        print(stock_data)

        # Step 2: Use Scraper to get fillings and data
        SCRAPING_AGENT_URL = os.getenv("SCRAPING_AGENT_URL", "http://localhost:8004") + "/scrape"

        # Inside your process_query function
        scrape_resp = await client.post(SCRAPING_AGENT_URL, json={"ticker": ticker})
        scraped_data = scrape_resp.json()

        

        # Step 3: Use LLM to generate a summary

        """
        llm_payload = {
            "exposure": "Apple has moderate exposure to global markets with high brand recognition.",
            "earnings": "Q2 earnings showed a 7% YoY increase with strong iPhone sales.",
            "sentiment": "Market sentiment is bullish due to consistent performance."
        }

        # Send to LLM agent
        llm_resp = await client.post(LLM_AGENT_URL, json=llm_payload)"""

        # Now pass scraped_data to LLM agent
        llm_resp = await client.post(LLM_AGENT_URL, json=scraped_data)
        summary = llm_resp.json()["brief"]
        #print(summary)
        


    return summary
