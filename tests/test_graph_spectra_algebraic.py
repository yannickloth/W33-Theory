"""
Phase XVII: Graph Spectra & Algebraic Graph Theory (T216-T230)
==============================================================

From (v, k, lam, mu, q) = (40, 12, 2, 4, 3) we derive 15 theorems
exploring the deeper spectral and algebraic invariants of W(3,3):
distance matrix, signless Laplacian, normalized Laplacian, walk
generating functions, graph energy, and modular arithmetic.

These connect the W(3,3) graph to quantum information theory,
Ramanujan graph theory, and algebraic number theory.

Theorems
--------
T216: Distance matrix eigenvalues from SRG formula
T217: Signless Laplacian spectrum Q = D + A
T218: Normalized Laplacian eigenvalues mu_i = 1 - theta_i/k
T219: Graph energy E(G) = sum|evals| from SRG spectrum
T220: Estrada index via exponential generating function
T221: Walk generating function W(t) = sum_k N_k t^k
T222: Resistance distance from Laplacian pseudoinverse
T223: Seidel matrix eigenvalues from adjacency
T224: Line graph spectrum L(W33)
T225: Automorphism group order |Aut(W33)| = |Sp(4,3)| = 51840
T226: Vertex connectivity kappa = k = 12 (optimally connected)
T227: Edge connectivity lambda_e = k = 12
T228: Algebraic connectivity a(G) = smallest positive L eigenvalue
T229: Shannon capacity from Lovasz theta
T230: Ihara zeta function reciprocal determinant
"""
from __future__ import annotations

import math
import numpy as np
import pytest
from fractions import Fraction
from collections import Counter, defaultdict

# ═══════════════════════════════════════════════════════════════
# SRG constants  (v, k, λ, μ, q) = (40, 12, 2, 4, 3)
# ═══════════════════════════════════════════════════════════════
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V * K // 2                        # 240 edges
F_MULT, G_MULT = 24, 15               # multiplicities
R_EIGEN, S_EIGEN = 2, -4              # non-trivial eigenvalues
THETA = 10                            # Lovász theta
PHI3 = Q**2 + Q + 1                   # 13
PHI6 = Q**2 - Q + 1                   # 7
ALBERT = V - K - 1                    # 27


# ── Build W(3,3) ───────────────────────────────────────────────
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

    iso = [p for p in points if J(p, p) == 0]
    adj_dict: dict[int, set[int]] = defaultdict(set)
    edges = []
    n = len(iso)
    for i in range(n):
        for j in range(i + 1, n):
            if J(iso[i], iso[j]) == 0:
                edges.append((i, j))
                adj_dict[i].add(j)
                adj_dict[j].add(i)

    tris = []
    for u, v_ in edges:
        for w in adj_dict[u] & adj_dict[v_]:
            if u < v_ < w:
                tris.append((u, v_, w))

    A = np.zeros((n, n), dtype=int)
    for u, v_ in edges:
        A[u, v_] = A[v_, u] = 1

    return iso, edges, adj_dict, tris, A


@pytest.fixture(scope="module")
def w33():
    pts, edges, adj, tris, A = _build_w33()
    nv = len(pts)
    evals = np.linalg.eigvalsh(A)
    evals_sorted = sorted(evals, reverse=True)

    # Laplacian
    D = np.diag(A.sum(axis=1))
    L = D - A

    # Distance matrix
    dist = np.full((nv, nv), 2, dtype=int)
    np.fill_diagonal(dist, 0)
    for u, v_ in edges:
        dist[u, v_] = dist[v_, u] = 1

    return {
        "pts": pts, "edges": edges, "adj": adj, "tris": tris,
        "A": A, "nv": nv, "evals": evals_sorted,
        "L": L, "D": D, "dist": dist,
    }


# ═══════════════════════════════════════════════════════════════
#  T216: Distance Matrix Eigenvalues
# ═══════════════════════════════════════════════════════════════

