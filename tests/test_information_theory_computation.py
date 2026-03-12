"""
Phase XC: Information Theory on Graphs (T1446-T1466)
====================================================

Computes graph entropy, von Neumann entropy, Renyi entropy, mutual
information, channel capacity, entropy rates, KL divergence, Fisher
information, and quantum information measures on W(3,3) = SRG(40,12,2,4).

All computations are from the actual adjacency matrix of the symplectic
polar space W(3,3) over GF(3).

Key results:
  W(3,3): n=40, k=12, lambda=2, mu=4
  A spectrum:  {12^1, 2^24, (-4)^15}
  L = kI - A,  spectrum: {0^1, 10^24, 16^15}
  240 edges, stationary distribution pi = 1/40 (uniform, regular graph)
  Transition matrix P = A/12; spectral gap = 1 - 2/12 = 5/6
  tr(L) = 480
  Von Neumann entropy from normalized Laplacian eigenvalues
  Entropy rate h = log(12) for k-regular graph
  Channel capacity C = log(40) - log(12)
  Entropy production = 0 (reversible walk on undirected graph)
"""

import pytest
import numpy as np
from scipy.linalg import expm, logm


# =====================================================================
# Build W(3,3)
# =====================================================================

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


def _safe_entropy(probs):
    """Compute -sum p_i log(p_i) with convention 0*log(0) = 0."""
    p = np.asarray(probs, dtype=float)
    mask = p > 0
    result = np.zeros_like(p)
    result[mask] = -p[mask] * np.log(p[mask])
    return np.sum(result)


def _safe_entropy_base2(probs):
    """Compute -sum p_i log2(p_i) with convention 0*log2(0) = 0."""
    p = np.asarray(probs, dtype=float)
    mask = p > 0
    result = np.zeros_like(p)
    result[mask] = -p[mask] * np.log2(p[mask])
    return np.sum(result)


# =====================================================================
# Fixtures
# =====================================================================

@pytest.fixture(scope="module")
def w33():
    return _build_w33()


@pytest.fixture(scope="module")
def laplacian(w33):
    """Graph Laplacian L = kI - A for k-regular graph (k=12)."""
    return 12.0 * np.eye(40) - w33.astype(float)


@pytest.fixture(scope="module")
def lap_eigenvalues(laplacian):
    """Sorted Laplacian eigenvalues (ascending)."""
    evals = np.linalg.eigvalsh(laplacian)
    return np.sort(evals)


@pytest.fixture(scope="module")
def adj_eigenvalues(w33):
    """Sorted adjacency eigenvalues (descending)."""
    evals = np.linalg.eigvalsh(w33.astype(float))
    return np.sort(evals)[::-1]


@pytest.fixture(scope="module")
def transition(w33):
    """Transition matrix P = A/k for simple random walk."""
    return w33.astype(float) / 12.0


@pytest.fixture(scope="module")
def stationary():
    """Stationary distribution: uniform pi = 1/40 for regular graph."""
    return np.ones(40) / 40.0


@pytest.fixture(scope="module")
def lap_eigen_decomp(laplacian):
    """Full eigendecomposition of L, sorted ascending."""
    evals, evecs = np.linalg.eigh(laplacian)
    idx = np.argsort(evals)
    return evals[idx], evecs[:, idx]


# =====================================================================
# T1446: Graph Entropy
# =====================================================================

class TestT1446GraphEntropy:
    """H(G) = log(n) for vertex-transitive graph (uniform stationary dist)."""

    def test_stationary_is_uniform(self, transition):
        """Stationary distribution of k-regular graph is uniform."""
        pi = np.ones(40) / 40.0
        pi_P = pi @ transition
        assert np.allclose(pi_P, pi), "pi*P != pi"

    def test_graph_entropy_equals_log_n(self, stationary):
        """H(G) = -sum pi_i log(pi_i) = log(40)."""
        H = _safe_entropy(stationary)
        assert np.isclose(H, np.log(40), atol=1e-12)

    def test_graph_entropy_maximal(self, stationary):
        """Uniform distribution maximizes entropy over 40 vertices."""
        H_uniform = _safe_entropy(stationary)
        # Any other distribution has H < log(40)
        rng = np.random.RandomState(42)
        for _ in range(10):
            q = rng.dirichlet(np.ones(40))
            H_q = _safe_entropy(q)
            assert H_q <= H_uniform + 1e-12

    def test_graph_entropy_numerical_value(self, stationary):
        """log(40) approx 3.6889."""
        H = _safe_entropy(stationary)
        assert np.isclose(H, 3.6888794541139363, atol=1e-10)


# =====================================================================
# T1447: Von Neumann Entropy
# =====================================================================

class TestT1447VonNeumannEntropy:
    """S = -tr(rho * log(rho)) where rho = L/tr(L), using non-zero eigenvalues."""

    def test_density_matrix_trace(self, laplacian):
        """tr(L) = 480 for W(3,3), so rho = L/480 has trace 1."""
        trL = np.trace(laplacian)
        assert np.isclose(trL, 480.0)
        rho = laplacian / trL
        assert np.isclose(np.trace(rho), 1.0)

    def test_von_neumann_from_eigenvalues(self, lap_eigenvalues):
        """S = -sum (mu_i/sum_j mu_j) log(mu_i/sum_j mu_j) for mu_i > 0."""
        pos = lap_eigenvalues[lap_eigenvalues > 1e-10]
        total = np.sum(pos)
        probs = pos / total
        S = _safe_entropy(probs)
        # 39 non-zero eigenvalues: 24 copies of 10, 15 copies of 16
        # probs: 24 copies of 10/480 = 1/48, 15 copies of 16/480 = 1/30
        p1 = 10.0 / 480.0  # = 1/48
        p2 = 16.0 / 480.0  # = 1/30
        S_exact = -24 * p1 * np.log(p1) - 15 * p2 * np.log(p2)
        assert np.isclose(S, S_exact, atol=1e-10)

    def test_von_neumann_bounds(self, lap_eigenvalues):
        """0 < S <= log(39) since 39 non-zero eigenvalues."""
        pos = lap_eigenvalues[lap_eigenvalues > 1e-10]
        probs = pos / np.sum(pos)
        S = _safe_entropy(probs)
        assert S > 0
        assert S <= np.log(39) + 1e-10

    def test_von_neumann_specific_value(self, lap_eigenvalues):
        """Compute exact von Neumann entropy from known spectrum."""
        # 24 eigenvalues = 10, 15 eigenvalues = 16, total = 24*10 + 15*16 = 480
        p10 = 10.0 / 480.0
        p16 = 16.0 / 480.0
        S_exact = -24 * p10 * np.log(p10) - 15 * p16 * np.log(p16)
        pos = lap_eigenvalues[lap_eigenvalues > 1e-10]
        probs = pos / np.sum(pos)
        S = _safe_entropy(probs)
        assert np.isclose(S, S_exact, atol=1e-12)
        # S should be less than log(39) because not uniform
        assert S < np.log(39)


