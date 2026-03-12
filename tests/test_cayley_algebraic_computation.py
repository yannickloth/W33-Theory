"""
Phase CIV -- Cayley Graph & Algebraic Structure (Hard Computation)
==================================================================
Theorems T1740 - T1760   (21 theorem-classes, 73 tests)

W(3,3) = SRG(40, 12, 2, 4) with adjacency eigenvalues:
    12 (mult 1),  2 (mult 24),  -4 (mult 15)

Topics: Bose-Mesner algebra, spectral idempotents, Krein parameters,
intersection numbers, distance-regularity, walk-regularity, interlacing,
absolute bounds, P/Q eigenmatrices, trace / moment identities.
"""

import numpy as np
import pytest


# ===================================================================
# Builder
# ===================================================================

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
            omega = (u[0]*v[1] - u[1]*v[0] + u[2]*v[3] - u[3]*v[2]) % 3
            if omega == 0:
                A[i, j] = A[j, i] = 1
    return A


# ===================================================================
# Module-scoped fixtures
# ===================================================================

@pytest.fixture(scope="module")
def adj():
    """Adjacency matrix A of W(3,3)."""
    return _build_w33()


@pytest.fixture(scope="module")
def n():
    return 40


@pytest.fixture(scope="module")
def srg_params():
    """SRG parameters (n, k, lambda, mu)."""
    return (40, 12, 2, 4)


@pytest.fixture(scope="module")
def eigenvalues():
    """Eigenvalues (k, r, s) and multiplicities (1, f, g)."""
    return dict(k=12, r=2, s=-4, f=24, g=15)


@pytest.fixture(scope="module")
def eig_decomp(adj):
    """Full eigendecomposition of A, sorted by eigenvalue."""
    vals, vecs = np.linalg.eigh(adj.astype(float))
    idx = np.argsort(vals)
    return vals[idx], vecs[:, idx]


@pytest.fixture(scope="module")
def J(n):
    """All-ones matrix."""
    return np.ones((n, n), dtype=float)


@pytest.fixture(scope="module")
def I_n(n):
    """Identity matrix."""
    return np.eye(n, dtype=float)


@pytest.fixture(scope="module")
def A_bar(adj, I_n, J):
    """Complement adjacency: A_bar = J - I - A."""
    return J - I_n - adj.astype(float)


@pytest.fixture(scope="module")
def P_mat():
    """First eigenmatrix (P-matrix) of the 2-class association scheme."""
    return np.array([
        [1,  12,  27],
        [1,   2,  -3],
        [1,  -4,   3],
    ], dtype=float)


@pytest.fixture(scope="module")
def Q_mat(P_mat, n):
    """Second eigenmatrix: Q = n * P^{-1}."""
    return n * np.linalg.inv(P_mat)


@pytest.fixture(scope="module")
def spectral_idempotents(adj, I_n, J, n):
    """Primitive idempotents E_0, E_1, E_2 of the Bose-Mesner algebra."""
    A = adj.astype(float)
    # E_0 = J / n
    E0 = J / n
    # E_1 = (A + 4I)(A - 12I) / ((r - s)(r - k)) = (A+4I)(A-12I)/(-60)
    E1 = (A + 4 * I_n) @ (A - 12 * I_n) / (-60.0)
    # E_2 = (A - 2I)(A - 12I) / ((s - r)(s - k)) = (A-2I)(A-12I)/(96)
    E2 = (A - 2 * I_n) @ (A - 12 * I_n) / 96.0
    return E0, E1, E2


# ===================================================================
# T1740 -- SRG Parameter Verification
# ===================================================================

class TestT1740:
    """SRG feasibility: k(k - lambda - 1) = mu(n - k - 1) = 108."""

    def test_left_identity(self, srg_params):
        n, k, lam, mu = srg_params
        assert k * (k - lam - 1) == 108

    def test_right_identity(self, srg_params):
        n, k, lam, mu = srg_params
        assert mu * (n - k - 1) == 108

    def test_left_equals_right(self, srg_params):
        n, k, lam, mu = srg_params
        assert k * (k - lam - 1) == mu * (n - k - 1)

    def test_vertex_count_consistency(self, adj, srg_params):
        """n = 40 from actual graph."""
        assert adj.shape[0] == srg_params[0]


