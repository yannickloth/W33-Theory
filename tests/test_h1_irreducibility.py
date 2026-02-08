import numpy as np
from scripts.analyze_h1_irreducibility import J_matrix, transvection_matrix, make_vertex_permutation, permutation_on_edges, permutation_matrix_from_perm, compute_commutant_dim
from scripts.w33_homology import build_w33
from scripts.w33_hodge import compute_hodge_laplacians, compute_h1_kernel


def test_h1_irreducible_commutant():
    J = J_matrix()
    # sample transvections
    vs = [np.array([1,0,0,0], dtype=int), np.array([0,1,0,0], dtype=int), np.array([0,0,1,0], dtype=int)]
    symp_mats = [transvection_matrix(u, J) for u in vs]

    n, vertices, adj, edges = build_w33()
    Ls = compute_hodge_laplacians()
    harmonic_basis, _ = compute_h1_kernel(Ls['L1'])

    reps = []
    for M in symp_mats:
        perm_v = make_vertex_permutation(M.tolist(), vertices)
        perm_e = permutation_on_edges(perm_v, edges)
        P = permutation_matrix_from_perm(perm_e)
        R = harmonic_basis.T @ P @ harmonic_basis
        reps.append(R)

    comm_dim = compute_commutant_dim(reps)
    # If the commutant is just scalars, dimension should be 1 (irreducible)
    assert comm_dim == 1, f"Expected commutant dim 1 (irreducible), got {comm_dim}"