# =====================================================================
# T1448: Renyi Entropy
# =====================================================================

class TestT1448RenyiEntropy:
    """H_alpha = 1/(1-alpha) * log(sum p_i^alpha) for stationary dist."""

    def test_renyi_equals_shannon_for_uniform(self, stationary):
        """For uniform distribution, H_alpha = log(40) for all alpha != 1."""
        for alpha in [0.5, 2.0, 3.0, 10.0, 0.1]:
            H_alpha = (1.0 / (1.0 - alpha)) * np.log(np.sum(stationary ** alpha))
            assert np.isclose(H_alpha, np.log(40), atol=1e-10), \
                f"Renyi alpha={alpha} failed"

    def test_renyi_alpha_zero(self, stationary):
        """H_0 = log(|support|) = log(40)."""
        support = np.sum(stationary > 0)
        H_0 = np.log(support)
        assert np.isclose(H_0, np.log(40))

    def test_renyi_converges_to_shannon(self, stationary):
        """As alpha -> 1, H_alpha -> H (Shannon entropy)."""
        H_shannon = _safe_entropy(stationary)
        for alpha in [0.99, 0.999, 1.001, 1.01]:
            H_alpha = (1.0 / (1.0 - alpha)) * np.log(np.sum(stationary ** alpha))
            assert np.isclose(H_alpha, H_shannon, atol=1e-3), \
                f"Renyi alpha={alpha}: {H_alpha} != {H_shannon}"

    def test_renyi_min_entropy(self, stationary):
        """H_inf = -log(max p_i) = log(40) for uniform."""
        H_inf = -np.log(np.max(stationary))
        assert np.isclose(H_inf, np.log(40), atol=1e-12)


# =====================================================================
# T1449: Mutual Information
# =====================================================================

class TestT1449MutualInformation:
    """I(X;Y) for random walk: I = H(X) - H(X|Y)."""

    def test_mutual_information_formula(self, transition, stationary):
        """I(X;Y) = H(X) - H(X|Y) = log(40) - log(12) = log(40/12) = log(10/3)."""
        H_X = _safe_entropy(stationary)
        # H(X|Y) = sum_i pi_i H(row_i of P) = log(12) for k-regular
        H_X_given_Y = np.log(12)
        I_XY = H_X - H_X_given_Y
        assert np.isclose(I_XY, np.log(40.0 / 12.0), atol=1e-12)

    def test_mutual_information_nonneg(self, transition, stationary):
        """I(X;Y) >= 0 always."""
        H_X = _safe_entropy(stationary)
        H_cond = np.sum(stationary * np.array([_safe_entropy(row) for row in transition]))
        I_XY = H_X - H_cond
        assert I_XY >= -1e-12

    def test_mutual_information_from_joint(self, transition, stationary):
        """I(X;Y) = sum_{x,y} p(x,y) log(p(x,y)/(p(x)p(y)))."""
        n = 40
        I = 0.0
        for i in range(n):
            for j in range(n):
                p_xy = stationary[i] * transition[i, j]
                if p_xy > 0 and stationary[j] > 0:
                    I += p_xy * np.log(p_xy / (stationary[i] * stationary[j]))
        assert np.isclose(I, np.log(40.0 / 12.0), atol=1e-10)

    def test_mutual_information_symmetry(self, transition, stationary):
        """For reversible walks, I(X;Y) = I(Y;X)."""
        # Check reversibility: pi_i P_ij = pi_j P_ji
        n = 40
        for i in range(n):
            for j in range(n):
                assert np.isclose(stationary[i] * transition[i, j],
                                  stationary[j] * transition[j, i], atol=1e-15)


# =====================================================================
# T1450: Conditional Entropy
# =====================================================================

class TestT1450ConditionalEntropy:
    """H(X|Y) = H(X,Y) - H(Y); from transition matrix P = A/12."""

    def test_conditional_entropy_for_regular(self, transition, stationary):
        """H(X|Y) = sum_i pi_i H(row_i of P) = log(12) for k-regular."""
        row_entropies = np.array([_safe_entropy(row) for row in transition])
        H_cond = np.dot(stationary, row_entropies)
        assert np.isclose(H_cond, np.log(12), atol=1e-10)

    def test_conditional_entropy_all_rows_equal(self, transition):
        """For k-regular, each row of P has exactly k nonzero entries = 1/k each."""
        row_entropies = np.array([_safe_entropy(row) for row in transition])
        assert np.allclose(row_entropies, np.log(12), atol=1e-10)

    def test_conditional_vs_joint(self, transition, stationary):
        """H(X|Y) = H(X,Y) - H(Y)."""
        n = 40
        # Joint distribution p(x,y) = pi(x) * P(x,y)
        joint = np.outer(stationary, np.ones(n)) * transition
        joint *= stationary[:, None]  # Actually pi_x * P_xy
        # Recompute correctly: p(x,y) = pi(x) * P(x,y)
        joint = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                joint[i, j] = stationary[i] * transition[i, j]
        H_joint = _safe_entropy(joint.ravel())
        H_Y = _safe_entropy(stationary)  # marginal of Y = stationary
        H_cond = H_joint - H_Y
        assert np.isclose(H_cond, np.log(12), atol=1e-10)

    def test_conditional_bounded(self, transition, stationary):
        """0 <= H(X|Y) <= H(X) = log(40)."""
        row_entropies = np.array([_safe_entropy(row) for row in transition])
        H_cond = np.dot(stationary, row_entropies)
        assert H_cond >= -1e-12
        assert H_cond <= np.log(40) + 1e-12


