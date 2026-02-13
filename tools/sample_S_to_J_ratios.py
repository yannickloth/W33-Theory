#!/usr/bin/env python3
"""Sample random g1_g1_g1 basis triples where Jacobi(l2) != 0 and compare
S_T vs J ratios across the 9 fiber triads.

Writes artifacts/S_to_J_ratio_samples.json
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from random import sample

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "S_to_J_ratio_samples.json"


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


def main(samples: int = 12):
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

    # build g1 basis indices
    g1_idx = [(i, j) for i in range(27) for j in range(3)]

    # find some triples with nonzero Jacobi
    triples = []
    for a_idx in g1_idx:
        for b_idx in g1_idx:
            for c_idx in g1_idx:
                if a_idx >= b_idx or b_idx >= c_idx:
                    continue
                x = toe.E8Z3.zero()
                x.g1[a_idx[0], a_idx[1]] = 1.0
                y = toe.E8Z3.zero()
                y.g1[b_idx[0], b_idx[1]] = 1.0
                z = toe.E8Z3.zero()
                z.g1[c_idx[0], c_idx[1]] = 1.0
                J = toe._jacobi(br_l2, x, y, z)
                if np.max(np.abs(J.e6)) > 1e-12:  # pick those with e6 Jacobi
                    triples.append((a_idx, b_idx, c_idx))
                if len(triples) >= samples:
                    break
            if len(triples) >= samples:
                break
        if len(triples) >= samples:
            break

    records = []
    for triple in triples:
        a_idx, b_idx, c_idx = triple
        x = toe.E8Z3.zero()
        x.g1[a_idx[0], a_idx[1]] = 1.0
        y = toe.E8Z3.zero()
        y.g1[b_idx[0], b_idx[1]] = 1.0
        z = toe.E8Z3.zero()
        z.g1[c_idx[0], c_idx[1]] = 1.0
        J = toe._jacobi(br_l2, x, y, z)
        Jf = flatten(J)
        nz = np.where(np.abs(Jf) > 1e-12)[0]
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
        # compute ratios S_T[nz] / J[nz]
        triad_ratios = []
        for S in Scols:
            r = (S[nz] / Jf[nz]).tolist()
            triad_ratios.append(float(np.mean(np.real(r))))
        records.append(
            {
                "triple": [list(a_idx), list(b_idx), list(c_idx)],
                "J_max_e6": float(np.max(np.abs(J.e6))),
                "triad_ratios_mean": triad_ratios,
                "Ssum_ratio_mean": float(np.mean(np.real((Ssum[nz] / Jf[nz])))),
            }
        )

    OUT.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
