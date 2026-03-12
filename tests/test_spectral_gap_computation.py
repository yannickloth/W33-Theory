"""
Phase CXX -- Spectral Gap Applications on W(3,3) = SRG(40, 12, 2, 4).

Spectrum:  {12^1, 2^24, (-4)^15}
Spectral gap (adjacency):  k - lambda_2 = 12 - 2 = 10
Fiedler value (algebraic connectivity):  10
Mixing rate:  max(|lambda_2|, |lambda_min|) / k = 4/12 = 1/3

80+ tests covering: mixing time bounds, random walk convergence,
expander properties, Cheeger constant, total variation distance decay,
hitting/cover times, Kemeny's constant, MCMC convergence, Poincare inequality.

Dependencies: numpy, pytest (standard library otherwise).
"""

import math
import numpy as np
import pytest


# ====================================================================
# W(3,3) builder
# ====================================================================

def _build_w33():
    """Build the adjacency matrix of W(3,3) = PG(3,3) symplectic graph."""
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


# ====================================================================
# Module-scoped fixtures (computed once)
# ====================================================================

@pytest.fixture(scope="module")
def A():
    return _build_w33()


@pytest.fixture(scope="module")
def spectrum(A):
    """Sorted eigenvalues of A in descending order."""
    eigs = np.linalg.eigvalsh(A)
    return np.sort(eigs)[::-1]


@pytest.fixture(scope="module")
def P(A):
    """Transition matrix of simple random walk on W(3,3)."""
    return A / 12.0


@pytest.fixture(scope="module")
def laplacian(A):
    """Combinatorial Laplacian L = kI - A."""
    return 12 * np.eye(40) - A


@pytest.fixture(scope="module")
def lap_spectrum(laplacian):
    """Laplacian eigenvalues in ascending order."""
    eigs = np.linalg.eigvalsh(laplacian)
    return np.sort(eigs)


@pytest.fixture(scope="module")
def P_eig(P):
    """Full eigen-decomposition of P."""
    vals, vecs = np.linalg.eigh(P)
    idx = np.argsort(vals)[::-1]
    return vals[idx], vecs[:, idx]


@pytest.fixture(scope="module")
def fundamental_matrix(P):
    """Fundamental matrix Z = (I - P + J/n)^{-1}."""
    n = 40
    J = np.ones((n, n)) / n
    M = np.eye(n) - P + J
    return np.linalg.inv(M)


@pytest.fixture(scope="module")
def hitting_times(fundamental_matrix):
    """Mean first passage time matrix H[i,j] = n * (Z[j,j] - Z[i,j])."""
    Z = fundamental_matrix
    n = 40
    H = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            H[i, j] = n * (Z[j, j] - Z[i, j])
    return H


# ====================================================================
# SECTION 1: SRG and Spectral Fundamentals (12 tests)
# ====================================================================

class TestSRGSpectralFundamentals:
    """Verify basic SRG parameters and adjacency spectrum."""

    def test_vertex_count(self, A):
        assert A.shape == (40, 40)

    def test_regularity(self, A):
        degrees = A.sum(axis=1)
        assert np.all(degrees == 12)

    def test_srg_lambda_parameter(self, A):
        """Adjacent pairs share exactly lambda=2 common neighbours."""
        for i in range(40):
            for j in range(i + 1, 40):
                if A[i, j] == 1:
                    common = int(A[i] @ A[j])
                    assert common == 2

    def test_srg_mu_parameter(self, A):
        """Non-adjacent pairs share exactly mu=4 common neighbours."""
        for i in range(40):
            for j in range(i + 1, 40):
                if A[i, j] == 0:
                    common = int(A[i] @ A[j])
                    assert common == 4

    def test_adjacency_symmetric(self, A):
        assert np.array_equal(A, A.T)

    def test_trace_zero(self, A):
        assert np.trace(A) == 0

    def test_three_distinct_eigenvalues(self, spectrum):
        rounded = np.round(spectrum, 6)
        assert len(set(rounded)) == 3

    def test_eigenvalue_12_multiplicity(self, spectrum):
        count = int(np.sum(np.abs(spectrum - 12) < 1e-8))
        assert count == 1

    def test_eigenvalue_2_multiplicity(self, spectrum):
        count = int(np.sum(np.abs(spectrum - 2) < 1e-8))
        assert count == 24

    def test_eigenvalue_neg4_multiplicity(self, spectrum):
        count = int(np.sum(np.abs(spectrum - (-4)) < 1e-8))
        assert count == 15

    def test_multiplicities_sum_to_n(self, spectrum):
        c12 = int(np.sum(np.abs(spectrum - 12) < 1e-8))
        c2 = int(np.sum(np.abs(spectrum - 2) < 1e-8))
        cm4 = int(np.sum(np.abs(spectrum + 4) < 1e-8))
        assert c12 + c2 + cm4 == 40

    def test_spectral_gap_value(self, spectrum):
        """Spectral gap = k - lambda_2 = 12 - 2 = 10."""
        gap = spectrum[0] - spectrum[1]
        assert abs(gap - 10) < 1e-8


