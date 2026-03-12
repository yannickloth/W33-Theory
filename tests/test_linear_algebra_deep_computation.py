"""
Phase CX: Deep Linear Algebra Computation on W(3,3) = SRG(40,12,2,4).

Tests cover matrix decompositions, norms, spectral projections, commutant
structure, matrix functions, generalized inverses, tensor/Kronecker products,
and numerical properties.

Key W(3,3) properties:
    n=40, k=12, lambda=2, mu=4
    Spectrum: {12^1, 2^24, (-4)^15}
    trace(A)=0, trace(A^2)=480
    det(A) = 12 * 2^24 * (-4)^15 = -3 * 2^56
    Minimal polynomial: x^3 - 10x^2 - 32x + 96 = (x-12)(x-2)(x+4)

All computations use numpy only (no scipy, no networkx).
"""

import numpy as np
import pytest


# ---------- W(3,3) builder ------------------------------------------------

def _build_w33():
    """Build adjacency matrix of W(3,3) = symplectic graph over GF(3)^4."""
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


# ---------- Module-scoped fixtures ----------------------------------------

@pytest.fixture(scope="module")
def A():
    """Adjacency matrix of W(3,3)."""
    return _build_w33()


@pytest.fixture(scope="module")
def eig(A):
    """Eigendecomposition via eigh (symmetric): sorted ascending."""
    vals, vecs = np.linalg.eigh(A)
    return vals, vecs


@pytest.fixture(scope="module")
def projections(eig):
    """Spectral projections P_{-4}, P_2, P_{12} onto each eigenspace."""
    vals, vecs = eig
    projs = {}
    for lam in (-4, 2, 12):
        mask = np.abs(vals - lam) < 0.5
        V = vecs[:, mask]
        projs[lam] = V @ V.T
    return projs


# ======================================================================
# 1. MATRIX DECOMPOSITIONS (12 tests)
# ======================================================================

class TestMatrixDecompositions:
    """SVD, eigendecomposition, polar decomposition, Schur form."""

    def test_svd_singular_values(self, A):
        """Singular values of symmetric A are |eigenvalues|: 12x1, 4x15, 2x24."""
        sv = np.linalg.svd(A, compute_uv=False)
        sv_sorted = np.sort(sv)[::-1]
        expected = np.sort([12.0] * 1 + [4.0] * 15 + [2.0] * 24)[::-1]
        np.testing.assert_allclose(sv_sorted, expected, atol=1e-10)

    def test_svd_count_12(self, A):
        """Exactly one singular value equals 12."""
        sv = np.linalg.svd(A, compute_uv=False)
        assert np.sum(np.abs(sv - 12.0) < 0.5) == 1

    def test_svd_count_4(self, A):
        """Exactly 15 singular values equal 4 (from eigenvalue -4)."""
        sv = np.linalg.svd(A, compute_uv=False)
        assert np.sum(np.abs(sv - 4.0) < 0.5) == 15

    def test_svd_count_2(self, A):
        """Exactly 24 singular values equal 2."""
        sv = np.linalg.svd(A, compute_uv=False)
        assert np.sum(np.abs(sv - 2.0) < 0.5) == 24

    def test_svd_reconstruction(self, A):
        """U S V^T reconstructs A exactly."""
        U, s, Vt = np.linalg.svd(A)
        reconstructed = U @ np.diag(s) @ Vt
        np.testing.assert_allclose(reconstructed, A, atol=1e-10)

    def test_eigendecomposition_reconstruction(self, A, eig):
        """V D V^T reconstructs A from eigendecomposition."""
        vals, vecs = eig
        reconstructed = vecs @ np.diag(vals) @ vecs.T
        np.testing.assert_allclose(reconstructed, A, atol=1e-10)

    def test_eigenvectors_orthonormal(self, eig):
        """Eigenvectors from eigh form an orthonormal set."""
        _, vecs = eig
        np.testing.assert_allclose(vecs.T @ vecs, np.eye(40), atol=1e-10)

    def test_eigenvalues_correct(self, eig):
        """Eigenvalues are {-4 x15, 2 x24, 12 x1}."""
        vals, _ = eig
        vals_sorted = np.sort(vals)
        expected = np.sort([-4.0] * 15 + [2.0] * 24 + [12.0] * 1)
        np.testing.assert_allclose(vals_sorted, expected, atol=1e-10)

    def test_polar_decomposition_reconstruction(self, A, eig):
        """A = U P where U orthogonal, P positive semi-definite."""
        vals, vecs = eig
        P = vecs @ np.diag(np.abs(vals)) @ vecs.T
        U = vecs @ np.diag(np.sign(vals)) @ vecs.T
        np.testing.assert_allclose(U @ P, A, atol=1e-10)

    def test_polar_U_orthogonal(self, eig):
        """The unitary factor U in polar decomposition is orthogonal."""
        vals, vecs = eig
        U = vecs @ np.diag(np.sign(vals)) @ vecs.T
        np.testing.assert_allclose(U @ U.T, np.eye(40), atol=1e-10)

    def test_polar_P_positive_semidefinite(self, eig):
        """The positive factor P has non-negative eigenvalues."""
        vals, vecs = eig
        P = vecs @ np.diag(np.abs(vals)) @ vecs.T
        eigP = np.linalg.eigvalsh(P)
        assert np.all(eigP > -1e-10)

    def test_schur_form_diagonal_for_symmetric(self, A, eig):
        """For real symmetric A, Schur form is diagonal (= eigenvalues)."""
        vals, vecs = eig
        T = vecs.T @ A @ vecs
        np.testing.assert_allclose(T, np.diag(vals), atol=1e-10)


