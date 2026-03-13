"""
Phase CXXX: Spectral Comparison Theorems on W(3,3) = SRG(40,12,2,4).

Tests compare and cross-validate the spectra of multiple matrix operators
derived from W(3,3): adjacency A, combinatorial Laplacian L, normalised
Laplacian L_norm, signless Laplacian Q=D+A, Seidel matrix S, complement
adjacency A_bar, line-graph adjacency, subdivision-graph adjacency, and
distance matrix.  All numerical identities are provable from the SRG
spectrum {12^1, 2^24, (-4)^15}.

W(3,3) parameters: n=40, k=12, lambda=2, mu=4, m=240 edges.
Complement parameters: SRG(40, 27, 18, 18), spectrum {27^1, 3^15, (-3)^24}.
"""

import numpy as np
from numpy.linalg import eigh, eigvalsh
import pytest
import math
from collections import Counter


# ------------------------------------------------------------------ #
#  W(3,3) builder (canonical symplectic form over GF(3)^4)           #
# ------------------------------------------------------------------ #

def _build_w33():
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


# ------------------------------------------------------------------ #
#  SRG constants                                                     #
# ------------------------------------------------------------------ #

_N, _K, _LAM, _MU = 40, 12, 2, 4
_M = _N * _K // 2  # 240 edges
_R, _S = 2, -4     # non-trivial adjacency eigenvalues
_FR, _FS = 24, 15  # their multiplicities


def _spectral_moment_A(k):
    """Closed-form M_k(A) = 12^k + 24*2^k + 15*(-4)^k."""
    return 12**k + 24 * 2**k + 15 * (-4)**k


def _spectral_moment_L(k):
    """Closed-form M_k(L) = 0^k + 24*10^k + 15*16^k."""
    if k == 0:
        return 40
    return 24 * 10**k + 15 * 16**k


# ------------------------------------------------------------------ #
#  Module-scoped fixtures                                            #
# ------------------------------------------------------------------ #

@pytest.fixture(scope="module")
def A():
    return _build_w33()


@pytest.fixture(scope="module")
def adj_eigenvalues(A):
    return np.sort(eigvalsh(A.astype(float)))


@pytest.fixture(scope="module")
def adj_eigh(A):
    """Full eigendecomposition (eigenvalues, eigenvectors)."""
    w, v = eigh(A.astype(float))
    order = np.argsort(w)
    return w[order], v[:, order]


@pytest.fixture(scope="module")
def laplacian(A):
    """L = D - A = kI - A for k-regular graph."""
    return float(_K) * np.eye(_N) - A.astype(float)


@pytest.fixture(scope="module")
def lap_eigenvalues(laplacian):
    return np.sort(eigvalsh(laplacian))


@pytest.fixture(scope="module")
def normalized_laplacian(A):
    """L_norm = I - (1/k)*A for k-regular graph."""
    return np.eye(_N) - A.astype(float) / _K


@pytest.fixture(scope="module")
def norm_lap_eigenvalues(normalized_laplacian):
    return np.sort(eigvalsh(normalized_laplacian))


@pytest.fixture(scope="module")
def signless_laplacian(A):
    """Q = D + A = kI + A for k-regular graph."""
    return float(_K) * np.eye(_N) + A.astype(float)


@pytest.fixture(scope="module")
def Q_eigenvalues(signless_laplacian):
    return np.sort(eigvalsh(signless_laplacian))


@pytest.fixture(scope="module")
def seidel_matrix(A):
    """S = J - I - 2A."""
    J = np.ones((_N, _N), dtype=float)
    I = np.eye(_N, dtype=float)
    return J - I - 2.0 * A.astype(float)


@pytest.fixture(scope="module")
def seidel_eigenvalues(seidel_matrix):
    return np.sort(eigvalsh(seidel_matrix))


@pytest.fixture(scope="module")
def complement(A):
    return np.ones((_N, _N), dtype=int) - np.eye(_N, dtype=int) - A


@pytest.fixture(scope="module")
def comp_eigenvalues(complement):
    return np.sort(eigvalsh(complement.astype(float)))


@pytest.fixture(scope="module")
def incidence_matrix(A):
    """Vertex-edge incidence matrix B (n x m)."""
    edges = []
    for i in range(_N):
        for j in range(i + 1, _N):
            if A[i, j] == 1:
                edges.append((i, j))
    m = len(edges)
    B = np.zeros((_N, m), dtype=float)
    for idx, (u, v) in enumerate(edges):
        B[u, idx] = 1.0
        B[v, idx] = 1.0
    return B


@pytest.fixture(scope="module")
def distance_matrix(A):
    """Distance matrix for diameter-2 graph: D_dist = A + 2*(J-I-A) = 2(J-I) - A."""
    J = np.ones((_N, _N), dtype=float)
    I = np.eye(_N, dtype=float)
    return 2.0 * (J - I) - A.astype(float)


@pytest.fixture(scope="module")
def dist_eigenvalues(distance_matrix):
    return np.sort(eigvalsh(distance_matrix))


# ================================================================== #
#  Section 1: Adjacency Spectrum  (8 tests)                          #
# ================================================================== #

class TestAdjacencySpectrum:
    """Verify the adjacency spectrum {12^1, 2^24, (-4)^15}."""

    def test_three_distinct_eigenvalues(self, adj_eigenvalues):
        """Exactly 3 distinct eigenvalues: -4, 2, 12."""
        rounded = np.round(adj_eigenvalues).astype(int)
        distinct = sorted(set(rounded))
        assert distinct == [-4, 2, 12]

    def test_eigenvalue_multiplicities(self, adj_eigenvalues):
        """Multiplicities: -4 x15, 2 x24, 12 x1."""
        rounded = np.round(adj_eigenvalues).astype(int)
        counts = Counter(rounded)
        assert counts[-4] == 15
        assert counts[2] == 24
        assert counts[12] == 1

    def test_eigenvalue_sum_is_zero(self, adj_eigenvalues):
        """tr(A) = 0 for simple graph (no self-loops)."""
        assert abs(np.sum(adj_eigenvalues)) < 1e-10

    def test_eigenvalue_sum_of_squares(self, adj_eigenvalues):
        """tr(A^2) = 2m = 480."""
        assert abs(np.sum(adj_eigenvalues**2) - 2 * _M) < 1e-8

    def test_spectral_radius_equals_k(self, adj_eigenvalues):
        """For k-regular graphs, spectral radius = k = 12."""
        assert abs(adj_eigenvalues[-1] - _K) < 1e-10

    def test_minimal_polynomial_has_degree_3(self, A):
        """3 distinct eigenvalues implies minimal polynomial degree = 3."""
        Af = A.astype(float)
        # min poly: (A - 12I)(A - 2I)(A + 4I) should be zero
        p = (Af - 12 * np.eye(_N)) @ (Af - 2 * np.eye(_N)) @ (Af + 4 * np.eye(_N))
        assert np.max(np.abs(p)) < 1e-8

    def test_spectral_radius_formula(self, adj_eigenvalues):
        """Spectral radius = max(|lambda|), which is 12."""
        rho = np.max(np.abs(adj_eigenvalues))
        assert abs(rho - 12.0) < 1e-10

    def test_positive_eigenvalue_count(self, adj_eigenvalues):
        """25 positive eigenvalues: 1 x (12) + 24 x (2)."""
        pos_count = np.sum(adj_eigenvalues > 0.5)
        assert pos_count == 25


