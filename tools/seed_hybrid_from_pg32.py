#!/usr/bin/env python3
"""Seed the hybrid LSQ→CP‑SAT search with supports derived from PG(3,2)/MOG.

- Builds candidate supports (indices into the 9 fiber triads) from PG(3,2)
  lines that hit the canonical 9 'bad' triads.
- Calls the CP‑SAT attempt routine from `tools/hybrid_linfty_search.py`
  on each seeded support (short time budget).
- Writes `artifacts/pg32_seeded_hybrid_results.json`.

This is conservative: it only *tests* candidate supports, it doesn't
overwrite canonical artifacts.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "pg32_seeded_hybrid_results.json"

# CLI
parser = argparse.ArgumentParser(
    description="Seed hybrid LSQ→CP‑SAT from PG(3,2) supports"
)
parser.add_argument(
    "--time", type=float, default=300.0, help="CP‑SAT time limit per support (seconds)"
)
parser.add_argument(
    "--max-support-size",
    type=int,
    default=4,
    help="Maximum allowed support size when collecting seeds (default: 4)",
)
parser.add_argument(
    "--include-line-unions",
    action="store_true",
    help="Also include unions of two PG(3,2) lines as candidate supports",
)
parser.add_argument(
    "--try-full-coeff",
    action="store_true",
    help="If baseline (delta) pass fails for a support, also try a full-coeff CP‑SAT search",
)
parser.add_argument(
    "--sampled-pure-rows",
    type=int,
    default=0,
    help="Number of sampled pure‑sector rows to append to CP‑SAT (split g1/g2). Default 0",
)
args = parser.parse_args()

# import hybrid module (we reuse its helpers)
spec = importlib.util.spec_from_file_location(
    "hybrid_linfty_search", ROOT / "tools" / "hybrid_linfty_search.py"
)
hybrid = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(hybrid)

# load canonical data
pg32 = json.loads((ROOT / "artifacts" / "pg32_lines_from_remaining15.json").read_text())
bad9 = json.loads((ROOT / "artifacts" / "firewall_bad_triads_mapping.json").read_text())

# map Schläfli vertex -> bad9 index (0..8) when present
schlafli_to_bad9 = {}
for bi, tri in enumerate(bad9["bad_triangles_Schlafli_orbit_index"]):
    for v in tri:
        schlafli_to_bad9[v] = bi

# build supports: for each PG(3,2) line (3 Schläfli vertices) collect any
# corresponding bad9 indices — keep supports size 1..4
candidate_supports = set()
for L in pg32["lines"]:
    pts = L["points"]  # these are Schläfli vertex ids in repo convention
    support = sorted({schlafli_to_bad9[v] for v in pts if v in schlafli_to_bad9})
    if 1 <= len(support) <= args.max_support_size:
        candidate_supports.add(tuple(support))

# optionally include unions of two PG(3,2) lines to expand candidate supports
if args.include_line_unions:
    lines_supports = []
    for L in pg32["lines"]:
        pts = L["points"]
        support = sorted({schlafli_to_bad9[v] for v in pts if v in schlafli_to_bad9})
        if 1 <= len(support) <= args.max_support_size:
            lines_supports.append(tuple(support))

    # add pairwise unions (deduplicated) up to max size
    for i in range(len(lines_supports)):
        for j in range(i + 1, len(lines_supports)):
            union = tuple(sorted(set(lines_supports[i]) | set(lines_supports[j])))
            if 1 <= len(union) <= args.max_support_size:
                candidate_supports.add(union)

candidate_supports = sorted(candidate_supports)
print(
    f"Generated {len(candidate_supports)} seed supports (size<={args.max_support_size})"
)

# prepare failing triple (use first failing triple from exhaustive artifact)
exh = json.loads(
    (ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json").read_text()
)
sector = exh.get("sectors", {}).get("g1_g1_g2", {})
fails = sector.get("failing_examples") or (
    [sector.get("first_fail")] if sector.get("first_fail") else []
)
if not fails or fails[0] is None:
    raise SystemExit("No failing triple recorded to target.")
ft = fails[0]
from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1, basis_elem_g2

# import toe module (use canonical tool implementation)
toe_spec = importlib.util.spec_from_file_location(
    "toe_e8_mod", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(toe_spec)
assert toe_spec and toe_spec.loader
toe_spec.loader.exec_module(toe)

# build toe helpers (copied from hybrid.main)
e6_basis = np.load(
    ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
).astype(np.complex128)
proj = toe.E6Projector(e6_basis)
all_triads = toe._load_signed_cubic_triads()
bad9_set = (
    set(tuple(sorted(t[:3])) for t in bad9["bad_triangles_Schlafli_e6id"])
    if "bad_triangles_Schlafli_e6id" in bad9
    else set()
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

# basis elements for failing triple (pass `toe` module)
x = basis_elem_g1(toe, tuple(ft["a"]))
y = basis_elem_g1(toe, tuple(ft["b"]))
z = basis_elem_g2(toe, tuple(ft["c"]))

# build S-matrix and J (local reimplementation, matching hybrid logic)


def flatten(e):
    return np.concatenate(
        [e.e6.reshape(-1), e.sl3.reshape(-1), e.g1.reshape(-1), e.g2.reshape(-1)]
    )


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

# reduced rows where |Jflat| > tol
nz_rows = np.where(np.abs(Jflat) > 1e-12)[0]
A_sub_full = A_full[nz_rows]
rhs_full = -Jflat[nz_rows]


# optionally append sampled pure-sector rows to raise effective rank
def _collect_sampled_pure_rows(n_g1: int, n_g2: int):
    """Return (A_extra, rhs_extra) arrays built from sampled pure-sector triples.

    - n_g1: number of g1_g1_g1 sampled triples
    - n_g2: number of g2_g2_g2 sampled triples
    """
    from numpy.random import default_rng

    rng = default_rng(20260212)
    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    A_rows = []
    rhs_rows = []

    def _add_sample(triple_type: str):
        # triple_type in {"g1", "g2"}
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

        # build S/J for this triple
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


# if user requested sampled rows, append them to A_sub_full / rhs_full
if args.sampled_pure_rows and args.sampled_pure_rows > 0:
    # default split: half g1 and half g2 (round down)
    n_total = int(args.sampled_pure_rows)
    n_g1 = n_total // 2
    n_g2 = n_total - n_g1
    A_extra, rhs_extra = _collect_sampled_pure_rows(n_g1, n_g2)
    if A_extra is not None:
        # stack new sampled rows under existing reduced rows
        A_sub_full = np.vstack([A_sub_full, A_extra])
        rhs_full = np.concatenate([rhs_full, rhs_extra])
        print(
            f"Appended sampled pure-sector rows: g1={n_g1}, g2={n_g2} -> +{A_extra.shape[0]} rows"
        )

# try CP-SAT on candidate supports
from tools.hybrid_linfty_search import cp_sat_try_for_support

results = []
for support in candidate_supports:
    support_idx = list(support)
    A_use = A_sub_full[:, support_idx]
    # search for delta relative to uniform baseline (1/9)
    baseline_sub = np.ones(len(support_idx)) * (1.0 / 9.0)
    D, scale, nums = cp_sat_try_for_support(
        A_use,
        rhs_full,
        support_idx,
        hybrid.D_LIST,
        hybrid.SCALE_CHOICES,
        args.time,
        verbose=False,
        baseline=baseline_sub,
    )
    mode = "baseline"
    # if baseline pass failed and user requested, try full‑coeff search (no baseline)
    if D is None and args.try_full_coeff:
        D, scale, nums = cp_sat_try_for_support(
            A_use,
            rhs_full,
            support_idx,
            hybrid.D_LIST,
            hybrid.SCALE_CHOICES,
            args.time,
            verbose=False,
            baseline=None,
        )
        if D is not None:
            mode = "full-coeff"

    rec = {
        "support": support_idx,
        "cp_found": D is not None,
        "mode": mode,
        "D": D,
        "scale": scale,
        "nums": nums,
    }
    results.append(rec)

OUT.write_text(
    json.dumps(
        {"candidate_supports": candidate_supports, "results": results}, indent=2
    ),
    encoding="utf-8",
)
print("Wrote:", OUT)
