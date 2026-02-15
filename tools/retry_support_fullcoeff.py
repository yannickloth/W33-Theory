#!/usr/bin/env python3
"""Retry CP‑SAT on a single MOG‑mapped support using `baseline=None` (full‑coeff).
Useful when the baseline run found an integer solution that failed numeric verification.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

# load the MOG artifact to get the candidate support
res = json.loads(
    (ROOT / "artifacts" / "mog_hexads_seeded_hybrid_results.json").read_text(
        encoding="utf-8"
    )
)
if not res.get("results"):
    raise SystemExit("No results found in mog_hexads_seeded_hybrid_results.json")
rec = res["results"][0]
support = rec["support"]
print(f"Retrying support: {support}")

# import hybrid helpers
spec = importlib.util.spec_from_file_location(
    "hybrid_linfty_search", ROOT / "tools" / "hybrid_linfty_search.py"
)
hybrid = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(hybrid)

# import toe and build S/J as in the seeder
toe_spec = importlib.util.spec_from_file_location(
    "toe_e8_mod", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(toe_spec)
assert toe_spec and toe_spec.loader
toe_spec.loader.exec_module(toe)

from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1, basis_elem_g2

# prepare br_l2 and br_fibers
e6_basis = np.load(
    ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
).astype(np.complex128)
proj = toe.E6Projector(e6_basis)
all_triads = toe._load_signed_cubic_triads()
bad9_set = set(
    tuple(sorted(t[:3]))
    for t in json.loads(
        (
            ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"
        ).read_text(encoding="utf-8")
    )["original"]["fiber_triads"]
)

br_l2 = toe.E8Z3Bracket(
    e6_projector=proj,
    cubic_triads=[t for t in all_triads if tuple(sorted(t[:3])) not in bad9_set],
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
    for T in [t for t in all_triads if tuple(sorted(t[:3])) in bad9_set]
]

# build S/J (use flatten from hybrid helper)
from tools.hybrid_linfty_search import flatten

Scols = []
# (no dummy/in-place calls needed; we'll build Scols below in the normal loop)

# replicate the same A_sub_full/rhs_full construction as in the seeder
# (load failing triple from exhaustive artifact)
exh = json.loads(
    (ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json").read_text(
        encoding="utf-8"
    )
)
sector = exh.get("sectors", {}).get("g1_g1_g2", {})
fails = sector.get("failing_examples") or (
    [sector.get("first_fail")] if sector.get("first_fail") else []
)
if not fails or fails[0] is None:
    raise SystemExit("No failing triple recorded to target.")
ft = fails[0]

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

# append sampled pure-sector rows to raise effective numeric rank (try 16 samples)
from numpy.random import default_rng


def _collect_sampled_pure_rows(n_g1: int, n_g2: int):
    rng = default_rng(20260212)
    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
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


n_total = 16
n_g1 = n_total // 2
n_g2 = n_total - n_g1
A_extra, rhs_extra = _collect_sampled_pure_rows(n_g1, n_g2)
if A_extra is not None:
    A_sub_full = np.vstack([A_sub_full, A_extra])
    rhs_full = np.concatenate([rhs_full, rhs_extra])
    print(
        f"Appended sampled pure-sector rows: g1={n_g1}, g2={n_g2} -> +{A_extra.shape[0]} rows"
    )

# inspect LSQ on this support first
A_use = A_sub_full[:, support]
lsq_vec, lsq_res = hybrid.lsq_on_support(A_full, Jflat, support)
print(f"LSQ on support {support} -> residual={lsq_res:.6e} coeffs={lsq_vec[support]}")

# attempt full-coeff CP-SAT on the support
print(
    "Calling cp_sat_try_for_support with baseline=None (full-coeff) and time_limit=600s"
)
D, scale, nums = hybrid.cp_sat_try_for_support(
    A_use,
    rhs_full,
    support,
    hybrid.D_LIST,
    hybrid.SCALE_CHOICES,
    600.0,
    verbose=True,
    baseline=None,
)
print("Result:", D, scale, nums)

# numeric verification for the returned candidate (if any)
if D is not None:
    # we called cp_sat_try_for_support with baseline=None (full-coeff), so
    # the returned `nums` are the absolute numerators and c_i = nums/D on the
    # supported indices (zeros elsewhere).
    cand = [0.0] * 9
    for j, idx in enumerate(support):
        cand[idx] = float(nums[j]) / float(D)
    ok, mag = hybrid.verify_candidate_numeric(
        toe, br_l2, br_fibers, x, y, z, cand, samples=320
    )
    print(f"verify_candidate_numeric -> {ok}, residual={mag:.3e}")
else:
    print("No integer solution found in full-coeff retry.")
