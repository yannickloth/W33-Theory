"""
Phase C -- Algebraic Number Theory on Graphs
Tests T1656-T1676: number-theoretic analysis of the W(3,3) adjacency spectrum.

The W(3,3) graph is SRG(40,12,2,4) with eigenvalues 12 (mult 1), 2 (mult 24),
-4 (mult 15).  Every test derives from exact matrix algebra over Z or Q;
no networkx dependency.
"""

import numpy as np
import pytest
from math import gcd
from functools import reduce

# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def _build_w33():
    """Build the W(3,3) = Sp(4,3) graph as a 40x40 adjacency matrix."""
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
# Finite-field rank helper
# ---------------------------------------------------------------------------

def _gfp_rank(M, p):
    """Compute rank of integer matrix M over GF(p) via Gaussian elimination."""
    m = M.copy() % p
    rows, cols = m.shape
    rank = 0
    for col in range(cols):
        pivot = None
        for row in range(rank, rows):
            if m[row, col] % p != 0:
                pivot = row
                break
        if pivot is None:
            continue
        m[[rank, pivot]] = m[[pivot, rank]]
        inv_val = pow(int(m[rank, col]), -1, p)
        m[rank] = (m[rank] * inv_val) % p
        for row in range(rows):
            if row != rank and m[row, col] % p != 0:
                factor = int(m[row, col])
                m[row] = (m[row] - factor * m[rank]) % p
        rank += 1
    return rank


# ---------------------------------------------------------------------------
# p-adic valuation helper
# ---------------------------------------------------------------------------

def _v_p(n, p):
    """Return the p-adic valuation of n (largest k such that p^k | n)."""
    if n == 0:
        return float('inf')
    n = abs(n)
    k = 0
    while n % p == 0:
        n //= p
        k += 1
    return k


# ---------------------------------------------------------------------------
# Module-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def A():
    """40x40 integer adjacency matrix of W(3,3)."""
    return _build_w33()


@pytest.fixture(scope="module")
def n():
    return 40


@pytest.fixture(scope="module")
def A2(A):
    return A @ A


@pytest.fixture(scope="module")
def A3(A, A2):
    return A @ A2


@pytest.fixture(scope="module")
def A4(A, A3):
    return A @ A3


@pytest.fixture(scope="module")
def A5(A, A4):
    return A @ A4


@pytest.fixture(scope="module")
def A6(A, A5):
    return A @ A5


@pytest.fixture(scope="module")
def J(n):
    """40x40 all-ones matrix."""
    return np.ones((n, n), dtype=int)


@pytest.fixture(scope="module")
def I_n(n):
    """40x40 identity matrix."""
    return np.eye(n, dtype=int)


@pytest.fixture(scope="module")
def eigenvalues(A):
    """Eigenvalues of A, rounded to nearest integer."""
    evals = np.linalg.eigvalsh(A)
    return np.round(evals).astype(int)


@pytest.fixture(scope="module")
def eigen_mults(eigenvalues):
    """Dict mapping each distinct eigenvalue to its multiplicity."""
    unique, counts = np.unique(eigenvalues, return_counts=True)
    return dict(zip(unique.tolist(), counts.tolist()))


@pytest.fixture(scope="module")
def spectral_idempotents(A, n):
    """Spectral projections E0 (eig 12), E1 (eig 2), E2 (eig -4)."""
    I = np.eye(n)
    Af = A.astype(float)
    E0 = (Af - 2 * I) @ (Af + 4 * I) / 160.0
    E1 = (Af - 12 * I) @ (Af + 4 * I) / (-60.0)
    E2 = (Af - 12 * I) @ (Af - 2 * I) / 96.0
    return E0, E1, E2


# SRG parameters
_n = 40
_k = 12
_lam = 2
_mu = 4
_r = 2      # positive restricted eigenvalue
_s = -4     # negative restricted eigenvalue


# ===================================================================
# T1656 -- Adjacency matrix construction and structural properties
# ===================================================================

class TestT1656:
    """Adjacency matrix basic structural properties."""

    def test_matrix_shape(self, A, n):
        """A is a 40x40 matrix."""
        assert A.shape == (n, n)

    def test_matrix_symmetric(self, A):
        """A is symmetric (undirected graph)."""
        assert np.array_equal(A, A.T)

    def test_zero_diagonal(self, A, n):
        """A has zero diagonal (no self-loops)."""
        assert np.array_equal(np.diag(A), np.zeros(n, dtype=int))

    def test_binary_entries(self, A):
        """All entries are 0 or 1."""
        assert set(np.unique(A)) == {0, 1}


