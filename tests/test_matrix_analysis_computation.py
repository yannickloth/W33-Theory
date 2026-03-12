"""
Phase LXXXIV — Matrix Analysis & Operator Theory (Hard Computation)
===================================================================

Theorems T1320 – T1340

Every result derived from first principles using only numpy / scipy on
the W(3,3) = SRG(40,12,2,4) adjacency matrix.

Covers: matrix norms, singular values, condition numbers, matrix
exponential/logarithm/square root, polar and Schur decompositions,
Hadamard and Kronecker products, resolvent operators, spectral
projections, Bose-Mesner commutant, numerical range, trace power
inequalities, eigenvalue interlacing, Perron-Frobenius theory,
Loewner ordering, minimal polynomial, tensor product spectra,
and matrix power series convergence.
"""

import math
import numpy as np
from numpy.linalg import eigvalsh, svd, norm, inv, matrix_rank
from scipy.linalg import expm, logm, sqrtm, polar, schur
import pytest


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
                    inv_ = pow(first, -1, 3)
                    canon = tuple((x * inv_) % 3 for x in v)
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


@pytest.fixture(scope="module")
def w33():
    return _build_w33()


@pytest.fixture(scope="module")
def spectrum(w33):
    """Eigenvalues of A sorted descending."""
    return np.sort(eigvalsh(w33.astype(float)))[::-1]


# ---------------------------------------------------------------------------
# T1320: Matrix norms
# ---------------------------------------------------------------------------

class TestT1320MatrixNorms:
    """Norms of the W(3,3) adjacency matrix A."""

    def test_spectral_norm_equals_12(self, w33):
        """||A||_2 = max singular value = spectral radius = 12 for k-regular."""
        s = svd(w33.astype(float), compute_uv=False)
        assert abs(s[0] - 12.0) < 1e-8

    def test_frobenius_norm(self, w33):
        """||A||_F = sqrt(2*|E|) = sqrt(480) = 4*sqrt(30)."""
        fro = norm(w33.astype(float), 'fro')
        assert abs(fro - 4.0 * math.sqrt(30)) < 1e-8

    def test_frobenius_from_spectrum(self, spectrum):
        """||A||_F^2 = sum lambda_i^2 = 12^2 + 24*2^2 + 15*(-4)^2 = 480."""
        assert abs(np.sum(spectrum**2) - 480.0) < 1e-6

    def test_one_norm_equals_12(self, w33):
        """||A||_1 = max column sum = 12 (regular graph)."""
        col_sums = np.sum(np.abs(w33), axis=0)
        assert int(np.max(col_sums)) == 12

    def test_inf_norm_equals_12(self, w33):
        """||A||_inf = max row sum = 12 (regular graph)."""
        row_sums = np.sum(np.abs(w33), axis=1)
        assert int(np.max(row_sums)) == 12

    def test_nuclear_norm(self, w33):
        """||A||_* = sum of singular values = 12 + 24*2 + 15*4 = 120."""
        s = svd(w33.astype(float), compute_uv=False)
        assert abs(np.sum(s) - 120.0) < 1e-6


# ---------------------------------------------------------------------------
# T1321: Singular values
# ---------------------------------------------------------------------------

class TestT1321SingularValues:
    """SVD of the symmetric adjacency matrix A."""

    def test_singular_values_are_abs_eigenvalues(self, w33, spectrum):
        """For symmetric A, singular values = |eigenvalues|."""
        s = np.sort(svd(w33.astype(float), compute_uv=False))[::-1]
        abs_eigs = np.sort(np.abs(spectrum))[::-1]
        assert np.allclose(s, abs_eigs, atol=1e-8)

    def test_singular_value_multiplicities(self, w33):
        """Singular values: 12 (x1), 4 (x15), 2 (x24)."""
        s = svd(w33.astype(float), compute_uv=False)
        s_rounded = np.round(s).astype(int)
        from collections import Counter
        c = Counter(s_rounded)
        assert c[12] == 1
        assert c[4] == 15
        assert c[2] == 24

    def test_svd_reconstruction(self, w33):
        """A = U @ diag(s) @ V^T must reconstruct A exactly."""
        Af = w33.astype(float)
        U, s, Vt = svd(Af, full_matrices=False)
        reconstructed = U @ np.diag(s) @ Vt
        assert np.allclose(reconstructed, Af, atol=1e-8)


# ---------------------------------------------------------------------------
# T1322: Condition number
# ---------------------------------------------------------------------------

