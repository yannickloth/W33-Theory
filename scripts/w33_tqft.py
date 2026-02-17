#!/usr/bin/env python3
"""
Pillar 60 — Topological Quantum Field Theory (TQFT) from W(3,3)

This pillar makes the "topological sector" of the W(3,3) theory explicit and
computable from first principles:

1) Clique complex / homology invariants (χ, Betti numbers).
2) Bose–Mesner (association-scheme) algebra of SRG(40,12,2,4) as a commutative
   Frobenius algebra → canonical 2D TQFT.
3) Fast state-sum counts over F2 and F3 determined solely by b1.

Usage:
    python scripts/w33_tqft.py
"""

from __future__ import annotations

import sys
import time
from collections import Counter
from pathlib import Path as _Path
from typing import Any, Dict

import numpy as np

sys.path.insert(0, str(_Path(__file__).resolve().parent))

from w33_homology import (
    boundary_matrix,
    build_clique_complex,
    build_w33,
    compute_homology,
)


def _adjacency_matrix(adj: list[list[int]], n: int) -> np.ndarray:
    A = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in adj[i]:
            A[i, j] = 1
    return A


def _rank_mod_p(M: np.ndarray, p: int) -> int:
    """Row-rank over F_p via Gaussian elimination (deterministic)."""
    if M.size == 0:
        return 0

    rows, cols = M.shape
    mat = [[int(M[r, c]) % p for c in range(cols)] for r in range(rows)]

    rank = 0
    for col in range(cols):
        pivot_row = None
        for r in range(rank, rows):
            if mat[r][col] % p != 0:
                pivot_row = r
                break
        if pivot_row is None:
            continue

        mat[rank], mat[pivot_row] = mat[pivot_row], mat[rank]

        pivot = mat[rank][col] % p
        inv = pow(pivot, p - 2, p)  # p is prime here (2 or 3)

        # eliminate below
        for r in range(rank + 1, rows):
            if mat[r][col] % p == 0:
                continue
            factor = (mat[r][col] * inv) % p
            for c in range(col, cols):
                mat[r][c] = (mat[r][c] - factor * mat[rank][c]) % p

        rank += 1
        if rank == rows:
            break

    return rank


def _b1_over_fp(simplices: dict[int, list[tuple[int, ...]]], p: int) -> Dict[str, Any]:
    v = simplices[0]
    e = simplices[1]
    t = simplices[2]

    d1 = boundary_matrix(e, v)
    d2 = boundary_matrix(t, e)

    r1 = _rank_mod_p(d1, p)
    r2 = _rank_mod_p(d2, p)
    b1 = len(e) - r1 - r2
    return {"p": p, "rank_d1": r1, "rank_d2": r2, "b1": b1}


def _primitive_idempotents(
    I: np.ndarray, A: np.ndarray, A2: np.ndarray
) -> Dict[str, Any]:
    n = int(I.shape[0])
    J = np.ones((n, n), dtype=float)
    I_f = I.astype(float)
    A_f = A.astype(float)
    A2_f = A2.astype(float)

    # Primitive idempotents (verified in-repo elsewhere; re-verified here).
    E0 = (1.0 / n) * J
    E1 = (3.0 / 5.0) * I_f + (1.0 / 10.0) * A_f + (-1.0 / 15.0) * A2_f
    E2 = (3.0 / 8.0) * I_f + (-1.0 / 8.0) * A_f + (1.0 / 24.0) * A2_f

    def proj_checks(E: np.ndarray) -> Dict[str, Any]:
        EE = E @ E
        idempotent = bool(np.allclose(EE, E, atol=1e-12, rtol=0))
        tr = float(np.trace(E))
        return {"idempotent": idempotent, "trace": tr, "rank_round": int(round(tr))}

    c0 = proj_checks(E0)
    c1 = proj_checks(E1)
    c2 = proj_checks(E2)

    sum_to_I = bool(np.allclose(E0 + E1 + E2, I_f, atol=1e-12, rtol=0))
    ortho_01 = bool(np.allclose(E0 @ E1, 0.0, atol=1e-12, rtol=0))
    ortho_02 = bool(np.allclose(E0 @ E2, 0.0, atol=1e-12, rtol=0))
    ortho_12 = bool(np.allclose(E1 @ E2, 0.0, atol=1e-12, rtol=0))

    ranks = {"E0": c0["rank_round"], "E1": c1["rank_round"], "E2": c2["rank_round"]}

    return {
        "E0": E0,
        "E1": E1,
        "E2": E2,
        "checks": {"E0": c0, "E1": c1, "E2": c2},
        "sum_to_I": sum_to_I,
        "pairwise_orthogonal": bool(ortho_01 and ortho_02 and ortho_12),
        "ranks": ranks,
    }


