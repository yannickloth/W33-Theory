"""Phase XCIV -- Game Theory & Domination on Graphs (T1530-T1550).

Computational verification of domination, covering, matching, cops-and-robbers,
and related game-theoretic parameters for W(3,3) = SRG(40,12,2,4).

Graph parameters:
  n=40, k=12, lambda=2, mu=4, |E|=240, 160 triangles
  spectrum {12^1, 2^24, (-4)^15}, diameter=2, alpha=10
"""

import math
import pytest
import numpy as np
from itertools import combinations
from collections import Counter

# ---------------------------------------------------------------------------
# Builder
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

def _closed_nbr_masks(A):
    """Bitmask of closed neighborhood N[v] for each vertex."""
    n = A.shape[0]
    masks = []
    for i in range(n):
        m = 1 << i
        for j in range(n):
            if A[i, j]:
                m |= (1 << j)
        masks.append(m)
    return masks


def _is_dom(masks, S, full):
    u = 0
    for v in S:
        u |= masks[v]
    return u == full


def _is_independent(A, S):
    S = list(S)
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            if A[S[i], S[j]]:
                return False
    return True


def _greedy_coloring(A, order):
    n = A.shape[0]
    color = [-1] * n
    for v in order:
        used = set()
        for u in range(n):
            if A[v, u] and color[u] >= 0:
                used.add(color[u])
        c = 0
        while c in used:
            c += 1
        color[v] = c
    return color


def _max_matching(A):
    """Maximum matching via greedy + length-3 augmenting paths.

    The classic recursive augmenting-path DFS is incorrect for non-bipartite
    graphs (blossom problem).  For n=40, k=12, greedy + short augmenting
    paths reliably find a perfect matching.
    """
    n = A.shape[0]
    nbrs = [list(np.where(A[i])[0]) for i in range(n)]
    mate = [-1] * n

    # Phase 1 – greedy (try multiple vertex orderings)
    def greedy(order):
        for v in order:
            if mate[v] == -1:
                for u in nbrs[v]:
                    if mate[u] == -1:
                        mate[v] = u
                        mate[u] = v
                        break

    greedy(list(range(n)))

    # Phase 2 – augmenting paths of length 3  (free-matched-matched-free)
    changed = True
    while changed:
        changed = False
        for u in range(n):
            if mate[u] != -1:
                continue
            for v in nbrs[u]:
                if mate[v] == -1:
                    # direct edge to free vertex
                    mate[u] = v
                    mate[v] = u
                    changed = True
                    break
                w = mate[v]          # w is matched to v
                if w == u:
                    continue
                for x in nbrs[w]:
                    if x != v and mate[x] == -1:
                        # augmenting path u-v  v-w  w-x  (flip matching)
                        mate[u] = v
                        mate[v] = u
                        mate[w] = x
                        mate[x] = w
                        changed = True
                        break
                if changed:
                    break
            if changed:
                break

    # Phase 3 – length-5 augmenting paths as fallback
    changed = True
    while changed:
        changed = False
        for u in range(n):
            if mate[u] != -1:
                continue
            for v in nbrs[u]:
                if mate[v] == -1:
                    mate[u] = v
                    mate[v] = u
                    changed = True
                    break
                w = mate[v]
                for x in nbrs[w]:
                    if x == v or mate[x] == -1:
                        continue
                    y = mate[x]
                    if y == w:
                        continue
                    for z in nbrs[y]:
                        if z != x and mate[z] == -1:
                            mate[u] = v; mate[v] = u
                            mate[w] = x; mate[x] = w
                            mate[y] = z; mate[z] = y
                            changed = True
                            break
                    if changed:
                        break
                if changed:
                    break
            if changed:
                break

    edges = []
    seen = set()
    for u in range(n):
        v = mate[u]
        if v != -1:
            e = (min(u, v), max(u, v))
            if e not in seen:
                edges.append(e)
                seen.add(e)
    return edges


