"""
Phase CXXXI -- Graph Product Theory on W(3,3) = SRG(40,12,2,4).

90+ tests covering Cartesian product G□H, tensor/categorical product G*H,
strong product G⊠H, lexicographic product G[H], corona product, modular
product, and rooted product.  For each product: vertex count, edge count,
regularity, spectrum formulas, adjacency rule, commutativity/associativity
where applicable, products with K1/K2/K3, Shannon capacity bounds,
independence/clique numbers in products.

All tests use only numpy and standard library.  Every assertion is
mathematically provable from the SRG(40,12,2,4) adjacency spectrum
    {12^1, 2^24, (-4)^15}.

Small factor graphs used: K1, K2, K3, K4, C4, P3.
"""

import numpy as np
from numpy.linalg import eigvalsh
import pytest

# ── Constants ─────────────────────────────────────────────────────────────────

_N, _K, _LAM, _MU = 40, 12, 2, 4

# ── W(3,3) builder ───────────────────────────────────────────────────────────


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


# ── Small graph builders ─────────────────────────────────────────────────────


def _complete_graph(n):
    """Complete graph K_n."""
    return (np.ones((n, n), dtype=int) - np.eye(n, dtype=int)).astype(int)


def _cycle_graph(n):
    """Cycle graph C_n."""
    A = np.zeros((n, n), dtype=int)
    for i in range(n):
        A[i, (i + 1) % n] = A[(i + 1) % n, i] = 1
    return A


def _path_graph(n):
    """Path graph P_n on n vertices."""
    A = np.zeros((n, n), dtype=int)
    for i in range(n - 1):
        A[i, i + 1] = A[i + 1, i] = 1
    return A


# ── Product builders ─────────────────────────────────────────────────────────


def _cartesian_product(A, B):
    """Cartesian product G□H:  A(G)⊗I_m + I_n⊗A(H)."""
    n, m = A.shape[0], B.shape[0]
    return (np.kron(A, np.eye(m, dtype=int))
            + np.kron(np.eye(n, dtype=int), B))


def _tensor_product(A, B):
    """Tensor / categorical product G×H:  A(G)⊗A(H)."""
    return np.kron(A, B)


def _strong_product(A, B):
    """Strong product G⊠H:  A(G)⊗I + I⊗A(H) + A(G)⊗A(H)."""
    n, m = A.shape[0], B.shape[0]
    In = np.eye(n, dtype=int)
    Im = np.eye(m, dtype=int)
    return np.kron(A, Im) + np.kron(In, B) + np.kron(A, B)


def _lexicographic_product(A, B):
    """Lexicographic product G[H]:  A(G)⊗J_m + I_n⊗A(H).

    J_m is the m×m all-ones matrix (including diagonal).
    """
    n, m = A.shape[0], B.shape[0]
    J = np.ones((m, m), dtype=int)
    return np.kron(A, J) + np.kron(np.eye(n, dtype=int), B)


def _corona_product(A, B):
    """Corona product G∘H: one copy of G, |V(G)| copies of H,
    vertex i of G joined to all vertices of the i-th copy of H."""
    n, m = A.shape[0], B.shape[0]
    N = n + n * m
    C = np.zeros((N, N), dtype=int)
    C[:n, :n] = A
    for i in range(n):
        r = n + i * m
        C[r:r + m, r:r + m] = B
        for j in range(m):
            C[i, r + j] = C[r + j, i] = 1
    return C


def _modular_product(A, B):
    """Modular product: (u1,v1)~(u2,v2) iff u1!=u2, v1!=v2 and
    (u1~u2 AND v1~v2) OR (u1!~u2 AND v1!~v2)."""
    n, m = A.shape[0], B.shape[0]
    N = n * m
    C = np.zeros((N, N), dtype=int)
    for i1 in range(n):
        for j1 in range(m):
            for i2 in range(n):
                for j2 in range(m):
                    if i1 == i2 or j1 == j2:
                        continue
                    ag = int(A[i1, i2])
                    bh = int(B[j1, j2])
                    if (ag == 1 and bh == 1) or (ag == 0 and bh == 0):
                        C[i1 * m + j1, i2 * m + j2] = 1
    return C


def _rooted_product(A, B, root=0):
    """Rooted product G∘_r H: n copies of H whose root vertices are
    connected according to G."""
    n, m = A.shape[0], B.shape[0]
    N = n * m
    C = np.zeros((N, N), dtype=int)
    # Internal H-edges in each copy
    for i in range(n):
        for a in range(m):
            for b in range(m):
                if B[a, b]:
                    C[i * m + a, i * m + b] = 1
    # G-edges between root vertices
    for i in range(n):
        for j in range(n):
            if A[i, j]:
                C[i * m + root, j * m + root] = 1
    return C


# ── Spectrum helpers ─────────────────────────────────────────────────────────


def _sorted_eigs(M):
    """Sorted eigenvalues of a symmetric integer matrix."""
    return np.sort(eigvalsh(M.astype(float)))


def _spectrum_eq(actual, expected, atol=1e-6):
    """Check two sorted spectra agree entry-by-entry."""
    a = np.sort(np.asarray(actual, dtype=float))
    e = np.sort(np.asarray(expected, dtype=float))
    return a.shape == e.shape and np.allclose(a, e, atol=atol)


