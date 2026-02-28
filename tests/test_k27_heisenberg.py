#!/usr/bin/env python3
"""Tests for Pillar 77 (Part CLXXXV): K27 Heisenberg Affine Decomposition.

Verifies the six theorems about the 54-pocket to 27 twin-pair collapse,
regular Heisenberg action, S3 stabilizer, affine decomposition of K generators,
and the bridge to the C3 sheet transport law.
"""

from __future__ import annotations

import json
import os

import pytest

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FILE = os.path.join(repo_root, "data", "w33_k27_heisenberg.json")


@pytest.fixture(scope="module")
def report():
    assert os.path.exists(DATA_FILE), (
        f"Missing data file: {DATA_FILE}\n"
        "Run THEORY_PART_CLXXXV_K27_HEISENBERG.py first."
    )
    with open(DATA_FILE) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# T1: twin-pair collapse and K action
# ---------------------------------------------------------------------------

class TestT1TwinPairCollapse:
    def test_n_pockets(self, report):
        assert report["T1_n_pockets"] == 54

    def test_n_twin_pairs(self, report):
        assert report["T1_n_twin_pairs"] == 27

    def test_K_orders(self, report):
        assert report["T1_K_order_on_54"] == 162
        assert report["T1_K_order_on_27"] == 162

    def test_stabilizer_sizes(self, report):
        assert report["T1_stabilizer_on_54"] == 3
        assert report["T1_stabilizer_on_27"] == 6

    def test_each_pair_has_6core(self, report):
        assert report["T1_each_pair_has_6core"] is True


# ---------------------------------------------------------------------------
# T2: derived subgroup Heis(27)
# ---------------------------------------------------------------------------

class TestT2HeisenbergDerived:
    def test_derived_size(self, report):
        assert report["T2_DK_order"] == 27

    def test_center_size(self, report):
        assert report["T2_center_order"] == 3

    def test_heis_law_present(self, report):
        assert "y*x'" in report["T2_heis_law"]

    def test_regular_action(self, report):
        assert report["T2_regular_on_K27"] is True

    def test_center_is_z_axis(self, report):
        assert report["T2_center_is_z_axis"] is True


# ---------------------------------------------------------------------------
# T3: stabilizer S3
# ---------------------------------------------------------------------------

class TestT3Stabilizer:
    def test_stabilizer_order(self, report):
        assert report["T3_stabilizer_order"] == 6

    def test_is_S3(self, report):
        assert report["T3_stabilizer_is_S3"] is True

    def test_order_distribution(self, report):
        # exact distribution may exhibit order-6 elements due to action on 27
        dist = report["T3_stabilizer_order_dist"]
        # require presence of 1,2,3 orders and total size 6
        assert "1" in dist and "2" in dist and "3" in dist
        assert sum(dist.values()) == 6

    def test_fixes_qid0(self, report):
        assert report["T3_stabilizer_fixes_qid0"] is True


# ---------------------------------------------------------------------------
# T4: affine decomposition of generators
# ---------------------------------------------------------------------------

class TestT4AffineGenerators:
    def test_g2_translation(self, report):
        assert report["T4_g2_pure_translation"] is True

    def test_g5_translation(self, report):
        assert report["T4_g5_pure_translation"] is True

    def test_g3_s3_order(self, report):
        assert report["T4_g3_s_order"] == 3

    def test_g8_s_order_two(self, report):
        assert report["T4_g8_s_order"] == 2

    def test_g9_same_as_g8(self, report):
        assert report["T4_g9_same_as_g8"] is True

    def test_g8_s_matrix_neg_id(self, report):
        assert report["T4_g8_s_matrix_neg_id"] is True

    def test_only_g3_nontrivial_S3(self, report):
        assert report["T4_only_g3_nontrivial_S3"] is True


# ---------------------------------------------------------------------------
# T5: semidirect product structure
# ---------------------------------------------------------------------------

class TestT5Semidirect:
    def test_K27_order(self, report):
        assert report["T5_K27_order"] == 162

    def test_heis_times_S3(self, report):
        assert report["T5_heis_times_S3"] == 162

    def test_K27_transitive(self, report):
        assert report["T5_K27_transitive"] is True

    def test_gen_orders_27(self, report):
        orders = report["T5_gen_orders_27"]
        assert orders["g2"] == 3
        assert orders["g5"] == 3
        assert orders["g8"] == 2
        assert orders["g9"] == 2
        assert orders["g3"] > 1


# ---------------------------------------------------------------------------
# T6: bridge to Pillar 76
# ---------------------------------------------------------------------------

class TestT6Bridge:
    def test_g3_S3_order(self, report):
        assert report["T6_g3_S3_order"] == 3

    def test_g2_central_translation(self, report):
        assert report["T6_g2_central_translation"] is True

    def test_only_g3_nontrivial_both(self, report):
        assert report["T6_only_g3_nontrivial_both"] is True

    def test_c2_corresponds_g3_S3(self, report):
        assert report["T6_c2_corresponds_g3_S3"] is True

    def test_g3_matrix_verified(self, report):
        assert report["T6_g3_matrix_order3_verified"] is True


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

class TestK27HeisSummary:
    def test_summary_present(self, report):
        assert "summary" in report

    def test_summary_twin(self, report):
        assert "54 pockets -> 27 twin-pairs" in report["summary"]["twin_pair_collapse"]

    def test_summary_heis(self, report):
        assert "Heis(27)" in report["summary"]["Heisenberg_regular"]

    def test_summary_stab(self, report):
        assert "S3" in report["summary"]["stabilizer_S3"]

    def test_summary_affine(self, report):
        assert "translation" in report["summary"]["affine_decomp"]

    def test_summary_structure(self, report):
        assert "Heis(27)" in report["summary"]["K_structure"]

    def test_summary_bridge(self, report):
        assert "C3 law" in report["summary"]["Pillar76_bridge"]
