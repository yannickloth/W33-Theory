#!/usr/bin/env python3
"""
Analyze symmetry breaking induced by the E6 F3 trilinear sign layer.

Input:
  - artifacts/e6_f3_trilinear_map.json

This script studies affine-plane symmetries on u in F3^2:
  u -> A u + b, with A in GL(2,3) or SL(2,3), b in F3^2.

It reports stabilizers for:
  1) the line support (12 affine lines),
  2) the full sign field s(line,z) on affine-line triads,
  3) the line product P(line) = prod_{z in Z3} s(line,z).

Outputs:
  - artifacts/e6_f3_trilinear_symmetry_breaking.json
  - artifacts/e6_f3_trilinear_symmetry_breaking.md
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import product
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def _line_key(line: list[list[int]]) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
    pts = sorted((int(p[0]), int(p[1])) for p in line)
    if len(pts) != 3:
        raise ValueError("line must have 3 points")
    return (pts[0], pts[1], pts[2])


def _line_equation_type(
    line: tuple[tuple[int, int], tuple[int, int], tuple[int, int]]
) -> tuple[str, int]:
    xs = {p[0] for p in line}
    ys = {p[1] for p in line}
    if len(xs) == 1:
        return ("x", next(iter(xs)))
    if len(ys) == 1:
        return ("y", next(iter(ys)))
    for m in (1, 2):
        cs = {(y - m * x) % 3 for x, y in line}
        if len(cs) == 1:
            return (f"y={m}x", next(iter(cs)))
    raise RuntimeError(f"Could not classify line {line}")


def _normalized_line_abc(
    line: tuple[tuple[int, int], tuple[int, int], tuple[int, int]]
) -> tuple[int, int, int]:
    """
    Return normalized (a,b,c) for a*x + b*y = c over F3,
    scaling so the first nonzero coefficient in (a,b) is 1.
    """
    eq_type, intercept = _line_equation_type(line)
    if eq_type == "x":
        return (1, 0, intercept)
    if eq_type == "y":
        return (0, 1, intercept)
    if eq_type == "y=1x":
        # y = x + c  ->  -x + y = c
        a, b, c = (2, 1, intercept)
    elif eq_type == "y=2x":
        # y = 2x + c  ->  -2x + y = c
        a, b, c = (1, 1, intercept)
    else:
        raise RuntimeError(f"Unexpected line equation type: {eq_type}")

    if a != 0:
        inv = 1 if a == 1 else 2
    else:
        inv = 1 if b == 1 else 2
    return ((a * inv) % 3, (b * inv) % 3, (c * inv) % 3)


def _all_affine_lines() -> list[tuple[tuple[int, int], tuple[int, int], tuple[int, int]]]:
    pts = [(x, y) for x in range(3) for y in range(3)]
    lines = set()
    normals = [(1, 0), (0, 1), (1, 1), (1, 2)]
    for a, b in normals:
        for c in range(3):
            line = tuple(sorted((x, y) for x, y in pts if (a * x + b * y - c) % 3 == 0))
            lines.add(line)
    out = sorted(lines)
    if len(out) != 12:
        raise RuntimeError(f"Expected 12 affine lines, got {len(out)}")
    return out


def _gl2_3() -> list[tuple[int, int, int, int, int]]:
    mats = []
    for a, b, c, d in product(range(3), repeat=4):
        det = (a * d - b * c) % 3
        if det != 0:
            mats.append((a, b, c, d, det))
    return mats


def _sl2_3() -> list[tuple[int, int, int, int, int]]:
    return [m for m in _gl2_3() if m[4] == 1]


def _map_point(
    A: tuple[int, int, int, int, int], shift: tuple[int, int], p: tuple[int, int]
) -> tuple[int, int]:
    a, b, c, d, _det = A
    x, y = p
    return ((a * x + b * y + shift[0]) % 3, (c * x + d * y + shift[1]) % 3)


def _map_line(
    A: tuple[int, int, int, int, int],
    shift: tuple[int, int],
    line: tuple[tuple[int, int], tuple[int, int], tuple[int, int]],
) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
    return tuple(sorted(_map_point(A, shift, p) for p in line))


def _map_z(z_map: tuple[int, int], z: int) -> int:
    az, bz = z_map
    return (az * z + bz) % 3


def _load_sign_field(
    path: Path,
) -> tuple[
    list[tuple[tuple[int, int], tuple[int, int], tuple[int, int]]],
    dict[tuple[tuple[tuple[int, int], tuple[int, int], tuple[int, int]], int], int],
]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("affine_u_line_slices")
    if not isinstance(rows, list):
        raise RuntimeError("Missing affine_u_line_slices")

    lines = []
    sign_field: dict[
        tuple[tuple[tuple[int, int], tuple[int, int], tuple[int, int]], int], int
    ] = {}
    for row in rows:
        line = _line_key(row["u_line"])
        lines.append(line)
        for entry in row["entries"]:
            z = int(entry["z_profile_over_u_line"][0])
            sign = int(entry["sign_pm1"])
            sign_field[(line, z)] = sign
    lines = sorted(set(lines))
    return lines, sign_field


def _stabilizer_support_size(
    lines: set[tuple[tuple[int, int], tuple[int, int], tuple[int, int]]],
    mats: list[tuple[int, int, int, int, int]],
) -> int:
    pts = [(x, y) for x in range(3) for y in range(3)]
    count = 0
    for A in mats:
        for b in pts:
            image = {_map_line(A, b, L) for L in lines}
            if image == lines:
                count += 1
    return count


def _stabilizer_full_sign_size(
    lines: list[tuple[tuple[int, int], tuple[int, int], tuple[int, int]],
    ],
    sign_field: dict[
        tuple[tuple[tuple[int, int], tuple[int, int], tuple[int, int]], int], int
    ],
    mats: list[tuple[int, int, int, int, int]],
) -> tuple[int, dict[str, int]]:
    pts = [(x, y) for x in range(3) for y in range(3)]
    z_maps = [(az, bz) for az in (1, 2) for bz in range(3)]
    kept = 0
    by_z_eps: Counter[str] = Counter()

    for A in mats:
        for b in pts:
            line_map = {L: _map_line(A, b, L) for L in lines}
            if set(line_map.values()) != set(lines):
                continue
            for z_map in z_maps:
                for eps in (1, -1):
                    ok = True
                    for L in lines:
                        L2 = line_map[L]
                        for z in (0, 1, 2):
                            if sign_field[(L2, _map_z(z_map, z))] != eps * sign_field[
                                (L, z)
                            ]:
                                ok = False
                                break
                        if not ok:
                            break
                    if ok:
                        kept += 1
                        by_z_eps[f"z_map={z_map},eps={eps}"] += 1
    return kept, dict(by_z_eps)


def _line_product_signs(
    lines: list[tuple[tuple[int, int], tuple[int, int], tuple[int, int]],
    ],
    sign_field: dict[
        tuple[tuple[tuple[int, int], tuple[int, int], tuple[int, int]], int], int
    ],
) -> dict[tuple[tuple[int, int], tuple[int, int], tuple[int, int]], int]:
    out = {}
    for L in lines:
        out[L] = int(sign_field[(L, 0)] * sign_field[(L, 1)] * sign_field[(L, 2)])
    return out


def _line_product_closed_form_check(
    line_product: dict[tuple[tuple[int, int], tuple[int, int], tuple[int, int]], int]
) -> dict[str, Any]:
    """
    Empirical closed form in the current gauge:
      P(line) = +1  iff  b*(a+b+c) == 0 (mod 3),
    with normalized line equation a*x + b*y = c.
    """
    rows = []
    mismatches = []
    for line, sign in sorted(line_product.items()):
        a, b, c = _normalized_line_abc(line)
        expr = (b * (a + b + c)) % 3
        pred = 1 if expr == 0 else -1
        row = {
            "line": [[int(p[0]), int(p[1])] for p in line],
            "abc": [int(a), int(b), int(c)],
            "expr_mod3": int(expr),
            "sign_product": int(sign),
            "predicted_sign_product": int(pred),
        }
        rows.append(row)
        if pred != sign:
            mismatches.append(row)
    return {
        "rule": "P(line)=+1 iff b*(a+b+c)==0 mod 3 (normalized a*x+b*y=c)",
        "holds": len(mismatches) == 0,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "rows": rows,
    }


def _stabilizer_line_product_size(
    lines: list[tuple[tuple[int, int], tuple[int, int], tuple[int, int]],
    ],
    product_sign: dict[tuple[tuple[int, int], tuple[int, int], tuple[int, int]], int],
    mats: list[tuple[int, int, int, int, int]],
) -> tuple[int, dict[str, int], dict[str, int]]:
    pts = [(x, y) for x in range(3) for y in range(3)]
    kept = 0
    det_hist: Counter[str] = Counter()
    eq_hist: Counter[str] = Counter()
    for A in mats:
        for b in pts:
            ok = True
            for L in lines:
                L2 = _map_line(A, b, L)
                if L2 not in product_sign or product_sign[L2] != product_sign[L]:
                    ok = False
                    break
            if ok:
                kept += 1
                det_hist[str(A[4])] += 1
                for L in lines:
                    eq_hist[str(_line_equation_type(_map_line(A, b, L))[0])] += 1
    return kept, dict(det_hist), dict(eq_hist)


def _build_md(out: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# E6 F3 trilinear symmetry breaking")
    lines.append("")
    lines.append("- Input: `{}`".format(out["input"]))
    lines.append("- Support lines: `{}`".format(out["counts"]["lines"]))
    lines.append("")
    lines.append("## Stabilizer sizes")
    lines.append(
        "- Support under `AGL(2,3)` (`|GL(2,3)|*9 = 432`): `{}`".format(
            out["stabilizers"]["support"]["agl23_size"]
        )
    )
    lines.append(
        "- Support under `F3^2 ⋊ SL(2,3)` (`216`): `{}`".format(
            out["stabilizers"]["support"]["hessian216_size"]
        )
    )
    lines.append(
        "- Full sign field under `(u-affine) x (z-affine) x {{global sign}}` in Hessian216: `{}`".format(
            out["stabilizers"]["full_sign"]["hessian216_with_z_affine_global_sign"]
        )
    )
    lines.append(
        "- Product sign `P(line)=prod_z s(line,z)` under `AGL(2,3)`: `{}`".format(
            out["stabilizers"]["line_product"]["agl23_size"]
        )
    )
    lines.append(
        "- Product sign `P(line)=prod_z s(line,z)` under Hessian216: `{}`".format(
            out["stabilizers"]["line_product"]["hessian216_size"]
        )
    )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("- The affine-line support retains full affine symmetry.")
    lines.append("- The full sign layer has trivial stabilizer in this gauge (identity only).")
    lines.append("- The line-product layer keeps a small residual subgroup.")
    lines.append("")
    lines.append("## Closed-form product law")
    lines.append(
        "- Rule `{}` holds: `{}`".format(
            out["cross_checks"]["line_product_closed_form"]["rule"],
            out["cross_checks"]["line_product_closed_form"]["holds"],
        )
    )
    lines.append("")
    lines.append("## Source pointers")
    lines.append("- Hesse configuration and Hessian group context: Artebani-Dolgachev (2006), arXiv:math/0611590.")
    lines.append("- 27 lines, tritangents, and E6 cubic context: Manivel (2007), EMS Surveys in Mathematical Sciences.")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--in-json",
        type=Path,
        default=ROOT / "artifacts" / "e6_f3_trilinear_map.json",
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "e6_f3_trilinear_symmetry_breaking.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "artifacts" / "e6_f3_trilinear_symmetry_breaking.md",
    )
    args = parser.parse_args()

    lines, sign_field = _load_sign_field(args.in_json)
    expected_lines = _all_affine_lines()
    if set(lines) != set(expected_lines):
        raise RuntimeError("Input affine_u_line_slices do not match AG(2,3) lines")

    gl = _gl2_3()
    sl = _sl2_3()

    support_agl = _stabilizer_support_size(set(lines), gl)
    support_hessian = _stabilizer_support_size(set(lines), sl)

    full_hessian, full_hessian_breakdown = _stabilizer_full_sign_size(lines, sign_field, sl)
    full_agl, full_agl_breakdown = _stabilizer_full_sign_size(lines, sign_field, gl)

    product_sign = _line_product_signs(lines, sign_field)
    closed_form = _line_product_closed_form_check(product_sign)
    prod_agl, prod_agl_det_hist, prod_agl_eq_hist = _stabilizer_line_product_size(
        lines, product_sign, gl
    )
    prod_hessian, prod_hessian_det_hist, prod_hessian_eq_hist = _stabilizer_line_product_size(
        lines, product_sign, sl
    )

    out = {
        "status": "ok",
        "input": str(args.in_json),
        "counts": {
            "lines": len(lines),
            "sign_values": len(sign_field),
            "gl23_size": len(gl),
            "sl23_size": len(sl),
            "agl23_size": len(gl) * 9,
            "hessian216_size": len(sl) * 9,
        },
        "stabilizers": {
            "support": {
                "agl23_size": int(support_agl),
                "hessian216_size": int(support_hessian),
            },
            "full_sign": {
                "agl23_with_z_affine_global_sign": int(full_agl),
                "hessian216_with_z_affine_global_sign": int(full_hessian),
                "agl23_breakdown": full_agl_breakdown,
                "hessian216_breakdown": full_hessian_breakdown,
            },
            "line_product": {
                "agl23_size": int(prod_agl),
                "hessian216_size": int(prod_hessian),
                "agl23_det_hist": prod_agl_det_hist,
                "hessian216_det_hist": prod_hessian_det_hist,
                "agl23_image_equation_type_hist": prod_agl_eq_hist,
                "hessian216_image_equation_type_hist": prod_hessian_eq_hist,
            },
        },
        "cross_checks": {
            "line_product_closed_form": closed_form,
        },
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    args.out_md.write_text(_build_md(out), encoding="utf-8")

    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
