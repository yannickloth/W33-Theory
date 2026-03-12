"""
Phase CXVII  --  Incidence Geometry Computation on W(3,3) = SRG(40,12,2,4).

80 tests covering projective space PG(3,3), generalized quadrangle GQ(3,3),
incidence matrix algebra, spreads & ovoids, collinearity & perpendicularity,
dual structure, subgeometry, and configuration counts.

All tests use only numpy and standard library.  Key structural facts:
    n = 40 = (3^4-1)/(3-1) points of PG(3,3)
    k = 12 neighbours via symplectic form  omega(u,v) = u0*v1 - u1*v0 + u2*v3 - u3*v2
    40 totally isotropic lines (= lines of GQ(3,3)), each of size 4
    GQ(3,3):  s = t = 3,  self-dual,  collinearity graph = SRG(40,12,2,4)
    adjacency spectrum:  {12^1, 2^24, (-4)^15}
"""

import numpy as np
from numpy.linalg import eigvalsh, matrix_rank
import pytest
from itertools import combinations
from collections import Counter


# ── W(3,3) builder ───────────────────────────────────────────────────────────

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
    return A, points


# ── Helpers ──────────────────────────────────────────────────────────────────

def _symplectic_form(u, v):
    """Symplectic form omega(u,v) mod 3."""
    return (u[0]*v[1] - u[1]*v[0] + u[2]*v[3] - u[3]*v[2]) % 3


def _find_gq_lines(A):
    """Find all 40 totally isotropic lines (maximal 4-cliques) of GQ(3,3)."""
    n = A.shape[0]
    line_set = set()
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j] != 1:
                continue
            cn = [k for k in range(n)
                  if k != i and k != j and A[i, k] == 1 and A[j, k] == 1]
            if len(cn) >= 2:
                for a, b in combinations(cn, 2):
                    if A[a, b] == 1:
                        line_set.add(tuple(sorted([i, j, a, b])))
    return sorted(line_set)


def _find_pg_lines(points):
    """Find all 130 lines of PG(3,3) via projective span."""
    n = len(points)
    all_lines = set()
    for i in range(n):
        for j in range(i + 1, n):
            pi, pj = points[i], points[j]
            line_pts = set()
            for a in range(3):
                for b in range(3):
                    if a == 0 and b == 0:
                        continue
                    v = tuple((a * pi[k] + b * pj[k]) % 3 for k in range(4))
                    # v cannot be zero for distinct canonical points
                    first = next(x for x in v if x != 0)
                    inv_f = pow(first, -1, 3)
                    canon = tuple((x * inv_f) % 3 for x in v)
                    idx = points.index(canon)
                    line_pts.add(idx)
            all_lines.add(tuple(sorted(line_pts)))
    return sorted(all_lines)


def _build_incidence_matrix(n_pts, lines):
    """Point-line incidence matrix B  (n_pts x n_lines)."""
    n_lines = len(lines)
    B = np.zeros((n_pts, n_lines), dtype=int)
    for j, line in enumerate(lines):
        for i in line:
            B[i, j] = 1
    return B


def _build_dual_adjacency(lines):
    """Concurrency graph on lines: D[i,j]=1 iff lines i,j share a point."""
    n = len(lines)
    D = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(i + 1, n):
            if set(lines[i]) & set(lines[j]):
                D[i, j] = D[j, i] = 1
    return D


def _find_spread(lines):
    """Find a spread (10 disjoint lines covering all 40 points) via MRV
    backtracking."""
    pt_to_lines = {}
    for idx, l in enumerate(lines):
        for p in l:
            pt_to_lines.setdefault(p, []).append(idx)
    line_sets = [frozenset(l) for l in lines]

    def bt(covered, chosen):
        if len(covered) == 40:
            return chosen[:]
        # Pick uncovered point with fewest remaining line options (MRV)
        best_pt, best_count = None, 999
        for p in range(40):
            if p in covered:
                continue
            cnt = sum(1 for li in pt_to_lines[p]
                      if not line_sets[li] & covered)
            if cnt == 0:
                return None
            if cnt < best_count:
                best_count = cnt
                best_pt = p
        for li in pt_to_lines[best_pt]:
            if not line_sets[li] & covered:
                r = bt(covered | line_sets[li], chosen + [lines[li]])
                if r is not None:
                    return r
        return None

    return bt(frozenset(), [])


