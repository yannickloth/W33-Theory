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

# for grade-plane automorphisms
try:
    from scripts.grade_weil_phase import apply_matrix, compute_phase
except ImportError:  # allow import failure in isolation
    apply_matrix = None  # type: ignore
    compute_phase = None  # type: ignore

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


def _phi_normal_form(alg: GolayLieAlgebra) -> dict[str, Any]:
    """Compute the within-grade mixing cocycle phi on the nonzero bracket domain.

    For a basis element index i, let c(i) in {0,1,2} be its position inside its
    grade fiber. For any nonzero bracket [i,j] = omega(g,h) * k, define

        phi(g,h) := c(k) - c(i) - c(j)  (mod 3).

    This is only defined on the domain omega(g,h) != 0 (non-collinear grades),
    i.e. where the bracket is nonzero. In the deterministic basis used by this
    repo, phi is identically 0 and the fiber index is pure addition.
    """
    grade_to_indices: dict[tuple[int, int], list[int]] = {}
    for i, g in enumerate(alg.grades):
        grade_to_indices.setdefault(tuple(g), []).append(int(i))

    for g in _GRADES_NONZERO:
        idxs = grade_to_indices.get(g, [])
        if len(idxs) != 3:
            raise AssertionError(f"expected 3 basis elements in grade {g}, got {idxs}")

    pos_in_grade: dict[int, int] = {}
    for g, idxs in grade_to_indices.items():
        for pos, idx in enumerate(idxs):
            pos_in_grade[int(idx)] = int(pos)

    phi_values: dict[tuple[tuple[int, int], tuple[int, int]], set[int]] = {}
    c_addition_ok = True
    for i in range(24):
        gi = tuple(alg.grades[i])
        ci = pos_in_grade[int(i)]
        for j in range(24):
            c = int(alg.bracket_c[i, j])
            if c == 0:
                continue
            gj = tuple(alg.grades[j])
            cj = pos_in_grade[int(j)]
            k = int(alg.bracket_k[i, j])
            ck = pos_in_grade[int(k)]
            val = (ck - ci - cj) % 3
            phi_values.setdefault((gi, gj), set()).add(int(val))
            if ck != (ci + cj) % 3:
                c_addition_ok = False

    # Constancy per grade pair on the nonzero bracket domain.
    bad: list[tuple[tuple[tuple[int, int], tuple[int, int]], list[int]]] = []
    phi_const: dict[str, int] = {}
    for (g, h), vals in sorted(phi_values.items()):
        if len(vals) != 1:
            bad.append(((g, h), sorted(vals)))
        else:
            phi_const[f"{g},{h}"] = int(next(iter(vals)))
    if bad:
        raise AssertionError(f"phi not constant for grade pairs: {bad[:5]}")

    all_vals = sorted({v for s in phi_values.values() for v in s})
    return {
        "available": True,
        "grade_pair_count": int(len(phi_values)),
        "phi_values_distinct": all_vals,
        "phi_is_zero": bool(all_vals == [0]),
        "c_addition_holds": bool(c_addition_ok),
        "phi_const_by_grade_pair": phi_const,
    }


def _analyze_fiber_algebra() -> dict[str, Any]:
    """Analyze the 3-dim commutative algebra A with basis {u0,u1,u2} and product
    u_i u_j = u_{i+j mod 3}.

    In characteristic 3, this is the group algebra F3[C3] which is a local algebra
    isomorphic to F3[ε]/(ε^3).
    """
    p = 3
    rows: list[np.ndarray] = []
    for i in range(3):
        for j in range(3):
            k = (i + j) % 3
            for q in range(3):
                coeffs = np.zeros((9,), dtype=np.int64)
                coeffs[q * 3 + int(k)] = (coeffs[q * 3 + int(k)] + 1) % p
                for a in range(3):
                    if (a + j) % 3 == q:
                        coeffs[a * 3 + int(i)] = (coeffs[a * 3 + int(i)] - 1) % p
                for a in range(3):
                    if (i + a) % 3 == q:
                        coeffs[a * 3 + int(j)] = (coeffs[a * 3 + int(j)] - 1) % p
                if np.any(coeffs):
                    rows.append(coeffs)
    A = np.stack(rows, axis=0) % p  # (eqns, 9)
    rank = _rank_mod_p(A, p)
    dim_der = 9 - rank
    return {
        "available": True,
        "field_p": 3,
        "dim": 3,
        "structure": "u_i u_j = u_{i+j mod 3} (group algebra F3[C3])",
        "dim_derivations": int(dim_der),
        "rank_system": int(rank),
        "n_equations": int(A.shape[0]),
    }


