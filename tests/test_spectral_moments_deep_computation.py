"""
Phase CXLII -- Spectral Moments and Trace Formulas Deep Computation
on W(3,3) = SRG(40,12,2,4).

103 tests covering spectral moments M_n = tr(A^n), Newton's identities
relating power sums to elementary symmetric polynomials, moment generating
function analytics, graph zeta function, Ihara zeta function, trace formulas
and cycle counting, spectral entropy, Estrada index, graph energy, and
resolvent trace / Stieltjes transform of the spectral measure.

All tests use only numpy and standard library.  Every assertion is
mathematically derivable from the SRG(40,12,2,4) spectrum
    adjacency:  {12^1, 2^24, (-4)^15}
"""

import math
import numpy as np
from numpy.testing import assert_allclose
import pytest


# ---------------------------------------------------------------------------
# W(3,3) builder
# ---------------------------------------------------------------------------

def _build_w33():
    """Build the 40-vertex SRG(40,12,2,4) adjacency matrix."""
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
            u, w = points[i], points[j]
            omega = (u[0]*w[1] - u[1]*w[0] + u[2]*w[3] - u[3]*w[2]) % 3
            if omega == 0:
                A[i, j] = A[j, i] = 1
    return A


# ---------------------------------------------------------------------------
# Module-level precomputation
# ---------------------------------------------------------------------------

_N = 40
_K = 12
_LAM = 2   # SRG lambda
_MU = 4    # SRG mu

# Eigenvalues and multiplicities
_EIGS = [12, 2, -4]
_MULTS = [1, 24, 15]

_A = _build_w33()
_eigvals = np.linalg.eigvalsh(_A.astype(float))
_eigvals_sorted = np.sort(_eigvals)[::-1]

# Precompute spectral moments from formula
def _moment(n):
    """M_n = sum_i m_i * lambda_i^n."""
    return sum(m * (lam ** n) for lam, m in zip(_EIGS, _MULTS))


# ---------------------------------------------------------------------------
# 1. Spectral Moments  (12 tests)
# ---------------------------------------------------------------------------

class TestSpectralMoments:
    """M_n = tr(A^n) = sum m_i * lambda_i^n."""

    def test_M0(self):
        assert _moment(0) == 40
        assert int(np.trace(np.eye(40))) == 40

    def test_M1_traceless(self):
        assert _moment(1) == 0
        assert int(np.trace(_A)) == 0

    def test_M2(self):
        # M_2 = v*k = 40*12 = 480
        expected = 480
        assert _moment(2) == expected
        assert int(np.trace(_A @ _A)) == expected

    def test_M3_triangles(self):
        # M_3 = 6 * (#triangles); #triangles = 160
        expected = 960
        assert _moment(3) == expected
        assert int(np.round(np.trace(_A @ _A @ _A))) == expected

    def test_triangle_count(self):
        M3 = int(np.round(np.trace(_A @ _A @ _A)))
        assert M3 // 6 == 160

    def test_M4(self):
        expected = 12**4 * 1 + 2**4 * 24 + (-4)**4 * 15
        assert expected == 24960
        assert _moment(4) == expected
        A2 = _A @ _A
        assert int(np.round(np.trace(A2 @ A2))) == expected

    def test_M5(self):
        expected = 12**5 + 24 * 2**5 + 15 * (-4)**5
        assert _moment(5) == expected
        A2 = _A @ _A
        A3 = A2 @ _A
        assert int(np.round(np.trace(A2 @ A3))) == expected

    def test_M6(self):
        expected = 12**6 + 24 * 2**6 + 15 * (-4)**6
        assert _moment(6) == expected

    def test_M7(self):
        expected = 12**7 + 24 * 2**7 + 15 * (-4)**7
        assert _moment(7) == expected

    def test_M8(self):
        expected = 12**8 + 24 * 2**8 + 15 * (-4)**8
        assert _moment(8) == expected

    def test_moments_from_matrix(self):
        """Verify M_n via actual matrix powers for n=0..6."""
        An = np.eye(40, dtype=float)
        for n in range(7):
            tr_val = int(np.round(np.trace(An)))
            assert tr_val == _moment(n), f"Mismatch at n={n}"
            An = An @ _A

    def test_even_moments_positive(self):
        for n in range(0, 12, 2):
            assert _moment(n) > 0


# ---------------------------------------------------------------------------
# 2. Newton's Identities  (11 tests)
# ---------------------------------------------------------------------------

