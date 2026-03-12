"""
Phase CVIII -- Random Matrix Theory Computation on W(3,3) = SRG(40,12,2,4).

81 tests across 8 classes:
  1. TestEigenvalueStatistics        (12 tests)
  2. TestSpectralRigidity            (10 tests)
  3. TestGaussianEnsembleComparison  (11 tests)
  4. TestNormalizedAdjacency         (10 tests)
  5. TestRandomPerturbation          (10 tests)
  6. TestMatrixFunctions             (10 tests)
  7. TestConcentrationInequalities   (10 tests)
  8. TestDeterministicVsRandom       ( 8 tests)

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
import collections
import numpy as np
import pytest


# ---------------------------------------------------------------------------
# W(3,3) builder  (exact copy from specification)
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
# Module-level data  (computed once)
# ---------------------------------------------------------------------------

_A = _build_w33()
_eigvals = np.sort(np.linalg.eigvalsh(_A.astype(float)))   # ascending
_n = 40
_k = 12


# ===================================================================
# 1.  Eigenvalue Statistics
# ===================================================================

class TestEigenvalueStatistics:
    """Level spacing, spacing ratios, unfolding, Wigner surmise."""

    def test_exact_eigenvalue_count(self):
        """Adjacency matrix has exactly n = 40 eigenvalues."""
        assert len(_eigvals) == _n

    def test_eigenvalue_multiplicities(self):
        """Spectrum is {-4^15, 2^24, 12^1}."""
        rounded = np.round(_eigvals).astype(int)
        counts = collections.Counter(rounded.tolist())
        assert counts[-4] == 15
        assert counts[2] == 24
        assert counts[12] == 1

    def test_eigenvalues_sorted_ascending(self):
        """Eigenvalues returned in non-decreasing order."""
        for i in range(_n - 1):
            assert _eigvals[i] <= _eigvals[i + 1] + 1e-10

    def test_level_spacings_count(self):
        """There are n - 1 = 39 level spacings s_i = lambda_{i+1} - lambda_i."""
        spacings = np.diff(_eigvals)
        assert len(spacings) == _n - 1

    def test_zero_spacing_count(self):
        """37 of 39 spacings are zero (14 inside the -4 block, 23 inside the 2 block)."""
        spacings = np.diff(_eigvals)
        zero_count = int(np.sum(np.abs(spacings) < 1e-8))
        assert zero_count == 37

    def test_nonzero_spacings_values(self):
        """Exactly 2 nonzero spacings: 6 (from -4 to 2) and 10 (from 2 to 12)."""
        spacings = np.diff(_eigvals)
        nonzero = np.sort(spacings[np.abs(spacings) > 1e-8])
        assert len(nonzero) == 2
        assert abs(nonzero[0] - 6.0) < 1e-8
        assert abs(nonzero[1] - 10.0) < 1e-8

    def test_mean_spacing(self):
        """Mean spacing = (12 - (-4)) / 39 = 16/39."""
        spacings = np.diff(_eigvals)
        assert abs(np.mean(spacings) - 16.0 / 39.0) < 1e-10

    def test_spacing_ratio_at_first_gap(self):
        """Spacing ratio r_i = min(s_i, s_{i+1})/max(s_i, s_{i+1}).
        At the -4 -> 2 gap: s_{13}=0, s_{14}=6, so r_{13} = 0."""
        spacings = np.diff(_eigvals)
        s_before = spacings[13]
        s_gap = spacings[14]
        denom = max(abs(s_before), abs(s_gap))
        r = min(abs(s_before), abs(s_gap)) / denom if denom > 1e-12 else 0.0
        assert abs(r) < 1e-8

    def test_spacing_ratio_at_second_gap(self):
        """At the 2 -> 12 gap: s_{37}=0, s_{38}=10, so r_{37} = 0."""
        spacings = np.diff(_eigvals)
        s_before = spacings[37]
        s_gap = spacings[38]
        denom = max(abs(s_before), abs(s_gap))
        r = min(abs(s_before), abs(s_gap)) / denom if denom > 1e-12 else 0.0
        assert abs(r) < 1e-8

    def test_degeneracy_fraction(self):
        """Fraction of zero spacings = 37/39 ~ 0.949,
        far from GOE where it would be 0 (level repulsion)."""
        spacings = np.diff(_eigvals)
        frac = np.sum(np.abs(spacings) < 1e-8) / len(spacings)
        assert abs(frac - 37.0 / 39.0) < 1e-10

    def test_spectral_density_three_atoms(self):
        """Empirical spectral measure has exactly 3 atoms."""
        rounded = np.round(_eigvals).astype(int)
        assert len(set(rounded.tolist())) == 3

    def test_integrated_density_jumps(self):
        """Integrated density N(E) = #{lambda_j <= E}/n jumps by 15/40, 24/40, 1/40
        at E = -4, 2, 12 respectively."""
        rounded = np.round(_eigvals).astype(int)
        assert int(np.sum(rounded <= -4)) == 15
        assert int(np.sum(rounded <= 2)) == 39
        assert int(np.sum(rounded <= 12)) == 40


# ===================================================================
# 2.  Spectral Rigidity
# ===================================================================

class TestSpectralRigidity:
    """Spectral form factor, number variance, pair correlation, Delta_3."""

    @staticmethod
    def _unfolded():
        """Rank-based unfolding: xi_i = i  (0-indexed) for sorted eigenvalues."""
        return np.arange(_n, dtype=float)

    def test_spectral_form_factor_at_zero(self):
        """K(0) = (1/n)|sum_j exp(0)|^2 = (1/n)*n^2 = n = 40."""
        tau = 0.0
        sff = np.abs(np.sum(np.exp(2j * np.pi * tau * _eigvals))) ** 2 / _n
        assert abs(sff - _n) < 1e-8

    def test_spectral_form_factor_nonnegative(self):
        """K(tau) >= 0 for all tau  (squared modulus)."""
        for tau in np.linspace(0, 2, 50):
            sff = np.abs(np.sum(np.exp(2j * np.pi * tau * _eigvals))) ** 2 / _n
            assert sff >= -1e-12

    def test_spectral_form_factor_symmetry(self):
        """K(tau) = K(-tau)  because all eigenvalues are real."""
        for tau in [0.1, 0.5, 1.0, 1.7]:
            k_pos = np.abs(np.sum(np.exp(2j * np.pi * tau * _eigvals))) ** 2 / _n
            k_neg = np.abs(np.sum(np.exp(-2j * np.pi * tau * _eigvals))) ** 2 / _n
            assert abs(k_pos - k_neg) < 1e-10

    def test_spectral_form_factor_integer_periodicity(self):
        """Eigenvalues are all integers, so exp(2*pi*i*(tau+1)*lambda) = exp(2*pi*i*tau*lambda).
        Therefore K(tau) has period 1."""
        for tau in [0.3, 0.7, 1.5]:
            k1 = np.abs(np.sum(np.exp(2j * np.pi * tau * _eigvals))) ** 2 / _n
            k2 = np.abs(np.sum(np.exp(2j * np.pi * (tau + 1.0) * _eigvals))) ** 2 / _n
            assert abs(k1 - k2) < 1e-8

    def test_spectral_form_factor_at_half_integer(self):
        """All eigenvalues are even (-4, 2, 12), so exp(i*pi*lambda) = 1 for every j.
        K(1/2) = (1/40)*40^2 = 40."""
        sff = np.abs(np.sum(np.exp(1j * np.pi * _eigvals))) ** 2 / _n
        assert abs(sff - _n) < 1e-8

    def test_number_variance_nonnegative(self):
        """Sigma^2(L) = Var_E[n(E,L)] >= 0 on the unfolded spectrum."""
        xi = self._unfolded()
        L = 5.0
        centers = np.linspace(0, _n - 1, 200)
        counts = np.array([np.sum((xi >= c - L / 2) & (xi < c + L / 2))
                           for c in centers])
        assert np.var(counts) >= -1e-12

    def test_number_variance_grows_with_L(self):
        """Sigma^2(L2) >= Sigma^2(L1) when L2 > L1 (for the rank-based unfolding
        the variance is non-decreasing because larger windows catch more of the
        boundary effects)."""
        xi = self._unfolded()
        centers = np.linspace(2, _n - 3, 200)

        def sigma2(L):
            counts = np.array([np.sum((xi >= c - L / 2) & (xi < c + L / 2))
                               for c in centers])
            return np.var(counts)

        assert sigma2(10.0) >= sigma2(3.0) - 1e-12

    def test_pair_correlation_distance_1(self):
        """On rank-based unfolded spectrum (xi_i = i), there are exactly n-1 = 39
        ordered pairs with |xi_i - xi_j| = 1."""
        xi = self._unfolded()
        pair_count = int(np.sum(np.abs(xi[:, None] - xi[None, :] - 1.0) < 0.01))
        assert pair_count == 39

    def test_delta3_nonnegative(self):
        """Delta_3(L) (least-squares fit of N(E) to a line) is >= 0."""
        xi = self._unfolded()
        L = 10.0
        center = _n / 2.0
        mask = (xi >= center - L / 2) & (xi < center + L / 2)
        xi_local = xi[mask]
        assert len(xi_local) >= 2
        N_local = np.arange(len(xi_local), dtype=float)
        A_fit = np.column_stack([xi_local, np.ones(len(xi_local))])
        coeffs, _, _, _ = np.linalg.lstsq(A_fit, N_local, rcond=None)
        residual = np.sum((N_local - A_fit @ coeffs) ** 2) / L
        assert residual >= -1e-12

    def test_spectral_compressibility_finite(self):
        """chi = Sigma^2(L) / L is finite and non-negative for finite L."""
        xi = self._unfolded()
        L = 15.0
        centers = np.linspace(3, _n - 4, 200)
        counts = np.array([np.sum((xi >= c - L / 2) & (xi < c + L / 2))
                           for c in centers])
        chi = np.var(counts) / L
        assert chi >= -1e-12
        assert np.isfinite(chi)


# ===================================================================
# 3.  Gaussian Ensemble Comparison
# ===================================================================

class TestGaussianEnsembleComparison:
    """Compare W(3,3) spectrum to GOE predictions and semicircle law."""

    def test_real_symmetric(self):
        """A is real symmetric  (GOE symmetry class beta = 1)."""
        assert np.allclose(_A, _A.T)

    def test_all_eigenvalues_real(self):
        """All eigenvalues are real  (Hermitian matrix theorem)."""
        eigvals_cmplx = np.linalg.eigvals(_A.astype(float))
        assert np.allclose(eigvals_cmplx.imag, 0, atol=1e-10)

    def test_eigenvalue_mean_zero(self):
        """Mean eigenvalue = tr(A)/n = 0  (zero diagonal adjacency matrix)."""
        assert abs(np.mean(_eigvals)) < 1e-10

    def test_eigenvalue_variance(self):
        """Var(lambda) = tr(A^2)/n - (tr(A)/n)^2 = 480/40 = 12."""
        assert abs(np.var(_eigvals) - 12.0) < 1e-8

    def test_eigenvalue_fourth_moment(self):
        """m_4 = (1/n) sum lambda^4 = (12^4 + 24*2^4 + 15*4^4)/40
        = (20736 + 384 + 3840)/40 = 24960/40 = 624."""
        assert abs(np.mean(_eigvals ** 4) - 624.0) < 1e-6

    def test_excess_kurtosis_positive(self):
        """Excess kurtosis = m4/m2^2 - 3 = 624/144 - 3 = 13/3 - 3 = 4/3 > 0.
        GOE semicircle kurtosis = 2 - 3 = -1.  Positive value shows non-GOE."""
        m2 = np.mean(_eigvals ** 2)
        m4 = np.mean(_eigvals ** 4)
        kurt = m4 / m2 ** 2 - 3.0
        assert abs(kurt - 4.0 / 3.0) < 1e-8
        assert kurt > 0

    def test_spectral_radius_equals_k(self):
        """Spectral radius rho(A) = max|lambda| = k = 12."""
        rho = max(abs(_eigvals[0]), abs(_eigvals[-1]))
        assert abs(rho - 12.0) < 1e-8

    def test_semicircle_outlier(self):
        """For A/sqrt(n), the semicircle support ~ [-2*sigma, 2*sigma] where sigma
        is the per-entry std.  The top eigenvalue 12/sqrt(40) ~ 1.90 exceeds this."""
        p = _k / (_n - 1.0)       # edge probability in complement view
        sigma = math.sqrt(p * (1 - p))
        R = 2.0 * sigma            # ~ 0.98
        top_scaled = _eigvals[-1] / math.sqrt(_n)
        assert top_scaled > R

    def test_nontrivial_inside_kesten_mckay_support(self):
        """Non-trivial eigenvalues {2, -4} lie within Kesten-McKay support
        [-2*sqrt(k-1), 2*sqrt(k-1)] = [-2*sqrt(11), 2*sqrt(11)] ~ [-6.633, 6.633]."""
        bound = 2.0 * math.sqrt(_k - 1.0)
        nontrivial = _eigvals[:-1]            # exclude largest (=k)
        assert np.all(np.abs(nontrivial) <= bound + 1e-8)

    def test_largest_eigenvalue_is_perron_outlier(self):
        """The largest eigenvalue 12 = k exceeds the Kesten-McKay support
        2*sqrt(k-1) ~ 6.633.  It is the Perron eigenvalue of a connected
        k-regular graph."""
        bound = 2.0 * math.sqrt(_k - 1.0)
        assert _eigvals[-1] > bound

    def test_goe_level_repulsion_absent(self):
        """GOE predicts P(s=0) = 0 (linear level repulsion).
        Our spectrum has 37/39 ~ 94.9 % of spacings at s = 0."""
        spacings = np.diff(_eigvals)
        frac_zero = np.sum(np.abs(spacings) < 1e-8) / len(spacings)
        assert frac_zero > 0.9


# ===================================================================
# 4.  Normalized Adjacency
# ===================================================================

class TestNormalizedAdjacency:
    """D^{-1/2} A D^{-1/2} = A/k  for k-regular graph."""

    @staticmethod
    def _normalized():
        return _A.astype(float) / _k

    def test_regular_normalization_identity(self):
        """For k-regular: D = kI, so D^{-1/2} A D^{-1/2} = A/k."""
        deg = np.sum(_A, axis=1)
        assert np.all(deg == _k)
        D_inv_sqrt = np.diag(1.0 / np.sqrt(deg.astype(float)))
        Anorm = D_inv_sqrt @ _A.astype(float) @ D_inv_sqrt
        assert np.allclose(Anorm, _A.astype(float) / _k)

    def test_normalized_spectrum(self):
        """Normalized spectrum = {(-1/3)^15, (1/6)^24, 1^1}."""
        eigs = np.sort(np.linalg.eigvalsh(self._normalized()))
        # Multiply by 6 to get integers for clean counting
        rounded6 = np.round(eigs * 6).astype(int)
        counts = collections.Counter(rounded6.tolist())
        assert counts[-2] == 15   # -1/3 * 6 = -2
        assert counts[1] == 24    #  1/6 * 6 =  1
        assert counts[6] == 1     #    1 * 6 =  6

    def test_spectral_gap(self):
        """Spectral gap = 1 - lambda_2(normalized) = 1 - 1/6 = 5/6."""
        eigs = np.sort(np.linalg.eigvalsh(self._normalized()))
        gap = eigs[-1] - eigs[-2]
        assert abs(gap - 5.0 / 6.0) < 1e-10

    def test_normalized_trace_zero(self):
        """tr(A/k) = tr(A)/k = 0."""
        assert abs(np.trace(self._normalized())) < 1e-10

    def test_normalized_frobenius_squared(self):
        """||A/k||_F^2 = tr(A^2)/k^2 = 480/144 = 10/3."""
        fro2 = np.sum(self._normalized() ** 2)
        assert abs(fro2 - 10.0 / 3.0) < 1e-10

    def test_normalized_eigenvalue_sum_zero(self):
        """Sum of normalized eigenvalues = 1 + 24/6 - 15/3 = 1 + 4 - 5 = 0."""
        eigs = np.linalg.eigvalsh(self._normalized())
        assert abs(np.sum(eigs)) < 1e-8

    def test_second_largest_eigenvalue(self):
        """lambda_2(A/k) = 1/6."""
        eigs = np.sort(np.linalg.eigvalsh(self._normalized()))
        assert abs(eigs[-2] - 1.0 / 6.0) < 1e-10

    def test_smallest_eigenvalue(self):
        """lambda_min(A/k) = -1/3."""
        eigs = np.sort(np.linalg.eigvalsh(self._normalized()))
        assert abs(eigs[0] - (-1.0 / 3.0)) < 1e-10

    def test_mixing_rate(self):
        """Mixing rate = max(|lambda_2|, |lambda_min|) of normalized = max(1/6, 1/3) = 1/3."""
        eigs = np.sort(np.linalg.eigvalsh(self._normalized()))
        mixing = max(abs(eigs[-2]), abs(eigs[0]))
        assert abs(mixing - 1.0 / 3.0) < 1e-10

    def test_random_walk_convergence(self):
        """(A/k)^m -> (1/n)*J  as m -> infinity.
        After m = 50 steps the mixing rate (1/3)^50 < 1e-23,
        so every entry should be within 1e-10 of 1/n."""
        eigs, V = np.linalg.eigh(self._normalized())
        m = 50
        Am = V @ np.diag(eigs ** m) @ V.T
        target = np.ones((_n, _n)) / _n
        assert np.allclose(Am, target, atol=1e-10)


# ===================================================================
# 5.  Random Perturbation
# ===================================================================

class TestRandomPerturbation:
    """Eigenvalue stability under perturbation; Weyl inequalities."""

    @staticmethod
    def _sym_perturbation(eps, seed=42):
        rng = np.random.RandomState(seed)
        E = rng.randn(_n, _n) * eps
        return (E + E.T) / 2.0

    def test_weyl_bound(self):
        """|lambda_i(A+E) - lambda_i(A)| <= ||E||_op  for every i."""
        E = self._sym_perturbation(0.01)
        eigs_pert = np.sort(np.linalg.eigvalsh(_A.astype(float) + E))
        E_op = np.linalg.norm(E, ord=2)
        assert np.all(np.abs(eigs_pert - _eigvals) <= E_op + 1e-10)

    def test_small_perturbation_preserves_gap(self):
        """With eps << smallest gap (=6), the three eigenvalue clusters stay separated."""
        E = self._sym_perturbation(0.1)
        eigs_pert = np.sort(np.linalg.eigvalsh(_A.astype(float) + E))
        gap_12 = eigs_pert[15] - eigs_pert[14]   # between -4 and 2 clusters
        assert gap_12 > 4.0

    def test_perturbation_lifts_degeneracy(self):
        """A generic symmetric perturbation splits the 24-fold degeneracy at lambda=2."""
        E = self._sym_perturbation(0.1)
        eigs_pert = np.sort(np.linalg.eigvalsh(_A.astype(float) + E))
        cluster = eigs_pert[15:39]
        assert np.max(np.abs(np.diff(cluster))) > 1e-6

    def test_perturbation_preserves_symmetry(self):
        """A + E remains symmetric."""
        E = self._sym_perturbation(0.1)
        B = _A.astype(float) + E
        assert np.allclose(B, B.T)

    def test_trace_perturbation_identity(self):
        """tr(A + E) = tr(A) + tr(E)  (linearity of trace)."""
        E = self._sym_perturbation(0.1)
        lhs = np.trace(_A.astype(float) + E)
        rhs = np.trace(_A.astype(float)) + np.trace(E)
        assert abs(lhs - rhs) < 1e-10

    def test_eigenvalue_sum_shift(self):
        """sum(lambda_i(A+E)) - sum(lambda_i(A)) = tr(E)."""
        E = self._sym_perturbation(0.1)
        eigs_pert = np.linalg.eigvalsh(_A.astype(float) + E)
        shift = np.sum(eigs_pert) - np.sum(_eigvals)
        assert abs(shift - np.trace(E)) < 1e-8

    def test_operator_norm_le_frobenius(self):
        """||E||_op <= ||E||_F  always."""
        E = self._sym_perturbation(0.1)
        assert np.linalg.norm(E, ord=2) <= np.linalg.norm(E, 'fro') + 1e-12

    def test_weyl_rank1_perturbation(self):
        """For rank-1 PSD perturbation vv^T, Weyl bound still holds."""
        rng = np.random.RandomState(99)
        v = rng.randn(_n) * 0.1
        E = np.outer(v, v)
        eigs_pert = np.sort(np.linalg.eigvalsh(_A.astype(float) + E))
        E_op = np.linalg.norm(E, ord=2)
        assert np.all(np.abs(eigs_pert - _eigvals) <= E_op + 1e-10)

    def test_spectral_radius_perturbation_bound(self):
        """rho(A + E) <= rho(A) + ||E||_op."""
        E = self._sym_perturbation(0.1)
        eigs_pert = np.linalg.eigvalsh(_A.astype(float) + E)
        rho_pert = np.max(np.abs(eigs_pert))
        E_op = np.linalg.norm(E, ord=2)
        assert rho_pert <= 12.0 + E_op + 1e-10

    def test_structural_gaps_exceed_perturbation(self):
        """For small eps, the SRG structural gaps (6 and 10) far exceed the
        maximum eigenvalue shift 2*||E||_op, showing structural stability."""
        E = self._sym_perturbation(0.01)
        E_op = np.linalg.norm(E, ord=2)
        assert 6.0 > 2 * E_op
        assert 10.0 > 2 * E_op


# ===================================================================
# 6.  Matrix Functions
# ===================================================================

class TestMatrixFunctions:
    """Resolvent, Green's function, Stieltjes transform, spectral density."""

    def test_resolvent_exists_off_spectrum(self):
        """(zI - A)^{-1} is well-defined for z not in {-4, 2, 12}."""
        z = 5.0
        M = z * np.eye(_n) - _A.astype(float)
        R = np.linalg.inv(M)
        assert np.allclose(R @ M, np.eye(_n), atol=1e-10)

    def test_resolvent_eigenvalues(self):
        """Eigenvalues of (zI - A)^{-1} are 1/(z - lambda_j)."""
        z = 7.0
        R = np.linalg.inv(z * np.eye(_n) - _A.astype(float))
        eigs_R = np.sort(np.linalg.eigvalsh(R))
        expected = np.sort(1.0 / (z - _eigvals))
        assert np.allclose(eigs_R, expected, atol=1e-8)

    def test_stieltjes_transform_consistency(self):
        """m(z) = (1/n) tr(R(z)) equals (1/n) sum 1/(z - lambda_j)."""
        z = 20.0
        R = np.linalg.inv(z * np.eye(_n) - _A.astype(float))
        m_trace = np.trace(R) / _n
        m_spectral = np.sum(1.0 / (z - _eigvals)) / _n
        assert abs(m_trace - m_spectral) < 1e-10

    def test_stieltjes_exact_value(self):
        """m(20) = (1/40)[1/8 + 24/18 + 15/24] = (1/40)(25/12) = 5/96."""
        m = np.sum(1.0 / (20.0 - _eigvals)) / _n
        assert abs(m - 5.0 / 96.0) < 1e-12

    def test_spectral_density_from_resolvent(self):
        """rho(E) = -(1/pi) Im[m(E + i*eps)].  Near E = 2 (mult 24) with eps = 0.1
        the density peaks at ~ 24/(n*pi*eps) = 6/pi."""
        eps = 0.1
        z = 2.0 + 1j * eps
        m_z = np.sum(1.0 / (z - _eigvals)) / _n
        rho = -m_z.imag / np.pi
        expected = 24.0 / (_n * np.pi * eps)
        assert abs(rho - expected) / expected < 0.01

    def test_resolvent_identity(self):
        """R(z1) - R(z2) = (z2 - z1) R(z1) R(z2)  (first resolvent identity)."""
        z1 = 5.0 + 1j
        z2 = 7.0 - 0.5j
        Ac = _A.astype(complex)
        R1 = np.linalg.inv(z1 * np.eye(_n, dtype=complex) - Ac)
        R2 = np.linalg.inv(z2 * np.eye(_n, dtype=complex) - Ac)
        lhs = R1 - R2
        rhs = (z2 - z1) * (R1 @ R2)
        assert np.allclose(lhs, rhs, atol=1e-8)

    def test_matrix_power_trace(self):
        """tr(A^k) = sum lambda_j^k  for k = 2, 3, 4, 5."""
        for k in [2, 3, 4, 5]:
            Ak = np.linalg.matrix_power(_A, k)
            tr_matrix = float(np.trace(Ak))
            tr_spectral = float(12 ** k + 24 * 2 ** k + 15 * (-4) ** k)
            assert abs(tr_matrix - tr_spectral) < 1e-4, f"k={k}"

    def test_matrix_exponential_trace(self):
        """tr(exp(tA)) = sum exp(t*lambda_j).
        For t = 0.1: exp(1.2) + 24*exp(0.2) + 15*exp(-0.4)."""
        t = 0.1
        eigs, V = np.linalg.eigh(_A.astype(float))
        expA = V @ np.diag(np.exp(t * eigs)) @ V.T
        tr_expA = np.trace(expA)
        expected = math.exp(1.2) + 24 * math.exp(0.2) + 15 * math.exp(-0.4)
        assert abs(tr_expA - expected) < 1e-8

    def test_log_det_from_spectrum(self):
        """log|det(zI - A)| = sum log|z - lambda_j|  for z off spectrum."""
        z = 8.0
        _, logdet = np.linalg.slogdet(z * np.eye(_n) - _A.astype(float))
        expected = np.sum(np.log(np.abs(z - _eigvals)))
        assert abs(logdet - expected) < 1e-8

    def test_green_function_diagonal_sum(self):
        """sum_i G_{ii}(z) = tr(R(z)) = sum 1/(z - lambda_j)."""
        z = 15.0
        R = np.linalg.inv(z * np.eye(_n) - _A.astype(float))
        diag_sum = np.sum(np.diag(R))
        spectral = np.sum(1.0 / (z - _eigvals))
        assert abs(diag_sum - spectral) < 1e-10


