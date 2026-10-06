from typing import List, Optional
from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    customer_name: str = "Demo Customer"
    agent_name: str = "Demo Agent"
    transcript: str = Field(min_length=10)

class ActionItem(BaseModel):
    owner: str
    action: str
    due: str

class CallSummary(BaseModel):
    id: str
    customer_name: str
    agent_name: str
    duration_sec: int
    sentiment: str
    sentiment_score: float
    intent: str
    urgency: str
    resolution: str
    csat: Optional[float] = None
    summary: str
    topics: List[str]
    action_items: List[ActionItem]
    transcript: str
    created_at: str
