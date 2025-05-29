This document logs the key AI tool usage, prompts, code generation strategies, and model parameters used in the development of the multi-agent assistant system.

Overview

The assistant comprises the following core agents:

Voice Agent: Handles speech-to-text (STT) and optional text-to-speech (TTS).

LLM Agent: Processes natural language queries.

Scraping Agent: Retrieves financial data from external sources (e.g., SEC filings).

Retriever Agent: Stores and queries chunked embeddings from documents.

Orchestrator: Routes tasks between agents.

Streamlit UI: User-facing frontend for voice/text queries.

AI Tool: Whisper (STT)

Tool: OpenAI Whisper (or equivalent local Whisper implementation)

Function: Converts voice recordings into text.

Prompt: N/A (used via API or direct inference)

Model Parameters: Default base or small model

Used In: voice_agent/stt.py

Integration: FastAPI endpoint /transcribe

Output: Transcribed user query in plain text

AI Tool: OpenAI GPT (LLM Agent)

Tool: GPT-4 or GPT-3.5-Turbo

Function: Interprets user queries, generates answers, summaries, or structured insights

Prompt Strategy:

system: You are a helpful assistant that answers financial questions concisely.
user: {transcribed or typed query}

Model Parameters:

temperature=0.7

max_tokens=500

top_p=1.0

Used In: llm_agent/llm_logic.py

Integration: Via orchestrator POST request

AI Tool: SentenceTransformers (Retriever Agent)

Tool: all-MiniLM-L6-v2 via sentence-transformers

Function: Embedding generator for document chunks

Used In: retriever_agent/embedder.py

Prompt: N/A

Model Parameters:

Output Dimension: 384

Storage: Pinecone vector database

Chunking: Custom NLTK-based chunker (now replaced with pre-chunked input)

AI Tool: gTTS (TTS)

Tool: gTTS Python package

Function: Converts reply text into spoken audio (optional frontend feature)

Used In: streamlit_app/app.py

Prompt: N/A (text is passed directly)

Language: en

Code Generation & Prompt Strategy

Most code was generated iteratively using prompts like:

"Implement a FastAPI endpoint to accept and transcribe an audio file."

"How do I send recorded audio from Streamlit to a FastAPI backend?"

"Write a retriever that stores sentence embeddings in Pinecone."

"Design an orchestrator that routes requests to different agents based on task type."

Prompts were refined to incrementally build modular components, with testing at each stage.

Notes

All AI tools are abstracted behind modular endpoints so that agents can be swapped.

TTS is optional and not part of the orchestrated flow but supported in the frontend.

This file will be updated as additional AI tools or inference strategies are introduced.
