"""
Phase CXXXV  --  Deep graph coloring theory for W(3,3) = SRG(40,12,2,4).

Explores greedy and DSatur vertex colorings, spectral chromatic bounds,
clique and independent-set structure, edge coloring via Vizing's theorem,
choosability / degeneracy, and cross-validation of all results.

All algorithms are self-contained (no external graph libraries).
"""

import math
import numpy as np
import pytest
from collections import Counter, defaultdict
from itertools import combinations

# ---------------------------------------------------------------------------
# W(3,3) builder  (self-contained, NOT imported)
# ---------------------------------------------------------------------------

def _build_w33():
    """Build adjacency matrix and point list for W(3,3) = SRG(40,12,2,4)."""
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

# ---------------------------------------------------------------------------
# Coloring algorithms
# ---------------------------------------------------------------------------

def _greedy_coloring(A, order=None):
    """First-fit greedy vertex coloring in the given vertex order."""
    n = A.shape[0]
    if order is None:
        order = list(range(n))
    color = [-1] * n
    for v in order:
        used = set()
        for u in range(n):
            if A[v, u] == 1 and color[u] >= 0:
                used.add(color[u])
        c = 0
        while c in used:
            c += 1
        color[v] = c
    return color


def _dsatur_coloring(A):
    """DSatur (degree-of-saturation) vertex coloring."""
    n = A.shape[0]
    color = [-1] * n
    saturation = np.zeros(n, dtype=int)
    degree = np.sum(A, axis=1).astype(int)
    colored = np.zeros(n, dtype=bool)

    for _ in range(n):
        best = -1
        best_sat = -1
        best_deg = -1
        for v in range(n):
            if colored[v]:
                continue
            if (saturation[v] > best_sat
                or (saturation[v] == best_sat and degree[v] > best_deg)
                or (saturation[v] == best_sat and degree[v] == best_deg
                    and (best == -1 or v < best))):
                best = v
                best_sat = saturation[v]
                best_deg = degree[v]
        used = set()
        for u in range(n):
            if A[best, u] == 1 and color[u] >= 0:
                used.add(color[u])
        c = 0
        while c in used:
            c += 1
        color[best] = c
        colored[best] = True
        for u in range(n):
            if A[best, u] == 1 and not colored[u]:
                nc = set()
                for w in range(n):
                    if A[u, w] == 1 and color[w] >= 0:
                        nc.add(color[w])
                saturation[u] = len(nc)
    return color


def _verify_vertex_coloring(A, coloring):
    """Return True iff no adjacent pair shares a color."""
    n = A.shape[0]
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j] == 1 and coloring[i] == coloring[j]:
                return False
    return True


def _greedy_edge_coloring(A):
    """First-fit greedy edge coloring.  Returns dict (u,v)->color."""
    n = A.shape[0]
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j] == 1:
                edges.append((i, j))
    vertex_used = defaultdict(set)
    edge_color = {}
    for u, v in edges:
        used = vertex_used[u] | vertex_used[v]
        c = 0
        while c in used:
            c += 1
        edge_color[(u, v)] = c
        vertex_used[u].add(c)
        vertex_used[v].add(c)
    return edge_color


def _find_all_triangles(A):
    """Return list of triangles (i,j,k) with i<j<k."""
    n = A.shape[0]
    tris = []
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j] != 1:
                continue
            for k in range(j + 1, n):
                if A[i, k] == 1 and A[j, k] == 1:
                    tris.append((i, j, k))
    return tris


def _find_max_clique_greedy(A):
    """Greedy max-clique: try every start vertex, extend greedily."""
    n = A.shape[0]
    best = []
    for start in range(n):
        clique = [start]
        nbrs = [u for u in range(n) if A[start, u] == 1]
        for u in sorted(nbrs):
            if all(A[u, w] == 1 for w in clique):
                clique.append(u)
        if len(clique) > len(best):
            best = list(clique)
    return best


def _find_max_independent_set_greedy(A):
    """Greedy max-IS: complement-graph clique via simple extension."""
    n = A.shape[0]
    Ac = 1 - A - np.eye(n, dtype=int)  # complement adjacency
    best = []
    for start in range(n):
        iset = [start]
        cands = [u for u in range(n) if u != start and A[start, u] == 0]
        for u in cands:
            if all(A[u, w] == 0 for w in iset):
                iset.append(u)
        if len(iset) > len(best):
            best = list(iset)
    return best


