"""
Phase CCIX --- Hodge Spectral Democracy Theorem

45 tests total.

Key result: In the W(3,3) clique complex, the Hodge Laplacians on
2-chains (triangles) and 3-chains (tetrahedra) are pure scalar
multiples of the identity:

    Delta_2 = mu * I_160    (mu = q + 1 = 4)
    Delta_3 = mu * I_40

This 'spectral democracy' means every triangle and every tetrahedron
vibrates at exactly the same frequency, set by the SRG parameter mu.

The physical origin is that each triangle belongs to exactly ONE
tetrahedron --- a partition property forced by lambda = 2.  Two adjacent
vertices share exactly lambda = 2 common neighbours; given a triangle
{a,b,c}, the only vertex that extends it to a K4 is the unique second
common neighbour of any edge of the triangle.  So distinct tetrahedra
share no triangular face.

The full Dirac-Kahler spectrum then decomposes per grade as:

    Delta_0: {0^1, Theta^f, mu^2^g}          = {0^1, 10^24, 16^15}
    Delta_1: {0^b1, mu^rank_d1, Theta^f, mu^2^g} = {0^81, 4^120, 10^24, 16^15}
    Delta_2: {mu^T}                            = {4^160}
    Delta_3: {mu^Tet}                          = {4^40}

    Full D^2: {0^82, 4^320, 10^48, 16^30}       480 total

The entire 480-dimensional spectrum is therefore completely determined
by the five SRG parameters (v, k, lambda, mu, q) and nothing else ---
no additional geometric or topological data is required.
"""

import numpy as np
from itertools import product as cartesian
from fractions import Fraction
import math

# ── SRG parameters ──────────────────────────────────────────────
Q   = 3
V   = (Q**4 - 1) // (Q - 1)          # 40
K   = Q * (Q + 1)                     # 12
LAM = Q - 1                           # 2
MU  = Q + 1                           # 4
E   = V * K // 2                      # 240
THETA = K - (-(Q + 1))                # wait -- adjacency eigenvalues
# adjacency eigenvalues: k=12, r=Q-1=2, s=-(Q+1)=-4
R_EIG = Q - 1                         # 2
S_EIG = -(Q + 1)                      # -4
F_MULT = 24                           # multiplicity of r
G_MULT = 15                           # multiplicity of s
# Laplacian eigenvalues = k - adj_eigenvalue
LAP_0 = 0                             # from k
LAP_1 = K - R_EIG                     # 10 = Theta(W33)
LAP_2 = K - S_EIG                     # 16 = mu^2
PHI3  = Q**2 + Q + 1                  # 13
PHI6  = Q**2 - Q + 1                  # 7

# Clique-complex dimensions
T_COUNT  = V * K * LAM // 6           # 160 triangles
TET_COUNT = V                          # 40 tetrahedra
DIM_C0 = V                            # 40
DIM_C1 = E                            # 240
DIM_C2 = T_COUNT                      # 160
DIM_C3 = TET_COUNT                    # 40
DIM_TOTAL = DIM_C0 + DIM_C1 + DIM_C2 + DIM_C3  # 480

# Betti numbers
B0, B1, B2, B3 = 1, Q**4, 0, 0       # (1, 81, 0, 0)

# Boundary ranks
RANK_D0 = V - B0                       # 39
RANK_D1 = E - B1 - RANK_D0            # 120
RANK_D2 = TET_COUNT                    # 40 (since b2=0 and b3=0)


# ── Graph construction ──────────────────────────────────────────
def _build_w33():
    """Build W(3,3) = SRG(40,12,2,4) from symplectic polar space."""
    F3 = range(3)
    raw = [(a, b, c, d) for a in F3 for b in F3 for c in F3 for d in F3
           if (a, b, c, d) != (0, 0, 0, 0)]
    seen, pts = set(), []
    for vec in raw:
        for i in range(4):
            if vec[i] != 0:
                inv = 1 if vec[i] == 1 else 2
                nv = tuple((x * inv) % 3 for x in vec)
                break
        if nv not in seen:
            seen.add(nv)
            pts.append(nv)
    n = len(pts)
    assert n == V

    def omega(u, w):
        return (u[0]*w[2] - u[2]*w[0] + u[1]*w[3] - u[3]*w[1]) % 3

    adj = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(i + 1, n):
            if omega(pts[i], pts[j]) == 0:
                adj[i, j] = adj[j, i] = 1
    return adj


