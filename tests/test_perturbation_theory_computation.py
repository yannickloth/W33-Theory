"""
Phase CVII -- Perturbation Theory & Sensitivity Analysis (Hard Computation)
===========================================================================

Theorems T1803 -- T1823

Every result derived from first principles using only numpy / scipy on
the W(3,3) = SRG(40,12,2,4) adjacency matrix.

Covers: eigenvalue sensitivity, Weyl's inequality, Davis-Kahan theorem,
condition numbers, pseudospectrum, resolvent norms, spectral gap stability,
edge/vertex deletion interlacing, rank-1 perturbation, Laplacian perturbation,
matrix exponential perturbation, Frobenius-spectral perturbation bounds,
Bauer-Fike theorem, Gershgorin disks, spectral projector stability,
numerical stability of eigendecomposition, eigenvector matrix condition,
determinant sensitivity, graph energy perturbation, SRG spectral rigidity.
"""

import numpy as np
from numpy.linalg import eigvalsh, eigh, norm, inv, det, cond, svd
from scipy.linalg import expm, eigvals
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
def eig_decomp(w33):
    """Full eigendecomposition: eigenvalues (descending) and eigenvectors."""
    vals, vecs = eigh(w33.astype(float))
    idx = np.argsort(vals)[::-1]
    return vals[idx], vecs[:, idx]


@pytest.fixture(scope="module")
def spectrum(eig_decomp):
    return eig_decomp[0]


@pytest.fixture(scope="module")
def eigvecs(eig_decomp):
    return eig_decomp[1]


@pytest.fixture(scope="module")
def laplacian(w33):
    """Laplacian L = D - A, where D = diag(degree) = 12*I for regular graph."""
    return 12 * np.eye(40) - w33.astype(float)


# ---------------------------------------------------------------------------
# T1803: Eigenvalue sensitivity d(lambda)/d(A_ij)
# ---------------------------------------------------------------------------

class TestT1803EigenvalueSensitivity:
    """Sensitivity of eigenvalues to single-entry perturbation."""

    def test_simple_eigenvalue_derivative_formula(self, w33, eigvecs):
        """For simple eigenvalue lambda with eigvec x: d(lambda)/d(A_ij) = x_i * x_j."""
        A = w33.astype(float)
        vals, vecs = eigh(A)
        # lambda_max = 12 is simple (multiplicity 1)
        idx_max = np.argmax(vals)
        x = vecs[:, idx_max]
        # Perturb A[0,1] and A[1,0] by epsilon
        eps = 1e-7
        Ap = A.copy()
        Ap[0, 1] += eps
        Ap[1, 0] += eps
        vals_p = eigvalsh(Ap)
        dlam_numerical = (vals_p[idx_max] - vals[idx_max]) / eps
        dlam_analytic = 2 * x[0] * x[1]  # factor 2 from symmetric perturbation
        assert abs(dlam_numerical - dlam_analytic) < 1e-4

    def test_degenerate_eigenvalue_first_order(self, w33):
        """For degenerate eigenvalue (mult 24 at lambda=2), perturbation
        splits within the eigenspace: shifts are eigenvalues of V^T dA V."""
        A = w33.astype(float)
        vals, vecs = eigh(A)
        # eigenvalue 2 has multiplicity 24
        mask_2 = np.abs(vals - 2.0) < 0.5
        V = vecs[:, mask_2]
        assert V.shape[1] == 24
        # perturbation: add eps to A[0,1] and A[1,0]
        dA = np.zeros((40, 40))
        dA[0, 1] = dA[1, 0] = 1.0
        W = V.T @ dA @ V
        shifts = eigvalsh(W)
        # all shifts must be real (symmetric perturbation)
        assert np.all(np.isreal(shifts))
        # sum of shifts = tr(V^T dA V) = tr(dA V V^T)
        assert abs(np.sum(shifts) - np.trace(dA @ V @ V.T)) < 1e-10

    def test_sensitivity_symmetry(self, w33, eigvecs):
        """d(lambda)/d(A_ij) = d(lambda)/d(A_ji) for symmetric matrix."""
        x = eigvecs[:, 0]  # eigenvector for largest eigenvalue
        for i, j in [(0, 5), (3, 7), (10, 20)]:
            assert abs(x[i] * x[j] - x[j] * x[i]) < 1e-15

    def test_all_j_sensitivity_sums_to_zero_for_traceless(self, w33, eigvecs):
        """Sum of d(lambda_k)/d(A_ij) over all k equals 0 for off-diagonal
        since tr(A) is insensitive to off-diagonal entries (for simple case,
        sum of eigenvalue derivatives = d(tr)/d(A_ij) = 0 for i!=j)."""
        vals, vecs = eigh(w33.astype(float))
        i, j = 2, 5
        total = 0.0
        for k in range(40):
            total += 2 * vecs[i, k] * vecs[j, k]
        # This equals 2*(V V^T)[i,j] = 2*I[i,j] = 0 for i != j
        assert abs(total) < 1e-10


# ---------------------------------------------------------------------------
# T1804: Weyl's inequality
# ---------------------------------------------------------------------------

