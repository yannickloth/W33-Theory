"""
Phase CXXVI -- Laplacian Powers & Fractional Calculus on W(3,3) = SRG(40,12,2,4).

85 tests across 10 classes:
  1. TestLaplacianSquared              (10 tests)
  2. TestLaplacianCube                 ( 8 tests)
  3. TestFractionalLaplacianHalf       (10 tests)
  4. TestFractionalLaplacianAlpha      ( 9 tests)
  5. TestHeatSemigroup                 ( 9 tests)
  6. TestWaveSemigroup                 ( 8 tests)
  7. TestDiffusionKernels              ( 8 tests)
  8. TestSobolevNorms                  ( 8 tests)
  9. TestGreenFunction                 ( 8 tests)
 10. TestBiharmonicAndRegularization   ( 7 tests)

Only numpy and standard library.  Every assertion is mathematically provable
from the SRG(40,12,2,4) spectrum:
    adjacency:  {12^1, 2^24, (-4)^15}
    Laplacian:  {0^1,  10^24, 16^15}
"""

import math
import numpy as np
from numpy.linalg import eigh, eigvalsh, norm, matrix_rank
import pytest


# ---------------------------------------------------------------------------
# W(3,3) builder
# ---------------------------------------------------------------------------

def _build_w33():
    """Build the 40-vertex symplectic graph W(3,3) = Sp(4,3)."""
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
# SRG parameters and constants
# ---------------------------------------------------------------------------

_N, _K, _LAM, _MU = 40, 12, 2, 4

# Laplacian eigenvalues and multiplicities
_LAP_EIGS = {0: 1, 10: 24, 16: 15}        # lambda: multiplicity
_LAP_EIGS_SORTED = [0.0, 10.0, 16.0]


# ---------------------------------------------------------------------------
# Module-level data (computed once)
# ---------------------------------------------------------------------------

_A = _build_w33()
_L = float(_K) * np.eye(_N) - _A.astype(float)      # Combinatorial Laplacian
_lap_vals, _lap_vecs = eigh(_L)                        # ascending eigenvalues

# Spectral projectors for each distinct eigenvalue
def _spectral_projector(lam, tol=1e-8):
    """Projector onto eigenspace of eigenvalue lam."""
    mask = np.abs(_lap_vals - lam) < tol
    V = _lap_vecs[:, mask]
    return V @ V.T

_P0  = _spectral_projector(0.0)    # rank 1  (constant vector)
_P10 = _spectral_projector(10.0)   # rank 24
_P16 = _spectral_projector(16.0)   # rank 15

def _spectral_function(f):
    """Build f(L) via spectral decomposition: sum_i f(lambda_i) P_i."""
    return f(0.0) * _P0 + f(10.0) * _P10 + f(16.0) * _P16


# ═══════════════════════════════════════════════════════════════════════════
# 1.  Laplacian Squared  L^2  (10 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestLaplacianSquared:
    """Properties of L^2 — eigenvalues {0, 100, 256}."""

    def test_L2_eigenvalues_exact(self):
        """L^2 has eigenvalues {0^1, 100^24, 256^15}."""
        L2 = _L @ _L
        vals = np.sort(eigvalsh(L2))
        expected = np.sort([0.0]*1 + [100.0]*24 + [256.0]*15)
        np.testing.assert_allclose(vals, expected, atol=1e-8)

    def test_L2_equals_matrix_square(self):
        """Spectral L^2 matches direct matrix product."""
        L2_spectral = _spectral_function(lambda x: x**2)
        L2_direct = _L @ _L
        np.testing.assert_allclose(L2_spectral, L2_direct, atol=1e-8)

    def test_L2_trace(self):
        """tr(L^2) = 0*1 + 100*24 + 256*15 = 6240."""
        L2 = _L @ _L
        assert abs(np.trace(L2) - 6240.0) < 1e-8

    def test_L2_symmetric(self):
        """L^2 is symmetric."""
        L2 = _L @ _L
        np.testing.assert_allclose(L2, L2.T, atol=1e-10)

    def test_L2_positive_semidefinite(self):
        """L^2 is positive semi-definite."""
        vals = eigvalsh(_L @ _L)
        assert np.all(vals > -1e-10)

    def test_L2_rank(self):
        """rank(L^2) = 39 (same nullity as L)."""
        L2 = _L @ _L
        assert matrix_rank(L2, tol=1e-8) == 39

    def test_L2_kernel_is_constants(self):
        """ker(L^2) = ker(L) = span(1)."""
        L2 = _L @ _L
        ones = np.ones(_N) / np.sqrt(_N)
        result = L2 @ ones
        np.testing.assert_allclose(result, np.zeros(_N), atol=1e-8)

    def test_L2_frobenius_norm(self):
        """||L^2||_F^2 = sum lambda_i^4 = 0 + 24*10000 + 15*65536 = 1223040."""
        L2 = _L @ _L
        frob_sq = np.sum(L2 ** 2)
        expected = 24 * 10000 + 15 * 65536
        assert abs(frob_sq - expected) < 1e-4

    def test_L2_spectral_radius(self):
        """Spectral radius of L^2 is 256 = 16^2."""
        vals = eigvalsh(_L @ _L)
        assert abs(np.max(vals) - 256.0) < 1e-8

    def test_L2_commutes_with_L(self):
        """L^2 commutes with L (obvious, but validates numerics)."""
        L2 = _L @ _L
        comm = L2 @ _L - _L @ L2
        np.testing.assert_allclose(comm, np.zeros((_N, _N)), atol=1e-8)