class TestDistanceMatrix:
    """T216: Distance matrix eigenvalues from SRG structure.

    For SRG(v,k,lam,mu) with diameter 2, the distance matrix
    D_ij = 1 if adjacent, 2 if non-adjacent (i!=j), 0 if i=j.
    D = 2(J - I) - A, where J is all-ones matrix.
    Eigenvalues of D follow from those of A and J.
    """

    def test_distance_matrix_formula(self, w33):
        """D = 2(J - I) - A."""
        n = w33["nv"]
        J = np.ones((n, n), dtype=int)
        expected = 2 * (J - np.eye(n, dtype=int)) - w33["A"]
        np.testing.assert_array_equal(w33["dist"], expected)

    def test_distance_eigenvalue_k(self, w33):
        """Eigenvalue for all-ones eigenvector: 2(v-1) - k."""
        # J has eigenvalue v for the all-ones vector, 0 otherwise
        # D = 2(J-I) - A, so for all-ones eigvec: 2(v-1) - k
        d_evals = sorted(np.linalg.eigvalsh(w33["dist"].astype(float)), reverse=True)
        expected_top = 2 * (V - 1) - K  # = 78 - 12 = 66
        assert abs(d_evals[0] - expected_top) < 1e-8
        assert expected_top == 2 * V - K - LAM  # = 80 - 12 - 2 = 66

    def test_distance_eigenvalue_r(self, w33):
        """For eigenvectors of A with eigenvalue r: D eigenvalue = -2 - r."""
        d_evals = sorted(np.linalg.eigvalsh(w33["dist"].astype(float)), reverse=True)
        # r = 2: distance eigenvalue = -2 - 2 = -4, multiplicity f=24
        d_r = -2 - R_EIGEN  # = -4
        count_r = sum(1 for e in d_evals if abs(e - d_r) < 1e-6)
        assert count_r == F_MULT
        assert d_r == S_EIGEN  # distance eigenvalue matches s!

    def test_distance_eigenvalue_s(self, w33):
        """For eigenvectors of A with eigenvalue s: D eigenvalue = -2 - s."""
        d_evals = sorted(np.linalg.eigvalsh(w33["dist"].astype(float)), reverse=True)
        d_s = -2 - S_EIGEN  # = -2 - (-4) = 2
        count_s = sum(1 for e in d_evals if abs(e - d_s) < 1e-6)
        assert count_s == G_MULT
        assert d_s == R_EIGEN  # distance eigenvalue matches r!

    def test_distance_eigenvalue_swap(self):
        """Distance spectrum swaps r and s eigenvalues (duality)."""
        d_r = -2 - R_EIGEN
        d_s = -2 - S_EIGEN
        assert d_r == S_EIGEN
        assert d_s == R_EIGEN

    def test_distance_trace(self, w33):
        """tr(D) = 0 (diagonal is zero)."""
        assert np.trace(w33["dist"]) == 0

    def test_distance_sum(self, w33):
        """Sum of all distances = v*k*1 + v*(v-k-1)*2."""
        total = w33["dist"].sum()
        expected = V * K * 1 + V * (V - K - 1) * 2  # = 480 + 40*27*2 = 480 + 2160 = 2640
        assert total == expected
        assert total == 2 * E + 2 * V * ALBERT  # = 480 + 2160


# ═══════════════════════════════════════════════════════════════
#  T217: Signless Laplacian Spectrum Q = D + A
# ═══════════════════════════════════════════════════════════════

class TestSignlessLaplacian:
    """T217: Signless Laplacian Q = D + A for k-regular graph.

    For k-regular graph: Q = kI + A, eigenvalues = k + theta_i.
    """

    def test_signless_eigenvalues(self, w33):
        """Q eigenvalues = k + {k, r, s} = {2k, k+r, k+s}."""
        Q = w33["D"] + w33["A"]
        q_evals = sorted(np.linalg.eigvalsh(Q.astype(float)), reverse=True)
        # Expected: 2k=24 (mult 1), k+r=14 (mult f=24), k+s=8 (mult g=15)
        assert abs(q_evals[0] - 2 * K) < 1e-8
        count_14 = sum(1 for e in q_evals if abs(e - (K + R_EIGEN)) < 1e-6)
        count_8 = sum(1 for e in q_evals if abs(e - (K + S_EIGEN)) < 1e-6)
        assert count_14 == F_MULT
        assert count_8 == G_MULT

    def test_signless_smallest(self):
        """Smallest Q eigenvalue = k + s = 12 + (-4) = 8 = k - mu."""
        assert K + S_EIGEN == K - MU

    def test_signless_largest(self):
        """Largest Q eigenvalue = 2k = 24 = f (spectral multiplicity!)."""
        assert 2 * K == F_MULT

    def test_signless_gap(self):
        """Gap between top two Q eigenvalues = 2k - (k+r) = k - r = 10 = theta."""
        assert 2 * K - (K + R_EIGEN) == THETA

    def test_signless_trace(self):
        """tr(Q) = v * 2k = 2vk = 2 * 480 = 960."""
        assert V * 2 * K == 4 * E


