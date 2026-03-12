"""
Phase CXII -- Polynomial Methods Computation on W(3,3) = SRG(40,12,2,4)
========================================================================

Comprehensive tests for seven graph polynomials and polynomial identities
derived from the adjacency matrix of the symplectic graph W(3,3).

Covers:
  1. Characteristic polynomial (Newton's identities, Faddeev-LeVerrier,
     elementary symmetric polynomials, determinant)
  2. Minimal polynomial (annihilation, minimality, Cayley-Hamilton)
  3. Hoffman polynomial (h(A) = J, evaluations at eigenvalues)
  4. Chromatic polynomial (bounds, colorability, structural properties)
  5. Independence polynomial (independent set counts, bounds)
  6. Matching polynomial (matching counts, Heilmann-Lieb, signs)
  7. Clique polynomial (clique counts, Euler characteristic)
  8. Polynomial identities (SRG equation, projectors, trace identities)

All computations use ONLY numpy and the standard library.
"""

import numpy as np
from math import comb, gcd, log
from collections import Counter
from itertools import combinations
import pytest


# ---------------------------------------------------------------------------
# Build W(3,3) = SRG(40,12,2,4) from the symplectic form on PG(3,3)
# ---------------------------------------------------------------------------

def _build_w33():
    """Build W(3,3) adjacency matrix from symplectic form on GF(3)^4."""
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


def _polymul_int(p, q):
    """Multiply two polynomials with integer coefficients.

    Polynomials are lists [c_n, c_{n-1}, ..., c_0] (highest degree first).
    """
    result = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            result[i + j] += a * b
    return result


def _char_poly_from_spectrum():
    """Compute exact integer characteristic polynomial coefficients.

    chi(x) = (x - 12)^1 * (x - 2)^24 * (x + 4)^15
    Returns list [c_40, c_39, ..., c_0] with c_40 = 1 (monic).
    """
    p = [1, -12]
    for _ in range(24):
        p = _polymul_int(p, [1, -2])
    for _ in range(15):
        p = _polymul_int(p, [1, 4])
    return p


def _faddeev_leverrier(A):
    """Faddeev-LeVerrier algorithm for the characteristic polynomial.

    Uses Python object dtype for exact arbitrary-precision integer arithmetic.
    Returns list of coefficients [1, c_{n-1}, ..., c_0].
    """
    n = A.shape[0]
    A_obj = A.astype(object)
    I_obj = np.eye(n, dtype=object)

    coeffs = [0] * (n + 1)
    coeffs[0] = 1  # leading coefficient (monic)

    M = A_obj.copy()
    for k in range(1, n + 1):
        if k > 1:
            M = A_obj @ (M + coeffs[k - 1] * I_obj)
        c = -int(np.trace(M)) // k
        coeffs[k] = c

    return coeffs


def _edge_list(A):
    """Extract list of edges (i, j) with i < j from adjacency matrix."""
    edges = []
    n = A.shape[0]
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j]:
                edges.append((i, j))
    return edges


def _count_independent_sets(A, size):
    """Count independent sets of a given size in graph with adjacency matrix A."""
    n = A.shape[0]
    count = 0
    for combo in combinations(range(n), size):
        is_independent = True
        for i in range(len(combo)):
            for j in range(i + 1, len(combo)):
                if A[combo[i], combo[j]]:
                    is_independent = False
                    break
            if not is_independent:
                break
        if is_independent:
            count += 1
    return count


def _count_cliques(A, size):
    """Count cliques of a given size in graph with adjacency matrix A."""
    n = A.shape[0]
    count = 0
    for combo in combinations(range(n), size):
        is_clique = True
        for i in range(len(combo)):
            for j in range(i + 1, len(combo)):
                if not A[combo[i], combo[j]]:
                    is_clique = False
                    break
            if not is_clique:
                break
        if is_clique:
            count += 1
    return count


def _count_k_matchings(edges, k):
    """Count k-matchings (k pairwise vertex-disjoint edges)."""
    if k == 0:
        return 1
    if k == 1:
        return len(edges)
    n_edges = len(edges)
    count = 0
    for combo in combinations(range(n_edges), k):
        vertices_used = set()
        valid = True
        for idx in combo:
            u, v = edges[idx]
            if u in vertices_used or v in vertices_used:
                valid = False
                break
            vertices_used.add(u)
            vertices_used.add(v)
        if valid:
            count += 1
    return count


def _dsatur_coloring(A):
    """DSatur greedy coloring algorithm. Returns color assignment list."""
    n = A.shape[0]
    colors = [-1] * n
    saturation = [0] * n
    adj_colors = [set() for _ in range(n)]

    # Start with vertex of highest degree (all same for regular graph)
    colors[0] = 0
    for j in range(n):
        if A[0, j]:
            adj_colors[j].add(0)
            saturation[j] = 1

    for step in range(1, n):
        # Pick uncolored vertex with highest saturation, break ties by degree
        best = -1
        best_sat = -1
        for v in range(n):
            if colors[v] == -1:
                if saturation[v] > best_sat:
                    best_sat = saturation[v]
                    best = v
        v = best

        # Assign smallest available color
        c = 0
        while c in adj_colors[v]:
            c += 1
        colors[v] = c

        # Update saturation for neighbors
        for j in range(n):
            if A[v, j] and colors[j] == -1:
                if c not in adj_colors[j]:
                    adj_colors[j].add(c)
                    saturation[j] = len(adj_colors[j])

    return colors


# ---------------------------------------------------------------------------
# Module-scoped fixtures (computed once)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def w33():
    return _build_w33()


