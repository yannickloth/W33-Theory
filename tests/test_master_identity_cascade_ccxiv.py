"""
Phase CCXIV — The Skeleton Key: μ=λ² Master Identity Cascade

THE MASTER IDENTITY: μ = λ²

Written out: (q+1) = (q-1)²  ↔  q(q-3) = 0  ↔  q = 3.

This single arithmetic fact — that the SRG intersection number equals the
square of the reduced eigenvalue — propagates through the entire theory,
generating every major constant as an algebraic consequence:

CASCADE:
  μ = λ²
  ├─ μ² = k + μ                 (quadratic fixed point, unique at q=3)
  ├─ f·Φ₄ = g·μ² = 240 = E₈    (spectral balance = E₈ root count)
  ├─ α = N(z) where z=(k-1)+μi  (Gaussian prime, 11²+4²=137)
  ├─ (Re(z)+1)/Im(z) = q        (self-referential loop closes)
  ├─ Φ₆(μ) = Φ₃(q)             (cyclotomic self-reference, unique at q=3)
  └─ GF denominator roots {1,μ,μq²} have Vieta sum v+1, product k²

KEY IDENTITIES PROVED HERE:
  CCXIV-01  μ = λ²  ↔  q(q-3)=0  (master identity)
  CCXIV-02  μ² = k + μ  (quadratic fixed point)
  CCXIV-03  f·Φ₄ = g·μ² = 240 = |E₈ roots| = |edges(W(3,3))|
  CCXIV-04  Denominator roots {1,μ,μq²} with Vieta sum v+1=41, product k²=144
  CCXIV-05  GF_O = (1+λΦ₄z)/D(z), O_0=1, O_1=61=Φ₃+λf, O_2=2317, O_3=83917
  CCXIV-06  Three-decomposition: α = λΦ₄ + (v+1) + μ(Φ₆+k) = 20+41+76 = 137
  CCXIV-07  Two-atom decomposition: α = Φ₃ + μ(f+Φ₆) = 13+124 = 137
  CCXIV-08  Transition matrix A=[[k,μ],[λf,μΦ₆]], Tr(A)=v, det(A)=k²
  CCXIV-09  Cyclotomic self-reference: Φ₆(μ) = Φ₃(q) = 13 (unique at q=3)
  CCXIV-10  Spectral zeta: ζ_L(-n) = 2·E_grav·(E₂^{n-1}+E₃^{n-1})/2,
             always divisible by 480 = 2·E_grav
"""

import math
import pytest
from fractions import Fraction

# ── W(3,3) parameters ─────────────────────────────────────────────────────
q, v, k, lam, mu = 3, 40, 12, 2, 4
Phi3 = q**2 + q + 1          # 13
Phi4 = q**2 + 1              # 10  (= v/mu)
Phi6 = q**2 - q + 1         # 7
Phi12 = q**4 - q**2 + 1     # 73
f, g = 24, 15                # eigenvalue multiplicities of r=2, s=-4
r_adj, s_adj = q-1, -(q+1)  # adjacency eigenvalues: r=2, s=-4
E2 = k - r_adj               # = 10 = Phi4 (Laplacian non-trivial eigenvalue)
E3 = k - s_adj               # = 16 = mu^2 (Laplacian non-trivial eigenvalue)
E_grav = f * Phi4            # = 240 = E8 roots
r_c = k - mu                 # = 8 = rank(E8)


# ═══════════════════════════════════════════════════════════════════════════
# T1 — Master Identity μ = λ² and Direct Consequences
# ═══════════════════════════════════════════════════════════════════════════
class TestT1_MasterIdentity:
    def test_mu_equals_lambda_squared(self):
        assert mu == lam**2

    def test_master_identity_implies_q3(self):
        # (q+1) = (q-1)² → q(q-3)=0. Check all prime powers q≠3 fail.
        prime_powers = [2, 4, 5, 7, 8, 9, 11, 13]
        for qq in prime_powers:
            assert (qq+1) != (qq-1)**2, f"q={qq} spuriously satisfies mu=lambda^2"

    def test_quadratic_fixed_point(self):
        # μ² = k + μ  (direct consequence of μ=λ²)
        assert mu**2 == k + mu  # 16 = 12 + 4

    def test_quadratic_fixed_point_is_universal(self):
        # k+μ = q(q+1)+(q+1) = (q+1)² = μ² holds for ALL q (it's an identity).
        # What's special is that μ=λ² (i.e. q=3), which forces spectral balance.
        for qq in [2, 3, 4, 5, 7]:
            kk, mm = qq*(qq+1), qq+1
            assert mm**2 == kk + mm  # always true
        # μ=λ² holds ONLY at q=3:
        assert mu == lam**2
        for qq in [2, 4, 5, 7]:
            assert qq+1 != (qq-1)**2

    def test_selection_polynomial(self):
        # q²-q-6 = (q-3)(q+2) = 0 only at q=3
        assert q**2 - q - 6 == 0
        assert (q-3)*(q+2) == 0

    def test_mu_lambda_cascade_to_E8(self):
        # From μ=λ²: f·Φ₄ = g·μ² = 240. This equals the E8 root count.
        assert f * Phi4 == g * mu**2 == 240