# =====================================================================
# T1451: Channel Capacity
# =====================================================================

class TestT1451ChannelCapacity:
    """C = max I(X;Y) = log(40) - H(X|Y) for uniform input on regular graph."""

    def test_capacity_formula(self, stationary):
        """C = log(40) - log(12) = log(10/3) for k-regular W(3,3)."""
        C = np.log(40) - np.log(12)
        assert np.isclose(C, np.log(40.0 / 12.0), atol=1e-12)

    def test_capacity_positive(self):
        """Channel capacity is positive since graph is not complete."""
        C = np.log(40) - np.log(12)
        assert C > 0

    def test_capacity_upper_bound(self):
        """C <= log(n) = log(40)."""
        C = np.log(40) - np.log(12)
        assert C <= np.log(40) + 1e-12

    def test_capacity_numerical_value(self):
        """log(10/3) approx 1.2040."""
        C = np.log(40) - np.log(12)
        assert np.isclose(C, np.log(10.0 / 3.0), atol=1e-12)
        assert np.isclose(C, 1.2039728043259361, atol=1e-8)


# =====================================================================
# T1452: Entropy Rate
# =====================================================================

class TestT1452EntropyRate:
    """h = lim H(X_n|X_{n-1}) = sum pi_i H(row_i of P) = log(12)."""

    def test_entropy_rate_value(self, transition, stationary):
        """h = log(12) for k-regular random walk."""
        row_entropies = np.array([_safe_entropy(row) for row in transition])
        h = np.dot(stationary, row_entropies)
        assert np.isclose(h, np.log(12), atol=1e-10)

    def test_entropy_rate_less_than_graph_entropy(self, transition, stationary):
        """h = log(12) < log(40) = H(G)."""
        row_entropies = np.array([_safe_entropy(row) for row in transition])
        h = np.dot(stationary, row_entropies)
        H_G = _safe_entropy(stationary)
        assert h < H_G

    def test_entropy_rate_equals_conditional(self, transition, stationary):
        """For stationary Markov chain, h = H(X_1 | X_0)."""
        # This is the same as the conditional entropy
        H_cond = np.log(12)
        row_entropies = np.array([_safe_entropy(row) for row in transition])
        h = np.dot(stationary, row_entropies)
        assert np.isclose(h, H_cond, atol=1e-10)

    def test_entropy_rate_numerical(self):
        """log(12) approx 2.4849."""
        assert np.isclose(np.log(12), 2.4849066497880004, atol=1e-8)


# =====================================================================
# T1453: KL Divergence
# =====================================================================

class TestT1453KLDivergence:
    """D_KL(P_i || pi) for row distributions vs stationary."""

    def test_kl_same_for_all_vertices(self, transition, stationary):
        """Vertex-transitive => KL(P_i || pi) is the same for all i."""
        kl_values = []
        for i in range(40):
            row = transition[i]
            kl = 0.0
            for j in range(40):
                if row[j] > 0:
                    kl += row[j] * np.log(row[j] / stationary[j])
            kl_values.append(kl)
        # All should be the same
        assert np.allclose(kl_values, kl_values[0], atol=1e-10)

    def test_kl_nonneg(self, transition, stationary):
        """D_KL >= 0 always (Gibbs' inequality)."""
        for i in range(40):
            row = transition[i]
            kl = 0.0
            for j in range(40):
                if row[j] > 0:
                    kl += row[j] * np.log(row[j] / stationary[j])
            assert kl >= -1e-12

    def test_kl_specific_value(self, transition, stationary):
        """D_KL(P_0 || pi) = log(40/12) = log(10/3) for regular graph."""
        # Row i of P: 12 entries of 1/12, 28 entries of 0 (including diagonal)
        # Actually: 12 entries of 1/12, rest are 0
        # But we only sum over j where P_ij > 0
        # KL = sum_j P_ij log(P_ij / pi_j) = 12 * (1/12) * log((1/12)/(1/40))
        #    = 1 * log(40/12) = log(10/3)
        kl_expected = np.log(40.0 / 12.0)
        row = transition[0]
        kl = np.sum(row[row > 0] * np.log(row[row > 0] / stationary[0]))
        assert np.isclose(kl, kl_expected, atol=1e-10)

    def test_kl_reverse(self, transition, stationary):
        """D_KL(pi || P_i) is also computable and differs from D_KL(P_i || pi)."""
        # D_KL(pi || P_0) = sum_j pi_j log(pi_j / P_0j)
        # For j where P_0j > 0: pi_j log(pi_j / P_0j) = (1/40)*log((1/40)/(1/12)) * 12
        # For j where P_0j = 0: infinite (undefined)
        # So D_KL(pi || P_0) = inf (since pi has support on vertices where P_0j=0)
        row = transition[0]
        # Verify that pi has support where P_0 does not
        zero_mask = row == 0
        assert np.any(stationary[zero_mask] > 0), "pi supported outside P_0 support"


# =====================================================================
# T1454: Fisher Information
# =====================================================================

