# app/services/tts.py
# Yeh file translated text ko audio mein convert karti hai.
# Do options hain:
# 1. gTTS (Google TTS) — Free, robotic voice, no API key needed
# 2. ElevenLabs — Human-like voice, free tier available, API key needed
# USE_ELEVENLABS=True set karo .env mein ElevenLabs use karne ke liye

import os
import subprocess
from typing import List
from app.config import settings


# ─────────────────────────────────────────────
# CORE TTS FUNCTION — gTTS ya ElevenLabs decide karta hai
# ─────────────────────────────────────────────

def text_to_speech_segment(text: str, language: str, output_path: str) -> str:
    """
    Single text segment ko audio mein convert karo.
    .env mein USE_ELEVENLABS=True set karo ElevenLabs ke liye,
    warna automatically gTTS use hoga.

    Args:
        text: Bol ne wala text
        language: Language code (e.g. 'hi', 'es', 'en')
        output_path: Output audio file ka path (.mp3)

    Returns:
        output_path: Saved audio file ka path
    """
    if not text or not text.strip():
        create_silent_audio(output_path, duration=1.0)
        return output_path

    use_elevenlabs = os.getenv("USE_ELEVENLABS", "False") == "True"
    api_key = os.getenv("ELEVENLABS_API_KEY", "")

    if use_elevenlabs and api_key:
        print(f"🎙️ Using ElevenLabs TTS")
        return _elevenlabs_tts(text, output_path)
    else:
        print(f"🎙️ Using gTTS")
        return _gtts_tts(text, language, output_path)


# ─────────────────────────────────────────────
# gTTS — Free, no API key
# ─────────────────────────────────────────────

def _gtts_tts(text: str, language: str, output_path: str) -> str:
    """
    gTTS se audio generate karo.
    Free hai, koi API key nahi chahiye.
    Voice thodi robotic hoti hai.
    """
    try:
        from gtts import gTTS
        tts = gTTS(text=text.strip(), lang=language, slow=False)
        tts.save(output_path)
        return output_path

    except Exception as e:
        print(f"⚠️ gTTS failed: {e}")
        create_silent_audio(output_path, duration=1.0)
        return output_path


# ─────────────────────────────────────────────
# ElevenLabs — Human-like voice
# ─────────────────────────────────────────────

def _elevenlabs_tts(text: str, output_path: str) -> str:
    try:
        from elevenlabs import ElevenLabs

        client = ElevenLabs(
            api_key=os.getenv("ELEVENLABS_API_KEY")
        )

        # Nayi API syntax
        audio = client.text_to_speech.convert(
            text=text.strip(),
            voice_id="21m00Tcm4TlvDq8ikWAM",   # Rachel voice ID
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )

        # Audio bytes file mein save karo
        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        print(f"✅ ElevenLabs audio saved: {output_path}")
        return output_path

    except Exception as e:
        print(f"⚠️ ElevenLabs failed: {e} — falling back to gTTS")
        return _gtts_tts(text, "en", output_path)

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def create_silent_audio(output_path: str, duration: float = 1.0):
    """
    Silent audio file banao FFmpeg se.
    Empty ya failed segments ke liye use hota hai.

    Args:
        output_path: Output file path
        duration: Silence duration in seconds
    """
    command = [
        "ffmpeg",
        "-f", "lavfi",
        "-i", f"anullsrc=r=22050:cl=mono",
        "-t", str(duration),
        "-y",
        output_path
    ]
    subprocess.run(command, capture_output=True)


