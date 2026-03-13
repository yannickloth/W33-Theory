#!/usr/bin/env python3
"""Tests for Phase CXXXVIII: Graph Diameter and Eccentricity Deep Computation.

The W(3,3) graph is SRG(40, 12, 2, 4) with spectrum {12^1, 2^24, -4^15}.
Since mu=4>0, any two non-adjacent vertices share 4 common neighbours,
making the graph connected with diameter 2.

Ten test classes cover:
  1. Diameter and radius
  2. Eccentricity distribution
  3. Distance matrix structure
  4. Distance matrix spectrum
  5. Wiener index
  6. Average path length and efficiency
  7. Periphery and center
  8. Distance distribution
  9. Distance powers (D^2)
 10. Transmission regularity
"""

from __future__ import annotations

import numpy as np
import pytest
from numpy.linalg import eigvalsh

# ---------------------------------------------------------------------------
# W(3,3) adjacency builder (symplectic form over PG(3,3))
# ---------------------------------------------------------------------------

def _build_w33():
    """Build the 40-vertex SRG(40,12,2,4) adjacency matrix."""
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
            u, w = points[i], points[j]
            omega = (u[0]*w[1] - u[1]*w[0] + u[2]*w[3] - u[3]*w[2]) % 3
            if omega == 0:
                A[i, j] = A[j, i] = 1
    return A


def _distance_matrix(A):
    """Compute all-pairs shortest path distance matrix via BFS."""
    n = A.shape[0]
    D = np.full((n, n), -1, dtype=int)
    for s in range(n):
        D[s, s] = 0
        queue = [s]
        head = 0
        while head < len(queue):
            u = queue[head]
            head += 1
            for v in range(n):
                if A[u, v] == 1 and D[s, v] == -1:
                    D[s, v] = D[s, u] + 1
                    queue.append(v)
    return D


# ---------------------------------------------------------------------------
# Module-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def adj():
    """Adjacency matrix A of W(3,3)."""
    return _build_w33()


@pytest.fixture(scope="module")
def dist(adj):
    """All-pairs shortest-path distance matrix D."""
    return _distance_matrix(adj)


@pytest.fixture(scope="module")
def n():
    """Number of vertices."""
    return 40


@pytest.fixture(scope="module")
def k():
    """Regularity (degree)."""
    return 12


@pytest.fixture(scope="module")
def eccentricities(dist):
    """Eccentricity array: ecc[i] = max_j D[i,j]."""
    return dist.max(axis=1)


@pytest.fixture(scope="module")
def transmissions(dist):
    """Transmission array: sigma[i] = sum_j D[i,j]."""
    return dist.sum(axis=1)


@pytest.fixture(scope="module")
def dist_spectrum(dist):
    """Eigenvalues of D sorted in descending order."""
    evals = eigvalsh(dist.astype(float))
    return np.sort(evals)[::-1]


@pytest.fixture(scope="module")
def d_squared(dist):
    """D^2 matrix."""
    return dist @ dist


# ===================================================================
# Class 1: Diameter and Radius
# ===================================================================

class TestDiameterAndRadius:
    """Diameter = radius = 2 for the vertex-transitive SRG(40,12,2,4)."""

    def test_diameter_is_2(self, dist):
        assert dist.max() == 2

    def test_radius_is_2(self, eccentricities):
        assert eccentricities.min() == 2

    def test_graph_is_connected(self, dist):
        # No entry should remain at the BFS sentinel value
        assert (dist >= 0).all()

    def test_diameter_at_least_1(self, dist, n):
        # Non-complete graph has diameter >= 1
        assert dist.max() >= 1

    def test_diameter_at_most_n_minus_1(self, dist, n):
        assert dist.max() <= n - 1

    def test_radius_leq_diameter(self, eccentricities):
        assert eccentricities.min() <= eccentricities.max()

    def test_all_distances_at_most_2(self, dist):
        assert (dist <= 2).all()

    def test_exists_pair_at_distance_2(self, dist):
        assert (dist == 2).any()

    def test_no_self_distance_positive(self, dist, n):
        for i in range(n):
            assert dist[i, i] == 0

    def test_max_eccentricity_equals_diameter(self, eccentricities, dist):
        assert eccentricities.max() == dist.max()

    def test_min_eccentricity_equals_radius(self, eccentricities):
        assert eccentricities.min() == 2