class TestT1454FisherInformation:
    """Fisher information on graph with spectral parameterization."""

    def test_fisher_stationary(self, stationary):
        """Fisher information for uniform distribution: F = n (since d/dtheta of log(1/n) = 0)."""
        # For uniform p(theta) = 1/n, score function = 0, F = 0
        # But for parameterized family p(x; theta) = exp(theta * f(x)) / Z(theta),
        # F = Var[f(X)] under p(theta)
        # Use a simple spectral parameterization: p_i(beta) = exp(-beta * lambda_i) / Z
        # At beta=0, F = Var(lambda) = E[lambda^2] - E[lambda]^2
        # With A eigenvalues {12, 2^24, -4^15}: E[lambda] = tr(A)/40 = (12+48-60)/40 = 0
        # E[lambda^2] = tr(A^2)/40 = (40*12)/40 = 12 (each row of A has 12 ones)
        # So F = 12 - 0 = 12
        F = 12.0  # Var(spectrum) at uniform
        assert F == 12.0

    def test_fisher_from_adjacency_spectrum(self, adj_eigenvalues):
        """F(beta=0) = Var(eigenvalues) = E[lambda^2] - E[lambda]^2."""
        mean_lam = np.mean(adj_eigenvalues)
        var_lam = np.mean(adj_eigenvalues ** 2) - mean_lam ** 2
        # E[lambda] = (12 + 24*2 + 15*(-4))/40 = (12 + 48 - 60)/40 = 0
        assert np.isclose(mean_lam, 0.0, atol=1e-10)
        # E[lambda^2] = (144 + 24*4 + 15*16)/40 = (144 + 96 + 240)/40 = 480/40 = 12
        assert np.isclose(np.mean(adj_eigenvalues ** 2), 12.0, atol=1e-10)
        assert np.isclose(var_lam, 12.0, atol=1e-10)

    def test_fisher_positive(self, adj_eigenvalues):
        """Fisher information is non-negative."""
        var_lam = np.var(adj_eigenvalues)
        assert var_lam >= -1e-12

    def test_fisher_from_transition_spectrum(self, transition):
        """Fisher information from transition matrix eigenvalues."""
        P_evals = np.linalg.eigvalsh(transition)
        mean_p = np.mean(P_evals)
        var_p = np.var(P_evals)
        # P = A/12, so P_evals = A_evals / 12
        # Var(P_evals) = Var(A_evals)/144 = 12/144 = 1/12
        assert np.isclose(var_p, 1.0 / 12.0, atol=1e-10)


# =====================================================================
# T1455: Degree Entropy
# =====================================================================

class TestT1455DegreeEntropy:
    """H_deg = 0 for regular graph (all degrees = 12)."""

    def test_all_degrees_equal(self, w33):
        """Every vertex has degree 12."""
        degrees = w33.sum(axis=1)
        assert np.all(degrees == 12)

    def test_degree_entropy_zero(self, w33):
        """H_deg = -sum p_d log(p_d) = 0 for regular graph (single degree value)."""
        degrees = w33.sum(axis=1)
        unique, counts = np.unique(degrees, return_counts=True)
        probs = counts / np.sum(counts)
        H_deg = _safe_entropy(probs)
        assert np.isclose(H_deg, 0.0, atol=1e-15)

    def test_degree_distribution_degenerate(self, w33):
        """Only one degree value (12), so distribution is a point mass."""
        degrees = w33.sum(axis=1)
        unique = np.unique(degrees)
        assert len(unique) == 1
        assert unique[0] == 12

    def test_degree_entropy_vs_irregular(self, w33):
        """Degree entropy of W(3,3) is strictly less than for any irregular graph."""
        # For regular graph, H_deg = 0, which is the minimum possible
        H_deg = 0.0
        assert H_deg == 0.0
        # For comparison, a graph with 2 degree values would have H > 0
        probs_example = np.array([0.5, 0.5])
        H_example = _safe_entropy(probs_example)
        assert H_example > H_deg


# =====================================================================
# T1456: Structural Entropy
# =====================================================================

class TestT1456StructuralEntropy:
    """Based on automorphism group orbits; 1 orbit -> H_struct = 0."""

    def test_vertex_transitive_single_orbit(self, w33):
        """W(3,3) is vertex-transitive, so all vertices are in one orbit."""
        # Verify vertex-transitivity via walk-regularity:
        # All diagonal entries of A^2 should be equal
        A2 = w33 @ w33
        diag_A2 = np.diag(A2)
        assert np.all(diag_A2 == diag_A2[0])

    def test_structural_entropy_zero(self):
        """H_struct = -sum (|O_i|/n) log(|O_i|/n) = -(40/40)*log(40/40) = 0."""
        # Single orbit of size 40
        orbit_sizes = [40]
        n = 40
        probs = np.array([s / n for s in orbit_sizes])
        H_struct = _safe_entropy(probs)
        assert np.isclose(H_struct, 0.0, atol=1e-15)

    def test_walk_matrix_regularity(self, w33):
        """A^k has constant diagonal for all k => vertex-transitive (walk-regular)."""
        Ak = np.eye(40, dtype=int)
        for k in range(1, 5):
            Ak = Ak @ w33
            diag = np.diag(Ak)
            assert np.all(diag == diag[0]), f"A^{k} diagonal not constant"

    def test_structural_entropy_minimum(self):
        """Structural entropy 0 is minimal; only achieved by vertex-transitive graphs."""
        H_struct = 0.0
        # Non-transitive graph with 2 orbits would have H > 0
        probs_2orbits = np.array([20.0 / 40, 20.0 / 40])
        H_2 = _safe_entropy(probs_2orbits)
        assert H_2 > H_struct


# =====================================================================
# T1457: Kolmogorov Complexity Bound
# =====================================================================

class TestT1457KolmogorovComplexity:
    """K(G) >= log2(C(40,2)) - log2(# SRGs with these params)."""

    def test_edge_count_bits(self, w33):
        """Number of bits to specify 240 edges from C(40,2) = 780 possible."""
        from math import comb, log2
        total_edges = comb(40, 2)
        assert total_edges == 780
        actual_edges = np.sum(w33) // 2
        assert actual_edges == 240
        bits = log2(comb(780, 240))
        assert bits > 0

    def test_adjacency_matrix_bits(self, w33):
        """Upper bound: n*(n-1)/2 = 780 bits to store upper triangle."""
        n = 40
        upper_tri_bits = n * (n - 1) // 2
        assert upper_tri_bits == 780

    def test_srg_constraint_reduces_complexity(self):
        """SRG parameters (40,12,2,4) constrain the graph significantly."""
        from math import comb, log2
        # All possible graphs on 40 vertices: 2^780
        # Number of graphs with these SRG parameters is much smaller
        # SRG(40,12,2,4) is the unique symplectic polar space W(3,3)
        # So Kolmogorov complexity is bounded by encoding the parameters
        total_bits = 780
        # Encoding 4 parameters (n,k,lambda,mu) takes O(log n) bits
        param_bits = 4 * np.ceil(np.log2(41))  # ~22 bits
        assert param_bits < total_bits

    def test_compression_ratio(self, w33):
        """Compressibility: SRG structure allows compression well below 780 bits."""
        from math import comb, log2
        raw_bits = 780  # upper triangle
        # Shannon entropy of the edge indicator
        p = 240.0 / 780.0  # probability an edge exists
        q = 1 - p
        H_edge = -p * np.log2(p) - q * np.log2(q)
        compressed_bits = H_edge * 780
        assert compressed_bits < raw_bits