def analyze_tqft() -> Dict[str, Any]:
    """Compute the Pillar-60 TQFT data from W(3,3) alone (no external inputs)."""
    n, vertices, adj, _edges_raw = build_w33()
    simplices = build_clique_complex(n, adj)

    hom = compute_homology(simplices)
    simplex_counts = hom["simplex_counts"]
    betti = hom["betti_numbers"]
    chi = hom["euler_characteristic"]

    # Bose–Mesner algebra of SRG(40,12,2,4)
    A = _adjacency_matrix(adj, n)
    I = np.eye(n, dtype=int)
    J = np.ones((n, n), dtype=int)
    A2 = J - I - A  # complement (excluding diagonal)

    AA = A @ A
    AA2 = A @ A2
    A2A2 = A2 @ A2

    srg_closed = {
        "A2_is_complement": bool(np.array_equal(A2, (J - I - A))),
        "A2_entries_0_1": bool(np.all((A2 == 0) | (A2 == 1))),
        "AA_relation": bool(np.array_equal(AA, 12 * I + 2 * A + 4 * A2)),
        "AA2_relation": bool(np.array_equal(AA2, 9 * A + 8 * A2)),
        "A2A2_relation": bool(np.array_equal(A2A2, 27 * I + 18 * A + 18 * A2)),
    }

    evals = np.linalg.eigvalsh(A.astype(float))
    evals_int = [int(round(float(x))) for x in evals]
    spectrum = dict(Counter(evals_int))

    idem = _primitive_idempotents(I, A, A2)
    E0, E1, E2 = idem["E0"], idem["E1"], idem["E2"]
    ranks = idem["ranks"]

    # Frobenius algebra counit ε(x) = Tr(x) in this representation.
    Z_S2 = int(round(float(np.trace(I.astype(float)))))  # ε(1) = Tr(I) = 40

    mu_delta_1 = (E0 / ranks["E0"]) + (E1 / ranks["E1"]) + (E2 / ranks["E2"])
    Z_T2 = float(np.trace(mu_delta_1))  # Σ_i Tr(Ei)/rank(Ei) = 3

    # State-sum counts over F2/F3 depend only on b1.
    b1_f2 = _b1_over_fp(simplices, 2)
    b1_f3 = _b1_over_fp(simplices, 3)

    partition_function = simplex_counts.get(1, 0)  # edges = 240

    return {
        "simplices": simplex_counts,
        "betti_numbers": betti,
        "euler_characteristic": chi,
        "bose_mesner": {
            "srg_closed": srg_closed,
            "structure_constants": {
                # Multiplication in basis {I, A, A2} (Bose–Mesner):
                # A^2 = 12 I + 2 A + 4 A2,  A A2 = 9 A + 8 A2,  A2^2 = 27 I + 18 A + 18 A2
                "A2": {"I": 12, "A": 2, "A2": 4},
                "AA2": {"I": 0, "A": 9, "A2": 8},
                "A2_2": {"I": 27, "A": 18, "A2": 18},
            },
            "adjacency_spectrum": spectrum,
            "idempotents": {
                "sum_to_I": idem["sum_to_I"],
                "pairwise_orthogonal": idem["pairwise_orthogonal"],
                "ranks": ranks,
                "checks": idem["checks"],
            },
        },
        "frobenius_tqft": {
            "Z_S2": Z_S2,
            "Z_T2": Z_T2,
            "dim_algebra": 3,
        },
        "state_sum": {
            "b1_mod_2": b1_f2,
            "b1_mod_3": b1_f3,
            "Z_GF2": pow(2, int(b1_f2["b1"])),
            "Z_GF3": pow(3, int(b1_f3["b1"])),
        },
        "partition_function": partition_function,
    }


