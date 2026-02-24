#!/usr/bin/env python3
"""Golay 24-dim Lie algebra over F3: deterministic invariants and fingerprints.

This repo's Monster/Golay/Heisenberg work repeatedly produces a very concrete
24-dimensional Lie algebra over GF(3).  It arises as the "noncentral" part of a
Weyl/Heisenberg-style closure acting on a 27-dimensional space (3 qutrits).

This module reconstructs that Lie algebra *deterministically* (no randomness,
no external tools) and computes a small set of invariants that can be asserted
in tests and used for identification:

  - grading by F3^2 \\ {(0,0)} with 8 grades, 3 basis elements each (8*3=24)
  - Jacobi identity (Lie)
  - perfectness ([L,L]=L)
  - center dimension (via adjoint faithfulness)
  - Killing form rank over F3
  - derivation algebra dimension over F3 (and inner/outer split)
  - a canonical 6-dim maximal abelian (self-centralizing) subalgebra coming
    from a 1D isotropic line in the grading

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_golay_lie_algebra.py
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


F3 = 3


def _mod_p(A: np.ndarray, p: int) -> np.ndarray:
    return (A.astype(np.int64) % int(p)).astype(np.int64)


def _rank_mod_p(H: np.ndarray, p: int) -> int:
    """Row-rank over GF(p) by Gaussian elimination (dense, small p)."""
    A = _mod_p(H, p).copy()
    m, n = A.shape
    r = 0
    c = 0
    while r < m and c < n:
        pivot = None
        for i in range(r, m):
            if int(A[i, c]) % p != 0:
                pivot = i
                break
        if pivot is None:
            c += 1
            continue
        if pivot != r:
            A[[r, pivot]] = A[[pivot, r]]

        inv = pow(int(A[r, c] % p), -1, p)
        A[r, :] = (A[r, :] * inv) % p

        for i in range(m):
            if i == r:
                continue
            factor = int(A[i, c] % p)
            if factor:
                A[i, :] = (A[i, :] - factor * A[r, :]) % p

        r += 1
        c += 1
    return int(r)


def _nullity_mod_p(H: np.ndarray, p: int) -> int:
    return int(H.shape[1]) - _rank_mod_p(H, p)


# --- Core construction -------------------------------------------------------

# Grade map: F3^6 -> F3^2
_GRADE_COEFFS = (
    (2, 2, 1, 2, 1, 2),
    (0, 2, 2, 0, 2, 1),
)


def grade_msg(m: tuple[int, int, int, int, int, int]) -> tuple[int, int]:
    a = _GRADE_COEFFS[0]
    b = _GRADE_COEFFS[1]
    g0 = sum(int(a[i]) * int(m[i]) for i in range(6)) % 3
    g1 = sum(int(b[i]) * int(m[i]) for i in range(6)) % 3
    return int(g0), int(g1)


def omega(g1: tuple[int, int], g2: tuple[int, int]) -> int:
    """Standard alternating form on F3^2."""
    return int((int(g1[0]) * int(g2[1]) - int(g1[1]) * int(g2[0])) % 3)


def add_msg(
    m1: tuple[int, int, int, int, int, int],
    m2: tuple[int, int, int, int, int, int],
) -> tuple[int, int, int, int, int, int]:
    return tuple((int(m1[i]) + int(m2[i])) % 3 for i in range(6))  # type: ignore[return-value]


def _build_W() -> tuple[tuple[int, ...], ...]:
    """3-dim subspace W ⊂ ker(grade_msg), stored as a tuple of 27 vectors."""
    ker_basis = (
        (0, 0, 0, 0, 1, 1),
        (0, 0, 1, 0, 0, 1),
        (0, 1, 0, 1, 0, 1),
    )
    W: list[tuple[int, ...]] = []
    for a, b, c in product(range(3), repeat=3):
        v = tuple(
            (a * ker_basis[0][i] + b * ker_basis[1][i] + c * ker_basis[2][i]) % 3
            for i in range(6)
        )
        W.append(v)
    W_sorted = tuple(sorted(set(W)))
    assert len(W_sorted) == 27
    return W_sorted


_GRADES_NONZERO: tuple[tuple[int, int], ...] = (
    (0, 1),
    (0, 2),
    (1, 0),
    (1, 1),
    (1, 2),
    (2, 0),
    (2, 1),
    (2, 2),
)


@dataclass(frozen=True)
class GolayLieAlgebra:
    """A concrete 24-dim Lie algebra over GF(3) in a monomial basis."""

    grades: tuple[tuple[int, int], ...]  # length 24; grade per basis element
    reps: tuple[tuple[int, int, int, int, int, int], ...]  # length 24; message rep
    # Bracket table: for (i,j), either (k, c) with c∈{1,2} or (-1,0) for zero.
    bracket_k: np.ndarray  # int64 shape (24,24), -1 indicates zero
    bracket_c: np.ndarray  # int64 shape (24,24), 0 indicates zero


def build_golay_lie_algebra() -> GolayLieAlgebra:
    """Rebuild the 24-dim algebra deterministically from the Heisenberg slicing."""
    messages = [tuple(int(x) for x in m) for m in product(range(3), repeat=6)]
    W = _build_W()
    W_set = set(W)

    # Deterministic coset reps: for each nonzero grade g, pick the three smallest
    # representatives (lex order) of the W-cosets inside the fiber grade^{-1}(g).
    coset_reps: list[tuple[tuple[int, int], tuple[int, int, int, int, int, int]]] = []
    for g in _GRADES_NONZERO:
        fiber = [m for m in messages if grade_msg(m) == g]
        fiber_sorted = sorted(fiber)
        used: set[tuple[int, int, int, int, int, int]] = set()
        reps_g: list[tuple[int, int, int, int, int, int]] = []
        for rep in fiber_sorted:
            if rep in used:
                continue
            reps_g.append(rep)
            for w in W:
                used.add(add_msg(rep, w))  # type: ignore[arg-type]
        reps_g = sorted(reps_g)
        if len(reps_g) != 3:
            raise ValueError(f"expected 3 W-cosets in fiber {g}, got {len(reps_g)}")
        for rep in reps_g:
            coset_reps.append((g, rep))

    if len(coset_reps) != 24:
        raise ValueError(f"expected 24 basis reps, got {len(coset_reps)}")

    grades = tuple(g for g, _ in coset_reps)
    reps = tuple(rep for _, rep in coset_reps)

    # Fast message -> basis-index map (partition of each fiber by W-cosets).
    msg_to_idx: dict[tuple[int, int, int, int, int, int], int] = {}
    for idx, rep in enumerate(reps):
        for w in W:
            msg_to_idx[add_msg(rep, w)] = int(idx)  # type: ignore[arg-type]

    def w_coset_of(m: tuple[int, int, int, int, int, int]) -> int | None:
        if grade_msg(m) == (0, 0):
            return None
        return msg_to_idx.get(m)

    bracket_k = -np.ones((24, 24), dtype=np.int64)
    bracket_c = np.zeros((24, 24), dtype=np.int64)

    for i in range(24):
        gi = grades[i]
        ri = reps[i]
        for j in range(24):
            gj = grades[j]
            rj = reps[j]
            c = omega(gi, gj)
            if c == 0:
                continue
            k = w_coset_of(add_msg(ri, rj))
            if k is None:
                continue
            bracket_k[i, j] = int(k)
            bracket_c[i, j] = int(c)

    # Sanity: nonzero brackets count is determined purely by the grading:
    # 48 ordered noncollinear grade-pairs * 9 internal pairs = 432.
    assert int(np.sum(bracket_c != 0)) == 432

    # Antisymmetry in this basis: [i,j] = -[j,i] => same k but coeff negated.
    for i in range(24):
        for j in range(24):
            if bracket_c[i, j] == 0:
                assert bracket_c[j, i] == 0
                continue
            assert bracket_k[i, j] == bracket_k[j, i]
            assert (bracket_c[i, j] + bracket_c[j, i]) % 3 == 0

    # Ensure the W we used sits in kernel of grade_msg.
    for w in W:
        assert grade_msg(w) == (0, 0)
        assert w in W_set

    return GolayLieAlgebra(
        grades=grades,
        reps=reps,
        bracket_k=bracket_k,
        bracket_c=bracket_c,
    )


def _bracket(
    alg: GolayLieAlgebra, i: int, j: int
) -> tuple[int, int] | None:  # (k, coeff)
    k = int(alg.bracket_k[int(i), int(j)])
    c = int(alg.bracket_c[int(i), int(j)])
    if c == 0:
        return None
    return k, c


def _ad_matrices(alg: GolayLieAlgebra) -> list[np.ndarray]:
    ad: list[np.ndarray] = []
    for i in range(24):
        M = np.zeros((24, 24), dtype=np.int64)
        for j in range(24):
            entry = _bracket(alg, i, j)
            if entry is None:
                continue
            k, c = entry
            M[int(k), int(j)] = int(c)
        ad.append(M % 3)
    return ad


# --- Invariants --------------------------------------------------------------


def _check_jacobi(alg: GolayLieAlgebra) -> None:
    """Jacobi in the monomial basis."""
    # Represent basis vectors by integer indices; since [e_i,e_j] is monomial,
    # we can check Jacobi by coefficient-chasing.
    for i in range(24):
        for j in range(24):
            for k in range(24):
                acc: dict[int, int] = {}
                for a, b, c in ((i, j, k), (j, k, i), (k, i, j)):
                    ab = _bracket(alg, a, b)
                    if ab is None:
                        continue
                    u, cuv = ab
                    uv = _bracket(alg, u, c)
                    if uv is None:
                        continue
                    v, coeff = uv
                    acc[v] = (acc.get(v, 0) + cuv * coeff) % 3
                if any(v != 0 for v in acc.values()):
                    raise AssertionError(f"Jacobi failed at (i,j,k)=({i},{j},{k}): {acc}")


def _center_dim_from_inner_ad_rank(ad: list[np.ndarray]) -> tuple[int, int]:
    """Return (center_dim, inner_der_rank) from the adjoint map x -> ad_x."""
    mats = np.stack([M.reshape(-1) for M in ad], axis=1) % 3  # (576,24)
    inner_rank = _rank_mod_p(mats, 3)
    center_dim = 24 - inner_rank
    return int(center_dim), int(inner_rank)


def _killing_form_rank(ad: list[np.ndarray]) -> int:
    K = np.zeros((24, 24), dtype=np.int64)
    for i in range(24):
        Ai = ad[i]
        for j in range(24):
            K[i, j] = int(np.trace((Ai @ ad[j]) % 3) % 3)
    return _rank_mod_p(K, 3)


def _derivation_dims(alg: GolayLieAlgebra, ad: list[np.ndarray]) -> dict[str, int]:
    """Compute derivation algebra dimension over F3, and inner/outer split."""
    # Unknowns: D_{q,k} in a 24x24 matrix, flattened by row-major (q*24 + k).
    # For each nonzero bracket [i,j]=c*e_k and each coordinate q, enforce:
    #   c*D[:,k] = sum_a D[a,i]*[a,j] + sum_a D[a,j]*[i,a].
    rows: list[np.ndarray] = []
    for i in range(24):
        for j in range(24):
            entry = _bracket(alg, i, j)
            if entry is None:
                continue
            k, c = entry
            for q in range(24):
                coeffs = np.zeros((24 * 24,), dtype=np.int64)
                coeffs[q * 24 + int(k)] = (coeffs[q * 24 + int(k)] + int(c)) % 3

                # sum_a D[a,i] * [a,j]
                for a in range(24):
                    aj = _bracket(alg, a, j)
                    if aj is not None and int(aj[0]) == q:
                        coeffs[a * 24 + int(i)] = (
                            coeffs[a * 24 + int(i)] - int(aj[1])
                        ) % 3

                # sum_a D[a,j] * [i,a]
                for a in range(24):
                    ia = _bracket(alg, i, a)
                    if ia is not None and int(ia[0]) == q:
                        coeffs[a * 24 + int(j)] = (
                            coeffs[a * 24 + int(j)] - int(ia[1])
                        ) % 3

                if np.any(coeffs):
                    rows.append(coeffs)
    A = np.stack(rows, axis=0) % 3  # (n_eq, 576)
    rank = _rank_mod_p(A, 3)
    dim_der = 576 - rank

    inner_basis = np.stack([M.reshape(-1) for M in ad], axis=0) % 3  # (24,576)
    dim_inner = _rank_mod_p(inner_basis, 3)
    dim_outer = dim_der - dim_inner
    return {
        "dim_derivations": int(dim_der),
        "dim_inner": int(dim_inner),
        "dim_outer": int(dim_outer),
        "rank_system": int(rank),
        "n_equations": int(A.shape[0]),
    }


def _centralizer_dim(ad: list[np.ndarray], basis_indices: list[int]) -> int:
    blocks = []
    for idx in basis_indices:
        blocks.append(_mod_p(ad[int(idx)], 3))
    M = np.concatenate(blocks, axis=0)  # (len*basis)*24 x 24
    return _nullity_mod_p(M, 3)


def analyze(*, compute_derivations: bool = True) -> dict[str, Any]:
    alg = build_golay_lie_algebra()
    ad = _ad_matrices(alg)

    # Lie check.
    _check_jacobi(alg)

    # Perfectness: every basis element appears as a bracket output.
    derived = set(int(k) for k in alg.bracket_k[alg.bracket_c != 0].tolist())
    assert len(derived) == 24

    center_dim, inner_rank = _center_dim_from_inner_ad_rank(ad)
    kill_rank = _killing_form_rank(ad)

    # Canonical 6-dim abelian: take two collinear grades (0,1) and (0,2).
    grade_to_indices: dict[tuple[int, int], list[int]] = {}
    for i, g in enumerate(alg.grades):
        grade_to_indices.setdefault(tuple(g), []).append(int(i))
    for g in _GRADES_NONZERO:
        assert len(grade_to_indices.get(g, [])) == 3

    cartan_indices = sorted(grade_to_indices[(0, 1)] + grade_to_indices[(0, 2)])
    assert len(cartan_indices) == 6
    # Self-centralizing => maximal abelian.
    cartan_centralizer_dim = _centralizer_dim(ad, cartan_indices)

    dims = None
    if compute_derivations:
        dims = _derivation_dims(alg, ad)

    return {
        "available": True,
        "field_p": 3,
        "dim": 24,
        "grading": {
            "grade_space": "F3^2",
            "nonzero_grades": [list(g) for g in _GRADES_NONZERO],
            "fiber_dim": 3,
        },
        "bracket": {
            "nonzero_pairs": int(np.sum(alg.bracket_c != 0)),
        },
        "lie": {
            "jacobi_holds": True,
            "perfect": True,
            "center_dim": int(center_dim),
            "killing_form_rank_mod3": int(kill_rank),
        },
        "adjoint": {
            "inner_derivation_rank": int(inner_rank),
        },
        "derivations": dims,
        "cartan_like": {
            "basis_indices": cartan_indices,
            "dim": 6,
            "centralizer_dim": int(cartan_centralizer_dim),
            "self_centralizing": bool(cartan_centralizer_dim == 6),
        },
    }


def main() -> None:
    t0 = time.time()
    rep = analyze(compute_derivations=True)
    if rep.get("available") is not True:
        raise SystemExit(f"Unavailable: {rep}")

    print("=" * 78)
    print("GOLAY 24-DIM LIE ALGEBRA OVER F3 (DETERMINISTIC INVARIANTS)")
    print("=" * 78)

    lie = rep["lie"]
    bracket = rep["bracket"]
    cartan = rep["cartan_like"]
    deriv = rep.get("derivations") or {}

    print()
    print("§1. Basic structure")
    print("-" * 58)
    print(f"  field p = {rep['field_p']}")
    print(f"  dim(L)  = {rep['dim']}")
    print("  grading fibers: 8 grades × 3 = 24")
    print(f"  nonzero bracket pairs: {bracket['nonzero_pairs']} (expected 432)")

    print()
    print("§2. Lie invariants")
    print("-" * 58)
    print(f"  Jacobi: {bool(lie['jacobi_holds'])}")
    print(f"  Perfect: {bool(lie['perfect'])}")
    print(f"  Center dim: {int(lie['center_dim'])}")
    print(f"  Killing form rank mod 3: {int(lie['killing_form_rank_mod3'])}")

    print()
    print("§3. Derivations (GF(3))")
    print("-" * 58)
    if isinstance(deriv, dict) and deriv:
        print(f"  dim Der(L): {int(deriv['dim_derivations'])}")
        print(f"  dim Inn(L): {int(deriv['dim_inner'])}")
        print(f"  dim Out(L): {int(deriv['dim_outer'])}")
        print(f"  linear system: {int(deriv['n_equations'])} eqns, rank={int(deriv['rank_system'])}")
    else:
        print("  (skipped)")

    print()
    print("§4. Canonical 6-dim maximal abelian (grading line)")
    print("-" * 58)
    print(f"  basis indices: {cartan['basis_indices']}")
    print(f"  centralizer dim: {int(cartan['centralizer_dim'])}")
    print(f"  self-centralizing: {bool(cartan['self_centralizing'])}")

    print()
    print("ALL CHECKS PASSED ✓")
    print(f"Elapsed: {time.time() - t0:.2f}s")


if __name__ == "__main__":
    main()

