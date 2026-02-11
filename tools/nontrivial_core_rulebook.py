#!/usr/bin/env python3
"""Derive compact rulebook summaries for nontrivial global core triplets.

Consumes the exhaustive size-3 core geometry classification and compresses each
z-cell/striation family into coordinate-level rules on triplet values
`(z_offset0, z_offset1, z_offset2)`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.classify_nontrivial_unsat_core_geometry as geom


def _triples_by_direction(
    signature_set: Sequence[Sequence[Sequence[Any]]],
) -> Dict[str, List[Tuple[int, int, int]]]:
    out: Dict[str, List[Tuple[int, int, int]]] = {}
    for sig in signature_set:
        # sig entries are tuples/lists [line_type, offset, z]
        rows = sorted(sig, key=lambda r: int(r[1]))
        t = str(rows[0][0])
        if any(str(r[0]) != t for r in rows):
            raise RuntimeError(f"Mixed-direction signature encountered: {sig}")
        z_trip = (int(rows[0][2]), int(rows[1][2]), int(rows[2][2]))
        out.setdefault(t, []).append(z_trip)
    return out


def _summarize_triples(triples: Sequence[Tuple[int, int, int]]) -> Dict[str, Any]:
    uniq = sorted(set(triples))
    fixed: Dict[str, int] = {}
    allowed: Dict[str, List[int]] = {}
    coords = list(zip(*uniq))
    for i, vals in enumerate(coords):
        s = sorted(set(vals))
        if len(s) == 1:
            fixed[f"z{i}"] = int(s[0])
        else:
            allowed[f"z{i}"] = [int(v) for v in s]

    varying_idx = [i for i in range(3) if f"z{i}" in allowed]
    product = 1
    for i in varying_idx:
        product *= len(allowed[f"z{i}"])
    missing: List[Tuple[int, ...]] = []
    if varying_idx:
        from itertools import product as cart_product

        present = {tuple(t[i] for i in varying_idx) for t in uniq}
        for p in cart_product(*[allowed[f"z{i}"] for i in varying_idx]):
            if tuple(int(v) for v in p) not in present:
                missing.append(tuple(int(v) for v in p))

    return {
        "triples": [list(map(int, t)) for t in uniq],
        "triple_count": int(len(uniq)),
        "fixed_coordinates": fixed,
        "allowed_coordinates": allowed,
        "varying_coordinate_count": int(len(varying_idx)),
        "cartesian_capacity": int(product),
        "missing_cartesian_points": [list(m) for m in missing],
        "is_full_cartesian_box": len(missing) == 0,
    }


def _cell_rulebook(cell: Dict[str, Any]) -> Dict[str, Any]:
    sig_set = cell["signature_set"]
    by_dir = _triples_by_direction(sig_set)
    per_dir = {d: _summarize_triples(ts) for d, ts in sorted(by_dir.items())}
    return {
        "minimal_core_count": int(cell["minimal_core_count"]),
        "direction_count": int(len(per_dir)),
        "directions": per_dir,
    }


def _iter_direction_rules(rulebook: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    for mode_row in rulebook["matrix"].values():
        for cell in mode_row.values():
            for d in cell["directions"].values():
                yield d


def build_report() -> Dict[str, Any]:
    payload = geom.build_report()

    matrix: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for mode in payload["modes"]:
        row: Dict[str, Dict[str, Any]] = {}
        for a, b in payload["nontrivial_z_maps"]:
            key = f"({a},{b})"
            row[key] = _cell_rulebook(payload["matrix"][mode][key])
        matrix[mode] = row

    rulebook = {
        "status": "ok",
        "modes": payload["modes"],
        "nontrivial_z_maps": payload["nontrivial_z_maps"],
        "matrix": matrix,
    }

    direction_rules = list(_iter_direction_rules(rulebook))
    theorem_flags = {
        "at_most_two_varying_coordinates_per_direction_rule": all(
            int(r["varying_coordinate_count"]) <= 2 for r in direction_rules
        ),
        "at_most_one_missing_cartesian_point_per_direction_rule": all(
            len(r["missing_cartesian_points"]) <= 1 for r in direction_rules
        ),
        "unique_non_cartesian_family_per_mode": all(
            sum(
                1
                for key in matrix[mode]
                for d in matrix[mode][key]["directions"].values()
                if not d["is_full_cartesian_box"]
            )
            == 1
            for mode in payload["modes"]
        ),
        "the_non_cartesian_family_is_z11_x_direction": all(
            len(
                matrix[mode]["(1,1)"]["directions"]
                .get("x", {})
                .get("missing_cartesian_points", [])
            )
            == 1
            and all(
                matrix[mode][key]["directions"][d]["is_full_cartesian_box"]
                for key in matrix[mode]
                for d in matrix[mode][key]["directions"]
                if not (key == "(1,1)" and d == "x")
            )
            for mode in payload["modes"]
        ),
    }

    rulebook["theorem_flags"] = theorem_flags
    rulebook["notes"] = (
        "Nontrivial size-3 global cores admit compact coordinate rulebooks over "
        "offset-ordered triplets."
    )
    return rulebook


def render_md(payload: Dict[str, Any]) -> str:
    lines: List[str] = ["# Nontrivial Core Rulebook", ""]
    lines.append(
        "- Rulebook view for nontrivial size-3 global UNSAT cores by z-map and striation."
    )
    lines.append("")
    lines.append("Mode | z=(1,1) | z=(1,2) | z=(2,0) | z=(2,1) | z=(2,2)")
    lines.append("--- | --- | --- | --- | --- | ---")
    for mode in payload["modes"]:
        vals = []
        for a, b in payload["nontrivial_z_maps"]:
            key = f"({a},{b})"
            vals.append(str(payload["matrix"][mode][key]["direction_count"]))
        lines.append(f"{mode} | " + " | ".join(vals))
    lines.append("")
    lines.append(f"- Theorem flags: `{payload['theorem_flags']}`")
    lines.append("")
    lines.append("## Example Rule (all_agl, z=(1,1), direction x)")
    ex = payload["matrix"]["all_agl"]["(1,1)"]["directions"]["x"]
    lines.append("")
    lines.append(f"- triples: `{ex['triples']}`")
    lines.append(f"- fixed: `{ex['fixed_coordinates']}`")
    lines.append(f"- allowed: `{ex['allowed_coordinates']}`")
    lines.append(f"- missing cartesian points: `{ex['missing_cartesian_points']}`")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("artifacts/nontrivial_core_rulebook_2026_02_11.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("docs/NONTRIVIAL_CORE_RULEBOOK_2026_02_11.md"),
    )
    args = parser.parse_args()

    payload = build_report()
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_md(payload), encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
