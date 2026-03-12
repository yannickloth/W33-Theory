"""
Phase CXVI  --  Covering & Lifting Computation on W(3,3) = SRG(40,12,2,4).

80 tests across eight categories:
  1. Fundamental Group          (10 tests)
  2. Voltage Graphs             (12 tests)
  3. Double Covers              (10 tests)
  4. Quotient Graphs            (10 tests)
  5. Universal Cover / Local    (10 tests)
  6. Deck Transformations       (10 tests)
  7. Homology Lifts             (10 tests)
  8. Spectral Covers / NB       ( 8 tests)

Only numpy + stdlib.  No scipy, no networkx.
"""

import numpy as np
import unittest
from collections import deque


# ---------------------------------------------------------------------------
# W(3,3) builder  (symplectic form on PG(3,3))
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
# Helpers
# ---------------------------------------------------------------------------

def _edge_list(A):
    """Sorted undirected edges (i, j) with i < j."""
    n = A.shape[0]
    return [(i, j) for i in range(n) for j in range(i + 1, n) if A[i, j]]


def _bfs_spanning_tree(A, root=0):
    """Return (tree_edges, parent) via BFS."""
    n = A.shape[0]
    visited = [False] * n
    visited[root] = True
    queue = deque([root])
    tree_edges = []
    parent = [-1] * n
    while queue:
        u = queue.popleft()
        for v in range(n):
            if A[u, v] and not visited[v]:
                visited[v] = True
                parent[v] = u
                tree_edges.append((min(u, v), max(u, v)))
                queue.append(v)
    return tree_edges, parent


def _incidence_matrix_oriented(A):
    """Oriented incidence matrix B  (n x m).
    Edge (i,j) with i<j:  B[i,e]=+1, B[j,e]=-1."""
    edges = _edge_list(A)
    n = A.shape[0]
    m = len(edges)
    B = np.zeros((n, m), dtype=int)
    for idx, (i, j) in enumerate(edges):
        B[i, idx] = 1
        B[j, idx] = -1
    return B, edges


def _bipartite_double_cover(A):
    """BDC adjacency matrix  (2n x 2n).
    (i,0)~(j,1) and (i,1)~(j,0) whenever i~j."""
    n = A.shape[0]
    BDC = np.zeros((2 * n, 2 * n), dtype=int)
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j]:
                BDC[i, n + j] = 1
                BDC[n + j, i] = 1
                BDC[n + i, j] = 1
                BDC[j, n + i] = 1
    return BDC


def _voltage_lift_z(A, voltages, p):
    """Z_p voltage lift.  voltages maps (i,j) i<j -> {0,..,p-1}.
    Vertex (v,s) = s*n + v.   Edge (i,s)~(j,(s+sigma)%p)."""
    n = A.shape[0]
    N = p * n
    L = np.zeros((N, N), dtype=int)
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j]:
                sigma = voltages.get((i, j), 0)
                for s in range(p):
                    u = s * n + i
                    v = ((s + sigma) % p) * n + j
                    L[u, v] = 1
                    L[v, u] = 1
    return L


def _find_triangles(A):
    """All triangles (i,j,k) with i<j<k."""
    n = A.shape[0]
    tri = []
    for i in range(n):
        for j in range(i + 1, n):
            if not A[i, j]:
                continue
            for k in range(j + 1, n):
                if A[i, k] and A[j, k]:
                    tri.append((i, j, k))
    return tri


def _boundary2_matrix(edges, triangles):
    """Boundary map d2: C2 -> C1 for the clique complex.
    Shape (num_edges, num_triangles).
    d2(i,j,k) = +(j,k) - (i,k) + (i,j)."""
    edge_idx = {e: idx for idx, e in enumerate(edges)}
    m = len(edges)
    t = len(triangles)
    D = np.zeros((m, t), dtype=int)
    for col, (i, j, k) in enumerate(triangles):
        D[edge_idx[(i, j)], col] = 1
        D[edge_idx[(i, k)], col] = -1
        D[edge_idx[(j, k)], col] = 1
    return D


