#!/usr/bin/env python3
"""Tests for Pillar 74 (Part CLXXXII): Tomotope-Axis Block Twist.

Verifies all six theorems relating the 48 tomotope blocks to both the
tomotope and axis-line maniplex (edge,face)-incidence pair structures:

  T1: 48 blocks = tomotope (edge,face) incidence pairs —
      4 blocks per tomotope edge (12 edges), 3 blocks per tomotope face (16 faces)
  T2: Same 48 blocks = axis (edge,face) incidence pairs —
      3 blocks per axis edge (16 edges), 4 blocks per axis face (12 faces)
  T3: Tomotope (4,12,16,8) and axis (1,16,12,4) share E_tomo=F_axis=12,
      F_tomo=E_axis=16; both have 192 flags (edge-face swap)
  T4: Axis r0, r3 belong to tomotope monodromy G (equal tr0, tr3 in tomotope
      coords); axis r1, r2 do NOT belong to G
  T5: Tomotope r1 = pure edge-swapper (keepE=0, keepVFC=192);
      tomotope r2 = pure face-swapper (keepF=0, keepVEC=192);
      axis r1, r2 are mixed (keepE=keepF=0 but not 192)
  T6: K voltage distribution — order-2 generators g8,g9 carry voltage 0 for
      48/54 edges; order-3 generators g2,g3,g5 carry non-trivial voltage;
      200/200 random inverse tests pass
"""

from __future__ import annotations

import json
import os

import pytest

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FILE = os.path.join(repo_root, "data", "w33_axis_block_twist.json")


@pytest.fixture(scope="module")
def report():
    assert os.path.exists(DATA_FILE), (
        f"Missing data file: {DATA_FILE}\n"
        "Run THEORY_PART_CLXXXII_AXIS_BLOCK_TWIST.py first."
    )
    with open(DATA_FILE) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# T1: 48 blocks = tomotope (edge,face) incidence pairs
# ---------------------------------------------------------------------------

class TestT1TomotopeBlockPairs:
    def test_status_ok(self, report):
        assert report["status"] == "ok"

    def test_n_blocks(self, report):
        assert report["T1_n_blocks"] == 48

    def test_tomotope_edges(self, report):
        assert report["T1_tomotope_edges"] == 12

    def test_tomotope_faces(self, report):
        assert report["T1_tomotope_faces"] == 16

    def test_blocks_per_tomotope_edge(self, report):
        assert report["T1_blocks_per_tomotope_edge"] == 4

    def test_blocks_per_tomotope_face(self, report):
        assert report["T1_blocks_per_tomotope_face"] == 3

    def test_ef_pairs_unique(self, report):
        assert report["T1_ef_pairs_unique"] is True

    def test_edge_face_product(self, report):
        """12 edges × 4 blocks + 16 faces × 3 blocks = 48 each."""
        assert report["T1_tomotope_edges"] * report["T1_blocks_per_tomotope_edge"] == 48
        assert report["T1_tomotope_faces"] * report["T1_blocks_per_tomotope_face"] == 48


# ---------------------------------------------------------------------------
# T2: Same 48 blocks = axis (edge,face) incidence pairs
# ---------------------------------------------------------------------------

class TestT2AxisBlockPairs:
    def test_axis_edges(self, report):
        assert report["T2_axis_edges"] == 16

    def test_axis_faces(self, report):
        assert report["T2_axis_faces"] == 12

    def test_blocks_per_axis_edge(self, report):
        assert report["T2_blocks_per_axis_edge"] == 3

    def test_blocks_per_axis_face(self, report):
        assert report["T2_blocks_per_axis_face"] == 4

    def test_axef_pairs_unique(self, report):
        assert report["T2_axef_pairs_unique"] is True

    def test_each_block_one_axis_edge(self, report):
        assert report["T2_each_block_one_axis_edge"] is True

    def test_each_block_one_axis_face(self, report):
        assert report["T2_each_block_one_axis_face"] is True

    def test_axis_edge_face_product(self, report):
        """16 ax-edges × 3 blocks + 12 ax-faces × 4 blocks = 48 each."""
        assert report["T2_axis_edges"] * report["T2_blocks_per_axis_edge"] == 48
        assert report["T2_axis_faces"] * report["T2_blocks_per_axis_face"] == 48


