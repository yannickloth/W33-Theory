"""
Phase CLXXXIII: Eigenvalue Multiplicity Formulas from Trace Equations of W(3,3)

The multiplicities f=MUL_R=24 and g=MUL_S=15 are uniquely determined by the
two linear trace equations. Several clean Q-polynomial formulas emerge.

Key discoveries:
  - System: f+g = V-1 = 39; r*f + s*g = -K = -12 (from tr(A^0)=V and tr(A)=0)
  - Solution: f = K*MU/2 = Q*(Q+1)^2/2 = 24; g = Q*(Q^2+1)/2 = 15
  - f = K^2/(r-s) = K^2/(2Q) = 144/6 = 24 (degree squared over eigenvalue gap!)
  - g = (K + LAM*(V-1))/(r-s) = Q^2*(Q^2+1)/(2Q) = Q*(Q^2+1)/2 = 15
  - Cramers: f = (-K - s*(V-1))/(r-s); g = (-K - r*(V-1))/(s-r) = 15
  - f = MUL_R = 2*Q*(Q+1) = 2*K?? No: 2*Q*(Q+1) = 24 = f ✓!
    Actually f = 2*Q*(Q+1)... is that right? 2*3*4=24 ✓! But from the formula: Q*(Q+1)^2/2 = 3*16/2=24 ✓.
    And 2*Q*(Q+1) = 2*12 = 24... and Q*(Q+1)^2/2 = Q*(Q+1)*(Q+1)/2 = K*MU/2 = 12*4/2 = 24 ✓.
  - Special Q=3 coincidence: Q^2+1 = 10 = THETA (only at Q=3!)
    → g = Q*THETA/2 = 3*10/2 = 15 (specific to Q=3!)
  - Newton identity p2: tr(A^2) = K^2 + r^2*f + s^2*g = V*K = 480
    → K^2*(1+f*r^2/K^2+g*s^2/K^2) = V*K confirms consistency
  - Third trace: K^3 + r^3*f + s^3*g = tr(A^3) = 960 (triangles check)
  - f/g = 24/15 = 8/5 = K*MU / (Q*(Q^2+1)) = K*MU / (Q*(ALPHA))
"""

from fractions import Fraction

# === W(3,3) parameters ===
Q = 3
V = 40
K = 12
LAM = 2
MU = 4

EIG_K = K
EIG_R = 2
EIG_S = -4

MUL_K = 1
MUL_R = 24
MUL_S = 15

THETA = EIG_K + EIG_R + EIG_S   # = 10
ALPHA = THETA    # alpha = THETA = 10 (Lovász theta bound, tight; specific to Q=3: Q^2+1=10=THETA)


# ============================================================
class TestT1_TraceSystemSetup:
    """The 2x2 linear system for f and g from tr(A)=0 and 1+f+g=V."""

    def test_trace_A0_identity(self):
        # tr(A^0) = tr(I) = V: 1 + f + g = V
        assert MUL_K + MUL_R + MUL_S == V

    def test_trace_A1_identity(self):
        # tr(A) = 0: K*1 + r*f + s*g = 0
        assert EIG_K * MUL_K + EIG_R * MUL_R + EIG_S * MUL_S == 0

    def test_f_plus_g_equals_V_minus_1(self):
        # f + g = V - 1 = 39
        assert MUL_R + MUL_S == V - 1

    def test_r_f_plus_s_g_equals_neg_K(self):
        # r*f + s*g = -K = -12
        assert EIG_R * MUL_R + EIG_S * MUL_S == -EIG_K

    def test_linear_system_determinant(self):
        # det([[1,1],[r,s]]) = s - r = -4 - 2 = -6 = -(r-s) = -2Q ≠ 0 (system has unique solution)
        det = EIG_S - EIG_R
        assert det == -6
        assert det == -(EIG_R - EIG_S)
        assert det == -2 * Q

    def test_system_rhs_values(self):
        # RHS: [V-1, -K] = [39, -12]
        assert V - 1 == 39
        assert -EIG_K == -12


