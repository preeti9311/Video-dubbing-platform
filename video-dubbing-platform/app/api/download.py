
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.utils.job_store import get_job
from app.models.schemas import JobStatus

router = APIRouter(prefix="/api/v1", tags=["Download"])


@router.get("/download/{job_id}")
async def download_dubbed_video(job_id: str):
    """
    Dubbed video download karo.
    
    - **job_id**: Job ka unique ID
    
    Returns the dubbed video file as a download.
    """
    # Job dhundo
    job = get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check karo ki job complete hai
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Job is not complete yet. Current status: {job.status} ({job.progress}%)"
        )

    # Result file exist karti hai?
    if not job.result_file or not os.path.exists(job.result_file):
        raise HTTPException(
            status_code=404,
            detail="Output file not found. It may have been deleted."
        )

    # File download ke liye return karo
    return FileResponse(
        path=job.result_file,
        media_type="video/mp4",
        filename=f"dubbed_{job.original_filename}"
    )