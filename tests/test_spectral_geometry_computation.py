"""
Phase CIX  --  Spectral Geometry Computation on W(3,3) = SRG(40,12,2,4).

75+ tests covering heat kernels, spectral zeta functions, discrete curvature,
distance spectrum, spectral dimension, Laplacian variants, isoperimetric
properties, and spectral embedding geometry.

All tests use only numpy and standard library.  Every assertion is
mathematically provable from the SRG(40,12,2,4) spectrum
    adjacency:  {12^1, 2^24, (-4)^15}
    Laplacian:  {0^1, 10^24, 16^15}
"""

import numpy as np
from numpy.linalg import eigh, eigvalsh, norm
import pytest
from itertools import combinations


# ── W(3,3) builder ───────────────────────────────────────────────────────────

def _build_w33():
    """Build the 40-vertex symplectic graph W(3,3) = Sp(4,3)."""
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


# ── SRG parameters ───────────────────────────────────────────────────────────

_N, _K, _LAM, _MU = 40, 12, 2, 4


# ── Module-scoped fixtures ───────────────────────────────────────────────────

@pytest.fixture(scope="module")
def A():
    """Adjacency matrix of W(3,3)."""
    return _build_w33()


@pytest.fixture(scope="module")
def L(A):
    """Combinatorial Laplacian L = kI - A."""
    return float(_K) * np.eye(_N, dtype=float) - A.astype(float)


@pytest.fixture(scope="module")
def lap_eigenvalues(L):
    """Sorted (ascending) Laplacian eigenvalues."""
    return np.sort(eigvalsh(L))


@pytest.fixture(scope="module")
def adj_eigenvalues(A):
    """Sorted (ascending) adjacency eigenvalues."""
    return np.sort(eigvalsh(A.astype(float)))


# ═════════════════════════════════════════════════════════════════════════════
# Section 1 : Heat Kernel   (14 tests)
# H(t) = exp(-tL);  trace H(t) = 1 + 24 exp(-10t) + 15 exp(-16t)
# ═════════════════════════════════════════════════════════════════════════════

class TestHeatKernel:

    # -- helpers --

    @staticmethod
    def _heat_matrix(L, t):
        """exp(-tL) via eigendecomposition."""
        vals, vecs = eigh(L)
        return vecs @ np.diag(np.exp(-t * vals)) @ vecs.T

    @staticmethod
    def _heat_trace_exact(t):
        """Exact trace from known Laplacian spectrum {0^1, 10^24, 16^15}."""
        return 1.0 + 24.0 * np.exp(-10.0 * t) + 15.0 * np.exp(-16.0 * t)

    # -- tests --

    def test_H0_is_identity(self, L):
        """H(0) = I_{40}."""
        H0 = self._heat_matrix(L, 0.0)
        assert np.allclose(H0, np.eye(_N), atol=1e-12)

    def test_heat_trace_at_zero(self, L):
        """trace H(0) = n = 40."""
        H0 = self._heat_matrix(L, 0.0)
        assert abs(np.trace(H0) - 40.0) < 1e-10

    def test_heat_trace_formula_t_point1(self, L):
        """trace H(0.1) matches spectral formula."""
        t = 0.1
        assert abs(np.trace(self._heat_matrix(L, t))
                    - self._heat_trace_exact(t)) < 1e-8

    def test_heat_trace_formula_t1(self, L):
        """trace H(1.0) matches spectral formula."""
        t = 1.0
        assert abs(np.trace(self._heat_matrix(L, t))
                    - self._heat_trace_exact(t)) < 1e-8

    def test_heat_trace_formula_t_point01(self, L):
        """trace H(0.01) matches spectral formula."""
        t = 0.01
        assert abs(np.trace(self._heat_matrix(L, t))
                    - self._heat_trace_exact(t)) < 1e-8

    def test_heat_symmetry(self, L):
        """H(t) is symmetric for every t > 0."""
        H = self._heat_matrix(L, 0.5)
        assert np.allclose(H, H.T, atol=1e-12)

    def test_heat_positive_semidefinite(self, L):
        """All eigenvalues of H(t) are >= 0."""
        evals = eigvalsh(self._heat_matrix(L, 0.3))
        assert np.all(evals >= -1e-12)

    def test_semigroup_property(self, L):
        """H(t1) @ H(t2) = H(t1 + t2)."""
        t1, t2 = 0.3, 0.5
        H1 = self._heat_matrix(L, t1)
        H2 = self._heat_matrix(L, t2)
        H12 = self._heat_matrix(L, t1 + t2)
        assert np.allclose(H1 @ H2, H12, atol=1e-10)

    def test_long_time_limit(self, L):
        """H(t) -> (1/n) J  as t -> inf."""
        H = self._heat_matrix(L, 50.0)
        J_over_n = np.ones((_N, _N)) / float(_N)
        assert np.allclose(H, J_over_n, atol=1e-10)

    def test_heat_content_constant(self, L):
        """E(t) = 1^T H(t) 1 = 40 for all t  (since L 1 = 0)."""
        ones = np.ones(_N)
        for t in [0.0, 0.1, 1.0, 10.0]:
            H = self._heat_matrix(L, t)
            E = ones @ H @ ones
            assert abs(E - 40.0) < 1e-8, f"E({t}) = {E}"

    def test_return_prob_at_zero(self, L):
        """P(0) = trace H(0) / n = 1."""
        P0 = np.trace(self._heat_matrix(L, 0.0)) / float(_N)
        assert abs(P0 - 1.0) < 1e-12

    def test_return_prob_long_time(self, L):
        """P(inf) -> 1/n = 1/40."""
        P_inf = np.trace(self._heat_matrix(L, 50.0)) / float(_N)
        assert abs(P_inf - 1.0 / 40.0) < 1e-12

    def test_heat_diagonal_uniform(self, L):
        """H(t)_{ii} identical for all i  (vertex-transitivity)."""
        diag = np.diag(self._heat_matrix(L, 0.2))
        assert np.allclose(diag, diag[0], atol=1e-10)

    def test_heat_trace_first_coefficient(self, L):
        """a_0 = 40  and  a_1 = trace(L) = 480."""
        assert abs(np.trace(L) - 480.0) < 1e-10