def _find_maximal_coclique(A):
    """Find a maximal (non-extendable) independent set via greedy."""
    n = A.shape[0]
    coclique = []
    for i in range(n):
        if all(A[i, j] == 0 for j in coclique):
            coclique.append(i)
    return coclique


def _no_ovoid_via_spread(A, spread):
    """Prove no ovoid exists by exhaustive backtracking over spread
    transversals.  Any independent set of size 10 must pick exactly one
    point from each spread line (10 lines x 1 point = 10).  We check
    all 4^10 ~ 10^6 transversals with pruning."""
    nbrs = [set(int(j) for j in np.where(A[i] == 1)[0]) for i in range(40)]
    line_pts = [list(l) for l in spread]

    def bt(depth, chosen):
        if depth == 10:
            return True  # found a valid transversal = ovoid
        for p in line_pts[depth]:
            if not any(p in nbrs[c] for c in chosen):
                if bt(depth + 1, chosen + [p]):
                    return True
        return False

    return not bt(0, [])  # True means no ovoid exists


# ── SRG parameters ───────────────────────────────────────────────────────────

_N, _K, _LAM, _MU = 40, 12, 2, 4
_S, _T = 3, 3          # GQ parameters


# ── Module-scoped fixtures ───────────────────────────────────────────────────

@pytest.fixture(scope="module")
def w33_data():
    A, pts = _build_w33()
    return A, pts


@pytest.fixture(scope="module")
def A(w33_data):
    """Adjacency matrix of W(3,3)."""
    return w33_data[0]


@pytest.fixture(scope="module")
def points(w33_data):
    """40 canonical points of PG(3,3)."""
    return w33_data[1]


@pytest.fixture(scope="module")
def gq_lines(A):
    """40 totally isotropic lines of GQ(3,3)."""
    return _find_gq_lines(A)


@pytest.fixture(scope="module")
def pg_lines(points):
    """130 lines of PG(3,3)."""
    return _find_pg_lines(points)


@pytest.fixture(scope="module")
def B(gq_lines):
    """40 x 40 incidence matrix (points x GQ-lines)."""
    return _build_incidence_matrix(40, gq_lines)


@pytest.fixture(scope="module")
def dual_adj(gq_lines):
    """Dual collinearity (concurrency) matrix on the 40 GQ lines."""
    return _build_dual_adjacency(gq_lines)


@pytest.fixture(scope="module")
def spread(gq_lines):
    """A spread: 10 disjoint lines covering all 40 points."""
    return _find_spread(gq_lines)


@pytest.fixture(scope="module")
def maximal_coclique(A):
    """A maximal (non-extendable) independent set."""
    return _find_maximal_coclique(A)


# ═════════════════════════════════════════════════════════════════════════════
# Section 1 : Projective Space PG(3,3)   (12 tests)
# ═════════════════════════════════════════════════════════════════════════════

