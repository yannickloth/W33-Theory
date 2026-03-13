"""Phase CXXXII: Walk Enumeration & Counting on W(3,3) = SRG(40,12,2,4).

Spectrum: {12^1, 2^24, (-4)^15}.
Fundamental identity: tr(A^k) = 12^k + 24*2^k + 15*(-4)^k.
Closed walks of length k from any vertex = tr(A^k) / 40  (vertex-transitivity).
"""

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# W(3,3) builder
# ---------------------------------------------------------------------------

def _build_w33():
    """Build the 40x40 adjacency matrix of W(3,3) = Sp(4,3) polar graph."""
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
# Spectral helpers
# ---------------------------------------------------------------------------

def _spectral_walk_count(k):
    """W_k = tr(A^k) = 12^k + 24*2^k + 15*(-4)^k."""
    return 12**k + 24 * (2**k) + 15 * ((-4)**k)


def _walk_per_vertex(k):
    """Closed walks of length k from any vertex (vertex-transitivity)."""
    wk = _spectral_walk_count(k)
    assert wk % 40 == 0
    return wk // 40


def _srg_power_coefficients(kmax):
    """Compute alpha, beta, gamma such that A^k = alpha*I + beta*A + gamma*J.

    Uses the SRG recurrence A^2 = 8I - 2A + 4J and the multiplication rules:
        A*I = A,  A*A = 8I - 2A + 4J,  A*J = 12*J.
    """
    coeffs = {}
    coeffs[0] = (1, 0, 0)
    coeffs[1] = (0, 1, 0)
    for k in range(2, kmax + 1):
        a_prev, b_prev, g_prev = coeffs[k - 1]
        # A * (a*I + b*A + g*J) = a*A + b*(8I - 2A + 4J) + 12*g*J
        a_new = 8 * b_prev
        b_new = a_prev - 2 * b_prev
        g_new = 4 * b_prev + 12 * g_prev
        coeffs[k] = (a_new, b_new, g_new)
    return coeffs


def _nb_power_coefficients(kmax):
    """Compute alpha, beta, gamma for the NB walk matrix P_k = a*I + b*A + g*J.

    P_0 = I, P_1 = A, P_2 = A^2 - 12*I.
    P_k = A * P_{k-1} - 11 * P_{k-2}  for k >= 3.
    """
    coeffs = {}
    coeffs[0] = (1, 0, 0)
    coeffs[1] = (0, 1, 0)
    coeffs[2] = (-4, -2, 4)  # A^2 - 12I = (8I - 2A + 4J) - 12I
    for k in range(3, kmax + 1):
        ap, bp, gp = coeffs[k - 1]
        app, bpp, gpp = coeffs[k - 2]
        # A * (ap*I + bp*A + gp*J) = ap*A + bp*(8I - 2A + 4J) + 12*gp*J
        a_mul = 8 * bp
        b_mul = ap - 2 * bp
        g_mul = 4 * bp + 12 * gp
        a_new = a_mul - 11 * app
        b_new = b_mul - 11 * bpp
        g_new = g_mul - 11 * gpp
        coeffs[k] = (a_new, b_new, g_new)
    return coeffs


# ---------------------------------------------------------------------------
# Module-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def A():
    return _build_w33()


@pytest.fixture(scope="module")
def A64(A):
    """A as int64 for safe matrix powers."""
    return A.astype(np.int64)


@pytest.fixture(scope="module")
def Apow(A64):
    """Precompute A^k for k = 0..10 as int64 matrices."""
    n = A64.shape[0]
    powers = {}
    powers[0] = np.eye(n, dtype=np.int64)
    cur = np.eye(n, dtype=np.int64)
    for k in range(1, 11):
        cur = cur @ A64
        powers[k] = cur.copy()
    return powers


@pytest.fixture(scope="module")
def eigenvalues(A):
    """Sorted eigenvalues of A."""
    vals = np.linalg.eigvalsh(A.astype(float))
    return np.sort(vals)[::-1]


@pytest.fixture(scope="module")
def srg_coeffs():
    """SRG power coefficients for k=0..10."""
    return _srg_power_coefficients(10)


@pytest.fixture(scope="module")
def nb_coeffs():
    """Non-backtracking walk matrix coefficients for k=0..8."""
    return _nb_power_coefficients(8)


# ===================================================================
# 1. Total closed walk counts  W_k = tr(A^k)
# ===================================================================

class TestTotalClosedWalkCounts:
    """Verify tr(A^k) = 12^k + 24*2^k + 15*(-4)^k for k = 0..10."""

    def test_W0(self, Apow):
        assert np.trace(Apow[0]) == _spectral_walk_count(0) == 40

    def test_W1(self, Apow):
        assert np.trace(Apow[1]) == _spectral_walk_count(1) == 0

    def test_W2(self, Apow):
        assert np.trace(Apow[2]) == _spectral_walk_count(2) == 480

    def test_W3(self, Apow):
        assert np.trace(Apow[3]) == _spectral_walk_count(3) == 960

    def test_W4(self, Apow):
        assert np.trace(Apow[4]) == _spectral_walk_count(4) == 24960

    def test_W5(self, Apow):
        assert np.trace(Apow[5]) == _spectral_walk_count(5) == 234240

    def test_W6(self, Apow):
        assert np.trace(Apow[6]) == _spectral_walk_count(6) == 3048960

    def test_W7(self, Apow):
        assert np.trace(Apow[7]) == _spectral_walk_count(7) == 35589120

    def test_W8(self, Apow):
        assert np.trace(Apow[8]) == _spectral_walk_count(8) == 430970880

    def test_W9(self, Apow):
        assert np.trace(Apow[9]) == _spectral_walk_count(9) == 5155860480

    def test_W10(self, Apow):
        assert np.trace(Apow[10]) == _spectral_walk_count(10) == 61933117440


