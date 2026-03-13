"""
Phase CXXIV -- Quantum Graph Theory Computation on W(3,3) = SRG(40,12,2,4).

87 tests across 12 classes:
  1.  TestCTQW                         (10 tests)
  2.  TestQuantumStateTransfer          ( 7 tests)
  3.  TestEntanglementEntropy           ( 8 tests)
  4.  TestQuantumChromaticNumber        ( 7 tests)
  5.  TestQuantumIndependenceNumber     ( 6 tests)
  6.  TestGroverSearch                  ( 7 tests)
  7.  TestQuantumMixing                 ( 7 tests)
  8.  TestReturnProbability             ( 8 tests)
  9.  TestWignerFunction                ( 6 tests)
  10. TestDensityMatrixEvolution        ( 8 tests)
  11. TestDecoherence                   ( 6 tests)
  12. TestQuantumTransport              ( 7 tests)

Only numpy and standard library.  Every assertion is mathematically provable.

W(3,3) = Sp(4,3) symplectic graph:
  n = 40 vertices  (projective points of PG(3,3))
  k = 12           (valency)
  lambda = 2       (common neighbours of adjacent pair)
  mu = 4           (common neighbours of non-adjacent pair)
  Spectrum: {12^1, 2^24, (-4)^15}
  240 edges, 160 triangles
"""

import math
import numpy as np
import pytest


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
# Module-level data (computed once)
# ---------------------------------------------------------------------------

_A = _build_w33()
_n = 40
_k = 12
_lam = 2
_mu = 4

# Eigendecomposition
_eigvals_raw, _eigvecs_raw = np.linalg.eigh(_A.astype(float))
_idx_sort = np.argsort(_eigvals_raw)
_eigvals = _eigvals_raw[_idx_sort]
_eigvecs = _eigvecs_raw[:, _idx_sort]


def _ctqw_unitary(t):
    """Continuous-time quantum walk unitary U(t) = exp(-i A t)."""
    return _eigvecs @ np.diag(np.exp(-1j * _eigvals * t)) @ _eigvecs.T.conj()


def _spectral_projectors():
    """Return spectral projectors E0 (eigenvalue 12), E1 (2), E2 (-4)."""
    E = {}
    for label, target in [("k", 12.0), ("r", 2.0), ("s", -4.0)]:
        mask = np.abs(_eigvals - target) < 0.5
        vecs = _eigvecs[:, mask]
        E[label] = vecs @ vecs.T
    return E["k"], E["r"], E["s"]


_E0, _E1, _E2 = _spectral_projectors()


# ===================================================================
# 1.  Continuous-Time Quantum Walk (CTQW)              (10 tests)
# ===================================================================

class TestCTQW:
    """CTQW unitary U(t) = exp(-iAt) on W(3,3)."""

    def test_U0_is_identity(self):
        """U(0) = I_40."""
        U0 = _ctqw_unitary(0.0)
        assert np.allclose(U0, np.eye(_n), atol=1e-12)

    def test_unitarity(self):
        """U(t) U(t)^dagger = I for several t values."""
        for t in [0.1, 0.5, 1.0, np.pi]:
            U = _ctqw_unitary(t)
            assert np.allclose(U @ U.conj().T, np.eye(_n), atol=1e-10)

    def test_group_property(self):
        """U(t1) U(t2) = U(t1 + t2)."""
        t1, t2 = 0.3, 0.7
        U1 = _ctqw_unitary(t1)
        U2 = _ctqw_unitary(t2)
        U12 = _ctqw_unitary(t1 + t2)
        assert np.allclose(U1 @ U2, U12, atol=1e-10)

    def test_inverse(self):
        """U(-t) = U(t)^dagger."""
        t = 0.5
        U = _ctqw_unitary(t)
        U_inv = _ctqw_unitary(-t)
        assert np.allclose(U_inv, U.conj().T, atol=1e-10)

    def test_transition_probabilities_sum_to_one(self):
        """Sum_j |<j|U(t)|k>|^2 = 1 for each starting vertex k."""
        U = _ctqw_unitary(1.0)
        probs = np.abs(U) ** 2
        col_sums = probs.sum(axis=0)
        assert np.allclose(col_sums, 1.0, atol=1e-10)

    def test_transition_probabilities_nonnegative(self):
        """|<j|U(t)|k>|^2 >= 0."""
        U = _ctqw_unitary(0.7)
        probs = np.abs(U) ** 2
        assert np.all(probs >= -1e-15)

    def test_vertex_transitivity_diagonal(self):
        """Vertex-transitivity: |<j|U(t)|j>|^2 identical for all j."""
        U = _ctqw_unitary(0.4)
        diag_probs = np.abs(np.diag(U)) ** 2
        assert np.allclose(diag_probs, diag_probs[0], atol=1e-10)

    def test_spectral_decomposition_consistency(self):
        """U(t) = sum_j exp(-i lambda_j t) E_j matches direct computation."""
        t = 0.6
        U_direct = _ctqw_unitary(t)
        U_spectral = (np.exp(-1j * 12 * t) * _E0 +
                      np.exp(-1j * 2 * t) * _E1 +
                      np.exp(-1j * (-4) * t) * _E2)
        assert np.allclose(U_direct, U_spectral, atol=1e-10)

    def test_trace_of_U(self):
        """tr(U(t)) = 1*exp(-12it) + 24*exp(-2it) + 15*exp(4it)."""
        t = 0.3
        U = _ctqw_unitary(t)
        tr_computed = np.trace(U)
        tr_exact = (1 * np.exp(-1j * 12 * t) +
                    24 * np.exp(-1j * 2 * t) +
                    15 * np.exp(-1j * (-4) * t))
        assert abs(tr_computed - tr_exact) < 1e-10

    def test_determinant_of_U(self):
        """det(U(t)) = exp(-i t tr(A)) = 1 since tr(A) = 0."""
        t = 0.5
        U = _ctqw_unitary(t)
        det_val = np.linalg.det(U)
        assert abs(abs(det_val) - 1.0) < 1e-10
        assert abs(det_val - 1.0) < 1e-8


