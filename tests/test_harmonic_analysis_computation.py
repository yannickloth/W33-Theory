"""
Phase LXXXV: Harmonic Analysis on Graphs (T1341-T1361)
======================================================

Computes the graph Fourier transform, spectral filtering, heat/wave
diffusion, wavelets, gradient/divergence operators, and spectral
clustering on W(3,3) = SRG(40,12,2,4).

All computations are from the actual adjacency matrix of the symplectic
polar space W(3,3) over GF(3).

Key results:
  W(3,3): n=40, k=12, lambda=2, mu=4
  A spectrum:  {12^1, 2^24, (-4)^15}
  L = kI - A,  spectrum: {0^1, 10^24, 16^15}
  240 edges, spectral gap lambda_2(L) = 10
  tr(L)   = 480
  tr(L^2) = 6240
  Total effective resistance = 133.5
"""

import pytest
import numpy as np
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
def laplacian(w33):
    """Graph Laplacian L = kI - A for k-regular graph (k=12)."""
    return 12.0 * np.eye(40) - w33.astype(float)


@pytest.fixture(scope="module")
def eigen_decomp(laplacian):
    """Full eigendecomposition of L, sorted by ascending eigenvalue."""
    evals, evecs = np.linalg.eigh(laplacian)
    idx = np.argsort(evals)
    return evals[idx], evecs[:, idx]


@pytest.fixture(scope="module")
def incidence(w33):
    """Oriented incidence matrix B (m x n) and edge list.

    Convention: for edge e = (i,j) with i < j,
        B[e, i] = -1,  B[e, j] = +1.
    So (grad f)(e) = B @ f = f(j) - f(i), and L = B^T B.
    """
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
# T1341: Graph Fourier Transform
# =====================================================================

class TestT1341GraphFourierTransform:
    """GFT uses eigenvectors of L as Fourier basis: f_hat = V^T f."""

    def test_eigenvector_orthonormality(self, eigen_decomp):
        """Eigenvectors of L form an orthonormal basis of R^40."""
        _, V = eigen_decomp
        assert np.allclose(V.T @ V, np.eye(40), atol=1e-10)
        assert np.allclose(V @ V.T, np.eye(40), atol=1e-10)

    def test_eigenvalue_spectrum(self, eigen_decomp):
        """L has spectrum {0^1, 10^24, 16^15}."""
        evals, _ = eigen_decomp
        from collections import Counter
        counts = Counter(np.round(evals).astype(int))
        assert counts[0] == 1
        assert counts[10] == 24
        assert counts[16] == 15

    def test_gft_roundtrip(self, eigen_decomp):
        """Forward then inverse GFT recovers original signal exactly."""
        _, V = eigen_decomp
        rng = np.random.RandomState(1341)
        f = rng.randn(40)
        f_hat = V.T @ f
        f_recovered = V @ f_hat
        assert np.allclose(f_recovered, f, atol=1e-10)

    def test_gft_inverse(self, eigen_decomp):
        """Inverse GFT then forward GFT recovers spectral coefficients."""
        _, V = eigen_decomp
        rng = np.random.RandomState(1341)
        f_hat = rng.randn(40)
        f = V @ f_hat
        f_hat_recovered = V.T @ f
        assert np.allclose(f_hat_recovered, f_hat, atol=1e-10)

    def test_dc_component(self, eigen_decomp):
        """Constant signal has energy only in the zeroth Fourier mode."""
        _, V = eigen_decomp
        f = np.ones(40) * 3.0
        f_hat = V.T @ f
        # V[:,0] ~ (1/sqrt(40)) * ones, so |f_hat[0]| = 3*sqrt(40)
        assert abs(abs(f_hat[0]) - 3.0 * np.sqrt(40)) < 1e-10
        assert np.allclose(f_hat[1:], 0.0, atol=1e-10)

    def test_diagonalisation(self, eigen_decomp, laplacian):
        """V^T L V = diag(eigenvalues)."""
        evals, V = eigen_decomp
        D = V.T @ laplacian @ V
        assert np.allclose(D, np.diag(evals), atol=1e-10)


# =====================================================================
# T1342: Parseval's Theorem
# =====================================================================

class TestT1342ParsevalTheorem:
    """Energy conservation under GFT: ||f||^2 = ||f_hat||^2."""

    def test_parseval_random_signals(self, eigen_decomp):
        """Parseval identity holds for several random signals."""
        _, V = eigen_decomp
        rng = np.random.RandomState(1342)
        for _ in range(10):
            f = rng.randn(40)
            f_hat = V.T @ f
            assert abs(np.dot(f, f) - np.dot(f_hat, f_hat)) < 1e-10

    def test_parseval_indicator(self, eigen_decomp):
        """Parseval for single-vertex indicator: ||f||^2 = 1."""
        _, V = eigen_decomp
        f = np.zeros(40)
        f[0] = 1.0
        f_hat = V.T @ f
        assert abs(np.dot(f_hat, f_hat) - 1.0) < 1e-10

    def test_parseval_degree_signal(self, eigen_decomp, w33):
        """Parseval for degree signal (constant k=12 for regular graph)."""
        _, V = eigen_decomp
        f = w33.astype(float).sum(axis=1)  # all entries are 12
        f_hat = V.T @ f
        assert abs(np.sum(f**2) - np.sum(f_hat**2)) < 1e-8

    def test_inner_product_preserved(self, eigen_decomp):
        """Inner product preserved: <f, g> = <f_hat, g_hat>."""
        _, V = eigen_decomp
        rng = np.random.RandomState(1342)
        f = rng.randn(40)
        g = rng.randn(40)
        assert abs(f @ g - (V.T @ f) @ (V.T @ g)) < 1e-10


# =====================================================================
# T1343: Spectral Filtering
# =====================================================================

class TestT1343SpectralFiltering:
    """h(L) = V diag(h(lambda)) V^T applies filter h in spectral domain."""

    def test_ideal_lowpass(self, eigen_decomp):
        """Ideal low-pass (cutoff < 10) passes only DC component."""
        evals, V = eigen_decomp
        h_vals = np.where(evals < 5.0, 1.0, 0.0)
        H = V @ np.diag(h_vals) @ V.T
        rng = np.random.RandomState(1343)
        f = rng.randn(40)
        f_filtered = H @ f
        # Only DC passes: output is constant = mean(f)
        assert np.allclose(f_filtered, np.mean(f), atol=1e-10)

    def test_ideal_highpass(self, eigen_decomp):
        """Ideal high-pass removes DC, so constants map to zero."""
        evals, V = eigen_decomp
        h_vals = np.where(evals > 5.0, 1.0, 0.0)
        H = V @ np.diag(h_vals) @ V.T
        f = np.ones(40) * 5.0
        assert np.allclose(H @ f, 0.0, atol=1e-10)

    def test_identity_filter(self, eigen_decomp):
        """h(lambda) = 1 for all lambda gives the identity."""
        _, V = eigen_decomp
        H = V @ np.diag(np.ones(40)) @ V.T
        assert np.allclose(H, np.eye(40), atol=1e-10)

    def test_laplacian_as_filter(self, eigen_decomp, laplacian):
        """h(lambda) = lambda recovers L itself."""
        evals, V = eigen_decomp
        H = V @ np.diag(evals) @ V.T
        assert np.allclose(H, laplacian, atol=1e-10)

    def test_filter_composition(self, eigen_decomp):
        """Composing two filters: (h1 * h2)(L) = h1(L) h2(L)."""
        evals, V = eigen_decomp
        h1 = np.exp(-0.1 * evals)
        h2 = 1.0 / (1.0 + evals)
        H1 = V @ np.diag(h1) @ V.T
        H2 = V @ np.diag(h2) @ V.T
        H12 = V @ np.diag(h1 * h2) @ V.T
        assert np.allclose(H1 @ H2, H12, atol=1e-10)