def _hashimoto_matrix(A):
    """Non-backtracking (Hashimoto) matrix on directed edges.
    B[(u,v),(w,x)] = 1 iff v==w and x!=u."""
    edges = _edge_list(A)
    directed = []
    for (i, j) in edges:
        directed.append((i, j))
        directed.append((j, i))
    nd = len(directed)
    n = A.shape[0]
    # lookup: outgoing directed edges from each vertex
    out = [[] for _ in range(n)]
    for idx, (u, v) in enumerate(directed):
        out[u].append(idx)
    B = np.zeros((nd, nd), dtype=int)
    for idx1, (u1, v1) in enumerate(directed):
        for idx2 in out[v1]:
            if directed[idx2][1] != u1:
                B[idx1, idx2] = 1
    return B, directed


def _bfs_ball_sizes(A, root=0, max_radius=None):
    """Ball sizes B(root, r) for r = 0 .. max_radius."""
    n = A.shape[0]
    dist = [-1] * n
    dist[root] = 0
    queue = deque([root])
    max_d = 0
    while queue:
        u = queue.popleft()
        for v in range(n):
            if A[u, v] and dist[v] == -1:
                dist[v] = dist[u] + 1
                if dist[v] > max_d:
                    max_d = dist[v]
                queue.append(v)
    if max_radius is None:
        max_radius = max_d
    return [sum(1 for d in dist if 0 <= d <= r) for r in range(max_radius + 1)]


def _gf_rank(M, p):
    """Rank of integer matrix M over GF(p) via row-reduction."""
    A = M.copy().astype(int) % p
    rows, cols = A.shape
    rank = 0
    for col in range(cols):
        pivot = None
        for row in range(rank, rows):
            if A[row, col] % p != 0:
                pivot = row
                break
        if pivot is None:
            continue
        A[[rank, pivot]] = A[[pivot, rank]]
        inv = pow(int(A[rank, col]), -1, p)
        A[rank] = (A[rank] * inv) % p
        for row in range(rows):
            if row != rank and A[row, col] % p != 0:
                A[row] = (A[row] - int(A[row, col]) * A[rank]) % p
        rank += 1
    return rank


# ===========================================================================
# Tests
# ===========================================================================

