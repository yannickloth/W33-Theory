"""
Phase CVI: Spectral Moments Computation on W(3,3) = SRG(40,12,2,4).

Tests verify spectral moments M_k = trace(A^k) and their algebraic,
combinatorial, information-theoretic, and analytic consequences.

W(3,3) spectrum: eigenvalue 12 (mult 1), 2 (mult 24), -4 (mult 15).
Spectral moment formula: M_k = 12^k + 24*2^k + 15*(-4)^k.
"""

import numpy as np
import pytest
import math


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


def _spectral_moment(k):
    """Closed-form M_k = 12^k + 24*2^k + 15*(-4)^k."""
    return 12**k + 24 * 2**k + 15 * (-4)**k


# ------------------------------------------------------------------ #
#  Module-scoped fixtures                                            #
# ------------------------------------------------------------------ #

@pytest.fixture(scope="module")
def A():
    return _build_w33()


@pytest.fixture(scope="module")
def eigenvalues(A):
    ev = np.linalg.eigvalsh(A)
    return np.sort(ev)


# ================================================================== #
#  1. Raw Moments  (~12 tests)                                       #
# ================================================================== #

class TestRawMoments:
    """Verify M0..M6 via both trace(A^k) and spectral formula."""

    def test_M0_identity_trace(self, A):
        """trace(I) = n = 40."""
        assert np.trace(np.eye(40, dtype=int)) == 40

    def test_M1_no_self_loops(self, A):
        """trace(A) = 0 (no self-loops in simple graph)."""
        assert np.trace(A) == 0

    def test_M2_equals_480(self, A):
        assert np.trace(A @ A) == 480

    def test_M3_equals_960(self, A):
        assert np.trace(A @ A @ A) == 960

    def test_M4_equals_24960(self, A):
        A2 = A @ A
        assert np.trace(A2 @ A2) == 24960

    def test_M5_equals_234240(self, A):
        A2 = A @ A
        assert np.trace(A2 @ A2 @ A) == 234240

    def test_M6_equals_3048960(self, A):
        A2 = A @ A
        A3 = A2 @ A
        assert np.trace(A3 @ A3) == 3048960

    def test_spectral_formula_M0(self):
        assert _spectral_moment(0) == 40

    def test_spectral_formula_M1(self):
        assert _spectral_moment(1) == 0

    def test_spectral_formula_M2(self):
        assert _spectral_moment(2) == 480

    def test_spectral_formula_M3_to_M6(self):
        assert _spectral_moment(3) == 960
        assert _spectral_moment(4) == 24960
        assert _spectral_moment(5) == 234240
        assert _spectral_moment(6) == 3048960

    def test_matrix_spectral_consistency_M0_through_M10(self, A):
        """trace(A^k) matches spectral formula for k = 0..10."""
        Ak = np.eye(40, dtype=int)
        for k in range(11):
            assert np.trace(Ak) == _spectral_moment(k), f"Mismatch at k={k}"
            Ak = Ak @ A


# ================================================================== #
#  2. Combinatorial Interpretations  (~10 tests)                     #
# ================================================================== #

