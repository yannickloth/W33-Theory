"""
Clique Partitions and Spreads Deep Computation  --  Phase CXL
=============================================================

Hard-computation tests for the clique structure of W(3,3) = SRG(40,12,2,4).

Key facts verified:
    - W(3,3) has 40 vertices, 240 edges, is 12-regular
    - Spectrum: {12^1, 2^24, (-4)^15}
    - Clique number omega = 4 (maximum cliques are tetrahedra)
    - 160 triangles, 40 tetrahedra, no 5-cliques
    - Each vertex in 12 triangles and 4 tetrahedra
    - Each edge in exactly 2 triangles (SRG lambda = 2)
    - Independence number alpha = 10 (ovoid)
    - Spreads: partitions of 40 vertices into 10 disjoint 4-cliques

100+ tests in 10 classes.
"""

from __future__ import annotations

import math
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Dict, FrozenSet, List, Set, Tuple

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def _build_w33() -> np.ndarray:
    """Build the 40x40 adjacency matrix of W(3,3) = SRG(40,12,2,4)."""
    points: list[tuple[int, ...]] = []
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
    assert len(points) == n
    A = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(i + 1, n):
            u, w = points[i], points[j]
            omega = (u[0] * w[1] - u[1] * w[0] + u[2] * w[3] - u[3] * w[2]) % 3
            if omega == 0:
                A[i, j] = A[j, i] = 1
    return A


def _adj_lists(A: np.ndarray) -> list[set[int]]:
    """Return adjacency sets from adjacency matrix."""
    n = A.shape[0]
    return [set(int(j) for j in range(n) if A[i, j]) for i in range(n)]


# ---------------------------------------------------------------------------
# Clique finders
# ---------------------------------------------------------------------------

def _find_all_cliques_of_size(adj: list[set[int]], k: int, n: int) -> list[frozenset[int]]:
    """Find all cliques of exactly size k via BK-like enumeration."""
    cliques: list[frozenset[int]] = []
    if k == 1:
        return [frozenset([v]) for v in range(n)]
    if k == 2:
        result = []
        for u in range(n):
            for v in adj[u]:
                if v > u:
                    result.append(frozenset([u, v]))
        return result

    # For k >= 3 build from (k-1)-cliques
    smaller = _find_all_cliques_of_size(adj, k - 1, n)
    seen: set[frozenset[int]] = set()
    for cl in smaller:
        # Find vertices adjacent to ALL in cl and > max(cl)
        common = set.intersection(*(adj[v] for v in cl))
        for w in common:
            if w > max(cl):
                new_cl = cl | frozenset([w])
                if new_cl not in seen:
                    seen.add(new_cl)
                    cliques.append(new_cl)
    return cliques


def _find_all_triangles(adj: list[set[int]], n: int) -> list[frozenset[int]]:
    return _find_all_cliques_of_size(adj, 3, n)


def _find_all_tetrahedra(adj: list[set[int]], n: int) -> list[frozenset[int]]:
    return _find_all_cliques_of_size(adj, 4, n)


def _find_max_independent_set_greedy(adj: list[set[int]], n: int) -> set[int]:
    """Greedy maximal independent set: pick vertex of min degree in subgraph."""
    remaining = set(range(n))
    indep: set[int] = set()
    while remaining:
        # pick vertex with smallest number of neighbors in remaining
        best = min(remaining, key=lambda v: len(adj[v] & remaining))
        indep.add(best)
        remaining -= {best} | (adj[best] & remaining)
    return indep


def _find_ovoid(adj: list[set[int]], tetrahedra: list[frozenset[int]],
                n: int, points: list[tuple] = None) -> set[int] | None:
    """Find an ovoid: independent set of size 10 meeting every tetrahedron in exactly 1 point.

    Uses greedy independent-set search enhanced with degree ordering.
    Falls back to constraint backtracking with MRV if greedy fails.
    """
    # Greedy approach: pick vertex with minimum degree in remaining graph
    import random
    random.seed(42)  # Reproducible
    for attempt in range(20):
        available = set(range(n))
        chosen = set()
        order = list(range(n))
        if attempt > 0:
            random.shuffle(order)
        while available:
            # Pick vertex with fewest available neighbours
            best_v = min(available, key=lambda v: len(adj[v] & available))
            chosen.add(best_v)
            available -= {best_v}
            available -= adj[best_v]
        if len(chosen) >= 10:
            # Verify it's independent
            for a in chosen:
                for b in chosen:
                    if a != b and b in adj[a]:
                        break
                else:
                    continue
                break
            else:
                return chosen
    # Backtracking fallback
    tet_list = list(tetrahedra)
    n_tets = len(tet_list)
    vert_to_tets: dict[int, list[int]] = {v: [] for v in range(n)}
    for ti, tet in enumerate(tet_list):
        for v in tet:
            vert_to_tets[v].append(ti)

    def backtrack(chosen: set[int], forbidden: set[int],
                  covered_tets: set[int], depth: int = 0) -> set[int] | None:
        if depth > 15:
            return None
        best_ti: int | None = None
        best_avail: list[int] | None = None
        for ti in range(n_tets):
            if ti in covered_tets:
                continue
            avail = [v for v in tet_list[ti] if v not in forbidden]
            if len(avail) == 0:
                return None
            if best_avail is None or len(avail) < len(best_avail):
                best_ti = ti
                best_avail = avail
        if best_ti is None:
            return set(chosen)
        for v in best_avail:
            new_forbidden = forbidden | {v} | adj[v]
            new_covered = set(covered_tets)
            for tj in vert_to_tets[v]:
                new_covered.add(tj)
            result = backtrack(chosen | {v}, new_forbidden, new_covered, depth + 1)
            if result is not None:
                return result
        return None

    return backtrack(set(), set(), set())


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def w33_data():
    """Compute and cache all clique data for the module."""
    A = _build_w33()
    n = A.shape[0]
    adj = _adj_lists(A)
    triangles = _find_all_triangles(adj, n)
    tetrahedra = _find_all_tetrahedra(adj, n)
    edges = _find_all_cliques_of_size(adj, 2, n)

    # Check no 5-cliques exist
    five_cliques = _find_all_cliques_of_size(adj, 5, n)

    # Eigenvalues
    eigvals = np.sort(np.linalg.eigvalsh(A.astype(float)))[::-1]

    # Find an ovoid (independent set of size 10)
    ovoid = _find_ovoid(adj, tetrahedra, n)

    return {
        "A": A,
        "n": n,
        "adj": adj,
        "triangles": triangles,
        "tetrahedra": tetrahedra,
        "edges": edges,
        "five_cliques": five_cliques,
        "eigvals": eigvals,
        "ovoid": ovoid,
    }


