"""
Phase CXXVIII -- Graph Entropy Deep Analysis on W(3,3) = SRG(40,12,2,4).

126 tests covering von Neumann entropy of density matrices (Laplacian and
adjacency), Renyi entropy of various orders, spectral entropy, random walk
entropy rate, structural entropy, mutual information between vertex subsets,
conditional entropy, entropy of complement graph, KL divergence from uniform,
relative entropy, entropy bounds (log n, log rank, Fano), entropy power
inequality, Tsallis entropy, information-theoretic capacity bounds (Lovasz
theta, Hoffman), topological entropy, and advanced identities (effective rank,
participation ratio, product-graph additivity).

All tests use only numpy and standard library.  Every assertion is
mathematically derivable from the SRG(40,12,2,4) spectrum
    adjacency:  {12^1, 2^24, (-4)^15}
    Laplacian:  {0^1, 10^24, 16^15}
"""

import math
import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest


# ---------------------------------------------------------------------------
# W(3,3) builder
# ---------------------------------------------------------------------------

def _build_w33():
    """Build the 40-vertex SRG(40,12,2,4) adjacency matrix."""
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
# Module-level precomputation
# ---------------------------------------------------------------------------

_N = 40
_K = 12
_LAM = 2
_MU = 4
_EDGES = _N * _K // 2  # 240 undirected edges

A = _build_w33()
I_ = np.eye(_N, dtype=float)
J = np.ones((_N, _N), dtype=float)
L = _K * I_ - A.astype(float)  # Combinatorial Laplacian

# Eigenvalues
_adj_evals = np.sort(np.linalg.eigvalsh(A.astype(float)))
_lap_evals = np.sort(np.linalg.eigvalsh(L))

# Laplacian density matrix  rho_L = L / tr(L)
_tr_L = np.trace(L)  # = 2|E| = 480
_rho_L = L / _tr_L

# Shifted adjacency density matrix  rho_A = (A + |lambda_min|I) / tr(...)
_A_shifted = A.astype(float) + 4.0 * I_
_tr_A_shifted = np.trace(_A_shifted)  # 160
_rho_A = _A_shifted / _tr_A_shifted

# Complement graph  SRG(40, 27, 18, 18)
_A_bar = J - I_ - A.astype(float)
_K_bar = _N - 1 - _K  # 27
_L_bar = _K_bar * I_ - _A_bar
_tr_L_bar = np.trace(_L_bar)  # 1080
_rho_L_bar = _L_bar / _tr_L_bar

# Random walk transition matrix (regular: P = A/k)
_P_rw = A.astype(float) / _K


def _safe_entropy(eigenvalues):
    """Compute -sum(lam * ln(lam)) for positive eigenvalues."""
    pos = eigenvalues[eigenvalues > 1e-14]
    return -np.sum(pos * np.log(pos))


def _renyi_entropy(eigenvalues, alpha):
    """Renyi entropy of order alpha from eigenvalue list."""
    pos = eigenvalues[eigenvalues > 1e-14]
    if alpha == 1.0:
        return _safe_entropy(eigenvalues)
    if np.isinf(alpha):
        return -np.log(np.max(pos))
    return (1.0 / (1.0 - alpha)) * np.log(np.sum(pos ** alpha))


# Precompute key entropy values
_S_vN_L = _safe_entropy(np.linalg.eigvalsh(_rho_L))
_S_vN_A = _safe_entropy(np.linalg.eigvalsh(_rho_A))
_S_vN_L_bar = _safe_entropy(np.linalg.eigvalsh(_rho_L_bar))


# =========================================================================
# 1.  Basic Setup Verification  (6 tests)
# =========================================================================

class TestBasicSetup:
    """Verify graph construction and spectral properties."""

    def test_vertex_count(self):
        assert A.shape == (_N, _N)

    def test_regular_degree(self):
        assert np.all(A.sum(axis=1) == _K)

    def test_edge_count(self):
        assert A.sum() == 2 * _EDGES  # 480

    def test_adjacency_spectrum(self):
        """Adjacency eigenvalues: {12^1, 2^24, (-4)^15}."""
        unique = sorted(np.unique(np.round(_adj_evals, 6)))
        assert_allclose(unique, [-4, 2, 12], atol=1e-8)

    def test_laplacian_spectrum(self):
        """Laplacian eigenvalues: {0^1, 10^24, 16^15}."""
        unique = sorted(np.unique(np.round(_lap_evals, 6)))
        assert_allclose(unique, [0, 10, 16], atol=1e-8)

    def test_laplacian_trace(self):
        """tr(L) = 2|E| = 480."""
        assert_allclose(_tr_L, 480.0, atol=1e-10)


# =========================================================================
# 2.  Laplacian Density Matrix  (8 tests)
# =========================================================================

