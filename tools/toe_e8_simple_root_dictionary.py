#!/usr/bin/env python3
"""
Produce a compact “E8 simple-root protocol dictionary”:

  - the 8 E8 simple roots (in trinification Cartan coordinates)
  - their Z3-grade (g0_e6 vs g1 vs g2)
  - their W33 edge (u,v)
  - the induced W33 line (4-point block) containing that edge
  - Coxeter orbit id (0..39) and Z6 phase (0..5)

Inputs:
  - artifacts/verify_e8_chevalley_from_z3graded.json
  - artifacts/e8_root_metadata_table.json

Outputs:
  - artifacts/toe_e8_simple_root_dictionary.json
  - artifacts/toe_e8_simple_root_dictionary.md
"""

from __future__ import annotations

import json
from itertools import product
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _build_w33_adj() -> np.ndarray:
    # W33 from PG(3,3) points with symplectic form omega; edge iff omega==0.
    F3 = [0, 1, 2]
    points = []
    seen = set()
    for vec in product(F3, repeat=4):
        if not any(vec):
            continue
        v = list(vec)
        for i in range(4):
            if v[i] != 0:
                inv = 1 if v[i] == 1 else 2
                v = [(x * inv) % 3 for x in v]
                break
        t = tuple(v)
        if t not in seen:
            seen.add(t)
            points.append(t)

    def omega(x, y) -> int:
        return (x[0] * y[2] - x[2] * y[0] + x[1] * y[3] - x[3] * y[1]) % 3

    n = len(points)
    if n != 40:
        raise RuntimeError(f"Expected 40 points; got {n}")
    adj = np.zeros((n, n), dtype=bool)
    for i in range(n):
        for j in range(i + 1, n):
            if omega(points[i], points[j]) == 0:
                adj[i, j] = adj[j, i] = True
    return adj


def _edge_line(adj: np.ndarray, u: int, v: int) -> Tuple[int, int, int, int]:
    # In SRG(40,12,2,4), each edge has exactly two common neighbors.
    common = [k for k in range(adj.shape[0]) if adj[u, k] and adj[v, k]]
    if len(common) != 2:
        raise RuntimeError(f"Edge ({u},{v}) has {len(common)} common neighbors")
    return tuple(sorted([u, v, common[0], common[1]]))


def main() -> None:
    cert = json.loads(
        (ROOT / "artifacts" / "verify_e8_chevalley_from_z3graded.json").read_text(
            encoding="utf-8"
        )
    )
    simples = cert["simple_roots"]["alpha8"]  # list of 8 roots (8 ints)
    where = cert["simple_roots"]["where"]

    meta = json.loads(
        (ROOT / "artifacts" / "e8_root_metadata_table.json").read_text(encoding="utf-8")
    )
    row_by_root: Dict[Tuple[int, ...], Dict[str, object]] = {}
    for row in meta["rows"]:
        rt = tuple(int(x) for x in row["root_trin"])
        row_by_root[rt] = row

    adj = _build_w33_adj()

    out_rows: List[Dict[str, object]] = []
    for i, a in enumerate(simples):
        rt = tuple(int(x) for x in a)
        rmeta = row_by_root.get(rt)
        if rmeta is None:
            raise RuntimeError(f"Missing root in metadata table: {rt}")
        u, v = (int(x) for x in rmeta["edge"])
        line = _edge_line(adj, u, v)

        out_rows.append(
            {
                "i": int(i),
                "alpha8_trin": list(rt),
                "grade": rmeta["grade"],
                "edge": [u, v],
                "line": list(line),
                "coxeter_orbit_id": int(rmeta["orbit_id"]),
                "phase_z6": int(rmeta["phase_z6"]),
                "i27": rmeta.get("i27"),
                "i3": rmeta.get("i3"),
                "cert_where": where[i],
            }
        )

    out = {"status": "ok", "rows": out_rows}

    out_json = ROOT / "artifacts" / "toe_e8_simple_root_dictionary.json"
    out_md = ROOT / "artifacts" / "toe_e8_simple_root_dictionary.md"
    _write_json(out_json, out)

    md: List[str] = []
    md.append("# TOE E8 simple-root dictionary\n")
    md.append(f"- status: `ok`")
    md.append(f"- count: `{len(out_rows)}`\n")
    md.append("## Roots\n")
    for row in out_rows:
        md.append(
            f"- i={row['i']} grade={row['grade']} edge={row['edge']} line={row['line']} "
            f"orbit={row['coxeter_orbit_id']} phase={row['phase_z6']} alpha={row['alpha8_trin']}"
        )
    md.append(f"\n- JSON: `{out_json}`")
    _write_md(out_md, md)

    print(f"ok simples={len(out_rows)}")


if __name__ == "__main__":
    main()
