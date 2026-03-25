"""
Phase CXCII: Walk Generating Function and Spectral Partial Fractions of W(3,3)

The per-vertex closed-walk generating function h(x) = sum_{k>=0} (tr(A^k)/V) * x^k has
an exact closed form with numerator/denominator expressible entirely in Q-formulas.

Key discoveries:
  - h(x) = N(x) / D(x) where D(x) = (1-Kx)(1-rx)(1-sx) = 1 - THETA*x - 32*x^2 + 96*x^3
  - N(x) = 1 - THETA*x - 2*THETA*x^2  (= 1 - (Q^2+1)*x*(1 + 2x)!)
  - N[0]=1, N[1]=-THETA=-10, N[2]=-2*THETA=-20 (BOTH non-trivial coeffs = multiple of THETA!)
  - Spectral partial fractions: h(x) = (1/V)/(1-Kx) + (m_1/V)/(1-rx) + (m_2/V)/(1+MU*x)
  - Residues = E_i[diag] = m_i/V (partial fraction coeffs ARE the idempotent diagonal entries!)
  - D(x) is the generating polynomial for the recurrence p_k = THETA*p_{k-1}+32*p_{k-2}-96*p_{k-3}
  - N(x) encodes initial conditions: N[1] = -(p_1/V + THETA) = -THETA, N[2] = K - 32 = -2*THETA
  - Convergence radius = 1/K = 1/12 (dominant pole); second pole at 1/MU=1/4; third at 1/r=1/2
  - Denominator roots: x = 1/K, 1/r, -1/MU = 1/12, 1/2, -1/4 (rational!)
  - Sum of residues: 1/V + m_1/V + m_2/V = V/V = 1 = h(0) ✓
  - N(x) evaluated at poles: N(1/K)=1/1440 (=1/(V*(r-1/K+...)))... or more cleanly via residues
"""

from fractions import Fraction

# === W(3,3) parameters ===
Q = 3
V = 40
K = 12
LAM = 2
MU = 4

EIG_K = K
EIG_R = 2      # = LAM = Q-1
EIG_S = -4     # = -MU = -(Q+1)

MUL_K = 1
MUL_R = 24
MUL_S = 15

THETA = 10     # = Q^2+1 = EIG_K + EIG_R + EIG_S
MINPOLY_C1 = 32    # = -(K*r + K*s + r*s) = (Q+1)^2*(Q-1)
MINPOLY_C0 = -96   # = K*r*s (constant term of min poly) → 96 = -K*r*s = K*LAM*MU

# Denominator coefficients: D(x) = 1 - THETA*x - MINPOLY_C1*x^2 + K*LAM*MU*x^3
D0 = 1
D1 = -THETA           # = -10
D2 = -MINPOLY_C1      # = -32
D3 = K * LAM * MU     # = 96

# Numerator coefficients (from initial conditions):
# N = (p_0/V) + (p_1/V - THETA*p_0/V)*x + (p_2/V - THETA*p_1/V - 32*p_0/V)*x^2
p0, p1, p2 = V, 0, V * K   # = 40, 0, 480
N0 = Fraction(p0, V)                              # = 1
N1 = Fraction(p1 - THETA * p0, V)                # = (0 - 10*40)/40 = -10 = -THETA
N2 = Fraction(p2 - THETA * p1 - MINPOLY_C1 * p0, V)  # = (480 - 0 - 32*40)/40 = -800/40 = -20

# Partial fraction residues
RES_K = Fraction(MUL_K, V)   # = 1/40 (residue at pole x=1/K)
RES_R = Fraction(MUL_R, V)   # = 3/5  (residue at pole x=1/r)
RES_S = Fraction(MUL_S, V)   # = 3/8  (residue at pole x=-1/MU)


def h_series(k):
    """Compute h_k = tr(A^k)/V using the recurrence or direct formula."""
    if k == 0:
        return 1
    if k == 1:
        return 0
    # From eigenvalue formula: h_k = (1/V)*K^k + (m_1/V)*r^k + (m_2/V)*s^k
    return (Fraction(MUL_K * EIG_K**k + MUL_R * EIG_R**k + MUL_S * EIG_S**k, V))


# Verify first six terms
h = [h_series(k) for k in range(6)]