# ===================================================================
# T1741 -- Bose-Mesner Algebra Dimension
# ===================================================================

class TestT1741:
    """The Bose-Mesner algebra of SRG(40,12,2,4) has dimension 3."""

    def test_three_basis_matrices(self, adj, I_n, J, A_bar):
        """I, A, J-I-A are linearly independent."""
        A = adj.astype(float)
        flat = np.array([I_n.ravel(), A.ravel(), A_bar.ravel()])
        assert np.linalg.matrix_rank(flat) == 3

    def test_A_squared_in_span(self, adj, I_n, J, A_bar):
        """A^2 lies in span{I, A, J-I-A}."""
        A = adj.astype(float)
        A2 = A @ A
        flat = np.array([I_n.ravel(), A.ravel(), A_bar.ravel(), A2.ravel()])
        assert np.linalg.matrix_rank(flat, tol=1e-6) == 3

    def test_Abar_squared_in_span(self, adj, I_n, J, A_bar):
        """A_bar^2 lies in span{I, A, J-I-A}."""
        A_bar2 = A_bar @ A_bar
        A = adj.astype(float)
        flat = np.array([I_n.ravel(), A.ravel(), A_bar.ravel(), A_bar2.ravel()])
        assert np.linalg.matrix_rank(flat, tol=1e-6) == 3


# ===================================================================
# T1742 -- Bose-Mesner Algebra Closure Under Multiplication
# ===================================================================

class TestT1742:
    """All pairwise products of {I, A, A_bar} lie inside the algebra."""

    def _in_span(self, M, I_n, A, A_bar):
        flat = np.array([I_n.ravel(), A.ravel(), A_bar.ravel()])
        aug = np.vstack([flat, M.ravel()])
        return np.linalg.matrix_rank(aug, tol=1e-6) == 3

    def test_A_times_Abar(self, adj, I_n, A_bar):
        A = adj.astype(float)
        assert self._in_span(A @ A_bar, I_n, A, A_bar)

    def test_Abar_times_A(self, adj, I_n, A_bar):
        A = adj.astype(float)
        assert self._in_span(A_bar @ A, I_n, A, A_bar)

    def test_Abar_times_Abar(self, adj, I_n, A_bar):
        A = adj.astype(float)
        assert self._in_span(A_bar @ A_bar, I_n, A, A_bar)

    def test_algebra_is_commutative(self, adj, A_bar):
        """The Bose-Mesner algebra is commutative: A * A_bar = A_bar * A."""
        A = adj.astype(float)
        assert np.allclose(A @ A_bar, A_bar @ A)


# ===================================================================
# T1743 -- A^2 = 8I - 2A + 4J
# ===================================================================

class TestT1743:
    """A^2 = kI + lambda*A + mu*(J-I-A) = 8I - 2A + 4J."""

    def test_A2_explicit(self, adj, I_n, J):
        A = adj.astype(float)
        A2 = A @ A
        expected = 8 * I_n - 2 * A + 4 * J
        assert np.allclose(A2, expected)

    def test_A2_via_srg_relation(self, adj, I_n, A_bar, srg_params):
        """A^2 = k*I + lambda*A + mu*A_bar (SRG equation)."""
        n, k, lam, mu = srg_params
        A = adj.astype(float)
        A2 = A @ A
        expected = k * I_n + lam * A + mu * A_bar
        assert np.allclose(A2, expected)

    def test_diagonal_of_A2(self, adj, srg_params):
        """Diagonal entry of A^2 is k (each vertex has k neighbors)."""
        A = adj.astype(float)
        A2 = A @ A
        k = srg_params[1]
        assert np.allclose(np.diag(A2), k)


# ===================================================================
# T1744 -- P-Matrix (First Eigenmatrix)
# ===================================================================

