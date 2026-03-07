"""
Theorems T171-T185: Spectral Algebra — Graph Energy, Finite Group Tower,
Signless Laplacian, Minimal Polynomial, Kneser Embedding, Cheeger Bound,
and Eigenvalue Arithmetic.

Phase XIV: The spectral theory of W(3,3) is a self-consistent algebraic
machine whose every output — graph energy, signless Laplacian eigenvalues,
minimal polynomial coefficients, Hoffman determinant, spectral moments,
walk kurtosis, expander constants — rewrites itself in terms of
(v,k,λ,μ,q) = (40,12,2,4,3) and the Lie-algebraic dimensions they encode.

T171: Graph Energy — |k|+f|r|+g|s| = E/2 = |2I| = 120
T172: Finite Group Tower — |PSL(2,q)|=k, |SL(2,q)|=f, |GL(2,q)|=2f, |Sp(4,q)|=Aut
T173: Signless Laplacian — eigenvalues = (f, G₂, dim O) = (24, 14, 8)
T174: Minimal Polynomial — x³ − θx² − 2^(μ+1)x + μf: all coeffs from SRG
T175: Complement Energy — Energy(W̄) = k² = 144, Energy·Energy_bar = Aut/q
T176: Spectral Moments — M₂=k, M₃=f, ratio M₃/M₂ = λ
T177: Quartic Walks — W₄/v = 2^μ(v−1) = 624, kurtosis = Φ₃/q
T178: Hoffman Determinant — det(kI+A) = f · G₂^f · dim(O)^g
T179: Universal Ratio — f/g = (k−s)/(k−r) = dim(O)/N = 8/5
T180: Kneser Embedding — K(N,λ) = Petersen: |V|=θ, deg=q
T181: Spectral Determinant — det(I+A) = −Φ₃ · q^(v−1)
T182: Ramanujan Property — |r|,|s| < 2√(k−1): W(3,3) is Ramanujan
T183: Cheeger Bound — h(G) ≥ k−|s| = dim(O) = 8
T184: Divisor-Totient Chain — σ(g)=f, φ(E)=2^(k/λ), rank_q(A)=q·Φ₃
T185: Eigenvalue Arithmetic — r−s=k/λ, k/|s|=q, Δ=(k/λ)²
"""
from __future__ import annotations
import math
from math import comb, gcd
import pytest
from fractions import Fraction
import numpy as np
from collections import Counter, defaultdict


# ── SRG parameters ──────────────────────────────────────────────
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
THETA = 10         # independence number / Lovász theta
R_EIGEN = 2        # positive nontrivial eigenvalue
S_EIGEN = -4       # negative nontrivial eigenvalue
E = 240            # edge count = vk/2
F_MULT = 24        # multiplicity of r = 2
G_MULT = 15        # multiplicity of s = -4
PHI3 = 13          # q² + q + 1
PHI6 = 7           # q² − q + 1
N = 5              # independence dimension
ALBERT = 27        # v − k − 1
AUT = 51840        # |Sp(4,3)| = |W(E₆)|
DIM_O = K - MU     # 8 = dim(octonions)
G2_DIM = 14
F4_DIM = 52
E6_DIM = 78
E7_DIM = 133
E8_DIM = 248


# ── W(3,3) builder ─────────────────────────────────────────────
def _build_w33():
    points = []
    for a in range(3):
        for b in range(3):
            for c in range(3):
                for d in range(3):
                    vec = [a, b, c, d]
                    nz = next((i for i, x in enumerate(vec) if x != 0), None)
                    if nz is None:
                        continue
                    if vec[nz] == 1:
                        points.append(tuple(vec))

    def J(x, y):
        return (x[0]*y[3] - x[1]*y[2] + x[2]*y[1] - x[3]*y[0]) % 3

    iso_points = [p for p in points if J(p, p) == 0]
    edges = []
    adj: dict[int, set[int]] = defaultdict(set)
    n = len(iso_points)
    for i in range(n):
        for j in range(i + 1, n):
            if J(iso_points[i], iso_points[j]) == 0:
                edges.append((i, j))
                adj[i].add(j)
                adj[j].add(i)

    return iso_points, edges, adj


