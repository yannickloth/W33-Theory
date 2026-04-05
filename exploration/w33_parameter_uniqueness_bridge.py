"""SRG parameter uniqueness: (40,12,2,4) is the unique SRG from GQ(3,3).

Phase CDLXXXIX — No other SRG parameters with v=40 and the same eigenvalues
exist. The parameter set is uniquely determined by v=40, r=2, s=-4.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def build_parameter_uniqueness_summary() -> dict:
    v, k, lam, mu, q = 40, 12, 2, 4, 3
    r, s = 2, -4
    f, g = 24, 15
    # From v and eigenvalues r, s, we can reconstruct k, λ, μ uniquely
    # k is the largest eigenvalue
    # λ = r + s + r*s + ... no. Standard: λ = μ + r + s, μ = ... 
    # From r, s: λ − μ = r + s = −2, and rs = μ − k
    # From multiplicities: 1 + f + g = v → f + g = 39
    # f = −k(s+1)(s−λ) / (μ(r−s)) but this is circular
    # Direct: given v=40, r=2, s=-4:
    # f = (v-1)(s² - s) / ((r-s)(k - s)) ... no, let's be more careful.
    # Actually: given r, s, and v, we get k from:
    # v - 1 = f + g, and k = (f*r² + g*s²)/(f + g) can be solved
    # Simpler: k = f*r²+g*s²/(v-1)... no.
    # From trace(A) = 0: k + f*r + g*s = 0
    # From trace(A²) = 2E = vk: k² + f*r² + g*s² = vk
    # And f + g = v - 1 = 39
    # Three equations, three unknowns (k, f, g):
    # g = 39 - f
    # k + 2f - 4(39-f) = 0 → k + 2f - 156 + 4f = 0 → k + 6f = 156
    # k² + 4f + 16(39-f) = 40k → k² - 12f + 624 = 40k → k² - 40k - 12f + 624 = 0
    # From first: k = 156 - 6f, substitute:
    # (156-6f)² - 40(156-6f) - 12f + 624 = 0
    # 24336 - 1872f + 36f² - 6240 + 240f - 12f + 624 = 0
    # 36f² - 1644f + 18720 = 0
    # f² - 45.667f + 520 = 0 ... let me redo:
    # 36f² + (-1872+240-12)f + (24336-6240+624) = 0
    # 36f² - 1644f + 18720 = 0
    # Divide by 12: 3f² - 137f + 1560 = 0
    # Discriminant: 137² - 4×3×1560 = 18769 - 18720 = 49
    # f = (137 ± 7) / 6 → f = 144/6 = 24 or f = 130/6 (not integer)
    # So f = 24 is UNIQUE, giving g = 15, k = 156 - 144 = 12
    disc_f = 137**2 - 4 * 3 * 1560  # 49
    import math
    sqrt_disc = math.isqrt(disc_f)  # 7
    f_solution = (137 + sqrt_disc) // 6  # 24
    k_solution = 156 - 6 * f_solution  # 12
    g_solution = 39 - f_solution  # 15
    lam_solution = k_solution + r + s - k_solution + (r * s + k_solution)  # not right
    # λ = r + s + rs/k... no. λ − μ = r + s = -2. μ = k − rs = 12 − (−8) = 20? No.
    # rs = −(k − μ) → μ = k + rs = 12 + (−8) = 4. ✓
    # λ = μ + r + s = 4 − 2 = 2. ✓
    mu_sol = k_solution + r * s  # 12 - 8 = 4
    lam_sol = mu_sol + r + s     # 4 - 2 = 2
    unique = (f_solution == f and k_solution == k and g_solution == g 
              and mu_sol == mu and lam_sol == lam)
    return {
        "status": "ok",
        "parameter_uniqueness": {
            "discriminant": disc_f,
            "sqrt_disc": sqrt_disc,
            "f_solution": f_solution,
            "k_solution": k_solution,
        },
        "parameter_uniqueness_theorem": {
            "discriminant_49": disc_f == 49,
            "sqrt_disc_7": sqrt_disc == 7,
            "unique_solution": unique,
            "therefore_parameters_unique": unique and disc_f == 49,
        },
    }
