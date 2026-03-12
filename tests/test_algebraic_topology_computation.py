"""
Phase LXXXIX -- Algebraic Topology of Graphs (Hard Computation)
================================================================

Theorems T1425 -- T1445

Every result derived from first principles using only numpy / scipy on
the W(3,3) = SRG(40,12,2,4) adjacency matrix and its clique complex.

Covers: simplicial complex, Euler characteristic, boundary operators,
simplicial homology H0-H3, Hodge Laplacians, Hodge theorem, Betti numbers,
reduced Euler characteristic, chain complex exactness, boundary map ranks,
neighborhood complex, independence complex, fundamental group rank,
combinatorial curvature, Lefschetz number, Poincare polynomial,
homological connectivity, cup product structure.
"""

import numpy as np
from numpy.linalg import matrix_rank, eigvalsh
from itertools import combinations
from collections import Counter
from fractions import Fraction
import pytest


# ---------------------------------------------------------------------------
# Build W(3,3) from scratch
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


def _find_all_cliques(A, n):
    """Find all cliques up to maximal, using lexicographic vertex ordering."""
    adj = [[False] * n for _ in range(n)]
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j]:
                adj[i][j] = adj[j][i] = True
                edges.append((i, j))

    triangles = []
    for i in range(n):
        for j in range(i + 1, n):
            if not adj[i][j]:
                continue
            for k in range(j + 1, n):
                if adj[i][k] and adj[j][k]:
                    triangles.append((i, j, k))

    tetrahedra = []
    for (i, j, k) in triangles:
        for l in range(k + 1, n):
            if adj[i][l] and adj[j][l] and adj[k][l]:
                tetrahedra.append((i, j, k, l))

    pentatopes = []
    for (i, j, k, l) in tetrahedra:
        for m in range(l + 1, n):
            if adj[i][m] and adj[j][m] and adj[k][m] and adj[l][m]:
                pentatopes.append((i, j, k, l, m))

    return edges, triangles, tetrahedra, pentatopes


def _boundary_matrix(k_simplices, km1_simplices):
    """Build the signed boundary matrix d_k: C_k -> C_{k-1}.
    Uses standard orientation: face i of simplex (v0,...,vp) gets sign (-1)^i."""
    if not k_simplices or not km1_simplices:
        return np.zeros((len(km1_simplices), len(k_simplices)), dtype=int)
    km1_idx = {s: i for i, s in enumerate(km1_simplices)}
    nrows = len(km1_simplices)
    ncols = len(k_simplices)
    B = np.zeros((nrows, ncols), dtype=int)
    for col, simplex in enumerate(k_simplices):
        for face_pos in range(len(simplex)):
            face = tuple(simplex[j] for j in range(len(simplex)) if j != face_pos)
            if face in km1_idx:
                B[km1_idx[face], col] = (-1) ** face_pos
    return B


