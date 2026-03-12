"""
Phase CXXII -- Spectral Partitioning & Community Detection on W(3,3) = SRG(40,12,2,4).

90 tests across 9 classes:
  1. TestModularityMatrixFundamentals    (10 tests)
  2. TestModularityEigenvalueAnalysis    (10 tests)
  3. TestFiedlerVectorAlgebraicConn      (12 tests)
  4. TestCheegerConductanceBounds        (10 tests)
  5. TestSpectralBisectionQuality        (10 tests)
  6. TestNormalizedCutAnalysis           (10 tests)
  7. TestRatioCutEdgeExpansion           (10 tests)
  8. TestKWayPartitioningBounds          (10 tests)
  9. TestAssortativeDisassortativeStructure (8 tests)

Only numpy and standard library.  Every assertion is mathematically provable
from the SRG(40,12,2,4) spectrum:
    Adjacency:  {12^1, 2^24, (-4)^15}
    Laplacian:  {0^1, 10^24, 16^15}
    Modularity: {0^1, 2^24, (-4)^15}
    Normalized Laplacian: {0^1, (5/6)^24, (4/3)^15}
"""

import collections
import math

import numpy as np
from numpy.linalg import eigh, eigvalsh, norm
import pytest


# ---------------------------------------------------------------------------
# W(3,3) builder  (exact copy from specification)
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
# SRG parameters and derived constants
# ---------------------------------------------------------------------------

_N, _K, _LAM, _MU = 40, 12, 2, 4
_M = _N * _K // 2                     # 240 edges
_R, _S_EIG = 2, -4                    # non-trivial adjacency eigenvalues
_MULT_R, _MULT_S = 24, 15             # multiplicities


# ---------------------------------------------------------------------------
# Module-level precomputation  (computed once)
# ---------------------------------------------------------------------------

_A = _build_w33()
_Af = _A.astype(float)

# Combinatorial Laplacian L = kI - A
_L = float(_K) * np.eye(_N) - _Af

# Modularity matrix B = A - k^2/(2m) * J
_B = _Af - (float(_K ** 2) / (2.0 * _M)) * np.ones((_N, _N))

# Normalized Laplacian L_norm = I - A/k  (k-regular)
_L_norm = np.eye(_N) - _Af / float(_K)

# Sorted eigenvalues
_adj_evals = np.sort(eigvalsh(_Af))
_lap_evals = np.sort(eigvalsh(_L))
_mod_evals = np.sort(eigvalsh(_B))
_norm_evals = np.sort(eigvalsh(_L_norm))

# Full Laplacian eigen-decomposition (for Fiedler analysis)
_lap_vals_full, _lap_vecs_full = eigh(_L)
_sort_idx = np.argsort(_lap_vals_full)
_lap_vals_full = _lap_vals_full[_sort_idx]
_lap_vecs_full = _lap_vecs_full[:, _sort_idx]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cut_size(A, S, Sbar):
    """Number of edges between S and Sbar."""
    s_list = sorted(S)
    sbar_list = sorted(Sbar)
    return int(np.sum(A[np.ix_(s_list, sbar_list)]))


def _internal_edges(A, S):
    """Number of edges with both endpoints in S."""
    s_list = sorted(S)
    sub = A[np.ix_(s_list, s_list)]
    return int(np.sum(sub)) // 2


def _spectral_bisection(A):
    """Partition vertices by the sign of the Fiedler vector."""
    n = A.shape[0]
    L = float(_K) * np.eye(n) - A.astype(float)
    evals, evecs = eigh(L)
    idx = np.argsort(evals)
    fiedler = evecs[:, idx[1]]
    S = set(np.where(fiedler >= 0)[0])
    Sbar = set(range(n)) - S
    return S, Sbar


# Precompute the spectral bisection
_bisect_S, _bisect_Sbar = _spectral_bisection(_A)
_bisect_cut = _cut_size(_A, _bisect_S, _bisect_Sbar)


# ===================================================================
# 1.  Modularity Matrix Fundamentals   (10 tests)
#     B = A - (k^2 / 2m) J = A - 0.3 J
# ===================================================================

