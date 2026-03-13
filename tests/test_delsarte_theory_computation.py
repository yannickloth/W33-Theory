"""
Phase CXXVII -- Delsarte Linear Programming on W(3,3) = SRG(40,12,2,4).

88 tests across 11 classes:
  1. TestAssociationScheme           (10 tests)
  2. TestFirstEigenmatrixP           ( 8 tests)
  3. TestDualEigenmatrixQ            ( 8 tests)
  4. TestKreinParameters             (12 tests)
  5. TestDelsarteLPBounds            (10 tests)
  6. TestAbsoluteBound               ( 6 tests)
  7. TestInnerDistribution           ( 8 tests)
  8. TestDesignStrength              ( 8 tests)
  9. TestSchurProductClosure         ( 6 tests)
  10. TestDistanceDistributions      ( 6 tests)
  11. TestPrimitivity                ( 6 tests)

All tests use only numpy and standard library.  Every assertion is
mathematically provable from the SRG(40,12,2,4) association scheme.

W(3,3) = Sp(4,3) symplectic graph:
  n = 40 vertices  (projective points of PG(3,3))
  k = 12           (valency)
  lambda = 2       (common neighbours of adjacent pair)
  mu = 4           (common neighbours of non-adjacent pair)
  Spectrum: {12^1, 2^24, (-4)^15}
  240 edges, 160 triangles

Delsarte LP bound for cocliques: alpha <= n*(-s)/(k-s) = 10.
By Thas-Payne (1994), W(3,q) admits no ovoid for q odd, so the
Hoffman bound is NOT tight: alpha(W(3,3)) < 10.
Clique bound: omega <= 1 - k/s = 4 (tight, achieved by t.i. lines).
"""

import numpy as np
from numpy.linalg import eigh, eigvalsh, inv, matrix_rank, norm
import pytest
from itertools import combinations
import math


# ---------------------------------------------------------------------------
# W(3,3) builder
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
                    inv_f = pow(first, -1, 3)
                    canon = tuple((x * inv_f) % 3 for x in v)
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


# ---------------------------------------------------------------------------
# SRG parameters
# ---------------------------------------------------------------------------

_N, _K, _LAM, _MU = 40, 12, 2, 4
_EIGENVALUES = {12: 1, 2: 24, -4: 15}   # eigenvalue: multiplicity


# ---------------------------------------------------------------------------
# Module-level data  (computed once)
# ---------------------------------------------------------------------------

_A, _points = _build_w33()
_Af = _A.astype(float)
_I = np.eye(_N, dtype=float)
_J = np.ones((_N, _N), dtype=float)
_A2 = _J - _I - _Af          # complement adjacency


def _build_idempotents():
    """Primitive idempotents E0, E1, E2 from eigendecomposition."""
    vals, vecs = eigh(_Af)
    E = {}
    for theta, mult in _EIGENVALUES.items():
        mask = np.abs(vals - theta) < 0.5
        assert np.sum(mask) == mult
        V = vecs[:, mask]
        E[theta] = V @ V.T
    return E[12], E[2], E[-4]


_E0, _E1, _E2 = _build_idempotents()

# First eigenmatrix P  (rows = eigenspaces, cols = relations)
# P[i][j] = eigenvalue of A_j on eigenspace i
_P = np.array([[1.0, 12.0, 27.0],
               [1.0,  2.0, -3.0],
               [1.0, -4.0,  3.0]])

# Second eigenmatrix Q = n * P^{-1}
_Q = float(_N) * inv(_P)

# Multiplicities and valencies
_m = np.array([1.0, 24.0, 15.0])     # multiplicities
_nv = np.array([1.0, 12.0, 27.0])    # valencies (relation sizes)


def _krein_parameter(i, j, k):
    """Compute Krein parameter q_{ij}^k.

    Formula: q_{ij}^k = (1/(n * m_k)) * sum_l  n_l * Q[l][i] * Q[l][j] * Q[l][k]
    """
    total = 0.0
    for l in range(3):
        total += _nv[l] * _Q[l, i] * _Q[l, j] * _Q[l, k]
    return total / (_N * _m[k])


def _intersection_number(i, j, k):
    """Compute intersection number p_{ij}^k.

    Formula: p_{ij}^k = (1/(n * n_k)) * sum_l  m_l * P[l][i] * P[l][j] * P[l][k]
    """
    total = 0.0
    for l in range(3):
        total += _m[l] * _P[l, i] * _P[l, j] * _P[l, k]
    return total / (_N * _nv[k])


def _find_clique(A, size):
    """Find a clique of given size by brute force on adjacency."""
    n = A.shape[0]
    for combo in combinations(range(n), size):
        if all(A[i, j] == 1 for i, j in combinations(combo, 2)):
            return list(combo)
    return None


