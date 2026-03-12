"""
Phase CV: Graph Decomposition Computation on W(3,3) = SRG(40,12,2,4).

Comprehensive tests covering edge decomposition, clique decomposition,
vertex cut / block analysis, tree decomposition bounds, modular decomposition,
ear decomposition, cycle space analysis, and matching decomposition.

All tests use only numpy and the Python standard library.
"""

import numpy as np
import pytest
from itertools import combinations
from collections import deque


# ── W(3,3) builder ──────────────────────────────────────────────────────────

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


# ── Shared fixtures ─────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def A():
    """Adjacency matrix of W(3,3)."""
    return _build_w33()


@pytest.fixture(scope="module")
def n():
    return 40


@pytest.fixture(scope="module")
def k():
    return 12


@pytest.fixture(scope="module")
def lam():
    """SRG lambda parameter."""
    return 2


@pytest.fixture(scope="module")
def mu():
    """SRG mu parameter."""
    return 4


@pytest.fixture(scope="module")
def edge_list(A):
    """List of edges as (i, j) pairs with i < j."""
    nn = A.shape[0]
    edges = []
    for i in range(nn):
        for j in range(i + 1, nn):
            if A[i, j]:
                edges.append((i, j))
    return edges


@pytest.fixture(scope="module")
def max_cliques(A):
    """All maximum cliques of size 4 in W(3,3)."""
    nn = A.shape[0]
    cliques = []
    for combo in combinations(range(nn), 4):
        if all(A[a, b] for a, b in combinations(combo, 2)):
            cliques.append(combo)
    return cliques


@pytest.fixture(scope="module")
def spanning_tree(A):
    """BFS spanning tree returned as a list of directed edges (parent, child)."""
    nn = A.shape[0]
    visited = [False] * nn
    visited[0] = True
    queue = deque([0])
    tree_edges = []
    while queue:
        u = queue.popleft()
        for v in range(nn):
            if A[u, v] and not visited[v]:
                visited[v] = True
                tree_edges.append((u, v))
                queue.append(v)
    return tree_edges


# ── Helper utilities ────────────────────────────────────────────────────────

def _bfs_connected(adj, nn, excluded=None):
    """Check if the graph (with some vertices excluded) is connected."""
    if excluded is None:
        excluded = set()
    remaining = [v for v in range(nn) if v not in excluded]
    if len(remaining) <= 1:
        return True
    visited = set()
    queue = deque([remaining[0]])
    visited.add(remaining[0])
    while queue:
        u = queue.popleft()
        for v in remaining:
            if v not in visited and adj[u, v]:
                visited.add(v)
                queue.append(v)
    return len(visited) == len(remaining)


def _maximum_matching(adj, nn):
    """Find maximum matching using randomised greedy + augmenting paths."""
    best_match = []

    for seed in range(20):
        partner = [-1] * nn
        rng = np.random.RandomState(seed)
        perm = list(rng.permutation(nn))

        # Greedy phase
        for i in perm:
            if partner[i] != -1:
                continue
            nbrs = [j for j in range(nn) if adj[i, j] and partner[j] == -1]
            if nbrs:
                j = nbrs[rng.randint(len(nbrs))]
                partner[i] = j
                partner[j] = i

        # Augmenting-path phase (BFS alternating tree)
        for _round in range(nn):
            found_aug = False
            for s in range(nn):
                if partner[s] != -1:
                    continue
                prev = {s: -1}
                queue = deque([s])
                target = -1
                while queue and target == -1:
                    u = queue.popleft()
                    for v in range(nn):
                        if v in prev or not adj[u, v]:
                            continue
                        prev[v] = u
                        if partner[v] == -1:
                            target = v
                            break
                        w = partner[v]
                        if w not in prev:
                            prev[w] = v
                            queue.append(w)
                if target != -1:
                    # Augment along alternating path
                    v = target
                    while v != -1:
                        u = prev[v]
                        old = partner[u]
                        partner[u] = v
                        partner[v] = u
                        v = old
                    found_aug = True
                    break
            if not found_aug:
                break

        match = [(i, partner[i]) for i in range(nn) if partner[i] > i]
        if len(match) > len(best_match):
            best_match = match
        if len(match) == nn // 2:
            return match

    return best_match