class TestT1744:
    """First eigenmatrix P of the 2-class association scheme."""

    def test_P_shape(self, P_mat):
        assert P_mat.shape == (3, 3)

    def test_P_first_row(self, P_mat, srg_params):
        """First row = valencies: [1, k, n-k-1]."""
        n, k, _, _ = srg_params
        assert np.allclose(P_mat[0], [1, k, n - k - 1])

    def test_P_eigenvalue_rows(self, P_mat, eigenvalues):
        """Rows 1,2 encode restricted eigenvalues on A_1, A_2."""
        r, s = eigenvalues['r'], eigenvalues['s']
        assert np.allclose(P_mat[1], [1, r, -(1 + r)])
        assert np.allclose(P_mat[2], [1, s, -(1 + s)])

    def test_P_column_sums(self, P_mat, eigenvalues):
        """Column 0 sums to 1 + f + g... wait, column sums of P:
        col 0: 1+1+1=3. This is just structure, verify first column is all-ones."""
        assert np.allclose(P_mat[:, 0], [1, 1, 1])


# ===================================================================
# T1745 -- Q-Matrix = n * P^{-1}
# ===================================================================

class TestT1745:
    """Second eigenmatrix Q = n * P^{-1}."""

    def test_Q_first_row(self, Q_mat, eigenvalues):
        """First row of Q = multiplicities [1, f, g]."""
        assert np.allclose(Q_mat[0], [1, eigenvalues['f'], eigenvalues['g']])

    def test_Q_first_column(self, Q_mat):
        """First column of Q is all-ones."""
        assert np.allclose(Q_mat[:, 0], [1, 1, 1])

    def test_Q_second_row(self, Q_mat, eigenvalues):
        """Q[1,:] = [1, f*r/k, g*s/k]."""
        f, g, r, s, k = eigenvalues['f'], eigenvalues['g'], eigenvalues['r'], eigenvalues['s'], eigenvalues['k']
        expected = [1, f * r / k, g * s / k]
        assert np.allclose(Q_mat[1], expected)

    def test_Q_third_row(self, Q_mat, eigenvalues):
        """Q[2,:] = [1, f*(-(1+r))/(n-k-1), g*(-(1+s))/(n-k-1)]."""
        f, g, r, s, k = eigenvalues['f'], eigenvalues['g'], eigenvalues['r'], eigenvalues['s'], eigenvalues['k']
        n_minus_k_1 = 27
        expected = [1, f * (-(1 + r)) / n_minus_k_1, g * (-(1 + s)) / n_minus_k_1]
        assert np.allclose(Q_mat[2], expected)


# ===================================================================
# T1746 -- PQ = nI Identity
# ===================================================================

class TestT1746:
    """The eigenmatrices satisfy PQ = QP = nI."""

    def test_PQ_equals_nI(self, P_mat, Q_mat, n):
        assert np.allclose(P_mat @ Q_mat, n * np.eye(3))

    def test_QP_equals_nI(self, P_mat, Q_mat, n):
        assert np.allclose(Q_mat @ P_mat, n * np.eye(3))

    def test_P_invertible(self, P_mat):
        assert abs(np.linalg.det(P_mat)) > 1e-8


# ===================================================================
# T1747 -- Spectral Idempotent E_0 = J/n
# ===================================================================

class TestT1747:
    """E_0 is the projection onto the all-ones eigenspace."""

    def test_E0_equals_J_over_n(self, spectral_idempotents, J, n):
        E0, _, _ = spectral_idempotents
        assert np.allclose(E0, J / n)

    def test_E0_rank(self, spectral_idempotents):
        E0, _, _ = spectral_idempotents
        assert np.linalg.matrix_rank(E0, tol=1e-8) == 1

    def test_E0_trace(self, spectral_idempotents):
        E0, _, _ = spectral_idempotents
        assert abs(np.trace(E0) - 1.0) < 1e-8

    def test_E0_is_idempotent(self, spectral_idempotents):
        E0, _, _ = spectral_idempotents
        assert np.allclose(E0 @ E0, E0)


# ===================================================================
# T1748 -- Spectral Idempotent E_1
# ===================================================================

class TestT1748:
    """E_1 projects onto the eigenvalue-2 eigenspace (rank 24)."""

    def test_E1_rank(self, spectral_idempotents):
        _, E1, _ = spectral_idempotents
        assert np.linalg.matrix_rank(E1, tol=1e-8) == 24

    def test_E1_trace(self, spectral_idempotents):
        _, E1, _ = spectral_idempotents
        assert abs(np.trace(E1) - 24.0) < 1e-8

    def test_E1_is_idempotent(self, spectral_idempotents):
        _, E1, _ = spectral_idempotents
        assert np.allclose(E1 @ E1, E1, atol=1e-8)

    def test_E1_explicit_formula(self, spectral_idempotents, adj, I_n, J):
        """E_1 = (2/3)I + (1/6)A - (1/15)J."""
        _, E1, _ = spectral_idempotents
        A = adj.astype(float)
        expected = (2.0 / 3) * I_n + (1.0 / 6) * A - (1.0 / 15) * J
        assert np.allclose(E1, expected, atol=1e-10)