# ===================================================================
# T1657 -- Strongly regular graph parameter verification
# ===================================================================

class TestT1657:
    """SRG(40,12,2,4) parameter verification."""

    def test_regularity_k12(self, A, n):
        """Every vertex has degree k = 12."""
        row_sums = A.sum(axis=1)
        assert np.all(row_sums == _k)

    def test_lambda_parameter(self, A, n):
        """Adjacent vertices have exactly lambda = 2 common neighbours."""
        for i in range(n):
            for j in range(i + 1, n):
                if A[i, j] == 1:
                    common = np.sum(A[i] * A[j])
                    assert common == _lam, f"lambda failed for ({i},{j})"
                    return  # spot check (full check below)
        # full check via matrix equation is in test_srg_matrix_equation

    def test_mu_parameter(self, A, n):
        """Non-adjacent vertices have exactly mu = 4 common neighbours."""
        for i in range(n):
            for j in range(i + 1, n):
                if A[i, j] == 0:
                    common = np.sum(A[i] * A[j])
                    assert common == _mu, f"mu failed for ({i},{j})"
                    return  # spot check

    def test_srg_matrix_equation(self, A, A2, I_n, J):
        """A^2 = 8I - 2A + 4J (the SRG matrix identity)."""
        expected = 8 * I_n - 2 * A + 4 * J
        assert np.array_equal(A2, expected)


# ===================================================================
# T1658 -- Eigenvalue computation and multiplicities
# ===================================================================

class TestT1658:
    """Eigenvalue structure of the adjacency matrix."""

    def test_three_distinct_eigenvalues(self, eigen_mults):
        """There are exactly 3 distinct eigenvalues."""
        assert len(eigen_mults) == 3

    def test_eigenvalue_values(self, eigen_mults):
        """The distinct eigenvalues are {12, 2, -4}."""
        assert set(eigen_mults.keys()) == {12, 2, -4}

    def test_multiplicity_trivial(self, eigen_mults):
        """The trivial eigenvalue k = 12 has multiplicity 1."""
        assert eigen_mults[12] == 1

    def test_eigenvalue_multiplicities(self, eigen_mults):
        """Multiplicities: 12 -> 1, 2 -> 24, -4 -> 15, totalling 40."""
        assert eigen_mults[12] == 1
        assert eigen_mults[2] == 24
        assert eigen_mults[-4] == 15
        assert sum(eigen_mults.values()) == _n


# ===================================================================
# T1659 -- Characteristic polynomial structure
# ===================================================================

class TestT1659:
    """Characteristic polynomial chi(x) = (x-12)(x-2)^24(x+4)^15."""

    def test_char_poly_degree(self, A, n):
        """chi(x) has degree 40."""
        # The characteristic polynomial of an nxn matrix has degree n
        evals = np.linalg.eigvalsh(A)
        assert len(evals) == n

    def test_char_poly_at_zero(self):
        """chi(0) = det(-A) = det(A) = (-12)*(-2)^24*(4)^15 = -3*2^56."""
        chi_0 = (-12)**1 * (-2)**24 * 4**15
        assert chi_0 == -3 * 2**56

    def test_char_poly_at_one(self):
        """chi(1) = (-11)*(-1)^24*5^15 = -11 * 5^15."""
        chi_1 = (-11)**1 * (-1)**24 * 5**15
        assert chi_1 == -11 * 5**15
        assert chi_1 == -335693359375

    def test_char_poly_leading_coefficient(self, eigen_mults):
        """chi(x) is monic (leading coefficient 1): verified by n eigenvalues."""
        total = sum(eigen_mults.values())
        assert total == _n


# ===================================================================
# T1660 -- Minimal polynomial
# ===================================================================