def main() -> Dict[str, Any]:
    t0 = time.time()
    print("=" * 70)
    print("PILLAR 60: Topological Quantum Field Theory from W(3,3)")
    print("=" * 70)

    tqft = analyze_tqft()

    # §1 Homology invariants
    print("\n§1. Clique complex / homology invariants")
    print("-" * 50)
    sc = tqft["simplices"]
    betti = tqft["betti_numbers"]
    chi = tqft["euler_characteristic"]
    print(f"  Simplex counts: {sc}")
    print(f"  Betti numbers:  {betti}")
    print(f"  Euler χ = {chi}")
    assert sc.get(0) == 40 and sc.get(1) == 240 and sc.get(2) == 160 and sc.get(3) == 40
    assert betti.get(1) == 81 and betti.get(2) == 0
    assert chi == -80
    print("  ✓ χ=-80, b1=81, b2=0 (topological matter sector)")

    # §2 Bose–Mesner / Frobenius structure
    print("\n§2. Bose–Mesner algebra (SRG(40,12,2,4)) → Frobenius algebra")
    print("-" * 50)
    bm = tqft["bose_mesner"]
    closed = bm["srg_closed"]
    print(f"  SRG closure checks: {closed}")
    assert all(bool(v) for v in closed.values())
    spec = bm["adjacency_spectrum"]
    print(f"  Adjacency spectrum (rounded): {spec}")
    assert spec.get(12) == 1 and spec.get(2) == 24 and spec.get(-4) == 15
    idem = bm["idempotents"]
    print(f"  Primitive idempotent ranks: {idem['ranks']}")
    assert idem["sum_to_I"] and idem["pairwise_orthogonal"]
    assert idem["ranks"] == {"E0": 1, "E1": 24, "E2": 15}
    print("  ✓ Bose–Mesner algebra verified; idempotents decompose C0 into 1+24+15")

    # §3 2D TQFT invariants
    print("\n§3. 2D TQFT invariants (commutative Frobenius algebra)")
    print("-" * 50)
    ft = tqft["frobenius_tqft"]
    print(f"  Z(S^2) = {ft['Z_S2']}")
    print(f"  Z(T^2) = {ft['Z_T2']}")
    assert ft["Z_S2"] == 40
    assert abs(ft["Z_T2"] - 3.0) < 1e-12
    print("  ✓ Z(S^2)=40 (vertices), Z(T^2)=3 (dim Bose–Mesner algebra)")

    # §4 State-sum counts over finite fields
    print("\n§4. State-sum counts (GF(2), GF(3))")
    print("-" * 50)
    ss = tqft["state_sum"]
    print(f"  b1 mod 2: {ss['b1_mod_2']}")
    print(f"  b1 mod 3: {ss['b1_mod_3']}")
    assert ss["b1_mod_2"]["b1"] == 81
    assert ss["b1_mod_3"]["b1"] == 81
    print(f"  Z_GF2 = 2^81 = {ss['Z_GF2']}")
    print(f"  Z_GF3 = 3^81 = {ss['Z_GF3']}")
    print("  ✓ State-sum partition functions determined by b1=81")

    # Summary
    elapsed = time.time() - t0
    print("\n" + "=" * 70)
    print("PILLAR 60 SUMMARY: TQFT from W(3,3)")
    print("=" * 70)
    print("  1. Clique complex: (40,240,160,40), χ=-80")
    print("  2. Homology: b1=81, b2=0 → cup product vanishes")
    print("  3. Bose–Mesner algebra: 3 idempotents (ranks 1,24,15)")
    print("  4. 2D TQFT: Z(S^2)=40, Z(T^2)=3")
    print("  5. State sums: Z_GF2=2^81, Z_GF3=3^81")
    print(f"  Elapsed: {elapsed:.2f}s")
    print("  ALL CHECKS PASSED ✓")

    return tqft


if __name__ == "__main__":
    main()
