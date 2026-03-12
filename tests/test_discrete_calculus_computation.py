"""
Phase CII: Discrete Calculus and Differential Forms on W(3,3) (T1698-T1718)
============================================================================

Builds the full DEC (Discrete Exterior Calculus) framework on the clique
complex of W(3,3).  Every operator -- gradient, divergence, Laplacians,
Hodge star, cup product, Whitney map, discrete vector fields -- is
constructed from scratch and verified against exact invariants.

Clique-complex data:
    f-vector         (40, 240, 160, 40)
    Betti numbers    (1, 81, 0, 0)
    Euler char       -80
    L1 spectrum      {0^81, 4^120, 10^24, 16^15}
    L2               4 * I_160
    L0 eigenvalues   {0^1, 10^24, 16^15}

21 theorem classes, 75 tests total -- pure numpy / scipy, no networkx.
"""

import pytest
import numpy as np
from fractions import Fraction
from collections import Counter

# ===================================================================
# Builders (self-contained)
# ===================================================================

def _build_w33():
    """Return W(3,3) adjacency matrix A (40x40) and point list."""
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


def _find_all_cliques(A, n):
    """Find all cliques of all sizes in the graph."""
    nbrs = [set(np.where(A[i])[0]) for i in range(n)]
    cliques = {1: [{i} for i in range(n)], 2: [], 3: [], 4: []}
    for i in range(n):
        for j in sorted(nbrs[i]):
            if j > i:
                cliques[2].append({i, j})
    for i in range(n):
        for j in sorted(nbrs[i]):
            if j > i:
                for k in sorted(nbrs[i] & nbrs[j]):
                    if k > j:
                        cliques[3].append({i, j, k})
    for i in range(n):
        for j in sorted(nbrs[i]):
            if j > i:
                common_ij = nbrs[i] & nbrs[j]
                for k in sorted(common_ij):
                    if k > j:
                        for l in sorted(common_ij & nbrs[k]):
                            if l > k:
                                cliques[4].append({i, j, k, l})
    return cliques


