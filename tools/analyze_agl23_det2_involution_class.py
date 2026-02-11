#!/usr/bin/env python3
"""Classify det=2 order-2 involutions inside AGL(2,3).

This is a pure finite computation that produces:
- the size and conjugacy-class structure of the det=2 involution set,
- a D12-structured centralizer fingerprint,
- induced action signatures on AG(2,3) points and affine lines.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable, TypeVar

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze

T = TypeVar("T")


def _cycle_signature(items: Iterable[T], image: Callable[[T], T]) -> list[int]:
    unseen = set(items)
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


def _fixed_points(
    elem: tuple[tuple[int, int, int, int, int], tuple[int, int]],
    points: list[tuple[int, int]],
) -> list[tuple[int, int]]:
    mat, shift = elem
    return sorted(p for p in points if analyze._map_point(mat, shift, p) == p)


def _fixed_lines(
    elem: tuple[tuple[int, int, int, int, int], tuple[int, int]],
    lines: list[tuple[tuple[int, int], tuple[int, int], tuple[int, int]]],
) -> list[tuple[tuple[int, int], tuple[int, int], tuple[int, int]]]:
    mat, shift = elem
    return sorted(L for L in lines if analyze._map_line(mat, shift, L) == L)


def _order(elem: tuple[tuple[int, int, int, int, int], tuple[int, int]]) -> int:
    return int(analyze._affine_order(elem))


def _conjugate(
    g: tuple[tuple[int, int, int, int, int], tuple[int, int]],
    x: tuple[tuple[int, int, int, int, int], tuple[int, int]],
) -> tuple[tuple[int, int, int, int, int], tuple[int, int]]:
    inv_g = analyze._inverse_affine(g)
    return analyze._compose_affine(analyze._compose_affine(inv_g, x), g)


def build_report() -> dict[str, Any]:
    points = [(x, y) for x in range(3) for y in range(3)]
    lines = list(analyze._all_affine_lines())
    mats = list(analyze._gl2_3())
    agl = [(mat, shift) for mat in mats for shift in points]

    candidates = [elem for elem in agl if int(elem[0][4]) == 2 and _order(elem) == 2]

    unseen = set(candidates)
    classes: list[set[tuple[tuple[int, int, int, int, int], tuple[int, int]]]] = []
    candidate_set = set(candidates)
    while unseen:
        rep = next(iter(unseen))
        cls = {_conjugate(g, rep) for g in agl}
        cls &= candidate_set
        classes.append(cls)
        unseen -= cls

    class_sizes = sorted(len(cls) for cls in classes)
    rep = next(iter(classes[0])) if classes else None

    centralizer: list[tuple[tuple[int, int, int, int, int], tuple[int, int]]] = []
    centralizer_order_hist: dict[str, int] = {}
    rep_fixed_points: list[list[int]] = []
    rep_fixed_lines: list[list[list[int]]] = []
    rep_point_cycle_sig: list[int] = []
    rep_line_cycle_sig: list[int] = []
    rep_fixed_line_type_hist: dict[str, int] = {}
    fixed_line_fiber_hist: dict[str, int] = {}
    fixed_line_type_fiber_hist: dict[str, dict[str, int]] = {}

    # Reflection structure: det=-1 affine involutions behave like "reflections":
    #  - 3 fixed points (an affine axis line),
    #  - 4 fixed lines (axis line + an entire striation of 3 parallel lines).
    axis_type_hist = Counter()
    fixed_striation_type_hist = Counter()
    axis_type_vs_fixed_striation_type = Counter()
    axis_line_to_types: dict[str, str] = {}
    axis_line_to_striations: dict[str, set[str]] = defaultdict(set)
    axis_line_and_striation_pairs = Counter()
    reflection_failures: list[dict[str, Any]] = []

    if rep is not None:
        centralizer = [g for g in agl if _conjugate(g, rep) == rep]
        cent_hist = Counter(_order(g) for g in centralizer)
        centralizer_order_hist = {str(k): int(v) for k, v in sorted(cent_hist.items())}

        fps = _fixed_points(rep, points)
        fls = _fixed_lines(rep, lines)
        rep_fixed_points = [list(p) for p in fps]
        rep_fixed_lines = [[list(p) for p in L] for L in fls]
        rep_point_cycle_sig = _cycle_signature(
            points, lambda p: analyze._map_point(rep[0], rep[1], p)
        )
        rep_line_cycle_sig = _cycle_signature(
            lines, lambda L: analyze._map_line(rep[0], rep[1], L)
        )
        rep_fixed_line_type_hist = Counter(
            analyze._line_equation_type(L)[0] for L in fls
        )
        rep_fixed_line_type_hist = {
            str(k): int(v) for k, v in sorted(rep_fixed_line_type_hist.items())
        }

        # Fiber: involution -> fixed-point line (3 points); count per affine line.
        fiber = Counter()
        fiber_by_type: dict[str, Counter[str]] = {}
        for elem in candidates:
            elem_fps = _fixed_points(elem, points)
            line_key = str(elem_fps)
            fiber[line_key] += 1
            ltype = analyze._line_equation_type(tuple(elem_fps))[0]
            fiber_by_type.setdefault(str(ltype), Counter())[line_key] += 1

        fixed_line_fiber_hist = {str(k): int(v) for k, v in sorted(fiber.items())}
        fixed_line_type_fiber_hist = {
            str(ltype): {str(k): int(v) for k, v in sorted(counter.items())}
            for ltype, counter in sorted(fiber_by_type.items())
        }

        # Reflection parameterization across the full candidate set.
        for elem in candidates:
            elem_fps = _fixed_points(elem, points)
            axis_key = str(elem_fps)
            try:
                axis_type = str(analyze._line_equation_type(tuple(elem_fps))[0])
            except Exception as exc:
                reflection_failures.append(
                    {
                        "affine_elem": [list(elem[0]), list(elem[1])],
                        "why": f"axis_type_error: {exc}",
                    }
                )
                continue
            axis_line_to_types[axis_key] = axis_type

            elem_fixed_lines = _fixed_lines(elem, lines)
            fixed_line_type_hist = Counter(
                str(analyze._line_equation_type(L)[0]) for L in elem_fixed_lines
            )
            striation_types = [
                t for t, count in fixed_line_type_hist.items() if int(count) == 3
            ]
            axis_count = int(fixed_line_type_hist.get(axis_type, 0))
            if (
                len(elem_fps) != 3
                or len(elem_fixed_lines) != 4
                or axis_count != 1
                or len(striation_types) != 1
            ):
                reflection_failures.append(
                    {
                        "affine_elem": [list(elem[0]), list(elem[1])],
                        "fixed_points_count": int(len(elem_fps)),
                        "fixed_lines_count": int(len(elem_fixed_lines)),
                        "fixed_line_type_histogram": {
                            str(k): int(v)
                            for k, v in sorted(fixed_line_type_hist.items())
                        },
                    }
                )
                continue

            fixed_striation_type = str(striation_types[0])
            axis_type_hist[axis_type] += 1
            fixed_striation_type_hist[fixed_striation_type] += 1
            axis_type_vs_fixed_striation_type[(axis_type, fixed_striation_type)] += 1
            axis_line_to_striations[axis_key].add(fixed_striation_type)
            axis_line_and_striation_pairs[(axis_key, fixed_striation_type)] += 1

    class_size = class_sizes[0] if class_sizes else 0
    centralizer_size = len(centralizer)
    d12_fingerprint = {
        "size": 12,
        "order_histogram": {"1": 1, "2": 7, "3": 2, "6": 2},
    }
    d12_match = bool(
        centralizer_size == d12_fingerprint["size"]
        and centralizer_order_hist == d12_fingerprint["order_histogram"]
    )

    fixed_line_fiber_values = list(fixed_line_fiber_hist.values())
    fixed_line_fiber_is_uniform_three = bool(
        fixed_line_fiber_values and set(fixed_line_fiber_values) == {3}
    )

    all_line_types = {"x", "y", "y=1x", "y=2x"}
    axis_line_striation_expected = {
        axis: sorted(list(all_line_types - {axis_type}))
        for axis, axis_type in axis_line_to_types.items()
    }
    axis_line_striation_observed = {
        axis: sorted(list(types))
        for axis, types in sorted(axis_line_to_striations.items())
    }
    axis_line_striation_bijection = bool(
        axis_line_striation_observed
        and axis_line_striation_observed == axis_line_striation_expected
        and all(v == 1 for v in axis_line_and_striation_pairs.values())
        and len(axis_line_and_striation_pairs) == 36
    )

    claim_checks = {
        "candidate_count_is_36": bool(len(candidates) == 36),
        "candidate_conjugacy_class_count_is_1": bool(len(classes) == 1),
        "class_size_is_36": bool(class_size == 36),
        "centralizer_size_is_12": bool(centralizer_size == 12),
        "centralizer_matches_d12_order_fingerprint": bool(d12_match),
        "rep_point_cycle_signature_matches_reflection": bool(
            rep_point_cycle_sig == [1, 1, 1, 2, 2, 2]
        ),
        "rep_line_cycle_signature_matches_reflection": bool(
            rep_line_cycle_sig == [1, 1, 1, 1, 2, 2, 2, 2]
        ),
        "rep_fixed_point_count_is_3": bool(len(rep_fixed_points) == 3),
        "rep_fixed_line_count_is_4": bool(len(rep_fixed_lines) == 4),
        "fixed_point_line_fiber_is_uniform_three": bool(
            fixed_line_fiber_is_uniform_three
        ),
        "fixed_point_line_count_is_12": bool(len(fixed_line_fiber_hist) == 12),
        "det2_involutions_reflection_parameterization_holds": bool(
            not reflection_failures and axis_line_striation_bijection
        ),
    }

    return {
        "status": "ok",
        "generated_utc": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "group": {
            "agl23_size": int(len(agl)),
            "gl2_3_size": int(len(mats)),
        },
        "det2_involutions": {
            "candidate_count": int(len(candidates)),
            "conjugacy_class_count": int(len(classes)),
            "class_sizes": class_sizes,
            "representative": {
                "affine_elem": (
                    [list(rep[0]), list(rep[1])] if rep is not None else None
                ),
                "fixed_points": rep_fixed_points,
                "fixed_lines": rep_fixed_lines,
                "fixed_line_type_histogram": rep_fixed_line_type_hist,
                "point_cycle_signature": rep_point_cycle_sig,
                "line_cycle_signature": rep_line_cycle_sig,
            },
            "centralizer": {
                "size": int(centralizer_size),
                "order_histogram": centralizer_order_hist,
                "d12_order_fingerprint": d12_fingerprint,
                "matches_d12_fingerprint": bool(d12_match),
            },
            "fixed_point_line_fiber": {
                "line_key_to_count": fixed_line_fiber_hist,
                "uniform_count_is_three": bool(fixed_line_fiber_is_uniform_three),
                "distinct_fixed_lines": int(len(fixed_line_fiber_hist)),
                "by_line_type": fixed_line_type_fiber_hist,
            },
            "reflection_parameterization": {
                "axis_line_count": int(len(axis_line_to_types)),
                "axis_type_histogram": {
                    str(k): int(v) for k, v in sorted(axis_type_hist.items())
                },
                "fixed_striation_type_histogram": {
                    str(k): int(v) for k, v in sorted(fixed_striation_type_hist.items())
                },
                "axis_type_vs_fixed_striation_type": {
                    str([k[0], k[1]]): int(v)
                    for k, v in sorted(axis_type_vs_fixed_striation_type.items())
                },
                "axis_line_to_fixed_striation_types": axis_line_striation_observed,
            },
        },
        "claim_checks": claim_checks,
        "claim": (
            "AGL(2,3) contains exactly 36 det=2 involutions (order 2) forming a single "
            "conjugacy class; a representative has point/line cycle signatures "
            "[1,1,1,2,2,2] and [1,1,1,1,2,2,2,2], fixes 3 points (an affine line) and "
            "4 affine lines, and has a centralizer with the D12 order fingerprint. "
            "Moreover, each det=2 involution is uniquely parameterized by its fixed-point "
            "axis line together with the choice of which of the other three line-directions "
            "is fixed as an entire striation (axis+striation gives 12*3=36)."
        ),
        "claim_holds": bool(all(claim_checks.values())),
    }


def render_md(report: dict[str, Any]) -> str:
    inv = report["det2_involutions"]
    rep = inv["representative"]
    cent = inv["centralizer"]
    fiber = inv["fixed_point_line_fiber"]
    refl = inv["reflection_parameterization"]

    lines: list[str] = []
    lines.append("# AGL(2,3) det=2 Involution Class (2026-02-11)")
    lines.append("")
    lines.append(f"- AGL size: `{report['group']['agl23_size']}`")
    lines.append(f"- det=2 involution count: `{inv['candidate_count']}`")
    lines.append(f"- conjugacy class count: `{inv['conjugacy_class_count']}`")
    lines.append(f"- class sizes: `{inv['class_sizes']}`")
    lines.append(f"- claim holds: `{report['claim_holds']}`")
    lines.append("")
    lines.append("## Representative")
    lines.append("")
    lines.append(f"- affine elem: `{rep['affine_elem']}`")
    lines.append(f"- fixed points: `{rep['fixed_points']}`")
    lines.append(f"- fixed lines: `{rep['fixed_lines']}`")
    lines.append(f"- fixed line types: `{rep['fixed_line_type_histogram']}`")
    lines.append(f"- point cycle signature: `{rep['point_cycle_signature']}`")
    lines.append(f"- line cycle signature: `{rep['line_cycle_signature']}`")
    lines.append("")
    lines.append("## Centralizer")
    lines.append("")
    lines.append(f"- size: `{cent['size']}`")
    lines.append(f"- order histogram: `{cent['order_histogram']}`")
    lines.append(f"- matches D12 fingerprint: `{cent['matches_d12_fingerprint']}`")
    lines.append("")
    lines.append("## Fixed-Line Fiber")
    lines.append("")
    lines.append(f"- distinct fixed lines: `{fiber['distinct_fixed_lines']}`")
    lines.append(f"- uniform fiber size is 3: `{fiber['uniform_count_is_three']}`")
    lines.append(f"- by line type: `{fiber['by_line_type']}`")
    lines.append("")
    lines.append("## Reflection Parameterization")
    lines.append("")
    lines.append(f"- axis line count: `{refl['axis_line_count']}`")
    lines.append(f"- axis type histogram: `{refl['axis_type_histogram']}`")
    lines.append(
        "- fixed striation type histogram: "
        f"`{refl['fixed_striation_type_histogram']}`"
    )
    lines.append(
        "- axis type vs fixed striation type: "
        f"`{refl['axis_type_vs_fixed_striation_type']}`"
    )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "agl23_det2_involution_class_2026_02_11.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "docs" / "AGL23_DET2_INVOLUTION_CLASS_2026_02_11.md",
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
