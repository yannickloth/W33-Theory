#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze


def _normalize_witness(row: dict[str, Any]) -> dict[str, Any]:
    line = [[int(point[0]), int(point[1])] for point in row.get("line", [])]
    sign_pm1 = int(row.get("sign_pm1", row.get("sign", 1)))
    z_value = int(row.get("z", 0))
    line_type = row.get("line_type")
    if not isinstance(line_type, str) or not line_type:
        line_key = tuple(tuple(point) for point in line)
        line_type = analyze._line_equation_type(line_key)[0]
    return {
        "line": line,
        "z": z_value,
        "sign_pm1": sign_pm1,
        "line_type": str(line_type),
    }


def _safe_int(value: Any, default: int = 1) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def classify_enumeration_payload(payload: dict[str, Any]) -> dict[str, Any]:
    representatives = payload.get("representatives", [])
    if not isinstance(representatives, list):
        raise RuntimeError("Missing representatives list")

    rows: list[dict[str, Any]] = []
    unique_lines_hist = Counter()
    multi_z_hist = Counter()
    family_count_hist = Counter()
    family_set_hist = Counter()
    has_full_z_line_count = 0
    weighted_has_full_z_line = 0
    total_weight = 0
    weighted_unique_lines_hist = Counter()
    weighted_multi_z_hist = Counter()
    weighted_family_count_hist = Counter()
    weighted_family_set_hist = Counter()

    for index, representative in enumerate(representatives):
        witness_rows = representative.get("canonical_repr", [])
        normalized_rows = [_normalize_witness(row) for row in witness_rows]
        geotype = analyze._classify_certificate_witnesses(normalized_rows)
        orbit = analyze._witness_orbit_stats(normalized_rows)
        hit_count = _safe_int(representative.get("hit_count", 1), default=1)
        total_weight += hit_count

        line_type_set = sorted({str(row["line_type"]) for row in normalized_rows})
        line_type_set_key = "|".join(line_type_set)
        unique_lines = int(geotype["unique_lines_count"])
        multi_z_lines = int(geotype["lines_with_multiple_z_count"])
        family_count = int(len(line_type_set))
        has_full_z_line = bool(geotype["has_full_z_line"])

        unique_lines_hist[unique_lines] += 1
        multi_z_hist[multi_z_lines] += 1
        family_count_hist[family_count] += 1
        family_set_hist[line_type_set_key] += 1

        weighted_unique_lines_hist[unique_lines] += hit_count
        weighted_multi_z_hist[multi_z_lines] += hit_count
        weighted_family_count_hist[family_count] += hit_count
        weighted_family_set_hist[line_type_set_key] += hit_count

        if has_full_z_line:
            has_full_z_line_count += 1
            weighted_has_full_z_line += hit_count

        rows.append(
            {
                "index": int(index),
                "hit_count": int(hit_count),
                "witness_count": int(len(normalized_rows)),
                "canonical_repr": normalized_rows,
                "striation_families": line_type_set,
                "striation_family_count": family_count,
                "orbit_size": int(orbit.get("orbit_size", 0)),
                "canonical_orbit_rep": orbit.get("canonical_rep", []),
                "geotype": {
                    "unique_lines_count": unique_lines,
                    "lines_with_multiple_z_count": multi_z_lines,
                    "z_histogram": geotype["z_histogram"],
                    "sign_histogram": geotype["sign_histogram"],
                    "line_type_hist": geotype["line_type_hist"],
                    "unique_points_covered": int(geotype["unique_points_covered"]),
                    "has_full_z_line": has_full_z_line,
                },
            }
        )

    return {
        "status": "ok",
        "source": {
            "mode": payload.get("mode"),
            "candidate_space": payload.get("candidate_space"),
            "k_min": payload.get("k_min"),
            "exact_solutions_count": payload.get("exact_solutions_count"),
            "distinct_canonical_representatives_found": payload.get(
                "distinct_canonical_representatives_found"
            ),
        },
        "total_representatives": int(len(rows)),
        "total_weight": int(total_weight),
        "aggregate": {
            "unique_lines_count_hist": {
                str(key): int(value) for key, value in sorted(unique_lines_hist.items())
            },
            "lines_with_multiple_z_count_hist": {
                str(key): int(value) for key, value in sorted(multi_z_hist.items())
            },
            "striation_family_count_hist": {
                str(key): int(value) for key, value in sorted(family_count_hist.items())
            },
            "striation_family_set_hist": {
                key: int(value) for key, value in sorted(family_set_hist.items())
            },
            "has_full_z_line_count": int(has_full_z_line_count),
            "weighted_unique_lines_count_hist": {
                str(key): int(value)
                for key, value in sorted(weighted_unique_lines_hist.items())
            },
            "weighted_lines_with_multiple_z_count_hist": {
                str(key): int(value)
                for key, value in sorted(weighted_multi_z_hist.items())
            },
            "weighted_striation_family_count_hist": {
                str(key): int(value)
                for key, value in sorted(weighted_family_count_hist.items())
            },
            "weighted_striation_family_set_hist": {
                key: int(value)
                for key, value in sorted(weighted_family_set_hist.items())
            },
            "weighted_has_full_z_line_count": int(weighted_has_full_z_line),
        },
        "representatives": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in-json", type=Path, required=True)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "e6_f3_trilinear_min_cert_classified.json",
    )
    args = parser.parse_args()

    payload = json.loads(args.in_json.read_text(encoding="utf-8"))
    classified = classify_enumeration_payload(payload)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(classified, indent=2), encoding="utf-8")
    print(
        "Wrote {} (reps={}, weighted_total={})".format(
            args.out_json,
            classified["total_representatives"],
            classified["total_weight"],
        )
    )


if __name__ == "__main__":
    main()
