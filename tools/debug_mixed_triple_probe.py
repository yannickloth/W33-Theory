#!/usr/bin/env python3
"""Debug probe: print Jacobi J and per-triad S overlaps for the mixed failing triple."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
# load toe
spec = importlib.util.spec_from_file_location(
    "toe", "tools/toe_e8_z3graded_bracket_jacobi.py"
)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)
# import basis_elem_g1 from module file (avoid package import issues)
exh_spec = importlib.util.spec_from_file_location(
    "exhaustive_hj", ROOT / "tools" / "exhaustive_homotopy_check_rationalized_l3.py"
)
exh_module = importlib.util.module_from_spec(exh_spec)
sys.modules[exh_spec.name] = exh_module
exh_spec.loader.exec_module(exh_module)
basis_elem_g1 = exh_module.basis_elem_g1
# prepare
e6_basis = np.load(
    ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
).astype(np.complex128)
proj = mod.E6Projector(e6_basis)
all_triads = mod._load_signed_cubic_triads()
# load bad9 via dynamic module loader (avoid package import)
linfty_spec = importlib.util.spec_from_file_location(
    "linfty_mod", ROOT / "tools" / "build_linfty_firewall_extension.py"
)
linfty_mod = importlib.util.module_from_spec(linfty_spec)
sys.modules[linfty_spec.name] = linfty_mod
linfty_spec.loader.exec_module(linfty_mod)
bad9 = linfty_mod._load_bad9()
br_l2 = mod.E8Z3Bracket(
    e6_projector=proj,
    cubic_triads=[t for t in all_triads if tuple(sorted(t[:3])) not in bad9],
    scale_g1g1=1.0,
    scale_g2g2=-1.0 / 6.0,
    scale_e6=1.0,
    scale_sl3=1.0 / 6.0,
)
# failing triple
ft = json.load(open(ROOT / "artifacts" / "mixed_triple_lsq_correction.json"))[
    "failed_triple"
]
a = tuple(ft["a"])
b = tuple(ft["b"])
c = tuple(ft["c"])
print("failed triple =", a, b, c)
x = basis_elem_g1(mod, a)
y = basis_elem_g1(mod, b)
z = basis_elem_g1(mod, c)
J = mod._jacobi(br_l2, x, y, z)
print(
    "J max abs (e6,sl3,g1,g2)=",
    np.max(np.abs(J.e6)),
    np.max(np.abs(J.sl3)),
    np.max(np.abs(J.g1)),
    np.max(np.abs(J.g2)),
)
Jflat = np.concatenate(
    [J.e6.reshape(-1), J.sl3.reshape(-1), J.g1.reshape(-1), J.g2.reshape(-1)]
)
# per-triad S contributions
fiber_triads = [t for t in all_triads if tuple(sorted(t[:3])) in bad9]
for i, T in enumerate(fiber_triads):
    brf = mod.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=[T],
        scale_g1g1=1.0,
        scale_g2g2=-1.0 / 6.0,
        scale_e6=1.0,
        scale_sl3=1.0 / 6.0,
    )
    j1 = brf.bracket(x, br_l2.bracket(y, z))
    j2 = brf.bracket(y, br_l2.bracket(z, x))
    j3 = brf.bracket(z, br_l2.bracket(x, y))
    f1 = br_l2.bracket(brf.bracket(x, y), z)
    f2 = br_l2.bracket(brf.bracket(y, z), x)
    f3 = br_l2.bracket(brf.bracket(z, x), y)
    ff1 = brf.bracket(x, brf.bracket(y, z))
    ff2 = brf.bracket(y, brf.bracket(z, x))
    ff3 = brf.bracket(z, brf.bracket(x, y))
    S = j1 + j2 + j3 + f1 + f2 + f3 + ff1 + ff2 + ff3
    Sflat = np.concatenate(
        [S.e6.reshape(-1), S.sl3.reshape(-1), S.g1.reshape(-1), S.g2.reshape(-1)]
    )
    nz = np.where(np.abs(Sflat) > 1e-12)[0]
    overlap_with_J = np.where(np.abs(Sflat * Jflat) > 1e-12)[0]
    print(
        f"triad {i} {T[:3]}: max|S.e6|={np.max(np.abs(S.e6)):.6g}, #nonzero_S={len(nz)}, overlap_with_J={len(overlap_with_J)}"
    )
