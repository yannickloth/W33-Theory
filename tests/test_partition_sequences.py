"""
Theorems T411–T425: Partition Theory, Sequence Cascades & Arithmetic Structures

Phase XXX explores partition functions, classical integer sequences (Pell,
Lucas, Padovan/Perrin), the Carmichael function, Jordan totient, Pochhammer
symbols, golden ratio powers, Stirling numbers (1st & 2nd kind), Wilson primes,
base-3 digit sums, magic constants, arithmetic progressions, and cubic residues
— all locking onto the SRG(40,12,2,4) parameter set.

T411: Partition Function Fixed Points — p(λ)=λ, p(q)=q; cascade p(μ)=N, p(Φ₆)=g
T412: Pell Number Triple — Pell(2)=λ, Pell(3)=N, Pell(4)=k
T413: Lucas Low-Index Quartet — L(2)=q, L(3)=μ, L(4)=Φ₆
T414: Carmichael Convergence — λ_c maps 6 values→λ, 5 values→μ
T415: Jordan Totient Tower — J₂(λ)=q, J₂(q)=dimO, J₂(μ)=k, J₄(μ)=E
T416: Pochhammer Relations — (λ)₂=δ, (λ)₃=f, (q)₂=k, (g)₂=E
T417: Golden Ratio Powers — round(φⁿ) for n=1..4 = {λ,q,μ,Φ₆}
T418: Unsigned Stirling 1st Kind — |s(4,1)|=δ, |s(5,1)|=f, |s(5,4)|=θ
T419: Restricted Partition Extended — p(g,μ parts)=albert, p(θ,q parts)=dimO
T420: Wilson Prime Pair — N=5 and Φ₃=13 are Wilson primes
T421: Base-3 Digit Sum — S₃(E)=dimO, S₃(v)=μ, S₃(g)=q
T422: Power Sum & Magic — λ²+q²=Φ₃; Magic(λ)=N, Magic(q)=g
T423: Stirling 2nd Kind at μ — S₂(μ,2)=Φ₆, S₂(μ,3)=δ
T424: Arithmetic Progressions — 7-term AP d=1, 6-term AP d=λ, 4-term AP d=q
T425: Cubic Residue Counts — #CR(Φ₃)=μ, #CR(Φ₆)=λ, #CR(N)=μ
"""

import math
from functools import lru_cache

# ── SRG(40,12,2,4) constants ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = 240; R = 2; S = -4; F = 24; G = 15
THETA = 10; PHI3 = 13; PHI6 = 7; DIMO = 8; N = 5
ALBERT = 27; DELTA = 6
VALS = {V, K, LAM, MU, Q, E, R, S, F, G, THETA, PHI3, PHI6, DIMO, N, ALBERT, DELTA}


# ── Helper functions ──

@lru_cache(maxsize=500)
def _partition_p(n):
    """Unrestricted partitions of n (Euler pentagonal recurrence)."""
    if n < 0:
        return 0
    if n == 0:
        return 1
    total = 0
    for i in range(1, n + 1):
        sign = (-1) ** (i + 1)
        g1 = i * (3 * i - 1) // 2
        g2 = i * (3 * i + 1) // 2
        if g1 <= n:
            total += sign * _partition_p(n - g1)
        if g2 <= n:
            total += sign * _partition_p(n - g2)
    return total


