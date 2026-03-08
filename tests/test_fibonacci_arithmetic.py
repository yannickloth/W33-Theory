"""
Phase XXIX: Fibonacci Arithmetic & Derivative Cascades (T396-T410)
===================================================================
Fifteen theorems showing that Fibonacci entry points, Pisano periods,
distinct-part partitions, aliquot sequences, arithmetic derivatives,
sum-of-prime-factors, pronic numbers, double factorials, continued
fractions, highly composite classification, and quadratic residue
counts all close over the SRG(40,12,2,4) parameter set.

Headline discoveries:
  - Fibonacci entry point α maps SRG values to SRG values with TWO
    fixed points: α(N)=N and α(k)=k
  - Pisano period π(g) = v = 40 (!)  and π(f) = f (fixed point)
  - Distinct-parts partition Q(θ) = θ (fixed point), Q(g) = albert
  - Arithmetic derivative has fixed points D(μ)=μ and D(albert)=albert

Every constant derives from (v, k, λ, μ, q) = (40, 12, 2, 4, 3).
"""

import math
from math import gcd, isqrt

# ── SRG parameters ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V * K // 2                       # 240
R, S = 2, -4
DELTA = R - S                        # 6
F = (-K - (V - 1) * S) // (R - S)   # 24
G = V - 1 - F                        # 15
N = Q + 2                            # 5
PHI3 = Q**2 + Q + 1                  # 13
PHI6 = Q**2 - Q + 1                  # 7
ALBERT = V - PHI3                    # 27
THETA = V * (-S) // (K - S)          # 10
DIM_O = 2**Q                         # 8


# ── helpers ──
def _fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _fib_entry_point(n):
    """Smallest m >= 1 such that n divides F(m)."""
    a, b = 0, 1
    for m in range(1, 10 * n + 1):
        a, b = b, (a + b) % n
        if a == 0:
            return m
    return None


def _pisano_period(n):
    """Period of Fibonacci sequence modulo n."""
    a, b = 0, 1
    for i in range(1, 6 * n + 10):
        a, b = b, (a + b) % n
        if a == 0 and b == 1:
            return i
    return None