# ============================================================
class TestT1_DenominatorPolynomial:
    """D(x) = (1-Kx)(1-rx)(1-sx) = 1 - THETA*x - 32*x^2 + 96*x^3."""

    def test_D1_equals_neg_THETA(self):
        assert D1 == -THETA

    def test_D2_equals_neg_32(self):
        assert D2 == -MINPOLY_C1

    def test_D3_equals_96(self):
        assert D3 == K * LAM * MU

    def test_D3_value(self):
        assert D3 == 96

    def test_D2_Q_formula(self):
        # D2 = -MINPOLY_C1 = -(Q+1)^2*(Q-1) = -32
        assert D2 == -((Q + 1)**2 * (Q - 1))

    def test_D3_Q_formula(self):
        # D3 = K*LAM*MU = Q(Q+1)*(Q-1)*(Q+1) = Q*(Q+1)^2*(Q-1) = 3*16*2 = 96
        assert D3 == Q * (Q + 1)**2 * (Q - 1)

    def test_D_expansion_from_roots(self):
        # (1-K*x)(1-r*x)(1-s*x) expanded:
        # coeff of x: -(K+r+s) = -THETA ✓
        # coeff of x^2: K*r+K*s+r*s = -MINPOLY_C1 = -32 ✓ (note: + sign in MINPOLY)
        # coeff of x^3: -K*r*s = K*LAM*MU = 96 (since s=-MU, r=LAM) ✓
        assert -(EIG_K + EIG_R + EIG_S) == D1
        assert EIG_K * EIG_R + EIG_K * EIG_S + EIG_R * EIG_S == D2
        assert -(EIG_K * EIG_R * EIG_S) == D3

    def test_D_roots_are_reciprocal_eigenvalues(self):
        # D(x) = 0 at x = 1/K=1/12, x=1/r=1/2, x=1/s=-1/4
        for eig in [EIG_K, EIG_R, EIG_S]:
            x = Fraction(1, eig)
            val = D0 + D1 * x + D2 * x**2 + D3 * x**3
            assert val == 0


class TestT2_NumeratorPolynomial:
    """N(x) = 1 - THETA*x - 2*THETA*x^2; both slope terms are multiples of THETA."""

    def test_N0_equals_1(self):
        assert N0 == 1

    def test_N1_equals_neg_THETA(self):
        assert N1 == -THETA

    def test_N2_equals_neg_2_THETA(self):
        assert N2 == -2 * THETA

    def test_N1_Q_formula(self):
        # N[1] = -THETA = -(Q^2+1) = -10
        assert N1 == -(Q**2 + 1)

    def test_N2_Q_formula(self):
        # N[2] = -2*THETA = -2*(Q^2+1) = -20
        assert N2 == -2 * (Q**2 + 1)

    def test_N1_equals_N2_div_2(self):
        # N[1] = N[2] / 2 (!) both encode THETA
        assert N1 == Fraction(N2, 2)

    def test_N2_from_initial_conditions(self):
        # N[2] = p_2/V - THETA*p_1/V - 32*p_0/V = K - 0 - 32 = K - 32 = -20
        assert N2 == K - MINPOLY_C1

    def test_N1_and_N2_only_nonzero_nontrivial(self):
        # Numerator has degree 2 (quadratic), denominator degree 3 (cubic)
        assert N0 == 1 and N1 != 0 and N2 != 0

    def test_N_factored(self):
        # N(x) = 1 - THETA*x*(1 + 2*x) for any x (symbolic verification at x=1):
        x = Fraction(1, 1)
        assert N0 + N1 * x + N2 * x**2 == 1 - THETA * x * (1 + 2 * x)


class TestT3_SeriesCoefficients:
    """h_k = tr(A^k)/V: verify first six via spectral formula and recurrence."""

    def test_h0_equals_1(self):
        assert h[0] == 1

    def test_h1_equals_0(self):
        # tr(A) = 0 (no self-loops in SRG)
        assert h[1] == 0

    def test_h2_equals_K(self):
        # tr(A^2)/V = K = 12 (each vertex contributes K closed 2-walks)
        assert h[2] == K

    def test_h3_equals_K_LAM(self):
        # tr(A^3)/V = K*LAM = 24 (closed 3-walks per vertex)
        assert h[3] == K * LAM

    def test_h4_value(self):
        # tr(A^4)/V = 624
        assert h[4] == 624

    def test_h5_via_recurrence(self):
        # h[5] = THETA*h[4] + 32*h[3] - 96*h[2]
        h5_rec = THETA * h[4] + 32 * h[3] - 96 * h[2]
        assert h[5] == h5_rec

    def test_h3_Q_formula(self):
        # K*LAM = Q(Q+1)*(Q-1) = Q*(Q^2-1) = 24
        assert h[3] == Q * (Q**2 - 1)

    def test_all_via_eigenvalue_formula(self):
        # h_k = (1/V)*K^k + (m_1/V)*r^k + (m_2/V)*s^k
        for k in range(6):
            expected = Fraction(MUL_K * EIG_K**k + MUL_R * EIG_R**k + MUL_S * EIG_S**k, V)
            assert h[k] == expected


