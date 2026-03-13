"""
Phase CXXXVII -- Deep distance matrix spectral theory for W(3,3) = SRG(40,12,2,4).

The W(3,3) symplectic polar graph has 40 vertices, each with 12 neighbours.
Being a connected strongly regular graph with diameter 2, every non-adjacent
pair sits at distance exactly 2.  The distance matrix therefore satisfies

    D = A + 2 A_2 = 2J - 2I - A

where A_2 = J - I - A is the complement adjacency.  This identity turns the
distance spectrum into an exact function of the adjacency spectrum
{12^1, 2^24, -4^15}:

    D spectrum  =  {66^1, -4^24, 2^15}

This module contains 113 deterministic tests covering distance construction,
spectral decomposition, Wiener index, distance energy, Laplacian variants,
polynomial identities, cofactor / inverse properties, eccentricity, and
algebraic relations inside the Bose-Mesner algebra.
"""

import numpy as np
import pytest
from collections import deque
from scipy.linalg import eigvalsh, eigh


# ---------------------------------------------------------------------------
# W(3,3) builder (self-contained, no external imports)
# ---------------------------------------------------------------------------

def _build_w33():
    """Build the 40x40 adjacency matrix of W(3,3) = SRG(40,12,2,4)."""
    points = []
    for a in range(3):
        for b in range(3):
            for c in range(3):
                for d in range(3):
                    v = (a, b, c, d)
                    if v == (0, 0, 0, 0):
                        continue
                    first = next(x for x in v if x != 0)
                    inv = pow(first, -1, 3)
                    canon = tuple((x * inv) % 3 for x in v)
                    if canon not in points:
                        points.append(canon)
    n = 40
    A = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(i + 1, n):
            u, v = points[i], points[j]
            omega = (u[0]*v[1] - u[1]*v[0] + u[2]*v[3] - u[3]*v[2]) % 3
            if omega == 0:
                A[i, j] = A[j, i] = 1
    return A


# ---------------------------------------------------------------------------
# BFS distance utilities
# ---------------------------------------------------------------------------

def _bfs_distances(A, src):
    """Return shortest-path distance vector from *src* using BFS."""
    n = A.shape[0]
    dist = np.full(n, -1, dtype=int)
    dist[src] = 0
    queue = deque([src])
    while queue:
        u = queue.popleft()
        for v in range(n):
            if A[u, v] == 1 and dist[v] == -1:
                dist[v] = dist[u] + 1
                queue.append(v)
    return dist


def _distance_matrix(A):
    """Build the full distance matrix via BFS from every vertex."""
    n = A.shape[0]
    D = np.zeros((n, n), dtype=int)
    for i in range(n):
        D[i] = _bfs_distances(A, i)
    return D


# ---------------------------------------------------------------------------
# Module-scoped fixtures (computed once)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def adj():
    return _build_w33()


@pytest.fixture(scope="module")
def n():
    return 40


@pytest.fixture(scope="module")
def dist_mat(adj):
    return _distance_matrix(adj)


@pytest.fixture(scope="module")
def evals_D(dist_mat):
    return np.sort(eigvalsh(dist_mat.astype(float)))


@pytest.fixture(scope="module")
def eig_decomp_D(dist_mat):
    vals, vecs = eigh(dist_mat.astype(float))
    return vals, vecs


@pytest.fixture(scope="module")
def evals_A(adj):
    return np.sort(eigvalsh(adj.astype(float)))


@pytest.fixture(scope="module")
def transmission(dist_mat):
    return dist_mat.sum(axis=1)


# ===================================================================
# Topic 1 -- Distance matrix construction
# ===================================================================

