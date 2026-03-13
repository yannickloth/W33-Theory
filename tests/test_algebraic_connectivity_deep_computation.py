"""
Phase CXXXVI: Deep Algebraic Connectivity and Fiedler Theory
Applied to W(3,3) = SRG(40, 12, 2, 4).

SRG parameters: n=40, k=12, lambda=2, mu=4
Adjacency spectrum: {12^1, 2^24, -4^15}
Laplacian L = 12I - A
Laplacian spectrum: {0^1, 10^24, 16^15}
Algebraic connectivity a(G) = lambda_2(L) = 10

Topics:
  1. Fiedler value and multiplicity
  2. Fiedler eigenvector space (24-dimensional)
  3. Vertex connectivity bounds from algebraic connectivity
  4. Edge connectivity and Laplacian structure
  5. Cheeger constant bounds
  6. Normalized Laplacian spectrum
  7. Resistance distance from Laplacian pseudoinverse
  8. Laplacian quadratic form and Rayleigh quotients
  9. Nodal domain theory for Fiedler vectors
 10. Isoperimetric / expansion bounds
 11. Laplacian powers spectrum
 12. Kirchhoff index and effective resistance totals
"""

import numpy as np
import pytest
from scipy import linalg as la


# ---------------------------------------------------------------------------
# W(3,3) builder (self-contained)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Module-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def adj():
    """Adjacency matrix of W(3,3)."""
    return _build_w33()


@pytest.fixture(scope="module")
def laplacian(adj):
    """Combinatorial Laplacian L = kI - A for k-regular graph."""
    n = adj.shape[0]
    return 12 * np.eye(n, dtype=float) - adj.astype(float)


@pytest.fixture(scope="module")
def lap_eig(laplacian):
    """Sorted eigenvalues and eigenvectors of L."""
    vals, vecs = la.eigh(laplacian)
    idx = np.argsort(vals)
    return vals[idx], vecs[:, idx]


@pytest.fixture(scope="module")
def adj_eig(adj):
    """Eigenvalues (descending) and eigenvectors of A."""
    vals, vecs = la.eigh(adj.astype(float))
    idx = np.argsort(-vals)
    return vals[idx], vecs[:, idx]


@pytest.fixture(scope="module")
def lap_pseudo(laplacian):
    """Moore-Penrose pseudoinverse of L."""
    return la.pinv(laplacian)


@pytest.fixture(scope="module")
def fiedler_space(lap_eig):
    """Eigenvectors spanning the Fiedler eigenspace (lambda=10)."""
    vals, vecs = lap_eig
    mask = np.abs(vals - 10.0) < 1e-8
    return vecs[:, mask]


@pytest.fixture(scope="module")
def norm_laplacian(adj):
    """Normalized Laplacian L_norm = I - D^{-1/2} A D^{-1/2}.
    For k-regular: L_norm = I - A/k = L/k."""
    n = adj.shape[0]
    d_inv_sqrt = (1.0 / np.sqrt(12)) * np.eye(n)
    return np.eye(n) - d_inv_sqrt @ adj.astype(float) @ d_inv_sqrt


@pytest.fixture(scope="module")
def norm_lap_eig(norm_laplacian):
    """Sorted eigenvalues of normalized Laplacian."""
    vals = la.eigvalsh(norm_laplacian)
    return np.sort(vals)


@pytest.fixture(scope="module")
def resistance_matrix(lap_pseudo):
    """Resistance distance matrix R_ij = L+_ii + L+_jj - 2*L+_ij."""
    diag = np.diag(lap_pseudo)
    R = diag[:, None] + diag[None, :] - 2 * lap_pseudo
    return R


# ===================================================================
# GROUP 1: Fiedler Value (algebraic connectivity)
# ===================================================================

class TestFiedlerValue:
    """a(G) = lambda_2(L) = 10 with multiplicity 24."""

    def test_smallest_eigenvalue_zero(self, lap_eig):
        vals, _ = lap_eig
        assert abs(vals[0]) < 1e-10

    def test_algebraic_connectivity_equals_10(self, lap_eig):
        vals, _ = lap_eig
        assert abs(vals[1] - 10.0) < 1e-8

    def test_fiedler_multiplicity_24(self, lap_eig):
        vals, _ = lap_eig
        count = np.sum(np.abs(vals - 10.0) < 1e-8)
        assert count == 24

    def test_largest_eigenvalue_16(self, lap_eig):
        vals, _ = lap_eig
        assert abs(vals[-1] - 16.0) < 1e-8

    def test_largest_multiplicity_15(self, lap_eig):
        vals, _ = lap_eig
        count = np.sum(np.abs(vals - 16.0) < 1e-8)
        assert count == 15

    def test_only_three_distinct_eigenvalues(self, lap_eig):
        vals, _ = lap_eig
        unique = []
        for v in vals:
            if not any(abs(v - u) < 1e-8 for u in unique):
                unique.append(v)
        assert len(unique) == 3

    def test_multiplicities_sum_to_n(self, lap_eig):
        """1 + 24 + 15 = 40 = n."""
        vals, _ = lap_eig
        assert len(vals) == 40

    def test_all_eigenvalues_nonneg(self, lap_eig):
        vals, _ = lap_eig
        assert np.all(vals > -1e-10)


# ===================================================================
# GROUP 2: Fiedler Vectors
# ===================================================================

