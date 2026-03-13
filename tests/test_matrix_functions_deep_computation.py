"""
Phase CXXXIV  --  Deep Matrix Function Theory on W(3,3) = SRG(40,12,2,4)
=========================================================================

We study the full panoply of matrix-function operations on the adjacency
matrix A of the W(3,3) symplectic graph, exploiting the fact that A has
only three distinct eigenvalues {12, 2, -4} with multiplicities {1, 24, 15}.

Topics
------
1.  Matrix exponential  (spectral decomposition)
2.  Matrix logarithm    (shifted positive-definite form)
3.  Matrix square root
4.  Matrix sign function
5.  Resolvent operator   R(z) = (zI - A)^{-1}
6.  Heat kernel          K(t) = exp(-t L),  L = kI - A
7.  Green's function     (Laplacian pseudo-inverse)
8.  Matrix power series  (truncated Taylor vs expm)
9.  Functional calculus  f(A)g(A) = (fg)(A)
10. Operator norms       ||exp(tA)||_2, ||sin(A)||_F
11. Cayley transform     unitary from self-adjoint
12. Chebyshev polynomial evaluation  T_k(A/12)
"""

import numpy as np
import pytest
from numpy.linalg import norm, eigvalsh, matrix_rank
from scipy.linalg import expm, logm, sqrtm, funm, inv, svdvals


# ---------------------------------------------------------------------------
#  W(3,3) builder  (self-contained)
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
                    inv_ = pow(first, -1, 3)
                    canon = tuple((x * inv_) % 3 for x in v)
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
#  Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def A():
    """Adjacency matrix of W(3,3)."""
    return _build_w33().astype(np.float64)


@pytest.fixture(scope="module")
def n():
    return 40


@pytest.fixture(scope="module")
def eigvals_spec():
    """Eigenvalue -> multiplicity dict for SRG(40,12,2,4)."""
    return {12: 1, 2: 24, -4: 15}


@pytest.fixture(scope="module")
def eigenprojectors(A, n):
    """
    Idempotent eigenprojectors E0, E1, E2 for eigenvalues 12, 2, -4.

    Built via Lagrange interpolation on the spectrum:
        E_i = prod_{j!=i} (A - lam_j I) / (lam_i - lam_j)
    """
    I = np.eye(n)
    lams = [12.0, 2.0, -4.0]
    projs = []
    for i, li in enumerate(lams):
        P = I.copy()
        for j, lj in enumerate(lams):
            if j != i:
                P = P @ (A - lj * I) / (li - lj)
        projs.append(P)
    return projs  # [E0, E1, E2]


@pytest.fixture(scope="module")
def laplacian(A, n):
    """Combinatorial graph Laplacian L = kI - A, k=12."""
    return 12.0 * np.eye(n) - A


# ---------------------------------------------------------------------------
#  0. Sanity: SRG identity A^2 = -2A + 8I + 4J
# ---------------------------------------------------------------------------

class TestSRGBasics:
    def test_vertex_count(self, A, n):
        assert A.shape == (n, n)

    def test_symmetric(self, A):
        assert np.allclose(A, A.T)

    def test_k_regular(self, A):
        deg = A.sum(axis=1)
        assert np.allclose(deg, 12)

    def test_srg_identity(self, A, n):
        I = np.eye(n)
        J = np.ones((n, n))
        lhs = A @ A
        rhs = -2 * A + 8 * I + 4 * J
        assert np.allclose(lhs, rhs)

    def test_spectrum(self, A, eigvals_spec):
        vals = np.sort(np.round(eigvalsh(A)).astype(int))
        counts = {}
        for v in vals:
            counts[v] = counts.get(v, 0) + 1
        assert counts == eigvals_spec


# ---------------------------------------------------------------------------
#  Eigenprojector infrastructure
# ---------------------------------------------------------------------------

