from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import uuid4

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
    scores: Dict[str, ScoreBreakdown]  # key: freelancer_id
    winner_id: str
    rationale: List[str]
    referee_summary: Dict[str, Any]