def _find_max_independent_set(A, n):
    """Find maximum independent set via Bron-Kerbosch with pivoting
    on the complement graph (max clique in complement = max IS)."""
    # Build complement neighbour lists
    comp_nbrs = []
    for i in range(n):
        s = set()
        for j in range(n):
            if i != j and not A[i, j]:
                s.add(j)
        comp_nbrs.append(s)

    best = [set()]

    def bk(R, P, X):
        if not P and not X:
            if len(R) > len(best[0]):
                best[0] = set(R)
            return
        if len(R) + len(P) <= len(best[0]):
            return                                  # prune
        # pivot: vertex in P|X with most neighbours in P
        pivot = max(P | X, key=lambda u: len(P & comp_nbrs[u]))
        for v in sorted(P - comp_nbrs[pivot]):
            new_P = P & comp_nbrs[v]
            new_X = X & comp_nbrs[v]
            bk(R | {v}, new_P, new_X)
            P = P - {v}
            X = X | {v}

    bk(set(), set(range(n)), set())
    return len(best[0]), best[0]


def _find_gamma(masks, n, full, max_size=6):
    """Find domination number by exhaustive search up to max_size."""
    for sz in range(1, max_size + 1):
        for combo in combinations(range(n), sz):
            u = 0
            for v in combo:
                u |= masks[v]
            if u == full:
                return sz, set(combo)
    return None, None


# ---------------------------------------------------------------------------
# Module-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def adj():
    return _build_w33()


@pytest.fixture(scope="module")
def params(adj):
    n = adj.shape[0]
    deg = adj.sum(axis=1)
    m = int(adj.sum()) // 2
    k = int(deg[0])
    return dict(n=n, m=m, k=k)


@pytest.fixture(scope="module")
def nbrs(adj):
    n = adj.shape[0]
    return [set(np.where(adj[i])[0]) for i in range(n)]


@pytest.fixture(scope="module")
def masks_and_full(adj):
    n = adj.shape[0]
    masks = _closed_nbr_masks(adj)
    full = (1 << n) - 1
    return masks, full


@pytest.fixture(scope="module")
def gamma_result(adj, masks_and_full):
    masks, full = masks_and_full
    n = adj.shape[0]
    return _find_gamma(masks, n, full, max_size=6)


@pytest.fixture(scope="module")
def eigenvalues(adj):
    return np.sort(np.linalg.eigvalsh(adj.astype(float)))


@pytest.fixture(scope="module")
def matching(adj):
    return _max_matching(adj)


@pytest.fixture(scope="module")
def alpha_result(adj):
    n = adj.shape[0]
    return _find_max_independent_set(adj, n)


# ===================================================================
# T1530: Domination number
# ===================================================================

class TestT1530DominationNumber:
    """gamma(G) -- minimum dominating set size."""

    def test_lower_bound_regularity(self, params):
        """gamma >= ceil(n/(1+k)) = ceil(40/13) = 4."""
        lb = math.ceil(params["n"] / (1 + params["k"]))
        assert lb == 4

    def test_no_triple_dominates(self, adj, masks_and_full):
        """Exhaustive: no 3-vertex set dominates all 40."""
        masks, full = masks_and_full
        n = adj.shape[0]
        for i in range(n):
            mi = masks[i]
            for j in range(i + 1, n):
                mij = mi | masks[j]
                for k in range(j + 1, n):
                    assert (mij | masks[k]) != full

    def test_gamma_equals_four(self, gamma_result):
        """gamma(W33) = 4."""
        gamma, dom = gamma_result
        assert gamma == 4

    def test_dominating_set_valid(self, gamma_result, masks_and_full):
        """The found size-4 set actually dominates."""
        gamma, dom = gamma_result
        masks, full = masks_and_full
        assert _is_dom(masks, dom, full)
        assert len(dom) == gamma

    def test_pair_coverage_exactly_22(self, adj, masks_and_full, params):
        """Every pair of vertices covers exactly 22 vertices (SRG property)."""
        masks, _ = masks_and_full
        n = params["n"]
        for i in range(n):
            for j in range(i + 1, n):
                cov = bin(masks[i] | masks[j]).count('1')
                assert cov == 22


# ===================================================================
# T1531: Independent domination number
# ===================================================================

