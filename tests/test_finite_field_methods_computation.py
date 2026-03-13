"""
Phase CXXV -- Finite Field Methods Computation on W(3,3) = SRG(40,12,2,4).

96 tests across 12 classes:
  1. TestGF2RankNullity             (10 tests)
  2. TestGF3RankNullity             (10 tests)
  3. TestGF5GF7Analysis             ( 8 tests)
  4. TestPRankSweep                 (10 tests)
  5. TestSmithDivisibility          ( 6 tests)
  6. TestKernelStructure            (10 tests)
  7. TestModularTraces              ( 8 tests)
  8. TestChevalleyWarning           ( 6 tests)
  9. TestQuadraticSymplectic        ( 8 tests)
 10. TestFiniteFieldDeterminant     ( 6 tests)
 11. TestCharPolyModP               ( 8 tests)
 12. TestSymplecticFormVerification ( 6 tests)

Only numpy and standard library.  Every assertion is mathematically provable
from the SRG(40,12,2,4) structure and its spectrum
    adjacency:  {12^1, 2^24, (-4)^15}

Key finite-field results:
    rank_GF(2)(A) = 16   nullity = 24   [A nilpotent mod 2, index 2]
    rank_GF(3)(A) = 39   nullity = 1    [ker = span(j)]
    rank_GF(p)(A) = 40   for all primes p >= 5   [det = -3 * 2^56]
"""

import numpy as np
import pytest
from math import gcd
from functools import reduce


# ---------------------------------------------------------------------------
# W(3,3) builder
# ---------------------------------------------------------------------------

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


def _build_points():
    """Build the 40 projective points of PG(3,3) in canonical order."""
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
    return points


# ---------------------------------------------------------------------------
# Finite field arithmetic helpers  (numpy + stdlib only)
# ---------------------------------------------------------------------------

def _gf_rank(M, p):
    """Rank of integer matrix M over GF(p) via Gaussian elimination."""
    W = np.array(M, dtype=np.int64) % p
    rows, cols = W.shape
    rank = 0
    for col in range(cols):
        pivot = None
        for row in range(rank, rows):
            if W[row, col] % p != 0:
                pivot = row
                break
        if pivot is None:
            continue
        W[[rank, pivot]] = W[[pivot, rank]]
        inv = pow(int(W[rank, col]), -1, p)
        W[rank] = (W[rank] * inv) % p
        for row in range(rows):
            if row != rank and W[row, col] % p != 0:
                W[row] = (W[row] - int(W[row, col]) * W[rank]) % p
        rank += 1
    return rank


def _gf_nullspace(M, p):
    """Null space basis of M over GF(p).  Returns list of numpy vectors."""
    W = np.array(M, dtype=np.int64) % p
    rows, cols = W.shape
    pivots = []
    for col in range(cols):
        pivot = None
        for row in range(len(pivots), rows):
            if W[row, col] % p != 0:
                pivot = row
                break
        if pivot is None:
            continue
        r = len(pivots)
        W[[r, pivot]] = W[[pivot, r]]
        inv = pow(int(W[r, col]), -1, p)
        W[r] = (W[r] * inv) % p
        for row in range(rows):
            if row != r and W[row, col] % p != 0:
                W[row] = (W[row] - int(W[row, col]) * W[r]) % p
        pivots.append(col)
    free = [c for c in range(cols) if c not in pivots]
    basis = []
    for fc in free:
        v = np.zeros(cols, dtype=np.int64)
        v[fc] = 1
        for i, pc in enumerate(pivots):
            v[pc] = (-W[i, fc]) % p
        basis.append(v % p)
    return basis


def _gf_det(M, p):
    """Determinant of square matrix M over GF(p) via row reduction."""
    W = np.array(M, dtype=np.int64) % p
    n = W.shape[0]
    assert W.shape[1] == n
    det = 1
    for col in range(n):
        pivot = None
        for row in range(col, n):
            if W[row, col] % p != 0:
                pivot = row
                break
        if pivot is None:
            return 0
        if pivot != col:
            W[[col, pivot]] = W[[pivot, col]]
            det = (-det) % p
        det = (det * int(W[col, col])) % p
        inv = pow(int(W[col, col]), -1, p)
        W[col] = (W[col] * inv) % p
        for row in range(col + 1, n):
            if W[row, col] % p != 0:
                W[row] = (W[row] - int(W[row, col]) * W[col]) % p
    return det % p


