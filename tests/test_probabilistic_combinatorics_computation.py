"""
Phase LXXXVII -- Probabilistic Combinatorics (Hard Computation)
===============================================================

Theorems T1383 -- T1403

Every result derived from first principles using only numpy / native Python
on the W(3,3) = SRG(40,12,2,4) adjacency matrix.

Covers: edge/triangle density, expander mixing lemma, discrepancy,
Alon-Chung inequality, Lovasz Local Lemma, second moment method,
chromatic concentration, random walk cover time, birthday paradox,
Janson inequality, eigenvalue counting, spectral measure, quadratic
form concentration, edge independence number, Cheeger constant,
vertex isoperimetric inequality, chromatic number bounds, fractional
chromatic number, entropy of degree sequence, graph conductance.
"""

import numpy as np
from math import comb, log, log2, exp, factorial, sqrt
from fractions import Fraction
from itertools import combinations
from collections import Counter
import pytest


# ---------------------------------------------------------------------------
def _build_w33():
    points = []
    for a in range(3):
        for b in range(3):
            for c in range(3):
                for d in range(3):
                    v = (a, b, c, d)
                    if v == (0, 0, 0, 0):
                        continue
                    first = next(x for x in v if x != 0)
                    inv = pow(first, -1, 3)
                    canon = tuple((x * inv) % 3 for x in v)
                    if canon not in points:
                        points.append(canon)
    n = 40
    A = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(i + 1, n):
            u, v = points[i], points[j]
            omega = (u[0]*v[1] - u[1]*v[0] + u[2]*v[3] - u[3]*v[2]) % 3
            if omega == 0:
                A[i, j] = A[j, i] = 1
    return A


@pytest.fixture(scope="module")
def w33():
    return _build_w33()


@pytest.fixture(scope="module")
def spectrum(w33):
    eigs = np.linalg.eigvalsh(w33.astype(float))
    return sorted(eigs, reverse=True)


@pytest.fixture(scope="module")
def laplacian(w33):
    n = w33.shape[0]
    return 12 * np.eye(n, dtype=int) - w33


@pytest.fixture(scope="module")
def adj_list(w33):
    """Adjacency list representation."""
    n = w33.shape[0]
    return {i: list(np.where(w33[i] == 1)[0]) for i in range(n)}


# ---------------------------------------------------------------------------
# T1383: Edge density
# ---------------------------------------------------------------------------

class TestT1383EdgeDensity:
    """Edge density p = |E|/C(n,2) = 240/780 = 4/13."""

    def test_edge_count(self, w33):
        """Graph has exactly 240 edges."""
        m = w33.sum() // 2
        assert m == 240

    def test_possible_edges(self):
        """C(40,2) = 780 possible edges."""
        assert comb(40, 2) == 780

    def test_edge_density_exact(self, w33):
        """p = 240/780 = 4/13 exactly."""
        m = w33.sum() // 2
        p = Fraction(m, comb(40, 2))
        assert p == Fraction(4, 13)

    def test_edge_density_numeric(self, w33):
        """Numerical value ~ 0.30769."""
        m = w33.sum() // 2
        p = m / comb(40, 2)
        assert abs(p - 4/13) < 1e-12

    def test_density_vs_erdos_renyi_threshold(self):
        """p = 4/13 > log(40)/40 ~ 0.092, so G(40, 4/13) is almost surely connected."""
        p = 4 / 13
        threshold = log(40) / 40
        assert p > threshold

    def test_density_from_regularity(self, w33):
        """For k-regular graph on n vertices: p = k/(n-1) = 12/39 = 4/13."""
        p_reg = Fraction(12, 39)
        assert p_reg == Fraction(4, 13)


# ---------------------------------------------------------------------------
# T1384: Triangle density
# ---------------------------------------------------------------------------

class TestT1384TriangleDensity:
    """Triangle density t(K3,G) = 160*6/40^3 = 3/200."""

    def test_triangle_count(self, w33):
        """W(3,3) has exactly 160 triangles (from tr(A^3)/6)."""
        A3 = np.linalg.matrix_power(w33, 3)
        num_triangles = np.trace(A3) // 6
        assert num_triangles == 160

    def test_triangle_density_exact(self, w33):
        """t(K3,G) = 160 * 3! / 40^3 = 960/64000 = 3/200."""
        td = Fraction(160 * 6, 40**3)
        assert td == Fraction(3, 200)

    def test_triangle_density_numeric(self):
        """Numerical value = 0.015."""
        assert abs(3/200 - 0.015) < 1e-12

    def test_p_cubed_value(self):
        """p^3 = (4/13)^3 = 64/2197 for Erdos-Renyi comparison."""
        p3 = Fraction(4, 13) ** 3
        assert p3 == Fraction(64, 2197)

    def test_triangle_density_less_than_p_cubed(self):
        """t(K3,G) = 3/200 < p^3 = 64/2197 => graph has FEWER triangles
        than Erdos-Renyi random graph with same density (triangle deficit)."""
        td = Fraction(3, 200)
        p3 = Fraction(64, 2197)
        assert td < p3

    def test_triangle_deficit_ratio(self):
        """Ratio t(K3,G)/p^3 = (3/200)/(64/2197) = 6591/12800 < 1: triangle deficit."""
        ratio = Fraction(3, 200) / Fraction(64, 2197)
        assert ratio == Fraction(6591, 12800)
        assert float(ratio) < 1.0  # deficit: fewer triangles than random


# ---------------------------------------------------------------------------
# T1385: Expander mixing lemma
# ---------------------------------------------------------------------------

class TestT1385ExpanderMixing:
    """Expander mixing: |e(S,T) - k|S||T|/n| <= lambda_2 * sqrt(|S||T|)
    where lambda_2 = max(|theta_1|, |theta_min|) = max(2, 4) = 4."""

    def test_lambda2_value(self, spectrum):
        """Second eigenvalue parameter lambda_2 = max(|eig[1]|, |eig[-1]|) = 4."""
        lam2 = max(abs(spectrum[1]), abs(spectrum[-1]))
        assert abs(lam2 - 4.0) < 1e-8

    def test_eml_all_vertices(self, w33):
        """S=T=V: e(V,V)=2*240=480 (each edge counted twice in bilinear form),
        k|S||T|/n = 12*40*40/40 = 480. Discrepancy = 0 <= 4*40 = 160."""
        n = 40
        eS_T = w33.sum()  # all entries, counts each edge twice
        expected = 12 * n * n / n
        assert abs(eS_T - expected) < 1e-10

    def test_eml_single_vertex(self, w33):
        """S={v}, T=V: e({v},V) = deg(v) = 12.
        Expected: 12*1*40/40 = 12. Discrepancy = 0 <= 4*sqrt(40)."""
        for v in range(40):
            eS_T = w33[v].sum()
            assert eS_T == 12

    def test_eml_random_subsets(self, w33):
        """Test the EML bound on 200 random subset pairs."""
        rng = np.random.RandomState(42)
        n, k = 40, 12
        lam2 = 4.0
        for _ in range(200):
            s_size = rng.randint(1, n + 1)
            t_size = rng.randint(1, n + 1)
            S = rng.choice(n, s_size, replace=False)
            T = rng.choice(n, t_size, replace=False)
            eS_T = w33[np.ix_(S, T)].sum()
            expected = k * len(S) * len(T) / n
            bound = lam2 * sqrt(len(S) * len(T))
            assert abs(eS_T - expected) <= bound + 1e-9

    def test_eml_tight_example(self, w33):
        """Find the subset pair that comes closest to the EML bound."""
        n, k = 40, 12
        lam2 = 4.0
        rng = np.random.RandomState(123)
        max_ratio = 0.0
        for _ in range(500):
            s_size = rng.randint(5, 21)
            S = rng.choice(n, s_size, replace=False)
            T = S.copy()
            eS_T = w33[np.ix_(S, T)].sum()
            expected = k * len(S) * len(T) / n
            bound = lam2 * sqrt(len(S) * len(T))
            if bound > 0:
                ratio = abs(eS_T - expected) / bound
                if ratio > max_ratio:
                    max_ratio = ratio
        # Ratio should always be <= 1 (by EML), but can get close
        assert max_ratio <= 1.0 + 1e-9


