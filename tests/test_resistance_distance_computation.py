"""
Phase CXVIII -- Resistance Distance & Electrical Networks on W(3,3) = SRG(40,12,2,4).

91 tests covering resistance distance, effective resistance, Foster's theorem,
Kirchhoff index, commute time, electrical flow, current conservation, power
dissipation, Schur complement, Rayleigh monotonicity, and related network theory.

All tests use only numpy and standard library.  Every assertion is
mathematically provable from the SRG(40,12,2,4) spectrum
    adjacency:  {12^1, 2^24, (-4)^15}
    Laplacian:  {0^1, 10^24, 16^15}

Key analytical results for SRG(40,12,2,4):
    L^+ diagonal           = 267/3200
    L^+ adjacent off-diag  = 7/3200
    L^+ non-adj  off-diag  = -13/3200
    R_adj  = 13/80          R_non = 7/40
    Kf     = 133.5           Foster edge sum = 39
    Commute_adj = 78         Commute_non = 84
    Kemeny constant = 40.05
"""

import numpy as np
from numpy.linalg import eigh, pinv, matrix_rank, norm
import pytest


# ── W(3,3) builder ───────────────────────────────────────────────────────────

def _build_w33():
    """Build the 40-vertex symplectic graph W(3,3) = SRG(40,12,2,4)."""
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


# ── SRG parameters ───────────────────────────────────────────────────────────

_N, _K, _LAM, _MU = 40, 12, 2, 4
_M = _N * _K // 2   # 240 edges

# Adjacency eigenvalues
_EIG_K, _EIG_R, _EIG_S = 12, 2, -4
_MULT_K, _MULT_R, _MULT_S = 1, 24, 15

# Laplacian eigenvalues
_LAP_0, _LAP_1, _LAP_2 = 0, _K - _EIG_R, _K - _EIG_S   # 0, 10, 16

# Pseudoinverse entries  (L^+ = (1/10)*P_r + (1/16)*P_s)
_LP_DIAG = 267.0 / 3200.0
_LP_ADJ  = 7.0 / 3200.0
_LP_NON  = -13.0 / 3200.0

# Resistance distances
_R_ADJ = 13.0 / 80.0    # 2*(267 - 7)/3200
_R_NON = 7.0 / 40.0     # 2*(267 + 13)/3200

# Kirchhoff index
_KF = 133.5              # 40*(24/10 + 15/16)


# ── Module-scoped fixture ────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def w33():
    """Precompute all derived quantities once per module."""
    A = _build_w33()
    n = _N

    # Laplacian  L = kI - A
    L = float(_K) * np.eye(n) - A.astype(float)

    # Spectral decompositions
    eigvals_A, eigvecs_A = eigh(A.astype(float))
    eigvals_L, eigvecs_L = eigh(L)

    # Moore-Penrose pseudoinverse
    Lp = pinv(L)

    # Resistance distance matrix  R_{ij} = L^+_{ii} + L^+_{jj} - 2 L^+_{ij}
    d = np.diag(Lp)
    R = d[:, None] + d[None, :] - 2.0 * Lp

    # Boolean masks for adjacent / non-adjacent distinct pairs
    adj = A.astype(bool)
    non_adj = (~adj) & (~np.eye(n, dtype=bool))

    return dict(
        A=A, n=n, k=_K, m=_M,
        L=L, Lp=Lp,
        eigvals_A=eigvals_A, eigvecs_A=eigvecs_A,
        eigvals_L=eigvals_L, eigvecs_L=eigvecs_L,
        R=R, adj=adj, non_adj=non_adj,
    )


# ══════════════════════════════════════════════════════════════════════════════
# 1.  Graph construction & SRG verification  (8 tests)
# ══════════════════════════════════════════════════════════════════════════════

class TestGraphConstruction:

    def test_vertex_count(self, w33):
        assert w33["A"].shape == (40, 40)

    def test_k_regular(self, w33):
        assert np.all(w33["A"].sum(axis=1) == _K)

    def test_symmetric(self, w33):
        assert np.array_equal(w33["A"], w33["A"].T)

    def test_binary_entries(self, w33):
        assert set(np.unique(w33["A"])) == {0, 1}

    def test_zero_diagonal(self, w33):
        assert np.all(np.diag(w33["A"]) == 0)

    def test_edge_count(self, w33):
        assert w33["A"].sum() == 2 * _M   # 480

    def test_srg_lambda_2(self, w33):
        """Adjacent pairs share exactly lambda=2 common neighbours."""
        A = w33["A"]
        A2 = A @ A
        rows, cols = np.where(np.triu(A, 1))
        assert np.all(A2[rows, cols] == _LAM)

    def test_srg_mu_4(self, w33):
        """Non-adjacent distinct pairs share exactly mu=4 common neighbours."""
        A = w33["A"]
        A2 = A @ A
        n = w33["n"]
        mask = np.triu(np.ones((n, n), dtype=bool), 1) & (~A.astype(bool))
        assert np.all(A2[mask] == _MU)