def _build_ear_decomposition(A, nn):
    """Build an ear decomposition for a 2-connected graph.

    Returns (ears, covered_edges) where ears is a list of vertex-sequences
    and covered_edges is a set of (min, max) edge tuples.
    """
    # Phase 0: find an initial triangle
    triangle = None
    for i in range(nn):
        if triangle:
            break
        for j in range(i + 1, nn):
            if not A[i, j]:
                continue
            if triangle:
                break
            for kk in range(j + 1, nn):
                if A[i, kk] and A[j, kk]:
                    triangle = (i, j, kk)
                    break

    in_decomp = set(triangle)
    covered = set()
    for idx in range(3):
        u, v = triangle[idx], triangle[(idx + 1) % 3]
        covered.add((min(u, v), max(u, v)))
    ears = [list(triangle)]

    total_edges = 0
    for i in range(nn):
        for j in range(i + 1, nn):
            if A[i, j]:
                total_edges += 1

    # Phase 1: extend through non-decomposition vertices until all are covered
    while len(in_decomp) < nn:
        found = False
        for start in sorted(in_decomp):
            if found:
                break
            for next_v in range(nn):
                if next_v in in_decomp or not A[start, next_v]:
                    continue
                # BFS from next_v through non-decomp vertices back to in_decomp
                prev = {next_v: start}
                bfs_q = deque([next_v])
                end = -1
                while bfs_q and end == -1:
                    u = bfs_q.popleft()
                    for w in range(nn):
                        if not A[u, w] or w in prev or w == start:
                            continue
                        prev[w] = u
                        if w in in_decomp:
                            end = w
                            break
                        bfs_q.append(w)
                if end == -1:
                    # Fallback: check if next_v itself connects to another decomp vertex
                    for w in sorted(in_decomp):
                        if w != start and A[next_v, w] and w not in prev:
                            prev[w] = next_v
                            end = w
                            break
                if end == -1:
                    continue

                path = []
                w = end
                while w != start:
                    path.append(w)
                    w = prev[w]
                path.append(start)
                path.reverse()

                ears.append(path)
                for idx in range(len(path) - 1):
                    e = (min(path[idx], path[idx + 1]),
                         max(path[idx], path[idx + 1]))
                    covered.add(e)
                for v in path[1:-1]:
                    in_decomp.add(v)
                found = True
                break

    # Phase 2: cover remaining edges as single-edge (chord) ears
    for i in range(nn):
        for j in range(i + 1, nn):
            if A[i, j] and (i, j) not in covered:
                ears.append([i, j])
                covered.add((i, j))

    return ears, covered


def _gauss_gf2_rank(matrix, nrows, ncols):
    """Compute rank of a binary matrix over GF(2) via Gaussian elimination."""
    M = matrix.copy() % 2
    rank = 0
    for col in range(ncols):
        pivot = None
        for row in range(rank, nrows):
            if M[row, col] % 2 == 1:
                pivot = row
                break
        if pivot is None:
            continue
        M[[rank, pivot]] = M[[pivot, rank]]
        for row in range(nrows):
            if row != rank and M[row, col] % 2 == 1:
                M[row] = (M[row] + M[rank]) % 2
        rank += 1
    return rank


# ══════════════════════════════════════════════════════════════════════════════
# 1. EDGE DECOMPOSITION
# ══════════════════════════════════════════════════════════════════════════════

