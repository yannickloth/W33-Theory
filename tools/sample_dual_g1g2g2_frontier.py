#!/usr/bin/env python3
"""Sample the first unresolved g1,g2,g2 triples after the current CE2 lifts.

This is a research probe, not a verifier. It loads the current l3 + exact CE2
artifact + global predictors, then walks the g1,g2,g2 basis sector in the same
order as the exhaustive checker. For each unresolved triple it computes the
local CE2 repair and records the sparse U/V/W support in a compact JSON report.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "dual_g1g2g2_frontier_sample.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _mag(e) -> float:
    return float(
        max(
            np.max(np.abs(e.e6)) if e.e6.size else 0.0,
            np.max(np.abs(e.sl3)) if e.sl3.size else 0.0,
            np.max(np.abs(e.g1)) if e.g1.size else 0.0,
            np.max(np.abs(e.g2)) if e.g2.size else 0.0,
        )
    )


def _decode_sparse(rats):
    out = []
    for i, r in enumerate(rats):
        if r is None:
            continue
        if i < 729:
            out.append(["e6", int(i) // 27, int(i) % 27, str(r)])
        elif i < 738:
            j = int(i) - 729
            out.append(["sl3", j // 3, j % 3, str(r)])
        elif i < 819:
            j = int(i) - 738
            out.append(["g1", j // 3, j % 3, str(r)])
        else:
            j = int(i) - 819
            out.append(["g2", j // 3, j % 3, str(r)])
    return out


def main(limit: int = 8) -> dict[str, object]:
    toe = _load(ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py", "toe_e8")
    build = _load(ROOT / "tools" / "build_linfty_firewall_extension.py", "build_linfty")
    coc = _load(ROOT / "scripts" / "ce2_global_cocycle.py", "ce2_global_cocycle")
    exh = _load(ROOT / "tools" / "exhaustive_homotopy_check_l3_l4.py", "exh_l3_l4")

    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    rat = json.loads(
        (ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json").read_text()
    )
    bad9 = set(tuple(sorted(t)) for t in rat["original"]["fiber_triads"])
    linfty = build.LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)
    linfty.attach_l4_from_symbolic_constants(
        ROOT / "artifacts" / "l4_symbolic_constants.json", load_ce2_artifact=True
    )
    linfty.enable_ce2_global_predictor()

    heis, _ = coc._heisenberg_vec_maps()
    rows = []
    for a_idx in exh.make_g1_basis(toe):
        for b_idx, c_idx in itertools.combinations(exh.make_g2_basis(toe), 2):
            x = exh.basis_elem_g1(toe, a_idx)
            y = exh.basis_elem_g2(toe, b_idx)
            z = exh.basis_elem_g2(toe, c_idx)
            j_l2 = toe._jacobi(linfty.br_l2, x, y, z)
            if _mag(j_l2) < 1e-12:
                continue
            hj = linfty.homotopy_jacobi(x, y, z)
            if _mag(hj) <= 1e-8:
                continue
            rec: dict[str, object] = {
                "triple": [list(a_idx), list(b_idx), list(c_idx)],
                "a_heis": [int(v) for v in heis[a_idx[0]]],
                "b_heis": [int(v) for v in heis[b_idx[0]]],
                "c_heis": [int(v) for v in heis[c_idx[0]]],
                "baseline": _mag(hj),
            }
            res = linfty.compute_local_ce2_alpha_for_triple(
                x, y, z, return_uv=True, rationalize_uv=True, max_den=5040
            )
            if res is not None:
                alpha, _U_flat, _V_flat, U_rats, V_rats = res
                rec["mode"] = getattr(alpha, "_ce2_solution_mode", None)
                rec["U"] = _decode_sparse(U_rats)
                rec["V"] = _decode_sparse(V_rats)
                rec["W"] = _decode_sparse(getattr(alpha, "_ce2_W_rats"))
            rows.append(rec)
            if len(rows) >= int(limit):
                out = {"limit": int(limit), "rows": rows}
                OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
                print(f"Wrote {OUT}")
                return out

    out = {"limit": int(limit), "rows": rows}
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")
    return out


if __name__ == "__main__":
    main()