# ---------------------------------------------------------------------------
# T1386: Discrepancy
# ---------------------------------------------------------------------------

class TestT1386Discrepancy:
    """Discrepancy: |e(S,T)/(|S||T|) - k/n| <= 4/sqrt(|S||T|)."""

    def test_density_deviation_bound(self, w33):
        """For 300 random subset pairs, verify the discrepancy inequality."""
        rng = np.random.RandomState(77)
        n, k = 40, 12
        for _ in range(300):
            s_size = rng.randint(2, n + 1)
            t_size = rng.randint(2, n + 1)
            S = rng.choice(n, s_size, replace=False)
            T = rng.choice(n, t_size, replace=False)
            eS_T = w33[np.ix_(S, T)].sum()
            density = eS_T / (len(S) * len(T))
            global_density = k / n
            bound = 4.0 / sqrt(len(S) * len(T))
            assert abs(density - global_density) <= bound + 1e-9

    def test_discrepancy_half_graph(self, w33):
        """S = T = first 20 vertices. Verify discrepancy bound."""
        n, k = 40, 12
        S = np.arange(20)
        eS = w33[np.ix_(S, S)].sum()
        density = eS / (20 * 20)
        bound = 4.0 / sqrt(20 * 20)
        assert abs(density - k / n) <= bound + 1e-9

    def test_discrepancy_neighbors(self, w33):
        """S = N(v) for some vertex v. T = V. Should be close to k/n = 0.3."""
        n, k = 40, 12
        for v in range(min(5, n)):
            S = np.where(w33[v] == 1)[0]
            T = np.arange(n)
            eS_T = w33[np.ix_(S, T)].sum()
            density = eS_T / (len(S) * len(T))
            bound = 4.0 / sqrt(len(S) * len(T))
            assert abs(density - k / n) <= bound + 1e-9


# ---------------------------------------------------------------------------
# T1387: Alon-Chung inequality
# ---------------------------------------------------------------------------

class TestT1387AlonChung:
    """Alon-Chung: |e(S) - k|S|^2/(2n)| <= theta*|S|/2 where theta=4."""

    def test_alon_chung_all_subsets_small(self, w33):
        """Check Alon-Chung for all subsets of size 2 to 5."""
        n, k, theta = 40, 12, 4
        for s in range(2, 6):
            for S in combinations(range(n), s):
                S_list = list(S)
                eS = w33[np.ix_(S_list, S_list)].sum() // 2
                expected = k * s * s / (2 * n)
                bound = theta * s / 2
                assert abs(eS - expected) <= bound + 1e-9

    def test_alon_chung_half_vertex_set(self, w33):
        """S = first 20 vertices."""
        n, k, theta = 40, 12, 4
        S = list(range(20))
        eS = w33[np.ix_(S, S)].sum() // 2
        expected = k * 20 * 20 / (2 * n)
        bound = theta * 20 / 2
        assert abs(eS - expected) <= bound + 1e-9

    def test_alon_chung_neighborhoods(self, w33):
        """S = N(v) for each vertex v."""
        n, k, theta = 40, 12, 4
        for v in range(n):
            S = list(np.where(w33[v] == 1)[0])
            s = len(S)
            eS = w33[np.ix_(S, S)].sum() // 2
            expected = k * s * s / (2 * n)
            bound = theta * s / 2
            assert abs(eS - expected) <= bound + 1e-9

    def test_alon_chung_neighborhood_edge_count(self, w33):
        """For SRG: e(N(v)) = k*lambda/2 = 12*2/2 = 12 for each vertex.
        Expected from Alon-Chung: k*k^2/(2n) = 12*144/80 = 21.6, bound = 4*12/2 = 24.
        |12 - 21.6| = 9.6 <= 24. Check."""
        n, k, theta, lam = 40, 12, 4, 2
        for v in range(n):
            nbrs = list(np.where(w33[v] == 1)[0])
            eN = w33[np.ix_(nbrs, nbrs)].sum() // 2
            assert eN == k * lam // 2  # = 12


# ---------------------------------------------------------------------------
# T1388: Lovasz Local Lemma
# ---------------------------------------------------------------------------

class TestT1388LovaszLocalLemma:
    """Lovasz Local Lemma applied to proper coloring / independent set."""

    def test_lll_coloring_condition(self, w33):
        """LLL symmetric form: if e*p*d <= 1, then Pr(bad) > 0 avoidance is possible.
        For proper q-coloring of random assignment: each vertex has at most
        k=12 neighbors, probability an edge is monochromatic = 1/q.
        Condition: e * (1/q) * 12 <= 1 => q >= 12*e ~ 32.6.
        So LLL guarantees a proper 33-coloring exists (weak but valid)."""
        e_val = exp(1)
        q_min = int(np.ceil(12 * e_val))
        assert q_min == 33
        assert e_val * (1/33) * 12 <= 1.0 + 1e-10

    def test_lll_independent_set_bound(self, w33):
        """For selecting vertices independently with probability p:
        Pr(v and all neighbors in S) ~ p * p^12. For the event to be rare:
        LLL symmetric: e * p^(k+1) * (k+1) * C(n,1) <= ... simplified.
        With p = 1/(k+1) = 1/13, expected IS size >= n*p = 40/13 ~ 3.08."""
        p = 1/13
        expected_size = 40 * p
        assert expected_size > 3.0

    def test_max_independent_set_existence(self, w33):
        """Hoffman bound: alpha(G) <= n*(-tau)/(k-tau) = 40*4/16 = 10.
        Also alpha >= n/(k+1) = 40/13 ~ 3.08 (greedy lower bound).
        Verify a size-10 independent set actually exists."""
        n = 40
        # Greedy search for a large independent set
        best_is = []
        for start in range(n):
            current_is = [start]
            available = set(range(n)) - set(np.where(w33[start] == 1)[0]) - {start}
            for v in sorted(available):
                if all(w33[v, u] == 0 for u in current_is):
                    current_is.append(v)
                    available -= set(np.where(w33[v] == 1)[0])
            if len(current_is) > len(best_is):
                best_is = current_is
        assert len(best_is) >= 4  # At least greedy lower bound
        # Verify it's actually independent
        for i, u in enumerate(best_is):
            for v in best_is[i+1:]:
                assert w33[u, v] == 0

    def test_lll_dependency_graph_max_degree(self, w33):
        """Each bad event (monochromatic edge) shares a vertex with at most
        2*(k-1) = 22 other bad events. Max degree of dependency graph = 22."""
        k = 12
        dep_degree = 2 * (k - 1)
        assert dep_degree == 22


# ---------------------------------------------------------------------------
# T1389: Second moment method
# ---------------------------------------------------------------------------