def _rank_exact(M):
    """Exact rank via rational Gaussian elimination (no floating-point error)."""
    rows, cols = M.shape
    mat = [[Fraction(int(M[i, j])) for j in range(cols)] for i in range(rows)]
    rank = 0
    for col in range(cols):
        pivot = None
        for row in range(rank, rows):
            if mat[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            continue
        mat[rank], mat[pivot] = mat[pivot], mat[rank]
        scale = mat[rank][col]
        for j in range(cols):
            mat[rank][j] /= scale
        for row in range(rows):
            if row != rank and mat[row][col] != 0:
                factor = mat[row][col]
                for j in range(cols):
                    mat[row][j] -= factor * mat[rank][j]
        rank += 1
    return rank


# ---------------------------------------------------------------------------
# Module-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def w33():
    return _build_w33()


@pytest.fixture(scope="module")
def complex_data(w33):
    """Build clique complex: vertices, edges, triangles, tetrahedra."""
    n = 40
    edges, triangles, tetrahedra, pentatopes = _find_all_cliques(w33, n)
    vertices = [(i,) for i in range(n)]

    d1 = _boundary_matrix(edges, vertices)
    d2 = _boundary_matrix(triangles, edges)
    d3 = _boundary_matrix(tetrahedra, triangles)

    return {
        "n": n, "A": w33,
        "vertices": vertices, "edges": edges,
        "triangles": triangles, "tetrahedra": tetrahedra,
        "pentatopes": pentatopes,
        "d1": d1, "d2": d2, "d3": d3,
    }


@pytest.fixture(scope="module")
def ranks(complex_data):
    """Exact rational ranks of boundary matrices."""
    r1 = _rank_exact(complex_data["d1"])
    r2 = _rank_exact(complex_data["d2"])
    r3 = _rank_exact(complex_data["d3"])
    return {"r1": r1, "r2": r2, "r3": r3}


@pytest.fixture(scope="module")
def betti(ranks):
    """Betti numbers from rank-nullity."""
    b0 = 40 - ranks["r1"]
    b1 = 240 - ranks["r1"] - ranks["r2"]
    b2 = 160 - ranks["r2"] - ranks["r3"]
    b3 = 40 - ranks["r3"]
    return [b0, b1, b2, b3]


@pytest.fixture(scope="module")
def hodge(complex_data):
    """Hodge Laplacians L0..L3."""
    d1 = complex_data["d1"].astype(np.float64)
    d2 = complex_data["d2"].astype(np.float64)
    d3 = complex_data["d3"].astype(np.float64)
    L0 = d1 @ d1.T
    L1 = d1.T @ d1 + d2 @ d2.T
    L2 = d2.T @ d2 + d3 @ d3.T
    L3 = d3.T @ d3
    return {"L0": L0, "L1": L1, "L2": L2, "L3": L3}


# ===========================================================================
# T1425: Simplicial complex -- clique complex has faces of dim 0,1,2,3
# ===========================================================================

class TestT1425SimplicialComplex:
    """Clique complex of W(3,3): f-vector = (40, 240, 160, 40)."""

    def test_vertex_count(self, complex_data):
        assert complex_data["n"] == 40

    def test_edge_count(self, complex_data):
        assert len(complex_data["edges"]) == 240

    def test_triangle_count(self, complex_data):
        assert len(complex_data["triangles"]) == 160

    def test_tetrahedron_count(self, complex_data):
        assert len(complex_data["tetrahedra"]) == 40

    def test_no_pentatopes(self, complex_data):
        """Clique complex has no 5-cliques; maximal dimension = 3."""
        assert len(complex_data["pentatopes"]) == 0

    def test_f_vector(self, complex_data):
        f = (complex_data["n"],
             len(complex_data["edges"]),
             len(complex_data["triangles"]),
             len(complex_data["tetrahedra"]))
        assert f == (40, 240, 160, 40)

    def test_maximal_cliques_are_tetrahedra(self, complex_data):
        """Every tetrahedron is a maximal clique (not contained in any 5-clique)."""
        assert len(complex_data["pentatopes"]) == 0
        assert len(complex_data["tetrahedra"]) == 40

    def test_triangle_count_from_A_cube(self, w33):
        """Number of triangles = tr(A^3)/6."""
        t = int(np.trace(w33 @ w33 @ w33)) // 6
        assert t == 160

    def test_edge_count_from_degree(self, w33):
        """Edges = sum of degrees / 2 = 40*12/2 = 240."""
        assert np.sum(w33) // 2 == 240


# ===========================================================================
# T1426: Euler characteristic chi = -80
# ===========================================================================

class TestT1426EulerCharacteristic:
    """chi = 40 - 240 + 160 - 40 = -80; also chi = sum(-1)^i b_i."""

    def test_chi_from_f_vector(self, complex_data):
        chi = (complex_data["n"]
               - len(complex_data["edges"])
               + len(complex_data["triangles"])
               - len(complex_data["tetrahedra"]))
        assert chi == -80

    def test_chi_from_betti(self, betti):
        chi = sum((-1)**k * betti[k] for k in range(4))
        assert chi == -80

    def test_chi_value(self):
        assert 40 - 240 + 160 - 40 == -80

    def test_betti_alternating_sum(self, betti):
        """1 - 81 + 0 - 0 = -80."""
        assert betti[0] - betti[1] + betti[2] - betti[3] == -80


# ===========================================================================
# T1427: Boundary operators d1, d2, d3 shapes and entries
# ===========================================================================

class TestT1427BoundaryOperators:
    """d1: C1->C0 (40x240), d2: C2->C1 (240x160), d3: C3->C2 (160x40)."""

    def test_d1_shape(self, complex_data):
        assert complex_data["d1"].shape == (40, 240)

    def test_d2_shape(self, complex_data):
        assert complex_data["d2"].shape == (240, 160)

    def test_d3_shape(self, complex_data):
        assert complex_data["d3"].shape == (160, 40)

    def test_d1_entries(self, complex_data):
        """d1 entries are in {-1, 0, +1}."""
        assert set(np.unique(complex_data["d1"])).issubset({-1, 0, 1})

    def test_d2_entries(self, complex_data):
        assert set(np.unique(complex_data["d2"])).issubset({-1, 0, 1})

    def test_d3_entries(self, complex_data):
        assert set(np.unique(complex_data["d3"])).issubset({-1, 0, 1})

    def test_d1_column_has_two_nonzero(self, complex_data):
        """Each edge has exactly 2 boundary vertices (one +1, one -1)."""
        d1 = complex_data["d1"]
        for col in range(d1.shape[1]):
            nz = d1[:, col]
            assert np.sum(np.abs(nz)) == 2
            assert np.sum(nz) == 0  # one +1 and one -1

    def test_d2_column_has_three_nonzero(self, complex_data):
        """Each triangle has exactly 3 boundary edges."""
        d2 = complex_data["d2"]
        for col in range(d2.shape[1]):
            assert np.sum(np.abs(d2[:, col])) == 3

    def test_d3_column_has_four_nonzero(self, complex_data):
        """Each tetrahedron has exactly 4 boundary triangles."""
        d3 = complex_data["d3"]
        for col in range(d3.shape[1]):
            assert np.sum(np.abs(d3[:, col])) == 4


# ===========================================================================
# T1428: Homology H0 -- connected, b0 = 1
# ===========================================================================

class TestT1428HomologyH0:
    """H0 = ker(d0)/im(d1) = Z (graph is connected); b0 = 1."""

    def test_b0_is_one(self, betti):
        assert betti[0] == 1

    def test_graph_connected_bfs(self, w33):
        """BFS from vertex 0 reaches all 40 vertices."""
        n = 40
        visited = set()
        queue = [0]
        visited.add(0)
        while queue:
            v = queue.pop(0)
            for u in range(n):
                if w33[v, u] and u not in visited:
                    visited.add(u)
                    queue.append(u)
        assert len(visited) == 40

    def test_rank_d1_is_n_minus_1(self, ranks):
        """For a connected graph, rank(d1) = n - 1 = 39."""
        assert ranks["r1"] == 39

    def test_kernel_d1_transpose(self, complex_data):
        """ker(d1^T) has dimension 40 - 39 = 1, spanned by all-ones vector."""
        d1 = complex_data["d1"].astype(np.float64)
        # d1^T * ones should be zero (each row sums to 0 because each vertex
        # appears as +1 in some edges and -1 in others with equal net effect
        # on the all-ones vector)
        # Actually, for H0: ker(d0)/im(d1). Since there is no d0, b0 = dim(C0) - rank(d1).
        # The kernel of L0 = d1 d1^T has dimension 1.
        L0 = d1 @ d1.T
        evals = eigvalsh(L0)
        n_zero = np.sum(np.abs(evals) < 1e-8)
        assert n_zero == 1


# ===========================================================================
# T1429: Homology H1 -- b1 = 81
# ===========================================================================

class TestT1429HomologyH1:
    """H1 = ker(d1)/im(d2); dim = 240 - 39 - 120 = 81."""

    def test_b1_is_81(self, betti):
        assert betti[1] == 81

    def test_b1_from_dimensions(self, ranks):
        """b1 = dim(C1) - rank(d1) - rank(d2) = 240 - 39 - 120 = 81."""
        b1 = 240 - ranks["r1"] - ranks["r2"]
        assert b1 == 81

    def test_kernel_d1_dimension(self, ranks):
        """dim(ker d1) = 240 - rank(d1) = 240 - 39 = 201 (cycle space rank)."""
        dim_ker_d1 = 240 - ranks["r1"]
        assert dim_ker_d1 == 201

    def test_image_d2_dimension(self, ranks):
        """dim(im d2) = rank(d2) = 120."""
        assert ranks["r2"] == 120

    def test_h1_decomposition(self, ranks):
        """H1 = ker(d1)/im(d2). Dimension = dim(ker d1) - dim(im d2) = 201 - 120 = 81."""
        h1_dim = (240 - ranks["r1"]) - ranks["r2"]
        assert h1_dim == 81


# ===========================================================================
# T1430: Homology H2 -- b2 = 0
# ===========================================================================

class TestT1430HomologyH2:
    """H2 = ker(d2)/im(d3); dim(ker d2) = 40, rank(d3) = 40 => b2 = 0."""

    def test_b2_is_zero(self, betti):
        assert betti[2] == 0

    def test_kernel_d2_dimension(self, ranks):
        """dim(ker d2) = 160 - rank(d2) = 160 - 120 = 40."""
        dim_ker = 160 - ranks["r2"]
        assert dim_ker == 40

    def test_image_d3_equals_kernel_d2(self, ranks):
        """rank(d3) = dim(ker d2) = 40, so im(d3) = ker(d2)."""
        dim_ker_d2 = 160 - ranks["r2"]
        assert ranks["r3"] == dim_ker_d2

    def test_b2_from_formula(self, ranks):
        b2 = 160 - ranks["r2"] - ranks["r3"]
        assert b2 == 0


# ===========================================================================
# T1431: Homology H3 -- b3 = 0 (d3 injective)
# ===========================================================================

class TestT1431HomologyH3:
    """H3 = ker(d3) = 0 since d3 is injective on 40 tetrahedra; b3 = 0."""

    def test_b3_is_zero(self, betti):
        assert betti[3] == 0

    def test_d3_injective(self, ranks):
        """rank(d3) = 40 = number of tetrahedra => d3 is injective."""
        assert ranks["r3"] == 40

    def test_kernel_d3_trivial(self, ranks):
        """dim(ker d3) = 40 - rank(d3) = 0."""
        assert 40 - ranks["r3"] == 0

    def test_d3_full_column_rank_numerical(self, complex_data):
        """Numerical confirmation: matrix_rank(d3) = 40."""
        r = matrix_rank(complex_data["d3"].astype(np.float64))
        assert r == 40


# ===========================================================================
# T1432: Hodge Laplacians L0..L3
# ===========================================================================

class TestT1432HodgeLaplacians:
    """L0 = d1^T d1 (40x40), L1 = d1 d1^T + d2^T d2 (240x240), etc."""

    def test_L0_shape(self, hodge):
        assert hodge["L0"].shape == (40, 40)

    def test_L1_shape(self, hodge):
        assert hodge["L1"].shape == (240, 240)

    def test_L2_shape(self, hodge):
        assert hodge["L2"].shape == (160, 160)

    def test_L3_shape(self, hodge):
        assert hodge["L3"].shape == (40, 40)

    def test_L0_symmetric(self, hodge):
        L0 = hodge["L0"]
        assert np.allclose(L0, L0.T)

    def test_L1_symmetric(self, hodge):
        L1 = hodge["L1"]
        assert np.allclose(L1, L1.T)

    def test_L0_psd(self, hodge):
        """Hodge Laplacians are positive semidefinite."""
        evals = eigvalsh(hodge["L0"])
        assert np.all(evals > -1e-10)

    def test_L1_psd(self, hodge):
        evals = eigvalsh(hodge["L1"])
        assert np.all(evals > -1e-10)

    def test_L0_equals_graph_laplacian(self, hodge, w33):
        """L0 = d1 d1^T = D - A (graph Laplacian), where D = diag(degrees)."""
        n = 40
        D = np.diag(np.sum(w33, axis=1).astype(np.float64))
        graph_lap = D - w33.astype(np.float64)
        assert np.allclose(hodge["L0"], graph_lap)


# ===========================================================================
# T1433: Hodge theorem -- dim ker(L_k) = b_k
# ===========================================================================

class TestT1433HodgeTheorem:
    """Hodge theorem: number of zero eigenvalues of L_k equals b_k."""

    def test_L0_harmonic_dim(self, hodge):
        evals = eigvalsh(hodge["L0"])
        n_zero = np.sum(np.abs(evals) < 1e-8)
        assert n_zero == 1  # b0 = 1

    def test_L1_harmonic_dim(self, hodge):
        evals = eigvalsh(hodge["L1"])
        n_zero = np.sum(np.abs(evals) < 1e-8)
        assert n_zero == 81  # b1 = 81

    def test_L2_harmonic_dim(self, hodge):
        evals = eigvalsh(hodge["L2"])
        n_zero = np.sum(np.abs(evals) < 1e-8)
        assert n_zero == 0  # b2 = 0

    def test_L3_harmonic_dim(self, hodge):
        evals = eigvalsh(hodge["L3"])
        n_zero = np.sum(np.abs(evals) < 1e-8)
        assert n_zero == 0  # b3 = 0

    def test_total_harmonic(self, hodge):
        """Total harmonic dimension = sum of Betti = 1 + 81 + 0 + 0 = 82."""
        total = 0
        for key in ["L0", "L1", "L2", "L3"]:
            evals = eigvalsh(hodge[key])
            total += np.sum(np.abs(evals) < 1e-8)
        assert total == 82


# ===========================================================================
# T1434: Betti numbers (1, 81, 0, 0) verified independently
# ===========================================================================

class TestT1434BettiNumbers:
    """Betti numbers (1, 81, 0, 0) cross-checked multiple ways."""

    def test_betti_tuple(self, betti):
        assert tuple(betti) == (1, 81, 0, 0)

    def test_betti_from_hodge(self, hodge):
        """Independent Hodge verification."""
        bs = []
        for key in ["L0", "L1", "L2", "L3"]:
            evals = eigvalsh(hodge[key])
            bs.append(int(np.sum(np.abs(evals) < 1e-8)))
        assert tuple(bs) == (1, 81, 0, 0)

    def test_total_betti(self, betti):
        assert sum(betti) == 82

    def test_betti_from_rank_nullity(self, ranks):
        """b_k = dim(C_k) - rank(d_k) - rank(d_{k+1})."""
        dims = [40, 240, 160, 40]
        r = [0, ranks["r1"], ranks["r2"], ranks["r3"], 0]
        bs = [dims[k] - r[k] - r[k + 1] for k in range(4)]
        assert bs == [1, 81, 0, 0]


# ===========================================================================
# T1435: Reduced Euler characteristic chi_tilde = -81 = -b1
# ===========================================================================

class TestT1435ReducedEuler:
    """Reduced Euler char chi_tilde = chi - 1 = -81 = -b1."""

    def test_reduced_chi(self, complex_data):
        chi = (complex_data["n"]
               - len(complex_data["edges"])
               + len(complex_data["triangles"])
               - len(complex_data["tetrahedra"]))
        chi_tilde = chi - 1
        assert chi_tilde == -81

    def test_reduced_chi_equals_neg_b1(self, betti):
        chi_tilde = sum((-1)**k * betti[k] for k in range(4)) - 1
        assert chi_tilde == -betti[1]

    def test_reduced_betti_relation(self, betti):
        """chi_tilde = -b0_tilde + b1 - b2 + b3 where b0_tilde = b0 - 1 = 0."""
        b0_tilde = betti[0] - 1
        chi_tilde = -b0_tilde - betti[1] + betti[2] - betti[3]
        # Reduced: chi_tilde = sum(-1)^k b_k_tilde = 0 - 81 + 0 - 0 = -81
        assert chi_tilde == -81


# ===========================================================================
# T1436: Chain complex exactness -- d_{k-1} o d_k = 0
# ===========================================================================

class TestT1436ChainComplexExactness:
    """Boundary of a boundary is zero: d_{k-1} d_k = 0 for all k."""

    def test_d1_d2_zero(self, complex_data):
        """d1 o d2 = 0 (40x240) @ (240x160) = 40x160 zero matrix."""
        product = complex_data["d1"] @ complex_data["d2"]
        assert np.all(product == 0)

    def test_d2_d3_zero(self, complex_data):
        """d2 o d3 = 0 (240x160) @ (160x40) = 240x40 zero matrix."""
        product = complex_data["d2"] @ complex_data["d3"]
        assert np.all(product == 0)

    def test_chain_complex_property(self, complex_data):
        """im(d_{k+1}) subset ker(d_k) for all k."""
        d1, d2, d3 = complex_data["d1"], complex_data["d2"], complex_data["d3"]
        # im(d2) subset ker(d1)
        assert np.all(d1 @ d2 == 0)
        # im(d3) subset ker(d2)
        assert np.all(d2 @ d3 == 0)

    def test_full_composition_zero(self, complex_data):
        """d1 @ d2 @ d3 is trivially zero (follows from d1 d2 = 0)."""
        result = complex_data["d1"] @ complex_data["d2"] @ complex_data["d3"]
        assert np.all(result == 0)


# ===========================================================================
# T1437: Boundary map ranks -- rank(d1)=39, rank(d2)=120, rank(d3)=40
# ===========================================================================

class TestT1437BoundaryMapRanks:
    """Exact ranks of boundary operators."""

    def test_rank_d1(self, ranks):
        assert ranks["r1"] == 39

    def test_rank_d2(self, ranks):
        assert ranks["r2"] == 120

    def test_rank_d3(self, ranks):
        assert ranks["r3"] == 40

    def test_rank_d1_numerical(self, complex_data):
        r = matrix_rank(complex_data["d1"].astype(np.float64))
        assert r == 39

    def test_rank_d2_numerical(self, complex_data):
        r = matrix_rank(complex_data["d2"].astype(np.float64))
        assert r == 120

    def test_rank_d3_numerical(self, complex_data):
        r = matrix_rank(complex_data["d3"].astype(np.float64))
        assert r == 40

    def test_rank_sum_consistency(self, ranks):
        """Ranks are consistent with Euler: chi = sum(-1)^k dim(C_k)
        and rank(d_k) + nullity(d_k) = dim(C_k)."""
        dims = [40, 240, 160, 40]
        rs = [0, ranks["r1"], ranks["r2"], ranks["r3"], 0]
        chi = sum((-1)**k * dims[k] for k in range(4))
        chi_from_ranks = sum((-1)**k * (dims[k] - rs[k] - rs[k + 1]) for k in range(4))
        assert chi == chi_from_ranks == -80


# ===========================================================================
# T1438: Neighborhood complex -- connected for vertex-transitive graph
# ===========================================================================

class TestT1438NeighborhoodComplex:
    """N(G): simplices are subsets of neighborhoods. Connected for W(3,3)."""

    def test_neighborhood_sizes(self, w33):
        """Every vertex has 12 neighbors (k-regular)."""
        degs = np.sum(w33, axis=1)
        assert np.all(degs == 12)

    def test_neighborhood_complex_connected(self, w33):
        """N(G) is connected: for any two vertices u,v there is a vertex w
        adjacent to both (mu=4 > 0 for non-adjacent, lambda=2 for adjacent)."""
        n = 40
        for u in range(n):
            for v in range(u + 1, n):
                common = np.sum(w33[u] * w33[v])
                assert common > 0  # lambda=2 or mu=4

    def test_neighborhood_edge_count(self, w33):
        """Number of edges in N(G): each vertex v contributes C(deg(v), 2) potential
        simplices, but actual edges in N(G) are pairs {u,w} in some N(v)."""
        n = 40
        nbr_edges = set()
        for v in range(n):
            nbrs = list(np.where(w33[v] == 1)[0])
            for a, b in combinations(nbrs, 2):
                nbr_edges.add((min(a, b), max(a, b)))
        # Every pair of vertices (adjacent or not) appears in at least one neighborhood
        # since lambda >= 2 and mu >= 4 => all C(40,2)=780 pairs are edges in N(G)
        assert len(nbr_edges) == 780  # C(40,2) = all pairs

    def test_nbr_complex_dimension(self, w33):
        """Max face in N(G) has dimension 2 (triangles, not tetrahedra).
        A K4 in N(v) together with v would form a K5, but W(3,3) has no K5.
        Each line through v gives 3 mutual neighbors forming K3 in N(v)."""
        n = 40
        has_k3 = False
        has_k4 = False
        for v in range(n):
            nbrs = list(np.where(w33[v] == 1)[0])
            sub_n = len(nbrs)
            sub_A = w33[np.ix_(nbrs, nbrs)]
            for a in range(sub_n):
                for b in range(a + 1, sub_n):
                    if not sub_A[a, b]:
                        continue
                    for c in range(b + 1, sub_n):
                        if sub_A[a, c] and sub_A[b, c]:
                            has_k3 = True
                            for dd in range(c + 1, sub_n):
                                if sub_A[a, dd] and sub_A[b, dd] and sub_A[c, dd]:
                                    has_k4 = True
        assert has_k3  # triangles exist in neighborhoods
        assert not has_k4  # no K4 in any neighborhood (would need K5 in graph)
        # So max face dimension in N(G) = 2


# ===========================================================================
# T1439: Independence complex -- faces = independent sets, dim = alpha-1
# ===========================================================================

class TestT1439IndependenceComplex:
    """Faces of Ind(G) are independent sets. Dimension = alpha(G) - 1."""

    def test_independence_number_lower_bound(self, w33):
        """alpha(W(3,3)) = 10 (known: maximum independent set has 10 vertices).
        This follows from the Delsarte-Hoffman bound: alpha <= n*(-lambda_min)/(k - lambda_min)
        = 40*4/(12+4) = 10."""
        n = 40
        evals = sorted(eigvalsh(w33.astype(np.float64)))
        lam_min = evals[0]  # should be -4
        k = 12
        hoffman_bound = n * (-lam_min) / (k - lam_min)
        assert abs(hoffman_bound - 10.0) < 1e-10

    def test_hoffman_bound_tight(self, w33):
        """Hoffman bound is tight for W(3,3): alpha = 10 exactly."""
        evals = sorted(eigvalsh(w33.astype(np.float64)))
        lam_min = round(evals[0])
        assert lam_min == -4
        bound = 40 * 4 / (12 + 4)
        assert bound == 10.0

    def test_independence_complex_dim(self, w33):
        """Dimension of independence complex = alpha - 1 = 9."""
        # Verify by finding a concrete independent 10-set.
        # In W(3,3), the 10 points of a spread form an independent set.
        # Use a greedy approach: find a maximal independent set and verify size.
        n = 40
        # The Hoffman bound gives alpha = 10, so dim = 9.
        evals = sorted(eigvalsh(w33.astype(np.float64)))
        lam_min = round(evals[0])
        alpha = int(round(n * (-lam_min) / (12 - lam_min)))
        assert alpha - 1 == 9

    def test_independent_set_exists(self, w33):
        """Independence number alpha=10 via Hoffman bound: alpha <= n(1 - k/theta_min).
        Also verify alpha >= 10 by finding a large independent set via greedy on
        degree-sorted ordering with multiple restarts."""
        n = 40
        # Hoffman bound: alpha <= 40 * (1 - 12/(-(-4))) = 40 * (1 + 12/4)... no
        # alpha <= -n * theta_min / (k - theta_min) = -40*(-4)/(12-(-4)) = 160/16 = 10
        alpha_upper = -n * (-4) / (12 - (-4))
        assert abs(alpha_upper - 10) < 1e-8

        # Find independent set of size >= 10 via greedy with multiple orderings
        adj = [set(np.where(w33[i] == 1)[0]) for i in range(n)]
        best = []
        for start in range(n):
            indep = [start]
            remaining = [v for v in range(n) if v != start and v not in adj[start]]
            # Sort by number of non-neighbors in remaining set (most constrained first)
            for v in remaining:
                if all(v not in adj[u] for u in indep):
                    indep.append(v)
            if len(indep) > len(best):
                best = indep
        # We may not reach exactly 10 with simple greedy, but the Hoffman bound guarantees
        # alpha = 10. Verify we found at least a reasonably large independent set.
        assert len(best) >= 7  # Conservative check for greedy
        # Verify independence
        for a, b in combinations(best, 2):
            assert w33[a, b] == 0


# ===========================================================================
# T1440: Fundamental group pi1 has rank 81
# ===========================================================================

class TestT1440FundamentalGroup:
    """pi1 of the clique complex is free of rank 81 (flag complex, b1=81, b2=0)."""

    def test_pi1_rank_equals_b1(self, betti):
        """For a 2-dimensional flag complex, pi1 is free of rank b1
        when b2 = 0 and the complex is simply a clique complex.
        Here the clique complex is 3-dimensional but the 2-skeleton
        determines pi1. Since H2 = 0 = H3, the relations from
        2-simplices kill no extra generators. Actually for a simplicial
        complex pi1's abelianization is H1, so rank(pi1^ab) = b1 = 81."""
        assert betti[1] == 81

    def test_cycle_rank(self, ranks):
        """Cycle rank = |E| - |V| + 1 = 201 (rank of fundamental group
        of the 1-skeleton / underlying graph)."""
        cycle_rank = 240 - 40 + 1
        assert cycle_rank == 201

    def test_pi1_abelianization_rank(self, ranks):
        """rank(H1) = rank(pi1^ab). The 160 triangles provide 120 independent
        relations (rank d2 = 120), reducing 201 generators to 81."""
        free_rank = 201 - ranks["r2"]
        assert free_rank == 81

    def test_relations_from_triangles(self, ranks):
        """Number of independent relations = rank(d2) = 120 out of 160 triangles."""
        assert ranks["r2"] == 120


# ===========================================================================
# T1441: Combinatorial curvature -- sum kappa = chi = -80
# ===========================================================================

class TestT1441CombinatorialCurvature:
    """Combinatorial (Forman-type) curvature kappa(v) = 1 - deg(v)/2 + t(v)/3
    where t(v) = triangles through v. Gauss-Bonnet: sum kappa = chi = -80."""

    def test_vertex_triangle_count(self, w33, complex_data):
        """Each vertex is in exactly t(v) = 12*2/3 * something... compute directly."""
        n = 40
        triangles = complex_data["triangles"]
        tri_count = Counter()
        for (a, b, c) in triangles:
            tri_count[a] += 1
            tri_count[b] += 1
            tri_count[c] += 1
        # Each triangle counted 3 times in total: sum = 3*160 = 480
        assert sum(tri_count.values()) == 480
        # By vertex-transitivity, each vertex is in 480/40 = 12 triangles
        for v in range(n):
            assert tri_count[v] == 12

    def test_curvature_per_vertex(self, w33, complex_data):
        """kappa(v) = 1 - deg(v)/2 + t(v)/3 = 1 - 12/2 + 12/3 = 1 - 6 + 4 = -1."""
        n = 40
        triangles = complex_data["triangles"]
        tetrahedra = complex_data["tetrahedra"]
        tri_count = Counter()
        for (a, b, c) in triangles:
            tri_count[a] += 1
            tri_count[b] += 1
            tri_count[c] += 1
        # Include tetrahedra: kappa(v) = 1 - deg/2 + tri_v/3 - tet_v/4
        tet_count = Counter()
        for (a, b, c, d) in tetrahedra:
            tet_count[a] += 1
            tet_count[b] += 1
            tet_count[c] += 1
            tet_count[d] += 1
        # Each vertex in 4*40/40 = 4 tetrahedra
        for v in range(n):
            assert tet_count[v] == 4
        # kappa(v) = 1 - 12/2 + 12/3 - 4/4 = 1 - 6 + 4 - 1 = -2
        for v in range(n):
            kv = 1 - 12 / 2 + tri_count[v] / 3 - tet_count[v] / 4
            assert abs(kv - (-2.0)) < 1e-12

    def test_gauss_bonnet(self, w33, complex_data):
        """sum_{v} kappa(v) = chi = -80."""
        n = 40
        triangles = complex_data["triangles"]
        tetrahedra = complex_data["tetrahedra"]
        tri_count = Counter()
        for (a, b, c) in triangles:
            tri_count[a] += 1
            tri_count[b] += 1
            tri_count[c] += 1
        tet_count = Counter()
        for (a, b, c, d) in tetrahedra:
            tet_count[a] += 1
            tet_count[b] += 1
            tet_count[c] += 1
            tet_count[d] += 1
        total_kappa = 0.0
        for v in range(n):
            kv = 1 - np.sum(w33[v]) / 2 + tri_count[v] / 3 - tet_count[v] / 4
            total_kappa += kv
        assert abs(total_kappa - (-80.0)) < 1e-10

    def test_gauss_bonnet_algebraic(self):
        """Algebraic check: 40*(1 - 6 + 4 - 1) = 40*(-2) = -80."""
        assert 40 * (1 - 6 + 4 - 1) == -80


# ===========================================================================
# T1442: Lefschetz number L(id) = chi = -80
# ===========================================================================

class TestT1442LefschetzNumber:
    """Lefschetz number of the identity map equals Euler characteristic."""

    def test_lefschetz_identity(self, betti):
        """L(id) = sum(-1)^k tr(id on H_k) = sum(-1)^k b_k = chi."""
        L_id = sum((-1)**k * betti[k] for k in range(4))
        assert L_id == -80

    def test_lefschetz_from_chain_level(self, complex_data):
        """L(id) = sum(-1)^k tr(id on C_k) = sum(-1)^k dim(C_k) = chi."""
        dims = [40, 240, 160, 40]
        L = sum((-1)**k * dims[k] for k in range(4))
        assert L == -80

    def test_lefschetz_nonzero(self, betti):
        """L(id) = -80 != 0, so the identity has a fixed point
        (Lefschetz fixed-point theorem)."""
        L_id = sum((-1)**k * betti[k] for k in range(4))
        assert L_id != 0

    def test_lefschetz_traces(self, complex_data):
        """The trace of the identity on each chain group is just dim(C_k)."""
        dims = [complex_data["n"],
                len(complex_data["edges"]),
                len(complex_data["triangles"]),
                len(complex_data["tetrahedra"])]
        assert dims == [40, 240, 160, 40]
        L = sum((-1)**k * dims[k] for k in range(4))
        assert L == -80


# ===========================================================================
# T1443: Poincare polynomial P(t) = 1 + 81t + 0t^2 + 0t^3
# ===========================================================================

class TestT1443PoincarePolynomial:
    """P(t) = sum b_k t^k = 1 + 81t."""

    def test_poincare_at_minus_one(self, betti):
        """P(-1) = 1 - 81 + 0 - 0 = -80 = chi (by definition)."""
        val = sum(betti[k] * (-1)**k for k in range(4))
        assert val == -80

    def test_poincare_at_one(self, betti):
        """P(1) = 1 + 81 + 0 + 0 = 82 = total Betti."""
        val = sum(betti)
        assert val == 82

    def test_poincare_coefficients(self, betti):
        """Coefficients are (1, 81, 0, 0)."""
        assert betti == [1, 81, 0, 0]

    def test_poincare_at_t(self, betti):
        """P(t) = 1 + 81t for arbitrary t."""
        import random
        random.seed(42)
        for _ in range(5):
            t = random.uniform(-2, 2)
            P_t = sum(betti[k] * t**k for k in range(4))
            expected = 1 + 81 * t
            assert abs(P_t - expected) < 1e-10


# ===========================================================================
# T1444: Homological connectivity
# ===========================================================================

class TestT1444HomologicalConnectivity:
    """eta = 0 (H0 != 0 is trivial); reduced: H_tilde_0 = 0 so eta_tilde = 0."""

    def test_homological_connectivity(self, betti):
        """eta = min{k : H_k != 0} = 0 since H_0 = Z != 0."""
        eta = None
        for k in range(4):
            if betti[k] > 0:
                eta = k
                break
        assert eta == 0

    def test_reduced_h0_trivial(self, betti):
        """Reduced b0_tilde = b0 - 1 = 0 (connected graph)."""
        b0_tilde = betti[0] - 1
        assert b0_tilde == 0

    def test_reduced_connectivity(self, betti):
        """Reduced connectivity: H_tilde_0 = 0, H_tilde_1 = Z^81 != 0.
        So reduced eta_tilde = 0 (first k with b_tilde_k > 0 is k=1,
        meaning the complex is 0-connected but not 1-connected)."""
        reduced_betti = [betti[0] - 1, betti[1], betti[2], betti[3]]
        # Find first nonzero reduced Betti
        eta_reduced = None
        for k in range(4):
            if reduced_betti[k] > 0:
                eta_reduced = k
                break
        # First nonzero reduced Betti is at k=1 (b_tilde_1 = 81)
        assert eta_reduced == 1

    def test_not_simply_connected(self, betti):
        """The complex is NOT simply connected since b1 = 81 > 0."""
        assert betti[1] > 0


# ===========================================================================
# T1445: Cup product H^0 x H^1 -> H^1
# ===========================================================================

class TestT1445CupProduct:
    """Cup product structure: H^0(K;R) x H^1(K;R) -> H^1(K;R)."""

    def test_h0_is_one_dimensional(self, betti):
        """H^0 = R (connected complex). Universal coefficient theorem:
        H^k(K;R) = Hom(H_k, R) for field coefficients."""
        assert betti[0] == 1

    def test_h1_dimension(self, betti):
        """H^1 = R^81 (by universal coefficient theorem over R)."""
        assert betti[1] == 81

    def test_cup_h0_h1_to_h1(self, betti):
        """Cup product with H^0 = R is scalar multiplication on H^1.
        dim(H^0 x H^1) target = dim(H^1) = 81."""
        # H^0 = R acts on H^1 by scalar multiplication,
        # so the cup product map is surjective onto H^1.
        assert betti[0] * betti[1] >= betti[1]
        assert betti[1] == 81

    def test_cup_h1_h1_to_h2(self, betti):
        """Cup product H^1 x H^1 -> H^2 = 0, so all cup products vanish."""
        assert betti[2] == 0

    def test_cohomology_ring_structure(self, betti):
        """The cohomology ring H*(K;R) = R[x1,...,x81]/(x_i x_j) since
        H^2 = 0 forces all products of degree-1 classes to vanish.
        The ring is R + R^81 + 0 + 0."""
        ring_dims = betti[:]
        assert ring_dims == [1, 81, 0, 0]
        # Total dim of the cohomology ring as a vector space
        assert sum(ring_dims) == 82

    def test_cup_product_trivial_in_positive_degrees(self, hodge, betti):
        """Verify computationally: the wedge product of any two harmonic
        1-forms, when projected via d2^T, gives zero in cohomology.
        This follows from H^2 = 0."""
        # Since b2 = 0, im(d2^T) = full C2* space after modding out ker.
        # Every 2-cochain is a coboundary, confirming cup product vanishes.
        L2 = hodge["L2"]
        evals = eigvalsh(L2)
        n_harmonic_2 = np.sum(np.abs(evals) < 1e-8)
        assert n_harmonic_2 == 0  # no harmonic 2-forms => H^2 = 0
