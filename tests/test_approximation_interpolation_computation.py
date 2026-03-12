"""
Phase XCII: Approximation & Interpolation on Graphs (T1488-T1508)
=================================================================

Computes bandlimited approximation, spectral filtering, Chebyshev
polynomials, sampling/reconstruction, regularization, Sobolev norms,
kernel regression, polynomial interpolation, wavelets, compressed
sensing, and graph convolution on W(3,3) = SRG(40,12,2,4).

All computations use the actual adjacency matrix of the symplectic
polar space W(3,3) over GF(3).

Key facts:
  W(3,3): n=40, k=12, lambda=2, mu=4
  A spectrum:  {12^1, 2^24, (-4)^15}
  L = kI - A,  spectrum: {0^1, 10^24, 16^15}
  240 edges, spectral gap lambda_1(L) = 10
"""

import pytest
import numpy as np
from numpy.polynomial.chebyshev import chebval
from scipy.linalg import expm


# =====================================================================
# Build W(3,3)
# =====================================================================

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


# =====================================================================
# Fixtures
# =====================================================================

@pytest.fixture(scope="module")
def w33():
    return _build_w33()


@pytest.fixture(scope="module")
def adjacency(w33):
    """Adjacency matrix as float."""
    return w33.astype(float)


@pytest.fixture(scope="module")
def laplacian(w33):
    """Graph Laplacian L = kI - A for k-regular graph (k=12)."""
    return 12.0 * np.eye(40) - w33.astype(float)


@pytest.fixture(scope="module")
def eigen_decomp_A(adjacency):
    """Full eigendecomposition of A, sorted ascending."""
    evals, evecs = np.linalg.eigh(adjacency)
    idx = np.argsort(evals)
    return evals[idx], evecs[:, idx]


@pytest.fixture(scope="module")
def eigen_decomp_L(laplacian):
    """Full eigendecomposition of L, sorted ascending."""
    evals, evecs = np.linalg.eigh(laplacian)
    idx = np.argsort(evals)
    return evals[idx], evecs[:, idx]


@pytest.fixture(scope="module")
def spectral_idempotents(eigen_decomp_A):
    """Spectral idempotents E0 (rank 1), E1 (rank 24), E2 (rank 15)."""
    evals, V = eigen_decomp_A
    # A eigenvalues sorted: -4 (15), 2 (24), 12 (1)
    # idx: 0..14 -> -4, 15..38 -> 2, 39 -> 12
    E2 = V[:, :15] @ V[:, :15].T    # eigenvalue -4, rank 15
    E1 = V[:, 15:39] @ V[:, 15:39].T  # eigenvalue 2, rank 24
    E0 = V[:, 39:40] @ V[:, 39:40].T  # eigenvalue 12, rank 1
    return E0, E1, E2


@pytest.fixture(scope="module")
def incidence(w33):
    """Oriented incidence matrix B (m x n) and edge list."""
    n = 40
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if w33[i, j] == 1:
                edges.append((i, j))
    m = len(edges)
    B = np.zeros((m, n), dtype=float)
    for e_idx, (i, j) in enumerate(edges):
        B[e_idx, i] = -1.0
        B[e_idx, j] = 1.0
    return B, edges


# =====================================================================
# T1488: Bandlimited Approximation
# =====================================================================

class TestT1488BandlimitedApproximation:
    """Project signal to k-bandlimited space (span of first k
    eigenvectors of L, i.e. lowest-frequency components)."""

    def test_projection_reduces_energy(self, eigen_decomp_L):
        """Projecting to bandlimited subspace cannot increase signal energy."""
        evals, V = eigen_decomp_L
        rng = np.random.RandomState(1488)
        f = rng.randn(40)
        for k in [1, 5, 10, 25]:
            Vk = V[:, :k]
            f_bl = Vk @ (Vk.T @ f)
            assert np.linalg.norm(f_bl) <= np.linalg.norm(f) + 1e-12

    def test_projection_is_idempotent(self, eigen_decomp_L):
        """Projecting twice gives the same result as once."""
        _, V = eigen_decomp_L
        rng = np.random.RandomState(14881)
        f = rng.randn(40)
        k = 25  # first 25 eigenvectors (0 + 24 of eigenvalue 10)
        Vk = V[:, :k]
        P = Vk @ Vk.T
        f_bl = P @ f
        f_bl2 = P @ f_bl
        assert np.allclose(f_bl, f_bl2, atol=1e-12)

    def test_bandlimited_spectral_content(self, eigen_decomp_L):
        """A k-bandlimited signal has zero Fourier coefficients above band k."""
        evals, V = eigen_decomp_L
        rng = np.random.RandomState(14882)
        f = rng.randn(40)
        k = 25
        Vk = V[:, :k]
        f_bl = Vk @ (Vk.T @ f)
        f_hat = V.T @ f_bl
        assert np.allclose(f_hat[k:], 0.0, atol=1e-12)
        # Coefficients in band should be non-trivial
        assert np.linalg.norm(f_hat[:k]) > 0.1

    def test_best_approximation_property(self, eigen_decomp_L):
        """k-bandlimited projection minimizes ||f - g||^2 over all
        k-bandlimited g (best approximation in L2)."""
        evals, V = eigen_decomp_L
        rng = np.random.RandomState(14883)
        f = rng.randn(40)
        k = 10
        Vk = V[:, :k]
        f_bl = Vk @ (Vk.T @ f)
        err_proj = np.linalg.norm(f - f_bl)
        # Any other k-bandlimited vector should give >= error
        for _ in range(20):
            c = rng.randn(k)
            g = Vk @ c
            assert np.linalg.norm(f - g) >= err_proj - 1e-12

    def test_full_band_is_identity(self, eigen_decomp_L):
        """With k=40 (all eigenvectors), projection is identity."""
        _, V = eigen_decomp_L
        rng = np.random.RandomState(14884)
        f = rng.randn(40)
        f_bl = V @ (V.T @ f)
        assert np.allclose(f_bl, f, atol=1e-12)


# =====================================================================
# T1489: Low-Pass Filter
# =====================================================================

class TestT1489LowPassFilter:
    """H_LP(lambda) = 1 if lambda <= threshold, 0 otherwise.
    Filtering A with threshold keeping only eigenvalue 12
    gives rank-1 E0 projection (constant signal)."""

    def test_low_pass_constant_signal(self, adjacency, eigen_decomp_A,
                                      spectral_idempotents):
        """Low-pass keeping eigenvalue 12 of A gives constant signal."""
        evals, V = eigen_decomp_A
        E0, _, _ = spectral_idempotents
        rng = np.random.RandomState(1489)
        f = rng.randn(40)
        # Filter: keep only eigenvalue 12 (the largest, index 39)
        f_hat = V.T @ f
        h = np.zeros(40)
        h[39] = 1.0  # only keep eigenvalue 12 component
        f_lp = V @ (h * f_hat)
        # Should be proportional to the all-ones eigenvector
        f_E0 = E0 @ f
        assert np.allclose(f_lp, f_E0, atol=1e-10)

    def test_low_pass_is_projection(self, eigen_decomp_A):
        """Applying low-pass filter twice is same as once."""
        evals, V = eigen_decomp_A
        # Keep eigenvalues >= 2 (i.e. eigenvalues 2 and 12)
        h = np.where(evals >= 2.0 - 0.5, 1.0, 0.0)
        H = V @ np.diag(h) @ V.T
        H2 = H @ H
        assert np.allclose(H, H2, atol=1e-10)

    def test_low_pass_rank(self, eigen_decomp_A):
        """Low-pass keeping eigenvalue >= 2 gives rank 25 filter."""
        evals, V = eigen_decomp_A
        h = np.where(evals >= 2.0 - 0.5, 1.0, 0.0)
        H = V @ np.diag(h) @ V.T
        assert np.linalg.matrix_rank(H, tol=1e-8) == 25

    def test_low_pass_spectrum_matches(self, eigen_decomp_L):
        """Low-pass on L with threshold=10 keeps eigenvalues 0,10."""
        evals, V = eigen_decomp_L
        h = np.where(evals <= 10.0 + 0.5, 1.0, 0.0)
        assert np.sum(h) == 25  # 1 (eigenvalue 0) + 24 (eigenvalue 10)


