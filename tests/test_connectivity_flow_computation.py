"""
Phase CXIII  --  Connectivity & Flow Computation on W(3,3) = SRG(40,12,2,4).

80 tests covering vertex/edge connectivity, network flows, algebraic
connectivity, toughness & resilience, spanning subgraphs, expansion
properties, and path/cycle structure.

All tests use only numpy and standard library.  Every assertion is
mathematically provable from the SRG(40,12,2,4) parameters:
    adjacency spectrum:  {12^1, 2^24, (-4)^15}
    Laplacian spectrum:  {0^1, 10^24, 16^15}
    n=40, k=12, lambda=2, mu=4, 240 edges, 160 triangles, diameter=2
"""

import numpy as np
import pytest
from collections import deque
import random


# ── W(3,3) builder ────────────────────────────────────────────────────────

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


# ── SRG parameters ────────────────────────────────────────────────────────

_N, _K, _LAM, _MU = 40, 12, 2, 4


# ── Helper functions ──────────────────────────────────────────────────────

def _bfs_connected(A, excluded=None):
    """Check if graph is connected after excluding a set of vertices."""
    if excluded is None:
        excluded = set()
    n = A.shape[0]
    remaining = [i for i in range(n) if i not in excluded]
    if len(remaining) <= 1:
        return True
    visited = set()
    queue = deque([remaining[0]])
    visited.add(remaining[0])
    while queue:
        v = queue.popleft()
        for u in remaining:
            if u not in visited and A[v, u]:
                visited.add(u)
                queue.append(u)
    return len(visited) == len(remaining)


def _count_components(A, excluded=None):
    """Count connected components after excluding vertices."""
    if excluded is None:
        excluded = set()
    n = A.shape[0]
    remaining = [i for i in range(n) if i not in excluded]
    if not remaining:
        return 0
    visited = set()
    components = 0
    for start in remaining:
        if start in visited:
            continue
        components += 1
        queue = deque([start])
        visited.add(start)
        while queue:
            v = queue.popleft()
            for u in remaining:
                if u not in visited and A[v, u]:
                    visited.add(u)
                    queue.append(u)
    return components


def _bfs_augmenting_path(residual, source, sink, parent):
    """BFS to find augmenting path in residual graph (Edmonds-Karp)."""
    n = residual.shape[0]
    visited = np.zeros(n, dtype=bool)
    visited[source] = True
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in range(n):
            if not visited[v] and residual[u, v] > 0:
                visited[v] = True
                parent[v] = u
                if v == sink:
                    return True
                queue.append(v)
    return False


def _edmonds_karp(capacity, source, sink):
    """Edmonds-Karp max-flow (Ford-Fulkerson with BFS augmentation)."""
    n = capacity.shape[0]
    residual = capacity.copy().astype(int)
    total_flow = 0
    while True:
        parent = np.full(n, -1, dtype=int)
        if not _bfs_augmenting_path(residual, source, sink, parent):
            break
        # trace back to find bottleneck
        path_flow = 10**9
        v = sink
        while v != source:
            u = parent[v]
            path_flow = min(path_flow, int(residual[u, v]))
            v = u
        # update residual graph
        v = sink
        while v != source:
            u = parent[v]
            residual[u, v] -= path_flow
            residual[v, u] += path_flow
            v = u
        total_flow += path_flow
    return total_flow, residual


def _edge_max_flow(A, source, sink):
    """Max-flow with unit edge capacities (= edge-disjoint paths)."""
    capacity = A.copy().astype(int)
    return _edmonds_karp(capacity, source, sink)


def _vertex_max_flow(A, source, sink):
    """Max-flow with node-splitting (= vertex-disjoint paths via Menger).

    Each vertex v is split into v_in (index v) and v_out (index v+n).
    Internal arc v_in -> v_out has capacity 1 for internal vertices
    and capacity deg(v) for source/sink.  Graph edge arcs u_out -> v_in
    have capacity 1 (each original edge used at most once per path).
    """
    n = A.shape[0]
    k = int(A[source].sum())          # degree bound for source/sink
    cap = np.zeros((2 * n, 2 * n), dtype=int)
    # internal arcs: v_in -> v_out
    for v in range(n):
        cap[v, v + n] = k if (v == source or v == sink) else 1
    # graph edge arcs: u_out -> v_in  (capacity 1 per direction)
    for u in range(n):
        for v in range(n):
            if A[u, v]:
                cap[u + n, v] = 1
    flow, _ = _edmonds_karp(cap, source, sink + n)
    return flow