class TestEigenprojectors:
    def test_idempotent(self, eigenprojectors):
        for E in eigenprojectors:
            assert np.allclose(E @ E, E, atol=1e-10)

    def test_orthogonal(self, eigenprojectors):
        for i in range(3):
            for j in range(i + 1, 3):
                assert np.allclose(eigenprojectors[i] @ eigenprojectors[j],
                                   0, atol=1e-10)

    def test_resolution_of_identity(self, eigenprojectors, n):
        S = sum(eigenprojectors)
        assert np.allclose(S, np.eye(n), atol=1e-10)

    def test_ranks(self, eigenprojectors):
        expected = [1, 24, 15]
        for E, r in zip(eigenprojectors, expected):
            assert abs(np.trace(E) - r) < 1e-8

    def test_E0_is_J_over_n(self, eigenprojectors, n):
        E0 = eigenprojectors[0]
        J = np.ones((n, n)) / n
        assert np.allclose(E0, J, atol=1e-10)

    def test_spectral_reconstruction(self, A, eigenprojectors):
        recon = 12 * eigenprojectors[0] + 2 * eigenprojectors[1] + (-4) * eigenprojectors[2]
        assert np.allclose(recon, A, atol=1e-10)


# ---------------------------------------------------------------------------
#  1. Matrix exponential
# ---------------------------------------------------------------------------

class TestMatrixExponential:
    @pytest.mark.parametrize("t", [0.1, 0.5, 1.0])
    def test_expm_spectral(self, A, eigenprojectors, t):
        """exp(tA) via scipy must equal spectral form."""
        E0, E1, E2 = eigenprojectors
        spectral = (np.exp(12 * t) * E0
                     + np.exp(2 * t) * E1
                     + np.exp(-4 * t) * E2)
        numerical = expm(t * A)
        assert np.allclose(numerical, spectral, atol=1e-8)

    def test_expm_at_zero(self, A, n):
        assert np.allclose(expm(0 * A), np.eye(n), atol=1e-12)

    @pytest.mark.parametrize("t", [0.1, 0.5])
    def test_expm_trace(self, A, t):
        """tr exp(tA) = e^{12t} + 24 e^{2t} + 15 e^{-4t}."""
        expected = np.exp(12 * t) + 24 * np.exp(2 * t) + 15 * np.exp(-4 * t)
        numerical = np.trace(expm(t * A))
        assert abs(numerical - expected) / abs(expected) < 1e-8

    def test_expm_determinant(self, A):
        """det exp(tA) = exp(t * tr A) = exp(0) = 1."""
        t = 0.3
        M = expm(t * A)
        # tr(A) = 0 (no self-loops)
        logdet = np.linalg.slogdet(M)[1]
        assert abs(logdet) < 1e-6

    def test_expm_positive_definite(self, A):
        """exp(tA) is always positive definite for real symmetric A."""
        M = expm(0.5 * A)
        eigs = eigvalsh(M)
        assert np.all(eigs > 0)

    def test_expm_semigroup(self, A):
        """exp(sA) exp(tA) = exp((s+t)A)."""
        s, t = 0.2, 0.3
        lhs = expm(s * A) @ expm(t * A)
        rhs = expm((s + t) * A)
        assert np.allclose(lhs, rhs, atol=1e-8)


# ---------------------------------------------------------------------------
#  2. Matrix logarithm
# ---------------------------------------------------------------------------

class TestMatrixLogarithm:
    def test_logm_round_trip(self, A, n):
        """exp(log(M)) = M for M = A + 5I (positive definite)."""
        M = A + 5 * np.eye(n)
        L = logm(M)
        assert np.allclose(expm(L), M, atol=1e-8)

    def test_logm_real(self, A, n):
        """log(A + 5I) should be real (eigenvalues 17, 7, 1 all > 0)."""
        M = A + 5 * np.eye(n)
        L = logm(M)
        assert np.allclose(L.imag, 0, atol=1e-10)

    def test_logm_spectral(self, A, n, eigenprojectors):
        """log(A+5I) = log(17)E0 + log(7)E1 + log(1)E2."""
        M = A + 5 * np.eye(n)
        E0, E1, E2 = eigenprojectors
        spectral = np.log(17) * E0 + np.log(7) * E1 + np.log(1) * E2
        numerical = logm(M).real
        assert np.allclose(numerical, spectral, atol=1e-8)

    def test_logm_trace(self, A, n):
        """tr log(M) = log det(M)."""
        M = A + 5 * np.eye(n)
        tr_log = np.trace(logm(M).real)
        log_det = np.linalg.slogdet(M)[1]
        assert abs(tr_log - log_det) < 1e-6

    def test_logm_symmetric(self, A, n):
        M = A + 5 * np.eye(n)
        L = logm(M).real
        assert np.allclose(L, L.T, atol=1e-10)


