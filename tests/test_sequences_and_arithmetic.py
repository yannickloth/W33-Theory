"""
Phase XX: Integer Sequences & Deep Arithmetic (T261-T275)
=========================================================

From (v, k, lam, mu, q) = (40, 12, 2, 4, 3) we derive 15 theorems
connecting W(3,3) to classical integer sequences (Tribonacci, Narayana,
Motzkin, Padovan, Perrin), characteristic polynomial evaluations,
number-theoretic functions, Bernoulli numbers, and spectral radii products.

These theorems reveal that the SRG parameters are not isolated numerical
coincidences but sit at intersections of deep combinatorial sequences.

Theorems
--------
T261: Tribonacci window Trib[6..10] = (Phi6, Phi3, f, v+mu, q^4)
T262: Narayana numbers N(N,lam)=theta, N(N,q)=v/2
T263: Motzkin numbers M(mu)=q^2, M(N)=3*Phi6
T264: Padovan P_10=k, P_13=28; Perrin_8=theta, Perrin_9=k
T265: det(I-A) = -(k-1)*N^g (characteristic polynomial at x=1)
T266: Cover time bounds from Kemeny constant
T267: Arc stabilizer |Aut|/(2E) = mu*ALBERT = 108
T268: Distance-2 eigenvalue product = -q^5
T269: Spectral radii product = 2^9 * 3^5
T270: Divisor count d(E) = d(240) = v/2 = 20
T271: Edge density = mu/Phi3, non-edges = ALBERT*v/2
T272: Trace ratios S3/S2 = lam, S4/S2 = dim(F4) = 52
T273: Bernoulli denominator tower: B_2->k/lam, B_4->v-theta, B_6->v+lam
T274: Partition values p(theta)=42, p(mu)=N=5, p(dimO)=lam*(k-1)
T275: Abundance of v: sigma(v)-2v = theta = 10
"""
from __future__ import annotations

import math
from fractions import Fraction

# ═══════════════════════════════════════════════════════════════
#  SRG CONSTANTS
# ═══════════════════════════════════════════════════════════════
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V * K // 2                         # 240
r, s = 2, -4                           # non-trivial eigenvalues
f, g = 24, 15                          # multiplicities
THETA = 10                             # Lovász theta
PHI3 = Q**2 + Q + 1                    # 13
PHI6 = Q**2 - Q + 1                    # 7
DIM_O = K - MU                         # 8
N = 5                                  # clique covering number
ALBERT = V - 1 - K                     # 27
AUT = 51840                            # |Sp(4,3)|


# ═══════════════════════════════════════════════════════════════
#  T261: Tribonacci Window
# ═══════════════════════════════════════════════════════════════

def _tribonacci(n: int) -> list[int]:
    """Compute tribonacci numbers T(0)..T(n)."""
    t = [0, 0, 1]
    for _ in range(n - 2):
        t.append(t[-1] + t[-2] + t[-3])
    return t


class TestTribonacciWindow:
    """T261: The tribonacci sequence hits five consecutive SRG-derived values.

    Trib(6)=7=Phi6, Trib(7)=13=Phi3, Trib(8)=24=f,
    Trib(9)=44=v+mu, Trib(10)=81=q^4.
    """

    TRIB = _tribonacci(12)

    def test_trib_6_is_phi6(self):
        assert self.TRIB[6] == PHI6

    def test_trib_7_is_phi3(self):
        assert self.TRIB[7] == PHI3

    def test_trib_8_is_f(self):
        assert self.TRIB[8] == f

    def test_trib_9_is_v_plus_mu(self):
        assert self.TRIB[9] == V + MU

    def test_trib_10_is_q4(self):
        assert self.TRIB[10] == Q**4

    def test_consecutive_window(self):
        """Five consecutive tribonacci numbers map to SRG values."""
        window = self.TRIB[6:11]
        expected = [PHI6, PHI3, f, V + MU, Q**4]
        assert window == expected

    def test_trib_recurrence_at_phi3(self):
        """Trib(7) = Trib(6)+Trib(5)+Trib(4) = 7+4+2 = 13 = Phi3."""
        assert self.TRIB[7] == self.TRIB[6] + self.TRIB[5] + self.TRIB[4]


# ═══════════════════════════════════════════════════════════════
#  T262: Narayana Numbers
# ═══════════════════════════════════════════════════════════════

def _narayana(n: int, k_val: int) -> Fraction:
    """Narayana number N(n,k) = (1/n) * C(n,k) * C(n,k-1)."""
    return Fraction(math.comb(n, k_val) * math.comb(n, k_val - 1), n)