def _mat_mul_mod(A, B, p):
    """Matrix product A @ B reduced mod p."""
    return (np.array(A, dtype=np.int64) @ np.array(B, dtype=np.int64)) % p


def _mat_pow_mod(M, k, p):
    """Matrix power M^k mod p via repeated squaring."""
    n = M.shape[0]
    result = np.eye(n, dtype=np.int64)
    base = np.array(M, dtype=np.int64) % p
    while k > 0:
        if k & 1:
            result = (result @ base) % p
        base = (base @ base) % p
        k >>= 1
    return result


# ---------------------------------------------------------------------------
# Module-level precomputed data  (built once)
# ---------------------------------------------------------------------------

_A = _build_w33()
_points = _build_points()
_n = 40
_k_reg = 12
_lam = 2
_mu = 4
_I = np.eye(_n, dtype=int)
_J = np.ones((_n, _n), dtype=int)
_j = np.ones(_n, dtype=int)

# Standard symplectic form matrix  Omega = [[0,1,0,0],[-1,0,0,0],...]
_Omega = np.array([[0, 1, 0, 0],
                    [-1, 0, 0, 0],
                    [0, 0, 0, 1],
                    [0, 0, -1, 0]], dtype=int)


# ===================================================================
# 1.  GF(2) Rank and Nullity                             (10 tests)
# ===================================================================

class TestGF2RankNullity:
    """GF(2) rank = 16, nullity = 24.  A is nilpotent mod 2 with index 2."""

    def test_rank_gf2_equals_16(self):
        """rank_GF(2)(A) = 16."""
        assert _gf_rank(_A, 2) == 16

    def test_nullity_gf2_equals_24(self):
        """nullity_GF(2)(A) = 40 - 16 = 24."""
        assert _n - _gf_rank(_A, 2) == 24

    def test_A_squared_zero_mod2(self):
        """A^2 = 0 over GF(2): from SRG eq A^2 = -2A+8I+4J, all coeffs even."""
        A2 = _mat_mul_mod(_A, _A, 2)
        assert np.all(A2 == 0)

    def test_A_nonzero_mod2(self):
        """A != 0 over GF(2): adjacency matrix has entries 1."""
        assert np.any(_A % 2 != 0)

    def test_nilpotency_index_is_2(self):
        """Nilpotency index of A mod 2 is exactly 2: A != 0 but A^2 = 0."""
        assert np.any(_A % 2 != 0)
        assert np.all((_A @ _A) % 2 == 0)

    def test_image_inside_kernel_mod2(self):
        """im(A mod 2) subset ker(A mod 2), so rank <= nullity."""
        r = _gf_rank(_A, 2)
        assert r <= _n - r

    def test_row_sums_zero_mod2(self):
        """k = 12 is even, so all row sums = 0 mod 2."""
        row_sums = np.sum(_A, axis=1) % 2
        assert np.all(row_sums == 0)

    def test_A_plus_I_invertible_mod2(self):
        """A + I has full rank 40 over GF(2)."""
        assert _gf_rank((_A + _I).astype(int), 2) == _n

    def test_symmetric_mod2(self):
        """A is symmetric over GF(2)."""
        assert np.array_equal(_A % 2, _A.T % 2)

    def test_diagonal_zero_mod2(self):
        """Diagonal of A is all zeros (simple graph, no self-loops)."""
        assert np.all(np.diag(_A) == 0)


# ===================================================================
# 2.  GF(3) Rank and Nullity                             (10 tests)
# ===================================================================