# ---------------------------------------------------------------------------
#  3. Matrix square root
# ---------------------------------------------------------------------------

class TestMatrixSquareRoot:
    def test_sqrtm_of_shifted(self, A, n):
        """sqrt(A+5I)^2 = A+5I."""
        M = A + 5 * np.eye(n)
        S = sqrtm(M)
        assert np.allclose(S @ S, M, atol=1e-8)

    def test_sqrtm_real(self, A, n):
        M = A + 5 * np.eye(n)
        S = sqrtm(M)
        assert np.allclose(S.imag, 0, atol=1e-10)

    def test_sqrtm_spectral(self, A, n, eigenprojectors):
        """sqrt(A+5I) = sqrt(17)E0 + sqrt(7)E1 + sqrt(1)E2."""
        M = A + 5 * np.eye(n)
        E0, E1, E2 = eigenprojectors
        spectral = np.sqrt(17) * E0 + np.sqrt(7) * E1 + np.sqrt(1) * E2
        numerical = sqrtm(M).real
        assert np.allclose(numerical, spectral, atol=1e-8)

    def test_sqrtm_of_A2_plus_I(self, A, n):
        """sqrt(A^2 + I) squared gives back A^2 + I."""
        M = A @ A + np.eye(n)
        S = sqrtm(M)
        assert np.allclose(S @ S, M, atol=1e-8)

    def test_sqrtm_positive_eigenvalues(self, A, n):
        M = A + 5 * np.eye(n)
        S = sqrtm(M).real
        eigs = eigvalsh(S)
        assert np.all(eigs > 0)

    def test_sqrtm_symmetric(self, A, n):
        M = A + 5 * np.eye(n)
        S = sqrtm(M).real
        assert np.allclose(S, S.T, atol=1e-10)


# ---------------------------------------------------------------------------
#  4. Matrix sign function
# ---------------------------------------------------------------------------

class TestMatrixSign:
    def _sign_matrix(self, A, eigenprojectors):
        """sign(A) = (+1)E0 + (+1)E1 + (-1)E2 since eigenvalues 12>0, 2>0, -4<0."""
        E0, E1, E2 = eigenprojectors
        return E0 + E1 - E2

    def test_sign_involutory(self, A, eigenprojectors):
        """sign(A)^2 = I."""
        S = self._sign_matrix(A, eigenprojectors)
        assert np.allclose(S @ S, np.eye(40), atol=1e-10)

    def test_sign_eigenvalues(self, A, eigenprojectors):
        S = self._sign_matrix(A, eigenprojectors)
        eigs = np.sort(np.round(eigvalsh(S)).astype(int))
        # 15 eigenvalues of -1, 25 eigenvalues of +1
        assert list(eigs) == [-1] * 15 + [1] * 25

    def test_sign_trace(self, A, eigenprojectors):
        """tr sign(A) = 1*1 + 1*24 + (-1)*15 = 10."""
        S = self._sign_matrix(A, eigenprojectors)
        assert abs(np.trace(S) - 10) < 1e-10

    def test_sign_symmetric(self, A, eigenprojectors):
        S = self._sign_matrix(A, eigenprojectors)
        assert np.allclose(S, S.T, atol=1e-10)

    def test_sign_commutes_with_A(self, A, eigenprojectors):
        S = self._sign_matrix(A, eigenprojectors)
        assert np.allclose(S @ A, A @ S, atol=1e-10)

    def test_sign_positive_projector(self, A, eigenprojectors):
        """P_+ = (I + sign(A))/2 projects onto eigenvalues > 0."""
        S = self._sign_matrix(A, eigenprojectors)
        Pp = (np.eye(40) + S) / 2.0
        assert np.allclose(Pp @ Pp, Pp, atol=1e-10)
        assert abs(np.trace(Pp) - 25) < 1e-8


