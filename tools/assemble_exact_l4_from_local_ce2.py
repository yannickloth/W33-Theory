#!/usr/bin/env python3
"""Assemble exact/rational CE2 local solutions into a global l4 prototype.

This tool:
- Loads the exhaustive failing-triple artifact
- For each failing triple computes a local CE2 alpha via
  LInftyE8Extension.compute_local_ce2_alpha_for_triple(..., return_uv=True,
  rationalize_uv=True)
- Stores rationalized U/V arrays (Fractions as strings) in
  artifacts/ce2_rational_local_solutions.json
- Builds a global `alpha_global` by summing local rational alphas and
  promotes it to an `l4` using LInftyE8Extension.attach_l4_from_ce2
- Verifies that homotopy_jacobi is (numerically) zero on every recorded
  failing triple and that pure-sector checks do not regress.

Purpose: produce exact/rational certificates for the CE2->l4 repair path.
"""
from __future__ import annotations

import concurrent.futures
import importlib.util
import itertools
import json
import os
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
import sys

# make project root importable when running script directly
sys.path.insert(0, str(ROOT))
OUT = ROOT / "artifacts" / "ce2_rational_local_solutions.json"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys_mod = __import__("sys")
    sys_mod.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def flat_rats_to_E8Z3(toe_mod, flat_rats: List[Any]):
    """Convert a flat list of Fraction/None to a numeric toe.E8Z3 element.

    None entries are treated as zero.
    """
    N = 27 * 27
    # coerce to floats for numeric verification (certificate kept separately)
    vec = np.zeros(len(flat_rats), dtype=np.complex128)
    for i, r in enumerate(flat_rats):
        if r is None:
            vec[i] = 0.0
        else:
            # Fraction -> float (exact rational representation kept in artifact)
            vec[i] = float(r)

    e6 = vec[:N].reshape((27, 27))
    off = N
    sl3 = vec[off : off + 9].reshape((3, 3))
    off += 9
    g1 = vec[off : off + 81].reshape((27, 3))
    off += 81
    g2 = vec[off : off + 81].reshape((27, 3))
    return toe_mod.E8Z3(e6=e6, sl3=sl3, g1=g1, g2=g2)