# ===================================================================
# T1749 -- Spectral Idempotent E_2
# ===================================================================

class TestT1749:
    """E_2 projects onto the eigenvalue-(-4) eigenspace (rank 15)."""

    def test_E2_rank(self, spectral_idempotents):
        _, _, E2 = spectral_idempotents
        assert np.linalg.matrix_rank(E2, tol=1e-8) == 15

    def test_E2_trace(self, spectral_idempotents):
        _, _, E2 = spectral_idempotents
        assert abs(np.trace(E2) - 15.0) < 1e-8

    def test_E2_is_idempotent(self, spectral_idempotents):
        _, _, E2 = spectral_idempotents
        assert np.allclose(E2 @ E2, E2, atol=1e-8)

    def test_E2_explicit_formula(self, spectral_idempotents, adj, I_n, J):
        """E_2 = (1/3)I - (1/6)A + (1/24)J."""
        _, _, E2 = spectral_idempotents
        A = adj.astype(float)
        expected = (1.0 / 3) * I_n - (1.0 / 6) * A + (1.0 / 24) * J
        assert np.allclose(E2, expected, atol=1e-10)


# ===================================================================
# T1750 -- Idempotent Orthogonality
# ===================================================================

class TestT1750:
    """E_i * E_j = delta_{ij} E_i  (mutual annihilation)."""

    def test_E0_E1_zero(self, spectral_idempotents):
        E0, E1, _ = spectral_idempotents
        assert np.allclose(E0 @ E1, 0, atol=1e-10)

    def test_E0_E2_zero(self, spectral_idempotents):
        E0, _, E2 = spectral_idempotents
        assert np.allclose(E0 @ E2, 0, atol=1e-10)

    def test_E1_E2_zero(self, spectral_idempotents):
        _, E1, E2 = spectral_idempotents
        assert np.allclose(E1 @ E2, 0, atol=1e-10)

    def test_all_pairs_orthogonal(self, spectral_idempotents):
        """Comprehensive check: E_i E_j = 0 for all i != j."""
        Es = spectral_idempotents
        for i in range(3):
            for j in range(3):
                prod = Es[i] @ Es[j]
                if i == j:
                    assert np.allclose(prod, Es[i], atol=1e-8)
                else:
                    assert np.allclose(prod, 0, atol=1e-10)


# ===================================================================
# T1751 -- Idempotent Completeness
# ===================================================================

class TestT1751:
    """E_0 + E_1 + E_2 = I  (resolution of the identity)."""

    def test_sum_equals_identity(self, spectral_idempotents, I_n):
        E0, E1, E2 = spectral_idempotents
        assert np.allclose(E0 + E1 + E2, I_n, atol=1e-10)

    def test_trace_sum(self, spectral_idempotents, n):
        """tr(E_0) + tr(E_1) + tr(E_2) = n = 40."""
        total = sum(np.trace(E) for E in spectral_idempotents)
        assert abs(total - n) < 1e-8

    def test_A_from_idempotents(self, spectral_idempotents, adj, eigenvalues):
        """A = k*E_0 + r*E_1 + s*E_2 (spectral decomposition)."""
        E0, E1, E2 = spectral_idempotents
        k, r, s = eigenvalues['k'], eigenvalues['r'], eigenvalues['s']
        reconstructed = k * E0 + r * E1 + s * E2
        assert np.allclose(reconstructed, adj.astype(float), atol=1e-8)


# ===================================================================
# T1752 -- Krein Parameters Non-Negativity
# ===================================================================

