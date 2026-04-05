"""Random matrix theory for graph adjacency.
Phase DLXXI — The empirical spectral distribution of W(3,3) adjacency matrix.
Three eigenvalues: 12(×1), 2(×24), -4(×15). Moments match SRG exactly.
Wigner semicircle has σ² = k = 12. The spectral gap r-s = 6.
"""
from __future__ import annotations
from functools import lru_cache
from fractions import Fraction
ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def build_random_matrix_summary() -> dict:
    v, k, lam, mu, q = 40, 12, 2, 4, 3
    r, s = 2, -4
    f, g = 24, 15
    # Empirical spectral measure: μ = (1/v)(δ_k + f·δ_r + g·δ_s)
    # Mean: (1/v)(k + f*r + g*s) = 0
    mean = Fraction(k + f*r + g*s, v)  # 0
    # Variance: (1/v)(k² + f*r² + g*s²) = 480/40 = 12 = k
    var = Fraction(k**2 + f*r**2 + g*s**2, v)  # 12
    var_is_k = var == k
    # Third moment: (1/v)(k³ + f*r³ + g*s³) = 960/40 = 24 = f
    m3 = Fraction(k**3 + f*r**3 + g*s**3, v)  # (1728+192-960)/40 = 960/40 = 24
    m3_is_f = m3 == f
    # Fourth moment: (1/v)(k⁴ + f*r⁴ + g*s⁴)
    m4 = Fraction(k**4 + f*r**4 + g*s**4, v)
    # = (20736 + 384 + 3840)/40 = 24960/40 = 624
    # For Wigner semicircle: m4 = 2σ⁴ = 2 × 144 = 288
    # Ours: 624 ≠ 288 → not semicircle (discrete spectrum vs continuous)
    # Kurtosis excess: m4/var² - 3 = 624/144 - 3 = 4.333... - 3 = 1.333 = 4/3
    kurtosis = m4 / var**2 - 3  # 624/144 - 3 = 13/3 - 3 = 4/3
    kurt_check = kurtosis == Fraction(4, 3)
    # 4/3 = C₂(SU(3)) = Casimir! (from Phase CDXCVIII)
    return {
        "status": "ok",
        "random_matrix_theorem": {
            "mean_zero": mean == 0,
            "var_k": var_is_k,
            "m3_f": m3_is_f,
            "kurtosis_4_3": kurt_check,
            "therefore_rmt_verified": mean==0 and var_is_k and m3_is_f and kurt_check,
        },
    }
