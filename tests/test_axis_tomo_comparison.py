#!/usr/bin/env python3
"""Tests for Pillar 87 (Part CXCIII): Axis Group H+ vs Tomotope P -- Parallel Normal Series
and W(E6)/W(D4) Numerology.

Verifies six theorems comparing H+ (axis-sign-plus subgroup, order 96) with the
tomotope edge group P (order 96), via their parallel normal-16 filtrations, and
proving the W(E6)/W(D4) = 270 Schreier-graph identity.
"""

from __future__ import annotations

import json
import os

import pytest

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FILE = os.path.join(repo_root, "data", "w33_axis_tomo_comparison.json")


@pytest.fixture(scope="module")
def report():
    assert os.path.exists(DATA_FILE), (
        f"Missing data file: {DATA_FILE}\n"
        "Run THEORY_PART_CXCIII_AXIS_TOMO_COMPARISON.py first."
    )
    with open(DATA_FILE) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# T1: H+ (axis-sign-plus, order 96) and C3 weld elements
# ---------------------------------------------------------------------------

class TestT1HplusAndWeld:
    def test_status_ok(self, report):
        assert report["status"] == "ok"

    def test_Hplus_order(self, report):
        assert report["T1_Hplus_order"] == 96

    def test_Hplus_order1_count(self, report):
        assert report["T1_Hplus_order_distribution"]["1"] == 1

    def test_Hplus_order2_count(self, report):
        assert report["T1_Hplus_order_distribution"]["2"] == 15

    def test_Hplus_order3_count(self, report):
        assert report["T1_Hplus_order_distribution"]["3"] == 32

    def test_Hplus_order4_count(self, report):
        assert report["T1_Hplus_order_distribution"]["4"] == 24

    def test_Hplus_order8_count(self, report):
        assert report["T1_Hplus_order_distribution"]["8"] == 24

    def test_Hplus_order_distribution_sums_to_96(self, report):
        total = sum(report["T1_Hplus_order_distribution"].values())
        assert total == 96

    def test_weld_elements_in_Hplus(self, report):
        assert report["T1_weld_elements_in_Hplus"] is True

    def test_weld_sign_products_plus1(self, report):
        assert report["T1_weld_sign_products_plus1"] is True


# ---------------------------------------------------------------------------
# T2: H+ normal N16 = Z4 x Z4; quotient = S3
# ---------------------------------------------------------------------------

class TestT2HplusNormal16:
    def test_N16_order(self, report):
        assert report["T2_N16_order"] == 16

    def test_N16_order1_count(self, report):
        assert report["T2_N16_order_distribution"]["1"] == 1

    def test_N16_order2_count(self, report):
        assert report["T2_N16_order_distribution"]["2"] == 3

    def test_N16_order4_count(self, report):
        assert report["T2_N16_order_distribution"]["4"] == 12

    def test_N16_order_dist_sums_to_16(self, report):
        total = sum(report["T2_N16_order_distribution"].values())
        assert total == 16

    def test_N16_structure_Z4xZ4(self, report):
        assert report["T2_N16_structure"] == "Z4xZ4"

    def test_quotient_coset_count(self, report):
        assert report["T2_quotient_coset_count"] == 6

    def test_quotient_order1(self, report):
        assert report["T2_quotient_order_distribution"]["1"] == 1

    def test_quotient_order2(self, report):
        assert report["T2_quotient_order_distribution"]["2"] == 3

    def test_quotient_order3(self, report):
        assert report["T2_quotient_order_distribution"]["3"] == 2

    def test_quotient_is_S3(self, report):
        assert report["T2_quotient_is_S3"] is True

    def test_quotient_order_sums_to_6(self, report):
        total = sum(report["T2_quotient_order_distribution"].values())
        assert total == 6


# ---------------------------------------------------------------------------
# T3: Tomotope P's normal 2-core N'16 = Z2^4; quotient = S3
# ---------------------------------------------------------------------------

class TestT3TomotopeP2Core:
    def test_P_order(self, report):
        assert report["T3_P_order"] == 96

    def test_P_order2_count(self, report):
        assert report["T3_P_order_distribution"]["2"] == 27

    def test_P_order3_count(self, report):
        assert report["T3_P_order_distribution"]["3"] == 32

    def test_P_order4_count(self, report):
        assert report["T3_P_order_distribution"]["4"] == 36

    def test_P_derived_order(self, report):
        assert report["T3_P_derived_order"] == 48

    def test_P_abelianization(self, report):
        assert report["T3_P_abelianization_order"] == 2

    def test_P_2core_order(self, report):
        assert report["T3_P_2core_order"] == 16

    def test_P_2core_structure(self, report):
        assert report["T3_P_2core_structure"] == "Z2^4"

    def test_P_quotient_cosets(self, report):
        assert report["T3_P_quotient_coset_count"] == 6

    def test_P_quotient_is_S3(self, report):
        assert report["T3_P_quotient_is_S3"] is True

    def test_P_quotient_order1(self, report):
        assert report["T3_P_quotient_order_distribution"]["1"] == 1

    def test_P_quotient_order2(self, report):
        assert report["T3_P_quotient_order_distribution"]["2"] == 3

    def test_P_quotient_order3(self, report):
        assert report["T3_P_quotient_order_distribution"]["3"] == 2


