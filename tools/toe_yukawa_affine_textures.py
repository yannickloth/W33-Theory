#!/usr/bin/env python3
"""
TOE: Yukawa textures (field-component level) annotated by affine-plane/Z3 geometry.

This connects three existing layers:
  1) E6 cubic triads inside the 27 (one generation) + firewall forbiddance,
  2) their quotient geometry AG(2,3) (9 forbidden blocks) + 12 affine lines with 3 Z3 lifts,
  3) the SM field/component labeling on the 27 vertices.

Inputs:
  - artifacts/toe_yukawa_textures.json
  - artifacts/toe_affine_plane_z3_connection.json

Outputs:
  - artifacts/toe_yukawa_affine_textures.json
  - artifacts/toe_yukawa_affine_textures.md
"""

from __future__ import annotations

import json
from collections import Counter
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
    textures_path = ROOT / "artifacts" / "toe_yukawa_textures.json"
    conn_path = ROOT / "artifacts" / "toe_affine_plane_z3_connection.json"
    sm_path = ROOT / "artifacts" / "toe_sm_decomposition_27.json"

    textures = _load_json(textures_path)
    conn = _load_json(conn_path)
    sm = _load_json(sm_path)

    if textures.get("status") != "ok":
        raise RuntimeError("toe_yukawa_textures.json status != ok")
    if conn.get("status") != "ok":
        raise RuntimeError("toe_affine_plane_z3_connection.json status != ok")
    if sm.get("status") != "ok":
        raise RuntimeError("toe_sm_decomposition_27.json status != ok")

    field_by_vertex = {int(v["i"]): str(v["field"]) for v in sm["per_vertex"]}

    # Forbidden blocks: each block is the kernel 3-cycle, and its vertices are the forbidden triad.
    triad_to_block: Dict[Tuple[int, ...], dict] = {}
    vertex_to_block: Dict[int, int] = {}
    for b in conn["blocks"]:
        bid = int(b["id"])
        vs = [int(vr["v"]) for vr in b["vertices"]]
        tri = _sorted_tuple(vs)
        triad_to_block[tri] = {"id": bid, "coord_f3_2": list(b["coord_f3_2"])}
        for v in vs:
            vertex_to_block[v] = bid

    # Allowed triads: indexed by sorted triad.
    triad_to_line: Dict[Tuple[int, ...], dict] = {}
    for line in conn["lines"]:
        info = {
            "blocks": list(line["blocks"]),
            "equation": dict(line["equation"]),
            "lambda": int(line["lambda"]),
            "ordered_blocks": list(line["ordered_blocks"]),
        }
        for tri in line["allowed_triads_cycle"]:
            t = _sorted_tuple(tri["vertices"])
            triad_to_line[t] = {
                **info,
                "t_shifted_param_order": list(tri["t_shifted_param_order"]),
            }

    def locate_triad(tri: Tuple[int, ...]) -> dict:
        if tri in triad_to_block:
            return {"kind": "forbidden_block", **triad_to_block[tri]}
        if tri in triad_to_line:
            return {"kind": "allowed_line", **triad_to_line[tri]}
        raise RuntimeError(f"Triad not found in connection (unexpected): {tri}")

    out_textures = []
    forbidden_field_hist = Counter()

    for tex in textures["textures"]:
        typ = list(tex["type"])
        comps = tex["components"]
        comp_rows = []
        for comp in comps:
            sig = list(comp["signature"])
            exs = comp["examples"]
            # Each signature can have multiple examples; we annotate all of them.
            examples = []
            for tri in exs:
                tri_t = _sorted_tuple(tri)
                loc = locate_triad(tri_t)
                examples.append(
                    {
                        "triad": list(tri_t),
                        "fields": sorted(field_by_vertex[v] for v in tri_t),
                        "location": loc,
                    }
                )
                if loc["kind"] == "forbidden_block":
                    forbidden_field_hist[
                        tuple(sorted(field_by_vertex[v] for v in tri_t))
                    ] += 1

            comp_rows.append(
                {
                    "signature": sig,
                    "count": int(comp["count"]),
                    "forbidden": int(comp["forbidden"]),
                    "examples": examples,
                }
            )

        out_textures.append(
            {
                "type": typ,
                "total_triads": int(tex["total"]),
                "forbidden_triads": int(tex["forbidden"]),
                "components": comp_rows,
            }
        )

    out = {
        "status": "ok",
        "sources": {
            "toe_yukawa_textures": str(textures_path),
            "toe_affine_plane_z3_connection": str(conn_path),
            "toe_sm_decomposition_27": str(sm_path),
        },
        "counts": {
            "texture_types": len(out_textures),
        },
        "textures": out_textures,
        "forbidden_field_histogram": {
            str(list(k)): int(v) for k, v in sorted(forbidden_field_hist.items())
        },
        "note": (
            "This annotates each component-level Yukawa triad with its affine-plane/Z3 location: "
            "either a forbidden block point or an allowed lifted affine line."
        ),
    }

    json_path = ROOT / "artifacts" / "toe_yukawa_affine_textures.json"
    md_path = ROOT / "artifacts" / "toe_yukawa_affine_textures.md"
    _write_json(json_path, out)

    md = []
    md.append("# TOE Yukawa affine textures")
    md.append("")
    md.append("## Forbidden triad-type histogram (from component examples)")
    for k, v in out["forbidden_field_histogram"].items():
        md.append(f"- {k}: {v}")
    md.append("")
    md.append("## Texture summaries")
    for tex in out["textures"]:
        md.append(
            f"- {tex['type']}: total={tex['total_triads']} forbidden={tex['forbidden_triads']}"
        )
    _write_md(md_path, "\n".join(md) + "\n")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