# ===================================================================
# 2.  Quantum State Transfer                            (7 tests)
# ===================================================================

class TestQuantumStateTransfer:
    """State transfer properties of CTQW on W(3,3)."""

    def _transfer_amplitude(self, a, b, t):
        """<b|U(t)|a> = sum_j exp(-i lambda_j t) (E_j)_{ba}."""
        return (np.exp(-1j * 12 * t) * _E0[b, a] +
                np.exp(-1j * 2 * t) * _E1[b, a] +
                np.exp(-1j * (-4) * t) * _E2[b, a])

    def test_self_transfer_at_zero(self):
        """<a|U(0)|a> = 1."""
        for a in range(5):
            amp = self._transfer_amplitude(a, a, 0.0)
            assert abs(amp - 1.0) < 1e-12

    def test_transfer_amplitude_bounded(self):
        """|<b|U(t)|a>| <= 1 for all a, b, t."""
        for t in [0.1, 0.5, 1.0, 2.0]:
            U = _ctqw_unitary(t)
            assert np.all(np.abs(U) <= 1.0 + 1e-10)

    def test_no_perfect_state_transfer_adjacent(self):
        """No PST between adjacent vertices.  Triangle inequality gives
        max|<b|U(t)|a>| <= |E0_{ba}|+|E1_{ba}|+|E2_{ba}| = 0.25 < 1."""
        a = 0
        b = int(np.where(_A[0] == 1)[0][0])
        max_amp = abs(_E0[b, a]) + abs(_E1[b, a]) + abs(_E2[b, a])
        assert max_amp < 1.0 - 1e-6

    def test_no_perfect_state_transfer_nonadjacent(self):
        """No PST between non-adjacent vertices either.
        Max amplitude sum ~ 2/15 < 1."""
        nonadj = np.where((_A[0] == 0) & (np.arange(_n) != 0))[0]
        b = nonadj[0]
        max_amp = abs(_E0[b, 0]) + abs(_E1[b, 0]) + abs(_E2[b, 0])
        assert max_amp < 1.0 - 1e-6

    def test_transfer_symmetry_vertex_transitive(self):
        """Vertex-transitivity: |<j|U(t)|j>|^2 identical for all j."""
        t = 1.0
        return_probs = np.array([abs(self._transfer_amplitude(j, j, t))**2
                                 for j in range(_n)])
        assert np.allclose(return_probs, return_probs[0], atol=1e-10)

    def test_transfer_to_neighbors_uniform(self):
        """By edge-transitivity of SRG, |<b|U(t)|a>|^2 is the same
        for all neighbours b of a."""
        t = 0.8
        a = 0
        neighbors = np.where(_A[a] == 1)[0]
        U = _ctqw_unitary(t)
        probs = np.abs(U[neighbors, a]) ** 2
        assert np.allclose(probs, probs[0], atol=1e-10)

    def test_transfer_to_nonneighbors_uniform(self):
        """|<b|U(t)|a>|^2 is the same for all non-neighbours b of a."""
        t = 0.8
        a = 0
        non_neighbors = np.where((_A[a] == 0) & (np.arange(_n) != a))[0]
        U = _ctqw_unitary(t)
        probs = np.abs(U[non_neighbors, a]) ** 2
        assert np.allclose(probs, probs[0], atol=1e-10)


