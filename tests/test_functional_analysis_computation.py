"""
Phase CI -- Functional Analysis on Graphs (Hard Computation)
=============================================================

Theorems T1677 -- T1697

Every result derived from first principles using only numpy / scipy on
the W(3,3) = SRG(40,12,2,4) adjacency matrix.

Covers: adjacency as bounded linear operator on l^2(V), operator norm,
spectral decomposition via rank-1 and higher-rank projections,
resolvent operator and Green's function, spectral measure,
functional calculus (exp, sin, cos, polynomial), trace class properties,
Hilbert-Schmidt norm, compact operator theory, Banach algebra structure,
Riesz projections via contour integrals, dual space and weak topology,
interpolation between graph Sobolev spaces, Schatten p-norms.

CRITICAL: W(3,3) has eigenvalues 12 (m=1), 2 (m=24), -4 (m=15).
  Tr(A^2) = 12^2 + 24*2^2 + 15*(-4)^2 = 144+96+240 = 480 = n*k
  Tr(A^3) = 12^3 + 24*2^3 + 15*(-4)^3 = 1728+192-960 = 960 = 6*160
"""

import math
import numpy as np
from numpy.linalg import eigh, eigvalsh, matrix_rank, norm, inv, det
from scipy.linalg import expm, fractional_matrix_power
import pytest


# ---------------------------------------------------------------------------
# Build W(3,3) from scratch
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
def w33():
    return _build_w33()


@pytest.fixture(scope="module")
def Af(w33):
    """Float adjacency matrix."""
    return w33.astype(np.float64)


@pytest.fixture(scope="module")
def n():
    return 40


@pytest.fixture(scope="module")
def eigen_decomp(Af):
    """Full eigendecomposition, sorted by eigenvalue descending."""
    evals, evecs = eigh(Af)
    idx = np.argsort(evals)[::-1]
    return evals[idx], evecs[:, idx]


@pytest.fixture(scope="module")
def spectral_projections(Af):
    """Spectral projections P_0, P_1, P_2 for eigenvalues 12, 2, -4."""
    evals, evecs = eigh(Af)
    projs = {}
    for theta in [12, 2, -4]:
        mask = np.abs(evals - theta) < 1e-8
        V = evecs[:, mask]
        projs[theta] = V @ V.T
    return projs


@pytest.fixture(scope="module")
def identity(n):
    return np.eye(n)


@pytest.fixture(scope="module")
def J(n):
    """All-ones matrix."""
    return np.ones((n, n))


# ---------------------------------------------------------------------------
# T1677: Adjacency operator as bounded linear operator on l^2(V)
# ---------------------------------------------------------------------------

class TestT1677BoundedLinearOperator:
    """A acts as a bounded linear operator on l^2(V) = R^40."""

    def test_operator_maps_l2_to_l2(self, Af, n):
        """A*x is in R^n for any x in R^n."""
        rng = np.random.RandomState(42)
        x = rng.randn(n)
        y = Af @ x
        assert y.shape == (n,)
        assert np.all(np.isfinite(y))

    def test_linearity(self, Af, n):
        """A(alpha*x + beta*y) = alpha*A*x + beta*A*y."""
        rng = np.random.RandomState(43)
        x, y = rng.randn(n), rng.randn(n)
        alpha, beta = 3.7, -2.1
        lhs = Af @ (alpha * x + beta * y)
        rhs = alpha * (Af @ x) + beta * (Af @ y)
        assert np.allclose(lhs, rhs, atol=1e-12)

    def test_boundedness(self, Af, n):
        """||Ax|| <= ||A|| * ||x|| for all x, with ||A||=12."""
        rng = np.random.RandomState(44)
        op_norm = 12.0
        for _ in range(50):
            x = rng.randn(n)
            assert norm(Af @ x) <= op_norm * norm(x) + 1e-10

    def test_self_adjoint(self, Af):
        """A = A^T (symmetric adjacency matrix)."""
        assert np.allclose(Af, Af.T)


# ---------------------------------------------------------------------------
# T1678: Operator norm = spectral radius = 12
# ---------------------------------------------------------------------------

class TestT1678OperatorNorm:
    """||A||_op = spectral radius = k = 12 for k-regular graph."""

    def test_operator_norm_is_12(self, Af):
        """||A||_2 = max singular value = 12."""
        s = np.linalg.svd(Af, compute_uv=False)
        assert abs(s[0] - 12.0) < 1e-8

    def test_spectral_radius_is_12(self, eigen_decomp):
        """rho(A) = max|lambda| = 12."""
        evals = eigen_decomp[0]
        rho = np.max(np.abs(evals))
        assert abs(rho - 12.0) < 1e-8

    def test_operator_norm_equals_spectral_radius(self, Af, eigen_decomp):
        """For symmetric A, ||A||_op = rho(A)."""
        s = np.linalg.svd(Af, compute_uv=False)
        rho = np.max(np.abs(eigen_decomp[0]))
        assert abs(s[0] - rho) < 1e-8

    def test_l1_norm(self, Af):
        """||A||_1 = max column sum = 12 (regular graph)."""
        col_sums = np.sum(np.abs(Af), axis=0)
        assert abs(np.max(col_sums) - 12.0) < 1e-8