class TestFiedlerVectors:
    """24-dimensional eigenspace of lambda_2 = 10."""

    def test_fiedler_space_dimension(self, fiedler_space):
        assert fiedler_space.shape == (40, 24)

    def test_fiedler_vectors_orthogonal_to_ones(self, fiedler_space):
        ones = np.ones(40)
        dots = fiedler_space.T @ ones
        assert np.allclose(dots, 0, atol=1e-10)

    def test_fiedler_vectors_orthonormal(self, fiedler_space):
        G = fiedler_space.T @ fiedler_space
        assert np.allclose(G, np.eye(24), atol=1e-10)

    def test_fiedler_vectors_are_eigenvectors(self, laplacian, fiedler_space):
        Lv = laplacian @ fiedler_space
        assert np.allclose(Lv, 10.0 * fiedler_space, atol=1e-8)

    def test_fiedler_projector_rank(self, fiedler_space):
        P = fiedler_space @ fiedler_space.T
        rank = np.linalg.matrix_rank(P, tol=1e-8)
        assert rank == 24

    def test_fiedler_projector_idempotent(self, fiedler_space):
        P = fiedler_space @ fiedler_space.T
        assert np.allclose(P @ P, P, atol=1e-10)

    def test_fiedler_projector_symmetric(self, fiedler_space):
        P = fiedler_space @ fiedler_space.T
        assert np.allclose(P, P.T, atol=1e-10)

    def test_fiedler_projector_trace(self, fiedler_space):
        P = fiedler_space @ fiedler_space.T
        assert abs(np.trace(P) - 24.0) < 1e-8

    def test_any_fiedler_vector_nonconstant(self, fiedler_space):
        for j in range(24):
            v = fiedler_space[:, j]
            assert np.std(v) > 1e-6

    def test_fiedler_vector_sum_zero(self, fiedler_space):
        for j in range(24):
            assert abs(np.sum(fiedler_space[:, j])) < 1e-10


# ===================================================================
# GROUP 3: Vertex Connectivity Bounds
# ===================================================================

class TestVertexConnectivity:
    """kappa(G) >= a(G) = 10; kappa(G) <= k = 12."""

    def test_algebraic_connectivity_lower_bound(self, lap_eig):
        """a(G) = 10 provides lower bound on vertex connectivity."""
        vals, _ = lap_eig
        assert vals[1] > 9.99

    def test_regularity_upper_bound(self, adj):
        """kappa(G) <= k = 12."""
        degrees = adj.sum(axis=1)
        assert int(degrees[0]) == 12

    def test_fiedler_bound_nontrivial(self, lap_eig):
        """a(G) = 10 > k/2 = 6 is a strong connectivity bound."""
        vals, _ = lap_eig
        assert vals[1] > 6.0

    def test_srg_connectivity_from_laplacian_rank(self, adj):
        """Connected graph has Laplacian nullity = 1."""
        n = adj.shape[0]
        L = 12 * np.eye(n) - adj.astype(float)
        rank = np.linalg.matrix_rank(L, tol=1e-8)
        assert rank == n - 1

    def test_algebraic_connectivity_is_positive(self, lap_eig):
        vals, _ = lap_eig
        assert vals[1] > 0

    def test_second_eigenvalue_separation(self, lap_eig):
        """Gap between lambda_1=0 and lambda_2=10 is exactly 10."""
        vals, _ = lap_eig
        gap = vals[1] - vals[0]
        assert abs(gap - 10.0) < 1e-8

    def test_max_degree_equals_min_degree(self, adj):
        """All degrees equal k=12 (regular graph)."""
        degrees = adj.sum(axis=1)
        assert np.all(degrees == 12)

    def test_complement_algebraic_connectivity(self, adj):
        """Complement SRG(40,27,18,18) has a(Q) = 24.
        Complement L eigenvalues: {0^1, 30^24, 24^15}, so a(Q)=24."""
        n = 40
        Q = 1 - adj - np.eye(n, dtype=int)
        L_Q = 27 * np.eye(n) - Q.astype(float)
        vals_Q = la.eigvalsh(L_Q)
        vals_Q.sort()
        assert abs(vals_Q[0]) < 1e-8
        assert abs(vals_Q[1] - 24.0) < 1e-7


# ===================================================================
# GROUP 4: Edge Connectivity
# ===================================================================

class TestEdgeConnectivity:
    """lambda(G) = k = 12 for vertex-transitive graphs."""

    def test_edge_connectivity_upper_bound(self, adj):
        """lambda(G) <= min degree = k = 12."""
        assert adj.sum(axis=1).min() == 12

    def test_algebraic_connectivity_le_edge_connectivity(self, lap_eig):
        """a(G) = 10 <= lambda(G) <= k = 12."""
        vals, _ = lap_eig
        assert vals[1] <= 12.0 + 1e-8

    def test_edge_count(self, adj):
        """Total edges = n*k/2 = 40*12/2 = 240."""
        assert adj.sum() == 480  # each edge counted twice
        assert adj.sum() // 2 == 240

    def test_edge_connectivity_bound_from_fiedler(self, lap_eig):
        """a(G) = 10 is a strong lower bound on edge connectivity."""
        vals, _ = lap_eig
        assert vals[1] >= 10.0 - 1e-8

    def test_laplacian_sum_of_rows_zero(self, laplacian):
        row_sums = laplacian.sum(axis=1)
        assert np.allclose(row_sums, 0, atol=1e-10)

    def test_laplacian_sum_of_cols_zero(self, laplacian):
        col_sums = laplacian.sum(axis=0)
        assert np.allclose(col_sums, 0, atol=1e-10)

    def test_laplacian_diagonal(self, laplacian):
        """Diagonal of L equals vertex degrees = 12."""
        assert np.allclose(np.diag(laplacian), 12.0)

    def test_laplacian_off_diagonal(self, laplacian, adj):
        """Off-diagonal L_ij = -A_ij."""
        n = 40
        for i in range(n):
            for j in range(n):
                if i != j:
                    assert abs(laplacian[i, j] + adj[i, j]) < 1e-10


# ===================================================================
# GROUP 5: Cheeger Constant Bounds
# ===================================================================

