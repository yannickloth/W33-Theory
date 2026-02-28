#!/usr/bin/env python3
"""Tests for Pillar 86 (Part CXCII): Twist Transport, Reye Configurations, and Hard Conjugacy Obstruction.

Verifies six theorems characterising how the true tomotope maniplex relates to
the axis-192 flag model via the conjugating bijection pi, and the definitive
hard conjugacy obstruction via the tomotope edge group P's 2-subset signature.
"""

from __future__ import annotations

import json
import os

import pytest

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FILE = os.path.join(repo_root, "data", "w33_twist_transport_reye.json")


@pytest.fixture(scope="module")
def report():
    assert os.path.exists(DATA_FILE), (
        f"Missing data file: {DATA_FILE}\n"
        "Run THEORY_PART_CXCII_TWIST_TRANSPORT_REYE.py first."
    )
    with open(DATA_FILE) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# T1: pi bijection — 50 fixed points, cycle structure, fixes r0 & r3
# ---------------------------------------------------------------------------

class TestT1PiBijection:
    def test_status_ok(self, report):
        assert report["status"] == "ok"

    def test_pi_is_permutation(self, report):
        assert report["T1_pi_is_permutation"] is True

    def test_pi_fixed_points(self, report):
        assert report["T1_pi_fixed_points"] == 50

    def test_pi_cycle_structure(self, report):
        cyc = report["T1_pi_cycle_structure"]
        assert cyc["1"] == 50
        assert cyc["4"] == 1
        assert cyc["9"] == 2
        assert cyc["27"] == 2
        assert cyc["66"] == 1

    def test_pi_cycle_count(self, report):
        """Total cycles = 50 + 1 + 2 + 2 + 1 = 56."""
        cyc = report["T1_pi_cycle_structure"]
        total_cycles = sum(cyc.values())
        assert total_cycles == 56

    def test_pi_total_flags(self, report):
        """Total flags covered = 50*1 + 1*4 + 2*9 + 2*27 + 1*66 = 192."""
        cyc = report["T1_pi_cycle_structure"]
        total = (
            int(cyc["1"]) * 1 + int(cyc["4"]) * 4 + int(cyc["9"]) * 9
            + int(cyc["27"]) * 27 + int(cyc["66"]) * 66
        )
        assert total == 192

    def test_r0_r3_fixed(self, report):
        assert report["T1_r0_r3_fixed"] is True

    def test_r1_r2_twisted(self, report):
        assert report["T1_r1_r2_twisted"] is True


# ---------------------------------------------------------------------------
# T2: Transported Coxeter relations (3, 12, 4, 2, 2, 2)
# ---------------------------------------------------------------------------

class TestT2TransportedCoxeter:
    def test_r0r1_order(self, report):
        assert report["T2_coxeter_orders"]["r0r1"] == 3

    def test_r1r2_order(self, report):
        assert report["T2_coxeter_orders"]["r1r2"] == 12

    def test_r2r3_order(self, report):
        assert report["T2_coxeter_orders"]["r2r3"] == 4

    def test_r0r2_order(self, report):
        assert report["T2_coxeter_orders"]["r0r2"] == 2

    def test_r0r3_order(self, report):
        assert report["T2_coxeter_orders"]["r0r3"] == 2

    def test_r1r3_order(self, report):
        assert report["T2_coxeter_orders"]["r1r3"] == 2

    def test_all_generators_involutions(self, report):
        assert report["T2_all_generators_involutions"] is True

    def test_coxeter_diagram_holds(self, report):
        assert report["T2_tomotope_coxeter_holds"] is True

    def test_six_coxeter_pairs(self, report):
        """Exactly 6 Coxeter pairs recorded."""
        assert len(report["T2_coxeter_orders"]) == 6


# ---------------------------------------------------------------------------
# T3: Twist elements d1, d2 — no fixed points, cycle structures
# ---------------------------------------------------------------------------

class TestT3TwistElements:
    def test_d1_order(self, report):
        assert report["T3_d1_order"] == 150

    def test_d1_fixed_points(self, report):
        assert report["T3_d1_fixed_points"] == 0

    def test_d1_cycle_structure(self, report):
        cyc = report["T3_d1_cycle_structure"]
        assert cyc["2"] == 4
        assert cyc["6"] == 4
        assert cyc["15"] == 4
        assert cyc["25"] == 4

    def test_d1_cycle_total(self, report):
        """d1 covers all 192 flags."""
        cyc = report["T3_d1_cycle_structure"]
        total = sum(int(k) * v for k, v in cyc.items())
        assert total == 192

    def test_d2_order(self, report):
        assert report["T3_d2_order"] == 46

    def test_d2_fixed_points(self, report):
        assert report["T3_d2_fixed_points"] == 0

    def test_d2_cycle_structure(self, report):
        cyc = report["T3_d2_cycle_structure"]
        assert cyc["2"] == 4
        assert cyc["46"] == 4

    def test_d2_cycle_total(self, report):
        """d2 covers all 192 flags."""
        cyc = report["T3_d2_cycle_structure"]
        total = sum(int(k) * v for k, v in cyc.items())
        assert total == 192

    def test_both_twists_no_fixed(self, report):
        assert report["T3_d1_fixed_points"] == 0
        assert report["T3_d2_fixed_points"] == 0


# ---------------------------------------------------------------------------
# T4: Tomotope edge group P — order 96, signature [48,6,6,6]
# ---------------------------------------------------------------------------

