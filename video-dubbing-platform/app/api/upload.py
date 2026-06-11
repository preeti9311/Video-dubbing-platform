# app/api/upload.py — Poora updated file

import asyncio
import traceback
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from typing import Optional
from app.models.schemas import UploadResponse, JobStatus
from app.utils.file_handler import (
    validate_video_file,
    save_upload_file,
    generate_job_id
)
from app.utils.job_store import create_job, update_job, get_job

router = APIRouter(prefix="/api/v1", tags=["Upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(..., description="Video file to dub"),
    target_language: Optional[str] = Form(
        default="hi",
        description="Target language code e.g. 'hi', 'es', 'fr'"
    ),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    validate_video_file(file)
    job_id = generate_job_id()

    try:
        saved_path = await save_upload_file(file, job_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File save failed: {str(e)}"
        )

    create_job(
        job_id=job_id,
        filename=saved_path,
        original_filename=file.filename
    )

    background_tasks.add_task(
        process_video_pipeline,
        job_id=job_id,
        file_path=saved_path,
        target_language=target_language
    )

    return UploadResponse(
        job_id=job_id,
        filename=file.filename,
        message=f"Video uploaded! Processing started for: {target_language}",
        status=JobStatus.PENDING
    )


async def process_video_pipeline(job_id: str, file_path: str,
                                  target_language: str):
    """
    Complete dubbing pipeline:
    1. Transcription (Whisper)
    2. Translation (deep-translator)
    3. Text-to-Speech (gTTS)
    4. Video Merge (FFmpeg)
    """
    loop = asyncio.get_event_loop()
    job = get_job(job_id)

    try:
        # ── STEP 1: TRANSCRIPTION ──────────────────────────────
        update_job(job_id, JobStatus.PROCESSING, 10,
                   "Extracting audio and transcribing speech...")

        from app.services.transcription import process_transcription
        transcription = await loop.run_in_executor(
            None, process_transcription, file_path, job_id
        )
        job.transcription = transcription

        update_job(job_id, JobStatus.PROCESSING, 30,
                   f"✅ Transcription done! "
                   f"Language: {transcription['language']} | "
                   f"{len(transcription['segments'])} segments")

        # ── STEP 2: TRANSLATION ────────────────────────────────
        update_job(job_id, JobStatus.PROCESSING, 35,
                   f"Translating to {target_language}...")

        from app.services.translation import translate_full_pipeline
        translation = await loop.run_in_executor(
            None, translate_full_pipeline, transcription, target_language
        )
        job.translation = translation

        update_job(job_id, JobStatus.PROCESSING, 55,
                   f"✅ Translation done! "
                   f"{transcription['language']} → {target_language}")

        # ── STEP 3: TEXT TO SPEECH ─────────────────────────────
        update_job(job_id, JobStatus.PROCESSING, 60,
                   f"Generating dubbed audio in {target_language}...")

        from app.services.tts import process_tts
        tts_audio_path = await loop.run_in_executor(
            None, process_tts,
            translation, target_language, job_id, file_path
        )
        job.tts_audio_path = tts_audio_path

        update_job(job_id, JobStatus.PROCESSING, 80,
                   "✅ Dubbed audio ready! Merging with video...")

        # ── STEP 4: VIDEO MERGE ────────────────────────────────
        from app.services.merger import process_merge
        output_path = await loop.run_in_executor(
            None, process_merge, file_path, tts_audio_path, job_id
        )

        # ── COMPLETE ───────────────────────────────────────────
        update_job(
            job_id,
            JobStatus.COMPLETED,
            100,
            f"🎉 Dubbing complete! Your video is ready to download.",
            result_file=output_path   # ← Download ke liye path save karo
        )

        print(f"🎉 Job {job_id} complete! Output: {output_path}")

    except Exception as e:
        error_msg = f"Pipeline failed: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        update_job(job_id, JobStatus.FAILED, 0,
                   "Processing failed", error=error_msg)