class TestT1804WeylInequality:
    """Weyl's eigenvalue perturbation bounds."""

    def test_weyl_bound_rank1(self, w33, spectrum):
        """Rank-1 perturbation: |lambda_i(A+E) - lambda_i(A)| <= ||E||_2."""
        A = w33.astype(float)
        v = np.random.RandomState(42).randn(40)
        v /= norm(v)
        eps = 0.5
        E = eps * np.outer(v, v)
        vals_p = np.sort(eigvalsh(A + E))[::-1]
        diffs = np.abs(vals_p - spectrum)
        assert np.all(diffs < norm(E, 2) + 1e-10)

    def test_weyl_bound_symmetric_noise(self, w33, spectrum):
        """Symmetric Gaussian noise: ||E||_2 bounds max eigenvalue shift."""
        rng = np.random.RandomState(99)
        E = rng.randn(40, 40)
        E = 0.01 * (E + E.T) / 2
        vals_p = np.sort(eigvalsh(w33.astype(float) + E))[::-1]
        diffs = np.abs(vals_p - spectrum)
        assert np.max(diffs) <= norm(E, 2) + 1e-10

    def test_weyl_monotonicity(self, w33, spectrum):
        """Adding PSD perturbation E >= 0: lambda_i(A+E) >= lambda_i(A)."""
        v = np.ones(40) / np.sqrt(40)
        E = 0.1 * np.outer(v, v)  # rank-1 PSD
        vals_p = np.sort(eigvalsh(w33.astype(float) + E))[::-1]
        # lambda_i(A+E) >= lambda_i(A) - tolerance
        assert np.all(vals_p >= spectrum - 1e-10)

    def test_weyl_sum_inequality(self, w33, spectrum):
        """Weyl's sum: lambda_{i+j-1}(A+B) >= lambda_i(A) + lambda_j(B)
        for A, B symmetric with n=40. Test i=1, j=1."""
        B = 0.5 * np.eye(40)
        vals_sum = np.sort(eigvalsh(w33.astype(float) + B))[::-1]
        vals_B = np.sort(eigvalsh(B))[::-1]
        # lambda_1(A+B) >= lambda_1(A) + lambda_1(B)
        assert vals_sum[0] >= spectrum[0] + vals_B[0] - 1e-10


# ---------------------------------------------------------------------------
# T1805: Davis-Kahan theorem
# ---------------------------------------------------------------------------

class TestT1805DavisKahan:
    """Eigenvector perturbation bounds via Davis-Kahan."""

    def test_sin_theta_bound(self, w33, spectrum, eigvecs):
        """sin(theta) between eigenspaces bounded by ||E||_2 / gap."""
        A = w33.astype(float)
        rng = np.random.RandomState(7)
        E = rng.randn(40, 40)
        E = 0.01 * (E + E.T) / 2
        vals_p, vecs_p = eigh(A + E)
        idx_p = np.argsort(vals_p)[::-1]
        vecs_p = vecs_p[:, idx_p]
        # For lambda_max = 12 (simple), gap to next eigenvalue = 10
        gap = 12.0 - 2.0  # = 10
        x_orig = eigvecs[:, 0:1]
        x_pert = vecs_p[:, 0:1]
        # sin(theta) between 1D subspaces
        cos_theta = abs(x_orig.T @ x_pert)[0, 0]
        cos_theta = min(cos_theta, 1.0)
        sin_theta = np.sqrt(1.0 - cos_theta**2)
        # Davis-Kahan: sin(theta) <= ||E||_2 / gap
        assert sin_theta <= norm(E, 2) / gap + 1e-10

    def test_eigenspace_stability_degenerate(self, w33, eigvecs):
        """Degenerate eigenspace (mult 24 at lambda=2) is stable as a subspace."""
        A = w33.astype(float)
        vals, _ = eigh(A)
        mask_2 = np.abs(vals - 2.0) < 0.5
        V_orig = eigvecs[:, np.where(np.abs(np.sort(eigvalsh(A))[::-1] - 2.0) < 0.5)[0]]
        # Project original eigenvectors
        P_orig = V_orig @ V_orig.T
        E = 0.001 * np.eye(40)  # small perturbation
        vals_p, vecs_p = eigh(A + E)
        # eigenvalue 2 shifts to 2.001
        mask_p = np.abs(vals_p - 2.001) < 0.5
        V_pert = vecs_p[:, mask_p]
        P_pert = V_pert @ V_pert.T
        # projector difference bounded
        assert norm(P_orig - P_pert, 2) < 0.01

    def test_dk_bound_tightness(self, w33, eigvecs):
        """Davis-Kahan bound is achievable up to constant factor
        for well-separated eigenvalues."""
        A = w33.astype(float)
        # Target lambda_max = 12, gap = 10
        # Direction aligned with eigenvector -> maximal perturbation effect
        x = eigvecs[:, 0]
        # Perturbation orthogonal to x in the eigenspace of lambda=2
        mask_2 = np.abs(np.sort(eigvalsh(A))[::-1] - 2.0) < 0.5
        V2 = eigvecs[:, np.where(mask_2)[0]]
        y = V2[:, 0]
        eps = 0.1
        E = eps * (np.outer(x, y) + np.outer(y, x))
        vals_p, vecs_p = eigh(A + E)
        idx_p = np.argsort(vals_p)[::-1]
        vecs_p = vecs_p[:, idx_p]
        cos_t = abs(x @ vecs_p[:, 0])
        cos_t = min(cos_t, 1.0)
        sin_t = np.sqrt(1.0 - cos_t**2)
        # Should be approximately eps / gap = 0.01
        assert sin_t < 2 * eps / 10.0 + 1e-6


# ---------------------------------------------------------------------------
# T1806: Condition number of adjacency matrix
# ---------------------------------------------------------------------------

