#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick exhaustive homotopy (l2 + l3 + l4) verifier that uses the
symbolic `l4` and assembled `ce2` artifacts already present.

This intentionally skips running the full `assemble_exact_l4_from_local_ce2`
step (which can be expensive) and instead reuses artifacts so the check
finishes quickly.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Dict

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

# load minimal helpers
spec_b = importlib.util.spec_from_file_location(
    "build_linfty", ROOT / "tools" / "build_linfty_firewall_extension.py"
)
build = importlib.util.module_from_spec(spec_b)
spec_b.loader.exec_module(build)

spec_toe = importlib.util.spec_from_file_location(
    "toe", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(spec_toe)
spec_toe.loader.exec_module(toe)

# setup projector / linfty
e6_basis = np.load(ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy").astype(np.complex128)
proj = toe.E6Projector(e6_basis)
all_triads = toe._load_signed_cubic_triads()
rat = json.loads((ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json").read_text())
bad9 = set(tuple(sorted(t)) for t in rat["original"]["fiber_triads"])
linfty = build.LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

# attach symbolic l4 (if present)
symp = ROOT / "artifacts" / "l4_symbolic_constants.json"
if symp.exists():
    linfty.attach_l4_from_symbolic_constants(symp)

# ensure CE2 coboundary is attached (explicit fallback)
ce2p = ROOT / "artifacts" / "ce2_rational_local_solutions.json"
if ce2p.exists():
    ce2 = json.loads(ce2p.read_text(encoding="utf-8"))

    from fractions import Fraction

    def flat_to_e8(vec_flat):
        N = 27 * 27
        e6 = vec_flat[:N].reshape((27, 27)).astype(np.complex128)
        off = N
        sl3 = vec_flat[off : off + 9].reshape((3, 3)).astype(np.complex128)
        off += 9
        g1 = vec_flat[off : off + 81].reshape((27, 3)).astype(np.complex128)
        off += 81
        g2 = vec_flat[off : off + 81].reshape((27, 3)).astype(np.complex128)
        return toe.E8Z3(e6=e6, sl3=sl3, g1=g1, g2=g2)

    from tools.exhaustive_homotopy_check_rationalized_l3 import (
        basis_elem_g1,
        basis_elem_g2,
    )

    def alpha_global(a, b):
        acc = toe.E8Z3.zero()
        for k, e in ce2.items():
            a_idx = tuple(e["a"])
            b_idx = tuple(e["b"])
            c_idx = tuple(e["c"])
            U_rats = [Fraction(s) if s != "0" else None for s in e.get("U_rats", [])]
            V_rats = [Fraction(s) if s != "0" else None for s in e.get("V_rats", [])]
            U_num = np.array([float(fr) if fr is not None else 0.0 for fr in U_rats], dtype=np.complex128)
            V_num = np.array([float(fr) if fr is not None else 0.0 for fr in V_rats], dtype=np.complex128)
            U_e8 = flat_to_e8(U_num)
            V_e8 = flat_to_e8(V_num)

            if np.allclose(a.g1, basis_elem_g1(toe, b_idx).g1) and np.allclose(b.g2, basis_elem_g2(toe, c_idx).g2):
                acc = acc + U_e8
            if np.allclose(a.g1, basis_elem_g1(toe, c_idx).g1) and np.allclose(b.g2, basis_elem_g2(toe, b_idx).g2):
                acc = acc - U_e8
            if np.allclose(a.g1, basis_elem_g1(toe, a_idx).g1) and np.allclose(b.g2, basis_elem_g2(toe, c_idx).g2):
                acc = acc + V_e8
            if np.allclose(a.g1, basis_elem_g1(toe, c_idx).g1) and np.allclose(b.g2, basis_elem_g2(toe, a_idx).g2):
                acc = acc - V_e8
        return acc

    linfty.attach_l4_from_ce2(alpha_global)

# quick exhaustive checks (only triples where Jacobi(l2) != 0 are tested)
from tools.exhaustive_homotopy_check_l3_l4 import (
    basis_elem_g1,
    basis_elem_g2,
    make_g1_basis,
    make_g2_basis,
)

TOL_J = 1e-12
TOL_FAIL = 1e-8

out: Dict[str, Dict] = {}

# evaluator
def eval_triple(x, y, z):
    hj = linfty.homotopy_jacobi(x, y, z)
    return float(
        max(
            np.max(np.abs(hj.e6)) if hj.e6.size else 0.0,
            np.max(np.abs(hj.sl3)) if hj.sl3.size else 0.0,
            np.max(np.abs(hj.g1)) if hj.g1.size else 0.0,
            np.max(np.abs(hj.g2)) if hj.g2.size else 0.0,
        )
    )

# run sectors
g1_idx = make_g1_basis(toe)
g2_idx = make_g2_basis(toe)

# g1_g1_g1
tested = 0
max_j = 0.0
max_total = 0.0
first_fail = None
for a_idx, b_idx, c_idx in __import__("itertools").combinations(g1_idx, 3):
    x = basis_elem_g1(toe, a_idx)
    y = basis_elem_g1(toe, b_idx)
    z = basis_elem_g1(toe, c_idx)
    j_l2 = toe._jacobi(linfty.br_l2, x, y, z)
    mag_j = max(
        np.max(np.abs(j_l2.e6)) if j_l2.e6.size else 0.0,
        np.max(np.abs(j_l2.sl3)) if j_l2.sl3.size else 0.0,
        np.max(np.abs(j_l2.g1)) if j_l2.g1.size else 0.0,
        np.max(np.abs(j_l2.g2)) if j_l2.g2.size else 0.0,
    )
    tested += 1
    max_j = max(max_j, mag_j)
    if mag_j < TOL_J:
        continue
    mag_tot = eval_triple(x, y, z)
    max_total = max(max_total, mag_tot)
    if mag_tot > TOL_FAIL:
        first_fail = {"a": a_idx, "b": b_idx, "c": c_idx, "mag_j": mag_j, "mag_tot": mag_tot}
        break
out["g1_g1_g1"] = {"passed": first_fail is None, "tested": tested, "first_fail": first_fail, "max_j": max_j, "max_total": max_total}

# g2_g2_g2
tested = 0
max_j = 0.0
max_total = 0.0
first_fail = None
for a_idx, b_idx, c_idx in __import__("itertools").combinations(g2_idx, 3):
    x = basis_elem_g2(toe, a_idx)
    y = basis_elem_g2(toe, b_idx)
    z = basis_elem_g2(toe, c_idx)
    j_l2 = toe._jacobi(linfty.br_l2, x, y, z)
    mag_j = max(
        np.max(np.abs(j_l2.e6)) if j_l2.e6.size else 0.0,
        np.max(np.abs(j_l2.sl3)) if j_l2.sl3.size else 0.0,
        np.max(np.abs(j_l2.g1)) if j_l2.g1.size else 0.0,
        np.max(np.abs(j_l2.g2)) if j_l2.g2.size else 0.0,
    )
    tested += 1
    max_j = max(max_j, mag_j)
    if mag_j < TOL_J:
        continue
    mag_tot = eval_triple(x, y, z)
    max_total = max(max_total, mag_tot)
    if mag_tot > TOL_FAIL:
        first_fail = {"a": a_idx, "b": b_idx, "c": c_idx, "mag_j": mag_j, "mag_tot": mag_tot}
        break
out["g2_g2_g2"] = {"passed": first_fail is None, "tested": tested, "first_fail": first_fail, "max_j": max_j, "max_total": max_total}

# g1_g1_g2
tested = 0
max_j = 0.0
max_total = 0.0
first_fail = None
for a_idx, b_idx in __import__("itertools").combinations(g1_idx, 2):
    for c_idx in g2_idx:
        x = basis_elem_g1(toe, a_idx)
        y = basis_elem_g1(toe, b_idx)
        z = basis_elem_g2(toe, c_idx)
        j_l2 = toe._jacobi(linfty.br_l2, x, y, z)
        mag_j = max(
            np.max(np.abs(j_l2.e6)) if j_l2.e6.size else 0.0,
            np.max(np.abs(j_l2.sl3)) if j_l2.sl3.size else 0.0,
            np.max(np.abs(j_l2.g1)) if j_l2.g1.size else 0.0,
            np.max(np.abs(j_l2.g2)) if j_l2.g2.size else 0.0,
        )
        tested += 1
        max_j = max(max_j, mag_j)
        if mag_j < TOL_J:
            continue
        mag_tot = eval_triple(x, y, z)
        max_total = max(max_total, mag_tot)
        if mag_tot > TOL_FAIL:
            first_fail = {"a": a_idx, "b": b_idx, "c": c_idx, "mag_j": mag_j, "mag_tot": mag_tot}
            break
    if first_fail:
        break
out["g1_g1_g2"] = {"passed": first_fail is None, "tested": tested, "first_fail": first_fail, "max_j": max_j, "max_total": max_total}

# g1_g2_g2
tested = 0
max_j = 0.0
max_total = 0.0
first_fail = None
for a_idx in g1_idx:
    for b_idx, c_idx in __import__("itertools").combinations(g2_idx, 2):
        x = basis_elem_g1(toe, a_idx)
        y = basis_elem_g2(toe, b_idx)
        z = basis_elem_g2(toe, c_idx)
        j_l2 = toe._jacobi(linfty.br_l2, x, y, z)
        mag_j = max(
            np.max(np.abs(j_l2.e6)) if j_l2.e6.size else 0.0,
            np.max(np.abs(j_l2.sl3)) if j_l2.sl3.size else 0.0,
            np.max(np.abs(j_l2.g1)) if j_l2.g1.size else 0.0,
            np.max(np.abs(j_l2.g2)) if j_l2.g2.size else 0.0,
        )
        tested += 1
        max_j = max(max_j, mag_j)
        if mag_j < TOL_J:
            continue
        mag_tot = eval_triple(x, y, z)
        max_total = max(max_total, mag_tot)
        if mag_tot > TOL_FAIL:
            first_fail = {"a": a_idx, "b": b_idx, "c": c_idx, "mag_j": mag_j, "mag_tot": mag_tot}
            break
    if first_fail:
        break
out["g1_g2_g2"] = {"passed": first_fail is None, "tested": tested, "first_fail": first_fail, "max_j": max_j, "max_total": max_total}

# persist
open(ROOT / 'artifacts' / 'exhaustive_homotopy_l3_l4.json','w',encoding='utf-8').write(json.dumps({'candidate_coeffs': [float(1/9.0)], 'sectors': out}, indent=2))
print(json.dumps(out, indent=2))

``` (truncated) -