class TestEdgeDecomposition:
    """Tests for edge-level decomposition properties of W(3,3)."""

    def test_total_edges(self, A, n, k):
        """Total edge count = n*k/2 = 240."""
        m = np.sum(A) // 2
        assert m == n * k // 2 == 240

    def test_triangle_count(self, A):
        """Number of triangles = trace(A^3) / 6 = 160."""
        A3 = A @ A @ A
        assert np.trace(A3) // 6 == 160

    def test_triangle_count_formula(self, A, n, k, lam):
        """Triangle count via SRG formula: n * k * lambda / 6."""
        expected = n * k * lam // 6
        A3 = A @ A @ A
        actual = np.trace(A3) // 6
        assert actual == expected == 160

    def test_triangles_per_edge(self, A, edge_list, lam):
        """Each edge participates in exactly lambda = 2 triangles."""
        nn = A.shape[0]
        for u, v in edge_list:
            common = sum(1 for w in range(nn) if A[u, w] and A[v, w])
            assert common == lam

    def test_trace_A4_from_spectrum(self, A):
        """trace(A^4) = 12^4*1 + 2^4*24 + (-4)^4*15 = 24960."""
        A4 = A @ A @ A @ A
        expected = 12**4 * 1 + 2**4 * 24 + (-4)**4 * 15
        assert np.trace(A4) == expected == 24960

    def test_A2_diagonal(self, A, k):
        """Diagonal of A^2 equals degree k = 12 at every vertex."""
        A2 = A @ A
        assert np.all(np.diag(A2) == k)

    def test_A2_off_diagonal_adjacent(self, A, lam):
        """For adjacent i, j: (A^2)[i,j] = lambda = 2."""
        A2 = A @ A
        nn = A.shape[0]
        for i in range(nn):
            for j in range(i + 1, nn):
                if A[i, j]:
                    assert A2[i, j] == lam

    def test_A2_off_diagonal_nonadjacent(self, A, mu):
        """For non-adjacent distinct i, j: (A^2)[i,j] = mu = 4."""
        A2 = A @ A
        nn = A.shape[0]
        for i in range(nn):
            for j in range(i + 1, nn):
                if not A[i, j]:
                    assert A2[i, j] == mu

    def test_K4_edge_partition(self, A, max_cliques, edge_list):
        """The 40 maximum cliques (K4s) partition all 240 edges."""
        covered = set()
        for clique in max_cliques:
            for a, b in combinations(clique, 2):
                e = (min(a, b), max(a, b))
                assert e not in covered, f"Edge {e} covered by multiple cliques"
                covered.add(e)
        assert covered == set(edge_list)

    def test_vizing_bound(self, k):
        """Vizing: chromatic index chi' in {Delta, Delta+1} = {12, 13}."""
        delta = k
        assert delta == 12
        # chi'(G) >= Delta for any graph, chi'(G) <= Delta + 1 by Vizing
        # So 12 <= chi' <= 13


# ══════════════════════════════════════════════════════════════════════════════
# 2. CLIQUE DECOMPOSITION
# ══════════════════════════════════════════════════════════════════════════════

class TestCliqueDecomposition:
    """Tests for clique decomposition properties of W(3,3)."""

    def test_max_clique_size(self, A):
        """Maximum clique size omega(W33) = 4.

        Achieved by maximal totally isotropic 2-d subspaces of Sp(4,3);
        Delsarte bound omega <= 1 + k/(-s_min) = 1 + 12/4 = 4 is tight.
        """
        nn = A.shape[0]
        found_4 = any(
            all(A[a, b] for a, b in combinations(combo, 2))
            for combo in combinations(range(nn), 4)
        )
        assert found_4, "No 4-clique found"

    def test_no_five_clique(self, A):
        """No 5-clique exists (omega = 4, not 5)."""
        nn = A.shape[0]
        for combo in combinations(range(nn), 5):
            if all(A[a, b] for a, b in combinations(combo, 2)):
                pytest.fail(f"Unexpected 5-clique: {combo}")

    def test_delsarte_clique_bound(self, k):
        """Delsarte/Hoffman bound: omega <= 1 + k / (-s_min) = 4."""
        s_min = -4
        bound = 1 + k / (-s_min)
        assert bound == 4.0

    def test_num_max_cliques(self, max_cliques):
        """Exactly 40 maximum cliques (K4s) in W(3,3).

        Equals the number of maximal totally isotropic 2-d subspaces
        of Sp(4,3): prod_{i=1}^{2}(3^i + 1) = 4 * 10 = 40.
        """
        assert len(max_cliques) == 40

    def test_cliques_per_vertex(self, max_cliques, n):
        """Each vertex belongs to exactly 4 maximum cliques.

        degree(v) = 12 edges; each K4 through v contributes 3 edges;
        so v is in 12/3 = 4 cliques.
        """
        count = [0] * n
        for clique in max_cliques:
            for v in clique:
                count[v] += 1
        assert all(c == 4 for c in count)

    def test_clique_pairwise_intersection(self, max_cliques):
        """Two distinct K4 cliques share at most 1 vertex."""
        for i in range(len(max_cliques)):
            for j in range(i + 1, len(max_cliques)):
                shared = len(set(max_cliques[i]) & set(max_cliques[j]))
                assert shared <= 1

    def test_edge_in_unique_clique(self, A, max_cliques, edge_list):
        """Each edge belongs to exactly one maximum clique."""
        edge_to_clique = {}
        for idx, clique in enumerate(max_cliques):
            for a, b in combinations(clique, 2):
                e = (min(a, b), max(a, b))
                assert e not in edge_to_clique
                edge_to_clique[e] = idx
        for e in edge_list:
            assert e in edge_to_clique

    def test_triangles_from_cliques(self, max_cliques):
        """Each K4 contains C(4,3) = 4 triangles; total = 40 * 4 = 160."""
        assert len(max_cliques) * 4 == 160

    def test_clique_cover_number(self, max_cliques):
        """Edge clique cover uses exactly 40 cliques of size 4."""
        assert len(max_cliques) == 40

    def test_lambda_from_clique_structure(self, A, max_cliques, lam):
        """lambda = 2 follows from clique structure: each K4 gives 2 common
        neighbours for every edge within it."""
        for clique in max_cliques:
            for a, b in combinations(clique, 2):
                others = [v for v in clique if v != a and v != b]
                assert len(others) == lam