# ═════════════════════════════════════════════════════════════════════════════
# Section 2 : Spectral Zeta Function   (10 tests)
# zeta_L(s) = sum_{lam > 0} lam^{-s} = 24 * 10^{-s} + 15 * 16^{-s}
# ═════════════════════════════════════════════════════════════════════════════

class TestSpectralZeta:

    @staticmethod
    def _zeta(s):
        """Exact spectral zeta from Laplacian spectrum {10^24, 16^15}."""
        return 24.0 * (10.0 ** (-s)) + 15.0 * (16.0 ** (-s))

    def test_zeta_at_0(self):
        """zeta_L(0) = #(nonzero eigenvalues) = 39."""
        assert abs(self._zeta(0) - 39.0) < 1e-12

    def test_zeta_at_1(self):
        """zeta_L(1) = 24/10 + 15/16 = 267/80."""
        assert abs(self._zeta(1) - 267.0 / 80.0) < 1e-12

    def test_zeta_at_2(self):
        """zeta_L(2) = 24/100 + 15/256 = 1911/6400."""
        assert abs(self._zeta(2) - 1911.0 / 6400.0) < 1e-12

    def test_zeta_at_half(self):
        """zeta_L(1/2) = 24/sqrt(10) + 15/4."""
        expected = 24.0 / np.sqrt(10.0) + 15.0 / 4.0
        assert abs(self._zeta(0.5) - expected) < 1e-12

    def test_zeta_neg1_is_trace_L(self, L):
        """zeta_L(-1) = sum lam_i = trace(L) = 480."""
        assert abs(self._zeta(-1) - 480.0) < 1e-8
        assert abs(self._zeta(-1) - np.trace(L)) < 1e-8

    def test_zeta_neg2_is_trace_L2(self, L):
        """zeta_L(-2) = sum lam_i^2 = trace(L^2) = 6240."""
        expected = 24.0 * 100.0 + 15.0 * 256.0   # 2400 + 3840
        assert abs(self._zeta(-2) - 6240.0) < 1e-6
        assert abs(np.trace(L @ L) - 6240.0) < 1e-6

    def test_zeta_neg3_is_trace_L3(self, L):
        """zeta_L(-3) = sum lam_i^3 = trace(L^3) = 85440."""
        expected = 24.0 * 1000.0 + 15.0 * 4096.0   # 24000 + 61440
        assert abs(self._zeta(-3) - 85440.0) < 1e-4
        assert abs(np.trace(L @ L @ L) - 85440.0) < 1e-4

    def test_log_regularized_determinant(self, L):
        """log det'(L) = 24 ln 10 + 15 ln 16."""
        expected = 24.0 * np.log(10.0) + 15.0 * np.log(16.0)
        evals = eigvalsh(L)
        log_det = np.sum(np.log(evals[evals > 1e-8]))
        assert abs(log_det - expected) < 1e-8

    def test_regularized_determinant_factorisation(self):
        """det'(L) = 10^24 * 16^15 = 2^84 * 5^24."""
        log_det = 24.0 * np.log(10.0) + 15.0 * np.log(16.0)
        log_alt = 84.0 * np.log(2.0) + 24.0 * np.log(5.0)
        assert abs(log_det - log_alt) < 1e-10

    def test_nonzero_eigenvalue_count(self, lap_eigenvalues):
        """Exactly 39 nonzero Laplacian eigenvalues."""
        assert np.sum(np.abs(lap_eigenvalues) > 1e-8) == 39