class TestDistanceMatrixConstruction:
    """Basic structural properties of the BFS-computed distance matrix."""

    def test_shape(self, dist_mat, n):
        assert dist_mat.shape == (n, n)

    def test_diagonal_zero(self, dist_mat, n):
        for i in range(n):
            assert dist_mat[i, i] == 0

    def test_symmetric(self, dist_mat):
        assert np.array_equal(dist_mat, dist_mat.T)

    def test_nonnegative(self, dist_mat):
        assert np.all(dist_mat >= 0)

    def test_diameter_is_2(self, dist_mat):
        assert dist_mat.max() == 2

    def test_no_unreachable(self, dist_mat, n):
        """All off-diagonal entries are 1 or 2 (graph is connected)."""
        for i in range(n):
            for j in range(n):
                if i != j:
                    assert dist_mat[i, j] in (1, 2)

    def test_distance_1_equals_adjacency(self, dist_mat, adj, n):
        A1 = (dist_mat == 1).astype(int)
        assert np.array_equal(A1, adj)

    def test_distance_2_is_complement(self, dist_mat, adj, n):
        J = np.ones((n, n), dtype=int)
        I = np.eye(n, dtype=int)
        A2 = (dist_mat == 2).astype(int)
        assert np.array_equal(A2, J - I - adj)

    def test_each_vertex_has_12_dist1_neighbours(self, dist_mat, n):
        for i in range(n):
            assert np.sum(dist_mat[i] == 1) == 12

    def test_each_vertex_has_27_dist2_neighbours(self, dist_mat, n):
        for i in range(n):
            assert np.sum(dist_mat[i] == 2) == 27


# ===================================================================
# Topic 2 -- Distance matrix spectrum
# ===================================================================

class TestDistanceMatrixSpectrum:
    """D spectrum = {66^1, -4^24, 2^15}."""

    def test_largest_eigenvalue(self, evals_D):
        assert abs(evals_D[-1] - 66) < 1e-10

    def test_smallest_eigenvalue(self, evals_D):
        assert abs(evals_D[0] - (-4)) < 1e-10

    def test_eigenvalue_2_multiplicity(self, evals_D):
        count = np.sum(np.abs(evals_D - 2) < 1e-10)
        assert count == 15

    def test_eigenvalue_neg4_multiplicity(self, evals_D):
        count = np.sum(np.abs(evals_D - (-4)) < 1e-10)
        assert count == 24

    def test_eigenvalue_66_multiplicity(self, evals_D):
        count = np.sum(np.abs(evals_D - 66) < 1e-10)
        assert count == 1

    def test_total_multiplicity(self, evals_D, n):
        assert len(evals_D) == n

    def test_three_distinct_eigenvalues(self, evals_D):
        unique = set()
        for v in evals_D:
            matched = False
            for u in unique:
                if abs(v - u) < 1e-10:
                    matched = True
                    break
            if not matched:
                unique.add(v)
        assert len(unique) == 3

    def test_spectrum_from_adjacency_formula(self, evals_A, evals_D, n):
        """D = 2J - 2I - A  =>  d = 2n-2-a (Perron), d = -2-a (rest)."""
        assert abs(evals_D[-1] - (2 * n - 2 - evals_A[-1])) < 1e-10
        # eigenvalue 2 of A -> -2 - 2 = -4 of D
        # eigenvalue -4 of A -> -2 - (-4) = 2 of D
        idx_a2 = np.argmin(np.abs(evals_A - 2))
        assert abs((-2 - evals_A[idx_a2]) - (-4)) < 1e-10


# ===================================================================
# Topic 3 -- D = 2J - 2I - A identity
# ===================================================================

class TestDistanceIdentity:
    """Entry-by-entry and matrix-level verification of D = 2J - 2I - A."""

    def test_D_equals_2J_minus_2I_minus_A(self, dist_mat, adj, n):
        J = np.ones((n, n), dtype=int)
        I = np.eye(n, dtype=int)
        expected = 2 * J - 2 * I - adj
        assert np.array_equal(dist_mat, expected)

    def test_identity_entrywise_adjacent(self, dist_mat, adj, n):
        for i in range(n):
            for j in range(n):
                if adj[i, j] == 1:
                    assert dist_mat[i, j] == 1  # 2 - 0 - 1

    def test_identity_entrywise_nonadjacent(self, dist_mat, adj, n):
        for i in range(n):
            for j in range(n):
                if i != j and adj[i, j] == 0:
                    assert dist_mat[i, j] == 2  # 2 - 0 - 0

    def test_D_plus_A_equals_2J_minus_2I(self, dist_mat, adj, n):
        J = np.ones((n, n), dtype=int)
        I = np.eye(n, dtype=int)
        assert np.array_equal(dist_mat + adj, 2 * J - 2 * I)

    def test_D_minus_2J_plus_2I_plus_A_zero(self, dist_mat, adj, n):
        J = np.ones((n, n), dtype=int)
        I = np.eye(n, dtype=int)
        residual = dist_mat - 2 * J + 2 * I + adj
        assert np.array_equal(residual, np.zeros((n, n), dtype=int))