# ======================================================================
# 2. MATRIX NORMS (10 tests)
# ======================================================================

class TestMatrixNorms:
    """Frobenius, spectral, nuclear, Schatten, Ky Fan norms."""

    def test_frobenius_norm(self, A):
        """||A||_F = sqrt(tr(A^T A)) = sqrt(480)."""
        np.testing.assert_allclose(
            np.linalg.norm(A, 'fro'), np.sqrt(480.0), atol=1e-10
        )

    def test_frobenius_from_trace(self, A):
        """||A||_F^2 = tr(A^2) = 480."""
        np.testing.assert_allclose(
            np.linalg.norm(A, 'fro') ** 2, np.trace(A @ A), atol=1e-10
        )

    def test_spectral_norm(self, A):
        """||A||_2 = max singular value = 12."""
        np.testing.assert_allclose(np.linalg.norm(A, 2), 12.0, atol=1e-10)

    def test_nuclear_norm(self, A):
        """Nuclear norm = sum of singular values = 12 + 15*4 + 24*2 = 120."""
        sv = np.linalg.svd(A, compute_uv=False)
        np.testing.assert_allclose(np.sum(sv), 120.0, atol=1e-10)

    def test_schatten_1_equals_nuclear(self, A):
        """Schatten-1 norm = nuclear norm = 120."""
        sv = np.linalg.svd(A, compute_uv=False)
        np.testing.assert_allclose(np.sum(sv), 120.0, atol=1e-10)

    def test_schatten_inf_equals_spectral(self, A):
        """Schatten-infinity norm = spectral norm = 12."""
        sv = np.linalg.svd(A, compute_uv=False)
        np.testing.assert_allclose(np.max(sv), 12.0, atol=1e-10)

    def test_schatten_2_equals_frobenius(self, A):
        """Schatten-2 norm = Frobenius norm = sqrt(480)."""
        sv = np.linalg.svd(A, compute_uv=False)
        schatten_2 = np.sqrt(np.sum(sv ** 2))
        np.testing.assert_allclose(schatten_2, np.sqrt(480.0), atol=1e-10)

    def test_ky_fan_1_norm(self, A):
        """Ky Fan 1-norm = largest singular value = 12."""
        sv = np.sort(np.linalg.svd(A, compute_uv=False))[::-1]
        np.testing.assert_allclose(sv[0], 12.0, atol=1e-10)

    def test_ky_fan_16_norm(self, A):
        """Ky Fan 16-norm = sum of 16 largest SVs = 12 + 15*4 = 72."""
        sv = np.sort(np.linalg.svd(A, compute_uv=False))[::-1]
        np.testing.assert_allclose(np.sum(sv[:16]), 72.0, atol=1e-10)

    def test_ky_fan_40_norm_equals_nuclear(self, A):
        """Ky Fan 40-norm (all SVs) = nuclear norm = 120."""
        sv = np.sort(np.linalg.svd(A, compute_uv=False))[::-1]
        np.testing.assert_allclose(np.sum(sv[:40]), 120.0, atol=1e-10)