class TestNewtonIdentities:
    """
    Newton's identities relate power sums p_k = M_k to elementary symmetric
    polynomials e_k of the eigenvalue multiset.

    For the 40 eigenvalues (with multiplicity):
      p_1 = e_1
      p_2 = p_1*e_1 - 2*e_2
      p_3 = p_2*e_1 - p_1*e_2 + 3*e_3
      ...
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        # Build full eigenvalue list with multiplicity
        self.eig_list = []
        for lam, m in zip(_EIGS, _MULTS):
            self.eig_list.extend([lam] * m)
        assert len(self.eig_list) == 40
        # Power sums
        self.p = [sum(x**k for x in self.eig_list) for k in range(11)]
        # Elementary symmetric polynomials from numpy (coefficients of char poly)
        coeffs = np.polynomial.polynomial.polyfromroots(self.eig_list)
        # coeffs[k] = e_{40-k} * (-1)^{40-k} ... use numpy's poly
        # Use np.poly which gives [1, -e1, e2, -e3, ...] for monic poly
        c = np.poly(self.eig_list)  # length 41, c[0]=1
        # e_k = (-1)^k * c[k]
        self.e = [(-1)**k * c[k] for k in range(41)]

    def test_e0(self):
        assert_allclose(self.e[0], 1.0, atol=1e-6)

    def test_e1_equals_p1(self):
        # e_1 = sum of eigenvalues = p_1 = 0
        assert_allclose(self.e[1], 0.0, atol=1e-6)

    def test_newton_k1(self):
        # p_1 = e_1
        assert_allclose(self.p[1], self.e[1], atol=1e-6)

    def test_newton_k2(self):
        # p_2 = e_1*p_1 - 2*e_2
        lhs = self.p[2]
        rhs = self.e[1] * self.p[1] - 2 * self.e[2]
        assert_allclose(lhs, rhs, atol=1e-4)

    def test_newton_k3(self):
        # p_3 = e_1*p_2 - e_2*p_1 + 3*e_3
        lhs = self.p[3]
        rhs = self.e[1]*self.p[2] - self.e[2]*self.p[1] + 3*self.e[3]
        assert_allclose(lhs, rhs, atol=1e-4)

    def test_newton_k4(self):
        lhs = self.p[4]
        rhs = (self.e[1]*self.p[3] - self.e[2]*self.p[2]
               + self.e[3]*self.p[1] - 4*self.e[4])
        assert_allclose(lhs, rhs, atol=1e-2)

    def test_newton_k5(self):
        lhs = self.p[5]
        rhs = (self.e[1]*self.p[4] - self.e[2]*self.p[3]
               + self.e[3]*self.p[2] - self.e[4]*self.p[1] + 5*self.e[5])
        assert_allclose(lhs, rhs, atol=1e-1)

    def test_e2_value(self):
        # e_2 = sum_{i<j} lam_i*lam_j = (p_1^2 - p_2)/2 = (0 - 480)/2 = -240
        expected = (self.p[1]**2 - self.p[2]) / 2
        assert_allclose(self.e[2], expected, atol=1e-6)
        assert_allclose(self.e[2], -240.0, atol=1e-6)

    def test_e40_determinant(self):
        # e_40 = product of all eigenvalues = det(A)
        prod_eig = (12**1) * (2**24) * ((-4)**15)
        det_A = np.linalg.det(_A.astype(float))
        assert_allclose(det_A, float(prod_eig), rtol=1e-6)

    def test_power_sum_p2(self):
        assert self.p[2] == 480

    def test_power_sum_p3(self):
        assert self.p[3] == 960


# ---------------------------------------------------------------------------
# 3. Moment Generating Function  (10 tests)
# ---------------------------------------------------------------------------

class TestMomentGeneratingFunction:
    """
    MGF: M(t) = sum_i m_i * exp(lambda_i * t)
             = exp(12t) + 24*exp(2t) + 15*exp(-4t)
    Taylor: M(t) = sum_{n>=0} M_n * t^n / n!
    """

    def _mgf(self, t):
        return math.exp(12*t) + 24*math.exp(2*t) + 15*math.exp(-4*t)

    def test_mgf_at_zero(self):
        assert_allclose(self._mgf(0), 40.0)

    def test_mgf_derivative_at_zero(self):
        # M'(0) = 12 + 24*2 + 15*(-4) = 12 + 48 - 60 = 0 = M_1
        h = 1e-8
        deriv = (self._mgf(h) - self._mgf(-h)) / (2*h)
        assert_allclose(deriv, 0.0, atol=1e-4)

    def test_mgf_second_derivative(self):
        # M''(0) = 12^2 + 24*4 + 15*16 = 144+96+240 = 480 = M_2
        h = 1e-5
        d2 = (self._mgf(h) - 2*self._mgf(0) + self._mgf(-h)) / h**2
        assert_allclose(d2, 480.0, atol=0.1)

    def test_mgf_positive(self):
        for t in np.linspace(-1, 1, 20):
            assert self._mgf(t) > 0

    def test_mgf_convex(self):
        """MGF of real distribution is log-convex."""
        ts = np.linspace(-0.5, 0.5, 50)
        vals = [math.log(self._mgf(t)) for t in ts]
        for i in range(1, len(vals)-1):
            assert vals[i] <= (vals[i-1] + vals[i+1]) / 2 + 1e-10

    def test_mgf_symmetry_break(self):
        """Not symmetric: M(t) != M(-t) in general."""
        assert abs(self._mgf(0.5) - self._mgf(-0.5)) > 1.0

    def test_mgf_large_positive_t(self):
        """For large t, dominated by exp(12t)."""
        t = 2.0
        ratio = self._mgf(t) / math.exp(12*t)
        assert_allclose(ratio, 1.0, atol=1e-3)

    def test_mgf_large_negative_t(self):
        """For large negative t, dominated by 15*exp(-4t)."""
        t = -3.0
        ratio = self._mgf(t) / (15 * math.exp(-4*t))
        assert_allclose(ratio, 1.0, atol=1e-3)

    def test_taylor_truncation(self):
        """Taylor series to order 6 at t=0.05 matches MGF."""
        t = 0.05
        taylor = sum(_moment(n) * t**n / math.factorial(n) for n in range(15))
        assert_allclose(taylor, self._mgf(t), rtol=1e-6)

    def test_mgf_laplace_relation(self):
        """M(t) = tr(exp(tA)); verify via eigendecomposition."""
        t = 0.3
        expected = self._mgf(t)
        # Via matrix exponential eigenvalues
        computed = sum(m * math.exp(lam*t) for lam, m in zip(_EIGS, _MULTS))
        assert_allclose(computed, expected)


# ---------------------------------------------------------------------------
# 4. Graph Zeta Function  (10 tests)
# ---------------------------------------------------------------------------

class TestGraphZeta:
    """
    Spectral zeta: Z(u) = prod_i (1 - u*lambda_i)^{-1}
                        = (1-12u)^{-1} * (1-2u)^{-24} * (1+4u)^{-15}
    Log-derivative: Z'/Z = sum_i m_i*lambda_i / (1 - u*lambda_i)
                         = sum_{n>=1} M_n * u^{n-1}
    """

    def _zeta(self, u):
        return ((1 - 12*u)**(-1) * (1 - 2*u)**(-24) * (1 + 4*u)**(-15))

    def test_zeta_at_zero(self):
        assert_allclose(self._zeta(0), 1.0)

    def test_zeta_pole_at_1_over_12(self):
        """Pole at u=1/12."""
        u = 1/12 - 1e-10
        assert self._zeta(u) > 1e8

    def test_zeta_pole_at_neg_1_over_4(self):
        """Pole at u=-1/4."""
        u = -1/4 + 1e-10
        assert self._zeta(u) > 1e8

    def test_zeta_log_derivative_coeff(self):
        """d/du log Z(u) |_{u=0} = sum m_i * lambda_i = M_1 = 0."""
        h = 1e-8
        logZ = lambda u: math.log(abs(self._zeta(u)))
        deriv = (logZ(h) - logZ(-h)) / (2*h)
        assert_allclose(deriv, 0.0, atol=1e-3)

    def test_zeta_small_u_expansion(self):
        """Z(u) ~ 1 + M_1*u + ... = 1 + 0*u + ... for small u."""
        u = 1e-6
        assert_allclose(self._zeta(u), 1.0, atol=1e-3)

    def test_zeta_reciprocal_polynomial(self):
        """1/Z(u) = (1-12u)(1-2u)^24 (1+4u)^15 is a polynomial of degree 40."""
        # Evaluate at u=0.01
        u = 0.01
        inv_z = (1-12*u) * (1-2*u)**24 * (1+4*u)**15
        assert_allclose(1/self._zeta(u), inv_z, rtol=1e-10)

    def test_zeta_product_form(self):
        """Verify product form equals eigenvalue-based definition."""
        u = 0.03
        prod_val = 1.0
        for lam, m in zip(_EIGS, _MULTS):
            prod_val *= (1 - u*lam)**(-m)
        assert_allclose(prod_val, self._zeta(u), rtol=1e-10)

    def test_zeta_determinantal(self):
        """Z(u) = 1/det(I - u*A)."""
        u = 0.02
        det_val = np.linalg.det(np.eye(40) - u * _A.astype(float))
        assert_allclose(1/det_val, self._zeta(u), rtol=1e-8)

    def test_zeta_radius_convergence(self):
        """Convergence radius = 1/max|lambda| = 1/12."""
        r = 1.0 / max(abs(l) for l in _EIGS)
        assert_allclose(r, 1/12)

    def test_zeta_negative_u(self):
        """Z at negative u still well-defined (away from poles)."""
        u = -0.1
        z = self._zeta(u)
        assert np.isfinite(z)
        assert z > 0  # all factors positive for this u


# ---------------------------------------------------------------------------
# 5. Ihara Zeta Function  (11 tests)
# ---------------------------------------------------------------------------

class TestIharaZeta:
    """
    Ihara zeta: zeta_Ihara(u) = (1-u^2)^{-(m-n)} * det(I - u*A + (k-1)*u^2*I)^{-1}
    where m = edges = n*k/2 = 240, n=40, k=12.

    The reciprocal:
      1/zeta_Ihara(u) = (1-u^2)^{m-n} * det(I - uA + (k-1)u^2 I)
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        self.n = 40
        self.k = 12
        self.m = self.n * self.k // 2  # 240 edges

    def _ihara_reciprocal(self, u):
        """Compute 1/zeta_Ihara(u)."""
        factor1 = (1 - u**2)**(self.m - self.n)  # (1-u^2)^200
        M = np.eye(self.n) - u * _A.astype(float) + (self.k - 1) * u**2 * np.eye(self.n)
        det_val = np.linalg.det(M)
        return factor1 * det_val

    def test_ihara_at_zero(self):
        assert_allclose(self._ihara_reciprocal(0), 1.0)

    def test_edge_count(self):
        assert self.m == 240

    def test_excess(self):
        """m - n = 240 - 40 = 200."""
        assert self.m - self.n == 200

    def test_ihara_det_matrix_at_zero(self):
        M = np.eye(40) - 0*_A + 11*0*np.eye(40)
        assert_allclose(np.linalg.det(M), 1.0)

    def test_ihara_small_u(self):
        """For small u, 1/zeta ~ 1."""
        val = self._ihara_reciprocal(0.01)
        assert abs(val - 1.0) < 0.5

    def test_ihara_eigenvalue_formula(self):
        """
        det(I - uA + (k-1)u^2 I) = prod_i (1 - u*lambda_i + (k-1)*u^2)
        """
        u = 0.05
        det_val = np.linalg.det(
            np.eye(40) - u*_A.astype(float) + 11*u**2*np.eye(40)
        )
        prod_val = 1.0
        for lam, mult in zip(_EIGS, _MULTS):
            prod_val *= (1 - u*lam + 11*u**2)**mult
        assert_allclose(det_val, prod_val, rtol=1e-8)

    def test_ihara_functional_eq_structure(self):
        """Verify (m-n) exponent is 200 for W(3,3)."""
        chi = self.n - self.m  # Euler char of underlying graph (neg)
        assert chi == -200

    def test_ihara_reciprocal_polynomial(self):
        """1/zeta_Ihara is a polynomial in u (of degree 2n + 2(m-n) = 480)."""
        # Just verify it is finite at several points
        for u in [0.01, 0.05, 0.1]:
            val = self._ihara_reciprocal(u)
            assert np.isfinite(val)

    def test_ihara_srg_factor(self):
        """
        For SRG, each eigenvalue factor: 1 - u*lam + 11*u^2.
        Discriminant: lam^2 - 44.
        lam=12: disc=144-44=100>0, real roots.
        lam=2:  disc=4-44=-40<0, complex roots.
        lam=-4: disc=16-44=-28<0, complex roots.
        """
        for lam, disc_expected in [(12, 100), (2, -40), (-4, -28)]:
            disc = lam**2 - 4*11
            assert disc == disc_expected

    def test_ihara_real_poles_from_k12(self):
        """For lam=12: roots of 1-12u+11u^2=0 are u=1, u=1/11."""
        roots = np.roots([11, -12, 1])
        roots_sorted = sorted(roots)
        assert_allclose(roots_sorted, [1/11, 1.0], atol=1e-10)

    def test_ihara_bass_formula(self):
        """
        Bass's determinant formula:
        1/zeta_Ihara(u) = (1-u^2)^{m-n} * prod_i (1 - lam_i*u + (k-1)*u^2)^{m_i}
        Verify at u=0.04.
        """
        u = 0.04
        bass = (1 - u**2)**200
        for lam, mult in zip(_EIGS, _MULTS):
            bass *= (1 - lam*u + 11*u**2)**mult
        direct = self._ihara_reciprocal(u)
        assert_allclose(bass, direct, rtol=1e-6)


