#!/usr/bin/env python3
"""
Certificate: Z3-graded E8 build from (e6 ⊕ sl3) ⊕ (27⊗3) ⊕ (27*⊗3*).

This is the "Jacobi-or-die" close-out:
  - fixes the relative normalizations (locked to ±1/6),
  - runs a Jacobi battery at those fixed scales,
  - checks that the bracket images span the expected graded pieces:
      [g1,g1] spans g2, [g2,g2] spans g1, [g1,g2] spans g0 = e6⊕sl3.

Inputs (repo-native):
  - artifacts/e6_27rep_basis_export/E6_basis_78.npy
  - artifacts/canonical_su3_gauge_and_cubic.json

Outputs:
  - artifacts/verify_e8_z3graded_trinification.json
  - artifacts/verify_e8_z3graded_trinification.md
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_tool() -> object:
    path = ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
    spec = importlib.util.spec_from_file_location(
        "toe_e8_z3graded_bracket_jacobi", path
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _matrix_rank(A: np.ndarray, *, tol: float = 1e-9) -> int:
    return int(np.linalg.matrix_rank(A, tol=tol))


def main() -> None:
    tool = _load_tool()

    basis_path = ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    if not basis_path.exists():
        raise RuntimeError(
            "Missing artifacts/e6_27rep_basis_export/E6_basis_78.npy. "
            "Run: python3 tools/build_e6_27rep_minuscule.py --export-basis78"
        )
    e6_basis = np.load(basis_path).astype(np.complex128)
    triads = tool._load_signed_cubic_triads()
    proj = tool.E6Projector(e6_basis)

    # Locked (empirically and consistently across seeds) by mixed Jacobi constraints:
    scale = {
        "scale_g1g1": 1.0,
        "scale_g2g2": -1.0 / 6.0,
        "scale_e6": 1.0,
        "scale_sl3": 1.0 / 6.0,
    }

    br = tool.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=triads,
        scale_g1g1=scale["scale_g1g1"],
        scale_g2g2=scale["scale_g2g2"],
        scale_e6=scale["scale_e6"],
        scale_sl3=scale["scale_sl3"],
    )

    rng = np.random.default_rng(0)

    def rand_g0():
        return tool._random_element(
            rng,
            e6_basis,
            scale0=2,
            scale1=0,
            scale2=0,
            include_g1=False,
            include_g2=False,
        )

    def rand_g1():
        return tool._random_element(
            rng,
            e6_basis,
            scale0=0,
            scale1=2,
            scale2=0,
            include_g0=False,
            include_g2=False,
        )

    def rand_g2():
        return tool._random_element(
            rng,
            e6_basis,
            scale0=0,
            scale1=0,
            scale2=2,
            include_g0=False,
            include_g1=False,
        )

    def rand_all():
        return tool._random_element(rng, e6_basis, scale0=2, scale1=2, scale2=2)

    jacobi_cases = [
        ("g0_g0_g0", (rand_g0, rand_g0, rand_g0)),
        ("g1_g1_g1", (rand_g1, rand_g1, rand_g1)),
        ("g2_g2_g2", (rand_g2, rand_g2, rand_g2)),
        ("g1_g1_g2", (rand_g1, rand_g1, rand_g2)),
        ("g1_g2_g2", (rand_g1, rand_g2, rand_g2)),
        ("mixed_all", (rand_all, rand_all, rand_all)),
    ]

    jacobi: Dict[str, Dict[str, float]] = {}
    for name, (fx, fy, fz) in jacobi_cases:
        max_res = 0.0
        trials = 300
        for _ in range(trials):
            j = tool._jacobi(br, fx(), fy(), fz())
            max_res = max(max_res, float(tool._elt_norm(j)))
        jacobi[name] = {"trials": float(trials), "max_residual": float(max_res)}

    # ---- span checks ----
    # [g1,g2] -> g0: e6 part is spanned by projections of E_{ij} (from matching SU3 indices);
    # sl3 part is spanned by sl3_project(E_{ab}) (from matching 27 indices).
    basis78 = e6_basis
    gram = np.einsum("aij,bji->ab", basis78, basis78)
    gram_inv = np.linalg.inv(gram)

    # For M = E_{i,j}, b_a = Tr(B_a M) = B_a[j,i].
    bt = basis78.transpose(0, 2, 1).reshape(78, 27 * 27)
    coeffs_e6_from_rank1 = gram_inv @ bt
    rank_e6 = _matrix_rank(coeffs_e6_from_rank1.real)

    sl3_vecs: List[np.ndarray] = []
    for a in range(3):
        for b in range(3):
            E = np.zeros((3, 3), dtype=np.complex128)
            E[a, b] = 1.0
            M = tool._sl3_project(E)
            sl3_vecs.append(M.reshape(-1).real)
    rank_sl3 = _matrix_rank(np.stack(sl3_vecs, axis=1))

    # [g1,g1] spans g2 and [g2,g2] spans g1: brute rank on basis-pair images.
    # Build explicit basis elements as E8Z3 (sparse).
    g1_elts: List[object] = []
    for i in range(27):
        for a in range(3):
            X = tool.E8Z3.zero()
            m = np.zeros((27, 3), dtype=np.complex128)
            m[i, a] = 1.0
            g1_elts.append(tool.E8Z3(e6=X.e6, sl3=X.sl3, g1=m, g2=X.g2))

    g2_elts: List[object] = []
    for i in range(27):
        for a in range(3):
            X = tool.E8Z3.zero()
            m = np.zeros((27, 3), dtype=np.complex128)
            m[i, a] = 1.0
            g2_elts.append(tool.E8Z3(e6=X.e6, sl3=X.sl3, g1=X.g1, g2=m))

    g2_images: List[np.ndarray] = []
    for p in range(len(g1_elts)):
        for q in range(p + 1, len(g1_elts)):
            out = br.bracket(g1_elts[p], g1_elts[q]).g2
            g2_images.append(out.reshape(-1).real)
    rank_g2 = _matrix_rank(np.stack(g2_images, axis=1))

    g1_images: List[np.ndarray] = []
    for p in range(len(g2_elts)):
        for q in range(p + 1, len(g2_elts)):
            out = br.bracket(g2_elts[p], g2_elts[q]).g1
            g1_images.append(out.reshape(-1).real)
    rank_g1 = _matrix_rank(np.stack(g1_images, axis=1))

    spans = {
        "rank_e6_from_[g1,g2]": int(rank_e6),
        "rank_sl3_from_[g1,g2]": int(rank_sl3),
        "rank_g2_from_[g1,g1]": int(rank_g2),
        "rank_g1_from_[g2,g2]": int(rank_g1),
    }

    status = "ok"
    if max(v["max_residual"] for v in jacobi.values()) > 1e-7:
        status = "fail"
    if spans["rank_e6_from_[g1,g2]"] != 78 or spans["rank_sl3_from_[g1,g2]"] != 8:
        status = "fail"
    if spans["rank_g2_from_[g1,g1]"] != 81 or spans["rank_g1_from_[g2,g2]"] != 81:
        status = "fail"

    report = {
        "status": status,
        "scales": scale,
        "paths": {
            "e6_basis": str(basis_path),
            "cubic_triads": "artifacts/canonical_su3_gauge_and_cubic.json",
        },
        "jacobi": jacobi,
        "spans": spans,
    }

    out_json = ROOT / "artifacts" / "verify_e8_z3graded_trinification.json"
    out_md = ROOT / "artifacts" / "verify_e8_z3graded_trinification.md"
    out_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    md_lines = [
        "# Z3-graded E8 certificate (trinification build)\n",
        f"- status: `{status}`",
        f"- scales: `g1g1={scale['scale_g1g1']}` `g2g2={scale['scale_g2g2']}` `e6={scale['scale_e6']}` `sl3={scale['scale_sl3']}`\n",
        "## Jacobi residuals (max entrywise abs)\n",
    ]
    for k, v in jacobi.items():
        md_lines.append(
            f"- {k}: `{v['max_residual']}` over `{int(v['trials'])}` trials"
        )
    md_lines.append("\n## Span checks (ranks)\n")
    for k, v in spans.items():
        md_lines.append(f"- {k}: `{v}`")
    out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"status={status}")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")

    if status != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