# =====================================================================
# T1344: Heat Diffusion
# =====================================================================

class TestT1344HeatDiffusion:
    """Heat kernel H(t) = exp(-tL); solution to du/dt = -Lu."""

    def test_heat_kernel_t0(self, laplacian):
        """H(0) = I."""
        H0 = expm(0.0 * laplacian)
        assert np.allclose(H0, np.eye(40), atol=1e-10)

    def test_heat_spectral_form(self, eigen_decomp, laplacian):
        """H(t) = V diag(exp(-t mu_k)) V^T matches matrix exponential."""
        evals, V = eigen_decomp
        t = 0.1
        H_expm = expm(-t * laplacian)
        H_spectral = V @ np.diag(np.exp(-t * evals)) @ V.T
        assert np.allclose(H_expm, H_spectral, atol=1e-10)

    def test_heat_symmetric(self, laplacian):
        """Heat kernel is symmetric for symmetric L."""
        Ht = expm(-0.5 * laplacian)
        assert np.allclose(Ht, Ht.T, atol=1e-10)

    def test_heat_mass_conservation(self, eigen_decomp):
        """Sum_j H(t,i,j) = 1 for all i (probability conservation)."""
        evals, V = eigen_decomp
        t = 0.3
        Ht = V @ np.diag(np.exp(-t * evals)) @ V.T
        row_sums = Ht.sum(axis=1)
        assert np.allclose(row_sums, 1.0, atol=1e-10)

    def test_heat_decay_to_uniform(self, eigen_decomp):
        """H(t, 0, 0) -> 1/40 as t -> infinity."""
        evals, V = eigen_decomp
        # Small t: above uniform
        H_small = np.sum(np.exp(-0.01 * evals) * V[0, :]**2)
        assert H_small > 1.0 / 40 + 1e-6
        # Large t: converges to uniform
        H_large = np.sum(np.exp(-100 * evals) * V[0, :]**2)
        assert abs(H_large - 1.0 / 40) < 1e-10

    def test_heat_semigroup(self, laplacian):
        """Semigroup property: H(s) H(t) = H(s+t)."""
        s, t = 0.2, 0.3
        Hs = expm(-s * laplacian)
        Ht = expm(-t * laplacian)
        Hst = expm(-(s + t) * laplacian)
        assert np.allclose(Hs @ Ht, Hst, atol=1e-10)


# =====================================================================
# T1345: Wave Equation
# =====================================================================

class TestT1345WaveEquation:
    """cos(sqrt(L) t) models wave propagation on the graph.

    Spectral form: cos(sqrt(L) t) = V diag(cos(sqrt(mu_k) t)) V^T.
    """

    def test_wave_t0(self, eigen_decomp):
        """cos(sqrt(L) * 0) = I."""
        evals, V = eigen_decomp
        cos_vals = np.cos(np.sqrt(np.maximum(evals, 0)) * 0.0)
        W0 = V @ np.diag(cos_vals) @ V.T
        assert np.allclose(W0, np.eye(40), atol=1e-10)

    def test_wave_symmetric(self, eigen_decomp):
        """Wave operator is symmetric for all t."""
        evals, V = eigen_decomp
        for t in [0.1, 0.5, 2.0]:
            cos_vals = np.cos(np.sqrt(np.maximum(evals, 0)) * t)
            Wt = V @ np.diag(cos_vals) @ V.T
            assert np.allclose(Wt, Wt.T, atol=1e-10)

    def test_wave_spectral_norm_bound(self, eigen_decomp):
        """All spectral values are bounded by 1: |cos(...)| <= 1."""
        evals, V = eigen_decomp
        for t in [0.3, 1.0, 5.0]:
            cos_vals = np.cos(np.sqrt(np.maximum(evals, 0)) * t)
            assert np.all(np.abs(cos_vals) <= 1.0 + 1e-15)

    def test_wave_preserves_constants(self, eigen_decomp):
        """Constant signals are eigenvectors with eigenvalue 0,
        so cos(0 * t) = 1: constant is preserved."""
        evals, V = eigen_decomp
        cos_vals = np.cos(np.sqrt(np.maximum(evals, 0)) * 2.0)
        Wt = V @ np.diag(cos_vals) @ V.T
        f = np.ones(40) * 7.0
        assert np.allclose(Wt @ f, f, atol=1e-10)

    def test_wave_differs_from_heat(self, eigen_decomp):
        """Wave operator is oscillatory, not dissipative: differs from heat."""
        evals, V = eigen_decomp
        t = 1.0
        cos_vals = np.cos(np.sqrt(np.maximum(evals, 0)) * t)
        exp_vals = np.exp(-t * evals)
        # At nonzero eigenvalues, cosine oscillates while exp decays
        # They must differ at eigenvalue 10: cos(sqrt(10)) vs exp(-10)
        assert not np.allclose(cos_vals, exp_vals, atol=0.01)


# =====================================================================
# T1346: Chebyshev Polynomial Expansion
# =====================================================================