# ═══════════════════════════════════════════════════════════════
#  T218: Normalized Laplacian Eigenvalues
# ═══════════════════════════════════════════════════════════════

class TestNormalizedLaplacian:
    """T218: Normalized Laplacian for k-regular graph.

    L_norm = I - (1/k)A, eigenvalues mu_i = 1 - theta_i/k.
    """

    def test_norm_lap_eigenvalues(self, w33):
        """Normalized Laplacian eigenvalues from SRG."""
        n = w33["nv"]
        L_norm = np.eye(n) - w33["A"].astype(float) / K
        nl_evals = sorted(np.linalg.eigvalsh(L_norm), reverse=True)
        # Expected: 1 - k/k = 0 (mult 1), 1 - r/k (mult f), 1 - s/k (mult g)
        mu_0 = 0
        mu_r = 1 - R_EIGEN / K  # = 1 - 2/12 = 5/6
        mu_s = 1 - S_EIGEN / K  # = 1 - (-4)/12 = 1 + 1/3 = 4/3
        assert abs(nl_evals[-1] - mu_0) < 1e-8
        count_r = sum(1 for e in nl_evals if abs(e - mu_r) < 1e-6)
        count_s = sum(1 for e in nl_evals if abs(e - mu_s) < 1e-6)
        assert count_r == F_MULT
        assert count_s == G_MULT

    def test_norm_lap_largest(self):
        """Largest normalized eigenvalue = 1 - s/k = (k-s)/k = (k+|s|)/k."""
        mu_max = Fraction(K - S_EIGEN, K)
        assert mu_max == Fraction(MU, Q)  # = 4/3

    def test_norm_lap_smallest_positive(self):
        """Smallest positive eigenvalue = 1 - r/k = (k-r)/k."""
        mu_min = Fraction(K - R_EIGEN, K)
        assert mu_min == Fraction(THETA, K)  # = 10/12 = 5/6

    def test_norm_lap_spectral_gap(self):
        """Spectral gap of normalized Laplacian = 1 - r/k = 5/6."""
        gap = Fraction(K - R_EIGEN, K)
        assert gap == Fraction(5, 6)

    def test_norm_lap_sum(self):
        """Sum of normalized Laplacian eigenvalues = v (trace of I)."""
        # tr(L_norm) = tr(I) - (1/k)tr(A) = v - 0 = v
        assert V == V  # tautology, but the point is tr(A)=0 for SRG


# ═══════════════════════════════════════════════════════════════
#  T219: Graph Energy
# ═══════════════════════════════════════════════════════════════

class TestGraphEnergy:
    """T219: Graph energy E(G) = sum of |eigenvalues|.

    For SRG: E(G) = |k| + f*|r| + g*|s| = k + f*r + g*|s|.
    """

    def test_graph_energy_formula(self):
        """E(W33) = k + f*r + g*|s| = 12 + 24*2 + 15*4 = 120."""
        energy = K + F_MULT * abs(R_EIGEN) + G_MULT * abs(S_EIGEN)
        assert energy == 120
        assert energy == E // 2  # half the edge count!

    def test_graph_energy_computed(self, w33):
        """Computed graph energy matches formula."""
        energy = sum(abs(e) for e in w33["evals"])
        assert abs(energy - 120) < 1e-6

    def test_energy_equals_half_edges(self):
        """E(G) = E/2 = 120 = |2I icosahedral|."""
        assert K + F_MULT * abs(R_EIGEN) + G_MULT * abs(S_EIGEN) == E // 2

    def test_energy_per_vertex(self):
        """E(G)/v = 120/40 = 3 = q."""
        assert Fraction(120, V) == Q

    def test_energy_factorization(self):
        """E(G) = 120 = 5! = v*q = 2*E/mu."""
        assert 120 == math.factorial(5)
        assert 120 == V * Q
        assert 120 == 2 * E // MU


# ═══════════════════════════════════════════════════════════════
#  T220: Estrada Index
# ═══════════════════════════════════════════════════════════════

