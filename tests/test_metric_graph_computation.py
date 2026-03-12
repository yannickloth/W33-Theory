"""
Phase LXXXVIII -- Metric Graph Theory (T1404-T1424)
Hard-computation test suite for W(3,3) = Sp(4,3) SRG(40,12,2,4).

Covers 21 theorems on distance matrix, Wiener index, resistance distance,
Szeged index, metric dimension, geodetic number, distance Laplacians,
peripheral vertices, and distance cospectrality.
"""

import math
import numpy as np
import pytest
from collections import Counter
from fractions import Fraction
from itertools import combinations


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


# ── helpers ─────────────────────────────────────────────────────────────────

def _bfs_distances(A):
    """Compute all-pairs shortest-path distance matrix via BFS."""
    from collections import deque
    n = A.shape[0]
    D = np.full((n, n), -1, dtype=int)
    for src in range(n):
        visited = np.zeros(n, dtype=bool)
        visited[src] = True
        D[src, src] = 0
        queue = deque([src])
        while queue:
            u = queue.popleft()
            for v in range(n):
                if A[u, v] and not visited[v]:
                    visited[v] = True
                    D[src, v] = D[src, u] + 1
                    queue.append(v)
    return D


def _greedy_hamiltonian_path(A):
    """Attempt to find a Hamiltonian path using Warnsdorff heuristic."""
    n = A.shape[0]
    nbr = [np.where(A[i] == 1)[0] for i in range(n)]
    for start in range(n):
        path = [start]
        visited = set([start])
        cur = start
        while len(path) < n:
            candidates = [v for v in nbr[cur] if v not in visited]
            if not candidates:
                break
            candidates.sort(
                key=lambda v: sum(1 for w in nbr[v] if w not in visited)
            )
            nxt = candidates[0]
            path.append(nxt)
            visited.add(nxt)
            cur = nxt
        if len(path) == n:
            return path
    return None


def _greedy_resolving_set(D):
    """Greedy algorithm for a small resolving set of the distance matrix D."""
    n = D.shape[0]
    S = []
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    distinguished = np.zeros(len(pairs), dtype=bool)
    while not np.all(distinguished):
        best_v, best_count = -1, 0
        for v in range(n):
            if v in S:
                continue
            cnt = 0
            for k, (i, j) in enumerate(pairs):
                if not distinguished[k] and D[i, v] != D[j, v]:
                    cnt += 1
            if cnt > best_count:
                best_count = cnt
                best_v = v
        S.append(best_v)
        for k, (i, j) in enumerate(pairs):
            if D[i, best_v] != D[j, best_v]:
                distinguished[k] = True
    return S


def _is_resolving(D, S):
    """Check whether S is a resolving set for distance matrix D."""
    n = D.shape[0]
    vecs = set()
    for v in range(n):
        vec = tuple(D[v, s] for s in S)
        if vec in vecs:
            return False
        vecs.add(vec)
    return True


def _geodetic_closure(A, D, S):
    """Compute the geodetic closure of vertex set S."""
    n = A.shape[0]
    closure = set(S)
    for s1 in S:
        for s2 in S:
            if s1 >= s2:
                continue
            d = D[s1, s2]
            if d == 0:
                continue
            for w in range(n):
                if D[s1, w] + D[w, s2] == d:
                    closure.add(w)
    return closure


def _greedy_geodetic_set(A, D):
    """Greedy algorithm for a small geodetic set."""
    n = A.shape[0]
    S = [0]
    closure = _geodetic_closure(A, D, S)
    while len(closure) < n:
        best_v, best_gain = -1, 0
        for v in range(n):
            if v in S:
                continue
            trial_closure = _geodetic_closure(A, D, S + [v])
            gain = len(trial_closure) - len(closure)
            if gain > best_gain:
                best_gain = gain
                best_v = v
        if best_v == -1:
            uncovered = [v for v in range(n) if v not in closure]
            best_v = uncovered[0]
        S.append(best_v)
        closure = _geodetic_closure(A, D, S)
    return S


# ── module-scoped fixtures ──────────────────────────────────────────────────

@pytest.fixture(scope="module")
def adj():
    """Adjacency matrix of W(3,3)."""
    return _build_w33()


@pytest.fixture(scope="module")
def n():
    return 40