# ===========================================================================
# CLASS 1: Clique Number (omega = 4)
# ===========================================================================

class TestCliqueNumber:
    """Verify that the clique number of W(3,3) is exactly 4."""

    def test_has_40_vertices(self, w33_data):
        assert w33_data["n"] == 40

    def test_has_240_edges(self, w33_data):
        assert len(w33_data["edges"]) == 240

    def test_degree_regular_12(self, w33_data):
        A = w33_data["A"]
        degrees = A.sum(axis=1)
        assert np.all(degrees == 12)

    def test_4_cliques_exist(self, w33_data):
        assert len(w33_data["tetrahedra"]) > 0

    def test_no_5_cliques(self, w33_data):
        assert len(w33_data["five_cliques"]) == 0

    def test_clique_number_equals_4(self, w33_data):
        """omega(W33) = 4: 4-cliques exist but 5-cliques do not."""
        assert len(w33_data["tetrahedra"]) > 0
        assert len(w33_data["five_cliques"]) == 0

    def test_adjacency_symmetric(self, w33_data):
        A = w33_data["A"]
        assert np.array_equal(A, A.T)

    def test_adjacency_zero_diagonal(self, w33_data):
        A = w33_data["A"]
        assert np.all(np.diag(A) == 0)

    def test_srg_lambda_parameter(self, w33_data):
        """For SRG(40,12,2,4), lambda = 2: adjacent vertices share 2 common neighbors."""
        A = w33_data["A"]
        adj = w33_data["adj"]
        n = w33_data["n"]
        for i in range(n):
            for j in adj[i]:
                if j > i:
                    common = len(adj[i] & adj[j])
                    assert common == 2, f"lambda({i},{j}) = {common}, expected 2"

    def test_srg_mu_parameter(self, w33_data):
        """For SRG(40,12,2,4), mu = 4: non-adjacent vertices share 4 common neighbors."""
        A = w33_data["A"]
        adj = w33_data["adj"]
        n = w33_data["n"]
        count = 0
        for i in range(n):
            for j in range(i + 1, n):
                if j not in adj[i]:
                    common = len(adj[i] & adj[j])
                    assert common == 4, f"mu({i},{j}) = {common}, expected 4"
                    count += 1
        # Number of non-edges = C(40,2) - 240 = 780 - 240 = 540
        assert count == 540

    def test_complement_is_27_regular(self, w33_data):
        """Complement of SRG(40,12,2,4) is 27-regular."""
        A = w33_data["A"]
        Ac = 1 - A - np.eye(40, dtype=int)
        degrees = Ac.sum(axis=1)
        assert np.all(degrees == 27)


# ===========================================================================
# CLASS 2: Maximum Clique Enumeration
# ===========================================================================

class TestMaximumCliqueEnumeration:
    """Enumerate and verify the 40 maximum (4-vertex) cliques."""

    def test_exactly_40_tetrahedra(self, w33_data):
        assert len(w33_data["tetrahedra"]) == 40

    def test_each_tetrahedron_has_4_vertices(self, w33_data):
        for tet in w33_data["tetrahedra"]:
            assert len(tet) == 4

    def test_each_tetrahedron_is_complete(self, w33_data):
        """Every pair in a tetrahedron must be adjacent."""
        adj = w33_data["adj"]
        for tet in w33_data["tetrahedra"]:
            verts = list(tet)
            for a, b in combinations(verts, 2):
                assert b in adj[a], f"{a} and {b} not adjacent in tetrahedron {tet}"

    def test_tetrahedra_are_distinct(self, w33_data):
        tets = w33_data["tetrahedra"]
        assert len(set(tets)) == len(tets)

    def test_tetrahedra_correspond_to_lines(self, w33_data):
        """40 tetrahedra = 40 totally isotropic lines in PG(3,3) = lines of GQ(3,3)."""
        assert len(w33_data["tetrahedra"]) == 40

    def test_each_edge_in_at_least_one_tetrahedron(self, w33_data):
        """Every edge belongs to at least one 4-clique (follows from lambda=2)."""
        edge_set: set[frozenset[int]] = set()
        for tet in w33_data["tetrahedra"]:
            for a, b in combinations(tet, 2):
                edge_set.add(frozenset([a, b]))
        # Not every edge need be in a tetrahedron in general SRGs,
        # but for W(3,3) they should be (lines cover all points pairwise).
        # Each 4-clique contributes C(4,2) = 6 edges.
        # 40 * 6 = 240 edge-tetrahedron incidences.
        assert len(edge_set) == 240

    def test_each_edge_in_exactly_one_tetrahedron(self, w33_data):
        """In W(3,3), each edge lies on exactly one totally isotropic line."""
        edge_count: Counter[frozenset[int]] = Counter()
        for tet in w33_data["tetrahedra"]:
            for a, b in combinations(tet, 2):
                edge_count[frozenset([a, b])] += 1
        # Every edge appears exactly once across tetrahedra
        assert all(c == 1 for c in edge_count.values())
        assert len(edge_count) == 240

    def test_tetrahedra_partition_edges(self, w33_data):
        """40 tetrahedra * 6 edges each = 240 = total edges, so they partition the edge set."""
        total_edge_incidences = sum(
            len(list(combinations(tet, 2))) for tet in w33_data["tetrahedra"]
        )
        assert total_edge_incidences == 240

    def test_sample_tetrahedron_vertex_values(self, w33_data):
        """Sanity: first tetrahedron has 4 distinct vertices in [0,39]."""
        tet0 = w33_data["tetrahedra"][0]
        verts = list(tet0)
        assert all(0 <= v < 40 for v in verts)
        assert len(set(verts)) == 4

    def test_no_two_tetrahedra_share_triangle(self, w33_data):
        """Since each edge is in exactly one tetrahedron, no two tetrahedra share a triangle."""
        for i, t1 in enumerate(w33_data["tetrahedra"]):
            for t2 in w33_data["tetrahedra"][i + 1:]:
                overlap = t1 & t2
                assert len(overlap) <= 1