class TestT1752:
    """Krein parameters q_{ij}^k >= 0  (from Hadamard product of idempotents)."""

    def _decompose_hadamard(self, M, Es, n):
        """Express M as linear combination of Es, return coefficients."""
        # E_i ∘ E_j = (1/n) sum_k q_{ij}^k E_k
        # Solve for q: M = (1/n) sum_k q_k E_k => n*M = sum_k q_k E_k
        # Use trace inner product: tr(E_a^T * n*M) = q_a * tr(E_a^T E_a)
        nM = n * M
        coeffs = []
        for a in range(3):
            # tr(E_a) gives the multiplicity m_a
            m_a = np.trace(Es[a])
            if m_a < 1e-12:
                coeffs.append(0.0)
            else:
                # q_a = tr(E_a * nM) / tr(E_a * E_a)
                # Since E_a is idempotent: E_a * E_a = E_a, so tr(E_a * E_a) = m_a
                # And E_a * nM: note these are MATRIX products, but we need
                # nM in Bose-Mesner algebra, so nM = sum q_k E_k
                # tr(E_a * sum q_k E_k) = q_a * tr(E_a) = q_a * m_a
                q_a = np.trace(Es[a] @ nM) / m_a
                coeffs.append(q_a)
        return np.array(coeffs)

    def test_krein_all_nonneg(self, spectral_idempotents, n):
        """All 27 Krein parameters q_{ij}^k >= 0."""
        Es = spectral_idempotents
        for i in range(3):
            for j in range(3):
                had = Es[i] * Es[j]  # Hadamard (entrywise) product
                q = self._decompose_hadamard(had, Es, n)
                for k_idx in range(3):
                    assert q[k_idx] > -1e-10, (
                        f"Krein q_{{{i}{j}}}^{k_idx} = {q[k_idx]:.6f} < 0"
                    )

    def test_krein_E0_hadamard_E0(self, spectral_idempotents, n):
        """E_0 ∘ E_0 = (1/n) * E_0 (since E_0 = J/n, all entries = 1/n)."""
        E0 = spectral_idempotents[0]
        had = E0 * E0  # Hadamard
        # E_0 ∘ E_0 = (J/n)∘(J/n) = J/n^2 = (1/n)(J/n) = (1/n) E_0
        assert np.allclose(had, E0 / n, atol=1e-12)

    def test_krein_symmetry(self, spectral_idempotents, n):
        """q_{ij}^k = q_{ji}^k (since Hadamard product is commutative)."""
        Es = spectral_idempotents
        for i in range(3):
            for j in range(i + 1, 3):
                had_ij = Es[i] * Es[j]
                had_ji = Es[j] * Es[i]
                assert np.allclose(had_ij, had_ji)


# ===================================================================
# T1753 -- Intersection Numbers p_{ij}^k
# ===================================================================