class TestCombinatorialInterpretations:
    """M_k encode degree, triangles, SRG parameters, walk counts."""

    def test_degree_from_M2(self, A):
        """M2/n = k = 12 (degree of k-regular graph)."""
        assert np.trace(A @ A) == 40 * 12

    def test_triangle_count_from_M3(self, A):
        """M3/6 = 160 undirected triangles."""
        assert np.trace(A @ A @ A) == 6 * 160

    def test_triangles_per_vertex(self, A):
        """Each vertex lies in M3/(6n) = 4 triangles."""
        assert np.trace(A @ A @ A) == 6 * 40 * 4

    def test_edge_count(self, A):
        """Number of edges = nk/2 = 240."""
        assert np.sum(A) == 2 * 240

    def test_vertex_degree_uniformity(self, A):
        """Every vertex has degree exactly 12."""
        degrees = np.sum(A, axis=1)
        assert np.all(degrees == 12)

    def test_srg_equation(self, A):
        """SRG identity: A^2 = 4J - 2A + 8I  for  (n,k,lam,mu)=(40,12,2,4)."""
        n = 40
        J = np.ones((n, n), dtype=int)
        I = np.eye(n, dtype=int)
        assert np.array_equal(A @ A, 4 * J - 2 * A + 8 * I)

    def test_lambda_parameter_common_neighbors(self, A):
        """Adjacent pairs share exactly lambda = 2 common neighbors."""
        A2 = A @ A
        rows, cols = np.where(np.triu(A, k=1) == 1)
        for i, j in zip(rows, cols):
            assert A2[i, j] == 2

    def test_mu_parameter_common_neighbors(self, A):
        """Non-adjacent pairs share exactly mu = 4 common neighbors."""
        A2 = A @ A
        n = 40
        for i in range(n):
            for j in range(i + 1, n):
                if A[i, j] == 0:
                    assert A2[i, j] == 4

    def test_adjacency_symmetric(self, A):
        assert np.array_equal(A, A.T)

    def test_returning_walks_even_positive(self, A):
        """For even k >= 2, M_k > 0 (sum of even powers with positive weights)."""
        Ak = np.eye(40, dtype=int)
        for k in range(2, 9, 2):
            Ak_even = np.linalg.matrix_power(A, k)
            assert np.trace(Ak_even) > 0, f"M_{k} not positive"


# ================================================================== #
#  3. Moment Generating Function  (~10 tests)                        #
# ================================================================== #

class TestMomentGeneratingFunction:
    """Spectral density, moment ratios, kurtosis, Hamburger conditions."""

    def test_spectral_density_count(self, eigenvalues):
        """Exactly 40 eigenvalues (counted with multiplicity)."""
        assert len(eigenvalues) == 40

    def test_mean_eigenvalue_zero(self, eigenvalues):
        """Mean eigenvalue = M1/n = 0."""
        assert abs(np.mean(eigenvalues)) < 1e-10

    def test_variance_eigenvalue(self, eigenvalues):
        """Var(eigenvalue dist) = M2/n = 12."""
        assert abs(np.mean(eigenvalues**2) - 12.0) < 1e-10

    def test_moment_ratio_M4_over_M2_squared(self):
        """M4/M2^2 = 24960/230400 = 13/120."""
        ratio = _spectral_moment(4) / _spectral_moment(2)**2
        assert abs(ratio - 13.0 / 120.0) < 1e-14

    def test_skewness(self):
        """Skewness gamma_1 = m3/sigma^3 = 1/sqrt(3),  m_k := M_k/n."""
        m2 = _spectral_moment(2) / 40.0     # 12
        m3 = _spectral_moment(3) / 40.0     # 24
        sigma = math.sqrt(m2)
        gamma1 = m3 / sigma**3
        assert abs(gamma1 - 1.0 / math.sqrt(3)) < 1e-12

    def test_kurtosis(self):
        """Kurtosis kappa_4 = m4/sigma^4 = 13/3."""
        m2 = _spectral_moment(2) / 40.0     # 12
        m4 = _spectral_moment(4) / 40.0     # 624
        kappa4 = m4 / m2**2
        assert abs(kappa4 - 13.0 / 3.0) < 1e-12

    def test_excess_kurtosis(self):
        """Excess kurtosis = 13/3 - 3 = 4/3  (leptokurtic)."""
        m2 = _spectral_moment(2) / 40.0
        m4 = _spectral_moment(4) / 40.0
        excess = m4 / m2**2 - 3.0
        assert abs(excess - 4.0 / 3.0) < 1e-12

    def test_hamburger_H0_positive(self):
        """Hankel determinant H_0 = M_0 = 40 > 0."""
        assert _spectral_moment(0) > 0

    def test_hamburger_H1_positive(self):
        """H_1 = det([[M0,M1],[M1,M2]]) = 40*480 - 0 = 19200 > 0."""
        H1 = np.linalg.det(np.array([
            [_spectral_moment(0), _spectral_moment(1)],
            [_spectral_moment(1), _spectral_moment(2)],
        ], dtype=float))
        assert H1 > 0
        assert abs(H1 - 19200.0) < 1.0

    def test_hamburger_H3_zero_three_point_support(self):
        """4x4 Hankel matrix has rank 3 (spectrum supported on 3 points)."""
        M = [_spectral_moment(k) for k in range(7)]
        H3 = np.array([
            [M[0], M[1], M[2], M[3]],
            [M[1], M[2], M[3], M[4]],
            [M[2], M[3], M[4], M[5]],
            [M[3], M[4], M[5], M[6]],
        ], dtype=float)
        # Rank must be exactly 3 (one zero singular value)
        assert np.linalg.matrix_rank(H3) == 3
        # Smallest singular value is zero relative to largest
        svs = np.linalg.svd(H3, compute_uv=False)
        assert svs[-1] / svs[0] < 1e-12


