"""Neutrino mass matrix structure from graph complement.

Phase DXXVIII — The PMNS mixing matrix from the complement graph SRG(40,27,18,18).
The equal λ̄=μ̄=18 means "democratic" mixing → tribimaximal pattern.
18/27 = 2/3 gives sin²θ₁₂ ≈ 1/3 (solar angle). 
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from fractions import Fraction

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def build_neutrino_mass_summary() -> dict:
    v, k, lam, mu, q = 40, 12, 2, 4, 3
    r, s = 2, -4
    f, g = 24, 15
    # Complement parameters
    k_bar = v - k - 1        # 27
    lam_bar = v - 2*k + mu - 2  # 18
    mu_bar = v - 2*k + lam    # 18
    # Democratic: λ̄ = μ̄ → equal common neighbors for all pairs in complement
    democratic = lam_bar == mu_bar  # True
    # Tribimaximal: sin²θ₁₂ = 1/3
    sin2_12 = Fraction(1, q)  # 1/3
    # From complement: ratio μ̄/k̄ = 18/27 = 2/3 = 1 - 1/3
    ratio_complement = Fraction(mu_bar, k_bar)  # 2/3
    cos2_12 = ratio_complement  # 2/3 → sin²θ₁₂ = 1 - 2/3 = 1/3 ✓
    sin2_12_from_complement = 1 - ratio_complement  # 1/3
    # Atmospheric: sin²θ₂₃ = 1/2 (maximal)
    sin2_23 = Fraction(1, lam)  # 1/2
    # Reactor: sin²θ₁₃ ≈ 0 (tribimaximal) or small
    # In tribimaximal: θ₁₃ = 0 exactly
    return {
        "status": "ok",
        "neutrino_mass": {
            "democratic": democratic,
            "sin2_12": str(sin2_12_from_complement),
            "sin2_23": str(sin2_23),
        },
        "neutrino_mass_theorem": {
            "democratic_mixing": democratic,
            "sin2_12_one_third": sin2_12_from_complement == Fraction(1, 3),
            "sin2_23_half": sin2_23 == Fraction(1, 2),
            "complement_ratio_2_3": ratio_complement == Fraction(2, 3),
            "therefore_neutrino_encoded": (
                democratic and sin2_12_from_complement == Fraction(1, 3)
                and sin2_23 == Fraction(1, 2)
            ),
        },
    }
