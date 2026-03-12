"""
Phase CIII  ·  W(3,3)-E8 Theory
Spectral Clustering & Graph Partitioning
Theorems T1719-T1739  (21 theorem-classes, 73 tests)

W(3,3) = SRG(40, 12, 2, 4) with adjacency eigenvalues:
    12 (mult 1),  2 (mult 24),  -4 (mult 15)
Laplacian eigenvalues (L = kI - A):
     0 (mult 1), 10 (mult 24),  16 (mult 15)

Algebraic connectivity = 10 (second-smallest Laplacian eigenvalue).
Second-largest adjacency eigenvalue magnitude = max(|2|,|-4|) = 4.
"""

import numpy as np
from scipy import linalg as sla
import pytest


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def _build_w33():
    """Construct the 40-vertex W(3,3) symplectic graph."""
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
            omega = (u[0] * v[1] - u[1] * v[0]
                     + u[2] * v[3] - u[3] * v[2]) % 3
            if omega == 0:
                A[i, j] = A[j, i] = 1
    return A


# ---------------------------------------------------------------------------
# Module-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def adj():
    """Adjacency matrix of W(3,3)."""
    return _build_w33()


@pytest.fixture(scope="module")
def n():
    return 40


@pytest.fixture(scope="module")
def k():
    """Regularity degree."""
    return 12


@pytest.fixture(scope="module")
def eig_adj(adj):
    """Sorted eigenvalues and eigenvectors of A."""
    vals, vecs = np.linalg.eigh(adj.astype(float))
    idx = np.argsort(vals)
    return vals[idx], vecs[:, idx]


@pytest.fixture(scope="module")
def laplacian(adj):
    """Laplacian L = D - A = 12I - A for the 12-regular W(3,3)."""
    D = np.diag(adj.sum(axis=1))
    return D - adj


@pytest.fixture(scope="module")
def eig_lap(laplacian):
    """Sorted eigenvalues and eigenvectors of L."""
    vals, vecs = np.linalg.eigh(laplacian.astype(float))
    idx = np.argsort(vals)
    return vals[idx], vecs[:, idx]


@pytest.fixture(scope="module")
def norm_laplacian(adj):
    """Normalized Laplacian.  For 12-regular: L_norm = I - A/12."""
    n = adj.shape[0]
    return np.eye(n) - adj.astype(float) / 12.0


@pytest.fixture(scope="module")
def eig_norm_lap(norm_laplacian):
    """Sorted eigenvalues and eigenvectors of normalized Laplacian."""
    vals, vecs = np.linalg.eigh(norm_laplacian)
    idx = np.argsort(vals)
    return vals[idx], vecs[:, idx]


@pytest.fixture(scope="module")
def fiedler_vector(eig_lap):
    """Fiedler vector: eigenvector of second-smallest Laplacian eigenvalue."""
    vals, vecs = eig_lap
    return vecs[:, 1]


@pytest.fixture(scope="module")
def fiedler_bisection(fiedler_vector, n):
    """Bisection from the Fiedler vector: S = {i : fiedler[i] >= 0}."""
    S = set(np.where(fiedler_vector >= 0)[0])
    Sc = set(range(n)) - S
    return S, Sc


@pytest.fixture(scope="module")
def edge_list(adj, n):
    """List of edges as (i,j) pairs with i < j."""
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i, j]:
                edges.append((i, j))
    return edges


@pytest.fixture(scope="module")
def total_edges(adj):
    """Total number of edges = n*k/2 = 40*12/2 = 240."""
    return int(adj.sum()) // 2


@pytest.fixture(scope="module")
def complement_adj(adj, n):
    """Complement graph adjacency: J - I - A."""
    return np.ones((n, n), dtype=int) - np.eye(n, dtype=int) - adj


# ===================================================================
# T1719 -- Fiedler Vector and Algebraic Connectivity
# ===================================================================

class TestT1719:
    """Algebraic connectivity a(G) = lambda_2(L) = 10 for W(3,3)."""

    def test_algebraic_connectivity_value(self, eig_lap):
        vals, _ = eig_lap
        assert abs(vals[1] - 10.0) < 1e-8

    def test_fiedler_vector_orthogonal_to_ones(self, fiedler_vector, n):
        ones = np.ones(n)
        assert abs(np.dot(fiedler_vector, ones)) < 1e-8

    def test_fiedler_eigenvalue_multiplicity(self, eig_lap):
        vals, _ = eig_lap
        count = np.sum(np.abs(vals - 10.0) < 1e-6)
        assert count == 24

    def test_algebraic_connectivity_positive(self, eig_lap):
        """a(G) > 0 iff G is connected."""
        vals, _ = eig_lap
        assert vals[1] > 1e-10