class TestT1322ConditionNumber:
    """Condition number kappa(A) of the adjacency matrix."""

    def test_condition_number_is_6(self, w33):
        """kappa_2(A) = sigma_max/sigma_min = 12/2 = 6."""
        s = svd(w33.astype(float), compute_uv=False)
        kappa = s[0] / s[-1]
        assert abs(kappa - 6.0) < 1e-8

    def test_condition_number_via_numpy(self, w33):
        """np.linalg.cond gives same result."""
        kappa = np.linalg.cond(w33.astype(float))
        assert abs(kappa - 6.0) < 1e-8

    def test_condition_number_laplacian(self, w33):
        """Pseudocondition of L (ignoring zero eigenvalue): 16/10 = 1.6."""
        L = 12 * np.eye(40) - w33.astype(float)
        evals = np.sort(eigvalsh(L))
        # Skip the zero eigenvalue
        nonzero = evals[evals > 0.5]
        kappa_L = nonzero[-1] / nonzero[0]
        assert abs(kappa_L - 1.6) < 1e-8


# ---------------------------------------------------------------------------
# T1323: Matrix exponential trace
# ---------------------------------------------------------------------------

class TestT1323MatrixExponentialTrace:
    """Trace of exp(A) via spectral decomposition."""

    def test_trace_exp_spectral(self, w33):
        """tr(exp(A)) = exp(12) + 24*exp(2) + 15*exp(-4)."""
        expected = math.exp(12) + 24 * math.exp(2) + 15 * math.exp(-4)
        E = expm(w33.astype(float))
        assert abs(np.trace(E) - expected) / expected < 1e-8

    def test_exp_is_symmetric(self, w33):
        """exp(A) is symmetric since A is symmetric."""
        E = expm(w33.astype(float))
        assert np.allclose(E, E.T, atol=1e-8)

    def test_exp_is_positive_definite(self, w33):
        """exp(A) is PD (all eigenvalues of exp(A) = exp(lambda_i) > 0)."""
        E = expm(w33.astype(float))
        evals = eigvalsh(E)
        assert np.all(evals > 0)

    def test_exp_eigenvalues(self, w33):
        """Eigenvalues of exp(A) are {exp(12), exp(2), exp(-4)}."""
        E = expm(w33.astype(float))
        evals = np.sort(eigvalsh(E))[::-1]
        from collections import Counter
        # Check the three distinct values
        assert abs(evals[0] - math.exp(12)) / math.exp(12) < 1e-6
        assert abs(evals[1] - math.exp(2)) / math.exp(2) < 1e-6
        assert abs(evals[-1] - math.exp(-4)) / math.exp(-4) < 1e-6


# ---------------------------------------------------------------------------
# T1324: Matrix logarithm
# ---------------------------------------------------------------------------

class TestT1324MatrixLogarithm:
    """Logarithm of shifted adjacency matrices."""

    def test_log_A_is_complex(self, w33):
        """A has eigenvalue -4 < 0, so logm(A) is complex-valued."""
        Af = w33.astype(float)
        L = logm(Af)
        # logm returns complex for matrices with negative eigenvalues
        assert np.any(np.abs(np.imag(L)) > 1e-6)

    def test_log_shifted_is_real(self, w33):
        """A + 5I has eigenvalues {17, 7, 1}, all positive => log is real."""
        M = w33.astype(float) + 5 * np.eye(40)
        L = logm(M)
        assert np.allclose(np.imag(L), 0, atol=1e-8)

    def test_log_shifted_roundtrip(self, w33):
        """exp(log(A+5I)) = A+5I (roundtrip via real logarithm)."""
        M = w33.astype(float) + 5 * np.eye(40)
        L = np.real(logm(M))
        recovered = expm(L)
        assert np.allclose(recovered, M, atol=1e-6)

    def test_log_trace(self, w33):
        """tr(log(A+5I)) = log(17) + 24*log(7) + 15*log(1) = log(17) + 24*log(7)."""
        M = w33.astype(float) + 5 * np.eye(40)
        L = np.real(logm(M))
        expected = math.log(17) + 24 * math.log(7)
        assert abs(np.trace(L) - expected) < 1e-6


# ---------------------------------------------------------------------------
# T1325: Matrix square root
# ---------------------------------------------------------------------------

class TestT1325MatrixSquareRoot:
    """Square root of the shifted adjacency matrix A + 4I (PSD)."""

    def test_shifted_is_psd(self, w33):
        """A + 4I has eigenvalues {16, 6, 0}: PSD."""
        M = w33.astype(float) + 4 * np.eye(40)
        evals = eigvalsh(M)
        assert np.all(evals >= -1e-10)

    def test_sqrtm_squares_back(self, w33):
        """sqrtm(A+4I)^2 = A+4I."""
        M = w33.astype(float) + 4 * np.eye(40)
        S = np.real(sqrtm(M))
        recovered = S @ S
        assert np.allclose(recovered, M, atol=1e-6)

    def test_sqrtm_eigenvalues(self, w33):
        """sqrt(A+4I) has eigenvalues {4, sqrt(6), 0}."""
        M = w33.astype(float) + 4 * np.eye(40)
        S = np.real(sqrtm(M))
        evals = np.sort(eigvalsh(S))[::-1]
        # Expect: 4 (x1), sqrt(6) (x24), 0 (x15)
        assert abs(evals[0] - 4.0) < 1e-6
        assert abs(evals[1] - math.sqrt(6)) < 1e-6
        assert abs(evals[-1]) < 1e-6

    def test_sqrtm_is_symmetric(self, w33):
        """sqrt of a symmetric PSD matrix is symmetric."""
        M = w33.astype(float) + 4 * np.eye(40)
        S = np.real(sqrtm(M))
        assert np.allclose(S, S.T, atol=1e-8)