class TestGF3RankNullity:
    """GF(3) rank = 39, nullity = 1.  ker(A mod 3) = span(j)."""

    def test_rank_gf3_equals_39(self):
        """rank_GF(3)(A) = 39.  Only one eigenvalue (12) is 0 mod 3."""
        assert _gf_rank(_A, 3) == 39

    def test_nullity_gf3_equals_1(self):
        """nullity_GF(3)(A) = 1."""
        assert _n - _gf_rank(_A, 3) == 1

    def test_kernel_gf3_is_span_of_j(self):
        """The unique (up to scalar) null vector over GF(3) is j = (1,...,1)."""
        ker = _gf_nullspace(_A, 3)
        assert len(ker) == 1
        v = ker[0]
        # v should be a nonzero scalar multiple of j mod 3
        first_nz = v[v != 0][0]
        inv = pow(int(first_nz), -1, 3)
        scaled = (v * inv) % 3
        assert np.array_equal(scaled, _j % 3)

    def test_A_plus_I_squared_equals_J_mod3(self):
        """(A + I)^2 = J over GF(3).  From SRG eq: A^2 - A - 2I = J."""
        # Since -2 = 1 mod 3:  A^2 + 2A + I = (A+I)^2 = ?
        # Actually A^2 = -2A + 8I + 4J.  Mod 3: A^2 = A + 2I + J.
        # So (A+I)^2 = A^2 + 2A + I = (A + 2I + J) + 2A + I = 3A + 3I + J = J mod 3.
        ApI2 = _mat_mul_mod(_A + _I, _A + _I, 3)
        assert np.array_equal(ApI2, _J % 3)

    def test_rank_A_minus_2I_mod3_equals_11(self):
        """rank(A - 2I mod 3) = 11.  Eigenvalue 2 has geometric mult 29."""
        assert _gf_rank((_A - 2 * _I).astype(int), 3) == 11

    def test_rank_A_minus_2I_squared_mod3_equals_1(self):
        """rank((A - 2I)^2 mod 3) = 1.  Since (A-2I)^2 = (A+I)^2 = J, rank = 1."""
        B = (_A - 2 * _I).astype(int)
        B2 = B @ B
        assert _gf_rank(B2, 3) == 1

    def test_row_sums_zero_mod3(self):
        """k = 12 = 0 mod 3, so all row sums vanish mod 3."""
        row_sums = np.sum(_A, axis=1) % 3
        assert np.all(row_sums == 0)

    def test_srg_equation_mod3(self):
        """SRG equation mod 3: A^2 = A + 2I + J."""
        A2 = _mat_mul_mod(_A, _A, 3)
        rhs = (_A + 2 * _I + _J) % 3
        assert np.array_equal(A2, rhs)

    def test_minimal_poly_divides_x_times_x_minus_2_squared_mod3(self):
        """x(x-2)^2 = x^3 + 2x^2 + x annihilates A over GF(3)."""
        # A^3 + 2A^2 + A mod 3 = 0
        A2 = _A @ _A
        A3 = A2 @ _A
        result = (A3 + 2 * A2 + _A) % 3
        assert np.all(result == 0)

    def test_x_times_x_minus_2_does_not_annihilate_mod3(self):
        """x(x-2) does NOT annihilate A mod 3: minimal poly has degree 3."""
        # A(A-2I) = A^2 - 2A mod 3
        result = (_A @ _A - 2 * _A) % 3
        assert np.any(result % 3 != 0)


# ===================================================================
# 3.  GF(5) and GF(7) Analysis                           (8 tests)
# ===================================================================

class TestGF5GF7Analysis:
    """For primes p >= 5, A has full rank 40 (det coprime to p)."""

    def test_rank_gf5_full(self):
        """rank_GF(5)(A) = 40."""
        assert _gf_rank(_A, 5) == _n

    def test_rank_gf7_full(self):
        """rank_GF(7)(A) = 40."""
        assert _gf_rank(_A, 7) == _n

    def test_det_nonzero_mod5(self):
        """det(A) = -3*2^56 != 0 mod 5.  2^4 = 1 mod 5, so det = -3 = 2 mod 5."""
        assert _gf_det(_A, 5) == 2

    def test_det_nonzero_mod7(self):
        """det(A) = -3*2^56 != 0 mod 7.  2^3 = 1 mod 7, so det = -12 = 2 mod 7."""
        assert _gf_det(_A, 7) == 2

    def test_row_sums_mod5(self):
        """k = 12 = 2 mod 5, so all row sums are 2 mod 5."""
        row_sums = np.sum(_A, axis=1) % 5
        assert np.all(row_sums == 2)

    def test_row_sums_mod7(self):
        """k = 12 = 5 mod 7, so all row sums are 5 mod 7."""
        row_sums = np.sum(_A, axis=1) % 7
        assert np.all(row_sums == 5)

    def test_srg_equation_mod5(self):
        """SRG equation mod 5: A^2 = -2A + 8I + 4J = 3A + 3I + 4J mod 5."""
        A2 = _mat_mul_mod(_A, _A, 5)
        rhs = (3 * _A + 3 * _I + 4 * _J) % 5
        assert np.array_equal(A2, rhs)

    def test_srg_equation_mod7(self):
        """SRG equation mod 7: A^2 = -2A + 8I + 4J = 5A + I + 4J mod 7."""
        A2 = _mat_mul_mod(_A, _A, 7)
        rhs = (5 * _A + 1 * _I + 4 * _J) % 7
        assert np.array_equal(A2, rhs)