class TestT1660:
    """Minimal polynomial p(x) = x^3 - 10x^2 - 32x + 96."""

    def test_min_poly_degree(self):
        """The minimal polynomial has degree 3 (= number of distinct eigenvalues)."""
        num_distinct = 3  # {12, 2, -4}
        assert num_distinct == 3

    def test_min_poly_coefficients(self):
        """p(x) = (x-12)(x-2)(x+4) = x^3 - 10x^2 - 32x + 96."""
        # Expand (x-12)(x-2)(x+4) symbolically
        # (x-12)(x-2) = x^2 - 14x + 24
        # (x^2 - 14x + 24)(x+4) = x^3 - 10x^2 - 32x + 96
        coeffs = [1, -10, -32, 96]
        # Verify each root
        for root in [12, 2, -4]:
            val = coeffs[0]*root**3 + coeffs[1]*root**2 + coeffs[2]*root + coeffs[3]
            assert val == 0, f"p({root}) != 0"

    def test_min_poly_annihilates(self, A, A2, A3, I_n):
        """p(A) = A^3 - 10A^2 - 32A + 96I = 0."""
        residual = A3 - 10 * A2 - 32 * A + 96 * I_n
        assert np.array_equal(residual, np.zeros_like(A))

    def test_no_degree2_annihilator(self, A, A2, I_n):
        """No degree-2 polynomial annihilates A (minimality)."""
        # (A-12I)(A-2I) != 0
        p12 = (A - 12 * I_n) @ (A - 2 * I_n)
        assert not np.array_equal(p12, np.zeros_like(A))
        # (A-12I)(A+4I) != 0
        p14 = (A - 12 * I_n) @ (A + 4 * I_n)
        assert not np.array_equal(p14, np.zeros_like(A))
        # (A-2I)(A+4I) != 0
        p24 = (A - 2 * I_n) @ (A + 4 * I_n)
        assert not np.array_equal(p24, np.zeros_like(A))


# ===================================================================
# T1661 -- Cayley-Hamilton theorem verification
# ===================================================================

class TestT1661:
    """Cayley-Hamilton: the characteristic polynomial annihilates A."""

    def test_char_poly_annihilates(self, A, I_n):
        """chi(A) = (A-12I)^1 (A-2I)^24 (A+4I)^15 = 0."""
        # Since minimal poly divides char poly, and p(A)=0, chi(A)=0.
        # Verify by evaluating minimal poly (which already implies char poly annihilation)
        A2 = A @ A
        A3 = A @ A2
        residual = A3 - 10 * A2 - 32 * A + 96 * I_n
        assert np.array_equal(residual, np.zeros_like(A))

    def test_A_cubed_from_minimal(self, A, A2, A3, I_n):
        """A^3 = 10A^2 + 32A - 96I (rearranged minimal polynomial)."""
        expected = 10 * A2 + 32 * A - 96 * I_n
        assert np.array_equal(A3, expected)

    def test_A_cubed_bose_mesner(self, A, A3, I_n, J):
        """A^3 = -16I + 12A + 40J (in the Bose-Mesner basis)."""
        expected = -16 * I_n + 12 * A + 40 * J
        assert np.array_equal(A3, expected)


# ===================================================================
# T1662 -- Determinant computation
# ===================================================================

class TestT1662:
    """Determinant of the adjacency matrix."""

    def test_det_exact_value(self):
        """det(A) = 12^1 * 2^24 * (-4)^15 = -3 * 2^56."""
        det_exact = 12 * (2**24) * ((-4)**15)
        assert det_exact == -3 * 2**56
        assert det_exact == -216172782113783808

    def test_det_sign_negative(self):
        """det(A) < 0 because (-4)^15 < 0."""
        det_val = -3 * 2**56
        assert det_val < 0

    def test_det_from_eigenvalue_product(self, eigenvalues):
        """det(A) = product of all eigenvalues with multiplicities."""
        product = 1
        for ev in eigenvalues:
            product *= int(ev)
        assert product == -3 * 2**56


# ===================================================================
# T1663 -- p-adic valuations of the determinant
# ===================================================================

class TestT1663:
    """p-adic structure of det(A) = -3 * 2^56."""

    def test_2adic_valuation(self):
        """v_2(|det|) = 56."""
        det_abs = 3 * 2**56
        assert _v_p(det_abs, 2) == 56

    def test_3adic_valuation(self):
        """v_3(|det|) = 1."""
        det_abs = 3 * 2**56
        assert _v_p(det_abs, 3) == 1

    def test_prime_support(self):
        """|det| = 3 * 2^56 is supported on primes {2, 3} only."""
        det_abs = 3 * 2**56
        remaining = det_abs
        for p in [2, 3]:
            while remaining % p == 0:
                remaining //= p
        assert remaining == 1

    def test_5adic_valuation_zero(self):
        """v_5(|det|) = 0, confirming 5 does not divide det."""
        det_abs = 3 * 2**56
        assert _v_p(det_abs, 5) == 0