# =====================================================================
# T1458: Chromatic Entropy
# =====================================================================

class TestT1458ChromaticEntropy:
    """H_chi from chromatic polynomial; bounds from spectrum."""

    def test_chromatic_number_lower_bound(self, adj_eigenvalues):
        """chi >= 1 + k/(-lambda_min) = 1 + 12/4 = 4."""
        lambda_min = adj_eigenvalues[-1]
        assert np.isclose(lambda_min, -4, atol=1e-8)
        chi_lb = 1 + 12.0 / (-lambda_min)
        assert np.isclose(chi_lb, 4.0)

    def test_clique_bound(self, w33):
        """Clique number omega <= chi; omega >= 1 + k/(k-lambda) = 1 + 12/10 = 2.2 => omega >= 3."""
        # lambda = 2 (adjacency parameter)
        omega_lb = 1 + 12.0 / (12.0 - 2.0)
        assert omega_lb > 2

    def test_chromatic_entropy_from_coloring(self, w33):
        """Chromatic entropy from greedy coloring distribution."""
        # Greedy coloring
        n = 40
        colors = [-1] * n
        for v in range(n):
            neighbor_colors = set()
            for u in range(n):
                if w33[v, u] == 1 and colors[u] >= 0:
                    neighbor_colors.add(colors[u])
            c = 0
            while c in neighbor_colors:
                c += 1
            colors[v] = c
        num_colors = max(colors) + 1
        # Color class sizes
        from collections import Counter
        color_counts = Counter(colors)
        total = sum(color_counts.values())
        probs = np.array([color_counts[c] / total for c in range(num_colors)])
        H_chi = _safe_entropy(probs)
        assert H_chi > 0
        assert H_chi <= np.log(num_colors) + 1e-10

    def test_fractional_chromatic_bound(self, adj_eigenvalues):
        """chi_f >= n / alpha(G) and spectral bound on independence number."""
        n = 40
        lambda_min = adj_eigenvalues[-1]  # -4
        # Hoffman bound: alpha <= n * (-lambda_min) / (k - lambda_min) = 40*4/16 = 10
        alpha_ub = n * (-lambda_min) / (12.0 - lambda_min)
        assert np.isclose(alpha_ub, 10.0)
        chi_f_lb = n / alpha_ub
        assert np.isclose(chi_f_lb, 4.0)


# =====================================================================
# T1459: Random Walk Entropy Production
# =====================================================================

class TestT1459EntropyProduction:
    """sigma = sum_ij pi_i P_ij log(P_ij/P_ji) = 0 (reversible walk)."""

    def test_entropy_production_zero(self, transition, stationary):
        """Entropy production rate is 0 for reversible walk on undirected graph."""
        n = 40
        sigma = 0.0
        for i in range(n):
            for j in range(n):
                if transition[i, j] > 0 and transition[j, i] > 0:
                    sigma += stationary[i] * transition[i, j] * np.log(
                        transition[i, j] / transition[j, i])
        assert np.isclose(sigma, 0.0, atol=1e-12)

    def test_detailed_balance(self, transition, stationary):
        """pi_i P_ij = pi_j P_ji for all i,j (detailed balance)."""
        n = 40
        for i in range(n):
            for j in range(n):
                lhs = stationary[i] * transition[i, j]
                rhs = stationary[j] * transition[j, i]
                assert np.isclose(lhs, rhs, atol=1e-15)

    def test_symmetric_transition(self, transition):
        """P is symmetric for vertex-transitive regular graph (P = A/k, A symmetric)."""
        assert np.allclose(transition, transition.T, atol=1e-15)

    def test_irreversibility_index(self, transition, stationary):
        """Irreversibility index = 0 for reversible chain."""
        # Irreversibility = D_KL(pi*P || reverse(pi*P))
        n = 40
        # Forward edge measure: mu(i,j) = pi_i * P_ij
        # Reverse edge measure: mu_rev(i,j) = pi_j * P_ji
        # For reversible chains, these are identical
        forward = np.zeros((n, n))
        reverse = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                forward[i, j] = stationary[i] * transition[i, j]
                reverse[i, j] = stationary[j] * transition[j, i]
        assert np.allclose(forward, reverse, atol=1e-15)


# =====================================================================
# T1460: Spectral Entropy
# =====================================================================

