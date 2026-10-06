from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import random

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "calls.json"

CUSTOMERS = ["Aisha Khan", "Daniel Reed", "Maya Patel", "Owen Carter", "Sofia Malik", "Liam Brooks", "Noah Williams", "Emma Chen"]
AGENTS = ["Nora", "Ethan", "Amelia", "Rayan"]
TRANSCRIPTS = [
    "Hi, I was charged twice for the same order and the invoice also shows the wrong amount. I am frustrated because my card was charged twice. Please review the payment and issue a refund. Thanks.",
    "My package is five days late and tracking has not moved. I need this resolved today because it is for a customer event tomorrow. Can you escalate this to the delivery team and call me back?",
    "I cannot log in to my account after changing my password. I have tried the verification step three times and now the account is locked. Please help me regain access as soon as possible.",
    "The integration stopped working after the update. We get an API error every time the system tries to sync. Engineering needs to investigate the bug, but the rest of the service is working.",
    "I really like the product and your support team was excellent. Everything was resolved quickly and I wanted to say thank you.",
    "I would like to cancel my subscription. I no longer need the premium plan. Please confirm when the cancellation is complete.",
    "Can you explain whether the new device supports USB-C charging and whether the advanced reporting feature is included in the standard plan?",
    "I requested a refund last week and still do not see the money back. Please check the refund status and follow up with me today.",
    "The courier marked the order delivered but it is missing. This is urgent because I need the package before tonight. Please escalate it immediately.",
    "The invoice looks correct now and I can confirm the duplicate charge has been resolved. Thank you for fixing it.",
    "Our team cannot access the dashboard and the login system seems broken. We have a deployment deadline, so this is critical. Please have someone call me now.",
    "Everything has been great so far. The product works exactly as expected and the onboarding was very helpful.",
]

def seed():
    rng = random.Random(42)
    now = datetime.now(timezone.utc)
    calls = []
    for i, transcript in enumerate(TRANSCRIPTS, 1):
        calls.append({
            "id": f"CALL-{202600 + i}",
            "customer_name": CUSTOMERS[(i - 1) % len(CUSTOMERS)],
            "agent_name": AGENTS[(i - 1) % len(AGENTS)],
            "duration_sec": rng.randint(180, 980),
            "transcript": transcript,
            "created_at": (now - timedelta(hours=i * 3)).isoformat(),
            "csat": round(rng.uniform(2.4, 5.0), 1),
        })
    DATA_FILE.write_text(json.dumps(calls, indent=2), encoding="utf-8")
    return calls

def load_calls():
    if not DATA_FILE.exists():
        return seed()
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))
