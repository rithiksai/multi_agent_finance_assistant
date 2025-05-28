# File: agents/voice_agent/voice_api.py

from fastapi import FastAPI, UploadFile, File
from .stt import transcribe_audio       #because it's in the same file we are using .stt


app = FastAPI()

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    audio_path = f"temp_{file.filename}"
    with open(audio_path, "wb") as f:
        f.write(await file.read())

    text = transcribe_audio(audio_path)
    return {"transcription": text}