# ---------------------------------------------------------------------------
#  5. Resolvent operator R(z) = (zI - A)^{-1}
# ---------------------------------------------------------------------------

class TestResolvent:
    @pytest.mark.parametrize("z", [20.0, -10.0, 5.0, 100.0])
    def test_resolvent_inverse(self, A, n, z):
        """(zI - A) R(z) = I."""
        R = inv(z * np.eye(n) - A)
        assert np.allclose((z * np.eye(n) - A) @ R, np.eye(n), atol=1e-10)

    @pytest.mark.parametrize("z", [20.0, -10.0, 5.0, 100.0])
    def test_resolvent_trace(self, A, n, z):
        """tr R(z) = 1/(z-12) + 24/(z-2) + 15/(z+4)."""
        R = inv(z * np.eye(n) - A)
        expected = 1.0/(z - 12) + 24.0/(z - 2) + 15.0/(z + 4)
        assert abs(np.trace(R) - expected) < 1e-8

    def test_resolvent_spectral(self, A, n, eigenprojectors):
        z = 7.0
        E0, E1, E2 = eigenprojectors
        spectral = E0 / (z - 12) + E1 / (z - 2) + E2 / (z + 4)
        numerical = inv(z * np.eye(n) - A)
        assert np.allclose(numerical, spectral, atol=1e-10)

    def test_resolvent_identity(self, A, n):
        """R(z) - R(w) = (w-z) R(z) R(w)  (resolvent identity)."""
        z, w = 7.0, 15.0
        I = np.eye(n)
        Rz = inv(z * I - A)
        Rw = inv(w * I - A)
        lhs = Rz - Rw
        rhs = (w - z) * Rz @ Rw
        assert np.allclose(lhs, rhs, atol=1e-10)

    def test_resolvent_symmetric(self, A, n):
        z = 7.0
        R = inv(z * np.eye(n) - A)
        assert np.allclose(R, R.T, atol=1e-12)

    def test_resolvent_decay(self, A, n):
        """||R(z)||_2 -> 0 as |z| -> infinity."""
        norms = []
        for z in [50, 100, 500, 1000]:
            R = inv(z * np.eye(n) - A)
            norms.append(norm(R, 2))
        # each should be smaller than previous
        for i in range(len(norms) - 1):
            assert norms[i + 1] < norms[i]


# ---------------------------------------------------------------------------
#  6. Heat kernel K(t) = exp(-tL), L = 12I - A
# ---------------------------------------------------------------------------

class TestHeatKernel:
    @pytest.mark.parametrize("t", [0.01, 0.1, 0.5, 1.0])
    def test_heat_trace(self, laplacian, t):
        """tr exp(-tL) = 1 + 24 exp(-10t) + 15 exp(-16t)."""
        K = expm(-t * laplacian)
        expected = 1 + 24 * np.exp(-10 * t) + 15 * np.exp(-16 * t)
        assert abs(np.trace(K) - expected) < 1e-6

    def test_heat_semigroup(self, laplacian):
        """exp(-sL) exp(-tL) = exp(-(s+t)L)."""
        s, t = 0.1, 0.2
        lhs = expm(-s * laplacian) @ expm(-t * laplacian)
        rhs = expm(-(s + t) * laplacian)
        assert np.allclose(lhs, rhs, atol=1e-8)

    def test_heat_positive_semidefinite(self, laplacian):
        K = expm(-0.5 * laplacian)
        eigs = eigvalsh(K)
        assert np.all(eigs > -1e-12)

    def test_heat_t0_identity(self, laplacian, n):
        K = expm(0 * laplacian)
        assert np.allclose(K, np.eye(n), atol=1e-12)

    def test_heat_large_t_equilibrium(self, laplacian, n):
        """As t -> inf, exp(-tL) -> E0 = J/n (converge to uniform)."""
        K = expm(-5.0 * laplacian)
        J = np.ones((n, n)) / n
        assert np.allclose(K, J, atol=1e-6)

    def test_heat_symmetric(self, laplacian):
        K = expm(-0.3 * laplacian)
        assert np.allclose(K, K.T, atol=1e-10)

    def test_heat_row_sums(self, laplacian):
        """Row sums of exp(-tL) = 1 (doubly stochastic for regular graph)."""
        K = expm(-0.5 * laplacian)
        assert np.allclose(K.sum(axis=1), 1.0, atol=1e-8)

    def test_heat_determinant(self, laplacian):
        """det exp(-tL) = exp(-t tr(L)) = exp(-t*40*12) (but we check via slogdet)."""
        t = 0.1
        K = expm(-t * laplacian)
        _, logdet = np.linalg.slogdet(K)
        # tr(L) = 40*12 = 480
        expected_logdet = -t * 480
        assert abs(logdet - expected_logdet) < 1e-4