def _num_edges(A):
    return int(A.sum()) // 2


def _hoffman_bound(A):
    """Hoffman independence-number bound for a regular graph."""
    n = A.shape[0]
    vals = eigvalsh(A.astype(float))
    k = float(np.max(vals))
    lmin = float(np.min(vals))
    if lmin >= -1e-12:
        return float(n)
    return n * (-lmin) / (k - lmin)


def _clique_bound(A):
    """Ratio bound on clique number: omega <= 1 - k/lambda_min."""
    vals = eigvalsh(A.astype(float))
    k = float(np.max(vals))
    lmin = float(np.min(vals))
    if lmin >= -1e-12:
        return A.shape[0]
    return 1.0 - k / lmin


def _independence_number_small(A):
    """Exact independence number via backtracking (small graphs only, n<=20)."""
    n = A.shape[0]
    assert n <= 20, "Graph too large for exact independence number"
    best = [0]

    def bt(idx, indep_set):
        if len(indep_set) + (n - idx) <= best[0]:
            return
        if idx == n:
            best[0] = max(best[0], len(indep_set))
            return
        # Try excluding idx
        bt(idx + 1, indep_set)
        # Try including idx
        if all(A[idx, v] == 0 for v in indep_set):
            indep_set.append(idx)
            bt(idx + 1, indep_set)
            indep_set.pop()

    bt(0, [])
    return best[0]


# ── Expected spectrum builders ───────────────────────────────────────────────

# W(3,3) adjacency eigenvalues with multiplicities
_W33_EIGS = [12.0] * 1 + [2.0] * 24 + [-4.0] * 15  # 40 total

_K1 = np.zeros((1, 1), dtype=int)
_K2_EIGS = [1.0, -1.0]
_K3_EIGS = [2.0, -1.0, -1.0]
_K4_EIGS = [3.0, -1.0, -1.0, -1.0]
_C4_EIGS = [2.0, 0.0, 0.0, -2.0]
_P3_EIGS = [np.sqrt(2), 0.0, -np.sqrt(2)]


def _cartesian_spectrum(eigs_g, eigs_h):
    """Eigenvalues of Cartesian product: lambda_i + mu_j."""
    out = []
    for l in eigs_g:
        for m in eigs_h:
            out.append(l + m)
    return sorted(out)


def _tensor_spectrum(eigs_g, eigs_h):
    """Eigenvalues of tensor product: lambda_i * mu_j."""
    out = []
    for l in eigs_g:
        for m in eigs_h:
            out.append(l * m)
    return sorted(out)


def _strong_spectrum(eigs_g, eigs_h):
    """Eigenvalues of strong product: (1+lambda_i)(1+mu_j) - 1."""
    out = []
    for l in eigs_g:
        for m in eigs_h:
            out.append((1 + l) * (1 + m) - 1)
    return sorted(out)


def _lex_spectrum_regular(eigs_g, eigs_h, m_h, k_h):
    """Eigenvalues of G[H] for regular H with |V(H)|=m_h, degree k_h.

    For each eigenvalue lambda_i of G: lambda_i * m_h + k_h.
    For each non-trivial eigenvalue mu_j of H (not k_h): mu_j with mult n_g.
    """
    n_g = len(eigs_g)
    # Eigenvalue k_h appears once in H-spectrum; rest are non-trivial
    out = []
    for l in eigs_g:
        out.append(l * m_h + k_h)
    # Non-trivial H eigenvalues (all except the largest = k_h)
    h_sorted = sorted(eigs_h, reverse=True)
    for mu in h_sorted[1:]:  # skip the degree eigenvalue
        for _ in range(n_g):
            out.append(mu)
    return sorted(out)


# ── Module-scoped fixtures ───────────────────────────────────────────────────

@pytest.fixture(scope="module")
def W():
    """Adjacency matrix of W(3,3)."""
    return _build_w33()


@pytest.fixture(scope="module")
def K2():
    return _complete_graph(2)


@pytest.fixture(scope="module")
def K3():
    return _complete_graph(3)


@pytest.fixture(scope="module")
def K4():
    return _complete_graph(4)


@pytest.fixture(scope="module")
def C4():
    return _cycle_graph(4)


@pytest.fixture(scope="module")
def P3():
    return _path_graph(3)


@pytest.fixture(scope="module")
def K1():
    return _K1.copy()


# =============================================================================
# Section 1 :  W(3,3) prerequisites  (6 tests)
# =============================================================================

class TestW33Prerequisites:
    """Verify W(3,3) = SRG(40,12,2,4) and its spectrum."""

    def test_vertex_count(self, W):
        assert W.shape == (_N, _N)

    def test_symmetric(self, W):
        assert np.array_equal(W, W.T)

    def test_no_self_loops(self, W):
        assert np.all(np.diag(W) == 0)

    def test_regular_degree_12(self, W):
        assert np.all(W.sum(axis=1) == _K)

    def test_edge_count_240(self, W):
        assert _num_edges(W) == _N * _K // 2  # 240

    def test_adjacency_spectrum(self, W):
        vals = _sorted_eigs(W)
        assert _spectrum_eq(vals, _W33_EIGS)


# =============================================================================
# Section 2 :  Factor graph spectra  (5 tests)
# =============================================================================