# ===================================================================
# Topic 4 -- Wiener index
# ===================================================================

class TestWienerIndex:
    """W = sum_{i<j} D[i,j] = 1320."""

    def test_wiener_index(self, dist_mat):
        W = np.sum(dist_mat) // 2
        assert W == 1320

    def test_wiener_from_formula(self):
        """W = 240*1 + 540*2 = 1320 (240 edges, 540 distance-2 pairs)."""
        assert 240 * 1 + 540 * 2 == 1320

    def test_wiener_per_vertex(self, dist_mat, n):
        for i in range(n):
            assert np.sum(dist_mat[i]) == 66

    def test_wiener_decomposition(self, dist_mat):
        num_dist1_pairs = np.sum(dist_mat == 1) // 2
        num_dist2_pairs = np.sum(dist_mat == 2) // 2
        W = num_dist1_pairs * 1 + num_dist2_pairs * 2
        assert W == 1320

    def test_number_of_edges(self, adj):
        assert np.sum(adj) // 2 == 240

    def test_number_of_dist2_pairs(self, dist_mat):
        assert np.sum(dist_mat == 2) // 2 == 540

    def test_wiener_from_transmission(self, transmission, n):
        """W = (1/2) sum_i t_i = 40*66/2 = 1320."""
        assert np.sum(transmission) // 2 == 1320


# ===================================================================
# Topic 5 -- Distance energy
# ===================================================================

class TestDistanceEnergy:
    """E_D = sum |d_i| = 66 + 24*4 + 15*2 = 192."""

    def test_distance_energy(self, evals_D):
        E_D = np.sum(np.abs(evals_D))
        assert abs(E_D - 192) < 1e-10

    def test_distance_energy_decomposition(self):
        assert 66 + 24 * 4 + 15 * 2 == 192

    def test_distance_energy_ratio(self, evals_D, n):
        """E_D / n = 192 / 40 = 4.8."""
        E_D = np.sum(np.abs(evals_D))
        assert abs(E_D / n - 4.8) < 1e-10

    def test_spectral_radius_equals_twice_wiener_over_n(self):
        """rho_D = 2W/n = 2*1320/40 = 66."""
        assert 2 * 1320 // 40 == 66

    def test_distance_energy_positive(self, evals_D):
        assert np.sum(np.abs(evals_D)) > 0


# ===================================================================
# Topic 6 -- Distance spectral radius
# ===================================================================

class TestDistanceSpectralRadius:
    """rho_D = 66 = 2(n-1) - k."""

    def test_spectral_radius_equals_66(self, evals_D):
        rho = max(np.abs(evals_D))
        assert abs(rho - 66) < 1e-10

    def test_spectral_radius_is_largest_eigenvalue(self, evals_D):
        assert abs(evals_D[-1] - 66) < 1e-10

    def test_spectral_radius_equals_transmission(self, transmission):
        assert abs(transmission[0] - 66) < 1e-10

    def test_spectral_radius_formula(self, n):
        """rho_D = 2(n-1) - k for diameter-2 SRG."""
        k = 12
        assert 2 * (n - 1) - k == 66

    def test_perron_eigenvector_is_constant(self, dist_mat, n):
        """Perron eigenvector (for eigenvalue 66) is proportional to 1."""
        vals, vecs = eigh(dist_mat.astype(float))
        idx = np.argmax(vals)
        perron = vecs[:, idx]
        assert np.max(np.abs(perron - perron[0])) < 1e-10


# ===================================================================
# Topic 7 -- Distance matrix powers
# ===================================================================