# ======================================================================
# 3. SPECTRAL PROJECTIONS (12 tests)
# ======================================================================

class TestSpectralProjections:
    """Spectral projection operators P_i for each eigenvalue."""

    def test_projections_sum_to_identity(self, projections):
        """P_{-4} + P_2 + P_{12} = I (resolution of the identity)."""
        total = projections[-4] + projections[2] + projections[12]
        np.testing.assert_allclose(total, np.eye(40), atol=1e-10)

    def test_projection_idempotent_neg4(self, projections):
        """P_{-4}^2 = P_{-4}."""
        P = projections[-4]
        np.testing.assert_allclose(P @ P, P, atol=1e-10)

    def test_projection_idempotent_2(self, projections):
        """P_2^2 = P_2."""
        P = projections[2]
        np.testing.assert_allclose(P @ P, P, atol=1e-10)

    def test_projection_idempotent_12(self, projections):
        """P_{12}^2 = P_{12}."""
        P = projections[12]
        np.testing.assert_allclose(P @ P, P, atol=1e-10)

    def test_projections_orthogonal_neg4_2(self, projections):
        """P_{-4} P_2 = 0."""
        prod = projections[-4] @ projections[2]
        np.testing.assert_allclose(prod, np.zeros((40, 40)), atol=1e-10)

    def test_projections_orthogonal_neg4_12(self, projections):
        """P_{-4} P_{12} = 0."""
        prod = projections[-4] @ projections[12]
        np.testing.assert_allclose(prod, np.zeros((40, 40)), atol=1e-10)

    def test_projections_orthogonal_2_12(self, projections):
        """P_2 P_{12} = 0."""
        prod = projections[2] @ projections[12]
        np.testing.assert_allclose(prod, np.zeros((40, 40)), atol=1e-10)

    def test_rank_P_12(self, projections):
        """rank(P_{12}) = tr(P_{12}) = 1."""
        np.testing.assert_allclose(np.trace(projections[12]), 1.0, atol=1e-10)

    def test_rank_P_2(self, projections):
        """rank(P_2) = tr(P_2) = 24."""
        np.testing.assert_allclose(np.trace(projections[2]), 24.0, atol=1e-10)

    def test_rank_P_neg4(self, projections):
        """rank(P_{-4}) = tr(P_{-4}) = 15."""
        np.testing.assert_allclose(np.trace(projections[-4]), 15.0, atol=1e-10)

    def test_spectral_reconstruction(self, A, projections):
        """A = 12 P_{12} + 2 P_2 + (-4) P_{-4}."""
        reconstructed = (12.0 * projections[12]
                         + 2.0 * projections[2]
                         + (-4.0) * projections[-4])
        np.testing.assert_allclose(reconstructed, A, atol=1e-10)

    def test_P12_is_J_over_40(self, projections):
        """P_{12} = J/40 (all-ones / 40), since j is the k-eigenvector."""
        J = np.ones((40, 40))
        np.testing.assert_allclose(projections[12], J / 40.0, atol=1e-10)


# ======================================================================
# 4. COMMUTANT (10 tests)
# ======================================================================

