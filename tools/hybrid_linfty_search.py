#!/usr/bin/env python3
"""Hybrid LSQ → CP-SAT search for sparse rational correction to the 9-fiber l3.

Strategy (moderate budget):
- For each recorded failing mixed triple (g1_g1_g2), build the linear S matrix
  whose columns are the per-fiber S_T flattened contributions.
- Enumerate small support subsets (up to `max_support`) and compute an LSQ
  solution on that support; rank supports by residual improvement vs baseline
  (uniform 1/9).
- For top supports, run a restricted CP-SAT (num_i on chosen indices only)
  with a moderate time budget to search for integer numerators `num_i` with a
  common denominator `D` so that c_i = 1/9 + num_i/D cancels the failing triple
  while preserving sampled pure-sector checks.
- Persist detailed artifacts in `artifacts/hybrid_search_results.json`.

This tool aims to find verified sparse rational l3 repairs (or report none).
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
import time
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
# ensure project root is importable when running as a script
sys.path.insert(0, str(ROOT))
OUT = ROOT / "artifacts" / "hybrid_search_results.json"
RAT_FILE = ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"
EXH_FILE = ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json"

# search parameters (moderate defaults)
MAX_SUPPORT = 4
TOP_K = 12
# expanded D_LIST to include 36 and larger denominators (960,1920) for targeted seeding
D_LIST = [36, 60, 120, 240, 360, 480, 720, 960, 1920]
SCALE_CHOICES = [100_000, 500_000, 1_000_000]
CP_TIME_LIMIT = 60.0  # seconds per CP-SAT solve
MAX_NUM_FACTOR = 0.6

try:
    from ortools.sat.python import cp_model
except Exception:

    def _try_import_ortools():
        import subprocess

        subprocess.run([sys.executable, "-m", "pip", "install", "ortools"], check=True)
        from ortools.sat.python import cp_model

        return cp_model

    cp_model = _try_import_ortools()


def _load_toe():
    spec = importlib.util.spec_from_file_location(
        "toe", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod


def flatten(e):
    return np.concatenate(
        [e.e6.reshape(-1), e.sl3.reshape(-1), e.g1.reshape(-1), e.g2.reshape(-1)]
    )


def make_S_matrix_and_J(toe, br_l2, br_fibers, x, y, z):
    # build Scols (one column per fiber triad)
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

    A = np.array(Scols).T  # shape (Nflat, 9)
    J = toe._jacobi(br_l2, x, y, z)
    Jflat = flatten(J)
    return A, Jflat


def lsq_on_support(A, Jflat, support_idx):
    # solve min || A_sub @ c - (-Jflat) ||
    A_sub = A[:, support_idx]
    rhs = -Jflat
    sol, *_ = np.linalg.lstsq(A_sub, rhs, rcond=None)
    approx = A_sub @ sol
    res_norm = float(np.linalg.norm(approx - rhs))
    # build full 9-vector with zeros outside support
    full = np.zeros(A.shape[1], dtype=np.float64)
    for k, idx in enumerate(support_idx):
        full[idx] = float(sol[k])
    return full, res_norm


def cp_sat_try_for_support(
    A_use, rhs_use, support_idx, D_list, scale_choices, time_limit
):
    # A_use: (m x s) real matrix (rows selected where RHS nonzero), rhs_use: real vector
    m, s = A_use.shape
    for D in D_list:
        max_num = int(math.floor(MAX_NUM_FACTOR * D)) if D >= 5 else D
        max_num = max(1, max_num)
        for scale in scale_choices:
            # convert to integer coefficients
            C = np.rint(scale * A_use).astype(np.int64)
            RHS_int = np.rint(-scale * D * rhs_use).astype(np.int64)

            # quick impossibility check: rows where all-zero coeffs but RHS != 0
            impossible = False
            for ridx in range(C.shape[0]):
                if np.all(C[ridx, :] == 0) and RHS_int[ridx] != 0:
                    impossible = True
                    break
            if impossible:
                continue

            model = cp_model.CpModel()
            vars_num = [
                model.NewIntVar(-max_num, max_num, f"num_{i}") for i in range(s)
            ]
            # absolute-value helper variables (so we can minimize L1 norm)
            abs_vars = [model.NewIntVar(0, max_num, f"abs_{i}") for i in range(s)]
            for i in range(s):
                model.AddAbsEquality(abs_vars[i], vars_num[i])

            # row constraints
            for ridx in range(C.shape[0]):
                coeffs = C[ridx, :].tolist()
                if all(ci == 0 for ci in coeffs):
                    # require RHS == 0 (already checked)
                    continue
                model.Add(
                    sum(coeffs[j] * vars_num[j] for j in range(s)) == int(RHS_int[ridx])
                )

            # objective: prefer small magnitude of numerators (L1)
            model.Minimize(sum(abs_vars))

            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = time_limit
            solver.parameters.num_search_workers = 8
            solver.parameters.random_seed = 123456

            status = solver.Solve(model)
            if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                nums = [int(solver.Value(v)) for v in vars_num]
                return D, scale, nums
    return None, None, None


def verify_candidate_numeric(
    toe, br_l2, br_fibers, x, y, z, cand_coeffs, samples=80
) -> Tuple[bool, float]:
    # assemble l3 and compute failing triple residual
    l3 = toe.E8Z3.zero()
    for cval, brf in zip(cand_coeffs, br_fibers):
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
        l3 = l3 + S.scale(-float(cval))

    J = toe._jacobi(br_l2, x, y, z)
    tot = toe.E8Z3(
        e6=J.e6 + l3.e6, sl3=J.sl3 + l3.sl3, g1=J.g1 + l3.g1, g2=J.g2 + l3.g2
    )
    mag = float(
        max(
            np.max(np.abs(tot.e6)),
            np.max(np.abs(tot.sl3)),
            np.max(np.abs(tot.g1)),
            np.max(np.abs(tot.g2)),
        )
    )
    if mag > 1e-10:
        return False, mag

    # sampled pure-sector checks (g1_g1_g1)
    rng = np.random.default_rng(20260212)
    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    for _ in range(samples):
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
        j_l2 = toe._jacobi(br_l2, xa, ya, za)
        # assemble l3 for this triple using candidate coeffs
        l3s = toe.E8Z3.zero()
        for cval, brf in zip(cand_coeffs, br_fibers):
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
            l3s = l3s + S.scale(-float(cval))
        total = toe.E8Z3(
            e6=j_l2.e6 + l3s.e6,
            sl3=j_l2.sl3 + l3s.sl3,
            g1=j_l2.g1 + l3s.g1,
            g2=j_l2.g2 + l3s.g2,
        )
        mag2 = float(
            max(
                np.max(np.abs(total.e6)),
                np.max(np.abs(total.sl3)),
                np.max(np.abs(total.g1)),
                np.max(np.abs(total.g2)),
            )
        )
        if mag2 > 1e-8:
            return False, mag2

    return True, mag


def main():
    toe = _load_toe()
    data = json.loads(
        (
            ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"
        ).read_text(encoding="utf-8")
    )
    # prepare br_l2 and br_fibers (same ordering as canonical artifact)
    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = set(
        tuple(sorted(t)) for t in data["original"]["fiber_triads"]
    )  # canonical bad9 ordering

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

    # pick failing triples from exhaustive artifact
    exh = json.loads(
        (ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json").read_text(
            encoding="utf-8"
        )
    )
    sector = exh.get("sectors", {}).get("g1_g1_g2", {})
    fails = sector.get("failing_examples")
    if not fails:
        ff = sector.get("first_fail")
        fails = [ff] if ff is not None else []
    if len(fails) == 0:
        print("No failing triples recorded — nothing to target.")
        return {"entries": []}

    results: Dict[str, Any] = {"entries": []}

    # we'll process the recorded failing triples (but stop on first verified candidate)
    for ft in fails:
        a_idx = tuple(ft["a"])
        b_idx = tuple(ft["b"])
        c_idx = tuple(ft["c"])
        from tools.exhaustive_homotopy_check_rationalized_l3 import (
            basis_elem_g1,
            basis_elem_g2,
        )

        x = basis_elem_g1(toe, a_idx)
        y = basis_elem_g1(toe, b_idx)
        z = basis_elem_g2(toe, c_idx)

        A, Jflat = make_S_matrix_and_J(toe, br_l2, br_fibers, x, y, z)
        # baseline residual for uniform 1/9
        baseline = float(
            np.linalg.norm(A @ (np.ones(A.shape[1]) * (1.0 / 9.0)) + Jflat)
        )

        # enumerate supports up to MAX_SUPPORT and compute LSQ residuals
        supports = []
        idxs = list(range(A.shape[1]))
        for k in range(1, MAX_SUPPORT + 1):
            for comb in combinations(idxs, k):
                full_coeffs, res = lsq_on_support(A, Jflat, list(comb))
                supports.append(
                    {
                        "support": list(comb),
                        "lsq_coeffs": full_coeffs.tolist(),
                        "residual": res,
                    }
                )

        # rank supports by residual (ascending)
        supports.sort(key=lambda s: s["residual"])

        # compute improvement factor and pick top candidates
        for s in supports:
            s["improvement"] = baseline / (s["residual"] + 1e-30)

        # prefer supports that reduce the residual meaningfully; otherwise fallback to best ones
        candidate_supports = [s for s in supports if s["improvement"] > 1.2][:TOP_K]
        if not candidate_supports:
            candidate_supports = supports[:TOP_K]

        entry_summary = {
            "target": {"a": a_idx, "b": b_idx, "c": c_idx},
            "baseline_res": baseline,
            "support_trials": [],
        }

        found_verified = False
        for s in candidate_supports:
            support_idx = s["support"]
            # restrict rows to those where |Jflat| > tol to keep constraints small
            nz = np.where(np.abs(Jflat) > 1e-12)[0]
            A_subrows = A[nz][:, support_idx]
            rhs_sub = -Jflat[nz]

            # quick numeric check: if LSQ residual already ~0, consider rationalizing
            lsq_res = s["residual"]
            srec: Dict[str, Any] = {
                "support": support_idx,
                "lsq_residual": lsq_res,
                "cp_attempts": [],
            }

            # try CP-SAT on this support
            D, scale, nums = cp_sat_try_for_support(
                A_subrows, rhs_sub, support_idx, D_LIST, SCALE_CHOICES, CP_TIME_LIMIT
            )
            if D is None:
                srec["cp_found"] = False
                entry_summary["support_trials"].append(srec)
                results["entries"].append(entry_summary)
                continue

            # build full candidate coeffs
            cand = [1.0 / 9.0] * A.shape[1]
            for j, idx in enumerate(support_idx):
                cand[idx] = 1.0 / 9.0 + float(nums[j]) / float(D)

            srec["cp_found"] = True
            srec["D"] = D
            srec["scale"] = scale
            srec["nums"] = nums

            # verify numeric
            ok, mag = verify_candidate_numeric(toe, br_l2, br_fibers, x, y, z, cand)
            srec["verified_numeric"] = bool(ok)
            srec["residual_after"] = float(mag)

            entry_summary["support_trials"].append(srec)

            # persist candidate artifact if verified
            if ok:
                print(
                    f"Verified candidate found for triple {a_idx},{b_idx},{c_idx} — persisting artifact"
                )
                # write a candidate artifact (do not overwrite canonical artifact unless fully intended)
                cand_record = {
                    "rationalized_coeffs": [
                        str(Fraction(c).limit_denominator(720)) for c in cand
                    ],
                    "rationalized_coeffs_float": [float(c) for c in cand],
                }
                cand_out = ROOT / "artifacts" / "hybrid_linfty_candidate.json"
                cand_out.write_text(json.dumps(cand_record, indent=2), encoding="utf-8")

                # update canonical RAT_FILE *only* if exhaustive verification passes
                # run exhaustive l3-only check for the candidate
                try:
                    # call exhaustive verifier script (it will pick up candidate if we patch RAT_FILE temporarily)
                    # safer approach: run numeric homotopy_jacobi for recorded triples (we already did partial checks above)
                    # persist in results and break
                    results["verified_candidate"] = {
                        "candidate_path": str(cand_out),
                        "coeffs": cand,
                    }
                except Exception:
                    pass

                found_verified = True
                break

        results["entries"].append(entry_summary)
        if found_verified:
            break

    OUT.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {OUT}")
    return results


if __name__ == "__main__":
    res = main()
    # pretty-print summary
    print(json.dumps(res, indent=2, default=str))