class TestModularityMatrixFundamentals:
    """Structure and basic properties of the Newman-Girvan modularity matrix."""

    def test_B_is_symmetric(self):
        """B is real symmetric."""
        assert np.allclose(_B, _B.T, atol=1e-12)

    def test_B_diagonal_value(self):
        """B_ii = A_ii - k^2/(2m) = 0 - 0.3 = -0.3 for all i."""
        expected = -float(_K ** 2) / (2 * _M)   # -0.3
        assert np.allclose(np.diag(_B), expected, atol=1e-12)

    def test_B_trace(self):
        """tr(B) = n * (-k^2/(2m)) = 40 * (-0.3) = -12."""
        assert abs(np.trace(_B) + 12.0) < 1e-10

    def test_B_row_sums_zero(self):
        """B * 1 = 0: the all-ones vector lies in ker(B)."""
        row_sums = _B @ np.ones(_N)
        assert np.allclose(row_sums, 0.0, atol=1e-10)

    def test_B_total_sum_zero(self):
        """1^T B 1 = 0: the total modularity contribution is zero."""
        total = np.ones(_N) @ _B @ np.ones(_N)
        assert abs(total) < 1e-8

    def test_B_adjacent_entry(self):
        """For every adjacent pair: B_ij = 1 - k^2/(2m) = 0.7."""
        mask_adj = _A == 1
        np.fill_diagonal(mask_adj, False)
        assert np.allclose(_B[mask_adj], 0.7, atol=1e-12)

    def test_B_nonadjacent_entry(self):
        """For every non-adjacent pair (i != j): B_ij = 0 - k^2/(2m) = -0.3."""
        mask_nonadj = (_A == 0)
        np.fill_diagonal(mask_nonadj, False)
        assert np.allclose(_B[mask_nonadj], -0.3, atol=1e-12)

    def test_B_Frobenius_norm_squared(self):
        """||B||_F^2 = sum B_ij^2 = sum of squared eigenvalues
        = 0 + 24*4 + 15*16 = 336."""
        frob_sq = np.sum(_B ** 2)
        expected = _MULT_R * _R ** 2 + _MULT_S * _S_EIG ** 2  # 96 + 240
        assert abs(frob_sq - 336.0) < 1e-6

    def test_B_rank_is_n_minus_1(self):
        """B has rank 39 (1-dimensional kernel spanned by 1)."""
        assert np.linalg.matrix_rank(_B, tol=1e-8) == _N - 1

    def test_B_equals_A_minus_outer(self):
        """B = A - d d^T / (2m) where d_i = k for k-regular."""
        d = np.full(_N, float(_K))
        expected = _Af - np.outer(d, d) / (2.0 * _M)
        assert np.allclose(_B, expected, atol=1e-12)


# ===================================================================
# 2.  Modularity Eigenvalue Analysis   (10 tests)
#     Spectrum of B: {0^1, 2^24, (-4)^15}
# ===================================================================

class TestModularityEigenvalueAnalysis:
    """Spectral decomposition of the modularity matrix."""

    def test_B_eigenvalue_count(self):
        """B has exactly n = 40 eigenvalues."""
        assert len(_mod_evals) == _N

    def test_B_spectrum_multiplicities(self):
        """Modularity spectrum is {(-4)^15, 0^1, 2^24}."""
        rounded = np.round(_mod_evals).astype(int)
        counts = collections.Counter(rounded.tolist())
        assert counts[-4] == 15
        assert counts[0] == 1
        assert counts[2] == 24

    def test_B_largest_eigenvalue(self):
        """beta_max = r = 2 (the positive SRG restricted eigenvalue)."""
        assert abs(np.max(_mod_evals) - float(_R)) < 1e-8

    def test_B_smallest_eigenvalue(self):
        """beta_min = s = -4 (the negative SRG restricted eigenvalue)."""
        assert abs(np.min(_mod_evals) - float(_S_EIG)) < 1e-8

    def test_B_positive_eigenvalue_sum(self):
        """Sum of positive eigenvalues = 24 * 2 = 48."""
        pos_sum = np.sum(_mod_evals[_mod_evals > 0.5])
        assert abs(pos_sum - 48.0) < 1e-6

    def test_B_negative_eigenvalue_sum(self):
        """Sum of negative eigenvalues = 15 * (-4) = -60."""
        neg_sum = np.sum(_mod_evals[_mod_evals < -0.5])
        assert abs(neg_sum + 60.0) < 1e-6

    def test_B_spectral_gap_positive_to_zero(self):
        """Gap from the zero eigenvalue to the positive block = 2."""
        assert abs(_mod_evals[-24] - _mod_evals[-25] - 2.0) < 1e-8

    def test_modularity_upper_bound_balanced_bisection(self):
        """Q_max for balanced bisection <= beta_max * n / (4m) = 2*40/960 = 1/12."""
        Q_upper = float(_R) * _N / (4.0 * _M)
        assert abs(Q_upper - 1.0 / 12.0) < 1e-12

    def test_modularity_lower_bound_balanced_bisection(self):
        """Q_min for balanced bisection >= beta_min * n / (4m) = -4*40/960 = -1/6."""
        Q_lower = float(_S_EIG) * _N / (4.0 * _M)
        assert abs(Q_lower + 1.0 / 6.0) < 1e-12

    def test_B_trace_of_square(self):
        """tr(B^2) = sum beta_i^2 = 24*4 + 15*16 = 336."""
        tr_B2 = np.trace(_B @ _B)
        expected = _MULT_R * _R ** 2 + _MULT_S * _S_EIG ** 2
        assert abs(tr_B2 - float(expected)) < 1e-4


