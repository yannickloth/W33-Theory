"""
Phase LII --- Walk Recursion & Transition Anatomy (T741--T755)
==============================================================
Fifteen theorems uncovering the walk algebra of W(3,3). The SRG walk entry
recursion has coefficients {K, LAM, Q^2, MU, DIM_O} --- all named constants.
The return-adjacent shift identity P^{n+1}_diag = P^n_adj reveals that p_3 =
1/72 = 1/|Delta(E_6)|. The power decomposition in the {I, A, J} basis gives
named coefficients: A^2 = DIM_O*I - LAM*A + MU*J, A^3 = -2^MU*I + K*A + V*J.
The I-coefficient follows a DIM_O * {1, LAM, K, V} scaling pattern. Diagonal
walk ratio d_4/d_3 = 26 = BOSONIC. Resolvent at N gives V*N/(Q*PHI6) = 200/21.
"""

from fractions import Fraction as Fr
import numpy as np
import pytest

# -- W(3,3) graph builder --
def _build_w33():
    F3 = range(3)
    raw = [(a,b,c,d) for a in F3 for b in F3 for c in F3 for d in F3
           if (a,b,c,d) != (0,0,0,0)]
    inv = {1: 1, 2: 2}
    seen, reps = {}, []
    for vec in raw:
        for i in range(4):
            if vec[i] != 0:
                s = inv[vec[i]]
                nv = tuple((s*x) % 3 for x in vec)
                break
        if nv not in seen:
            seen[nv] = len(reps)
            reps.append(nv)
    n = len(reps)
    def symp(u, w):
        return (u[0]*w[2] - u[2]*w[0] + u[1]*w[3] - u[3]*w[1]) % 3
    A = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(i+1, n):
            if symp(reps[i], reps[j]) == 0:
                A[i][j] = A[j][i] = 1
    return A

@pytest.fixture(scope="module")
def w33():
    return {"A": _build_w33()}

# -- Source constants --
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V * K // 2          # 240
R, S = 2, -4
F, G = 24, 15
N = Q + 2               # 5
ALPHA = V // MU          # 10
DIM_O = K - MU           # 8
ALBERT = V - (Q**2 + MU) # 27
PHI3 = Q**2 + Q + 1      # 13
PHI6 = Q**2 - Q + 1      # 7
K_BAR = V - 1 - K        # 27
r_s = R - S              # 6
BOSONIC = 26
DELTA_E6 = 72            # |Delta(E6)| = number of E6 roots


# -- Walk entry computations --
def walk_diag(n):
    """(A^n)_{ii} for any vertex i (walk-regular)."""
    return Fr(K**n + F * R**n + G * S**n, V)


def walk_adj(n):
    """(A^n)_{ij} for adjacent i ~ j."""
    return Fr(K**n, V) + Fr(R**n, ALPHA) - Fr(S**n, DIM_O)


def walk_non(n):
    """(A^n)_{ij} for non-adjacent i, j."""
    return Fr(K**n, V) - Fr(R**n, G) + Fr(S**n, F)