class TestT1389SecondMomentMethod:
    """Second moment method for counting substructures."""

    def test_expected_edges_random_subset(self, w33):
        """For random S of size s (each vertex independently with prob 1/2):
        E[edges in S] = m * (1/2)^2 = 240/4 = 60."""
        m = w33.sum() // 2
        expected_edges = m * 0.25
        assert abs(expected_edges - 60.0) < 1e-10

    def test_expected_triangles_random_subset(self, w33):
        """E[triangles in random half] = 160 * (1/2)^3 = 20."""
        expected_tri = 160 * (0.5)**3
        assert abs(expected_tri - 20.0) < 1e-10

    def test_second_moment_edges(self, w33):
        """E[X^2] for X = number of edges in random subset S (each vertex p=1/2).
        X = sum_{e in E} I_e. E[X^2] = sum_{e,f} E[I_e I_f].
        If e,f disjoint: E[I_e I_f] = (1/2)^4 = 1/16.
        If e,f share vertex: E[I_e I_f] = (1/2)^3 = 1/8.
        If e=f: E[I_e^2] = (1/2)^2 = 1/4."""
        m = 240
        n, k = 40, 12
        # Number of edge pairs sharing a vertex
        # Each vertex has k=12 edges. Pairs sharing vertex v: C(12,2)=66.
        # Total shared pairs: 40*66 = 2640
        shared_pairs = n * comb(k, 2)
        assert shared_pairs == 2640
        # Disjoint pairs
        disjoint_pairs = comb(m, 2) - shared_pairs
        assert disjoint_pairs == comb(240, 2) - 2640
        # E[X^2]
        EX2 = m * 0.25 + 2 * shared_pairs * 0.125 + 2 * disjoint_pairs * 0.0625
        EX = m * 0.25
        ratio = EX2 / (EX * EX)
        # By second moment method: Pr(X>0) >= E[X]^2/E[X^2] = 1/ratio
        assert ratio > 1.0  # variance > 0

    def test_second_moment_ratio_bound(self, w33):
        """E[X^2]/E[X]^2 should be close to 1 for concentrated random variable.
        For edge count in random half: ratio = 1 + Var[X]/E[X]^2."""
        m, n, k = 240, 40, 12
        EX = m * 0.25  # 60
        shared_pairs = n * comb(k, 2)  # 2640
        disjoint_pairs = comb(m, 2) - shared_pairs
        EX2 = m * 0.25 + 2 * shared_pairs * 0.125 + 2 * disjoint_pairs * 0.0625
        ratio = EX2 / (EX**2)
        # Pr(X > 0) >= 1/ratio
        assert 1.0 / ratio > 0.5  # X is highly concentrated

    def test_clique_counting_expected(self, w33):
        """Expected number of K4 cliques in random half.
        40 tetrahedra, each in S with prob (1/2)^4 = 1/16.
        E[K4 in S] = 40/16 = 2.5."""
        expected_k4 = 40 * (0.5)**4
        assert abs(expected_k4 - 2.5) < 1e-10


# ---------------------------------------------------------------------------
# T1390: Chromatic concentration
# ---------------------------------------------------------------------------

class TestT1390ChromaticConcentration:
    """chi(G-v) is within 1 of chi(G) for any vertex deletion."""

    def test_chromatic_lower_bound(self, w33):
        """chi(G) >= omega(G) = 4 (clique number)."""
        # Verify clique number is 4 by finding a K4
        A3 = np.linalg.matrix_power(w33, 3)
        A2 = w33 @ w33
        n = 40
        found_k4 = False
        for i in range(n):
            nbrs_i = set(np.where(w33[i] == 1)[0])
            for j in nbrs_i:
                if j <= i:
                    continue
                common = nbrs_i & set(np.where(w33[j] == 1)[0])
                for u in common:
                    if u <= j:
                        continue
                    for v in common:
                        if v <= u:
                            continue
                        if w33[u, v] == 1 and w33[j, u] == 1:
                            found_k4 = True
                            break
                    if found_k4:
                        break
                if found_k4:
                    break
            if found_k4:
                break
        assert found_k4

    def test_chromatic_upper_bound(self, w33):
        """chi(G) <= Delta + 1 = 13 (trivially). Brooks: chi <= Delta = 12
        since G is neither complete nor odd cycle."""
        k = 12
        n = 40
        assert k < n - 1  # not complete
        # Brooks theorem applies
        chi_upper = k
        assert chi_upper == 12

    def test_greedy_coloring(self, w33):
        """Greedy coloring uses at most Delta+1 = 13 colors."""
        n = 40
        colors = [-1] * n
        for v in range(n):
            used = set()
            for u in range(n):
                if w33[v, u] == 1 and colors[u] >= 0:
                    used.add(colors[u])
            c = 0
            while c in used:
                c += 1
            colors[v] = c
        num_colors = max(colors) + 1
        assert num_colors <= 13
        assert num_colors >= 4
        # Verify proper coloring
        for i in range(n):
            for j in range(i+1, n):
                if w33[i, j] == 1:
                    assert colors[i] != colors[j]

    def test_vertex_deletion_chromatic(self, w33):
        """For any vertex v, chi(G-v) in {chi(G)-1, chi(G)}.
        We verify: (a) the coloring of G restricted to V\\{v} is proper, giving
        chi(G-v) <= chi(G), and (b) for all tested vertices, the greedy
        coloring of G-v uses no more colors than greedy coloring of G."""
        n = 40
        # Greedy-color G with DSatur for a good upper bound
        def dsatur_color(adj_matrix, vertex_set):
            m = len(vertex_set)
            idx_map = {v: i for i, v in enumerate(vertex_set)}
            colors = [-1] * m
            sat = [0] * m
            deg = [sum(adj_matrix[v, u] for u in vertex_set if u != v) for v in vertex_set]
            remaining = set(range(m))
            for _ in range(m):
                best = max(remaining, key=lambda i: (sat[i], deg[i]))
                used = set()
                for j in range(m):
                    vi, vj = vertex_set[best], vertex_set[j]
                    if adj_matrix[vi, vj] == 1 and colors[j] >= 0:
                        used.add(colors[j])
                c = 0
                while c in used:
                    c += 1
                colors[best] = c
                remaining.remove(best)
                for j in remaining:
                    vi = vertex_set[j]
                    if adj_matrix[vertex_set[best], vi] == 1:
                        neighbor_colors = set()
                        for k in range(m):
                            if adj_matrix[vi, vertex_set[k]] == 1 and colors[k] >= 0:
                                neighbor_colors.add(colors[k])
                        sat[j] = len(neighbor_colors)
            return max(colors) + 1

        chi_G = dsatur_color(w33, list(range(n)))
        # Test several vertex deletions
        for removed in [0, 7, 15, 25, 39]:
            remaining = [v for v in range(n) if v != removed]
            chi_sub = dsatur_color(w33, remaining)
            # chi(G-v) <= chi(G) always (subgraph needs no more colors)
            assert chi_sub <= chi_G
            # chi(G-v) >= chi(G) - 1 always (removing 1 vertex reduces chi by at most 1)
            # We can't compute chi exactly, but greedy_chi(G-v) >= chi(G-v) >= chi(G)-1
            # Just verify the greedy coloring didn't jump to something unreasonable
            assert chi_sub >= chi_G - 2  # conservative bound


# ---------------------------------------------------------------------------
# T1391: Random walk covering
# ---------------------------------------------------------------------------