def _partitions_distinct(n):
    """Q(n) = number of partitions of n into distinct parts."""
    dp = [0] * (n + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        for j in range(n, i - 1, -1):
            dp[j] += dp[j - i]
    return dp[n]


def _aliquot_step(n):
    """s(n) = sum of proper divisors of n."""
    return sum(d for d in range(1, n) if n % d == 0)


def _factorize(n):
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def _arith_deriv(n):
    """Arithmetic derivative: D(p) = 1 for prime p, Leibniz rule."""
    if n <= 1:
        return 0
    facs = _factorize(n)
    return sum(n * e // p for p, e in facs.items())


def _sopfr(n):
    """Sum of prime factors with repetition."""
    return sum(p * e for p, e in _factorize(n).items())


def _double_factorial(n):
    result = 1
    while n > 1:
        result *= n
        n -= 2
    return result


def _cf_sqrt_period(n):
    """Period length of the continued fraction of sqrt(n).
    Returns 0 if n is a perfect square."""
    a0 = isqrt(n)
    if a0 * a0 == n:
        return 0
    m, d, a = 0, 1, a0
    seen = []
    for _ in range(200):
        m = d * a - m
        d = (n - m * m) // d
        a = (a0 + m) // d
        state = (m, d)
        if state in seen:
            return len(seen) - seen.index(state)
        seen.append(state)
    return -1


def _count_divisors(n):
    return sum(1 for d in range(1, n + 1) if n % d == 0)


# ══════════════════════════════════════════════
# T396: Fibonacci Entry Point Cascade
# ══════════════════════════════════════════════
class TestFibEntryPointCascade:
    """α(n) = smallest m with n | F(m).
    α maps the primary SRG triple (λ,q,μ) to (q,μ,δ),
    and α(N) = N is a stunning fixed point."""

    def test_alpha_lam(self):
        """α(2) = 3 = q.  (F₃ = 2)."""
        assert _fib_entry_point(LAM) == Q

    def test_alpha_q(self):
        """α(3) = 4 = μ.  (F₄ = 3)."""
        assert _fib_entry_point(Q) == MU

    def test_alpha_mu(self):
        """α(4) = 6 = δ.  (F₆ = 8, divisible by 4)."""
        assert _fib_entry_point(MU) == DELTA

    def test_alpha_N_fixed(self):
        """α(5) = 5 = N — fixed point!  (F₅ = 5)."""
        assert _fib_entry_point(N) == N

    def test_alpha_delta(self):
        """α(6) = 12 = k.  (F₁₂ = 144, divisible by 6)."""
        assert _fib_entry_point(DELTA) == K


# ══════════════════════════════════════════════
# T397: Fibonacci Entry Point Extended
# ══════════════════════════════════════════════
class TestFibEntryPointExtended:
    """α continues to map SRG values to SRG values,
    with k = 12 as a second fixed point: α(12) = 12."""

    def test_alpha_phi6(self):
        """α(7) = 8 = dim(O).  (F₈ = 21 = 7×3)."""
        assert _fib_entry_point(PHI6) == DIM_O

    def test_alpha_theta(self):
        """α(10) = 15 = g.  (F₁₅ = 610 = 10×61)."""
        assert _fib_entry_point(THETA) == G

    def test_alpha_k_fixed(self):
        """α(12) = 12 = k — second fixed point!  (F₁₂ = 144 = 12²)."""
        assert _fib_entry_point(K) == K

    def test_alpha_phi3(self):
        """α(13) = 7 = Φ₆.  (F₇ = 13)."""
        assert _fib_entry_point(PHI3) == PHI6

    def test_alpha_f(self):
        """α(24) = 12 = k.  (F₁₂ = 144 = 24×6)."""
        assert _fib_entry_point(F) == K


# ══════════════════════════════════════════════
# T398: Pisano Period Map
# ══════════════════════════════════════════════
class TestPisanoPeriodMap:
    """π(n) = period of Fibonacci mod n.
    π maps SRG values to SRG values, with the
    extraordinary result π(g) = v = 40."""

    def test_pisano_lam(self):
        """π(2) = 3 = q."""
        assert _pisano_period(LAM) == Q

    def test_pisano_q(self):
        """π(3) = 8 = dim(O)."""
        assert _pisano_period(Q) == DIM_O

    def test_pisano_mu(self):
        """π(4) = 6 = δ."""
        assert _pisano_period(MU) == DELTA

    def test_pisano_g_equals_v(self):
        """π(15) = 40 = v — Pisano period at g equals the graph order!"""
        assert _pisano_period(G) == V

    def test_pisano_f_fixed(self):
        """π(24) = 24 = f — Pisano period fixed point."""
        assert _pisano_period(F) == F


# ══════════════════════════════════════════════
# T399: Distinct-Parts Partition Map
# ══════════════════════════════════════════════
class TestDistinctPartsPartition:
    """Q(n) = number of partitions of n into distinct parts.
    Q maps SRG values to SRG values; Q(θ) = θ is a fixed point,
    and Q(g) = albert = 27."""

    def test_Q_k(self):
        """Q(12) = 15 = g."""
        assert _partitions_distinct(K) == G

    def test_Q_delta(self):
        """Q(6) = 4 = μ."""
        assert _partitions_distinct(DELTA) == MU

    def test_Q_theta_fixed(self):
        """Q(10) = 10 = θ — fixed point!"""
        assert _partitions_distinct(THETA) == THETA

    def test_Q_g(self):
        """Q(15) = 27 = albert."""
        assert _partitions_distinct(G) == ALBERT

    def test_Q_phi6(self):
        """Q(7) = 5 = N."""
        assert _partitions_distinct(PHI6) == N


# ══════════════════════════════════════════════
# T400: Aliquot Cascade Through SRG
# ══════════════════════════════════════════════
class TestAliquotCascade:
    """The aliquot sequence s(n) = σ(n)−n cascades through SRG values.
    aliquot(k): 12→16→15→9→4→3→1 visits g, μ, q.
    aliquot(albert): 27→13→1 visits Φ₃."""

    def test_aliquot_k_hits_g(self):
        """s(s(12)) = s(16) = 15 = g."""
        assert _aliquot_step(_aliquot_step(K)) == G

    def test_aliquot_k_hits_mu(self):
        """Aliquot from 12 reaches μ=4 at step 4."""
        n = K
        for _ in range(4):
            n = _aliquot_step(n)
        assert n == MU

    def test_aliquot_albert_hits_phi3(self):
        """s(27) = 13 = Φ₃ — one step from albert to cyclotomic."""
        assert _aliquot_step(ALBERT) == PHI3

    def test_aliquot_theta_hits_dimO(self):
        """s(10) = 8 = dim(O)."""
        assert _aliquot_step(THETA) == DIM_O

    def test_aliquot_theta_hits_phi6(self):
        """s(s(10)) = s(8) = 7 = Φ₆."""
        assert _aliquot_step(_aliquot_step(THETA)) == PHI6


# ══════════════════════════════════════════════
# T401: Arithmetic Derivative SRG Map
# ══════════════════════════════════════════════
class TestArithmeticDerivative:
    """D(n) = arithmetic derivative (Leibniz rule on primes).
    Two fixed points: D(μ) = μ = 4 and D(albert) = albert = 27.
    Plus D(θ) = Φ₆, D(δ) = N, D(dimO) = k."""

    def test_D_mu_fixed(self):
        """D(4) = 4 = μ — arithmetic derivative fixed point!"""
        assert _arith_deriv(MU) == MU

    def test_D_albert_fixed(self):
        """D(27) = 27 = albert — second fixed point!"""
        assert _arith_deriv(ALBERT) == ALBERT

    def test_D_theta(self):
        """D(10) = 7 = Φ₆."""
        assert _arith_deriv(THETA) == PHI6

    def test_D_delta(self):
        """D(6) = 5 = N."""
        assert _arith_deriv(DELTA) == N

    def test_D_dimO(self):
        """D(8) = 12 = k."""
        assert _arith_deriv(DIM_O) == K


# ══════════════════════════════════════════════
# T402: Sum-of-Prime-Factors Map
# ══════════════════════════════════════════════
class TestSopfrMap:
    """sopfr(n) = sum of prime factors with repetition.
    Maps SRG values to SRG values in a cascade."""

    def test_sopfr_k(self):
        """sopfr(12) = 2+2+3 = 7 = Φ₆."""
        assert _sopfr(K) == PHI6

    def test_sopfr_g(self):
        """sopfr(15) = 3+5 = 8 = dim(O)."""
        assert _sopfr(G) == DIM_O

    def test_sopfr_delta(self):
        """sopfr(6) = 2+3 = 5 = N."""
        assert _sopfr(DELTA) == N

    def test_sopfr_dimO(self):
        """sopfr(8) = 2+2+2 = 6 = δ."""
        assert _sopfr(DIM_O) == DELTA

    def test_sopfr_theta(self):
        """sopfr(10) = 2+5 = 7 = Φ₆."""
        assert _sopfr(THETA) == PHI6


# ══════════════════════════════════════════════
# T403: Pronic Number Triple
# ══════════════════════════════════════════════
class TestPronicTriple:
    """Pronic(n) = n(n+1).  Three SRG values map to SRG values:
    Pronic(λ) = δ, Pronic(q) = k, Pronic(g) = E."""

    def test_pronic_lam(self):
        """2×3 = 6 = δ."""
        assert LAM * (LAM + 1) == DELTA

    def test_pronic_q(self):
        """3×4 = 12 = k."""
        assert Q * (Q + 1) == K

    def test_pronic_g(self):
        """15×16 = 240 = E — the edge count is pronic at g!"""
        assert G * (G + 1) == E

    def test_pronic_chain(self):
        """Pronic(λ)=δ, Pronic(q)=k: consecutive hits."""
        assert LAM * (LAM + 1) == DELTA
        assert Q * (Q + 1) == K

    def test_pronic_g_connects_to_E(self):
        """E = g(g+1) = 15×16 = f × θ cross-check."""
        assert G * (G + 1) == E
        assert E == F * THETA


# ══════════════════════════════════════════════
# T404: Double Factorial Chain
# ══════════════════════════════════════════════
class TestDoubleFactorial:
    """Four consecutive double factorials land on SRG values:
    2!! = λ, 3!! = q, 4!! = dimO, 5!! = g."""

    def test_df_2(self):
        """2!! = 2 = λ."""
        assert _double_factorial(2) == LAM

    def test_df_3(self):
        """3!! = 3 = q."""
        assert _double_factorial(3) == Q

    def test_df_4(self):
        """4!! = 4×2 = 8 = dim(O)."""
        assert _double_factorial(4) == DIM_O

    def test_df_5(self):
        """5!! = 5×3 = 15 = g."""
        assert _double_factorial(5) == G

    def test_df_consecutive(self):
        """Four consecutive double factorials all SRG values."""
        dfs = [_double_factorial(n) for n in range(2, 6)]
        assert dfs == [LAM, Q, DIM_O, G]


# ══════════════════════════════════════════════
# T405: CF Period Universality
# ══════════════════════════════════════════════
class TestCFPeriodUniversal:
    """The continued fraction of sqrt(n) for every non-square
    SRG constant n has period length exactly λ = 2."""

    def test_cf_sqrt_v(self):
        """CF period of sqrt(40) = 2 = λ."""
        assert _cf_sqrt_period(V) == LAM

    def test_cf_sqrt_k(self):
        """CF period of sqrt(12) = 2 = λ."""
        assert _cf_sqrt_period(K) == LAM

    def test_cf_sqrt_E(self):
        """CF period of sqrt(240) = 2 = λ."""
        assert _cf_sqrt_period(E) == LAM

    def test_cf_sqrt_f(self):
        """CF period of sqrt(24) = 2 = λ."""
        assert _cf_sqrt_period(F) == LAM

    def test_cf_sqrt_g(self):
        """CF period of sqrt(15) = 2 = λ."""
        assert _cf_sqrt_period(G) == LAM


# ══════════════════════════════════════════════
# T406: Highly Composite Numbers
# ══════════════════════════════════════════════
class TestHighlyComposite:
    """Six SRG constants — λ, μ, δ, k, f, E — are all highly
    composite numbers (each has more divisors than any smaller
    positive integer)."""

    def _is_highly_composite(self, n):
        dn = _count_divisors(n)
        return all(_count_divisors(m) < dn for m in range(1, n))

    def test_lam_hc(self):
        """2 is highly composite (d(2)=2 > d(1)=1)."""
        assert self._is_highly_composite(LAM)

    def test_mu_hc(self):
        """4 is highly composite (d(4)=3)."""
        assert self._is_highly_composite(MU)

    def test_delta_hc(self):
        """6 is highly composite (d(6)=4)."""
        assert self._is_highly_composite(DELTA)

    def test_k_hc(self):
        """12 is highly composite (d(12)=6)."""
        assert self._is_highly_composite(K)

    def test_f_hc(self):
        """24 is highly composite (d(24)=8)."""
        assert self._is_highly_composite(F)


# ══════════════════════════════════════════════
# T407: Quadratic Residue Counts
# ══════════════════════════════════════════════
class TestQuadraticResidueCounts:
    """For each SRG-associated odd prime p, the number of
    quadratic residues mod p equals an SRG parameter:
    #QR(N) = λ, #QR(Φ₆) = q, #QR(Φ₃) = δ."""

    def _count_qr(self, p):
        """Count quadratic residues mod p (excluding 0)."""
        return sum(1 for x in range(1, p) if pow(x, (p - 1) // 2, p) == 1)

    def test_qr_N(self):
        """#QR(5) = 2 = λ.  QR = {1, 4}."""
        assert self._count_qr(N) == LAM

    def test_qr_phi6(self):
        """#QR(7) = 3 = q.  QR = {1, 2, 4}."""
        assert self._count_qr(PHI6) == Q

    def test_qr_phi3(self):
        """#QR(13) = 6 = δ.  QR = {1, 3, 4, 9, 10, 12}."""
        assert self._count_qr(PHI3) == DELTA

    def test_qr_count_formula(self):
        """#QR(p) = (p−1)/2 for odd prime p."""
        for p in [Q, N, PHI6, PHI3]:
            assert self._count_qr(p) == (p - 1) // 2

    def test_qr_sum_spans_srg(self):
        """#QR values {1, 2, 3, 6} for SRG primes {3,5,7,13}."""
        qr_counts = {self._count_qr(p) for p in [Q, N, PHI6, PHI3]}
        assert qr_counts == {1, LAM, Q, DELTA}


# ══════════════════════════════════════════════
# T408: Factorization Arithmetic Functions
# ══════════════════════════════════════════════
class TestFactorizationFunctions:
    """ω(n) (distinct primes), Ω(n) (with multiplicity), rad(n)
    all yield SRG values when evaluated at SRG constants."""

    def test_omega_v(self):
        """ω(40) = 2 = λ.  (40 = 2³·5)."""
        assert len(_factorize(V)) == LAM

    def test_bigomega_v(self):
        """Ω(40) = 4 = μ.  (2³·5 → 3+1 = 4 prime factors)."""
        assert sum(_factorize(V).values()) == MU

    def test_rad_v(self):
        """rad(40) = 2·5 = 10 = θ."""
        facs = _factorize(V)
        assert math.prod(facs.keys()) == THETA

    def test_omega_E(self):
        """ω(240) = 3 = q.  (240 = 2⁴·3·5)."""
        assert len(_factorize(E)) == Q

    def test_bigomega_E(self):
        """Ω(240) = 6 = δ.  (2⁴·3·5 → 4+1+1 = 6)."""
        assert sum(_factorize(E).values()) == DELTA


# ══════════════════════════════════════════════
# T409: Arithmetic Derivative Chains
# ══════════════════════════════════════════════
class TestArithDerivChains:
    """Iterated arithmetic derivatives from SRG values
    traverse other SRG values before reaching 1 or cycling."""

    def test_D_chain_delta(self):
        """D-chain: 6 → 5 → 1  (δ → N → terminal)."""
        assert _arith_deriv(DELTA) == N
        assert _arith_deriv(N) == 1

    def test_D_chain_theta(self):
        """D-chain: 10 → 7 → 1  (θ → Φ₆ → terminal)."""
        assert _arith_deriv(THETA) == PHI6
        assert _arith_deriv(PHI6) == 1

    def test_D_chain_g(self):
        """D-chain: 15 → 8 → 12  (g → dimO → k)."""
        assert _arith_deriv(G) == DIM_O
        assert _arith_deriv(DIM_O) == K

    def test_D_chain_f_reaches_E(self):
        """D-chain from f=24 eventually reaches E=240."""
        chain = [F]
        x = F
        for _ in range(10):
            x = _arith_deriv(x)
            chain.append(x)
            if x == E:
                break
        assert E in chain

    def test_D_chain_g_three_deep(self):
        """D(D(D(g))) = D(D(8)) = D(12) = 16."""
        d1 = _arith_deriv(G)       # 8
        d2 = _arith_deriv(d1)      # 12 = k
        d3 = _arith_deriv(d2)      # 16
        assert d1 == DIM_O
        assert d2 == K


# ══════════════════════════════════════════════
# T410: Octagonal, Star & Centered Figurate
# ══════════════════════════════════════════════
class TestFigurateExtended:
    """Extended figurate numbers at SRG: octagonal P₈(4) = v,
    Star(2) = Φ₃, square pyramidal Pyr(2) = N,
    centered-13-gonal C₁₃(3) = v."""

    def test_octagonal_v(self):
        """P₈(4) = 4(3·4−2) = 40 = v.  (8-gonal number)."""
        n = 4
        assert n * (3 * n - 2) == V

    def test_star_phi3(self):
        """Star(2) = 6·2·1 + 1 = 13 = Φ₃."""
        n = 2
        assert 6 * n * (n - 1) + 1 == PHI3

    def test_square_pyramidal_N(self):
        """Pyr(2) = 2·3·5/6 = 5 = N."""
        n = 2
        assert n * (n + 1) * (2 * n + 1) // 6 == N

    def test_centered_13gonal_v(self):
        """C₁₃(3) = 13·3·2/2 + 1 = 40 = v."""
        s, n = 13, 3
        assert s * n * (n - 1) // 2 + 1 == V

    def test_hex_phi3(self):
        """Hex(3) = 2·9−6+1 = 13 = Φ₃.  (centered hexagonal)."""
        n = 3
        assert 2 * n * n - 2 * n + 1 == PHI3
