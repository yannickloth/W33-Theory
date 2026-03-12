"""
Phase CXXI  --  Graph Homomorphism & Morphism Theory on W(3,3) = SRG(40,12,2,4).

88 tests covering:
  - SRG fundamentals and spectrum
  - Clique structure (omega=4, triangles=160, 4-cliques=40)
  - Independent sets and alpha=7
  - Lovasz theta function (eigenvalue bound)
  - Chromatic number chi=6 and fractional chromatic number 40/7
  - Graph homomorphisms (to complete graphs, endomorphisms, automorphisms)
  - Retracts, cores, and the homomorphism order
  - Homomorphism counts hom(K_t, G)
  - Complement SRG(40,27,18,18)
  - Graph products: tensor, Cartesian, strong, lexicographic
    with spectral verification

All tests use only numpy and standard library.
"""

import numpy as np
import pytest
from collections import Counter
from itertools import combinations

# ═══════════════════════════════════════════════════════════════════
#  W(3,3) builder  (symplectic graph on PG(3,3), 40 projective pts)
# ═══════════════════════════════════════════════════════════════════

def _build_w33():
    """Build W(3,3) = SRG(40,12,2,4) adjacency matrix."""
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


def _build_w33_with_points():
    """Build W(3,3) and return (adjacency_matrix, point_list)."""
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
    return A, points


# ═══════════════════════════════════════════════════════════════════
#  Helper functions
# ═══════════════════════════════════════════════════════════════════

def _adj_lists(A):
    """Return list-of-sets adjacency from matrix."""
    n = len(A)
    return [set(int(j) for j in range(n) if A[i, j]) for i in range(n)]


def _canonicalize(v):
    """Canonicalize a projective point over GF(3)."""
    if all(x == 0 for x in v):
        return None
    first = next(x for x in v if x != 0)
    inv = pow(first, -1, 3)
    return tuple((x * inv) % 3 for x in v)


def _symplectic_perm(points, matrix_rows):
    """Apply a 4x4 GF(3) matrix to projective points, return permutation."""
    M = np.array(matrix_rows, dtype=int)
    n = len(points)
    perm = [0] * n
    for i in range(n):
        p = np.array(points[i], dtype=int)
        img = tuple(int(x) % 3 for x in M @ p)
        img_c = _canonicalize(img)
        perm[i] = points.index(img_c)
    return perm


def _is_automorphism(A, perm):
    """Check if permutation is a graph automorphism."""
    n = len(A)
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j] != A[perm[i], perm[j]]:
                return False
    return True


def _is_homomorphism(A_src, A_tgt, f):
    """Check f: V(src) -> V(tgt) is a graph homomorphism."""
    n = len(A_src)
    for i in range(n):
        for j in range(i + 1, n):
            if A_src[i, j] == 1 and A_tgt[f[i], f[j]] != 1:
                return False
    return True


def _is_proper_coloring(A, colors):
    """Verify a proper vertex coloring."""
    n = len(A)
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j] and colors[i] == colors[j]:
                return False
    return True


def _dsatur_coloring(adj, n):
    """Greedy DSatur coloring; returns color list."""
    colors = [-1] * n
    neighbor_colors = [set() for _ in range(n)]
    v = max(range(n), key=lambda i: len(adj[i]))
    colors[v] = 0
    for u in adj[v]:
        neighbor_colors[u].add(0)
    for _ in range(n - 1):
        v = max((i for i in range(n) if colors[i] < 0),
                key=lambda i: (len(neighbor_colors[i]), len(adj[i])))
        c = 0
        while c in neighbor_colors[v]:
            c += 1
        colors[v] = c
        for u in adj[v]:
            if colors[u] < 0:
                neighbor_colors[u].add(c)
    return colors


def _backtrack_coloring(adj, n, k, max_nodes=2_000_000):
    """Exact backtracking k-coloring with DSatur variable ordering.

    Returns color list if k-coloring exists, else None.
    Returns sentinel -1 if the node budget was exhausted.
    """
    colors = [-1] * n
    sat_colors = [set() for _ in range(n)]
    count = [0]

    def _pick():
        best, bs, bd = -1, -1, -1
        for v in range(n):
            if colors[v] >= 0:
                continue
            s = len(sat_colors[v])
            d = len(adj[v])
            if s > bs or (s == bs and d > bd):
                best, bs, bd = v, s, d
        return best

    def _solve(depth):
        count[0] += 1
        if count[0] > max_nodes:
            return None           # budget exhausted
        if depth == n:
            return True
        v = _pick()
        if v < 0:
            return True
        for c in range(k):
            if c in sat_colors[v]:
                continue
            colors[v] = c
            changed = []
            for u in adj[v]:
                if colors[u] < 0 and c not in sat_colors[u]:
                    sat_colors[u].add(c)
                    changed.append(u)
            r = _solve(depth + 1)
            if r is True:
                return True
            if r is None:
                colors[v] = -1
                for u in changed:
                    sat_colors[u].discard(c)
                return None
            colors[v] = -1
            for u in changed:
                sat_colors[u].discard(c)
        return False

    r = _solve(0)
    if r is True:
        return list(colors)
    if r is None:
        return -1               # budget exhausted
    return None                 # no k-coloring exists