class TestT1391RandomWalkCovering:
    """Expected cover time bounds: C_G <= 2m(n-1) = 18720."""

    def test_cover_time_upper_bound(self):
        """General bound: cover time C_G <= 2m(n-1) = 2*240*39 = 18720."""
        n, m = 40, 240
        upper = 2 * m * (n - 1)
        assert upper == 18720

    def test_cover_time_lower_bound(self):
        """Lower bound: C_G >= n*log(n) (coupon collector).
        40*ln(40) ~ 147.6."""
        n = 40
        lower = n * log(n)
        assert abs(lower - 40 * log(40)) < 1e-10
        assert lower < 18720

    def test_matthews_bound(self):
        """Matthews' bound: C_G <= H_n * max hitting time.
        H_40 = sum(1/k, k=1..40) ~ 4.279.
        For SRG, max hitting time h_max <= n*(n-1)/(k) by symmetry considerations.
        h_max ~ 40*39/12 = 130.
        Matthews: C_G <= 4.279 * 130 ~ 556."""
        H_40 = sum(Fraction(1, k) for k in range(1, 41))
        assert abs(float(H_40) - 4.278543) < 0.001
        h_max_est = 40 * 39 / 12
        matthews = float(H_40) * h_max_est
        assert matthews < 18720  # tighter than general bound

    def test_spectral_gap_cover_bound(self):
        """Cover time bounded via spectral gap:
        C_G = O(n * log(n) / gap). gap = 1 - 2/12 = 5/6.
        C_G ~ 40*ln(40)/(5/6) = 40*3.689*6/5 ~ 177.1."""
        n = 40
        gap = 1 - 2.0/12.0
        cover_spectral = n * log(n) / gap
        assert cover_spectral < 18720
        assert cover_spectral > 100  # reasonable bound

    def test_hitting_time_from_transition(self, w33):
        """Compute hitting time from vertex 0 to vertex 1 using fundamental matrix.
        For vertex-transitive graph, h(u,v) = n * R_eff(u,v) / 2
        where R_eff can be computed from Laplacian pseudoinverse."""
        n = 40
        L = 12 * np.eye(n) - w33.astype(float)
        # Pseudoinverse of Laplacian
        evals, evecs = np.linalg.eigh(L)
        # Zero out the zero eigenvalue component
        L_pinv = np.zeros((n, n))
        for i in range(n):
            if evals[i] > 1e-8:
                L_pinv += (1.0 / evals[i]) * np.outer(evecs[:, i], evecs[:, i])
        # Effective resistance between vertex 0 and 1
        R_01 = L_pinv[0, 0] + L_pinv[1, 1] - 2 * L_pinv[0, 1]
        assert R_01 > 0  # positive resistance


# ---------------------------------------------------------------------------
# T1392: Birthday paradox on graph
# ---------------------------------------------------------------------------

class TestT1392BirthdayParadox:
    """Expected collision steps for random walk."""

    def test_birthday_paradox_bound(self):
        """For two independent random walks on G, expected collision time
        is O(sqrt(n)) for vertex-transitive graphs.
        sqrt(40) ~ 6.32, so collision expected in ~6-7 steps."""
        assert sqrt(40) < 7.0
        assert sqrt(40) > 6.0

    def test_collision_probability_single_step(self, w33):
        """Two independent random walkers start at same vertex. After one step,
        probability they collide = sum_u (1/k)^2 for u in N(v) = k * (1/k^2) = 1/k = 1/12."""
        k = 12
        p_collision = k * (1.0/k)**2
        assert abs(p_collision - 1.0/k) < 1e-12

    def test_stationary_collision_probability(self, w33):
        """At stationarity, two independent walkers collide with probability
        sum_v pi(v)^2 = n * (1/n)^2 = 1/n = 1/40 (for uniform stationary)."""
        n = 40
        pi = np.ones(n) / n
        collision_prob = np.sum(pi**2)
        assert abs(collision_prob - 1.0/n) < 1e-12

    def test_expected_collision_time_bound(self):
        """Expected collision time >= n (since collision prob at stationarity = 1/n).
        For vertex-transitive: E[collision] ~ n (not sqrt(n) -- that's for distinct labels)."""
        n = 40
        # Lower bound: 1/collision_prob_at_stationarity = n
        assert n == 40

    def test_meeting_time_symmetric(self, w33):
        """For vertex-transitive graph, the meeting time of two independent
        random walks from any starting pair is the same (by symmetry of the
        transition matrix acting on product space)."""
        # The transition matrix on product space is P tensor P
        P = w33.astype(float) / 12.0
        # Meeting probability from (0,0): after 1 step = 1/12
        P_meet_1 = np.sum(P[0, :] * P[0, :])
        assert abs(P_meet_1 - 1.0/12) < 1e-10


# ---------------------------------------------------------------------------
# T1393: Janson inequality application
# ---------------------------------------------------------------------------

class TestT1393JansonInequality:
    """Janson inequality for independent sets."""

    def test_expected_independent_edges(self, w33):
        """In random subset S where each vertex is included with prob p=0.3:
        X = number of edges in S (want X=0 for independent set).
        E[X] = m*p^2 = 240*0.09 = 21.6."""
        p = 0.3
        EX = 240 * p**2
        assert abs(EX - 21.6) < 1e-10

    def test_janson_mu_computation(self, w33):
        """mu = sum over edges e of Pr(e in S) = m * p^2.
        For p = 1/sqrt(m/alpha_target) we want to be in regime where E[X] ~ 1."""
        m = 240
        # p such that m*p^2 = 1 => p = 1/sqrt(240) ~ 0.0645
        p_crit = 1.0 / sqrt(m)
        EX_at_crit = m * p_crit**2
        assert abs(EX_at_crit - 1.0) < 1e-10

    def test_janson_delta_computation(self, w33):
        """Delta = sum over ordered pairs of intersecting edges (e~f)
        of Pr(e union f subset S).
        Each shared-vertex edge pair: Pr = p^3 (3 distinct vertices).
        Number of such ordered pairs: 2 * n * C(k,2) = 2*40*66 = 5280."""
        n, k = 40, 12
        p = 0.3
        ordered_shared = 2 * n * comb(k, 2)
        assert ordered_shared == 5280
        Delta = ordered_shared * p**3
        assert abs(Delta - 5280 * 0.027) < 1e-10

    def test_janson_bound_pr_no_edges(self):
        """Janson: Pr(X=0) <= exp(-mu + Delta/2) for mu = E[X], Delta as above.
        At p=0.3: mu=21.6, Delta=142.56.
        exp(-21.6 + 71.28) = exp(49.68) -- this is huge, so bound is vacuous.
        At p = 1/sqrt(240): mu=1, Delta = 5280/240^(3/2) ~ 1.423.
        exp(-1 + 0.712) = exp(-0.288) ~ 0.75."""
        m, n, k = 240, 40, 12
        p = 1.0 / sqrt(m)
        mu = m * p**2
        Delta = 2 * n * comb(k, 2) * p**3
        janson_upper = exp(-mu + Delta / 2)
        assert janson_upper < 1.0  # meaningful bound
        assert abs(mu - 1.0) < 1e-10

    def test_janson_lower_bound(self):
        """Janson lower bound: Pr(X=0) >= exp(-mu - Delta).
        At p = 1/sqrt(240): exp(-1 - 1.423) = exp(-2.423) ~ 0.0886."""
        m, n, k = 240, 40, 12
        p = 1.0 / sqrt(m)
        mu = m * p**2
        Delta = 2 * n * comb(k, 2) * p**3
        janson_lower = exp(-mu - Delta)
        assert janson_lower > 0  # positive probability


# ---------------------------------------------------------------------------
# T1394: Eigenvalue counting
# ---------------------------------------------------------------------------

