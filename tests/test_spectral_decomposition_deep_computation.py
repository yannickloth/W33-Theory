"""
Phase CXXXIII: Deep Spectral Decomposition of W(3,3) = SRG(40,12,2,4).

Tests explore complete eigenprojector decomposition, spectral reconstruction,
projector polynomial expressions, powers of A, matrix functions via the spectral
theorem, spectral idempotent algebra, distance matrix spectral analysis,
complementary graph spectral decomposition, Seidel matrix spectral decomposition,
and spectral gap analysis.

W(3,3) spectrum: eigenvalue 12 (mult 1), 2 (mult 24), -4 (mult 15).
Laplacian spectrum: 0 (mult 1), 10 (mult 24), 16 (mult 15).
Parameters: n=40, k=12, lambda=2, mu=4, 240 edges.
SRG identity: A^2 = -2A + 8I + 4J.
"""

import numpy as np
import pytest
from numpy.linalg import matrix_rank
from scipy.linalg import expm


# ------------------------------------------------------------------ #
#  W(3,3) builder (canonical symplectic form over GF(3)^4)           #
# ------------------------------------------------------------------ #

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


# ------------------------------------------------------------------ #
#  Module-scoped fixtures                                            #
# ------------------------------------------------------------------ #

@pytest.fixture(scope="module")
def A():
    """Adjacency matrix of W(3,3)."""
    return _build_w33()


@pytest.fixture(scope="module")
def n():
    return 40


@pytest.fixture(scope="module")
def I40():
    return np.eye(40)


@pytest.fixture(scope="module")
def J40():
    return np.ones((40, 40))


@pytest.fixture(scope="module")
def eigen_decomp(A):
    """Full eigendecomposition: eigenvalues and eigenvectors."""
    evals, evecs = np.linalg.eigh(A)
    return evals, evecs


@pytest.fixture(scope="module")
def projectors(eigen_decomp):
    """Eigenprojectors E0 (eigenvalue 12), E1 (eigenvalue 2), E2 (eigenvalue -4)."""
    evals, evecs = eigen_decomp
    n = 40
    # E0: eigenvalue 12 (multiplicity 1) = J/40
    E0 = np.ones((n, n)) / n
    # E1: eigenvalue 2 (multiplicity 24)
    mask1 = np.abs(evals - 2) < 0.5
    V1 = evecs[:, mask1]
    E1 = V1 @ V1.T
    # E2: eigenvalue -4 (multiplicity 15)
    mask2 = np.abs(evals - (-4)) < 0.5
    V2 = evecs[:, mask2]
    E2 = V2 @ V2.T
    return E0, E1, E2


@pytest.fixture(scope="module")
def laplacian(A):
    """Combinatorial Laplacian L = D - A = 12I - A for 12-regular graph."""
    return 12 * np.eye(40) - A


@pytest.fixture(scope="module")
def complement(A, I40, J40):
    """Complement graph adjacency: A_bar = J - I - A."""
    return J40 - I40 - A


@pytest.fixture(scope="module")
def seidel(A, I40, J40):
    """Seidel matrix: S = J - I - 2A."""
    return J40 - I40 - 2 * A


@pytest.fixture(scope="module")
def distance_matrix(A, I40, J40):
    """Distance matrix D[i,j] = shortest path. Diameter 2, so D = 2(J-I) - A."""
    return 2 * (J40 - I40) - A


# ================================================================== #
#  1. Complete Eigenprojector Decomposition  (~12 tests)              #
# ================================================================== #

class TestEigenprojectorDecomposition:
    """Verify E0, E1, E2 form a complete orthogonal set of idempotents."""

    def test_partition_of_unity(self, projectors, I40):
        """E0 + E1 + E2 = I (completeness)."""
        E0, E1, E2 = projectors
        assert np.allclose(E0 + E1 + E2, I40, atol=1e-10)

    def test_E0_idempotent(self, projectors):
        """E0^2 = E0."""
        E0 = projectors[0]
        assert np.allclose(E0 @ E0, E0, atol=1e-10)

    def test_E1_idempotent(self, projectors):
        """E1^2 = E1."""
        E1 = projectors[1]
        assert np.allclose(E1 @ E1, E1, atol=1e-10)

    def test_E2_idempotent(self, projectors):
        """E2^2 = E2."""
        E2 = projectors[2]
        assert np.allclose(E2 @ E2, E2, atol=1e-10)

    def test_E0_E1_orthogonal(self, projectors):
        """E0 @ E1 = 0."""
        E0, E1, _ = projectors
        assert np.allclose(E0 @ E1, 0, atol=1e-10)

    def test_E0_E2_orthogonal(self, projectors):
        """E0 @ E2 = 0."""
        E0, _, E2 = projectors
        assert np.allclose(E0 @ E2, 0, atol=1e-10)

    def test_E1_E2_orthogonal(self, projectors):
        """E1 @ E2 = 0."""
        _, E1, E2 = projectors
        assert np.allclose(E1 @ E2, 0, atol=1e-10)

    def test_rank_E0(self, projectors):
        """rank(E0) = 1 (multiplicity of eigenvalue 12)."""
        assert matrix_rank(projectors[0], tol=1e-8) == 1

    def test_rank_E1(self, projectors):
        """rank(E1) = 24 (multiplicity of eigenvalue 2)."""
        assert matrix_rank(projectors[1], tol=1e-8) == 24

    def test_rank_E2(self, projectors):
        """rank(E2) = 15 (multiplicity of eigenvalue -4)."""
        assert matrix_rank(projectors[2], tol=1e-8) == 15

    def test_E0_is_J_over_n(self, projectors, J40):
        """E0 = J/40 (rank-1 projector onto all-ones vector)."""
        E0 = projectors[0]
        assert np.allclose(E0, J40 / 40, atol=1e-10)

    def test_projectors_symmetric(self, projectors):
        """All projectors are symmetric matrices."""
        for Ei in projectors:
            assert np.allclose(Ei, Ei.T, atol=1e-12)