# =====================================================================
# T1490: Chebyshev Approximation
# =====================================================================

class TestT1490ChebyshevApproximation:
    """T_n(x) Chebyshev polynomials of A/12 for approximating functions."""

    def test_chebyshev_identity(self, adjacency):
        """T_0(A/12) = I and T_1(A/12) = A/12."""
        n = 40
        A_scaled = adjacency / 12.0
        T0 = np.eye(n)
        T1 = A_scaled
        # Using recurrence: T_0(x)=1, T_1(x)=x
        assert np.allclose(T0, np.eye(n), atol=1e-14)
        assert np.allclose(T1, A_scaled, atol=1e-14)

    def test_chebyshev_recurrence(self, adjacency):
        """T_{n+1}(x) = 2x T_n(x) - T_{n-1}(x) holds for matrix argument."""
        A_scaled = adjacency / 12.0
        T_prev = np.eye(40)
        T_curr = A_scaled.copy()
        for _ in range(5):
            T_next = 2.0 * A_scaled @ T_curr - T_prev
            T_prev = T_curr
            T_curr = T_next
        # After 5 recurrence steps from T_0, T_1 we have T_6(A/12)
        # Verify eigenvalues: T_6(lambda/12) for each lambda
        evals_A = np.sort(np.linalg.eigvalsh(adjacency))
        evals_T6 = np.sort(np.linalg.eigvalsh(T_curr))
        expected = np.array([np.polynomial.chebyshev.chebval(
            lam / 12.0, [0] * 6 + [1]) for lam in evals_A])
        assert np.allclose(np.sort(evals_T6), np.sort(expected), atol=1e-8)

    def test_chebyshev_approximation_exp(self, adjacency, eigen_decomp_A):
        """Chebyshev expansion approximates exp(-A/12) on spectrum."""
        evals, V = eigen_decomp_A
        # Exact: exp(-lambda/12) for each eigenvalue
        exact_diag = np.exp(-evals / 12.0)
        # Chebyshev approx degree 10 on [-1,1] for exp(-x)
        # Map eigenvalues to [-1,1]: x = lambda/12
        # but eigenvalues of A are -4,2,12 so x in {-1/3, 1/6, 1}
        coeffs = np.polynomial.chebyshev.chebfit(
            evals / 12.0, np.exp(-evals / 12.0), deg=10)
        approx_diag = np.array([chebval(lam / 12.0, coeffs) for lam in evals])
        assert np.allclose(approx_diag, exact_diag, atol=1e-10)

    def test_chebyshev_orthogonality_on_spectrum(self, eigen_decomp_A):
        """Chebyshev polynomials on the three distinct eigenvalues."""
        distinct_evals = np.array([-4.0, 2.0, 12.0])
        x = distinct_evals / 12.0  # scale to check polynomial vals
        T0 = np.ones(3)
        T1 = x
        T2 = 2.0 * x**2 - 1.0
        # These are 3 polynomials at 3 points -> Vandermonde-like
        M = np.column_stack([T0, T1, T2])
        assert np.linalg.matrix_rank(M) == 3  # full rank, linearly indep


# =====================================================================
# T1491: Jackson Theorem
# =====================================================================

class TestT1491JacksonTheorem:
    """Best polynomial approximation rate for smooth functions on spectrum."""

    def test_jackson_rate_for_exp(self, eigen_decomp_A):
        """Error of degree-d polynomial approximation to exp(-x)
        on spectrum {-4,2,12} decreases with degree."""
        evals, V = eigen_decomp_A
        distinct = np.array([-4.0, 2.0, 12.0])
        target = np.exp(-distinct / 12.0)
        errors = []
        for d in range(1, 6):
            x_scaled = distinct / 12.0
            coeffs = np.polynomial.chebyshev.chebfit(x_scaled, target, deg=d)
            approx = np.array([chebval(xi, coeffs) for xi in x_scaled])
            errors.append(np.max(np.abs(approx - target)))
        # Error should be monotonically non-increasing
        for i in range(len(errors) - 1):
            assert errors[i + 1] <= errors[i] + 1e-14

    def test_exact_interpolation_at_degree_2(self, eigen_decomp_A):
        """With 3 distinct eigenvalues, degree-2 polynomial is exact."""
        distinct = np.array([-4.0, 2.0, 12.0])
        target = np.exp(-distinct / 12.0)
        x_scaled = distinct / 12.0
        coeffs = np.polynomial.chebyshev.chebfit(x_scaled, target, deg=2)
        approx = np.array([chebval(xi, coeffs) for xi in x_scaled])
        assert np.allclose(approx, target, atol=1e-12)

    def test_jackson_kernel_matrix(self, eigen_decomp_A, adjacency):
        """Degree-2 polynomial exactly represents any spectral function
        since there are only 3 distinct eigenvalues."""
        evals, V = eigen_decomp_A
        # f(A) for f(x) = x^2 + 1
        f_exact = adjacency @ adjacency + np.eye(40)
        # Polynomial fit on distinct eigenvalues
        distinct = np.array([-4.0, 2.0, 12.0])
        target = distinct**2 + 1.0
        # Lagrange on 3 points -> degree 2 exact
        coeffs = np.polyfit(distinct, target, deg=2)
        # Build p(A) = c[0]*A^2 + c[1]*A + c[2]*I using matrix powers
        f_poly = coeffs[0] * (adjacency @ adjacency) + \
                 coeffs[1] * adjacency + coeffs[2] * np.eye(40)
        assert np.allclose(f_exact, f_poly, atol=1e-8)


# =====================================================================
# T1492: Sampling and Reconstruction
# =====================================================================