def _pell(n):
    """Pell numbers: P(0)=0, P(1)=1, P(n)=2P(n-1)+P(n-2)."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, 2 * b + a
    return a


def _lucas(n):
    """Lucas numbers: L(0)=2, L(1)=1, L(n)=L(n-1)+L(n-2)."""
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _carmichael(n):
    """Carmichael function λ(n)."""
    if n <= 2:
        return 1
    factors = {}
    temp = n
    d = 2
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    result = 1
    for p, e in factors.items():
        if p == 2 and e >= 3:
            pe = p ** (e - 2)
        elif p == 2 and e == 2:
            pe = 2
        elif p == 2 and e == 1:
            pe = 1
        else:
            pe = (p - 1) * p ** (e - 1)
        result = result * pe // math.gcd(result, pe)
    return result


def _jordan_totient(k_exp, n):
    """Jordan totient J_k(n) = n^k * Π_{p|n}(1 - 1/p^k)."""
    result = n ** k_exp
    temp = n
    p = 2
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result = result * (p ** k_exp - 1) // (p ** k_exp)
        p += 1
    if temp > 1:
        result = result * (temp ** k_exp - 1) // (temp ** k_exp)
    return result


def _rising_factorial(x, n):
    """Pochhammer symbol (x)_n = x(x+1)...(x+n-1)."""
    prod = 1
    for i in range(n):
        prod *= (x + i)
    return prod


@lru_cache(maxsize=10000)
def _stirling1_unsigned(n, k):
    """Unsigned Stirling number of the first kind |s(n,k)|."""
    if n == 0 and k == 0:
        return 1
    if n == 0 or k == 0:
        return 0
    return (n - 1) * _stirling1_unsigned(n - 1, k) + _stirling1_unsigned(n - 1, k - 1)


@lru_cache(maxsize=10000)
def _stirling2(n, k):
    """Stirling number of the second kind S(n,k)."""
    if n == 0 and k == 0:
        return 1
    if n == 0 or k == 0:
        return 0
    return k * _stirling2(n - 1, k) + _stirling2(n - 1, k - 1)


@lru_cache(maxsize=10000)
def _partitions_k_parts(n, k):
    """Number of partitions of n into exactly k positive parts."""
    if k == 0:
        return 1 if n == 0 else 0
    if n <= 0 or k < 0 or k > n:
        return 0
    return _partitions_k_parts(n - 1, k - 1) + _partitions_k_parts(n - k, k)


def _digit_sum_base(n, b):
    """Sum of digits of n in base b."""
    s = 0
    while n > 0:
        s += n % b
        n //= b
    return s


def _magic_constant(n):
    """Magic constant of n×n normal magic square: n(n²+1)/2."""
    return n * (n ** 2 + 1) // 2


# ═══════════════════════════════════════════════════════════════
# T411 — Partition Function Fixed Points & Cascade
# ═══════════════════════════════════════════════════════════════

class TestPartitionFixedPoints:
    """T411: p(λ)=λ and p(q)=q are partition fixed points.

    p(2)=2=λ, p(3)=3=q: TWO fixed points!
    The cascade continues: p(μ)=N=5, p(Φ₆)=g=15.
    """

    def test_p_lam_fixedpoint(self):
        """p(2) = 2 = λ: partition function fixed point."""
        assert _partition_p(LAM) == LAM

    def test_p_q_fixedpoint(self):
        """p(3) = 3 = q: partition function fixed point."""
        assert _partition_p(Q) == Q

    def test_p_mu_is_N(self):
        """p(4) = 5 = N."""
        assert _partition_p(MU) == N

    def test_p_phi6_is_g(self):
        """p(7) = 15 = g."""
        assert _partition_p(PHI6) == G

    def test_cascade_chain(self):
        """p maps λ→λ, q→q, μ→N, N→Φ₆, Φ₆→g — all SRG values."""
        chain = [_partition_p(x) for x in [LAM, Q, MU, N, PHI6]]
        assert chain == [LAM, Q, N, PHI6, G]


# ═══════════════════════════════════════════════════════════════
# T412 — Pell Number Triple
# ═══════════════════════════════════════════════════════════════

class TestPellTriple:
    """T412: Pell(2)=λ=2, Pell(3)=N=5, Pell(4)=k=12.

    Three consecutive Pell numbers are SRG values.
    """

    def test_pell_2_is_lam(self):
        """Pell(2) = 2 = λ."""
        assert _pell(2) == LAM

    def test_pell_3_is_N(self):
        """Pell(3) = 5 = N."""
        assert _pell(3) == N

    def test_pell_4_is_k(self):
        """Pell(4) = 12 = k."""
        assert _pell(4) == K

    def test_pell_recurrence(self):
        """Pell(4) = 2·Pell(3) + Pell(2) = 2N + λ = k."""
        assert 2 * N + LAM == K

    def test_pell_ratios(self):
        """Pell(4)/Pell(3) = k/N = 12/5."""
        assert _pell(4) * N == _pell(3) * K


# ═══════════════════════════════════════════════════════════════
# T413 — Lucas Low-Index Quartet
# ═══════════════════════════════════════════════════════════════

class TestLucasLowIndex:
    """T413: L(2)=q, L(3)=μ, L(4)=Φ₆.

    Three consecutive Lucas numbers at low indices are SRG values.
    """

    def test_lucas_2_is_q(self):
        """L(2) = 3 = q."""
        assert _lucas(2) == Q

    def test_lucas_3_is_mu(self):
        """L(3) = 4 = μ."""
        assert _lucas(3) == MU

    def test_lucas_4_is_phi6(self):
        """L(4) = 7 = Φ₆."""
        assert _lucas(4) == PHI6

    def test_lucas_recurrence(self):
        """L(4) = L(3) + L(2) = μ + q = Φ₆."""
        assert MU + Q == PHI6

    def test_lucas_window(self):
        """L(2..4) = (q, μ, Φ₆) — consecutive SRG values."""
        window = [_lucas(i) for i in range(2, 5)]
        assert window == [Q, MU, PHI6]


# ═══════════════════════════════════════════════════════════════
# T414 — Carmichael Convergence
# ═══════════════════════════════════════════════════════════════

class TestCarmichaelConvergence:
    """T414: Carmichael λ_c maps SRG values to SRG values.

    Six values map to λ=2: {q, μ, δ, dimO, k, f}
    Five values map to μ=4: {N, θ, g, v, E}
    Also: λ_c(Φ₆)=δ, λ_c(Φ₃)=k.
    """

    def test_six_to_lambda(self):
        """λ_c maps {q,μ,δ,dimO,k,f} → λ=2."""
        targets = [Q, MU, DELTA, DIMO, K, F]
        assert all(_carmichael(t) == LAM for t in targets)

    def test_five_to_mu(self):
        """λ_c maps {N,θ,g,v,E} → μ=4."""
        targets = [N, THETA, G, V, E]
        assert all(_carmichael(t) == MU for t in targets)

    def test_phi6_to_delta(self):
        """λ_c(Φ₆) = λ_c(7) = 6 = δ."""
        assert _carmichael(PHI6) == DELTA

    def test_phi3_to_k(self):
        """λ_c(Φ₃) = λ_c(13) = 12 = k."""
        assert _carmichael(PHI3) == K

    def test_convergence_structure(self):
        """11 of 13 tested values (v>1) map to {λ, μ, δ, k} — all SRG."""
        results = {_carmichael(x) for x in [Q, MU, N, DELTA, PHI6, DIMO, THETA, K, PHI3, G, F, V, E]}
        assert results == {LAM, MU, DELTA, K}


# ═══════════════════════════════════════════════════════════════
# T415 — Jordan Totient Tower
# ═══════════════════════════════════════════════════════════════

class TestJordanTotientTower:
    """T415: Jordan totient J_k(n) maps SRG → SRG across multiple orders.

    J₂(λ)=q, J₂(q)=dimO, J₂(μ)=k, J₂(N)=f
    J₃(λ)=Φ₆; J₄(λ)=g; J₄(μ)=E(!)
    """

    def test_j2_lam_is_q(self):
        """J₂(2) = 3 = q."""
        assert _jordan_totient(2, LAM) == Q

    def test_j2_q_is_dimO(self):
        """J₂(3) = 8 = dimO."""
        assert _jordan_totient(2, Q) == DIMO

    def test_j2_mu_is_k(self):
        """J₂(4) = 12 = k."""
        assert _jordan_totient(2, MU) == K

    def test_j2_N_is_f(self):
        """J₂(5) = 24 = f."""
        assert _jordan_totient(2, N) == F

    def test_j4_mu_is_E(self):
        """J₄(4) = 240 = E — the edge count emerges from J₄(μ)!"""
        assert _jordan_totient(4, MU) == E


# ═══════════════════════════════════════════════════════════════
# T416 — Pochhammer Rising Factorial
# ═══════════════════════════════════════════════════════════════

class TestPochhammerRelations:
    """T416: Rising factorials map SRG → SRG.

    (λ)₂ = 2·3 = 6 = δ
    (λ)₃ = 2·3·4 = 24 = f
    (q)₂ = 3·4 = 12 = k
    (g)₂ = 15·16 = 240 = E
    """

    def test_lam_rising_2_is_delta(self):
        """(λ)₂ = λ(λ+1) = 2·3 = 6 = δ."""
        assert _rising_factorial(LAM, 2) == DELTA

    def test_lam_rising_3_is_f(self):
        """(λ)₃ = λ(λ+1)(λ+2) = 2·3·4 = 24 = f."""
        assert _rising_factorial(LAM, 3) == F

    def test_q_rising_2_is_k(self):
        """(q)₂ = q(q+1) = 3·4 = 12 = k."""
        assert _rising_factorial(Q, 2) == K

    def test_g_rising_2_is_E(self):
        """(g)₂ = g(g+1) = 15·16 = 240 = E."""
        assert _rising_factorial(G, 2) == E

    def test_rising_factorial_chain(self):
        """(λ)₁=λ, (λ)₂=δ, (λ)₃=f — three consecutive rising factorials."""
        assert [_rising_factorial(LAM, n) for n in [1, 2, 3]] == [LAM, DELTA, F]


# ═══════════════════════════════════════════════════════════════
# T417 — Golden Ratio Power Cascade
# ═══════════════════════════════════════════════════════════════

class TestGoldenRatioPowers:
    """T417: round(φⁿ) for n=1..4 produces {λ, q, μ, Φ₆}.

    φ = (1+√5)/2 ≈ 1.618
    round(φ) = 2 = λ, round(φ²) = 3 = q,
    round(φ³) = 4 = μ, round(φ⁴) = 7 = Φ₆.
    """
    PHI = (1 + 5 ** 0.5) / 2

    def test_phi1_is_lam(self):
        """round(φ) = 2 = λ."""
        assert round(self.PHI) == LAM

    def test_phi2_is_q(self):
        """round(φ²) = 3 = q."""
        assert round(self.PHI ** 2) == Q

    def test_phi3_is_mu(self):
        """round(φ³) = 4 = μ."""
        assert round(self.PHI ** 3) == MU

    def test_phi4_is_phi6(self):
        """round(φ⁴) = 7 = Φ₆."""
        assert round(self.PHI ** 4) == PHI6

    def test_golden_cascade(self):
        """Four consecutive golden ratio powers round to SRG values."""
        cascade = [round(self.PHI ** n) for n in range(1, 5)]
        assert cascade == [LAM, Q, MU, PHI6]


# ═══════════════════════════════════════════════════════════════
# T418 — Unsigned Stirling Numbers of the First Kind
# ═══════════════════════════════════════════════════════════════

class TestStirling1stKind:
    """T418: |s(n,k)| (unsigned Stirling 1st kind) at SRG indices = SRG values.

    |s(4,1)| = 3! = 6 = δ
    |s(5,1)| = 4! = 24 = f
    |s(5,4)| = C(5,2) = 10 = θ
    |s(6,5)| = C(6,2) = 15 = g
    """

    def test_s41_is_delta(self):
        """|s(4,1)| = 6 = δ."""
        assert _stirling1_unsigned(4, 1) == DELTA

    def test_s51_is_f(self):
        """|s(5,1)| = 24 = f."""
        assert _stirling1_unsigned(5, 1) == F

    def test_s54_is_theta(self):
        """|s(5,4)| = 10 = θ."""
        assert _stirling1_unsigned(5, 4) == THETA

    def test_s65_is_g(self):
        """|s(6,5)| = 15 = g."""
        assert _stirling1_unsigned(6, 5) == G

    def test_s_n1_is_factorial(self):
        """|s(n,1)| = (n-1)! for all n ≥ 1."""
        for n in range(1, 7):
            assert _stirling1_unsigned(n, 1) == math.factorial(n - 1)


# ═══════════════════════════════════════════════════════════════
# T419 — Restricted Partition Extended
# ═══════════════════════════════════════════════════════════════

class TestRestrictedPartitionExtended:
    """T419: Partitions of non-k values into SRG-many parts = SRG values.

    p(g, μ parts) = p(15, 4) = 27 = albert(!)
    p(albert, λ parts) = p(27, 2) = 13 = Φ₃
    p(f, λ parts) = p(24, 2) = 12 = k
    p(θ, q parts) = p(10, 3) = 8 = dimO
    """

    def test_p_g_mu_is_albert(self):
        """p(15, 4 parts) = 27 = albert."""
        assert _partitions_k_parts(G, MU) == ALBERT

    def test_p_albert_lam_is_phi3(self):
        """p(27, 2 parts) = 13 = Φ₃."""
        assert _partitions_k_parts(ALBERT, LAM) == PHI3

    def test_p_f_lam_is_k(self):
        """p(24, 2 parts) = 12 = k."""
        assert _partitions_k_parts(F, LAM) == K

    def test_p_theta_q_is_dimO(self):
        """p(10, 3 parts) = 8 = dimO."""
        assert _partitions_k_parts(THETA, Q) == DIMO

    def test_p_dimO_q_is_N(self):
        """p(8, 3 parts) = 5 = N."""
        assert _partitions_k_parts(DIMO, Q) == N


# ═══════════════════════════════════════════════════════════════
# T420 — Wilson Prime Pair
# ═══════════════════════════════════════════════════════════════

class TestWilsonPrimePair:
    """T420: N=5 and Φ₃=13 are both Wilson primes.

    Wilson prime: (p-1)! + 1 ≡ 0 (mod p²).
    Only three known: 5, 13, 563.
    The first two are SRG values!
    """

    def test_5_is_wilson_prime(self):
        """(5-1)! + 1 = 25 = 5² ≡ 0 (mod 25)."""
        assert (math.factorial(N - 1) + 1) % (N ** 2) == 0

    def test_13_is_wilson_prime(self):
        """(13-1)! + 1 ≡ 0 (mod 169)."""
        assert (math.factorial(PHI3 - 1) + 1) % (PHI3 ** 2) == 0

    def test_first_two_known(self):
        """5 and 13 are the first two Wilson primes (third is 563)."""
        wilson_primes = []
        for p in range(2, 100):
            if all(p % d != 0 for d in range(2, int(p ** 0.5) + 1)):
                if (math.factorial(p - 1) + 1) % (p ** 2) == 0:
                    wilson_primes.append(p)
        assert wilson_primes == [N, PHI3]

    def test_wilson_quotient_5(self):
        """Wilson quotient W(5) = (4!+1)/5 = 5 = N itself!"""
        wq = (math.factorial(N - 1) + 1) // N
        assert wq == N

    def test_both_srg_primes(self):
        """Both Wilson primes are SRG-associated primes."""
        assert N in VALS
        assert PHI3 in VALS


# ═══════════════════════════════════════════════════════════════
# T421 — Base-3 Digit Sum Map
# ═══════════════════════════════════════════════════════════════

class TestBase3DigitSum:
    """T421: Digit sum in base q=3 maps SRG values to SRG values.

    S₃(E)=dimO, S₃(v)=μ, S₃(f)=μ, S₃(g)=q, S₃(θ)=λ, S₃(k)=λ.
    """

    def test_S3_E_is_dimO(self):
        """S₃(240) = 2+2+2+2+0 = 8 = dimO."""
        assert _digit_sum_base(E, Q) == DIMO

    def test_S3_v_is_mu(self):
        """S₃(40) = 1+1+1+1 = 4 = μ."""
        assert _digit_sum_base(V, Q) == MU

    def test_S3_f_is_mu(self):
        """S₃(24) = 2+2+0 = 4 = μ."""
        assert _digit_sum_base(F, Q) == MU

    def test_S3_g_is_q(self):
        """S₃(15) = 1+2+0 = 3 = q."""
        assert _digit_sum_base(G, Q) == Q

    def test_S3_theta_is_lam(self):
        """S₃(10) = 1+0+1 = 2 = λ."""
        assert _digit_sum_base(THETA, Q) == LAM


# ═══════════════════════════════════════════════════════════════
# T422 — Power Sum & Magic Constants
# ═══════════════════════════════════════════════════════════════

class TestPowerSumMagic:
    """T422: λ² + q² = Φ₃; magic constant M(n).

    λ² + q² = 4 + 9 = 13 = Φ₃
    M(λ) = M(2) = 5 = N
    M(q) = M(3) = 15 = g
    """

    def test_power_sum_is_phi3(self):
        """λ² + q² = 4 + 9 = 13 = Φ₃."""
        assert LAM ** 2 + Q ** 2 == PHI3

    def test_magic_lam_is_N(self):
        """Magic constant M(2) = 2·5/2 = 5 = N."""
        assert _magic_constant(LAM) == N

    def test_magic_q_is_g(self):
        """Magic constant M(3) = 3·10/2 = 15 = g."""
        assert _magic_constant(Q) == G

    def test_magic_formula(self):
        """M(n) = n(n²+1)/2 at SRG values."""
        assert _magic_constant(LAM) == LAM * (LAM ** 2 + 1) // 2
        assert _magic_constant(Q) == Q * (Q ** 2 + 1) // 2

    def test_power_sum_factors(self):
        """Φ₃ = λ² + q² = 13 is prime."""
        assert all(PHI3 % d != 0 for d in range(2, int(PHI3 ** 0.5) + 1))


# ═══════════════════════════════════════════════════════════════
# T423 — Stirling 2nd Kind at μ
# ═══════════════════════════════════════════════════════════════

class TestStirling2ndKindMu:
    """T423: S₂(μ, k) at μ=4 produces SRG values.

    S₂(4,2) = 7 = Φ₆; S₂(4,3) = 6 = δ.
    Extends T167 which covers S₂(N, k).
    """

    def test_s2_mu_2_is_phi6(self):
        """S₂(4,2) = 7 = Φ₆."""
        assert _stirling2(MU, 2) == PHI6

    def test_s2_mu_3_is_delta(self):
        """S₂(4,3) = 6 = δ."""
        assert _stirling2(MU, 3) == DELTA

    def test_s2_mu_spectrum(self):
        """S₂(4,k) for k=1..4 = {1, 7, 6, 1}: Φ₆ and δ appear."""
        spec = [_stirling2(MU, j) for j in range(1, MU + 1)]
        assert spec == [1, PHI6, DELTA, 1]

    def test_s2_mu_sum(self):
        """Σ S₂(4,k) = B(4) = 15 = g."""
        assert sum(_stirling2(MU, j) for j in range(1, MU + 1)) == G

    def test_s2_phi6_plus_delta(self):
        """S₂(4,2) + S₂(4,3) = Φ₆ + δ = 13 = Φ₃."""
        assert PHI6 + DELTA == PHI3


# ═══════════════════════════════════════════════════════════════
# T424 — Arithmetic Progressions in SRG Values
# ═══════════════════════════════════════════════════════════════

class TestArithmeticProgressionsSRG:
    """T424: SRG values contain remarkable APs.

    7-term AP d=1: {2,3,4,5,6,7,8} = {λ,q,μ,N,δ,Φ₆,dimO}
    6-term AP d=λ=2: {2,4,6,8,10,12} = {λ,μ,δ,dimO,θ,k}
    4-term AP d=q=3: {4,7,10,13} = {μ,Φ₆,θ,Φ₃}
    """

    def test_7term_ap_d1(self):
        """SRG values contain 7 consecutive integers 2..8."""
        ap = list(range(LAM, DIMO + 1))
        assert len(ap) == 7
        assert all(x in VALS for x in ap)

    def test_6term_ap_d_lam(self):
        """AP with d=λ=2: {2,4,6,8,10,12} ⊂ VALS."""
        ap = list(range(LAM, K + 1, LAM))
        assert len(ap) == 6
        assert all(x in VALS for x in ap)

    def test_4term_ap_d_q(self):
        """AP with d=q=3: {4,7,10,13} ⊂ VALS."""
        ap = [MU + Q * i for i in range(4)]
        assert ap == [MU, PHI6, THETA, PHI3]
        assert all(x in VALS for x in ap)

    def test_ap_d_q_values(self):
        """The 4-term AP d=q covers {μ, Φ₆, θ, Φ₃}."""
        assert MU + Q == PHI6
        assert PHI6 + Q == THETA
        assert THETA + Q == PHI3

    def test_ap_count(self):
        """At least 3 APs of length ≥ 4 exist in SRG values."""
        count = 0
        vals_sorted = sorted(v for v in VALS if v > 0)
        vs = set(vals_sorted)
        for i in range(len(vals_sorted)):
            for j in range(i + 1, len(vals_sorted)):
                d = vals_sorted[j] - vals_sorted[i]
                length = 2
                nxt = vals_sorted[j] + d
                while nxt in vs:
                    length += 1
                    nxt += d
                if length >= 4:
                    count += 1
        assert count >= 3


# ═══════════════════════════════════════════════════════════════
# T425 — Cubic Residue Counts
# ═══════════════════════════════════════════════════════════════

class TestCubicResidueCounts:
    """T425: #CR(p) = number of distinct cubic residues mod p.

    #CR(Φ₃=13) = 4 = μ
    #CR(Φ₆=7) = 2 = λ
    #CR(N=5) = 4 = μ
    """

    def test_cr_phi3_is_mu(self):
        """#CR(mod 13) = 4 = μ."""
        cr = len({pow(a, 3, PHI3) for a in range(1, PHI3)})
        assert cr == MU

    def test_cr_phi6_is_lam(self):
        """#CR(mod 7) = 2 = λ."""
        cr = len({pow(a, 3, PHI6) for a in range(1, PHI6)})
        assert cr == LAM

    def test_cr_N_is_mu(self):
        """#CR(mod 5) = 4 = μ."""
        cr = len({pow(a, 3, N) for a in range(1, N)})
        assert cr == MU

    def test_cr_q_is_lam(self):
        """#CR(mod 3) = 2 = λ — trivially, {1,2} mod 3."""
        cr = len({pow(a, 3, Q) for a in range(1, Q)})
        assert cr == LAM

    def test_cr_formula(self):
        """For prime p, #CR(p) = (p-1)/gcd(3,p-1) + 1 ... actually #nonzero CR.
        For p≡1(mod 3): #CR = (p-1)/3. For p≡2(mod 3): #CR = p-1."""
        # Φ₃=13: 13≡1(mod 3), so #CR = (13-1)/3 = 4 = μ ✓
        assert (PHI3 - 1) // math.gcd(3, PHI3 - 1) == MU
        # Φ₆=7: 7≡1(mod 3), so #CR = (7-1)/3 = 2 = λ ✓
        assert (PHI6 - 1) // math.gcd(3, PHI6 - 1) == LAM