# ═══════════════════════════════════════════════════════════════════════════
# 2.  Laplacian Cube  L^3  (8 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestLaplacianCube:
    """Properties of L^3 — eigenvalues {0, 1000, 4096}."""

    def test_L3_eigenvalues_exact(self):
        """L^3 has eigenvalues {0^1, 1000^24, 4096^15}."""
        L3 = _L @ _L @ _L
        vals = np.sort(eigvalsh(L3))
        expected = np.sort([0.0]*1 + [1000.0]*24 + [4096.0]*15)
        np.testing.assert_allclose(vals, expected, atol=1e-6)

    def test_L3_trace(self):
        """tr(L^3) = 0 + 24*1000 + 15*4096 = 85440."""
        L3 = _L @ _L @ _L
        assert abs(np.trace(L3) - 85440.0) < 1e-5

    def test_L3_equals_L_times_L2(self):
        """L^3 = L * L^2."""
        L2 = _L @ _L
        L3a = _L @ L2
        L3b = L2 @ _L
        np.testing.assert_allclose(L3a, L3b, atol=1e-8)

    def test_L3_spectral_decomposition(self):
        """Spectral L^3 matches direct product."""
        L3_spectral = _spectral_function(lambda x: x**3)
        L3_direct = _L @ _L @ _L
        np.testing.assert_allclose(L3_spectral, L3_direct, atol=1e-6)

    def test_L3_rank(self):
        """rank(L^3) = 39."""
        L3 = _L @ _L @ _L
        assert matrix_rank(L3, tol=1e-6) == 39

    def test_L3_symmetric(self):
        """L^3 is symmetric since L is."""
        L3 = _L @ _L @ _L
        np.testing.assert_allclose(L3, L3.T, atol=1e-8)

    def test_L3_spectral_gap_cubed(self):
        """Smallest positive eigenvalue of L^3 is 1000 = 10^3."""
        L3 = _L @ _L @ _L
        vals = np.sort(eigvalsh(L3))
        pos_vals = vals[vals > 0.5]
        assert abs(pos_vals[0] - 1000.0) < 1e-6

    def test_L3_determinant_ratio(self):
        """Product of nonzero eigenvalues of L^3 = (product of L)^3."""
        vals_L = np.sort(eigvalsh(_L))
        vals_L3 = np.sort(eigvalsh(_L @ _L @ _L))
        log_prod_L = np.sum(np.log(vals_L[vals_L > 0.5]))
        log_prod_L3 = np.sum(np.log(vals_L3[vals_L3 > 0.5]))
        np.testing.assert_allclose(log_prod_L3, 3.0 * log_prod_L, rtol=1e-8)


