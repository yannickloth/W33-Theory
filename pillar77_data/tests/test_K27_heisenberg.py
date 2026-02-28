#!/usr/bin/env python3
"""Tests for Pillar 77 (Part CLXXXV): K54 → K27 Heisenberg(3) ⋊ C6.

These tests validate the *reported* invariants in:
  data/w33_K27_heisenberg.json

Run:
  python THEORY_PART_CLXXXV_K27_HEISENBERG.py
before running pytest.
"""
from __future__ import annotations

import json
import os
import pytest

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FILE = os.path.join(repo_root, "data", "w33_K27_heisenberg.json")


@pytest.fixture(scope="module")
def report():
    assert os.path.exists(DATA_FILE), (
        f"Missing data file: {DATA_FILE}\n"
        "Run THEORY_PART_CLXXXV_K27_HEISENBERG.py first."
    )
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


class TestT1TwinPairing:
    def test_status_ok(self, report):
        assert report["status"] == "ok"

    def test_pair_count(self, report):
        assert report["twin_pairing"]["pair_count"] == 27

    def test_intersection_size(self, report):
        assert report["twin_pairing"]["intersection_size"] == 6


class TestT2InducedAction:
    def test_K_order_on_54(self, report):
        assert report["K"]["order_on_54"] == 162

    def test_K_order_on_27(self, report):
        assert report["K"]["order_on_27"] == 162

    def test_orbits(self, report):
        assert report["K"]["orbit_size_on_54"] == 54
        assert report["K"]["orbit_size_on_27"] == 27


class TestT3HeisenbergLayer:
    def test_derived_order(self, report):
        assert report["Heisenberg"]["derived_order"] == 27

    def test_center_order(self, report):
        assert report["Heisenberg"]["center_order"] == 3

    def test_commutator_order(self, report):
        assert report["Heisenberg"]["commutator_order"] == 3

    def test_g2_central(self, report):
        assert report["Heisenberg"]["g2_is_central"] is True

    def test_presentation_law_present(self, report):
        assert "z+z' - y*x'" in report["Heisenberg"]["presentation_law"]


class TestT4StabilizerC6:
    def test_stabilizer_size(self, report):
        assert report["stabilizer_C6"]["size"] == 6

    def test_stabilizer_is_abelian(self, report):
        assert report["stabilizer_C6"]["is_abelian"] is True

    def test_order_distribution(self, report):
        # C6: 1:1, 2:1, 3:2, 6:2
        d = {int(k): int(v) for k, v in report["stabilizer_C6"]["order_distribution"].items()}
        assert d == {1: 1, 2: 1, 3: 2, 6: 2}

    def test_generator_order6_present(self, report):
        gen = report["stabilizer_C6"]["generator_order6"]
        assert gen["A"] is not None
        assert len(gen["perm"]) == 27


class TestT5AffineDecomposition:
    def test_generators_present(self, report):
        assert set(report["generators_affine"].keys()) == {"g2", "g3", "g5", "g8", "g9"}

    def test_g2_pure_translation(self, report):
        assert report["generators_affine"]["g2"]["s_order"] == 1

    def test_g5_pure_translation(self, report):
        assert report["generators_affine"]["g5"]["s_order"] == 1

    def test_g8_g9_same_involution(self, report):
        assert report["K_generators_27"]["g8"] == report["K_generators_27"]["g9"]
        assert report["generators_affine"]["g8"]["s_order"] == 2
        assert report["generators_affine"]["g9"]["s_order"] == 2

    def test_g3_has_order3_stabilizer_part(self, report):
        assert report["generators_affine"]["g3"]["s_order"] == 3


class TestArtifacts:
    def test_artifact_names(self, report):
        arts = report["artifacts"]
        assert arts["K54_to_K27_twin_map_csv"].endswith(".csv")
        assert arts["K27_heisenberg_coords_csv"].endswith(".csv")
        assert arts["K54_edges_with_coords_voltage_csv"].endswith(".csv")