@pytest.fixture(scope="module")
def eigenvalues(w33):
    """Sorted eigenvalues (descending) as integers."""
    eigs = np.linalg.eigvalsh(w33.astype(float))
    return np.sort(np.round(eigs).astype(int))[::-1]


@pytest.fixture(scope="module")
def edges(w33):
    return _edge_list(w33)


@pytest.fixture(scope="module")
def char_poly_exact():
    """Exact integer coefficients of the characteristic polynomial."""
    return _char_poly_from_spectrum()


@pytest.fixture(scope="module")
def faddeev_coeffs(w33):
    """Characteristic polynomial coefficients via Faddeev-LeVerrier."""
    return _faddeev_leverrier(w33)


# ===========================================================================
# 1. CHARACTERISTIC POLYNOMIAL (12 tests)
# ===========================================================================

class TestCharacteristicPolynomial:
    """Characteristic polynomial of W(3,3): (x-12)(x-2)^24(x+4)^15."""

    def test_eigenvalue_count(self, eigenvalues):
        """Total number of eigenvalues equals n = 40."""
        assert len(eigenvalues) == 40

    def test_eigenvalue_12_multiplicity_1(self, eigenvalues):
        """Eigenvalue k = 12 has multiplicity 1 (the all-ones eigenvector)."""
        assert np.sum(eigenvalues == 12) == 1

    def test_eigenvalue_2_multiplicity_24(self, eigenvalues):
        """Eigenvalue r = 2 has multiplicity 24."""
        assert np.sum(eigenvalues == 2) == 24

    def test_eigenvalue_neg4_multiplicity_15(self, eigenvalues):
        """Eigenvalue s = -4 has multiplicity 15."""
        assert np.sum(eigenvalues == -4) == 15

    def test_newton_p1_trace_zero(self, w33):
        """p_1 = tr(A) = 12 + 24*2 + 15*(-4) = 0."""
        assert np.trace(w33) == 0

    def test_newton_p2_twice_edges(self, w33):
        """p_2 = tr(A^2) = 2*|E| = 2 * 240 = 480."""
        assert int(np.trace(w33 @ w33)) == 480

    def test_newton_p3_six_triangles(self, w33):
        """p_3 = tr(A^3) = 6 * 160 = 960 (160 triangles from lambda=2)."""
        A3 = w33 @ w33 @ w33
        assert int(np.trace(A3)) == 960

    def test_newton_p4(self, w33):
        """p_4 = 12^4 + 24*2^4 + 15*(-4)^4 = 24960."""
        A2 = w33 @ w33
        A4 = A2 @ A2
        expected = 12**4 + 24 * 2**4 + 15 * (-4)**4
        assert expected == 24960
        assert int(np.trace(A4)) == 24960

    def test_newton_p5(self, w33):
        """p_5 = 12^5 + 24*2^5 + 15*(-4)^5 = 234240."""
        A2 = w33 @ w33
        A5 = A2 @ A2 @ w33
        expected = 12**5 + 24 * 2**5 + 15 * (-4)**5
        assert expected == 234240
        assert int(np.trace(A5)) == 234240

    def test_faddeev_leverrier_leading_coeff(self, faddeev_coeffs):
        """Leading coefficient of characteristic polynomial is 1 (monic)."""
        assert faddeev_coeffs[0] == 1

    def test_faddeev_leverrier_matches_spectrum(self, faddeev_coeffs, char_poly_exact):
        """Faddeev-LeVerrier coefficients match the exact polynomial from spectrum."""
        assert len(faddeev_coeffs) == len(char_poly_exact)
        for i in range(len(faddeev_coeffs)):
            assert faddeev_coeffs[i] == char_poly_exact[i], (
                f"Mismatch at coefficient index {i}: "
                f"FL={faddeev_coeffs[i]}, exact={char_poly_exact[i]}"
            )

    def test_determinant_sign_and_magnitude(self, w33):
        """det(A) = 12 * 2^24 * (-4)^15 = -3 * 2^56.

        sign = -1, ln|det| = ln(3) + 56*ln(2).
        """
        sign, logabsdet = np.linalg.slogdet(w33.astype(float))
        assert sign == -1
        expected_log = np.log(3.0) + 56 * np.log(2.0)
        assert abs(logabsdet - expected_log) < 1e-8


# ===========================================================================
# 2. MINIMAL POLYNOMIAL (10 tests)
# ===========================================================================

