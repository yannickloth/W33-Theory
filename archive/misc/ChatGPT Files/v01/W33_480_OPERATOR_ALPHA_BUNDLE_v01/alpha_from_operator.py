
#!/usr/bin/env python3
"""alpha_from_operator.py

This file delivers the missing hinge for the SRG alpha correction term.

Given the W(3,3) collinearity graph SRG(v,k,λ,μ) = SRG(40,12,2,4),
define the vertex-space operator:

    M := (k-1) * ( (A - λ I)^2 + I )

where A is the adjacency matrix.

Key fact:
  The all-ones vector 1 is an eigenvector of A with eigenvalue k.
  Therefore 1 is an eigenvector of M with eigenvalue:
    (k-1) * ( (k-λ)^2 + 1 ).

Hence:
    1^T M^{-1} 1 = v / [ (k-1) * ( (k-λ)^2 + 1 ) ].

For W(3,3): this equals 40 / 1111 = 0.036003600360...

This *exactly* reproduces the fractional term in your alpha formula:
    α^{-1} = (k^2 - 2μ + 1) + 1^T M^{-1} 1
          = 137 + 40/1111
          = 137.036003600360...

Interpretation:
  - (A-λI) recenters the spectrum at the "λ-mode" (here λ=2 equals the SRG
    parameter and also an adjacency eigenvalue).
  - The "+I" is an imaginary-mass / phase regularizer: (X^2 + I) = (X-i)(X+i).
  - The leading (k-1) is the natural factor coming from directed-edge dynamics
    (non-backtracking outdegree).

This does not *yet* fix physical normalization of α (that requires a physics
model), but it converts the ad hoc denominator into a forced operator identity.
"""


from __future__ import annotations
import numpy as np
from fractions import Fraction


def main():
    A = np.load("w33_adjacency.npy").astype(float)
    v = A.shape[0]
    k = int(A.sum(axis=1)[0])

    # SRG parameters for W(3,3)
    lam = 2
    mu = 4

    I = np.eye(v)

    M = (k - 1) * (((A - lam * I) @ (A - lam * I)) + I)

    ones = np.ones(v)
    x = np.linalg.solve(M, ones)
    frac_term = float(ones @ x)

    denom = (k - 1) * (((k - lam) ** 2) + 1)
    frac_closed = v / denom

    integer_part = k * k - 2 * mu + 1
    alpha_inv = integer_part + frac_term

    print("Alpha correction as a forced operator identity")
    print("=" * 72)
    print(f"v={v}, k={k}, λ={lam}, μ={mu}")
    print()
    print("Define M = (k-1)((A-λI)^2 + I). Then:")
    print(f"  denom = (k-1)((k-λ)^2+1) = {denom}")
    print(f"  ones^T M^{-1} ones (numeric) = {frac_term:.15f}")
    print(f"  closed form v/denom          = {frac_closed:.15f}")
    print(f"  exact rational               = {Fraction(frac_term).limit_denominator()}\n")
    print(f"Integer part: k^2 - 2μ + 1 = {integer_part}")
    print(f"alpha^{-1} = integer + frac = {alpha_inv:.15f}")
    print(f"exact rational alpha^{-1}    = {Fraction(alpha_inv).limit_denominator()}")


if __name__ == "__main__":
    main()