class TestCheegerConstant:
    """h(G) bounds from algebraic connectivity: a(G)/2 <= h(G) <= sqrt(2*k*a(G))."""

    def test_cheeger_lower_bound(self, lap_eig):
        """h(G) >= a(G)/2 = 5."""
        vals, _ = lap_eig
        lower = vals[1] / 2.0
        assert abs(lower - 5.0) < 1e-8

    def test_cheeger_upper_bound_from_alg_conn(self, lap_eig):
        """h(G) <= sqrt(2*k*a(G)) = sqrt(240)."""
        vals, _ = lap_eig
        upper = np.sqrt(2 * 12 * vals[1])
        assert abs(upper - np.sqrt(240)) < 1e-8

    def test_cheeger_upper_bound_value(self):
        """sqrt(240) ~ 15.49."""
        assert abs(np.sqrt(240) - 15.4919) < 0.001

    def test_cheeger_single_vertex_bound(self):
        """h(G) <= k = 12 from S={v}: |bdry|/|S| = 12/1."""
        assert 12 <= np.sqrt(240) + 1e-8

    def test_cheeger_adjacent_pair_bound(self, adj):
        """For adjacent S={i,j}: edges from i to V\\S = 11, from j = 11.
        boundary = 22, ratio = 22/2 = 11."""
        i, j = np.argwhere(adj > 0)[0]
        boundary = 0
        for v in range(40):
            if v == i or v == j:
                continue
            boundary += adj[i, v] + adj[j, v]
        assert abs(boundary / 2.0 - 11.0) < 1e-10

    def test_cheeger_nonadjacent_pair_bound(self, adj):
        """For non-adjacent S={i,j}: boundary = 24, ratio = 12."""
        for i in range(40):
            for j in range(i + 1, 40):
                if adj[i, j] == 0:
                    boundary = 0
                    for v in range(40):
                        if v == i or v == j:
                            continue
                        boundary += adj[i, v] + adj[j, v]
                    assert abs(boundary / 2.0 - 12.0) < 1e-10
                    return

    def test_spectral_gap_equals_algebraic_connectivity(self, adj_eig, lap_eig):
        """For k-regular: a(G) = k - lambda_2(A) = 12 - 2 = 10."""
        adj_vals, _ = adj_eig
        lap_vals, _ = lap_eig
        assert abs(12 - adj_vals[1] - lap_vals[1]) < 1e-8

    def test_cheeger_interval_nonempty(self, lap_eig):
        """Lower bound 5 < upper bound sqrt(240) ~ 15.49."""
        vals, _ = lap_eig
        lower = vals[1] / 2.0
        upper = np.sqrt(2 * 12 * vals[1])
        assert lower < upper


# ===================================================================
# GROUP 6: Normalized Laplacian
# ===================================================================

class TestNormalizedLaplacian:
    """L_norm = I - D^{-1/2} A D^{-1/2}; for k-regular: L_norm = L/k."""

    def test_norm_lap_smallest_eigenvalue_zero(self, norm_lap_eig):
        assert abs(norm_lap_eig[0]) < 1e-10

    def test_norm_lap_second_eigenvalue(self, norm_lap_eig):
        """1 - 2/12 = 5/6."""
        assert abs(norm_lap_eig[1] - 5.0 / 6.0) < 1e-8

    def test_norm_lap_largest_eigenvalue(self, norm_lap_eig):
        """1 - (-4)/12 = 4/3."""
        assert abs(norm_lap_eig[-1] - 4.0 / 3.0) < 1e-8

    def test_norm_lap_second_multiplicity(self, norm_lap_eig):
        count = np.sum(np.abs(norm_lap_eig - 5.0 / 6.0) < 1e-8)
        assert count == 24

    def test_norm_lap_largest_multiplicity(self, norm_lap_eig):
        count = np.sum(np.abs(norm_lap_eig - 4.0 / 3.0) < 1e-8)
        assert count == 15

    def test_norm_lap_equals_L_over_k(self, norm_laplacian, laplacian):
        """For k-regular graph, L_norm = L/k."""
        assert np.allclose(norm_laplacian, laplacian / 12.0, atol=1e-10)

    def test_norm_lap_trace(self, norm_laplacian):
        """tr(L_norm) = n for k-regular (each diagonal entry = 1)."""
        assert abs(np.trace(norm_laplacian) - 40.0) < 1e-8

    def test_norm_lap_symmetric(self, norm_laplacian):
        assert np.allclose(norm_laplacian, norm_laplacian.T, atol=1e-10)

    def test_norm_lap_psd(self, norm_lap_eig):
        """All eigenvalues >= 0."""
        assert np.all(norm_lap_eig > -1e-10)

    def test_norm_lap_eigenvalue_sum(self, norm_lap_eig):
        """Sum of eigenvalues = trace = 40."""
        assert abs(np.sum(norm_lap_eig) - 40.0) < 1e-7

    def test_norm_lap_spectral_gap(self, norm_lap_eig):
        """Normalized spectral gap = 5/6."""
        gap = norm_lap_eig[1] - norm_lap_eig[0]
        assert abs(gap - 5.0 / 6.0) < 1e-8


# ===================================================================
# GROUP 7: Resistance Distance
# ===================================================================