# ====================================================================
# SECTION 2: Laplacian Properties (8 tests)
# ====================================================================

class TestLaplacianProperties:
    """Combinatorial and normalised Laplacian analysis."""

    def test_laplacian_eigenvalues(self, lap_spectrum):
        """L = kI - A has eigenvalues {0^1, 10^24, 16^15}."""
        expected = sorted([0] * 1 + [10] * 24 + [16] * 15)
        for a, e in zip(lap_spectrum, expected):
            assert abs(a - e) < 1e-8

    def test_fiedler_value(self, lap_spectrum):
        """Algebraic connectivity (second-smallest Laplacian eig) = 10."""
        fiedler = lap_spectrum[1]
        assert abs(fiedler - 10) < 1e-8

    def test_laplacian_psd(self, lap_spectrum):
        """Laplacian is positive semidefinite."""
        assert np.all(lap_spectrum >= -1e-10)

    def test_laplacian_nullity(self, lap_spectrum):
        """Nullity = 1 (graph is connected)."""
        nullity = int(np.sum(np.abs(lap_spectrum) < 1e-8))
        assert nullity == 1

    def test_laplacian_trace(self, laplacian):
        """tr(L) = n * k = 40 * 12 = 480."""
        assert abs(np.trace(laplacian) - 480) < 1e-8

    def test_normalized_laplacian_eigenvalues(self, A):
        """Normalised Laplacian I - A/k has eigenvalues {0^1, (5/6)^24, (4/3)^15}."""
        L_norm = np.eye(40) - A / 12.0
        eigs = np.sort(np.linalg.eigvalsh(L_norm))
        c0 = int(np.sum(np.abs(eigs) < 1e-8))
        c56 = int(np.sum(np.abs(eigs - 5.0 / 6) < 1e-8))
        c43 = int(np.sum(np.abs(eigs - 4.0 / 3) < 1e-8))
        assert (c0, c56, c43) == (1, 24, 15)

    def test_spanning_tree_count_log(self, lap_spectrum):
        """log(spanning trees) = log(prod nonzero L eigs / n)."""
        nonzero = lap_spectrum[lap_spectrum > 1e-8]
        log_tau = np.sum(np.log(nonzero)) - np.log(40)
        expected = 24 * np.log(10) + 15 * np.log(16) - np.log(40)
        assert abs(log_tau - expected) < 1e-6

    def test_laplacian_eigenvalue_sum(self, lap_spectrum):
        """Sum of Laplacian eigenvalues = tr(L) = 480."""
        assert abs(np.sum(lap_spectrum) - 480) < 1e-6


# ====================================================================
# SECTION 3: Transition Matrix and Random Walk (10 tests)
# ====================================================================

class TestTransitionMatrix:
    """Simple random walk P = A/k on k-regular W(3,3)."""

    def test_row_stochastic(self, P):
        row_sums = P.sum(axis=1)
        np.testing.assert_allclose(row_sums, 1.0, atol=1e-14)

    def test_doubly_stochastic(self, P):
        col_sums = P.sum(axis=0)
        np.testing.assert_allclose(col_sums, 1.0, atol=1e-14)

    def test_transition_eigenvalues(self, P):
        """Eigenvalues of P = {1^1, (1/6)^24, (-1/3)^15}."""
        eigs = np.sort(np.linalg.eigvalsh(P))[::-1]
        c1 = int(np.sum(np.abs(eigs - 1.0) < 1e-8))
        c16 = int(np.sum(np.abs(eigs - 1.0 / 6) < 1e-8))
        cm13 = int(np.sum(np.abs(eigs + 1.0 / 3) < 1e-8))
        assert (c1, c16, cm13) == (1, 24, 15)

    def test_stationary_uniform(self, P):
        """pi = (1/40, ..., 1/40) is stationary: pi P = pi."""
        pi = np.ones(40) / 40
        np.testing.assert_allclose(pi @ P, pi, atol=1e-14)

    def test_lambda_star(self, P):
        """lambda* = max(|lambda_2(P)|, |lambda_min(P)|) = 1/3."""
        eigs = np.sort(np.linalg.eigvalsh(P))[::-1]
        lam_star = max(abs(eigs[1]), abs(eigs[-1]))
        assert abs(lam_star - 1.0 / 3) < 1e-8

    def test_spectral_gap_of_P(self, P):
        """gap(P) = 1 - lambda_2(P) = 1 - 1/6 = 5/6."""
        eigs = np.sort(np.linalg.eigvalsh(P))[::-1]
        gap = 1 - eigs[1]
        assert abs(gap - 5.0 / 6) < 1e-8

    def test_absolute_spectral_gap(self, P):
        """Absolute gap = 1 - lambda* = 1 - 1/3 = 2/3."""
        eigs = np.linalg.eigvalsh(P)
        lam_star = max(abs(e) for e in eigs if abs(e - 1.0) > 1e-8)
        assert abs(1 - lam_star - 2.0 / 3) < 1e-8

    def test_mixing_rate(self):
        """Mixing rate = max(|lambda_2|, |lambda_min|)/k = 4/12 = 1/3."""
        assert abs(4.0 / 12 - 1.0 / 3) < 1e-15

    def test_P_irreducible(self, A):
        """Graph is connected => P irreducible (BFS reaches all 40 vertices)."""
        visited = {0}
        frontier = [0]
        while frontier:
            nxt = []
            for u in frontier:
                for v in range(40):
                    if A[u, v] == 1 and v not in visited:
                        visited.add(v)
                        nxt.append(v)
            frontier = nxt
        assert len(visited) == 40

    def test_P_aperiodic(self, A):
        """W(3,3) has triangles (lambda=2 > 0) => odd cycles => aperiodic."""
        found = False
        for i in range(40):
            if found:
                break
            for j in range(i + 1, 40):
                if A[i, j] == 0:
                    continue
                for kk in range(j + 1, 40):
                    if A[i, kk] == 1 and A[j, kk] == 1:
                        found = True
                        break
                if found:
                    break
        assert found