# ===================================================================
# Class 2: Eccentricity Distribution
# ===================================================================

class TestEccentricityDistribution:
    """All eccentricities equal 2 (vertex-transitive graph)."""

    def test_ecc_vertex_0(self, eccentricities):
        assert eccentricities[0] == 2

    def test_all_eccentricities_equal_2(self, eccentricities, n):
        assert np.array_equal(eccentricities, np.full(n, 2))

    def test_ecc_shape(self, eccentricities, n):
        assert eccentricities.shape == (n,)

    def test_ecc_std_zero(self, eccentricities):
        assert eccentricities.std() == 0.0

    def test_mean_eccentricity(self, eccentricities):
        assert eccentricities.mean() == 2.0

    def test_min_ecc(self, eccentricities):
        assert eccentricities.min() == 2

    def test_max_ecc(self, eccentricities):
        assert eccentricities.max() == 2

    def test_ecc_equals_row_max(self, dist, n):
        for i in range(n):
            assert dist[i].max() == 2

    def test_num_distinct_eccentricities(self, eccentricities):
        assert len(set(eccentricities.tolist())) == 1

    def test_uniform_eccentricity_is_vertex_transitive_signature(self, eccentricities, n):
        # All eccentricities identical implies graph could be vertex-transitive
        assert np.unique(eccentricities).size == 1


# ===================================================================
# Class 3: Distance Matrix Structure
# ===================================================================

class TestDistanceMatrixStructure:
    """D[i,j] in {0,1,2}, symmetric, zero-diagonal, related to A."""

    def test_symmetric(self, dist):
        assert np.array_equal(dist, dist.T)

    def test_zero_diagonal(self, dist, n):
        assert np.array_equal(np.diag(dist), np.zeros(n, dtype=int))

    def test_entries_in_012(self, dist):
        vals = set(np.unique(dist))
        assert vals == {0, 1, 2}

    def test_shape(self, dist, n):
        assert dist.shape == (n, n)

    def test_d1_iff_adjacent(self, dist, adj, n):
        for i in range(n):
            for j in range(n):
                if i != j:
                    assert (dist[i, j] == 1) == (adj[i, j] == 1)

    def test_d2_iff_non_adjacent(self, dist, adj, n):
        for i in range(n):
            for j in range(n):
                if i != j:
                    assert (dist[i, j] == 2) == (adj[i, j] == 0)

    def test_formula_D_eq_2JmI_minus_A(self, dist, adj, n):
        J = np.ones((n, n), dtype=int)
        I = np.eye(n, dtype=int)
        expected = 2 * (J - I) - adj
        assert np.array_equal(dist, expected)

    def test_integer_valued(self, dist):
        assert dist.dtype in (np.int32, np.int64, int)

    def test_non_negative(self, dist):
        assert (dist >= 0).all()

    def test_triangle_inequality_sample(self, dist, n):
        # Check triangle inequality for 200 random triples
        rng = np.random.RandomState(42)
        for _ in range(200):
            i, j, m = rng.choice(n, 3, replace=False)
            assert dist[i, j] <= dist[i, m] + dist[m, j]

    def test_trace_zero(self, dist):
        assert np.trace(dist) == 0


# ===================================================================
# Class 4: Distance Matrix Spectrum
# ===================================================================