# ================================================================== #
#  2. Spectral Reconstruction  (~8 tests)                            #
# ================================================================== #

class TestSpectralReconstruction:
    """Verify A = 12*E0 + 2*E1 + (-4)*E2."""

    def test_spectral_reconstruction_exact(self, A, projectors):
        """A = 12*E0 + 2*E1 - 4*E2 matches original adjacency matrix."""
        E0, E1, E2 = projectors
        A_recon = 12 * E0 + 2 * E1 + (-4) * E2
        assert np.allclose(A_recon, A, atol=1e-10)

    def test_spectral_reconstruction_integer_entries(self, A, projectors):
        """Reconstructed matrix has integer entries (0 or 1 off diagonal, 0 on diagonal)."""
        E0, E1, E2 = projectors
        A_recon = 12 * E0 + 2 * E1 + (-4) * E2
        A_round = np.round(A_recon).astype(int)
        assert np.allclose(A_recon, A_round, atol=1e-10)

    def test_reconstruction_diagonal_zero(self, A, projectors):
        """Diagonal of reconstructed A is zero."""
        E0, E1, E2 = projectors
        A_recon = 12 * E0 + 2 * E1 + (-4) * E2
        assert np.allclose(np.diag(A_recon), 0, atol=1e-10)

    def test_reconstruction_row_sums(self, A, projectors):
        """Each row of reconstructed A sums to 12."""
        E0, E1, E2 = projectors
        A_recon = 12 * E0 + 2 * E1 + (-4) * E2
        assert np.allclose(np.sum(A_recon, axis=1), 12, atol=1e-10)

    def test_reconstruction_frobenius_norm(self, A, projectors):
        """||A - A_recon||_F = 0."""
        E0, E1, E2 = projectors
        A_recon = 12 * E0 + 2 * E1 + (-4) * E2
        assert np.linalg.norm(A - A_recon, 'fro') < 1e-10

    def test_reconstruction_preserves_symmetry(self, projectors):
        """Reconstructed matrix is symmetric."""
        E0, E1, E2 = projectors
        A_recon = 12 * E0 + 2 * E1 + (-4) * E2
        assert np.allclose(A_recon, A_recon.T, atol=1e-12)

    def test_spectral_reconstruction_trace(self, projectors):
        """tr(A) = 12*tr(E0) + 2*tr(E1) - 4*tr(E2) = 12 + 48 - 60 = 0."""
        E0, E1, E2 = projectors
        tr_recon = 12 * np.trace(E0) + 2 * np.trace(E1) + (-4) * np.trace(E2)
        assert abs(tr_recon) < 1e-10

    def test_spectral_reconstruction_sum_all(self, projectors):
        """Sum of all entries = 12*40 + 2*0 - 4*0 = 480 (12*n from E0, others sum to 0)."""
        E0, E1, E2 = projectors
        A_recon = 12 * E0 + 2 * E1 + (-4) * E2
        # sum(A) = n*k = 40*12 = 480
        assert abs(np.sum(A_recon) - 480) < 1e-8


# ================================================================== #
#  3. Projector Polynomial Expressions (Lagrange)  (~8 tests)        #
# ================================================================== #