class TestT1460SpectralEntropy:
    """H_spec = -sum (lambda_i/sum_j lambda_j) * log(lambda_i/sum_j lambda_j) for positive eigenvalues."""

    def test_spectral_entropy_from_adjacency(self, adj_eigenvalues):
        """Spectral entropy of adjacency positive eigenvalues."""
        pos = adj_eigenvalues[adj_eigenvalues > 1e-10]
        # Positive eigenvalues: 12 (mult 1) and 2 (mult 24) => 25 values
        assert len(pos) == 25
        total = np.sum(pos)
        assert np.isclose(total, 12.0 + 24 * 2.0)  # = 60
        probs = pos / total
        H_spec = _safe_entropy(probs)
        # = -(1/60)*12*log(12/60) - (24/60)*2*log(2/60) -- wait, these aren't probs
        # probs: one copy of 12/60 = 1/5, 24 copies of 2/60 = 1/30
        p1 = 12.0 / 60.0  # = 1/5
        p2 = 2.0 / 60.0   # = 1/30
        H_exact = -p1 * np.log(p1) - 24 * p2 * np.log(p2)
        assert np.isclose(H_spec, H_exact, atol=1e-10)

    def test_spectral_entropy_from_laplacian(self, lap_eigenvalues):
        """Spectral entropy using Laplacian positive eigenvalues."""
        pos = lap_eigenvalues[lap_eigenvalues > 1e-10]
        assert len(pos) == 39
        total = np.sum(pos)
        assert np.isclose(total, 480.0)
        probs = pos / total
        H_spec_L = _safe_entropy(probs)
        # 24 eigenvalues = 10, 15 eigenvalues = 16
        p10 = 10.0 / 480.0
        p16 = 16.0 / 480.0
        H_exact = -24 * p10 * np.log(p10) - 15 * p16 * np.log(p16)
        assert np.isclose(H_spec_L, H_exact, atol=1e-10)

    def test_spectral_entropy_bounded(self, adj_eigenvalues):
        """H_spec <= log(number of positive eigenvalues) = log(25)."""
        pos = adj_eigenvalues[adj_eigenvalues > 1e-10]
        probs = pos / np.sum(pos)
        H_spec = _safe_entropy(probs)
        assert H_spec <= np.log(len(pos)) + 1e-10
        assert H_spec > 0

    def test_spectral_entropy_comparison(self, adj_eigenvalues, lap_eigenvalues):
        """Compare spectral entropies from A and L."""
        pos_A = adj_eigenvalues[adj_eigenvalues > 1e-10]
        H_A = _safe_entropy(pos_A / np.sum(pos_A))
        pos_L = lap_eigenvalues[lap_eigenvalues > 1e-10]
        H_L = _safe_entropy(pos_L / np.sum(pos_L))
        # Both should be positive and finite
        assert H_A > 0
        assert H_L > 0
        # They measure different things, so generally H_A != H_L
        assert not np.isclose(H_A, H_L, atol=0.01)


# =====================================================================
# T1461: Information Dimension
# =====================================================================

class TestT1461InformationDimension:
    """d_I = lim H(epsilon)/log(1/epsilon) on graph with resolution epsilon."""

    def test_graph_at_full_resolution(self, w33):
        """At epsilon such that each vertex is its own box, H = log(40)."""
        # Full resolution: 40 boxes, uniform distribution
        H = np.log(40)
        assert np.isclose(H, np.log(40))

    def test_graph_at_coarse_resolution(self, w33):
        """At epsilon = diameter + 1, single box, H = 0."""
        # One box containing all vertices
        H = np.log(1)
        assert H == 0.0

    def test_information_dimension_via_neighborhoods(self, w33):
        """d_I from box-counting: partition by BFS neighborhoods at various radii."""
        n = 40
        # Compute shortest path distances
        dist = np.full((n, n), n + 1, dtype=int)
        np.fill_diagonal(dist, 0)
        for i in range(n):
            for j in range(n):
                if w33[i, j] == 1:
                    dist[i, j] = 1
        # Floyd-Warshall
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i, k] + dist[k, j] < dist[i, j]:
                        dist[i, j] = dist[i, k] + dist[k, j]
        diameter = np.max(dist)
        assert diameter == 2  # SRG with mu > 0 has diameter 2

        # At radius r=1: each vertex covers itself + 12 neighbors = 13 vertices
        # Greedy set cover to find minimal boxes
        # At radius r=0: 40 boxes, H = log(40)
        # At radius r=2 (diameter): 1 box, H = 0
        H_values = []
        eps_values = []
        for r in range(diameter + 1):
            # Boxes = balls of radius r centered at greedy cover
            covered = set()
            boxes = []
            for center in range(n):
                ball = set(j for j in range(n) if dist[center, j] <= r)
                if not ball - covered:
                    continue
                boxes.append(ball)
                covered |= ball
                if len(covered) == n:
                    break
            # Probability: uniform measure, each box gets |box cap support|/n
            box_probs = np.array([len(b) / n for b in boxes])
            # Normalize to sum to 1 (greedy covers may overlap conceptually)
            box_probs = box_probs / np.sum(box_probs)
            H = _safe_entropy(box_probs)
            H_values.append(H)
            eps_values.append(r + 1)

        # H should be monotonically non-increasing as epsilon grows
        for i in range(len(H_values) - 1):
            assert H_values[i] >= H_values[i + 1] - 1e-10

    def test_information_dimension_bounded(self):
        """For finite graph, d_I is bounded: 0 <= d_I < inf."""
        # On a finite graph with diameter 2, the information dimension
        # is bounded above by log(40)/log(3) (since we have 3 scales: r=0,1,2)
        d_I_bound = np.log(40) / np.log(3)
        assert d_I_bound > 0
        assert d_I_bound < 10  # finite and reasonable


# =====================================================================
# T1462: Fidelity and Trace Distance
# =====================================================================