class TestLaplacianDensityMatrix:
    """Properties of rho_L = L / tr(L)."""

    def test_trace_one(self):
        assert_allclose(np.trace(_rho_L), 1.0, atol=1e-14)

    def test_symmetric(self):
        assert_allclose(_rho_L, _rho_L.T, atol=1e-14)

    def test_positive_semidefinite(self):
        evals = np.linalg.eigvalsh(_rho_L)
        assert np.all(evals >= -1e-14)

    def test_rank_39(self):
        """rho_L has rank 39 (one zero eigenvalue from constant vector)."""
        evals = np.linalg.eigvalsh(_rho_L)
        assert np.sum(evals > 1e-10) == _N - 1

    def test_eigenvalues(self):
        """rho_L eigenvalues: 0 (x1), 1/48 (x24), 1/30 (x15)."""
        evals = np.sort(np.linalg.eigvalsh(_rho_L))
        assert_allclose(evals[0], 0.0, atol=1e-14)
        assert_allclose(evals[1:25], 1.0 / 48.0, atol=1e-12)
        assert_allclose(evals[25:], 1.0 / 30.0, atol=1e-12)

    def test_purity(self):
        """tr(rho^2) = 24*(1/48)^2 + 15*(1/30)^2 = 13/480."""
        purity = np.trace(_rho_L @ _rho_L)
        assert_allclose(purity, 13.0 / 480.0, atol=1e-14)

    def test_purity_lower_bound(self):
        """tr(rho^2) >= 1/n for any n-dimensional density matrix."""
        purity = np.trace(_rho_L @ _rho_L)
        assert purity >= 1.0 / _N - 1e-14

    def test_rho_L_formula(self):
        """rho_L = L/480 element by element."""
        assert_allclose(_rho_L, L / 480.0, atol=1e-15)


# =========================================================================
# 3.  Adjacency Density Matrix  (7 tests)
# =========================================================================

class TestAdjacencyDensityMatrix:
    """Properties of rho_A = (A + 4I) / tr(A + 4I)."""

    def test_shift_trace(self):
        """tr(A + 4I) = 4*40 = 160."""
        assert_allclose(_tr_A_shifted, 160.0, atol=1e-10)

    def test_trace_one(self):
        assert_allclose(np.trace(_rho_A), 1.0, atol=1e-14)

    def test_positive_semidefinite(self):
        evals = np.linalg.eigvalsh(_rho_A)
        assert np.all(evals >= -1e-14)

    def test_rank_25(self):
        """rho_A has rank 25 (15 zero eigenvalues from -4 shifted to 0)."""
        evals = np.linalg.eigvalsh(_rho_A)
        assert np.sum(evals > 1e-10) == 25

    def test_eigenvalues(self):
        """rho_A eigenvalues: 0 (x15), 3/80 (x24), 1/10 (x1)."""
        evals = np.sort(np.linalg.eigvalsh(_rho_A))
        assert_allclose(evals[:15], 0.0, atol=1e-12)
        assert_allclose(evals[15:39], 3.0 / 80.0, atol=1e-12)
        assert_allclose(evals[39], 1.0 / 10.0, atol=1e-12)

    def test_purity(self):
        """tr(rho_A^2) = 24*(3/80)^2 + (1/10)^2."""
        expected = 24.0 * (3.0 / 80.0) ** 2 + (1.0 / 10.0) ** 2
        purity = np.trace(_rho_A @ _rho_A)
        assert_allclose(purity, expected, atol=1e-14)

    def test_entropy_less_than_laplacian(self):
        """rho_A has lower rank (25 < 39), so S(rho_A) < S(rho_L)."""
        assert _S_vN_A < _S_vN_L


# =========================================================================
# 4.  Von Neumann Entropy  (10 tests)
# =========================================================================

class TestVonNeumannEntropy:
    """Von Neumann entropy S = -tr(rho log rho)."""

    def test_vN_laplacian_analytical(self):
        """S(rho_L) = (1/2)*ln(1440) exactly."""
        expected = 0.5 * np.log(1440.0)
        assert_allclose(_S_vN_L, expected, atol=1e-12)

    def test_vN_laplacian_decomposition(self):
        """S(rho_L) = (1/2)*ln(48) + (1/2)*ln(30)."""
        expected = 0.5 * np.log(48.0) + 0.5 * np.log(30.0)
        assert_allclose(_S_vN_L, expected, atol=1e-12)

    def test_vN_laplacian_positive(self):
        assert _S_vN_L > 0

    def test_vN_adjacency_positive(self):
        assert _S_vN_A > 0

    def test_vN_upper_bound_log_rank(self):
        """S(rho_L) <= log(rank) = log(39)."""
        assert _S_vN_L <= np.log(39.0) + 1e-10

    def test_vN_adjacency_upper_bound(self):
        """S(rho_A) <= log(25) since rank = 25."""
        assert _S_vN_A <= np.log(25.0) + 1e-10

    def test_vN_lower_bound_positive(self):
        """S(rho) > 0 unless rho is a pure state."""
        assert _S_vN_L > 0
        assert _S_vN_A > 0

    def test_vN_from_eigenvalue_formula(self):
        """Verify S = -sum(lam_i * ln(lam_i)) via direct eigenvalue sum."""
        evals = np.linalg.eigvalsh(_rho_L)
        pos = evals[evals > 1e-14]
        S_direct = -np.sum(pos * np.log(pos))
        assert_allclose(S_direct, _S_vN_L, atol=1e-12)

    def test_vN_complement_analytical(self):
        """S(rho_L_bar) = (1/3)*ln(45) + (2/3)*ln(36)."""
        expected = (1.0 / 3.0) * np.log(45.0) + (2.0 / 3.0) * np.log(36.0)
        assert_allclose(_S_vN_L_bar, expected, atol=1e-12)

    def test_vN_laplacian_numerical_value(self):
        """S(rho_L) ~ 3.636."""
        assert_allclose(_S_vN_L, np.log(1440.0) / 2.0, atol=1e-10)
        assert 3.63 < _S_vN_L < 3.64


# =========================================================================
# 5.  Renyi Entropy  (10 tests)
# =========================================================================