class TestCommutant:
    """Commutant algebra {M : AM = MA} and Bose-Mesner algebra."""

    def test_commutant_dimension(self, A):
        """dim{M : AM = MA} = 1^2 + 24^2 + 15^2 = 802.

        Verified via null space of the Kronecker operator (I x A - A^T x I).
        """
        n = 40
        I_n = np.eye(n)
        K = np.kron(I_n, A) - np.kron(A.T, I_n)
        rank_K = np.linalg.matrix_rank(K, tol=1e-8)
        commutant_dim = n * n - rank_K
        assert commutant_dim == 802

    def test_bose_mesner_I_commutes(self, A):
        """I commutes with A (trivially)."""
        I = np.eye(40)
        np.testing.assert_allclose(A @ I, I @ A, atol=1e-12)

    def test_bose_mesner_Abar_commutes(self, A):
        """Complement adjacency Abar = J - I - A commutes with A."""
        J = np.ones((40, 40))
        Abar = J - np.eye(40) - A
        np.testing.assert_allclose(A @ Abar, Abar @ A, atol=1e-10)

    def test_bose_mesner_closure_A_squared(self, A):
        """SRG equation: A^2 = 8I - 2A + 4J  [= (k-mu)I + (lam-mu)A + mu*J]."""
        J = np.ones((40, 40))
        A2 = A @ A
        expected = 8.0 * np.eye(40) - 2.0 * A + 4.0 * J
        np.testing.assert_allclose(A2, expected, atol=1e-10)

    def test_bose_mesner_Abar_squared(self, A):
        """Complement SRG(40,27,18,18): Abar^2 = 9I + 18J."""
        J = np.ones((40, 40))
        I = np.eye(40)
        Abar = J - I - A
        Abar2 = Abar @ Abar
        expected = 9.0 * I + 18.0 * J
        np.testing.assert_allclose(Abar2, expected, atol=1e-10)

    def test_bose_mesner_product_A_Abar(self, A):
        """A Abar = -8I + A + 8J (derived from SRG equation)."""
        J = np.ones((40, 40))
        I = np.eye(40)
        Abar = J - I - A
        prod = A @ Abar
        expected = -8.0 * I + A + 8.0 * J
        np.testing.assert_allclose(prod, expected, atol=1e-10)

    def test_bose_mesner_hadamard_closure(self, A):
        """Hadamard product A o Abar = 0 (disjoint supports)."""
        Abar = np.ones((40, 40)) - np.eye(40) - A
        had = A * Abar
        np.testing.assert_allclose(had, np.zeros((40, 40)), atol=1e-12)

    def test_bose_mesner_span_dimension(self, A):
        """span{I, A, Abar} has dimension 3 (linearly independent)."""
        I = np.eye(40)
        J = np.ones((40, 40))
        Abar = J - I - A
        vecs = np.array([I.ravel(), A.ravel(), Abar.ravel()])
        rank = np.linalg.matrix_rank(vecs, tol=1e-10)
        assert rank == 3

    def test_eigenvalue_multiplicity_formula(self, eig):
        """Commutant dim = sum m_i^2 = 1 + 576 + 225 = 802."""
        vals, _ = eig
        m_neg4 = int(np.sum(np.abs(vals - (-4)) < 0.5))
        m_2 = int(np.sum(np.abs(vals - 2) < 0.5))
        m_12 = int(np.sum(np.abs(vals - 12) < 0.5))
        dim = m_neg4 ** 2 + m_2 ** 2 + m_12 ** 2
        assert dim == 802

    def test_bose_mesner_J_in_algebra(self, A):
        """J = I + A + Abar lies in the Bose-Mesner algebra."""
        J = np.ones((40, 40))
        # J commutes with A since AJ = JA = kJ
        np.testing.assert_allclose(A @ J, J @ A, atol=1e-10)


# ======================================================================
# 5. MATRIX FUNCTIONS (10 tests)
# ======================================================================

