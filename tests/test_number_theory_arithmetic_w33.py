"""
Phase CXCVIII -- Number-Theoretic Arithmetic Functions on W33 Parameters
=========================================================================
W(3,3) = SRG(40, 12, 2, 4) with Q = 3.

The classical arithmetic functions phi (Euler totient), sigma (sum of
divisors), tau (divisor count), and mu (Mobius) evaluated at the key
integer parameters of W(3,3), Heawood, Fano, and Perkel produce exact
matches to other W33 constants.  Every assertion uses Python's integer
arithmetic (all values are integers; no fractions needed).

Six test groups (40 tests total):
  T1  Euler totient      -- phi(n) equals W33/Perkel constants
  T2  Sum of divisors    -- sigma(n) equals W33/Perkel constants
  T3  Divisor count      -- tau(n) equals W33 eigenvalues/parameters
  T4  Mobius function    -- mu(n) on W33 parameters; squarefree/repeated structure
  T5  Iterated chains    -- sigma/phi compositions produce FANO, LAM, MU
  T6  Composite laws     -- products, ratios, and the PSL(2,7) crown jewel
"""

import pytest

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------
Q = 3

# W(3,3) = SRG(40, 12, 2, 4)
V = 40;  K = 12;  LAM = 2;  MU = 4
THETA = 10;  EIG_R = 2;  EIG_S = -4;  MUL_R = 24;  MUL_S = 15

# Heawood graph
N_H = 14;  K_H = 3;  E_H = 21

# Fano plane
FANO_ORDER = 7

# Perkel graph
V_57 = 57;  K_P = 6;  MUL1 = 18;  MUL2 = 18;  MUL3 = 20


# ------------------------------------------------------------------
# Arithmetic function helpers
# ------------------------------------------------------------------
def phi_euler(n):
    """Euler's totient phi(n): count of 1 <= k <= n with gcd(k,n)=1."""
    result = 1
    nn = n;  d = 2
    while d * d <= nn:
        if nn % d == 0:
            result *= (d - 1);  nn //= d
            while nn % d == 0:
                result *= d;  nn //= d
        d += 1
    if nn > 1:
        result *= (nn - 1)
    return result


def sigma(n):
    """Sum of all positive divisors of n."""
    return sum(d for d in range(1, n + 1) if n % d == 0)


def tau(n):
    """Number of positive divisors of n."""
    return sum(1 for d in range(1, n + 1) if n % d == 0)


def mobius(n):
    """Mobius function: 0 if p^2|n; (-1)^k if n is product of k distinct primes."""
    if n == 1:
        return 1
    factors = [];  nn = n;  d = 2
    while d * d <= nn:
        if nn % d == 0:
            factors.append(d);  nn //= d
            if nn % d == 0:
                return 0
        d += 1
    if nn > 1:
        factors.append(nn)
    return (-1) ** len(factors)


