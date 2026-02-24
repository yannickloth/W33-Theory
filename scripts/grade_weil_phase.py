#!/usr/bin/env python3
"""Metaplectic/Weil 1-cocycle on the grade plane F3^2.

This is a small, *self-contained* computation for the qutrit (p=3) case.

Let V = F3^2 with coordinates g=(x,y). A convenient (non-alternating) Heisenberg
2-cocycle for a section V -> H(V) is:

    phi(g,h) := x * y'  (mod 3)  where h=(x',y').

This cocycle is cohomologous to the alternating form omega(g,h)=x*y' - y*x'
and corresponds to a choice of ordering/section for Weyl operators.

For any A in Sp(2,3)=SL(2,3), define the transported cocycle:

    phi_A(g,h) := phi(A g, A h).

Because A preserves the alternating class, phi_A is cohomologous to phi, so
there exists a 1-cochain mu_A: V -> F3 such that:

    phi_A(g,h) - phi(g,h) = mu_A(g+h) - mu_A(g) - mu_A(h).          (*)

This mu_A is the finite-field shadow of the metaplectic (Weil) correction.
We compute one canonical solution with mu_A(0)=0 by solving the linear system
over GF(3) induced by (*).

The returned mu is a dict on the 8 nonzero grades (0,0) is fixed to 0.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np

F3 = 3
U2 = tuple[int, int]

GRADES_NONZERO: tuple[U2, ...] = tuple(
    (i, j) for i in range(3) for j in range(3) if not (i == 0 and j == 0)
)


def _u2_add(g: U2, h: U2) -> U2:
    return ((int(g[0]) + int(h[0])) % 3, (int(g[1]) + int(h[1])) % 3)


def omega(g: U2, h: U2) -> int:
    """Alternating form omega((x,y),(x',y')) = x*y' - y*x' (mod 3)."""
    return int((int(g[0]) * int(h[1]) - int(g[1]) * int(h[0])) % 3)


def phi(g: U2, h: U2) -> int:
    """A standard (section-dependent) Heisenberg cocycle: phi(g,h)=x*y' (mod 3)."""
    return int((int(g[0]) * int(h[1])) % 3)


def apply_matrix(A: np.ndarray, g: U2) -> U2:
    return (
        (int(A[0, 0]) * int(g[0]) + int(A[0, 1]) * int(g[1])) % 3,
        (int(A[1, 0]) * int(g[0]) + int(A[1, 1]) * int(g[1])) % 3,
    )


@dataclass(frozen=True)
class LinearSystemMod3:
    A: np.ndarray  # shape (m,n) in {0,1,2}
    b: np.ndarray  # shape (m,) in {0,1,2}


def _solve_mod3(system: LinearSystemMod3) -> np.ndarray | None:
    """Solve A x = b over GF(3), returning one solution with free vars = 0."""
    A = np.array(system.A, dtype=np.int64) % 3
    b = np.array(system.b, dtype=np.int64) % 3
    m, n = A.shape

    # Augmented matrix [A | b].
    M = np.zeros((m, n + 1), dtype=np.int64)
    M[:, :n] = A
    M[:, n] = b

    pivot_cols: list[int] = []
    row = 0
    for col in range(n):
        if row >= m:
            break
        pivot = None
        for r in range(row, m):
            if int(M[r, col]) % 3 != 0:
                pivot = r
                break
        if pivot is None:
            continue
        if pivot != row:
            M[[row, pivot]] = M[[pivot, row]]
        inv = pow(int(M[row, col] % 3), -1, 3)
        M[row, :] = (M[row, :] * inv) % 3
        for r in range(m):
            if r == row:
                continue
            f = int(M[r, col] % 3)
            if f:
                M[r, :] = (M[r, :] - f * M[row, :]) % 3
        pivot_cols.append(int(col))
        row += 1

    # Check consistency: rows [0 ...] = 0 with nonzero RHS.
    for r in range(row, m):
        if int(np.sum(M[r, :n]) % 3) == 0 and int(M[r, n] % 3) != 0:
            return None

    free_cols = [c for c in range(n) if c not in pivot_cols]
    x = np.zeros((n,), dtype=np.int64)
    # free vars already set to 0; solve pivot vars from reduced form.
    for pr, pc in enumerate(pivot_cols):
        acc = int(M[pr, n] % 3)
        for fc in free_cols:
            acc = (acc - int(M[pr, fc]) * int(x[fc])) % 3
        x[pc] = acc % 3
    return x % 3


