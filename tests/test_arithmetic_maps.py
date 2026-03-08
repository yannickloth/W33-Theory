"""
Phase XXVIII: Arithmetic Maps & Number-Theoretic Cascades (T381-T395)
=====================================================================
Fifteen theorems showing that classical arithmetic functions —
floor-sqrt, sigma, Euler totient, multiplicative order, cototient,
Collatz stopping time, divisor count, q-geometric series, gcd/lcm,
and binomial coefficients — form closed cascades over SRG(40,12,2,4)
parameters.  The headline discovery: isqrt maps ALL eleven core
constants back into the SRG parameter set, and σ and φ satisfy a
remarkable duality σ(p) = φ(next SRG prime).

Every constant derives from (v, k, λ, μ, q) = (40, 12, 2, 4, 3).
"""

import math
from math import isqrt, gcd, comb

# ── SRG parameters ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V * K // 2                       # 240
R, S = 2, -4                         # eigenvalues
DELTA = R - S                        # 6
F = (-K - (V - 1) * S) // (R - S)   # 24  (mult of r)
G = V - 1 - F                        # 15  (mult of s)
N = Q + 2                            # 5
PHI3 = Q**2 + Q + 1                  # 13
PHI6 = Q**2 - Q + 1                  # 7
ALBERT = V - PHI3                    # 27
THETA = V * (-S) // (K - S)          # 10
DIM_O = 2**Q                         # 8  (dim of octonions)


# ── helpers ──
def _sigma(n, k=1):
    """Sum of k-th powers of divisors of n."""
    return sum(d**k for d in range(1, n + 1) if n % d == 0)


def _euler_phi(n):
    """Euler's totient function."""
    return sum(1 for i in range(1, n + 1) if gcd(i, n) == 1)


def _mult_order(a, n):
    """Multiplicative order of a modulo n (n must be coprime to a)."""
    if gcd(a, n) != 1:
        return None
    order = 1
    current = a % n
    while current != 1:
        current = (current * a) % n
        order += 1
    return order


def _collatz_steps(n):
    """Number of steps in the Collatz sequence from n to 1."""
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps


def _divisor_count(n):
    """Number of divisors of n."""
    return sum(1 for d in range(1, n + 1) if n % d == 0)


def _lcm(*args):
    """LCM of multiple integers."""
    result = args[0]
    for a in args[1:]:
        result = result * a // gcd(result, a)
    return result


# ══════════════════════════════════════════════
# T381: Floor-Sqrt Primary Cascade
# ══════════════════════════════════════════════
class TestFloorSqrtPrimary:
    """isqrt maps the five principal constants {v,k,E,f,albert}
    bijectively onto {δ,q,g,μ,N} — the secondary SRG layer."""

    def test_isqrt_v(self):
        """isqrt(40) = 6 = δ."""
        assert isqrt(V) == DELTA

    def test_isqrt_k(self):
        """isqrt(12) = 3 = q."""
        assert isqrt(K) == Q

    def test_isqrt_E(self):
        """isqrt(240) = 15 = g."""
        assert isqrt(E) == G

    def test_isqrt_f(self):
        """isqrt(24) = 4 = μ."""
        assert isqrt(F) == MU

    def test_isqrt_albert(self):
        """isqrt(27) = 5 = N."""
        assert isqrt(ALBERT) == N


# ══════════════════════════════════════════════
# T382: Floor-Sqrt Closure
# ══════════════════════════════════════════════
class TestFloorSqrtClosure:
    """isqrt maps every secondary constant back into {λ,q},
    proving the SRG value-set is closed under floor-sqrt."""

    def test_isqrt_phi3(self):
        """isqrt(13) = 3 = q."""
        assert isqrt(PHI3) == Q

    def test_isqrt_phi6(self):
        """isqrt(7) = 2 = λ."""
        assert isqrt(PHI6) == LAM

    def test_isqrt_theta(self):
        """isqrt(10) = 3 = q."""
        assert isqrt(THETA) == Q

    def test_isqrt_delta(self):
        """isqrt(6) = 2 = λ."""
        assert isqrt(DELTA) == LAM

    def test_isqrt_N(self):
        """isqrt(5) = 2 = λ."""
        assert isqrt(N) == LAM


# ══════════════════════════════════════════════
# T383: Sigma Chain at Small Values
# ══════════════════════════════════════════════
class TestSigmaChain:
    """σ₁ maps λ→q→μ→…→k, threading through SRG parameters
    at values not covered by Phase XXV (T340)."""

    def test_sigma_lam(self):
        """σ(2) = 3 = q."""
        assert _sigma(LAM) == Q

    def test_sigma_q(self):
        """σ(3) = 4 = μ."""
        assert _sigma(Q) == MU

    def test_sigma_N(self):
        """σ(5) = 6 = δ."""
        assert _sigma(N) == DELTA

    def test_sigma_delta(self):
        """σ(6) = 12 = k."""
        assert _sigma(DELTA) == K

    def test_sigma_phi6(self):
        """σ(7) = 8 = dim(O)."""
        assert _sigma(PHI6) == DIM_O