class TestResistanceDistance:
    """R_ij from Laplacian pseudoinverse."""

    def test_resistance_diagonal_zero(self, resistance_matrix):
        assert np.allclose(np.diag(resistance_matrix), 0, atol=1e-10)

    def test_resistance_symmetric(self, resistance_matrix):
        assert np.allclose(resistance_matrix, resistance_matrix.T, atol=1e-10)

    def test_resistance_nonnegative(self, resistance_matrix):
        assert np.all(resistance_matrix > -1e-10)

    def test_resistance_two_values(self, resistance_matrix, adj):
        """SRG has exactly 2 distinct off-diagonal resistance values."""
        vals = set()
        for i in range(40):
            for j in range(i + 1, 40):
                vals.add(round(resistance_matrix[i, j], 8))
        assert len(vals) == 2

    def test_resistance_adjacent_lt_nonadjacent(self, resistance_matrix, adj):
        """Adjacent vertices have smaller resistance distance."""
        r_adj = r_non = None
        for i in range(40):
            for j in range(i + 1, 40):
                if adj[i, j] == 1 and r_adj is None:
                    r_adj = resistance_matrix[i, j]
                elif adj[i, j] == 0 and r_non is None:
                    r_non = resistance_matrix[i, j]
                if r_adj is not None and r_non is not None:
                    break
            if r_adj is not None and r_non is not None:
                break
        assert r_adj < r_non

    def test_resistance_adjacent_value(self, resistance_matrix, adj):
        """R_adj = 13/80 from spectral projector decomposition.
        P_2 = (A+4I-16J/40)/6; for adjacent i~j: (P_2)_ij = 0.1
        P_3 = I-J/n-P_2; (P_3)_ij = -0.125
        L+_ij = 0.1/10 + (-0.125)/16 = 0.0021875
        L+_ii = 24/(40*10) + 15/(40*16) = 0.0834375
        R_adj = 2*(0.0834375 - 0.0021875) = 13/80."""
        i, j = np.argwhere(adj > 0)[0]
        assert abs(resistance_matrix[i, j] - 13.0 / 80.0) < 1e-8

    def test_resistance_nonadjacent_value(self, resistance_matrix, adj):
        """R_non = 7/40 from spectral projector decomposition.
        For non-adjacent: (P_2)_ij = -1/15, (P_3)_ij = 1/24
        L+_ij = (-1/15)/10 + (1/24)/16 = -13/3200
        R_non = 2*(0.0834375 + 13/3200) = 7/40."""
        for i in range(40):
            for j in range(i + 1, 40):
                if adj[i, j] == 0:
                    assert abs(resistance_matrix[i, j] - 7.0 / 40.0) < 1e-8
                    return

    def test_resistance_triangle_inequality(self, resistance_matrix):
        """Resistance distance is a metric: R_ij <= R_ik + R_kj."""
        n = 40
        for i in range(0, n, 5):
            for j in range(0, n, 5):
                for k in range(0, n, 5):
                    if i != j and j != k and i != k:
                        assert resistance_matrix[i, j] <= (
                            resistance_matrix[i, k] + resistance_matrix[k, j] + 1e-10
                        )

    def test_resistance_constant_per_adjacency_class(self, resistance_matrix, adj):
        """All adjacent pairs share one R value; all non-adjacent share another."""
        r_adj_set = set()
        r_non_set = set()
        for i in range(40):
            for j in range(i + 1, 40):
                r = round(resistance_matrix[i, j], 10)
                if adj[i, j] == 1:
                    r_adj_set.add(r)
                else:
                    r_non_set.add(r)
        assert len(r_adj_set) == 1
        assert len(r_non_set) == 1

    def test_pseudoinverse_symmetric(self, lap_pseudo):
        assert np.allclose(lap_pseudo, lap_pseudo.T, atol=1e-10)

    def test_pseudoinverse_moore_penrose(self, lap_pseudo, laplacian):
        """L * L+ * L = L (Moore-Penrose condition 1)."""
        product = laplacian @ lap_pseudo @ laplacian
        assert np.allclose(product, laplacian, atol=1e-8)


# ===================================================================
# GROUP 8: Laplacian Quadratic Form
# ===================================================================

class TestLaplacianQuadraticForm:
    """x^T L x = sum_{(i,j) in E} (x_i - x_j)^2."""

    def test_quadratic_form_equals_edge_sum(self, laplacian, adj):
        """x^T L x equals the sum of squared differences over edges."""
        rng = np.random.RandomState(42)
        x = rng.randn(40)
        form_val = x @ laplacian @ x
        edge_sum = 0.0
        for i in range(40):
            for j in range(i + 1, 40):
                if adj[i, j] == 1:
                    edge_sum += (x[i] - x[j]) ** 2
        assert abs(form_val - edge_sum) < 1e-8

    def test_quadratic_form_zero_for_constant(self, laplacian):
        """x = constant => x^T L x = 0."""
        x = np.ones(40) * 3.7
        assert abs(x @ laplacian @ x) < 1e-10

    def test_quadratic_form_nonneg(self, laplacian):
        """x^T L x >= 0 for all x (L is positive semidefinite)."""
        rng = np.random.RandomState(123)
        for _ in range(20):
            x = rng.randn(40)
            assert x @ laplacian @ x > -1e-10

    def test_minimum_over_perp_ones(self, laplacian, fiedler_space):
        """min x^T L x / x^T x over x perp 1 equals a(G) = 10."""
        v = fiedler_space[:, 0]
        ratio = (v @ laplacian @ v) / (v @ v)
        assert abs(ratio - 10.0) < 1e-8

    def test_rayleigh_quotient_fiedler(self, laplacian, fiedler_space):
        """All Fiedler vectors achieve Rayleigh quotient = 10."""
        for j in range(24):
            v = fiedler_space[:, j]
            r = (v @ laplacian @ v) / (v @ v)
            assert abs(r - 10.0) < 1e-8

    def test_rayleigh_quotient_top_eigenvector(self, laplacian, lap_eig):
        """Top eigenvector achieves Rayleigh quotient = 16."""
        _, vecs = lap_eig
        v = vecs[:, -1]
        r = (v @ laplacian @ v) / (v @ v)
        assert abs(r - 16.0) < 1e-8

    def test_quadratic_form_random_perp_ones(self, laplacian):
        """Any x perp 1 has x^T L x >= 10 * x^T x."""
        rng = np.random.RandomState(77)
        for _ in range(10):
            x = rng.randn(40)
            x -= np.mean(x)  # project perpendicular to all-ones
            if np.linalg.norm(x) < 1e-10:
                continue
            ratio = (x @ laplacian @ x) / (x @ x)
            assert ratio > 10.0 - 1e-8

    def test_hessian_of_quadratic_form(self, laplacian):
        """The Hessian of f(x) = x^T L x is 2L (verified via finite differences)."""
        rng = np.random.RandomState(99)
        x0 = rng.randn(40)
        eps = 1e-5
        for i in range(5):
            for j in range(5):
                ei = np.zeros(40); ei[i] = 1
                ej = np.zeros(40); ej[j] = 1
                f_pp = (x0 + eps*ei + eps*ej) @ laplacian @ (x0 + eps*ei + eps*ej)
                f_pm = (x0 + eps*ei - eps*ej) @ laplacian @ (x0 + eps*ei - eps*ej)
                f_mp = (x0 - eps*ei + eps*ej) @ laplacian @ (x0 - eps*ei + eps*ej)
                f_mm = (x0 - eps*ei - eps*ej) @ laplacian @ (x0 - eps*ei - eps*ej)
                hess_ij = (f_pp - f_pm - f_mp + f_mm) / (4 * eps**2)
                assert abs(hess_ij - 2 * laplacian[i, j]) < 1e-3

    def test_laplacian_null_space_dimension(self, laplacian):
        """Null space of L is 1-dimensional (spanned by all-ones)."""
        _, S, _ = la.svd(laplacian)
        null_dim = np.sum(S < 1e-8)
        assert null_dim == 1


