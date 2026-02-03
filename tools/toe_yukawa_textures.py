#!/usr/bin/env python3
"""
Extract SM-component "texture" information from the 45 cubic triads of the E6 27.

Inputs:
  - artifacts/toe_sm_decomposition_27.json

Outputs:
  - artifacts/toe_yukawa_textures.json
  - artifacts/toe_yukawa_textures.md

What this computes (purely combinatorial, no physics claims beyond the data):
  - For each gauge-invariant triad type (e.g. H_u Q u^c), list all component-level
    couplings present in the E6 cubic triads, and mark which are firewall-forbidden.
  - Component labels are derived from the recovered SM quantum numbers:
      * color label from the SU(3) weight (E6 w1,w2)
      * SU(2) component from w5 (= ±1 -> T3 = ±1/2)
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


ColorW = Tuple[int, int]

# Canonical A2 weight labels (chosen for readability, not a claim about physics).
COLOR_LABEL: Dict[ColorW, str] = {
    (0, 1): "c0",
    (1, -1): "c1",
    (-1, 0): "c2",
}


def _color_label(w12: ColorW, *, rep: str) -> str:
    """
    For su3 rep:
      - if rep == '3'   : use COLOR_LABEL(w12)
      - if rep == '3bar': use COLOR_LABEL(-w12) so 3bar matches the corresponding 3 color
    """
    if rep == "3":
        key = w12
    elif rep == "3bar":
        key = (-w12[0], -w12[1])
    else:
        raise ValueError(f"Unexpected SU3 rep: {rep}")
    if key not in COLOR_LABEL:
        raise ValueError(f"Unexpected SU3 weight for color label: {w12} rep={rep}")
    return COLOR_LABEL[key]


def _su2_comp(w5: int) -> str:
    if w5 == 1:
        return "up"
    if w5 == -1:
        return "dn"
    raise ValueError("Expected SU2 doublet component w5=±1")


@dataclass(frozen=True)
class Vtx:
    i: int
    field: str
    su3: str
    su2: str
    y6: int
    q6: int
    w: Tuple[int, int, int, int, int, int]

    @property
    def w12(self) -> ColorW:
        return (self.w[1], self.w[2])

    @property
    def w5(self) -> int:
        return self.w[5]

    def color(self) -> str | None:
        if self.su3 == "1":
            return None
        return _color_label(self.w12, rep=self.su3)

    def comp(self) -> str | None:
        if self.su2 == "1":
            return None
        return _su2_comp(self.w5)


def main(argv: Sequence[str] | None = None) -> None:
    sm_path = ROOT / "artifacts" / "toe_sm_decomposition_27.json"
    out_json = ROOT / "artifacts" / "toe_yukawa_textures.json"
    out_md = ROOT / "artifacts" / "toe_yukawa_textures.md"

    sm = _load_json(sm_path)
    if not isinstance(sm, dict):
        raise RuntimeError("Invalid toe_sm_decomposition_27.json")
    per_v = sm.get("per_vertex")
    triads = (
        sm.get("triads", {}).get("records")
        if isinstance(sm.get("triads"), dict)
        else None
    )
    if not (isinstance(per_v, list) and isinstance(triads, list)):
        raise RuntimeError(
            "toe_sm_decomposition_27.json missing per_vertex or triads.records"
        )

    vtx: Dict[int, Vtx] = {}
    for row in per_v:
        if not isinstance(row, dict):
            continue
        i = int(row["i"])
        vtx[i] = Vtx(
            i=i,
            field=str(row["field"]),
            su3=str(row["su3"]),
            su2=str(row["su2"]),
            y6=int(row["Y6"]),
            q6=int(row["Q6"]),
            w=tuple(int(x) for x in row["w"]),
        )
    if len(vtx) != 27:
        raise RuntimeError("Expected 27 vertices in per_vertex")

    # Helper: canonical triad signature.
    def triad_sig(verts: List[int]) -> Tuple[int, int, int]:
        a, b, c = sorted(int(x) for x in verts)
        return (a, b, c)

    # Collect by field-type triple.
    by_type: Dict[Tuple[str, str, str], List[dict]] = defaultdict(list)
    for rec in triads:
        if not isinstance(rec, dict):
            continue
        verts = rec.get("verts")
        fields = rec.get("fields")
        if not (
            isinstance(verts, list)
            and len(verts) == 3
            and isinstance(fields, list)
            and len(fields) == 3
        ):
            continue
        key = tuple(sorted(str(x) for x in fields))
        by_type[key].append(rec)

    # Texture extraction for selected SM-relevant types.
    # For each type, we record component labels for each vertex and group counts by a compact key.
    def texture_key(
        fields: Tuple[str, str, str], tri: Tuple[int, int, int]
    ) -> Tuple[Tuple[str, str], ...]:
        rows = []
        for i in tri:
            vv = vtx[i]
            label = vv.field
            parts = []
            if vv.color() is not None:
                parts.append(vv.color())
            if vv.comp() is not None:
                parts.append(vv.comp())
            if parts:
                label = f"{label}[{','.join(parts)}]"
            rows.append((vv.field, label))
        # Sort by *base* field name for stable grouping, but preserve enriched labels.
        return tuple(sorted(rows, key=lambda x: x[0]))

    texture_out = []
    for ftype in sorted(by_type):
        recs = by_type[ftype]
        # Only include common physics-facing ones for now.
        include = ftype in {
            ("H_u", "Q", "u^c"),
            ("H_d", "Q", "d^c"),
            ("H_d", "L", "e^c"),
            ("H_u", "L", "nu^c"),
            ("D", "Q", "Q"),
            ("Dbar", "L", "Q"),
            ("Dbar", "d^c", "u^c"),
            ("D", "Dbar", "S"),
            ("H_d", "H_u", "S"),
        }
        if not include:
            continue

        sig_counts = Counter()
        sig_forbidden = Counter()
        examples: Dict[Tuple[Tuple[str, str], ...], List[Tuple[int, int, int]]] = (
            defaultdict(list)
        )
        for rec in recs:
            tri = triad_sig(rec["verts"])
            sig = texture_key(ftype, tri)
            sig_counts[sig] += 1
            if rec.get("forbidden"):
                sig_forbidden[sig] += 1
            if len(examples[sig]) < 3:
                examples[sig].append(tri)

        texture_out.append(
            {
                "type": list(ftype),
                "total": len(recs),
                "forbidden": int(sum(1 for r in recs if r.get("forbidden"))),
                "components": [
                    {
                        "signature": [lbl for _, lbl in sig],
                        "count": int(sig_counts[sig]),
                        "forbidden": int(sig_forbidden.get(sig, 0)),
                        "examples": [list(t) for t in examples[sig]],
                    }
                    for sig in sorted(
                        sig_counts, key=lambda s: (tuple(x[1] for x in s))
                    )
                ],
            }
        )

    out: Dict[str, object] = {
        "status": "ok",
        "source": {"toe_sm_decomposition_27": str(sm_path)},
        "textures": texture_out,
    }
    _write_json(out_json, out)

    lines: List[str] = []
    lines.append("# TOE: Component-Level Coupling Textures (from cubic triads)")
    lines.append("")
    lines.append(f"- Source: `{sm_path}`")
    lines.append("")
    for block in texture_out:
        lines.append(f"## {block['type']}")
        lines.append(f"- total: `{block['total']}` forbidden: `{block['forbidden']}`")
        lines.append("")
        for comp in block["components"]:
            lines.append(
                f"- {comp['signature']}: count `{comp['count']}` forbidden `{comp['forbidden']}` examples `{comp['examples']}`"
            )
        lines.append("")
    lines.append(f"- JSON: `{out_json}`")
    _write_md(out_md, lines)

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