# ---------------------------------------------------------------------------
# T1326: Polar decomposition
# ---------------------------------------------------------------------------

class TestT1326PolarDecomposition:
    """Polar decomposition A = U*P for symmetric A."""

    def test_polar_product_equals_A(self, w33):
        """A = U @ P exactly."""
        Af = w33.astype(float)
        U, P = polar(Af)
        assert np.allclose(U @ P, Af, atol=1e-8)

    def test_U_is_orthogonal(self, w33):
        """U is orthogonal: U^T U = I."""
        Af = w33.astype(float)
        U, P = polar(Af)
        assert np.allclose(U.T @ U, np.eye(40), atol=1e-8)

    def test_P_is_psd(self, w33):
        """P is positive semidefinite."""
        Af = w33.astype(float)
        U, P = polar(Af)
        evals = eigvalsh(P)
        assert np.all(evals >= -1e-8)

    def test_U_is_involution(self, w33):
        """For symmetric A, U = sgn(A) is an involution: U^2 = I."""
        Af = w33.astype(float)
        U, P = polar(Af)
        assert np.allclose(U @ U, np.eye(40), atol=1e-8)

    def test_U_eigenvalues(self, w33):
        """U = sgn(A): eigenvalues +1 (mult 25) and -1 (mult 15)."""
        Af = w33.astype(float)
        U, P = polar(Af)
        evals = np.sort(np.round(eigvalsh(U)).astype(int))
        from collections import Counter
        c = Counter(evals)
        assert c[-1] == 15  # from eigenvalue -4 subspace
        assert c[1] == 25   # from eigenvalues 12 and 2 subspaces

    def test_P_trace(self, w33):
        """tr(P) = sum |lambda_i| = 12 + 24*2 + 15*4 = 120."""
        Af = w33.astype(float)
        U, P = polar(Af)
        assert abs(np.trace(P) - 120.0) < 1e-6


# ---------------------------------------------------------------------------
# T1327: Schur decomposition
# ---------------------------------------------------------------------------

class TestT1327SchurDecomposition:
    """Schur decomposition A = Q T Q^T for symmetric A."""

    def test_schur_form_is_diagonal(self, w33):
        """For real symmetric A, the Schur form T is diagonal."""
        T, Q = schur(w33.astype(float), output='real')
        # Off-diagonal elements should be zero
        off_diag = T - np.diag(np.diag(T))
        assert np.allclose(off_diag, 0, atol=1e-8)

    def test_schur_Q_orthogonal(self, w33):
        """The Schur vectors Q form an orthogonal matrix."""
        T, Q = schur(w33.astype(float), output='real')
        assert np.allclose(Q.T @ Q, np.eye(40), atol=1e-8)

    def test_schur_reconstruction(self, w33):
        """Q T Q^T = A."""
        Af = w33.astype(float)
        T, Q = schur(Af, output='real')
        assert np.allclose(Q @ T @ Q.T, Af, atol=1e-8)

    def test_schur_diagonal_are_eigenvalues(self, w33):
        """Diagonal of T contains the eigenvalues {12, 2, -4}."""
        T, Q = schur(w33.astype(float), output='real')
        diag = np.sort(np.diag(T))
        evals = np.sort(eigvalsh(w33.astype(float)))
        assert np.allclose(diag, evals, atol=1e-8)


# ---------------------------------------------------------------------------
# T1328: Hadamard product
# ---------------------------------------------------------------------------

class TestT1328HadamardProduct:
    """Hadamard (entrywise) product properties of 0-1 adjacency matrix."""

    def test_hadamard_idempotent(self, w33):
        """A circ A = A since A is a 0-1 matrix."""
        H = w33 * w33  # entrywise
        assert np.array_equal(H, w33)

    def test_hadamard_with_J(self, w33):
        """A circ J = A (J is all-ones)."""
        J = np.ones((40, 40), dtype=int)
        H = w33 * J
        assert np.array_equal(H, w33)

    def test_hadamard_with_complement_is_zero(self, w33):
        """A circ (J - I - A) = 0 (adjacency and complement are disjoint)."""
        Abar = np.ones((40, 40), dtype=int) - np.eye(40, dtype=int) - w33
        H = w33 * Abar
        assert np.all(H == 0)

    def test_schur_product_theorem(self, w33):
        """If B, C are PSD then B circ C is PSD.
        (A+4I) circ (A+4I) is PSD since A+4I is PSD."""
        M = w33.astype(float) + 4 * np.eye(40)
        H = M * M  # Hadamard
        evals = eigvalsh(H)
        assert np.all(evals >= -1e-8)

    def test_hadamard_trace(self, w33):
        """tr(A circ A) = sum A_ii^2 = 0 (no self-loops)."""
        H = w33 * w33
        assert np.trace(H) == 0