# ================================================================== #
#  4. Zeta Function and Ihara  (~10 tests)                           #
# ================================================================== #

class TestZetaFunctionIhara:
    """Ihara zeta function:  Z(u)^{-1} = (1-u^2)^{m-n} det(I - uA + qu^2 I)."""

    @staticmethod
    def _ihara_det(A, u):
        """det(I - u*A + 11*u^2*I) evaluated at scalar u."""
        n = A.shape[0]
        M = (1.0 + 11.0 * u * u) * np.eye(n) - u * A
        return np.linalg.det(M)

    @staticmethod
    def _ihara_factored(u):
        """Product form: (1-12u+11u^2)*(1-2u+11u^2)^24*(1+4u+11u^2)^15."""
        f12 = 1.0 - 12.0 * u + 11.0 * u * u
        f2 = 1.0 - 2.0 * u + 11.0 * u * u
        fm4 = 1.0 + 4.0 * u + 11.0 * u * u
        return f12 * f2**24 * fm4**15

    def test_ihara_det_at_u_zero(self, A):
        """det(I) = 1 at u = 0."""
        assert abs(self._ihara_det(A, 0.0) - 1.0) < 1e-12

    def test_ihara_real_zero_u1(self, A):
        """u = 1 is a zero: min eigenvalue of (12I - A) is 0."""
        n = A.shape[0]
        M = 12.0 * np.eye(n) - A.astype(float)
        ev = np.linalg.eigvalsh(M)
        assert abs(min(ev)) < 1e-10

    def test_ihara_real_zero_u_inv11(self, A):
        """u = 1/11 is a zero: 1 - 12/11 + 1/11 = 0."""
        d = self._ihara_det(A, 1.0 / 11.0)
        assert abs(d) < 1e-6

    def test_ihara_factored_matches_det_at_005(self, A):
        """Factored product matches np.linalg.det at u = 0.05."""
        u = 0.05
        d1 = self._ihara_det(A, u)
        d2 = self._ihara_factored(u)
        assert abs(d1 / d2 - 1.0) < 1e-8

    def test_ihara_factored_matches_det_at_02(self, A):
        """Factored product matches np.linalg.det at u = 0.2."""
        u = 0.2
        d1 = self._ihara_det(A, u)
        d2 = self._ihara_factored(u)
        assert abs(d1 / d2 - 1.0) < 1e-6

    def test_edge_count_m(self, A):
        """m = nk/2 = 240 undirected edges."""
        assert np.sum(A) // 2 == 240

    def test_circuit_rank(self, A):
        """Circuit rank r = m - n + 1 = 201 (graph is connected)."""
        m = np.sum(A) // 2
        n = A.shape[0]
        assert m - n + 1 == 201

    def test_graph_connected(self, eigenvalues):
        """W(3,3) is connected: second-largest eigenvalue < k = 12."""
        sorted_ev = eigenvalues[::-1]  # descending
        assert sorted_ev[0] == pytest.approx(12.0, abs=1e-8)
        assert sorted_ev[1] < 12.0 - 1e-8

    def test_ihara_factor_roots_eigenvalue12(self):
        """Quadratic 1-12u+11u^2 = (1-u)(1-11u) roots at u=1, u=1/11."""
        # Roots of 11u^2 - 12u + 1 = 0
        disc = 144 - 44
        assert disc == 100
        r1 = (12 + 10) / 22
        r2 = (12 - 10) / 22
        assert abs(r1 - 1.0) < 1e-14
        assert abs(r2 - 1.0 / 11.0) < 1e-14

    def test_ihara_functional_equation(self, A):
        """xi(u) = 11^40 * u^80 * xi(1/(11u)) where xi = det(I-uA+11u^2 I)."""
        u = 0.2
        u_dual = 1.0 / (11.0 * u)
        # Compare in log space to avoid overflow
        xi_u = self._ihara_det(A, u)
        xi_dual = self._ihara_det(A, u_dual)
        # Both are negative (from the lambda=12 factor)
        log_ratio = math.log(abs(xi_u)) - math.log(abs(xi_dual))
        log_expected = 40.0 * math.log(11.0) + 80.0 * math.log(u)
        assert abs(log_ratio - log_expected) < 1e-4