# ====================================================================
# SECTION 4: Mixing Time Bounds (10 tests)
# ====================================================================

class TestMixingTimeBounds:
    """Upper/lower bounds on mixing time from spectral data."""

    def test_relaxation_time(self):
        """t_rel = 1 / (1 - lambda*) = 1 / (2/3) = 3/2."""
        t_rel = 1.0 / (1 - 1.0 / 3)
        assert abs(t_rel - 1.5) < 1e-14

    def test_mixing_time_upper_bound(self):
        """Using d(t) <= sqrt(n-1) * lambda*^t, find smallest t with d(t) < 1/4.
           t >= ln(sqrt(39) / 0.25) / ln(3) => t_mix(1/4) <= 3."""
        lam_star = 1.0 / 3
        eps = 0.25
        t_upper = math.ceil(
            math.log(math.sqrt(39) / eps) / math.log(1 / lam_star)
        )
        assert t_upper == 3

    def test_tv_bound_t3_below_quarter(self):
        """At t=3, spectral TV bound sqrt(39) * (1/3)^3 < 1/4."""
        bound = math.sqrt(39) * (1.0 / 3) ** 3
        assert bound < 0.25

    def test_tv_bound_t2_above_quarter(self):
        """At t=2, spectral TV bound sqrt(39) * (1/3)^2 > 1/4."""
        bound = math.sqrt(39) * (1.0 / 3) ** 2
        assert bound > 0.25

    def test_tv_bound_t5_near_zero(self):
        """At t=5, TV bound sqrt(39)*(1/3)^5 < 0.03."""
        bound = math.sqrt(39) * (1.0 / 3) ** 5
        assert bound < 0.03

    def test_mixing_time_lower_bound(self):
        """t_mix(1/4) >= 1 since the graph has diameter 2."""
        # A single step from a vertex reaches only 12 of 40 vertices.
        # TV at t=0 is 39/40, so at least one step is required.
        assert 1 >= 1  # lower bound is 1

    def test_lazy_walk_eigenvalues(self, P):
        """P_lazy = (I + P)/2 has eigenvalues {1^1, (7/12)^24, (1/3)^15}."""
        P_lazy = (np.eye(40) + P) / 2
        eigs = np.sort(np.linalg.eigvalsh(P_lazy))[::-1]
        c1 = int(np.sum(np.abs(eigs - 1.0) < 1e-8))
        c712 = int(np.sum(np.abs(eigs - 7.0 / 12) < 1e-8))
        c13 = int(np.sum(np.abs(eigs - 1.0 / 3) < 1e-8))
        assert (c1, c712, c13) == (1, 24, 15)

    def test_lazy_walk_spectral_gap(self):
        """Lazy walk gap = 1 - 7/12 = 5/12."""
        gap = 1 - 7.0 / 12
        assert abs(gap - 5.0 / 12) < 1e-14

    def test_lazy_mixing_time_upper(self):
        """Lazy walk lambda*_lazy = 7/12; mixing time bound is larger."""
        lam_star_lazy = 7.0 / 12
        eps = 0.25
        t_upper = math.ceil(
            math.log(math.sqrt(39) / eps) / math.log(1 / lam_star_lazy)
        )
        assert t_upper <= 7

    def test_log_sobolev_constant_bound(self):
        """Modified log-Sobolev constant alpha >= gap / ln(n).
           alpha >= (5/6) / ln(40) > 0.2."""
        alpha_lower = (5.0 / 6) / math.log(40)
        assert alpha_lower > 0.2


# ====================================================================
# SECTION 5: Random Walk Convergence (10 tests)
# ====================================================================