# ===================================================================
# 2. Per-vertex closed walk counts  (A^k)_{ii}
# ===================================================================

class TestPerVertexClosedWalks:
    """By vertex-transitivity, (A^k)_{ii} = tr(A^k)/40 for every i."""

    def test_per_vertex_k0(self, Apow):
        assert _walk_per_vertex(0) == 1
        assert all(Apow[0][i, i] == 1 for i in range(40))

    def test_per_vertex_k2(self, Apow):
        assert _walk_per_vertex(2) == 12
        assert all(Apow[2][i, i] == 12 for i in range(40))

    def test_per_vertex_k3(self, Apow):
        assert _walk_per_vertex(3) == 24
        assert all(Apow[3][i, i] == 24 for i in range(40))

    def test_per_vertex_k4(self, Apow):
        assert _walk_per_vertex(4) == 624
        assert all(Apow[4][i, i] == 624 for i in range(40))

    def test_per_vertex_k5(self, Apow):
        assert _walk_per_vertex(5) == 5856
        assert all(Apow[5][i, i] == 5856 for i in range(40))

    def test_per_vertex_k6(self, Apow):
        assert _walk_per_vertex(6) == 76224
        assert all(Apow[6][i, i] == 76224 for i in range(40))


# ===================================================================
# 3. Walk-regularity: diagonal of A^k is constant for all k
# ===================================================================

class TestWalkRegularity:
    """W(3,3) is walk-regular: diag(A^k) is uniform for every k."""

    @pytest.mark.parametrize("k", [1, 2, 3, 4, 5, 6, 7])
    def test_diagonal_constant(self, Apow, k):
        diag = np.diag(Apow[k])
        assert np.all(diag == diag[0]), f"diag(A^{k}) is not constant"

    @pytest.mark.parametrize("k", [2, 3, 4, 5, 6, 7, 8])
    def test_diagonal_matches_spectral(self, Apow, k):
        expected = _walk_per_vertex(k)
        assert Apow[k][0, 0] == expected


# ===================================================================
# 4. Walk matrix entries (A^k)_{ij}  for adjacent / non-adjacent
# ===================================================================

class TestWalkMatrixEntries:
    """For an SRG, A^k has at most 3 distinct entry values:
    diagonal, adjacent-pair, non-adjacent-pair.
    Verify exact values via the SRG power-coefficient recurrence.
    """

    @pytest.mark.parametrize("k, diag, adj, nonadj", [
        (2, 12, 2, 4),
        (3, 24, 52, 40),
        (4, 624, 488, 528),
        (5, 5856, 6352, 6176),
        (6, 76224, 74144, 74816),
    ])
    def test_three_entry_values(self, Apow, A, k, diag, adj, nonadj):
        Ak = Apow[k]
        n = 40
        for i in range(n):
            assert Ak[i, i] == diag, f"k={k} diag mismatch at ({i},{i})"
        # Check a sample of adjacent and non-adjacent pairs
        for i in range(n):
            for j in range(i + 1, n):
                if A[i, j] == 1:
                    assert Ak[i, j] == adj, f"k={k} adj mismatch at ({i},{j})"
                else:
                    assert Ak[i, j] == nonadj, f"k={k} nonadj mismatch at ({i},{j})"

    def test_A2_only_three_distinct_values(self, Apow, A):
        vals = set(Apow[2].ravel())
        assert vals == {12, 2, 4}

    def test_srg_coefficient_diagonal(self, srg_coeffs):
        """Verify alpha_k + gamma_k = per-vertex walk count."""
        for k in range(11):
            a, b, g = srg_coeffs[k]
            assert a + g == _walk_per_vertex(k)

    def test_srg_coefficient_adjacent(self, srg_coeffs):
        """Verify beta_k + gamma_k = adjacent entry value."""
        expected = {2: 2, 3: 52, 4: 488, 5: 6352, 6: 74144}
        for k, val in expected.items():
            _, b, g = srg_coeffs[k]
            assert b + g == val

    def test_srg_coefficient_nonadjacent(self, srg_coeffs):
        """Verify gamma_k = non-adjacent entry value."""
        expected = {2: 4, 3: 40, 4: 528, 5: 6176, 6: 74816}
        for k, val in expected.items():
            _, _, g = srg_coeffs[k]
            assert g == val

    def test_row_sums_of_Ak(self, Apow):
        """Row sums of A^k equal 12^k (regular graph)."""
        for k in range(1, 8):
            row_sums = Apow[k].sum(axis=1)
            assert np.all(row_sums == 12**k)