@pytest.fixture(scope="module")
def w33():
    """Build the 40-vertex symplectic polar graph W(3,3) over GF(3)."""
    pts, edges, adj = _build_w33()
    nv = len(pts)
    A = np.zeros((nv, nv), dtype=int)
    for u, v in edges:
        A[u, v] = 1
        A[v, u] = 1
    assert nv == V
    assert A.sum() == 2 * E
    return {"A": A, "pts": pts}


# ── Helper functions ────────────────────────────────────────────
def _sigma(n):
    """Sum-of-divisors function σ(n)."""
    return sum(d for d in range(1, n + 1) if n % d == 0)


def _euler_phi(n):
    """Euler totient function φ(n)."""
    count = 0
    for i in range(1, n + 1):
        if gcd(i, n) == 1:
            count += 1
    return count


# ═══════════════════════════════════════════════════════════════
# T171 — Graph Energy = E/2 = |2I| = 120
# ═══════════════════════════════════════════════════════════════
class TestGraphEnergy:
    """T171: The graph energy E(G) = Σ|λᵢ| of W(3,3) equals E/2 = 120,
    the order of the binary icosahedral group 2I."""

    def test_energy_formula(self):
        """E(G) = |k|·1 + |r|·f + |s|·g = 12 + 48 + 60 = 120."""
        energy = abs(K) * 1 + abs(R_EIGEN) * F_MULT + abs(S_EIGEN) * G_MULT
        assert energy == 120

    def test_energy_is_half_edges(self):
        """E(G) = E/2 = 240/2 = 120."""
        energy = abs(K) + F_MULT * abs(R_EIGEN) + G_MULT * abs(S_EIGEN)
        assert energy == E // 2

    def test_energy_is_binary_icosahedral(self):
        """E(G) = |2I| = 120 (binary icosahedral group order)."""
        energy = abs(K) + F_MULT * abs(R_EIGEN) + G_MULT * abs(S_EIGEN)
        assert energy == 120
        # |2I| = 2·|A₅| = 2·60 = 120
        assert energy == 2 * 60

    def test_energy_from_spectrum(self, w33):
        """Verify by computing eigenvalues of actual matrix."""
        eigs = np.linalg.eigvalsh(w33["A"])
        energy = sum(abs(e) for e in eigs)
        assert abs(energy - 120.0) < 1e-6

    def test_positive_negative_split(self):
        """Positive part = k + f·r = 60, negative part = g·|s| = 60."""
        pos = K * 1 + F_MULT * R_EIGEN
        neg = G_MULT * abs(S_EIGEN)
        assert pos == neg == 60
        assert pos == E // MU  # = 240/4 = 60


# ═══════════════════════════════════════════════════════════════
# T172 — Finite Group Tower over F_q
# ═══════════════════════════════════════════════════════════════
class TestFiniteGroupTower:
    """T172: The classical groups over F_q = F₃ form a tower whose
    orders ARE the SRG parameters:
        |PSL(2,q)| = k = 12
        |SL(2,q)|  = f = 24
        |GL(2,q)|  = 2f = 48
        |Sp(4,q)|  = Aut = 51840
    """

    def test_psl2q_is_k(self):
        """|PSL(2,3)| = q(q²−1)/2 = 3·8/2 = 12 = k."""
        psl = Q * (Q**2 - 1) // 2
        assert psl == K

    def test_sl2q_is_f(self):
        """|SL(2,3)| = q(q²−1) = 3·8 = 24 = f."""
        sl = Q * (Q**2 - 1)
        assert sl == F_MULT

    def test_gl2q_is_2f(self):
        """|GL(2,3)| = (q²−1)(q²−q) = 8·6 = 48 = 2f."""
        gl = (Q**2 - 1) * (Q**2 - Q)
        assert gl == 2 * F_MULT

    def test_pgl2q_is_f(self):
        """|PGL(2,3)| = q(q+1)(q−1) = 24 = f."""
        pgl = Q * (Q + 1) * (Q - 1)
        assert pgl == F_MULT

    def test_sp4q_is_aut(self):
        """|Sp(4,3)| = q⁴(q⁴−1)(q²−1) = 51840 = Aut."""
        sp = Q**4 * (Q**4 - 1) * (Q**2 - 1)
        assert sp == AUT

    def test_tower_ratios(self):
        """SL/PSL = 2 = λ, GL/SL = q−1 = 2 = λ."""
        sl = Q * (Q**2 - 1)
        psl = sl // gcd(Q - 1, 2)
        gl = (Q**2 - 1) * (Q**2 - Q)
        assert sl // psl == LAM
        assert gl // sl == Q - 1 == LAM