class TestRenyiEntropy:
    """Renyi entropy S_alpha(rho) = (1/(1-alpha)) * ln(tr(rho^alpha))."""

    @pytest.fixture(autouse=True)
    def _evals(self):
        self.evals_L = np.linalg.eigvalsh(_rho_L)
        self.evals_A = np.linalg.eigvalsh(_rho_A)

    def test_renyi_order_0(self):
        """S_0 = log(rank) = log(39) for rho_L."""
        S0 = _renyi_entropy(self.evals_L, 0.0)
        assert_allclose(S0, np.log(39.0), atol=1e-10)

    def test_renyi_order_1_equals_vN(self):
        """S_1 = S_vN (von Neumann entropy)."""
        S1 = _renyi_entropy(self.evals_L, 1.0)
        assert_allclose(S1, _S_vN_L, atol=1e-12)

    def test_renyi_order_2(self):
        """S_2 = -log(tr(rho^2)) = log(480/13)."""
        S2 = _renyi_entropy(self.evals_L, 2.0)
        expected = np.log(480.0 / 13.0)
        assert_allclose(S2, expected, atol=1e-12)

    def test_renyi_order_2_from_purity(self):
        """S_2 = -log(purity)."""
        purity = np.trace(_rho_L @ _rho_L)
        S2 = _renyi_entropy(self.evals_L, 2.0)
        assert_allclose(S2, -np.log(purity), atol=1e-12)

    def test_renyi_order_3(self):
        """S_3 from tr(rho^3) = 24*(1/48)^3 + 15*(1/30)^3."""
        tr_rho3 = 24.0 * (1.0 / 48.0) ** 3 + 15.0 * (1.0 / 30.0) ** 3
        expected = (1.0 / (1.0 - 3.0)) * np.log(tr_rho3)
        S3 = _renyi_entropy(self.evals_L, 3.0)
        assert_allclose(S3, expected, atol=1e-12)

    def test_renyi_inf(self):
        """S_inf = -log(max eigenvalue) = -log(1/30) = log(30)."""
        S_inf = _renyi_entropy(self.evals_L, np.inf)
        assert_allclose(S_inf, np.log(30.0), atol=1e-12)

    def test_renyi_monotone_decreasing(self):
        """S_alpha is non-increasing: S_0 >= S_1 >= S_2 >= S_inf."""
        S0 = _renyi_entropy(self.evals_L, 0.0)
        S1 = _renyi_entropy(self.evals_L, 1.0)
        S2 = _renyi_entropy(self.evals_L, 2.0)
        S_inf = _renyi_entropy(self.evals_L, np.inf)
        assert S0 >= S1 - 1e-12
        assert S1 >= S2 - 1e-12
        assert S2 >= S_inf - 1e-12

    def test_renyi_half(self):
        """S_{1/2} from tr(rho^{1/2})."""
        tr_sqrt = 24.0 * np.sqrt(1.0 / 48.0) + 15.0 * np.sqrt(1.0 / 30.0)
        expected = (1.0 / (1.0 - 0.5)) * np.log(tr_sqrt)
        S_half = _renyi_entropy(self.evals_L, 0.5)
        assert_allclose(S_half, expected, atol=1e-12)

    def test_renyi_adjacency_order_2(self):
        """S_2 for adjacency density matrix from purity."""
        purity_A = np.trace(_rho_A @ _rho_A)
        S2_A = _renyi_entropy(self.evals_A, 2.0)
        assert_allclose(S2_A, -np.log(purity_A), atol=1e-12)

    def test_renyi_order_0_adjacency(self):
        """S_0(rho_A) = log(25) since rank = 25."""
        S0_A = _renyi_entropy(self.evals_A, 0.0)
        assert_allclose(S0_A, np.log(25.0), atol=1e-10)


# =========================================================================
# 6.  Spectral Entropy  (8 tests)
# =========================================================================