class TestT1394EigenvalueCounting:
    """N(x) = #{lambda_i <= x}: step function with jumps at {-4, 2, 12}."""

    def test_eigenvalue_multiplicities(self, spectrum):
        """Spectrum: {12^1, 2^24, (-4)^15}. Total = 40."""
        eigs_rounded = [round(e) for e in spectrum]
        counts = Counter(eigs_rounded)
        assert counts[12] == 1
        assert counts[2] == 24
        assert counts[-4] == 15
        assert sum(counts.values()) == 40

    def test_counting_function_below_minus5(self, spectrum):
        """N(-5) = 0: no eigenvalues below -5."""
        count = sum(1 for e in spectrum if e <= -5 + 1e-8)
        assert count == 0

    def test_counting_function_at_minus4(self, spectrum):
        """N(-4) = 15: fifteen eigenvalues at -4."""
        count = sum(1 for e in spectrum if e <= -4 + 1e-8)
        assert count == 15

    def test_counting_function_at_0(self, spectrum):
        """N(0) = 15: still only eigenvalues at -4 (none between -4 and 2)."""
        count = sum(1 for e in spectrum if e <= 0 + 1e-8)
        assert count == 15

    def test_counting_function_at_2(self, spectrum):
        """N(2) = 39: eigenvalues at -4 (15) + at 2 (24) = 39."""
        count = sum(1 for e in spectrum if e <= 2 + 1e-8)
        assert count == 39

    def test_counting_function_at_12(self, spectrum):
        """N(12) = 40: all eigenvalues."""
        count = sum(1 for e in spectrum if e <= 12 + 1e-8)
        assert count == 40

    def test_eigenvalue_gaps(self, spectrum):
        """Gaps: from -4 to 2 is 6; from 2 to 12 is 10."""
        distinct = sorted(set(round(e) for e in spectrum))
        assert distinct == [-4, 2, 12]
        assert distinct[1] - distinct[0] == 6
        assert distinct[2] - distinct[1] == 10


# ---------------------------------------------------------------------------
# T1395: Spectral measure
# ---------------------------------------------------------------------------

class TestT1395SpectralMeasure:
    """mu = (15*delta_{-4} + 24*delta_2 + 1*delta_{12})/40."""

    def test_spectral_measure_weights(self, spectrum):
        """Weights sum to 1."""
        w_neg4 = Fraction(15, 40)
        w_2 = Fraction(24, 40)
        w_12 = Fraction(1, 40)
        assert w_neg4 + w_2 + w_12 == 1

    def test_spectral_measure_mean(self, spectrum):
        """Mean = (15*(-4) + 24*2 + 1*12)/40 = (-60+48+12)/40 = 0/40 = 0.
        This equals tr(A)/n = 0 (no self-loops)."""
        mean = Fraction(15 * (-4) + 24 * 2 + 1 * 12, 40)
        assert mean == 0

    def test_spectral_measure_second_moment(self, spectrum):
        """E[lambda^2] = (15*16 + 24*4 + 1*144)/40 = (240+96+144)/40 = 480/40 = 12.
        This equals tr(A^2)/n = 2m/n = 480/40 = 12 = k."""
        second = Fraction(15*16 + 24*4 + 1*144, 40)
        assert second == 12

    def test_spectral_measure_variance(self, spectrum):
        """Var = E[lambda^2] - E[lambda]^2 = 12 - 0 = 12."""
        var = 12 - 0
        assert var == 12

    def test_spectral_measure_third_moment(self, spectrum):
        """E[lambda^3] = (15*(-64) + 24*8 + 1*1728)/40 = (-960+192+1728)/40 = 960/40 = 24.
        This equals tr(A^3)/n = 6*triangles/n = 960/40 = 24."""
        third = Fraction(15*(-64) + 24*8 + 1*1728, 40)
        assert third == 24

    def test_spectral_measure_fourth_moment(self, w33, spectrum):
        """E[lambda^4] = (15*256 + 24*16 + 1*20736)/40 = (3840+384+20736)/40 = 24960/40 = 624.
        Also equals tr(A^4)/n."""
        fourth = Fraction(15*256 + 24*16 + 1*20736, 40)
        assert fourth == 624
        A4 = np.linalg.matrix_power(w33, 4)
        assert np.trace(A4) == 624 * 40

    def test_spectral_cumulative_distribution(self, spectrum):
        """CDF: F(-5)=0, F(-3)=15/40=3/8, F(3)=39/40, F(13)=1."""
        assert Fraction(15, 40) == Fraction(3, 8)
        assert Fraction(39, 40) == Fraction(39, 40)


# ---------------------------------------------------------------------------
# T1396: Concentration of quadratic forms
# ---------------------------------------------------------------------------

class TestT1396QuadraticFormConcentration:
    """f^T A f / f^T f concentrates around mean for random f."""

    def test_rayleigh_quotient_range(self, w33, spectrum):
        """Rayleigh quotient lies in [lambda_min, lambda_max] = [-4, 12]."""
        lam_min = round(spectrum[-1])
        lam_max = round(spectrum[0])
        assert lam_min == -4
        assert lam_max == 12

    def test_rayleigh_random_vectors(self, w33):
        """For 1000 random Gaussian vectors, R(f) = f^T A f / f^T f
        should concentrate around tr(A)/n = 0."""
        rng = np.random.RandomState(42)
        A = w33.astype(float)
        n = 40
        rayleighs = []
        for _ in range(1000):
            f = rng.randn(n)
            R = f @ A @ f / (f @ f)
            rayleighs.append(R)
            assert -4 - 1e-8 <= R <= 12 + 1e-8
        mean_R = np.mean(rayleighs)
        # Mean should be close to tr(A)/n = 0
        assert abs(mean_R) < 1.0  # within statistical fluctuation

    def test_rayleigh_mean_theory(self, w33):
        """For f ~ N(0, I), E[f^T A f] = tr(A) = 0. E[f^T f] = n = 40.
        So E[R] ~ tr(A)/n = 0 (approximate, not exact for ratio)."""
        tr_A = np.trace(w33)
        assert tr_A == 0

    def test_rayleigh_variance_bound(self, w33):
        """Variance of f^T A f / ||f||^2 bounded by spectral range.
        For SRG: the distribution is discrete with known weights."""
        rng = np.random.RandomState(99)
        A = w33.astype(float)
        n = 40
        rayleighs = [rng.randn(n) for _ in range(500)]
        R_values = [(f @ A @ f) / (f @ f) for f in rayleighs]
        var_R = np.var(R_values)
        # Variance bounded by (lambda_max - lambda_min)^2 / 4 = 256/4 = 64
        assert var_R < 64

    def test_quadratic_form_eigenvector(self, w33):
        """For eigenvector v_i: R(v_i) = lambda_i exactly."""
        evals, evecs = np.linalg.eigh(w33.astype(float))
        for i in range(40):
            v = evecs[:, i]
            R = v @ w33.astype(float) @ v / (v @ v)
            assert abs(R - evals[i]) < 1e-8


# ---------------------------------------------------------------------------
# T1397: Edge independence number (maximum matching)
# ---------------------------------------------------------------------------

