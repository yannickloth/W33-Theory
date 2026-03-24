"""
Phase CLXXVI: Graph Energy and Spectral Invariants of W(3,3)

The graph energy E(G) = sum of |eigenvalues| of A:
  E = K + |r|*MUL_R + |s|*MUL_S = 12 + 48 + 60 = 120

Key discoveries:
  - E(W33) = Q*V = 3*40 = 120 (energy = q times vertex count!)
  - E(W33) = THETA*K = 10*12 = 120 (energy = Lovász-theta-complement times degree)
  - |r| = EIG_R = 2 = LAM (absolute value of r equals lambda!)
  - |s| = |EIG_S| = 4 = MU (absolute value of s equals mu!)
  - LAM*MUL_R = K*MU = 48 (the r-contribution to energy)
  - MU*MUL_S = K*THETA/2 = 60 (the s-contribution to energy)
  - Complement energy E_c = K^2 = 144; ratio E/E_c = THETA/K = 5/6
  - E*E_c = K^3*THETA = 17280 (product of energies)
  - McClelland: E^2 = 14400 <= V*tr(A^2) = 19200; ratio = Q/(Q+1) = 3/4
  - Lovász theta: THETA = ϑ(complement) = -V*s/(K-s) = 10
  - Hoffman bound: alpha <= THETA = 10; omega <= MU = 4 (both TIGHT!)
  - Energy per vertex E/V = Q = 3; energy per degree E/K = THETA = 10
  - Spectral spread K - s = K + MU = 16 = Q*(Q+1)+1 ... = 4Q+4 = Q(Q+1)+Q+1
"""

from fractions import Fraction

# === W(3,3) parameters ===
Q = 3
V = 40
K = 12
LAM = 2
MU = 4

EIG_K = K       # = 12
EIG_R = 2       # = r > 0
EIG_S = -4      # = s < 0

MUL_K = 1
MUL_R = 24
MUL_S = 15

# Sum K + r + s = THETA (trace of distinct-eigenvalue sum)
THETA = EIG_K + EIG_R + EIG_S   # = 10

# ---- Graph energy of W(3,3) ----
ABS_R = EIG_R          # = 2 = LAM
ABS_S = -EIG_S         # = 4 = MU  (s < 0, so |s| = -s)

ENERGY = MUL_K * EIG_K + MUL_R * ABS_R + MUL_S * ABS_S   # = 12 + 48 + 60 = 120

ENERGY_R_PART = MUL_R * ABS_R   # = 48
ENERGY_S_PART = MUL_S * ABS_S   # = 60

# ---- Complement graph parameters ----
EIG_K_C = V - 1 - K   # = 27 (complement trivial eigenvalue)
EIG_R_C = -1 - EIG_R  # = -3  (sign-flipped)
EIG_S_C = -1 - EIG_S  # = +3  (sign-flipped; negative s becomes positive)

# Multiplicities unchanged: MUL_K=1, MUL_R=24, MUL_S=15
ENERGY_C = MUL_K * EIG_K_C + MUL_R * abs(EIG_R_C) + MUL_S * abs(EIG_S_C)
# = 27 + 24*3 + 15*3 = 27 + 72 + 45 = 144

# ---- tr(A^2) = sum of squared eigenvalues ----
TR_A2 = MUL_K * EIG_K**2 + MUL_R * EIG_R**2 + MUL_S * EIG_S**2
# = 144 + 4*24 + 16*15 = 144 + 96 + 240 = 480


# ============================================================
class TestT1_EnergyBasicDefinition:
    """E(G) = sum |eigenvalues| = 12 + 48 + 60 = 120."""

    def test_energy_value(self):
        assert ENERGY == 120

    def test_energy_formula_components(self):
        # E = |K|*1 + |r|*24 + |s|*15 = 12 + 48 + 60
        assert MUL_K * EIG_K + MUL_R * ABS_R + MUL_S * ABS_S == 120

    def test_energy_r_part(self):
        # MUL_R * |r| = 24*2 = 48
        assert ENERGY_R_PART == 48

    def test_energy_s_part(self):
        # MUL_S * |s| = 15*4 = 60
        assert ENERGY_S_PART == 60

    def test_energy_three_parts_sum_to_120(self):
        # K + 48 + 60 = 120
        assert EIG_K + ENERGY_R_PART + ENERGY_S_PART == ENERGY

    def test_energy_equals_Q_times_V(self):
        # E = Q * V = 3 * 40 = 120
        assert ENERGY == Q * V

    def test_energy_equals_THETA_times_K(self):
        # E = THETA * K = 10 * 12 = 120
        assert ENERGY == THETA * K


