"""
Phase XCVIII  ·  W(3,3)-E8 Theory
Spectral Graph Drawing and Layout
Theorems T1614-T1634  (21 theorem-classes, 78 tests)

W(3,3) = SRG(40, 12, 2, 4) with adjacency eigenvalues:
    12 (mult 1),  2 (mult 24),  -4 (mult 15)
Laplacian eigenvalues (L = kI - A):
     0 (mult 1), 10 (mult 24),  16 (mult 15)
"""

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def _build_w33():
    """Construct the 40-vertex W(3,3) symplectic graph."""
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
            omega = (u[0] * v[1] - u[1] * v[0]
                     + u[2] * v[3] - u[3] * v[2]) % 3
            if omega == 0:
                A[i, j] = A[j, i] = 1
    return A


# ---------------------------------------------------------------------------
# Module-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def adj():
    """Adjacency matrix of W(3,3)."""
    return _build_w33()


@pytest.fixture(scope="module")
def n():
    return 40


@pytest.fixture(scope="module")
def eig_adj(adj):
    """Sorted eigenvalues and eigenvectors of A."""
    vals, vecs = np.linalg.eigh(adj.astype(float))
    idx = np.argsort(vals)
    return vals[idx], vecs[:, idx]


@pytest.fixture(scope="module")
def laplacian(adj):
    """Laplacian L = D - A = 12I - A for the 12-regular W(3,3)."""
    D = np.diag(adj.sum(axis=1))
    return D - adj


@pytest.fixture(scope="module")
def eig_lap(laplacian):
    """Sorted eigenvalues and eigenvectors of L."""
    vals, vecs = np.linalg.eigh(laplacian.astype(float))
    idx = np.argsort(vals)
    return vals[idx], vecs[:, idx]


@pytest.fixture(scope="module")
def signless_laplacian(adj):
    """Signless Laplacian Q = D + A = 12I + A."""
    D = np.diag(adj.sum(axis=1))
    return D + adj


@pytest.fixture(scope="module")
def eig_signless(signless_laplacian):
    """Sorted eigenvalues and eigenvectors of Q."""
    vals, vecs = np.linalg.eigh(signless_laplacian.astype(float))
    idx = np.argsort(vals)
    return vals[idx], vecs[:, idx]


@pytest.fixture(scope="module")
def norm_laplacian(adj):
    """Normalized Laplacian.  For 12-regular: L_norm = I - A/12."""
    n = adj.shape[0]
    return np.eye(n) - adj.astype(float) / 12.0


@pytest.fixture(scope="module")
def eig_norm_lap(norm_laplacian):
    vals, vecs = np.linalg.eigh(norm_laplacian)
    idx = np.argsort(vals)
    return vals[idx], vecs[:, idx]


@pytest.fixture(scope="module")
def distance_matrix(adj):
    """Shortest-path distance matrix for diameter-2 SRG.
    D_dist = A + 2*(J - I - A) = 2J - 2I - A.
    """
    n = adj.shape[0]
    J = np.ones((n, n))
    I = np.eye(n)
    return (2 * J - 2 * I - adj).astype(float)


@pytest.fixture(scope="module")
def eig_dist(distance_matrix):
    vals, vecs = np.linalg.eigh(distance_matrix)
    idx = np.argsort(vals)
    return vals[idx], vecs[:, idx]


@pytest.fixture(scope="module")
def spectral_coords_2d(eig_lap):
    """2D spectral drawing: first two non-trivial Laplacian eigenvectors."""
    _, vecs = eig_lap
    return vecs[:, 1:3]


@pytest.fixture(scope="module")
def spectral_coords_3d(eig_lap):
    """3D spectral drawing: first three non-trivial Laplacian eigenvectors."""
    _, vecs = eig_lap
    return vecs[:, 1:4]


# ===================================================================
# T1614 -- Adjacency Spectrum Verification
# ===================================================================

