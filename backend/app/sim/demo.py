from __future__ import annotations
from typing import Optional
from ..core.models import Task, DecisionReport
from ..core.report import pick_winner
from ..agents.freelancer import FreelancerProfile, propose_bid
from ..llm.base import LLM

DEFAULT_WEIGHTS = {"price": 0.9, "eta": 0.35, "quality": 1.2, "risk": 1.1}

async def run_demo(llm: Optional[LLM] = None) -> DecisionReport:
    task = Task(
        title="Implement a FastAPI endpoint + unit tests",
        acceptance_criteria=[
            "POST /tasks creates a task",
            "POST /tasks/{id}/run selects winner",
            "Return a JSON decision report",
            "Include basic unit tests",
        ],
        budget_usd=250,
    )

    freelancers = [
        FreelancerProfile("cheap_risky", 0.35, base_speed=2, base_price=80,  risk_flags=["low_test_coverage", "copy_paste_history"]),
        FreelancerProfile("steady_mid",  0.70, base_speed=3, base_price=140, risk_flags=[]),
        FreelancerProfile("fast_good",   0.78, base_speed=2, base_price=165, risk_flags=["tight_schedule"]),
        FreelancerProfile("slow_safe",   0.82, base_speed=5, base_price=150, risk_flags=[]),
        FreelancerProfile("premium",     0.92, base_speed=3, base_price=210, risk_flags=[]),
    ]

    bids = []
    for f in freelancers:
        bids.append(await propose_bid(task, f, llm=llm))

    return pick_winner(task, bids, DEFAULT_WEIGHTS)