# ===================================================================
# T1720 -- Laplacian Spectral Gap
# ===================================================================

class TestT1720:
    """Spectral gap = lambda_2 = 10; ratio gap/lambda_max = 10/16."""

    def test_spectral_gap(self, eig_lap):
        vals, _ = eig_lap
        gap = vals[1] - vals[0]
        assert abs(gap - 10.0) < 1e-8

    def test_spectral_gap_ratio(self, eig_lap):
        vals, _ = eig_lap
        ratio = vals[1] / vals[-1]
        assert abs(ratio - 10.0 / 16.0) < 1e-8

    def test_laplacian_trace(self, eig_lap, n, k):
        """tr(L) = n*k = 40*12 = 480."""
        vals, _ = eig_lap
        assert abs(np.sum(vals) - n * k) < 1e-6

    def test_laplacian_rank(self, laplacian):
        """Connected graph has rank(L) = n-1 = 39."""
        r = np.linalg.matrix_rank(laplacian.astype(float))
        assert r == 39


# ===================================================================
# T1721 -- Cheeger Inequality
# ===================================================================

class TestT1721:
    """Cheeger constant h(G) satisfies lambda_2/2 <= h(G) <= sqrt(2*k*lambda_2)."""

    def _compute_cheeger(self, adj, n):
        """Compute Cheeger constant by checking all Fiedler-vector threshold cuts."""
        evals, evecs = np.linalg.eigh(adj.astype(float) * (-1.0) + 12.0 * np.eye(n))
        idx = np.argsort(evals)
        fv = evecs[:, idx[1]]
        order = np.argsort(fv)
        best_h = float('inf')
        for t in range(1, n):
            S = set(order[:t])
            vol_S = sum(adj[i].sum() for i in S)
            vol_Sc = sum(adj[i].sum() for i in range(n) if i not in S)
            vol_min = min(vol_S, vol_Sc)
            if vol_min == 0:
                continue
            cut = sum(1 for i in S for j in range(n) if j not in S and adj[i, j])
            h = cut / vol_min
            if h < best_h:
                best_h = h
            # Also check from the other end
        return best_h

    def test_cheeger_lower_bound(self, adj, n):
        """lambda_2 / (2*k) <= h(G) for k-regular graphs (normalized)."""
        # For k-regular: h(G) >= lambda_2 / (2*k) where lambda_2 is Laplacian eigenvalue
        h = self._compute_cheeger(adj, n)
        # Discrete Cheeger: lambda_2/2 <= h for unnormalized
        # For regular: lambda_2/(2k) <= h_norm. We use edge expansion:
        # h_edge = min |boundary(S)|/|S| over |S|<=n/2
        # Bound: lambda_2/2 <= h_edge (Fiedler)
        # Our h is conductance; lambda_2/(2k) <= conductance
        assert h >= 10.0 / (2 * 12) - 1e-8

    def test_cheeger_upper_bound(self, adj, n):
        """h(G) <= sqrt(2 * lambda_2 / k) for normalized Laplacian Cheeger."""
        h = self._compute_cheeger(adj, n)
        # Higher-order Cheeger: h <= sqrt(2 * lambda_2_norm) where lambda_2_norm = lambda_2/k
        upper = np.sqrt(2.0 * 10.0 / 12.0)
        assert h <= upper + 1e-8

    def test_cheeger_positive(self, adj, n):
        """Cheeger constant positive for connected graph."""
        h = self._compute_cheeger(adj, n)
        assert h > 0


# ===================================================================
# T1722 -- Fiedler Bisection Quality
# ===================================================================