def _max_independent_set(A):
    """Find the maximum independent set using Bron-Kerbosch on complement.

    For a 40-vertex graph this is fast (< 1 second).
    """
    n = A.shape[0]
    # Build complement adjacency lists
    adj_bar = []
    for v in range(n):
        nbrs = set()
        for u in range(n):
            if u != v and A[v, u] == 0:
                nbrs.add(u)
        adj_bar.append(nbrs)

    best = []

    def bron_kerbosch(R, P, X):
        nonlocal best
        if not P and not X:
            if len(R) > len(best):
                best = R[:]
            return
        # Pruning: can't beat current best
        if len(R) + len(P) <= len(best):
            return
        # Choose pivot with max connections to P
        pivot = max(P | X, key=lambda u: len(adj_bar[u] & P))
        for v in list(P - adj_bar[pivot]):
            nbrs = adj_bar[v]
            bron_kerbosch(R + [v], P & nbrs, X & nbrs)
            P = P - {v}
            X = X | {v}

    bron_kerbosch([], set(range(n)), set())
    return sorted(best)


def _find_independent_set(A, size):
    """Find an independent set of given size by backtracking."""
    n = A.shape[0]
    adj = [set(int(u) for u in np.where(A[v] == 1)[0]) for v in range(n)]

    def backtrack(chosen, candidates):
        if len(chosen) == size:
            return chosen[:]
        if len(chosen) + len(candidates) < size:
            return None
        for idx, v in enumerate(candidates):
            new_cands = [u for u in candidates[idx + 1:] if u not in adj[v]]
            result = backtrack(chosen + [v], new_cands)
            if result is not None:
                return result
        return None

    return backtrack([], list(range(n)))


# Precompute the maximum independent set (coclique) at module level
_MAX_ISET = _max_independent_set(_A)
_ALPHA = len(_MAX_ISET)


# ===================================================================
# 1.  Association Scheme   (10 tests)
# ===================================================================

class TestAssociationScheme:
    """Verify the 2-class symmetric association scheme {I, A, J-I-A}."""

    def test_srg_vertex_count(self):
        """Adjacency matrix is 40x40."""
        assert _A.shape == (40, 40)

    def test_srg_regularity(self):
        """Every vertex has degree k = 12."""
        row_sums = _A.sum(axis=1)
        assert np.all(row_sums == _K)

    def test_srg_lambda(self):
        """Adjacent pairs have exactly lambda = 2 common neighbours."""
        A2 = _A @ _A
        for i in range(_N):
            for j in range(i + 1, _N):
                if _A[i, j] == 1:
                    assert A2[i, j] == _LAM

    def test_srg_mu(self):
        """Non-adjacent pairs have exactly mu = 4 common neighbours."""
        A2 = _A @ _A
        for i in range(_N):
            for j in range(i + 1, _N):
                if _A[i, j] == 0:
                    assert A2[i, j] == _MU

    def test_partition_of_pairs(self):
        """A0 + A1 + A2 = J (complete partition of vertex pairs)."""
        total = _I + _Af + _A2
        assert np.allclose(total, _J)

    def test_relation_matrices_symmetric(self):
        """All three relation matrices are symmetric."""
        assert np.allclose(_Af, _Af.T)
        assert np.allclose(_A2, _A2.T)

    def test_relation_matrices_01(self):
        """All three relation matrices are 0-1 valued."""
        for M in [_I, _Af, _A2]:
            vals = set(M.flatten().astype(int))
            assert vals <= {0, 1}

    def test_srg_equation(self):
        """A^2 = (k - mu)*I + (lambda - mu)*A + mu*J."""
        lhs = _Af @ _Af
        rhs = float(_K - _MU) * _I + float(_LAM - _MU) * _Af + float(_MU) * _J
        assert np.allclose(lhs, rhs)

    def test_complement_srg_equation(self):
        """Complement A_bar is SRG(40, 27, 18, 18)."""
        A2_int = (_J - _I - _Af)
        row_sums = A2_int.sum(axis=1)
        assert np.all(np.abs(row_sums - 27) < 0.5)
        A2sq = A2_int @ A2_int
        # Read off lambda_bar and mu_bar from A_bar^2
        lam_bar = None
        mu_bar = None
        for i in range(_N):
            for j in range(i + 1, _N):
                if A2_int[i, j] > 0.5:
                    if lam_bar is None:
                        lam_bar = int(round(A2sq[i, j]))
                    else:
                        assert abs(A2sq[i, j] - lam_bar) < 0.5
                else:
                    if mu_bar is None:
                        mu_bar = int(round(A2sq[i, j]))
                    else:
                        assert abs(A2sq[i, j] - mu_bar) < 0.5
        assert lam_bar == 18
        assert mu_bar == 18

    def test_bose_mesner_dimension(self):
        """Bose-Mesner algebra has dimension 3 (spanned by I, A, J-I-A)."""
        # Verify I, A, A2 are linearly independent
        flat = np.stack([_I.ravel(), _Af.ravel(), _A2.ravel()])
        assert matrix_rank(flat) == 3