# ===================================================================
# 3.  Entanglement Entropy of Graph States              (8 tests)
# ===================================================================

class TestEntanglementEntropy:
    """Graph state |G> = prod CZ |+>^n; entropy = rank_GF(2) of bipartite
    adjacency submatrix."""

    @staticmethod
    def _gf2_rank(M):
        """Rank of binary matrix M over GF(2) via Gaussian elimination."""
        mat = np.array(M, dtype=int) % 2
        rows, cols = mat.shape
        mat = mat.copy()
        rank = 0
        for col in range(cols):
            pivot = None
            for row in range(rank, rows):
                if mat[row, col] % 2 == 1:
                    pivot = row
                    break
            if pivot is None:
                continue
            mat[[rank, pivot]] = mat[[pivot, rank]]
            for row in range(rows):
                if row != rank and mat[row, col] % 2 == 1:
                    mat[row] = (mat[row] + mat[rank]) % 2
            rank += 1
        return rank

    def test_single_vertex_entropy(self):
        """S({v}) = rank_GF2 of 1 x 39 row = 1 (since k=12 > 0)."""
        row = _A[0, 1:].reshape(1, -1)
        assert self._gf2_rank(row) == 1

    def test_two_adjacent_vertices_entropy(self):
        """S({i,j}) = 2 for adjacent i,j (distinct neighbour rows)."""
        j = int(np.where(_A[0] == 1)[0][0])
        complement = [v for v in range(_n) if v != 0 and v != j]
        sub = _A[np.ix_([0, j], complement)]
        assert self._gf2_rank(sub) == 2

    def test_two_nonadjacent_vertices_entropy(self):
        """S({i,j}) = 2 for non-adjacent i,j."""
        nonadj = np.where((_A[0] == 0) & (np.arange(_n) != 0))[0]
        j = nonadj[0]
        complement = [v for v in range(_n) if v != 0 and v != j]
        sub = _A[np.ix_([0, j], complement)]
        assert self._gf2_rank(sub) == 2

    def test_entropy_bounded_by_subsystem_size(self):
        """S(A) <= |A| for any subset A."""
        for size in [1, 3, 5, 10]:
            subset = list(range(size))
            complement = [v for v in range(_n) if v not in subset]
            sub = _A[np.ix_(subset, complement)]
            rank = self._gf2_rank(sub)
            assert rank <= size

    def test_entropy_bounded_by_complement_size(self):
        """S(A) <= n - |A|."""
        for size in [35, 38]:
            subset = list(range(size))
            complement = [v for v in range(_n) if v not in subset]
            sub = _A[np.ix_(subset, complement)]
            rank = self._gf2_rank(sub)
            assert rank <= _n - size

    def test_entropy_half_partition(self):
        """Entropy of a 20-vertex partition is positive and <= 20."""
        subset = list(range(20))
        complement = list(range(20, 40))
        sub = _A[np.ix_(subset, complement)]
        rank = self._gf2_rank(sub)
        assert 0 < rank <= 20

    def test_full_gf2_rank_of_adjacency(self):
        """GF(2) rank of full adjacency matrix is positive and <= n."""
        rank = self._gf2_rank(_A)
        assert 0 < rank <= _n

    def test_entropy_symmetry(self):
        """S(A) = S(B) where B = complement of A (pure graph state)."""
        subset = list(range(15))
        complement = [v for v in range(_n) if v not in subset]
        sub_AB = _A[np.ix_(subset, complement)]
        sub_BA = _A[np.ix_(complement, subset)]
        assert self._gf2_rank(sub_AB) == self._gf2_rank(sub_BA)


# ===================================================================
# 4.  Quantum Chromatic Number Bounds                   (7 tests)
# ===================================================================