class TestNarayanaNumbers:
    """T262: Narayana numbers at SRG parameters yield fundamental invariants.

    N(N, lam) = theta = 10, N(N, q) = v/2 = 20.
    """

    def test_narayana_N_lam_is_theta(self):
        assert _narayana(N, LAM) == THETA

    def test_narayana_N_q_is_half_v(self):
        assert _narayana(N, Q) == V // 2

    def test_narayana_sum_is_catalan(self):
        """Sum of N(n,k) for k=1..n equals Catalan(n)."""
        cat_N = math.comb(2 * N, N) // (N + 1)
        total = sum(_narayana(N, kk) for kk in range(1, N + 1))
        assert total == cat_N

    def test_narayana_symmetry(self):
        """N(n,k) = N(n, n+1-k)."""
        assert _narayana(N, LAM) == _narayana(N, N + 1 - LAM)

    def test_narayana_ratio(self):
        """N(N,q)/N(N,lam) = v/(2*theta) = 2."""
        assert Fraction(_narayana(N, Q), _narayana(N, LAM)) == Fraction(V, 2 * THETA)


# ═══════════════════════════════════════════════════════════════
#  T263: Motzkin Numbers
# ═══════════════════════════════════════════════════════════════

class TestMotzkinNumbers:
    """T263: Motzkin numbers at SRG parameters.

    M(mu) = 9 = q^2, M(N) = 21 = 3*Phi6.
    """

    MOTZKIN = [1, 1, 2, 4, 9, 21, 51, 127, 323, 835, 2188]

    def test_motzkin_mu_is_q_squared(self):
        assert self.MOTZKIN[MU] == Q**2

    def test_motzkin_N_is_3_phi6(self):
        assert self.MOTZKIN[N] == 3 * PHI6

    def test_motzkin_lam(self):
        """M(lambda) = M(2) = 2 = lambda."""
        assert self.MOTZKIN[LAM] == LAM

    def test_motzkin_q(self):
        """M(q) = M(3) = 4 = mu."""
        assert self.MOTZKIN[Q] == MU

    def test_motzkin_ratio(self):
        """M(N)/M(mu) = 21/9 = 7/3 = Phi6/q."""
        assert Fraction(self.MOTZKIN[N], self.MOTZKIN[MU]) == Fraction(PHI6, Q)


# ═══════════════════════════════════════════════════════════════
#  T264: Padovan and Perrin Sequences
# ═══════════════════════════════════════════════════════════════

def _padovan(n: int) -> list[int]:
    """Padovan sequence: P(n) = P(n-2) + P(n-3), P(0)=P(1)=P(2)=1."""
    p = [1, 1, 1]
    for _ in range(n - 2):
        p.append(p[-2] + p[-3])
    return p


def _perrin(n: int) -> list[int]:
    """Perrin sequence: a(n) = a(n-2) + a(n-3), a(0)=3, a(1)=0, a(2)=2."""
    p = [3, 0, 2]
    for _ in range(n - 2):
        p.append(p[-2] + p[-3])
    return p


class TestPadovanPerrin:
    """T264: Padovan and Perrin sequences hit SRG parameters.

    Padovan: P(6)=mu, P(10)=k, P(13)=28=perfect.
    Perrin: Pe(3)=q, Pe(8)=theta, Pe(9)=k.
    """

    PADOVAN = _padovan(22)
    PERRIN = _perrin(12)

    def test_padovan_6_is_mu(self):
        assert self.PADOVAN[6] == MU

    def test_padovan_10_is_k(self):
        assert self.PADOVAN[10] == K

    def test_padovan_11_is_k_plus_mu(self):
        assert self.PADOVAN[11] == K + MU

    def test_padovan_13_is_perfect_28(self):
        assert self.PADOVAN[13] == V - K
        assert self.PADOVAN[13] == 28  # second perfect number

    def test_padovan_20_is_Nv(self):
        """P(20) = 200 = N*v = E-v."""
        assert self.PADOVAN[20] == N * V
        assert self.PADOVAN[20] == E - V

    def test_perrin_3_is_q(self):
        assert self.PERRIN[3] == Q

    def test_perrin_8_is_theta(self):
        assert self.PERRIN[8] == THETA

    def test_perrin_9_is_k(self):
        assert self.PERRIN[9] == K


# ═══════════════════════════════════════════════════════════════
#  T265: Characteristic Polynomial at x=1
# ═══════════════════════════════════════════════════════════════