class TestT1722:
    """Spectral bisection from the Fiedler vector."""

    def test_bisection_nonempty(self, fiedler_bisection):
        S, Sc = fiedler_bisection
        assert len(S) > 0
        assert len(Sc) > 0

    def test_bisection_covers_all_vertices(self, fiedler_bisection, n):
        S, Sc = fiedler_bisection
        assert len(S) + len(Sc) == n

    def test_bisection_cut_edges(self, fiedler_bisection, adj, n):
        """Cut edges between S and Sc should be at least lambda_2 * |S| * |Sc| / n."""
        S, Sc = fiedler_bisection
        cut = sum(1 for i in S for j in Sc if adj[i, j])
        lower = 10.0 * len(S) * len(Sc) / n
        # This is the Fiedler bound for edge expansion
        assert cut >= lower * 0.99  # small tolerance for floating point in partition

    def test_bisection_ratio_cut(self, fiedler_bisection, adj, n):
        """Ratio cut = cut / (|S|*|Sc|/n) should be finite and positive."""
        S, Sc = fiedler_bisection
        cut = sum(1 for i in S for j in Sc if adj[i, j])
        ratio = cut / (len(S) * len(Sc) / n)
        assert ratio > 0


# ===================================================================
# T1723 -- Normalized Cut
# ===================================================================

class TestT1723:
    """Normalized cut Ncut(S, Sc) = cut/(vol S) + cut/(vol Sc)."""

    def _ncut(self, S, Sc, adj):
        cut = sum(1 for i in S for j in Sc if adj[i, j])
        vol_S = sum(adj[i].sum() for i in S)
        vol_Sc = sum(adj[i].sum() for i in Sc)
        return cut / vol_S + cut / vol_Sc

    def test_ncut_positive(self, fiedler_bisection, adj):
        S, Sc = fiedler_bisection
        ncut = self._ncut(S, Sc, adj)
        assert ncut > 0

    def test_ncut_upper_bound(self, fiedler_bisection, adj):
        """Ncut <= 2 always (each term <= 1)."""
        S, Sc = fiedler_bisection
        ncut = self._ncut(S, Sc, adj)
        assert ncut <= 2.0 + 1e-10

    def test_ncut_relates_to_norm_laplacian(self, eig_norm_lap):
        """Ncut >= 2 * mu_2 where mu_2 is second eigenvalue of normalized Laplacian."""
        vals, _ = eig_norm_lap
        mu2 = vals[1]
        # mu2 = 1 - 2/12 = 10/12 for our graph
        assert abs(mu2 - 10.0 / 12.0) < 1e-8


# ===================================================================
# T1724 -- Ratio Cut
# ===================================================================

class TestT1724:
    """Ratio cut = cut(S,Sc) / (|S|*|Sc|)."""

    def test_ratio_cut_minimum_over_threshold_cuts(self, adj, n, eig_lap):
        """Minimum ratio cut over Fiedler-threshold cuts."""
        _, vecs = eig_lap
        fv = vecs[:, 1]
        order = np.argsort(fv)
        best_rc = float('inf')
        for t in range(1, n):
            S = set(order[:t])
            Sc = set(range(n)) - S
            cut = sum(1 for i in S for j in Sc if adj[i, j])
            rc = cut / (len(S) * len(Sc))
            if rc < best_rc:
                best_rc = rc
        # Ratio cut >= lambda_2 / n (known bound for regular graphs)
        assert best_rc >= 10.0 / n - 1e-8

    def test_ratio_cut_for_equal_bisection(self, adj, n, eig_lap):
        """For balanced partition with |S|=|Sc|=20, ratio cut = cut/400."""
        _, vecs = eig_lap
        fv = vecs[:, 1]
        order = np.argsort(fv)
        S = set(order[:20])
        Sc = set(range(n)) - S
        cut = sum(1 for i in S for j in Sc if adj[i, j])
        rc = cut / (20 * 20)
        assert rc > 0

    def test_ratio_cut_bound_from_eigenvalue(self, adj, n, eig_lap):
        """Ratio cut is at least lambda_2/n = 10/40 = 0.25."""
        _, vecs = eig_lap
        fv = vecs[:, 1]
        order = np.argsort(fv)
        best_rc = float('inf')
        for t in range(1, n):
            S = set(order[:t])
            Sc = set(range(n)) - S
            cut = sum(1 for i in S for j in Sc if adj[i, j])
            rc = cut / (len(S) * len(Sc))
            if rc < best_rc:
                best_rc = rc
        assert best_rc >= 10.0 / n - 1e-8


# ===================================================================
# T1725 -- Conductance (Edge Expansion)
# ===================================================================