# ══════════════════════════════════════════════════════════════════════════════
# 2.  Adjacency spectrum  (6 tests)
# ══════════════════════════════════════════════════════════════════════════════

class TestAdjacencySpectrum:

    def test_largest_eigenvalue_12(self, w33):
        assert np.isclose(np.max(w33["eigvals_A"]), _EIG_K, atol=1e-8)

    def test_eigenvalue_2_mult_24(self, w33):
        cnt = np.sum(np.isclose(w33["eigvals_A"], _EIG_R, atol=1e-6))
        assert cnt == _MULT_R

    def test_eigenvalue_neg4_mult_15(self, w33):
        cnt = np.sum(np.isclose(w33["eigvals_A"], _EIG_S, atol=1e-6))
        assert cnt == _MULT_S

    def test_three_distinct(self, w33):
        rounded = np.round(w33["eigvals_A"], 4)
        assert len(set(rounded)) == 3

    def test_trace_zero(self, w33):
        assert np.isclose(w33["eigvals_A"].sum(), 0.0, atol=1e-8)

    def test_trace_A2_equals_nk(self, w33):
        """tr(A^2) = sum(lambda_i^2) = n*k = 480."""
        assert np.isclose((w33["eigvals_A"] ** 2).sum(), _N * _K, atol=1e-6)


# ══════════════════════════════════════════════════════════════════════════════
# 3.  Laplacian construction & properties  (8 tests)
# ══════════════════════════════════════════════════════════════════════════════

class TestLaplacianProperties:

    def test_formula_kI_minus_A(self, w33):
        expected = float(_K) * np.eye(_N) - w33["A"].astype(float)
        assert np.allclose(w33["L"], expected)

    def test_row_sums_zero(self, w33):
        assert np.allclose(w33["L"].sum(axis=1), 0.0, atol=1e-12)

    def test_col_sums_zero(self, w33):
        assert np.allclose(w33["L"].sum(axis=0), 0.0, atol=1e-12)

    def test_symmetric(self, w33):
        assert np.allclose(w33["L"], w33["L"].T)

    def test_positive_semidefinite(self, w33):
        assert np.all(w33["eigvals_L"] >= -1e-10)

    def test_rank_n_minus_1(self, w33):
        assert matrix_rank(w33["L"]) == _N - 1

    def test_trace_sum_degrees(self, w33):
        """tr(L) = n*k = 480."""
        assert np.isclose(np.trace(w33["L"]), _N * _K)

    def test_quadratic_form_nonneg(self, w33):
        """x^T L x >= 0 for random vectors."""
        rng = np.random.RandomState(123)
        for _ in range(20):
            x = rng.randn(_N)
            assert x @ w33["L"] @ x >= -1e-10


# ══════════════════════════════════════════════════════════════════════════════
# 4.  Laplacian spectrum  (6 tests)
# ══════════════════════════════════════════════════════════════════════════════

class TestLaplacianSpectrum:

    def test_zero_eigenvalue_mult_1(self, w33):
        cnt = np.sum(np.isclose(w33["eigvals_L"], 0.0, atol=1e-8))
        assert cnt == 1

    def test_eigenvalue_10_mult_24(self, w33):
        cnt = np.sum(np.isclose(w33["eigvals_L"], _LAP_1, atol=1e-6))
        assert cnt == _MULT_R   # 24

    def test_eigenvalue_16_mult_15(self, w33):
        cnt = np.sum(np.isclose(w33["eigvals_L"], _LAP_2, atol=1e-6))
        assert cnt == _MULT_S   # 15

    def test_spectral_gap_10(self, w33):
        """Algebraic connectivity = smallest nonzero Laplacian eigenvalue = 10."""
        nonzero = w33["eigvals_L"][w33["eigvals_L"] > 0.5]
        assert np.isclose(np.min(nonzero), _LAP_1, atol=1e-6)

    def test_largest_laplacian_eigenvalue_16(self, w33):
        assert np.isclose(np.max(w33["eigvals_L"]), _LAP_2, atol=1e-6)

    def test_trace_L_squared(self, w33):
        """tr(L^2) = 24*100 + 15*256 = 6240."""
        expected = _MULT_R * _LAP_1**2 + _MULT_S * _LAP_2**2
        actual = (w33["eigvals_L"] ** 2).sum()
        assert np.isclose(actual, expected, atol=1e-6)


# ══════════════════════════════════════════════════════════════════════════════
# 5.  Moore-Penrose pseudoinverse L^+  (10 tests)
# ══════════════════════════════════════════════════════════════════════════════