class TestDistanceMatrixPowers:
    """D^k spectrum = {66^k, (-4)^k, 2^k}."""

    def test_D_squared_spectrum(self, evals_D):
        evals_D2 = np.sort(evals_D ** 2)
        expected = np.array(sorted([66**2] + [16] * 24 + [4] * 15), dtype=float)
        assert np.allclose(evals_D2, expected, atol=1e-8)

    def test_D_cubed_spectrum(self, evals_D):
        evals_D3 = np.sort(evals_D ** 3)
        expected = np.array(sorted([66**3] + [(-4)**3] * 24 + [8] * 15), dtype=float)
        assert np.allclose(evals_D3, expected, atol=1e-4)

    def test_D_squared_trace(self, dist_mat):
        D2 = dist_mat @ dist_mat
        expected = 66**2 + 24 * 16 + 15 * 4  # 4356 + 384 + 60 = 4800
        assert abs(np.trace(D2) - expected) < 1e-8

    def test_D_squared_trace_from_entries(self, dist_mat):
        """tr(D^2) = sum D[i,j]^2 = 40*(12*1 + 27*4) = 4800."""
        assert np.sum(dist_mat ** 2) == 4800
        assert np.trace(dist_mat @ dist_mat) == 4800

    def test_D_cubed_trace(self, dist_mat):
        D2 = dist_mat @ dist_mat
        D3 = D2 @ dist_mat
        expected = 66**3 + 24 * ((-4)**3) + 15 * (2**3)
        assert abs(np.trace(D3) - expected) < 1e-6

    def test_D_fourth_power_trace(self, dist_mat):
        D2 = dist_mat @ dist_mat
        D4 = D2 @ D2
        expected = 66**4 + 24 * ((-4)**4) + 15 * (2**4)
        assert abs(np.trace(D4) - expected) < 1e-4

    def test_D_power_commutes_with_A(self, dist_mat, adj):
        D2 = dist_mat @ dist_mat
        assert np.allclose(D2 @ adj, adj @ D2, atol=1e-8)

    def test_D_squared_eigenvalues_direct(self, dist_mat):
        """Eigenvalues of D^2 computed directly match prediction."""
        D2 = dist_mat @ dist_mat
        evals_D2 = np.sort(eigvalsh(D2.astype(float)))
        expected = np.array(sorted([4356.0] + [16.0] * 24 + [4.0] * 15))
        assert np.allclose(evals_D2, expected, atol=1e-6)


# ===================================================================
# Topic 8 -- Distance Laplacian
# ===================================================================

class TestDistanceLaplacian:
    """D_L = diag(t) - D.  Spectrum {0^1, 70^24, 64^15}."""

    def test_distance_laplacian_diagonal(self, dist_mat, transmission, n):
        DL = np.diag(transmission) - dist_mat
        for i in range(n):
            assert DL[i, i] == transmission[i]

    def test_distance_laplacian_offdiag(self, dist_mat, transmission, n):
        DL = np.diag(transmission) - dist_mat
        for i in range(n):
            for j in range(n):
                if i != j:
                    assert DL[i, j] == -dist_mat[i, j]

    def test_DL_row_sums_zero(self, dist_mat, transmission):
        DL = np.diag(transmission) - dist_mat
        row_sums = DL.sum(axis=1)
        assert np.allclose(row_sums, 0, atol=1e-10)

    def test_DL_spectrum(self, dist_mat, transmission):
        DL = np.diag(transmission) - dist_mat.astype(float)
        evals = np.sort(eigvalsh(DL))
        expected = np.array(sorted([0.0] + [70.0] * 24 + [64.0] * 15))
        assert np.allclose(evals, expected, atol=1e-8)

    def test_DL_smallest_eigenvalue_zero(self, dist_mat, transmission):
        DL = np.diag(transmission) - dist_mat.astype(float)
        evals = np.sort(eigvalsh(DL))
        assert abs(evals[0]) < 1e-10

    def test_DL_zero_multiplicity_one(self, dist_mat, transmission):
        """Multiplicity of 0 = 1 (connected graph)."""
        DL = np.diag(transmission) - dist_mat.astype(float)
        evals = np.sort(eigvalsh(DL))
        assert np.sum(np.abs(evals) < 1e-10) == 1

    def test_DL_second_smallest(self, dist_mat, transmission):
        DL = np.diag(transmission) - dist_mat.astype(float)
        evals = np.sort(eigvalsh(DL))
        assert abs(evals[1] - 64) < 1e-8

    def test_DL_largest_eigenvalue(self, dist_mat, transmission):
        DL = np.diag(transmission) - dist_mat.astype(float)
        evals = np.sort(eigvalsh(DL))
        assert abs(evals[-1] - 70) < 1e-8

    def test_DL_trace(self, dist_mat, transmission):
        """tr(D_L) = 24*70 + 15*64 = 2640."""
        DL = np.diag(transmission) - dist_mat.astype(float)
        expected = 24 * 70 + 15 * 64  # 1680 + 960 = 2640
        assert abs(np.trace(DL) - expected) < 1e-8

    def test_DL_positive_semidefinite(self, dist_mat, transmission):
        DL = np.diag(transmission) - dist_mat.astype(float)
        evals = eigvalsh(DL)
        assert np.all(evals >= -1e-10)