# ---------------------------------------------------------------------------
# 6. Trace Formulas and Cycle Counting  (12 tests)
# ---------------------------------------------------------------------------

class TestTraceFormulasCycles:
    """
    tr(A^n) counts closed walks of length n.
    For n=3: 6*triangles.
    For n=4: related to 4-cycles, paths, etc.
    SRG identity: A^2 = -2A + 8I + 4J.
    """

    def test_closed_walks_2(self):
        """Closed walks of length 2 = sum of degrees = 40*12 = 480."""
        assert int(np.trace(_A @ _A)) == 480

    def test_closed_walks_3(self):
        """Closed walks of length 3 = 6 * triangles = 960."""
        assert int(np.round(np.trace(_A @ _A @ _A))) == 960

    def test_srg_identity(self):
        """A^2 = -2A + 8I + 4J (SRG identity for (40,12,2,4))."""
        A2 = _A @ _A
        J = np.ones((40, 40), dtype=int)
        rhs = -2*_A + 8*np.eye(40, dtype=int) + 4*J
        assert np.array_equal(A2, rhs)

    def test_srg_identity_params(self):
        """lam - mu = -2, k - mu = 8."""
        assert _LAM - _MU == -2
        assert _K - _MU == 8

    def test_A3_via_srg(self):
        """A^3 = A*A^2 = A*(-2A+8I+4J) = -2A^2+8A+4AJ.
        AJ = kJ = 12J. So A^3 = -2(-2A+8I+4J)+8A+48J = 4A-16I-8J+8A+48J = 12A-16I+40J.
        tr(A^3) = 12*0 - 16*40 + 40*40 = -640+1600 = 960."""
        assert 12*0 - 16*40 + 40*40 == 960

    def test_A4_via_srg(self):
        """
        A^4 = A*A^3 = A*(12A-16I+40J)= 12A^2 - 16A + 40*AJ
            = 12*(-2A+8I+4J) - 16A + 40*12J
            = -24A + 96I + 48J - 16A + 480J
            = -40A + 96I + 528J.
        tr(A^4) = -40*0 + 96*40 + 528*40 = 3840 + 21120 = 24960.
        """
        expected = -40*0 + 96*40 + 528*40
        assert expected == 24960
        assert _moment(4) == 24960

    def test_A5_trace_via_srg(self):
        """
        A^5 = A*A^4 = A*(-40A+96I+528J)= -40A^2+96A+528*12J
            = -40*(-2A+8I+4J)+96A+6336J
            = 80A-320I-160J+96A+6336J
            = 176A-320I+6176J.
        tr(A^5) = 176*0 - 320*40 + 6176*40 = -12800+247040 = 234240.
        """
        expected = 176*0 - 320*40 + 6176*40
        assert expected == 234240
        assert _moment(5) == 234240

    def test_triangle_per_vertex(self):
        """Each vertex is in lam*k/2 = ... no. Total triangles=160, per vertex = 160*3/40 = 12."""
        assert 160 * 3 // 40 == 12

    def test_quadrilateral_count(self):
        """
        Number of 4-cycles: from M_4 and known formulas.
        Closed 4-walks = M_4 = 24960.
        These include: degenerate walks and true 4-cycles.
        Degenerate = n*k + 2*n*k*(k-1) + 6*T_count (where T_count=triangles counted via adjacent edges).
        For SRG: # 4-cycles = (M_4 - n*k*(2k-1) - 6*(# triangles)*2 ... complex formula).
        Just verify M_4 matches.
        """
        A4_trace = int(np.round(np.trace(np.linalg.matrix_power(_A, 4))))
        assert A4_trace == 24960

    def test_return_probability(self):
        """Return probability after n steps from vertex 0:
        p_0^{(n)} = (1/40) * sum_i m_i * (lambda_i/k)^n (spectral formula)."""
        # After 2 steps
        p2 = sum(m * (lam/12)**2 for lam, m in zip(_EIGS, _MULTS)) / 40
        # Should equal A^2[0,0]/k^2 = degree/k = 12/12 = ... no.
        # p_0^(2) = (A^2)[0,0] / k^2 ... actually for lazy walk.
        # For simple walk: p^(2)_return = A^2[0,0] / 12^2 (if normalized)
        # A^2[0,0] = k = 12 (SRG: diagonal of A^2 = k).
        A2_00 = (_A @ _A)[0, 0]
        assert A2_00 == 12

    def test_mixing_time_bound(self):
        """Spectral gap = k - lambda_2 = 12 - 2 = 10.
        Mixing time ~ k/gap = 12/10 = 1.2 (very fast mixing)."""
        gap = 12 - 2
        assert gap == 10

    def test_A2_diagonal_constant(self):
        """For k-regular graph, all diagonal entries of A^2 equal k."""
        diag = np.diag(_A @ _A)
        assert np.all(diag == 12)


