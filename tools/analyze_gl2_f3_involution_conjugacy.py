#!/usr/bin/env python3
"""Enumerate the det=2 involution class in GL(2,3) with explicit conjugators.

This bridges group-theoretic and graph-theoretic structure:
- group: conjugacy class + centralizer counts,
- graph: induced cycle signatures on AG(2,3) points/lines.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any, Callable, Iterable, TypeVar

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze

T = TypeVar("T")


def _cycle_signature(items: Iterable[T], image: Callable[[T], T]) -> list[int]:
    items_list = list(items)
    unseen = set(items_list)
    sig: list[int] = []
    while unseen:
        start = min(unseen)
        cur = start
        count = 0
        while cur in unseen:
            unseen.remove(cur)
            cur = image(cur)
            count += 1
        sig.append(int(count))
    return sorted(sig)


def _conjugate_by(u: tuple[int, int, int, int, int], m: tuple[int, int, int, int, int]):
    u_inv = analyze._inverse_affine((u, (0, 0)))[0]
    conj = analyze._compose_affine((u_inv, (0, 0)), (m, (0, 0)))
    conj = analyze._compose_affine(conj, (u, (0, 0)))
    return conj[0]


def build_report() -> dict[str, Any]:
    gl2 = list(analyze._gl2_3())
    diag = (2, 0, 0, 1, 2)  # diag(-1,1) over F3
    candidates = [
        m for m in gl2 if m[4] == 2 and analyze._affine_order((m, (0, 0))) == 2
    ]

    points = [(u, v) for u in range(3) for v in range(3)]
    lines = list(analyze._all_affine_lines())

    centralizer = [u for u in gl2 if _conjugate_by(u, diag) == diag]
    class_size_from_orbit_stabilizer = len(gl2) // len(centralizer)

    rows: list[dict[str, Any]] = []
    for mat in sorted(candidates):
        conjugators = [u for u in gl2 if _conjugate_by(u, mat) == diag]
        point_sig = _cycle_signature(
            points, lambda p: analyze._map_point(mat, (0, 0), p)
        )
        line_sig = _cycle_signature(lines, lambda l: analyze._map_line(mat, (0, 0), l))
        rows.append(
            {
                "matrix": list(mat),
                "conjugator_count_to_diag": int(len(conjugators)),
                "conjugator_example": list(conjugators[0]) if conjugators else None,
                "point_cycle_signature": point_sig,
                "line_cycle_signature": line_sig,
                "fixed_point_count": int(point_sig.count(1)),
                "fixed_line_count": int(line_sig.count(1)),
            }
        )

    point_sigs = sorted({tuple(row["point_cycle_signature"]) for row in rows})
    line_sigs = sorted({tuple(row["line_cycle_signature"]) for row in rows})
    conj_counts = sorted({int(row["conjugator_count_to_diag"]) for row in rows})

    return {
        "status": "ok",
        "generated_utc": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "group_counts": {
            "gl2_3_size": int(len(gl2)),
            "det2_order2_involution_count": int(len(candidates)),
            "diag_centralizer_size": int(len(centralizer)),
            "class_size_from_orbit_stabilizer": int(class_size_from_orbit_stabilizer),
        },
        "conjugacy": {
            "canonical_diag": list(diag),
            "all_candidates_conjugate_to_diag": bool(
                rows and all(row["conjugator_count_to_diag"] > 0 for row in rows)
            ),
            "uniform_conjugator_count_set": conj_counts,
        },
        "graph_action_profile": {
            "unique_point_cycle_signatures": [list(sig) for sig in point_sigs],
            "unique_line_cycle_signatures": [list(sig) for sig in line_sigs],
            "point_signature_expected": [1, 1, 1, 2, 2, 2],
            "line_signature_expected": [1, 1, 1, 1, 2, 2, 2, 2],
            "all_point_signatures_match_expected": bool(
                point_sigs == [(1, 1, 1, 2, 2, 2)]
            ),
            "all_line_signatures_match_expected": bool(
                line_sigs == [(1, 1, 1, 1, 2, 2, 2, 2)]
            ),
        },
        "candidates": rows,
        "claim": (
            "All det=2 order-2 elements in GL(2,3) form one conjugacy class "
            "represented by diag(-1,1), and induce a uniform affine-graph cycle "
            "profile on AG(2,3): points [1,1,1,2,2,2], lines [1,1,1,1,2,2,2,2]."
        ),
        "claim_holds": bool(
            len(candidates) == class_size_from_orbit_stabilizer
            and rows
            and all(row["conjugator_count_to_diag"] > 0 for row in rows)
            and point_sigs == [(1, 1, 1, 2, 2, 2)]
            and line_sigs == [(1, 1, 1, 1, 2, 2, 2, 2)]
        ),
    }


def render_md(report: dict[str, Any]) -> str:
    g = report["group_counts"]
    c = report["conjugacy"]
    p = report["graph_action_profile"]

    lines: list[str] = []
    lines.append("# GL(2,3) Involution Conjugacy Bridge (2026-02-11)")
    lines.append("")
    lines.append("- `|GL(2,3)|`: `{}`".format(g["gl2_3_size"]))
    lines.append(
        "- det=2, order-2 involution count: `{}`".format(
            g["det2_order2_involution_count"]
        )
    )
    lines.append(
        "- centralizer size of `diag(-1,1)`: `{}`".format(g["diag_centralizer_size"])
    )
    lines.append(
        "- class size via orbit-stabilizer: `{}`".format(
            g["class_size_from_orbit_stabilizer"]
        )
    )
    lines.append(
        "- all candidates conjugate to `diag(-1,1)`: `{}`".format(
            c["all_candidates_conjugate_to_diag"]
        )
    )
    lines.append("- claim holds: `{}`".format(report["claim_holds"]))
    lines.append("")
    lines.append("## Graph Profile")
    lines.append("")
    lines.append(
        "- unique point-cycle signatures on `AG(2,3)` points: `{}`".format(
            p["unique_point_cycle_signatures"]
        )
    )
    lines.append(
        "- unique line-cycle signatures on affine-line graph vertices: `{}`".format(
            p["unique_line_cycle_signatures"]
        )
    )
    lines.append("")
    lines.append("## Candidate Rows")
    lines.append("")
    lines.append(
        "| matrix | conjugator_count | point_cycle_signature | line_cycle_signature |"
    )
    lines.append("|---|---:|---|---|")
    for row in report.get("candidates", []):
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` |".format(
                row["matrix"],
                row["conjugator_count_to_diag"],
                row["point_cycle_signature"],
                row["line_cycle_signature"],
            )
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "gl2_f3_involution_conjugacy_2026_02_11.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "docs" / "GL2_F3_INVOLUTION_CONJUGACY_2026_02_11.md",
    )
    args = parser.parse_args()

    report = build_report()
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_md(report), encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