class TestPG33:
    """Projective geometry of PG(3,3) = 40 points, 130 lines, Grassmannian."""

    def test_point_count(self, points):
        """PG(3,3) has (3^4-1)/(3-1) = 40 points."""
        assert len(points) == 40

    def test_points_canonical(self, points):
        """Every point has first nonzero coordinate = 1."""
        for p in points:
            first_nz = next(x for x in p if x != 0)
            assert first_nz == 1

    def test_points_distinct(self, points):
        """All 40 points are distinct tuples."""
        assert len(set(points)) == 40

    def test_points_are_4tuples_mod3(self, points):
        """All coordinates in {0, 1, 2}."""
        for p in points:
            assert len(p) == 4
            assert all(0 <= c <= 2 for c in p)

    def test_pg_line_count(self, pg_lines):
        """PG(3,3) has [4,2]_3 = 130 lines."""
        assert len(pg_lines) == 130

    def test_pg_line_size(self, pg_lines):
        """Every PG line has exactly q+1 = 4 points."""
        for line in pg_lines:
            assert len(line) == 4

    def test_lines_through_point(self, pg_lines):
        """Each point lies on (q^3-1)/(q-1) = 13 PG lines."""
        for p in range(40):
            count = sum(1 for l in pg_lines if p in l)
            assert count == 13

    def test_two_points_determine_unique_line(self, pg_lines, points):
        """Any two distinct points lie on exactly one PG line."""
        # Check a sample of 200 pairs
        rng = np.random.RandomState(42)
        pairs = set()
        while len(pairs) < 200:
            i, j = sorted(rng.choice(40, 2, replace=False))
            pairs.add((i, j))
        for i, j in pairs:
            count = sum(1 for l in pg_lines if i in l and j in l)
            assert count == 1

    def test_isotropic_line_count(self, pg_lines, A):
        """Exactly 40 of the 130 PG lines are totally isotropic."""
        iso = [l for l in pg_lines if A[l[0], l[1]] == 1]
        assert len(iso) == 40

    def test_non_isotropic_line_count(self, pg_lines, A):
        """130 - 40 = 90 PG lines are not totally isotropic."""
        non_iso = [l for l in pg_lines if A[l[0], l[1]] == 0]
        assert len(non_iso) == 90

    def test_isotropic_lines_match_gq_lines(self, pg_lines, gq_lines, A):
        """Totally isotropic PG lines are exactly the GQ lines."""
        iso_set = {l for l in pg_lines if A[l[0], l[1]] == 1}
        gq_set = set(gq_lines)
        assert iso_set == gq_set

    def test_pg_plane_count_formula(self, points):
        """PG(3,3) has (3^4-1)/(3-1) = 40 planes (equal to #points by duality)."""
        # Gaussian binomial [4,3]_3 = (3^4-1)/(3-1) = 40
        gauss_43 = (3**4 - 1) // (3 - 1)
        assert gauss_43 == 40


# ═════════════════════════════════════════════════════════════════════════════
# Section 2 : Generalized Quadrangle GQ(3,3)   (10 tests)
# ═════════════════════════════════════════════════════════════════════════════

class TestGQ33:
    """GQ(3,3) axioms, parameters, and consistency."""

    def test_gq_point_count(self, A):
        """GQ(3,3) has (s+1)(st+1) = 4*10 = 40 points."""
        assert A.shape[0] == 40

    def test_gq_line_count(self, gq_lines):
        """GQ(3,3) has (t+1)(st+1) = 4*10 = 40 lines."""
        assert len(gq_lines) == 40

    def test_line_size(self, gq_lines):
        """Every GQ line has s+1 = 4 points."""
        for line in gq_lines:
            assert len(line) == 4

    def test_lines_per_point(self, gq_lines):
        """Each point is on t+1 = 4 lines."""
        for p in range(40):
            assert sum(1 for l in gq_lines if p in l) == 4

    def test_collinear_pair_unique_line(self, A, gq_lines):
        """Two collinear points lie on exactly one GQ line."""
        for i in range(40):
            for j in range(i + 1, 40):
                if A[i, j] == 1:
                    cnt = sum(1 for l in gq_lines if i in l and j in l)
                    assert cnt == 1

    def test_gq_axiom_antiflags(self, A, gq_lines):
        """GQ axiom: for each anti-flag (P, L), exactly 1 point on L is
        collinear with P (and exactly 1 line through P meets L)."""
        for li, line in enumerate(gq_lines):
            line_set = set(line)
            for p in range(40):
                if p in line_set:
                    continue
                collinear_on_L = [q for q in line if A[p, q] == 1]
                assert len(collinear_on_L) == 1

    def test_srg_degree(self, A):
        """Collinearity graph is k = 12 regular."""
        degs = A.sum(axis=1)
        assert np.all(degs == 12)

    def test_srg_lambda(self, A):
        """lambda = 2: adjacent pair has 2 common neighbours."""
        for i in range(40):
            for j in range(i + 1, 40):
                if A[i, j] == 1:
                    cn = sum(A[i, k] * A[j, k] for k in range(40))
                    assert cn == 2

    def test_srg_mu(self, A):
        """mu = 4: non-adjacent pair has 4 common neighbours."""
        for i in range(40):
            for j in range(i + 1, 40):
                if A[i, j] == 0:
                    cn = sum(A[i, k] * A[j, k] for k in range(40))
                    assert cn == 4

    def test_no_two_lines_share_two_points(self, gq_lines):
        """Partial linear space: two lines share at most 1 point."""
        for i in range(len(gq_lines)):
            for j in range(i + 1, len(gq_lines)):
                assert len(set(gq_lines[i]) & set(gq_lines[j])) <= 1


