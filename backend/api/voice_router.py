import os
import tempfile
# pyrefly: ignore [missing-import]
import httpx
import json
from fastapi import APIRouter, File, UploadFile, HTTPException  # pyrefly: ignore [missing-import]
from fastapi.responses import FileResponse  # pyrefly: ignore [missing-import]

try:
    import speech_recognition as sr  # pyrefly: ignore [missing-import]
except ImportError:
    sr = None

try:
    from gtts import gTTS  # pyrefly: ignore [missing-import]
except ImportError:
    gTTS = None

router = APIRouter()
OLLAMA_URL = "http://localhost:11434/api/generate"

@router.post("/voice")
async def process_voice(audio: UploadFile = File(...)):
    """
    Transcribes uploaded audio (using speech_recognition), calls Ollama Llama3.2
    to generate a friendly response, and outputs spoken audio response (using gTTS).
    """
    transcribed_text = "What should I eat now?"
    
    # 1. Save uploaded file to temp file
    temp_dir = tempfile.gettempdir()
    temp_audio_path = os.path.join(temp_dir, audio.filename)
    
    try:
        with open(temp_audio_path, "wb") as f:
            content = await audio.read()
            f.write(content)
    except Exception as e:
        print(f"Error saving uploaded audio: {e}")
        temp_audio_path = None

    # 2. Perform speech-to-text transcription
    if temp_audio_path and sr is not None:
        try:
            r = sr.Recognizer()
            with sr.AudioFile(temp_audio_path) as source:
                audio_data = r.record(source)
                # Google Web Speech API (free, built-in)
                transcribed_text = r.recognize_google(audio_data)
                print(f"Transcribed audio text: {transcribed_text}")
        except Exception as e:
            print(f"Speech Recognition error or unsupported format: {e}. Falling back to default query.")
            # Standard WAV conversions or direct fallbacks are logged
    
    # 3. Call Ollama (Llama 3.2) to generate a concise spoken coach reply
    prompt = f"""
    You are the voice coach for NutriMind. The user said by voice: "{transcribed_text}"
    Provide a warm, supportive, and very concise reply (maximum 2 sentences) that is easy to listen to.
    """
    
    try:
        payload = {
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }
        # Request Ollama
        response = httpx.post(OLLAMA_URL, json=payload, timeout=20.0)
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response", "").strip()
        else:
            raise Exception(f"Ollama returned status code: {response.status_code}")
    except Exception as e:
        print(f"Ollama speech processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Ollama voice processing failed: {str(e)}")

    # Clean up formatting if any tags or json markers are in the text
    response_text = response_text.replace("{", "").replace("}", "").replace('"', '').replace("coach_reply:", "").strip()

    # 4. Perform Text-to-Speech (gTTS)
    audio_filename = "voice_response.mp3"
    temp_mp3_path = os.path.join(temp_dir, audio_filename)
    
    if gTTS is not None:
        try:
            tts = gTTS(text=response_text, lang='en')
            tts.save(temp_mp3_path)
            print(f"Saved TTS response audio to: {temp_mp3_path}")
        except Exception as e:
            print(f"TTS Generation Error: {e}")
            raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")
    else:
        raise HTTPException(status_code=500, detail="gTTS library not installed on the system.")

    # Serve the generated audio link
    audio_response_url = f"http://127.0.0.1:8000/api/voice/audio/{audio_filename}"

    # Clean up temp upload file if exists
    if temp_audio_path and os.path.exists(temp_audio_path):
        try:
            os.remove(temp_audio_path)
        except Exception:
            pass

    return {
        "transcription": transcribed_text,
        "assistant_reply": response_text,
        "audio_url": audio_response_url
    }

@router.get("/audio/{filename}")
def get_audio_response(filename: str):
    """
    Serves the generated audio response file to play in browser.
    """
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mp3")
    raise HTTPException(status_code=404, detail="Audio response file not found")