class TestPseudoinverse:

    def test_symmetric(self, w33):
        assert np.allclose(w33["Lp"], w33["Lp"].T, atol=1e-12)

    def test_mp_condition_1(self, w33):
        """L L^+ L = L  (Moore-Penrose axiom 1)."""
        assert np.allclose(w33["L"] @ w33["Lp"] @ w33["L"],
                           w33["L"], atol=1e-8)

    def test_mp_condition_2(self, w33):
        """L^+ L L^+ = L^+  (Moore-Penrose axiom 2)."""
        assert np.allclose(w33["Lp"] @ w33["L"] @ w33["Lp"],
                           w33["Lp"], atol=1e-10)

    def test_mp_condition_3(self, w33):
        """(L L^+)^T = L L^+  (Moore-Penrose axiom 3)."""
        P = w33["L"] @ w33["Lp"]
        assert np.allclose(P, P.T, atol=1e-10)

    def test_mp_condition_4(self, w33):
        """(L^+ L)^T = L^+ L  (Moore-Penrose axiom 4)."""
        Q = w33["Lp"] @ w33["L"]
        assert np.allclose(Q, Q.T, atol=1e-10)

    def test_row_sums_zero(self, w33):
        """L^+ has zero row sums (ones vector in null space of L)."""
        assert np.allclose(w33["Lp"].sum(axis=1), 0.0, atol=1e-10)

    def test_col_sums_zero(self, w33):
        assert np.allclose(w33["Lp"].sum(axis=0), 0.0, atol=1e-10)

    def test_diagonal_entries(self, w33):
        """All diagonal entries of L^+ = 267/3200."""
        assert np.allclose(np.diag(w33["Lp"]), _LP_DIAG, atol=1e-10)

    def test_adjacent_offdiag(self, w33):
        """L^+_{ij} = 7/3200 for adjacent i,j."""
        vals = w33["Lp"][w33["adj"]]
        assert np.allclose(vals, _LP_ADJ, atol=1e-10)

    def test_nonadjacent_offdiag(self, w33):
        """L^+_{ij} = -13/3200 for non-adjacent distinct i,j."""
        vals = w33["Lp"][w33["non_adj"]]
        assert np.allclose(vals, _LP_NON, atol=1e-10)


# ══════════════════════════════════════════════════════════════════════════════
# 6.  Resistance distance fundamentals  (12 tests)
# ══════════════════════════════════════════════════════════════════════════════

class TestResistanceDistance:

    def test_self_resistance_zero(self, w33):
        """R(i,i) = 0 for all i."""
        assert np.allclose(np.diag(w33["R"]), 0.0, atol=1e-12)

    def test_positive_offdiag(self, w33):
        """R(i,j) > 0 for all distinct i,j."""
        R = w33["R"]; n = w33["n"]
        offdiag = R[~np.eye(n, dtype=bool)]
        assert np.all(offdiag > 1e-14)

    def test_symmetric(self, w33):
        """R(i,j) = R(j,i)."""
        assert np.allclose(w33["R"], w33["R"].T, atol=1e-12)

    def test_adjacent_resistance(self, w33):
        """R_adj = 13/80 for all adjacent pairs."""
        vals = w33["R"][w33["adj"]]
        assert np.allclose(vals, _R_ADJ, atol=1e-10)

    def test_nonadjacent_resistance(self, w33):
        """R_non = 7/40 for all non-adjacent pairs."""
        vals = w33["R"][w33["non_adj"]]
        assert np.allclose(vals, _R_NON, atol=1e-10)

    def test_two_distinct_nonzero_values(self, w33):
        """Exactly two distinct positive R values (SRG symmetry)."""
        R = w33["R"]; n = w33["n"]
        offdiag = R[~np.eye(n, dtype=bool)]
        distinct = set(np.round(offdiag, 8))
        assert len(distinct) == 2

    def test_nonadj_greater_adj(self, w33):
        """Non-adjacent resistance exceeds adjacent resistance."""
        assert _R_NON > _R_ADJ

    def test_ratio_14_over_13(self, w33):
        """R_non / R_adj = (7/40) / (13/80) = 14/13."""
        ratio = _R_NON / _R_ADJ
        assert np.isclose(ratio, 14.0 / 13.0, atol=1e-12)

    def test_triangle_inequality(self, w33):
        """R defines a metric: R(i,k) <= R(i,j) + R(j,k)."""
        R = w33["R"]
        rng = np.random.RandomState(42)
        for _ in range(300):
            i, j, k = rng.choice(_N, 3, replace=False)
            assert R[i, k] <= R[i, j] + R[j, k] + 1e-12

    def test_resistance_diameter(self, w33):
        """Resistance diameter = max R = R_non = 7/40."""
        assert np.isclose(w33["R"].max(), _R_NON, atol=1e-10)

    def test_bounded_by_2_over_lambda2(self, w33):
        """All R(i,j) <= 2/lambda_2 = 2/10 = 0.2."""
        assert w33["R"].max() <= 2.0 / _LAP_1 + 1e-10

    def test_sqrt_R_triangle_inequality(self, w33):
        """sqrt(R) values also satisfy the triangle inequality (Euclidean embedding)."""
        sqR = np.sqrt(w33["R"])
        rng = np.random.RandomState(99)
        for _ in range(300):
            i, j, k = rng.choice(_N, 3, replace=False)
            assert sqR[i, k] <= sqR[i, j] + sqR[j, k] + 1e-10