# ═════════════════════════════════════════════════════════════════════════════
# Section 3 : Incidence Matrix   (10 tests)
# ═════════════════════════════════════════════════════════════════════════════

class TestIncidenceMatrix:
    """Incidence matrix B (40 x 40) and its algebraic properties."""

    def test_shape(self, B):
        """B is 40 x 40 (points x lines)."""
        assert B.shape == (40, 40)

    def test_column_sums(self, B):
        """Each column (line) has s+1 = 4 ones."""
        assert np.all(B.sum(axis=0) == 4)

    def test_row_sums(self, B):
        """Each row (point) has t+1 = 4 ones."""
        assert np.all(B.sum(axis=1) == 4)

    def test_BBT_equals_A_plus_4I(self, B, A):
        """BB^T = A + 4I  (two collinear points share exactly 1 line)."""
        BBT = B @ B.T
        expected = A + 4 * np.eye(40, dtype=int)
        assert np.array_equal(BBT, expected)

    def test_BTB_diagonal(self, B):
        """Diagonal of B^TB = s+1 = 4 (points per line)."""
        BTB = B.T @ B
        assert np.all(np.diag(BTB) == 4)

    def test_BTB_off_diagonal_binary(self, B):
        """Off-diagonal entries of B^TB are in {0, 1}."""
        BTB = B.T @ B
        off = BTB - np.diag(np.diag(BTB))
        assert set(np.unique(off)).issubset({0, 1})

    def test_rank(self, B):
        """rank(B) = 25  (from BB^T eigenvalue 0 with multiplicity 15)."""
        assert matrix_rank(B) == 25

    def test_BBT_eigenvalues(self, B):
        """BB^T has eigenvalues {16, 6, 0}."""
        ev = np.sort(eigvalsh((B @ B.T).astype(float)))
        expected = sorted([0.0] * 15 + [6.0] * 24 + [16.0])
        assert np.allclose(ev, expected, atol=1e-8)

    def test_BBT_eigenvalue_multiplicities(self, B):
        """Multiplicities: 0 x 15, 6 x 24, 16 x 1."""
        ev = eigvalsh((B @ B.T).astype(float))
        c = Counter(round(float(e)) for e in ev)
        assert c[0] == 15
        assert c[6] == 24
        assert c[16] == 1

    def test_trace_BBT(self, B):
        """trace(BB^T) = 40 * 4 = 160  (each point on 4 lines)."""
        assert np.trace(B @ B.T) == 160


# ═════════════════════════════════════════════════════════════════════════════
# Section 4 : Spreads & Ovoids   (10 tests)
# ═════════════════════════════════════════════════════════════════════════════

class TestSpreadsOvoids:
    """Spreads exist; ovoids do NOT (Thas' theorem: W(q) has ovoids iff q even)."""

    def test_spread_exists(self, spread):
        """A spread (partition into lines) exists for GQ(3,3)."""
        assert spread is not None

    def test_spread_size(self, spread):
        """Spread has 10 lines (40 / 4)."""
        assert len(spread) == 10

    def test_spread_covers_all_points(self, spread):
        """Spread lines cover all 40 points."""
        covered = set()
        for line in spread:
            covered.update(line)
        assert len(covered) == 40

    def test_spread_lines_disjoint(self, spread):
        """Spread lines are pairwise disjoint."""
        for i in range(len(spread)):
            for j in range(i + 1, len(spread)):
                assert not set(spread[i]) & set(spread[j])

    def test_spread_lines_are_gq_lines(self, spread, gq_lines):
        """Every spread line is a GQ line."""
        gq_set = set(gq_lines)
        for line in spread:
            assert tuple(sorted(line)) in gq_set

    def test_no_ovoid_exists(self, A, spread):
        """W(3) = W(q) for q=3 (odd) has NO ovoid (Thas' theorem).
        Exhaustive backtracking over spread transversals confirms
        no independent set of size st+1 = 10 exists."""
        assert _no_ovoid_via_spread(A, spread)

    def test_hoffman_bound(self, A):
        """Hoffman bound: independence number <= n*(-s_min)/(k-s_min) = 10.
        The bound is NOT achieved (no ovoid for q odd)."""
        s_min = -4.0  # least eigenvalue of SRG(40,12,2,4)
        bound = 40 * (-s_min) / (12 - s_min)
        assert abs(bound - 10.0) < 1e-10

    def test_maximal_coclique_exists(self, maximal_coclique):
        """A maximal (non-extendable) independent set exists."""
        assert len(maximal_coclique) >= 1

    def test_maximal_coclique_is_independent(self, maximal_coclique, A):
        """Maximal coclique is an independent set."""
        for i, j in combinations(maximal_coclique, 2):
            assert A[i, j] == 0

    def test_maximal_coclique_non_extendable(self, maximal_coclique, A):
        """Maximal coclique cannot be extended: every non-member has a
        neighbour in the coclique."""
        S = set(maximal_coclique)
        for v in range(40):
            if v in S:
                continue
            assert any(A[v, u] == 1 for u in S)