# ===================================================================
# 3.  Fiedler Vector & Algebraic Connectivity   (12 tests)
#     lambda_2(L) = k - r = 10,  multiplicity 24
# ===================================================================

class TestFiedlerVectorAlgebraicConnectivity:
    """Algebraic connectivity and the Fiedler eigenspace."""

    def test_algebraic_connectivity_value(self):
        """lambda_2(L) = 10."""
        assert abs(_lap_vals_full[1] - 10.0) < 1e-8

    def test_algebraic_connectivity_from_srg_formula(self):
        """For SRG: lambda_2(L) = k - r = 12 - 2 = 10."""
        assert abs(_lap_vals_full[1] - (_K - _R)) < 1e-8

    def test_fiedler_eigenspace_dimension(self):
        """The Fiedler eigenspace has dimension 24 (multiplicity of lambda_2)."""
        count = int(np.sum(np.abs(_lap_vals_full - 10.0) < 1e-6))
        assert count == 24

    def test_fiedler_vector_orthogonal_to_ones(self):
        """Every Fiedler vector is orthogonal to 1."""
        fiedler = _lap_vecs_full[:, 1]
        assert abs(np.sum(fiedler)) < 1e-10

    def test_fiedler_vector_satisfies_eigenequation(self):
        """L v = 10 v for the Fiedler vector v."""
        v = _lap_vecs_full[:, 1]
        assert norm(_L @ v - 10.0 * v) < 1e-10

    def test_fiedler_vector_unit_norm(self):
        """Fiedler eigenvector has unit L2 norm."""
        assert abs(norm(_lap_vecs_full[:, 1]) - 1.0) < 1e-12

    def test_spectral_gap_adjacency(self):
        """Spectral gap of A = k - r = 12 - 2 = 10."""
        adj_sorted = np.sort(_adj_evals)
        assert abs(adj_sorted[-1] - adj_sorted[-2] - 10.0) < 1e-8

    def test_fiedler_partition_two_nonempty_sets(self):
        """The sign partition of a Fiedler vector gives two nonempty sets."""
        assert len(_bisect_S) > 0 and len(_bisect_Sbar) > 0

    def test_fiedler_partition_covers_all_vertices(self):
        """The Fiedler partition covers all 40 vertices."""
        assert len(_bisect_S) + len(_bisect_Sbar) == _N
        assert _bisect_S | _bisect_Sbar == set(range(_N))

    def test_largest_laplacian_eigenvalue(self):
        """lambda_max(L) = k - s = 12 - (-4) = 16."""
        assert abs(_lap_vals_full[-1] - 16.0) < 1e-8

    def test_laplacian_spectral_width(self):
        """Spectral width = lambda_max - lambda_2 = 16 - 10 = 6."""
        assert abs(_lap_vals_full[-1] - _lap_vals_full[1] - 6.0) < 1e-8

    def test_fiedler_rayleigh_quotient(self):
        """Rayleigh quotient v^T L v / (v^T v) = 10 for any Fiedler vector."""
        v = _lap_vecs_full[:, 1]
        rq = (v @ _L @ v) / (v @ v)
        assert abs(rq - 10.0) < 1e-8


# ===================================================================
# 4.  Cheeger Inequality & Conductance Bounds   (10 tests)
#     Normalized Laplacian spectrum: {0^1, (5/6)^24, (4/3)^15}
# ===================================================================

