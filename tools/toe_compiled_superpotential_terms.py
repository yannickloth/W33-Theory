#!/usr/bin/env python3
"""
TOE: Compile "superpotential terms" from the AG(2,3)+Z3 connection.

This is the field-language upgrade of `toe_coupling_mask_compiler.py`.

Inputs:
  - artifacts/toe_affine_plane_z3_connection.json
  - artifacts/toe_compiled_coupling_mask.json
  - artifacts/toe_sm_decomposition_27.json

Outputs:
  - artifacts/toe_compiled_superpotential_terms.json
  - artifacts/toe_compiled_superpotential_terms.md

What it provides:
  - The 9 forbidden block-triads (firewall points) with SM-field labels + charges.
  - The 12 affine lines, each with its 3 allowed lifted triads, in SM-field language.
  - Aggregated type counts (allowed vs forbidden) matching the known 45 triads.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sorted_tuple(xs: Iterable[int]) -> Tuple[int, ...]:
    return tuple(sorted(int(x) for x in xs))


def main() -> None:
    conn_path = ROOT / "artifacts" / "toe_affine_plane_z3_connection.json"
    mask_path = ROOT / "artifacts" / "toe_compiled_coupling_mask.json"
    sm_path = ROOT / "artifacts" / "toe_sm_decomposition_27.json"

    conn = _load_json(conn_path)
    mask = _load_json(mask_path)
    sm = _load_json(sm_path)

    if conn.get("status") != "ok":
        raise RuntimeError("toe_affine_plane_z3_connection.json status != ok")
    if mask.get("status") != "ok":
        raise RuntimeError("toe_compiled_coupling_mask.json status != ok")
    if sm.get("status") != "ok":
        raise RuntimeError("toe_sm_decomposition_27.json status != ok")

    per_vertex = sm["per_vertex"]
    if not (isinstance(per_vertex, list) and len(per_vertex) == 27):
        raise RuntimeError(
            "toe_sm_decomposition_27.json: expected 27 per_vertex records"
        )

    # Minimal per-vertex SM record for downstream reporting.
    vrec: Dict[int, dict] = {int(r["i"]): dict(r) for r in per_vertex}
    field_by = {i: str(vrec[i]["field"]) for i in vrec}

    forbidden = [_sorted_tuple(t) for t in mask["forbidden_triads"]]
    allowed = [_sorted_tuple(t) for t in mask["allowed_triads"]]
    forbidden_set = set(forbidden)
    allowed_set = set(allowed)
    if len(forbidden_set) != 9 or len(allowed_set) != 36:
        raise RuntimeError("Unexpected triad counts in compiled coupling mask")
    if forbidden_set & allowed_set:
        raise RuntimeError("Forbidden/allowed overlap in compiled coupling mask")

    # Block records come from kernel cycles in the connection: each block is exactly one forbidden triad.
    blocks_out = []
    for b in sorted(conn["blocks"], key=lambda x: int(x["id"])):
        bid = int(b["id"])
        vs = [int(v["v"]) for v in b["vertices"]]
        tri = _sorted_tuple(vs)
        if tri not in forbidden_set:
            raise RuntimeError("Connection block triad not in compiled forbidden set")
        blocks_out.append(
            {
                "id": bid,
                "coord_f3_2": list(b["coord_f3_2"]),
                "offset_z3": int(b["offset_z3"]),
                "forbidden_triad": {
                    "vertices": list(tri),
                    "fields": sorted(field_by[v] for v in tri),
                    "vertex_records": [vrec[v] for v in tri],
                },
                "vertices": b["vertices"],
            }
        )

    # Lines: annotate each allowed triad with SM fields + charges.
    lines_out = []
    allowed_type_hist = Counter()
    for line in sorted(conn["lines"], key=lambda x: tuple(x["blocks"])):
        blocks = _sorted_tuple(line["blocks"])
        tri_entries = []
        for tri in line["allowed_triads_cycle"]:
            verts = _sorted_tuple(tri["vertices"])
            if verts not in allowed_set:
                raise RuntimeError("Connection line triad not in compiled allowed set")
            fields = sorted(field_by[v] for v in verts)
            allowed_type_hist[tuple(fields)] += 1
            tri_entries.append(
                {
                    "vertices": list(verts),
                    "fields": fields,
                    "vertex_records": [vrec[v] for v in verts],
                    "t_shifted_param_order": list(tri["t_shifted_param_order"]),
                }
            )

        lines_out.append(
            {
                "blocks": list(blocks),
                "equation": line["equation"],
                "lambda": int(line["lambda"]),
                "lift_orbit_type": list(line["lift_orbit_type"]),
                "ordered_blocks": list(line["ordered_blocks"]),
                "allowed_triads_cycle": tri_entries,
            }
        )

    # Aggregate allowed+forbidden triad types.
    type_counts = defaultdict(lambda: {"allowed": 0, "forbidden": 0})
    for tri in allowed_set:
        typ = tuple(sorted(field_by[v] for v in tri))
        type_counts[typ]["allowed"] += 1
    for tri in forbidden_set:
        typ = tuple(sorted(field_by[v] for v in tri))
        type_counts[typ]["forbidden"] += 1

    types_out = []
    for typ, counts in sorted(
        type_counts.items(), key=lambda kv: (-sum(kv[1].values()), kv[0])
    ):
        tot = counts["allowed"] + counts["forbidden"]
        types_out.append(
            {
                "fields": list(typ),
                "total": tot,
                "allowed": counts["allowed"],
                "forbidden": counts["forbidden"],
                "forbidden_frac": 0.0 if tot == 0 else counts["forbidden"] / tot,
            }
        )

    out = {
        "status": "ok",
        "sources": {
            "toe_affine_plane_z3_connection": str(conn_path),
            "toe_compiled_coupling_mask": str(mask_path),
            "toe_sm_decomposition_27": str(sm_path),
        },
        "counts": {
            "blocks": 9,
            "affine_lines": 12,
            "triads_total": 45,
            "triads_forbidden": 9,
            "triads_allowed": 36,
        },
        "blocks": blocks_out,
        "lines": lines_out,
        "triad_type_counts": types_out,
        "note": (
            "Forbidden triads are the 9 firewall blocks (points of AG(2,3)); allowed triads "
            "are the 36 lifted line-triads compiled from the Z3 connection."
        ),
    }

    json_path = ROOT / "artifacts" / "toe_compiled_superpotential_terms.json"
    md_path = ROOT / "artifacts" / "toe_compiled_superpotential_terms.md"
    _write_json(json_path, out)

    md = []
    md.append("# TOE compiled superpotential terms (AG(2,3)+Z3)")
    md.append("")
    md.append("## Counts")
    for k, v in out["counts"].items():
        md.append(f"- {k}: {v}")
    md.append("")
    md.append("## Forbidden block triads (firewall points)")
    for b in out["blocks"]:
        tri = b["forbidden_triad"]
        md.append(
            f"- block {b['id']} @ {b['coord_f3_2']}: {tri['fields']}  verts={tri['vertices']}"
        )
    md.append("")
    md.append("## Allowed triad type histogram")
    for typ, cnt in sorted(allowed_type_hist.items(), key=lambda kv: (-kv[1], kv[0])):
        md.append(f"- {list(typ)}: {cnt}")
    _write_md(md_path, "\n".join(md) + "\n")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