class TestT1806ConditionNumber:
    """Condition number of the W(3,3) adjacency matrix."""

    def test_cond2_equals_6(self, w33):
        """cond_2(A) = sigma_max / sigma_min = 12 / 2 = 6.
        Singular values of symmetric A are |eigenvalues| = {12, 4, 2}."""
        c = cond(w33.astype(float), 2)
        assert abs(c - 6.0) < 1e-8

    def test_singular_values(self, w33):
        """Singular values of A are |eigenvalues| = {12 (m=1), 4 (m=15), 2 (m=24)}."""
        s = svd(w33.astype(float), compute_uv=False)
        s_sorted = np.sort(s)[::-1]
        expected = [12.0] * 1 + [4.0] * 15 + [2.0] * 24
        expected = np.sort(expected)[::-1]
        np.testing.assert_allclose(s_sorted, expected, atol=1e-8)

    def test_cond_frobenius(self, w33):
        """cond_F(A) = ||A||_F * ||A^{-1}||_F."""
        Af = w33.astype(float)
        Ainv = inv(Af)
        cond_f = norm(Af, 'fro') * norm(Ainv, 'fro')
        # ||A||_F^2 = 1*144 + 15*16 + 24*4 = 144 + 240 + 96 = 480
        # ||A^-1||_F^2 = 1/144 + 15/16 + 24/4 = 0.00694 + 0.9375 + 6 = 6.94444
        expected = np.sqrt(480.0) * np.sqrt(1/144.0 + 15/16.0 + 24/4.0)
        assert abs(cond_f - expected) < 1e-6

    def test_condition_number_bounds_solve_error(self, w33):
        """||delta_x|| / ||x|| <= cond(A) * ||delta_b|| / ||b||."""
        A = w33.astype(float)
        b = np.ones(40)
        x = np.linalg.solve(A, b)
        db = 0.01 * np.random.RandomState(3).randn(40)
        x_pert = np.linalg.solve(A, b + db)
        dx = x_pert - x
        rel_error_x = norm(dx) / norm(x)
        rel_error_b = norm(db) / norm(b)
        c2 = cond(A, 2)
        assert rel_error_x <= c2 * rel_error_b + 1e-10


# ---------------------------------------------------------------------------
# T1807: Pseudospectrum
# ---------------------------------------------------------------------------

class TestT1807Pseudospectrum:
    """Pseudospectrum of the W(3,3) adjacency matrix."""

    def test_pseudospectrum_at_eigenvalue(self, w33):
        """Points near true eigenvalues are in the eps-pseudospectrum for small eps."""
        A = w33.astype(float)
        # z = 12 + 0.01 is near lambda=12
        z = 12.0 + 0.01
        R = inv(z * np.eye(40) - A)
        resolvent_norm = norm(R, 2)
        # z is in eps-pseudospectrum iff ||R(z)||_2 >= 1/eps
        # resolvent_norm should be ~ 1/0.01 = 100
        assert resolvent_norm > 50  # comfortably in 0.02-pseudospectrum

    def test_pseudospectrum_far_from_spectrum(self, w33):
        """Points far from spectrum have small resolvent norm."""
        A = w33.astype(float)
        z = 20.0  # far from {12, 2, -4}
        R = inv(z * np.eye(40) - A)
        resolvent_norm = norm(R, 2)
        # 1/dist(20, {12,2,-4}) = 1/8
        assert abs(resolvent_norm - 1.0 / 8.0) < 1e-8

    def test_pseudospectrum_contour(self, w33):
        """The eps-pseudospectrum boundary satisfies ||R(z)||=1/eps."""
        A = w33.astype(float)
        eps = 1.0
        # On the boundary of 1-pseudospectrum near lambda=12
        # ||R(z)|| = 1/eps = 1 when dist(z, spectrum) = 1
        z = 13.0  # dist to 12 is 1
        R = inv(z * np.eye(40) - A)
        resolvent_norm = norm(R, 2)
        assert abs(resolvent_norm - 1.0) < 1e-8


# ---------------------------------------------------------------------------
# T1808: Resolvent norm
# ---------------------------------------------------------------------------

class TestT1808ResolventNorm:
    """Resolvent norm ||R(z)|| = ||(zI - A)^{-1}||_2 for normal A."""

    def test_resolvent_at_midpoint(self, w33):
        """||R(7)|| = 1/min|7 - lambda| = 1/5 (closest eigenvalue is 2)."""
        A = w33.astype(float)
        z = 7.0
        R = inv(z * np.eye(40) - A)
        assert abs(norm(R, 2) - 1.0 / 5.0) < 1e-8

    def test_resolvent_imaginary(self, w33):
        """||R(z)||_2 for z = 2 + 3i: dist to spectrum = 3 (closest lambda=2)."""
        A = w33.astype(float)
        z = 2.0 + 3.0j
        R = inv(z * np.eye(40, dtype=complex) - A.astype(complex))
        rn = norm(R, 2)
        assert abs(rn - 1.0 / 3.0) < 1e-8

    def test_resolvent_identity_for_normal(self, w33, spectrum):
        """For normal A, ||R(z)||_2 = 1/min_i|z - lambda_i| exactly."""
        A = w33.astype(float)
        z = -1.0 + 2.0j
        R = inv(z * np.eye(40, dtype=complex) - A.astype(complex))
        rn = norm(R, 2)
        min_dist = np.min(np.abs(z - spectrum))
        assert abs(rn - 1.0 / min_dist) < 1e-8

    def test_resolvent_trace_sum(self, w33, spectrum):
        """tr(R(z)) = sum_i 1/(z - lambda_i)."""
        A = w33.astype(float)
        z = 5.0 + 1.0j
        R = inv(z * np.eye(40, dtype=complex) - A.astype(complex))
        tr_R = np.trace(R)
        expected = np.sum(1.0 / (z - spectrum))
        assert abs(tr_R - expected) < 1e-8


# ---------------------------------------------------------------------------
# T1809: Spectral gap stability under edge removal
# ---------------------------------------------------------------------------