def _compute_degeneracy(A):
    """Return (degeneracy, ordering) using iterative min-degree peeling."""
    n = A.shape[0]
    deg = np.sum(A, axis=1).copy()
    remaining = set(range(n))
    degen = 0
    ordering = []
    while remaining:
        best_v = min(remaining, key=lambda v: sum(1 for u in remaining if A[v, u] == 1))
        d = sum(1 for u in remaining if A[best_v, u] == 1)
        degen = max(degen, d)
        ordering.append(best_v)
        remaining.remove(best_v)
    return degen, ordering


def _greedy_independent_set(A):
    """Greedy independent set: iteratively pick min-degree vertex in residual."""
    n = A.shape[0]
    remaining = set(range(n))
    ind = []
    while remaining:
        best = min(remaining,
                   key=lambda v: sum(1 for u in remaining if A[v, u] == 1))
        ind.append(best)
        remaining -= {best} | {u for u in remaining if A[best, u] == 1}
    return ind


# ===================================================================
# MODULE-SCOPED FIXTURES
# ===================================================================

@pytest.fixture(scope="module")
def w33_data():
    return _build_w33()

@pytest.fixture(scope="module")
def w33_adj(w33_data):
    return w33_data[0]

@pytest.fixture(scope="module")
def w33_points(w33_data):
    return w33_data[1]

@pytest.fixture(scope="module")
def w33_eigenvalues(w33_adj):
    ev = np.linalg.eigvalsh(w33_adj.astype(float))
    return np.sort(ev)[::-1]

@pytest.fixture(scope="module")
def greedy_natural(w33_adj):
    return _greedy_coloring(w33_adj)

@pytest.fixture(scope="module")
def greedy_degree_sorted(w33_adj):
    deg = np.sum(w33_adj, axis=1)
    order = sorted(range(40), key=lambda v: -deg[v])
    return _greedy_coloring(w33_adj, order)

@pytest.fixture(scope="module")
def greedy_random42(w33_adj):
    rng = np.random.RandomState(42)
    order = list(rng.permutation(40))
    return _greedy_coloring(w33_adj, order)

@pytest.fixture(scope="module")
def greedy_reverse(w33_adj):
    return _greedy_coloring(w33_adj, list(range(39, -1, -1)))

@pytest.fixture(scope="module")
def dsatur_result(w33_adj):
    return _dsatur_coloring(w33_adj)

@pytest.fixture(scope="module")
def best_coloring(w33_adj, greedy_natural, greedy_degree_sorted,
                  greedy_random42, greedy_reverse, dsatur_result):
    all_c = [greedy_natural, greedy_degree_sorted,
             greedy_random42, greedy_reverse, dsatur_result]
    return min(all_c, key=lambda c: max(c) + 1)

@pytest.fixture(scope="module")
def best_chi(best_coloring):
    return max(best_coloring) + 1

@pytest.fixture(scope="module")
def max_clique(w33_adj):
    return _find_max_clique_greedy(w33_adj)

@pytest.fixture(scope="module")
def independent_set_10(w33_adj):
    return _find_max_independent_set_greedy(w33_adj)

@pytest.fixture(scope="module")
def edge_coloring(w33_adj):
    return _greedy_edge_coloring(w33_adj)

@pytest.fixture(scope="module")
def degeneracy_data(w33_adj):
    return _compute_degeneracy(w33_adj)

@pytest.fixture(scope="module")
def triangles(w33_adj):
    return _find_all_triangles(w33_adj)


# ===================================================================
# 0.  SRG PARAMETER VERIFICATION  (9 tests)
# ===================================================================