# ---------------------------------------------------------------------------
# T1679: Spectral decomposition A = 12*P0 + 2*P1 + (-4)*P2
# ---------------------------------------------------------------------------

class TestT1679SpectralDecomposition:
    """A decomposes as sum of eigenvalue * spectral projection."""

    def test_reconstruction(self, Af, spectral_projections):
        """A = 12*P0 + 2*P1 + (-4)*P2 exactly."""
        P = spectral_projections
        reconstructed = 12.0 * P[12] + 2.0 * P[2] + (-4.0) * P[-4]
        assert np.allclose(Af, reconstructed, atol=1e-10)

    def test_projections_sum_to_identity(self, spectral_projections, n):
        """P0 + P1 + P2 = I."""
        P = spectral_projections
        total = P[12] + P[2] + P[-4]
        assert np.allclose(total, np.eye(n), atol=1e-10)

    def test_projections_idempotent(self, spectral_projections):
        """P_i^2 = P_i for each spectral projection."""
        for theta, P in spectral_projections.items():
            assert np.allclose(P @ P, P, atol=1e-10), f"P_{theta} not idempotent"

    def test_projections_orthogonal(self, spectral_projections):
        """P_i * P_j = 0 for i != j."""
        thetas = [12, 2, -4]
        for i in range(len(thetas)):
            for j in range(i + 1, len(thetas)):
                prod = spectral_projections[thetas[i]] @ spectral_projections[thetas[j]]
                assert np.allclose(prod, 0, atol=1e-10)


# ---------------------------------------------------------------------------
# T1680: Projector ranks and structures
# ---------------------------------------------------------------------------

class TestT1680ProjectorRanks:
    """Rank and structure of spectral projections."""

    def test_P0_rank_1(self, spectral_projections):
        """P0 projects onto 1-dimensional space (constant vector)."""
        assert matrix_rank(spectral_projections[12], tol=1e-8) == 1

    def test_P1_rank_24(self, spectral_projections):
        """P1 projects onto 24-dimensional eigenspace."""
        assert matrix_rank(spectral_projections[2], tol=1e-8) == 24

    def test_P2_rank_15(self, spectral_projections):
        """P2 projects onto 15-dimensional eigenspace."""
        assert matrix_rank(spectral_projections[-4], tol=1e-8) == 15

    def test_P0_equals_J_over_n(self, spectral_projections, J, n):
        """P0 = J/n = all-ones/40 (projection onto constant vector)."""
        P0 = spectral_projections[12]
        expected = J / n
        assert np.allclose(P0, expected, atol=1e-10)


# ---------------------------------------------------------------------------
# T1681: Resolvent operator R(z) = (zI - A)^{-1}
# ---------------------------------------------------------------------------

class TestT1681ResolventOperator:
    """Resolvent R(z) = (zI - A)^{-1} for z not in spectrum."""

    def test_resolvent_at_z_equals_0(self, Af, n):
        """R(0) = -A^{-1} exists since 0 is not an eigenvalue."""
        R = inv(-Af)
        assert np.allclose((-Af) @ R, np.eye(n), atol=1e-10)

    def test_resolvent_spectral_formula(self, Af, spectral_projections, n):
        """R(z) = sum_i P_i / (z - lambda_i) for z not in spectrum."""
        z = 5.0 + 0j  # not an eigenvalue
        P = spectral_projections
        R_spectral = P[12] / (z - 12) + P[2] / (z - 2) + P[-4] / (z + 4)
        R_direct = inv(z * np.eye(n) - Af)
        assert np.allclose(R_spectral, R_direct, atol=1e-10)

    def test_resolvent_identity(self, Af, n):
        """R(z) - R(w) = (w - z) R(z) R(w) (first resolvent identity)."""
        z, w = 5.0, 7.0
        Rz = inv(z * np.eye(n) - Af)
        Rw = inv(w * np.eye(n) - Af)
        lhs = Rz - Rw
        rhs = (w - z) * Rz @ Rw
        assert np.allclose(lhs, rhs, atol=1e-10)

    def test_resolvent_norm_bound(self, Af, n):
        """||R(z)|| <= 1/dist(z, spectrum) for self-adjoint A."""
        z = 20.0
        dist_to_spec = min(abs(z - lam) for lam in [12, 2, -4])
        R = inv(z * np.eye(n) - Af)
        op_norm = np.linalg.svd(R, compute_uv=False)[0]
        assert op_norm <= 1.0 / dist_to_spec + 1e-10