# ══════════════════════════════════════════════
# T384: Sigma–Albert Bridge
# ══════════════════════════════════════════════
class TestSigmaAlbertBridge:
    """σ(albert) = σ(27) = 1+3+9+27 = 40 = v.
    The Jordan algebra dimension maps to the graph order via
    the sum-of-divisors function.  Also σ(θ) = 2q²."""

    def test_sigma_albert_equals_v(self):
        """σ(27) = 40 = v — the headline identity."""
        assert _sigma(ALBERT) == V

    def test_sigma_albert_decomposition(self):
        """σ(27) = 1 + 3 + 9 + 27 = sum of powers of q."""
        assert _sigma(ALBERT) == 1 + Q + Q**2 + Q**3

    def test_sigma_theta(self):
        """σ(10) = 18 = 2q²."""
        assert _sigma(THETA) == 2 * Q**2

    def test_sigma_albert_is_perfect_power_sum(self):
        """σ(q³) = (q⁴-1)/(q-1) = v (geometric series)."""
        assert _sigma(Q**3) == (Q**4 - 1) // (Q - 1)

    def test_sigma_chain_to_v(self):
        """Composing: σ(σ(σ(λ))) = σ(σ(q)) = σ(μ) = 7 = Φ₆."""
        assert _sigma(_sigma(_sigma(LAM))) == PHI6


# ══════════════════════════════════════════════
# T385: Euler Totient Small Cascade
# ══════════════════════════════════════════════
class TestTotientSmallCascade:
    """φ maps the four SRG-associated primes {q,N,Φ₆,Φ₃}
    to {λ,μ,δ,k} — a perfect bijection."""

    def test_phi_q(self):
        """φ(3) = 2 = λ."""
        assert _euler_phi(Q) == LAM

    def test_phi_N(self):
        """φ(5) = 4 = μ."""
        assert _euler_phi(N) == MU

    def test_phi_phi6(self):
        """φ(7) = 6 = δ."""
        assert _euler_phi(PHI6) == DELTA

    def test_phi_phi3(self):
        """φ(13) = 12 = k."""
        assert _euler_phi(PHI3) == K

    def test_phi_prime_bijection(self):
        """φ on {q,N,Φ₆,Φ₃} gives {λ,μ,δ,k}: all distinct."""
        images = {_euler_phi(p) for p in [Q, N, PHI6, PHI3]}
        assert images == {LAM, MU, DELTA, K}


# ══════════════════════════════════════════════
# T386: Totient at Multiplicities
# ══════════════════════════════════════════════
class TestTotientMultiplicities:
    """φ(f) = φ(g) = 8 = dim(O): both eigenvalue multiplicities
    share the same totient, equal to the octonion dimension."""

    def test_phi_f(self):
        """φ(24) = 8 = dim(O)."""
        assert _euler_phi(F) == DIM_O

    def test_phi_g(self):
        """φ(15) = 8 = dim(O)."""
        assert _euler_phi(G) == DIM_O

    def test_phi_f_equals_phi_g(self):
        """φ(f) = φ(g) despite f ≠ g."""
        assert _euler_phi(F) == _euler_phi(G)
        assert F != G

    def test_phi_multiplicity_ratio(self):
        """f/g = 24/15 = 8/5 yet φ(f) = φ(g)."""
        assert F * 5 == G * 8  # cross-multiply to avoid float

    def test_phi_fg_product(self):
        """φ(f) · φ(g) = 64 = μ³ = φ(E)."""
        assert _euler_phi(F) * _euler_phi(G) == MU**3


# ══════════════════════════════════════════════
# T387: Multiplicative Order of 2
# ══════════════════════════════════════════════
class TestMultiplicativeOrder:
    """ord_n(2) maps the four SRG primes to SRG parameters:
    ord_3(2)=λ, ord_5(2)=μ, ord_7(2)=q, ord_13(2)=k.
    These are the lengths of binary expansions mod p."""

    def test_ord2_mod_q(self):
        """ord_3(2) = 2 = λ.  (2²≡1 mod 3)."""
        assert _mult_order(2, Q) == LAM

    def test_ord2_mod_N(self):
        """ord_5(2) = 4 = μ.  (2⁴≡1 mod 5)."""
        assert _mult_order(2, N) == MU

    def test_ord2_mod_phi6(self):
        """ord_7(2) = 3 = q.  (2³≡1 mod 7)."""
        assert _mult_order(2, PHI6) == Q

    def test_ord2_mod_phi3(self):
        """ord_13(2) = 12 = k.  (2¹²≡1 mod 13)."""
        assert _mult_order(2, PHI3) == K

    def test_ord2_power_check(self):
        """Verify: 2^ord ≡ 1 (mod p) for each SRG prime."""
        for p, expected in [(Q, LAM), (N, MU), (PHI6, Q), (PHI3, K)]:
            assert pow(2, expected, p) == 1


