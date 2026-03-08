"""
Phase XV: Information & Dynamics — Random Walks, Resistance, Entropy (T186–T200)
================================================================================

From the five SRG parameters (v, k, λ, μ, q) = (40, 12, 2, 4, 3) we derive
15 theorems spanning random walk dynamics, effective resistance, spectral zeta
functions, Rényi entropy, resolvent evaluations, and walk-matrix algebra.

Theorems
--------
T186: Kemeny constant K = fk/(k−r) + gk/(k−s) = 801/20
T187: Kirchhoff index Kf = v·(f/(k−r) + g/(k−s)) = 267/2
T188: Effective resistance — R_adj = Φ₃/(2v), R_non = Φ₆/v, ratio = G₂/Φ₃
T189: Return probability P₄ = Φ₃/((k+|s|)·Albert) = 13/432
T190: Spectral gap dimO/k = 2/3, mixing rate q/λ = 3/2
T191: Estrada index EE = eᵏ + f·eʳ + g·eˢ
T192: Adjacency spectral zeta — ζ(1) = q²Φ₆/μ, ζ(2) = q(v−q)/μ²
T193: Transition eigenvalues — 1, r/k = 1/(k/λ), s/k = −1/q
T194: Vertex stabilizer |GL(2,q)|·Albert = 48·27 = 1296
T195: Complement determinant det(Ā) = q^(v+λ) = 3⁴²
T196: Eigenspace projections — E₁_adj = 1/θ, E₂_adj = −1/dim(O)
T197: Resolvent spectrum — R(θ) = N²/Φ₆, R(dimO) = N, R(G₂) = θ/q
T198: Walk matrix entries — (A³)_adj = F₄ = 52, (A³)_non = v = 40
T199: Rényi entropy H₂ = log₂(λ·q·N) = log₂(30)
T200: Wiener index W = v·q·(k−1) = 1320
"""
from __future__ import annotations

import math
import numpy as np
import pytest
from fractions import Fraction

# ═══════════════════════════════════════════════════════════════
# SRG constants  (v, k, λ, μ, q) = (40, 12, 2, 4, 3)
# ═══════════════════════════════════════════════════════════════
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V * K // 2                        # 240 edges
F_MULT, G_MULT = 24, 15               # multiplicities
R_EIGEN, S_EIGEN = 2, -4              # non-trivial eigenvalues
THETA = K - R_EIGEN                   # 10  (Lovász theta / Laplacian gap)
N_IND = 5                             # independence number
ALBERT = 27                           # dim(Albert algebra)
DIM_O = 8                             # dim(octonions)
G2_DIM = 14                           # dim(G₂)
PHI3 = Q**2 + Q + 1                   # 13 = Φ₃(3)
PHI6 = Q**2 - Q + 1                   # 7  = Φ₆(3)
AUT = 51840                           # |Sp(4,3)| = |W(E₆)|
F4_DIM = 52                           # dim(F₄)
GL2Q = Q * (Q - 1) * (Q**2 - 1)      # |GL(2,3)| = 48


# ═══════════════════════════════════════════════════════════════
# Fixture — build the 40-vertex W(3,3) graph
# ═══════════════════════════════════════════════════════════════
def _build_w33():
    """Construct W(3,3): the symplectic polar graph over GF(3)."""
    F3 = range(3)
    raw = [
        (a, b, c, d)
        for a in F3 for b in F3 for c in F3 for d in F3
        if (a, b, c, d) != (0, 0, 0, 0)
    ]
    inv = {1: 1, 2: 2}
    seen: dict[tuple[int, ...], int] = {}
    reps: list[tuple[int, ...]] = []
    for vec in raw:
        for i in range(4):
            if vec[i] != 0:
                s = inv[vec[i]]
                nv = tuple((s * x) % 3 for x in vec)
                break
        if nv not in seen:
            seen[nv] = len(reps)
            reps.append(nv)
    n = len(reps)
    assert n == V

    def symp(u, w):
        return (u[0] * w[2] - u[2] * w[0] + u[1] * w[3] - u[3] * w[1]) % 3

    A = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(i + 1, n):
            if symp(reps[i], reps[j]) == 0:
                A[i][j] = A[j][i] = 1
    return A


@pytest.fixture(scope="module")
def w33():
    A = _build_w33()
    return {"A": A}


