# app/utils/job_store.py
# File-based storage — server restart hone par bhi jobs rahenge

import json
import os
import time
from typing import Dict, Optional
from app.models.schemas import JobStatus

JOBS_FILE = "storage/jobs.json"

class JobInfo:
    def __init__(self, job_id: str, filename: str, original_filename: str):
        self.job_id = job_id
        self.filename = filename
        self.original_filename = original_filename
        self.status = JobStatus.PENDING
        self.progress = 0
        self.message = "Job created, waiting to start"
        self.result_file: Optional[str] = None
        self.error: Optional[str] = None
        self.created_at = time.time()
        self.updated_at = time.time()
        self.transcription = None
        self.translation = None
        self.tts_audio_path = None

    def update(self, status, progress, message,
               result_file=None, error=None):
        self.status = status
        self.progress = progress
        self.message = message
        self.result_file = result_file
        self.error = error
        self.updated_at = time.time()

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "result_file": self.result_file,
            "error": self.error,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# In-memory store
_job_store: Dict[str, JobInfo] = {}


def _save_to_file():
    """Jobs ko file mein save karo"""
    try:
        os.makedirs("storage", exist_ok=True)
        data = {k: v.to_dict() for k, v in _job_store.items()}
        with open(JOBS_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"⚠️ Could not save jobs: {e}")


def _load_from_file():
    """File se jobs load karo"""
    try:
        if os.path.exists(JOBS_FILE):
            with open(JOBS_FILE, "r") as f:
                data = json.load(f)
            for job_id, job_data in data.items():
                job = JobInfo(
                    job_data["job_id"],
                    job_data["filename"],
                    job_data["original_filename"]
                )
                job.status = job_data["status"]
                job.progress = job_data["progress"]
                job.message = job_data["message"]
                job.result_file = job_data.get("result_file")
                job.error = job_data.get("error")
                _job_store[job_id] = job
            print(f"✅ Loaded {len(_job_store)} jobs from file")
    except Exception as e:
        print(f"⚠️ Could not load jobs: {e}")


# App start hone par load karo
_load_from_file()


def create_job(job_id: str, filename: str,
               original_filename: str) -> JobInfo:
    job = JobInfo(job_id, filename, original_filename)
    _job_store[job_id] = job
    _save_to_file()
    print(f"✅ Job created: {job_id}")
    return job


def get_job(job_id: str) -> Optional[JobInfo]:
    return _job_store.get(job_id)


def update_job(job_id: str, status, progress: int,
               message: str, result_file=None,
               error=None) -> Optional[JobInfo]:
    job = _job_store.get(job_id)
    if job:
        job.update(status, progress, message, result_file, error)
        _save_to_file()
        print(f"📝 Job {job_id} updated: {status} ({progress}%)")
    return job


def list_jobs() -> list:
    return [job.to_dict() for job in _job_store.values()]