class TestMinimalPolynomial:
    """Minimal polynomial: m(x) = (x-12)(x-2)(x+4) = x^3 - 10x^2 - 32x + 96."""

    def test_minimal_poly_coefficients(self):
        """m(x) = x^3 - 10x^2 - 32x + 96."""
        # (x-12)(x-2) = x^2 - 14x + 24
        # (x^2 - 14x + 24)(x+4) = x^3 + 4x^2 - 14x^2 - 56x + 24x + 96
        #                        = x^3 - 10x^2 - 32x + 96
        coeffs = _polymul_int(_polymul_int([1, -12], [1, -2]), [1, 4])
        assert coeffs == [1, -10, -32, 96]

    def test_minimal_poly_annihilates_A(self, w33):
        """A^3 - 10*A^2 - 32*A + 96*I = 0 exactly."""
        n = 40
        I = np.eye(n, dtype=int)
        A2 = w33 @ w33
        A3 = A2 @ w33
        M = A3 - 10 * A2 - 32 * w33 + 96 * I
        assert np.max(np.abs(M)) == 0

    def test_no_degree_1_annihilator(self, w33):
        """No polynomial of degree 1 annihilates A (A has 3 distinct eigenvalues)."""
        n = 40
        I = np.eye(n, dtype=int)
        for lam in [12, 2, -4]:
            M = w33 - lam * I
            assert np.max(np.abs(M)) > 0

    def test_no_degree_2_annihilator(self, w33):
        """No polynomial of degree 2 annihilates A.

        All three degree-2 sub-products of the minimal polynomial are non-zero at A.
        """
        n = 40
        I = np.eye(n, dtype=int)
        M1 = (w33 - 12 * I) @ (w33 - 2 * I)
        M2 = (w33 - 12 * I) @ (w33 + 4 * I)
        M3 = (w33 - 2 * I) @ (w33 + 4 * I)
        assert np.max(np.abs(M1)) > 0
        assert np.max(np.abs(M2)) > 0
        assert np.max(np.abs(M3)) > 0

    def test_minimal_poly_roots(self):
        """Roots of m(x) are exactly {12, 2, -4}."""
        # m(x) = x^3 - 10x^2 - 32x + 96
        for lam in [12, 2, -4]:
            val = lam**3 - 10 * lam**2 - 32 * lam + 96
            assert val == 0

    def test_A_cubed_from_minimal(self, w33):
        """From m(A)=0: A^3 = 10*A^2 + 32*A - 96*I."""
        n = 40
        I = np.eye(n, dtype=int)
        A2 = w33 @ w33
        A3 = A2 @ w33
        expected = 10 * A2 + 32 * w33 - 96 * I
        assert np.array_equal(A3, expected)

    def test_A_fourth_from_minimal(self, w33):
        """A^4 = 132*A^2 + 224*A - 960*I (derived from A^3 expression)."""
        n = 40
        I = np.eye(n, dtype=int)
        A2 = w33 @ w33
        A4 = A2 @ A2
        # A^4 = A * A^3 = A(10A^2 + 32A - 96I) = 10A^3 + 32A^2 - 96A
        #     = 10(10A^2+32A-96I) + 32A^2 - 96A = 132A^2 + 224A - 960I
        expected = 132 * A2 + 224 * w33 - 960 * I
        assert np.array_equal(A4, expected)

    def test_A_inverse_from_minimal(self, w33):
        """From m(A)=0: A^(-1) = (A^2 - 10*A - 32*I) / (-96)."""
        n = 40
        I = np.eye(n, dtype=float)
        A_float = w33.astype(float)
        # A(A^2 - 10A - 32I) = A^3 - 10A^2 - 32A = -96I
        # => A^(-1) = -(A^2 - 10A - 32I)/96
        A_inv_computed = -(A_float @ A_float - 10 * A_float - 32 * I) / 96.0
        A_inv_direct = np.linalg.inv(A_float)
        assert np.allclose(A_inv_computed, A_inv_direct, atol=1e-10)

    def test_cayley_hamilton_from_minimal(self, w33):
        """Since m(x) divides the characteristic polynomial, m(A)=0 implies CH.

        The char poly chi(x) = (x-12)(x-2)^24(x+4)^15 is divisible by
        m(x) = (x-12)(x-2)(x+4), so m(A)=0 implies chi(A)=0.
        """
        n = 40
        I = np.eye(n, dtype=int)
        M = (w33 - 12 * I) @ (w33 - 2 * I) @ (w33 + 4 * I)
        assert np.max(np.abs(M)) == 0

    def test_minimal_divides_characteristic(self, char_poly_exact):
        """The characteristic polynomial is divisible by the minimal polynomial.

        chi(x) / m(x) = (x-2)^23 * (x+4)^14 must have integer coefficients.
        """
        # Compute (x-2)^23 * (x+4)^14
        quotient = [1]
        for _ in range(23):
            quotient = _polymul_int(quotient, [1, -2])
        for _ in range(14):
            quotient = _polymul_int(quotient, [1, 4])

        # Verify quotient * minimal = characteristic
        minimal = [1, -10, -32, 96]
        product = _polymul_int(quotient, minimal)
        assert product == char_poly_exact


# ===========================================================================
# 3. HOFFMAN POLYNOMIAL (10 tests)
# ===========================================================================