class TestDistanceMatrixSpectrum:
    """D = 2J - 2I - A has spectrum {66^1, -4^24, 2^15}."""

    def test_largest_eigenvalue_66(self, dist_spectrum):
        assert abs(dist_spectrum[0] - 66.0) < 1e-8

    def test_multiplicity_66(self, dist_spectrum):
        count = np.sum(np.abs(dist_spectrum - 66.0) < 1e-6)
        assert count == 1

    def test_eigenvalue_neg4_mult_24(self, dist_spectrum):
        count = np.sum(np.abs(dist_spectrum - (-4.0)) < 1e-6)
        assert count == 24

    def test_eigenvalue_2_mult_15(self, dist_spectrum):
        count = np.sum(np.abs(dist_spectrum - 2.0) < 1e-6)
        assert count == 15

    def test_three_distinct_eigenvalues(self, dist_spectrum):
        rounded = np.round(dist_spectrum, 6)
        assert len(set(rounded)) == 3

    def test_trace_sum_eigenvalues_zero(self, dist_spectrum):
        # trace(D) = 0 = sum of eigenvalues
        assert abs(dist_spectrum.sum()) < 1e-6

    def test_trace_d2_sum_squared_eigenvalues(self, dist_spectrum):
        # trace(D^2) = sum(eigenvalues^2) = 66^2 + 24*16 + 15*4 = 4800
        ssq = np.sum(dist_spectrum ** 2)
        assert abs(ssq - 4800.0) < 1e-4

    def test_determinant_positive(self, dist_spectrum):
        # det(D) = 66 * (-4)^24 * 2^15 > 0 (since (-4)^24 > 0)
        log_det = np.sum(np.log(np.abs(dist_spectrum)))
        sign = np.prod(np.sign(dist_spectrum))
        assert sign > 0

    def test_full_rank(self, dist_spectrum):
        # No zero eigenvalue
        assert np.all(np.abs(dist_spectrum) > 0.5)

    def test_all_ones_is_eigenvector_66(self, dist, n):
        ones = np.ones(n)
        result = dist.astype(float) @ ones
        expected = 66.0 * ones
        assert np.allclose(result, expected)


# ===================================================================
# Class 5: Wiener Index
# ===================================================================

class TestWienerIndex:
    """Wiener index W = sum of all pairwise distances (unordered) = 1320."""

    def test_wiener_index_value(self, dist):
        W = dist.sum() // 2
        assert W == 1320

    def test_wiener_half_total(self, dist):
        assert dist.sum() == 2 * 1320

    def test_wiener_from_distance_counts(self, dist, n):
        # W = 240*1 + 540*2 = 1320
        d1_pairs = np.sum(dist == 1) // 2
        d2_pairs = np.sum(dist == 2) // 2
        W = d1_pairs * 1 + d2_pairs * 2
        assert W == 1320

    def test_wiener_from_transmission(self, transmissions, n):
        # W = (1/2) * sum(transmissions)
        W = transmissions.sum() // 2
        assert W == 1320

    def test_sum_of_squared_distances(self, dist):
        # WW = sum over unordered pairs of d^2 = 240*1 + 540*4 = 2400
        WW = np.sum(dist ** 2) // 2
        assert WW == 2400

    def test_hyper_wiener_index(self, dist):
        # Hyper-Wiener = (W + WW) / 2 = (1320 + 2400) / 2 = 1860
        W = dist.sum() // 2
        WW = np.sum(dist ** 2) // 2
        hyper = (W + WW) // 2
        assert hyper == 1860

    def test_wiener_geq_pairs(self, dist, n):
        # W >= C(n,2) with equality iff complete graph
        W = dist.sum() // 2
        pairs = n * (n - 1) // 2
        assert W >= pairs

    def test_wiener_strictly_greater_than_complete(self, dist, n):
        # Not a complete graph, so W > C(n,2) = 780
        W = dist.sum() // 2
        assert W > n * (n - 1) // 2

    def test_schultz_index(self, dist, adj, n, k):
        # For k-regular graph: Schultz = sum (deg(i)+deg(j))*d(i,j) over pairs
        # = 2k * W = 24 * 1320 = 31680
        W = dist.sum() // 2
        schultz = 2 * k * W
        assert schultz == 31680

    def test_wiener_formula_nk(self, n, k):
        # W = (k * 1 + (n-1-k) * 2) * n / 2 = 66 * 40 / 2
        W = (k + 2 * (n - 1 - k)) * n // 2
        assert W == 1320


# ===================================================================
# Class 6: Average Path Length and Efficiency
# ===================================================================

