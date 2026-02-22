#!/usr/bin/env python3
"""Analyze the grade-level Jacobi failure pattern in the s12 report."""
from __future__ import annotations

import argparse
import datetime as dt
import itertools
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _all_grade_triples() -> list[tuple[int, int, int]]:
    return [(a, b, c) for a in range(3) for b in range(3) for c in range(3)]


def _is_expected_failure(triple: tuple[int, int, int]) -> bool:
    return all(v != 0 for v in triple) and (sum(triple) % 3 != 0)


def _is_two_of_one_one_of_other(triple: tuple[int, int, int]) -> bool:
    if 0 in triple:
        return False
    counts = sorted((triple.count(1), triple.count(2)))
    return counts == [1, 2]


def _permute(
    triple: tuple[int, int, int], perm: tuple[int, int, int]
) -> tuple[int, int, int]:
    return (triple[perm[0]], triple[perm[1]], triple[perm[2]])


def _failure_orbits_under_s3(
    failures: set[tuple[int, int, int]]
) -> list[dict[str, Any]]:
    perms = list(itertools.permutations((0, 1, 2)))
    unseen = set(failures)
    out: list[dict[str, Any]] = []
    while unseen:
        rep = min(unseen)
        orb = sorted({_permute(rep, perm) for perm in perms})
        for item in orb:
            unseen.discard(item)
        out.append(
            {
                "representative": list(rep),
                "size": len(orb),
                "orbit": [list(t) for t in orb],
            }
        )
    out.sort(key=lambda rec: tuple(rec["representative"]))
    return out


def build_report(s12_report_json: Path) -> dict[str, Any]:
    payload = json.loads(s12_report_json.read_text(encoding="utf-8"))
    laws = payload.get("universal_grade_laws", {})
    raw_failures = laws.get("jacobi_failures", [])

    observed_failures = {
        tuple(int(v) for v in row.get("grades", [])) for row in raw_failures
    }
    all_triples = _all_grade_triples()
    expected_failures = {
        triple for triple in all_triples if _is_expected_failure(triple)
    }
    two_one_failures = {
        triple for triple in all_triples if _is_two_of_one_one_of_other(triple)
    }

    missing = sorted(expected_failures - observed_failures)
    extra = sorted(observed_failures - expected_failures)
    pattern_match = not missing and not extra
    two_one_match = observed_failures == two_one_failures

    coeff_hist: dict[str, int] = {}
    for row in raw_failures:
        key = str(int(row.get("jacobi_coeff_mod3", 0)))
        coeff_hist[key] = coeff_hist.get(key, 0) + 1

    orbits = _failure_orbits_under_s3(observed_failures)

    return {
        "status": "ok",
        "generated_utc": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "source": str(s12_report_json),
        "jacobi_failure_count_reported": int(laws.get("jacobi_failure_count", 0)),
        "jacobi_failure_count_observed": int(len(observed_failures)),
        "checked_grade_triples": int(laws.get("checked_grade_triples", 0)),
        "observed_failures": [list(t) for t in sorted(observed_failures)],
        "expected_failures_predicate": "all grades nonzero and (a+b+c) mod 3 != 0",
        "expected_failures": [list(t) for t in sorted(expected_failures)],
        "pattern_match": bool(pattern_match),
        "missing_from_observed": [list(t) for t in missing],
        "extra_in_observed": [list(t) for t in extra],
        "two_of_one_one_of_other_match": bool(two_one_match),
        "coeff_mod3_histogram": coeff_hist,
        "s3_failure_orbits": orbits,
        "s3_orbit_count": len(orbits),
        "claim": (
            "Jacobi failures are exactly the six nonzero grade triples with nonzero "
            "sum mod 3, equivalently the 2+1 nonzero composition pattern "
            "(two entries of one nonzero grade and one of the other)."
        ),
        "claim_holds": bool(pattern_match and two_one_match),
        "web_sources": [
            {
                "title": "Finite order automorphisms of semisimple Lie algebras",
                "url": "https://www.mathnet.ru/php/archive.phtml?wshow=paper&jrnid=im&paperid=3460&option_lang=eng",
                "year": 1969,
            },
            {
                "title": "Periodic contractions of semisimple Lie algebras and delta-quasi-Jordan algebras",
                "url": "https://www.worldscientific.com/doi/abs/10.1142/S021949882250059X",
                "year": 2022,
            },
        ],
    }


def _render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# s12 Jacobi Failure Pattern (2026-02-11)")
    lines.append("")
    lines.append(f"- source: `{report['source']}`")
    lines.append(
        "- failure counts (reported/observed): `{}/{}`".format(
            report["jacobi_failure_count_reported"],
            report["jacobi_failure_count_observed"],
        )
    )
    lines.append(f"- checked triples: `{report['checked_grade_triples']}`")
    lines.append(f"- predicate match: `{report['pattern_match']}`")
    lines.append(
        "- two-of-one/one-of-other match: `{}`".format(
            report["two_of_one_one_of_other_match"]
        )
    )
    lines.append(f"- S3 orbit count on failures: `{report['s3_orbit_count']}`")
    lines.append(f"- claim holds: `{report['claim_holds']}`")
    lines.append("")
    lines.append("## Failures")
    lines.append("")
    for triple in report["observed_failures"]:
        lines.append(f"- `{triple}`")
    lines.append("")
    lines.append("## S3 Orbits")
    lines.append("")
    for orb in report["s3_failure_orbits"]:
        lines.append(
            "- rep `{}` size `{}` orbit `{}`".format(
                orb["representative"],
                orb["size"],
                orb["orbit"],
            )
        )
    lines.append("")
    lines.append("## Sources")
    lines.append("")
    for src in report.get("web_sources", []):
        lines.append(f"- {src['year']}: [{src['title']}]({src['url']})")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--s12-report-json",
        type=Path,
        default=ROOT / "artifacts" / "s12_universalization_report.json",
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "s12_jacobi_failure_pattern_2026_02_11.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "docs" / "S12_JACOBI_FAILURE_PATTERN_2026_02_11.md",
    )
    args = parser.parse_args()

    report = build_report(args.s12_report_json)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(_render_markdown(report), encoding="utf-8")

    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