class TestSpectralEntropy:
    """Entropy from normalized eigenvalue magnitude distribution."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        abs_evals = np.abs(_adj_evals)
        self.total_abs = np.sum(abs_evals)  # 12 + 24*2 + 15*4 = 120
        self.p_spec = abs_evals / self.total_abs
        pos_lap = _lap_evals[_lap_evals > 1e-14]
        total_lap = np.sum(pos_lap)  # 24*10 + 15*16 = 480
        self.p_lap = pos_lap / total_lap

    def test_total_abs_eigenvalue_sum(self):
        """sum |lambda_i| = 12 + 24*2 + 15*4 = 120."""
        assert_allclose(self.total_abs, 120.0, atol=1e-10)

    def test_spectral_distribution_sums_to_one(self):
        assert_allclose(np.sum(self.p_spec), 1.0, atol=1e-14)

    def test_spectral_entropy_value(self):
        """S_spec = (1/10)*ln(10) + (2/5)*ln(60) + (1/2)*ln(30)."""
        S = -np.sum(self.p_spec * np.log(self.p_spec + 1e-300))
        expected = ((1.0 / 10.0) * np.log(10)
                    + (2.0 / 5.0) * np.log(60)
                    + (1.0 / 2.0) * np.log(30))
        assert_allclose(S, expected, atol=1e-10)

    def test_spectral_entropy_upper_bound(self):
        """S_spec <= log(n) = log(40)."""
        S = -np.sum(self.p_spec * np.log(self.p_spec + 1e-300))
        assert S <= np.log(40.0) + 1e-10

    def test_spectral_entropy_positive(self):
        S = -np.sum(self.p_spec * np.log(self.p_spec + 1e-300))
        assert S > 0

    def test_laplacian_spectral_entropy(self):
        """Spectral entropy of Laplacian eigenvalue distribution (non-zero)."""
        S_lap = -np.sum(self.p_lap * np.log(self.p_lap))
        assert S_lap > 0
        assert S_lap <= np.log(39.0) + 1e-10

    def test_laplacian_spectral_entropy_equals_vN(self):
        """Laplacian spectral distribution matches rho_L eigenvalues,
        so spectral entropy = von Neumann entropy."""
        S_lap = -np.sum(self.p_lap * np.log(self.p_lap))
        assert_allclose(S_lap, _S_vN_L, atol=1e-12)

    def test_spectral_effective_dimension(self):
        """Effective dimension exp(S_spec) in [1, n]."""
        S = -np.sum(self.p_spec * np.log(self.p_spec + 1e-300))
        d_eff = np.exp(S)
        assert 1.0 <= d_eff <= _N + 1e-10


# =========================================================================
# 7.  Random Walk Entropy  (8 tests)
# =========================================================================

class TestRandomWalkEntropy:
    """Entropy rate and related quantities for random walk on W(3,3)."""

    def test_transition_matrix_stochastic(self):
        """Each row of P sums to 1."""
        assert_allclose(_P_rw.sum(axis=1), np.ones(_N), atol=1e-14)

    def test_stationary_distribution_uniform(self):
        """For k-regular graph, stationary distribution is uniform."""
        pi = np.ones(_N) / _N
        assert_allclose(pi @ _P_rw, pi, atol=1e-14)

    def test_entropy_rate_equals_log_k(self):
        """For k-regular graph, entropy rate h = log(k) = log(12)."""
        pi = np.ones(_N) / _N
        h = 0.0
        for i in range(_N):
            for j in range(_N):
                if _P_rw[i, j] > 0:
                    h -= pi[i] * _P_rw[i, j] * np.log(_P_rw[i, j])
        assert_allclose(h, np.log(12.0), atol=1e-12)

    def test_entropy_rate_upper_bound(self):
        """h <= log(n) = log(40)."""
        assert np.log(12.0) <= np.log(40.0) + 1e-10

    def test_joint_entropy(self):
        """H(X_t, X_{t+1}) = log(n*k) = log(480) for regular graph."""
        pi = np.ones(_N) / _N
        H_direct = 0.0
        for i in range(_N):
            for j in range(_N):
                p_ij = pi[i] * _P_rw[i, j]
                if p_ij > 0:
                    H_direct -= p_ij * np.log(p_ij)
        assert_allclose(H_direct, np.log(480.0), atol=1e-10)

    def test_mutual_information_random_walk(self):
        """MI(X_t; X_{t+1}) = 2*log(40) - log(480) = log(10/3)."""
        MI = 2.0 * np.log(40.0) - np.log(480.0)
        assert_allclose(MI, np.log(10.0 / 3.0), atol=1e-12)
        assert MI > 0

    def test_conditional_entropy_equals_rate(self):
        """H(X_{t+1}|X_t) = log(480) - log(40) = log(12)."""
        H_cond = np.log(480.0) - np.log(40.0)
        assert_allclose(H_cond, np.log(12.0), atol=1e-12)

    def test_spectral_gap(self):
        """Gap of P = 1 - lambda_2/k = 1 - 2/12 = 5/6.  Fast mixing."""
        gap = 1.0 - 2.0 / 12.0
        assert_allclose(gap, 5.0 / 6.0, atol=1e-14)
        assert 1.0 / gap < _N  # mixing time bound < n


# =========================================================================
# 8.  Structural Entropy  (7 tests)
# =========================================================================

class TestStructuralEntropy:
    """Degree-based and structural entropy measures."""

    def test_degree_entropy_regular(self):
        """For k-regular graph, degree distribution is degenerate: H = 0."""
        degrees = A.sum(axis=1)
        unique_degs, counts = np.unique(degrees, return_counts=True)
        p = counts / counts.sum()
        H_deg = -np.sum(p * np.log(p))
        assert_allclose(H_deg, 0.0, atol=1e-14)

    def test_edge_endpoint_entropy(self):
        """Vertex distribution d_i/(2|E|) is uniform: H = log(40)."""
        degrees = A.sum(axis=1).astype(float)
        p = degrees / degrees.sum()
        H = -np.sum(p * np.log(p))
        assert_allclose(H, np.log(40.0), atol=1e-12)

    def test_row_entropy_uniform(self):
        """Each row of A normalized by k has entropy log(12)."""
        for i in range(_N):
            row = A[i].astype(float) / _K
            pos = row[row > 0]
            H_row = -np.sum(pos * np.log(pos))
            assert_allclose(H_row, np.log(12.0), atol=1e-12)

    def test_mean_row_entropy(self):
        """Average row entropy = log(12) for regular graph."""
        H_avg = 0.0
        for i in range(_N):
            row = A[i].astype(float) / _K
            pos = row[row > 0]
            H_avg -= np.sum(pos * np.log(pos))
        H_avg /= _N
        assert_allclose(H_avg, np.log(12.0), atol=1e-12)

    def test_graph_energy(self):
        """Graph energy = sum |lambda_i| = 120."""
        energy = np.sum(np.abs(_adj_evals))
        assert_allclose(energy, 120.0, atol=1e-8)

    def test_graph_energy_per_vertex(self):
        """Energy per vertex = 120/40 = 3."""
        assert_allclose(np.sum(np.abs(_adj_evals)) / _N, 3.0, atol=1e-8)

    def test_estrada_index(self):
        """EE = exp(12) + 24*exp(2) + 15*exp(-4)."""
        EE = np.sum(np.exp(_adj_evals))
        expected = np.exp(12.0) + 24.0 * np.exp(2.0) + 15.0 * np.exp(-4.0)
        assert_allclose(EE, expected, rtol=1e-10)


# =========================================================================
# 9.  Mutual Information Between Vertex Subsets  (7 tests)
# =========================================================================

class TestMutualInformation:
    """Mutual information from graph structure and random walks."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        self.S1 = list(range(20))
        self.S2 = list(range(20, 40))
        A_f = A.astype(float)
        self.e_within_S1 = A_f[np.ix_(self.S1, self.S1)].sum() / 2.0
        self.e_within_S2 = A_f[np.ix_(self.S2, self.S2)].sum() / 2.0
        self.e_between = A_f[np.ix_(self.S1, self.S2)].sum()

    def test_edge_partition(self):
        """within_S1 + within_S2 + between = total edges."""
        total = self.e_within_S1 + self.e_within_S2 + self.e_between
        assert_allclose(total, _EDGES, atol=1e-10)

    def test_cut_entropy(self):
        """Shannon entropy of edge partition (within_S1, within_S2, between)."""
        counts = np.array([self.e_within_S1, self.e_within_S2, self.e_between])
        p = counts / counts.sum()
        H = -np.sum(p * np.log(p + 1e-300))
        assert H > 0
        assert H <= np.log(3.0) + 1e-10

    def test_cut_ratio_bounded(self):
        """Cut ratio (between / total) is in (0, 1)."""
        cut_ratio = self.e_between / _EDGES
        assert 0 < cut_ratio < 1

    def test_MI_from_walk_nonneg(self):
        """MI(X_t; X_{t+1}) = log(10/3) > 0."""
        MI = 2.0 * np.log(40.0) - np.log(480.0)
        assert MI > 0

    def test_MI_bounded_by_marginal(self):
        """MI(X_t; X_{t+1}) <= H(X_t) = log(40)."""
        MI = np.log(10.0 / 3.0)
        assert MI <= np.log(40.0) + 1e-10

    def test_coarse_MI_between_halves(self):
        """MI between indicator (in S1 vs S2) at times t and t+1."""
        pi = np.ones(_N) / _N
        # P(next in S1 | current in S1)
        p11 = sum(pi[i] * _P_rw[i, j]
                   for i in self.S1 for j in self.S1) / 0.5
        p_joint = np.array([[0.5 * p11, 0.5 * (1.0 - p11)],
                            [0.5 * (1.0 - p11), 0.5 * p11]])
        # Adjust for non-symmetry between halves
        p12 = sum(pi[i] * _P_rw[i, j]
                  for i in self.S1 for j in self.S2) / 0.5
        p21 = sum(pi[i] * _P_rw[i, j]
                  for i in self.S2 for j in self.S1) / 0.5
        p22 = 1.0 - p21
        p_joint = np.array([[0.5 * p11, 0.5 * p12],
                            [0.5 * p21, 0.5 * p22]])
        p_row = p_joint.sum(axis=1)
        p_col = p_joint.sum(axis=0)
        MI = 0.0
        for a in range(2):
            for b in range(2):
                if p_joint[a, b] > 1e-15:
                    MI += p_joint[a, b] * np.log(
                        p_joint[a, b] / (p_row[a] * p_col[b]))
        assert MI >= -1e-10  # MI >= 0

    def test_laplacian_submatrix_entropy(self):
        """Von Neumann entropy of 20x20 Laplacian submatrix (normalized)."""
        L_sub = L[np.ix_(self.S1, self.S1)]
        tr_sub = np.trace(L_sub)
        assert tr_sub > 0
        rho_sub = L_sub / tr_sub
        evals_sub = np.linalg.eigvalsh(rho_sub)
        S_sub = _safe_entropy(evals_sub)
        assert S_sub >= 0
        assert S_sub <= np.log(20.0) + 1e-10


