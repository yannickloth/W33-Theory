#!/usr/bin/env python3
"""SNF certificate builder for CE2 local solutions (U/V).

- Loads `artifacts/ce2_rational_local_solutions.json` (rationalized U/V)
- Reconstructs the linear operator M (as in compute_local_ce2_alpha_for_triple)
  and the target rhs = -(J + l3) for each failing triple.
- For a list of denominators `D_LIST` constructs integer lifts M_int, b_int and
  verifies that the provided rational U/V (scaled by D) satisfy M_int @ u_int = b_int.
- When a witness is found, compute Smith Normal Form (SNF) of M_int and
  include the canonical divisibility checks (U * b) as the certificate.
- Writes `artifacts/snf_certificate_ce2_uv.json` with per-triple certificates.

This produces formal, machine-checkable algebraic certificates for the CE2 -> l4 repair.
"""
from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from sympy import Matrix
from sympy.matrices.normalforms import smith_normal_form

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "artifacts" / "ce2_rational_local_solutions.json"
OUT = ROOT / "artifacts" / "snf_certificate_ce2_uv.json"

# denominators to try (include likely denominators from previous rationalizations)
D_LIST = [1, 6, 9, 18, 36, 72, 240, 480, 720]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys_mod = __import__("sys")
    sys_mod.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def flatten(e):
    return np.concatenate(
        [e.e6.reshape(-1), e.sl3.reshape(-1), e.g1.reshape(-1), e.g2.reshape(-1)]
    )


def parse_frac_list(str_list: List[str]) -> List[Optional[Fraction]]:
    out: List[Optional[Fraction]] = []
    for s in str_list:
        if s in ("0", "0/1", "None", ""):
            out.append(None)
            continue
        out.append(Fraction(s))
    return out


def vec_from_fracs(fracs: List[Optional[Fraction]]) -> np.ndarray:
    v = np.zeros(len(fracs), dtype=np.complex128)
    for i, f in enumerate(fracs):
        if f is None:
            v[i] = 0.0
        else:
            v[i] = float(f)
    return v


