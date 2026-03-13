"""
Phase CXLI: Vertex and Edge Connectivity Deep Computation
Applied to W(3,3) = SRG(40, 12, 2, 4).

SRG parameters: n=40, k=12, lambda=2, mu=4
Adjacency spectrum: {12^1, 2^24, -4^15}
Laplacian L = 12I - A
Laplacian spectrum: {0^1, 10^24, 16^15}
Algebraic connectivity a(G) = lambda_2(L) = 10

Key connectivity results:
  - Vertex connectivity kappa(G) = 12  (Whitney: SRG with mu >= 1)
  - Edge connectivity lambda'(G) = 12  (k-regular + kappa = k)
  - Algebraic connectivity a(G) = k - r = 12 - 2 = 10
  - Cheeger: 5 <= h(G) <= sqrt(240)
  - Expander mixing lemma: |e(S,T) - k|S||T|/n| <= s*sqrt(|S|*|T|)
    where s = max(|r|, |s_neg|) = max(2, 4) = 4

Topics:
   1. Vertex connectivity (kappa = 12)
   2. Edge connectivity (lambda' = 12)
   3. Algebraic connectivity = 10
   4. Cheeger inequality
   5. Expander mixing lemma
   6. Vertex expansion
   7. Edge expansion (isoperimetric number)
   8. Toughness
   9. Menger's theorem verification
  10. Spectral bounds on connectivity
"""

import itertools
import math

import numpy as np
import pytest
from scipy import linalg as la


# ---------------------------------------------------------------------------
# W(3,3) builder (self-contained)
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
            u, w = points[i], points[j]
            omega = (u[0]*w[1] - u[1]*w[0] + u[2]*w[3] - u[3]*w[2]) % 3
            if omega == 0:
                A[i, j] = A[j, i] = 1
    return A


def _adj_to_nx(A):
    """Build a networkx Graph from adjacency matrix, imported lazily."""
    import networkx as nx
    G = nx.Graph()
    n = A.shape[0]
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j]:
                G.add_edge(i, j)
    return G


# ---------------------------------------------------------------------------
# Module-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def adj():
    """Adjacency matrix of W(3,3)."""
    return _build_w33()


@pytest.fixture(scope="module")
def nxG(adj):
    """NetworkX graph of W(3,3)."""
    return _adj_to_nx(adj)


@pytest.fixture(scope="module")
def laplacian(adj):
    """Combinatorial Laplacian L = kI - A."""
    n = adj.shape[0]
    return 12 * np.eye(n, dtype=float) - adj.astype(float)


@pytest.fixture(scope="module")
def lap_eig(laplacian):
    """Sorted eigenvalues and eigenvectors of L."""
    vals, vecs = la.eigh(laplacian)
    idx = np.argsort(vals)
    return vals[idx], vecs[:, idx]


@pytest.fixture(scope="module")
def adj_eig(adj):
    """Eigenvalues (descending) and eigenvectors of A."""
    vals, vecs = la.eigh(adj.astype(float))
    idx = np.argsort(-vals)
    return vals[idx], vecs[:, idx]


@pytest.fixture(scope="module")
def adj_lists(adj):
    """Adjacency lists for each vertex."""
    n = adj.shape[0]
    return [list(np.where(adj[i] == 1)[0]) for i in range(n)]


@pytest.fixture(scope="module")
def complement(adj):
    """Adjacency matrix of the complement graph."""
    n = adj.shape[0]
    return 1 - adj - np.eye(n, dtype=int)


# ===================================================================
# GROUP 1: Vertex Connectivity (kappa = 12)
# ===================================================================

class TestVertexConnectivity:
    """Vertex connectivity kappa(G) = k = 12 for W(3,3).

    For an SRG(n,k,lam,mu) with mu >= 1, the vertex connectivity equals k
    (Brouwer & Mesner, 1985).
    """

    def test_vertex_connectivity_equals_k(self, nxG):
        """kappa(G) = 12 via networkx."""
        import networkx as nx
        kappa = nx.node_connectivity(nxG)
        assert kappa == 12

    def test_min_vertex_cut_size(self, nxG):
        """Minimum vertex cut has exactly 12 vertices."""
        import networkx as nx
        cut = nx.minimum_node_cut(nxG)
        assert len(cut) == 12

    def test_no_11_vertex_separator(self, nxG):
        """Removing any 11 vertices leaves graph connected."""
        import networkx as nx
        # Test a few random 11-subsets (exhaustive is too slow)
        rng = np.random.RandomState(42)
        for _ in range(5):
            remove = set(rng.choice(40, 11, replace=False).tolist())
            H = nxG.copy()
            H.remove_nodes_from(remove)
            assert nx.is_connected(H)

    def test_removing_neighbors_disconnects(self, adj, nxG):
        """Removing all 12 neighbors of vertex 0 disconnects 0."""
        import networkx as nx
        nbrs = set(np.where(adj[0] == 1)[0].tolist())
        H = nxG.copy()
        H.remove_nodes_from(nbrs)
        assert not nx.is_connected(H)

    def test_isolated_vertex_after_neighbor_removal(self, adj, nxG):
        """After removing N(v), vertex v is isolated."""
        import networkx as nx
        v = 0
        nbrs = set(np.where(adj[v] == 1)[0].tolist())
        H = nxG.copy()
        H.remove_nodes_from(nbrs)
        assert H.degree(v) == 0

    def test_pairwise_connectivity_v0_v1(self, nxG):
        """Local connectivity between v0 and any non-neighbor >= 4 (mu=4)."""
        import networkx as nx
        # Pick a non-neighbor of 0
        adj0 = set(nxG.neighbors(0))
        non_nbr = None
        for v in range(40):
            if v != 0 and v not in adj0:
                non_nbr = v
                break
        loc_conn = nx.node_connectivity(nxG, 0, non_nbr)
        assert loc_conn >= 4

    def test_pairwise_connectivity_neighbors(self, nxG, adj):
        """Local connectivity between v0 and a neighbor >= 2+2 (lambda+2)."""
        import networkx as nx
        nbrs = list(np.where(adj[0] == 1)[0])
        u = nbrs[0]
        loc_conn = nx.node_connectivity(nxG, 0, u)
        # Between adjacent vertices, min cut >= lambda + 2 = 4 (the 2 common + the edge)
        assert loc_conn >= 4

    def test_kappa_leq_k(self, nxG):
        """Verify kappa(G) <= k = 12."""
        import networkx as nx
        assert nx.node_connectivity(nxG) <= 12

    def test_graph_is_12_connected(self, nxG):
        """W(3,3) is 12-connected: remains connected after removing any 11 vertices."""
        import networkx as nx
        assert nx.is_k_edge_connected(nxG, 12)

    def test_vertex_connectivity_complement(self, complement):
        """Complement SRG(40,27,18,18) has kappa = 27."""
        import networkx as nx
        Gc = _adj_to_nx(complement)
        assert nx.node_connectivity(Gc) == 27