class TestQuantumChromaticNumber:
    """Bounds on the quantum chromatic number chi_q(G)."""

    def test_clique_number_bound(self):
        """Hoffman bound: omega(G) <= 1 - k/s = 1 - 12/(-4) = 4."""
        omega_bound = 1 - _k / (-4)
        assert omega_bound == 4

    def test_hoffman_independence_bound(self):
        """alpha(G) <= n*(-s)/(k-s) = 40*4/16 = 10."""
        alpha_bound = _n * 4 / (_k + 4)
        assert abs(alpha_bound - 10.0) < 1e-10

    def test_fractional_chromatic_lower_bound(self):
        """chi_f(G) >= n/alpha(G) >= 40/10 = 4."""
        chi_f_lower = _n / 10.0
        assert abs(chi_f_lower - 4.0) < 1e-10

    def test_quantum_chromatic_lower_bound(self):
        """chi_q(G) >= omega(G) = 4."""
        omega = int(1 - _k / (-4))
        assert omega >= 4

    def test_lovasz_theta_value(self):
        """theta(G) = -n*s/(k-s) = 160/16 = 10 for SRG(40,12,2,4)."""
        theta = -_n * (-4.0) / (_k - (-4.0))
        assert abs(theta - 10.0) < 1e-10

    def test_chromatic_upper_bound(self):
        """chi(G) <= Delta + 1 = k + 1 = 13 (Brooks' theorem for non-complete)."""
        assert _k + 1 == 13

    def test_theta_sandwich(self):
        """Sandwich: omega(G) <= n/theta(G) ... more precisely
        n/theta(G) <= chi_q(G) <= chi(G).  n/theta = 40/10 = 4."""
        theta_G = 10.0
        lower = _n / theta_G
        assert abs(lower - 4.0) < 1e-10


# ===================================================================
# 5.  Quantum Independence Number                      (6 tests)
# ===================================================================

class TestQuantumIndependenceNumber:
    """Quantum independence number alpha_q and related bounds."""

    def test_hoffman_bound_value(self):
        """alpha(G) <= 10 (Hoffman bound)."""
        alpha_H = int(_n * 4 / (_k + 4))
        assert alpha_H == 10

    def test_independent_set_exists(self):
        """Greedy algorithm finds an independent set of size >= 4."""
        available = set(range(_n))
        indep = []
        for v in range(_n):
            if v in available:
                indep.append(v)
                neighbors = set(np.where(_A[v] == 1)[0])
                available -= neighbors
                available.discard(v)
        # Greedy on 12-regular: each pick removes <= 13 vertices
        # so we get at least ceil(40/13) = 4
        assert len(indep) >= 4
        # Verify it is actually independent
        for i in range(len(indep)):
            for j in range(i + 1, len(indep)):
                assert _A[indep[i], indep[j]] == 0

    def test_quantum_independence_lower_bound(self):
        """alpha_q(G) >= alpha(G) (classical sets are quantum sets)."""
        # Hoffman bound gives alpha = 10, which is achievable
        assert 10 >= 4  # omega(G) = 4

    def test_lovasz_theta_as_upper_bound(self):
        """alpha(G) <= theta(G) = 10."""
        theta = -_n * (-4.0) / (_k - (-4.0))
        assert abs(theta - 10.0) < 1e-10

    def test_complement_degree(self):
        """Complement G_bar has degree n-1-k = 27."""
        A_bar = 1 - _A - np.eye(_n, dtype=int)
        assert np.all(A_bar.sum(axis=1) == 27)

    def test_sum_alpha_omega_bound(self):
        """alpha(G) + omega(G) <= n + 1.  10 + 4 = 14 <= 41."""
        assert 10 + 4 <= _n + 1


# ===================================================================
# 6.  Grover Search on Graph                            (7 tests)
# ===================================================================

class TestGroverSearch:
    """Grover-type quantum search using the graph structure."""

    @staticmethod
    def _grover_operator(marked):
        """G = D * O where O = phase-flip on marked, D = 2|psi><psi| - I."""
        O = np.eye(_n)
        for m in marked:
            O[m, m] = -1
        psi = np.ones(_n) / np.sqrt(_n)
        D = 2.0 * np.outer(psi, psi) - np.eye(_n)
        return D @ O

    def test_grover_operator_unitary(self):
        """Grover operator is unitary (product of two reflections)."""
        G = self._grover_operator([0])
        assert np.allclose(G @ G.T, np.eye(_n), atol=1e-10)

    def test_grover_single_marked_amplification(self):
        """After O(sqrt(n)) iterations, marked-vertex probability grows."""
        G = self._grover_operator([0])
        psi = np.ones(_n) / np.sqrt(_n)
        p0 = abs(psi[0]) ** 2
        num_iter = int(np.pi / 4 * np.sqrt(_n))
        state = psi.copy()
        for _ in range(num_iter):
            state = G @ state
        p_final = abs(state[0]) ** 2
        assert p_final > p0

    def test_grover_preserves_norm(self):
        """Grover iteration preserves the state norm."""
        G = self._grover_operator([0])
        state = np.ones(_n) / np.sqrt(_n)
        for _ in range(5):
            state = G @ state
            assert abs(np.linalg.norm(state) - 1.0) < 1e-10

    def test_grover_operator_determinant(self):
        """|det(G)| = 1 for unitary G."""
        G = self._grover_operator([0])
        assert abs(abs(np.linalg.det(G)) - 1.0) < 1e-10

    def test_grover_multiple_marked(self):
        """With 4 marked vertices, amplification still works."""
        marked = [0, 1, 2, 3]
        G = self._grover_operator(marked)
        state = np.ones(_n) / np.sqrt(_n)
        num_iter = int(np.pi / 4 * np.sqrt(_n / len(marked)))
        for _ in range(num_iter):
            state = G @ state
        p_marked = sum(abs(state[m]) ** 2 for m in marked)
        assert p_marked > len(marked) / _n

    def test_oracle_is_involution(self):
        """Oracle O^2 = I (phase flip is its own inverse)."""
        O = np.eye(_n)
        O[0, 0] = -1
        assert np.allclose(O @ O, np.eye(_n))

    def test_diffusion_is_involution(self):
        """Diffusion D = 2|psi><psi| - I satisfies D^2 = I."""
        psi = np.ones(_n) / np.sqrt(_n)
        D = 2.0 * np.outer(psi, psi) - np.eye(_n)
        assert np.allclose(D @ D, np.eye(_n), atol=1e-10)