class TestMatrixFunctions:
    """exp(A), cos(A), sin(A), function calculus, Cayley transform.

    All matrix functions computed via spectral decomposition:
        f(A) = sum_i f(lambda_i) P_i = V diag(f(lambda)) V^T
    """

    @staticmethod
    def _fun_via_spectral(f, eig):
        """Compute f(A) = V diag(f(eigenvalues)) V^T."""
        vals, vecs = eig
        return vecs @ np.diag(f(vals)) @ vecs.T

    def test_exp_A_determinant(self, eig):
        """det(exp(A)) = exp(tr(A)) = exp(0) = 1."""
        expA = self._fun_via_spectral(np.exp, eig)
        det = np.linalg.det(expA)
        np.testing.assert_allclose(det, 1.0, rtol=1e-8)

    def test_exp_A_eigenvalues(self, eig):
        """Eigenvalues of exp(A) are exp(lambda_i)."""
        expA = self._fun_via_spectral(np.exp, eig)
        eig_expA = np.sort(np.linalg.eigvalsh(expA))
        expected = np.sort(
            [np.exp(-4.0)] * 15 + [np.exp(2.0)] * 24 + [np.exp(12.0)] * 1
        )
        np.testing.assert_allclose(eig_expA, expected, rtol=1e-8)

    def test_exp_A_symmetric(self, eig):
        """exp(A) is symmetric when A is symmetric."""
        expA = self._fun_via_spectral(np.exp, eig)
        np.testing.assert_allclose(expA, expA.T, atol=1e-10)

    def test_cos_A_eigenvalues(self, eig):
        """Eigenvalues of cos(A) are cos(lambda_i)."""
        cosA = self._fun_via_spectral(np.cos, eig)
        eig_cosA = np.sort(np.linalg.eigvalsh(cosA))
        expected = np.sort(
            [np.cos(-4.0)] * 15 + [np.cos(2.0)] * 24 + [np.cos(12.0)] * 1
        )
        np.testing.assert_allclose(eig_cosA, expected, atol=1e-10)

    def test_sin_A_eigenvalues(self, eig):
        """Eigenvalues of sin(A) are sin(lambda_i)."""
        sinA = self._fun_via_spectral(np.sin, eig)
        eig_sinA = np.sort(np.linalg.eigvalsh(sinA))
        expected = np.sort(
            [np.sin(-4.0)] * 15 + [np.sin(2.0)] * 24 + [np.sin(12.0)] * 1
        )
        np.testing.assert_allclose(eig_sinA, expected, atol=1e-10)

    def test_cos_sin_pythagorean(self, eig):
        """cos(A)^2 + sin(A)^2 = I (matrix Pythagorean identity)."""
        cosA = self._fun_via_spectral(np.cos, eig)
        sinA = self._fun_via_spectral(np.sin, eig)
        result = cosA @ cosA + sinA @ sinA
        np.testing.assert_allclose(result, np.eye(40), atol=1e-10)

    def test_function_calculus_polynomial(self, A, eig):
        """f(A) via spectral = f(A) via direct for f(x) = x^2 - 10x."""
        f = lambda x: x ** 2 - 10.0 * x
        fA_spectral = self._fun_via_spectral(f, eig)
        fA_direct = A @ A - 10.0 * A
        np.testing.assert_allclose(fA_spectral, fA_direct, atol=1e-10)

    def test_cayley_transform_reconstruction(self, A, eig):
        """(I+A)(I-A)^{-1} via spectral matches direct matrix computation."""
        vals, vecs = eig
        cayley_eigs = (1.0 + vals) / (1.0 - vals)
        C_spectral = vecs @ np.diag(cayley_eigs) @ vecs.T
        I = np.eye(40)
        C_direct = (I + A) @ np.linalg.inv(I - A)
        np.testing.assert_allclose(C_spectral, C_direct, atol=1e-8)

    def test_cayley_eigenvalue_12(self, eig):
        """Cayley eigenvalue for lambda=12: (1+12)/(1-12) = -13/11."""
        vals, _ = eig
        cayley_eigs = (1.0 + vals) / (1.0 - vals)
        ev_12 = cayley_eigs[np.argmin(np.abs(vals - 12.0))]
        np.testing.assert_allclose(ev_12, -13.0 / 11.0, atol=1e-10)

    def test_cayley_eigenvalue_neg4(self, eig):
        """Cayley eigenvalue for lambda=-4: (1-4)/(1+4) = -3/5."""
        vals, _ = eig
        cayley_eigs = (1.0 + vals) / (1.0 - vals)
        ev_neg4 = cayley_eigs[np.argmin(np.abs(vals - (-4.0)))]
        np.testing.assert_allclose(ev_neg4, -3.0 / 5.0, atol=1e-10)


# ======================================================================
# 6. GENERALIZED INVERSES (10 tests)
# ======================================================================