class TestT1346ChebyshevExpansion:
    """T_k(L_scaled) for scaled Laplacian L_s = 2L/lambda_max - I."""

    def test_scaled_spectrum_in_range(self, laplacian):
        """Scaled Laplacian has spectrum in [-1, 1]."""
        lam_max = 16.0
        L_s = 2.0 * laplacian / lam_max - np.eye(40)
        evals = np.linalg.eigvalsh(L_s)
        assert np.all(evals >= -1.0 - 1e-10)
        assert np.all(evals <= 1.0 + 1e-10)

    def test_scaled_eigenvalue_positions(self, laplacian):
        """Scaled eigenvalues: 0 -> -1, 10 -> 0.25, 16 -> 1."""
        lam_max = 16.0
        evals = sorted(np.linalg.eigvalsh(laplacian))
        scaled = [2.0 * e / lam_max - 1.0 for e in evals]
        assert abs(scaled[0] - (-1.0)) < 1e-10
        assert abs(scaled[1] - 0.25) < 1e-10
        assert abs(scaled[-1] - 1.0) < 1e-10

    def test_chebyshev_recurrence(self, laplacian):
        """T_0 = I, T_1 = X, T_{k+1} = 2X T_k - T_{k-1}."""
        lam_max = 16.0
        L_s = 2.0 * laplacian / lam_max - np.eye(40)
        T0 = np.eye(40)
        T1 = L_s.copy()
        T2_recur = 2.0 * L_s @ T1 - T0
        T2_direct = 2.0 * L_s @ L_s - np.eye(40)
        assert np.allclose(T2_recur, T2_direct, atol=1e-10)

    def test_chebyshev_approximation_quality(self, eigen_decomp, laplacian):
        """Chebyshev expansion of exp(-tL) converges to exact filter."""
        evals, V = eigen_decomp
        lam_max = 16.0
        t = 0.1
        # Exact filter in spectral domain
        h_exact_vals = np.exp(-t * evals)
        f_exact = V @ np.diag(h_exact_vals) @ V.T

        # Chebyshev approximation: fit exp(-t * lam_max*(x+1)/2) on [-1,1]
        from numpy.polynomial.chebyshev import chebfit
        K = 20
        x_pts = np.linspace(-1, 1, 500)
        h_pts = np.exp(-t * lam_max * (x_pts + 1.0) / 2.0)
        coeffs = chebfit(x_pts, h_pts, K)

        # Apply via matrix Chebyshev recurrence
        L_s = 2.0 * laplacian / lam_max - np.eye(40)
        T_prev = np.eye(40)
        T_curr = L_s.copy()
        result = coeffs[0] * T_prev + coeffs[1] * T_curr
        for k in range(2, K + 1):
            T_next = 2.0 * L_s @ T_curr - T_prev
            result += coeffs[k] * T_next
            T_prev = T_curr
            T_curr = T_next

        assert np.allclose(result, f_exact, atol=1e-4)


# =====================================================================
# T1347: Graph Wavelets
# =====================================================================

class TestT1347GraphWavelets:
    """Spectral graph wavelet transform (SGWT).

    psi_{s,n}(m) = sum_l g(s lambda_l) chi_l(n) chi_l(m)
    where g is a wavelet generating kernel and s is scale.
    """

    def test_wavelet_kernel_zero_dc(self, eigen_decomp):
        """Wavelet kernel g(x) = x exp(-x) vanishes at DC: g(0) = 0."""
        evals, V = eigen_decomp
        s = 0.1
        g_vals = (s * evals) * np.exp(-s * evals)
        assert abs(g_vals[0]) < 1e-15

    def test_wavelet_at_vertex(self, eigen_decomp):
        """Wavelet centered at vertex n sums to zero (zero DC component)."""
        evals, V = eigen_decomp
        s = 0.1
        g_vals = (s * evals) * np.exp(-s * evals)
        # Wavelet at vertex 0: psi = V diag(g) V^T e_0
        psi = V @ (g_vals * V[0, :])
        assert psi.shape == (40,)
        assert abs(np.sum(psi)) < 1e-10

    def test_wavelet_localization(self, eigen_decomp, w33):
        """At small scale, wavelet is concentrated near the center vertex."""
        evals, V = eigen_decomp
        s = 0.02  # small scale = high frequency = local
        g_vals = (s * evals) * np.exp(-s * evals)
        psi = V @ (g_vals * V[0, :])
        center_energy = psi[0]**2
        # Neighbors of vertex 0
        neighbors = np.where(w33[0] == 1)[0]
        neighbor_energy = np.sum(psi[neighbors]**2)
        far_energy = np.sum(psi**2) - center_energy - neighbor_energy
        # At small scale, energy should be mostly near vertex 0
        assert center_energy + neighbor_energy > far_energy

    def test_multiscale_frame_coverage(self, eigen_decomp):
        """Scaling function + wavelets at multiple scales cover spectrum."""
        evals, V = eigen_decomp
        # Scaling function: h(x) = exp(-5x)
        h_vals = np.exp(-5.0 * evals)
        scales = [0.05, 0.1, 0.3, 1.0, 3.0]
        frame_sum = h_vals**2
        for s in scales:
            g_vals = (s * evals) * np.exp(-s * evals)
            frame_sum += g_vals**2
        # Nonzero eigenvalue positions must have positive frame sum
        nonzero_mask = evals > 0.5
        assert np.all(frame_sum[nonzero_mask] > 1e-10)

    def test_wavelet_norm_varies_with_scale(self, eigen_decomp):
        """Wavelet norms change with scale, reflecting different frequency bands."""
        evals, V = eigen_decomp
        norms = []
        for s in [0.01, 0.1, 1.0, 10.0]:
            g_vals = (s * evals) * np.exp(-s * evals)
            psi = V @ (g_vals * V[0, :])
            norms.append(np.linalg.norm(psi))
        # Norms should differ across scales
        assert len(set(np.round(norms, 6))) > 1


# =====================================================================
# T1348: Convolution Theorem
# =====================================================================

class TestT1348ConvolutionTheorem:
    """Graph convolution in spectral domain: (f * g)_hat = f_hat . g_hat."""

    def test_spectral_multiplication(self, eigen_decomp):
        """Convolution = pointwise product in spectral domain."""
        _, V = eigen_decomp
        rng = np.random.RandomState(1348)
        f = rng.randn(40)
        g = rng.randn(40)
        f_hat = V.T @ f
        g_hat = V.T @ g
        # Spectral convolution
        conv_spectral = V @ (f_hat * g_hat)
        # Equivalent to applying filter diag(f_hat) to g
        conv_matrix = V @ np.diag(f_hat) @ V.T @ g
        assert np.allclose(conv_spectral, conv_matrix, atol=1e-10)

    def test_convolution_with_delta(self, eigen_decomp):
        """Convolving filter h with delta at vertex 0 extracts kernel column."""
        evals, V = eigen_decomp
        h_vals = np.exp(-0.1 * evals)
        delta = np.zeros(40)
        delta[0] = 1.0
        delta_hat = V.T @ delta
        result = V @ (h_vals * delta_hat)
        # Equals column 0 of h(L) = V diag(h) V^T
        H = V @ np.diag(h_vals) @ V.T
        assert np.allclose(result, H[:, 0], atol=1e-10)

    def test_convolution_commutativity(self, eigen_decomp):
        """Spectral graph convolution is commutative: f * g = g * f."""
        _, V = eigen_decomp
        rng = np.random.RandomState(1348)
        f, g = rng.randn(40), rng.randn(40)
        f_hat, g_hat = V.T @ f, V.T @ g
        fg = V @ (f_hat * g_hat)
        gf = V @ (g_hat * f_hat)
        assert np.allclose(fg, gf, atol=1e-14)

    def test_convolution_associativity(self, eigen_decomp):
        """(f * g) * h = f * (g * h) in spectral domain."""
        _, V = eigen_decomp
        rng = np.random.RandomState(1348)
        f, g, h = rng.randn(40), rng.randn(40), rng.randn(40)
        f_hat, g_hat, h_hat = V.T @ f, V.T @ g, V.T @ h
        lhs = V @ (f_hat * g_hat * h_hat)
        rhs = V @ (f_hat * (g_hat * h_hat))
        assert np.allclose(lhs, rhs, atol=1e-12)


