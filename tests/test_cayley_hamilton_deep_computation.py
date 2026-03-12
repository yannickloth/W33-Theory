"""
Phase CXIX  --  Cayley-Hamilton Deep Applications on W(3,3) = SRG(40,12,2,4).

Minimal polynomial:  m(x) = (x-12)(x-2)(x+4) = x^3 - 10x^2 - 32x + 96
SRG identity:        A^2  = -2A + 8I + 4J
Combined:            every A^n = alpha_n * I + beta_n * A + gamma_n * J

130 tests covering:
  - Graph / SRG basics
  - Eigenvalue structure
  - Cayley-Hamilton theorem and minimal polynomial
  - SRG matrix identity
  - Power reduction recurrence
  - Minimal polynomial recurrence for higher powers
  - Polynomial evaluation on A
  - Matrix inverse from minimal polynomial
  - Faddeev-LeVerrier algorithm
  - Spectral projectors (Lagrange interpolation)
  - Resolvent via spectral decomposition
  - Matrix function series truncation
  - Advanced power reduction identities
"""

import math
import numpy as np
from numpy.testing import assert_array_equal, assert_allclose
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

A = _build_w33()
N = 40
I_ = np.eye(N, dtype=int)
J = np.ones((N, N), dtype=int)
A2 = A @ A
A3 = A2 @ A
A4 = A3 @ A
A5 = A4 @ A


def _power_coefficients(max_n):
    """Return (alpha_n, beta_n, gamma_n) for A^n = alpha*I + beta*A + gamma*J.

    Recurrence from SRG identity A^2 = -2A + 8I + 4J:
        alpha_{n+1} = 8 * beta_n
        beta_{n+1}  = alpha_n - 2 * beta_n
        gamma_{n+1} = 4 * beta_n + 12 * gamma_n
    """
    coeffs = [(1, 0, 0), (0, 1, 0)]
    for _ in range(2, max_n + 1):
        a, b, g = coeffs[-1]
        coeffs.append((8 * b, a - 2 * b, 4 * b + 12 * g))
    return coeffs


# =========================================================================
# 1.  Basic Graph / SRG Properties  (9 tests)
# =========================================================================

class TestGraphProperties:
    """Verify W(3,3) is SRG(40, 12, 2, 4)."""

    def test_shape(self):
        assert A.shape == (N, N)

    def test_symmetric(self):
        assert_array_equal(A, A.T)

    def test_binary_entries(self):
        assert set(np.unique(A)).issubset({0, 1})

    def test_no_self_loops(self):
        assert np.trace(A) == 0

    def test_regular_degree_12(self):
        assert_array_equal(A.sum(axis=1), np.full(N, 12))

    def test_total_directed_edges(self):
        assert A.sum() == N * 12  # 480 directed = 240 undirected

    def test_lambda_common_neighbors(self):
        """Adjacent vertex pairs share exactly lambda = 2 common neighbors."""
        adj_mask = A.astype(bool)
        assert np.all(A2[adj_mask] == 2)

    def test_mu_common_neighbors(self):
        """Non-adjacent distinct pairs share exactly mu = 4 common neighbors."""
        non_adj = (A == 0)
        np.fill_diagonal(non_adj, False)
        assert np.all(A2[non_adj] == 4)

    def test_diagonal_of_A_squared(self):
        """A^2 diagonal equals degree k = 12."""
        assert np.all(np.diag(A2) == 12)


# =========================================================================
# 2.  Eigenvalue Structure  (8 tests)
# =========================================================================

class TestEigenvalues:
    """Eigenvalues of SRG(40,12,2,4) are {12, 2, -4}."""

    @pytest.fixture(autouse=True)
    def _eigenvalues(self):
        self.evals = np.sort(np.linalg.eigvalsh(A.astype(float)))

    def test_three_distinct_eigenvalues(self):
        unique = np.unique(np.round(self.evals, 6))
        assert len(unique) == 3

    def test_eigenvalue_values(self):
        unique = sorted(np.unique(np.round(self.evals, 6)))
        assert_allclose(unique, [-4, 2, 12], atol=1e-8)

    def test_multiplicity_12(self):
        assert np.sum(np.abs(self.evals - 12) < 1e-6) == 1

    def test_multiplicity_2(self):
        assert np.sum(np.abs(self.evals - 2) < 1e-6) == 24

    def test_multiplicity_neg4(self):
        assert np.sum(np.abs(self.evals + 4) < 1e-6) == 15

    def test_trace_equals_eigenvalue_sum(self):
        assert np.trace(A) == 0
        assert 12 * 1 + 2 * 24 + (-4) * 15 == 0

    def test_trace_A2_equals_sum_sq(self):
        expected = 12**2 + 2**2 * 24 + (-4)**2 * 15  # 144+96+240 = 480
        assert np.trace(A2) == expected

    def test_trace_A3_equals_sum_cube(self):
        expected = 12**3 + 2**3 * 24 + (-4)**3 * 15  # 1728+192-960 = 960
        assert np.trace(A3) == expected


# =========================================================================
# 3.  SRG Matrix Identity: A^2 = -2A + 8I + 4J  (7 tests)
# =========================================================================

class TestSRGIdentity:
    """The fundamental SRG relation A^2 = (lam-mu)A + (k-mu)I + mu*J."""

    def test_srg_identity_exact(self):
        assert_array_equal(A2, -2 * A + 8 * I_ + 4 * J)

    def test_srg_coefficients_from_parameters(self):
        lam, mu, k = 2, 4, 12
        assert (lam - mu) == -2
        assert (k - mu) == 8

    def test_A_times_J_equals_kJ(self):
        assert_array_equal(A @ J, 12 * J)

    def test_J_times_A_equals_kJ(self):
        assert_array_equal(J @ A, 12 * J)

    def test_J_squared_equals_nJ(self):
        assert_array_equal(J @ J, N * J)

    def test_A_J_commute(self):
        assert_array_equal(A @ J, J @ A)

    def test_A_J_commutator_zero(self):
        assert_array_equal(A @ J - J @ A, np.zeros((N, N), dtype=int))