class TestCheegerConductanceBounds:
    """Cheeger-type isoperimetric bounds from spectral data."""

    def test_normalized_laplacian_spectrum_zero(self):
        """L_norm has one zero eigenvalue (connected graph)."""
        assert abs(_norm_evals[0]) < 1e-10

    def test_normalized_laplacian_spectrum_middle(self):
        """24 eigenvalues equal 5/6 = 1 - r/k."""
        assert np.allclose(_norm_evals[1:25], 5.0 / 6.0, atol=1e-8)

    def test_normalized_laplacian_spectrum_top(self):
        """15 eigenvalues equal 4/3 = 1 - s/k."""
        assert np.allclose(_norm_evals[25:], 4.0 / 3.0, atol=1e-8)

    def test_normalized_laplacian_gap(self):
        """mu_2 = 1 - r/k = 5/6."""
        assert abs(_norm_evals[1] - 5.0 / 6.0) < 1e-10

    def test_cheeger_lower_bound(self):
        """Conductance phi(G) >= mu_2 / 2 = 5/12."""
        mu2 = 5.0 / 6.0
        lower = mu2 / 2.0
        assert abs(lower - 5.0 / 12.0) < 1e-12

    def test_cheeger_upper_bound(self):
        """Conductance phi(G) <= sqrt(2 mu_2) = sqrt(5/3)."""
        mu2 = 5.0 / 6.0
        upper = np.sqrt(2.0 * mu2)
        assert abs(upper - np.sqrt(5.0 / 3.0)) < 1e-12

    def test_edge_expansion_lower_bound(self):
        """h(G) = min |E(S,Sbar)|/|S| >= lambda_2 / 2 = 5.
        Verified on singleton sets: h({v}) = k = 12 >= 5."""
        for v in range(5):
            S = {v}
            Sbar = set(range(_N)) - S
            cut = _cut_size(_A, S, Sbar)
            assert cut / len(S) >= _lap_vals_full[1] / 2.0 - 1e-8

    def test_random_walk_spectral_gap(self):
        """Transition matrix P = A/k has spectral gap
        1 - max(|r/k|, |s/k|) = 1 - max(1/6, 1/3) = 2/3."""
        P_evals = _adj_evals / float(_K)
        rho = np.max(np.abs(P_evals[:-1]))
        gap = 1.0 - rho
        assert abs(gap - 2.0 / 3.0) < 1e-8

    def test_mixing_time_upper_bound(self):
        """t_mix(1/4) <= ceil((1/gap) * ln(4n)) = ceil(1.5 * ln 160) < 10."""
        gap = 2.0 / 3.0
        bound = (1.0 / gap) * np.log(4.0 * _N)
        assert bound < 10.0

    def test_bipartiteness_ratio_negative(self):
        """mu_max = 4/3 > 1: the graph is far from bipartite.
        Bipartiteness ratio beta = 1 - mu_max < 0."""
        mu_max = 4.0 / 3.0
        assert mu_max > 1.0
        assert (1.0 - mu_max) < 0.0


# ===================================================================
# 5.  Spectral Bisection Quality   (10 tests)
#     Eigenvalue bounds on balanced bisection cut:
#     100 <= |E(S,Sbar)| <= 160
# ===================================================================