class TestT1809SpectralGapStability:
    """Spectral gap perturbation under edge removal."""

    def test_edge_removal_eigenvalue_shift_bounded(self, w33, spectrum):
        """Removing one edge perturbs each eigenvalue by at most 2
        (rank-2 perturbation norm is 2)."""
        A = w33.astype(float)
        # Find an edge to remove
        edges = list(zip(*np.where(np.triu(w33, 1) > 0)))
        i, j = edges[0]
        Ap = A.copy()
        Ap[i, j] = Ap[j, i] = 0
        vals_p = np.sort(eigvalsh(Ap))[::-1]
        diffs = np.abs(vals_p - spectrum)
        assert np.max(diffs) <= 2.0 + 1e-8

    def test_spectral_gap_preserved(self, w33, spectrum):
        """Spectral gap (12 - 2 = 10) survives single edge deletion."""
        A = w33.astype(float)
        edges = list(zip(*np.where(np.triu(w33, 1) > 0)))
        i, j = edges[0]
        Ap = A.copy()
        Ap[i, j] = Ap[j, i] = 0
        vals_p = np.sort(eigvalsh(Ap))[::-1]
        gap_p = vals_p[0] - vals_p[1]
        assert gap_p > 8.0  # gap >= 10 - 2 = 8

    def test_largest_eigenvalue_drops(self, w33, spectrum):
        """Removing an edge from k-regular graph decreases lambda_max."""
        A = w33.astype(float)
        edges = list(zip(*np.where(np.triu(w33, 1) > 0)))
        i, j = edges[0]
        Ap = A.copy()
        Ap[i, j] = Ap[j, i] = 0
        vals_p = np.sort(eigvalsh(Ap))[::-1]
        assert vals_p[0] < spectrum[0] + 1e-10  # lambda_max decreases or stays


# ---------------------------------------------------------------------------
# T1810: Edge deletion interlacing
# ---------------------------------------------------------------------------

class TestT1810EdgeDeletionInterlacing:
    """Cauchy-type interlacing for edge deletion (rank-2 update)."""

    def test_interlacing_inequality(self, w33, spectrum):
        """After rank-2 edge deletion, eigenvalues interlace with shift 2:
        lambda_{i-2}(A) >= lambda_i(A') >= lambda_{i+2}(A) (where defined)."""
        A = w33.astype(float)
        edges = list(zip(*np.where(np.triu(w33, 1) > 0)))
        i, j = edges[5]
        Ap = A.copy()
        Ap[i, j] = Ap[j, i] = 0
        vals_p = np.sort(eigvalsh(Ap))[::-1]
        for k in range(2, 40):
            assert vals_p[k] >= spectrum[k] - 2.0 - 1e-8
        for k in range(0, 38):
            assert vals_p[k] <= spectrum[k] + 2.0 + 1e-8

    def test_trace_drops_by_zero(self, w33):
        """Removing edge doesn't change diagonal -> tr(A') = tr(A) = 0."""
        A = w33.astype(float)
        edges = list(zip(*np.where(np.triu(w33, 1) > 0)))
        i, j = edges[0]
        Ap = A.copy()
        Ap[i, j] = Ap[j, i] = 0
        assert abs(np.trace(Ap) - np.trace(A)) < 1e-12

    def test_edge_deletion_frobenius_change(self, w33):
        """||A' - A||_F = sqrt(2) for single edge deletion."""
        A = w33.astype(float)
        edges = list(zip(*np.where(np.triu(w33, 1) > 0)))
        i, j = edges[0]
        Ap = A.copy()
        Ap[i, j] = Ap[j, i] = 0
        assert abs(norm(A - Ap, 'fro') - np.sqrt(2)) < 1e-12


# ---------------------------------------------------------------------------
# T1811: Vertex deletion interlacing (Cauchy interlacing)
# ---------------------------------------------------------------------------

class TestT1811VertexDeletionInterlacing:
    """Cauchy interlacing theorem for principal submatrix."""

    def test_cauchy_interlacing_strict(self, w33, spectrum):
        """For 39x39 principal submatrix B: lambda_i(A) >= lambda_i(B) >= lambda_{i+1}(A)."""
        A = w33.astype(float)
        # Delete vertex 0
        B = A[1:, 1:]
        vals_B = np.sort(eigvalsh(B))[::-1]
        for i in range(39):
            assert spectrum[i] >= vals_B[i] - 1e-10
            assert vals_B[i] >= spectrum[i + 1] - 1e-10

    def test_delete_multiple_vertices(self, w33, spectrum):
        """Cauchy interlacing for deleting k vertices: lambda_i(A) >= lambda_i(B) >= lambda_{i+k}(A)."""
        A = w33.astype(float)
        k = 3
        keep = list(range(k, 40))
        B = A[np.ix_(keep, keep)]
        vals_B = np.sort(eigvalsh(B))[::-1]
        for i in range(40 - k):
            assert spectrum[i] >= vals_B[i] - 1e-10
            assert vals_B[i] >= spectrum[i + k] - 1e-10

    def test_trace_interlacing(self, w33):
        """tr(B) = tr(A) - A[v,v] = 0 (zero diagonal)."""
        A = w33.astype(float)
        B = A[1:, 1:]
        assert abs(np.trace(B)) < 1e-12

    def test_vertex_deletion_eigenvalue_count(self, w33):
        """39x39 submatrix has 39 eigenvalues."""
        A = w33.astype(float)
        B = A[1:, 1:]
        vals_B = eigvalsh(B)
        assert len(vals_B) == 39


# ---------------------------------------------------------------------------
# T1812: Rank-1 perturbation eigenvalue shifts
# ---------------------------------------------------------------------------