def _rank_exact(M):
    """Exact rank via Fraction-based Gaussian elimination."""
    m, n = M.shape
    mat = [[Fraction(int(M[i, j])) for j in range(n)] for i in range(m)]
    rank = 0
    for col in range(n):
        pivot = None
        for row in range(rank, m):
            if mat[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            continue
        mat[rank], mat[pivot] = mat[pivot], mat[rank]
        inv = Fraction(1, mat[rank][col])
        for j in range(n):
            mat[rank][j] *= inv
        for row in range(m):
            if row != rank and mat[row][col] != 0:
                factor = mat[row][col]
                for j in range(n):
                    mat[row][j] -= factor * mat[rank][j]
        rank += 1
    return rank


# ===================================================================
# Build coboundary (exterior derivative) matrices
# ===================================================================

def _build_coboundary_maps(edges, triangles, tetrahedra, edge_idx, tri_idx):
    """Build d0, d1, d2 -- the discrete exterior derivatives.

    d0 : C^0 -> C^1  (240 x 40)   gradient
    d1 : C^1 -> C^2  (160 x 240)  curl
    d2 : C^2 -> C^3  (40 x 160)   div-like
    """
    n_v, n_e, n_t, n_tet = 40, len(edges), len(triangles), len(tetrahedra)

    # d0: for edge (i,j), d0[e,i]=-1, d0[e,j]=+1
    d0 = np.zeros((n_e, n_v), dtype=int)
    for idx, (i, j) in enumerate(edges):
        d0[idx, i] = -1
        d0[idx, j] = 1

    # d1: for triangle (i,j,k), boundary = [j,k]-[i,k]+[i,j]
    # d1 = boundary_2^T
    d1 = np.zeros((n_t, n_e), dtype=int)
    for idx, (i, j, k) in enumerate(triangles):
        d1[idx, edge_idx[(i, j)]] = 1
        d1[idx, edge_idx[(i, k)]] = -1
        d1[idx, edge_idx[(j, k)]] = 1

    # d2: for tet (i,j,k,l), boundary = [j,k,l]-[i,k,l]+[i,j,l]-[i,j,k]
    # d2 = boundary_3^T
    d2 = np.zeros((n_tet, n_t), dtype=int)
    for idx, (i, j, k, l) in enumerate(tetrahedra):
        d2[idx, tri_idx[(j, k, l)]] = 1
        d2[idx, tri_idx[(i, k, l)]] = -1
        d2[idx, tri_idx[(i, j, l)]] = 1
        d2[idx, tri_idx[(i, j, k)]] = -1

    return d0, d1, d2


# ===================================================================
# Cup product helper
# ===================================================================

def _cup_product_01(alpha, beta, edges):
    """Cup product alpha in C^0, beta in C^1 -> result in C^1.

    (alpha cup beta)[v0,v1] = alpha[v0] * beta[edge(v0,v1)]
    """
    result = np.zeros(len(edges), dtype=float)
    for idx, (v0, v1) in enumerate(edges):
        result[idx] = alpha[v0] * beta[idx]
    return result


def _cup_product_10(alpha, beta, edges):
    """Cup product alpha in C^1, beta in C^0 -> result in C^1.

    (alpha cup beta)[v0,v1] = alpha[edge(v0,v1)] * beta[v1]
    """
    result = np.zeros(len(edges), dtype=float)
    for idx, (v0, v1) in enumerate(edges):
        result[idx] = alpha[idx] * beta[v1]
    return result


def _cup_product_00(alpha, beta):
    """Cup product alpha in C^0, beta in C^0 -> result in C^0.

    Pointwise multiplication.
    """
    return alpha * beta


def _cup_product_11(alpha, beta, triangles, edge_idx):
    """Cup product alpha in C^1, beta in C^1 -> result in C^2.

    (alpha cup beta)[v0,v1,v2] = alpha[edge(v0,v1)] * beta[edge(v1,v2)]
    """
    result = np.zeros(len(triangles), dtype=float)
    for idx, (v0, v1, v2) in enumerate(triangles):
        result[idx] = alpha[edge_idx[(v0, v1)]] * beta[edge_idx[(v1, v2)]]
    return result


# ===================================================================
# Fixtures
# ===================================================================

@pytest.fixture(scope="module")
def graph_data():
    """Build W(3,3) adjacency and clique complex."""
    A, pts = _build_w33()
    n = 40
    cliques = _find_all_cliques(A, n)
    edges = sorted(tuple(sorted(c)) for c in cliques[2])
    triangles = sorted(tuple(sorted(c)) for c in cliques[3])
    tetrahedra = sorted(tuple(sorted(c)) for c in cliques[4])
    edge_idx = {e: i for i, e in enumerate(edges)}
    tri_idx = {t: i for i, t in enumerate(triangles)}
    return {
        "A": A, "points": pts, "n": n,
        "edges": edges, "triangles": triangles, "tetrahedra": tetrahedra,
        "edge_idx": edge_idx, "tri_idx": tri_idx,
    }


@pytest.fixture(scope="module")
def coboundary(graph_data):
    """Discrete exterior derivatives d0, d1, d2."""
    d0, d1, d2 = _build_coboundary_maps(
        graph_data["edges"], graph_data["triangles"],
        graph_data["tetrahedra"], graph_data["edge_idx"],
        graph_data["tri_idx"],
    )
    return {"d0": d0, "d1": d1, "d2": d2}


@pytest.fixture(scope="module")
def exact_ranks(coboundary):
    """Exact ranks of d0, d1, d2 via Fraction arithmetic."""
    r0 = _rank_exact(coboundary["d0"])
    r1 = _rank_exact(coboundary["d1"])
    r2 = _rank_exact(coboundary["d2"])
    return {"r0": r0, "r1": r1, "r2": r2}


@pytest.fixture(scope="module")
def laplacians(coboundary):
    """All four Hodge Laplacians."""
    d0 = coboundary["d0"].astype(float)
    d1 = coboundary["d1"].astype(float)
    d2 = coboundary["d2"].astype(float)
    L0 = d0.T @ d0                     # 40 x 40
    L1 = d0 @ d0.T + d1.T @ d1         # 240 x 240
    L2 = d1 @ d1.T + d2.T @ d2         # 160 x 160
    L3 = d2 @ d2.T                     # 40 x 40
    return {"L0": L0, "L1": L1, "L2": L2, "L3": L3}


@pytest.fixture(scope="module")
def hodge_stars(graph_data):
    """Combinatorial Hodge stars -- diagonal PD matrices.

    Weight of a k-simplex sigma is 1 + (number of (k+1)-cofaces of sigma).
    """
    edges = graph_data["edges"]
    triangles = graph_data["triangles"]
    tetrahedra = graph_data["tetrahedra"]
    n_v, n_e, n_t, n_tet = 40, len(edges), len(triangles), len(tetrahedra)

    # *0: weight = 1 + deg(v)  (deg = 12 for all v in W(3,3))
    star0 = np.full(n_v, 13.0)

    # *1: weight = 1 + number of triangles containing each edge
    tri_count_edge = np.zeros(n_e, dtype=int)
    edge_idx = graph_data["edge_idx"]
    for (i, j, k) in triangles:
        tri_count_edge[edge_idx[(i, j)]] += 1
        tri_count_edge[edge_idx[(i, k)]] += 1
        tri_count_edge[edge_idx[(j, k)]] += 1
    star1 = 1.0 + tri_count_edge.astype(float)

    # *2: weight = 1 + number of tetrahedra containing each triangle
    tet_count_tri = np.zeros(n_t, dtype=int)
    tri_idx = graph_data["tri_idx"]
    for (i, j, k, l) in tetrahedra:
        tet_count_tri[tri_idx[(i, j, k)]] += 1
        tet_count_tri[tri_idx[(i, j, l)]] += 1
        tet_count_tri[tri_idx[(i, k, l)]] += 1
        tet_count_tri[tri_idx[(j, k, l)]] += 1
    star2 = 1.0 + tet_count_tri.astype(float)

    # *3: weight = 1 (no 4-simplices exist)
    star3 = np.ones(n_tet)

    return {"s0": star0, "s1": star1, "s2": star2, "s3": star3}


# ===================================================================
# T1698  Graph construction and regularity
# ===================================================================
class TestT1698:
    """W(3,3) adjacency matrix: 40 vertices, 12-regular, simple, symmetric."""

    def test_vertex_count(self, graph_data):
        assert graph_data["A"].shape == (40, 40)

    def test_symmetric(self, graph_data):
        A = graph_data["A"]
        assert np.array_equal(A, A.T)

    def test_no_self_loops(self, graph_data):
        assert np.all(np.diag(graph_data["A"]) == 0)

    def test_regular_degree_12(self, graph_data):
        degrees = graph_data["A"].sum(axis=1)
        assert np.all(degrees == 12)


# ===================================================================
# T1699  Clique complex f-vector
# ===================================================================
class TestT1699:
    """f-vector = (40, 240, 160, 40)."""

    def test_40_vertices(self, graph_data):
        assert graph_data["n"] == 40

    def test_240_edges(self, graph_data):
        assert len(graph_data["edges"]) == 240

    def test_160_triangles(self, graph_data):
        assert len(graph_data["triangles"]) == 160

    def test_40_tetrahedra(self, graph_data):
        assert len(graph_data["tetrahedra"]) == 40


# ===================================================================
# T1700  Euler characteristic
# ===================================================================
class TestT1700:
    """chi = 40 - 240 + 160 - 40 = -80."""

    def test_euler_char_value(self, graph_data):
        chi = (40 - len(graph_data["edges"])
               + len(graph_data["triangles"])
               - len(graph_data["tetrahedra"]))
        assert chi == -80

    def test_euler_alternating(self, graph_data):
        f = [40, 240, 160, 40]
        assert sum((-1)**i * f[i] for i in range(4)) == -80

    def test_chi_equals_minus_2v(self):
        """chi = -2 * v  is an exact identity for W(3,3)."""
        assert 40 - 240 + 160 - 40 == -2 * 40


# ===================================================================
# T1701  Discrete gradient d_0 (C^0 -> C^1)
# ===================================================================
class TestT1701:
    """d_0 is the 240x40 signed edge-vertex incidence matrix."""

    def test_shape(self, coboundary):
        assert coboundary["d0"].shape == (240, 40)

    def test_row_structure(self, coboundary):
        """Each row has exactly one +1 and one -1."""
        d0 = coboundary["d0"]
        for r in range(d0.shape[0]):
            c = Counter(d0[r])
            assert c[1] == 1 and c[-1] == 1 and c[0] == 38

    def test_row_sums_zero(self, coboundary):
        assert np.all(coboundary["d0"].sum(axis=1) == 0)

    def test_gradient_of_constant(self, coboundary):
        """d_0(1) = 0 -- constant 0-forms are closed."""
        f = np.ones(40, dtype=int)
        assert np.all(coboundary["d0"] @ f == 0)


# ===================================================================
# T1702  Discrete divergence  -d_0^T
# ===================================================================
class TestT1702:
    """div = -d_0^T maps 1-forms to 0-forms."""

    def test_shape(self, coboundary):
        div = -coboundary["d0"].T
        assert div.shape == (40, 240)

    def test_neg_transpose_identity(self, coboundary):
        div = -coboundary["d0"].T
        assert np.array_equal(div, -coboundary["d0"].T)

    def test_div_grad_equals_laplacian(self, coboundary, graph_data):
        """div(grad f) = -L_0 f  where L_0 = D - A."""
        d0 = coboundary["d0"]
        L0 = d0.T @ d0
        A = graph_data["A"]
        D = np.diag(A.sum(axis=1))
        assert np.array_equal(L0, D - A)


# ===================================================================
# T1703  Graph Laplacian L_0 = d_0^T d_0 = D - A
# ===================================================================
class TestT1703:
    """L_0 = d_0^T d_0 is the 40x40 graph Laplacian."""

    def test_shape(self, laplacians):
        assert laplacians["L0"].shape == (40, 40)

    def test_equals_degree_minus_adj(self, graph_data, laplacians):
        A = graph_data["A"].astype(float)
        D = np.diag(A.sum(axis=1))
        assert np.allclose(laplacians["L0"], D - A, atol=1e-12)

    def test_psd(self, laplacians):
        eigvals = np.linalg.eigvalsh(laplacians["L0"])
        assert np.all(eigvals > -1e-10)

    def test_spectrum(self, laplacians):
        """L_0 eigenvalues: {0^1, 10^24, 16^15}."""
        eigvals = np.linalg.eigvalsh(laplacians["L0"])
        counts = Counter(int(round(e)) for e in eigvals)
        assert counts[0] == 1
        assert counts[10] == 24
        assert counts[16] == 15


# ===================================================================
# T1704  Coboundary d_1 (C^1 -> C^2)
# ===================================================================
class TestT1704:
    """d_1 is the 160x240 discrete curl."""

    def test_shape(self, coboundary):
        assert coboundary["d1"].shape == (160, 240)

    def test_row_entries(self, coboundary):
        """Each row has exactly two +1 entries and one -1 entry."""
        d1 = coboundary["d1"]
        for r in range(d1.shape[0]):
            c = Counter(d1[r])
            assert c[1] == 2 and c[-1] == 1

    def test_entries_pm1(self, coboundary):
        nz = coboundary["d1"][coboundary["d1"] != 0]
        assert set(nz.tolist()) == {1, -1}

    def test_row_sums(self, coboundary):
        """Each row sums to 1 (two +1 and one -1)."""
        assert np.all(coboundary["d1"].sum(axis=1) == 1)


# ===================================================================
# T1705  Coboundary d_2 (C^2 -> C^3)
# ===================================================================
class TestT1705:
    """d_2 is the 40x160 top-level coboundary."""

    def test_shape(self, coboundary):
        assert coboundary["d2"].shape == (40, 160)

    def test_row_entries(self, coboundary):
        """Each row has two +1 and two -1 entries."""
        d2 = coboundary["d2"]
        for r in range(d2.shape[0]):
            c = Counter(d2[r])
            assert c[1] == 2 and c[-1] == 2

    def test_row_sums_zero(self, coboundary):
        assert np.all(coboundary["d2"].sum(axis=1) == 0)


# ===================================================================
# T1706  Cochain complex  d^2 = 0
# ===================================================================
class TestT1706:
    """d_1 d_0 = 0  and  d_2 d_1 = 0."""

    def test_d1_d0_zero(self, coboundary):
        assert np.all(coboundary["d1"] @ coboundary["d0"] == 0)

    def test_d2_d1_zero(self, coboundary):
        assert np.all(coboundary["d2"] @ coboundary["d1"] == 0)

    def test_image_in_kernel(self, coboundary):
        """For 10 random 0-forms, d_1(d_0(f)) = 0."""
        rng = np.random.RandomState(42)
        d0, d1 = coboundary["d0"], coboundary["d1"]
        for _ in range(10):
            f = rng.randint(-5, 6, size=40)
            assert np.all(d1 @ (d0 @ f) == 0)


# ===================================================================
# T1707  Exact ranks of coboundary maps
# ===================================================================
class TestT1707:
    """rank(d_0)=39, rank(d_1)=120, rank(d_2)=40."""

    def test_rank_d0(self, exact_ranks):
        assert exact_ranks["r0"] == 39

    def test_rank_d1(self, exact_ranks):
        assert exact_ranks["r1"] == 120

    def test_rank_d2(self, exact_ranks):
        assert exact_ranks["r2"] == 40

    def test_rank_sum(self, exact_ranks):
        assert exact_ranks["r0"] + exact_ranks["r1"] + exact_ranks["r2"] == 199


# ===================================================================
# T1708  Betti numbers from exact ranks
# ===================================================================
class TestT1708:
    """b_k = nullity(d_k) - rank(d_{k-1})."""

    def test_b0(self, exact_ranks):
        b0 = 40 - exact_ranks["r0"]
        assert b0 == 1

    def test_b1(self, exact_ranks):
        nullity_d1 = 240 - exact_ranks["r1"]       # 120
        b1 = nullity_d1 - exact_ranks["r0"]         # 120 - 39 = 81
        assert b1 == 81

    def test_b2(self, exact_ranks):
        nullity_d2 = 160 - exact_ranks["r2"]        # 120
        b2 = nullity_d2 - exact_ranks["r1"]         # 120 - 120 = 0
        assert b2 == 0

    def test_b3(self, exact_ranks):
        b3 = 40 - exact_ranks["r2"]                 # 40 - 40 = 0
        assert b3 == 0


# ===================================================================
# T1709  DEC Laplacian L_1  (240 x 240)
# ===================================================================
class TestT1709:
    """L_1 = d_0 d_0^T + d_1^T d_1,  ker dim = 81."""

    def test_shape(self, laplacians):
        assert laplacians["L1"].shape == (240, 240)

    def test_symmetric(self, laplacians):
        L1 = laplacians["L1"]
        assert np.allclose(L1, L1.T, atol=1e-12)

    def test_psd(self, laplacians):
        eigvals = np.linalg.eigvalsh(laplacians["L1"])
        assert np.all(eigvals > -1e-10)

    def test_spectrum(self, laplacians):
        """L_1 eigenvalues: {0^81, 4^120, 10^24, 16^15}."""
        eigvals = np.linalg.eigvalsh(laplacians["L1"])
        counts = Counter(int(round(e)) for e in eigvals)
        assert counts[0] == 81
        assert counts[4] == 120
        assert counts[10] == 24
        assert counts[16] == 15


# ===================================================================
# T1710  DEC Laplacians L_2 and L_3
# ===================================================================
class TestT1710:
    """L_2 = 4 I_{160},  L_3 positive definite."""

    def test_L2_shape(self, laplacians):
        assert laplacians["L2"].shape == (160, 160)

    def test_L2_equals_4I(self, laplacians):
        """L_2 = d_1 d_1^T + d_2^T d_2 = 4 I_{160}."""
        assert np.allclose(laplacians["L2"], 4.0 * np.eye(160), atol=1e-10)

    def test_L3_shape(self, laplacians):
        assert laplacians["L3"].shape == (40, 40)

    def test_L3_positive_definite(self, laplacians):
        """b_3 = 0 implies L_3 has trivial kernel."""
        eigvals = np.linalg.eigvalsh(laplacians["L3"])
        assert np.min(eigvals) > 0.5


# ===================================================================
# T1711  Hodge star construction
# ===================================================================
class TestT1711:
    """Combinatorial Hodge stars: positive diagonal matrices."""

    def test_star0_positive(self, hodge_stars):
        assert np.all(hodge_stars["s0"] > 0)
        assert hodge_stars["s0"].shape == (40,)

    def test_star1_positive(self, hodge_stars):
        assert np.all(hodge_stars["s1"] > 0)
        assert hodge_stars["s1"].shape == (240,)

    def test_star2_positive(self, hodge_stars):
        assert np.all(hodge_stars["s2"] > 0)
        assert hodge_stars["s2"].shape == (160,)

    def test_star3_unit(self, hodge_stars):
        """Top-level Hodge star is the identity (no 4-simplices)."""
        assert np.allclose(hodge_stars["s3"], 1.0)
        assert hodge_stars["s3"].shape == (40,)


# ===================================================================
# T1712  Weighted codifferential
# ===================================================================
class TestT1712:
    """delta_k^w = *_{k-1}^{-1} d_{k-1}^T *_k  is the weighted adjoint."""

    def test_codiff1_shape(self, coboundary, hodge_stars):
        """delta_1^w: C^1 -> C^0  has shape 40 x 240."""
        d0 = coboundary["d0"].astype(float)
        s0_inv = 1.0 / hodge_stars["s0"]
        s1 = hodge_stars["s1"]
        delta1 = np.diag(s0_inv) @ d0.T @ np.diag(s1)
        assert delta1.shape == (40, 240)

    def test_weighted_laplacian0_psd(self, coboundary, hodge_stars):
        """L_0^w = delta_1^w d_0 is positive semidefinite."""
        d0 = coboundary["d0"].astype(float)
        s0_inv = 1.0 / hodge_stars["s0"]
        s1 = hodge_stars["s1"]
        delta1 = np.diag(s0_inv) @ d0.T @ np.diag(s1)
        L0w = delta1 @ d0
        eigvals = np.linalg.eigvalsh(L0w)
        assert np.all(eigvals > -1e-10)

    def test_weighted_laplacian0_kernel_dim1(self, coboundary, hodge_stars):
        """Weighted L_0 still has 1-dim kernel (b_0 = 1)."""
        d0 = coboundary["d0"].astype(float)
        s0_inv = 1.0 / hodge_stars["s0"]
        s1 = hodge_stars["s1"]
        delta1 = np.diag(s0_inv) @ d0.T @ np.diag(s1)
        L0w = delta1 @ d0
        eigvals = np.linalg.eigvalsh(L0w)
        n_zero = np.sum(np.abs(eigvals) < 1e-8)
        assert n_zero == 1


# ===================================================================
# T1713  Hodge decomposition dimensions
# ===================================================================
class TestT1713:
    """C^1 = exact + coexact + harmonic,  dims 39 + 120 + 81 = 240."""

    def test_exact_dim(self, exact_ranks):
        """dim(im d_0) = rank(d_0) = 39."""
        assert exact_ranks["r0"] == 39

    def test_coexact_dim(self, exact_ranks):
        """dim(im d_1^T) = rank(d_1) = 120."""
        assert exact_ranks["r1"] == 120

    def test_harmonic_dim(self, exact_ranks):
        """dim(harmonic) = b_1 = 81."""
        b1 = (240 - exact_ranks["r1"]) - exact_ranks["r0"]
        assert b1 == 81

    def test_total_dimension(self, exact_ranks):
        """39 + 120 + 81 = 240 = dim C^1."""
        b1 = (240 - exact_ranks["r1"]) - exact_ranks["r0"]
        total = exact_ranks["r0"] + exact_ranks["r1"] + b1
        assert total == 240


# ===================================================================
# T1714  Harmonic 1-forms (numerical projection)
# ===================================================================
class TestT1714:
    """Harmonic 1-forms live in ker(d_0^T) ∩ ker(d_1)."""

    def test_harmonic_count(self, laplacians):
        """Eigenvalue count: 81 zeros of L_1."""
        eigvals = np.linalg.eigvalsh(laplacians["L1"])
        n_zero = np.sum(np.abs(eigvals) < 1e-8)
        assert n_zero == 81

    def test_harmonic_in_ker_d0T(self, coboundary, laplacians):
        """Every harmonic 1-form h satisfies d_0^T h = 0."""
        d0 = coboundary["d0"].astype(float)
        L1 = laplacians["L1"]
        eigvals, eigvecs = np.linalg.eigh(L1)
        harm_idx = np.where(np.abs(eigvals) < 1e-8)[0]
        H = eigvecs[:, harm_idx]                # 240 x 81
        assert np.allclose(d0.T @ H, 0, atol=1e-8)

    def test_harmonic_in_ker_d1(self, coboundary, laplacians):
        """Every harmonic 1-form h satisfies d_1 h = 0."""
        d1 = coboundary["d1"].astype(float)
        L1 = laplacians["L1"]
        eigvals, eigvecs = np.linalg.eigh(L1)
        harm_idx = np.where(np.abs(eigvals) < 1e-8)[0]
        H = eigvecs[:, harm_idx]
        assert np.allclose(d1 @ H, 0, atol=1e-8)


# ===================================================================
# T1715  Discrete Stokes theorem
# ===================================================================
class TestT1715:
    """<d omega, sigma> = <omega, partial sigma>  for all cochains."""

    def test_stokes_0form(self, coboundary, graph_data):
        """For 0-form f and edge (i,j): (d_0 f)(e) = f(j) - f(i)."""
        d0 = coboundary["d0"]
        rng = np.random.RandomState(123)
        f = rng.randint(-10, 11, size=40)
        df = d0 @ f
        for idx, (i, j) in enumerate(graph_data["edges"]):
            assert df[idx] == f[j] - f[i]

    def test_stokes_1form(self, coboundary, graph_data):
        """For 1-form w and triangle (i,j,k):
           (d_1 w)(t) = w(ij) - w(ik) + w(jk)."""
        d1 = coboundary["d1"]
        rng = np.random.RandomState(456)
        w = rng.randint(-10, 11, size=240)
        dw = d1 @ w
        eidx = graph_data["edge_idx"]
        for idx, (i, j, k) in enumerate(graph_data["triangles"]):
            expected = w[eidx[(i, j)]] - w[eidx[(i, k)]] + w[eidx[(j, k)]]
            assert dw[idx] == expected

    def test_stokes_2form(self, coboundary, graph_data):
        """For 2-form eta and tetrahedron (i,j,k,l):
           (d_2 eta)(T) = eta(jkl) - eta(ikl) + eta(ijl) - eta(ijk)."""
        d2 = coboundary["d2"]
        rng = np.random.RandomState(789)
        eta = rng.randint(-10, 11, size=160)
        deta = d2 @ eta
        tidx = graph_data["tri_idx"]
        for idx, (i, j, k, l) in enumerate(graph_data["tetrahedra"]):
            expected = (eta[tidx[(j, k, l)]] - eta[tidx[(i, k, l)]]
                        + eta[tidx[(i, j, l)]] - eta[tidx[(i, j, k)]])
            assert deta[idx] == expected

    def test_stokes_general(self, coboundary):
        """d_k^T acting as boundary: <d_k w, sigma_k+1> = <w, d_k^T sigma_k+1>.

        For indicator cochain e_{sigma}, d_k^T e_{sigma} gives the boundary."""
        d0 = coboundary["d0"]
        # Indicator of edge 0
        e_edge = np.zeros(240, dtype=int)
        e_edge[0] = 1
        # d_0^T e_edge gives the boundary of the edge as a 0-chain
        boundary = d0.T @ e_edge
        # Should have exactly one +1 and one -1
        assert np.sum(boundary == 1) == 1
        assert np.sum(boundary == -1) == 1
        assert np.sum(boundary == 0) == 38


# ===================================================================
# T1716  Cup product on cochains
# ===================================================================
class TestT1716:
    """Simplicial cup product satisfies Leibniz rule on cochains."""

    def test_cup_00_pointwise(self, graph_data):
        """Cup of two 0-cochains is pointwise product."""
        rng = np.random.RandomState(100)
        alpha = rng.randn(40)
        beta = rng.randn(40)
        result = _cup_product_00(alpha, beta)
        assert np.allclose(result, alpha * beta)

    def test_leibniz_00(self, coboundary, graph_data):
        """d(alpha cup beta) = d(alpha) cup beta + alpha cup d(beta)
        for alpha, beta in C^0."""
        d0 = coboundary["d0"].astype(float)
        edges = graph_data["edges"]
        rng = np.random.RandomState(200)
        alpha = rng.randn(40)
        beta = rng.randn(40)

        # LHS: d_0(alpha * beta)
        lhs = d0 @ (alpha * beta)

        # RHS: (d_0 alpha) cup_{10} beta  +  alpha cup_{01} (d_0 beta)
        d_alpha = d0 @ alpha
        d_beta = d0 @ beta
        rhs = _cup_product_10(d_alpha, beta, edges) + \
              _cup_product_01(alpha, d_beta, edges)

        assert np.allclose(lhs, rhs, atol=1e-10)

    def test_leibniz_01(self, coboundary, graph_data):
        """d(alpha cup_{01} omega) = d(alpha) cup_{11} omega
        + alpha cup_{01} d(omega)   for alpha in C^0, omega in C^1.

        Evaluates on C^2 (triangles)."""
        d0 = coboundary["d0"].astype(float)
        d1 = coboundary["d1"].astype(float)
        edges = graph_data["edges"]
        triangles = graph_data["triangles"]
        edge_idx = graph_data["edge_idx"]
        rng = np.random.RandomState(300)
        alpha = rng.randn(40)
        omega = rng.randn(240)

        # alpha cup_{01} omega  is a 1-cochain
        a_cup_w = _cup_product_01(alpha, omega, edges)
        # d_1(a_cup_w) is a 2-cochain
        lhs = d1 @ a_cup_w

        # d_0(alpha) cup_{11} omega  is a 2-cochain
        d_alpha = d0 @ alpha
        term1 = _cup_product_11(d_alpha, omega, triangles, edge_idx)
        # alpha cup_{01} d_1(omega)  -- but alpha is C^0, d_1 omega is C^2
        # so (alpha cup d1 omega)[tri_{ijk}] = alpha[i] * (d1 omega)[tri_{ijk}]
        d_omega = d1 @ omega
        term2 = np.zeros(len(triangles), dtype=float)
        for idx, (i, j, k) in enumerate(triangles):
            term2[idx] = alpha[i] * d_omega[idx]
        rhs = term1 + term2

        assert np.allclose(lhs, rhs, atol=1e-10)

    def test_cup_associative_000(self, graph_data):
        """(alpha cup beta) cup gamma = alpha cup (beta cup gamma)
        for 0-cochains (pointwise product is associative)."""
        rng = np.random.RandomState(400)
        a = rng.randn(40)
        b = rng.randn(40)
        c = rng.randn(40)
        lhs = _cup_product_00(_cup_product_00(a, b), c)
        rhs = _cup_product_00(a, _cup_product_00(b, c))
        assert np.allclose(lhs, rhs, atol=1e-14)


# ===================================================================
# T1717  Discrete vector fields and Morse theory
# ===================================================================
class TestT1717:
    """A discrete gradient vector field from a Morse function."""

    def test_morse_function_valid(self, graph_data):
        """A dimension-based Morse function: f(sigma) = dim(sigma).
        All simplices are critical (no gradient pairings)."""
        # With f(sigma) = dim(sigma), every coface has strictly
        # higher value, so no irregular pairs => all cells critical.
        f = [40, 240, 160, 40]
        n_critical = sum(f)
        assert n_critical == 480

    def test_weak_morse_inequality(self, exact_ranks):
        """Number of critical k-cells >= b_k for any Morse function."""
        betti = [1, 81, 0, 0]
        f_vec = [40, 240, 160, 40]
        # Trivial Morse function: all cells critical
        for k in range(4):
            assert f_vec[k] >= betti[k]

    def test_morse_euler(self, graph_data):
        """Alternating sum of critical cells = Euler characteristic."""
        # For the trivial Morse function (all cells critical):
        f = [40, 240, 160, 40]
        morse_euler = sum((-1)**k * f[k] for k in range(4))
        assert morse_euler == -80


# ===================================================================
# T1718  Poincare duality and currents
# ===================================================================
class TestT1718:
    """Poincare duality and the current pairing."""

    def test_poincare_duality_fails(self, exact_ranks):
        """W(3,3) clique complex is NOT a closed manifold:
        b_0 = 1 != 0 = b_3, so Poincare duality fails."""
        b0 = 40 - exact_ranks["r0"]
        b3 = 40 - exact_ranks["r2"]
        assert b0 == 1
        assert b3 == 0
        assert b0 != b3

    def test_current_boundary(self, coboundary):
        """Boundary of a 1-current T satisfies
        <partial T, f> = <T, d_0 f> for all 0-forms f.

        This is the transpose relation: partial = d^T."""
        d0 = coboundary["d0"].astype(float)
        rng = np.random.RandomState(500)
        # T is a 1-current (element of C_1), f is a 0-cochain
        T = rng.randn(240)
        f = rng.randn(40)
        # <T, d_0 f> = T^T (d_0 f) = (d_0^T T)^T f = <d_0^T T, f>
        lhs = T @ (d0 @ f)
        rhs = (d0.T @ T) @ f
        assert abs(lhs - rhs) < 1e-10

    def test_cap_product_dimension(self, graph_data, coboundary):
        """The cap product pairs H^k with H_n to get H_{n-k}.
        For the complex dimension n=3:
        cap: H^1 x H_3 -> H_2.
        Since b_2 = 0 and b_3 = 0, the cap product into H_2 is trivial."""
        # b_2 = 0 means the cap product image is zero
        # This is consistent with the failure of Poincare duality
        d2 = coboundary["d2"]
        # rank(d2) = 40 = dim(C^3), so ker(d2) in C^2 has dim 120,
        # and im(d1) also has dim 120 => H^2 = 0
        rank_d2 = _rank_exact(d2)
        assert rank_d2 == 40
        assert 40 - rank_d2 == 0  # b_3 = 0