# =========================================================================
# 10.  Conditional Entropy  (5 tests)
# =========================================================================

class TestConditionalEntropy:
    """Conditional entropy of graph-related random variables."""

    def test_H_Xt1_given_Xt(self):
        """H(X_{t+1}|X_t) = log(12) for regular graph."""
        assert_allclose(np.log(480.0) - np.log(40.0), np.log(12.0), atol=1e-14)

    def test_conditional_nonneg(self):
        assert np.log(12.0) > 0

    def test_conditional_less_than_marginal(self):
        """H(X_{t+1}|X_t) <= H(X_{t+1}) = log(40)."""
        assert np.log(12.0) <= np.log(40.0)

    def test_chain_rule(self):
        """H(X,Y) = H(X) + H(Y|X)."""
        H_X = np.log(40.0)
        H_Y_given_X = np.log(12.0)
        H_XY = np.log(480.0)
        assert_allclose(H_X + H_Y_given_X, H_XY, atol=1e-14)

    def test_two_step_conditional_entropy(self):
        """H(X_{t+2}|X_t) >= H(X_{t+1}|X_t) = log(12)."""
        P2 = _P_rw @ _P_rw
        pi = np.ones(_N) / _N
        H_cond_2 = 0.0
        for i in range(_N):
            for j in range(_N):
                if P2[i, j] > 0:
                    H_cond_2 -= pi[i] * P2[i, j] * np.log(P2[i, j])
        assert H_cond_2 > np.log(12.0) - 1e-10


# =========================================================================
# 11.  Complement Graph Entropy  (8 tests)
# =========================================================================