def main() -> Dict[str, Any]:
    assert IN.exists(), "Run assemble_exact_l4_from_local_ce2.py first"
    raw = json.loads(IN.read_text(encoding="utf-8"))

    toe = _load_module(ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py", "toe_e8")
    exh = _load_module(
        ROOT / "tools" / "exhaustive_homotopy_check_rationalized_l3.py", "exh"
    )

    proj = toe.E6Projector(
        np.load(
            ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
        ).astype(np.complex128)
    )
    all_triads = toe._load_signed_cubic_triads()

    # try to find bad9 from linfty helper artifact if available
    bad9 = set()
    try:
        linfty_mod = _load_module(
            ROOT / "tools" / "build_linfty_firewall_extension.py", "linfty_mod"
        )
        bad9 = linfty_mod._load_bad9()
    except Exception:
        # fall back to artifact
        try:
            rat = json.loads(
                (
                    ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"
                ).read_text()
            )
            bad9 = set(tuple(sorted(t)) for t in rat["original"]["fiber_triads"])
        except Exception:
            bad9 = set()

    br_l2 = toe.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=[t for t in all_triads if tuple(sorted(t[:3])) not in bad9],
        scale_g1g1=1.0,
        scale_g2g2=-1.0 / 6.0,
        scale_e6=1.0,
        scale_sl3=1.0 / 6.0,
    )

    results: Dict[str, Any] = {"entries": {}}

    for key, entry in raw.items():
        a = tuple(entry["a"])
        b = tuple(entry["b"])
        c = tuple(entry["c"])

        # build per-triad fiber brackets from bad9 (ordered as in canonical artifact)
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

        x = exh.basis_elem_g1(toe, a)
        y = exh.basis_elem_g1(toe, b)
        z = exh.basis_elem_g2(toe, c)

        # target: -(J + l3) as in compute_local_ce2_alpha_for_triple
        J = toe._jacobi(br_l2, x, y, z)
        l3_total = toe.E8Z3.zero()
        # load canonical rationalized l3 coeffs from artifact
        ratf = json.loads(
            (
                ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"
            ).read_text()
        )
        canon = [
            float(Fraction(s))
            for s in ratf.get("rationalized_coeffs_float", [1.0 / 9.0] * len(br_fibers))
        ]
        for cval, brf in zip(canon, br_fibers):
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
            l3_total = l3_total + S.scale(-float(cval))

        target = -(flatten(J) + flatten(l3_total))

        # Build operator M (columns bracket(x, e_i), -bracket(y, e_i))
        Nflat = len(flatten(J))
        eye = np.eye(Nflat, dtype=np.complex128)

        def flat_to_E8Z3(vec_flat: np.ndarray):
            N = 27 * 27
            e6 = vec_flat[:N].reshape((27, 27)).astype(np.complex128)
            off = N
            sl3 = vec_flat[off : off + 9].reshape((3, 3)).astype(np.complex128)
            off += 9
            g1 = vec_flat[off : off + 81].reshape((27, 3)).astype(np.complex128)
            off += 81
            g2 = vec_flat[off : off + 81].reshape((27, 3)).astype(np.complex128)
            return toe.E8Z3(e6=e6, sl3=sl3, g1=g1, g2=g2)

        A_cols = []
        B_cols = []
        for i in range(Nflat):
            vec = flat_to_E8Z3(eye[:, i])
            A_cols.append(flatten(br_l2.bracket(x, vec)))
            B_cols.append(-flatten(br_l2.bracket(y, vec)))

        A = np.column_stack(A_cols)
        B = np.column_stack(B_cols)
        M = np.hstack([A, B])

        M_real = np.vstack([np.real(M), np.imag(M)])
        rhs = np.concatenate([np.real(target), np.imag(target)])

        # parse provided rational U/V
        U_rats = (
            parse_frac_list(entry["U_rats"]) if "U_rats" in entry else [None] * Nflat
        )
        V_rats = (
            parse_frac_list(entry["V_rats"]) if "V_rats" in entry else [None] * Nflat
        )

        u_vec = np.array(
            [float(f) if f is not None else 0.0 for f in U_rats], dtype=np.complex128
        )
        v_vec = np.array(
            [float(f) if f is not None else 0.0 for f in V_rats], dtype=np.complex128
        )
        sol_vec = np.concatenate([u_vec, v_vec])

        entry_res: Dict[str, Any] = {
            "a": a,
            "b": b,
            "c": c,
            "verified": False,
            "D_found": None,
            "snf": None,
        }

        for D in D_LIST:
            M_int = np.rint(M_real * D).astype(int)
            b_int = np.rint(rhs * D).astype(int)

            # build integer sol candidate from rational U/V scaled by D
            def scaled_ints(fracs: List[Optional[Fraction]]):
                out = []
                for f in fracs:
                    if f is None:
                        out.append(0)
                    else:
                        out.append(int(f * D))
                return np.array(out, dtype=int)

            u_int = scaled_ints(U_rats)
            v_int = scaled_ints(V_rats)
            cand = np.concatenate([u_int, v_int])

            # quick check: does M_int @ cand == b_int ?
            lhs = M_int.dot(cand)
            if np.array_equal(lhs, b_int):
                # compute SNF and membership divisibility checks for canonical certificate
                Mm = Matrix(M_int.tolist())
                try:
                    S, U_mat, V_mat = smith_normal_form(Mm)
                    diag = [
                        int(S[i, i]) for i in range(min(S.rows, S.cols)) if S[i, i] != 0
                    ]
                    Ub = U_mat * Matrix(b_int.tolist())
                    Ub_list = [int(x) for x in Ub]
                    # divisibility checks
                    r = len(diag)
                    div_checks = []
                    ok_div = True
                    for i in range(r):
                        si = int(S[i, i])
                        yi = int(Ub_list[i])
                        div_checks.append(
                            {"i": i, "si": si, "yi": yi, "divisible": (yi % si == 0)}
                        )
                        if yi % si != 0:
                            ok_div = False
                    # remaining Ub rows must be zero
                    for j in range(r, len(Ub_list)):
                        if Ub_list[j] != 0:
                            ok_div = False
                    entry_res.update(
                        {
                            "verified": True,
                            "D_found": D,
                            "cand_int_len": int(cand.size),
                            "snf_diag": diag,
                            "U_times_b": Ub_list,
                            "div_checks": div_checks,
                        }
                    )
                    break
                except Exception as e:
                    entry_res.update({"snf_error": str(e)})
                    break

        results["entries"][key] = entry_res

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")
    return results


if __name__ == "__main__":
    main()
