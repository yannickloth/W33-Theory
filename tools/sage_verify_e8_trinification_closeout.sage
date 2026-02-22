#!/usr/bin/env sage
"""
Sage cross-check for the Python-built trinification closeout artifacts.

This is intentionally small and "external": it does NOT re-run the Python
construction. It only validates the *outputs* using Sage's independent
Cartan/RootSystem/WeylGroup machinery.

Run (Docker fallback supported):
  SAGE_DOCKER_IMAGE=sagemath/sagemath:latest ./run_sage.sh tools/sage_verify_e8_trinification_closeout.sage

Outputs:
  - artifacts/sage_verify_e8_trinification_closeout.json
  - artifacts/sage_verify_e8_trinification_closeout.md
"""

from __future__ import annotations

import json
from pathlib import Path
from itertools import permutations

from sage.all import CartanType, WeylGroup, ZZ, matrix  # type: ignore


ROOT = Path(".").resolve()
IN_JSON = ROOT / "artifacts" / "verify_e8_dynkin_from_trinification.json"
OUT_JSON = ROOT / "artifacts" / "sage_verify_e8_trinification_closeout.json"
OUT_MD = ROOT / "artifacts" / "sage_verify_e8_trinification_closeout.md"


def main() -> None:
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))

    C_raw = matrix(ZZ, data["cartan_matrix_raw"])
    C_e8 = CartanType(["E", 8]).cartan_matrix()
    # Find a permutation that matches Sage's canonical E8 matrix.
    perm_to_sage: list[int] | None = None
    for p in permutations(range(8)):
        Cp = C_raw.matrix_from_rows_and_columns(list(p), list(p))
        if Cp == C_e8:
            perm_to_sage = list(p)
            break

    ok_matches = perm_to_sage is not None
    C_perm = C_raw.matrix_from_rows_and_columns(perm_to_sage, perm_to_sage) if ok_matches else C_raw

    # Basic invariants
    det_raw = int(C_raw.det())
    det_perm = int(C_perm.det())
    det_e8 = int(C_e8.det())

    # Weyl group order (exact, Sage)
    we8_order = int(WeylGroup(CartanType(["E", 8])).order())

    # Sanity checks expected for E8
    ok = bool(ok_matches and det_e8 == 1 and det_perm == 1 and we8_order == 696729600)

    out = {
        "status": "ok" if ok else "fail",
        "input": str(IN_JSON.as_posix()),
        "checks": {
            "perm_matches_canonical_e8": ok_matches,
            "det_cartan_raw": det_raw,
            "det_cartan_perm": det_perm,
            "det_cartan_canonical": det_e8,
            "weyl_group_order_e8": we8_order,
        },
        "perm_to_sage_canonical": perm_to_sage,
        "perm_to_python_canonical": list(data.get("perm_to_canonical", [])),
    }

    OUT_JSON.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    md = []
    md.append("# Sage verify: E8 trinification closeout\n")
    md.append(f"- status: `{out['status']}`")
    md.append(f"- input: `{out['input']}`")
    md.append(f"- perm matches canonical E8: `{ok_matches}`")
    md.append(f"- det(Cartan): raw `{det_raw}`, perm `{det_perm}`, canonical `{det_e8}`")
    md.append(f"- |W(E8)| (Sage): `{we8_order}`\n")
    md.append("## Cartan matrix (canonical order)\n")
    md.append("```")
    for row in C_perm.rows():
        md.append(" ".join(f"{int(x):2d}" for x in row))
    md.append("```")
    md.append(f"- JSON: `{OUT_JSON.as_posix()}`")
    OUT_MD.write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    print(json.dumps(out, indent=2, sort_keys=True))
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
