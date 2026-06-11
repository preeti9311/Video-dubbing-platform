# app/services/transcription.py
# Yeh file do kaam karti hai:
# 1. Video se audio extract karna (FFmpeg use karke)
# 2. Audio se speech-to-text karna (Whisper use karke)

import os
import subprocess
import whisper
from app.config import settings

# Whisper model ek baar load karo — memory mein rehega
# Baar baar load karna slow hota hai
_whisper_model = None

def get_whisper_model():
    """
    Whisper model load karo.
    Pehli baar slow hoga (download karega), baad mein fast.
    'base' model = ~74MB, good balance of speed and accuracy.
    """
    global _whisper_model
    if _whisper_model is None:
        print(f"⏳ Loading Whisper model: {settings.WHISPER_MODEL}")
        _whisper_model = whisper.load_model(settings.WHISPER_MODEL)
        print("✅ Whisper model loaded!")
    return _whisper_model


def extract_audio_from_video(video_path: str, job_id: str) -> str:
    """
    Video file se audio extract karo FFmpeg use karke.
    
    Args:
        video_path: Input video ka path
        job_id: Unique job identifier
    
    Returns:
        audio_path: Extracted audio file ka path (.wav)
    
    FFmpeg command explanation:
    -i input.mp4     → input file
    -vn              → video nahi chahiye (video no)
    -acodec pcm_s16le → audio format (WAV ke liye standard)
    -ar 16000        → 16kHz sample rate (Whisper ke liye optimal)
    -ac 1            → mono audio (1 channel, Whisper prefer karta hai)
    output.wav       → output file
    """
    audio_path = os.path.join(settings.AUDIO_DIR, f"{job_id}_audio.wav")
    
    command = [
        "ffmpeg",
        "-i", video_path,      # Input video
        "-vn",                  # No video
        "-acodec", "pcm_s16le", # WAV format
        "-ar", "16000",         # 16kHz (Whisper optimal)
        "-ac", "1",             # Mono
        "-y",                   # Overwrite if exists
        audio_path              # Output
    ]
    
    print(f"🎵 Extracting audio from: {video_path}")
    
    # FFmpeg command run karo
    result = subprocess.run(
        command,
        capture_output=True,  # stdout/stderr capture karo
        text=True
    )
    
    # Error check karo
    if result.returncode != 0:
        raise Exception(f"FFmpeg audio extraction failed: {result.stderr}")
    
    # File exist karti hai?
    if not os.path.exists(audio_path):
        raise Exception("Audio file was not created by FFmpeg")
    
    print(f"✅ Audio extracted: {audio_path}")
    return audio_path


def transcribe_audio(audio_path: str) -> dict:
    """
    Audio file ko text mein convert karo Whisper use karke.
    
    Args:
        audio_path: .wav file ka path
    
    Returns:
        dict with:
            - text: Poora transcribed text
            - language: Detected language code (e.g. 'en')
            - segments: Time-stamped segments list
    
    Segments example:
    [
        {"start": 0.0, "end": 2.5, "text": "Hello everyone"},
        {"start": 2.5, "end": 5.0, "text": "Welcome to our show"}
    ]
    """
    print(f"🎙️ Starting transcription: {audio_path}")
    
    model = get_whisper_model()
    
    # Whisper se transcribe karo
    # fp16=False → CPU par better compatibility (GPU nahi hai toh)
    result = model.transcribe(
        audio_path,
        fp16=False,
        verbose=False  # Console spam band karo
    )
    
    # Sirf zaroori data extract karo
    transcription = {
        "text": result["text"].strip(),
        "language": result["language"],  # Auto-detected language
        "segments": [
            {
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip()
            }
            for seg in result["segments"]
        ]
    }
    
    print(f"✅ Transcription done!")
    print(f"   Detected language: {transcription['language']}")
    print(f"   Total segments: {len(transcription['segments'])}")
    print(f"   Preview: {transcription['text'][:100]}...")
    
    return transcription


def process_transcription(video_path: str, job_id: str) -> dict:
    """
    Main function — video se audio extract karo, phir transcribe karo.
    Yeh function pipeline mein call hoga.
    
    Returns: transcription dict
    """
    # Step 1: Audio extract karo
    audio_path = extract_audio_from_video(video_path, job_id)
    
    # Step 2: Transcribe karo
    transcription = transcribe_audio(audio_path)
    
    return transcription