class TestAveragePathLengthAndEfficiency:
    """Average path length = 22/13, global efficiency = 17/26."""

    def test_avg_path_length_value(self, dist, n):
        pairs = n * (n - 1)
        off_diag_sum = dist.sum()
        avg = off_diag_sum / pairs
        assert abs(avg - 22 / 13) < 1e-12

    def test_avg_path_length_gt_1(self, dist, n):
        pairs = n * (n - 1)
        avg = dist.sum() / pairs
        assert avg > 1.0

    def test_avg_path_length_lt_2(self, dist, n):
        pairs = n * (n - 1)
        avg = dist.sum() / pairs
        assert avg < 2.0

    def test_global_efficiency(self, dist, n):
        # E_glob = (1 / n(n-1)) * sum_{i!=j} 1/d(i,j)
        inv_d = np.zeros_like(dist, dtype=float)
        for i in range(n):
            for j in range(n):
                if i != j:
                    inv_d[i, j] = 1.0 / dist[i, j]
        E_glob = inv_d.sum() / (n * (n - 1))
        assert abs(E_glob - 17 / 26) < 1e-12

    def test_efficiency_gt_half(self, dist, n):
        d_safe = dist.copy()
        d_safe[d_safe == 0] = 1  # mask diagonal; those contribute 0 anyway
        inv_d = np.where(dist > 0, 1.0 / d_safe, 0.0)
        E_glob = inv_d.sum() / (n * (n - 1))
        assert E_glob > 0.5

    def test_efficiency_lt_1(self, dist, n):
        d_safe = dist.copy()
        d_safe[d_safe == 0] = 1
        inv_d = np.where(dist > 0, 1.0 / d_safe, 0.0)
        E_glob = inv_d.sum() / (n * (n - 1))
        assert E_glob < 1.0

    def test_closeness_centrality_uniform(self, dist, n):
        # C(v) = (n-1) / sigma(v); same for all v in vertex-transitive graph
        closeness = np.array([(n - 1) / dist[v].sum() for v in range(n)])
        assert abs(closeness.std()) < 1e-14

    def test_closeness_centrality_value(self, dist, n):
        # C(v) = 39 / 66 = 13/22
        c0 = (n - 1) / dist[0].sum()
        assert abs(c0 - 13 / 22) < 1e-12

    def test_harmonic_centrality_uniform(self, dist, n):
        harm = np.zeros(n)
        for v in range(n):
            harm[v] = sum(1.0 / dist[v, u] for u in range(n) if u != v)
        assert abs(harm.std()) < 1e-10

    def test_harmonic_centrality_value(self, dist, n):
        # H(v) = sum 1/d(v,u) = 12*1 + 27*0.5 = 12 + 13.5 = 25.5
        h0 = sum(1.0 / dist[0, u] for u in range(n) if u != 0)
        assert abs(h0 - 25.5) < 1e-12


# ===================================================================
# Class 7: Periphery and Center
# ===================================================================

class TestPeripheryAndCenter:
    """Periphery = center = V since all eccentricities = 2 = diameter = radius."""

    def test_periphery_is_all_vertices(self, eccentricities, n):
        # periphery = {v : ecc(v) = diam}
        diam = eccentricities.max()
        periphery = set(np.where(eccentricities == diam)[0])
        assert periphery == set(range(n))

    def test_center_is_all_vertices(self, eccentricities, n):
        # center = {v : ecc(v) = rad}
        rad = eccentricities.min()
        center = set(np.where(eccentricities == rad)[0])
        assert center == set(range(n))

    def test_periphery_equals_center(self, eccentricities):
        diam = eccentricities.max()
        rad = eccentricities.min()
        periphery = set(np.where(eccentricities == diam)[0])
        center = set(np.where(eccentricities == rad)[0])
        assert periphery == center

    def test_periphery_size_40(self, eccentricities):
        diam = eccentricities.max()
        assert np.sum(eccentricities == diam) == 40

    def test_center_size_40(self, eccentricities):
        rad = eccentricities.min()
        assert np.sum(eccentricities == rad) == 40

    def test_periphery_union_center_is_V(self, eccentricities, n):
        diam = eccentricities.max()
        rad = eccentricities.min()
        union = set(np.where(eccentricities == diam)[0]) | set(
            np.where(eccentricities == rad)[0]
        )
        assert union == set(range(n))

    def test_periphery_intersect_center_is_V(self, eccentricities, n):
        diam = eccentricities.max()
        rad = eccentricities.min()
        inter = set(np.where(eccentricities == diam)[0]) & set(
            np.where(eccentricities == rad)[0]
        )
        assert inter == set(range(n))

    def test_vertex_0_in_center(self, eccentricities):
        rad = eccentricities.min()
        assert eccentricities[0] == rad

    def test_vertex_0_in_periphery(self, eccentricities):
        diam = eccentricities.max()
        assert eccentricities[0] == diam

    def test_self_centered_graph(self, eccentricities, n):
        # A graph is self-centered if center = V
        rad = eccentricities.min()
        assert np.all(eccentricities == rad)