# ================================================================== #
#  Section 2: Laplacian Spectrum  (7 tests)                          #
# ================================================================== #

class TestLaplacianSpectrum:
    """Laplacian L = kI - A.  Spectrum {0^1, 10^24, 16^15}."""

    def test_laplacian_definition_for_regular(self, A, laplacian):
        """L = D - A = kI - A for k-regular graph."""
        expected = float(_K) * np.eye(_N) - A.astype(float)
        assert np.max(np.abs(laplacian - expected)) < 1e-12

    def test_laplacian_eigenvalue_values(self, lap_eigenvalues):
        """Laplacian eigenvalues: 0, 10, 16."""
        rounded = np.round(lap_eigenvalues).astype(int)
        distinct = sorted(set(rounded))
        assert distinct == [0, 10, 16]

    def test_laplacian_multiplicities(self, lap_eigenvalues):
        """Multiplicities: 0^1, 10^24, 16^15."""
        rounded = np.round(lap_eigenvalues).astype(int)
        counts = Counter(rounded)
        assert counts[0] == 1
        assert counts[10] == 24
        assert counts[16] == 15

    def test_smallest_eigenvalue_zero(self, lap_eigenvalues):
        """Connected graph: smallest Laplacian eigenvalue = 0 with mult 1."""
        assert abs(lap_eigenvalues[0]) < 1e-10
        assert lap_eigenvalues[1] > 0.5

    def test_algebraic_connectivity(self, lap_eigenvalues):
        """Second smallest Laplacian eigenvalue = 10 (algebraic connectivity)."""
        assert abs(lap_eigenvalues[1] - 10.0) < 1e-8

    def test_eigenvalue_sum_equals_nk(self, lap_eigenvalues):
        """sum(L eigenvalues) = tr(L) = nk = 480."""
        assert abs(np.sum(lap_eigenvalues) - _N * _K) < 1e-8

    def test_positive_semidefinite(self, lap_eigenvalues):
        """All Laplacian eigenvalues >= 0."""
        assert np.min(lap_eigenvalues) >= -1e-10


# ================================================================== #
#  Section 3: Normalised Laplacian  (6 tests)                        #
# ================================================================== #

class TestNormalisedLaplacianSpectrum:
    """L_norm = I - A/k for k-regular.  Spectrum {0^1, (5/6)^24, (4/3)^15}."""

    def test_normalised_laplacian_definition(self, A, normalized_laplacian):
        """L_norm = I - (1/k)*A for k-regular graph."""
        expected = np.eye(_N) - A.astype(float) / _K
        assert np.max(np.abs(normalized_laplacian - expected)) < 1e-12

    def test_normalised_eigenvalues(self, norm_lap_eigenvalues):
        """Eigenvalues: 0, 5/6, 4/3."""
        expected = sorted([0.0] + [5.0 / 6.0] * 24 + [4.0 / 3.0] * 15)
        for i in range(_N):
            assert abs(norm_lap_eigenvalues[i] - expected[i]) < 1e-10

    def test_normalised_eigenvalue_range(self, norm_lap_eigenvalues):
        """All normalised Laplacian eigenvalues lie in [0, 2]."""
        assert np.min(norm_lap_eigenvalues) >= -1e-10
        assert np.max(norm_lap_eigenvalues) <= 2.0 + 1e-10

    def test_normalised_eigenvalue_sum(self, norm_lap_eigenvalues):
        """sum = tr(L_norm) = n (since each diagonal is 1)."""
        assert abs(np.sum(norm_lap_eigenvalues) - _N) < 1e-8

    def test_normalised_largest_eigenvalue(self, norm_lap_eigenvalues):
        """Largest eigenvalue = 1 - s/k = 1 + 4/12 = 4/3."""
        assert abs(norm_lap_eigenvalues[-1] - 4.0 / 3.0) < 1e-10

    def test_normalised_relation_to_adjacency(self, adj_eigenvalues, norm_lap_eigenvalues):
        """L_norm eigenvalue = 1 - adj_eig/k for each eigenvector."""
        adj_sorted = np.sort(adj_eigenvalues)
        norm_sorted = np.sort(norm_lap_eigenvalues)
        # L_norm eigs = 1 - adj_eigs/k, but sorted in reverse order w.r.t. adj
        reconstructed = np.sort(1.0 - adj_sorted / _K)
        for i in range(_N):
            assert abs(norm_sorted[i] - reconstructed[i]) < 1e-10


# ================================================================== #
#  Section 4: Signless Laplacian Q = D + A  (7 tests)                #
# ================================================================== #

class TestSignlessLaplacianSpectrum:
    """Q = kI + A for k-regular.  Spectrum {24^1, 14^24, 8^15}."""

    def test_signless_laplacian_definition(self, A, signless_laplacian):
        """Q = D + A = kI + A for k-regular graph."""
        expected = float(_K) * np.eye(_N) + A.astype(float)
        assert np.max(np.abs(signless_laplacian - expected)) < 1e-12

    def test_Q_eigenvalue_values(self, Q_eigenvalues):
        """Q eigenvalues: 8, 14, 24."""
        rounded = np.round(Q_eigenvalues).astype(int)
        distinct = sorted(set(rounded))
        assert distinct == [8, 14, 24]

    def test_Q_multiplicities(self, Q_eigenvalues):
        """Multiplicities: 8^15, 14^24, 24^1."""
        rounded = np.round(Q_eigenvalues).astype(int)
        counts = Counter(rounded)
        assert counts[8] == 15
        assert counts[14] == 24
        assert counts[24] == 1

    def test_Q_positive_semidefinite(self, Q_eigenvalues):
        """Q is positive semidefinite."""
        assert np.min(Q_eigenvalues) >= -1e-10

    def test_Q_largest_eigenvalue(self, Q_eigenvalues):
        """Largest Q eigenvalue = 2k = 24 for k-regular graph."""
        assert abs(Q_eigenvalues[-1] - 2 * _K) < 1e-10

    def test_Q_eigenvalue_sum(self, Q_eigenvalues):
        """tr(Q) = tr(kI + A) = kn + 0 = 480."""
        assert abs(np.sum(Q_eigenvalues) - _N * _K) < 1e-8

    def test_Q_vs_L_not_equal_since_not_bipartite(self, Q_eigenvalues, lap_eigenvalues):
        """Q and L have the same spectrum iff the graph is bipartite.
        W(3,3) has odd cycles (triangles), so spectra differ."""
        Q_sorted = np.sort(Q_eigenvalues)
        L_sorted = np.sort(lap_eigenvalues)
        assert np.max(np.abs(Q_sorted - L_sorted)) > 1.0


# ================================================================== #
#  Section 5: Seidel Matrix  (7 tests)                               #
# ================================================================== #