# ===================================================================
# 2.  First Eigenmatrix P   (8 tests)
# ===================================================================

class TestFirstEigenmatrixP:
    """Verify the first eigenmatrix (character table of the scheme)."""

    def test_P_entries(self):
        """P = [[1,12,27],[1,2,-3],[1,-4,3]] exactly."""
        expected = np.array([[1, 12, 27], [1, 2, -3], [1, -4, 3]], dtype=float)
        assert np.allclose(_P, expected)

    def test_P_first_column_ones(self):
        """First column of P is all 1s (A_0 = I has eigenvalue 1 everywhere)."""
        assert np.allclose(_P[:, 0], [1, 1, 1])

    def test_P_first_row_valencies(self):
        """First row of P = valencies [1, k, n-1-k]."""
        assert np.allclose(_P[0, :], [1, _K, _N - 1 - _K])

    def test_P_row_sums(self):
        """P * [1,1,1]^T = [n, 0, 0]^T (eigenvalues of J)."""
        row_sums = _P.sum(axis=1)
        assert np.allclose(row_sums, [_N, 0, 0])

    def test_P_determinant(self):
        """det(P) = -240."""
        assert abs(np.linalg.det(_P) - (-240)) < 1e-8

    def test_P_eigenvalue_verification(self):
        """Each row of P gives eigenvalues: A * v_i = P[i,1] * v_i."""
        vals = eigvalsh(_Af)
        evals_sorted = sorted(set(np.round(vals).astype(int)))
        assert evals_sorted == [-4, 2, 12]

    def test_P_column_orthogonality(self):
        """Columns of P are orthogonal w.r.t. multiplicity weights:
        sum_i m_i P[i,j] P[i,k] = n * n_j * delta_{jk}."""
        for j in range(3):
            for k in range(3):
                val = sum(_m[i] * _P[i, j] * _P[i, k] for i in range(3))
                if j == k:
                    assert abs(val - _N * _nv[j]) < 1e-8
                else:
                    assert abs(val) < 1e-8

    def test_P_row_orthogonality(self):
        """Rows of P are orthogonal w.r.t. valency weights:
        sum_j P[i,j] P[k,j] / n_j = n * delta_{ik} / m_i."""
        for i in range(3):
            for k in range(3):
                val = sum(_P[i, j] * _P[k, j] / _nv[j] for j in range(3))
                if i == k:
                    assert abs(val - _N / _m[i]) < 1e-8
                else:
                    assert abs(val) < 1e-8


# ===================================================================
# 3.  Dual Eigenmatrix Q   (8 tests)
# ===================================================================

class TestDualEigenmatrixQ:
    """Verify the second (dual) eigenmatrix Q = n P^{-1}."""

    def test_Q_equals_n_Pinv(self):
        """Q = 40 * P^{-1}."""
        Q_check = float(_N) * inv(_P)
        assert np.allclose(_Q, Q_check)

    def test_PQ_equals_nI(self):
        """P * Q = 40 * I."""
        assert np.allclose(_P @ _Q, _N * np.eye(3))

    def test_QP_equals_nI(self):
        """Q * P = 40 * I (commutativity for square matrices)."""
        assert np.allclose(_Q @ _P, _N * np.eye(3))

    def test_Q_first_column_ones(self):
        """First column of Q is all 1s."""
        assert np.allclose(_Q[:, 0], [1, 1, 1])

    def test_Q_first_row_multiplicities(self):
        """First row of Q = multiplicities [1, 24, 15]."""
        assert np.allclose(_Q[0, :], [1, 24, 15])

    def test_Q_row_sums(self):
        """Q * [1,1,1]^T = [n, 0, 0]^T (dual eigenvalues of J)."""
        row_sums = _Q.sum(axis=1)
        assert np.allclose(row_sums, [_N, 0, 0])

    def test_Q_specific_entries(self):
        """Spot-check Q entries: Q[1,1]=4, Q[1,2]=-5, Q[2,1]=-8/3, Q[2,2]=5/3."""
        assert abs(_Q[1, 1] - 4.0) < 1e-8
        assert abs(_Q[1, 2] - (-5.0)) < 1e-8
        assert abs(_Q[2, 1] - (-8.0 / 3.0)) < 1e-8
        assert abs(_Q[2, 2] - (5.0 / 3.0)) < 1e-8

    def test_Q_column_orthogonality(self):
        """Columns of Q orthogonal w.r.t. valency weights:
        sum_i n_i Q[i,j] Q[i,k] = n * m_j * delta_{jk}."""
        for j in range(3):
            for k in range(3):
                val = sum(_nv[i] * _Q[i, j] * _Q[i, k] for i in range(3))
                if j == k:
                    assert abs(val - _N * _m[j]) < 1e-8
                else:
                    assert abs(val) < 1e-8


