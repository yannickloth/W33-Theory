"""
Phase CLXXI: Seidel Matrix, Two-Graph, and Switching Classes of W(3,3)

The Seidel matrix S = J - I - 2A replaces adjacencies with -1, non-adjacencies with +1.
Its spectrum reveals a two-graph structure and deep Q-formulas.

Key discoveries:
  - S eigenvalues: sigma0=5Q=15 (x1), sigma1=-(2Q-1)=-5 (x24), sigma2=2Q+1=7 (x15)
  - sigma0 + sigma1 + sigma2 = K + MU + 1 = 17 (sum = degree + mu + 1 — stunning!)
  - sigma0*sigma1 + sigma0*sigma2 + sigma1*sigma2 = sigma1 = -5 (e2 = sigma1!)
  - sigma0 - sigma2 = 2*MU = 8 (gap = twice mu)
  - sigma0 / |sigma1| = Q = 3 (ratio = field order!)
  - |sigma1| * sigma2 = V - MU - 1 = 35 (product = v - mu - 1!)
  - S^2 = 33I - 4A + 6J; entries: diag=V-1=39, adj=2, non=6
  - Two-graph N- = 4480 = triangles(160) + one-edge-triples(4320)
  - N- = C(V,3)/2 - tr(S^3)/12 = 4940 - 460 = 4480
  - #one-edge-triples = (V*K/2) * Q^2*(Q-1) = 240 * 18 = 4320
"""

from fractions import Fraction

# === W(3,3) parameters ===
Q = 3
V = 40
K = 12
LAM = 2
MU = 4

EIG_K = K
EIG_R = 2
EIG_S = -4

MUL_K = 1
MUL_R = 24
MUL_S = 15

# Seidel eigenvalues
SIGMA0 = V - 1 - 2 * K     # = 15 = 5Q   (multiplicity 1)
SIGMA1 = -1 - 2 * EIG_R    # = -5 = -(2Q-1)  (multiplicity MUL_R=24)
SIGMA2 = -1 - 2 * EIG_S    # = 7  = 2Q+1  (multiplicity MUL_S=15)


# ============================================================
class TestT1_SeidelEigenvalues:
    """Seidel eigenvalues sigma_i = -1 - 2*theta_i (J acts 0 on r,s eigenspaces)."""

    def test_sigma0_from_eigenvalue_k(self):
        # sigma0 = V - 1 - 2K = 40 - 1 - 24 = 15
        assert SIGMA0 == V - 1 - 2 * EIG_K

    def test_sigma1_from_eigenvalue_r(self):
        # sigma1 = -1 - 2*r = -1 - 4 = -5 (J acts as 0 on r-eigenspace)
        assert SIGMA1 == -1 - 2 * EIG_R

    def test_sigma2_from_eigenvalue_s(self):
        # sigma2 = -1 - 2*s = -1 + 8 = 7 (J acts as 0 on s-eigenspace)
        assert SIGMA2 == -1 - 2 * EIG_S

    def test_sigma0_equals_5Q(self):
        # sigma0 = 5Q = 15 (Seidel main eigenvalue = 5 times field order!)
        assert SIGMA0 == 5 * Q

    def test_sigma1_equals_minus_2Q_minus_1(self):
        # sigma1 = -(2Q-1) = -5 (compact Q-formula)
        assert SIGMA1 == -(2 * Q - 1)

    def test_sigma2_equals_2Q_plus_1(self):
        # sigma2 = 2Q+1 = 7 (compact Q-formula)
        assert SIGMA2 == 2 * Q + 1

    def test_multiplicities_sum_to_V(self):
        # 1 + 24 + 15 = 40 = V
        assert MUL_K + MUL_R + MUL_S == V

    def test_trace_S_is_zero(self):
        # tr(S) = sigma0 + MUL_R*sigma1 + MUL_S*sigma2 = 15 - 120 + 105 = 0
        assert MUL_K * SIGMA0 + MUL_R * SIGMA1 + MUL_S * SIGMA2 == 0


