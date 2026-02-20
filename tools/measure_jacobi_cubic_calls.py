#!/usr/bin/env python3
"""Measure how many `cubic_sym` calls occur during a single `toe._jacobi`.
"""
from __future__ import annotations

import importlib.util
import sys
import time
from pathlib import Path

# make project root importable when running script directly
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location(
    "toe", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(toe)

# monkeypatch counter
_counter = {"calls": 0}
_orig = toe.E8Z3Bracket.cubic_sym


def _counting_cubic_sym(self, u, v, *, scale):
    _counter["calls"] += 1
    return _orig(self, u, v, scale=scale)


# apply monkeypatch
toe.E8Z3Bracket.cubic_sym = _counting_cubic_sym

# build a bracket + sample triple (use the same helpers as the exhaustive check)
from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1, basis_elem_g2

proj = toe.E6Projector(
    np.load(ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy").astype(
        np.complex128
    )
)
all_triads = toe._load_signed_cubic_triads()
bad9 = set(
    tuple(sorted(t[:3]))
    for t in __import__("json").loads(
        (
            ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"
        ).read_text()
    )["original"]["fiber_triads"]
)
br = toe.E8Z3Bracket(
    e6_projector=proj,
    cubic_triads=[t for t in all_triads if tuple(sorted(t[:3])) not in bad9],
)

# choose a known-heavy triple
x = basis_elem_g1(toe, (0, 0))
y = basis_elem_g1(toe, (17, 1))
z = basis_elem_g2(toe, (3, 0))

_counter["calls"] = 0
t0 = time.perf_counter()
J = toe._jacobi(br, x, y, z)
t1 = time.perf_counter()
print("jacobi time:", t1 - t0)
print("cubic_sym calls during this jacobi:", _counter["calls"])

# also measure a batch to get rate
N = 100
_counter["calls"] = 0
t0 = time.perf_counter()
for _ in range(N):
    _ = toe._jacobi(br, x, y, z)
t1 = time.perf_counter()
print(f"{N} jacobi calls in {t1-t0:.4f}s => {N/(t1-t0):.1f} calls/s")
print("avg cubic_sym calls per jacobi:", _counter["calls"] / N)