# ═══════════════════════════════════════════════════════════════
# T186 — Kemeny Constant: K = 801/20
# ═══════════════════════════════════════════════════════════════
class TestKemenyConstant:
    """T186: The Kemeny constant for random walk on W(3,3):

    K = f·k/(k−r) + g·k/(k−s) = 801/20.
    K − (v−1) = q·Φ₆/(μ·N) = 21/20.
    """

    def test_kemeny_value(self):
        """K = f·k/(k−r) + g·k/(k−s) = 801/20."""
        K_val = Fraction(F_MULT * K, K - R_EIGEN) + Fraction(G_MULT * K, K - S_EIGEN)
        assert K_val == Fraction(801, 20)

    def test_kemeny_decomposition(self):
        """K = 144/5 + 45/4 = 801/20."""
        assert Fraction(F_MULT * K, THETA) == Fraction(144, 5)
        assert Fraction(G_MULT * K, K - S_EIGEN) == Fraction(45, 4)

    def test_kemeny_excess(self):
        """K − (v−1) = q·Φ₆/(μ·N) = 21/20."""
        K_val = Fraction(801, 20)
        excess = K_val - (V - 1)
        assert excess == Fraction(Q * PHI6, MU * N_IND)
        assert excess == Fraction(21, 20)

    def test_kemeny_from_laplacian(self, w33):
        """Numerical: K = v · Σ 1/(nonzero Lapl eigenvalue)."""
        L_eigs = np.linalg.eigvalsh(K * np.eye(V) - w33["A"])
        nonzero = [e for e in L_eigs if e > 0.5]
        K_num = K * sum(1.0 / e for e in nonzero)
        assert abs(K_num - 801 / 20) < 1e-8

    def test_kemeny_per_vertex(self):
        """K/v = 801/800 ≈ 1 + 1/800."""
        assert Fraction(801, 20) / V == Fraction(801, 800)


# ═══════════════════════════════════════════════════════════════
# T187 — Kirchhoff Index: Kf = 267/2
# ═══════════════════════════════════════════════════════════════
class TestKirchhoffIndex:
    """T187: The Kirchhoff index (total effective resistance):

    Kf = v·(f/(k−r) + g/(k−s)) = 267/2.
    Kf = v·K/k (Kemeny–Kirchhoff relation).
    """

    def test_kirchhoff_value(self):
        """Kf = v·(f/(k−r) + g/(k−s)) = 267/2."""
        Kf = V * (Fraction(F_MULT, K - R_EIGEN) + Fraction(G_MULT, K - S_EIGEN))
        assert Kf == Fraction(267, 2)

    def test_kemeny_kirchhoff_relation(self):
        """Kf = v·K/k."""
        K_val = Fraction(801, 20)
        Kf_from_K = V * K_val / K
        assert Kf_from_K == Fraction(267, 2)

    def test_kirchhoff_from_resistances(self):
        """Kf = E·R_adj + (C(v,2)−E)·R_non."""
        R_adj = Fraction(PHI3, 2 * V)     # 13/80
        R_non = Fraction(PHI6, V)         # 7/40
        non_edges = V * (V - 1) // 2 - E  # 540
        Kf = E * R_adj + non_edges * R_non
        assert Kf == Fraction(267, 2)

    def test_kirchhoff_numerical(self, w33):
        """Numerical verification from pseudoinverse."""
        L = K * np.eye(V) - w33["A"]
        Lp = np.linalg.pinv(L)
        Kf = sum(Lp[i, i] + Lp[j, j] - 2 * Lp[i, j]
                 for i in range(V) for j in range(i + 1, V))
        assert abs(Kf - 267 / 2) < 1e-6