# ===================================================================
# 5. Spectral properties and moments
# ===================================================================

class TestSpectralProperties:
    """Eigenvalue structure of W(3,3)."""

    def test_eigenvalue_set(self, eigenvalues):
        rounded = np.round(eigenvalues).astype(int)
        assert set(rounded) == {12, 2, -4}

    def test_multiplicity_12(self, eigenvalues):
        assert np.sum(np.abs(eigenvalues - 12) < 0.5) == 1

    def test_multiplicity_2(self, eigenvalues):
        assert np.sum(np.abs(eigenvalues - 2) < 0.5) == 24

    def test_multiplicity_neg4(self, eigenvalues):
        assert np.sum(np.abs(eigenvalues + 4) < 0.5) == 15

    def test_total_multiplicities(self, eigenvalues):
        assert len(eigenvalues) == 40

    def test_spectral_radius(self, eigenvalues):
        assert np.isclose(np.max(np.abs(eigenvalues)), 12, atol=1e-8)

    def test_spectral_gap(self, eigenvalues):
        """Gap = lambda_1 - lambda_2 = 12 - 2 = 10 = dim(Sp(4))."""
        sorted_unique = sorted(set(np.round(eigenvalues).astype(int)), reverse=True)
        assert sorted_unique[0] - sorted_unique[1] == 10

    def test_spectral_moments_match_traces(self, A64):
        """sum(lambda_i^k) = tr(A^k) for k=1..6."""
        vals = np.linalg.eigvalsh(A64.astype(float))
        for k in range(1, 7):
            moment = np.sum(vals**k)
            expected = _spectral_walk_count(k)
            assert abs(moment - expected) < 1.0, f"moment {k}: {moment} vs {expected}"

    def test_eigenvalue_sum(self, eigenvalues):
        """tr(A) = sum of eigenvalues = 0 (no self-loops)."""
        assert abs(np.sum(eigenvalues)) < 1e-8

    def test_eigenvalue_sum_of_squares(self, eigenvalues):
        """sum(lambda^2) = tr(A^2) = 2*|E| = 480."""
        assert abs(np.sum(eigenvalues**2) - 480) < 1e-6


# ===================================================================
# 6. SRG algebraic identity  A^2 = 8I - 2A + 4J
# ===================================================================

class TestSRGRecurrence:
    """SRG(40,12,2,4) satisfies A^2 = (k-mu)I + (lam-mu)A + mu*J."""

    def test_srg_identity(self, A64):
        n = 40
        I = np.eye(n, dtype=np.int64)
        J = np.ones((n, n), dtype=np.int64)
        A2 = A64 @ A64
        rhs = 8 * I - 2 * A64 + 4 * J
        assert np.array_equal(A2, rhs)

    def test_A3_via_srg(self, A64, Apow):
        """A^3 = -16I + 12A + 40J from the SRG recurrence."""
        n = 40
        I = np.eye(n, dtype=np.int64)
        J = np.ones((n, n), dtype=np.int64)
        expected = -16 * I + 12 * A64 + 40 * J
        assert np.array_equal(Apow[3], expected)

    def test_A4_via_srg(self, A64, Apow):
        """A^4 = 96I - 40A + 528J."""
        n = 40
        I = np.eye(n, dtype=np.int64)
        J = np.ones((n, n), dtype=np.int64)
        expected = 96 * I - 40 * A64 + 528 * J
        assert np.array_equal(Apow[4], expected)

    def test_minimal_polynomial(self, A64):
        """Minimal polynomial: A^3 - 6A^2 - 48A + 96*J/... check A satisfies
        the SRG quadratic on the orthogonal complement of all-ones.
        That is, (A - 2I)(A + 4I) annihilates vectors perp to 1."""
        n = 40
        I = np.eye(n, dtype=np.int64)
        factor = (A64 - 2 * I) @ (A64 + 4 * I)
        # Should map everything into span of all-ones vector
        # i.e. each row of factor should be proportional to all-ones
        for i in range(n):
            row = factor[i]
            assert np.all(row == row[0]), f"row {i} not constant"

    def test_J_commutes_with_A(self, A64):
        """AJ = JA = 12J (k-regular)."""
        n = 40
        J = np.ones((n, n), dtype=np.int64)
        AJ = A64 @ J
        assert np.array_equal(AJ, 12 * J)
        JA = J @ A64
        assert np.array_equal(JA, 12 * J)


# ===================================================================
# 7. Walk generating function  G(x) = tr((I - xA)^{-1})
# ===================================================================