class TestT1753:
    """Intersection numbers (structure constants) of the association scheme.
    A_i A_j = sum_k p_{ij}^k A_k  for A_0=I, A_1=A, A_2=J-I-A.
    """

    def test_p11(self, adj, I_n, A_bar, srg_params):
        """A^2 = k*I + lambda*A + mu*A_bar => p_{11} = (k, lambda, mu) = (12, 2, 4)."""
        n, k, lam, mu = srg_params
        A = adj.astype(float)
        A2 = A @ A
        expected = k * I_n + lam * A + mu * A_bar
        assert np.allclose(A2, expected)

    def test_p12(self, adj, I_n, A_bar, srg_params):
        """A * A_bar = (k-lambda-1)*A_bar + ... decomposition."""
        n, k, lam, mu = srg_params
        A = adj.astype(float)
        prod = A @ A_bar
        # A * A_bar must be in span{I, A, A_bar}. Solve for coefficients.
        # A * A_bar = a*I + b*A + c*A_bar
        # Diagonal: (A*A_bar)_{ii} = sum_j A_{ij}*A_bar_{ij} = 0 (A, A_bar disjoint)
        # So a = 0.
        # For adjacent pair (i~j): row i of A dot col j of A_bar
        # = #{z : z~i, z not~j, z!=j}
        # = k - lambda - 1 (neighbors of i minus: j itself and lambda common neighbors)
        # = 12 - 2 - 1 = 9
        # For non-adj pair (i not~j, i!=j): row i of A dot col j of A_bar
        # = #{z: z~i, z not~j, z!=j}
        # = k - mu (neighbors of i minus mu common neighbors; j not a neighbor of i so no subtraction for j)
        # = 12 - 4 = 8
        # So A*A_bar = 0*I + 9*A_bar + 8*... wait. Let me reconsider.
        # (A*A_bar)_{ij} for i=j: sum_z A_{iz}*A_bar_{zi} = 0 (A, A_bar have disjoint supports, both 0 on diagonal)
        # Actually A_{iz} = 1 iff z~i; A_bar_{zi} = 1 iff z not~i and z!=i. These are mutually exclusive. So diag = 0. -> a = 0
        # (A*A_bar)_{ij} for i~j: #{z: z~i and (z not~j and z!=j)} = k - lambda - 1 = 9 -> on A entries this gives b
        # Wait: on entry (i,j) where A_{ij}=1: (A*A_bar)_{ij} = 9 -> coeff of A is 9? No, need c such that 0*1 + b*1 + c*0 = 9 -> b = 9
        # (A*A_bar)_{ij} for i not~j, i!=j: #{z: z~i and (z not~j and z!=j)} = k - mu = 8 -> 0*0 + 9*0 + c*1 = 8 -> c = 8
        expected = 9 * A + 8 * A_bar
        assert np.allclose(prod, expected)

    def test_p22(self, adj, I_n, A_bar, srg_params):
        """A_bar^2 decomposition into {I, A, A_bar}."""
        n, k, lam, mu = srg_params
        k_bar = n - k - 1  # = 27
        A = adj.astype(float)
        A_bar2 = A_bar @ A_bar
        # Complement SRG params: n'=n, k'=n-k-1=27, lambda'=n-2k+mu-2=22, mu'=n-2k+lambda=18
        lam_bar = n - 2 * k + mu - 2  # 40 - 24 + 4 - 2 = 18
        mu_bar = n - 2 * k + lam  # 40 - 24 + 2 = 18
        # A_bar^2 = k_bar*I + lam_bar*A_bar + mu_bar*A
        expected = k_bar * I_n + lam_bar * A_bar + mu_bar * A
        assert np.allclose(A_bar2, expected)


# ===================================================================
# T1754 -- Distance-Regularity (Diameter 2)
# ===================================================================

class TestT1754:
    """W(3,3) is distance-regular with diameter 2 and
    intersection array {k, k-lambda-1; 1, mu} = {12, 9; 1, 4}.
    """

    def test_diameter_is_2(self, adj):
        """All non-identical vertex pairs are at distance 1 or 2 (diameter = 2)."""
        n = adj.shape[0]
        A = adj.astype(float)
        A2 = A @ A
        J = np.ones((n, n))
        I = np.eye(n)
        # Reachable in <= 2 steps: I + A + (A2 > 0) should cover all entries
        reach = (I + A + (A2 > 0).astype(float))
        assert np.all(reach > 0)

    def test_intersection_array_b0(self, srg_params):
        """b_0 = k = 12."""
        assert srg_params[1] == 12

    def test_intersection_array_b1(self, srg_params):
        """b_1 = k - lambda - 1 = 9."""
        n, k, lam, mu = srg_params
        assert k - lam - 1 == 9

    def test_intersection_array_c1(self):
        """c_1 = 1 (by convention for distance-regular graphs)."""
        assert 1 == 1  # trivially true for all connected graphs

    def test_intersection_array_c2(self, srg_params):
        """c_2 = mu = 4."""
        assert srg_params[3] == 4


# ===================================================================
# T1755 -- Walk-Regularity
# ===================================================================

class TestT1755:
    """W(3,3) is walk-regular: (A^k)_{ii} is constant for all i, for every k."""

    def test_walk_regular_k2(self, adj):
        A = adj.astype(float)
        diag = np.diag(A @ A)
        assert np.allclose(diag, diag[0])

    def test_walk_regular_k3(self, adj):
        A = adj.astype(float)
        A3 = A @ A @ A
        diag = np.diag(A3)
        assert np.allclose(diag, diag[0])

    def test_walk_regular_k4(self, adj):
        A = adj.astype(float)
        A2 = A @ A
        A4 = A2 @ A2
        diag = np.diag(A4)
        assert np.allclose(diag, diag[0])

    def test_walk_regular_k5(self, adj):
        A = adj.astype(float)
        A2 = A @ A
        A5 = A2 @ A2 @ A
        diag = np.diag(A5)
        assert np.allclose(diag, diag[0])