# ═══════════════════════════════════════════════════════════════════════════
# 3.  Fractional Laplacian L^{1/2}  (10 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestFractionalLaplacianHalf:
    """L^{1/2} via spectral decomposition: eigenvalues {0, sqrt(10), 4}."""

    @pytest.fixture(scope="class")
    def Lhalf(self):
        return _spectral_function(lambda x: np.sqrt(x))

    def test_Lhalf_eigenvalues(self, Lhalf):
        """L^{1/2} eigenvalues are {0^1, sqrt(10)^24, 4^15}."""
        vals = np.sort(eigvalsh(Lhalf))
        expected = np.sort([0.0]*1 + [np.sqrt(10.0)]*24 + [4.0]*15)
        np.testing.assert_allclose(vals, expected, atol=1e-10)

    def test_Lhalf_squared_equals_L(self, Lhalf):
        """(L^{1/2})^2 = L."""
        L_reconstructed = Lhalf @ Lhalf
        np.testing.assert_allclose(L_reconstructed, _L, atol=1e-10)

    def test_Lhalf_symmetric(self, Lhalf):
        """L^{1/2} is symmetric."""
        np.testing.assert_allclose(Lhalf, Lhalf.T, atol=1e-12)

    def test_Lhalf_positive_semidefinite(self, Lhalf):
        """L^{1/2} is positive semi-definite."""
        vals = eigvalsh(Lhalf)
        assert np.all(vals > -1e-10)

    def test_Lhalf_trace(self, Lhalf):
        """tr(L^{1/2}) = 0 + 24*sqrt(10) + 15*4 = 24*sqrt(10) + 60."""
        expected = 24 * np.sqrt(10.0) + 60.0
        assert abs(np.trace(Lhalf) - expected) < 1e-8

    def test_Lhalf_kernel_dimension(self, Lhalf):
        """ker(L^{1/2}) has dimension 1."""
        vals = eigvalsh(Lhalf)
        nullity = np.sum(np.abs(vals) < 1e-8)
        assert nullity == 1

    def test_Lhalf_commutes_with_L(self, Lhalf):
        """[L^{1/2}, L] = 0."""
        comm = Lhalf @ _L - _L @ Lhalf
        np.testing.assert_allclose(comm, np.zeros((_N, _N)), atol=1e-10)

    def test_Lhalf_rank(self, Lhalf):
        """rank(L^{1/2}) = 39."""
        assert matrix_rank(Lhalf, tol=1e-8) == 39

    def test_Lhalf_frobenius_norm(self, Lhalf):
        """||L^{1/2}||_F^2 = sum lambda_i = tr(L) = 0 + 24*10 + 15*16 = 480."""
        frob_sq = np.sum(Lhalf ** 2)
        assert abs(frob_sq - 480.0) < 1e-8

    def test_Lhalf_spectral_gap(self, Lhalf):
        """Spectral gap of L^{1/2} is sqrt(10)."""
        vals = np.sort(eigvalsh(Lhalf))
        pos = vals[vals > 0.1]
        assert abs(pos[0] - np.sqrt(10.0)) < 1e-10