# ------------------------------------------------------------------
# T1 -- Euler totient evaluations
# ------------------------------------------------------------------
class TestT1EulerTotient:

    def test_phi_fano_equals_kp(self):
        """phi(FANO_ORDER) = phi(7) = 6 = K_P (Perkel degree = 2Q) [FANO is prime: phi(p)=p-1]."""
        assert phi_euler(FANO_ORDER) == K_P
        assert phi_euler(7) == 6

    def test_phi_mu_equals_lam(self):
        """phi(MU) = phi(4) = 2 = LAM; phi(Q+1)=Q-1 iff Q=3 [iff Q(Q-3)=0]."""
        assert phi_euler(MU) == LAM
        assert phi_euler(4) == 2
        # Uniqueness: phi(q+1)=q-1 holds for q=3 (phi(4)=2) but not q=2 (phi(3)=2!=1) or q=4 (phi(5)=4!=3)
        assert phi_euler(3) != 1   # q=2 fails
        assert phi_euler(5) != 3   # q=4 fails

    def test_phi_theta_equals_mu(self):
        """phi(THETA) = phi(10) = 4 = MU; phi((Q-1)(Q+2)) = Q+1 = MU at Q=3."""
        assert phi_euler(THETA) == MU
        assert phi_euler(10) == 4

    def test_phi_nh_equals_kp(self):
        """phi(N_H) = phi(14) = phi(2)*phi(7) = 1*6 = 6 = K_P [N_H=2*FANO_ORDER]."""
        assert phi_euler(N_H) == K_P
        assert phi_euler(14) == 6

    def test_phi_eh_equals_k(self):
        """phi(E_H) = phi(21) = phi(3)*phi(7) = 2*6 = 12 = K [E_H=Q*FANO_ORDER=3*7]."""
        assert phi_euler(E_H) == K
        assert phi_euler(21) == 12

    def test_phi_v_equals_q_plus_one_squared(self):
        """phi(V) = phi(40) = 16 = (Q+1)^2 = K + MU [40 = 8*5, phi = 4*4]."""
        assert phi_euler(V) == (Q + 1)**2
        assert phi_euler(V) == K + MU
        assert phi_euler(40) == 16

    def test_phi_v57_equals_q_times_k(self):
        """phi(V_57) = phi(57) = phi(3)*phi(19) = 2*18 = 36 = Q*K."""
        assert phi_euler(V_57) == Q * K
        assert phi_euler(57) == 36


# ------------------------------------------------------------------
# T2 -- Sum of divisors
# ------------------------------------------------------------------
class TestT2SumOfDivisors:

    def test_sigma_lam_equals_q(self):
        """sigma(LAM) = sigma(2) = 1+2 = 3 = Q [2 is prime: sigma(p)=p+1=Q+1... wait p=2=LAM, sigma(2)=3=Q]."""
        assert sigma(LAM) == Q
        assert sigma(2) == 3

    def test_sigma_mu_equals_fano(self):
        """sigma(MU) = sigma(4) = 1+2+4 = 7 = FANO_ORDER; sigma(Q+1)=Q^2-Q+1=Phi_6(Q) at Q=3."""
        assert sigma(MU) == FANO_ORDER
        assert sigma(4) == 7

    def test_sigma_fano_equals_lam_times_mu(self):
        """sigma(FANO) = sigma(7) = 1+7 = 8 = LAM*MU = LAM^3 [FANO is prime]."""
        assert sigma(FANO_ORDER) == LAM * MU
        assert sigma(7) == 8

    def test_sigma_theta_equals_mul1(self):
        """sigma(THETA) = sigma(10) = 1+2+5+10 = 18 = MUL1 = MUL2 (Perkel multiplicities)."""
        assert sigma(THETA) == MUL1
        assert sigma(THETA) == MUL2
        assert sigma(10) == 18

    def test_sigma_k_equals_v_minus_k(self):
        """sigma(K) = sigma(12) = 28 = V-K = Q^3+1 [unique to Q=3]."""
        assert sigma(K) == V - K
        assert sigma(K) == Q**3 + 1
        assert sigma(12) == 28

    def test_sigma_nh_equals_mul_r(self):
        """sigma(N_H) = sigma(14) = 1+2+7+14 = 24 = MUL_R [sum of divisors = W33 larger mult]."""
        assert sigma(N_H) == MUL_R
        assert sigma(14) == 24

    def test_sigma_v_equals_q2_times_theta(self):
        """sigma(V) = sigma(40) = 90 = Q^2 * THETA = 9*10 [40=8*5, sigma=90=Q^2*THETA]."""
        assert sigma(V) == Q**2 * THETA
        assert sigma(40) == 90

    def test_sigma_kp_equals_k(self):
        """sigma(K_P) = sigma(6) = 1+2+3+6 = 12 = K [sum of divisors of Perkel degree = W33 degree]."""
        assert sigma(K_P) == K
        assert sigma(6) == 12