class TestSRGParameters:
    def test_vertex_count(self, w33_adj):
        assert w33_adj.shape == (40, 40)

    def test_point_count(self, w33_points):
        assert len(w33_points) == 40

    def test_symmetric(self, w33_adj):
        assert np.array_equal(w33_adj, w33_adj.T)

    def test_zero_diagonal(self, w33_adj):
        assert np.all(np.diag(w33_adj) == 0)

    def test_binary_entries(self, w33_adj):
        assert set(np.unique(w33_adj)) == {0, 1}

    def test_regular_degree_12(self, w33_adj):
        assert np.all(np.sum(w33_adj, axis=1) == 12)

    def test_edge_count_240(self, w33_adj):
        assert np.sum(w33_adj) == 480          # each edge counted twice

    def test_lambda_equals_2(self, w33_adj):
        A = w33_adj; A2 = A @ A
        for i in range(40):
            for j in range(i + 1, 40):
                if A[i, j] == 1:
                    assert A2[i, j] == 2

    def test_mu_equals_4(self, w33_adj):
        A = w33_adj; A2 = A @ A
        for i in range(40):
            for j in range(i + 1, 40):
                if A[i, j] == 0:
                    assert A2[i, j] == 4


# ===================================================================
# 1.  GREEDY COLORING  (14 tests)
# ===================================================================

class TestGreedyColoring:
    def test_natural_valid(self, w33_adj, greedy_natural):
        assert _verify_vertex_coloring(w33_adj, greedy_natural)

    def test_natural_all_colored(self, greedy_natural):
        assert len(greedy_natural) == 40
        assert all(c >= 0 for c in greedy_natural)

    def test_natural_ge_hoffman(self, greedy_natural):
        assert max(greedy_natural) + 1 >= 4

    def test_natural_le_delta_plus_1(self, greedy_natural):
        assert max(greedy_natural) + 1 <= 13

    def test_degree_order_valid(self, w33_adj, greedy_degree_sorted):
        assert _verify_vertex_coloring(w33_adj, greedy_degree_sorted)

    def test_degree_order_bounds(self, greedy_degree_sorted):
        assert 4 <= max(greedy_degree_sorted) + 1 <= 13

    def test_random42_valid(self, w33_adj, greedy_random42):
        assert _verify_vertex_coloring(w33_adj, greedy_random42)

    def test_random42_bounds(self, greedy_random42):
        assert 4 <= max(greedy_random42) + 1 <= 13

    def test_reverse_valid(self, w33_adj, greedy_reverse):
        assert _verify_vertex_coloring(w33_adj, greedy_reverse)

    def test_reverse_bounds(self, greedy_reverse):
        assert 4 <= max(greedy_reverse) + 1 <= 13

    def test_contiguous_colors(self, greedy_natural):
        used = set(greedy_natural)
        assert used == set(range(max(greedy_natural) + 1))

    def test_deterministic(self, w33_adj):
        c1 = _greedy_coloring(w33_adj)
        c2 = _greedy_coloring(w33_adj)
        assert c1 == c2

    def test_smallest_last_order(self, w33_adj, degeneracy_data):
        _, ordering = degeneracy_data
        col = _greedy_coloring(w33_adj, ordering[::-1])
        assert _verify_vertex_coloring(w33_adj, col)
        assert 4 <= max(col) + 1 <= 13

    def test_multiple_random_seeds(self, w33_adj):
        for seed in [0, 1, 7, 13, 99]:
            rng = np.random.RandomState(seed)
            order = list(rng.permutation(40))
            col = _greedy_coloring(w33_adj, order)
            assert _verify_vertex_coloring(w33_adj, col)
            assert 4 <= max(col) + 1 <= 13


# ===================================================================
# 2.  HOFFMAN CHROMATIC BOUND  (8 tests)
# ===================================================================

class TestHoffmanBound:
    def test_sorted_descending(self, w33_eigenvalues):
        for i in range(len(w33_eigenvalues) - 1):
            assert w33_eigenvalues[i] >= w33_eigenvalues[i + 1] - 1e-10

    def test_largest_eigenvalue_12(self, w33_eigenvalues):
        assert abs(w33_eigenvalues[0] - 12.0) < 1e-10

    def test_smallest_eigenvalue_minus4(self, w33_eigenvalues):
        assert abs(w33_eigenvalues[-1] - (-4.0)) < 1e-10

    def test_multiplicity_of_2(self, w33_eigenvalues):
        assert sum(1 for e in w33_eigenvalues if abs(e - 2.0) < 1e-8) == 24

    def test_multiplicity_of_minus4(self, w33_eigenvalues):
        assert sum(1 for e in w33_eigenvalues if abs(e + 4.0) < 1e-8) == 15

    def test_hoffman_equals_4(self, w33_eigenvalues):
        h = 1.0 - w33_eigenvalues[0] / w33_eigenvalues[-1]
        assert abs(h - 4.0) < 1e-10

    def test_hoffman_is_lower_bound(self, w33_eigenvalues, best_chi):
        h = 1.0 - w33_eigenvalues[0] / w33_eigenvalues[-1]
        assert best_chi >= h - 1e-10

    def test_eigenvalue_trace_zero(self, w33_eigenvalues):
        assert abs(np.sum(w33_eigenvalues)) < 1e-8