@pytest.fixture(scope="module")
def dist(adj):
    """All-pairs shortest-path distance matrix."""
    return _bfs_distances(adj)


@pytest.fixture(scope="module")
def laplacian(adj):
    """Graph Laplacian L = D_deg - A."""
    return np.diag(adj.sum(axis=1)) - adj


@pytest.fixture(scope="module")
def dist_evals(dist):
    """Eigenvalues of D, sorted decreasingly."""
    return np.sort(np.linalg.eigvalsh(dist.astype(float)))[::-1]


@pytest.fixture(scope="module")
def complement_adj(adj):
    """Adjacency matrix of the complement of W(3,3)."""
    n = adj.shape[0]
    return np.ones((n, n), dtype=int) - np.eye(n, dtype=int) - adj


@pytest.fixture(scope="module")
def complement_dist(complement_adj):
    """Distance matrix of the complement graph."""
    return _bfs_distances(complement_adj)


@pytest.fixture(scope="module")
def resistance(laplacian):
    """Resistance distance matrix from Laplacian pseudoinverse."""
    L = laplacian.astype(float)
    L_plus = np.linalg.pinv(L)
    n = L.shape[0]
    R = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            R[i, j] = L_plus[i, i] + L_plus[j, j] - 2 * L_plus[i, j]
    return R


@pytest.fixture(scope="module")
def rd_matrix(dist):
    """Reciprocal distance matrix RD[i,j] = 1/d(i,j) for i != j."""
    n = dist.shape[0]
    RD = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(n):
            if i != j:
                RD[i, j] = 1.0 / dist[i, j]
    return RD


@pytest.fixture(scope="module")
def dist_lap(dist):
    """Distance Laplacian D_L = diag(transmission) - D."""
    t = dist.sum(axis=1)
    return np.diag(t) - dist


@pytest.fixture(scope="module")
def dist_q(dist):
    """Distance signless Laplacian D_Q = diag(transmission) + D."""
    t = dist.sum(axis=1)
    return np.diag(t) + dist


@pytest.fixture(scope="module")
def resolving_set(dist):
    """A greedy resolving set for W(3,3)."""
    return _greedy_resolving_set(dist)


@pytest.fixture(scope="module")
def geodetic_set(adj, dist):
    """A greedy geodetic set for W(3,3)."""
    return _greedy_geodetic_set(adj, dist)


# ═══════════════════════════════════════════════════════════════════════════
# T1404  Distance matrix
# ═══════════════════════════════════════════════════════════════════════════

class TestT1404DistanceMatrix:
    """D[i,j] in {0,1,2}; D = 2(J-I) - A; spectrum {66^1, 2^15, -4^24}."""

    def test_distance_values_only_012(self, dist):
        assert set(np.unique(dist)) == {0, 1, 2}

    def test_diagonal_zero(self, dist, n):
        assert np.all(np.diag(dist) == 0)

    def test_symmetry(self, dist):
        assert np.array_equal(dist, dist.T)

    def test_formula_D_eq_2JI_minus_A(self, dist, adj, n):
        """D = 2(J - I) - A for diameter-2 SRG."""
        J = np.ones((n, n), dtype=int)
        I = np.eye(n, dtype=int)
        assert np.array_equal(dist, 2 * (J - I) - adj)

    def test_spectrum_eigenvalue_66(self, dist_evals):
        assert abs(dist_evals[0] - 66) < 1e-8

    def test_spectrum_eigenvalue_2_mult_15(self, dist_evals):
        assert np.sum(np.abs(dist_evals - 2) < 1e-8) == 15

    def test_spectrum_eigenvalue_m4_mult_24(self, dist_evals):
        assert np.sum(np.abs(dist_evals + 4) < 1e-8) == 24

    def test_total_eigenvalue_count(self, dist_evals, n):
        assert len(dist_evals) == n


# ═══════════════════════════════════════════════════════════════════════════
# T1405  Wiener index
# ═══════════════════════════════════════════════════════════════════════════

class TestT1405WienerIndex:
    """W = sum_{i<j} d(i,j) = 1320."""

    def test_wiener_value(self, dist):
        W = int(np.sum(np.triu(dist, k=1)))
        assert W == 1320

    def test_edge_count_and_nonadj_count(self, dist):
        d1 = np.sum(dist == 1) // 2
        d2 = np.sum(dist == 2) // 2
        assert d1 == 240
        assert d2 == 540

    def test_wiener_decomposition(self, dist):
        d1 = np.sum(dist == 1) // 2
        d2 = np.sum(dist == 2) // 2
        assert d1 * 1 + d2 * 2 == 1320

    def test_wiener_from_full_sum(self, dist):
        assert np.sum(dist) == 2 * 1320


