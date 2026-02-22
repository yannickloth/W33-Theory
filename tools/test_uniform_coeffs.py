#!/usr/bin/env python3
"""Test effect of a uniform coefficient vector on the failing triple.
Prints the Jacobi and l3 contributions and their sum.
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

    coeffs = [1.0 / 9.0] * 9

    l3_total = toe.E8Z3.zero()
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

    total = toe.E8Z3(
        e6=J.e6 + l3_total.e6,
        sl3=J.sl3 + l3_total.sl3,
        g1=J.g1 + l3_total.g1,
        g2=J.g2 + l3_total.g2,
    )

    print("J.e6 max abs =", np.max(np.abs(J.e6)))
    print(
        "sum_S.e6 max abs =",
        np.max(
            np.abs(
                sum(
                    [
                        flatten(s)[:78]
                        for s in [
                            brf.bracket(x, br_l2.bracket(y, z)) for brf in br_fibers
                        ]
                    ]
                )
            )
        ),
    )
    print("l3_total.e6 max abs =", np.max(np.abs(l3_total.e6)))
    print(
        "total max abs =",
        max(
            np.max(np.abs(total.e6)),
            np.max(np.abs(total.sl3)),
            np.max(np.abs(total.g1)),
            np.max(np.abs(total.g2)),
        ),
    )


if __name__ == "__main__":
    main()