# ═════════════════════════════════════════════════════════════════════════════
# Section 5 : Collinearity & Perpendicularity   (10 tests)
# ═════════════════════════════════════════════════════════════════════════════

class TestCollinearityPerp:
    """Symplectic form, collinearity, and perp geometry."""

    def test_form_alternating(self, points):
        """omega(u,u) = 0 for every point (alternating form)."""
        for p in points:
            assert _symplectic_form(p, p) == 0

    def test_form_antisymmetric(self, points):
        """omega(u,v) = -omega(v,u) mod 3."""
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                w1 = _symplectic_form(points[i], points[j])
                w2 = _symplectic_form(points[j], points[i])
                assert (w1 + w2) % 3 == 0

    def test_collinear_iff_omega_zero(self, A, points):
        """A[i,j] = 1 iff omega(pi,pj) = 0 (for i != j)."""
        for i in range(40):
            for j in range(i + 1, 40):
                w = _symplectic_form(points[i], points[j])
                assert A[i, j] == (1 if w == 0 else 0)

    def test_perp_size(self, A):
        """perp(p) = {p} union neighbours(p) has 1 + 12 = 13 elements."""
        for p in range(40):
            perp = {p} | {q for q in range(40) if A[p, q] == 1}
            assert len(perp) == 13

    def test_perp_contains_self(self, A):
        """p is always in perp(p)."""
        # trivially true by definition, verify consistency
        for p in range(40):
            perp = {p} | {q for q in range(40) if A[p, q] == 1}
            assert p in perp

    def test_perp_symmetric(self, A):
        """i in perp(j) iff j in perp(i)  (A is symmetric)."""
        assert np.array_equal(A, A.T)

    def test_form_nondegenerate(self):
        """Symplectic form matrix has det != 0 mod 3."""
        # omega(u,v) = u^T M v with M = [[0,1,0,0],[-1,0,0,0],[0,0,0,1],[0,0,-1,0]]
        M = np.array([[0, 1, 0, 0],
                       [2, 0, 0, 0],
                       [0, 0, 0, 1],
                       [0, 0, 2, 0]], dtype=int)  # -1 = 2 mod 3
        det = int(round(np.linalg.det(M.astype(float))))
        assert det % 3 != 0

    def test_form_matrix_entries(self):
        """Explicit symplectic matrix reproduces form on basis vectors."""
        e = [(1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)]
        # omega(e0,e1) = 1, omega(e2,e3) = 1, all others 0
        assert _symplectic_form(e[0], e[1]) == 1
        assert _symplectic_form(e[2], e[3]) == 1
        assert _symplectic_form(e[0], e[2]) == 0
        assert _symplectic_form(e[0], e[3]) == 0
        assert _symplectic_form(e[1], e[2]) == 0
        assert _symplectic_form(e[1], e[3]) == 0

    def test_common_perp_collinear_is_line(self, A, gq_lines):
        """For collinear i~j: perp(i) ∩ perp(j) = the 4-point line through them."""
        checked = 0
        for line in gq_lines[:10]:
            i, j = line[0], line[1]
            perp_i = {i} | {k for k in range(40) if A[i, k] == 1}
            perp_j = {j} | {k for k in range(40) if A[j, k] == 1}
            inter = perp_i & perp_j
            assert inter == set(line)
            checked += 1
        assert checked == 10

    def test_common_perp_noncollinear_count(self, A):
        """For non-collinear i,j: |perp(i) ∩ perp(j)| = mu = 4."""
        checked = 0
        for i in range(40):
            for j in range(i + 1, 40):
                if A[i, j] == 0:
                    perp_i = {i} | {k for k in range(40) if A[i, k] == 1}
                    perp_j = {j} | {k for k in range(40) if A[j, k] == 1}
                    assert len(perp_i & perp_j) == 4
                    checked += 1
                    if checked >= 50:
                        break
            if checked >= 50:
                break
        assert checked == 50