# ==============================================================
# T741 -- SRG Walk Entry Recursion
# ==============================================================
class TestT741WalkEntryRecursion:
    """T741: The walk entries (d_n, a_n, b_n) = (diagonal, adjacent, non-adj)
    satisfy:
        d_{n+1} = K * a_n
        a_{n+1} = d_n + LAM * a_n + Q^2 * b_n
        b_{n+1} = MU * a_n + DIM_O * b_n
    with d_0=1, a_0=0, b_0=0. Coefficients: {K, LAM, Q^2, MU, DIM_O}.
    """

    def _seq(self, nmax):
        d, a, b = [Fr(1)], [Fr(0)], [Fr(0)]
        for _ in range(nmax):
            d.append(K * a[-1])
            a.append(d[-2] + LAM * a[-1] + Q**2 * b[-1])
            b.append(MU * a[-2] + DIM_O * b[-1])
        return d, a, b

    def test_recursion_diagonal(self):
        """d_{n+1} = K * a_n for n = 0..5."""
        for n in range(6):
            assert walk_diag(n + 1) == K * walk_adj(n)

    def test_recursion_adjacent(self):
        """a_{n+1} = d_n + LAM * a_n + Q^2 * b_n for n = 0..5."""
        for n in range(6):
            lhs = walk_adj(n + 1)
            rhs = walk_diag(n) + LAM * walk_adj(n) + Q**2 * walk_non(n)
            assert lhs == rhs

    def test_recursion_nonadj(self):
        """b_{n+1} = MU * a_n + DIM_O * b_n for n = 0..5."""
        for n in range(6):
            lhs = walk_non(n + 1)
            rhs = MU * walk_adj(n) + DIM_O * walk_non(n)
            assert lhs == rhs

    def test_coefficients_named(self):
        """Recursion coefficients {K, LAM, Q^2, MU, DIM_O} = {12, 2, 9, 4, 8}."""
        assert K == 12
        assert LAM == 2
        assert Q**2 == 9
        assert MU == 4
        assert DIM_O == 8

    def test_q_squared_is_k_minus_lam_minus_1(self):
        """Q^2 = K - 1 - LAM = 9 (non-common-non-adjacent neighbors)."""
        assert Q**2 == K - 1 - LAM

    def test_recursion_vs_spectral(self):
        """Recursive and spectral walk entries agree for n = 0..6."""
        d, a, b = self._seq(6)
        for n in range(7):
            assert d[n] == walk_diag(n)
            assert a[n] == walk_adj(n)
            assert b[n] == walk_non(n)


# ==============================================================
# T742 -- Return-Adjacent Probability Shift
# ==============================================================
class TestT742ReturnAdjacentShift:
    """T742: The (n+1)-step return probability equals the n-step
    adjacent transition probability:
        P^{n+1}_diag = P^n_adj    for all n >= 0.
    Consequence of d_{n+1} = K * a_n, so d_{n+1}/K^{n+1} = a_n/K^n.
    """

    def test_shift_identity(self):
        """P^{n+1}_diag = P^n_adj for n = 0..5."""
        for n in range(6):
            p_return = Fr(walk_diag(n + 1), K**(n + 1))
            p_adj = Fr(walk_adj(n), K**n)
            assert p_return == p_adj

    def test_p3_equals_P2_adj(self):
        """p_3 = P^2_adj = LAM/K^2 = 1/72."""
        p3 = Fr(walk_diag(3), K**3)
        P2_adj = Fr(walk_adj(2), K**2)
        assert p3 == P2_adj == Fr(1, 72)

    def test_p4_equals_P3_adj(self):
        """p_4 = P^3_adj = dim(F4)/K^3 = 13/432 (matches T189)."""
        p4 = Fr(walk_diag(4), K**4)
        P3_adj = Fr(walk_adj(3), K**3)
        assert p4 == P3_adj == Fr(PHI3, 432)

    def test_shift_mechanism(self):
        """The identity follows from vertex transitivity: every
        closed (n+1)-walk decomposes as step-to-neighbor + n-walk-back."""
        # d_{n+1} = sum_{j~i} (A^n)_{ji} = K * a_n (since all adj entries equal)
        for n in range(4):
            assert walk_diag(n + 1) == K * walk_adj(n)


# ==============================================================
# T743 -- p_3 = 1/|Delta(E6)| = 1/72
# ==============================================================
class TestT743ReturnProbP3:
    """T743: The 3-step return probability:
        p_3 = 1/72 = 1/|Delta(E6)|
    where 72 = 2 * r_s^2 = 2 * 36 is the number of roots of E6.
    """

    def test_p3_value(self):
        """p_3 = (K^3 + F*R^3 + G*S^3)/(V*K^3) = 1/72."""
        p3 = Fr(K**3 + F * R**3 + G * S**3, V * K**3)
        assert p3 == Fr(1, 72)

    def test_72_is_delta_E6(self):
        """72 = |Delta(E6)| = 2 * r_s^2."""
        assert DELTA_E6 == 72
        assert 2 * r_s**2 == 72

    def test_p3_from_LAM_K(self):
        """p_3 = LAM/K^2 = 2/144 = 1/72 (via shift identity)."""
        assert Fr(LAM, K**2) == Fr(1, 72)

    def test_p3_over_p2(self):
        """p_3/p_2 = 1/r_s = 1/6."""
        p2 = Fr(1, K)
        p3 = Fr(1, 72)
        assert p3 / p2 == Fr(1, r_s)

    def test_p3_numerical(self, w33):
        """Numerical verification from transition matrix."""
        P = w33["A"].astype(float) / K
        P3 = np.linalg.matrix_power(P, 3)
        assert abs(P3[0, 0] - 1 / 72) < 1e-12