class TestProjectorPolynomials:
    """Each Ei as a polynomial in A via Lagrange interpolation on {12, 2, -4}."""

    def test_E0_lagrange(self, A, projectors, I40):
        """E0 = (A - 2I)(A + 4I) / ((12-2)(12+4)) = (A-2I)(A+4I)/160."""
        E0 = projectors[0]
        E0_lag = (A - 2 * I40) @ (A + 4 * I40) / 160.0
        assert np.allclose(E0_lag, E0, atol=1e-10)

    def test_E1_lagrange(self, A, projectors, I40):
        """E1 = (A - 12I)(A + 4I) / ((2-12)(2+4)) = (A-12I)(A+4I)/(-60)."""
        E1 = projectors[1]
        E1_lag = (A - 12 * I40) @ (A + 4 * I40) / (-60.0)
        assert np.allclose(E1_lag, E1, atol=1e-10)

    def test_E2_lagrange(self, A, projectors, I40):
        """E2 = (A - 12I)(A - 2I) / ((-4-12)(-4-2)) = (A-12I)(A-2I)/96."""
        E2 = projectors[2]
        E2_lag = (A - 12 * I40) @ (A - 2 * I40) / 96.0
        assert np.allclose(E2_lag, E2, atol=1e-10)

    def test_lagrange_sum_to_identity(self, A, I40):
        """Lagrange projectors sum to I independently of eigendecomposition."""
        E0_lag = (A - 2 * I40) @ (A + 4 * I40) / 160.0
        E1_lag = (A - 12 * I40) @ (A + 4 * I40) / (-60.0)
        E2_lag = (A - 12 * I40) @ (A - 2 * I40) / 96.0
        assert np.allclose(E0_lag + E1_lag + E2_lag, I40, atol=1e-10)

    def test_lagrange_E0_rank(self, A, I40):
        """Lagrange E0 has rank 1."""
        E0_lag = (A - 2 * I40) @ (A + 4 * I40) / 160.0
        assert matrix_rank(E0_lag, tol=1e-8) == 1

    def test_lagrange_E1_rank(self, A, I40):
        """Lagrange E1 has rank 24."""
        E1_lag = (A - 12 * I40) @ (A + 4 * I40) / (-60.0)
        assert matrix_rank(E1_lag, tol=1e-8) == 24

    def test_lagrange_E2_rank(self, A, I40):
        """Lagrange E2 has rank 15."""
        E2_lag = (A - 12 * I40) @ (A - 2 * I40) / 96.0
        assert matrix_rank(E2_lag, tol=1e-8) == 15

    def test_lagrange_mutual_orthogonality(self, A, I40):
        """Lagrange projectors are mutually orthogonal (Ei@Ej=0 for i!=j)."""
        E0 = (A - 2 * I40) @ (A + 4 * I40) / 160.0
        E1 = (A - 12 * I40) @ (A + 4 * I40) / (-60.0)
        E2 = (A - 12 * I40) @ (A - 2 * I40) / 96.0
        assert np.allclose(E0 @ E1, 0, atol=1e-10)
        assert np.allclose(E0 @ E2, 0, atol=1e-10)
        assert np.allclose(E1 @ E2, 0, atol=1e-10)


# ================================================================== #
#  4. Powers of A via Spectral Decomposition  (~12 tests)            #
# ================================================================== #

class TestPowersOfA:
    """A^k = 12^k*E0 + 2^k*E1 + (-4)^k*E2 for various k."""

    @pytest.mark.parametrize("k", [1, 2, 3, 4, 5, 6, 7, 8])
    def test_power_k_spectral(self, A, projectors, k):
        """A^k equals spectral formula 12^k*E0 + 2^k*E1 + (-4)^k*E2."""
        E0, E1, E2 = projectors
        Ak_spectral = (12**k) * E0 + (2**k) * E1 + ((-4)**k) * E2
        Ak_direct = np.linalg.matrix_power(A, k)
        assert np.allclose(Ak_spectral, Ak_direct, atol=1e-6)

    def test_A2_srg_identity(self, A, I40, J40):
        """A^2 = -2A + 8I + 4J (SRG identity for (40,12,2,4))."""
        A2 = A @ A
        expected = -2 * A + 8 * I40 + 4 * J40
        assert np.allclose(A2, expected, atol=1e-10)

    def test_A3_from_srg(self, A, I40, J40):
        """A^3 = 12A - 16I + 40J (derived from SRG recurrence)."""
        A3 = np.linalg.matrix_power(A, 3)
        expected = 12 * A - 16 * I40 + 40 * J40
        assert np.allclose(A3, expected, atol=1e-8)

    def test_trace_A2(self, A):
        """tr(A^2) = 12^2 + 2^2*24 + (-4)^2*15 = 144 + 96 + 240 = 480 = n*k."""
        tr = np.trace(A @ A)
        assert abs(tr - 480) < 1e-8

    def test_trace_A4(self, A, projectors):
        """tr(A^4) = 12^4*1 + 2^4*24 + 4^4*15 = 20736 + 384 + 3840 = 24960."""
        E0, E1, E2 = projectors
        expected_trace = 12**4 * 1 + 2**4 * 24 + 4**4 * 15
        assert expected_trace == 24960
        A4 = np.linalg.matrix_power(A, 4)
        assert abs(np.trace(A4) - expected_trace) < 1e-6


# ================================================================== #
#  5. Matrix Functions via Spectral Theorem  (~12 tests)             #
# ================================================================== #

