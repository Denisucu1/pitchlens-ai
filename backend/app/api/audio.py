from fastapi import APIRouter, Response, HTTPException, Query
import re
from typing import Dict
import edge_tts

audio_router = APIRouter(prefix="/api/audio", tags=["Audio Commentary"])

# In-memory LRU audio cache to avoid re-generating audio for repeated phrases:
# Key: f"{voice}:{cleaned_text}" -> bytes
_AUDIO_CACHE: Dict[str, bytes] = {}
_MAX_CACHE_SIZE = 150

def get_voice_for_language(lang: str) -> str:
    lang_clean = lang.lower().strip()
    if "ro" in lang_clean:
        return "ro-RO-EmilNeural"   # Authentic Romanian male sports commentator voice
    elif "es" in lang_clean:
        return "es-ES-AlvaroNeural"  # Passionate Spanish football commentator voice
    else:
        return "en-GB-RyanNeural"   # Authentic British Premier League TV commentator voice

def clean_speech_text(text: str) -> str:
    # Remove bracketed telemetry e.g. [xG: 0.82 | ...]
    text = re.sub(r"\[.*?\]", "", text)
    # Remove emojis and graphical icons
    text = re.sub(r"[\U00010000-\U0010ffff]|[\u2600-\u27bf]|⭐|⚡|🔥|🛡️|⚽|👀|🎯|🚩|💥|🧤|⚠️", "", text)
    # Collapse multiple whitespaces
    return re.sub(r"\s+", " ", text).strip()

@audio_router.get("/tts")
async def stream_neural_tts(
    text: str = Query(..., description="Commentary text to speak"),
    lang: str = Query("ro", description="Language code ('ro', 'en', 'es')")
):
    """
    Generates broadcast-quality Microsoft Cognitive Neural Voice audio (MP3).
    Supports Romanian (EmilNeural), English (RyanNeural UK), and Spanish (AlvaroNeural).
    """
    cleaned = clean_speech_text(text)
    if not cleaned:
        raise HTTPException(status_code=400, detail="Empty commentary text after sanitization")

    voice = get_voice_for_language(lang)
    cache_key = f"{voice}:{cleaned}"

    # Return cached audio if available
    if cache_key in _AUDIO_CACHE:
        return Response(
            content=_AUDIO_CACHE[cache_key],
            media_type="audio/mpeg",
            headers={"X-Audio-Cache": "HIT"}
        )

    try:
        communicator = edge_tts.Communicate(text=cleaned, voice=voice)
        audio_chunks = []
        async for chunk in communicator.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])

        audio_bytes = b"".join(audio_chunks)
        if len(audio_bytes) > 0:
            if len(_AUDIO_CACHE) >= _MAX_CACHE_SIZE:
                # Evict oldest entry
                _AUDIO_CACHE.pop(next(iter(_AUDIO_CACHE)))
            _AUDIO_CACHE[cache_key] = audio_bytes
            return Response(
                content=audio_bytes,
                media_type="audio/mpeg",
                headers={"X-Audio-Cache": "MISS"}
            )
        else:
            raise HTTPException(status_code=500, detail="No audio stream generated")
    except Exception as e:
        print(f"[Neural TTS Error] {e}")
        raise HTTPException(status_code=500, detail=f"TTS error: {e}")