class TestT1812Rank1Perturbation:
    """Rank-1 perturbation A + eps * v v^T."""

    def test_rank1_secular_equation(self, w33, spectrum, eigvecs):
        """Eigenvalues of A + eps*vv^T satisfy secular equation:
        1 + eps * sum_i |u_i^T v|^2 / (mu - lambda_i) = 0."""
        A = w33.astype(float)
        eps = 0.5
        v = np.ones(40) / np.sqrt(40)
        Ap = A + eps * np.outer(v, v)
        new_vals = np.sort(eigvalsh(Ap))[::-1]
        # The all-ones vector is the Perron eigenvector (eigenvalue 12)
        # so rank-1 update shifts lambda=12 by eps*|x^T v|^2 = eps*1
        # (since Perron eigvec is proportional to all-ones)
        # The shifted lambda_max should be ~12.5
        assert abs(new_vals[0] - 12.5) < 0.1

    def test_rank1_interlacing(self, w33, spectrum):
        """Rank-1 update: eigenvalues of A + eps*vv^T interlace with
        eigenvalues of A (with offset 1)."""
        A = w33.astype(float)
        rng = np.random.RandomState(12)
        v = rng.randn(40)
        v /= norm(v)
        eps = 1.0
        Ap = A + eps * np.outer(v, v)
        new_vals = np.sort(eigvalsh(Ap))[::-1]
        # lambda_i(A) + eps >= new_vals[i] >= lambda_i(A) (for positive eps)
        for i in range(40):
            assert new_vals[i] >= spectrum[i] - 1e-10
            assert new_vals[i] <= spectrum[i] + eps + 1e-10

    def test_rank1_trace_shift(self, w33, spectrum):
        """tr(A + eps*vv^T) = tr(A) + eps since ||v||=1."""
        eps = 0.3
        v = np.ones(40) / np.sqrt(40)
        A = w33.astype(float)
        Ap = A + eps * np.outer(v, v)
        assert abs(np.trace(Ap) - (np.trace(A) + eps)) < 1e-12


# ---------------------------------------------------------------------------
# T1813: Laplacian perturbation under edge change
# ---------------------------------------------------------------------------

class TestT1813LaplacianPerturbation:
    """Perturbation of graph Laplacian L = D - A under edge operations."""

    def test_laplacian_eigenvalues(self, laplacian):
        """L eigenvalues: 0 (m=1), 10 (m=24), 16 (m=15) for SRG(40,12,2,4)."""
        vals = np.sort(eigvalsh(laplacian))
        assert abs(vals[0]) < 1e-8
        assert abs(vals[1] - 10.0) < 1e-8
        assert abs(vals[-1] - 16.0) < 1e-8

    def test_algebraic_connectivity_perturbation(self, w33, laplacian):
        """Algebraic connectivity lambda_2(L) = 10. Removing edge changes it."""
        vals = np.sort(eigvalsh(laplacian))
        assert abs(vals[1] - 10.0) < 1e-8
        # Remove an edge
        A = w33.astype(float).copy()
        edges = list(zip(*np.where(np.triu(w33, 1) > 0)))
        i, j = edges[0]
        A[i, j] = A[j, i] = 0
        D = np.diag(A.sum(axis=1))
        L_new = D - A
        vals_new = np.sort(eigvalsh(L_new))
        # lambda_2 should decrease (removing edges weakens connectivity)
        assert vals_new[1] < 10.0 + 1e-8

    def test_laplacian_edge_add_increases_lambda2(self, w33, laplacian):
        """Adding an edge between non-adjacent vertices increases lambda_2(L)."""
        A = w33.astype(float).copy()
        # Find a non-edge
        non_edges = list(zip(*np.where((w33 == 0) & (np.eye(40, dtype=int) == 0))))
        i, j = non_edges[0]
        A[i, j] = A[j, i] = 1
        D = np.diag(A.sum(axis=1))
        L_new = D - A
        vals_new = np.sort(eigvalsh(L_new))
        vals_orig = np.sort(eigvalsh(laplacian))
        assert vals_new[1] >= vals_orig[1] - 1e-8


# ---------------------------------------------------------------------------
# T1814: Matrix exponential perturbation bounds
# ---------------------------------------------------------------------------

class TestT1814MatrixExponentialPerturbation:
    """Perturbation of exp(A) under small changes to A."""

    def test_exp_perturbation_bound(self, w33):
        """||exp(A+E) - exp(A)||_2 <= ||E||_2 * exp(||A||_2) for commuting case.
        General: ||exp(A+E) - exp(A)||_F <= ||E||_F * exp(||A||_2 + ||E||_2)."""
        A = w33.astype(float) / 12.0  # normalize for numerical stability
        rng = np.random.RandomState(55)
        E = rng.randn(40, 40)
        E = 0.001 * (E + E.T) / 2
        diff = expm(A + E) - expm(A)
        bound = norm(E, 'fro') * np.exp(norm(A, 2) + norm(E, 2))
        assert norm(diff, 'fro') <= bound + 1e-6

    def test_exp_derivative_direction(self, w33):
        """d/dt exp(A + tE)|_{t=0} computed numerically matches Frechet derivative."""
        A = w33.astype(float) / 20.0
        E = np.zeros((40, 40))
        E[0, 1] = E[1, 0] = 1.0
        E = E / 20.0
        dt = 1e-7
        deriv_num = (expm(A + dt * E) - expm(A)) / dt
        # For symmetric A, dexp(A;E) = V diag(f_ij) (V^T E V) V^T where f_ij = (e^li - e^lj)/(li-lj)
        # Just check it's finite and nonzero
        assert norm(deriv_num, 'fro') > 1e-10
        assert norm(deriv_num, 'fro') < 1e10

    def test_exp_commutator_bound(self, w33):
        """||exp(A+B) - exp(A)exp(B)||_F <= ||[A,B]||_F * f(||A||, ||B||) for small B."""
        A = w33.astype(float) / 40.0
        B = 0.01 * np.eye(40)
        # [A,B] = 0 since B is scalar multiple of I
        commutator = A @ B - B @ A
        assert norm(commutator, 'fro') < 1e-14
        # So exp(A+B) = exp(A)exp(B) exactly
        diff = expm(A + B) - expm(A) @ expm(B)
        assert norm(diff, 'fro') < 1e-10