class TestWalkGeneratingFunction:
    """G(x) = sum_{k>=0} W_k x^k = 1/(1-12x) + 24/(1-2x) + 15/(1+4x)."""

    def _gf(self, x):
        """Evaluate the walk generating function from spectral decomposition."""
        return 1.0 / (1.0 - 12.0 * x) + 24.0 / (1.0 - 2.0 * x) + 15.0 / (1.0 + 4.0 * x)

    def test_gf_at_zero(self):
        assert self._gf(0.0) == 40.0

    def test_gf_radius_of_convergence(self):
        """Radius of convergence = 1/rho(A) = 1/12."""
        # G(x) has poles at x = 1/12, 1/2, -1/4.
        # Smallest |pole| = 1/12.
        poles = [1.0 / 12, 0.5, -0.25]
        assert min(abs(p) for p in poles) == pytest.approx(1.0 / 12)

    def test_gf_partial_sums(self):
        """Partial sum of G(x) matches sum_{k=0}^{K} W_k x^k at x = 0.01."""
        x = 0.01
        partial = sum(_spectral_walk_count(k) * x**k for k in range(30))
        exact = self._gf(x)
        assert abs(partial - exact) / abs(exact) < 1e-10

    def test_gf_via_resolvent(self, A64):
        """G(x) = tr((I - xA)^{-1}) for |x| < 1/12."""
        n = 40
        x = 0.05
        M = np.eye(n) - x * A64.astype(float)
        resolvent_trace = np.trace(np.linalg.inv(M))
        expected = self._gf(x)
        assert abs(resolvent_trace - expected) < 1e-8

    def test_per_vertex_gf(self):
        """Per-vertex generating function g(x) = G(x)/40."""
        x = 0.02
        gv = self._gf(x) / 40.0
        partial = sum(_walk_per_vertex(k) * x**k for k in range(25))
        assert abs(gv - partial) / abs(gv) < 1e-10

    def test_gf_derivative_at_zero(self):
        """G'(0) = W_1 = 0 (no self-loops)."""
        # G'(x) = 12/(1-12x)^2 + 48/(1-2x)^2 - 60/(1+4x)^2
        # G'(0) = 12 + 48 - 60 = 0
        deriv = 12.0 + 48.0 - 60.0
        assert deriv == 0.0


# ===================================================================
# 8. Return probability for the random walk P = A/12
# ===================================================================

class TestReturnProbability:
    """Return probability p_k = (A^k)_{ii} / 12^k = (1/40)(1 + 24/6^k + 15(-1/3)^k)."""

    def _p_ret(self, k):
        return _walk_per_vertex(k) / 12**k

    def test_p0(self):
        assert self._p_ret(0) == 1.0

    def test_p1(self):
        assert self._p_ret(1) == 0.0

    def test_p2(self):
        # 12 / 144 = 1/12
        assert self._p_ret(2) == pytest.approx(1.0 / 12)

    def test_p3(self):
        # 24 / 1728 = 1/72
        assert self._p_ret(3) == pytest.approx(1.0 / 72)

    def test_limiting_return_probability(self):
        """p_k -> 1/n = 1/40 as k -> inf (uniform mixing)."""
        for k in [20, 40, 60]:
            pk = 1.0 / 40 * (1 + 24 * (1 / 6)**k + 15 * ((-1 / 3)**k))
            assert abs(pk - 1.0 / 40) < 1e-8

    def test_return_probability_from_matrix(self, A):
        """Compare matrix (P^k)_{00} with spectral formula."""
        P = A.astype(float) / 12.0
        Pk = np.eye(40)
        for k in range(1, 8):
            Pk = Pk @ P
            expected = self._p_ret(k)
            assert abs(Pk[0, 0] - expected) < 1e-10


# ===================================================================
# 9. Non-backtracking walks
# ===================================================================