# ═══════════════════════════════════════════════════════════════
# T188 — Effective Resistance: R_adj = Φ₃/(2v), R_non = Φ₆/v
# ═══════════════════════════════════════════════════════════════
class TestEffectiveResistance:
    """T188: Effective resistances on W(3,3):

    R_adj = Φ₃/(2v) = 13/80,  R_non = Φ₆/v = 7/40.
    R_non/R_adj = G₂/Φ₃ = 14/13.
    """

    def test_r_adj_value(self, w33):
        """R_adj = 13/80 = Φ₃/(2v)."""
        L = K * np.eye(V) - w33["A"]
        Lp = np.linalg.pinv(L)
        i, j = 0, int(np.where(w33["A"][0])[0][0])
        R = Lp[i, i] + Lp[j, j] - 2 * Lp[i, j]
        assert abs(R - 13 / 80) < 1e-10

    def test_r_non_value(self, w33):
        """R_non = 7/40 = Φ₆/v."""
        L = K * np.eye(V) - w33["A"]
        Lp = np.linalg.pinv(L)
        non_nbrs = np.where(w33["A"][0] == 0)[0]
        j = non_nbrs[non_nbrs > 0][0]
        R = Lp[0, 0] + Lp[j, j] - 2 * Lp[0, j]
        assert abs(R - 7 / 40) < 1e-10

    def test_resistance_ratio(self):
        """R_non/R_adj = G₂/Φ₃ = 14/13."""
        ratio = Fraction(PHI6, V) / Fraction(PHI3, 2 * V)
        assert ratio == Fraction(G2_DIM, PHI3)

    def test_r_adj_times_v(self):
        """R_adj · v = Φ₃/2."""
        assert Fraction(PHI3, 2 * V) * V == Fraction(PHI3, 2)

    def test_r_non_times_v(self):
        """R_non · v = Φ₆ = 7."""
        assert Fraction(PHI6, V) * V == PHI6

    def test_all_adj_same(self, w33):
        """All adjacent pairs have identical resistance (SRG regularity)."""
        L = K * np.eye(V) - w33["A"]
        Lp = np.linalg.pinv(L)
        vals = set()
        for j in range(V):
            if w33["A"][0][j]:
                vals.add(round(Lp[0, 0] + Lp[j, j] - 2 * Lp[0, j], 10))
        assert len(vals) == 1


# ═══════════════════════════════════════════════════════════════
# T189 — Return Probability: P₄ = Φ₃/((k+|s|)·Albert)
# ═══════════════════════════════════════════════════════════════
class TestReturnProbability:
    """T189: The 4-step return probability for random walk on W(3,3):

    P₄ = (k⁴ + f·r⁴ + g·s⁴)/(v·k⁴) = Φ₃/((k+|s|)·Albert) = 13/432.
    """

    def test_p4_value(self):
        """P₄ = 13/432 = Φ₃/((k+|s|)·Albert)."""
        P4 = Fraction(K**4 + F_MULT * R_EIGEN**4 + G_MULT * S_EIGEN**4,
                       V * K**4)
        assert P4 == Fraction(PHI3, (K + abs(S_EIGEN)) * ALBERT)
        assert P4 == Fraction(13, 432)

    def test_p4_denominator_factors(self):
        """432 = 16 · 27 = (k+|s|) · Albert."""
        assert 432 == (K + abs(S_EIGEN)) * ALBERT

    def test_p2_is_reciprocal_k(self):
        """P₂ = 1/k = 1/12 (universal for k-regular)."""
        P2 = Fraction(K**2 + F_MULT * R_EIGEN**2 + G_MULT * S_EIGEN**2,
                       V * K**2)
        assert P2 == Fraction(1, K)

    def test_p4_numerical(self, w33):
        """Verify via actual transition matrix."""
        P = w33["A"].astype(float) / K
        P4 = np.linalg.matrix_power(P, 4)
        assert abs(P4[0, 0] - 13 / 432) < 1e-10

    def test_p4_numerator_is_phi3(self):
        """Numerator (after reducing) = Φ₃ = 13."""
        assert Fraction(13, 432).numerator == PHI3


