"""Theta function and modular form connection.

Phase DXII — The theta series Θ(q) = Σ a_n q^n counts closed walks of length n.
a₀ = v = 40, a₁ = 0, a₂ = 2E = 480, a₃ = 6T = 960.
The generating function f(x) = Σ a_n x^n = v/(1-k²x) for mean-field, but
exactly f(x) = 1/(1-kx) + f/(1-rx) + g/(1-sx).
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from fractions import Fraction

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def build_theta_modular_summary() -> dict:
    v, k, lam, mu, q = 40, 12, 2, 4, 3
    r, s = 2, -4
    f, g = 24, 15
    E = 240
    T = 160
    # Walk counts: a_n = tr(A^n) = k^n + f×r^n + g×s^n
    a0 = k**0 + f * r**0 + g * s**0     # 1 + 24 + 15 = 40 = v
    a1 = k**1 + f * r**1 + g * s**1     # 12 + 48 - 60 = 0
    a2 = k**2 + f * r**2 + g * s**2     # 144 + 96 + 240 = 480 = 2E
    a3 = k**3 + f * r**3 + g * s**3     # 1728 + 192 - 960 = 960 = 6T
    a4 = k**4 + f * r**4 + g * s**4     # 20736 + 384 + 3840 = 24960
    a5 = k**5 + f * r**5 + g * s**5     # 248832 + 768 - 15360 = 234240
    # a₄ = 24960 = v × k × (k² + f×r²/g + ... ) ... 
    # a₄ counts closed walks of length 4
    # Ratio a₄/a₂ = 24960/480 = 52
    ratio_42 = a4 // a2  # 52
    # 52 = v + k = 40 + 12 ✓
    ratio_is_v_plus_k = ratio_42 == v + k
    return {
        "status": "ok",
        "theta_modular": {
            "a0": a0, "a1": a1, "a2": a2, "a3": a3, "a4": a4, "a5": a5,
            "ratio_42": ratio_42,
        },
        "theta_modular_theorem": {
            "a0_v": a0 == v,
            "a1_0": a1 == 0,
            "a2_2E": a2 == 2 * E,
            "a3_6T": a3 == 6 * T,
            "ratio_v_plus_k": ratio_is_v_plus_k,
            "therefore_theta_verified": (
                a0 == v and a1 == 0 and a2 == 2 * E
                and a3 == 6 * T and ratio_is_v_plus_k
            ),
        },
    }