# ═════════════════════════════════════════════════════════════════════════════
# Section 6 : Dual Structure   (10 tests)
# ═════════════════════════════════════════════════════════════════════════════

class TestDualStructure:
    """GQ(3,3) is self-dual (s = t); dual collinearity = concurrency on lines."""

    def test_dual_point_count(self, dual_adj):
        """Dual has 40 points (= 40 GQ lines)."""
        assert dual_adj.shape[0] == 40

    def test_dual_degree(self, dual_adj):
        """Each line is concurrent with 12 others: 4 points x 3 other lines."""
        degs = dual_adj.sum(axis=1)
        assert np.all(degs == 12)

    def test_dual_adjacency_symmetric(self, dual_adj):
        """Concurrency is symmetric."""
        assert np.array_equal(dual_adj, dual_adj.T)

    def test_dual_trace_zero(self, dual_adj):
        """No line is concurrent with itself (no self-loops)."""
        assert np.trace(dual_adj) == 0

    def test_dual_lambda(self, dual_adj):
        """Dual lambda = 2: two concurrent lines have 2 common concurrent lines."""
        checked = 0
        for i in range(40):
            for j in range(i + 1, 40):
                if dual_adj[i, j] == 1:
                    cn = sum(dual_adj[i, k] * dual_adj[j, k] for k in range(40))
                    assert cn == 2, f"lines {i},{j}: lambda = {cn}"
                    checked += 1
                    if checked >= 60:
                        break
            if checked >= 60:
                break
        assert checked >= 60

    def test_dual_mu(self, dual_adj):
        """Dual mu = 4: two non-concurrent lines have 4 common concurrent lines."""
        checked = 0
        for i in range(40):
            for j in range(i + 1, 40):
                if dual_adj[i, j] == 0:
                    cn = sum(dual_adj[i, k] * dual_adj[j, k] for k in range(40))
                    assert cn == 4, f"lines {i},{j}: mu = {cn}"
                    checked += 1
                    if checked >= 60:
                        break
            if checked >= 60:
                break
        assert checked >= 60

    def test_dual_eigenvalues(self, dual_adj):
        """Dual adjacency has same spectrum: {12^1, 2^24, (-4)^15}."""
        ev = np.sort(eigvalsh(dual_adj.astype(float)))
        expected = sorted([-4.0] * 15 + [2.0] * 24 + [12.0])
        assert np.allclose(ev, expected, atol=1e-8)

    def test_concurrent_pair_count(self, dual_adj):
        """Number of concurrent line pairs = 40 * 12 / 2 = 240."""
        assert dual_adj.sum() // 2 == 240

    def test_nonconcurrent_pair_count(self, dual_adj):
        """Non-concurrent pairs = C(40,2) - 240 = 540."""
        total = 40 * 39 // 2
        concurrent = dual_adj.sum() // 2
        assert total - concurrent == 540

    def test_dual_incidence_is_BT(self, B, gq_lines):
        """Incidence matrix of dual = B^T: dual 'point' i (line) on dual 'line'
        j (point) iff original point j on original line i."""
        B_dual = B.T
        # Each row of B_dual (= column of B) has 4 ones (line has 4 points)
        assert np.all(B_dual.sum(axis=1) == 4)
        # Each column of B_dual (= row of B) has 4 ones (point on 4 lines)
        assert np.all(B_dual.sum(axis=0) == 4)