# ===================================================================
# Topic 9 -- Distance signless Laplacian
# ===================================================================

class TestDistanceSignlessLaplacian:
    """D_Q = diag(t) + D.  Spectrum {132^1, 62^24, 68^15}."""

    def test_DQ_definition(self, dist_mat, transmission, n):
        DQ = np.diag(transmission) + dist_mat
        for i in range(n):
            assert DQ[i, i] == transmission[i]

    def test_DQ_spectrum(self, dist_mat, transmission):
        DQ = np.diag(transmission) + dist_mat.astype(float)
        evals = np.sort(eigvalsh(DQ))
        expected = np.array(sorted([132.0] + [62.0] * 24 + [68.0] * 15))
        assert np.allclose(evals, expected, atol=1e-8)

    def test_DQ_largest_eigenvalue(self, dist_mat, transmission):
        DQ = np.diag(transmission) + dist_mat.astype(float)
        evals = np.sort(eigvalsh(DQ))
        assert abs(evals[-1] - 132) < 1e-8

    def test_DQ_smallest_eigenvalue(self, dist_mat, transmission):
        DQ = np.diag(transmission) + dist_mat.astype(float)
        evals = np.sort(eigvalsh(DQ))
        assert abs(evals[0] - 62) < 1e-8

    def test_DQ_trace(self, dist_mat, transmission):
        """tr(D_Q) = 132 + 24*62 + 15*68 = 2640."""
        DQ = np.diag(transmission) + dist_mat.astype(float)
        expected = 132 + 24 * 62 + 15 * 68  # 132 + 1488 + 1020 = 2640
        assert abs(np.trace(DQ) - expected) < 1e-8

    def test_DQ_positive_definite(self, dist_mat, transmission):
        DQ = np.diag(transmission) + dist_mat.astype(float)
        evals = eigvalsh(DQ)
        assert np.all(evals > 0)

    def test_DQ_DL_sum(self, dist_mat, transmission, n):
        """D_Q + D_L = 2 diag(t)."""
        DQ = np.diag(transmission) + dist_mat
        DL = np.diag(transmission) - dist_mat
        assert np.array_equal(DQ + DL, 2 * np.diag(transmission))

    def test_DQ_DL_difference(self, dist_mat, transmission):
        """D_Q - D_L = 2 D."""
        DQ = np.diag(transmission) + dist_mat
        DL = np.diag(transmission) - dist_mat
        assert np.array_equal(DQ - DL, 2 * dist_mat)


# ===================================================================
# Topic 10 -- Transmission regularity
# ===================================================================

class TestTransmissionRegularity:
    """All transmissions = 66 (vertex-transitive => transmission-regular)."""

    def test_all_transmissions_equal(self, transmission, n):
        for i in range(n):
            assert transmission[i] == 66

    def test_transmission_value(self, transmission):
        assert transmission[0] == 66

    def test_transmission_sum(self, transmission, n):
        assert np.sum(transmission) == n * 66

    def test_transmission_equals_wiener_ratio(self, transmission, n):
        """t = 2W/n for transmission-regular graph."""
        assert transmission[0] == 2 * 1320 // n

    def test_transmission_from_degree(self, n):
        """t = k*1 + (n-1-k)*2 = 2(n-1) - k = 66."""
        k = 12
        assert 2 * (n - 1) - k == 66

    def test_intersection_number_c1(self, dist_mat, adj, n):
        """c_1 = 1 for any connected graph (unique predecessor)."""
        for src in range(min(5, n)):
            for v in range(n):
                if dist_mat[src, v] == 1:
                    count = sum(
                        1 for w in range(n)
                        if adj[v, w] == 1 and dist_mat[src, w] == 0
                    )
                    assert count == 1