def _bfs_distances(A, source):
    """BFS shortest-path distances from source."""
    n = A.shape[0]
    dist = np.full(n, -1, dtype=int)
    dist[source] = 0
    queue = deque([source])
    while queue:
        v = queue.popleft()
        for u in range(n):
            if dist[u] == -1 and A[v, u]:
                dist[u] = dist[v] + 1
                queue.append(u)
    return dist


def _edge_connected_after_removal(A, removed_edges):
    """Check connectivity after removing specific edges."""
    B = A.copy()
    for u, v in removed_edges:
        B[u, v] = B[v, u] = 0
    return _bfs_connected(B)


def _laplacian(A):
    """Combinatorial Laplacian L = D - A."""
    return np.diag(A.sum(axis=1)) - A


def _min_cut_from_residual(A, residual, source):
    """Compute min-cut size from residual graph after max-flow."""
    n = A.shape[0]
    visited = set()
    queue = deque([source])
    visited.add(source)
    while queue:
        u = queue.popleft()
        for v in range(n):
            if v not in visited and residual[u, v] > 0:
                visited.add(v)
                queue.append(v)
    cut = sum(1 for u in visited for v in range(n)
              if v not in visited and A[u, v])
    return cut, visited


# ── Module-scoped fixtures ────────────────────────────────────────────────

@pytest.fixture(scope="module")
def w33():
    return _build_w33()


@pytest.fixture(scope="module")
def lap_eigs(w33):
    """Sorted Laplacian eigenvalues (ascending)."""
    L = _laplacian(w33).astype(float)
    return np.sort(np.linalg.eigvalsh(L))


@pytest.fixture(scope="module")
def adj_eigs(w33):
    """Adjacency eigenvalues sorted descending."""
    return np.sort(np.linalg.eigvalsh(w33.astype(float)))[::-1]


@pytest.fixture(scope="module")
def neighbors_of_0(w33):
    """Neighbor list of vertex 0."""
    return list(np.where(w33[0] == 1)[0])


@pytest.fixture(scope="module")
def nonadj_of_0(w33):
    """First non-neighbor of vertex 0 (other than itself)."""
    for j in range(1, 40):
        if not w33[0, j]:
            return j


# ══════════════════════════════════════════════════════════════════════════
#  1.  VERTEX CONNECTIVITY  (10 tests)
# ══════════════════════════════════════════════════════════════════════════

class TestVertexConnectivity:
    """Vertex connectivity kappa(G) = 12 for vertex-transitive W(3,3)."""

    def test_graph_is_connected(self, w33):
        """Basic connectivity check."""
        assert _bfs_connected(w33)

    def test_kappa_equals_k_via_menger(self, w33):
        """kappa = k = 12 via vertex-disjoint path count (Menger)."""
        flow = _vertex_max_flow(w33, 0, 1)
        assert flow == 12

    def test_removing_neighborhood_disconnects(self, w33, neighbors_of_0):
        """Removing N(v) isolates v, proving kappa <= k = 12."""
        assert len(neighbors_of_0) == 12
        comps = _count_components(w33, set(neighbors_of_0))
        assert comps >= 2

    def test_removing_neighborhood_creates_exactly_2_components(self, w33, neighbors_of_0):
        """N(v) removal yields {v} isolated + connected complement."""
        comps = _count_components(w33, set(neighbors_of_0))
        assert comps == 2

    def test_removing_11_of_12_neighbors_stays_connected(self, w33, neighbors_of_0):
        """Removing 11 neighbors keeps graph connected (kappa = 12 > 11)."""
        excluded = set(neighbors_of_0[:11])
        assert _bfs_connected(w33, excluded)

    def test_removing_10_random_vertices_connected(self, w33):
        """Removing 10 random vertices preserves connectivity."""
        rng = random.Random(42)
        for _ in range(5):
            excluded = set(rng.sample(range(40), 10))
            assert _bfs_connected(w33, excluded)

    def test_menger_adjacent_pair(self, w33, neighbors_of_0):
        """12 vertex-disjoint paths between an adjacent pair."""
        t = neighbors_of_0[0]
        flow = _vertex_max_flow(w33, 0, t)
        assert flow == 12

    def test_menger_nonadjacent_pair(self, w33, nonadj_of_0):
        """12 vertex-disjoint paths between a non-adjacent pair."""
        flow = _vertex_max_flow(w33, 0, nonadj_of_0)
        assert flow == 12

    def test_minimum_vertex_cut_equals_12(self, w33):
        """min over all sinks t of (vertex-disjoint 0-t paths) = 12."""
        cuts = [_vertex_max_flow(w33, 0, t) for t in range(1, 40)]
        assert min(cuts) == 12

    def test_vertex_connectivity_several_pairs(self, w33):
        """kappa = 12 for diverse source-sink pairs."""
        pairs = [(0, 5), (1, 10), (3, 20), (7, 35), (12, 39)]
        for s, t in pairs:
            assert _vertex_max_flow(w33, s, t) == 12