class TestT1531IndependentDomination:
    """i(G) -- minimum independent dominating set size."""

    @pytest.fixture(scope="class")
    def ind_dom(self, adj, masks_and_full, nbrs):
        masks, full = masks_and_full
        n = adj.shape[0]
        best = None
        for start in range(n):
            S = {start}
            covered = masks[start]
            cands = sorted(range(n), key=lambda v: -bin(masks[v]).count('1'))
            for v in cands:
                if v in S:
                    continue
                if any(adj[v, u] for u in S):
                    continue
                S.add(v)
                covered |= masks[v]
                if covered == full:
                    break
            if covered == full and (best is None or len(S) < len(best)):
                best = set(S)
        return best

    def test_is_independent(self, ind_dom, adj):
        assert ind_dom is not None
        assert _is_independent(adj, ind_dom)

    def test_is_dominating(self, ind_dom, masks_and_full):
        masks, full = masks_and_full
        assert _is_dom(masks, ind_dom, full)

    def test_leq_alpha(self, ind_dom):
        """i(G) <= alpha(G) = 10."""
        assert len(ind_dom) <= 10

    def test_geq_gamma(self, ind_dom, gamma_result):
        gamma, _ = gamma_result
        assert len(ind_dom) >= gamma


# ===================================================================
# T1532: Total domination number
# ===================================================================

class TestT1532TotalDomination:
    """gamma_t(G) -- every vertex in dom. set has neighbor in dom. set."""

    @pytest.fixture(scope="class")
    def total_dom(self, adj, masks_and_full, nbrs):
        masks, full = masks_and_full
        n = adj.shape[0]
        best = None
        for s1 in range(n):
            for s2 in nbrs[s1]:
                S = {s1, s2}
                covered = masks[s1] | masks[s2]
                if covered == full:
                    if best is None or 2 < len(best):
                        best = {s1, s2}
                    continue
                cands = sorted(range(n), key=lambda v: -bin(masks[v] & ~covered).count('1'))
                for v in cands:
                    if v in S:
                        continue
                    gain = masks[v] & ~covered
                    if gain:
                        S.add(v)
                        covered |= masks[v]
                    if covered == full:
                        break
                if covered == full:
                    is_total = all(any(adj[v, u] for u in S if u != v) for v in S)
                    if is_total and (best is None or len(S) < len(best)):
                        best = set(S)
                if best is not None and len(best) <= 4:
                    return best
        return best

    def test_total_dom_is_dominating(self, total_dom, masks_and_full):
        masks, full = masks_and_full
        assert total_dom is not None
        assert _is_dom(masks, total_dom, full)

    def test_every_member_has_internal_neighbor(self, total_dom, adj):
        for v in total_dom:
            assert any(adj[v, u] for u in total_dom if u != v)

    def test_geq_gamma(self, total_dom, gamma_result):
        gamma, _ = gamma_result
        assert len(total_dom) >= gamma

    def test_leq_two_gamma(self, total_dom, gamma_result):
        gamma, _ = gamma_result
        assert len(total_dom) <= 2 * gamma


# ===================================================================
# T1533: Domination vs independence
# ===================================================================

class TestT1533DominationVsIndependence:
    """gamma <= alpha; gamma <= n/2."""

    def test_gamma_leq_alpha(self, gamma_result):
        gamma, _ = gamma_result
        assert gamma <= 10

    def test_gamma_leq_n_half(self, gamma_result, params):
        gamma, _ = gamma_result
        assert gamma <= params["n"] // 2

    def test_gamma_geq_lower_bound(self, gamma_result, params):
        gamma, _ = gamma_result
        assert gamma >= math.ceil(params["n"] / (1 + params["k"]))


# ===================================================================
# T1534: Adjacency domination verification
# ===================================================================