# ===================================================================
# Topic 11 -- Distance polynomial and minimal polynomial
# ===================================================================

class TestDistancePolynomial:
    """Minimal polynomial of D: (x - 66)(x + 4)(x - 2) = x^3 - 64x^2 - 140x + 528."""

    def test_trace_D0(self, n):
        assert n == 40

    def test_trace_D1(self, dist_mat):
        assert np.trace(dist_mat) == 0

    def test_trace_D2(self, dist_mat):
        assert np.trace(dist_mat @ dist_mat) == 4800

    def test_minimal_polynomial(self, dist_mat, n):
        """D^3 - 64 D^2 - 140 D + 528 I = 0."""
        D = dist_mat.astype(float)
        I = np.eye(n)
        D2 = D @ D
        D3 = D2 @ D
        result = D3 - 64 * D2 - 140 * D + 528 * I
        assert np.allclose(result, 0, atol=1e-6)

    def test_minimal_polynomial_coefficient_expansion(self):
        """Verify (x-66)(x+4)(x-2) expands to x^3 - 64x^2 - 140x + 528."""
        p = np.convolve(np.convolve([1, -66], [1, 4]), [1, -2])
        assert list(p) == [1, -64, -140, 528]

    def test_cayley_hamilton(self, dist_mat, n):
        """D satisfies its characteristic polynomial (implied by min poly)."""
        D = dist_mat.astype(float)
        I = np.eye(n)
        D2 = D @ D
        D3 = D2 @ D
        assert np.allclose(D3 - 64 * D2 - 140 * D + 528 * I, 0, atol=1e-6)

    def test_no_degree_2_annihilator(self, dist_mat, n):
        """D does not satisfy any polynomial of degree 2."""
        D = dist_mat.astype(float)
        I = np.eye(n)
        result = D @ D - 62 * D - 264 * I
        assert not np.allclose(result, 0, atol=1e-6)

    def test_determinant(self, dist_mat):
        """det(D) = 66 * (-4)^24 * 2^15 = 66 * 2^63."""
        det_computed = np.linalg.det(dist_mat.astype(float))
        det_expected = 66.0 * (2.0 ** 63)
        assert abs(det_computed - det_expected) / abs(det_expected) < 1e-8


# ===================================================================
# Topic 12 -- Graham-Lovasz: inverse and cofactors
# ===================================================================

class TestGrahamLovasz:
    """D is invertible; inverse / cofactor properties."""

    def test_D_invertible(self, evals_D):
        assert np.all(np.abs(evals_D) > 0.5)

    def test_D_inverse_spectrum(self, dist_mat):
        """D^{-1} eigenvalues: {1/66, -1/4, 1/2}."""
        D_inv = np.linalg.inv(dist_mat.astype(float))
        evals_inv = np.sort(eigvalsh(D_inv))
        expected = np.array(sorted([1.0 / 66] + [-0.25] * 24 + [0.5] * 15))
        assert np.allclose(evals_inv, expected, atol=1e-10)

    def test_D_inv_times_D_identity(self, dist_mat, n):
        D = dist_mat.astype(float)
        D_inv = np.linalg.inv(D)
        assert np.allclose(D_inv @ D, np.eye(n), atol=1e-10)

    def test_sum_D_inverse_entries(self, dist_mat):
        """1^T D^{-1} 1 = 40/66 = 20/33."""
        D_inv = np.linalg.inv(dist_mat.astype(float))
        total = np.sum(D_inv)
        assert abs(total - 40.0 / 66.0) < 1e-10

    def test_D_inverse_row_sum(self, dist_mat, n):
        """D^{-1} 1 = (1/66) 1."""
        D_inv = np.linalg.inv(dist_mat.astype(float))
        row_sums = D_inv @ np.ones(n)
        expected = np.ones(n) / 66.0
        assert np.allclose(row_sums, expected, atol=1e-10)

    def test_cofactor_matrix_rank(self, dist_mat, n):
        """adj(D) = det(D) D^{-1} has rank 40."""
        D = dist_mat.astype(float)
        rank = np.linalg.matrix_rank(D)
        assert rank == n


# ===================================================================
# Topic 13 -- Eccentricity
# ===================================================================

