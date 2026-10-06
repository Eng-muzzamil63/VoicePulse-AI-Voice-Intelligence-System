from __future__ import annotations
from datetime import datetime, timezone
import json
import os
import shutil
import uuid
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .config import CORS_ORIGINS, UPLOAD_DIR, WHISPER_MODEL
from .schemas import AnalyzeRequest
from .services.nlp import analyze_transcript
from .services.seed import load_calls, seed

app = FastAPI(title="VoicePulse AI", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in CORS_ORIGINS.split(",") if x.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def enriched_calls():
    out = []
    for c in load_calls():
        a = analyze_transcript(c["transcript"])
        out.append({**c, **a})
    return out

@app.get("/")
def root():
    return {"product": "VoicePulse AI", "status": "ok"}

@app.get("/api/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.post("/api/seed")
def seed_demo():
    calls = seed()
    return {"seeded": len(calls)}

@app.get("/api/overview")
def overview():
    calls = enriched_calls()
    total = len(calls)
    negative = sum(c["sentiment"] == "Negative" for c in calls)
    high_urgency = sum(c["urgency"] in {"High", "Critical"} for c in calls)
    resolved = sum(c["resolution"] == "Resolved" for c in calls)
    avg_csat = round(sum(c.get("csat") or 0 for c in calls) / max(total, 1), 1)
    return {
        "calls_today": total,
        "negative_sentiment_pct": round(negative / max(total, 1) * 100),
        "high_urgency_calls": high_urgency,
        "resolution_rate": round(resolved / max(total, 1) * 100),
        "avg_csat": avg_csat,
        "deep_learning": {
            "sentiment": "DistilBERT (optional)",
            "intent": "Sentence-Transformer (optional)",
            "speech_to_text": f"Whisper / faster-whisper ({WHISPER_MODEL})",
        },
    }

@app.get("/api/trends")
def trends():
    calls = enriched_calls()
    data = []
    for i, c in enumerate(sorted(calls, key=lambda x: x["created_at"])):
        data.append({
            "label": c["id"][-3:],
            "sentiment": round((1 - c["sentiment_score"]) * 100 if c["sentiment"] == "Negative" else c["sentiment_score"] * 100),
            "urgency": round(c["urgency_score"] * 100),
            "csat": c.get("csat", 0),
        })
    return data

@app.get("/api/calls")
def calls(search: str = "", sentiment: str = "all", urgency: str = "all"):
    result = enriched_calls()
    s = search.lower().strip()
    if s:
        result = [c for c in result if s in c["customer_name"].lower() or s in c["agent_name"].lower() or s in c["transcript"].lower() or s in c["intent"].lower()]
    if sentiment.lower() != "all":
        result = [c for c in result if c["sentiment"].lower() == sentiment.lower()]
    if urgency.lower() != "all":
        result = [c for c in result if c["urgency"].lower() == urgency.lower()]
    return result

@app.get("/api/calls/{call_id}")
def call_detail(call_id: str):
    for c in enriched_calls():
        if c["id"] == call_id:
            return c
    raise HTTPException(404, detail="Call not found")

@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    result = analyze_transcript(req.transcript)
    return {
        "id": f"LIVE-{uuid.uuid4().hex[:8].upper()}",
        "customer_name": req.customer_name,
        "agent_name": req.agent_name,
        "duration_sec": max(60, min(3600, len(req.transcript.split()) * 3)),
        "transcript": req.transcript,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "csat": None,
        **result,
    }

@app.post("/api/transcribe")
def transcribe(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename or "audio")[1].lower()
    if suffix not in {".wav", ".mp3", ".m4a", ".mp4", ".webm", ".ogg"}:
        raise HTTPException(400, detail="Upload WAV, MP3, M4A, MP4, WebM, or OGG audio.")
    path = UPLOAD_DIR / f"{uuid.uuid4().hex}{suffix}"
    with path.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
        segments, info = model.transcribe(str(path), vad_filter=True)
        text = " ".join(seg.text.strip() for seg in segments).strip()
        if not text:
            raise HTTPException(422, detail="No speech detected in audio.")
        analysis = analyze_transcript(text)
        return {"filename": file.filename, "language": info.language, "transcript": text, **analysis}
    except ImportError:
        raise HTTPException(503, detail="Voice transcription is optional. Install backend/requirements-ai.txt to enable open-source Whisper transcription.")
    except Exception as exc:
        raise HTTPException(500, detail=f"Transcription failed: {exc}")
    finally:
        try:
            path.unlink(missing_ok=True)
        except Exception:
            pass
