"""Walk matrix powers and return probabilities.

Phase DIV — The probability of return to origin after t steps on the
random walk (lazy or uniform) on k-regular SRG:
p_t(v→v) = (1/v)[1 + f(r/k)^t + g(s/k)^t].
At t=2: p₂ = (1/40)[1 + 24(1/6)² + 15(1/3)²] = (1+24/36+15/9)/40
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from fractions import Fraction

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def build_walk_return_summary() -> dict:
    v, k, lam, mu, q = 40, 12, 2, 4, 3
    r, s = 2, -4
    f, g = 24, 15
    # Return probability at time t
    # p_t = (1/v) Σ m_i × (λ_i/k)^t
    # p_0 = (1+24+15)/40 = 1.0 (trivially)
    p0 = Fraction(1 + f + g, v)  # 40/40 = 1
    # p_1 = (1/40)[1×1 + 24×(1/6) + 15×(-1/3)] = (1+4-5)/40 = 0
    p1 = Fraction(1, v) * (1 + f * Fraction(r, k) + g * Fraction(s, k))
    # = (1 + 24×1/6 + 15×(-1/3))/40 = (1+4-5)/40 = 0/40 = 0
    # p_2 = (1/40)[1 + 24×(1/6)² + 15×(1/3)²]
    p2 = Fraction(1, v) * (1 + f * Fraction(r, k)**2 + g * Fraction(s, k)**2)
    # = (1 + 24/36 + 15/9)/40 = (1 + 2/3 + 5/3)/40 = (1+7/3)/40 = (10/3)/40 = 1/12
    # p_2 = 1/12 = 1/k! Because p_2 = k/v × (1/k) = ... 
    p2_expected = Fraction(1, k)  # 1/12
    # p_∞ = 1/v (stationary) = 1/40
    p_inf = Fraction(1, v)
    return {
        "status": "ok",
        "walk_return": {
            "p0": str(p0),
            "p1": str(p1),
            "p2": str(p2),
            "p_inf": str(p_inf),
        },
        "walk_return_theorem": {
            "p0_is_1": p0 == 1,
            "p1_is_0": p1 == 0,
            "p2_is_1_over_k": p2 == p2_expected,
            "stationary_1_over_v": p_inf == Fraction(1, v),
            "therefore_walk_exact": (
                p0 == 1 and p1 == 0 and p2 == p2_expected
            ),
        },
    }