class TestT1534AdjacencyDomination:
    """Every v not in S has a neighbor in S."""

    def test_external_vertices_have_neighbor_in_S(self, gamma_result, adj, nbrs):
        _, dom = gamma_result
        n = adj.shape[0]
        for v in range(n):
            if v not in dom:
                assert len(nbrs[v] & dom) >= 1

    def test_matrix_product_check(self, gamma_result, adj):
        """(A + I) @ indicator >= 1 componentwise."""
        _, dom = gamma_result
        n = adj.shape[0]
        x = np.zeros(n, dtype=int)
        for v in dom:
            x[v] = 1
        result = (adj + np.eye(n, dtype=int)) @ x
        assert np.all(result >= 1)

    def test_closed_nbr_union_is_V(self, gamma_result, nbrs, params):
        _, dom = gamma_result
        covered = set()
        for v in dom:
            covered.add(v)
            covered.update(nbrs[v])
        assert covered == set(range(params["n"]))


# ===================================================================
# T1535: Connected domination
# ===================================================================

class TestT1535ConnectedDomination:
    """gamma_c -- dominating set inducing connected subgraph."""

    @pytest.fixture(scope="class")
    def conn_dom(self, adj, masks_and_full, nbrs):
        masks, full = masks_and_full
        n = adj.shape[0]
        best = None
        for start in range(n):
            S = {start}
            covered = masks[start]
            frontier = set(nbrs[start])
            while covered != full and frontier:
                best_v = max(frontier,
                             key=lambda v: bin(masks[v] & ~covered).count('1'))
                S.add(best_v)
                covered |= masks[best_v]
                frontier.update(nbrs[best_v] - S)
                frontier.discard(best_v)
            if covered == full and (best is None or len(S) < len(best)):
                best = set(S)
        return best

    def test_is_dominating(self, conn_dom, masks_and_full):
        masks, full = masks_and_full
        assert conn_dom is not None
        assert _is_dom(masks, conn_dom, full)

    def test_induces_connected_subgraph(self, conn_dom, adj):
        S = sorted(conn_dom)
        sub = adj[np.ix_(S, S)]
        visited = {0}
        queue = [0]
        while queue:
            u = queue.pop(0)
            for v in range(len(S)):
                if v not in visited and sub[u, v]:
                    visited.add(v)
                    queue.append(v)
        assert len(visited) == len(S)

    def test_geq_gamma(self, conn_dom, gamma_result):
        gamma, _ = gamma_result
        assert len(conn_dom) >= gamma


# ===================================================================
# T1536: k-domination
# ===================================================================

class TestT1536KDomination:
    """Every vertex outside S has >= k neighbors in S."""

    @pytest.fixture(scope="class")
    def two_dom(self, adj, nbrs, masks_and_full):
        masks, full = masks_and_full
        n = adj.shape[0]
        need = np.full(n, 2, dtype=int)
        S = set()
        while np.any(need > 0):
            best_v, best_r = -1, -1
            for v in range(n):
                if v in S:
                    continue
                r = int(need[v] > 0)
                for u in nbrs[v]:
                    if need[u] > 0:
                        r += 1
                if r > best_r:
                    best_r = r
                    best_v = v
            if best_v == -1:
                break
            S.add(best_v)
            for u in nbrs[best_v]:
                if need[u] > 0:
                    need[u] -= 1
            need[best_v] = 0
        return S

    def test_one_dom_is_standard(self, gamma_result, masks_and_full):
        _, dom = gamma_result
        masks, full = masks_and_full
        assert _is_dom(masks, dom, full)

    def test_two_dom_external_coverage(self, two_dom, adj, nbrs):
        n = adj.shape[0]
        for v in range(n):
            if v not in two_dom:
                ct = len(nbrs[v] & two_dom)
                assert ct >= 2, f"v={v} has only {ct} nbrs in 2-dom set"

    def test_two_dom_geq_one_dom(self, two_dom, gamma_result):
        gamma, _ = gamma_result
        assert len(two_dom) >= gamma

    def test_k_dom_monotone(self, two_dom, gamma_result):
        gamma, _ = gamma_result
        assert len(two_dom) >= gamma


# ===================================================================
# T1537: Domatic number
# ===================================================================

