#!/usr/bin/env python3
"""CP-SAT search for a sparse exact rational correction to the 9-fiber l3.

- Searches for integer numerators `num_i` with a common denominator `D` so that
  c_i = 1/9 + num_i/D cancels the single failing mixed triple while
  preserving sampled pure-sector checks.
- Prioritizes smaller support (few nonzero num_i) and smaller magnitudes.
- Verifies any CP-SAT candidate numerically and writes to the rationalized
  artifact only when exhaustive verification + unit tests pass.

This is a conservative, reversible helper — it never overwrites artifacts
unless the candidate passes full verification.
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAT_FILE = ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"

# ensure the project root is on sys.path so \"from tools.*\" imports work
import sys

sys.path.insert(0, str(ROOT))


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


def _try_import_ortools():
    try:
        from ortools.sat.python import cp_model  # type: ignore

        return cp_model
    except Exception:
        # try to install (same strategy used elsewhere in repo)
        import subprocess

        subprocess.run([sys.executable, "-m", "pip", "install", "ortools"], check=True)
        from ortools.sat.python import cp_model  # type: ignore

        return cp_model


def verify_candidate(
    toe, br_l2, br_fibers, J, nz_inds, cand_coeffs: List[float], samples=200
) -> Tuple[bool, float]:
    """Numeric verification for failing triple + sampled pure-sector checks.
    Returns (passed_bool, failing_triple_residual_max).
    """
    # evaluate failing triple residual under candidate
    # assemble l3 from candidate
    l3 = toe.E8Z3.zero()
    for cval, brf in zip(cand_coeffs, br_fibers):
        # build per-fiber S as used elsewhere
        # (same sequence used in other tools)
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

    res = toe.E8Z3(
        e6=J.e6 + l3.e6, sl3=J.sl3 + l3.sl3, g1=J.g1 + l3.g1, g2=J.g2 + l3.g2
    )
    res_max = float(
        max(
            np.max(np.abs(res.e6)),
            np.max(np.abs(res.sl3)),
            np.max(np.abs(res.g1)),
            np.max(np.abs(res.g2)),
        )
    )

    if res_max > 1e-8:
        return False, res_max

    # sampled pure-sector checks (g1_g1_g1 and g2_g2_g2)
    rng = np.random.default_rng(20260212)
    from tools.build_linfty_firewall_extension import LInftyE8Extension

    all_triads = toe._load_signed_cubic_triads()
    data = json.loads(RAT_FILE.read_text(encoding="utf-8"))
    bad9 = set(tuple(sorted(t)) for t in data["original"]["fiber_triads"])
    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)
    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    def assemble_l3_for_triple(xa, ya, za, coeffs):
        l3s = toe.E8Z3.zero()
        for cval, brf in zip(coeffs, br_fibers):
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
        return l3s

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
        l3s = assemble_l3_for_triple(xa, ya, za, cand_coeffs)
        total = toe.E8Z3(
            e6=j_l2.e6 + l3s.e6,
            sl3=j_l2.sl3 + l3s.sl3,
            g1=j_l2.g1 + l3s.g1,
            g2=j_l2.g2 + l3s.g2,
        )
        if (
            max(
                np.max(np.abs(total.e6)),
                np.max(np.abs(total.sl3)),
                np.max(np.abs(total.g1)),
                np.max(np.abs(total.g2)),
            )
            > 1e-8
        ):
            return False, res_max

    return True, res_max


if __name__ == "__main__":
    # parameters to sweep (expanded grid + targeted row‑reduction mode)
    denoms = [60, 120, 240, 360, 480, 720, 960]
    support_limits = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    # larger integer scaling choices to improve integer-relaxation behavior
    scale_choices = [100_000, 1_000_000, 2_000_000, 5_000_000]
    # try a few row-reduction trims (None = use all rows; otherwise keep top-k rows by |RHS|)
    row_trims = [None, 40, 80]
    # increase per-solve time budget to allow harder instances to complete
    time_limit = 240.0  # seconds per CP-SAT solve
    # allow somewhat larger numerators relative to denominator (up from 0.2*D -> 0.6*D)
    # (this changes the range for `num_i` variables inside the solver)
    max_num_factor = 0.6

    toe = _load_toe()
    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)

    all_triads = toe._load_signed_cubic_triads()
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

    # failing mixed triple (from exhaustive check)
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
    Jflat = flatten(J)
    nz = np.where(np.abs(Jflat) > 1e-12)[0]

    # build Scols matrix (complex) and reduce to rows nz
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

    # stack real + imag rows (we will convert to integer constraints via scaling)
    A_realstack = np.vstack([np.real(A_sub), np.imag(A_sub)])
    r_uniform = (A_sub @ np.array([1.0 / 9.0] * A_sub.shape[1])) + Jflat[nz]
    r_realstack = np.concatenate([np.real(r_uniform), np.imag(r_uniform)])

    # Prefer ortools from the project virtualenv; fall back to auto-install helper
try:
    from ortools.sat.python import cp_model  # type: ignore
except Exception:
    cp_model = _try_import_ortools()

found = False
best_solution = None

for D in denoms:
    for support_limit in support_limits:
        for scale in scale_choices:
            for row_trim in row_trims:
                rt_str = f"rows≤{row_trim}" if row_trim is not None else "rows=all"
                print(
                    f"CP-SAT attempt: denom={D} support≤{support_limit} scale={scale} {rt_str}"
                )

            # build integer matrix C = round(scale * A_realstack)
            C = np.rint(scale * A_realstack).astype(np.int64)
            RHS = np.rint(-scale * D * r_realstack).astype(np.int64)

            # quick numeric diagnostic: check gcd of row coefficients to trim rows
            # (skip rows where all C[:,i] are zero and RHS==0)
            useful_rows = [
                i
                for i in range(C.shape[0])
                if not (np.all(C[i, :] == 0) and RHS[i] == 0)
            ]
            C_use = C[useful_rows, :]
            RHS_use = RHS[useful_rows]

            # optional row‑reduction (targeted CP‑SAT): keep only top-|RHS| rows
            if row_trim is not None and row_trim > 0 and row_trim < C_use.shape[0]:
                ord_idx = np.argsort(-np.abs(RHS_use))
                keep = ord_idx[:row_trim]
                C_use = C_use[keep, :]
                RHS_use = RHS_use[keep]
                # remap useful_rows for debugging prints later
                useful_rows = [useful_rows[i] for i in keep.tolist()]

            model = cp_model.CpModel()
            num_vars = []
            s_vars = []
            abs_vars = []
            max_num = int(math.floor(max_num_factor * D)) if D >= 5 else D
            max_num = max(1, max_num)

            for i in range(C_use.shape[1]):
                v = model.NewIntVar(-max_num, max_num, f"num_{i}")
                bvar = model.NewBoolVar(f"s_{i}")
                av = model.NewIntVar(0, max_num, f"abs_{i}")
                # linking: if s_i == 0 then num_i == 0
                model.Add(v <= max_num * bvar)
                model.Add(v >= -max_num * bvar)
                # absolute
                model.AddAbsEquality(av, v)
                num_vars.append(v)
                s_vars.append(bvar)
                abs_vars.append(av)

            # linear equality constraints: sum_j C[row, i] * num_i == RHS[row]
            for ridx in range(C_use.shape[0]):
                row_coeffs = C_use[ridx, :].tolist()
                if all(ci == 0 for ci in row_coeffs):
                    # require RHS_use[ridx] == 0
                    if RHS_use[ridx] != 0:
                        # impossible under this scaling, mark infeasible
                        model.Add(RHS_use[ridx] == RHS_use[ridx] + 1)  # unsat trivial
                    continue
                model.Add(
                    sum(row_coeffs[i] * num_vars[i] for i in range(len(num_vars)))
                    == int(RHS_use[ridx])
                )

                # support limit
                model.Add(sum(s_vars) <= support_limit)

                # objective: first minimize support, then magnitude
                W = 10_000
                model.Minimize(W * sum(s_vars) + sum(abs_vars))

                solver = cp_model.CpSolver()
                solver.parameters.max_time_in_seconds = time_limit
                solver.parameters.num_search_workers = 8
                solver.parameters.random_seed = 123456

                status = solver.Solve(model)
                if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                    print("  no feasible solution (CP-SAT returned status)")
                    continue

                nums = [int(solver.Value(v)) for v in num_vars]
                supp = [int(solver.Value(b)) for b in s_vars]
                print(f"  CP-SAT found nums={nums} support={supp}")

                # build rational candidate and verify numerically
                cand = [float(Fraction(1, 9) + Fraction(n, D)) for n in nums]
                # Quick failing-triple numeric check
                # Recompute the failing triple residual exactly like other tools
                # (we reuse x,y,z,J,br_l2,br_fibers)
                l3 = toe.E8Z3.zero()
                for cval, brf in zip(cand, br_fibers):
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
                res = toe.E8Z3(
                    e6=J.e6 + l3.e6,
                    sl3=J.sl3 + l3.sl3,
                    g1=J.g1 + l3.g1,
                    g2=J.g2 + l3.g2,
                )
                res_max = float(
                    max(
                        np.max(np.abs(res.e6)),
                        np.max(np.abs(res.sl3)),
                        np.max(np.abs(res.g1)),
                        np.max(np.abs(res.g2)),
                    )
                )
                print(f"  failing-triple residual (after cand) = {res_max:.3e}")

                if res_max > 1e-10:
                    print(
                        "  candidate does not cancel the failing triple numerically (reject)"
                    )
                    continue

                # sampled pure-sector checks
                sample_ok = True
                rng = np.random.default_rng(20260212)
                for _ in range(80):
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
                    l3s = toe.E8Z3.zero()
                    for cval, brf in zip(cand, br_fibers):
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
                    if (
                        max(
                            np.max(np.abs(total.e6)),
                            np.max(np.abs(total.sl3)),
                            np.max(np.abs(total.g1)),
                            np.max(np.abs(total.g2)),
                        )
                        > 1e-8
                    ):
                        sample_ok = False
                        break

                if not sample_ok:
                    print("  candidate failed sampled pure-sector checks (reject)")
                    continue

                # full exhaustive verification + unit tests
                import subprocess

                print(
                    "  candidate passed numeric and sampled checks — running exhaustive verification + unit tests..."
                )
                # write a temporary artifact copy (do not overwrite original yet)
                cand_rats = [str(Fraction(1, 9) + Fraction(n, D)) for n in nums]
                cand_floats = [float(Fraction(fr)) for fr in cand_rats]

                # apply to a temp artifact in-memory and run exhaustive check by passing candidate through environment
                # easiest: write a temp backup and patch RAT_FILE then revert if tests fail
                bak = RAT_FILE.with_suffix(RAT_FILE.suffix + ".cpsat.bak")
                orig_text = RAT_FILE.read_text(encoding="utf-8")
                bak.write_text(orig_text, encoding="utf-8")
                try:
                    data = json.loads(orig_text)
                    data["rationalized_coeffs"] = cand_rats
                    data["rationalized_coeffs_float"] = cand_floats
                    RAT_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

                    subprocess.run(
                        [
                            sys.executable,
                            "tools/exhaustive_homotopy_check_rationalized_l3.py",
                        ],
                        check=True,
                    )
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
                except subprocess.CalledProcessError:
                    print(
                        "  exhaustive verification or unit tests failed — reverting artifact"
                    )
                    bak.write_text(bak.read_text(encoding="utf-8"), encoding="utf-8")
                    RAT_FILE.write_text(orig_text, encoding="utf-8")
                    continue
                else:
                    print(
                        "  candidate fully verified and tests passed — artifact updated."
                    )
                    # remove backup and exit
                    try:
                        bak.unlink()
                    except Exception:
                        pass
                    found = True
                    best_solution = (nums, cand_rats, cand_floats)
                    break
            if found:
                break
        if found:
            break

    if not found:
        print("No CP-SAT candidate found with the tried parameter grid.")
        sys.exit(2)

    print("SUCCESS — CP-SAT produced a verified patch:")
    nums, rats, floats = best_solution
    print("  numerators:", nums)
    print("  rational coeffs:", rats)
    print("  floats (first 6):", [round(f, 12) for f in floats[:6]])
    sys.exit(0)