class TestT2_CramerFormulas:
    """Cramers rule: f = (-K - s*(V-1))/(r-s); g = (-K - r*(V-1))/(s-r)."""

    def test_f_cramer_formula(self):
        # f = (-K - s*(V-1)) / (r-s) = (-12 - (-4)*39) / 6 = (-12+156)/6 = 144/6 = 24
        numerator_f = -EIG_K - EIG_S * (V - 1)
        denom = EIG_R - EIG_S
        assert numerator_f == 144
        assert denom == 6
        assert numerator_f // denom == MUL_R

    def test_g_cramer_formula(self):
        # g = (-K - r*(V-1)) / (s-r) = (-12 - 2*39) / (-6) = (-90)/(-6) = 15
        numerator_g = -EIG_K - EIG_R * (V - 1)
        denom = EIG_S - EIG_R
        assert numerator_g == -90
        assert denom == -6
        assert numerator_g // denom == MUL_S

    def test_f_numerator_value(self):
        # -K - s*(V-1) = -12 + 4*39 = -12 + 156 = 144
        assert -EIG_K - EIG_S * (V - 1) == 144

    def test_g_numerator_value(self):
        # -K - r*(V-1) = -12 - 2*39 = -12 - 78 = -90
        assert -EIG_K - EIG_R * (V - 1) == -90

    def test_f_numerator_Q_formula(self):
        # -K - s*(V-1) = MU*(V-1) - K = 4*39 - 12 = 144 = K^2 ✓ (K^2 = 144!)
        assert MU * (V - 1) - EIG_K == 144
        assert MU * (V - 1) - EIG_K == EIG_K**2

    def test_g_numerator_Q_formula(self):
        # -K - r*(V-1) = -(K + LAM*(V-1)) = -(12 + 2*39) = -90 = -Q^2*(Q^2+1)
        assert EIG_K + LAM * (V - 1) == 90
        assert EIG_K + LAM * (V - 1) == Q**2 * (Q**2 + 1)


class TestT3_CleanFormulas:
    """f = K^2/(2Q) = 24; g = Q*(Q^2+1)/2 = 15."""

    def test_f_equals_K_squared_over_2Q(self):
        # f = K^2 / (r-s) = K^2 / (2Q) = 144/6 = 24
        assert Fraction(EIG_K**2, EIG_R - EIG_S) == MUL_R

    def test_f_K_squared_over_eigenvalue_gap(self):
        # f = K^2/(r-s) = 144/6 = 24 (degree squared over eigenvalue gap!)
        assert EIG_K**2 // (EIG_R - EIG_S) == MUL_R

    def test_f_Q_formula_1(self):
        # f = Q*(Q+1)^2/2 = 3*16/2 = 24
        assert Q * (Q + 1)**2 // 2 == MUL_R

    def test_f_Q_formula_2(self):
        # f = K*MU/2 = 12*4/2 = 24 (degree × non-adjacency parameter / 2!)
        assert EIG_K * MU // 2 == MUL_R

    def test_f_Q_formula_3(self):
        # f = 2*Q*(Q+1) = 2*12 = 24 ✓ (also works!)
        assert 2 * Q * (Q + 1) == MUL_R

    def test_g_Q_formula(self):
        # g = Q*(Q^2+1)/2 = 3*10/2 = 15
        assert Q * (Q**2 + 1) // 2 == MUL_S

    def test_g_via_THETA_Q3_magic(self):
        # At Q=3: Q^2+1 = 10 = THETA (specific to Q=3!) → g = Q*THETA/2 = 3*10/2 = 15
        assert Q**2 + 1 == THETA   # Q=3 magic: Q^2+1 = THETA
        assert Q * THETA // 2 == MUL_S

    def test_g_numerator_equals_Q_squared_times_Q_squared_plus_1(self):
        # K + LAM*(V-1) = Q^2*(Q^2+1) = 9*10 = 90
        assert EIG_K + LAM * (V - 1) == Q**2 * (Q**2 + 1)


class TestT4_MultiplicityRelations:
    """f/g = K*MU / (Q*(Q^2+1)) = 8/5; various ratios and products."""

    def test_f_over_g_ratio(self):
        # f/g = 24/15 = 8/5
        assert Fraction(MUL_R, MUL_S) == Fraction(8, 5)

    def test_f_over_g_Q_formula(self):
        # f/g = K*MU / (Q*(Q^2+1)) = 12*4 / (3*10) = 48/30 = 8/5
        assert Fraction(EIG_K * MU, Q * (Q**2 + 1)) == Fraction(8, 5)

    def test_f_times_g(self):
        # f*g = 24*15 = 360
        assert MUL_R * MUL_S == 360

    def test_f_times_g_Q_formula(self):
        # f*g = Q^2*(Q+1)^2*(Q^2+1)/4 = 9*16*10/4 = 1440/4 = 360
        assert Q**2 * (Q + 1)**2 * (Q**2 + 1) // 4 == 360

    def test_f_plus_g(self):
        # f + g = 39 = V - 1
        assert MUL_R + MUL_S == V - 1

    def test_f_minus_g(self):
        # f - g = 24 - 15 = 9 = Q^2
        assert MUL_R - MUL_S == Q**2

    def test_f_minus_g_equals_Q_squared(self):
        # f - g = Q^2 = 9 (remarkable: difference = field order squared!)
        assert MUL_R - MUL_S == Q**2

    def test_f_times_r_sq_plus_g_times_s_sq(self):
        # f*r^2 + g*s^2 = 24*4 + 15*16 = 96+240 = 336 = V*K - K^2 = 480-144
        assert MUL_R * EIG_R**2 + MUL_S * EIG_S**2 == V * EIG_K - EIG_K**2