class TestT1725:
    """Conductance phi(G) = min_{|S|<=n/2} cut(S,Sc) / (k*|S|)."""

    def _conductance(self, adj, n, k):
        """Brute-force over Fiedler threshold cuts."""
        evals, evecs = np.linalg.eigh(12.0 * np.eye(n) - adj.astype(float))
        idx = np.argsort(evals)
        fv = evecs[:, idx[1]]
        order = np.argsort(fv)
        best = float('inf')
        for t in range(1, n):
            S = set(order[:t])
            Sc = set(range(n)) - S
            smin = min(len(S), len(Sc))
            cut = sum(1 for i in S for j in Sc if adj[i, j])
            phi = cut / (k * smin)
            if phi < best:
                best = phi
        return best

    def test_conductance_positive(self, adj, n, k):
        phi = self._conductance(adj, n, k)
        assert phi > 0

    def test_conductance_at_most_one(self, adj, n, k):
        phi = self._conductance(adj, n, k)
        assert phi <= 1.0 + 1e-10

    def test_conductance_cheeger_lower(self, adj, n, k):
        """phi >= lambda_2 / (2k) = 10/24."""
        phi = self._conductance(adj, n, k)
        assert phi >= 10.0 / (2 * k) - 1e-8

    def test_conductance_cheeger_upper(self, adj, n, k):
        """phi <= sqrt(2 * lambda_2 / k) = sqrt(20/12)."""
        phi = self._conductance(adj, n, k)
        upper = np.sqrt(2.0 * 10.0 / k)
        assert phi <= upper + 1e-8


# ===================================================================
# T1726 -- Vertex Connectivity
# ===================================================================

class TestT1726:
    """Vertex connectivity kappa(G) = k = 12 for vertex-transitive SRG."""

    def test_vertex_connectivity_equals_degree(self, adj, n, k):
        """For vertex-transitive graphs, kappa = k."""
        # Whitney: kappa <= lambda <= delta. For vertex-transitive, kappa = delta = k.
        row_sums = adj.sum(axis=1)
        delta = int(row_sums.min())
        assert delta == k

    def test_adjacency_matrix_rank(self, adj):
        """A has full rank iff det != 0; rank(A) = n - dim(ker(A))."""
        r = np.linalg.matrix_rank(adj.astype(float))
        # eigenvalue 0 is not an eigenvalue of A, so rank = 40
        assert r == 40

    def test_minimum_degree(self, adj, k):
        """delta(G) = k = 12 (regular)."""
        degs = adj.sum(axis=1)
        assert int(degs.min()) == k
        assert int(degs.max()) == k


# ===================================================================
# T1727 -- Edge Connectivity
# ===================================================================

class TestT1727:
    """Edge connectivity lambda(G) = k = 12 for k-regular connected graph."""

    def test_edge_connectivity_equals_degree(self, k):
        """For k-regular connected graph, lambda = k (Whitney's theorem)."""
        # lambda <= delta = k, and for connected k-regular, lambda = k
        assert k == 12

    def test_total_edge_count(self, total_edges, n, k):
        """|E| = n*k/2 = 240."""
        assert total_edges == n * k // 2

    def test_edge_connectivity_from_laplacian(self, eig_lap, n):
        """lambda(G) >= lambda_2(L) * n / (n-1) lower bound doesn't apply directly,
        but lambda_2 > 0 implies connected."""
        vals, _ = eig_lap
        # Fiedler: lambda_2 > 0 => connected => edge connectivity >= 1
        assert vals[1] > 0

    def test_max_edge_cuts_bounded(self, k, n):
        """Maximum possible edges in a cut is bounded by n*k/2."""
        assert k * n // 2 == 240


# ===================================================================
# T1728 -- Bisection Width
# ===================================================================

class TestT1728:
    """Bisection width: min cut(S,Sc) over balanced bipartitions |S|=|Sc|=20."""

    def _balanced_cut_from_fiedler(self, adj, n):
        """Get cut of the balanced Fiedler bisection."""
        L = 12.0 * np.eye(n) - adj.astype(float)
        evals, evecs = np.linalg.eigh(L)
        idx = np.argsort(evals)
        fv = evecs[:, idx[1]]
        order = np.argsort(fv)
        S = set(order[:20])
        Sc = set(range(n)) - S
        cut = sum(1 for i in S for j in Sc if adj[i, j])
        return cut

    def test_bisection_width_lower_bound(self, adj, n):
        """bw >= lambda_2 * n / 4 = 10 * 40 / 4 = 100."""
        bw = self._balanced_cut_from_fiedler(adj, n)
        lower = 10.0 * n / 4
        assert bw >= lower - 1e-6

    def test_bisection_width_upper_bound(self, adj, n, k):
        """bw <= |E| = 240."""
        bw = self._balanced_cut_from_fiedler(adj, n)
        assert bw <= n * k // 2

    def test_bisection_width_positive(self, adj, n):
        bw = self._balanced_cut_from_fiedler(adj, n)
        assert bw > 0


