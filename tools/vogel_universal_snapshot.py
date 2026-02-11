#!/usr/bin/env python3
"""Build a reproducible Vogel-universality snapshot tied to s12 outputs."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _fraction_str(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def vogel_dimension(alpha: Fraction, beta: Fraction, gamma: Fraction) -> Fraction:
    """Vogel universal dimension formula in the common alpha,beta,gamma gauge."""
    t = alpha + beta + gamma
    numerator = (alpha - 2 * t) * (beta - 2 * t) * (gamma - 2 * t)
    denominator = alpha * beta * gamma
    if denominator == 0:
        raise ZeroDivisionError("Degenerate Vogel parameters with zero denominator.")
    return Fraction(numerator, denominator)


def _is_square(num: int) -> bool:
    if num < 0:
        return False
    root = int(math.isqrt(num))
    return root * root == num


def _solve_classical_hits(target_dim: int) -> dict[str, list[int]]:
    hits = {"A": [], "B": [], "C": [], "D": []}

    # A_{n-1}: dim = n^2 - 1
    n2 = int(target_dim) + 1
    if _is_square(n2):
        n = int(math.isqrt(n2))
        if n >= 2:
            hits["A"].append(n - 1)

    # B_n / C_n: dim = n(2n+1)
    disc_bc = 1 + 8 * int(target_dim)
    if _is_square(disc_bc):
        root = int(math.isqrt(disc_bc))
        if (root - 1) % 4 == 0:
            n = (root - 1) // 4
            if n >= 2:
                hits["B"].append(n)
                hits["C"].append(n)

    # D_n: dim = n(2n-1)
    disc_d = 1 + 8 * int(target_dim)
    if _is_square(disc_d):
        root = int(math.isqrt(disc_d))
        if (root + 1) % 4 == 0:
            n = (root + 1) // 4
            if n >= 4:
                hits["D"].append(n)

    return hits


def _exceptional_line_parametrization_holds() -> dict[str, Any]:
    entries = [
        ("G2", Fraction(-2, 3), 14),
        ("D4", Fraction(0, 1), 28),
        ("F4", Fraction(1, 1), 52),
        ("E6", Fraction(2, 1), 78),
        ("E7", Fraction(4, 1), 133),
        ("E8", Fraction(8, 1), 248),
    ]
    rows = []
    for name, m, expected_dim in entries:
        alpha = Fraction(-2, 1)
        beta = m + 4
        gamma = 2 * m + 4
        got = vogel_dimension(alpha, beta, gamma)
        rows.append(
            {
                "name": name,
                "m": _fraction_str(m),
                "alpha": _fraction_str(alpha),
                "beta": _fraction_str(beta),
                "gamma": _fraction_str(gamma),
                "expected_dim": int(expected_dim),
                "vogel_dim": int(got),
                "matches": int(got) == int(expected_dim),
            }
        )
    return {
        "all_match": all(row["matches"] for row in rows),
        "rows": rows,
    }


def _search_exceptional_line_target(
    target_dim: int, max_denominator: int = 24, abs_numerator_bound: int = 2000
) -> dict[str, Any]:
    hits = set()
    alpha = Fraction(-2, 1)
    for denominator in range(1, int(max_denominator) + 1):
        for numerator in range(-abs_numerator_bound, abs_numerator_bound + 1):
            m = Fraction(numerator, denominator)
            beta = m + 4
            gamma = 2 * m + 4
            den = alpha * beta * gamma
            if den == 0:
                continue
            if vogel_dimension(alpha, beta, gamma) == int(target_dim):
                hits.add(m)
    return {
        "target_dim": int(target_dim),
        "search_max_denominator": int(max_denominator),
        "search_abs_numerator_bound": int(abs_numerator_bound),
        "hit_count": len(hits),
        "hits": [_fraction_str(v) for v in sorted(hits)],
    }


def _load_s12_report(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_snapshot(
    s12_report_path: Path, exceptional_line_denominator_cap: int = 24
) -> dict[str, Any]:
    exceptional_direct = {
        "A2": (Fraction(-2), Fraction(2), Fraction(3), 8),
        "G2": (Fraction(-2), Fraction(10, 3), Fraction(8, 3), 14),
        "D4": (Fraction(-2), Fraction(4), Fraction(4), 28),
        "F4": (Fraction(-2), Fraction(5), Fraction(6), 52),
        "E6": (Fraction(-2), Fraction(6), Fraction(8), 78),
        "E7": (Fraction(-2), Fraction(8), Fraction(12), 133),
        "E8": (Fraction(-2), Fraction(12), Fraction(20), 248),
    }
    direct_rows = []
    for name, (alpha, beta, gamma, expected_dim) in exceptional_direct.items():
        got = vogel_dimension(alpha, beta, gamma)
        direct_rows.append(
            {
                "name": name,
                "alpha": _fraction_str(alpha),
                "beta": _fraction_str(beta),
                "gamma": _fraction_str(gamma),
                "expected_dim": int(expected_dim),
                "vogel_dim": int(got),
                "matches": int(got) == int(expected_dim),
            }
        )

    s12_report = _load_s12_report(s12_report_path)
    s12_summary = None
    if s12_report is not None:
        laws = s12_report.get("universal_grade_laws", {})
        checks = s12_report.get("exhaustive_checks", {})
        s12_summary = {
            "source": str(s12_report_path),
            "total_nonzero_dim": int(
                s12_report.get("algebra_dimensions", {}).get("total_nonzero", 0)
            ),
            "quotient_dim": int(
                s12_report.get("algebra_dimensions", {}).get("quotient_by_grade0", 0)
            ),
            "jacobi_failure_count": int(laws.get("jacobi_failure_count", 0)),
            "checked_grade_triples": int(laws.get("checked_grade_triples", 0)),
            "jacobi_holds": bool(laws.get("jacobi_coefficient_identity_holds", False)),
            "ad3_holds": bool(laws.get("ad3_coefficient_identity_holds", False)),
            "jordan_symmetry_holds": bool(
                laws.get("jordan_triple_xz_symmetry_holds", False)
            ),
            "ad3_zero_on_g1_holds": bool(
                checks.get("ad3_zero_on_g1", {}).get("holds", False)
            ),
        }

    target_dims = [728, 486, 242]
    classical_hits = {str(dim): _solve_classical_hits(dim) for dim in target_dims}
    exceptional_line_hits = {
        str(dim): _search_exceptional_line_target(
            dim,
            max_denominator=exceptional_line_denominator_cap,
            abs_numerator_bound=2500,
        )
        for dim in target_dims
    }

    snapshot = {
        "status": "ok",
        "generated_utc": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "vogel_dimension_formula": "dim = ((alpha-2t)(beta-2t)(gamma-2t))/(alpha*beta*gamma), t=alpha+beta+gamma",
        "exceptional_direct_table": {
            "all_match": all(row["matches"] for row in direct_rows),
            "rows": direct_rows,
        },
        "exceptional_line_parametrization": _exceptional_line_parametrization_holds(),
        "target_dimension_hits": {
            "classical_families": classical_hits,
            "exceptional_line_rational_search": exceptional_line_hits,
        },
        "s12_bridge": s12_summary,
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
                "title": "On Refined Vogel's universality and link homologies",
                "url": "https://arxiv.org/abs/2504.13831",
                "year": 2025,
            },
            {
                "title": "On Macdonald deformation of Vogel's universality and LMOV-like formula for exceptional hyperpolynomials",
                "url": "https://arxiv.org/abs/2505.16569",
                "year": 2025,
            },
            {
                "title": "Vogel's universality and Macdonald dimensions",
                "url": "https://arxiv.org/abs/2507.11414",
                "year": 2025,
            },
            {
                "title": "Construction of the Lie algebra weight system kernel via Vogel algebra",
                "url": "https://arxiv.org/abs/2411.14417",
                "year": 2024,
            },
            {
                "title": "Vogel universality and differential operators on Jacobi diagrams",
                "url": "https://link.springer.com/article/10.1140/epjc/s10052-025-14406-9",
                "year": 2025,
            },
            {
                "title": "On Macdonald deformation of Vogel's universality and LMOV-like formula for exceptional hyperpolynomials",
                "url": "https://doi.org/10.1016/j.physletb.2025.139730",
                "year": 2025,
            },
        ],
    }
    return snapshot


def _render_markdown(snapshot: dict[str, Any]) -> str:
    lines = []
    lines.append("# Vogel Universal Snapshot (2026-02-11)")
    lines.append("")
    lines.append("- Formula: `{}`".format(snapshot.get("vogel_dimension_formula", "")))
    lines.append(
        "- Exceptional direct table matches: `{}`".format(
            snapshot["exceptional_direct_table"]["all_match"]
        )
    )
    lines.append(
        "- Exceptional-line parametrization matches: `{}`".format(
            snapshot["exceptional_line_parametrization"]["all_match"]
        )
    )
    lines.append("")
    lines.append("## Target-Dimension Scan")
    lines.append("")
    for key, value in snapshot["target_dimension_hits"]["classical_families"].items():
        lines.append(f"- dim `{key}` classical hits: `{value}`")
    for key, value in snapshot["target_dimension_hits"][
        "exceptional_line_rational_search"
    ].items():
        lines.append(
            "- dim `{}` exceptional-line rational hits (den<= {}): `{}`".format(
                key,
                value["search_max_denominator"],
                value["hit_count"],
            )
        )
    lines.append("")
    s12 = snapshot.get("s12_bridge")
    if s12:
        lines.append("## s12 Bridge")
        lines.append("")
        lines.append(f"- source: `{s12['source']}`")
        lines.append(f"- dim(s12): `{s12['total_nonzero_dim']}`")
        lines.append(f"- dim(s12 / grade0): `{s12['quotient_dim']}`")
        lines.append(
            "- Jacobi status: `{}` with failures `{}/{} grade triples`".format(
                s12["jacobi_holds"],
                s12["jacobi_failure_count"],
                s12["checked_grade_triples"],
            )
        )
        lines.append(f"- ad^3 law holds: `{s12['ad3_holds']}`")
        lines.append(
            f"- Jordan triple symmetry holds: `{s12['jordan_symmetry_holds']}`"
        )
        lines.append("")
    lines.append("## Recent Sources")
    lines.append("")
    for src in snapshot.get("web_sources", []):
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
        "--exceptional-line-denominator-cap",
        type=int,
        default=24,
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "vogel_universal_snapshot_2026_02_11.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "docs" / "VOGEL_UNIVERSAL_RESEARCH_2026_02_11.md",
    )
    args = parser.parse_args()

    snapshot = build_snapshot(
        s12_report_path=args.s12_report_json,
        exceptional_line_denominator_cap=int(args.exceptional_line_denominator_cap),
    )
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    rendered = _render_markdown(snapshot)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(rendered, encoding="utf-8")

    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