class TestFactorGraphSpectra:
    """Verify spectra of small factor graphs K2, K3, K4, C4, P3."""

    def test_K2_spectrum(self, K2):
        assert _spectrum_eq(_sorted_eigs(K2), _K2_EIGS)

    def test_K3_spectrum(self, K3):
        assert _spectrum_eq(_sorted_eigs(K3), _K3_EIGS)

    def test_K4_spectrum(self, K4):
        assert _spectrum_eq(_sorted_eigs(K4), _K4_EIGS)

    def test_C4_spectrum(self, C4):
        assert _spectrum_eq(_sorted_eigs(C4), _C4_EIGS)

    def test_P3_spectrum(self, P3):
        assert _spectrum_eq(_sorted_eigs(P3), _P3_EIGS)


# =============================================================================
# Section 3 :  Cartesian product G□H  (14 tests)
# =============================================================================

class TestCartesianProduct:
    """Cartesian product: eigenvalues lambda_i + mu_j."""

    def test_vertex_count_K2(self, W, K2):
        P = _cartesian_product(W, K2)
        assert P.shape == (80, 80)

    def test_vertex_count_K3(self, W, K3):
        P = _cartesian_product(W, K3)
        assert P.shape == (120, 120)

    def test_edge_count_K2(self, W, K2):
        P = _cartesian_product(W, K2)
        # |E| = m*|E_G| + n*|E_H| = 2*240 + 40*1 = 520
        assert _num_edges(P) == 520

    def test_edge_count_K3(self, W, K3):
        P = _cartesian_product(W, K3)
        # |E| = 3*240 + 40*3 = 840
        assert _num_edges(P) == 840

    def test_regularity_K2(self, W, K2):
        P = _cartesian_product(W, K2)
        assert np.all(P.sum(axis=1) == 13)  # 12 + 1

    def test_regularity_K3(self, W, K3):
        P = _cartesian_product(W, K3)
        assert np.all(P.sum(axis=1) == 14)  # 12 + 2

    def test_spectrum_K2(self, W, K2):
        P = _cartesian_product(W, K2)
        expected = _cartesian_spectrum(_W33_EIGS, _K2_EIGS)
        assert _spectrum_eq(_sorted_eigs(P), expected)

    def test_spectrum_K3(self, W, K3):
        P = _cartesian_product(W, K3)
        expected = _cartesian_spectrum(_W33_EIGS, _K3_EIGS)
        assert _spectrum_eq(_sorted_eigs(P), expected)

    def test_spectrum_C4(self, W, C4):
        P = _cartesian_product(W, C4)
        expected = _cartesian_spectrum(_W33_EIGS, _C4_EIGS)
        assert _spectrum_eq(_sorted_eigs(P), expected)

    def test_symmetric(self, W, K2):
        P = _cartesian_product(W, K2)
        assert np.array_equal(P, P.T)

    def test_no_self_loops(self, W, K3):
        P = _cartesian_product(W, K3)
        assert np.all(np.diag(P) == 0)

    def test_commutativity_spectrum(self):
        """K2□K3 and K3□K2 have the same spectrum."""
        A, B = _complete_graph(2), _complete_graph(3)
        P1 = _cartesian_product(A, B)
        P2 = _cartesian_product(B, A)
        assert _spectrum_eq(_sorted_eigs(P1), _sorted_eigs(P2))

    def test_associativity_spectrum(self):
        """(K2□K3)□C4 and K2□(K3□C4) have the same spectrum."""
        A, B, C = _complete_graph(2), _complete_graph(3), _cycle_graph(4)
        P1 = _cartesian_product(_cartesian_product(A, B), C)
        P2 = _cartesian_product(A, _cartesian_product(B, C))
        assert _spectrum_eq(_sorted_eigs(P1), _sorted_eigs(P2))

    def test_product_with_K1(self, W):
        """G□K1 is isomorphic to G (identity element)."""
        P = _cartesian_product(W, _K1)
        assert np.array_equal(P, W)


# =============================================================================
# Section 4 :  Tensor / categorical product G×H  (12 tests)
# =============================================================================

