# agents/llm_agent/llm_logic.py

import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate as LangPromptTemplate 
from pathlib import Path

# Load API key
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("OPENAI_API_KEY")

# Step 1: Create LLM
llm = ChatOpenAI(api_key=api_key, temperature=0.5)

# Step 2: Prompt template
comprehensive_prompt = PromptTemplate.from_template("""
    You are a financial assistant generating a market briefing based on various data sources.

    Use the following information to answer the user's query:

    Query: {query}
    Company Ticker: {ticker}
    Stock Data: {stock_data}
    Filing Summary: {filing_summary}
    Filing Type: {filing_type}
    Data Source: {data_source}

    Now write a concise, 2-3 sentence answer that combines this information to give the user an update.
    """)

contextual_chain = comprehensive_prompt | llm

# Step 4: Final function
def generate_contextual_brief(data) -> str:
    try:
        response = contextual_chain.invoke({
            "query": data.query,
            "ticker": data.ticker,
            "stock_data": str(data.stock_data),  # Convert dict to string
            "filing_summary": data.filing_summary,
            "filing_type": data.filing_type,
            "data_source": data.data_source
        })
        return response.content
    except Exception as e:
        return f"⚠️ Failed to generate LLM response: {str(e)}"


extraction_prompt = LangPromptTemplate.from_template("""
Extract the stock ticker symbol from this query: "{query}"

Rules:
- Return ONLY the ticker symbol (e.g., AAPL, MSFT, GOOGL)
- If a company name is mentioned, return its ticker symbol
- Common mappings: Apple->AAPL, Microsoft->MSFT, Google/Alphabet->GOOGL, Amazon->AMZN, Tesla->TSLA, Meta/Facebook->META, Nvidia->NVDA
- If no company or ticker is found, return "NONE"
- Return only the ticker, no other text

Query: {query}
Ticker:
""")

extraction_chain = extraction_prompt | llm

def extract_ticker(query: str) -> str:
    result = extraction_chain.invoke({"query": query})
    return result.content.strip()