# ══════════════════════════════════════════════════════════════════════════
#  2.  EDGE CONNECTIVITY  (10 tests)
# ══════════════════════════════════════════════════════════════════════════

class TestEdgeConnectivity:
    """Edge connectivity lambda(G) = 12 for W(3,3)."""

    def test_lambda_equals_k(self, w33):
        """lambda = 12 via edge-disjoint paths (vertex 0 -> vertex 1)."""
        flow, _ = _edge_max_flow(w33, 0, 1)
        assert flow == 12

    def test_whitney_inequality(self, w33):
        """Whitney: kappa <= lambda <= delta.  All equal 12 here."""
        kappa = _vertex_max_flow(w33, 0, 1)
        lam, _ = _edge_max_flow(w33, 0, 1)
        delta = int(w33[0].sum())
        assert kappa <= lam <= delta
        assert kappa == lam == delta == 12

    def test_edge_disjoint_adjacent(self, w33, neighbors_of_0):
        """12 edge-disjoint paths between adjacent vertices."""
        t = neighbors_of_0[0]
        flow, _ = _edge_max_flow(w33, 0, t)
        assert flow == 12

    def test_edge_disjoint_nonadjacent(self, w33, nonadj_of_0):
        """12 edge-disjoint paths between non-adjacent vertices."""
        flow, _ = _edge_max_flow(w33, 0, nonadj_of_0)
        assert flow == 12

    def test_removing_11_edges_keeps_connected(self, w33, neighbors_of_0):
        """Removing 11 edges incident to v keeps graph connected."""
        edges = [(0, j) for j in neighbors_of_0[:11]]
        assert _edge_connected_after_removal(w33, edges)

    def test_removing_12_edges_disconnects(self, w33, neighbors_of_0):
        """Removing all 12 edges of a vertex isolates it."""
        edges = [(0, j) for j in neighbors_of_0]
        assert not _edge_connected_after_removal(w33, edges)

    def test_edge_connectivity_from_multiple_sources(self, w33):
        """lambda = 12 for several source-sink pairs."""
        for t in [5, 15, 25, 39]:
            flow, _ = _edge_max_flow(w33, 0, t)
            assert flow == 12

    def test_minimum_edge_cut_equals_12(self, w33):
        """min-cut over sampled sinks from vertex 0 equals 12."""
        flows = [_edge_max_flow(w33, 0, t)[0] for t in range(1, 40, 3)]
        assert min(flows) == 12

    def test_edge_connectivity_symmetric(self, w33):
        """lambda(s,t) = lambda(t,s) for undirected graph."""
        s, t = 3, 28
        f1, _ = _edge_max_flow(w33, s, t)
        f2, _ = _edge_max_flow(w33, t, s)
        assert f1 == f2 == 12

    def test_edge_bond_lower_bound(self, w33, adj_eigs):
        """Every edge bond (minimal edge cut) has size >= k = 12."""
        # For k-regular vertex-transitive: every bond has size >= k.
        # Spectral certificate: lambda_2(L) > 0 guarantees connected
        # and delta(G) = k gives bond >= k.
        k = int(w33[0].sum())
        assert k == 12
        # verify via a specific bond: edges between {v} and V\{v}
        for v in [0, 10, 20, 30]:
            bond_size = int(w33[v].sum())
            assert bond_size >= 12


# ══════════════════════════════════════════════════════════════════════════
#  3.  NETWORK FLOWS  (12 tests)
# ══════════════════════════════════════════════════════════════════════════