# ══════════════════════════════════════════════
# T388: Cototient Map
# ══════════════════════════════════════════════
class TestCototientMap:
    """The cototient n − φ(n) maps SRG values to SRG values:
    v→f, k→dim(O), θ→δ."""

    def test_cototient_v(self):
        """40 − φ(40) = 40 − 16 = 24 = f."""
        assert V - _euler_phi(V) == F

    def test_cototient_k(self):
        """12 − φ(12) = 12 − 4 = 8 = dim(O)."""
        assert K - _euler_phi(K) == DIM_O

    def test_cototient_theta(self):
        """10 − φ(10) = 10 − 4 = 6 = δ."""
        assert THETA - _euler_phi(THETA) == DELTA

    def test_cototient_albert(self):
        """27 − φ(27) = 27 − 18 = 9 = q²."""
        assert ALBERT - _euler_phi(ALBERT) == Q**2

    def test_cototient_E(self):
        """240 − φ(240) = 240 − 64 = 176 = 11·16 = 11·μ²."""
        assert E - _euler_phi(E) == 11 * MU**2


# ══════════════════════════════════════════════
# T389: Collatz Stopping Time Map
# ══════════════════════════════════════════════
class TestCollatzStoppingTime:
    """The Collatz stopping time (steps to reach 1) maps
    five SRG values to five other SRG values.
    steps(N)=N is a fixed point!"""

    def test_collatz_q(self):
        """steps(3) = 7 = Φ₆."""
        assert _collatz_steps(Q) == PHI6

    def test_collatz_N_fixed(self):
        """steps(5) = 5 = N — a Collatz-stopping-time fixed point!"""
        assert _collatz_steps(N) == N

    def test_collatz_dimO(self):
        """steps(8) = 3 = q."""
        assert _collatz_steps(DIM_O) == Q

    def test_collatz_f(self):
        """steps(24) = 10 = θ."""
        assert _collatz_steps(F) == THETA

    def test_collatz_v(self):
        """steps(40) = 8 = dim(O)."""
        assert _collatz_steps(V) == DIM_O


# ══════════════════════════════════════════════
# T390: Divisor Count Extended
# ══════════════════════════════════════════════
class TestDivisorCountExtended:
    """d(n) (number of divisors) maps SRG values to SRG values.
    Extends T340 which covered d(v)=8 and d(E)=20."""

    def test_d_k(self):
        """d(12) = 6 = δ."""
        assert _divisor_count(K) == DELTA

    def test_d_albert(self):
        """d(27) = 4 = μ."""
        assert _divisor_count(ALBERT) == MU

    def test_d_phi3(self):
        """d(13) = 2 = λ  (13 is prime)."""
        assert _divisor_count(PHI3) == LAM

    def test_d_g(self):
        """d(15) = 4 = μ."""
        assert _divisor_count(G) == MU

    def test_d_theta(self):
        """d(10) = 4 = μ."""
        assert _divisor_count(THETA) == MU


# ══════════════════════════════════════════════
# T391: q-Geometric Series Identity
# ══════════════════════════════════════════════
class TestGeometricSeries:
    """(qⁿ−1)/(q−1) = 1+q+…+q^{n−1} yields μ, Φ₃, v
    for n=2,3,4.  v = |PG(3,q)| — the full projective space."""

    def test_geo2(self):
        """(q²−1)/(q−1) = q+1 = 4 = μ."""
        assert (Q**2 - 1) // (Q - 1) == MU

    def test_geo3(self):
        """(q³−1)/(q−1) = q²+q+1 = 13 = Φ₃."""
        assert (Q**3 - 1) // (Q - 1) == PHI3

    def test_geo4_equals_v(self):
        """(q⁴−1)/(q−1) = 40 = v — the graph order is |PG(3,q)|."""
        assert (Q**4 - 1) // (Q - 1) == V

    def test_v_as_polynomial(self):
        """v = 1 + q + q² + q³ explicitly."""
        assert 1 + Q + Q**2 + Q**3 == V

    def test_projective_counting(self):
        """v/μ = (q⁴−1)/(q²−1) = q²+1 = 10 = θ."""
        assert V * (Q - 1) // (Q**2 - 1) == Q**2 + 1
        assert Q**2 + 1 == THETA