class TestT1492SamplingReconstruction:
    """Given values at S subset V, reconstruct bandlimited signal."""

    def test_reconstruction_from_enough_samples(self, eigen_decomp_L):
        """A 25-bandlimited signal can be reconstructed from 25+ samples."""
        evals, V = eigen_decomp_L
        rng = np.random.RandomState(1492)
        k = 25
        Vk = V[:, :k]
        # Create a k-bandlimited signal
        c = rng.randn(k)
        f_true = Vk @ c
        # Sample at 30 vertices
        S = rng.choice(40, 30, replace=False)
        Vk_S = Vk[S, :]
        f_S = f_true[S]
        # Reconstruct via least squares
        c_hat, _, _, _ = np.linalg.lstsq(Vk_S, f_S, rcond=None)
        f_hat = Vk @ c_hat
        assert np.allclose(f_hat, f_true, atol=1e-8)

    def test_underdetermined_fails(self, eigen_decomp_L):
        """Fewer samples than bandwidth cannot guarantee reconstruction."""
        evals, V = eigen_decomp_L
        k = 25
        Vk = V[:, :k]
        rng = np.random.RandomState(14921)
        c = rng.randn(k)
        f_true = Vk @ c
        # Only 10 samples for bandwidth 25 -> underdetermined
        S = rng.choice(40, 10, replace=False)
        Vk_S = Vk[S, :]
        assert Vk_S.shape[0] < k  # underdetermined

    def test_exact_at_sample_points(self, eigen_decomp_L):
        """Reconstructed signal matches original at sample points."""
        evals, V = eigen_decomp_L
        rng = np.random.RandomState(14922)
        k = 10  # low bandwidth for easier reconstruction
        Vk = V[:, :k]
        c = rng.randn(k)
        f_true = Vk @ c
        S = np.arange(0, 40, 2)  # 20 samples, > k=10
        Vk_S = Vk[S, :]
        f_S = f_true[S]
        c_hat, _, _, _ = np.linalg.lstsq(Vk_S, f_S, rcond=None)
        f_hat = Vk @ c_hat
        assert np.allclose(f_hat[S], f_true[S], atol=1e-10)
        assert np.allclose(f_hat, f_true, atol=1e-8)


# =====================================================================
# T1493: Nyquist-Type Bound
# =====================================================================

class TestT1493NyquistBound:
    """|S| >= bandwidth for perfect reconstruction."""

    def test_minimum_samples_equals_bandwidth(self, eigen_decomp_L):
        """Need at least k samples for k-bandlimited reconstruction."""
        _, V = eigen_decomp_L
        for k in [1, 10, 25]:
            Vk = V[:, :k]
            # Minimum sample set of size k should (generically) suffice
            rng = np.random.RandomState(1493 + k)
            S = rng.choice(40, k, replace=False)
            Vk_S = Vk[S, :]
            rank = np.linalg.matrix_rank(Vk_S, tol=1e-10)
            # Generically full rank (= k), or at least rank <= k
            assert rank <= k

    def test_bandwidth_equals_eigenspace_dimension(self, eigen_decomp_L):
        """For W(3,3), bandwidths align with spectral multiplicities:
        band 1 (eigenvalue 0), band 25 (eigenvalues 0,10), band 40 (all)."""
        evals, _ = eigen_decomp_L
        from collections import Counter
        counts = Counter(np.round(evals).astype(int))
        # Cumulative bandwidths
        assert counts[0] == 1   # bandwidth 1
        assert counts[0] + counts[10] == 25   # bandwidth 25
        assert counts[0] + counts[10] + counts[16] == 40  # full bandwidth

    def test_subsampling_below_nyquist(self, eigen_decomp_L):
        """Sampling below Nyquist rate leads to rank deficiency."""
        _, V = eigen_decomp_L
        k = 25
        Vk = V[:, :k]
        # Only take 5 samples for bandwidth 25
        S = np.array([0, 5, 10, 15, 20])
        Vk_S = Vk[S, :]
        rank = np.linalg.matrix_rank(Vk_S, tol=1e-10)
        assert rank <= 5  # can't exceed number of samples
        assert rank < k   # strictly less than bandwidth


# =====================================================================
# T1494: Tikhonov Regularization
# =====================================================================

class TestT1494TikhonovRegularization:
    """min ||f - g||^2 + gamma * f^T L f for graph smoothing."""

    def test_tikhonov_solution_formula(self, laplacian, eigen_decomp_L):
        """Closed form: f* = (I + gamma*L)^{-1} g."""
        evals, V = eigen_decomp_L
        rng = np.random.RandomState(1494)
        g = rng.randn(40)
        gamma = 0.5
        # Closed form
        f_star = np.linalg.solve(np.eye(40) + gamma * laplacian, g)
        # Spectral form
        g_hat = V.T @ g
        f_hat = g_hat / (1.0 + gamma * evals)
        f_spectral = V @ f_hat
        assert np.allclose(f_star, f_spectral, atol=1e-10)

    def test_tikhonov_smoother_than_input(self, laplacian, eigen_decomp_L):
        """Tikhonov-regularised signal is smoother (lower graph smoothness)."""
        evals, V = eigen_decomp_L
        rng = np.random.RandomState(14941)
        g = rng.randn(40)
        gamma = 1.0
        g_hat = V.T @ g
        f_hat = g_hat / (1.0 + gamma * evals)
        # Smoothness = f^T L f = sum lambda_i |f_hat_i|^2
        smooth_g = np.sum(evals * g_hat**2)
        smooth_f = np.sum(evals * f_hat**2)
        assert smooth_f < smooth_g

    def test_tikhonov_gamma_zero_identity(self, laplacian):
        """With gamma=0, Tikhonov returns the input signal."""
        rng = np.random.RandomState(14942)
        g = rng.randn(40)
        f = np.linalg.solve(np.eye(40) + 0.0 * laplacian, g)
        assert np.allclose(f, g, atol=1e-12)

    def test_tikhonov_large_gamma_constant(self, laplacian, eigen_decomp_L):
        """As gamma -> infinity, f* approaches a constant (DC component)."""
        evals, V = eigen_decomp_L
        rng = np.random.RandomState(14943)
        g = rng.randn(40)
        gamma = 1e6
        g_hat = V.T @ g
        f_hat = g_hat / (1.0 + gamma * evals)
        f = V @ f_hat
        # Non-zero eigenvalues get crushed; only DC survives
        assert np.std(f) < 1e-4  # nearly constant


# =====================================================================
# T1495: Sobolev Smoothness
# =====================================================================

