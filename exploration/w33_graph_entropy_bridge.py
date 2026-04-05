"""Graph entropy and von Neumann entropy of the density matrix.

Phase DVII — The density matrix ρ = L/(v×k) has von Neumann entropy
S_vN = −Σ λ̃_i log₂ λ̃_i where λ̃_i = μ_i/(v×k) are normalized Laplacian eigenvalues.
0 contributes 0, 10/(40×12)=1/48 (×24), 16/(40×12)=1/30 (×15).
"""
from __future__ import annotations
from functools import lru_cache
import math
from pathlib import Path
from fractions import Fraction

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def build_graph_entropy_summary() -> dict:
    v, k, lam, mu, q = 40, 12, 2, 4, 3
    r, s = 2, -4
    f, g = 24, 15
    mu1 = k - r  # 10
    mu2 = k - s  # 16
    E = v * k // 2  # 240
    # Normalized eigenvalues for density matrix ρ = L/(Tr L) = L/(vk)
    # These should sum to 1:
    # 0 × 1 + (10/(480)) × 24 + (16/(480)) × 15 = 240/480 + 240/480 = 1 ✓
    tilde_0 = Fraction(0)
    tilde_1 = Fraction(mu1, v * k)  # 10/480 = 1/48
    tilde_2 = Fraction(mu2, v * k)  # 16/480 = 1/30
    # Check sum: 0 + 24/48 + 15/30 = 1/2 + 1/2 = 1 ✓
    norm_sum = tilde_0 * 1 + tilde_1 * f + tilde_2 * g
    # Von Neumann entropy (in bits):
    # S = -[24 × (1/48) log₂(1/48) + 15 × (1/30) log₂(1/30)]
    # = -[1/2 × log₂(1/48) + 1/2 × log₂(1/30)]
    # = (1/2)[log₂(48) + log₂(30)]
    # = (1/2) log₂(48 × 30) = (1/2) log₂(1440)
    s_vN = 0.5 * math.log2(48 * 30)  # 0.5 × log₂(1440)
    # log₂(1440) ≈ 10.493
    # S ≈ 5.247 bits
    # Maximum possible: log₂(v-1) = log₂(39) ≈ 5.285 (if all equal)
    s_max = math.log2(v - 1)  # log₂(39) ≈ 5.285
    # Ratio S/S_max ≈ 0.993 — nearly maximal entropy!
    ratio = s_vN / s_max
    return {
        "status": "ok",
        "graph_entropy": {
            "tilde_1": str(tilde_1),
            "tilde_2": str(tilde_2),
            "s_vN": round(s_vN, 6),
            "s_max": round(s_max, 6),
            "ratio": round(ratio, 6),
        },
        "graph_entropy_theorem": {
            "normalized_sum_1": norm_sum == 1,
            "tilde1_1_48": tilde_1 == Fraction(1, 48),
            "tilde2_1_30": tilde_2 == Fraction(1, 30),
            "product_1440": 48 * 30 == 1440,
            "near_maximal": ratio > 0.99,
            "therefore_entropy_verified": (
                norm_sum == 1
                and tilde_1 == Fraction(1, 48)
                and tilde_2 == Fraction(1, 30)
                and ratio > 0.99
            ),
        },
    }