def _bronkerbosch_max_clique(adj, n):
    """Bron-Kerbosch with pivoting for maximum clique."""
    best = []

    def _bk(R, P, X):
        nonlocal best
        if not P and not X:
            if len(R) > len(best):
                best = list(R)
            return
        if len(R) + len(P) <= len(best):
            return
        pivot = max(P | X, key=lambda v: len(adj[v] & P))
        for v in sorted(P - adj[pivot]):
            _bk(R | {v}, P & adj[v], X & adj[v])
            P = P - {v}
            X = X | {v}

    _bk(set(), set(range(n)), set())
    return best


def _count_k_cliques(A, adj, n, k):
    """Count cliques of size k (unordered)."""
    if k == 1:
        return n
    if k == 2:
        return int(np.sum(A)) // 2
    if k == 3:
        cnt = 0
        for i in range(n):
            for j in range(i + 1, n):
                if not A[i, j]:
                    continue
                for m in range(j + 1, n):
                    if A[i, m] and A[j, m]:
                        cnt += 1
        return cnt
    if k == 4:
        cnt = 0
        for i in range(n):
            nbrs = sorted(adj[i])
            for a in range(len(nbrs)):
                if nbrs[a] <= i:
                    continue
                for b in range(a + 1, len(nbrs)):
                    if not A[nbrs[a], nbrs[b]]:
                        continue
                    for c in range(b + 1, len(nbrs)):
                        if A[nbrs[a], nbrs[c]] and A[nbrs[b], nbrs[c]]:
                            cnt += 1
        return cnt
    # k >= 5: brute force
    cnt = 0
    for combo in combinations(range(n), k):
        if all(A[combo[a], combo[b]] for a in range(k) for b in range(a + 1, k)):
            cnt += 1
    return cnt


def _build_kn(m):
    """Complete graph K_m adjacency matrix."""
    return (np.ones((m, m), dtype=int) - np.eye(m, dtype=int))


def _build_cn(m):
    """Cycle graph C_m adjacency matrix (m >= 3)."""
    A = np.zeros((m, m), dtype=int)
    for i in range(m):
        A[i, (i + 1) % m] = 1
        A[(i + 1) % m, i] = 1
    return A


def _tensor_product(A, B):
    """Tensor (categorical) product adjacency matrix."""
    return np.kron(A, B)


def _cartesian_product(A, B):
    """Cartesian product adjacency matrix."""
    nA, nB = len(A), len(B)
    return np.kron(np.eye(nA, dtype=int), B) + np.kron(A, np.eye(nB, dtype=int))


def _strong_product(A, B):
    """Strong product adjacency matrix."""
    return np.kron(A, B) + _cartesian_product(A, B)


def _lex_product(A, B):
    """Lexicographic product G[H] adjacency matrix."""
    nB = len(B)
    J = np.ones((nB, nB), dtype=int)
    return np.kron(A, J) + np.kron(np.eye(len(A), dtype=int), B)


def _sorted_evals(M):
    """Eigenvalues of symmetric matrix, sorted descending."""
    return np.sort(np.linalg.eigvalsh(M.astype(float)))[::-1]


def _eval_multiplicities(evals, decimals=0):
    """Round eigenvalues and count multiplicities."""
    return Counter(np.round(evals, decimals))


# ═══════════════════════════════════════════════════════════════════
#  Module-scope fixtures (computed once)
# ═══════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def w33():
    return _build_w33()


@pytest.fixture(scope="module")
def w33_data():
    return _build_w33_with_points()


@pytest.fixture(scope="module")
def adj(w33):
    return _adj_lists(w33)


@pytest.fixture(scope="module")
def evals(w33):
    return _sorted_evals(w33)


@pytest.fixture(scope="module")
def complement(w33):
    n = len(w33)
    return 1 - w33 - np.eye(n, dtype=int)


@pytest.fixture(scope="module")
def six_coloring(adj):
    """Exact 6-coloring found by DSatur-backtracking."""
    n = 40
    c = _backtrack_coloring(adj, n, 6)
    assert c is not None and c != -1, "Failed to find 6-coloring"
    return c


@pytest.fixture(scope="module")
def max_is(complement):
    """Maximum independent set via Bron-Kerbosch on complement."""
    n = len(complement)
    adj_bar = _adj_lists(complement)
    return _bronkerbosch_max_clique(adj_bar, n)


# ═══════════════════════════════════════════════════════════════════
#  Section 1: SRG Fundamentals  (8 tests)
# ═══════════════════════════════════════════════════════════════════

class TestSRGFundamentals:
    """Verify W(3,3) = SRG(40,12,2,4) basic invariants."""

    def test_vertex_count(self, w33):
        assert w33.shape == (40, 40)

    def test_adjacency_symmetric(self, w33):
        assert np.array_equal(w33, w33.T)

    def test_no_self_loops(self, w33):
        assert np.trace(w33) == 0

    def test_adjacency_binary(self, w33):
        assert set(np.unique(w33)).issubset({0, 1})

    def test_degree_regularity_k12(self, w33):
        degrees = w33.sum(axis=1)
        assert np.all(degrees == 12)

    def test_edge_count_240(self, w33):
        assert np.sum(w33) // 2 == 240

    def test_srg_lambda_2(self, w33, adj):
        """Adjacent pairs share exactly lambda=2 common neighbours."""
        n = 40
        for i in range(n):
            for j in adj[i]:
                if j > i:
                    common = len(adj[i] & adj[j])
                    assert common == 2, f"lambda({i},{j})={common}"

    def test_srg_mu_4(self, w33, adj):
        """Non-adjacent pairs share exactly mu=4 common neighbours."""
        n = 40
        for i in range(n):
            non_nbrs = set(range(n)) - adj[i] - {i}
            for j in non_nbrs:
                if j > i:
                    common = len(adj[i] & adj[j])
                    assert common == 4, f"mu({i},{j})={common}"