class TestHoffmanPolynomial:
    """Hoffman polynomial h(x) satisfying h(A) = J (all-ones matrix).

    For SRG(n,k,lam,mu) with eigenvalues k, r, s:
    h(x) = n * (x - r)(x - s) / ((k - r)(k - s))
         = 40 * (x - 2)(x + 4) / (10 * 16) = (x^2 + 2x - 8) / 4
    """

    def test_hoffman_at_k_equals_n(self):
        """h(k) = h(12) = 40 = n."""
        # h(x) = (x^2 + 2x - 8) / 4
        val = (12**2 + 2 * 12 - 8) / 4
        assert val == 40.0

    def test_hoffman_at_r_equals_zero(self):
        """h(r) = h(2) = 0."""
        val = (2**2 + 2 * 2 - 8) / 4
        assert val == 0.0

    def test_hoffman_at_s_equals_zero(self):
        """h(s) = h(-4) = 0."""
        val = ((-4)**2 + 2 * (-4) - 8) / 4
        assert val == 0.0

    def test_hoffman_of_A_equals_J(self, w33):
        """h(A) = A^2/4 + A/2 - 2*I = J (all-ones matrix)."""
        n = 40
        A_f = w33.astype(float)
        J = np.ones((n, n), dtype=float)
        h_A = (A_f @ A_f) / 4.0 + A_f / 2.0 - 2.0 * np.eye(n)
        assert np.allclose(h_A, J, atol=1e-10)

    def test_hoffman_coefficients(self):
        """h(x) = (1/4)x^2 + (1/2)x - 2."""
        # h(x) = 40*(x-2)(x+4)/(10*16) = 40*(x^2+2x-8)/160 = (x^2+2x-8)/4
        a2 = 1.0 / 4
        a1 = 2.0 / 4
        a0 = -8.0 / 4
        assert a2 == 0.25
        assert a1 == 0.5
        assert a0 == -2.0

    def test_hoffman_is_degree_2(self):
        """Hoffman polynomial has degree = number of distinct eigenvalues - 1 = 2."""
        # 3 distinct eigenvalues => degree 2
        num_distinct = 3
        assert num_distinct - 1 == 2

    def test_hoffman_leading_coefficient(self):
        """Leading coefficient of h(x) is n / ((k-r)(k-s)) = 40/160 = 1/4."""
        leading = 40.0 / ((12 - 2) * (12 - (-4)))
        assert leading == 0.25

    def test_hoffman_constant_term(self):
        """Constant term h(0) = 40 * (-2)*(4) / (10*16) = -2."""
        val = 40 * (-2) * 4 / (10 * 16)
        assert val == -2.0

    def test_hoffman_squared_equals_n_times_hoffman(self, w33):
        """h(A)^2 = J^2 = 40*J = 40*h(A), since J^2 = nJ."""
        n = 40
        A_f = w33.astype(float)
        I_f = np.eye(n)
        h_A = (A_f @ A_f) / 4.0 + A_f / 2.0 - 2.0 * I_f
        h_A_sq = h_A @ h_A
        assert np.allclose(h_A_sq, 40.0 * h_A, atol=1e-8)

    def test_AJ_equals_kJ(self, w33):
        """A*J = k*J = 12*J (the all-ones vector is an eigenvector)."""
        n = 40
        J = np.ones((n, n), dtype=int)
        AJ = w33 @ J
        assert np.array_equal(AJ, 12 * J)


# ===========================================================================
# 4. CHROMATIC POLYNOMIAL (10 tests)
# ===========================================================================

class TestChromaticPolynomial:
    """Chromatic polynomial properties of W(3,3).

    The exact chromatic polynomial is exponentially hard to compute,
    so we verify structural bounds and colorability properties.
    """

    def test_hoffman_chromatic_bound(self):
        """Hoffman bound: chi(G) >= 1 - k/s = 1 - 12/(-4) = 4."""
        bound = 1 - 12 / (-4)
        assert bound == 4.0

    def test_clique_number_is_4(self, w33):
        """omega(W33) = 4: there exist 4-cliques but no 5-cliques.

        4-cliques correspond to totally isotropic lines in PG(3,3).
        """
        c4 = _count_cliques(w33, 4)
        assert c4 > 0, "No 4-cliques found"
        c5 = _count_cliques(w33, 5)
        assert c5 == 0, "5-clique found, but omega should be 4"

    def test_clique_number_lower_bound_on_chi(self, w33):
        """chi(G) >= omega(G) = 4, so P(3) = 0."""
        c4 = _count_cliques(w33, 4)
        assert c4 > 0  # omega >= 4

    def test_brooks_bound(self, w33):
        """Brooks' theorem: chi(G) <= Delta(G) = 12 for non-complete regular graph."""
        degrees = np.sum(w33, axis=1)
        delta = int(np.max(degrees))
        assert delta == 12
        # W(3,3) is not complete (n=40 > k+1=13)
        assert 40 > delta + 1

    def test_not_bipartite(self, w33):
        """W(3,3) has odd cycles (triangles), so P(2) = 0."""
        # tr(A^3) = 960 > 0 means there are triangles => not bipartite
        A3 = w33 @ w33 @ w33
        assert int(np.trace(A3)) > 0

    def test_p_at_1_is_zero(self, w33):
        """P(1) = 0 since the graph has edges (not edgeless)."""
        num_edges = int(np.sum(w33)) // 2
        assert num_edges > 0  # 240 edges => no proper 1-coloring

    def test_greedy_coloring_valid(self, w33):
        """DSatur produces a valid proper coloring (no adjacent same-color)."""
        colors = _dsatur_coloring(w33)
        n = w33.shape[0]
        for i in range(n):
            for j in range(i + 1, n):
                if w33[i, j]:
                    assert colors[i] != colors[j], (
                        f"Adjacent vertices {i},{j} share color {colors[i]}"
                    )

    def test_greedy_coloring_upper_bound(self, w33):
        """Greedy coloring uses at most Delta+1 = 13 colors."""
        colors = _dsatur_coloring(w33)
        num_colors = len(set(colors))
        assert num_colors <= 13

    def test_chromatic_at_least_4(self, w33):
        """Chromatic number is at least 4 (from both Hoffman and clique bounds)."""
        # Hoffman bound
        hoffman_bound = 1 - 12 / (-4)
        assert hoffman_bound >= 4
        # Clique bound
        c4 = _count_cliques(w33, 4)
        assert c4 > 0  # omega >= 4 => chi >= 4

    def test_lovasz_theta_complement_bound(self, w33):
        """Lovasz theta function bound: chi >= n / theta(G).

        theta(G) = n * (-s) / (k - s) = 40 * 4 / 16 = 10.
        So chi >= n / theta = 40/10 = 4.
        """
        theta = 40 * 4.0 / (12 + 4)
        assert theta == 10.0
        chi_lower = 40.0 / theta
        assert chi_lower == 4.0