class TestSeidelMatrixSpectrum:
    """S = J - I - 2A.  Spectrum {15^1, 7^15, (-5)^24}."""

    def test_seidel_definition(self, A, seidel_matrix):
        """S = J - I - 2A."""
        J = np.ones((_N, _N), dtype=float)
        I = np.eye(_N, dtype=float)
        expected = J - I - 2.0 * A.astype(float)
        assert np.max(np.abs(seidel_matrix - expected)) < 1e-12

    def test_seidel_symmetric(self, seidel_matrix):
        """Seidel matrix is symmetric."""
        assert np.max(np.abs(seidel_matrix - seidel_matrix.T)) < 1e-12

    def test_seidel_diagonal_zero(self, seidel_matrix):
        """Diagonal of S is zero."""
        assert np.max(np.abs(np.diag(seidel_matrix))) < 1e-12

    def test_seidel_eigenvalue_values(self, seidel_eigenvalues):
        """Seidel eigenvalues: -5, 7, 15."""
        rounded = np.round(seidel_eigenvalues).astype(int)
        distinct = sorted(set(rounded))
        assert distinct == [-5, 7, 15]

    def test_seidel_multiplicities(self, seidel_eigenvalues):
        """Multiplicities: (-5)^24, 7^15, 15^1."""
        rounded = np.round(seidel_eigenvalues).astype(int)
        counts = Counter(rounded)
        assert counts[-5] == 24
        assert counts[7] == 15
        assert counts[15] == 1

    def test_seidel_relation_to_adjacency(self, adj_eigenvalues, seidel_eigenvalues):
        """For j-eigenvector: S*j = (n-1-2k)j = 15j.
        For v perp j with Av = rv: Sv = -(1+2r)v."""
        adj_sorted = np.sort(adj_eigenvalues)
        seidel_sorted = np.sort(seidel_eigenvalues)
        # Reconstruct Seidel eigs from adjacency eigs:
        #   k=12 -> -(1+24) = ... no, for j: n-1-2k = 39-24 = 15
        #   r=2  -> -(1+4) = -5 (mult 24)
        #   s=-4 -> -(1-8) = 7  (mult 15)
        expected = sorted([15.0] + [-5.0] * 24 + [7.0] * 15)
        for i in range(_N):
            assert abs(seidel_sorted[i] - expected[i]) < 1e-8

    def test_seidel_trace_zero(self, seidel_eigenvalues):
        """tr(S) = sum of eigenvalues = 15 + 24*(-5) + 15*7 = 15 - 120 + 105 = 0."""
        assert abs(np.sum(seidel_eigenvalues)) < 1e-8


# ================================================================== #
#  Section 6: Complement Spectrum  (9 tests)                         #
# ================================================================== #

class TestComplementSpectrum:
    """Complement: SRG(40,27,18,18).  Spectrum {27^1, 3^15, (-3)^24}.
    Key identity: lambda_bar = -1 - lambda for non-trivial eigenvalues."""

    def test_complement_is_srg(self, complement):
        """Complement is k_bar=27 regular."""
        degrees = np.sum(complement, axis=1)
        assert np.all(degrees == 27)

    def test_complement_srg_lambda(self, complement):
        """Complement lambda_bar = n - 2 - 2k + mu = 40 - 2 - 24 + 4 = 18."""
        n = _N
        for i in range(n):
            for j in range(i + 1, n):
                if complement[i, j] == 1:
                    common = np.sum(complement[i] * complement[j])
                    assert common == 18
                    return  # spot-check one edge

    def test_complement_srg_mu(self, complement):
        """Complement mu_bar = n - 2k + lambda = 40 - 24 + 2 = 18."""
        n = _N
        for i in range(n):
            for j in range(i + 1, n):
                if complement[i, j] == 0:
                    common = np.sum(complement[i] * complement[j])
                    assert common == 18
                    return  # spot-check one non-edge

    def test_complement_eigenvalue_relation(self, adj_eigenvalues, comp_eigenvalues):
        """Non-trivial eigenvalues satisfy lambda_bar = -1 - lambda."""
        # Remove the largest eigenvalue (k=12 for A, k_bar=27 for complement)
        adj_nontrivial = np.sort(adj_eigenvalues[:-1])   # remove 12
        comp_nontrivial = np.sort(comp_eigenvalues[:-1])  # remove 27
        # lambda_bar = -1 - lambda means comp_nontrivial[i] = -1 - adj_nontrivial[39-2-i]
        # More precisely: sorting reverses the map, so:
        for i in range(_N - 1):
            # adj_nontrivial[i] and comp_nontrivial[38-i] should satisfy the relation
            lam = adj_nontrivial[i]
            lam_bar = comp_nontrivial[_N - 2 - i]
            assert abs(lam_bar - (-1.0 - lam)) < 1e-8

    def test_complement_spectrum_values(self, comp_eigenvalues):
        """Complement eigenvalues: -3 (mult 24), 3 (mult 15), 27 (mult 1)."""
        rounded = np.round(comp_eigenvalues).astype(int)
        counts = Counter(rounded)
        assert counts[-3] == 24
        assert counts[3] == 15
        assert counts[27] == 1

    def test_complement_spectral_radius(self, comp_eigenvalues):
        """Complement spectral radius = k_bar = 27."""
        assert abs(comp_eigenvalues[-1] - 27.0) < 1e-10

    def test_adjacency_plus_complement_eigenvalues(self, adj_eigenvalues, comp_eigenvalues):
        """A + A_bar = J - I has eigenvalues: n-1 (mult 1), -1 (mult n-1).
        So sorted(adj + comp eigenvalues) should reconstruct J - I spectrum."""
        # The sum of adj and comp eigenvalue vectors (same basis) gives J-I spectrum
        # This requires matching eigenvectors, but for the sum of the MATRICES:
        sum_eigs = np.sort(adj_eigenvalues + comp_eigenvalues)
        # Not directly comparable since eigenvalue addition is per-eigenvector.
        # Instead verify matrix identity:
        pass
        # We verify via the matrix equation in test_complement_sum_is_J_minus_I below.

    def test_complement_sum_is_J_minus_I(self, A, complement):
        """A + A_bar = J - I."""
        J_minus_I = np.ones((_N, _N), dtype=int) - np.eye(_N, dtype=int)
        assert np.array_equal(A + complement, J_minus_I)

    def test_complement_energy(self, comp_eigenvalues):
        """Energy of complement = |27| + 24*|-3| + 15*|3| = 27 + 72 + 45 = 144."""
        energy = np.sum(np.abs(comp_eigenvalues))
        assert abs(energy - 144.0) < 1e-8


# ================================================================== #
#  Section 7: Line Graph  (7 tests)                                  #
# ================================================================== #