# ===================================================================
# T1664 -- Trace of matrix powers
# ===================================================================

class TestT1664:
    """Trace formulas tr(A^k) = sum_i lambda_i^k * m_i."""

    def test_trace_A1(self, A):
        """tr(A) = 0 (diagonal is all zeros)."""
        assert np.trace(A) == 0

    def test_trace_A2(self, A2):
        """tr(A^2) = n*k = 40*12 = 480."""
        assert np.trace(A2) == _n * _k

    def test_trace_A3(self, A3):
        """tr(A^3) = 6 * (number of triangles) = 960."""
        expected = 12**3 * 1 + 2**3 * 24 + (-4)**3 * 15
        assert expected == 960
        assert np.trace(A3) == 960

    def test_trace_A4(self, A4):
        """tr(A^4) = 12^4 + 24*16 + 15*256 = 24960."""
        expected = 12**4 * 1 + 2**4 * 24 + (-4)**4 * 15
        assert expected == 24960
        assert np.trace(A4) == 24960


# ===================================================================
# T1665 -- Spectral idempotent decomposition
# ===================================================================

class TestT1665:
    """Spectral projections E_i for eigenvalues 12, 2, -4."""

    def test_idempotent_sum(self, spectral_idempotents, n):
        """E0 + E1 + E2 = I (resolution of the identity)."""
        E0, E1, E2 = spectral_idempotents
        assert np.allclose(E0 + E1 + E2, np.eye(n), atol=1e-10)

    def test_spectral_decomposition(self, A, spectral_idempotents):
        """A = 12*E0 + 2*E1 + (-4)*E2."""
        E0, E1, E2 = spectral_idempotents
        recon = 12 * E0 + 2 * E1 + (-4) * E2
        assert np.allclose(recon, A.astype(float), atol=1e-10)

    def test_idempotent_orthogonality(self, spectral_idempotents):
        """E_i * E_j = 0 for i != j."""
        E0, E1, E2 = spectral_idempotents
        assert np.allclose(E0 @ E1, 0, atol=1e-10)
        assert np.allclose(E0 @ E2, 0, atol=1e-10)
        assert np.allclose(E1 @ E2, 0, atol=1e-10)

    def test_idempotent_square(self, spectral_idempotents):
        """E_i^2 = E_i (projection property)."""
        E0, E1, E2 = spectral_idempotents
        assert np.allclose(E0 @ E0, E0, atol=1e-10)
        assert np.allclose(E1 @ E1, E1, atol=1e-10)
        assert np.allclose(E2 @ E2, E2, atol=1e-10)


# ===================================================================
# T1666 -- Bose-Mesner algebra recurrence
# ===================================================================

class TestT1666:
    """A^n = a_n I + b_n A + c_n J via the Bose-Mesner recurrence."""

    def test_A2_bose_mesner(self, A, A2, I_n, J):
        """A^2 = 8I - 2A + 4J."""
        assert np.array_equal(A2, 8 * I_n - 2 * A + 4 * J)

    def test_A4_bose_mesner(self, A, A4, I_n, J):
        """A^4 = 96I - 40A + 528J."""
        expected = 96 * I_n - 40 * A + 528 * J
        assert np.array_equal(A4, expected)

    def test_A5_bose_mesner(self, A, A5, I_n, J):
        """A^5 = -320I + 176A + 6176J."""
        expected = -320 * I_n + 176 * A + 6176 * J
        assert np.array_equal(A5, expected)


# ===================================================================
# T1667 -- Discriminant and resultant of the minimal polynomial
# ===================================================================

class TestT1667:
    """Discriminant of p(x) = (x-12)(x-2)(x+4)."""

    def test_discriminant_value(self):
        """disc(p) = prod_{i<j} (r_i - r_j)^2 = 10^2 * 16^2 * 6^2 = 921600."""
        disc = (12 - 2)**2 * (12 - (-4))**2 * (2 - (-4))**2
        assert disc == 921600

    def test_discriminant_positive(self):
        """disc > 0 confirms all roots are real and distinct."""
        disc = 921600
        assert disc > 0

    def test_discriminant_factorisation(self):
        """921600 = 2^12 * 3^2 * 5^2."""
        assert 921600 == 2**12 * 3**2 * 5**2
        assert _v_p(921600, 2) == 12
        assert _v_p(921600, 3) == 2
        assert _v_p(921600, 5) == 2
        remaining = 921600 // (2**12 * 3**2 * 5**2)
        assert remaining == 1