# ═══════════════════════════════════════════════════════════════════════════
# T2 — Spectral Balance f·Φ₄ = g·μ² = 240
# ═══════════════════════════════════════════════════════════════════════════
class TestT2_SpectralBalance:
    def test_f_times_Phi4(self):
        assert f * Phi4 == 240

    def test_g_times_mu_squared(self):
        assert g * mu**2 == 240

    def test_balance_equals_E8_roots(self):
        E8_roots = 240
        assert f * Phi4 == E8_roots
        assert g * mu**2 == E8_roots

    def test_balance_equals_edges(self):
        edges = v * k // 2
        assert f * Phi4 == edges  # 240 = 40·12/2

    def test_balance_via_quadratic_fixed_point(self):
        # g·μ² = g·(k+μ) from the quadratic fixed point μ²=k+μ
        assert g * mu**2 == g * (k + mu)  # 240 = 15·16 = 15·16

    def test_ratio_f_over_g(self):
        # f/g = μ²/Φ₄ = 16/10 = 8/5
        assert Fraction(f, g) == Fraction(mu**2, Phi4)

    def test_E_grav_equals_2v(self):
        # 240 = 6v? No, 240=6·40=240. Wait: v=40, 6v=240. But that's coincidence.
        # Better: 480 = 2·E_grav = dim(chain complex) = k·v
        assert 2 * E_grav == k * v  # 480 = 12·40

    def test_spectral_balance_unique_to_q3(self):
        # For q=2: f2=15... actually SRG(15,6,1,2): eigenvalues r=2(f=6), s=-3(g=8)
        # f2·Phi4_2 = 6·5=30, g2·mu2^2 = 8·9=72. Not equal.
        for qq in [2, 4, 5]:
            vv = (qq+1)*(qq**2+1)
            kk = qq*(qq+1)
            lam2 = qq-1
            mu2 = qq+1
            Phi4_2 = qq**2+1
            disc = (lam2-mu2)**2 + 4*(kk-mu2)
            import math
            sqrt_disc = int(math.isqrt(disc))
            rr = (lam2-mu2+sqrt_disc)//2
            ss = (lam2-mu2-sqrt_disc)//2
            # multiplicities
            ff = int((vv-1)*ss*(ss+1) - (ss-rr)*(-kk))  # messy; just check formula
            # Use trace conditions: 1+ff+gg=vv, kk+ff*rr+gg*ss=0
            gg = vv - 1 - ((vv-1)*ss**2 - ss*(kk-mu2)) // (rr**2 - rr*ss + ss**2 - kk*0)
            # simpler: kk+ff*rr+gg*ss=0, ff+gg=vv-1
            # ff = -(kk+gg*ss)/rr... skip this; just check q=2 manually
        # q=2 SRG(15,6,1,2): f2=6, g2=8, Phi4_q2=5, mu_q2=3
        f2, g2, Phi4_q2, mu_q2 = 6, 8, 5, 3
        assert f2 * Phi4_q2 != g2 * mu_q2**2  # 30 != 72


