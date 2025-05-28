# 🎙️Voice-Activated Financial Assistant

A modular AI agent system that converts voice queries into intelligent financial insights. Built with **FastAPI**, **LangChain**, **OpenAI**, and modern agent architecture.

---

## 🚀 Overview

This project allows users to speak natural language queries (e.g., "What's the latest update on Apple Inc?") and receive comprehensive financial analysis through a multi-agent system.

---

## ✅ Implemented Features

### 1. **Voice-to-Text Agent (STT)**

- ✅ Converts spoken audio to text using **OpenAI Whisper**
- ✅ FastAPI endpoint: `POST /transcribe`
- ✅ Supports `.wav` audio format
- ✅ Temporary storage in `data_ingestion/`

### 2. **API Agent**

- ✅ Fetches real-time stock market data
- ✅ FastAPI endpoint: `POST /api/stock-data`
- ✅ Supports major ticker symbols (AAPL, GOOG, MSFT, etc.)
- ✅ Returns current price, change percentage, and market cap

### 3. **LLM Agent**

- ✅ Generates intelligent summaries using **LangChain + OpenAI**
- ✅ FastAPI endpoint: `POST /llm/brief`
- ✅ Contextual understanding of financial queries
- ✅ Structured response generation

---

## 📁 Project Structure

```
ragaai/
│
├── 📂 agents/
│   ├── 📂 voice_agent/
│   │   ├── 📄 voice_api.py      # FastAPI STT routes
│   │   └── 📄 stt.py            # Whisper transcription logic
│   │
│   ├── 📂 api_agent/
│   │   ├── 📄 api_service.py    # FastAPI stock data routes
│   │   └── 📄 service.py        # yfinance integration
│   │
│   └── 📂 llm_agent/
│       ├── 📄 llm_service.py    # FastAPI LLM routes
│       └── 📄 llm_logic.py      # LangChain + OpenAI logic
│
├── 📂 data_ingestion/           # Temporary storage for audio/text
│
├── 📄 .env                      # Environment variables (API keys)
├── 📄 .gitignore               # Git ignore rules
├── 📄 requirements.txt         # Python dependencies
└── 📄 README.md               # Project documentation
```

---

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- OpenAI API key
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/ragaai.git
   cd ragaai
   ```

2. **Create and activate virtual environment**

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   ```bash
   # Create .env file
   cp .env.example .env

   # Add your API keys
   OPENAI_API_KEY=your_openai_api_key_here
   ```

---

## 🚀 Running the Services

Start each agent service in a separate terminal:

```bash
# Terminal 1: Voice Agent (Port 8002)
uvicorn agents.voice_agent.voice_api:app --reload --port 8002

# Terminal 2: API Agent (Port 8001)
uvicorn agents.api_agent.api_service:app --reload --port 8001

# Terminal 3: LLM Agent (Port 8003)
uvicorn agents.llm_agent.llm_service:app --reload --port 8003
```

---

## 📡 API Endpoints

### Voice Agent

- **POST** `/transcribe` - Convert audio to text
  ```json
  {
    "file": "audio.wav"
  }
  ```

### API Agent

- **POST** `/api/stock-data` - Get stock information
  ```json
  {
    "ticker": "AAPL"
  }
  ```

### LLM Agent

- **POST** `/llm/generate_brief` - Generate financial summary
  ```json
  {
    "query": "Summarize Apple's latest performance"
  }
  ```

---

## 🚧 Next Steps

### Core Features

- [ ] **Build Orchestrator Agent** - Central coordinator for all agents
- [ ] **Implement Scraping Agent** - Extract data from SEC filings and news
- [ ] **Add Text-to-Speech (TTS)** - Convert responses to audio
- [ ] **Create Frontend Interface** - Streamlit-based UI

### Documentation

- [ ] **API Documentation** - Swagger/OpenAPI specs
- [ ] **User Guide** - End-user documentation
- [ ] **Developer Guide** - Contribution guidelines
- [ ] **Architecture Diagrams** - System design visuals

---

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- OpenAI for Whisper and GPT models
- LangChain for the agent framework
- FastAPI for the modern API framework
- yfinance for stock market data
