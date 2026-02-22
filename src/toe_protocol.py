"""Utilities for a falsifiability-first Theory of Everything (ToE) workflow.

This module turns high-level ToE requirements into a compact, reproducible score.
The goal is not to declare a final ToE, but to prioritize models that are both
mathematically coherent and experimentally testable.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TheoryCandidate:
    """Evaluation snapshot for a proposed ToE framework.

    Each field should be a value in [0.0, 1.0].

    - 0.0 means no support for the criterion.
    - 1.0 means criterion is fully met at current evidence quality.
    """

    name: str
    reproduces_gravity: float
    reproduces_standard_model: float
    dark_sector_explanatory_power: float
    quantitative_predictions: float
    consistency_and_uv_completion: float


def _clamp01(value: float) -> float:
    """Clamp a value into [0.0, 1.0]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def toe_readiness_score(candidate: TheoryCandidate) -> float:
    """Compute a weighted readiness score in [0.0, 1.0].

    The weighting emphasizes Standard Model recovery and mathematical consistency,
    which are usually the hardest bottlenecks.
    """

    w_gr = 0.20
    w_sm = 0.25
    w_dm = 0.15
    w_pred = 0.20
    w_consistency = 0.20

    score = (
        w_gr * _clamp01(candidate.reproduces_gravity)
        + w_sm * _clamp01(candidate.reproduces_standard_model)
        + w_dm * _clamp01(candidate.dark_sector_explanatory_power)
        + w_pred * _clamp01(candidate.quantitative_predictions)
        + w_consistency * _clamp01(candidate.consistency_and_uv_completion)
    )

    return round(score, 4)


def toe_status_label(score: float) -> str:
    """Map readiness score to a qualitative status."""
    s = _clamp01(score)
    if s >= 0.90:
        return "candidate_toe"
    if s >= 0.70:
        return "promising_unification"
    if s >= 0.40:
        return "partial_framework"
    return "early_stage"


def weakest_link(candidate: TheoryCandidate) -> tuple[str, float]:
    """Return the weakest criterion for targeted iteration."""

    criteria = {
        "reproduces_gravity": _clamp01(candidate.reproduces_gravity),
        "reproduces_standard_model": _clamp01(candidate.reproduces_standard_model),
        "dark_sector_explanatory_power": _clamp01(
            candidate.dark_sector_explanatory_power
        ),
        "quantitative_predictions": _clamp01(candidate.quantitative_predictions),
        "consistency_and_uv_completion": _clamp01(
            candidate.consistency_and_uv_completion
        ),
    }
    return min(criteria.items(), key=lambda kv: kv[1])
