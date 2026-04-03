
#!/usr/bin/env python3
"""nonbacktracking_480.py

Build the 480-state directed-edge carrier space (2m with m=240 edges)
and the non-backtracking (Hashimoto) operator B on directed edges.

For a directed edge e=(a->b), B transitions to f=(b->c) where c != a.

Outputs:
  - number of directed edges = 480
  - each row has exactly k-1 = 11 outgoing transitions
  - saves directed edges list and sparse CSR matrix B for reuse
"""

from __future__ import annotations
import numpy as np
from scipy import sparse


def load_A(path: str = "w33_adjacency.npy") -> np.ndarray:
    A = np.load(path)
    if A.shape != (40, 40):
        raise ValueError(f"Unexpected adjacency shape {A.shape}")
    return A


def directed_edges_from_adj(A: np.ndarray):
    n = A.shape[0]
    return [(i, j) for i in range(n) for j in range(n) if A[i, j] == 1]


def build_nonbacktracking(A: np.ndarray):
    dir_edges = directed_edges_from_adj(A)
    idx = {e: t for t, e in enumerate(dir_edges)}
    rows, cols, data = [], [], []
    for i, (a, b) in enumerate(dir_edges):
        nbrs = np.where(A[b] == 1)[0]
        for c in nbrs:
            if c == a:
                continue
            j = idx[(b, c)]
            rows.append(i)
            cols.append(j)
            data.append(1)
    B = sparse.csr_matrix((data, (rows, cols)), shape=(len(dir_edges),) * 2, dtype=np.int8)
    return dir_edges, B


def main():
    A = load_A()
    dir_edges, B = build_nonbacktracking(A)

    print("Directed-edge carrier (2m) + non-backtracking operator")
    print("=" * 72)
    print(f"directed edges: {len(dir_edges)} (expected 480)")
    print(f"B shape: {B.shape}, nnz={B.nnz}")
    outdeg = B.getnnz(axis=1)
    print(f"outdegree min/max: {outdeg.min()}/{outdeg.max()} (expected 11)")
    print(f"mean outdegree: {outdeg.mean():.3f}")
    print()

    # Save artifacts
    np.save("w33_directed_edges.npy", np.array(dir_edges, dtype=np.int16))
    sparse.save_npz("w33_nonbacktracking_B.npz", B)
    print("Saved w33_directed_edges.npy and w33_nonbacktracking_B.npz")


if __name__ == "__main__":
    main()
