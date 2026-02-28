#!/usr/bin/env python3
"""Tests for Pillar 76 (Part CLXXXIV): S3 Sheet Transport Law.

Verifies all six theorems establishing the C3 transport law for the K
Schreier Z3 voltage:

  T1: L(v) = s_g * L(u) * c^e satisfied on all 270 edges
  T2: Unique minimal solution: only s_{g3} = c^2 is nontrivial
  T3: Voltage reconstruction c^e = s_g^{-1} * L(v) * L(u)^{-1} exact
  T4: Only 1/243 C3 generator-constant combinations is consistent
  T5: Exactly 3 valid gauges (right-C3 gauge freedom)
  T6: c <-> t^4 (tomotope triality); s_{g3} = c^{-1} (inverse shift)
"""

from __future__ import annotations

import json
import os

import pytest

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FILE = os.path.join(repo_root, "data", "w33_S3_sheet_transport.json")


@pytest.fixture(scope="module")
def report():
    assert os.path.exists(DATA_FILE), (
        f"Missing data file: {DATA_FILE}\n"
        "Run THEORY_PART_CLXXXIV_S3_SHEET_TRANSPORT.py first."
    )
    with open(DATA_FILE) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# T1: C3 transport law
# ---------------------------------------------------------------------------

class TestT1TransportLaw:
    def test_status_ok(self, report):
        assert report["status"] == "ok"

    def test_edges_total(self, report):
        assert report["T1_edges_total"] == 270

    def test_edges_satisfied(self, report):
        assert report["T1_edges_satisfied"] == 270

    def test_transport_law_holds(self, report):
        assert report["T1_transport_law_holds"] is True

    def test_c_is_3cycle(self, report):
        assert report["T1_c"] == [1, 2, 0]

    def test_s_g3(self, report):
        assert report["T1_s_g3"] == [2, 0, 1]

    def test_all_edges_exact(self, report):
        """All 270 directed Schreier edges satisfied — zero exceptions."""
        assert report["T1_edges_satisfied"] == report["T1_edges_total"]


# ---------------------------------------------------------------------------
# T2: Minimal generator constants
# ---------------------------------------------------------------------------

class TestT2MinimalConstants:
    def test_s_g2_trivial(self, report):
        assert report["T2_s_g2_trivial"] is True

    def test_s_g3_is_c2(self, report):
        assert report["T2_s_g3"] == [2, 0, 1]  # c^2 = (2,0,1)

    def test_s_g5_trivial(self, report):
        assert report["T2_s_g5_trivial"] is True

    def test_s_g8_trivial(self, report):
        assert report["T2_s_g8_trivial"] is True

    def test_s_g9_trivial(self, report):
        assert report["T2_s_g9_trivial"] is True

    def test_flat_fails(self, report):
        """All-identity generator constants fail (g3 must be nontrivial)."""
        assert report["T2_flat_fails"] is True

    def test_only_g3_nontrivial(self, report):
        assert report["T2_only_g3_nontrivial"] is True

    def test_s_g3_correct_tuple(self, report):
        """s_{g3} = c^2 = (2,0,1) in cycle notation."""
        s_g3 = report["s_g_minimal"]["g3"]
        assert s_g3 == [2, 0, 1]


# ---------------------------------------------------------------------------
# T3: Voltage reconstruction
# ---------------------------------------------------------------------------

class TestT3VoltageReconstruction:
    def test_reconstruction_ok(self, report):
        assert report["T3_reconstruction_ok"] == 270

    def test_reconstruction_total(self, report):
        assert report["T3_reconstruction_total"] == 270

    def test_exact(self, report):
        assert report["T3_exact"] is True

    def test_reconstruction_complete(self, report):
        """c^e = s_g^{-1} * L(v) * L(u)^{-1} works on every edge."""
        assert report["T3_reconstruction_ok"] == report["T3_reconstruction_total"]


# ---------------------------------------------------------------------------
# T4: C3 uniqueness
# ---------------------------------------------------------------------------