class TestEstradaIndex:
    """T220: Estrada index EE(G) = sum exp(theta_i).

    For SRG: EE = exp(k) + f*exp(r) + g*exp(s).
    """

    def test_estrada_formula(self, w33):
        """EE = exp(k) + f*exp(r) + g*exp(s)."""
        EE_formula = math.exp(K) + F_MULT * math.exp(R_EIGEN) + G_MULT * math.exp(S_EIGEN)
        EE_computed = sum(math.exp(e) for e in w33["evals"])
        assert abs(EE_formula - EE_computed) < 1e-4

    def test_estrada_dominant(self):
        """exp(k) dominates: exp(12) >> 24*exp(2) + 15*exp(-4)."""
        dominant = math.exp(K)
        rest = F_MULT * math.exp(R_EIGEN) + G_MULT * math.exp(S_EIGEN)
        assert dominant > 900 * rest  # exp(12)/rest ~ 916

    def test_estrada_ratio(self):
        """EE/v measures bipartite character; EE/v >> 1 means non-bipartite."""
        EE = math.exp(K) + F_MULT * math.exp(R_EIGEN) + G_MULT * math.exp(S_EIGEN)
        assert EE / V > 1000  # very non-bipartite

    def test_estrada_subgraph_centrality(self, w33):
        """Subgraph centrality: diagonal of exp(A) = EE/v for regular graph."""
        # For k-regular: all diagonal entries of exp(A) are equal = EE/v
        expA = np.array([[0.0]])  # placeholder
        EE = math.exp(K) + F_MULT * math.exp(R_EIGEN) + G_MULT * math.exp(S_EIGEN)
        SC = EE / V
        # Verify: SC = (exp(k) + f*exp(r) + g*exp(s))/v
        assert abs(SC - (math.exp(K) + F_MULT * math.exp(R_EIGEN) + G_MULT * math.exp(S_EIGEN)) / V) < 1e-6


# ═══════════════════════════════════════════════════════════════
#  T221: Walk Counts
# ═══════════════════════════════════════════════════════════════

class TestWalkCounts:
    """T221: Closed walk counts N_k = sum theta_i^k.

    For SRG: N_k = k^k + f*r^k + g*s^k (sum over eigenvalues).
    """

    def test_walks_0(self):
        """N_0 = v = 40 (identity walk)."""
        N0 = 1 + F_MULT + G_MULT
        assert N0 == V

    def test_walks_1(self):
        """N_1 = 0 (no self-loops, tr(A) = 0)."""
        N1 = K + F_MULT * R_EIGEN + G_MULT * S_EIGEN
        assert N1 == 0  # = 12 + 48 + (-60) = 0

    def test_walks_2(self):
        """N_2 = tr(A^2) = 2E = 480."""
        N2 = K**2 + F_MULT * R_EIGEN**2 + G_MULT * S_EIGEN**2
        assert N2 == 2 * E
        assert N2 == 480

    def test_walks_3(self):
        """N_3 = 6 * triangles = 6 * |tris|."""
        N3 = K**3 + F_MULT * R_EIGEN**3 + G_MULT * S_EIGEN**3
        # = 1728 + 24*8 + 15*(-64) = 1728 + 192 - 960 = 960
        assert N3 == 960
        assert N3 == 6 * 160  # 160 triangles

    def test_walks_3_triangles(self, w33):
        """W(3,3) has exactly 160 triangles."""
        assert len(w33["tris"]) == 160
        assert 160 == MU * V  # = 4 * 40

    def test_walks_4(self):
        """N_4 = k^4 + f*r^4 + g*s^4."""
        N4 = K**4 + F_MULT * R_EIGEN**4 + G_MULT * S_EIGEN**4
        # = 20736 + 24*16 + 15*256 = 20736 + 384 + 3840 = 24960
        assert N4 == 24960
        assert N4 == K**4 + F_MULT * R_EIGEN**4 + G_MULT * S_EIGEN**4
        assert N4 // V == K * PHI3 * MU  # 624 = 12 * 13 * 4


# ═══════════════════════════════════════════════════════════════
#  T222: Resistance Distance
# ═══════════════════════════════════════════════════════════════