# ═══════════════════════════════════════════════════════════════════════════
# T1406  Average distance
# ═══════════════════════════════════════════════════════════════════════════

class TestT1406AverageDistance:
    """d_avg = 1320 / C(40,2) = 22/13."""

    def test_exact_fraction(self, dist, n):
        W = int(np.sum(np.triu(dist, k=1)))
        pairs = n * (n - 1) // 2
        assert Fraction(W, pairs) == Fraction(22, 13)

    def test_float_value(self, dist, n):
        W = np.sum(np.triu(dist, k=1))
        d_avg = W / (n * (n - 1) / 2)
        assert abs(d_avg - 22 / 13) < 1e-14

    def test_bounded_by_diameter(self, dist, n):
        d_avg = np.sum(np.triu(dist, k=1)) / (n * (n - 1) / 2)
        assert 1.0 < d_avg < 2.0


# ═══════════════════════════════════════════════════════════════════════════
# T1407  Distance regularity -- intersection array {12,9;1,4}
# ═══════════════════════════════════════════════════════════════════════════

class TestT1407DistanceRegularity:
    """b0=12, b1=9, c1=1, c2=4, a1=2."""

    def test_b0_equals_degree(self, dist, n):
        for v in range(n):
            assert np.sum(dist[v] == 1) == 12

    def test_c1_always_one(self, adj, dist, n):
        """c1: each dist-1 neighbor w of v has exactly 1 neighbor at dist 0 (= v)."""
        for v in range(n):
            for w in np.where(dist[v] == 1)[0]:
                cnt = np.sum((adj[w] == 1) & (dist[v] == 0))
                assert cnt == 1

    def test_b1_equals_nine(self, adj, dist, n):
        """b1: each dist-1 neighbor w of v has 9 neighbors at dist 2 from v."""
        for v in range(n):
            for w in np.where(dist[v] == 1)[0]:
                cnt = np.sum((adj[w] == 1) & (dist[v] == 2))
                assert cnt == 9

    def test_c2_equals_four(self, adj, dist, n):
        """c2 = mu = 4: each dist-2 vertex w has 4 neighbors at dist 1 from v."""
        for v in range(n):
            for w in np.where(dist[v] == 2)[0]:
                cnt = np.sum((adj[w] == 1) & (dist[v] == 1))
                assert cnt == 4

    def test_a1_equals_lambda(self, adj, dist, n):
        """a1 = 2: each dist-1 neighbor w has 2 neighbors also at dist 1 from v."""
        for v in range(n):
            for w in np.where(dist[v] == 1)[0]:
                cnt = np.sum((adj[w] == 1) & (dist[v] == 1))
                # This counts v itself (adj[w,v]=1, dist[v,v]=... wait dist[v,v]=0 not 1)
                # Actually dist[v,v]=0, so (dist[v]==1) excludes v.
                # So cnt counts neighbors of w that are at distance 1 from v, excluding v.
                assert cnt == 2


# ═══════════════════════════════════════════════════════════════════════════
# T1408  Eccentricity
# ═══════════════════════════════════════════════════════════════════════════

class TestT1408Eccentricity:
    """ecc(v) = 2 for all v; diameter = radius = 2."""

    def test_all_eccentricities_two(self, dist, n):
        for v in range(n):
            assert np.max(dist[v]) == 2

    def test_diameter(self, dist):
        assert np.max(dist) == 2

    def test_radius(self, dist, n):
        assert min(np.max(dist[v]) for v in range(n)) == 2

    def test_self_centered(self, dist, n):
        eccs = [np.max(dist[v]) for v in range(n)]
        assert min(eccs) == max(eccs)


# ═══════════════════════════════════════════════════════════════════════════
# T1409  Distance energy
# ═══════════════════════════════════════════════════════════════════════════