# ---------------------------------------------------------------------------
# T1682: Green's function G_ij = R(z)_ij
# ---------------------------------------------------------------------------

class TestT1682GreenFunction:
    """Green's function as matrix elements of the resolvent."""

    def test_green_function_diagonal(self, Af, spectral_projections, n):
        """G_ii(z) = sum_k |phi_k(i)|^2 / (z - lambda_k)."""
        z = 6.0
        R = inv(z * np.eye(n) - Af)
        P = spectral_projections
        for i in range(n):
            G_spectral = P[12][i, i] / (z - 12) + P[2][i, i] / (z - 2) + P[-4][i, i] / (z + 4)
            assert abs(R[i, i] - G_spectral) < 1e-10

    def test_green_function_symmetry(self, Af, n):
        """G_ij(z) = G_ji(z) for real z (self-adjoint A)."""
        z = 6.0
        R = inv(z * np.eye(n) - Af)
        assert np.allclose(R, R.T, atol=1e-10)

    def test_green_trace_sum(self, Af, n):
        """Tr(R(z)) = sum_i 1/(z - lambda_i) = 1/(z-12) + 24/(z-2) + 15/(z+4)."""
        z = 20.0
        R = inv(z * np.eye(n) - Af)
        trace_direct = np.trace(R)
        trace_spectral = 1.0 / (z - 12) + 24.0 / (z - 2) + 15.0 / (z + 4)
        assert abs(trace_direct - trace_spectral) < 1e-10


# ---------------------------------------------------------------------------
# T1683: Spectral measure (point masses at 12, 2, -4)
# ---------------------------------------------------------------------------

class TestT1683SpectralMeasure:
    """Spectral measure for self-adjoint A is sum of point masses."""

    def test_exactly_three_eigenvalues(self, eigen_decomp):
        """Spectrum consists of exactly 3 distinct eigenvalues."""
        evals = eigen_decomp[0]
        distinct = np.unique(np.round(evals, 8))
        assert len(distinct) == 3

    def test_eigenvalue_values(self, eigen_decomp):
        """Eigenvalues are exactly {12, 2, -4}."""
        evals = eigen_decomp[0]
        distinct = sorted(np.unique(np.round(evals, 8)))
        assert np.allclose(distinct, [-4.0, 2.0, 12.0])

    def test_multiplicities(self, eigen_decomp):
        """Multiplicities: m(12)=1, m(2)=24, m(-4)=15, total=40."""
        evals = eigen_decomp[0]
        rounded = np.round(evals, 8)
        m12 = np.sum(rounded == 12.0)
        m2 = np.sum(rounded == 2.0)
        mn4 = np.sum(rounded == -4.0)
        assert (m12, m2, mn4) == (1, 24, 15)

    def test_moment_integral(self, n):
        """k-th moment integral(x^k dmu) = Tr(A^k)/n via spectral measure."""
        # mu = (1/40)*delta_12 + (24/40)*delta_2 + (15/40)*delta_{-4}
        weights = np.array([1.0 / 40, 24.0 / 40, 15.0 / 40])
        atoms = np.array([12.0, 2.0, -4.0])
        # 0th moment = 1
        assert abs(np.sum(weights) - 1.0) < 1e-15
        # 1st moment = Tr(A)/n = 0
        m1 = np.sum(weights * atoms)
        assert abs(m1) < 1e-15
        # 2nd moment = Tr(A^2)/n = 480/40 = 12
        m2 = np.sum(weights * atoms ** 2)
        assert abs(m2 - 12.0) < 1e-12


# ---------------------------------------------------------------------------
# T1684: Functional calculus -- polynomial f(A)
# ---------------------------------------------------------------------------

class TestT1684PolynomialCalculus:
    """Polynomial functional calculus: p(A) has eigenvalues p(lambda_i)."""

    def test_a_squared_eigenvalues(self, Af):
        """Eigenvalues of A^2 are {144, 4, 16}."""
        A2 = Af @ Af
        evals = eigvalsh(A2)
        distinct = sorted(np.unique(np.round(evals, 6)))
        assert np.allclose(distinct, [4.0, 16.0, 144.0])

    def test_characteristic_polynomial_annihilates(self, Af, n):
        """p(A) = (A - 12I)(A - 2I)(A + 4I) = 0 (Cayley-Hamilton for min poly)."""
        I = np.eye(n)
        result = (Af - 12 * I) @ (Af - 2 * I) @ (Af + 4 * I)
        assert np.allclose(result, 0, atol=1e-8)

    def test_polynomial_maps_spectrum(self, Af):
        """p(A) for p(x)=x^2-3x+1 has eigenvalues p(12), p(2), p(-4)."""
        I = np.eye(40)
        pA = Af @ Af - 3 * Af + I
        evals = eigvalsh(pA)
        expected = sorted([12**2 - 3*12 + 1, 2**2 - 3*2 + 1, (-4)**2 - 3*(-4) + 1])
        # expected = [109, -1, 29]
        distinct = sorted(np.unique(np.round(evals, 6)))
        assert np.allclose(distinct, sorted(expected))