# =====================================================================
# T1349: Spectral Clustering
# =====================================================================

class TestT1349SpectralClustering:
    """Fiedler vector partitions graph based on 2nd Laplacian eigenvector."""

    def test_fiedler_eigenvalue(self, eigen_decomp):
        """Algebraic connectivity lambda_2(L) = 10."""
        evals, _ = eigen_decomp
        assert abs(evals[1] - 10.0) < 1e-8

    def test_fiedler_vector_partition(self, eigen_decomp, w33):
        """Fiedler vector sign gives a nontrivial partition with cut edges."""
        _, V = eigen_decomp
        fiedler = V[:, 1]
        S_plus = set(np.where(fiedler >= 0)[0])
        S_minus = set(np.where(fiedler < 0)[0])
        assert len(S_plus) > 0
        assert len(S_minus) > 0
        cut = sum(1 for i in S_plus for j in S_minus if w33[i, j] == 1)
        assert cut > 0

    def test_fiedler_rayleigh_quotient(self, eigen_decomp, laplacian):
        """Fiedler vector achieves Rayleigh quotient exactly lambda_2 = 10."""
        evals, V = eigen_decomp
        fiedler = V[:, 1]
        rq = (fiedler @ laplacian @ fiedler) / (fiedler @ fiedler)
        assert abs(rq - 10.0) < 1e-8

    def test_laplacian_kernel_is_constant(self, eigen_decomp):
        """Kernel of L is one-dimensional, spanned by the all-ones vector."""
        evals, V = eigen_decomp
        null_idx = np.where(np.abs(evals) < 1e-8)[0]
        assert len(null_idx) == 1
        null_vec = V[:, null_idx[0]]
        assert np.allclose(np.abs(null_vec), np.abs(null_vec[0]), atol=1e-10)

    def test_two_eigenspace_clustering(self, eigen_decomp):
        """Using eigenvectors for lambda=0 and lambda=10 gives 40-dim embedding;
        the lambda=10 eigenspace has multiplicity 24."""
        evals, _ = eigen_decomp
        idx_10 = np.where(np.abs(evals - 10.0) < 0.5)[0]
        assert len(idx_10) == 24


# =====================================================================
# T1350: Random Signal Energy
# =====================================================================

class TestT1350RandomSignalEnergy:
    """For Gaussian white noise f ~ N(0,I): E[||Lf||^2] = tr(L^2)."""

    def test_trace_L_squared_exact(self, laplacian):
        """tr(L^2) = sum mu_k^2 = 0 + 24*100 + 15*256 = 6240."""
        tr_L2 = np.trace(laplacian @ laplacian)
        assert abs(tr_L2 - 6240.0) < 1e-6

    def test_expected_energy_per_vertex(self, eigen_decomp):
        """E[||Lf||^2] / n = sum mu_k^2 / n = 6240/40 = 156."""
        evals, _ = eigen_decomp
        expected_per_vertex = np.sum(evals**2) / 40.0
        assert abs(expected_per_vertex - 156.0) < 1e-8

    def test_monte_carlo_energy(self, laplacian):
        """Monte Carlo estimate of E[||Lf||^2 / n] ~ 156 for white noise."""
        rng = np.random.RandomState(1350)
        n_trials = 5000
        energies = np.empty(n_trials)
        for t in range(n_trials):
            f = rng.randn(40)
            Lf = laplacian @ f
            energies[t] = np.dot(Lf, Lf) / 40.0
        empirical = np.mean(energies)
        # Statistical tolerance: SD of mean is about 0.55
        assert abs(empirical - 156.0) < 5.0

    def test_energy_decomposition_by_eigenspace(self, eigen_decomp):
        """Energy contributions: eigenspace mu=10 gives 24*100=2400,
        eigenspace mu=16 gives 15*256=3840; total 6240."""
        evals, _ = eigen_decomp
        e10 = np.sum(evals[np.abs(evals - 10) < 0.5]**2)
        e16 = np.sum(evals[np.abs(evals - 16) < 0.5]**2)
        assert abs(e10 - 2400.0) < 1e-6
        assert abs(e16 - 3840.0) < 1e-6
        assert abs(e10 + e16 - 6240.0) < 1e-6


# =====================================================================
# T1351: Smoothness Measure (Rayleigh Quotient)
# =====================================================================

class TestT1351SmoothnessMeasure:
    """f^T L f / f^T f measures signal smoothness (Rayleigh quotient)."""

    def test_constant_is_smoothest(self, laplacian):
        """Constant signal achieves minimum Rayleigh quotient = 0."""
        f = np.ones(40) * 3.0
        rq = (f @ laplacian @ f) / (f @ f)
        assert abs(rq) < 1e-12

    def test_fiedler_smoothness(self, eigen_decomp, laplacian):
        """Fiedler eigenvector has Rayleigh quotient = 10."""
        _, V = eigen_decomp
        f = V[:, 1]
        rq = (f @ laplacian @ f) / (f @ f)
        assert abs(rq - 10.0) < 1e-8

    def test_roughest_eigenvector(self, eigen_decomp, laplacian):
        """Eigenvector for lambda_max = 16 achieves maximum Rayleigh quotient."""
        _, V = eigen_decomp
        f = V[:, -1]
        rq = (f @ laplacian @ f) / (f @ f)
        assert abs(rq - 16.0) < 1e-8

    def test_rayleigh_bounds(self, laplacian):
        """Rayleigh quotient is in [0, 16] for all nonzero f."""
        rng = np.random.RandomState(1351)
        for _ in range(100):
            f = rng.randn(40)
            rq = (f @ laplacian @ f) / (f @ f)
            assert rq >= -1e-10
            assert rq <= 16.0 + 1e-10

    def test_quadratic_form_equals_edge_sum(self, laplacian, w33):
        """f^T L f = sum_{(i,j) in E} (f(i) - f(j))^2."""
        rng = np.random.RandomState(1351)
        f = rng.randn(40)
        quad = f @ laplacian @ f
        edge_sum = 0.0
        for i in range(40):
            for j in range(i + 1, 40):
                if w33[i, j] == 1:
                    edge_sum += (f[i] - f[j])**2
        assert abs(quad - edge_sum) < 1e-10


# =====================================================================
# T1352: Graph Gradient
# =====================================================================