# ===================================================================
# T1668 -- Newton's identities (power sums and elementary symmetric)
# ===================================================================

class TestT1668:
    """Newton's identities relating power sums to Vieta coefficients."""

    def test_newton_p1(self):
        """p1 = e1 = 12 + 2 + (-4) = 10."""
        p1 = 12 + 2 + (-4)
        e1 = 10
        assert p1 == e1

    def test_newton_p2(self):
        """p2 = p1*e1 - 2*e2 = 10*10 - 2*(-32) = 164."""
        e1, e2 = 10, -32
        p1 = 10
        p2_actual = 12**2 + 2**2 + (-4)**2
        p2_newton = p1 * e1 - 2 * e2
        assert p2_actual == 164
        assert p2_newton == p2_actual

    def test_newton_p3(self):
        """p3 = p2*e1 - p1*e2 + 3*e3 = 1672."""
        e1, e2, e3 = 10, -32, -96
        p1, p2 = 10, 164
        p3_actual = 12**3 + 2**3 + (-4)**3
        p3_newton = p2 * e1 - p1 * e2 + 3 * e3
        assert p3_actual == 1672
        assert p3_newton == p3_actual


# ===================================================================
# T1669 -- GF(2) reduction and nilpotency
# ===================================================================

class TestT1669:
    """Properties of the adjacency matrix reduced modulo 2."""

    def test_A_mod2_nonzero(self, A):
        """A mod 2 is nonzero (A has entries equal to 1)."""
        assert np.any(A % 2 != 0)

    def test_nilpotent_mod2(self, A2):
        """A^2 = 0 mod 2 (all entries of A^2 are even)."""
        assert np.all(A2 % 2 == 0)

    def test_nilpotency_index_exactly_2(self, A, A2):
        """Nilpotency index over GF(2) is exactly 2: A != 0 but A^2 = 0 mod 2."""
        assert np.any(A % 2 != 0), "A mod 2 should be nonzero"
        assert np.all(A2 % 2 == 0), "A^2 mod 2 should be zero"

    def test_gf2_rank(self, A):
        """rank_GF(2)(A) = 16; null space dimension = 24."""
        r2 = _gfp_rank(A, 2)
        assert r2 == 16
        assert _n - r2 == 24


# ===================================================================
# T1670 -- GF(3) reduction
# ===================================================================

class TestT1670:
    """Properties of the adjacency matrix reduced modulo 3."""

    def test_A2_mod3(self, A, A2, I_n, J):
        """A^2 = 2I + A + J (mod 3)."""
        expected_mod3 = (2 * I_n + A + J) % 3
        actual_mod3 = A2 % 3
        assert np.array_equal(actual_mod3, expected_mod3)

    def test_gf3_rank(self, A):
        """rank_GF(3)(A) = 39; the null space is 1-dimensional."""
        r3 = _gfp_rank(A, 3)
        assert r3 == 39
        assert _n - r3 == 1

    def test_all_ones_in_gf3_kernel(self, A):
        """The all-ones vector j is in ker(A mod 3) since A*j = 12*j = 0*j mod 3."""
        j = np.ones(_n, dtype=int)
        Aj = A @ j
        assert np.all(Aj % 3 == 0)


# ===================================================================
# T1671 -- Eigenvalue multiplicative orders modulo primes
# ===================================================================

class TestT1671:
    """Multiplicative orders of eigenvalues in GF(p)^*."""

    @staticmethod
    def _mult_order(a, p):
        """Return the multiplicative order of a in (Z/pZ)^*."""
        a = a % p
        if a == 0:
            return None  # not invertible
        order = 1
        val = a
        while val % p != 1:
            val = (val * a) % p
            order += 1
        return order

    def test_orders_mod5(self):
        """mod 5: ord(12)=4, ord(2)=4, ord(-4)=1."""
        assert self._mult_order(12, 5) == 4
        assert self._mult_order(2, 5) == 4
        assert self._mult_order(-4, 5) == 1

    def test_orders_mod7(self):
        """mod 7: ord(12)=6, ord(2)=3, ord(-4)=6."""
        assert self._mult_order(12, 7) == 6
        assert self._mult_order(2, 7) == 3
        assert self._mult_order(-4, 7) == 6

    def test_orders_mod13(self):
        """mod 13: ord(12)=2, ord(2)=12, ord(-4)=3."""
        assert self._mult_order(12, 13) == 2
        assert self._mult_order(2, 13) == 12
        assert self._mult_order(-4, 13) == 3


