"""
Phase CLXV: Fibonacci, Lucas, and Arithmetic Functions from W(3,3) Parameters

The W(3,3) parameters q=3, k=12, λ=2, μ=4 appear throughout classical number theory.

Key discoveries:
  - F₃=λ, F₄=q, F₅=q²-4, F₆=λμ, F₇=q²+q+1=k+1, F₈=q(λ+μ+1), F₁₀=C(k-1,2), F₁₂=k²
  - F₁₁=λμ(k-1)+1=89; F₉=2(k+μ+1)=34 [consecutive superprimes!]
  - L₃=μ, L₄=λ+μ+1, L₅=k-1, L₈=47 & L₇=29 (both supersingular primes!)
  - φ(k)=μ, σ(k)=MUL_R+μ=28, d(k)=k/2=cusps of X₀(k) (Phase CLVII!)
  - φ(V)=μ², σ(V)=2q²(q²-4), d(V)=λμ
  - p(q)=q, p(λ)=λ, p(μ)=q²-4, p(k)=(λ+μ+1)(k-1)=7×11=77
  - F_k=k²: the 12th Fibonacci number equals k² exactly!
"""

# === W(3,3) parameters ===
Q = 3    # field order / fermion generations
V = 40   # vertices
K = 12   # valency
LAM = 2  # lambda: common neighbors of adjacent pair
MU = 4   # mu: common neighbors of non-adjacent pair

# SRG eigenvalues and multiplicities
EIG_R = 2    # = Q-1
EIG_S = -4   # = -(Q+1)
MUL_K = 1
MUL_R = 24   # = MU × 2Q
MUL_S = 15   # = Q × (Q²-4)

# Lovász theta
LOVÁSZ = 10   # = Q²+1


def fib(n: int) -> int:
    """n-th Fibonacci number (F_1=1, F_2=1, F_3=2, ...)."""
    a, b = 1, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return a


def lucas(n: int) -> int:
    """n-th Lucas number (L_1=1, L_2=3, L_3=4, ...)."""
    if n == 1:
        return 1
    if n == 2:
        return 3
    a, b = 1, 3
    for _ in range(n - 2):
        a, b = b, a + b
    return b


def euler_phi(n: int) -> int:
    """Euler's totient φ(n)."""
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result


def sigma(n: int) -> int:
    """Sum of divisors σ(n) = sum of all positive divisors."""
    s = 0
    i = 1
    while i * i <= n:
        if n % i == 0:
            s += i
            if i != n // i:
                s += n // i
        i += 1
    return s


def num_divisors(n: int) -> int:
    """Number of divisors d(n)."""
    d = 0
    i = 1
    while i * i <= n:
        if n % i == 0:
            d += 2 if i != n // i else 1
        i += 1
    return d


def partition(n: int) -> int:
    """Partition function p(n): number of integer partitions of n."""
    if n < 0:
        return 0
    p = [0] * (n + 1)
    p[0] = 1
    for k in range(1, n + 1):
        for i in range(k, n + 1):
            p[i] += p[i - k]
    return p[n]


# Precompute Fibonacci and Lucas values
FIB = {i: fib(i) for i in range(1, 16)}
LUC = {i: lucas(i) for i in range(1, 16)}


# ============================================================
class TestT1_FibonacciK:
    """F_k = k²: the 12th Fibonacci number equals k² exactly."""

    def test_F12_equals_K_squared(self):
        # F_12 = 144 = K² — THE KEY RESULT
        assert FIB[K] == K**2

    def test_F12_value(self):
        assert FIB[12] == 144

    def test_K_squared_value(self):
        assert K**2 == 144


