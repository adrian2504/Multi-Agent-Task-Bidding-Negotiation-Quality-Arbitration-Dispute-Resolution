from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from uuid import uuid4
from datetime import datetime

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    acceptance_criteria: List[str]
    budget_usd: float

class Bid(BaseModel):
    freelancer_id: str
    price_usd: float
    eta_days: int
    confidence: float  # 0..1
    portfolio_score: float  # 0..1
    risk_flags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None

class ScoreBreakdown(BaseModel):
    price_term: float
    eta_term: float
    quality_term: float
    risk_term: float
    total: float

class DecisionReport(BaseModel):
    task: Task
    weights: Dict[str, float]
    bids: List[Bid]
    scores: Dict[str, ScoreBreakdown]
    winner_id: str
    rationale: List[str]
    referee_summary: Dict[str, Any]
    events: List["Event"] = Field(default_factory=list)
    score_history: List[Dict[str, Any]] = Field(default_factory=list)




EventType = Literal[
    "TASK_POSTED",
    "BID_SUBMITTED",
    "COUNTEROFFER_SENT",
    "COUNTEROFFER_RESPONSE",
    "ROUND_COMPLETE",
    "WINNER_SELECTED",
]

class Event(BaseModel):
    run_id: str
    seq: int
    type: EventType
    ts: str  # ISO string
    round: int = 0
    summary: str
    data: Dict[str, Any] = Field(default_factory=dict)