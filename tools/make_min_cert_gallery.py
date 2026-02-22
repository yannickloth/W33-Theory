#!/usr/bin/env python3
"""Render a compact markdown gallery for classified minimal certificates."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _render_witness_table(canon: list[dict[str, Any]]) -> list[str]:
    lines = []
    lines.append("| line | z | sign | line_type |")
    lines.append("|---|---:|---:|---|")
    for row in canon:
        line_repr = json.dumps(row.get("line", []))
        z = int(row.get("z", 0))
        sign = int(row.get("sign_pm1", row.get("sign", 1)))
        line_type = str(row.get("line_type", ""))
        lines.append(f"| `{line_repr}` | {z} | {sign} | `{line_type}` |")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in-json", type=Path, required=True)
    parser.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "docs" / "MIN_CERT_REPRESENTATIVE_GALLERY.md",
    )
    parser.add_argument("--max-items", type=int, default=12)
    parser.add_argument("--title", type=str, default="Minimal-Certificate Gallery")
    args = parser.parse_args()

    payload = json.loads(args.in_json.read_text(encoding="utf-8"))
    reps = list(payload.get("representatives", []))
    total = len(reps)
    shown = max(0, min(int(args.max_items), total))

    orbit_hist = Counter()
    for entry in reps:
        orbit_hist[str(int(entry.get("orbit_size", 0)))] += 1

    lines = []
    lines.append(f"# {args.title}")
    lines.append("")
    lines.append(f"- Source: `{args.in_json}`")
    lines.append(f"- Total representatives: `{total}`")
    lines.append(f"- Displayed: `{shown}`")
    lines.append(
        "- Orbit histogram: `{}`".format(
            dict(sorted(orbit_hist.items(), key=lambda item: int(item[0])))
        )
    )
    lines.append("")

    for idx, entry in enumerate(reps[:shown], start=1):
        geotype = entry.get("geotype", {})
        lines.append(f"## Representative {idx}")
        lines.append("")
        lines.append(f"- orbit_size: `{int(entry.get('orbit_size', 0))}`")
        lines.append(f"- hit_count: `{int(entry.get('hit_count', 1))}`")
        lines.append(
            f"- unique_lines_count: `{int(geotype.get('unique_lines_count', 0))}`"
        )
        lines.append(
            "- lines_with_multiple_z_count: `{}`".format(
                int(geotype.get("lines_with_multiple_z_count", 0))
            )
        )
        lines.append(
            f"- unique_points_covered: `{int(geotype.get('unique_points_covered', 0))}`"
        )
        lines.append("")
        lines.extend(_render_witness_table(list(entry.get("canonical_repr", []))))
        lines.append("")

    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {args.out_md} (shown={shown}/{total})")


if __name__ == "__main__":
    main()