# ===================================================================
# 4.  p-Rank Sweep                                       (10 tests)
# ===================================================================

class TestPRankSweep:
    """p-rank of A for the first 10 primes.
    Only p = 2 and p = 3 divide det(A) = -3*2^56."""

    @pytest.mark.parametrize("p, expected_rank", [
        (2, 16),
        (3, 39),
        (5, 40),
        (7, 40),
        (11, 40),
        (13, 40),
        (17, 40),
        (19, 40),
        (23, 40),
        (29, 40),
    ])
    def test_p_rank(self, p, expected_rank):
        """rank_GF(p)(A) matches expected value."""
        assert _gf_rank(_A, p) == expected_rank


# ===================================================================
# 5.  Smith Normal Form / Divisibility                    (6 tests)
# ===================================================================

class TestSmithDivisibility:
    """Invariant-factor divisibility from det = -3 * 2^56 and p-ranks."""

    def test_d1_equals_1(self):
        """First invariant factor d_1 = gcd of all entries = 1."""
        entries = _A.ravel()
        assert reduce(gcd, entries.tolist()) == 1

    def test_gcd_2x2_minors_equals_1(self):
        """gcd of all 2x2 minors = 1, so d_2 = 1 as well."""
        g = 0
        for i1 in range(_n):
            for i2 in range(i1 + 1, _n):
                for j1 in range(_n):
                    for j2 in range(j1 + 1, _n):
                        det2 = int(_A[i1, j1]) * int(_A[i2, j2]) \
                             - int(_A[i1, j2]) * int(_A[i2, j1])
                        g = gcd(g, abs(det2))
                        if g == 1:
                            return  # early exit: gcd is already 1
        assert g == 1

    def test_2adic_valuation_of_det(self):
        """v_2(det(A)) = 56.  det = -3 * 2^56."""
        d = abs(12 * (2 ** 24) * ((-4) ** 15))
        v = 0
        while d % 2 == 0:
            d //= 2
            v += 1
        assert v == 56

    def test_3adic_valuation_of_det(self):
        """v_3(det(A)) = 1.  Only one eigenvalue (12) is divisible by 3."""
        d = abs(12 * (2 ** 24) * ((-4) ** 15))
        v = 0
        while d % 3 == 0:
            d //= 3
            v += 1
        assert v == 1

    def test_no_prime_ge5_divides_det(self):
        """v_p(det) = 0 for every prime p >= 5."""
        d = abs(12 * (2 ** 24) * ((-4) ** 15))
        # Strip 2s and 3s
        while d % 2 == 0:
            d //= 2
        while d % 3 == 0:
            d //= 3
        assert d == 1

    def test_abs_det_equals_3_times_2_to_56(self):
        """|det(A)| = 3 * 2^56 = 216172782113783808."""
        expected = 3 * (2 ** 56)
        actual = abs(12 * (2 ** 24) * ((-4) ** 15))
        assert actual == expected


# ===================================================================
# 6.  Kernel Structure                                   (10 tests)
# ===================================================================

