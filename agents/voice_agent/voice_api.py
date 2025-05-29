# File: agents/voice_agent/voice_api.py

import os
from pathlib import Path
import httpx
from fastapi import FastAPI, UploadFile, File
from .stt import transcribe_audio    #because it's in the same file we are using .stt
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)


ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000/ask")

app = FastAPI()

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    audio_path = f"temp_{file.filename}"
    with open(audio_path, "wb") as f:
        f.write(await file.read())

    text = transcribe_audio(audio_path)
    # Step 2: Send text to orchestrator
    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(ORCHESTRATOR_URL, json={"query": text})
        print("Raw response:", response.status_code, response.text)

        reply = response.json()["response"]

    return {"transcription": text, "reply": reply}