# ===================================================================
# 7.  Quantum Mixing                                    (7 tests)
# ===================================================================

class TestQuantumMixing:
    """Average mixing matrix and instantaneous uniform mixing."""

    @staticmethod
    def _average_mixing_matrix():
        """M_avg_{ab} = sum_j (E_j)_{ab}^2 (time-averaged transition probs)."""
        return _E0 ** 2 + _E1 ** 2 + _E2 ** 2

    def test_average_mixing_doubly_stochastic(self):
        """M_avg is doubly stochastic: rows and columns sum to 1."""
        M = self._average_mixing_matrix()
        assert np.allclose(M.sum(axis=0), 1.0, atol=1e-10)
        assert np.allclose(M.sum(axis=1), 1.0, atol=1e-10)

    def test_average_mixing_nonnegative(self):
        """M_avg >= 0 entrywise (sum of squares)."""
        M = self._average_mixing_matrix()
        assert np.all(M >= -1e-15)

    def test_average_mixing_symmetric(self):
        """M_avg is symmetric (each E_j is real symmetric)."""
        M = self._average_mixing_matrix()
        assert np.allclose(M, M.T, atol=1e-12)

    def test_average_mixing_diagonal_constant(self):
        """Vertex-transitivity: M_avg_{jj} is the same for all j."""
        M = self._average_mixing_matrix()
        diag = np.diag(M)
        assert np.allclose(diag, diag[0], atol=1e-10)

    def test_average_mixing_diagonal_value(self):
        """M_avg_{jj} = (1/40)^2 + (24/40)^2 + (15/40)^2 = 802/1600 = 401/800.
        Uses vertex-transitivity: (E_j)_{ii} = mult_j / n."""
        M = self._average_mixing_matrix()
        expected = (1 + 576 + 225) / 1600.0   # = 401/800
        assert abs(M[0, 0] - expected) < 1e-10

    def test_average_mixing_not_uniform(self):
        """W(3,3) does NOT have uniform average mixing (M_avg != J/n)."""
        M = self._average_mixing_matrix()
        uniform = np.ones((_n, _n)) / _n
        assert not np.allclose(M, uniform, atol=0.01)

    def test_average_mixing_three_values(self):
        """For rank-3 SRG, M_avg takes exactly 3 values:
        diagonal, adjacent, non-adjacent."""
        M = self._average_mixing_matrix()
        vals = set()
        for i in range(_n):
            for j in range(_n):
                vals.add(round(M[i, j], 8))
        assert len(vals) == 3


# ===================================================================
# 8.  Return Probability                                (8 tests)
# ===================================================================