# ===================================================================
# 7.  Concentration Inequalities
# ===================================================================

class TestConcentrationInequalities:
    """Trace formulas, Wigner moments, Gershgorin, Markov / Chebyshev."""

    def test_trace_a0(self):
        """tr(A^0) = tr(I) = n = 40."""
        assert np.trace(np.eye(_n, dtype=int)) == _n

    def test_trace_a1(self):
        """tr(A) = 0  (adjacency has zero diagonal)."""
        assert np.trace(_A) == 0

    def test_trace_a2_equals_twice_edges(self):
        """tr(A^2) = 2|E| = 480."""
        assert int(np.trace(_A @ _A)) == 480

    def test_trace_a3_equals_six_triangles(self):
        """tr(A^3) = 6 * #triangles = 6 * 160 = 960."""
        A3 = np.linalg.matrix_power(_A, 3)
        assert int(np.trace(A3)) == 960

    def test_trace_a4(self):
        """tr(A^4) = 12^4 + 24*16 + 15*256 = 20736 + 384 + 3840 = 24960."""
        A4 = np.linalg.matrix_power(_A, 4)
        assert int(np.trace(A4)) == 24960

    def test_wigner_trace_formula(self):
        """tr(A^k) = 12^k + 24*2^k + 15*(-4)^k  for k = 1 .. 6."""
        for k in range(1, 7):
            Ak = np.linalg.matrix_power(_A, k)
            tr_mat = int(np.trace(Ak))
            tr_spec = 12 ** k + 24 * 2 ** k + 15 * (-4) ** k
            assert tr_mat == tr_spec, f"k={k}: {tr_mat} != {tr_spec}"

    def test_gershgorin_bound(self):
        """All eigenvalues lie in the Gershgorin disks.
        Centre = A_{ii} = 0, radius = sum_{j != i} |A_{ij}| = k = 12.
        So every eigenvalue is in [-12, 12]."""
        assert _eigvals[0] >= -12.0 - 1e-10
        assert _eigvals[-1] <= 12.0 + 1e-10

    def test_markov_bound(self):
        """P(|lambda| > t) <= tr(A^2)/(n*t^2).
        For t = 10: empirical = 1/40, bound = 480/4000 = 0.12."""
        t = 10.0
        empirical = float(np.sum(np.abs(_eigvals) > t)) / _n
        bound = 480.0 / (_n * t ** 2)
        assert empirical <= bound + 1e-10

    def test_chebyshev_bound(self):
        """P(|lambda - mu| > t) <= sigma^2/t^2  with mu = 0, sigma^2 = 12.
        For t = 8: empirical P(|lambda| > 8) = 1/40, bound = 12/64 = 3/16."""
        t = 8.0
        empirical = float(np.sum(np.abs(_eigvals) > t)) / _n
        bound = 12.0 / t ** 2
        assert empirical <= bound + 1e-10

    def test_trace_moment_ratio(self):
        """m_4/m_2^2 = (24960/40)/(480/40)^2 = 624/144 = 13/3.
        GOE semicircle gives C_2 = 2.  Our ratio exceeds 2: non-GOE."""
        m2 = float(np.trace(_A @ _A)) / _n
        A4 = np.linalg.matrix_power(_A, 4)
        m4 = float(np.trace(A4)) / _n
        ratio = m4 / m2 ** 2
        assert abs(ratio - 13.0 / 3.0) < 1e-8
        assert ratio > 2.0