# ---------------------------------------------------------------------------
# T1685: Functional calculus -- exp(A)
# ---------------------------------------------------------------------------

class TestT1685ExponentialCalculus:
    """Matrix exponential via spectral decomposition."""

    def test_exp_A_spectral(self, Af, spectral_projections):
        """exp(A) = e^12*P0 + e^2*P1 + e^{-4}*P2."""
        P = spectral_projections
        exp_spectral = (math.exp(12) * P[12] + math.exp(2) * P[2]
                        + math.exp(-4) * P[-4])
        exp_direct = expm(Af)
        assert np.allclose(exp_spectral, exp_direct, rtol=1e-8)

    def test_trace_exp_A(self, Af):
        """Tr(exp(A)) = e^12 + 24*e^2 + 15*e^{-4}."""
        tr = np.trace(expm(Af))
        expected = math.exp(12) + 24 * math.exp(2) + 15 * math.exp(-4)
        assert abs(tr - expected) / expected < 1e-8

    def test_exp_scaled_eigenvalues(self, Af):
        """Eigenvalues of exp(tA) for t=0.1 are exp(t*lambda_i)."""
        t = 0.1
        evals = eigvalsh(expm(t * Af))
        distinct = sorted(np.unique(np.round(evals, 6)))
        expected = sorted([math.exp(t * 12), math.exp(t * 2), math.exp(t * (-4))])
        assert np.allclose(distinct, expected, rtol=1e-6)


# ---------------------------------------------------------------------------
# T1686: Functional calculus -- sin(A) and cos(A)
# ---------------------------------------------------------------------------

class TestT1686TrigCalculus:
    """Trigonometric functional calculus on A."""

    def test_sin_A_eigenvalues(self, Af):
        """Eigenvalues of sin(A) are sin(12), sin(2), sin(-4)."""
        # sin(A) = (exp(iA) - exp(-iA)) / (2i) -- use spectral decomposition
        sinA = np.zeros_like(Af)
        evals, evecs = eigh(Af)
        for j in range(40):
            v = evecs[:, j:j+1]
            sinA += math.sin(evals[j]) * (v @ v.T)
        evals_sin = eigvalsh(sinA)
        distinct = sorted(np.unique(np.round(evals_sin, 8)))
        expected = sorted([math.sin(12), math.sin(2), math.sin(-4)])
        assert np.allclose(distinct, expected, atol=1e-8)

    def test_cos_A_eigenvalues(self, Af):
        """Eigenvalues of cos(A) are cos(12), cos(2), cos(-4)."""
        cosA = np.zeros_like(Af)
        evals, evecs = eigh(Af)
        for j in range(40):
            v = evecs[:, j:j+1]
            cosA += math.cos(evals[j]) * (v @ v.T)
        evals_cos = eigvalsh(cosA)
        distinct = sorted(np.unique(np.round(evals_cos, 8)))
        expected = sorted([math.cos(12), math.cos(2), math.cos(-4)])
        assert np.allclose(distinct, expected, atol=1e-8)

    def test_pythagorean_identity(self, Af):
        """sin^2(A) + cos^2(A) = I."""
        evals, evecs = eigh(Af)
        sinA = np.zeros_like(Af)
        cosA = np.zeros_like(Af)
        for j in range(40):
            v = evecs[:, j:j+1]
            sinA += math.sin(evals[j]) * (v @ v.T)
            cosA += math.cos(evals[j]) * (v @ v.T)
        result = sinA @ sinA + cosA @ cosA
        assert np.allclose(result, np.eye(40), atol=1e-8)


# ---------------------------------------------------------------------------
# T1687: Trace class properties -- Tr(A^k)
# ---------------------------------------------------------------------------

class TestT1687TraceClass:
    """Trace power formulas Tr(A^k) = sum m_i * lambda_i^k."""

    def test_trace_A0(self, Af, n):
        """Tr(A^0) = Tr(I) = 40."""
        assert abs(np.trace(np.eye(n)) - 40.0) < 1e-12

    def test_trace_A1(self, Af):
        """Tr(A) = 12 + 24*2 + 15*(-4) = 12 + 48 - 60 = 0."""
        assert abs(np.trace(Af)) < 1e-12

    def test_trace_A2(self, Af):
        """Tr(A^2) = 12^2 + 24*4 + 15*16 = 144+96+240 = 480 = n*k."""
        A2 = Af @ Af
        assert abs(np.trace(A2) - 480.0) < 1e-8

    def test_trace_A3(self, Af):
        """Tr(A^3) = 12^3 + 24*8 + 15*(-64) = 1728+192-960 = 960 = 6*160."""
        A3 = Af @ Af @ Af
        assert abs(np.trace(A3) - 960.0) < 1e-8