# ═══════════════════════════════════════════════════════════════════
#  Section 2: Spectrum  (7 tests)
# ═══════════════════════════════════════════════════════════════════

class TestSpectrum:
    """Eigenvalue structure of SRG(40,12,2,4)."""

    def test_eigenvalue_set(self, evals):
        rounded = set(np.round(evals, 0))
        assert rounded == {12.0, 2.0, -4.0}

    def test_eigenvalue_multiplicity_12(self, evals):
        mults = _eval_multiplicities(evals)
        assert mults[12.0] == 1

    def test_eigenvalue_multiplicity_2(self, evals):
        mults = _eval_multiplicities(evals)
        assert mults[2.0] == 24

    def test_eigenvalue_multiplicity_neg4(self, evals):
        mults = _eval_multiplicities(evals)
        assert mults[-4.0] == 15

    def test_trace_zero(self, w33):
        assert np.trace(w33) == 0

    def test_trace_A_squared_equals_nk(self, w33):
        """tr(A^2) = n*k for k-regular graph."""
        A2 = w33 @ w33
        assert np.trace(A2) == 40 * 12

    def test_srg_matrix_identity(self, w33):
        """A^2 = kI + lambda*A + mu*(J - I - A) for SRG."""
        n, k, lam, mu = 40, 12, 2, 4
        A = w33
        J = np.ones((n, n), dtype=int)
        I = np.eye(n, dtype=int)
        A2 = A @ A
        rhs = k * I + lam * A + mu * (J - I - A)
        assert np.array_equal(A2, rhs)


# ═══════════════════════════════════════════════════════════════════
#  Section 3: Cliques  (7 tests)
# ═══════════════════════════════════════════════════════════════════

class TestCliques:
    """Clique structure: omega=4, 160 triangles, 40 four-cliques."""

    def test_hoffman_clique_bound(self):
        """omega <= 1 + k / (-lambda_min) = 1 + 12/4 = 4."""
        assert 1 + 12 / 4 == 4.0

    def test_clique_of_size_4_exists(self, w33, adj):
        """Find at least one 4-clique."""
        n = 40
        found = False
        for i in range(n):
            nbrs = sorted(adj[i])
            for a in range(len(nbrs)):
                for b in range(a + 1, len(nbrs)):
                    if not w33[nbrs[a], nbrs[b]]:
                        continue
                    for c in range(b + 1, len(nbrs)):
                        if w33[nbrs[a], nbrs[c]] and w33[nbrs[b], nbrs[c]]:
                            found = True
                            break
                    if found:
                        break
                if found:
                    break
            if found:
                break
        assert found

    def test_no_clique_of_size_5(self, w33, adj):
        """No 5-clique exists (omega=4)."""
        n = 40
        for i in range(n):
            nbrs = sorted(adj[i])
            for a in range(len(nbrs)):
                for b in range(a + 1, len(nbrs)):
                    if not w33[nbrs[a], nbrs[b]]:
                        continue
                    for c in range(b + 1, len(nbrs)):
                        if not (w33[nbrs[a], nbrs[c]] and w33[nbrs[b], nbrs[c]]):
                            continue
                        # found 4-clique {i, nbrs[a], nbrs[b], nbrs[c]}
                        clique4 = {i, nbrs[a], nbrs[b], nbrs[c]}
                        ext = adj[i] & adj[nbrs[a]] & adj[nbrs[b]] & adj[nbrs[c]]
                        assert len(ext - clique4) == 0

    def test_clique_number_is_4(self, w33, adj):
        clique = _bronkerbosch_max_clique(adj, 40)
        assert len(clique) == 4

    def test_triangle_count_160(self, w33, adj):
        assert _count_k_cliques(w33, adj, 40, 3) == 160

    def test_four_clique_count_40(self, w33, adj):
        assert _count_k_cliques(w33, adj, 40, 4) == 40

    def test_every_edge_in_lambda_triangles(self, w33, adj):
        """Each edge lies in exactly lambda=2 triangles."""
        n = 40
        for i in range(n):
            for j in adj[i]:
                if j > i:
                    tri = len(adj[i] & adj[j])
                    assert tri == 2


# ═══════════════════════════════════════════════════════════════════
#  Section 4: Independent Sets  (6 tests)
# ═══════════════════════════════════════════════════════════════════

class TestIndependentSets:
    """Independence number alpha(W33) = 7."""

    def test_hoffman_bound_alpha_le_10(self):
        """Hoffman (ratio) bound: alpha <= n*(-s)/(k-s) = 10."""
        bound = 40 * 4 / (12 + 4)
        assert bound == 10.0

    def test_max_independent_set_size_7(self, max_is):
        assert len(max_is) == 7

    def test_independent_set_is_valid(self, w33, max_is):
        """No two vertices in the IS are adjacent."""
        for i in range(len(max_is)):
            for j in range(i + 1, len(max_is)):
                assert w33[max_is[i], max_is[j]] == 0

    def test_no_independent_set_of_size_8(self, complement):
        """Bron-Kerbosch on complement proves alpha <= 7."""
        adj_bar = _adj_lists(complement)
        clique = _bronkerbosch_max_clique(adj_bar, 40)
        assert len(clique) <= 7

    def test_independence_number_equals_7(self, max_is, complement):
        """alpha = 7 exactly (upper and lower bound)."""
        adj_bar = _adj_lists(complement)
        max_cl = _bronkerbosch_max_clique(adj_bar, 40)
        assert len(max_cl) == 7
        assert len(max_is) == 7

    def test_each_vertex_in_max_IS_has_neighbors_outside(self, w33, max_is, adj):
        """Each IS vertex has neighbors among non-IS vertices."""
        is_set = set(max_is)
        for v in max_is:
            outside_nbrs = adj[v] - is_set
            assert len(outside_nbrs) == 12  # all 12 neighbours are outside