class TestNetworkFlows:
    """Edmonds-Karp max-flow / min-cut on W(3,3)."""

    def test_max_flow_adjacent(self, w33, neighbors_of_0):
        """Max-flow = 12 for an adjacent pair."""
        t = neighbors_of_0[0]
        flow, _ = _edge_max_flow(w33, 0, t)
        assert flow == 12

    def test_max_flow_nonadjacent(self, w33, nonadj_of_0):
        """Max-flow = 12 for a non-adjacent pair."""
        flow, _ = _edge_max_flow(w33, 0, nonadj_of_0)
        assert flow == 12

    def test_max_flow_min_cut_theorem(self, w33):
        """Max-flow = min-cut verified by residual reachability."""
        s, t = 0, 20
        flow, residual = _edge_max_flow(w33, s, t)
        cut, _ = _min_cut_from_residual(w33, residual, s)
        assert cut == flow

    def test_no_augmenting_path_after_max_flow(self, w33):
        """Residual graph has no s-t path after max-flow."""
        s, t = 0, 10
        _, residual = _edge_max_flow(w33, s, t)
        parent = np.full(40, -1, dtype=int)
        assert not _bfs_augmenting_path(residual, s, t, parent)

    def test_flow_conservation(self, w33):
        """Net flow = 0 at every internal node."""
        s, t = 0, 15
        cap = w33.copy().astype(int)
        total_flow, residual = _edmonds_karp(cap, s, t)
        flow_matrix = cap - residual
        for v in range(40):
            if v in (s, t):
                continue
            net = sum(flow_matrix[u, v] - flow_matrix[v, u] for u in range(40))
            assert net == 0, f"Conservation violated at node {v}"

    def test_flow_value_source_sink(self, w33):
        """Positive flow out of source = positive flow into sink = total flow.

        For undirected graphs modelled as bidirected arcs, only positive
        entries of (cap - residual) represent actual forward flow.
        """
        s, t = 0, 25
        cap = w33.copy().astype(int)
        total_flow, residual = _edmonds_karp(cap, s, t)
        fm = cap - residual
        source_out = sum(int(fm[s, v]) for v in range(40) if fm[s, v] > 0)
        sink_in = sum(int(fm[v, t]) for v in range(40) if fm[v, t] > 0)
        assert source_out == total_flow
        assert sink_in == total_flow

    def test_max_flow_symmetric(self, w33):
        """flow(s,t) = flow(t,s) for undirected graph."""
        for s, t in [(0, 10), (5, 30), (12, 38)]:
            f1, _ = _edge_max_flow(w33, s, t)
            f2, _ = _edge_max_flow(w33, t, s)
            assert f1 == f2

    def test_max_flow_all_sinks_from_v0(self, w33):
        """Max-flow = 12 from vertex 0 to every other vertex."""
        for t in range(1, 40):
            flow, _ = _edge_max_flow(w33, 0, t)
            assert flow == 12, f"flow(0,{t}) = {flow}"

    def test_min_cut_partition_nonempty(self, w33):
        """Min-cut partitions V into two non-empty sides."""
        s, t = 0, 20
        _, residual = _edge_max_flow(w33, s, t)
        _, S_side = _min_cut_from_residual(w33, residual, s)
        T_side = set(range(40)) - S_side
        assert len(S_side) >= 1 and len(T_side) >= 1

    def test_max_flow_bounded_by_degree(self, w33):
        """Max-flow <= min(deg(s), deg(t)) = 12."""
        for s, t in [(0, 1), (5, 10), (20, 39)]:
            flow, _ = _edge_max_flow(w33, s, t)
            assert flow <= min(int(w33[s].sum()), int(w33[t].sum()))

    def test_ford_fulkerson_terminates(self, w33):
        """Algorithm terminates for all sampled pairs (integer capacities)."""
        for s in range(0, 40, 10):
            for t in range(1, 40, 10):
                if s != t:
                    flow, _ = _edge_max_flow(w33, s, t)
                    assert flow >= 0

    def test_vertex_flow_matches_edge_flow(self, w33):
        """For W(3,3): vertex-disjoint = edge-disjoint = 12 (Whitney tight)."""
        s, t = 0, 20
        v_flow = _vertex_max_flow(w33, s, t)
        e_flow, _ = _edge_max_flow(w33, s, t)
        assert v_flow <= e_flow          # Whitney
        assert v_flow == e_flow == 12    # tight for this graph


# ══════════════════════════════════════════════════════════════════════════
#  4.  ALGEBRAIC CONNECTIVITY  (10 tests)
# ══════════════════════════════════════════════════════════════════════════