class TestEccentricity:
    """All eccentricities = 2 => diameter = radius = 2, center = V."""

    def test_all_eccentricities_equal_2(self, dist_mat, n):
        for i in range(n):
            assert max(dist_mat[i, j] for j in range(n)) == 2

    def test_diameter_equals_2(self, dist_mat):
        assert dist_mat.max() == 2

    def test_radius_equals_2(self, dist_mat, n):
        eccs = [max(dist_mat[i]) for i in range(n)]
        assert min(eccs) == 2

    def test_center_is_all_vertices(self, dist_mat, n):
        eccs = [max(dist_mat[i]) for i in range(n)]
        radius = min(eccs)
        center = [i for i in range(n) if eccs[i] == radius]
        assert len(center) == n

    def test_periphery_is_all_vertices(self, dist_mat, n):
        eccs = [max(dist_mat[i]) for i in range(n)]
        diam = max(eccs)
        periphery = [i for i in range(n) if eccs[i] == diam]
        assert len(periphery) == n

    def test_diameter_equals_radius(self, dist_mat, n):
        eccs = [max(dist_mat[i]) for i in range(n)]
        assert max(eccs) == min(eccs)

    def test_self_centered(self, dist_mat, n):
        """Graph is self-centered (diam = rad)."""
        eccs = [max(dist_mat[i]) for i in range(n)]
        assert max(eccs) == min(eccs) == 2


# ===================================================================
# Topic 14 -- Eigenvector properties
# ===================================================================

class TestEigenvectorProperties:
    """Shared eigenspaces, orthogonality, spectral reconstruction."""

    def test_D_A_commute(self, dist_mat, adj):
        """D and A commute => shared eigenbasis."""
        D = dist_mat.astype(float)
        A = adj.astype(float)
        assert np.allclose(D @ A, A @ D, atol=1e-8)

    def test_eigenvector_orthogonality(self, eig_decomp_D):
        vals, vecs = eig_decomp_D
        assert np.allclose(vecs.T @ vecs, np.eye(len(vals)), atol=1e-10)

    def test_eigenvalue_66_eigenvector_constant(self, eig_decomp_D):
        vals, vecs = eig_decomp_D
        idx = np.argmax(vals)
        v = vecs[:, idx]
        assert np.std(np.abs(v)) < 1e-10

    def test_neg4_eigenvectors_orthogonal_to_ones(self, eig_decomp_D, n):
        vals, vecs = eig_decomp_D
        ones = np.ones(n) / np.sqrt(n)
        for i in range(len(vals)):
            if abs(vals[i] - (-4)) < 1e-10:
                assert abs(np.dot(vecs[:, i], ones)) < 1e-10

    def test_2_eigenvectors_orthogonal_to_ones(self, eig_decomp_D, n):
        vals, vecs = eig_decomp_D
        ones = np.ones(n) / np.sqrt(n)
        for i in range(len(vals)):
            if abs(vals[i] - 2) < 1e-10:
                assert abs(np.dot(vecs[:, i], ones)) < 1e-10

    def test_spectral_decomposition_reconstructs_D(self, eig_decomp_D, dist_mat):
        vals, vecs = eig_decomp_D
        D_reconstructed = vecs @ np.diag(vals) @ vecs.T
        assert np.allclose(D_reconstructed, dist_mat.astype(float), atol=1e-8)

    def test_projection_onto_66_space(self, eig_decomp_D, n):
        """Projection onto eigenvalue-66 eigenspace = (1/n) J."""
        vals, vecs = eig_decomp_D
        idx = np.argmax(vals)
        v = vecs[:, idx:idx + 1]
        P = v @ v.T
        J_n = np.ones((n, n)) / n
        assert np.allclose(P, J_n, atol=1e-10)


# ===================================================================
# Topic 15 -- Additional spectral properties
# ===================================================================

