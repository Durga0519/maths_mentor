import whisper

model = whisper.load_model("base")

def transcribe_audio(audio_file):
    """
    Returns (text, confidence) tuple.
    Whisper doesn't expose a simple confidence scalar, so we derive it
    from the mean of per-segment avg_logprob (mapped to 0–1).
    """
    result = model.transcribe(audio_file)
    text   = result.get("text", "").strip()

    segments = result.get("segments", [])
    if segments:
        avg_logprob = sum(s.get("avg_logprob", -1.0) for s in segments) / len(segments)
        # avg_logprob is typically in [-2, 0]; map to [0, 1]
        confidence = max(0.0, min(1.0, 1.0 + avg_logprob / 2.0))
    else:
        confidence = 0.5   # unknown

    return text, round(confidence, 3)