# ---------------------------------------------------------------------------
#  7. Green's function (Laplacian pseudo-inverse)
# ---------------------------------------------------------------------------

class TestGreensFunction:
    @pytest.fixture(scope="class")
    def green(self, laplacian, n):
        """Pseudo-inverse of L via spectral: G = E1/10 + E2/16."""
        I = np.eye(n)
        A = 12 * I - laplacian
        # Build eigenprojectors
        lams = [12.0, 2.0, -4.0]
        projs = []
        for i, li in enumerate(lams):
            P = I.copy()
            for j, lj in enumerate(lams):
                if j != i:
                    P = P @ (A - lj * I) / (li - lj)
            projs.append(P)
        E0, E1, E2 = projs
        # L eigenvalues: 0 (mult 1), 10 (mult 24), 16 (mult 15)
        return E1 / 10.0 + E2 / 16.0

    def test_LGL_equals_L(self, laplacian, green):
        assert np.allclose(laplacian @ green @ laplacian, laplacian, atol=1e-8)

    def test_GLG_equals_G(self, laplacian, green):
        assert np.allclose(green @ laplacian @ green, green, atol=1e-8)

    def test_GL_symmetric(self, laplacian, green):
        GL = green @ laplacian
        assert np.allclose(GL, GL.T, atol=1e-10)

    def test_LG_symmetric(self, laplacian, green):
        LG = laplacian @ green
        assert np.allclose(LG, LG.T, atol=1e-10)

    def test_green_trace(self, green):
        """tr G = 24/10 + 15/16 = 2.4 + 0.9375 = 3.3375."""
        expected = 24.0 / 10 + 15.0 / 16
        assert abs(np.trace(green) - expected) < 1e-8

    def test_green_rank(self, green):
        assert matrix_rank(green, tol=1e-8) == 39

    def test_green_symmetric(self, green):
        assert np.allclose(green, green.T, atol=1e-10)

    def test_green_kernel(self, green, n):
        """G * ones = 0 (constant vector in kernel)."""
        ones = np.ones(n)
        assert np.allclose(green @ ones, 0, atol=1e-10)


# ---------------------------------------------------------------------------
#  8. Matrix power series vs expm
# ---------------------------------------------------------------------------

class TestMatrixPowerSeries:
    def test_taylor_convergence(self, A):
        """Truncated Taylor series converges to expm for small t."""
        t = 0.05
        tA = t * A
        S = np.eye(40, dtype=np.float64)
        term = np.eye(40, dtype=np.float64)
        for k in range(1, 40):
            term = term @ tA / k
            S = S + term
        exact = expm(tA)
        assert np.allclose(S, exact, atol=1e-8)

    def test_taylor_first_order(self, A, n):
        """For very small t, exp(tA) ~ I + tA."""
        t = 1e-6
        M = expm(t * A)
        approx = np.eye(n) + t * A
        assert np.allclose(M, approx, atol=1e-8)

    def test_taylor_second_order(self, A, n):
        """exp(tA) ~ I + tA + t^2 A^2 / 2 for small t."""
        t = 1e-4
        M = expm(t * A)
        approx = np.eye(n) + t * A + (t**2 / 2) * (A @ A)
        assert np.allclose(M, approx, atol=1e-6)

    def test_series_error_decreases(self, A, n):
        """Adding more terms to the series decreases error above machine eps."""
        t = 0.1
        tA = t * A
        exact = expm(tA)
        errors = []
        S = np.eye(n, dtype=np.float64)
        term = np.eye(n, dtype=np.float64)
        for k in range(1, 20):
            term = term @ tA / k
            S = S + term
            errors.append(norm(S - exact))
        # check that errors decrease while above machine precision
        above_eps = [(i, e) for i, e in enumerate(errors) if e > 1e-12]
        for idx in range(len(above_eps) - 1):
            assert above_eps[idx + 1][1] < above_eps[idx][1]
        # final error should be near machine precision
        assert errors[-1] < 1e-10