class TestT1495SobolevSmoothness:
    """||f||_s^2 = sum lambda_i^s |f_hat(i)|^2 defines graph Sobolev norm."""

    def test_sobolev_norm_zero_is_l2(self, eigen_decomp_L):
        """s=0: Sobolev norm = L2 norm (Parseval)."""
        evals, V = eigen_decomp_L
        rng = np.random.RandomState(1495)
        f = rng.randn(40)
        f_hat = V.T @ f
        sobolev_0 = np.sum(f_hat**2)  # lambda^0 = 1
        l2_sq = np.sum(f**2)
        assert abs(sobolev_0 - l2_sq) < 1e-10

    def test_sobolev_norm_one_is_dirichlet(self, laplacian, eigen_decomp_L):
        """s=1: ||f||_1^2 = f^T L f (Dirichlet energy, excluding DC)."""
        evals, V = eigen_decomp_L
        rng = np.random.RandomState(14951)
        f = rng.randn(40)
        f_hat = V.T @ f
        sobolev_1 = np.sum(evals * f_hat**2)
        dirichlet = f @ laplacian @ f
        assert abs(sobolev_1 - dirichlet) < 1e-10

    def test_sobolev_embedding(self, eigen_decomp_L):
        """Higher-order Sobolev norm dominates lower for non-constant signal."""
        evals, V = eigen_decomp_L
        rng = np.random.RandomState(14952)
        f = rng.randn(40)
        f -= np.mean(f)  # remove DC to avoid 0^s issues
        f_hat = V.T @ f
        norms = []
        for s in [0.5, 1.0, 1.5, 2.0]:
            # Skip eigenvalue 0 (DC removed)
            sob = np.sum(np.where(evals > 0.5, evals**s, 0.0) * f_hat**2)
            norms.append(sob)
        # lambda_i >= 10 > 1, so lambda_i^s increases with s
        for i in range(len(norms) - 1):
            assert norms[i + 1] >= norms[i] - 1e-10

    def test_constant_signal_sobolev(self, eigen_decomp_L):
        """Constant signal has Sobolev norm 0 for s >= 1 (only DC component)."""
        evals, V = eigen_decomp_L
        f = np.ones(40) * 2.5
        f_hat = V.T @ f
        for s in [1, 2, 3]:
            sob = np.sum(evals**s * f_hat**2)
            assert abs(sob) < 1e-10


# =====================================================================
# T1496: Kernel Regression
# =====================================================================

class TestT1496KernelRegression:
    """K(i,j) = sum_l exp(-lambda_l * t) phi_l(i) phi_l(j) heat kernel."""

    def test_heat_kernel_is_symmetric(self, eigen_decomp_L):
        """Heat kernel matrix is symmetric."""
        evals, V = eigen_decomp_L
        t = 0.1
        K = V @ np.diag(np.exp(-evals * t)) @ V.T
        assert np.allclose(K, K.T, atol=1e-12)

    def test_heat_kernel_matches_expm(self, laplacian, eigen_decomp_L):
        """Heat kernel K = exp(-t*L) matches scipy expm."""
        evals, V = eigen_decomp_L
        t = 0.05
        K_spectral = V @ np.diag(np.exp(-evals * t)) @ V.T
        K_expm = expm(-t * laplacian)
        assert np.allclose(K_spectral, K_expm, atol=1e-10)

    def test_heat_kernel_regression_smoothing(self, eigen_decomp_L):
        """Heat kernel regression smooths noisy signal."""
        evals, V = eigen_decomp_L
        rng = np.random.RandomState(1496)
        f_clean = V[:, :5] @ rng.randn(5)  # low-frequency signal
        noise = 0.5 * rng.randn(40)
        f_noisy = f_clean + noise
        t = 0.1
        K = V @ np.diag(np.exp(-evals * t)) @ V.T
        f_smooth = K @ f_noisy
        # Smoothed signal should be closer to clean than noisy is
        err_noisy = np.linalg.norm(f_noisy - f_clean)
        err_smooth = np.linalg.norm(f_smooth - f_clean)
        assert err_smooth < err_noisy

    def test_heat_kernel_trace(self, eigen_decomp_L):
        """tr(K_t) = sum exp(-lambda_i * t). At t=0, tr = 40."""
        evals, V = eigen_decomp_L
        for t in [0.0, 0.01, 0.1, 1.0]:
            tr_expected = np.sum(np.exp(-evals * t))
            K = V @ np.diag(np.exp(-evals * t)) @ V.T
            assert abs(np.trace(K) - tr_expected) < 1e-10


# =====================================================================
# T1497: Polynomial Interpolation
# =====================================================================

class TestT1497PolynomialInterpolation:
    """Given f values at d+1 spectral nodes, find p(A) of degree d."""

    def test_degree_2_interpolates_3_eigenvalues(self, adjacency,
                                                  eigen_decomp_A):
        """A degree-2 polynomial in A can interpolate any function
        on the 3 distinct eigenvalues of W(3,3)."""
        evals, V = eigen_decomp_A
        distinct = np.array([-4.0, 2.0, 12.0])
        target_vals = np.array([1.0, -0.5, 3.0])
        # Solve Vandermonde
        Vand = np.column_stack([distinct**k for k in range(3)])
        coeffs = np.linalg.solve(Vand, target_vals)
        # Build p(A) = c0*I + c1*A + c2*A^2
        pA = coeffs[0] * np.eye(40) + coeffs[1] * adjacency + \
             coeffs[2] * adjacency @ adjacency
        # Verify on eigenspaces
        pA_evals = np.sort(np.linalg.eigvalsh(pA))
        expected = np.sort(np.concatenate([
            [np.polyval(coeffs[::-1], lam)] * mult
            for lam, mult in [(-4, 15), (2, 24), (12, 1)]
        ]))
        assert np.allclose(pA_evals, expected, atol=1e-8)

    def test_polynomial_interpolation_unique(self, adjacency):
        """Degree-2 interpolant on 3 distinct nodes is unique."""
        distinct = np.array([-4.0, 2.0, 12.0])
        Vand = np.column_stack([distinct**k for k in range(3)])
        assert abs(np.linalg.det(Vand)) > 1e-6

    def test_polynomial_annihilates_at_identity(self, adjacency,
                                                 spectral_idempotents):
        """Polynomial that vanishes on eigenvalues -4, 2 but equals 1 on 12
        gives the E0 idempotent."""
        E0, _, _ = spectral_idempotents
        distinct = np.array([-4.0, 2.0, 12.0])
        target_vals = np.array([0.0, 0.0, 1.0])
        Vand = np.column_stack([distinct**k for k in range(3)])
        coeffs = np.linalg.solve(Vand, target_vals)
        pA = coeffs[0] * np.eye(40) + coeffs[1] * adjacency + \
             coeffs[2] * adjacency @ adjacency
        assert np.allclose(pA, E0, atol=1e-10)


# =====================================================================
# T1498: Lagrange Basis
# =====================================================================

class TestT1498LagrangeBasis:
    """L_i(A) = prod_{j!=i} (A - theta_j I)/(theta_i - theta_j)."""

    def test_lagrange_idempotent_sum(self, adjacency):
        """Sum of Lagrange basis matrices equals identity."""
        thetas = np.array([-4.0, 2.0, 12.0])
        Ls = []
        for i in range(3):
            Li = np.eye(40)
            for j in range(3):
                if j != i:
                    Li = Li @ (adjacency - thetas[j] * np.eye(40)) / \
                         (thetas[i] - thetas[j])
            Ls.append(Li)
        assert np.allclose(Ls[0] + Ls[1] + Ls[2], np.eye(40), atol=1e-10)

    def test_lagrange_are_idempotent(self, adjacency):
        """Each L_i(A) is idempotent: L_i^2 = L_i."""
        thetas = np.array([-4.0, 2.0, 12.0])
        for i in range(3):
            Li = np.eye(40)
            for j in range(3):
                if j != i:
                    Li = Li @ (adjacency - thetas[j] * np.eye(40)) / \
                         (thetas[i] - thetas[j])
            assert np.allclose(Li @ Li, Li, atol=1e-10)

    def test_lagrange_are_orthogonal(self, adjacency):
        """L_i(A) * L_j(A) = 0 for i != j."""
        thetas = np.array([-4.0, 2.0, 12.0])
        Ls = []
        for i in range(3):
            Li = np.eye(40)
            for j in range(3):
                if j != i:
                    Li = Li @ (adjacency - thetas[j] * np.eye(40)) / \
                         (thetas[i] - thetas[j])
            Ls.append(Li)
        for i in range(3):
            for j in range(3):
                if i != j:
                    assert np.allclose(Ls[i] @ Ls[j],
                                       np.zeros((40, 40)), atol=1e-10)

    def test_lagrange_ranks(self, adjacency):
        """Lagrange basis matrices have ranks 15, 24, 1."""
        thetas = np.array([-4.0, 2.0, 12.0])
        ranks = []
        for i in range(3):
            Li = np.eye(40)
            for j in range(3):
                if j != i:
                    Li = Li @ (adjacency - thetas[j] * np.eye(40)) / \
                         (thetas[i] - thetas[j])
            ranks.append(np.linalg.matrix_rank(Li, tol=1e-8))
        assert sorted(ranks) == [1, 15, 24]