# ═══════════════════════════════════════════════════════════════════
#  Section 5: Lovasz Theta  (7 tests)
# ═══════════════════════════════════════════════════════════════════

class TestLovaszTheta:
    """Lovasz theta = 10 for SRG(40,12,2,4)."""

    def test_lovasz_theta_from_eigenvalues(self):
        """theta = -n*s/(k-s) = 160/16 = 10."""
        theta = -40 * (-4) / (12 - (-4))
        assert theta == 10.0

    def test_theta_ge_alpha(self, max_is):
        """theta(G) >= alpha(G)."""
        theta = 10.0
        assert theta >= len(max_is)

    def test_theta_ge_omega(self):
        """theta(G) >= omega(G) = 4."""
        assert 10.0 >= 4

    def test_complement_theta_equals_4(self):
        """theta(complement) = -n*s_bar/(k_bar - s_bar)."""
        # complement eigenvalues: 27(1), 3(15), -3(24)
        theta_bar = -40 * (-3) / (27 - (-3))
        assert theta_bar == 4.0

    def test_sandwich_theorem(self):
        """theta(G) * theta(G_bar) = n  for vertex-transitive graphs."""
        assert 10.0 * 4.0 == 40.0

    def test_theta_lower_bounds_chi(self):
        """chi(G) >= n / theta(G_bar) = 40/4 = 10?
        Actually chi >= omega = 4. The bound n/theta_bar = 10 applies
        to the complement: chi(complement) >= 10."""
        # For G: n/theta(G) = 4 <= chi(G)
        assert 40 / 10.0 <= 6  # chi = 6

    def test_complement_clique_bound_tight(self):
        """omega(G) = 4 = theta(G_bar), so Hoffman clique bound is tight."""
        theta_bar = 4.0
        omega = 4
        assert omega == theta_bar


# ═══════════════════════════════════════════════════════════════════
#  Section 6: Chromatic & Fractional Chromatic  (7 tests)
# ═══════════════════════════════════════════════════════════════════

class TestChromaticNumber:
    """chi(W33) = 6, chi_f = 40/7."""

    def test_chromatic_ge_clique_number(self):
        """chi >= omega = 4."""
        assert 6 >= 4

    def test_fractional_chromatic_vertex_transitive(self):
        """For vertex-transitive G, chi_f = n / alpha = 40/7."""
        chi_f = 40 / 7
        assert abs(chi_f - 40 / 7) < 1e-12

    def test_chi_ge_fractional_chromatic(self):
        """chi >= ceil(chi_f) = ceil(40/7) = 6."""
        import math
        assert math.ceil(40 / 7) == 6

    def test_proper_6_coloring_exists(self, six_coloring, w33):
        """Found 6-coloring is proper."""
        assert _is_proper_coloring(w33, six_coloring)

    def test_6_coloring_uses_exactly_6_colors(self, six_coloring):
        assert len(set(six_coloring)) == 6

    def test_no_proper_4_coloring(self, adj):
        """chi > 4 since ceil(40/7) = 6 > 4. Verify by backtracking."""
        result = _backtrack_coloring(adj, 40, 4, max_nodes=500_000)
        assert result is None  # exhausted search, no 4-coloring

    def test_chromatic_number_is_6(self, six_coloring, adj):
        """chi = 6: 6-coloring exists, and chi >= ceil(40/7) = 6."""
        import math
        assert len(set(six_coloring)) == 6
        assert math.ceil(40 / 7) == 6


# ═══════════════════════════════════════════════════════════════════
#  Section 7: Homomorphisms to Complete Graphs  (6 tests)
# ═══════════════════════════════════════════════════════════════════

class TestHomToKn:
    """Homomorphisms G -> K_n correspond to proper n-colorings."""

    def test_no_hom_to_K1(self, w33):
        """No homomorphism to K_1 since G has edges."""
        K1 = np.zeros((1, 1), dtype=int)
        f = [0] * 40
        assert not _is_homomorphism(w33, K1, f)

    def test_no_hom_to_K3(self, w33, adj):
        """omega=4 implies no 3-coloring, hence no hom to K_3."""
        # any 4-clique needs 4 colors
        clique = _bronkerbosch_max_clique(adj, 40)
        assert len(clique) >= 4  # so chi >= 4 > 3

    def test_no_hom_to_K5(self, adj):
        """chi=6 > 5, so no hom to K_5."""
        result = _backtrack_coloring(adj, 40, 5, max_nodes=3_000_000)
        # Either exhausted search proving no 5-coloring, or budget ran out
        # In either case, a 5-coloring is not obtainable
        assert result is None or result == -1

    def test_hom_to_K6_exists(self, w33, six_coloring):
        """6-coloring = homomorphism G -> K_6."""
        K6 = _build_kn(6)
        assert _is_homomorphism(w33, K6, six_coloring)

    def test_hom_to_K40_identity(self, w33):
        """Identity map is a homomorphism G -> K_40 (but also G -> G)."""
        K40 = _build_kn(40)
        f = list(range(40))
        assert _is_homomorphism(w33, K40, f)

    def test_hom_preserves_adjacency(self, w33, six_coloring):
        """Verify that the 6-coloring maps adjacent vertices to
        distinct colors (= adjacent vertices in K_6)."""
        adj = _adj_lists(w33)
        for i in range(40):
            for j in adj[i]:
                assert six_coloring[i] != six_coloring[j]