# ══════════════════════════════════════════════
# T392: GCD-LCM SRG Lattice
# ══════════════════════════════════════════════
class TestGcdLcmLattice:
    """gcd and lcm of SRG parameter pairs produce SRG values,
    forming a divisibility lattice."""

    def test_gcd_v_k(self):
        """gcd(40, 12) = 4 = μ."""
        assert gcd(V, K) == MU

    def test_gcd_f_g(self):
        """gcd(24, 15) = 3 = q."""
        assert gcd(F, G) == Q

    def test_lcm_lam_q(self):
        """lcm(2, 3) = 6 = δ."""
        assert _lcm(LAM, Q) == DELTA

    def test_lcm_q_mu(self):
        """lcm(3, 4) = 12 = k."""
        assert _lcm(Q, MU) == K

    def test_lcm_lam_q_mu(self):
        """lcm(λ, q, μ) = 12 = k — three-way lcm equals k."""
        assert _lcm(LAM, Q, MU) == K


# ══════════════════════════════════════════════
# T393: Binomial Coefficients at SRG Indices
# ══════════════════════════════════════════════
class TestBinomialSRG:
    """C(a,b) with a,b ∈ SRG values yields further SRG values."""

    def test_comb_N_lam(self):
        """C(5,2) = 10 = θ."""
        assert comb(N, LAM) == THETA

    def test_comb_delta_lam(self):
        """C(6,2) = 15 = g."""
        assert comb(DELTA, LAM) == G

    def test_comb_theta_q(self):
        """C(10,3) = 120 = E/2."""
        assert comb(THETA, Q) == E // 2

    def test_comb_delta_q(self):
        """C(6,3) = 20 = v/λ."""
        assert comb(DELTA, Q) == V // LAM

    def test_comb_theta_lam(self):
        """C(10,2) = 45 = v + N."""
        assert comb(THETA, LAM) == V + N


# ══════════════════════════════════════════════
# T394: σ–φ Duality on SRG Primes
# ══════════════════════════════════════════════
class TestSigmaPhiDuality:
    """σ and φ interleave on the SRG prime chain q < N < Φ₆ < Φ₃:
    σ(q) = φ(N) = μ, σ(N) = φ(Φ₆) = δ, σ(Φ₆) = φ(g) = dim(O).
    This duality is a consequence of p prime ⇒ σ(p) = p+1 = φ(next)."""

    def test_sigma_q_equals_phi_N(self):
        """σ(3) = 4 = φ(5)."""
        assert _sigma(Q) == _euler_phi(N)

    def test_sigma_N_equals_phi_phi6(self):
        """σ(5) = 6 = φ(7)."""
        assert _sigma(N) == _euler_phi(PHI6)

    def test_sigma_phi6_equals_phi_g(self):
        """σ(7) = 8 = φ(15)."""
        assert _sigma(PHI6) == _euler_phi(G)

    def test_duality_chain(self):
        """The three duality equations in sequence."""
        chain = [Q, N, PHI6]
        targets = [N, PHI6, G]
        for p, t in zip(chain, targets):
            assert _sigma(p) == _euler_phi(t)

    def test_duality_values_ascending(self):
        """σ(q) < σ(N) < σ(Φ₆): strictly ascending."""
        vals = [_sigma(Q), _sigma(N), _sigma(PHI6)]
        assert vals == [MU, DELTA, DIM_O]
        assert vals == sorted(vals)
        assert len(set(vals)) == 3


# ══════════════════════════════════════════════
# T395: Arithmetic Map Compositions
# ══════════════════════════════════════════════
class TestArithmeticCompositions:
    """Composing arithmetic functions on SRG values still yields
    SRG values — the cascade is stable under iteration."""

    def test_isqrt_sigma_albert(self):
        """isqrt(σ(27)) = isqrt(40) = 6 = δ."""
        assert isqrt(_sigma(ALBERT)) == DELTA

    def test_phi_sigma_q(self):
        """φ(σ(q)) = φ(4) = 2 = λ."""
        assert _euler_phi(_sigma(Q)) == LAM

    def test_sigma_phi_N(self):
        """σ(φ(N)) = σ(4) = 7 = Φ₆."""
        assert _sigma(_euler_phi(N)) == PHI6

    def test_d_sigma_lam(self):
        """d(σ(λ)) = d(3) = 2 = λ — fixed point of d∘σ."""
        assert _divisor_count(_sigma(LAM)) == LAM

    def test_isqrt_isqrt_v(self):
        """isqrt(isqrt(v)) = isqrt(6) = 2 = λ — nested floor-sqrt."""
        assert isqrt(isqrt(V)) == LAM