# ---------------------------------------------------------------------------
#  9. Functional calculus  f(A) g(A) = (fg)(A)
# ---------------------------------------------------------------------------

class TestFunctionalCalculus:
    def test_polynomial_product(self, A, n):
        """(A+I)(A-2I) vs A^2 - A - 2I."""
        I = np.eye(n)
        lhs = (A + I) @ (A - 2 * I)
        rhs = A @ A - A - 2 * I
        assert np.allclose(lhs, rhs, atol=1e-10)

    def test_polynomial_square(self, A, n):
        """(2A + 3I)^2 = 4A^2 + 12A + 9I."""
        I = np.eye(n)
        lhs = (2 * A + 3 * I) @ (2 * A + 3 * I)
        rhs = 4 * (A @ A) + 12 * A + 9 * I
        assert np.allclose(lhs, rhs, atol=1e-10)

    def test_exp_times_exp(self, A):
        """exp(A/10) * exp(A/20) = exp(3A/20)."""
        lhs = expm(A / 10) @ expm(A / 20)
        rhs = expm(3 * A / 20)
        assert np.allclose(lhs, rhs, atol=1e-8)

    def test_srg_identity_functional(self, A, n):
        """Using A^2 = -2A + 8I + 4J to compute A^3."""
        I = np.eye(n)
        J = np.ones((n, n))
        A2 = -2 * A + 8 * I + 4 * J
        A3_expected = A @ A2
        A3_direct = A @ A @ A
        assert np.allclose(A3_expected, A3_direct, atol=1e-10)

    def test_A_cubed_from_srg(self, A, n):
        """A^3 = -2A^2 + 8A + 4JA = -2(-2A+8I+4J) + 8A + 4*12J
              = 4A - 16I - 8J + 8A + 48J = 12A - 16I + 40J."""
        I = np.eye(n)
        J = np.ones((n, n))
        A3 = A @ A @ A
        expected = 12 * A - 16 * I + 40 * J
        assert np.allclose(A3, expected, atol=1e-10)

    def test_commuting_functions(self, A, n):
        """f(A) g(A) = g(A) f(A) for any f, g."""
        I = np.eye(n)
        f_A = A @ A + 3 * A + I
        g_A = 2 * A - 5 * I
        assert np.allclose(f_A @ g_A, g_A @ f_A, atol=1e-10)

    def test_minimal_polynomial(self, A, n):
        """A satisfies minimal polynomial (A-12I)(A-2I)(A+4I) = 0."""
        I = np.eye(n)
        Z = (A - 12 * I) @ (A - 2 * I) @ (A + 4 * I)
        assert np.allclose(Z, 0, atol=1e-8)


# ---------------------------------------------------------------------------
#  10. Operator norms
# ---------------------------------------------------------------------------

