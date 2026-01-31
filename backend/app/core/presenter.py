from __future__ import annotations
from typing import Any, Dict, List
from .models import DecisionReport

def _round(x: float, n: int = 4) -> float:
    return float(round(x, n))

def to_ui(report: DecisionReport) -> Dict[str, Any]:
    # Build flat rows
    rows: List[Dict[str, Any]] = []
    for bid in report.bids:
        sb = report.scores[bid.freelancer_id]
        rows.append({
            "freelancerId": bid.freelancer_id,
            "priceUsd": _round(bid.price_usd, 2),
            "etaDays": bid.eta_days,
            "confidence": _round(bid.confidence, 3),
            "portfolioScore": _round(bid.portfolio_score, 3),
            "riskFlags": bid.risk_flags,
            "notes": (bid.notes or "").strip(),
            "score": {
                "price": _round(sb.price_term),
                "eta": _round(sb.eta_term),
                "quality": _round(sb.quality_term),
                "risk": _round(sb.risk_term),
                "total": _round(sb.total),
            },
        })

    # Rank by total score
    rows.sort(key=lambda r: r["score"]["total"], reverse=True)
    for i, r in enumerate(rows, start=1):
        r["rank"] = i
        r["isWinner"] = (r["freelancerId"] == report.winner_id)

    winner_row = next(r for r in rows if r["isWinner"])

    return {
        "task": {
            "id": report.task.id,
            "title": report.task.title,
            "budgetUsd": _round(report.task.budget_usd, 2),
            "acceptanceCriteria": report.task.acceptance_criteria,
        },
        "weights": report.weights,
        "winner": {
            "freelancerId": report.winner_id,
            "totalScore": winner_row["score"]["total"],
            "highlights": report.rationale,
        },
        "referee": report.referee_summary,
        "bids": rows,
    }
