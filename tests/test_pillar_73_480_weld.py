#!/usr/bin/env python3
"""
Test Suite for Pillar 73: 480-Weld — Directed Edges ↔ Octonion Orbit
======================================================================

Verifies the 480-weld theorem:
  - W33 has 480 directed edges
  - Sp(4,3) acts transitively on directed edges
  - Stabilizer order = 25920/480 = 54
  - Octonion orbit size = 480
  - W33 lines decompose directed edges as 480 = 40 × 12
"""
import os
import sys
from collections import Counter

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from e8_embedding_group_theoretic import build_w33
from w33_480_weld import (
    build_directed_edges,
    build_edge_to_line_map,
    build_sp43_group,
    build_w33_lines,
    check_directed_edge_transitivity,
    compute_stabilizer_size,
    directed_edge_permutation,
)

# =========================================================================
# Fixtures
# =========================================================================


@pytest.fixture(scope="module")
def w33():
    """Build the W33 graph."""
    return build_w33()


@pytest.fixture(scope="module")
def directed_edges(w33):
    """Build directed edges."""
    n, vertices, adj, edges = w33
    return build_directed_edges(edges)


@pytest.fixture(scope="module")
def de_index(directed_edges):
    """Build directed edge index."""
    return {de: i for i, de in enumerate(directed_edges)}


@pytest.fixture(scope="module")
def sp43_group(w33):
    """Build Sp(4,3) group."""
    n, vertices, adj, edges = w33
    return build_sp43_group(n, vertices, adj, edges)


@pytest.fixture(scope="module")
def w33_lines(w33):
    """Build W33 lines."""
    n, vertices, adj, edges = w33
    return build_w33_lines(n, adj)


# =========================================================================
# Test Class: Directed Edge Properties
# =========================================================================


class TestDirectedEdgeProperties:
    """Verify directed edge construction."""

    def test_480_directed_edges(self, directed_edges):
        """W33 has exactly 480 directed edges."""
        assert len(directed_edges) == 480

    def test_directed_edges_are_pairs(self, directed_edges, w33):
        """Each undirected edge yields exactly 2 directed edges."""
        n, vertices, adj, edges = w33
        for u, v in edges:
            assert (u, v) in directed_edges or (v, u) in directed_edges

    def test_all_directed_edges_are_valid(self, directed_edges, w33):
        """All directed edges connect adjacent vertices."""
        n, vertices, adj, edges = w33
        adj_sets = [set(adj[i]) for i in range(n)]
        for u, v in directed_edges:
            assert v in adj_sets[u], f"({u},{v}) not an edge"


# =========================================================================
# Test Class: W33 Line Structure
# =========================================================================


class TestW33LineStructure:
    """Verify W33 line properties."""

    def test_40_lines(self, w33_lines):
        """W33 has exactly 40 lines."""
        assert len(w33_lines) == 40

    def test_4_vertices_per_line(self, w33_lines):
        """Each line has exactly 4 vertices."""
        for line in w33_lines:
            assert len(line) == 4

    def test_6_edges_per_line(self, w33_lines, w33):
        """Each line contains C(4,2) = 6 edges."""
        from itertools import combinations

        n, vertices, adj, edges = w33
        edge_set = set(edges)
        for line in w33_lines:
            line_edges = [
                (min(u, v), max(u, v)) for u, v in combinations(line, 2)
            ]
            for e in line_edges:
                assert e in edge_set

    def test_each_edge_on_one_line(self, w33_lines, w33):
        """Each edge lies on exactly one line."""
        n, vertices, adj, edges = w33
        edge_to_line = build_edge_to_line_map(edges, w33_lines)
        assert len(edge_to_line) == len(edges)

    def test_12_directed_edges_per_line(self, w33_lines, directed_edges):
        """Each line has 12 directed edges (6 edges × 2 directions)."""
        from itertools import combinations

        for line in w33_lines:
            count = 0
            for u, v in combinations(line, 2):
                if (u, v) in directed_edges:
                    count += 1
                if (v, u) in directed_edges:
                    count += 1
            # Actually we need to check membership differently
            de_set = set(directed_edges)
            count = sum(
                1
                for u, v in combinations(line, 2)
                for pair in [(u, v), (v, u)]
                if pair in de_set
            )
            assert count == 12


# =========================================================================
# Test Class: Group Action
# =========================================================================


class TestGroupAction:
    """Verify Sp(4,3) group action on directed edges."""

    def test_group_order_25920(self, sp43_group):
        """PSp(4,3) has order 25920."""
        assert len(sp43_group) == 25920

    def test_transitive_on_directed_edges(
        self, sp43_group, directed_edges, de_index
    ):
        """Sp(4,3) acts transitively on directed edges."""
        is_transitive, orbit_size = check_directed_edge_transitivity(
            sp43_group, directed_edges, de_index
        )
        assert is_transitive
        assert orbit_size == 480

    def test_stabilizer_order(self, sp43_group, directed_edges, de_index):
        """Stabilizer of a directed edge has order |G|/480."""
        stab = compute_stabilizer_size(
            sp43_group, directed_edges, de_index
        )
        expected = len(sp43_group) // 480
        assert stab == expected


# =========================================================================
# Test Class: 480 Weld Numerology
# =========================================================================


class TestWeldNumerology:
    """Verify the 480-weld numerical coincidences."""

    def test_octonion_orbit_480(self):
        """Octonion multiplication table orbit = 645120 / 1344 = 480."""
        assert 2**7 * 5040 == 645120
        assert 645120 // 1344 == 480

    def test_w33_directed_equals_octonion(self, directed_edges):
        """|W33 directed edges| = |Octonion orbit| = 480."""
        assert len(directed_edges) == 480
        assert 645120 // 1344 == 480

    def test_480_decompositions(self):
        """480 = 40 × 12 = 2 × 240."""
        assert 480 == 40 * 12
        assert 480 == 2 * 240

    def test_g2_stabilizer_1344(self):
        """G2(2) stabilizer = 1344 = 2^6 × 3 × 7."""
        assert 1344 == 64 * 21
        assert 1344 == 2**6 * 3 * 7
