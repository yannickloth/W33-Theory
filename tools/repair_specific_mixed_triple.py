#!/usr/bin/env python3
"""Targeted repair for the mixed failing triple (0,0),(17,1),(3,1).

- Run LSQ across the 9 fiber triads to find per-triad coefficient corrections.
- Try to rationalize the LSQ solution (limit_den=240).
- If rationalized candidate cancels the triple, write artifact and (optionally)
  print the exact candidate for manual application.

This is a focused, non-destructive helper (does NOT auto-commit changes).
"""
from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import List

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "mixed_triple_lsq_probe_0_0_17_1_3_1.json"

# --- helpers -----------------------------------------------------------------


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


# --- main --------------------------------------------------------------------
if __name__ == "__main__":
    toe = _load_module(ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py", "toe_e8")
    # basis + projector
    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)

    all_triads = toe._load_signed_cubic_triads()
    rat = json.loads(
        (
            ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"
        ).read_text()
    )
    bad9 = set(tuple(sorted(t)) for t in rat["original"]["fiber_triads"])

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
        for T in [t for t in all_triads if tuple(sorted(t[:3])) in bad9]
    ]

    from tools.exhaustive_homotopy_check_rationalized_l3 import (
        basis_elem_g1,
        basis_elem_g2,
    )

    # target triple (0,0),(17,1),(3,1)
    a_idx = (0, 0)
    b_idx = (17, 1)
    c_idx = (3, 1)
    x = basis_elem_g1(toe, a_idx)
    y = basis_elem_g1(toe, b_idx)
    z = basis_elem_g2(toe, c_idx)

    J = toe._jacobi(br_l2, x, y, z)
    Jflat = flatten(J)
    nz = np.where(np.abs(Jflat) > 1e-12)[0]

    # build Scols
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

    A = np.array(Scols).T
    A_sub = A[nz, :]
    b = -Jflat[nz]

    # quick diagnostics
    overlaps = [np.vdot(A_sub[:, i], b) for i in range(A_sub.shape[1])]
    col_norms = np.linalg.norm(A_sub, axis=0)
    ranking = sorted(
        range(A_sub.shape[1]), key=lambda i: (-abs(overlaps[i]), -col_norms[i])
    )

    # real least-squares
    A_real = np.vstack([np.real(A_sub), np.imag(A_sub)])
    b_real = np.concatenate([np.real(b), np.imag(b)])
    sol, *rest = np.linalg.lstsq(A_real, b_real, rcond=None)
    residual = float(np.max(np.abs(A_real.dot(sol) - b_real)))

    # rationalize
    rats = [Fraction(float(v)).limit_denominator(240) for v in sol]

    # check residual after applying rationalized solution
    cand = [float(v) for v in rats]
    res_after = float(np.max(np.abs(A_sub.dot(cand) + Jflat[nz])))

    out = {
        "failed_triple": {"a": list(a_idx), "b": list(b_idx), "c": list(c_idx)},
        "J_nonzero_count": int(nz.size),
        "lsq_residual_float": float(residual),
        "lsq_solution_float_first9": [float(v) for v in sol[:9]],
        "lsq_solution_rational_first9": [str(r) for r in rats[:9]],
        "residual_after_rationalized_candidate": res_after,
        "top_ranked_triads": ranking[:6],
    }

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote:", OUT)

    # print short summary
    print(
        json.dumps(
            {
                "residual_before": float(
                    np.max(np.abs(A_sub.dot([1.0 / 9.0] * 9) + Jflat[nz]))
                ),
                "lsq_residual": residual,
                "res_after_rationalized": res_after,
                "rats_first9": [str(r) for r in rats[:9]],
            },
            indent=2,
        )
    )