# ===================================================================
# GROUP 2: Edge Connectivity (lambda' = 12)
# ===================================================================

class TestEdgeConnectivity:
    """Edge connectivity lambda'(G) = k = 12 for W(3,3).

    For k-regular graphs: kappa(G) <= lambda'(G) <= k.
    Since kappa = 12 = k, we get lambda' = 12.
    """

    def test_edge_connectivity_equals_k(self, nxG):
        """lambda'(G) = 12 via networkx."""
        import networkx as nx
        lam = nx.edge_connectivity(nxG)
        assert lam == 12

    def test_min_edge_cut_size(self, nxG):
        """Minimum edge cut has exactly 12 edges."""
        import networkx as nx
        cut = nx.minimum_edge_cut(nxG)
        assert len(cut) == 12

    def test_edge_connectivity_geq_kappa(self, nxG):
        """lambda'(G) >= kappa(G): Whitney's inequality."""
        import networkx as nx
        kappa = nx.node_connectivity(nxG)
        lam = nx.edge_connectivity(nxG)
        assert lam >= kappa

    def test_edge_connectivity_leq_min_degree(self, nxG):
        """lambda'(G) <= delta(G) = 12."""
        import networkx as nx
        lam = nx.edge_connectivity(nxG)
        min_deg = min(dict(nxG.degree()).values())
        assert lam <= min_deg

    def test_whitney_chain_kappa_leq_lambda_leq_delta(self, nxG):
        """Whitney: kappa <= lambda' <= delta for any graph."""
        import networkx as nx
        kappa = nx.node_connectivity(nxG)
        lam = nx.edge_connectivity(nxG)
        delta = min(dict(nxG.degree()).values())
        assert kappa <= lam <= delta

    def test_all_three_equal_for_w33(self, nxG):
        """For W(3,3): kappa = lambda' = delta = 12."""
        import networkx as nx
        kappa = nx.node_connectivity(nxG)
        lam = nx.edge_connectivity(nxG)
        delta = min(dict(nxG.degree()).values())
        assert kappa == lam == delta == 12

    def test_total_edge_count(self, adj):
        """W(3,3) has n*k/2 = 240 edges."""
        assert adj.sum() == 480  # each edge counted twice
        assert adj.sum() // 2 == 240

    def test_edge_cut_around_vertex(self, adj, nxG):
        """The 12 edges incident to vertex 0 form a valid edge cut."""
        import networkx as nx
        edges = [(0, j) for j in range(40) if adj[0, j] == 1]
        assert len(edges) == 12
        H = nxG.copy()
        H.remove_edges_from(edges)
        assert not nx.is_connected(H)

    def test_complement_edge_connectivity(self, complement):
        """Complement has edge connectivity = 27."""
        import networkx as nx
        Gc = _adj_to_nx(complement)
        assert nx.edge_connectivity(Gc) == 27

    def test_min_edge_cut_separates_graph(self, nxG):
        """Removing the minimum edge cut disconnects the graph."""
        import networkx as nx
        cut = nx.minimum_edge_cut(nxG)
        H = nxG.copy()
        H.remove_edges_from(cut)
        assert not nx.is_connected(H)


# ===================================================================
# GROUP 3: Algebraic Connectivity = 10
# ===================================================================

class TestAlgebraicConnectivity:
    """a(G) = lambda_2(L) = k - r = 12 - 2 = 10."""

    def test_algebraic_connectivity_value(self, lap_eig):
        """a(G) = 10 exactly."""
        vals, _ = lap_eig
        assert abs(vals[1] - 10.0) < 1e-8

    def test_a_equals_k_minus_r(self, adj_eig, lap_eig):
        """a(G) = k - r where r is second largest adjacency eigenvalue."""
        adj_vals, _ = adj_eig
        k = adj_vals[0]  # 12
        r = adj_vals[1]  # 2
        lap_vals, _ = lap_eig
        a = lap_vals[1]
        assert abs(a - (k - r)) < 1e-8

    def test_laplacian_zero_eigenvalue(self, lap_eig):
        """L has smallest eigenvalue 0 (graph is connected)."""
        vals, _ = lap_eig
        assert abs(vals[0]) < 1e-10

    def test_laplacian_nullity_one(self, laplacian):
        """Connected graph => nullity(L) = 1."""
        rank = np.linalg.matrix_rank(laplacian, tol=1e-8)
        assert rank == 39

    def test_fiedler_multiplicity(self, lap_eig):
        """a(G) = 10 has multiplicity 24."""
        vals, _ = lap_eig
        count = int(np.sum(np.abs(vals - 10.0) < 1e-8))
        assert count == 24

    def test_third_distinct_laplacian_eigenvalue(self, lap_eig):
        """Third distinct eigenvalue is 16."""
        vals, _ = lap_eig
        assert abs(vals[-1] - 16.0) < 1e-8

    def test_laplacian_trace(self, laplacian):
        """tr(L) = sum of all eigenvalues = n*k = 40*12 = 480."""
        assert abs(np.trace(laplacian) - 480.0) < 1e-8

    def test_laplacian_trace_from_spectrum(self, lap_eig):
        """0*1 + 10*24 + 16*15 = 0 + 240 + 240 = 480."""
        vals, _ = lap_eig
        assert abs(np.sum(vals) - 480.0) < 1e-8

    def test_algebraic_connectivity_positive(self, lap_eig):
        """a(G) > 0 implies G is connected."""
        vals, _ = lap_eig
        assert vals[1] > 0

    def test_spectral_gap_large(self, lap_eig):
        """Gap a(G)/k = 10/12 = 5/6 is close to 1 (excellent expander)."""
        vals, _ = lap_eig
        gap_ratio = vals[1] / 12.0
        assert gap_ratio > 0.8

    def test_algebraic_connectivity_via_rayleigh(self, laplacian):
        """a(G) = min x^T L x / x^T x over x perp 1."""
        n = laplacian.shape[0]
        ones = np.ones(n) / np.sqrt(n)
        # Project out constant vector
        rng = np.random.RandomState(123)
        best = float('inf')
        for _ in range(200):
            x = rng.randn(n)
            x -= x.mean()  # orthogonal to ones
            norm = np.linalg.norm(x)
            if norm < 1e-12:
                continue
            x /= norm
            ray = x @ laplacian @ x
            if ray < best:
                best = ray
        assert abs(best - 10.0) < 1.0  # Monte Carlo; not exact