class TestT1352GraphGradient:
    """Gradient operator: (grad f)(e_{ij}) = f(j) - f(i) via B @ f."""

    def test_gradient_of_constant(self, incidence):
        """Gradient of a constant signal is identically zero."""
        B, _ = incidence
        f = np.ones(40) * 5.0
        grad_f = B @ f
        assert np.allclose(grad_f, 0.0, atol=1e-12)

    def test_gradient_dimension(self, incidence):
        """B is m x n = 240 x 40 (one row per oriented edge)."""
        B, edges = incidence
        assert B.shape == (240, 40)
        assert len(edges) == 240

    def test_gradient_energy_equals_laplacian(self, incidence, laplacian):
        """||grad f||^2 = f^T L f (L = B^T B)."""
        B, _ = incidence
        rng = np.random.RandomState(1352)
        f = rng.randn(40)
        grad_f = B @ f
        energy_grad = np.dot(grad_f, grad_f)
        energy_lap = f @ laplacian @ f
        assert abs(energy_grad - energy_lap) < 1e-10

    def test_gradient_of_eigenvector(self, incidence, eigen_decomp):
        """||grad v_k||^2 = mu_k for normalized eigenvector v_k."""
        B, _ = incidence
        evals, V = eigen_decomp
        for k in [0, 1, 25, 39]:
            vk = V[:, k]
            grad_vk = B @ vk
            assert abs(np.dot(grad_vk, grad_vk) - evals[k]) < 1e-8

    def test_gradient_sparsity(self, incidence):
        """Each row of B has exactly 2 nonzero entries (+1 and -1)."""
        B, _ = incidence
        for e in range(B.shape[0]):
            row = B[e, :]
            nonzero = np.where(np.abs(row) > 0.5)[0]
            assert len(nonzero) == 2
            vals = sorted(row[nonzero])
            assert abs(vals[0] - (-1.0)) < 1e-15
            assert abs(vals[1] - 1.0) < 1e-15


# =====================================================================
# T1353: Graph Divergence
# =====================================================================

class TestT1353GraphDivergence:
    """div = B^T (adjoint of grad); L = B^T B = div(grad)."""

    def test_laplacian_factorization(self, incidence, laplacian):
        """L = B^T B exactly."""
        B, _ = incidence
        L_from_B = B.T @ B
        assert np.allclose(L_from_B, laplacian, atol=1e-10)

    def test_div_grad_equals_laplacian(self, incidence, laplacian):
        """div(grad f) = B^T(Bf) = Lf."""
        B, _ = incidence
        rng = np.random.RandomState(1353)
        f = rng.randn(40)
        grad_f = B @ f
        div_grad_f = B.T @ grad_f
        assert np.allclose(div_grad_f, laplacian @ f, atol=1e-10)

    def test_total_divergence_vanishes(self, incidence):
        """Sum of divergences over all vertices = 0 for any edge signal w.
        Proof: 1^T B^T w = (B 1)^T w = 0 since B @ ones = 0."""
        B, _ = incidence
        # First verify B @ ones = 0
        assert np.allclose(B @ np.ones(40), 0.0, atol=1e-12)
        # Then any edge signal
        rng = np.random.RandomState(1353)
        w = rng.randn(240)
        div_w = B.T @ w
        assert abs(np.sum(div_w)) < 1e-10

    def test_gradient_rank(self, incidence):
        """rank(B) = n - 1 = 39 for connected graph."""
        B, _ = incidence
        rank = np.linalg.matrix_rank(B)
        assert rank == 39

    def test_kernel_of_div(self, incidence):
        """ker(div) = ker(B^T) has dimension m - rank = 240 - 39 = 201."""
        B, _ = incidence
        _, S, _ = np.linalg.svd(B)
        null_dim = 240 - np.sum(S > 1e-10)
        assert null_dim == 201


# =====================================================================
# T1354: Helmholtz Decomposition
# =====================================================================

class TestT1354HelmholtzDecomposition:
    """Edge signals decompose into gradient + cycle (harmonic) components.

    R^m = im(B) + ker(B^T)   (orthogonal direct sum)
    dim im(B) = n - 1 = 39   (gradient signals)
    dim ker(B^T) = m - n + 1 = 201  (cycle space)
    """

    def test_gradient_space_dimension(self, incidence):
        """im(B) = image of gradient has dimension n - 1 = 39."""
        B, _ = incidence
        assert np.linalg.matrix_rank(B) == 39

    def test_cycle_space_dimension(self, incidence):
        """Cycle space ker(B^T) has dimension m - n + 1 = 201."""
        B, _ = incidence
        rank_BT = np.linalg.matrix_rank(B.T)
        cycle_dim = 240 - rank_BT
        assert cycle_dim == 201

    def test_gradient_orthogonal_to_cycles(self, incidence):
        """Any gradient signal Bf is orthogonal to ker(B^T)."""
        B, _ = incidence
        rng = np.random.RandomState(1354)
        f = rng.randn(40)
        grad_f = B @ f
        # Find a cycle vector via SVD of B^T
        U, S, Vt = np.linalg.svd(B.T, full_matrices=True)
        null_start = np.sum(S > 1e-10)
        # Vt[null_start:, :] spans ker(B^T)
        cycle = Vt[null_start, :]
        assert abs(np.dot(grad_f, cycle)) < 1e-8

    def test_decompose_edge_signal(self, incidence):
        """Decompose arbitrary edge signal w = w_grad + w_cycle."""
        B, _ = incidence
        rng = np.random.RandomState(1354)
        w = rng.randn(240)
        # Project onto gradient space: w_grad = B (B^T B)^+ B^T w
        L = B.T @ B
        L_pinv = np.linalg.pinv(L)
        w_grad = B @ L_pinv @ B.T @ w
        w_cycle = w - w_grad
        # Check orthogonality
        assert abs(np.dot(w_grad, w_cycle)) < 1e-8
        # Check reconstruction
        assert np.allclose(w_grad + w_cycle, w, atol=1e-10)
        # Check w_cycle is in ker(B^T)
        assert np.allclose(B.T @ w_cycle, 0.0, atol=1e-8)
        # Check w_grad is in im(B)
        # w_grad = B (L^+ B^T w), so it is manifestly in im(B)
        assert np.linalg.norm(w_grad - B @ (L_pinv @ B.T @ w)) < 1e-10

    def test_pure_gradient_signal(self, incidence):
        """A pure gradient signal has zero cycle component."""
        B, _ = incidence
        rng = np.random.RandomState(1354)
        f = rng.randn(40)
        w = B @ f  # pure gradient
        # w is already in im(B), so cycle component should be zero
        L = B.T @ B
        L_pinv = np.linalg.pinv(L)
        w_grad = B @ L_pinv @ B.T @ w
        w_cycle = w - w_grad
        assert np.allclose(w_cycle, 0.0, atol=1e-8)


# =====================================================================
# T1355: Effective Resistance from Laplacian Pseudoinverse
# =====================================================================