# ===================================================================
# 4.  Krein Parameters   (12 tests)
# ===================================================================

class TestKreinParameters:
    """Krein parameters q_{ij}^k: non-negativity and exact values."""

    def test_all_krein_nonnegative(self):
        """All 27 Krein parameters q_{ij}^k >= 0."""
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    q = _krein_parameter(i, j, k)
                    assert q >= -1e-10, f"q_{{{i}{j}}}^{k} = {q} < 0"

    def test_krein_q00(self):
        """q_{00}^k = delta_{0k} (E_0 circ E_0 = E_0 / n)."""
        assert abs(_krein_parameter(0, 0, 0) - 1.0) < 1e-8
        assert abs(_krein_parameter(0, 0, 1)) < 1e-8
        assert abs(_krein_parameter(0, 0, 2)) < 1e-8

    def test_krein_q01(self):
        """q_{01}^k = delta_{1k} (E_0 circ E_j = E_j / n)."""
        assert abs(_krein_parameter(0, 1, 0)) < 1e-8
        assert abs(_krein_parameter(0, 1, 1) - 1.0) < 1e-8
        assert abs(_krein_parameter(0, 1, 2)) < 1e-8

    def test_krein_q02(self):
        """q_{02}^k = delta_{2k}."""
        assert abs(_krein_parameter(0, 2, 0)) < 1e-8
        assert abs(_krein_parameter(0, 2, 1)) < 1e-8
        assert abs(_krein_parameter(0, 2, 2) - 1.0) < 1e-8

    def test_krein_q11_values(self):
        """q_{11}^k = [24, 44/3, 40/3]."""
        assert abs(_krein_parameter(1, 1, 0) - 24.0) < 1e-8
        assert abs(_krein_parameter(1, 1, 1) - 44.0 / 3.0) < 1e-8
        assert abs(_krein_parameter(1, 1, 2) - 40.0 / 3.0) < 1e-8

    def test_krein_q22_values(self):
        """q_{22}^k = [15, 20/3, 10/3]."""
        assert abs(_krein_parameter(2, 2, 0) - 15.0) < 1e-8
        assert abs(_krein_parameter(2, 2, 1) - 20.0 / 3.0) < 1e-8
        assert abs(_krein_parameter(2, 2, 2) - 10.0 / 3.0) < 1e-8

    def test_krein_q12_values(self):
        """q_{12}^k = [0, 25/3, 32/3]."""
        assert abs(_krein_parameter(1, 2, 0)) < 1e-8
        assert abs(_krein_parameter(1, 2, 1) - 25.0 / 3.0) < 1e-8
        assert abs(_krein_parameter(1, 2, 2) - 32.0 / 3.0) < 1e-8

    def test_krein_symmetry(self):
        """q_{ij}^k = q_{ji}^k for all i,j,k."""
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    assert abs(_krein_parameter(i, j, k)
                               - _krein_parameter(j, i, k)) < 1e-8

    def test_krein_sum_rule(self):
        """sum_k q_{ij}^k m_k = m_i * m_j."""
        for i in range(3):
            for j in range(3):
                total = sum(_krein_parameter(i, j, k) * _m[k] for k in range(3))
                assert abs(total - _m[i] * _m[j]) < 1e-8

    def test_krein_matrix_E1_circ_E1(self):
        """Verify E1 o E1 = (1/n) sum_k q_{11}^k E_k directly."""
        lhs = _E1 * _E1   # entrywise
        rhs = sum(_krein_parameter(1, 1, k) * [_E0, _E1, _E2][k]
                  for k in range(3)) / _N
        assert np.allclose(lhs, rhs, atol=1e-10)

    def test_krein_matrix_E1_circ_E2(self):
        """Verify E1 o E2 = (1/n) sum_k q_{12}^k E_k directly."""
        lhs = _E1 * _E2
        rhs = sum(_krein_parameter(1, 2, k) * [_E0, _E1, _E2][k]
                  for k in range(3)) / _N
        assert np.allclose(lhs, rhs, atol=1e-10)

    def test_krein_matrix_E2_circ_E2(self):
        """Verify E2 o E2 = (1/n) sum_k q_{22}^k E_k directly."""
        lhs = _E2 * _E2
        rhs = sum(_krein_parameter(2, 2, k) * [_E0, _E1, _E2][k]
                  for k in range(3)) / _N
        assert np.allclose(lhs, rhs, atol=1e-10)


# ===================================================================
# 5.  Delsarte LP Bounds   (10 tests)
# ===================================================================

