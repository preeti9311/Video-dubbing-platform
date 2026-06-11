# app/api/status.py

from fastapi import APIRouter, HTTPException
from app.models.schemas import StatusResponse
from app.utils.job_store import get_job, list_jobs

# ✅ Router pehle define hona chahiye — baaki sab baad mein
router = APIRouter(prefix="/api/v1", tags=["Status"])


@router.get("/status/{job_id}", response_model=StatusResponse)
async def get_job_status(job_id: str):
    """
    Job ki processing status check karo.
    """
    job = get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' not found. Please check your job_id."
        )

    return StatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        message=job.message,
        result_file=job.result_file,
        error=job.error
    )


@router.get("/jobs", tags=["Debug"])
async def list_all_jobs():
    """
    Saare jobs ki list dekho (debugging ke liye).
    """
    jobs = list_jobs()
    return {
        "total": len(jobs),
        "jobs": jobs
    }


@router.get("/transcript/{job_id}", tags=["Debug"])
async def get_transcript(job_id: str):
    """
    Job ka transcribed text dekho (debugging ke liye).
    """
    job = get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if not hasattr(job, 'transcription') or job.transcription is None:
        return {
            "job_id": job_id,
            "transcription": None,
            "message": "Transcription data not stored yet"
        }

    return {
        "job_id": job_id,
        "detected_language": job.transcription.get("language"),
        "full_text": job.transcription.get("text"),
        "total_segments": len(job.transcription.get("segments", [])),
        "segments": job.transcription.get("segments", [])
    }


@router.get("/translation/{job_id}", tags=["Debug"])
async def get_translation(job_id: str):
    """
    Job ka translated text dekho (debugging ke liye).
    """
    job = get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if not hasattr(job, 'translation') or job.translation is None:
        return {
            "job_id": job_id,
            "translation": None,
            "message": "Translation not done yet"
        }

    return {
        "job_id": job_id,
        "source_language": job.translation.get("source_language"),
        "target_language": job.translation.get("target_language"),
        "original_text": job.translation.get("original_text"),
        "translated_text": job.translation.get("translated_text"),
        "total_segments": len(job.translation.get("segments", [])),
        "segments_preview": job.translation.get("segments", [])[:5]
    }