def _find_cliques(adj):
    """Find all edges, triangles, tetrahedra (sorted tuples)."""
    n = adj.shape[0]
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i, j]:
                edges.append((i, j))
    triangles = []
    for i in range(n):
        for j in range(i + 1, n):
            if not adj[i, j]:
                continue
            for k in range(j + 1, n):
                if adj[i, k] and adj[j, k]:
                    triangles.append((i, j, k))
    tetrahedra = []
    for i, j, k in triangles:
        for l in range(k + 1, n):
            if adj[i, l] and adj[j, l] and adj[k, l]:
                tetrahedra.append((i, j, k, l))
    return edges, triangles, tetrahedra


def _boundary_d0(n, edges):
    """d0: C^0 -> C^1  (E x V matrix)."""
    d = np.zeros((len(edges), n), dtype=float)
    for idx, (i, j) in enumerate(edges):
        d[idx, i] = -1.0
        d[idx, j] = 1.0
    return d


def _boundary_d1(edges, triangles):
    """d1: C^1 -> C^2  (T x E matrix)."""
    eidx = {e: i for i, e in enumerate(edges)}
    d = np.zeros((len(triangles), len(edges)), dtype=float)
    for idx, (a, b, c) in enumerate(triangles):
        d[idx, eidx[(b, c)]] = 1.0
        d[idx, eidx[(a, c)]] = -1.0
        d[idx, eidx[(a, b)]] = 1.0
    return d


def _boundary_d2(triangles, tetrahedra):
    """d2: C^2 -> C^3  (Tet x T matrix)."""
    tidx = {t: i for i, t in enumerate(triangles)}
    d = np.zeros((len(tetrahedra), len(triangles)), dtype=float)
    for idx, (a, b, c, dd) in enumerate(tetrahedra):
        d[idx, tidx[(b, c, dd)]] = 1.0
        d[idx, tidx[(a, c, dd)]] = -1.0
        d[idx, tidx[(a, b, dd)]] = 1.0
        d[idx, tidx[(a, b, c)]] = -1.0
    return d


# ── Lazy-cached build ───────────────────────────────────────────
_CACHE = {}

def _get_all():
    """Build everything once and cache."""
    if _CACHE:
        return _CACHE
    adj = _build_w33()
    edges, triangles, tetrahedra = _find_cliques(adj)
    d0 = _boundary_d0(V, edges)
    d1 = _boundary_d1(edges, triangles)
    d2 = _boundary_d2(triangles, tetrahedra)
    L0 = d0.T @ d0                          # Hodge Laplacian grade 0
    L1 = d0 @ d0.T + d1.T @ d1             # Hodge Laplacian grade 1
    L2 = d1 @ d1.T + d2.T @ d2             # Hodge Laplacian grade 2
    L3 = d2 @ d2.T                          # Hodge Laplacian grade 3
    _CACHE.update(adj=adj, edges=edges, triangles=triangles,
                  tetrahedra=tetrahedra, d0=d0, d1=d1, d2=d2,
                  L0=L0, L1=L1, L2=L2, L3=L3)
    return _CACHE


def _sorted_eigs(M, tol=1e-8):
    """Sorted rounded eigenvalues of symmetric M."""
    vals = np.linalg.eigvalsh(M)
    return sorted(np.round(vals).astype(int))


# ═══════════════════════════════════════════════════════════════
# T1 — Chain complex dimensions and boundary ranks  (7 tests)
# ═══════════════════════════════════════════════════════════════
class TestT1ChainComplex:
    def test_vertex_count(self):
        c = _get_all()
        assert c['adj'].shape[0] == V == 40

    def test_edge_count(self):
        assert len(_get_all()['edges']) == E == 240

    def test_triangle_count(self):
        assert len(_get_all()['triangles']) == T_COUNT == 160

    def test_tetrahedron_count(self):
        assert len(_get_all()['tetrahedra']) == TET_COUNT == 40

    def test_total_chain_dim(self):
        assert V + E + T_COUNT + TET_COUNT == 480

    def test_d0_rank(self):
        c = _get_all()
        assert np.linalg.matrix_rank(c['d0']) == RANK_D0 == 39

    def test_d1_rank(self):
        c = _get_all()
        assert np.linalg.matrix_rank(c['d1']) == RANK_D1 == 120