class TestT4EdgeGroupP:
    def test_P_order(self, report):
        assert report["T4_P_order"] == 96

    def test_P_generators_involutions(self, report):
        assert report["T4_P_generators_involutions"] is True

    def test_P_order1_count(self, report):
        assert report["T4_P_order_distribution"]["1"] == 1

    def test_P_order2_count(self, report):
        assert report["T4_P_order_distribution"]["2"] == 27

    def test_P_order3_count(self, report):
        assert report["T4_P_order_distribution"]["3"] == 32

    def test_P_order4_count(self, report):
        assert report["T4_P_order_distribution"]["4"] == 36

    def test_P_order_distribution_sums_to_96(self, report):
        total = sum(report["T4_P_order_distribution"].values())
        assert total == 96

    def test_P_2subset_signature(self, report):
        assert sorted(report["T4_P_2subset_signature"], reverse=True) == [48, 6, 6, 6]

    def test_P_2subset_orbit_count(self, report):
        """66 2-subsets split into 4 orbits: 48+6+6+6=66."""
        assert report["T4_P_2subset_orbit_count"] == 4

    def test_P_2subset_sizes_sum(self, report):
        """48 + 6 + 6 + 6 = 66 = C(12,2)."""
        sig = report["T4_P_2subset_signature"]
        assert sum(sig) == 66

    def test_P_three_small_orbits(self, report):
        """Three orbits of size 6."""
        sig = report["T4_P_2subset_signature"]
        assert sig.count(6) == 3


# ---------------------------------------------------------------------------
# T5: Four Reye (12,16)-configurations
# ---------------------------------------------------------------------------

class TestT5ReyeConfigurations:
    def test_size16_orbit_count(self, report):
        assert report["T5_size16_orbit_count"] == 4

    def test_reye_configs_valid(self, report):
        assert report["T5_reye_configs_valid"] == 4

    def test_reye_point_count(self, report):
        assert report["T5_reye_point_count"] == 12

    def test_reye_line_count(self, report):
        assert report["T5_reye_line_count"] == 16

    def test_reye_point_degree(self, report):
        """Every point lies on exactly 4 lines."""
        assert report["T5_reye_point_degree"] == 4

    def test_reye_max_intersection(self, report):
        """Any two lines share at most 1 point."""
        assert report["T5_reye_max_intersection"] == 1

    def test_3subset_orbit_distribution(self, report):
        """3-subset orbits include [48,48,48,16,16,16,16,12]."""
        sizes = sorted(report["T5_3subset_orbit_sizes"], reverse=True)
        assert sizes[0] == 48
        assert sizes.count(16) == 4
        assert 12 in sizes

    def test_3subset_total(self, report):
        """Total 3-subsets = C(12,3) = 220."""
        total = sum(report["T5_3subset_orbit_sizes"])
        assert total == 220

    def test_all_valid_means_point_reye(self, report):
        """All 4 size-16 orbits are valid Reye configs."""
        assert report["T5_reye_configs_valid"] == report["T5_size16_orbit_count"]


# ---------------------------------------------------------------------------
# T6: Hard conjugacy obstruction
# ---------------------------------------------------------------------------

class TestT6HardObstruction:
    def test_tomotope_P_signature(self, report):
        assert sorted(report["T6_tomotope_P_signature"], reverse=True) == [48, 6, 6, 6]

    def test_axis_index2_count(self, report):
        assert report["T6_axis_index2_count"] == 3

    def test_all_axis_signatures_are_48_12_6(self, report):
        for sig in report["T6_all_axis_signatures"]:
            assert sorted(sig, reverse=True) == [48, 12, 6]

    def test_signatures_differ(self, report):
        """Tomotope signature [48,6,6,6] != axis signature [48,12,6]."""
        tomo = sorted(report["T6_tomotope_P_signature"], reverse=True)
        for sig in report["T6_all_axis_signatures"]:
            assert tomo != sorted(sig, reverse=True)

    def test_obstruction_confirmed(self, report):
        assert report["T6_obstruction_confirmed"] is True

    def test_tomotope_not_axis_model(self, report):
        assert report["T6_tomotope_not_axis_model"] is True

    def test_axis_signature_sum(self, report):
        """48 + 12 + 6 = 66 = C(12,2)."""
        for sig in report["T6_all_axis_signatures"]:
            assert sum(sig) == 66

    def test_tomotope_signature_sum(self, report):
        """48 + 6 + 6 + 6 = 66 = C(12,2)."""
        assert sum(report["T6_tomotope_P_signature"]) == 66


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

class TestTwistTransportReySummary:
    def test_summary_present(self, report):
        assert "summary" in report

    def test_summary_pi_bijection(self, report):
        assert "50" in report["summary"]["pi_bijection"]
        assert "r0" in report["summary"]["pi_bijection"]

    def test_summary_coxeter(self, report):
        assert "3" in report["summary"]["coxeter_diagram"]
        assert "12" in report["summary"]["coxeter_diagram"]

    def test_summary_twist_elements(self, report):
        assert "150" in report["summary"]["twist_elements"]
        assert "46" in report["summary"]["twist_elements"]

    def test_summary_edge_group_P(self, report):
        assert "96" in report["summary"]["edge_group_P"]
        assert "48" in report["summary"]["edge_group_P"]

    def test_summary_reye(self, report):
        assert "16" in report["summary"]["reye_configs"]
        assert "12" in report["summary"]["reye_configs"]

    def test_summary_obstruction(self, report):
        assert "48" in report["summary"]["hard_obstruction"]
        assert "12" in report["summary"]["hard_obstruction"]