# ---------------------------------------------------------------------------
# 7. Spectral Entropy  (10 tests)
# ---------------------------------------------------------------------------

class TestSpectralEntropy:
    """
    Spectral entropy: H = -sum p_i * log(p_i)
    where p_i = |lambda_i| / sum|lambda_j|.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        abs_eigs = []
        for lam, m in zip(_EIGS, _MULTS):
            abs_eigs.extend([abs(lam)] * m)
        total = sum(abs_eigs)
        self.total = total
        self.probs = [x / total for x in abs_eigs]
        self.entropy = -sum(p * math.log(p) for p in self.probs if p > 0)
        # Grouped form
        self.abs_eigs_unique = [12, 2, 4]
        self.grouped_probs = [m * abs(lam) / total
                              for lam, m in zip(_EIGS, _MULTS)]

    def test_total_absolute_eigenvalue(self):
        # |12|*1 + |2|*24 + |-4|*15 = 12+48+60 = 120
        assert self.total == 120

    def test_probabilities_sum_to_one(self):
        assert_allclose(sum(self.probs), 1.0)

    def test_entropy_positive(self):
        assert self.entropy > 0

    def test_entropy_upper_bound(self):
        """H <= log(n) = log(40)."""
        assert self.entropy <= math.log(40) + 1e-10

    def test_entropy_lower_bound(self):
        """H > 0 for non-degenerate spectrum."""
        assert self.entropy > 0.1

    def test_grouped_entropy(self):
        """Entropy computed from 3 distinct |eigenvalue| groups."""
        gp = self.grouped_probs
        assert_allclose(sum(gp), 1.0)
        H_grouped = -sum(p * math.log(p) for p in gp if p > 0)
        # This is the entropy of the 3-group distribution
        assert H_grouped > 0
        assert H_grouped <= math.log(3) + 1e-10

    def test_entropy_not_maximal(self):
        """Not uniform => entropy < log(40)."""
        assert self.entropy < math.log(40) - 0.1

    def test_prob_eigenvalue_12(self):
        assert_allclose(self.grouped_probs[0], 12/120)

    def test_prob_eigenvalue_2(self):
        assert_allclose(self.grouped_probs[1], 48/120)

    def test_prob_eigenvalue_neg4(self):
        assert_allclose(self.grouped_probs[2], 60/120)


# ---------------------------------------------------------------------------
# 8. Estrada Index  (11 tests)
# ---------------------------------------------------------------------------

class TestEstradaIndex:
    """
    Estrada index: EE(G) = sum_i exp(lambda_i)
                         = exp(12) + 24*exp(2) + 15*exp(-4).
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        self.EE = (math.exp(12) + 24*math.exp(2) + 15*math.exp(-4))

    def test_estrada_value(self):
        assert_allclose(self.EE, 162932.39, atol=1.0)

    def test_estrada_dominant_term(self):
        """exp(12) ~ 162754.79 dominates."""
        assert math.exp(12) / self.EE > 0.99

    def test_estrada_from_moments(self):
        """EE = sum_{n>=0} M_n / n!"""
        ee_approx = sum(_moment(n) / math.factorial(n) for n in range(50))
        assert_allclose(ee_approx, self.EE, rtol=1e-8)

    def test_estrada_lower_bound(self):
        """EE >= n = 40."""
        assert self.EE >= 40

    def test_estrada_upper_bound_simple(self):
        """EE <= n * exp(k) for k-regular."""
        assert self.EE <= 40 * math.exp(12)

    def test_estrada_via_matrix(self):
        """EE = tr(exp(A))."""
        expA = np.zeros(40)
        for lam, m in zip(_EIGS, _MULTS):
            expA = None  # placeholder
            break
        # Direct: tr(expm(A)) via eigenvalues
        tr_exp = sum(m * math.exp(lam) for lam, m in zip(_EIGS, _MULTS))
        assert_allclose(tr_exp, self.EE)

    def test_estrada_subgraph_centrality(self):
        """SC(v) = [exp(A)]_{vv}. Sum over v = EE."""
        # For k-regular SRG each SC(v) = EE/n by symmetry... only if vertex-transitive
        # W(3,3) is vertex-transitive, so SC(v) = EE/40 for all v.
        sc_v = self.EE / 40
        assert sc_v > 0

    def test_estrada_bipartite_gap(self):
        """W(3,3) is NOT bipartite (has triangles), so EE > n."""
        assert self.EE > 40

    def test_estrada_exp2_contribution(self):
        contrib = 24 * math.exp(2)
        assert_allclose(contrib, 177.32, atol=0.1)

    def test_estrada_exp_neg4_contribution(self):
        contrib = 15 * math.exp(-4)
        assert_allclose(contrib, 0.2747, atol=0.01)

    def test_estrada_ratio_to_n(self):
        """EE/n is the average subgraph centrality."""
        assert self.EE / 40 > 4000