def compute_phase(A: np.ndarray) -> dict[U2, int] | None:
    """Return mu_A on the 8 nonzero grades, normalized by mu_A(0)=0."""
    grades = list(GRADES_NONZERO)
    idx = {g: i for i, g in enumerate(grades)}

    rows: list[np.ndarray] = []
    rhs: list[int] = []

    for g in grades:
        for h in grades:
            gh = _u2_add(g, h)
            lhs = (phi(apply_matrix(A, g), apply_matrix(A, h)) - phi(g, h)) % 3

            # Equation: mu(gh) - mu(g) - mu(h) = lhs, with mu(0)=0.
            row = np.zeros((len(grades),), dtype=np.int64)
            if gh != (0, 0):
                row[idx[gh]] = (row[idx[gh]] + 1) % 3
            row[idx[g]] = (row[idx[g]] - 1) % 3
            row[idx[h]] = (row[idx[h]] - 1) % 3
            rows.append(row % 3)
            rhs.append(int(lhs))

    system = LinearSystemMod3(A=np.stack(rows, axis=0) % 3, b=np.array(rhs) % 3)
    sol = _solve_mod3(system)
    if sol is None:
        return None

    return {g: int(sol[i] % 3) for i, g in enumerate(grades)}


def all_symplectic_matrices() -> list[np.ndarray]:
    """All 2×2 matrices over F3 with det=1 (Sp(2,3)=SL(2,3), size 24)."""
    mats: list[np.ndarray] = []
    for a, b, c, d in itertools.product(range(3), repeat=4):
        if (a * d - b * c) % 3 == 1:
            mats.append(np.array([[a, b], [c, d]], dtype=int))
    return mats


def verify_cocycle_identity() -> None:
    """Quick sanity: phi is a 2-cocycle on the additive group V."""
    V = [(i, j) for i in range(3) for j in range(3)]
    for a in V:
        for b in V:
            for c in V:
                # phi(b,c) - phi(a+b,c) + phi(a,b+c) - phi(a,b) == 0
                ab = _u2_add(a, b)
                bc = _u2_add(b, c)
                left = (phi(b, c) - phi(ab, c) + phi(a, bc) - phi(a, b)) % 3
                if left != 0:
                    raise AssertionError(f"phi is not a cocycle at {(a,b,c)}")


def main() -> None:
    verify_cocycle_identity()
    mats = all_symplectic_matrices()
    print("total Sp(2,3) mats:", len(mats))
    n_ok = 0
    n_nontrivial = 0
    for A in mats:
        mu = compute_phase(A)
        if mu is None:
            continue
        n_ok += 1
        if any(v != 0 for v in mu.values()):
            n_nontrivial += 1
    print("phase solved for:", n_ok, "matrices")
    print("nontrivial phases:", n_nontrivial)
    if n_ok != len(mats):
        raise SystemExit("ERROR: phase solver failed for some symplectic matrices")

    # verify the 1-cocycle property: mu_{AB}(g) = mu_A(g) + mu_B(A g)
    def _verify_cocycle() -> bool:
        for A in mats:
            for B in mats:
                muA = compute_phase(A)
                muB = compute_phase(B)
                muAB = compute_phase((A @ B) % 3)
                if muA is None or muB is None or muAB is None:
                    return False
                for g in GRADES_NONZERO:
                    lhs = int(muAB[g])
                    rhs = (int(muA[g]) + int(muB[apply_matrix(A, g)])) % 3
                    if lhs != rhs:
                        print("cocycle failure", A, B, g, lhs, rhs)
                        return False
        return True

    if not _verify_cocycle():
        raise SystemExit("ERROR: Weil phase failed 1-cocycle identity")
    else:
        print("1-cocycle identity holds for all pairs")

    print("ALL CHECKS PASSED ✓")


if __name__ == "__main__":
    main()
