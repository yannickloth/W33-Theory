#!/usr/bin/env python3
"""Find per-triad coefficient correction to cancel the failing g1_g1_g2 triple.

Outputs a small JSON with LSQ solution and a rationalized candidate (limit_den=240).
"""
from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import List

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "mixed_triple_lsq_correction.json"


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
    linfty_mod = _load_module(
        ROOT / "tools" / "build_linfty_firewall_extension.py", "linfty_mod"
    )

    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)

    all_triads = toe._load_signed_cubic_triads()
    bad9 = linfty_mod._load_bad9()

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

    # failing triple from exhaustive check (g1,g1,g2)
    from tools.exhaustive_homotopy_check_rationalized_l3 import (
        basis_elem_g1,
        basis_elem_g2,
    )

    a_idx = (0, 0)
    b_idx = (17, 1)
    c_idx = (3, 0)

    x = basis_elem_g1(toe, a_idx)
    y = basis_elem_g1(toe, b_idx)
    z = basis_elem_g2(toe, c_idx)

    J = toe._jacobi(br_l2, x, y, z)
    Jflat = flatten(J)
    nz = np.where(np.abs(Jflat) > 1e-12)[0]

    # build Scols per fiber triad
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

    # real least-squares
    A_real = np.vstack([np.real(A_sub), np.imag(A_sub)])
    b_real = np.concatenate([np.real(b), np.imag(b)])
    sol, *_ = np.linalg.lstsq(A_real, b_real, rcond=None)

    # also compute "delta" that would adjust uniform=1/9 -> uniform+delta
    uniform = np.array([1.0 / 9.0] * len(sol))
    # compute residual after uniform
    r_uniform = (A_sub @ uniform) + Jflat[nz]
    # solve A_sub delta = -r_uniform
    rhs = -r_uniform
    rhs_real = np.concatenate([np.real(rhs), np.imag(rhs)])
    delta, *_ = np.linalg.lstsq(A_real, rhs_real, rcond=None)

    rats_sol = [Fraction(s).limit_denominator(240) for s in sol]
    rats_delta = [Fraction(d).limit_denominator(240) for d in delta]

    out = {
        "failed_triple": {"a": a_idx, "b": b_idx, "c": c_idx},
        "J_nonzero_count": int(nz.size),
        "lsq_solution_float": [float(v) for v in sol.tolist()],
        "lsq_solution_rational": [str(r) for r in rats_sol],
        "uniform": [float(u) for u in uniform.tolist()],
        "delta_float": [float(v) for v in delta.tolist()],
        "delta_rational": [str(r) for r in rats_delta],
        "residual_after_uniform_max_abs": float(np.max(np.abs(r_uniform))),
        "residual_after_lsq_max_abs": float(np.max(np.abs(A_sub @ sol + Jflat[nz]))),
    }

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