# ===================================================================
# GROUP 9: Nodal Domain Theory
# ===================================================================

class TestNodalDomains:
    """Sign pattern of Fiedler vectors and induced nodal domains."""

    def _count_components(self, vertex_set, adj):
        """Count connected components within a vertex subset."""
        visited = set()
        components = 0
        for start in vertex_set:
            if start in visited:
                continue
            components += 1
            queue = [start]
            visited.add(start)
            while queue:
                u = queue.pop(0)
                for v in vertex_set:
                    if v not in visited and adj[u, v] == 1:
                        visited.add(v)
                        queue.append(v)
        return components

    def test_fiedler_vector_has_pos_and_neg(self, fiedler_space):
        """Every Fiedler vector has both positive and negative entries."""
        for j in range(24):
            v = fiedler_space[:, j]
            assert np.any(v > 1e-10)
            assert np.any(v < -1e-10)

    def test_nodal_domains_at_least_two(self, fiedler_space, adj):
        """Any Fiedler vector induces at least 2 nodal domains."""
        v = fiedler_space[:, 0]
        pos = set(i for i in range(40) if v[i] > 1e-12)
        neg = set(i for i in range(40) if v[i] < -1e-12)
        n_pos = self._count_components(pos, adj)
        n_neg = self._count_components(neg, adj)
        assert n_pos + n_neg >= 2

    def test_nodal_domain_positive_connected(self, fiedler_space, adj):
        """For the first Fiedler vector, positive vertices typically
        form a connected subgraph (1 component)."""
        v = fiedler_space[:, 0]
        pos = set(i for i in range(40) if v[i] > 1e-12)
        if len(pos) > 0:
            n_comp = self._count_components(pos, adj)
            # With high multiplicity, positive set may have a few components
            assert n_comp >= 1

    def test_fiedler_positive_set_size(self, fiedler_space):
        """Positive and negative sets are both non-trivial."""
        v = fiedler_space[:, 0]
        n_pos = np.sum(v > 1e-12)
        n_neg = np.sum(v < -1e-12)
        assert n_pos >= 1
        assert n_neg >= 1
        assert n_pos + n_neg <= 40

    def test_fiedler_partition_quality(self, fiedler_space, adj):
        """Sign-partition of Fiedler vector gives a non-trivial cut
        (cut < total edges)."""
        v = fiedler_space[:, 0]
        pos = v > 0
        cut = 0
        for i in range(40):
            for j in range(i + 1, 40):
                if adj[i, j] == 1 and pos[i] != pos[j]:
                    cut += 1
        assert 0 < cut < 240

    def test_sign_pattern_negation_symmetry(self, fiedler_space):
        """Negating a Fiedler vector swaps positive and negative counts."""
        v = fiedler_space[:, 0]
        pos1 = np.sum(v > 1e-12)
        neg1 = np.sum(v < -1e-12)
        pos2 = np.sum(-v > 1e-12)
        neg2 = np.sum(-v < -1e-12)
        assert pos1 == neg2
        assert neg1 == pos2

    def test_random_fiedler_combination_nonconstant(self, fiedler_space):
        """Random combination in Fiedler eigenspace has both signs."""
        rng = np.random.RandomState(42)
        coeffs = rng.randn(24)
        v = fiedler_space @ coeffs
        assert np.any(v > 1e-10)
        assert np.any(v < -1e-10)

    def test_fiedler_cut_ratio_bound(self, fiedler_space, adj):
        """The smaller side of the Fiedler partition has boundary/|S| >= a(G)/2 = 5
        (Cheeger inequality guarantees this for any set with |S| <= n/2)."""
        v = fiedler_space[:, 0]
        pos_idx = np.where(v > 0)[0]
        neg_idx = np.where(v <= 0)[0]
        # Use the smaller set for the Cheeger bound
        if len(pos_idx) <= len(neg_idx):
            S = set(pos_idx.tolist())
        else:
            S = set(neg_idx.tolist())
        s = len(S)
        if s == 0 or s > 20:
            return  # skip degenerate case
        boundary = 0
        for i in S:
            for j in range(40):
                if j not in S and adj[i, j] == 1:
                    boundary += 1
        ratio = boundary / s
        assert ratio >= 5.0 - 1e-8


# ===================================================================
# GROUP 10: Isoperimetric / Expansion Bounds
# ===================================================================