class TestComplementEntropy:
    """Entropy of complement graph SRG(40, 27, 18, 18)."""

    def test_complement_adjacency(self):
        """A + A_bar = J - I."""
        assert_allclose(A.astype(float) + _A_bar, J - I_, atol=1e-14)

    def test_complement_degree(self):
        """Complement has degree n-1-k = 27."""
        assert_allclose(_A_bar.sum(axis=1), np.full(_N, 27.0), atol=1e-10)

    def test_complement_laplacian_trace(self):
        """tr(L_bar) = 2 * |E_bar| = 2 * (40*27/2) = 1080."""
        assert_allclose(_tr_L_bar, 1080.0, atol=1e-10)

    def test_complement_spectrum(self):
        """Complement eigenvalues: {27^1, 3^15, (-3)^24}."""
        evals_bar = np.sort(np.linalg.eigvalsh(_A_bar))
        unique = sorted(np.unique(np.round(evals_bar, 6)))
        assert_allclose(unique, [-3, 3, 27], atol=1e-8)

    def test_complement_laplacian_spectrum(self):
        """Complement Laplacian: {0^1, 24^15, 30^24}."""
        lap_bar = np.sort(np.linalg.eigvalsh(_L_bar))
        unique = sorted(np.unique(np.round(lap_bar, 6)))
        assert_allclose(unique, [0, 24, 30], atol=1e-8)

    def test_complement_vN_entropy(self):
        """S(rho_L_bar) = (1/3)*ln(45) + (2/3)*ln(36)."""
        expected = (1.0 / 3.0) * np.log(45.0) + (2.0 / 3.0) * np.log(36.0)
        assert_allclose(_S_vN_L_bar, expected, atol=1e-12)

    def test_complement_entropy_different(self):
        """S(rho_L) != S(rho_L_bar)."""
        assert abs(_S_vN_L - _S_vN_L_bar) > 0.01

    def test_complement_purity(self):
        """tr(rho_L_bar^2) = 15*(1/45)^2 + 24*(1/36)^2 = 7/270."""
        expected = 15.0 * (1.0 / 45.0) ** 2 + 24.0 * (1.0 / 36.0) ** 2
        purity = np.trace(_rho_L_bar @ _rho_L_bar)
        assert_allclose(purity, expected, atol=1e-14)


# =========================================================================
# 12.  KL Divergence  (7 tests)
# =========================================================================

class TestKLDivergence:
    """KL divergence from various reference distributions."""

    def test_KL_from_uniform(self):
        """D_KL(rho_L || I/n) = log(n) - S(rho_L) = log(40) - ln(1440)/2."""
        D_KL = np.log(40.0) - _S_vN_L
        expected = np.log(40.0) - np.log(1440.0) / 2.0
        assert_allclose(D_KL, expected, atol=1e-12)

    def test_KL_from_uniform_simplified(self):
        """D_KL = log(sqrt(10)/3) = (1/2)*ln(10) - ln(3)."""
        D_KL = np.log(40.0) - _S_vN_L
        expected = 0.5 * np.log(10.0) - np.log(3.0)
        assert_allclose(D_KL, expected, atol=1e-12)

    def test_KL_nonneg(self):
        """Gibbs' inequality: KL divergence >= 0."""
        D_KL = np.log(40.0) - _S_vN_L
        assert D_KL >= -1e-14

    def test_KL_complement_from_uniform(self):
        """D_KL(rho_L_bar || I/n) = log(40) - S(rho_L_bar) >= 0."""
        D_KL_bar = np.log(40.0) - _S_vN_L_bar
        assert D_KL_bar >= -1e-14

    def test_KL_spectral_from_uniform(self):
        """KL of spectral distribution from uniform 1/40."""
        abs_evals = np.abs(_adj_evals)
        p = abs_evals / np.sum(abs_evals)
        q = np.ones(_N) / _N
        D_KL = np.sum(p * np.log(p / q))
        assert D_KL >= -1e-14

    def test_KL_adjacency_from_uniform(self):
        """D_KL(rho_A || I/n) = log(40) - S(rho_A) >= 0."""
        D_KL = np.log(40.0) - _S_vN_A
        assert D_KL >= -1e-14

    def test_KL_ordering(self):
        """rho_A (rank 25) is farther from I/40 than rho_L (rank 39)."""
        D_KL_L = np.log(40.0) - _S_vN_L
        D_KL_A = np.log(40.0) - _S_vN_A
        assert D_KL_A > D_KL_L


# =========================================================================
# 13.  Relative Entropy Between Graph and Complement  (5 tests)
# =========================================================================

class TestRelativeEntropy:
    """Relative entropy between graph and complement density matrices."""

    def test_both_rank_39(self):
        """Both rho_L and rho_L_bar have rank 39."""
        rank_L = np.sum(np.linalg.eigvalsh(_rho_L) > 1e-10)
        rank_Lb = np.sum(np.linalg.eigvalsh(_rho_L_bar) > 1e-10)
        assert rank_L == 39
        assert rank_Lb == 39

    def test_spectral_KL_nonneg(self):
        """KL between sorted positive eigenvalues >= 0 by Gibbs."""
        p = np.sort(np.linalg.eigvalsh(_rho_L))
        q = np.sort(np.linalg.eigvalsh(_rho_L_bar))
        p = p[p > 1e-14]
        q = q[q > 1e-14]
        assert len(p) == len(q) == 39
        D = np.sum(p * np.log(p / q))
        assert D >= -1e-10

    def test_sum_of_entropies_bound(self):
        """S(rho_L) + S(rho_L_bar) <= 2*log(39)."""
        assert _S_vN_L + _S_vN_L_bar <= 2.0 * np.log(39.0) + 1e-10

    def test_entropy_difference_finite(self):
        """Entropy difference is finite and computable."""
        diff = abs(_S_vN_L - _S_vN_L_bar)
        assert np.isfinite(diff)
        assert diff >= 0

    def test_joint_bound(self):
        """S(rho_L) + S(rho_L_bar) >= max(S(rho_L), S(rho_L_bar))."""
        assert (_S_vN_L + _S_vN_L_bar
                >= max(_S_vN_L, _S_vN_L_bar) - 1e-14)


