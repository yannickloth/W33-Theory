#!/usr/bin/env python3
"""
Analyze how the Z3-graded decomposition (g0_e6/g0_a2/g1/g2) distributes across
the 40 Coxeter-6 orbits (size-6 root packets) that underpin the W33 edge bijection.

Input:
  - artifacts/e8_root_metadata_table.json

Outputs:
  - artifacts/e8_orbit_grade_structure.json
  - artifacts/e8_orbit_grade_structure.md
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    meta = json.loads(
        (ROOT / "artifacts" / "e8_root_metadata_table.json").read_text(encoding="utf-8")
    )
    rows = meta["rows"]

    by_orbit: Dict[int, List[dict]] = defaultdict(list)
    for r in rows:
        by_orbit[int(r["orbit_id"])].append(r)

    orbit_summaries: List[Dict[str, object]] = []
    type_counter: Counter[Tuple[Tuple[str, int], ...]] = Counter()

    for oid in range(40):
        lst = by_orbit.get(oid, [])
        if len(lst) != 6:
            raise RuntimeError(f"Orbit {oid} expected 6 roots; got {len(lst)}")
        grades = Counter(str(x["grade"]) for x in lst)
        key = tuple(sorted(grades.items()))
        type_counter[key] += 1

        # reconstruct the underlying W33 line: union of the 6 edges is 4 vertices
        verts = sorted({int(v) for x in lst for v in x["edge"]})
        orbit_summaries.append(
            {
                "orbit_id": oid,
                "grade_counts": dict(grades),
                "line_vertices": verts,
                "roots": [x["root_trin"] for x in lst],
                "edges": [x["edge"] for x in lst],
            }
        )

    out = {
        "status": "ok",
        "orbit_type_counts": {str(k): int(v) for k, v in type_counter.items()},
        "orbits": orbit_summaries,
    }

    out_json = ROOT / "artifacts" / "e8_orbit_grade_structure.json"
    out_md = ROOT / "artifacts" / "e8_orbit_grade_structure.md"
    _write_json(out_json, out)

    md: List[str] = []
    md.append("# E8 orbit grade structure\n")
    md.append("- status: `ok`\n")
    md.append("## Orbit type counts\n")
    for k, v in sorted(type_counter.items(), key=lambda kv: (-kv[1], str(kv[0]))):
        md.append(f"- {dict(k)}: `{v}` orbits")
    md.append(f"\n- JSON: `{out_json}`")
    _write_md(out_md, md)

    print("ok orbits=40 types=", len(type_counter))


if __name__ == "__main__":
    main()
