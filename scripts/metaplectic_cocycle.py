r"""Finite-field metaplectic cocycle solver for Sp(2,3).

This module provides a complementary, purely algebraic way to compute the
``mu_A`` phase cochain appearing in :mod:`grade_weil_phase`.  Instead of
using the closed-form gauge choice, we set up and solve the linear system

    phi(A g, A h) - phi(g,h) = mu(g+h) - mu(g) - mu(h)    (all mod 3)

for the 1-cochain \mu: F3^2 -> F3.  The space of solutions is an affine
translate of the space of linear functionals, reflecting the usual
ambiguity by additive characters.  The canonical gauge used in
:mod:`grade_weil_phase` is recovered by subtracting the unique linear
functional that vanishes on the eight nonzero grade vectors.

The solver here is mainly intended to verify that our closed formula is
correct, and to serve as a reference for extending the construction to other
prime fields.
"""

from __future__ import annotations

import itertools
from typing import Dict, Tuple

import numpy as np

# re-export utilities from grade_weil_phase for convenience
from scripts.grade_weil_phase import F3, U2, apply_matrix, phi, GRADES_NONZERO


def _add(u: U2, v: U2) -> U2:
    return ((u[0] + v[0]) % 3, (u[1] + v[1]) % 3)


def _add_p(u: tuple[int, int], v: tuple[int, int], p: int) -> tuple[int, int]:
    return ((u[0] + v[0]) % p, (u[1] + v[1]) % p)


def _row_reduce_mod_p(mat: np.ndarray, p: int) -> tuple[int, np.ndarray, list[int]]:
    """Return (rank, rref, pivot_cols) over F_p."""
    A = (np.asarray(mat, dtype=np.int64) % int(p)).copy()
    m, n = A.shape
    row = 0
    pivots: list[int] = []

    for col in range(n):
        pivot = None
        for r in range(row, m):
            if int(A[r, col] % p) != 0:
                pivot = r
                break
        if pivot is None:
            continue
        if pivot != row:
            A[[row, pivot]] = A[[pivot, row]]
        inv = pow(int(A[row, col] % p), -1, p)
        A[row, :] = (A[row, :] * inv) % p
        for r in range(m):
            if r == row:
                continue
            factor = int(A[r, col] % p)
            if factor:
                A[r, :] = (A[r, :] - factor * A[row, :]) % p
        pivots.append(int(col))
        row += 1
        if row == m:
            break
    return int(row), A % p, pivots


def all_solutions(A: np.ndarray) -> list[Dict[U2, int]]:
    """Convenience wrapper for the p=3 case."""
    return all_solutions_p(A, 3)


def all_solutions_p(A: np.ndarray, p: int) -> list[Dict[tuple[int, int], int]]:
    r"""Return *all* cochain solutions for matrix ``A`` over \(\mathbb F_p\).

    The arguments mirror :func:`all_solutions` but work for any odd prime ``p``.
    We solve the linear system on \(\mu:\mathbb F_p^2\to\mathbb F_p\) (with
    the gauge \(\mu(0)=0\)) by row-reduction over \(\mathbb F_p\), and then
    generate the full affine solution space by adding all linear functionals.

        phi_p(A g, A h) - phi_p(g, h) = mu(g+h) - mu(g) - mu(h)  (mod p)

    where ``phi_p(g,h)=g[0]*h[1]`` is the standard Heisenberg cocycle.

    The list returned consists of dictionaries mapping the \(p^2\) vectors
    of \(\mathbb F_p^2\) to elements of \(\mathbb F_p\).  Solutions form an
    affine space over the 2-dimensional space of linear functionals.
    """

    p = int(p)
    if p <= 1 or p % 2 == 0:
        raise ValueError(f"expected odd prime p, got {p}")

    A = (np.asarray(A, dtype=np.int64) % p).reshape((2, 2))

    # vector space V = F_p^2
    V = [(i, j) for i in range(p) for j in range(p)]

    def apply_matrix_p(A: np.ndarray, g: tuple[int,int]) -> tuple[int,int]:
        return (
            (int(A[0, 0]) * g[0] + int(A[0, 1]) * g[1]) % p,
            (int(A[1, 0]) * g[0] + int(A[1, 1]) * g[1]) % p,
        )

    def phi_p(g: tuple[int,int], h: tuple[int,int]) -> int:
        return (g[0] * h[1]) % p

    # precompute deltas
    delta = {}
    for g, h in itertools.product(V, V):
        delta[(g, h)] = (
            phi_p(apply_matrix_p(A, g), apply_matrix_p(A, h)) - phi_p(g, h)
        ) % p

    nonzeros = [v for v in V if v != (0, 0)]
    idx = {v: i for i, v in enumerate(nonzeros)}  # unknown index
    n = len(nonzeros)  # = p^2 - 1

    # Build dense linear system M x = b over F_p:
    #   x[v] = mu(v) for v != 0; and mu(0)=0 is fixed.
    rows = p * p * p * p
    M = np.zeros((rows, n), dtype=np.int64)
    b = np.zeros((rows,), dtype=np.int64)
    r = 0
    for g in V:
        for h in V:
            gh = _add_p(g, h, p)
            # mu(g+h) - mu(g) - mu(h) = delta(g,h)
            if gh != (0, 0):
                M[r, idx[gh]] = (M[r, idx[gh]] + 1) % p
            if g != (0, 0):
                M[r, idx[g]] = (M[r, idx[g]] - 1) % p
            if h != (0, 0):
                M[r, idx[h]] = (M[r, idx[h]] - 1) % p
            b[r] = int(delta[(g, h)] % p)
            r += 1

    # Solve by row-reducing the augmented system [M|b].
    aug = np.concatenate([M, b.reshape((-1, 1))], axis=1) % p
    _rank, rref, pivots = _row_reduce_mod_p(aug, p)

    # Inconsistency check: 0 = 1 rows.
    for i in range(rref.shape[0]):
        if np.all((rref[i, :n] % p) == 0) and int(rref[i, n] % p) != 0:
            return []

    # Pick a particular solution by setting all free variables = 0.
    x0 = np.zeros((n,), dtype=np.int64)
    for row, col in enumerate(pivots):
        x0[int(col)] = int(rref[row, n] % p)

    mu0: dict[tuple[int, int], int] = {(0, 0): 0}
    for v in nonzeros:
        mu0[v] = int(x0[idx[v]] % p)

    # Generate the full affine space by adding all linear maps (a,b)⋅(x,y).
    out: list[Dict[tuple[int, int], int]] = []
    for a in range(p):
        for bb in range(p):
            mu: dict[tuple[int, int], int] = {}
            for x, y in V:
                mu[(x, y)] = int((mu0[(x, y)] + a * x + bb * y) % p)
            out.append(mu)
    return out




