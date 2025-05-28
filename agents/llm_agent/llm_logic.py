# agents/llm_agent/llm_logic.py

import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from pathlib import Path

# Load API key
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("OPENAI_API_KEY")

# Step 1: Create LLM
llm = ChatOpenAI(api_key=api_key, temperature=0.5)

# Step 2: Prompt template
template = """
You are a financial assistant generating a morning market briefing.

Here is the data:
- Asia tech exposure: {exposure}%
- Earnings surprises: {earnings}
- Market sentiment: {sentiment}

Write a short 2-sentence market brief using this info.
"""

prompt = PromptTemplate.from_template(template)

# Step 3: Chain = prompt | LLM (this is the new pattern)
chain = prompt | llm  # This is a RunnableSequence

# Step 4: Final function
def generate_brief(exposure: str, earnings: str, sentiment: str) -> str:
    result = chain.invoke({
        "exposure": exposure,
        "earnings": earnings,
        "sentiment": sentiment
    })
    return result.content
