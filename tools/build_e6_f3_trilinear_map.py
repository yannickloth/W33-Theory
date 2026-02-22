#!/usr/bin/env python3
"""
Build a finite-field analogue of the E6 cubic:
  T : {0..26}^3 -> F3
from canonical signed cubic triads and the Heisenberg labeling on H27.

Conventions:
  - Only distinct-index triads are nonzero.
  - sign +1 -> coeff 1 (mod 3)
  - sign -1 -> coeff 2 (mod 3), i.e. -1 in F3.
  - Sparse output stores 45 unordered nonzero triads.

Inputs (defaults):
  - artifacts/canonical_su3_gauge_and_cubic.json
  - artifacts/e6_cubic_affine_heisenberg_model.json

Outputs:
  - artifacts/e6_f3_trilinear_map.json
  - artifacts/e6_f3_trilinear_map.md
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import sys

# ensure project root on sys.path so `src.*` imports work when script is executed directly from tools/
sys.path.insert(0, str(ROOT))

from src.e6_f3_trilinear import (
    HeisenbergLabel,
    classify_triad_geometry,
    ordered_nonzero_entries_count,
    sign_to_f3_coeff,
    sorted_u_line_for_triad,
    triad_key,
    z_profile_over_u_line,
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_signed_triples(
    cubic: dict[str, Any]
) -> list[tuple[tuple[int, int, int], int]]:
    sol = cubic.get("solution")
    if isinstance(sol, dict):
        d_triples = sol.get("d_triples")
        if isinstance(d_triples, list):
            out = []
            for row in d_triples:
                if not isinstance(row, dict):
                    continue
                tri = triad_key(row["triple"])
                sign = int(row["sign"])
                out.append((tri, sign))
            if out:
                return out

    # Fallback: if only triad support is present, set sign=+1.
    triads = cubic.get("triads")
    if isinstance(triads, list):
        return [(triad_key(t), 1) for t in triads]

    raise RuntimeError("Could not extract signed triads from cubic input JSON")


def _load_heisenberg_labels(heis: dict[str, Any]) -> dict[int, HeisenbergLabel]:
    raw = heis.get("e6id_to_heisenberg")
    if not isinstance(raw, dict):
        raise RuntimeError("Missing e6id_to_heisenberg in Heisenberg JSON")
    labels: dict[int, HeisenbergLabel] = {}
    for k, v in raw.items():
        e6id = int(k)
        if not isinstance(v, dict):
            raise RuntimeError(f"Bad heisenberg row for id {k}")
        u = v.get("u")
        z = v.get("z")
        if not (isinstance(u, list) and len(u) == 2):
            raise RuntimeError(f"Bad u for id {k}")
        labels[e6id] = HeisenbergLabel(u=(int(u[0]), int(u[1])), z=int(z))
    return labels


def _build_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# E6 F3 trilinear map")
    lines.append("")
    lines.append(
        "- Nonzero unordered entries: `{}`".format(
            report["counts"]["nonzero_unordered"]
        )
    )
    lines.append(
        "- Nonzero ordered entries: `{}`".format(report["counts"]["nonzero_ordered"])
    )
    lines.append("- Geometry histogram: `{}`".format(report["counts"]["geometry"]))
    lines.append("- Coeff histogram (F3): `{}`".format(report["counts"]["coeff_f3"]))
    lines.append("")
    lines.append("## Affine line slices")
    lines.append(
        "- Distinct u-lines: `{}`".format(report["counts"]["distinct_affine_u_lines"])
    )
    lines.append(
        "- Per-line triad multiplicities: `{}`".format(
            report["counts"]["affine_u_line_sizes"]
        )
    )
    lines.append("")
    lines.append("## Notes")
    lines.append("- `coeff_f3=1` means +1; `coeff_f3=2` means -1 in F3.")
    lines.append(
        "- Triads are stored as sorted E6 ids; tensor is symmetric in indices."
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--in-cubic",
        type=Path,
        default=ROOT / "artifacts" / "canonical_su3_gauge_and_cubic.json",
    )
    parser.add_argument(
        "--in-heisenberg",
        type=Path,
        default=ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json",
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "e6_f3_trilinear_map.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "artifacts" / "e6_f3_trilinear_map.md",
    )
    args = parser.parse_args()

    cubic = _load_json(args.in_cubic)
    heis = _load_json(args.in_heisenberg)

    signed = _extract_signed_triples(cubic)
    labels = _load_heisenberg_labels(heis)

    triad_to_sign: dict[tuple[int, int, int], int] = {}
    for triad, sign in signed:
        if triad in triad_to_sign and triad_to_sign[triad] != sign:
            raise RuntimeError(f"Conflicting sign assignment for triad {triad}")
        triad_to_sign[triad] = sign

    geometry_counter: Counter[str] = Counter()
    coeff_counter: Counter[int] = Counter()
    coeff_counter_by_kind: dict[str, Counter[int]] = defaultdict(Counter)
    by_u_line: dict[
        tuple[tuple[int, int], tuple[int, int], tuple[int, int]],
        list[dict[str, Any]],
    ] = defaultdict(list)
    entries: list[dict[str, Any]] = []

    for triad in sorted(triad_to_sign):
        sign = int(triad_to_sign[triad])
        coeff = sign_to_f3_coeff(sign)
        kind = classify_triad_geometry(triad, labels)
        geometry_counter[kind] += 1
        coeff_counter[coeff] += 1
        coeff_counter_by_kind[kind][coeff] += 1

        row: dict[str, Any] = {
            "triad": [int(x) for x in triad],
            "sign_pm1": int(sign),
            "coeff_f3": int(coeff),
            "kind": kind,
            "heisenberg": [
                {
                    "e6id": int(i),
                    "u": [int(labels[i].u[0]), int(labels[i].u[1])],
                    "z": int(labels[i].z),
                }
                for i in triad
            ],
        }

        if kind == "affine_line":
            u_line = sorted_u_line_for_triad(triad, labels)
            z_profile = z_profile_over_u_line(triad, labels, u_line)
            row["u_line"] = [[int(u[0]), int(u[1])] for u in u_line]
            row["z_profile_over_u_line"] = [int(z) for z in z_profile]
            row["z_sum_mod3"] = int(sum(z_profile) % 3)
            by_u_line[u_line].append(
                {
                    "triad": [int(x) for x in triad],
                    "sign_pm1": int(sign),
                    "coeff_f3": int(coeff),
                    "z_profile_over_u_line": [int(z) for z in z_profile],
                    "z_sum_mod3": int(sum(z_profile) % 3),
                }
            )

        entries.append(row)

    if geometry_counter.get("other", 0) != 0:
        raise RuntimeError("Found non-fiber/non-affine triads in signed cubic support")

    line_sizes = sorted(len(v) for v in by_u_line.values())

    report = {
        "status": "ok",
        "inputs": {
            "cubic_json": str(args.in_cubic),
            "heisenberg_json": str(args.in_heisenberg),
        },
        "counts": {
            "nonzero_unordered": len(entries),
            "nonzero_ordered": ordered_nonzero_entries_count(len(entries)),
            "geometry": dict(sorted(geometry_counter.items())),
            "coeff_f3": {str(k): int(v) for k, v in sorted(coeff_counter.items())},
            "coeff_f3_by_kind": {
                kind: {str(k): int(v) for k, v in sorted(counter.items())}
                for kind, counter in sorted(coeff_counter_by_kind.items())
            },
            "distinct_affine_u_lines": int(len(by_u_line)),
            "affine_u_line_sizes": line_sizes,
        },
        "sparse_unordered_entries": entries,
        "affine_u_line_slices": [
            {
                "u_line": [[int(u[0]), int(u[1])] for u in u_line],
                "entries": sorted(rows, key=lambda r: tuple(r["triad"])),
            }
            for u_line, rows in sorted(by_u_line.items())
        ],
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    args.out_md.write_text(_build_markdown(report), encoding="utf-8")

    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