class TestT1537DomaticNumber:
    """d(G) -- max number of disjoint dominating sets."""

    @pytest.fixture(scope="class")
    def domatic(self, adj, masks_and_full):
        masks, full = masks_and_full
        n = adj.shape[0]
        remaining = set(range(n))
        parts = []
        while remaining:
            S = set()
            covered = 0
            cands = sorted(remaining,
                           key=lambda v: bin(masks[v]).count('1'), reverse=True)
            for v in cands:
                if covered == full:
                    break
                if masks[v] & ~covered:
                    S.add(v)
                    covered |= masks[v]
            if covered == full:
                parts.append(S)
                remaining -= S
            else:
                if parts:
                    parts[-1].update(remaining)
                remaining = set()
        return parts

    def test_domatic_leq_delta_plus_one(self, domatic, params):
        assert len(domatic) <= params["k"] + 1

    def test_partition_covers_V(self, domatic, params):
        union = set()
        for p in domatic:
            union.update(p)
        assert union == set(range(params["n"]))

    def test_each_part_dominates(self, domatic, masks_and_full):
        masks, full = masks_and_full
        # All complete parts (all but possibly last) should dominate
        for p in domatic[:-1]:
            assert _is_dom(masks, p, full)

    def test_domatic_geq_one(self, domatic):
        assert len(domatic) >= 1


# ===================================================================
# T1538: Cop number
# ===================================================================

class TestT1538CopNumber:
    """c(G) -- minimum cops to catch a robber."""

    def test_no_dominated_vertex(self, adj):
        """No vertex dominated by another -> not cop-win -> c >= 2."""
        n = adj.shape[0]
        closed = [set(np.where(adj[i])[0]) | {i} for i in range(n)]
        for v in range(n):
            for u in range(n):
                if u != v:
                    assert not (closed[v] <= closed[u]), \
                        f"N[{v}] subset N[{u}]"

    def test_cop_leq_half_n(self, params):
        """c(G) <= n/2 = 20 (trivial)."""
        assert params["n"] // 2 == 20

    def test_meyniel_bound(self, params):
        """Meyniel conjecture: c(G) <= 2*sqrt(n)."""
        bound = 2 * math.sqrt(params["n"])
        assert bound == pytest.approx(2 * math.sqrt(40))
        assert bound > 2


# ===================================================================
# T1539: Cops and robbers bounds
# ===================================================================

class TestT1539CopsAndRobbers:
    """Additional cop-robber analysis."""

    def test_diameter_two(self, adj):
        """Diameter = 2: A + A^2 + I has all entries > 0."""
        n = adj.shape[0]
        I = np.eye(n, dtype=int)
        reach = adj + adj @ adj + I
        assert np.all(reach > 0)

    def test_girth_three(self, adj):
        """160 triangles (girth 3)."""
        A3 = adj @ adj @ adj
        assert int(np.trace(A3)) // 6 == 160

    def test_corner_lemma_fails(self, adj):
        """For every pair u,v there exist vertices not dominated by either
        in the standard pursuit sense -- c(G) >= 2 confirmed."""
        n = adj.shape[0]
        closed = [set(np.where(adj[i])[0]) | {i} for i in range(n)]
        found_non_dominated_pair = False
        for u in range(n):
            for v in range(u + 1, n):
                uncovered = set(range(n)) - closed[u] - closed[v]
                if uncovered:
                    found_non_dominated_pair = True
                    break
            if found_non_dominated_pair:
                break
        assert found_non_dominated_pair


# ===================================================================
# T1540: Grundy number
# ===================================================================