# ═════════════════════════════════════════════════════════════════════════════
# Section 3 : Discrete Curvature   (11 tests)
# Forman-Ricci, triangle counts, clustering coefficient
# ═════════════════════════════════════════════════════════════════════════════

class TestDiscreteCurvature:

    @staticmethod
    def _edges(A):
        """All edges (i, j) with i < j."""
        n = A.shape[0]
        return [(i, j) for i in range(n) for j in range(i + 1, n) if A[i, j]]

    @staticmethod
    def _tri_count_edge(A, u, v):
        """Number of triangles through edge (u, v)."""
        return int(np.sum(A[u] * A[v]))

    # -- tests --

    def test_total_edges(self, A):
        """m = nk/2 = 240."""
        assert np.sum(A) // 2 == 240

    def test_total_triangles(self, A):
        """trace(A^3)/6 = n k lambda / 6 = 160."""
        assert int(np.trace(A @ A @ A)) // 6 == 160

    def test_triangles_per_edge_is_lambda(self, A):
        """Every edge sits in exactly lambda = 2 triangles."""
        for u, v in self._edges(A)[:30]:
            assert self._tri_count_edge(A, u, v) == _LAM

    def test_common_neighbours_nonadj_is_mu(self, A):
        """Every non-edge has exactly mu = 4 common neighbours."""
        A2 = A @ A
        checked = 0
        for i in range(_N):
            for j in range(i + 1, _N):
                if A[i, j] == 0:
                    assert A2[i, j] == _MU
                    checked += 1
                    if checked >= 40:
                        return

    def test_forman_basic(self, A):
        """Basic Forman-Ricci  F = 4 - deg(u) - deg(v) = -20  per edge."""
        for u, v in self._edges(A)[:20]:
            assert 4 - int(np.sum(A[u])) - int(np.sum(A[v])) == -20

    def test_augmented_forman(self, A):
        """Augmented Forman  F' = 4 - d(u) - d(v) + 3 |tri| = -14  per edge."""
        for u, v in self._edges(A)[:20]:
            tri = self._tri_count_edge(A, u, v)
            F = 4 - int(np.sum(A[u])) - int(np.sum(A[v])) + 3 * tri
            assert F == -14

    def test_forman_constant_all_edges(self, A):
        """Augmented Forman curvature is the same on every edge (edge-transitive)."""
        vals = set()
        for u, v in self._edges(A):
            tri = self._tri_count_edge(A, u, v)
            vals.add(4 - int(np.sum(A[u])) - int(np.sum(A[v])) + 3 * tri)
        assert vals == {-14}

    def test_clustering_coefficient(self, A):
        """C(v) = lambda / (k - 1) = 2/11  for every vertex."""
        for v in range(_N):
            nbrs = np.where(A[v] == 1)[0]
            k_v = len(nbrs)
            edges_among = sum(1 for i, j in combinations(nbrs, 2) if A[i, j])
            cc = 2.0 * edges_among / (k_v * (k_v - 1))
            assert abs(cc - 2.0 / 11.0) < 1e-12

    def test_triangles_per_vertex(self, A):
        """Each vertex belongs to k lambda / 2 = 12 triangles."""
        diag_A3 = np.diag(A @ A @ A)
        for v in range(_N):
            assert diag_A3[v] // 2 == 12

    def test_scalar_forman_per_vertex(self, A):
        """Sum of augmented Forman over edges incident to v  =  k * (-14) = -168."""
        for v in range(_N):
            nbrs = np.where(A[v] == 1)[0]
            s = 0
            for u in nbrs:
                tri = self._tri_count_edge(A, v, u)
                s += 4 - int(np.sum(A[v])) - int(np.sum(A[u])) + 3 * tri
            assert s == -168

    def test_mean_augmented_forman(self, A):
        """Mean augmented Forman curvature over all 240 edges = -14."""
        total = sum(
            4 - int(np.sum(A[u])) - int(np.sum(A[v]))
            + 3 * self._tri_count_edge(A, u, v)
            for u, v in self._edges(A)
        )
        assert abs(total / 240.0 - (-14.0)) < 1e-12