class TestTensorProduct:
    """Tensor product: eigenvalues lambda_i * mu_j."""

    def test_vertex_count_K2(self, W, K2):
        P = _tensor_product(W, K2)
        assert P.shape == (80, 80)

    def test_edge_count_K2(self, W, K2):
        P = _tensor_product(W, K2)
        # 2 * |E_G| * |E_H| = 2*240*1 = 480
        assert _num_edges(P) == 480

    def test_edge_count_K3(self, W, K3):
        P = _tensor_product(W, K3)
        # 2 * 240 * 3 = 1440
        assert _num_edges(P) == 1440

    def test_regularity_K2(self, W, K2):
        P = _tensor_product(W, K2)
        assert np.all(P.sum(axis=1) == 12)  # k_G * k_H = 12 * 1

    def test_regularity_K3(self, W, K3):
        P = _tensor_product(W, K3)
        assert np.all(P.sum(axis=1) == 24)  # 12 * 2

    def test_spectrum_K2(self, W, K2):
        P = _tensor_product(W, K2)
        expected = _tensor_spectrum(_W33_EIGS, _K2_EIGS)
        assert _spectrum_eq(_sorted_eigs(P), expected)

    def test_spectrum_K3(self, W, K3):
        P = _tensor_product(W, K3)
        expected = _tensor_spectrum(_W33_EIGS, _K3_EIGS)
        assert _spectrum_eq(_sorted_eigs(P), expected)

    def test_spectrum_C4(self, W, C4):
        P = _tensor_product(W, C4)
        expected = _tensor_spectrum(_W33_EIGS, _C4_EIGS)
        assert _spectrum_eq(_sorted_eigs(P), expected)

    def test_symmetric(self, W, K3):
        P = _tensor_product(W, K3)
        assert np.array_equal(P, P.T)

    def test_commutativity_spectrum(self):
        """K3×K4 and K4×K3 have the same spectrum."""
        A, B = _complete_graph(3), _complete_graph(4)
        P1 = _tensor_product(A, B)
        P2 = _tensor_product(B, A)
        assert _spectrum_eq(_sorted_eigs(P1), _sorted_eigs(P2))

    def test_associativity_spectrum(self):
        """(K2×K3)×C4 and K2×(K3×C4) have the same spectrum."""
        A, B, C = _complete_graph(2), _complete_graph(3), _cycle_graph(4)
        P1 = _tensor_product(_tensor_product(A, B), C)
        P2 = _tensor_product(A, _tensor_product(B, C))
        assert _spectrum_eq(_sorted_eigs(P1), _sorted_eigs(P2))

    def test_K2_tensor_K2_disconnected(self):
        """K2×K2 has two connected components (bipartite tensor = disconnected)."""
        A = _complete_graph(2)
        P = _tensor_product(A, A)
        # K2 x K2 = two disjoint edges.  Spectrum: {1, 1, -1, -1}.
        vals = _sorted_eigs(P)
        assert _spectrum_eq(vals, [-1, -1, 1, 1])
        assert _num_edges(P) == 2


# =============================================================================
# Section 5 :  Strong product G⊠H  (13 tests)
# =============================================================================

class TestStrongProduct:
    """Strong product: eigenvalues (1+lambda_i)(1+mu_j) - 1."""

    def test_vertex_count_K2(self, W, K2):
        P = _strong_product(W, K2)
        assert P.shape == (80, 80)

    def test_edge_count_K2(self, W, K2):
        P = _strong_product(W, K2)
        # Cartesian(520) + Tensor(480) = 1000
        assert _num_edges(P) == 1000

    def test_edge_count_K3(self, W, K3):
        P = _strong_product(W, K3)
        # (3*240+40*3) + (2*240*3) = 840 + 1440 = 2280
        assert _num_edges(P) == 2280

    def test_regularity_K2(self, W, K2):
        P = _strong_product(W, K2)
        # (1+12)(1+1)-1 = 25
        assert np.all(P.sum(axis=1) == 25)

    def test_regularity_K3(self, W, K3):
        P = _strong_product(W, K3)
        # (1+12)(1+2)-1 = 38
        assert np.all(P.sum(axis=1) == 38)

    def test_spectrum_K2(self, W, K2):
        P = _strong_product(W, K2)
        expected = _strong_spectrum(_W33_EIGS, _K2_EIGS)
        assert _spectrum_eq(_sorted_eigs(P), expected)

    def test_spectrum_K3(self, W, K3):
        P = _strong_product(W, K3)
        expected = _strong_spectrum(_W33_EIGS, _K3_EIGS)
        assert _spectrum_eq(_sorted_eigs(P), expected)

    def test_spectrum_C4(self, W, C4):
        P = _strong_product(W, C4)
        expected = _strong_spectrum(_W33_EIGS, _C4_EIGS)
        assert _spectrum_eq(_sorted_eigs(P), expected)

    def test_symmetric(self, W, K2):
        P = _strong_product(W, K2)
        assert np.array_equal(P, P.T)

    def test_equals_cart_plus_tensor(self, W, K3):
        """A(G⊠H) = A(G□H) + A(G×H) (union of Cartesian and tensor)."""
        Sc = _cartesian_product(W, K3)
        St = _tensor_product(W, K3)
        Ss = _strong_product(W, K3)
        assert np.array_equal(Ss, Sc + St)

    def test_commutativity_spectrum(self):
        A, B = _complete_graph(3), _cycle_graph(4)
        P1 = _strong_product(A, B)
        P2 = _strong_product(B, A)
        assert _spectrum_eq(_sorted_eigs(P1), _sorted_eigs(P2))

    def test_associativity_spectrum(self):
        A, B, C = _complete_graph(2), _complete_graph(3), _cycle_graph(4)
        P1 = _strong_product(_strong_product(A, B), C)
        P2 = _strong_product(A, _strong_product(B, C))
        assert _spectrum_eq(_sorted_eigs(P1), _sorted_eigs(P2))

    def test_product_with_K1(self, W):
        """G⊠K1 is isomorphic to G (identity for strong product)."""
        P = _strong_product(W, _K1)
        assert np.array_equal(P, W)


# =============================================================================
# Section 6 :  Lexicographic product G[H]  (11 tests)
# =============================================================================

