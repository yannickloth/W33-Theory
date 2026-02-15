#!/usr/bin/env python3
"""Seed the hybrid LSQ→CP‑SAT search with supports derived from MOG hexads.

This script now (1) enumerates the 132 Steiner hexads (S(5,6,12)),
(2) maps MOG positions -> AG(2,3) lines -> `N12` (Schläfli/W33) vertex ids,
(3) converts each hexad into a candidate `bad9` support (when a bad-triad
    lies entirely inside the hexad), and (4) optionally runs the hybrid
    LSQ→CP‑SAT trial on the mapped supports.

Usage examples:
  - Enumerate & persist hexads only (no CP‑SAT):
      python tools/seed_hybrid_from_mog_hexads.py

  - Map hexads -> bad9 supports and run CP‑SAT (time=300s, max support=6):
      python tools/seed_hybrid_from_mog_hexads.py --try-cp --time 300 --max-support-size 6 --sampled-pure-rows 4
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from pathlib import Path
from typing import Dict, FrozenSet, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "mog_hexads.json"
OUT_CP_RESULTS = ROOT / "artifacts" / "mog_hexads_seeded_hybrid_results.json"

# --- build Golay weight-6 hexads (same construction as THE_EXACT_MAP.py) ---
G = [
    [1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    [0, 1, 0, 0, 0, 0, 1, 0, 1, 2, 2, 1],
    [0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 2, 2],
    [0, 0, 0, 1, 0, 0, 1, 2, 1, 0, 1, 2],
    [0, 0, 0, 0, 1, 0, 1, 2, 2, 1, 0, 1],
    [0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 1, 0],
]


def _generate_golay_codewords():
    codewords = []
    for a in range(3):
        for b in range(3):
            for c in range(3):
                for d in range(3):
                    for e in range(3):
                        for f in range(3):
                            coeffs = (a, b, c, d, e, f)
                            vec = [0] * 12
                            for i, row in enumerate(G):
                                s = (
                                    sum(
                                        coef * row_j for coef, row_j in zip(coeffs, row)
                                    )
                                    % 3
                                )
                                vec[i] = s
                            codewords.append(tuple(vec))
    return codewords


codewords = _generate_golay_codewords()
nonzero = [c for c in codewords if any(x != 0 for x in c)]

hexads = sorted(
    list(
        {
            tuple(sorted(i for i, x in enumerate(c) if x != 0))
            for c in nonzero
            if sum(1 for x in c if x != 0) == 6
        }
    )
)

# --- try to import THE_EXACT_MAP (provides F3_lines + pos_to_line_mog) ---
exact = None
pos_to_line_mog = None
try:
    spec = importlib.util.spec_from_file_location(
        "THE_EXACT_MAP", ROOT / "THE_EXACT_MAP.py"
    )
    exact = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(exact)
    pos_to_line_mog = getattr(exact, "pos_to_line_mog", None)
except Exception:
    exact = None
    pos_to_line_mog = None

# persist basic hexad artifact (always)
OUT.write_text(
    json.dumps(
        {
            "n_hexads": len(hexads),
            "hexads": [list(h) for h in hexads],
            "pos_to_line_mog": pos_to_line_mog,
        },
        indent=2,
    ),
    encoding="utf-8",
)
print(f"Wrote {OUT} ({len(hexads)} hexads)")

# CLI ---------------------------------------------------------------------
parser = argparse.ArgumentParser(
    description="Map MOG hexads -> bad9 supports and optionally try CP-SAT"
)
parser.add_argument(
    "--try-cp", action="store_true", help="Run CP‑SAT on mapped supports"
)
parser.add_argument(
    "--time", type=float, default=300.0, help="CP‑SAT time limit per support (seconds)"
)
parser.add_argument(
    "--max-support-size",
    type=int,
    default=4,
    help="Maximum allowed support size when collecting seeds",
)
parser.add_argument(
    "--try-full-coeff",
    action="store_true",
    help="If baseline pass fails, also try full-coeff CP‑SAT",
)
parser.add_argument(
    "--sampled-pure-rows",
    type=int,
    default=0,
    help="Number of sampled pure‑sector rows to append to CP‑SAT (split g1/g2)",
)
args = parser.parse_args()

# If user didn't ask for CP step, we're done after writing hexads
if not args.try_cp:
    print("Mapping only (no CP‑SAT). Rerun with --try-cp to run hybrid trials.")
    raise SystemExit(0)

# --- Need exact map + F3_lines + pos_to_line_mog for mapping ---
if exact is None or pos_to_line_mog is None:
    raise SystemExit(
        "THE_EXACT_MAP.pos_to_line_mog not available — run THE_EXACT_MAP.py first"
    )

# --- load N12 CSV from Heisenberg bundle (canonical mapping) ---
n12_csv = (
    ROOT
    / "artifacts"
    / "bundles"
    / "W33_Heisenberg_action_bundle_20260209_v1"
    / "N12_vertices_as_affine_lines.csv"
)
if not n12_csv.exists():
    raise SystemExit(f"Missing N12 CSV: {n12_csv}")

# --- build mapping: frozenset{(x,y)} -> N12_vertex id and N12 -> H27 vertices
f3points_to_n12: Dict[FrozenSet[Tuple[int, int]], int] = {}
n12_to_h27: Dict[int, set] = {}
with n12_csv.open("r", encoding="utf-8") as fh:
    reader = csv.DictReader(fh)
    for r in reader:
        nid = int(r["N12_vertex"])
        pts_raw = r["phase_points"]  # format: "(0,0);(0,1);(0,2)"
        pts = tuple(
            tuple(int(x) for x in p.strip("() ").split(",")) for p in pts_raw.split(";")
        )
        f3points_to_n12[frozenset(pts)] = nid
        # parse H27 vertices listed for this N12 line (space-separated ints)
        h27_raw = r.get("H_vertices_in_coset", "")
        n12_to_h27[nid] = set(int(v) for v in h27_raw.split()) if h27_raw else set()

# build mapping: F3_line_index -> N12 vertex id
f3line_to_n12: Dict[int, int] = {}
for li, line in enumerate(exact.F3_lines):
    pts = tuple(sorted(line))
    key = frozenset(pts)
    if key not in f3points_to_n12:
        raise RuntimeError(f"F3 line {li} {pts} not found in N12 CSV mapping")
    f3line_to_n12[li] = f3points_to_n12[key]

# load canonical bad9 artifact (use H27-labelled triads for containment checks)
bad9 = json.loads(
    (ROOT / "artifacts" / "firewall_bad_triads_mapping.json").read_text(
        encoding="utf-8"
    )
)
bad_triads_h27 = bad9["bad_triangles_H27_local"]

# Convert hexads -> candidate bad9 supports (compare in H27 label-space)
candidate_supports = set()
hexad_to_supports: Dict[Tuple[int, ...], List[int]] = {}
for h in hexads:
    # map MOG positions -> F3_line indices -> N12 vertex ids -> H27 vertices
    h27_set = set()
    for p in h:
        li = pos_to_line_mog[p]
        nid = f3line_to_n12[li]
        h27_set.update(n12_to_h27.get(nid, set()))

    mapped = []
    for bi, tri in enumerate(bad_triads_h27):
        if set(tri).issubset(h27_set):
            mapped.append(bi)

    if 1 <= len(mapped) <= args.max_support_size:
        candidate_supports.add(tuple(sorted(mapped)))
    if mapped:
        hexad_to_supports[tuple(h)] = mapped

candidate_supports = sorted(candidate_supports)
print(
    f"Mapped hexads -> {len(hexad_to_supports)} nonempty hexads; {len(candidate_supports)} candidate supports (size <= {args.max_support_size})"
)

if not candidate_supports:
    print(
        "No candidate supports found from MOG hexads (under current max-support-size). Exiting."
    )
    raise SystemExit(0)

# -------------------------------------------------------------------------
# Build S/J system (same as other seeders) and try CP‑SAT on each support
# -------------------------------------------------------------------------
# import hybrid module (we reuse its helpers)
spec = importlib.util.spec_from_file_location(
    "hybrid_linfty_search", ROOT / "tools" / "hybrid_linfty_search.py"
)
hybrid = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(hybrid)

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

# import toe module (use canonical tool implementation)
toe_spec = importlib.util.spec_from_file_location(
    "toe_e8_mod", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(toe_spec)
assert toe_spec and toe_spec.loader
toe_spec.loader.exec_module(toe)

from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1, basis_elem_g2

# build toe helpers (copied from hybrid.main)
e6_basis = (
    __import__("numpy")
    .load(ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy")
    .astype(__import__("numpy").complex128)
)
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
import numpy as _np


def flatten(e):
    return _np.concatenate(
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

A_full = _np.array(Scols).T
Jflat = flatten(toe._jacobi(br_l2, x, y, z))

# reduced rows where |Jflat| > tol
nz_rows = _np.where(_np.abs(Jflat) > 1e-12)[0]
A_sub_full = A_full[nz_rows]
rhs_full = -Jflat[nz_rows]

# optionally append sampled pure-sector rows to raise effective rank
from numpy.random import default_rng


def _collect_sampled_pure_rows(n_g1: int, n_g2: int):
    rng = default_rng(20260212)
    e6_basis = _np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(_np.complex128)
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
                _np.concatenate(
                    [
                        S.e6.reshape(-1),
                        S.sl3.reshape(-1),
                        S.g1.reshape(-1),
                        S.g2.reshape(-1),
                    ]
                )
            )

        A_sample = _np.array(Scols).T
        J_sample = flatten(toe._jacobi(br_l2, xa, ya, za))
        nz = _np.where(_np.abs(J_sample) > 1e-12)[0]
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
    A_extra = _np.vstack(A_rows)
    rhs_extra = _np.concatenate(rhs_rows)
    return A_extra, rhs_extra


if args.sampled_pure_rows and args.sampled_pure_rows > 0:
    n_total = int(args.sampled_pure_rows)
    n_g1 = n_total // 2
    n_g2 = n_total - n_g1
    A_extra, rhs_extra = _collect_sampled_pure_rows(n_g1, n_g2)
    if A_extra is not None:
        A_sub_full = _np.vstack([A_sub_full, A_extra])
        rhs_full = _np.concatenate([rhs_full, rhs_extra])
        print(
            f"Appended sampled pure-sector rows: g1={n_g1}, g2={n_g2} -> +{A_extra.shape[0]} rows"
        )

# try CP-SAT on candidate supports
from tools.hybrid_linfty_search import cp_sat_try_for_support

results = []
for support in candidate_supports:
    support_idx = list(support)
    A_use = A_sub_full[:, support_idx]
    baseline_sub = _np.ones(len(support_idx)) * (1.0 / 9.0)
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

OUT_CP_RESULTS.write_text(
    json.dumps(
        {
            "hexad_to_supports": {
                "-".join(map(str, k)): v for k, v in hexad_to_supports.items()
            },
            "candidate_supports": candidate_supports,
            "results": results,
        },
        indent=2,
    ),
    encoding="utf-8",
)
print(f"Wrote: {OUT_CP_RESULTS}")