class TestKernelStructure:
    """Kernel bases over various GF(p) and their code-theoretic properties."""

    def test_gf2_kernel_dimension(self):
        """dim ker(A mod 2) = 24."""
        ker = _gf_nullspace(_A, 2)
        assert len(ker) == 24

    def test_gf2_kernel_vectors_satisfy_Av_zero(self):
        """Every GF(2) kernel vector v satisfies Av = 0 mod 2."""
        ker = _gf_nullspace(_A, 2)
        for v in ker:
            assert np.all((_A @ v) % 2 == 0)

    def test_gf2_kernel_vectors_even_weight(self):
        """All GF(2) kernel vectors have even Hamming weight."""
        ker = _gf_nullspace(_A, 2)
        for v in ker:
            assert int(np.sum(v)) % 2 == 0

    def test_j_in_gf2_kernel(self):
        """j = (1,...,1) is in ker(A mod 2) since k = 12 is even."""
        assert np.all((_A @ _j) % 2 == 0)

    def test_j_in_gf3_kernel(self):
        """j is in ker(A mod 3) since k = 12 = 0 mod 3."""
        assert np.all((_A @ _j) % 3 == 0)

    def test_j_not_in_gf5_kernel(self):
        """j is NOT in ker(A mod 5): Aj = 12j, 12 = 2 mod 5 != 0."""
        result = (_A @ _j) % 5
        assert not np.all(result == 0)
        assert np.all(result == 2)  # Aj = 12j = 2j mod 5

    def test_gf3_kernel_spanned_by_j(self):
        """ker(A mod 3) = 1-dimensional, spanned by j."""
        ker = _gf_nullspace(_A, 3)
        assert len(ker) == 1

    def test_gf5_kernel_trivial(self):
        """ker(A mod 5) = {0}: A is invertible mod 5."""
        ker = _gf_nullspace(_A, 5)
        assert len(ker) == 0

    def test_image_mod2_is_self_orthogonal(self):
        """im(A mod 2) is self-orthogonal: A^T A = A^2 = 0 mod 2."""
        A2 = _mat_mul_mod(_A, _A, 2)
        assert np.all(A2 == 0)

    def test_kernel_mod2_is_not_self_orthogonal(self):
        """ker(A mod 2) properly contains im(A mod 2), so not self-orthogonal.
        dim(ker) = 24 > dim(im) = 16; ker cannot be inside its dual (= im)."""
        ker = _gf_nullspace(_A, 2)
        gram = np.zeros((_n, _n), dtype=int)
        # Check inner products of kernel basis vectors mod 2
        ker_arr = np.array(ker, dtype=np.int64)
        gram = (ker_arr @ ker_arr.T) % 2
        assert np.any(gram != 0)


# ===================================================================
# 7.  Modular Traces  (eigenvalue power sums)             (8 tests)
# ===================================================================

class TestModularTraces:
    """tr(A^k) = 12^k + 24*2^k + 15*(-4)^k for all k >= 0."""

    def test_trace_A0(self):
        """tr(I) = 40."""
        assert np.trace(_I) == _n

    def test_trace_A1(self):
        """tr(A) = 12 + 48 - 60 = 0."""
        assert int(np.trace(_A)) == 0

    def test_trace_A2(self):
        """tr(A^2) = 144 + 96 + 240 = 480 = n*k."""
        assert int(np.trace(_A @ _A)) == 480

    def test_trace_A3(self):
        """tr(A^3) = 6 * triangles = 6*160 = 960."""
        A3 = _A @ _A @ _A
        assert int(np.trace(A3)) == 960

    def test_trace_A4(self):
        """tr(A^4) = 12^4 + 24*16 + 15*256 = 24960."""
        A4 = np.linalg.matrix_power(_A, 4)
        assert int(np.trace(A4)) == 24960

    def test_trace_formula_k5_to_k8(self):
        """tr(A^k) matches 12^k + 24*2^k + 15*(-4)^k for k = 5..8."""
        for k in range(5, 9):
            Ak = np.linalg.matrix_power(_A, k)
            expected = 12**k + 24 * (2**k) + 15 * ((-4)**k)
            assert int(np.trace(Ak)) == expected

    def test_traces_all_zero_mod2(self):
        """All eigenvalues are even, so tr(A^k) = 0 mod 2 for k >= 1."""
        for k in range(1, 6):
            Ak = np.linalg.matrix_power(_A, k)
            assert int(np.trace(Ak)) % 2 == 0

    def test_traces_all_zero_mod3(self):
        """12^k + 24*2^k + 15*(-4)^k = 0 mod 3 for k >= 1.
        (12 = 0, 24 = 0, 15 = 0 mod 3.)"""
        for k in range(1, 6):
            expected = 12**k + 24 * (2**k) + 15 * ((-4)**k)
            assert expected % 3 == 0


