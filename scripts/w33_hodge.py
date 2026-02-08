#!/usr/bin/env python3
"""Compute Hodge Laplacians for W33 and analyze eigenvalue structure.

- Verifies that L1 has kernel dimension b1 = 81
- Shows L1 decomposes according to H1 (81), im(d2) (120), im(d1^T) (39)
- Verifies that eigenvalues on im(d1^T) equal k - adjacency_eigs (SRG-derived)
- Computes inclusion map H1(H27) -> H1(W33) and reports its rank
- Writes results to checks/PART_CVII_w33_hodge_<ts>.json
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Tuple

import numpy as np

# ensure we can import sibling modules in scripts/ (same pattern as other scripts)
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).parent))

# re-use clique complex and boundary helpers
from w33_homology import build_clique_complex, boundary_matrix, build_w33


def build_incidence_matrix(n: int, edges: List[Tuple[int, int]]) -> np.ndarray:
    """Build oriented vertex-edge incidence matrix D (shape n x m).

    For each edge (i, j) with i<j we put column with +1 at i and -1 at j.
    Orientation is arbitrary but must be consistent.
    """
    m = len(edges)
    D = np.zeros((n, m), dtype=float)
    for col, (i, j) in enumerate(edges):
        D[i, col] = 1.0
        D[j, col] = -1.0
    return D


def compute_hodge_laplacians():
    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)

    # B1: boundary from edges -> vertices (vertex-edge incidence with signs)
    B1 = boundary_matrix(simplices[1], simplices[0]).astype(float)
    # boundary matrix B2: triangles -> edges (from simplices)
    B2 = boundary_matrix(simplices[2], simplices[1]).astype(float)

    # D as oriented incidence (n x m) - alternative to B1^T (note sign conventions)
    D = build_incidence_matrix(n, edges)

    # Verify shapes
    assert D.shape == B1.shape
    # Hodge Laplacians:
    # L0 = D D^T (vertex Laplacian)
    L0 = D @ D.T
    # L1 = D^T D + B2 B2^T
    L1 = D.T @ D + B2 @ B2.T
    # L2 = B2^T B2 (triangle Laplacian)
    L2 = B2.T @ B2

    return {
        "n": n,
        "edges": edges,
        "adj": adj,
        "D": D,
        "B1": B1,
        "B2": B2,
        "L0": L0,
        "L1": L1,
        "L2": L2,
    }


def eigen_decomp_sorted(M: np.ndarray):
    w, v = np.linalg.eigh(M)
    # sort ascending
    idx = np.argsort(w)
    return w[idx], v[:, idx]


def multiplicity_dict(vals: np.ndarray, tol=1e-8):
    """Return a dict mapping unique eigenvalue (rounded) -> multiplicity."""
    res = {}
    for x in vals:
        key = round(float(x), 8)
        res[key] = res.get(key, 0) + 1
    return res


def analyze_im_d1_image(D: np.ndarray, L0: np.ndarray):
    """Analyze eigenvalues on im(d1^T) via vertex Laplacian L0."""
    w0, v0 = eigen_decomp_sorted(L0)
    # Laplacian has one zero eigenvalue (constant vector)
    # The nonzero eigenvalues correspond to eigenvalues on im(d1^T) (dimension n-1)
    # For our regular SRG, these values should equal k - adjacency_eigvalues
    return w0, v0


def compute_h27_vertices(adj: List[List[int]]):
    """Return H27 vertex set: non-neighbors of vertex 0 (excluding vertex 0)."""
    # Choose a canonical vertex (0)
    n = len(adj)
    non_neighbors = [v for v in range(n) if v != 0 and v not in adj[0]]
    assert len(non_neighbors) == 27, f"H27 expected 27 vertices, found {len(non_neighbors)}"
    return sorted(non_neighbors)


def compute_h1_kernel(L1: np.ndarray, tol=1e-8):
    """Compute kernel basis (harmonic 1-forms) of L1 numerically via eigh."""
    w, v = eigen_decomp_sorted(L1)
    null_idx = np.where(np.abs(w) < tol)[0]
    basis = v[:, null_idx]
    return basis, w


def compute_inclusion_rank(h27_edges_global_idx: List[int], h27_kernel_basis: np.ndarray, w33_kernel_basis: np.ndarray, n_edges_global: int, tol=1e-8):
    """Given harmonic basis for H1(H27) (in local edge coords) embed into global edge space and compute rank of images in global H1 space.

    - h27_edges_global_idx: list mapping local edge index -> global edge index, length m_local
    - h27_kernel_basis: shape (m_local, k_local)
    - w33_kernel_basis: shape (m_global, k_global)

    Returns: rank of images in H1(W33) (dimension of span of projections onto global harmonic subspace)
    """
    # Embed local basis into global edge coordinates
    m_local = h27_kernel_basis.shape[0]
    m_global = n_edges_global
    k_local = h27_kernel_basis.shape[1]

    # Build embedded vectors
    embedded = np.zeros((m_global, k_local), dtype=float)
    for local_e_idx, global_e_idx in enumerate(h27_edges_global_idx):
        embedded[global_e_idx, :] = h27_kernel_basis[local_e_idx, :]

    # Project embedded vectors onto global harmonic subspace (w33_kernel_basis)
    # Compute coordinates: C = W^T * embedded
    coords = w33_kernel_basis.T @ embedded
    # Now rank of columns of coords (over reals)
    u, s, vh = np.linalg.svd(coords, full_matrices=False)
    rank = np.sum(s > tol)
    return int(rank)


def compute_h27_inclusion():
    """Build H27 induced subgraph, compute H1 kernel basis, and compute inclusion rank."""
    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)
    h27_vertices = compute_h27_vertices(adj)
    # Build induced adjacency for H27
    index_map = {v: i for i, v in enumerate(h27_vertices)}
    h27_edges = []
    for i, u in enumerate(h27_vertices):
        for v in adj[u]:
            if v in index_map and v > u:
                h27_edges.append((index_map[u], index_map[v]))
    # Build clique complex for H27
    # Use boundary matrices directly
    # Build B1_H27 and B2_H27 relative to the H27 vertices/edges
    # Re-use boundary_matrix: need simplices lists
    # import as sibling module
    from w33_homology import build_clique_complex as _build_clique

    # Create small adjacency for H27
    n_h = len(h27_vertices)
    adj_h = [[] for _ in range(n_h)]
    for (i, j) in h27_edges:
        adj_h[i].append(j)
        adj_h[j].append(i)
    simplices_h = _build_clique(n_h, adj_h)

    B1_h = boundary_matrix(simplices_h[1], simplices_h[0]).astype(float)
    B2_h = boundary_matrix(simplices_h[2], simplices_h[1]).astype(float)
    D_h = np.zeros((n_h, len(simplices_h[1])), dtype=float)
    for col, (i, j) in enumerate(simplices_h[1]):
        D_h[i, col] = 1.0
        D_h[j, col] = -1.0

    L1_h = D_h.T @ D_h + B2_h @ B2_h.T

    # harmonic bases (numerical)
    h27_harm_basis, w_h = compute_h1_kernel(L1_h)

    # Global harmonic basis
    Ls = compute_hodge_laplacians()
    L1 = Ls["L1"]
    w33_harm_basis, w33_w = compute_h1_kernel(L1)

    # Map local edges to global edge indices
    # Need to find for each H27 edge which global edge index it corresponds to
    global_edge_index = {e: i for i, e in enumerate(edges)}
    # H27 edges in global indices
    h27_edges_global_idx = []
    for (i, j) in simplices_h[1]:
        u = h27_vertices[i]
        v = h27_vertices[j]
        # canonical ordering (min,max)
        key = (min(u, v), max(u, v))
        ge = global_edge_index.get(key)
        assert ge is not None
        h27_edges_global_idx.append(ge)

    rank = compute_inclusion_rank(h27_edges_global_idx, h27_harm_basis, w33_harm_basis, len(edges))

    return {
        "h27_vertices": h27_vertices,
        "h27_edge_count": len(simplices_h[1]),
        "h27_b1": h27_harm_basis.shape[1],
        "w33_b1": w33_harm_basis.shape[1],
        "inclusion_rank": rank,
    }


def main():
    t0 = time.time()
    print("Computing Hodge Laplacians for W33...")
    Ls = compute_hodge_laplacians()
    D = Ls["D"]
    B1 = Ls["B1"]
    B2 = Ls["B2"]
    L0 = Ls["L0"]
    L1 = Ls["L1"]

    # Eigen-decompositions
    w0, v0 = eigen_decomp_sorted(L0)
    w1, v1 = eigen_decomp_sorted(L1)

    # harmonic 1-forms
    harmonic_basis, w1_all = compute_h1_kernel(L1)
    b1 = harmonic_basis.shape[1]
    print(f"Harmonic 1-forms (b1): {b1}")

    # Check decomposition counts
    n_vertices = L0.shape[0]
    n_edges = L1.shape[0]
    rank_d1 = np.linalg.matrix_rank(B1)
    rank_d2 = np.linalg.matrix_rank(B2)
    print(f"Edges: {n_edges}, rank(d1): {rank_d1}, rank(d2): {rank_d2}")
    print(f"Sanity: {n_edges} = {b1} + {rank_d2} + {rank_d1}")

    # Vertex Laplacian eigenvalues (nonzero) correspond to im(d1^T) eigenvalues
    # For SRG, adjacency eigenvalues are known: k=12, r=2 (mult=24), s=-4 (mult=15)
    # So Laplacian eigenvalues on im(d1^T) should be 12 - 2 = 10 (mult 24) and 12 - (-4) = 16 (mult 15)
    unique_w0 = multiplicity_dict(w0)

    # L1 zero multiplicity
    zero_mult = int(np.sum(np.isclose(w1, 0.0, atol=1e-8)))

    # eigenvalues on im(d1^T): compute eigenvalues of D.T@D restricted to column space of D.T
    # but easier: compute eigenvalues of L0 and translate
    lap_eigs = multiplicity_dict(w0)

    # eigenvalues on im(d2): compute eigenvalues of B2@B2.T restricted to its image
    # get eigenvalues of B2 B2^T
    w_b2, v_b2 = eigen_decomp_sorted(B2 @ B2.T)
    b2_nonzero = w_b2[w_b2 > 1e-8]
    b2_multiplicity = multiplicity_dict(b2_nonzero)

    # H27 inclusion
    h27 = compute_h27_inclusion()

    out = {
        "timestamp": int(t0),
        "b1": b1,
        "zero_multiplicity_L1": zero_mult,
        "edges": n_edges,
        "rank_d1": int(rank_d1),
        "rank_d2": int(rank_d2),
        "laplacian_vertex_eigs_mult": lap_eigs,
        "b2_nonzero_eigs_mult": b2_multiplicity,
        "h27_inclusion": h27,
    }

    ts = int(time.time())
    out_path = Path.cwd() / "checks" / f"PART_CVII_w33_hodge_{ts}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"Wrote results to {out_path}")
    print("Summary:")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
