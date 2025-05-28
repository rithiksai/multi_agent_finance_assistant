# 🎙️ RagaAI - Voice-Activated Financial Assistant

This project is a modular AI agent system that lets users speak a query (like "What's the latest update on Apple Inc?") and get back summarized financial insights. It's built using **FastAPI**, **LangChain**, **OpenAI**, and other agent services.

---

## ✅ What We’ve Built So Far

### 1. **Voice-to-Text Agent (STT)**

- Converts user's spoken audio into text using **OpenAI Whisper**
- Exposes a FastAPI route: `POST /transcribe`
- Stores uploaded `.wav` audio temporarily in `data_ingestion/`

### 2. **API Agent**

- Fetches real-time stock market data (e.g., current price, change %)
- Exposes route: `POST /api/stock-data`
- Accepts ticker symbols like `AAPL`, `GOOG`, etc.

### 3. **LLM Agent**

- Takes text queries and uses **LangChain + OpenAI** to generate intelligent summaries
- Example: "Summarize Apple’s latest financial performance"
- Exposes route: `POST /llm/brief`

---

## ⚙️ Project Structure

ragaai/
├── agents/
│ ├── voice_agent/
│ │ ├── voice_api.py # FastAPI STT route
│ │ └── stt.py # Whisper-based transcriber
│ ├── api_agent/
│ │ ├── api_service.py # FastAPI route for stock data
│ │ └── service.py # API logic using yfinance
│ └── llm_agent/
│ ├── llm_service.py # FastAPI route
│ └── llm_logic.py # LangChain + OpenAI logic
├── data_ingestion/ # Temporary files (audio, scraped text, etc.)
├── .env # API keys (not committed)
├── .gitignore # Prevents tracking of venv, .env, etc.
├── requirements.txt # Python dependencies
└── README.md # You're reading this!

---

## 🧪 How to Run

```bash
# Activate virtual environment
venv\Scripts\activate     # Windows
source venv/bin/activate  # Mac/Linux

# Start services
uvicorn agents.voice_agent.voice_api:app --reload --port 8002
uvicorn agents.api_agent.api_service:app --reload --port 8001
uvicorn agents.llm_agent.llm_service:app --reload --port 8003

🚧 Next Steps
 Build the Orchestrator Agent

 Add the Scraping Agent (SEC filings, news, etc.)

 Add frontend interface via Streamlit

 Implement text-to-speech (TTS) to speak back results
```