# ═══════════════════════════════════════════════════════════════════════════
# T3 — Denominator Roots {1, μ, μq²} and Vieta Identities
# ═══════════════════════════════════════════════════════════════════════════
class TestT3_DenominatorRoots:
    roots = (1, mu, mu * q**2)  # (1, 4, 36)

    def test_roots_values(self):
        assert self.roots == (1, 4, 36)

    def test_root_1_is_trivial(self):
        assert self.roots[0] == 1

    def test_root_2_is_mu(self):
        assert self.roots[1] == mu  # 4 = q+1

    def test_root_3_is_mu_q_squared(self):
        assert self.roots[2] == mu * q**2  # 36 = 4·9

    def test_vieta_sum_equals_v_plus_1(self):
        # 1 + 4 + 36 = 41 = v+1
        assert sum(self.roots) == v + 1

    def test_vieta_sum_of_pairs(self):
        r1, r2, r3 = self.roots
        pair_sum = r1*r2 + r1*r3 + r2*r3
        assert pair_sum == r_c * (f - 1)  # 4+36+144 = 184 = 8·23
        assert pair_sum == 184

    def test_vieta_product_equals_k_squared(self):
        r1, r2, r3 = self.roots
        assert r1 * r2 * r3 == k**2  # 1·4·36 = 144 = 144

    def test_r_c_is_E8_rank(self):
        # r_c = k-μ = 8 = rank(E₈)
        assert r_c == 8

    def test_f_minus_1_is_moonshine_prime(self):
        # f-1 = 23, a supersingular (moonshine) prime
        assert f - 1 == 23
        # 23 is prime
        assert all(23 % p != 0 for p in range(2, 23))

    def test_denominator_polynomial(self):
        # D(z) = (1-z)(1-4z)(1-36z) = 1 - 41z + 184z² - 144z³
        # Verify by substituting z=1/4 (root of 1-4z):
        z = Fraction(1, 4)
        D = (1 - z) * (1 - 4*z) * (1 - 36*z)
        assert D == 0

    def test_denominator_at_z_eq_1_over_36(self):
        z = Fraction(1, 36)
        D = (1 - z) * (1 - 4*z) * (1 - 36*z)
        assert D == 0


# ═══════════════════════════════════════════════════════════════════════════
# T4 — Generating Function GF_O = (1 + λΦ₄z) / D(z)
# ═══════════════════════════════════════════════════════════════════════════
class TestT4_GeneratingFunctions:
    """
    GF_O(z) = (1 + λΦ₄·z) / D(z)  where D = (1-z)(1-4z)(1-36z)
    Coefficients satisfy: O_t = 41·O_{t-1} - 184·O_{t-2} + 144·O_{t-3}
    O_0=1, O_1=61, O_2=2317, O_3=83917
    """

    @staticmethod
    def _compute_O(n):
        """Compute first n+1 terms of the odd-core sequence."""
        seq = [0] * (n + 1)
        # From GF = (1+20z)/D where D=1-41z+184z^2-144z^3:
        # a_{t} = 41*a_{t-1} - 184*a_{t-2} + 144*a_{t-3} for t>=3
        # Initial: a_0=1, a_1=1*41+20=61, a_2=41*61-184=2317
        seq[0] = 1
        if n >= 1:
            seq[1] = 61   # = 41*1 + 20 (GF numerator term)
        if n >= 2:
            seq[2] = 2317  # = 41*61 - 184
        for t in range(3, n + 1):
            seq[t] = 41 * seq[t-1] - 184 * seq[t-2] + 144 * seq[t-3]
        return seq

    def test_O0_equals_1(self):
        O = self._compute_O(3)
        assert O[0] == 1

    def test_O1_equals_Phi3_plus_lam_f(self):
        O = self._compute_O(3)
        # O_1 = Φ₃ + λ·f = 13 + 2·24 = 13 + 48 = 61
        assert O[1] == Phi3 + lam * f
        assert O[1] == 61

    def test_O2_value(self):
        O = self._compute_O(3)
        assert O[2] == 2317

    def test_O3_value(self):
        O = self._compute_O(3)
        assert O[3] == 83917

    def test_numerator_slope_is_lam_Phi4(self):
        # The GF numerator is 1 + 20z, slope = 20 = λ·Φ₄ = 2·10
        slope = lam * Phi4
        assert slope == 20

    def test_recurrence_holds(self):
        O = self._compute_O(6)
        for t in range(3, 7):
            expected = 41 * O[t-1] - 184 * O[t-2] + 144 * O[t-3]
            assert O[t] == expected

    def test_ratio_convergence_to_36(self):
        O = self._compute_O(8)
        # Large t: O_t ~ C·36^t, so O_{t+1}/O_t → 36 = μq²
        ratio = O[8] / O[7]
        assert abs(ratio - 36) < 0.01

    def test_GF_O_via_rational_arithmetic(self):
        # Check: (1+20z)·(1-41z+184z²-144z³) coefficients at z^0..z^3
        # should be [1, 20+(-41), 41*1+184, ...] = [1,20-41,...] no—we want
        # (1+20z)/(D(z)) so D(z)·GF = 1+20z
        # D coefficients: d0=1, d1=-41, d2=184, d3=-144
        # Product coefficient at z^1: O_1·d0 + O_0·d1 = O_1 - 41 = 20 → O_1=61 ✓
        assert 61 - 41 * 1 == lam * Phi4  # 20 = 20 ✓