# ---------------------------------------------------------------------------
# T3: Tomotope-axis edge-face swap; both have 192 flags
# ---------------------------------------------------------------------------

class TestT3EdgeFaceSwap:
    def test_tomotope_fvector(self, report):
        fv = report["T3_tomotope_fvector"]
        assert fv["V"] == 4
        assert fv["E"] == 12
        assert fv["F"] == 16
        assert fv["C"] == 8

    def test_axis_fvector(self, report):
        fv = report["T3_axis_fvector"]
        assert fv["V"] == 1
        assert fv["E"] == 16
        assert fv["F"] == 12
        assert fv["C"] == 4

    def test_edge_face_swap(self, report):
        assert report["T3_edge_face_swap"] is True

    def test_shared_flags(self, report):
        assert report["T3_shared_flags"] == 192

    def test_tomotope_E_equals_axis_F(self, report):
        """E_tomo = 12 = F_axis."""
        assert report["T3_tomotope_fvector"]["E"] == report["T3_axis_fvector"]["F"] == 12

    def test_tomotope_F_equals_axis_E(self, report):
        """F_tomo = 16 = E_axis."""
        assert report["T3_tomotope_fvector"]["F"] == report["T3_axis_fvector"]["E"] == 16

    def test_tomotope_V_times_C_matches_axis(self, report):
        """Tomotope V=4, C=8 vs axis V=1, C=4 — dual pairing."""
        assert report["T3_tomotope_fvector"]["V"] == report["T3_axis_fvector"]["C"]

    def test_total_flags_192(self, report):
        assert report["T3_shared_flags"] == 192


# ---------------------------------------------------------------------------
# T4: Axis r0, r3 in tomotope G; axis r1, r2 not in G
# ---------------------------------------------------------------------------

class TestT4GeneratorMembership:
    def test_axis_r0_in_G(self, report):
        assert report["T4_axis_r0_in_G"] is True

    def test_axis_r3_in_G(self, report):
        assert report["T4_axis_r3_in_G"] is True

    def test_axis_r1_not_in_G(self, report):
        assert report["T4_axis_r1_not_in_G"] is True

    def test_axis_r2_not_in_G(self, report):
        assert report["T4_axis_r2_not_in_G"] is True

    def test_r0_r3_shared(self, report):
        assert report["T4_r0_r3_shared"] is True

    def test_boundary_generators_shared(self, report):
        """r0 and r3 (boundary generators) are shared; r1, r2 (internal) are twisted."""
        assert report["T4_axis_r0_in_G"] is True
        assert report["T4_axis_r3_in_G"] is True
        assert report["T4_axis_r1_not_in_G"] is True
        assert report["T4_axis_r2_not_in_G"] is True


# ---------------------------------------------------------------------------
# T5: Pure edge/face-swapper vs mixed twist
# ---------------------------------------------------------------------------

class TestT5GeneratorTwist:
    def test_tomo_r1_keepE(self, report):
        """Tomotope r1 swaps all edges (keepE=0)."""
        assert report["T5_tomo_r1_keepE"] == 0

    def test_tomo_r1_keepVFC(self, report):
        """Tomotope r1 fixes all V, F, C incidences (keepVFC=192)."""
        assert report["T5_tomo_r1_keepVFC"] == 192

    def test_tomo_r2_keepF(self, report):
        """Tomotope r2 swaps all faces (keepF=0)."""
        assert report["T5_tomo_r2_keepF"] == 0

    def test_tomo_r2_keepVEC(self, report):
        """Tomotope r2 fixes all V, E, C incidences (keepVEC=192)."""
        assert report["T5_tomo_r2_keepVEC"] == 192

    def test_axis_r1_keepE_tomo_zero(self, report):
        """Axis r1 (in tomotope coords) swaps all tomotope edges (keepE=0)."""
        assert report["T5_axis_r1_keepE_tomo"] == 0

    def test_axis_r1_keepF_tomo_zero(self, report):
        """Axis r1 (in tomotope coords) swaps all tomotope faces (keepF=0)."""
        assert report["T5_axis_r1_keepF_tomo"] == 0

    def test_axis_r1_not_pure_edge_swapper(self, report):
        """Axis r1 is NOT a pure edge-swapper (keepF != 192)."""
        assert report["T5_axis_r1_keepF_tomo"] != 192

    def test_generators_twisted(self, report):
        assert report["T5_generators_twisted"] is True

    def test_tomo_r1_pure_edge_swapper(self, report):
        """tomo r1: keepE=0 (swaps edges) but keepVFC=192 (pure edge-only action)."""
        assert report["T5_tomo_r1_keepE"] == 0
        assert report["T5_tomo_r1_keepVFC"] == 192

    def test_tomo_r2_pure_face_swapper(self, report):
        """tomo r2: keepF=0 (swaps faces) but keepVEC=192 (pure face-only action)."""
        assert report["T5_tomo_r2_keepF"] == 0
        assert report["T5_tomo_r2_keepVEC"] == 192