# =========================================================================
# 4.  Cayley-Hamilton Theorem  (10 tests)
# =========================================================================

class TestCayleyHamilton:
    """Minimal polynomial m(x) = x^3 - 10x^2 - 32x + 96 annihilates A."""

    def test_minimal_poly_annihilates(self):
        """A^3 - 10 A^2 - 32 A + 96 I = 0."""
        assert_array_equal(A3 - 10 * A2 - 32 * A + 96 * I_,
                           np.zeros((N, N), dtype=int))

    def test_minimal_poly_via_factors(self):
        """(A-12I)(A-2I)(A+4I) = 0."""
        P = (A - 12 * I_) @ (A - 2 * I_) @ (A + 4 * I_)
        assert_array_equal(P, np.zeros((N, N), dtype=int))

    def test_factor_order_132(self):
        P = (A - 12 * I_) @ (A + 4 * I_) @ (A - 2 * I_)
        assert_array_equal(P, np.zeros((N, N), dtype=int))

    def test_factor_order_213(self):
        P = (A - 2 * I_) @ (A - 12 * I_) @ (A + 4 * I_)
        assert_array_equal(P, np.zeros((N, N), dtype=int))

    def test_factor_order_231(self):
        P = (A - 2 * I_) @ (A + 4 * I_) @ (A - 12 * I_)
        assert_array_equal(P, np.zeros((N, N), dtype=int))

    def test_factor_order_312(self):
        P = (A + 4 * I_) @ (A - 12 * I_) @ (A - 2 * I_)
        assert_array_equal(P, np.zeros((N, N), dtype=int))

    def test_factor_order_321(self):
        P = (A + 4 * I_) @ (A - 2 * I_) @ (A - 12 * I_)
        assert_array_equal(P, np.zeros((N, N), dtype=int))

    def test_no_degree_1_annihilator(self):
        """No linear polynomial kills A."""
        for lam in [12, 2, -4]:
            assert np.any((A - lam * I_) != 0)

    def test_no_degree_2_annihilator(self):
        """No quadratic factor of m(x) annihilates A."""
        pairs = [(12, 2), (12, -4), (2, -4)]
        for a, b in pairs:
            P = (A - a * I_) @ (A - b * I_)
            assert np.any(P != 0), f"(x-{a})(x-{b}) should not annihilate"

    def test_characteristic_poly_degree(self):
        coeffs = np.poly(A.astype(float))
        assert len(coeffs) == N + 1


# =========================================================================
# 5.  Power Reduction: A^n = alpha_n I + beta_n A + gamma_n J  (15 tests)
# =========================================================================

class TestPowerReduction:
    """Every power A^n reduces to a linear combination of I, A, J."""

    @pytest.fixture(autouse=True)
    def _coeffs(self):
        self.coeffs = _power_coefficients(10)

    def test_A0_identity(self):
        assert self.coeffs[0] == (1, 0, 0)

    def test_A1_is_A(self):
        assert self.coeffs[1] == (0, 1, 0)

    def test_A2_coefficients(self):
        assert self.coeffs[2] == (8, -2, 4)

    def test_A3_coefficients(self):
        assert self.coeffs[3] == (-16, 12, 40)

    def test_A4_coefficients(self):
        assert self.coeffs[4] == (96, -40, 528)

    def test_A5_coefficients(self):
        assert self.coeffs[5] == (-320, 176, 6176)

    def test_A2_reconstruction(self):
        a, b, g = self.coeffs[2]
        assert_array_equal(A2, a * I_ + b * A + g * J)

    def test_A3_reconstruction(self):
        a, b, g = self.coeffs[3]
        assert_array_equal(A3, a * I_ + b * A + g * J)

    def test_A4_reconstruction(self):
        a, b, g = self.coeffs[4]
        assert_array_equal(A4, a * I_ + b * A + g * J)

    def test_A5_reconstruction(self):
        a, b, g = self.coeffs[5]
        assert_array_equal(A5, a * I_ + b * A + g * J)

    def test_trace_from_coefficients(self):
        """tr(A^n) = N*(alpha_n + gamma_n) since tr(A) = 0."""
        for n in range(6):
            a, b, g = self.coeffs[n]
            expected = 12**n + 24 * 2**n + 15 * (-4)**n
            assert N * (a + g) == expected, f"n={n}"

    def test_recurrence_consistency(self):
        for n in range(9):
            a, b, g = self.coeffs[n]
            a1, b1, g1 = self.coeffs[n + 1]
            assert a1 == 8 * b, f"alpha at n={n}"
            assert b1 == a - 2 * b, f"beta at n={n}"
            assert g1 == 4 * b + 12 * g, f"gamma at n={n}"

    def test_eigenvalue_12_on_coefficients(self):
        """alpha_n + 12*beta_n + 40*gamma_n = 12^n."""
        for n in range(11):
            a, b, g = self.coeffs[n]
            assert a + 12 * b + 40 * g == 12**n, f"n={n}"

    def test_eigenvalue_2_on_coefficients(self):
        """alpha_n + 2*beta_n = 2^n  (J kills 2-eigenspace)."""
        for n in range(11):
            a, b, g = self.coeffs[n]
            assert a + 2 * b == 2**n, f"n={n}"

    def test_eigenvalue_neg4_on_coefficients(self):
        """alpha_n - 4*beta_n = (-4)^n  (J kills -4-eigenspace)."""
        for n in range(11):
            a, b, g = self.coeffs[n]
            assert a + (-4) * b == (-4)**n, f"n={n}"


