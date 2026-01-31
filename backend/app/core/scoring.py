from __future__ import annotations
from .models import Bid, ScoreBreakdown

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def estimate_quality(b: Bid) -> float:
    # Simple expected quality proxy (recruiter-friendly + deterministic)
    # confidence and portfolio help; risk_flags hurts.
    risk_penalty = 0.12 * len(b.risk_flags)
    q = 0.55 * b.confidence + 0.45 * b.portfolio_score - risk_penalty
    return clamp(q, 0.0, 1.0)

def estimate_risk(b: Bid) -> float:
    # Risk is not just #flags; lower confidence increases risk too
    base = 0.15 * len(b.risk_flags)
    conf_penalty = (1.0 - b.confidence) * 0.35
    return clamp(base + conf_penalty, 0.0, 1.0)

def score_bid(
    b: Bid,
    budget_usd: float,
    max_eta_days: int,
    weights: dict,
) -> ScoreBreakdown:
    # Normalize: lower is better for price/eta; higher is better for quality; lower is better for risk.
    price_norm = clamp(b.price_usd / max(budget_usd, 1.0), 0.0, 2.0)        # 0..2
    eta_norm   = clamp(b.eta_days / max(max_eta_days, 1), 0.0, 2.0)         # 0..2
    quality    = estimate_quality(b)                                        # 0..1
    risk       = estimate_risk(b)                                           # 0..1

    price_term   = -weights["price"] * price_norm
    eta_term     = -weights["eta"] * eta_norm
    quality_term =  weights["quality"] * quality
    risk_term    = -weights["risk"] * risk

    total = price_term + eta_term + quality_term + risk_term
    return ScoreBreakdown(
        price_term=price_term,
        eta_term=eta_term,
        quality_term=quality_term,
        risk_term=risk_term,
        total=total,
    )