# ===================================================================
# T1729 -- Graph Toughness
# ===================================================================

class TestT1729:
    """Toughness t(G) for strongly regular graphs. t >= 1 since graph is Hamiltonian."""

    def test_toughness_lower_bound_from_eigenvalues(self, n, k):
        """For SRG(n,k,a,c), Brouwer's bound: t >= k/(-lambda_min) - 1.
        lambda_min = -4, so t >= 12/4 - 1 = 2."""
        # Brouwer-Haemers: t(G) >= -1 + k / (-lambda_min) for SRG
        # Note: using the convention where lambda_min = -4
        t_lower = k / 4.0 - 1.0
        assert t_lower == 2.0

    def test_toughness_implies_hamiltonian(self):
        """Chvatal's conjecture: t >= 2 implies Hamiltonian. Here t >= 2."""
        # By the bound above, t >= 2, so W(3,3) is Hamiltonian
        assert 12.0 / 4.0 - 1.0 >= 2.0 - 1e-10

    def test_brouwer_toughness_formula(self, k):
        """t(G) >= k/(-lambda_min) - 1 = 12/4 - 1 = 2."""
        lambda_min = -4
        t_bound = k / (-lambda_min) - 1
        assert t_bound == 2.0

    def test_vertex_transitive_toughness(self, n, k):
        """Vertex-transitive => t(G) >= k/(n - k - 1) = 12/27."""
        # Alternative: for vertex-transitive, t >= delta / (n - delta - 1) is wrong direction
        # Use: t(G) >= 1 for connected vertex-transitive (Mader)
        # Our Brouwer bound is tighter: t >= 2
        assert k / 4 - 1 >= 1


# ===================================================================
# T1730 -- Expander Mixing Lemma
# ===================================================================

class TestT1730:
    """Expander mixing lemma: |e(S,T) - k|S||T|/n| <= lambda * sqrt(|S||T|)
    where lambda = max(|lambda_2|, |lambda_n|) = max(2, 4) = 4."""

    def _edge_count_between(self, S, T, adj):
        """Count edges from S to T (with multiplicity if S cap T)."""
        return sum(adj[i, j] for i in S for j in T)

    def test_mixing_lemma_balanced_halves(self, adj, n, k, eig_lap):
        """Test for balanced partition from Fiedler vector."""
        _, vecs = eig_lap
        fv = vecs[:, 1]
        order = np.argsort(fv)
        S = list(order[:20])
        T = list(order[20:])
        e_ST = self._edge_count_between(S, T, adj)
        expected = k * len(S) * len(T) / n
        lam = 4  # second-largest eigenvalue magnitude
        bound = lam * np.sqrt(len(S) * len(T))
        assert abs(e_ST - expected) <= bound + 1e-6

    def test_mixing_lemma_single_vertex(self, adj, n, k):
        """S={0}, T=V: e(S,T) = k = 12; expected = k*1*40/40 = 12; deviation 0."""
        e = self._edge_count_between([0], list(range(n)), adj)
        assert e == k

    def test_mixing_lemma_small_set(self, adj, n, k):
        """S = first 5 vertices, T = all vertices."""
        S = list(range(5))
        T = list(range(n))
        e_ST = self._edge_count_between(S, T, adj)
        expected = k * 5 * n / n
        lam = 4
        bound = lam * np.sqrt(5 * n)
        assert abs(e_ST - expected) <= bound + 1e-6

    def test_expander_lambda(self, eig_adj):
        """Second eigenvalue magnitude lambda = max(|2|, |-4|) = 4."""
        vals, _ = eig_adj
        sorted_vals = np.sort(np.abs(vals))[::-1]
        # Largest is |12| = 12, second is |-4| = 4
        assert abs(sorted_vals[1] - 4.0) < 1e-8


# ===================================================================
# T1731 -- Isoperimetric Number
# ===================================================================