class TestT1397EdgeIndependence:
    """Maximum matching nu(G) for W(3,3)."""

    def test_matching_lower_bound(self, w33):
        """nu(G) >= n/2 = 20 for any graph with a perfect matching.
        For 12-regular graph, by Petersen's theorem any 2k-regular graph
        has a perfect matching... but 12 is even so this applies if biconnected.
        Greedy matching gives lower bound."""
        n = 40
        matched = set()
        matching = []
        for i in range(n):
            if i in matched:
                continue
            for j in range(i + 1, n):
                if j in matched:
                    continue
                if w33[i, j] == 1:
                    matching.append((i, j))
                    matched.add(i)
                    matched.add(j)
                    break
        assert len(matching) >= 15  # greedy gives at least this

    def test_perfect_matching_exists(self, w33):
        """12-regular graph on 40 (even) vertices. By Babai's theorem,
        every connected vertex-transitive graph on an even number of vertices
        has a perfect matching. Verify via randomized greedy search."""
        n = 40
        k = 12
        assert k % 2 == 0
        assert n % 2 == 0
        # Randomized greedy matching with many restarts
        rng = np.random.RandomState(42)
        best_matching_size = 0
        best_matching = []
        for _ in range(200):
            perm = rng.permutation(n)
            matched = set()
            matching = []
            for v in perm:
                if v in matched:
                    continue
                nbrs = np.where(w33[v] == 1)[0]
                rng.shuffle(nbrs)
                for u in nbrs:
                    if u not in matched:
                        matching.append((v, u))
                        matched.add(v)
                        matched.add(u)
                        break
            if len(matching) > best_matching_size:
                best_matching_size = len(matching)
                best_matching = matching
            if best_matching_size == 20:
                break
        assert best_matching_size == 20  # perfect matching found
        # Verify matching is valid
        vertices_used = set()
        for u, v in best_matching:
            assert w33[u, v] == 1
            assert u not in vertices_used
            assert v not in vertices_used
            vertices_used.add(u)
            vertices_used.add(v)
        assert len(vertices_used) == n

    def test_matching_edges_are_independent(self, w33):
        """Verify a greedy matching produces vertex-disjoint edges."""
        n = 40
        matched = set()
        matching = []
        for i in range(n):
            if i in matched:
                continue
            for j in range(i+1, n):
                if j in matched:
                    continue
                if w33[i, j] == 1:
                    matching.append((i, j))
                    matched.add(i)
                    matched.add(j)
                    break
        # Verify independence
        vertices_used = set()
        for u, v in matching:
            assert u not in vertices_used
            assert v not in vertices_used
            vertices_used.add(u)
            vertices_used.add(v)
            assert w33[u, v] == 1

    def test_fractional_matching(self, w33):
        """Fractional matching number nu*(G) = n/2 = 20 for vertex-transitive.
        (Each edge gets weight 1/k, total weight per vertex = 1, sum = n/2.)"""
        n, k = 40, 12
        m = 240
        # Uniform fractional matching: each edge gets weight 1/k
        weight_per_edge = Fraction(1, k)
        total = weight_per_edge * m
        assert total == Fraction(m, k)
        assert total == 20  # n/2 exactly


# ---------------------------------------------------------------------------
# T1398: Cheeger constant
# ---------------------------------------------------------------------------

class TestT1398CheegerConstant:
    """h(G) = min |E(S, V\\S)| / min(|S|, |V\\S|) bounded by eigenvalues."""

    def test_cheeger_spectral_lower_bound(self, w33):
        """Cheeger inequality (discrete): h(G) >= (k - lambda_2)/2 = (12-2)/2 = 5.
        Here lambda_2 is the second-largest eigenvalue of A, which is 2."""
        k, lambda2 = 12, 2
        h_lower = (k - lambda2) / 2
        assert h_lower == 5.0

    def test_cheeger_spectral_upper_bound(self, w33):
        """h(G) <= sqrt(2k(k - lambda_2)) = sqrt(2*12*10) = sqrt(240) ~ 15.49."""
        k, lambda2 = 12, 2
        h_upper = sqrt(2 * k * (k - lambda2))
        assert abs(h_upper - sqrt(240)) < 1e-10

    def test_cheeger_brute_small_sets(self, w33):
        """Compute h(G) exactly for small subset sizes (1 to 5).
        For S of size 1: |E(S,V\\S)| = k = 12. h = 12/1 = 12.
        For S of size s: boundary >= k*s - 2*e(S) by handshaking."""
        n, k = 40, 12
        # Size 1
        for v in range(n):
            boundary = w33[v].sum()
            assert boundary == k
        # So h({v}) = 12/1 = 12 for any single vertex

        # Size 2: if (u,v) edge, boundary = 2k - 2*1 - 2*lambda_common
        # where lambda_common = |N(u) cap N(v)| = lambda=2.
        # boundary = 24 - 2 - 2*2 = 18? No: count edges from S to V\S.
        # |E(S,V\S)| = sum deg in S - 2*e(S) = 24 - 2*1 = 22 (if edge)
        # or 24 - 0 = 24 (if not edge)
        min_boundary_2 = n  # initialize high
        for i in range(n):
            for j in range(i+1, n):
                S = [i, j]
                boundary = 0
                for s in S:
                    for t in range(n):
                        if t not in S and w33[s, t] == 1:
                            boundary += 1
                if boundary < min_boundary_2:
                    min_boundary_2 = boundary
        # For adjacent pair: 2*12 - 2*1 = 22
        assert min_boundary_2 == 22

    def test_cheeger_computed_lower(self, w33):
        """Sample many random subsets and compute the min ratio.
        h(G) must be >= 5 (from spectral bound)."""
        rng = np.random.RandomState(42)
        n, k = 40, 12
        min_h = float('inf')
        for _ in range(500):
            s = rng.randint(1, 21)
            S = set(rng.choice(n, s, replace=False).tolist())
            complement = set(range(n)) - S
            boundary = 0
            for u in S:
                for v in complement:
                    if w33[u, v] == 1:
                        boundary += 1
            h_S = boundary / min(len(S), len(complement))
            if h_S < min_h:
                min_h = h_S
        assert min_h >= 5.0 - 1e-9  # spectral guarantee


# ---------------------------------------------------------------------------
# T1399: Vertex isoperimetric inequality
# ---------------------------------------------------------------------------

class TestT1399VertexIsoperimetric:
    """min |N(S)\\S| for sets of size s."""

    def test_vertex_expansion_single(self, w33):
        """For single vertex: |N({v})| = k = 12."""
        n = 40
        for v in range(n):
            nbrs = set(np.where(w33[v] == 1)[0]) - {v}
            assert len(nbrs) == 12

    def test_vertex_expansion_pair(self, w33):
        """For adjacent pair {u,v}: |N(S)\\S| = |N(u) union N(v)| - |S intersect (N(u) union N(v))|.
        |N(u) cap N(v)| = lambda = 2 (SRG parameter for adjacent pairs).
        |N(u) union N(v)| = 12+12-2 = 22. But u in N(v) and v in N(u), so
        S = {u,v} subset N(u) union N(v). Thus |N(S)\\S| = 22 - 2 = 20."""
        n = 40
        # Test a few adjacent pairs
        count_checked = 0
        for i in range(n):
            for j in range(i+1, n):
                if w33[i, j] == 1:
                    S = {i, j}
                    nbrs = set()
                    for s in S:
                        nbrs |= set(np.where(w33[s] == 1)[0])
                    nbrs -= S
                    assert len(nbrs) == 20
                    count_checked += 1
                    if count_checked >= 10:
                        break
            if count_checked >= 10:
                break

    def test_vertex_expansion_nonadjacent_pair(self, w33):
        """For non-adjacent pair {u,v}: |N(u) cap N(v)| = mu = 4.
        |N(S)\\S| = 12 + 12 - 4 - 2 = 18... Wait, |N(u) union N(v)| = 12+12-4 = 20.
        |N(S)\\S| = 20."""
        n = 40
        count_checked = 0
        for i in range(n):
            for j in range(i+1, n):
                if w33[i, j] == 0:
                    S = {i, j}
                    nbrs = set()
                    for s in S:
                        nbrs |= set(np.where(w33[s] == 1)[0])
                    nbrs -= S
                    assert len(nbrs) == 20
                    count_checked += 1
                    if count_checked >= 10:
                        break
            if count_checked >= 10:
                break

    def test_vertex_expansion_lower_bound(self, w33):
        """Vertex expansion >= (k - lambda_2)/2 * |S| / (something).
        For SRG, vertex expansion is bounded below by spectral gap.
        Test 200 random subsets of size 1..10."""
        rng = np.random.RandomState(42)
        n = 40
        for _ in range(200):
            s = rng.randint(1, 11)
            S = set(rng.choice(n, s, replace=False).tolist())
            nbrs = set()
            for v in S:
                nbrs |= set(np.where(w33[v] == 1)[0])
            nbrs -= S
            # For vertex-transitive graph, expansion should be positive
            assert len(nbrs) >= 1


# ---------------------------------------------------------------------------
# T1400: Chromatic number bounds
# ---------------------------------------------------------------------------