class TestLexicographicProduct:
    """Lexicographic product G[H]:  A(G)⊗J_m + I_n⊗A(H)."""

    def test_vertex_count_K2(self, W, K2):
        P = _lexicographic_product(W, K2)
        assert P.shape == (80, 80)

    def test_edge_count_K2(self, W, K2):
        P = _lexicographic_product(W, K2)
        # |E_G|*m^2 + n*|E_H| = 240*4 + 40*1 = 1000
        assert _num_edges(P) == 1000

    def test_edge_count_K3(self, W, K3):
        P = _lexicographic_product(W, K3)
        # 240*9 + 40*3 = 2280
        assert _num_edges(P) == 2280

    def test_regularity_K2(self, W, K2):
        P = _lexicographic_product(W, K2)
        # k_G * |H| + k_H = 12*2 + 1 = 25
        assert np.all(P.sum(axis=1) == 25)

    def test_regularity_C4(self, W, C4):
        P = _lexicographic_product(W, C4)
        # 12*4 + 2 = 50
        assert np.all(P.sum(axis=1) == 50)

    def test_spectrum_K2_matches_formula(self, W, K2):
        """Spectrum of G[K2] from the explicit formula for regular H."""
        P = _lexicographic_product(W, K2)
        expected = _lex_spectrum_regular(_W33_EIGS, _K2_EIGS, 2, 1)
        assert _spectrum_eq(_sorted_eigs(P), expected)

    def test_spectrum_K3_matches_formula(self, W, K3):
        P = _lexicographic_product(W, K3)
        expected = _lex_spectrum_regular(_W33_EIGS, _K3_EIGS, 3, 2)
        assert _spectrum_eq(_sorted_eigs(P), expected)

    def test_spectrum_C4_matches_formula(self, W, C4):
        P = _lexicographic_product(W, C4)
        expected = _lex_spectrum_regular(_W33_EIGS, _C4_EIGS, 4, 2)
        assert _spectrum_eq(_sorted_eigs(P), expected)

    def test_G_lex_Kn_equals_strong_Kn(self, W, K3):
        """G[K_n] = G⊠K_n when H is complete."""
        Pl = _lexicographic_product(W, K3)
        Ps = _strong_product(W, K3)
        assert np.array_equal(Pl, Ps)

    def test_not_commutative(self):
        """C4[K2] != K2[C4]:  different degree, hence different spectra."""
        A, B = _cycle_graph(4), _complete_graph(2)
        P1 = _lexicographic_product(A, B)
        P2 = _lexicographic_product(B, A)
        d1 = P1.sum(axis=1)
        d2 = P2.sum(axis=1)
        # C4[K2]: degree 2*2+1=5;  K2[C4]: degree 1*4+2=6
        assert np.all(d1 == 5)
        assert np.all(d2 == 6)

    def test_product_with_K1(self, W):
        """G[K1] is isomorphic to G."""
        P = _lexicographic_product(W, _K1)
        assert np.array_equal(P, W)


# =============================================================================
# Section 7 :  Corona product  (8 tests)
# =============================================================================

class TestCoronaProduct:
    """Corona product G∘H."""

    def test_vertex_count_K1(self, W):
        P = _corona_product(W, _K1)
        # n + n*1 = 80
        assert P.shape == (80, 80)

    def test_vertex_count_K2(self, W, K2):
        P = _corona_product(W, K2)
        # 40 + 40*2 = 120
        assert P.shape == (120, 120)

    def test_edge_count_K1(self, W):
        P = _corona_product(W, _K1)
        # |E_G| + n*|E_H| + n*m = 240 + 0 + 40 = 280
        assert _num_edges(P) == 280

    def test_edge_count_K2(self, W, K2):
        P = _corona_product(W, K2)
        # 240 + 40*1 + 40*2 = 360
        assert _num_edges(P) == 360

    def test_not_regular_K2(self, W, K2):
        """Corona is not regular: G-vertices deg 14, H-vertices deg 2."""
        P = _corona_product(W, K2)
        degs = P.sum(axis=1)
        g_degs = degs[:40]
        h_degs = degs[40:]
        assert np.all(g_degs == 14)   # 12 + 2
        assert np.all(h_degs == 2)    # 1 (K2 partner) + 1 (G vertex)

    def test_symmetric(self, W, K2):
        P = _corona_product(W, K2)
        assert np.array_equal(P, P.T)

    def test_no_self_loops(self, W, K2):
        P = _corona_product(W, K2)
        assert np.all(np.diag(P) == 0)

    def test_not_commutative(self):
        """K2∘K3 != K3∘K2 (different vertex counts)."""
        A, B = _complete_graph(2), _complete_graph(3)
        P1 = _corona_product(A, B)
        P2 = _corona_product(B, A)
        assert P1.shape != P2.shape


# =============================================================================
# Section 8 :  Modular product  (9 tests)
# =============================================================================