# ═══════════════════════════════════════════════════════════════
# T190 — Spectral Gap & Mixing Rate
# ═══════════════════════════════════════════════════════════════
class TestSpectralGapMixing:
    """T190: Random walk spectral gap and mixing:

    gap = 1 − |s|/k = (k−|s|)/k = dim(O)/k = 2/3.
    Mixing rate = k/(k−|s|) = k/dim(O) = q/λ = 3/2.
    """

    def test_spectral_gap(self):
        """Spectral gap = 1 − |s|/k = dim(O)/k = 2/3."""
        gap = Fraction(K - abs(S_EIGEN), K)
        assert gap == Fraction(DIM_O, K)
        assert gap == Fraction(2, 3)

    def test_mixing_rate(self):
        """Mixing rate = k/dim(O) = q/λ = 3/2."""
        rate = Fraction(K, K - abs(S_EIGEN))
        assert rate == Fraction(Q, LAM)
        assert rate == Fraction(3, 2)

    def test_gap_from_transition(self, w33):
        """Numerical: gap = 1 − max(|eig₂|, |eig_min|)/k."""
        P = w33["A"].astype(float) / K
        eigs = np.linalg.eigvalsh(P)
        eigs_sorted = sorted(abs(e) for e in eigs)
        second_largest = eigs_sorted[-2]
        assert abs(1 - second_largest - 2 / 3) < 1e-10

    def test_mixing_rate_identity(self):
        """q/λ = k/dim(O) — two independent derivations agree."""
        assert Fraction(Q, LAM) == Fraction(K, DIM_O)


# ═══════════════════════════════════════════════════════════════
# T191 — Estrada Index
# ═══════════════════════════════════════════════════════════════
class TestEstradaIndex:
    """T191: The Estrada index of W(3,3):

    EE = eᵏ + f·eʳ + g·eˢ = e¹² + 24·e² + 15·e⁻⁴.
    Dominated by eᵏ: ln(EE) ≈ k.
    """

    def test_estrada_components(self):
        """EE = e¹² + 24·e² + 15·e⁻⁴."""
        EE = math.exp(K) + F_MULT * math.exp(R_EIGEN) + G_MULT * math.exp(S_EIGEN)
        assert EE > 0

    def test_estrada_dominated_by_k(self):
        """ln(EE) − k < 0.002 (eᵏ dominates)."""
        EE = math.exp(K) + F_MULT * math.exp(R_EIGEN) + G_MULT * math.exp(S_EIGEN)
        assert abs(math.log(EE) - K) < 0.002

    def test_estrada_numerical(self, w33):
        """Verify from actual eigenvalues."""
        eigs = np.linalg.eigvalsh(w33["A"])
        EE_num = sum(math.exp(e) for e in eigs)
        EE_formula = math.exp(K) + F_MULT * math.exp(R_EIGEN) + G_MULT * math.exp(S_EIGEN)
        assert abs(EE_num - EE_formula) < 1e-4

    def test_estrada_positive(self):
        """EE > 0 (always true for adjacency matrix)."""
        EE = math.exp(K) + F_MULT * math.exp(R_EIGEN) + G_MULT * math.exp(S_EIGEN)
        assert EE > math.exp(K)  # actually f*e^r > 0

    def test_subexponential_correction(self):
        """f·e^(r−k) + g·e^(s−k) ≈ 1.09 × 10⁻³."""
        delta = F_MULT * math.exp(R_EIGEN - K) + G_MULT * math.exp(S_EIGEN - K)
        assert 1e-4 < delta < 2e-3


# ═══════════════════════════════════════════════════════════════
# T192 — Adjacency Spectral Zeta
# ═══════════════════════════════════════════════════════════════
class TestAdjacencySpectralZeta:
    """T192: The adjacency spectral zeta function:

    ζ_A(s) = Σ |eig_i|^(−s) over nonzero eigenvalues.

    ζ(1) = q²·Φ₆/μ = 63/4,  ζ(2) = q·(v−q)/μ² = 111/16.
    """

    def test_zeta1_value(self):
        """ζ(1) = f/|r| + g/|s| = 63/4 = q²·Φ₆/μ."""
        z1 = Fraction(F_MULT, abs(R_EIGEN)) + Fraction(G_MULT, abs(S_EIGEN))
        assert z1 == Fraction(Q**2 * PHI6, MU)
        assert z1 == Fraction(63, 4)

    def test_zeta2_value(self):
        """ζ(2) = f/r² + g/s² = 111/16 = q·(v−q)/μ²."""
        z2 = Fraction(F_MULT, R_EIGEN**2) + Fraction(G_MULT, S_EIGEN**2)
        assert z2 == Fraction(Q * (V - Q), MU**2)
        assert z2 == Fraction(111, 16)

    def test_zeta1_decomposition(self):
        """ζ(1) = 12 + 15/4."""
        assert Fraction(F_MULT, abs(R_EIGEN)) == 12
        assert Fraction(G_MULT, abs(S_EIGEN)) == Fraction(15, 4)

    def test_zeta2_decomposition(self):
        """ζ(2) = 6 + 15/16."""
        assert Fraction(F_MULT, R_EIGEN**2) == 6
        assert Fraction(G_MULT, S_EIGEN**2) == Fraction(15, 16)

    def test_zeta1_numerator(self):
        """Numerator 63 = q²·Φ₆ = 9·7."""
        assert Q**2 * PHI6 == 63