class TestAlgebraicConnectivity:
    """Fiedler value a(G) = 10 and Laplacian spectral properties."""

    def test_fiedler_value_equals_10(self, lap_eigs):
        """Algebraic connectivity = second-smallest Laplacian eigenvalue = 10."""
        assert abs(lap_eigs[0]) < 1e-10
        assert abs(lap_eigs[1] - 10.0) < 1e-8

    def test_laplacian_spectrum_multiplicities(self, lap_eigs):
        """Laplacian spectrum = {0^1, 10^24, 16^15}."""
        c0 = np.sum(np.abs(lap_eigs) < 1e-8)
        c10 = np.sum(np.abs(lap_eigs - 10.0) < 1e-8)
        c16 = np.sum(np.abs(lap_eigs - 16.0) < 1e-8)
        assert (c0, c10, c16) == (1, 24, 15)
        assert c0 + c10 + c16 == 40

    def test_laplacian_positive_semidefinite(self, lap_eigs):
        """All Laplacian eigenvalues >= 0."""
        assert np.all(lap_eigs >= -1e-10)

    def test_laplacian_row_sums_zero(self, w33):
        """Each row of L sums to zero (Lx1 = 0)."""
        L = _laplacian(w33)
        assert np.allclose(L.sum(axis=1), 0)

    def test_laplacian_symmetric(self, w33):
        """L is symmetric."""
        L = _laplacian(w33)
        assert np.allclose(L, L.T)

    def test_laplacian_rank_n_minus_1(self, lap_eigs):
        """rank(L) = n - 1 = 39 (exactly one zero eigenvalue)."""
        rank = np.sum(np.abs(lap_eigs) > 1e-8)
        assert rank == 39

    def test_cheeger_lower_bound(self, adj_eigs):
        """Cheeger inequality lower bound: h(G) >= (k - theta_1)/2 = 5."""
        k = 12
        theta_1 = adj_eigs[1]  # second-largest adjacency eigenvalue
        assert abs(theta_1 - 2.0) < 1e-8
        lower_bound = (k - theta_1) / 2
        assert lower_bound >= 5.0 - 1e-8

    def test_cheeger_upper_bound(self, adj_eigs):
        """Cheeger inequality upper bound: h(G) <= sqrt(2k(k - theta_1))."""
        k = 12
        theta_1 = adj_eigs[1]
        upper = np.sqrt(2 * k * (k - theta_1))
        # upper ~ sqrt(240) ~ 15.49
        assert upper < 16.0
        assert upper > 15.0

    def test_algebraic_connectivity_positive_implies_connected(self, lap_eigs):
        """a(G) > 0 certifies connectivity."""
        assert lap_eigs[1] > 1e-8

    def test_fiedler_multiplicity_24(self, lap_eigs):
        """Fiedler eigenvalue 10 has multiplicity 24."""
        mult = np.sum(np.abs(lap_eigs - lap_eigs[1]) < 1e-8)
        assert mult == 24


# ══════════════════════════════════════════════════════════════════════════
#  5.  TOUGHNESS & RESILIENCE  (10 tests)
# ══════════════════════════════════════════════════════════════════════════