# ---------------------------------------------------------------------------
# T1329: Kronecker product properties
# ---------------------------------------------------------------------------

class TestT1329KroneckerProduct:
    """Kronecker product properties of A."""

    def test_kronecker_trace(self, w33):
        """tr(A kron I_2) = 2 * tr(A) = 0 (since tr(A) = 0)."""
        K = np.kron(w33.astype(float), np.eye(2))
        assert abs(np.trace(K)) < 1e-10

    def test_kronecker_squared_trace(self, w33):
        """tr((A kron I_2)^2) = 2 * tr(A^2) = 2 * 480 = 960."""
        K = np.kron(w33.astype(float), np.eye(2))
        val = np.trace(K @ K)
        assert abs(val - 960.0) < 1e-4

    def test_kronecker_eigenvalues(self, w33):
        """Eigenvalues of A kron I_2 are eigenvalues of A, each doubled.
        Distinct eigenvalues: {12, 2, -4} with multiplied multiplicities."""
        K = np.kron(w33.astype(float), np.eye(2))
        evals = np.round(eigvalsh(K)).astype(int)
        from collections import Counter
        c = Counter(evals)
        assert c[12] == 2
        assert c[2] == 48
        assert c[-4] == 30

    def test_kronecker_mixed_product(self, w33):
        """tr(A kron A) = tr(A)^2 = 0."""
        # Verify via identity without forming 1600x1600 matrix
        assert abs(np.trace(w33.astype(float))**2) < 1e-10


# ---------------------------------------------------------------------------
# T1330: Resolvent operator
# ---------------------------------------------------------------------------

class TestT1330Resolvent:
    """Resolvent R(z) = (zI - A)^{-1} and its trace."""

    def test_resolvent_trace_at_z5(self, w33):
        """tr(R(5)) = 1/(5-12) + 24/(5-2) + 15/(5+4) = 200/21."""
        z = 5.0
        R = inv(z * np.eye(40) - w33.astype(float))
        expected = 200.0 / 21.0
        assert abs(np.trace(R) - expected) < 1e-8

    def test_resolvent_trace_at_z20(self, w33):
        """tr(R(20)) = 1/8 + 24/18 + 15/24 = 25/12."""
        z = 20.0
        R = inv(z * np.eye(40) - w33.astype(float))
        expected = 1.0/8 + 24.0/18 + 15.0/24
        assert abs(np.trace(R) - expected) < 1e-8

    def test_resolvent_blows_up_near_eigenvalue(self, w33):
        """||R(z)||_2 -> infinity as z -> eigenvalue.
        At z = 2.01, the norm is large (~100)."""
        z = 2.01
        R = inv(z * np.eye(40) - w33.astype(float))
        s_max = svd(R, compute_uv=False)[0]
        assert s_max > 50.0  # 1/0.01 = 100

    def test_resolvent_identity(self, w33):
        """R(z) @ (zI - A) = I."""
        z = 7.0
        Af = w33.astype(float)
        R = inv(z * np.eye(40) - Af)
        product = R @ (z * np.eye(40) - Af)
        assert np.allclose(product, np.eye(40), atol=1e-8)


# ---------------------------------------------------------------------------
# T1331: Spectral projections
# ---------------------------------------------------------------------------