# ==============================================================
# T744 -- Transition Probability P^2 Anatomy
# ==============================================================
class TestT744TransitionP2:
    """T744: The 2-step transition probabilities:
        P^2_adj = LAM/K^2 = 1/72 = 1/|Delta(E6)|
        P^2_non = MU/K^2 = 1/36 = 1/r_s^2
        P^2_non / P^2_adj = MU/LAM = 2 = LAM.
    """

    def test_P2_adj(self):
        """P^2_adj = LAM/K^2 = 1/72 = 1/|Delta(E6)|."""
        assert Fr(LAM, K**2) == Fr(1, DELTA_E6)

    def test_P2_non(self):
        """P^2_non = MU/K^2 = 1/36 = 1/r_s^2."""
        assert Fr(MU, K**2) == Fr(1, r_s**2)

    def test_P2_ratio(self):
        """P^2_non / P^2_adj = MU/LAM = 2."""
        ratio = Fr(MU, LAM)
        assert ratio == 2
        assert ratio == LAM

    def test_P2_sum(self):
        """P^2_diag + K*P^2_adj + K_BAR*P^2_non = 1 (probability sum)."""
        total = Fr(1, K) + K * Fr(LAM, K**2) + K_BAR * Fr(MU, K**2)
        assert total == 1

    def test_P2_non_numerical(self, w33):
        """Numerical verification: P^2 non-adjacent entry = 1/36."""
        P = w33["A"].astype(float) / K
        P2 = P @ P
        non_nbrs = np.where(w33["A"][0] == 0)[0]
        j = non_nbrs[non_nbrs > 0][0]
        assert abs(P2[0, j] - 1 / 36) < 1e-12


# ==============================================================
# T745 -- Power Decomposition in {I, A, J}
# ==============================================================
class TestT745PowerDecomposition:
    """T745: Matrix powers in the Bose-Mesner basis {I, A, J}:
        A^2 =  DIM_O * I  -  LAM * A  +  MU * J
        A^3 = -2^MU  * I  +  K   * A  +  V  * J
        A^4 = K*DIM_O * I  -  V   * A  +  T_{2^N} * J
    where T_{2^N} = T_32 = 528 is the 32nd triangular number.
    """

    def test_A2_decomposition(self):
        """A^2 = DIM_O*I - LAM*A + MU*J (standard SRG relation)."""
        # In IAJ form: (A^2)_{ii} = c_I + c_J, (A^2)_{adj} = c_A + c_J, (A^2)_{non} = c_J
        assert walk_diag(2) == K            # d_2 = I-coeff + J-coeff = DIM_O + MU = 12
        # In IAJ form: (A^2)_{ii} = c_I + c_J, (A^2)_{adj} = c_A + c_J, (A^2)_{non} = c_J
        c_I, c_A, c_J = DIM_O, -LAM, MU
        assert c_I + c_J == K               # diagonal
        assert c_A + c_J == LAM             # adjacent
        assert c_J == MU                    # non-adjacent

    def test_A3_decomposition(self):
        """A^3 = -2^MU * I + K * A + V * J."""
        c_I, c_A, c_J = -(2**MU), K, V
        assert c_I + c_J == F               # diagonal: -16 + 40 = 24
        assert c_A + c_J == MU * PHI3       # adjacent: 12 + 40 = 52
        assert c_J == V                     # non-adjacent: 40

    def test_A4_decomposition(self):
        """A^4 = K*DIM_O * I - V * A + T_{2^N} * J."""
        T_32 = 2**N * (2**N + 1) // 2      # 528
        c_I, c_A, c_J = K * DIM_O, -V, T_32
        assert c_I + c_J == 2**MU * (V - 1) # diagonal: 96 + 528 = 624
        assert c_A + c_J == T_32 - V        # adjacent: -40 + 528 = 488
        assert c_J == T_32                   # non-adjacent: 528

    def test_A2_coefficients_named(self):
        """A^2 coefficients: {DIM_O, -LAM, MU} = {8, -2, 4}."""
        assert DIM_O == 8
        assert -LAM == -2
        assert MU == 4

    def test_A3_coefficients_named(self):
        """A^3 coefficients: {-2^MU, K, V} = {-16, 12, 40}."""
        assert -(2**MU) == -16
        assert K == 12
        assert V == 40

    def test_A2_numerical(self, w33):
        """Numerical: A^2 = 8I - 2A + 4J."""
        A = w33["A"]
        A2 = A @ A
        J = np.ones((V, V), dtype=int)
        I = np.eye(V, dtype=int)
        expected = DIM_O * I - LAM * A + MU * J
        assert np.array_equal(A2, expected)