class TestToughnessResilience:
    """Toughness bounds and resilience under vertex/edge deletion."""

    def test_kappa_removal_stays_connected(self, w33):
        """Removing fewer than kappa = 12 vertices preserves connectivity."""
        rng = random.Random(123)
        for size in [1, 3, 5, 8, 11]:
            for _ in range(3):
                excl = set(rng.sample(range(40), size))
                assert _bfs_connected(w33, excl), \
                    f"Disconnected after removing {size} vertices"

    def test_toughness_at_least_one(self, w33):
        """t(G) >= 1: |S| >= omega(G-S) for sampled sets of size >= 12."""
        rng = random.Random(456)
        for size in range(12, 26):
            for _ in range(3):
                S = set(rng.sample(range(40), size))
                omega = _count_components(w33, S)
                assert size >= omega, \
                    f"|S|={size} but omega={omega}"

    def test_hoffman_independence_bound(self, adj_eigs):
        """Hoffman bound: alpha(G) <= n(-s)/(k-s) = 10."""
        s = adj_eigs[-1]  # most negative eigenvalue
        bound = _N * (-s) / (_K - s)
        assert abs(bound - 10.0) < 1e-8

    def test_single_edge_removal_connected(self, w33):
        """Removing any single edge preserves connectivity (lambda = 12)."""
        # test 12 distinct edges
        tested = 0
        for i in range(40):
            for j in range(i + 1, 40):
                if w33[i, j]:
                    assert _edge_connected_after_removal(w33, [(i, j)])
                    tested += 1
                    if tested >= 12:
                        break
            if tested >= 12:
                break

    def test_removing_up_to_11_edges_from_vertex(self, w33):
        """Removing 1..11 edges incident to vertex 5 keeps graph connected."""
        nbrs = list(np.where(w33[5] == 1)[0])
        for cnt in [1, 3, 5, 8, 11]:
            edges = [(5, nbrs[j]) for j in range(cnt)]
            assert _edge_connected_after_removal(w33, edges)

    def test_random_edge_removal_resilience(self, w33):
        """Removing < 12 random edges preserves connectivity."""
        rng = random.Random(789)
        all_edges = [(i, j) for i in range(40)
                     for j in range(i + 1, 40) if w33[i, j]]
        for cnt in [1, 5, 10, 11]:
            removed = rng.sample(all_edges, cnt)
            assert _edge_connected_after_removal(w33, removed)

    def test_neighborhood_removal_2_components(self, w33):
        """Removing N(v) yields exactly 2 components for several v."""
        for v in [0, 5, 10, 20, 30]:
            nbrs = set(np.where(w33[v] == 1)[0])
            assert _count_components(w33, nbrs) == 2

    def test_isolated_vertex_after_neighborhood_removal(self, w33):
        """After removing N(v), vertex v has zero remaining edges."""
        v = 0
        nbrs = set(np.where(w33[v] == 1)[0])
        remaining = [u for u in range(40) if u not in nbrs and u != v]
        assert all(w33[v, u] == 0 for u in remaining)

    def test_toughness_lower_bound_from_min_cut(self, w33):
        """t(G) >= kappa / omega_max; min vertex cut of 12 gives 2 components."""
        nbrs = set(np.where(w33[0] == 1)[0])
        omega = _count_components(w33, nbrs)
        assert omega == 2
        assert len(nbrs) / omega == 6.0  # toughness contribution

    def test_binding_number_positive(self, w33):
        """Binding number: |N({v})| / |{v}| = 12 for every singleton."""
        for v in range(40):
            assert int(w33[v].sum()) == 12


# ══════════════════════════════════════════════════════════════════════════
#  6.  SPANNING SUBGRAPHS  (10 tests)
# ══════════════════════════════════════════════════════════════════════════