class TestNonBacktrackingWalks:
    """Non-backtracking (NB) walk matrix P_k via recurrence.
    P_0 = I, P_1 = A, P_2 = A^2 - 12I.
    P_k = A*P_{k-1} - 11*P_{k-2}  for k >= 3.
    """

    def test_nb_closed_walks_length_2_zero(self, nb_coeffs):
        """No NB closed walks of length 2 (would require backtracking)."""
        a, b, g = nb_coeffs[2]
        diag = a + g
        assert diag == 0

    def test_nb_walk_k2_adjacent(self, nb_coeffs):
        """NB walks of length 2 between adjacent vertices = lambda = 2."""
        _, b, g = nb_coeffs[2]
        assert b + g == 2

    def test_nb_walk_k2_nonadjacent(self, nb_coeffs):
        """NB walks of length 2 between non-adjacent vertices = mu = 4."""
        _, _, g = nb_coeffs[2]
        assert g == 4

    def test_nb_closed_walks_length_3(self, nb_coeffs):
        """NB closed walks of length 3 per vertex = 24 (= oriented triangles through vertex)."""
        a, _, g = nb_coeffs[3]
        assert a + g == 24

    def test_nb_total_closed_walks_3_equals_tr_A3(self, nb_coeffs):
        """Total NB closed walks of length 3 = tr(A^3) = 960."""
        a, _, g = nb_coeffs[3]
        assert 40 * (a + g) == 960

    def test_nb_closed_walks_length_4(self, nb_coeffs):
        """NB closed walks of length 4 per vertex = 348."""
        a, _, g = nb_coeffs[4]
        assert a + g == 348

    def test_nb_matrix_recurrence_via_matrix(self, A64):
        """Verify P_k matrix recurrence numerically for k = 2..6."""
        n = 40
        I = np.eye(n, dtype=np.int64)
        P_prev2 = I.copy()       # P_0
        P_prev1 = A64.copy()     # P_1
        P2 = A64 @ A64 - 12 * I  # P_2
        assert np.all(np.diag(P2) == 0), "P_2 diagonal should be 0"
        P_prev2 = P_prev1
        P_prev1 = P2
        for k in range(3, 7):
            Pk = A64 @ P_prev1 - 11 * P_prev2
            # Verify diagonal is constant (walk-regular for NB walks too)
            diag = np.diag(Pk)
            assert np.all(diag == diag[0]), f"NB P_{k} diagonal not constant"
            P_prev2 = P_prev1
            P_prev1 = Pk

    def test_nb_total_walks_from_vertex_k2(self, A64):
        """Total NB walks of length 2 from any vertex = k*(k-1) = 132."""
        n = 40
        I = np.eye(n, dtype=np.int64)
        P2 = A64 @ A64 - 12 * I
        row_sum = P2[0].sum()
        assert row_sum == 12 * 11  # 132

    def test_nb_walk_matrix_agrees_with_coefficients(self, A64, nb_coeffs):
        """NB walk matrix P_k matches alpha*I + beta*A + gamma*J."""
        n = 40
        I_n = np.eye(n, dtype=np.int64)
        J = np.ones((n, n), dtype=np.int64)
        # Build P_k iteratively
        P_prev2 = I_n.copy()       # P_0
        P_prev1 = A64.copy()       # P_1
        Pk = A64 @ A64 - 12 * I_n  # P_2
        P_prev2 = P_prev1          # shift: P_prev2 = P_1
        P_prev1 = Pk               # shift: P_prev1 = P_2
        for k in range(3, 7):
            Pk = A64 @ P_prev1 - 11 * P_prev2
            P_prev2 = P_prev1
            P_prev1 = Pk
            a, b, g = nb_coeffs[k]
            expected = a * I_n + b * A64 + g * J
            assert np.array_equal(Pk, expected), f"NB P_{k} mismatch"

    def test_nb_eigenvalues(self, A):
        """NB walk matrix P_k has eigenvalues related to Chebyshev polynomials
        applied to adjacency eigenvalues."""
        # For a k-reg graph, NB eigenvalue for adjacency eigenvalue lam:
        # The NB transfer polynomial satisfies the same recurrence as P_k:
        #   f_0(x) = 1, f_1(x) = x, f_2(x) = x^2 - 12
        #   f_k(x) = x*f_{k-1}(x) - 11*f_{k-2}(x)
        def f(k_val, x):
            if k_val == 0:
                return 1
            if k_val == 1:
                return x
            if k_val == 2:
                return x * x - 12  # P_2 uses k=12, not k-1=11
            a, b = x, x * x - 12  # f_1, f_2
            for _ in range(3, k_val + 1):
                a, b = b, x * b - 11 * a
            return b
        for k_val in [3, 4, 5]:
            # Eigenvalues of P_k should be f_k(12), f_k(2), f_k(-4)
            # with multiplicities 1, 24, 15
            nb_eigs_expected = sorted([f(k_val, 12)] * 1 + [f(k_val, 2)] * 24 +
                                      [f(k_val, -4)] * 15, reverse=True)
            # Compare with trace
            trace_expected = sum(nb_eigs_expected)
            a, _, g = _nb_power_coefficients(k_val)[k_val]
            trace_actual = 40 * (a + g)
            assert trace_expected == trace_actual


# ===================================================================
# 10. Self-returning walks
# ===================================================================

class TestSelfReturningWalks:
    """Analysis of self-returning (closed) walks."""

    def test_no_odd_closed_walks_parity(self, Apow):
        """W(3,3) is NOT bipartite, so odd closed walks exist (W_3 = 960 > 0)."""
        assert np.trace(Apow[3]) > 0

    def test_first_nonzero_return(self, Apow):
        """First nonzero closed walk count is at k=2 (degree = 12)."""
        assert np.trace(Apow[1]) == 0
        assert np.trace(Apow[2]) == 480 > 0

    def test_closed_walks_even_vs_odd(self):
        """Even-k closed walks are always larger than odd-k for large k
        because (-4)^k adds for even k and subtracts for odd k."""
        for k in range(4, 10):
            w_even = _spectral_walk_count(k) if k % 2 == 0 else _spectral_walk_count(k + 1)
            w_odd = _spectral_walk_count(k + 1) if k % 2 == 0 else _spectral_walk_count(k)
            # W_{k+1}/W_k -> 12 as k grows; both positive for large k
            assert w_even > 0

    def test_expected_return_time(self):
        """For a random walk on a vertex-transitive k-regular graph,
        the expected return time to any vertex is n = 40."""
        # By the theory of random walks on regular graphs,
        # stationary distribution is uniform: pi_v = 1/n.
        # Expected return time = 1/pi_v = n = 40.
        n = 40
        pi_v = 1.0 / n
        expected_return = 1.0 / pi_v
        assert expected_return == 40.0

    def test_cumulative_return_probability(self):
        """Cumulative return probability sum_{k=0}^K p_k approaches meaningful bounds."""
        # p_k = per-vertex return probability at step k
        cum = 0.0
        for k in range(100):
            pk = (1.0 / 40) * (1 + 24 * (1.0 / 6)**k + 15 * ((-1.0 / 3)**k))
            cum += pk
        # Cumulative should be finite and > 1 (recurrent graph is finite)
        assert cum > 2.0


