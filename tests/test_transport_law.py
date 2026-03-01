#!/usr/bin/env python3
"""Tests for Pillar 97: 270-edge transport law."""

from __future__ import annotations

from THEORY_PART_CXCVII_TRANSPORT_LAW import analyse_transport


def test_transport_structure():
    s = analyse_transport()
    # T1: 270 edges, 5 generators
    assert s["T1_total_edges"] == 270
    assert s["T1_num_generators"] == 5
    assert all(v == 54 for v in s["T1_edges_per_generator"].values())


def test_involutions():
    s = analyse_transport()
    # T2: g8, g9 are involutions with 3 fixed points each
    assert set(s["T2_involution_generators"]) == {"g8", "g9"}
    assert s["T2_involution_fixed_points"]["g8"] == 3
    assert s["T2_involution_fixed_points"]["g9"] == 3


def test_order3():
    s = analyse_transport()
    # T3: g2, g3, g5 are non-involutions
    assert set(s["T3_order3_generators"]) == {"g2", "g3", "g5"}


def test_affine_det1():
    s = analyse_transport()
    # T4: all affine matrices have determinant 1
    assert s["T4_all_det_1"] is True
    # exactly 3 distinct matrices
    assert len(s["T4_affine_matrices"]) == 3


def test_cocycle_distribution():
    s = analyse_transport()
    # T5: cocycle sums to 270
    total = sum(s["T5_cocycle_global"].values())
    assert total == 270
    # most are trivial
    assert s["T5_cocycle_global"][0] > s["T5_cocycle_global"].get(1, 0)


def test_orient_strata():
    s = analyse_transport()
    # T7: 10 orient strata of 27 each
    assert s["T7_num_orient_strata"] == 10
    assert all(v == 27 for v in s["T7_orient_sizes"].values())