# ===================================================================
# Class 8: Distance Distribution
# ===================================================================

class TestDistanceDistribution:
    """Distance-1 pairs = 240, distance-2 pairs = 540, total = 780."""

    def test_d0_count(self, dist, n):
        # Diagonal entries
        assert np.sum(dist == 0) == n

    def test_d1_ordered_count(self, dist):
        # Ordered pairs at distance 1 = 2 * edges = 480
        assert np.sum(dist == 1) == 480

    def test_d1_unordered_count(self, dist):
        assert np.sum(dist == 1) // 2 == 240

    def test_d2_ordered_count(self, dist):
        assert np.sum(dist == 2) == 1080

    def test_d2_unordered_count(self, dist):
        assert np.sum(dist == 2) // 2 == 540

    def test_total_pairs(self, n):
        assert n * (n - 1) // 2 == 780

    def test_d1_plus_d2_equals_total(self, dist, n):
        d1 = np.sum(dist == 1) // 2
        d2 = np.sum(dist == 2) // 2
        assert d1 + d2 == n * (n - 1) // 2

    def test_each_vertex_12_at_d1(self, dist, n):
        for v in range(n):
            assert np.sum(dist[v] == 1) == 12

    def test_each_vertex_27_at_d2(self, dist, n):
        for v in range(n):
            assert np.sum(dist[v] == 2) == 27

    def test_no_vertex_at_d_ge_3(self, dist):
        assert np.sum(dist >= 3) == 0

    def test_d1_matches_edge_count(self, adj):
        edges = adj.sum() // 2
        assert edges == 240

    def test_distance_histogram(self, dist):
        # Ordered histogram: [40 at d=0, 480 at d=1, 1080 at d=2]
        hist = [np.sum(dist == d) for d in range(3)]
        assert hist == [40, 480, 1080]


# ===================================================================
# Class 9: Distance Powers D^2
# ===================================================================

class TestDistancePowerD2:
    """D^2 = 108J + 12I + 2A with spectrum {4356^1, 16^24, 4^15}."""

    def test_d2_formula(self, d_squared, adj, n):
        J = np.ones((n, n), dtype=int)
        I = np.eye(n, dtype=int)
        expected = 108 * J + 12 * I + 2 * adj
        assert np.array_equal(d_squared, expected)

    def test_d2_symmetric(self, d_squared):
        assert np.array_equal(d_squared, d_squared.T)

    def test_d2_diagonal_120(self, d_squared, n):
        # D^2[i,i] = sum_j d(i,j)^2 = 12*1 + 27*4 = 120
        for i in range(n):
            assert d_squared[i, i] == 120

    def test_d2_adjacent_entry_110(self, d_squared, adj, n):
        # For adjacent i,j: 108 + 0 + 2 = 110
        for i in range(n):
            for j in range(i + 1, n):
                if adj[i, j] == 1:
                    assert d_squared[i, j] == 110
                    break
            else:
                continue
            break

    def test_d2_non_adjacent_entry_108(self, d_squared, adj, n):
        # For non-adjacent i!=j: 108 + 0 + 0 = 108
        for i in range(n):
            for j in range(i + 1, n):
                if adj[i, j] == 0:
                    assert d_squared[i, j] == 108
                    break
            else:
                continue
            break

    def test_d2_all_adjacent_110(self, d_squared, adj, n):
        mask = (adj == 1)
        assert np.all(d_squared[mask] == 110)

    def test_d2_all_non_adjacent_off_diag_108(self, d_squared, adj, n):
        I = np.eye(n, dtype=int)
        mask = (adj == 0) & (I == 0)
        assert np.all(d_squared[mask] == 108)

    def test_d2_trace(self, d_squared, n):
        assert np.trace(d_squared) == 120 * n  # = 4800

    def test_d2_spectrum_4356(self, d_squared):
        evals = np.sort(eigvalsh(d_squared.astype(float)))[::-1]
        assert abs(evals[0] - 4356.0) < 1e-4

    def test_d2_spectrum_16_mult_24(self, d_squared):
        evals = eigvalsh(d_squared.astype(float))
        count = np.sum(np.abs(evals - 16.0) < 1e-4)
        assert count == 24

    def test_d2_spectrum_4_mult_15(self, d_squared):
        evals = eigvalsh(d_squared.astype(float))
        count = np.sum(np.abs(evals - 4.0) < 1e-4)
        assert count == 15

    def test_d2_minus_d_non_negative(self, d_squared, dist):
        diff = d_squared - dist
        assert (diff >= 0).all()