# ═══════════════════════════════════════════════════════════════
# T2 — Chain complex condition d^2 = 0  (6 tests)
# ═══════════════════════════════════════════════════════════════
class TestT2ChainCondition:
    def test_d1_d0_is_zero(self):
        c = _get_all()
        assert np.allclose(c['d1'] @ c['d0'], 0)

    def test_d2_d1_is_zero(self):
        c = _get_all()
        assert np.allclose(c['d2'] @ c['d1'], 0)

    def test_d2_rank(self):
        c = _get_all()
        assert np.linalg.matrix_rank(c['d2']) == RANK_D2 == 40

    def test_betti_0(self):
        c = _get_all()
        b0 = V - np.linalg.matrix_rank(c['d0'])
        assert b0 == B0 == 1

    def test_betti_1(self):
        c = _get_all()
        ker_d1 = E - np.linalg.matrix_rank(c['d1'])
        b1 = ker_d1 - np.linalg.matrix_rank(c['d0'])
        assert b1 == B1 == 81

    def test_betti_2(self):
        c = _get_all()
        ker_d2 = T_COUNT - np.linalg.matrix_rank(c['d2'])
        b2 = ker_d2 - np.linalg.matrix_rank(c['d1'])
        assert b2 == B2 == 0


# ═══════════════════════════════════════════════════════════════
# T3 — Hodge Laplacian grade 0 (graph Laplacian)  (6 tests)
# ═══════════════════════════════════════════════════════════════
class TestT3HodgeLaplacianGrade0:
    def test_L0_is_graph_laplacian(self):
        c = _get_all()
        L_graph = K * np.eye(V) - c['adj']
        assert np.allclose(c['L0'], L_graph)

    def test_L0_eigenvalue_0(self):
        eigs = _sorted_eigs(_get_all()['L0'])
        assert eigs.count(0) == 1

    def test_L0_eigenvalue_theta(self):
        eigs = _sorted_eigs(_get_all()['L0'])
        assert eigs.count(LAP_1) == F_MULT == 24

    def test_L0_eigenvalue_mu_sq(self):
        eigs = _sorted_eigs(_get_all()['L0'])
        assert eigs.count(LAP_2) == G_MULT == 15

    def test_L0_theta_equals_fiedler(self):
        """Mass gap = algebraic connectivity = Theta(W33) = 10."""
        assert LAP_1 == Q**2 + 1 == 10

    def test_L0_mu_squared(self):
        """Second Laplacian eigenvalue = mu^2 = (q+1)^2 = 16."""
        assert LAP_2 == MU**2 == 16


# ═══════════════════════════════════════════════════════════════
# T4 — Hodge Laplacian grade 1  (7 tests)
# ═══════════════════════════════════════════════════════════════
class TestT4HodgeLaplacianGrade1:
    def test_L1_dim(self):
        assert _get_all()['L1'].shape == (E, E)

    def test_L1_harmonic_count(self):
        eigs = _sorted_eigs(_get_all()['L1'])
        assert eigs.count(0) == B1 == 81

    def test_L1_mu_count(self):
        eigs = _sorted_eigs(_get_all()['L1'])
        assert eigs.count(MU) == RANK_D1 == 120

    def test_L1_theta_count(self):
        eigs = _sorted_eigs(_get_all()['L1'])
        assert eigs.count(LAP_1) == F_MULT == 24

    def test_L1_mu_sq_count(self):
        eigs = _sorted_eigs(_get_all()['L1'])
        assert eigs.count(LAP_2) == G_MULT == 15

    def test_L1_total(self):
        eigs = _sorted_eigs(_get_all()['L1'])
        assert len(eigs) == E == 240

    def test_L1_only_four_eigenvalues(self):
        eigs = set(_sorted_eigs(_get_all()['L1']))
        assert eigs == {0, MU, LAP_1, LAP_2}


# ═══════════════════════════════════════════════════════════════
# T5 — Triangle partition theorem  (6 tests)
# ═══════════════════════════════════════════════════════════════
class TestT5TrianglePartition:
    """Each triangle belongs to exactly ONE tetrahedron."""

    def test_each_triangle_in_one_tet(self):
        c = _get_all()
        tri_set = set(c['triangles'])
        for a, b, cc, d in c['tetrahedra']:
            for face in [(b, cc, d), (a, cc, d), (a, b, d), (a, b, cc)]:
                assert face in tri_set

    def test_face_count_matches(self):
        """40 tets * 4 faces = 160 triangles (exact partition)."""
        assert TET_COUNT * 4 == T_COUNT

    def test_no_shared_faces(self):
        """Distinct tetrahedra share no triangular face."""
        c = _get_all()
        face_to_tet = {}
        for idx, (a, b, cc, d) in enumerate(c['tetrahedra']):
            for face in [(b, cc, d), (a, cc, d), (a, b, d), (a, b, cc)]:
                assert face not in face_to_tet, "shared face found"
                face_to_tet[face] = idx
        assert len(face_to_tet) == T_COUNT

    def test_lambda_forces_unique_extension(self):
        """With lambda=2, each triangle extends to exactly 1 K4."""
        c = _get_all()
        adj = c['adj']
        for a, b, cc in c['triangles'][:20]:  # spot check
            common = [v for v in range(V)
                      if v not in (a, b, cc)
                      and adj[a, v] and adj[b, v] and adj[cc, v]]
            assert len(common) == 1

    def test_vertex_in_mu_tetrahedra(self):
        """Each vertex is in exactly mu = 4 tetrahedra."""
        c = _get_all()
        for v in range(V):
            count = sum(1 for t in c['tetrahedra'] if v in t)
            assert count == MU

    def test_neighborhood_is_mu_triangles(self):
        """Each vertex's neighbourhood is mu disjoint triangles."""
        c = _get_all()
        adj = c['adj']
        for v in range(V):
            nbrs = [u for u in range(V) if adj[v, u]]
            assert len(nbrs) == K
            # Each pair of adjacent neighbours shares exactly lambda-1 = 1
            # other common neighbour in the neighbourhood -> mu copies of K3
            tri_count = 0
            for i in range(len(nbrs)):
                for j in range(i + 1, len(nbrs)):
                    if adj[nbrs[i], nbrs[j]]:
                        tri_count += 1
            # K3 has 3 edges, mu copies -> mu*3 = 12 = K edges
            assert tri_count == K  # each K3 contributes 3 edges, 4*3=12