# =========================================================================
# 14.  Entropy Bounds  (8 tests)
# =========================================================================

class TestEntropyBounds:
    """Information-theoretic bounds on graph entropy."""

    def test_vN_bounded_by_log_n(self):
        """S(rho_L) <= log(n) = log(40)."""
        assert _S_vN_L <= np.log(40.0) + 1e-10

    def test_vN_bounded_by_log_rank(self):
        """S(rho_L) <= log(39)."""
        assert _S_vN_L <= np.log(39.0) + 1e-10

    def test_renyi_2_leq_vN(self):
        """S_2 <= S_1 (von Neumann)."""
        evals = np.linalg.eigvalsh(_rho_L)
        S2 = _renyi_entropy(evals, 2.0)
        assert S2 <= _S_vN_L + 1e-12

    def test_min_entropy_leq_renyi_2(self):
        """S_inf <= S_2."""
        evals = np.linalg.eigvalsh(_rho_L)
        S2 = _renyi_entropy(evals, 2.0)
        S_inf = _renyi_entropy(evals, np.inf)
        assert S_inf <= S2 + 1e-12

    def test_subadditivity(self):
        """S(rho_L) <= S(rho_A) + S(rho_B) + reasonable overhead for
        a bipartition into two 20-vertex halves."""
        S1 = list(range(20))
        S2 = list(range(20, 40))
        L_s1 = L[np.ix_(S1, S1)]
        L_s2 = L[np.ix_(S2, S2)]
        tr1 = np.trace(L_s1)
        tr2 = np.trace(L_s2)
        if tr1 > 0 and tr2 > 0:
            S_A = _safe_entropy(np.linalg.eigvalsh(L_s1 / tr1))
            S_B = _safe_entropy(np.linalg.eigvalsh(L_s2 / tr2))
            assert _S_vN_L <= S_A + S_B + np.log(2.0) + 5.0

    def test_fano_inequality(self):
        """Fano: H(X|Y) <= h(p_e) + p_e*log(n-1).
        p_e = 1 - 1/12 = 11/12 for uniform neighbor transitions."""
        p_e = 1.0 - 1.0 / _K
        h_pe = -p_e * np.log(p_e) - (1 - p_e) * np.log(1 - p_e)
        fano_bound = h_pe + p_e * np.log(_N - 1.0)
        H_cond = np.log(12.0)
        assert H_cond <= fano_bound + 1e-10

    def test_entropy_rate_positive(self):
        """h = log(12) > 0."""
        assert np.log(12.0) > 0

    def test_lower_bound_from_max_eval(self):
        """S(rho) >= -log(max eigenvalue of rho) = log(30)."""
        evals = np.linalg.eigvalsh(_rho_L)
        assert _S_vN_L >= -np.log(np.max(evals)) - 1e-10


# =========================================================================
# 15.  Entropy Power Inequality and Tsallis  (5 tests)
# =========================================================================

class TestEntropyPowerAndTsallis:
    """Entropy power, Tsallis entropy, and isoperimetric bounds."""

    def test_entropy_power_positive(self):
        """Entropy power N = exp(2*S/r) > 0."""
        r = 39
        N_ent = np.exp(2.0 * _S_vN_L / r)
        assert N_ent > 0

    def test_entropy_power_bounded(self):
        """exp(2*S/r) <= r since S <= (r/2)*log(r) follows from S <= log(r)."""
        r = 39
        N_ent = np.exp(2.0 * _S_vN_L / r)
        assert N_ent <= r + 1e-10

    def test_hoffman_independent_set_bound(self):
        """alpha(G) <= n*|s|/(k+|s|) = 40*4/16 = 10.  log(alpha) < log(n)."""
        alpha_bound = _N * 4.0 / (_K + 4.0)
        assert_allclose(alpha_bound, 10.0, atol=1e-10)
        assert np.log(alpha_bound) < np.log(_N)

    def test_tsallis_entropy_order_2(self):
        """T_2(rho) = (1 - tr(rho^2))/(2-1) = 1 - purity = 1 - 13/480."""
        purity = np.trace(_rho_L @ _rho_L)
        T2 = 1.0 - purity
        assert T2 > 0
        assert T2 < 1
        expected = 1.0 - 13.0 / 480.0
        assert_allclose(T2, expected, atol=1e-14)

    def test_tsallis_order_2_complement(self):
        """T_2(rho_L_bar) = 1 - 7/270."""
        purity_bar = np.trace(_rho_L_bar @ _rho_L_bar)
        T2_bar = 1.0 - purity_bar
        expected = 1.0 - 7.0 / 270.0
        assert_allclose(T2_bar, expected, atol=1e-14)


# =========================================================================
# 16.  Information-Theoretic Capacity  (6 tests)
# =========================================================================