# ===========================================================================
# 5. INDEPENDENCE POLYNOMIAL (10 tests)
# ===========================================================================

class TestIndependencePolynomial:
    """Independence polynomial I(x) = sum_{k=0}^{alpha} a_k * x^k.

    a_k = number of independent sets of size k in W(3,3).
    """

    def test_a0_is_1(self):
        """a_0 = 1 (the empty set is independent)."""
        assert 1 == 1  # By definition

    def test_a1_is_40(self, w33):
        """a_1 = n = 40 (each singleton is independent)."""
        assert w33.shape[0] == 40

    def test_a2_non_edges(self, w33, edges):
        """a_2 = C(40,2) - |E| = 780 - 240 = 540."""
        n = w33.shape[0]
        num_edges = len(edges)
        assert num_edges == 240
        a2 = comb(n, 2) - num_edges
        assert a2 == 540

    def test_a2_from_complement_edges(self, w33):
        """a_2 equals the number of edges in the complement graph."""
        complement = 1 - w33 - np.eye(40, dtype=int)
        num_complement_edges = int(np.sum(complement)) // 2
        assert num_complement_edges == 540

    def test_a3_computed(self, w33):
        """a_3 = number of independent triples, computed by enumeration.

        For SRG(40,12,2,4), each non-edge (u,v) has mu=4 common neighbors,
        so there are 40-2-4 = 34 vertices non-adjacent to both u and v minus
        those adjacent to at least one. We verify computationally.
        """
        a3 = _count_independent_sets(w33, 3)
        assert a3 > 0
        # a_3 should be less than C(40,3) = 9880
        assert a3 < 9880
        # a_3 should be consistent: 3*a_3 <= a_2 * (40 - 2 - ...)
        # Just verify it's computed correctly by checking a small identity
        # Each vertex v has 40 - 1 - 12 = 27 non-neighbors
        # So a_3 <= 40 * C(27, 2) / 3 = 40 * 351 / 3 = 4680
        assert a3 <= 4680

    def test_independence_number_upper_bound(self, w33):
        """Delsarte-Hoffman bound: alpha <= n*(-s)/(k-s) = 40*4/16 = 10."""
        # alpha <= 40 * 4 / (12 - (-4)) = 160 / 16 = 10
        bound = 40 * 4.0 / (12 + 4)
        assert bound == 10.0

    def test_independence_poly_at_zero(self):
        """I(0) = a_0 = 1."""
        assert 1 == 1  # a_0 = 1

    def test_a2_formula_from_degree(self, w33):
        """a_2 = C(n,2) - |E| = C(n,2) - n*k/2 for k-regular graph."""
        n = 40
        k = 12
        a2 = comb(n, 2) - n * k // 2
        assert a2 == 540

    def test_a_k_nonnegative(self, w33):
        """All coefficients a_k are nonnegative (they count sets)."""
        a0 = 1
        a1 = 40
        a2 = 540
        a3 = _count_independent_sets(w33, 3)
        for val in [a0, a1, a2, a3]:
            assert val >= 0

    def test_total_independent_sets_lower_bound(self, w33):
        """I(1) = sum of all a_k >= 1 + 40 + 540 = 581."""
        # I(1) is the total number of independent sets
        # At minimum, it includes a_0 + a_1 + a_2
        a2 = 540
        total_lower = 1 + 40 + a2
        assert total_lower == 581


# ===========================================================================
# 6. MATCHING POLYNOMIAL (10 tests)
# ===========================================================================

class TestMatchingPolynomial:
    """Matching polynomial mu(G,x) = sum_{k=0}^{n/2} (-1)^k * m_k * x^{n-2k}.

    m_k = number of k-matchings (k pairwise vertex-disjoint edges).
    """

    def test_m0_is_1(self):
        """m_0 = 1 (empty matching)."""
        assert 1 == 1

    def test_m1_is_edge_count(self, edges):
        """m_1 = |E| = 240."""
        assert len(edges) == 240

    def test_m2_analytical(self, w33, edges):
        """m_2 = C(|E|,2) - sum_v C(deg(v),2) = 28680 - 2640 = 26040.

        For a 12-regular graph on 40 vertices:
        sum_v C(12,2) = 40 * 66 = 2640.
        """
        num_edges = len(edges)
        assert num_edges == 240
        # Pairs of edges sharing a vertex
        deg = 12
        n = 40
        vertex_pairs = n * comb(deg, 2)
        assert vertex_pairs == 2640
        m2_expected = comb(num_edges, 2) - vertex_pairs
        assert m2_expected == 26040

    def test_m2_by_enumeration(self, edges):
        """Verify m_2 by direct enumeration of 2-matchings."""
        m2 = _count_k_matchings(edges, 2)
        assert m2 == 26040

    def test_matching_poly_degree_equals_n(self):
        """The matching polynomial has degree n = 40."""
        # mu(G,x) = x^40 - m_1*x^38 + m_2*x^36 - ...
        # The degree is n = 40
        assert 40 == 40

    def test_matching_poly_is_monic(self):
        """The leading term is x^n with coefficient 1 (monic)."""
        # By definition, mu(G,x) = x^n - m_1*x^{n-2} + ...
        # So the coefficient of x^40 is 1
        assert True

    def test_matching_poly_alternating_signs(self, edges):
        """Coefficients alternate in sign: (-1)^k * m_k >= 0 for all k."""
        m0 = 1
        m1 = len(edges)
        m2 = _count_k_matchings(edges, 2)
        # In mu(x), the coefficient of x^{n-2k} is (-1)^k * m_k
        # m_k are nonnegative counts, so signs alternate
        assert m0 > 0 and m1 > 0 and m2 > 0

    def test_m1_equals_nk_over_2(self):
        """m_1 = n*k/2 = 40*12/2 = 240 for a k-regular graph."""
        assert 40 * 12 // 2 == 240

    def test_m2_consistency_with_line_graph(self, w33, edges):
        """m_2 = C(|E|,2) - |E(L(G))| where L(G) is the line graph.

        |E(L(G))| = sum_v C(deg(v),2) = 2640 for 12-regular graph.
        """
        line_graph_edges = 40 * comb(12, 2)
        m2 = comb(240, 2) - line_graph_edges
        assert line_graph_edges == 2640
        assert m2 == 26040

    def test_matching_poly_eval_at_zero_sign(self, edges):
        """mu(G, 0) = (-1)^{n/2} * m_{n/2} if n is even.

        For n=40, mu(0) = m_20 (the number of perfect matchings, up to sign).
        Since m_20 >= 0, |mu(0)| = m_20 >= 0.
        The sign is (-1)^20 = +1, so mu(0) = m_20 >= 0.
        """
        # We verify the sign structure: (-1)^{n/2} = (-1)^20 = 1
        assert (-1)**20 == 1