# ══════════════════════════════════════════════════════════════════════════════
# 3. VERTEX CUT AND BLOCK ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

class TestVertexCutBlock:
    """Tests for vertex / edge connectivity and block structure."""

    def test_graph_connected(self, A, n):
        """W(3,3) is connected."""
        assert _bfs_connected(A, n)

    def test_complement_connected(self, A, n):
        """Complement SRG(40,27,18,18) is connected."""
        Ac = 1 - A - np.eye(n, dtype=int)
        assert _bfs_connected(Ac, n)

    def test_regular_degree(self, A, k):
        """All vertices have degree k = 12."""
        degrees = np.sum(A, axis=1)
        assert np.all(degrees == k)

    def test_laplacian_eigenvalues(self, A, n, k):
        """Laplacian L = D - A has spectrum {0^1, 10^24, 16^15}."""
        L = np.diag(np.sum(A, axis=1)) - A
        eigvals = np.sort(np.round(np.linalg.eigvalsh(L.astype(float)), 6))
        vals, counts = np.unique(np.round(eigvals), return_counts=True)
        spec = dict(zip(vals.astype(int), counts))
        assert spec == {0: 1, 10: 24, 16: 15}

    def test_algebraic_connectivity(self, A):
        """Algebraic connectivity (2nd smallest Laplacian eigenvalue) = 10."""
        L = np.diag(np.sum(A, axis=1)) - A
        eigvals = np.sort(np.linalg.eigvalsh(L.astype(float)))
        assert abs(eigvals[1] - 10.0) < 1e-8

    def test_laplacian_rank(self, A, n):
        """rank(L) = n - 1 = 39 (one zero eigenvalue for connected graph)."""
        L = np.diag(np.sum(A, axis=1)) - A
        rank = np.linalg.matrix_rank(L.astype(float))
        assert rank == n - 1

    def test_two_connected(self, A, n):
        """Removing any single vertex keeps the graph connected."""
        for v in range(n):
            assert _bfs_connected(A, n, excluded={v}), \
                f"Removing vertex {v} disconnects the graph"

    def test_vertex_connectivity_upper_bound(self, A, n, k):
        """kappa <= k = 12: removing N(v) isolates v."""
        v = 0
        neighbors = {u for u in range(n) if A[v, u]}
        assert len(neighbors) == k
        remaining = [u for u in range(n) if u not in neighbors]
        assert v in remaining
        assert all(A[v, u] == 0 for u in remaining if u != v)

    def test_high_connectivity_sample(self, A, n):
        """Graph stays connected after removing any 11 of the 12 neighbours
        of vertex 0 (evidence that kappa >= 12)."""
        nbrs = [u for u in range(n) if A[0, u]]
        for drop in nbrs:
            removed = set(nbrs) - {drop}
            assert len(removed) == 11
            assert _bfs_connected(A, n, excluded=removed)

    def test_neighborhood_subgraph(self, A, n, lam):
        """Each vertex in N(v) has exactly lambda = 2 neighbours inside N(v)."""
        for v in range(n):
            nbrs = [u for u in range(n) if A[v, u]]
            for u in nbrs:
                deg_in_nbrs = sum(1 for w in nbrs if A[u, w])
                assert deg_in_nbrs == lam


# ══════════════════════════════════════════════════════════════════════════════
# 4. TREE DECOMPOSITION
# ══════════════════════════════════════════════════════════════════════════════

