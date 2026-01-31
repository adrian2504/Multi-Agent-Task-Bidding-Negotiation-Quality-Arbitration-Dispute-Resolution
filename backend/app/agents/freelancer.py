from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from ..core.models import Bid, Task
from ..llm.base import LLM

@dataclass
class FreelancerProfile:
    freelancer_id: str
    portfolio_score: float
    base_speed: int           # lower = faster
    base_price: float
    risk_flags: list[str]

async def propose_bid(task: Task, p: FreelancerProfile, llm: Optional[LLM] = None) -> Bid:
    # Deterministic bid math (v0.2 will add negotiation rounds)
    price = min(task.budget_usd, p.base_price + (len(task.acceptance_criteria) * 15))
    eta = max(1, p.base_speed + (len(task.acceptance_criteria) // 2))
    confidence = max(0.35, min(0.95, 0.6 + 0.4 * p.portfolio_score - 0.08 * len(p.risk_flags)))

    notes = None
    if llm:
        notes = await llm.generate(
    prompt=(
        "Return ONLY the bid note text. No preamble, no quotes.\n"
        f"Task: {task.title}\n"
        f"Criteria: {task.acceptance_criteria}\n"
        f"Price: {price}, ETA days: {eta}, confidence: {confidence:.2f}"
    ),
    system="Write a concise 1–2 sentence freelancer bid note. Output only the note."
    )


    return Bid(
        freelancer_id=p.freelancer_id,
        price_usd=float(price),
        eta_days=int(eta),
        confidence=float(confidence),
        portfolio_score=float(p.portfolio_score),
        risk_flags=list(p.risk_flags),
        notes=notes,
    )