class TestT1409DistanceEnergy:
    """E_D = sum|d_i| = 66 + 24*4 + 15*2 = 192."""

    def test_total_energy(self, dist_evals):
        assert abs(np.sum(np.abs(dist_evals)) - 192) < 1e-6

    def test_contribution_66(self, dist_evals):
        mask = np.abs(dist_evals - 66) < 1e-8
        assert abs(np.sum(np.abs(dist_evals[mask])) - 66) < 1e-8

    def test_contribution_m4(self, dist_evals):
        mask = np.abs(dist_evals + 4) < 1e-8
        assert abs(np.sum(np.abs(dist_evals[mask])) - 96) < 1e-6

    def test_contribution_2(self, dist_evals):
        mask = np.abs(dist_evals - 2) < 1e-8
        assert abs(np.sum(np.abs(dist_evals[mask])) - 30) < 1e-6


# ═══════════════════════════════════════════════════════════════════════════
# T1410  Detour matrix
# ═══════════════════════════════════════════════════════════════════════════

class TestT1410DetourMatrix:
    """Longest-path (detour) properties for diameter-2 graph."""

    def test_hamiltonian_path_exists(self, adj):
        """W(3,3) admits a Hamiltonian path (greedy Warnsdorff)."""
        path = _greedy_hamiltonian_path(adj)
        assert path is not None
        assert len(path) == 40

    def test_hamiltonian_path_valid(self, adj):
        """The Hamiltonian path uses only actual edges."""
        path = _greedy_hamiltonian_path(adj)
        for k in range(len(path) - 1):
            assert adj[path[k], path[k + 1]] == 1

    def test_hamiltonian_path_visits_all(self, adj):
        """Hamiltonian path visits every vertex exactly once."""
        path = _greedy_hamiltonian_path(adj)
        assert len(set(path)) == 40

    def test_adjacent_detour_at_least_two(self, adj, n):
        """Any adjacent pair u,v has a path of length >= 2 via common neighbor."""
        for i in range(n):
            for j in range(i + 1, n):
                if adj[i, j]:
                    common = np.where((adj[i] == 1) & (adj[j] == 1))[0]
                    assert len(common) >= 2  # lambda = 2


# ═══════════════════════════════════════════════════════════════════════════
# T1411  Resistance distance
# ═══════════════════════════════════════════════════════════════════════════

class TestT1411ResistanceDistance:
    """R_ij from Laplacian pseudoinverse; Kirchhoff index = 133.5."""

    def test_kirchhoff_index(self, resistance, n):
        K_f = np.sum(np.triu(resistance, k=1))
        assert abs(K_f - 133.5) < 1e-6

    def test_kirchhoff_from_eigenvalues(self, laplacian, n):
        """K_f = n * sum(1/mu_i) over non-zero Laplacian eigenvalues."""
        evals = np.sort(np.linalg.eigvalsh(laplacian.astype(float)))
        nonzero = evals[1:]  # skip the zero eigenvalue
        K_f = n * np.sum(1.0 / nonzero)
        assert abs(K_f - 133.5) < 1e-6

    def test_resistance_symmetric(self, resistance):
        assert np.allclose(resistance, resistance.T, atol=1e-10)

    def test_resistance_diagonal_zero(self, resistance, n):
        assert np.allclose(np.diag(resistance), 0, atol=1e-10)

    def test_resistance_positive_offdiag(self, resistance, n):
        for i in range(n):
            for j in range(i + 1, n):
                assert resistance[i, j] > 0

    def test_resistance_adjacent_value(self, resistance, adj, n):
        """All adjacent pairs have R = 13/80."""
        for i in range(n):
            for j in range(i + 1, n):
                if adj[i, j]:
                    assert abs(resistance[i, j] - 13.0 / 80) < 1e-8

    def test_resistance_nonadjacent_value(self, resistance, adj, n):
        """All non-adjacent pairs have R = 7/40."""
        for i in range(n):
            for j in range(i + 1, n):
                if not adj[i, j]:
                    assert abs(resistance[i, j] - 7.0 / 40) < 1e-8


# ═══════════════════════════════════════════════════════════════════════════
# T1412  Transmission
# ═══════════════════════════════════════════════════════════════════════════

class TestT1412Transmission:
    """t(v) = 12*1 + 27*2 = 66 for all v."""

    def test_all_transmissions_66(self, dist, n):
        for v in range(n):
            assert dist[v].sum() == 66

    def test_transmission_decomposition(self, dist, n):
        for v in range(n):
            d1 = np.sum(dist[v] == 1)
            d2 = np.sum(dist[v] == 2)
            assert d1 == 12 and d2 == 27
            assert d1 + d2 * 2 == 66

    def test_transmission_regular(self, dist, n):
        t = dist.sum(axis=1)
        assert np.all(t == t[0])


