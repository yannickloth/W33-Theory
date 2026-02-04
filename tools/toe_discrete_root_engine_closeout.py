#!/usr/bin/env python3
"""
One-shot closeout for the *purely discrete* E8 root-channel engine.

This is the bridge step between:
  - W33 finite geometry + Z6 clock + line fusion laws, and
  - the full E8 Chevalley-Serre relations.

It runs (in order) and summarizes:
  1) W33 line phase structure (A2 hexagon per line)
  2) line-pair diff→output-line fusion determinism
  3) line-pair output-phase affine-dihedral law
  4) line-pair discrete inner-product model (orthogonal/adjacent/all-diffs)
  5) self-duality: line-orthogonality graph is SRG(40,12,2,4)
  6) full discrete engine: reproduces all E8 ips + all α·β=-1 sums
  7) cocycle sign patterns on the W33 fusion data
  8) Chevalley-Serre certificate for E8 from the W33-discrete cocycle bracket
  9) signed bracket from W33 tables (diff/output/phase/sign signatures)
  10) trinification tensor-product structure (E6×A2 on grades g1/g2)
  11) export full E8 structure constants (248-dim) from W33-discrete data
  12) verify Z3 grading (e6⊕a2, 27⊗3, 27̄⊗3̄) from the exported 248-dim table
  13) verify full Jacobi identity for the exported 248-dim table
  14) Sage cross-check of (4),(3) and (9)
  15) g1×g1→g2 coupling atlas vs cubic triads + firewall (45→36)
  16) g1×g2→g0 coupling semantics (e6 preserves i3; a2 preserves i27)
  17) Sage: Aut(W33) and point stabilizer (51840, 1296)

Outputs:
  - artifacts/toe_discrete_root_engine_closeout.json
  - artifacts/toe_discrete_root_engine_closeout.md
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    # Some stdlib utilities (e.g. dataclasses) expect the module to exist in sys.modules
    # during execution.
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _read_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _run_py(tool: str) -> None:
    _load_module(ROOT / "tools" / tool, tool.replace(".py", "")).main()


def _run_sage(sage_path: Path) -> None:
    subprocess.run(
        [str(ROOT / "run_sage.sh"), str(sage_path)], check=True, cwd=str(ROOT)
    )


def main() -> None:
    # 1)–8) Python checks.
    _run_py("analyze_w33_line_phase_structure.py")
    p1 = _read_json(ROOT / "artifacts" / "w33_line_phase_structure.json")

    _run_py("analyze_w33_line_pair_phase_fusion_patterns.py")
    p2 = _read_json(ROOT / "artifacts" / "w33_line_pair_phase_fusion_patterns.json")

    _run_py("analyze_w33_line_pair_output_phase_law.py")
    p3 = _read_json(ROOT / "artifacts" / "w33_line_pair_output_phase_law.json")

    _run_py("derive_w33_line_pair_ip_model.py")
    p4 = _read_json(ROOT / "artifacts" / "w33_line_pair_ip_model.json")

    _run_py("verify_w33_line_orthogonality_graph.py")
    p5 = _read_json(ROOT / "artifacts" / "w33_line_orthogonality_graph.json")

    _run_py("verify_discrete_e8_root_engine.py")
    # (this tool prints PASS, but we also treat its exit as the check)

    _run_py("analyze_e8_cocycle_signs_on_w33_fusion.py")
    p7 = _read_json(ROOT / "artifacts" / "e8_cocycle_signs_on_w33_fusion.json")

    _run_py("verify_e8_chevalley_from_w33_discrete.py")
    p8 = _read_json(ROOT / "artifacts" / "verify_e8_chevalley_from_w33_discrete.json")

    _run_py("verify_e8_discrete_bracket_from_w33_tables.py")
    p9 = _read_json(
        ROOT / "artifacts" / "verify_e8_discrete_bracket_from_w33_tables.json"
    )

    _run_py("verify_e8_trinification_tensor_product_structure.py")
    p10 = _read_json(
        ROOT / "artifacts" / "e8_trinification_tensor_product_structure.json"
    )

    _run_py("export_e8_structure_constants_from_w33_discrete.py")
    p11 = _read_json(ROOT / "artifacts" / "e8_structure_constants_w33_discrete.json")
    p11_sha256 = hashlib.sha256(
        (ROOT / "artifacts" / "e8_structure_constants_w33_discrete.json").read_bytes()
    ).hexdigest()

    _run_py("verify_e8_z3grading_from_structure_constants.py")
    p12 = _read_json(
        ROOT / "artifacts" / "verify_e8_z3grading_from_structure_constants.json"
    )

    _run_py("verify_e8_jacobi_from_structure_constants.py")
    p13 = _read_json(ROOT / "artifacts" / "verify_e8_jacobi_w33_discrete.json")

    # 14) Sage checks (optional but should work via docker fallback).
    _run_sage(Path("tools/sage_verify_discrete_e8_root_engine.sage"))
    sage_p1 = _read_json(
        ROOT / "artifacts" / "sage_verify_discrete_e8_root_engine.json"
    )

    _run_sage(Path("tools/sage_verify_e8_discrete_bracket_from_w33_tables.sage"))
    sage_p2 = _read_json(
        ROOT / "artifacts" / "sage_verify_e8_discrete_bracket_from_w33_tables.json"
    )

    _run_py("analyze_e8_g1g1_couplings_cubic_firewall.py")
    p15 = _read_json(ROOT / "artifacts" / "e8_g1g1_couplings_cubic_firewall.json")

    _run_py("analyze_e8_g1g2_to_g0_couplings.py")
    p16 = _read_json(ROOT / "artifacts" / "e8_g1g2_to_g0_couplings.json")

    _run_sage(Path("tools/sage_w33_point_stabilizer_structure.sage"))
    sage_p3 = _read_json(
        ROOT / "artifacts" / "sage_w33_point_stabilizer_structure.json"
    )

    status = "ok"
    if sage_p1.get("status") != "ok":
        status = "fail"
    if sage_p2.get("status") != "ok":
        status = "fail"
    if not p4.get("theorem", {}).get("discrete_ip_model_matches_all_line_pairs", False):
        status = "fail"
    if not p8.get("checks", {}).get("serre_ok", False):
        status = "fail"
    if p9.get("status") != "ok":
        status = "fail"
    if p10.get("status") != "ok":
        status = "fail"
    if p11.get("status") != "ok":
        status = "fail"
    if p12.get("status") != "ok":
        status = "fail"
    if p13.get("status") != "ok":
        status = "fail"
    if p15.get("status") != "ok":
        status = "fail"
    if p16.get("status") != "ok":
        status = "fail"
    if sage_p3.get("status") != "ok":
        status = "fail"

    out: Dict[str, object] = {
        "status": status,
        "w33_line_phase": {
            "status": p1.get("status"),
            "counts": p1.get("counts"),
        },
        "w33_line_pair_fusion": {
            "status": p2.get("status", "ok"),
            "diff_pattern_counts": p2.get("diff_pattern_counts"),
        },
        "w33_line_pair_output_phase_law": {
            "theorems": p3.get("theorems"),
            "a_counts": p3.get("histograms", {}).get("affine_a_counts"),
        },
        "w33_line_pair_ip_model": {
            "theorem": p4.get("theorem"),
            "counts": p4.get("counts"),
        },
        "w33_line_orthogonality_graph": {
            "srg": p5.get("srg"),
        },
        "e8_cocycle_signs_on_w33_fusion": {
            "counts": p7.get("counts"),
        },
        "e8_chevalley_from_w33_discrete": {
            "status": p8.get("status"),
            "checks": p8.get("checks"),
        },
        "verify_e8_discrete_bracket_from_w33_tables": p9,
        "e8_trinification_tensor_product_structure": p10,
        "e8_structure_constants_w33_discrete": {
            "status": p11.get("status"),
            "sha256": p11_sha256,
            "counts": p11.get("counts"),
        },
        "verify_e8_z3grading_from_structure_constants": p12,
        "verify_e8_jacobi_w33_discrete": p13,
        "sage_verify_discrete_e8_root_engine": sage_p1,
        "sage_verify_e8_discrete_bracket_from_w33_tables": sage_p2,
        "e8_g1g1_couplings_cubic_firewall": {
            "status": p15.get("status"),
            "counts": p15.get("counts"),
            "checks": p15.get("checks"),
        },
        "e8_g1g2_to_g0_couplings": {
            "status": p16.get("status"),
            "counts": p16.get("counts"),
            "checks": p16.get("checks"),
        },
        "sage_w33_point_stabilizer_structure": sage_p3,
        "artifacts": {
            "w33_line_phase_structure": "artifacts/w33_line_phase_structure.json",
            "w33_line_pair_phase_fusion_patterns": "artifacts/w33_line_pair_phase_fusion_patterns.json",
            "w33_line_pair_output_phase_law": "artifacts/w33_line_pair_output_phase_law.json",
            "w33_line_pair_ip_model": "artifacts/w33_line_pair_ip_model.json",
            "w33_line_orthogonality_graph": "artifacts/w33_line_orthogonality_graph.json",
            "e8_cocycle_signs_on_w33_fusion": "artifacts/e8_cocycle_signs_on_w33_fusion.json",
            "verify_e8_chevalley_from_w33_discrete": "artifacts/verify_e8_chevalley_from_w33_discrete.json",
            "verify_e8_discrete_bracket_from_w33_tables": "artifacts/verify_e8_discrete_bracket_from_w33_tables.json",
            "e8_trinification_tensor_product_structure": "artifacts/e8_trinification_tensor_product_structure.json",
            "e8_structure_constants_w33_discrete": "artifacts/e8_structure_constants_w33_discrete.json",
            "verify_e8_z3grading_from_structure_constants": "artifacts/verify_e8_z3grading_from_structure_constants.json",
            "verify_e8_jacobi_w33_discrete": "artifacts/verify_e8_jacobi_w33_discrete.json",
            "sage_verify_discrete_e8_root_engine": "artifacts/sage_verify_discrete_e8_root_engine.json",
            "sage_verify_e8_discrete_bracket_from_w33_tables": "artifacts/sage_verify_e8_discrete_bracket_from_w33_tables.json",
            "e8_g1g1_couplings_cubic_firewall": "artifacts/e8_g1g1_couplings_cubic_firewall.json",
            "e8_g1g2_to_g0_couplings": "artifacts/e8_g1g2_to_g0_couplings.json",
            "sage_w33_point_stabilizer_structure": "artifacts/sage_w33_point_stabilizer_structure.json",
        },
    }

    out_json = ROOT / "artifacts" / "toe_discrete_root_engine_closeout.json"
    out_md = ROOT / "artifacts" / "toe_discrete_root_engine_closeout.md"
    _write_json(out_json, out)

    md: List[str] = []
    md.append("# TOE discrete root-engine closeout\n")
    md.append(f"- status: `{status}`\n")
    md.append("## Highlights")
    md.append("- W33 lines carry A2 hexagons (Z6 phases {0..5} per line).")
    md.append(
        "- Coupled line-pairs: diff→output-line is deterministic; output phase is affine-dihedral."
    )
    md.append(
        "- Line-pair inner products admit a 3-type discrete model (orthogonal/adjacent/all-diffs)."
    )
    md.append(
        "- The orthogonality graph on lines is SRG(40,12,2,4) again (W33 self-duality)."
    )
    md.append(
        "- Chevalley-Serre relations for E8 verify using only the W33-discrete cocycle bracket."
    )
    md.append(
        "- The full signed bracket matches using only W33 fusion/phase/signature tables."
    )
    md.append(
        "- Trinification structure holds: su3 changes i3 only; e6 changes i27 only (27⊗3)."
    )
    md.append(
        "- A full 248-dim sparse structure-constants table is exported from the discrete data."
    )
    md.append("- The exported bracket respects the Z3 grading (e6⊕a2, 27⊗3, 27̄⊗3̄).")
    md.append(
        "- Jacobi identity holds for the exported 248-dim table (checked on all C(248,3) triples)."
    )
    md.append(
        "- g1×g1→g2 couplings realize the 45 E6 cubic triads (firewall forbids 9, leaving 36)."
    )
    md.append("- g1×g2→g0 couplings split cleanly: e6 preserves i3; a2 preserves i27.")
    md.append(
        "- Sage: Aut(W33) has order 51840 and point stabilizer has order 1296 (matches effective-triad symmetry)."
    )
    md.append("")
    md.append(f"- JSON: `{out_json}`")
    _write_md(out_md, md)

    print(f"status={status}")
    print(f"wrote={out_json}")
    print(f"wrote={out_md}")
    if status != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