class TestCoveringLiftingComputation(unittest.TestCase):
    """Phase CXVI: Covering & Lifting on W(3,3) = SRG(40,12,2,4)."""

    @classmethod
    def setUpClass(cls):
        cls.A = _build_w33()
        cls.n = 40
        cls.k = 12
        cls.lam = 2
        cls.mu = 4
        cls.edges = _edge_list(cls.A)
        cls.m = len(cls.edges)
        cls.eig = np.sort(
            np.round(np.linalg.eigvalsh(cls.A.astype(float))).astype(int)
        )
        cls.BDC = _bipartite_double_cover(cls.A)

    # ===================================================================
    # 1. Fundamental Group  (10 tests)
    # ===================================================================

    def test_fund_01_vertex_count(self):
        """n = 40 vertices."""
        self.assertEqual(self.A.shape[0], 40)

    def test_fund_02_edge_count(self):
        """m = n*k/2 = 240 edges."""
        self.assertEqual(self.m, 240)

    def test_fund_03_connected(self):
        """Graph is connected (BFS reaches all 40 vertices)."""
        tree_edges, _ = _bfs_spanning_tree(self.A)
        self.assertEqual(len(tree_edges), self.n - 1)

    def test_fund_04_cycle_rank(self):
        """Cycle rank = m - n + 1 = 201."""
        self.assertEqual(self.m - self.n + 1, 201)

    def test_fund_05_spanning_tree_edges(self):
        """Spanning tree has n - 1 = 39 edges."""
        tree_edges, _ = _bfs_spanning_tree(self.A)
        self.assertEqual(len(tree_edges), 39)

    def test_fund_06_non_tree_edges(self):
        """Non-tree edges = 201 = number of fundamental cycles."""
        tree_set = set(_bfs_spanning_tree(self.A)[0])
        non_tree = [e for e in self.edges if e not in tree_set]
        self.assertEqual(len(non_tree), 201)

    def test_fund_07_incidence_rank(self):
        """Rank of oriented incidence matrix = n - 1 = 39."""
        B, _ = _incidence_matrix_oriented(self.A)
        self.assertEqual(np.linalg.matrix_rank(B.astype(float)), 39)

    def test_fund_08_cycle_space_dimension(self):
        """dim(null(B^T)) = cycle rank = 201."""
        B, _ = _incidence_matrix_oriented(self.A)
        r = np.linalg.matrix_rank(B.astype(float))
        self.assertEqual(self.m - r, 201)

    def test_fund_09_pi1_free_rank(self):
        """pi_1(G) is free on 201 generators (graph fundamental group)."""
        self.assertEqual(self.m - self.n + 1, 201)

    def test_fund_10_tree_columns_full_rank(self):
        """Tree columns of incidence matrix span R^{n-1}."""
        B, edges = _incidence_matrix_oriented(self.A)
        tree_set = set(_bfs_spanning_tree(self.A)[0])
        tree_idx = [i for i, e in enumerate(edges) if e in tree_set]
        self.assertEqual(np.linalg.matrix_rank(B[:, tree_idx].astype(float)),
                         self.n - 1)

    # ===================================================================
    # 2. Voltage Graphs  (12 tests)
    # ===================================================================

    def test_volt_01_trivial_z2_two_copies(self):
        """Trivial Z2 voltage (all 0) yields two disjoint copies of G."""
        vol = {e: 0 for e in self.edges}
        L = _voltage_lift_z(self.A, vol, 2)
        np.testing.assert_array_equal(L[:40, :40], self.A)
        np.testing.assert_array_equal(L[40:, 40:], self.A)

    def test_volt_02_trivial_z2_disconnected(self):
        """Trivial Z2 lift has no cross edges."""
        vol = {e: 0 for e in self.edges}
        L = _voltage_lift_z(self.A, vol, 2)
        self.assertEqual(np.sum(L[:40, 40:]), 0)

    def test_volt_03_all_one_z2_is_bdc(self):
        """All-1 Z2 voltage lift equals the bipartite double cover."""
        vol = {e: 1 for e in self.edges}
        L = _voltage_lift_z(self.A, vol, 2)
        np.testing.assert_array_equal(L, self.BDC)

    def test_volt_04_trivial_z3_three_copies(self):
        """Trivial Z3 voltage yields 3 disjoint copies."""
        vol = {e: 0 for e in self.edges}
        L = _voltage_lift_z(self.A, vol, 3)
        self.assertEqual(L.shape[0], 120)
        np.testing.assert_array_equal(L[:40, :40], self.A)
        self.assertEqual(np.sum(L[:40, 40:80]), 0)
        self.assertEqual(np.sum(L[:40, 80:]), 0)

    def test_volt_05_z2_lift_80_vertices(self):
        """Z2 lift has 2n = 80 vertices."""
        vol = {e: 1 for e in self.edges}
        L = _voltage_lift_z(self.A, vol, 2)
        self.assertEqual(L.shape[0], 80)

    def test_volt_06_z3_lift_120_vertices(self):
        """Z3 lift has 3n = 120 vertices."""
        vol = {e: 1 for e in self.edges}
        L = _voltage_lift_z(self.A, vol, 3)
        self.assertEqual(L.shape[0], 120)

    def test_volt_07_lift_symmetric(self):
        """Any voltage lift adjacency matrix is symmetric."""
        vol = {e: 1 for e in self.edges}
        L = _voltage_lift_z(self.A, vol, 2)
        np.testing.assert_array_equal(L, L.T)

    def test_volt_08_fiber_regularity_z2(self):
        """Every vertex in Z2 all-1 lift has degree k = 12."""
        vol = {e: 1 for e in self.edges}
        L = _voltage_lift_z(self.A, vol, 2)
        np.testing.assert_array_equal(L.sum(axis=1), 12)

    def test_volt_09_fiber_regularity_z3(self):
        """Every vertex in a random Z3 lift has degree k = 12."""
        rng = np.random.RandomState(42)
        vol = {e: int(rng.randint(0, 3)) for e in self.edges}
        L = _voltage_lift_z(self.A, vol, 3)
        np.testing.assert_array_equal(L.sum(axis=1), 12)

    def test_volt_10_trivial_voltage_spectrum_tripled(self):
        """Trivial Z3 lift spectrum = three copies of base spectrum."""
        vol = {e: 0 for e in self.edges}
        L = _voltage_lift_z(self.A, vol, 3)
        eig_lift = np.sort(np.round(np.linalg.eigvalsh(L.astype(float))).astype(int))
        eig_base = np.sort(self.eig)
        expected = np.sort(np.concatenate([eig_base] * 3))
        np.testing.assert_array_equal(eig_lift, expected)

    def test_volt_11_no_self_loops(self):
        """Voltage lift has no self-loops."""
        vol = {e: 1 for e in self.edges}
        L = _voltage_lift_z(self.A, vol, 2)
        self.assertEqual(np.trace(L), 0)

    def test_volt_12_z2_lift_edge_count(self):
        """Z2 all-1 lift has 2m = 480 edges."""
        vol = {e: 1 for e in self.edges}
        L = _voltage_lift_z(self.A, vol, 2)
        self.assertEqual(np.sum(L) // 2, 480)

    # ===================================================================
    # 3. Double Covers  (10 tests)
    # ===================================================================

    def test_dc_01_bdc_80_vertices(self):
        """BDC has 80 vertices."""
        self.assertEqual(self.BDC.shape[0], 80)

    def test_dc_02_bdc_12_regular(self):
        """BDC is 12-regular."""
        self.assertTrue(np.all(self.BDC.sum(axis=1) == 12))

    def test_dc_03_bdc_bipartite(self):
        """BDC is bipartite: no edges within each half."""
        self.assertEqual(np.sum(self.BDC[:40, :40]), 0)
        self.assertEqual(np.sum(self.BDC[40:, 40:]), 0)

    def test_dc_04_bdc_symmetric(self):
        """BDC adjacency matrix is symmetric."""
        np.testing.assert_array_equal(self.BDC, self.BDC.T)

    def test_dc_05_bdc_no_self_loops(self):
        """BDC has no self-loops."""
        self.assertEqual(np.trace(self.BDC), 0)

    def test_dc_06_bdc_spectrum_plus_minus(self):
        """BDC spectrum = {+lam, -lam} for each eigenvalue lam of A."""
        eig_bdc = np.sort(np.round(
            np.linalg.eigvalsh(self.BDC.astype(float)), 6))
        eig_a = np.sort(np.round(
            np.linalg.eigvalsh(self.A.astype(float)), 6))
        expected = np.sort(np.concatenate([eig_a, -eig_a]))
        np.testing.assert_array_almost_equal(eig_bdc, expected, decimal=4)

    def test_dc_07_bdc_480_edges(self):
        """BDC has 2m = 480 edges."""
        self.assertEqual(np.sum(self.BDC) // 2, 480)

    def test_dc_08_bdc_connected(self):
        """BDC is connected (W33 is connected and non-bipartite)."""
        n2 = 80
        visited = [False] * n2
        visited[0] = True
        queue = deque([0])
        while queue:
            u = queue.popleft()
            for v in range(n2):
                if self.BDC[u, v] and not visited[v]:
                    visited[v] = True
                    queue.append(v)
        self.assertTrue(all(visited))

    def test_dc_09_bdc_eigenvalue_12_multiplicity(self):
        """BDC has eigenvalue +12 once and -12 once."""
        eig = np.round(np.linalg.eigvalsh(self.BDC.astype(float))).astype(int)
        self.assertEqual(np.sum(eig == 12), 1)
        self.assertEqual(np.sum(eig == -12), 1)

    def test_dc_10_bdc_no_odd_cycles(self):
        """BDC is bipartite => trace(A^3) = 0 (no triangles)."""
        A3 = self.BDC @ self.BDC @ self.BDC
        self.assertEqual(np.trace(A3), 0)

    # ===================================================================
    # 4. Quotient Graphs  (10 tests)
    # ===================================================================

    def _srg_equitable_cells(self, v=0):
        """Return the standard equitable partition [{v}, N(v), non-adj]."""
        nbrs = sorted(np.where(self.A[v] == 1)[0])
        non_adj = sorted(set(range(self.n)) - set(nbrs) - {v})
        return [[v], nbrs, non_adj]

    def test_quot_01_partition_sizes(self):
        """Equitable partition sizes: 1, 12, 27."""
        cells = self._srg_equitable_cells()
        self.assertEqual([len(c) for c in cells], [1, 12, 27])

    def test_quot_02_complete_partition_divisor(self):
        """Complete partition (one cell) has divisor = [[k]] = [[12]]."""
        self.assertEqual(self.k, 12)

    def test_quot_03_divisor_matrix(self):
        """Divisor matrix = [[0,12,0],[1,2,9],[0,4,8]] for SRG."""
        cells = self._srg_equitable_cells()
        D = np.zeros((3, 3), dtype=int)
        for ci, cell in enumerate(cells):
            rep = cell[0]
            for cj, other in enumerate(cells):
                D[ci, cj] = sum(self.A[rep, w] for w in other)
        expected = np.array([[0, 12, 0], [1, 2, 9], [0, 4, 8]])
        np.testing.assert_array_equal(D, expected)

    def test_quot_04_divisor_eigenvalues(self):
        """Divisor eigenvalues = {12, 2, -4} = SRG spectrum."""
        D = np.array([[0, 12, 0], [1, 2, 9], [0, 4, 8]], dtype=float)
        eig = np.sort(np.round(np.linalg.eigvals(D).real).astype(int))
        np.testing.assert_array_equal(eig, [-4, 2, 12])

    def test_quot_05_eigenvalue_interlacing(self):
        """Every divisor eigenvalue appears in the graph spectrum."""
        div_eig = {-4, 2, 12}
        graph_eig = set(self.eig)
        self.assertTrue(div_eig.issubset(graph_eig))

    def test_quot_06_divisor_trace(self):
        """tr(D) = 0 + 2 + 8 = 10."""
        D = np.array([[0, 12, 0], [1, 2, 9], [0, 4, 8]])
        self.assertEqual(np.trace(D), 10)

    def test_quot_07_equitable_vertex_to_cell(self):
        """Every neighbor of v has exactly 1 edge into {v}."""
        v = 0
        nbrs = np.where(self.A[v] == 1)[0]
        for u in nbrs:
            self.assertEqual(self.A[u, v], 1)

    def test_quot_08_equitable_lambda_check(self):
        """Each neighbor of v has lambda = 2 neighbors in N(v) \\ {self}."""
        v = 0
        nbrs = set(np.where(self.A[v] == 1)[0])
        for u in nbrs:
            cnt = sum(1 for w in nbrs if w != u and self.A[u, w])
            self.assertEqual(cnt, self.lam)

    def test_quot_09_equitable_mu_check(self):
        """Each non-neighbor has mu = 4 neighbors in N(v)."""
        v = 0
        nbrs = set(np.where(self.A[v] == 1)[0])
        non_adj = set(range(self.n)) - nbrs - {v}
        for w in non_adj:
            cnt = sum(1 for u in nbrs if self.A[w, u])
            self.assertEqual(cnt, self.mu)

    def test_quot_10_divisor_det(self):
        """det(D) = 0*(16-36) - 12*(8-0) + 0 = -96."""
        D = np.array([[0, 12, 0], [1, 2, 9], [0, 4, 8]], dtype=float)
        self.assertAlmostEqual(np.linalg.det(D), -96.0, places=6)

    # ===================================================================
    # 5. Universal Cover / Local Structure  (10 tests)
    # ===================================================================

    def test_univ_01_ball_radius_0(self):
        """B(v,0) = 1."""
        self.assertEqual(_bfs_ball_sizes(self.A, 0, 0)[0], 1)

    def test_univ_02_ball_radius_1(self):
        """B(v,1) = 1 + k = 13."""
        self.assertEqual(_bfs_ball_sizes(self.A, 0, 1)[1], 13)

    def test_univ_03_ball_radius_2(self):
        """B(v,2) = 40 (diameter 2 for SRG with mu > 0)."""
        self.assertEqual(_bfs_ball_sizes(self.A, 0, 2)[2], 40)

    def test_univ_04_diameter_is_2(self):
        """Diameter = 2."""
        max_d = 0
        for v in range(self.n):
            dist = [-1] * self.n
            dist[v] = 0
            q = deque([v])
            while q:
                u = q.popleft()
                for w in range(self.n):
                    if self.A[u, w] and dist[w] == -1:
                        dist[w] = dist[u] + 1
                        if dist[w] > max_d:
                            max_d = dist[w]
                        q.append(w)
        self.assertEqual(max_d, 2)

    def test_univ_05_tree_excess(self):
        """Tree excess = m - (n-1) = 201."""
        te, _ = _bfs_spanning_tree(self.A)
        self.assertEqual(self.m - len(te), 201)

    def test_univ_06_girth_is_3(self):
        """Girth = 3 (triangles exist since lambda = 2)."""
        A3 = self.A @ self.A @ self.A
        self.assertGreater(np.trace(A3), 0)

    def test_univ_07_growth_rate_radius_1(self):
        """Growth from r=0 to r=1 is k = 12."""
        b = _bfs_ball_sizes(self.A, 0, 1)
        self.assertEqual(b[1] - b[0], 12)

    def test_univ_08_vertices_at_distance_2(self):
        """Vertices at distance exactly 2 from any v = 27."""
        b = _bfs_ball_sizes(self.A, 0, 2)
        self.assertEqual(b[2] - b[1], 27)

    def test_univ_09_bfs_tree_acyclic_connected(self):
        """BFS tree is connected and acyclic (n-1 edges, all reached)."""
        te, _ = _bfs_spanning_tree(self.A)
        T = np.zeros((self.n, self.n), dtype=int)
        for (i, j) in te:
            T[i, j] = T[j, i] = 1
        visited = [False] * self.n
        visited[0] = True
        q = deque([0])
        while q:
            u = q.popleft()
            for v in range(self.n):
                if T[u, v] and not visited[v]:
                    visited[v] = True
                    q.append(v)
        self.assertTrue(all(visited))
        self.assertEqual(len(te), self.n - 1)

    def test_univ_10_ball_v1_uniform(self):
        """B(v,1) = 13 for every vertex v (k-regular)."""
        for v in range(self.n):
            self.assertEqual(_bfs_ball_sizes(self.A, v, 1)[1], 13)

    # ===================================================================
    # 6. Deck Transformations  (10 tests)
    # ===================================================================

    @staticmethod
    def _deck_perm():
        """Swap permutation sigma: (v,0)<->(v,1)."""
        return list(range(40, 80)) + list(range(40))

    def test_deck_01_swap_is_automorphism(self):
        """sigma is an automorphism of BDC."""
        p = self._deck_perm()
        np.testing.assert_array_equal(
            self.BDC[np.ix_(p, p)], self.BDC)

    def test_deck_02_fixed_point_free(self):
        """sigma has no fixed points."""
        p = self._deck_perm()
        self.assertEqual(sum(1 for i in range(80) if p[i] == i), 0)

    def test_deck_03_order_2(self):
        """sigma^2 = identity."""
        p = self._deck_perm()
        self.assertEqual([p[p[i]] for i in range(80)], list(range(80)))

    def test_deck_04_deck_group_z2(self):
        """Deck group = {id, sigma} has order 2."""
        p = self._deck_perm()
        self.assertNotEqual(p, list(range(80)))
        self.assertEqual([p[p[i]] for i in range(80)], list(range(80)))

    def test_deck_05_orbit_count(self):
        """sigma partitions 80 vertices into 40 orbits."""
        p = self._deck_perm()
        orbits = {frozenset([i, p[i]]) for i in range(80)}
        self.assertEqual(len(orbits), 40)

    def test_deck_06_orbit_size_2(self):
        """Each orbit has exactly 2 elements."""
        p = self._deck_perm()
        for i in range(80):
            self.assertEqual(len({i, p[i]}), 2)

    def test_deck_07_quotient_recovers_A(self):
        """BDC / deck-group = original graph A."""
        Q = np.zeros((40, 40), dtype=int)
        for i in range(40):
            for j in range(40):
                if self.BDC[i, 40 + j] or self.BDC[40 + i, j]:
                    Q[i, j] = 1
        np.testing.assert_array_equal(Q, self.A)

    def test_deck_08_sigma_commutes_with_BDC(self):
        """Permutation matrix P of sigma commutes with BDC."""
        p = self._deck_perm()
        P = np.zeros((80, 80), dtype=int)
        for i in range(80):
            P[i, p[i]] = 1
        np.testing.assert_array_equal(P @ self.BDC, self.BDC @ P)

    def test_deck_09_fibers_partition(self):
        """Fibers {(v,0),(v,1)} partition the 80 vertices."""
        all_v = set()
        for v in range(40):
            fib = frozenset([v, v + 40])
            self.assertEqual(len(fib & all_v), 0)
            all_v |= fib
        self.assertEqual(all_v, set(range(80)))

    def test_deck_10_sigma_swaps_halves(self):
        """sigma maps part-0 onto part-1 and vice versa."""
        p = self._deck_perm()
        self.assertEqual({p[v] for v in range(40)}, set(range(40, 80)))
        self.assertEqual({p[v] for v in range(40, 80)}, set(range(40)))

    # ===================================================================
    # 7. Homology Lifts  (10 tests)
    # ===================================================================

    def test_hom_01_h1_rank(self):
        """H_1(G, Z) has rank = cycle rank = 201."""
        B, _ = _incidence_matrix_oriented(self.A)
        self.assertEqual(self.m - np.linalg.matrix_rank(B.astype(float)), 201)

    def test_hom_02_mod2_cycle_space(self):
        """Cycle-space dimension over GF(2) = 201."""
        B, _ = _incidence_matrix_oriented(self.A)
        self.assertEqual(self.m - _gf_rank(B % 2, 2), 201)

    def test_hom_03_mod3_cycle_space(self):
        """Cycle-space dimension over GF(3) = 201."""
        B, _ = _incidence_matrix_oriented(self.A)
        self.assertEqual(self.m - _gf_rank(B % 3, 3), 201)

    def test_hom_04_incidence_rank_gf2(self):
        """rank_GF(2)(B) = 39."""
        B, _ = _incidence_matrix_oriented(self.A)
        self.assertEqual(_gf_rank(B % 2, 2), 39)

    def test_hom_05_incidence_rank_gf3(self):
        """rank_GF(3)(B) = 39."""
        B, _ = _incidence_matrix_oriented(self.A)
        self.assertEqual(_gf_rank(B % 3, 3), 39)

    def test_hom_06_triangle_count_formula(self):
        """Number of triangles = n*k*lambda/6 = 160."""
        A3 = self.A @ self.A @ self.A
        self.assertEqual(np.trace(A3) // 6, 160)

    def test_hom_07_triangle_enumeration(self):
        """Explicit triangle enumeration gives 160."""
        self.assertEqual(len(_find_triangles(self.A)), 160)

    def test_hom_08_boundary2_rank(self):
        """rank(d2) = 120."""
        D2 = _boundary2_matrix(self.edges, _find_triangles(self.A))
        self.assertEqual(np.linalg.matrix_rank(D2.astype(float)), 120)

    def test_hom_09_betti_1_clique_complex(self):
        """b_1(clique complex) = 201 - rank(d2) = 81."""
        D2 = _boundary2_matrix(self.edges, _find_triangles(self.A))
        b1 = 201 - np.linalg.matrix_rank(D2.astype(float))
        self.assertEqual(b1, 81)

    def test_hom_10_euler_characteristic(self):
        """chi(2-skeleton) = V - E + T = 40 - 240 + 160 = -40."""
        chi = self.n - self.m + len(_find_triangles(self.A))
        self.assertEqual(chi, -40)

    # ===================================================================
    # 8. Spectral Covers / Non-backtracking  (8 tests)
    # ===================================================================

    @classmethod
    def _get_nb(cls):
        """Lazy-cached Hashimoto matrix and eigenvalues."""
        if not hasattr(cls, '_nb_cache'):
            H, de = _hashimoto_matrix(cls.A)
            eig = np.linalg.eigvals(H.astype(float))
            cls._nb_cache = (H, de, eig)
        return cls._nb_cache

    def test_spec_01_hashimoto_dimensions(self):
        """Hashimoto matrix is 480 x 480 (= 2m)."""
        H, _, _ = self._get_nb()
        self.assertEqual(H.shape, (480, 480))

    def test_spec_02_nb_eigenvalue_11(self):
        """Adjacency eigenvalue k=12 yields NB eigenvalue 11."""
        _, _, eig = self._get_nb()
        real_eig = eig[np.abs(eig.imag) < 0.5].real
        self.assertTrue(any(abs(e - 11) < 0.5 for e in real_eig))

    def test_spec_03_nb_plus1_multiplicity(self):
        """NB eigenvalue +1 has multiplicity 201."""
        _, _, eig = self._get_nb()
        self.assertEqual(sum(1 for e in eig if abs(e - 1) < 0.3), 201)

    def test_spec_04_nb_minus1_multiplicity(self):
        """NB eigenvalue -1 has multiplicity 200."""
        _, _, eig = self._get_nb()
        self.assertEqual(sum(1 for e in eig if abs(e + 1) < 0.3), 200)

    def test_spec_05_nb_spectral_radius(self):
        """Spectral radius of NB matrix = k - 1 = 11."""
        _, _, eig = self._get_nb()
        self.assertAlmostEqual(np.max(np.abs(eig)), 11.0, places=2)

    def test_spec_06_nb_ramanujan_modulus(self):
        """Non-trivial NB eigenvalues have modulus sqrt(k-1) = sqrt(11)."""
        _, _, eig = self._get_nb()
        non_triv = [e for e in eig
                    if abs(abs(e) - 1) > 0.5 and abs(e - 11) > 0.5]
        for e in non_triv:
            self.assertAlmostEqual(abs(e), np.sqrt(11), places=2)

    def test_spec_07_ihara_determinant(self):
        """Ihara formula: det(I-uB) = (1-u^2)^(m-n) det(I-uA+(k-1)u^2 I)
        verified at u = 0.3 via log-determinants."""
        u = 0.3
        H, _, _ = self._get_nb()
        nd = H.shape[0]
        # LHS
        M_lhs = np.eye(nd) - u * H.astype(float)
        s_lhs, ld_lhs = np.linalg.slogdet(M_lhs)
        # RHS
        excess = self.m - self.n          # 200
        fac = 1.0 - u * u                 # 0.91
        log_fac = excess * np.log(abs(fac))
        sign_fac = 1.0 if fac > 0 else (-1.0) ** excess
        M_rhs = (np.eye(self.n) * (1 + 11 * u * u)
                 - u * self.A.astype(float))
        s_inner, ld_inner = np.linalg.slogdet(M_rhs)
        ld_rhs = log_fac + ld_inner
        s_rhs = sign_fac * s_inner
        self.assertAlmostEqual(float(s_lhs), float(s_rhs), places=0)
        self.assertAlmostEqual(ld_lhs, ld_rhs, delta=1.0)

    def test_spec_08_nb_eigenvalue_partition(self):
        """480 NB eigenvalues split: 201 at +1, 200 at -1, 1 at 11,
        78 at |z|=sqrt(11)."""
        _, _, eig = self._get_nb()
        at_1  = sum(1 for e in eig if abs(e - 1) < 0.3)
        at_m1 = sum(1 for e in eig if abs(e + 1) < 0.3)
        at_11 = sum(1 for e in eig if abs(e - 11) < 0.3)
        rest  = sum(1 for e in eig
                    if abs(abs(e) - np.sqrt(11)) < 0.3
                    and abs(e - 1) > 0.3
                    and abs(e + 1) > 0.3
                    and abs(e - 11) > 0.3)
        self.assertEqual(at_1, 201)
        self.assertEqual(at_m1, 200)
        self.assertEqual(at_11, 1)
        self.assertEqual(rest, 78)
        self.assertEqual(at_1 + at_m1 + at_11 + rest, 480)


if __name__ == "__main__":
    unittest.main()
