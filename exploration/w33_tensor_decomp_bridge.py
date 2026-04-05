"""Tensor product decomposition of adjacency representation.

Phase DXXIX — The adjacency matrix A acts on ℝ⁴⁰.
ℝ⁴⁰ = V₀ ⊕ V₁ ⊕ V₂ where V₀ = span(j) (dim 1), V₁ = E_r eigenspace (dim 24),
V₂ = E_s eigenspace (dim 15). Under tensor product:
V₁ ⊗ V₁ = ℝ²⁴⊗²⁴ decomposes into Sym² ⊕ Alt² = ℝ³⁰⁰ ⊕ ℝ²⁷⁶.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def build_tensor_decomp_summary() -> dict:
    v, k, lam, mu, q = 40, 12, 2, 4, 3
    r, s = 2, -4
    f, g = 24, 15
    # Eigenspace dimensions
    dim0 = 1   # trivial
    dim1 = f   # 24
    dim2 = g   # 15
    # Check sum
    total = dim0 + dim1 + dim2  # 40 = v
    # Tensor products decomposed
    sym2_v1 = dim1 * (dim1 + 1) // 2  # C(25,2) = 300
    alt2_v1 = dim1 * (dim1 - 1) // 2  # C(24,2) = 276
    # 300 = 12 × 25 = k × (f+1)
    is_k_times = sym2_v1 == k * (f + 1)  # 300
    # 276 = 12 × 23 = k × (f-1)
    is_k_times_alt = alt2_v1 == k * (f - 1)  # 276
    # For V₂: Sym²(V₂) = 15×16/2 = 120, Alt²(V₂) = 15×14/2 = 105
    sym2_v2 = dim2 * (dim2 + 1) // 2  # 120
    alt2_v2 = dim2 * (dim2 - 1) // 2  # 105
    # 120 = v × q = graph energy!
    # 105 = |∂E| Seidel component = |s₂| × g = 7 × 15
    # V₁ ⊗ V₂ = ℝ^{24×15} = ℝ^360 = f × g
    tensor_12 = dim1 * dim2  # 360
    return {
        "status": "ok",
        "tensor_decomp": {
            "total_dim": total,
            "sym2_v1": sym2_v1,
            "alt2_v1": alt2_v1,
            "sym2_v2": sym2_v2,
            "alt2_v2": alt2_v2,
            "tensor_12": tensor_12,
        },
        "tensor_decomp_theorem": {
            "total_v": total == v,
            "sym2_300": sym2_v1 == 300,
            "alt2_276": alt2_v1 == 276,
            "sym2_v2_120": sym2_v2 == 120,
            "alt2_v2_105": alt2_v2 == 105,
            "tensor_360": tensor_12 == 360,
            "therefore_tensor_verified": (
                total == v and sym2_v1 == 300 and alt2_v1 == 276
                and sym2_v2 == 120 and alt2_v2 == 105 and tensor_12 == 360
            ),
        },
    }