# ═════════════════════════════════════════════════════════════════════════════
# Section 4 : Distance Spectrum   (10 tests)
# D = 2(J - I) - A   for diameter-2 SRG
# Distance eigenvalues: {66^1, (-4)^24, 2^15}
# ═════════════════════════════════════════════════════════════════════════════

class TestDistanceSpectrum:

    @pytest.fixture(scope="class")
    def D(self, A):
        """Distance matrix: D_ij = 0, 1, or 2."""
        J = np.ones((_N, _N), dtype=float)
        I = np.eye(_N, dtype=float)
        return 2.0 * (J - I) - A.astype(float)

    def test_distance_entries(self, A, D):
        """D_ij in {0, 1, 2} with correct adjacency/non-adjacency."""
        for i in range(_N):
            assert D[i, i] == 0.0
            for j in range(i + 1, _N):
                if A[i, j] == 1:
                    assert D[i, j] == 1.0
                else:
                    assert D[i, j] == 2.0

    def test_diameter_is_2(self, D):
        """diam(W(3,3)) = 2."""
        assert int(np.max(D)) == 2

    def test_wiener_index(self, D):
        """W = (1/2) sum D_ij = 1320."""
        W = np.sum(D) / 2.0
        assert abs(W - 1320.0) < 1e-8

    def test_wiener_formula(self):
        """W = n(k + 2(n-1-k)) / 2 = 40*66/2 = 1320."""
        W = _N * (_K * 1 + (_N - 1 - _K) * 2) // 2
        assert W == 1320

    def test_distance_row_sum(self, D):
        """Row sum = k + 2(n-1-k) = 66  for every vertex."""
        assert np.allclose(np.sum(D, axis=1), 66.0, atol=1e-10)

    def test_distance_eigenvalues(self, D):
        """Distance spectrum: {66^1, 2^15, (-4)^24}  (sorted descending)."""
        evals = np.sort(eigvalsh(D))[::-1]
        assert abs(evals[0] - 66.0) < 1e-8
        for i in range(1, 16):
            assert abs(evals[i] - 2.0) < 1e-8, f"evals[{i}]={evals[i]}"
        for i in range(16, 40):
            assert abs(evals[i] - (-4.0)) < 1e-8, f"evals[{i}]={evals[i]}"

    def test_distance_energy(self, D):
        """Distance energy = sum |d_i| = 66 + 15*2 + 24*4 = 192."""
        energy = np.sum(np.abs(eigvalsh(D)))
        assert abs(energy - 192.0) < 1e-6

    def test_average_distance(self, D):
        """Average distance = 2W / n(n-1) = 22/13."""
        avg = np.sum(D) / (_N * (_N - 1))
        assert abs(avg - 22.0 / 13.0) < 1e-10

    def test_eccentricity_uniform(self, D):
        """All eccentricities = 2  (connected diameter-2 SRG)."""
        for v in range(_N):
            assert int(np.max(D[v])) == 2

    def test_distance_symmetric(self, D):
        """D is symmetric."""
        assert np.allclose(D, D.T, atol=1e-14)