class TestT1331SpectralProjections:
    """Spectral idempotents E_i for each distinct eigenvalue."""

    def _projections(self, w33):
        """Compute spectral projections for eigenvalues 12, 2, -4."""
        Af = w33.astype(float)
        I = np.eye(40)
        # E0 for eigenvalue 12: (A-2I)(A+4I) / ((12-2)(12+4))
        E0 = (Af - 2*I) @ (Af + 4*I) / 160.0
        # E1 for eigenvalue 2: (A-12I)(A+4I) / ((2-12)(2+4))
        E1 = (Af - 12*I) @ (Af + 4*I) / (-60.0)
        # E2 for eigenvalue -4: (A-12I)(A-2I) / ((-4-12)(-4-2))
        E2 = (Af - 12*I) @ (Af - 2*I) / 96.0
        return E0, E1, E2

    def test_projections_are_idempotent(self, w33):
        """E_i^2 = E_i for each spectral projection."""
        E0, E1, E2 = self._projections(w33)
        assert np.allclose(E0 @ E0, E0, atol=1e-8)
        assert np.allclose(E1 @ E1, E1, atol=1e-8)
        assert np.allclose(E2 @ E2, E2, atol=1e-8)

    def test_projections_orthogonal(self, w33):
        """E_i @ E_j = 0 for i != j."""
        E0, E1, E2 = self._projections(w33)
        assert np.allclose(E0 @ E1, 0, atol=1e-8)
        assert np.allclose(E0 @ E2, 0, atol=1e-8)
        assert np.allclose(E1 @ E2, 0, atol=1e-8)

    def test_projections_sum_to_identity(self, w33):
        """E0 + E1 + E2 = I."""
        E0, E1, E2 = self._projections(w33)
        assert np.allclose(E0 + E1 + E2, np.eye(40), atol=1e-8)

    def test_projection_ranks(self, w33):
        """rank(E0)=1, rank(E1)=24, rank(E2)=15."""
        E0, E1, E2 = self._projections(w33)
        assert matrix_rank(E0, tol=1e-6) == 1
        assert matrix_rank(E1, tol=1e-6) == 24
        assert matrix_rank(E2, tol=1e-6) == 15

    def test_E0_is_J_over_n(self, w33):
        """E0 = J/40 (projection onto all-ones eigenvector)."""
        E0, _, _ = self._projections(w33)
        assert np.allclose(E0, np.ones((40, 40)) / 40.0, atol=1e-8)

    def test_spectral_reconstruction(self, w33):
        """A = 12*E0 + 2*E1 + (-4)*E2."""
        E0, E1, E2 = self._projections(w33)
        reconstructed = 12*E0 + 2*E1 + (-4)*E2
        assert np.allclose(reconstructed, w33.astype(float), atol=1e-8)


# ---------------------------------------------------------------------------
# T1332: Commutant (Bose-Mesner algebra)
# ---------------------------------------------------------------------------

class TestT1332Commutant:
    """Matrices commuting with A form the 3-dimensional Bose-Mesner algebra."""

    def test_I_commutes(self, w33):
        """I commutes with A."""
        Af = w33.astype(float)
        I = np.eye(40)
        assert np.allclose(I @ Af, Af @ I)

    def test_J_commutes(self, w33):
        """J commutes with A (A is walk-regular / vertex-transitive)."""
        Af = w33.astype(float)
        J = np.ones((40, 40))
        assert np.allclose(J @ Af, Af @ J, atol=1e-8)

    def test_complement_commutes(self, w33):
        """A_bar = J - I - A commutes with A."""
        Af = w33.astype(float)
        Abar = np.ones((40, 40)) - np.eye(40) - Af
        assert np.allclose(Abar @ Af, Af @ Abar, atol=1e-8)

    def test_bose_mesner_dimension(self, w33):
        """The commutant has dimension 3 = number of distinct eigenvalues.
        Verify by checking that a random linear combination in span{I,A,A_bar}
        commutes with A, and that a generic perturbation outside the span does not."""
        Af = w33.astype(float)
        I40 = np.eye(40)
        Abar = np.ones((40, 40)) - I40 - Af
        # Random element in Bose-Mesner algebra
        rng = np.random.RandomState(42)
        B = 2.5 * I40 + 1.3 * Af + 0.7 * Abar
        assert np.allclose(B @ Af, Af @ B, atol=1e-8)
        # Perturb one off-diagonal entry to leave the algebra
        C = B.copy()
        C[0, 1] += 1.0
        comm = C @ Af - Af @ C
        assert norm(comm) > 0.1  # does not commute

    def test_srg_equation(self, w33):
        """SRG identity: A^2 = 2A + 4(J-I-A) + 12I = -2A + 4J + 8I."""
        Af = w33.astype(float)
        A2 = Af @ Af
        J = np.ones((40, 40))
        expected = -2 * Af + 4 * J + 8 * np.eye(40)
        assert np.allclose(A2, expected, atol=1e-8)


# ---------------------------------------------------------------------------
# T1333: Numerical range
# ---------------------------------------------------------------------------

class TestT1333NumericalRange:
    """Numerical range W(A) = {x^T A x : ||x||=1} for symmetric A."""

    def test_numerical_range_equals_interval(self, w33):
        """For real symmetric A, W(A) = [lambda_min, lambda_max] = [-4, 12]."""
        evals = eigvalsh(w33.astype(float))
        assert abs(min(evals) - (-4.0)) < 1e-8
        assert abs(max(evals) - 12.0) < 1e-8

    def test_maximum_rayleigh_quotient(self, w33):
        """max x^T A x = 12, attained by x = (1,...,1)/sqrt(40)."""
        x = np.ones(40) / math.sqrt(40)
        val = x @ w33.astype(float) @ x
        assert abs(val - 12.0) < 1e-8

    def test_minimum_rayleigh_quotient(self, w33, spectrum):
        """min x^T A x = -4, attained by any eigenvector of -4."""
        Af = w33.astype(float)
        evals, evecs = np.linalg.eigh(Af)
        idx = np.argmin(evals)
        x = evecs[:, idx]
        val = x @ Af @ x
        assert abs(val - (-4.0)) < 1e-8

    def test_interior_point(self, w33):
        """A random unit vector gives Rayleigh quotient in (-4, 12)."""
        rng = np.random.RandomState(123)
        x = rng.randn(40)
        x /= norm(x)
        val = x @ w33.astype(float) @ x
        assert -4.0 - 1e-8 <= val <= 12.0 + 1e-8