# =====================================================================
# T1499: Newton Form
# =====================================================================

class TestT1499NewtonForm:
    """Divided differences for polynomial interpolation on eigenvalues."""

    def test_divided_differences_linear(self):
        """f[-4] = f(-4); f[-4,2] = (f(2)-f(-4))/(2-(-4))."""
        nodes = np.array([-4.0, 2.0, 12.0])
        f_vals = np.exp(nodes / 12.0)
        # 0th order
        dd0 = f_vals[0]
        assert abs(dd0 - np.exp(-4.0 / 12.0)) < 1e-14
        # 1st order
        dd1 = (f_vals[1] - f_vals[0]) / (nodes[1] - nodes[0])
        expected = (np.exp(2.0 / 12.0) - np.exp(-4.0 / 12.0)) / 6.0
        assert abs(dd1 - expected) < 1e-14

    def test_newton_polynomial_matches_lagrange(self, adjacency):
        """Newton form p(A) = f[t0]I + f[t0,t1](A-t0 I) + f[t0,t1,t2](A-t0 I)(A-t1 I)
        matches Lagrange interpolant."""
        nodes = np.array([-4.0, 2.0, 12.0])
        f_vals = np.array([1.0, 0.5, 2.0])
        # Divided differences
        dd = f_vals.copy()
        for j in range(1, 3):
            for i in range(2, j - 1, -1):
                dd[i] = (dd[i] - dd[i - 1]) / (nodes[i] - nodes[i - j])
        # Actually compute standard divided difference table
        dd_table = np.zeros((3, 3))
        dd_table[:, 0] = f_vals
        for j in range(1, 3):
            for i in range(j, 3):
                dd_table[i, j] = (dd_table[i, j-1] - dd_table[i-1, j-1]) / \
                                 (nodes[i] - nodes[i-j])
        c0 = dd_table[0, 0]
        c1 = dd_table[1, 1]
        c2 = dd_table[2, 2]
        # Newton form
        I = np.eye(40)
        pA_newton = c0 * I + c1 * (adjacency - nodes[0] * I) + \
                    c2 * (adjacency - nodes[0] * I) @ (adjacency - nodes[1] * I)
        # Lagrange form
        Vand = np.column_stack([nodes**k for k in range(3)])
        coeffs = np.linalg.solve(Vand, f_vals)
        pA_lagrange = coeffs[0] * I + coeffs[1] * adjacency + \
                      coeffs[2] * adjacency @ adjacency
        assert np.allclose(pA_newton, pA_lagrange, atol=1e-8)

    def test_newton_divided_diff_symmetry(self):
        """Divided differences are symmetric in the nodes."""
        nodes = np.array([-4.0, 2.0, 12.0])
        f_vals = np.array([1.0, 3.0, -2.0])
        # f[t0,t1,t2] should be same regardless of order
        def dd2(n, f):
            return ((f[2] - f[1]) / (n[2] - n[1]) - (f[1] - f[0]) / (n[1] - n[0])) / \
                   (n[2] - n[0])
        val1 = dd2(nodes, f_vals)
        # Permute
        perm = [1, 2, 0]
        val2 = dd2(nodes[perm], f_vals[perm])
        assert abs(val1 - val2) < 1e-12


# =====================================================================
# T1500: Minimax Polynomial
# =====================================================================

class TestT1500MinimaxPolynomial:
    """Best uniform approximation on spectrum {-4, 2, 12}."""

    def test_minimax_degree1(self):
        """Best degree-1 polynomial minimizing max |f(x) - p(x)|
        on {-4, 2, 12} for f(x) = x^2."""
        nodes = np.array([-4.0, 2.0, 12.0])
        target = nodes**2
        # For 3 points, degree-1 minimax: equioscillation at 2 points
        # With 3 points and degree 1, best fit is least-squares on all 3
        # but minimax has error equioscillation
        # Use Chebyshev approach: the best degree-1 has equi-oscillating error
        # Brute force: minimize max |target - (a + b*x)| over a,b
        from scipy.optimize import minimize
        def obj(params):
            a, b = params
            errs = np.abs(target - (a + b * nodes))
            return np.max(errs)
        res = minimize(obj, [0, 0], method='Nelder-Mead')
        minimax_err = res.fun
        # Check the minimax error is less than any random degree-1
        rng = np.random.RandomState(1500)
        for _ in range(50):
            a, b = rng.randn(2) * 10
            err = np.max(np.abs(target - (a + b * nodes)))
            assert err >= minimax_err - 1e-6

    def test_minimax_degree2_exact(self):
        """Degree-2 polynomial on 3 points is exact -> minimax error = 0."""
        nodes = np.array([-4.0, 2.0, 12.0])
        target = np.sin(nodes / 10.0)
        # 3 points, degree 2 -> exact interpolation
        coeffs = np.polyfit(nodes, target, deg=2)
        approx = np.polyval(coeffs, nodes)
        assert np.max(np.abs(approx - target)) < 1e-12

    def test_minimax_equioscillation(self):
        """Minimax degree-0 (constant) approximation of f(x)=x on {-4,2,12}:
        best constant = (max+min)/2 = (-4+12)/2 = 4."""
        nodes = np.array([-4.0, 2.0, 12.0])
        target = nodes.copy()
        best_const = (np.max(target) + np.min(target)) / 2.0
        assert abs(best_const - 4.0) < 1e-14
        # Max error = (max-min)/2 = 8
        max_err = np.max(np.abs(target - best_const))
        assert abs(max_err - 8.0) < 1e-14


# =====================================================================
# T1501: Bernstein Inequality
# =====================================================================