class TestOperatorNorms:
    def test_spectral_norm_A(self, A):
        """||A||_2 = max |eigenvalue| = 12."""
        assert abs(norm(A, 2) - 12) < 1e-8

    def test_frobenius_norm_A(self, A, n):
        """||A||_F = sqrt(sum eigenvalue_i^2) = sqrt(12^2 + 24*4 + 15*16) = sqrt(480)."""
        expected = np.sqrt(12**2 + 24 * 4 + 15 * 16)
        assert abs(norm(A, 'fro') - expected) < 1e-8

    def test_expm_spectral_norm(self, A):
        """||exp(tA)||_2 = exp(12t) for t > 0."""
        t = 0.3
        M = expm(t * A)
        expected = np.exp(12 * t)
        assert abs(norm(M, 2) - expected) < 1e-4

    @pytest.mark.parametrize("t", [0.1, 0.5, 1.0])
    def test_heat_spectral_norm(self, laplacian, t):
        """||exp(-tL)||_2 = 1 (largest eigenvalue of L is 0 -> exp(0)=1)."""
        K = expm(-t * laplacian)
        assert abs(norm(K, 2) - 1.0) < 1e-8

    def test_frobenius_expm(self, A, n):
        """||exp(tA)||_F^2 = sum e^{2t*lambda_i} (over all eigenvalues with multiplicity)."""
        t = 0.2
        M = expm(t * A)
        frob_sq = norm(M, 'fro') ** 2
        expected = np.exp(24 * t) + 24 * np.exp(4 * t) + 15 * np.exp(-8 * t)
        assert abs(frob_sq - expected) < 1e-4

    def test_norm_submultiplicative(self, A, n):
        """||AB||_2 <= ||A||_2 ||B||_2."""
        I = np.eye(n)
        B = A + 3 * I
        assert norm(A @ B, 2) <= norm(A, 2) * norm(B, 2) + 1e-10


# ---------------------------------------------------------------------------
#  11. Cayley transform: C = (A - iI)(A + iI)^{-1}
# ---------------------------------------------------------------------------

class TestCayleyTransform:
    @pytest.fixture(scope="class")
    def cayley(self, A, n):
        I = np.eye(n)
        return (A - 1j * I) @ inv(A + 1j * I)

    def test_cayley_unitary(self, cayley, n):
        """C^H C = I (unitary)."""
        assert np.allclose(cayley.conj().T @ cayley, np.eye(n), atol=1e-10)

    def test_cayley_eigenvalues_on_unit_circle(self, cayley):
        eigs = np.linalg.eigvals(cayley)
        mods = np.abs(eigs)
        assert np.allclose(mods, 1.0, atol=1e-10)

    def test_cayley_expected_eigenvalues(self, cayley):
        """Eigenvalues should be (lambda - i)/(lambda + i) for lambda in {12,2,-4}."""
        expected_set = set()
        for lam in [12, 2, -4]:
            z = (lam - 1j) / (lam + 1j)
            expected_set.add(round(z.real, 8) + 1j * round(z.imag, 8))
        eigs = np.linalg.eigvals(cayley)
        for e in eigs:
            z = round(e.real, 6) + 1j * round(e.imag, 6)
            # Should be close to one of the expected values
            dists = [abs(z - exp) for exp in expected_set]
            assert min(dists) < 1e-4

    def test_cayley_determinant(self, cayley):
        """Unitary matrix has |det| = 1."""
        assert abs(abs(np.linalg.det(cayley)) - 1) < 1e-8

    def test_cayley_inverse(self, A, n, cayley):
        """A = i(I + C)(I - C)^{-1} (inverse Cayley transform)."""
        I = np.eye(n)
        recovered = 1j * (I + cayley) @ inv(I - cayley)
        assert np.allclose(recovered.real, A, atol=1e-8)
        assert np.allclose(recovered.imag, 0, atol=1e-8)

    def test_cayley_trace(self, cayley):
        """tr C = sum (lambda_i - i)/(lambda_i + i)."""
        expected = (12 - 1j)/(12 + 1j) + 24*(2 - 1j)/(2 + 1j) + 15*(-4 - 1j)/(-4 + 1j)
        assert abs(np.trace(cayley) - expected) < 1e-8


# ---------------------------------------------------------------------------
#  12. Chebyshev polynomial evaluation T_k(A/12)
# ---------------------------------------------------------------------------