def adjust_audio_duration(audio_path: str, target_duration: float,
                           output_path: str) -> str:
    """
    Audio ki speed adjust karo taaki original segment
    duration se match kare — timing mismatch fix karta hai.

    Example:
    TTS audio = 3 seconds
    Original segment = 2 seconds
    → Audio 1.5x speed par chalega (3/2 = 1.5)

    Speed range: 0.5x (slow) to 2.0x (fast)
    Extreme values avoid karte hain — unnatural lagta hai.

    Args:
        audio_path: Input audio path
        target_duration: Original segment ki duration (seconds)
        output_path: Speed-adjusted output path

    Returns:
        output_path agar success, warna original audio_path
    """
    # Actual audio duration nikalo
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            audio_path
        ],
        capture_output=True,
        text=True
    )

    try:
        actual_duration = float(result.stdout.strip())
    except:
        return audio_path  # Duration nahi mili

    if actual_duration <= 0 or target_duration <= 0:
        return audio_path

    # Speed ratio calculate karo
    speed_ratio = actual_duration / target_duration

    # 0.5x se 2.0x ke beech rakho
    speed_ratio = max(0.5, min(2.0, speed_ratio))

    print(f"   ⏱️ Duration adjust: {actual_duration:.1f}s → {target_duration:.1f}s "
          f"(speed: {speed_ratio:.2f}x)")

    # atempo filter se speed adjust karo
    # Note: atempo sirf 0.5-2.0 range support karta hai
    command = [
        "ffmpeg",
        "-i", audio_path,
        "-filter:a", f"atempo={speed_ratio:.2f}",
        "-y",
        output_path
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        return output_path
    else:
        print(f"⚠️ Duration adjust failed, using original")
        return audio_path


def get_video_duration(video_path: str) -> float:
    """
    Video ki total duration nikalo FFprobe se.
    Merge step mein base silent audio banane ke liye use hota hai.

    Returns:
        Duration in seconds (default 60.0 agar detect na ho)
    """
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            video_path
        ],
        capture_output=True,
        text=True
    )
    try:
        return float(result.stdout.strip())
    except:
        return 60.0


# ─────────────────────────────────────────────
# SEGMENT-LEVEL TTS GENERATION
# ─────────────────────────────────────────────

def generate_tts_for_segments(segments: List[dict], target_language: str,
                               job_id: str) -> List[dict]:
    """
    Har translated segment ke liye TTS audio generate karo.
    Har segment ka alag audio file banta hai.

    Args:
        segments: Translated segments list
                  [{"start": 0.0, "end": 2.5, "text": "नमस्ते"}]
        target_language: TTS language code
        job_id: File naming ke liye

    Returns:
        Same segments list with audio_path added to each
    """
    print(f"🔊 Generating TTS for {len(segments)} segments "
          f"(language: {target_language})...")

    segments_with_audio = []

    for i, segment in enumerate(segments):
        text = segment["text"]
        start = segment["start"]
        end = segment["end"]
        target_duration = end - start

        # File paths
        raw_audio = os.path.join(
            settings.AUDIO_DIR,
            f"{job_id}_seg_{i:04d}_raw.mp3"
        )
        adjusted_audio = os.path.join(
            settings.AUDIO_DIR,
            f"{job_id}_seg_{i:04d}.mp3"
        )

        # Step 1: TTS generate karo
        text_to_speech_segment(text, target_language, raw_audio)

        # Step 2: Duration adjust karo (timing fix)
        if os.path.exists(raw_audio):
            adjust_audio_duration(raw_audio, target_duration, adjusted_audio)

        # Best available file use karo
        final_audio = (
            adjusted_audio if os.path.exists(adjusted_audio)
            else raw_audio if os.path.exists(raw_audio)
            else None
        )

        segments_with_audio.append({
            **segment,
            "audio_path": final_audio,
            "target_duration": target_duration
        })

        # Progress print
        if (i + 1) % 5 == 0 or (i + 1) == len(segments):
            print(f"   ✅ {i + 1}/{len(segments)} segments done")

    print(f"✅ TTS generation complete!")
    return segments_with_audio


# ─────────────────────────────────────────────
# AUDIO MERGING
# ─────────────────────────────────────────────