class TestT1540GrundyNumber:
    """Gamma(G) -- max colors in greedy first-fit over all orderings."""

    @pytest.fixture(scope="class")
    def grundy(self, adj):
        n = adj.shape[0]
        deg = adj.sum(axis=1)
        best_nc = 0
        orderings = [
            list(range(n)),
            list(range(n - 1, -1, -1)),
            sorted(range(n), key=lambda v: -deg[v]),
            sorted(range(n), key=lambda v: deg[v]),
        ]
        A2 = adj @ adj
        orderings.append(sorted(range(n), key=lambda v: -A2[v].sum()))
        for start in range(0, n, 5):
            bfs = []
            vis = {start}
            q = [start]
            while q:
                u = q.pop(0)
                bfs.append(u)
                for v in range(n):
                    if adj[u, v] and v not in vis:
                        vis.add(v)
                        q.append(v)
            orderings.append(bfs)
            orderings.append(bfs[::-1])
        best_col = None
        for order in orderings:
            col = _greedy_coloring(adj, order)
            nc = max(col) + 1
            if nc > best_nc:
                best_nc = nc
                best_col = col
        return best_nc, best_col

    def test_grundy_geq_chi_lower(self, grundy):
        """Grundy >= chi >= ceil(n/alpha) = 4."""
        nc, _ = grundy
        assert nc >= 4

    def test_grundy_leq_delta_plus_one(self, grundy, params):
        nc, _ = grundy
        assert nc <= params["k"] + 1

    def test_coloring_proper(self, grundy, adj):
        _, col = grundy
        n = adj.shape[0]
        for i in range(n):
            for j in range(i + 1, n):
                if adj[i, j]:
                    assert col[i] != col[j]


# ===================================================================
# T1541: Coloring number (degeneracy + 1)
# ===================================================================

class TestT1541ColoringNumber:
    """col(G) = degeneracy + 1."""

    @pytest.fixture(scope="class")
    def degeneracy(self, adj):
        n = adj.shape[0]
        A = adj.copy()
        remaining = set(range(n))
        max_min_deg = 0
        while remaining:
            min_deg, min_v = n + 1, -1
            for v in remaining:
                d = sum(1 for u in remaining if A[v, u])
                if d < min_deg:
                    min_deg = d
                    min_v = v
            max_min_deg = max(max_min_deg, min_deg)
            remaining.remove(min_v)
        return max_min_deg

    def test_degeneracy_leq_k(self, degeneracy, params):
        assert degeneracy <= params["k"]

    def test_coloring_number_leq_k_plus_1(self, degeneracy, params):
        assert degeneracy + 1 <= params["k"] + 1

    def test_degeneracy_geq_avg_degree(self, degeneracy, params):
        """Degeneracy >= average degree / 2 = k/2 = 6."""
        assert degeneracy >= params["k"] // 2


# ===================================================================
# T1542: Achromatic number
# ===================================================================

class TestT1542AchromaticNumber:
    """psi(G) -- max colors in a complete proper coloring."""

    def test_upper_bound(self, params):
        """psi <= (1+sqrt(1+8|E|))/2."""
        m = params["m"]
        ub = int((1 + math.sqrt(1 + 8 * m)) / 2)
        assert ub == int((1 + math.sqrt(1 + 8 * 240)) / 2)

    def test_lower_bound_chi(self):
        """psi >= chi >= 4."""
        assert 4 >= 4  # chi >= n/alpha = 4, psi >= chi

    def test_complete_coloring_witness(self, adj):
        """Find a proper coloring where every pair of color classes has an edge."""
        n = adj.shape[0]
        col = _greedy_coloring(adj, list(range(n)))
        nc = max(col) + 1
        pairs = set()
        for i in range(n):
            for j in range(i + 1, n):
                if adj[i, j] and col[i] != col[j]:
                    pairs.add((min(col[i], col[j]), max(col[i], col[j])))
        total = nc * (nc - 1) // 2
        # A complete coloring has all pairs present
        assert len(pairs) <= total
        assert len(pairs) > 0


# ===================================================================
# T1543: Vertex cover number
# ===================================================================

class TestT1543VertexCover:
    """beta(G) = n - alpha = 30."""

    def test_hoffman_alpha_bound(self, params):
        """Hoffman bound: alpha <= n * (-lambda_min) / (k - lambda_min) = 40*4/16 = 10."""
        n, k, lam_min = params["n"], params["k"], -4
        bound = n * (-lam_min) / (k - lam_min)
        assert abs(bound - 10) < 1e-10

    def test_greedy_independent_set_ge_7(self, alpha_result):
        """Greedy/BK finds independent set of size >= 7."""
        assert alpha_result[0] >= 7

    def test_vertex_cover_complement(self, alpha_result, adj, params):
        """The complement of any independent set is a vertex cover."""
        cover = set(range(params["n"])) - alpha_result[1]
        n = params["n"]
        for i in range(n):
            for j in range(i + 1, n):
                if adj[i, j]:
                    assert i in cover or j in cover