# ================================================================== #
#  5. Newton's Identities  (~10 tests)                               #
# ================================================================== #

class TestNewtonsIdentities:
    """Minimal polynomial, elementary symmetric polys, power-sum recurrence."""

    def test_distinct_eigenvalues(self, eigenvalues):
        """Exactly 3 distinct eigenvalues: -4, 2, 12."""
        uniq = sorted(set(np.round(eigenvalues).astype(int)))
        assert uniq == [-4, 2, 12]

    def test_multiplicities(self, eigenvalues):
        """Multiplicities: 12 x 1, 2 x 24, -4 x 15."""
        rounded = np.round(eigenvalues).astype(int)
        counts = {}
        for v in rounded:
            counts[v] = counts.get(v, 0) + 1
        assert counts == {-4: 15, 2: 24, 12: 1}

    def test_elementary_symmetric_e1(self):
        """e1 = 12 + 2 + (-4) = 10  (sum of distinct eigenvalues)."""
        assert 12 + 2 + (-4) == 10

    def test_elementary_symmetric_e2(self):
        """e2 = 12*2 + 12*(-4) + 2*(-4) = -32."""
        assert 12 * 2 + 12 * (-4) + 2 * (-4) == -32

    def test_elementary_symmetric_e3(self):
        """e3 = 12 * 2 * (-4) = -96."""
        assert 12 * 2 * (-4) == -96

    def test_minimal_polynomial(self, A):
        """A satisfies its minimal polynomial: A^3 - 10A^2 - 32A + 96I = 0."""
        n = 40
        I = np.eye(n, dtype=int)
        A2 = A @ A
        A3 = A2 @ A
        residual = A3 - 10 * A2 - 32 * A + 96 * I
        assert np.array_equal(residual, np.zeros((n, n), dtype=int))

    def test_newton_p1(self):
        """p_1 = e_1 = 10  (power sum of distinct eigenvalues)."""
        p1 = 12 + 2 + (-4)
        assert p1 == 10

    def test_newton_p2(self):
        """p_2 = e1*p1 - 2*e2 = 100 + 64 = 164."""
        p2 = 12**2 + 2**2 + (-4)**2
        assert p2 == 164
        # Newton identity: p2 = e1*p1 - 2*e2
        assert 10 * 10 - 2 * (-32) == 164

    def test_newton_p3(self):
        """p_3 = e1*p2 - e2*p1 + 3*e3 = 1640 + 320 - 288 = 1672."""
        p3 = 12**3 + 2**3 + (-4)**3
        assert p3 == 1672
        # Newton identity
        assert 10 * 164 - (-32) * 10 + 3 * (-96) == 1672

    def test_cayley_hamilton_recurrence(self):
        """M_{k+3} = 10*M_{k+2} + 32*M_{k+1} - 96*M_k  for k >= 0."""
        for k in range(8):
            lhs = _spectral_moment(k + 3)
            rhs = 10 * _spectral_moment(k + 2) + 32 * _spectral_moment(k + 1) \
                  - 96 * _spectral_moment(k)
            assert lhs == rhs, f"Recurrence fails at k={k}"


# ================================================================== #
#  6. Spectral Entropy  (~10 tests)                                  #
# ================================================================== #