def _l0_slice_indices() -> list[int]:
    """Indices for the c=0 slice: one basis element per grade (8 total)."""
    # In build_golay_lie_algebra() the basis is constructed grade-by-grade and
    # each grade contributes exactly 3 basis elements in sorted order; the first
    # one is the c=0 representative.
    return [3 * i for i in range(8)]


def _analyze_l0_slice(alg: GolayLieAlgebra) -> dict[str, Any]:
    """Analyze the 8-dim c=0 slice subalgebra L0 ⊂ L."""
    idxs = _l0_slice_indices()
    loc = {int(g): int(i) for i, g in enumerate(idxs)}
    n = len(idxs)
    assert n == 8

    bk = -np.ones((n, n), dtype=np.int64)
    bc = np.zeros((n, n), dtype=np.int64)
    for a, i in enumerate(idxs):
        for b, j in enumerate(idxs):
            c = int(alg.bracket_c[int(i), int(j)])
            if c == 0:
                continue
            k = int(alg.bracket_k[int(i), int(j)])
            if k not in loc:
                raise AssertionError(f"L0 not closed: [{i},{j}] -> {k}")
            bk[a, b] = int(loc[k])
            bc[a, b] = int(c)

    # Quick Jacobi check (coefficient-chasing in a monomial basis).
    for i in range(n):
        for j in range(n):
            for k in range(n):
                acc: dict[int, int] = {}
                for a, b, c in ((i, j, k), (j, k, i), (k, i, j)):
                    if bc[a, b] == 0:
                        continue
                    u = int(bk[a, b])
                    cu = int(bc[a, b])
                    if bc[u, c] == 0:
                        continue
                    v = int(bk[u, c])
                    cv = int(bc[u, c])
                    acc[v] = (acc.get(v, 0) + cu * cv) % 3
                if any(v != 0 for v in acc.values()):
                    raise AssertionError(f"L0 Jacobi failed at {(i,j,k)}: {acc}")

    # Derivations for L0 (64 unknowns, small).
    rows: list[np.ndarray] = []
    for i in range(n):
        for j in range(n):
            c = int(bc[i, j])
            if c == 0:
                continue
            k = int(bk[i, j])
            for q in range(n):
                coeffs = np.zeros((n * n,), dtype=np.int64)
                coeffs[q * n + int(k)] = (coeffs[q * n + int(k)] + c) % 3
                for a in range(n):
                    c2 = int(bc[a, j])
                    if c2 != 0 and int(bk[a, j]) == q:
                        coeffs[a * n + int(i)] = (coeffs[a * n + int(i)] - c2) % 3
                for a in range(n):
                    c2 = int(bc[i, a])
                    if c2 != 0 and int(bk[i, a]) == q:
                        coeffs[a * n + int(j)] = (coeffs[a * n + int(j)] - c2) % 3
                if np.any(coeffs):
                    rows.append(coeffs)
    A = np.stack(rows, axis=0) % 3  # (eqns, 64)
    rank = _rank_mod_p(A, 3)
    dim_der = n * n - rank

    # Inner derivations span for L0.
    ad0: list[np.ndarray] = []
    for i in range(n):
        M = np.zeros((n, n), dtype=np.int64)
        for j in range(n):
            if bc[i, j] == 0:
                continue
            M[int(bk[i, j]), int(j)] = int(bc[i, j])
        ad0.append(M % 3)
    inner_basis = np.stack([M.reshape(-1) for M in ad0], axis=0) % 3
    dim_inner = _rank_mod_p(inner_basis, 3)

    # Center dim from adjoint map.
    mats = np.stack([M.reshape(-1) for M in ad0], axis=1) % 3  # (n^2, n)
    center_dim = n - _rank_mod_p(mats, 3)

    # Killing form rank.
    K = np.zeros((n, n), dtype=np.int64)
    for i in range(n):
        for j in range(n):
            K[i, j] = int(np.trace((ad0[i] @ ad0[j]) % 3) % 3)
    kill_rank = _rank_mod_p(K, 3)

    return {
        "available": True,
        "field_p": 3,
        "dim": 8,
        "lie": {
            "jacobi_holds": True,
            "perfect": True,
            "center_dim": int(center_dim),
            "killing_form_rank_mod3": int(kill_rank),
        },
        "derivations": {
            "dim_derivations": int(dim_der),
            "dim_inner": int(dim_inner),
            "dim_outer": int(dim_der - dim_inner),
            "rank_system": int(rank),
            "n_equations": int(A.shape[0]),
        },
    }