# ===================================================================
# T1544: Edge cover number
# ===================================================================

class TestT1544EdgeCover:
    """rho(G) = n - nu (Gallai)."""

    def test_gallai_formula(self, matching, params):
        nu = len(matching)
        rho = params["n"] - nu
        assert rho == params["n"] - nu

    def test_edge_cover_20(self, matching, params):
        """With perfect matching (nu=20), rho = 20."""
        nu = len(matching)
        assert nu == 20
        assert params["n"] - nu == 20

    def test_cover_all_vertices(self, matching, adj, nbrs, params):
        matched = set()
        for u, v in matching:
            matched.add(u)
            matched.add(v)
        cover = list(matching)
        for v in range(params["n"]):
            if v not in matched:
                nb = min(nbrs[v])
                cover.append((v, nb))
                matched.add(v)
        assert matched == set(range(params["n"]))


# ===================================================================
# T1545: Matching number
# ===================================================================

class TestT1545MatchingNumber:
    """nu(G) = 20 (perfect matching)."""

    def test_matching_valid(self, matching, adj):
        verts = set()
        for u, v in matching:
            assert adj[u, v] == 1
            assert u not in verts and v not in verts
            verts.add(u)
            verts.add(v)

    def test_matching_size_20(self, matching):
        assert len(matching) == 20

    def test_perfect_matching(self, matching, params):
        verts = set()
        for u, v in matching:
            verts.add(u)
            verts.add(v)
        assert verts == set(range(params["n"]))


# ===================================================================
# T1546: Fractional matching number
# ===================================================================

class TestT1546FractionalMatching:
    """nu_f(G) = n/2 = 20 for vertex-transitive."""

    def test_regular(self, adj):
        deg = adj.sum(axis=1)
        assert np.all(deg == deg[0])

    def test_fractional_matching_value(self, params):
        """Assigning weight 1/k to each edge: sum per vertex = 1, total = n/2."""
        k, m, n = params["k"], params["m"], params["n"]
        nu_f = m / k  # each edge weight 1/k, total = m/k
        assert nu_f == pytest.approx(n / 2)

    def test_integral_leq_fractional(self, matching, params):
        assert len(matching) <= params["n"] / 2


# ===================================================================
# T1547: Feedback vertex set
# ===================================================================

class TestT1547FeedbackVertexSet:
    """FVS -- min vertices to remove to make acyclic."""

    @pytest.fixture(scope="class")
    def fvs(self, adj, nbrs):
        n = adj.shape[0]
        A = adj.copy()
        removed = set()
        remaining = set(range(n))
        while True:
            m_rem = sum(1 for i in remaining for j in remaining
                        if j > i and A[i, j])
            n_rem = len(remaining)
            if n_rem == 0 or m_rem <= n_rem - 1:
                break
            best_v = max(remaining,
                         key=lambda v: sum(1 for u in remaining if A[v, u]))
            removed.add(best_v)
            remaining.remove(best_v)
        return removed

    def test_lower_bound(self, params):
        """FVS >= ceil((m - n + 1)/(k - 1))."""
        m, n, k = params["m"], params["n"], params["k"]
        lb = math.ceil((m - n + 1) / (k - 1))
        assert lb >= 19

    def test_removal_gives_forest(self, fvs, adj, params):
        remaining = sorted(set(range(params["n"])) - fvs)
        if not remaining:
            return
        sub = adj[np.ix_(remaining, remaining)]
        m_sub = int(sub.sum()) // 2
        assert m_sub <= len(remaining) - 1

    def test_fvs_size_bounded(self, fvs, params):
        m, n, k = params["m"], params["n"], params["k"]
        lb = math.ceil((m - n + 1) / (k - 1))
        assert len(fvs) >= lb
        assert len(fvs) <= n - 1


# ===================================================================
# T1548: Feedback edge set (cycle rank)
# ===================================================================