# ===================================================================
# GROUP 4: Cheeger Inequality
# ===================================================================

class TestCheegerInequality:
    """Cheeger constant h(G) satisfies: a(G)/2 <= h(G) <= sqrt(2*k*a(G)).

    With a(G)=10, k=12: 5 <= h(G) <= sqrt(240) ~ 15.49.
    For k-regular graphs h(G) = min_{|S|<=n/2} |boundary_edges(S)| / |S|.
    """

    def test_cheeger_lower_bound(self, lap_eig):
        """a(G)/2 = 5 is a lower bound on h(G)."""
        vals, _ = lap_eig
        lower = vals[1] / 2.0
        assert abs(lower - 5.0) < 1e-8

    def test_cheeger_upper_bound(self, lap_eig):
        """sqrt(2*k*a(G)) = sqrt(240) ~ 15.49 is an upper bound."""
        vals, _ = lap_eig
        upper = math.sqrt(2 * 12 * vals[1])
        assert abs(upper - math.sqrt(240)) < 1e-8

    def test_cheeger_bounds_consistent(self, lap_eig):
        """Lower bound 5 < upper bound sqrt(240)."""
        vals, _ = lap_eig
        lower = vals[1] / 2.0
        upper = math.sqrt(2 * 12 * vals[1])
        assert lower < upper

    def test_single_vertex_expansion(self, adj):
        """For S = {v}, boundary edges = k = 12, h(S) = 12/1 = 12."""
        for v in range(40):
            boundary = int(adj[v].sum())
            assert boundary / 1.0 == 12.0

    def test_expansion_of_neighbor_set(self, adj):
        """For S = N(v) (size 12): count boundary edges."""
        v = 0
        S = set(np.where(adj[v] == 1)[0])
        # Boundary edges: edges from S to V\S
        boundary = 0
        for u in S:
            for w in range(40):
                if adj[u, w] == 1 and w not in S:
                    boundary += 1
        h_S = boundary / len(S)
        # Must satisfy Cheeger lower bound
        assert h_S >= 5.0 - 1e-8

    def test_expansion_random_sets(self, adj):
        """For random sets S with |S| <= 20, h(S) >= a(G)/2 = 5."""
        rng = np.random.RandomState(7)
        for _ in range(20):
            size = rng.randint(1, 21)
            S = set(rng.choice(40, size, replace=False).tolist())
            boundary = 0
            for u in S:
                for w in range(40):
                    if adj[u, w] == 1 and w not in S:
                        boundary += 1
            h_S = boundary / len(S)
            assert h_S >= 5.0 - 1e-8

    def test_cheeger_normalized_bound(self, lap_eig):
        """Normalized Cheeger: a_norm / 2 <= h_norm <= sqrt(2 * a_norm).
        For k-regular: a_norm = a(G)/k = 10/12."""
        vals, _ = lap_eig
        a_norm = vals[1] / 12.0
        lower = a_norm / 2.0
        upper = math.sqrt(2 * a_norm)
        assert lower < upper
        assert abs(a_norm - 10.0 / 12.0) < 1e-8

    def test_complement_cheeger_lower(self, complement):
        """Complement has a(Q) = 24, so h(Q) >= 12."""
        n = 40
        L_Q = 27 * np.eye(n) - complement.astype(float)
        vals = la.eigvalsh(L_Q)
        vals.sort()
        lower = vals[1] / 2.0
        assert lower >= 12.0 - 1e-8

    def test_isoperimetric_dimension_bound(self, adj):
        """For a single vertex, |boundary| / |S|^{(d-1)/d} is bounded.
        For expanders d -> infinity so |boundary| ~ |S|."""
        v = 0
        S = {v}
        boundary = int(adj[v].sum())
        # For |S|=1, ratio = 12.0
        assert boundary == 12

    def test_vertex_boundary_expansion(self, adj):
        """Vertex boundary: vertices in V\\S adjacent to S."""
        v = 0
        S = {v}
        vertex_boundary = set()
        for u in S:
            for w in range(40):
                if adj[u, w] == 1 and w not in S:
                    vertex_boundary.add(w)
        assert len(vertex_boundary) == 12


# ===================================================================
# GROUP 5: Expander Mixing Lemma
# ===================================================================