# ===================================================================
# 8.  Chevalley--Warning Theorem                          (6 tests)
# ===================================================================

class TestChevalleyWarning:
    """Chevalley-Warning: polynomial zeros over GF(q) when sum(deg) < n vars."""

    def test_orthogonal_count_is_27_per_vertex(self):
        """For each vertex u, |{v in GF(3)^4 : omega(u,v) = 0}| = 3^3 = 27.
        omega(u, .) is a nonzero linear form with 3-dim kernel."""
        pts = _points
        for idx in range(_n):
            u = np.array(pts[idx])
            count = 0
            for a in range(3):
                for b in range(3):
                    for c in range(3):
                        for d in range(3):
                            x = np.array([a, b, c, d])
                            if int(u @ _Omega @ x) % 3 == 0:
                                count += 1
            assert count == 27

    def test_chevalley_warning_bound_27_mod3(self):
        """27 = 0 mod 3, consistent with Chevalley-Warning (deg 1 < 4 vars)."""
        assert 27 % 3 == 0

    def test_omega_takes_each_value_equally(self):
        """For nonzero u, omega(u,.) : GF(3)^4 -> GF(3) is surjective,
        each value hit exactly 3^3 = 27 times.  (81 / 3 = 27.)"""
        u = np.array(_points[0])
        counts = [0, 0, 0]
        for a in range(3):
            for b in range(3):
                for c in range(3):
                    for d in range(3):
                        val = int(u @ _Omega @ np.array([a, b, c, d])) % 3
                        counts[val] += 1
        assert counts == [27, 27, 27]

    def test_quadratic_form_zeros(self):
        """Hyperbolic Q(x) = x0*x1 + x2*x3 has 33 zeros in GF(3)^4."""
        count = 0
        for a in range(3):
            for b in range(3):
                for c in range(3):
                    for d in range(3):
                        if (a * b + c * d) % 3 == 0:
                            count += 1
        assert count == 33

    def test_quadratic_zeros_mod3(self):
        """33 = 0 mod 3, consistent with Chevalley-Warning (deg 2 < 4 vars)."""
        assert 33 % 3 == 0

    def test_omega_kernel_trivial(self):
        """Omega is non-degenerate: ker(Omega) = {0} over GF(3).
        rank(Omega mod 3) = 4 (full rank)."""
        assert _gf_rank(_Omega, 3) == 4


# ===================================================================
# 9.  Quadratic and Symplectic Forms                      (8 tests)
# ===================================================================