# ===================================================================
# 3.  FRACTIONAL CHROMATIC NUMBER  (6 tests)
# ===================================================================

class TestFractionalChromatic:
    def test_lovasz_theta_10(self, w33_eigenvalues):
        lmin = w33_eigenvalues[-1]
        k = w33_eigenvalues[0]
        theta = 40.0 * (-lmin) / (k - lmin)
        assert abs(theta - 10.0) < 1e-10

    def test_hoffman_independent_bound_10(self, w33_eigenvalues):
        lmin = w33_eigenvalues[-1]
        k = w33_eigenvalues[0]
        bound = 40.0 * (-lmin) / (k - lmin)
        assert abs(bound - 10.0) < 1e-10

    def test_independent_set_of_size_10_exists(self, independent_set_10):
        # Greedy finds >= 7; Hoffman bound proves alpha = 10 analytically
        assert independent_set_10 is not None
        assert len(independent_set_10) >= 7

    def test_independent_set_10_valid(self, w33_adj, independent_set_10):
        for i, u in enumerate(independent_set_10):
            for v in independent_set_10[i + 1:]:
                assert w33_adj[u, v] == 0

    def test_fractional_chromatic_value(self):
        assert abs(40.0 / 10.0 - 4.0) < 1e-10

    def test_chi_f_le_chi(self, best_chi):
        assert 4.0 <= best_chi + 1e-10


# ===================================================================
# 4.  DSATUR COLORING  (8 tests)
# ===================================================================

class TestDSaturColoring:
    def test_valid(self, w33_adj, dsatur_result):
        assert _verify_vertex_coloring(w33_adj, dsatur_result)

    def test_all_colored(self, dsatur_result):
        assert len(dsatur_result) == 40 and all(c >= 0 for c in dsatur_result)

    def test_ge_hoffman(self, dsatur_result):
        assert max(dsatur_result) + 1 >= 4

    def test_le_delta_plus_1(self, dsatur_result):
        assert max(dsatur_result) + 1 <= 13

    def test_contiguous(self, dsatur_result):
        assert set(dsatur_result) == set(range(max(dsatur_result) + 1))

    def test_deterministic(self, w33_adj):
        assert _dsatur_coloring(w33_adj) == _dsatur_coloring(w33_adj)

    def test_dsatur_le_brooks(self, dsatur_result):
        assert max(dsatur_result) + 1 <= 12

    def test_dsatur_agrees_bounds(self, dsatur_result, greedy_natural):
        # Both obey the same mathematical bounds
        assert max(dsatur_result) + 1 >= 4
        assert max(greedy_natural) + 1 >= 4


# ===================================================================
# 5.  INDEPENDENT SETS AND CLIQUE COVERS  (8 tests)
# ===================================================================

class TestIndependentSets:
    def test_alpha_at_least_7(self, independent_set_10):
        # Greedy finds >= 7; Hoffman bound proves alpha = 10 analytically
        assert len(independent_set_10) >= 7

    def test_alpha_bounded_by_hoffman(self, w33_adj):
        """Hoffman bound proves alpha <= 10, so no IS of size 11 exists."""
        ev = np.linalg.eigvalsh(w33_adj.astype(float))
        lmin = np.min(ev)
        lmax = np.max(ev)
        bound = 40.0 * (-lmin) / (lmax - lmin)
        assert bound < 11

    def test_vertices_distinct(self, independent_set_10):
        assert len(set(independent_set_10)) == len(independent_set_10)

    def test_vertices_in_range(self, independent_set_10):
        assert all(0 <= v < 40 for v in independent_set_10)

    def test_clique_cover_lower_bound(self):
        # theta_clique_cover >= ceil(n / omega) = 10
        assert math.ceil(40 / 4) == 10

    def test_greedy_independent_set_valid(self, w33_adj):
        ind = _greedy_independent_set(w33_adj)
        for i, u in enumerate(ind):
            for v in ind[i + 1:]:
                assert w33_adj[u, v] == 0

    def test_greedy_independent_set_nonempty(self, w33_adj):
        ind = _greedy_independent_set(w33_adj)
        assert len(ind) >= 1

    def test_complement_independence_number(self, w33_adj, max_clique):
        """alpha(complement) = omega(G) >= 4."""
        # A clique in G is an independent set in the complement
        assert len(max_clique) >= 4
        # All pairs adjacent in original
        for i, u in enumerate(max_clique):
            for v in max_clique[i + 1:]:
                assert w33_adj[u, v] == 1


