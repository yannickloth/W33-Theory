#!/usr/bin/env python3
"""Compute LSQ correction for the failing mixed triple, apply it to the
rationalized candidate in `artifacts/linfty_coord_search_results_rationalized.json`,
and run the exhaustive homotopy verification and unit tests.

This script is intended to be a small, reversible helper for the current
interactive session.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAT_FILE = ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"


def _load_toe():
    spec = importlib.util.spec_from_file_location(
        "toe_e8_z3graded_bracket_jacobi",
        ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


def compute_candidate():
    toe = _load_toe()
    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)

    all_triads = toe._load_signed_cubic_triads()
    # load bad9 from the existing rationalized artifact so we preserve order
    data = json.loads(RAT_FILE.read_text(encoding="utf-8"))
    bad9 = set(tuple(sorted(t)) for t in data["original"]["fiber_triads"])

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

    # failing triple from exhaustive check
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

    def flatten(e):
        return np.concatenate(
            [e.e6.reshape(-1), e.sl3.reshape(-1), e.g1.reshape(-1), e.g2.reshape(-1)]
        )

    Jflat = flatten(J)
    nz = np.where(np.abs(Jflat) > 1e-12)[0]

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
    r_uniform = (A_sub @ np.array([1.0 / 9.0] * A_sub.shape[1])) + Jflat[nz]

    # solve for delta so uniform + delta cancels this triple
    rhs = -r_uniform
    A_real = np.vstack([np.real(A_sub), np.imag(A_sub)])
    rhs_real = np.concatenate([np.real(rhs), np.imag(rhs)])
    delta, *_ = np.linalg.lstsq(A_real, rhs_real, rcond=None)

    # rationalize delta with small denominators
    rats_delta = [Fraction(d).limit_denominator(240) for d in delta]
    candidate = [Fraction(1, 9) + rd for rd in rats_delta]

    return {
        "delta_float": [float(d) for d in delta.tolist()],
        "delta_rational": [str(r) for r in rats_delta],
        "candidate_rational": [str(fr) for fr in candidate],
        "candidate_float": [float(fr) for fr in candidate],
    }


def apply_candidate_to_artifact(candidate_floats, candidate_rats):
    text = RAT_FILE.read_text(encoding="utf-8")
    data = json.loads(text)
    # replace rationalized arrays
    data["rationalized_coeffs"] = candidate_rats
    data["rationalized_coeffs_float"] = candidate_floats
    # write a backup and then overwrite
    bak = RAT_FILE.with_suffix(RAT_FILE.suffix + ".bak")
    bak.write_text(text, encoding="utf-8")
    RAT_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print("Updated", RAT_FILE, "(backup ->", bak, ")")


def main():
    cand = compute_candidate()
    print("Computed candidate:")
    print(json.dumps(cand, indent=2))

    apply_candidate_to_artifact(cand["candidate_float"], cand["candidate_rational"])

    # run exhaustive check
    import subprocess

    print("Running exhaustive homotopy check (rationalized candidate)...")
    subprocess.run(
        [sys.executable, "tools/exhaustive_homotopy_check_rationalized_l3.py"],
        check=True,
    )

    print("Running unit tests (linfty firewall)...")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/test_linfty_firewall_extension.py",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
