#!/usr/bin/env python3
"""
build_w33_core.py

Construct the generalized quadrangle GQ(3,3) = W(3,3) in its symplectic model over GF(3),
then expose:

- 40 points = 1D subspaces of GF(3)^4 (projective points)
- collinearity graph adjacency A (40x40) with SRG parameters (40,12,2,4)
- 240 undirected edges, 480 directed edges
- 40 totally isotropic lines (each a K4 clique in A)

We use the standard symplectic form J on GF(3)^4:
  <v,w> = v^T J w  (mod 3)
and define collinearity as: <v,w> == 0 and v != w.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Iterable

import itertools
import numpy as np
import scipy.sparse as sp


F3 = (0, 1, 2)

# Standard symplectic matrix J over GF(3)
J = np.array(
    [
        [0, 0, 1, 0],
        [0, 0, 0, 1],
        [-1, 0, 0, 0],
        [0, -1, 0, 0],
    ],
    dtype=int,
) % 3


def f3_dotJ(v: np.ndarray, w: np.ndarray) -> int:
    return int((v @ J @ w) % 3)


def normalize_1d_subspace(v: Iterable[int]) -> Tuple[int, int, int, int]:
    """
    Normalize a nonzero vector v in GF(3)^4 to a canonical representative
    of its 1D subspace: scale so the first nonzero coordinate equals 1.
    """
    vv = np.array(tuple(v), dtype=int) % 3
    if np.all(vv == 0):
        raise ValueError("Cannot normalize zero vector.")
    # find first nonzero coordinate
    for c in vv:
        if c != 0:
            inv = 1 if c == 1 else 2  # 2 is its own inverse mod 3
            vn = (vv * inv) % 3
            return tuple(int(x) for x in vn)
    raise RuntimeError("Unreachable")


def build_points() -> List[np.ndarray]:
    """Return list of 40 canonical reps of 1D subspaces in GF(3)^4."""
    seen = set()
    pts: List[np.ndarray] = []
    for v in itertools.product(F3, repeat=4):
        if all(c == 0 for c in v):
            continue
        rep = normalize_1d_subspace(v)
        if rep not in seen:
            seen.add(rep)
            pts.append(np.array(rep, dtype=int) % 3)
    assert len(pts) == 40, f"Expected 40 points, got {len(pts)}"
    return pts


def build_adjacency(points: List[np.ndarray]) -> np.ndarray:
    """Build 40x40 adjacency matrix A of collinearity graph."""
    n = len(points)
    A = np.zeros((n, n), dtype=int)
    for i, v in enumerate(points):
        for j, w in enumerate(points):
            if i == j:
                continue
            if f3_dotJ(v, w) == 0:
                A[i, j] = 1
    # sanity: symmetric
    assert np.all(A == A.T)
    # no self-loops
    assert np.all(np.diag(A) == 0)
    return A


def srg_parameters(A: np.ndarray) -> Tuple[int, int, int, int]:
    """Compute SRG(v,k,lambda,mu) parameters from adjacency A."""
    v = A.shape[0]
    degs = A.sum(axis=1)
    k = int(degs[0])
    assert np.all(degs == k)
    # compute common neighbors counts
    # lambda: for adjacent pairs; mu: for non-adjacent pairs
    lam = None
    mu = None
    for i in range(v):
        for j in range(i + 1, v):
            cn = int(np.dot(A[i], A[j]))
            if A[i, j] == 1:
                lam = cn if lam is None else lam
                assert cn == lam
            else:
                mu = cn if mu is None else mu
                assert cn == mu
    assert lam is not None and mu is not None
    return v, k, lam, mu


def adjacency_eigens(A: np.ndarray) -> List[Tuple[float, int]]:
    """Return sorted list of (eigenvalue, multiplicity) for A."""
    w = np.linalg.eigvalsh(A.astype(float))
    # cluster by rounding
    vals = [round(float(x), 10) for x in w]
    out: Dict[float, int] = {}
    for x in vals:
        out[x] = out.get(x, 0) + 1
    return sorted(out.items(), key=lambda t: -t[0])


def build_edges(A: np.ndarray) -> List[Tuple[int, int]]:
    """List undirected edges (i<j)."""
    n = A.shape[0]
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j] == 1:
                edges.append((i, j))
    return edges


def build_directed_edges(edges: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Turn undirected edges into directed edges (a,b) and (b,a)."""
    dedges = []
    for a, b in edges:
        dedges.append((a, b))
        dedges.append((b, a))
    return dedges


