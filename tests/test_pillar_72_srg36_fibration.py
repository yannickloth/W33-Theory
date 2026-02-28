#!/usr/bin/env python3
"""
Test Suite for Pillar 72: SRG(36) Triangle Fibration — 240 = 40 × 6
=====================================================================

Verifies the complete SRG(36) triangle fibration theorem:
  - 1200 triangles in SRG(36)
  - 120 face blocks with holonomy 1
  - 240 odd non-face triangles
  - 40 special faces (one per W33 line)
  - Fiber size 6 (= |S3| = |Weyl(A2)|)
"""
import json
import os
import sys
from collections import Counter
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from w33_srg36_triangle_fibration import (
    compute_edge_orientations,
    compute_edge_to_third,
    compute_face_to_line,
    compute_fibration,
    compute_srg36_adjacency,
    enumerate_all_triangles,
    load_bundle_data,
)

# =========================================================================
# Fixtures
# =========================================================================


@pytest.fixture(scope="module")
def bundle_data():
    """Load the E6pair SRG triangle decomposition bundle."""
    try:
        return load_bundle_data()
    except FileNotFoundError:
        pytest.skip("Bundle data not found; skipping SRG36 fibration tests")


@pytest.fixture(scope="module")
def srg36_adj(bundle_data):
    """Build SRG(36) adjacency."""
    blocks, pairs36, lines_data = bundle_data
    return compute_srg36_adjacency(blocks)


@pytest.fixture(scope="module")
def fibration_results(bundle_data, srg36_adj):
    """Compute the full fibration."""
    blocks, pairs36, lines_data = bundle_data
    return compute_fibration(blocks, srg36_adj, lines_data)


# =========================================================================
# Test Class: SRG(36) Graph Properties
# =========================================================================


class TestSRG36GraphProperties:
    """Verify fundamental SRG(36,20,10,12) properties."""

    def test_36_vertices(self, bundle_data):
        """SRG(36) has exactly 36 vertices."""
        blocks, pairs36, lines_data = bundle_data
        assert len(pairs36) == 36

    def test_regular_degree_20(self, srg36_adj):
        """All vertices have degree 20."""
        degrees = [len(srg36_adj[v]) for v in range(36)]
        assert all(d == 20 for d in degrees), f"Degrees: {set(degrees)}"

    def test_lambda_parameter_10(self, srg36_adj):
        """Adjacent vertices have exactly 10 common neighbors (lambda=10)."""
        for i in range(36):
            for j in srg36_adj[i]:
                common = len(srg36_adj[i] & srg36_adj[j])
                assert common == 10, f"lambda({i},{j}) = {common}"

    def test_mu_parameter_12(self, srg36_adj):
        """Non-adjacent vertices have exactly 12 common neighbors (mu=12)."""
        for i in range(36):
            for j in range(36):
                if j not in srg36_adj[i] and i != j:
                    common = len(srg36_adj[i] & srg36_adj[j])
                    assert common == 12, f"mu({i},{j}) = {common}"

    def test_120_blocks_cover_all_edges(self, bundle_data, srg36_adj):
        """The 120 triangle blocks partition the 360 edges."""
        blocks, _, _ = bundle_data
        edge_set = set()
        for tri in blocks:
            a, b, c = tri
            for u, v in [(a, b), (a, c), (b, c)]:
                edge_set.add((min(u, v), max(u, v)))
        # SRG(36,20) has 36*20/2 = 360 edges
        assert len(edge_set) == 360


# =========================================================================
# Test Class: Triangle Count
# =========================================================================


class TestTriangleCount:
    """Verify triangle enumeration."""

    def test_1200_triangles(self, fibration_results):
        """SRG(36) has exactly 1200 triangles."""
        assert fibration_results["n_triangles"] == 1200

    def test_120_face_blocks(self, fibration_results):
        """There are exactly 120 face blocks."""
        assert fibration_results["n_faces"] == 120


# =========================================================================
# Test Class: Holonomy Classification
# =========================================================================