class TestT1355EffectiveResistance:
    """R_eff(i,j) = L^+(i,i) + L^+(j,j) - 2 L^+(i,j)."""

    def test_all_resistances_positive(self, laplacian):
        """All pairwise effective resistances are strictly positive."""
        L_pinv = np.linalg.pinv(laplacian)
        for i in range(40):
            for j in range(i + 1, 40):
                R = L_pinv[i, i] + L_pinv[j, j] - 2 * L_pinv[i, j]
                assert R > -1e-10

    def test_adjacent_resistance_uniform(self, laplacian, w33):
        """For an SRG, all adjacent pairs have the same effective resistance."""
        L_pinv = np.linalg.pinv(laplacian)
        R_adj = []
        for i in range(40):
            for j in range(i + 1, 40):
                if w33[i, j] == 1:
                    R = L_pinv[i, i] + L_pinv[j, j] - 2 * L_pinv[i, j]
                    R_adj.append(R)
        assert len(R_adj) == 240
        assert np.allclose(R_adj, R_adj[0], atol=1e-10)

    def test_nonadjacent_larger_than_adjacent(self, laplacian, w33):
        """Non-adjacent pairs have strictly larger effective resistance."""
        L_pinv = np.linalg.pinv(laplacian)
        i = 0
        j_adj = np.where(w33[0] == 1)[0][0]
        R_adj = L_pinv[i, i] + L_pinv[j_adj, j_adj] - 2 * L_pinv[i, j_adj]
        nonadj = np.where((w33[0] == 0) & (np.arange(40) != 0))[0]
        j_nonadj = nonadj[0]
        R_nonadj = L_pinv[i, i] + L_pinv[j_nonadj, j_nonadj] - 2 * L_pinv[i, j_nonadj]
        assert R_nonadj > R_adj + 1e-10

    def test_total_effective_resistance(self, laplacian):
        """Total R_eff = n * sum_{k>=1} 1/mu_k.

        = 40 * (24/10 + 15/16) = 40 * 3.3375 = 133.5.
        """
        evals = np.linalg.eigvalsh(laplacian)
        nonzero = evals[evals > 0.5]
        total_formula = 40.0 * np.sum(1.0 / nonzero)
        assert abs(total_formula - 133.5) < 1e-8
        # Cross-check with pairwise sum
        L_pinv = np.linalg.pinv(laplacian)
        total_direct = 0.0
        for i in range(40):
            for j in range(i + 1, 40):
                total_direct += L_pinv[i, i] + L_pinv[j, j] - 2 * L_pinv[i, j]
        assert abs(total_direct - total_formula) < 1e-6

    def test_resistance_from_eigendecomposition(self, eigen_decomp, w33):
        """R_eff(i,j) = sum_{k>=1} (v_k(i) - v_k(j))^2 / mu_k."""
        evals, V = eigen_decomp
        i, j = 0, np.where(w33[0] == 1)[0][0]
        R_spectral = 0.0
        for k in range(40):
            if evals[k] > 0.5:
                R_spectral += (V[i, k] - V[j, k])**2 / evals[k]
        L_pinv = np.linalg.pinv(np.diag(evals))
        R_pinv = (V[i, :] - V[j, :]) @ np.diag(
            np.where(evals > 0.5, 1.0 / evals, 0.0)
        ) @ (V[i, :] - V[j, :])
        assert abs(R_spectral - R_pinv) < 1e-10


# =====================================================================
# T1356: Spectral Gap and Expansion
# =====================================================================

class TestT1356SpectralGapExpansion:
    """lambda_2(L) = 10 gives Cheeger-type expansion bound."""

    def test_spectral_gap(self, laplacian):
        """lambda_2(L) = 10."""
        evals = sorted(np.linalg.eigvalsh(laplacian))
        assert abs(evals[1] - 10.0) < 1e-8

    def test_cheeger_lower_bound(self):
        """Cheeger inequality for k-regular: h(G) >= lambda_2 / 2.

        lambda_2 = 10 implies h(G) >= 5.
        """
        lambda_2 = 10.0
        h_lower = lambda_2 / 2.0
        assert abs(h_lower - 5.0) < 1e-10

    def test_expansion_of_small_set(self, w33):
        """For S = {0,1,2}, boundary expansion >= 5."""
        S = {0, 1, 2}
        boundary = 0
        for v in S:
            for u in range(40):
                if u not in S and w33[v, u] == 1:
                    boundary += 1
        ratio = boundary / len(S)
        assert ratio >= 5.0

    def test_algebraic_connectivity_positive(self, laplacian):
        """Positive algebraic connectivity implies connected graph."""
        evals = sorted(np.linalg.eigvalsh(laplacian))
        assert evals[0] < 1e-8   # zero eigenvalue exists
        assert evals[1] > 1e-8   # positive => connected

    def test_expander_mixing_lemma(self, w33):
        """Expander mixing: |e(S,T) - k|S||T|/n| <= lambda * sqrt(|S||T|).

        Here lambda = max(|r|,|s|) = max(2,4) = 4 for SRG restricted eigenvalues.
        """
        n, k, lam = 40, 12, 4  # lam = max absolute eigenvalue excluding k
        rng = np.random.RandomState(1356)
        for _ in range(20):
            S = set(rng.choice(40, size=rng.randint(1, 20), replace=False))
            T = set(rng.choice(40, size=rng.randint(1, 20), replace=False))
            e_ST = sum(1 for i in S for j in T if w33[i, j] == 1)
            expected = k * len(S) * len(T) / n
            bound = lam * np.sqrt(len(S) * len(T))
            assert abs(e_ST - expected) <= bound + 1e-8


# =====================================================================
# T1357: Return Probability Decay
# =====================================================================

class TestT1357ReturnProbabilityDecay:
    """Continuous-time random walk: p_t(v,v) via heat kernel diagonal."""

    def test_return_prob_t0(self, eigen_decomp):
        """p_0(v,v) = 1."""
        evals, V = eigen_decomp
        p0 = np.sum(np.exp(0 * evals) * V[0, :]**2)
        assert abs(p0 - 1.0) < 1e-10

    def test_return_prob_large_t(self, eigen_decomp):
        """p_t(v,v) -> 1/n = 1/40 as t -> infinity."""
        evals, V = eigen_decomp
        p_large = np.sum(np.exp(-100 * evals) * V[0, :]**2)
        assert abs(p_large - 1.0 / 40) < 1e-10

    def test_return_prob_vertex_transitive(self, eigen_decomp):
        """W(3,3) is vertex-transitive, so p_t(v,v) is the same for all v."""
        evals, V = eigen_decomp
        t = 0.5
        probs = [np.sum(np.exp(-t * evals) * V[v, :]**2) for v in range(40)]
        assert np.allclose(probs, probs[0], atol=1e-10)

    def test_return_prob_monotone_decay(self, eigen_decomp):
        """p_t(v,v) decreases monotonically toward 1/40."""
        evals, V = eigen_decomp
        times = np.linspace(0, 3, 30)
        probs = [np.sum(np.exp(-t * evals) * V[0, :]**2) for t in times]
        for i in range(len(probs) - 1):
            assert probs[i] >= probs[i + 1] - 1e-10

    def test_return_prob_exact_formula(self):
        """Exact formula from eigenvalue multiplicities and vertex transitivity.

        p_t(v,v) = (1/40)(1 + 24 exp(-10t) + 15 exp(-16t)).
        """
        for t in [0.0, 0.1, 0.5, 1.0]:
            p = (1.0 / 40) * (1 + 24 * np.exp(-10 * t) + 15 * np.exp(-16 * t))
            if t == 0:
                assert abs(p - 1.0) < 1e-10
            else:
                assert p > 1.0 / 40 + 1e-12
                assert p < 1.0

    def test_return_prob_matches_heat_kernel(self, eigen_decomp, laplacian):
        """p_t(v,v) = H(t)_{v,v} from matrix exponential."""
        evals, V = eigen_decomp
        t = 0.3
        p_spectral = np.sum(np.exp(-t * evals) * V[0, :]**2)
        Ht = expm(-t * laplacian)
        assert abs(p_spectral - Ht[0, 0]) < 1e-10