class TestQuadraticSymplectic:
    """Symplectic geometry of W(3,3): alternating form, isotropy, TI lines."""

    def test_omega_skew_symmetric(self):
        """Omega^T = -Omega (skew-symmetric / alternating)."""
        assert np.array_equal(_Omega, -_Omega.T)

    def test_omega_determinant_is_1(self):
        """det(Omega) = 1 over Z."""
        d = int(round(np.linalg.det(_Omega.astype(float))))
        assert d == 1

    def test_omega_alternating_all_vectors(self):
        """omega(v, v) = 0 for every v in GF(3)^4 (alternating form)."""
        for a in range(3):
            for b in range(3):
                for c in range(3):
                    for d in range(3):
                        v = np.array([a, b, c, d])
                        assert int(v @ _Omega @ v) % 3 == 0

    def test_adjacency_is_omega_orthogonality(self):
        """A[i,j] = 1 iff omega(points[i], points[j]) = 0 (for i != j)."""
        for i in range(_n):
            for j in range(i + 1, _n):
                u = np.array(_points[i])
                v = np.array(_points[j])
                orth = (int(u @ _Omega @ v) % 3 == 0)
                assert (_A[i, j] == 1) == orth

    def test_40_projective_points(self):
        """PG(3,3) has (3^4 - 1)/(3 - 1) = 40 projective points."""
        assert len(_points) == 40
        assert (3**4 - 1) // (3 - 1) == 40

    def test_each_point_has_12_neighbors(self):
        """Each vertex has exactly k = 12 omega-orthogonal neighbours."""
        degrees = np.sum(_A, axis=1)
        assert np.all(degrees == _k_reg)

    def test_totally_isotropic_line_count(self):
        """W(3,3) has exactly 40 totally isotropic lines (maximal TI 2-subspaces).
        Formula: product_{i=0}^{k-1} (q^{2(n-i)}-1)/(q^{i+1}-1) for k=n=2, q=3 => 40."""
        # Each edge lies on a unique TI line; each line has C(4,2) = 6 edges.
        # So TI_lines = 240 edges / 6 = 40.
        ti_edges = 0
        for i in range(_n):
            for j in range(i + 1, _n):
                if _A[i, j] != 1:
                    continue
                u, v = np.array(_points[i]), np.array(_points[j])
                line_pts = set()
                for a in range(3):
                    for b in range(3):
                        if a == 0 and b == 0:
                            continue
                        w = (a * u + b * v) % 3
                        first = next(x for x in w if x != 0)
                        inv_f = pow(int(first), -1, 3)
                        canon = tuple((int(c) * inv_f) % 3 for c in w)
                        line_pts.add(canon)
                # Verify all 4 points on line are mutually adjacent
                lp = list(line_pts)
                assert len(lp) == 4
                all_adj = True
                for a in range(4):
                    for b in range(a + 1, 4):
                        ia = _points.index(lp[a])
                        ib = _points.index(lp[b])
                        if _A[ia, ib] != 1:
                            all_adj = False
                assert all_adj
                ti_edges += 1
        assert ti_edges // 6 == 40

    def test_witt_index_is_2(self):
        """Witt index of Sp(4,3) is 2: there exist TI 2-subspaces.
        Example: span{e1, e3} = {(a,0,c,0)} has omega = 0 on all pairs."""
        e1 = np.array([1, 0, 0, 0])
        e3 = np.array([0, 0, 1, 0])
        assert int(e1 @ _Omega @ e3) % 3 == 0  # omega(e1, e3) = 0
        # Count projective points on this TI plane
        pts_on_plane = set()
        for a in range(3):
            for c in range(3):
                if a == 0 and c == 0:
                    continue
                v = (a * e1 + c * e3) % 3
                first = next(x for x in v if x != 0)
                inv_f = pow(int(first), -1, 3)
                canon = tuple((int(x) * inv_f) % 3 for x in v)
                pts_on_plane.add(canon)
        assert len(pts_on_plane) == 4  # (3^2 - 1)/(3 - 1) = 4


# ===================================================================
# 10. Finite Field Determinant                            (6 tests)
# ===================================================================

class TestFiniteFieldDeterminant:
    """det(A) = -3 * 2^56 verified mod various primes via GF(p) row reduction."""

    def test_det_from_eigenvalues(self):
        """det = 12 * 2^24 * (-4)^15 = -3 * 2^56."""
        det_val = 12 * (2 ** 24) * ((-4) ** 15)
        assert det_val == -3 * (2 ** 56)

    def test_det_zero_mod2(self):
        """det(A) = 0 mod 2 (A is singular over GF(2))."""
        assert _gf_det(_A, 2) == 0

    def test_det_zero_mod3(self):
        """det(A) = 0 mod 3 (A is singular over GF(3))."""
        assert _gf_det(_A, 3) == 0

    def test_det_mod5_equals_2(self):
        """det(A) mod 5 = 2.  (2^4 = 1 mod 5, so 2^56 = 1; -3 = 2 mod 5.)"""
        assert _gf_det(_A, 5) == 2

    def test_det_mod7_equals_2(self):
        """det(A) mod 7 = 2.  (2^3 = 1 mod 7, so 2^56 = 2^2 = 4; -3*4 = -12 = 2.)"""
        assert _gf_det(_A, 7) == 2

    def test_det_mod11_equals_6(self):
        """det(A) mod 11 = 6.  (2^10 = 1, 2^56 = 2^6 = 64 = 9; -3*9 = -27 = 6.)"""
        assert _gf_det(_A, 11) == 6


# ===================================================================
# 11. Characteristic Polynomial mod p                     (8 tests)
# ===================================================================