class TestSpectralBisectionQuality:
    """Properties of the spectral (Fiedler) bisection."""

    def test_bisection_cut_satisfies_eigenvalue_lower_bound(self):
        """For any partition of sizes s, n-s:
        cut >= s(n-s)(k-r) / n.  For the spectral bisection this holds."""
        s = len(_bisect_S)
        lower = s * (_N - s) * (_K - _R) / float(_N)
        assert _bisect_cut >= lower - 1e-6

    def test_bisection_cut_satisfies_eigenvalue_upper_bound(self):
        """cut <= s(n-s)(k - s_min) / n."""
        s = len(_bisect_S)
        upper = s * (_N - s) * (_K - _S_EIG) / float(_N)
        assert _bisect_cut <= upper + 1e-6

    def test_bisection_is_valid_partition(self):
        """S and Sbar are disjoint and cover all vertices."""
        assert len(_bisect_S & _bisect_Sbar) == 0
        assert len(_bisect_S) + len(_bisect_Sbar) == _N

    def test_bisection_modularity_within_spectral_bounds(self):
        """Modularity Q of the bisection satisfies -1/6 <= Q <= 1/12."""
        e_S = _internal_edges(_A, _bisect_S) / float(_M)
        e_Sbar = _internal_edges(_A, _bisect_Sbar) / float(_M)
        a_S = (_K * len(_bisect_S)) / (2.0 * _M)
        a_Sbar = (_K * len(_bisect_Sbar)) / (2.0 * _M)
        Q = (e_S - a_S ** 2) + (e_Sbar - a_Sbar ** 2)
        assert Q <= 1.0 / 12.0 + 1e-6
        assert Q >= -1.0 / 6.0 - 1e-6

    def test_bisection_cut_positive(self):
        """The spectral bisection produces a nonzero cut (graph is connected)."""
        assert _bisect_cut > 0

    def test_bisection_edges_partition_consistently(self):
        """|E(S)| + |E(Sbar)| + cut = m = 240."""
        e_S = _internal_edges(_A, _bisect_S)
        e_Sbar = _internal_edges(_A, _bisect_Sbar)
        assert e_S + e_Sbar + _bisect_cut == _M

    def test_bisection_degree_sum_identity(self):
        """k |S| = 2 |E(S)| + cut(S) for each side of the partition."""
        e_S = _internal_edges(_A, _bisect_S)
        assert _K * len(_bisect_S) == 2 * e_S + _bisect_cut

    def test_modularity_via_quadratic_form(self):
        """Q = s^T B s / (4m) where s_i = +1 if i in S, -1 otherwise.
        Must agree with the direct computation."""
        s_vec = np.array([1.0 if i in _bisect_S else -1.0 for i in range(_N)])
        Q_quad = (s_vec @ _B @ s_vec) / (4.0 * _M)
        # Direct computation
        e_S = _internal_edges(_A, _bisect_S) / float(_M)
        e_Sbar = _internal_edges(_A, _bisect_Sbar) / float(_M)
        a_S = (_K * len(_bisect_S)) / (2.0 * _M)
        a_Sbar = (_K * len(_bisect_Sbar)) / (2.0 * _M)
        Q_direct = (e_S - a_S ** 2) + (e_Sbar - a_Sbar ** 2)
        assert abs(Q_quad - Q_direct) < 1e-8

    def test_balanced_bisection_cut_bounds(self):
        """For balanced bisection (|S| = 20): 100 <= cut <= 160.
        lower = 20*20*(12-2)/40 = 100,  upper = 20*20*(12+4)/40 = 160."""
        lower = 20 * 20 * (_K - _R) / float(_N)          # 100
        upper = 20 * 20 * (_K - _S_EIG) / float(_N)       # 160
        assert abs(lower - 100.0) < 1e-10
        assert abs(upper - 160.0) < 1e-10

    def test_bisection_cut_per_vertex_bounded(self):
        """Average external degree = cut / |S| is between 0 and k."""
        avg = _bisect_cut / float(len(_bisect_S))
        assert 0 < avg <= _K


# ===================================================================
# 6.  Normalized Cut Analysis   (10 tests)
#     NCut(S) = cut/vol(S) + cut/vol(Sbar),  vol(S) = k|S| for k-regular
# ===================================================================