# ---------------------------------------------------------------------------
# T4: P and H+ are non-isomorphic
# ---------------------------------------------------------------------------

class TestT4PvsHplusNonIso:
    def test_P_involutions(self, report):
        assert report["T4_P_involutions"] == 27

    def test_P_no_order8(self, report):
        assert report["T4_P_order8_count"] == 0

    def test_Hplus_involutions(self, report):
        assert report["T4_Hplus_involutions"] == 15

    def test_Hplus_order8_count(self, report):
        assert report["T4_Hplus_order8_count"] == 24

    def test_P_normal16_Z2pow4(self, report):
        assert report["T4_P_normal16_structure"] == "Z2^4"

    def test_Hplus_normal16_Z4xZ4(self, report):
        assert report["T4_Hplus_normal16_structure"] == "Z4xZ4"

    def test_nonisomorphic(self, report):
        assert report["T4_P_Hplus_nonisomorphic"] is True

    def test_involution_counts_differ(self, report):
        """P has 12 more involutions than H+."""
        assert report["T4_P_involutions"] - report["T4_Hplus_involutions"] == 12

    def test_order8_counts_differ(self, report):
        """H+ has 24 more order-8 elements than P."""
        assert report["T4_Hplus_order8_count"] - report["T4_P_order8_count"] == 24


# ---------------------------------------------------------------------------
# T5: K Schreier 270 edges = |W(E6)|/|W(D4)|
# ---------------------------------------------------------------------------

class TestT5SchreierW:
    def test_schreier_edges(self, report):
        assert report["T5_schreier_edges"] == 270

    def test_gen_count(self, report):
        assert report["T5_gen_count"] == 5

    def test_edges_per_gen(self, report):
        assert report["T5_edges_per_gen"] == 54

    def test_gen_times_pockets(self, report):
        assert report["T5_gen_count"] * report["T5_edges_per_gen"] == 270

    def test_cocycle_exp0(self, report):
        assert report["T5_cocycle_exp0_count"] == 201

    def test_cocycle_exp1(self, report):
        assert report["T5_cocycle_exp1_count"] == 33

    def test_cocycle_exp2(self, report):
        assert report["T5_cocycle_exp2_count"] == 36

    def test_cocycle_total(self, report):
        total = (
            report["T5_cocycle_exp0_count"]
            + report["T5_cocycle_exp1_count"]
            + report["T5_cocycle_exp2_count"]
        )
        assert total == 270

    def test_nontrivial_edges(self, report):
        assert report["T5_nontrivial_edges"] == 69

    def test_W_E6(self, report):
        assert report["T5_W_E6"] == 51840

    def test_W_D4(self, report):
        assert report["T5_W_D4"] == 192

    def test_W_E6_over_W_D4(self, report):
        assert report["T5_W_E6_over_W_D4"] == 270

    def test_schreier_matches_quotient(self, report):
        assert report["T5_schreier_matches_quotient"] is True


# ---------------------------------------------------------------------------
# T6: C3 weld is order-preserving monomorphism C3 -> H+
# ---------------------------------------------------------------------------

class TestT6C3Weld:
    def test_weld_C3_size(self, report):
        assert report["T6_weld_C3_size"] == 3

    def test_id_r_stab(self, report):
        assert report["T6_id_r_stab_index"] == 7

    def test_sigma_r_stab(self, report):
        assert report["T6_sigma_r_stab_index"] == 399

    def test_sigma_inv_r_stab(self, report):
        assert report["T6_sigma_inv_r_stab_index"] == 246

    def test_weld_order_preserving(self, report):
        assert report["T6_weld_order_preserving"] is True

    def test_weld_monomorphism(self, report):
        assert report["T6_weld_monomorphism"] is True

    def test_all_weld_in_Hplus(self, report):
        assert report["T6_all_weld_in_Hplus"] is True

    def test_weld_element_stab_indices_distinct(self, report):
        """Three weld elements have distinct stab indices."""
        indices = {
            report["T6_id_r_stab_index"],
            report["T6_sigma_r_stab_index"],
            report["T6_sigma_inv_r_stab_index"],
        }
        assert len(indices) == 3


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

class TestAxisTomoComparisonSummary:
    def test_summary_present(self, report):
        assert "summary" in report

    def test_summary_Hplus(self, report):
        assert "96" in report["summary"]["Hplus_structure"]
        assert "C3" in report["summary"]["Hplus_structure"]

    def test_summary_N16(self, report):
        assert "Z4" in report["summary"]["Hplus_N16"]
        assert "S3" in report["summary"]["Hplus_N16"]

    def test_summary_P_2core(self, report):
        assert "Z2" in report["summary"]["P_2core"]
        assert "S3" in report["summary"]["P_2core"]

    def test_summary_P_vs_Hplus(self, report):
        assert "Z2^4" in report["summary"]["P_vs_Hplus"]
        assert "Z4xZ4" in report["summary"]["P_vs_Hplus"]

    def test_summary_schreier(self, report):
        assert "270" in report["summary"]["schreier"]
        assert "51840" in report["summary"]["schreier"]

    def test_summary_C3_weld(self, report):
        assert "r(399)" in report["summary"]["C3_weld"]
        assert "r(246)" in report["summary"]["C3_weld"]