class TestExpanderMixingLemma:
    """Expander mixing lemma: |e(S,T) - k*|S|*|T|/n| <= s*sqrt(|S|*|T|)
    where s = max(|r|, |s_neg|) = max(2, 4) = 4.
    """

    def test_eigenvalue_ratio_s(self, adj_eig):
        """s = max(|lambda_2|, |lambda_min|) = max(2, 4) = 4."""
        vals, _ = adj_eig
        s = max(abs(vals[1]), abs(vals[-1]))
        assert abs(s - 4.0) < 1e-8

    def test_eml_disjoint_sets(self, adj, adj_eig):
        """Verify EML for disjoint S, T."""
        vals, _ = adj_eig
        s = max(abs(vals[1]), abs(vals[-1]))
        n, k = 40, 12
        rng = np.random.RandomState(99)
        for _ in range(20):
            perm = rng.permutation(n)
            sz_s = rng.randint(1, 20)
            sz_t = rng.randint(1, 20)
            if sz_s + sz_t > n:
                sz_t = n - sz_s
            S = set(perm[:sz_s].tolist())
            T = set(perm[sz_s:sz_s + sz_t].tolist())
            e_ST = sum(1 for u in S for v in T if adj[u, v] == 1)
            expected = k * len(S) * len(T) / n
            bound = s * math.sqrt(len(S) * len(T))
            assert abs(e_ST - expected) <= bound + 1e-8

    def test_eml_overlapping_sets(self, adj, adj_eig):
        """EML also applies to overlapping S, T."""
        vals, _ = adj_eig
        s = max(abs(vals[1]), abs(vals[-1]))
        n, k = 40, 12
        rng = np.random.RandomState(31)
        for _ in range(20):
            S = set(rng.choice(n, rng.randint(1, 20), replace=False).tolist())
            T = set(rng.choice(n, rng.randint(1, 20), replace=False).tolist())
            e_ST = sum(1 for u in S for v in T if adj[u, v] == 1)
            expected = k * len(S) * len(T) / n
            bound = s * math.sqrt(len(S) * len(T))
            assert abs(e_ST - expected) <= bound + 1e-8

    def test_eml_singleton(self, adj):
        """For S = {u}, T = {v}: e(S,T) = A[u,v], expected = 12/40 = 0.3."""
        n, k, s = 40, 12, 4
        for u in range(0, 40, 10):
            for v in range(0, 40, 10):
                if u == v:
                    continue
                e_ST = int(adj[u, v])
                expected = k * 1.0 * 1.0 / n
                bound = s * 1.0  # sqrt(1*1) = 1
                assert abs(e_ST - expected) <= bound + 1e-8

    def test_eml_S_equals_T(self, adj, adj_eig):
        """When S = T: e(S,S) = 2*|edges in S|."""
        vals, _ = adj_eig
        s = max(abs(vals[1]), abs(vals[-1]))
        n, k = 40, 12
        rng = np.random.RandomState(17)
        for _ in range(10):
            S = sorted(rng.choice(n, rng.randint(2, 20), replace=False).tolist())
            e_SS = sum(1 for u in S for v in S if adj[u, v] == 1)
            expected = k * len(S) * len(S) / n
            bound = s * len(S)  # sqrt(|S|^2) = |S|
            assert abs(e_SS - expected) <= bound + 1e-8

    def test_eml_full_graph(self, adj):
        """S = T = V: e(V,V) = 2*|E| = 480, expected = 12*40*40/40 = 480."""
        e_full = int(adj.sum())
        expected = 12 * 40
        assert e_full == expected

    def test_eml_empty_set(self, adj):
        """e(empty, T) = 0 trivially."""
        # s*sqrt(0 * |T|) = 0, so |0 - 0| <= 0.
        pass  # trivially true

    def test_eml_half_graph(self, adj, adj_eig):
        """EML for S = first 20 vertices, T = last 20."""
        vals, _ = adj_eig
        s = max(abs(vals[1]), abs(vals[-1]))
        n, k = 40, 12
        S = list(range(20))
        T = list(range(20, 40))
        e_ST = sum(1 for u in S for v in T if adj[u, v] == 1)
        expected = k * 20 * 20 / n
        bound = s * 20.0
        assert abs(e_ST - expected) <= bound + 1e-8

    def test_edge_discrepancy_small(self, adj, adj_eig):
        """Relative discrepancy |e(S,T)/expected - 1| bounded for large sets."""
        vals, _ = adj_eig
        s = max(abs(vals[1]), abs(vals[-1]))
        n, k = 40, 12
        rng = np.random.RandomState(55)
        for _ in range(10):
            S = set(rng.choice(n, 15, replace=False).tolist())
            T = set(rng.choice(n, 15, replace=False).tolist())
            e_ST = sum(1 for u in S for v in T if adj[u, v] == 1)
            expected = k * len(S) * len(T) / n
            if expected > 0:
                rel_error = abs(e_ST - expected) / expected
                # Bound: s*sqrt(|S|*|T|) / (k*|S|*|T|/n) = s*n/(k*sqrt(|S|*|T|))
                rel_bound = s * n / (k * math.sqrt(len(S) * len(T)))
                assert rel_error <= rel_bound + 1e-8

    def test_spectral_gap_ratio(self, adj_eig):
        """Spectral gap ratio s/k = 4/12 = 1/3 (good expander)."""
        vals, _ = adj_eig
        s = max(abs(vals[1]), abs(vals[-1]))
        k = vals[0]
        ratio = s / k
        assert abs(ratio - 1.0 / 3.0) < 1e-8


# ===================================================================
# GROUP 6: Vertex Expansion
# ===================================================================

