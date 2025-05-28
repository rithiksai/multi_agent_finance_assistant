# File: agents/voice_agent/stt.py
import whisper

# Load the Whisper model (we can use "tiny", "base", "small", "medium", or "large")
model = whisper.load_model("base")

def transcribe_audio(audio_path: str) -> str:
    result = model.transcribe(audio_path)
    return result["text"]