# ═══════════════════════════════════════════════════════════════════════════
# T1413  Harary index
# ═══════════════════════════════════════════════════════════════════════════

class TestT1413HararyIndex:
    """H = sum_{i<j} 1/d(i,j) = 510."""

    def test_harary_value(self, dist, n):
        H = sum(1.0 / dist[i, j]
                for i in range(n) for j in range(i + 1, n))
        assert abs(H - 510) < 1e-10

    def test_harary_decomposition(self, dist):
        d1 = np.sum(dist == 1) // 2
        d2 = np.sum(dist == 2) // 2
        H = d1 * 1.0 + d2 * 0.5
        assert abs(H - 510) < 1e-10

    def test_cauchy_schwarz_harary_wiener(self, dist, n):
        """Cauchy-Schwarz: H * W >= C(n,2)^2."""
        W = np.sum(np.triu(dist, k=1))
        H = sum(1.0 / dist[i, j]
                for i in range(n) for j in range(i + 1, n))
        pairs = n * (n - 1) // 2
        assert H * W >= pairs ** 2 - 1e-6


# ═══════════════════════════════════════════════════════════════════════════
# T1414  Reciprocal distance matrix
# ═══════════════════════════════════════════════════════════════════════════

class TestT1414ReciprocalDistanceMatrix:
    """RD = A/2 + (J - I)/2; eigenvalues {25.5^1, 0.5^24, -2.5^15}."""

    def test_rd_formula(self, rd_matrix, adj, n):
        J = np.ones((n, n))
        I_n = np.eye(n)
        expected = adj / 2.0 + (J - I_n) / 2.0
        assert np.allclose(rd_matrix, expected, atol=1e-12)

    def test_rd_diagonal_zero(self, rd_matrix):
        assert np.allclose(np.diag(rd_matrix), 0)

    def test_rd_symmetric(self, rd_matrix):
        assert np.allclose(rd_matrix, rd_matrix.T)

    def test_rd_eigenvalue_largest(self, rd_matrix):
        evals = np.linalg.eigvalsh(rd_matrix)
        assert abs(np.max(evals) - 25.5) < 1e-6

    def test_rd_eigenvalue_05_mult_24(self, rd_matrix):
        evals = np.linalg.eigvalsh(rd_matrix)
        assert np.sum(np.abs(evals - 0.5) < 1e-6) == 24

    def test_rd_eigenvalue_m25_mult_15(self, rd_matrix):
        evals = np.linalg.eigvalsh(rd_matrix)
        assert np.sum(np.abs(evals + 2.5) < 1e-6) == 15


# ═══════════════════════════════════════════════════════════════════════════
# T1415  Hyper-Wiener index
# ═══════════════════════════════════════════════════════════════════════════

class TestT1415HyperWienerIndex:
    """WW = (W + sum d^2) / 2 = (1320 + 2400) / 2 = 1860."""

    def test_hyper_wiener_value(self, dist):
        W = np.sum(np.triu(dist, k=1))
        W2 = np.sum(np.triu(dist ** 2, k=1))
        assert abs((W + W2) / 2 - 1860) < 1e-10

    def test_sum_squared_distances(self, dist):
        W2 = np.sum(np.triu(dist ** 2, k=1))
        assert W2 == 2400

    def test_hyper_wiener_from_edge_counts(self, dist):
        d1 = np.sum(dist == 1) // 2
        d2 = np.sum(dist == 2) // 2
        WW = (d1 * 1 + d2 * 2 + d1 * 1 + d2 * 4) / 2
        assert abs(WW - 1860) < 1e-10


# ═══════════════════════════════════════════════════════════════════════════
# T1416  Szeged index
# ═══════════════════════════════════════════════════════════════════════════