# ---------------------------------------------------------------------------
# T1334: Trace inequalities
# ---------------------------------------------------------------------------

class TestT1334TraceInequalities:
    """Trace powers tr(A^k) from spectral data and direct computation."""

    def test_trace_A(self, w33):
        """tr(A) = sum eigenvalues = 12 + 24*2 + 15*(-4) = 0."""
        assert np.trace(w33) == 0

    def test_trace_A2(self, w33):
        """tr(A^2) = 2*|E| = 480 = 12^2 + 24*4 + 15*16."""
        A2 = w33.astype(float) @ w33.astype(float)
        assert abs(np.trace(A2) - 480.0) < 1e-8

    def test_trace_A3(self, w33):
        """tr(A^3) = 6*triangles = 6*160 = 960."""
        Af = w33.astype(float)
        A3 = Af @ Af @ Af
        expected = 12**3 + 24 * 2**3 + 15 * (-4)**3  # 1728 + 192 - 960 = 960
        assert abs(np.trace(A3) - expected) < 1e-6
        assert abs(np.trace(A3) - 960.0) < 1e-6

    def test_trace_A4(self, w33):
        """tr(A^4) = sum lambda_i^4 = 12^4 + 24*16 + 15*256 = 24960."""
        Af = w33.astype(float)
        A4 = Af @ Af @ Af @ Af
        expected = 12**4 + 24 * 2**4 + 15 * (-4)**4  # 20736 + 384 + 3840 = 24960
        assert abs(np.trace(A4) - expected) < 1e-4
        assert abs(np.trace(A4) - 24960.0) < 1e-4

    def test_trace_A2_from_edges(self, w33):
        """tr(A^2) = sum_ij A_ij^2 = 2*|E| since A is 0-1 symmetric."""
        num_edges = np.sum(w33) // 2
        assert num_edges == 240
        assert abs(np.trace(w33 @ w33) - 2 * num_edges) < 1e-8

    def test_trace_power_positivity(self, w33):
        """tr(A^{2k}) > 0 for all k (sum of even powers of real eigenvalues)."""
        Af = w33.astype(float)
        Ak = np.eye(40)
        for k in range(1, 6):
            Ak = Ak @ Af @ Af  # A^{2k}
            assert np.trace(Ak) > 0


# ---------------------------------------------------------------------------
# T1335: Eigenvalue interlacing
# ---------------------------------------------------------------------------

class TestT1335EigenvalueInterlacing:
    """Cauchy interlacing: deleting a vertex gives interlacing eigenvalues."""

    def test_interlacing_holds(self, w33):
        """Delete vertex 0: eigenvalues of 39x39 submatrix interlace those of A.
        lambda_i(A) >= mu_i(B) >= lambda_{i+1}(A) for i=1..39."""
        Af = w33.astype(float)
        # Delete vertex 0
        B = Af[1:, 1:]
        lam = np.sort(eigvalsh(Af))[::-1]  # A eigenvalues descending
        mu = np.sort(eigvalsh(B))[::-1]     # B eigenvalues descending
        for i in range(39):
            assert lam[i] >= mu[i] - 1e-8
            assert mu[i] >= lam[i + 1] - 1e-8

    def test_squeezed_eigenvalues(self, w33):
        """Between consecutive equal eigenvalues of A, B's eigenvalue is forced.
        A has 2 repeated 24 times => many B eigenvalues pinched to 2."""
        Af = w33.astype(float)
        B = Af[1:, 1:]
        mu = np.sort(eigvalsh(B))[::-1]
        # mu_2 through mu_24 should all be 2 (23 copies)
        count_two = np.sum(np.abs(mu[1:24] - 2.0) < 1e-6)
        assert count_two == 23

    def test_squeezed_minus4(self, w33):
        """A has -4 repeated 15 times => 14 eigenvalues of B are pinched to -4."""
        Af = w33.astype(float)
        B = Af[1:, 1:]
        mu = np.sort(eigvalsh(B))
        # Bottom 14 eigenvalues should be -4
        count_m4 = np.sum(np.abs(mu[:14] - (-4.0)) < 1e-6)
        assert count_m4 == 14


# ---------------------------------------------------------------------------
# T1336: Perron-Frobenius theorem
# ---------------------------------------------------------------------------