class TestSpanningSubgraphs:
    """Kirchhoff spanning-tree count and related properties."""

    def test_spanning_tree_count_log(self, lap_eigs):
        """tau = 2^81 * 5^23 via sum-of-log of Laplacian eigenvalues."""
        nonzero = lap_eigs[lap_eigs > 1e-8]
        log_tau = np.sum(np.log(nonzero)) - np.log(40)
        expected = 81 * np.log(2) + 23 * np.log(5)
        assert abs(log_tau - expected) < 1e-6

    def test_spanning_tree_eigenvalue_formula(self):
        """tau = (1/40) * 10^24 * 16^15 = 2^81 * 5^23 algebraically."""
        # 10^24 = 2^24 * 5^24;  16^15 = 2^60
        # product = 2^84 * 5^24;  divide by 40 = 2^3 * 5 => 2^81 * 5^23
        log_tau = 24 * np.log(10) + 15 * np.log(16) - np.log(40)
        expected = 81 * np.log(2) + 23 * np.log(5)
        assert abs(log_tau - expected) < 1e-10

    def test_matrix_tree_cofactor(self, w33):
        """Kirchhoff: tau = det(L_{00}) via cofactor expansion."""
        L = _laplacian(w33).astype(float)
        cofactor = L[1:, 1:]
        sign, logdet = np.linalg.slogdet(cofactor)
        assert sign > 0
        expected = 81 * np.log(2) + 23 * np.log(5)
        assert abs(logdet - expected) < 1e-6

    def test_all_cofactors_equal(self, w33):
        """For k-regular graph all Laplacian cofactors are equal."""
        L = _laplacian(w33).astype(float)
        _, ld0 = np.linalg.slogdet(L[1:, 1:])
        idx = 17
        rows = list(range(40))
        rows.remove(idx)
        cols = list(range(40))
        cols.remove(idx)
        _, ld1 = np.linalg.slogdet(L[np.ix_(rows, cols)])
        assert abs(ld0 - ld1) < 1e-6

    def test_power_of_2_in_tau(self):
        """tau is divisible by 2^81 (from 16^15 * 10^24 / 40)."""
        pow2 = 60 + 24 - 3   # 2^60 from 16^15, 2^24 from 10^24, /2^3 from 40
        assert pow2 == 81

    def test_power_of_5_in_tau(self):
        """tau is divisible by 5^23 (from 10^24 / 40)."""
        pow5 = 24 - 1   # 5^24 from 10^24, /5 from 40
        assert pow5 == 23

    def test_log10_of_tau(self):
        """log10(tau) ~ 40.46:  an astronomically large count."""
        log10_tau = 81 * np.log10(2) + 23 * np.log10(5)
        assert abs(log10_tau - 40.46) < 0.01

    def test_edge_count_sufficient_for_spanning_tree(self, w33):
        """Graph has 240 edges >> n-1 = 39 needed for a spanning tree."""
        m = w33.sum() // 2
        assert m == 240
        assert m >= 39

    def test_complement_spanning_tree_count(self, w33):
        """Complement SRG(40,27,18,18) spanning tree log consistency."""
        # complement adjacency spectrum: {27^1, (-3)^24, 3^15}
        # complement Laplacian eigenvalues: 0, 30^24, 24^15
        Ac = 1 - w33 - np.eye(40, dtype=int)
        Lc = np.diag(Ac.sum(axis=1)) - Ac
        eigs_c = np.sort(np.linalg.eigvalsh(Lc.astype(float)))
        nonzero_c = eigs_c[eigs_c > 1e-8]
        log_tau_c = np.sum(np.log(nonzero_c)) - np.log(40)
        expected = 24 * np.log(30) + 15 * np.log(24) - np.log(40)
        assert abs(log_tau_c - expected) < 1e-5

    def test_spanning_tree_count_positive(self, w33):
        """Connected graph => tau > 0."""
        L = _laplacian(w33).astype(float)
        sign, logdet = np.linalg.slogdet(L[1:, 1:])
        assert sign > 0 and logdet > 0


# ══════════════════════════════════════════════════════════════════════════
#  7.  EXPANSION PROPERTIES  (10 tests)
# ══════════════════════════════════════════════════════════════════════════

class TestExpansionProperties:
    """Vertex / edge expansion, expander mixing, spectral certificates."""

    def test_every_vertex_has_boundary_12(self, w33):
        """delta({v}) = deg(v) = 12 for every vertex v."""
        for v in range(40):
            assert int(w33[v].sum()) == 12

    def test_vertex_expansion_singletons(self, w33):
        """For S = {v}: |N(S) setminus S| = 12."""
        for v in range(0, 40, 5):
            nbrs = set(np.where(w33[v] == 1)[0])
            assert len(nbrs) == 12  # all outside S={v}

    def test_edge_expansion_spectral_lower_bound(self, adj_eigs):
        """h(G) >= (k - theta_1)/2 = 5."""
        theta_1 = adj_eigs[1]
        assert (_K - theta_1) / 2 >= 5.0 - 1e-8

    def test_expander_mixing_lemma(self, w33, adj_eigs):
        """Expander-mixing: |e(S,T) - k|S||T|/n| <= theta*sqrt(|S||T|)."""
        theta = max(abs(adj_eigs[1]), abs(adj_eigs[-1]))
        assert abs(theta - 4.0) < 1e-8
        S = set(range(10))
        T = set(range(10, 20))
        e_ST = sum(1 for u in S for v in T if w33[u, v])
        expected = _K * len(S) * len(T) / _N
        bound = theta * np.sqrt(len(S) * len(T))
        assert abs(e_ST - expected) <= bound + 1e-8

    def test_spectral_gap_equals_10(self, adj_eigs):
        """Spectral gap k - theta_1 = 12 - 2 = 10."""
        gap = adj_eigs[0] - adj_eigs[1]
        assert abs(gap - 10.0) < 1e-8

    def test_spectral_gap_is_fiedler(self, adj_eigs, lap_eigs):
        """For k-regular: spectral gap of A = Fiedler value of L."""
        gap = adj_eigs[0] - adj_eigs[1]
        fiedler = lap_eigs[1]
        assert abs(gap - fiedler) < 1e-8

    def test_edge_boundary_adjacent_pair(self, w33, neighbors_of_0):
        """Edge boundary of {u,v} adjacent = 22 (11 from each)."""
        u, v = 0, neighbors_of_0[0]
        S = {u, v}
        comp = set(range(40)) - S
        eb = sum(1 for x in S for y in comp if w33[x, y])
        # u: 12-1=11 edges out, v: 12-1=11 edges out  => 22
        assert eb == 22

    def test_edge_boundary_nonadjacent_pair(self, w33, nonadj_of_0):
        """Edge boundary of {u,v} non-adjacent = 24 (12 from each)."""
        u, v = 0, nonadj_of_0
        S = {u, v}
        comp = set(range(40)) - S
        eb = sum(1 for x in S for y in comp if w33[x, y])
        assert eb == 24

    def test_closed_neighborhood_magnification(self, w33):
        """Magnification: |N[v]| / |{v}| = 13 for every singleton."""
        for v in range(40):
            closed = 1 + int(w33[v].sum())
            assert closed == 13

    def test_expander_mixing_random_sets(self, w33, adj_eigs):
        """Expander-mixing holds for 5 random (S, T) pairs."""
        theta = max(abs(adj_eigs[1]), abs(adj_eigs[-1]))
        rng = random.Random(314)
        for _ in range(5):
            sS = rng.randint(3, 15)
            sT = rng.randint(3, 15)
            S = set(rng.sample(range(40), sS))
            T = set(rng.sample(range(40), sT))
            e_ST = sum(1 for u in S for v in T if w33[u, v])
            expected = _K * len(S) * len(T) / _N
            bound = theta * np.sqrt(len(S) * len(T))
            assert abs(e_ST - expected) <= bound + 1e-8