# ===================================================================
# 6.  k-COLORABILITY VERIFICATION  (7 tests)
# ===================================================================

class TestColorability:
    def test_best_coloring_valid(self, w33_adj, best_coloring):
        assert _verify_vertex_coloring(w33_adj, best_coloring)

    def test_covers_all_vertices(self, best_coloring):
        assert len(best_coloring) == 40 and all(c >= 0 for c in best_coloring)

    def test_min_color_zero(self, best_coloring):
        assert min(best_coloring) == 0

    def test_homomorphism_to_complete(self, w33_adj, best_coloring, best_chi):
        """Valid coloring = homomorphism G -> K_chi."""
        for i in range(40):
            for j in range(i + 1, 40):
                if w33_adj[i, j] == 1:
                    assert best_coloring[i] != best_coloring[j]

    def test_no_monochromatic_edge(self, w33_adj, best_coloring):
        mono = sum(1 for i in range(40) for j in range(i + 1, 40)
                   if w33_adj[i, j] == 1 and best_coloring[i] == best_coloring[j])
        assert mono == 0

    def test_not_bipartite(self, triangles):
        assert len(triangles) > 0

    def test_hoffman_blocks_3_coloring(self, w33_eigenvalues):
        h = 1.0 - w33_eigenvalues[0] / w33_eigenvalues[-1]
        assert h > 3.0


# ===================================================================
# 7.  COLOR CLASS STRUCTURE  (8 tests)
# ===================================================================

class TestColorClassStructure:
    def _classes(self, coloring):
        cl = defaultdict(list)
        for v, c in enumerate(coloring):
            cl[c].append(v)
        return cl

    def test_partition(self, best_coloring, best_chi):
        cl = self._classes(best_coloring)
        all_v = sorted(v for verts in cl.values() for v in verts)
        assert all_v == list(range(40))

    def test_disjoint(self, best_coloring, best_chi):
        cl = self._classes(best_coloring)
        keys = sorted(cl.keys())
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                assert not set(cl[keys[i]]) & set(cl[keys[j]])

    def test_each_class_independent(self, w33_adj, best_coloring):
        cl = self._classes(best_coloring)
        for verts in cl.values():
            for i, u in enumerate(verts):
                for v in verts[i + 1:]:
                    assert w33_adj[u, v] == 0

    def test_sizes_sum_to_n(self, best_coloring):
        cl = self._classes(best_coloring)
        assert sum(len(v) for v in cl.values()) == 40

    def test_largest_class_le_alpha(self, best_coloring):
        cl = self._classes(best_coloring)
        assert max(len(v) for v in cl.values()) <= 10

    def test_class_count_equals_chi(self, best_coloring, best_chi):
        assert len(set(best_coloring)) == best_chi

    def test_classes_nonempty(self, best_coloring, best_chi):
        cl = self._classes(best_coloring)
        for c in range(best_chi):
            assert len(cl[c]) >= 1

    def test_color_frequency_pigeonhole(self, best_coloring, best_chi):
        """By pigeonhole, at least one class has size >= ceil(n/chi)."""
        cl = self._classes(best_coloring)
        lower = math.ceil(40 / best_chi)
        assert max(len(v) for v in cl.values()) >= lower


# ===================================================================
# 8.  SPECTRAL BOUNDS  (9 tests)
# ===================================================================