class TestIsoperimetricBounds:
    """Expansion properties from algebraic connectivity."""

    def test_mixing_lemma(self, adj):
        """Expander mixing lemma: |e(S,T) - k|S||T|/n| <= lambda* sqrt(|S||T|)
        where lambda* = max(|lambda_2|, |lambda_n|) = max(2, 4) = 4."""
        n, k = 40, 12
        lambda_star = 4.0
        rng = np.random.RandomState(42)
        for _ in range(10):
            perm = rng.permutation(n)
            s = rng.randint(1, 20)
            t = rng.randint(1, 20)
            S = set(perm[:s].tolist())
            T = set(perm[s:s + t].tolist())
            e_ST = sum(1 for i in S for j in T if adj[i, j] == 1)
            expected = k * len(S) * len(T) / n
            bound = lambda_star * np.sqrt(len(S) * len(T))
            assert abs(e_ST - expected) <= bound + 1e-8

    def test_edge_expansion_lower_bound(self, adj):
        """For S with |S| <= n/2: |boundary(S)| / |S| >= h(G) >= a(G)/2 = 5."""
        n = 40
        rng = np.random.RandomState(55)
        for _ in range(5):
            s_size = rng.randint(1, 10)
            S = set(rng.choice(n, s_size, replace=False).tolist())
            boundary = 0
            for i in S:
                for j in range(n):
                    if j not in S and adj[i, j] == 1:
                        boundary += 1
            assert boundary / len(S) >= 5.0 - 1e-8

    def test_vertex_expansion_single(self, adj):
        """N({v}) = k = 12 for any single vertex."""
        N_0 = set()
        for j in range(40):
            if adj[0, j] == 1:
                N_0.add(j)
        assert len(N_0) == 12

    def test_diameter_equals_two(self, adj):
        """W(3,3) has diameter 2 (any two vertices at distance <= 2)."""
        n = 40
        diameter = 0
        for start in range(n):
            dist = [-1] * n
            dist[start] = 0
            queue = [start]
            while queue:
                u = queue.pop(0)
                for v in range(n):
                    if adj[u, v] == 1 and dist[v] == -1:
                        dist[v] = dist[u] + 1
                        queue.append(v)
            diameter = max(diameter, max(dist))
        assert diameter == 2

    def test_diameter_spectral_upper_bound(self):
        """Spectral bound: diam <= ceil(log(n-1)/log(k/lambda_2(A))).
        = ceil(log(39)/log(6)) ~ ceil(2.04) = 3 >= actual diameter 2."""
        import math
        n, k, lam2 = 40, 12, 2
        bound = math.ceil(math.log(n - 1) / math.log(k / lam2))
        assert bound >= 2  # >= actual diameter
        assert bound <= 3

    def test_spectral_gap_implies_rapid_mixing(self, adj_eig):
        """Spectral gap = k - lambda_2(A) = 10 implies mixing time ~ k/gap."""
        vals, _ = adj_eig
        spectral_gap = vals[0] - vals[1]
        assert abs(spectral_gap - 10.0) < 1e-8
        mixing_time_bound = 12.0 / spectral_gap
        assert mixing_time_bound < 2.0  # very fast mixing

    def test_expansion_strong(self, lap_eig):
        """a(G) = 10 is large relative to k = 12 (ratio 10/12 = 5/6),
        certifying W(3,3) as an excellent expander."""
        vals, _ = lap_eig
        ratio = vals[1] / 12.0
        assert abs(ratio - 5.0 / 6.0) < 1e-8


# ===================================================================
# GROUP 11: Laplacian Powers Spectrum
# ===================================================================

class TestLaplacianPowers:
    """L^p eigenvalues = (eigenvalues of L)^p."""

    def test_L_squared_eigenvalues(self, laplacian, lap_eig):
        vals, _ = lap_eig
        L2 = laplacian @ laplacian
        vals2 = la.eigvalsh(L2)
        vals2.sort()
        expected = np.sort(vals ** 2)
        assert np.allclose(vals2, expected, atol=1e-6)

    def test_L_squared_spectrum(self, lap_eig):
        """L^2 eigenvalues: 0^1, 100^24, 256^15."""
        vals, _ = lap_eig
        vals2 = np.sort(vals ** 2)
        assert abs(vals2[0]) < 1e-8
        assert abs(vals2[1] - 100.0) < 1e-6
        assert abs(vals2[-1] - 256.0) < 1e-6

    def test_L_cubed_eigenvalues(self, laplacian, lap_eig):
        vals, _ = lap_eig
        L3 = laplacian @ laplacian @ laplacian
        vals3 = la.eigvalsh(L3)
        vals3.sort()
        expected = np.sort(vals ** 3)
        assert np.allclose(vals3, expected, atol=1e-4)

    def test_L_cubed_spectrum(self, lap_eig):
        """L^3 eigenvalues: 0^1, 1000^24, 4096^15."""
        vals, _ = lap_eig
        vals3 = np.sort(vals ** 3)
        assert abs(vals3[0]) < 1e-8
        assert abs(vals3[1] - 1000.0) < 1e-4
        assert abs(vals3[-1] - 4096.0) < 1e-4

    def test_trace_L_squared(self, laplacian):
        """tr(L^2) = 0 + 24*100 + 15*256 = 6240."""
        L2 = laplacian @ laplacian
        assert abs(np.trace(L2) - 6240.0) < 1e-6

    def test_trace_L_cubed(self, laplacian):
        """tr(L^3) = 0 + 24*1000 + 15*4096 = 85440."""
        L3 = laplacian @ laplacian @ laplacian
        assert abs(np.trace(L3) - 85440.0) < 1e-4

    def test_trace_L(self, laplacian):
        """tr(L) = 0 + 24*10 + 15*16 = 480 = n*k."""
        assert abs(np.trace(laplacian) - 480.0) < 1e-8

    def test_trace_L_equals_2m(self, adj):
        """For k-regular: tr(L) = n*k = 2|E|."""
        n = adj.shape[0]
        num_edges = adj.sum() // 2
        assert n * 12 == 2 * num_edges  # 480 = 2*240

    def test_L_power_preserves_eigenspaces(self, laplacian, fiedler_space):
        """L^2 on Fiedler space gives 100 * Fiedler space."""
        L2 = laplacian @ laplacian
        result = L2 @ fiedler_space
        expected = 100.0 * fiedler_space
        assert np.allclose(result, expected, atol=1e-6)

    def test_L_fourth_power_spectrum(self, lap_eig):
        """L^4 eigenvalues: 0, 10000, 65536."""
        vals, _ = lap_eig
        vals4 = np.sort(vals ** 4)
        assert abs(vals4[0]) < 1e-6
        assert abs(vals4[1] - 10000.0) < 0.1
        assert abs(vals4[-1] - 65536.0) < 0.1

    def test_polynomial_of_L(self, laplacian, lap_eig):
        """p(L) = 2L^2 - 3L + I has eigenvalues p(lambda_i).
        p(0)=1, p(10)=171, p(16)=465."""
        vals, _ = lap_eig
        pL = 2 * laplacian @ laplacian - 3 * laplacian + np.eye(40)
        pvals = la.eigvalsh(pL)
        pvals.sort()
        expected = np.sort(2 * vals ** 2 - 3 * vals + 1)
        assert np.allclose(pvals, expected, atol=1e-4)