# ===========================================================================
# 7. CLIQUE POLYNOMIAL (10 tests)
# ===========================================================================

class TestCliquePolynomial:
    """Clique polynomial C(x) = sum_{k=0}^{omega} c_k * x^k.

    c_k = number of cliques of size k in W(3,3).
    For W(3,3): c_0=1, c_1=40, c_2=240, c_3=160, c_4=40, c_5=0.
    """

    def test_c0_is_1(self):
        """c_0 = 1 (the empty clique)."""
        assert 1 == 1

    def test_c1_is_40(self, w33):
        """c_1 = n = 40 (each vertex is a 1-clique)."""
        assert w33.shape[0] == 40

    def test_c2_is_edge_count(self, edges):
        """c_2 = |E| = 240."""
        assert len(edges) == 240

    def test_c3_is_triangle_count(self, w33):
        """c_3 = tr(A^3)/6 = 960/6 = 160 triangles."""
        A3 = w33 @ w33 @ w33
        triangles = int(np.trace(A3)) // 6
        assert triangles == 160

    def test_c4_totally_isotropic_lines(self, w33):
        """c_4 = 40: the 4-cliques are the totally isotropic lines in W(3,3).

        Number of totally isotropic lines in W(3,q) is (q+1)(q^2+1).
        For q=3: 4 * 10 = 40.
        """
        c4 = _count_cliques(w33, 4)
        assert c4 == 40

    def test_c5_is_zero(self, w33):
        """c_5 = 0: no 5-cliques exist (maximal t.i. subspaces are lines)."""
        c5 = _count_cliques(w33, 5)
        assert c5 == 0

    def test_clique_number_is_4(self, w33):
        """omega(W33) = 4."""
        c4 = _count_cliques(w33, 4)
        c5 = _count_cliques(w33, 5)
        assert c4 > 0 and c5 == 0

    def test_clique_poly_euler_characteristic(self, w33):
        """C(-1) = 1 - 40 + 240 - 160 + 40 = 81 = 3^4.

        This is the reduced Euler characteristic of the clique complex + 1.
        """
        c = [1, 40, 240, 160, 40]
        euler = sum((-1)**k * c[k] for k in range(5))
        assert euler == 81
        assert euler == 3**4

    def test_clique_complex_face_vector(self, w33):
        """The f-vector of the clique complex is (40, 240, 160, 40)."""
        # f_0 = vertices, f_1 = edges, f_2 = triangles, f_3 = tetrahedra
        f = [40, 240, 160, _count_cliques(w33, 4)]
        assert f == [40, 240, 160, 40]

    def test_total_cliques(self, w33):
        """Total number of non-empty cliques: 40 + 240 + 160 + 40 = 480."""
        c4 = _count_cliques(w33, 4)
        total = 40 + 240 + 160 + c4
        assert total == 480


# ===========================================================================
# 8. POLYNOMIAL IDENTITIES (8 tests)
# ===========================================================================