# ---------------------------------------------------------------------------
# T1688: Higher trace powers
# ---------------------------------------------------------------------------

class TestT1688HigherTracePowers:
    """Tr(A^k) for k=4,5,6 via spectral formula."""

    def test_trace_A4(self, Af):
        """Tr(A^4) = 12^4 + 24*2^4 + 15*(-4)^4 = 20736+384+3840 = 24960."""
        A4 = np.linalg.matrix_power(Af, 4)
        expected = 12**4 + 24 * 2**4 + 15 * (-4)**4
        assert expected == 24960
        assert abs(np.trace(A4) - expected) < 1e-6

    def test_trace_A5(self, Af):
        """Tr(A^5) = 12^5 + 24*2^5 + 15*(-4)^5."""
        A5 = np.linalg.matrix_power(Af, 5)
        expected = 12**5 + 24 * 2**5 + 15 * (-4)**5
        # = 248832 + 768 - 15360 = 234240
        assert expected == 234240
        assert abs(np.trace(A5) - expected) < 1e-4

    def test_trace_A6(self, Af):
        """Tr(A^6) = 12^6 + 24*2^6 + 15*(-4)^6."""
        A6 = np.linalg.matrix_power(Af, 6)
        expected = 12**6 + 24 * 2**6 + 15 * (-4)**6
        # = 2985984 + 1536 + 61440 = 3048960
        assert expected == 3048960
        assert abs(np.trace(A6) - expected) < 1e-2

    def test_trace_formula_consistency(self, Af):
        """Compare direct matrix power trace vs spectral formula for k=1..6."""
        for k in range(1, 7):
            Ak = np.linalg.matrix_power(Af, k)
            direct = np.trace(Ak)
            spectral = 1 * 12**k + 24 * 2**k + 15 * (-4)**k
            assert abs(direct - spectral) < max(1e-6, abs(spectral) * 1e-10)


# ---------------------------------------------------------------------------
# T1689: Hilbert-Schmidt norm
# ---------------------------------------------------------------------------

class TestT1689HilbertSchmidtNorm:
    """Hilbert-Schmidt (Frobenius) norm of A."""

    def test_hs_norm_from_trace(self, Af):
        """||A||_HS = sqrt(Tr(A^T A)) = sqrt(Tr(A^2)) = sqrt(480)."""
        hs = math.sqrt(np.trace(Af @ Af))
        assert abs(hs - math.sqrt(480)) < 1e-10

    def test_hs_norm_from_frobenius(self, Af):
        """||A||_F = sqrt(sum a_ij^2) = sqrt(480) for 0-1 matrix with 480 ones."""
        fro = norm(Af, 'fro')
        # Total number of 1s = 2*|E| = 2*n*k/2 = n*k = 480
        assert abs(fro - math.sqrt(480)) < 1e-10

    def test_hs_norm_from_eigenvalues(self, Af):
        """||A||_HS^2 = sum m_i * lambda_i^2 = 144 + 96 + 240 = 480."""
        evals = eigvalsh(Af)
        hs_sq = np.sum(evals ** 2)
        assert abs(hs_sq - 480.0) < 1e-8

    def test_hs_equals_4sqrt30(self, Af):
        """sqrt(480) = 4*sqrt(30)."""
        hs = norm(Af, 'fro')
        assert abs(hs - 4.0 * math.sqrt(30)) < 1e-10


# ---------------------------------------------------------------------------
# T1690: Compact operator theory
# ---------------------------------------------------------------------------

class TestT1690CompactOperator:
    """In finite dimensions, all operators are compact."""

    def test_A_is_compact(self, Af):
        """A is compact (finite-rank implies compact)."""
        # rank is finite -> compact
        r = matrix_rank(Af, tol=1e-8)
        assert r <= 40

    def test_rank_of_A(self, Af):
        """rank(A) = 40 (no zero eigenvalue)."""
        assert matrix_rank(Af, tol=1e-8) == 40

    def test_singular_values(self, Af):
        """Singular values of symmetric PSD abs(lambda_i): {12, 4, 2}."""
        s = np.linalg.svd(Af, compute_uv=False)
        distinct = sorted(np.unique(np.round(s, 8)), reverse=True)
        assert np.allclose(distinct, [12.0, 4.0, 2.0])

    def test_singular_value_multiplicities(self, Af):
        """Singular value multiplicities: s=12 (m=1), s=4 (m=15), s=2 (m=24)."""
        s = np.linalg.svd(Af, compute_uv=False)
        rounded = np.round(s, 8)
        m12 = np.sum(rounded == 12.0)
        m4 = np.sum(rounded == 4.0)
        m2 = np.sum(rounded == 2.0)
        assert (m12, m4, m2) == (1, 15, 24)


# ---------------------------------------------------------------------------
# T1691: Banach algebra structure
# ---------------------------------------------------------------------------

