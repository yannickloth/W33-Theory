#!/usr/bin/env python3
"""Try small supports that include triads implicated by the exhaustive failures.

This script:
 - reads the first failing triple from artifacts/exhaustive_homotopy_rationalized_l3.json
 - builds the S/J system for that triple
 - tries a list of candidate supports (lsq -> CP-SAT full-coeff)
 - runs numeric verification and records results in artifacts/targeted_repair_results.json
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import List

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "targeted_repair_results.json"

# load failing triple
exh = json.loads(
    (ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json").read_text(
        encoding="utf-8"
    )
)
sector = exh.get("sectors", {}).get("g1_g1_g2") or exh.get("sectors", {}).get(
    "g1_g2_g2"
)
if not sector:
    raise SystemExit("No failing sector found to target (g1_g1_g2 or g1_g2_g2)")
ft = sector.get("first_fail")
if not ft:
    raise SystemExit("No first_fail recorded in exhaustive artifact")

# import toe and hybrid helpers
spec_toe = importlib.util.spec_from_file_location(
    "toe_e8", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(spec_toe)
assert spec_toe and spec_toe.loader
spec_toe.loader.exec_module(toe)

spec_h = importlib.util.spec_from_file_location(
    "hybrid_linfty_search", ROOT / "tools" / "hybrid_linfty_search.py"
)
hybrid = importlib.util.module_from_spec(spec_h)
assert spec_h and spec_h.loader
spec_h.loader.exec_module(hybrid)

# load basis helper from exhaustive checker
from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1, basis_elem_g2

# `flatten` helper lives in hybrid module
from tools.hybrid_linfty_search import flatten

# prepare br_l2/br_fibers
e6_basis = np.load(
    ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
).astype(np.complex128)
proj = toe.E6Projector(e6_basis)
all_triads = toe._load_signed_cubic_triads()
bad9 = set(
    tuple(sorted(t))
    for t in json.loads(
        (
            ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"
        ).read_text(encoding="utf-8")
    )["original"]["fiber_triads"]
)

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

# assemble S/J for the failing triple
x = basis_elem_g1(toe, tuple(ft["a"]))
y = basis_elem_g1(toe, tuple(ft["b"]))
z = basis_elem_g2(toe, tuple(ft["c"]))

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

A_full = np.array(Scols).T
Jflat = flatten(toe._jacobi(br_l2, x, y, z))

nz_rows = np.where(np.abs(Jflat) > 1e-12)[0]
A_sub_full = A_full[nz_rows]
rhs_full = -Jflat[nz_rows]

# append sampled pure-sector rows to raise numeric rank
from numpy.random import default_rng


def collect_sampled_pure_rows(n_g1: int, n_g2: int):
    rng = default_rng(20260212)
    A_rows = []
    rhs_rows = []

    def _add_sample(triple_type: str):
        if triple_type == "g1":
            xa = toe._random_element(
                rng,
                e6_basis,
                scale0=0,
                scale1=2,
                scale2=0,
                include_g0=False,
                include_g2=False,
            )
            ya = toe._random_element(
                rng,
                e6_basis,
                scale0=0,
                scale1=2,
                scale2=0,
                include_g0=False,
                include_g2=False,
            )
            za = toe._random_element(
                rng,
                e6_basis,
                scale0=0,
                scale1=2,
                scale2=0,
                include_g0=False,
                include_g2=False,
            )
        else:
            xa = toe._random_element(
                rng,
                e6_basis,
                scale0=0,
                scale1=0,
                scale2=2,
                include_g0=False,
                include_g1=False,
            )
            ya = toe._random_element(
                rng,
                e6_basis,
                scale0=0,
                scale1=0,
                scale2=2,
                include_g0=False,
                include_g1=False,
            )
            za = toe._random_element(
                rng,
                e6_basis,
                scale0=0,
                scale1=0,
                scale2=2,
                include_g0=False,
                include_g1=False,
            )

        Scols = []
        for brf in br_fibers:
            j1 = brf.bracket(xa, br_l2.bracket(ya, za))
            j2 = brf.bracket(ya, br_l2.bracket(za, xa))
            j3 = brf.bracket(za, br_l2.bracket(xa, ya))
            f1 = br_l2.bracket(brf.bracket(xa, ya), za)
            f2 = br_l2.bracket(brf.bracket(ya, za), xa)
            f3 = br_l2.bracket(brf.bracket(za, xa), ya)
            ff1 = brf.bracket(xa, brf.bracket(ya, za))
            ff2 = brf.bracket(ya, brf.bracket(za, xa))
            ff3 = brf.bracket(za, brf.bracket(xa, ya))
            S = j1 + j2 + j3 + f1 + f2 + f3 + ff1 + ff2 + ff3
            Scols.append(
                np.concatenate(
                    [
                        S.e6.reshape(-1),
                        S.sl3.reshape(-1),
                        S.g1.reshape(-1),
                        S.g2.reshape(-1),
                    ]
                )
            )

        A_sample = np.array(Scols).T
        J_sample = flatten(toe._jacobi(br_l2, xa, ya, za))
        nz = np.where(np.abs(J_sample) > 1e-12)[0]
        if nz.size == 0:
            return
        A_rows.append(A_sample[nz, :])
        rhs_rows.append(-J_sample[nz])

    for _ in range(n_g1):
        _add_sample("g1")
    for _ in range(n_g2):
        _add_sample("g2")

    if not A_rows:
        return None, None
    A_extra = np.vstack(A_rows)
    rhs_extra = np.concatenate(rhs_rows)
    return A_extra, rhs_extra


A_extra, rhs_extra = collect_sampled_pure_rows(8, 8)
if A_extra is not None:
    A_sub_full = np.vstack([A_sub_full, A_extra])
    rhs_full = np.concatenate([rhs_full, rhs_extra])

# candidate supports to try (include triads implicated by failing triple)
# triad indices: from artifacts/linfty_coord_search_results_rationalized.json
candidates: List[List[int]] = [
    [0, 8],
    [0, 3, 8],
    [0, 2, 8],
    [0, 1, 8],
    [0, 4, 8],
    [0, 8, 7],
    [0, 3],
    [3, 8],
]

results = []
for support in candidates:
    print("Trying support:", support)
    A_use = A_sub_full[:, support]
    try:
        lsq_vec, lsq_res = hybrid.lsq_on_support(A_full, Jflat, support)
    except Exception as e:
        lsq_vec, lsq_res = None, str(e)
    row = {"support": support, "lsq_residual": lsq_res}

    # attempt CP-SAT full-coeff (baseline=None)
    try:
        D, scale, nums = hybrid.cp_sat_try_for_support(
            A_use,
            rhs_full,
            support,
            hybrid.D_LIST,
            hybrid.SCALE_CHOICES,
            300.0,
            verbose=False,
            baseline=None,
        )
    except Exception as e:
        D, scale, nums = None, None, None
        row["cp_error"] = str(e)

    if D is None:
        row.update({"D": D, "scale": scale, "nums": nums})
        results.append(row)
        continue

    # assemble candidate coefficients vector (9 entries)
    cand = [0.0] * 9
    for j, idx in enumerate(support):
        cand[idx] = float(nums[j]) / float(D)
    row.update({"D": D, "scale": scale, "nums": nums, "coeffs": cand})

    # numeric verification on the failing triple (and samples)
    ok, mag = hybrid.verify_candidate_numeric(
        toe, br_l2, br_fibers, x, y, z, cand, samples=320
    )
    row.update({"verify_sample_ok": ok, "verify_sample_residual": float(mag)})

    results.append(row)

OUT.write_text(
    json.dumps({"targeted_results": results, "fail_triple": ft}, indent=2),
    encoding="utf-8",
)
print("Wrote", OUT)