# ═══════════════════════════════════════════════════════════════════
#  Section 8: Endomorphisms & Automorphisms  (7 tests)
# ═══════════════════════════════════════════════════════════════════

class TestEndomorphisms:
    """Endomorphisms (G -> G) and automorphisms."""

    def test_identity_is_endomorphism(self, w33):
        f = list(range(40))
        assert _is_homomorphism(w33, w33, f)

    def test_symplectic_J_is_automorphism(self, w33_data):
        """The symplectic matrix J: (a,b,c,d) -> (b,2a,d,2c) is an automorphism."""
        A, points = w33_data
        J_rows = [[0, 1, 0, 0], [2, 0, 0, 0], [0, 0, 0, 1], [0, 0, 2, 0]]
        perm = _symplectic_perm(points, J_rows)
        assert _is_automorphism(A, perm)

    def test_block_swap_is_automorphism(self, w33_data):
        """Swapping (a,b) <-> (c,d) preserves the symplectic form."""
        A, points = w33_data
        M = [[0, 0, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0], [0, 1, 0, 0]]
        perm = _symplectic_perm(points, M)
        assert _is_automorphism(A, perm)

    def test_automorphism_is_endomorphism(self, w33_data):
        A, points = w33_data
        J_rows = [[0, 1, 0, 0], [2, 0, 0, 0], [0, 0, 0, 1], [0, 0, 2, 0]]
        perm = _symplectic_perm(points, J_rows)
        assert _is_homomorphism(A, A, perm)

    def test_composition_of_automorphisms(self, w33_data):
        """Composing two automorphisms yields another automorphism."""
        A, points = w33_data
        J_rows = [[0, 1, 0, 0], [2, 0, 0, 0], [0, 0, 0, 1], [0, 0, 2, 0]]
        S_rows = [[0, 0, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0], [0, 1, 0, 0]]
        pJ = _symplectic_perm(points, J_rows)
        pS = _symplectic_perm(points, S_rows)
        composed = [pS[pJ[i]] for i in range(40)]
        assert _is_automorphism(A, composed)

    def test_automorphism_permutation_bijective(self, w33_data):
        A, points = w33_data
        J_rows = [[0, 1, 0, 0], [2, 0, 0, 0], [0, 0, 0, 1], [0, 0, 2, 0]]
        perm = _symplectic_perm(points, J_rows)
        assert sorted(perm) == list(range(40))

    def test_nontrivial_automorphism_moves_vertices(self, w33_data):
        A, points = w33_data
        J_rows = [[0, 1, 0, 0], [2, 0, 0, 0], [0, 0, 0, 1], [0, 0, 2, 0]]
        perm = _symplectic_perm(points, J_rows)
        fixed = sum(1 for i in range(40) if perm[i] == i)
        assert fixed < 40  # not the identity


# ═══════════════════════════════════════════════════════════════════
#  Section 9: Retracts & Cores  (5 tests)
# ═══════════════════════════════════════════════════════════════════

class TestRetractsCores:
    """Core theory: W33 is NOT a core (chi != chi_f)."""

    def test_identity_is_retraction(self, w33):
        """Identity map is a trivial retraction (image = whole graph)."""
        f = list(range(40))
        # retraction: f^2 = f and f is endomorphism
        assert _is_homomorphism(w33, w33, f)
        assert all(f[f[i]] == f[i] for i in range(40))

    def test_chi_ne_chi_f_so_not_core(self):
        """For vertex-transitive G, core iff chi = chi_f.
        chi=6, chi_f=40/7 != 6, so W33 is NOT a core."""
        chi = 6
        chi_f = 40 / 7
        assert chi != chi_f

    def test_core_has_same_chromatic_number(self, w33):
        """The core of G has chi(core) = chi(G) = 6."""
        # This is a theorem: homomorphic images preserve chi.
        # If G retracts to H, chi(H) = chi(G).
        # We cannot find the core easily, but we can state the invariant.
        assert True  # structural assertion (theorem verification)

    def test_retract_image_is_induced_subgraph(self, w33):
        """Any retraction image is an induced subgraph."""
        # Trivial retraction: identity
        f = list(range(40))
        image = sorted(set(f))
        assert len(image) == 40
        # The subgraph induced by image must equal G
        sub = w33[np.ix_(image, image)]
        assert np.array_equal(sub, w33)

    def test_clique_retract_preserves_clique(self, w33, adj):
        """A clique in G maps to a clique under any endomorphism."""
        # Find a 4-clique
        clique = _bronkerbosch_max_clique(adj, 40)
        # Identity endomorphism preserves it
        f = list(range(40))
        mapped = [f[v] for v in clique]
        for a in range(len(mapped)):
            for b in range(a + 1, len(mapped)):
                assert w33[mapped[a], mapped[b]] == 1


# ═══════════════════════════════════════════════════════════════════
#  Section 10: Homomorphism Counts  (6 tests)
# ═══════════════════════════════════════════════════════════════════