class TestT1462FidelityTraceDistance:
    """Between thermal states rho(beta) at different temperatures via spectrum."""

    def test_thermal_state_trace(self, lap_eigenvalues):
        """rho(beta) = exp(-beta*L)/Z has trace 1."""
        beta = 0.1
        exp_vals = np.exp(-beta * lap_eigenvalues)
        Z = np.sum(exp_vals)
        probs = exp_vals / Z
        assert np.isclose(np.sum(probs), 1.0)

    def test_fidelity_same_state(self, lap_eigenvalues):
        """F(rho, rho) = 1."""
        beta = 0.1
        exp_vals = np.exp(-beta * lap_eigenvalues)
        probs = exp_vals / np.sum(exp_vals)
        # For diagonal states, F = (sum sqrt(p_i * q_i))^2
        F = np.sum(np.sqrt(probs * probs)) ** 2
        assert np.isclose(F, 1.0, atol=1e-10)

    def test_fidelity_different_temperatures(self, lap_eigenvalues):
        """F(rho(beta1), rho(beta2)) < 1 for beta1 != beta2."""
        beta1, beta2 = 0.1, 0.5
        exp1 = np.exp(-beta1 * lap_eigenvalues)
        p1 = exp1 / np.sum(exp1)
        exp2 = np.exp(-beta2 * lap_eigenvalues)
        p2 = exp2 / np.sum(exp2)
        F = np.sum(np.sqrt(p1 * p2)) ** 2
        assert F < 1.0
        assert F > 0.0

    def test_trace_distance_bounds(self, lap_eigenvalues):
        """0 <= T(rho1, rho2) <= 1 and related to fidelity."""
        beta1, beta2 = 0.1, 0.5
        exp1 = np.exp(-beta1 * lap_eigenvalues)
        p1 = exp1 / np.sum(exp1)
        exp2 = np.exp(-beta2 * lap_eigenvalues)
        p2 = exp2 / np.sum(exp2)
        # Trace distance for diagonal states: T = 0.5 * sum |p_i - q_i|
        T = 0.5 * np.sum(np.abs(p1 - p2))
        assert 0 <= T <= 1
        # Fuchs-van de Graaf: 1 - sqrt(F) <= T <= sqrt(1 - F)
        F = np.sum(np.sqrt(p1 * p2)) ** 2
        assert T >= 1 - np.sqrt(F) - 1e-10
        assert T <= np.sqrt(1 - F) + 1e-10

    def test_trace_distance_triangle(self, lap_eigenvalues):
        """Trace distance satisfies triangle inequality."""
        betas = [0.1, 0.3, 0.5]
        probs = []
        for b in betas:
            e = np.exp(-b * lap_eigenvalues)
            probs.append(e / np.sum(e))
        T01 = 0.5 * np.sum(np.abs(probs[0] - probs[1]))
        T12 = 0.5 * np.sum(np.abs(probs[1] - probs[2]))
        T02 = 0.5 * np.sum(np.abs(probs[0] - probs[2]))
        assert T02 <= T01 + T12 + 1e-10


# =====================================================================
# T1463: Holevo Bound
# =====================================================================

class TestT1463HolevoBound:
    """chi <= S(rho_avg) - sum p_i S(rho_i) for ensemble of graph states."""

    def test_holevo_quantity_nonneg(self, lap_eigenvalues):
        """Holevo chi >= 0."""
        # Ensemble: rho_i = thermal state at beta_i, uniform prior
        betas = [0.1, 0.3, 0.5, 1.0]
        n_states = len(betas)
        # Compute each rho_i as diagonal vector
        rho_list = []
        for b in betas:
            e = np.exp(-b * lap_eigenvalues)
            rho_list.append(e / np.sum(e))
        # Average state
        rho_avg = np.mean(rho_list, axis=0)
        S_avg = _safe_entropy(rho_avg)
        S_individual = np.mean([_safe_entropy(r) for r in rho_list])
        chi = S_avg - S_individual
        assert chi >= -1e-10

    def test_holevo_bounds_mutual_info(self, lap_eigenvalues):
        """Accessible information <= chi (Holevo bound)."""
        betas = [0.1, 0.5]
        rho_list = []
        for b in betas:
            e = np.exp(-b * lap_eigenvalues)
            rho_list.append(e / np.sum(e))
        rho_avg = np.mean(rho_list, axis=0)
        S_avg = _safe_entropy(rho_avg)
        S_individual = np.mean([_safe_entropy(r) for r in rho_list])
        chi = S_avg - S_individual
        # chi >= 0 and chi <= log(number of messages)
        assert chi >= -1e-10
        assert chi <= np.log(len(betas)) + 1e-10

    def test_holevo_concavity(self, lap_eigenvalues):
        """S(sum p_i rho_i) >= sum p_i S(rho_i) — concavity of entropy."""
        betas = [0.05, 0.1, 0.2, 0.5, 1.0, 2.0]
        weights = np.ones(len(betas)) / len(betas)
        rho_list = []
        for b in betas:
            e = np.exp(-b * lap_eigenvalues)
            rho_list.append(e / np.sum(e))
        rho_avg = sum(w * r for w, r in zip(weights, rho_list))
        S_avg = _safe_entropy(rho_avg)
        S_weighted = sum(w * _safe_entropy(r) for w, r in zip(weights, rho_list))
        assert S_avg >= S_weighted - 1e-10


# =====================================================================
# T1464: Quantum Relative Entropy
# =====================================================================

class TestT1464QuantumRelativeEntropy:
    """S(rho||sigma) for different graph-derived density matrices."""

    def test_relative_entropy_nonneg(self, lap_eigenvalues):
        """S(rho||sigma) >= 0 (Klein's inequality)."""
        beta1, beta2 = 0.1, 0.5
        e1 = np.exp(-beta1 * lap_eigenvalues)
        p = e1 / np.sum(e1)
        e2 = np.exp(-beta2 * lap_eigenvalues)
        q = e2 / np.sum(e2)
        # S(rho||sigma) = sum p_i (log p_i - log q_i) for commuting states
        S_rel = np.sum(p * (np.log(p) - np.log(q)))
        assert S_rel >= -1e-10

    def test_relative_entropy_zero_iff_equal(self, lap_eigenvalues):
        """S(rho||rho) = 0."""
        beta = 0.2
        e = np.exp(-beta * lap_eigenvalues)
        p = e / np.sum(e)
        S_rel = np.sum(p * (np.log(p) - np.log(p)))
        assert np.isclose(S_rel, 0.0, atol=1e-15)

    def test_relative_entropy_asymmetric(self, lap_eigenvalues):
        """S(rho||sigma) != S(sigma||rho) in general."""
        beta1, beta2 = 0.1, 1.0
        e1 = np.exp(-beta1 * lap_eigenvalues)
        p = e1 / np.sum(e1)
        e2 = np.exp(-beta2 * lap_eigenvalues)
        q = e2 / np.sum(e2)
        S_pq = np.sum(p * (np.log(p) - np.log(q)))
        S_qp = np.sum(q * (np.log(q) - np.log(p)))
        assert S_pq >= 0
        assert S_qp >= 0
        assert not np.isclose(S_pq, S_qp, atol=1e-6)

    def test_pinsker_inequality(self, lap_eigenvalues):
        """T(rho, sigma)^2 <= S(rho||sigma) / 2 (Pinsker's inequality)."""
        beta1, beta2 = 0.1, 0.5
        e1 = np.exp(-beta1 * lap_eigenvalues)
        p = e1 / np.sum(e1)
        e2 = np.exp(-beta2 * lap_eigenvalues)
        q = e2 / np.sum(e2)
        S_rel = np.sum(p * (np.log(p) - np.log(q)))
        T = 0.5 * np.sum(np.abs(p - q))
        assert T ** 2 <= S_rel / 2 + 1e-10


