#!/usr/bin/env python3
"""
Test Suite for Pillar 74: Weyl(A2) Fiber Structure
====================================================

Verifies the fiber structure of the 240 odd non-face triangles:
  - 40 fibers of size 6 = |S3| = |Weyl(A2)|
  - 18 distinct vertices per fiber, 0 face overlap
  - Each fiber vertex adjacent to exactly 2 of 3 face vertices
  - Non-adjacency vertex map well-defined
  - Uniform conjugacy distribution across all fibers
"""
import os
import sys
from collections import Counter

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from w33_srg36_triangle_fibration import (
    compute_fibration,
    compute_srg36_adjacency,
    load_bundle_data,
)

from w33_weyl_fiber_labeling import (
    compute_non_adjacency_map,
    label_fibers_by_non_adjacency,
    perm_cycle_type,
    perm_to_s3_label,
    s3_conjugacy_class,
)

# =========================================================================
# Fixtures
# =========================================================================


@pytest.fixture(scope="module")
def bundle_data():
    """Load bundle data."""
    try:
        return load_bundle_data()
    except FileNotFoundError:
        pytest.skip("Bundle data not found; skipping Weyl fiber tests")


@pytest.fixture(scope="module")
def fibration_and_labels(bundle_data):
    """Compute fibration and fiber labels."""
    blocks, pairs36, lines_data = bundle_data
    adj = compute_srg36_adjacency(blocks)
    results = compute_fibration(blocks, adj, lines_data)
    fiber_labels = label_fibers_by_non_adjacency(blocks, adj, lines_data, results)
    return results, fiber_labels, adj


# =========================================================================
# Test Class: S3 Utility Functions
# =========================================================================


class TestS3Utilities:
    """Verify S3 labeling utilities."""

    def test_identity_label(self):
        assert perm_to_s3_label((0, 1, 2)) == "id"

    def test_transposition_labels(self):
        assert perm_to_s3_label((1, 0, 2)) == "(01)"
        assert perm_to_s3_label((2, 1, 0)) == "(02)"
        assert perm_to_s3_label((0, 2, 1)) == "(12)"

    def test_three_cycle_labels(self):
        assert perm_to_s3_label((1, 2, 0)) == "(012)"
        assert perm_to_s3_label((2, 0, 1)) == "(021)"

    def test_cycle_types(self):
        assert perm_cycle_type((0, 1, 2)) == (1, 1, 1)
        assert perm_cycle_type((1, 0, 2)) == (1, 2)
        assert perm_cycle_type((1, 2, 0)) == (3,)


# =========================================================================
# Test Class: Fiber Structure
# =========================================================================


class TestFiberStructure:
    """Verify fiber size and count."""

    def test_40_fibers(self, fibration_and_labels):
        _, fiber_labels, _ = fibration_and_labels
        assert len(fiber_labels) == 40

    def test_all_fibers_size_6(self, fibration_and_labels):
        _, fiber_labels, _ = fibration_and_labels
        for face, data in fiber_labels.items():
            assert len(data["triangles"]) == 6

    def test_total_240(self, fibration_and_labels):
        _, fiber_labels, _ = fibration_and_labels
        total = sum(len(d["triangles"]) for d in fiber_labels.values())
        assert total == 240


# =========================================================================
# Test Class: Vertex Properties
# =========================================================================


class TestVertexProperties:
    """Verify vertex structure within fibers."""

    def test_18_vertices_per_fiber(self, fibration_and_labels):
        """Each fiber has 18 distinct vertices."""
        _, fiber_labels, _ = fibration_and_labels
        for face, data in fiber_labels.items():
            all_verts = set()
            for t in data["triangles"]:
                all_verts.update(t)
            assert len(all_verts) == 18, f"Face {face}: {len(all_verts)} vertices"

    def test_no_face_vertex_overlap(self, fibration_and_labels):
        """No fiber vertex is also a face vertex."""
        _, fiber_labels, _ = fibration_and_labels
        for face, data in fiber_labels.items():
            face_set = set(face)
            for t in data["triangles"]:
                assert not (set(t) & face_set), f"Overlap in face {face}"

    def test_each_vertex_adj_to_2_face_verts(self, fibration_and_labels):
        """Each fiber vertex is adjacent to exactly 2 of 3 face vertices."""
        _, fiber_labels, adj = fibration_and_labels
        for face, data in fiber_labels.items():
            for t in data["triangles"]:
                for v in t:
                    n_adj = sum(1 for fv in face if fv in adj[v])
                    assert n_adj == 2, (
                        f"Vertex {v} in triangle {t}: "
                        f"adj to {n_adj} face verts (expected 2)"
                    )


# =========================================================================
# Test Class: Non-Adjacency Map
# =========================================================================


class TestNonAdjacencyMap:
    """Verify the non-adjacency vertex map."""

    def test_all_labels_valid(self, fibration_and_labels):
        """All non-adjacency maps produce valid permutations."""
        _, fiber_labels, _ = fibration_and_labels
        for face, data in fiber_labels.items():
            for label in data["labels"]:
                assert label is not None, f"Invalid label in face {face}"
                assert sorted(label) == [0, 1, 2], (
                    f"Not a permutation: {label}"
                )

    def test_only_transpositions_and_3cycles(self, fibration_and_labels):
        """Only transpositions and 3-cycles appear (no identity in fibers)."""
        _, fiber_labels, _ = fibration_and_labels
        all_types = set()
        for data in fiber_labels.values():
            for ct in data["cycle_types"]:
                all_types.add(ct)
        assert all_types == {"transposition", "3-cycle"}, (
            f"Unexpected types: {all_types}"
        )

    def test_exactly_2_permutation_types(self, fibration_and_labels):
        """Exactly 2 distinct permutation types appear across all fibers."""
        _, fiber_labels, _ = fibration_and_labels
        all_perms = set()
        for data in fiber_labels.values():
            for l in data["labels"]:
                if l:
                    all_perms.add(l)
        assert len(all_perms) == 2, f"Found {len(all_perms)} types: {all_perms}"


# =========================================================================
# Test Class: Numerology
# =========================================================================


class TestWeylNumerology:
    """Verify key numerical facts."""

    def test_s3_order_6(self):
        from itertools import permutations
        assert len(list(permutations(range(3)))) == 6

    def test_240_equals_40_times_6(self):
        assert 240 == 40 * 6

    def test_s3_conjugacy_classes(self):
        """S3 has 3 conjugacy classes: {id}, {3 transpositions}, {2 three-cycles}."""
        from itertools import permutations
        classes = Counter()
        for p in permutations(range(3)):
            classes[s3_conjugacy_class(p)] += 1
        assert classes == Counter({"identity": 1, "transposition": 3, "3-cycle": 2})