# ═════════════════════════════════════════════════════════════════════════════
# Section 5 : Spectral Dimension   (10 tests)
# d_s(t) = -2 d(ln P) / d(ln t),   P(t) = trace H(t) / n
# ═════════════════════════════════════════════════════════════════════════════

class TestSpectralDimension:

    @staticmethod
    def _P(t):
        """Return probability from known spectrum."""
        return (1.0 + 24.0 * np.exp(-10.0 * t) + 15.0 * np.exp(-16.0 * t)) / 40.0

    @staticmethod
    def _dP_dt(t):
        """dP/dt."""
        return (-240.0 * np.exp(-10.0 * t) - 240.0 * np.exp(-16.0 * t)) / 40.0

    def _spectral_dim(self, t):
        """d_s(t) = -2 t P'(t) / P(t)."""
        return -2.0 * t * self._dP_dt(t) / self._P(t)

    # -- tests --

    def test_return_prob_t0(self):
        """P(0) = 1."""
        assert abs(self._P(0.0) - 1.0) < 1e-14

    def test_return_prob_limit(self):
        """P(inf) -> 1/40."""
        assert abs(self._P(100.0) - 1.0 / 40.0) < 1e-14

    def test_return_prob_monotone_decreasing(self):
        """P(t) is strictly decreasing for t > 0."""
        ts = np.linspace(0.01, 5.0, 200)
        Ps = np.array([self._P(t) for t in ts])
        assert np.all(np.diff(Ps) < 1e-14)

    def test_return_prob_bounds(self):
        """1/40 <= P(t) <= 1 for all t >= 0."""
        for t in [0.0, 0.01, 0.1, 1.0, 10.0]:
            P = self._P(t)
            assert P >= 1.0 / 40.0 - 1e-14
            assert P <= 1.0 + 1e-14

    def test_spectral_dim_short_time_limit(self):
        """d_s(t) -> 0 as t -> 0+."""
        assert abs(self._spectral_dim(1e-6)) < 0.01

    def test_spectral_dim_long_time_limit(self):
        """d_s(t) -> 0 as t -> inf."""
        assert abs(self._spectral_dim(100.0)) < 1e-6

    def test_spectral_dim_positive_intermediate(self):
        """d_s(t) > 0 for intermediate t."""
        assert self._spectral_dim(0.1) > 0

    def test_spectral_dim_max_exists(self):
        """d_s has a positive maximum at some finite 0 < t < inf."""
        ts = np.linspace(0.001, 3.0, 2000)
        ds = np.array([self._spectral_dim(t) for t in ts])
        peak = np.max(ds)
        assert peak > 0
        idx = np.argmax(ds)
        assert 0 < idx < len(ts) - 1          # not at an endpoint

    def test_spectral_dim_from_matrix(self, L):
        """d_s from matrix exponentiation matches analytic formula."""
        t = 0.2
        vals, vecs = eigh(L)
        Ht = vecs @ np.diag(np.exp(-t * vals)) @ vecs.T
        P_mat = np.trace(Ht) / float(_N)
        assert abs(P_mat - self._P(t)) < 1e-10

    def test_spectral_dim_numerical_derivative(self):
        """d_s via finite differences matches analytic form."""
        t = 0.15
        dt = 1e-7
        lnP_plus = np.log(self._P(t + dt))
        lnP_minus = np.log(self._P(t - dt))
        lnt_plus = np.log(t + dt)
        lnt_minus = np.log(t - dt)
        ds_num = -2.0 * (lnP_plus - lnP_minus) / (lnt_plus - lnt_minus)
        ds_ana = self._spectral_dim(t)
        assert abs(ds_num - ds_ana) < 1e-4


# ═════════════════════════════════════════════════════════════════════════════
# Section 6 : Laplacian Variants   (11 tests)
# Normalized Laplacian, signless Laplacian, Bethe Hessian
# ═════════════════════════════════════════════════════════════════════════════