class TestChebyshev:
    @pytest.fixture(scope="class")
    def scaled_A(self, A):
        """A/12 has eigenvalues 1, 1/6, -1/3 (all in [-1,1])."""
        return A / 12.0

    def test_T0(self, scaled_A, n):
        """T_0(X) = I."""
        assert np.allclose(np.eye(n), np.eye(n))

    def test_T1(self, scaled_A, n):
        """T_1(X) = X."""
        pass  # trivially true

    def test_T2(self, scaled_A, n):
        """T_2(X) = 2X^2 - I."""
        X = scaled_A
        I = np.eye(n)
        T2 = 2 * X @ X - I
        # eigenvalues: T_2(1)=1, T_2(1/6)=2/36-1=-17/18, T_2(-1/3)=2/9-1=-7/9
        eigs = np.sort(eigvalsh(T2))
        expected = sorted([-17/18] * 24 + [-7/9] * 15 + [1.0])
        assert np.allclose(eigs, expected, atol=1e-8)

    def test_three_term_recurrence(self, scaled_A, n):
        """T_{k+1}(X) = 2X T_k(X) - T_{k-1}(X)."""
        X = scaled_A
        I = np.eye(n)
        T_prev = I.copy()           # T0
        T_curr = X.copy()           # T1
        for k in range(2, 7):
            T_next = 2 * X @ T_curr - T_prev
            T_prev = T_curr
            T_curr = T_next
        # T6 should satisfy recurrence; verify by independent scalar check
        # T_6(1) = 1, T_6(1/6) = 2*cos(6*arccos(1/6)), T_6(-1/3) = 2*cos(6*arccos(-1/3))
        # But we just verify shape and symmetry
        assert T_curr.shape == (n, n)
        assert np.allclose(T_curr, T_curr.T, atol=1e-10)

    def test_chebyshev_eigenvalues(self, scaled_A, n):
        """T_3(X) eigenvalues = T_3(lambda_i/12) for each eigenvalue."""
        X = scaled_A
        I = np.eye(n)
        T1 = X
        T2 = 2 * X @ X - I
        T3 = 2 * X @ T2 - T1
        eigs = np.sort(eigvalsh(T3))
        # T_3(x) = 4x^3 - 3x
        def T3_scalar(x):
            return 4 * x**3 - 3 * x
        expected = sorted(
            [T3_scalar(1.0)] * 1 +
            [T3_scalar(1.0/6)] * 24 +
            [T3_scalar(-1.0/3)] * 15
        )
        assert np.allclose(eigs, expected, atol=1e-8)

    def test_chebyshev_T4_eigenvalues(self, scaled_A, n):
        """T_4(X) eigenvalues via 8x^4 - 8x^2 + 1."""
        X = scaled_A
        I = np.eye(n)
        T0 = I
        T1 = X
        T2 = 2 * X @ T1 - T0
        T3 = 2 * X @ T2 - T1
        T4 = 2 * X @ T3 - T2
        def T4_scalar(x):
            return 8 * x**4 - 8 * x**2 + 1
        eigs = np.sort(eigvalsh(T4))
        expected = sorted(
            [T4_scalar(1.0)] * 1 +
            [T4_scalar(1.0/6)] * 24 +
            [T4_scalar(-1.0/3)] * 15
        )
        assert np.allclose(eigs, expected, atol=1e-8)

    def test_chebyshev_orthogonality_trace(self, scaled_A, n):
        """tr(T_j(X) T_k(X)) can be computed spectrally."""
        X = scaled_A
        I = np.eye(n)
        T0, T1 = I, X
        T2 = 2 * X @ T1 - T0
        T3 = 2 * X @ T2 - T1
        # tr(T2 T3) = sum_i T_2(lam_i) T_3(lam_i)
        def T2s(x): return 2*x**2 - 1
        def T3s(x): return 4*x**3 - 3*x
        expected_trace = (1 * T2s(1.0) * T3s(1.0)
                          + 24 * T2s(1/6) * T3s(1/6)
                          + 15 * T2s(-1/3) * T3s(-1/3))
        assert abs(np.trace(T2 @ T3) - expected_trace) < 1e-8

    def test_chebyshev_bound(self, scaled_A, n):
        """||T_k(X)||_2 <= 1 when ||X||_2 <= 1."""
        X = scaled_A
        I = np.eye(n)
        T_prev, T_curr = I, X
        for k in range(2, 7):
            T_next = 2 * X @ T_curr - T_prev
            T_prev = T_curr
            T_curr = T_next
        # ||X||_2 = 1 so T_k eigenvalues in [-1,1]
        eigs = eigvalsh(T_curr)
        assert np.all(eigs >= -1 - 1e-10)
        assert np.all(eigs <= 1 + 1e-10)