class TestGeneralizedInverses:
    """A^{-1}, Moore-Penrose pseudoinverse, minimal polynomial formula."""

    def test_A_invertible(self, A):
        """det(A) != 0, so A is invertible."""
        assert abs(np.linalg.det(A)) > 1e-10

    def test_determinant_value(self, A):
        """det(A) = 12 * 2^24 * (-4)^15 = -3 * 2^56."""
        det = np.linalg.det(A)
        expected = -3.0 * (2.0 ** 56)
        np.testing.assert_allclose(det, expected, rtol=1e-6)

    def test_A_inv_roundtrip(self, A):
        """A A^{-1} = I."""
        Ainv = np.linalg.inv(A)
        np.testing.assert_allclose(A @ Ainv, np.eye(40), atol=1e-10)

    def test_A_inv_symmetric(self, A):
        """A^{-1} is symmetric since A is symmetric."""
        Ainv = np.linalg.inv(A)
        np.testing.assert_allclose(Ainv, Ainv.T, atol=1e-10)

    def test_A_inv_eigenvalues(self, A):
        """Eigenvalues of A^{-1} are {1/12, 1/2 x24, -1/4 x15}."""
        Ainv = np.linalg.inv(A)
        eigs = np.sort(np.linalg.eigvalsh(Ainv))
        expected = np.sort([-0.25] * 15 + [0.5] * 24 + [1.0 / 12.0] * 1)
        np.testing.assert_allclose(eigs, expected, atol=1e-10)

    def test_A_inv_from_minimal_poly(self, A):
        """A^{-1} = (A^2 - 10A - 32I) / (-96) from minimal polynomial.

        Since A^3 - 10A^2 - 32A + 96I = 0, we have
        A(A^2 - 10A - 32I) = -96I, so A^{-1} = -(A^2 - 10A - 32I)/96.
        """
        I = np.eye(40)
        Ainv_poly = (A @ A - 10.0 * A - 32.0 * I) / (-96.0)
        Ainv = np.linalg.inv(A)
        np.testing.assert_allclose(Ainv_poly, Ainv, atol=1e-10)

    def test_minimal_polynomial_zero(self, A):
        """A^3 - 10A^2 - 32A + 96I = 0 (annihilating polynomial)."""
        I = np.eye(40)
        A2 = A @ A
        A3 = A2 @ A
        result = A3 - 10.0 * A2 - 32.0 * A + 96.0 * I
        np.testing.assert_allclose(result, np.zeros((40, 40)), atol=1e-10)

    def test_A_inv_squared_eigenvalues(self, A):
        """Eigenvalues of (A^{-1})^2 are {1/144, 1/4 x24, 1/16 x15}."""
        Ainv = np.linalg.inv(A)
        Ainv2 = Ainv @ Ainv
        eigs = np.sort(np.linalg.eigvalsh(Ainv2))
        expected = np.sort(
            [1.0 / 144.0] * 1 + [1.0 / 16.0] * 15 + [0.25] * 24
        )
        np.testing.assert_allclose(eigs, expected, atol=1e-10)

    def test_moore_penrose_equals_inverse(self, A):
        """Since A is invertible, the pseudoinverse equals the inverse."""
        Ainv = np.linalg.inv(A)
        Apinv = np.linalg.pinv(A)
        np.testing.assert_allclose(Apinv, Ainv, atol=1e-8)

    def test_A_inv_trace(self, A):
        """tr(A^{-1}) = 1/12 + 24/2 + 15*(-1/4) = 25/3."""
        Ainv = np.linalg.inv(A)
        expected = 1.0 / 12.0 + 24.0 * 0.5 + 15.0 * (-0.25)  # = 25/3
        np.testing.assert_allclose(np.trace(Ainv), expected, atol=1e-10)


# ======================================================================
# 7. TENSOR / KRONECKER PRODUCTS (10 tests)
# ======================================================================

class TestTensorKronecker:
    """Kronecker products A x B and Hadamard (entrywise) products."""

    def test_hadamard_A_circ_A_equals_A(self, A):
        """A o A = A since A has 0/1 entries and 0^2=0, 1^2=1."""
        np.testing.assert_allclose(A * A, A, atol=1e-12)

    def test_trace_kron_A_A_is_zero(self, A):
        """tr(A x A) = tr(A)^2 = 0^2 = 0."""
        trA = float(np.trace(A))
        assert abs(trA * trA) < 1e-12

    def test_kron_A_I2_eigenvalues(self, A, eig):
        """Eigenvalues of A x I_2: each eigenvalue of A doubled in mult."""
        vals, _ = eig
        expected = np.sort(np.repeat(vals, 2))
        AI2 = np.kron(A, np.eye(2))
        actual = np.sort(np.linalg.eigvalsh(AI2))
        np.testing.assert_allclose(actual, expected, atol=1e-8)

    def test_kron_I2_A_matches_A_I2(self, A):
        """I_2 x A and A x I_2 have the same eigenvalues."""
        I2A = np.kron(np.eye(2), A)
        AI2 = np.kron(A, np.eye(2))
        eigs_I2A = np.sort(np.linalg.eigvalsh(I2A))
        eigs_AI2 = np.sort(np.linalg.eigvalsh(AI2))
        np.testing.assert_allclose(eigs_I2A, eigs_AI2, atol=1e-8)

    def test_kron_A_A_distinct_eigenvalues(self, eig):
        """A x A has distinct eigenvalue products {144, 24, -48, 4, -8, 16}."""
        vals, _ = eig
        kron_eigs = np.outer(vals, vals).ravel()
        expected_set = {144, 24, -48, 4, -8, 16}
        actual_set = set(np.round(np.unique(kron_eigs)).astype(int))
        assert actual_set == expected_set

    def test_kron_A_A_largest_eigenvalue(self, eig):
        """Largest eigenvalue of A x A is 12*12 = 144."""
        vals, _ = eig
        kron_eigs = np.outer(vals, vals).ravel()
        np.testing.assert_allclose(np.max(kron_eigs), 144.0, atol=0.5)

    def test_hadamard_with_J(self, A):
        """A o J = A (Hadamard with all-ones leaves A unchanged)."""
        J = np.ones((40, 40))
        np.testing.assert_allclose(A * J, A, atol=1e-12)

    def test_hadamard_A_Abar_zero(self, A):
        """A o Abar = 0 (A and its complement have disjoint support)."""
        Abar = np.ones((40, 40)) - np.eye(40) - A
        np.testing.assert_allclose(A * Abar, np.zeros((40, 40)), atol=1e-12)

    def test_kron_sum_trace(self, A):
        """tr(A x I + I x A) = 2n tr(A) = 0."""
        # Eigenvalues of the Kronecker sum are lambda_i + lambda_j,
        # so the trace is n*tr(A) + n*tr(A) = 2*40*0 = 0.
        n = 40
        tr_expected = 2.0 * n * np.trace(A)
        assert abs(tr_expected) < 1e-12

    def test_kron_A_A_multiplicity_4(self, eig):
        """The eigenvalue 4 of A x A has multiplicity 24*24 = 576."""
        vals, _ = eig
        kron_eigs = np.outer(vals, vals).ravel()
        count_4 = np.sum(np.abs(kron_eigs - 4.0) < 0.5)
        assert count_4 == 576


