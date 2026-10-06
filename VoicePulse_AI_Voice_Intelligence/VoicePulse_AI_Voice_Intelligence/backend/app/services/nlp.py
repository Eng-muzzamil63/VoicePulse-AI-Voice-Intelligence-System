from __future__ import annotations
from functools import lru_cache
from typing import Dict, List, Tuple
import re

INTENTS = [
    "Billing issue",
    "Refund request",
    "Delivery problem",
    "Account access",
    "Product question",
    "Technical support",
    "Cancellation",
    "Positive feedback",
]

INTENT_PROTOTYPES = {
    "Billing issue": ["charged twice invoice payment price incorrect bill card charged"],
    "Refund request": ["refund money back return reimbursement charge reversal"],
    "Delivery problem": ["delivery late shipment tracking courier package arrived"],
    "Account access": ["cannot login password account locked sign in verification"],
    "Product question": ["product feature specification how does it work compatible"],
    "Technical support": ["bug error broken not working integration technical"],
    "Cancellation": ["cancel subscription close plan stop service"],
    "Positive feedback": ["happy great excellent helpful satisfied love service"],
}

POSITIVE = {"great", "excellent", "happy", "helpful", "thanks", "thank", "perfect", "love", "satisfied", "resolved"}
NEGATIVE = {"angry", "frustrated", "terrible", "bad", "awful", "upset", "failed", "broken", "wrong", "late", "charged", "cannot", "can't", "issue", "problem"}
URGENT = {"urgent", "immediately", "today", "asap", "critical", "emergency", "blocked", "deadline", "now"}


def _tokens(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z']+", text.lower())

@lru_cache(maxsize=1)
def transformer_sentiment():
    try:
        from transformers import pipeline
        return pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    except Exception:
        return None

@lru_cache(maxsize=1)
def sentence_model():
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        return None


def analyze_sentiment(text: str) -> Tuple[str, float, str]:
    model = transformer_sentiment()
    if model:
        try:
            out = model(text[:3000])[0]
            raw = float(out["score"])
            if out["label"].upper() == "POSITIVE":
                return "Positive", raw, "Deep-learning sentiment model"
            return "Negative", raw, "Deep-learning sentiment model"
        except Exception:
            pass
    toks = _tokens(text)
    p = sum(t in POSITIVE for t in toks)
    n = sum(t in NEGATIVE for t in toks)
    score = (p - n) / max(len(toks), 1)
    if score > 0.03:
        return "Positive", min(0.99, 0.6 + score * 3), "Lexical fallback"
    if score < -0.03:
        return "Negative", min(0.99, 0.6 + abs(score) * 3), "Lexical fallback"
    return "Neutral", 0.62, "Lexical fallback"


def classify_intent(text: str) -> Tuple[str, float, str]:
    emb = sentence_model()
    if emb:
        try:
            import numpy as np
            query = emb.encode([text], normalize_embeddings=True)[0]
            labels = list(INTENT_PROTOTYPES)
            protos = emb.encode([INTENT_PROTOTYPES[x][0] for x in labels], normalize_embeddings=True)
            sims = protos @ query
            idx = int(np.argmax(sims))
            return labels[idx], float((sims[idx] + 1) / 2), "Sentence-Transformer semantic intent"
        except Exception:
            pass
    toks = set(_tokens(text))
    scores = {}
    for label, phrases in INTENT_PROTOTYPES.items():
        scores[label] = len(toks & set(_tokens(phrases[0])))
    label = max(scores, key=scores.get)
    score = min(0.95, 0.55 + scores[label] * 0.07)
    return label, score, "Keyword fallback"


def urgency(text: str, sentiment: str) -> Tuple[str, float]:
    toks = set(_tokens(text))
    hits = len(toks & URGENT)
    if hits >= 2 or ("blocked" in toks and sentiment == "Negative"):
        return "Critical", 0.93
    if hits == 1 or sentiment == "Negative" and len(toks) > 30:
        return "High", 0.79
    if sentiment == "Negative":
        return "Medium", 0.63
    return "Low", 0.42


def topics(text: str) -> List[str]:
    lower = text.lower()
    mapping = {
        "payment": ["payment", "charged", "invoice", "billing"],
        "delivery": ["delivery", "shipping", "courier", "arrive", "tracking"],
        "refund": ["refund", "money back", "return"],
        "account": ["login", "password", "account", "verification"],
        "subscription": ["subscription", "plan", "cancel"],
        "product": ["product", "feature", "compatible", "specification"],
        "technical": ["bug", "error", "not working", "integration"],
    }
    found = []
    for topic, kws in mapping.items():
        if any(k in lower for k in kws):
            found.append(topic)
    return found[:5] or ["general support"]


def action_items(text: str) -> List[Dict[str, str]]:
    t = text.lower()
    items = []
    patterns = [
        (r"refund", "Billing team", "Review/refund the disputed charge", "24h"),
        (r"call me|follow up|follow-up", "Account owner", "Follow up with the customer", "24h"),
        (r"escalat", "Support lead", "Escalate the case to a specialist", "4h"),
        (r"invoice|charged twice|billing", "Billing team", "Validate invoice and payment ledger", "24h"),
        (r"bug|error|not working", "Engineering", "Reproduce and investigate the reported issue", "48h"),
    ]
    for pattern, owner, action, due in patterns:
        if re.search(pattern, t):
            items.append({"owner": owner, "action": action, "due": due})
    return items[:3]


def analyze_transcript(text: str) -> Dict:
    sentiment, sent_score, sent_method = analyze_sentiment(text)
    intent, intent_score, intent_method = classify_intent(text)
    urg, urg_score = urgency(text, sentiment)
    topics_found = topics(text)
    actions = action_items(text)
    resolution = "Resolved" if any(k in text.lower() for k in ["resolved", "fixed", "sorted", "thank you", "that works"]) else "Follow-up required"
    summary = _summary(text, intent, sentiment, urg, resolution)
    return {
        "sentiment": sentiment,
        "sentiment_score": round(sent_score, 3),
        "sentiment_method": sent_method,
        "intent": intent,
        "intent_score": round(intent_score, 3),
        "intent_method": intent_method,
        "urgency": urg,
        "urgency_score": round(urg_score, 3),
        "resolution": resolution,
        "topics": topics_found,
        "action_items": actions,
        "summary": summary,
    }


def _summary(text: str, intent: str, sentiment: str, urg: str, resolution: str) -> str:
    words = text.strip().split()
    snippet = " ".join(words[:34]).rstrip(".,")
    return f"Customer discussed {intent.lower()} with {sentiment.lower()} sentiment. Urgency is {urg.lower()}, and the case is currently marked {resolution.lower()}. Key context: {snippet}."