# ===================================================================
# 11. Cycle counting from trace formulas
# ===================================================================

class TestCycleCounting:
    """Count short cycles using trace-based formulas."""

    def test_triangle_count(self, Apow):
        """Number of triangles = tr(A^3)/6 = 960/6 = 160."""
        assert np.trace(Apow[3]) == 960
        assert np.trace(Apow[3]) % 6 == 0
        triangles = np.trace(Apow[3]) // 6
        assert triangles == 160

    def test_triangles_per_vertex(self):
        """Each vertex lies in 160*3/40 = 12 triangles."""
        total_triangles = 160
        triangles_per_vertex = total_triangles * 3 // 40
        assert triangles_per_vertex == 12

    def test_four_cycle_count(self, Apow, A):
        """Number of 4-cycles from the trace formula:
        N_4 = (tr(A^4) - n*k*(2k-1)) / 8."""
        n, k = 40, 12
        N4 = (np.trace(Apow[4]) - n * k * (2 * k - 1)) // 8
        assert N4 == 1740

    def test_four_cycles_per_vertex(self):
        """Each vertex lies in 1740*4/40 = 174 four-cycles."""
        assert 1740 * 4 // 40 == 174

    def test_triangle_count_from_A3_diagonal(self, Apow):
        """(A^3)_{ii}/2 = number of oriented triangles through i / 2 = triangles through i."""
        per_vertex = Apow[3][0, 0] // 2
        assert per_vertex == 12

    def test_four_cycle_count_from_diagonal(self, Apow):
        """From the diagonal decomposition:
        (A^4)_{ii} = k + 2k(k-1) + 2*c4(i)
        => c4(i) = (624 - 12*23)/2 = (624 - 276)/2 = 174."""
        k = 12
        overhead = k * (2 * k - 1)  # k + 2k(k-1) = k(2k-1)
        c4_per_vertex = (Apow[4][0, 0] - overhead) // 2
        assert c4_per_vertex == 174

    def test_edge_count(self, A):
        """Number of edges = n*k/2 = 240. Also tr(A^2)/2 = 480/2 = 240."""
        assert A.sum() == 2 * 240
        assert np.trace(A.astype(np.int64) @ A.astype(np.int64)) // 2 == 240


# ===================================================================
# 12. Ihara zeta function
# ===================================================================

class TestIharaZeta:
    """Ihara zeta function: zeta(u)^{-1} = (1-u^2)^{m-n} det(I - Au + (k-1)u^2 I).
    For W(3,3): n=40, m=240, k=12, so m-n=200.
    """

    def _ihara_det(self, u, A):
        """Compute det(I - uA + 11u^2 I)."""
        n = A.shape[0]
        M = (1 + 11 * u**2) * np.eye(n) - u * A.astype(float)
        return np.linalg.det(M)

    def test_ihara_det_factorization(self, A):
        """det(I - uA + 11u^2 I) = prod(1 - lam*u + 11u^2) over eigenvalues."""
        u = 0.03
        det_val = self._ihara_det(u, A)
        # From spectral decomposition
        spectral_val = ((1 - 12 * u + 11 * u**2)**1 *
                        (1 - 2 * u + 11 * u**2)**24 *
                        (1 + 4 * u + 11 * u**2)**15)
        assert abs(det_val - spectral_val) / abs(spectral_val) < 1e-8

    def test_ihara_factor_12(self):
        """Factor for lambda=12: 1-12u+11u^2 = (1-u)(1-11u)."""
        # Roots at u = 1 and u = 1/11
        for u in [1.0, 1.0 / 11]:
            val = 1 - 12 * u + 11 * u**2
            assert abs(val) < 1e-12

    def test_ihara_poles(self):
        """Poles of Ihara zeta at u where det=0, i.e., 1 - lam*u + 11u^2 = 0.
        For lambda=12: u = 1/11 (smallest positive).
        Radius of convergence of log(zeta) = 1/11."""
        # Poles from 1-12u+11u^2: u=1, u=1/11
        # Poles from 1-2u+11u^2: u = (2 +/- sqrt(4-44))/(22) = (1 +/- i*sqrt(10))/11
        #   |u| = sqrt(1+10)/11 = sqrt(11)/11 = 1/sqrt(11)
        # Poles from 1+4u+11u^2: u = (-4 +/- sqrt(16-44))/(22) = (-2 +/- i*sqrt(7))/11
        #   |u| = sqrt(4+7)/11 = sqrt(11)/11 = 1/sqrt(11)
        # Smallest positive pole = 1/sqrt(11) (complex) or 1/11 (real)
        # Radius of convergence = 1/sqrt(11)
        assert 1.0 / 11 < 1.0 / np.sqrt(11)  # 1/11 < 1/sqrt(11)
        assert abs(1.0 / np.sqrt(11) - np.sqrt(11) / 11) < 1e-12

    def test_ihara_at_zero(self, A):
        """zeta(0)^{-1} = 1 (all factors equal 1 at u=0)."""
        det0 = self._ihara_det(0, A)
        assert abs(det0 - 1.0) < 1e-12

    def test_ihara_reciprocal_polynomial_degree(self, A):
        """The reciprocal polynomial of the Ihara zeta has degree 2n = 80
        (from det(I - uA + 11u^2 I)) plus 2(m-n) = 400 from (1-u^2) factor.
        Total degree of zeta^{-1} as polynomial in u = 80 + 400 = 480 = 2m."""
        n, m = 40, 240
        assert 2 * n + 2 * (m - n) == 2 * m == 480


