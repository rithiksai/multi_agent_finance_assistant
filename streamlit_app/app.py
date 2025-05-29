import streamlit as st
import httpx
import tempfile
import os
from gtts import gTTS
import base64
import time
from dotenv import load_dotenv
from pathlib import Path

from streamlit_webrtc import webrtc_streamer

AUDIO_SAVE_PATH = "audio_responses"
os.makedirs(AUDIO_SAVE_PATH, exist_ok=True)

# Load environment variables
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

# Point to your local voice agent
VOICE_AGENT_URL= os.getenv("VOICE_AGENT_URL")

def synthesize_and_play(text: str):
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    
    # Play back in Streamlit
    with open("response.mp3", "rb") as audio_file:
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3")
    
    # Optional: clean up the file
    os.remove("response.mp3")

st.set_page_config(page_title="Stock Insights", layout="centered")
st.title("📈Stock Insight Assistant")

audio_file = st.audio_input("Record your query")  # Allows users to record audio input

if audio_file is not None:
    # Define the save path for the recorded audio
    audio_save_path = os.path.join(AUDIO_SAVE_PATH, "recorded_response.wav")
    
    # Save the recorded audio file locally
    with open(audio_save_path, "wb") as f:
        f.write(audio_file.getbuffer())  # Writes the audio file buffer to the specified path
    
    st.write(f"Audio saved at: {audio_save_path}")  # Display the save path for reference
    st.audio(audio_file)
    
    # Show spinner while processing
    with st.spinner('🎯 Analyzing your query... Please wait while we work our magic!'):
        try:
            with open(audio_save_path, "rb") as f:
                files = {"file": f}
                transcription = httpx.post(VOICE_AGENT_URL, files=files, timeout=90.0)
            
            if transcription.status_code == 200:
                data = transcription.json()
                transcribed_text = data.get("transcription", "")
                reply = data.get("reply", "")
                
                st.markdown("**Transcription:**")
                st.write(transcribed_text)
                
                st.markdown("**Insight from AI:**")
                st.success(reply)
                # 🔊 Speak it
                synthesize_and_play(reply)
            else:
                st.error(f"❌ Voice Agent Error: {transcription.status_code} - {transcription.text}")
        except Exception as e:
            st.error(f"❌ Failed to call voice agent: {e}")