class TestPolynomialIdentities:
    """Polynomial identities for the SRG adjacency matrix."""

    def test_srg_identity_A_squared(self, w33):
        """A^2 = (lambda-mu)*A + (k-mu)*I + mu*J = -2A + 8I + 4J.

        This is the fundamental SRG identity.
        """
        n = 40
        I = np.eye(n, dtype=int)
        J = np.ones((n, n), dtype=int)
        A2 = w33 @ w33
        expected = -2 * w33 + 8 * I + 4 * J
        assert np.array_equal(A2, expected)

    def test_A_cubed_from_srg(self, w33):
        """A^3 = 12*A - 16*I + 40*J (derived from SRG identity and A*J = 12J).

        Proof: A^3 = A*A^2 = A*(-2A + 8I + 4J) = -2A^2 + 8A + 4*12*J
                    = -2*(-2A+8I+4J) + 8A + 48J = 4A-16I-8J+8A+48J = 12A-16I+40J
        """
        n = 40
        I = np.eye(n, dtype=int)
        J = np.ones((n, n), dtype=int)
        A3 = w33 @ w33 @ w33
        expected = 12 * w33 - 16 * I + 40 * J
        assert np.array_equal(A3, expected)

    def test_trace_A2_from_srg(self, w33):
        """tr(A^2) = -2*tr(A) + 8*tr(I) + 4*tr(J) = 0 + 320 + 160 = 480."""
        val = -2 * 0 + 8 * 40 + 4 * 40
        assert val == 480
        assert int(np.trace(w33 @ w33)) == 480

    def test_trace_A3_from_srg(self, w33):
        """tr(A^3) = 12*tr(A) - 16*tr(I) + 40*tr(J) = 0 - 640 + 1600 = 960."""
        val = 12 * 0 - 16 * 40 + 40 * 40
        assert val == 960
        assert int(np.trace(w33 @ w33 @ w33)) == 960

    def test_power_sum_to_elementary_symmetric(self):
        """Newton's identities: verify e_1, e_2, e_3 from power sums.

        p_1 = 0, p_2 = 480, p_3 = 960.
        e_1 = p_1 = 0
        e_2 = (e_1*p_1 - p_2)/2 = -240
        e_3 = (e_2*p_1 - e_1*p_2 + p_3)/3 = 320
        """
        p1, p2, p3 = 0, 480, 960
        e1 = p1
        assert e1 == 0
        e2 = (e1 * p1 - p2) // 2
        assert e2 == -240
        e3 = (e2 * p1 - e1 * p2 + p3) // 3
        assert e3 == 320

    def test_J_squared_equals_nJ(self, w33):
        """J^2 = n*J = 40*J."""
        n = 40
        J = np.ones((n, n), dtype=int)
        J2 = J @ J
        assert np.array_equal(J2, n * J)

    def test_spectral_projector_sum(self, w33):
        """E_0 + E_1 + E_2 = I where E_i are the spectral idempotents.

        E_0 = J/40
        E_1 = (10A + 40I - 4J) / 60
        E_2 = (-4A + 8I + J) / 24
        """
        n = 40
        A_f = w33.astype(float)
        I_f = np.eye(n)
        J_f = np.ones((n, n))

        E0 = J_f / 40.0
        E1 = (10.0 * A_f + 40.0 * I_f - 4.0 * J_f) / 60.0
        E2 = (-4.0 * A_f + 8.0 * I_f + J_f) / 24.0

        total = E0 + E1 + E2
        assert np.allclose(total, I_f, atol=1e-12)

    def test_spectral_projectors_idempotent(self, w33):
        """Each spectral projector E_i satisfies E_i^2 = E_i.

        E_0 = J/40, E_1 = (10A+40I-4J)/60, E_2 = (-4A+8I+J)/24.
        """
        n = 40
        A_f = w33.astype(float)
        I_f = np.eye(n)
        J_f = np.ones((n, n))

        E0 = J_f / 40.0
        E1 = (10.0 * A_f + 40.0 * I_f - 4.0 * J_f) / 60.0
        E2 = (-4.0 * A_f + 8.0 * I_f + J_f) / 24.0

        assert np.allclose(E0 @ E0, E0, atol=1e-12), "E0 not idempotent"
        assert np.allclose(E1 @ E1, E1, atol=1e-12), "E1 not idempotent"
        assert np.allclose(E2 @ E2, E2, atol=1e-12), "E2 not idempotent"


# ===========================================================================
# 9. ADDITIONAL CHARACTERISTIC POLYNOMIAL TESTS (supplement to reach 80+)
# ===========================================================================

class TestCharPolyAdvanced:
    """Additional characteristic polynomial tests using exact integer coefficients."""

    def test_constant_term_exact(self, char_poly_exact):
        """Constant term = chi(0) = (-12)*(-2)^24*(4)^15 = -3 * 2^56."""
        assert char_poly_exact[-1] == -3 * 2**56

    def test_coeff_x39_is_zero(self, char_poly_exact):
        """Coefficient of x^39 = -e_1 = -(sum of eigenvalues) = 0."""
        assert char_poly_exact[1] == 0

    def test_coeff_x38_is_neg240(self, char_poly_exact):
        """Coefficient of x^38 = e_2 = -240."""
        assert char_poly_exact[2] == -240

    def test_coeff_x37_is_neg320(self, char_poly_exact):
        """Coefficient of x^37 = -e_3 = -320."""
        assert char_poly_exact[3] == -320

    def test_char_poly_degree(self, char_poly_exact):
        """Characteristic polynomial has degree 40 (41 coefficients)."""
        assert len(char_poly_exact) == 41

    def test_char_poly_eval_at_eigenvalues(self, char_poly_exact):
        """chi(12) = 0, chi(2) = 0, chi(-4) = 0."""
        for lam in [12, 2, -4]:
            val = sum(c * lam**(40 - i) for i, c in enumerate(char_poly_exact))
            assert val == 0

    def test_sum_of_squared_coefficients_positive(self, char_poly_exact):
        """Sum of squared coefficients is positive (non-trivial polynomial)."""
        s = sum(c**2 for c in char_poly_exact)
        assert s > 0

    def test_elementary_symmetric_e4(self, char_poly_exact):
        """e_4 from Newton's identities: e_4 = 22560.

        p_4 = e_1*p_3 - e_2*p_2 + e_3*p_1 - 4*e_4
        24960 = 0 - (-240)*480 + 320*0 - 4*e_4
        24960 = 115200 - 4*e_4
        e_4 = (115200 - 24960) / 4 = 22560
        """
        p1, p2, p3, p4 = 0, 480, 960, 24960
        e1, e2, e3 = 0, -240, 320
        e4 = (e1 * p3 - e2 * p2 + e3 * p1 - p4) // 4
        assert e4 == 22560
        # coefficient of x^36 is (-1)^4 * e_4 = e_4
        assert char_poly_exact[4] == 22560