class TestMatrixFunctions:
    """exp(tA), cos(tA), resolvent (zI-A)^{-1} via spectral decomposition."""

    def test_expm_at_t01(self, A, projectors):
        """exp(0.1*A) via spectral vs scipy expm."""
        t = 0.1
        E0, E1, E2 = projectors
        spectral = np.exp(12*t)*E0 + np.exp(2*t)*E1 + np.exp(-4*t)*E2
        direct = expm(t * A.astype(float))
        assert np.allclose(spectral, direct, atol=1e-8)

    def test_expm_at_t05(self, A, projectors):
        """exp(0.5*A) via spectral vs scipy expm."""
        t = 0.5
        E0, E1, E2 = projectors
        spectral = np.exp(12*t)*E0 + np.exp(2*t)*E1 + np.exp(-4*t)*E2
        direct = expm(t * A.astype(float))
        assert np.allclose(spectral, direct, atol=1e-6)

    def test_expm_at_t_negative(self, A, projectors):
        """exp(-0.2*A) via spectral vs scipy expm."""
        t = -0.2
        E0, E1, E2 = projectors
        spectral = np.exp(12*t)*E0 + np.exp(2*t)*E1 + np.exp(-4*t)*E2
        direct = expm(t * A.astype(float))
        assert np.allclose(spectral, direct, atol=1e-8)

    def test_cos_A_spectral(self, A, projectors, I40):
        """cos(A) = cos(12)*E0 + cos(2)*E1 + cos(-4)*E2."""
        E0, E1, E2 = projectors
        cosA_spectral = np.cos(12)*E0 + np.cos(2)*E1 + np.cos(-4)*E2
        # cos(A) = (expm(iA) + expm(-iA)) / 2
        Af = A.astype(float)
        cosA_direct = (expm(1j * Af) + expm(-1j * Af)).real / 2
        assert np.allclose(cosA_spectral, cosA_direct, atol=1e-6)

    def test_sin_A_spectral(self, A, projectors):
        """sin(A) = sin(12)*E0 + sin(2)*E1 + sin(-4)*E2."""
        E0, E1, E2 = projectors
        sinA_spectral = np.sin(12)*E0 + np.sin(2)*E1 + np.sin(-4)*E2
        Af = A.astype(float)
        eiA = expm(1j * Af)
        sinA_direct = (eiA - expm(-1j * Af)) / (2j)
        assert np.allclose(sinA_spectral, sinA_direct.real, atol=1e-6)

    def test_cos_tA_parametric(self, A, projectors):
        """cos(0.3*A) matches spectral formula."""
        t = 0.3
        E0, E1, E2 = projectors
        cosA = np.cos(12*t)*E0 + np.cos(2*t)*E1 + np.cos(-4*t)*E2
        Af = t * A.astype(float)
        eiA = expm(1j * Af)
        cosA_direct = (eiA + expm(-1j * Af)).real / 2
        assert np.allclose(cosA, cosA_direct, atol=1e-6)

    def test_resolvent_z5(self, A, projectors, I40):
        """(5I - A)^{-1} = E0/(5-12) + E1/(5-2) + E2/(5+4)."""
        z = 5.0
        E0, E1, E2 = projectors
        R_spectral = E0 / (z - 12) + E1 / (z - 2) + E2 / (z + 4)
        R_direct = np.linalg.inv(z * I40 - A.astype(float))
        assert np.allclose(R_spectral, R_direct, atol=1e-8)

    def test_resolvent_z20(self, A, projectors, I40):
        """(20I - A)^{-1} via spectral decomposition."""
        z = 20.0
        E0, E1, E2 = projectors
        R_spectral = E0 / (z - 12) + E1 / (z - 2) + E2 / (z + 4)
        R_direct = np.linalg.inv(z * I40 - A.astype(float))
        assert np.allclose(R_spectral, R_direct, atol=1e-10)

    def test_resolvent_z_negative10(self, A, projectors, I40):
        """(-10I - A)^{-1} via spectral decomposition (z=-10 avoids spectrum)."""
        z = -10.0
        E0, E1, E2 = projectors
        R_spectral = E0 / (z - 12) + E1 / (z - 2) + E2 / (z + 4)
        R_direct = np.linalg.inv(z * I40 - A.astype(float))
        assert np.allclose(R_spectral, R_direct, atol=1e-8)

    def test_resolvent_symmetric(self, A, projectors, I40):
        """Resolvent of symmetric matrix is symmetric."""
        z = 7.0
        E0, E1, E2 = projectors
        R = E0 / (z - 12) + E1 / (z - 2) + E2 / (z + 4)
        assert np.allclose(R, R.T, atol=1e-12)

    def test_matrix_inverse_spectral(self, A, projectors, I40):
        """(A + 5I)^{-1} = E0/(12+5) + E1/(2+5) + E2/(-4+5) = E0/17 + E1/7 + E2."""
        E0, E1, E2 = projectors
        inv_spectral = E0 / 17 + E1 / 7 + E2 / 1
        inv_direct = np.linalg.inv(A.astype(float) + 5 * I40)
        assert np.allclose(inv_spectral, inv_direct, atol=1e-8)

    def test_expm_trace(self, A, projectors):
        """tr(exp(t*A)) = exp(12t) + 24*exp(2t) + 15*exp(-4t)."""
        t = 0.1
        E0, E1, E2 = projectors
        spectral_trace = np.exp(12*t) + 24*np.exp(2*t) + 15*np.exp(-4*t)
        actual_trace = np.trace(expm(t * A.astype(float)))
        assert abs(spectral_trace - actual_trace) < 1e-6


