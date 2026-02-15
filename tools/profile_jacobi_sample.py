#!/usr/bin/env python3
"""Profile toe._jacobi screening on a sample of g1_g1_g1 triples.

Run with:
  python -m cProfile -o checks/prof_jacobi_sample.prof tools/profile_jacobi_sample.py
Then examine with: python -m pstats checks/prof_jacobi_sample.prof
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import importlib

# load toe and linfty (fast-path similar to exhaustive script)
from tools import toe_e8_z3graded_bracket_jacobi as toe_mod

E6_BASIS = np.load(
    ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
).astype(np.complex128)
proj = toe_mod.E6Projector(E6_BASIS)
all_triads = toe_mod._load_signed_cubic_triads()

from tools.build_linfty_firewall_extension import (
    LInftyE8Extension,
    _load_bad9,
    _load_bracket_tool,
)

toe = _load_bracket_tool()
proj = toe.E6Projector(E6_BASIS)
bad9 = _load_bad9()
linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)
# attach l4 if available (do not assemble here)
symp = ROOT / "artifacts" / "l4_symbolic_constants.json"
if symp.exists():
    linfty.attach_l4_from_symbolic_constants(symp)

# sample g1 triples
from tools.exhaustive_homotopy_check_l3_l4 import basis_elem_g1, flat_mag, make_g1_basis

g1_idx = make_g1_basis(toe)
triples = list(itertools.combinations(g1_idx, 3))[:1000]

print(f"Profiling {len(triples)} g1_g1_g1 triples (toe._jacobi screening)")

for a_idx, b_idx, c_idx in triples:
    x = (lambda idx: toe.E8Z3.zero().__class__.zero() or None)(None)
    # use existing basis_elem_g1 from exhaustive helper if available
    from tools.exhaustive_homotopy_check_l3_l4 import basis_elem_g1

    x = basis_elem_g1(toe, a_idx)
    y = basis_elem_g1(toe, b_idx)
    z = basis_elem_g1(toe, c_idx)
    # run the screening jacobi
    j = toe._jacobi(linfty.br_l2, x, y, z)
    _ = flat_mag(j)

print("Sample screening complete")

# timing: safe bulk homotopy_jacobi sampling (avoid IndexError by cycling triples)
from time import perf_counter

N = 1000
if len(triples) >= N:
    sample_triples = triples[:N]
else:
    from itertools import cycle, islice

    sample_triples = list(islice(cycle(triples), N))

# warm-up (compile lazy paths)
_basis_elem = basis_elem_g1
_a, _b, _c = sample_triples[0]
_ = linfty.homotopy_jacobi(
    _basis_elem(toe, _a), _basis_elem(toe, _b), _basis_elem(toe, _c)
)

start = perf_counter()
for a_idx, b_idx, c_idx in sample_triples:
    x = _basis_elem(toe, a_idx)
    y = _basis_elem(toe, b_idx)
    z = _basis_elem(toe, c_idx)
    _ = linfty.homotopy_jacobi(x, y, z)
elapsed = perf_counter() - start
print(
    f"Timed {len(sample_triples)} homotopy_jacobi calls: {elapsed:.3f}s ({elapsed/len(sample_triples):.6f}s/call)"
)
