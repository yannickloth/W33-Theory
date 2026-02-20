#!/usr/bin/env python3
"""Compute CE2 local solution for the first recorded failing triple and attach l4.

Purpose: lightweight alternative to full `assemble_exact_l4_from_local_ce2.py`
which performs an exhaustive scan. This script reads
`artifacts/exhaustive_homotopy_rationalized_l3.json`, extracts the
`first_fail` from sector `g1_g1_g2`, computes a rational CE2 U/V for that
triple (using `compute_local_ce2_alpha_for_triple`), writes a single-entry
`artifacts/ce2_rational_local_solutions.json`, attaches the resulting l4 to
`LInftyE8Extension` and verifies the triple is fixed.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any, Dict

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EXH = ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json"
OUT = ROOT / "artifacts" / "ce2_rational_local_solutions.json"

if not EXH.exists():
    raise SystemExit("Run tools/exhaustive_homotopy_check_rationalized_l3.py first")

exh = json.loads(EXH.read_text(encoding="utf-8"))
sector = exh.get("sectors", {}).get("g1_g1_g2", {})
ff = sector.get("first_fail")
if ff is None:
    raise SystemExit("No first_fail recorded in g1_g1_g2 sector")

# load toe and build LInftyE8Extension
spec = importlib.util.spec_from_file_location(
    "toe_e8", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(toe)  # type: ignore

proj = toe.E6Projector(
    np.load(ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy").astype(
        np.complex128
    )
)
all_triads = toe._load_signed_cubic_triads()
bad9 = set(
    tuple(sorted(t[:3]))
    for t in json.loads(
        (
            ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"
        ).read_text()
    )["original"]["fiber_triads"]
)

# make project root importable (so `import tools.*` works)
import sys

sys.path.insert(0, str(ROOT))

from tools.build_linfty_firewall_extension import LInftyE8Extension

linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)


# helper constructors (copied from exhaustive script)
def basis_elem_g1(idx):
    i, j = idx
    e = toe.E8Z3.zero()
    arr = np.zeros((27, 3), dtype=np.complex128)
    arr[i, j] = 1.0
    return toe.E8Z3(e6=e.e6, sl3=e.sl3, g1=arr, g2=e.g2)


def basis_elem_g2(idx):
    i, j = idx
    e = toe.E8Z3.zero()
    arr = np.zeros((27, 3), dtype=np.complex128)
    arr[i, j] = 1.0
    return toe.E8Z3(e6=e.e6, sl3=e.sl3, g1=e.g1, g2=arr)


# extract triple
a_idx = tuple(ff["a"])
b_idx = tuple(ff["b"])
c_idx = tuple(ff["c"])

x = basis_elem_g1(a_idx)
y = basis_elem_g1(b_idx)
z = basis_elem_g2(c_idx)

print("Computing local CE2 for triple", a_idx, b_idx, c_idx)
res = linfty.compute_local_ce2_alpha_for_triple(
    x, y, z, return_uv=True, rationalize_uv=True, max_den=720
)
if res is None:
    raise SystemExit("Local CE2 solver failed on the triple")
alpha_fn, U_flat, V_flat, U_rats, V_rats = res

# store single-entry artifact (merge into existing CE2 file instead of overwriting)
key = f"{a_idx[0]},{a_idx[1]}:{b_idx[0]},{b_idx[1]}:{c_idx[0]},{c_idx[1]}"
collected = {
    key: {
        "a": a_idx,
        "b": b_idx,
        "c": c_idx,
        "U_norm": float(np.linalg.norm(U_flat)),
        "V_norm": float(np.linalg.norm(V_flat)),
        "U_rats": [str(r) if r is not None else "0" for r in U_rats],
        "V_rats": [str(r) if r is not None else "0" for r in V_rats],
    }
}
# merge with any existing entries to avoid accidental overwrite
if OUT.exists():
    existing = json.loads(OUT.read_text(encoding="utf-8"))
else:
    existing = {}
existing.update(collected)
OUT.write_text(json.dumps(existing, indent=2), encoding="utf-8")
print("Wrote/merged CE2 artifact entry ->", OUT)

# build alpha_global from the single rational solution and attach
from tools.assemble_exact_l4_from_local_ce2 import flat_rats_to_E8Z3


def make_alpha_from_rats(Ur, Vr, x_ref=x, y_ref=y, z_ref=z):
    def alpha(a, b):
        if (
            np.allclose(a.g1, y_ref.g1)
            and np.allclose(a.g2, y_ref.g2)
            and np.allclose(b.g1, z_ref.g1)
            and np.allclose(b.g2, z_ref.g2)
        ):
            return flat_rats_to_E8Z3(toe, Ur)
        if (
            np.allclose(a.g1, z_ref.g1)
            and np.allclose(a.g2, z_ref.g2)
            and np.allclose(b.g1, y_ref.g1)
            and np.allclose(b.g2, y_ref.g2)
        ):
            return flat_rats_to_E8Z3(
                toe, [(-float(r)) if r is not None else 0.0 for r in Ur]
            )
        if (
            np.allclose(a.g1, x_ref.g1)
            and np.allclose(a.g2, x_ref.g2)
            and np.allclose(b.g1, z_ref.g1)
            and np.allclose(b.g2, z_ref.g2)
        ):
            return flat_rats_to_E8Z3(toe, Vr)
        if (
            np.allclose(a.g1, z_ref.g1)
            and np.allclose(a.g2, z_ref.g2)
            and np.allclose(b.g1, x_ref.g1)
            and np.allclose(b.g2, x_ref.g2)
        ):
            return flat_rats_to_E8Z3(
                toe, [(-float(r)) if r is not None else 0.0 for r in Vr]
            )
        return toe.E8Z3.zero()

    return alpha


alpha_global = make_alpha_from_rats(U_rats, V_rats)
linfty.attach_l4_from_ce2(alpha_global)
print("Attached l4 prototype from single CE2 local solution")

# verify the triple is fixed
hh = linfty.homotopy_jacobi(x, y, z)
mag = max(
    float(np.max(np.abs(hh.e6))) if hh.e6.size else 0.0,
    float(np.max(np.abs(hh.sl3))) if hh.sl3.size else 0.0,
    float(np.max(np.abs(hh.g1))) if hh.g1.size else 0.0,
    float(np.max(np.abs(hh.g2))) if hh.g2.size else 0.0,
)
print("homotopy_jacobi magnitude on triple after attach:", mag)
if mag > 1e-8:
    raise SystemExit("Triple not fixed after attaching l4")
print("Triple successfully fixed (<=1e-8)")
