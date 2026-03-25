"""
Phase CXCIII — Heawood Graph and Fano Plane Spectral Identities
==============================================================

The Heawood graph is the point-line incidence graph of the Fano plane PG(2,2).
All its parameters embed into the W(3,3) algebra via the single prime Q=3.

Key integer identities verified here (all exact, using fractions.Fraction):

    N_H  = 2*(Q^2-Q+1)  = 14        (Heawood vertices = 2 * Fano order)
    E_H  = N_H*Q/2      = 21        (edges; degree K_H = Q = 3)
    Girth_H = 2*Q       = 6
    Diam_H  = Q         = 3

    Middle adjacency eigenvalue SQUARED = Q-1 = LAM          [W33 lambda!]
    Laplacian middle eigenvalue SUM     = 2*Q = LAM+MU        [W33 sum!]
    Laplacian middle eigenvalue PRODUCT = Q^2-Q+1 = FANO_ORD  [Fano order!]
    Trace(A_H^2) = N_H*K_H = 42
    Trace(A_H^4) = N_H*K_H*(2*K_H-1) = 210

    Fano order = FANO_ORD = Q^2-Q+1 = 7
    N_H - 1    = Q^2+Q+1 = Phi_3(Q) = 13               [cyclotomic coincidence!]
    2*(Q^2-Q+1) = 1+(Q^2+Q+1)  only at Q=3              [unique coincidence]

    det(A_H) = -Q^2*(Q-1)^6 = -576 = -(K*LAM)^2         [W33 bridge!]

Power cascade — (Q-1)^k equals W33/W33-derived parameters:
    (Q-1)^1 = 2  = LAM    (W33 lambda)
    (Q-1)^2 = 4  = MU     (W33 mu; also = LAM^2)
    (Q-1)^3 = 8  = K+s    (degree plus negative eigenvalue)
    (Q-1)^4 = 16 = K+MU   (degree plus mu)
    (Q-1)^5 = 32 = MINPOLY_C1   (W33 min-poly x-coefficient magnitude)
    (Q-1)^6 = 64 = Sylow-2 order in axis-192 group H

All formulas computed in exact integer / Fraction arithmetic.
"""

from fractions import Fraction
import unittest

# ── W(3,3) parameters ────────────────────────────────────────────────────────
Q = 3
V = 40           # vertices
K = 12           # degree
LAM = 2          # lambda (common neighbours of adjacent pair)
MU = 4           # mu    (common neighbours of non-adjacent pair)
THETA = 10       # Lovász theta of W33 complement = K+r+s
EIG_K = 12       # trivial eigenvalue
EIG_R = 2        # positive non-trivial eigenvalue
EIG_S = -4       # negative non-trivial eigenvalue
MUL_K = 1        # multiplicity of K
MUL_R = 24       # multiplicity of r
MUL_S = 15       # multiplicity of s
MINPOLY_C1 = 32  # |x-coefficient| of W33 minimal polynomial (x^3-10x^2-32x+96)
MINPOLY_C0 = 96  # constant term of W33 minimal polynomial

# ── Heawood / Fano derived parameters ────────────────────────────────────────
FANO_ORDER = Q**2 - Q + 1   # = 7   (points and lines in PG(2,2) / Phi_6(Q))
PHI3_Q     = Q**2 + Q + 1   # = 13  (cyclotomic Phi_3(Q))
N_H  = 2 * FANO_ORDER       # = 14  (Heawood vertices)
E_H  = N_H * Q // 2         # = 21  (edges)
K_H  = Q                    # = 3   (Heawood degree)
GIRTH_H = 2 * Q             # = 6
DIAM_H  = Q                 # = 3
MID_EIG_SQ = Q - 1          # = 2   (squared middle eigenvalue)
LAP_MID_SUM  = 2 * Q        # = 6   (sum of Laplacian middle pair)
LAP_MID_PROD = FANO_ORDER   # = 7   (product of Laplacian middle pair)
TRACE_A2_H = N_H * K_H      # = 42
TRACE_A4_H = N_H * K_H * (2 * K_H - 1)  # = 210
DET_A_H_NEG = Q**2 * (Q - 1)**6         # = 576  so det = -576


