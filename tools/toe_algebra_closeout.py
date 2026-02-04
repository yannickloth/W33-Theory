#!/usr/bin/env python3
"""
One-shot closeout for the algebraic spine of the TOE.

Runs and summarizes:
  1) Z3-graded E8 bracket Jacobi + span certificate
  2) E8 root system (240 roots, rank 8, simply-laced) from trinification weights
  3) Dynkin recovery (Cartan matrix matches canonical E8)
  4) Chevalley-Serre certificate for E8 inside the Z3-graded bracket
  5) Root↔edge bridge: trinification roots -> canonical E8 roots -> W33 edges

Outputs:
  - artifacts/toe_algebra_closeout.json
  - artifacts/toe_algebra_closeout.md
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _read_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    # 1) Jacobi + spans for the Z3-graded bracket build.
    _load_module(
        ROOT / "tools" / "verify_e8_z3graded_trinification.py",
        "verify_e8_z3graded_trinification",
    ).main()
    j = _read_json(ROOT / "artifacts" / "verify_e8_z3graded_trinification.json")

    # 2) Root system count / rank / equal lengths.
    _load_module(
        ROOT / "tools" / "verify_e8_root_system_from_trinification.py",
        "verify_e8_root_system_from_trinification",
    ).main()
    r = _read_json(ROOT / "artifacts" / "verify_e8_root_system_from_trinification.json")

    # 3) Dynkin recovery.
    _load_module(
        ROOT / "tools" / "verify_e8_dynkin_from_trinification.py",
        "verify_e8_dynkin_from_trinification",
    ).main()
    d = _read_json(ROOT / "artifacts" / "verify_e8_dynkin_from_trinification.json")

    # 4) Chevalley-Serre certificate for the constructed E8.
    _load_module(
        ROOT / "tools" / "verify_e8_chevalley_from_z3graded.py",
        "verify_e8_chevalley_from_z3graded",
    ).main()
    c = _read_json(ROOT / "artifacts" / "verify_e8_chevalley_from_z3graded.json")

    # 5) Root<->edge bridge in W33.
    _load_module(
        ROOT / "tools" / "verify_e8_root_to_w33_edge_from_trinification.py",
        "verify_e8_root_to_w33_edge_from_trinification",
    ).main()
    b = _read_json(
        ROOT / "artifacts" / "verify_e8_root_to_w33_edge_from_trinification.json"
    )

    status = "ok"
    for obj in (j, r, d, c, b):
        if obj.get("status") != "ok":
            status = "fail"

    out: Dict[str, object] = {
        "status": status,
        "e8_z3graded": {
            "status": j.get("status"),
            "scales": j.get("scales"),
            "spans": j.get("spans"),
            "jacobi": j.get("jacobi"),
        },
        "e8_root_system": {
            "status": r.get("status"),
            "counts": r.get("counts"),
            "form": r.get("form"),
        },
        "e8_dynkin": {
            "status": d.get("status"),
            "counts": d.get("counts"),
            "cartan_matrix_matches_canonical": d.get("cartan_matrix_matches_canonical"),
            "perm_to_canonical": d.get("perm_to_canonical"),
        },
        "e8_chevalley": {
            "status": c.get("status"),
            "cartan": c.get("cartan"),
            "serre": c.get("serre"),
        },
        "e8_root_to_w33_edge": {
            "status": b.get("status"),
            "counts": b.get("counts"),
        },
        "artifacts": {
            "verify_e8_z3graded_trinification": "artifacts/verify_e8_z3graded_trinification.json",
            "verify_e8_root_system_from_trinification": "artifacts/verify_e8_root_system_from_trinification.json",
            "verify_e8_dynkin_from_trinification": "artifacts/verify_e8_dynkin_from_trinification.json",
            "verify_e8_chevalley_from_z3graded": "artifacts/verify_e8_chevalley_from_z3graded.json",
            "verify_e8_root_to_w33_edge_from_trinification": "artifacts/verify_e8_root_to_w33_edge_from_trinification.json",
        },
    }

    out_json = ROOT / "artifacts" / "toe_algebra_closeout.json"
    out_md = ROOT / "artifacts" / "toe_algebra_closeout.md"
    _write_json(out_json, out)

    md: List[str] = []
    md.append("# TOE algebra closeout\n")
    md.append(f"- status: `{status}`\n")

    md.append("## Z3-graded E8 bracket")
    md.append(f"- status: `{j.get('status')}`")
    md.append(f"- scales: `{j.get('scales')}`")
    md.append(f"- spans: `{j.get('spans')}`\n")

    md.append("## E8 root system")
    md.append(f"- status: `{r.get('status')}`")
    md.append(f"- counts: `{r.get('counts')}`")
    md.append(f"- form: `{r.get('form')}`\n")

    md.append("## E8 Dynkin")
    md.append(f"- status: `{d.get('status')}`")
    md.append(f"- matches canonical: `{d.get('cartan_matrix_matches_canonical')}`")
    md.append(f"- perm_to_canonical: `{d.get('perm_to_canonical')}`\n")

    md.append("## E8 Chevalley-Serre")
    md.append(f"- status: `{c.get('status')}`")
    md.append(f"- cartan: `{c.get('cartan')}`")
    md.append(f"- serre: `{c.get('serre')}`\n")

    md.append("## E8 ↔ W33 bridge")
    md.append(f"- status: `{b.get('status')}`")
    md.append(f"- counts: `{b.get('counts')}`\n")

    md.append(f"- JSON: `{out_json}`")
    _write_md(out_md, md)

    print(f"status={status}")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    if status != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