class TestCharPolyEval:
    """T265: det(I - A) = (1-k)(1-r)^f(1-s)^g = -(k-1)*N^g.

    Evaluating the characteristic polynomial of the adjacency matrix
    at x = 1 gives |det(I-A)| = (k-1) * N^g = 11 * 5^15.
    """

    def test_det_I_minus_A(self):
        det_val = (1 - K) * (1 - r)**f * (1 - s)**g
        assert det_val == -(K - 1) * N**g

    def test_sign_is_negative(self):
        det_val = (1 - K) * (1 - r)**f * (1 - s)**g
        assert det_val < 0

    def test_factors(self):
        """(1-k) = -(k-1) = -11, (1-r)^f = (-1)^24 = 1, (1-s)^g = 5^15."""
        assert 1 - K == -(K - 1)
        assert (1 - r)**f == 1  # (-1)^24 = 1
        assert (1 - s)**g == N**g  # 5^15

    def test_k_minus_1_is_prime(self):
        """k-1 = 11 is prime."""
        from sympy import isprime
        assert isprime(K - 1)

    def test_N_is_prime(self):
        """N = 5 is prime, making N^g a prime power."""
        from sympy import isprime
        assert isprime(N)


# ═══════════════════════════════════════════════════════════════
#  T266: Cover Time Bounds
# ═══════════════════════════════════════════════════════════════

class TestCoverTime:
    """T266: Cover time bounds from Kemeny constant.

    Kemeny K = 801/20. Matthews bound gives cover time <= K*ln(v).
    Relaxation time tau = q/lam = 3/2.
    """

    KEMENY = Fraction(801, 20)

    def test_kemeny_value(self):
        K_val = f * Fraction(K, K - r) + g * Fraction(K, K - s)
        assert K_val == self.KEMENY

    def test_matthews_upper(self):
        """Cover time <= Kemeny * H_v where H_v = v-th harmonic number."""
        H_v = sum(Fraction(1, i) for i in range(1, V + 1))
        ct_upper = self.KEMENY * H_v
        # Cover time upper bound is finite and well-defined
        assert ct_upper > V  # must visit all v vertices

    def test_kemeny_close_to_v(self):
        """Kemeny = 801/20 = 40.05, remarkably close to v = 40."""
        excess = self.KEMENY - V
        assert excess == Fraction(1, 20)

    def test_relaxation_time(self):
        """Relaxation tau = 1/(spectral gap) = q/lam = 3/2."""
        rho = max(abs(r), abs(s))
        gap = 1 - Fraction(rho, K)
        tau = Fraction(1, gap)
        assert tau == Fraction(Q, LAM)

    def test_spectral_gap_is_2_over_3(self):
        rho = max(abs(r), abs(s))
        gap = 1 - Fraction(rho, K)
        assert gap == Fraction(2, 3)


# ═══════════════════════════════════════════════════════════════
#  T267: Arc Stabilizer
# ═══════════════════════════════════════════════════════════════

class TestArcStabilizer:
    """T267: The arc stabilizer of Sp(4,3) acting on W(3,3).

    |Aut|/(2E) = 51840/480 = 108 = mu * ALBERT = 4 * 27.
    Vertex stabilizer = 6^4, edge stabilizer = 6^3.
    """

    def test_arc_stabilizer_is_mu_albert(self):
        arc_stab = AUT // (2 * E)
        assert arc_stab == MU * ALBERT

    def test_arc_stabilizer_value(self):
        assert AUT // (2 * E) == 108

    def test_vertex_stabilizer(self):
        assert AUT // V == 6**4

    def test_edge_stabilizer(self):
        assert AUT // E == 6**3

    def test_stab_ratio_is_k_over_lam(self):
        """vertex_stab / edge_stab = k/lam = 6."""
        v_stab = AUT // V
        e_stab = AUT // E
        assert v_stab // e_stab == K // LAM


# ═══════════════════════════════════════════════════════════════
#  T268: Distance-2 Eigenvalue Product
# ═══════════════════════════════════════════════════════════════

class TestD2EigenProduct:
    """T268: Product of distance-2 matrix eigenvalues = -q^5.

    D2 = J - I - A has eigenvalues (ALBERT, -q, q) = (27, -3, 3).
    Product = 27 * (-3) * 3 = -243 = -q^5.
    """

    def test_d2_eigenvalues(self):
        d2_eigs = (V - 1 - K, -1 - r, -1 - s)
        assert d2_eigs == (ALBERT, -Q, Q)

    def test_product_is_neg_q5(self):
        prod = ALBERT * (-Q) * Q
        assert prod == -(Q**5)

    def test_product_value(self):
        assert ALBERT * Q * Q == 243
        assert 243 == 3**5

    def test_d2_trace(self):
        """trace(D2) = ALBERT + f*(-q) + g*q = 27 - 72 + 45 = 0."""
        tr = ALBERT + f * (-Q) + g * Q
        assert tr == 0

    def test_d2_sum_of_squares(self):
        """Sum of squared D2 eigenvalues = v * (v-1-k)."""
        ss = ALBERT**2 + f * Q**2 + g * Q**2
        assert ss == V * (V - 1 - K)


