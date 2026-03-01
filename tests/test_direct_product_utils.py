#!/usr/bin/env python3
"""Tests for the direct product helper functions."""

from __future__ import annotations

import json
from pathlib import Path

from THEORY_PART_CXCIV_DIRECT_PRODUCT_UTILS import direct_product_closure
from THEORY_PART_CXCVII_AUT_NORMALISER import load_permutations, build_gamma
from THEORY_PART_CXCVI_TOMOTOPE_AUTOMORPHISMS import (
    compute_automorphisms,
    build_graph,
    load_r_generators,
)


def load_Gamma_H():
    perms = load_permutations()
    Gamma = build_gamma(perms)
    G = build_graph(load_r_generators())
    autos = compute_automorphisms(G)
    H = [tuple(autos[i][j] for j in range(192)) for i in range(len(autos))]
    return Gamma, H


def test_direct_product_size():
    Gamma, H = load_Gamma_H()
    closure = direct_product_closure(Gamma, H)
    assert len(closure) == len(Gamma) * len(H)
    # ensure no duplicates
    assert len(set(closure)) == len(closure)


def test_contains_Gamma_and_H():
    Gamma, H = load_Gamma_H()
    closure = direct_product_closure(Gamma, H)
    # any g in Gamma should appear as g*id
    for g in Gamma:
        assert g in closure
    # any h in H should appear as id*h
    idp = tuple(range(192))
    for h in H:
        assert h in closure