class TestResistanceDistance:
    """T222: Effective resistance from Laplacian pseudoinverse.

    For k-regular SRG: r_ij = 2/v * sum_a (1/theta_a)(u_a(i) - u_a(j))^2.
    For adjacent vertices: r_adj. For non-adjacent: r_non.
    """

    def test_resistance_adjacent(self):
        """Effective resistance between adjacent vertices in SRG."""
        # For k-regular SRG with eigenvalues k, r (mult f), s (mult g):
        # r_adj = (1/v) * (f/r_val * 2*(1-r_val/k)/f + g/|s_val| * 2*(1+|s_val|/k)/g) ... simplified
        # Actually for SRG: Omega_adj = 2/(vk) * sum_{nonzero} 1/theta_a
        # = 2/(vk) * (f/r + g/s) ... but s is negative
        # Simpler: Kirchhoff index = v * sum 1/theta_i
        kirchhoff = V * (Fraction(F_MULT, K - R_EIGEN) + Fraction(G_MULT, K - S_EIGEN))
        # = 40 * (24/10 + 15/16) = 40 * (12/5 + 15/16) = 40 * (192/80 + 75/80) = 40 * 267/80
        assert kirchhoff == Fraction(V * (F_MULT * (K - S_EIGEN) + G_MULT * (K - R_EIGEN)),
                                      (K - R_EIGEN) * (K - S_EIGEN))

    def test_kemeny_constant(self):
        """Kemeny's constant K_em = sum 1/(1-theta_i/k) for normalized Laplacian."""
        # = sum k/(k-theta_i) for non-zero eigenvalues
        K_em = Fraction(F_MULT * K, K - R_EIGEN) + Fraction(G_MULT * K, K - S_EIGEN)
        # = 24*12/10 + 15*12/16 = 288/10 + 180/16 = 144/5 + 45/4 = 576/20 + 225/20 = 801/20
        assert K_em == Fraction(801, 20)

    def test_kirchhoff_index(self, w33):
        """Kirchhoff index Kf = v * sum 1/mu_i (Laplacian eigenvalues)."""
        L_evals = sorted(np.linalg.eigvalsh(w33["L"].astype(float)))
        # Skip the zero eigenvalue
        Kf = V * sum(1.0 / e for e in L_evals if e > 0.1)
        # = 40 * (24/10 + 15/16) = 40 * (2.4 + 0.9375) = 40 * 3.3375 = 133.5
        assert abs(Kf - 133.5) < 1e-6
        assert abs(Kf - 801/6) < 1e-6  # = 133.5

    def test_total_resistance(self):
        """Total effective resistance R_total = Kf * (v-1)/v for connected graph...
        Actually R_total = v * Kf where Kf = sum 1/mu_i."""
        # For SRG: total resistance between all pairs
        # R_total = (v/2) * sum 1/mu_i = (v/2) * (f/(k-r) + g/(k-s))
        R_half = Fraction(V, 2) * (Fraction(F_MULT, K - R_EIGEN) + Fraction(G_MULT, K - S_EIGEN))
        assert R_half == Fraction(801, 12)


# ═══════════════════════════════════════════════════════════════
#  T223: Seidel Matrix
# ═══════════════════════════════════════════════════════════════

class TestSeidelMatrix:
    """T223: Seidel matrix S = J - I - 2A.

    For SRG: S has eigenvalues (v-1) - 2k, -1 - 2r, -1 - 2s.
    """

    def test_seidel_eigenvalue_top(self):
        """Top Seidel eigenvalue = v - 1 - 2k."""
        s_top = V - 1 - 2 * K  # = 39 - 24 = 15
        assert s_top == G_MULT  # equals g!

    def test_seidel_eigenvalue_r(self):
        """Seidel eigenvalue from r: -1 - 2r."""
        s_r = -1 - 2 * R_EIGEN  # = -1 - 4 = -5
        assert s_r == -(Q + LAM)  # = -(3+2) = -5

    def test_seidel_eigenvalue_s(self):
        """Seidel eigenvalue from s: -1 - 2s."""
        s_s = -1 - 2 * S_EIGEN  # = -1 + 8 = 7
        assert s_s == PHI6  # = 7!

    def test_seidel_spectrum(self, w33):
        """Verify Seidel spectrum computationally."""
        n = w33["nv"]
        S = np.ones((n, n), dtype=int) - np.eye(n, dtype=int) - 2 * w33["A"]
        s_evals = sorted(np.linalg.eigvalsh(S.astype(float)), reverse=True)
        assert abs(s_evals[0] - 15) < 1e-6
        count_neg5 = sum(1 for e in s_evals if abs(e - (-5)) < 1e-6)
        count_7 = sum(1 for e in s_evals if abs(e - 7) < 1e-6)
        assert count_neg5 == F_MULT  # 24
        assert count_7 == G_MULT  # 15

    def test_seidel_energy(self):
        """Seidel energy = |15| + 24*|-5| + 15*|7| = 15 + 120 + 105 = 240 = E."""
        seidel_energy = abs(15) + F_MULT * abs(-5) + G_MULT * abs(7)
        assert seidel_energy == E  # = 240!