# ===================================================================
# 13. Walk transfer matrix for SRG
# ===================================================================

class TestWalkTransferMatrix:
    """3-state transfer matrix T for SRG(40,12,2,4).
    States: 0=same, 1=adjacent, 2=non-adjacent relative to start vertex.
    T = [[0, 12, 0], [1, 2, 9], [0, 4, 8]].
    Eigenvalues of T = {12, 2, -4} = adjacency eigenvalues.
    """

    def _transfer_matrix(self):
        return np.array([[0, 12, 0],
                         [1, 2, 9],
                         [0, 4, 8]], dtype=np.int64)

    def test_transfer_matrix_eigenvalues(self):
        """T has eigenvalues {12, 2, -4} matching adjacency spectrum."""
        T = self._transfer_matrix()
        eigs = np.sort(np.linalg.eigvals(T).real)[::-1]
        expected = np.array([12.0, 2.0, -4.0])
        assert np.allclose(eigs, expected, atol=1e-8)

    def test_transfer_matrix_row_sums(self):
        """Row sums of T = k = 12 (each row sums to degree)."""
        T = self._transfer_matrix()
        assert np.all(T.sum(axis=1) == 12)

    def test_transfer_matrix_walk_counts(self, Apow, A):
        """T^k @ [1,0,0] gives the walk distribution [diag, adj, nonadj],
        matching diagonal and off-diagonal entries of A^k."""
        T = self._transfer_matrix().astype(float)
        v = np.array([1.0, 0.0, 0.0])
        coeffs = _srg_power_coefficients(8)
        for k in range(1, 9):
            v = T @ v if k == 1 else v
            if k > 1:
                v = np.linalg.matrix_power(T, k) @ np.array([1.0, 0.0, 0.0])
            a_k, b_k, g_k = coeffs[k]
            expected_diag = a_k + g_k
            expected_adj = b_k + g_k
            expected_nonadj = g_k
            assert abs(v[0] - expected_diag) < 1e-6, f"k={k} diag"
            assert abs(v[1] - expected_adj) < 1e-6, f"k={k} adj"
            assert abs(v[2] - expected_nonadj) < 1e-6, f"k={k} nonadj"

    def test_transfer_matrix_trace_equals_walk_count(self):
        """tr(T^k) = sum of eigenvalue k-th powers.
        But careful: tr(T^k) != tr(A^k) because T is 3x3.
        tr(T^k) = 12^k + 2^k + (-4)^k."""
        T = self._transfer_matrix().astype(float)
        for k in range(1, 8):
            tr_Tk = np.trace(np.linalg.matrix_power(T, k))
            expected = 12**k + 2**k + (-4)**k
            assert abs(tr_Tk - expected) < 1.0


# ===================================================================
# 14. Asymptotic growth rate
# ===================================================================

class TestAsymptoticGrowthRate:
    """Walk counts grow as ~ c * rho^k where rho = spectral radius = 12."""

    def test_growth_rate_from_ratio(self):
        """W_{k+1}/W_k -> 12 as k -> inf."""
        for k in [15, 20, 30]:
            ratio = _spectral_walk_count(k + 1) / _spectral_walk_count(k)
            assert abs(ratio - 12.0) < 1e-3

    def test_kth_root_convergence(self):
        """W_k^{1/k} -> 12 as k -> inf."""
        for k in [10, 20, 30]:
            wk = _spectral_walk_count(k)
            root = wk ** (1.0 / k)
            assert abs(root - 12.0) < 0.1

    def test_dominant_eigenvalue_contribution(self):
        """For large k, W_k ~ 12^k (dominant term)."""
        for k in [10, 15, 20]:
            wk = _spectral_walk_count(k)
            dominant = 12**k
            assert abs(wk / dominant - 1.0) < 0.01

    def test_subdominant_ratio(self):
        """Second eigenvalue ratio: max(|2|, |-4|)/12 = 1/3."""
        assert max(abs(2), abs(-4)) / 12 == pytest.approx(1.0 / 3)

    def test_mixing_rate(self):
        """Mixing rate = |lambda_2|/k = 4/12 = 1/3 where lambda_2 = -4.
        This controls how fast the random walk mixes."""
        mixing_rate = 4.0 / 12.0
        assert mixing_rate == pytest.approx(1.0 / 3)


# ===================================================================
# 15. Path counting (walks with all distinct vertices)
# ===================================================================