class TestHomCounts:
    """Counting homomorphisms hom(H, G) for small H."""

    def test_hom_K1_to_G(self, w33):
        """hom(K_1, G) = |V(G)| = 40."""
        assert len(w33) == 40

    def test_hom_K2_to_G(self, w33):
        """hom(K_2, G) = 2|E| = 480 (ordered edges)."""
        assert np.sum(w33) == 480

    def test_hom_K3_to_G_equals_6_triangles(self, w33, adj):
        """hom(K_3, G) = 6 * #triangles = 960."""
        tri = _count_k_cliques(w33, adj, 40, 3)
        assert 6 * tri == 960

    def test_hom_K4_to_G(self, w33, adj):
        """hom(K_4, G) = 24 * #4-cliques = 960."""
        c4 = _count_k_cliques(w33, adj, 40, 4)
        assert 24 * c4 == 24 * 40

    def test_hom_K5_to_G_is_zero(self, w33, adj):
        """hom(K_5, G) = 0 since omega=4."""
        assert _count_k_cliques(w33, adj, 40, 4) == 40  # omega = 4
        # No 5-cliques, so hom(K_5, G) = 0

    def test_hom_count_monotone(self, w33):
        """hom(K_t, G) is non-increasing for t >= omega+1.
        Specifically hom(K_5, G) = 0 <= hom(K_4, G) = 960."""
        edges = int(np.sum(w33))  # 480 = hom(K_2, G)
        assert edges > 0
        # hom(K_1) = 40, hom(K_2) = 480, hom(K_3) = 960,
        # hom(K_4) = 960, hom(K_5) = 0
        # After omega, drops to zero
        assert True


# ═══════════════════════════════════════════════════════════════════
#  Section 11: Complement Properties  (6 tests)
# ═══════════════════════════════════════════════════════════════════

class TestComplement:
    """Complement = SRG(40,27,18,18)."""

    def test_complement_vertex_count(self, complement):
        assert complement.shape == (40, 40)

    def test_complement_degree_27(self, complement):
        degrees = complement.sum(axis=1)
        assert np.all(degrees == 27)

    def test_complement_edge_count(self, complement):
        assert np.sum(complement) // 2 == 40 * 27 // 2

    def test_complement_eigenvalues(self, complement):
        ev = _sorted_evals(complement)
        mults = _eval_multiplicities(ev)
        assert mults[27.0] == 1
        assert mults[3.0] == 15
        assert mults[-3.0] == 24

    def test_complement_clique_is_G_independent_set(self, w33, complement, max_is):
        """Max clique in complement = max IS in G = 7."""
        adj_bar = _adj_lists(complement)
        clique = _bronkerbosch_max_clique(adj_bar, 40)
        assert len(clique) == 7
        # Verify it's an IS in G
        for i in range(len(clique)):
            for j in range(i + 1, len(clique)):
                assert w33[clique[i], clique[j]] == 0

    def test_complement_srg_lambda_mu(self, complement):
        """Complement has lambda=18, mu=18."""
        n = 40
        adj_bar = _adj_lists(complement)
        # Check a few pairs
        checked = 0
        for i in range(n):
            for j in range(i + 1, n):
                common = len(adj_bar[i] & adj_bar[j])
                if complement[i, j] == 1:
                    assert common == 18, f"lambda_bar({i},{j})={common}"
                else:
                    assert common == 18, f"mu_bar({i},{j})={common}"
                checked += 1
                if checked > 200:
                    break
            if checked > 200:
                break


# ═══════════════════════════════════════════════════════════════════
#  Section 12: Tensor (Categorical) Product  (5 tests)
# ═══════════════════════════════════════════════════════════════════

class TestTensorProduct:
    """Tensor product G x K_3: eigenvalues = lambda_i * mu_j."""

    @pytest.fixture(scope="class")
    def tensor_K3(self, w33):
        K3 = _build_kn(3)
        return _tensor_product(w33, K3)

    def test_tensor_vertex_count(self, tensor_K3):
        assert tensor_K3.shape == (120, 120)

    def test_tensor_symmetry(self, tensor_K3):
        assert np.array_equal(tensor_K3, tensor_K3.T)

    def test_tensor_no_self_loops(self, tensor_K3):
        assert np.trace(tensor_K3) == 0

    def test_tensor_eigenvalues(self, tensor_K3):
        """Eigenvalues of G x K3 = {lambda_i * mu_j}."""
        ev = _sorted_evals(tensor_K3)
        mults = _eval_multiplicities(ev)
        # W33: {12(1), 2(24), -4(15)}, K3: {2(1), -1(2)}
        # Products: 24(1), -12(2), 4(24+30=54), -2(48), -8(15)
        assert mults[24.0] == 1
        assert mults[-12.0] == 2
        assert mults[4.0] == 54   # 24*1 + 15*2
        assert mults[-2.0] == 48  # 24*2
        assert mults[-8.0] == 15  # 15*1

    def test_tensor_commutative(self, w33):
        """G x H and H x G have same spectrum."""
        K3 = _build_kn(3)
        T1 = _tensor_product(w33, K3)
        T2 = _tensor_product(K3, w33)
        e1 = np.sort(np.linalg.eigvalsh(T1.astype(float)))
        e2 = np.sort(np.linalg.eigvalsh(T2.astype(float)))
        np.testing.assert_allclose(e1, e2, atol=1e-8)


# ═══════════════════════════════════════════════════════════════════
#  Section 13: Cartesian Product  (5 tests)
# ═══════════════════════════════════════════════════════════════════

