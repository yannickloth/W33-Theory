
#!/usr/bin/env python3
"""build_w33.py

Reconstruct W(3,3) as the collinearity graph of GQ(3,3), realized as
1D subspaces of F3^4 with adjacency given by symplectic orthogonality:
    v ~ w  iff  v^T J w = 0 mod 3 and v != w.

Outputs:
  - adjacency matrix A (40x40)
  - SRG parameter checks: v=40, k=12, lambda=2, mu=4
  - spectrum of A: {12^1, 2^24, (-4)^15}

This script is self-contained and does not depend on repo files.
"""

from __future__ import annotations
import itertools
import numpy as np

F = (0, 1, 2)

# Standard symplectic form J on F3^4 (block [[0,I],[-I,0]])
J = np.array(
    [
        [0, 0, 1, 0],
        [0, 0, 0, 1],
        [-1, 0, 0, 0],
        [0, -1, 0, 0],
    ],
    dtype=int,
) % 3


def dotJ(v: np.ndarray, w: np.ndarray) -> int:
    return int((v @ J @ w) % 3)


def normalize_1d(v: np.ndarray) -> np.ndarray:
    """Normalize a nonzero vector by scaling so the first nonzero entry is 1."""
    for c in v:
        if c % 3 != 0:
            inv = 1 if c % 3 == 1 else 2  # inverse in F3
            return (v * inv) % 3
    raise ValueError("zero vector cannot be normalized")


def build_points() -> list[np.ndarray]:
    points = []
    seen = set()
    for tup in itertools.product(F, repeat=4):
        if all(c == 0 for c in tup):
            continue
        v = np.array(tup, dtype=int) % 3
        vn = normalize_1d(v)
        key = tuple(vn.tolist())
        if key not in seen:
            seen.add(key)
            points.append(vn)
    assert len(points) == 40
    return points


def build_adjacency(points: list[np.ndarray]) -> np.ndarray:
    n = len(points)
    A = np.zeros((n, n), dtype=int)
    for i, v in enumerate(points):
        for j, w in enumerate(points):
            if i != j and dotJ(v, w) == 0:
                A[i, j] = 1
    return A


def srg_params(A: np.ndarray):
    n = A.shape[0]
    deg = A.sum(axis=1)
    assert np.all(deg == deg[0])
    k = int(deg[0])

    # lambda: common neighbors of adjacent vertices
    # mu: common neighbors of nonadjacent distinct vertices
    lam_vals = set()
    mu_vals = set()
    for i in range(n):
        for j in range(i + 1, n):
            cn = int(np.dot(A[i], A[j]))
            if A[i, j] == 1:
                lam_vals.add(cn)
            else:
                mu_vals.add(cn)
    if len(lam_vals) != 1 or len(mu_vals) != 1:
        raise RuntimeError(f"Not SRG: lambda set={lam_vals}, mu set={mu_vals}")
    lam = next(iter(lam_vals))
    mu = next(iter(mu_vals))
    return n, k, lam, mu


def spectrum(A: np.ndarray):
    eig = np.linalg.eigvalsh(A.astype(float))
    # group by rounded value
    counts = {}
    for x in eig:
        r = int(round(x))
        counts[r] = counts.get(r, 0) + 1
    return counts


def main():
    points = build_points()
    A = build_adjacency(points)

    v, k, lam, mu = srg_params(A)
    m = int(A.sum() // 2)

    print("W(3,3) / GQ(3,3) collinearity graph")
    print("=" * 72)
    print(f"v={v} vertices")
    print(f"k={k} regular degree")
    print(f"edges m=vk/2 = {m}")
    print(f"SRG parameters: SRG({v},{k},{lam},{mu})")
    print()
    print("Adjacency eigenvalue multiplicities:")
    for val, mult in sorted(spectrum(A).items()):
        print(f"  {val:>3} : {mult}")

    # Save adjacency for other scripts
    np.save("w33_adjacency.npy", A)
    print("\nSaved w33_adjacency.npy")


if __name__ == "__main__":
    main()