# ------------------------------------------------------------------
# T3 -- Divisor count
# ------------------------------------------------------------------
class TestT3DivisorCount:

    def test_tau_v_equals_lam_times_mu(self):
        """tau(V) = tau(40) = 8 = LAM*MU = LAM^3 [40 = 2^3 * 5 has (3+1)(1+1)=8 divisors]."""
        assert tau(V) == LAM * MU
        assert tau(40) == 8

    def test_tau_k_equals_kp(self):
        """tau(K) = tau(12) = 6 = K_P [12 = 2^2*3 has (2+1)(1+1)=6 divisors = Perkel degree]."""
        assert tau(K) == K_P
        assert tau(12) == 6

    def test_tau_fano_equals_lam(self):
        """tau(FANO) = tau(7) = 2 = LAM [FANO=7 is prime: exactly 2 divisors]."""
        assert tau(FANO_ORDER) == LAM
        assert tau(7) == 2

    def test_tau_mu_equals_q(self):
        """tau(MU) = tau(4) = 3 = Q [4 = 2^2 has 3 divisors: 1,2,4]."""
        assert tau(MU) == Q
        assert tau(4) == 3

    def test_tau_nh_equals_mu(self):
        """tau(N_H) = tau(14) = 4 = MU [14 = 2*7 squarefree with 2 prime factors -> 4 divisors]."""
        assert tau(N_H) == MU
        assert tau(14) == 4

    def test_tau_theta_equals_mu(self):
        """tau(THETA) = tau(10) = 4 = MU [10 = 2*5 squarefree -> 4 divisors]."""
        assert tau(THETA) == MU
        assert tau(10) == 4

    def test_tau_v57_equals_mu(self):
        """tau(V_57) = tau(57) = 4 = MU [57 = 3*19 squarefree -> 4 divisors]."""
        assert tau(V_57) == MU
        assert tau(57) == 4


# ------------------------------------------------------------------
# T4 -- Mobius function
# ------------------------------------------------------------------
class TestT4MobiusFunction:

    def test_mu_fano_equals_minus_one(self):
        """mu(FANO) = mu(7) = -1 [FANO = 7 is prime: mu(p) = -1]."""
        assert mobius(FANO_ORDER) == -1

    def test_mu_nh_equals_one(self):
        """mu(N_H) = mu(14) = mu(2*7) = (-1)^2 = 1 [14 squarefree, 2 distinct primes]."""
        assert mobius(N_H) == 1

    def test_mu_theta_equals_one(self):
        """mu(THETA) = mu(10) = mu(2*5) = 1 [10 squarefree, 2 distinct primes]."""
        assert mobius(THETA) == 1

    def test_mu_eh_equals_one(self):
        """mu(E_H) = mu(21) = mu(3*7) = 1 [21 squarefree, 2 distinct primes]."""
        assert mobius(E_H) == 1

    def test_mu_v_equals_zero(self):
        """mu(V) = mu(40) = 0 [40 = 2^3 * 5: 4 | 40 so mu = 0]."""
        assert mobius(V) == 0

    def test_mu_k_equals_zero(self):
        """mu(K) = mu(12) = 0 [12 = 2^2 * 3: 4 | 12 so mu = 0]."""
        assert mobius(K) == 0