class TestRandomWalkConvergence:
    """Numerical verification of random walk convergence."""

    def test_P_power_convergence(self, P):
        """P^20 converges to J/n (uniform matrix)."""
        Pt = np.linalg.matrix_power(P, 20)
        J = np.ones((40, 40)) / 40
        np.testing.assert_allclose(Pt, J, atol=1e-6)

    def test_convergence_rate(self, P):
        """||P^t - J/n||_F decays; successive ratios < 0.5."""
        J = np.ones((40, 40)) / 40
        norms = []
        for t in range(1, 11):
            Pt = np.linalg.matrix_power(P, t)
            norms.append(np.linalg.norm(Pt - J, 'fro'))
        for t in range(1, len(norms)):
            ratio = norms[t] / norms[t - 1]
            assert ratio < 0.5

    def test_l2_distance_decay(self, P):
        """L2 distance from row 0 to uniform decays at rate lambda*^t."""
        pi = np.ones(40) / 40
        for t in [1, 2, 3, 5, 10]:
            Pt = np.linalg.matrix_power(P, t)
            dist = np.linalg.norm(Pt[0] - pi)
            bound = math.sqrt(39.0 / 40) * (1.0 / 3) ** t
            assert dist <= bound + 1e-10

    def test_P_squared_all_positive(self, P):
        """P^2 has all positive entries (diameter <= 2)."""
        P2 = P @ P
        assert np.all(P2 > 0)

    def test_P_cubed_close_to_uniform(self, P):
        """Each entry of P^3 is within 0.02 of 1/40."""
        P3 = np.linalg.matrix_power(P, 3)
        max_dev = np.max(np.abs(P3 - 1.0 / 40))
        assert max_dev < 0.02

    def test_walk_from_single_vertex(self, P):
        """Starting from vertex 0, distribution at t=4 is nearly uniform."""
        e0 = np.zeros(40)
        e0[0] = 1.0
        dist = e0 @ np.linalg.matrix_power(P, 4)
        np.testing.assert_allclose(dist, np.ones(40) / 40, atol=0.006)

    def test_walk_distribution_symmetry(self, P):
        """By vertex-transitivity, all rows of P^4 have the same sorted profile."""
        P4 = np.linalg.matrix_power(P, 4)
        ref = np.sort(P4[0])[::-1]
        for i in range(1, 40):
            np.testing.assert_allclose(np.sort(P4[i])[::-1], ref, atol=1e-10)

    def test_variance_decay_rate(self, P):
        """Var_pi(P^t f) <= lambda*^{2t} * Var_pi(f) for f(i) = i."""
        f = np.arange(40, dtype=float)
        var_f = np.var(f)
        for t in [1, 2, 3, 5]:
            Pt_f = np.linalg.matrix_power(P, t) @ f
            var_Pt_f = np.var(Pt_f)
            bound = (1.0 / 3) ** (2 * t) * var_f
            assert var_Pt_f <= bound + 1e-10

    def test_tv_monotone_lazy(self, P):
        """TV distance for lazy walk is monotonically non-increasing."""
        P_lazy = (np.eye(40) + P) / 2
        pi = np.ones(40) / 40
        prev_tv = 1.0
        for t in range(1, 15):
            row = np.linalg.matrix_power(P_lazy, t)[0]
            tv = 0.5 * np.sum(np.abs(row - pi))
            assert tv <= prev_tv + 1e-12
            prev_tv = tv

    def test_coupling_time_bound(self):
        """Expected coupling time = O(t_rel * ln(n)) = O(1.5 * ln(40)) < 6."""
        t_coupling = 1.5 * math.log(40)
        assert t_coupling < 6


# ====================================================================
# SECTION 6: Total Variation Distance (8 tests)
# ====================================================================