class TestT2_SeidelElementarySymmetricPolynomials:
    """Seidel eigenvalue identities: e1, e2, e3 of {sigma0, sigma1, sigma2}."""

    def test_e1_sum_equals_K_plus_MU_plus_1(self):
        # sigma0 + sigma1 + sigma2 = 15 - 5 + 7 = 17 = K + MU + 1 (degree + mu + 1!)
        assert SIGMA0 + SIGMA1 + SIGMA2 == K + MU + 1

    def test_e2_equals_sigma1(self):
        # sigma0*sigma1 + sigma0*sigma2 + sigma1*sigma2 = -75 + 105 - 35 = -5 = sigma1
        # (the e2 elementary symmetric poly EQUALS sigma1 — stunning!)
        e2 = SIGMA0 * SIGMA1 + SIGMA0 * SIGMA2 + SIGMA1 * SIGMA2
        assert e2 == SIGMA1

    def test_e3_product(self):
        # sigma0 * sigma1 * sigma2 = 15 * (-5) * 7 = -525
        assert SIGMA0 * SIGMA1 * SIGMA2 == -525

    def test_e3_as_Q_formula(self):
        # -525 = -(5Q)(Q+2)(2Q+1) = -15*5*7
        assert SIGMA0 * SIGMA1 * SIGMA2 == -(5 * Q) * (Q + 2) * (2 * Q + 1)

    def test_sigma0_minus_sigma2_equals_2MU(self):
        # sigma0 - sigma2 = 15 - 7 = 8 = 2*MU (gap = twice mu!)
        assert SIGMA0 - SIGMA2 == 2 * MU

    def test_sigma0_over_abs_sigma1_equals_Q(self):
        # sigma0 / |sigma1| = 15 / 5 = 3 = Q (ratio = field order!)
        assert SIGMA0 // abs(SIGMA1) == Q
        assert SIGMA0 % abs(SIGMA1) == 0

    def test_abs_sigma1_times_sigma2_equals_V_minus_MU_minus_1(self):
        # |sigma1| * sigma2 = 5 * 7 = 35 = V - MU - 1 = 40 - 4 - 1 (!)
        assert abs(SIGMA1) * SIGMA2 == V - MU - 1

    def test_minimal_polynomial_coefficients(self):
        # Minimal poly of S: (x-15)(x+5)(x-7) = x^3 - 17x^2 - 5x + 525
        # coefficient of x: e2(sigma0,sigma1,sigma2) = -5 = sigma1
        e2 = SIGMA0 * SIGMA1 + SIGMA0 * SIGMA2 + SIGMA1 * SIGMA2
        assert e2 == -5
        # constant: -e3 = 525
        assert -(SIGMA0 * SIGMA1 * SIGMA2) == 525


class TestT3_SeidelTraceFormulas:
    """Traces of S, S^2, S^3 from eigenvalue spectrum."""

    def test_tr_S_is_zero(self):
        # All diagonal entries of S are 0
        assert MUL_K * SIGMA0 + MUL_R * SIGMA1 + MUL_S * SIGMA2 == 0

    def test_tr_S2_equals_V_times_V_minus_1(self):
        # tr(S^2) = S has +-1 off-diagonal so S^2_{ii} = sum_j S_{ij}^2 = V-1
        # tr(S^2) = V*(V-1) = 40*39 = 1560
        tr_S2 = MUL_K * SIGMA0**2 + MUL_R * SIGMA1**2 + MUL_S * SIGMA2**2
        assert tr_S2 == V * (V - 1)

    def test_tr_S2_value(self):
        tr_S2 = MUL_K * SIGMA0**2 + MUL_R * SIGMA1**2 + MUL_S * SIGMA2**2
        assert tr_S2 == 1560

    def test_tr_S2_components(self):
        # 225 + 24*25 + 15*49 = 225 + 600 + 735 = 1560
        assert 1 * 225 + 24 * 25 + 15 * 49 == 1560

    def test_tr_S3_value(self):
        # tr(S^3) = 1*15^3 + 24*(-5)^3 + 15*7^3 = 3375 - 3000 + 5145 = 5520
        tr_S3 = MUL_K * SIGMA0**3 + MUL_R * SIGMA1**3 + MUL_S * SIGMA2**3
        assert tr_S3 == 5520

    def test_tr_S3_components(self):
        # 1*3375 + 24*(-125) + 15*343 = 3375 - 3000 + 5145 = 5520
        assert 1 * 3375 + 24 * (-125) + 15 * 343 == 5520

    def test_tr_S3_divisible_by_6(self):
        # tr(S^3)/6 counts triples (each counted 6 ways by symmetry)
        tr_S3 = MUL_K * SIGMA0**3 + MUL_R * SIGMA1**3 + MUL_S * SIGMA2**3
        assert tr_S3 % 6 == 0

    def test_tr_S3_over_6(self):
        # tr(S^3)/6 = 5520/6 = 920
        tr_S3 = MUL_K * SIGMA0**3 + MUL_R * SIGMA1**3 + MUL_S * SIGMA2**3
        assert tr_S3 // 6 == 920