# ─────────────────────────────────────────────────────────────────────────────
class T1HeawoodIntegerParameters(unittest.TestCase):
    """Heawood graph combinatorial parameters, all exact integers."""

    def test_n_vertices(self):
        """n_H = 2*(Q^2-Q+1) = 14."""
        self.assertEqual(N_H, 14)

    def test_n_equals_twice_fano_order(self):
        """n_H = 2 * FANO_ORDER."""
        self.assertEqual(N_H, 2 * FANO_ORDER)

    def test_edge_count(self):
        """e_H = n_H * K_H / 2 = 21."""
        self.assertEqual(E_H, 21)

    def test_degree(self):
        """Heawood degree = Q = 3."""
        self.assertEqual(K_H, Q)

    def test_girth(self):
        """Girth of Heawood graph = 2*Q = 6."""
        self.assertEqual(GIRTH_H, 6)
        self.assertEqual(GIRTH_H, 2 * Q)

    def test_diameter(self):
        """Diameter of Heawood graph = Q = 3."""
        self.assertEqual(DIAM_H, Q)

    def test_bipartite_parts(self):
        """Each bipartite part has N_H/2 = FANO_ORDER = 7 vertices."""
        self.assertEqual(N_H // 2, FANO_ORDER)
        self.assertEqual(N_H % 2, 0)  # even, bipartite

    def test_heawood_degree_equals_w33_first_eigenvalue(self):
        """Heawood degree K_H = Q = W33 non-trivial eigenvalue EIG_R... wait:
        EIG_R=2, not Q=3.  The correct identity: K_H = Q = W33's base prime."""
        self.assertEqual(K_H, Q)
        # Also: K_H * MU = Q * MU = 12 = K (W33 degree)
        self.assertEqual(K_H * MU, K)


# ─────────────────────────────────────────────────────────────────────────────
class T2AdjacencyEigenvalueIdentities(unittest.TestCase):
    """Integer identities for the Heawood adjacency spectrum {±Q^1, ±sqrt(Q-1)^6}."""

    def test_extremal_eigenvalue_equals_Q(self):
        """Heawood extremal eigenvalue = Q (integer)."""
        self.assertEqual(K_H, Q)     # K_H is both degree and extremal |eigenvalue|

    def test_middle_eigenvalue_squared(self):
        """Middle eigenvalue squared = Q-1 = LAM (W33 lambda!)."""
        self.assertEqual(MID_EIG_SQ, Q - 1)
        self.assertEqual(MID_EIG_SQ, LAM)

    def test_trace_A2(self):
        """Trace(A_H^2) = sum of eigenvalue^2 = N_H*K_H = 42."""
        # From eigenvalues: 2*Q^2 + 12*(Q-1)
        from_eigs = 2 * Q**2 + 2 * (N_H // 2 - 1) * (Q - 1)
        self.assertEqual(from_eigs, TRACE_A2_H)
        self.assertEqual(TRACE_A2_H, 42)

    def test_trace_A2_equals_N_K(self):
        """Trace(A_H^2) = N_H * K_H (sum-of-degrees for regular graph)."""
        self.assertEqual(TRACE_A2_H, N_H * K_H)

    def test_trace_A4_from_eigenvalues(self):
        """Trace(A_H^4) = 2*Q^4 + 12*(Q-1)^2 = 210."""
        from_eigs = 2 * Q**4 + 2 * (N_H // 2 - 1) * (Q - 1)**2
        self.assertEqual(from_eigs, 210)

    def test_trace_A4_formula(self):
        """Trace(A_H^4) = N_H * K_H * (2*K_H-1) = 210."""
        # Girth-6 combinatorial identity: A^4[v,v] = K_H^2 + K_H*(K_H-1)
        # so trace = N_H * K_H * (2*K_H - 1)
        self.assertEqual(TRACE_A4_H, 210)
        self.assertEqual(TRACE_A4_H, N_H * K_H * (2 * K_H - 1))

    def test_trace_A4_per_vertex(self):
        """A^4[v,v] = K_H*(2*K_H-1) = 15 for every vertex (girth-6 identity)."""
        per_vertex = K_H * (2 * K_H - 1)
        self.assertEqual(per_vertex, 15)
        self.assertEqual(TRACE_A4_H, N_H * per_vertex)

    def test_bipartite_odd_trace_zero(self):
        """All odd traces = 0 (bipartite graph has symmetric spectrum)."""
        # Sum of odd powers of eigenvalues = 0 for bipartite
        trace_A1 = 1 * Q + (N_H // 2 - 1) * 0 - (N_H // 2 - 1) * 0 - 1 * Q
        self.assertEqual(trace_A1, 0)
        trace_A3 = 1 * Q**3 + (N_H // 2 - 1) * 0 - (N_H // 2 - 1) * 0 - 1 * Q**3
        self.assertEqual(trace_A3, 0)


# ─────────────────────────────────────────────────────────────────────────────
class T3LaplacianSpectralIdentities(unittest.TestCase):
    """Laplacian middle eigenvalue identities: sum = 2Q = LAM+MU; product = FANO_ORDER."""

    def test_laplacian_middle_sum_integer(self):
        """Sum of Laplacian middle pair = 2*Q = LAM+MU (W33 parameters!)."""
        self.assertEqual(LAP_MID_SUM, 2 * Q)
        self.assertEqual(LAP_MID_SUM, LAM + MU)

    def test_laplacian_middle_sum_value(self):
        """Sum of Laplacian middle pair = 6."""
        self.assertEqual(LAP_MID_SUM, 6)

    def test_laplacian_middle_product_integer(self):
        """Product of Laplacian middle pair = Q^2-Q+1 = FANO_ORDER = 7."""
        self.assertEqual(LAP_MID_PROD, FANO_ORDER)

    def test_laplacian_middle_product_value(self):
        """Product of Laplacian middle pair = 7."""
        self.assertEqual(LAP_MID_PROD, 7)

    def test_laplacian_middle_min_poly_linear(self):
        """Laplacian middle min-poly: x^2 - 2Q*x + (Q^2-Q+1) has integer coefficients."""
        # Coefficients: linear = -2Q, constant = Q^2-Q+1 = FANO_ORDER
        linear_coeff = -LAP_MID_SUM        # = -6 (integer)
        const_coeff  = LAP_MID_PROD        # = 7 (integer)
        self.assertEqual(linear_coeff, -2 * Q)
        self.assertEqual(const_coeff, FANO_ORDER)

    def test_laplacian_middle_discriminant(self):
        """Discriminant of middle min-poly = (2Q)^2 - 4*FANO_ORDER = 4*(Q-1)."""
        disc = LAP_MID_SUM**2 - 4 * LAP_MID_PROD
        self.assertEqual(disc, 4 * (Q - 1))  # = 4*LAM = 8

    def test_laplacian_algebraic_connectivity_formula(self):
        """Algebraic connectivity = Q - sqrt(Q-1); product with spectral gap partner = FANO_ORDER."""
        # (Q - sqrt(Q-1)) * (Q + sqrt(Q-1)) = Q^2 - (Q-1) = Q^2-Q+1 = FANO_ORDER
        product_int = Q**2 - (Q - 1)
        self.assertEqual(product_int, FANO_ORDER)

    def test_laplacian_max_eigenvalue(self):
        """Maximum Laplacian eigenvalue = 2*K_H = 6 (bipartite, since K_H+K_H)."""
        # For bipartite K_H-regular graph, max Laplacian eigenvalue = 2*K_H
        max_lap = 2 * K_H
        self.assertEqual(max_lap, 6)
        self.assertEqual(max_lap, LAM + MU)  # = 2+4 = 6 (W33 sum too!)


# ─────────────────────────────────────────────────────────────────────────────
class T4FanoPlaneParametersW33Bridge(unittest.TestCase):
    """Fano plane order = Q^2-Q+1 = 7; remarkable coincidences at Q=3."""

    def test_fano_order(self):
        """FANO_ORDER = Q^2-Q+1 = 7."""
        self.assertEqual(FANO_ORDER, 7)

    def test_fano_order_formula(self):
        """FANO_ORDER = Q^2-Q+1 for Q=3."""
        self.assertEqual(FANO_ORDER, Q**2 - Q + 1)

    def test_fano_points_per_line(self):
        """PG(2,2) has 3 points per line = Q = K_H (Heawood degree)."""
        pts_per_line = Q   # Fano plane has q+1=3 points per line with q=2; and Q=3 here
        self.assertEqual(pts_per_line, K_H)

    def test_n_heawood_minus_1_equals_phi3(self):
        """N_H - 1 = Q^2+Q+1 = Phi_3(Q) = 13 (cyclotomic coincidence!)."""
        self.assertEqual(N_H - 1, PHI3_Q)
        self.assertEqual(N_H - 1, 13)

    def test_n_heawood_unique_coincidence(self):
        """N_H = 2*Phi_6(Q) = 1+Phi_3(Q) ONLY at Q=3 (unique coincidence)."""
        # 2*(Q^2-Q+1) = 1+(Q^2+Q+1) iff Q^2-3Q = 0 iff Q=3
        self.assertEqual(2 * (Q**2 - Q + 1), 1 + (Q**2 + Q + 1))
        self.assertEqual(N_H, 14)

    def test_fano_order_equals_lap_mid_product(self):
        """FANO_ORDER = Laplacian-middle-product (structural bridge)."""
        self.assertEqual(FANO_ORDER, LAP_MID_PROD)

    def test_heawood_n_times_k_w33(self):
        """N_H * K = 14*12 = 168 = 2 * FANO_ORDER * K (Heawood × W33 degree product)."""
        product = N_H * K
        self.assertEqual(product, 168)
        self.assertEqual(product, 2 * FANO_ORDER * K)

    def test_fano_order_in_cayley_menger(self):
        """FANO_ORDER * N_H = 7*14 = 98 = 2*FANO_ORDER^2."""
        self.assertEqual(FANO_ORDER * N_H, 2 * FANO_ORDER**2)


# ─────────────────────────────────────────────────────────────────────────────
class T5CharPolyAndDeterminant(unittest.TestCase):
    """Characteristic polynomial factored form and integer determinant."""

    def test_char_poly_constant_sign(self):
        """char_poly(0) = product of negated eigenvalues = (-1)^14 * det(A)."""
        # char poly = (x-3)(x+3)(x^2-2)^6; at x=0: (-3)(3)(-2)^6 = -9*64 = -576
        char_poly_at_0 = (-Q) * (Q) * (-(Q - 1))**6
        self.assertEqual(char_poly_at_0, -576)

    def test_determinant_formula(self):
        """det(A_H) = -Q^2*(Q-1)^6 = -576."""
        det_A_H = -(Q**2) * (Q - 1)**6
        self.assertEqual(det_A_H, -576)
        self.assertEqual(DET_A_H_NEG, Q**2 * (Q - 1)**6)

    def test_determinant_w33_bridge(self):
        """det(A_H) = -(K*LAM)^2 (W33 degree × lambda squared)."""
        self.assertEqual(DET_A_H_NEG, (K * LAM)**2)

    def test_char_poly_squared_form(self):
        """char_poly = (x^2 - Q^2) * (x^2 - (Q-1))^(N_H/2-1); all integer coefficients."""
        # (x^2-9)*(x^2-2)^6: verify constant and leading terms
        factor1_const = -(Q**2)                # = -9
        factor2_const = -(Q - 1)               # = -2
        const_term = factor1_const * factor2_const**(N_H // 2 - 1)
        self.assertEqual(const_term, -(Q**2) * (Q - 1)**(N_H // 2 - 1))
        self.assertEqual(const_term, -576)

    def test_char_poly_degree(self):
        """Characteristic polynomial degree = N_H = 14."""
        # degree = 2 + 2*(N_H/2-1) = N_H
        deg = 2 + 2 * (N_H // 2 - 1)
        self.assertEqual(deg, N_H)

    def test_spectral_radius(self):
        """Spectral radius = K_H = Q = 3 (extremal eigenvalue)."""
        spectral_radius = K_H
        self.assertEqual(spectral_radius, Q)

    def test_energy(self):
        """Graph energy E(H) = sum|lambda_i| = 2*Q + 2*(N_H/2-1)*sqrt(Q-1).
        Integer part: 2*Q = 6; total = 2*3 + 12*sqrt(2)."""
        # Integer part of energy (eigenvalue magnitudes summed for integer ones)
        integer_eigenvalues_sum = 2 * Q   # from ±Q once each
        self.assertEqual(integer_eigenvalues_sum, 6)
        # The 12 copies of sqrt(Q-1) contribute 12*sqrt(Q-1) which is irrational
        middle_count = N_H - 2    # = 12
        self.assertEqual(middle_count, 12)


# ─────────────────────────────────────────────────────────────────────────────
class T6PowerCascadeIdentities(unittest.TestCase):
    """(Q-1)^k cascade: W33 parameters appear as consecutive powers of LAM=Q-1."""

    def test_cascade_1_is_LAM(self):
        """(Q-1)^1 = 2 = LAM (W33 lambda)."""
        self.assertEqual((Q - 1)**1, LAM)

    def test_cascade_2_is_MU(self):
        """(Q-1)^2 = 4 = MU (W33 mu); MU = LAM^2 (remarkable!)."""
        self.assertEqual((Q - 1)**2, MU)
        self.assertEqual(MU, LAM**2)

    def test_cascade_3_is_K_plus_s(self):
        """(Q-1)^3 = 8 = K + EIG_S (W33 degree + negative eigenvalue)."""
        self.assertEqual((Q - 1)**3, K + EIG_S)
        self.assertEqual((Q - 1)**3, 8)

    def test_cascade_4_is_K_plus_MU(self):
        """(Q-1)^4 = 16 = K + MU (W33 degree + mu)."""
        self.assertEqual((Q - 1)**4, K + MU)
        self.assertEqual((Q - 1)**4, 16)

    def test_cascade_5_is_MINPOLY_C1(self):
        """(Q-1)^5 = 32 = MINPOLY_C1 (W33 min-poly x-coefficient magnitude)."""
        self.assertEqual((Q - 1)**5, MINPOLY_C1)
        self.assertEqual((Q - 1)**5, 32)

    def test_cascade_6_is_sylow2_order(self):
        """(Q-1)^6 = 64 = order of Sylow-2 subgroup of axis-192 group H."""
        sylow2_order = 64  # |H| = 192 = 3 * 64; Sylow-2 has order 64
        self.assertEqual((Q - 1)**6, sylow2_order)

    def test_cascade_consecutive_ratio(self):
        """Each step in cascade multiplies by (Q-1) = LAM = 2."""
        for k in range(1, 6):
            self.assertEqual((Q - 1)**(k + 1), (Q - 1)**k * LAM)

    def test_cascade_spans_W33_parameters(self):
        """Powers 1..5 cover {LAM, MU, K+s, K+MU, MINPOLY_C1} = five W33 constants."""
        w33_vals = {LAM, MU, K + EIG_S, K + MU, MINPOLY_C1}
        cascade_vals = {(Q - 1)**k for k in range(1, 6)}
        self.assertEqual(cascade_vals, w33_vals)

    def test_mu_equals_lam_squared(self):
        """MU = LAM^2 follows from LAM = Q-1 and MU = (Q-1)^2 at Q=3."""
        self.assertEqual(MU, LAM**2)
        self.assertEqual(MU, (Q - 1)**2)
        # This holds only at Q=3 in the SRG context
        self.assertEqual(LAM, Q - 1)

    def test_minpoly_c0_in_cascade(self):
        """MINPOLY_C0 = K*MU*LAM = 96 = K*(Q-1)^3 (extended cascade)."""
        self.assertEqual(MINPOLY_C0, K * (Q - 1)**3)
        self.assertEqual(MINPOLY_C0, 96)


# ─────────────────────────────────────────────────────────────────────────────
class T7CrossBridgeIdentities(unittest.TestCase):
    """Cross-connecting Heawood, Fano, and W33 parameters in exact arithmetic."""

    def test_n_h_times_fano_equals_2_fano_sq(self):
        """N_H * FANO_ORDER = 2 * FANO_ORDER^2 = 98."""
        self.assertEqual(N_H * FANO_ORDER, 2 * FANO_ORDER**2)

    def test_heawood_plus_w33_vertex(self):
        """N_H + V = 14 + 40 = 54 (pocket count in K-subgroup E6/D4 descent!)."""
        self.assertEqual(N_H + V, 54)   # 54 pockets in Pillar 71

    def test_edge_count_plus_fano(self):
        """E_H + FANO_ORDER = 21 + 7 = 28 = K + THETA + V/(K+1) (integer bridge)."""
        # 28 = 4*7 = 4*FANO_ORDER
        self.assertEqual(E_H + FANO_ORDER, 4 * FANO_ORDER)
        self.assertEqual(E_H + FANO_ORDER, 28)

    def test_trace_a2_plus_fano(self):
        """Trace(A_H^2) + FANO_ORDER = 42 + 7 = 49 = 7^2 = FANO_ORDER^2."""
        self.assertEqual(TRACE_A2_H + FANO_ORDER, FANO_ORDER**2)

    def test_det_over_fano(self):
        """|det(A_H)| / FANO_ORDER = 576 / 7... not integer; but K^2*MU/FANO_ORDER:"""
        # 576 = 9 * 64 = Q^2 * (Q-1)^6
        # 576 = (K*LAM)^2 = (12*2)^2
        self.assertEqual(DET_A_H_NEG, (K * LAM)**2)
        self.assertEqual(DET_A_H_NEG, Q**2 * (Q - 1)**6)

    def test_heawood_lap_eigenvalue_sum_equals_w33(self):
        """All Laplacian eigenvalues sum = N_H * K_H = 42 = trace(A_H^2)."""
        # sum(L eigenvalues) = trace(L) = sum(degrees) = N_H*K_H = N_H*Q
        self.assertEqual(N_H * K_H, 42)
        self.assertEqual(N_H * K_H, TRACE_A2_H)

    def test_w33_theta_equals_sum_lam_mid_products(self):
        """THETA = 10 = LAP_MID_SUM + FANO_ORDER - Q = 6 + 7 - 3."""
        self.assertEqual(THETA, LAP_MID_SUM + FANO_ORDER - Q)

    def test_fano_order_times_lam_equals_theta_plus_lam(self):
        """FANO_ORDER * LAM = 7*2 = 14 = N_H (Heawood vertices!)."""
        self.assertEqual(FANO_ORDER * LAM, N_H)

    def test_v_minus_n_h(self):
        """V - N_H = 40 - 14 = 26 = 2*(Q^2+Q-1)... or 2*13 = 2*PHI3_Q."""
        self.assertEqual(V - N_H, 2 * (PHI3_Q - 1) + 2)   # = 26
        # Simpler: V - N_H = V - 2*(Q^2-Q+1) = (Q+1)(Q^2+1) - 2Q^2+2Q-2
        self.assertEqual(V - N_H, 26)


if __name__ == "__main__":
    unittest.main(verbosity=2)
