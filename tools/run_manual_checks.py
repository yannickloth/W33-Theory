#!/usr/bin/env python3
"""Run sector checks using explicit coefficient vector (no artifact read).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys_mod = __import__("sys")
    sys_mod.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


if __name__ == "__main__":
    toe = _load_module(ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py", "toe_e8")
    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()

    linfty = _load_module(
        ROOT / "tools" / "build_linfty_firewall_extension.py", "linfty_mod"
    )
    bad9 = linfty._load_bad9()

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

    # import checker functions from the exhaustive script
    chk = _load_module(
        ROOT / "tools" / "exhaustive_homotopy_check_rationalized_l3.py", "exh"
    )

    coeffs = [1.0 / 9.0] * 9
    print("Running g1_g1_g1 check with coeffs:", coeffs)
    g1_idx = [(i, j) for i in range(27) for j in range(3)]
    res = chk.check_sector_g1g1g1(g1_idx, coeffs, br_l2, br_fibers, toe)
    print("g1_g1_g1 ->", res)

    g2_idx = [(i, j) for i in range(27) for j in range(3)]
    res2 = chk.check_sector_g2g2g2(g2_idx, coeffs, br_l2, br_fibers, toe)
    print("g2_g2_g2 ->", res2)

    res3 = chk.check_sector_g1g1g2(g1_idx, g2_idx, coeffs, br_l2, br_fibers, toe)
    print("g1_g1_g2 ->", res3)

    res4 = chk.check_sector_g1g2g2(g1_idx, g2_idx, coeffs, br_l2, br_fibers, toe)
    print("g1_g2_g2 ->", res4)