def build_nonbacktracking_B(A: np.ndarray, dedges: List[Tuple[int, int]]) -> sp.csr_matrix:
    """
    Hashimoto/non-backtracking matrix B on directed edges.
    B[(a->b),(b->c)] = 1 iff c != a and (b,c) is an edge.
    """
    n_dir = len(dedges)
    # map (u,v) to index
    idx = {e: i for i, e in enumerate(dedges)}
    rows = []
    cols = []
    data = []
    # build adjacency list from A
    neigh = [np.where(A[i] == 1)[0].tolist() for i in range(A.shape[0])]
    for i, (a, b) in enumerate(dedges):
        for c in neigh[b]:
            if c == a:
                continue
            j = idx[(b, c)]
            rows.append(i)
            cols.append(j)
            data.append(1)
    B = sp.csr_matrix((data, (rows, cols)), shape=(n_dir, n_dir), dtype=int)
    return B


def enumerate_totally_isotropic_lines(points: List[np.ndarray]) -> List[Tuple[int, int, int, int]]:
    """
    Enumerate 2D totally isotropic subspaces ("lines") in the symplectic polar space.
    Each such line contains exactly 4 projective points.

    Approach:
      - pick two distinct points p,q with <p,q>=0
      - consider span{p,q} in GF(3)^4 (a 2D subspace)
      - collect its 1D subspaces: {p, q, p+q, p+2q} (up to scaling)
      - normalize each to projective reps and map to point indices
      - deduplicate
    """
    # map canonical reps to index
    rep_to_idx = {tuple(int(x) for x in p.tolist()): i for i, p in enumerate(points)}
    lines = set()
    for i, p in enumerate(points):
        for j, q in enumerate(points):
            if j <= i:
                continue
            if f3_dotJ(p, q) != 0:
                continue
            # generate nonzero vectors in span
            vs = [
                p,
                q,
                (p + q) % 3,
                (p + 2 * q) % 3,
            ]
            idxs = []
            for v in vs:
                rep = normalize_1d_subspace(v.tolist())
                idxs.append(rep_to_idx[rep])
            idxs = tuple(sorted(set(idxs)))
            if len(idxs) != 4:
                # degenerate if p and q not independent (should not happen)
                continue
            lines.add(idxs)
    lines = sorted(lines)
    # W(3,3) should have 40 lines
    return lines


def assert_lines_are_K4(A: np.ndarray, lines: List[Tuple[int, int, int, int]]) -> None:
    for line in lines:
        for i in range(4):
            for j in range(i + 1, 4):
                assert A[line[i], line[j]] == 1, f"Line not clique: {line}"


@dataclass(frozen=True)
class W33:
    points: List[np.ndarray]
    A: np.ndarray
    edges: List[Tuple[int, int]]
    dedges: List[Tuple[int, int]]
    B: sp.csr_matrix
    lines: List[Tuple[int, int, int, int]]

    @staticmethod
    def build() -> "W33":
        pts = build_points()
        A = build_adjacency(pts)
        edges = build_edges(A)
        dedges = build_directed_edges(edges)
        B = build_nonbacktracking_B(A, dedges)
        lines = enumerate_totally_isotropic_lines(pts)
        assert len(edges) == 240, f"Expected 240 edges, got {len(edges)}"
        assert len(dedges) == 480, f"Expected 480 directed edges, got {len(dedges)}"
        assert len(lines) == 40, f"Expected 40 lines, got {len(lines)}"
        assert_lines_are_K4(A, lines)
        return W33(pts, A, edges, dedges, B, lines)