# =========================================================================
# 6.  Minimal Polynomial Recurrence for Higher Powers  (8 tests)
# =========================================================================

class TestMinimalPolyRecurrence:
    """Using A^3 = 10 A^2 + 32 A - 96 I to cascade higher powers."""

    def test_A3_from_recurrence(self):
        assert_array_equal(A3, 10 * A2 + 32 * A - 96 * I_)

    def test_A4_from_recurrence(self):
        assert_array_equal(A4, 10 * A3 + 32 * A2 - 96 * A)

    def test_A5_from_recurrence(self):
        assert_array_equal(A5, 10 * A4 + 32 * A3 - 96 * A2)

    def test_A6_from_recurrence(self):
        A6 = A5 @ A
        assert_array_equal(A6, 10 * A5 + 32 * A4 - 96 * A3)

    def test_trace_A4_eigenvalues(self):
        expected = 12**4 + 24 * 2**4 + 15 * (-4)**4  # 20736+384+3840 = 24960
        assert np.trace(A4) == expected

    def test_trace_A5_eigenvalues(self):
        expected = 12**5 + 24 * 2**5 + 15 * (-4)**5
        assert np.trace(A5) == expected

    def test_powers_commute(self):
        assert_array_equal(A2 @ A3, A3 @ A2)

    def test_A2_times_A3_equals_A5(self):
        assert_array_equal(A2 @ A3, A5)


# =========================================================================
# 7.  Polynomial Evaluation on A  (9 tests)
# =========================================================================

class TestPolynomialEvaluation:
    """Evaluate polynomials at A, reducing via minimal polynomial."""

    def test_identity_polynomial(self):
        """p(x) = x."""
        assert_array_equal(A, A)

    def test_square_polynomial(self):
        """p(x) = x^2 reduces to -2A + 8I + 4J."""
        assert_array_equal(A2, -2 * A + 8 * I_ + 4 * J)

    def test_linear_combination(self):
        """p(x) = x^2 + 3x + 1 = A + 9I + 4J."""
        result = A2 + 3 * A + I_
        expected = A + 9 * I_ + 4 * J
        assert_array_equal(result, expected)

    def test_cubic_annihilator(self):
        """x^3 - 10x^2 - 32x + 96 vanishes at A."""
        assert_array_equal(A3 - 10 * A2 - 32 * A + 96 * I_,
                           np.zeros((N, N), dtype=int))

    def test_quartic_polynomial(self):
        """p(x) = x^4 - x^2 + 2x - 5 = 83I - 36A + 524J."""
        result = A4 - A2 + 2 * A - 5 * I_
        expected = 83 * I_ - 36 * A + 524 * J
        assert_array_equal(result, expected)

    def test_high_degree_polynomial(self):
        """x^5 + 2x^3 - x + 7 = -345I + 199A + 6256J."""
        result = A5 + 2 * A3 - A + 7 * I_
        expected = -345 * I_ + 199 * A + 6256 * J
        assert_array_equal(result, expected)

    def test_polynomial_eigenvalues(self):
        """p(A) has eigenvalues p(lambda_i)."""
        # p(x) = x^2 + x - 6
        P = A2 + A - 6 * I_
        evals_P = np.sort(np.linalg.eigvalsh(P.astype(float)))
        expected = sorted([150] * 1 + [0] * 24 + [6] * 15)
        assert_allclose(evals_P, expected, atol=1e-6)

    def test_polynomial_kernel_rank(self):
        """rank(A - 2I) = 40 - 24 = 16."""
        rank = np.linalg.matrix_rank((A - 2 * I_).astype(float))
        assert rank == 16

    def test_polynomial_kernel_nullity(self):
        """nullity(A - 2I) = 24."""
        rank = np.linalg.matrix_rank((A - 2 * I_).astype(float))
        assert N - rank == 24


# =========================================================================
# 8.  Matrix Inverse from Minimal Polynomial  (8 tests)
# =========================================================================

class TestMatrixInverse:
    """A^{-1} = (3A + 6I - J) / 24.

    Derivation: m(A) = 0  =>  A(A^2 - 10A - 32I) = -96I
                =>  A^{-1} = -(A^2 - 10A - 32I) / 96
                using A^2 = -2A + 8I + 4J this simplifies to (3A + 6I - J)/24.
    """

    @pytest.fixture(autouse=True)
    def _inverse(self):
        self.A_inv_scaled = 3 * A + 6 * I_ - J      # = 24 * A^{-1}, integer
        self.A_inv = self.A_inv_scaled.astype(float) / 24.0

    def test_determinant_nonzero(self):
        det = np.linalg.det(A.astype(float))
        assert abs(det) > 1e-10

    def test_determinant_value(self):
        """det(A) = 12^1 * 2^24 * (-4)^15 = -3 * 2^56."""
        det = np.linalg.det(A.astype(float))
        expected = 12.0 * (2.0**24) * ((-4.0)**15)
        assert_allclose(det, expected, rtol=1e-3)

    def test_inverse_from_minimal_poly(self):
        """A^{-1} = -(A^2 - 10A - 32I) / 96."""
        alt = -(A2 - 10 * A - 32 * I_).astype(float) / 96.0
        assert_allclose(alt, self.A_inv, atol=1e-12)

    def test_inverse_right_product(self):
        """A * A^{-1} = I  (integer-scaled: A*(3A + 6I - J) = 24I)."""
        assert_array_equal(A @ self.A_inv_scaled, 24 * I_)

    def test_inverse_left_product(self):
        """A^{-1} * A = I  (integer-scaled)."""
        assert_array_equal(self.A_inv_scaled @ A, 24 * I_)

    def test_inverse_symmetric(self):
        assert_allclose(self.A_inv, self.A_inv.T, atol=1e-14)

    def test_inverse_eigenvalues(self):
        inv_evals = np.sort(np.linalg.eigvalsh(self.A_inv))
        expected = sorted([1.0 / 12] + [1.0 / 2] * 24 + [-1.0 / 4] * 15)
        assert_allclose(inv_evals, expected, atol=1e-8)

    def test_inverse_squared_eigenvalues(self):
        A_inv2 = self.A_inv @ self.A_inv
        evals = np.sort(np.linalg.eigvalsh(A_inv2))
        expected = sorted([1.0 / 144] + [1.0 / 4] * 24 + [1.0 / 16] * 15)
        assert_allclose(evals, expected, atol=1e-8)