class TestModularProduct:
    """Modular product: same-type adjacency across both factors."""

    def test_vertex_count_C4(self, W, C4):
        P = _modular_product(W, C4)
        assert P.shape == (160, 160)

    def test_symmetric_C4(self, W, C4):
        P = _modular_product(W, C4)
        assert np.array_equal(P, P.T)

    def test_no_self_loops_C4(self, W, C4):
        P = _modular_product(W, C4)
        assert np.all(np.diag(P) == 0)

    def test_regularity_C4(self, W, C4):
        """Both factors regular => modular product regular.
        degree = k1*k2 + (n1-1-k1)*(n2-1-k2) = 12*2 + 27*1 = 51."""
        P = _modular_product(W, C4)
        assert np.all(P.sum(axis=1) == 51)

    def test_edge_count_C4(self, W, C4):
        P = _modular_product(W, C4)
        assert _num_edges(P) == 160 * 51 // 2  # 4080

    def test_regularity_formula_K4(self, W, K4):
        """k1*k2 + (n1-1-k1)*(n2-1-k2) = 12*3 + 27*0 = 36."""
        P = _modular_product(W, K4)
        assert np.all(P.sum(axis=1) == 36)

    def test_equals_tensor_for_complete_H(self, W, K3):
        """When H is complete, non-edge condition never fires,
        so modular product = tensor product."""
        Pm = _modular_product(W, K3)
        Pt = _tensor_product(W, K3)
        assert np.array_equal(Pm, Pt)

    def test_commutativity_spectrum(self):
        """C4 mod K3 and K3 mod C4 have the same spectrum."""
        A, B = _cycle_graph(4), _complete_graph(3)
        P1 = _modular_product(A, B)
        P2 = _modular_product(B, A)
        assert _spectrum_eq(_sorted_eigs(P1), _sorted_eigs(P2))

    def test_small_modular_C4_C4(self):
        """C4 mod C4: degree = 2*2 + 1*1 = 5, 16 vertices."""
        A = _cycle_graph(4)
        P = _modular_product(A, A)
        assert P.shape == (16, 16)
        assert np.all(P.sum(axis=1) == 5)
        assert _num_edges(P) == 40


# =============================================================================
# Section 9 :  Rooted product  (8 tests)
# =============================================================================

class TestRootedProduct:
    """Rooted product G o_r H:  n copies of H, root-vertices joined by G."""

    def test_vertex_count_P3(self, W, P3):
        P = _rooted_product(W, P3, root=0)
        assert P.shape == (120, 120)

    def test_vertex_count_K3(self, W, K3):
        P = _rooted_product(W, K3, root=0)
        assert P.shape == (120, 120)

    def test_edge_count_P3(self, W, P3):
        P = _rooted_product(W, P3, root=0)
        # n*|E_H| + |E_G| = 40*2 + 240 = 320
        assert _num_edges(P) == 320

    def test_edge_count_K3(self, W, K3):
        P = _rooted_product(W, K3, root=0)
        # 40*3 + 240 = 360
        assert _num_edges(P) == 360

    def test_symmetric(self, W, P3):
        P = _rooted_product(W, P3, root=0)
        assert np.array_equal(P, P.T)

    def test_no_self_loops(self, W, K3):
        P = _rooted_product(W, K3, root=0)
        assert np.all(np.diag(P) == 0)

    def test_degree_distribution_P3(self, W, P3):
        """Root vertices (v,0): deg(0 in P3)=1 + deg_G=12 = 13.
        Middle vertices (v,1): deg(1 in P3) = 2.
        Leaf vertices (v,2): deg(2 in P3) = 1."""
        P = _rooted_product(W, P3, root=0)
        degs = P.sum(axis=1)
        for i in range(40):
            assert degs[i * 3 + 0] == 13   # root
            assert degs[i * 3 + 1] == 2    # middle
            assert degs[i * 3 + 2] == 1    # leaf

    def test_root_adjacency_matches_G(self, W, P3):
        """Root vertices are adjacent iff corresponding G-vertices are."""
        P = _rooted_product(W, P3, root=0)
        m = P3.shape[0]
        for i in range(40):
            for j in range(i + 1, 40):
                assert P[i * m, j * m] == W[i, j]


# =============================================================================
# Section 10 :  Cross-product identities  (6 tests)
# =============================================================================

class TestCrossProductIdentities:
    """Relationships between different product types."""

    def test_strong_is_cart_plus_tensor_K2(self, W, K2):
        """A(G⊠K2) = A(G□K2) + A(G×K2)."""
        Sc = _cartesian_product(W, K2)
        St = _tensor_product(W, K2)
        Ss = _strong_product(W, K2)
        assert np.array_equal(Ss, Sc + St)

    def test_strong_is_cart_plus_tensor_C4(self, W, C4):
        """A(G⊠C4) = A(G□C4) + A(G×C4)."""
        Sc = _cartesian_product(W, C4)
        St = _tensor_product(W, C4)
        Ss = _strong_product(W, C4)
        assert np.array_equal(Ss, Sc + St)

    def test_lex_Kn_equals_strong_Kn_K2(self, W, K2):
        """G[K2] = G⊠K2 (holds when H is complete)."""
        Pl = _lexicographic_product(W, K2)
        Ps = _strong_product(W, K2)
        assert np.array_equal(Pl, Ps)

    def test_lex_Kn_equals_strong_Kn_K4(self, W, K4):
        """G[K4] = G⊠K4."""
        Pl = _lexicographic_product(W, K4)
        Ps = _strong_product(W, K4)
        assert np.array_equal(Pl, Ps)

    def test_lex_not_equal_strong_for_non_complete(self, W, C4):
        """G[C4] != G⊠C4 when H is not complete."""
        Pl = _lexicographic_product(W, C4)
        Ps = _strong_product(W, C4)
        assert not np.array_equal(Pl, Ps)

    def test_edge_count_identity_strong(self, W, C4):
        """Edge count of strong = Cartesian + tensor edge counts."""
        ec = _num_edges(_cartesian_product(W, C4))
        et = _num_edges(_tensor_product(W, C4))
        es = _num_edges(_strong_product(W, C4))
        assert es == ec + et