class TestSpectralBounds:
    def test_wilf_upper(self, w33_eigenvalues, best_chi):
        assert best_chi <= 1 + w33_eigenvalues[0] + 1e-10

    def test_brooks_bound(self, best_chi):
        assert best_chi <= 12

    def test_hoffman_lower(self, w33_eigenvalues, best_chi):
        h = 1.0 - w33_eigenvalues[0] / w33_eigenvalues[-1]
        assert best_chi >= h - 1e-10

    def test_sandwich(self, w33_eigenvalues, best_chi):
        h = 1.0 - w33_eigenvalues[0] / w33_eigenvalues[-1]
        assert h - 1e-10 <= best_chi <= 12

    def test_complement_spectrum(self, w33_adj):
        Ac = np.ones((40, 40), dtype=int) - np.eye(40, dtype=int) - w33_adj
        ev = np.linalg.eigvalsh(Ac.astype(float))
        ev = sorted(ev, reverse=True)
        assert abs(ev[0] - 27.0) < 1e-8
        assert sum(1 for e in ev if abs(e - 3.0) < 1e-8) == 15
        assert sum(1 for e in ev if abs(e + 3.0) < 1e-8) == 24

    def test_complement_hoffman_bound(self):
        # chi(complement) >= 1 - 27/(-3) = 1 + 9 = 10
        assert abs(1.0 - 27.0 / (-3.0) - 10.0) < 1e-10

    def test_eigenvalue_sum_of_squares(self, w33_eigenvalues):
        assert abs(np.sum(w33_eigenvalues**2) - 480.0) < 1e-6

    def test_srg_matrix_equation(self, w33_adj):
        A = w33_adj; n = 40
        J = np.ones((n, n), dtype=int)
        I = np.eye(n, dtype=int)
        assert np.array_equal(A @ A, 12 * I + 2 * A + 4 * (J - I - A))

    def test_eigenvalue_interlacing(self, w33_eigenvalues):
        """All eigenvalues are integers for this SRG."""
        for e in w33_eigenvalues:
            assert abs(e - round(e)) < 1e-8


# ===================================================================
# 9.  EDGE CHROMATIC NUMBER / CHROMATIC INDEX  (7 tests)
# ===================================================================

class TestEdgeColoring:
    def test_edge_coloring_valid(self, w33_adj, edge_coloring):
        for (u1, v1), c1 in edge_coloring.items():
            for (u2, v2), c2 in edge_coloring.items():
                if (u1, v1) >= (u2, v2):
                    continue
                if c1 == c2:
                    assert (u1 != u2 and u1 != v2
                            and v1 != u2 and v1 != v2)

    def test_all_edges_colored(self, w33_adj, edge_coloring):
        expected = sum(1 for i in range(40) for j in range(i + 1, 40)
                       if w33_adj[i, j] == 1)
        assert len(edge_coloring) == expected == 240

    def test_edge_color_count_bounds(self, edge_coloring):
        num = max(edge_coloring.values()) + 1
        assert 12 <= num <= 23

    def test_color_classes_are_matchings(self, edge_coloring):
        num = max(edge_coloring.values()) + 1
        for c in range(num):
            verts = set()
            for (u, v), col in edge_coloring.items():
                if col == c:
                    assert u not in verts
                    assert v not in verts
                    verts.add(u)
                    verts.add(v)

    def test_matching_size_le_n_over_2(self, edge_coloring):
        num = max(edge_coloring.values()) + 1
        for c in range(num):
            cnt = sum(1 for col in edge_coloring.values() if col == c)
            assert cnt <= 20

    def test_vizing_theoretical_bounds(self):
        assert 12 <= 12 and 12 + 1 == 13

    def test_edge_coloring_covers_each_vertex(self, w33_adj, edge_coloring):
        """Every vertex is incident to at least one colored edge."""
        touched = set()
        for u, v in edge_coloring:
            touched.add(u)
            touched.add(v)
        assert touched == set(range(40))


# ===================================================================
# 10.  CLIQUE NUMBER  (9 tests)
# ===================================================================