# ==============================================================
# T746 -- I-Coefficient DIM_O Scaling Pattern
# ==============================================================
class TestT746ICoefficientPattern:
    """T746: The I-coefficient in the {I, A, J} decomposition of A^n
    follows:
        c_I(n) = (-1)^n * DIM_O * X_n
    where X_2=1, X_3=LAM, X_4=K, X_5=V. The multiplier sequence
    {1, LAM, K, V} is the fundamental SRG parameter ladder.
    """

    @staticmethod
    def _i_coeff(n):
        """Extract I-coefficient: c_I = (A^n)_diag - (A^n)_non."""
        return walk_diag(n) - walk_non(n)

    def test_n2(self):
        """c_I(2) = DIM_O * 1 = 8."""
        assert self._i_coeff(2) == DIM_O

    def test_n3(self):
        """c_I(3) = -DIM_O * LAM = -16."""
        assert self._i_coeff(3) == -DIM_O * LAM

    def test_n4(self):
        """c_I(4) = DIM_O * K = 96."""
        assert self._i_coeff(4) == DIM_O * K

    def test_n5(self):
        """c_I(5) = -DIM_O * V = -320."""
        assert self._i_coeff(5) == -DIM_O * V

    def test_pattern_is_srg_ladder(self):
        """Multiplier sequence {1, LAM, K, V} = {1, 2, 12, 40}."""
        expected = [1, LAM, K, V]
        for i, n in enumerate(range(2, 6)):
            sign = (-1)**n
            assert self._i_coeff(n) == sign * DIM_O * expected[i]


# ==============================================================
# T747 -- Walk-4 Triangular Number
# ==============================================================
class TestT747Walk4Triangular:
    """T747: The 4-step walk entries:
        d_4 = 2^MU * (V-1) = 624
        a_4 = T_{2^N} - V = 488
        b_4 = T_{2^N} = 528    (32nd triangular number)
        Total: d_4 + K*a_4 + K_BAR*b_4 = K^4 = 20736.
    """

    def test_b4_is_triangular(self):
        """b_4 = T_{2^N} = T_32 = 32*33/2 = 528."""
        T_32 = 2**N * (2**N + 1) // 2
        assert walk_non(4) == T_32 == 528

    def test_d4_value(self):
        """d_4 = 2^MU * (V-1) = 624."""
        assert walk_diag(4) == 2**MU * (V - 1)

    def test_a4_complement(self):
        """a_4 = T_{2^N} - V = 528 - 40 = 488."""
        T_32 = 2**N * (2**N + 1) // 2
        assert walk_adj(4) == T_32 - V

    def test_total_K4(self):
        """d_4 + K*a_4 + K_BAR*b_4 = K^4 = 20736."""
        total = walk_diag(4) + K * walk_adj(4) + K_BAR * walk_non(4)
        assert total == K**4

    def test_b4_numerical(self, w33):
        """Numerical: (A^4)_{non-adj} = 528."""
        A4 = np.linalg.matrix_power(w33["A"], 4)
        non_nbrs = np.where(w33["A"][0] == 0)[0]
        j = non_nbrs[non_nbrs > 0][0]
        assert A4[0, j] == 528