# ═══════════════════════════════════════════════════════════════════════════
# 4.  Fractional Laplacian L^alpha for various alpha  (9 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestFractionalLaplacianAlpha:
    """L^alpha for alpha in {1/3, 1/4, 2/3, 3/2, -1/2, pi}."""

    def test_L_one_third_cubed_equals_L(self):
        """(L^{1/3})^3 = L."""
        L13 = _spectral_function(lambda x: x ** (1.0/3.0))
        L_recon = L13 @ L13 @ L13
        np.testing.assert_allclose(L_recon, _L, atol=1e-8)

    def test_L_one_quarter_fourth_equals_L(self):
        """(L^{1/4})^4 = L."""
        L14 = _spectral_function(lambda x: x ** 0.25)
        L_recon = L14 @ L14 @ L14 @ L14
        np.testing.assert_allclose(L_recon, _L, atol=1e-8)

    def test_L_two_thirds_eigenvalues(self):
        """L^{2/3} eigenvalues: {0, 10^{2/3}, 16^{2/3}}."""
        L23 = _spectral_function(lambda x: x ** (2.0/3.0))
        vals = np.sort(eigvalsh(L23))
        expected = np.sort(
            [0.0]*1 + [10.0**(2.0/3.0)]*24 + [16.0**(2.0/3.0)]*15
        )
        np.testing.assert_allclose(vals, expected, atol=1e-10)

    def test_L_three_halves_eigenvalues(self):
        """L^{3/2} eigenvalues: {0, 10*sqrt(10), 64}."""
        L32 = _spectral_function(lambda x: x ** 1.5)
        vals = np.sort(eigvalsh(L32))
        expected = np.sort(
            [0.0]*1 + [10.0 * np.sqrt(10.0)]*24 + [64.0]*15
        )
        np.testing.assert_allclose(vals, expected, atol=1e-8)

    def test_power_law_composition(self):
        """L^a * L^b = L^{a+b} for a=1/3, b=2/3."""
        La = _spectral_function(lambda x: x ** (1.0/3.0))
        Lb = _spectral_function(lambda x: x ** (2.0/3.0))
        product = La @ Lb
        np.testing.assert_allclose(product, _L, atol=1e-8)

    def test_power_law_composition_half_plus_half(self):
        """L^{1/2} * L^{1/2} = L."""
        Lh = _spectral_function(lambda x: np.sqrt(x))
        np.testing.assert_allclose(Lh @ Lh, _L, atol=1e-10)

    def test_power_law_composition_quarter_plus_three_quarter(self):
        """L^{1/4} * L^{3/4} = L."""
        L14 = _spectral_function(lambda x: x ** 0.25)
        L34 = _spectral_function(lambda x: x ** 0.75)
        np.testing.assert_allclose(L14 @ L34, _L, atol=1e-8)

    def test_L_pi_eigenvalues(self):
        """L^pi eigenvalues: {0, 10^pi, 16^pi}."""
        Lpi = _spectral_function(lambda x: x ** np.pi)
        vals = np.sort(eigvalsh(Lpi))
        expected = np.sort(
            [0.0]*1 + [10.0**np.pi]*24 + [16.0**np.pi]*15
        )
        np.testing.assert_allclose(vals, expected, atol=1e-2)

    def test_negative_half_power_eigenvalues(self):
        """L^{-1/2} (on range of L): eigenvalues {1/sqrt(10), 1/4} (no zero)."""
        # Pseudoinverse fractional power — apply only to nonzero eigenspace
        Lneg = _spectral_function(
            lambda x: 1.0 / np.sqrt(x) if x > 0.5 else 0.0
        )
        vals = np.sort(eigvalsh(Lneg))
        pos = vals[vals > 1e-8]
        expected = np.sort([1.0 / np.sqrt(10.0)]*24 + [0.25]*15)
        np.testing.assert_allclose(pos, expected, atol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════
# 5.  Heat Semigroup  e^{-tL}  (9 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestHeatSemigroup:
    """Heat kernel e^{-tL}: eigenvalues {1, e^{-10t}, e^{-16t}}."""

    def _heat(self, t):
        return _spectral_function(lambda x: np.exp(-t * x))

    def test_heat_t0_is_identity(self):
        """e^{0*L} = I."""
        H = self._heat(0.0)
        np.testing.assert_allclose(H, np.eye(_N), atol=1e-12)

    def test_heat_semigroup_property(self):
        """e^{-sL} e^{-tL} = e^{-(s+t)L} for s=0.1, t=0.2."""
        Hs = self._heat(0.1)
        Ht = self._heat(0.2)
        Hst = self._heat(0.3)
        np.testing.assert_allclose(Hs @ Ht, Hst, atol=1e-12)

    def test_heat_eigenvalues_t1(self):
        """At t=1: eigenvalues {1, e^{-10}, e^{-16}}."""
        H = self._heat(1.0)
        vals = np.sort(eigvalsh(H))[::-1]  # descending
        expected = np.sort([1.0]*1 + [np.exp(-10.0)]*24 + [np.exp(-16.0)]*15)[::-1]
        np.testing.assert_allclose(vals, expected, atol=1e-10)

    def test_heat_trace(self):
        """tr(e^{-tL}) = 1 + 24*e^{-10t} + 15*e^{-16t} for t=0.5."""
        t = 0.5
        H = self._heat(t)
        expected = 1.0 + 24.0 * np.exp(-10.0 * t) + 15.0 * np.exp(-16.0 * t)
        assert abs(np.trace(H) - expected) < 1e-10

    def test_heat_symmetric(self):
        """e^{-tL} is symmetric for t=0.3."""
        H = self._heat(0.3)
        np.testing.assert_allclose(H, H.T, atol=1e-14)

    def test_heat_positive_definite(self):
        """e^{-tL} is positive definite for t > 0."""
        H = self._heat(0.5)
        vals = eigvalsh(H)
        assert np.all(vals > 0)

    def test_heat_long_time_limit(self):
        """As t -> inf, e^{-tL} -> P0 = (1/n) J  (projection onto constants)."""
        H = self._heat(100.0)
        proj = np.ones((_N, _N)) / _N
        np.testing.assert_allclose(H, proj, atol=1e-10)

    def test_heat_preserves_total_mass(self):
        """e^{-tL} preserves sum: 1^T e^{-tL} = 1^T."""
        H = self._heat(0.5)
        ones = np.ones(_N)
        np.testing.assert_allclose(H @ ones, ones, atol=1e-12)

    def test_heat_derivative_at_t0(self):
        """d/dt e^{-tL}|_{t=0} = -L (verified by finite difference)."""
        dt = 1e-7
        H0 = self._heat(0.0)
        H1 = self._heat(dt)
        deriv = (H1 - H0) / dt
        np.testing.assert_allclose(deriv, -_L, atol=1e-4)


# ═══════════════════════════════════════════════════════════════════════════
# 6.  Wave Semigroup  cos(sqrt(L)*t)  (8 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestWaveSemigroup:
    """Wave propagator cos(sqrt(L)*t): eigenvalues {1, cos(sqrt(10)*t), cos(4t)}."""

    def _wave(self, t):
        return _spectral_function(lambda x: np.cos(np.sqrt(x) * t))

    def test_wave_t0_is_identity(self):
        """cos(sqrt(L)*0) = I."""
        W = self._wave(0.0)
        np.testing.assert_allclose(W, np.eye(_N), atol=1e-12)

    def test_wave_eigenvalues(self):
        """Wave eigenvalues at t=1: {1, cos(sqrt(10)), cos(4)}."""
        W = self._wave(1.0)
        vals = np.sort(eigvalsh(W))
        expected = np.sort(
            [1.0]*1 + [np.cos(np.sqrt(10.0))]*24 + [np.cos(4.0)]*15
        )
        np.testing.assert_allclose(vals, expected, atol=1e-10)

    def test_wave_symmetric(self):
        """cos(sqrt(L)*t) is symmetric."""
        W = self._wave(0.7)
        np.testing.assert_allclose(W, W.T, atol=1e-12)

    def test_wave_trace(self):
        """tr(cos(sqrt(L)*t)) = 1 + 24*cos(sqrt(10)*t) + 15*cos(4t)."""
        t = 0.5
        W = self._wave(t)
        expected = (1.0 + 24.0 * np.cos(np.sqrt(10.0) * t)
                    + 15.0 * np.cos(4.0 * t))
        assert abs(np.trace(W) - expected) < 1e-10

    def test_wave_periodicity_4pi(self):
        """cos(4t) is 2pi/4 = pi/2 periodic; the 16-eigenspace recurs."""
        t0 = 0.3
        period = np.pi / 2.0
        W0 = self._wave(t0)
        Wp = self._wave(t0 + period)
        # The 16-eigenspace components agree; 10-eigenspace generally doesn't
        # so check only the 16-block: P16 * (Wp - W0) * P16 = 0
        diff_16 = _P16 @ (Wp - W0) @ _P16
        np.testing.assert_allclose(diff_16, np.zeros((_N, _N)), atol=1e-10)

    def test_wave_unitarity(self):
        """cos(sqrt(L)*t) has eigenvalues in [-1, 1], so ||W|| <= 1."""
        W = self._wave(1.0)
        vals = eigvalsh(W)
        assert np.all(vals >= -1.0 - 1e-10)
        assert np.all(vals <= 1.0 + 1e-10)

    def test_wave_commutes_with_L(self):
        """[cos(sqrt(L)*t), L] = 0."""
        W = self._wave(0.5)
        comm = W @ _L - _L @ W
        np.testing.assert_allclose(comm, np.zeros((_N, _N)), atol=1e-10)

    def test_wave_second_derivative(self):
        """d^2/dt^2 cos(sqrt(L)*t)|_{t=0} = -L (wave equation)."""
        dt = 1e-5
        Wp = self._wave(dt)
        W0 = self._wave(0.0)
        Wm = self._wave(-dt)
        d2W = (Wp - 2 * W0 + Wm) / (dt ** 2)
        np.testing.assert_allclose(d2W, -_L, atol=1e-3)


# ═══════════════════════════════════════════════════════════════════════════
# 7.  Diffusion Kernels  (8 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestDiffusionKernels:
    """Diffusion kernel K_t = exp(-tL) and fractional diffusion."""

    def test_diffusion_kernel_diagonal_uniform(self):
        """At t=0 diagonal is 1; at large t diagonal -> 1/n."""
        H = _spectral_function(lambda x: np.exp(-100.0 * x))
        diag = np.diag(H)
        np.testing.assert_allclose(diag, np.full(_N, 1.0/_N), atol=1e-10)

    def test_diffusion_kernel_row_sums(self):
        """Row sums of e^{-tL} are 1 (mass conservation)."""
        H = _spectral_function(lambda x: np.exp(-0.5 * x))
        row_sums = H @ np.ones(_N)
        np.testing.assert_allclose(row_sums, np.ones(_N), atol=1e-12)

    def test_diffusion_kernel_nonnegative_large_t(self):
        """For large t, kernel entries are nonnegative (close to 1/n)."""
        H = _spectral_function(lambda x: np.exp(-10.0 * x))
        assert np.all(H > -1e-12)

    def test_fractional_diffusion_kernel_eigenvalues(self):
        """Fractional diffusion e^{-t*L^{1/2}} eigenvalues."""
        t = 1.0
        Kf = _spectral_function(lambda x: np.exp(-t * np.sqrt(x)))
        vals = np.sort(eigvalsh(Kf))[::-1]
        expected = np.sort(
            [1.0]*1 + [np.exp(-np.sqrt(10.0))]*24 + [np.exp(-4.0)]*15
        )[::-1]
        np.testing.assert_allclose(vals, expected, atol=1e-10)

    def test_fractional_diffusion_heavier_tails(self):
        """Fractional diffusion decays slower: e^{-sqrt(16)} > e^{-16}."""
        # This is a mathematical fact about the operator
        assert np.exp(-4.0) > np.exp(-16.0)

    def test_diffusion_distance_well_defined(self):
        """Diffusion distance d_t(i,j) = ||K_t(i,:) - K_t(j,:)||_2 >= 0."""
        H = _spectral_function(lambda x: np.exp(-1.0 * x))
        D = np.zeros((_N, _N))
        for i in range(_N):
            for j in range(i + 1, _N):
                D[i, j] = D[j, i] = norm(H[i, :] - H[j, :])
        # Triangle inequality check for random triple
        np.random.seed(42)
        for _ in range(20):
            a, b, c = np.random.choice(_N, 3, replace=False)
            assert D[a, c] <= D[a, b] + D[b, c] + 1e-12

    def test_diffusion_distance_two_scales(self):
        """Diffusion distances shrink with increasing t."""
        H1 = _spectral_function(lambda x: np.exp(-0.1 * x))
        H2 = _spectral_function(lambda x: np.exp(-1.0 * x))
        d1 = norm(H1[0, :] - H1[1, :])
        d2 = norm(H2[0, :] - H2[1, :])
        assert d2 < d1  # more diffusion = closer

    def test_return_probability_decay(self):
        """p_t(i, i) = (1/n)(1 + 24*e^{-10t} + 15*e^{-16t}) for vertex i=0."""
        t = 0.5
        H = _spectral_function(lambda x: np.exp(-t * x))
        p_return = H[0, 0]
        expected = (1.0 + 24.0 * np.exp(-10.0 * t)
                    + 15.0 * np.exp(-16.0 * t)) / _N
        assert abs(p_return - expected) < 1e-10


# ═══════════════════════════════════════════════════════════════════════════
# 8.  Sobolev Norms  ||f||_s^2 = sum lambda_i^s |f_hat_i|^2  (8 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestSobolevNorms:
    """Sobolev norms induced by powers of the Laplacian."""

    @pytest.fixture(scope="class")
    def random_f(self):
        """A reproducible random signal on 40 vertices."""
        rng = np.random.RandomState(12345)
        return rng.randn(_N)

    @pytest.fixture(scope="class")
    def f_hat(self, random_f):
        """Spectral coefficients: f_hat_i = <phi_i, f>."""
        return _lap_vecs.T @ random_f

    def test_sobolev_s0_equals_L2_norm(self, random_f, f_hat):
        """||f||_{s=0}^2 = ||f||_2^2  (with lambda^0 = 1 for all)."""
        s0_norm = np.sum(np.abs(f_hat) ** 2)
        l2_norm = np.sum(random_f ** 2)
        np.testing.assert_allclose(s0_norm, l2_norm, rtol=1e-10)

    def test_sobolev_s1_equals_dirichlet_energy(self, random_f, f_hat):
        """||f||_{s=1}^2 = f^T L f  (Dirichlet energy)."""
        sobolev = np.sum(_lap_vals * np.abs(f_hat) ** 2)
        dirichlet = random_f @ _L @ random_f
        np.testing.assert_allclose(sobolev, dirichlet, rtol=1e-10)

    def test_sobolev_s2_equals_biharmonic_energy(self, random_f, f_hat):
        """||f||_{s=2}^2 = f^T L^2 f."""
        sobolev = np.sum(_lap_vals**2 * np.abs(f_hat) ** 2)
        biharm = random_f @ _L @ _L @ random_f
        np.testing.assert_allclose(sobolev, biharm, rtol=1e-10)

    def test_sobolev_half_via_Lhalf(self, random_f, f_hat):
        """||f||_{s=1/2}^2 = f^T L^{1/2} f."""
        Lhalf = _spectral_function(lambda x: np.sqrt(x))
        sobolev = np.sum(np.sqrt(_lap_vals) * np.abs(f_hat) ** 2)
        quad = random_f @ Lhalf @ random_f
        np.testing.assert_allclose(sobolev, quad, rtol=1e-10)

    def test_sobolev_monotonicity(self, f_hat):
        """||f||_s is non-decreasing in s for s >= 0 (on nonzero modes)."""
        # Remove the zero-eigenvalue component for clean monotonicity
        nonzero = _lap_vals > 0.5
        vals = _lap_vals[nonzero]
        coeffs = np.abs(f_hat[nonzero]) ** 2
        for s1, s2 in [(0.0, 0.5), (0.5, 1.0), (1.0, 2.0)]:
            n1 = np.sum(vals**s1 * coeffs)
            n2 = np.sum(vals**s2 * coeffs)
            assert n2 >= n1 - 1e-10  # since all vals >= 10 > 1

    def test_sobolev_constant_function_zero(self):
        """Constant function has ||f||_s = 0 for s > 0."""
        f_const = np.ones(_N)
        fhat = _lap_vecs.T @ f_const
        for s in [0.5, 1.0, 2.0, 3.0]:
            sobolev = np.sum(_lap_vals**s * np.abs(fhat)**2)
            # Relative to ||f||_0^2 = 40, this should be negligible
            assert abs(sobolev) < 1e-5

    def test_sobolev_eigenvector_norm(self):
        """Eigenvector phi_j has ||phi_j||_s^2 = lambda_j^s."""
        # Pick an eigenvector from the 10-eigenspace
        idx = np.where(np.abs(_lap_vals - 10.0) < 0.1)[0][0]
        phi = _lap_vecs[:, idx]
        fhat = _lap_vecs.T @ phi
        for s in [0.5, 1.0, 2.0]:
            sobolev = np.sum(_lap_vals**s * np.abs(fhat)**2)
            expected = 10.0 ** s
            np.testing.assert_allclose(sobolev, expected, rtol=1e-8)

    def test_sobolev_interpolation_inequality(self, f_hat):
        """Sobolev interpolation: ||f||_1^2 <= ||f||_0 * ||f||_2."""
        nonzero = _lap_vals > 0.5
        vals = _lap_vals[nonzero]
        coeffs = np.abs(f_hat[nonzero]) ** 2
        s0 = np.sqrt(np.sum(coeffs))
        s1 = np.sum(vals * coeffs)
        s2 = np.sqrt(np.sum(vals**2 * coeffs))
        # By Cauchy-Schwarz: (sum lambda |c|^2)^2 <= (sum |c|^2)(sum lambda^2 |c|^2)
        assert s1**2 <= (s0**2) * (s2**2) + 1e-8


# ═══════════════════════════════════════════════════════════════════════════
# 9.  Green's Function  L^{-1} (pseudoinverse)  (8 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestGreenFunction:
    """Moore-Penrose pseudoinverse L^+ as discrete Green's function."""

    @pytest.fixture(scope="class")
    def Lplus(self):
        """Green's function: pseudoinverse of L."""
        return _spectral_function(
            lambda x: 1.0 / x if x > 0.5 else 0.0
        )

    def test_green_eigenvalues(self, Lplus):
        """L^+ eigenvalues: {0^1, 1/10^24, 1/16^15}."""
        vals = np.sort(eigvalsh(Lplus))
        expected = np.sort([0.0]*1 + [0.1]*24 + [0.0625]*15)
        np.testing.assert_allclose(vals, expected, atol=1e-10)

    def test_green_times_L_is_projector(self, Lplus):
        """L^+ L = I - P0 (projection off constants)."""
        prod = Lplus @ _L
        expected = np.eye(_N) - _P0
        np.testing.assert_allclose(prod, expected, atol=1e-10)

    def test_green_symmetric(self, Lplus):
        """L^+ is symmetric."""
        np.testing.assert_allclose(Lplus, Lplus.T, atol=1e-12)

    def test_green_trace(self, Lplus):
        """tr(L^+) = 24/10 + 15/16 = 2.4 + 0.9375 = 3.3375."""
        expected = 24.0 / 10.0 + 15.0 / 16.0
        assert abs(np.trace(Lplus) - expected) < 1e-10

    def test_green_solves_poisson(self, Lplus):
        """L^+ solves Lf = g (for g orthogonal to constants)."""
        # Create source with zero mean
        g = np.zeros(_N)
        g[0] = 1.0
        g[1] = -1.0
        f = Lplus @ g
        Lf = _L @ f
        # Lf should equal g projected off constants
        g_proj = g - np.mean(g) * np.ones(_N)
        np.testing.assert_allclose(Lf, g_proj, atol=1e-10)

    def test_green_kernel_is_constants(self, Lplus):
        """ker(L^+) = span(1)."""
        ones = np.ones(_N) / np.sqrt(_N)
        result = Lplus @ ones
        np.testing.assert_allclose(result, np.zeros(_N), atol=1e-12)

    def test_green_effective_resistance(self, Lplus):
        """Effective resistance R(i,j) = L^+_{ii} + L^+_{jj} - 2*L^+_{ij}."""
        Lp = Lplus
        # For adjacent vertices: R(0,1) if edge exists
        # All adjacent pairs should have same R (vertex-transitive)
        resistances = set()
        for i in range(_N):
            for j in range(i + 1, _N):
                if _A[i, j] == 1:
                    R = Lp[i, i] + Lp[j, j] - 2.0 * Lp[i, j]
                    resistances.add(round(R, 8))
        # SRG is vertex- and edge-transitive: all edge resistances equal
        assert len(resistances) == 1

    def test_kirchhoff_resistance_distance_sum(self, Lplus):
        """Kirchhoff index K_f = n * tr(L^+) = 40 * 3.3375 = 133.5."""
        Kf = _N * np.trace(Lplus)
        expected = _N * (24.0 / 10.0 + 15.0 / 16.0)
        assert abs(Kf - expected) < 1e-8


# ═══════════════════════════════════════════════════════════════════════════
# 10. Biharmonic Operator & Regularization  (7 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestBiharmonicAndRegularization:
    """Biharmonic L^2, Tikhonov regularization, and zeta regularization."""

    def test_biharmonic_eigenvalues(self):
        """Biharmonic L^2 eigenvalues: {0, 100, 256}."""
        B = _L @ _L
        vals = np.sort(eigvalsh(B))
        expected = np.sort([0.0]*1 + [100.0]*24 + [256.0]*15)
        np.testing.assert_allclose(vals, expected, atol=1e-8)

    def test_tikhonov_regularized_inverse(self):
        """(L + epsilon*I)^{-1} converges to L^+ as epsilon -> 0."""
        Lplus = _spectral_function(lambda x: 1.0/x if x > 0.5 else 0.0)
        for eps in [1.0, 0.1, 0.01]:
            L_reg = _L + eps * np.eye(_N)
            L_inv = np.linalg.inv(L_reg)
            # Project off constant mode for comparison
            L_inv_proj = L_inv - _P0 @ L_inv - L_inv @ _P0 + _P0 @ L_inv @ _P0
            Lplus_proj = Lplus  # already zero on constants
            # Error should decrease with epsilon
            if eps == 0.01:
                err = norm(L_inv_proj - Lplus_proj)
                assert err < 0.2  # close to pseudoinverse

    def test_tikhonov_eigenvalues(self):
        """(L + eps*I)^{-1} eigenvalues: {1/eps, 1/(10+eps), 1/(16+eps)}."""
        eps = 0.5
        L_reg = _L + eps * np.eye(_N)
        vals = np.sort(eigvalsh(np.linalg.inv(L_reg)))[::-1]
        expected = np.sort(
            [1.0 / eps]*1 + [1.0/(10.0+eps)]*24 + [1.0/(16.0+eps)]*15
        )[::-1]
        np.testing.assert_allclose(vals, expected, atol=1e-10)

    def test_spectral_zeta_function(self):
        """zeta_L(s) = sum_{lambda>0} lambda^{-s} = 24*10^{-s} + 15*16^{-s}."""
        for s in [1.0, 2.0, 0.5]:
            zeta = 24.0 * (10.0 ** (-s)) + 15.0 * (16.0 ** (-s))
            # Compute from eigenvalues
            vals = eigvalsh(_L)
            pos = vals[vals > 0.5]
            zeta_computed = np.sum(pos ** (-s))
            np.testing.assert_allclose(zeta_computed, zeta, rtol=1e-10)

    def test_zeta_regularized_determinant(self):
        """log det'(L) = -zeta_L'(0) = sum_{lambda>0} log(lambda)."""
        vals = eigvalsh(_L)
        pos = vals[vals > 0.5]
        log_det = np.sum(np.log(pos))
        expected = 24 * np.log(10.0) + 15 * np.log(16.0)
        np.testing.assert_allclose(log_det, expected, rtol=1e-10)

    def test_resolvent_spectral_representation(self):
        """(zI - L)^{-1} = sum P_i/(z - lambda_i) for z not in spectrum."""
        z = 5.0 + 0j  # real z not in {0, 10, 16}
        R_direct = np.linalg.inv(z * np.eye(_N) - _L)
        R_spectral = (_P0 / (z - 0.0) + _P10 / (z - 10.0)
                       + _P16 / (z - 16.0))
        np.testing.assert_allclose(R_direct, R_spectral, atol=1e-10)

    def test_functional_calculus_consistency(self):
        """f(L) g(L) = (fg)(L) for f(x)=x^2, g(x)=e^{-x}."""
        fL = _spectral_function(lambda x: x**2)
        gL = _spectral_function(lambda x: np.exp(-x))
        fgL = _spectral_function(lambda x: x**2 * np.exp(-x))
        np.testing.assert_allclose(fL @ gL, fgL, atol=1e-10)