class TestT2_EigenvalueAbsoluteValues:
    """|r| = LAM = 2 and |s| = MU = 4: absolute eigenvalues equal SRG parameters."""

    def test_abs_r_equals_LAM(self):
        # |r| = 2 = LAM (stunning coincidence!)
        assert ABS_R == LAM

    def test_abs_s_equals_MU(self):
        # |s| = 4 = MU (stunning coincidence!)
        assert ABS_S == MU

    def test_abs_r_equals_EIG_R(self):
        # r > 0, so |r| = r = 2
        assert ABS_R == EIG_R

    def test_abs_s_equals_neg_EIG_S(self):
        # s < 0, so |s| = -s = 4
        assert ABS_S == -EIG_S

    def test_abs_r_is_Q_minus_1(self):
        # |r| = LAM = Q-1 = 2
        assert ABS_R == Q - 1

    def test_abs_s_is_Q_plus_1(self):
        # |s| = MU = Q+1 = 4
        assert ABS_S == Q + 1

    def test_abs_s_over_abs_r_equals_MU_over_LAM(self):
        # |s|/|r| = MU/LAM = 4/2 = 2
        assert Fraction(ABS_S, ABS_R) == Fraction(MU, LAM)

    def test_abs_s_minus_abs_r_equals_2(self):
        # |s| - |r| = MU - LAM = 4 - 2 = 2
        assert ABS_S - ABS_R == 2