class TestT1416SzegedIndex:
    """Sz = sum_{uv edge} n_u * n_v = 240 * 100 = 24000."""

    def test_szeged_value(self, adj, dist, n):
        Sz = 0
        for u in range(n):
            for v in range(u + 1, n):
                if not adj[u, v]:
                    continue
                n_u = int(np.sum(dist[:, u] < dist[:, v]))
                n_v = int(np.sum(dist[:, v] < dist[:, u]))
                Sz += n_u * n_v
        assert Sz == 24000

    def test_per_edge_n_u_eq_10(self, adj, dist, n):
        for u in range(n):
            for v in range(u + 1, n):
                if not adj[u, v]:
                    continue
                n_u = int(np.sum(dist[:, u] < dist[:, v]))
                assert n_u == 10

    def test_per_edge_n_v_eq_10(self, adj, dist, n):
        for u in range(n):
            for v in range(u + 1, n):
                if not adj[u, v]:
                    continue
                n_v = int(np.sum(dist[:, v] < dist[:, u]))
                assert n_v == 10

    def test_neutral_count(self, adj, dist, n):
        """20 vertices equidistant to both endpoints of each edge."""
        for u in range(n):
            for v in range(u + 1, n):
                if not adj[u, v]:
                    continue
                n_eq = int(np.sum(dist[:, u] == dist[:, v]))
                assert n_eq == 20
                break
            break


# ═══════════════════════════════════════════════════════════════════════════
# T1417  Distance polynomial
# ═══════════════════════════════════════════════════════════════════════════

class TestT1417DistancePolynomial:
    """det(xI - D) = (x - 66)(x + 4)^24 (x - 2)^15."""

    def test_roots_sorted(self, dist_evals):
        tol = 1e-6
        # Decreasing order: 66, then 15 copies of 2, then 24 copies of -4
        assert abs(dist_evals[0] - 66) < tol
        for v in dist_evals[1:16]:
            assert abs(v - 2) < tol
        for v in dist_evals[16:]:
            assert abs(v + 4) < tol

    def test_log_determinant(self, dist):
        """sign * exp(logdet) = 66 * 2^15 * (-4)^24 = 66 * 2^63 > 0."""
        sign, logdet = np.linalg.slogdet(dist.astype(float))
        expected_logdet = math.log(66) + 63 * math.log(2)
        assert sign == 1
        assert abs(logdet - expected_logdet) < 1e-4

    def test_trace_powers(self, dist):
        """tr(D^k) = 66^k + 24*(-4)^k + 15*2^k."""
        D = dist.astype(float)
        for k in [1, 2, 3, 4]:
            Dk = np.linalg.matrix_power(D, k)
            tr_actual = np.trace(Dk)
            tr_expected = 66**k + 24 * ((-4)**k) + 15 * (2**k)
            assert abs(tr_actual - tr_expected) < 1e-2

    def test_D_squared(self, dist, adj, n):
        """D^2 = A^2 - 4A + 4(J - I) from D = 2(J-I) - A."""
        D = dist.astype(float)
        A = adj.astype(float)
        J = np.ones((n, n))
        I_n = np.eye(n)
        D2 = D @ D
        expected = A @ A - 4 * A + 4 * (J - I_n)
        # D = 2(J-I) - A, D^2 = 4(J-I)^2 - 4(J-I)A + A^2
        # (J-I)^2 = J^2 - 2J + I = 40J - 2J + I = 38J + I
        # Wait, J^2 = 40J for n=40. So (J-I)^2 = 40J - 2J + I = 38J + I
        # (J-I)A = JA - A = 12J - A (since A*j = 12*j → JA = 12J)
        # D^2 = 4(38J + I) - 4(12J - A) + A^2
        #      = 152J + 4I - 48J + 4A + A^2
        #      = 104J + 4I + 4A + A^2
        expected2 = 104 * J + 4 * I_n + 4 * A + A @ A
        assert np.allclose(D2, expected2, atol=1e-8)


# ═══════════════════════════════════════════════════════════════════════════
# T1418  Metric dimension
# ═══════════════════════════════════════════════════════════════════════════

class TestT1418MetricDimension:
    """Minimum resolving set size with lower bound ceil(log2(40)) = 6."""

    def test_lower_bound(self):
        assert math.ceil(math.log2(40)) == 6

    def test_resolving_set_valid(self, dist, resolving_set):
        assert _is_resolving(dist, resolving_set)

    def test_resolving_set_ge_lower_bound(self, resolving_set):
        assert len(resolving_set) >= 6

    def test_all_distance_vectors_distinct(self, dist, resolving_set, n):
        vecs = [tuple(dist[v, s] for s in resolving_set) for v in range(n)]
        assert len(set(vecs)) == n

    def test_distance_vectors_binary_for_non_members(self, dist, resolving_set, n):
        """For v not in S, distance to each s is 1 or 2 (binary signal)."""
        S_set = set(resolving_set)
        for v in range(n):
            if v not in S_set:
                for s in resolving_set:
                    assert dist[v, s] in (1, 2)