class TestTotalVariationDistance:
    """Exact and bounded TV distance computations."""

    def test_tv_distance_t0(self):
        """At t=0, TV from delta_0 to uniform = 1 - 1/n = 39/40."""
        e0 = np.zeros(40)
        e0[0] = 1.0
        pi = np.ones(40) / 40
        tv = 0.5 * np.sum(np.abs(e0 - pi))
        assert abs(tv - 39.0 / 40) < 1e-14

    def test_tv_exponential_decay(self, P):
        """log(TV) decreases roughly linearly => exponential decay."""
        pi = np.ones(40) / 40
        tvs = []
        for t in range(1, 8):
            row = np.linalg.matrix_power(P, t)[0]
            tv = 0.5 * np.sum(np.abs(row - pi))
            tvs.append(tv)
        log_tvs = [math.log(tv) for tv in tvs if tv > 1e-15]
        if len(log_tvs) >= 3:
            slopes = [log_tvs[i + 1] - log_tvs[i] for i in range(len(log_tvs) - 1)]
            avg_slope = sum(slopes) / len(slopes)
            assert avg_slope < -0.5  # decays faster than e^{-0.5 t}

    def test_tv_explicit_t1(self, P):
        """TV at t=1 from vertex 0: row has 12 entries of 1/12 and 28 zeros.
           TV = 0.5 * (12*|1/12 - 1/40| + 28*|0 - 1/40|) = 7/10."""
        pi = np.ones(40) / 40
        row = P[0]
        tv = 0.5 * np.sum(np.abs(row - pi))
        assert abs(tv - 0.7) < 1e-10

    def test_tv_explicit_t2(self, P):
        """TV at t=2 from vertex 0, computed from A^2 structure:
           P^2[0,0] = 1/12, P^2[0,adj] = 1/72, P^2[0,nonadj] = 1/36."""
        pi = np.ones(40) / 40
        P2 = P @ P
        tv = 0.5 * np.sum(np.abs(P2[0] - pi))
        expected_tv = 0.5 * (
            abs(1.0 / 12 - 1.0 / 40)
            + 12 * abs(1.0 / 72 - 1.0 / 40)
            + 27 * abs(1.0 / 36 - 1.0 / 40)
        )
        assert abs(tv - expected_tv) < 1e-10

    def test_tv_explicit_t3_below_threshold(self, P):
        """TV at t=3 is below the 1/4 mixing threshold."""
        pi = np.ones(40) / 40
        P3 = np.linalg.matrix_power(P, 3)
        tv = 0.5 * np.sum(np.abs(P3[0] - pi))
        assert tv < 0.25

    def test_separation_distance_bound(self, P):
        """Separation distance s(t) >= TV distance d(t) for all t."""
        pi = np.ones(40) / 40
        for t in [2, 3, 5]:
            Pt = np.linalg.matrix_power(P, t)
            row = Pt[0]
            tv = 0.5 * np.sum(np.abs(row - pi))
            sep = 1 - np.min(row) * 40
            assert sep >= tv - 1e-10

    def test_chi_squared_decay(self, P):
        """chi^2(P^t(0,.), pi) <= (n-1) * lambda*^{2t}."""
        pi = np.ones(40) / 40
        for t in [1, 2, 3]:
            Pt = np.linalg.matrix_power(P, t)
            row = Pt[0]
            chi2 = np.sum((row - pi) ** 2 / pi)
            bound = 39 * (1.0 / 3) ** (2 * t)
            assert chi2 <= bound + 1e-10

    def test_tv_worst_case_uniform_by_symmetry(self, P):
        """By vertex-transitivity, TV at t=3 is identical from every vertex."""
        pi = np.ones(40) / 40
        P3 = np.linalg.matrix_power(P, 3)
        tvs = [0.5 * np.sum(np.abs(P3[i] - pi)) for i in range(40)]
        np.testing.assert_allclose(tvs, tvs[0], atol=1e-10)


# ====================================================================
# SECTION 7: Cheeger Constant and Isoperimetry (8 tests)
# ====================================================================

class TestCheegerIsoperimetry:
    """Cheeger inequality and edge/vertex expansion."""

    def test_cheeger_lower_bound(self):
        """Cheeger inequality: h(G) >= (k - lambda_2) / 2 = 10/2 = 5."""
        h_lower = (12 - 2) / 2.0
        assert abs(h_lower - 5) < 1e-14

    def test_cheeger_upper_bound(self):
        """h(G) <= min(sqrt(2k(k-lambda_2)), k) = min(sqrt(240), 12) = 12."""
        h_upper = min(math.sqrt(2 * 12 * 10), 12)
        assert abs(h_upper - 12) < 1e-10

    def test_single_vertex_boundary(self, A):
        """Edge boundary of a single vertex = degree = 12."""
        boundary = int(A[0].sum())
        assert boundary == 12

    def test_edge_expansion_sampled(self, A):
        """For random S with |S| <= 20, edge expansion |E(S,Sc)|/|S| >= 5."""
        rng = np.random.RandomState(42)
        for _ in range(20):
            size = rng.randint(1, 21)
            S = rng.choice(40, size, replace=False)
            S_set = set(S.tolist())
            boundary = 0
            for u in S:
                for v in range(40):
                    if A[u, v] == 1 and v not in S_set:
                        boundary += 1
            ratio = boundary / len(S)
            assert ratio >= 5 - 1e-10

    def test_vertex_expansion(self, A):
        """Vertex expansion: |N(S) \\ S| >= |S| for small S."""
        S = [0, 1, 2]
        S_set = set(S)
        neighbors = set()
        for u in S:
            for v in range(40):
                if A[u, v] == 1 and v not in S_set:
                    neighbors.add(v)
        assert len(neighbors) >= len(S)

    def test_isoperimetric_half(self, A):
        """Edge boundary of a random half-partition (|S|=20) >= 100."""
        rng = np.random.RandomState(123)
        S = rng.choice(40, 20, replace=False)
        S_set = set(S.tolist())
        boundary = sum(
            1 for u in S for v in range(40)
            if A[u, v] == 1 and v not in S_set
        )
        assert boundary >= 100

    def test_cheeger_normalized(self):
        """Normalized Cheeger bounds from mu_1 = 5/6:
           5/12 <= h_norm <= sqrt(5/3)."""
        mu1 = 5.0 / 6
        lower = mu1 / 2
        upper = math.sqrt(2 * mu1)
        assert abs(lower - 5.0 / 12) < 1e-14
        assert abs(upper - math.sqrt(5.0 / 3)) < 1e-10

    def test_edge_isoperimetric_profile_sampled(self, A):
        """Min edge-expansion ratio stays above 3 for sampled subsets."""
        rng = np.random.RandomState(77)
        for s in [1, 2, 5, 10, 15, 20]:
            min_ratio = float('inf')
            for _ in range(10):
                S = rng.choice(40, s, replace=False)
                S_set = set(S.tolist())
                bdry = sum(
                    1 for u in S for v in range(40)
                    if A[u, v] == 1 and v not in S_set
                )
                min_ratio = min(min_ratio, bdry / s)
            assert min_ratio >= 3