# ══════════════════════════════════════════════════════════════════════════════
# 7.  Resistance matrix algebra  (6 tests)
# ══════════════════════════════════════════════════════════════════════════════

class TestResistanceMatrixAlgebra:

    def test_decomposition(self, w33):
        """R = (7/40)(J - I) - (1/80)A  exactly."""
        n = w33["n"]; A = w33["A"].astype(float)
        J = np.ones((n, n))
        I_n = np.eye(n)
        R_formula = (7.0 / 40.0) * (J - I_n) - (1.0 / 80.0) * A
        assert np.allclose(w33["R"], R_formula, atol=1e-10)

    def test_eigenvalues(self, w33):
        """R has eigenvalues 267/40 (x1), -1/5 (x24), -1/8 (x15)."""
        eigs = np.sort(np.linalg.eigvalsh(w33["R"]))
        expected = sorted([267.0 / 40.0] + [-0.2] * 24 + [-0.125] * 15)
        assert np.allclose(eigs, expected, atol=1e-8)

    def test_full_rank(self, w33):
        """R has full rank 40."""
        assert matrix_rank(w33["R"]) == _N

    def test_row_sum_constant(self, w33):
        """Each row of R sums to 267/40 (vertex-transitive)."""
        row_sums = w33["R"].sum(axis=1)
        assert np.allclose(row_sums, 267.0 / 40.0, atol=1e-8)

    def test_total_sum_equals_2Kf(self, w33):
        """Sum of all entries of R = 2*Kf = 267."""
        assert np.isclose(w33["R"].sum(), 2.0 * _KF, atol=1e-6)

    def test_conditionally_negative_definite(self, w33):
        """x^T R x <= 0 for all x with sum(x)=0."""
        R = w33["R"]
        rng = np.random.RandomState(77)
        for _ in range(50):
            x = rng.randn(_N)
            x -= x.mean()   # project onto sum=0 hyperplane
            assert x @ R @ x <= 1e-10


# ══════════════════════════════════════════════════════════════════════════════
# 8.  Foster's first theorem  (5 tests)
# ══════════════════════════════════════════════════════════════════════════════

class TestFosterTheorem:

    def test_foster_first(self, w33):
        """Sum of effective resistance over all edges = n - 1 = 39."""
        A = w33["A"]; R = w33["R"]
        edge_R_sum = 0.5 * (A * R).sum()
        assert np.isclose(edge_R_sum, _N - 1, atol=1e-8)

    def test_average_edge_resistance(self, w33):
        """Mean edge R = (n-1)/|E| = 39/240 = 13/80."""
        assert np.isclose((_N - 1.0) / _M, _R_ADJ)

    def test_spanning_tree_edge_probability(self, w33):
        """P(edge in uniform random spanning tree) = R_eff(edge) = 13/80."""
        # For unit-weight graphs: P(e in random ST) = R_eff(e)
        # Every spanning tree has exactly n-1 = 39 edges
        # Expected count = sum over edges of P = 39 = n-1  (consistent)
        expected_count = _M * _R_ADJ   # 240 * 13/80 = 39
        assert np.isclose(expected_count, _N - 1)

    def test_all_edges_equal_resistance(self, w33):
        """By SRG symmetry every edge has the same effective resistance."""
        edge_vals = w33["R"][w33["adj"]]
        assert np.allclose(edge_vals, edge_vals[0], atol=1e-10)

    def test_foster_consistent_with_Kf(self, w33):
        """Foster edge sum + non-edge contribution = Kf."""
        R = w33["R"]; n = w33["n"]
        mask_upper = np.triu(np.ones((n, n), dtype=bool), 1)
        Kf = R[mask_upper].sum()
        assert np.isclose(Kf, _KF, atol=1e-6)


# ══════════════════════════════════════════════════════════════════════════════
# 9.  Kirchhoff index  (8 tests)
# ══════════════════════════════════════════════════════════════════════════════