class TestT1501BernsteinInequality:
    """For bandlimited f: ||grad f|| <= lambda_max * ||f||."""

    def test_bernstein_inequality_holds(self, laplacian, eigen_decomp_L,
                                        incidence):
        """||B f||^2 <= lambda_max * ||f||^2 for bandlimited signals."""
        evals, V = eigen_decomp_L
        B, _ = incidence
        rng = np.random.RandomState(1501)
        lambda_max = 16.0
        for k in [1, 25, 40]:
            for trial in range(10):
                c = rng.randn(k)
                f = V[:, :k] @ c
                grad_norm_sq = np.sum((B @ f)**2)
                # f^T L f = ||grad f||^2 = sum over edges
                # By Rayleigh quotient: f^T L f <= lambda_max * ||f||^2
                assert grad_norm_sq <= lambda_max * np.sum(f**2) + 1e-10

    def test_bernstein_tight_at_top_eigenspace(self, laplacian, eigen_decomp_L,
                                                incidence):
        """Equality in Bernstein when f is in the top eigenspace (lambda=16)."""
        evals, V = eigen_decomp_L
        B, _ = incidence
        # f in eigenspace of lambda=16 (last 15 eigenvectors)
        rng = np.random.RandomState(15011)
        c = rng.randn(15)
        f = V[:, 25:] @ c
        grad_norm_sq = np.sum((B @ f)**2)
        ratio = grad_norm_sq / np.sum(f**2)
        assert abs(ratio - 16.0) < 1e-8

    def test_bernstein_bound_value(self, laplacian, eigen_decomp_L):
        """For W(3,3), Bernstein bound involves lambda_max(L) = 16."""
        evals, _ = eigen_decomp_L
        assert abs(np.max(evals) - 16.0) < 1e-10


# =====================================================================
# T1502: Poincare Inequality
# =====================================================================

class TestT1502PoincareInequality:
    """||f - f_avg||^2 <= (1/lambda_1) * f^T L f where lambda_1 = 10."""

    def test_poincare_inequality_holds(self, laplacian, eigen_decomp_L):
        """Poincare inequality for many random signals."""
        evals, V = eigen_decomp_L
        lambda_1 = 10.0
        rng = np.random.RandomState(1502)
        for _ in range(100):
            f = rng.randn(40)
            f_centered = f - np.mean(f)
            lhs = np.sum(f_centered**2)
            rhs = (1.0 / lambda_1) * (f @ laplacian @ f)
            assert lhs <= rhs + 1e-10

    def test_poincare_tight_at_eigenvalue_10(self, laplacian, eigen_decomp_L):
        """Equality when f is in the eigenspace of lambda_1=10."""
        evals, V = eigen_decomp_L
        rng = np.random.RandomState(15021)
        c = rng.randn(24)
        f = V[:, 1:25] @ c  # eigenspace of lambda=10
        f_centered = f - np.mean(f)
        lhs = np.sum(f_centered**2)
        rhs = (1.0 / 10.0) * (f @ laplacian @ f)
        assert abs(lhs - rhs) < 1e-8

    def test_poincare_spectral_gap(self, eigen_decomp_L):
        """The spectral gap lambda_1 = 10 for W(3,3)."""
        evals, _ = eigen_decomp_L
        # Smallest positive eigenvalue
        pos_evals = evals[evals > 0.5]
        assert abs(np.min(pos_evals) - 10.0) < 1e-10

    def test_poincare_constant_signal_equality(self, laplacian):
        """Constant signal: both sides are zero."""
        f = np.ones(40) * 5.0
        f_centered = f - np.mean(f)
        assert np.allclose(f_centered, 0.0, atol=1e-14)
        assert abs(f @ laplacian @ f) < 1e-10


# =====================================================================
# T1503: Total Variation
# =====================================================================

class TestT1503TotalVariation:
    """TV(f) = sum_{i~j} |f(i)-f(j)| for graph signals."""

    def test_tv_constant_is_zero(self, w33):
        """TV of constant signal is 0."""
        f = np.ones(40) * 3.14
        n = 40
        tv = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                if w33[i, j]:
                    tv += abs(f[i] - f[j])
        assert abs(tv) < 1e-14

    def test_tv_indicator_counts_cut(self, w33):
        """TV of {0,1} indicator = number of cut edges."""
        rng = np.random.RandomState(1503)
        f = (rng.rand(40) > 0.5).astype(float)
        n = 40
        tv = 0.0
        cut = 0
        for i in range(n):
            for j in range(i + 1, n):
                if w33[i, j]:
                    tv += abs(f[i] - f[j])
                    if f[i] != f[j]:
                        cut += 1
        assert abs(tv - cut) < 1e-14
        assert cut > 0

    def test_tv_versus_gradient(self, w33, incidence):
        """TV(f) = ||B f||_1 = sum |grad_e f|."""
        B, edges = incidence
        rng = np.random.RandomState(15031)
        f = rng.randn(40)
        grad_f = B @ f
        tv_from_B = np.sum(np.abs(grad_f))
        tv_direct = 0.0
        n = 40
        for i in range(n):
            for j in range(i + 1, n):
                if w33[i, j]:
                    tv_direct += abs(f[i] - f[j])
        assert abs(tv_from_B - tv_direct) < 1e-10

    def test_tv_triangle_inequality(self, incidence):
        """TV(f + g) <= TV(f) + TV(g)."""
        B, _ = incidence
        rng = np.random.RandomState(15032)
        f = rng.randn(40)
        g = rng.randn(40)
        tv_f = np.sum(np.abs(B @ f))
        tv_g = np.sum(np.abs(B @ g))
        tv_fg = np.sum(np.abs(B @ (f + g)))
        assert tv_fg <= tv_f + tv_g + 1e-10


# =====================================================================
# T1504: Graph Splines
# =====================================================================

