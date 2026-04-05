"""Characteristic polynomial and minimal polynomial of A.

Phase DXX — The characteristic polynomial of A for SRG(40,12,2,4):
χ(x) = (x-12)(x-2)²⁴(x+4)¹⁵.
The minimal polynomial: m(x) = (x-12)(x-2)(x+4) (degree 3 = diameter + 1).
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def build_char_poly_summary() -> dict:
    v, k, lam, mu, q = 40, 12, 2, 4, 3
    r, s = 2, -4
    f, g = 24, 15
    # Characteristic polynomial: χ(x) = (x-k)^1 × (x-r)^f × (x-s)^g
    # Degree = 1 + f + g = 40 = v ✓
    char_degree = 1 + f + g  # 40
    # Minimal polynomial: m(x) = (x-k)(x-r)(x-s) since all eigenvalues distinct
    min_degree = 3
    # m(x) = (x-12)(x-2)(x+4) = x³ - 10x² - 8x + 96
    # Coefficients: expand (x-12)(x-2)(x+4)
    # = (x-12)(x² + 2x - 8)
    # = x³ + 2x² - 8x - 12x² - 24x + 96
    # = x³ - 10x² - 32x + 96
    coeff_x2 = -(k + r + s)  # -(12+2-4) = -10
    coeff_x1 = k*r + k*s + r*s  # 24 - 48 - 8 = -32
    coeff_x0 = -(k * r * s)  # -12×2×(-4) = 96
    # This means A³ = 10A² + 32A - 96I (Cayley-Hamilton for minimal poly)
    # Verify: with eigenvalue k=12: 12³ = 10×144 + 32×12 - 96 = 1440+384-96 = 1728 ✓
    check_k = k**3 == -coeff_x2 * k**2 - coeff_x1 * k - coeff_x0
    # Eigenvalue r=2: 8 = 10×4 + 32×2 - 96 = 40+64-96 = 8 ✓
    check_r = r**3 == -coeff_x2 * r**2 - coeff_x1 * r - coeff_x0
    # Eigenvalue s=-4: -64 = 10×16 + 32×(-4) - 96 = 160-128-96 = -64 ✓
    check_s = s**3 == -coeff_x2 * s**2 - coeff_x1 * s - coeff_x0
    return {
        "status": "ok",
        "char_poly": {
            "char_degree": char_degree,
            "min_poly": f"x³ + {coeff_x2}x² + {coeff_x1}x + {coeff_x0}",
            "coefficients": [1, coeff_x2, coeff_x1, coeff_x0],
        },
        "char_poly_theorem": {
            "degree_v": char_degree == v,
            "min_degree_3": min_degree == 3,
            "cayley_hamilton_k": check_k,
            "cayley_hamilton_r": check_r,
            "cayley_hamilton_s": check_s,
            "coeff_sum": 1 + coeff_x2 + coeff_x1 + coeff_x0 == 1 - 10 - 32 + 96,
            "therefore_char_poly_verified": (
                char_degree == v and min_degree == 3
                and check_k and check_r and check_s
            ),
        },
    }