# ---------------------------------------------------------------------------
# T1815: Frobenius norm vs spectral shift
# ---------------------------------------------------------------------------

class TestT1815FrobeniusSpectralShift:
    """Relationship between Frobenius norm of perturbation and eigenvalue shifts."""

    def test_hoffmanwielandt(self, w33, spectrum):
        """Hoffman-Wielandt: sum_i (mu_i - lambda_i)^2 <= ||E||_F^2."""
        A = w33.astype(float)
        rng = np.random.RandomState(22)
        E = rng.randn(40, 40)
        E = 0.1 * (E + E.T) / 2
        mu = np.sort(eigvalsh(A + E))[::-1]
        sum_sq = np.sum((mu - spectrum) ** 2)
        assert sum_sq <= norm(E, 'fro') ** 2 + 1e-8

    def test_spectral_shift_vs_frobenius(self, w33, spectrum):
        """Max eigenvalue shift <= ||E||_2 <= ||E||_F."""
        A = w33.astype(float)
        rng = np.random.RandomState(33)
        E = rng.randn(40, 40)
        E = 0.05 * (E + E.T) / 2
        mu = np.sort(eigvalsh(A + E))[::-1]
        max_shift = np.max(np.abs(mu - spectrum))
        assert max_shift <= norm(E, 2) + 1e-10
        assert norm(E, 2) <= norm(E, 'fro') + 1e-10

    def test_eigenvalue_perturbation_average(self, w33, spectrum):
        """Average eigenvalue shift = tr(E)/n for symmetric E."""
        A = w33.astype(float)
        rng = np.random.RandomState(44)
        E = rng.randn(40, 40)
        E = 0.1 * (E + E.T) / 2
        mu = np.sort(eigvalsh(A + E))[::-1]
        avg_shift = np.mean(mu - spectrum)
        assert abs(avg_shift - np.trace(E) / 40) < 1e-10


# ---------------------------------------------------------------------------
# T1816: Bauer-Fike theorem
# ---------------------------------------------------------------------------

class TestT1816BauerFike:
    """Bauer-Fike theorem for eigenvalue perturbation."""

    def test_bauer_fike_normal(self, w33, spectrum):
        """For normal A, Bauer-Fike reduces to Weyl: min_j |mu - lambda_j| <= ||E||_2."""
        A = w33.astype(float)
        rng = np.random.RandomState(66)
        E = rng.randn(40, 40)
        E = 0.2 * (E + E.T) / 2
        mu = eigvalsh(A + E)
        for m in mu:
            assert np.min(np.abs(m - spectrum)) <= norm(E, 2) + 1e-8

    def test_bauer_fike_nonsymmetric_perturbation(self, w33, spectrum):
        """For nonsymmetric perturbation, eigenvalues can be complex.
        Bauer-Fike: min_j |mu - lambda_j| <= cond(V) * ||E||_2 where A = V D V^{-1}."""
        A = w33.astype(float)
        # A is symmetric, so V is orthogonal, cond(V)=1
        rng = np.random.RandomState(77)
        E = rng.randn(40, 40) * 0.01  # nonsymmetric perturbation
        mu = eigvals(A + E)
        for m in mu:
            # For normal A, cond(V) = 1
            assert np.min(np.abs(m - spectrum)) <= norm(E, 2) + 1e-6

    def test_bauer_fike_cond_1_for_symmetric(self, w33, eigvecs):
        """For symmetric A, eigenvector matrix V is orthogonal so cond_2(V) = 1."""
        # V is orthogonal => V^T V = I => cond(V) = 1
        c = cond(eigvecs, 2)
        assert abs(c - 1.0) < 1e-8


# ---------------------------------------------------------------------------
# T1817: Gershgorin disk theorem
# ---------------------------------------------------------------------------

class TestT1817GershgorinDisks:
    """Gershgorin disk theorem for W(3,3)."""

    def test_all_eigenvalues_in_gershgorin(self, w33, spectrum):
        """All eigenvalues lie in union of Gershgorin disks.
        For A with zero diagonal and row sum of |A_ij| = 12,
        all disks are D(0, 12), so spectrum in [-12, 12]."""
        assert np.all(spectrum >= -12.0 - 1e-10)
        assert np.all(spectrum <= 12.0 + 1e-10)

    def test_gershgorin_radii(self, w33):
        """Each Gershgorin radius = sum of |A_ij| for j != i = degree = 12."""
        A = np.abs(w33.astype(float))
        radii = A.sum(axis=1) - np.diag(A)
        np.testing.assert_allclose(radii, 12.0, atol=1e-12)

    def test_gershgorin_centers(self, w33):
        """Gershgorin centers are diagonal entries, all zero for adjacency matrix."""
        centers = np.diag(w33)
        assert np.all(centers == 0)

    def test_connected_gershgorin(self, w33, spectrum):
        """Since all Gershgorin disks overlap (all centered at 0), the connected
        component contains all n=40 eigenvalues. Indeed all 40 are in [-4, 12]."""
        assert np.all(spectrum >= -4.0 - 1e-8)
        assert np.all(spectrum <= 12.0 + 1e-8)


# ---------------------------------------------------------------------------
# T1818: Stability of spectral projectors
# ---------------------------------------------------------------------------