class TestSpectralEntropy:
    """Shannon, von Neumann, and Renyi entropies of the spectrum."""

    def test_density_matrix_trace_one(self, A):
        """rho = A^2/trace(A^2) has trace 1."""
        A2 = (A @ A).astype(float)
        rho = A2 / np.trace(A2)
        assert abs(np.trace(rho) - 1.0) < 1e-14

    def test_density_matrix_eigenvalues(self, A):
        """rho eigenvalues: 3/10 (x1), 1/120 (x24), 1/30 (x15)."""
        A2 = (A @ A).astype(float)
        rho = A2 / np.trace(A2)
        ev = sorted(np.linalg.eigvalsh(rho))
        # 24 copies of 1/120 ~ 0.00833, 15 copies of 1/30 ~ 0.03333, 1 copy of 3/10 = 0.3
        assert abs(ev[0] - 1.0 / 120.0) < 1e-10
        assert abs(ev[23] - 1.0 / 120.0) < 1e-10
        assert abs(ev[24] - 1.0 / 30.0) < 1e-10
        assert abs(ev[38] - 1.0 / 30.0) < 1e-10
        assert abs(ev[39] - 3.0 / 10.0) < 1e-10

    def test_density_matrix_positive_semidefinite(self, A):
        """All eigenvalues of rho are non-negative."""
        A2 = (A @ A).astype(float)
        rho = A2 / np.trace(A2)
        ev = np.linalg.eigvalsh(rho)
        assert np.all(ev > -1e-14)

    def test_von_neumann_entropy(self, A):
        """S_vN = -tr(rho ln rho) computed from exact eigenvalues."""
        # rho eigenvalues with multiplicities
        p = np.array([3.0 / 10.0] * 1 + [1.0 / 120.0] * 24 + [1.0 / 30.0] * 15)
        s_vn = -np.sum(p * np.log(p))
        # Compute directly from matrix
        A2 = (A @ A).astype(float)
        rho = A2 / np.trace(A2)
        ev = np.linalg.eigvalsh(rho)
        ev_pos = ev[ev > 1e-15]
        s_matrix = -np.sum(ev_pos * np.log(ev_pos))
        assert abs(s_vn - s_matrix) < 1e-10

    def test_von_neumann_entropy_bounds(self, A):
        """0 < S_vN < ln(40)."""
        p = np.array([3.0 / 10.0] * 1 + [1.0 / 120.0] * 24 + [1.0 / 30.0] * 15)
        s_vn = -np.sum(p * np.log(p))
        assert s_vn > 0
        assert s_vn < math.log(40)

    def test_renyi_purity(self, A):
        """tr(rho^2) = (3/10)^2 + 24*(1/120)^2 + 15*(1/30)^2 = 13/120."""
        A2 = (A @ A).astype(float)
        rho = A2 / np.trace(A2)
        purity = np.trace(rho @ rho)
        assert abs(purity - 13.0 / 120.0) < 1e-12

    def test_renyi_entropy_order2(self):
        """H_2 = -ln(tr(rho^2)) = -ln(13/120) = ln(120/13)."""
        h2 = -math.log(13.0 / 120.0)
        assert abs(h2 - math.log(120.0 / 13.0)) < 1e-14

    def test_shannon_spectral_entropy(self):
        """Shannon entropy of multiplicity distribution (1/40, 24/40, 15/40)."""
        p = np.array([1.0 / 40.0, 24.0 / 40.0, 15.0 / 40.0])
        s = -np.sum(p * np.log(p))
        # Must be positive and less than ln(3)
        assert s > 0
        assert s < math.log(3)

    def test_spectral_entropy_normalization(self):
        """Multiplicity distribution sums to 1."""
        p = np.array([1.0 / 40.0, 24.0 / 40.0, 15.0 / 40.0])
        assert abs(np.sum(p) - 1.0) < 1e-15

    def test_entropy_ordering(self):
        """von Neumann >= Renyi-2  (standard inequality)."""
        # von Neumann
        p_rho = np.array([3.0 / 10.0] * 1 + [1.0 / 120.0] * 24 + [1.0 / 30.0] * 15)
        s_vn = -np.sum(p_rho * np.log(p_rho))
        # Renyi-2
        h2 = -math.log(np.sum(p_rho**2))
        assert s_vn >= h2 - 1e-14