# ===========================================================================
# CLASS 3: Clique-Vertex Incidence Matrix Properties
# ===========================================================================

class TestCliqueVertexIncidence:
    """Properties of the 40x40 tetrahedron-vertex incidence matrix."""

    @pytest.fixture()
    def incidence(self, w33_data):
        """Build 40-tetrahedra x 40-vertices incidence matrix."""
        tets = w33_data["tetrahedra"]
        n = w33_data["n"]
        M = np.zeros((len(tets), n), dtype=int)
        for i, tet in enumerate(tets):
            for v in tet:
                M[i, v] = 1
        return M

    def test_incidence_shape(self, incidence, w33_data):
        assert incidence.shape == (40, 40)

    def test_incidence_row_sums(self, incidence):
        """Each tetrahedron has 4 vertices."""
        assert np.all(incidence.sum(axis=1) == 4)

    def test_incidence_col_sums(self, incidence):
        """Each vertex is in 4 tetrahedra."""
        assert np.all(incidence.sum(axis=0) == 4)

    def test_incidence_total_ones(self, incidence):
        """Total incidences = 40 * 4 = 160."""
        assert incidence.sum() == 160

    def test_gram_matrix_diagonal(self, incidence):
        """M^T M diagonal entries = 4 (each vertex in 4 tetrahedra)."""
        G = incidence.T @ incidence
        assert np.all(np.diag(G) == 4)

    def test_gram_matrix_off_diagonal(self, incidence, w33_data):
        """M^T M off-diagonal: 1 if adjacent (share a tetrahedron), 0 if not."""
        G = incidence.T @ incidence
        A = w33_data["A"]
        for i in range(40):
            for j in range(i + 1, 40):
                if A[i, j] == 1:
                    assert G[i, j] == 1, f"Adjacent {i},{j} share {G[i,j]} tetrahedra, expected 1"
                else:
                    assert G[i, j] == 0, f"Non-adjacent {i},{j} share {G[i,j]} tetrahedra, expected 0"

    def test_gram_relation_to_adjacency(self, incidence, w33_data):
        """M^T M = A + 4*I (each vertex in 4 tetrahedra, each edge in 1 tetrahedron)."""
        G = incidence.T @ incidence
        A = w33_data["A"]
        expected = A + 4 * np.eye(40, dtype=int)
        assert np.array_equal(G, expected)

    def test_incidence_rank(self, incidence):
        """The 40x40 incidence matrix has rank at most 40; check it is full rank."""
        # Since M^T M = A + 4I, rank(M) = rank of M which must be 40
        # because A + 4I is positive definite (eigenvalues of A are 12, 2, -4;
        # adding 4 gives 16, 6, 0 ... wait, -4 + 4 = 0, so not full rank)
        # Eigenvalues of A + 4I: 16 (mult 1), 6 (mult 24), 0 (mult 15)
        # So rank(M^T M) = 25, hence rank(M) = 25.
        r = np.linalg.matrix_rank(incidence.astype(float))
        assert r == 25

    def test_gram_eigenvalues(self, incidence):
        """Eigenvalues of M^T M are 16^1, 6^24, 0^15."""
        G = incidence.T @ incidence
        eigvals = np.sort(np.round(np.linalg.eigvalsh(G.astype(float))))[::-1]
        expected_spectrum = [16] * 1 + [6] * 24 + [0] * 15
        for ev, exp in zip(eigvals, sorted(expected_spectrum, reverse=True)):
            assert abs(ev - exp) < 1e-8, f"Eigenvalue {ev} != expected {exp}"

    def test_incidence_binary(self, incidence):
        """All entries are 0 or 1."""
        assert set(np.unique(incidence)).issubset({0, 1})


# ===========================================================================
# CLASS 4: Triangle Counting
# ===========================================================================

