# app/utils/job_store.py
# Yeh ek simple in-memory "database" hai jobs track karne ke liye.
# Real production mein Redis ya PostgreSQL use hota hai,
# lekin MVP ke liye dictionary bilkul theek hai.

from typing import Dict, Optional
from app.models.schemas import JobStatus
import time

# Job ki poori information store karne ka structure
class JobInfo:
    def __init__(self, job_id: str, filename: str, original_filename: str):
        self.job_id = job_id
        self.filename = filename                    # Saved file ka naam (job_id.ext)
        self.original_filename = original_filename  # User ne jo naam diya tha
        self.status = JobStatus.PENDING             # Shuru mein PENDING
        self.progress = 0                           # 0% complete
        self.message = "Job created, waiting to start"
        self.result_file: Optional[str] = None      # Output file path
        self.error: Optional[str] = None            # Error message if failed
        self.created_at = time.time()               # Timestamp
        self.updated_at = time.time()
        self.transcription = None
        self.translation = None  
        self.tts_audio_path = None  

    def update(self, status: JobStatus, progress: int, message: str,
               result_file: str = None, error: str = None):
        """Job ki status update karo"""
        self.status = status
        self.progress = progress
        self.message = message
        self.result_file = result_file
        self.error = error
        self.updated_at = time.time()

    def to_dict(self) -> dict:
        """Object ko dictionary mein convert karo (API response ke liye)"""
        return {
            "job_id": self.job_id,
            "filename": self.original_filename,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "result_file": self.result_file,
            "error": self.error,
            "created_at": self.created_at,
        }


# Global job store — poore app mein yahi use hoga
# Key = job_id, Value = JobInfo object
_job_store: Dict[str, JobInfo] = {}


def create_job(job_id: str, filename: str, original_filename: str) -> JobInfo:
    """Naya job create karo aur store mein save karo"""
    job = JobInfo(job_id, filename, original_filename)
    _job_store[job_id] = job
    print(f"✅ Job created: {job_id}")
    return job


def get_job(job_id: str) -> Optional[JobInfo]:
    """Job ID se job fetch karo. None return karta hai agar exist nahi karta."""
    return _job_store.get(job_id)


def update_job(job_id: str, status: JobStatus, progress: int,
               message: str, result_file: str = None, error: str = None) -> Optional[JobInfo]:
    """Existing job ki status update karo"""
    job = _job_store.get(job_id)
    if job:
        job.update(status, progress, message, result_file, error)
        print(f"📝 Job {job_id} updated: {status} ({progress}%)")
    return job


def list_jobs() -> list:
    """Saare jobs ki list return karo (debugging ke liye)"""
    return [job.to_dict() for job in _job_store.values()]