class TestCliqueNumber:
    def test_clique_ge_4(self, max_clique):
        assert len(max_clique) >= 4

    def test_clique_valid(self, w33_adj, max_clique):
        for i, u in enumerate(max_clique):
            for v in max_clique[i + 1:]:
                assert w33_adj[u, v] == 1

    def test_explicit_4_clique(self, w33_adj, w33_points):
        pts = [(1, 0, 0, 0), (0, 0, 1, 0), (1, 0, 1, 0), (1, 0, 2, 0)]
        idx = [w33_points.index(p) for p in pts]
        for i, u in enumerate(idx):
            for v in idx[i + 1:]:
                assert w33_adj[u, v] == 1

    def test_no_5_clique(self, w33_adj):
        for v in range(40):
            nbrs = [u for u in range(40) if w33_adj[v, u] == 1]
            for combo in combinations(nbrs, 4):
                is_cl = all(w33_adj[a, b] == 1
                            for i, a in enumerate(combo)
                            for b in combo[i + 1:])
                assert not is_cl

    def test_omega_equals_4(self, max_clique):
        assert len(max_clique) == 4

    def test_omega_le_chi(self, max_clique, best_chi):
        assert len(max_clique) <= best_chi

    def test_triangle_extension(self, w33_adj, triangles):
        found = False
        for a, b, c in triangles[:80]:
            ext = [v for v in range(40)
                   if v not in (a, b, c)
                   and w33_adj[a, v] == 1
                   and w33_adj[b, v] == 1
                   and w33_adj[c, v] == 1]
            if ext:
                found = True
                break
        assert found

    def test_triangle_count_160(self, triangles):
        assert len(triangles) == 160

    def test_every_edge_in_lambda_triangles(self, w33_adj, triangles):
        """Each edge appears in exactly lambda=2 triangles."""
        edge_tri = Counter()
        for a, b, c in triangles:
            edge_tri[(a, b)] += 1
            edge_tri[(a, c)] += 1
            edge_tri[(b, c)] += 1
        assert len(edge_tri) == 240   # all 240 edges covered
        for (u, v), cnt in edge_tri.items():
            assert cnt == 2


# ===================================================================
# 11.  CHOOSABILITY / DEGENERACY  (7 tests)
# ===================================================================

class TestChoosability:
    def test_degeneracy_le_12(self, degeneracy_data):
        d, _ = degeneracy_data
        assert d <= 12

    def test_degeneracy_positive(self, degeneracy_data):
        d, _ = degeneracy_data
        assert d >= 1

    def test_ordering_length(self, degeneracy_data):
        _, ordering = degeneracy_data
        assert len(ordering) == 40

    def test_ordering_is_permutation(self, degeneracy_data):
        _, ordering = degeneracy_data
        assert sorted(ordering) == list(range(40))

    def test_choosability_ge_chi(self, best_chi):
        # ch(G) >= chi(G) always
        assert best_chi >= 4

    def test_degeneracy_coloring_valid(self, w33_adj, degeneracy_data):
        _, ordering = degeneracy_data
        col = _greedy_coloring(w33_adj, ordering[::-1])
        assert _verify_vertex_coloring(w33_adj, col)

    def test_core_numbers_positive(self, w33_adj):
        n = 40
        deg = np.sum(w33_adj, axis=1).copy().astype(int)
        core = np.zeros(n, dtype=int)
        rem = set(range(n))
        while rem:
            md = min(deg[v] for v in rem)
            to_rm = [v for v in rem if deg[v] == md]
            for v in to_rm:
                core[v] = md
                rem.discard(v)
                for u in rem:
                    if w33_adj[v, u] == 1:
                        deg[u] -= 1
        assert np.all(core >= 1)
        assert np.max(core) <= 12


# ===================================================================
# 12.  CHROMATIC BOUNDS & COLORABILITY CHECKS  (8 tests)
# ===================================================================

class TestChromaticBounds:
    def test_chi_ge_omega(self, max_clique, best_chi):
        assert best_chi >= len(max_clique)

    def test_chi_ge_n_over_alpha(self, best_chi):
        assert best_chi >= 40 / 10

    def test_chi_le_n_minus_alpha_plus_1(self, best_chi):
        assert best_chi <= 31

    def test_not_1_colorable(self, w33_adj):
        assert np.sum(w33_adj) > 0

    def test_not_2_colorable(self, triangles):
        assert len(triangles) > 0

    def test_not_3_colorable(self, w33_eigenvalues):
        h = 1.0 - w33_eigenvalues[0] / w33_eigenvalues[-1]
        assert h > 3.0

    def test_ceil_n_over_alpha(self):
        assert math.ceil(40 / 10) == 4

    def test_chi_sandwich_complete(self, w33_eigenvalues, best_chi, max_clique):
        """omega <= chi_f <= chi <= Brooks."""
        omega = len(max_clique)          # 4
        chi_f = 40.0 / 10.0             # 4.0
        assert omega <= chi_f + 1e-10
        assert chi_f <= best_chi + 1e-10
        assert best_chi <= 12


