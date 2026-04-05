"""Vertex propagator and Green's function on W(3,3).

Phase CDLXXXVIII — The resolvent G(z) = (zI - A)⁻¹ has poles at eigenvalues
k=12, r=2, s=-4 with residues determined by multiplicities f=24, g=15.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from fractions import Fraction

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def build_vertex_propagator_summary() -> dict:
    v, k, lam, mu, q = 40, 12, 2, 4, 3
    r, s = 2, -4
    f, g = 24, 15
    # Resolvent: G_ij(z) = Σ_α P^α_ij / (z - λ_α)
    # For SRG: idempotents E_0 = J/v, E_1, E_2
    # Residues at poles: Res(z=k) = E_0 = J/v (rank 1)
    # Res(z=r) = E_1 (rank f=24)
    # Res(z=s) = E_2 (rank g=15)
    # Check: ranks sum to v
    rank_sum = 1 + f + g  # 40
    # The diagonal Green's function at vertex:
    # G_vv(z) = 1/(z-k) × (1/v) + 1/(z-r) × (f/v) + 1/(z-s) × (g/v)
    # At z = 0: G_vv(0) = -1/(k×v) - f/(r×v) - g/(s×v)
    # = -1/480 - 24/80 - 15/(-160)
    # = -1/480 - 3/10 + 3/32
    # Using fractions for exact computation:
    g_vv_0 = Fraction(-1, k * v) + Fraction(-f, r * v) + Fraction(-g, s * v)
    # = -1/480 - 24/80 + 15/160
    # = -1/480 - 144/480 + 45/480
    # = (-1 - 144 + 45)/480 = -100/480 = -5/24
    expected = Fraction(-5, 24)  # = -5/f
    is_neg5_over_f = g_vv_0 == Fraction(-5, f)
    return {
        "status": "ok",
        "vertex_propagator": {
            "rank_sum": rank_sum,
            "g_vv_0": str(g_vv_0),
            "expected": str(expected),
        },
        "vertex_propagator_theorem": {
            "rank_sum_v": rank_sum == v,
            "g_vv_at_zero_neg5_over_f": is_neg5_over_f,
            "therefore_propagator_exact": rank_sum == v and is_neg5_over_f,
        },
    }