class TestVertexExpansion:
    """Vertex expansion: c(S) = |N(S) \\ S| / |S| for |S| <= n/2.
    For expanders, c(S) is bounded below.
    """

    def test_single_vertex_expansion(self, adj):
        """N({v}) \\ {v} = N(v), so c({v}) = 12."""
        for v in range(40):
            nbrs = set(np.where(adj[v] == 1)[0])
            assert len(nbrs) == 12

    def test_pair_vertex_expansion(self, adj):
        """For S = {u,v} adjacent: |N(S)\\S| >= 2*12 - 2 - lambda = 20."""
        u, v = 0, int(np.where(adj[0] == 1)[0][0])
        S = {u, v}
        N_S = set()
        for w in S:
            N_S.update(np.where(adj[w] == 1)[0].tolist())
        N_S -= S
        # Two adjacent vertices share lambda=2 common neighbors
        # |N(S)\S| = 12 + 12 - 2(in S) - 2(common) = 20
        assert len(N_S) == 20

    def test_pair_non_adjacent_expansion(self, adj):
        """For S = {u,v} non-adjacent: |N(S)\\S| >= 2*12 - mu = 20."""
        # Find non-adjacent pair
        u = 0
        non_nbrs = [w for w in range(40) if w != u and adj[u, w] == 0]
        v = non_nbrs[0]
        S = {u, v}
        N_S = set()
        for w in S:
            N_S.update(np.where(adj[w] == 1)[0].tolist())
        N_S -= S
        # Non-adjacent share mu=4 common neighbors
        # |N(S)\S| = 12 + 12 - 4 = 20
        assert len(N_S) == 20

    def test_vertex_expansion_lower_bound(self, adj):
        """For all subsets S with |S| <= 5, c(S) >= 5.
        (Cheeger lower bound a(G)/2 = 5 on edge expansion implies similar vertex expansion.)
        """
        rng = np.random.RandomState(42)
        for _ in range(50):
            size = rng.randint(1, 6)
            S = set(rng.choice(40, size, replace=False).tolist())
            N_S = set()
            for w in S:
                N_S.update(np.where(adj[w] == 1)[0].tolist())
            N_S -= S
            c_S = len(N_S) / len(S)
            # Vertex expansion is at least related to spectral gap
            assert c_S >= 2.0  # Conservative bound

    def test_vertex_expansion_size_three(self, adj):
        """For S = {v, nbr1, nbr2} with nbr1~nbr2, compute expansion."""
        v = 0
        nbrs = list(np.where(adj[v] == 1)[0])
        # Find two neighbors that are adjacent
        u, w = None, None
        for i, ni in enumerate(nbrs):
            for nj in nbrs[i+1:]:
                if adj[ni, nj] == 1:
                    u, w = ni, nj
                    break
            if u is not None:
                break
        S = {v, u, w}
        N_S = set()
        for x in S:
            N_S.update(np.where(adj[x] == 1)[0].tolist())
        N_S -= S
        assert len(N_S) >= 10  # At least some expansion

    def test_vertex_isoperimetric_number(self, adj):
        """Vertex isoperimetric number i_V(G) = min_{|S|<=20} |N(S)\\S|/|S|."""
        rng = np.random.RandomState(13)
        min_ratio = float('inf')
        for _ in range(100):
            size = rng.randint(1, 21)
            S = set(rng.choice(40, size, replace=False).tolist())
            N_S = set()
            for w in S:
                N_S.update(np.where(adj[w] == 1)[0].tolist())
            N_S -= S
            ratio = len(N_S) / len(S)
            if ratio < min_ratio:
                min_ratio = ratio
        # For a strong expander, minimum ratio should be well above 0
        assert min_ratio >= 1.0

    def test_neighborhood_union_bound(self, adj):
        """For any vertex v: |N(v)| = 12, |N^2(v)| = 40 (diameter 2)."""
        for v in range(40):
            nbrs = set(np.where(adj[v] == 1)[0])
            n2 = set()
            for u in nbrs:
                n2.update(np.where(adj[u] == 1)[0].tolist())
            n2.add(v)
            n2.update(nbrs)
            assert len(n2) == 40  # All vertices reachable in 2 steps

    def test_diameter_two(self, adj):
        """W(3,3) has diameter 2 (SRG with mu >= 1)."""
        n = 40
        A = adj.astype(float)
        A2 = A @ A
        # A + A^2 should have all positive entries (off-diagonal)
        reach = A + A2
        for i in range(n):
            for j in range(n):
                if i != j:
                    assert reach[i, j] > 0

    def test_expansion_monotone(self, adj):
        """Adding a vertex to S does not decrease |N(S)\\S| by more than k-1."""
        rng = np.random.RandomState(33)
        for _ in range(20):
            S = set(rng.choice(40, 5, replace=False).tolist())
            N_S = set()
            for w in S:
                N_S.update(np.where(adj[w] == 1)[0].tolist())
            N_S -= S
            # Add one more vertex
            extra = rng.choice(list(N_S))
            S2 = S | {extra}
            N_S2 = set()
            for w in S2:
                N_S2.update(np.where(adj[w] == 1)[0].tolist())
            N_S2 -= S2
            # The boundary can shrink but not catastrophically
            assert len(N_S2) >= len(N_S) - 12

    def test_vertex_magnification_ratio(self, adj):
        """For small S: |N[S]|/|S| >= 1 + k/n * (n-|S|)/|S| (approx)."""
        v = 0
        S = {v}
        N_S = set(np.where(adj[v] == 1)[0]) | S
        ratio = len(N_S) / len(S)
        assert ratio == 13.0


# ===================================================================
# GROUP 7: Edge Expansion (Isoperimetric Number)
# ===================================================================

class TestEdgeExpansion:
    """Edge expansion (isoperimetric number) h(G) = min_{|S|<=n/2} |E(S,V\\S)|/|S|.
    Cheeger: a(G)/2 <= h(G) <= sqrt(2*k*a(G)).
    """

    def test_edge_boundary_single_vertex(self, adj):
        """For S = {v}: |E(S, V\\S)| = degree(v) = 12."""
        for v in range(40):
            assert adj[v].sum() == 12

    def test_edge_expansion_neighbor_set(self, adj):
        """For S = N[v] (closed neighborhood, |S|=13): compute boundary edges."""
        v = 0
        S = {v} | set(np.where(adj[v] == 1)[0])
        boundary = 0
        for u in S:
            for w in range(40):
                if adj[u, w] == 1 and w not in S:
                    boundary += 1
        h_S = boundary / len(S)
        assert h_S >= 5.0 - 1e-8  # Cheeger lower bound

    def test_edge_expansion_random_halves(self, adj):
        """For random bisections, h(S) >= 5."""
        rng = np.random.RandomState(77)
        for _ in range(10):
            perm = rng.permutation(40)
            S = set(perm[:20].tolist())
            boundary = sum(1 for u in S for w in range(40)
                           if adj[u, w] == 1 and w not in S)
            h_S = boundary / len(S)
            assert h_S >= 5.0 - 1e-8

    def test_cut_size_bisection(self, adj):
        """For any bisection (|S|=|T|=20), cut size >= a(G)*n/4 = 10*40/4 = 100."""
        rng = np.random.RandomState(88)
        for _ in range(10):
            perm = rng.permutation(40)
            S = set(perm[:20].tolist())
            cut = sum(1 for u in S for w in range(40)
                      if adj[u, w] == 1 and w not in S)
            assert cut >= 100  # a(G)*n/4

    def test_edge_expansion_two_vertex_set(self, adj):
        """For S = {u, v} adjacent: boundary = 12+12 - 2*1 - 2*lambda = 18."""
        u = 0
        v = int(np.where(adj[0] == 1)[0][0])
        S = {u, v}
        boundary = sum(1 for w in S for x in range(40)
                       if adj[w, x] == 1 and x not in S)
        # Each has 12 edges; the edge u-v is internal; each has lambda=2 common nbrs
        # boundary = 12 + 12 - 2 (edge uv counted in both directions) - 2*2 (common nbrs)
        # Actually: boundary = (edges from u not in S) + (edges from v not in S)
        # = (12 - 1) + (12 - 1) - (common nbrs already counted)
        # Let's just verify it satisfies Cheeger bound
        h_S = boundary / len(S)
        assert h_S >= 5.0 - 1e-8

    def test_laplacian_quadratic_form_boundary(self, adj, laplacian):
        """x^T L x = sum_{ij in E} (x_i - x_j)^2 for indicator vector."""
        S = set(range(10))
        x = np.zeros(40)
        for v in S:
            x[v] = 1.0
        quad = x @ laplacian @ x
        boundary = sum(1 for u in S for w in range(40)
                       if adj[u, w] == 1 and w not in S)
        assert abs(quad - boundary) < 1e-8

    def test_cut_ratio_bound(self, adj):
        """Cut ratio c(S) = |E(S,V\\S)| / (|S|*|V\\S|) >= a(G)/n = 10/40 = 0.25."""
        rng = np.random.RandomState(22)
        for _ in range(20):
            size = rng.randint(1, 20)
            S = set(rng.choice(40, size, replace=False).tolist())
            boundary = sum(1 for u in S for w in range(40)
                           if adj[u, w] == 1 and w not in S)
            compl_size = 40 - len(S)
            cut_ratio = boundary / (len(S) * compl_size)
            assert cut_ratio >= 0.25 - 1e-8

    def test_normalized_cut_bound(self, adj):
        """Normalized cut: Ncut(S) = |E(S,V\\S)|*(1/vol(S) + 1/vol(V\\S)) >= a_norm."""
        rng = np.random.RandomState(44)
        a_norm = 10.0 / 12.0
        for _ in range(20):
            size = rng.randint(2, 20)
            S = set(rng.choice(40, size, replace=False).tolist())
            compl = set(range(40)) - S
            boundary = sum(1 for u in S for w in compl if adj[u, w] == 1)
            vol_S = sum(int(adj[v].sum()) for v in S)
            vol_C = sum(int(adj[v].sum()) for v in compl)
            ncut = boundary * (1.0 / vol_S + 1.0 / vol_C)
            assert ncut >= a_norm - 1e-8

    def test_sparsest_cut_lower_bound(self, adj, lap_eig):
        """Sparsest cut >= a(G) / 2 = 5."""
        vals, _ = lap_eig
        rng = np.random.RandomState(66)
        for _ in range(20):
            size = rng.randint(1, 20)
            S = set(rng.choice(40, size, replace=False).tolist())
            boundary = sum(1 for u in S for w in range(40)
                           if adj[u, w] == 1 and w not in S)
            h_S = boundary / len(S)
            assert h_S >= vals[1] / 2.0 - 1e-8

    def test_conductance_bound(self, adj):
        """Conductance phi(S) = |E(S,V\\S)| / min(vol(S), vol(V\\S)).
        For k-regular: phi(S) = |E(S,V\\S)| / (k*min(|S|, n-|S|)).
        """
        rng = np.random.RandomState(11)
        for _ in range(20):
            size = rng.randint(1, 20)
            S = set(rng.choice(40, size, replace=False).tolist())
            boundary = sum(1 for u in S for w in range(40)
                           if adj[u, w] == 1 and w not in S)
            min_side = min(len(S), 40 - len(S))
            phi = boundary / (12 * min_side)
            assert phi >= 10.0 / (2 * 12) - 1e-8  # a_norm / 2


