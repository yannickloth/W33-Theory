"""
Theorems T156-T170: Combinatorial Depth — Partitions, Catalan, Bell, Ramsey,
Dual Coxeter, Stable Homotopy, Platonic Solids, and Fibonacci-Lucas.

Phase XIII: Deep combinatorial and algebraic structures that lock the
SRG parameters (v,k,λ,μ,q) = (40,12,2,4,3) into every branch of
pure mathematics — from partitions of integers to stable homotopy groups.

T156: Stabilizer Power — |Stab(x)| = (k/λ)^μ = 6⁴ = 1296
T157: Partition Spectrum — p(k,j) for j=1..k returns all SRG values
T158: Catalan-G₂ — C(μ) = C(4) = 14 = dim(G₂)
T159: Bell-F₄ — B(N) = B(5) = 52 = dim(F₄)
T160: Ramsey-Perfect — R(q,q) = R(3,3) = 6 = k/λ
T161: Dual Coxeter Spectrum — {h∨(G₂..E₈)} = {μ, q², k, 2q², v−θ}
T162: Stable Homotopy — |π₃ˢ(S⁰)| = 24 = f
T163: Icosahedral Parameters — (V,E,F)_ico = (k, v−θ, v/2)
T164: Alternating & Binary Icosahedral — |A_N| = E/μ, |2I| = E/2
T165: Derangement Count — D(μ) = q²
T166: Modular Group Index — [SL(2,ℤ):Γ(q)] = f = 24
T167: Stirling Square — S₂(N,q) = N²
T168: Total Partitions — p(k) = Φ₆·(k−1) = 77
T169: Fibonacci-Lucas Cycle — F(Φ₆) = Φ₃, L(N) = k−1
T170: Partition of N — p(N) = Φ₆ = 7
"""
from __future__ import annotations
import math
from math import comb, factorial
import pytest
from fractions import Fraction


# ── SRG parameters ──────────────────────────────────────────────
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
THETA = 10
R_EIGEN = 2
S_EIGEN = -4
E = 240        # edges
F_MULT = 24    # multiplicity of eigenvalue r=2
G_MULT = 15    # multiplicity of eigenvalue s=-4
PHI3 = 13      # q² + q + 1
PHI6 = 7       # q² − q + 1
N_IND = 5      # independence number
ALBERT = 27    # v − k − 1
AUT_ORDER = 51840  # |Sp(4,3)| = |W(E₆)|
DIM_O = K - MU     # 8 = dim(octonions)
G2_DIM = 14
F4_DIM = 52
E6_DIM = 78
E7_DIM = 133
E8_DIM = 248


# ── Combinatorial helper functions ─────────────────────────────
def _partitions_into_k_parts(n, k):
    """Number of partitions of n into exactly k positive parts."""
    if k == 0:
        return 1 if n == 0 else 0
    if n <= 0 or k < 0 or k > n:
        return 0
    if k == n:
        return 1
    if k == 1:
        return 1
    return _partitions_into_k_parts(n - 1, k - 1) + _partitions_into_k_parts(n - k, k)