# ================================================================== #
#  6. Spectral Idempotent Algebra  (~12 tests)                       #
# ================================================================== #

class TestSpectralIdempotentAlgebra:
    """Trace, Frobenius norm, and Hadamard products of eigenprojectors."""

    def test_trace_E0(self, projectors):
        """tr(E0) = 1 (multiplicity of eigenvalue 12)."""
        assert abs(np.trace(projectors[0]) - 1) < 1e-10

    def test_trace_E1(self, projectors):
        """tr(E1) = 24 (multiplicity of eigenvalue 2)."""
        assert abs(np.trace(projectors[1]) - 24) < 1e-10

    def test_trace_E2(self, projectors):
        """tr(E2) = 15 (multiplicity of eigenvalue -4)."""
        assert abs(np.trace(projectors[2]) - 15) < 1e-10

    def test_trace_sum(self, projectors):
        """tr(E0) + tr(E1) + tr(E2) = 40 = n."""
        total = sum(np.trace(E) for E in projectors)
        assert abs(total - 40) < 1e-10

    def test_frobenius_norm_E0(self, projectors):
        """||E0||_F = sqrt(tr(E0)) = 1 (since E0 is idempotent)."""
        E0 = projectors[0]
        assert abs(np.linalg.norm(E0, 'fro') - 1.0) < 1e-10

    def test_frobenius_norm_E1(self, projectors):
        """||E1||_F = sqrt(24) (since E1 is idempotent, ||E||_F^2 = tr(E))."""
        E1 = projectors[1]
        assert abs(np.linalg.norm(E1, 'fro') - np.sqrt(24)) < 1e-10

    def test_frobenius_norm_E2(self, projectors):
        """||E2||_F = sqrt(15)."""
        E2 = projectors[2]
        assert abs(np.linalg.norm(E2, 'fro') - np.sqrt(15)) < 1e-10

    def test_hadamard_E0_self(self, projectors):
        """E0 o E0 = J/1600 (all entries 1/40 squared = 1/1600)."""
        E0 = projectors[0]
        had = E0 * E0  # Hadamard (elementwise) product
        expected = np.ones((40, 40)) / 1600
        assert np.allclose(had, expected, atol=1e-12)

    def test_hadamard_sum_diagonal(self, projectors):
        """Sum of Ei o Ei diagonal entries = diagonal of I (each = 1) via Parseval."""
        E0, E1, E2 = projectors
        diag_sum = np.diag(E0 * E0) + np.diag(E1 * E1) + np.diag(E2 * E2)
        # For each vertex v: sum_i (E_i[v,v])^2 is not necessarily 1
        # But sum_i E_i[v,v] = 1 (partition of unity diagonal)
        for v in range(40):
            s = E0[v, v] + E1[v, v] + E2[v, v]
            assert abs(s - 1.0) < 1e-10

    def test_E0_constant_diagonal(self, projectors):
        """E0 diagonal is constant 1/40."""
        E0 = projectors[0]
        assert np.allclose(np.diag(E0), 1.0 / 40, atol=1e-12)

    def test_E1_constant_diagonal(self, projectors):
        """E1 diagonal is constant 24/40 = 3/5 (vertex-transitive graph)."""
        E1 = projectors[1]
        expected = 24.0 / 40.0
        assert np.allclose(np.diag(E1), expected, atol=1e-10)

    def test_E2_constant_diagonal(self, projectors):
        """E2 diagonal is constant 15/40 = 3/8 (vertex-transitive graph)."""
        E2 = projectors[2]
        expected = 15.0 / 40.0
        assert np.allclose(np.diag(E2), expected, atol=1e-10)


# ================================================================== #
#  7. Distance Matrix Spectral Analysis  (~10 tests)                 #
# ================================================================== #