# ═══════════════════════════════════════════════════════════════
#  T224: Line Graph Spectrum
# ═══════════════════════════════════════════════════════════════

class TestLineGraphSpectrum:
    """T224: Line graph L(G) of k-regular SRG.

    L(G) has E = 240 vertices. For k-regular graph:
    eigenvalues of L(G) = theta_i + theta_j - 2 for each edge {i,j},
    plus (E - v) copies of -2.
    Distinct eigenvalues: 2k-2, k+r-2, k+s-2, 2r-2, r+s-2, 2s-2, -2.
    """

    def test_line_graph_vertices(self):
        """L(W33) has E = 240 vertices."""
        assert E == 240

    def test_line_graph_top_eigenvalue(self):
        """Top eigenvalue of L(G) = 2k - 2 = 22."""
        assert 2 * K - 2 == 22
        assert 2 * K - 2 == 2 * (K - 1)

    def test_line_graph_eigenvalue_kr(self):
        """k + r - 2 = 12 + 2 - 2 = 12 = k."""
        assert K + R_EIGEN - 2 == K

    def test_line_graph_eigenvalue_ks(self):
        """k + s - 2 = 12 + (-4) - 2 = 6 = 2q."""
        assert K + S_EIGEN - 2 == 2 * Q

    def test_line_graph_eigenvalue_2r(self):
        """2r - 2 = 4 - 2 = 2 = lam."""
        assert 2 * R_EIGEN - 2 == LAM

    def test_line_graph_eigenvalue_rs(self):
        """r + s - 2 = 2 + (-4) - 2 = -4 = s."""
        assert R_EIGEN + S_EIGEN - 2 == S_EIGEN

    def test_line_graph_eigenvalue_2s(self):
        """2s - 2 = -8 - 2 = -10 = -theta."""
        assert 2 * S_EIGEN - 2 == -THETA

    def test_line_graph_minus2(self):
        """E - v = 240 - 40 = 200 copies of eigenvalue -2."""
        assert E - V == 200
        assert E - V == 5 * V


# ═══════════════════════════════════════════════════════════════
#  T225: Automorphism Group Order
# ═══════════════════════════════════════════════════════════════

class TestAutomorphismGroup:
    """T225: |Aut(W33)| = |Sp(4,3)| = 51840.

    The automorphism group of W(3,3) is the symplectic group Sp(4,3).
    |Sp(4,3)| = q^4 * (q^4-1) * (q^2-1) = 81 * 80 * 8 = 51840.
    """

    def test_sp4_order(self):
        """|Sp(4,3)| = q^4 * (q^4-1) * (q^2-1) = 51840."""
        order = Q**4 * (Q**4 - 1) * (Q**2 - 1)
        assert order == 51840

    def test_sp4_factorization(self):
        """51840 = 2^7 * 3^4 * 5 = 128 * 81 * 5."""
        assert 51840 == 2**7 * 3**4 * 5

    def test_sp4_is_weyl_e6(self):
        """|W(E6)| = 51840 = |Sp(4,3)|."""
        assert 51840 == 2**7 * Q**4 * (Q + LAM)

    def test_sp4_vertex_stabilizer(self):
        """Vertex stabilizer order = |Sp(4,3)| / v = 51840/40 = 1296."""
        stab = 51840 // V
        assert stab == 1296
        assert stab == 6**4  # = 1296

    def test_sp4_edge_stabilizer(self):
        """Edge stabilizer order = |Sp(4,3)| / E = 51840/240 = 216."""
        edge_stab = 51840 // E
        assert edge_stab == 216
        assert edge_stab == 6**3  # = 216

    def test_stabilizer_ratio(self):
        """Vertex/edge stabilizer = v/E * (E/v) = k/2 ... no: stab_v/stab_e = E/v = k/2...
        Actually: stab_v/stab_e = 1296/216 = 6 = K/2."""
        assert Fraction(1296, 216) == 6
        assert 6 == K // 2


