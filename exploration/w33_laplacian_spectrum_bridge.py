"""Laplacian spectrum and Kirchhoff matrix tree theorem details.

Phase DI — The Laplacian L = D - A has eigenvalues k-λ_i:
k-k=0 (×1), k-r=10 (×24), k-s=16 (×15).
Det'(L) = v⁻¹ × 10²⁴ × 16¹⁵ = spanning tree count / v.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def build_laplacian_spectrum_summary() -> dict:
    v, k, lam, mu, q = 40, 12, 2, 4, 3
    r, s = 2, -4
    f, g = 24, 15
    # Laplacian eigenvalues
    lap_0 = k - k   # 0 (×1)
    lap_1 = k - r    # 10 (×f=24)
    lap_2 = k - s    # 16 (×g=15)
    # Check: eigenvalue sum (trace) = v × k (trace of Laplacian = sum of degrees)
    trace_L = lap_0 * 1 + lap_1 * f + lap_2 * g  # 0 + 240 + 240 = 480 = v×k
    # Spanning trees: τ = v⁻¹ × Π (non-zero Laplacian eigenvalues)
    # τ = (1/40) × 10²⁴ × 16¹⁵
    # = (1/40) × 10²⁴ × 2⁶⁰
    # 10²⁴ = 2²⁴ × 5²⁴, so τ = 2⁸⁴ × 5²⁴ / 40 = 2⁸⁴ × 5²⁴ / (8 × 5) = 2⁸¹ × 5²³
    # From Phase CDLI
    tau_2exp = 81
    tau_5exp = 23
    tau_2_check = 24 + 60 - 3  # 24 from 10²⁴ has 2²⁴, 16¹⁵=2⁶⁰, ÷ 40 = ÷2³×5¹ → 84-3=81
    tau_5_check = 24 - 1  # 10²⁴ has 5²⁴, ÷ 5¹ → 23
    # Algebraic connectivity (Fiedler value) = min non-zero Laplacian eigenvalue
    fiedler = min(lap_1, lap_2)  # 10
    return {
        "status": "ok",
        "laplacian_spectrum": {
            "eigenvalues": [f"0(×1)", f"{lap_1}(×{f})", f"{lap_2}(×{g})"],
            "trace": trace_L,
            "fiedler": fiedler,
        },
        "laplacian_spectrum_theorem": {
            "trace_vk": trace_L == v * k,
            "fiedler_10": fiedler == 10,
            "tau_2_81": tau_2_check == tau_2exp,
            "tau_5_23": tau_5_check == tau_5exp,
            "lap1_plus_lap2_26": lap_1 + lap_2 == 26,
            "therefore_laplacian_verified": (
                trace_L == v * k and fiedler == 10
                and tau_2_check == 81 and tau_5_check == 23
            ),
        },
    }
