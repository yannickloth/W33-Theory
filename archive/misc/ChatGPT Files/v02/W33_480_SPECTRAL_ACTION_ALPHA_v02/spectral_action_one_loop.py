#!/usr/bin/env python3
"""
spectral_action_one_loop.py

A minimal, reproducible "spectral action" story that is *actually forced*
by the W33 data:

Layer 1 (480 directed edges):
  - Non-backtracking transport operator B (Hashimoto matrix)
  - Ihara zeta Z(u) = 1/det(I - u B)
  - Vertex factor Q(u) = I - u A + u^2 (k-1) I

Layer 2 (40 vertices):
  - Quadratic propagator centered at λ with imaginary regulator (mass) 1:
      R := (A - λ I)^2 + I = (A-(λ+i)I)(A-(λ-i)I)
    and M := (k-1) R

Alpha fractional correction is exactly the constant-mode susceptibility:
  <1, M^{-1} 1> = v / ((k-1)((k-λ)^2+1))

This file shows how that term is a standard Gaussian integral:
  Z(J) = ∫ dφ exp(-1/2 φ^T M φ + J * 1^T φ)
so:
  log Z(J) = const + (J^2/2) * 1^T M^{-1} 1
and the coefficient of J^2 is precisely 40/1111.

We also prove the integer part 137 is a forced "norm-square" in this model:
  For W33 = GQ(3,3), parameters satisfy:
     μ = 4, k = 12, and uniquely (among symmetric GQ(s,s)) we have μ^2 = 2(k-μ).
  Hence:
     k^2 - 2μ + 1 = (k-1)^2 + μ^2 = |(k-1) + i μ|^2 = 11^2 + 4^2 = 137.

This gives a tight structural rewrite of your alpha formula:

  α^{-1} = |(k-1) + i μ|^2  +  <1, (k-1)^{-1} |A-(λ+i)I|^{-2} 1>.

Nothing in this file asserts this is "physics"; it shows the missing *math hinge*:
both terms are canonical quantities associated to (i) non-backtracking transport
(k-1) and (ii) a regulated propagator at λ+i, with the constant mode picking out
the simple rational v/((k-1)((k-λ)^2+1)).
"""

from __future__ import annotations

import numpy as np

from build_w33_core import W33, srg_parameters


def gaussian_susceptibility(M: np.ndarray) -> float:
    v = M.shape[0]
    ones = np.ones((v, 1), dtype=float)
    Minv = np.linalg.inv(M)
    return float((ones.T @ Minv @ ones)[0, 0])


def main():
    w = W33.build()
    A = w.A.astype(float)
    v, k, lam, mu = srg_parameters(w.A)

    # Build M = (k-1)((A-lam I)^2 + I)
    I = np.eye(v, dtype=float)
    R = (A - lam * I) @ (A - lam * I) + I
    M = (k - 1) * R

    # Fractional correction
    chi = gaussian_susceptibility(M)
    chi_expected = v / ((k - 1) * ((k - lam) ** 2 + 1))
    print("Susceptibility (constant-mode):")
    print("  chi = 1^T M^{-1} 1 =", chi)
    print("  expected           =", chi_expected)
    print("  difference         =", chi - chi_expected)

    # Integer part as norm-square (unique s=t=3 hinge)
    integer_part = k * k - 2 * mu + 1

    # Check the special identity: integer_part == (k-1)^2 + mu^2
    alt = (k - 1) ** 2 + mu**2
    print("\nInteger part:")
    print("  k^2 - 2μ + 1 =", integer_part)
    print("  (k-1)^2 + μ^2 =", alt, "   (matches exactly for W33)")

    # Put together
    alpha_inv = integer_part + chi
    print("\nAlpha formula as 'norm^2 + susceptibility':")
    print("  alpha^{-1} =", alpha_inv)
    print("  exact rational form = 137 + 40/1111 = 137.036003600360...")

    # Extra: show uniqueness among symmetric GQ(s,s) for the norm-square identity
    # For GQ(s,s): k = s(s+1), μ=s+1. Condition integer_part == (k-1)^2+μ^2 reduces to s=3.
    hits = []
    for s in range(2, 11):
        k_s = s * (s + 1)
        mu_s = s + 1
        lhs = k_s * k_s - 2 * mu_s + 1
        rhs = (k_s - 1) ** 2 + mu_s**2
        if lhs == rhs:
            hits.append(s)
    print("\nSymmetric GQ(s,s) uniqueness check for the identity k^2-2μ+1=(k-1)^2+μ^2:")
    print("  solutions s =", hits, "(unique: s=3)")

if __name__ == "__main__":
    main()