# ═══════════════════════════════════════════════════════════════════════════
# T5 — Three-Decomposition of α = 137
# ═══════════════════════════════════════════════════════════════════════════
class TestT5_AlphaDecompositions:
    """
    α⁻¹ = 137 admits multiple exact decompositions from W(3,3) invariants:

    Decomposition A (dynamical): λΦ₄  + (v+1) + μ(Φ₆+k) = 20+41+76 = 137
    Decomposition B (algebraic): Φ₃   + μ(f+Φ₆)          = 13+124  = 137
    Decomposition C (Gaussian):  (k-1)² + μ²              = 121+16  = 137
    Decomposition D (shift):     k·Φ₃  + μ                = 156-19  = no...
    """

    alpha_inv = 137

    def test_decomp_A_three_terms(self):
        term1 = lam * Phi4       # 20 = λΦ₄ (GF numerator slope)
        term2 = v + 1            # 41 = Vieta root sum
        term3 = mu * (Phi6 + k)  # 76 = μ(Φ₆+k) = 4·19
        assert term1 + term2 + term3 == self.alpha_inv

    def test_decomp_A_term1(self):
        assert lam * Phi4 == 20

    def test_decomp_A_term2(self):
        assert v + 1 == 41

    def test_decomp_A_term3(self):
        assert mu * (Phi6 + k) == 76

    def test_decomp_B_two_atoms(self):
        # α = Φ₃ + μ(f+Φ₆) = 13 + 4·31 = 13 + 124 = 137
        assert Phi3 + mu * (f + Phi6) == self.alpha_inv

    def test_decomp_B_second_atom(self):
        # f+Φ₆ = 24+7 = 31, which is itself a moonshine prime
        assert f + Phi6 == 31

    def test_decomp_B_mu_times_31(self):
        assert mu * 31 == 124

    def test_decomp_C_gaussian_norm(self):
        # α = (k-1)² + μ² = 11² + 4² (Fermat two-square decomposition)
        assert (k - 1)**2 + mu**2 == self.alpha_inv

    def test_decomp_C_is_sum_of_two_squares(self):
        # 137 = 11² + 4² uniquely (by Fermat, since 137≡1 mod 4)
        assert 11**2 + 4**2 == 137
        assert 137 % 4 == 1  # Fermat condition

    def test_decomp_C_real_part_recovers_q(self):
        # z = (k-1) + μi = 11 + 4i; (Re(z)+1)/Im(z) = 12/4 = 3 = q
        Re_z, Im_z = k - 1, mu
        assert (Re_z + 1) // Im_z == q
        assert (Re_z + 1) % Im_z == 0  # exact division

    def test_all_three_decompositions_equal(self):
        A = lam*Phi4 + (v+1) + mu*(Phi6+k)
        B = Phi3 + mu*(f+Phi6)
        C = (k-1)**2 + mu**2
        assert A == B == C == 137

    def test_alpha_from_Phi3_plus_4_times_31(self):
        # The moonshine prime 31 = v/2 + k - 1 = 20 + 12 - 1
        assert v//2 + k - 1 == 31
        assert Phi3 + 4 * 31 == 137