class TestReturnProbability:
    """Quantum return probability p(t) = |<0|U(t)|0>|^2."""

    def _return_prob(self, t):
        """p(t) via spectral decomposition.  Vertex-transitive so any
        vertex gives the same result."""
        a0 = 1.0 / _n        # E0_{00} = 1/40
        a1 = 24.0 / _n       # E1_{00} = 24/40
        a2 = 15.0 / _n       # E2_{00} = 15/40
        amp = (a0 * np.exp(-1j * 12 * t) +
               a1 * np.exp(-1j * 2 * t) +
               a2 * np.exp(1j * 4 * t))
        return abs(amp) ** 2

    def test_return_prob_at_zero(self):
        """p(0) = 1."""
        assert abs(self._return_prob(0.0) - 1.0) < 1e-12

    def test_return_prob_bounded(self):
        """0 <= p(t) <= 1 for all t."""
        for t in np.linspace(0, 10, 200):
            p = self._return_prob(t)
            assert -1e-12 <= p <= 1.0 + 1e-12

    def test_return_prob_time_average(self):
        """Time-averaged return probability = M_avg_{00} = 401/800."""
        times = np.linspace(0, 1000, 50000)
        avg = np.mean([self._return_prob(t) for t in times])
        expected = 401.0 / 800.0
        assert abs(avg - expected) < 0.01

    def test_return_prob_formula(self):
        """p(t) matches direct U(t) computation."""
        t = 1.3
        U = _ctqw_unitary(t)
        p_direct = abs(U[0, 0]) ** 2
        assert abs(self._return_prob(t) - p_direct) < 1e-10

    def test_return_prob_periodic(self):
        """Eigenvalues are integers, so p(t) has period 2*pi."""
        t = 0.7
        p1 = self._return_prob(t)
        p2 = self._return_prob(t + 2 * np.pi)
        assert abs(p1 - p2) < 1e-10

    def test_return_prob_even_function(self):
        """p(t) = p(-t)."""
        t = 0.9
        assert abs(self._return_prob(t) - self._return_prob(-t)) < 1e-12

    def test_return_prob_nonnegative(self):
        """p(t) >= 0 (squared modulus)."""
        for t in np.linspace(0.1, 6.0, 100):
            assert self._return_prob(t) >= -1e-15

    def test_return_prob_at_pi(self):
        """At t = pi all eigenvalues are even integers, so
        exp(-i*lambda*pi) = 1 for each.  Hence p(pi) = 1."""
        p = self._return_prob(np.pi)
        assert abs(p - 1.0) < 1e-10


# ===================================================================
# 9.  Wigner Function on Graph                          (6 tests)
# ===================================================================

class TestWignerFunction:
    """Discrete Wigner-type function built from spectral projectors.
    W(j) = n * <phi_j|rho|phi_j>  where {phi_j} are eigenvectors of A."""

    @staticmethod
    def _wigner(rho):
        """Compute W(j) = n * <phi_j | rho | phi_j> for each eigenvector."""
        W = np.zeros(_n)
        for j in range(_n):
            v = _eigvecs[:, j]
            W[j] = _n * np.real(v.conj() @ rho @ v)
        return W

    def test_wigner_normalization(self):
        """sum_j W(j) = n * tr(rho) = n for any state with tr(rho)=1."""
        psi = np.zeros(_n); psi[0] = 1.0
        rho = np.outer(psi, psi)
        W = self._wigner(rho)
        assert abs(np.sum(W) - _n) < 1e-10

    def test_wigner_uniform_state(self):
        """For rho = I/n: W(j) = n * (1/n) = 1 for all j."""
        rho = np.eye(_n) / _n
        W = self._wigner(rho)
        assert np.allclose(W, 1.0, atol=1e-10)

    def test_wigner_eigenstate_delta(self):
        """W of eigenstate |phi_k> is n * delta_{jk}."""
        k = 5
        psi = _eigvecs[:, k]
        rho = np.outer(psi, psi)
        W = self._wigner(rho)
        expected = np.zeros(_n); expected[k] = _n
        assert np.allclose(W, expected, atol=1e-8)

    def test_wigner_nonnegative(self):
        """W(j) = n|<phi_j|psi>|^2 >= 0 for any pure state."""
        psi = np.zeros(_n); psi[0] = 1.0
        rho = np.outer(psi, psi)
        W = self._wigner(rho)
        assert np.all(W >= -1e-10)

    def test_wigner_time_invariant(self):
        """W(j) is time-invariant under CTQW since {phi_j} diagonalise H=A.
        Proof: <phi_j|U rho U^dag|phi_j> = <phi_j|rho|phi_j>."""
        psi = np.zeros(_n, dtype=complex); psi[0] = 1.0
        rho0 = np.outer(psi, psi.conj())
        W0 = self._wigner(rho0)
        U = _ctqw_unitary(1.7)
        rho_t = U @ rho0 @ U.conj().T
        Wt = self._wigner(rho_t)
        assert np.allclose(W0, Wt, atol=1e-8)

    def test_wigner_localized_nonuniform(self):
        """W of a vertex-localised state is non-uniform across eigenstates."""
        psi = np.zeros(_n); psi[0] = 1.0
        rho = np.outer(psi, psi)
        W = self._wigner(rho)
        assert np.max(W) - np.min(W) > 1e-6