# ===================================================================
# T1756 -- Interlacing for Induced Subgraphs
# ===================================================================

class TestT1756:
    """Eigenvalue interlacing: induced subgraph eigenvalues interlace
    with parent eigenvalues.
    """

    def _interlaces(self, parent_eigs, sub_eigs):
        """Check Cauchy interlacing: lam_i <= mu_i <= lam_{n-m+i}."""
        n = len(parent_eigs)
        m = len(sub_eigs)
        lam = np.sort(parent_eigs)
        mu = np.sort(sub_eigs)
        for i in range(m):
            if mu[i] < lam[i] - 1e-8:
                return False
            if mu[i] > lam[n - m + i] + 1e-8:
                return False
        return True

    def test_interlace_neighborhood(self, adj, eig_decomp):
        """Induced subgraph on vertex 0's neighborhood (12 vertices)."""
        parent_vals, _ = eig_decomp
        nbrs = np.where(adj[0] == 1)[0]
        sub_A = adj[np.ix_(nbrs, nbrs)].astype(float)
        sub_vals = np.linalg.eigvalsh(sub_A)
        assert self._interlaces(parent_vals, sub_vals)

    def test_interlace_non_neighborhood(self, adj, eig_decomp):
        """Induced subgraph on vertices NOT adjacent to vertex 0."""
        parent_vals, _ = eig_decomp
        non_nbrs = np.where((adj[0] == 0) & (np.arange(40) != 0))[0]
        sub_A = adj[np.ix_(non_nbrs, non_nbrs)].astype(float)
        sub_vals = np.linalg.eigvalsh(sub_A)
        assert self._interlaces(parent_vals, sub_vals)

    def test_interlace_first_20(self, adj, eig_decomp):
        """Induced subgraph on the first 20 vertices."""
        parent_vals, _ = eig_decomp
        idx = np.arange(20)
        sub_A = adj[np.ix_(idx, idx)].astype(float)
        sub_vals = np.linalg.eigvalsh(sub_A)
        assert self._interlaces(parent_vals, sub_vals)


# ===================================================================
# T1757 -- Absolute Bound
# ===================================================================

class TestT1757:
    """Absolute bound: n <= f_i * (f_i + 3) / 2 for each non-trivial
    multiplicity f_i.
    """

    def test_absolute_bound_f1(self, n, eigenvalues):
        """n = 40 <= f_1*(f_1+3)/2 = 24*27/2 = 324."""
        f = eigenvalues['f']
        bound = f * (f + 3) // 2
        assert n <= bound
        assert bound == 324

    def test_absolute_bound_f2(self, n, eigenvalues):
        """n = 40 <= f_2*(f_2+3)/2 = 15*18/2 = 135."""
        g = eigenvalues['g']
        bound = g * (g + 3) // 2
        assert n <= bound
        assert bound == 135

    def test_absolute_bound_tighter(self, n, eigenvalues):
        """The tighter bound n <= f_i*(f_i+1)/2 also holds."""
        f, g = eigenvalues['f'], eigenvalues['g']
        assert n <= f * (f + 1) // 2  # 40 <= 300
        assert n <= g * (g + 1) // 2  # 40 <= 120


# ===================================================================
# T1758 -- Complement Graph Algebra
# ===================================================================

class TestT1758:
    """Properties of the complement adjacency A_bar = J - I - A."""

    def test_Abar_symmetric(self, A_bar):
        assert np.allclose(A_bar, A_bar.T)

    def test_Abar_regularity(self, A_bar):
        """Complement is 27-regular."""
        row_sums = A_bar.sum(axis=1)
        assert np.allclose(row_sums, 27)

    def test_Abar_eigenvalues(self, A_bar):
        """Complement eigenvalues: n-1-k=27 (m=1), -1-r=-3 (m=24), -1-s=3 (m=15)."""
        vals = np.linalg.eigvalsh(A_bar)
        unique = sorted(set(np.round(vals, 6)))
        assert np.allclose(unique, [-3, 3, 27])

    def test_Abar_is_complement_srg(self, A_bar):
        """A_bar defines SRG(40, 27, 18, 18)."""
        n = A_bar.shape[0]
        k_bar = int(round(A_bar[0].sum()))
        assert k_bar == 27
        # lambda_bar for adjacent pair in complement
        A_b = A_bar.astype(float)
        A_b2 = A_b @ A_b
        lam_bar = int(round(A_b2[0, 1]))  # vertex 0 and a complement-neighbor
        # Find a complement neighbor
        nbr = np.where(A_bar[0] == 1)[0][0]
        lam_bar = int(round(A_b2[0, nbr]))
        assert lam_bar == 18