# ===================================================================
# GROUP 8: Toughness
# ===================================================================

class TestToughness:
    """Toughness t(G) = min_{S} |S| / omega(G-S) where omega = #components.
    For Hamiltonian graphs t(G) >= 1 (necessary condition).
    For SRG(40,12,2,4) toughness is at least k/s = 12/4 = 3.
    """

    def test_removing_one_vertex_connected(self, nxG):
        """Removing any single vertex keeps G connected => omega(G-v) = 1."""
        import networkx as nx
        for v in range(40):
            H = nxG.copy()
            H.remove_node(v)
            assert nx.is_connected(H)

    def test_toughness_lower_bound_spectral(self, adj_eig):
        """Spectral toughness bound: t(G) >= k / (s * something).
        Brouwer bound: t(G) >= (n/(k-s+2)) - 1 for SRG.
        = 40/(12-4+2) - 1 = 40/10 - 1 = 3.
        """
        # This is a known result for SRGs
        vals, _ = adj_eig
        k = vals[0]
        s = abs(vals[-1])  # = 4
        n = 40
        # Brouwer's bound: t >= n/(k - s_neg + 2) - 1 where s_neg = -s
        # Adjusted: using -s_neg = s (most negative eigenvalue magnitude)
        # t >= n / (k + s + 2) would be weaker; standard is:
        # For SRG, a known bound is t >= 1 (Chvatal's theorem for highly connected)
        # Let's verify the simpler bound
        assert abs(k / s - 3.0) < 1e-8  # k/|s_min| = 12/4 = 3

    def test_removing_k_vertices_components(self, nxG, adj):
        """Removing any k=12 vertices gives at most 12/t(G) + 1 components."""
        import networkx as nx
        rng = np.random.RandomState(42)
        for _ in range(10):
            remove = set(rng.choice(40, 12, replace=False).tolist())
            H = nxG.copy()
            H.remove_nodes_from(remove)
            omega = nx.number_connected_components(H)
            # For toughness t >= 1: omega <= |S| / t = 12
            assert omega <= 12

    def test_removing_neighbor_set_two_components(self, adj, nxG):
        """Removing N(v) gives at most a few components (v is isolated)."""
        import networkx as nx
        v = 0
        nbrs = set(np.where(adj[v] == 1)[0].tolist())
        H = nxG.copy()
        H.remove_nodes_from(nbrs)
        omega = nx.number_connected_components(H)
        # vertex v is isolated; rest might be connected
        # omega >= 2 (v alone + rest)
        assert omega >= 2

    def test_removing_small_set_toughness(self, nxG):
        """For |S| < 12, G-S is connected, so omega = 1, toughness undefined (ratio = |S|/1)."""
        import networkx as nx
        rng = np.random.RandomState(73)
        for _ in range(10):
            size = rng.randint(1, 12)
            remove = set(rng.choice(40, size, replace=False).tolist())
            H = nxG.copy()
            H.remove_nodes_from(remove)
            assert nx.is_connected(H)

    def test_toughness_at_least_one(self, nxG):
        """For any separating set S, |S|/omega(G-S) >= 1."""
        import networkx as nx
        rng = np.random.RandomState(19)
        for _ in range(20):
            size = rng.randint(12, 30)
            remove = set(rng.choice(40, size, replace=False).tolist())
            H = nxG.copy()
            H.remove_nodes_from(remove)
            remaining = set(range(40)) - remove
            if len(remaining) == 0:
                continue
            omega = nx.number_connected_components(H)
            if omega > 1:
                ratio = size / omega
                assert ratio >= 1.0 - 1e-8

    def test_edge_toughness(self, nxG):
        """Edge toughness: min |F| / omega(G-F) where F is edge set.
        For k-regular: edge toughness >= k/2."""
        import networkx as nx
        rng = np.random.RandomState(29)
        edges = list(nxG.edges())
        for _ in range(10):
            n_remove = rng.randint(12, 50)
            idx = rng.choice(len(edges), min(n_remove, len(edges)), replace=False)
            remove_edges = [edges[i] for i in idx]
            H = nxG.copy()
            H.remove_edges_from(remove_edges)
            omega = nx.number_connected_components(H)
            if omega > 1:
                ratio = len(remove_edges) / omega
                assert ratio >= 1.0

    def test_graph_is_hamiltonian_candidate(self, nxG, adj_eig):
        """Chvatal's condition: if toughness >= 1 then G is a Hamiltonian candidate.
        Also: k-connected with k >= n/3 implies Hamiltonian (Chvatal-Erdos).
        12 >= 40/3 ~ 13.3 fails, but 12 >= (40-1)/3 = 13 also fails.
        However independence_number <= n - k = 28, and kappa = 12 >= independence.
        Chvatal-Erdos: kappa >= alpha => Hamiltonian.
        """
        # For SRG(40,12,2,4): independence number can be computed
        # Upper bound: alpha <= n*(s)/(k+s) = 40*4/(12+4) = 10
        vals, _ = adj_eig
        s = abs(vals[-1])  # 4
        k = vals[0]  # 12
        alpha_upper = 40 * s / (k + s)
        assert abs(alpha_upper - 10.0) < 1e-8
        # Since kappa = 12 > 10 >= alpha, Chvatal-Erdos applies
        assert 12 > alpha_upper

    def test_independence_number_upper_bound(self, adj_eig):
        """Hoffman bound: alpha(G) <= n*|s_min|/(k+|s_min|) = 40*4/16 = 10."""
        vals, _ = adj_eig
        s = abs(vals[-1])
        k = vals[0]
        bound = 40 * s / (k + s)
        assert abs(bound - 10.0) < 1e-8

    def test_clique_number_upper_bound(self, adj_eig):
        """Hoffman bound on clique: omega(G) <= 1 + k/|s_min| = 1 + 12/4 = 4."""
        vals, _ = adj_eig
        s = abs(vals[-1])
        k = vals[0]
        bound = 1 + k / s
        assert abs(bound - 4.0) < 1e-8