class TestLaplacianVariants:

    def test_normalized_laplacian_eigenvalues(self, A):
        """L_norm = I - D^{-1/2} A D^{-1/2}:  spectrum {0^1, (5/6)^24, (4/3)^15}."""
        Af = A.astype(float)
        D_inv_sqrt = np.eye(_N) / np.sqrt(float(_K))
        L_norm = np.eye(_N) - D_inv_sqrt @ Af @ D_inv_sqrt
        evals = np.sort(eigvalsh(L_norm))
        assert abs(evals[0]) < 1e-10
        for i in range(1, 25):
            assert abs(evals[i] - 5.0 / 6.0) < 1e-10
        for i in range(25, 40):
            assert abs(evals[i] - 4.0 / 3.0) < 1e-10

    def test_normalized_laplacian_trace(self, A):
        """trace(L_norm) = n = 40  (sum of eigenvalues: 0 + 24*5/6 + 15*4/3 = 40)."""
        Af = A.astype(float)
        D_inv_sqrt = np.eye(_N) / np.sqrt(float(_K))
        L_norm = np.eye(_N) - D_inv_sqrt @ Af @ D_inv_sqrt
        assert abs(np.trace(L_norm) - 40.0) < 1e-10

    def test_normalized_laplacian_max_less_than_2(self, A):
        """Largest L_norm eigenvalue = 4/3 < 2; equality holds iff bipartite."""
        Af = A.astype(float)
        D_inv_sqrt = np.eye(_N) / np.sqrt(float(_K))
        L_norm = np.eye(_N) - D_inv_sqrt @ Af @ D_inv_sqrt
        assert np.max(eigvalsh(L_norm)) < 2.0 - 0.1

    def test_signless_laplacian_eigenvalues(self, A):
        """Q = D + A:  spectrum {24^1, 14^24, 8^15}."""
        Q = float(_K) * np.eye(_N) + A.astype(float)
        evals = np.sort(eigvalsh(Q))
        for i in range(15):
            assert abs(evals[i] - 8.0) < 1e-8
        for i in range(15, 39):
            assert abs(evals[i] - 14.0) < 1e-8
        assert abs(evals[39] - 24.0) < 1e-8

    def test_signless_laplacian_trace(self, A):
        """trace(Q) = nk = 480."""
        Q = float(_K) * np.eye(_N) + A.astype(float)
        assert abs(np.trace(Q) - 480.0) < 1e-10

    def test_signless_laplacian_psd(self, A):
        """Q is positive semidefinite."""
        Q = float(_K) * np.eye(_N) + A.astype(float)
        assert np.all(eigvalsh(Q) >= -1e-10)

    def test_L_plus_Q_equals_2D(self, A, L):
        """L + Q = 2D = 2kI  for k-regular graphs."""
        Q = float(_K) * np.eye(_N) + A.astype(float)
        assert np.allclose(L + Q, 2.0 * float(_K) * np.eye(_N), atol=1e-10)

    def test_bethe_hessian_spectrum(self, A):
        """H_r = (r^2 - 1)I - rA  at r = sqrt(k-1) = sqrt(11)."""
        r = np.sqrt(float(_K) - 1.0)
        H_r = (r**2 - 1.0) * np.eye(_N) - r * A.astype(float)
        evals = np.sort(eigvalsh(H_r))
        # From A eigenvalues -4, 2, 12:
        ev_k = 10.0 - 12.0 * r      # most negative, mult 1
        ev_r = 10.0 - 2.0 * r       # mult 24
        ev_s = 10.0 + 4.0 * r       # mult 15
        assert abs(evals[0] - ev_k) < 1e-8
        for i in range(1, 25):
            assert abs(evals[i] - ev_r) < 1e-8
        for i in range(25, 40):
            assert abs(evals[i] - ev_s) < 1e-8

    def test_bethe_hessian_one_negative(self, A):
        """Exactly 1 negative eigenvalue of H_r -> 1 community."""
        r = np.sqrt(float(_K) - 1.0)
        H_r = (r**2 - 1.0) * np.eye(_N) - r * A.astype(float)
        assert np.sum(eigvalsh(H_r) < -1e-8) == 1

    def test_L_Q_trace_sum(self, A, L):
        """sum L_i + sum Q_i = 2nk = 960."""
        Q = float(_K) * np.eye(_N) + A.astype(float)
        assert abs(np.trace(L) + np.trace(Q) - 960.0) < 1e-8

    def test_L_Q_determinant_relation(self, A, L):
        """det(L) = 0  and  det(Q) > 0  (Q has no zero eigenvalue since A
        eigenvalue -k does not occur for connected non-bipartite graph)."""
        Q = float(_K) * np.eye(_N) + A.astype(float)
        evals_L = eigvalsh(L)
        evals_Q = eigvalsh(Q)
        assert np.min(np.abs(evals_L)) < 1e-8          # L has zero eigenvalue
        assert np.min(evals_Q) > 1e-2                   # Q is positive definite