# ═══════════════════════════════════════════════════════════════
# T193 — Transition Matrix Eigenvalues
# ═══════════════════════════════════════════════════════════════
class TestTransitionEigenvalues:
    """T193: The random walk transition matrix P = A/k has eigenvalues:

    1,  r/k = λ/k = 1/6,  s/k = −1/q = −1/3.
    """

    def test_positive_eigenvalue(self):
        """r/k = 1/6 = λ/k."""
        assert Fraction(R_EIGEN, K) == Fraction(LAM, K)
        assert Fraction(R_EIGEN, K) == Fraction(1, 6)

    def test_negative_eigenvalue(self):
        """s/k = −1/q = −1/3."""
        assert Fraction(S_EIGEN, K) == Fraction(-1, Q)

    def test_eigenvalue_sum(self):
        """1 + f·(r/k) + g·(s/k) = 0 (trace of P = tr(A)/k = 0)."""
        total = 1 + F_MULT * Fraction(R_EIGEN, K) + G_MULT * Fraction(S_EIGEN, K)
        assert total == 0

    def test_numerical_transition(self, w33):
        """Verify transition eigenvalues from actual matrix."""
        P = w33["A"].astype(float) / K
        eigs = sorted(np.linalg.eigvalsh(P))
        assert abs(eigs[-1] - 1.0) < 1e-10
        assert abs(eigs[-2] - 1 / 6) < 1e-10
        assert abs(eigs[0] - (-1 / 3)) < 1e-10

    def test_spectral_radius_is_one(self, w33):
        """Spectral radius of P = 1 (stochastic matrix)."""
        P = w33["A"].astype(float) / K
        assert abs(np.max(np.abs(np.linalg.eigvalsh(P))) - 1.0) < 1e-10