class TestT4_SeidelSquareMatrix:
    """S^2 lies in the Bose-Mesner algebra: S^2 = 33I - 4A + 6J."""

    def test_S2_bose_mesner_coefficients(self):
        # S^2 = alpha*I + beta*A + gamma*J with:
        # alpha+beta*r = sigma1^2 = 25; alpha+beta*s = sigma2^2 = 49
        # beta*(r-s) = 25-49 = -24; r-s=6; beta = -4
        # alpha = 25 - beta*r = 25+8 = 33
        # gamma = (sigma0^2 - alpha - beta*k)/V = (225-33+48)/40 = 240/40 = 6
        beta = (SIGMA1**2 - SIGMA2**2) // (EIG_R - EIG_S)
        assert beta == -4
        alpha = SIGMA1**2 - beta * EIG_R
        assert alpha == 33
        gamma = (SIGMA0**2 - alpha - beta * EIG_K) // V
        assert gamma == 6

    def test_S2_diagonal_entry(self):
        # (S^2)_{ii} = alpha*1 + beta*0 + gamma*1 = 33 + 6 = 39 = V-1
        alpha, beta, gamma = 33, -4, 6
        assert alpha + gamma == V - 1

    def test_S2_adjacent_entry(self):
        # (S^2)_{i~j} = alpha*0 + beta*1 + gamma*1 = -4 + 6 = 2
        alpha, beta, gamma = 33, -4, 6
        assert beta + gamma == 2

    def test_S2_nonadjacent_entry(self):
        # (S^2)_{i not adj j} = alpha*0 + beta*0 + gamma*1 = 6
        alpha, beta, gamma = 33, -4, 6
        assert gamma == 6

    def test_S2_diagonal_is_V_minus_1(self):
        # (S^2)_{ii} = sum_j S_{ij}^2 = V-1 (each off-diagonal entry is +-1)
        assert 33 + 6 == V - 1

    def test_S2_adjacent_from_combinatorics(self):
        # For i~j: common nbrs contribute (+1), diff-nbrs contribute (-1), mutual-non contribute (+1)
        # LAM*(+1) + (K-1-LAM)*(-1) + (K-1-LAM)*(-1) + (V-2-2*(K-1-LAM)-LAM)*(+1)
        common = LAM
        diff_i = K - 1 - LAM   # = 9 = Q^2
        diff_j = K - 1 - LAM
        mutual_non = V - 2 - 2 * (K - 1 - LAM) - LAM   # = 38 - 18 - 2 = 18
        result = common * 1 + diff_i * (-1) + diff_j * (-1) + mutual_non * 1
        assert result == 2

    def test_S2_nonadjacent_from_combinatorics(self):
        # For i not adj j: common nbrs MU (+1), diff nbrs K-MU (-1), mutual non K-MU (-1)
        common = MU   # = 4
        diff_i = K - MU   # = 8
        diff_j = K - MU
        mutual_non = V - 2 - MU - 2 * (K - MU)   # = 38 - 4 - 16 = 18
        result = common * 1 + diff_i * (-1) + diff_j * (-1) + mutual_non * 1
        assert result == 6