# ================================================================== #
#  7. Chebyshev Moments  (~10 tests)                                 #
# ================================================================== #

class TestChebyshevMoments:
    """Chebyshev expansion of the spectral density rescaled to [-1, 1]."""

    # Scaling: x = (lambda - 4) / 8 maps [-4, 12] -> [-1, 1]
    SCALED = {12: 1.0, 2: -0.25, -4: -1.0}
    MULTS = {12: 1, 2: 24, -4: 15}

    @staticmethod
    def _chebyshev_T(k, x):
        """Evaluate T_k(x) via recurrence. Pure numpy, no scipy."""
        if k == 0:
            return np.ones_like(x, dtype=float)
        if k == 1:
            return x.copy().astype(float)
        t_prev, t_curr = np.ones_like(x, dtype=float), x.copy().astype(float)
        for _ in range(k - 1):
            t_prev, t_curr = t_curr, 2.0 * x * t_curr - t_prev
        return t_curr

    def _mu(self, k):
        """k-th Chebyshev moment: (1/n) sum_i m_i T_k(x_i)."""
        val = 0.0
        for lam, m in self.MULTS.items():
            x = self.SCALED[lam]
            val += m * float(self._chebyshev_T(k, np.array([x]))[0])
        return val / 40.0

    def test_eigenvalue_scaling(self):
        """Scaled eigenvalues land in [-1, 1]: 12->1, 2->-1/4, -4->-1."""
        assert self.SCALED[12] == 1.0
        assert self.SCALED[2] == -0.25
        assert self.SCALED[-4] == -1.0

    def test_mu0_normalization(self):
        """mu_0 = 1 (T_0 = 1 everywhere)."""
        assert abs(self._mu(0) - 1.0) < 1e-14

    def test_mu1(self):
        """mu_1 = (1*1 + 24*(-1/4) + 15*(-1)) / 40 = -1/2."""
        assert abs(self._mu(1) - (-0.5)) < 1e-14

    def test_mu2(self):
        """mu_2 = -1/8.   T_2(x) = 2x^2 - 1."""
        assert abs(self._mu(2) - (-1.0 / 8.0)) < 1e-14

    def test_mu3(self):
        """mu_3 = 1/16.   T_3(x) = 4x^3 - 3x."""
        assert abs(self._mu(3) - 1.0 / 16.0) < 1e-14

    def test_mu4(self):
        """mu_4 = 23/32.   T_4(x) = 8x^4 - 8x^2 + 1."""
        assert abs(self._mu(4) - 23.0 / 32.0) < 1e-14

    def test_power_to_chebyshev_consistency(self):
        """mu_2 = 2<x^2> - 1 where <x^k> is the k-th power moment of scaled density."""
        # <x^2> = (1*1 + 24*(1/16) + 15*1) / 40 = (1+1.5+15)/40 = 17.5/40 = 7/16
        x2_avg = (1 * 1.0 + 24 * (0.25**2) + 15 * 1.0) / 40.0
        assert abs(x2_avg - 7.0 / 16.0) < 1e-14
        mu2_from_power = 2.0 * x2_avg - 1.0
        assert abs(mu2_from_power - self._mu(2)) < 1e-14

    def test_three_term_recurrence(self):
        """T_{k+1}(x) = 2x*T_k(x) - T_{k-1}(x)  at each scaled eigenvalue."""
        xs = np.array([1.0, -0.25, -1.0])
        for k in range(1, 8):
            tk_plus = self._chebyshev_T(k + 1, xs)
            tk = self._chebyshev_T(k, xs)
            tk_minus = self._chebyshev_T(k - 1, xs)
            recur = 2.0 * xs * tk - tk_minus
            assert np.allclose(tk_plus, recur, atol=1e-12), f"Recurrence fails at k={k}"

    def test_jackson_kernel_g0(self):
        """Jackson kernel g_0^{(N)} = 1  for any N."""
        for N in [10, 20, 50]:
            g0 = ((N + 1) * math.cos(0) + math.sin(0) / math.tan(math.pi / (N + 1))) / (N + 1)
            assert abs(g0 - 1.0) < 1e-12

    def test_jackson_kernel_decay(self):
        """Jackson damping factors g_k decrease with k for N = 20."""
        N = 20
        gs = []
        for k in range(N):
            if k == 0:
                g = 1.0
            else:
                g = ((N + 1 - k) * math.cos(math.pi * k / (N + 1))
                     + math.sin(math.pi * k / (N + 1)) / math.tan(math.pi / (N + 1))) / (N + 1)
            gs.append(abs(g))
        # g_0 should be largest; general trend is decreasing
        assert gs[0] >= gs[1]
        assert gs[0] >= gs[-1]