class TestAdditionalSpectral:
    """Rank, trace identities, Frobenius norm, resolvent, etc."""

    def test_D_rank(self, dist_mat):
        assert np.linalg.matrix_rank(dist_mat) == 40

    def test_sum_of_eigenvalues_zero(self, evals_D):
        """tr(D) = sum d_i = 0."""
        assert abs(np.sum(evals_D)) < 1e-10

    def test_sum_of_eigenvalues_squared(self, evals_D):
        """sum d_i^2 = 4800."""
        assert abs(np.sum(evals_D ** 2) - 4800) < 1e-8

    def test_sum_of_eigenvalues_cubed(self, evals_D):
        expected = 66**3 + 24 * ((-4)**3) + 15 * (2**3)
        assert abs(np.sum(evals_D ** 3) - expected) < 1e-4

    def test_frobenius_norm(self, dist_mat):
        """||D||_F = sqrt(4800)."""
        fro = np.linalg.norm(dist_mat.astype(float), 'fro')
        assert abs(fro - np.sqrt(4800)) < 1e-10

    def test_D_squared_entry_sum(self, dist_mat, n):
        """sum_{i,j} D^2[i,j] = 40 * 66^2 = 174240."""
        D2 = dist_mat @ dist_mat
        assert np.sum(D2) == 40 * 66 * 66

    def test_resolvent_at_z100(self, dist_mat, n):
        """(100 I - D)^{-1} eigenvalues: {1/34, 1/104, 1/98}."""
        D = dist_mat.astype(float)
        R = np.linalg.inv(100 * np.eye(n) - D)
        evals_R = np.sort(eigvalsh(R))
        expected = np.array(sorted([1.0 / 34] + [1.0 / 104] * 24 + [1.0 / 98] * 15))
        assert np.allclose(evals_R, expected, atol=1e-10)

    def test_distance_complement_spectrum(self, adj, n):
        """A_2 = J - I - A has spectrum {27^1, -3^24, 3^15}."""
        A2 = np.ones((n, n), dtype=int) - np.eye(n, dtype=int) - adj
        evals = np.sort(eigvalsh(A2.astype(float)))
        expected = np.array(sorted([27.0] + [-3.0] * 24 + [3.0] * 15))
        assert np.allclose(evals, expected, atol=1e-8)

    def test_average_distance(self, dist_mat, n):
        """Average distance = 2W/(n(n-1)) = 2640/1560 = 22/13."""
        total = np.sum(dist_mat)
        avg = total / (n * (n - 1))
        assert abs(avg - 22.0 / 13.0) < 1e-10


# ===================================================================
# Topic 16 -- Distance algebraic relations (Bose-Mesner algebra)
# ===================================================================

class TestDistanceAlgebraicRelations:
    """D as a polynomial in A; SRG recurrence; Bose-Mesner membership."""

    def test_D_as_polynomial_in_A(self, dist_mat, adj, n):
        """D = (A^2 - 12 I) / 2.  Proof: eigenvalue check gives 66, -4, 2."""
        A = adj.astype(float)
        I = np.eye(n)
        D_from_A = (A @ A - 12 * I) / 2.0
        assert np.allclose(D_from_A, dist_mat.astype(float), atol=1e-10)

    def test_J_as_polynomial_in_A(self, adj, n):
        """J = (A^2 + 2A - 8I) / 4  (from the SRG recurrence)."""
        A = adj.astype(float)
        I = np.eye(n)
        J = np.ones((n, n))
        J_from_A = (A @ A + 2 * A - 8 * I) / 4.0
        assert np.allclose(J_from_A, J, atol=1e-10)

    def test_srg_recurrence(self, adj, n):
        """A^2 = (k - mu) I + (lambda - mu) A + mu J = 8I - 2A + 4J."""
        A = adj.astype(float)
        I = np.eye(n)
        J = np.ones((n, n))
        A2 = A @ A
        expected = 8 * I - 2 * A + 4 * J
        assert np.allclose(A2, expected, atol=1e-10)

    def test_D_commutes_with_complement(self, dist_mat, adj, n):
        D = dist_mat.astype(float)
        A2 = np.ones((n, n)) - np.eye(n) - adj.astype(float)
        assert np.allclose(D @ A2, A2 @ D, atol=1e-8)

    def test_D_in_bose_mesner_algebra(self, dist_mat, adj, n):
        """D = A + 2 A_2 in the Bose-Mesner basis {I, A, A_2}."""
        A = adj.astype(float)
        I = np.eye(n)
        A2 = np.ones((n, n)) - I - A
        D_from_BM = A + 2 * A2
        assert np.allclose(D_from_BM, dist_mat.astype(float), atol=1e-10)
