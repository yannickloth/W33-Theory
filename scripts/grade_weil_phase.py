#!/usr/bin/env python3
"""Metaplectic/Weil phase on the grade plane F3^2.

This is a small, *self-contained* computation for the qutrit (p=3) case.

Let V = F3^2 with coordinates g=(x,y). A convenient (non-alternating) Heisenberg
2-cocycle for a section V -> H(V) is:

    phi(g,h) := x * y'  (mod 3)  where h=(x',y').

This cocycle is cohomologous to the alternating form omega(g,h)=x*y' - y*x'
and corresponds to a choice of ordering/section for Weyl operators.

For any A in Sp(2,3)=SL(2,3), define the transported cocycle:

    phi_A(g,h) := phi(A g, A h).

Because A preserves the alternating form, phi_A is cohomologous to phi, so there
exists a 1-cochain mu_A: V -> F3 such that:

    phi_A(g,h) - phi(g,h) = mu_A(g+h) - mu_A(g) - mu_A(h).          (*)

This mu_A is the finite-field shadow of the metaplectic (Weil) correction.

Important subtlety (and the reason this file exists): the solution mu_A is not
unique. If mu_A solves (*), then so does mu_A + ℓ for any additive homomorphism
ℓ:V->F3 (i.e. a linear functional). Picking arbitrary representatives for each A
breaks the expected composition law.

We avoid that by using a closed-form gauge choice.

Define the Sp-invariant alternating cocycle:

    psi(g,h) := (1/2)·omega(g,h)  (mod 3),  with 1/2 = 2 in F3.

Then phi and psi differ by an exact coboundary:

    phi(g,h) = psi(g,h) + (d f)(g,h),   with f(x,y) = 2·x·y.

So a canonical, composition-compatible choice is:

    mu_A(g) := f(A g) - f(g).

The returned mu is a dict on the 8 nonzero grades (0,0) is fixed to 0.
"""

from __future__ import annotations

import itertools
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

def psi(g: U2, h: U2) -> int:
    """Sp-invariant alternating cocycle: psi = (1/2)·omega, with 1/2=2 in F3."""
    return int((2 * omega(g, h)) % 3)


def gauge_f(g: U2) -> int:
    """Gauge 1-cochain f(x,y)=2·x·y so that phi = psi + d f."""
    return int((2 * int(g[0]) * int(g[1])) % 3)


def compute_phase(A: np.ndarray) -> dict[U2, int] | None:
    """Return canonical mu_A on the 8 nonzero grades, normalized by mu_A(0)=0."""
    A = np.array(A, dtype=int) % 3
    return {
        g: int((gauge_f(apply_matrix(A, g)) - gauge_f(g)) % 3) for g in GRADES_NONZERO
    }


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

    # verify the 1-cocycle property for the induced Heisenberg automorphisms:
    # (A,mu_A)∘(B,mu_B) = (AB, mu_B + mu_A∘B).
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
                    rhs = (int(muB[g]) + int(muA[apply_matrix(B, g)])) % 3
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
