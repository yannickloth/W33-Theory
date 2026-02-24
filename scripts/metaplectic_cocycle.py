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


def all_solutions(A: np.ndarray) -> list[Dict[U2, int]]:
    r"""Return *all* cochain solutions \mu_A satisfying the cocycle eq.

    For each 2×2 matrix ``A`` over F3 we brute-force the 3^8 possible
    assignments on the nonzero grades (with mu(0,0)=0) and collect those
    satisfying

        phi(A g, A h) - phi(g, h) = mu(g+h) - mu(g) - mu(h)   (mod 3)

    The result is a list of dictionaries mapping the 9 vectors of F3^2
    to values in F3.  The affine structure of the solution space is
    obvious: adding any linear functional (a*g+b*h) to a solution produces
    another.
    """

    V = [(i, j) for i in range(3) for j in range(3)]
    solutions: list[Dict[U2, int]] = []

    # precompute deltas
    delta = {}
    for g, h in itertools.product(V, V):
        delta[(g, h)] = (
            phi(apply_matrix(A, g), apply_matrix(A, h)) - phi(g, h)
        ) % 3

    # iterate over all assignments on nonzero grades; include zero fixed to 0
    nonzeros = GRADES_NONZERO
    for values in itertools.product(range(3), repeat=len(nonzeros)):
        mu = {(0, 0): 0}
        mu.update({g: int(v) for g, v in zip(nonzeros, values)})
        ok = True
        for g, h in itertools.product(V, V):
            gh = _add(g, h)
            lhs = (mu[gh] - mu[g] - mu[h]) % 3
            if lhs != delta[(g, h)]:
                ok = False
                break
        if ok:
            solutions.append(mu)
    return solutions




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