# ==============================================================
# T748 -- Walk-2 Ratios
# ==============================================================
class TestT748Walk2Ratios:
    """T748: Walk-2 entry ratios are named SRG constants:
        d_2/a_2 = K/LAM = r_s = 6
        d_2/b_2 = K/MU  = Q   = 3
        a_2/b_2 = LAM/MU = 1/2
    The adjacency parameter ratio LAM/MU = 1/2 governs the 2-step
    transition preference.
    """

    def test_diag_over_adj(self):
        """d_2/a_2 = K/LAM = r_s = 6."""
        ratio = Fr(walk_diag(2), walk_adj(2))
        assert ratio == r_s == Fr(K, LAM)

    def test_diag_over_non(self):
        """d_2/b_2 = K/MU = Q = 3."""
        ratio = Fr(walk_diag(2), walk_non(2))
        assert ratio == Q == Fr(K, MU)

    def test_adj_over_non(self):
        """a_2/b_2 = LAM/MU = 1/2."""
        ratio = Fr(walk_adj(2), walk_non(2))
        assert ratio == Fr(LAM, MU) == Fr(1, 2)

    def test_k_over_lam_equals_r_minus_s(self):
        """K/LAM = r_s = R - S = 6 (spectral gap ratio)."""
        assert Fr(K, LAM) == r_s

    def test_lam_mu_ratio_meaning(self):
        """LAM/MU = 1/2 means neighbors have half the 2-walk density of non-neighbors."""
        assert Fr(LAM, MU) == Fr(1, 2)


# ==============================================================
# T749 -- Walk-3 Ratios
# ==============================================================
class TestT749Walk3Ratios:
    """T749: Walk-3 entry ratios reveal named fractions:
        d_3/b_3 = F/V  = Q/N   = 3/5
        a_3/b_3 = dim(F4)/V = PHI3/ALPHA = 13/10
        a_3/d_3 = dim(F4)/F = PHI3/r_s   = 13/6
    """

    def test_diag_over_non(self):
        """d_3/b_3 = F/V = Q/N = 3/5."""
        ratio = Fr(walk_diag(3), walk_non(3))
        assert ratio == Fr(F, V) == Fr(Q, N) == Fr(3, 5)

    def test_adj_over_non(self):
        """a_3/b_3 = dim(F4)/V = PHI3/ALPHA = 13/10."""
        ratio = Fr(walk_adj(3), walk_non(3))
        assert ratio == Fr(PHI3, ALPHA) == Fr(13, 10)

    def test_adj_over_diag(self):
        """a_3/d_3 = dim(F4)/F = PHI3/r_s = 13/6."""
        ratio = Fr(walk_adj(3), walk_diag(3))
        assert ratio == Fr(PHI3, r_s) == Fr(13, 6)

    def test_diag_over_non_two_namings(self):
        """Q/N = F/V: the field order / independence ratio equals
        the multiplicity / vertex ratio."""
        assert Fr(Q, N) == Fr(F, V)


# ==============================================================
# T750 -- Walk-3 Cube Decomposition
# ==============================================================
class TestT750Walk3Cube:
    """T750: The total 3-walks from any vertex decompose:
        K^3 = F + K * dim(F4) + K_BAR * V
        1728 = 24 + 624 + 1080
    with K * dim(F4) = d_4 = 624 and K_BAR * V = ALBERT * V = 1080.
    """

    def test_cube_decomposition(self):
        """K^3 = F + K*52 + K_BAR*V = 1728."""
        assert F + K * 52 + K_BAR * V == K**3

    def test_k_times_f4(self):
        """K * dim(F4) = K * MU * PHI3 = 624 = d_4 = (A^4)_diag."""
        assert K * MU * PHI3 == 624
        assert K * MU * PHI3 == walk_diag(4)

    def test_kbar_times_v(self):
        """K_BAR * V = ALBERT * V = 1080 = 2 * E_bar."""
        E_bar = V * K_BAR // 2  # complement edges = 540
        assert K_BAR * V == ALBERT * V == 1080
        assert K_BAR * V == 2 * E_bar

    def test_total_n_general(self):
        """d_n + K*a_n + K_BAR*b_n = K^n for all n."""
        for n in range(7):
            total = walk_diag(n) + K * walk_adj(n) + K_BAR * walk_non(n)
            assert total == K**n