class TestT5_TraceVerification:
    """Verify multiplicities through tr(A^2), tr(A^3) power sums."""

    def test_trace_A2_check(self):
        # K^2 + r^2*f + s^2*g = tr(A^2) = V*K = 480
        assert EIG_K**2 + EIG_R**2 * MUL_R + EIG_S**2 * MUL_S == V * EIG_K

    def test_trace_A3_check(self):
        # K^3 + r^3*f + s^3*g = tr(A^3) = 960 = 6 * triangles
        tr_A3 = EIG_K**3 + EIG_R**3 * MUL_R + EIG_S**3 * MUL_S
        assert tr_A3 == 960

    def test_r2_f_contribution(self):
        # r^2 * f = 4 * 24 = 96 = K * MU = 48 * 2? No: 12*8=96 ✓
        assert EIG_R**2 * MUL_R == EIG_K * MU * 2
        assert EIG_R**2 * MUL_R == 96

    def test_s2_g_contribution(self):
        # s^2 * g = 16 * 15 = 240 = K * Q^2 * (Q+1)? = 12*9*? hmm
        # 240 = V*K - K^2 - r^2*f = 480 - 144 - 96 = 240 ✓
        assert EIG_S**2 * MUL_S == V * EIG_K - EIG_K**2 - EIG_R**2 * MUL_R

    def test_fourth_power_trace(self):
        # K^4 + r^4*f + s^4*g = tr(A^4) = 24960
        tr_A4 = EIG_K**4 + EIG_R**4 * MUL_R + EIG_S**4 * MUL_S
        assert tr_A4 == 24960

    def test_fourth_power_from_recurrence(self):
        # p_4 = THETA*p_3 + 32*p_2 - 96*p_1 = 10*960 + 32*480 - 0 = 9600+15360 = 24960
        p3 = 960
        p2 = V * EIG_K
        p1 = 0
        p4 = THETA * p3 + (MU * (EIG_K - MU)) * p2 - (EIG_K * (EIG_K - MU)) * p1
        assert p4 == 24960


class TestT6_MultiplicitiesAsDimensions:
    """f, g as dimensions of eigenspaces; all V = 1 + f + g = 40."""

    def test_total_dimension(self):
        # Sum of all eigenspace dimensions = V
        assert MUL_K + MUL_R + MUL_S == V

    def test_MUL_K_is_1(self):
        # Trivial eigenspace has dimension 1 (W(3,3) is connected)
        assert MUL_K == 1

    def test_f_larger_than_g(self):
        # f = 24 > g = 15 (eigenspace with smaller |eigenvalue| is larger!)
        assert MUL_R > MUL_S

    def test_g_is_integer(self):
        # g = Q*(Q^2+1)/2 is an integer (Q*(Q^2+1) = 3*10 = 30, even since Q*THETA even)
        assert Q * (Q**2 + 1) % 2 == 0

    def test_f_is_integer(self):
        # f = Q*(Q+1)^2/2 is an integer (Q*(Q+1)^2 = 3*16 = 48, even)
        assert Q * (Q + 1)**2 % 2 == 0

    def test_Q_squared_plus_1_equals_THETA(self):
        # At Q=3: Q^2+1 = 9+1 = 10 = THETA (Q=3 magic!)
        assert Q**2 + 1 == THETA

    def test_multiplicities_determine_parameters(self):
        # Given f=24, g=15, we can recover r and s:
        # r = -(K + s*(V-1))/(f) and s = -(K + r*(V-1))/(g) ... via system
        # Check via f*(r-s) = K^2: 24*6 = 144 = K^2 ✓
        assert MUL_R * (EIG_R - EIG_S) == EIG_K**2
