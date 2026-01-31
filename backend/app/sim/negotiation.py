from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple
import random

from ..core.models import Bid, Task
from ..core.scoring import score_bid

@dataclass
class CounterOffer:
    freelancer_id: str
    target_price_usd: float
    target_eta_days: int

def propose_counteroffers(
    task: Task,
    bids: List[Bid],
    weights: Dict[str, float],
    rng: random.Random,
) -> Tuple[str, List[CounterOffer]]:
    # Compute current best score
    max_eta = max(b.eta_days for b in bids) if bids else 1
    scored = []
    for b in bids:
        sb = score_bid(b, task.budget_usd, max_eta, weights)
        scored.append((b, sb.total))
    scored.sort(key=lambda x: x[1], reverse=True)
    leader = scored[0][0].freelancer_id

    offers: List[CounterOffer] = []
    for b, _ in scored:
        # Simple deterministic-ish improvement request:
        # Ask expensive bids to move closer to budget, and very slow bids to shave ETA.
        price_target = min(b.price_usd, task.budget_usd * (0.92 + 0.03 * rng.random()))
        eta_target = b.eta_days
        if b.eta_days > 5:
            eta_target = max(2, b.eta_days - 1)

        offers.append(CounterOffer(
            freelancer_id=b.freelancer_id,
            target_price_usd=float(round(price_target, 2)),
            target_eta_days=int(eta_target),
        ))

    return leader, offers

def apply_counteroffer(
    bid: Bid,
    offer: CounterOffer,
    rng: random.Random,
) -> Bid:
    # Each freelancer responds with limited flexibility:
    # - may partially accept price reduction
    # - may reduce ETA if not already tight
    new_price = bid.price_usd
    new_eta = bid.eta_days

    # price move: accept 60%–100% of requested improvement
    if offer.target_price_usd < bid.price_usd:
        alpha = 0.6 + 0.4 * rng.random()
        new_price = bid.price_usd - alpha * (bid.price_usd - offer.target_price_usd)

    # eta move: accept 0 or 1 day improvement if possible
    if offer.target_eta_days < bid.eta_days:
        if rng.random() > 0.35:
            new_eta = bid.eta_days - 1

    # Confidence: if ETA gets tighter or price drops a lot, reduce confidence slightly
    conf = bid.confidence
    if new_eta < bid.eta_days:
        conf -= 0.02
    if new_price < bid.price_usd * 0.9:
        conf -= 0.03

    # Risk flags: if schedule tightens, add a flag (demo realism)
    risk = list(bid.risk_flags)
    if new_eta <= 3 and "tight_schedule" not in risk:
        risk.append("tight_schedule")

    return bid.model_copy(update={
        "price_usd": float(round(new_price, 2)),
        "eta_days": int(new_eta),
        "confidence": max(0.3, min(0.95, float(round(conf, 3)))),
        "risk_flags": risk,
    })