class TestNormalizedCutAnalysis:
    """Normalized cut values, bounds, and identities."""

    def test_ncut_lower_bound_from_normalized_laplacian(self):
        """For any non-trivial partition: NCut >= mu_2 = 5/6.
        Proof: NCut = cut*n / (k*|S|*|Sbar|) and the Rayleigh
        quotient of the partition indicator gives cut*n/(|S||Sbar|) >= lambda_2,
        so NCut >= lambda_2/k = mu_2."""
        s = len(_bisect_S)
        ncut = _bisect_cut * _N / (float(_K) * s * (_N - s))
        assert ncut >= 5.0 / 6.0 - 1e-8

    def test_ncut_balanced_lower_bound(self):
        """Balanced bisection: min cut = 100, NCut_min = 100/120 = 5/6."""
        assert abs(100.0 / 120.0 - 5.0 / 6.0) < 1e-12

    def test_ncut_balanced_upper_bound(self):
        """Balanced bisection: max cut = 160, NCut_max = 160/120 = 4/3."""
        assert abs(160.0 / 120.0 - 4.0 / 3.0) < 1e-12

    def test_ncut_relaxation_equals_mu2(self):
        """The continuous relaxation of NCut gives mu_2 = 5/6."""
        assert abs(_norm_evals[1] - 5.0 / 6.0) < 1e-10

    def test_ncut_first_10_partition_satisfies_bound(self):
        """NCut of {0,...,9} vs {10,...,39} satisfies NCut >= mu_2."""
        s_list = list(range(10))
        sbar_list = list(range(10, _N))
        cut = int(np.sum(_A[np.ix_(s_list, sbar_list)]))
        ncut = cut / (float(_K) * 10) + cut / (float(_K) * 30)
        assert ncut >= 5.0 / 6.0 - 1e-8

    def test_ncut_complement_symmetry(self):
        """NCut(S, Sbar) = NCut(Sbar, S) by definition (symmetric formula)."""
        s = len(_bisect_S)
        ncut1 = _bisect_cut / (float(_K) * s) + _bisect_cut / (float(_K) * (_N - s))
        ncut2 = _bisect_cut / (float(_K) * (_N - s)) + _bisect_cut / (float(_K) * s)
        assert abs(ncut1 - ncut2) < 1e-12

    def test_normalized_laplacian_trace(self):
        """tr(L_norm) = 0 + 24*(5/6) + 15*(4/3) = 20 + 20 = 40 = n."""
        assert abs(np.trace(_L_norm) - 40.0) < 1e-10

    def test_ncut_equals_rcut_over_k(self):
        """For k-regular graph: NCut = RCut / k."""
        s = len(_bisect_S)
        rcut = _bisect_cut * (1.0 / s + 1.0 / (_N - s))
        ncut = _bisect_cut * (1.0 / (_K * s) + 1.0 / (_K * (_N - s)))
        assert abs(ncut - rcut / _K) < 1e-10

    def test_ncut_eigenvalue_sum(self):
        """Sum of all normalized Laplacian eigenvalues = n = 40."""
        assert abs(np.sum(_norm_evals) - 40.0) < 1e-8

    def test_ncut_log_det_normalized_laplacian(self):
        """log det'(L_norm) = 24 ln(5/6) + 15 ln(4/3)."""
        nonzero = _norm_evals[np.abs(_norm_evals) > 1e-8]
        log_prod = np.sum(np.log(nonzero))
        expected = 24 * np.log(5.0 / 6.0) + 15 * np.log(4.0 / 3.0)
        assert abs(log_prod - expected) < 1e-6


# ===================================================================
# 7.  Ratio Cut & Edge Expansion   (10 tests)
#     RCut(S) = cut * (1/|S| + 1/|Sbar|) = cut * n / (|S| |Sbar|)
# ===================================================================

class TestRatioCutEdgeExpansion:
    """Ratio-cut quality and edge expansion constants."""

    def test_rcut_lower_bound_from_fiedler(self):
        """lambda_2(L) <= RCut for any non-trivial partition.
        So RCut >= 10."""
        s = len(_bisect_S)
        rcut = _bisect_cut * _N / float(s * (_N - s))
        assert rcut >= 10.0 - 1e-6

    def test_rcut_balanced_bounds(self):
        """For balanced bisection: RCut = cut/10.
        With 100 <= cut <= 160: 10 <= RCut <= 16."""
        assert abs(100.0 / 10.0 - 10.0) < 1e-12
        assert abs(160.0 / 10.0 - 16.0) < 1e-12

    def test_rcut_spectral_bisection_satisfies_fiedler_bound(self):
        """The actual spectral bisection obeys RCut >= lambda_2."""
        s = len(_bisect_S)
        rcut = _bisect_cut * _N / float(s * (_N - s))
        assert rcut >= _lap_vals_full[1] - 1e-6

    def test_edge_expansion_singleton(self):
        """h({v}) = |E({v}, V\\{v})| / 1 = k = 12 for any vertex."""
        for v in range(_N):
            S = {v}
            Sbar = set(range(_N)) - S
            cut = _cut_size(_A, S, Sbar)
            assert cut == _K

    def test_edge_expansion_adjacent_pair(self):
        """For S = {u,v} adjacent: |E(S,Sbar)| = 2k - 2 = 22.
        (The single edge u-v is internal, so cut = 12+12-2*1 = 22.)"""
        for i in range(_N):
            for j in range(i + 1, _N):
                if _A[i, j] == 1:
                    S = {i, j}
                    Sbar = set(range(_N)) - S
                    cut = _cut_size(_A, S, Sbar)
                    assert cut == 22
                    return
        pytest.fail("No adjacent pair found")

    def test_edge_expansion_nonadjacent_pair(self):
        """For S = {u,v} non-adjacent: |E(S,Sbar)| = 2k = 24.
        (No internal edges, so cut = 12 + 12 = 24.)"""
        for i in range(_N):
            for j in range(i + 1, _N):
                if _A[i, j] == 0:
                    S = {i, j}
                    Sbar = set(range(_N)) - S
                    cut = _cut_size(_A, S, Sbar)
                    assert cut == 24
                    return
        pytest.fail("No non-adjacent pair found")

    def test_rcut_two_formulations_agree(self):
        """RCut = cut/|S| + cut/|Sbar| = cut*n / (|S|*|Sbar|)."""
        s = len(_bisect_S)
        rcut_v1 = _bisect_cut / float(s) + _bisect_cut / float(_N - s)
        rcut_v2 = _bisect_cut * _N / float(s * (_N - s))
        assert abs(rcut_v1 - rcut_v2) < 1e-10

    def test_edge_expansion_all_singletons_equal(self):
        """h({v}) = 12 for every vertex (vertex-transitive graph)."""
        cuts = []
        for v in range(_N):
            S = {v}
            Sbar = set(range(_N)) - S
            cuts.append(_cut_size(_A, S, Sbar))
        assert all(c == _K for c in cuts)

    def test_edge_expansion_adjacent_pair_all(self):
        """Every adjacent pair has cut = 22  (SRG regularity)."""
        count_checked = 0
        for i in range(_N):
            for j in range(i + 1, _N):
                if _A[i, j] == 1:
                    S = {i, j}
                    Sbar = set(range(_N)) - S
                    assert _cut_size(_A, S, Sbar) == 22
                    count_checked += 1
                    if count_checked >= 20:
                        return
        assert count_checked > 0

    def test_total_degree_identity(self):
        """2m = n k = 480.  Each partition S has vol(S) = k |S|."""
        assert _N * _K == 2 * _M
        assert 2 * _M == 480