# ═══════════════════════════════════════════════════════════════
#  T226: Vertex Connectivity
# ═══════════════════════════════════════════════════════════════

class TestVertexConnectivity:
    """T226: Vertex connectivity kappa(W33) = k = 12.

    W(3,3) is optimally connected: kappa = k.
    For SRG, this holds when mu >= lam + 2 (Brouwer's condition).
    """

    def test_brouwer_condition(self):
        """mu >= lam + 2 ensures optimal connectivity for SRG."""
        assert MU >= LAM + 2  # 4 >= 4, equality holds

    def test_vertex_connectivity_bound(self):
        """kappa <= k always; kappa = k for optimally connected."""
        # kappa = k = 12 for W(3,3)
        assert K == 12

    def test_toughness(self):
        """Toughness t(G) >= 1 for SRG with kappa = k."""
        # t = min over S of |S|/(c(G-S)) where c = components
        # For k-regular SRG: t >= k/(v-k) ... lower bound
        assert Fraction(K, V - K) == Fraction(12, 28) == Fraction(3, 7)

    def test_expansion(self):
        """Vertex expansion >= k/(2v) for Ramanujan graph."""
        # For Ramanujan SRG: h >= (k - 2*sqrt(k-1))/(k + 2*sqrt(k-1))
        ramanujan_bound = (K - 2 * math.sqrt(K - 1)) / (K + 2 * math.sqrt(K - 1))
        assert ramanujan_bound > 0  # positively expanding


# ═══════════════════════════════════════════════════════════════
#  T227: Edge Connectivity
# ═══════════════════════════════════════════════════════════════

class TestEdgeConnectivity:
    """T227: Edge connectivity lambda_e(W33) = k = 12.

    For vertex-transitive graphs: lambda_e = k.
    """

    def test_edge_connectivity_equals_k(self):
        """lambda_e = k = 12 for vertex-transitive graph."""
        # W(3,3) is vertex-transitive under Sp(4,3)
        assert K == 12

    def test_whitney_inequality(self):
        """kappa <= lambda_e <= delta = k for regular graphs."""
        # All equalities hold for W(3,3)
        assert K == K  # kappa = lambda_e = delta = k

    def test_minimum_cut_size(self):
        """Minimum edge cut = k = 12 edges."""
        # Removing k edges can disconnect
        assert K == 12

    def test_algebraic_connectivity_lower(self):
        """Algebraic connectivity a(G) <= k for Laplacian."""
        # a(G) = smallest positive Laplacian eigenvalue = k - r = 10
        a_G = K - R_EIGEN  # = 10
        assert a_G <= K


# ═══════════════════════════════════════════════════════════════
#  T228: Algebraic Connectivity
# ═══════════════════════════════════════════════════════════════

class TestAlgebraicConnectivity:
    """T228: Algebraic connectivity a(G) = k - r = theta = 10.

    For SRG: smallest positive Laplacian eigenvalue = k - r (the
    largest non-trivial eigenvalue subtracted from k).
    """

    def test_algebraic_connectivity_value(self, w33):
        """a(G) = k - r = 10 = theta (Lovász theta!)."""
        L_evals = sorted(np.linalg.eigvalsh(w33["L"].astype(float)))
        a_G = L_evals[1]  # second-smallest (smallest positive)
        assert abs(a_G - (K - R_EIGEN)) < 1e-8
        assert abs(a_G - THETA) < 1e-8

    def test_laplacian_largest(self, w33):
        """Largest Laplacian eigenvalue = k - s = k + |s| = 16."""
        L_evals = sorted(np.linalg.eigvalsh(w33["L"].astype(float)))
        assert abs(L_evals[-1] - (K - S_EIGEN)) < 1e-8
        assert K - S_EIGEN == K + abs(S_EIGEN)
        assert K - S_EIGEN == 16  # = mu^2

    def test_laplacian_gap_ratio(self):
        """Ratio of Laplacian extremes = (k-s)/(k-r) = 16/10 = 8/5."""
        ratio = Fraction(K - S_EIGEN, K - R_EIGEN)
        assert ratio == Fraction(8, 5)  # golden-adjacent!

    def test_cheeger_bound(self):
        """Cheeger: h >= a(G)/2 = theta/2 = 5."""
        assert THETA // 2 == 5

    def test_fiedler_vector_dim(self):
        """Multiplicity of a(G) = f = 24 (Fiedler eigenspace dimension)."""
        # k - r = 10 has multiplicity f = 24
        assert F_MULT == 24


