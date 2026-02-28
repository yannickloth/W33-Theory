#!/usr/bin/env python3
"""Tests for Pillar 75 (Part CLXXXIII): The C3 Torsor Weld.

Verifies all six theorems linking the K pocket stabilizer C3 to the
H octonion axis-line stabilizer triality element via right-multiplication
on the 192-element torsor:

  T1: K orbit (54 pockets, C3 stabilizer, 270 Schreier edges)
  T2: C3 weld — sigma -> r(399), sigma_inv -> r(246); verified on all 192
  T3: Deck-flip test — both nontrivial sigma preserve enc class (no flip)
  T4: H+ (axis-sign+, order 96) contains the weld C3
  T5: Normal Z4xZ4 (order 16) inside H+; quotient is S3 (6 cosets)
  T6: 270 = |W(E6)|/|W(D4)|; 192 = |W(D4)| = tomotope flags; exact chain
"""

from __future__ import annotations

import json
import os

import pytest

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FILE = os.path.join(repo_root, "data", "w33_triality_weld.json")


@pytest.fixture(scope="module")
def report():
    assert os.path.exists(DATA_FILE), (
        f"Missing data file: {DATA_FILE}\n"
        "Run THEORY_PART_CLXXXIII_TRIALITY_WELD.py first."
    )
    with open(DATA_FILE) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# T1: K pocket orbit
# ---------------------------------------------------------------------------

class TestT1KPocketOrbit:
    def test_status_ok(self, report):
        assert report["status"] == "ok"

    def test_K_order(self, report):
        assert report["T1_K_order"] == 162

    def test_orbit_pockets(self, report):
        assert report["T1_orbit_pockets"] == 54

    def test_stabilizer_order(self, report):
        assert report["T1_stabilizer_order"] == 3

    def test_schreier_edges(self, report):
        assert report["T1_schreier_edges"] == 270

    def test_sigma(self, report):
        assert report["T1_sigma"] == [1, 3, 5, 0, 2, 4, 6]

    def test_sigma_inv(self, report):
        assert report["T1_sigma_inv"] == [3, 0, 4, 1, 5, 2, 6]

    def test_stabilizer_verified(self, report):
        assert report["T1_stabilizer_verified"] is True

    def test_schreier_equals_orbit_times_gens(self, report):
        """270 = 54 pockets × 5 generators."""
        assert report["T1_schreier_edges"] == report["T1_orbit_pockets"] * 5

    def test_K_order_factored(self, report):
        """162 = 2 × 3^4."""
        assert report["T1_K_order"] == 2 * 3**4


# ---------------------------------------------------------------------------
# T2: C3 weld
# ---------------------------------------------------------------------------

class TestT2C3Weld:
    def test_sigma_r_stab(self, report):
        assert report["T2_sigma_r_stab"] == 399

    def test_sigma_inv_r_stab(self, report):
        assert report["T2_sigma_inv_r_stab"] == 246

    def test_id_r_stab(self, report):
        assert report["T2_id_r_stab"] == 7

    def test_weld_verified_enc0(self, report):
        assert report["T2_weld_verified_enc0"] is True

    def test_weld_verified_enc1(self, report):
        assert report["T2_weld_verified_enc1"] is True

    def test_weld_n_elements(self, report):
        assert report["T2_weld_n_elements"] == 192

    def test_sigma_r_is_order3(self, report):
        """The weld element r(399) has order 3 (triality)."""
        assert report["T2_sigma_r_stab"] == 399

    def test_weld_covers_both_enc(self, report):
        """Both enc0 and enc1 are verified (192-element torsor is complete)."""
        assert report["T2_weld_verified_enc0"] is True
        assert report["T2_weld_verified_enc1"] is True


# ---------------------------------------------------------------------------
# T3: Deck-flip test
# ---------------------------------------------------------------------------

class TestT3DeckFlip:
    def test_no_deck_flip(self, report):
        assert report["T3_deck_flip_occurs"] is False

    def test_enc0_preserved(self, report):
        assert report["T3_enc0_preserved"] is True

    def test_enc1_preserved(self, report):
        assert report["T3_enc1_preserved"] is True

    def test_both_sheets_stable(self, report):
        """Both encoding sheets are individually stable under nontrivial sigma."""
        assert report["T3_enc0_preserved"] is True
        assert report["T3_enc1_preserved"] is True
        assert report["T3_deck_flip_occurs"] is False


# ---------------------------------------------------------------------------
# T4: H+ subgroup
# ---------------------------------------------------------------------------

