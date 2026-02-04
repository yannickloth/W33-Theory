#!/usr/bin/env python3
"""
TOE: Compile affine-line lift details in SM field language.

This is the "selection-rule compiler" in the most literal sense:

  blocks (forbidden triads)  +  Z3 connection
        ->  12 affine lines, each with 3 lifted allowed triads

For each line we output:
  - its 3 blocks (points) with their forbidden field triples
  - its equation type + lambda
  - the 3 lifted allowed triads, written as per-block choices:
      (block_id, coord, t_shifted) -> (vertex, field)

Inputs:
  - artifacts/toe_affine_plane_z3_connection.json
  - artifacts/toe_sm_decomposition_27.json

Outputs:
  - artifacts/toe_line_lift_field_compiler.json
  - artifacts/toe_line_lift_field_compiler.md
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    conn_path = ROOT / "artifacts" / "toe_affine_plane_z3_connection.json"
    sm_path = ROOT / "artifacts" / "toe_sm_decomposition_27.json"
    conn = _load_json(conn_path)
    sm = _load_json(sm_path)

    if conn.get("status") != "ok":
        raise RuntimeError("toe_affine_plane_z3_connection.json status != ok")
    if sm.get("status") != "ok":
        raise RuntimeError("toe_sm_decomposition_27.json status != ok")

    field_by = {int(v["i"]): str(v["field"]) for v in sm["per_vertex"]}

    # Block structures
    block_coords = {}
    forbidden_triads_by_block = {}
    v_to_block = {}
    t_shifted_by_v = {}
    v_by_block_t: Dict[int, Dict[int, int]] = defaultdict(dict)

    for b in conn["blocks"]:
        bid = int(b["id"])
        coord = tuple(int(x) for x in b["coord_f3_2"])
        block_coords[bid] = coord
        vs = [int(vr["v"]) for vr in b["vertices"]]
        forbidden_triads_by_block[bid] = tuple(sorted(vs))
        for vr in b["vertices"]:
            v = int(vr["v"])
            v_to_block[v] = bid
            ts = int(vr["t_shifted"])
            t_shifted_by_v[v] = ts
            v_by_block_t[bid][ts] = v

    if len(block_coords) != 9:
        raise RuntimeError("Expected 9 blocks")
    if any(set(m.keys()) != {0, 1, 2} for m in v_by_block_t.values()):
        raise RuntimeError("Each block must contain all three t_shifted values")

    # Lines: per-line lift selection
    lines_out = []
    family_hist = Counter()
    for line in sorted(conn["lines"], key=lambda x: tuple(x["blocks"])):
        blocks = [int(x) for x in line["blocks"]]
        ordered_blocks = [int(x) for x in line["ordered_blocks"]]
        eq = dict(line["equation"])
        lam = int(line["lambda"])
        family = eq["type"] if eq["type"] != "y=mx+c" else f"m={eq['m']}"
        family_hist[family] += 1

        points = []
        for b in blocks:
            tri = forbidden_triads_by_block[b]
            points.append(
                {
                    "block": b,
                    "coord_f3_2": list(block_coords[b]),
                    "forbidden_triad": {
                        "vertices": list(tri),
                        "fields": sorted(field_by[v] for v in tri),
                    },
                }
            )

        lifts = []
        for tri in line["allowed_triads_cycle"]:
            verts = [int(x) for x in tri["vertices"]]
            if len(verts) != 3:
                raise RuntimeError("Expected triad of 3 vertices")
            # Map vertices to blocks
            by_block = {v_to_block[v]: v for v in verts}
            if set(by_block.keys()) != set(blocks):
                raise RuntimeError("Allowed triad blocks do not match line blocks")
            # Use ordered_blocks to align with t_shifted_param_order
            tvec = [int(x) for x in tri["t_shifted_param_order"]]
            if len(tvec) != 3:
                raise RuntimeError("Expected 3 t_shifted entries")
            per_block = []
            for b, t in zip(ordered_blocks, tvec):
                v = by_block[b]
                if t_shifted_by_v[v] != t:
                    raise RuntimeError(
                        "t_shifted mismatch between vertex record and triad param order"
                    )
                per_block.append(
                    {
                        "block": b,
                        "coord_f3_2": list(block_coords[b]),
                        "t_shifted": t,
                        "vertex": v,
                        "field": field_by[v],
                    }
                )
            lifts.append(
                {
                    "triad_vertices": sorted(verts),
                    "triad_fields": sorted(field_by[v] for v in verts),
                    "per_block_choices": per_block,
                }
            )

        lines_out.append(
            {
                "blocks": blocks,
                "equation": eq,
                "lambda": lam,
                "family": family,
                "ordered_blocks": ordered_blocks,
                "points": points,
                "lifts": lifts,
            }
        )

    out = {
        "status": "ok",
        "sources": {
            "toe_affine_plane_z3_connection": str(conn_path),
            "toe_sm_decomposition_27": str(sm_path),
        },
        "counts": {
            "blocks": 9,
            "lines": 12,
            "lifts_per_line": 3,
            "family_hist": dict(family_hist),
        },
        "lines": lines_out,
        "note": (
            "This is a field-level, per-block lift description of the 36 allowed triads, "
            "organized by the 12 affine lines on the 9 firewall blocks."
        ),
    }

    json_path = ROOT / "artifacts" / "toe_line_lift_field_compiler.json"
    md_path = ROOT / "artifacts" / "toe_line_lift_field_compiler.md"
    _write_json(json_path, out)

    md = []
    md.append("# TOE line lift field compiler")
    md.append("")
    md.append("## Counts")
    for k, v in out["counts"].items():
        md.append(f"- {k}: {v}")
    md.append("")
    md.append("## Family histogram")
    for k, v in sorted(family_hist.items()):
        md.append(f"- {k}: {v}")
    md.append("")
    md.append("## Example line")
    ex = out["lines"][0]
    md.append(
        f"- blocks={ex['blocks']} eq={ex['equation']} lambda={ex['lambda']} family={ex['family']}"
    )
    for lift in ex["lifts"]:
        md.append(
            f"  - {lift['triad_fields']} choices={[(c['block'], c['t_shifted'], c['field']) for c in lift['per_block_choices']]}"
        )
    _write_md(md_path, "\n".join(md) + "\n")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