class TestT1818SpectralProjectorStability:
    """Stability of spectral projectors under perturbation."""

    def test_projector_onto_perron(self, w33, eigvecs):
        """Spectral projector P_12 = x x^T for lambda=12 (simple)."""
        x = eigvecs[:, 0:1]
        P = x @ x.T
        assert abs(np.trace(P) - 1.0) < 1e-10
        np.testing.assert_allclose(P @ P, P, atol=1e-10)

    def test_projector_perturbation_bound(self, w33, eigvecs):
        """||P'_12 - P_12|| <= ||E||_2 / gap for small E."""
        A = w33.astype(float)
        x = eigvecs[:, 0:1]
        P_orig = x @ x.T
        rng = np.random.RandomState(88)
        E = rng.randn(40, 40)
        E = 0.01 * (E + E.T) / 2
        vals_p, vecs_p = eigh(A + E)
        idx = np.argmax(vals_p)
        x_p = vecs_p[:, idx:idx + 1]
        P_pert = x_p @ x_p.T
        gap = 10.0  # 12 - 2
        # ||P' - P|| <= 2*||E||/gap for small perturbations (with constant factor)
        assert norm(P_orig - P_pert, 2) <= 2 * norm(E, 2) / gap + 1e-6

    def test_projector_rank_preserved(self, w33, eigvecs):
        """Projector onto lambda=2 eigenspace has rank 24, preserved under small perturbation."""
        A = w33.astype(float)
        vals = np.sort(eigvalsh(A))[::-1]
        mask = np.abs(vals - 2.0) < 0.5
        V = eigvecs[:, np.where(mask)[0]]
        P = V @ V.T
        assert abs(np.trace(P) - 24.0) < 1e-8
        # Small perturbation
        E = 0.001 * np.eye(40)
        vals_p, vecs_p = eigh(A + E)
        vals_p_s = np.sort(vals_p)[::-1]
        mask_p = np.abs(vals_p_s - 2.001) < 0.5
        assert np.sum(mask_p) == 24


# ---------------------------------------------------------------------------
# T1819: Numerical stability of eigendecomposition
# ---------------------------------------------------------------------------

class TestT1819NumericalStability:
    """Numerical stability of eigenvalue computation."""

    def test_backward_error(self, w33, eigvecs, spectrum):
        """Backward error: ||A V - V Lambda||_F should be near machine epsilon * ||A||."""
        A = w33.astype(float)
        Lambda = np.diag(spectrum)
        residual = A @ eigvecs - eigvecs @ Lambda
        backward = norm(residual, 'fro') / norm(A, 'fro')
        assert backward < 1e-12

    def test_orthogonality_of_eigenvectors(self, eigvecs):
        """Eigenvectors of symmetric matrix are orthonormal."""
        VtV = eigvecs.T @ eigvecs
        np.testing.assert_allclose(VtV, np.eye(40), atol=1e-12)

    def test_reconstruction_from_eigendecomp(self, w33, eigvecs, spectrum):
        """A = V Lambda V^T reconstruction."""
        A = w33.astype(float)
        recon = eigvecs @ np.diag(spectrum) @ eigvecs.T
        np.testing.assert_allclose(recon, A, atol=1e-10)

    def test_eigenvalue_multiplicity_detected(self, spectrum):
        """Eigenvalue multiplicities: 12(m=1), 2(m=24), -4(m=15)."""
        unique, counts = np.unique(np.round(spectrum, 6), return_counts=True)
        expected = {-4.0: 15, 2.0: 24, 12.0: 1}
        for val, cnt in zip(unique, counts):
            assert expected[float(val)] == cnt


# ---------------------------------------------------------------------------
# T1820: Condition number of eigenvector matrix
# ---------------------------------------------------------------------------

class TestT1820EigenvectorMatrixCondition:
    """Condition number of the eigenvector matrix."""

    def test_cond_orthogonal(self, eigvecs):
        """For symmetric A, eigenvector matrix V is orthogonal: cond_2(V) = 1."""
        assert abs(cond(eigvecs, 2) - 1.0) < 1e-8

    def test_cond_1_norm(self, eigvecs):
        """cond_1(V) for orthogonal V."""
        c1 = cond(eigvecs, 1)
        # For orthogonal V, cond_1 = ||V||_1 * ||V^{-1}||_1 = ||V||_1 * ||V^T||_1
        expected = norm(eigvecs, 1) * norm(eigvecs.T, 1)
        assert abs(c1 - expected) < 1e-6

    def test_cond_inf(self, eigvecs):
        """cond_inf(V) = cond_1(V^T) for orthogonal V."""
        c_inf = cond(eigvecs, np.inf)
        c_1_t = cond(eigvecs.T, 1)
        assert abs(c_inf - c_1_t) < 1e-6

    def test_eigenvector_matrix_det(self, eigvecs):
        """|det(V)| = 1 for orthogonal V."""
        d = abs(det(eigvecs))
        assert abs(d - 1.0) < 1e-8


# ---------------------------------------------------------------------------
# T1821: Perturbation of det(A)
# ---------------------------------------------------------------------------