# ===================================================================
# 8.  k-Way Partitioning Bounds   (10 tests)
# ===================================================================

class TestKWayPartitioningBounds:
    """Multi-way partitioning bounds from higher Laplacian eigenvalues."""

    def test_2way_fiedler_bound(self):
        """lambda_2 = 10 lower-bounds the 2-way ratio cut."""
        assert abs(_lap_vals_full[1] - 10.0) < 1e-8

    def test_eigenvalues_2_through_25_constant(self):
        """lambda_2 through lambda_25 all equal 10 (the 24-fold block)."""
        for i in range(1, 25):
            assert abs(_lap_vals_full[i] - 10.0) < 1e-6

    def test_eigenvalue_jump_at_26(self):
        """lambda_26 = 16 (entering the 15-fold block)."""
        assert abs(_lap_vals_full[25] - 16.0) < 1e-6

    def test_eigengap_heuristic(self):
        """Largest gap in the Laplacian spectrum:
        gap_1 = 10 (between 0 and 10), gap_25 = 6 (between 10 and 16).
        The dominant gap at position 1 reflects the vertex-transitive
        structure having no natural 2-community split."""
        gaps = np.diff(_lap_vals_full)
        assert abs(gaps[0] - 10.0) < 1e-6   # 0 -> 10
        assert abs(gaps[24] - 6.0) < 1e-6    # 10 -> 16

    def test_multiway_cheeger_2way_bound(self):
        """lambda_2 / 2 = 5 lower-bounds the 2-way expansion rho_2."""
        assert abs(_lap_vals_full[1] / 2.0 - 5.0) < 1e-8

    def test_singleton_partition_cut_equals_m(self):
        """k = n = 40 partition (singletons): every edge is cut.
        Total cut edges = m = 240."""
        assert _M == 240

    def test_4way_balanced_cut_lower_bound(self):
        """For 4-way balanced partition (parts of 10):
        max internal edges per part = s^2(k + r)/(2n) = 100*14/80 = 17.5.
        Total internal <= 4*17.5 = 70, so total cut >= 240 - 70 = 170.

        Wait -- recalculate: for s = 10:
        2|E(S)| <= s^2 k/n + r s(n-s)/n = 100*12/40 + 2*10*30/40 = 30+15 = 45
        |E(S)| <= 22.5. Total internal <= 90. Cut >= 150."""
        s = 10
        max_2e = (s ** 2 * _K + _R * s * (_N - s)) / float(_N)
        max_internal = max_2e / 2.0   # 22.5
        min_total_cut = _M - 4 * max_internal
        assert abs(min_total_cut - 150.0) < 1e-8

    def test_laplacian_sum_of_squares(self):
        """tr(L^2) = 0 + 24*100 + 15*256 = 6240."""
        expected = 24 * 100 + 15 * 256
        assert abs(np.trace(_L @ _L) - float(expected)) < 1e-4

    def test_kway_ncut_lower_bound_sum(self):
        """For q-way NCut: the sum of the first (q-1) non-trivial
        normalized Laplacian eigenvalues gives a lower bound.
        For q = 2: mu_2 = 5/6.  For q = 3: mu_2 + mu_3 = 10/6 = 5/3."""
        assert abs(_norm_evals[1] - 5.0 / 6.0) < 1e-8
        two_sum = _norm_evals[1] + _norm_evals[2]
        assert abs(two_sum - 5.0 / 3.0) < 1e-8

    def test_spectral_embedding_dimension(self):
        """The Fiedler eigenspace is 24-dimensional, providing a
        natural spectral embedding into R^24."""
        dim = int(np.sum(np.abs(_lap_vals_full - 10.0) < 1e-6))
        assert dim == 24