def canonical_phase(A: np.ndarray) -> Dict[U2, int]:
    """Return the canonical phase as computed by grade_weil_phase.

    This is just a thin wrapper around :func:`grade_weil_phase.compute_phase`.
    It is provided here so that tests can compare the two methods.
    """
    from scripts.grade_weil_phase import compute_phase

    mu = compute_phase(A)
    if mu is None:
        raise RuntimeError("compute_phase returned None")
    # extend with zero at origin
    out = {(0, 0): 0}
    out.update(mu)
    return out


# -----------------------------------------------------------------------------
# helper routines for deeper exploration
# -----------------------------------------------------------------------------

def _linear_functional(a: int, b: int) -> Dict[U2, int]:
    """Linear map V=F3^2→F3 sending (x,y) to a*x + b*y."""
    return {(x, y): (a * x + b * y) % 3 for x in range(3) for y in range(3)}


def linear_functionals() -> list[Dict[U2, int]]:
    """List all additive characters ``V->F3`` (nine total)."""
    return [_linear_functional(a, b) for a in range(3) for b in range(3)]


def is_linear(mu: Dict[U2, int]) -> bool:
    """Return ``True`` if ``mu`` agrees with a linear functional on its domain."""
    trimmed = {g: v for g, v in mu.items() if g != (0, 0)}
    return any(all(trimmed.get(g, 0) == lf[g] for g in trimmed) for lf in linear_functionals())


def difference(mu1: Dict[U2, int], mu2: Dict[U2, int]) -> Dict[U2, int]:
    """Pointwise subtraction ``mu1-mu2`` (mod 3)."""
    return {g: (mu1.get(g, 0) - mu2.get(g, 0)) % 3 for g in set(mu1) | set(mu2)}


def difference_is_linear(mu1: Dict[U2, int], mu2: Dict[U2, int]) -> bool:
    """Return whether ``mu1-mu2`` is an additive character."""
    return is_linear(difference(mu1, mu2))


def solution_space_metadata(A: np.ndarray) -> dict:
    """Gather statistics about the cocycle solutions for ``A``.

    The returned dict contains:

    * ``order`` – multiplicative order of ``A`` in Sp(2,3);
    * ``trace`` – trace of ``A``; 0,1,2 modulo 3;
    * ``canonical`` – full 9‑point canonical phase map;
    * ``dist`` – histogram of values appearing in ``canonical``;
    * ``num_solutions`` – cardinality of the affine solution set (should be 9).
    """
    # compute order
    I = np.eye(2, dtype=int)
    k = 1
    M = A.copy()
    while not np.array_equal(M % 3, I):
        M = (M @ A) % 3
        k += 1
        if k > 50:  # safety
            k = None
            break

    mu_can = canonical_phase(A)
    hist: dict[int, int] = {}
    for v in mu_can.values():
        hist[v] = hist.get(v, 0) + 1

    return {
        "order": k,
        "trace": int((A[0, 0] + A[1, 1]) % 3),
        "canonical": mu_can,
        "dist": hist,
        "num_solutions": len(all_solutions(A)),
    }