# ==============================================================
# T751 -- Resolvent at N = V*N/(Q*PHI6)
# ==============================================================
class TestT751ResolventAtN:
    """T751: The resolvent trace at z = N = 5:
        tr G(N) = 1/(N-K) + F/(N-R) + G/(N-S) = V*N/(Q*PHI6) = 200/21.
    """

    def test_resolvent_value(self):
        """tr G(N) = V*N/(Q*PHI6) = 200/21."""
        g = Fr(1, N - K) + Fr(F, N - R) + Fr(G, N - S)
        assert g == Fr(V * N, Q * PHI6)
        assert g == Fr(200, 21)

    def test_denominator_is_q_phi6(self):
        """Q*PHI6 = 3*7 = 21."""
        assert Q * PHI6 == 21

    def test_numerator_is_v_times_n(self):
        """V*N = 40*5 = 200."""
        assert V * N == 200

    def test_numerical(self, w33):
        """Numerical verification from matrix inverse."""
        zI_A = N * np.eye(V) - w33["A"].astype(float)
        g = np.trace(np.linalg.inv(zI_A))
        assert abs(g - 200 / 21) < 1e-8


# ==============================================================
# T752 -- Resolvent at r_s and OMEGA
# ==============================================================
class TestT752ResolventRsOmega:
    """T752: The resolvent trace at z = r_s = 6 and z = K-S = 16:
        tr G(r_s) = 2(K-1)/Q = 22/3
        tr G(K-S) = (K+PHI6)/PHI6 = 19/7
    """

    def test_resolvent_at_rs(self):
        """tr G(r_s) = 2(K-1)/Q = 22/3."""
        g = Fr(1, r_s - K) + Fr(F, r_s - R) + Fr(G, r_s - S)
        assert g == Fr(2 * (K - 1), Q)
        assert g == Fr(22, 3)

    def test_resolvent_at_omega(self):
        """tr G(K-S) = (K+PHI6)/PHI6 = 19/7."""
        z = K - S  # 16
        g = Fr(1, z - K) + Fr(F, z - R) + Fr(G, z - S)
        assert g == Fr(K + PHI6, PHI6)
        assert g == Fr(19, 7)

    def test_resolvent_at_mu(self):
        """tr G(MU) = 55/4."""
        g = Fr(1, MU - K) + Fr(F, MU - R) + Fr(G, MU - S)
        assert g == Fr(55, 4)

    def test_mu_resolvent_triangular(self):
        """55 = T_ALPHA = ALPHA*(ALPHA+1)/2 (10th triangular number)."""
        T_alpha = ALPHA * (ALPHA + 1) // 2
        assert T_alpha == 55

    def test_numerical_rs(self, w33):
        """Numerical: tr G(r_s) = 22/3."""
        zI_A = r_s * np.eye(V) - w33["A"].astype(float)
        g = np.trace(np.linalg.inv(zI_A))
        assert abs(g - 22 / 3) < 1e-8


# ==============================================================
# T753 -- Walk Generating Function at 1/ALPHA
# ==============================================================
class TestT753WalkGF:
    """T753: The diagonal walk generating function at u = 1/ALPHA:
        W(1/ALPHA) = (1/V) sum m_i/(1 - theta_i/ALPHA) = N^2/(MU*PHI6) = 25/28.
    """

    def test_wgf_value(self):
        """W(1/ALPHA) = N^2/(MU*PHI6) = 25/28."""
        u = Fr(1, ALPHA)
        w = Fr(1, V) * (Fr(1, 1 - K * u) + Fr(F, 1 - R * u) + Fr(G, 1 - S * u))
        assert w == Fr(N**2, MU * PHI6)
        assert w == Fr(25, 28)

    def test_denominator_mu_phi6(self):
        """MU * PHI6 = 4 * 7 = 28."""
        assert MU * PHI6 == 28

    def test_numerator_n_squared(self):
        """N^2 = 25."""
        assert N**2 == 25

    def test_wgf_closed_form(self):
        """Closed-form W(1/ALPHA) = (1/V)(1/(1-K/A) + F/(1-R/A) + G/(1-S/A)) = 25/28."""
        u = Fr(1, ALPHA)
        exact = Fr(1, V) * (Fr(1, 1-K*u) + Fr(F, 1-R*u) + Fr(G, 1-S*u))
        assert exact == Fr(25, 28)