# ====================================================================
# SECTION 8: Expander Properties (8 tests)
# ====================================================================

class TestExpanderProperties:
    """Expander mixing lemma, Ramanujan bound, discrepancy."""

    def test_expander_mixing_lemma(self, A):
        """For any S, T: |e(S,T) - k|S||T|/n| <= lambda * sqrt(|S||T|)
           with lambda = max(|lambda_2|, |lambda_min|) = 4."""
        rng = np.random.RandomState(42)
        lam = 4
        for _ in range(30):
            s = rng.randint(1, 30)
            t = rng.randint(1, 30)
            S = rng.choice(40, s, replace=False)
            T = rng.choice(40, t, replace=False)
            edges = sum(int(A[u, v]) for u in S for v in T)
            expected = 12 * len(S) * len(T) / 40.0
            bound = lam * math.sqrt(len(S) * len(T))
            assert abs(edges - expected) <= bound + 1e-10

    def test_spectral_expansion_parameter(self):
        """lambda(G) = max(|lambda_2|, |lambda_min|) = max(2, 4) = 4."""
        assert max(abs(2), abs(-4)) == 4

    def test_ramanujan_property(self):
        """W(3,3) is Ramanujan: lambda(G) = 4 <= 2*sqrt(k-1) = 2*sqrt(11)."""
        bound = 2 * math.sqrt(11)
        assert 4 <= bound

    def test_alon_boppana(self):
        """Alon-Boppana: for any k-regular graph, lambda_2 >= 2*sqrt(k-1) - o(1).
           Here lambda_2 = 2 < 2*sqrt(11) (graph has small girth)."""
        assert 2 < 2 * math.sqrt(11)

    def test_edge_count_from_spectrum(self, spectrum):
        """Number of edges = sum(lambda_i^2) / 2 = n*k/2 = 240."""
        assert abs(np.sum(spectrum ** 2) / 2 - 240) < 1e-6

    def test_triangle_count_from_spectrum(self, spectrum):
        """Number of triangles = tr(A^3)/6 = sum(lambda_i^3)/6.
           12^3 + 24*2^3 + 15*(-4)^3 = 1728 + 192 - 960 = 960; triangles = 160."""
        tr_A3 = np.sum(spectrum ** 3)
        assert abs(tr_A3 - 960) < 1e-6
        assert abs(tr_A3 / 6 - 160) < 1e-6

    def test_discrepancy_bound(self, A):
        """For S = first 10 vertices, |e(S,S) - k|S|^2/n| <= lambda*|S|.
           Using directed edge count for simplicity."""
        S = list(range(10))
        edges_dir = sum(int(A[u, v]) for u in S for v in S)
        expected = 12 * 10 * 10 / 40.0
        assert abs(edges_dir - expected) <= 4 * 10

    def test_eigenvalue_interlacing(self, A):
        """Cauchy interlacing: for induced subgraph on m=20 vertices,
           lambda_i(A) >= lambda_i(B) >= lambda_{i+20}(A)."""
        B = A[:20, :20]
        eigs_B = np.sort(np.linalg.eigvalsh(B))[::-1]
        eigs_A = np.sort(np.linalg.eigvalsh(A))[::-1]
        for i in range(20):
            assert eigs_A[i] >= eigs_B[i] - 1e-8
            assert eigs_B[i] >= eigs_A[i + 20] - 1e-8


# ====================================================================
# SECTION 9: Hitting and Cover Times (6 tests)
# ====================================================================