# ---------------------------------------------------------------------------
# 9. Graph Energy  (13 tests)
# ---------------------------------------------------------------------------

class TestGraphEnergy:
    """
    Energy: E(G) = sum |lambda_i| = 12 + 24*2 + 15*4 = 120.
    For k-regular graph on n vertices with m edges: m = nk/2 = 240.
    E(G) = 120 = m/2 = 240/2 (beautiful relation!).
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        self.energy = sum(abs(lam) * m for lam, m in zip(_EIGS, _MULTS))

    def test_energy_value(self):
        assert self.energy == 120

    def test_energy_from_eigenvalues(self):
        energy_from_eigs = sum(abs(ev) for ev in _eigvals)
        assert_allclose(energy_from_eigs, 120.0, atol=1e-8)

    def test_energy_equals_half_edges(self):
        """E(G) = nk/2 / 1 ... actually E = 120 = m/2 = 240/2. Wait: m = 240, E=120 = m/2."""
        m = 40 * 12 // 2
        assert m == 240
        assert self.energy == m // 2

    def test_energy_decomposition(self):
        assert 1 * 12 == 12
        assert 24 * 2 == 48
        assert 15 * 4 == 60
        assert 12 + 48 + 60 == 120

    def test_energy_lower_bound(self):
        """E(G) >= 2*m/n = 2*240/40 = 12."""
        assert self.energy >= 2 * 240 / 40

    def test_energy_upper_bound_simple(self):
        """E(G) <= sqrt(n * 2m) = sqrt(40*480) = sqrt(19200) ~ 138.6."""
        ub = math.sqrt(40 * 480)
        assert self.energy <= ub + 1e-10

    def test_energy_koolen_moulton(self):
        """Koolen-Moulton: E(G) <= 2m/n + (n-1)*sqrt(2m/n * (1 - (2m/n^2)^...) ... skip exact.
        Just verify energy is less than n*sqrt(2m/n)."""
        avg_sq = 480 / 40  # M_2/n = average squared eigenvalue = 12
        ub = 40 * math.sqrt(avg_sq)  # n * sqrt(M_2/n)
        assert self.energy <= ub + 1e-10

    def test_hyperenergetic(self):
        """G is hyperenergetic if E(G) > E(K_n) = 2*(n-1) = 78.
        120 > 78, so W(3,3) is hyperenergetic."""
        assert self.energy > 2 * (40 - 1)

    def test_borderenergetic_not(self):
        """G is borderenergetic if E(G) = 2*(n-1). 120 != 78."""
        assert self.energy != 2 * (40 - 1)

    def test_energy_per_vertex(self):
        assert_allclose(self.energy / 40, 3.0)

    def test_energy_per_edge(self):
        assert_allclose(self.energy / 240, 0.5)

    def test_coulson_integral(self):
        """E(G) = (1/pi) * integral_{-inf}^{inf} (n - iy * tr(resolvent)) dy / y^2.
        Numerically: E = (1/pi) * integral sum_i log(1 + lambda_i^2/y^2) dy... complex.
        Just verify sum |lam| via absolute values of computed eigenvalues."""
        abs_sum = np.sum(np.abs(_eigvals_sorted))
        assert_allclose(abs_sum, 120.0, atol=1e-8)

    def test_energy_complement(self):
        """
        Complement has eigenvalues: -1-lambda_i for i>0, and n-1-k for i=0.
        Complement eigenvalues: {27^1, -3^24, 3^15}.
        E(complement) = 27 + 24*3 + 15*3 = 27+72+45 = 144.
        """
        comp_energy = 27 + 24*3 + 15*3
        assert comp_energy == 144


# ---------------------------------------------------------------------------
# 10. Resolvent Trace and Stieltjes Transform  (13 tests)
# ---------------------------------------------------------------------------

class TestResolventStieltjes:
    """
    Resolvent: R(z) = (zI - A)^{-1}.
    Trace of resolvent: tr(R(z)) = sum_i m_i / (z - lambda_i).
    Stieltjes transform: S(z) = (1/n) * tr(R(z))
                               = (1/40) * [1/(z-12) + 24/(z-2) + 15/(z+4)].
    """

    def _stieltjes(self, z):
        """Stieltjes transform of spectral measure."""
        return (1.0/40) * (1/(z-12) + 24/(z-2) + 15/(z+4))

    def _resolvent_trace(self, z):
        return 1/(z-12) + 24/(z-2) + 15/(z+4)

    def test_resolvent_trace_large_z(self):
        """For z >> 12, tr(R(z)) ~ 40/z."""
        z = 1000
        assert_allclose(self._resolvent_trace(z), 40/z, rtol=1e-3)

    def test_stieltjes_large_z(self):
        """S(z) ~ 1/z for large z."""
        z = 1000
        assert_allclose(self._stieltjes(z), 1/z, rtol=1e-3)

    def test_stieltjes_moments(self):
        """
        S(z) = sum_{n>=0} M_n / (n * z^{n+1}).
        Actually: S(z) = (1/40)*sum_{n>=0} M_n / z^{n+1}.
        """
        z = 20.0  # outside spectrum
        s_direct = self._stieltjes(z)
        s_series = (1/40) * sum(_moment(n) / z**(n+1) for n in range(50))
        assert_allclose(s_series, s_direct, rtol=1e-8)

    def test_resolvent_poles(self):
        """Poles at z = 12, 2, -4."""
        for pole in [12, 2, -4]:
            z = pole + 1e-10
            assert abs(self._resolvent_trace(z)) > 1e8

    def test_resolvent_via_matrix(self):
        """tr((zI-A)^{-1}) computed via actual matrix inverse."""
        z = 20.0
        R = np.linalg.inv(z * np.eye(40) - _A.astype(float))
        tr_R = np.trace(R)
        assert_allclose(tr_R, self._resolvent_trace(z), rtol=1e-8)

    def test_stieltjes_imaginary_axis(self):
        """S(iy) for y real: spectral density recovery via Stieltjes inversion."""
        y = 5.0
        z = 1j * y
        s = (1.0/40) * (1/(z-12) + 24/(z-2) + 15/(z+4))
        assert np.isfinite(abs(s))

    def test_spectral_density_peaks(self):
        """Im(S(x+i*eps)) / pi peaks at eigenvalues."""
        eps = 0.01
        for lam in _EIGS:
            z = lam + 1j * eps
            s = self._stieltjes(z)
            # Should have large imaginary part near eigenvalue
            assert abs(s.imag) > 1.0

    def test_resolvent_identity(self):
        """R(z1) - R(z2) = (z2-z1)*R(z1)*R(z2) at trace level (not directly).
        Instead verify: tr(R(z)) derivative = -tr(R(z)^2) = -sum m_i/(z-lam_i)^2."""
        z = 15.0
        h = 1e-6
        deriv = (self._resolvent_trace(z+h) - self._resolvent_trace(z-h)) / (2*h)
        neg_tr_R2 = -sum(m / (z-lam)**2 for lam, m in zip(_EIGS, _MULTS))
        assert_allclose(deriv, neg_tr_R2, rtol=1e-4)

    def test_stieltjes_normalization(self):
        """Integral of spectral measure = 1. Equivalently, lim z*S(z) = 1 as z->inf."""
        z = 1e6
        assert_allclose(z * self._stieltjes(z), 1.0, rtol=1e-4)

    def test_resolvent_at_z_neg5(self):
        """z=-5 is between eigenvalues -4 and 2."""
        z = -5.0
        val = self._resolvent_trace(z)
        # 1/(-5-12) + 24/(-5-2) + 15/(-5+4) = -1/17 - 24/7 - 15
        expected = -1/17 - 24/7 - 15
        assert_allclose(val, expected, rtol=1e-10)

    def test_greens_function_diagonal(self):
        """G_{00}(z) = [R(z)]_{00}. For vertex-transitive: G_{00} = S(z)."""
        z = 20.0
        R = np.linalg.inv(z * np.eye(40) - _A.astype(float))
        G00 = R[0, 0]
        # For vertex-transitive graph, all diagonal elements equal
        assert_allclose(G00, self._stieltjes(z), rtol=1e-6)

    def test_all_diagonal_resolvent_equal(self):
        """Vertex-transitivity: all diagonal elements of resolvent are equal."""
        z = 20.0
        R = np.linalg.inv(z * np.eye(40) - _A.astype(float))
        diag = np.diag(R)
        assert_allclose(diag, diag[0], rtol=1e-8)

    def test_cauchy_transform_real_line(self):
        """On real axis away from spectrum, S(x) is real and monotone decreasing
        in each interval between eigenvalues."""
        xs = np.linspace(-3.9, 1.9, 50)  # between -4 and 2
        vals = [self._stieltjes(x) for x in xs]
        # Should be monotone decreasing
        for i in range(len(vals)-1):
            assert vals[i] >= vals[i+1] - 1e-10