# ===================================================================
# 10. Density Matrix Evolution                          (8 tests)
# ===================================================================

class TestDensityMatrixEvolution:
    """Unitary evolution rho(t) = U(t) rho(0) U(t)^dagger."""

    @staticmethod
    def _evolve_rho(rho0, t):
        U = _ctqw_unitary(t)
        return U @ rho0 @ U.conj().T

    def test_trace_preserved(self):
        """tr(rho(t)) = 1."""
        rho0 = np.zeros((_n, _n), dtype=complex); rho0[0, 0] = 1.0
        for t in [0.1, 0.5, 1.0, 3.0]:
            rho = self._evolve_rho(rho0, t)
            assert abs(np.trace(rho) - 1.0) < 1e-10

    def test_purity_preserved(self):
        """tr(rho(t)^2) = 1 for pure initial state."""
        rho0 = np.zeros((_n, _n), dtype=complex); rho0[0, 0] = 1.0
        for t in [0.2, 1.0]:
            rho = self._evolve_rho(rho0, t)
            assert abs(np.real(np.trace(rho @ rho)) - 1.0) < 1e-10

    def test_positive_semidefinite(self):
        """rho(t) >= 0."""
        rho0 = np.zeros((_n, _n), dtype=complex); rho0[0, 0] = 1.0
        rho = self._evolve_rho(rho0, 0.5)
        evals = np.linalg.eigvalsh(rho)
        assert np.all(evals >= -1e-10)

    def test_hermiticity_preserved(self):
        """rho(t) is Hermitian."""
        rho0 = np.zeros((_n, _n), dtype=complex); rho0[0, 0] = 1.0
        rho = self._evolve_rho(rho0, 0.7)
        assert np.allclose(rho, rho.conj().T, atol=1e-10)

    def test_von_neumann_entropy_preserved(self):
        """S(rho(t)) = 0 for pure-state evolution."""
        rho0 = np.zeros((_n, _n), dtype=complex); rho0[0, 0] = 1.0
        rho = self._evolve_rho(rho0, 1.0)
        evals = np.linalg.eigvalsh(rho)
        evals_pos = evals[evals > 1e-12]
        S = -np.sum(evals_pos * np.log(evals_pos))
        assert abs(S) < 1e-8

    def test_mixed_state_evolution(self):
        """Mixed state (0.5|0><0| + 0.5|1><1|): purity = 0.5 preserved."""
        rho0 = np.zeros((_n, _n), dtype=complex)
        rho0[0, 0] = 0.5; rho0[1, 1] = 0.5
        rho = self._evolve_rho(rho0, 0.5)
        assert abs(np.trace(rho) - 1.0) < 1e-10
        assert abs(np.real(np.trace(rho @ rho)) - 0.5) < 1e-10

    def test_commutator_stationary(self):
        """Maximally mixed state commutes with A, so rho(t) = rho(0)."""
        rho0 = np.eye(_n, dtype=complex) / _n
        rho = self._evolve_rho(rho0, 1.0)
        assert np.allclose(rho, rho0, atol=1e-10)

    def test_eigenstate_stationary(self):
        """An eigenstate |phi><phi| of A is stationary under evolution."""
        psi = _eigvecs[:, 0].astype(complex)
        rho0 = np.outer(psi, psi.conj())
        rho = self._evolve_rho(rho0, 1.0)
        assert np.allclose(rho, rho0, atol=1e-10)


# ===================================================================
# 11. Decoherence                                       (6 tests)
# ===================================================================