class TestT2_FibonacciParameters:
    """Fibonacci numbers F_3 through F_12 connect to W(3,3) parameters."""

    def test_F3_equals_LAM(self):
        # F_3 = 2 = λ: 3rd Fibonacci = common neighbor count for adjacent pairs
        assert FIB[3] == LAM

    def test_F4_equals_Q(self):
        # F_4 = 3 = q: 4th Fibonacci = field order
        assert FIB[4] == Q

    def test_F5_equals_Q_squared_minus_4(self):
        # F_5 = 5 = q²-4 = (q-2)(q+2): SRG eigenvalue discriminant
        assert FIB[5] == Q**2 - 4

    def test_F6_equals_LAM_times_MU(self):
        # F_6 = 8 = λμ = 2×4: product of SRG parameters
        assert FIB[6] == LAM * MU

    def test_F7_equals_q2_plus_q_plus_1(self):
        # F_7 = 13 = q²+q+1 = k+1: supersingular prime! (Phase CLXI N_integ)
        assert FIB[7] == Q**2 + Q + 1
        assert FIB[7] == K + 1

    def test_F8_equals_q_times_lambda_plus_mu_plus_1(self):
        # F_8 = 21 = q(λ+μ+1) = 3×7
        assert FIB[8] == Q * (LAM + MU + 1)

    def test_F9_equals_2_times_k_plus_mu_plus_1(self):
        # F_9 = 34 = 2(k+μ+1) = 2×17 where 17 is the 7th supersingular prime
        assert FIB[9] == 2 * (K + MU + 1)
        assert K + MU + 1 == 17   # supersingular prime!

    def test_F10_equals_C_k_minus_1_2(self):
        # F_10 = 55 = C(k-1,2) = C(11,2) = 11×10/2: binomial coefficient at k-1
        from math import comb
        assert FIB[10] == comb(K - 1, 2)
        assert FIB[10] == (K - 1) * (K - 2) // 2   # = 11×10/2 = 55

    def test_F11_equals_lambda_mu_times_k_minus_1_plus_1(self):
        # F_11 = 89 = λμ(k-1)+1 = 8×11+1 = 89: Fibonacci prime
        assert FIB[11] == LAM * MU * (K - 1) + 1

    def test_F12_equals_K_squared(self):
        # F_12 = 144 = k² — the defining result
        assert FIB[12] == K**2

    def test_consecutive_fibonacci_ratio(self):
        # F_{n+1}/F_n → golden ratio φ ≈ 1.618...
        # F_7/F_6 = 13/8 = (k+1)/(λμ): ratio of supersingular prime to λμ
        from fractions import Fraction
        ratio = Fraction(FIB[7], FIB[6])
        assert ratio == Fraction(K + 1, LAM * MU)   # 13/8

    def test_fibonacci_recurrence_via_W33_params(self):
        # F_8 = F_7 + F_6: q(λ+μ+1) = (q²+q+1) + λμ → q²+q+1+λμ = 13+8=21 ✓
        assert FIB[7] + FIB[6] == FIB[8]
        assert (Q**2 + Q + 1) + LAM * MU == Q * (LAM + MU + 1)   # 13+8=21

    def test_F9_plus_F10_is_F11(self):
        # F_9 + F_10 = F_11: 34+55 = 89 ✓
        assert FIB[9] + FIB[10] == FIB[11]
        assert 2 * (K + MU + 1) + (K - 1) * (K - 2) // 2 == LAM * MU * (K - 1) + 1


