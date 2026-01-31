from __future__ import annotations
from typing import Optional, Dict
import random

from ..core.models import Task, DecisionReport
from ..core.report import pick_winner
from ..agents.freelancer import FreelancerProfile, propose_bid
from ..llm.base import LLM
from ..core.ledger import Ledger
from .negotiation import propose_counteroffers, apply_counteroffer

DEFAULT_WEIGHTS = {"price": 0.9, "eta": 0.35, "quality": 1.2, "risk": 1.1}

async def run_demo(
    llm: Optional[LLM] = None,
    *,
    seed: int = 42,
    rounds: int = 2,
    weights: Optional[Dict[str, float]] = None,
) -> DecisionReport:
    rng = random.Random(seed)
    ledger = Ledger()
    w = weights or DEFAULT_WEIGHTS

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

    ledger.add("TASK_POSTED", f"Task posted: {task.title}", round=0, data={"budget_usd": task.budget_usd})

    freelancers = [
        FreelancerProfile("cheap_risky", 0.35, base_speed=2, base_price=80,  risk_flags=["low_test_coverage", "copy_paste_history"]),
        FreelancerProfile("steady_mid",  0.70, base_speed=3, base_price=140, risk_flags=[]),
        FreelancerProfile("fast_good",   0.78, base_speed=2, base_price=165, risk_flags=["tight_schedule"]),
        FreelancerProfile("slow_safe",   0.82, base_speed=5, base_price=150, risk_flags=[]),
        FreelancerProfile("premium",     0.92, base_speed=3, base_price=210, risk_flags=[]),
    ]

    bids = []
    for f in freelancers:
        b = await propose_bid(task, f, llm=llm)
        bids.append(b)
        ledger.add("BID_SUBMITTED", f"Bid submitted by {b.freelancer_id}", round=0, data=b.model_dump())

    # Negotiation rounds
    for r in range(1, rounds + 1):
        leader, offers = propose_counteroffers(task, bids, w, rng)

        ledger.add(
            "COUNTEROFFER_SENT",
            f"Mediator sent round {r} counteroffers (leader: {leader})",
            round=r,
            data={"leader": leader, "offers": [o.__dict__ for o in offers]},
        )

        # Apply responses
        new_bids = []
        for b in bids:
            offer = next(o for o in offers if o.freelancer_id == b.freelancer_id)
            updated = apply_counteroffer(b, offer, rng)
            new_bids.append(updated)

            ledger.add(
                "COUNTEROFFER_RESPONSE",
                f"{b.freelancer_id} responded to counteroffer",
                round=r,
                data={"before": b.model_dump(), "after": updated.model_dump()},
            )

        bids = new_bids
        ledger.add("ROUND_COMPLETE", f"Round {r} complete", round=r)

    report = pick_winner(task, bids, w)
    report.events = ledger.events

    ledger.add("WINNER_SELECTED", f"Winner selected: {report.winner_id}", round=rounds, data={"winner_id": report.winner_id})
    report.events = ledger.events  # include final event

    return report