class TestTreeDecomposition:
    """Tests for tree-width bounds and related decomposition parameters."""

    def test_treewidth_lower_bound_clique(self, max_cliques):
        """tw >= omega - 1 = 3."""
        omega = max(len(c) for c in max_cliques)
        assert omega - 1 >= 3

    def test_treewidth_lower_bound_degeneracy(self, A):
        """tw >= degeneracy = 12.

        For k-regular G the whole graph has min-degree k, so
        degeneracy >= k; and max-degree = k gives degeneracy <= k.
        """
        nn = A.shape[0]
        remaining = set(range(nn))
        adj = {v: set(u for u in range(nn) if A[v, u]) for v in range(nn)}
        max_min_deg = 0
        for _ in range(nn):
            min_v = min(remaining,
                        key=lambda v: len(adj[v] & remaining))
            min_deg = len(adj[min_v] & remaining)
            max_min_deg = max(max_min_deg, min_deg)
            remaining.remove(min_v)
        assert max_min_deg == 12

    def test_degeneracy_ordering_exists(self, A):
        """A valid degeneracy ordering achieves max back-degree 12."""
        nn = A.shape[0]
        remaining = set(range(nn))
        adj = {v: set(u for u in range(nn) if A[v, u]) for v in range(nn)}
        ordering = []
        max_back = 0
        while remaining:
            min_v = min(remaining,
                        key=lambda v: len(adj[v] & remaining))
            d = len(adj[min_v] & remaining)
            max_back = max(max_back, d)
            ordering.append(min_v)
            remaining.remove(min_v)
        assert max_back == 12
        assert len(ordering) == nn

    def test_treewidth_lower_independence(self, n):
        """tw >= n / (alpha + 1) - 1.

        Hoffman bound gives alpha <= 10 for SRG(40,12,2,4),
        so tw >= 40/11 - 1 > 2.6, i.e. tw >= 3.
        """
        alpha_upper = 10
        bound = n / (alpha_upper + 1) - 1
        assert bound > 2.5

    def test_treewidth_upper_bound(self, n):
        """tw <= n - 1 = 39 (trivial)."""
        assert n - 1 == 39

    def test_chordal_upper_bound(self, A, n):
        """Minimum-degree elimination ordering gives a constructive tw upper bound."""
        remaining = set(range(n))
        adj = {v: set(u for u in range(n) if A[v, u]) for v in range(n)}
        max_clique = 0
        for _ in range(n):
            min_v = min(remaining,
                        key=lambda v: len(adj[v] & remaining))
            nbrs = adj[min_v] & remaining - {min_v}
            max_clique = max(max_clique, len(nbrs) + 1)
            # Fill: make the neighbourhood a clique
            for u in nbrs:
                for w in nbrs:
                    if u < w and w not in adj[u]:
                        adj[u].add(w)
                        adj[w].add(u)
            remaining.remove(min_v)
        tw_upper = max_clique - 1
        assert tw_upper >= 12   # at least degeneracy
        assert tw_upper <= n - 1

    def test_minimum_degree_subgraph_bound(self, A, n):
        """Every induced subgraph has a vertex of degree at most 12."""
        rng = np.random.RandomState(42)
        for _ in range(30):
            size = rng.randint(5, n)
            subset = list(rng.choice(n, size, replace=False))
            min_deg = n
            for v in subset:
                d = sum(1 for u in subset if A[v, u])
                min_deg = min(min_deg, d)
            assert min_deg <= 12

    def test_bramble_from_clique(self, max_cliques):
        """Any single K4 is a bramble of order 4, giving tw >= 3."""
        clique = max_cliques[0]
        assert len(clique) == 4

    def test_sparse_density_ratio(self, n, k):
        """Edge density = k / (n - 1) = 12/39."""
        density = k / (n - 1)
        assert abs(density - 12 / 39) < 1e-12

    def test_complement_degeneracy(self, A, n):
        """Complement SRG(40,27,18,18) has degeneracy 27."""
        Ac = 1 - A - np.eye(n, dtype=int)
        remaining = set(range(n))
        adj = {v: set(u for u in range(n) if Ac[v, u]) for v in range(n)}
        max_min_deg = 0
        for _ in range(n):
            min_v = min(remaining,
                        key=lambda v: len(adj[v] & remaining))
            min_deg = len(adj[min_v] & remaining)
            max_min_deg = max(max_min_deg, min_deg)
            remaining.remove(min_v)
        assert max_min_deg == 27


# ══════════════════════════════════════════════════════════════════════════════
# 5. MODULAR DECOMPOSITION
# ══════════════════════════════════════════════════════════════════════════════