# ---------------------------------------------------------------------------
# T6: K voltage distribution
# ---------------------------------------------------------------------------

class TestT6KVoltageDistribution:
    def test_inverse_tests_ok(self, report):
        assert report["T6_inverse_tests_ok"] == 200

    def test_g8_g9_mostly_voltage0(self, report):
        assert report["T6_g8_g9_mostly_voltage0"] is True

    def test_order3_gens_carry_voltage(self, report):
        assert report["T6_order3_gens_carry_voltage"] is True

    def test_gen_order_g2(self, report):
        assert report["T6_gen_orders"]["g2"] == 3

    def test_gen_order_g3(self, report):
        assert report["T6_gen_orders"]["g3"] == 3

    def test_gen_order_g5(self, report):
        assert report["T6_gen_orders"]["g5"] == 3

    def test_gen_order_g8(self, report):
        assert report["T6_gen_orders"]["g8"] == 2

    def test_gen_order_g9(self, report):
        assert report["T6_gen_orders"]["g9"] == 2

    def test_g8_voltage0_count(self, report):
        """g8 has voltage=0 on 48/54 Schreier edges."""
        dist = report["T6_exp_dist"]["g8"]
        assert int(dist.get("0", 0)) == 48

    def test_g9_voltage0_count(self, report):
        """g9 has voltage=0 on 48/54 Schreier edges."""
        dist = report["T6_exp_dist"]["g9"]
        assert int(dist.get("0", 0)) == 48

    def test_g8_total_edges(self, report):
        """K Schreier graph has 54 edges per generator."""
        dist = report["T6_exp_dist"]["g8"]
        assert sum(int(v) for v in dist.values()) == 54

    def test_g2_has_nonzero_voltage(self, report):
        dist = report["T6_exp_dist"]["g2"]
        nonzero = sum(int(v) for k, v in dist.items() if k != "0")
        assert nonzero > 0

    def test_g3_has_nonzero_voltage(self, report):
        dist = report["T6_exp_dist"]["g3"]
        nonzero = sum(int(v) for k, v in dist.items() if k != "0")
        assert nonzero > 0

    def test_g5_has_nonzero_voltage(self, report):
        dist = report["T6_exp_dist"]["g5"]
        nonzero = sum(int(v) for k, v in dist.items() if k != "0")
        assert nonzero > 0


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

class TestAxisBlockTwistSummary:
    def test_summary_present(self, report):
        assert "summary" in report

    def test_summary_block_tomo(self, report):
        assert "4 blocks/edge" in report["summary"]["block_as_tomotope_ef_pair"]

    def test_summary_block_axis(self, report):
        assert "3 blocks/axis-edge" in report["summary"]["block_as_axis_ef_pair"]

    def test_summary_edge_face_swap(self, report):
        assert "E_tomo=12=F_axis" in report["summary"]["edge_face_swap"]

    def test_summary_shared_generators(self, report):
        assert "r0" in report["summary"]["shared_generators"]
        assert "r3" in report["summary"]["shared_generators"]

    def test_summary_twisted_generators(self, report):
        assert "r1" in report["summary"]["twisted_generators"]
        assert "r2" in report["summary"]["twisted_generators"]

    def test_summary_voltage_structure(self, report):
        assert "g2" in report["summary"]["K_voltage_structure"]