# ===================================================================
# 8.  Deterministic vs Random
# ===================================================================

class TestDeterministicVsRandom:
    """Compare SRG spectrum to random d-regular graph expectations."""

    def test_eigenvalue_integrality(self):
        """All eigenvalues of the SRG are integers (elements of Z)."""
        for ev in _eigvals:
            assert abs(ev - round(ev)) < 1e-8

    def test_max_multiplicity_far_from_random(self):
        """Maximum eigenvalue multiplicity = 24.
        A generic random symmetric matrix has all eigenvalues simple (mult 1)."""
        counts = collections.Counter(np.round(_eigvals).astype(int).tolist())
        assert max(counts.values()) == 24

    def test_srg_eigenvalues_from_parameters(self):
        """SRG(n,k,lam,mu) non-trivial eigenvalues:
        r = (lam - mu + sqrt(Delta))/2,  s = (lam - mu - sqrt(Delta))/2
        with Delta = (lam - mu)^2 + 4(k - mu).
        Here Delta = 4 + 32 = 36, r = 2, s = -4."""
        lam, mu = 2, 4
        delta = (lam - mu) ** 2 + 4 * (_k - mu)
        sqrt_d = int(round(math.sqrt(delta)))
        assert sqrt_d ** 2 == delta
        r = ((lam - mu) + sqrt_d) / 2.0
        s = ((lam - mu) - sqrt_d) / 2.0
        assert r == 2.0
        assert s == -4.0

    def test_srg_multiplicities_from_parameters(self):
        """Multiplicities from sum rules:
        f + g = n - 1,  f*r + g*s = -k.
        f = (-k - (n-1)*s) / (r - s) = (-12 + 156)/6 = 24,  g = 15."""
        r, s = 2.0, -4.0
        f = (-_k - (_n - 1) * s) / (r - s)
        g = (_n - 1) - f
        assert abs(f - 24) < 1e-10
        assert abs(g - 15) < 1e-10

    def test_ramanujan_property(self):
        """W(3,3) is Ramanujan: max(|r|, |s|) = 4 <= 2*sqrt(k-1) = 2*sqrt(11) ~ 6.633."""
        nontrivial_max = max(abs(2), abs(-4))
        bound = 2.0 * math.sqrt(_k - 1.0)
        assert nontrivial_max <= bound

    def test_kesten_mckay_second_moment_deviation(self):
        """Kesten-McKay 2nd moment for random d-regular: k - 1 = 11.
        SRG non-trivial empirical 2nd moment: (24*4 + 15*16)/39 = 336/39 ~ 8.615.
        Deviation |8.615 - 11| > 2 quantifies departure from universality."""
        nontrivial_eigs = np.concatenate([np.full(24, 2.0), np.full(15, -4.0)])
        m2_emp = float(np.mean(nontrivial_eigs ** 2))
        m2_km = float(_k - 1)          # = 11
        assert abs(m2_emp - 336.0 / 39.0) < 1e-10
        assert abs(m2_emp - m2_km) > 2.0

    def test_arithmeticity_measure(self):
        """Sum of distances to nearest integer = 0  (maximally arithmetic spectrum)."""
        arith = sum(abs(float(ev) - round(float(ev))) for ev in _eigvals)
        assert arith < 1e-6

    def test_spectral_gap_exceeds_random_expectation(self):
        """SRG spectral gap k - r = 10.
        Random d-regular: expected gap ~ k - 2*sqrt(k-1) = 12 - 2*sqrt(11) ~ 5.37.
        SRG gap (10) substantially exceeds the random expectation."""
        gap = float(_eigvals[-1] - _eigvals[-2])    # 12 - 2 = 10
        random_expected_gap = _k - 2.0 * math.sqrt(_k - 1.0)
        assert abs(gap - 10.0) < 1e-8
        assert gap > random_expected_gap