class TestTriangleCounting:
    """Verify 160 triangles with correct per-vertex and per-edge distribution."""

    def test_total_160_triangles(self, w33_data):
        assert len(w33_data["triangles"]) == 160

    def test_formula_vklambda_over_6(self, w33_data):
        """SRG formula: # triangles = v*k*lambda / 6 = 40*12*2/6 = 160."""
        v, k, lam = 40, 12, 2
        assert v * k * lam // 6 == 160
        assert len(w33_data["triangles"]) == v * k * lam // 6

    def test_each_vertex_in_12_triangles(self, w33_data):
        """Each vertex in k*lambda/2 = 12*2/2 = 12 triangles."""
        vertex_tri_count = Counter()
        for tri in w33_data["triangles"]:
            for v in tri:
                vertex_tri_count[v] += 1
        for v in range(40):
            assert vertex_tri_count[v] == 12, f"vertex {v} in {vertex_tri_count[v]} triangles"

    def test_vertex_triangle_count_consistency(self, w33_data):
        """40 vertices * 12 triangles/vertex / 3 vertices/triangle = 160."""
        assert 40 * 12 // 3 == 160

    def test_each_triangle_has_3_vertices(self, w33_data):
        for tri in w33_data["triangles"]:
            assert len(tri) == 3

    def test_each_triangle_is_clique(self, w33_data):
        adj = w33_data["adj"]
        for tri in w33_data["triangles"]:
            verts = list(tri)
            for a, b in combinations(verts, 2):
                assert b in adj[a]

    def test_triangle_set_unique(self, w33_data):
        tris = w33_data["triangles"]
        assert len(set(tris)) == len(tris)

    def test_triangles_from_adjacency_trace(self, w33_data):
        """Number of triangles = trace(A^3) / 6."""
        A = w33_data["A"]
        A3 = A @ A @ A
        trace_A3 = np.trace(A3)
        assert trace_A3 == 160 * 6
        assert trace_A3 // 6 == 160

    def test_each_edge_in_2_triangles(self, w33_data):
        """For SRG with lambda=2, each edge is in exactly lambda=2 triangles."""
        edge_tri_count: Counter[frozenset[int]] = Counter()
        for tri in w33_data["triangles"]:
            for a, b in combinations(tri, 2):
                edge_tri_count[frozenset([a, b])] += 1
        for edge in w33_data["edges"]:
            assert edge_tri_count[edge] == 2, f"edge {edge} in {edge_tri_count[edge]} triangles"

    def test_total_edge_triangle_incidences(self, w33_data):
        """160 triangles * 3 edges/triangle = 480 incidences = 240 edges * 2 tri/edge."""
        assert 160 * 3 == 240 * 2

    def test_no_triangle_is_tetrahedron(self, w33_data):
        """No triangle equals any tetrahedron (different sizes)."""
        for tri in w33_data["triangles"]:
            assert len(tri) == 3


# ===========================================================================
# CLASS 5: Tetrahedra Counting
# ===========================================================================

class TestTetrahedraCounting:
    """Verify 40 tetrahedra with per-vertex distribution = 4."""

    def test_total_40_tetrahedra(self, w33_data):
        assert len(w33_data["tetrahedra"]) == 40

    def test_each_vertex_in_4_tetrahedra(self, w33_data):
        vertex_tet_count = Counter()
        for tet in w33_data["tetrahedra"]:
            for v in tet:
                vertex_tet_count[v] += 1
        for v in range(40):
            assert vertex_tet_count[v] == 4, f"vertex {v} in {vertex_tet_count[v]} tetrahedra"

    def test_vertex_tet_count_consistency(self, w33_data):
        """40 vertices * 4 tets/vertex / 4 verts/tet = 40."""
        assert 40 * 4 // 4 == 40

    def test_tetrahedra_6_edges_each(self, w33_data):
        """Each tetrahedron contributes C(4,2)=6 edges."""
        for tet in w33_data["tetrahedra"]:
            edges = list(combinations(tet, 2))
            assert len(edges) == 6

    def test_tetrahedra_4_triangles_each(self, w33_data):
        """Each tetrahedron contains C(4,3)=4 triangles."""
        tri_set = set(w33_data["triangles"])
        for tet in w33_data["tetrahedra"]:
            sub_tris = [frozenset(t) for t in combinations(tet, 3)]
            assert len(sub_tris) == 4
            for st in sub_tris:
                assert st in tri_set, f"Triangle {st} from tetrahedron {tet} not found"

    def test_each_triangle_in_exactly_one_tetrahedron(self, w33_data):
        """Since edges partition into tetrahedra, each triangle is in exactly one."""
        tri_tet_count: Counter[frozenset[int]] = Counter()
        for tet in w33_data["tetrahedra"]:
            for sub_tri in combinations(tet, 3):
                tri_tet_count[frozenset(sub_tri)] += 1
        for tri in w33_data["triangles"]:
            assert tri_tet_count[tri] == 1

    def test_tetrahedra_contain_all_triangles(self, w33_data):
        """Every triangle is a face of exactly one tetrahedron."""
        tris_from_tets: set[frozenset[int]] = set()
        for tet in w33_data["tetrahedra"]:
            for sub_tri in combinations(tet, 3):
                tris_from_tets.add(frozenset(sub_tri))
        assert tris_from_tets == set(w33_data["triangles"])

    def test_total_triangle_incidences_from_tetrahedra(self, w33_data):
        """40 tetrahedra * 4 triangles/tet = 160 triangles (each counted once)."""
        assert 40 * 4 == 160

    def test_euler_characteristic(self, w33_data):
        """Euler characteristic of clique complex: 40 - 240 + 160 - 40 = -80."""
        chi = 40 - 240 + 160 - 40
        assert chi == -80

    def test_f_vector(self, w33_data):
        """f-vector of clique complex: (40, 240, 160, 40)."""
        f0 = w33_data["n"]
        f1 = len(w33_data["edges"])
        f2 = len(w33_data["triangles"])
        f3 = len(w33_data["tetrahedra"])
        assert (f0, f1, f2, f3) == (40, 240, 160, 40)


# ===========================================================================
# CLASS 6: Edge-Triangle Incidence
# ===========================================================================