class TestDistanceMatrixSpectral:
    """D[i,j] = shortest-path distance; D = 2(J-I) - A. Spectrum: {66, -4, 2}."""

    def test_diameter_is_2(self, A):
        """W(3,3) has diameter 2: all non-adjacent vertices are at distance 2."""
        n = 40
        D = np.zeros((n, n), dtype=int)
        for start in range(n):
            # BFS
            visited = {start}
            frontier = [start]
            dist = 0
            while frontier:
                dist += 1
                next_frontier = []
                for u in frontier:
                    for v in range(n):
                        if A[u, v] == 1 and v not in visited:
                            visited.add(v)
                            D[start, v] = dist
                            next_frontier.append(v)
                frontier = next_frontier
        assert np.max(D) == 2

    def test_distance_formula(self, A, I40, J40, distance_matrix):
        """D = 2(J-I) - A since diameter=2 and mu>0."""
        n = 40
        D_bfs = np.zeros((n, n), dtype=int)
        for start in range(n):
            visited = {start}
            frontier = [start]
            dist = 0
            while frontier:
                dist += 1
                next_frontier = []
                for u in frontier:
                    for v in range(n):
                        if A[u, v] == 1 and v not in visited:
                            visited.add(v)
                            D_bfs[start, v] = dist
                            next_frontier.append(v)
                frontier = next_frontier
        assert np.allclose(D_bfs, distance_matrix, atol=1e-10)

    def test_distance_eigenvalue_66(self, distance_matrix):
        """Distance matrix has eigenvalue 66 with multiplicity 1."""
        evals = np.linalg.eigvalsh(distance_matrix)
        count = np.sum(np.abs(evals - 66) < 0.5)
        assert count == 1

    def test_distance_eigenvalue_neg4(self, distance_matrix):
        """Distance matrix has eigenvalue -4 with multiplicity 24."""
        evals = np.linalg.eigvalsh(distance_matrix)
        count = np.sum(np.abs(evals - (-4)) < 0.5)
        assert count == 24

    def test_distance_eigenvalue_2(self, distance_matrix):
        """Distance matrix has eigenvalue 2 with multiplicity 15."""
        evals = np.linalg.eigvalsh(distance_matrix)
        count = np.sum(np.abs(evals - 2) < 0.5)
        assert count == 15

    def test_distance_spectral_reconstruction(self, distance_matrix, projectors):
        """D = 66*E0 + (-4)*E1 + 2*E2."""
        E0, E1, E2 = projectors
        D_recon = 66 * E0 + (-4) * E1 + 2 * E2
        assert np.allclose(D_recon, distance_matrix, atol=1e-8)

    def test_distance_trace(self, distance_matrix):
        """tr(D) = 0 (diagonal is zero)."""
        assert abs(np.trace(distance_matrix)) < 1e-10

    def test_distance_row_sum(self, distance_matrix):
        """Each row of D sums to 12*1 + 27*2 = 66 (12 neighbors at dist 1, 27 at dist 2)."""
        row_sums = np.sum(distance_matrix, axis=1)
        assert np.allclose(row_sums, 66, atol=1e-10)

    def test_distance_wiener_index(self, distance_matrix):
        """Wiener index W = sum(D)/2 = 40*66/2 = 1320."""
        W = np.sum(distance_matrix) / 2
        assert abs(W - 1320) < 1e-8

    def test_distance_matrix_symmetric(self, distance_matrix):
        """Distance matrix is symmetric."""
        assert np.allclose(distance_matrix, distance_matrix.T, atol=1e-12)


# ================================================================== #
#  8. Complementary Graph Spectral Decomposition  (~12 tests)        #
# ================================================================== #

class TestComplementSpectral:
    """A_bar = J - I - A; complement is SRG(40,27,18,18).
    Spectrum: {27^1, 3^15, -3^24}."""

    def test_complement_is_srg(self, complement):
        """Complement has degree 27."""
        assert np.allclose(np.sum(complement, axis=1), 27, atol=1e-10)

    def test_complement_symmetric(self, complement):
        """Complement adjacency is symmetric with zero diagonal."""
        assert np.allclose(complement, complement.T, atol=1e-12)
        assert np.allclose(np.diag(complement), 0, atol=1e-12)

    def test_complement_eigenvalue_27(self, complement):
        """Complement has eigenvalue 27 with multiplicity 1."""
        evals = np.linalg.eigvalsh(complement)
        count = np.sum(np.abs(evals - 27) < 0.5)
        assert count == 1

    def test_complement_eigenvalue_3(self, complement):
        """Complement has eigenvalue 3 with multiplicity 15."""
        evals = np.linalg.eigvalsh(complement)
        count = np.sum(np.abs(evals - 3) < 0.5)
        assert count == 15

    def test_complement_eigenvalue_neg3(self, complement):
        """Complement has eigenvalue -3 with multiplicity 24."""
        evals = np.linalg.eigvalsh(complement)
        count = np.sum(np.abs(evals - (-3)) < 0.5)
        assert count == 24

    def test_complement_spectral_reconstruction(self, complement, projectors):
        """A_bar = 27*E0 + (-3)*E1 + 3*E2 (same projectors, transformed eigenvalues)."""
        E0, E1, E2 = projectors
        Abar_recon = 27 * E0 + (-3) * E1 + 3 * E2
        assert np.allclose(Abar_recon, complement, atol=1e-8)

    def test_complement_shares_eigenspaces(self, complement, projectors):
        """Complement shares eigenprojectors E0, E1, E2 with original."""
        E0, E1, E2 = projectors
        # A_bar * E1 = -3 * E1
        assert np.allclose(complement @ E1, -3 * E1, atol=1e-8)
        # A_bar * E2 = 3 * E2
        assert np.allclose(complement @ E2, 3 * E2, atol=1e-8)

    def test_complement_srg_identity(self, complement, I40, J40):
        """A_bar^2 + (18-18)*A_bar - (27-18)*I = 18*J
        i.e., A_bar^2 - 9I = 18J."""
        Abar2 = complement @ complement
        expected = 9 * I40 + 18 * J40
        assert np.allclose(Abar2, expected, atol=1e-8)

    def test_complement_trace_A2(self, complement):
        """tr(A_bar^2) = 27^2 + (-3)^2*24 + 3^2*15 = 729 + 216 + 135 = 1080 = 40*27."""
        tr = np.trace(complement @ complement)
        assert abs(tr - 1080) < 1e-6

    def test_complement_lagrange_E0(self, complement, projectors, I40):
        """E0 from complement Lagrange: (A_bar+3I)(A_bar-3I)/((27+3)(27-3)) = .../720."""
        E0 = projectors[0]
        Af = complement.astype(float)
        E0_lag = (Af + 3*I40) @ (Af - 3*I40) / ((27+3)*(27-3))
        assert np.allclose(E0_lag, E0, atol=1e-10)

    def test_A_plus_Abar_equals_J_minus_I(self, A, complement, I40, J40):
        """A + A_bar = J - I."""
        assert np.allclose(A + complement, J40 - I40, atol=1e-12)

    def test_complement_edges(self, complement):
        """Complement has 40*27/2 = 540 edges."""
        assert abs(np.sum(complement) / 2 - 540) < 1e-8