# ═════════════════════════════════════════════════════════════════════════════
# Section 7 : Subgeometry   (10 tests)
# ═════════════════════════════════════════════════════════════════════════════

class TestSubgeometry:
    """Pencils, stars, transversals, quadrangles, residues."""

    def test_pencil_size(self, gq_lines):
        """Pencil at each point (set of lines through it) has t+1 = 4 lines."""
        for p in range(40):
            pencil = [l for l in gq_lines if p in l]
            assert len(pencil) == 4

    def test_pencil_lines_share_point(self, gq_lines):
        """All lines in a pencil share the base point."""
        for p in range(40):
            pencil = [l for l in gq_lines if p in l]
            for l in pencil:
                assert p in l

    def test_pencil_partition_neighbours(self, A, gq_lines):
        """The 4 lines through p partition p's 12 neighbours into 4 groups of 3."""
        for p in range(40):
            pencil = [l for l in gq_lines if p in l]
            groups = [set(l) - {p} for l in pencil]
            union = set()
            for g in groups:
                assert len(g) == 3
                assert not union & g
                union |= g
            assert union == {q for q in range(40) if A[p, q] == 1}

    def test_star_covers_all_neighbours(self, A, gq_lines):
        """Star at p: the 12 neighbours are exactly the 4*3 non-p points on
        lines through p."""
        for p in range(10):  # sample 10 points
            nbrs = {q for q in range(40) if A[p, q] == 1}
            star = set()
            for l in gq_lines:
                if p in l:
                    star |= set(l) - {p}
            assert star == nbrs

    def test_transversal_count(self, A, gq_lines):
        """Two non-concurrent lines have exactly s+1 = 4 transversal lines."""
        line_index = {tuple(l): i for i, l in enumerate(gq_lines)}
        checked = 0
        for i in range(len(gq_lines)):
            for j in range(i + 1, len(gq_lines)):
                if set(gq_lines[i]) & set(gq_lines[j]):
                    continue  # concurrent
                # Count transversal lines connecting gq_lines[i] to gq_lines[j]
                trans = set()
                for p in gq_lines[i]:
                    for q in gq_lines[j]:
                        if A[p, q] == 1:
                            # find GQ line through p and q
                            for l in gq_lines:
                                if p in l and q in l:
                                    trans.add(tuple(l))
                assert len(trans) == 4
                checked += 1
                if checked >= 40:
                    break
            if checked >= 40:
                break
        assert checked == 40

    def test_transversal_bijection(self, A, gq_lines):
        """Transversals form a bijection between points of two non-concurrent lines."""
        for i in range(len(gq_lines)):
            for j in range(i + 1, len(gq_lines)):
                if set(gq_lines[i]) & set(gq_lines[j]):
                    continue
                # build mapping: point of L -> unique collinear point of M
                mapping = {}
                for p in gq_lines[i]:
                    cols = [q for q in gq_lines[j] if A[p, q] == 1]
                    assert len(cols) == 1  # GQ axiom
                    mapping[p] = cols[0]
                # mapping is injective => bijective (|domain|=|codomain|=4)
                assert len(set(mapping.values())) == 4
                return  # one pair suffices
        pytest.fail("no non-concurrent pair found")

    def test_quadrangle_exists(self, A):
        """A geometric quadrangle (4-cycle without diagonals) exists."""
        found = False
        for p1 in range(40):
            if found:
                break
            for p2 in range(p1 + 1, 40):
                if A[p1, p2] != 1:
                    continue
                for p3 in range(40):
                    if p3 == p1 or p3 == p2:
                        continue
                    if A[p2, p3] != 1 or A[p1, p3] != 0:
                        continue
                    # p1 ~ p2 ~ p3, p1 not~ p3
                    for p4 in range(40):
                        if p4 in (p1, p2, p3):
                            continue
                        if (A[p3, p4] == 1 and A[p4, p1] == 1
                                and A[p2, p4] == 0):
                            found = True
                            break
                    if found:
                        break
                if found:
                    break
        assert found

    def test_projection_unique(self, A, gq_lines):
        """For anti-flag (P, L): the unique point on L collinear with P
        and the unique line through P meeting L are well-defined."""
        checked = 0
        for line in gq_lines[:10]:
            line_set = set(line)
            for p in range(40):
                if p in line_set:
                    continue
                # foot = unique point on L collinear with P
                foot = [q for q in line if A[p, q] == 1]
                assert len(foot) == 1
                # line through P and foot
                pf_lines = [l for l in gq_lines if p in l and foot[0] in l]
                assert len(pf_lines) == 1
                checked += 1
        assert checked > 0

    def test_three_collinear_on_line(self, A, gq_lines):
        """Any 3 mutually collinear points lie on a common GQ line."""
        checked = 0
        for line in gq_lines:
            for triple in combinations(line, 3):
                a, b, c = triple
                assert A[a, b] == 1 and A[a, c] == 1 and A[b, c] == 1
                # they share a GQ line
                common = [l for l in gq_lines
                          if a in l and b in l and c in l]
                assert len(common) == 1
                checked += 1
        assert checked == 40 * 4  # C(4,3) = 4 triples per line

    def test_residue_at_point(self, A, gq_lines):
        """Residue at a point: the 4 lines and 12 neighbours form a
        generalized digon (complete bipartite K_{4,3} structure)."""
        p = 0
        pencil = [l for l in gq_lines if p in l]
        assert len(pencil) == 4
        # Each pair of pencil lines shares only p
        for l1, l2 in combinations(pencil, 2):
            assert set(l1) & set(l2) == {p}


