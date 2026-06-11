# app/services/translation.py
# Yeh file transcribed text ko target language mein translate karti hai.
# deep-translator library use karti hai jo Google Translate ko free mein use karta hai.
# Koi API key nahi chahiye MVP ke liye.

from deep_translator import GoogleTranslator
from typing import List

# Supported languages reference
SUPPORTED_LANGUAGES = {
    "hi": "Hindi",
    "es": "Spanish", 
    "fr": "French",
    "de": "German",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ar": "Arabic",
    "pt": "Portuguese",
    "ru": "Russian",
    "it": "Italian",
}


def translate_text(text: str, target_language: str, source_language: str = "auto") -> str:
    """
    Single text string translate karo.
    
    Args:
        text: Translate karne wala text
        target_language: Target language code (e.g. 'hi', 'es')
        source_language: Source language (default: auto-detect)
    
    Returns:
        Translated text string
    """
    if not text or not text.strip():
        return text

    try:
        translator = GoogleTranslator(
            source=source_language,
            target=target_language
        )
        translated = translator.translate(text)
        return translated if translated else text

    except Exception as e:
        print(f"⚠️ Translation failed for text: '{text[:50]}...' | Error: {e}")
        # Fail hone par original text return karo
        return text


def translate_segments(segments: List[dict], target_language: str,
                        source_language: str = "auto") -> List[dict]:
    """
    Whisper segments ki list translate karo.
    Har segment alag translate hota hai — better accuracy ke liye.
    
    Args:
        segments: Whisper segments list
                  [{"start": 0.0, "end": 2.5, "text": "Hello"}]
        target_language: Target language code
        source_language: Source language code
    
    Returns:
        Translated segments list (same structure, text translated)
    """
    print(f"🌐 Translating {len(segments)} segments to '{target_language}'...")

    translated_segments = []

    for i, segment in enumerate(segments):
        original_text = segment["text"]

        # Translate karo
        translated_text = translate_text(
            original_text,
            target_language,
            source_language
        )

        # Same structure rakho, sirf text replace karo
        translated_segments.append({
            "start": segment["start"],
            "end": segment["end"],
            "text": translated_text,
            "original_text": original_text  # Debug ke liye original bhi rakho
        })

        # Progress print karo har 10 segments par
        if (i + 1) % 10 == 0:
            print(f"   Translated {i + 1}/{len(segments)} segments...")

    print(f"✅ Translation complete! {len(translated_segments)} segments translated")
    return translated_segments


def translate_full_pipeline(transcription: dict, target_language: str) -> dict:
    """
    Main function — poori transcription translate karo.
    Pipeline mein yahi call hoga.
    
    Args:
        transcription: Whisper ka output dict
                      {"text": "...", "language": "en", "segments": [...]}
        target_language: Target language code
    
    Returns:
        Translation result dict
    """
    source_language = transcription.get("language", "auto")

    print(f"🌐 Starting translation: {source_language} → {target_language}")

    # Full text translate karo
    translated_text = translate_text(
        transcription["text"],
        target_language,
        source_language
    )

    # Segments translate karo
    translated_segments = translate_segments(
        transcription["segments"],
        target_language,
        source_language
    )

    result = {
        "original_text": transcription["text"],
        "translated_text": translated_text,
        "source_language": source_language,
        "target_language": target_language,
        "segments": translated_segments
    }

    print(f"📝 Translation preview:")
    print(f"   Original : {result['original_text'][:100]}")
    print(f"   Translated: {result['translated_text'][:100]}")

    return result