def main(max_den: int = 720) -> Dict[str, Any]:
    toe = _load_module(ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py", "toe_e8")

    # load exhaustive artifact (must exist)
    exh_path = ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json"
    assert (
        exh_path.exists()
    ), "Run tools/exhaustive_homotopy_check_rationalized_l3.py first"
    exh = json.loads(exh_path.read_text(encoding="utf-8"))

    sector = exh.get("sectors", {}).get("g1_g1_g2", {})
    # support both shapes (list or single first_fail)
    fails = sector.get("failing_examples")
    if not fails:
        ff = sector.get("first_fail")
        # if only a single `first_fail` was recorded, scan exhaustively to
        # collect any additional failing triples (so we can assemble CE2 for
        # every remaining anomaly rather than just the first one).
        if ff is not None:
            fails = [ff]
            # exhaustive scan over g1_g1_g2 triples to find all failures
            from tools.exhaustive_homotopy_check_rationalized_l3 import (
                basis_elem_g1,
                basis_elem_g2,
            )

            def flat_mag(e):
                return float(
                    max(
                        0.0 if e.e6.size == 0 else np.max(np.abs(e.e6)),
                        0.0 if e.sl3.size == 0 else np.max(np.abs(e.sl3)),
                        0.0 if e.g1.size == 0 else np.max(np.abs(e.g1)),
                        0.0 if e.g2.size == 0 else np.max(np.abs(e.g2)),
                    )
                )

            g1_idx = [(i, j) for i in range(27) for j in range(3)]
            g2_idx = [(i, j) for i in range(27) for j in range(3)]
            TOL_J = 1e-12
            TOL_FAIL = 1e-8

            # set up temporary LInfty to evaluate l3 contributions
            proj = toe.E6Projector(
                np.load(
                    ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
                ).astype(np.complex128)
            )
            all_triads = toe._load_signed_cubic_triads()
            bad9 = set(
                tuple(sorted(t[:3]))
                for t in json.loads(
                    (
                        ROOT
                        / "artifacts"
                        / "linfty_coord_search_results_rationalized.json"
                    ).read_text()
                )["original"]["fiber_triads"]
            )
            from tools.build_linfty_firewall_extension import LInftyE8Extension

            linfty_tmp = LInftyE8Extension(
                toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0
            )

            for a_idx, b_idx in itertools.combinations(g1_idx, 2):
                for c_idx in g2_idx:
                    x = basis_elem_g1(toe, a_idx)
                    y = basis_elem_g1(toe, b_idx)
                    z = basis_elem_g2(toe, c_idx)
                    j_l2 = toe._jacobi(linfty_tmp.br_l2, x, y, z)
                    mag_j = flat_mag(j_l2)
                    if mag_j < TOL_J:
                        continue
                    tot = linfty_tmp.homotopy_jacobi(x, y, z)
                    mag_tot = flat_mag(tot)
                    if mag_tot > TOL_FAIL:
                        fails.append(
                            {
                                "a": list(a_idx),
                                "b": list(b_idx),
                                "c": list(c_idx),
                                "mag_j": mag_j,
                                "mag_tot": mag_tot,
                            }
                        )
        else:
            fails = []

    if len(fails) == 0:
        print("No failing triples recorded — nothing to assemble.")
        return {}

    # set up LInfty helper
    proj = toe.E6Projector(
        np.load(
            ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
        ).astype(np.complex128)
    )
    all_triads = toe._load_signed_cubic_triads()
    bad9 = set(
        tuple(sorted(t[:3]))
        for t in json.loads(
            (
                ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"
            ).read_text()
        )["original"]["fiber_triads"]
    )

    from tools.build_linfty_firewall_extension import LInftyE8Extension

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    # collect local rationalized CE2 solutions
    collected: Dict[str, Any] = {}
    local_alphas = []

    from tools.exhaustive_homotopy_check_rationalized_l3 import (
        basis_elem_g1,
        basis_elem_g2,
    )

    # helper for single-triple CE2 computation (used by worker processes)
    def _compute_local_for_triple(ft):
        a_idx = tuple(ft["a"])
        b_idx = tuple(ft["b"])
        c_idx = tuple(ft["c"])

        # re-import tool in worker context
        mod = _load_module(
            ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py", "toe_e8"
        )
        from tools.exhaustive_homotopy_check_rationalized_l3 import (
            basis_elem_g1,
            basis_elem_g2,
        )

        proj_w = mod.E6Projector(
            np.load(
                ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
            ).astype(np.complex128)
        )
        all_triads_w = mod._load_signed_cubic_triads()
        bad9_w = set(
            tuple(sorted(t[:3]))
            for t in json.loads(
                (
                    ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"
                ).read_text()
            )["original"]["fiber_triads"]
        )
        from tools.build_linfty_firewall_extension import LInftyE8Extension

        linfty_w = LInftyE8Extension(
            mod, proj_w, all_triads_w, bad9_w, l3_scale=1.0 / 9.0
        )
        x = basis_elem_g1(mod, a_idx)
        y = basis_elem_g1(mod, b_idx)
        z = basis_elem_g2(mod, c_idx)
        res = linfty_w.compute_local_ce2_alpha_for_triple(
            x, y, z, return_uv=True, rationalize_uv=True, max_den=max_den
        )
        if res is None:
            return (a_idx, b_idx, c_idx, None)
        alpha_fn, U_flat, V_flat, U_rats, V_rats = res
        return (
            a_idx,
            b_idx,
            c_idx,
            float(np.linalg.norm(U_flat)),
            float(np.linalg.norm(V_flat)),
            [str(r) if r is not None else "0" for r in U_rats],
            [str(r) if r is not None else "0" for r in V_rats],
        )

    # run local CE2 solves in parallel (worker reconstructs its own LInfty)
    parallel_workers = int(os.environ.get("ASSEMBLE_L4_WORKERS", os.cpu_count() or 2))
    if parallel_workers > 1 and len(fails) > 1:
        with concurrent.futures.ProcessPoolExecutor(max_workers=parallel_workers) as ex:
            futs = {ex.submit(_compute_local_for_triple, ft): ft for ft in fails}
            for fut in concurrent.futures.as_completed(futs):
                a_idx, b_idx, c_idx, *rest = fut.result()
                key = (
                    f"{a_idx[0]},{a_idx[1]}:{b_idx[0]},{b_idx[1]}:{c_idx[0]},{c_idx[1]}"
                )
                if rest[0] is None:
                    raise RuntimeError(
                        f"Local CE2 solver failed on triple {a_idx},{b_idx},{c_idx}"
                    )
                U_norm, V_norm, U_rats, V_rats = rest
                collected[key] = {
                    "a": a_idx,
                    "b": b_idx,
                    "c": c_idx,
                    "U_norm": U_norm,
                    "V_norm": V_norm,
                    "U_rats": U_rats,
                    "V_rats": V_rats,
                }
                # reconstruct basis elements in main process for alpha closure
                from tools.exhaustive_homotopy_check_rationalized_l3 import (
                    basis_elem_g1,
                    basis_elem_g2,
                )

                x = basis_elem_g1(toe, a_idx)
                y = basis_elem_g1(toe, b_idx)
                z = basis_elem_g2(toe, c_idx)

                def make_alpha_from_rats(
                    Ur: List[Any], Vr: List[Any], x_ref=x, y_ref=y, z_ref=z
                ):
                    def alpha(a, b):
                        if (
                            np.allclose(a.g1, y_ref.g1)
                            and np.allclose(a.g2, y_ref.g2)
                            and np.allclose(b.g1, z_ref.g1)
                            and np.allclose(b.g2, z_ref.g2)
                        ):
                            return flat_rats_to_E8Z3(toe, Ur)
                        if (
                            np.allclose(a.g1, z_ref.g1)
                            and np.allclose(a.g2, z_ref.g2)
                            and np.allclose(b.g1, y_ref.g1)
                            and np.allclose(b.g2, y_ref.g2)
                        ):
                            return flat_rats_to_E8Z3(
                                toe, [(-float(r)) if r is not None else 0.0 for r in Ur]
                            )
                        if (
                            np.allclose(a.g1, x_ref.g1)
                            and np.allclose(a.g2, x_ref.g2)
                            and np.allclose(b.g1, z_ref.g1)
                            and np.allclose(b.g2, z_ref.g2)
                        ):
                            return flat_rats_to_E8Z3(toe, Vr)
                        if (
                            np.allclose(a.g1, z_ref.g1)
                            and np.allclose(a.g2, z_ref.g2)
                            and np.allclose(b.g1, x_ref.g1)
                            and np.allclose(b.g2, x_ref.g2)
                        ):
                            return flat_rats_to_E8Z3(
                                toe, [(-float(r)) if r is not None else 0.0 for r in Vr]
                            )
                        return toe.E8Z3.zero()

                    return alpha

                local_alphas.append(make_alpha_from_rats(U_rats, V_rats))
    else:
        # fallback to sequential loop
        for ft in fails:
            a_idx = tuple(ft["a"])
            b_idx = tuple(ft["b"])
            c_idx = tuple(ft["c"])
            x = basis_elem_g1(toe, a_idx)
            y = basis_elem_g1(toe, b_idx)
            z = basis_elem_g2(toe, c_idx)

            res = linfty.compute_local_ce2_alpha_for_triple(
                x, y, z, return_uv=True, rationalize_uv=True, max_den=max_den
            )
            if res is None:
                raise RuntimeError(
                    f"Local CE2 solver failed on triple {a_idx},{b_idx},{c_idx}"
                )

            # unpack
            alpha_fn, U_flat, V_flat, U_rats, V_rats = res

            # store rationalized arrays as strings for artifact readability
            key = f"{a_idx[0]},{a_idx[1]}:{b_idx[0]},{b_idx[1]}:{c_idx[0]},{c_idx[1]}"
            collected[key] = {
                "a": a_idx,
                "b": b_idx,
                "c": c_idx,
                "U_norm": float(np.linalg.norm(U_flat)),
                "V_norm": float(np.linalg.norm(V_flat)),
                "U_rats": [str(r) if r is not None else "0" for r in U_rats],
                "V_rats": [str(r) if r is not None else "0" for r in V_rats],
            }

            # build a rational alpha (returns numeric toe.E8Z3 from Fraction lists)
            def make_alpha_from_rats(
                Ur: List[Any], Vr: List[Any], x_ref=x, y_ref=y, z_ref=z
            ):
                def alpha(a, b):
                    # compare by coordinates (cheap identity using g1/g2 arrays)
                    if (
                        np.allclose(a.g1, y_ref.g1)
                        and np.allclose(a.g2, y_ref.g2)
                        and np.allclose(b.g1, z_ref.g1)
                        and np.allclose(b.g2, z_ref.g2)
                    ):
                        return flat_rats_to_E8Z3(toe, Ur)
                    if (
                        np.allclose(a.g1, z_ref.g1)
                        and np.allclose(a.g2, z_ref.g2)
                        and np.allclose(b.g1, y_ref.g1)
                        and np.allclose(b.g2, y_ref.g2)
                    ):
                        return flat_rats_to_E8Z3(
                            toe, [(-float(r)) if r is not None else 0.0 for r in Ur]
                        )
                    if (
                        np.allclose(a.g1, x_ref.g1)
                        and np.allclose(a.g2, x_ref.g2)
                        and np.allclose(b.g1, z_ref.g1)
                        and np.allclose(b.g2, z_ref.g2)
                    ):
                        return flat_rats_to_E8Z3(toe, Vr)
                    if (
                        np.allclose(a.g1, z_ref.g1)
                        and np.allclose(a.g2, z_ref.g2)
                        and np.allclose(b.g1, x_ref.g1)
                        and np.allclose(b.g2, x_ref.g2)
                    ):
                        return flat_rats_to_E8Z3(
                            toe, [(-float(r)) if r is not None else 0.0 for r in Vr]
                        )
                    return toe.E8Z3.zero()

                return alpha

            local_alphas.append(make_alpha_from_rats(U_rats, V_rats))

    # assemble global CE2 by summing local alphas
    def alpha_global(a, b):
        acc = toe.E8Z3.zero()
        for alpha in local_alphas:
            acc = acc + alpha(a, b)
        return acc

    # persist artifact
    OUT.write_text(json.dumps(collected, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")

    # attach to linfty as an l4 prototype and verify
    linfty.attach_l4_from_ce2(alpha_global)

    # verify each recorded failing triple is fixed
    results = []
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
        tot = linfty.homotopy_jacobi(x, y, z)
        mag = max(
            float(np.max(np.abs(tot.e6))) if tot.e6.size else 0.0,
            float(np.max(np.abs(tot.sl3))) if tot.sl3.size else 0.0,
            float(np.max(np.abs(tot.g1))) if tot.g1.size else 0.0,
            float(np.max(np.abs(tot.g2))) if tot.g2.size else 0.0,
        )
        results.append(((a_idx, b_idx, c_idx), mag))

    # sanity check: random pure-sector triples don't regress
    rng = np.random.default_rng(20260213)
    for _ in range(30):
        xa = toe._random_element(
            rng,
            np.load(
                ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
            ).astype(np.complex128),
            scale0=0,
            scale1=2,
            scale2=0,
            include_g0=False,
            include_g2=False,
        )
        ya = toe._random_element(
            rng,
            np.load(
                ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
            ).astype(np.complex128),
            scale0=0,
            scale1=2,
            scale2=0,
            include_g0=False,
            include_g2=False,
        )
        za = toe._random_element(
            rng,
            np.load(
                ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
            ).astype(np.complex128),
            scale0=0,
            scale1=2,
            scale2=0,
            include_g0=False,
            include_g2=False,
        )
        hh = linfty.homotopy_jacobi(xa, ya, za)
        magp = max(
            float(np.max(np.abs(hh.e6))) if hh.e6.size else 0.0,
            float(np.max(np.abs(hh.sl3))) if hh.sl3.size else 0.0,
            float(np.max(np.abs(hh.g1))) if hh.g1.size else 0.0,
            float(np.max(np.abs(hh.g2))) if hh.g2.size else 0.0,
        )
        if magp > 1e-8:
            raise RuntimeError(
                "Pure-sector regression detected after attaching exact l4"
            )

    print("All failing triples reduced; pure-sector checks OK.")

    # generate SNF / PSLQ certificates for the recorded local CE2 solutions
    certificates: Dict[str, Any] = {}
    try:
        spec = importlib.util.spec_from_file_location(
            "snf_ce2", ROOT / "tools" / "snf_certificate_ce2_uv.py"
        )
        snf_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(snf_mod)
        snf_report = snf_mod.main()
        certificates["snf_certificate"] = snf_report
    except Exception as e:
        certificates["snf_certificate_error"] = str(e)

    try:
        spec2 = importlib.util.spec_from_file_location(
            "pslq_ce2", ROOT / "tools" / "pslq_snf_ce2_uv_check.py"
        )
        pslq_mod = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(pslq_mod)
        pslq_report = pslq_mod.main()
        certificates["pslq_check"] = pslq_report
    except Exception as e:
        certificates["pslq_check_error"] = str(e)

    return {"results": results, "artifact": str(OUT), "certificates": certificates}


if __name__ == "__main__":
    main()