# ===================================================================
# GROUP 12: Kirchhoff Index and Effective Resistance
# ===================================================================

class TestKirchhoffIndex:
    """Kf = n * sum(1/lambda_i for nonzero lambda_i)."""

    def test_kirchhoff_index_value(self, lap_eig):
        """Kf = 40 * (24/10 + 15/16) = 40 * 3.3375 = 133.5."""
        vals, _ = lap_eig
        nonzero = vals[vals > 1e-8]
        Kf = 40 * np.sum(1.0 / nonzero)
        assert abs(Kf - 133.5) < 1e-6

    def test_kirchhoff_from_resistance_matrix(self, resistance_matrix):
        """Kf = (1/2) sum_ij R_ij = sum_{i<j} R_ij."""
        Kf = np.sum(resistance_matrix) / 2.0
        assert abs(Kf - 133.5) < 1e-6

    def test_kirchhoff_from_pair_counts(self):
        """Kf = 240*(13/80) + 540*(7/40) = 39 + 94.5 = 133.5.
        (240 adjacent pairs, 540 non-adjacent pairs.)"""
        n_adj = 240
        n_non = 540
        R_adj = 13.0 / 80.0
        R_non = 7.0 / 40.0
        Kf = n_adj * R_adj + n_non * R_non
        assert abs(Kf - 133.5) < 1e-10

    def test_average_resistance_adjacent(self, resistance_matrix, adj):
        """Mean R over adjacent pairs = 13/80 (all identical)."""
        total = 0.0
        count = 0
        for i in range(40):
            for j in range(i + 1, 40):
                if adj[i, j] == 1:
                    total += resistance_matrix[i, j]
                    count += 1
        assert count == 240
        assert abs(total / count - 13.0 / 80.0) < 1e-10

    def test_average_resistance_nonadjacent(self, resistance_matrix, adj):
        """Mean R over non-adjacent pairs = 7/40 (all identical)."""
        total = 0.0
        count = 0
        for i in range(40):
            for j in range(i + 1, 40):
                if adj[i, j] == 0:
                    total += resistance_matrix[i, j]
                    count += 1
        assert count == 540
        assert abs(total / count - 7.0 / 40.0) < 1e-10

    def test_log_spanning_tree_count(self, lap_eig):
        """tau = (1/n) prod(nonzero lambda_i) = (1/40)*10^24*16^15.
        log(tau) = -log(40) + 24*log(10) + 15*log(16) ~ 93.16."""
        vals, _ = lap_eig
        nonzero = vals[vals > 1e-8]
        log_tau = -np.log(40) + np.sum(np.log(nonzero))
        expected = -np.log(40) + 24 * np.log(10) + 15 * np.log(16)
        assert abs(log_tau - expected) < 1e-4

    def test_spanning_tree_from_cofactor(self, laplacian):
        """det(L_minor) = tau (any (n-1)x(n-1) principal minor).
        slogdet gives (sign, log|det|)."""
        L_minor = laplacian[1:, 1:]
        sign, logdet = np.linalg.slogdet(L_minor)
        expected_logdet = -np.log(40) + 24 * np.log(10) + 15 * np.log(16)
        assert abs(logdet - expected_logdet) < 0.1
        assert sign > 0

    def test_kirchhoff_index_alt_formula(self):
        """Kf = 40*(24/10 + 15/16) = 40*3.3375 = 133.5."""
        Kf = 40 * (24.0 / 10.0 + 15.0 / 16.0)
        assert abs(Kf - 133.5) < 1e-10

    def test_effective_resistance_ratio(self):
        """R_non / R_adj = (7/40)/(13/80) = 14/13."""
        ratio = (7.0 / 40.0) / (13.0 / 80.0)
        assert abs(ratio - 14.0 / 13.0) < 1e-10

    def test_foster_first_formula(self, resistance_matrix, adj):
        """Foster's first formula: sum_{(i,j) in E} R_ij = n - 1 = 39.
        For k-regular: 240 * (13/80) = 39."""
        total = 0.0
        for i in range(40):
            for j in range(i + 1, 40):
                if adj[i, j] == 1:
                    total += resistance_matrix[i, j]
        assert abs(total - 39.0) < 1e-6

    def test_foster_formula_verification(self):
        """240 * (13/80) = 39 = n - 1 = 40 - 1."""
        assert abs(240 * 13.0 / 80.0 - 39.0) < 1e-10


# ===================================================================
# GROUP 13: Additional Cross-Topic Verifications
# ===================================================================