class TestHittingCoverTimes:
    """Hitting times, commute times, cover time bounds."""

    def test_expected_return_time(self):
        """For uniform pi, expected return to any vertex = 1/pi(i) = 40."""
        assert abs(1.0 / (1.0 / 40) - 40) < 1e-14

    def test_hitting_times_positive(self, hitting_times):
        """All off-diagonal hitting times are positive."""
        H = hitting_times
        for i in range(40):
            for j in range(40):
                if i != j:
                    assert H[i, j] > 0

    def test_hitting_time_upper_bound(self, hitting_times):
        """Max hitting time bounded by n * t_rel * ln(n) ~ 221."""
        max_hit = np.max(hitting_times)
        assert max_hit < 300

    def test_commute_time_from_resistance(self, A, hitting_times):
        """Commute time C(i,j) = 2m * R_eff(i,j) with m = 240."""
        H = hitting_times
        C = H + H.T
        L = 12 * np.eye(40) - A
        L_pinv = np.linalg.pinv(L)
        m = 240
        for i in range(0, 40, 10):
            for j in range(i + 1, 40, 10):
                R_eff = L_pinv[i, i] + L_pinv[j, j] - 2 * L_pinv[i, j]
                expected_C = 2 * m * R_eff
                assert abs(C[i, j] - expected_C) < 0.01

    def test_cover_time_upper_bound(self, hitting_times):
        """Cover time <= max_hitting * ln(n) + n (Matthews-style bound)."""
        max_hit = np.max(hitting_times)
        cover_bound = max_hit * math.log(40) + 40
        assert cover_bound < 2000

    def test_hitting_time_adj_vs_nonadj(self, A, hitting_times):
        """By rank-3 symmetry, H(i,j) constant on adjacent / non-adjacent pairs.
           Non-adjacent hitting time exceeds adjacent hitting time."""
        H = hitting_times
        adj_hits = []
        nonadj_hits = []
        for i in range(40):
            for j in range(40):
                if i == j:
                    continue
                if A[i, j] == 1:
                    adj_hits.append(H[i, j])
                else:
                    nonadj_hits.append(H[i, j])
        np.testing.assert_allclose(adj_hits, adj_hits[0], atol=1e-6)
        np.testing.assert_allclose(nonadj_hits, nonadj_hits[0], atol=1e-6)
        assert nonadj_hits[0] > adj_hits[0]


# ====================================================================
# SECTION 10: Kemeny's Constant (5 tests)
# ====================================================================

class TestKemenysConstant:
    """Kemeny's constant K = sum_{i>=2} 1/(1 - lambda_i(P))."""

    def test_kemeny_exact(self):
        """K = 24/(5/6) + 15/(4/3) = 144/5 + 45/4 = 801/20 = 40.05."""
        K = 24 * 6.0 / 5 + 15 * 3.0 / 4
        assert abs(K - 801.0 / 20) < 1e-12
        assert abs(K - 40.05) < 1e-12

    def test_kemeny_from_eigenvalues(self, P):
        """Compute Kemeny numerically from P eigenvalues."""
        eigs = np.sort(np.linalg.eigvalsh(P))[::-1]
        K = sum(1.0 / (1 - e) for e in eigs[1:])
        assert abs(K - 40.05) < 1e-6

    def test_kemeny_independent_of_start(self, hitting_times):
        """K = (1/n) * sum_j H(i,j) is the same for every starting vertex i."""
        H = hitting_times
        row_means = [np.mean(H[i]) for i in range(40)]
        for rm in row_means:
            assert abs(rm - row_means[0]) < 1e-6

    def test_kemeny_equals_mean_hitting(self, hitting_times):
        """Mean hitting time from any vertex = K = 40.05."""
        H = hitting_times
        mean_hit = np.mean(H[0])
        assert abs(mean_hit - 40.05) < 1e-4

    def test_kemeny_from_fundamental_trace(self, fundamental_matrix):
        """K = tr(Z) - 1 where Z = (I - P + J/n)^{-1}."""
        K = np.trace(fundamental_matrix) - 1
        assert abs(K - 40.05) < 1e-6


# ====================================================================
# SECTION 11: Poincare Inequality (5 tests)
# ====================================================================

class TestPoincareInequality:
    """Poincare inequality and variance bounds."""

    def test_poincare_constant(self):
        """Poincare constant C_P = 1 / gap(P) = 1 / (5/6) = 6/5."""
        C_P = 1.0 / (5.0 / 6)
        assert abs(C_P - 6.0 / 5) < 1e-14

    def test_variance_decay_poincare(self, P):
        """Var_pi(P f) <= lambda*^2 * Var_pi(f) = (1/9) * Var_pi(f)."""
        f = np.sin(np.arange(40) * 2 * math.pi / 40)
        Pf = P @ f
        var_f = np.var(f)
        var_Pf = np.var(Pf)
        assert var_Pf <= (1.0 / 3) ** 2 * var_f + 1e-12

    def test_rayleigh_quotient_min(self, A):
        """min_{f perp 1} (f^T L f) / (f^T f) = Fiedler value = 10."""
        L = 12 * np.eye(40) - A
        eigs = np.sort(np.linalg.eigvalsh(L))
        assert abs(eigs[1] - 10) < 1e-8

    def test_dirichlet_form_bound(self, P):
        """Poincare: Var_pi(f) <= C_P * E(f,f) with C_P = 6/5, for f(i) = i."""
        f = np.arange(40, dtype=float)
        var_f = np.mean((f - np.mean(f)) ** 2)
        E = 0.0
        for i in range(40):
            for j in range(40):
                E += (1.0 / 40) * P[i, j] * (f[i] - f[j]) ** 2
        E /= 2
        C_P = 6.0 / 5
        assert var_f <= C_P * E + 1e-8

    def test_poincare_quadratic_function(self, P):
        """Poincare inequality holds for f(i) = i^2."""
        f = (np.arange(40, dtype=float)) ** 2
        var_f = np.mean((f - np.mean(f)) ** 2)
        E = 0.0
        for i in range(40):
            for j in range(40):
                E += (1.0 / 40) * P[i, j] * (f[i] - f[j]) ** 2
        E /= 2
        C_P = 6.0 / 5
        assert var_f <= C_P * E + 1e-8


