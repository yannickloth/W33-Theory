#!/usr/bin/env python3
"""Bridge s12 grade dimensions to block-cyclic Z3 gradings of sl_n."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _load_s12_dimensions(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    dims = payload.get("algebra_dimensions", {})
    return {
        "source": str(path),
        "total_nonzero": int(dims.get("total_nonzero", 0)),
        "grade0": int(dims.get("grade0", 0)),
        "grade1": int(dims.get("grade1", 0)),
        "grade2": int(dims.get("grade2", 0)),
        "quotient_by_grade0": int(dims.get("quotient_by_grade0", 0)),
    }


def _sl_n_block_cyclic_z3_dims(a: int, b: int, c: int) -> dict[str, int]:
    n = int(a + b + c)
    g1 = int(a * b + b * c + c * a)
    return {
        "n": n,
        "g0": int(a * a + b * b + c * c - 1),
        "g1": g1,
        "g2": g1,
        "total": int(n * n - 1),
    }


def _find_matching_partitions(
    target_g0: int, target_g1: int, target_g2: int, max_block_size: int
) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for a in range(1, int(max_block_size) + 1):
        for b in range(a, int(max_block_size) + 1):
            for c in range(b, int(max_block_size) + 1):
                dims = _sl_n_block_cyclic_z3_dims(a, b, c)
                if (
                    dims["g0"] == int(target_g0)
                    and dims["g1"] == int(target_g1)
                    and dims["g2"] == int(target_g2)
                ):
                    matches.append(
                        {
                            "block_sizes": [int(a), int(b), int(c)],
                            "n": int(dims["n"]),
                            "a_family_rank": int(dims["n"] - 1),
                            "grade0": int(dims["g0"]),
                            "grade1": int(dims["g1"]),
                            "grade2": int(dims["g2"]),
                            "total_dim": int(dims["total"]),
                        }
                    )
    return matches


def _a_family_rank_from_total_dim(total_dim: int) -> int | None:
    n2 = int(total_dim) + 1
    if n2 <= 0:
        return None
    root = int(math.isqrt(n2))
    if root * root != n2:
        return None
    if root < 2:
        return None
    return int(root - 1)


def build_bridge_report(s12_report_json: Path, max_block_size: int) -> dict[str, Any]:
    s12 = _load_s12_dimensions(s12_report_json)
    matches = _find_matching_partitions(
        target_g0=s12["grade0"],
        target_g1=s12["grade1"],
        target_g2=s12["grade2"],
        max_block_size=int(max_block_size),
    )
    equal_block_hits = [
        rec for rec in matches if rec["block_sizes"][0] == rec["block_sizes"][2]
    ]
    rank_from_total = _a_family_rank_from_total_dim(s12["total_nonzero"])
    unique_sorted_solution = len(matches) == 1
    first_match = matches[0] if matches else None

    canonical_rows = []
    for block in range(1, 13):
        dims = _sl_n_block_cyclic_z3_dims(block, block, block)
        canonical_rows.append(
            {
                "block_size": int(block),
                "n": int(3 * block),
                "a_family_rank": int(3 * block - 1),
                "grade0": int(dims["g0"]),
                "grade1": int(dims["g1"]),
                "grade2": int(dims["g2"]),
                "total_dim": int(dims["total"]),
            }
        )

    bridge_claim_holds = bool(
        unique_sorted_solution
        and first_match is not None
        and first_match["block_sizes"] == [9, 9, 9]
        and first_match["total_dim"] == s12["total_nonzero"]
        and rank_from_total == first_match["a_family_rank"]
    )

    return {
        "status": "ok",
        "generated_utc": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "s12_dimensions": s12,
        "search": {
            "max_block_size": int(max_block_size),
            "match_count": int(len(matches)),
            "unique_sorted_solution": bool(unique_sorted_solution),
            "matches": matches,
            "equal_block_match_count": int(len(equal_block_hits)),
            "equal_block_matches": equal_block_hits,
        },
        "vogel_a_family_bridge": {
            "total_dim": int(s12["total_nonzero"]),
            "a_family_rank_from_total_dim": rank_from_total,
            "rank_matches_solution": bool(
                first_match is not None
                and rank_from_total is not None
                and int(first_match["a_family_rank"]) == int(rank_from_total)
            ),
        },
        "canonical_equal_block_family": canonical_rows,
        "bridge_claim": (
            "The s12 split (242,243,243) is uniquely realized by the block-cyclic "
            "Z3 grading of sl_27 with block partition 27=9+9+9, yielding "
            "g0=3*9^2-1=242 and g1=g2=3*9^2=243."
        ),
        "bridge_claim_holds": bool(bridge_claim_holds),
        "web_sources": [
            {
                "title": "Vogel universality and beyond",
                "url": "https://arxiv.org/abs/2601.01612",
                "year": 2026,
            },
            {
                "title": "A universal Lie algebra generated by one element and one relation",
                "url": "https://arxiv.org/abs/2506.15280",
                "year": 2025,
            },
            {
                "title": "Periodic contractions of semisimple Lie algebras and delta-quasi-Jordan algebras",
                "url": "https://www.worldscientific.com/doi/abs/10.1142/S021949882250059X",
                "year": 2022,
            },
            {
                "title": "Finite order automorphisms of semisimple Lie algebras",
                "url": "https://www.mathnet.ru/php/archive.phtml?wshow=paper&jrnid=im&paperid=3460&option_lang=eng",
                "year": 1969,
            },
        ],
    }


def _render_markdown(report: dict[str, Any]) -> str:
    s12 = report["s12_dimensions"]
    search = report["search"]
    vogel = report["vogel_a_family_bridge"]

    lines: list[str] = []
    lines.append("# s12 <-> sl_27 Z3 Grading Bridge (2026-02-11)")
    lines.append("")
    lines.append("- s12 source: `{}`".format(s12["source"]))
    lines.append(
        "- s12 dimensions: `({}, {}, {})`".format(
            s12["grade0"], s12["grade1"], s12["grade2"]
        )
    )
    lines.append("- s12 total nonzero dimension: `{}`".format(s12["total_nonzero"]))
    lines.append(
        "- matching 3-block partitions found: `{}`".format(search["match_count"])
    )
    lines.append(
        "- unique sorted solution: `{}`".format(search["unique_sorted_solution"])
    )
    lines.append(
        "- A-family rank from total dimension (`n^2-1` inversion): `A_{}`".format(
            vogel["a_family_rank_from_total_dim"]
        )
    )
    lines.append("- bridge claim holds: `{}`".format(report["bridge_claim_holds"]))
    lines.append("")
    lines.append("## Matching Partitions")
    lines.append("")
    if not search["matches"]:
        lines.append("- none")
    else:
        for rec in search["matches"]:
            lines.append(
                "- blocks `{}` -> `(g0,g1,g2,total)=({}, {}, {}, {})`, rank `A_{}`".format(
                    rec["block_sizes"],
                    rec["grade0"],
                    rec["grade1"],
                    rec["grade2"],
                    rec["total_dim"],
                    rec["a_family_rank"],
                )
            )
    lines.append("")
    lines.append("## Equal-Block Family")
    lines.append("")
    lines.append(
        "- For `sl_(3r)` with blocks `(r,r,r)`: `g0=3r^2-1`, `g1=g2=3r^2`, `total=9r^2-1`."
    )
    lines.append("- Selected rows:")
    for rec in report["canonical_equal_block_family"]:
        if rec["block_size"] in {1, 2, 3, 6, 9, 12}:
            lines.append(
                "- `r={}` -> `(g0,g1,g2,total)=({}, {}, {}, {})`".format(
                    rec["block_size"],
                    rec["grade0"],
                    rec["grade1"],
                    rec["grade2"],
                    rec["total_dim"],
                )
            )
    lines.append("")
    lines.append("## Sources")
    lines.append("")
    for src in report.get("web_sources", []):
        lines.append("- {}: [{}]({})".format(src["year"], src["title"], src["url"]))
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--s12-report-json",
        type=Path,
        default=ROOT / "artifacts" / "s12_universalization_report.json",
    )
    parser.add_argument("--max-block-size", type=int, default=60)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "s12_sl27_z3_bridge_2026_02_11.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "docs" / "S12_SL27_Z3_BRIDGE_2026_02_11.md",
    )
    args = parser.parse_args()

    report = build_bridge_report(
        s12_report_json=args.s12_report_json,
        max_block_size=int(args.max_block_size),
    )
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    rendered = _render_markdown(report)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(rendered, encoding="utf-8")

    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