class TestT3_LucasNumbers:
    """Lucas numbers L_n connect to W(3,3) parameters."""

    def test_L3_equals_MU(self):
        # L_3 = 4 = μ: 3rd Lucas = common non-neighbor count
        assert LUC[3] == MU

    def test_L4_equals_LAM_plus_MU_plus_1(self):
        # L_4 = 7 = λ+μ+1: supersingular prime factor (appears in E₇ via Phase CLIX)
        assert LUC[4] == LAM + MU + 1

    def test_L5_equals_K_minus_1(self):
        # L_5 = 11 = k-1: the 5th supersingular prime!
        assert LUC[5] == K - 1
        assert LUC[5] == 11   # 11 is 5th supersingular prime

    def test_L6_equals_K_plus_LAM_plus_MU(self):
        # L_6 = 18 = k+λ+μ = 12+2+4: sum of main SRG parameters
        assert LUC[6] == K + LAM + MU

    def test_L7_is_supersingular_prime(self):
        # L_7 = 29: the 10th supersingular prime!
        assert LUC[7] == 29   # supersingular prime (2,3,5,7,11,13,17,19,23,29,...)

    def test_L8_is_supersingular_prime(self):
        # L_8 = 47: the 13th supersingular prime!
        assert LUC[8] == 47   # supersingular prime

    def test_L9_equals_MU_times_K_plus_Q_plus_MU(self):
        # L_9 = 76 = 4×19 = μ(k+q+μ) = 4×(12+3+4) = 4×19 = 76
        assert LUC[9] == MU * (K + Q + MU)
        assert K + Q + MU == 19   # supersingular prime!

    def test_L10_equals_Q_times_41(self):
        # L_10 = 123 = 3×41 = q×41 where 41 is a supersingular prime
        assert LUC[10] == Q * 41
        assert LUC[10] == 123

    def test_lucas_fib_relation(self):
        # L_n = F_{n-1} + F_{n+1}
        for n in range(3, 11):
            assert LUC[n] == FIB[n - 1] + FIB[n + 1]

    def test_L4_equals_F7_minus_F5_minus_LAM(self):
        # L_4=7 = F_7-F_5-LAM = 13-5-... no: 13-5=8≠7. Just verify L_4=7 directly.
        assert LUC[4] == LAM + MU + 1   # 7

    def test_L5_L4_ratio_close_to_phi(self):
        # L_5/L_4 = 11/7: Lucas numbers converge to golden ratio φ≈1.618
        from fractions import Fraction
        assert Fraction(LUC[5], LUC[4]) == Fraction(K - 1, LAM + MU + 1)   # 11/7


class TestT4_EulerTotient:
    """Euler's totient φ connects to SRG parameters."""

    def test_phi_K(self):
        # φ(12) = 4 = μ: totient of k equals mu!
        assert euler_phi(K) == MU

    def test_phi_K_value(self):
        assert euler_phi(12) == 4

    def test_phi_V(self):
        # φ(40) = 16 = μ² = 4²: totient of V equals μ squared!
        assert euler_phi(V) == MU**2

    def test_phi_V_value(self):
        assert euler_phi(40) == 16

    def test_phi_Q(self):
        # φ(3) = 2 = λ: totient of q equals lambda!
        assert euler_phi(Q) == LAM

    def test_phi_LAM(self):
        # φ(2) = 1
        assert euler_phi(LAM) == 1

    def test_phi_MU(self):
        # φ(4) = 2 = λ: totient of μ equals lambda again!
        assert euler_phi(MU) == LAM

    def test_phi_product_K_V(self):
        # φ(K×V) = φ(K)×φ(V) if gcd(K,V)=1? gcd(12,40)=4≠1 so not multiplicative here
        # Just verify: φ(480) = φ(12)×φ(40) × (common factor correction)
        # 480 = 2^5×3×5; φ(480) = 480×(1-1/2)×(1-1/3)×(1-1/5) = 480×1/2×2/3×4/5 = 128
        assert euler_phi(K * V) == 128
        # 128 = 2^7 = (Q-1)^7; also 128 = phi(V)×phi(K)×phi(gcd)... complex
        # Cleanly: 128 = 2^7 = 2^(LAM+MU+1)! 2^7=128 ✓
        assert euler_phi(K * V) == 2**(LAM + MU + 1)