# ═══════════════════════════════════════════════════════════════
#  T269: Spectral Radii Product
# ═══════════════════════════════════════════════════════════════

class TestSpectralRadiiProduct:
    """T269: Product of spectral radii of four graph matrices.

    rho(A)=k, rho(L)=k+mu, rho(Q)=2k=f, rho(D2)=ALBERT.
    Product = k * (k+mu) * f * ALBERT = 12*16*24*27 = 124416 = 2^9 * 3^5.
    """

    def test_rho_A(self):
        assert K == 12

    def test_rho_L(self):
        assert K + MU == 16

    def test_rho_Q_is_f(self):
        assert 2 * K == f

    def test_rho_D2_is_albert(self):
        assert V - 1 - K == ALBERT

    def test_product(self):
        prod = K * (K + MU) * f * ALBERT
        assert prod == 124416

    def test_product_factorization(self):
        """Product = 2^9 * 3^5 = 512 * 243."""
        assert 124416 == 2**9 * 3**5

    def test_product_is_2q_power(self):
        """124416 = (2*q)^5 * 2^4 = 6^5 * 16."""
        assert 124416 == 6**5 * 16
        assert 6**5 * (K + MU) == 124416


# ═══════════════════════════════════════════════════════════════
#  T270: Divisor Count of E
# ═══════════════════════════════════════════════════════════════

class TestDivisorCount:
    """T270: d(E) = d(240) = 20 = v/2.

    240 = 2^4 * 3 * 5, so d(240) = 5*2*2 = 20 = v/2.
    """

    def test_d_of_E_is_half_v(self):
        d_E = sum(1 for i in range(1, E + 1) if E % i == 0)
        assert d_E == V // 2

    def test_d_of_E_value(self):
        d_E = sum(1 for i in range(1, E + 1) if E % i == 0)
        assert d_E == 20

    def test_E_factorization(self):
        """E = 240 = 2^4 * 3 * 5."""
        assert E == 2**4 * 3 * 5

    def test_d_formula(self):
        """d(2^4 * 3 * 5) = (4+1)(1+1)(1+1) = 20."""
        assert (4 + 1) * (1 + 1) * (1 + 1) == V // 2

    def test_d_of_k(self):
        """d(k) = d(12) = 6 = k/lam."""
        d_k = sum(1 for i in range(1, K + 1) if K % i == 0)
        assert d_k == K // LAM


# ═══════════════════════════════════════════════════════════════
#  T271: Edge Density and Non-edges
# ═══════════════════════════════════════════════════════════════

class TestEdgeDensity:
    """T271: Edge density = mu/Phi3, non-edges = ALBERT * v/2.

    E / C(v,2) = 240/780 = 4/13 = mu/Phi3.
    Non-edges = C(v,2) - E = 540 = ALBERT * v/2.
    Edges/Non-edges = mu/q^2 = 4/9.
    """

    def test_edge_density(self):
        density = Fraction(E, math.comb(V, 2))
        assert density == Fraction(MU, PHI3)

    def test_edge_density_value(self):
        assert Fraction(E, math.comb(V, 2)) == Fraction(4, 13)

    def test_non_edges(self):
        non = math.comb(V, 2) - E
        assert non == ALBERT * V // 2

    def test_non_edges_value(self):
        assert math.comb(V, 2) - E == 540

    def test_edge_ratio(self):
        """E / non-edges = mu / q^2 = 4/9."""
        non = math.comb(V, 2) - E
        assert Fraction(E, non) == Fraction(MU, Q**2)


# ═══════════════════════════════════════════════════════════════
#  T272: Trace Ratios and F4
# ═══════════════════════════════════════════════════════════════