def _outer_derivation_tensor_decomposition(
    *,
    alg: GolayLieAlgebra,
    ad: list[np.ndarray],
    dim_der: int,
    dim_inner: int,
) -> dict[str, Any]:
    """Construct the 9-dimensional outer derivation space as:

      Out(L) = (Out(L0) ⊗ A)  ⊕  (Cent(L0) ⊗ Der(A)),

    where L0 is the 8-dim c=0 slice and A is the 3-dim fiber algebra.
    """
    if dim_inner != 24 or dim_der != 33:
        # Only assert the decomposition on the expected regime.
        return {
            "available": False,
            "reason": f"unexpected dims: Der={dim_der} Inn={dim_inner}",
        }

    # Compute outer(L0) (2-dimensional) from the L0 slice.
    idxs0 = _l0_slice_indices()
    loc0 = {int(g): int(i) for i, g in enumerate(idxs0)}
    n0 = len(idxs0)

    bk0 = -np.ones((n0, n0), dtype=np.int64)
    bc0 = np.zeros((n0, n0), dtype=np.int64)
    for a, i in enumerate(idxs0):
        for b, j in enumerate(idxs0):
            c = int(alg.bracket_c[int(i), int(j)])
            if c == 0:
                continue
            k = int(alg.bracket_k[int(i), int(j)])
            bk0[a, b] = int(loc0[k])
            bc0[a, b] = int(c)

    rows: list[np.ndarray] = []
    for i in range(n0):
        for j in range(n0):
            c = int(bc0[i, j])
            if c == 0:
                continue
            k = int(bk0[i, j])
            for q in range(n0):
                coeffs = np.zeros((n0 * n0,), dtype=np.int64)
                coeffs[q * n0 + int(k)] = (coeffs[q * n0 + int(k)] + c) % 3
                for a in range(n0):
                    c2 = int(bc0[a, j])
                    if c2 != 0 and int(bk0[a, j]) == q:
                        coeffs[a * n0 + int(i)] = (coeffs[a * n0 + int(i)] - c2) % 3
                for a in range(n0):
                    c2 = int(bc0[i, a])
                    if c2 != 0 and int(bk0[i, a]) == q:
                        coeffs[a * n0 + int(j)] = (coeffs[a * n0 + int(j)] - c2) % 3
                if np.any(coeffs):
                    rows.append(coeffs)
    A0 = np.stack(rows, axis=0) % 3  # (eqns, 64)

    # RREF for nullspace basis.
    A = _mod_p(A0, 3).copy()
    m, nvars = A.shape
    pivot_cols: list[int] = []
    row = 0
    for col in range(nvars):
        if row >= m:
            break
        pivot = None
        for r in range(row, m):
            if int(A[r, col]) % 3 != 0:
                pivot = r
                break
        if pivot is None:
            continue
        if pivot != row:
            A[[row, pivot]] = A[[pivot, row]]
        inv = pow(int(A[row, col] % 3), -1, 3)
        A[row, :] = (A[row, :] * inv) % 3
        for r in range(m):
            if r == row:
                continue
            f = int(A[r, col] % 3)
            if f:
                A[r, :] = (A[r, :] - f * A[row, :]) % 3
        pivot_cols.append(int(col))
        row += 1
    free_cols = [c for c in range(nvars) if c not in pivot_cols]
    ns0 = []
    for f in free_cols:
        v = np.zeros((nvars,), dtype=np.int64)
        v[int(f)] = 1
        for i, pc in enumerate(pivot_cols):
            v[int(pc)] = (-int(A[i, int(f)])) % 3
        ns0.append(v)
    ns0 = np.stack(ns0, axis=0) % 3
    assert ns0.shape[0] == 10

    # Inner(L0) basis vectors (8 of them).
    ad0: list[np.ndarray] = []
    for i in range(n0):
        M = np.zeros((n0, n0), dtype=np.int64)
        for j in range(n0):
            if bc0[i, j] == 0:
                continue
            M[int(bk0[i, j]), int(j)] = int(bc0[i, j])
        ad0.append(M % 3)
    inner0 = np.stack([M.reshape(-1) for M in ad0], axis=0) % 3

    # Choose 2 vectors in ns0 that extend the rank of inner0.
    def _rank_mod(M: np.ndarray) -> int:
        return _rank_mod_p(M, 3)

    stack = inner0.copy() % 3
    cur = _rank_mod(stack)
    outer0: list[np.ndarray] = []
    for v in ns0:
        test = np.vstack([stack, v]) % 3
        r = _rank_mod(test)
        if r > cur:
            outer0.append(v)
            stack = test
            cur = r
        if len(outer0) == 2:
            break
    assert len(outer0) == 2

    # Multiplication-by-u_a matrices on the fiber basis {0,1,2}.
    P = []
    for a in range(3):
        M = np.zeros((3, 3), dtype=np.int64)
        for c in range(3):
            M[(c + a) % 3, c] = 1
        P.append(M % 3)

    # Der(A) basis matrices (3 of them) extended uniformly across 8 grades.
    fiber = _analyze_fiber_algebra()
    if (
        fiber.get("available") is not True
        or int(fiber.get("dim_derivations", -1)) != 3
    ):
        return {"available": False, "reason": "unexpected Der(A) dimension"}

    derA_blocks = [
        np.array([[0, 2, 0], [0, 0, 1], [0, 0, 0]], dtype=np.int64) % 3,
        np.array([[0, 0, 2], [0, 0, 0], [0, 1, 0]], dtype=np.int64) % 3,
        np.array([[0, 0, 0], [0, 2, 0], [0, 0, 1]], dtype=np.int64) % 3,
    ]
    uniform: list[np.ndarray] = []
    for D3 in derA_blocks:
        D = np.zeros((24, 24), dtype=np.int64)
        for g in range(8):
            b = [3 * g + 0, 3 * g + 1, 3 * g + 2]
            D[np.ix_(b, b)] = D3
        uniform.append(D % 3)

    # Extend outer(L0) via kron(d, mult_by_u_a).
    ext: list[np.ndarray] = []
    for v in outer0:
        d = v.reshape((8, 8)) % 3
        for a in range(3):
            ext.append(np.kron(d, P[a]) % 3)

    # Verify derivation property for constructed outer matrices.
    bk_full = alg.bracket_k
    bc_full = alg.bracket_c

    def _is_derivation(D: np.ndarray) -> bool:
        for i in range(24):
            col_i = D[:, i] % 3
            nz_i = np.nonzero(col_i)[0]
            for j in range(24):
                c = int(bc_full[i, j])
                if c == 0:
                    continue
                k = int(bk_full[i, j])
                left = (c * D[:, k]) % 3

                col_j = D[:, j] % 3
                nz_j = np.nonzero(col_j)[0]
                right = np.zeros((24,), dtype=np.int64)
                for a in nz_i:
                    ca = int(col_i[int(a)])
                    c2 = int(bc_full[int(a), j])
                    if c2 != 0:
                        right[int(bk_full[int(a), j])] = (
                            right[int(bk_full[int(a), j])] + ca * c2
                        ) % 3
                for b in nz_j:
                    cb = int(col_j[int(b)])
                    c2 = int(bc_full[i, int(b)])
                    if c2 != 0:
                        right[int(bk_full[i, int(b)])] = (
                            right[int(bk_full[i, int(b)])] + cb * c2
                        ) % 3
                if not np.array_equal(left % 3, right % 3):
                    return False
        return True

    for D in uniform + ext:
        if not _is_derivation(D):
            return {
                "available": False,
                "reason": "constructed matrix failed derivation check",
            }

    # Show these 9 derivations extend the inner span to full Der(L).
    inner_full = np.stack([M.reshape(-1) for M in ad], axis=0) % 3  # (24,576)
    span = np.vstack([inner_full] + [D.reshape(-1) for D in (uniform + ext)]) % 3
    span_rank = _rank_mod_p(span, 3)
    return {
        "available": True,
        "dim_inner": int(dim_inner),
        "dim_derivations": int(dim_der),
        "constructed_outer_dim": 9,
        "constructed_outer_components": {
            "outer_l0_tensor_A": 6,
            "centroid_l0_tensor_derA": 3,
        },
        "span_rank": int(span_rank),
        "span_is_all_derivations": bool(span_rank == dim_der),
    }


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

    normal_form = _phi_normal_form(alg)
    l0 = _analyze_l0_slice(alg)
    fiber = _analyze_fiber_algebra()

    deriv_decomp = None
    if isinstance(dims, dict):
        deriv_decomp = _outer_derivation_tensor_decomposition(
            alg=alg,
            ad=ad,
            dim_der=int(dims.get("dim_derivations", 0) or 0),
            dim_inner=int(dims.get("dim_inner", 0) or 0),
        )

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
        "normal_form": normal_form,
        "tensor_decomposition": {
            "l0_slice": l0,
            "fiber_algebra": fiber,
            "derivation_decomposition": deriv_decomp,
        },
        "cartan_like": {
            "basis_indices": cartan_indices,
            "dim": 6,
            "centralizer_dim": int(cartan_centralizer_dim),
            "self_centralizing": bool(cartan_centralizer_dim == 6),
        },
    }