# =============================================================================
# Section 11 :  Shannon capacity, independence, clique bounds  (10 tests)
# =============================================================================

class TestShannonCapacityBounds:
    """Hoffman bound, independence/clique bounds in products."""

    def test_hoffman_bound_w33(self, W):
        """Hoffman bound: alpha <= n*|lmin|/(k+|lmin|) = 40*4/16 = 10."""
        hb = _hoffman_bound(W)
        assert abs(hb - 10.0) < 1e-8

    def test_clique_bound_w33(self, W):
        """Ratio bound: omega <= 1 - k/lmin = 1 + 12/4 = 4."""
        cb = _clique_bound(W)
        assert abs(cb - 4.0) < 1e-8

    def test_hoffman_cartesian_K2(self, W, K2):
        """Hoffman bound for G□K2: n=80, k=13, lmin=-5 => 80*5/18."""
        P = _cartesian_product(W, K2)
        hb = _hoffman_bound(P)
        expected = 80.0 * 5.0 / 18.0
        assert abs(hb - expected) < 1e-6

    def test_hoffman_tensor_K2(self, W, K2):
        """Hoffman bound for G×K2: n=80, k=12, lmin=-12 => 80*12/24 = 40."""
        P = _tensor_product(W, K2)
        hb = _hoffman_bound(P)
        assert abs(hb - 40.0) < 1e-6

    def test_hoffman_strong_K2(self, W, K2):
        """Hoffman bound for G⊠K2: n=80, k=25, lmin=-7 => 80*7/32 = 17.5."""
        P = _strong_product(W, K2)
        hb = _hoffman_bound(P)
        assert abs(hb - 17.5) < 1e-6

    def test_hoffman_strong_product_bound(self, W, K3):
        """Hoffman(G⊠H) >= Hoffman(G) * alpha(H) for strong product.
        For K3: alpha=1. Hoffman(G)=10. So Hoffman(G⊠K3) >= 10."""
        P = _strong_product(W, K3)
        hb = _hoffman_bound(P)
        assert hb >= 10.0 - 1e-8

    def test_independence_small_C4(self):
        """alpha(C4) = 2."""
        A = _cycle_graph(4)
        assert _independence_number_small(A) == 2

    def test_independence_small_P3(self):
        """alpha(P3) = 2."""
        A = _path_graph(3)
        assert _independence_number_small(A) == 2

    def test_independence_small_K4(self):
        """alpha(K4) = 1."""
        A = _complete_graph(4)
        assert _independence_number_small(A) == 1

    def test_strong_product_independence_bound(self):
        """alpha(C4 ⊠ P3) >= alpha(C4) * alpha(P3) = 2*2 = 4."""
        A = _cycle_graph(4)
        B = _path_graph(3)
        P = _strong_product(A, B)
        alpha_prod = _independence_number_small(P)
        assert alpha_prod >= 4


# =============================================================================
# Section 12 :  Adjacency rule verification  (7 tests)
# =============================================================================