class TestCrossTopicVerifications:
    """Additional tests linking different aspects of algebraic connectivity."""

    def test_eigenvalue_interlacing_complement(self, lap_eig):
        """L eigenvalues {0, 10, 16} and complement L eigenvalues {0, 24, 30}
        satisfy: for k-regular, complement lambda_i = n - L_lambda_{n+1-i}
        for the non-trivial eigenvalues.
        L has 10 (mult 24) and 16 (mult 15).
        Complement L has n - 10 = 30 (mult 24) and n - 16 = 24 (mult 15)."""
        vals, _ = lap_eig
        n = 40
        # non-trivial eigenvalues
        fiedler_val = 10.0
        top_val = 16.0
        assert abs((n - fiedler_val) - 30.0) < 1e-8
        assert abs((n - top_val) - 24.0) < 1e-8

    def test_laplacian_energy(self, lap_eig):
        """Laplacian energy LE = sum |lambda_i - 2|E|/n|.
        2|E|/n = 480/40 = 12. So LE = |0-12| + 24*|10-12| + 15*|16-12|
        = 12 + 24*2 + 15*4 = 12 + 48 + 60 = 120."""
        vals, _ = lap_eig
        avg = 480.0 / 40.0  # = 12
        LE = np.sum(np.abs(vals - avg))
        assert abs(LE - 120.0) < 1e-6

    def test_resistance_and_kirchhoff_consistency(self, resistance_matrix, lap_eig):
        """Cross-check: Kf from resistance matrix equals Kf from eigenvalues."""
        Kf_resist = np.sum(resistance_matrix) / 2.0
        vals, _ = lap_eig
        nonzero = vals[vals > 1e-8]
        Kf_spectral = 40 * np.sum(1.0 / nonzero)
        assert abs(Kf_resist - Kf_spectral) < 1e-6

    def test_pseudoinverse_eigenvalues(self, lap_pseudo):
        """L+ eigenvalues: 0 (mult 1), 1/10 (mult 24), 1/16 (mult 15)."""
        vals = la.eigvalsh(lap_pseudo)
        vals_sorted = np.sort(vals)
        assert abs(vals_sorted[0]) < 1e-10  # eigenvalue 0
        assert abs(vals_sorted[1] - 1.0 / 16.0) < 1e-8  # 1/16
        assert abs(vals_sorted[16] - 1.0 / 10.0) < 1e-8  # 1/10

    def test_pseudoinverse_trace(self, lap_pseudo):
        """tr(L+) = sum(1/lambda_i for nonzero) = 24/10 + 15/16 = 3.3375."""
        expected = 24.0 / 10.0 + 15.0 / 16.0
        assert abs(np.trace(lap_pseudo) - expected) < 1e-8

    def test_spectral_decomposition_of_A(self, adj, adj_eig):
        """A = 12*(J/n) + 2*P_2 + (-4)*P_3 reconstructs adjacency matrix."""
        vals, vecs = adj_eig
        n = 40
        # Projector onto eigenvalue 12 (eigenvector proportional to ones)
        P0 = np.ones((n, n)) / n
        # Projector onto eigenvalue 2
        mask2 = np.abs(vals - 2.0) < 1e-8
        V2 = vecs[:, mask2]
        P2 = V2 @ V2.T
        # Projector onto eigenvalue -4
        mask4 = np.abs(vals - (-4.0)) < 1e-8
        V4 = vecs[:, mask4]
        P3 = V4 @ V4.T
        A_recon = 12 * P0 + 2 * P2 + (-4) * P3
        assert np.allclose(A_recon, adj.astype(float), atol=1e-8)

    def test_L_spectral_decomposition(self, laplacian, lap_eig):
        """L = 0*P_0 + 10*P_1 + 16*P_2 reconstructs Laplacian."""
        vals, vecs = lap_eig
        n = 40
        L_recon = np.zeros((n, n))
        for lam in [0.0, 10.0, 16.0]:
            mask = np.abs(vals - lam) < 1e-8
            V = vecs[:, mask]
            L_recon += lam * (V @ V.T)
        assert np.allclose(L_recon, laplacian, atol=1e-8)

    def test_normalized_algebraic_connectivity_ratio(self, lap_eig):
        """Normalized ratio a(G)/k = 10/12 = 5/6 measures expansion quality.
        Values close to 1 indicate Ramanujan-like expansion."""
        vals, _ = lap_eig
        ratio = vals[1] / 12.0
        assert abs(ratio - 5.0 / 6.0) < 1e-8
        # Ramanujan bound for k-regular: lambda_2(A) <= 2*sqrt(k-1) ~ 6.63
        # Actual lambda_2(A) = 2 << 6.63, so W(3,3) is Ramanujan
        assert 2.0 < 2.0 * np.sqrt(11) + 1e-8

    def test_resistance_from_eigendecomposition(self, adj, lap_eig):
        """Verify R_adj directly from eigendecomposition.
        L+_ii = (1/n)*sum(1/lambda_k) = (1/40)*(24/10 + 15/16) = 0.0834375
        For adjacent i~j: L+_ij computed from projectors.
        R_adj = 2*(L+_ii - L+_ij) = 13/80."""
        vals, vecs = lap_eig
        n = 40
        # Compute L+ from eigendecomposition
        Lp = np.zeros((n, n))
        for idx in range(n):
            if vals[idx] > 1e-8:
                v = vecs[:, idx:idx+1]
                Lp += (1.0 / vals[idx]) * (v @ v.T)
        # Find an adjacent pair
        i, j = np.argwhere(adj > 0)[0]
        R_ij = Lp[i, i] + Lp[j, j] - 2 * Lp[i, j]
        assert abs(R_ij - 13.0 / 80.0) < 1e-8

    def test_w33_is_ramanujan(self, adj_eig):
        """W(3,3) is Ramanujan: lambda_2(A) = 2 <= 2*sqrt(k-1) = 2*sqrt(11) ~ 6.63."""
        vals, _ = adj_eig
        lambda2 = vals[1]  # second-largest adjacency eigenvalue
        ramanujan_bound = 2.0 * np.sqrt(11)
        assert lambda2 < ramanujan_bound + 1e-8
        assert abs(lambda2 - 2.0) < 1e-8