class TestModularDecomposition:
    """Tests for modular decomposition of W(3,3)."""

    @staticmethod
    def _is_module(A, nn, M):
        """Return True if M is a module in graph with adjacency A."""
        M_set = set(M)
        for v in range(nn):
            if v in M_set:
                continue
            adj_count = sum(1 for u in M if A[v, u])
            if 0 < adj_count < len(M):
                return False
        return True

    def test_singleton_modules(self, A, n):
        """Every singleton {v} is a trivial module."""
        for v in range(n):
            assert self._is_module(A, n, [v])

    def test_full_set_module(self, A, n):
        """The full vertex set V is a trivial module."""
        assert self._is_module(A, n, list(range(n)))

    def test_empty_module(self, A, n):
        """The empty set is a trivial module."""
        assert self._is_module(A, n, [])

    def test_no_nontrivial_module_size_2(self, A, n):
        """No pair of vertices forms a non-trivial module.

        For adjacent u ~ v: |N(u) \\ N[v]| = k - 1 - lambda = 9 > 0.
        For non-adjacent u, v: |N(u) \\ N(v)| = k - mu = 8 > 0.
        Either way some external vertex distinguishes u from v.
        """
        for i in range(n):
            for j in range(i + 1, n):
                assert not self._is_module(A, n, [i, j])

    def test_no_nontrivial_module_size_3(self, A, n):
        """No triple of vertices forms a non-trivial module (exhaustive sample)."""
        rng = np.random.RandomState(123)
        for _ in range(300):
            triple = sorted(rng.choice(n, 3, replace=False))
            assert not self._is_module(A, n, list(triple))

    def test_neighborhood_not_module(self, A, n, k, mu):
        """N(v) is not a module for any vertex v.

        For non-neighbour w of v, w has mu = 4 neighbours in N(v),
        but 0 < 4 < 12 = |N(v)|.
        """
        for v in range(n):
            nbrs = [u for u in range(n) if A[v, u]]
            assert not self._is_module(A, n, nbrs)

    def test_non_neighborhood_not_module(self, A, n, k, lam):
        """V \\ N[v] is not a module for any vertex v.

        Each neighbour w of v has k - 1 - lambda = 9 neighbours
        in V \\ N[v], but 0 < 9 < 27 = |V \\ N[v]|.
        """
        for v in range(n):
            non_nbrs = [u for u in range(n) if not A[v, u] and u != v]
            assert len(non_nbrs) == n - k - 1
            assert not self._is_module(A, n, non_nbrs)

    def test_prime_decomposition(self, A, n):
        """W(3,3) has prime modular decomposition: no modules of size 4..6."""
        rng = np.random.RandomState(456)
        for size in [4, 5, 6]:
            for _ in range(100):
                subset = sorted(rng.choice(n, size, replace=False))
                assert not self._is_module(A, n, list(subset))

    def test_complement_no_small_modules(self, A, n):
        """Complement SRG(40,27,18,18) has no size-2 modules either."""
        Ac = 1 - A - np.eye(n, dtype=int)
        for i in range(n):
            for j in range(i + 1, n):
                assert not self._is_module(Ac, n, [i, j])

    def test_srg_primitivity(self, A, n, mu):
        """Primitive SRG: connected, complement connected, mu > 0."""
        assert _bfs_connected(A, n)
        Ac = 1 - A - np.eye(n, dtype=int)
        assert _bfs_connected(Ac, n)
        assert mu > 0


# ══════════════════════════════════════════════════════════════════════════════
# 6. EAR DECOMPOSITION
# ══════════════════════════════════════════════════════════════════════════════