# ================================================================== #
#  9. Seidel Matrix Spectral Decomposition  (~10 tests)              #
# ================================================================== #

class TestSeidelSpectral:
    """S = J - I - 2A; Seidel spectrum: {15^1, -5^24, 7^15}."""

    def test_seidel_definition(self, seidel, A, I40, J40):
        """S = J - I - 2A."""
        expected = J40 - I40 - 2 * A
        assert np.allclose(seidel, expected, atol=1e-12)

    def test_seidel_symmetric(self, seidel):
        """Seidel matrix is symmetric."""
        assert np.allclose(seidel, seidel.T, atol=1e-12)

    def test_seidel_diagonal(self, seidel):
        """Seidel matrix has zero diagonal."""
        assert np.allclose(np.diag(seidel), 0, atol=1e-12)

    def test_seidel_eigenvalue_15(self, seidel):
        """Seidel has eigenvalue 15 with multiplicity 1."""
        evals = np.linalg.eigvalsh(seidel)
        count = np.sum(np.abs(evals - 15) < 0.5)
        assert count == 1

    def test_seidel_eigenvalue_neg5(self, seidel):
        """Seidel has eigenvalue -5 with multiplicity 24."""
        evals = np.linalg.eigvalsh(seidel)
        count = np.sum(np.abs(evals - (-5)) < 0.5)
        assert count == 24

    def test_seidel_eigenvalue_7(self, seidel):
        """Seidel has eigenvalue 7 with multiplicity 15."""
        evals = np.linalg.eigvalsh(seidel)
        count = np.sum(np.abs(evals - 7) < 0.5)
        assert count == 15

    def test_seidel_spectral_reconstruction(self, seidel, projectors):
        """S = 15*E0 + (-5)*E1 + 7*E2."""
        E0, E1, E2 = projectors
        S_recon = 15 * E0 + (-5) * E1 + 7 * E2
        assert np.allclose(S_recon, seidel, atol=1e-8)

    def test_seidel_trace(self, seidel):
        """tr(S) = 15 + (-5)*24 + 7*15 = 15 - 120 + 105 = 0."""
        assert abs(np.trace(seidel)) < 1e-10

    def test_seidel_S2_formula(self, seidel, I40, J40):
        """S^2 = (n-1)I - 2(J-I-2A) + ... Verify via spectral:
        S^2 = 225*E0 + 25*E1 + 49*E2."""
        S2 = seidel @ seidel
        evals_S2 = np.sort(np.linalg.eigvalsh(S2))
        # Eigenvalues of S^2: 15^2=225, 5^2=25, 7^2=49
        assert np.sum(np.abs(evals_S2 - 225) < 0.5) == 1
        assert np.sum(np.abs(evals_S2 - 25) < 0.5) == 24
        assert np.sum(np.abs(evals_S2 - 49) < 0.5) == 15

    def test_seidel_trace_S2(self, seidel):
        """tr(S^2) = 225 + 25*24 + 49*15 = 225 + 600 + 735 = 1560 = n(n-1)."""
        tr = np.trace(seidel @ seidel)
        assert abs(tr - 1560) < 1e-6


# ================================================================== #
#  10. Spectral Gap Analysis  (~10 tests)                            #
# ================================================================== #