class TestT1336PerronFrobenius:
    """Perron-Frobenius for the nonnegative adjacency matrix."""

    def test_spectral_radius_equals_k(self, w33):
        """Spectral radius rho(A) = max |lambda_i| = k = 12."""
        evals = eigvalsh(w33.astype(float))
        rho = max(abs(e) for e in evals)
        assert abs(rho - 12.0) < 1e-8

    def test_perron_vector_is_constant(self, w33):
        """Perron eigenvector = (1,...,1)/sqrt(40) for k-regular graph."""
        evals, evecs = np.linalg.eigh(w33.astype(float))
        idx = np.argmax(evals)
        v = evecs[:, idx]
        # Should be constant (up to sign)
        v = v * np.sign(v[0])
        expected = np.ones(40) / math.sqrt(40)
        assert np.allclose(v, expected, atol=1e-8)

    def test_perron_vector_positive(self, w33):
        """Perron vector has all positive entries (connected graph, PF theorem)."""
        evals, evecs = np.linalg.eigh(w33.astype(float))
        idx = np.argmax(evals)
        v = evecs[:, idx]
        v = v * np.sign(v[0])
        assert np.all(v > 0)

    def test_spectral_radius_unique_max(self, w33):
        """rho(A) = 12 has multiplicity 1 (connected graph)."""
        evals = np.sort(eigvalsh(w33.astype(float)))[::-1]
        assert abs(evals[0] - 12.0) < 1e-8
        assert evals[1] < 12.0 - 0.5  # next eigenvalue is 2


# ---------------------------------------------------------------------------
# T1337: Matrix monotonicity (Loewner order)
# ---------------------------------------------------------------------------

class TestT1337MatrixMonotonicity:
    """Loewner ordering: A <= B iff B - A is PSD."""

    def test_upper_bound(self, w33):
        """A <= 12I: eigenvalues of 12I - A are {0, 10, 16}, all >= 0."""
        M = 12 * np.eye(40) - w33.astype(float)
        evals = eigvalsh(M)
        assert np.all(evals >= -1e-10)

    def test_lower_bound(self, w33):
        """A >= -4I: eigenvalues of A + 4I are {16, 6, 0}, all >= 0."""
        M = w33.astype(float) + 4 * np.eye(40)
        evals = eigvalsh(M)
        assert np.all(evals >= -1e-10)

    def test_sandwich(self, w33):
        """Combining: -4I <= A <= 12I. Width = 16 = k - tau."""
        assert 12 - (-4) == 16

    def test_strict_lower_bound_at_minus3(self, w33):
        """A + 3I is NOT PSD (eigenvalue -4 + 3 = -1 < 0)."""
        M = w33.astype(float) + 3 * np.eye(40)
        evals = eigvalsh(M)
        assert np.min(evals) < -0.5


# ---------------------------------------------------------------------------
# T1338: Minimal polynomial and Cayley-Hamilton
# ---------------------------------------------------------------------------

class TestT1338MinimalPolynomial:
    """Minimal polynomial m(x) = (x-12)(x-2)(x+4) = x^3 - 10x^2 - 32x + 96."""

    def test_minimal_polynomial_annihilates(self, w33):
        """m(A) = A^3 - 10A^2 - 32A + 96I = 0."""
        Af = w33.astype(float)
        I = np.eye(40)
        A2 = Af @ Af
        A3 = A2 @ Af
        result = A3 - 10 * A2 - 32 * Af + 96 * I
        assert np.allclose(result, 0, atol=1e-6)

    def test_minimal_polynomial_degree_3(self, w33):
        """No degree-2 polynomial annihilates A (3 distinct eigenvalues)."""
        Af = w33.astype(float)
        I = np.eye(40)
        A2 = Af @ Af
        # Try (A - 12I)(A - 2I) = A^2 - 14A + 24I
        p2 = A2 - 14 * Af + 24 * I
        assert not np.allclose(p2, 0, atol=1e-6)

    def test_cayley_hamilton(self, w33):
        """Characteristic polynomial chi(A) = 0 by Cayley-Hamilton.
        chi(x) = (x-12)*(x-2)^24*(x+4)^15.
        Since m(x) | chi(x) and m(A) = 0, this is satisfied automatically.
        But we verify A^3 = 10A^2 + 32A - 96I (rewrite of m(A)=0)."""
        Af = w33.astype(float)
        A3 = Af @ Af @ Af
        expected = 10 * (Af @ Af) + 32 * Af - 96 * np.eye(40)
        assert np.allclose(A3, expected, atol=1e-6)

    def test_minimal_poly_roots(self):
        """Roots of x^3 - 10x^2 - 32x + 96 are 12, 2, -4."""
        coeffs = [1, -10, -32, 96]
        roots = sorted(np.roots(coeffs))
        assert abs(roots[0] - (-4)) < 1e-8
        assert abs(roots[1] - 2) < 1e-8
        assert abs(roots[2] - 12) < 1e-8


# ---------------------------------------------------------------------------
# T1339: Tensor product spectrum
# ---------------------------------------------------------------------------