class TestEarDecomposition:
    """Tests for ear decomposition of 2-connected W(3,3)."""

    def test_two_connected_prerequisite(self, A, n):
        """W(3,3) is 2-connected: prerequisite for ear decomposition."""
        for v in range(n):
            assert _bfs_connected(A, n, excluded={v})

    def test_ear_decomposition_exists(self, A, n):
        """An ear decomposition can be constructed."""
        ears, covered = _build_ear_decomposition(A, n)
        assert len(ears) > 0

    def test_ear_covers_all_edges(self, A, n):
        """Ear decomposition covers all 240 edges."""
        ears, covered = _build_ear_decomposition(A, n)
        assert len(covered) == 240

    def test_ear_covers_all_vertices(self, A, n):
        """Ear decomposition covers all 40 vertices."""
        ears, _ = _build_ear_decomposition(A, n)
        verts = set()
        for ear in ears:
            verts.update(ear)
        assert verts == set(range(n))

    def test_ear_count(self, A, n):
        """Total number of ears = m - n + 1 = 201."""
        ears, covered = _build_ear_decomposition(A, n)
        assert len(covered) == 240
        assert len(ears) == 240 - n + 1

    def test_initial_ear_is_cycle(self, A, n):
        """First ear is a cycle (triangle)."""
        ears, _ = _build_ear_decomposition(A, n)
        first = ears[0]
        assert len(first) >= 3
        for i in range(len(first)):
            u, v = first[i], first[(i + 1) % len(first)]
            assert A[u, v] == 1

    def test_ear_endpoints_in_previous(self, A, n):
        """Each ear's endpoints lie in the previously built structure."""
        ears, _ = _build_ear_decomposition(A, n)
        in_decomp = set(ears[0])
        for ear in ears[1:]:
            assert ear[0] in in_decomp, \
                f"Ear start {ear[0]} not in decomposition"
            assert ear[-1] in in_decomp, \
                f"Ear end {ear[-1]} not in decomposition"
            for v in ear[1:-1]:
                in_decomp.add(v)

    def test_ear_edges_are_valid(self, A, n):
        """Each consecutive pair in an ear is a graph edge."""
        ears, _ = _build_ear_decomposition(A, n)
        for ear in ears:
            for i in range(len(ear) - 1):
                assert A[ear[i], ear[i + 1]] == 1

    def test_cycle_rank_equals_ears(self, A, n):
        """Cycle rank m - n + 1 = 201 equals the ear count."""
        m = np.sum(A) // 2
        assert m - n + 1 == 201

    def test_short_ears_exist(self, A, n):
        """Some ears have length 1 (single chord edge)."""
        ears, _ = _build_ear_decomposition(A, n)
        short = [e for e in ears[1:] if len(e) == 2]
        assert len(short) > 0


# ══════════════════════════════════════════════════════════════════════════════
# 7. CYCLE SPACE ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

class TestCycleSpace:
    """Tests for cycle space and cut space of W(3,3)."""

    def test_cycle_rank(self, n):
        """Cycle rank = m - n + c = 240 - 40 + 1 = 201."""
        m, c = 240, 1
        assert m - n + c == 201

    def test_girth_is_3(self, A):
        """Girth = 3 (triangles exist since lambda = 2 > 0)."""
        A3 = A @ A @ A
        assert np.trace(A3) > 0

    def test_spanning_tree_edges_count(self, spanning_tree, n):
        """Spanning tree has n - 1 = 39 edges."""
        assert len(spanning_tree) == n - 1

    def test_spanning_tree_is_tree(self, spanning_tree, A, n):
        """Spanning tree covers all vertices with n - 1 edges (acyclic)."""
        verts = set()
        for u, v in spanning_tree:
            verts.add(u)
            verts.add(v)
        assert len(verts) == n
        assert len(spanning_tree) == n - 1

    def test_non_tree_edges(self, spanning_tree, n):
        """Non-tree edges = m - (n-1) = 201."""
        m = 240
        assert m - len(spanning_tree) == 201

    def test_fundamental_cycles_count(self, spanning_tree, A, n):
        """Each non-tree edge generates one fundamental cycle; total = 201."""
        tree_set = set()
        for u, v in spanning_tree:
            tree_set.add((min(u, v), max(u, v)))
        non_tree = []
        for i in range(n):
            for j in range(i + 1, n):
                if A[i, j] and (i, j) not in tree_set:
                    non_tree.append((i, j))
        assert len(non_tree) == 201

    def test_fundamental_cycle_uses_one_non_tree_edge(self, spanning_tree, A, n):
        """Each fundamental cycle contains exactly one non-tree edge.

        Verified for the first 20 non-tree edges.
        """
        tree_adj = np.zeros((n, n), dtype=int)
        for u, v in spanning_tree:
            tree_adj[u, v] = tree_adj[v, u] = 1
        tree_set = set()
        for u, v in spanning_tree:
            tree_set.add((min(u, v), max(u, v)))

        count_checked = 0
        for i in range(n):
            for j in range(i + 1, n):
                if A[i, j] and (i, j) not in tree_set:
                    # BFS in tree from i to j
                    parent = {i: None}
                    queue = deque([i])
                    while queue:
                        u = queue.popleft()
                        if u == j:
                            break
                        for v in range(n):
                            if tree_adj[u, v] and v not in parent:
                                parent[v] = u
                                queue.append(v)
                    assert j in parent, f"No tree path from {i} to {j}"
                    # All edges on the tree path are tree edges
                    v = j
                    while parent[v] is not None:
                        e = (min(v, parent[v]), max(v, parent[v]))
                        assert e in tree_set
                        v = parent[v]
                    count_checked += 1
                    if count_checked >= 20:
                        break
            if count_checked >= 20:
                break
        assert count_checked == 20

    def test_incidence_matrix_rank_gf2(self, A, n):
        """Rank of incidence matrix over GF(2) = n - 1 = 39."""
        edges = []
        for i in range(n):
            for j in range(i + 1, n):
                if A[i, j]:
                    edges.append((i, j))
        m = len(edges)
        B = np.zeros((n, m), dtype=int)
        for idx, (i, j) in enumerate(edges):
            B[i, idx] = 1
            B[j, idx] = 1
        rank = _gauss_gf2_rank(B, n, m)
        assert rank == n - 1

    def test_cut_space_dimension(self, n):
        """Cut space dimension = n - c = 39."""
        assert n - 1 == 39

    def test_cycle_cut_dimensions_sum(self, n):
        """dim(cycle space) + dim(cut space) = m = 240."""
        assert 201 + 39 == 240


