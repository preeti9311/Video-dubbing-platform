# app/api/upload.py

import asyncio
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from typing import Optional
from app.models.schemas import UploadResponse, JobStatus
from app.utils.file_handler import (
    validate_video_file,
    save_upload_file,
    generate_job_id
)
from app.utils.job_store import create_job, update_job

# Router — ek mini-app jisme related routes group hote hain
router = APIRouter(prefix="/api/v1", tags=["Upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(..., description="Video file to dub"),
    target_language: Optional[str] = Form(default="hi", description="Target language code, e.g. 'hi' for Hindi, 'es' for Spanish"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Video upload karo dubbing ke liye.
    
    - **file**: Video file (.mp4, .avi, .mov, .mkv, .webm)
    - **target_language**: Jis language mein dub karna hai (default: Hindi)
    
    Returns a **job_id** to track processing status.
    """

    # Step 1: File validate karo
    validate_video_file(file)

    # Step 2: Unique job ID generate karo
    job_id = generate_job_id()

    # Step 3: File disk par save karo
    try:
        saved_path = await save_upload_file(file, job_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")

    # Step 4: Job store mein entry banao
    create_job(
        job_id=job_id,
        filename=saved_path,
        original_filename=file.filename
    )

    # Step 5: Background mein processing shuru karo
    # (Abhi placeholder hai, Step 4 mein actual processing add karenge)
    background_tasks.add_task(
        process_video_pipeline,
        job_id=job_id,
        file_path=saved_path,
        target_language=target_language
    )

    # Step 6: Response return karo
    return UploadResponse(
        job_id=job_id,
        filename=file.filename,
        message=f"Video uploaded successfully! Processing started for language: {target_language}",
        status=JobStatus.PENDING
    )


async def process_video_pipeline(job_id: str, file_path: str, target_language: str):
    """
    Yeh background task hai jo actual dubbing pipeline run karega.
    Abhi placeholder hai — Step 4, 5, 6, 7 mein fill karenge.
    
    Pipeline order:
    1. Transcription (Whisper) — Step 4
    2. Translation — Step 5
    3. Text-to-Speech — Step 6
    4. Audio/Video Merge — Step 7
    """
    print(f" Starting pipeline for job: {job_id}")

    # Status: Processing shuru
    update_job(job_id, JobStatus.PROCESSING, 10, "Pipeline started...")

    # --- Placeholder: Aage yahan actual steps aayenge ---
    # Abhi sirf simulate kar rahe hain processing ko
    await asyncio.sleep(2)
    update_job(job_id, JobStatus.PROCESSING, 25, "Transcription in progress...")

    await asyncio.sleep(2)
    update_job(job_id, JobStatus.PROCESSING, 50, "Translation in progress...")

    await asyncio.sleep(2)
    update_job(job_id, JobStatus.PROCESSING, 75, "Text-to-speech in progress...")

    await asyncio.sleep(2)
    update_job(job_id, JobStatus.COMPLETED, 100, "Dubbing complete! (Placeholder)")

    print(f"✅ Pipeline complete for job: {job_id}")