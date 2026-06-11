# app/services/merger.py
# Yeh file original video ke saath dubbed audio merge karti hai.
# FFmpeg use karta hai — industry standard tool for video processing.
# Original video ki quality same rehti hai, sirf audio replace hota hai.

import os
import subprocess
from app.config import settings
from app.utils.file_handler import get_output_path


def merge_audio_with_video(video_path: str, audio_path: str,
                            job_id: str) -> str:
    """
    Original video ke saath dubbed audio merge karo.
    
    Strategy:
    1. Original video ka audio remove karo (-an flag)
    2. Naya dubbed audio add karo
    3. Video quality same rakho (-c:v copy)
    
    Args:
        video_path: Original video file path
        audio_path: Dubbed TTS audio file path
        job_id: Job identifier
    
    Returns:
        output_path: Final dubbed video ka path
    """
    output_path = get_output_path(job_id)

    print(f"🎬 Merging video + dubbed audio...")
    print(f"   Video : {video_path}")
    print(f"   Audio : {audio_path}")
    print(f"   Output: {output_path}")

    # FFmpeg command:
    # -i video_path     → input 1: original video
    # -i audio_path     → input 2: dubbed audio
    # -c:v copy         → video stream copy karo (re-encode mat karo, fast!)
    # -map 0:v:0        → video stream video se lo
    # -map 1:a:0        → audio stream dubbed audio se lo
    # -shortest         → jab bhi koi stream khatam ho, video khatam karo
    # -y                → output overwrite karo

    command = [
        "ffmpeg",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        "-y",
        output_path
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"❌ FFmpeg merge failed:\n{result.stderr[-500:]}")
        raise Exception(f"Video merge failed: {result.stderr[-200:]}")

    # Output file exist karti hai?
    if not os.path.exists(output_path):
        raise Exception("Output video was not created by FFmpeg")

    # File size check karo
    file_size = os.path.getsize(output_path)
    file_size_mb = file_size / (1024 * 1024)
    print(f"✅ Video merge complete!")
    print(f"   Output size: {file_size_mb:.1f} MB")
    print(f"   Output path: {output_path}")

    return output_path


def verify_output_video(output_path: str) -> dict:
    """
    Output video verify karo — duration aur streams check karo.
    
    Returns:
        dict with video info
    """
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            "-show_format",
            output_path
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return {"verified": False, "error": result.stderr}

    import json
    try:
        probe_data = json.loads(result.stdout)
        streams = probe_data.get("streams", [])
        format_info = probe_data.get("format", {})

        has_video = any(s["codec_type"] == "video" for s in streams)
        has_audio = any(s["codec_type"] == "audio" for s in streams)
        duration = float(format_info.get("duration", 0))

        return {
            "verified": True,
            "has_video": has_video,
            "has_audio": has_audio,
            "duration": round(duration, 2),
            "size_mb": round(
                int(format_info.get("size", 0)) / (1024 * 1024), 2
            )
        }
    except Exception as e:
        return {"verified": False, "error": str(e)}


def process_merge(video_path: str, tts_audio_path: str, job_id: str) -> str:
    """
    Main merge function — pipeline mein yahi call hoga.
    
    Returns:
        output_path: Final video ka path
    """
    # Merge karo
    output_path = merge_audio_with_video(video_path, tts_audio_path, job_id)

    # Verify karo
    verification = verify_output_video(output_path)
    if verification.get("verified"):
        print(f"✅ Video verified:")
        print(f"   Duration : {verification['duration']}s")
        print(f"   Has video: {verification['has_video']}")
        print(f"   Has audio: {verification['has_audio']}")
        print(f"   Size     : {verification['size_mb']} MB")
    else:
        print(f"⚠️ Video verification failed: {verification.get('error')}")

    return output_path