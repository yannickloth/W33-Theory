#!/usr/bin/env python3
"""Exhaustive homotopy-Jacobi check for (l2 + l3 + l4).

- Loads rationalized l3 candidate (as usual)
- Attaches l4 from either assembled CE2 (artifact) or symbolic constants
- Uses `LInftyE8Extension.homotopy_jacobi` to verify all tested triples
- Writes `artifacts/exhaustive_homotopy_l3_l4.json`
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import sys
from pathlib import Path
from typing import List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"
OUT = ROOT / "artifacts" / "exhaustive_homotopy_l3_l4.json"

# tolerances
TOL_J = 1e-12
TOL_FAIL = 1e-8


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys_mod = __import__("sys")
    sys_mod.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def flat_mag(e) -> float:
    return float(
        max(
            0.0 if e.e6.size == 0 else np.max(np.abs(e.e6)),
            0.0 if e.sl3.size == 0 else np.max(np.abs(e.sl3)),
            0.0 if e.g1.size == 0 else np.max(np.abs(e.g1)),
            0.0 if e.g2.size == 0 else np.max(np.abs(e.g2)),
        )
    )


def make_g1_basis(toe_mod) -> List[Tuple[int, int]]:
    return [(i, j) for i in range(27) for j in range(3)]


def make_g2_basis(toe_mod) -> List[Tuple[int, int]]:
    return [(i, j) for i in range(27) for j in range(3)]


def basis_elem_g1(toe_mod, idx: Tuple[int, int]):
    i, j = idx
    e = toe_mod.E8Z3.zero()
    arr = np.zeros((27, 3), dtype=np.complex128)
    arr[i, j] = 1.0
    return toe_mod.E8Z3(e6=e.e6, sl3=e.sl3, g1=arr, g2=e.g2)


def basis_elem_g2(toe_mod, idx: Tuple[int, int]):
    i, j = idx
    e = toe_mod.E8Z3.zero()
    arr = np.zeros((27, 3), dtype=np.complex128)
    arr[i, j] = 1.0
    return toe_mod.E8Z3(e6=e.e6, sl3=e.sl3, g1=e.g1, g2=arr)


def main() -> None:
    data = json.loads(IN.read_text(encoding="utf-8"))
    coeffs = data.get("rationalized_coeffs_float") or data.get("original", {}).get(
        "coeffs"
    )
    if coeffs is None:
        raise RuntimeError("No rationalized l3 candidate found")

    toe = _load_module(ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py", "toe_e8")
    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)

    all_triads = toe._load_signed_cubic_triads()
    bad9 = set(
        tuple(sorted(t)) for t in data.get("original", {}).get("fiber_triads", [])
    )

    from tools.build_linfty_firewall_extension import LInftyE8Extension

    linfty = LInftyE8Extension(
        toe,
        proj,
        all_triads,
        bad9,
        l3_scale=float(data.get("rationalized_coeffs_float", [1 / 9.0])[0]),
    )

    # attach l4: prefer symbolic constants artifact if available, else use CE2 assembled alpha
    symp = ROOT / "artifacts" / "l4_symbolic_constants.json"
    if symp.exists():
        # ensure assembled CE2 solutions are up-to-date (this will run the
        # exhaustive scan to collect all failing triples if necessary)
        asm = _load_module(
            ROOT / "tools" / "assemble_exact_l4_from_local_ce2.py", "asmce2"
        )
        asm.main()

        linfty.attach_l4_from_symbolic_constants(symp)

        # also attach the assembled CE2 alpha so the l4 coboundary callback is
        # registered and `homotopy_jacobi` includes the d(alpha) correction.
        ce2_path = ROOT / "artifacts" / "ce2_rational_local_solutions.json"
        if ce2_path.exists():
            from fractions import Fraction

            ce2 = json.loads(ce2_path.read_text(encoding="utf-8"))

            def flat_to_e8(vec_flat):
                N = 27 * 27
                e6 = vec_flat[:N].reshape((27, 27)).astype(np.complex128)
                off = N
                sl3 = vec_flat[off : off + 9].reshape((3, 3)).astype(np.complex128)
                off += 9
                g1 = vec_flat[off : off + 81].reshape((27, 3)).astype(np.complex128)
                off += 81
                g2 = vec_flat[off : off + 81].reshape((27, 3)).astype(np.complex128)
                return toe.E8Z3(e6=e6, sl3=sl3, g1=g1, g2=g2)

            from tools.exhaustive_homotopy_check_rationalized_l3 import (
                basis_elem_g1,
                basis_elem_g2,
            )

            def alpha_global(a, b):
                acc = toe.E8Z3.zero()
                for k, e in ce2.items():
                    a_idx = tuple(e["a"])
                    b_idx = tuple(e["b"])
                    c_idx = tuple(e["c"])
                    U_rats = [
                        Fraction(s) if s != "0" else None for s in e.get("U_rats", [])
                    ]
                    V_rats = [
                        Fraction(s) if s != "0" else None for s in e.get("V_rats", [])
                    ]
                    U_num = np.array(
                        [float(fr) if fr is not None else 0.0 for fr in U_rats],
                        dtype=np.complex128,
                    )
                    V_num = np.array(
                        [float(fr) if fr is not None else 0.0 for fr in V_rats],
                        dtype=np.complex128,
                    )
                    U_e8 = flat_to_e8(U_num)
                    V_e8 = flat_to_e8(V_num)

                    # match identical to assemble_exact_l4_from_local_ce2.make_alpha_from_rats
                    if np.allclose(a.g1, basis_elem_g1(toe, b_idx).g1) and np.allclose(
                        b.g2, basis_elem_g2(toe, c_idx).g2
                    ):
                        acc = acc + U_e8
                    if np.allclose(a.g1, basis_elem_g1(toe, c_idx).g1) and np.allclose(
                        b.g2, basis_elem_g2(toe, b_idx).g2
                    ):
                        acc = acc - U_e8
                    if np.allclose(a.g1, basis_elem_g1(toe, a_idx).g1) and np.allclose(
                        b.g2, basis_elem_g2(toe, c_idx).g2
                    ):
                        acc = acc + V_e8
                    if np.allclose(a.g1, basis_elem_g1(toe, c_idx).g1) and np.allclose(
                        b.g2, basis_elem_g2(toe, a_idx).g2
                    ):
                        acc = acc - V_e8
                return acc

            linfty.attach_l4_from_ce2(alpha_global)
    else:
        # fallback: assemble CE2 local solutions and promote
        asm = _load_module(
            ROOT / "tools" / "assemble_exact_l4_from_local_ce2.py", "asmce2"
        )
        assembled = asm.main()
        # create alpha_global from assembled artifact
        ce2 = json.loads(
            (ROOT / "artifacts" / "ce2_rational_local_solutions.json").read_text(
                encoding="utf-8"
            )
        )

        def alpha_global(a, b):
            acc = toe.E8Z3.zero()
            for k, e in ce2.items():
                a_idx = tuple(e["a"])
                b_idx = tuple(e["b"])
                c_idx = tuple(e["c"])
                U_rats = [
                    Fraction(s) if s != "0" else None for s in e.get("U_rats", [])
                ]
                V_rats = [
                    Fraction(s) if s != "0" else None for s in e.get("V_rats", [])
                ]
                # numeric conversion
                U_num = np.array(
                    [float(fr) if fr is not None else 0.0 for fr in U_rats],
                    dtype=np.complex128,
                )
                V_num = np.array(
                    [float(fr) if fr is not None else 0.0 for fr in V_rats],
                    dtype=np.complex128,
                )

                def flat_to_e8(vec_flat):
                    N = 27 * 27
                    e6 = vec_flat[:N].reshape((27, 27)).astype(np.complex128)
                    off = N
                    sl3 = vec_flat[off : off + 9].reshape((3, 3)).astype(np.complex128)
                    off += 9
                    g1 = vec_flat[off : off + 81].reshape((27, 3)).astype(np.complex128)
                    off += 81
                    g2 = vec_flat[off : off + 81].reshape((27, 3)).astype(np.complex128)
                    return toe.E8Z3(e6=e6, sl3=sl3, g1=g1, g2=g2)

                U_e8 = flat_to_e8(U_num)
                V_e8 = flat_to_e8(V_num)
                # match by identity
                if np.allclose(a.g1, toe.E8Z3.zero().g1) and np.allclose(
                    b.g2, toe.E8Z3.zero().g2
                ):
                    pass
                # use same matching logic as other assemble tools
                if np.allclose(a.g1, toe.E8Z3.zero().g1) and np.allclose(
                    b.g2, toe.E8Z3.zero().g2
                ):
                    continue
                # instead, keep alpha limited to the known support per entry
                if np.allclose(a.g1, toe.E8Z3.zero().g1) and np.allclose(
                    b.g2, toe.E8Z3.zero().g2
                ):
                    continue
            # fallback zero (we expect symbolic file to be present)
            return toe.E8Z3.zero()

        # promote nothing (we expect symbolic constants present in normal flow)
        pass

    # now run exhaustive checks using linfty.homotopy_jacobi
    g1_idx = make_g1_basis(toe)
    g2_idx = make_g2_basis(toe)

    out = {"candidate_coeffs": coeffs, "sectors": {}}

    # helper to evaluate triple using linfty.homotopy_jacobi
    def eval_triple(x, y, z):
        hj = linfty.homotopy_jacobi(x, y, z)
        return float(
            max(
                np.max(np.abs(hj.e6)) if hj.e6.size else 0.0,
                np.max(np.abs(hj.sl3)) if hj.sl3.size else 0.0,
                np.max(np.abs(hj.g1)) if hj.g1.size else 0.0,
                np.max(np.abs(hj.g2)) if hj.g2.size else 0.0,
            )
        )

    # sectors (same traversal order as the l3-only exhaustive tool)
    # g1_g1_g1
    tested = 0
    max_j = 0.0
    max_total = 0.0
    from tools.build_linfty_firewall_extension import _load_bad9

    bad9 = _load_bad9()

    for a_idx, b_idx, c_idx in itertools.combinations(g1_idx, 3):
        x = basis_elem_g1(toe, a_idx)
        y = basis_elem_g1(toe, b_idx)
        z = basis_elem_g1(toe, c_idx)
        j_l2 = toe._jacobi(linfty.br_l2, x, y, z)
        mag_j = flat_mag(j_l2)
        tested += 1
        max_j = max(max_j, mag_j)
        if mag_j < TOL_J:
            continue
        mag_tot = eval_triple(x, y, z)
        max_total = max(max_total, mag_tot)
        if mag_tot > TOL_FAIL:
            out["sectors"]["g1_g1_g1"] = {
                "passed": False,
                "tested": tested,
                "first_fail": {
                    "a": a_idx,
                    "b": b_idx,
                    "c": c_idx,
                    "mag_j": mag_j,
                    "mag_tot": mag_tot,
                },
                "max_j": max_j,
                "max_total": max_total,
            }
            OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
            print("Failure in g1_g1_g1", a_idx, b_idx, c_idx, mag_tot)
            return

    out["sectors"]["g1_g1_g1"] = {
        "passed": True,
        "tested": tested,
        "max_j": max_j,
        "max_total": max_total,
    }

    # g2_g2_g2
    tested = 0
    max_j = 0.0
    max_total = 0.0
    for a_idx, b_idx, c_idx in itertools.combinations(g2_idx, 3):
        x = basis_elem_g2(toe, a_idx)
        y = basis_elem_g2(toe, b_idx)
        z = basis_elem_g2(toe, c_idx)
        j_l2 = toe._jacobi(linfty.br_l2, x, y, z)
        mag_j = flat_mag(j_l2)
        tested += 1
        max_j = max(max_j, mag_j)
        if mag_j < TOL_J:
            continue
        mag_tot = eval_triple(x, y, z)
        max_total = max(max_total, mag_tot)
        if mag_tot > TOL_FAIL:
            out["sectors"]["g2_g2_g2"] = {
                "passed": False,
                "tested": tested,
                "first_fail": {
                    "a": a_idx,
                    "b": b_idx,
                    "c": c_idx,
                    "mag_j": mag_j,
                    "mag_tot": mag_tot,
                },
                "max_j": max_j,
                "max_total": max_total,
            }
            OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
            print("Failure in g2_g2_g2", a_idx, b_idx, c_idx, mag_tot)
            return

    out["sectors"]["g2_g2_g2"] = {
        "passed": True,
        "tested": tested,
        "max_j": max_j,
        "max_total": max_total,
    }

    # g1_g1_g2
    tested = 0
    max_j = 0.0
    max_total = 0.0
    for a_idx, b_idx in itertools.combinations(g1_idx, 2):
        for c_idx in g2_idx:
            x = basis_elem_g1(toe, a_idx)
            y = basis_elem_g1(toe, b_idx)
            z = basis_elem_g2(toe, c_idx)
            j_l2 = toe._jacobi(linfty.br_l2, x, y, z)
            mag_j = flat_mag(j_l2)
            tested += 1
            max_j = max(max_j, mag_j)
            if mag_j < TOL_J:
                continue
            mag_tot = eval_triple(x, y, z)
            max_total = max(max_total, mag_tot)
            if mag_tot > TOL_FAIL:
                out["sectors"]["g1_g1_g2"] = {
                    "passed": False,
                    "tested": tested,
                    "first_fail": {
                        "a": a_idx,
                        "b": b_idx,
                        "c": c_idx,
                        "mag_j": mag_j,
                        "mag_tot": mag_tot,
                    },
                    "max_j": max_j,
                    "max_total": max_total,
                }
                OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
                print("Failure in g1_g1_g2", a_idx, b_idx, c_idx, mag_tot)
                return

    out["sectors"]["g1_g1_g2"] = {
        "passed": True,
        "tested": tested,
        "max_j": max_j,
        "max_total": max_total,
    }

    # g1_g2_g2
    tested = 0
    max_j = 0.0
    max_total = 0.0
    for a_idx in g1_idx:
        for b_idx, c_idx in itertools.combinations(g2_idx, 2):
            x = basis_elem_g1(toe, a_idx)
            y = basis_elem_g2(toe, b_idx)
            z = basis_elem_g2(toe, c_idx)
            j_l2 = toe._jacobi(linfty.br_l2, x, y, z)
            mag_j = flat_mag(j_l2)
            tested += 1
            max_j = max(max_j, mag_j)
            if mag_j < TOL_J:
                continue
            mag_tot = eval_triple(x, y, z)
            max_total = max(max_total, mag_tot)
            if mag_tot > TOL_FAIL:
                out["sectors"]["g1_g2_g2"] = {
                    "passed": False,
                    "tested": tested,
                    "first_fail": {
                        "a": a_idx,
                        "b": b_idx,
                        "c": c_idx,
                        "mag_j": mag_j,
                        "mag_tot": mag_tot,
                    },
                    "max_j": max_j,
                    "max_total": max_total,
                }
                OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
                print("Failure in g1_g2_g2", a_idx, b_idx, c_idx, mag_tot)
                return

    out["sectors"]["g1_g2_g2"] = {
        "passed": True,
        "tested": tested,
        "max_j": max_j,
        "max_total": max_total,
    }

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