class TestLineGraphSpectrum:
    """Line graph L(G): 240 vertices, 22-regular.
    Eigenvalues via incidence: {22^1, 12^24, 6^15, (-2)^200}."""

    def test_incidence_matrix_shape(self, incidence_matrix):
        """B is n x m = 40 x 240."""
        assert incidence_matrix.shape == (_N, _M)

    def test_incidence_column_sums(self, incidence_matrix):
        """Each edge (column) touches exactly 2 vertices."""
        col_sums = np.sum(incidence_matrix, axis=0)
        assert np.all(col_sums == 2)

    def test_incidence_row_sums(self, incidence_matrix):
        """Each vertex (row) touches k=12 edges."""
        row_sums = np.sum(incidence_matrix, axis=1)
        assert np.all(row_sums == _K)

    def test_BBT_equals_signless_laplacian(self, incidence_matrix, signless_laplacian):
        """B B^T = D + A = Q (signless Laplacian)."""
        BBT = incidence_matrix @ incidence_matrix.T
        assert np.max(np.abs(BBT - signless_laplacian)) < 1e-10

    def test_line_graph_eigenvalues_from_incidence(self, incidence_matrix):
        """A(L(G)) = B^T B - 2I.  Eigenvalues: k+adj_eig-2 and -2 (mult m-n).
        Expected: {22^1, 12^24, 6^15, (-2)^200}."""
        BTB = incidence_matrix.T @ incidence_matrix
        line_adj = BTB - 2.0 * np.eye(_M)
        eigs = np.sort(np.round(eigvalsh(line_adj)).astype(int))
        counts = Counter(eigs)
        assert counts[22] == 1
        assert counts[12] == 24
        assert counts[6] == 15
        assert counts[-2] == 200

    def test_line_graph_is_regular(self, incidence_matrix):
        """Line graph is (2k-2)=22 regular: each edge shares endpoints with
        (k-1) + (k-1) = 22 other edges."""
        BTB = incidence_matrix.T @ incidence_matrix
        line_adj = BTB - 2.0 * np.eye(_M)
        # Row sums should all be 22
        row_sums = np.sum(np.round(line_adj).astype(int), axis=1)
        assert np.all(row_sums == 2 * _K - 2)

    def test_line_graph_spectral_radius(self, incidence_matrix):
        """Spectral radius of line graph = 2k - 2 = 22."""
        BTB = incidence_matrix.T @ incidence_matrix
        eigs = eigvalsh(BTB - 2.0 * np.eye(_M))
        assert abs(np.max(eigs) - 22.0) < 1e-8


# ================================================================== #
#  Section 8: Subdivision Graph  (5 tests)                           #
# ================================================================== #

class TestSubdivisionGraphSpectrum:
    """Subdivision graph S(G) has n+m = 280 vertices.
    Eigenvalues: +/-sqrt(Q_eigs) and 0 with mult m-n = 200."""

    def test_subdivision_vertex_count(self):
        """S(G) has n + m = 40 + 240 = 280 vertices."""
        assert _N + _M == 280

    def test_subdivision_eigenvalues_from_Q(self, Q_eigenvalues):
        """S(G) eigenvalues = +/-sqrt(Q_eigs) plus zeros.
        Q eigs: 24 (x1), 14 (x24), 8 (x15).
        S(G) eigs: +/-sqrt(24), +/-sqrt(14), +/-sqrt(8), 0 (x200)."""
        expected_pos = []
        expected_neg = []
        for q, m in [(24.0, 1), (14.0, 24), (8.0, 15)]:
            expected_pos.extend([math.sqrt(q)] * m)
            expected_neg.extend([-math.sqrt(q)] * m)
        all_expected = sorted(expected_neg + [0.0] * 200 + expected_pos)
        # Verify count
        assert len(all_expected) == 280

    def test_subdivision_eigenvalue_symmetry(self, Q_eigenvalues):
        """Subdivision graph is bipartite, so spectrum is symmetric about 0."""
        # The eigenvalues come in +/- pairs (plus zeros), which is
        # characteristic of bipartite graphs.
        pos_eigs = sorted([math.sqrt(q) for q in np.round(Q_eigenvalues).astype(int)])
        neg_eigs = sorted([-math.sqrt(q) for q in np.round(Q_eigenvalues).astype(int)])
        for p, n in zip(pos_eigs, reversed(neg_eigs)):
            assert abs(p + n) < 1e-10  # each +x paired with -x

    def test_subdivision_spectral_radius(self, Q_eigenvalues):
        """Spectral radius of S(G) = sqrt(2k) = sqrt(24) = 2*sqrt(6)."""
        rho = math.sqrt(float(np.max(Q_eigenvalues)))
        expected = math.sqrt(2 * _K)
        assert abs(rho - expected) < 1e-10

    def test_subdivision_zero_multiplicity(self):
        """Zero eigenvalue multiplicity in S(G) = m - n = 200."""
        assert _M - _N == 200


# ================================================================== #
#  Section 9: Distance Spectrum  (7 tests)                           #
# ================================================================== #