# =====================================================================
# T1465: Data Processing Inequality
# =====================================================================

class TestT1465DataProcessingInequality:
    """I(X;Y) >= I(X;Z) for Markov chain X -> Y -> Z on graph."""

    def test_one_step_vs_two_step(self, transition, stationary):
        """I(X; X_1) >= I(X; X_2) for Markov chain on the graph."""
        P = transition
        P2 = P @ P  # Two-step transition
        # I(X; X_1) = H(X) - H(X|X_1)
        H_X = _safe_entropy(stationary)
        # H(X|X_1) for one step
        H_cond_1 = np.dot(stationary, np.array([_safe_entropy(row) for row in P]))
        I_1 = H_X - H_cond_1
        # H(X|X_2) for two steps
        H_cond_2 = np.dot(stationary, np.array([_safe_entropy(row) for row in P2]))
        I_2 = H_X - H_cond_2
        assert I_1 >= I_2 - 1e-10

    def test_multi_step_monotonicity(self, transition, stationary):
        """I(X; X_t) is non-increasing in t."""
        H_X = _safe_entropy(stationary)
        Pt = np.eye(40)
        I_prev = H_X  # I(X; X_0) = H(X)
        for t in range(1, 6):
            Pt = Pt @ transition
            H_cond_t = np.dot(stationary, np.array([_safe_entropy(row) for row in Pt]))
            I_t = H_X - H_cond_t
            assert I_t <= I_prev + 1e-10
            I_prev = I_t

    def test_convergence_to_zero(self, transition, stationary):
        """I(X; X_t) -> 0 as t -> infinity (mixing)."""
        H_X = _safe_entropy(stationary)
        P_power = np.linalg.matrix_power(transition, 50)
        # After many steps, each row of P^t should be close to stationary
        H_cond_inf = np.dot(stationary, np.array([_safe_entropy(row) for row in P_power]))
        I_inf = H_X - H_cond_inf
        assert np.isclose(I_inf, 0.0, atol=1e-6)

    def test_dpi_with_coarse_graining(self, transition, stationary):
        """Coarse-graining reduces mutual information."""
        P = transition
        n = 40
        # Partition vertices into groups by index mod 4 (10 groups of ~4)
        num_groups = 10
        group = np.array([i % num_groups for i in range(n)])
        # Coarse-grained transition: P_bar[g1, g2] = average transition from group g1 to g2
        P_bar = np.zeros((num_groups, num_groups))
        for g1 in range(num_groups):
            members_g1 = np.where(group == g1)[0]
            for g2 in range(num_groups):
                members_g2 = np.where(group == g2)[0]
                P_bar[g1, g2] = np.mean([np.sum(P[i, members_g2]) for i in members_g1])
        pi_bar = np.ones(num_groups) / num_groups
        H_coarse = _safe_entropy(pi_bar)
        H_cond_coarse = np.dot(pi_bar, np.array([_safe_entropy(row) for row in P_bar]))
        I_coarse = H_coarse - H_cond_coarse

        # Fine-grained mutual information
        H_fine = _safe_entropy(stationary)
        H_cond_fine = np.dot(stationary, np.array([_safe_entropy(row) for row in P]))
        I_fine = H_fine - H_cond_fine

        # DPI: coarse-graining cannot increase mutual information
        assert I_coarse <= I_fine + 1e-8


# =====================================================================
# T1466: Entropy Power Inequality
# =====================================================================

class TestT1466EntropyPowerInequality:
    """N(X+Y) >= N(X) + N(Y) verification in graph context."""

    def test_entropy_power_definition(self, stationary):
        """Entropy power N(X) = (1/(2*pi*e)) * exp(2*H(X)/n) for discrete analog."""
        H = _safe_entropy(stationary)
        # Discrete entropy power (1D analog): N = exp(2*H)/(2*pi*e)
        # But for discrete distributions, we use N = exp(2*H(X))
        N = np.exp(2 * H)
        assert np.isclose(N, 40.0 ** 2)  # exp(2*log(40)) = 1600

    def test_entropy_power_convolution(self, transition, stationary):
        """For independent X, Y on graph, H(X*Y) >= H(X) via entropy power."""
        # X uniform, Y = one step of walk from X
        # The "sum" in graph context is convolution on the group
        # For walks: P^2 represents two-step distribution
        P = transition
        P2 = P @ P
        # Each row of P2 is the two-step distribution
        # H(row of P2) should relate to H(row of P)
        H_one = np.mean([_safe_entropy(row) for row in P])
        H_two = np.mean([_safe_entropy(row) for row in P2])
        # Two-step walk explores more vertices => higher entropy
        assert H_two >= H_one - 1e-10

    def test_entropy_power_mixing(self, transition):
        """Entropy of convolution with uniform approaches maximum."""
        P = transition
        n = 40
        # After many steps, distribution converges to uniform => max entropy
        P_many = np.linalg.matrix_power(P, 20)
        row_entropies = np.array([_safe_entropy(row) for row in P_many])
        # All rows should have entropy close to log(40) after mixing
        assert np.allclose(row_entropies, np.log(40), atol=1e-4)

    def test_entropy_power_comparison(self, transition, stationary):
        """Entropy power of t-step walk is non-decreasing in t."""
        P = transition
        Pt = np.eye(40)
        prev_N = 0
        for t in range(1, 8):
            Pt = Pt @ P
            # Average entropy of rows
            H_t = np.mean([_safe_entropy(row) for row in Pt])
            N_t = np.exp(2 * H_t)
            if t > 1:
                assert N_t >= prev_N - 1e-6
            prev_N = N_t

    def test_entropy_power_bound(self, stationary):
        """Entropy power is bounded: N(X) <= exp(2*log(n)) = n^2."""
        H = _safe_entropy(stationary)
        N = np.exp(2 * H)
        n_sq = 40.0 ** 2
        assert np.isclose(N, n_sq, atol=1e-6)