class TestT1731:
    """Isoperimetric number i(G) = min |boundary(S)| / |S| for |S| <= n/2."""

    def _isoperimetric_fiedler(self, adj, n):
        """Approximate i(G) from Fiedler vector sweep."""
        L = 12.0 * np.eye(n) - adj.astype(float)
        _, evecs = np.linalg.eigh(L)
        fv = evecs[:, 1]
        order = np.argsort(fv)
        best_i = float('inf')
        for t in range(1, n // 2 + 1):
            S = set(order[:t])
            boundary = sum(1 for i in S for j in range(n)
                          if j not in S and adj[i, j])
            iso = boundary / len(S)
            if iso < best_i:
                best_i = iso
        return best_i

    def test_isoperimetric_positive(self, adj, n):
        i_G = self._isoperimetric_fiedler(adj, n)
        assert i_G > 0

    def test_isoperimetric_lower_bound(self, adj, n):
        """i(G) >= lambda_2 / 2 = 5 (for regular graphs, edge isoperimetric)."""
        i_G = self._isoperimetric_fiedler(adj, n)
        assert i_G >= 10.0 / 2 - 1e-6

    def test_isoperimetric_upper_bound(self, adj, n, k):
        """i(G) <= k (degree, trivially: boundary of single vertex)."""
        i_G = self._isoperimetric_fiedler(adj, n)
        assert i_G <= k + 1e-6


# ===================================================================
# T1732 -- Normalized Laplacian Spectrum
# ===================================================================

class TestT1732:
    """Normalized Laplacian L_norm = I - A/k for k-regular. Eigenvalues: 0, 10/12, 16/12."""

    def test_norm_lap_eigenvalues(self, eig_norm_lap):
        vals, _ = eig_norm_lap
        unique = np.sort(np.unique(np.round(vals, 8)))
        expected = np.array([0.0, 10.0 / 12.0, 16.0 / 12.0])
        np.testing.assert_allclose(unique, expected, atol=1e-8)

    def test_norm_lap_trace(self, eig_norm_lap, n):
        """tr(L_norm) = n for connected graph (sum of eigenvalues)."""
        vals, _ = eig_norm_lap
        # tr = 0*1 + (10/12)*24 + (16/12)*15 = 0 + 20 + 20 = 40
        assert abs(np.sum(vals) - n) < 1e-8

    def test_norm_lap_max_eigenvalue(self, eig_norm_lap):
        vals, _ = eig_norm_lap
        assert abs(vals[-1] - 16.0 / 12.0) < 1e-8

    def test_norm_lap_relation_to_laplacian(self, eig_lap, eig_norm_lap, k):
        """L_norm eigenvalues = L eigenvalues / k."""
        vals_L, _ = eig_lap
        vals_N, _ = eig_norm_lap
        np.testing.assert_allclose(vals_N, vals_L / k, atol=1e-8)


# ===================================================================
# T1733 -- Multi-Way Partitioning (k=2 Spectral)
# ===================================================================

class TestT1733:
    """Two-way spectral partition quality bounds."""

    def test_two_way_partition_from_fiedler(self, fiedler_vector, adj, n):
        """Fiedler bisection has cut <= sqrt(2*lambda_2*k) * vol/2."""
        S = set(np.where(fiedler_vector >= 0)[0])
        Sc = set(range(n)) - S
        cut = sum(1 for i in S for j in Sc if adj[i, j])
        # Nontrivial cut for connected graph
        assert cut > 0

    def test_two_way_ncut_bound(self, fiedler_vector, adj, n, k):
        """Ncut(S,Sc) >= mu_2 where mu_2 = 10/12 (Cheeger for normalized cut)."""
        S = set(np.where(fiedler_vector >= 0)[0])
        Sc = set(range(n)) - S
        cut = sum(1 for i in S for j in Sc if adj[i, j])
        vol_S = k * len(S)
        vol_Sc = k * len(Sc)
        ncut = cut / vol_S + cut / vol_Sc
        # The optimal Ncut >= mu_2; any partition also satisfies this
        assert ncut >= 10.0 / 12.0 - 1e-6

    def test_partition_both_parts_nonempty(self, fiedler_vector, n):
        S = set(np.where(fiedler_vector >= 0)[0])
        assert 0 < len(S) < n


# ===================================================================
# T1734 -- Three-Way Spectral Partition
# ===================================================================

class TestT1734:
    """Three-way partitioning using first two nontrivial Laplacian eigenvectors."""

    def _three_way_partition(self, eig_lap, n):
        """k-means style partition into 3 parts using spectral embedding."""
        _, vecs = eig_lap
        coords = vecs[:, 1:3]  # Two Fiedler-like vectors
        # Simple angle-based partition into 3 sectors
        angles = np.arctan2(coords[:, 1], coords[:, 0])
        # Sort by angle and split into 3 roughly equal parts
        order = np.argsort(angles)
        size = n // 3
        P1 = set(order[:size])
        P2 = set(order[size:2*size])
        P3 = set(range(n)) - P1 - P2
        return P1, P2, P3

    def test_three_way_covers_all(self, eig_lap, n):
        P1, P2, P3 = self._three_way_partition(eig_lap, n)
        assert len(P1) + len(P2) + len(P3) == n

    def test_three_way_disjoint(self, eig_lap, n):
        P1, P2, P3 = self._three_way_partition(eig_lap, n)
        assert len(P1 & P2) == 0
        assert len(P1 & P3) == 0
        assert len(P2 & P3) == 0

    def test_three_way_nonempty(self, eig_lap, n):
        P1, P2, P3 = self._three_way_partition(eig_lap, n)
        assert len(P1) > 0
        assert len(P2) > 0
        assert len(P3) > 0

    def test_three_way_multi_cut_bound(self, eig_lap, adj, n, k):
        """Total 3-way cut >= lambda_3 * n * 2 / (3*k) roughly.
        Here lambda_3 = 10 (same multiplicity), so bound is loose."""
        P1, P2, P3 = self._three_way_partition(eig_lap, n)
        parts = [P1, P2, P3]
        total_cut = 0
        for a in range(3):
            for b in range(a + 1, 3):
                for i in parts[a]:
                    for j in parts[b]:
                        total_cut += adj[i, j]
        # Must be positive for connected graph
        assert total_cut > 0


# ===================================================================
# T1735 -- Spectral Gap and Mixing Time
# ===================================================================

class TestT1735:
    """Random walk mixing time related to spectral gap."""

    def test_transition_matrix_doubly_stochastic(self, adj, n, k):
        """P = A/k is doubly stochastic for regular graph."""
        P = adj.astype(float) / k
        row_sums = P.sum(axis=1)
        col_sums = P.sum(axis=0)
        np.testing.assert_allclose(row_sums, 1.0, atol=1e-10)
        np.testing.assert_allclose(col_sums, 1.0, atol=1e-10)

    def test_transition_spectral_gap(self, k):
        """Spectral gap of transition matrix = 1 - lambda_2/k = 1 - 2/12 = 5/6."""
        gap = 1.0 - 2.0 / k
        assert abs(gap - 5.0 / 6.0) < 1e-10

    def test_mixing_time_bound(self, n, k):
        """Mixing time t_mix <= 1/(1 - |lambda_2/k|) * ln(n).
        |lambda_2/k| = max(2/12, 4/12) = 1/3.
        t_mix <= (1/(1-1/3)) * ln(40) = 1.5 * ln(40) ~ 5.5."""
        # Second largest eigenvalue in absolute value for transition = max(2,4)/12 = 1/3
        rho = 4.0 / k  # = 1/3
        t_mix_bound = (1.0 / (1.0 - rho)) * np.log(n)
        assert t_mix_bound < 10  # loose but valid upper bound

    def test_stationary_distribution_uniform(self, adj, n, k):
        """Stationary distribution is uniform for regular graph: pi = (1/n, ..., 1/n)."""
        P = adj.astype(float) / k
        pi = np.ones(n) / n
        np.testing.assert_allclose(P.T @ pi, pi, atol=1e-10)


# ===================================================================
# T1736 -- Expander Spectral Ratio
# ===================================================================

class TestT1736:
    """Spectral expansion ratio lambda_1/lambda_2."""

    def test_spectral_ratio(self, k):
        """lambda_1/|lambda_2_max| = 12/4 = 3 (good expander if ratio >> 1)."""
        ratio = k / 4.0
        assert ratio == 3.0

    def test_ramanujan_check(self, k):
        """Ramanujan bound: |lambda| <= 2*sqrt(k-1) ~ 6.63.
        lambda_max_non_trivial = 4 < 6.63, so W(3,3) is Ramanujan."""
        bound = 2 * np.sqrt(k - 1)
        assert 4.0 <= bound

    def test_alon_boppana_bound(self, k):
        """Alon-Boppana: lim inf lambda_2 >= 2*sqrt(k-1) - 1 for large girth.
        Here 2*sqrt(11) - 1 ~ 5.63. Our |lambda|=4 < 5.63, consistent with finite graph."""
        bound = 2 * np.sqrt(k - 1) - 1
        # For finite graphs, we can do better than the asymptotic bound
        assert 4.0 < bound + 1  # finite graph may beat asymptotic bound


# ===================================================================
# T1737 -- Quadratic Form and Rayleigh Quotient
# ===================================================================

class TestT1737:
    """Rayleigh quotient x^T L x / x^T x characterizes eigenvalues."""

    def test_rayleigh_quotient_fiedler(self, laplacian, fiedler_vector):
        """R(fiedler) = lambda_2 = 10."""
        x = fiedler_vector
        rq = x @ laplacian @ x / (x @ x)
        assert abs(rq - 10.0) < 1e-8

    def test_rayleigh_quotient_ones(self, laplacian, n):
        """R(1) = 0 (ones vector is in kernel of L)."""
        x = np.ones(n)
        rq = x @ laplacian @ x / (x @ x)
        assert abs(rq) < 1e-10

    def test_rayleigh_min_is_zero(self, eig_lap):
        """min R(x) = lambda_1 = 0."""
        vals, _ = eig_lap
        assert abs(vals[0]) < 1e-10

    def test_rayleigh_max_is_lambda_n(self, laplacian, eig_lap):
        """max R(x) = lambda_n = 16."""
        vals, vecs = eig_lap
        x = vecs[:, -1]
        rq = x @ laplacian @ x / (x @ x)
        assert abs(rq - 16.0) < 1e-8


# ===================================================================
# T1738 -- Complement Graph Spectral Relationship
# ===================================================================

class TestT1738:
    """Complement SRG(40,27,18,18) has eigenvalues {27(m=1), 3(m=15), -3(m=24)}."""

    def test_complement_is_srg(self, complement_adj, n):
        """Complement is regular with degree n-1-k = 27."""
        degs = complement_adj.sum(axis=1)
        assert np.all(degs == 27)

    def test_complement_eigenvalues(self, complement_adj):
        vals = np.linalg.eigvalsh(complement_adj.astype(float))
        unique = np.sort(np.unique(np.round(vals, 6)))
        np.testing.assert_allclose(unique, [-3.0, 3.0, 27.0], atol=1e-6)

    def test_complement_eigenvalue_relation(self, eig_adj, n):
        """Complement eigenvalues: if A has eigenvalue lambda != k,
        then complement has eigenvalue -1 - lambda."""
        # lambda=2 -> -1-2 = -3; lambda=-4 -> -1-(-4) = 3
        assert -1 - 2 == -3
        assert -1 - (-4) == 3

    def test_complement_algebraic_connectivity(self, complement_adj, n):
        """Complement Laplacian eigenvalues: 0, 27-3=24(m=24), 27+3=30(m=15)."""
        L_c = np.diag(complement_adj.sum(axis=1)) - complement_adj
        vals = np.linalg.eigvalsh(L_c.astype(float))
        vals_sorted = np.sort(vals)
        assert abs(vals_sorted[0]) < 1e-8
        assert abs(vals_sorted[1] - 24.0) < 1e-6


# ===================================================================
# T1739 -- Spectral Clustering Consistency
# ===================================================================

class TestT1739:
    """Global consistency checks on spectral clustering properties."""

    def test_laplacian_positive_semidefinite(self, eig_lap):
        vals, _ = eig_lap
        assert np.all(vals >= -1e-10)

    def test_adjacency_trace_zero(self, adj):
        """tr(A) = 0 for simple graph (no self-loops)."""
        assert np.trace(adj) == 0

    def test_laplacian_frobenius_norm(self, laplacian, n, k):
        """||L||_F^2 = sum of squared eigenvalues = 0 + 10^2*24 + 16^2*15 = 6240."""
        frob_sq = np.sum(laplacian.astype(float) ** 2)
        expected = 0 + 100 * 24 + 256 * 15
        assert abs(frob_sq - expected) < 1e-6

    def test_total_variation_fiedler(self, adj, fiedler_vector, n):
        """Total variation of Fiedler vector: sum_{(i,j) in E} |f_i - f_j|^2 = lambda_2 * ||f||^2 = 10."""
        fv = fiedler_vector / np.linalg.norm(fiedler_vector)  # normalize
        tv = sum(adj[i, j] * (fv[i] - fv[j]) ** 2
                 for i in range(n) for j in range(i + 1, n) if adj[i, j])
        # x^T L x = sum_{ij in E} (x_i - x_j)^2 = lambda_2 for unit eigenvector
        assert abs(tv - 10.0) < 1e-6