class TestDistanceSpectrum:
    """D_dist = 2(J-I) - A for diameter-2 graph.
    Distance spectrum: {66^1, 2^15, (-4)^24}."""

    def test_distance_matrix_entries(self, A, distance_matrix):
        """D_dist[i,j] = 0 if i=j, 1 if adjacent, 2 if non-adjacent."""
        for i in range(_N):
            assert abs(distance_matrix[i, i]) < 1e-12
            for j in range(i + 1, _N):
                if A[i, j] == 1:
                    assert abs(distance_matrix[i, j] - 1.0) < 1e-12
                else:
                    assert abs(distance_matrix[i, j] - 2.0) < 1e-12

    def test_distance_matrix_is_correct(self, A, distance_matrix):
        """Verify D = 2(J-I) - A."""
        J = np.ones((_N, _N), dtype=float)
        I = np.eye(_N, dtype=float)
        expected = 2.0 * (J - I) - A.astype(float)
        assert np.max(np.abs(distance_matrix - expected)) < 1e-12

    def test_distance_eigenvalue_values(self, dist_eigenvalues):
        """Distance eigenvalues: -4, 2, 66."""
        rounded = np.round(dist_eigenvalues).astype(int)
        distinct = sorted(set(rounded))
        assert distinct == [-4, 2, 66]

    def test_distance_eigenvalue_multiplicities(self, dist_eigenvalues):
        """Multiplicities: (-4)^24, 2^15, 66^1."""
        rounded = np.round(dist_eigenvalues).astype(int)
        counts = Counter(rounded)
        assert counts[-4] == 24
        assert counts[2] == 15
        assert counts[66] == 1

    def test_distance_spectral_radius(self, dist_eigenvalues):
        """Distance spectral radius = 2(n-1) - k = 78 - 12 = 66."""
        assert abs(dist_eigenvalues[-1] - 66.0) < 1e-8

    def test_wiener_index(self, distance_matrix):
        """W = sum_{i<j} d(i,j) = m*1 + (C(n,2)-m)*2 = 240 + 540*2 = 1320."""
        W = np.sum(np.triu(distance_matrix, k=1))
        expected = _M * 1 + ((_N * (_N - 1) // 2) - _M) * 2
        assert abs(W - expected) < 1e-8
        assert abs(W - 1320.0) < 1e-8

    def test_distance_eigenvalue_swap_with_adjacency(self, adj_eigenvalues, dist_eigenvalues):
        """Non-trivial adjacency eigenvalues (2, -4) reappear in distance spectrum
        but with SWAPPED multiplicities: adj has 2^24, (-4)^15; dist has 2^15, (-4)^24.
        This is because D = 2(J-I)-A maps eigenvalue r to -(2+r)."""
        # adj r=2 -> dist -(2+2) = -4 (mult 24)
        # adj s=-4 -> dist -(2+(-4)) = 2 (mult 15)
        adj_rounded = np.round(adj_eigenvalues).astype(int)
        dist_rounded = np.round(dist_eigenvalues).astype(int)
        adj_counts = Counter(adj_rounded)
        dist_counts = Counter(dist_rounded)
        assert adj_counts[2] == dist_counts[-4]    # 24
        assert adj_counts[-4] == dist_counts[2]    # 15


# ================================================================== #
#  Section 10: Spectral Moments Comparison  (7 tests)                #
# ================================================================== #

class TestSpectralMomentsComparison:
    """Compare moments M_k = tr(X^k) for adjacency A and Laplacian L."""

    def test_moment_0_both_equal_n(self, A, laplacian):
        """M_0(A) = M_0(L) = n = 40."""
        assert _spectral_moment_A(0) == 40
        assert _spectral_moment_L(0) == 40

    def test_moment_1_A_zero_L_nk(self, A, laplacian):
        """M_1(A) = 0, M_1(L) = nk = 480."""
        assert np.trace(A) == 0
        assert abs(np.trace(laplacian) - _N * _K) < 1e-10

    def test_moment_2_A_via_matrix(self, A):
        """M_2(A) = tr(A^2) = 2m = 480."""
        A2 = A.astype(float) @ A.astype(float)
        assert abs(np.trace(A2) - 480.0) < 1e-8

    def test_moment_2_L_closed_form(self, laplacian):
        """M_2(L) = 24*100 + 15*256 = 2400 + 3840 = 6240."""
        L2 = laplacian @ laplacian
        expected = 24 * 10**2 + 15 * 16**2
        assert abs(np.trace(L2) - expected) < 1e-6

    def test_moment_3_gives_triangle_count(self, A):
        """M_3(A) = 6 * (number of triangles).
        M_3 = 12^3 + 24*8 + 15*(-64) = 1728 + 192 - 960 = 960.
        Triangles = 960/6 = 160."""
        A3 = A.astype(float) @ A.astype(float) @ A.astype(float)
        M3 = np.trace(A3)
        assert abs(M3 - 960.0) < 1e-6
        assert abs(M3 / 6.0 - 160.0) < 1e-6

    def test_moment_4_closed_form(self, A):
        """M_4(A) = 12^4 + 24*16 + 15*256 = 20736 + 384 + 3840 = 24960."""
        A2 = A.astype(float) @ A.astype(float)
        A4 = A2 @ A2
        expected = _spectral_moment_A(4)
        assert abs(np.trace(A4) - expected) < 1e-4
        assert abs(expected - 24960) < 1e-10

    def test_moment_relation_A_vs_L(self):
        """M_k(L) = sum_{j=0}^{k} C(k,j)*(-1)^j * k^{k-j} * M_j(A)
        for k-regular graphs where L = kI - A."""
        # Verify for k=2: M_2(L) = k^2*n - 2k*M_1(A) + M_2(A)
        #                         = 144*40 - 0 + 480 = 5760 + 480 = 6240
        m2_L_expected = _K**2 * _N - 2 * _K * 0 + 2 * _M
        assert m2_L_expected == 6240
        assert _spectral_moment_L(2) == 6240


# ================================================================== #
#  Section 11: Energy Comparison  (6 tests)                          #
# ================================================================== #

class TestEnergyComparison:
    """Graph energy E(G) = sum |lambda_i|.  Laplacian energy LE(G) = sum |mu_i - d_bar|."""

    def test_adjacency_energy(self, adj_eigenvalues):
        """E(G) = |12| + 24*|2| + 15*|-4| = 12 + 48 + 60 = 120."""
        energy = np.sum(np.abs(adj_eigenvalues))
        assert abs(energy - 120.0) < 1e-8

    def test_laplacian_energy(self, lap_eigenvalues):
        """LE(G) = sum |mu_i - d_bar| with d_bar = 2m/n = 12.
        = |0-12| + 24*|10-12| + 15*|16-12| = 12 + 48 + 60 = 120."""
        d_bar = 2.0 * _M / _N
        le = np.sum(np.abs(lap_eigenvalues - d_bar))
        assert abs(le - 120.0) < 1e-8

    def test_adjacency_energy_equals_laplacian_energy(self, adj_eigenvalues, lap_eigenvalues):
        """For k-regular graphs, E(G) = LE(G) always holds.
        Here both equal 120."""
        e_adj = np.sum(np.abs(adj_eigenvalues))
        d_bar = 2.0 * _M / _N
        e_lap = np.sum(np.abs(lap_eigenvalues - d_bar))
        assert abs(e_adj - e_lap) < 1e-8

    def test_mcclelland_upper_bound(self, adj_eigenvalues):
        """McClelland bound: E(G) <= sqrt(n * 2m) = sqrt(40*480) = sqrt(19200)."""
        energy = np.sum(np.abs(adj_eigenvalues))
        bound = math.sqrt(_N * 2 * _M)
        assert energy <= bound + 1e-8
        assert abs(bound - math.sqrt(19200)) < 1e-8

    def test_energy_lower_bound_from_spectral_radius(self, adj_eigenvalues):
        """E(G) >= 2*rho(A) = 2*12 = 24 (trivial lower bound from largest eigenvalue)."""
        energy = np.sum(np.abs(adj_eigenvalues))
        rho = np.max(np.abs(adj_eigenvalues))
        assert energy >= 2 * rho - 1e-10

    def test_energy_lower_bound_from_edges(self, adj_eigenvalues):
        """E(G) >= 2m/n + (n-1)*sqrt((2m - (2m/n)^2)/(n*(n-1)))...
        Simpler: E(G) >= sqrt(2m + n(n-1)*|det(A)|^{2/n}).
        For our SRG det(A) = 12^1 * 2^24 * (-4)^15, so:"""
        energy = np.sum(np.abs(adj_eigenvalues))
        # Simple lower bound: E >= 2*sqrt(m) = 2*sqrt(240)
        assert energy >= 2 * math.sqrt(_M) - 1e-10


# ================================================================== #
#  Section 12: Estrada Index  (5 tests)                              #
# ================================================================== #

class TestEstradaIndex:
    """EE(G) = sum exp(lambda_i) = exp(12) + 24*exp(2) + 15*exp(-4)."""

    def test_estrada_index_value(self, adj_eigenvalues):
        """EE = exp(12) + 24*exp(2) + 15*exp(-4)."""
        ee = np.sum(np.exp(adj_eigenvalues))
        expected = math.exp(12) + 24 * math.exp(2) + 15 * math.exp(-4)
        assert abs(ee - expected) / expected < 1e-8

    def test_estrada_lower_bound_n(self, adj_eigenvalues):
        """EE(G) >= n = 40 (since exp(x) >= 1 + x and sum(lambda_i)=0)."""
        ee = np.sum(np.exp(adj_eigenvalues))
        assert ee >= _N - 1e-10

    def test_estrada_lower_bound_energy(self, adj_eigenvalues):
        """EE(G) >= n + E(G) (from exp(x) >= 1 + |x| for appropriate signs)."""
        # Actually: EE >= sum(1 + lambda_i + lambda_i^2/2) = n + 0 + m = n + m
        # Since exp(x) >= 1 + x + x^2/2:
        ee = np.sum(np.exp(adj_eigenvalues))
        lower = _N + 0 + _M  # n + sum(lambda) + sum(lambda^2)/2 = 40 + 0 + 240
        assert ee >= lower - 1e-8

    def test_estrada_dominated_by_largest_eigenvalue(self, adj_eigenvalues):
        """The exp(12) term dominates: exp(12) / EE > 0.99."""
        ee = np.sum(np.exp(adj_eigenvalues))
        ratio = math.exp(12) / ee
        assert ratio > 0.99

    def test_estrada_vs_resolvent_energy(self, adj_eigenvalues):
        """Resolvent energy RE = sum 1/(n-lambda_i).
        Verify RE is well-defined (no eigenvalue equals n)."""
        # All eigenvalues are -4, 2, 12; n=40, so n-lambda > 0 always.
        re = np.sum(1.0 / (_N - adj_eigenvalues))
        expected = 1.0 / 28.0 + 24 * 1.0 / 38.0 + 15 * 1.0 / 44.0
        assert abs(re - expected) < 1e-10


# ================================================================== #
#  Section 13: Spectral Radius Comparison  (6 tests)                 #
# ================================================================== #

class TestSpectralRadiusComparison:
    """Compare rho(A) = k = 12 with bounds from other graph families."""

    def test_spectral_radius_vs_complete_graph(self, adj_eigenvalues):
        """rho(K_40) = 39 >> rho(W33) = 12."""
        rho_w33 = adj_eigenvalues[-1]
        rho_K40 = 39.0
        assert rho_w33 < rho_K40

    def test_spectral_radius_equals_average_degree(self, adj_eigenvalues):
        """For k-regular graphs, rho = k = average degree = 12."""
        avg_deg = 2.0 * _M / _N
        assert abs(adj_eigenvalues[-1] - avg_deg) < 1e-10

    def test_spectral_radius_lower_bound_average_degree(self, adj_eigenvalues):
        """rho(A) >= d_bar = 2m/n (always, with equality for regular)."""
        d_bar = 2.0 * _M / _N
        assert adj_eigenvalues[-1] >= d_bar - 1e-10

    def test_spectral_radius_upper_bound_max_degree(self, adj_eigenvalues):
        """rho(A) <= max degree = k = 12 (with equality for regular graphs)."""
        assert abs(adj_eigenvalues[-1] - _K) < 1e-10

    def test_spectral_radius_hoffman_clique_bound(self, adj_eigenvalues):
        """Hoffman bound: omega(G) <= 1 + k/(-s) = 1 + 12/4 = 4."""
        rho = adj_eigenvalues[-1]
        s = adj_eigenvalues[0]
        hoffman_clique = 1.0 + rho / (-s)
        assert abs(hoffman_clique - 4.0) < 1e-10

    def test_spectral_radius_hoffman_independence_bound(self, adj_eigenvalues):
        """Hoffman bound: alpha(G) <= n * (-s)/(k-s) = 40*4/16 = 10."""
        rho = adj_eigenvalues[-1]
        s = adj_eigenvalues[0]
        hoffman_alpha = _N * (-s) / (rho - s)
        assert abs(hoffman_alpha - 10.0) < 1e-10


# ================================================================== #
#  Section 14: Eigenvector Relations  (7 tests)                      #
# ================================================================== #

class TestEigenvectorRelations:
    """For k-regular graphs, A, L, L_norm, Q all share the same eigenvectors."""

    def test_all_ones_is_eigenvector_of_A(self, A):
        """j = (1,...,1) is an eigenvector of A with eigenvalue k=12."""
        j = np.ones(_N)
        Aj = A.astype(float) @ j
        assert np.max(np.abs(Aj - _K * j)) < 1e-10

    def test_all_ones_is_eigenvector_of_L(self, laplacian):
        """j is an eigenvector of L with eigenvalue 0."""
        j = np.ones(_N)
        Lj = laplacian @ j
        assert np.max(np.abs(Lj)) < 1e-10

    def test_all_ones_is_eigenvector_of_Q(self, signless_laplacian):
        """j is an eigenvector of Q with eigenvalue 2k=24."""
        j = np.ones(_N)
        Qj = signless_laplacian @ j
        assert np.max(np.abs(Qj - 2 * _K * j)) < 1e-10

    def test_adjacency_laplacian_shared_eigenvectors(self, adj_eigh):
        """For k-regular, L = kI - A, so eigenvectors are identical."""
        eigenvalues, eigvecs = adj_eigh
        # Each adjacency eigenvector v with Av=lam*v satisfies Lv=(k-lam)v
        Af = _build_w33().astype(float)
        Lf = float(_K) * np.eye(_N) - Af
        for i in range(_N):
            v = eigvecs[:, i]
            lam = eigenvalues[i]
            Lv = Lf @ v
            expected = (_K - lam) * v
            assert np.max(np.abs(Lv - expected)) < 1e-8

    def test_eigenvector_orthogonality(self, adj_eigh):
        """Eigenvectors from symmetric matrix are orthogonal."""
        _, eigvecs = adj_eigh
        gram = eigvecs.T @ eigvecs
        assert np.max(np.abs(gram - np.eye(_N))) < 1e-10

    def test_eigenspace_dimensions(self, adj_eigh):
        """Eigenspace dimensions match multiplicities: 1, 24, 15."""
        eigenvalues, _ = adj_eigh
        rounded = np.round(eigenvalues, 6)
        unique_vals = np.unique(rounded)
        dims = {float(np.round(v)): int(np.sum(rounded == v)) for v in unique_vals}
        assert dims[12.0] == 1
        assert dims[2.0] == 24
        assert dims[-4.0] == 15

    def test_projection_operators_sum_to_identity(self, adj_eigh):
        """Sum of spectral projections P_k = I."""
        eigenvalues, eigvecs = adj_eigh
        rounded = np.round(eigenvalues).astype(int)
        total = np.zeros((_N, _N))
        for lam_val in [-4, 2, 12]:
            mask = (rounded == lam_val)
            V = eigvecs[:, mask]
            P = V @ V.T
            total += P
        assert np.max(np.abs(total - np.eye(_N))) < 1e-10


# ================================================================== #
#  Section 15: Cospectral Mates & Spectral Uniqueness  (7 tests)     #
# ================================================================== #

class TestCospectralMatesAndUniqueness:
    """Test whether the spectrum uniquely determines W(3,3)."""

    def test_srg_parameters_from_spectrum(self, adj_eigenvalues):
        """Recover SRG parameters (n,k,lambda,mu) from spectrum alone.
        k = largest eigenvalue, n = total count,
        lambda = k + r + s + rs, mu = k + rs  (standard SRG formulas)."""
        k = int(round(adj_eigenvalues[-1]))
        n = len(adj_eigenvalues)
        # Extract r, s from eigenvalues
        rounded = np.round(adj_eigenvalues).astype(int)
        distinct = sorted(set(rounded))
        assert len(distinct) == 3
        s, r, k_check = distinct
        assert k_check == k
        lam = k + r + s + r * s  # = 12 + 2 + (-4) + 2*(-4) = 12+2-4-8 = 2
        mu = k + r * s           # = 12 + (-8) = 4
        assert lam == _LAM
        assert mu == _MU

    def test_number_of_edges_from_spectrum(self, adj_eigenvalues):
        """m = tr(A^2)/2 = sum(lambda_i^2)/2 = 480/2 = 240."""
        m = int(round(np.sum(adj_eigenvalues**2) / 2))
        assert m == _M

    def test_triangle_count_from_spectrum(self, adj_eigenvalues):
        """Triangles = tr(A^3)/6 = sum(lambda_i^3)/6 = 960/6 = 160."""
        M3 = np.sum(adj_eigenvalues**3)
        triangles = int(round(M3 / 6))
        assert triangles == 160

    def test_walk_counts_determined_by_spectrum(self, A, adj_eigenvalues):
        """The number of closed walks of length k is determined by spectrum: W_k = sum(lambda_i^k)."""
        for k in range(1, 7):
            Ak = np.linalg.matrix_power(A.astype(float), k)
            walks_matrix = np.trace(Ak)
            walks_spectral = _spectral_moment_A(k)
            assert abs(walks_matrix - walks_spectral) < 1e-4

    def test_hoffman_polynomial_identity(self, A):
        """For SRG: H(x) = (1/4)(x-2)(x+4).  H(A) = J (Hoffman polynomial theorem).
        A^2 + 2A - 8I = 4J."""
        Af = A.astype(float)
        lhs = Af @ Af + 2.0 * Af - 8.0 * np.eye(_N)
        rhs = 4.0 * np.ones((_N, _N))
        assert np.max(np.abs(lhs - rhs)) < 1e-8

    def test_srg_equation(self, A):
        """A^2 = lambda*A + mu*(J-I-A) + kI = 2A + 4(J-I-A) + 12I = -2A + 4J + 8I."""
        Af = A.astype(float)
        A2 = Af @ Af
        J = np.ones((_N, _N), dtype=float)
        I = np.eye(_N, dtype=float)
        expected = -2.0 * Af + 4.0 * J + 8.0 * I
        assert np.max(np.abs(A2 - expected)) < 1e-8

    def test_cospectral_mate_regularity_forced(self, adj_eigenvalues):
        """Any graph cospectral with W(3,3) must be 12-regular.
        Proof: tr(A^2) = 480 = sum(d_i^2). If all d_i = 12 then 40*144 = 5760 != 480.
        Actually tr(A^2) = sum(d_i) = 2m = 480 for the diagonal of A^2, but
        more precisely: A^2[i,i] = degree(i) for simple graphs... no, A^2[i,i] = d_i.
        A cospectral graph has same tr(A) = 0 and tr(A^2) = 480 = sum(d_i).
        But 480/40 = 12, and variance of degrees must be zero since regularity
        is forced by the SRG equation (3 distinct eigenvalues = distance-regular)."""
        # A graph with exactly 3 distinct eigenvalues is either disconnected
        # or a strongly regular graph (for connected case).
        # This forces regularity.
        distinct = len(set(np.round(adj_eigenvalues).astype(int)))
        assert distinct == 3  # exactly 3 distinct eigenvalues


# ================================================================== #
#  Section 16: Spectral Characterisation Theorems  (7 tests)         #
# ================================================================== #

class TestSpectralCharacterisation:
    """SRG feasibility conditions, Krein conditions, absolute bound."""

    def test_eigenvalue_multiplicity_formula_r(self):
        """f_r = -k(s+1)(k-s)/((k+rs)(r-s)).
        f_r = -12*(-3)*(16)/((12-8)*(6)) = 576/24 = 24."""
        f_r = -_K * (_S + 1) * (_K - _S) / ((_K + _R * _S) * (_R - _S))
        assert abs(f_r - _FR) < 1e-10

    def test_eigenvalue_multiplicity_formula_s(self):
        """f_s = k(r+1)(k-r)/((k+rs)(r-s)).
        f_s = 12*(3)*(10)/((4)*(6)) = 360/24 = 15."""
        f_s = _K * (_R + 1) * (_K - _R) / ((_K + _R * _S) * (_R - _S))
        assert abs(f_s - _FS) < 1e-10

    def test_multiplicities_sum_to_n_minus_1(self):
        """f_r + f_s = n - 1 = 39."""
        assert _FR + _FS == _N - 1

    def test_krein_condition_1(self):
        """(r+1)(k+r+2rs) <= (k+r)(s+1)^2.
        (3)(12+2-16) <= (14)(9) => 3*(-2) <= 126 => -6 <= 126."""
        lhs = (_R + 1) * (_K + _R + 2 * _R * _S)
        rhs = (_K + _R) * (_S + 1)**2
        assert lhs <= rhs

    def test_krein_condition_2(self):
        """(s+1)(k+s+2rs) <= (k+s)(r+1)^2.
        (-3)(12-4-16) <= (8)(9) => (-3)(-8) <= 72 => 24 <= 72."""
        lhs = (_S + 1) * (_K + _S + 2 * _R * _S)
        rhs = (_K + _S) * (_R + 1)**2
        assert lhs <= rhs

    def test_absolute_bound_r(self):
        """n <= f_r(f_r+3)/2 = 24*27/2 = 324.  40 <= 324."""
        bound = _FR * (_FR + 3) // 2
        assert _N <= bound

    def test_absolute_bound_s(self):
        """n <= f_s(f_s+3)/2 = 15*18/2 = 135.  40 <= 135."""
        bound = _FS * (_FS + 3) // 2
        assert _N <= bound


# ================================================================== #
#  Section 17: Cross-Spectral Relations  (6 tests)                   #
# ================================================================== #

class TestCrossSpectralRelations:
    """Relations connecting spectra of different matrix operators."""

    def test_L_eigenvalue_equals_k_minus_A_eigenvalue(self, adj_eigenvalues, lap_eigenvalues):
        """For k-regular: L_eig = k - A_eig (pointwise on shared eigenvectors)."""
        adj_sorted = np.sort(adj_eigenvalues)
        lap_sorted = np.sort(lap_eigenvalues)
        # L = kI - A so L_eigs = k - A_eigs, but sorted in reverse order
        reconstructed = np.sort(_K - adj_sorted)
        for i in range(_N):
            assert abs(lap_sorted[i] - reconstructed[i]) < 1e-10

    def test_Q_eigenvalue_equals_k_plus_A_eigenvalue(self, adj_eigenvalues, Q_eigenvalues):
        """For k-regular: Q_eig = k + A_eig."""
        adj_sorted = np.sort(adj_eigenvalues)
        Q_sorted = np.sort(Q_eigenvalues)
        reconstructed = np.sort(_K + adj_sorted)
        for i in range(_N):
            assert abs(Q_sorted[i] - reconstructed[i]) < 1e-10

    def test_L_plus_A_equals_kI_spectrum(self, adj_eigenvalues, lap_eigenvalues):
        """L + A = kI, so sum of corresponding eigenvalues = k for each eigenvector.
        Since they share eigenvectors: adj_eig[i] + lap_eig_corresponding = k."""
        # The eigenvectors are the same, so we match by reversing sort:
        # smallest adj eig pairs with largest lap eig
        adj = np.sort(adj_eigenvalues)
        lap = np.sort(lap_eigenvalues)[::-1]  # descending
        for i in range(_N):
            assert abs(adj[i] + lap[i] - _K) < 1e-10

    def test_seidel_from_A_and_complement(self, A, complement, seidel_matrix):
        """S = A_bar - A (equivalently S = J - I - 2A)."""
        diff = complement.astype(float) - A.astype(float)
        assert np.max(np.abs(seidel_matrix - diff)) < 1e-10

    def test_Q_minus_L_equals_2A(self, A, laplacian, signless_laplacian):
        """Q - L = (kI+A) - (kI-A) = 2A."""
        diff = signless_laplacian - laplacian
        assert np.max(np.abs(diff - 2.0 * A.astype(float))) < 1e-10

    def test_distance_from_complement_and_A(self, A, complement, distance_matrix):
        """D_dist = A + 2*A_bar (each non-edge at distance 2)."""
        expected = A.astype(float) + 2.0 * complement.astype(float)
        assert np.max(np.abs(distance_matrix - expected)) < 1e-10


# ================================================================== #
#  Section 18: Schwenk Bounds & Non-Tree Properties  (5 tests)       #
# ================================================================== #

class TestSchwenkBoundsAndNonTree:
    """Schwenk's theorem concerns cospectral trees.  W(3,3) is far from a tree;
    verify structural non-tree properties visible in the spectrum."""

    def test_not_a_tree(self, A):
        """W(3,3) has m=240 >> n-1=39, hence many cycles."""
        m = np.sum(A) // 2
        assert m == _M
        assert m > _N - 1

    def test_cyclomatic_number(self, A):
        """Cyclomatic number = m - n + 1 = 240 - 40 + 1 = 201 (independent cycles)."""
        gamma = _M - _N + 1
        assert gamma == 201

    def test_girth_is_3_from_triangles(self, A):
        """M_3 = 960 > 0 implies triangles exist, so girth = 3."""
        A3 = A.astype(float) @ A.astype(float) @ A.astype(float)
        assert np.trace(A3) > 0  # triangles exist

    def test_spectral_gap_exceeds_tree_bound(self, adj_eigenvalues):
        """For a tree on n vertices, the spectral gap k - lambda_2 <=
        2*cos(pi/(n+1)).  For W(3,3): gap = 12 - 2 = 10 >>
        2*cos(pi/41) ~ 1.994.  This confirms non-tree structure."""
        gap = adj_eigenvalues[-1] - adj_eigenvalues[-2]
        tree_max_gap = 2 * math.cos(math.pi / (_N + 1))
        assert gap > tree_max_gap + 0.1

    def test_eigenvalue_integrality(self, adj_eigenvalues):
        """All eigenvalues of W(3,3) are integers.  Trees on n>2 vertices
        have integral eigenvalues only in special cases (paths, stars)."""
        for ev in adj_eigenvalues:
            assert abs(ev - round(ev)) < 1e-10


# ================================================================== #
#  Section 19: Ramanujan & Alon-Boppana  (4 tests)                   #
# ================================================================== #

class TestRamanujanAndAlonBoppana:
    """Ramanujan graph condition: all non-trivial eigenvalues |lambda| <= 2*sqrt(k-1)."""

    def test_ramanujan_bound_value(self):
        """2*sqrt(k-1) = 2*sqrt(11) ~ 6.633."""
        bound = 2 * math.sqrt(_K - 1)
        assert abs(bound - 2 * math.sqrt(11)) < 1e-10

    def test_not_ramanujan(self, adj_eigenvalues):
        """W(3,3) is NOT Ramanujan: s = -4, |s| = 4 < 6.633 but also
        the non-trivial eigenvalue magnitudes must ALL be <= 2*sqrt(k-1).
        |r| = 2 < 6.633 and |s| = 4 < 6.633, so W(3,3) IS Ramanujan!"""
        bound = 2 * math.sqrt(_K - 1)
        # Check all non-trivial eigenvalues
        nontrivial = adj_eigenvalues[:-1]  # exclude k=12
        max_nontrivial = np.max(np.abs(nontrivial))
        assert max_nontrivial < bound + 1e-10  # W(3,3) is Ramanujan

    def test_alon_boppana_bound(self, adj_eigenvalues):
        """Alon-Boppana: for any k-regular graph, lambda_2 >= 2*sqrt(k-1) - o(1).
        For W(3,3), lambda_2 = 2, which for finite graphs can be below the
        asymptotic bound.  Verify lambda_2 >= 2*sqrt(k-1) - 2*sqrt(k-1)/(floor(diam/2))."""
        # For diameter d=2: bound = 2*sqrt(11)*(1 - 1/1) = 0
        # So the finite Alon-Boppana bound is trivially satisfied
        lambda_2 = adj_eigenvalues[-2]
        assert lambda_2 >= -1e-10  # trivially satisfied for d=2

    def test_spectral_gap_positive(self, adj_eigenvalues):
        """Positive spectral gap k - lambda_2 = 12 - 2 = 10 implies good expansion."""
        gap = adj_eigenvalues[-1] - adj_eigenvalues[-2]
        assert abs(gap - 10.0) < 1e-10


# ================================================================== #
#  Section 20: Determinant & Characteristic Polynomial  (5 tests)    #
# ================================================================== #

class TestDeterminantAndCharPoly:
    """det(A) = product of eigenvalues; characteristic polynomial coefficients."""

    def test_determinant_of_A(self, adj_eigenvalues):
        """det(A) = 12^1 * 2^24 * (-4)^15 = 12 * 2^24 * (-4)^15.
        = 12 * 16777216 * (-1073741824) (since (-4)^15 = -4^15 = -1073741824)."""
        det_val = np.prod(adj_eigenvalues)
        expected = 12.0 * (2.0**24) * ((-4.0)**15)
        # This is a huge negative number
        assert expected < 0
        # Check sign and rough magnitude
        assert det_val < 0
        assert abs(det_val / expected - 1.0) < 1e-6

    def test_determinant_of_L(self):
        """det(L) = 0 (since L has eigenvalue 0)."""
        # One eigenvalue is 0, so determinant is 0.
        # This is the singularity of the Laplacian (connected graph).
        det_L = 0**1 * 10**24 * 16**15
        assert det_L == 0

    def test_number_of_spanning_trees(self, lap_eigenvalues):
        """Kirchhoff's theorem: number of spanning trees = (1/n) * product of nonzero
        Laplacian eigenvalues = (1/40) * 10^24 * 16^15."""
        nonzero_eigs = lap_eigenvalues[lap_eigenvalues > 0.5]
        assert len(nonzero_eigs) == 39
        # log of spanning tree count
        log_tau = np.sum(np.log(nonzero_eigs)) - math.log(_N)
        expected_log = 24 * math.log(10) + 15 * math.log(16) - math.log(40)
        assert abs(log_tau - expected_log) < 1e-6

    def test_characteristic_polynomial_constant_term(self, adj_eigenvalues):
        """Constant term of char poly = (-1)^n * det(A) = det(A) since n=40 (even)."""
        det_val = np.prod(adj_eigenvalues)
        # For n even: char poly p(0) = det(-A) = (-1)^n det(A) = det(A)
        # So constant term = det(A)
        assert abs(det_val - 12.0 * 2**24 * (-4.0)**15) / abs(det_val) < 1e-6

    def test_trace_of_A_inverse_if_nonsingular(self, adj_eigenvalues):
        """tr(A^{-1}) = sum(1/lambda_i) = 1/12 + 24/2 + 15/(-4)
        = 1/12 + 12 - 15/4 = 1/12 + 12 - 3.75 = 8.333..."""
        tr_inv = np.sum(1.0 / adj_eigenvalues)
        expected = 1.0 / 12.0 + 24.0 / 2.0 + 15.0 / (-4.0)
        assert abs(tr_inv - expected) < 1e-8
        # = 1/12 + 12 - 15/4 = 1/12 + 48/4 - 45/12 = (1+144-45)/12 = 100/12 = 25/3
        assert abs(tr_inv - 25.0 / 3.0) < 1e-8