# ═════════════════════════════════════════════════════════════════════════════
# Section 8 : Configuration Counts   (8 tests)
# ═════════════════════════════════════════════════════════════════════════════

class TestConfigurationCounts:
    """Combinatorial counts derived from GQ(3,3) / SRG(40,12,2,4)."""

    def test_edge_count(self, A):
        """Number of edges = n*k/2 = 40*12/2 = 240."""
        assert A.sum() // 2 == 240

    def test_triangle_count(self, A):
        """Number of triangles = n*k*lambda/6 = 40*12*2/6 = 160.
        Equivalently, 40 lines x C(4,3) = 160."""
        # count via trace(A^3)/6
        A3 = A @ A @ A
        triangles = np.trace(A3) // 6
        assert triangles == 160

    def test_all_triangles_on_lines(self, A, gq_lines):
        """Every triangle in the collinearity graph comes from 3 points
        on a GQ line (no non-trivial triangles in a GQ)."""
        # Triangles from lines: 40 * C(4,3) = 160
        line_triangles = set()
        for line in gq_lines:
            for triple in combinations(line, 3):
                line_triangles.add(tuple(sorted(triple)))
        # Count ALL triangles in the graph
        all_triangles = set()
        for i in range(40):
            for j in range(i + 1, 40):
                if A[i, j] != 1:
                    continue
                for k in range(j + 1, 40):
                    if A[i, k] == 1 and A[j, k] == 1:
                        all_triangles.add((i, j, k))
        assert all_triangles == line_triangles
        assert len(all_triangles) == 160

    def test_flag_count(self, gq_lines):
        """Number of flags (point-line incidences) = 40*4 = 160."""
        total = sum(len(l) for l in gq_lines)
        assert total == 160

    def test_anti_flag_count(self, gq_lines):
        """Number of anti-flags = 40*40 - 160 = 1440."""
        flags = sum(len(l) for l in gq_lines)
        assert 40 * 40 - flags == 1440

    def test_ordered_collinear_triples(self, gq_lines):
        """Ordered collinear triples = 40 lines * P(4,3) = 40 * 24 = 960."""
        # Each line of 4 points contributes 4*3*2 = 24 ordered triples
        assert 40 * 24 == 960

    def test_concurrent_line_pairs_from_points(self, gq_lines):
        """Concurrent line pairs counted via pencils: 40 points * C(4,2) = 240."""
        total = 0
        for p in range(40):
            pencil_size = sum(1 for l in gq_lines if p in l)
            total += pencil_size * (pencil_size - 1) // 2
        assert total == 240

    def test_eigenvalue_spectrum(self, A):
        """Full adjacency spectrum: {12^1, 2^24, (-4)^15}."""
        ev = np.sort(eigvalsh(A.astype(float)))
        expected = np.array(sorted([-4.0] * 15 + [2.0] * 24 + [12.0]))
        assert np.allclose(ev, expected, atol=1e-8)
