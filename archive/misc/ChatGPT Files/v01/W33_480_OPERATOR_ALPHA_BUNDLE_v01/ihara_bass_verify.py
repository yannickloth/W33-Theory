
#!/usr/bin/env python3
"""ihara_bass_verify.py

Numerical verification of the Ihara–Bass determinant identity for a k-regular graph:

  det(I - u B) = (1 - u^2)^(m-n) * det(I - u A + u^2 (k-1) I)

where:
  - A is the n×n adjacency matrix (n=40)
  - B is the 2m×2m non-backtracking operator (2m=480)
  - m is the number of undirected edges (m=240)
  - k is the degree (k=12)

We verify using eigenvalues:
  det(I - uB) = Π_i (1 - u β_i)
  det(I - uA + u^2(k-1)I) = Π_j (1 - u λ_j + u^2(k-1))

NOTE: This check is *exact up to numerical floating precision*.
"""

from __future__ import annotations
import numpy as np
from scipy import sparse
import numpy.linalg as LA


def load_A():
    return np.load("w33_adjacency.npy").astype(float)


def load_B():
    return sparse.load_npz("w33_nonbacktracking_B.npz").astype(float).toarray()


def logdet_from_eigs(eigs, u):
    u = complex(u)
    return np.sum(np.log(1 - u * eigs))


def main():
    A = load_A()
    B = load_B()

    n = A.shape[0]
    m = int(A.sum() // 2)
    k = int(A.sum(axis=1)[0])

    eigA = LA.eigvalsh(A)
    eigB = LA.eigvals(B)

    print("Ihara–Bass determinant identity check")
    print("=" * 72)
    print(f"n={n}, m={m}, 2m={2*m}, k={k}")
    print()

    us = [0.01, 0.05, 0.1, 0.2, 0.3, 0.5]
    for u in us:
        lhs = logdet_from_eigs(eigB, u)
        rhs = (m - n) * np.log(1 - (complex(u) ** 2)) + np.sum(
            np.log(1 - complex(u) * eigA + (k - 1) * (complex(u) ** 2) + 0j)
        )
        diff = lhs - rhs
        print(f"u={u:>4}: |lhs-rhs| = {abs(diff):.3e}")

    print("\nIf errors are ~1e-14 or smaller, the identity is numerically verified.")


if __name__ == "__main__":
    main()