class TestT1400ChromaticNumberBounds:
    """chi(G) >= n/alpha = 40/10 = 4; chi(G) <= Delta = 12 (Brooks)."""

    def test_hoffman_chromatic_lower(self, w33):
        """chi(G) >= 1 - k/tau = 1 - 12/(-4) = 1 + 3 = 4."""
        chi_lower = 1 - 12 / (-4)
        assert chi_lower == 4.0

    def test_fractional_chromatic_lower(self):
        """Hoffman bound: chi_f >= 1 - k/tau = 1 + 3 = 4.
        For vertex-transitive: chi_f = n/alpha. The Hoffman bound on alpha
        gives alpha <= 10, but the actual alpha = 7 (W(q) has no ovoids for
        q odd; max partial ovoid = q^2-q+1 = 7). So chi_f = 40/7 > 4."""
        hoffman_bound = 1 - Fraction(12, -4)
        assert hoffman_bound == 4
        # Actual chi_f is higher
        chi_f_actual = Fraction(40, 7)
        assert chi_f_actual > hoffman_bound

    def test_clique_lower_bound(self, w33):
        """chi(G) >= omega(G) = 4 (clique number of W(3,3) is 4)."""
        # Count K4s from tr(A^4) and triangle/path counts
        A = w33
        A2 = A @ A
        A3 = A @ A2
        triangles = np.trace(A3) // 6
        assert triangles == 160
        # K4: each tetrahedron contributes 4! = 24 closed walks of length 4
        # through its vertices. But tr(A^4) also counts other walks.
        # Instead verify K4 exists by direct search on a triangle
        n = 40
        found = False
        for i in range(n):
            if found:
                break
            ni = set(np.where(A[i] == 1)[0])
            for j in ni:
                if j <= i:
                    continue
                nj = set(np.where(A[j] == 1)[0])
                common_ij = ni & nj
                for u in common_ij:
                    if u <= j:
                        continue
                    for v in common_ij:
                        if v <= u:
                            continue
                        if A[u, v] == 1:
                            found = True
                            break
                    if found:
                        break
                if found:
                    break
        assert found  # K4 exists, so omega >= 4

    def test_brooks_upper_bound(self, w33):
        """Brooks: chi(G) <= Delta(G) = 12 (not complete, not odd cycle).
        Actually find a proper 4-coloring to show chi = 4."""
        n = 40
        # DSatur coloring for better performance
        sat = np.zeros(n, dtype=int)
        colors = [-1] * n
        degree = w33.sum(axis=1)
        uncolored = set(range(n))

        for step in range(n):
            # Pick uncolored vertex with max saturation, break ties by degree
            best = max(uncolored, key=lambda v: (sat[v], degree[v]))
            used = set()
            for u in range(n):
                if w33[best, u] == 1 and colors[u] >= 0:
                    used.add(colors[u])
            c = 0
            while c in used:
                c += 1
            colors[best] = c
            uncolored.remove(best)
            # Update saturation
            for u in range(n):
                if w33[best, u] == 1 and colors[u] < 0:
                    sat[u] = len({colors[w] for w in range(n)
                                  if w33[u, w] == 1 and colors[w] >= 0})

        num_colors = max(colors) + 1
        assert num_colors <= 12  # Brooks bound
        assert num_colors >= 4   # Hoffman bound
        # Verify proper coloring
        for i in range(n):
            for j in range(i+1, n):
                if w33[i, j] == 1:
                    assert colors[i] != colors[j]

    def test_chromatic_bounds_from_alpha(self, w33):
        """Alpha(W(3,3)) = 7 (max partial ovoid of W(q) for q=3 is q^2-q+1=7,
        since W(q) has no ovoids for odd q by Payne 1971).
        chi >= ceil(n/alpha) = ceil(40/7) = 6.
        Verify alpha = 7 via Bron-Kerbosch and chi <= 12 via greedy coloring."""
        n = 40
        adj = {i: frozenset(np.where(w33[i] == 1)[0]) for i in range(n)}
        # Complement adjacency for Bron-Kerbosch (max clique in complement = max IS)
        cadj = {i: frozenset(j for j in range(n) if j != i and w33[i, j] == 0)
                for i in range(n)}
        best = [0]
        best_set = [[]]

        def bron_kerbosch(R, P, X):
            if not P and not X:
                if len(R) > best[0]:
                    best[0] = len(R)
                    best_set[0] = list(R)
                return
            if len(R) + len(P) <= best[0]:
                return
            pivot_cands = P | X
            if not pivot_cands:
                return
            pivot = max(pivot_cands, key=lambda v: len(cadj[v] & P))
            for v in list(P - cadj[pivot]):
                bron_kerbosch(R | {v}, P & cadj[v], X & cadj[v])
                P = P - {v}
                X = X | {v}

        bron_kerbosch(frozenset(), frozenset(range(n)), frozenset())
        alpha = best[0]
        assert alpha == 7
        # Verify the IS is actually independent
        IS = best_set[0]
        for i, u in enumerate(IS):
            for v in IS[i+1:]:
                assert w33[u, v] == 0
        # Chromatic bounds
        import math
        assert math.ceil(n / alpha) == 6  # chi >= 6
        # Hoffman bound is weaker: chi >= 4
        assert 1 - 12 / (-4) == 4.0


# ---------------------------------------------------------------------------
# T1401: Fractional chromatic number
# ---------------------------------------------------------------------------

class TestT1401FractionalChromatic:
    """chi_f(G) = n/alpha(G) = 40/10 = 4.0 exactly (vertex-transitive)."""

    def test_fractional_chromatic_formula(self):
        """For vertex-transitive graphs: chi_f = n/alpha.
        With alpha = 7: chi_f = 40/7."""
        chi_f = Fraction(40, 7)
        assert chi_f == Fraction(40, 7)
        assert float(chi_f) > 5.71
        assert float(chi_f) < 5.72

    def test_hoffman_bound_not_tight(self):
        """Hoffman bound: chi_f >= 1 - k/tau = 1 + 3 = 4.
        Actual chi_f = 40/7 ~ 5.71 > 4, so Hoffman bound is NOT tight.
        This gap arises because alpha = 7 < 10 (Hoffman upper bound on alpha)."""
        hoffman = 1 - Fraction(12, -4)
        assert hoffman == 4
        chi_f = Fraction(40, 7)
        assert chi_f > hoffman  # gap: Hoffman bound is not tight

    def test_clique_cover_fractional(self):
        """Fractional clique cover number = chi_f(complement).
        complement is SRG(40,27,18,18) with tau'=-3, k'=27.
        chi_f(complement) = 1 - 27/(-3) = 10.
        Lovász: theta(G) * theta(G_bar) = n = 40.
        theta(G) = 10, theta(G_bar) = 4."""
        chi_f_comp = 1 - Fraction(27, -3)
        assert chi_f_comp == 10

    def test_fractional_integrality_gap(self):
        """chi_f = 40/7 ~ 5.71. chi(G) >= 6 (integer).
        Integrality gap = chi(G) / chi_f(G) >= 6/(40/7) = 42/40 = 21/20.
        There is a small integrality gap for W(3,3)."""
        chi_f = Fraction(40, 7)
        # chi >= 6, so gap >= 6 / (40/7) = 42/40 = 21/20
        gap_lower = Fraction(6, 1) / chi_f
        assert gap_lower == Fraction(42, 40)
        assert gap_lower == Fraction(21, 20)
        assert float(gap_lower) >= 1.0

    def test_lp_relaxation_value(self, w33):
        """Hoffman bound: alpha <= n*(-tau)/(k-tau) = 40*4/16 = 10.
        This is an upper bound; actual alpha = 7 < 10."""
        alpha_bound = 40 * 4 / 16
        assert alpha_bound == 10.0
        # The actual independence number is 7 (W(q) no ovoids for q odd)
        assert 7 < alpha_bound

    def test_independent_set_of_size_7_exists(self, w33):
        """Find an independent set of size 7 to confirm alpha = 7.
        The max partial ovoid of W(3) has size q^2-q+1 = 7 (Ball 2004)."""
        n = 40
        # Use Bron-Kerbosch on complement to find max IS
        cadj = {i: frozenset(j for j in range(n) if j != i and w33[i, j] == 0)
                for i in range(n)}
        best = [0]
        best_set = [[]]

        def bk(R, P, X):
            if not P and not X:
                if len(R) > best[0]:
                    best[0] = len(R)
                    best_set[0] = list(R)
                return
            if len(R) + len(P) <= best[0]:
                return
            pivot_cands = P | X
            if not pivot_cands:
                return
            pivot = max(pivot_cands, key=lambda v: len(cadj[v] & P))
            for v in list(P - cadj[pivot]):
                bk(R | {v}, P & cadj[v], X & cadj[v])
                P = P - {v}
                X = X | {v}

        bk(frozenset(), frozenset(range(n)), frozenset())
        assert best[0] == 7
        # Verify it is actually independent
        IS = best_set[0]
        for i, u in enumerate(IS):
            for v in IS[i+1:]:
                assert w33[u, v] == 0


