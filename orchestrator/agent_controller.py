# agent_controller.py
import os
import httpx
import json
from typing import Dict, Optional, Tuple

# Agent URLs
API_AGENT_URL = os.getenv("API_AGENT_URL", "http://localhost:8001")
LLM_AGENT_URL = os.getenv("LLM_AGENT_URL", "http://localhost:8003")
RETRIEVER_AGENT_URL = os.getenv("RETRIEVER_AGENT_URL", "http://localhost:8004")
SCRAPING_AGENT_URL = "http://localhost:8005"

async def extract_ticker_using_llm(query: str) -> Optional[str]:
    """
    Call the LLM agent to extract a stock ticker from user query.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print(f"🤖 Sending query to LLM for ticker extraction: {query}")
            response = await client.post(
                f"{LLM_AGENT_URL}/extract_ticker",
                json={"query": query}
            )

            if response.status_code == 200:
                data = response.json()
                ticker = data.get("ticker", "").strip().upper()
                
                if ticker and ticker != "NONE" and len(ticker) <= 5:
                    print(f"✅ LLM extracted ticker: {ticker}")
                    return ticker
                else:
                    print("❌ No valid ticker found.")
                    return None
            else:
                print(f"⚠️ Error from LLM agent: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"❌ Exception while calling LLM: {e}")
            return None


async def check_vector_db_for_data(ticker: str, query: str) -> Optional[Dict]:
    """
    Check if we already have relevant data in vector DB.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Search vector DB for relevant data
            response = await client.post(
                f"{RETRIEVER_AGENT_URL}/query",
                json={"query": f"{ticker} {query}"}
            )
            
            if response.status_code == 200:
                results = response.json().get("matches", [])
                if results and len(results) > 0:
                    # Check if results are relevant (high similarity score)
                    if results[0].get("score", 0) > 0.7:  # Threshold for relevance
                        return {
                            "source": "vector_db",
                            "data": results
                        }
            return None
        except Exception as e:
            print(f"Vector DB search failed: {e}")
            return None

async def process_and_store_filing(ticker: str, filing_type: str) -> Tuple[str, int]:
    """
    Process filing through scraping agent and store in vector DB.
    Returns (summary, chunks_stored_count)
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Step 1: Get filing data from scraping agent
        print(f"📄 Fetching {filing_type} for {ticker}...")
        
        scraping_response = await client.post(
            f"{SCRAPING_AGENT_URL}/process",
            json={
                "ticker": ticker,
                "filing_type": filing_type
            }
        )
        
        if scraping_response.status_code != 200:
            raise Exception(f"Scraping failed: {scraping_response.text}")
        
        scraping_data = scraping_response.json()
        
        if scraping_data["status"] != "success":
            raise Exception(f"Scraping failed: {scraping_data.get('message')}")
        
        summary = scraping_data.get("summary", "")
        chunks = scraping_data.get("chunks", [])
        
        print(f"✅ Got summary and {len(chunks)} chunks")
        
        # Step 2: Store chunks in vector DB
        stored_count = 0
        for chunk in chunks:
            try:
                store_response = await client.post(
                    f"{RETRIEVER_AGENT_URL}/store",
                    json={
                        "doc_id": chunk["doc_id"],
                        "text": chunk["text"]
                    }
                )
                if store_response.status_code == 200:
                    result = store_response.json()
                    if result.get("status") == "success":
                        stored_count += 1
            except Exception as e:
                print(f"Failed to store chunk: {e}")
        
        print(f"💾 Stored {stored_count}/{len(chunks)} chunks in vector DB")
        
        return summary, stored_count

async def process_query(query: str) -> str:
    """
    Main orchestration logic:
    1. Extract ticker from query using LLM
    2. Check vector DB for existing data
    3. If not found, fetch and process filing
    4. Get real-time stock data
    5. Generate comprehensive response using LLM
    """
    
    try:
        # Step 1: Extract ticker from query using LLM
        ticker = await extract_ticker_using_llm(query)
        if not ticker:
            return "I couldn't identify a stock ticker in your query. Please mention a specific company or stock symbol."
        
        print(f"🎯 Detected ticker: {ticker}")
        
        # Step 2: Fixed filing type - always use 10-K
        filing_type = "10-K"
        print(f"📋 Using filing type: {filing_type} (annual report)")
        
        async with httpx.AsyncClient(timeout=90.0) as client:
            # Step 3: Get real-time stock data
            print(f"📈 Fetching real-time data for {ticker}...")
            stock_resp = await client.post(
                f"{API_AGENT_URL}/stock_data",
                json={"symbol": ticker}
            )
            stock_data = stock_resp.json()
            
            # Step 4: Check if we have filing data in vector DB
            print(f"🔍 Checking vector DB for existing data...")
            vector_data = await check_vector_db_for_data(ticker, query)
            
            filing_summary = ""
            
            if vector_data:
                print("✅ Found relevant data in vector DB")
                # Extract text from vector DB results
                filing_summary = "\n".join([
                    result.get("text", "") 
                    for result in vector_data["data"][:3]  # Top 3 results
                ])
            else:
                print("📥 No recent data found, fetching new filing...")
                # Process new filing
                try:
                    filing_summary, chunks_stored = await process_and_store_filing(ticker, filing_type)
                    print(f"✅ Processing complete: {chunks_stored} chunks stored")
                except Exception as e:
                    print(f"⚠️ Filing processing failed: {e}")
                    filing_summary = f"Unable to fetch {filing_type} filing. Using real-time data only."
            
            # Step 5: Prepare context for LLM
            llm_context = {
                "query": query,
                "ticker": ticker,
                "stock_data": stock_data,
                "filing_summary": filing_summary[:3000],  # Limit to 3000 chars
                "filing_type": filing_type,
                "data_source": "vector_db" if vector_data else "fresh_scrape"
            }
            
            # Step 6: Generate final response using LLM
            print("🤖 Generating comprehensive response...")
            llm_resp = await client.post(
                f"{LLM_AGENT_URL}/generate_brief",
                json=llm_context
            )
            
            if llm_resp.status_code == 200:
                return llm_resp.json()["brief"]
            else:
                # Fallback response if LLM fails
                return f"""
                    Based on the latest data for {ticker}:

                    **Current Stock Price**: ${stock_data.get('current_price', 'N/A')}
                    **Daily Change**: {stock_data.get('change_percent', 'N/A')}%

                    {filing_summary[:500] if filing_summary else 'Filing data not available.'}

                    *Note: This is a simplified response as the AI summary service is temporarily unavailable.*
                    """
                                
    except Exception as e:
        print(f"❌ Error in orchestrator: {e}")
        return f"I encountered an error processing your request: {str(e)}. Please try again or rephrase your query."