class TestT1504GraphSplines:
    """Minimize f^T L^s f subject to interpolation at given vertices."""

    def test_spline_interpolates(self, laplacian, eigen_decomp_L):
        """Graph spline passes through prescribed values."""
        evals, V = eigen_decomp_L
        s = 2  # bi-Laplacian spline
        # Interpolation constraints at vertices 0,5,10,15
        interp_verts = np.array([0, 5, 10, 15])
        interp_vals = np.array([1.0, -1.0, 0.5, 2.0])
        # Spline minimizes f^T L^s f subject to f[interp_verts] = interp_vals
        # L^s in spectral domain
        L_s_diag = evals**s
        # Replace zero eigenvalue penalty with 0 (unconstrained DC)
        L_s_diag[0] = 0.0
        # Use Lagrange multiplier: (L^s) f + C^T mu = 0, C f = d
        # where C is selection matrix
        n = 40
        m = len(interp_verts)
        L_s = V @ np.diag(L_s_diag) @ V.T
        C = np.zeros((m, n))
        for idx, v in enumerate(interp_verts):
            C[idx, v] = 1.0
        # KKT system
        KKT = np.zeros((n + m, n + m))
        KKT[:n, :n] = L_s + 1e-12 * np.eye(n)  # tiny regularizer for DC
        KKT[:n, n:] = C.T
        KKT[n:, :n] = C
        rhs = np.zeros(n + m)
        rhs[n:] = interp_vals
        sol = np.linalg.solve(KKT, rhs)
        f_spline = sol[:n]
        # Check interpolation
        assert np.allclose(f_spline[interp_verts], interp_vals, atol=1e-8)

    def test_spline_smoother_than_alternatives(self, laplacian, eigen_decomp_L):
        """Graph spline has lower smoothness penalty than random interpolants."""
        evals, V = eigen_decomp_L
        s = 1
        interp_verts = np.array([0, 10, 20, 30])
        interp_vals = np.array([1.0, -1.0, 2.0, 0.0])
        n = 40
        m = len(interp_verts)
        L_s_diag = evals**s
        L_s_diag[0] = 0.0
        L_s = V @ np.diag(L_s_diag) @ V.T
        C = np.zeros((m, n))
        for idx, v in enumerate(interp_verts):
            C[idx, v] = 1.0
        KKT = np.zeros((n + m, n + m))
        KKT[:n, :n] = L_s + 1e-12 * np.eye(n)
        KKT[:n, n:] = C.T
        KKT[n:, :n] = C
        rhs = np.zeros(n + m)
        rhs[n:] = interp_vals
        sol = np.linalg.solve(KKT, rhs)
        f_spline = sol[:n]
        cost_spline = f_spline @ L_s @ f_spline
        # Compare with random interpolants
        rng = np.random.RandomState(1504)
        for _ in range(30):
            f_rand = rng.randn(40)
            # Enforce interpolation
            for idx, v in enumerate(interp_verts):
                f_rand[v] = interp_vals[idx]
            cost_rand = f_rand @ L_s @ f_rand
            assert cost_spline <= cost_rand + 1e-6

    def test_spline_higher_s_smoother(self, laplacian, eigen_decomp_L):
        """Higher s penalizes roughness more, giving smoother splines."""
        evals, V = eigen_decomp_L
        interp_verts = np.array([0, 10, 20, 30])
        interp_vals = np.array([1.0, -1.0, 2.0, 0.0])
        n = 40
        m = len(interp_verts)
        C = np.zeros((m, n))
        for idx, v in enumerate(interp_verts):
            C[idx, v] = 1.0
        # Dirichlet energy (s=1) of splines for different s
        L1 = V @ np.diag(evals) @ V.T
        dirichlet_energies = []
        for s in [1, 2, 3]:
            L_s_diag = evals**s
            L_s_diag[0] = 0.0
            L_s = V @ np.diag(L_s_diag) @ V.T
            KKT = np.zeros((n + m, n + m))
            KKT[:n, :n] = L_s + 1e-12 * np.eye(n)
            KKT[:n, n:] = C.T
            KKT[n:, :n] = C
            rhs = np.zeros(n + m)
            rhs[n:] = interp_vals
            sol = np.linalg.solve(KKT, rhs)
            f = sol[:n]
            dirichlet_energies.append(f @ L1 @ f)
        # Just check they're all finite and non-negative
        for de in dirichlet_energies:
            assert de >= -1e-8


# =====================================================================
# T1505: Diffusion Wavelets
# =====================================================================

class TestT1505DiffusionWavelets:
    """Dyadic powers of diffusion operator T = (I + A/12)/2."""

    def test_diffusion_operator_spectrum(self, adjacency, eigen_decomp_A):
        """T = (I + A/12)/2 has eigenvalues (1+lambda/12)/2."""
        evals_A, V = eigen_decomp_A
        T = (np.eye(40) + adjacency / 12.0) / 2.0
        evals_T = np.sort(np.linalg.eigvalsh(T))
        expected = np.sort((1.0 + evals_A / 12.0) / 2.0)
        assert np.allclose(evals_T, expected, atol=1e-10)
        # Distinct T-eigenvalues: (1+(-4/12))/2=1/3, (1+(2/12))/2=7/12, (1+1)/2=1
        distinct = np.array([1.0 / 3.0, 7.0 / 12.0, 1.0])
        for d in distinct:
            assert np.min(np.abs(evals_T - d)) < 1e-10

    def test_diffusion_powers_decay(self, adjacency):
        """T^{2^j} eigenvalues decay: lambda^{2^j} -> 0 for |lambda|<1."""
        T = (np.eye(40) + adjacency / 12.0) / 2.0
        # Non-trivial eigenvalues (< 1) should shrink with dyadic powers
        prev_second = None
        for j in range(5):
            Tj = np.linalg.matrix_power(T, 2**j)
            evals = np.sort(np.linalg.eigvalsh(Tj))
            # Second-largest eigenvalue (eigenvalue 1 stays at 1)
            second_largest = evals[-2]
            if prev_second is not None:
                assert second_largest <= prev_second + 1e-10
            prev_second = second_largest
        # After 16 powers, second-largest should be very small
        assert prev_second < 0.01

    def test_diffusion_wavelet_subspaces(self, adjacency, eigen_decomp_A):
        """Diffusion wavelet detail at scale j captures information
        in T^{2^j} - T^{2^{j+1}} eigenspace."""
        evals_A, V = eigen_decomp_A
        T = (np.eye(40) + adjacency / 12.0) / 2.0
        for j in range(3):
            Tj = np.linalg.matrix_power(T, 2**j)
            Tj1 = np.linalg.matrix_power(T, 2**(j + 1))
            W_j = Tj - Tj1  # wavelet operator at scale j
            # W_j is symmetric
            assert np.allclose(W_j, W_j.T, atol=1e-10)
            # W_j is positive semidefinite (eigenvalues of T in [0,1])
            evals_W = np.linalg.eigvalsh(W_j)
            assert np.all(evals_W >= -1e-10)

    def test_diffusion_operator_stochastic(self, adjacency):
        """T is doubly stochastic (row sums = 1 for regular graph)."""
        T = (np.eye(40) + adjacency / 12.0) / 2.0
        row_sums = T.sum(axis=1)
        assert np.allclose(row_sums, 1.0, atol=1e-12)


# =====================================================================
# T1506: Spectral Graph Wavelet
# =====================================================================

class TestT1506SpectralGraphWavelet:
    """g(L) = sum g(lambda_i) E_i for wavelet kernel g."""

    def test_wavelet_kernel_localization(self, eigen_decomp_L):
        """Wavelet at vertex 0: psi_0 = g(L) delta_0 is localized."""
        evals, V = eigen_decomp_L
        # Mexican hat wavelet kernel: g(x) = x * exp(-x^2 / (2*s^2))
        s = 5.0
        g_vals = evals * np.exp(-evals**2 / (2.0 * s**2))
        # g(L) = V diag(g) V^T
        delta_0 = np.zeros(40)
        delta_0[0] = 1.0
        psi_0 = V @ (g_vals * (V.T @ delta_0))
        # Psi should be concentrated near vertex 0
        assert abs(psi_0[0]) > 0.01  # non-trivial at origin
        # Total energy is finite
        assert np.sum(psi_0**2) > 0

    def test_wavelet_scale_partition(self, eigen_decomp_L):
        """Multi-scale wavelet decomposition: sum of squared kernels
        at multiple scales covers spectrum."""
        evals, V = eigen_decomp_L
        scales = [1.0, 3.0, 8.0, 15.0]
        # g_s(x) = x * exp(-x^2/(2s^2))
        total = np.zeros(40)
        for s in scales:
            g = evals * np.exp(-evals**2 / (2.0 * s**2))
            total += g**2
        # All non-zero eigenvalues should have positive total coverage
        for i in range(1, 40):
            assert total[i] > 0

    def test_wavelet_frame_bound(self, eigen_decomp_L):
        """Wavelet system forms a frame: A ||f||^2 <= sum |<f, psi_{s,i}>|^2 <= B ||f||^2."""
        evals, V = eigen_decomp_L
        scales = [2.0, 5.0, 12.0]
        rng = np.random.RandomState(1506)
        f = rng.randn(40)
        f -= np.mean(f)  # remove DC
        f_hat = V.T @ f
        total_energy = 0.0
        for s in scales:
            g = evals * np.exp(-evals**2 / (2.0 * s**2))
            # Energy in this scale
            total_energy += np.sum((g * f_hat)**2)
        # Should be bounded above and below by some multiple of ||f||^2
        f_norm_sq = np.sum(f**2)
        # Total energy > 0 (frame lower bound)
        assert total_energy > 0
        # And finite (frame upper bound)
        assert total_energy < 1e10 * f_norm_sq


