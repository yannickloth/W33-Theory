#!/usr/bin/env python3
"""
TOE: Affine-line rewrite rules (forbidden points -> allowed lifts).

Given:
  - 9 forbidden block triads (points)
  - 12 affine lines (3 points each)
  - 3 lifted allowed triads per line (Z3 lifts)

We summarize each line as a rule:
  multiset(point_field_types)  -->  multiset(lift_field_types)

and classify whether the line is "type-trivial" (same multiset) or not.

Inputs:
  - artifacts/toe_line_lift_field_compiler.json

Outputs:
  - artifacts/toe_affine_line_rewrite_rules.json
  - artifacts/toe_affine_line_rewrite_rules.md
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Iterable, Tuple

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _ms_key(types: Iterable[Iterable[str]]) -> Tuple[Tuple[str, ...], ...]:
    return tuple(sorted(tuple(t) for t in types))


def main() -> None:
    inp = ROOT / "artifacts" / "toe_line_lift_field_compiler.json"
    data = _load_json(inp)
    if data.get("status") != "ok":
        raise RuntimeError("toe_line_lift_field_compiler.json status != ok")

    rules = []
    trivial = 0
    for line in data["lines"]:
        blocks = list(line["blocks"])
        points = [tuple(p["forbidden_triad"]["fields"]) for p in line["points"]]
        lifts = [tuple(l["triad_fields"]) for l in line["lifts"]]
        ms_points = _ms_key(points)
        ms_lifts = _ms_key(lifts)
        is_trivial = ms_points == ms_lifts
        trivial += int(is_trivial)
        rules.append(
            {
                "blocks": blocks,
                "equation": line["equation"],
                "lambda": int(line["lambda"]),
                "family": str(line["family"]),
                "points_multiset": [list(x) for x in ms_points],
                "lifts_multiset": [list(x) for x in ms_lifts],
                "type_trivial": bool(is_trivial),
            }
        )

    # Histogram by (points_multiset -> lifts_multiset).
    trans_hist = Counter(
        (
            tuple(map(tuple, r["points_multiset"])),
            tuple(map(tuple, r["lifts_multiset"])),
        )
        for r in rules
    )
    out = {
        "status": "ok",
        "sources": {"toe_line_lift_field_compiler": str(inp)},
        "counts": {
            "lines": len(rules),
            "type_trivial": trivial,
            "type_nontrivial": len(rules) - trivial,
            "distinct_transitions": len(trans_hist),
        },
        "rules": sorted(rules, key=lambda r: tuple(r["blocks"])),
        "transition_histogram": [
            {
                "points_multiset": [list(x) for x in k[0]],
                "lifts_multiset": [list(x) for x in k[1]],
                "count": int(v),
            }
            for k, v in trans_hist.most_common()
        ],
        "note": (
            "Each affine line gives 3 forbidden point-triads and 3 allowed lifted triads. "
            "Some lines preserve the field-type multiset, others rewrite it."
        ),
    }

    out_json = ROOT / "artifacts" / "toe_affine_line_rewrite_rules.json"
    out_md = ROOT / "artifacts" / "toe_affine_line_rewrite_rules.md"
    _write_json(out_json, out)

    md = []
    md.append("# TOE affine line rewrite rules")
    md.append("")
    md.append("## Counts")
    for k, v in out["counts"].items():
        md.append(f"- {k}: {v}")
    md.append("")
    md.append("## Transition histogram")
    for row in out["transition_histogram"]:
        md.append(
            f"- {row['count']}x  {row['points_multiset']}  ->  {row['lifts_multiset']}"
        )
    _write_md(out_md, "\n".join(md) + "\n")

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