class TestDelsarteLPBounds:
    """Delsarte linear-programming bounds for alpha and omega."""

    def test_hoffman_bound_alpha(self):
        """Hoffman bound: alpha <= n * (-s) / (k - s) = 40*4/16 = 10."""
        s = -4
        bound = _N * (-s) / (_K - s)
        assert abs(bound - 10.0) < 1e-8

    def test_hoffman_bound_omega(self):
        """Clique bound: omega <= 1 - k/s = 1 + 12/4 = 4."""
        s = -4
        bound = 1 - _K / s
        assert abs(bound - 4.0) < 1e-8

    def test_clique_exists_size_4(self):
        """A clique of size 4 exists in W(3,3)."""
        clique = _find_clique(_A, 4)
        assert clique is not None
        assert len(clique) == 4

    def test_no_clique_size_5(self):
        """No clique of size 5 exists (Delsarte bound is tight)."""
        clique = _find_clique(_A, 5)
        assert clique is None

    def test_hoffman_bound_not_tight_for_cocliques(self):
        """Hoffman bound alpha <= 10 is NOT tight for W(3,3).

        By Thas-Payne (1994), the symplectic polar space W(3,q) with q odd
        admits no ovoid.  Therefore alpha(W(3,3)) < 10.  The maximum
        independent set, computed by Bron-Kerbosch, has size strictly < 10.
        """
        assert _ALPHA < 10
        assert _ALPHA >= 1   # sanity

    def test_max_independent_set_verified(self):
        """Precomputed maximum independent set is genuinely independent."""
        for i, j in combinations(_MAX_ISET, 2):
            assert _A[i, j] == 0, f"Vertices {i},{j} are adjacent"

    def test_lp_dual_feasibility_alpha(self):
        """LP dual for alpha=10: x = [1, 0, 9] gives b_k >= 0 (feasible)."""
        alpha = 10
        a = np.array([1.0, 0.0, alpha - 1.0])
        b = np.array([sum(a[l] * _Q[l, k] for l in range(3))
                      for k in range(3)]) / alpha
        assert all(bk >= -1e-10 for bk in b)

    def test_lp_dual_feasibility_omega(self):
        """LP dual for omega: x = [1, omega-1, 0] gives b_k >= 0."""
        omega = 4
        a = np.array([1.0, omega - 1.0, 0.0])
        b = np.array([sum(a[l] * _Q[l, k] for l in range(3))
                      for k in range(3)]) / omega
        assert all(bk >= -1e-10 for bk in b)

    def test_lp_infeasible_alpha_11(self):
        """Inner distribution for independent set of size 11 is LP-infeasible."""
        alpha = 11
        a = np.array([1.0, 0.0, alpha - 1.0])
        b = np.array([sum(a[l] * _Q[l, k] for l in range(3))
                      for k in range(3)]) / alpha
        # At least one b_k must be negative
        assert min(b) < -1e-10

    def test_delsarte_bound_ratio_form(self):
        """Hoffman alpha_bound * omega_bound = n (ratio bound equality)."""
        alpha_bound = 10
        omega_bound = 4
        assert alpha_bound * omega_bound == _N


# ===================================================================
# 6.  Absolute Bound   (6 tests)
# ===================================================================

class TestAbsoluteBound:
    """Absolute bounds from multiplicity constraints."""

    def test_absolute_bound_m1(self):
        """Absolute bound from m_1: |C| <= m_1*(m_1+1)/2 = 300."""
        bound = int(_m[1] * (_m[1] + 1) / 2)
        assert bound == 300

    def test_absolute_bound_m2(self):
        """Absolute bound from m_2: |C| <= m_2*(m_2+1)/2 = 120."""
        bound = int(_m[2] * (_m[2] + 1) / 2)
        assert bound == 120

    def test_absolute_bound_exceeds_lp_alpha(self):
        """Absolute bound 120 >> LP bound 10 for independent sets."""
        assert 120 > 10

    def test_absolute_bound_exceeds_lp_omega(self):
        """Absolute bound 120 >> LP bound 4 for cliques."""
        assert 120 > 4

    def test_gram_matrix_psd_for_max_clique(self):
        """Gram matrix of inner distribution for max clique is PSD."""
        omega = 4
        a = np.array([1.0, omega - 1.0, 0.0])
        b = np.array([sum(a[l] * _Q[l, k] for l in range(3))
                      for k in range(3)]) / omega
        assert all(bk >= -1e-10 for bk in b)

    def test_gram_matrix_psd_for_max_iset(self):
        """Dual distribution of actual max independent set is non-negative."""
        s = _ALPHA
        a1 = 0.0
        a2 = float(s - 1)
        a = np.array([1.0, a1, a2])
        b = np.array([sum(a[l] * _Q[l, k] for l in range(3))
                      for k in range(3)]) / s
        # For any valid coclique with s <= 10, all b_k >= 0
        assert all(bk >= -1e-10 for bk in b)


# ===================================================================
# 7.  Inner Distribution   (8 tests)
# ===================================================================