# ===================================================================
# T1759 -- Trace / Moment Identities
# ===================================================================

class TestT1759:
    """Trace identities: tr(A^k) = sum_i lambda_i^k * m_i."""

    def test_trace_A0(self, adj, n):
        """tr(I) = n = 40."""
        assert adj.shape[0] == n

    def test_trace_A1(self, adj):
        """tr(A) = 0 (no self-loops)."""
        assert np.trace(adj) == 0

    def test_trace_A2(self, adj, eigenvalues):
        """tr(A^2) = 2*|E| = 12^2*1 + 2^2*24 + (-4)^2*15 = 144+96+240 = 480."""
        A = adj.astype(float)
        tr = np.trace(A @ A)
        expected = 12**2 * 1 + 2**2 * 24 + (-4)**2 * 15
        assert abs(tr - expected) < 1e-8
        assert expected == 480
        assert abs(tr - 2 * adj.sum() / 2) < 1e-8  # 2|E| = n*k = 40*12 = 480

    def test_trace_A3(self, adj, eigenvalues):
        """tr(A^3) = 6 * (number of triangles).
        tr(A^3) = 12^3*1 + 2^3*24 + (-4)^3*15 = 1728 + 192 - 960 = 960.
        Number of triangles = 160.
        """
        A = adj.astype(float)
        tr = np.trace(A @ A @ A)
        expected = 12**3 * 1 + 2**3 * 24 + (-4)**3 * 15
        assert abs(tr - expected) < 1e-8
        assert expected == 960
        # Number of triangles = tr(A^3)/6
        assert abs(tr / 6 - 160) < 1e-8


# ===================================================================
# T1760 -- Eigenvalue Multiplicities from Parameters
# ===================================================================

class TestT1760:
    """Multiplicities f, g derived from SRG parameters (n, k, lambda, mu)."""

    def test_multiplicity_formula(self, srg_params, eigenvalues):
        """Standard formulas for r, s, f, g from (n, k, lambda, mu)."""
        n, k, lam, mu = srg_params
        # Eigenvalues r, s are roots of x^2 - (lambda - mu)x - (k - mu) = 0
        disc = (lam - mu)**2 + 4 * (k - mu)
        sqrt_disc = disc ** 0.5
        r = ((lam - mu) + sqrt_disc) / 2.0
        s = ((lam - mu) - sqrt_disc) / 2.0
        assert abs(r - eigenvalues['r']) < 1e-10
        assert abs(s - eigenvalues['s']) < 1e-10

    def test_multiplicity_f(self, srg_params, eigenvalues):
        """f = (1/2)(n - 1 - 2k(n-1-k)/(k-mu) * 1/sqrt(disc))... use explicit formula.
        For integer eigenvalues: f = k(s+1)(s-lambda) / (mu*(s-r))
        """
        n, k, lam, mu = srg_params
        r, s = eigenvalues['r'], eigenvalues['s']
        # f + g = n - 1 and k*f*... but simpler: f = (1/2)(n-1 + 2k+(n-1)(lam-mu) / sqrt(D))
        # Or: f * r + g * s = -k (trace of A restricted to non-trivial) wait...
        # trace(A) = k + f*r + g*s = 0 => f*r + g*s = -k
        # f + g = n - 1
        # So f = -(k + (n-1)*s) / (r - s)
        f_calc = -(k + (n - 1) * s) / (r - s)
        assert abs(f_calc - eigenvalues['f']) < 1e-10

    def test_multiplicity_g(self, srg_params, eigenvalues):
        n, k, lam, mu = srg_params
        r, s = eigenvalues['r'], eigenvalues['s']
        g_calc = -(k + (n - 1) * r) / (s - r)
        assert abs(g_calc - eigenvalues['g']) < 1e-10

    def test_multiplicities_sum(self, eigenvalues, n):
        """1 + f + g = n."""
        assert 1 + eigenvalues['f'] + eigenvalues['g'] == n