class TestTraceRatios:
    """T272: Ratios of spectral power sums reveal Lie algebra dimensions.

    S_n = tr(A^n) = k^n + f*r^n + g*s^n.
    S1=0, S2=2E=480, S3=vf=960, S4=v*624.
    S3/S2 = lam = 2, S4/S2 = 52 = dim(F4), S4/S3 = 2*Phi3 = 26.
    """

    S1 = K + f * r + g * s
    S2 = K**2 + f * r**2 + g * s**2
    S3 = K**3 + f * r**3 + g * s**3
    S4 = K**4 + f * r**4 + g * s**4

    def test_s1_is_zero(self):
        assert self.S1 == 0

    def test_s2_is_2E(self):
        assert self.S2 == 2 * E

    def test_s3_is_vf(self):
        assert self.S3 == V * f

    def test_s3_over_s2_is_lam(self):
        assert Fraction(self.S3, self.S2) == LAM

    def test_s4_over_s2_is_dim_f4(self):
        assert self.S4 // self.S2 == 52

    def test_s4_over_s3_is_2_phi3(self):
        assert Fraction(self.S4, self.S3) == 2 * PHI3

    def test_s2_over_v_is_k(self):
        assert self.S2 // V == K

    def test_s3_over_v_is_f(self):
        assert self.S3 // V == f


# ═══════════════════════════════════════════════════════════════
#  T273: Bernoulli Denominator Tower
# ═══════════════════════════════════════════════════════════════

class TestBernoulliDenomTower:
    """T273: Denominators of Bernoulli numbers encode SRG parameters.

    denom(|B_2|) = 6 = k/lam
    denom(|B_4|) = 30 = v - theta
    denom(|B_6|) = 42 = v + lam
    denom(|B_10|) = 66 = v + k + mu + theta
    """

    def test_b2_denom_is_k_over_lam(self):
        assert Fraction(1, 6) == Fraction(LAM, K)
        assert 6 == K // LAM

    def test_b4_denom_is_v_minus_theta(self):
        assert 30 == V - THETA

    def test_b6_denom_is_v_plus_lam(self):
        assert 42 == V + LAM

    def test_b10_denom_is_sum(self):
        """denom(|B_10|) = 66 = v + k + mu + theta."""
        assert 66 == V + K + MU + THETA

    def test_b6_is_the_answer(self):
        """denom(|B_6|) = 42 = The Answer."""
        assert V + LAM == 42

    def test_bernoulli_tower_ascending(self):
        """6 < 30 < 42 < 66: monotone tower from SRG sums."""
        denoms = [K // LAM, V - THETA, V + LAM, V + K + MU + THETA]
        assert denoms == [6, 30, 42, 66]
        assert all(denoms[i] < denoms[i + 1] for i in range(len(denoms) - 1))


# ═══════════════════════════════════════════════════════════════
#  T274: Partition Function at SRG Values
# ═══════════════════════════════════════════════════════════════

class TestPartitionValues:
    """T274: Integer partition function at SRG parameters.

    p(theta) = p(10) = 42 = The Answer = v + lam.
    p(mu) = p(4) = 5 = N.
    p(dimO) = p(8) = 22 = lam * (k-1).
    """

    # Partitions p(n) for n = 0..12
    P = [1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56, 77]

    def test_p_theta_is_42(self):
        assert self.P[THETA] == 42

    def test_p_theta_is_v_plus_lam(self):
        assert self.P[THETA] == V + LAM

    def test_p_mu_is_N(self):
        assert self.P[MU] == N

    def test_p_dimO_is_lam_times_k_minus_1(self):
        assert self.P[DIM_O] == LAM * (K - 1)

    def test_p_dimO_value(self):
        assert self.P[DIM_O] == 22

    def test_p_theta_minus_p_dimO(self):
        """p(theta) - p(dimO) = 42 - 22 = 20 = v/2."""
        assert self.P[THETA] - self.P[DIM_O] == V // 2


# ═══════════════════════════════════════════════════════════════
#  T275: Abundance and Sigma
# ═══════════════════════════════════════════════════════════════

class TestAbundance:
    """T275: sigma(v) - 2v = theta: the abundance of v encodes the Lovász theta.

    sigma(40) = 90, so abundance = 90 - 80 = 10 = theta.
    Also: d(v) = d(40) = 8 = dimO (number of divisors of v).
    """

    def test_sigma_v(self):
        sig = sum(d for d in range(1, V + 1) if V % d == 0)
        assert sig == 90

    def test_abundance_is_theta(self):
        sig = sum(d for d in range(1, V + 1) if V % d == 0)
        abundance = sig - 2 * V
        assert abundance == THETA

    def test_v_is_abundant(self):
        sig = sum(d for d in range(1, V + 1) if V % d == 0)
        assert sig > 2 * V

    def test_d_v_is_dimO(self):
        """d(v) = d(40) = 8 = dimO."""
        d_v = sum(1 for i in range(1, V + 1) if V % i == 0)
        assert d_v == DIM_O

    def test_abundance_ratio(self):
        """sigma(v)/v = 9/4 = q^2/mu."""
        sig = sum(d for d in range(1, V + 1) if V % d == 0)
        assert Fraction(sig, V) == Fraction(Q**2, MU)