# ==============================================================
# T754 -- Diagonal Walk Ratios & BOSONIC
# ==============================================================
class TestT754DiagonalWalkRatios:
    """T754: Consecutive diagonal walk ratios:
        d_3/d_2 = F/K = 2 = LAM
        d_4/d_3 = 2^MU*(V-1)/F = 26 = BOSONIC
    The closed-walk growth rate from n=3 to n=4 is the bosonic string
    dimension 26.
    """

    def test_d3_over_d2(self):
        """d_3/d_2 = F/K = 2 = LAM."""
        ratio = Fr(walk_diag(3), walk_diag(2))
        assert ratio == LAM == Fr(F, K)

    def test_d4_over_d3_bosonic(self):
        """d_4/d_3 = 26 = BOSONIC (bosonic string dimension!)."""
        ratio = Fr(walk_diag(4), walk_diag(3))
        assert ratio == BOSONIC == 26

    def test_d4_d3_decomposition(self):
        """d_4/d_3 = 2^MU*(V-1)/F = 2*PHI3 = 26."""
        assert Fr(2**MU * (V - 1), F) == 2 * PHI3 == BOSONIC

    def test_d2_naming(self):
        """d_2 = K = 12 (degree, closed 2-walks per vertex)."""
        assert walk_diag(2) == K

    def test_d3_naming(self):
        """d_3 = F = 24 (closed 3-walks per vertex = 2 * triangles per vertex)."""
        assert walk_diag(3) == F
        assert walk_diag(3) == 2 * (K * LAM // 2)


# ==============================================================
# T755 -- A-Coefficient SRG Parameter Sequence
# ==============================================================
class TestT755ACoefficientSequence:
    """T755: The A-coefficient in the {I, A, J} decomposition of A^n:
        n: 0  1  2    3   4
        c: 0  1  -LAM  K  -V
    Absolute values: {0, 1, LAM, K, V} — the SRG fundamental ladder.
    Signs alternate after n=1.
    """

    @staticmethod
    def _a_coeff(n):
        """Extract A-coefficient: c_A = (A^n)_adj - (A^n)_non."""
        return walk_adj(n) - walk_non(n)

    def test_n0(self):
        """c_A(0) = 0."""
        assert self._a_coeff(0) == 0

    def test_n1(self):
        """c_A(1) = 1."""
        assert self._a_coeff(1) == 1

    def test_n2(self):
        """c_A(2) = -LAM = -2."""
        assert self._a_coeff(2) == -LAM

    def test_n3(self):
        """c_A(3) = K = 12."""
        assert self._a_coeff(3) == K

    def test_n4(self):
        """c_A(4) = -V = -40."""
        assert self._a_coeff(4) == -V

    def test_alternating_signs(self):
        """Signs alternate: -, +, - for n = 2, 3, 4 (pattern (-1)^(n+1))."""
        expected_signs = [-1, +1, -1]  # n=2: -, n=3: +, n=4: -
        coeffs = [self._a_coeff(n) for n in range(2, 5)]
        for sign, c in zip(expected_signs, coeffs):
            assert (c > 0) == (sign > 0)

    def test_absolute_values_are_srg_params(self):
        """|c_A| for n=2,3,4 are {LAM, K, V} — the SRG parameter ladder."""
        assert abs(self._a_coeff(2)) == LAM
        assert abs(self._a_coeff(3)) == K
        assert abs(self._a_coeff(4)) == V