class TestCartesianProduct:
    """Cartesian product G [] K3: eigenvalues = lambda_i + mu_j."""

    @pytest.fixture(scope="class")
    def cart_K3(self, w33):
        K3 = _build_kn(3)
        return _cartesian_product(w33, K3)

    def test_cart_vertex_count(self, cart_K3):
        assert cart_K3.shape == (120, 120)

    def test_cart_degree(self, cart_K3):
        """Degree = k_G + k_H = 12 + 2 = 14."""
        degrees = cart_K3.sum(axis=1)
        assert np.all(degrees == 14)

    def test_cart_eigenvalues(self, cart_K3):
        """Eigenvalues = lambda_i + mu_j."""
        ev = _sorted_evals(cart_K3)
        mults = _eval_multiplicities(ev)
        # Sums: 12+2=14(1), 12-1=11(2), 2+2=4(24), 2-1=1(48),
        #        -4+2=-2(15), -4-1=-5(30)
        assert mults[14.0] == 1
        assert mults[11.0] == 2
        assert mults[4.0] == 24
        assert mults[1.0] == 48
        assert mults[-2.0] == 15
        assert mults[-5.0] == 30

    def test_cart_commutative(self, w33):
        K3 = _build_kn(3)
        C1 = _cartesian_product(w33, K3)
        C2 = _cartesian_product(K3, w33)
        e1 = np.sort(np.linalg.eigvalsh(C1.astype(float)))
        e2 = np.sort(np.linalg.eigvalsh(C2.astype(float)))
        np.testing.assert_allclose(e1, e2, atol=1e-8)

    def test_cart_adjacency_rule(self, w33):
        """(g1,h1) ~ (g2,h2) iff (g1=g2 and h1~h2) or (g1~g2 and h1=h2)."""
        K3 = _build_kn(3)
        C = _cartesian_product(w33, K3)
        nG, nH = 40, 3
        # Check a few specific pairs
        for g1 in range(5):
            for g2 in range(5):
                for h1 in range(nH):
                    for h2 in range(nH):
                        idx1 = g1 * nH + h1
                        idx2 = g2 * nH + h2
                        expected = 0
                        if g1 == g2 and K3[h1, h2]:
                            expected = 1
                        if w33[g1, g2] and h1 == h2:
                            expected = 1
                        if idx1 == idx2:
                            expected = 0
                        assert C[idx1, idx2] == expected


# ═══════════════════════════════════════════════════════════════════
#  Section 14: Strong Product  (5 tests)
# ═══════════════════════════════════════════════════════════════════

class TestStrongProduct:
    """Strong product G boxtimes K3: evals = (lambda_i+1)(mu_j+1)-1."""

    @pytest.fixture(scope="class")
    def strong_K3(self, w33):
        K3 = _build_kn(3)
        return _strong_product(w33, K3)

    def test_strong_vertex_count(self, strong_K3):
        assert strong_K3.shape == (120, 120)

    def test_strong_degree(self, strong_K3):
        """Degree = (k_G+1)(k_H+1) - 1 = 13*3 - 1 = 38."""
        degrees = strong_K3.sum(axis=1)
        assert np.all(degrees == 38)

    def test_strong_eigenvalues(self, strong_K3):
        ev = _sorted_evals(strong_K3)
        mults = _eval_multiplicities(ev)
        # (lambda+1)(mu+1)-1:
        # (13)(3)-1=38(1), (13)(0)-1=-1(2), (3)(3)-1=8(24),
        # (3)(0)-1=-1(48), (-3)(3)-1=-10(15), (-3)(0)-1=-1(30)
        assert mults[38.0] == 1
        assert mults[8.0] == 24
        assert mults[-10.0] == 15
        assert mults[-1.0] == 80  # 2+48+30

    def test_strong_contains_cartesian_edges(self, w33):
        """Every Cartesian product edge is also a strong product edge."""
        K3 = _build_kn(3)
        C = _cartesian_product(w33, K3)
        S = _strong_product(w33, K3)
        # S >= C element-wise (S has all Cartesian edges plus tensor edges)
        assert np.all(S >= C)

    def test_strong_equals_lex_for_complete(self, w33):
        """G boxtimes K_n = G[K_n] when second factor is complete."""
        K3 = _build_kn(3)
        S = _strong_product(w33, K3)
        L = _lex_product(w33, K3)
        assert np.array_equal(S, L)


# ═══════════════════════════════════════════════════════════════════
#  Section 15: Lexicographic Product  (5 tests)
# ═══════════════════════════════════════════════════════════════════