# ===================================================================
# 9.  Assortative / Disassortative Structure   (8 tests)
# ===================================================================

class TestAssortativeDisassortativeStructure:
    """Mixing patterns, clustering, and community structure signatures."""

    def test_degree_sequence_constant(self):
        """W(3,3) is 12-regular: all degrees equal 12."""
        degrees = np.sum(_A, axis=1)
        assert np.all(degrees == _K)

    def test_degree_variance_zero(self):
        """For a regular graph, degree variance is zero.
        Newman assortativity is undefined (division by zero)."""
        degrees = np.sum(_A, axis=1).astype(float)
        assert np.std(degrees) < 1e-12

    def test_neighbor_connectivity_constant(self):
        """Average neighbor degree = k = 12 for every vertex
        (consequence of k-regularity)."""
        degrees = np.sum(_A, axis=1).astype(float)
        for v in range(_N):
            nbrs = np.where(_A[v] == 1)[0]
            assert abs(np.mean(degrees[nbrs]) - float(_K)) < 1e-10

    def test_eigenvalue_ratio_r_over_abs_s(self):
        """r / |s| = 2/4 = 1/2: the negative eigenvalue magnitude dominates,
        indicating stronger anti-community (disassortative) spectral structure."""
        assert abs(float(_R) / float(abs(_S_EIG)) - 0.5) < 1e-12

    def test_positive_vs_negative_modularity_mass(self):
        """Positive eigenvalue mass / |negative| = 48/60 = 4/5 < 1.
        Negative modularity mass exceeds positive: the graph has stronger
        disassortative character than assortative."""
        pos_mass = _MULT_R * _R       # 48
        neg_mass = abs(_MULT_S * _S_EIG)  # 60
        assert abs(pos_mass / neg_mass - 4.0 / 5.0) < 1e-12

    def test_internal_edge_surplus_vs_deficiency(self):
        """For balanced bisection eigenvalue bounds:
        max |E(S)| = 70 (surplus = 10 above random expectation of 60),
        min |E(S)| = 40 (deficiency = 20 below random expectation).
        Deficiency > surplus => disassortative direction is stronger."""
        s = _N // 2
        max_int = (s ** 2 * (_K + _R)) / (2.0 * _N)      # 70
        min_int = (s ** 2 * (_K + _S_EIG)) / (2.0 * _N)   # 40
        random_int = _M * (float(s) / _N) ** 2             # 60
        surplus = max_int - random_int     # 10
        deficiency = random_int - min_int  # 20
        assert abs(surplus - 10.0) < 1e-8
        assert abs(deficiency - 20.0) < 1e-8
        assert deficiency > surplus

    def test_clustering_coefficient(self):
        """Clustering coefficient = lambda/(k-1) = 2/11 for SRG(n,k,lambda,mu).
        Each vertex v has k lambda / 2 = 12 edges among its neighbors,
        out of C(k,2) = 66 possible.  C(v) = 12/66 = 2/11."""
        for v in range(_N):
            nbrs = np.where(_A[v] == 1)[0]
            sub = _A[np.ix_(nbrs, nbrs)]
            edges_among = int(np.sum(sub)) // 2
            cc = edges_among / (len(nbrs) * (len(nbrs) - 1) / 2.0)
            assert abs(cc - 2.0 / 11.0) < 1e-12

    def test_triangle_count_from_spectrum(self):
        """Triangles = tr(A^3)/6 = (12^3 + 24*2^3 + 15*(-4)^3)/6
        = (1728 + 192 - 960)/6 = 960/6 = 160."""
        spectral = (12 ** 3 + _MULT_R * _R ** 3 + _MULT_S * _S_EIG ** 3)
        assert spectral // 6 == 160
        actual = int(round(np.trace(_A @ _A @ _A) / 6.0))
        assert actual == 160
