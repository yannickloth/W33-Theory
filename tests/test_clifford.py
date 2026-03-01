#!/usr/bin/env python3
"""Tests for Pillar 99: Clifford algebra embedding."""

from __future__ import annotations

from THEORY_PART_CXCIX_CLIFFORD import compute_clifford_data, CliffordElement


def test_clifford_basics():
    s = compute_clifford_data()
    # T1: Cl(2, F_3) has dimension 4
    assert s["T1_Cl2_dim"] == 4
    # generators anticommute
    assert s["T1_anticommute"] is True


def test_unit_vectors():
    s = compute_clifford_data()
    # 4 unit vectors in F_3^2 (Euclidean form a^2+b^2=1 mod 3)
    assert s["T2_num_unit_vectors"] == 4


def test_spin_embedding():
    s = compute_clifford_data()
    # N should embed in Spin(4, F_3)
    assert 4 in s["T4_N_embeds_in"]
    assert s["T4_smallest_embedding_dim"] == 4
    # index 3
    assert s["T5_index_in_Spin4"] == 3


def test_clifford_element_algebra():
    # Basic algebra checks
    n = 2
    e0 = CliffordElement.generator(n, 0)
    e1 = CliffordElement.generator(n, 1)
    one = CliffordElement.scalar(n, 1)

    # e_i^2 = 1
    assert e0 * e0 == one
    assert e1 * e1 == one

    # anticommutation: e0*e1 + e1*e0 = 0
    assert (e0 * e1 + e1 * e0).is_zero()