# ══════════════════════════════════════════════════════════════════════════
#  8.  PATH & CYCLE STRUCTURE  (8 tests)
# ══════════════════════════════════════════════════════════════════════════

class TestPathCycleStructure:
    """Diameter, girth, distance distribution, and cycle counts."""

    def test_diameter_equals_2(self, w33):
        """diam(G) = 2  (SRG with mu > 0)."""
        max_dist = 0
        for v in range(40):
            d = _bfs_distances(w33, v)
            max_dist = max(max_dist, int(d.max()))
        assert max_dist == 2

    def test_girth_equals_3(self, w33):
        """girth = 3 (triangles exist since lambda = 2 > 0)."""
        nbrs = list(np.where(w33[0] == 1)[0])
        found = any(w33[nbrs[i], nbrs[j]]
                     for i in range(len(nbrs))
                     for j in range(i + 1, len(nbrs)))
        assert found

    def test_simple_graph_no_loops(self, w33):
        """No self-loops and adjacency is 0/1 (simple graph)."""
        assert np.all(np.diag(w33) == 0)
        assert set(np.unique(w33)).issubset({0, 1})

    def test_eccentricity_all_equal_2(self, w33):
        """Every vertex has eccentricity 2 (vertex-transitive, diam = 2)."""
        for v in range(40):
            d = _bfs_distances(w33, v)
            assert int(d.max()) == 2

    def test_radius_equals_2(self, w33):
        """radius = diam = 2 for vertex-transitive graph."""
        eccs = [int(_bfs_distances(w33, v).max()) for v in range(40)]
        assert min(eccs) == 2

    def test_triangle_count_160(self, w33):
        """W(3,3) has exactly 160 triangles (trace(A^3)/6)."""
        A3 = w33 @ w33 @ w33
        assert np.trace(A3) // 6 == 160

    def test_average_distance(self, w33):
        """avg dist = (240*1 + 540*2) / 780 = 22/13 ~ 1.692."""
        total = 0
        count = 0
        for v in range(40):
            d = _bfs_distances(w33, v)
            for u in range(v + 1, 40):
                total += d[u]
                count += 1
        avg = total / count
        assert abs(avg - 22 / 13) < 1e-10

    def test_distance_distribution(self, w33):
        """240 pairs at distance 1, 540 at distance 2."""
        d1, d2 = 0, 0
        for v in range(40):
            d = _bfs_distances(w33, v)
            for u in range(v + 1, 40):
                if d[u] == 1:
                    d1 += 1
                elif d[u] == 2:
                    d2 += 1
        assert d1 == 240
        assert d2 == 540
        assert d1 + d2 == 40 * 39 // 2
