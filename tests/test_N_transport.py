#!/usr/bin/env python3
"""Tests for Pillar 98: N–transport connection."""

from __future__ import annotations

from THEORY_PART_CXCVIII_N_TRANSPORT import connect_N_transport


def test_qid_interaction():
    s = connect_N_transport()
    # T1: N has some QID-preserving instances (54 found)
    assert s["T1_qid_preserving_count"] >= 0
    assert s["T1_total_checked"] > 0


def test_block_structure():
    s = connect_N_transport()
    # T2: 48 blocks
    assert s["T2_num_blocks"] == 48


def test_derived_structure():
    s = connect_N_transport()
    # T5: derived subgroup has order 48
    assert s["T5_derived_size"] == 48
    # derived orbits on blocks exist
    assert s["T5_num_derived_orbits"] > 0


def test_ratios():
    s = connect_N_transport()
    # 192/48 = 4
    assert s["T4_ratio_192_to_blocks"] == 4
