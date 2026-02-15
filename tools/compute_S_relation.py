#!/usr/bin/env python3
"""Compute relation between Σ_T S_T and the Jacobi vector for a chosen triple.

Prints ratios and writes artifacts/inspect_S_relation.json.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import List

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "inspect_S_relation.json"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys_mod = __import__("sys")
    sys_mod.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def flatten(e):
    return np.concatenate(
        [e.e6.reshape(-1), e.sl3.reshape(-1), e.g1.reshape(-1), e.g2.reshape(-1)]
    )


def main():
    toe = _load_module(ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py", "toe_e8")
    linfty = _load_module(
        ROOT / "tools" / "build_linfty_firewall_extension.py", "linfty_mod"
    )

    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)

    all_triads = toe._load_signed_cubic_triads()
    bad9 = linfty._load_bad9()
    fiber_triads = [t for t in all_triads if tuple(sorted(t[:3])) in bad9]

    br_l2 = toe.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=[t for t in all_triads if tuple(sorted(t[:3])) not in bad9],
        scale_g1g1=1.0,
        scale_g2g2=-1.0 / 6.0,
        scale_e6=1.0,
        scale_sl3=1.0 / 6.0,
    )

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

    from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1

    a_idx = (0, 0)
    b_idx = (1, 1)
    c_idx = (21, 2)

    x = basis_elem_g1(toe, a_idx)
    y = basis_elem_g1(toe, b_idx)
    z = basis_elem_g1(toe, c_idx)

    J = toe._jacobi(br_l2, x, y, z)
    Jf = flatten(J)

    Scols = []
    for brf in br_fibers:
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
        Scols.append(flatten(S))

    Ssum = sum(Scols)

    nz = np.where(np.abs(Jf) > 1e-12)[0]
    ratios = (Ssum[nz] / Jf[nz]).tolist()

    per_triads = []
    for i, S in enumerate(Scols):
        r = (S[nz] / Jf[nz]).tolist()
        per_triads.append(
            {
                "triad_index": i,
                "mean_ratio_real": float(np.mean(np.real(S[nz] / Jf[nz]))),
                "max_abs": float(np.max(np.abs(S))),
            }
        )

    out = {
        "J_max_e6": float(np.max(np.abs(J.e6))),
        "J_nonzero_count": int(len(nz)),
        "sum_ratio_mean_real": float(np.mean(np.real(ratios))) if len(ratios) else None,
        "per_triads": per_triads,
        "Ssum_nonzero_count": int(np.count_nonzero(np.abs(Ssum) > 1e-12)),
    }

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