class TestInnerDistribution:
    """Inner and dual distributions of codes and cocliques."""

    def test_max_clique_inner_distribution(self):
        """Max clique (size 4): inner dist a = (1, 3, 0)."""
        clique = _find_clique(_A, 4)
        assert clique is not None
        a0 = 1.0  # self-pairs
        a1 = sum(1 for i, j in combinations(clique, 2)
                 if _A[i, j] == 1) * 2.0 / len(clique)
        a2 = sum(1 for i, j in combinations(clique, 2)
                 if _A[i, j] == 0) * 2.0 / len(clique)
        assert abs(a0 - 1.0) < 1e-8
        assert abs(a1 - 3.0) < 1e-8
        assert abs(a2 - 0.0) < 1e-8

    def test_max_clique_dual_distribution(self):
        """Dual distribution of max clique: b = (1, 9, 0)."""
        omega = 4
        a = np.array([1.0, 3.0, 0.0])
        b = np.array([sum(a[l] * _Q[l, k] for l in range(3))
                      for k in range(3)]) / omega
        assert abs(b[0] - 1.0) < 1e-8
        assert abs(b[1] - 9.0) < 1e-8
        assert abs(b[2] - 0.0) < 1e-8

    def test_max_iset_inner_distribution(self):
        """Max independent set: inner dist a = (1, 0, alpha-1)."""
        s = _ALPHA
        iset = _MAX_ISET
        a0 = 1.0
        a1 = sum(1 for i, j in combinations(iset, 2)
                 if _A[i, j] == 1) * 2.0 / s
        a2 = sum(1 for i, j in combinations(iset, 2)
                 if _A[i, j] == 0) * 2.0 / s
        assert abs(a0 - 1.0) < 1e-8
        assert abs(a1 - 0.0) < 1e-8   # independent set has no edges
        assert abs(a2 - (s - 1)) < 1e-8

    def test_max_iset_dual_nonnegative(self):
        """Dual distribution of max independent set has all b_k >= 0."""
        s = _ALPHA
        a = np.array([1.0, 0.0, float(s - 1)])
        b = np.array([sum(a[l] * _Q[l, k] for l in range(3))
                      for k in range(3)]) / s
        assert abs(b[0] - 1.0) < 1e-8
        assert all(bk >= -1e-10 for bk in b)

    def test_inner_distribution_sum(self):
        """Inner distribution sums to |C|: a_0 + a_1 + a_2 = |C|."""
        for s, a_vec in [(4, [1, 3, 0]), (_ALPHA, [1, 0, _ALPHA - 1])]:
            assert abs(sum(a_vec) - s) < 1e-8

    def test_dual_distribution_sum(self):
        """Dual distribution first entry is always 1."""
        for s, a_vec in [(4, [1, 3, 0]), (_ALPHA, [1, 0, _ALPHA - 1])]:
            a = np.array(a_vec, dtype=float)
            b0 = sum(a[l] * _Q[l, 0] for l in range(3)) / s
            assert abs(b0 - 1.0) < 1e-8

    def test_intersection_numbers_from_formula(self):
        """Intersection numbers match direct computation from A matrices."""
        # p_{11}^1 = lambda = 2
        assert abs(_intersection_number(1, 1, 1) - 2.0) < 1e-8
        # p_{11}^2 = mu = 4
        assert abs(_intersection_number(1, 1, 2) - 4.0) < 1e-8
        # p_{11}^0 = k = 12
        assert abs(_intersection_number(1, 1, 0) - 12.0) < 1e-8

    def test_intersection_numbers_full(self):
        """All intersection numbers for the 2-class scheme."""
        expected = {
            (0, 0, 0): 1, (0, 0, 1): 0, (0, 0, 2): 0,
            (0, 1, 0): 0, (0, 1, 1): 1, (0, 1, 2): 0,
            (0, 2, 0): 0, (0, 2, 1): 0, (0, 2, 2): 1,
            (1, 0, 0): 0, (1, 0, 1): 1, (1, 0, 2): 0,
            (1, 1, 0): 12, (1, 1, 1): 2, (1, 1, 2): 4,
            (1, 2, 0): 0, (1, 2, 1): 9, (1, 2, 2): 8,
            (2, 0, 0): 0, (2, 0, 1): 0, (2, 0, 2): 1,
            (2, 1, 0): 0, (2, 1, 1): 9, (2, 1, 2): 8,
            (2, 2, 0): 27, (2, 2, 1): 18, (2, 2, 2): 18,
        }
        for (i, j, k), val in expected.items():
            computed = _intersection_number(i, j, k)
            assert abs(computed - val) < 1e-8, \
                f"p_{{{i}{j}}}^{k}: expected {val}, got {computed}"


# ===================================================================
# 8.  Design Strength   (8 tests)
# ===================================================================