# ═══════════════════════════════════════════════════════════════
# T6 — Spectral democracy: Delta_3 = mu * I  (6 tests)
# ═══════════════════════════════════════════════════════════════
class TestT6SpectralDemocracyGrade3:
    """Delta_3 = d2 d2^T = mu * I_{40}."""

    def test_L3_is_scalar(self):
        c = _get_all()
        assert np.allclose(c['L3'], MU * np.eye(TET_COUNT))

    def test_L3_single_eigenvalue(self):
        eigs = _sorted_eigs(_get_all()['L3'])
        assert set(eigs) == {MU}

    def test_L3_multiplicity(self):
        eigs = _sorted_eigs(_get_all()['L3'])
        assert eigs.count(MU) == TET_COUNT == 40

    def test_L3_trace(self):
        c = _get_all()
        assert abs(np.trace(c['L3']) - MU * TET_COUNT) < 1e-10

    def test_L3_determinant(self):
        c = _get_all()
        expected = MU ** TET_COUNT  # 4^40
        assert abs(np.linalg.det(c['L3']) - expected) / expected < 1e-6

    def test_L3_diagonal_entries(self):
        c = _get_all()
        for i in range(TET_COUNT):
            assert abs(c['L3'][i, i] - MU) < 1e-10


# ═══════════════════════════════════════════════════════════════
# T7 — Spectral democracy: Delta_2 = mu * I  (7 tests)
# ═══════════════════════════════════════════════════════════════
class TestT7SpectralDemocracyGrade2:
    """Delta_2 = d1 d1^T + d2^T d2 = mu * I_{160}."""

    def test_L2_is_scalar(self):
        c = _get_all()
        assert np.allclose(c['L2'], MU * np.eye(T_COUNT))

    def test_L2_single_eigenvalue(self):
        eigs = _sorted_eigs(_get_all()['L2'])
        assert set(eigs) == {MU}

    def test_L2_multiplicity(self):
        eigs = _sorted_eigs(_get_all()['L2'])
        assert eigs.count(MU) == T_COUNT == 160

    def test_L2_trace(self):
        c = _get_all()
        assert abs(np.trace(c['L2']) - MU * T_COUNT) < 1e-10

    def test_L2_no_harmonic_forms(self):
        """b_2 = 0 consistent with Delta_2 being strictly positive."""
        eigs = _sorted_eigs(_get_all()['L2'])
        assert 0 not in eigs

    def test_down_part_eigenvalue(self):
        """d1 d1^T restricted to Im(d1) has eigenvalue mu = 4."""
        c = _get_all()
        down = c['d1'] @ c['d1'].T  # T x T
        eigs = sorted(np.round(np.linalg.eigvalsh(down)).astype(int))
        nonzero = [e for e in eigs if e != 0]
        assert all(e == MU for e in nonzero)
        assert len(nonzero) == RANK_D1 == 120

    def test_up_part_eigenvalue(self):
        """d2^T d2 restricted to Im(d2^T) has eigenvalue mu = 4."""
        c = _get_all()
        up = c['d2'].T @ c['d2']  # T x T
        eigs = sorted(np.round(np.linalg.eigvalsh(up)).astype(int))
        nonzero = [e for e in eigs if e != 0]
        assert all(e == MU for e in nonzero)
        assert len(nonzero) == RANK_D2 == 40
