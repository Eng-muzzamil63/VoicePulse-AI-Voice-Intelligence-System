from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

DEMO_MODE = os.getenv("VOICEPULSE_DEMO_MODE", "true").lower() == "true"
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
TRANSFORMER_SENTIMENT_MODEL = os.getenv(
    "TRANSFORMER_SENTIMENT_MODEL",
    "distilbert-base-uncased-finetuned-sst-2-english",
)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000")