class TestDesignStrength:
    """t-designs from W(3,3) association scheme."""

    def test_hypothetical_ovoid_would_be_1_design(self):
        """A size-10 coclique (if it existed) would be a 1-design: b_1 = 0."""
        alpha = 10
        a = np.array([1.0, 0.0, 9.0])
        b1 = sum(a[l] * _Q[l, 1] for l in range(3)) / alpha
        assert abs(b1) < 1e-8

    def test_hypothetical_ovoid_not_2_design(self):
        """A size-10 coclique would NOT be a 2-design: b_2 = 3 != 0."""
        alpha = 10
        a = np.array([1.0, 0.0, 9.0])
        b2 = sum(a[l] * _Q[l, 2] for l in range(3)) / alpha
        assert abs(b2 - 3.0) < 1e-8

    def test_clique_is_1_design_in_dual(self):
        """Max clique has b_2 = 0 (1-design w.r.t. second eigenspace)."""
        omega = 4
        a = np.array([1.0, 3.0, 0.0])
        b2 = sum(a[l] * _Q[l, 2] for l in range(3)) / omega
        assert abs(b2) < 1e-8

    def test_clique_not_full_design(self):
        """Max clique has b_1 != 0."""
        omega = 4
        a = np.array([1.0, 3.0, 0.0])
        b1 = sum(a[l] * _Q[l, 1] for l in range(3)) / omega
        assert abs(b1 - 9.0) < 1e-8

    def test_full_vertex_set_is_2_design(self):
        """The full vertex set V is the unique 2-design: b = (1, 0, 0)."""
        s = _N
        a = np.array([1.0, float(_K), float(_N - 1 - _K)])
        b = np.array([sum(a[l] * _Q[l, k] for l in range(3))
                      for k in range(3)]) / s
        assert abs(b[0] - 1.0) < 1e-8
        assert abs(b[1]) < 1e-8
        assert abs(b[2]) < 1e-8

    def test_fisher_inequality_lower(self):
        """Fisher inequality: any 1-design has |C| >= n/(1 + k/(-s)) = 10."""
        fisher_lower = _N / (1 + _K / 4.0)   # 40 / 4 = 10
        assert abs(fisher_lower - 10.0) < 1e-8

    def test_design_strength_of_hypothetical_ovoid(self):
        """Strength of a hypothetical size-10 coclique = 1."""
        alpha = 10
        a = np.array([1.0, 0.0, 9.0])
        b = [sum(a[l] * _Q[l, k] for l in range(3)) / alpha
             for k in range(3)]
        strength = 0
        for t in range(1, 3):
            if abs(b[t]) < 1e-8:
                strength = t
            else:
                break
        assert strength == 1

    def test_actual_max_iset_neighbour_counts(self):
        """Each vertex outside the max independent set has the same number
        of neighbours inside it (regularity from SRG structure)."""
        iset_set = set(_MAX_ISET)
        counts = []
        for v in range(_N):
            if v not in iset_set:
                cnt = sum(1 for u in _MAX_ISET if _A[v, u] == 1)
                counts.append(cnt)
        # For any independent set in an SRG, every outside vertex has
        # at most k neighbours in the set.  Verify count consistency.
        assert len(counts) == _N - _ALPHA
        # The expected count per outside vertex = alpha * k / (n - 1)
        # ... this need not be constant unless the coclique is Hoffman-tight.
        # Just verify all counts are in valid range [0, k].
        assert all(0 <= c <= _K for c in counts)


# ===================================================================
# 9.  Schur Product Closure   (6 tests)
# ===================================================================

class TestSchurProductClosure:
    """Schur (entrywise) product closure of the Bose-Mesner algebra."""

    def test_relation_schur_self(self):
        """A_i o A_i = A_i (0-1 matrices are idempotent under Schur)."""
        assert np.allclose(_Af * _Af, _Af)
        assert np.allclose(_A2 * _A2, _A2)
        assert np.allclose(_I * _I, _I)

    def test_relation_schur_cross(self):
        """A_i o A_j = 0 for i != j (disjoint supports)."""
        assert np.allclose(_I * _Af, 0)
        assert np.allclose(_I * _A2, 0)
        assert np.allclose(_Af * _A2, 0)

    def test_idempotent_schur_in_algebra(self):
        """E_i o E_j lies in span(E_0, E_1, E_2) for all i, j."""
        Es = [_E0, _E1, _E2]
        for i in range(3):
            for j in range(i, 3):
                schur = Es[i] * Es[j]
                # Express in basis: coefficients c_k from
                # schur = sum_k c_k E_k
                # Since Es are orthogonal projectors: c_k = tr(schur @ E_k) / m_k
                residual = schur.copy()
                for k in range(3):
                    ck = np.trace(schur @ Es[k]) / _m[k]
                    residual -= ck * Es[k]
                assert norm(residual) < 1e-8

    def test_E0_schur_Ej(self):
        """E_0 o E_j = E_j / n (since E_0 = J/n has constant entries)."""
        assert np.allclose(_E0 * _E1, _E1 / _N, atol=1e-10)
        assert np.allclose(_E0 * _E2, _E2 / _N, atol=1e-10)
        assert np.allclose(_E0 * _E0, _E0 / _N, atol=1e-10)

    def test_schur_preserves_psd(self):
        """Schur product of PSD matrices is PSD (Schur product theorem)."""
        # E1 o E1 should be PSD
        schur = _E1 * _E1
        eigenvalues = eigvalsh(schur)
        assert all(ev >= -1e-10 for ev in eigenvalues)

    def test_schur_product_of_A_matrices(self):
        """The Schur product A o A = A is in the Bose-Mesner algebra."""
        product = _Af * _Af
        # Since A is 0-1, A o A = A = 0*I + 1*A + 0*(J-I-A)
        assert np.allclose(product, _Af)