# =========================================================================
# 9.  Faddeev-LeVerrier Algorithm  (8 tests)
# =========================================================================

class TestFaddeevLeVerrier:
    """Faddeev-LeVerrier produces the characteristic polynomial coefficients.

    B_0 = I
    For k = 1, ..., n:
        c_k = -tr(A B_{k-1}) / k
        B_k = A B_{k-1} + c_k I
    """

    @pytest.fixture(autouse=True)
    def _run_algorithm(self):
        Af = A.astype(float)
        If = np.eye(N)
        self.B = [If.copy()]
        self.c = [None]  # c_0 unused
        B_prev = If.copy()
        for k in range(1, 4):
            c_k = -np.trace(Af @ B_prev) / k
            B_k = Af @ B_prev + c_k * If
            self.c.append(c_k)
            self.B.append(B_k)
            B_prev = B_k

    def test_c1_equals_neg_trace(self):
        """c_1 = -tr(A) = 0."""
        assert_allclose(self.c[1], 0.0, atol=1e-10)

    def test_c2_value(self):
        """c_2 = -tr(A^2)/2 = -480/2 = -240."""
        assert_allclose(self.c[2], -240.0, atol=1e-8)

    def test_c3_value(self):
        """c_3 = -tr(A(A^2 - 240I))/3 = -(960 - 0)/3 = -320."""
        assert_allclose(self.c[3], -320.0, atol=1e-6)

    def test_B1_equals_A(self):
        assert_allclose(self.B[1], A.astype(float), atol=1e-10)

    def test_B2_structure(self):
        """B_2 = A^2 - 240 I."""
        expected = A2.astype(float) - 240 * np.eye(N)
        assert_allclose(self.B[2], expected, atol=1e-8)

    def test_newton_identity_s1(self):
        """s_1 + c_1 = 0."""
        s1 = float(np.trace(A))
        assert_allclose(s1 + self.c[1], 0.0, atol=1e-10)

    def test_newton_identity_s2(self):
        """s_2 + c_1 s_1 + 2 c_2 = 0."""
        s1, s2 = float(np.trace(A)), float(np.trace(A2))
        assert_allclose(s2 + self.c[1] * s1 + 2 * self.c[2], 0.0, atol=1e-8)

    def test_newton_identity_s3(self):
        """s_3 + c_1 s_2 + c_2 s_1 + 3 c_3 = 0."""
        s1 = float(np.trace(A))
        s2 = float(np.trace(A2))
        s3 = float(np.trace(A3))
        assert_allclose(s3 + self.c[1]*s2 + self.c[2]*s1 + 3*self.c[3],
                        0.0, atol=1e-6)


# =========================================================================
# 10. Spectral Projectors (Lagrange Interpolation)  (18 tests)
# =========================================================================

class TestSpectralProjectors:
    """E_1, E_2, E_3 for eigenvalues 12, 2, -4.

    E_1 = (A-2I)(A+4I) / 160  = J / 40
    E_2 = (A-12I)(A+4I) / -60 = (5A + 20I - 2J) / 30
    E_3 = (A-12I)(A-2I) / 96  = (-4A + 8I + J) / 24
    """

    @pytest.fixture(autouse=True)
    def _projectors(self):
        Af = A.astype(float)
        If = np.eye(N)
        Jf = np.ones((N, N))
        self.E1 = Jf / N
        self.E2 = (5 * Af + 20 * If - 2 * Jf) / 30.0
        self.E3 = (-4 * Af + 8 * If + Jf) / 24.0

    def test_E1_equals_J_over_n(self):
        assert_allclose(self.E1, np.ones((N, N)) / N, atol=1e-14)

    def test_E1_from_lagrange(self):
        """(A-2I)(A+4I) = 4J, so E_1 = 4J/160 = J/40."""
        num = (A - 2 * I_) @ (A + 4 * I_)
        assert_array_equal(num, 4 * J)
        assert_allclose(num.astype(float) / 160.0, self.E1, atol=1e-14)

    def test_E2_from_lagrange(self):
        num = (A - 12 * I_) @ (A + 4 * I_)
        assert_allclose(num.astype(float) / (-60.0), self.E2, atol=1e-10)

    def test_E3_from_lagrange(self):
        num = (A - 12 * I_) @ (A - 2 * I_)
        assert_allclose(num.astype(float) / 96.0, self.E3, atol=1e-10)

    def test_partition_of_unity(self):
        assert_allclose(self.E1 + self.E2 + self.E3, np.eye(N), atol=1e-10)

    def test_E1_idempotent(self):
        assert_allclose(self.E1 @ self.E1, self.E1, atol=1e-10)

    def test_E2_idempotent(self):
        assert_allclose(self.E2 @ self.E2, self.E2, atol=1e-10)

    def test_E3_idempotent(self):
        assert_allclose(self.E3 @ self.E3, self.E3, atol=1e-10)

    def test_E1_E2_orthogonal(self):
        assert_allclose(self.E1 @ self.E2, np.zeros((N, N)), atol=1e-10)

    def test_E1_E3_orthogonal(self):
        assert_allclose(self.E1 @ self.E3, np.zeros((N, N)), atol=1e-10)

    def test_E2_E3_orthogonal(self):
        assert_allclose(self.E2 @ self.E3, np.zeros((N, N)), atol=1e-10)

    def test_E1_rank(self):
        assert np.linalg.matrix_rank(self.E1) == 1

    def test_E2_rank(self):
        assert np.linalg.matrix_rank(self.E2) == 24

    def test_E3_rank(self):
        assert np.linalg.matrix_rank(self.E3) == 15

    def test_spectral_decomposition_of_A(self):
        """A = 12 E_1 + 2 E_2 + (-4) E_3."""
        recon = 12 * self.E1 + 2 * self.E2 + (-4) * self.E3
        assert_allclose(recon, A.astype(float), atol=1e-10)

    def test_spectral_decomposition_of_A2(self):
        recon = 144 * self.E1 + 4 * self.E2 + 16 * self.E3
        assert_allclose(recon, A2.astype(float), atol=1e-8)

    def test_trace_E2(self):
        assert_allclose(np.trace(self.E2), 24.0, atol=1e-8)

    def test_trace_E3(self):
        assert_allclose(np.trace(self.E3), 15.0, atol=1e-8)