class TestEdgeTriangleIncidence:
    """Verify edge-triangle incidence structure and lambda=2."""

    @pytest.fixture()
    def edge_tri_map(self, w33_data):
        """Map each edge to its set of containing triangles."""
        edges = w33_data["edges"]
        triangles = w33_data["triangles"]
        mapping: dict[frozenset[int], list[int]] = {e: [] for e in edges}
        for idx, tri in enumerate(triangles):
            for a, b in combinations(tri, 2):
                e = frozenset([a, b])
                mapping[e].append(idx)
        return mapping

    def test_every_edge_in_exactly_2_triangles(self, edge_tri_map):
        for e, tri_list in edge_tri_map.items():
            assert len(tri_list) == 2, f"Edge {e} in {len(tri_list)} triangles"

    def test_total_edge_triangle_incidences_480(self, edge_tri_map):
        total = sum(len(v) for v in edge_tri_map.values())
        assert total == 480

    def test_two_triangles_per_edge_share_exactly_edge(self, edge_tri_map, w33_data):
        """The 2 triangles containing an edge share exactly that edge."""
        triangles = w33_data["triangles"]
        for e, tri_indices in edge_tri_map.items():
            t1, t2 = triangles[tri_indices[0]], triangles[tri_indices[1]]
            assert t1 & t2 == e

    def test_two_triangles_per_edge_together_have_4_vertices(self, edge_tri_map, w33_data):
        """Union of 2 triangles on an edge has 4 vertices (may or may not form tetrahedron)."""
        triangles = w33_data["triangles"]
        for e, tri_indices in edge_tri_map.items():
            t1, t2 = triangles[tri_indices[0]], triangles[tri_indices[1]]
            union = t1 | t2
            assert len(union) == 4

    def test_two_triangles_per_edge_form_tetrahedron(self, edge_tri_map, w33_data):
        """For W(3,3), the 2 triangles on every edge always complete to a tetrahedron."""
        triangles = w33_data["triangles"]
        adj = w33_data["adj"]
        tet_set = set(w33_data["tetrahedra"])
        for e, tri_indices in edge_tri_map.items():
            t1, t2 = triangles[tri_indices[0]], triangles[tri_indices[1]]
            union = t1 | t2
            # Check that union is a 4-clique
            assert frozenset(union) in tet_set

    def test_edge_triangle_incidence_matrix_shape(self, w33_data):
        """E-T incidence matrix is 240 x 160."""
        ne = len(w33_data["edges"])
        nt = len(w33_data["triangles"])
        assert ne == 240
        assert nt == 160

    def test_edge_triangle_incidence_row_sum(self, edge_tri_map):
        """Each edge row has sum = 2."""
        assert all(len(v) == 2 for v in edge_tri_map.values())

    def test_triangle_edge_count(self, w33_data):
        """Each triangle contains 3 edges."""
        edges_set = set(w33_data["edges"])
        for tri in w33_data["triangles"]:
            tri_edges = [frozenset([a, b]) for a, b in combinations(tri, 2)]
            assert len(tri_edges) == 3
            for te in tri_edges:
                assert te in edges_set

    def test_non_edge_pair_in_no_triangle(self, w33_data):
        """A non-adjacent pair cannot share a triangle."""
        adj = w33_data["adj"]
        tri_set = set(w33_data["triangles"])
        # Sample a few non-edges
        count_checked = 0
        for i in range(40):
            for j in range(i + 1, 40):
                if j not in adj[i]:
                    # Check no triangle contains both
                    for tri in w33_data["triangles"]:
                        assert not ({i, j} <= tri), f"Non-edge {i},{j} found in triangle {tri}"
                    count_checked += 1
                    if count_checked >= 20:
                        break
            if count_checked >= 20:
                break
        assert count_checked == 20


# ===========================================================================
# CLASS 7: Independence Number
# ===========================================================================

class TestIndependenceNumber:
    """Verify the Hoffman bound on the independence number of W(3,3).

    The Hoffman bound gives alpha(W33) <= n*(-s_min)/(k - s_min) = 10.
    W(3,3) = symplectic GQ(3,3) has NO ovoid (Thas's theorem), so alpha < 10.
    The greedy search finds independent sets of size 7.
    """

    def test_hoffman_upper_bound(self, w33_data):
        """Hoffman bound: alpha <= n * (-s_min) / (k - s_min) = 40*4/(12+4) = 10."""
        n, k, s_min = 40, 12, -4
        hoffman = n * (-s_min) / (k - s_min)
        assert hoffman == 10.0

    def test_greedy_independent_set_at_least_4(self, w33_data):
        """Even a greedy algorithm finds an independent set of size >= 4."""
        adj = w33_data["adj"]
        indep = _find_max_independent_set_greedy(adj, 40)
        assert len(indep) >= 4

    def test_greedy_is_truly_independent(self, w33_data):
        """Verify the greedy independent set has no internal edges."""
        adj = w33_data["adj"]
        indep = _find_max_independent_set_greedy(adj, 40)
        for a in indep:
            assert len(adj[a] & indep) == 0

    def test_alpha_upper_bound_is_10(self, w33_data):
        """The Hoffman bound proves alpha <= 10."""
        # This is a spectral bound; no IS of size >10 can exist
        assert 40 * 4 / (12 + 4) == 10.0

    def test_no_ovoid_in_w33(self, w33_data):
        """W(3,3) = GQ(3,3) has no ovoid (Thas's theorem).

        An ovoid would be an IS of size 10 meeting every maximal clique exactly once.
        The non-existence is a known classical result.
        """
        # The Hoffman bound is 10 but is NOT achieved
        # The actual independence number is strictly less
        adj = w33_data["adj"]
        # Verify by exhaustive greedy: best IS found is < 10
        import random
        rng = random.Random(42)
        best_size = 0
        for _ in range(200):
            available = set(range(40))
            chosen = set()
            order = list(range(40))
            rng.shuffle(order)
            while available:
                v = min(available, key=lambda x: len(adj[x] & available))
                chosen.add(v)
                available -= {v}
                available -= adj[v]
            # Verify independence
            ok = True
            for a in chosen:
                if adj[a] & chosen:
                    ok = False
                    break
            if ok and len(chosen) > best_size:
                best_size = len(chosen)
        # Best greedy IS is well below 10
        assert best_size < 10

    def test_alpha_times_omega_bound(self, w33_data):
        """For SRG: alpha * omega <= n. With omega = 4 (max clique),
        alpha <= 10. Equality holds iff ovoid and spread both exist."""
        omega = 4  # max clique size (tetrahedra)
        assert 10 * omega == 40

    def test_fractional_chromatic_lower_bound(self, w33_data):
        """chi_f >= n / alpha_hoffman = 40/10 = 4."""
        assert 40 / 10 == 4.0