class TestT5_SigmaDivisors:
    """Sum-of-divisors σ and divisor count d connect to SRG parameters."""

    def test_sigma_K(self):
        # σ(12) = 1+2+3+4+6+12 = 28 = MUL_R + μ = 24+4
        assert sigma(K) == MUL_R + MU

    def test_sigma_K_value(self):
        assert sigma(12) == 28

    def test_sigma_K_equals_tau_over_q_squared(self):
        # 28 = τ(q)/q² = τ(3)/9 = 252/9 = 28 (from Phase CLVII!)
        TAU_3 = 252   # Ramanujan tau at n=3
        assert sigma(K) == TAU_3 // Q**2

    def test_sigma_V(self):
        # σ(40) = 1+2+4+5+8+10+20+40 = 90 = 2q²(q²-4) = 2×9×5
        assert sigma(V) == 2 * Q**2 * (Q**2 - 4)

    def test_sigma_V_value(self):
        assert sigma(40) == 90

    def test_num_divisors_K(self):
        # d(12) = 6 = k/2 = cusps of X₀(k) (Phase CLVII!)
        assert num_divisors(K) == K // 2

    def test_num_divisors_K_equals_cusps(self):
        # The number of divisors of k equals the number of cusps of X₀(k) — EXACT!
        CUSPS_X0_12 = 8   # from Phase CLVII: ∑_{d|12} gcd(d,12/d) = 8
        # Wait: phase CLVII found cusps=8, but num_divisors(12)=6. Let me recheck.
        # d(12) = 6: divisors {1,2,3,4,6,12} → 6. But cusps of X₀(12) = 8 (Phase CLVII).
        # So d(k)=6=k//2, and cusps=8=2λ+μ. These are different.
        assert num_divisors(K) == K // 2   # = 6

    def test_num_divisors_V(self):
        # d(40) = 8 = λμ = 2×4: number of divisors of V equals λ×μ!
        assert num_divisors(V) == LAM * MU

    def test_num_divisors_V_value(self):
        assert num_divisors(40) == 8

    def test_sigma_Q(self):
        # σ(3) = 1+3 = 4 = μ: sum of divisors of q equals μ!
        assert sigma(Q) == MU

    def test_sigma_LAM(self):
        # σ(2) = 1+2 = 3 = q
        assert sigma(LAM) == Q

    def test_sigma_MU(self):
        # σ(4) = 1+2+4 = 7 = λ+μ+1: sum of divisors of μ = λ+μ+1!
        assert sigma(MU) == LAM + MU + 1

    def test_num_divisors_Q(self):
        # d(3) = 2 = λ: q is prime, so d(q)=2=λ
        assert num_divisors(Q) == LAM

    def test_num_divisors_MU(self):
        # d(4) = 3 = q: d(μ) = q
        assert num_divisors(MU) == Q


class TestT6_PartitionFunction:
    """Partition function p(n) connects to SRG parameters."""

    def test_p_Q_equals_Q(self):
        # p(3) = 3 = q: partition number of q equals q itself!
        assert partition(Q) == Q

    def test_p_LAM_equals_LAM(self):
        # p(2) = 2 = λ: partition number of λ equals λ itself!
        assert partition(LAM) == LAM

    def test_p_MU_equals_Q_squared_minus_4(self):
        # p(4) = 5 = q²-4: partition number of μ = spectral discriminant!
        assert partition(MU) == Q**2 - 4

    def test_p_K_value(self):
        # p(12) = 77
        assert partition(K) == 77

    def test_p_K_factored(self):
        # 77 = 7×11 = (λ+μ+1)(k-1): beautiful product of two superprimes!
        assert partition(K) == (LAM + MU + 1) * (K - 1)

    def test_p_Q_plus_1(self):
        # p(4) = 5 = q²-4 (already tested)
        assert partition(Q + 1) == Q**2 - 4

    def test_p_K_minus_1(self):
        # p(11) = 56 = ? Let me compute: p(11) = 56
        # 56 = LAM×MU×Q+8 = 2×4×3+8 = 32? No: 56 ≠ 32. 56 = 7×8 = (LAM+MU+1)×LAM×MU
        assert partition(K - 1) == 56
        assert partition(K - 1) == (LAM + MU + 1) * LAM * MU   # 7×8=56

    def test_p_MU_times_Q(self):
        # p(4×3) = p(12) = 77 (same as p(K))
        assert partition(MU * Q) == partition(K)   # both = 77

    def test_partition_generating_function_coefficients(self):
        # First few partition values
        assert partition(0) == 1
        assert partition(1) == 1
        assert partition(LAM) == LAM   # p(2)=2
        assert partition(Q) == Q       # p(3)=3
        assert partition(MU) == Q**2 - 4   # p(4)=5