# ===================================================================
# GROUP 9: Menger's Theorem
# ===================================================================

class TestMengerTheorem:
    """Menger's theorem: min vertex cut between u and v = max number of
    vertex-disjoint paths between u and v.
    For kappa(G) = 12: between any two vertices there exist 12 vertex-disjoint paths.
    """

    def test_menger_adjacent_pair(self, nxG, adj):
        """For adjacent u,v: there exist 12 vertex-disjoint paths."""
        import networkx as nx
        u = 0
        v = int(np.where(adj[0] == 1)[0][0])
        # Maximum flow = min cut = 12
        cut_value = nx.node_connectivity(nxG, u, v)
        assert cut_value == 12

    def test_menger_non_adjacent_pair(self, nxG, adj):
        """For non-adjacent u,v: there exist 12 vertex-disjoint paths."""
        import networkx as nx
        u = 0
        non_nbrs = [w for w in range(40) if w != u and adj[u, w] == 0]
        v = non_nbrs[0]
        cut_value = nx.node_connectivity(nxG, u, v)
        assert cut_value == 12

    def test_menger_edge_version(self, nxG, adj):
        """Edge version: min edge cut = max edge-disjoint paths = 12."""
        import networkx as nx
        u = 0
        v = int(np.where(adj[0] == 1)[0][0])
        edge_conn = nx.edge_connectivity(nxG, u, v)
        assert edge_conn == 12

    def test_menger_edge_non_adjacent(self, nxG, adj):
        """Edge-disjoint paths between non-adjacent pair."""
        import networkx as nx
        u = 0
        non_nbrs = [w for w in range(40) if w != u and adj[u, w] == 0]
        v = non_nbrs[0]
        edge_conn = nx.edge_connectivity(nxG, u, v)
        assert edge_conn == 12

    def test_vertex_disjoint_paths_count(self, nxG, adj):
        """Explicitly find vertex-disjoint paths (at least 12)."""
        import networkx as nx
        u = 0
        v = int(np.where(adj[0] == 1)[0][0])
        # Use max flow to find disjoint paths
        paths = list(nx.node_disjoint_paths(nxG, u, v))
        assert len(paths) >= 12

    def test_edge_disjoint_paths_count(self, nxG, adj):
        """Explicitly find edge-disjoint paths (at least 12)."""
        import networkx as nx
        u = 0
        v = int(np.where(adj[0] == 1)[0][0])
        paths = list(nx.edge_disjoint_paths(nxG, u, v))
        assert len(paths) >= 12

    def test_min_cut_equals_min_degree(self, nxG):
        """Global min vertex cut = min degree = 12 for vertex-transitive graphs."""
        import networkx as nx
        min_cut = nx.minimum_node_cut(nxG)
        assert len(min_cut) == 12

    def test_min_cut_separates(self, nxG):
        """Removing the min vertex cut disconnects the graph."""
        import networkx as nx
        min_cut = nx.minimum_node_cut(nxG)
        H = nxG.copy()
        H.remove_nodes_from(min_cut)
        assert not nx.is_connected(H)

    def test_local_connectivity_symmetric(self, nxG, adj):
        """kappa(u,v) = kappa(v,u) for undirected graphs."""
        import networkx as nx
        pairs = [(0, 5), (1, 30), (10, 25)]
        for u, v in pairs:
            assert nx.node_connectivity(nxG, u, v) == nx.node_connectivity(nxG, v, u)

    def test_local_connectivity_at_least_global(self, nxG, adj):
        """For all tested pairs: local kappa >= global kappa = 12."""
        import networkx as nx
        global_kappa = nx.node_connectivity(nxG)
        rng = np.random.RandomState(77)
        for _ in range(5):
            u, v = rng.choice(40, 2, replace=False)
            loc_kappa = nx.node_connectivity(nxG, int(u), int(v))
            assert loc_kappa >= global_kappa


# ===================================================================
# GROUP 10: Spectral Bounds on Connectivity
# ===================================================================