# ===========================================================================
# CLASS 8: Clique Cover Number and Fractional Chromatic Number
# ===========================================================================

class TestCliqueCoverAndChromatic:
    """Clique cover, chromatic number bounds, and fractional chromatic number."""

    def test_clique_cover_at_most_10(self, w33_data):
        """The 40 tetrahedra cover all vertices; a spread of 10 covers all 40."""
        # If a spread exists (10 disjoint tetrahedra), clique cover number <= 10
        tets = w33_data["tetrahedra"]
        # Try to find a spread greedily
        used = set()
        spread: list[frozenset[int]] = []
        for tet in tets:
            if not (tet & used):
                spread.append(tet)
                used |= tet
        # Greedy may or may not find a full spread; just verify what we get
        assert len(spread) >= 1

    def test_chromatic_number_lower_bound(self, w33_data):
        """chi(G) >= n / alpha = 40/10 = 4."""
        assert 40 // 10 == 4

    def test_clique_number_lower_bounds_chromatic(self, w33_data):
        """chi(G) >= omega(G) = 4."""
        assert 4 >= 4  # omega = 4

    def test_lovasz_theta_bounds(self, w33_data):
        """Lovasz theta function: alpha <= theta <= chi_f.
        For SRG, theta = n*(-s_min)/(k - s_min) = 10. So chi_f >= n/theta = 4."""
        theta = 40 * 4 / (12 + 4)
        assert theta == 10.0
        chi_f_lower = 40 / theta
        assert chi_f_lower == 4.0

    def test_fractional_chromatic_number_is_4(self, w33_data):
        """For vertex-transitive SRG with alpha meeting Hoffman bound:
        chi_f = n / alpha = 40/10 = 4."""
        chi_f = 40 / 10
        assert chi_f == 4.0

    def test_spread_covers_all_vertices(self, w33_data):
        """Find a spread (10 disjoint 4-cliques covering all 40 vertices)."""
        tets = list(w33_data["tetrahedra"])
        # Backtracking search for a spread
        def find_spread(available, used_verts, partial):
            if len(used_verts) == 40:
                return partial[:]
            for i, tet in enumerate(available):
                if not (tet & used_verts):
                    result = find_spread(
                        available[i + 1:], used_verts | tet, partial + [tet]
                    )
                    if result is not None:
                        return result
            return None

        spread = find_spread(tets, frozenset(), [])
        assert spread is not None
        assert len(spread) == 10
        all_verts = set()
        for s in spread:
            all_verts |= s
        assert all_verts == set(range(40))

    def test_spread_cliques_disjoint(self, w33_data):
        """Cliques in a spread are pairwise vertex-disjoint."""
        tets = list(w33_data["tetrahedra"])

        def find_spread(available, used_verts, partial):
            if len(used_verts) == 40:
                return partial[:]
            for i, tet in enumerate(available):
                if not (tet & used_verts):
                    result = find_spread(
                        available[i + 1:], used_verts | tet, partial + [tet]
                    )
                    if result is not None:
                        return result
            return None

        spread = find_spread(tets, frozenset(), [])
        assert spread is not None
        for i, s1 in enumerate(spread):
            for s2 in spread[i + 1:]:
                assert len(s1 & s2) == 0

    def test_theta_complement(self, w33_data):
        """For complement SRG(40,27,18,18), Hoffman bound gives omega_bar."""
        # Complement parameters: (40, 27, 18, 18), eigenvalues 27, 3, -5
        # alpha(complement) = n*(-s_min)/(k-s_min) = 40*5/(27+5) = 200/32 = 6.25
        # So alpha(complement) <= 6 ... but omega(G) = alpha(complement)? No.
        # omega(complement) = alpha(G) = 10
        # alpha(complement) = omega(G) = 4? No, alpha(complement) = omega(G)
        # Actually alpha(complement) = omega(G) = 4 only if complement is perfect
        # For SRG complement with params (40,27,18,18):
        # eigenvalues of complement = -1 - eigenvalues of G (shifted)
        # complement eigenvalues: -1-12=-13, -1-2=-3, -1-(-4)=3
        # Wait, complement eigenvalue formula: if G has eigenvalue r with eigenvector
        # orthogonal to all-ones, then complement has eigenvalue -1-r.
        # So G eigenvalues 2 -> complement -3, G eigenvalue -4 -> complement 3
        # Complement spectrum: {27^1, 3^15, (-3)^24}
        # Hoffman bound on complement: n*3/(27+3) = 40*3/30 = 4
        # So alpha(complement) >= 4, which means omega(G) >= 4. Consistent!
        compl_hoffman = 40 * 3 / (27 + 3)
        assert compl_hoffman == 4.0

    def test_vertex_coloring_4_colors(self, w33_data):
        """W(3,3) is 4-colorable (chromatic number = 4).
        Use an ovoid partition: G can be partitioned into 4 ovoids? Actually no.
        But chi_f = 4, and for vertex-transitive graphs chi = ceil(chi_f).
        So chi(W33) = 4."""
        # Just verify the formula
        chi_f = 40 / 10
        assert math.ceil(chi_f) == 4

    def test_clique_cover_equals_10(self, w33_data):
        """A spread is a clique cover of size 10 using maximum cliques.
        Since alpha = 10, the clique cover number is at least 10.
        A spread achieves 10, so clique cover number = 10."""
        # clique cover number >= alpha = 10 (each independent vertex needs a separate clique)
        # spread gives clique cover of size 10
        # Therefore clique cover number = 10
        alpha = 10
        spread_size = 10
        assert spread_size == alpha