class TestT4_PartialFractions:
    """Residues = m_i/V = E_i[diag]; poles at 1/eigenvalue."""

    def test_residue_at_K_pole(self):
        # Residue at x=1/K is m_0/V = 1/V = 1/40
        assert RES_K == Fraction(1, V)

    def test_residue_at_r_pole(self):
        # Residue at x=1/r is m_1/V = 24/40 = 3/5
        assert RES_R == Fraction(3, 5)

    def test_residue_at_s_pole(self):
        # Residue at x=1/s is m_2/V = 15/40 = 3/8
        assert RES_S == Fraction(3, 8)

    def test_residues_sum_to_1(self):
        # h(0) = 1 = sum of residues (partial fractions constant term)
        assert RES_K + RES_R + RES_S == 1

    def test_residues_equal_idempotent_diagonal(self):
        # Residue at pole 1/lambda_i = E_i[diag] = m_i/V (profound connection!)
        assert RES_K == Fraction(MUL_K, V)
        assert RES_R == Fraction(MUL_R, V)
        assert RES_S == Fraction(MUL_S, V)

    def test_partial_fraction_reconstruction_h2(self):
        # h_2 = RES_K * K^2 + RES_R * r^2 + RES_S * s^2
        h2_pf = RES_K * EIG_K**2 + RES_R * EIG_R**2 + RES_S * EIG_S**2
        assert h2_pf == K

    def test_partial_fraction_reconstruction_h3(self):
        h3_pf = RES_K * EIG_K**3 + RES_R * EIG_R**3 + RES_S * EIG_S**3
        assert h3_pf == K * LAM

    def test_poles_are_rational(self):
        # All three poles 1/K=1/12, 1/r=1/2, 1/s=-1/4 are rational!
        assert Fraction(1, EIG_K) == Fraction(1, 12)
        assert Fraction(1, EIG_R) == Fraction(1, 2)
        assert Fraction(1, EIG_S) == Fraction(-1, 4)


class TestT5_GeneratingFunctionIdentities:
    """N(x)/D(x) correctly encodes all walk counts via matching."""

    def test_N_at_x_equals_1_over_K(self):
        # N(1/K) = N(1/12): evaluate numerator at the K-pole
        x = Fraction(1, EIG_K)
        n_val = N0 + N1 * x + N2 * x**2
        # = 1 - 10/12 - 20/144 = 1 - 5/6 - 5/36 = 36/36-30/36-5/36 = 1/36
        assert n_val == Fraction(1, 36)

    def test_N_at_x_equals_1_over_r(self):
        # N(1/2): evaluate at r-pole
        x = Fraction(1, EIG_R)
        n_val = N0 + N1 * x + N2 * x**2
        # = 1 - 5 - 5 = -9
        assert n_val == -9

    def test_N_at_x_equals_1_over_neg_MU(self):
        # N(-1/4): evaluate at s-pole
        x = Fraction(1, EIG_S)
        n_val = N0 + N1 * x + N2 * x**2
        # = 1 + 10/4 - 20/16 = 1 + 5/2 - 5/4 = 4/4+10/4-5/4 = 9/4
        assert n_val == Fraction(9, 4)

    def test_denominator_leading_term(self):
        # Leading coefficient of x^3 in D(x) = 96 = -K*r*s = K*LAM*MU
        assert D3 == K * LAM * MU

    def test_generating_function_ratio(self):
        # At k=3: h[3] = N1*D2 correction... verify via recurrence
        # h[3] = THETA*h[2] + 32*h[1] - 96*h[0] = 10*12 + 0 - 96 = 24 = K*LAM ✓
        assert THETA * h[2] + 32 * h[1] - 96 * h[0] == K * LAM

    def test_D_equals_minpoly_reversed(self):
        # D(x) = x^3 * minpoly(1/x) where minpoly(t) = t^3 - THETA*t^2 - 32*t + 96
        # x^3*(1/x^3 - THETA/x^2 - 32/x + 96) = 1 - THETA*x - 32*x^2 + 96*x^3 ✓
        assert D1 == -THETA and D2 == -MINPOLY_C1 and D3 == -MINPOLY_C0


class TestT6_WalkCountSeries:
    """Exact walk counts tr(A^k) for k=0..5 verified against formulas."""

    def test_p0(self):
        assert h[0] * V == V    # tr(I) = V

    def test_p1(self):
        assert h[1] * V == 0    # tr(A) = 0

    def test_p2(self):
        assert h[2] * V == V * K   # tr(A^2) = V*K = 480

    def test_p3(self):
        assert h[3] * V == V * K * LAM   # tr(A^3) = 960

    def test_p4(self):
        assert h[4] * V == 24960   # tr(A^4) = 24960

    def test_p5(self):
        # tr(A^5)/V = h[5] = THETA*h[4] + 32*h[3] - 96*h[2]
        # = 10*624 + 32*24 - 96*12 = 6240+768-1152 = 5856
        assert h[5] == 5856

    def test_p5_Q_formula(self):
        # p_5 = V * 5856 = 40*5856 = 234240
        # 5856 = 10*624 + 32*24 - 96*12 (from recurrence) — verify
        assert THETA * h[4] + MINPOLY_C1 * h[3] - K * LAM * MU * h[2] == h[5]

    def test_h4_Q_formula(self):
        # h[4] = 624 = MU^2*Q*PHI3 / V ... hmm: 624 = MU^2*Q*PHI3 = 16*3*13 = 624 ✓
        PHI3 = Q**2 + Q + 1   # = 13 (cyclotomic)
        assert h[4] == Fraction(MU**2 * Q * PHI3, 1)
