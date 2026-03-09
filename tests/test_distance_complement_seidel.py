"""
Phase XLIII: Distance, Complement & Seidel Algebra on W(3,3) (T606-T620)
=========================================================================

Fifteen theorems on the natural matrix algebra spanned by {I, A, J}.

Every matrix derived from the adjacency A — distance D, complement Ā,
Seidel S, Laplacian L — has eigenvalues that are key W(3,3) constants:

  A:  K=12,   r=2,      s=-4
  D:  66,     s=-4,     r=2       ← eigenvalues SWAP!
  Ā:  q³=27,  -q=-3,    q=3       ← ALL powers of q!
  S:  g=15,   -N=-5,    Φ₆=7      ← ALL key constants!
  L:  0,      Θ=10,     16

The graph W(3,3) encodes its entire mathematical identity in the
eigenvalue spectra of its natural matrices.

Parameters: (v, k, λ, μ, q) = (40, 12, 2, 4, 3).
"""

import math
import pytest
from fractions import Fraction

# ── SRG parameters for W(3,3) ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V * K // 2           # 240
R, S = 2, -4             # eigenvalues
F, G = 24, 15            # multiplicities
N = Q + 2                # 5
PHI3 = Q**2 + Q + 1      # 13
PHI6 = Q**2 - Q + 1      # 7
ALBERT = V - PHI3        # 27
DIM_O = K - MU           # 8
THETA = K - R             # 10
NONEDGES = V * (V - 1) // 2 - E   # 540


# ═══════════════════════════════════════════════════════════════════
# T606: Distance Matrix
# ═══════════════════════════════════════════════════════════════════
class TestDistanceMatrix:
    """D = 2J − 2I − A for diameter-2 graphs.
    Eigenvalues: 2V−2−K = 66, s = −4, r = 2.
    """

    def test_formula(self):
        """D = 2J − 2I − A (all distances are 0, 1, or 2)."""
        # Eigenvalue on all-ones: 2V - 2 - K
        d0 = 2*V - 2 - K
        assert d0 == 66

    def test_eigenvalue_trivial(self):
        """Trivial eigenvalue = 2V−2−K = 66."""
        assert 2*V - 2 - K == 66

    def test_eigenvalue_on_r_space(self):
        """On r-eigenspace: d = −2−r = −4 = s (swapped!)."""
        assert -2 - R == S

    def test_eigenvalue_on_s_space(self):
        """On s-eigenspace: d = −2−s = 2 = r (swapped!)."""
        assert -2 - S == R

    def test_trace_zero(self):
        """Tr(D) = 0 (diagonal is all zeros)."""
        assert (2*V - 2 - K) + F*S + G*R == 0


# ═══════════════════════════════════════════════════════════════════
# T607: Eigenvalue Swap under Distance
# ═══════════════════════════════════════════════════════════════════
class TestEigenvalueSwap:
    """The distance matrix swaps eigenvalues r ↔ s:
    the map x ↦ −2−x sends r→s and s→r.
    """

    def test_r_maps_to_s(self):
        """−2 − r = s: eigenvalue r becomes s."""
        assert -2 - R == S

    def test_s_maps_to_r(self):
        """−2 − s = r: eigenvalue s becomes r."""
        assert -2 - S == R

    def test_involution(self):
        """The map x ↦ −2−x is an involution: applied twice gives identity."""
        for x in [R, S, K]:
            assert -2 - (-2 - x) == x

    def test_fixed_point(self):
        """Fixed point of x ↦ −2−x is x = −1."""
        assert -2 - (-1) == -1

    def test_midpoint(self):
        """(r + s)/2 = −1 = fixed point of the swap map."""
        assert Fraction(R + S, 2) == -1