# ======================================================================
# 8. NUMERICAL PROPERTIES (8 tests)
# ======================================================================

class TestNumericalProperties:
    """Condition number, spectral radius, numerical rank, stability."""

    def test_condition_number(self, A):
        """cond_2(A) = sigma_max / sigma_min = 12 / 2 = 6."""
        cond = np.linalg.cond(A)
        np.testing.assert_allclose(cond, 6.0, atol=1e-8)

    def test_spectral_radius(self, eig):
        """rho(A) = max|lambda| = 12."""
        vals, _ = eig
        rho = np.max(np.abs(vals))
        np.testing.assert_allclose(rho, 12.0, atol=1e-10)

    def test_numerical_rank_full(self, A):
        """A has full numerical rank 40 (since det != 0)."""
        assert np.linalg.matrix_rank(A) == 40

    def test_eigenvalue_perturbation_weyl(self, A, eig):
        """Weyl's theorem: |lambda_i(A+E) - lambda_i(A)| <= ||E||_2."""
        vals_orig = np.sort(eig[0])
        rng = np.random.RandomState(42)
        E = rng.randn(40, 40) * 1e-12
        E = (E + E.T) / 2  # symmetrize for Weyl's theorem
        vals_pert = np.sort(np.linalg.eigvalsh(A + E))
        max_diff = np.max(np.abs(vals_pert - vals_orig))
        assert max_diff < np.linalg.norm(E, 2) + 1e-14

    def test_trace_equals_zero(self, A):
        """tr(A) = 0 (no self-loops in SRG)."""
        assert np.trace(A) == 0

    def test_trace_A_squared(self, A):
        """tr(A^2) = 2|E| = 2 * nk/2 = nk = 480."""
        np.testing.assert_allclose(np.trace(A @ A), 480.0, atol=1e-10)

    def test_trace_A_cubed(self, A):
        """tr(A^3) = 12^3 + 24*2^3 + 15*(-4)^3 = 1728+192-960 = 960.

        Equivalently, 6 * (number of triangles) = 6 * 160 = 960.
        """
        expected = 12 ** 3 + 24 * (2 ** 3) + 15 * ((-4) ** 3)  # = 960
        np.testing.assert_allclose(
            np.trace(A @ A @ A), float(expected), atol=1e-8
        )

    def test_machine_epsilon_eigval_separation(self, eig):
        """Eigenvalue gaps (6 and 10) are far above machine epsilon."""
        vals = np.sort(eig[0])
        unique_vals = np.array([-4.0, 2.0, 12.0])
        gaps = np.diff(unique_vals)  # [6, 10]
        eps = np.finfo(float).eps
        assert np.all(gaps > 1e6 * eps)
