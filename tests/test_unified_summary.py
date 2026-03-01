#!/usr/bin/env python3
"""Tests for Pillar 100: Unified algebraic summary."""

from __future__ import annotations

from THEORY_PART_CC_UNIFIED_SUMMARY import build_unified_summary


def test_unified_summary_structure():
    s = build_unified_summary()
    assert s["pillar_100_unified_summary"] is True
    assert s["tomotope"]["flags"] == 192
    assert s["tomotope"]["rank"] == 4


def test_N_structure():
    s = build_unified_summary()
    n = s["regular_subgroup_N"]
    assert n["order"] == 192
    assert n["centre_trivial"] is True
    assert n["num_conjugacy_classes"] == 14
    assert sum(n["class_sizes"]) == 192
    assert n["derived_order"] == 48
    assert n["abelianisation_order"] == 4
    assert n["order3_equals_derived"] is True


def test_transport_law():
    s = build_unified_summary()
    t = s["transport_law"]
    assert t["total_edges"] == 270
    assert t["num_generators"] == 5
    assert t["affine_matrices_all_det_1"] is True


def test_clifford():
    s = build_unified_summary()
    c = s["clifford_embedding"]
    assert c["N_embeds_in_Spin_dim"] == 4
    assert c["index_of_N"] == 3


def test_direct_product():
    s = build_unified_summary()
    d = s["direct_product"]
    assert d["is_direct_product"] is True
    assert d["closure_order"] == d["Gamma_order"] * d["H_order"]
