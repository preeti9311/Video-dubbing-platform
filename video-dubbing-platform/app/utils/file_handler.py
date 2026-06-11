
import os
import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.config import settings

def ensure_directories():
   
    dirs = [settings.UPLOAD_DIR, settings.AUDIO_DIR, settings.OUTPUT_DIR]
    for directory in dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)
    print(" Storage directories ready")

def generate_job_id() -> str:
   
    return str(uuid.uuid4())

def get_file_extension(filename: str) -> str:
   
    return Path(filename).suffix.lower()

def validate_video_file(file: UploadFile) -> None:

    extension = get_file_extension(file.filename)
    
    if extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{extension}'. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )

async def save_upload_file(file: UploadFile, job_id: str) -> str:
   
    extension = get_file_extension(file.filename)
    
    # Job ID se filename banao - unique rahega
    saved_filename = f"{job_id}{extension}"
    save_path = os.path.join(settings.UPLOAD_DIR, saved_filename)
    
    # File ko disk par save karo
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    print(f" File saved: {save_path}")
    return save_path

def get_output_path(job_id: str) -> str:
   
    return os.path.join(settings.OUTPUT_DIR, f"{job_id}_dubbed.mp4")

def cleanup_temp_files(job_id: str) -> None:
   
    temp_patterns = [
        os.path.join(settings.AUDIO_DIR, f"{job_id}*"),
    ]
    import glob
    for pattern in temp_patterns:
        for file_path in glob.glob(pattern):
            try:
                os.remove(file_path)
                print(f"🗑️ Cleaned up: {file_path}")
            except Exception as e:
                print(f"⚠️ Could not delete {file_path}: {e}")