class TestT4Uniqueness:
    def test_combinations_tried(self, report):
        assert report["T4_c3_combinations_tried"] == 243

    def test_valid_solutions(self, report):
        assert report["T4_valid_solutions"] == 1

    def test_unique(self, report):
        assert report["T4_unique"] is True

    def test_unique_solution_g3(self, report):
        """The unique solution has g3 mapped to S3 element #4 = (2,0,1)."""
        sol = report["T4_unique_solution"]
        assert sol["g3"] == 4

    def test_unique_solution_others_trivial(self, report):
        """All other generator constants are identity (S3 element #0)."""
        sol = report["T4_unique_solution"]
        for gname in ["g2", "g5", "g8", "g9"]:
            assert sol[gname] == 0

    def test_243_is_c3_power5(self, report):
        """243 = 3^5 = |C3|^5 (one choice per generator)."""
        assert report["T4_c3_combinations_tried"] == 3**5


# ---------------------------------------------------------------------------
# T5: Gauge freedom
# ---------------------------------------------------------------------------

class TestT5GaugeFreedom:
    def test_valid_L0_count(self, report):
        assert report["T5_valid_L0_count"] == 3

    def test_gauge_group(self, report):
        assert report["T5_gauge_group"] == "C3"

    def test_gauge_freedom(self, report):
        assert report["T5_gauge_freedom"] is True

    def test_3_solutions_for_3_c3_elements(self, report):
        """3 valid L(0) choices correspond exactly to the 3 elements of C3."""
        assert report["T5_valid_L0_count"] == 3


# ---------------------------------------------------------------------------
# T6: Tomotope triality identification
# ---------------------------------------------------------------------------

class TestT6TomotopeBridge:
    def test_c_order(self, report):
        assert report["T6_c_order"] == 3

    def test_c_is_t4_analog(self, report):
        assert report["T6_c_is_t4_analog"] is True

    def test_s_g3_is_c_inverse(self, report):
        assert report["T6_s_g3_is_c_inverse"] is True

    def test_transport_as_triality_phase(self, report):
        assert report["T6_transport_as_triality_phase"] is True

    def test_phase_distribution_sums_to_54(self, report):
        """L-values cover all 54 pockets."""
        d = report["T6_phase_distribution"]
        assert sum(int(v) for v in d.values()) == 54

    def test_phase_distribution_three_values(self, report):
        """L-values use exactly 3 C3 phases (0, 1, 2)."""
        d = report["T6_phase_distribution"]
        assert len(d) == 3
        for k in ["0", "1", "2"]:
            assert k in d

    def test_L_table_length(self, report):
        """L-table covers all 54 pocket nodes."""
        assert len(report["T6_L_table"]) == 54

    def test_L_table_values_in_C3(self, report):
        """All L-values are in {0, 1, 2} (C3 exponents)."""
        assert all(v in [0, 1, 2] for v in report["T6_L_table"])

    def test_s_g3_inverse_of_c(self, report):
        """s_{g3} = c^2 = c^{-1}; applying twice gives c^3 = id."""
        s_g3 = tuple(report["s_g_minimal"]["g3"])
        c_perm = tuple(report["T1_c"])
        # c^2 * c = id?
        composed = tuple(s_g3[c_perm[i]] for i in range(3))
        assert composed == (0, 1, 2)


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

class TestS3SheetTransportSummary:
    def test_summary_present(self, report):
        assert "summary" in report

    def test_summary_transport_law(self, report):
        assert "c=(1,2,0)" in report["summary"]["transport_law"]

    def test_summary_nontrivial_gen(self, report):
        assert "g3" in report["summary"]["only_nontrivial_gen"]

    def test_summary_edges_verified(self, report):
        assert report["summary"]["edges_verified"] == 270

    def test_summary_unique(self, report):
        assert report["summary"]["unique_C3_solution"] is True

    def test_summary_gauge_freedom(self, report):
        assert "3 solutions" in report["summary"]["gauge_freedom"]

    def test_summary_tomotope_bridge(self, report):
        assert "t^4" in report["summary"]["tomotope_bridge"]

    def test_L_table_canonical_stored(self, report):
        """Full L-table is stored for downstream use."""
        assert "L_table_canonical" in report
        assert len(report["L_table_canonical"]) == 54

    def test_s_g_minimal_stored(self, report):
        assert "s_g_minimal" in report
        assert set(report["s_g_minimal"].keys()) == {"g2", "g3", "g5", "g8", "g9"}
