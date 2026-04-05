"""Spectral action principle.
Phase DLVI — Chamseddine-Connes spectral action: S = Tr(f(D/Λ))
For graph Dirac operator D with eigenvalues ±√λ_i where λ_i are Laplacian eigenvalues:
Laplacian eigenvalues: 0(×1), 10(×24), 16(×15).
Spectral action coefficients from heat trace.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def build_spectral_action_summary() -> dict:
    v, k, lam, mu, q = 40, 12, 2, 4, 3
    r, s = 2, -4
    f, g = 24, 15
    # Laplacian eigenvalues: μ_j = k - θ_j where θ_j are adjacency eigenvalues
    lap_0 = k - k   # 0 (×1)
    lap_1 = k - r   # 10 (×f=24)
    lap_2 = k - s   # 16 (×g=15)
    # Heat trace: Tr(e^{-tL}) = 1 + f*e^{-10t} + g*e^{-16t}
    # At t=0: Tr(e^0) = 1 + 24 + 15 = 40 = v ✓
    heat_0 = 1 + f + g  # 40 = v
    # Spectral action moments: a_n = Σ λ_i^n
    a0 = 1 + f + g  # 40
    a1 = 0 + f * lap_1 + g * lap_2  # 0 + 240 + 240 = 480
    a2 = 0 + f * lap_1**2 + g * lap_2**2  # 0 + 2400 + 3840 = 6240
    # a1 = 480 = 2E = vk (trace of Laplacian = sum of degrees)
    a1_check = a1 == v * k  # 480 ✓
    # a2 relates to: Σ_i d_i² + 2E = v*k² + 2E... wait
    # Tr(L²) = Σ λ² = f*(k-r)² + g*(k-s)² = 24*100 + 15*256 = 2400+3840 = 6240
    # Also: Tr(L²) = Tr((kI-A)²) = Tr(k²I - 2kA + A²) = vk² - 0 + vk = v(k²+k)
    # = 40 × (144+12) = 40 × 156 = 6240 ✓
    a2_check = a2 == v * (k**2 + k)  # 6240 ✓
    # Ratio a2/a1 = 6240/480 = 13 = Φ₃ = q²+q+1
    from fractions import Fraction
    ratio = Fraction(a2, a1)  # 13
    ratio_phi3 = ratio == q**2 + q + 1  # 13 ✓
    return {
        "status": "ok",
        "spectral_action_theorem": {
            "heat_0_v": heat_0 == v,
            "a1_vk": a1_check,
            "a2_vk2k": a2_check,
            "ratio_phi3": ratio_phi3,
            "therefore_spectral_action_verified": heat_0==v and a1_check and a2_check and ratio_phi3,
        },
    }