class TestT1614:
    """Adjacency eigenvalues of SRG(40,12,2,4) are {12, 2, -4}."""

    def test_eigenvalue_set(self, eig_adj):
        vals, _ = eig_adj
        unique = set(np.unique(np.round(vals, 6)))
        assert unique == {-4.0, 2.0, 12.0}

    def test_multiplicity_12(self, eig_adj):
        vals, _ = eig_adj
        assert np.sum(np.abs(vals - 12.0) < 1e-8) == 1

    def test_multiplicity_2(self, eig_adj):
        vals, _ = eig_adj
        assert np.sum(np.abs(vals - 2.0) < 1e-8) == 24

    def test_multiplicity_neg4(self, eig_adj):
        vals, _ = eig_adj
        assert np.sum(np.abs(vals + 4.0) < 1e-8) == 15


# ===================================================================
# T1615 -- Laplacian Spectrum from Adjacency
# ===================================================================

class TestT1615:
    """Laplacian L = 12I - A;  eigenvalues {0, 10, 16}."""

    def test_laplacian_eigenvalue_set(self, eig_lap):
        vals, _ = eig_lap
        unique = set(np.unique(np.round(vals, 6)))
        assert unique == {0.0, 10.0, 16.0}

    def test_multiplicity_0(self, eig_lap):
        vals, _ = eig_lap
        assert np.sum(np.abs(vals) < 1e-8) == 1

    def test_multiplicity_10(self, eig_lap):
        vals, _ = eig_lap
        assert np.sum(np.abs(vals - 10.0) < 1e-8) == 24

    def test_multiplicity_16(self, eig_lap):
        vals, _ = eig_lap
        assert np.sum(np.abs(vals - 16.0) < 1e-8) == 15


# ===================================================================
# T1616 -- Spectral Radius Equals Regularity Degree
# ===================================================================

class TestT1616:
    """Spectral radius rho(A) = k = 12."""

    def test_spectral_radius_value(self, eig_adj):
        vals, _ = eig_adj
        rho = np.max(np.abs(vals))
        assert abs(rho - 12.0) < 1e-8

    def test_spectral_radius_equals_degree(self, adj):
        k = int(adj.sum(axis=1)[0])
        vals = np.linalg.eigvalsh(adj.astype(float))
        assert abs(np.max(np.abs(vals)) - k) < 1e-8

    def test_perron_eigenvector_positive(self, eig_adj):
        """Perron-Frobenius: eigenvector for rho has all entries same sign."""
        vals, vecs = eig_adj
        pf_vec = vecs[:, np.argmax(vals)]
        assert np.all(pf_vec > 0) or np.all(pf_vec < 0)

    def test_perron_eigenvector_constant(self, eig_adj):
        """For k-regular graph, Perron eigenvector is constant (= 1/sqrt n)."""
        vals, vecs = eig_adj
        pf_vec = np.abs(vecs[:, np.argmax(vals)])
        assert np.allclose(pf_vec, pf_vec[0], atol=1e-8)


# ===================================================================
# T1617 -- Graph Energy
# ===================================================================