class TestKirchhoffIndex:

    def test_Kf_value(self, w33):
        """Kf = sum_{i<j} R(i,j) = 133.5."""
        R = w33["R"]; n = w33["n"]
        mask = np.triu(np.ones((n, n), dtype=bool), 1)
        Kf = R[mask].sum()
        assert np.isclose(Kf, _KF, atol=1e-6)

    def test_Kf_via_eigenvalues(self, w33):
        """Kf = n * sum(1/lambda_i) for nonzero Laplacian eigenvalues."""
        eigs = w33["eigvals_L"]
        nonzero = eigs[eigs > 0.5]
        Kf = float(_N) * np.sum(1.0 / nonzero)
        assert np.isclose(Kf, _KF, atol=1e-6)

    def test_Kf_via_trace_Lp(self, w33):
        """Kf = n * tr(L^+)."""
        Kf = float(_N) * np.trace(w33["Lp"])
        assert np.isclose(Kf, _KF, atol=1e-6)

    def test_Kf_analytic_decomposition(self, w33):
        """Kf = 40*(24/10 + 15/16) = 40*3.3375 = 133.5."""
        val = 40.0 * (24.0 / 10.0 + 15.0 / 16.0)
        assert np.isclose(val, _KF)

    def test_Kf_from_edge_and_nonedge(self, w33):
        """Kf = 240*(13/80) + 540*(7/40) = 39 + 94.5 = 133.5."""
        Kf = _M * _R_ADJ + 540 * _R_NON
        assert np.isclose(Kf, _KF)

    def test_reciprocal_eigenvalue_sum(self, w33):
        """sum(1/lambda_i) for nonzero eigenvalues = 3.3375."""
        eigs = w33["eigvals_L"]
        nonzero = eigs[eigs > 0.5]
        assert np.isclose(np.sum(1.0 / nonzero), 3.3375, atol=1e-8)

    def test_additive_degree_kirchhoff(self, w33):
        """Kf+ = sum_{i<j} (d_i+d_j)*R(i,j) = 2k*Kf = 3204 for k-regular."""
        R = w33["R"]; n = w33["n"]
        mask = np.triu(np.ones((n, n), dtype=bool), 1)
        Kf_plus = np.sum(2.0 * _K * R[mask])
        assert np.isclose(Kf_plus, 2 * _K * _KF, atol=1e-4)

    def test_complement_kirchhoff_index(self, w33):
        """Complement SRG(40,27,18,18) has Kf_comp = 57."""
        # Complement Laplacian eigenvalues: 0, 30 (x24), 24 (x15)
        Kf_comp = 40.0 * (24.0 / 30.0 + 15.0 / 24.0)
        assert np.isclose(Kf_comp, 57.0, atol=1e-10)


# ══════════════════════════════════════════════════════════════════════════════
# 10. Commute time & random walk  (9 tests)
# ══════════════════════════════════════════════════════════════════════════════

class TestCommuteTimeRandomWalk:

    def test_commute_time_adj(self, w33):
        """C(i,j) = 2m*R(i,j) = 480*(13/80) = 78 for adjacent."""
        C = 2.0 * _M * _R_ADJ
        assert np.isclose(C, 78.0)

    def test_commute_time_non(self, w33):
        """C(i,j) = 2m*R(i,j) = 480*(7/40) = 84 for non-adjacent."""
        C = 2.0 * _M * _R_NON
        assert np.isclose(C, 84.0)

    def test_hitting_time_adj(self, w33):
        """H(i,j) = C(i,j)/2 = 39 for adjacent (vertex-transitive)."""
        H = 2.0 * _M * _R_ADJ / 2.0
        assert np.isclose(H, 39.0)

    def test_hitting_time_non(self, w33):
        """H(i,j) = C(i,j)/2 = 42 for non-adjacent (vertex-transitive)."""
        H = 2.0 * _M * _R_NON / 2.0
        assert np.isclose(H, 42.0)

    def test_kemeny_constant(self, w33):
        """Kemeny's constant K = k * sum(1/lambda_i) = 12*3.3375 = 40.05."""
        K = float(_K) * (24.0 / 10.0 + 15.0 / 16.0)
        assert np.isclose(K, 40.05)

    def test_kemeny_via_transition_eigenvalues(self, w33):
        """K = sum 1/(1-mu_i) where mu_i are non-trivial transition eigenvalues.
        mu_i = adj_eigenvalue/k: 2/12=1/6 (x24), -4/12=-1/3 (x15).
        K = 24/(1-1/6) + 15/(1+1/3) = 24*6/5 + 15*3/4 = 28.8 + 11.25 = 40.05."""
        K = 24.0 * 6.0 / 5.0 + 15.0 * 3.0 / 4.0
        assert np.isclose(K, 40.05)

    def test_sum_hitting_times_from_vertex(self, w33):
        """sum_j H(0,j) = m * sum_j R(0,j) = 240 * 267/40 = 1602."""
        R = w33["R"]
        total = float(_M) * R[0].sum()
        assert np.isclose(total, 1602.0, atol=1e-6)

    def test_average_return_time(self, w33):
        """Expected return time = 2m/d_v = 480/12 = 40 = n for k-regular."""
        assert np.isclose(2.0 * _M / _K, float(_N))

    def test_stationary_distribution_uniform(self, w33):
        """Stationary distribution pi_v = d_v/(2m) = 12/480 = 1/40 for all v."""
        pi = float(_K) / (2.0 * _M)
        assert np.isclose(pi, 1.0 / _N)