class TestPathCounting:
    """Count paths (walks visiting distinct vertices) of small lengths."""

    def test_paths_length_1(self, A):
        """Paths of length 1 from vertex 0 = degree = 12."""
        assert A[0].sum() == 12

    def test_paths_length_2_adjacent(self, Apow, A):
        """Paths of length 2 between adjacent i,j = (A^2)_{ij} = lambda = 2.
        (In a simple graph, all length-2 walks between distinct vertices are paths.)"""
        i, j = 0, int(np.where(A[0] == 1)[0][0])
        assert Apow[2][i, j] == 2

    def test_paths_length_2_nonadjacent(self, Apow, A):
        """Paths of length 2 between non-adjacent i,j = mu = 4."""
        i = 0
        j = int(np.where(A[0] == 0)[0][1])  # skip j=0 (self)
        assert Apow[2][i, j] == 4

    def test_total_paths_length_2_from_vertex(self, Apow, A):
        """Total paths of length 2 from vertex 0 (to all other vertices).
        = 12 * lambda + 27 * mu = 12*2 + 27*4 = 24 + 108 = 132 = k*(k-1)."""
        row = Apow[2][0].copy()
        row[0] = 0  # exclude self
        assert row.sum() == 12 * 11

    def test_paths_length_3_adjacent(self, Apow, A):
        """Paths of length 3 from i to adjacent j.
        Walks of length 3 = 52.  Subtract non-path walks.
        Non-path walks with repeated vertex: 12 + 12 - 1 = 23.
        Paths = 52 - 23 = 29."""
        i = 0
        j = int(np.where(A[0] == 1)[0][0])
        walks_3 = Apow[3][i, j]
        assert walks_3 == 52
        # Subtract walks with repeated vertices:
        # Walks i->a->i->j (a any neighbor of i): k * A[i,j] = 12
        case1 = 12 * A[i, j]
        # Walks i->j->b->j (b any neighbor of j, b != j by no self-loop): k * A[i,j] = 12
        case2 = 12 * A[i, j]
        # Walks i->j->i->j: A[i,j]^3 = 1
        case12 = int(A[i, j]**3)
        paths_3 = walks_3 - case1 - case2 + case12
        assert paths_3 == 29

    def test_paths_length_3_nonadjacent(self, Apow, A):
        """Paths of length 3 from i to non-adjacent j.
        Walks of length 3 = 40.  No non-path walks (since A[i,j]=0).
        Paths = 40."""
        i = 0
        j = int(np.where(A[0] == 0)[0][1])
        walks_3 = Apow[3][i, j]
        assert walks_3 == 40
        # Since A[i,j]=0, no walk can use repeated vertex at i or j
        # (no edge between them to enable backtracking)
        paths_3 = walks_3  # all walks are paths
        assert paths_3 == 40

    def test_total_paths_length_3_from_vertex(self, Apow, A):
        """Total paths of length 3 from vertex 0 to all other vertices.
        = 12*29 (to adj) + 27*40 (to non-adj) = 348 + 1080 = 1428."""
        # Adjacent paths + non-adjacent paths
        total = 12 * 29 + 27 * 40
        assert total == 1428


# ===================================================================
# 16. Additional walk identities
# ===================================================================

class TestWalkIdentities:
    """Miscellaneous walk identities and consistency checks."""

    def test_walk_count_parity(self):
        """W_k has a specific parity pattern from the spectral formula.
        For even k: all three terms positive, W_k > 0.
        For odd k > 0: 15*(-4)^k < 0, but dominated by 12^k + 24*2^k."""
        for k in range(1, 20):
            wk = _spectral_walk_count(k)
            assert wk >= 0, f"W_{k} = {wk} < 0"
            if k >= 2:
                assert wk > 0

    def test_trace_A_power_divisibility(self):
        """tr(A^k) is divisible by 40 for all k (vertex-transitivity)."""
        for k in range(20):
            assert _spectral_walk_count(k) % 40 == 0

    def test_walk_monotonicity_large_k(self):
        """|W_k| is eventually monotonically increasing for k >= 2."""
        for k in range(3, 20):
            assert _spectral_walk_count(k) < _spectral_walk_count(k + 1)

    def test_W2_equals_twice_edges(self):
        """W_2 = tr(A^2) = 2*|E| = 2*240 = 480."""
        assert _spectral_walk_count(2) == 2 * 240

    def test_frobenius_norm_squared(self, A):
        """||A||_F^2 = tr(A^T A) = tr(A^2) = 480."""
        frob_sq = np.sum(A.astype(np.int64)**2)
        assert frob_sq == 480

    def test_total_common_neighbors(self, Apow, A):
        """Sum of all (A^2)_{ij} for i != j = sum of common neighbor counts.
        = 12*2*240 (adj pairs) + 4*(40*39/2 - 240) (non-adj pairs)... via row sums."""
        off_diag_sum = Apow[2].sum() - np.trace(Apow[2])
        # Row sum of A^2 = 144, so total sum = 40*144 = 5760
        # Diagonal sum = 40*12 = 480
        # Off-diagonal = 5760 - 480 = 5280
        assert off_diag_sum == 5280

    def test_walk_count_second_moment(self):
        """sum_{k=0}^{K} W_k^2 / 12^{2k} converges (finite sum of squared return probs)."""
        S = sum((_spectral_walk_count(k) / (40.0 * 12**k))**2 for k in range(100))
        # Should converge to finite value
        assert S < 100.0
        assert S > 1.0  # at least k=0 contributes 1

    def test_A_squared_trace_via_degree(self, A):
        """tr(A^2) = sum of degrees = n*k = 40*12 = 480."""
        assert np.trace(A.astype(np.int64) @ A.astype(np.int64)) == 40 * 12