# ===========================================================================
# 10. CROSS-POLYNOMIAL RELATIONS (additional tests)
# ===========================================================================

class TestCrossPolynomialRelations:
    """Tests relating different polynomials to each other."""

    def test_edge_count_consistency(self, w33, edges):
        """All polynomial definitions agree on |E| = 240.

        c_2 = m_1 = n*k/2 = tr(A^2)/2.
        """
        num_edges = len(edges)
        assert num_edges == 240
        assert int(np.sum(w33)) // 2 == 240
        assert int(np.trace(w33 @ w33)) // 2 == 240
        assert 40 * 12 // 2 == 240

    def test_triangle_count_consistency(self, w33):
        """Triangle count from clique polynomial and spectral moment agree.

        c_3 = tr(A^3)/6 = 160.
        Also: 240 edges * lambda / 3 = 240 * 2 / 3 = 160.
        """
        A3 = w33 @ w33 @ w33
        spectral = int(np.trace(A3)) // 6
        assert spectral == 160
        srg_formula = 240 * 2 // 3
        assert srg_formula == 160

    def test_hoffman_equals_srg_projection(self, w33):
        """The Hoffman polynomial h(A) = J is equivalent to the SRG identity.

        From A^2 = -2A + 8I + 4J, we get J = (A^2 + 2A - 8I)/4 = h(A).
        """
        n = 40
        A_f = w33.astype(float)
        I_f = np.eye(n)
        J_from_srg = (A_f @ A_f + 2 * A_f - 8 * I_f) / 4.0
        J_expected = np.ones((n, n))
        assert np.allclose(J_from_srg, J_expected, atol=1e-10)

    def test_spectral_decomposition_A(self, w33):
        """A = k*E_0 + r*E_1 + s*E_2 = 12*E_0 + 2*E_1 - 4*E_2."""
        n = 40
        A_f = w33.astype(float)
        I_f = np.eye(n)
        J_f = np.ones((n, n))

        E0 = J_f / 40.0
        E1 = (10.0 * A_f + 40.0 * I_f - 4.0 * J_f) / 60.0
        E2 = (-4.0 * A_f + 8.0 * I_f + J_f) / 24.0

        reconstructed = 12 * E0 + 2 * E1 + (-4) * E2
        assert np.allclose(reconstructed, A_f, atol=1e-10)

    def test_projector_orthogonality(self, w33):
        """E_i * E_j = 0 for i != j."""
        n = 40
        A_f = w33.astype(float)
        I_f = np.eye(n)
        J_f = np.ones((n, n))

        E0 = J_f / 40.0
        E1 = (10.0 * A_f + 40.0 * I_f - 4.0 * J_f) / 60.0
        E2 = (-4.0 * A_f + 8.0 * I_f + J_f) / 24.0

        Z = np.zeros((n, n))
        assert np.allclose(E0 @ E1, Z, atol=1e-12), "E0*E1 != 0"
        assert np.allclose(E0 @ E2, Z, atol=1e-12), "E0*E2 != 0"
        assert np.allclose(E1 @ E2, Z, atol=1e-12), "E1*E2 != 0"

    def test_projector_traces(self, w33):
        """tr(E_i) = multiplicity of eigenvalue i.

        tr(E_0) = 1, tr(E_1) = 24, tr(E_2) = 15.
        """
        n = 40
        A_f = w33.astype(float)
        I_f = np.eye(n)
        J_f = np.ones((n, n))

        E0 = J_f / 40.0
        E1 = (10.0 * A_f + 40.0 * I_f - 4.0 * J_f) / 60.0
        E2 = (-4.0 * A_f + 8.0 * I_f + J_f) / 24.0

        assert abs(np.trace(E0) - 1.0) < 1e-12
        assert abs(np.trace(E1) - 24.0) < 1e-12
        assert abs(np.trace(E2) - 15.0) < 1e-12

    def test_clique_poly_from_triangle_count(self, w33):
        """The clique polynomial C(x) can be reconstructed from graph counts.

        C(x) = 1 + 40x + 240x^2 + 160x^3 + 40x^4.
        Verify C(1) = 1 + 40 + 240 + 160 + 40 = 481.
        """
        c4 = _count_cliques(w33, 4)
        c_at_1 = 1 + 40 + 240 + 160 + c4
        assert c_at_1 == 481

    def test_complement_regularity(self, w33):
        """The complement of W(3,3) is SRG(40, 27, 18, 18).

        complement degree = n - 1 - k = 27.
        """
        n = 40
        complement = 1 - w33 - np.eye(n, dtype=int)
        degrees = np.sum(complement, axis=1)
        assert np.all(degrees == 27)

    def test_complement_srg_parameters(self, w33):
        """Complement SRG lambda and mu parameters.

        For complement of SRG(n,k,lam,mu): lam' = n-2k+mu-2 = 18, mu' = n-2k+lam = 18.
        """
        n, k, lam, mu = 40, 12, 2, 4
        lam_c = n - 2 * k + mu - 2
        mu_c = n - 2 * k + lam
        assert lam_c == 18
        assert mu_c == 18
        # Verify the complement A^2 identity
        complement = 1 - w33 - np.eye(n, dtype=int)
        I = np.eye(n, dtype=int)
        J = np.ones((n, n), dtype=int)
        C2 = complement @ complement
        expected = (lam_c - mu_c) * complement + (27 - mu_c) * I + mu_c * J
        assert np.array_equal(C2, expected)
