import numpy as np

from scripts.w33_hodge import (
    compute_h1_kernel,
    compute_h27_inclusion,
    compute_hodge_laplacians,
)


def test_b1_and_decomposition():
    Ls = compute_hodge_laplacians()
    L1 = Ls["L1"]
    B1 = Ls["B1"]
    B2 = Ls["B2"]

    # harmonic basis
    basis, w1 = compute_h1_kernel(L1)
    b1 = basis.shape[1]
    assert b1 == 81, f"Expected b1=81, got {b1}"

    # ranks
    rank_d1 = np.linalg.matrix_rank(B1)
    rank_d2 = np.linalg.matrix_rank(B2)
    assert rank_d1 == 39
    assert rank_d2 == 120

    # decomposition sum
    n_edges = L1.shape[0]
    assert n_edges == (b1 + rank_d2 + rank_d1)


def test_vertex_laplacian_srg_relation():
    Ls = compute_hodge_laplacians()
    L0 = Ls["L0"]
    w0, _ = np.linalg.eigh(L0)
    # multiplicities of Laplacian eigenvalues (rounded)
    vals = [round(float(x), 8) for x in w0]
    unique, counts = np.unique(vals, return_counts=True)
    mapping = dict(zip(unique, counts))
    # expect eigenvalues {0:1, 10:24, 16:15}
    assert mapping.get(0.0, 0) == 1
    assert mapping.get(10.0, 0) == 24
    assert mapping.get(16.0, 0) == 15


def test_b2_eigenvalue_triangle_regular():
    Ls = compute_hodge_laplacians()
    B2 = Ls["B2"]
    T = B2 @ B2.T
    w, _ = np.linalg.eigh(T)
    nonzero = w[w > 1e-8]
    # all nonzero eigenvalues should be equal (triangle-regular behaviour)
    vals = np.unique(np.round(nonzero, 8))
    assert len(vals) == 1
    assert int(len(nonzero)) == 120
    assert abs(float(vals[0]) - 4.0) < 1e-8


def test_h27_inclusion_rank():
    res = compute_h27_inclusion()
    # Observed: H27 b1 = 46 and inclusion rank (image dimension) = 46
    assert res["h27_b1"] == 46
    assert res["inclusion_rank"] == 46