# ═════════════════════════════════════════════════════════════════════════════
# Section 7 : Isoperimetric Properties   (10 tests)
# Cheeger bounds, expansion, Hoffman bound
# ═════════════════════════════════════════════════════════════════════════════

class TestIsoperimetricProperties:

    def test_algebraic_connectivity(self, lap_eigenvalues):
        """lambda_2(L) = 10."""
        assert abs(lap_eigenvalues[1] - 10.0) < 1e-8

    def test_spectral_gap(self, adj_eigenvalues):
        """Spectral gap = k - lambda_2(A) = 12 - 2 = 10."""
        evals = adj_eigenvalues[::-1]
        assert abs(evals[0] - evals[1] - 10.0) < 1e-8

    def test_cheeger_lower_bound(self, lap_eigenvalues):
        """Discrete Cheeger: h >= lambda_2 / 2 = 5."""
        # We verify the *bound* value, not h itself.
        assert lap_eigenvalues[1] / 2.0 >= 5.0 - 1e-10

    def test_expansion_lower_bound_from_spectrum(self, adj_eigenvalues):
        """Edge expansion h >= (k - lambda*) / 2  where
        lambda* = max(|r|, |s|) = 4.  So h >= 4."""
        evals = adj_eigenvalues[::-1]
        lam_star = max(abs(evals[1]), abs(evals[-1]))
        assert abs(lam_star - 4.0) < 1e-8
        assert (float(_K) - lam_star) / 2.0 >= 4.0 - 1e-10

    def test_edge_expansion_single_vertex(self, A):
        """Single vertex: |boundary| / |S| = k = 12."""
        assert np.sum(A[0]) == _K

    def test_edge_expansion_adjacent_pair(self, A):
        """Adjacent pair {u,v}: edge boundary = 22  (each vertex sends 11 out)."""
        u = 0
        v = int(np.where(A[0] == 1)[0][0])
        S = {u, v}
        boundary = sum(1 for x in S for y in range(_N) if y not in S and A[x, y])
        assert boundary == 22

    def test_edge_expansion_4clique(self, A):
        """A 4-clique (line of W(3)): edge boundary = 36."""
        # Find a 4-clique: four mutually adjacent vertices
        clique = None
        for i in range(_N):
            ni = set(np.where(A[i] == 1)[0])
            for j in ni:
                if j <= i:
                    continue
                common_ij = ni & set(np.where(A[j] == 1)[0])
                for c in common_ij:
                    if c <= j:
                        continue
                    # {i,j,c} triangle -- look for 4th vertex adjacent to all
                    common_ijc = ni & set(np.where(A[j] == 1)[0]) & set(np.where(A[c] == 1)[0])
                    for d in common_ijc:
                        if d > c:
                            clique = [i, j, c, d]
                            break
                    if clique:
                        break
                if clique:
                    break
            if clique:
                break
        assert clique is not None
        S = set(clique)
        boundary = sum(1 for x in S for y in range(_N) if y not in S and A[x, y])
        assert boundary == 36     # 4 * (12 - 3)

    def test_hoffman_bound(self):
        """Hoffman bound: alpha(G) <= n (-s) / (k - s) = 40*4/16 = 10."""
        bound = _N * 4.0 / (float(_K) + 4.0)
        assert abs(bound - 10.0) < 1e-10

    def test_chromatic_lower_bound(self):
        """Hoffman chromatic bound: chi >= 1 + k/(-s) = 1 + 12/4 = 4."""
        chi_lower = 1.0 + float(_K) / 4.0
        assert abs(chi_lower - 4.0) < 1e-10

    def test_expander_mixing_lemma(self, A):
        """For S = {0,..,9},  |e(S,Sc) - k|S||Sc|/n| <= lam* sqrt(|S||Sc|)
        with lam* = max(|r|,|s|) = 4."""
        S = list(range(10))
        Sc = list(range(10, _N))
        e_cross = sum(int(A[i, j]) for i in S for j in Sc)
        expected = float(_K) * 10.0 * 30.0 / float(_N)       # 90
        bound = 4.0 * np.sqrt(10.0 * 30.0)
        assert abs(e_cross - expected) <= bound + 1e-8