class TestT5_TwoGraphTripleCounting:
    """Two-graph T(W33): triples with S_{ij}S_{jk}S_{ki} = -1."""

    def test_total_triples(self):
        # C(40,3) = 40*39*38/6 = 9880
        assert V * (V - 1) * (V - 2) // 6 == 9880

    def test_N_minus_from_trace(self):
        # N- = C(V,3)/2 - tr(S^3)/12 = 4940 - 460 = 4480
        CvC3 = V * (V - 1) * (V - 2) // 6
        tr_S3 = MUL_K * SIGMA0**3 + MUL_R * SIGMA1**3 + MUL_S * SIGMA2**3
        assert CvC3 % 2 == 0
        assert tr_S3 % 12 == 0
        N_minus = CvC3 // 2 - tr_S3 // 12
        assert N_minus == 4480

    def test_triangles_are_negative_triples(self):
        # For a triangle {i,j,k}: S_{ij}=S_{jk}=S_{ki}=-1; product=-1 (in T)
        triangles = V * K * LAM // 6
        assert triangles == 160

    def test_one_edge_triples_are_negative(self):
        # 1-edge triple {i,j,k} with i~j, i not~k, j not~k:
        # S_{ij}=-1, S_{ik}=+1, S_{jk}=+1; product=-1 (in T)
        # For each edge (i,j): mutual non-nbrs k = V-K-1 - (K-LAM-1) = Q^3 - Q^2 = 18
        edges = V * K // 2
        mutual_non_nbrs = (V - K - 1) - (K - LAM - 1)   # = Q^3 - Q^2 = 27 - 9 = 18
        assert mutual_non_nbrs == Q**3 - Q**2
        assert mutual_non_nbrs == Q**2 * (Q - 1)
        assert edges * mutual_non_nbrs == 4320

    def test_N_minus_splits_as_triangles_plus_one_edge(self):
        # N- = triangles + 1-edge triples = 160 + 4320 = 4480
        triangles = V * K * LAM // 6
        one_edge = (V * K // 2) * (Q**3 - Q**2)
        assert triangles + one_edge == 4480

    def test_one_edge_triples_via_Q_formula(self):
        # 4320 = (V*K/2) * Q^2*(Q-1) = 240 * 18 = 4320
        assert (V * K // 2) * Q**2 * (Q - 1) == 4320

    def test_N_plus_value(self):
        # N+ = C(V,3) - N- = 9880 - 4480 = 5400
        CvC3 = V * (V - 1) * (V - 2) // 6
        assert CvC3 - 4480 == 5400

    def test_N_minus_plus_N_plus_is_C_V_3(self):
        # N- + N+ = C(V,3)
        assert 4480 + 5400 == V * (V - 1) * (V - 2) // 6

    def test_tr_S3_via_two_graph(self):
        # tr(S^3) = 6*(C(V,3) - 2*N-) = 6*(9880 - 8960) = 6*920 = 5520
        CvC3 = V * (V - 1) * (V - 2) // 6
        N_minus = 4480
        assert 6 * (CvC3 - 2 * N_minus) == 5520

    def test_two_graph_triples_460_from_S3(self):
        # tr(S^3)/12 = 460 = triangles/... = 460
        tr_S3 = 5520
        assert tr_S3 // 12 == 460


class TestT6_SeidelQFormulaConnections:
    """Cross-phase connections: Seidel eigenvalues in terms of Q."""

    def test_sigma0_is_5Q(self):
        assert SIGMA0 == 5 * Q

    def test_sigma1_is_minus_2Q_minus_1(self):
        assert SIGMA1 == -(2 * Q - 1)

    def test_sigma2_is_2Q_plus_1(self):
        assert SIGMA2 == 2 * Q + 1

    def test_sum_of_seidel_eigs_is_K_plus_MU_plus_1(self):
        # 15 - 5 + 7 = 17 = K + MU + 1 (degree + mu + 1!)
        assert SIGMA0 + SIGMA1 + SIGMA2 == K + MU + 1

    def test_mutual_non_nbrs_in_1edge_triple_is_Q2_times_Q_minus_1(self):
        # 18 = Q^2*(Q-1) = 9*2 = 18 (from V-K-1-K+LAM+1 = Q^3 - Q^2)
        assert Q**2 * (Q - 1) == 18
        assert (V - K - 1) - (K - LAM - 1) == 18

    def test_two_graph_N_minus_prime_factorization(self):
        # N- = 4480 = 2^7 * 5 * 7 = 128 * 35
        N_minus = 4480
        assert N_minus == 2**7 * 5 * 7
        assert N_minus == 128 * 35

    def test_two_graph_N_plus_prime_factorization(self):
        # N+ = 5400 = 2^3 * 3^3 * 5^2 = 8 * 675
        N_plus = 5400
        assert N_plus == 2**3 * 3**3 * 5**2

    def test_tr_S2_over_2_is_V_choose_2(self):
        # tr(S^2)/2 = 1560/2 = 780 = C(V,2) = V*(V-1)/2
        tr_S2 = MUL_K * SIGMA0**2 + MUL_R * SIGMA1**2 + MUL_S * SIGMA2**2
        assert tr_S2 // 2 == V * (V - 1) // 2

    def test_seidel_encodes_A_and_complement(self):
        # S = J - I - 2A encodes both W33 and its complement:
        # S_{ij} = -1 iff i~j (W33 edge); +1 iff i not~j (complement edge)
        # Non-adj count V-K-1 = Q^3 = 27
        assert V - K - 1 == Q**3

    def test_sigma0_sigma1_sigma2_are_distinct_odd(self):
        # All three Seidel eigenvalues are odd integers
        for sigma in (SIGMA0, SIGMA1, SIGMA2):
            assert sigma % 2 != 0

    def test_seidel_range(self):
        # sigma1 < 0 < sigma2 < sigma0
        assert SIGMA1 < 0
        assert 0 < SIGMA2 < SIGMA0