# ================================================================== #
#  8. Higher-Order Correlations  (~8 tests)                          #
# ================================================================== #

class TestHigherOrderCorrelations:
    """Spectral form factor, pair correlation, level spacing."""

    @staticmethod
    def _form_factor(t):
        """K(t) = |e^{12it} + 24 e^{2it} + 15 e^{-4it}|^2 / 1600."""
        s = (np.exp(12j * t) + 24.0 * np.exp(2j * t) + 15.0 * np.exp(-4j * t))
        return (abs(s)**2) / 1600.0

    @staticmethod
    def _form_factor_cos(t):
        """Closed form: (802 + 48 cos 10t + 30 cos 16t + 720 cos 6t) / 1600."""
        return (802.0 + 48.0 * math.cos(10 * t)
                + 30.0 * math.cos(16 * t)
                + 720.0 * math.cos(6 * t)) / 1600.0

    def test_form_factor_at_zero(self):
        """K(0) = 1 (all phases aligned)."""
        assert abs(self._form_factor(0.0) - 1.0) < 1e-14

    def test_form_factor_at_pi(self):
        """K(pi) = 1 (all eigenvalues are even integers)."""
        assert abs(self._form_factor(math.pi) - 1.0) < 1e-12

    def test_form_factor_at_pi_half(self):
        """K(pi/2) = |1 - 24 + 15|^2 / 1600 = 64/1600 = 1/25."""
        kval = self._form_factor(math.pi / 2.0)
        assert abs(kval - 1.0 / 25.0) < 1e-12

    def test_form_factor_cos_formula_consistency(self):
        """Exponential and cosine forms agree at several t values."""
        for t in [0.1, 0.5, 1.0, 2.0, math.pi / 3.0, math.pi / 6.0]:
            k1 = self._form_factor(t)
            k2 = self._form_factor_cos(t)
            assert abs(k1 - k2) < 1e-12, f"Mismatch at t={t}"

    def test_pair_correlation_total(self):
        """Sum of R_2 weights = n(n-1) = 1560."""
        mults = {12: 1, 2: 24, -4: 15}
        total = 0
        for la, ma in mults.items():
            for lb, mb in mults.items():
                if la == lb:
                    total += ma * (ma - 1)
                else:
                    total += ma * mb
        assert total == 40 * 39

    def test_level_spacings(self):
        """Distinct eigenvalues -4, 2, 12 give spacings 6, 10."""
        distinct = sorted([-4, 2, 12])
        spacings = [distinct[i + 1] - distinct[i] for i in range(len(distinct) - 1)]
        assert spacings == [6, 10]
        assert sum(spacings) / len(spacings) == 8.0

    def test_spectral_gap(self, eigenvalues):
        """Spectral gap = k - r = 12 - 2 = 10 (largest minus second-largest)."""
        desc = sorted(eigenvalues, reverse=True)
        gap = desc[0] - desc[1]
        assert abs(gap - 10.0) < 1e-8

    def test_form_factor_at_pi_third(self):
        """K(pi/3) = 1483/1600 via cosine formula."""
        kval = self._form_factor_cos(math.pi / 3.0)
        assert abs(kval - 1483.0 / 1600.0) < 1e-12