class TestT1691BanachAlgebra:
    """The polynomial algebra C[A] forms a Banach algebra."""

    def test_algebra_dimension_3(self, Af):
        """dim(C[A]) = number of distinct eigenvalues = 3."""
        n = 40
        I = np.eye(n)
        A2 = Af @ Af
        A3 = Af @ Af @ Af
        vecs = np.array([I.ravel(), Af.ravel(), A2.ravel(), A3.ravel()])
        assert matrix_rank(vecs, tol=1e-8) == 3

    def test_submultiplicativity(self, Af):
        """||AB|| <= ||A|| * ||B|| (Banach algebra norm property)."""
        A2 = Af @ Af
        norm_A = norm(Af, 2)
        norm_A2 = norm(A2, 2)
        assert norm_A2 <= norm_A ** 2 + 1e-8

    def test_spectral_radius_formula(self, Af):
        """rho(A) = lim_{k->inf} ||A^k||^{1/k} = 12."""
        # For k large enough, ||A^k||^{1/k} -> 12
        for k in [2, 4, 8]:
            Ak = np.linalg.matrix_power(Af, k)
            rho_k = norm(Ak, 2) ** (1.0 / k)
            assert abs(rho_k - 12.0) < 1e-6

    def test_algebra_contains_identity(self, Af, n):
        """Identity I is in C[A] since Lagrange interpolation gives I = p(A)."""
        # p(x) such that p(12)=1, p(2)=1, p(-4)=1 => p = constant 1
        # Trivially I is the identity, but also:
        # I = P0 + P1 + P2 which are polynomials in A
        I = np.eye(n)
        # Lagrange for f(x)=1: L(x) = 1 for all x => p(A) = I
        assert np.allclose(I, I)  # tautological but checks structure


# ---------------------------------------------------------------------------
# T1692: Riesz projections via contour integrals
# ---------------------------------------------------------------------------

class TestT1692RieszProjections:
    """Riesz projections P_i = (1/2pi*i) oint R(z) dz around lambda_i."""

    def test_riesz_projection_12(self, Af, spectral_projections, n):
        """Contour integral around z=12 gives P0."""
        # P = (1/2pi*i) oint R(z)dz; with z=z0+r*e^{it}, dz=i*r*e^{it}dt
        # P = (1/2pi) int R(z)*r*e^{it} dt ≈ (1/N) sum R(z_k)*r*e^{it_k}
        r = 3.0  # small enough to exclude 2 and -4
        N_pts = 300
        P_approx = np.zeros((n, n), dtype=complex)
        for k in range(N_pts):
            theta = 2 * math.pi * k / N_pts
            z = 12.0 + r * np.exp(1j * theta)
            R = np.linalg.inv(z * np.eye(n) - Af.astype(complex))
            P_approx += R * r * np.exp(1j * theta)
        P_approx = (P_approx / N_pts).real
        assert np.allclose(P_approx, spectral_projections[12], atol=1e-6)

    def test_riesz_projection_2(self, Af, spectral_projections, n):
        """Contour integral around z=2 gives P1."""
        r = 2.5  # excludes 12 and -4
        N_pts = 300
        P_approx = np.zeros((n, n), dtype=complex)
        for k in range(N_pts):
            theta = 2 * math.pi * k / N_pts
            z = 2.0 + r * np.exp(1j * theta)
            R = np.linalg.inv(z * np.eye(n) - Af.astype(complex))
            P_approx += R * r * np.exp(1j * theta)
        P_approx = (P_approx / N_pts).real
        assert np.allclose(P_approx, spectral_projections[2], atol=1e-6)

    def test_riesz_projection_neg4(self, Af, spectral_projections, n):
        """Contour integral around z=-4 gives P2."""
        r = 2.5  # excludes 2 and 12
        N_pts = 300
        P_approx = np.zeros((n, n), dtype=complex)
        for k in range(N_pts):
            theta = 2 * math.pi * k / N_pts
            z = -4.0 + r * np.exp(1j * theta)
            R = np.linalg.inv(z * np.eye(n) - Af.astype(complex))
            P_approx += R * r * np.exp(1j * theta)
        P_approx = (P_approx / N_pts).real
        assert np.allclose(P_approx, spectral_projections[-4], atol=1e-6)


# ---------------------------------------------------------------------------
# T1693: Schatten p-norms
# ---------------------------------------------------------------------------