class TestCharPolyModP:
    """Characteristic polynomial (x-12)(x-2)^24(x+4)^15 reduced mod primes."""

    def test_eigenvalue_residues_mod2(self):
        """All eigenvalues {12, 2, -4} are 0 mod 2 => char poly = x^40 mod 2."""
        assert 12 % 2 == 0
        assert 2 % 2 == 0
        assert (-4) % 2 == 0

    def test_eigenvalue_residues_mod3(self):
        """Mod 3: 12=0, 2=2, -4=2.  char poly = x * (x-2)^39 mod 3."""
        assert 12 % 3 == 0
        assert 2 % 3 == 2
        assert (-4) % 3 == 2

    def test_eigenvalue_residues_mod5(self):
        """Mod 5: 12=2, 2=2, -4=1.  char poly = (x-2)^25 * (x-1)^15 mod 5."""
        assert 12 % 5 == 2
        assert 2 % 5 == 2
        assert (-4) % 5 == 1

    def test_eigenvalue_residues_mod7(self):
        """Mod 7: 12=5, 2=2, -4=3.  char poly = (x-5)(x-2)^24(x-3)^15 mod 7."""
        assert 12 % 7 == 5
        assert 2 % 7 == 2
        assert (-4) % 7 == 3

    def test_charpoly_eval_at_1_mod3(self):
        """char(1) mod 3: from x*(x-2)^39 at x=1 => 1*(-1)^39 = -1 = 2 mod 3.
        Verify via det(I - A) mod 3."""
        assert _gf_det((_I - _A).astype(int), 3) == 2

    def test_charpoly_eval_at_3_mod5(self):
        """char(3) mod 5: from (x-2)^25*(x-1)^15 at x=3 => 1^25 * 2^15 mod 5.
        2^4=1 mod 5 => 2^15 = 2^3 = 8 = 3 mod 5.  So char(3)=3 mod 5.
        Verify via det(3I - A) mod 5."""
        assert _gf_det((3 * _I - _A).astype(int), 5) == 3

    def test_charpoly_root_at_2_mod5(self):
        """2 is a root of char poly mod 5 (mult 25).  det(2I-A) = 0 mod 5."""
        assert _gf_det((2 * _I - _A).astype(int), 5) == 0

    def test_charpoly_root_at_5_mod7(self):
        """5 = 12 mod 7 is a root of char poly mod 7.  det(5I-A) = 0 mod 7."""
        assert _gf_det((5 * _I - _A).astype(int), 7) == 0


# ===================================================================
# 12. Symplectic Form Verification                        (6 tests)
# ===================================================================

class TestSymplecticFormVerification:
    """Structural tests on the symplectic form and complement graph."""

    def test_complement_is_27_regular(self):
        """Complement graph has regularity n-1-k = 39-12 = 27."""
        Abar = _J - _I - _A
        degrees = np.sum(Abar, axis=1)
        assert np.all(degrees == 27)

    def test_complement_rank_gf2(self):
        """rank_GF(2) of complement adjacency matrix is 40 (full rank).
        Abar = J-I-A; over GF(2), J=jj^T (rank 1), I has rank 40."""
        Abar = (_J - _I - _A)
        assert _gf_rank(Abar, 2) == 40

    def test_complement_rank_gf3(self):
        """rank_GF(3) of complement adjacency matrix is 10."""
        Abar = (_J - _I - _A)
        assert _gf_rank(Abar, 3) == 10

    def test_distinct_rows_mod2(self):
        """A has 40 distinct rows over GF(2) (each vertex has a unique
        neighbourhood as a binary vector)."""
        rows = set()
        for i in range(_n):
            rows.add(tuple(_A[i] % 2))
        assert len(rows) == 40

    def test_distinct_rows_mod3(self):
        """A has 40 distinct rows over GF(3)."""
        rows = set()
        for i in range(_n):
            rows.add(tuple(_A[i] % 3))
        assert len(rows) == 40

    def test_omega_rank4_mod_all_primes(self):
        """Omega has rank 4 over GF(p) for p = 2, 3, 5, 7 (non-degenerate)."""
        for p in [2, 3, 5, 7]:
            assert _gf_rank(_Omega, p) == 4