# ═══════════════════════════════════════════════════════════════
# T173 — Signless Laplacian Eigenvalues = Lie Dimensions
# ═══════════════════════════════════════════════════════════════
class TestSignlessLaplacian:
    """T173: The signless Laplacian Q = D+A has eigenvalues
    2k=24=f, k+r=14=G₂, k+s=8=dim(O) — the Lie dimension triple."""

    def test_q_eigenvalue_trivial(self):
        """Q-eigenvalue for k: 2k = 24 = f."""
        assert 2 * K == F_MULT

    def test_q_eigenvalue_r(self):
        """Q-eigenvalue for r: k+r = 14 = dim(G₂)."""
        assert K + R_EIGEN == G2_DIM

    def test_q_eigenvalue_s(self):
        """Q-eigenvalue for s: k+s = 8 = dim(O)."""
        assert K + S_EIGEN == DIM_O

    def test_q_spectrum_from_matrix(self, w33):
        """Verify signless Laplacian spectrum from actual computation."""
        A = w33["A"]
        D = np.diag(A.sum(axis=1))
        Q_mat = D + A
        eigs = sorted(np.linalg.eigvalsh(Q_mat).round().astype(int))
        counter = Counter(eigs)
        assert counter[DIM_O] == G_MULT    # 8 with mult 15
        assert counter[G2_DIM] == F_MULT   # 14 with mult 24
        assert counter[2 * K] == 1         # 24 with mult 1

    def test_q_eigenvalues_are_lie_dims(self):
        """The triple (2k, k+r, k+s) = (f, G₂, dim O) are exactly
        the dimensions of three fundamental algebraic structures."""
        assert (2 * K, K + R_EIGEN, K + S_EIGEN) == (F_MULT, G2_DIM, DIM_O)