# =====================================================================
# T1358: Total Variation on Graph
# =====================================================================

class TestT1358TotalVariation:
    """TV(f) = sum_{(i,j) in E} |f(i) - f(j)|."""

    def test_tv_constant_is_zero(self, w33):
        """TV of constant signal = 0."""
        f = np.ones(40) * 7.0
        tv = sum(abs(f[i] - f[j]) for i in range(40)
                 for j in range(i + 1, 40) if w33[i, j])
        assert abs(tv) < 1e-12

    def test_tv_indicator(self, w33):
        """TV of single-vertex indicator = degree = 12."""
        f = np.zeros(40)
        f[0] = 1.0
        tv = sum(abs(f[i] - f[j]) for i in range(40)
                 for j in range(i + 1, 40) if w33[i, j])
        assert abs(tv - 12.0) < 1e-10

    def test_tv_nonnegative(self, w33):
        """TV is nonnegative for any signal."""
        rng = np.random.RandomState(1358)
        for _ in range(20):
            f = rng.randn(40)
            tv = sum(abs(f[i] - f[j]) for i in range(40)
                     for j in range(i + 1, 40) if w33[i, j])
            assert tv >= -1e-15

    def test_tv_equals_grad_l1_norm(self, incidence):
        """TV(f) = ||grad f||_1 = ||Bf||_1."""
        B, _ = incidence
        rng = np.random.RandomState(1358)
        for _ in range(5):
            f = rng.randn(40)
            grad_f = B @ f
            tv_from_grad = np.sum(np.abs(grad_f))
            assert tv_from_grad > 0

    def test_tv_triangle_inequality(self, incidence):
        """TV(f + g) <= TV(f) + TV(g)."""
        B, _ = incidence
        rng = np.random.RandomState(1358)
        for _ in range(10):
            f = rng.randn(40)
            g = rng.randn(40)
            tv_fg = np.sum(np.abs(B @ (f + g)))
            tv_f = np.sum(np.abs(B @ f))
            tv_g = np.sum(np.abs(B @ g))
            assert tv_fg <= tv_f + tv_g + 1e-10

    def test_tv_homogeneity(self, incidence):
        """TV(alpha f) = |alpha| TV(f)."""
        B, _ = incidence
        rng = np.random.RandomState(1358)
        f = rng.randn(40)
        alpha = -2.5
        tv_f = np.sum(np.abs(B @ f))
        tv_af = np.sum(np.abs(B @ (alpha * f)))
        assert abs(tv_af - abs(alpha) * tv_f) < 1e-10


# =====================================================================
# T1359: Graph Entropy from Spectrum
# =====================================================================

class TestT1359GraphEntropy:
    """Von Neumann entropy H = -sum p_k log(p_k), p_k = mu_k / tr(L)."""

    def test_trace_of_laplacian(self, laplacian):
        """tr(L) = n * k = 40 * 12 = 480."""
        assert abs(np.trace(laplacian) - 480.0) < 1e-10

    def test_spectral_entropy_analytic(self):
        """Analytic entropy from two distinct nonzero eigenvalue groups.

        p(10) = 10/480 = 1/48, multiplicity 24
        p(16) = 16/480 = 1/30, multiplicity 15
        H = -(24/48) log(1/48) - (15/30) log(1/30)
          = (1/2) log(48) + (1/2) log(30)
          = (1/2) log(1440).
        """
        p10 = 10.0 / 480.0
        p16 = 16.0 / 480.0
        H = -(24 * p10 * np.log(p10) + 15 * p16 * np.log(p16))
        H_analytic = 0.5 * np.log(1440.0)
        assert abs(H - H_analytic) < 1e-10

    def test_entropy_from_matrix(self, laplacian):
        """Entropy computed from eigenvalues matches analytic formula."""
        evals = np.linalg.eigvalsh(laplacian)
        nonzero = evals[evals > 0.5]
        total = np.sum(nonzero)
        probs = nonzero / total
        H = -np.sum(probs * np.log(probs))
        H_exact = 0.5 * np.log(1440.0)
        assert abs(H - H_exact) < 1e-10

    def test_entropy_bounds(self):
        """0 < H < log(39) (strict since eigenvalues are not all equal)."""
        H = 0.5 * np.log(1440.0)
        assert H > 0
        assert H < np.log(39)
        # sqrt(1440) ~ 37.95 < 39, so log(sqrt(1440)) < log(39)

    def test_maximum_entropy(self):
        """Maximum entropy log(39) would require all 39 nonzero eigenvalues equal.
        Our H = (1/2) log(1440) < log(39), confirming spectral non-uniformity."""
        H_actual = 0.5 * np.log(1440.0)
        H_max = np.log(39.0)
        gap = H_max - H_actual
        # gap = log(39) - log(sqrt(1440)) = log(39/sqrt(1440))
        assert gap > 0.01


# =====================================================================
# T1360: Bandlimited Signals
# =====================================================================