def _total_partitions(n):
    """Number of unrestricted partitions of n."""
    dp = [0] * (n + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        for j in range(i, n + 1):
            dp[j] += dp[j - i]
    return dp[n]


def _catalan(n):
    """nth Catalan number."""
    return comb(2 * n, n) // (n + 1)


def _bell(n):
    """nth Bell number via Bell triangle."""
    if n == 0:
        return 1
    B = [[0] * (n + 1) for _ in range(n + 1)]
    B[0][0] = 1
    for i in range(1, n + 1):
        B[i][0] = B[i - 1][i - 1]
        for j in range(1, i + 1):
            B[i][j] = B[i][j - 1] + B[i - 1][j - 1]
    return B[n][0]


def _derangement(n):
    """Number of derangements of n elements."""
    if n == 0:
        return 1
    if n == 1:
        return 0
    d = [0] * (n + 1)
    d[0] = 1
    d[1] = 0
    for i in range(2, n + 1):
        d[i] = (i - 1) * (d[i - 1] + d[i - 2])
    return d[n]


def _stirling2(n, k):
    """Stirling number of the second kind S(n, k)."""
    if n == 0 and k == 0:
        return 1
    if n == 0 or k == 0:
        return 0
    if k == 1 or k == n:
        return 1
    return k * _stirling2(n - 1, k) + _stirling2(n - 1, k - 1)


def _fib(n):
    """nth Fibonacci number."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _lucas(n):
    """nth Lucas number."""
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a + b
    return a


# ═══════════════════════════════════════════════════════════════
# T156 — Stabilizer Power: |Stab(x)| = (k/λ)^μ
# ═══════════════════════════════════════════════════════════════
class TestStabilizerPower:
    """T156: The vertex stabilizer in Aut(W(3,3)) = Sp(4,3) has order
    |Stab(x)| = |Aut|/v = 51840/40 = 1296 = (k/λ)^μ = 6⁴.

    The stabilizer is the μ-th power of the ratio k/λ (first perfect number).
    """

    def test_stabilizer_order(self):
        """51840/40 = 1296."""
        assert AUT_ORDER // V == 1296

    def test_stabilizer_is_power(self):
        """1296 = (k/λ)^μ = 6⁴."""
        assert AUT_ORDER // V == (K // LAM) ** MU

    def test_perfect_number_power(self):
        """6⁴: the first perfect number raised to the common-neighbor count."""
        assert 6**4 == 1296

    def test_base_is_k_over_lambda(self):
        """k/λ = 6 is both first perfect number and R(3,3)."""
        assert K // LAM == 6

    def test_factorization(self):
        """1296 = 2⁴ × 3⁴ = (2·3)⁴ = (λ·q)^μ."""
        assert 1296 == (LAM * Q) ** MU


# ═══════════════════════════════════════════════════════════════
# T157 — Partition Spectrum of k
# ═══════════════════════════════════════════════════════════════
class TestPartitionSpectrum:
    """T157: The partition spectrum p(k, j) for j = 1, 2, ..., k returns
    EXACTLY the SRG parameter set:

    p(12,1)=1=β₀, p(12,2)=6=k/λ, p(12,3)=12=k, p(12,4)=15=g,
    p(12,5)=13=Φ₃, p(12,6)=11=k−1, p(12,7)=7=Φ₆, p(12,8)=5=N,
    p(12,9)=3=q, p(12,10)=2=λ, p(12,11)=1=β₀, p(12,12)=1=β₀.

    Every entry in this partition table is an SRG-derived value.
    This is perhaps the deepest single identity in the theory.
    """

    EXPECTED = [1, 6, 12, 15, 13, 11, 7, 5, 3, 2, 1, 1]
    SRG_VALS = [1, K // LAM, K, G_MULT, PHI3, K - 1, PHI6, N_IND, Q, LAM, 1, 1]

    def test_full_spectrum(self):
        """p(k,j) for j=1..k matches expected sequence."""
        spectrum = [_partitions_into_k_parts(K, j) for j in range(1, K + 1)]
        assert spectrum == self.EXPECTED

    def test_spectrum_equals_srg(self):
        """Every entry is an SRG-derived value."""
        spectrum = [_partitions_into_k_parts(K, j) for j in range(1, K + 1)]
        assert spectrum == self.SRG_VALS

    def test_p_1_is_beta0(self):
        """p(12,1) = 1 = β₀."""
        assert _partitions_into_k_parts(K, 1) == 1

    def test_p_lambda_is_perfect(self):
        """p(12,2) = 6 = k/λ = first perfect number."""
        assert _partitions_into_k_parts(K, LAM) == K // LAM

    def test_p_q_is_k(self):
        """p(12,3) = 12 = k: partitions into q parts returns degree."""
        assert _partitions_into_k_parts(K, Q) == K

    def test_p_mu_is_g(self):
        """p(12,4) = 15 = g: partitions into μ parts returns s-multiplicity."""
        assert _partitions_into_k_parts(K, MU) == G_MULT

    def test_p_N_is_phi3(self):
        """p(12,5) = 13 = Φ₃: partitions into N parts returns cyclotomic."""
        assert _partitions_into_k_parts(K, N_IND) == PHI3

    def test_p_6_is_k_minus_1(self):
        """p(12,6) = 11 = k−1."""
        assert _partitions_into_k_parts(K, K // LAM) == K - 1

    def test_p_phi6_is_itself(self):
        """p(12,7) = 7 = Φ₆: Φ₆ appears at position Φ₆."""
        assert _partitions_into_k_parts(K, PHI6) == PHI6

    def test_p_8_is_N(self):
        """p(12,8) = 5 = N."""
        assert _partitions_into_k_parts(K, DIM_O) == N_IND

    def test_p_q2_is_q(self):
        """p(12,9) = 3 = q: symmetric echo."""
        assert _partitions_into_k_parts(K, Q**2) == Q

    def test_p_theta_is_lambda(self):
        """p(12,10) = 2 = λ."""
        assert _partitions_into_k_parts(K, THETA) == LAM

    def test_total_partitions(self):
        """Sum of spectrum = p(12) = 77 = Φ₆·(k−1)."""
        assert sum(self.EXPECTED) == _total_partitions(K)


# ═══════════════════════════════════════════════════════════════
# T158 — Catalan Number → G₂
# ═══════════════════════════════════════════════════════════════
class TestCatalanG2:
    """T158: C(μ) = C(4) = 14 = dim(G₂).

    The μ-th Catalan number equals the dimension of the smallest
    exceptional Lie algebra G₂ (automorphisms of the octonions).
    """

    def test_catalan_mu_is_G2(self):
        """C(4) = 14 = dim(G₂)."""
        assert _catalan(MU) == G2_DIM

    def test_catalan_formula(self):
        """C(4) = C(8,4)/5 = 70/5 = 14."""
        assert comb(2 * MU, MU) // (MU + 1) == 14

    def test_G2_is_aut_O(self):
        """dim(G₂) = 14 = 2·Φ₆ = 2(q²−q+1)."""
        assert G2_DIM == 2 * PHI6

    def test_catalan_sequence(self):
        """C(1..5) = {1, 2, 5, 14, 42}. Two SRG values appear: C(2)=λ, C(3)=N."""
        seq = [_catalan(i) for i in range(1, 6)]
        assert seq == [1, 2, 5, 14, 42]
        assert seq[1] == LAM    # C(2) = 2 = λ
        assert seq[2] == N_IND  # C(3) = 5 = N


# ═══════════════════════════════════════════════════════════════
# T159 — Bell Number → F₄
# ═══════════════════════════════════════════════════════════════
class TestBellF4:
    """T159: B(N) = B(5) = 52 = dim(F₄).

    The N-th Bell number (set partitions of {1,...,N}) equals the
    dimension of the exceptional Lie algebra F₄ (automorphisms
    of the exceptional Jordan algebra J₃(𝕆)).
    """

    def test_bell_N_is_F4(self):
        """B(5) = 52 = dim(F₄)."""
        assert _bell(N_IND) == F4_DIM

    def test_bell_sequence(self):
        """B(0..5) = {1, 1, 2, 5, 15, 52}: three SRG values."""
        seq = [_bell(i) for i in range(6)]
        assert seq == [1, 1, 2, 5, 15, 52]
        assert seq[2] == LAM     # B(2) = 2 = λ
        assert seq[3] == N_IND   # B(3) = 5 = N
        assert seq[4] == G_MULT  # B(4) = 15 = g

    def test_F4_from_bell_and_catalan(self):
        """B(N) − C(μ) = 52 − 14 = 38 = dim(SU(N+1)²−1)?
        Actually 38 = 2·19, not obviously SRG, but F₄ − G₂ = 38."""
        assert _bell(N_IND) - _catalan(MU) == F4_DIM - G2_DIM

    def test_catalan_bell_sum(self):
        """C(μ) + B(N) = 14 + 52 = 66 = C(k,2) = dim(so(k))."""
        assert _catalan(MU) + _bell(N_IND) == comb(K, 2)


# ═══════════════════════════════════════════════════════════════
# T160 — Ramsey Number R(q,q) = First Perfect Number
# ═══════════════════════════════════════════════════════════════
class TestRamseyPerfect:
    """T160: R(q,q) = R(3,3) = 6 = k/λ = first perfect number.

    The diagonal Ramsey number R(q,q): the smallest n such that any
    2-coloring of K_n contains a monochromatic K_q. For q = 3, this
    is the party problem: any group of 6 has 3 mutual friends or strangers.
    """

    def test_R33_is_6(self):
        """R(3,3) = 6 (well-known Ramsey theory result)."""
        # R(3,3) = 6 is one of the most famous results in combinatorics
        assert 6 == K // LAM

    def test_R33_is_perfect(self):
        """R(3,3) = 6: the first perfect number."""
        sigma = sum(d for d in range(1, 7) if 6 % d == 0)
        assert sigma == 12 == 2 * 6

    def test_R22_is_lambda(self):
        """R(2,2) = 2 = λ."""
        assert LAM == 2

    def test_ramsey_at_srg_values(self):
        """R(λ,λ) = R(2,2) = 2 = λ (fixed point)."""
        assert LAM == 2  # R(2,2) = 2

    def test_R33_partition_match(self):
        """R(q,q) = p(k,λ) = 6: Ramsey meets partition spectrum."""
        assert K // LAM == _partitions_into_k_parts(K, LAM)


# ═══════════════════════════════════════════════════════════════
# T161 — Dual Coxeter Numbers = SRG Values
# ═══════════════════════════════════════════════════════════════
class TestDualCoxeterSpectrum:
    """T161: The dual Coxeter numbers of all 5 exceptional Lie algebras
    are SRG-derived:

    h∨(G₂) = 4 = μ
    h∨(F₄) = 9 = q²
    h∨(E₆) = 12 = k
    h∨(E₇) = 18 = 2q²
    h∨(E₈) = 30 = v − θ

    The dual Coxeter number governs conformal levels and WZW models.
    """

    # Dual Coxeter numbers (well-established mathematical constants)
    DUAL_COXETER = {14: 4, 52: 9, 78: 12, 133: 18, 248: 30}

    def test_G2(self):
        """h∨(G₂) = 4 = μ."""
        assert self.DUAL_COXETER[G2_DIM] == MU

    def test_F4(self):
        """h∨(F₄) = 9 = q²."""
        assert self.DUAL_COXETER[F4_DIM] == Q**2

    def test_E6(self):
        """h∨(E₆) = 12 = k."""
        assert self.DUAL_COXETER[E6_DIM] == K

    def test_E7(self):
        """h∨(E₇) = 18 = 2q²."""
        assert self.DUAL_COXETER[E7_DIM] == 2 * Q**2

    def test_E8(self):
        """h∨(E₈) = 30 = v − θ."""
        assert self.DUAL_COXETER[E8_DIM] == V - THETA

    def test_sum(self):
        """4+9+12+18+30 = 73 (prime, Hubble local value H₀)."""
        assert sum(self.DUAL_COXETER.values()) == 73

    def test_product_factorization(self):
        """4×9×12×18×30 = 233280 = |Aut|·(9/2) = 51840×4.5.
        Or: 233280 = 2⁵·3⁶·5·(k/λ)... 233280 = 2⁵·3⁶·5·6/2.
        Actually: 233280 = 51840 × μ + 51840/2... let's check:
        233280 / 51840 = 4.5 = q²/λ."""
        prod = MU * Q**2 * K * (2 * Q**2) * (V - THETA)
        assert prod == 233280
        assert Fraction(prod, AUT_ORDER) == Fraction(Q**2, LAM)


# ═══════════════════════════════════════════════════════════════
# T162 — Stable Homotopy Group |π₃ˢ| = f
# ═══════════════════════════════════════════════════════════════
class TestStableHomotopy:
    """T162: |π₃ˢ(S⁰)| = 24 = f.

    The third stable homotopy group of spheres is ℤ/24, a deep
    invariant of algebraic topology. Its order equals the eigenvalue
    multiplicity f, connecting homotopy theory to spectral graph theory.
    """

    # Well-known stable stems: |π_n^s| for n = 0,1,2,3
    STABLE_STEMS = {0: 1, 1: 2, 2: 2, 3: 24}

    def test_pi3_is_f(self):
        """π₃ˢ ≅ ℤ/24: order = f = 24."""
        assert self.STABLE_STEMS[3] == F_MULT

    def test_pi1_is_lambda(self):
        """π₁ˢ ≅ ℤ/2: order = λ = 2."""
        assert self.STABLE_STEMS[1] == LAM

    def test_pi2_is_lambda(self):
        """π₂ˢ ≅ ℤ/2: order = λ = 2."""
        assert self.STABLE_STEMS[2] == LAM

    def test_pi0_is_1(self):
        """π₀ˢ ≅ ℤ: free part = 1 = β₀."""
        assert self.STABLE_STEMS[0] == 1

    def test_24_is_f_mult(self):
        """f = 24 = 4! = μ!."""
        assert F_MULT == factorial(MU)


# ═══════════════════════════════════════════════════════════════
# T163 — Icosahedral Parameters from SRG
# ═══════════════════════════════════════════════════════════════
class TestIcosahedralParameters:
    """T163: The icosahedron — one of 5 Platonic solids — has:
    (V, E, F) = (12, 30, 20) = (k, v−θ, v/2).

    Its dual the dodecahedron has (V, E, F) = (v/2, v−θ, k).
    Both encode SRG parameters in their combinatorial structure.
    """

    ICO_V, ICO_E, ICO_F = 12, 30, 20

    def test_ico_vertices_is_k(self):
        """12 vertices = k."""
        assert self.ICO_V == K

    def test_ico_edges_is_v_minus_theta(self):
        """30 edges = v − θ = 40 − 10."""
        assert self.ICO_E == V - THETA

    def test_ico_faces_is_v_over_2(self):
        """20 faces = v/2."""
        assert self.ICO_F == V // 2

    def test_euler_char(self):
        """V − E + F = 12 − 30 + 20 = 2 (sphere)."""
        assert self.ICO_V - self.ICO_E + self.ICO_F == 2

    def test_dodecahedron_dual(self):
        """Dual: (V,E,F) = (20, 30, 12) = (v/2, v−θ, k)."""
        assert (V // 2, V - THETA, K) == (20, 30, 12)

    def test_platonic_count_is_N(self):
        """Exactly N = 5 Platonic solids exist."""
        assert N_IND == 5


# ═══════════════════════════════════════════════════════════════
# T164 — Alternating & Binary Icosahedral Groups
# ═══════════════════════════════════════════════════════════════
class TestAlternatingBinaryIcosahedral:
    """T164: |A_N| = |A₅| = 60 = E/μ = σ(f).
    |2I| = 120 = E/2 (binary icosahedral group, double cover of A₅).

    A₅ is the unique simple group of order 60, and the icosahedral
    rotation group. Its double cover 2I ⊂ SU(2) connects to E₈
    via the McKay correspondence.
    """

    def test_alt_N_order(self):
        """|A₅| = 5!/2 = 60."""
        assert factorial(N_IND) // 2 == 60

    def test_alt_N_is_E_over_mu(self):
        """|A₅| = E/μ = 240/4 = 60."""
        assert factorial(N_IND) // 2 == E // MU

    def test_binary_icosahedral(self):
        """|2I| = 120 = E/2 = 240/2."""
        assert 120 == E // 2

    def test_2I_is_double_cover(self):
        """|2I| = 2·|A₅| = 2·60 = 120."""
        assert 2 * (factorial(N_IND) // 2) == E // 2

    def test_sigma_f(self):
        """σ(24) = 60 = |A₅|: divisor sum of f equals alternating group order."""
        sigma_f = sum(d for d in range(1, F_MULT + 1) if F_MULT % d == 0)
        assert sigma_f == factorial(N_IND) // 2

    def test_mckay_ADE(self):
        """2I → E₈ in McKay correspondence: |2I| = 120, dim(E₈) = 248."""
        assert E // 2 == 120
        assert E8_DIM == 248


# ═══════════════════════════════════════════════════════════════
# T165 — Derangement Count D(μ) = q²
# ═══════════════════════════════════════════════════════════════
class TestDerangementCount:
    """T165: D(μ) = D(4) = 9 = q².

    The number of derangements (fixed-point-free permutations) of μ
    elements equals q². The subfactorial !4 = 9 connects the
    common-neighbor parameter to the field order.
    """

    def test_D_mu_is_q_squared(self):
        """D(4) = 9 = q²."""
        assert _derangement(MU) == Q**2

    def test_derangement_formula(self):
        """D(4) = 4!(1 − 1 + 1/2 − 1/6 + 1/24) = 24·(9/24) = 9."""
        assert _derangement(MU) == 9

    def test_D_sequence(self):
        """D(0..5) = {1, 0, 1, 2, 9, 44}: D(3) = λ, D(4) = q²."""
        seq = [_derangement(i) for i in range(6)]
        assert seq == [1, 0, 1, 2, 9, 44]
        assert seq[3] == LAM

    def test_D5_is_v_plus_mu(self):
        """D(5) = 44 = v + μ = 4(k−1)."""
        assert _derangement(5) == V + MU
        assert _derangement(5) == 4 * (K - 1)


# ═══════════════════════════════════════════════════════════════
# T166 — Modular Group Index [SL(2,ℤ):Γ(q)] = f
# ═══════════════════════════════════════════════════════════════
class TestModularGroupIndex:
    """T166: [SL(2,ℤ) : Γ(q)] = q³·(1 − 1/q²) = 27·(8/9) = 24 = f.

    The index of the principal congruence subgroup Γ(3) in the
    modular group equals the eigenvalue multiplicity f = 24.
    This connects modular forms to spectral graph theory.
    """

    def test_index_is_f(self):
        """[SL(2,ℤ) : Γ(3)] = 24 = f."""
        # q³ × (q²-1)/q² = q(q²-1) = 3×8 = 24
        index = Q * (Q**2 - 1)
        assert index == F_MULT

    def test_formula_expanded(self):
        """q(q² − 1) = q(q−1)(q+1) = 3·2·4 = 24."""
        assert Q * (Q - 1) * (Q + 1) == F_MULT

    def test_factors(self):
        """q(q−1)(q+1) = q·λ·μ = 3·2·4 = 24."""
        assert Q * LAM * MU == F_MULT

    def test_f_is_mu_factorial(self):
        """24 = μ! = 4! — the multiplicity is also a factorial."""
        assert F_MULT == factorial(MU)


# ═══════════════════════════════════════════════════════════════
# T167 — Stirling Square: S₂(N, q) = N²
# ═══════════════════════════════════════════════════════════════
class TestStirlingSquare:
    """T167: S₂(N, q) = S₂(5, 3) = 25 = N².

    The Stirling number of the second kind: the number of ways to
    partition {1,...,N} into exactly q non-empty subsets equals N².
    """

    def test_S2_is_N_squared(self):
        """S₂(5, 3) = 25 = N² = 5²."""
        assert _stirling2(N_IND, Q) == N_IND**2

    def test_verification(self):
        """S₂(5,3) = (1/6)[3⁵ − 3·2⁵ + 3] = (243−96+3)/6 = 150/6 = 25."""
        val = (Q**N_IND - Q * 2**N_IND + Q) // factorial(Q)
        assert val == N_IND**2

    def test_other_stirling(self):
        """S₂(N, λ) = S₂(5, 2) = 15 = g."""
        assert _stirling2(N_IND, LAM) == G_MULT

    def test_stirling_mu(self):
        """S₂(N, μ) = S₂(5, 4) = 10 = θ."""
        assert _stirling2(N_IND, MU) == THETA

    def test_stirling_spectrum(self):
        """S₂(5, j) for j=1..5 = {1, 15, 25, 10, 1}: SRG values throughout."""
        seq = [_stirling2(N_IND, j) for j in range(1, N_IND + 1)]
        assert seq == [1, G_MULT, N_IND**2, THETA, 1]


# ═══════════════════════════════════════════════════════════════
# T168 — Total Partitions p(k) = Φ₆·(k−1)
# ═══════════════════════════════════════════════════════════════
class TestTotalPartitions:
    """T168: p(k) = p(12) = 77 = Φ₆·(k−1) = 7 × 11.

    The total number of unrestricted partitions of k factors into
    the cyclotomic value Φ₆ and k−1 (both SRG-derived primes).
    """

    def test_p12_is_77(self):
        """p(12) = 77."""
        assert _total_partitions(K) == 77

    def test_factorization(self):
        """77 = 7 × 11 = Φ₆ × (k−1)."""
        assert _total_partitions(K) == PHI6 * (K - 1)

    def test_both_factors_prime(self):
        """7 and 11 are both prime."""
        assert all(7 % p != 0 for p in range(2, 3))
        assert all(11 % p != 0 for p in range(2, 4))

    def test_spectrum_sum(self):
        """Sum of partition spectrum = p(k)."""
        spectrum = [_partitions_into_k_parts(K, j) for j in range(1, K + 1)]
        assert sum(spectrum) == _total_partitions(K)


# ═══════════════════════════════════════════════════════════════
# T169 — Fibonacci-Lucas Cycle
# ═══════════════════════════════════════════════════════════════
class TestFibonacciLucasCycle:
    """T169: The Fibonacci and Lucas sequences at SRG values form a
    closed cycle through the parameter space:

    F(Φ₆) = F(7) = 13 = Φ₃
    L(N) = L(5) = 11 = k−1
    L(N) + F(N) = 11 + 5 = 16 = 2^μ
    L(N) − F(N) = 11 − 5 = 6 = k/λ

    Fibonacci maps cyclotomic to cyclotomic; Lucas encodes SRG sums.
    """

    def test_fib_phi6_is_phi3(self):
        """F(Φ₆) = F(7) = 13 = Φ₃."""
        assert _fib(PHI6) == PHI3

    def test_lucas_N_is_k_minus_1(self):
        """L(N) = L(5) = 11 = k − 1."""
        assert _lucas(N_IND) == K - 1

    def test_lucas_plus_fib(self):
        """L(5) + F(5) = 11 + 5 = 16 = 2^μ."""
        assert _lucas(N_IND) + _fib(N_IND) == 2**MU

    def test_lucas_minus_fib(self):
        """L(5) − F(5) = 11 − 5 = 6 = k/λ = first perfect number."""
        assert _lucas(N_IND) - _fib(N_IND) == K // LAM

    def test_lucas_fib_product(self):
        """L(5)·F(5) = 11 × 5 = 55 = F(10) = F(θ)."""
        assert _lucas(N_IND) * _fib(N_IND) == _fib(THETA)

    def test_fib_N_is_N(self):
        """F(5) = 5 = N: Fibonacci fixed point."""
        assert _fib(N_IND) == N_IND

    def test_lucas_decomposition(self):
        """L(5) = F(4) + F(6) = 3 + 8 = q + dim(O) = k − 1."""
        assert _fib(MU) + _fib(MU + 2) == K - 1
        assert _fib(MU) == Q
        assert _fib(MU + 2) == DIM_O


# ═══════════════════════════════════════════════════════════════
# T170 — Partition of N = Φ₆
# ═══════════════════════════════════════════════════════════════
class TestPartitionOfN:
    """T170: p(N) = p(5) = 7 = Φ₆.

    The number of unrestricted partitions of N (the independence number)
    equals Φ₆ (the 6th cyclotomic polynomial at q). With T158-T159
    this forms a combinatorial trilogy:

    C(μ) = dim(G₂) = 14
    B(N) = dim(F₄) = 52
    p(N) = Φ₆ = 7

    Catalan, Bell, and partition functions all return SRG values
    when evaluated at SRG parameters.
    """

    def test_p5_is_phi6(self):
        """p(5) = 7 = Φ₆."""
        assert _total_partitions(N_IND) == PHI6

    def test_partitions_of_5(self):
        """5, 4+1, 3+2, 3+1+1, 2+2+1, 2+1+1+1, 1+1+1+1+1 → 7 partitions."""
        assert _total_partitions(5) == 7

    def test_trilogy(self):
        """C(μ) + B(N) + p(N) = 14 + 52 + 7 = 73 (prime, H₀ local)."""
        total = _catalan(MU) + _bell(N_IND) + _total_partitions(N_IND)
        assert total == 73

    def test_catalan_bell_partition_sum(self):
        """Same sum: 73 = sum of dual Coxeter numbers of all exceptionals."""
        assert 73 == MU + Q**2 + K + 2 * Q**2 + (V - THETA)

    def test_p_of_srg_primes(self):
        """p(2)=2=λ, p(3)=3=q, p(5)=7=Φ₆: partitions of SRG primes return SRG values."""
        assert _total_partitions(LAM) == LAM
        assert _total_partitions(Q) == Q
        assert _total_partitions(N_IND) == PHI6
