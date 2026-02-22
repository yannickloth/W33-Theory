#!/usr/bin/env python3
"""Re-rank LSQ supports by independent row count and re-run CP-SAT on top candidates.
Writes:
 - artifacts/hybrid_supports_reranked_by_rowcount.json
 - artifacts/hybrid_rerank_rerun_results.json
 - artifacts/hybrid_linfty_candidate_rerank.json (if a verified candidate is found)
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

try:
    ROOT = Path(__file__).resolve().parents[1]
except NameError:
    ROOT = Path(".").resolve()

# import hybrid module
spec = importlib.util.spec_from_file_location(
    "hybrid_linfty_search", ROOT / "tools" / "hybrid_linfty_search.py"
)
hybrid = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(hybrid)

# import toe and helpers
toe_spec = importlib.util.spec_from_file_location(
    "toe", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(toe_spec)
assert toe_spec and toe_spec.loader
toe_spec.loader.exec_module(toe)
from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1, basis_elem_g2

# build br_l2 / br_fibers
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
        ).read_text()
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

# pick failing triple
exh = json.loads(
    (ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json").read_text()
)
sector = exh.get("sectors", {}).get("g1_g1_g2", {})
fails = sector.get("failing_examples") or (
    [sector.get("first_fail")] if sector.get("first_fail") else []
)
if not fails or not fails[0]:
    raise SystemExit("No failing triple recorded")
ft = fails[0]
x = basis_elem_g1(toe, tuple(ft["a"]))
y = basis_elem_g1(toe, tuple(ft["b"]))
z = basis_elem_g2(toe, tuple(ft["c"]))

# build S/J
A, Jflat = hybrid.make_S_matrix_and_J(toe, br_l2, br_fibers, x, y, z)
# rows where Jflat nonzero
nz = np.where(np.abs(Jflat) > 1e-12)[0]
A_subrows_full = A[nz]
rhs_sub = -Jflat[nz]

# always enumerate all supports up to MAX_SUPPORT (we need row-rank for every combo)
from itertools import combinations

idxs = list(range(A.shape[1]))
supports = []
for k in range(1, hybrid.MAX_SUPPORT + 1):
    for comb in combinations(idxs, k):
        full_coeffs, res = hybrid.lsq_on_support(A, Jflat, list(comb))
        supports.append({"support": list(comb), "lsq_residual": res})

# also load any previously-stored candidate list for reference (optional)
hybrid_art = Path(ROOT / "artifacts" / "hybrid_search_results.json")
artifact_supports = []
if hybrid_art.exists():
    data = json.loads(hybrid_art.read_text())
    for entry in data.get("entries", []):
        for s in entry.get("support_trials", []):
            artifact_supports.append(s["support"])


# compute nonzero rows and rank for each support
aug = []
for rec in supports:
    sidx = rec["support"]
    A_sub = A_subrows_full[:, sidx]
    nonzero_rows = int(np.sum(np.any(np.abs(A_sub) > 1e-15, axis=1)))
    rank = int(np.linalg.matrix_rank(A_sub))
    aug.append(
        {
            "support": sidx,
            "nonzero_rows": nonzero_rows,
            "rank": rank,
            "lsq_residual": rec.get("lsq_residual", None),
        }
    )

# sort by rank desc, then nonzero_rows desc, then lsq_residual asc
aug_sorted = sorted(
    aug,
    key=lambda r: (
        -r["rank"],
        -r["nonzero_rows"],
        (r["lsq_residual"] if r["lsq_residual"] is not None else 1e9),
    ),
)
OUT = ROOT / "artifacts" / "hybrid_supports_reranked_by_rowcount.json"
OUT.write_text(json.dumps({"reranked": aug_sorted[:60]}, indent=2), encoding="utf-8")
print("Wrote", OUT)

# select supports with rank >= 2 (preferred); otherwise fallback to top-N
supports_with_rank_ge_2 = [r for r in aug_sorted if r["rank"] >= 2]
if supports_with_rank_ge_2:
    candidates = supports_with_rank_ge_2
    reason = f"rank>=2 ({len(candidates)} supports)"
else:
    TOP_N = min(24, len(aug_sorted))
    candidates = aug_sorted[:TOP_N]
    reason = f"top-{TOP_N} by rank/nonzero_rows"

from fractions import Fraction

cp_results = []
max_tests = min(48, len(candidates))
for rec in candidates[:max_tests]:
    support = rec["support"]
    A_use = A_subrows_full[:, support]
    D, scale, nums = hybrid.cp_sat_try_for_support(
        A_use,
        rhs_sub,
        support,
        hybrid.D_LIST,
        hybrid.SCALE_CHOICES,
        hybrid.CP_TIME_LIMIT,
        verbose=False,
        baseline=np.ones(len(support)) * (1.0 / 9.0),
    )
    resrec = {
        "support": support,
        "rank": rec["rank"],
        "nonzero_rows": rec["nonzero_rows"],
        "cp_found": D is not None,
        "D": D,
        "scale": scale,
        "nums": nums,
    }
    if D is not None:
        # build full coeffs and numeric verify
        cand = [1.0 / 9.0] * A.shape[1]
        for j, idx in enumerate(support):
            cand[idx] = 1.0 / 9.0 + float(nums[j]) / float(D)
        ok, mag = hybrid.verify_candidate_numeric(
            toe, br_l2, br_fibers, x, y, z, cand, samples=320
        )
        resrec["verified_numeric"] = bool(ok)
        resrec["residual_after"] = float(mag)
        if ok:
            cand_out = ROOT / "artifacts" / "hybrid_linfty_candidate_rerank.json"
            cand_record = {
                "rationalized_coeffs": [
                    str(Fraction(c).limit_denominator(720)) for c in cand
                ],
                "rationalized_coeffs_float": [float(c) for c in cand],
                "origin": "rerank_top",
            }
            cand_out.write_text(json.dumps(cand_record, indent=2), encoding="utf-8")
    cp_results.append(resrec)

OUT2 = ROOT / "artifacts" / "hybrid_rerank_rerun_results.json"
OUT2.write_text(
    json.dumps(
        {
            "selection_reason": reason,
            "candidates_tested": candidates[:max_tests],
            "cp_results": cp_results,
        },
        indent=2,
    ),
    encoding="utf-8",
)
print("Wrote", OUT2)
print("Done")