class TestAdjacencyRules:
    """Spot-check the adjacency definition for each product type."""

    def test_cartesian_adjacency_rule(self, W, K2):
        """(u1,v1)~(u2,v2) iff (u1=u2 and v1~v2) or (u1~u2 and v1=v2)."""
        P = _cartesian_product(W, K2)
        m = 2
        for _ in range(200):
            i1, j1 = np.random.randint(40), np.random.randint(m)
            i2, j2 = np.random.randint(40), np.random.randint(m)
            if i1 == i2 and j1 == j2:
                continue
            rule = ((i1 == i2 and K2[j1, j2]) or
                    (W[i1, i2] and j1 == j2))
            assert P[i1 * m + j1, i2 * m + j2] == int(rule)

    def test_tensor_adjacency_rule(self, W, K3):
        """(u1,v1)~(u2,v2) iff u1~u2 AND v1~v2."""
        P = _tensor_product(W, K3)
        m = 3
        for _ in range(200):
            i1, j1 = np.random.randint(40), np.random.randint(m)
            i2, j2 = np.random.randint(40), np.random.randint(m)
            if i1 == i2 and j1 == j2:
                continue
            rule = bool(W[i1, i2]) and bool(K3[j1, j2])
            assert P[i1 * m + j1, i2 * m + j2] == int(rule)

    def test_strong_adjacency_rule(self, W, K2):
        """(u1,v1)~(u2,v2) iff (u1~u2 or u1=u2) and (v1~v2 or v1=v2),
        excluding self-loops."""
        P = _strong_product(W, K2)
        m = 2
        for _ in range(200):
            i1, j1 = np.random.randint(40), np.random.randint(m)
            i2, j2 = np.random.randint(40), np.random.randint(m)
            if i1 == i2 and j1 == j2:
                continue
            g_ok = (W[i1, i2] == 1) or (i1 == i2)
            h_ok = (K2[j1, j2] == 1) or (j1 == j2)
            rule = g_ok and h_ok
            assert P[i1 * m + j1, i2 * m + j2] == int(rule)

    def test_lexicographic_adjacency_rule(self, W, C4):
        """(u1,v1)~(u2,v2) iff u1~u2 OR (u1=u2 and v1~v2)."""
        C = _cycle_graph(4)
        P = _lexicographic_product(W, C)
        m = 4
        for _ in range(200):
            i1, j1 = np.random.randint(40), np.random.randint(m)
            i2, j2 = np.random.randint(40), np.random.randint(m)
            if i1 == i2 and j1 == j2:
                continue
            rule = bool(W[i1, i2]) or (i1 == i2 and bool(C[j1, j2]))
            assert P[i1 * m + j1, i2 * m + j2] == int(rule)

    def test_corona_adjacency_rule(self, W, K2):
        """G-vertex i ~ H-vertex (i,k) for all k; internal H edges preserved."""
        P = _corona_product(W, K2)
        n, m = 40, 2
        # Check G-to-H connections
        for i in range(n):
            for k in range(m):
                assert P[i, n + i * m + k] == 1
        # Check no cross-connections between different H copies
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                for ki in range(m):
                    for kj in range(m):
                        assert P[n + i * m + ki, n + j * m + kj] == 0

    def test_modular_adjacency_rule(self):
        """(u1,v1)~(u2,v2) iff u1!=u2, v1!=v2, same adjacency type."""
        A = _cycle_graph(4)
        B = _path_graph(3)
        P = _modular_product(A, B)
        na, nb = 4, 3
        for i1 in range(na):
            for j1 in range(nb):
                for i2 in range(na):
                    for j2 in range(nb):
                        if i1 == i2 and j1 == j2:
                            continue
                        v1 = i1 * nb + j1
                        v2 = i2 * nb + j2
                        if i1 == i2 or j1 == j2:
                            assert P[v1, v2] == 0
                        else:
                            same = (A[i1, i2] == B[j1, j2])
                            assert P[v1, v2] == int(same)

    def test_rooted_adjacency_rule(self, W, P3):
        """Root-root edges match G; internal edges match H."""
        R = _rooted_product(W, P3, root=0)
        m = 3
        # Root-root adjacency matches W
        for i in range(40):
            for j in range(i + 1, 40):
                assert R[i * m, j * m] == W[i, j]
        # Internal edges match P3 within each copy
        Hp = _path_graph(3)
        for i in range(40):
            for a in range(m):
                for b in range(m):
                    assert R[i * m + a, i * m + b] == Hp[a, b]


# =============================================================================
# Section 13 :  Additional spectrum and product tests  (5 tests)
# =============================================================================

class TestAdditionalProductProperties:
    """Extra tests for coverage: spectrum with P3, K4, and mixed products."""

    def test_cartesian_P3_spectrum(self, W, P3):
        """Spectrum of G□P3 matches formula even though P3 is not regular."""
        P = _cartesian_product(W, P3)
        expected = _cartesian_spectrum(_W33_EIGS, _P3_EIGS)
        assert _spectrum_eq(_sorted_eigs(P), expected)

    def test_tensor_P3_spectrum(self, W, P3):
        P = _tensor_product(W, P3)
        expected = _tensor_spectrum(_W33_EIGS, _P3_EIGS)
        assert _spectrum_eq(_sorted_eigs(P), expected)

    def test_strong_P3_spectrum(self, W, P3):
        P = _strong_product(W, P3)
        expected = _strong_spectrum(_W33_EIGS, _P3_EIGS)
        assert _spectrum_eq(_sorted_eigs(P), expected)

    def test_cartesian_K4_spectrum(self, W, K4):
        P = _cartesian_product(W, K4)
        expected = _cartesian_spectrum(_W33_EIGS, _K4_EIGS)
        assert _spectrum_eq(_sorted_eigs(P), expected)

    def test_strong_K4_spectrum(self, W, K4):
        P = _strong_product(W, K4)
        expected = _strong_spectrum(_W33_EIGS, _K4_EIGS)
        assert _spectrum_eq(_sorted_eigs(P), expected)


# =============================================================================
# Section 14 :  Lexicographic associativity and extra  (3 tests)
# =============================================================================

class TestLexicographicExtra:
    """Associativity and edge-count formulas for lexicographic product."""

    def test_associativity_spectrum(self):
        """(K2[K3])[C4] and K2[K3[C4]] have the same spectrum."""
        A = _complete_graph(2)
        B = _complete_graph(3)
        C = _cycle_graph(4)
        P1 = _lexicographic_product(_lexicographic_product(A, B), C)
        P2 = _lexicographic_product(A, _lexicographic_product(B, C))
        assert _spectrum_eq(_sorted_eigs(P1), _sorted_eigs(P2))

    def test_edge_count_formula_C4(self, W, C4):
        """Edges = |E_G|*m^2 + n*|E_H| = 240*16 + 40*4 = 4000."""
        P = _lexicographic_product(W, C4)
        assert _num_edges(P) == 4000

    def test_lex_C4_degree(self, W, C4):
        """G[C4]: degree = k_G*|C4| + k_{C4} = 12*4 + 2 = 50."""
        P = _lexicographic_product(W, C4)
        assert np.all(P.sum(axis=1) == 50)