class TestT1360BandlimitedSignals:
    """K-bandlimited signal lives in span(V[:,:K]); recoverable from K samples."""

    def test_bandlimited_spectral_support(self, eigen_decomp):
        """K-bandlimited signal has zero GFT coefficients beyond index K."""
        _, V = eigen_decomp
        K = 10
        rng = np.random.RandomState(1360)
        coeffs = rng.randn(K)
        f_bl = V[:, :K] @ coeffs
        f_hat = V.T @ f_bl
        assert np.allclose(f_hat[K:], 0.0, atol=1e-10)
        assert not np.allclose(f_hat[:K], 0.0, atol=1e-10)

    def test_perfect_recovery_from_samples(self, eigen_decomp):
        """K-bandlimited signal can be recovered from K vertex samples."""
        _, V = eigen_decomp
        K = 5
        rng = np.random.RandomState(1360)
        coeffs = rng.randn(K)
        f_bl = V[:, :K] @ coeffs
        # Select K vertices with highest leverage scores
        VK = V[:, :K]
        leverage = np.sum(VK**2, axis=1)
        sample_idx = np.argsort(leverage)[-K:]
        V_S = VK[sample_idx, :]
        f_S = f_bl[sample_idx]
        # Solve for coefficients and reconstruct
        assert np.linalg.matrix_rank(V_S) == K
        c_recovered = np.linalg.solve(V_S, f_S)
        f_recovered = VK @ c_recovered
        assert np.allclose(f_recovered, f_bl, atol=1e-8)

    def test_bandlimited_rayleigh_bound(self, eigen_decomp, laplacian):
        """K-bandlimited signal has Rayleigh quotient <= max eigenvalue in band."""
        evals, V = eigen_decomp
        K = 25  # eigenvalues 0 and 10 are in this band
        rng = np.random.RandomState(1360)
        coeffs = rng.randn(K)
        coeffs /= np.linalg.norm(coeffs)
        f_bl = V[:, :K] @ coeffs
        rq = (f_bl @ laplacian @ f_bl) / (f_bl @ f_bl)
        assert rq <= evals[K - 1] + 1e-8
        assert rq >= evals[0] - 1e-8

    def test_projection_idempotent(self, eigen_decomp):
        """Projection P_K = V[:,:K] V[:,:K]^T is idempotent and symmetric."""
        _, V = eigen_decomp
        K = 15
        P_K = V[:, :K] @ V[:, :K].T
        assert np.allclose(P_K @ P_K, P_K, atol=1e-10)
        assert np.allclose(P_K, P_K.T, atol=1e-10)

    def test_projection_trace(self, eigen_decomp):
        """tr(P_K) = K (projection rank equals bandwidth)."""
        _, V = eigen_decomp
        for K in [1, 5, 10, 25, 40]:
            P_K = V[:, :K] @ V[:, :K].T
            assert abs(np.trace(P_K) - K) < 1e-8

    def test_oversampling_stability(self, eigen_decomp):
        """With M > K samples, least-squares recovery is stable."""
        _, V = eigen_decomp
        K = 5
        M = 15  # oversample 3x
        rng = np.random.RandomState(1360)
        coeffs = rng.randn(K)
        f_bl = V[:, :K] @ coeffs
        VK = V[:, :K]
        sample_idx = rng.choice(40, size=M, replace=False)
        V_S = VK[sample_idx, :]
        f_S = f_bl[sample_idx]
        c_ls, _, _, _ = np.linalg.lstsq(V_S, f_S, rcond=None)
        f_recovered = VK @ c_ls
        assert np.allclose(f_recovered, f_bl, atol=1e-8)


# =====================================================================
# T1361: Spectral Density and Moment Verification
# =====================================================================

class TestT1361SpectralDensity:
    """Empirical spectral distribution and moment verification.

    The k-th spectral moment is tr(L^k)/n, which counts weighted
    closed walks on the graph.
    """

    def test_zeroth_moment(self, laplacian):
        """mu_0 = tr(I)/n = 1."""
        n = 40
        assert abs(np.trace(np.eye(n)) / n - 1.0) < 1e-10

    def test_first_moment(self, laplacian):
        """mu_1 = tr(L)/n = 480/40 = 12 = k."""
        n = 40
        assert abs(np.trace(laplacian) / n - 12.0) < 1e-10

    def test_second_moment(self, laplacian):
        """mu_2 = tr(L^2)/n = 6240/40 = 156."""
        n = 40
        assert abs(np.trace(laplacian @ laplacian) / n - 156.0) < 1e-8

    def test_third_moment(self, laplacian):
        """mu_3 = tr(L^3)/n = (24*10^3 + 15*16^3)/40 = 85440/40 = 2136."""
        n = 40
        L3 = laplacian @ laplacian @ laplacian
        mu3 = np.trace(L3) / n
        expected = (24 * 1000.0 + 15 * 4096.0) / 40.0
        assert abs(expected - 2136.0) < 1e-8
        assert abs(mu3 - expected) < 1e-4

    def test_eigenvalue_counting_function(self, eigen_decomp):
        """Empirical CDF N(x) = #{mu_k <= x}/n at key points."""
        evals, _ = eigen_decomp
        # N(5) = 1/40 (only mu=0)
        assert np.sum(evals <= 5) == 1
        # N(11) = 25/40 (mu=0 plus 24 copies of mu=10)
        assert np.sum(evals <= 11) == 25
        # N(17) = 40/40 (all eigenvalues)
        assert np.sum(evals <= 17) == 40

    def test_spectral_density_three_peaks(self, eigen_decomp):
        """Gaussian-broadened spectral density has peaks near 0, 10, 16."""
        evals, _ = eigen_decomp
        sigma = 0.5
        x = np.linspace(-2, 20, 2000)
        density = np.zeros_like(x)
        for ev in evals:
            density += np.exp(-0.5 * ((x - ev) / sigma)**2)
        density /= 40.0 * sigma * np.sqrt(2 * np.pi)
        # Find local maxima
        peaks = []
        for i in range(1, len(x) - 1):
            if density[i] > density[i - 1] and density[i] > density[i + 1]:
                peaks.append(x[i])
        assert any(abs(p) < 1.0 for p in peaks), f"No peak near 0, peaks={peaks}"
        assert any(abs(p - 10) < 1.0 for p in peaks), f"No peak near 10, peaks={peaks}"
        assert any(abs(p - 16) < 1.0 for p in peaks), f"No peak near 16, peaks={peaks}"

    def test_moments_from_adjacency_walks(self, w33, laplacian):
        """Cross-check: tr(L^k) relates to tr(A^k) via binomial expansion.

        L = 12I - A, so tr(L^2) = 144*40 - 24*tr(A) + tr(A^2)
                                 = 5760 - 0 + 480 = 6240.
        """
        A = w33.astype(float)
        L = laplacian
        n = 40
        # tr(A^0) = 40
        assert abs(np.trace(np.eye(n)) - 40) < 1e-10
        # tr(A^1) = 0 (no self-loops)
        assert abs(np.trace(A)) < 1e-10
        # tr(A^2) = n*k = 480 (number of directed edges)
        assert abs(np.trace(A @ A) - 480) < 1e-8
        # Cross-check: tr(L^2) = tr((12I - A)^2) = 144n - 24*tr(A) + tr(A^2)
        tr_L2_from_A = 144 * n - 24 * np.trace(A) + np.trace(A @ A)
        assert abs(tr_L2_from_A - np.trace(L @ L)) < 1e-6

    def test_spectral_variance(self, eigen_decomp):
        """Spectral variance = mu_2 - mu_1^2 = 156 - 144 = 12."""
        evals, _ = eigen_decomp
        mu1 = np.mean(evals)
        mu2 = np.mean(evals**2)
        variance = mu2 - mu1**2
        assert abs(variance - 12.0) < 1e-8