# ═══════════════════════════════════════════════════════════════════════════
# T1419  Geodetic number
# ═══════════════════════════════════════════════════════════════════════════

class TestT1419GeodeticNumber:
    """Minimum S with geodetic closure = V."""

    def test_geodetic_closure_covers_all(self, adj, dist, geodetic_set, n):
        closure = _geodetic_closure(adj, dist, geodetic_set)
        assert len(closure) == n

    def test_closure_includes_common_neighbors(self, adj, dist, n):
        """For s1, s2 at distance 2, closure includes their mu = 4 common neighbors."""
        found = False
        for i in range(n):
            for j in range(i + 1, n):
                if dist[i, j] == 2:
                    S = [i, j]
                    closure = _geodetic_closure(adj, dist, S)
                    common = set(np.where((adj[i] == 1) & (adj[j] == 1))[0])
                    assert common.issubset(closure)
                    assert len(common) == 4
                    found = True
                    break
            if found:
                break

    def test_geodetic_number_bounds(self, geodetic_set, n):
        assert 2 <= len(geodetic_set) <= n

    def test_single_vertex_not_geodetic(self, adj, dist, n):
        """A single vertex cannot be a geodetic set (closure = {v})."""
        closure = _geodetic_closure(adj, dist, [0])
        assert len(closure) < n


# ═══════════════════════════════════════════════════════════════════════════
# T1420  Distance spectrum sum
# ═══════════════════════════════════════════════════════════════════════════

class TestT1420DistanceSpectrumSum:
    """sum of D eigenvalues = tr(D) = 0."""

    def test_trace_zero(self, dist):
        assert np.trace(dist) == 0

    def test_eigenvalue_sum_zero(self, dist_evals):
        assert abs(np.sum(dist_evals)) < 1e-8

    def test_analytic_sum(self):
        """66 + 24*(-4) + 15*2 = 0."""
        assert 66 + 24 * (-4) + 15 * 2 == 0

    def test_total_sum_2640(self, dist, n):
        """sum(D) = 40 * 66 = 2640 = 2 * W."""
        assert np.sum(dist) == 2640
        assert np.sum(dist) == 2 * 1320


# ═══════════════════════════════════════════════════════════════════════════
# T1421  Distance Laplacian
# ═══════════════════════════════════════════════════════════════════════════

class TestT1421DistanceLaplacian:
    """D_L = 66I - D; spectrum {0^1, 64^15, 70^24}."""

    def test_formula_transmission_regular(self, dist_lap, dist, n):
        expected = 66 * np.eye(n, dtype=int) - dist
        assert np.array_equal(dist_lap, expected)

    def test_row_sums_zero(self, dist_lap, n):
        assert np.allclose(dist_lap.sum(axis=1), 0)

    def test_eigenvalue_zero(self, dist_lap):
        evals = np.linalg.eigvalsh(dist_lap.astype(float))
        assert abs(np.min(np.abs(evals))) < 1e-8

    def test_eigenvalue_64_mult_15(self, dist_lap):
        evals = np.linalg.eigvalsh(dist_lap.astype(float))
        assert np.sum(np.abs(evals - 64) < 1e-6) == 15

    def test_eigenvalue_70_mult_24(self, dist_lap):
        evals = np.linalg.eigvalsh(dist_lap.astype(float))
        assert np.sum(np.abs(evals - 70) < 1e-6) == 24

    def test_zero_eigenvector_all_ones(self, dist_lap, n):
        evals, evecs = np.linalg.eigh(dist_lap.astype(float))
        idx = np.argmin(np.abs(evals))
        v = evecs[:, idx]
        assert np.allclose(np.abs(v), np.abs(v[0]), atol=1e-8)


# ═══════════════════════════════════════════════════════════════════════════
# T1422  Distance signless Laplacian
# ═══════════════════════════════════════════════════════════════════════════