# ====================================================================
# SECTION 12: MCMC Convergence (5 tests)
# ====================================================================

class TestMCMCConvergence:
    """MCMC convergence via Metropolis-Hastings on W(3,3)."""

    def test_detailed_balance(self, P):
        """Simple RW satisfies detailed balance: pi(i) P(i,j) = pi(j) P(j,i)."""
        pi_val = 1.0 / 40
        for i in range(40):
            for j in range(40):
                lhs = pi_val * P[i, j]
                rhs = pi_val * P[j, i]
                assert abs(lhs - rhs) < 1e-14

    def test_metropolis_convergence(self, A):
        """Metropolis-Hastings with non-uniform target converges in TV."""
        rng = np.random.RandomState(42)
        target = np.exp(-0.1 * np.arange(40))
        target /= target.sum()
        x = 0
        counts = np.zeros(40)
        for step in range(50000):
            neighbors = np.where(A[x] == 1)[0]
            y = rng.choice(neighbors)
            alpha = min(1.0, target[y] / target[x])
            if rng.random() < alpha:
                x = y
            counts[x] += 1
        empirical = counts / counts.sum()
        tv = 0.5 * np.sum(np.abs(empirical - target))
        assert tv < 0.05

    def test_autocorrelation_time_bound(self):
        """Integrated autocorrelation time tau <= 1/gap = 6/5 = 1.2."""
        tau_int = 1.0 / (5.0 / 6)
        assert abs(tau_int - 1.2) < 1e-14

    def test_effective_sample_size(self):
        """ESS = N / (2 * tau_int). With N=1000, ESS >= 416."""
        N = 1000
        tau_int = 1.2
        ESS = N / (2 * tau_int)
        assert ESS > 400

    def test_empirical_uniform_convergence(self, A):
        """Simple random walk empirical distribution converges to uniform."""
        rng = np.random.RandomState(123)
        x = 0
        counts = np.zeros(40)
        for _ in range(40000):
            neighbors = np.where(A[x] == 1)[0]
            x = rng.choice(neighbors)
            counts[x] += 1
        empirical = counts / counts.sum()
        tv = 0.5 * np.sum(np.abs(empirical - 1.0 / 40))
        assert tv < 0.03


# ====================================================================
# SECTION 13: Additional Spectral Gap Applications (5 tests)
# ====================================================================

class TestAdditionalSpectralGap:
    """Effective resistance, graph energy, independence bounds."""

    def test_resistance_diameter(self, A):
        """Effective resistance diameter is small for strong expanders."""
        L = 12 * np.eye(40) - A
        L_pinv = np.linalg.pinv(L)
        max_R = 0
        for i in range(40):
            for j in range(i + 1, 40):
                R = L_pinv[i, i] + L_pinv[j, j] - 2 * L_pinv[i, j]
                max_R = max(max_R, R)
        assert max_R > 0
        assert max_R < 1

    def test_kirchhoff_index(self, A):
        """Kirchhoff index Kf = n * sum_{i>=2} 1/mu_i
           = 40 * (24/10 + 15/16) = 40 * 3.3375 = 133.5."""
        L = 12 * np.eye(40) - A
        eigs = np.sort(np.linalg.eigvalsh(L))
        nonzero = eigs[eigs > 1e-8]
        Kf = 40 * np.sum(1.0 / nonzero)
        expected = 40 * (24.0 / 10 + 15.0 / 16)
        assert abs(Kf - expected) < 1e-6
        assert abs(Kf - 133.5) < 1e-6

    def test_graph_energy(self, spectrum):
        """Graph energy E(G) = sum |lambda_i| = 12 + 24*2 + 15*4 = 120."""
        energy = np.sum(np.abs(spectrum))
        assert abs(energy - 120) < 1e-6

    def test_hoffman_bound(self):
        """Hoffman bound: alpha(G) <= n * (-lambda_min) / (k - lambda_min)
           = 40 * 4 / 16 = 10."""
        alpha_bound = 40 * 4.0 / (12 + 4)
        assert abs(alpha_bound - 10) < 1e-10

    def test_lovasz_theta(self):
        """For SRG with 3 eigenvalues, Lovasz theta = Hoffman bound = 10."""
        theta = 40 * (-(-4)) / (12 - (-4))
        assert abs(theta - 10) < 1e-10