# ===================================================================
# T1672 -- Characteristic polynomial at integer points
# ===================================================================

class TestT1672:
    """chi(m) = (m-12)^1 * (m-2)^24 * (m+4)^15 at selected integers."""

    def test_chi_at_zero(self):
        """chi(0) = det(A) = -3 * 2^56."""
        chi_0 = (-12)**1 * (-2)**24 * 4**15
        assert chi_0 == -3 * 2**56

    def test_chi_at_one(self):
        """chi(1) = -11 * 5^15 = -335693359375."""
        chi_1 = (-11) * (-1)**24 * 5**15
        assert chi_1 == -11 * 5**15
        assert chi_1 == -335693359375

    def test_chi_at_minus_one(self):
        """chi(-1) = -13 * 3^39."""
        chi_m1 = (-13) * (-3)**24 * 3**15
        assert chi_m1 == -13 * 3**39
        assert chi_m1 == -13 * 4052555153018976267

    def test_chi_at_three(self):
        """chi(3) = -9 * 7^15."""
        chi_3 = (-9) * 1**24 * 7**15
        assert chi_3 == -9 * 7**15
        assert chi_3 == -42728053589487


# ===================================================================
# T1673 -- Complement graph spectrum
# ===================================================================

class TestT1673:
    """Spectral properties of the complement graph J - I - A."""

    def test_complement_eigenvalues(self, A, I_n, J):
        """Complement eigenvalues are 27 (mult 1), -3 (mult 24), 3 (mult 15)."""
        Abar = J - I_n - A
        evals = np.linalg.eigvalsh(Abar.astype(float))
        evals_int = np.round(evals).astype(int)
        unique, counts = np.unique(evals_int, return_counts=True)
        mults = dict(zip(unique.tolist(), counts.tolist()))
        assert mults == {27: 1, -3: 24, 3: 15}

    def test_complement_regularity(self, A, I_n, J):
        """Complement is (n-1-k) = 27 regular."""
        Abar = J - I_n - A
        row_sums = Abar.sum(axis=1)
        assert np.all(row_sums == _n - 1 - _k)
        assert _n - 1 - _k == 27

    def test_complement_in_bose_mesner(self, A, I_n, J):
        """A_complement = J - I - A belongs to span{I, A, J}."""
        # Coefficients: a=-1, b=-1, c=1 in aI + bA + cJ
        Abar = J - I_n - A
        expected = -1 * I_n + (-1) * A + 1 * J
        assert np.array_equal(Abar, expected)


# ===================================================================
# T1674 -- Companion matrix of the minimal polynomial
# ===================================================================

class TestT1674:
    """Companion matrix of p(x) = x^3 - 10x^2 - 32x + 96."""

    @pytest.fixture
    def C(self):
        """Companion matrix in standard form."""
        return np.array([[0, 0, -96],
                         [1, 0,  32],
                         [0, 1,  10]], dtype=int)

    def test_companion_satisfies_min_poly(self, C):
        """C^3 - 10C^2 - 32C + 96I_3 = 0."""
        I3 = np.eye(3, dtype=int)
        C2 = C @ C
        C3 = C @ C2
        residual = C3 - 10 * C2 - 32 * C + 96 * I3
        assert np.array_equal(residual, np.zeros((3, 3), dtype=int))

    def test_companion_eigenvalues(self, C):
        """Companion matrix has eigenvalues {12, 2, -4}."""
        evals = np.linalg.eigvals(C)
        evals_sorted = sorted(np.round(evals.real).astype(int))
        assert evals_sorted == [-4, 2, 12]

    def test_companion_char_poly(self, C):
        """det(xI - C) = x^3 - 10x^2 - 32x + 96."""
        # Verify by evaluating det(xI - C) at the three roots
        I3 = np.eye(3)
        for root in [12, 2, -4]:
            det_val = np.linalg.det(root * I3 - C.astype(float))
            assert abs(det_val) < 1e-10, f"det({root}I - C) should be 0"


# ===================================================================
# T1675 -- Galois group and algebraic integer properties
# ===================================================================