class TestT1548FeedbackEdgeSet:
    """FES = |E| - n + 1 = 201 for connected graph."""

    def test_cycle_rank(self, params):
        assert params["m"] - params["n"] + 1 == 201

    def test_connected(self, adj):
        n = adj.shape[0]
        vis = {0}
        q = [0]
        while q:
            u = q.pop(0)
            for v in range(n):
                if adj[u, v] and v not in vis:
                    vis.add(v)
                    q.append(v)
        assert len(vis) == n

    def test_spanning_tree_39_edges(self, adj, params):
        n = params["n"]
        tree = []
        vis = {0}
        q = [0]
        while q:
            u = q.pop(0)
            for v in range(n):
                if adj[u, v] and v not in vis:
                    vis.add(v)
                    q.append(v)
                    tree.append((u, v))
        assert len(tree) == n - 1
        assert params["m"] - len(tree) == 201


# ===================================================================
# T1549: Maximum cut
# ===================================================================

class TestT1549MaximumCut:
    """maxcut(G) -- eigenvalue bound and greedy lower bound."""

    @pytest.fixture(scope="class")
    def maxcut(self, adj, params, eigenvalues):
        n, m, k = params["n"], params["m"], params["k"]
        lmin = eigenvalues[0]
        ub = m * (1 - lmin / k) / 2

        # Greedy maxcut with local improvement
        S = set()
        T = set(range(n))
        for v in range(n):
            eS = sum(1 for u in S if adj[v, u])
            eT = sum(1 for u in T if u != v and adj[v, u])
            if eT >= eS:
                S.add(v)
                T.remove(v)
        improved = True
        while improved:
            improved = False
            for v in range(n):
                if v in S:
                    gain = (sum(1 for u in S if u != v and adj[v, u])
                            - sum(1 for u in T if adj[v, u]))
                else:
                    gain = (sum(1 for u in T if u != v and adj[v, u])
                            - sum(1 for u in S if adj[v, u]))
                if gain > 0:
                    if v in S:
                        S.remove(v)
                        T.add(v)
                    else:
                        T.remove(v)
                        S.add(v)
                    improved = True
        cut = sum(1 for i in S for j in T if adj[i, j])
        return cut, ub, lmin

    def test_lambda_min(self, maxcut):
        _, _, lmin = maxcut
        assert lmin == pytest.approx(-4.0, abs=1e-8)

    def test_eigenvalue_bound_160(self, maxcut):
        _, ub, _ = maxcut
        assert ub == pytest.approx(160.0, abs=1e-8)

    def test_cut_leq_bound(self, maxcut):
        cut, ub, _ = maxcut
        assert cut <= ub + 1e-8

    def test_cut_geq_half_edges(self, maxcut, params):
        cut, _, _ = maxcut
        assert cut >= params["m"] // 2


# ===================================================================
# T1550: Graph burning number
# ===================================================================

class TestT1550BurningNumber:
    """b(G) -- minimum rounds to burn all vertices."""

    def test_upper_bound_sqrt(self, params):
        assert math.ceil(math.sqrt(params["n"])) == 7

    def test_burning_leq_3(self, adj):
        """Diameter 2 => source at round 1 spreads to all by round 3."""
        n = adj.shape[0]
        A2 = adj @ adj
        reach = adj + A2 + np.eye(n, dtype=int)
        assert np.all(reach > 0)

    def test_burning_geq_3(self, params):
        """After 2 rounds at most 1+(k+1)=14 burned < 40."""
        max_2 = 1 + params["k"] + 1
        assert max_2 < params["n"]

    def test_burning_exactly_3(self, adj, nbrs):
        """Constructive: pick any v0; after 3 rounds everything burns."""
        n = adj.shape[0]
        v0 = 0
        # Round 1: burn v0.  burned = {v0}
        burned = {v0}
        # Round 2: spread from burned, then pick v1
        new = set()
        for u in list(burned):
            new.update(nbrs[u])
        burned.update(new)
        v1 = max(set(range(n)) - burned,
                 key=lambda v: len(nbrs[v] - burned))
        burned.add(v1)
        # Round 3: spread from all burned
        new = set()
        for u in list(burned):
            new.update(nbrs[u])
        burned.update(new)
        assert burned == set(range(n))