# ═════════════════════════════════════════════════════════════════════════════
# Section 8 : Spectral Embedding Geometry   (9 tests)
# Fiedler coordinates, spectral distances, pseudoinverse trace
# ═════════════════════════════════════════════════════════════════════════════

class TestSpectralEmbedding:

    @pytest.fixture(scope="class")
    def fiedler_data(self, L):
        """Eigenvectors for eigenvalue 10 (multiplicity 24)."""
        vals, vecs = eigh(L)
        idx = np.where(np.abs(vals - 10.0) < 0.5)[0]
        return vecs[:, idx]

    def test_fiedler_value(self, lap_eigenvalues):
        """Fiedler value (algebraic connectivity) = 10."""
        assert abs(lap_eigenvalues[1] - 10.0) < 1e-8

    def test_fiedler_multiplicity_24(self, L):
        """Multiplicity of the Fiedler eigenvalue = 24."""
        vals = eigvalsh(L)
        assert np.sum(np.abs(vals - 10.0) < 0.5) == 24

    def test_distinct_nonzero_eigenvalues(self, L):
        """Exactly 2 distinct nonzero Laplacian eigenvalues: 10 and 16."""
        vals = eigvalsh(L)
        nonzero = vals[vals > 1e-8]
        unique = np.unique(np.round(nonzero, 6))
        assert len(unique) == 2
        assert abs(unique[0] - 10.0) < 1e-4
        assert abs(unique[1] - 16.0) < 1e-4

    def test_fiedler_orthonormality(self, fiedler_data):
        """Fiedler eigenvectors are orthonormal."""
        G = fiedler_data.T @ fiedler_data
        assert np.allclose(G, np.eye(G.shape[0]), atol=1e-10)

    def test_fiedler_orthogonal_to_ones(self, fiedler_data):
        """Fiedler coordinates sum to zero (perp to constant eigenvector)."""
        col_sums = np.sum(fiedler_data, axis=0)
        assert np.allclose(col_sums, 0.0, atol=1e-10)

    def test_spectral_radius(self, adj_eigenvalues):
        """Spectral radius rho(A) = k = 12."""
        assert abs(np.max(np.abs(adj_eigenvalues)) - 12.0) < 1e-8

    def test_spectral_distance_adj_lt_nonadj(self, L, A):
        """Mean commute-time spectral distance: adjacent < non-adjacent."""
        vals, vecs = eigh(L)
        nz = vals > 1e-8
        coords = vecs[:, nz] / np.sqrt(vals[nz])      # weighted embedding
        adj_d, nonadj_d = [], []
        for i in range(20):
            for j in range(i + 1, _N):
                d = float(norm(coords[i] - coords[j]))
                (adj_d if A[i, j] else nonadj_d).append(d)
        assert np.mean(adj_d) < np.mean(nonadj_d)

    def test_embedding_equal_norms(self, fiedler_data):
        """Vertex-transitivity => all vertices have the same norm in the
        Fiedler (eigenvalue-10) eigenspace."""
        norms = np.array([float(norm(fiedler_data[i])) for i in range(_N)])
        assert np.allclose(norms, norms[0], atol=1e-10)

    def test_pseudoinverse_trace(self, L):
        """trace(L^+) = zeta_L(1) = 267/80."""
        vals, vecs = eigh(L)
        nz = vals > 1e-8
        trace_Lp = np.sum(1.0 / vals[nz])
        assert abs(trace_Lp - 267.0 / 80.0) < 1e-8