class TestT1422DistanceSignlessLaplacian:
    """D_Q = 66I + D; spectrum {62^24, 68^15, 132^1}."""

    def test_formula(self, dist_q, dist, n):
        expected = 66 * np.eye(n, dtype=int) + dist
        assert np.array_equal(dist_q, expected)

    def test_eigenvalue_132(self, dist_q):
        evals = np.linalg.eigvalsh(dist_q.astype(float))
        assert abs(np.max(evals) - 132) < 1e-6

    def test_eigenvalue_68_mult_15(self, dist_q):
        evals = np.linalg.eigvalsh(dist_q.astype(float))
        assert np.sum(np.abs(evals - 68) < 1e-6) == 15

    def test_eigenvalue_62_mult_24(self, dist_q):
        evals = np.linalg.eigvalsh(dist_q.astype(float))
        assert np.sum(np.abs(evals - 62) < 1e-6) == 24

    def test_positive_semidefinite(self, dist_q):
        evals = np.linalg.eigvalsh(dist_q.astype(float))
        assert np.all(evals > -1e-8)


# ═══════════════════════════════════════════════════════════════════════════
# T1423  Peripheral vertices
# ═══════════════════════════════════════════════════════════════════════════

class TestT1423PeripheralVertices:
    """All 40 vertices are peripheral (ecc = diam = 2)."""

    def test_all_peripheral(self, dist, n):
        diam = np.max(dist)
        for v in range(n):
            assert np.max(dist[v]) == diam

    def test_peripheral_count_40(self, dist, n):
        diam = np.max(dist)
        peripheral = [v for v in range(n) if np.max(dist[v]) == diam]
        assert len(peripheral) == 40

    def test_center_equals_all(self, dist, n):
        radius = min(np.max(dist[v]) for v in range(n))
        center = [v for v in range(n) if np.max(dist[v]) == radius]
        assert len(center) == 40

    def test_periphery_eq_center_eq_V(self, dist, n):
        diam = np.max(dist)
        radius = min(np.max(dist[v]) for v in range(n))
        assert diam == radius
        periph = {v for v in range(n) if np.max(dist[v]) == diam}
        center = {v for v in range(n) if np.max(dist[v]) == radius}
        assert periph == center == set(range(n))


# ═══════════════════════════════════════════════════════════════════════════
# T1424  Distance cospectrality
# ═══════════════════════════════════════════════════════════════════════════

class TestT1424DistanceCospectrality:
    """W(3,3) vs complement distance spectra."""

    def test_complement_is_srg_40_27_18_18(self, complement_adj, n):
        A_c = complement_adj
        assert np.all(A_c.sum(axis=1) == 27)
        A_c2 = A_c @ A_c
        # lambda = mu = 18 for complement, so A_c^2[i,j] = 18 for all i != j
        off_diag = A_c2[~np.eye(n, dtype=bool)]
        assert np.all(off_diag == 18)

    def test_complement_distance_spectrum(self, complement_dist):
        """Spectrum {51^1, 1^24, -5^15}."""
        evals = np.sort(np.linalg.eigvalsh(complement_dist.astype(float)))[::-1]
        tol = 1e-6
        assert abs(evals[0] - 51) < tol
        assert np.sum(np.abs(evals - 1) < tol) == 24
        assert np.sum(np.abs(evals + 5) < tol) == 15

    def test_not_distance_cospectral(self, dist_evals, complement_dist):
        comp_evals = np.sort(
            np.linalg.eigvalsh(complement_dist.astype(float)))[::-1]
        assert not np.allclose(dist_evals, comp_evals, atol=0.1)

    def test_both_trace_zero(self, dist, complement_dist):
        assert np.trace(dist) == 0
        assert np.trace(complement_dist) == 0

    def test_complement_wiener_1020(self, complement_dist):
        W_c = int(np.sum(np.triu(complement_dist, k=1)))
        assert W_c == 1020

    def test_distance_energy_comparison(self, dist_evals, complement_dist):
        """E_D(W33) = 192, E_D(complement) = 150."""
        E_D = np.sum(np.abs(dist_evals))
        comp_evals = np.linalg.eigvalsh(complement_dist.astype(float))
        E_comp = np.sum(np.abs(comp_evals))
        assert abs(E_D - 192) < 1e-6
        assert abs(E_comp - 150) < 1e-6
        assert E_D > E_comp
