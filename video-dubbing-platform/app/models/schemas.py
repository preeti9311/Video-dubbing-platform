from pydantic import BaseModel
from typing import Optional
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"         # Job queue mein hai
    PROCESSING = "processing"   # Kaam chal raha hai
    COMPLETED = "completed"     # Ho gaya!
    FAILED = "failed"           # Kuch gadbad ho gayi

class UploadResponse(BaseModel):
    job_id: str                 # Unique ID - status track karne ke liye
    filename: str               # Original file ka naam
    message: str                # User ko message
    status: JobStatus           # Current status

class StatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: int               # 0-100 percentage
    message: str
    result_file: Optional[str] = None  # Output file path (jab complete ho)
    error: Optional[str] = None        # Error message (agar failed ho)

# Translation request
class TranslationRequest(BaseModel):
    text: str                   # Text to translate
    source_language: str = "auto"  # Auto-detect source
    target_language: str = "hi"    # Default: Hindi