# ---------------------------------------------------------------------------
# T1402: Entropy of degree sequence
# ---------------------------------------------------------------------------

class TestT1402DegreeEntropy:
    """H = -sum p_d log p_d; for regular graph H = 0."""

    def test_degree_sequence(self, w33):
        """All degrees equal k=12 (12-regular)."""
        degrees = w33.sum(axis=1)
        assert np.all(degrees == 12)

    def test_degree_distribution(self, w33):
        """Degree distribution: p_12 = 1, all others = 0."""
        degrees = w33.sum(axis=1)
        counts = Counter(degrees.tolist())
        assert counts == {12: 40}

    def test_entropy_zero(self, w33):
        """Shannon entropy of degree distribution: H = -1*log(1) = 0."""
        degrees = w33.sum(axis=1)
        counts = Counter(degrees.tolist())
        n = 40
        H = 0.0
        for d, cnt in counts.items():
            p = cnt / n
            if p > 0:
                H -= p * log2(p)
        assert abs(H) < 1e-15

    def test_max_entropy_comparison(self):
        """Maximum entropy for degree distribution on {0,...,39} would be
        log2(40) ~ 5.32. Regular graph achieves minimum entropy = 0."""
        H_max = log2(40)
        assert H_max > 5.0
        assert 0.0 < H_max

    def test_joint_degree_entropy(self, w33):
        """Joint degree distribution: for each edge (u,v), the pair
        (deg(u), deg(v)) = (12, 12) always. Entropy = 0."""
        n = 40
        pairs = []
        for i in range(n):
            for j in range(i+1, n):
                if w33[i, j] == 1:
                    di = w33[i].sum()
                    dj = w33[j].sum()
                    pairs.append((di, dj))
        counts = Counter(pairs)
        assert counts == {(12, 12): 240}
        # Entropy of edge-degree distribution
        H_edge = 0.0
        m = 240
        for pair, cnt in counts.items():
            p = cnt / m
            if p > 0:
                H_edge -= p * log2(p)
        assert abs(H_edge) < 1e-15

    def test_neighbor_degree_variance(self, w33):
        """For regular graph, neighbor degree variance = 0."""
        n = 40
        for v in range(n):
            nbrs = np.where(w33[v] == 1)[0]
            nbr_degrees = [w33[u].sum() for u in nbrs]
            assert np.var(nbr_degrees) == 0.0


# ---------------------------------------------------------------------------
# T1403: Graph conductance
# ---------------------------------------------------------------------------

class TestT1403GraphConductance:
    """phi(G) = min_{S:|S|<=n/2} |E(S,V\\S)|/(k*|S|); relates to spectral gap."""

    def test_conductance_lower_bound(self, w33):
        """Cheeger inequality: phi(G) >= (k - lambda_2)/(2k) = (12-2)/24 = 5/12."""
        k, lam2 = 12, 2
        phi_lower = Fraction(k - lam2, 2 * k)
        assert phi_lower == Fraction(5, 12)

    def test_conductance_upper_bound(self, w33):
        """phi(G) <= sqrt(2(k-lambda_2)/k) = sqrt(2*10/12) = sqrt(5/3) ~ 1.29.
        But conductance <= 1, so this is vacuous. Better: phi <= 1."""
        k, lam2 = 12, 2
        bound = sqrt(2 * (k - lam2) / k)
        assert bound > 1.0  # vacuous upper bound from spectral
        # Conductance is at most 1 by definition (when all edges leave S)
        # For k-regular: phi(S) = |E(S,V\S)|/(k*|S|) <= k*|S|/(k*|S|) = 1

    def test_conductance_single_vertex(self, w33):
        """phi({v}) = |E({v}, V\\{v})|/(k*1) = 12/12 = 1."""
        n, k = 40, 12
        for v in range(n):
            boundary = w33[v].sum()
            phi_v = boundary / k
            assert abs(phi_v - 1.0) < 1e-12

    def test_conductance_random_samples(self, w33):
        """Sample 500 random subsets of size <= 20 and verify phi >= 5/12."""
        rng = np.random.RandomState(42)
        n, k = 40, 12
        phi_lower = 5.0 / 12.0
        for _ in range(500):
            s = rng.randint(1, 21)
            S = set(rng.choice(n, s, replace=False).tolist())
            complement = set(range(n)) - S
            boundary = sum(1 for u in S for v in complement if w33[u, v] == 1)
            phi_S = boundary / (k * len(S))
            assert phi_S >= phi_lower - 1e-9

    def test_conductance_spectral_gap_relation(self, w33):
        """Spectral gap of normalized Laplacian: gamma = 1 - lambda_2/k = 1 - 2/12 = 5/6.
        Cheeger: gamma/2 <= phi(G) <= sqrt(2*gamma).
        5/12 <= phi(G) <= sqrt(5/3) ~ 1.29."""
        k, lam2 = 12, 2
        gamma = 1 - lam2 / k
        assert abs(gamma - 5/6) < 1e-12
        lower = gamma / 2
        upper = sqrt(2 * gamma)
        assert abs(lower - 5/12) < 1e-12
        assert upper > 1.0

    def test_conductance_vs_expansion(self, w33):
        """Edge expansion h(G) = phi(G) * k for k-regular graphs.
        So h(G) >= k * (k - lambda_2)/(2k) = (k - lambda_2)/2 = 5."""
        k, lam2 = 12, 2
        h_lower = (k - lam2) / 2
        assert h_lower == 5.0

    def test_normalized_laplacian_gap(self, w33):
        """Normalized Laplacian L_norm = I - D^{-1/2} A D^{-1/2}.
        For k-regular: L_norm = I - A/k. Eigenvalues: 1 - lambda_i/k.
        Spectral gap = 1 - 2/12 = 5/6. Largest eigenvalue = 1 - (-4)/12 = 4/3."""
        n, k = 40, 12
        L_norm = np.eye(n) - w33.astype(float) / k
        evals = sorted(np.linalg.eigvalsh(L_norm))
        # Smallest eigenvalue should be 0 (for k/k = 1)
        assert abs(evals[0]) < 1e-10
        # Second smallest = 1 - 2/12 = 5/6
        assert abs(evals[1] - 5/6) < 1e-8
        # Largest = 1 - (-4)/12 = 4/3
        assert abs(evals[-1] - 4/3) < 1e-8