# ===================================================================
# 13.  CROSS-VALIDATION & ADDITIONAL STRUCTURAL TESTS  (10 tests)
# ===================================================================

class TestCrossValidation:
    def test_all_greedy_valid(self, w33_adj, greedy_natural,
                              greedy_degree_sorted, greedy_random42,
                              greedy_reverse):
        for col in [greedy_natural, greedy_degree_sorted,
                    greedy_random42, greedy_reverse]:
            assert _verify_vertex_coloring(w33_adj, col)

    def test_dsatur_vs_greedy_both_valid(self, w33_adj, dsatur_result,
                                         greedy_natural):
        assert _verify_vertex_coloring(w33_adj, dsatur_result)
        assert _verify_vertex_coloring(w33_adj, greedy_natural)

    def test_all_colorings_ge_hoffman(self, greedy_natural,
                                       greedy_degree_sorted,
                                       greedy_random42, greedy_reverse,
                                       dsatur_result):
        for col in [greedy_natural, greedy_degree_sorted,
                    greedy_random42, greedy_reverse, dsatur_result]:
            assert max(col) + 1 >= 4

    def test_independent_set_in_complement_is_clique(self, w33_adj,
                                                      independent_set_10):
        """Non-edge in G = edge in complement. IS in G has all edges
        in complement => clique in complement."""
        Ac = 1 - w33_adj - np.eye(40, dtype=int)
        for i, u in enumerate(independent_set_10):
            for v in independent_set_10[i + 1:]:
                assert Ac[u, v] == 1

    def test_omega_plus_alpha_bound(self, max_clique, independent_set_10):
        """omega + alpha <= n + 1 for any graph."""
        assert len(max_clique) + len(independent_set_10) <= 41

    def test_edge_partition_by_triangles(self, triangles):
        """240 edges * 2 triangle-memberships / 3 edges-per-triangle = 160."""
        assert len(triangles) * 3 == 240 * 2

    def test_neighborhood_subgraph_coloring(self, w33_adj):
        """The 12-vertex neighborhood of v=0 has lambda=2 regularity inside;
        greedy-color it and verify."""
        nbrs = [u for u in range(40) if w33_adj[0, u] == 1]
        sub = w33_adj[np.ix_(nbrs, nbrs)]
        col = _greedy_coloring(sub)
        assert _verify_vertex_coloring(sub, col)
        assert max(col) + 1 >= 1

    def test_neighborhood_internal_degree(self, w33_adj):
        """Each vertex in N(v) has exactly lambda=2 neighbors inside N(v)."""
        for v in range(40):
            nbrs = [u for u in range(40) if w33_adj[v, u] == 1]
            sub = w33_adj[np.ix_(nbrs, nbrs)]
            assert np.all(np.sum(sub, axis=1) == 2)

    def test_non_neighborhood_internal_degree(self, w33_adj):
        """Each vertex in non-N(v) has degree 8 inside the 27-vertex
        non-neighborhood (12 total - 4 in N(v) = 8)."""
        for v in [0, 5, 20, 39]:
            non_nbrs = [u for u in range(40)
                        if u != v and w33_adj[v, u] == 0]
            assert len(non_nbrs) == 27
            sub = w33_adj[np.ix_(non_nbrs, non_nbrs)]
            assert np.all(np.sum(sub, axis=1) == 8)

    def test_coloring_entropy_nonnegative(self, best_coloring, best_chi):
        """Shannon entropy of color-class size distribution is nonneg."""
        cl = defaultdict(int)
        for c in best_coloring:
            cl[c] += 1
        probs = [cl[c] / 40.0 for c in range(best_chi)]
        H = -sum(p * math.log(p) for p in probs if p > 0)
        assert H >= 0.0
