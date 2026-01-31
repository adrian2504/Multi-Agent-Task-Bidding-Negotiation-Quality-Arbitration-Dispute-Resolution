from __future__ import annotations
from .models import DecisionReport, Task, Bid
from .scoring import score_bid

def pick_winner(task: Task, bids: list[Bid], weights: dict) -> DecisionReport:
    max_eta = max(b.eta_days for b in bids) if bids else 1
    scores = {}
    for b in bids:
        scores[b.freelancer_id] = score_bid(b, task.budget_usd, max_eta, weights)

    winner_id = max(scores.items(), key=lambda kv: kv[1].total)[0]

    rationale = [
        f"Winner chosen by multi-attribute scoring (price + ETA + expected quality − risk).",
        f"Budget: ${task.budget_usd:.0f}. Bids evaluated deterministically.",
        f"Winner '{winner_id}' had the highest total score after risk/quality normalization."
    ]

    referee_summary = {
        "tests_passing": True,
        "rubric_score": 8.5,
        "style_score": 9.0,
        "plagiarism_risk": "low",
        "note": "v0.1 uses stub referee metrics (v0.3 will run real tests + rubric evaluation).",
    }

    return DecisionReport(
        task=task,
        weights=weights,
        bids=bids,
        scores=scores,
        winner_id=winner_id,
        rationale=rationale,
        referee_summary=referee_summary,
    )
