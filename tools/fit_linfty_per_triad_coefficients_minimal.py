#!/usr/bin/env python3
"""
Deterministic small-sample least-squares fit of per-triad l_3 coefficients.

Select a small set of basis g1 triples and solve the linear system exactly (or
least-squares) for coefficients on the 9 fiber triads. Much faster than random
sampling and sufficient when the triad basis spans the image.

Writes: artifacts/linfty_per_triad_fit_minimal.json
"""
from __future__ import annotations

import importlib.util
import json
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "linfty_per_triad_fit_minimal.json"


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

    # firewall-filtered l2 bracket
    br_l2 = toe.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=[t for t in all_triads if tuple(sorted(t[:3])) not in bad9],
        scale_g1g1=1.0,
        scale_g2g2=-1.0 / 6.0,
        scale_e6=1.0,
        scale_sl3=1.0 / 6.0,
    )

    # fiber triads and their single-triad br_fibers
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

    # canonical g1 basis (81 basis vectors)
    g1_basis = []
    for i in range(27):
        for j in range(3):
            e = toe.E8Z3.zero()
            g1 = np.zeros((27, 3), dtype=np.complex128)
            g1[i, j] = 1.0
            g1_basis.append(
                toe.E8Z3(
                    e6=np.zeros((27, 27), dtype=np.complex128),
                    sl3=np.zeros((3, 3), dtype=np.complex128),
                    g1=g1,
                    g2=np.zeros((27, 3), dtype=np.complex128),
                )
            )

    # choose small set of basis indices to form triples
    idxs = list(range(12))  # first 12 basis vectors -> C(12,3)=220 triples
    triples = list(combinations(idxs, 3))[:30]  # use first 30 triples

    m = len(triples)
    dim = 27 * 27 + 3 * 3 + 27 * 3 + 27 * 3
    N = len(fiber_triads)

    A = np.zeros((m * dim, N), dtype=np.complex128)
    b = np.zeros((m * dim,), dtype=np.complex128)

    for i, (ia, ib, ic) in enumerate(triples):
        x = g1_basis[ia]
        y = g1_basis[ib]
        z = g1_basis[ic]

        J = (
            br_l2.bracket(x, br_l2.bracket(y, z))
            + br_l2.bracket(y, br_l2.bracket(z, x))
            + br_l2.bracket(z, br_l2.bracket(x, y))
        )
        Jflat = _flatten(J)
        b[i * dim : (i + 1) * dim] = -Jflat  # we want A c = -J

        for t_idx, brf in enumerate(br_fibers):
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
            A[i * dim : (i + 1) * dim, t_idx] = np.concatenate(
                [
                    S.e6.reshape(-1),
                    S.sl3.reshape(-1),
                    S.g1.reshape(-1),
                    S.g2.reshape(-1),
                ]
            )

    # Solve least-squares (real system)
    A_real = np.vstack([A.real, A.imag])
    b_real = np.concatenate([b.real, b.imag])
    coeffs, *_ = np.linalg.lstsq(A_real, b_real, rcond=None)

    coeffs_real = [float(c) for c in coeffs]

    # quick verification on a few random mixed triples
    rng = np.random.default_rng(42)
    max_before = 0.0
    max_after = 0.0
    for _ in range(100):
        x = toe._random_element(rng, e6_basis, scale0=2, scale1=2, scale2=2)
        y = toe._random_element(rng, e6_basis, scale0=2, scale1=2, scale2=2)
        z = toe._random_element(rng, e6_basis, scale0=2, scale1=2, scale2=2)
        J = (
            br_l2.bracket(x, br_l2.bracket(y, z))
            + br_l2.bracket(y, br_l2.bracket(z, x))
            + br_l2.bracket(z, br_l2.bracket(x, y))
        )
        mag_before = max(
            np.max(np.abs(J.e6)),
            np.max(np.abs(J.sl3)),
            np.max(np.abs(J.g1)),
            np.max(np.abs(J.g2)),
        )
        max_before = max(max_before, float(mag_before))

        # build l3 from coeffs
        l3_total = toe.E8Z3.zero()
        for c, brf in zip(coeffs_real, br_fibers):
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
        mag_after = max(
            np.max(np.abs(total.e6)),
            np.max(np.abs(total.sl3)),
            np.max(np.abs(total.g1)),
            np.max(np.abs(total.g2)),
        )
        max_after = max(max_after, float(mag_after))

    out = {
        "fiber_triads": [list(t[:3]) for t in fiber_triads],
        "coeffs": coeffs_real,
        "max_homotopy_before_sampled": float(max_before),
        "max_homotopy_after_sampled": float(max_after),
        "triples_used": len(triples),
    }
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote", OUT)
    print("max before:", max_before, "max after:", max_after)


if __name__ == "__main__":
    main()