# ------------------------------------------------------------------
# T5 -- Iterated chains
# ------------------------------------------------------------------
class TestT5IteratedChains:

    def test_sigma_phi_k_equals_fano(self):
        """sigma(phi(K)) = sigma(phi(12)) = sigma(4) = 7 = FANO_ORDER."""
        assert sigma(phi_euler(K)) == FANO_ORDER
        assert phi_euler(K) == MU     # phi(12) = 4 = MU (intermediate)
        assert sigma(MU) == FANO_ORDER

    def test_sigma_sigma_mu_equals_lam_times_mu(self):
        """sigma(sigma(MU)) = sigma(sigma(4)) = sigma(7) = 8 = LAM*MU = LAM^3."""
        assert sigma(sigma(MU)) == LAM * MU
        assert sigma(MU) == FANO_ORDER   # intermediate step
        assert sigma(FANO_ORDER) == LAM * MU

    def test_phi_phi_fano_equals_lam(self):
        """phi(phi(FANO)) = phi(phi(7)) = phi(6) = 2 = LAM."""
        assert phi_euler(phi_euler(FANO_ORDER)) == LAM
        assert phi_euler(FANO_ORDER) == K_P   # intermediate: phi(7)=6=K_P
        assert phi_euler(K_P) == LAM           # phi(6) = 2 = LAM

    def test_sigma_sigma_lam_equals_mu(self):
        """sigma(sigma(LAM)) = sigma(sigma(2)) = sigma(3) = 4 = MU."""
        assert sigma(sigma(LAM)) == MU
        assert sigma(LAM) == Q     # intermediate: sigma(2)=3=Q
        assert sigma(Q) == MU     # sigma(3)=4=MU

    def test_sigma_phi_theta_equals_fano(self):
        """sigma(phi(THETA)) = sigma(phi(10)) = sigma(4) = 7 = FANO_ORDER."""
        assert sigma(phi_euler(THETA)) == FANO_ORDER
        assert phi_euler(THETA) == MU   # phi(10)=4=MU

    def test_three_step_chain(self):
        """LAM -[sigma]-> Q -[sigma]-> MU -[sigma]-> FANO -[sigma]-> LAM*MU chain."""
        assert sigma(LAM) == Q
        assert sigma(Q) == MU
        assert sigma(MU) == FANO_ORDER
        assert sigma(FANO_ORDER) == LAM * MU


# ------------------------------------------------------------------
# T6 -- Composite arithmetic laws
# ------------------------------------------------------------------
class TestT6CompositeArithmeticLaws:

    def test_product_sigma_lam_mu_fano_equals_psl27(self):
        """sigma(LAM)*sigma(MU)*sigma(FANO) = 3*7*8 = 168 = |PSL(2,7)|."""
        product = sigma(LAM) * sigma(MU) * sigma(FANO_ORDER)
        assert product == 168
        psl27 = 7 * (7**2 - 1) // 2
        assert product == psl27

    def test_sum_sigma_lam_mu_fano_equals_mul1(self):
        """sigma(LAM)+sigma(MU)+sigma(FANO) = 3+7+8 = 18 = MUL1 = MUL2 (Perkel multiplicities)."""
        total = sigma(LAM) + sigma(MU) + sigma(FANO_ORDER)
        assert total == MUL1
        assert total == MUL2

    def test_sigma_k_over_lam_equals_nh(self):
        """sigma(K)/LAM = 28/2 = 14 = N_H."""
        assert sigma(K) % LAM == 0
        assert sigma(K) // LAM == N_H

    def test_sigma_k_over_mu_equals_fano(self):
        """sigma(K)/MU = 28/4 = 7 = FANO_ORDER."""
        assert sigma(K) % MU == 0
        assert sigma(K) // MU == FANO_ORDER

    def test_sigma_nh_times_sigma_theta_equals_phi_v_times_q3(self):
        """sigma(N_H)*sigma(THETA) = 24*18 = 432 = phi(V)*Q^3 = 16*27."""
        assert sigma(N_H) * sigma(THETA) == phi_euler(V) * Q**3
        assert sigma(N_H) * sigma(THETA) == 432

    def test_phi_v_sigma_v_over_v_equals_q_times_k(self):
        """phi(V)*sigma(V)/V = 16*90/40 = 36 = Q*K = phi(V_57)."""
        product = phi_euler(V) * sigma(V)
        assert product % V == 0
        assert product // V == Q * K
        assert product // V == phi_euler(V_57)
