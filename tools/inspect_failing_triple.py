#!/usr/bin/env python3
"""Inspect which fiber triads contribute to a failing g1_g1_g1 triple.

Writes a small JSON summary to artifacts/failing_triple_inspect.json for use by
other scripts.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import List

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "failing_triple_inspect.json"


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

    # failing triple from exhaustive check
    from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1

    a_idx = (0, 0)
    b_idx = (1, 1)
    c_idx = (21, 2)

    x = basis_elem_g1(toe, a_idx)
    y = basis_elem_g1(toe, b_idx)
    z = basis_elem_g1(toe, c_idx)

    J = toe._jacobi(br_l2, x, y, z)
    Jflat = flatten(J)

    # collect S_T flats and e6 contributions
    S_flats = []
    S_e6_max = []
    overlap_with_J = []

    J_nz = set(np.where(np.abs(Jflat) > 1e-12)[0].tolist())

    for i, brf in enumerate(br_fibers):
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
        Sflat = flatten(S)

        S_flats.append(Sflat.tolist())
        S_e6_max.append(float(np.max(np.abs(S.e6))))

        overlap = list(
            np.intersect1d(np.where(np.abs(Sflat) > 1e-12)[0], list(J_nz)).tolist()
        )
        overlap_with_J.append(overlap)

    # try small LSQ to cancel the Jacobi on this triple (real LSQ)
    A_real = np.vstack([np.real(np.array(S_flats)).T, np.imag(np.array(S_flats)).T])
    b_real = -np.concatenate([np.real(Jflat), np.imag(Jflat)])
    coeffs, *_ = np.linalg.lstsq(A_real, b_real, rcond=None)

    output = {
        "failed_triple": {"a": a_idx, "b": b_idx, "c": c_idx},
        "J_flat_nonzero_count": len(J_nz),
        "J_max_e6": float(np.max(np.abs(J.e6))),
        "fiber_triads": [list(t[:3]) for t in fiber_triads],
        "S_e6_max": S_e6_max,
        "overlap_with_J_counts": [len(o) for o in overlap_with_J],
        "lsq_coeffs": [float(c) for c in coeffs.tolist()],
        "lsq_residual_linf": float(np.max(np.abs(A_real.dot(coeffs) - b_real))),
    }

    OUT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
