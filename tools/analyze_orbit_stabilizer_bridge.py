#!/usr/bin/env python3
"""Analyze orbit-stabilizer structure for minimal-certificate representatives.

Bridges:
- group action size `|AGL(2,3)| * |Aff(Z3)| = 432 * 6 = 2592`,
- observed orbit sizes (`1296`, `2592`),
- reduced-orbit involution signatures from GL(2,3).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Iterable, TypeVar

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze

T = TypeVar("T")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonicalize_witnesses(
    witnesses: list[dict[str, Any]],
) -> tuple[tuple[Any, ...], ...]:
    out = []
    for witness in witnesses:
        mapped_pts = tuple(sorted(tuple(p) for p in witness.get("line", [])))
        line_type = witness.get("line_type", analyze._line_equation_type(mapped_pts)[0])
        out.append(
            (
                mapped_pts,
                int(witness.get("z", 0)),
                int(witness.get("sign_pm1", 1)),
                str(line_type),
            )
        )
    return tuple(sorted(out))


def _act_on_witnesses(
    witnesses: list[dict[str, Any]],
    affine_elem: tuple[tuple[int, int, int, int, int], tuple[int, int]],
    z_map: tuple[int, int],
) -> tuple[tuple[Any, ...], ...]:
    mat, shift = affine_elem
    out = []
    for witness in witnesses:
        mapped_pts = tuple(
            sorted(
                analyze._map_point(mat, shift, tuple(point))
                for point in witness.get("line", [])
            )
        )
        line_type = analyze._line_equation_type(mapped_pts)[0]
        out.append(
            (
                mapped_pts,
                int(analyze._map_z(z_map, int(witness.get("z", 0)))),
                int(witness.get("sign_pm1", 1)),
                str(line_type),
            )
        )
    return tuple(sorted(out))


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


def _build_space_report(
    space_name: str,
    classified_json: Path,
    affine_elements: list[tuple[tuple[int, int, int, int, int], tuple[int, int]]],
    z_maps: list[tuple[int, int]],
    points: list[tuple[int, int]],
    lines: list[tuple[tuple[int, int], tuple[int, int], tuple[int, int]]],
) -> dict[str, Any]:
    payload = _load_json(classified_json)
    representatives = list(payload.get("representatives", []))
    action_size = len(affine_elements) * len(z_maps)

    orbit_hist: Counter[int] = Counter()
    stab_hist: Counter[int] = Counter()
    nontrivial_rows: list[dict[str, Any]] = []
    orbit_stabilizer_rows: list[dict[str, Any]] = []

    for rec in representatives:
        rep = list(rec.get("canonical_orbit_rep", []))
        canonical = _canonicalize_witnesses(rep)
        stabilizer_elements: list[
            tuple[
                tuple[tuple[int, int, int, int, int], tuple[int, int]], tuple[int, int]
            ]
        ] = []

        for affine_elem in affine_elements:
            for z_map in z_maps:
                if _act_on_witnesses(rep, affine_elem, z_map) == canonical:
                    stabilizer_elements.append((affine_elem, z_map))

        orbit_size = int(rec.get("orbit_size", 0))
        stab_size = len(stabilizer_elements)
        orbit_hist[orbit_size] += 1
        stab_hist[stab_size] += 1

        orbit_stabilizer_rows.append(
            {
                "orbit_size": orbit_size,
                "stabilizer_size": int(stab_size),
                "orbit_times_stabilizer": int(orbit_size * stab_size),
                "matches_action_size": bool(orbit_size * stab_size == action_size),
            }
        )

        if stab_size > 1:
            non_identity = None
            for mat_shift, z_map in stabilizer_elements:
                mat, shift = mat_shift
                if mat == (1, 0, 0, 1, 1) and shift == (0, 0) and z_map == (1, 0):
                    continue
                non_identity = (mat, shift, z_map)
                break

            if non_identity is None:
                continue

            mat, shift, z_map = non_identity
            point_sig = _cycle_signature(
                points,
                lambda p: analyze._map_point(mat, (0, 0), p),
            )
            line_sig = _cycle_signature(
                lines,
                lambda l: analyze._map_line(mat, (0, 0), l),
            )
            nontrivial_rows.append(
                {
                    "orbit_size": orbit_size,
                    "linear_matrix": list(mat),
                    "shift": list(shift),
                    "z_map": list(z_map),
                    "linear_det": int(mat[4]),
                    "linear_order": int(analyze._affine_order((mat, (0, 0)))),
                    "point_cycle_signature": point_sig,
                    "line_cycle_signature": line_sig,
                }
            )

    z_map_hist = Counter(tuple(row["z_map"]) for row in nontrivial_rows)
    det_hist = Counter(int(row["linear_det"]) for row in nontrivial_rows)
    order_hist = Counter(int(row["linear_order"]) for row in nontrivial_rows)
    point_sig_set = sorted(
        {tuple(row["point_cycle_signature"]) for row in nontrivial_rows}
    )
    line_sig_set = sorted(
        {tuple(row["line_cycle_signature"]) for row in nontrivial_rows}
    )

    return {
        "candidate_space": space_name,
        "source_json": str(classified_json),
        "action_size": int(action_size),
        "representative_count": int(len(representatives)),
        "orbit_size_histogram": {str(k): int(v) for k, v in sorted(orbit_hist.items())},
        "stabilizer_size_histogram": {
            str(k): int(v) for k, v in sorted(stab_hist.items())
        },
        "orbit_stabilizer_identity_holds": all(
            row["matches_action_size"] for row in orbit_stabilizer_rows
        ),
        "nontrivial_stabilizer_representative_count": int(len(nontrivial_rows)),
        "nontrivial_stabilizer_examples": nontrivial_rows,
        "nontrivial_profiles": {
            "z_map_histogram": {
                str(list(k)): int(v) for k, v in sorted(z_map_hist.items())
            },
            "linear_det_histogram": {
                str(k): int(v) for k, v in sorted(det_hist.items())
            },
            "linear_order_histogram": {
                str(k): int(v) for k, v in sorted(order_hist.items())
            },
            "unique_point_cycle_signatures": [list(sig) for sig in point_sig_set],
            "unique_line_cycle_signatures": [list(sig) for sig in line_sig_set],
        },
    }


def build_report(
    hessian_json: Path,
    agl_json: Path,
    hessian_exhaustive_json: Path | None = None,
) -> dict[str, Any]:
    points = [(x, y) for x in range(3) for y in range(3)]
    z_maps = [(az, bz) for az in (1, 2) for bz in range(3)]
    affine_elements = [(mat, shift) for mat in analyze._gl2_3() for shift in points]
    lines = list(analyze._all_affine_lines())

    hessian = _build_space_report(
        "hessian",
        hessian_json,
        affine_elements,
        z_maps,
        points,
        lines,
    )
    agl = _build_space_report(
        "agl",
        agl_json,
        affine_elements,
        z_maps,
        points,
        lines,
    )

    hessian_exhaustive = None
    if hessian_exhaustive_json is not None and hessian_exhaustive_json.exists():
        hessian_exhaustive = _build_space_report(
            "hessian_exhaustive",
            hessian_exhaustive_json,
            affine_elements,
            z_maps,
            points,
            lines,
        )

    hessian_nontrivial = hessian["nontrivial_stabilizer_representative_count"]
    agl_nontrivial = agl["nontrivial_stabilizer_representative_count"]
    hessian_profiles = hessian.get("nontrivial_profiles", {})

    claim_checks = {
        "orbit_stabilizer_identity_holds_all_spaces": bool(
            hessian["orbit_stabilizer_identity_holds"]
            and agl["orbit_stabilizer_identity_holds"]
        ),
        "hessian_reduced_orbits_have_stabilizer_2": bool(
            hessian.get("orbit_size_histogram", {}).get("1296", 0)
            == hessian.get("stabilizer_size_histogram", {}).get("2", 0)
            and hessian.get("orbit_size_histogram", {}).get("1296", 0) > 0
        ),
        "full_orbits_have_stabilizer_1": bool(
            hessian.get("orbit_size_histogram", {}).get("2592", 0)
            == hessian.get("stabilizer_size_histogram", {}).get("1", 0)
            and agl.get("orbit_size_histogram", {}).get("2592", 0)
            == agl.get("stabilizer_size_histogram", {}).get("1", 0)
        ),
        "nontrivial_stabilizers_only_in_hessian": bool(
            hessian_nontrivial > 0 and agl_nontrivial == 0
        ),
        "all_hessian_nontrivial_linear_parts_are_det2_order2": bool(
            hessian_profiles.get("linear_det_histogram", {}).keys() == {"2"}
            and hessian_profiles.get("linear_order_histogram", {}).keys() == {"2"}
        ),
        "hessian_nontrivial_cycle_signatures_match_gl2_bridge": bool(
            hessian_profiles.get("unique_point_cycle_signatures", [])
            == [[1, 1, 1, 2, 2, 2]]
            and hessian_profiles.get("unique_line_cycle_signatures", [])
            == [[1, 1, 1, 1, 2, 2, 2, 2]]
        ),
    }
    if hessian_exhaustive is not None:
        ex_profiles = hessian_exhaustive.get("nontrivial_profiles", {})
        z_keys = set(ex_profiles.get("z_map_histogram", {}).keys())
        claim_checks["hessian_exhaustive_zmap_support_is_exact_three_involutions"] = (
            bool(z_keys == {"[1, 0]", "[2, 0]", "[2, 1]"})
        )

    spaces: dict[str, Any] = {
        "hessian": hessian,
        "agl": agl,
    }
    if hessian_exhaustive is not None:
        spaces["hessian_exhaustive"] = hessian_exhaustive

    return {
        "status": "ok",
        "generated_utc": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "action_model": {
            "agl23_size": 432,
            "z_affine_size": 6,
            "total_action_size": 2592,
            "notes": "Action on witness sets via affine map on AG(2,3) and affine map on z.",
        },
        "spaces": spaces,
        "claim_checks": claim_checks,
        "claim": (
            "In exact min-cert representative data, orbit-size splitting is exactly an "
            "orbit-stabilizer splitting: full orbits have trivial stabilizer, while reduced "
            "orbits are halved by a unique nontrivial det=2/order-2 symmetry with the same "
            "GL(2,3) point/line cycle signature."
        ),
        "claim_holds": bool(all(claim_checks.values())),
    }


def render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Orbit-Stabilizer Bridge (2026-02-11)")
    lines.append("")
    action = report.get("action_model", {})
    lines.append(
        "- action size: `{}` (`AGL(2,3)={}`, `z-affine={}`)".format(
            action.get("total_action_size"),
            action.get("agl23_size"),
            action.get("z_affine_size"),
        )
    )
    lines.append(f"- claim holds: `{report.get('claim_holds')}`")
    lines.append("")

    for key in ("hessian", "agl", "hessian_exhaustive"):
        if key not in report.get("spaces", {}):
            continue
        space = report.get("spaces", {}).get(key, {})
        lines.append(f"## {key}")
        lines.append("")
        lines.append(f"- source: `{space.get('source_json')}`")
        lines.append(f"- representatives: `{space.get('representative_count')}`")
        lines.append(f"- orbit histogram: `{space.get('orbit_size_histogram', {})}`")
        lines.append(
            f"- stabilizer histogram: `{space.get('stabilizer_size_histogram', {})}`"
        )
        lines.append(
            "- orbit-stabilizer identity holds: "
            f"`{space.get('orbit_stabilizer_identity_holds')}`"
        )
        lines.append(
            "- nontrivial stabilizer reps: "
            f"`{space.get('nontrivial_stabilizer_representative_count')}`"
        )
        profiles = space.get("nontrivial_profiles", {})
        if profiles:
            lines.append(
                f"- nontrivial z-map histogram: `{profiles.get('z_map_histogram', {})}`"
            )
            lines.append(
                "- nontrivial linear det/order hist: "
                f"`det={profiles.get('linear_det_histogram', {})}, "
                f"order={profiles.get('linear_order_histogram', {})}`"
            )
            lines.append(
                "- nontrivial point signatures: "
                f"`{profiles.get('unique_point_cycle_signatures', [])}`"
            )
            lines.append(
                "- nontrivial line signatures: "
                f"`{profiles.get('unique_line_cycle_signatures', [])}`"
            )
        lines.append("")

    lines.append("## Claim Checks")
    lines.append("")
    for key, value in report.get("claim_checks", {}).items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--hessian-json",
        type=Path,
        default=ROOT
        / "artifacts"
        / "e6_f3_trilinear_min_cert_exact_hessian_full_with_geotypes.json",
    )
    parser.add_argument(
        "--agl-json",
        type=Path,
        default=ROOT
        / "artifacts"
        / "e6_f3_trilinear_min_cert_exact_agl_full_with_geotypes.json",
    )
    parser.add_argument(
        "--hessian-exhaustive-json",
        type=Path,
        default=ROOT
        / "artifacts"
        / "e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2_with_geotypes.json",
        help="Optional exhaustive Hessian representative file for stronger z-map support checks.",
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "orbit_stabilizer_bridge_2026_02_11.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "docs" / "ORBIT_STABILIZER_BRIDGE_2026_02_11.md",
    )
    args = parser.parse_args()

    report = build_report(
        hessian_json=args.hessian_json,
        agl_json=args.agl_json,
        hessian_exhaustive_json=args.hessian_exhaustive_json,
    )
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_md(report), encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