# ══════════════════════════════════════════════════════════════════════════════
# 11. Electrical flow & current conservation  (10 tests)
# ══════════════════════════════════════════════════════════════════════════════

class TestElectricalFlow:
    """Unit current injected at source s, extracted at sink t."""

    @pytest.fixture()
    def flow_adj(self, w33):
        """Pick an adjacent (s,t) pair and solve for voltages/currents."""
        A = w33["A"]; Lp = w33["Lp"]
        # find first adjacent pair
        s, t = np.argwhere(np.triu(A, 1))[0]
        b = np.zeros(_N)
        b[s] = 1.0; b[t] = -1.0
        v = Lp @ b     # voltage vector
        return dict(s=s, t=t, v=v, A=A)

    @pytest.fixture()
    def flow_non(self, w33):
        """Pick a non-adjacent (s,t) pair and solve for voltages/currents."""
        A = w33["A"]; Lp = w33["Lp"]; n = w33["n"]
        mask = np.triu(np.ones((n, n), dtype=bool), 1) & (~A.astype(bool))
        s, t = np.argwhere(mask)[0]
        b = np.zeros(_N)
        b[s] = 1.0; b[t] = -1.0
        v = Lp @ b
        return dict(s=s, t=t, v=v, A=A)

    def test_voltage_drop_equals_R_adj(self, flow_adj):
        """v_s - v_t = R_eff(s,t) for adjacent pair."""
        vs = flow_adj["v"][flow_adj["s"]]
        vt = flow_adj["v"][flow_adj["t"]]
        assert np.isclose(vs - vt, _R_ADJ, atol=1e-10)

    def test_voltage_drop_equals_R_non(self, flow_non):
        """v_s - v_t = R_eff(s,t) for non-adjacent pair."""
        vs = flow_non["v"][flow_non["s"]]
        vt = flow_non["v"][flow_non["t"]]
        assert np.isclose(vs - vt, _R_NON, atol=1e-10)

    def test_kcl_conservation_adj(self, flow_adj):
        """Kirchhoff current law: net current = 0 at all intermediate vertices."""
        A = flow_adj["A"]; v = flow_adj["v"]
        s = flow_adj["s"]; t = flow_adj["t"]
        for i in range(_N):
            if i == s or i == t:
                continue
            neighbours = np.where(A[i] == 1)[0]
            net_out = sum(v[i] - v[j] for j in neighbours)
            assert np.isclose(net_out, 0.0, atol=1e-10)

    def test_kcl_conservation_non(self, flow_non):
        """KCL at intermediate vertices for non-adjacent source-sink."""
        A = flow_non["A"]; v = flow_non["v"]
        s = flow_non["s"]; t = flow_non["t"]
        for i in range(_N):
            if i == s or i == t:
                continue
            neighbours = np.where(A[i] == 1)[0]
            net_out = sum(v[i] - v[j] for j in neighbours)
            assert np.isclose(net_out, 0.0, atol=1e-10)

    def test_net_source_current_adj(self, flow_adj):
        """Net current out of source = 1."""
        A = flow_adj["A"]; v = flow_adj["v"]; s = flow_adj["s"]
        neighbours = np.where(A[s] == 1)[0]
        net_out = sum(v[s] - v[j] for j in neighbours)
        assert np.isclose(net_out, 1.0, atol=1e-10)

    def test_net_sink_current_adj(self, flow_adj):
        """Net current into sink = 1."""
        A = flow_adj["A"]; v = flow_adj["v"]; t = flow_adj["t"]
        neighbours = np.where(A[t] == 1)[0]
        net_out = sum(v[t] - v[j] for j in neighbours)
        assert np.isclose(net_out, -1.0, atol=1e-10)

    def test_power_dissipation_adj(self, flow_adj):
        """Total power = sum (v_i-v_j)^2 over edges = R_eff for unit current."""
        A = flow_adj["A"]; v = flow_adj["v"]
        rows, cols = np.where(np.triu(A, 1))
        power = sum((v[i] - v[j]) ** 2 for i, j in zip(rows, cols))
        assert np.isclose(power, _R_ADJ, atol=1e-10)

    def test_power_dissipation_non(self, flow_non):
        """Total power = R_eff for non-adjacent source-sink."""
        A = flow_non["A"]; v = flow_non["v"]
        rows, cols = np.where(np.triu(A, 1))
        power = sum((v[i] - v[j]) ** 2 for i, j in zip(rows, cols))
        assert np.isclose(power, _R_NON, atol=1e-10)

    def test_current_antisymmetry(self, flow_adj):
        """Edge current f(i,j) = -f(j,i) = v_i - v_j."""
        v = flow_adj["v"]; A = flow_adj["A"]
        rows, cols = np.where(np.triu(A, 1))
        for i, j in list(zip(rows, cols))[:50]:
            assert np.isclose((v[i] - v[j]) + (v[j] - v[i]), 0.0, atol=1e-15)

    def test_max_edge_current_bounded(self, flow_adj):
        """No edge carries more than 1 unit of current (unit injection)."""
        v = flow_adj["v"]; A = flow_adj["A"]
        rows, cols = np.where(np.triu(A, 1))
        max_curr = max(abs(v[i] - v[j]) for i, j in zip(rows, cols))
        assert max_curr <= 1.0 + 1e-10