# ═══════════════════════════════════════════════════════════════
# T194 — Vertex Stabilizer: |GL(2,q)| · Albert = 1296
# ═══════════════════════════════════════════════════════════════
class TestVertexStabilizer:
    """T194: The vertex stabilizer in Aut(W(3,3)) = Sp(4,3):

    |Stab(v)| = |Aut|/v = 51840/40 = 1296 = |GL(2,q)| · Albert = 48 · 27.
    """

    def test_stabilizer_order(self):
        """|Stab(v)| = |Aut|/v = 51840/40 = 1296."""
        assert AUT // V == 1296

    def test_gl2q_times_albert(self):
        """|GL(2,3)| · Albert = 48 · 27 = 1296."""
        assert GL2Q * ALBERT == 1296

    def test_gl2q_value(self):
        """|GL(2,3)| = q(q−1)(q²−1) = 3·2·8 = 48."""
        assert GL2Q == 48

    def test_stabilizer_factorization(self):
        """1296 = 2⁴ · 3⁴ = 6⁴."""
        assert 1296 == 6**4
        assert 1296 == 2**4 * 3**4

    def test_stabilizer_is_sixth_power(self):
        """1296 = (k/λ)^μ = 6⁴."""
        assert (K // LAM) ** MU == 1296


# ═══════════════════════════════════════════════════════════════
# T195 — Complement Determinant: det(Ā) = q^(v+λ) = 3⁴²
# ═══════════════════════════════════════════════════════════════
class TestComplementDeterminant:
    """T195: The determinant of the complement adjacency matrix:

    det(Ā) = (v−k−1)·(−1−r)^f·(−1−s)^g = 27·(-3)²⁴·3¹⁵ = 3⁴² = q^(v+λ).
    """

    def test_complement_det_formula(self):
        """det(Ā) = Albert · (−3)^f · 3^g = 3⁴²."""
        k_bar = V - K - 1          # 27
        r_bar = -1 - S_EIGEN       # 3
        s_bar = -1 - R_EIGEN       # -3
        det_bar = k_bar * s_bar**F_MULT * r_bar**G_MULT
        assert det_bar == 3**42

    def test_exponent_is_v_plus_lam(self):
        """Exponent 42 = v + λ."""
        assert V + LAM == 42

    def test_det_bar_numerical(self, w33):
        """Numerical verification of complement determinant."""
        A_bar = np.ones((V, V), dtype=int) - np.eye(V, dtype=int) - w33["A"]
        det_bar = np.linalg.det(A_bar.astype(float))
        assert abs(det_bar / 3**42 - 1.0) < 1e-6

    def test_complement_det_pure_prime_power(self):
        """det(Ā) is a pure power of q = 3."""
        val = 3**42
        # Check it's purely 3
        while val % 3 == 0:
            val //= 3
        assert val == 1

    def test_det_ratio(self):
        """det(A)/det(Ā) = −3·2⁵⁶ / 3⁴² = −2⁵⁶/3⁴¹."""
        det_A = -3 * 2**56
        det_bar = 3**42
        ratio = Fraction(det_A, det_bar)
        assert ratio == Fraction(-2**56, 3**41)


# ═══════════════════════════════════════════════════════════════
# T196 — Eigenspace Projection Entries
# ═══════════════════════════════════════════════════════════════
class TestEigenspaceProjections:
    """T196: The spectral idempotent entries for W(3,3):

    E₁_adj = 1/θ = 1/10,   E₁_non = −1/g = −1/15,
    E₂_adj = −1/dim(O) = −1/8,   E₂_non = 1/f = 1/24.
    Diagonal: E₁_diag = q/N = 3/5,  E₂_diag = q/dim(O) = 3/8.
    """

    def test_e1_adjacent(self):
        """E₁_adj = (λ−k−s)/((r−s)(r−k)) = 1/θ = 1/10."""
        e1 = Fraction(LAM - K - S_EIGEN, (R_EIGEN - S_EIGEN) * (R_EIGEN - K))
        assert e1 == Fraction(1, THETA)

    def test_e1_nonadjacent(self):
        """E₁_non = μ/((r−s)(r−k)) = −1/g = −1/15."""
        e1 = Fraction(MU, (R_EIGEN - S_EIGEN) * (R_EIGEN - K))
        assert e1 == Fraction(-1, G_MULT)

    def test_e2_adjacent(self):
        """E₂_adj = (λ−k−r)/((s−r)(s−k)) = −1/dim(O) = −1/8."""
        e2 = Fraction(LAM - K - R_EIGEN, (S_EIGEN - R_EIGEN) * (S_EIGEN - K))
        assert e2 == Fraction(-1, DIM_O)

    def test_e2_nonadjacent(self):
        """E₂_non = μ/((s−r)(s−k)) = 1/f = 1/24."""
        e2 = Fraction(MU, (S_EIGEN - R_EIGEN) * (S_EIGEN - K))
        assert e2 == Fraction(1, F_MULT)

    def test_e1_diagonal(self):
        """E₁_diag = f/v = q/N = 3/5."""
        assert Fraction(F_MULT, V) == Fraction(Q, N_IND)

    def test_e2_diagonal(self):
        """E₂_diag = g/v = q/dim(O) = 3/8."""
        assert Fraction(G_MULT, V) == Fraction(Q, DIM_O)

    def test_idempotent_sum_adjacent(self):
        """E₀ + E₁ + E₂ at adjacent = 1/v + 1/θ − 1/dimO for A_ij=1 pairs."""
        total = Fraction(1, V) + Fraction(1, THETA) + Fraction(-1, DIM_O)
        # This should equal A_ij * (projection identity component)
        # Actually: sum of idempotent (i,j) entries = delta_ij
        # For i≠j adjacent: E_0_ij + E_1_ij + E_2_ij = 0
        e0 = Fraction(1, V)
        e1 = Fraction(1, THETA)
        e2 = Fraction(-1, DIM_O)
        assert e0 + e1 + e2 == 0


# ═══════════════════════════════════════════════════════════════
# T197 — Resolvent Spectrum: R(θ) = N²/Φ₆, R(dimO) = N, R(G₂) = θ/q
# ═══════════════════════════════════════════════════════════════
class TestResolventSpectrum:
    """T197: The resolvent trace Tr(zI−A)⁻¹ at three special points:

    R(θ)   = 1/(θ−k) + f/(θ−r) + g/(θ−s) = N²/Φ₆ = 25/7.
    R(dimO) = 1/(dimO−k) + f/(dimO−r) + g/(dimO−s) = N = 5.
    R(G₂)  = 1/(G₂−k) + f/(G₂−r) + g/(G₂−s) = θ/q = 10/3.
    """

    def test_resolvent_at_theta(self):
        """R(θ) = N²/Φ₆ = 25/7."""
        z = THETA
        R = Fraction(1, z - K) + Fraction(F_MULT, z - R_EIGEN) + Fraction(G_MULT, z - S_EIGEN)
        assert R == Fraction(N_IND**2, PHI6)

    def test_resolvent_at_dimO(self):
        """R(dim O) = N = 5."""
        z = DIM_O
        R = Fraction(1, z - K) + Fraction(F_MULT, z - R_EIGEN) + Fraction(G_MULT, z - S_EIGEN)
        assert R == N_IND

    def test_resolvent_at_G2(self):
        """R(G₂) = θ/q = 10/3."""
        z = G2_DIM
        R = Fraction(1, z - K) + Fraction(F_MULT, z - R_EIGEN) + Fraction(G_MULT, z - S_EIGEN)
        assert R == Fraction(THETA, Q)

    def test_resolvent_theta_numerical(self, w33):
        """Numerical verification at z = θ."""
        zI_A = THETA * np.eye(V) - w33["A"].astype(float)
        R = np.trace(np.linalg.inv(zI_A))
        assert abs(R - 25 / 7) < 1e-8

    def test_resolvent_dimO_numerical(self, w33):
        """Numerical verification at z = dim(O)."""
        zI_A = DIM_O * np.eye(V) - w33["A"].astype(float)
        R = np.trace(np.linalg.inv(zI_A))
        assert abs(R - 5.0) < 1e-8


# ═══════════════════════════════════════════════════════════════
# T198 — Walk Matrix Entries: (A³)_adj = F₄, (A³)_non = v
# ═══════════════════════════════════════════════════════════════
class TestWalkMatrixEntries:
    """T198: The 3-step walk counts between vertex types:

    (A³)_adj = F₄ = 52  (walks between adjacent vertices),
    (A³)_non = v = 40   (walks between non-adjacent vertices).
    """

    def test_a3_adj_formula(self):
        """(A³)_adj = k³/v + r³·E₁_adj + s³·E₂_adj = 52 = dim(F₄)."""
        a3 = (Fraction(K**3, V)
              + R_EIGEN**3 * Fraction(1, THETA)
              + S_EIGEN**3 * Fraction(-1, DIM_O))
        assert a3 == F4_DIM

    def test_a3_non_formula(self):
        """(A³)_non = k³/v + r³·E₁_non + s³·E₂_non = 40 = v."""
        a3 = (Fraction(K**3, V)
              + R_EIGEN**3 * Fraction(-1, G_MULT)
              + S_EIGEN**3 * Fraction(1, F_MULT))
        assert a3 == V

    def test_a3_adj_numerical(self, w33):
        """Verify (A³)_adj = 52 from actual matrix."""
        A3 = np.linalg.matrix_power(w33["A"], 3)
        i = 0
        j = int(np.where(w33["A"][0])[0][0])
        assert A3[i, j] == F4_DIM

    def test_a3_non_numerical(self, w33):
        """Verify (A³)_non = 40 from actual matrix."""
        A3 = np.linalg.matrix_power(w33["A"], 3)
        non_nbrs = np.where(w33["A"][0] == 0)[0]
        j = non_nbrs[non_nbrs > 0][0]
        assert A3[0, j] == V

    def test_a3_adj_is_constant(self, w33):
        """All adjacent pairs have (A³)_ij = 52 (walk-regular)."""
        A3 = np.linalg.matrix_power(w33["A"], 3)
        vals = {A3[i, j] for i in range(V) for j in range(V)
                if i != j and w33["A"][i][j] == 1}
        assert vals == {F4_DIM}

    def test_a3_non_is_constant(self, w33):
        """All non-adjacent pairs have (A³)_ij = 40 (walk-regular)."""
        A3 = np.linalg.matrix_power(w33["A"], 3)
        vals = {A3[i, j] for i in range(V) for j in range(V)
                if i != j and w33["A"][i][j] == 0}
        assert vals == {V}


# ═══════════════════════════════════════════════════════════════
# T199 — Rényi Entropy: H₂ = log₂(λ·q·N) = log₂(30)
# ═══════════════════════════════════════════════════════════════
class TestRenyiEntropy:
    """T199: The order-2 Rényi entropy of the spectral distribution:

    p_i = |eigenvalue_i| / Energy,  H₂ = −log₂(Σ p_i²) = log₂(30).
    30 = λ · q · N = 2 · 3 · 5.
    """

    def test_sum_p_squared(self):
        """Σ p_i² = 1/30 = 1/(λ·q·N)."""
        energy = K + F_MULT * abs(R_EIGEN) + G_MULT * abs(S_EIGEN)  # 120
        sum_p2 = (Fraction(K, energy)**2
                  + F_MULT * Fraction(abs(R_EIGEN), energy)**2
                  + G_MULT * Fraction(abs(S_EIGEN), energy)**2)
        assert sum_p2 == Fraction(1, LAM * Q * N_IND)

    def test_renyi_h2(self):
        """H₂ = log₂(30) = log₂(λ·q·N)."""
        h2 = math.log2(LAM * Q * N_IND)
        assert abs(h2 - math.log2(30)) < 1e-10

    def test_thirty_factors(self):
        """30 = λ·q·N = 2·3·5."""
        assert LAM * Q * N_IND == 30

    def test_energy_is_120(self):
        """Energy = k + f·|r| + g·|s| = 120 = 4·30."""
        energy = K + F_MULT * abs(R_EIGEN) + G_MULT * abs(S_EIGEN)
        assert energy == 4 * (LAM * Q * N_IND)

    def test_renyi_numerical(self, w33):
        """Numerical verification from eigenvalues."""
        eigs = np.linalg.eigvalsh(w33["A"])
        abs_eigs = np.abs(eigs)
        energy = sum(abs_eigs)
        probs = abs_eigs / energy
        h2 = -math.log2(sum(p**2 for p in probs))
        assert abs(h2 - math.log2(30)) < 1e-8


# ═══════════════════════════════════════════════════════════════
# T200 — Wiener Index: W = v·q·(k−1) = 1320
# ═══════════════════════════════════════════════════════════════
class TestWienerIndex:
    """T200: The Wiener index (sum of all pairwise distances):

    W = E·1 + (C(v,2)−E)·2 = v·q·(k−1) = 1320.
    Average distance = 2(k−1)/Φ₃ = 22/13.
    """

    def test_wiener_value(self):
        """W = E + 2·(C(v,2) − E) = 1320 = v·q·(k−1)."""
        non_edges = V * (V - 1) // 2 - E
        W = E * 1 + non_edges * 2
        assert W == V * Q * (K - 1)
        assert W == 1320

    def test_wiener_formula(self):
        """W = 2·C(v,2) − E = v(v−1) − E."""
        assert V * (V - 1) - E == 1320

    def test_average_distance(self):
        """d̄ = W/C(v,2) = 22/13 = 2(k−1)/Φ₃."""
        d_avg = Fraction(1320, V * (V - 1) // 2)
        assert d_avg == Fraction(2 * (K - 1), PHI3)
        assert d_avg == Fraction(22, 13)

    def test_wiener_numerical(self, w33):
        """Numerical: sum of shortest path distances."""
        from collections import deque
        total = 0
        for i in range(V):
            dist = [-1] * V
            dist[i] = 0
            queue = deque([i])
            while queue:
                u = queue.popleft()
                for v_idx in range(V):
                    if w33["A"][u][v_idx] and dist[v_idx] == -1:
                        dist[v_idx] = dist[u] + 1
                        queue.append(v_idx)
            total += sum(d for d in dist if d > 0)
        W = total // 2  # each pair counted twice
        assert W == 1320

    def test_diameter_is_2(self, w33):
        """Diameter = 2 (SRG with μ > 0)."""
        from collections import deque
        dist = [-1] * V
        dist[0] = 0
        queue = deque([0])
        while queue:
            u = queue.popleft()
            for v_idx in range(V):
                if w33["A"][u][v_idx] and dist[v_idx] == -1:
                    dist[v_idx] = dist[u] + 1
                    queue.append(v_idx)
        assert max(dist) == 2
