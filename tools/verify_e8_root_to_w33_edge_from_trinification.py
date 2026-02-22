#!/usr/bin/env python3
"""
Bridge certificate:

  (E6⊕A2 + 27⊗3 weights)  -->  240 E8 roots (in coroot-eigenvalue coordinates)
  --> express each root in the recovered E8 simple-root basis
  --> convert to *canonical* E8 simple-root coordinates
  --> map to a W33 edge via the repo's canonical edge<->root bijection.

This produces a machine-checkable dictionary that closes the loop:
  "the 240 E8 root channels ARE the 240 W33 edges"
in a single coordinate system, without handwaving.

Inputs:
  - tools/verify_e8_root_system_from_trinification.py (constructs roots in Z^8)
  - artifacts/verify_e8_dynkin_from_trinification.json (simple roots + perm_to_canonical)
  - artifacts/sage_verify_e8_trinification_closeout.json (perm_to_sage_canonical)
  - artifacts/e8_root_to_edge.json (canonical E8 root coords -> W33 edge (u,v))

Outputs:
  - artifacts/verify_e8_root_to_w33_edge_from_trinification.json
  - artifacts/verify_e8_root_to_w33_edge_from_trinification.md
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _parse_root_key(k: str) -> Tuple[int, ...]:
    s = k.strip()
    if not (s.startswith("(") and s.endswith(")")):
        raise ValueError(f"Bad root key: {k}")
    body = s[1:-1].strip()
    if not body:
        return tuple()
    parts = [p.strip() for p in body.split(",")]
    return tuple(int(p) for p in parts)


def main() -> None:
    root_mod = _load_module(
        "verify_e8_root_system_from_trinification",
        ROOT / "tools" / "verify_e8_root_system_from_trinification.py",
    )

    # Build the 240 roots in the repo's "trinification Cartan basis" coords.
    e6_roots = root_mod.generate_roots_from_cartan(root_mod.E6_CARTAN)
    w27 = root_mod.load_e6_27_weights_from_chevalley()
    w3 = root_mod.a2_weights_fund3()
    a2_roots = root_mod.a2_roots_from_weights(w3)

    roots8: List[Tuple[int, ...]] = []
    seen = set()
    for r in e6_roots:
        t = tuple(list(r) + [0, 0])
        if t not in seen:
            roots8.append(t)
            seen.add(t)
    for r in a2_roots:
        t = tuple([0] * 6 + list(r))
        if t not in seen:
            roots8.append(t)
            seen.add(t)
    for mu in w27:
        for nu in w3:
            t1 = tuple(list(mu.tolist()) + list(nu.tolist()))
            t2 = tuple(list((-mu).tolist()) + list((-nu).tolist()))
            if t1 not in seen:
                roots8.append(t1)
                seen.add(t1)
            if t2 not in seen:
                roots8.append(t2)
                seen.add(t2)
    roots8 = [r for r in roots8 if r != tuple([0] * 8)]
    roots8 = sorted(roots8)
    if len(roots8) != 240:
        raise RuntimeError(f"Expected 240 roots; got {len(roots8)}")

    dyn = json.loads(
        (ROOT / "artifacts" / "verify_e8_dynkin_from_trinification.json").read_text(
            encoding="utf-8"
        )
    )
    simples = np.array(dyn["simples"], dtype=int)  # (8,8) rows
    M = simples.T.astype(float)  # columns are simple roots in this coordinate basis

    # The canonical ordering used by `artifacts/e8_root_to_edge.json` comes from the
    # E8 Coxeter-orbit construction (Sage pipeline) and matches Sage's CartanType('E8')
    # convention, not necessarily the Python verifier's internal node order.
    sage_close = json.loads(
        (ROOT / "artifacts" / "sage_verify_e8_trinification_closeout.json").read_text(
            encoding="utf-8"
        )
    )
    perm_to_sage = list(sage_close["perm_to_sage_canonical"])

    # Load canonical E8 root coords -> W33 edge map.
    raw_map = json.loads(
        (ROOT / "artifacts" / "e8_root_to_edge.json").read_text(encoding="utf-8")
    )
    canon_to_edge: Dict[Tuple[int, ...], Tuple[int, int]] = {}
    for k, v in raw_map.items():
        rt = _parse_root_key(k)
        canon_to_edge[rt] = (int(v[0]), int(v[1]))

    def to_canonical_simple_coeffs(r: Sequence[int]) -> Tuple[int, ...]:
        rr = np.array(r, dtype=float).reshape(8)
        coeff = np.linalg.solve(M, rr)
        ci = np.rint(coeff).astype(int)
        if not np.allclose(coeff, ci, atol=1e-8):
            raise RuntimeError(f"Non-integer coeffs for root {r}: {coeff.tolist()}")
        if not np.array_equal(
            (M @ ci.astype(float)).astype(int), np.array(r, dtype=int)
        ):
            raise RuntimeError("Coeff solve failed exact reconstruction")
        # Reorder to match the root-coordinate convention used in e8_root_to_edge.json.
        return tuple(int(ci[p]) for p in perm_to_sage)

    root_to_edge: Dict[str, List[int]] = {}
    edge_to_root: Dict[str, List[int]] = {}
    missing = 0
    for r in roots8:
        canon = to_canonical_simple_coeffs(r)
        edge = canon_to_edge.get(canon)
        if edge is None:
            missing += 1
            continue
        root_key = "(" + ", ".join(str(x) for x in r) + ")"
        edge_key = f"({edge[0]}, {edge[1]})"
        root_to_edge[root_key] = [edge[0], edge[1]]
        edge_to_root[edge_key] = list(r)

    unique_edges = {tuple(v) for v in root_to_edge.values()}

    status = "ok"
    if missing != 0:
        status = "fail"
    if len(root_to_edge) != 240:
        status = "fail"
    if len(unique_edges) != 240:
        status = "fail"

    out = {
        "status": status,
        "counts": {
            "roots": 240,
            "mapped": int(len(root_to_edge)),
            "missing": int(missing),
            "unique_edges": int(len(unique_edges)),
        },
        "sources": {
            "e8_dynkin_simple_system": "artifacts/verify_e8_dynkin_from_trinification.json",
            "e8_perm_to_sage": "artifacts/sage_verify_e8_trinification_closeout.json",
            "e8_root_to_edge_canonical": "artifacts/e8_root_to_edge.json",
        },
        "perm_to_sage": perm_to_sage,
        "root_to_edge": root_to_edge,
        "edge_to_root": edge_to_root,
    }

    out_json = ROOT / "artifacts" / "verify_e8_root_to_w33_edge_from_trinification.json"
    out_md = ROOT / "artifacts" / "verify_e8_root_to_w33_edge_from_trinification.md"
    _write_json(out_json, out)

    md: List[str] = []
    md.append("# Verify E8 root ↔ W33 edge bridge (trinification)\n")
    md.append(f"- status: `{status}`")
    md.append(f"- roots: `{out['counts']['roots']}`")
    md.append(f"- mapped: `{out['counts']['mapped']}`")
    md.append(f"- unique_edges: `{out['counts']['unique_edges']}`")
    md.append(f"- missing: `{out['counts']['missing']}`")
    md.append(f"- perm_to_sage: `{perm_to_sage}`\n")
    md.append("## Summary\n")
    md.append(
        "This script expresses each of the 240 trinification-derived roots in the recovered E8 simple basis,"
    )
    md.append(
        "converts to canonical E8 simple-root coordinates, and then applies the repo's canonical `e8_root_to_edge` map."
    )
    md.append("\n- JSON: `" + str(out_json) + "`")
    _write_md(out_md, md)

    print(
        f"status={status} mapped={len(root_to_edge)} unique_edges={len(unique_edges)}"
    )
    if status != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