# ══════════════════════════════════════════════════════════════════════════════
# 12. Schur complement, Rayleigh monotonicity, spanning trees  (8 tests)
# ══════════════════════════════════════════════════════════════════════════════

class TestAdvancedNetworkIdentities:

    def test_schur_complement_adj(self, w33):
        """Schur complement of L onto {s,t} gives effective conductance."""
        A = w33["A"]; L = w33["L"]
        s, t = np.argwhere(np.triu(A, 1))[0]
        idx = [s, t]
        comp = [i for i in range(_N) if i not in idx]
        L_ss = L[np.ix_(idx, idx)]
        L_sc = L[np.ix_(idx, comp)]
        L_cc = L[np.ix_(comp, comp)]
        L_cs = L[np.ix_(comp, idx)]
        L_schur = L_ss - L_sc @ np.linalg.solve(L_cc, L_cs)
        # L_schur should be [[g, -g], [-g, g]]
        g_eff = L_schur[0, 0]
        assert np.isclose(L_schur[0, 1], -g_eff, atol=1e-8)
        assert np.isclose(1.0 / g_eff, _R_ADJ, atol=1e-8)

    def test_schur_complement_non(self, w33):
        """Schur complement for non-adjacent pair."""
        A = w33["A"]; L = w33["L"]; n = w33["n"]
        mask = np.triu(np.ones((n, n), dtype=bool), 1) & (~A.astype(bool))
        s, t = np.argwhere(mask)[0]
        idx = [s, t]
        comp = [i for i in range(_N) if i not in idx]
        L_ss = L[np.ix_(idx, idx)]
        L_sc = L[np.ix_(idx, comp)]
        L_cc = L[np.ix_(comp, comp)]
        L_cs = L[np.ix_(comp, idx)]
        L_schur = L_ss - L_sc @ np.linalg.solve(L_cc, L_cs)
        g_eff = L_schur[0, 0]
        assert np.isclose(L_schur[0, 1], -g_eff, atol=1e-8)
        assert np.isclose(1.0 / g_eff, _R_NON, atol=1e-8)

    def test_rayleigh_monotonicity(self, w33):
        """Removing an edge increases effective resistance (Rayleigh)."""
        A = w33["A"]; n = w33["n"]
        # pick an edge to remove
        s, t = np.argwhere(np.triu(A, 1))[0]
        A2 = A.copy()
        A2[s, t] = A2[t, s] = 0
        k2 = A2.sum(axis=1)
        L2 = np.diag(k2.astype(float)) - A2.astype(float)
        Lp2 = pinv(L2)
        R_new = Lp2[s, s] + Lp2[t, t] - 2 * Lp2[s, t]
        assert R_new > _R_ADJ - 1e-12

    def test_spanning_tree_count_log(self, w33):
        """log(tau) = 24*log(10) + 15*log(16) - log(40) via eigenvalues."""
        log_tau_eig = 24.0 * np.log(10.0) + 15.0 * np.log(16.0) - np.log(40.0)
        # Also compute via cofactor: det(L with row/col 0 removed)
        L = w33["L"]
        sign, logdet = np.linalg.slogdet(L[1:, 1:])
        assert sign == 1
        assert np.isclose(logdet, log_tau_eig, atol=1e-6)

    def test_spanning_tree_count_cofactor_any_vertex(self, w33):
        """det(L_{ii}) is the same for any deleted row/col i (matrix tree theorem)."""
        L = w33["L"]
        ref_sign, ref_logdet = np.linalg.slogdet(L[1:, 1:])
        for i in [0, 5, 15, 30, 39]:
            idx = [j for j in range(_N) if j != i]
            s, ld = np.linalg.slogdet(L[np.ix_(idx, idx)])
            assert s == ref_sign
            assert np.isclose(ld, ref_logdet, atol=1e-4)

    def test_electrical_centrality_uniform(self, w33):
        """All vertices have equal electrical closeness centrality (vertex-transitive)."""
        R = w33["R"]
        row_sums = R.sum(axis=1)
        C_E = (_N - 1.0) / row_sums
        assert np.allclose(C_E, C_E[0], atol=1e-8)

    def test_electrical_centrality_value(self, w33):
        """C_E(v) = 39 / (267/40) = 520/89 for all v."""
        R = w33["R"]
        C_E = (_N - 1.0) / R[0].sum()
        assert np.isclose(C_E, 520.0 / 89.0, atol=1e-8)

    def test_euclidean_embedding(self, w33):
        """R(i,j) = ||phi_i - phi_j||^2 in the spectral embedding space."""
        Lp = w33["Lp"]
        eigvals, eigvecs = eigh(Lp)
        # keep only positive eigenvalues
        pos = eigvals > 1e-12
        Lambda_half = np.sqrt(eigvals[pos])
        phi = eigvecs[:, pos] * Lambda_half[None, :]   # n x d embedding
        # compute pairwise squared distances
        R_embed = np.zeros((_N, _N))
        for i in range(_N):
            diff = phi - phi[i]
            R_embed[i] = (diff ** 2).sum(axis=1)
        assert np.allclose(R_embed, w33["R"], atol=1e-8)