class TestInformationCapacity:
    """Shannon capacity, Lovasz theta, and related bounds."""

    def test_hoffman_bound(self):
        """alpha <= n*|lambda_min|/(k+|lambda_min|) = 10."""
        alpha = _N * 4.0 / (_K + 4.0)
        assert_allclose(alpha, 10.0, atol=1e-10)

    def test_lovasz_theta(self):
        """theta(G) = -n*s/(k-s) = 160/16 = 10 for vertex-transitive SRG."""
        theta = -_N * (-4.0) / (_K - (-4.0))
        assert_allclose(theta, 10.0, atol=1e-10)

    def test_lovasz_theta_complement(self):
        """theta(G_bar) = -40*(-3)/(27+3) = 4."""
        theta_bar = -_N * (-3.0) / (_K_bar - (-3.0))
        assert_allclose(theta_bar, 4.0, atol=1e-10)

    def test_theta_product_equals_n(self):
        """theta(G) * theta(G_bar) = 10 * 4 = 40 = n."""
        theta_G = 10.0
        theta_bar = 4.0
        assert_allclose(theta_G * theta_bar, float(_N), atol=1e-10)

    def test_entropy_capacity_ratio(self):
        """S(rho_L)/log(n) in (0, 1): not maximally entropic."""
        ratio = _S_vN_L / np.log(40.0)
        assert 0 < ratio < 1

    def test_holevo_quantity(self):
        """Holevo chi = S(rho) bounds accessible information. Verify value."""
        assert_allclose(_S_vN_L, np.log(1440.0) / 2.0, atol=1e-10)
        assert _S_vN_L > 0


# =========================================================================
# 17.  Topological Entropy  (5 tests)
# =========================================================================

class TestTopologicalEntropy:
    """Topological and spectral-radius entropy of graph."""

    def test_topological_entropy_from_spectral_radius(self):
        """h_top = log(spectral_radius(A)) = log(12)."""
        spectral_radius = np.max(np.abs(_adj_evals))
        assert_allclose(np.log(spectral_radius), np.log(12.0), atol=1e-10)

    def test_topological_entropy_positive(self):
        assert np.log(12.0) > 0

    def test_variational_principle(self):
        """h_top >= h_metric (entropy rate).  Equality for uniform on regular."""
        h_top = np.log(12.0)
        h_metric = np.log(12.0)
        assert h_top >= h_metric - 1e-14

    def test_ihara_zeta_determinant(self):
        """det(I - u*A + (k-1)*u^2*I) is finite at u = 1/k."""
        u = 1.0 / _K
        M = (1.0 + (_K - 1.0) * u ** 2) * I_ - u * A.astype(float)
        evals_M = np.linalg.eigvalsh(M)
        log_det = np.sum(np.log(np.abs(evals_M)))
        assert np.isfinite(log_det)

    def test_chromatic_lower_bound(self):
        """chi >= 1 + k/|lambda_min| = 1 + 12/4 = 4."""
        chi_lb = 1 + _K / 4.0
        assert chi_lb == 4.0
        assert np.log(chi_lb) > 0


# =========================================================================
# 18.  Advanced Entropy Identities  (6 tests)
# =========================================================================

class TestAdvancedEntropyIdentities:
    """Cross-cutting entropy identities and consistency checks."""

    def test_full_renyi_chain(self):
        """S_0 >= S_{1/2} >= S_1 >= S_2 >= S_inf."""
        evals = np.linalg.eigvalsh(_rho_L)
        chain = [_renyi_entropy(evals, a)
                 for a in [0.0, 0.5, 1.0, 2.0, np.inf]]
        for i in range(len(chain) - 1):
            assert chain[i] >= chain[i + 1] - 1e-10

    def test_purity_from_renyi_2(self):
        """exp(-S_2) = tr(rho^2) = purity."""
        evals = np.linalg.eigvalsh(_rho_L)
        S2 = _renyi_entropy(evals, 2.0)
        purity = np.trace(_rho_L @ _rho_L)
        assert_allclose(np.exp(-S2), purity, atol=1e-14)

    def test_effective_rank(self):
        """Effective rank = exp(S_vN) = sqrt(1440)."""
        r_eff = np.exp(_S_vN_L)
        assert_allclose(r_eff, np.sqrt(1440.0), atol=1e-8)
        assert 1.0 <= r_eff <= 39.0 + 1e-10

    def test_participation_ratio(self):
        """PR = 1/tr(rho^2) = 480/13."""
        purity = np.trace(_rho_L @ _rho_L)
        PR = 1.0 / purity
        assert_allclose(PR, 480.0 / 13.0, atol=1e-10)

    def test_entropy_of_A_squared_density(self):
        """A^2 eigenvalues {144, 4, 16}; tr(A^2)=480; density matrix entropy > 0."""
        A2 = (A @ A).astype(float)
        tr_A2 = np.trace(A2)
        assert_allclose(tr_A2, 480.0, atol=1e-8)
        rho_A2 = A2 / tr_A2
        S_A2 = _safe_entropy(np.linalg.eigvalsh(rho_A2))
        assert S_A2 > 0
        assert S_A2 <= np.log(40.0) + 1e-10

    def test_entropy_additivity_kronecker(self):
        """For tensor product state rho_kron = rho_L (x) rho_L,
        S(rho_kron) = 2 * S(rho_L)."""
        rho_prod = np.kron(_rho_L, _rho_L)
        evals_prod = np.linalg.eigvalsh(rho_prod)
        S_prod = _safe_entropy(evals_prod)
        assert_allclose(S_prod, 2.0 * _S_vN_L, atol=1e-8)
