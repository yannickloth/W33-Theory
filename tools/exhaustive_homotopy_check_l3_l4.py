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
import os
import sys
from concurrent.futures import ThreadPoolExecutor
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
    import argparse

    parser = argparse.ArgumentParser(description="Exhaustive homotopy L3/L4 check")
    default_workers = max(1, min(4, int(os.cpu_count() or 1)))
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=default_workers,
        help="number of worker threads for jacobi screening",
    )
    parser.add_argument(
        "--skip-assemble",
        action="store_true",
        help="skip running CE2 assembly (faster local smoke)",
    )
    parser.add_argument(
        "--ce2-mode",
        choices=["predictor", "artifact"],
        default="artifact",
        help="use global Weil predictor or assembled CE2 artifact (default)",
    )
    # Allow this tool to be called from within other runners (e.g. pytest)
    # where unrelated CLI flags may be present on sys.argv.
    args, _unknown = parser.parse_known_args()
    nworkers = int(args.workers)
    skip_assemble = bool(args.skip_assemble)
    ce2_mode = str(args.ce2_mode)

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

    # l3 coefficients: the rationalized artifact stores a per-fiber-triad vector.
    # LInftyE8Extension supports either a scalar (uniform) or a per-triad list/tuple.
    coeffs_vec = data.get("rationalized_coeffs_float") or data.get("original", {}).get(
        "coeffs"
    )
    if not (isinstance(coeffs_vec, list) and len(coeffs_vec) == 9):
        coeffs_vec = None

    l3_scale = (1.0 / 9.0) if ce2_mode == "predictor" else coeffs_vec
    if l3_scale is None:
        l3_scale = 1.0 / 9.0

    linfty = LInftyE8Extension(
        toe,
        proj,
        all_triads,
        bad9,
        l3_scale=l3_scale,
    )

    # Attach l4 (symbolic constants) and choose how to supply the CE2 coboundary:
    #   - predictor: global metaplectic/Weil closed form (no per-triple lookup)
    #   - artifact: assembled per-triple CE2 table (legacy, heavy)
    symp = ROOT / "artifacts" / "l4_symbolic_constants.json"
    if symp.exists():
        if ce2_mode == "artifact":
            # Only assemble when the CE2 artifact is missing (the normal repo
            # flow is to reuse the committed artifact for speed).
            ce2_path = ROOT / "artifacts" / "ce2_rational_local_solutions.json"
            if not ce2_path.exists() and (not skip_assemble):
                asm = _load_module(
                    ROOT / "tools" / "assemble_exact_l4_from_local_ce2.py", "asmce2"
                )
                asm.main()
            linfty.attach_l4_from_symbolic_constants(symp, load_ce2_artifact=True)
        else:
            linfty.attach_l4_from_symbolic_constants(symp, load_ce2_artifact=False)
            linfty.enable_ce2_global_predictor()

            # Quick sanity-check: the canonical mixed triple cancels.
            xa = basis_elem_g1(toe, (0, 0))
            ya = basis_elem_g1(toe, (17, 1))
            za = basis_elem_g2(toe, (3, 0))
            mag = float(flat_mag(linfty.homotopy_jacobi(xa, ya, za)))
            if mag > TOL_FAIL:
                raise AssertionError(
                    f"global CE2 predictor did not cancel mixed triple (mag={mag})"
                )
    else:
        if ce2_mode == "artifact":
            raise RuntimeError("missing artifacts/l4_symbolic_constants.json")
        linfty.enable_ce2_global_predictor()

    # now run exhaustive checks using linfty.homotopy_jacobi
    g1_idx = make_g1_basis(toe)
    g2_idx = make_g2_basis(toe)

    out = {"candidate_coeffs": coeffs, "ce2_mode": ce2_mode, "sectors": {}}

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

    triples = list(itertools.combinations(g1_idx, 3))
    if nworkers <= 1:
        for a_idx, b_idx, c_idx in triples:
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
    else:

        def _mag_j_for_triple(triple):
            a_idx, b_idx, c_idx = triple
            x = basis_elem_g1(toe, a_idx)
            y = basis_elem_g1(toe, b_idx)
            z = basis_elem_g1(toe, c_idx)
            return flat_mag(toe._jacobi(linfty.br_l2, x, y, z))

        with ThreadPoolExecutor(max_workers=nworkers) as ex:
            for triple, mag_j in zip(triples, ex.map(_mag_j_for_triple, triples)):
                a_idx, b_idx, c_idx = triple
                tested += 1
                max_j = max(max_j, mag_j)
                if mag_j < TOL_J:
                    continue
                x = basis_elem_g1(toe, a_idx)
                y = basis_elem_g1(toe, b_idx)
                z = basis_elem_g1(toe, c_idx)
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
    triples = list(itertools.combinations(g2_idx, 3))
    if nworkers <= 1:
        for a_idx, b_idx, c_idx in triples:
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
    else:

        def _mag_j_for_triple_g2(triple):
            a_idx, b_idx, c_idx = triple
            x = basis_elem_g2(toe, a_idx)
            y = basis_elem_g2(toe, b_idx)
            z = basis_elem_g2(toe, c_idx)
            return flat_mag(toe._jacobi(linfty.br_l2, x, y, z))

        with ThreadPoolExecutor(max_workers=nworkers) as ex:
            for triple, mag_j in zip(triples, ex.map(_mag_j_for_triple_g2, triples)):
                a_idx, b_idx, c_idx = triple
                tested += 1
                max_j = max(max_j, mag_j)
                if mag_j < TOL_J:
                    continue
                x = basis_elem_g2(toe, a_idx)
                y = basis_elem_g2(toe, b_idx)
                z = basis_elem_g2(toe, c_idx)
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
    triples = [
        (a_idx, b_idx, c_idx)
        for a_idx, b_idx in itertools.combinations(g1_idx, 2)
        for c_idx in g2_idx
    ]
    if nworkers <= 1:
        for a_idx, b_idx, c_idx in triples:
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
    else:

        def _mag_j_for_triple_g1g1g2(triple):
            a_idx, b_idx, c_idx = triple
            x = basis_elem_g1(toe, a_idx)
            y = basis_elem_g1(toe, b_idx)
            z = basis_elem_g2(toe, c_idx)
            return flat_mag(toe._jacobi(linfty.br_l2, x, y, z))

        with ThreadPoolExecutor(max_workers=nworkers) as ex:
            for triple, mag_j in zip(
                triples, ex.map(_mag_j_for_triple_g1g1g2, triples)
            ):
                a_idx, b_idx, c_idx = triple
                tested += 1
                max_j = max(max_j, mag_j)
                if mag_j < TOL_J:
                    continue
                x = basis_elem_g1(toe, a_idx)
                y = basis_elem_g1(toe, b_idx)
                z = basis_elem_g2(toe, c_idx)
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
    triples = [
        (a_idx, b_idx, c_idx)
        for a_idx in g1_idx
        for b_idx, c_idx in itertools.combinations(g2_idx, 2)
    ]
    if nworkers <= 1:
        for a_idx, b_idx, c_idx in triples:
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
    else:

        def _mag_j_for_triple_g1g2g2(triple):
            a_idx, b_idx, c_idx = triple
            x = basis_elem_g1(toe, a_idx)
            y = basis_elem_g2(toe, b_idx)
            z = basis_elem_g2(toe, c_idx)
            return flat_mag(toe._jacobi(linfty.br_l2, x, y, z))

        with ThreadPoolExecutor(max_workers=nworkers) as ex:
            for triple, mag_j in zip(
                triples, ex.map(_mag_j_for_triple_g1g2g2, triples)
            ):
                a_idx, b_idx, c_idx = triple
                tested += 1
                max_j = max(max_j, mag_j)
                if mag_j < TOL_J:
                    continue
                x = basis_elem_g1(toe, a_idx)
                y = basis_elem_g2(toe, b_idx)
                z = basis_elem_g2(toe, c_idx)
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