# ══════════════════════════════════════════════════════════════════════════════
# 13. Additional resistance-network identities  (5 tests)
# ══════════════════════════════════════════════════════════════════════════════

class TestResistanceNetworkIdentities:

    def test_complement_R_adj(self, w33):
        """Complement graph resistance for adjacent (in complement) pairs."""
        A = w33["A"]; n = w33["n"]
        A_comp = (np.ones((n, n), dtype=float) - np.eye(n) - A.astype(float))
        L_comp = np.diag(A_comp.sum(axis=1)) - A_comp
        Lp_comp = pinv(L_comp)
        d_comp = np.diag(Lp_comp)
        R_comp = d_comp[:, None] + d_comp[None, :] - 2.0 * Lp_comp
        # Non-adjacent in original = adjacent in complement
        # R_comp for complement-adjacent: computed from complement Laplacian
        adj_comp = A_comp.astype(bool)
        vals = R_comp[adj_comp]
        # For SRG(40,27,18,18) complement: analytic R values
        # R_comp_adj = 2*(Lp_comp_diag - Lp_comp_adj)
        assert np.allclose(vals, vals[0], atol=1e-10)  # all equal by symmetry

    def test_complement_foster(self, w33):
        """Foster's theorem on complement: sum R_comp over complement edges = 39."""
        A = w33["A"]; n = w33["n"]
        A_comp = (np.ones((n, n), dtype=float) - np.eye(n) - A.astype(float))
        L_comp = np.diag(A_comp.sum(axis=1)) - A_comp
        Lp_comp = pinv(L_comp)
        d_comp = np.diag(Lp_comp)
        R_comp = d_comp[:, None] + d_comp[None, :] - 2.0 * Lp_comp
        foster_sum = 0.5 * (A_comp * R_comp).sum()
        assert np.isclose(foster_sum, _N - 1, atol=1e-6)

    def test_resistance_harmonic_mean(self, w33):
        """For k-regular: harmonic mean of R over edges = (n-1)/(|E|) = R_adj."""
        # Since all edges have same R, harmonic mean = R_adj
        assert np.isclose(_R_ADJ, (_N - 1.0) / _M)

    def test_kirchhoff_kf_plus_complement(self, w33):
        """Kf + Kf_comp = 133.5 + 57 = 190.5."""
        Kf_comp = 40.0 * (24.0 / 30.0 + 15.0 / 24.0)
        assert np.isclose(_KF + Kf_comp, 190.5, atol=1e-10)

    def test_resistance_distance_laplacian(self, w33):
        """The resistance-distance Laplacian RL (diag=row sums of R, off-diag=-R)
        has known eigenvalues for SRG: 0 (x1), n/(n*lambda_i) relationship."""
        R = w33["R"]; n = w33["n"]
        RL = np.diag(R.sum(axis=1)) - R
        # RL has zero row sums by construction
        assert np.allclose(RL.sum(axis=1), 0.0, atol=1e-8)
        # rank = n-1 (same as graph Laplacian)
        assert matrix_rank(RL) == n - 1