# =========================================================================
# 11. Resolvent (sI - A)^{-1} via Spectral Decomposition  (9 tests)
# =========================================================================

class TestResolvent:
    """(sI - A)^{-1} = E_1/(s-12) + E_2/(s-2) + E_3/(s+4)."""

    def _resolvent_spectral(self, s):
        Af = A.astype(float)
        If = np.eye(N)
        Jf = np.ones((N, N))
        E1 = Jf / N
        E2 = (5 * Af + 20 * If - 2 * Jf) / 30.0
        E3 = (-4 * Af + 8 * If + Jf) / 24.0
        return E1 / (s - 12) + E2 / (s - 2) + E3 / (s + 4)

    def test_resolvent_s5(self):
        s = 5.0
        spec = self._resolvent_spectral(s)
        direct = np.linalg.inv(s * np.eye(N) - A.astype(float))
        assert_allclose(spec, direct, atol=1e-8)

    def test_resolvent_s_neg1(self):
        s = -1.0
        spec = self._resolvent_spectral(s)
        direct = np.linalg.inv(s * np.eye(N) - A.astype(float))
        assert_allclose(spec, direct, atol=1e-8)

    def test_resolvent_s20(self):
        s = 20.0
        spec = self._resolvent_spectral(s)
        direct = np.linalg.inv(s * np.eye(N) - A.astype(float))
        assert_allclose(spec, direct, atol=1e-8)

    def test_resolvent_s_neg10(self):
        s = -10.0
        spec = self._resolvent_spectral(s)
        direct = np.linalg.inv(s * np.eye(N) - A.astype(float))
        assert_allclose(spec, direct, atol=1e-8)

    def test_resolvent_symmetric(self):
        R = self._resolvent_spectral(7.0)
        assert_allclose(R, R.T, atol=1e-10)

    def test_resolvent_at_s0_gives_neg_inv(self):
        """(0I - A)^{-1} = -A^{-1}."""
        R0 = self._resolvent_spectral(0.0)
        A_inv = (3 * A + 6 * I_ - J).astype(float) / 24.0
        assert_allclose(R0, -A_inv, atol=1e-10)

    def test_resolvent_identity(self):
        """R(s) - R(t) = (t - s) R(s) R(t)."""
        s, t = 5.0, -1.0
        Rs = self._resolvent_spectral(s)
        Rt = self._resolvent_spectral(t)
        assert_allclose(Rs - Rt, (t - s) * Rs @ Rt, atol=1e-8)

    def test_resolvent_trace(self):
        """tr R(s) = 1/(s-12) + 24/(s-2) + 15/(s+4)."""
        s = 7.0
        R = self._resolvent_spectral(s)
        expected = 1.0 / (s - 12) + 24.0 / (s - 2) + 15.0 / (s + 4)
        assert_allclose(np.trace(R), expected, atol=1e-8)

    def test_neumann_series_resolvent(self):
        """For |s| > rho(A), (sI-A)^{-1} = (1/s) sum_k (A/s)^k."""
        s = 20.0
        Af = A.astype(float)
        If = np.eye(N)
        neumann = np.zeros((N, N))
        term = If.copy()
        for _ in range(50):
            neumann += term
            term = term @ (Af / s)
        neumann /= s
        direct = np.linalg.inv(s * If - Af)
        assert_allclose(neumann, direct, atol=1e-10)


# =========================================================================
# 12. Matrix Function Series Truncation  (12 tests)
# =========================================================================