# ===================================================================
# Class 10: Transmission Regularity
# ===================================================================

class TestTransmissionRegularity:
    """Every vertex has transmission 66; the graph is transmission-regular."""

    def test_transmission_vertex_0(self, transmissions):
        assert transmissions[0] == 66

    def test_all_transmissions_66(self, transmissions, n):
        assert np.array_equal(transmissions, np.full(n, 66))

    def test_transmission_shape(self, transmissions, n):
        assert transmissions.shape == (n,)

    def test_transmission_std_zero(self, transmissions):
        assert transmissions.std() == 0.0

    def test_transmission_regular(self, transmissions):
        assert len(set(transmissions.tolist())) == 1

    def test_transmission_formula(self, n, k):
        # sigma = k*1 + (n-1-k)*2
        sigma = k + 2 * (n - 1 - k)
        assert sigma == 66

    def test_sum_of_transmissions(self, transmissions, n):
        assert transmissions.sum() == n * 66  # = 2640

    def test_twice_wiener_equals_sum_transmissions(self, transmissions, dist):
        W = dist.sum() // 2
        assert 2 * W == transmissions.sum()

    def test_normalized_transmission(self, transmissions, n):
        # sigma_i / (n-1) = 66/39 = 22/13
        norm = transmissions[0] / (n - 1)
        assert abs(norm - 22 / 13) < 1e-12

    def test_betweenness_centrality_uniform(self, dist, adj, n):
        # For vertex-transitive graph all betweenness values are equal.
        # B(v) = sum_{s!=v!=t} (num shortest s-t paths through v) / (num shortest s-t paths)
        # For diameter-2 SRG: paths of length 1 (adjacent) never go through
        # an intermediate; paths of length 2 go through one of mu common
        # neighbors. Each non-adjacent pair has mu = 4 shortest paths.
        # By symmetry, each intermediate vertex is used equally.
        # Total intermediary loads = 540 * 1 (one intermediate per path
        # of length 2, and there are 4 paths, so each of the 4 intermediaries
        # handles 1 path).  But let's just verify uniformity numerically.
        betw = np.zeros(n, dtype=float)
        for s in range(n):
            for t in range(s + 1, n):
                if dist[s, t] == 1:
                    continue  # direct edge, no intermediary
                # Non-adjacent: shortest paths of length 2 go through common neighbors
                intermediaries = [
                    v for v in range(n) if adj[s, v] == 1 and adj[v, t] == 1
                ]
                num_paths = len(intermediaries)
                for v in intermediaries:
                    betw[v] += 1.0 / num_paths
        assert abs(betw.std()) < 1e-10, "Betweenness must be uniform"

    def test_betweenness_centrality_value(self, dist, adj, n):
        # Each of 540 non-adjacent pairs has mu=4 shortest paths;
        # total load = 540 (each path uses 1 intermediary).
        # By symmetry spread over 40 vertices: B(v) = 540/40 = 13.5
        betw = np.zeros(n, dtype=float)
        for s in range(n):
            for t in range(s + 1, n):
                if dist[s, t] == 1:
                    continue
                intermediaries = [
                    v for v in range(n) if adj[s, v] == 1 and adj[v, t] == 1
                ]
                num_paths = len(intermediaries)
                for v in intermediaries:
                    betw[v] += 1.0 / num_paths
        assert abs(betw[0] - 13.5) < 1e-10