def merge_tts_segments(segments_with_audio: List[dict],
                       job_id: str,
                       total_duration: float) -> str:
    """
    Saare TTS segments ko ek final audio file mein merge karo.
    Har segment apne original timestamp par play hoga.

    Strategy:
    1. Full duration ka silent base audio banao
    2. Har segment ko uske start time par overlay karo (adelay)
    3. Sab mix karo amix filter se

    Args:
        segments_with_audio: Segments with audio_path
        job_id: Job identifier
        total_duration: Original video ki total duration

    Returns:
        final_audio_path: Complete dubbed audio file
    """
    print(f"🔗 Merging {len(segments_with_audio)} audio segments...")

    final_audio_path = os.path.join(
        settings.AUDIO_DIR,
        f"{job_id}_final_tts.mp3"
    )

    # Base silent audio — full video duration ka
    base_audio_path = os.path.join(
        settings.AUDIO_DIR,
        f"{job_id}_base.mp3"
    )
    create_silent_audio(base_audio_path, duration=total_duration)

    # Valid segments filter karo
    valid_segments = [
        s for s in segments_with_audio
        if s.get("audio_path") and os.path.exists(s["audio_path"])
    ]

    if not valid_segments:
        print("⚠️ No valid segments — returning silent base audio")
        return base_audio_path

    # FFmpeg inputs build karo
    inputs = ["-i", base_audio_path]
    filter_parts = []

    for i, seg in enumerate(valid_segments):
        inputs += ["-i", seg["audio_path"]]
        delay_ms = int(seg["start"] * 1000)  # Milliseconds mein
        filter_parts.append(
            f"[{i + 1}]adelay={delay_ms}|{delay_ms}[a{i}]"
        )

    # Mix filter banao
    mix_inputs = "[0]" + "".join(f"[a{i}]" for i in range(len(filter_parts)))
    filter_complex = (
        ";".join(filter_parts) +
        f";{mix_inputs}amix=inputs={len(filter_parts) + 1}"
        f":normalize=0[out]"
    )

    command = [
        "ffmpeg",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-y",
        final_audio_path
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"⚠️ Merge failed, trying simple concat...")
        return _simple_concat(valid_segments, job_id)

    print(f"✅ Audio merge complete: {final_audio_path}")
    return final_audio_path


def _simple_concat(segments_with_audio: List[dict], job_id: str) -> str:
    """
    Fallback: Segments ko simply ek ke baad ek join karo.
    Timestamps match nahi hoga lekin kaam karega.
    """
    print("🔄 Using simple concat fallback...")

    concat_list = os.path.join(settings.AUDIO_DIR, f"{job_id}_concat.txt")
    output_path = os.path.join(settings.AUDIO_DIR, f"{job_id}_final_tts.mp3")

    with open(concat_list, "w") as f:
        for seg in segments_with_audio:
            f.write(f"file '{os.path.abspath(seg['audio_path'])}'\n")

    command = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list,
        "-y",
        output_path
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(f"Concat also failed: {result.stderr[-200:]}")

    return output_path


# ─────────────────────────────────────────────
# MAIN PIPELINE FUNCTION
# ─────────────────────────────────────────────

def process_tts(translation: dict, target_language: str,
                job_id: str, video_path: str) -> str:
    """
    Main TTS function — upload.py pipeline se yahi call hota hai.

    Flow:
    1. Video duration nikalo
    2. Har segment ke liye TTS generate karo
    3. Sab segments merge karo ek audio mein

    Args:
        translation: translate_full_pipeline ka output
        target_language: TTS language code
        job_id: Job identifier
        video_path: Original video path (duration ke liye)

    Returns:
        final_audio_path: Complete dubbed audio file ka path
    """
    print(f"\n{'='*50}")
    print(f"🔊 TTS Pipeline starting for job: {job_id}")
    print(f"   Language : {target_language}")
    print(f"   Segments : {len(translation['segments'])}")
    print(f"{'='*50}\n")

    # Video duration
    total_duration = get_video_duration(video_path)
    print(f"   Video duration: {total_duration:.1f}s")

    # Segment-level TTS
    segments_with_audio = generate_tts_for_segments(
        translation["segments"],
        target_language,
        job_id
    )

    # Final merge
    final_audio_path = merge_tts_segments(
        segments_with_audio,
        job_id,
        total_duration
    )

    print(f"\n✅ TTS Pipeline complete!")
    print(f"   Output: {final_audio_path}\n")

    return final_audio_path