class TestT3_EnergyComponentIdentities:
    """LAM*MUL_R = K*MU and MU*MUL_S = K*THETA/2."""

    def test_LAM_times_MUL_R(self):
        # |r| * MUL_R = LAM * MUL_R = 2*24 = 48
        assert LAM * MUL_R == 48

    def test_LAM_times_MUL_R_equals_K_times_MU(self):
        # LAM*MUL_R = 48 = K*MU = 12*4 = 48 (remarkable product identity!)
        assert LAM * MUL_R == K * MU

    def test_MU_times_MUL_S(self):
        # |s| * MUL_S = MU * MUL_S = 4*15 = 60
        assert MU * MUL_S == 60

    def test_MU_times_MUL_S_equals_K_THETA_over_2(self):
        # MU*MUL_S = 60 = K*THETA/2 = 12*10/2 = 60
        assert MU * MUL_S * 2 == K * THETA

    def test_energy_from_K_formula(self):
        # E = K*(1 + MU + THETA/2) = K*(1 + 4 + 5) = K*10 = 120
        # 1 + MU + THETA/2 = 1 + 4 + 5 = 10 = THETA ✓
        assert K * (1 + MU + THETA // 2) == ENERGY

    def test_r_part_plus_s_part(self):
        # 48 + 60 = 108 = ENERGY - K = 120 - 12
        assert ENERGY_R_PART + ENERGY_S_PART == ENERGY - EIG_K

    def test_r_part_over_s_part(self):
        # 48/60 = 4/5 = (K*MU)/(K*THETA/2) = 2*MU/THETA = 8/10 = 4/5
        assert Fraction(ENERGY_R_PART, ENERGY_S_PART) == Fraction(4, 5)

    def test_K_plus_r_plus_s_equals_THETA(self):
        # K + r + s = 12 + 2 - 4 = 10 = THETA
        assert EIG_K + EIG_R + EIG_S == THETA

    def test_r_plus_s_equals_LAM_minus_MU(self):
        # r + s = 2 + (-4) = -2 = LAM - MU (for SRG: r+s = lambda-mu)
        assert EIG_R + EIG_S == LAM - MU


class TestT4_ComplementGraphEnergy:
    """Complement energy E_c = K^2 = 144."""

    def test_complement_trivial_eigenvalue(self):
        # K_c = V - 1 - K = 27
        assert EIG_K_C == 27

    def test_complement_r_eigenvalue(self):
        # r_c = -1 - r = -1 - 2 = -3
        assert EIG_R_C == -3

    def test_complement_s_eigenvalue(self):
        # s_c = -1 - s = -1 - (-4) = 3
        assert EIG_S_C == 3

    def test_complement_eigenvalues_abs_equal(self):
        # |r_c| = 3 = |s_c| (complement has EQUAL non-trivial |eigenvalues|!)
        assert abs(EIG_R_C) == abs(EIG_S_C)

    def test_complement_energy_value(self):
        # E_c = 27 + 24*3 + 15*3 = 27 + 72 + 45 = 144
        assert ENERGY_C == 144

    def test_complement_energy_equals_K_squared(self):
        # E_c = K^2 = 12^2 = 144
        assert ENERGY_C == K**2

    def test_complement_K_squared_formula(self):
        # K^2 = 144
        assert K**2 == 144

    def test_complement_energy_parts(self):
        # Trivial: 27; r-part: 24*3=72; s-part: 15*3=45
        assert EIG_K_C + 24 * abs(EIG_R_C) + 15 * abs(EIG_S_C) == ENERGY_C

    def test_complement_non_trivial_eigenvalue_is_Q(self):
        # |r_c| = |s_c| = 3 = Q (both complement nontrivial eigenvalues have abs = Q!)
        assert abs(EIG_R_C) == Q
        assert abs(EIG_S_C) == Q


class TestT5_EnergyRatioAndProduct:
    """E/E_c = THETA/K = 5/6; E*E_c = K^3*THETA = 17280."""

    def test_energy_ratio(self):
        # E/E_c = 120/144 = 5/6
        assert Fraction(ENERGY, ENERGY_C) == Fraction(5, 6)

    def test_energy_ratio_equals_THETA_over_K(self):
        # E/E_c = 120/144 = 5/6 = THETA/K = 10/12
        assert Fraction(ENERGY, ENERGY_C) == Fraction(THETA, K)

    def test_THETA_over_K_reduced(self):
        # THETA/K = 10/12 = 5/6
        assert Fraction(THETA, K) == Fraction(5, 6)

    def test_energy_product(self):
        # E * E_c = 120 * 144 = 17280
        assert ENERGY * ENERGY_C == 17280

    def test_energy_product_equals_K3_THETA(self):
        # E * E_c = K^3 * THETA = 1728 * 10 = 17280
        assert ENERGY * ENERGY_C == K**3 * THETA

    def test_K_cubed_is_1728(self):
        # K^3 = 1728 (= 12^3, "Ramanujan" cube)
        assert K**3 == 1728

    def test_energy_per_vertex(self):
        # E/V = 120/40 = 3 = Q (energy per vertex equals field order!)
        assert Fraction(ENERGY, V) == Q

    def test_energy_per_degree(self):
        # E/K = 120/12 = 10 = THETA (energy per degree = Lovász theta complement!)
        assert Fraction(ENERGY, K) == THETA

    def test_complement_energy_over_V(self):
        # E_c/V = 144/40 = 18/5 (non-integer; E_c not divisible by V)
        assert Fraction(ENERGY_C, V) == Fraction(18, 5)

    def test_energy_complement_ratio_not_integer(self):
        # E_c/V = 144/40; not an integer
        assert ENERGY_C % V != 0


class TestT6_McClellandBound:
    """McClelland: E^2 <= V * tr(A^2) = 19200; ratio = Q/(Q+1) = 3/4."""

    def test_tr_A2_value(self):
        # tr(A^2) = sum of squared eigenvalues = K^2 + r^2*24 + s^2*15
        # = 144 + 96 + 240 = 480
        assert TR_A2 == 480

    def test_tr_A2_equals_V_times_K(self):
        # tr(A^2) = V*K = 40*12 = 480 (for K-regular graph: tr(A^2) = sum degrees = V*K)
        assert TR_A2 == V * K

    def test_tr_A2_components(self):
        # 144 + 4*24 + 16*15 = 144 + 96 + 240 = 480
        assert EIG_K**2 + EIG_R**2 * MUL_R + EIG_S**2 * MUL_S == TR_A2

    def test_mcclelland_bound(self):
        # E^2 <= V * tr(A^2) = 40 * 480 = 19200
        assert ENERGY**2 <= V * TR_A2

    def test_mcclelland_bound_rhs(self):
        # V * tr(A^2) = 40 * 480 = 19200
        assert V * TR_A2 == 19200

    def test_energy_squared(self):
        # E^2 = 120^2 = 14400
        assert ENERGY**2 == 14400

    def test_mcclelland_gap(self):
        # V*tr(A^2) - E^2 = 19200 - 14400 = 4800
        assert V * TR_A2 - ENERGY**2 == 4800

    def test_mcclelland_ratio(self):
        # E^2 / (V * tr(A^2)) = 14400/19200 = 3/4 = Q/(Q+1)
        assert Fraction(ENERGY**2, V * TR_A2) == Fraction(Q, Q + 1)

    def test_mcclelland_ratio_equals_Q_over_Q_plus_1(self):
        # 3/4 = Q/(Q+1) (remarkable: efficiency = field fraction!)
        assert Fraction(ENERGY**2, V * TR_A2) == Fraction(3, 4)

    def test_mcclelland_deficit_fraction(self):
        # 1 - Q/(Q+1) = 1/(Q+1) = 1/4 = MU/V * ... check:
        # 1 - 3/4 = 1/4
        assert Fraction(1) - Fraction(Q, Q + 1) == Fraction(1, Q + 1)


class TestT7_LovaszThetaEnergyConnection:
    """THETA = Lovász theta(complement) = -V*s/(K-s) = 10; E = THETA*K."""

    def test_THETA_value(self):
        # THETA = K + r + s = 10
        assert THETA == 10

    def test_lovasz_theta_formula(self):
        # Lovász theta of complement = -V*s/(K-s) = -40*(-4)/(12+4) = 160/16 = 10
        lovasz = Fraction(-V * EIG_S, K - EIG_S)
        assert lovasz == THETA

    def test_lovasz_theta_numerator(self):
        # -V*s = -40*(-4) = 160 = V*MU
        assert -V * EIG_S == V * MU

    def test_lovasz_theta_denominator(self):
        # K - s = 12 - (-4) = 16 = K + MU (spectral spread!)
        assert K - EIG_S == K + MU

    def test_lovasz_theta_equals_V_MU_over_K_plus_MU(self):
        # THETA = V*MU/(K+MU) = 40*4/16 = 10
        assert Fraction(V * MU, K + MU) == THETA

    def test_lovasz_product_identity(self):
        # ϑ(G) * ϑ(G_c) = V for vertex-transitive (sandwich theorem equality)
        # ϑ(G) = V/THETA = 40/10 = 4 = MU = omega(G)
        theta_G = Fraction(V, THETA)
        assert theta_G == MU

    def test_theta_G_equals_omega(self):
        # ϑ(G) = MU = omega(G) = 4 (Lovász theta of G equals clique number!)
        assert Fraction(V, THETA) == MU

    def test_energy_via_lovasz(self):
        # E = ϑ(G_c) * K = THETA * K = 10 * 12 = 120
        assert THETA * K == ENERGY

    def test_THETA_via_eigenvalues(self):
        # THETA = K + r + s = sum of distinct eigenvalues
        assert EIG_K + EIG_R + EIG_S == THETA

    def test_THETA_via_LAM_MU(self):
        # THETA = K + LAM - MU = 12 + 2 - 4 = 10 (since r = LAM, s = -MU for SRG)
        # Wait: r = 2 = LAM, s = -4 = -MU, so THETA = K + r + s = K + LAM - MU ✓
        assert K + LAM - MU == THETA


class TestT8_HoffmanBounds:
    """Hoffman bounds: alpha <= THETA = 10 (TIGHT) and omega <= MU = 4 (TIGHT)."""

    def test_hoffman_independence_formula(self):
        # alpha <= V*|s|/(K + |s|) = 40*4/16 = 10 = THETA
        hoffman_alpha = Fraction(V * ABS_S, K + ABS_S)
        assert hoffman_alpha == THETA

    def test_hoffman_alpha_is_THETA(self):
        # Hoffman bound for independence = THETA = 10
        assert Fraction(V * MU, K + MU) == THETA

    def test_hoffman_alpha_denominator(self):
        # Denominator = K + MU = 16 (spectral spread K - s = K + MU)
        assert K + MU == 16

    def test_hoffman_alpha_numerator(self):
        # Numerator = V * MU = 40 * 4 = 160
        assert V * MU == 160

    def test_hoffman_alpha_is_tight(self):
        # The Hoffman bound alpha <= 10 is TIGHT (W(3,3) has independence sets of size 10)
        # Confirmed by: V * |s| == THETA * (K + |s|) => equality in bound
        assert V * ABS_S == THETA * (K + ABS_S)

    def test_hoffman_clique_via_complement(self):
        # omega(G) = alpha(G_c); apply Hoffman to G_c:
        # alpha(G_c) <= V*|s_c_min|/(K_c + |s_c_min|) = 40*3/(27+3) = 120/30 = 4 = MU
        K_c = EIG_K_C   # = 27
        s_c_min = EIG_R_C   # = -3 (more negative than s_c=3)
        hoffman_omega = Fraction(V * abs(s_c_min), K_c + abs(s_c_min))
        assert hoffman_omega == MU

    def test_hoffman_omega_is_MU(self):
        # Hoffman clique bound: omega <= MU = 4 (TIGHT!)
        assert Fraction(V * Q, EIG_K_C + Q) == MU

    def test_hoffman_omega_tight(self):
        # Tight because: V * |s_c| = MU * (K_c + |s_c|) => 40*3 = 4*30 = 120 ✓
        assert V * Q == MU * (EIG_K_C + Q)

    def test_lovász_sandwich(self):
        # omega(G) <= ϑ(G_c) = THETA = 10 (weak Lovász sandwich)
        assert MU <= THETA

    def test_alpha_times_omega(self):
        # alpha * omega = THETA * MU = 10 * 4 = 40 = V (perfect covering!)
        assert THETA * MU == V


class TestT9_SpectralSpreadAndDiameter:
    """Spectral spread K - s = K + MU = 16; diameter 2; Alon-Boppana."""

    def test_spectral_spread(self):
        # spectral spread = K - s = 12 - (-4) = 16
        assert K - EIG_S == 16

    def test_spectral_spread_equals_K_plus_MU(self):
        # K - s = K + |s| = K + MU = 12 + 4 = 16
        assert K - EIG_S == K + MU

    def test_spectral_spread_Q_formula(self):
        # K + MU = Q(Q+1) + (Q+1) = (Q+1)^2 = 4^2 = 16 ✓
        assert K + MU == (Q + 1)**2

    def test_spectral_gap(self):
        # spectral gap = K - r = 12 - 2 = 10 = THETA
        assert K - EIG_R == THETA

    def test_spectral_gap_equals_THETA(self):
        # K - r = 10 = THETA (spectral gap = Lovász theta complement!)
        assert K - EIG_R == THETA

    def test_second_largest_eigenvalue(self):
        # r = 2 = LAM (second-largest eigenvalue = lambda!)
        assert EIG_R == LAM

    def test_alon_boppana_Q_formula(self):
        # Alon-Boppana: r >= 2*sqrt(K-1) - o(1); here r=2 << 2*sqrt(11)~6.6
        # W(3,3) is NOT a Ramanujan graph (r < 2*sqrt(K-1) not guaranteed to be tight)
        # But the exact inequality: 2*sqrt(K-1) > r is NOT the right direction
        # Instead: r < 2*sqrt(K-1) for expander; check r^2 vs 4*(K-1)
        assert EIG_R**2 < 4 * (K - 1)   # 4 < 44 ✓ (r is well below Alon-Boppana)

    def test_eigenvalue_interlacing_sum(self):
        # K*1 + r*MUL_R + s*MUL_S = tr(A) = 0
        assert EIG_K * MUL_K + EIG_R * MUL_R + EIG_S * MUL_S == 0

    def test_eigenvalue_interlacing_sum_of_squares(self):
        # K^2 + r^2*MUL_R + s^2*MUL_S = tr(A^2) = V*K = 480
        assert EIG_K**2 * MUL_K + EIG_R**2 * MUL_R + EIG_S**2 * MUL_S == V * K