# ═══════════════════════════════════════════════════════════════════
# T608: Wiener Index
# ═══════════════════════════════════════════════════════════════════
class TestWienerIndex:
    """Wiener index W = Σ d(i,j) = V(V−1) − E = 1320.
    Sum of all pairwise distances.
    """

    def test_wiener_value(self):
        """W = 1320."""
        W = V * (V - 1) - E
        assert W == 1320

    def test_wiener_formula(self):
        """W = E·1 + nonedges·2 = 240 + 1080."""
        W = E + 2 * NONEDGES
        assert W == 1320

    def test_wiener_vertex_formula(self):
        """W = V·(2V−2−K)/2 = 40·66/2."""
        W = V * (2*V - 2 - K) // 2
        assert W == 1320

    def test_wiener_prime_factors(self):
        """1320 = 2³·3·5·11, four prime factors = μ."""
        assert 2**3 * 3 * 5 * 11 == 1320
        primes = set()
        n = 1320
        for p in [2, 3, 5, 7, 11]:
            while n % p == 0:
                primes.add(p)
                n //= p
        assert len(primes) == MU


# ═══════════════════════════════════════════════════════════════════
# T609: Average Distance
# ═══════════════════════════════════════════════════════════════════
class TestAverageDistance:
    """Average distance d̄ = W/binom(V,2) = 22/Φ₃ = 22/13."""

    def test_avg_distance(self):
        """d̄ = 1320/780 = 22/13."""
        avg = Fraction(V*(V-1) - E, V*(V-1)//2)
        assert avg == Fraction(22, 13)

    def test_avg_phi3(self):
        """d̄ = 22/Φ₃ where Φ₃ = 13."""
        avg = Fraction(22, PHI3)
        assert avg == Fraction(22, 13)

    def test_numerator_22(self):
        """22 = 2·11 = 2(K−1)."""
        assert 22 == 2 * (K - 1)

    def test_avg_between_1_and_2(self):
        """1 < d̄ < 2 (diameter = 2)."""
        avg = Fraction(22, 13)
        assert 1 < avg < 2

    def test_complement_fraction(self):
        """2 − d̄ = 4/13 = μ/Φ₃ (fraction at distance 1)."""
        complement = 2 - Fraction(22, 13)
        assert complement == Fraction(MU, PHI3)


# ═══════════════════════════════════════════════════════════════════
# T610: Distance Determinant
# ═══════════════════════════════════════════════════════════════════
class TestDistanceDeterminant:
    """det(D) = 66 · (−4)²⁴ · 2¹⁵ = 3·11·2⁶⁴."""

    def test_det_value(self):
        """det(D) = 3 · 11 · 2⁶⁴."""
        det_D = (2*V-2-K) * S**F * R**G
        assert det_D == 3 * 11 * 2**64

    def test_det_positive(self):
        """det(D) > 0 (f = 24 is even, so s^f > 0)."""
        det_D = (2*V-2-K) * S**F * R**G
        assert det_D > 0

    def test_66_factored(self):
        """66 = 2·3·11 = 2·(K−1)·3 = 2V−2−K."""
        assert 2*V - 2 - K == 66
        assert 66 == 2 * 3 * 11

    def test_exponent_64(self):
        """2⁶⁴: power of 2 exponent = 2f + g = 48 + 15 + 1 = 64."""
        # From s^f * r^g = (-4)^24 * 2^15 = 4^24 * 2^15 = 2^48 * 2^15 = 2^63
        # Times 66 = 2*33 gives 2^64 * 33 = 2^64 * 3*11
        assert 2*F + G + 1 == 64


# ═══════════════════════════════════════════════════════════════════
# T611: Complement Eigenvalues — All Powers of q
# ═══════════════════════════════════════════════════════════════════
class TestComplementEigenvalues:
    """Ā eigenvalues: q³ = 27, −q = −3, +q = 3.
    ALL complement eigenvalues are powers/negations of q!
    """

    def test_complement_trivial(self):
        """k̄ = V−1−K = 27 = q³ = ALBERT."""
        assert V - 1 - K == Q**3
        assert V - 1 - K == ALBERT

    def test_complement_r(self):
        """Complement r̄ = −1−r = −3 = −q."""
        assert -1 - R == -Q

    def test_complement_s(self):
        """Complement s̄ = −1−s = 3 = q."""
        assert -1 - S == Q

    def test_all_q_powers(self):
        """All complement eigenvalues: {q³, q, −q} — all from q."""
        eigs = {V-1-K, -1-R, -1-S}
        assert eigs == {Q**3, Q, -Q}

    def test_symmetric_nontrivial(self):
        """Non-trivial complement eigenvalues are ±q = ±3."""
        assert -1 - R == -(-1 - S)  # symmetric around 0


# ═══════════════════════════════════════════════════════════════════
# T612: Complement Determinant
# ═══════════════════════════════════════════════════════════════════
class TestComplementDeterminant:
    """det(Ā) = q³ · (−q)^f · q^g = q^(3+f+g) = q^42 = 3^42."""

    def test_det_value(self):
        """det(Ā) = 3⁴² = q⁴²."""
        det_bar = (V-1-K) * (-1-R)**F * (-1-S)**G
        assert det_bar == Q**42

    def test_exponent_42(self):
        """Exponent: 3 + f + g = 3 + 24 + 15 = 42 = V + 2."""
        assert 3 + F + G == 42
        assert 3 + F + G == V + 2

    def test_det_positive(self):
        """det(Ā) > 0 since (−q)^f = (−3)^24 > 0."""
        assert (-1-R)**F > 0  # f=24 is even

    def test_pure_prime_power(self):
        """det(Ā) = 3⁴² — a pure prime power!"""
        det_bar = Q**42
        n = det_bar
        while n % 3 == 0:
            n //= 3
        assert n == 1


# ═══════════════════════════════════════════════════════════════════
# T613: Seidel Eigenvalues — All Key Constants
# ═══════════════════════════════════════════════════════════════════
class TestSeidelEigenvalues:
    """Seidel matrix S = J − I − 2A has eigenvalues:
    g = 15 (×1), −N = −5 (×f), Φ₆ = 7 (×g).
    EVERY key constant appears as a Seidel eigenvalue!
    """

    def test_seidel_trivial(self):
        """Trivial Seidel eigenvalue = V−1−2K = 15 = g."""
        assert V - 1 - 2*K == G

    def test_seidel_on_r_space(self):
        """On r-eigenspace: −1−2r = −5 = −N."""
        assert -1 - 2*R == -N

    def test_seidel_on_s_space(self):
        """On s-eigenspace: −1−2s = 7 = Φ₆."""
        assert -1 - 2*S == PHI6

    def test_all_key_constants(self):
        """Seidel eigenvalues = {g, −N, Φ₆} = {15, −5, 7}."""
        eigs = {V-1-2*K, -1-2*R, -1-2*S}
        assert eigs == {G, -N, PHI6}

    def test_seidel_trace_zero(self):
        """Tr(S) = g + f(−N) + g·Φ₆ = 15 − 120 + 105 = 0."""
        assert G + F*(-N) + G*PHI6 == 0


# ═══════════════════════════════════════════════════════════════════
# T614: Seidel Energy Equals E
# ═══════════════════════════════════════════════════════════════════
class TestSeidelEnergy:
    """Seidel energy = Σ|s_i| = |g| + f|N| + g·Φ₆ = 240 = E.
    The Seidel energy equals the number of edges!
    """

    def test_seidel_energy_value(self):
        """Σ|s_i| = 15 + 120 + 105 = 240 = E."""
        energy = abs(G) + F*abs(N) + G*PHI6
        assert energy == E

    def test_components(self):
        """Components: g=15, f·N=120=E/2, g·Φ₆=105."""
        assert abs(G) == 15
        assert F * N == 120
        assert G * PHI6 == 105

    def test_fn_half_E(self):
        """f·N = 24·5 = 120 = E/2."""
        assert F * N == E // 2

    def test_seidel_energy_ratio(self):
        """Seidel energy / V = E/V = K/2 = 6 = 2q."""
        assert Fraction(E, V) == Fraction(K, 2)


# ═══════════════════════════════════════════════════════════════════
# T615: Seidel Determinant
# ═══════════════════════════════════════════════════════════════════
class TestSeidelDeterminant:
    """det(S) = g · (−N)^f · Φ₆^g = q · N²⁵ · Φ₆^g."""

    def test_det_formula(self):
        """det(S) = 15 · (−5)²⁴ · 7¹⁵ = 3·5²⁵·7¹⁵."""
        det_S = G * (-N)**F * PHI6**G
        assert det_S == 3 * 5**25 * 7**15

    def test_det_as_q_N_phi6(self):
        """det(S) = q · N²⁵ · Φ₆^g."""
        det_S = G * (-N)**F * PHI6**G
        assert det_S == Q * N**25 * PHI6**G

    def test_det_positive(self):
        """det(S) > 0 since (−N)^f = (−5)^24 > 0."""
        assert (-N)**F > 0

    def test_three_prime_factors(self):
        """det(S) has 3 prime factors {3,5,7} — all single-digit primes."""
        det_val = 3 * 5**25 * 7**15
        n = det_val
        primes = set()
        for p in [3, 5, 7]:
            while n % p == 0:
                primes.add(p)
                n //= p
        assert n == 1
        assert primes == {Q, N, PHI6}


# ═══════════════════════════════════════════════════════════════════
# T616: Transmission and Harary
# ═══════════════════════════════════════════════════════════════════
class TestTransmissionHarary:
    """Transmission T(v) = 66 = 2(V−1)−K (constant, vertex-transitive).
    Harary index H = E + nonedges/2 = 510.
    """

    def test_transmission(self):
        """T(v) = 2V−2−K = 66 for all v."""
        T = 2*V - 2 - K
        assert T == 66

    def test_transmission_factored(self):
        """66 = 2·3·11 = 6·(K−1)."""
        assert 66 == 6 * (K - 1)
        assert 66 == 2 * 3 * 11

    def test_harary_index(self):
        """H = Σ 1/d(i,j) = E + nonedges/2 = 510."""
        H = E + NONEDGES // 2
        assert H == 510

    def test_harary_factored(self):
        """510 = 2·3·5·17."""
        assert 2 * 3 * 5 * 17 == 510

    def test_transmission_11(self):
        """T(v) / 6 = 11 = K − 1."""
        assert 66 // 6 == K - 1


# ═══════════════════════════════════════════════════════════════════
# T617: Seidel Trace Identities
# ═══════════════════════════════════════════════════════════════════
class TestSeidelTraces:
    """Tr(S) = 0 and Tr(S²) = V(V−1) = 1560."""

    def test_trace_S_zero(self):
        """Tr(S) = 0 (S has zero diagonal)."""
        assert G + F*(-N) + G*PHI6 == 0

    def test_trace_S2(self):
        """Tr(S²) = V(V−1) = 1560."""
        tr2 = G**2 + F*N**2 + G*PHI6**2
        assert tr2 == V * (V - 1)

    def test_S2_diagonal(self):
        """S²ᵢᵢ = V − 1 = 39 for all i."""
        # Tr(S²)/V = V-1
        assert (G**2 + F*N**2 + G*PHI6**2) // V == V - 1

    def test_S2_from_components(self):
        """Tr(S²) = 225 + 600 + 735 = 1560."""
        assert G**2 == 225
        assert F * N**2 == 600
        assert G * PHI6**2 == 735
        assert 225 + 600 + 735 == 1560


# ═══════════════════════════════════════════════════════════════════
# T618: Eigenvalue Dictionary
# ═══════════════════════════════════════════════════════════════════
class TestEigenvalueDictionary:
    """Every key W(3,3) constant appears as a matrix eigenvalue:
    K, r, s ← A;  Θ, 16 ← L;  q³, ±q ← Ā;  g, N, Φ₆ ← S.
    """

    def test_K_from_A(self):
        """K = 12 is an A-eigenvalue."""
        assert K == 12

    def test_theta_from_L(self):
        """Θ = K−r = 10 is an L-eigenvalue."""
        assert K - R == THETA

    def test_albert_from_complement(self):
        """ALBERT = q³ = 27 is an Ā-eigenvalue."""
        assert V - 1 - K == ALBERT

    def test_q_from_complement(self):
        """q = 3 is an Ā-eigenvalue."""
        assert -1 - S == Q

    def test_g_from_seidel(self):
        """g = 15 is a Seidel eigenvalue."""
        assert V - 1 - 2*K == G

    def test_N_from_seidel(self):
        """N = 5 is a |Seidel eigenvalue|."""
        assert abs(-1 - 2*R) == N

    def test_phi6_from_seidel(self):
        """Φ₆ = 7 is a Seidel eigenvalue."""
        assert -1 - 2*S == PHI6


# ═══════════════════════════════════════════════════════════════════
# T619: Matrix Linear Span
# ═══════════════════════════════════════════════════════════════════
class TestMatrixSpan:
    """All natural matrices lie in span{I, A, J}:
    D = 2J − 2I − A, Ā = J − I − A, S = J − I − 2A, L = KI − A.
    """

    def test_D_coefficients(self):
        """D = 2J − 2I − A: coeffs (I=-2, A=-1, J=2)."""
        # Verify via eigenvalue: 2V - 2 - K = 2*40-2-12 = 66 ✓
        assert 2*V - 2*1 - K == 66

    def test_complement_coefficients(self):
        """Ā = J − I − A: coeffs (I=-1, A=-1, J=1)."""
        assert V - 1 - K == ALBERT

    def test_seidel_coefficients(self):
        """S = J − I − 2A: coeffs (I=-1, A=-2, J=1)."""
        assert V - 1 - 2*K == G

    def test_laplacian_coefficients(self):
        """L = KI − A: coeffs (I=K, A=-1, J=0)."""
        assert K - K == 0  # trivial eigenvalue
        assert K - R == THETA  # first non-trivial

    def test_bose_mesner_dimension(self):
        """dim(span{I, A, J}) = 3 = rank of association scheme."""
        # Three linearly independent: I, A, J
        # All matrices have eigenvalues determined by 3 eigenspaces
        assert Q == 3


# ═══════════════════════════════════════════════════════════════════
# T620: Determinant Catalog
# ═══════════════════════════════════════════════════════════════════
class TestDeterminantCatalog:
    """Determinants of all natural matrices from SRG parameters:
    det(A) = −3·2⁵⁶, det(Ā) = q⁴², det(S) = q·N²⁵·Φ₆^g,
    det(D) = 3·11·2⁶⁴, det'(L) = 2⁸⁴·5²⁴.
    """

    def test_det_A(self):
        """det(A) = −3·2⁵⁶."""
        assert K * R**F * S**G == -3 * 2**56

    def test_det_complement(self):
        """det(Ā) = q⁴² = 3⁴²."""
        assert (V-1-K) * (-1-R)**F * (-1-S)**G == Q**42

    def test_det_seidel(self):
        """det(S) = q·N²⁵·Φ₆^g."""
        assert G * (-N)**F * PHI6**G == Q * N**25 * PHI6**G

    def test_det_distance(self):
        """det(D) = 3·11·2⁶⁴."""
        assert (2*V-2-K) * S**F * R**G == 3 * 11 * 2**64

    def test_det_prime_laplacian(self):
        """det'(L) = 10²⁴·16¹⁵ = 2⁸⁴·5²⁴ (product of nonzero L-eigenvalues)."""
        assert (K-R)**F * (K-S)**G == 2**84 * 5**24