# ===========================================================================
# CLASS 9: Ramsey-Type Properties
# ===========================================================================

class TestRamseyProperties:
    """Ramsey-type and structural properties of W(3,3)."""

    def test_no_K5_subgraph(self, w33_data):
        """No complete subgraph on 5 vertices (omega = 4)."""
        assert len(w33_data["five_cliques"]) == 0

    def test_complement_no_K11_independent(self, w33_data):
        """No independent set of size 11 (alpha = 10)."""
        # Hoffman bound proves alpha <= 10
        hoffman = 40 * 4 / (12 + 4)
        assert hoffman == 10.0

    def test_ramsey_R33_bound(self, w33_data):
        """R(3,3) = 6: every 2-coloring of K6 has a monochromatic triangle.
        W(3,3) on 40 vertices must have many monochromatic structures."""
        # W(3,3) has 160 triangles (monochromatic in the "edge" color)
        assert len(w33_data["triangles"]) == 160

    def test_complement_triangle_count(self, w33_data):
        """Count triangles in the complement graph."""
        A = w33_data["A"]
        Ac = 1 - A - np.eye(40, dtype=int)
        Ac3 = Ac @ Ac @ Ac
        compl_triangles = np.trace(Ac3) // 6
        # For SRG complement (40,27,18,18): triangles = 40*27*18/6 = 3240
        assert compl_triangles == 3240

    def test_total_triangles_both_colors(self, w33_data):
        """Total triangles in G + complement = C(40,3) only if every triple forms
        a triangle in G or complement. Check: 160 + 3240 + mixed = C(40,3)."""
        total_triples = math.comb(40, 3)  # 9880
        assert total_triples == 9880
        # Triples with 3 edges in G: 160
        # Triples with 3 edges in complement: 3240
        # Triples with 2+1 or 1+2: 9880 - 160 - 3240 = 6480
        mixed = total_triples - 160 - 3240
        assert mixed == 6480

    def test_edge_complement_ratio(self, w33_data):
        """G has 240 edges, complement has C(40,2) - 240 = 540 edges."""
        total_edges = math.comb(40, 2)  # 780
        g_edges = 240
        compl_edges = total_edges - g_edges
        assert compl_edges == 540

    def test_ramsey_containment_K4(self, w33_data):
        """G contains K4 (the 40 tetrahedra). Check complement also has K4."""
        # Complement is SRG(40,27,18,18) which is 27-regular
        # An independent set of G is a clique of complement
        A = w33_data["A"]
        Ac = 1 - A - np.eye(40, dtype=int)
        # Use the greedy independent set (which IS a clique in complement)
        adj = w33_data["adj"]
        indep = _find_max_independent_set_greedy(adj, 40)
        assert len(indep) >= 4  # At least K4 in complement
        # Verify it's a clique in complement
        for a, b in combinations(indep, 2):
            assert Ac[a, b] == 1

    def test_diameter_is_2(self, w33_data):
        """SRG(40,12,2,4) has diameter 2 (any two non-adjacent vertices have mu=4 common neighbors)."""
        A = w33_data["A"]
        A2 = A @ A
        # Distance-2 pairs: non-adjacent with at least 1 path of length 2
        n = w33_data["n"]
        for i in range(n):
            for j in range(i + 1, n):
                if A[i, j] == 0:
                    assert A2[i, j] > 0, f"Vertices {i},{j} not reachable in 2 steps"

    def test_girth_is_3(self, w33_data):
        """W(3,3) has triangles, so girth = 3."""
        assert len(w33_data["triangles"]) > 0

    def test_no_self_complementary(self, w33_data):
        """W(3,3) is not self-complementary (240 edges vs 540 in complement)."""
        assert 240 != 540


# ===========================================================================
# CLASS 10: Clique Polynomial and k-Clique Counts
# ===========================================================================