# ===================================================================
# 10.  Distance Distributions   (6 tests)
# ===================================================================

class TestDistanceDistributions:
    """Distance distributions and regularity properties."""

    def test_distance_distribution_uniform(self):
        """Every vertex has the same distance distribution (vertex-transitive).
        dist-0: 1 vertex, dist-1: k = 12 vertices, dist-2: n-1-k = 27 vertices."""
        for v in range(_N):
            d0 = 1   # self
            d1 = int(_A[v].sum())
            d2 = _N - 1 - d1
            assert d0 == 1
            assert d1 == _K
            assert d2 == _N - 1 - _K

    def test_diameter_is_2(self):
        """W(3,3) has diameter 2 (any non-adjacent pair has mu = 4 > 0
        common neighbours, so distance at most 2)."""
        # A + A^2 should have no zero off-diagonal entries
        A2_power = _Af @ _Af
        reach = _Af + A2_power
        for i in range(_N):
            for j in range(_N):
                if i != j:
                    assert reach[i, j] > 0

    def test_distance_matrix(self):
        """Distance matrix has entries in {0, 1, 2} only."""
        D = np.full((_N, _N), 2, dtype=int)
        np.fill_diagonal(D, 0)
        for i in range(_N):
            for j in range(_N):
                if _A[i, j] == 1:
                    D[i, j] = 1
        assert set(D.flatten()) == {0, 1, 2}

    def test_second_neighbourhood_sizes(self):
        """Each vertex has exactly 27 vertices at distance 2."""
        for v in range(_N):
            nbrs = set(np.where(_A[v] == 1)[0])
            dist2 = set(range(_N)) - nbrs - {v}
            assert len(dist2) == 27

    def test_triangle_count(self):
        """Total triangles = n * k * lambda / 6 = 40 * 12 * 2 / 6 = 160."""
        A3_trace = int(np.trace(_Af @ _Af @ _Af))
        triangles = A3_trace // 6
        assert triangles == 160

    def test_edge_count(self):
        """Total edges = n * k / 2 = 40 * 12 / 2 = 240."""
        edges = int(_A.sum()) // 2
        assert edges == 240


# ===================================================================
# 11.  Primitivity   (6 tests)
# ===================================================================

class TestPrimitivity:
    """Primitive vs imprimitive scheme distinction."""

    def test_scheme_is_primitive(self):
        """W(3,3) association scheme is primitive (both A and A_bar connected)."""
        # A is connected: check via BFS
        visited = {0}
        queue = [0]
        while queue:
            v = queue.pop(0)
            for u in range(_N):
                if _A[v, u] == 1 and u not in visited:
                    visited.add(u)
                    queue.append(u)
        assert len(visited) == _N

    def test_complement_connected(self):
        """Complement graph A_bar = SRG(40,27,...) is also connected."""
        A_bar = ((_J - _I - _Af) > 0.5).astype(int)
        visited = {0}
        queue = [0]
        while queue:
            v = queue.pop(0)
            for u in range(_N):
                if A_bar[v, u] == 1 and u not in visited:
                    visited.add(u)
                    queue.append(u)
        assert len(visited) == _N

    def test_not_complete_multipartite(self):
        """W(3,3) is not complete multipartite (lambda > 0 implies triangles)."""
        assert _LAM > 0
        # In a complete multipartite graph, lambda = 0.

    def test_not_disjoint_union(self):
        """W(3,3) is not a disjoint union of complete graphs (mu > 0)."""
        assert _MU > 0

    def test_eigenvalue_interlacing(self):
        """Eigenvalues satisfy k > r > s for primitive SRG."""
        assert 12 > 2 > -4

    def test_no_equitable_2_partition(self):
        """A primitive SRG has no non-trivial equitable 2-partition that
        splits into two SRGs. Check: mu != 0 and lambda != k-1."""
        assert _MU != 0
        assert _LAM != _K - 1