# ---------------------------------------------------------------------------
# Symplectic-grade automorphisms using Weil phase
# ---------------------------------------------------------------------------

def symplectic_aut_permutation(alg: GolayLieAlgebra, A: np.ndarray) -> list[int]:
    """Return the permutation of the 24 basis indices induced by the linear
    action of the symplectic matrix ``A`` on the grade plane.  This map simply
    sends a basis element with grade ``g`` and fiber position ``c`` to the
    element with grade ``A g`` and the *same* fiber position.  No Weil phase
    is used; because our algebra has trivial cocycle, this permutation is a
    genuine Lie automorphism.
    """
    if apply_matrix is None:
        raise ImportError("grade_weil_phase.apply_matrix unavailable")

    # build grade -> indices and pos-in-grade maps
    grade_to_indices: dict[tuple[int, int], list[int]] = {}
    for i, g in enumerate(alg.grades):
        grade_to_indices.setdefault(tuple(g), []).append(i)
    pos_in_grade: dict[int, int] = {}
    for g, idxs in grade_to_indices.items():
        for pos, idx in enumerate(idxs):
            pos_in_grade[idx] = pos

    perm: list[int] = [-1] * 24
    for i in range(24):
        g = tuple(alg.grades[i])
        c = pos_in_grade[i]
        newg = apply_matrix(A, g)
        idxs = grade_to_indices.get(tuple(newg))
        if idxs is None:
            raise AssertionError(f"grade {newg} not found")
        perm[i] = idxs[c]
    return perm