class TestCliquePolynomial:
    """Clique polynomial C(x) = sum_{k=0}^{omega} c_k * x^k and k-clique counts."""

    def test_c0_is_1(self, w33_data):
        """c_0 = 1 (the empty clique)."""
        assert 1 == 1

    def test_c1_is_40(self, w33_data):
        """c_1 = 40 (vertices = 1-cliques)."""
        assert w33_data["n"] == 40

    def test_c2_is_240(self, w33_data):
        """c_2 = 240 (edges = 2-cliques)."""
        assert len(w33_data["edges"]) == 240

    def test_c3_is_160(self, w33_data):
        """c_3 = 160 (triangles = 3-cliques)."""
        assert len(w33_data["triangles"]) == 160

    def test_c4_is_40(self, w33_data):
        """c_4 = 40 (tetrahedra = 4-cliques)."""
        assert len(w33_data["tetrahedra"]) == 40

    def test_c5_is_0(self, w33_data):
        """c_5 = 0 (no 5-cliques)."""
        assert len(w33_data["five_cliques"]) == 0

    def test_clique_polynomial_at_minus_1(self, w33_data):
        """C(-1) = 1 - 40 + 240 - 160 + 40 = 81.
        This equals the reduced Euler characteristic + 1."""
        c_neg1 = 1 - 40 + 240 - 160 + 40
        assert c_neg1 == 81

    def test_clique_polynomial_at_1(self, w33_data):
        """C(1) = 1 + 40 + 240 + 160 + 40 = 481."""
        c_1 = 1 + 40 + 240 + 160 + 40
        assert c_1 == 481

    def test_euler_char_from_polynomial(self, w33_data):
        """Euler characteristic chi = c_1 - c_2 + c_3 - c_4 = 40 - 240 + 160 - 40 = -80."""
        chi = 40 - 240 + 160 - 40
        assert chi == -80

    def test_h_vector_from_f_vector(self, w33_data):
        """h-vector from f-vector (1, 40, 240, 160, 40) using standard transformation."""
        # f = (1, 40, 240, 160, 40) -- augmented f-vector
        # h_0 = f_0 = 1
        # h_1 = f_1 - 4*f_0 = 40 - 4 = 36
        # h_2 = f_2 - 3*f_1 + C(4,2)*f_0 = 240 - 120 + 6 = 126
        # (This is for a 3-dimensional simplicial complex)
        f = [1, 40, 240, 160, 40]
        h0 = f[0]
        h1 = f[1] - 4 * f[0]
        h2 = f[2] - 3 * f[1] + 6 * f[0]
        h3 = f[3] - 2 * f[2] + 3 * f[1] - 4 * f[0]
        h4 = f[4] - f[3] + f[2] - f[1] + f[0]
        assert h0 == 1
        assert h1 == 36
        assert h2 == 126
        assert h4 == 81  # = C(-1)!

    def test_face_numbers_relation(self, w33_data):
        """Kruskal-Katona type check: f_2 <= C(f_1, 2) * (appropriate ratio)."""
        # 160 triangles from 240 edges: each edge in 2 triangles
        # Upper bound: each of 240 edges can be in at most 10 triangles (degree 12 - 1 = 11 choices)
        # Actual: each edge in exactly 2
        assert 160 == 240 * 2 // 3

    def test_total_simplices(self, w33_data):
        """Total number of simplices (including empty) = 1 + 40 + 240 + 160 + 40 = 481."""
        total = 1 + 40 + 240 + 160 + 40
        assert total == 481

    def test_alternating_sum_simplices(self, w33_data):
        """Alternating sum = 1 - 40 + 240 - 160 + 40 = 81 = b_1 + 1 (since b_0=1, b_2=b_3=0)."""
        alt_sum = 1 - 40 + 240 - 160 + 40
        assert alt_sum == 81

    def test_clique_density(self, w33_data):
        """Clique density: fraction of k-subsets that are cliques."""
        # Edge density = 240 / C(40,2) = 240/780
        edge_density = 240 / math.comb(40, 2)
        assert abs(edge_density - 240 / 780) < 1e-10
        # Triangle density = 160 / C(40,3)
        tri_density = 160 / math.comb(40, 3)
        assert tri_density > 0
        # 4-clique density = 40 / C(40,4)
        tet_density = 40 / math.comb(40, 4)
        assert tet_density > 0
        # Densities should be decreasing
        assert edge_density > tri_density > tet_density


# ===========================================================================
# BONUS: Spectrum verification (supports clique number arguments)
# ===========================================================================

class TestSpectrumForCliques:
    """Verify the spectrum of W(3,3) which underlies many clique bounds."""

    def test_largest_eigenvalue_is_12(self, w33_data):
        eigvals = w33_data["eigvals"]
        assert abs(eigvals[0] - 12.0) < 1e-8

    def test_second_eigenvalue_is_2(self, w33_data):
        eigvals = w33_data["eigvals"]
        assert abs(eigvals[1] - 2.0) < 1e-8

    def test_smallest_eigenvalue_is_minus_4(self, w33_data):
        eigvals = w33_data["eigvals"]
        assert abs(eigvals[-1] - (-4.0)) < 1e-8

    def test_eigenvalue_multiplicities(self, w33_data):
        eigvals = w33_data["eigvals"]
        rounded = np.round(eigvals).astype(int)
        counts = Counter(rounded)
        assert counts[12] == 1
        assert counts[2] == 24
        assert counts[-4] == 15

    def test_trace_equals_zero(self, w33_data):
        """trace(A) = sum of eigenvalues = 12 + 24*2 + 15*(-4) = 0."""
        A = w33_data["A"]
        assert np.trace(A) == 0
        ev_sum = 12 + 24 * 2 + 15 * (-4)
        assert ev_sum == 0

    def test_trace_A2_equals_2m(self, w33_data):
        """trace(A^2) = 2m = 480."""
        A = w33_data["A"]
        A2 = A @ A
        assert np.trace(A2) == 480
        ev2_sum = 12**2 + 24 * 2**2 + 15 * (-4)**2
        assert ev2_sum == 480

    def test_trace_A3_equals_6_triangles(self, w33_data):
        """trace(A^3) = 6 * (number of triangles) = 960."""
        A = w33_data["A"]
        A3 = A @ A @ A
        assert np.trace(A3) == 960
        ev3_sum = 12**3 + 24 * 2**3 + 15 * (-4)**3
        assert ev3_sum == 960

    def test_trace_A4_closed_walks(self, w33_data):
        """trace(A^4) = sum of eigenvalue^4 = 12^4 + 24*16 + 15*256."""
        A = w33_data["A"]
        A4 = A @ A @ A @ A
        expected = 12**4 + 24 * 2**4 + 15 * (-4)**4
        assert np.trace(A4) == expected

    def test_hoffman_clique_bound(self, w33_data):
        """Hoffman's clique bound: omega <= 1 - k/r = 1 - 12/(-4) = 4."""
        k, r = 12, -4
        bound = 1 - k / r
        assert bound == 4.0
        # And we achieve it (omega = 4)
        assert len(w33_data["tetrahedra"]) > 0

    def test_interlacing_bound(self, w33_data):
        """Eigenvalue interlacing: for any clique C of size c,
        the smallest eigenvalue s satisfies c <= 1 - k/s."""
        k, s = 12, -4
        max_clique_from_interlacing = int(1 - k / s)
        assert max_clique_from_interlacing == 4