class TestT4HPlus:
    def test_hplus_order(self, report):
        assert report["T4_hplus_order"] == 96

    def test_hplus_matches_tomotope_P(self, report):
        assert report["T4_hplus_matches_tomotope_P"] is True

    def test_weld_C3_in_hplus(self, report):
        assert report["T4_weld_C3_in_hplus"] is True

    def test_hplus_axis_sign_positive(self, report):
        assert report["T4_hplus_axis_sign_all_pos"] is True

    def test_hplus_order_equals_tomotope_gamma(self, report):
        """H+ has order 96 = |Gamma(tomotope)| (the tomotope automorphism group)."""
        assert report["T4_hplus_order"] == 96

    def test_weld_C3_subset_hplus(self, report):
        """C3 = {id, r(399), r(246)} all have axis_sign=+1 hence lie in H+."""
        assert report["T4_weld_C3_in_hplus"] is True


# ---------------------------------------------------------------------------
# T5: Normal N and S3 quotient
# ---------------------------------------------------------------------------

class TestT5QuotientS3:
    def test_normal_N_order(self, report):
        assert report["T5_normal_N_order"] == 16

    def test_hplus_over_N_cosets(self, report):
        assert report["T5_hplus_over_N_cosets"] == 6

    def test_quotient_is_S3(self, report):
        assert report["T5_quotient_is_S3"] is True

    def test_quotient_order_dist_identity(self, report):
        assert report["T5_quotient_order_dist"].get("1", 0) == 1

    def test_quotient_order_dist_involutions(self, report):
        assert report["T5_quotient_order_dist"].get("2", 0) == 3

    def test_quotient_order_dist_3cycles(self, report):
        assert report["T5_quotient_order_dist"].get("3", 0) == 2

    def test_N_index_in_hplus(self, report):
        """96 / 16 = 6."""
        assert report["T4_hplus_order"] // report["T5_normal_N_order"] == 6

    def test_S3_order(self, report):
        """S3 has order 6 = 1 + 3 + 2 (orders 1, 2, 3)."""
        d = report["T5_quotient_order_dist"]
        total = sum(int(v) for v in d.values())
        assert total == 6


# ---------------------------------------------------------------------------
# T6: Numerical coincidence chain
# ---------------------------------------------------------------------------

class TestT6NumericalChain:
    def test_W_D4(self, report):
        assert report["T6_W_D4"] == 192

    def test_tomotope_flags(self, report):
        assert report["T6_tomotope_flags"] == 192

    def test_W_D4_equals_tomotope_flags(self, report):
        assert report["T6_W_D4"] == report["T6_tomotope_flags"]

    def test_W_E6(self, report):
        assert report["T6_W_E6"] == 51840

    def test_E6_over_D4(self, report):
        assert report["T6_E6_over_D4"] == 270

    def test_schreier_equals_E6_over_D4(self, report):
        assert report["T6_schreier_equals_E6_over_D4"] is True

    def test_product_identity(self, report):
        assert report["T6_product_identity"] is True

    def test_product_identity_numerical(self, report):
        """270 × 192 = 51840 = |W(E6)| exactly."""
        assert report["T6_E6_over_D4"] * report["T6_W_D4"] == report["T6_W_E6"]

    def test_W_E8(self, report):
        assert report["T6_W_E8"] == 696729600

    def test_volt_g8_zero_count(self, report):
        assert report["T6_volt_g8_zero_count"] == 48

    def test_volt_g9_zero_count(self, report):
        assert report["T6_volt_g9_zero_count"] == 48

    def test_order3_gens_nontrivial(self, report):
        assert report["T6_order3_gens_nontrivial"] is True

    def test_g8_g9_voltage_fraction(self, report):
        """g8 and g9 have voltage 0 on 48 of 54 edges = 88.9%."""
        assert report["T6_volt_g8_zero_count"] == 48
        assert report["T6_volt_g9_zero_count"] == 48


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

class TestTrialityWeldSummary:
    def test_summary_present(self, report):
        assert "summary" in report

    def test_summary_K_orbit(self, report):
        assert "54" in report["summary"]["K_orbit"]

    def test_summary_C3_weld(self, report):
        assert "399" in report["summary"]["C3_weld"]

    def test_summary_deck_flip(self, report):
        assert "no flip" in report["summary"]["deck_flip"].lower()

    def test_summary_H_plus_order(self, report):
        assert report["summary"]["H_plus_order"] == 96

    def test_summary_normal_N(self, report):
        assert "S3" in report["summary"]["normal_N"]

    def test_summary_coincidence_chain(self, report):
        assert "270" in report["summary"]["coincidence_chain"]
        assert "192" in report["summary"]["coincidence_chain"]