class TestHolonomyClassification:
    """Verify holonomy computation and classification."""

    def test_all_chosen_faces_hol1(self, fibration_results):
        """All 120 chosen faces have holonomy 1."""
        hc = fibration_results["holonomy_counts"]
        assert hc["chosen_hol1"] == 120

    def test_240_odd_nonface(self, fibration_results):
        """Exactly 240 non-face triangles have holonomy 1."""
        assert fibration_results["n_odd_nonface"] == 240

    def test_holonomy_partition(self, fibration_results):
        """Holonomy partition: 120 + 240 + 840 = 1200."""
        hc = fibration_results["holonomy_counts"]
        total = hc["chosen_hol1"] + hc["nonface_hol1"] + hc["nonface_hol0"]
        assert total == 1200

    def test_nonface_hol0_count(self, fibration_results):
        """840 non-face triangles have holonomy 0."""
        hc = fibration_results["holonomy_counts"]
        assert hc["nonface_hol0"] == 840


# =========================================================================
# Test Class: Fibration Structure
# =========================================================================


class TestFibrationStructure:
    """Verify the 240 = 40 × 6 fibration."""

    def test_constant_degree_10(self, fibration_results):
        """Face-image map has constant degree 10."""
        assert fibration_results["preimage_degree_set"] == [10]

    def test_40_special_faces(self, fibration_results):
        """Exactly 40 special faces receive odd non-face triangles."""
        assert fibration_results["n_special_faces"] == 40

    def test_40_special_lines(self, fibration_results):
        """Special faces biject to 40 W33 lines."""
        assert fibration_results["n_special_lines"] == 40

    def test_fiber_size_6(self, fibration_results):
        """Each special face has exactly 6 odd non-face preimages."""
        for face in fibration_results["special_faces"]:
            profile = fibration_results["face_profiles"][face]
            assert profile["odd_nonface"] == 6, (
                f"Face {face}: odd_nonface = {profile['odd_nonface']}"
            )

    def test_240_equals_40_times_6(self, fibration_results):
        """240 = 40 × 6."""
        assert fibration_results["n_odd_nonface"] == 40 * 6

    def test_special_profile(self, fibration_results):
        """Special faces have profile (odd=6, even=3, self=1)."""
        for face in fibration_results["special_faces"]:
            profile = fibration_results["face_profiles"][face]
            assert profile["odd_nonface"] == 6
            assert profile["even_nonface"] == 3
            assert profile["self"] == 1
            assert profile["total"] == 10

    def test_ordinary_profile(self, fibration_results):
        """Ordinary faces have profile (odd=0, even=9, self=1)."""
        for face, profile in fibration_results["face_profiles"].items():
            if not profile["is_special"]:
                assert profile["odd_nonface"] == 0
                assert profile["even_nonface"] == 9
                assert profile["self"] == 1
                assert profile["total"] == 10

    def test_80_ordinary_faces(self, fibration_results):
        """80 faces are ordinary (120 - 40 = 80)."""
        n_ordinary = sum(
            1
            for profile in fibration_results["face_profiles"].values()
            if not profile["is_special"]
        )
        assert n_ordinary == 80


# =========================================================================
# Test Class: Numerology
# =========================================================================


class TestNumerology:
    """Verify the key numerical coincidences."""

    def test_240_equals_e8_roots(self):
        """240 = |Roots(E8)| = |Edges(W33)|."""
        assert 240 == 240  # trivial but documents the coincidence

    def test_40_equals_w33_lines(self):
        """40 = |Lines(W33)| = |Vertices(W33)|."""
        assert 40 == 40

    def test_6_equals_s3_order(self):
        """6 = |S3| = |Weyl(A2)|."""
        assert 6 == 6

    def test_1200_triangle_count(self):
        """1200 = 5 × 240 = 10 × 120."""
        assert 1200 == 5 * 240
        assert 1200 == 10 * 120

    def test_holonomy_split(self):
        """360 = 120 + 240 (hol=1 partition)."""
        assert 120 + 240 == 360
        # And 360 = 36 * 20 / 2 = number of SRG(36) edges
        assert 360 == 36 * 20 // 2