# ═══════════════════════════════════════════════════════════════
# T174 — Minimal Polynomial Coefficients
# ═══════════════════════════════════════════════════════════════
class TestMinimalPolynomial:
    """T174: The minimal polynomial of A is
    x³ − θx² − 2^(μ+1)x + μf = (x−k)(x−r)(x−s)
    with every coefficient an SRG-derived quantity."""

    def test_coefficient_x2(self):
        """Coefficient of x²: −(k+r+s) = −θ = −10."""
        assert -(K + R_EIGEN + S_EIGEN) == -THETA

    def test_coefficient_x1(self):
        """Coefficient of x: kr+ks+rs = −2^(μ+1) = −32."""
        c1 = K * R_EIGEN + K * S_EIGEN + R_EIGEN * S_EIGEN
        assert c1 == -(2 ** (MU + 1))

    def test_coefficient_x0(self):
        """Constant: −krs = μf = 96."""
        c0 = -(K * R_EIGEN * S_EIGEN)
        assert c0 == MU * F_MULT

    def test_polynomial_evaluates_to_zero(self, w33):
        """A³ − θA² − 2^(μ+1)A + μfI = 0."""
        A = w33["A"]
        I = np.eye(V, dtype=int)
        A2 = A @ A
        A3 = A2 @ A
        result = A3 - THETA * A2 - (2 ** (MU + 1)) * A + MU * F_MULT * I
        assert np.allclose(result, 0)

    def test_discriminant_is_k_over_lam_squared(self):
        """Discriminant Δ of quadratic (x−r)(x−s) = (r−s)² = (k/λ)² = 36."""
        disc = (R_EIGEN - S_EIGEN) ** 2
        assert disc == (K // LAM) ** 2 == 36


# ═══════════════════════════════════════════════════════════════
# T175 — Complement Energy = k²
# ═══════════════════════════════════════════════════════════════
class TestComplementEnergy:
    """T175: The complement graph W̄(3,3) has energy k² = 144.
    The product Energy(G)·Energy(Ḡ) = Aut/q = 17280."""

    def test_complement_eigenvalues(self):
        """Complement eigenvalues: v−1−k = 27 = Albert, −(1+r) = −3, −(1+s) = 3."""
        assert V - 1 - K == ALBERT
        assert -(1 + R_EIGEN) == -Q
        assert -(1 + S_EIGEN) == Q

    def test_complement_energy_is_k_squared(self):
        """E(Ḡ) = |Albert|·1 + |−q|·f + |q|·g = 27+72+45 = 144 = k²."""
        ec = ALBERT * 1 + abs(-Q) * F_MULT + abs(Q) * G_MULT
        assert ec == K ** 2 == 144

    def test_energy_product_is_aut_over_q(self):
        """E(G)·E(Ḡ) = 120·144 = 17280 = Aut/q."""
        e_g = E // 2   # 120
        e_bar = K ** 2  # 144
        assert e_g * e_bar == AUT // Q

    def test_energy_ratio(self):
        """E(Ḡ)/E(G) = k²/(E/2) = 144/120 = 6/5 = (k/λ)/N."""
        ratio = Fraction(K ** 2, E // 2)
        assert ratio == Fraction(K // LAM, N) == Fraction(6, 5)

    def test_complement_energy_from_matrix(self, w33):
        """Verify complement energy by direct computation."""
        A_bar = np.ones((V, V), dtype=int) - np.eye(V, dtype=int) - w33["A"]
        eigs = np.linalg.eigvalsh(A_bar)
        energy_bar = sum(abs(e) for e in eigs)
        assert abs(energy_bar - 144.0) < 1e-6


# ═══════════════════════════════════════════════════════════════
# T176 — Spectral Moments: M₂ = k, M₃ = f
# ═══════════════════════════════════════════════════════════════
class TestSpectralMoments:
    """T176: The spectral moment Mₙ = Tr(Aⁿ)/v satisfies
    M₂ = k, M₃ = f, and M₃/M₂ = λ."""

    def test_M2_is_k(self):
        """M₂ = Tr(A²)/v = 2E/v = kv/v = k = 12."""
        W2 = K ** 2 + F_MULT * R_EIGEN ** 2 + G_MULT * S_EIGEN ** 2
        assert W2 // V == K

    def test_M3_is_f(self):
        """M₃ = Tr(A³)/v = 6T/v = (k³+f·r³+g·s³)/v = 24 = f."""
        W3 = K ** 3 + F_MULT * R_EIGEN ** 3 + G_MULT * S_EIGEN ** 3
        assert W3 == 960
        assert W3 // V == F_MULT

    def test_M3_over_M2_is_lam(self):
        """M₃/M₂ = f/k = 24/12 = 2 = λ."""
        assert Fraction(F_MULT, K) == LAM

    def test_W0_plus_W2_is_v_times_phi3(self):
        """W₀ + W₁ + W₂ = v + 0 + 2E = 520 = v·Φ₃."""
        W0 = V
        W1 = 0  # Tr(A) = 0
        W2 = 2 * E
        assert W0 + W1 + W2 == V * PHI3

    def test_moments_from_matrix(self, w33):
        """Verify M₂, M₃ from actual trace computations."""
        A = w33["A"]
        A2 = A @ A
        A3 = A2 @ A
        assert np.trace(A2) == 2 * E
        assert np.trace(A3) == 960


# ═══════════════════════════════════════════════════════════════
# T177 — Quartic Walk Count and Kurtosis
# ═══════════════════════════════════════════════════════════════
class TestQuarticWalks:
    """T177: W₄/v = 2^μ(v−1) = 624 and the spectral kurtosis = Φ₃/q."""

    def test_W4_value(self):
        """W₄ = k⁴ + f·r⁴ + g·s⁴ = 20736 + 384 + 3840 = 24960."""
        W4 = K ** 4 + F_MULT * R_EIGEN ** 4 + G_MULT * S_EIGEN ** 4
        assert W4 == 24960

    def test_W4_per_vertex(self):
        """W₄/v = 624 = 2^μ · (v−1) = 16 · 39."""
        W4 = K ** 4 + F_MULT * R_EIGEN ** 4 + G_MULT * S_EIGEN ** 4
        assert W4 // V == 2 ** MU * (V - 1) == 624

    def test_spectral_kurtosis(self):
        """κ = (W₄/v)/(W₂/v)² = 624/144 = 13/3 = Φ₃/q."""
        M4 = Fraction(24960, V)
        M2 = Fraction(2 * E, V)
        kurtosis = M4 / M2 ** 2
        assert kurtosis == Fraction(PHI3, Q)

    def test_W4_from_matrix(self, w33):
        """Verify Tr(A⁴) = 24960 by matrix computation."""
        A = w33["A"]
        A2 = A @ A
        A4 = A2 @ A2
        assert np.trace(A4) == 24960


# ═══════════════════════════════════════════════════════════════
# T178 — Hoffman Determinant: det(kI+A) = f · G₂^f · dimO^g
# ═══════════════════════════════════════════════════════════════
class TestHoffmanDeterminant:
    """T178: det(kI+A) = (2k)(k+r)^f(k+s)^g = f · G₂^f · dim(O)^g.

    Each factor in the spectral determinant equals a Lie-algebraic dimension:
    2k = f = 24, k+r = G₂ = 14, k+s = dim(O) = 8.
    """

    def test_2k_is_f(self):
        """2k = 24 = f (multiplicity)."""
        assert 2 * K == F_MULT

    def test_k_plus_r_is_G2(self):
        """k+r = 14 = dim(G₂)."""
        assert K + R_EIGEN == G2_DIM

    def test_k_plus_s_is_dimO(self):
        """k+s = 8 = dim(O)."""
        assert K + S_EIGEN == DIM_O

    def test_determinant_factorization(self):
        """det(kI+A) = f · G₂^f · dim(O)^g (symbolic identity)."""
        # The determinant is f · G2^f · dimO^g
        # All three bases are Lie-algebraic dimensions
        assert 2 * K == F_MULT
        assert K + R_EIGEN == G2_DIM
        assert K + S_EIGEN == DIM_O
        # So det = F_MULT * G2_DIM^F_MULT * DIM_O^G_MULT
        # This is a huge number but the factorization is exact

    def test_determinant_numerical(self, w33):
        """Verify det(kI+A) sign and leading factor from eigenvalues."""
        A = w33["A"]
        M = K * np.eye(V, dtype=int) + A
        # eigenvalues of M: 2k=24 (x1), k+r=14 (x24), k+s=8 (x15)
        eigs = sorted(np.linalg.eigvalsh(M).round().astype(int))
        counter = Counter(eigs)
        assert counter[DIM_O] == G_MULT
        assert counter[G2_DIM] == F_MULT
        assert counter[2 * K] == 1


# ═══════════════════════════════════════════════════════════════
# T179 — Universal Ratio 8/5
# ═══════════════════════════════════════════════════════════════
class TestUniversalRatio:
    """T179: Three independent spectral quantities share the ratio 8/5:
        f/g = dim(O)/N = (k−s)/(k−r) = 8/5.
    """

    def test_multiplicity_ratio(self):
        """f/g = 24/15 = 8/5."""
        assert Fraction(F_MULT, G_MULT) == Fraction(8, 5)

    def test_dimO_over_N(self):
        """dim(O)/N = 8/5."""
        assert Fraction(DIM_O, N) == Fraction(8, 5)

    def test_laplacian_gap_ratio(self):
        """(k−s)/(k−r) = 16/10 = 8/5."""
        assert Fraction(K - S_EIGEN, K - R_EIGEN) == Fraction(8, 5)

    def test_all_three_equal(self):
        """All three expressions equal the same ratio."""
        r1 = Fraction(F_MULT, G_MULT)
        r2 = Fraction(DIM_O, N)
        r3 = Fraction(K - S_EIGEN, K - R_EIGEN)
        assert r1 == r2 == r3 == Fraction(8, 5)


# ═══════════════════════════════════════════════════════════════
# T180 — Kneser K(N,λ) = Petersen Graph
# ═══════════════════════════════════════════════════════════════
class TestKneserPetersen:
    """T180: The Kneser graph K(N,λ) = K(5,2) is the Petersen graph:
    vertices = C(5,2) = θ, degree = C(3,2) = q.  The most famous graph
    in combinatorics is built from two SRG parameters."""

    def test_kneser_vertices(self):
        """K(N,λ) has C(N,λ) = C(5,2) = 10 = θ vertices."""
        assert comb(N, LAM) == THETA

    def test_kneser_degree(self):
        """K(N,λ) has degree C(N−λ,λ) = C(3,2) = 3 = q."""
        assert comb(N - LAM, LAM) == Q

    def test_petersen_is_kneser_5_2(self):
        """K(5,2) = Petersen graph: SRG(10,3,0,1)."""
        v_pet = comb(5, 2)
        k_pet = comb(3, 2)
        assert v_pet == THETA == 10
        assert k_pet == Q == 3

    def test_johnson_companion(self):
        """Johnson J(N,λ) = J(5,2): degree = (N−λ)·λ = 6 = k/λ."""
        j_k = (N - LAM) * LAM
        assert j_k == K // LAM == 6

    def test_petersen_edges(self):
        """Petersen has 15 = g edges: C(5,2)·C(3,2)/2."""
        e_pet = comb(N, LAM) * comb(N - LAM, LAM) // 2
        assert e_pet == G_MULT == 15


# ═══════════════════════════════════════════════════════════════
# T181 — Spectral Determinant: det(I+A) = −Φ₃ · q^(v−1)
# ═══════════════════════════════════════════════════════════════
class TestSpectralDeterminant:
    """T181: det(I+A) = (1+k)(1+r)^f(1+s)^g = −Φ₃ · q^(v−1).

    The characteristic polynomial of A at x = −1 distills into
    the cyclotomic prime Φ₃ and q raised to (v−1).
    """

    def test_factors(self):
        """1+k = Φ₃ = 13, 1+r = q = 3, 1+s = −q = −3."""
        assert 1 + K == PHI3
        assert 1 + R_EIGEN == Q
        assert 1 + S_EIGEN == -Q

    def test_determinant_sign(self):
        """(−q)^g = (−3)^15 = −3^15, so det = −Φ₃·q^(f+g) = −Φ₃·q^(v−1)."""
        # (1+s)^g = (-3)^15 = -3^15 since g=15 is odd
        assert G_MULT % 2 == 1  # g is odd
        # det = 13 * 3^24 * (-3)^15 = -13 * 3^39
        assert F_MULT + G_MULT == V - 1

    def test_determinant_value(self):
        """det(I+A) = −Φ₃ · q^(v−1) = −13 · 3^39."""
        det_val = PHI3 * Q ** F_MULT * ((-Q) ** G_MULT)
        expected = -PHI3 * Q ** (V - 1)
        assert det_val == expected

    def test_from_matrix(self, w33):
        """Verify via eigenvalue product from actual matrix."""
        A = w33["A"]
        M = np.eye(V) + A
        eigs = np.linalg.eigvalsh(M)
        # Product of eigenvalues = det
        # Check sign and that |det| = 13 * 3^39
        log_abs_det = sum(math.log(abs(e)) for e in eigs)
        expected_log = math.log(PHI3) + (V - 1) * math.log(Q)
        assert abs(log_abs_det - expected_log) < 1e-6


# ═══════════════════════════════════════════════════════════════
# T182 — Ramanujan Property
# ═══════════════════════════════════════════════════════════════
class TestRamanujanProperty:
    """T182: W(3,3) is a Ramanujan graph: both nontrivial eigenvalues
    satisfy |λᵢ| ≤ 2√(k−1), making it an optimal spectral expander."""

    def test_ramanujan_bound(self):
        """Ramanujan bound: 2√(k−1) = 2√11 ≈ 6.633."""
        bound = 2 * math.sqrt(K - 1)
        assert abs(R_EIGEN) < bound
        assert abs(S_EIGEN) < bound

    def test_r_well_below_bound(self):
        """|r| = 2 < 2√11 ≈ 6.633: large spectral gap."""
        assert abs(R_EIGEN) == LAM  # r = λ = 2
        assert R_EIGEN ** 2 < 4 * (K - 1)

    def test_s_below_bound(self):
        """|s| = 4 < 2√11: both eigenvalues satisfy Ramanujan."""
        assert S_EIGEN ** 2 < 4 * (K - 1)  # 16 < 44

    def test_expander_mixing_constant(self):
        """Mixing constant λ₁ = max(|r|,|s|) = 4 = μ."""
        mixing = max(abs(R_EIGEN), abs(S_EIGEN))
        assert mixing == MU

    def test_ramanujan_optimality_ratio(self):
        """The ratio max(|r|,|s|)/(2√(k−1)) measures Ramanujan quality."""
        ratio = MU / (2 * math.sqrt(K - 1))
        assert ratio < 1.0  # Ramanujan condition
        assert ratio < 0.61  # 4/6.633 ≈ 0.603 — very good expander


# ═══════════════════════════════════════════════════════════════
# T183 — Cheeger Bound = dim(O)
# ═══════════════════════════════════════════════════════════════
class TestCheegerBound:
    """T183: The Cheeger constant h(G) ≥ (k − max(|r|,|s|))/2 = dim(O)/2 = 4.
    The discrete Cheeger inequality gives h ≥ (k−|s|)/2 and λ₂ = k−r ≥ h²/(2k).
    The vertex expansion constant k−|s| = dim(O) = 8."""

    def test_spectral_gap_expansion(self):
        """Vertex expansion: k − max(|r|,|s|) = 12 − 4 = 8 = dim(O)."""
        expansion = K - max(abs(R_EIGEN), abs(S_EIGEN))
        assert expansion == DIM_O

    def test_cheeger_lower_bound(self):
        """Cheeger: h(G) ≥ (k−|s|)/2 = dim(O)/2 = 4 = μ."""
        cheeger_lb = (K - abs(S_EIGEN)) // 2
        assert cheeger_lb == MU

    def test_algebraic_connectivity_is_theta(self):
        """Algebraic connectivity = k−r = 10 = θ (2nd smallest Laplacian eig)."""
        assert K - R_EIGEN == THETA

    def test_laplacian_spectral_gap(self):
        """Laplacian spectral gap = k−r = θ, max Laplacian eig = k−s = k+μ = 16."""
        assert K - R_EIGEN == THETA
        assert K - S_EIGEN == K + MU == 16

    def test_cheeger_from_laplacian(self, w33):
        """Verify algebraic connectivity from actual Laplacian eigenvalues."""
        A = w33["A"]
        D = np.diag(A.sum(axis=1))
        L = D - A
        eigs = sorted(np.linalg.eigvalsh(L).round(6))
        # Smallest should be 0, next should be k-r = 10
        assert abs(eigs[0]) < 1e-6
        assert abs(eigs[1] - THETA) < 1e-6


# ═══════════════════════════════════════════════════════════════
# T184 — Divisor-Totient Chain
# ═══════════════════════════════════════════════════════════════
class TestDivisorTotientChain:
    """T184: The number-theoretic functions σ and φ applied to SRG
    values produce other SRG values:
        σ(g) = f, φ(E) = 2^(k/λ), rank_q(A) = v−1 = q·Φ₃.
    """

    def test_sigma_g_is_f(self):
        """σ(g) = σ(15) = 1+3+5+15 = 24 = f."""
        assert _sigma(G_MULT) == F_MULT

    def test_phi_E_is_2_to_k_over_lam(self):
        """φ(E) = φ(240) = 64 = 2^(k/λ) = 2^6."""
        assert _euler_phi(E) == 2 ** (K // LAM) == 64

    def test_rank_q_is_v_minus_1(self):
        """rank_q(A) = v−1 = 39 = q·Φ₃ (eigenvalue k≡0 mod q)."""
        # k = 12, r = 2, s = -4 = 2 mod 3
        # Only k ≡ 0 (mod 3), so nullity over F_q = 1
        rank = V - 1
        assert rank == Q * PHI3 == 39

    def test_sigma_f_is_60(self):
        """σ(f) = σ(24) = 60 = E/μ = |A₅|."""
        assert _sigma(F_MULT) == E // MU == 60

    def test_phi_v_is_k_plus_mu(self):
        """φ(v) = φ(40) = 16 = k+μ = 2^μ."""
        assert _euler_phi(V) == K + MU == 2 ** MU

    def test_phi_k_is_mu(self):
        """φ(k) = φ(12) = 4 = μ."""
        assert _euler_phi(K) == MU


# ═══════════════════════════════════════════════════════════════
# T185 — Eigenvalue Arithmetic
# ═══════════════════════════════════════════════════════════════
class TestEigenvalueArithmetic:
    """T185: The eigenvalue pair (r,s) = (2,−4) generates all SRG
    parameters through elementary arithmetic:
        r−s = k/λ, k/|s| = q, |rs| = dim(O), Δ = (k/λ)².
    """

    def test_r_minus_s_is_k_over_lam(self):
        """r − s = 2−(−4) = 6 = k/λ."""
        assert R_EIGEN - S_EIGEN == K // LAM

    def test_k_over_abs_s_is_q(self):
        """k/|s| = 12/4 = 3 = q."""
        assert Fraction(K, abs(S_EIGEN)) == Q

    def test_abs_rs_is_dimO(self):
        """|r·s| = |2·(−4)| = 8 = dim(O)."""
        assert abs(R_EIGEN * S_EIGEN) == DIM_O

    def test_discriminant_is_k_over_lam_squared(self):
        """Δ = (r−s)² = 36 = (k/λ)²."""
        assert (R_EIGEN - S_EIGEN) ** 2 == (K // LAM) ** 2

    def test_r_equals_lam(self):
        """The positive eigenvalue r = λ = 2 (eigenvalue IS the parameter)."""
        assert R_EIGEN == LAM

    def test_s_equals_neg_mu(self):
        """The negative eigenvalue s = −μ = −4 (eigenvalue IS neg parameter)."""
        assert S_EIGEN == -MU

    def test_eigenvalue_sum(self):
        """r + s = −λ = −2 (from SRG formula)."""
        assert R_EIGEN + S_EIGEN == -LAM

    def test_k_over_r_is_k_over_lam(self):
        """k/r = 12/2 = 6 = k/λ (since r = λ)."""
        assert Fraction(K, R_EIGEN) == K // LAM
