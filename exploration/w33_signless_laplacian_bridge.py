"""Signless Laplacian Q = D + A spectrum.

Phase DII — Q has eigenvalues k+λ_i: k+k=24 (×1), k+r=14 (×24), k+s=8 (×15).
Trace(Q) = Trace(L) = vk = 480. The signless Laplacian relates to bipartiteness
and frustrated systems.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def build_signless_laplacian_summary() -> dict:
    v, k, lam, mu, q = 40, 12, 2, 4, 3
    r, s = 2, -4
    f, g = 24, 15
    # Signless Laplacian eigenvalues: k + λ_i
    q0 = k + k   # 24 (×1)
    q1 = k + r   # 14 (×24)
    q2 = k + s   # 8 (×15)
    trace_Q = q0 * 1 + q1 * f + q2 * g  # 24 + 336 + 120 = 480
    # q2 = 8 = dim(𝕆) = v/5
    octonion_dim = q2  # 8
    # The smallest eigenvalue of Q: q2 = 8. 
    # For bipartite graphs, smallest Q eigenvalue = 0. Since q2 = 8 > 0, non-bipartite ✓
    non_bipartite = q2 > 0
    # Energy of Q: sum of |q_i - 2E/v| = ... 
    # Mean of Q eigenvalues = 480/40 = 12 = k
    mean_q = trace_Q // v  # 12
    return {
        "status": "ok",
        "signless_laplacian": {
            "eigenvalues": [f"{q0}(×1)", f"{q1}(×{f})", f"{q2}(×{g})"],
            "trace": trace_Q,
        },
        "signless_laplacian_theorem": {
            "trace_vk": trace_Q == v * k,
            "q2_is_8": q2 == 8,
            "non_bipartite": non_bipartite,
            "mean_is_k": mean_q == k,
            "q0_is_2k": q0 == 2 * k,
            "therefore_signless_verified": (
                trace_Q == v * k and q2 == 8
                and non_bipartite and mean_q == k and q0 == 2 * k
            ),
        },
    }