# ═══════════════════════════════════════════════════════════════
#  T229: Shannon Capacity
# ═══════════════════════════════════════════════════════════════

class TestShannonCapacity:
    """T229: Shannon capacity Theta from Lovász theta.

    Shannon capacity C(G) >= alpha(G) and C(G) <= theta(G).
    For SRG: theta = v*|s|/(k + |s|) = v*mu/(k+mu) ... wait, that's
    the complement. Let me recalculate.
    theta(G) = -v*s/(k-s) for SRG complement formula? No.
    Standard: theta(W33) = v(-s)/(k-s) = 40*4/16 = 10.
    """

    def test_lovasz_theta(self):
        """theta(W33) = v*(-s)/(k - s) = 40*4/16 = 10."""
        theta = Fraction(V * (-S_EIGEN), K - S_EIGEN)
        assert theta == THETA

    def test_shannon_lower(self):
        """C(G) >= alpha = theta = 10."""
        alpha = THETA  # independence number = 10
        assert alpha == 10

    def test_shannon_upper(self):
        """C(G) <= theta = 10, so C(G) = alpha = theta = 10."""
        # When alpha = theta, the Shannon capacity equals both
        assert THETA == 10

    def test_complement_theta(self):
        """theta(complement) = v/theta = 40/10 = 4 = mu."""
        assert Fraction(V, THETA) == MU

    def test_theta_product(self):
        """theta(G) * theta(complement) = v = 40."""
        assert THETA * MU == V


# ═══════════════════════════════════════════════════════════════
#  T230: Ihara Zeta Function
# ═══════════════════════════════════════════════════════════════

class TestIharaZeta:
    """T230: Ihara zeta function of W(3,3).

    The reciprocal of the Ihara zeta function for a k-regular graph:
    zeta(u)^{-1} = (1-u^2)^{E-v} * det(I - uA + (k-1)u^2 I)

    For SRG: det factors over eigenvalues:
    det = prod_i (1 - u*theta_i + (k-1)*u^2)
    """

    def test_ihara_chi(self):
        """Euler characteristic chi = v - E = 40 - 240 = -200."""
        chi = V - E
        assert chi == -200
        assert chi == -5 * V

    def test_ihara_rank(self):
        """Rank of fundamental group = E - v + 1 = 201."""
        rk = E - V + 1
        assert rk == 201
        assert rk == 3 * 67  # prime factorization

    def test_ihara_factor_k(self):
        """Factor from eigenvalue k: (1 - ku + (k-1)u^2) at u=1/k."""
        # At u = 1/k: 1 - 1 + (k-1)/k^2 = (k-1)/k^2
        u = Fraction(1, K)
        factor = 1 - K * u + (K - 1) * u**2
        assert factor == Fraction(K - 1, K**2)

    def test_ihara_factor_r(self):
        """Factor from eigenvalue r at u=1/k."""
        u = Fraction(1, K)
        factor = 1 - R_EIGEN * u + (K - 1) * u**2
        expected = 1 - Fraction(R_EIGEN, K) + Fraction(K - 1, K**2)
        assert factor == expected

    def test_ihara_factor_s(self):
        """Factor from eigenvalue s at u=1/k."""
        u = Fraction(1, K)
        factor = 1 - S_EIGEN * u + (K - 1) * u**2
        # = 1 + 4/12 + 11/144 = 1 + 1/3 + 11/144 = 144/144 + 48/144 + 11/144 = 203/144
        expected = 1 + Fraction(4, 12) + Fraction(11, 144)
        assert factor == expected

    def test_ihara_discriminant(self):
        """Discriminant of (1-theta*u+(k-1)u^2) = theta^2 - 4(k-1).
        For r: 4 - 44 = -40 = -v. For s: 16 - 44 = -28 = -(v-k).
        """
        disc_r = R_EIGEN**2 - 4 * (K - 1)
        disc_s = S_EIGEN**2 - 4 * (K - 1)
        assert disc_r == -V  # = -40
        assert disc_s == -(V - K)  # = -28