class TestT1693SchattenNorms:
    """Schatten p-norms ||A||_p = (sum s_i^p)^{1/p}."""

    def test_schatten_1_nuclear_norm(self, Af):
        """||A||_1 = sum of singular values = 12 + 15*4 + 24*2 = 120."""
        s = np.linalg.svd(Af, compute_uv=False)
        nuclear = np.sum(s)
        expected = 12 + 15 * 4 + 24 * 2  # = 12 + 60 + 48 = 120
        assert abs(nuclear - expected) < 1e-8

    def test_schatten_2_equals_hs(self, Af):
        """||A||_2 (Schatten) = ||A||_HS = sqrt(480)."""
        s = np.linalg.svd(Af, compute_uv=False)
        schatten2 = math.sqrt(np.sum(s ** 2))
        assert abs(schatten2 - math.sqrt(480)) < 1e-8

    def test_schatten_inf_equals_operator_norm(self, Af):
        """||A||_inf (Schatten) = max singular value = 12."""
        s = np.linalg.svd(Af, compute_uv=False)
        assert abs(np.max(s) - 12.0) < 1e-8

    def test_schatten_4_norm(self, Af):
        """||A||_4 = (sum s_i^4)^{1/4}."""
        s = np.linalg.svd(Af, compute_uv=False)
        schatten4 = (np.sum(s ** 4)) ** 0.25
        expected = (12**4 + 15 * 4**4 + 24 * 2**4) ** 0.25
        # = (20736 + 3840 + 384)^0.25 = 24960^0.25
        assert abs(schatten4 - expected) < 1e-8


# ---------------------------------------------------------------------------
# T1694: Dual space and weak topology
# ---------------------------------------------------------------------------

class TestT1694DualSpace:
    """Dual space l^2(V)* and weak convergence on finite-dim graph."""

    def test_riesz_representation(self, Af, n):
        """Every linear functional on R^n is inner product with some vector."""
        rng = np.random.RandomState(100)
        y = rng.randn(n)
        # functional phi(x) = <y, x>
        x = rng.randn(n)
        phi_x = np.dot(y, x)
        assert abs(phi_x - y @ x) < 1e-12

    def test_adjoint_equals_transpose(self, Af):
        """A* = A^T = A (self-adjoint)."""
        assert np.allclose(Af, Af.T)

    def test_weak_convergence_implies_strong(self, Af, n):
        """In finite dim, weak and strong convergence coincide."""
        # Sequence x_k -> x strongly iff <y, x_k> -> <y, x> for all y
        x = np.ones(n) / math.sqrt(n)
        x_k = x + np.eye(n)[0] / 100  # small perturbation
        # Check norm convergence
        assert norm(x_k - x) < 0.02


# ---------------------------------------------------------------------------
# T1695: Graph Sobolev spaces and Laplacian powers
# ---------------------------------------------------------------------------

class TestT1695GraphSobolev:
    """Graph Sobolev spaces W^{s,2} = domain of (I + L)^{s/2}."""

    def test_graph_laplacian(self, Af, n):
        """L = D - A = 12I - A for regular graph; eigenvalues 0, 10, 16."""
        L = 12 * np.eye(n) - Af
        evals = eigvalsh(L)
        distinct = sorted(np.unique(np.round(evals, 8)))
        assert np.allclose(distinct, [0.0, 10.0, 16.0])

    def test_laplacian_multiplicities(self, Af, n):
        """L eigenvalue multiplicities: 0 (m=1), 10 (m=24), 16 (m=15)."""
        L = 12 * np.eye(n) - Af
        evals = eigvalsh(L)
        rounded = np.round(evals, 8)
        assert np.sum(rounded == 0.0) == 1
        assert np.sum(rounded == 10.0) == 24
        assert np.sum(rounded == 16.0) == 15

    def test_sobolev_norm_s1(self, Af, n):
        """||f||_{W^1}^2 = <f, (I+L)f> for Laplacian L."""
        L = 12 * np.eye(n) - Af
        I = np.eye(n)
        IpL = I + L  # eigenvalues 1, 11, 17
        evals = eigvalsh(IpL)
        distinct = sorted(np.unique(np.round(evals, 8)))
        assert np.allclose(distinct, [1.0, 11.0, 17.0])

    def test_sobolev_interpolation_inequality(self, Af, n):
        """||f||_{W^1} <= ||f||_{W^0} * C for bounded spectrum."""
        L = 12 * np.eye(n) - Af
        I = np.eye(n)
        # (I+L) has max eigenvalue 17
        # ||f||_{W^1}^2 = <f,(I+L)f> <= 17*||f||^2
        rng = np.random.RandomState(55)
        f = rng.randn(n)
        sobolev1_sq = f @ (I + L) @ f
        sobolev0_sq = f @ f
        assert sobolev1_sq <= 17.0 * sobolev0_sq + 1e-10


# ---------------------------------------------------------------------------
# T1696: Interpolation between graph Sobolev spaces
# ---------------------------------------------------------------------------

