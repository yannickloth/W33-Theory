#!/usr/bin/env python3
"""ihara_bass_and_M_bridge.py (optimized)

Builds W33 and the 480×480 non-backtracking operator B, then:

1) Verifies Ihara–Bass determinant identity using sparse LU:
      det(I-uB) = (1-u^2)^{m-n} det(Q(u))
   where Q(u)=I-uA+u^2(k-1)I.

2) Builds the canonical regulated vertex propagator:
      M := (k-1)*((A-λI)^2 + I)
   and proves the alpha fractional term is the constant-mode susceptibility:
      1^T M^{-1} 1 = v/[(k-1)((k-λ)^2+1)] = 40/1111.

3) Connects M to the Ihara vertex factor Q(u) on the non-constant modes by
   choosing the unique complex u solving Q(s)/Q(r)=37 for eigenvalues r=2, s=-4.

Run:
  python ihara_bass_and_M_bridge.py
"""

from __future__ import annotations

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
import scipy.linalg as la

from build_w33_core import W33


def perm_parity(p: np.ndarray) -> int:
    """Return +1 for even permutation, -1 for odd permutation."""
    n = len(p)
    seen = np.zeros(n, dtype=bool)
    parity = 1
    for i in range(n):
        if seen[i]:
            continue
        j = i
        cycle_len = 0
        while not seen[j]:
            seen[j] = True
            j = p[j]
            cycle_len += 1
        if cycle_len > 0 and (cycle_len - 1) % 2 == 1:
            parity *= -1
    return parity


def det_sparse_lu(M: sp.csc_matrix) -> complex:
    """Determinant via sparse LU (SuperLU): det(M)=det(Pr)det(Pc)∏diag(U)."""
    lu = spla.splu(M)
    sign = perm_parity(lu.perm_r) * perm_parity(lu.perm_c)
    diagU = lu.U.diagonal().astype(complex)
    return sign * diagU.prod()


def main():
    w = W33.build()
    A = w.A.astype(float)
    B = w.B

    v, k, lam, mu = 40, 12, 2, 4
    m, n = 240, 40

    # Ihara–Bass check
    I_B = sp.identity(B.shape[0], dtype=complex, format="csc")
    I_A = np.eye(v, dtype=complex)

    print("Ihara–Bass numerical checks (sparse LU det):")
    for u in [0.01, 0.05, -0.03, 0.1]:
        lhs = det_sparse_lu((I_B - (u * B).astype(complex)).tocsc())
        Q = I_A - u * A + (u**2) * (k - 1) * I_A
        rhs = (1 - u**2) ** (m - n) * np.linalg.det(Q)
        rel = abs(lhs - rhs) / max(1.0, abs(rhs))
        print(f"  u={u:+.3f}: rel_err={rel:.2e}")

    # Build M
    A_c = w.A.astype(complex)
    M = (k - 1) * (
        (A_c - lam * np.eye(v, dtype=complex))
        @ (A_c - lam * np.eye(v, dtype=complex))
        + np.eye(v, dtype=complex)
    )

    ones = np.ones((v, 1), dtype=complex)
    frac = (ones.T @ np.linalg.inv(M) @ ones)[0, 0]
    expected = v / ((k - 1) * ((k - lam) ** 2 + 1))

    print("\nAlpha fractional term from operator M:")
    print("  1^T M^{-1} 1 =", frac)
    print("  expected       =", expected)

    # Solve complex u so that Q(s)/Q(r)=37 (r=2, s=-4)
    # 66 u^2 - 13 u + 6 = 0
    a, b, c = 66, -13, 6
    disc = b * b - 4 * a * c
    u1 = (13 + 1j * np.sqrt(-disc)) / (2 * a)
    u2 = (13 - 1j * np.sqrt(-disc)) / (2 * a)

    r_e, s_e = 2.0, -4.0

    def Q_ev(u, ev):
        return 1 - u * ev + (u**2) * (k - 1)

    print("\nComplex u solving ratio constraint Q(s)/Q(r)=37:")
    for uu in [u1, u2]:
        qr = Q_ev(uu, r_e)
        qs = Q_ev(uu, s_e)
        ratio = qs / qr
        print(f"  u = {uu}")
        print(f"    Q(r)={qr}")
        print(f"    Q(s)={qs}")
        print(f"    Q(s)/Q(r)={ratio}  (target 37)")

    # Project comparison on orthogonal-to-ones subspace
    Jm = np.ones((v, v), dtype=complex)
    P = np.eye(v, dtype=complex) - (1 / v) * Jm
    R = (
        (A_c - lam * np.eye(v, dtype=complex))
        @ (A_c - lam * np.eye(v, dtype=complex))
        + np.eye(v, dtype=complex)
    )

    uu = u1
    Q = np.eye(v, dtype=complex) - uu * A_c + (uu**2) * (k - 1) * np.eye(v, dtype=complex)
    # scale by matching trace on P
    cscale = np.trace(P @ Q @ P) / np.trace(P @ R @ P)
    diff = la.norm(P @ (Q - cscale * R) @ P) / max(1.0, la.norm(P @ Q @ P))

    print("\nVertex-factor matching on orthogonal subspace (using u=u1):")
    print(f"  scalar c = {cscale}")
    print(f"  relative Frobenius diff (on P) = {diff:.2e}")
    print("  (Q(u) matches (A-λI)^2+I on non-constant modes, up to scalar.)")


if __name__ == "__main__":
    main()