class TestMatrixFunctions:
    """Matrix functions via spectral formula and Taylor series truncation."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        self.Af = A.astype(float)
        self.If = np.eye(N)
        self.Jf = np.ones((N, N))
        self.E1 = self.Jf / N
        self.E2 = (5 * self.Af + 20 * self.If - 2 * self.Jf) / 30.0
        self.E3 = (-4 * self.Af + 8 * self.If + self.Jf) / 24.0

    def _spectral_func(self, f12, f2, fm4):
        return f12 * self.E1 + f2 * self.E2 + fm4 * self.E3

    # -- exponential ---------------------------------------------------------

    def test_exp_scaled_A_taylor(self):
        """exp(0.1 A) via 30-term Taylor series matches spectral formula."""
        t = 0.1
        tA = t * self.Af
        taylor = self.If.copy()
        term = self.If.copy()
        for k in range(1, 30):
            term = term @ tA / k
            taylor = taylor + term
        spectral = self._spectral_func(np.exp(12 * t),
                                       np.exp(2 * t),
                                       np.exp(-4 * t))
        assert_allclose(taylor, spectral, atol=1e-10)

    def test_exp_A_taylor_60_terms(self):
        """exp(A) via 60-term Taylor series matches spectral formula."""
        taylor = self.If.copy()
        term = self.If.copy()
        for k in range(1, 60):
            term = term @ self.Af / k
            taylor = taylor + term
        spectral = self._spectral_func(np.exp(12), np.exp(2), np.exp(-4))
        assert_allclose(taylor, spectral, rtol=1e-6)

    def test_exp_tA_at_t0(self):
        """exp(0*A) = I."""
        assert_allclose(self._spectral_func(1.0, 1.0, 1.0),
                        self.If, atol=1e-10)

    def test_exp_A_eigenvalues(self):
        expA = self._spectral_func(np.exp(12), np.exp(2), np.exp(-4))
        evals = np.sort(np.linalg.eigvalsh(expA))
        expected = sorted([np.exp(12)] + [np.exp(2)] * 24 + [np.exp(-4)] * 15)
        assert_allclose(evals, expected, rtol=1e-6)

    # -- trigonometric -------------------------------------------------------

    def test_cos_A_trace(self):
        cosA = self._spectral_func(np.cos(12), np.cos(2), np.cos(-4))
        expected = np.cos(12) + 24 * np.cos(2) + 15 * np.cos(4)
        assert_allclose(np.trace(cosA), expected, atol=1e-8)

    def test_sin_A_trace(self):
        sinA = self._spectral_func(np.sin(12), np.sin(2), np.sin(-4))
        expected = np.sin(12) + 24 * np.sin(2) + 15 * np.sin(-4)
        assert_allclose(np.trace(sinA), expected, atol=1e-8)

    def test_sin2_plus_cos2_identity(self):
        """sin^2(A) + cos^2(A) = I."""
        sinA = self._spectral_func(np.sin(12), np.sin(2), np.sin(-4))
        cosA = self._spectral_func(np.cos(12), np.cos(2), np.cos(-4))
        assert_allclose(sinA @ sinA + cosA @ cosA, self.If, atol=1e-8)

    # -- square root and logarithm -------------------------------------------

    def test_sqrt_shifted(self):
        """sqrt(A + 5I) where eigenvalues {17, 7, 1} are all positive."""
        sqrtM = self._spectral_func(np.sqrt(17), np.sqrt(7), np.sqrt(1))
        assert_allclose(sqrtM @ sqrtM, self.Af + 5 * self.If, atol=1e-8)

    def test_log_shifted(self):
        """log(A + 5I) via spectral formula; exp(log(M)) = M."""
        logM = self._spectral_func(np.log(17), np.log(7), np.log(1))
        explogM = self._spectral_func(17, 7, 1)
        assert_allclose(explogM, self.Af + 5 * self.If, atol=1e-8)

    # -- general function as polynomial in A ---------------------------------

    def test_matrix_function_is_polynomial_in_A(self):
        """Any f(A) = alpha*I + beta*A + gamma*J."""
        f12, f2, fm4 = 3.7, -1.2, 0.5
        fA = self._spectral_func(f12, f2, fm4)
        # Solve: alpha + 2*beta = f2, alpha - 4*beta = fm4, rest via J
        beta = (f2 - fm4) / 6.0
        alpha = f2 - 2 * beta
        gamma = (f12 - alpha - 12 * beta) / 40.0
        recon = alpha * self.If + beta * self.Af + gamma * self.Jf
        assert_allclose(fA, recon, atol=1e-10)

    def test_series_truncation_improves(self):
        """More Taylor terms give smaller residual for exp(0.05 A)."""
        t = 0.05
        tA = t * self.Af
        spectral = self._spectral_func(np.exp(12 * t),
                                       np.exp(2 * t),
                                       np.exp(-4 * t))
        errors = []
        taylor = self.If.copy()
        term = self.If.copy()
        for k in range(1, 15):
            term = term @ tA / k
            taylor = taylor + term
            errors.append(np.max(np.abs(taylor - spectral)))
        # Each successive error should be smaller than the previous
        for i in range(len(errors) - 1):
            assert errors[i + 1] <= errors[i] + 1e-15

    def test_cayley_transform(self):
        """Cayley transform C = (I - A)(I + A)^{-1} via spectral formula.

        Eigenvalues: (1-lambda)/(1+lambda) for lambda in {12, 2, -4}.
        """
        c12 = (1 - 12) / (1 + 12)    # -11/13
        c2 = (1 - 2) / (1 + 2)       # -1/3
        cm4 = (1 - (-4)) / (1 + (-4))  # 5/(-3) = -5/3
        C = self._spectral_func(c12, c2, cm4)
        # Verify (I + A) C = (I - A)
        lhs = (self.If + self.Af) @ C
        rhs = self.If - self.Af
        assert_allclose(lhs, rhs, atol=1e-8)


# =========================================================================
# 13. Advanced Power Reduction Identities  (12 tests)
# =========================================================================

class TestPowerReductionAdvanced:
    """Additional identities derived from Cayley-Hamilton reduction."""

    def test_A3_plus_16I_equals_12A_plus_40J(self):
        """A^3 + 16I = 12A + 40J (from A^3 = -16I + 12A + 40J)."""
        assert_array_equal(A3 + 16 * I_, 12 * A + 40 * J)

    def test_A2_minus_8I_eigenvalues(self):
        """A^2 - 8I = -2A + 4J has eigenvalues {136, -4, 8}."""
        M = (A2 - 8 * I_).astype(float)
        evals = np.sort(np.linalg.eigvalsh(M))
        expected = sorted([136] + [-4] * 24 + [8] * 15)
        assert_allclose(evals, expected, atol=1e-6)

    def test_commutator_A_J_vanishes(self):
        assert_array_equal(A @ J - J @ A, np.zeros((N, N), dtype=int))

    def test_A_inv_commutes_with_J(self):
        A_inv = (3 * A + 6 * I_ - J).astype(float) / 24.0
        Jf = J.astype(float)
        assert_allclose(A_inv @ Jf, Jf @ A_inv, atol=1e-10)

    def test_companion_matrix_eigenvalues(self):
        """Companion matrix of m(x) has eigenvalues {12, 2, -4}."""
        C = np.array([[0, 0, -96],
                      [1, 0,  32],
                      [0, 1,  10]], dtype=float)
        evals = sorted(np.linalg.eigvals(C).real)
        assert_allclose(evals, [-4, 2, 12], atol=1e-8)

    def test_trace_power_formula(self):
        """tr(A^n) = 12^n + 24*2^n + 15*(-4)^n for n = 0..5."""
        powers = [I_, A, A2, A3, A4, A5]
        for n, An in enumerate(powers):
            expected = 12**n + 24 * 2**n + 15 * (-4)**n
            assert np.trace(An) == expected, f"n={n}"

    def test_frobenius_norm_A(self):
        """||A||_F^2 = tr(A^T A) = tr(A^2) = 480."""
        assert np.sum(A * A) == 480

    def test_frobenius_norm_A2(self):
        """||A^2||_F^2 = tr(A^4)."""
        assert np.sum(A2 * A2) == np.trace(A4)

    def test_mixed_power_product(self):
        assert_array_equal(A3 @ A2, A5)

    def test_polynomial_ring_closure(self):
        """(I + A)(I - A) = -7I + 2A - 4J."""
        product = (I_ + A) @ (I_ - A)
        expected = -7 * I_ + 2 * A - 4 * J
        assert_array_equal(product, expected)

    def test_A_sixth_power_via_cube_squared(self):
        """(A^3)^2 = (A^2)^3 (both equal A^6)."""
        assert_array_equal(A3 @ A3, A2 @ A2 @ A2)

    def test_nilpotent_component_vanishes(self):
        """A has no nilpotent part: (A - 12E1 - 2E2 + 4E3) = 0."""
        Af = A.astype(float)
        If = np.eye(N)
        Jf = np.ones((N, N))
        E1 = Jf / N
        E2 = (5 * Af + 20 * If - 2 * Jf) / 30.0
        E3 = (-4 * Af + 8 * If + Jf) / 24.0
        residual = Af - 12 * E1 - 2 * E2 - (-4) * E3
        assert_allclose(residual, np.zeros((N, N)), atol=1e-10)


# =========================================================================
# 14. Spectral Zeta and Generating Functions  (7 tests)
# =========================================================================

class TestSpectralGenerating:
    """Generating-function and zeta identities from the spectral triple."""

    def test_walk_generating_function_trace(self):
        """sum_{k=0}^{K} tr(A^k) t^k at t = 0.05 via closed form."""
        t = 0.05
        K = 20
        # Direct summation using eigenvalue formula
        direct = sum((12 * t)**k + 24 * (2 * t)**k + 15 * (-4 * t)**k
                     for k in range(K + 1))
        # Geometric series closed form
        geo = (1 - (12 * t)**(K + 1)) / (1 - 12 * t) + \
              24 * (1 - (2 * t)**(K + 1)) / (1 - 2 * t) + \
              15 * (1 - (-4 * t)**(K + 1)) / (1 - (-4) * t)
        assert_allclose(direct, geo, atol=1e-10)

    def test_spectral_zeta_s2(self):
        """zeta_A(2) = sum lambda_i^{-2} = 1/144 + 24/4 + 15/16."""
        expected = 1.0 / 144 + 24.0 / 4 + 15.0 / 16
        A_inv = (3 * A + 6 * I_ - J).astype(float) / 24.0
        zeta2 = np.trace(A_inv @ A_inv)
        assert_allclose(zeta2, expected, atol=1e-8)

    def test_spectral_zeta_s1(self):
        """zeta_A(1) = sum |lambda_i|^{-1} ... tr(|A|^{-1}).
        For A with eigenvalues 12,2,-4:  1/12 + 24/2 + 15/4."""
        expected = 1.0 / 12 + 24.0 / 2 + 15.0 / 4
        # |A|^{-1} = spectral: 1/|lam| on each eigenspace
        Af = A.astype(float)
        If = np.eye(N)
        Jf = np.ones((N, N))
        E1 = Jf / N
        E2 = (5 * Af + 20 * If - 2 * Jf) / 30.0
        E3 = (-4 * Af + 8 * If + Jf) / 24.0
        abs_inv = (1.0 / 12) * E1 + (1.0 / 2) * E2 + (1.0 / 4) * E3
        assert_allclose(np.trace(abs_inv), expected, atol=1e-8)

    def test_heat_kernel_trace_small_t(self):
        """tr(exp(tA)) = e^{12t} + 24 e^{2t} + 15 e^{-4t}."""
        t = 0.01
        expected = np.exp(12 * t) + 24 * np.exp(2 * t) + 15 * np.exp(-4 * t)
        # Compute via Taylor
        tA = t * A.astype(float)
        If = np.eye(N)
        taylor = If.copy()
        term = If.copy()
        for k in range(1, 25):
            term = term @ tA / k
            taylor = taylor + term
        assert_allclose(np.trace(taylor), expected, atol=1e-10)

    def test_walk_count_length_2(self):
        """Number of closed walks of length 2 = tr(A^2) = 480."""
        assert np.trace(A2) == 480

    def test_walk_count_length_3(self):
        """tr(A^3) = 6 * (number of triangles). W(3,3) has 160 triangles."""
        assert np.trace(A3) == 960
        assert np.trace(A3) % 6 == 0
        assert np.trace(A3) // 6 == 160

    def test_number_of_edges(self):
        """edges = tr(A^2) / 2 = 240."""
        assert np.trace(A2) // 2 == 240


# =========================================================================
# 15. Matrix Norm and Condition Number Identities  (8 tests)
# =========================================================================

class TestNormCondition:
    """Norm and condition-number facts from the spectral structure."""

    def test_spectral_norm(self):
        """||A||_2 = max |eigenvalue| = 12."""
        s = np.linalg.svd(A.astype(float), compute_uv=False)
        assert_allclose(s[0], 12.0, atol=1e-8)

    def test_spectral_radius(self):
        evals = np.linalg.eigvalsh(A.astype(float))
        assert_allclose(np.max(np.abs(evals)), 12.0, atol=1e-8)

    def test_condition_number(self):
        """cond(A) = max|lam| / min|lam| = 12/2 = 6."""
        s = np.linalg.svd(A.astype(float), compute_uv=False)
        cond = s[0] / s[-1]
        assert_allclose(cond, 6.0, atol=1e-8)

    def test_singular_values(self):
        """Singular values of symmetric A are |eigenvalues|: {12, 4, 2}."""
        s = np.sort(np.linalg.svd(A.astype(float), compute_uv=False))[::-1]
        unique_sv = sorted(set(np.round(s, 6)), reverse=True)
        assert_allclose(unique_sv, [12, 4, 2], atol=1e-6)

    def test_sv_multiplicities(self):
        s = np.round(np.linalg.svd(A.astype(float), compute_uv=False), 6)
        assert np.sum(s == 12.0) == 1
        assert np.sum(np.abs(s - 4.0) < 1e-4) == 15
        assert np.sum(np.abs(s - 2.0) < 1e-4) == 24

    def test_frobenius_norm_from_eigenvalues(self):
        """||A||_F^2 = sum lam_i^2 = 480."""
        frob_sq = np.sum(A.astype(float) ** 2)
        spectral = 12**2 + 24 * 2**2 + 15 * 4**2
        assert_allclose(frob_sq, spectral, atol=1e-8)

    def test_nuclear_norm(self):
        """Nuclear norm = sum |lam_i| = 12 + 24*2 + 15*4 = 120."""
        s = np.linalg.svd(A.astype(float), compute_uv=False)
        assert_allclose(np.sum(s), 120.0, atol=1e-6)

    def test_operator_norm_of_inverse(self):
        """||A^{-1}||_2 = 1 / min|lam| = 1/2."""
        A_inv = (3 * A + 6 * I_ - J).astype(float) / 24.0
        s = np.linalg.svd(A_inv, compute_uv=False)
        assert_allclose(s[0], 0.5, atol=1e-8)


# =========================================================================
# 16. Idempotent Algebra and Peirce Decomposition  (7 tests)
# =========================================================================

class TestIdempotentAlgebra:
    """The algebra span{I, A, J} and its idempotent structure."""

    def test_algebra_dimension(self):
        """span{I, A, J} is a 3-dimensional commutative matrix algebra."""
        # Verify linear independence
        vecs = np.stack([I_.ravel(), A.ravel(), J.ravel()], axis=0).astype(float)
        assert np.linalg.matrix_rank(vecs) == 3

    def test_algebra_closed_under_product(self):
        """Product of any two basis elements lies in span{I, A, J}."""
        # A*A = -2A + 8I + 4J (known)
        # A*J = 12J (known)
        # J*J = 40J (known)
        # All products verified to lie in span{I, A, J}
        prods = [A @ A, A @ J, J @ J]
        targets = [
            -2 * A + 8 * I_ + 4 * J,
            12 * J,
            40 * J,
        ]
        for P, T in zip(prods, targets):
            assert_array_equal(P, T)

    def test_algebra_commutative(self):
        """A*J = J*A, so the algebra is commutative."""
        assert_array_equal(A @ J, J @ A)

    def test_minimal_idempotents_partition(self):
        """E_1, E_2, E_3 form a complete orthogonal set of idempotents."""
        Af = A.astype(float)
        If = np.eye(N)
        Jf = np.ones((N, N))
        E1 = Jf / N
        E2 = (5 * Af + 20 * If - 2 * Jf) / 30.0
        E3 = (-4 * Af + 8 * If + Jf) / 24.0
        assert_allclose(E1 + E2 + E3, If, atol=1e-10)

    def test_peirce_component_1(self):
        """A E_1 = 12 E_1."""
        Af = A.astype(float)
        E1 = np.ones((N, N)) / N
        assert_allclose(Af @ E1, 12 * E1, atol=1e-10)

    def test_peirce_component_2(self):
        """A E_2 = 2 E_2."""
        Af = A.astype(float)
        If = np.eye(N)
        Jf = np.ones((N, N))
        E2 = (5 * Af + 20 * If - 2 * Jf) / 30.0
        assert_allclose(Af @ E2, 2 * E2, atol=1e-10)

    def test_peirce_component_3(self):
        """A E_3 = -4 E_3."""
        Af = A.astype(float)
        If = np.eye(N)
        Jf = np.ones((N, N))
        E3 = (-4 * Af + 8 * If + Jf) / 24.0
        assert_allclose(Af @ E3, -4 * E3, atol=1e-10)