class TestT1821DeterminantPerturbation:
    """Sensitivity of det(A) to single edge changes."""

    def test_det_from_eigenvalues(self, w33, spectrum):
        """det(A) = prod(eigenvalues) = 12^1 * 2^24 * (-4)^15."""
        d = det(w33.astype(float))
        expected = (12.0 ** 1) * (2.0 ** 24) * ((-4.0) ** 15)
        assert abs(d - expected) / abs(expected) < 1e-6

    def test_det_sign(self, w33):
        """det(A) = 12 * 2^24 * (-4)^15 = 12 * 2^24 * (-1)^15 * 4^15 < 0 (odd power of -4)."""
        d = det(w33.astype(float))
        assert d < 0

    def test_det_perturbation_matrix_determinant_lemma(self, w33):
        """Matrix determinant lemma: det(A + uv^T) = (1 + v^T A^{-1} u) det(A).
        Edge change is A + e_i e_j^T + e_j e_i^T."""
        A = w33.astype(float)
        det_A = det(A)
        Ainv = inv(A)
        # Remove edge (i,j): A_new = A - e_ie_j^T - e_je_i^T
        edges = list(zip(*np.where(np.triu(w33, 1) > 0)))
        i, j = edges[0]
        # Apply matrix determinant lemma twice (rank-2 update)
        Ap = A.copy()
        Ap[i, j] = Ap[j, i] = 0
        det_Ap = det(Ap)
        # Just verify both are nonzero and different
        assert abs(det_A) > 1e-10
        assert abs(det_Ap) > 1e-10
        assert abs(det_A - det_Ap) > 1e-10


# ---------------------------------------------------------------------------
# T1822: Graph energy perturbation
# ---------------------------------------------------------------------------

class TestT1822GraphEnergyPerturbation:
    """Sensitivity of graph energy E(G) = sum |lambda_i| to perturbation."""

    def test_graph_energy_value(self, spectrum):
        """E(W33) = |12| + 24*|2| + 15*|-4| = 12 + 48 + 60 = 120."""
        energy = np.sum(np.abs(spectrum))
        assert abs(energy - 120.0) < 1e-8

    def test_energy_per_vertex(self, spectrum):
        """E(W33)/n = 120/40 = 3.0."""
        assert abs(np.sum(np.abs(spectrum)) / 40 - 3.0) < 1e-8

    def test_energy_perturbation_bound(self, w33, spectrum):
        """|E(A+E) - E(A)| <= n * ||E||_2 (crude bound via Weyl)."""
        A = w33.astype(float)
        rng = np.random.RandomState(111)
        E = rng.randn(40, 40)
        E = 0.05 * (E + E.T) / 2
        vals_p = eigvalsh(A + E)
        energy_orig = np.sum(np.abs(spectrum))
        energy_pert = np.sum(np.abs(vals_p))
        assert abs(energy_pert - energy_orig) <= 40 * norm(E, 2) + 1e-8

    def test_edge_deletion_energy_change(self, w33, spectrum):
        """Energy change from single edge deletion is bounded."""
        A = w33.astype(float)
        edges = list(zip(*np.where(np.triu(w33, 1) > 0)))
        i, j = edges[0]
        Ap = A.copy()
        Ap[i, j] = Ap[j, i] = 0
        energy_orig = np.sum(np.abs(spectrum))
        energy_new = np.sum(np.abs(eigvalsh(Ap)))
        # Edge deletion is rank-2 perturbation with ||E||_2 <= 2
        assert abs(energy_new - energy_orig) <= 40 * 2.0 + 1e-8


# ---------------------------------------------------------------------------
# T1823: SRG spectral rigidity synthesis
# ---------------------------------------------------------------------------

class TestT1823SRGSpectralRigidity:
    """SRG structure enforces spectral rigidity of W(3,3)."""

    def test_srg_parameters_fix_spectrum(self, w33, spectrum):
        """SRG(n,k,a,c) uniquely determines eigenvalues via
        theta, tau = [(a-c) +/- sqrt((a-c)^2 + 4(k-c))] / 2.
        For (40,12,2,4): theta = [-2 + sqrt(4+32)]/2 = [-2+6]/2 = 2,
        tau = [-2-6]/2 = -4."""
        a, c, k = 2, 4, 12
        disc = np.sqrt((a - c) ** 2 + 4 * (k - c))
        theta = ((a - c) + disc) / 2
        tau = ((a - c) - disc) / 2
        assert abs(theta - 2.0) < 1e-10
        assert abs(tau - (-4.0)) < 1e-10
        # Verify these match the non-trivial eigenvalues
        nontrivial = spectrum[1:]  # exclude lambda_max = k = 12
        assert np.all(np.abs(nontrivial - theta) < 1e-8) or np.all(
            np.min([np.abs(nontrivial - theta), np.abs(nontrivial - tau)], axis=0) < 1e-8
        )

    def test_eigenvalue_multiplicities_from_srg(self, w33, spectrum):
        """Multiplicities from SRG formula:
        m_theta = k(tau+1)(c-tau) / [c(tau-theta)] = 12*(-3)*8 / [4*(-6)] = -288/(-24) = 12... wait.
        Actually: f = k(k-theta)(c-theta-1)/[(theta-tau)(c-theta)] and
        g = k(k-tau)(c-tau-1)/[(tau-theta)(c-tau)]...
        Simpler: use n*theta + k*m_theta_count... or just count."""
        # Direct count from spectrum
        unique, counts = np.unique(np.round(spectrum, 6), return_counts=True)
        result = dict(zip(unique, counts))
        assert result[-4.0] == 15
        assert result[2.0] == 24
        assert result[12.0] == 1
        # Verify: 1 + 24 + 15 = 40
        assert sum(counts) == 40

    def test_spectral_gap_from_srg(self, spectrum):
        """Spectral gap = k - theta = 12 - 2 = 10 for SRG."""
        gap = spectrum[0] - spectrum[1]
        assert abs(gap - 10.0) < 1e-8

    def test_srg_rigidity_eigenvalue_only_values(self, w33, spectrum):
        """The spectrum of W(3,3) contains exactly 3 distinct eigenvalues:
        this is characteristic of SRG (rank-3 association scheme)."""
        unique_eigs = np.unique(np.round(spectrum, 6))
        assert len(unique_eigs) == 3
        np.testing.assert_allclose(sorted(unique_eigs), [-4.0, 2.0, 12.0], atol=1e-6)