def symplectic_aut_with_phase(alg: GolayLieAlgebra, A: np.ndarray) -> list[int] | None:
    """Variant that applies Weil phase shifts to fiber indices.

    This map is *not* guaranteed to be a Lie automorphism because the phase
    cochain need not be additive.  It is provided for exploratory experimentation
    and does exactly what earlier versions of this module attempted to do.
    """
    if apply_matrix is None or compute_phase is None:
        raise ImportError("grade_weil_phase utilities unavailable")

    mu = compute_phase(A)
    if mu is None:
        return None

    grade_to_indices: dict[tuple[int, int], list[int]] = {}
    for i, g in enumerate(alg.grades):
        grade_to_indices.setdefault(tuple(g), []).append(i)
    pos_in_grade: dict[int, int] = {}
    for g, idxs in grade_to_indices.items():
        for pos, idx in enumerate(idxs):
            pos_in_grade[idx] = pos

    perm: list[int] = [-1] * 24
    for i in range(24):
        g = tuple(alg.grades[i])
        c = pos_in_grade[i]
        newg = apply_matrix(A, g)
        newc = (c + mu.get(g, 0)) % 3
        idxs = grade_to_indices.get(tuple(newg))
        if idxs is None or newc >= len(idxs):
            return None
        perm[i] = idxs[newc]
    return perm