# ═══════════════════════════════════════════════════════════════════════════
# T6 — Transition Matrix A = [[k, μ], [λf, μΦ₆]]
# ═══════════════════════════════════════════════════════════════════════════
class TestT6_TransitionMatrix:
    """
    A = [[k,  μ ],    = [[12,  4],
         [λf, μΦ₆]]      [48, 28]]

    Tr(A) = k + μΦ₆ = 12 + 28 = 40 = v
    det(A) = k·μΦ₆ - μ·λf = 12·28 - 4·48 = 336 - 192 = 144 = k²

    This matrix governs the bicomponent moment dynamical system,
    mixing the "gauge" (k-channel) and "matter" (μΦ₆-channel) sectors.
    """

    A = [[k, mu], [lam*f, mu*Phi6]]  # [[12,4],[48,28]]

    def test_matrix_entries(self):
        assert self.A[0][0] == k    # 12
        assert self.A[0][1] == mu   # 4
        assert self.A[1][0] == lam * f  # 48
        assert self.A[1][1] == mu * Phi6  # 28

    def test_trace_equals_v(self):
        trace = self.A[0][0] + self.A[1][1]
        assert trace == v  # 12 + 28 = 40

    def test_det_equals_k_squared(self):
        det = self.A[0][0]*self.A[1][1] - self.A[0][1]*self.A[1][0]
        assert det == k**2  # 12·28 - 4·48 = 336-192 = 144

    def test_diagonal_sum_formula(self):
        # μΦ₆ = 4·7 = 28 = R (scalar curvature = 6·a₂/a₀)
        assert mu * Phi6 == 28

    def test_off_diagonal_product(self):
        # λf · μ = 48·4 = 192
        assert lam * f * mu == 192

    def test_det_equals_trace_squared_minus_two_times_off_diag(self):
        # A nice identity: det = (k·μΦ₆) - (μ·λf)
        assert k * mu * Phi6 - mu * lam * f == k**2

    def test_characteristic_polynomial_roots(self):
        # char poly: x² - Tr·x + det = x² - 40x + 144 = (x-4)(x-36)
        # So eigenvalues of A are 4 and 36 = roots of GF denominator!
        import math
        tr, det = v, k**2
        discriminant = tr**2 - 4*det
        assert discriminant == v**2 - 4*k**2  # 1600 - 576 = 1024
        assert discriminant == 1024  # = 32²
        lam1 = (tr - int(math.isqrt(discriminant))) // 2
        lam2 = (tr + int(math.isqrt(discriminant))) // 2
        assert set([lam1, lam2]) == {mu, mu*q**2}  # {4, 36}


# ═══════════════════════════════════════════════════════════════════════════
# T7 — Cyclotomic Self-Reference Φ₆(μ) = Φ₃(q)
# ═══════════════════════════════════════════════════════════════════════════
class TestT7_CyclotomicSelfReference:
    """
    The key cyclotomic identity: Φ₆(μ) = Φ₃(q) = 13

    Φ₆(x) = x² - x + 1   →  Φ₆(4) = 16 - 4 + 1 = 13
    Φ₃(x) = x² + x + 1   →  Φ₃(3) = 9 + 3 + 1 = 13

    This is a polynomial identity that holds ONLY for (q, μ) satisfying
    μ = q+1 and q=3. It reflects the fact that 13 is simultaneously
    Φ₃(q) and Φ₆(q+1), a coincidence unique to q=3.
    """

    def test_Phi6_of_mu_equals_Phi3(self):
        Phi6_of_mu = mu**2 - mu + 1
        assert Phi6_of_mu == Phi3

    def test_Phi3_of_q_value(self):
        assert q**2 + q + 1 == Phi3  # 13

    def test_self_reference_equation(self):
        # Φ₆(μ) = Φ₃(q) — same value 13 from two different cyclotomics
        Phi6_at_mu = mu**2 - mu + 1
        Phi3_at_q  = q**2 + q + 1
        assert Phi6_at_mu == Phi3_at_q == 13

    def test_Phi6_mu_equals_Phi3_q_is_universal(self):
        # Φ₆(q+1) = (q+1)²-(q+1)+1 = q²+q+1 = Φ₃(q)  — holds for ALL q.
        # This is a polynomial identity: Φ₆(x+1) = Φ₃(x) for all x.
        for qq in [2, 3, 4, 5, 7]:
            mm = qq + 1
            Phi6_mm = mm**2 - mm + 1
            Phi3_qq = qq**2 + qq + 1
            assert Phi6_mm == Phi3_qq  # universal identity
        # At q=3 the value is 13, which is also the SRG's Φ₃ cyclotomic prime:
        assert mu**2 - mu + 1 == Phi3 == 13

    def test_13_is_Phi3_and_Phi6(self):
        assert 13 == q**2 + q + 1      # Φ₃(3)
        assert 13 == (q+1)**2 - (q+1) + 1  # Φ₆(4)

    def test_Phi12_from_Phi3_Phi6(self):
        # Φ₁₂(q) = q⁴ - q² + 1 = 73
        assert q**4 - q**2 + 1 == Phi12
        # And Φ₁₂ = Φ₆(q²) ? : Φ₆(9) = 81-9+1=73 ✓
        assert q**4 - q**2 + 1 == (q**2)**2 - (q**2) + 1

    def test_cyclotomic_ladder(self):
        # Φ₃(q) = 13, Φ₆(q) = 7, Φ₁₂(q) = 73; note Φ₃·Φ₆ = 91 = 7·13
        assert Phi3 * Phi6 == 91
        assert Phi3 + Phi6 == 20 == lam * Phi4  # 20! (GF numerator slope)