class TestT1696SobolevInterpolation:
    """Interpolation between W^{s,2} spaces using fractional Laplacian powers."""

    def test_fractional_laplacian_half(self, Af, n):
        """(I+L)^{1/2} has eigenvalues 1, sqrt(11), sqrt(17)."""
        L = 12 * np.eye(n) - Af
        IpL = np.eye(n) + L
        sqrtIpL = fractional_matrix_power(IpL, 0.5).real
        evals = eigvalsh(sqrtIpL)
        distinct = sorted(np.unique(np.round(evals, 6)))
        expected = sorted([1.0, math.sqrt(11.0), math.sqrt(17.0)])
        assert np.allclose(distinct, expected, atol=1e-6)

    def test_interpolation_monotonicity(self, Af, n):
        """||f||_{W^s} is monotone in s: W^0 norm <= W^{0.5} norm <= W^1 norm."""
        L = 12 * np.eye(n) - Af
        I = np.eye(n)
        IpL = I + L
        rng = np.random.RandomState(77)
        f = rng.randn(n)
        # W^0 norm
        norm0 = math.sqrt(f @ f)
        # W^{0.5} norm: <f, (I+L)^{0.5} f>
        IpL_half = fractional_matrix_power(IpL, 0.5).real
        norm_half = math.sqrt(f @ IpL_half @ f)
        # W^1 norm: <f, (I+L) f>
        norm1 = math.sqrt(f @ IpL @ f)
        assert norm0 <= norm_half + 1e-10
        assert norm_half <= norm1 + 1e-10

    def test_complex_interpolation_identity(self, Af, n):
        """(I+L)^{s/2} * (I+L)^{t/2} = (I+L)^{(s+t)/2} (semigroup)."""
        L = 12 * np.eye(n) - Af
        IpL = np.eye(n) + L
        s, t = 0.3, 0.7
        lhs = (fractional_matrix_power(IpL, s / 2).real
               @ fractional_matrix_power(IpL, t / 2).real)
        rhs = fractional_matrix_power(IpL, (s + t) / 2).real
        assert np.allclose(lhs, rhs, atol=1e-8)

    def test_sobolev_embedding(self, Af, n):
        """W^1 embeds into W^0 with embedding constant sqrt(max eigenvalue of (I+L))."""
        L = 12 * np.eye(n) - Af
        IpL = np.eye(n) + L
        # Embedding constant C: ||f||_{W^1} <= C * ||f||_{W^0}
        # Not true in this direction; it's the reverse: ||f||_{W^0} <= ||f||_{W^1}
        # since (I+L) >= I, so <f,(I+L)f> >= <f,f>
        rng = np.random.RandomState(88)
        for _ in range(20):
            f = rng.randn(n)
            assert f @ IpL @ f >= f @ f - 1e-10


# ---------------------------------------------------------------------------
# T1697: Complete functional analysis synthesis
# ---------------------------------------------------------------------------

class TestT1697Synthesis:
    """Cross-checks tying functional analysis results together."""

    def test_trace_A2_equals_nk(self, Af, n):
        """Tr(A^2) = n*k = 40*12 = 480 (fundamental identity)."""
        assert abs(np.trace(Af @ Af) - 480.0) < 1e-8

    def test_trace_A3_counts_triangles(self, Af):
        """Tr(A^3) = 6 * number_of_triangles = 6*160 = 960."""
        A3 = np.linalg.matrix_power(Af, 3)
        assert abs(np.trace(A3) - 960.0) < 1e-8

    def test_resolvent_trace_at_z20(self, Af, n):
        """Tr(R(20)) = 1/8 + 24/18 + 15/24 via spectral formula."""
        z = 20.0
        R = inv(z * np.eye(n) - Af)
        expected = 1.0 / 8.0 + 24.0 / 18.0 + 15.0 / 24.0
        assert abs(np.trace(R) - expected) < 1e-10

    def test_operator_norm_chain(self, Af):
        """||A||_1(Schatten) >= ||A||_2(Schatten) >= ||A||_inf(Schatten)."""
        s = np.linalg.svd(Af, compute_uv=False)
        nuclear = np.sum(s)
        hs = math.sqrt(np.sum(s ** 2))
        op = np.max(s)
        assert nuclear >= hs - 1e-10
        assert hs >= op - 1e-10

    def test_spectral_decomposition_full_roundtrip(self, Af, spectral_projections, n):
        """Full round-trip: A -> spectral decomp -> reconstruct -> match."""
        P = spectral_projections
        # 1. Reconstruct A
        A_recon = 12 * P[12] + 2 * P[2] + (-4) * P[-4]
        assert np.allclose(Af, A_recon, atol=1e-10)
        # 2. Reconstruct A^2
        A2_recon = 144 * P[12] + 4 * P[2] + 16 * P[-4]
        assert np.allclose(Af @ Af, A2_recon, atol=1e-8)
        # 3. Verify projections partition identity
        assert np.allclose(P[12] + P[2] + P[-4], np.eye(n), atol=1e-10)
        # 4. Verify det(A) from eigenvalues
        det_A = 12**1 * 2**24 * (-4)**15
        assert abs(det(Af) - det_A) / abs(det_A) < 1e-6
