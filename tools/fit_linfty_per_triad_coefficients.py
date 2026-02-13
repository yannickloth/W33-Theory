#!/usr/bin/env python3
"""
Fit independent l_3 coefficients on the 9 fiber triads by least-squares.

Goal: find small, interpretable c_T (one per fiber triad) so that
  Jacobi(l_2) + Σ_T c_T · B_T ≈ 0
on sampled triples (minimize mixed residual).

Outputs: artifacts/linfty_per_triad_fit.json
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "linfty_per_triad_fit.json"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys_mod = __import__("sys")
    sys_mod.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _flatten(e):
    return np.concatenate(
        [e.e6.reshape(-1), e.sl3.reshape(-1), e.g1.reshape(-1), e.g2.reshape(-1)]
    )


def main(sample_count: int = 500):
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

    # List of fiber triad keys (the 9 triads)
    fiber_triads = [t for t in all_triads if tuple(sorted(t[:3])) in bad9]
    assert len(fiber_triads) == 9

    # Build L_infty helper for single-triad basis functions
    # For each fiber triad T we create a bracket br_fiber_T and compute B_T(x,y,z)
    # where l3_T(x,y,z) = -1 * B_T (when l3_scale=1 on that single triad)

    # Build firewall-filtered l2 bracket (36 triads)
    br_l2 = toe.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=[t for t in all_triads if tuple(sorted(t[:3])) not in bad9],
        scale_g1g1=1.0,
        scale_g2g2=-1.0 / 6.0,
        scale_e6=1.0,
        scale_sl3=1.0 / 6.0,
    )

    # Precompute single-triad br_fiber objects
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

    rng = np.random.default_rng(20260212)

    # Collect sample equations: for each sampled triple produce a vector J (Jacobi_l2)
    # and column vectors B_T (so that l3 = -Σ c_T B_T). We want J + Σ c_T B_T ≈ 0.

    vecs_J = []
    mat_B_cols = []  # will be list of lists per sample

    samples_used = 0
    attempts = 0
    max_attempts = sample_count * 6

    while samples_used < sample_count and attempts < max_attempts:
        attempts += 1
        # sample mixed triples (hard case)
        x = toe._random_element(rng, e6_basis, scale0=2, scale1=2, scale2=2)
        y = toe._random_element(rng, e6_basis, scale0=2, scale1=2, scale2=2)
        z = toe._random_element(rng, e6_basis, scale0=2, scale1=2, scale2=2)

        J = (
            br_l2.bracket(x, br_l2.bracket(y, z))
            + br_l2.bracket(y, br_l2.bracket(z, x))
            + br_l2.bracket(z, br_l2.bracket(x, y))
        )
        Jflat = _flatten(J)
        # skip trivial samples
        if np.linalg.norm(Jflat) < 1e-12:
            continue

        # build column for each fiber triad: the pre-scaled B_T so that l3 contribution = -c_T * B_T
        Bcols = []
        for brf in br_fibers:
            # compute the same nine-term composition used in LInftyE8Extension.l3 but with single-triad br_fiber
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
            # LInfty uses l3 = -s * S, so the pre-scaled basis vector is S
            Bcols.append(_flatten(S))

        vecs_J.append(Jflat)
        mat_B_cols.append(Bcols)
        samples_used += 1

    # Assemble linear system: for each sample i: J_i + Σ_T c_T * B_iT ≈ 0
    # Stack into big system: [B] c = -J
    m = vecs_J[0].shape[0]
    N = len(fiber_triads)
    S_big = np.zeros((samples_used * m, N), dtype=np.complex128)
    J_big = np.zeros((samples_used * m,), dtype=np.complex128)

    for i in range(samples_used):
        for t_idx in range(N):
            S_big[i * m : (i + 1) * m, t_idx] = mat_B_cols[i][t_idx]
        J_big[i * m : (i + 1) * m] = -vecs_J[i]

    # Solve least-squares for complex coefficients c (we restrict to real since data is real)
    # Use real representation: stack real & imag parts to avoid complex least-squares subtleties
    A_real = np.vstack([np.real(S_big), np.imag(S_big)])
    b_real = np.concatenate([np.real(J_big), np.imag(J_big)])

    coeffs, *_ = np.linalg.lstsq(A_real, b_real, rcond=None)

    # Evaluate residuals on held-out random verification set
    rng2 = np.random.default_rng(321)
    verify_trials = 120
    max_homotopy_before = 0.0
    max_homotopy_after = 0.0

    # build a function to compute l3_from_coeffs on triple
    def l3_from_coeffs(x, y, z, coeffs_vec: List[float]):
        total = None
        for c, brf in zip(coeffs_vec, br_fibers):
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
            contrib = S.scale(float(c))
            total = contrib if total is None else total + contrib
        # l3 = -Σ c_T * S_T  (because earlier we arranged J_big = -J and S_big columns = S)
        return total.scale(-1.0) if total is not None else toe.E8Z3.zero()

    for _ in range(verify_trials):
        x = toe._random_element(rng2, e6_basis, scale0=2, scale1=2, scale2=2)
        y = toe._random_element(rng2, e6_basis, scale0=2, scale1=2, scale2=2)
        z = toe._random_element(rng2, e6_basis, scale0=2, scale1=2, scale2=2)
        j_l2 = toe._jacobi(br_l2, x, y, z)
        mag_before = max(
            np.max(np.abs(j_l2.e6)),
            np.max(np.abs(j_l2.sl3)),
            np.max(np.abs(j_l2.g1)),
            np.max(np.abs(j_l2.g2)),
        )
        max_homotopy_before = max(max_homotopy_before, float(mag_before))

        l3_val = l3_from_coeffs(x, y, z, coeffs)
        total = toe.E8Z3(
            e6=j_l2.e6 + l3_val.e6,
            sl3=j_l2.sl3 + l3_val.sl3,
            g1=j_l2.g1 + l3_val.g1,
            g2=j_l2.g2 + l3_val.g2,
        )
        mag_after = max(
            np.max(np.abs(total.e6)),
            np.max(np.abs(total.sl3)),
            np.max(np.abs(total.g1)),
            np.max(np.abs(total.g2)),
        )
        max_homotopy_after = max(max_homotopy_after, float(mag_after))

    # prepare human-friendly output (real coefficients)
    coeffs_real = [float(np.real(c)) for c in coeffs]

    output = {
        "fiber_triads": [list(t[:3]) for t in fiber_triads],
        "coeffs": coeffs_real,
        "max_homotopy_before_sampled": float(max_homotopy_before),
        "max_homotopy_after_sampled": float(max_homotopy_after),
        "samples_used": samples_used,
    }

    OUT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print("Wrote", OUT)
    print("Max homotopy before (sampled):", max_homotopy_before)
    print("Max homotopy after  (sampled):", max_homotopy_after)


if __name__ == "__main__":
    main(sample_count=400)