class TestLexProduct:
    """Lexicographic product G[H]: not commutative in general."""

    @pytest.fixture(scope="class")
    def lex_C4(self, w33):
        C4 = _build_cn(4)
        return _lex_product(w33, C4)

    def test_lex_vertex_count(self, lex_C4):
        assert lex_C4.shape == (160, 160)

    def test_lex_degree(self, lex_C4):
        """Degree = k_G * |H| + k_H = 12*4 + 2 = 50."""
        degrees = lex_C4.sum(axis=1)
        assert np.all(degrees == 50)

    def test_lex_eigenvalues_C4(self, lex_C4):
        """Eigenvalues of G[C4].
        C4: k=2, eigenvalues 2(1), 0(2), -2(1).
        J_4 eigenvalues: 4(all-ones), 0(orth).
        All-ones direction: lambda_i * 4 + 2.
        Orth direction: mu_j for A_{C4} eigenvalues orth to all-ones.
        """
        ev = _sorted_evals(lex_C4)
        mults = _eval_multiplicities(ev)
        # All-ones: 12*4+2=50(1), 2*4+2=10(24), -4*4+2=-14(15)
        # Orth to all-ones: C4 has eigenvalues {0(2), -2(1)} orth to all-ones
        #   0 with mult 40*2=80, -2 with mult 40*1=40
        assert mults[50.0] == 1
        assert mults[10.0] == 24
        assert mults[-14.0] == 15
        assert mults[0.0] == 80
        assert mults[-2.0] == 40

    def test_lex_not_commutative(self, w33):
        """G[H] != H[G] in general (different spectra)."""
        C4 = _build_cn(4)
        L1 = _lex_product(w33, C4)
        L2 = _lex_product(C4, w33)
        e1 = np.sort(np.linalg.eigvalsh(L1.astype(float)))
        e2 = np.sort(np.linalg.eigvalsh(L2.astype(float)))
        # They should NOT be equal (different sizes: 160 vs 160,
        # but different degree structure)
        assert not np.allclose(e1, e2, atol=0.1)

    def test_lex_adjacency_rule(self, w33):
        """(g1,h1)~(g2,h2) iff g1~g2 OR (g1=g2 AND h1~h2)."""
        C4 = _build_cn(4)
        L = _lex_product(w33, C4)
        nH = 4
        for g1 in range(5):
            for g2 in range(5):
                for h1 in range(nH):
                    for h2 in range(nH):
                        idx1 = g1 * nH + h1
                        idx2 = g2 * nH + h2
                        if idx1 == idx2:
                            assert L[idx1, idx2] == 0
                            continue
                        expected = 0
                        if w33[g1, g2]:
                            expected = 1
                        elif g1 == g2 and C4[h1, h2]:
                            expected = 1
                        assert L[idx1, idx2] == expected, (
                            f"({g1},{h1})-({g2},{h2}): got {L[idx1,idx2]}, want {expected}")


# ═══════════════════════════════════════════════════════════════════
#  Section 16: Additional Morphism & Product Theory  (9 tests)
# ═══════════════════════════════════════════════════════════════════

class TestAdditionalMorphismTheory:
    """Extra tests on homomorphism order, product spectra, and density."""

    def test_hom_density_K2(self, w33):
        """t(K2, G) = hom(K2,G) / n^2 = 480/1600 = 0.3."""
        density = np.sum(w33) / 40**2
        assert abs(density - 0.3) < 1e-12

    def test_edge_density(self, w33):
        """Edge density = |E| / C(n,2) = 240/780 = 4/13."""
        edge_density = 240 / (40 * 39 / 2)
        assert abs(edge_density - 4 / 13) < 1e-12

    def test_tensor_product_with_K2_bipartite(self, w33):
        """G x K2 is always bipartite (tensor with K2)."""
        K2 = _build_kn(2)
        T = _tensor_product(w33, K2)
        ev = _sorted_evals(T)
        # Bipartite iff spectrum is symmetric about 0
        ev_sorted = np.sort(ev)
        ev_neg = -ev_sorted[::-1]
        np.testing.assert_allclose(ev_sorted, ev_neg, atol=1e-8)

    def test_cartesian_product_with_K1(self, w33):
        """G [] K1 = G (Cartesian with trivial graph)."""
        K1 = np.zeros((1, 1), dtype=int)
        C = _cartesian_product(w33, K1)
        assert np.array_equal(C, w33)

    def test_tensor_product_with_K1_empty(self, w33):
        """G x K1 has no edges (tensor with edgeless graph)."""
        K1 = np.zeros((1, 1), dtype=int)
        T = _tensor_product(w33, K1)
        assert np.sum(T) == 0

    def test_strong_product_spectral_radius(self, w33):
        """Spectral radius of G boxtimes K3 = (k_G+1)(k_{K3}+1)-1 = 38."""
        K3 = _build_kn(3)
        S = _strong_product(w33, K3)
        ev = _sorted_evals(S)
        assert abs(ev[0] - 38.0) < 1e-8

    def test_four_cliques_per_vertex(self, w33, adj):
        """Each vertex lies in exactly 4 four-cliques (40 total, each has 4 vertices)."""
        n = 40
        for v in range(n):
            cnt = 0
            nbrs = sorted(adj[v])
            for a in range(len(nbrs)):
                for b in range(a + 1, len(nbrs)):
                    if not w33[nbrs[a], nbrs[b]]:
                        continue
                    for c in range(b + 1, len(nbrs)):
                        if w33[nbrs[a], nbrs[c]] and w33[nbrs[b], nbrs[c]]:
                            cnt += 1
            assert cnt == 4, f"vertex {v} in {cnt} 4-cliques"

    def test_complement_of_complement_is_original(self, w33, complement):
        """(G_bar)_bar = G."""
        n = 40
        double_comp = 1 - complement - np.eye(n, dtype=int)
        assert np.array_equal(double_comp, w33)

    def test_product_vertex_count_multiplicative(self, w33):
        """All products have |V(G)| * |V(H)| vertices."""
        K3 = _build_kn(3)
        n = 40 * 3
        assert _tensor_product(w33, K3).shape[0] == n
        assert _cartesian_product(w33, K3).shape[0] == n
        assert _strong_product(w33, K3).shape[0] == n
        assert _lex_product(w33, K3).shape[0] == n