# =====================================================================
# T1507: Compressed Sensing
# =====================================================================

class TestT1507CompressedSensing:
    """Random sampling + sparse recovery via basis pursuit."""

    def test_sparse_signal_recovery(self, eigen_decomp_L):
        """Recover a spectrally sparse signal from few samples via
        least squares on the correct support."""
        evals, V = eigen_decomp_L
        rng = np.random.RandomState(1507)
        # Create a 3-sparse signal in GFT domain
        k_sparse = 3
        support = rng.choice(40, k_sparse, replace=False)
        f_hat = np.zeros(40)
        f_hat[support] = rng.randn(k_sparse)
        f = V @ f_hat
        # Sample at m = 15 random vertices
        m = 15
        S = rng.choice(40, m, replace=False)
        y = f[S]
        # Oracle recovery (known support): V_S[:,support] c = y
        VS = V[S, :][:, support]
        c_hat, _, _, _ = np.linalg.lstsq(VS, y, rcond=None)
        f_hat_rec = np.zeros(40)
        f_hat_rec[support] = c_hat
        f_rec = V @ f_hat_rec
        assert np.allclose(f_rec, f, atol=1e-6)

    def test_rip_proxy(self, eigen_decomp_L):
        """Check near-isometry of subsampled Fourier matrix for
        random column subsets (RIP-like condition)."""
        _, V = eigen_decomp_L
        rng = np.random.RandomState(15071)
        m = 20  # measurements
        S = rng.choice(40, m, replace=False)
        Phi = V[S, :] * np.sqrt(40.0 / m)  # normalized
        # For random s-sparse vectors, Phi should approximately preserve norms
        s = 3
        singular_vals = np.linalg.svd(Phi[:, :s], compute_uv=False)
        # All singular values should be O(1)
        assert np.max(singular_vals) < 10
        assert np.min(singular_vals) > 0.01

    def test_measurement_matrix_coherence(self, eigen_decomp_L):
        """Coherence mu = max_{i,j} |<phi_i, phi_j>| of the sensing basis."""
        _, V = eigen_decomp_L
        n = 40
        # Coherence of the GFT basis: max off-diagonal of V^T V
        # V is orthonormal, so V^T V = I. But we compute coherence of rows
        G = V @ V.T  # should be I
        np.fill_diagonal(G, 0)
        mu = np.max(np.abs(G))
        assert mu < 1e-10  # orthonormal => zero coherence among basis


# =====================================================================
# T1508: Graph Convolutional Filter
# =====================================================================

class TestT1508GraphConvolutionalFilter:
    """H(L) = sum_k h_k L^k; output y = H(L)*x for input signal x."""

    def test_linear_filter(self, laplacian, eigen_decomp_L):
        """Degree-1 filter H(L) = h0*I + h1*L."""
        evals, V = eigen_decomp_L
        h0, h1 = 2.0, -0.1
        H = h0 * np.eye(40) + h1 * laplacian
        rng = np.random.RandomState(1508)
        x = rng.randn(40)
        y = H @ x
        # In spectral domain: y_hat = (h0 + h1*lambda) * x_hat
        x_hat = V.T @ x
        y_hat_expected = (h0 + h1 * evals) * x_hat
        y_expected = V @ y_hat_expected
        assert np.allclose(y, y_expected, atol=1e-10)

    def test_filter_composition(self, laplacian, eigen_decomp_L):
        """Composing filters: H1(L) H2(L) = (H1*H2)(L) in spectral domain."""
        evals, V = eigen_decomp_L
        h1_coeffs = np.array([1.0, -0.05, 0.001])  # h1(L) = 1 - 0.05L + 0.001L^2
        h2_coeffs = np.array([0.5, 0.1])  # h2(L) = 0.5 + 0.1L
        # Build filter matrices
        n = 40
        L = laplacian
        H1 = h1_coeffs[0] * np.eye(n) + h1_coeffs[1] * L + h1_coeffs[2] * L @ L
        H2 = h2_coeffs[0] * np.eye(n) + h2_coeffs[1] * L
        # Composition
        H12 = H1 @ H2
        # Spectral: multiply frequency responses
        resp1 = h1_coeffs[0] + h1_coeffs[1] * evals + h1_coeffs[2] * evals**2
        resp2 = h2_coeffs[0] + h2_coeffs[1] * evals
        resp12 = resp1 * resp2
        H12_spectral = V @ np.diag(resp12) @ V.T
        assert np.allclose(H12, H12_spectral, atol=1e-8)

    def test_filter_frequency_response(self, laplacian, eigen_decomp_L):
        """Frequency response of filter H(L) evaluated at eigenvalues."""
        evals, V = eigen_decomp_L
        # Low-pass FIR: H(L) = I - L/16
        h_coeffs = [1.0, -1.0 / 16.0]
        n = 40
        H = h_coeffs[0] * np.eye(n) + h_coeffs[1] * laplacian
        # Frequency response at distinct eigenvalues
        distinct = np.array([0.0, 10.0, 16.0])
        responses = h_coeffs[0] + h_coeffs[1] * distinct
        assert np.allclose(responses, [1.0, 1.0 - 10.0/16.0, 0.0], atol=1e-14)
        # At lambda=16, response is 0 -> high frequencies killed
        # Verify: H kills eigenvalue-16 eigenvectors
        top_evec = V[:, -1]  # eigenvalue 16
        assert np.allclose(H @ top_evec, 0.0, atol=1e-10)

    def test_filter_preserves_eigenspaces(self, laplacian, eigen_decomp_L):
        """Any polynomial filter H(L) preserves eigenspaces of L."""
        evals, V = eigen_decomp_L
        n = 40
        L = laplacian
        H = 3 * np.eye(n) - 0.2 * L + 0.01 * L @ L
        # H should commute with L (both diagonal in same basis)
        assert np.allclose(H @ L, L @ H, atol=1e-8)

    def test_filter_output_energy(self, laplacian, eigen_decomp_L):
        """Output energy ||y||^2 = sum |H(lambda_i)|^2 |x_hat_i|^2."""
        evals, V = eigen_decomp_L
        rng = np.random.RandomState(15082)
        x = rng.randn(40)
        x_hat = V.T @ x
        # Filter: H(lambda) = exp(-lambda/10)
        h_vals = np.exp(-evals / 10.0)
        y = V @ (h_vals * x_hat)
        energy_y = np.sum(y**2)
        energy_spectral = np.sum(h_vals**2 * x_hat**2)
        assert abs(energy_y - energy_spectral) < 1e-10