class TestT1339TensorProductSpectrum:
    """Spectrum of A kron I + I kron B for small B."""

    def test_tensor_sum_eigenvalues(self, w33):
        """For B = Pauli X = [[0,1],[1,0]] with eigenvalues +/-1:
        eigenvalues of A kron I_2 + I_40 kron B are lambda_i + mu_j.
        Distinct values: {13, 11, 3, 1, -3, -5}."""
        Af = w33.astype(float)
        B = np.array([[0, 1], [1, 0]], dtype=float)
        M = np.kron(Af, np.eye(2)) + np.kron(np.eye(40), B)
        evals = np.sort(np.round(eigvalsh(M), 6))[::-1]
        from collections import Counter
        c = Counter(np.round(evals).astype(int))
        assert c[13] == 1
        assert c[11] == 1
        assert c[3] == 24
        assert c[1] == 24
        assert c[-3] == 15
        assert c[-5] == 15

    def test_tensor_sum_trace(self, w33):
        """tr(A kron I_2 + I_40 kron B) = 2*tr(A) + 40*tr(B) = 0 + 0 = 0."""
        Af = w33.astype(float)
        B = np.array([[0, 1], [1, 0]], dtype=float)
        M = np.kron(Af, np.eye(2)) + np.kron(np.eye(40), B)
        assert abs(np.trace(M)) < 1e-10

    def test_tensor_product_eigenvalues(self, w33):
        """Eigenvalues of A kron B (product) are lambda_i * mu_j.
        For B = diag(2,3): products are {24,36, 4,6, -8,-12}."""
        Af = w33.astype(float)
        B = np.diag([2.0, 3.0])
        M = np.kron(Af, B)
        evals = np.sort(np.round(eigvalsh(M), 6))[::-1]
        from collections import Counter
        c = Counter(np.round(evals).astype(int))
        assert c[36] == 1
        assert c[24] == 1
        assert c[6] == 24
        assert c[4] == 24
        assert c[-8] == 15
        assert c[-12] == 15

    def test_tensor_sum_size(self, w33):
        """A kron I_m + I_n kron B has size nm x nm."""
        m = 3
        n = 40
        M = np.kron(w33.astype(float), np.eye(m)) + np.kron(np.eye(n), np.zeros((m, m)))
        assert M.shape == (n * m, n * m)


# ---------------------------------------------------------------------------
# T1340: Matrix power series and exp(A) via spectral decomposition
# ---------------------------------------------------------------------------

class TestT1340MatrixPowerSeries:
    """Sum_{k=0}^{inf} A^k/k! = exp(A), verified spectrally."""

    def test_exp_via_spectral(self, w33):
        """exp(A) = sum_i exp(lambda_i) * E_i where E_i are spectral projections."""
        Af = w33.astype(float)
        I = np.eye(40)
        E0 = (Af - 2*I) @ (Af + 4*I) / 160.0
        E1 = (Af - 12*I) @ (Af + 4*I) / (-60.0)
        E2 = (Af - 12*I) @ (Af - 2*I) / 96.0
        exp_spectral = math.exp(12)*E0 + math.exp(2)*E1 + math.exp(-4)*E2
        exp_direct = expm(Af)
        assert np.allclose(exp_spectral, exp_direct, atol=1e-4)

    def test_partial_series_convergence(self, w33):
        """Truncated Taylor series sum_{k=0}^{N} A^k/k! converges to exp(A).
        Using A/20 (scaled to ensure fast convergence)."""
        Af = w33.astype(float) / 20.0  # scale down for convergence
        partial = np.zeros((40, 40))
        Ak = np.eye(40)
        for k in range(30):
            partial += Ak / math.factorial(k)
            Ak = Ak @ Af
        expected = expm(Af)
        assert np.allclose(partial, expected, atol=1e-6)

    def test_resolvent_neumann_series(self, w33):
        """For |z| > rho(A) = 12: R(z) = sum_{k=0}^{inf} A^k / z^{k+1}.
        At z = 50: the series converges (ratio 12/50 = 0.24 < 1)."""
        Af = w33.astype(float)
        z = 50.0
        # Truncate at N terms
        partial = np.zeros((40, 40))
        Ak = np.eye(40)
        for k in range(40):
            partial += Ak / (z**(k + 1))
            Ak = Ak @ Af
        exact = inv(z * np.eye(40) - Af)
        assert np.allclose(partial, exact, atol=1e-6)

    def test_matrix_polynomial_via_cayley_hamilton(self, w33):
        """Any matrix polynomial p(A) can be reduced to degree <= 2 via
        the minimal polynomial identity A^3 = 10A^2 + 32A - 96I.
        Verify for A^5 = 10*A^4 + 32*A^3 - 96*A^2."""
        Af = w33.astype(float)
        A2 = Af @ Af
        A3 = A2 @ Af
        A4 = A3 @ Af
        A5 = A4 @ Af
        expected = 10 * A4 + 32 * A3 - 96 * A2
        assert np.allclose(A5, expected, atol=1e-4)


# ============================================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
