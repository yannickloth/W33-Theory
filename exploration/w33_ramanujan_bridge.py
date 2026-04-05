"""Ramanujan graph property and spectral gap for W(3,3).

Phase CDXCIII — A k-regular graph is Ramanujan if all non-trivial eigenvalues
satisfy |λ| ≤ 2√(k-1). For k=12: 2√11 ≈ 6.633. We have |r|=2, |s|=4,
both ≤ 6.633, so W(3,3) IS Ramanujan.
"""
from __future__ import annotations
from functools import lru_cache
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def build_ramanujan_summary() -> dict:
    v, k, lam, mu, q = 40, 12, 2, 4, 3
    r, s = 2, -4
    f, g = 24, 15
    # Ramanujan bound: 2√(k-1)
    ram_bound = 2 * math.sqrt(k - 1)  # 2√11 ≈ 6.6332...
    is_ramanujan = abs(r) <= ram_bound and abs(s) <= ram_bound
    # Spectral gap: k - max(|r|, |s|) = 12 - 4 = 8
    spectral_gap = k - max(abs(r), abs(s))  # 8
    # Cheeger constant h: spectral_gap/2 ≤ h ≤ √(2k × spectral_gap)
    # h_lower = 8/2 = 4
    h_lower = spectral_gap / 2  # 4.0
    # h_upper = √(2 × 12 × 8) = √192 ≈ 13.86
    # Expansion ratio: min |∂S|/|S| for |S| ≤ v/2
    # Alon-Boppana bound: for large girth, non-trivial eigenvalues ≥ 2√(k-1) - o(1)
    # Since |s| = 4 < 6.633 = 2√11, we have a large spectral gap → good expander
    # Ratio s²/(k-1) = 16/11 ≈ 1.455 (related to Ramanujan quality)
    ram_quality = abs(s) / ram_bound  # 4/6.633 ≈ 0.603
    return {
        "status": "ok",
        "ramanujan": {
            "ram_bound": ram_bound,
            "spectral_gap": spectral_gap,
            "ram_quality": round(ram_quality, 4),
        },
        "ramanujan_theorem": {
            "is_ramanujan": is_ramanujan,
            "spectral_gap_8": spectral_gap == 8,
            "quality_below_1": ram_quality < 1.0,
            "therefore_ramanujan_expander": is_ramanujan and spectral_gap == 8,
        },
    }