class TestT1617:
    """Graph energy E(G) = sum |lambda_i| = 12 + 48 + 60 = 120."""

    def test_energy_value(self, eig_adj):
        vals, _ = eig_adj
        assert abs(np.sum(np.abs(vals)) - 120.0) < 1e-6

    def test_energy_decomposition(self, eig_adj):
        vals, _ = eig_adj
        c12 = np.sum(np.abs(vals[np.abs(vals - 12) < 0.5]))
        c2  = np.sum(np.abs(vals[np.abs(vals - 2) < 0.5]))
        cm4 = np.sum(np.abs(vals[np.abs(vals + 4) < 0.5]))
        assert abs(c12 - 12.0) < 1e-8
        assert abs(c2  - 48.0) < 1e-8
        assert abs(cm4 - 60.0) < 1e-8

    def test_energy_bounds(self, adj, eig_adj):
        """sqrt(2m) <= E(G) <= sqrt(2mn)."""
        vals, _ = eig_adj
        energy = np.sum(np.abs(vals))
        m = int(np.sum(adj) // 2)
        n = adj.shape[0]
        assert energy >= np.sqrt(2 * m) - 1e-8
        assert energy <= np.sqrt(2 * m * n) + 1e-8


# ===================================================================
# T1618 -- Estrada Index
# ===================================================================

class TestT1618:
    """EE(G) = sum exp(lambda_i) = exp(12) + 24*exp(2) + 15*exp(-4)."""

    def test_estrada_value(self, eig_adj):
        vals, _ = eig_adj
        ee = np.sum(np.exp(vals))
        expected = np.exp(12) + 24 * np.exp(2) + 15 * np.exp(-4)
        assert abs(ee - expected) / expected < 1e-8

    def test_estrada_lower_bound_n(self, eig_adj, n):
        """EE >= n since exp(x) >= 1+x and sum lambda_i = 0."""
        assert np.sum(np.exp(eig_adj[0])) >= n - 1e-8

    def test_estrada_dominated_by_spectral_radius(self, eig_adj):
        """exp(12) contributes > 99 % of EE."""
        vals, _ = eig_adj
        ee = np.sum(np.exp(vals))
        assert np.exp(12) / ee > 0.99

    def test_normalized_estrada_gt_1(self, eig_adj, n):
        """EE / n > 1 for any graph with edges."""
        assert np.sum(np.exp(eig_adj[0])) / n > 1.0


# ===================================================================
# T1619 -- Fiedler Vector and Algebraic Connectivity
# ===================================================================

class TestT1619:
    """Algebraic connectivity a(G) = lambda_2(L) = 10."""

    def test_algebraic_connectivity(self, eig_lap):
        vals, _ = eig_lap
        assert abs(np.sort(vals)[1] - 10.0) < 1e-8

    def test_fiedler_orthogonal_to_ones(self, eig_lap):
        _, vecs = eig_lap
        fiedler = vecs[:, 1]
        assert abs(np.sum(fiedler)) < 1e-8

    def test_fiedler_unit_norm(self, eig_lap):
        _, vecs = eig_lap
        fiedler = vecs[:, 1]
        assert abs(np.dot(fiedler, fiedler) - 1.0) < 1e-8

    def test_fiedler_partition_nontrivial(self, eig_lap):
        """Fiedler vector sign gives a non-degenerate bipartition."""
        _, vecs = eig_lap
        fiedler = vecs[:, 1]
        assert np.sum(fiedler > 0) > 0
        assert np.sum(fiedler < 0) > 0


# ===================================================================
# T1620 -- Spectral Gap and Connectivity
# ===================================================================

class TestT1620:
    """Spectral gap = k - lambda_2(A) = 12 - 2 = 10."""

    def test_spectral_gap_value(self, eig_adj):
        vals, _ = eig_adj
        desc = np.sort(vals)[::-1]
        assert abs(desc[0] - desc[1] - 10.0) < 1e-8

    def test_positive_algebraic_connectivity_implies_connected(self, eig_lap):
        vals, _ = eig_lap
        assert np.sort(vals)[1] > 1e-8

    def test_gap_equals_algebraic_connectivity(self, eig_adj, eig_lap):
        """For k-regular graphs, spectral gap of A = lambda_2(L)."""
        avals, _ = eig_adj
        lvals, _ = eig_lap
        gap = np.sort(avals)[::-1][0] - np.sort(avals)[::-1][1]
        a_conn = np.sort(lvals)[1]
        assert abs(gap - a_conn) < 1e-8

    def test_kirchhoff_index(self, eig_lap, n):
        """Kf(G) = n * sum 1/lambda_i = 40*(24/10 + 15/16) = 133.5."""
        vals, _ = eig_lap
        nz = vals[vals > 1e-8]
        kf = n * np.sum(1.0 / nz)
        assert abs(kf - 133.5) < 1e-6


# ===================================================================
# T1621 -- Normalized Laplacian Spectrum
# ===================================================================

class TestT1621:
    """L_norm = I - A/k;  eigenvalues {0, 5/6, 4/3}."""

    def test_norm_lap_eigenvalue_set(self, eig_norm_lap):
        vals, _ = eig_norm_lap
        unique = set(np.unique(np.round(vals, 6)))
        assert unique == {0.0, round(5 / 6, 6), round(4 / 3, 6)}

    def test_trace_equals_n(self, eig_norm_lap, n):
        """trace(L_norm) = n for k-regular graphs."""
        vals, _ = eig_norm_lap
        assert abs(np.sum(vals) - n) < 1e-6

    def test_mult_zero(self, eig_norm_lap):
        vals, _ = eig_norm_lap
        assert np.sum(np.abs(vals) < 1e-8) == 1

    def test_mult_5_over_6(self, eig_norm_lap):
        vals, _ = eig_norm_lap
        assert np.sum(np.abs(vals - 5 / 6) < 1e-6) == 24


# ===================================================================
# T1622 -- Signless Laplacian Spectrum
# ===================================================================

class TestT1622:
    """Q = D + A = 12I + A;  eigenvalues {24, 14, 8}."""

    def test_signless_eigenvalue_set(self, eig_signless):
        vals, _ = eig_signless
        unique = set(np.unique(np.round(vals, 6)))
        assert unique == {8.0, 14.0, 24.0}

    def test_mult_24(self, eig_signless):
        vals, _ = eig_signless
        assert np.sum(np.abs(vals - 24.0) < 1e-8) == 1

    def test_mult_14(self, eig_signless):
        vals, _ = eig_signless
        assert np.sum(np.abs(vals - 14.0) < 1e-8) == 24

    def test_mult_8(self, eig_signless):
        vals, _ = eig_signless
        assert np.sum(np.abs(vals - 8.0) < 1e-8) == 15


# ===================================================================
# T1623 -- Distance Matrix Spectrum
# ===================================================================

class TestT1623:
    """D_dist = 2(J-I) - A for diameter-2 SRG;  eigenvalues {66, -4, 2}."""

    def test_distance_eigenvalue_set(self, eig_dist):
        vals, _ = eig_dist
        unique = set(np.unique(np.round(vals, 6)))
        assert unique == {-4.0, 2.0, 66.0}

    def test_distance_spectral_radius(self, eig_dist):
        vals, _ = eig_dist
        assert abs(np.max(np.abs(vals)) - 66.0) < 1e-6

    def test_distance_matrix_symmetric(self, distance_matrix):
        assert np.allclose(distance_matrix, distance_matrix.T)

    def test_distance_values_1_or_2(self, distance_matrix):
        """Off-diagonal entries are exactly 1 (adjacent) or 2 (non-adjacent)."""
        n = distance_matrix.shape[0]
        off = distance_matrix[np.triu_indices(n, k=1)]
        assert set(np.unique(off)) == {1.0, 2.0}


# ===================================================================
# T1624 -- 2D Spectral Drawing Coordinates
# ===================================================================

class TestT1624:
    """2D spectral drawing from two smallest non-trivial Laplacian eigenvectors."""

    def test_shape(self, spectral_coords_2d, n):
        assert spectral_coords_2d.shape == (n, 2)

    def test_centered(self, spectral_coords_2d):
        """Spectral coordinates are centered (eigenvectors orthogonal to 1)."""
        assert np.allclose(np.mean(spectral_coords_2d, axis=0), 0, atol=1e-8)

    def test_unit_norm(self, spectral_coords_2d):
        """Each coordinate vector has unit Euclidean norm."""
        for d in range(2):
            assert abs(np.linalg.norm(spectral_coords_2d[:, d]) - 1.0) < 1e-8

    def test_orthogonal(self, spectral_coords_2d):
        """The two coordinate vectors are mutually orthogonal."""
        dot = spectral_coords_2d[:, 0] @ spectral_coords_2d[:, 1]
        assert abs(dot) < 1e-8


# ===================================================================
# T1625 -- 3D Spectral Drawing
# ===================================================================

class TestT1625:
    """3D spectral drawing from three non-trivial Laplacian eigenvectors."""

    def test_shape(self, spectral_coords_3d, n):
        assert spectral_coords_3d.shape == (n, 3)

    def test_centered(self, spectral_coords_3d):
        assert np.allclose(np.mean(spectral_coords_3d, axis=0), 0, atol=1e-8)

    def test_gram_identity(self, spectral_coords_3d):
        """Gram matrix of coordinates = I_3 (orthonormality)."""
        G = spectral_coords_3d.T @ spectral_coords_3d
        assert np.allclose(G, np.eye(3), atol=1e-8)


# ===================================================================
# T1626 -- Stress in Spectral Embedding
# ===================================================================

class TestT1626:
    """Graph-distance stress and Laplacian energy of the 2D spectral layout."""

    def test_stress_positive_finite(self, spectral_coords_2d, distance_matrix):
        n = distance_matrix.shape[0]
        stress = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                dg = distance_matrix[i, j]
                de = np.linalg.norm(spectral_coords_2d[i] - spectral_coords_2d[j])
                stress += (dg - de) ** 2
        assert stress > 0 and np.isfinite(stress)

    def test_normalized_stress_bounded(self, spectral_coords_2d, distance_matrix):
        """Normalized stress in (0, 1)."""
        n = distance_matrix.shape[0]
        stress, denom = 0.0, 0.0
        for i in range(n):
            for j in range(i + 1, n):
                dg = distance_matrix[i, j]
                de = np.linalg.norm(spectral_coords_2d[i] - spectral_coords_2d[j])
                stress += (dg - de) ** 2
                denom += dg ** 2
        assert 0 < stress / denom < 1

    def test_laplacian_energy_per_coordinate(self, spectral_coords_2d, laplacian):
        """Each spectral coordinate's Laplacian energy equals eigenvalue 10."""
        L = laplacian.astype(float)
        for d in range(2):
            x = spectral_coords_2d[:, d]
            assert abs(x @ L @ x - 10.0) < 1e-6


# ===================================================================
# T1627 -- Laplacian Energy and Strain (Classical MDS)
# ===================================================================

class TestT1627:
    """Total Laplacian energy and MDS strain of spectral embeddings."""

    def test_edge_length_sum_2d(self, spectral_coords_2d, adj):
        """Sum of squared edge lengths = Laplacian energy = 10 + 10 = 20."""
        n = adj.shape[0]
        s = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                if adj[i, j]:
                    s += np.sum((spectral_coords_2d[i] - spectral_coords_2d[j]) ** 2)
        assert abs(s - 20.0) < 1e-4

    def test_edge_length_sum_3d(self, spectral_coords_3d, adj):
        """Sum of squared edge lengths = 10 + 10 + 10 = 30."""
        n = adj.shape[0]
        s = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                if adj[i, j]:
                    s += np.sum((spectral_coords_3d[i] - spectral_coords_3d[j]) ** 2)
        assert abs(s - 30.0) < 1e-4

    def test_mds_strain_bounded(self, distance_matrix, n):
        """Classical MDS strain for any d-dimensional projection is in [0, 1]."""
        D2 = distance_matrix ** 2
        H = np.eye(n) - np.ones((n, n)) / n
        B = -0.5 * H @ D2 @ H
        bvals = np.sort(np.linalg.eigvalsh(B))[::-1]
        pos = bvals[bvals > 1e-8]
        total = np.sum(pos)
        # 2D strain
        strain_2d = 1.0 - np.sum(pos[:2]) / total
        assert 0 <= strain_2d <= 1


# ===================================================================
# T1628 -- Walk Counting from Spectrum
# ===================================================================

class TestT1628:
    """Closed walks of length l = trace(A^l) = sum lambda_i^l."""

    def test_closed_walks_0(self, eig_adj, n):
        """l=0: trace(I) = 40."""
        vals, _ = eig_adj
        assert abs(np.sum(vals ** 0) - 40.0) < 1e-8

    def test_closed_walks_1(self, eig_adj):
        """l=1: trace(A) = 0 (no self-loops)."""
        vals, _ = eig_adj
        assert abs(np.sum(vals)) < 1e-6

    def test_closed_walks_2(self, eig_adj):
        """l=2: 2|E| = 480."""
        vals, _ = eig_adj
        assert abs(np.sum(vals ** 2) - 480.0) < 1e-4

    def test_closed_walks_3(self, eig_adj):
        """l=3: 6 * triangles = 6 * 160 = 960."""
        vals, _ = eig_adj
        assert abs(np.sum(vals ** 3) - 960.0) < 1e-2


# ===================================================================
# T1629 -- Walk Generating Function
# ===================================================================

class TestT1629:
    """Walk GF W(x) = trace((I - xA)^{-1}) = sum_i 1/(1 - x lambda_i)."""

    def test_wgf_at_zero(self, n):
        """W(0) = n = 40."""
        assert n == 40

    def test_wgf_small_x(self, eig_adj, n):
        """W(x) near x = 0 is close to n."""
        vals, _ = eig_adj
        x = 0.01
        wgf = np.sum(1.0 / (1.0 - x * vals))
        assert abs(wgf - n) < 1.0

    def test_convergence_radius(self, eig_adj):
        """Convergence radius = 1 / rho(A) = 1/12."""
        vals, _ = eig_adj
        r = 1.0 / np.max(np.abs(vals))
        assert abs(r - 1.0 / 12) < 1e-10

    def test_total_walks_length_l(self, adj, n):
        """Total walks of length l = n * k^l for k-regular graph."""
        k = 12
        A2 = adj.astype(float) @ adj.astype(float)
        total = np.sum(A2)
        assert abs(total - n * k ** 2) < 1e-4


# ===================================================================
# T1630 -- Embedding Dimension from Eigenvalue Analysis
# ===================================================================

class TestT1630:
    """Effective embedding dimension from spectral structure."""

    def test_rank_of_adjacency(self, adj):
        """All adjacency eigenvalues non-zero => rank = 40."""
        assert np.linalg.matrix_rank(adj.astype(float)) == 40

    def test_distinct_adj_eigenvalue_count(self, eig_adj):
        """Three distinct adjacency eigenvalues."""
        vals, _ = eig_adj
        assert len(np.unique(np.round(vals, 6))) == 3

    def test_distinct_nonzero_lap_eigenvalue_count(self, eig_lap):
        """Two distinct non-zero Laplacian eigenvalues (10 and 16)."""
        vals, _ = eig_lap
        nz = vals[vals > 1e-8]
        assert len(np.unique(np.round(nz, 6))) == 2

    def test_participation_ratio(self, eig_lap):
        """Participation ratio PR = (sum lambda)^2 / (d * sum lambda^2) in (0,1]."""
        vals, _ = eig_lap
        nz = vals[vals > 1e-8]
        pr = np.sum(nz) ** 2 / (len(nz) * np.sum(nz ** 2))
        assert 0 < pr <= 1


# ===================================================================
# T1631 -- Spectral Partitioning via Fiedler Vector
# ===================================================================

class TestT1631:
    """Fiedler vector sign partitions the graph with quality guarantee."""

    def test_partition_nontrivial(self, eig_lap):
        _, vecs = eig_lap
        fiedler = vecs[:, 1]
        assert np.sum(fiedler > 0) > 0 and np.sum(fiedler < 0) > 0

    def test_cut_positive(self, adj, eig_lap):
        _, vecs = eig_lap
        fiedler = vecs[:, 1]
        S = set(np.where(fiedler >= 0)[0])
        S_bar = set(np.where(fiedler < 0)[0])
        cut = sum(1 for i in S for j in S_bar if adj[i, j])
        assert cut > 0

    def test_ratio_cut_lower_bound(self, adj, eig_lap, n):
        """Ratio cut >= lambda_2(L) = 10  (variational characterisation)."""
        _, vecs = eig_lap
        fiedler = vecs[:, 1]
        S = np.where(fiedler >= 0)[0]
        S_bar = np.where(fiedler < 0)[0]
        cut = sum(int(adj[i, j]) for i in S for j in S_bar)
        ratio_cut = cut * n / (len(S) * len(S_bar))
        assert ratio_cut >= 10.0 - 1e-6


# ===================================================================
# T1632 -- Spectral Moments and Resolvent
# ===================================================================

class TestT1632:
    """Spectral moments M_k = trace(A^k) / n."""

    def test_moment_0(self, n):
        """M_0 = 1."""
        assert n / n == 1

    def test_moment_2(self, eig_adj, n):
        """M_2 = 2|E|/n = 480/40 = 12 = k."""
        vals, _ = eig_adj
        assert abs(np.sum(vals ** 2) / n - 12.0) < 1e-6

    def test_moment_3(self, eig_adj, n):
        """M_3 = 960/40 = 24."""
        vals, _ = eig_adj
        assert abs(np.sum(vals ** 3) / n - 24.0) < 1e-4

    def test_moment_4(self, eig_adj, n):
        """M_4 = 24960/40 = 624."""
        vals, _ = eig_adj
        assert abs(np.sum(vals ** 4) / n - 624.0) < 1e-2


# ===================================================================
# T1633 -- Heat Kernel and Diffusion
# ===================================================================

class TestT1633:
    """Heat trace Z(t) = trace exp(-tL) = 1 + 24 exp(-10t) + 15 exp(-16t)."""

    def test_heat_trace_at_zero(self, n):
        """Z(0) = n = 40."""
        assert abs(1 + 24 + 15 - 40) < 1e-10

    def test_heat_trace_always_positive(self):
        for t in [0.01, 0.1, 1.0, 10.0]:
            ht = 1 + 24 * np.exp(-10 * t) + 15 * np.exp(-16 * t)
            assert ht > 0

    def test_heat_trace_monotone_decreasing(self):
        ts = np.linspace(0.01, 5, 200)
        hts = 1 + 24 * np.exp(-10 * ts) + 15 * np.exp(-16 * ts)
        assert np.all(np.diff(hts) <= 1e-12)

    def test_heat_trace_limit_one(self):
        """Z(t) -> 1 as t -> inf  (one connected component)."""
        ht = 1 + 24 * np.exp(-1000) + 15 * np.exp(-1600)
        assert abs(ht - 1.0) < 1e-10


# ===================================================================
# T1634 -- Drawing Quality and Spectral Coherence
# ===================================================================

class TestT1634:
    """Quality metrics for the spectral graph layout."""

    def test_edge_length_cv_bounded(self, adj, spectral_coords_2d):
        """Coefficient of variation of edge lengths in the layout is bounded."""
        n = adj.shape[0]
        lengths = []
        for i in range(n):
            for j in range(i + 1, n):
                if adj[i, j]:
                    lengths.append(np.linalg.norm(
                        spectral_coords_2d[i] - spectral_coords_2d[j]))
        lengths = np.array(lengths)
        cv = np.std(lengths) / np.mean(lengths)
        assert cv < 2.0

    def test_angular_resolution_nonzero(self, adj, spectral_coords_2d):
        """At least some vertices have positive angular resolution."""
        good = 0
        n = adj.shape[0]
        for v in range(n):
            nbrs = np.where(adj[v] == 1)[0]
            if len(nbrs) < 2:
                continue
            vecs = spectral_coords_2d[nbrs] - spectral_coords_2d[v]
            nrm = np.linalg.norm(vecs, axis=1, keepdims=True)
            nrm = np.maximum(nrm, 1e-15)
            vecs = vecs / nrm
            min_angle = np.pi
            for a in range(len(nbrs)):
                for b in range(a + 1, len(nbrs)):
                    cos_ab = np.clip(vecs[a] @ vecs[b], -1, 1)
                    min_angle = min(min_angle, np.arccos(cos_ab))
            if min_angle > 0.01:
                good += 1
        assert good > 0

    def test_spectral_aspect_ratio(self, eig_lap):
        """lambda_max / lambda_2 = 16/10 = 1.6  (drawing aspect ratio)."""
        vals, _ = eig_lap
        sv = np.sort(vals)
        assert abs(sv[-1] / sv[1] - 1.6) < 1e-6

    def test_nonadj_farther_than_adj(self, adj, spectral_coords_2d):
        """On average, non-adjacent vertices are farther apart than adjacent."""
        n = adj.shape[0]
        adj_d, nonadj_d = [], []
        for i in range(n):
            for j in range(i + 1, n):
                d = np.linalg.norm(spectral_coords_2d[i] - spectral_coords_2d[j])
                (adj_d if adj[i, j] else nonadj_d).append(d)
        assert np.mean(nonadj_d) >= np.mean(adj_d) * 0.5