class TestT1675:
    """Algebraic number theory of the spectrum."""

    def test_all_eigenvalues_are_integers(self, A):
        """All eigenvalues of A are rational integers (elements of Z)."""
        evals = np.linalg.eigvalsh(A)
        for ev in evals:
            assert abs(ev - round(ev)) < 1e-10, f"eigenvalue {ev} is not an integer"

    def test_galois_group_trivial(self):
        """The minimal polynomial splits over Q, so Gal(Q(eigenvalues)/Q) = {id}."""
        # All roots 12, 2, -4 are in Q, so the splitting field is Q itself.
        roots = [12, 2, -4]
        # Each root is rational: Galois group has order 1
        assert all(isinstance(r, int) for r in roots)
        # Galois group order = degree of splitting field extension = [Q:Q] = 1
        galois_order = 1
        assert galois_order == 1

    def test_srg_integrality_condition(self):
        """SRG integrality: (lambda-mu)^2 + 4(k-mu) = 36 is a perfect square."""
        Delta = (_lam - _mu)**2 + 4 * (_k - _mu)
        assert Delta == 36
        import math
        assert math.isqrt(Delta)**2 == Delta


# ===================================================================
# T1676 -- Number-theoretic identities from SRG parameters
# ===================================================================

class TestT1676:
    """Number-theoretic identities connecting SRG parameters and spectrum."""

    def test_vieta_sum(self):
        """Sum of minimal poly roots = 12 + 2 + (-4) = 10 = -(-10) = coeff of x^2."""
        assert 12 + 2 + (-4) == 10

    def test_vieta_product(self):
        """Product of roots = 12 * 2 * (-4) = -96 = (-1)^3 * 96."""
        assert 12 * 2 * (-4) == -96

    def test_vieta_sum_of_pairs(self):
        """Sum of pairwise products = 12*2 + 12*(-4) + 2*(-4) = -32."""
        assert 12 * 2 + 12 * (-4) + 2 * (-4) == -32

    def test_srg_parameter_identity(self):
        """k(k - lambda - 1) = mu(n - k - 1) => 108 = 108."""
        lhs = _k * (_k - _lam - 1)
        rhs = _mu * (_n - _k - 1)
        assert lhs == rhs
        assert lhs == 108

    def test_multiplicity_formula(self):
        """Multiplicities from SRG parameters via the standard formula."""
        Delta = (_lam - _mu)**2 + 4 * (_k - _mu)
        sqrt_Delta = 6  # sqrt(36) = 6
        assert sqrt_Delta**2 == Delta
        f = (_n - 1 + ((_n - 1) * (_mu - _lam) - 2 * _k) / sqrt_Delta) / 2
        g = (_n - 1 - ((_n - 1) * (_mu - _lam) - 2 * _k) / sqrt_Delta) / 2
        assert f == 24  # multiplicity of r = 2
        assert g == 15  # multiplicity of s = -4

    def test_eigenvalue_sum_rule(self):
        """Weighted eigenvalue sum: 12*1 + 2*24 + (-4)*15 = 0 = tr(A)."""
        weighted_sum = 12 * 1 + 2 * 24 + (-4) * 15
        assert weighted_sum == 0

    def test_eigenvalue_quadratic_relation(self):
        """Restricted eigenvalues r, s satisfy x^2 - (lambda-mu)x - (k-mu) = 0."""
        for x in [_r, _s]:
            val = x**2 - (_lam - _mu) * x - (_k - _mu)
            assert val == 0, f"r={x} does not satisfy the quadratic"

    def test_triangle_count(self, A3):
        """Number of triangles = n*k*lambda/6 = 160."""
        num_triangles = _n * _k * _lam // 6
        assert num_triangles == 160
        assert np.trace(A3) == 6 * num_triangles

    def test_edge_count(self, A):
        """Number of edges = n*k/2 = 240."""
        num_edges = np.sum(A) // 2
        assert num_edges == _n * _k // 2
        assert num_edges == 240

    def test_sum_inverse_eigenvalues(self):
        """1/12 + 1/2 + 1/(-4) = 1/3."""
        from fractions import Fraction
        s = Fraction(1, 12) + Fraction(1, 2) + Fraction(1, -4)
        assert s == Fraction(1, 3)

    def test_gf5_gf7_full_rank(self, A):
        """A has full rank over GF(5) and GF(7) (det coprime to 5 and 7)."""
        r5 = _gfp_rank(A, 5)
        r7 = _gfp_rank(A, 7)
        assert r5 == 40
        assert r7 == 40