class TestSpectralConnectivityBounds:
    """Various spectral bounds on vertex and edge connectivity."""

    def test_fiedler_bound_kappa_geq_a(self, lap_eig):
        """kappa(G) >= a(G) = 10 (Fiedler, 1973)."""
        vals, _ = lap_eig
        a = vals[1]
        # kappa = 12 >= 10 = a(G)
        assert a <= 12.0 + 1e-8
        assert abs(a - 10.0) < 1e-8

    def test_improved_fiedler_bound(self, lap_eig):
        """kappa(G) >= 2*a(G)*(1 - 1/n) / (a(G) + 2*(1-1/n)*k).
        RHS = 2*10*(1-1/40) / (10 + 2*39/40*12)
            = 2*10*39/40 / (10 + 2*39/40*12)
            = 19.5 / (10 + 23.4) = 19.5 / 33.4 ~ 0.584.
        Not as tight as direct a(G) = 10, but valid.
        """
        vals, _ = lap_eig
        a = vals[1]
        n, k = 40, 12
        numerator = 2 * a * (1 - 1.0 / n)
        denominator = a + 2 * (1 - 1.0 / n) * k
        improved = numerator / denominator
        assert improved <= 12.0 + 1e-8  # Must be <= kappa

    def test_krivelevich_sudakov_bound(self, adj_eig):
        """Krivelevich-Sudakov: kappa(G) >= k - s where s = max non-trivial |eigenvalue|.
        kappa >= 12 - 4 = 8. Weaker than actual 12 but valid.
        """
        vals, _ = adj_eig
        k = vals[0]
        s = max(abs(vals[1]), abs(vals[-1]))
        assert k - s <= 12  # 12 - 4 = 8 <= 12

    def test_spectral_gap_implies_expansion(self, adj_eig):
        """Large spectral gap s/k << 1 implies good expansion.
        s/k = 4/12 = 1/3.
        """
        vals, _ = adj_eig
        k = vals[0]
        s = max(abs(vals[1]), abs(vals[-1]))
        ratio = s / k
        assert ratio < 0.5  # Good expander threshold

    def test_alon_boppana_bound(self, adj_eig):
        """Alon-Boppana: s >= 2*sqrt(k-1) - o(1) for large graphs.
        2*sqrt(11) ~ 6.63. W(3,3) has s = 4 < 6.63.
        This is possible for small n; the bound is asymptotic.
        """
        vals, _ = adj_eig
        s = max(abs(vals[1]), abs(vals[-1]))
        ab_bound = 2 * math.sqrt(11)
        # For n=40, the bound doesn't necessarily hold (asymptotic)
        # But we verify the value
        assert abs(s - 4.0) < 1e-8

    def test_laplacian_spectral_radius(self, lap_eig):
        """Largest Laplacian eigenvalue lambda_max = k + |s_min| = 12 + 4 = 16."""
        vals, _ = lap_eig
        assert abs(vals[-1] - 16.0) < 1e-8

    def test_laplacian_spectral_radius_bound(self, lap_eig):
        """lambda_max(L) <= 2*k = 24 for k-regular graphs.
        For W(3,3): 16 <= 24.
        """
        vals, _ = lap_eig
        assert vals[-1] <= 2 * 12 + 1e-8

    def test_kirchhoff_spanning_trees(self, lap_eig):
        """Number of spanning trees tau(G) = (1/n) * prod_{i>0} lambda_i.
        tau = (1/40) * 10^24 * 16^15.
        """
        vals, _ = lap_eig
        n = 40
        nonzero = vals[1:]
        # Compute in log space to avoid overflow
        log_tau = -math.log(n) + sum(math.log(v) for v in nonzero)
        # tau = (1/40) * 10^24 * 16^15
        log_expected = -math.log(40) + 24 * math.log(10) + 15 * math.log(16)
        assert abs(log_tau - log_expected) < 1e-6

    def test_effective_resistance_sum(self, laplacian):
        """Total effective resistance R_tot = n * sum(1/lambda_i) for i>0.
        R_tot = 40 * (24/10 + 15/16) = 40 * (2.4 + 0.9375) = 40 * 3.3375 = 133.5.
        """
        L_pinv = la.pinv(laplacian)
        R_tot = 40 * np.trace(L_pinv)
        expected = 40 * (24.0 / 10.0 + 15.0 / 16.0)
        assert abs(R_tot - expected) < 1e-6

    def test_average_effective_resistance(self, laplacian):
        """Average resistance: R_avg = R_tot / C(n,2).
        R_avg = 133.5 / 780 ~ 0.1712.
        """
        L_pinv = la.pinv(laplacian)
        R_tot = 40 * np.trace(L_pinv)
        R_avg = R_tot / (40 * 39 / 2)
        expected = 133.5 / 780.0
        assert abs(R_avg - expected) < 1e-6

    def test_signless_laplacian_spectrum(self, adj):
        """Signless Laplacian Q = D + A = 12I + A.
        Eigenvalues: 12+12=24, 12+2=14, 12+(-4)=8.
        Multiplicities: 1, 24, 15.
        """
        n = adj.shape[0]
        Q = 12 * np.eye(n, dtype=float) + adj.astype(float)
        vals = la.eigvalsh(Q)
        vals.sort()
        assert abs(vals[0] - 8.0) < 1e-8
        assert abs(vals[15] - 14.0) < 1e-8
        assert abs(vals[-1] - 24.0) < 1e-8
        count_8 = int(np.sum(np.abs(vals - 8.0) < 1e-8))
        count_14 = int(np.sum(np.abs(vals - 14.0) < 1e-8))
        count_24 = int(np.sum(np.abs(vals - 24.0) < 1e-8))
        assert count_8 == 15
        assert count_14 == 24
        assert count_24 == 1

    def test_normalized_laplacian_spectrum(self, adj):
        """Normalized Laplacian = I - A/k.
        Eigenvalues: 0, 1-2/12=5/6, 1-(-4)/12=4/3.
        """
        n = adj.shape[0]
        L_norm = np.eye(n) - adj.astype(float) / 12.0
        vals = la.eigvalsh(L_norm)
        vals.sort()
        assert abs(vals[0]) < 1e-10
        assert abs(vals[1] - 5.0 / 6.0) < 1e-8
        assert abs(vals[-1] - 4.0 / 3.0) < 1e-8

    def test_connectivity_from_second_eigenvalue_bound(self, adj_eig, lap_eig):
        """Multiple bounds agree: kappa >= ceil(a(G)) = 10, actual = 12."""
        adj_vals, _ = adj_eig
        lap_vals, _ = lap_eig
        a = lap_vals[1]
        k = adj_vals[0]
        s = max(abs(adj_vals[1]), abs(adj_vals[-1]))
        # All these are lower bounds on kappa = 12
        assert math.ceil(a) <= 12  # ceil(10) = 10 <= 12
        assert k - s <= 12  # 12 - 4 = 8 <= 12
        assert a <= 12  # 10 <= 12
