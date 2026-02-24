#!/usr/bin/env python3
"""Compute a Weil/metaplectic phase law on the grade plane F3^2.

Given our 2-cocycle phi(g,h) from the Golay algebra, any linear symplectic
transformation A : F3^2 -> F3^2 induces a new cocycle
    phi_A(g,h) = phi(A*g, A*h)
which is cohomologous to phi because omega is preserved.  A phase function
µ(A, g) satisfying

    phi_A(g,h) - phi(g,h) = µ(A, g+h) - µ(A, g) - µ(A, h)

provides the metaplectic correction needed for lifting the Sp-action to the
central extension.  This script computes µ for a given A (if possible).

Example usage:
    from scripts.grade_weil_phase import phi, compute_phase
    A = np.array([[0,1],[2,0]])  # some symplectic matrix mod3
    mu = compute_phase(A)
    print(mu)

The output is a dict mapping each nonzero grade to an F3 phase.
"""

import itertools
import numpy as np

# reimport phi_const_map from earlier; for convenience recreate here
phi_const = {
    ((0, 1), (1, 0)): 2,
    ((0, 1), (1, 1)): 1,
    ((0, 1), (1, 2)): 0,
    ((0, 1), (2, 0)): 1,
    ((0, 1), (2, 1)): 0,
    ((0, 1), (2, 2)): 2,
    ((0, 2), (1, 0)): 0,
    ((0, 2), (1, 1)): 1,
    ((0, 2), (1, 2)): 2,
    ((0, 2), (2, 0)): 1,
    ((0, 2), (2, 1)): 2,
    ((0, 2), (2, 2)): 0,
    ((1, 0), (0, 1)): 2,
    ((1, 0), (0, 2)): 0,
    ((1, 0), (1, 1)): 0,
    ((1, 0), (1, 2)): 2,
    ((1, 0), (2, 1)): 1,
    ((1, 0), (2, 2)): 1,
    ((1, 1), (0, 1)): 1,
    ((1, 1), (0, 2)): 1,
    ((1, 1), (1, 0)): 0,
    ((1, 1), (1, 2)): 2,
    ((1, 1), (2, 0)): 0,
    ((1, 1), (2, 1)): 2,
    ((1, 2), (0, 1)): 0,
    ((1, 2), (0, 2)): 2,
    ((1, 2), (1, 0)): 2,
    ((1, 2), (1, 1)): 2,
    ((1, 2), (2, 0)): 2,
    ((1, 2), (2, 2)): 1,
    ((2, 0), (0, 1)): 1,
    ((2, 0), (0, 2)): 1,
    ((2, 0), (1, 1)): 0,
    ((2, 0), (1, 2)): 2,
    ((2, 0), (2, 1)): 2,
    ((2, 0), (2, 2)): 0,
    ((2, 1), (0, 1)): 0,
    ((2, 1), (0, 2)): 2,
    ((2, 1), (1, 0)): 1,
    ((2, 1), (1, 1)): 2,
    ((2, 1), (2, 0)): 2,
    ((2, 1), (2, 2)): 2,
    ((2, 2), (0, 1)): 2,
    ((2, 2), (0, 2)): 0,
    ((2, 2), (1, 0)): 1,
    ((2, 2), (1, 2)): 1,
    ((2, 2), (2, 0)): 0,
    ((2, 2), (2, 1)): 2,
}

grades = [(i, j) for i in range(3) for j in range(3) if not (i == 0 and j == 0)]

def omega(g, h):
    return (g[0]*h[1] - g[1]*h[0]) % 3


def phi(g, h):
    return phi_const.get((g, h), 0)


def apply_matrix(A, g):
    return ((A[0,0]*g[0] + A[0,1]*g[1]) % 3, (A[1,0]*g[0] + A[1,1]*g[1]) % 3)


def compute_phase(A: np.ndarray) -> dict:
    """Solve for µ such that phi(A*g,A*h)-phi(g,h) = µ(g+h)-µ(g)-µ(h).

    Returns dict grade->µ value in F3, or None if no solution exists.
    """
    # unknowns µ_g for each nonzero grade (8 variables). brute-force search.
    for assign in itertools.product(range(3), repeat=len(grades)):
        mu = dict(zip(grades, assign))
        ok = True
        for g in grades:
            for h in grades:
                gh = ((g[0]+h[0])%3, (g[1]+h[1])%3)
                if gh == (0,0):
                    continue
                lhs = (phi(apply_matrix(A,g), apply_matrix(A,h)) - phi(g,h)) % 3
                rhs = (mu[gh] - mu[g] - mu[h]) % 3
                if lhs != rhs:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return mu
    return None


def all_symplectic_matrices():
    # generate all 2x2 matrices over F3 with det=1 (Sp(2,3)=SL(2,3))
    mats = []
    for a,b,c,d in itertools.product(range(3), repeat=4):
        if (a*d - b*c) % 3 == 1:
            mats.append(np.array([[a,b],[c,d]], dtype=int))
    return mats

if __name__ == '__main__':
    mats = all_symplectic_matrices()
    print('total Sp(2,3) mats:', len(mats))
    for A in mats:
        mu = compute_phase(A)
        if mu is not None:
            print('found phase for A=\n', A)
            print(mu)
            break
    else:
        print('no phase found for any symplectic A')
