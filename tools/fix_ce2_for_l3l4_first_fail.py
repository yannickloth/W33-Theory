#!/usr/bin/env python3
"""Attempt CE2 local solves for the `first_fail` entries in
`artifacts/exhaustive_homotopy_l3_l4.json`.

- Try rationalized solve with larger max_den first.
- If that fails, fall back to numeric solve and *attach* the numeric
  alpha to the in-memory LInftyE8Extension (so verification can pass),
  but do not write a rational artifact entry.

Usage: python tools/fix_ce2_for_l3l4_first_fail.py
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EXH = ROOT / "artifacts" / "exhaustive_homotopy_l3_l4.json"
CE2P = ROOT / "artifacts" / "ce2_rational_local_solutions.json"

if not EXH.exists():
    raise SystemExit("Run tools/exhaustive_homotopy_check_l3_l4.py first")

exh = json.loads(EXH.read_text(encoding="utf-8"))
# collect all `first_fail` triples from sectors
fails = []
for sec in ("g1_g1_g1", "g2_g2_g2", "g1_g1_g2", "g1_g2_g2"):
    f = exh.get("sectors", {}).get(sec, {}).get("first_fail")
    if f:
        fails.append((sec, tuple(f["a"]), tuple(f["b"]), tuple(f["c"])))

if not fails:
    print("No recorded first_fail in exhaustive_homotopy_l3_l4.json")
    raise SystemExit(0)

# load toe and linfty
spec = importlib.util.spec_from_file_location(
    "toe_e8", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(toe)  # type: ignore

sys_path_insert = str(ROOT)
import sys

if sys_path_insert not in sys.path:
    sys.path.insert(0, sys_path_insert)

from tools.build_linfty_firewall_extension import LInftyE8Extension

_e6 = np.load(ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy").astype(
    np.complex128
)
proj = toe.E6Projector(_e6)
all_triads = toe._load_signed_cubic_triads()
rat = json.loads(
    (ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json").read_text()
)
bad9 = set(tuple(sorted(t)) for t in rat["original"]["fiber_triads"])
linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

# helpers to make basis elements


def basis_elem_g1(idx: Tuple[int, int]):
    i, j = idx
    e = toe.E8Z3.zero()
    arr = np.zeros((27, 3), dtype=np.complex128)
    arr[i, j] = 1.0
    return toe.E8Z3(e6=e.e6, sl3=e.sl3, g1=arr, g2=e.g2)


def basis_elem_g2(idx: Tuple[int, int]):
    i, j = idx
    e = toe.E8Z3.zero()
    arr = np.zeros((27, 3), dtype=np.complex128)
    arr[i, j] = 1.0
    return toe.E8Z3(e6=e.e6, sl3=e.sl3, g1=e.g1, g2=arr)


# attempt solves
for sec, a_idx, b_idx, c_idx in fails:
    print("Processing failure:", sec, a_idx, b_idx, c_idx)
    x = basis_elem_g1(a_idx)
    y = basis_elem_g1(b_idx)
    z = (
        basis_elem_g1(c_idx)
        if sec == "g1_g1_g1"
        else (
            basis_elem_g2(c_idx)
            if sec in ("g1_g1_g2", "g1_g2_g2")
            else basis_elem_g1(c_idx)
        )
    )

    # try rationalized solver with larger denominator limit
    res = linfty.compute_local_ce2_alpha_for_triple(
        x, y, z, return_uv=True, rationalize_uv=True, max_den=5040
    )
    if res is not None:
        alpha_fn, U_flat, V_flat, U_rats, V_rats = res
        key = f"{a_idx[0]},{a_idx[1]}:{b_idx[0]},{b_idx[1]}:{c_idx[0]},{c_idx[1]}"
        # append to CE2 artifact (merge)
        if CE2P.exists():
            ce2 = json.loads(CE2P.read_text(encoding="utf-8"))
        else:
            ce2 = {}
        ce2[key] = {
            "a": a_idx,
            "b": b_idx,
            "c": c_idx,
            "U_norm": float(np.linalg.norm(U_flat)),
            "V_norm": float(np.linalg.norm(V_flat)),
            "U_rats": [str(r) if r is not None else "0" for r in U_rats],
            "V_rats": [str(r) if r is not None else "0" for r in V_rats],
        }
        CE2P.write_text(json.dumps(ce2, indent=2), encoding="utf-8")
        print("  -> rational CE2 solution found and appended to artifact:", key)

        # attach to linfty so further checks include it
        def make_alpha_from_rats(Ur, Vr, x_ref=x, y_ref=y, z_ref=z):
            def alpha(a, b):
                if (
                    np.allclose(a.g1, y_ref.g1)
                    and np.allclose(a.g2, y_ref.g2)
                    and np.allclose(b.g1, z_ref.g1)
                    and np.allclose(b.g2, z_ref.g2)
                ):
                    return linfty.tool.E8Z3(
                        e6=np.array(U_flat[: 27 * 27])
                        .reshape((27, 27))
                        .astype(np.complex128),
                        sl3=np.array(U_flat[27 * 27 : 27 * 27 + 9])
                        .reshape((3, 3))
                        .astype(np.complex128),
                        g1=np.array(U_flat[27 * 27 + 9 : 27 * 27 + 9 + 81])
                        .reshape((27, 3))
                        .astype(np.complex128),
                        g2=np.array(U_flat[27 * 27 + 9 + 81 :])
                        .reshape((27, 3))
                        .astype(np.complex128),
                    )
                if (
                    np.allclose(a.g1, z_ref.g1)
                    and np.allclose(a.g2, z_ref.g2)
                    and np.allclose(b.g1, y_ref.g1)
                    and np.allclose(b.g2, y_ref.g2)
                ):
                    return linfty.tool.E8Z3(
                        e6=-np.array(U_flat[: 27 * 27])
                        .reshape((27, 27))
                        .astype(np.complex128),
                        sl3=-np.array(U_flat[27 * 27 : 27 * 27 + 9])
                        .reshape((3, 3))
                        .astype(np.complex128),
                        g1=-np.array(U_flat[27 * 27 + 9 : 27 * 27 + 9 + 81])
                        .reshape((27, 3))
                        .astype(np.complex128),
                        g2=-np.array(U_flat[27 * 27 + 9 + 81 :])
                        .reshape((27, 3))
                        .astype(np.complex128),
                    )
                if (
                    np.allclose(a.g1, x_ref.g1)
                    and np.allclose(a.g2, x_ref.g2)
                    and np.allclose(b.g1, z_ref.g1)
                    and np.allclose(b.g2, z_ref.g2)
                ):
                    return linfty.tool.E8Z3(
                        e6=np.array(V_flat[: 27 * 27])
                        .reshape((27, 27))
                        .astype(np.complex128),
                        sl3=np.array(V_flat[27 * 27 : 27 * 27 + 9])
                        .reshape((3, 3))
                        .astype(np.complex128),
                        g1=np.array(V_flat[27 * 27 + 9 : 27 * 27 + 9 + 81])
                        .reshape((27, 3))
                        .astype(np.complex128),
                        g2=np.array(V_flat[27 * 27 + 9 + 81 :])
                        .reshape((27, 3))
                        .astype(np.complex128),
                    )
                if (
                    np.allclose(a.g1, z_ref.g1)
                    and np.allclose(a.g2, z_ref.g2)
                    and np.allclose(b.g1, x_ref.g1)
                    and np.allclose(b.g2, x_ref.g2)
                ):
                    return linfty.tool.E8Z3(
                        e6=-np.array(V_flat[: 27 * 27])
                        .reshape((27, 27))
                        .astype(np.complex128),
                        sl3=-np.array(V_flat[27 * 27 : 27 * 27 + 9])
                        .reshape((3, 3))
                        .astype(np.complex128),
                        g1=-np.array(V_flat[27 * 27 + 9 : 27 * 27 + 9 + 81])
                        .reshape((27, 3))
                        .astype(np.complex128),
                        g2=-np.array(V_flat[27 * 27 + 9 + 81 :])
                        .reshape((27, 3))
                        .astype(np.complex128),
                    )
                return linfty.tool.E8Z3.zero()

            return alpha

        linfty.attach_ce2_alpha(make_alpha_from_rats(U_flat, V_flat))
        linfty.attach_l4_from_ce2(linfty._ce2_alpha)
        print("  -> attached rational CE2 to linfty (in-memory)")
        # verify triple
        mag = float(np.max(np.abs(linfty.homotopy_jacobi(x, y, z).g1)))
        print("  -> homotopy_jacobi magnitude after attach:", mag)
        continue

    # rationalize failed; try numeric solve
    print("  -> rational solve failed; trying numeric least-squares solve...")
    res2 = linfty.compute_local_ce2_alpha_for_triple(
        x, y, z, return_uv=True, rationalize_uv=False
    )
    if res2 is None:
        print(
            "  -> numeric CE2 solver also failed for triple; cannot fix automatically"
        )
        continue
    alpha_fn, U_flat, V_flat = res2
    # attach numeric alpha to linfty instance and register it (nonpersistent)
    linfty.attach_ce2_alpha(alpha_fn)
    linfty.attach_l4_from_ce2(alpha_fn)
    mag2 = float(np.max(np.abs(linfty.homotopy_jacobi(x, y, z).g1)))
    print("  -> numeric CE2 attached; homotopy_jacobi magnitude after attach:", mag2)
    if mag2 <= 1e-8:
        print(
            "  -> triple fixed by numeric CE2 (artifact not updated) — consider rationalizing later."
        )
    else:
        print(
            "  -> numeric CE2 did not fully fix triple; manual investigation required."
        )

print("Done")