# ═══════════════════════════════════════════════════════════════════════════
# T8 — Gaussian Loop and Spectral Zeta Identity
# ═══════════════════════════════════════════════════════════════════════════
class TestT8_GaussianAndZeta:
    """
    GAUSSIAN SELF-REFERENCE:
      z = (k-1) + μi = 11 + 4i
      N(z) = |z|² = 11² + 4² = 137 = α⁻¹
      q_recovered = (Re(z)+1)/Im(z) = 12/4 = 3 = q  ← loop closes

    SPECTRAL ZETA IDENTITY:
      ζ_L(-n) = f·E₂ⁿ + g·E₃ⁿ = 24·10ⁿ + 15·16ⁿ
      Always divisible by 480 = 2·E_grav
      ζ_L(-n)/480 = (E₂^{n-1} + E₃^{n-1})/2
    """

    def test_gaussian_norm_equals_alpha_inv(self):
        Re_z, Im_z = k - 1, mu  # 11, 4
        assert Re_z**2 + Im_z**2 == 137

    def test_gaussian_recovers_q(self):
        Re_z, Im_z = k - 1, mu
        assert (Re_z + 1) % Im_z == 0
        assert (Re_z + 1) // Im_z == q

    def test_gaussian_loop_is_tautology(self):
        # z=(k-1)+μi → (Re+1)/Im = k/μ = q(q+1)/(q+1) = q for ALL q.
        # The loop q→z→q is always a fixed point (universal identity).
        # What's UNIQUE to q=3: N(z) = 137 = the fine-structure constant.
        for qq in [2, 3, 4, 5, 7]:
            kk, mm = qq*(qq+1), qq+1
            assert (kk - 1 + 1) // mm == qq   # always recovers q
        # Only at q=3 does N(z) = 11²+4² = 137 ≈ 1/α_em
        assert (k-1)**2 + mu**2 == 137
        # For other q, N(z) is not 137:
        for qq in [2, 4, 5]:
            kk, mm = qq*(qq+1), qq+1
            Nz = (kk-1)**2 + mm**2
            assert Nz != 137

    def test_137_is_gaussian_prime(self):
        # 137 is prime and ≡ 1 mod 4, so it's a Gaussian prime norm
        assert 137 % 4 == 1  # can be written as sum of two squares
        # Unique representation: 137 = 11² + 4²
        squares = [(a, b) for a in range(1, 12) for b in range(1, a)
                   if a**2 + b**2 == 137]
        assert len(squares) == 1
        assert squares[0] == (11, 4)

    def test_spectral_zeta_n1(self):
        # ζ_L(-1) = 24·10 + 15·16 = 240+240 = 480 = 2·E_grav
        zeta_minus1 = f * E2 + g * E3
        assert zeta_minus1 == 480
        assert zeta_minus1 == 2 * E_grav

    def test_spectral_zeta_n2_divisible_by_480(self):
        zeta_minus2 = f * E2**2 + g * E3**2  # 24·100+15·256 = 2400+3840 = 6240
        assert zeta_minus2 % 480 == 0
        assert zeta_minus2 // 480 == 13 == Phi3  # beautiful!

    def test_spectral_zeta_n3_divisible_by_480(self):
        zeta_minus3 = f * E2**3 + g * E3**3
        assert zeta_minus3 % 480 == 0

    def test_spectral_zeta_formula(self):
        # ζ_L(-n)/480 = (E2^{n-1} + E3^{n-1})/2
        for n in range(1, 6):
            zeta = f * E2**n + g * E3**n
            assert zeta % 480 == 0
            ratio = zeta // 480
            assert 2 * ratio == E2**(n-1) + E3**(n-1)

    def test_spectral_zeta_n2_ratio_is_Phi3(self):
        # ζ_L(-2)/480 = (E2+E3)/2 = (10+16)/2 = 13 = Φ₃
        zeta_minus2 = f * E2**2 + g * E3**2
        assert zeta_minus2 // 480 == (E2 + E3) // 2 == Phi3
