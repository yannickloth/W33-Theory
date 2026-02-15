#!/usr/bin/env python3
"""Verify a candidate coefficient vector (from artifact) by running the same
sector checks as exhaustive_homotopy_check_rationalized_l3.py but *using the
coeffs as read* (no sign conversion).

Usage: python -m tools.verify_candidate_coeffs
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys_mod = __import__("sys")
    sys_mod.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def flat_mag(e) -> float:
    return float(
        max(
            0.0 if e.e6.size == 0 else np.max(np.abs(e.e6)),
            0.0 if e.sl3.size == 0 else np.max(np.abs(e.sl3)),
            0.0 if e.g1.size == 0 else np.max(np.abs(e.g1)),
            0.0 if e.g2.size == 0 else np.max(np.abs(e.g2)),
        )
    )


def make_g1_basis(toe_mod):
    return [(i, j) for i in range(27) for j in range(3)]


def make_g2_basis(toe_mod):
    return [(i, j) for i in range(27) for j in range(3)]


def basis_elem_g1(toe_mod, idx):
    i, j = idx
    e = toe_mod.E8Z3.zero()
    arr = np.zeros((27, 3), dtype=np.complex128)
    arr[i, j] = 1.0
    return toe_mod.E8Z3(e6=e.e6, sl3=e.sl3, g1=arr, g2=e.g2)


def basis_elem_g2(toe_mod, idx):
    i, j = idx
    e = toe_mod.E8Z3.zero()
    arr = np.zeros((27, 3), dtype=np.complex128)
    arr[i, j] = 1.0
    return toe_mod.E8Z3(e6=e.e6, sl3=e.sl3, g1=e.g1, g2=arr)


def assemble_l3_total_from_coeffs(coeffs, br_l2, br_fibers, toe_mod, x, y, z):
    l3_total = toe_mod.E8Z3.zero()
    for c, brf in zip(coeffs, br_fibers):
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
        l3_total = l3_total + S.scale(-float(c))
    return l3_total


def check_sector_g1g1g1(g1_basis_idx, coeffs, br_l2, br_fibers, toe_mod):
    import itertools

    tested = 0
    max_j = 0.0
    max_total = 0.0
    for a_idx, b_idx, c_idx in itertools.combinations(g1_basis_idx, 3):
        x = basis_elem_g1(toe_mod, a_idx)
        y = basis_elem_g1(toe_mod, b_idx)
        z = basis_elem_g1(toe_mod, c_idx)
        j_l2 = toe_mod._jacobi(br_l2, x, y, z)
        mag_j = flat_mag(j_l2)
        tested += 1
        max_j = max(max_j, mag_j)
        if mag_j < 1e-12:
            continue
        l3_total = assemble_l3_total_from_coeffs(
            coeffs, br_l2, br_fibers, toe_mod, x, y, z
        )
        total = toe_mod.E8Z3(
            e6=j_l2.e6 + l3_total.e6,
            sl3=j_l2.sl3 + l3_total.sl3,
            g1=j_l2.g1 + l3_total.g1,
            g2=j_l2.g2 + l3_total.g2,
        )
        mag_tot = flat_mag(total)
        max_total = max(max_total, mag_tot)
        if mag_tot > 1e-8:
            return {
                "passed": False,
                "tested": tested,
                "first_fail": {
                    "a": a_idx,
                    "b": b_idx,
                    "c": c_idx,
                    "mag_j": mag_j,
                    "mag_tot": mag_tot,
                },
                "max_j": max_j,
                "max_total": max_total,
            }
    return {"passed": True, "tested": tested, "max_j": max_j, "max_total": max_total}


def main():
    data = json.loads(IN.read_text(encoding="utf-8"))
    coeffs = data.get("rationalized_coeffs_float") or data.get("original", {}).get(
        "coeffs"
    )
    print("Loaded coeffs:", coeffs)

    toe = _load_module(ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py", "toe_e8")
    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = (
        set(tuple(sorted(t)) for t in data["original"]["fiber_triads"])
        if "original" in data
        else set()
    )

    br_l2 = toe.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=[t for t in all_triads if tuple(sorted(t[:3])) not in bad9],
        scale_g1g1=1.0,
        scale_g2g2=-1.0 / 6.0,
        scale_e6=1.0,
        scale_sl3=1.0 / 6.0,
    )
    fiber_triads = [t for t in all_triads if tuple(sorted(t[:3])) in bad9]
    br_fibers = [
        toe.E8Z3Bracket(
            e6_projector=proj,
            cubic_triads=[T],
            scale_g1g1=1.0,
            scale_g2g2=-1.0 / 6.0,
            scale_e6=1.0,
            scale_sl3=1.0 / 6.0,
        )
        for T in fiber_triads
    ]

    g1_idx = make_g1_basis(toe)

    res_g1 = check_sector_g1g1g1(g1_idx, coeffs, br_l2, br_fibers, toe)
    print("g1_g1_g1 ->", res_g1)


if __name__ == "__main__":
    main()