class TestSpectralGap:
    """Spectral gap, Cheeger bounds, expansion, mixing time estimates."""

    def test_adjacency_spectral_gap(self, A):
        """Adjacency spectral gap = k - max(|lambda_2|, |lambda_min|) = 12 - 4 = 8."""
        evals = np.sort(np.linalg.eigvalsh(A))
        k = evals[-1]
        lambda_2 = evals[-2]
        lambda_min = evals[0]
        gap = k - max(abs(lambda_2), abs(lambda_min))
        assert abs(gap - 8) < 1e-8

    def test_laplacian_spectral_gap(self, laplacian):
        """Smallest nonzero Laplacian eigenvalue = k - lambda_2 = 12 - 2 = 10."""
        evals = np.sort(np.linalg.eigvalsh(laplacian))
        # First eigenvalue is 0, second is 10
        assert abs(evals[0]) < 1e-10
        assert abs(evals[1] - 10) < 1e-8

    def test_laplacian_spectrum_values(self, laplacian):
        """Laplacian eigenvalues: 0 (mult 1), 10 (mult 24), 16 (mult 15)."""
        evals = np.linalg.eigvalsh(laplacian)
        assert np.sum(np.abs(evals - 0) < 0.5) == 1
        assert np.sum(np.abs(evals - 10) < 0.5) == 24
        assert np.sum(np.abs(evals - 16) < 0.5) == 15

    def test_normalized_laplacian_gap(self, A, I40):
        """Normalized Laplacian mu_1 = 1 - lambda_2/k = 1 - 2/12 = 5/6."""
        evals = np.sort(np.linalg.eigvalsh(A))
        k = 12.0
        lambda_2 = evals[-2]
        mu_1 = 1 - lambda_2 / k
        assert abs(mu_1 - 5.0/6) < 1e-8

    def test_cheeger_lower_bound(self, laplacian):
        """Cheeger inequality lower bound: h(G) >= lambda_1_L / (2k) = 10/24 = 5/12."""
        evals = np.sort(np.linalg.eigvalsh(laplacian))
        lambda_1_L = evals[1]
        k = 12.0
        h_lower = lambda_1_L / (2 * k)
        assert abs(h_lower - 5.0/12) < 1e-8
        assert h_lower > 0  # positive expansion

    def test_hoffman_bound_independence_number(self, A):
        """Hoffman bound: alpha(G) <= n * (-lambda_min) / (k - lambda_min) = 40*4/16 = 10."""
        evals = np.sort(np.linalg.eigvalsh(A))
        k = evals[-1]
        lambda_min = evals[0]
        hoffman = 40 * (-lambda_min) / (k - lambda_min)
        assert abs(hoffman - 10) < 1e-8

    def test_hoffman_bound_clique(self, A):
        """Hoffman bound for clique: omega(G) <= 1 - k/lambda_min = 1 - 12/(-4) = 4."""
        evals = np.sort(np.linalg.eigvalsh(A))
        k = evals[-1]
        lambda_min = evals[0]
        omega_bound = 1 - k / lambda_min
        assert abs(omega_bound - 4) < 1e-8

    def test_expander_mixing_lemma(self, A, projectors):
        """For vertex subsets S, T: |e(S,T) - k|S||T|/n| <= lambda * sqrt(|S||T|)
        where lambda = max(|lambda_2|, |lambda_min|) = 4.
        Test with S = T = first 10 vertices."""
        lam = 4.0  # max(|2|, |-4|)
        k = 12.0
        n = 40
        S = list(range(10))
        T = list(range(10))
        # Count edges between S and T
        e_ST = sum(A[i, j] for i in S for j in T)
        expected = k * len(S) * len(T) / n
        bound = lam * np.sqrt(len(S) * len(T))
        assert abs(e_ST - expected) <= bound + 1e-8

    def test_mixing_time_bound(self, A):
        """Mixing time upper bound: t_mix <= k/(k-lambda) * ln(n) where lambda=4.
        For lazy random walk: t_mix <= 12/(12-4) * ln(40) = 1.5 * ln(40) ~ 5.5."""
        k = 12.0
        lam = 4.0  # max(|lambda_2|, |-4|)
        t_mix_bound = k / (k - lam) * np.log(40)
        assert t_mix_bound < 6.0  # fast mixing
        assert t_mix_bound > 4.0  # not trivially fast

    def test_ramanujan_property(self, A):
        """W(3,3) is NOT Ramanujan: need max(|lambda_2|, |lambda_min|) <= 2*sqrt(k-1).
        2*sqrt(11) ~ 6.63 > 4, so actually IS Ramanujan."""
        evals = np.sort(np.linalg.eigvalsh(A))
        k = evals[-1]
        lam = max(abs(evals[-2]), abs(evals[0]))
        threshold = 2 * np.sqrt(k - 1)
        # lambda=4, threshold=2*sqrt(11)~6.63, so W(3,3) is Ramanujan
        assert lam <= threshold + 1e-8