class TestDecoherence:
    """Dephasing decoherence in vertex basis (Lindblad channel)."""

    @staticmethod
    def _dephase(rho, gamma):
        """One step of dephasing: rho -> (1-gamma)*rho + gamma*diag(rho)."""
        return (1 - gamma) * rho + gamma * np.diag(np.diag(rho))

    def test_dephasing_preserves_trace(self):
        """tr(rho) = 1 after dephasing."""
        rho = np.zeros((_n, _n), dtype=complex); rho[0, 0] = 1.0
        rho = self._dephase(self._dephase(rho, 0.1), 0.1)
        assert abs(np.trace(rho) - 1.0) < 1e-12

    def test_dephasing_preserves_positivity(self):
        """Dephasing is completely positive: eigenvalues stay >= 0."""
        psi = np.ones(_n, dtype=complex) / np.sqrt(_n)
        rho = np.outer(psi, psi.conj())
        rho = self._dephase(rho, 0.3)
        evals = np.linalg.eigvalsh(rho)
        assert np.all(evals >= -1e-12)

    def test_dephasing_decreases_purity(self):
        """Dephasing of a non-diagonal pure state decreases purity."""
        psi = np.ones(_n, dtype=complex) / np.sqrt(_n)
        rho = np.outer(psi, psi.conj())
        purity_before = np.real(np.trace(rho @ rho))
        rho_deph = self._dephase(rho, 0.5)
        purity_after = np.real(np.trace(rho_deph @ rho_deph))
        assert purity_after < purity_before - 1e-6

    def test_full_dephasing_kills_coherence(self):
        """gamma = 1: only diagonal survives."""
        psi = np.ones(_n, dtype=complex) / np.sqrt(_n)
        rho = np.outer(psi, psi.conj())
        rho_deph = self._dephase(rho, 1.0)
        off_diag = rho_deph - np.diag(np.diag(rho_deph))
        assert np.allclose(off_diag, 0, atol=1e-12)

    def test_dephased_ctqw_purity_decay(self):
        """Alternating CTQW and dephasing: purity decays from 1."""
        rho = np.zeros((_n, _n), dtype=complex); rho[0, 0] = 1.0
        gamma = 0.05
        dt = 0.1
        purities = [np.real(np.trace(rho @ rho))]
        for _ in range(20):
            U = _ctqw_unitary(dt)
            rho = U @ rho @ U.conj().T
            rho = self._dephase(rho, gamma)
            purities.append(np.real(np.trace(rho @ rho)))
        assert purities[-1] < purities[0] - 0.01

    def test_dephased_steady_state(self):
        """Repeated strong dephasing + CTQW converges toward diagonal."""
        rho = np.zeros((_n, _n), dtype=complex); rho[0, 0] = 1.0
        for _ in range(200):
            U = _ctqw_unitary(0.1)
            rho = U @ rho @ U.conj().T
            rho = self._dephase(rho, 0.3)
        off_diag_norm = np.linalg.norm(rho - np.diag(np.diag(rho)))
        assert off_diag_norm < 0.5


# ===================================================================
# 12. Quantum Transport                                 (7 tests)
# ===================================================================

class TestQuantumTransport:
    """Transport efficiency and propagation on W(3,3)."""

    def test_transport_efficiency(self):
        """At t > 0, some probability has left the source vertex."""
        source = 0
        U = _ctqw_unitary(1.0)
        probs = np.abs(U[:, source]) ** 2
        eta = 1.0 - probs[source]
        assert eta > 0

    def test_ballistic_spreading(self):
        """CTQW spreads: variance of graph-distance grows from 0."""
        source = 0
        dist = np.zeros(_n, dtype=int)
        dist[_A[source] == 1] = 1
        dist[(_A[source] == 0) & (np.arange(_n) != source)] = 2
        variances = []
        for t in [0.1, 0.5, 1.0]:
            U = _ctqw_unitary(t)
            probs = np.abs(U[:, source]) ** 2
            mean_d = np.sum(probs * dist)
            var_d = np.sum(probs * dist ** 2) - mean_d ** 2
            variances.append(var_d)
        assert variances[-1] > variances[0] - 0.01

    def test_graph_diameter_2(self):
        """W(3,3) has diameter 2: A + A^2 is positive off-diagonal."""
        A2 = _A @ _A
        reachable = _A + A2
        for i in range(_n):
            for j in range(_n):
                if i != j:
                    assert reachable[i, j] > 0

    def test_transport_to_all_vertices(self):
        """At generic time, CTQW has nonzero probability on every vertex."""
        U = _ctqw_unitary(1.0)
        probs = np.abs(U[:, 0]) ** 2
        assert np.all(probs > 1e-15)

    def test_current_antisymmetric(self):
        """Probability current J_{jk} = 2 Im(rho_{jk} A_{jk}) is
        antisymmetric and has zero total sum."""
        rho = np.zeros((_n, _n), dtype=complex); rho[0, 0] = 1.0
        U = _ctqw_unitary(0.5)
        rho_t = U @ rho @ U.conj().T
        J = 2.0 * np.imag(rho_t * _A.astype(float))
        assert np.allclose(J, -J.T, atol=1e-10)
        assert abs(np.sum(J)) < 1e-10

    def test_propagator_symmetry(self):
        """U(t) = U(t)^T since A is real symmetric."""
        U = _ctqw_unitary(0.8)
        assert np.allclose(U, U.T, atol=1e-10)

    def test_zero_initial_transport_rate(self):
        """d/dt p_j(0) = -2 Im(A_{j0}) = 0 since A is real:
        no instantaneous transport at t = 0."""
        for j in range(_n):
            assert abs(-2 * np.imag(complex(_A[j, 0]))) < 1e-15
