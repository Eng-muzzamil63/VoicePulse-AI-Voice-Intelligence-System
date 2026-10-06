# VoicePulse AI — Voice Intelligence System

VoicePulse AI is a portfolio-ready customer conversation intelligence platform. It turns voice/audio into searchable, decision-ready support intelligence.

## What it solves
Support teams often have thousands of calls but limited time to review them. VoicePulse can transcribe calls, detect sentiment, classify intent, estimate urgency, surface topics, identify action items, and create a concise case summary.

## Stack
- FastAPI + Python
- Optional faster-whisper for open-source speech-to-text
- Optional Hugging Face Transformers / DistilBERT for sentiment
- Optional Sentence-Transformers for semantic intent classification
- Next.js + React + TypeScript
- SVG/CSS UI with responsive layout

## Core flow
Audio -> Whisper -> Transcript -> Deep NLP -> Conversation Intelligence -> FastAPI -> Next.js

## Run backend
```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs

## Enable open-source deep-learning models
```powershell
python -m pip install -r requirements-ai.txt
```
The first inference can download model weights. CPU inference works for demos; GPU/CUDA is recommended for high-volume workloads.

## Run frontend
```powershell
cd frontend
npm install
npm run dev
```
Open http://localhost:3000

## Demo mode
The dashboard works immediately using seeded synthetic call data. Use **Analyze transcript** to test a new conversation without audio, or **Upload audio** after installing the optional AI requirements.

## Important
The included call data is synthetic. This project is for portfolio/demo use and not for automated employment, medical, legal, or other high-stakes decisions.