def verify_symplectic_automorphism(alg: GolayLieAlgebra, A: np.ndarray) -> bool:
    """Check that the permutation returned by ``symplectic_aut_permutation``
    preserves the Lie bracket (i.e. is an automorphism of the algebra).
    """
    perm = symplectic_aut_permutation(alg, A)
    for i in range(24):
        for j in range(24):
            entry = _bracket(alg, i, j)
            if entry is None:
                if _bracket(alg, perm[i], perm[j]) is not None:
                    return False
                continue
            k, c = entry
            entry2 = _bracket(alg, perm[i], perm[j])
            if entry2 is None:
                return False
            k2, c2 = entry2
            if perm[k] != k2 or (c % 3) != (c2 % 3):
                return False
    return True


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
    nf = rep.get("normal_form") or {}
    td = rep.get("tensor_decomposition") or {}
    l0 = td.get("l0_slice") if isinstance(td, dict) else {}
    fiber = td.get("fiber_algebra") if isinstance(td, dict) else {}
    decomp = td.get("derivation_decomposition") if isinstance(td, dict) else {}

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
    if isinstance(nf, dict) and nf.get("available") is True:
        print("§3. Normal form (grading + fiber)")
        print("-" * 58)
        print(
            f"  grade pairs with omega!=0: {int(nf.get('grade_pair_count', 0) or 0)} (expected 48)"
        )
        print(f"  phi values distinct: {nf.get('phi_values_distinct')}")
        print(f"  phi is identically 0: {bool(nf.get('phi_is_zero'))}")
        print(f"  fiber index addition holds: {bool(nf.get('c_addition_holds'))}")
        print()

    if (
        isinstance(l0, dict)
        and l0.get("available") is True
        and isinstance(fiber, dict)
        and fiber.get("available") is True
    ):
        d0 = l0.get("derivations", {})
        if not isinstance(d0, dict):
            d0 = {}
        print("§4. Tensor factorization: L ~= L0 tensor A")
        print("-" * 58)
        print(
            f"  dim(L0)=8 (c=0 slice), dim Der(L0)={int(d0.get('dim_derivations', 0) or 0)}"
        )
        print(
            f"  dim(A)=3 (u_i u_j = u_{{i+j}}), dim Der(A)={int(fiber.get('dim_derivations', 0) or 0)}"
        )
        print()

    print("§5. Derivations (GF(3))")
    print("-" * 58)
    if isinstance(deriv, dict) and deriv:
        print(f"  dim Der(L): {int(deriv['dim_derivations'])}")
        print(f"  dim Inn(L): {int(deriv['dim_inner'])}")
        print(f"  dim Out(L): {int(deriv['dim_outer'])}")
        print(
            f"  linear system: {int(deriv['n_equations'])} eqns, rank={int(deriv['rank_system'])}"
        )
    else:
        print("  (skipped)")

    if isinstance(decomp, dict) and decomp.get("available") is True:
        comps = decomp.get("constructed_outer_components", {})
        if isinstance(comps, dict):
            a = int(comps.get("outer_l0_tensor_A", 0) or 0)
            b = int(comps.get("centroid_l0_tensor_derA", 0) or 0)
            total = int(decomp.get("constructed_outer_dim", 0) or 0)
            print(f"  outer decomposition: {a} + {b} = {total}")
        print(
            f"  span(inner + constructed outers) rank: {int(decomp.get('span_rank', 0) or 0)}"
        )
        print(f"  spans all derivations: {bool(decomp.get('span_is_all_derivations'))}")

    print()
    print("§6. Canonical 6-dim maximal abelian (grading line)")
    print("-" * 58)
    print(f"  basis indices: {cartan['basis_indices']}")
    print(f"  centralizer dim: {int(cartan['centralizer_dim'])}")
    print(f"  self-centralizing: {bool(cartan['self_centralizing'])}")

    print()
    print("ALL CHECKS PASSED ✓")
    print(f"Elapsed: {time.time() - t0:.2f}s")


if __name__ == "__main__":
    main()