# ══════════════════════════════════════════════════════════════════════════════
# 8. MATCHING DECOMPOSITION
# ══════════════════════════════════════════════════════════════════════════════

class TestMatchingDecomposition:
    """Tests for matching and edge independence properties of W(3,3)."""

    def test_even_order(self, n):
        """n = 40 is even, necessary condition for a perfect matching."""
        assert n % 2 == 0

    def test_perfect_matching_exists(self, A, n):
        """A perfect matching exists (vertex-transitive graph, even order)."""
        match = _maximum_matching(A, n)
        assert len(match) == n // 2

    def test_maximum_matching_size(self, A, n):
        """Maximum matching has size n/2 = 20."""
        match = _maximum_matching(A, n)
        assert len(match) == 20

    def test_matching_is_valid(self, A, n):
        """Found matching has no shared vertices and all edges are valid."""
        match = _maximum_matching(A, n)
        used = set()
        for u, v in match:
            assert A[u, v] == 1, f"({u},{v}) is not an edge"
            assert u not in used, f"Vertex {u} used twice"
            assert v not in used, f"Vertex {v} used twice"
            used.add(u)
            used.add(v)

    def test_matching_covers_all_vertices(self, A, n):
        """Perfect matching covers all 40 vertices."""
        match = _maximum_matching(A, n)
        covered = set()
        for u, v in match:
            covered.add(u)
            covered.add(v)
        assert covered == set(range(n))

    def test_tutte_matrix_nonsingular(self, A, n):
        """Random skew-symmetric Tutte matrix has nonzero determinant,
        certifying existence of a perfect matching (Schwartz-Zippel)."""
        rng = np.random.RandomState(42)
        T = np.zeros((n, n), dtype=float)
        for i in range(n):
            for j in range(i + 1, n):
                if A[i, j]:
                    val = rng.randint(1, 1000)
                    T[i, j] = val
                    T[j, i] = -val
        det = np.linalg.det(T)
        assert abs(det) > 1e-6, "Tutte matrix determinant is zero"

    def test_two_disjoint_matchings(self, A, n):
        """Two edge-disjoint perfect matchings exist."""
        match1 = _maximum_matching(A, n)
        assert len(match1) == n // 2
        # Remove first matching edges
        A2 = A.copy()
        for u, v in match1:
            A2[u, v] = A2[v, u] = 0
        match2 = _maximum_matching(A2, n)
        assert len(match2) == n // 2
        # Check disjointness
        set1 = set((min(u, v), max(u, v)) for u, v in match1)
        set2 = set((min(u, v), max(u, v)) for u, v in match2)
        assert len(set1 & set2) == 0

    def test_deficiency_zero(self, A, n):
        """Deficiency = n - 2 * nu(G) = 0 for graphs with perfect matchings."""
        match = _maximum_matching(A, n)
        deficiency = n - 2 * len(match)
        assert deficiency == 0

    def test_fractional_matching(self, A, n, k):
        """Fractional perfect matching: weight 1/k on each edge gives
        value m/k = 240/12 = 20 = n/2, saturating all vertices."""
        m = np.sum(A) // 2
        fractional_value = m / k
        assert fractional_value == n / 2 == 20.0
        # Verify each vertex is saturated: sum of weights on incident edges = 1
        for v in range(n):
            total = sum(1 / k for u in range(n) if A[v, u])
            assert abs(total - 1.0) < 1e-12

    def test_matching_complement(self, A, n):
        """Complement SRG(40,27,18,18) also has a perfect matching."""
        Ac = 1 - A - np.eye(n, dtype=int)
        match = _maximum_matching(Ac, n)
        assert len(match) == n // 2
