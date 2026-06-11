
import os
from dotenv import load_dotenv

# .env file ko load karo
load_dotenv()

class Settings:
    # App basic info
    APP_NAME: str = "Video Dubbing Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"
    
    UPLOAD_DIR: str = "storage/uploads"
    AUDIO_DIR: str = "storage/audio"
    OUTPUT_DIR: str = "storage/outputs"
    
    # File size limit - 500MB max
    MAX_FILE_SIZE: int = 500 * 1024 * 1024
    
    # Allowed video formats
    ALLOWED_EXTENSIONS: set = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
    
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base").lower()
    # Default translation target language
    DEFAULT_TARGET_LANGUAGE: str = os.getenv("DEFAULT_TARGET_LANGUAGE", "hi")  # Hindi

settings = Settings()