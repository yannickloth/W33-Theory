#!/usr/bin/env python3
"""
Build a concrete "interaction dictionary" for the firewall quotient geometry:

  - 9 firewall bad triads (points of AG(2,3))
  - 12 affine lines on those 9 points
  - 36 allowed triads = 12 lines × 3 Z3 lifts
  - 36↔36 duality: each affine line also indexes 3 double-sixes (Z3 lifts)

This script annotates:
  - each bad-triad block with its SM field triple (and coupling counts)
  - each affine line with:
      * the 3 allowed triads (lifts) + their SM field triples
      * per-line coupling totals from the 3-generation coupling atlas (3×3→3̄)
      * the 3 double-sixes (lifts) and the SM field multiset on A∪B

Inputs:
  - artifacts/toe_affine_plane_duality.json
  - artifacts/toe_sm_decomposition_27.json
  - artifacts/toe_three_generation_coupling_atlas.json

Outputs:
  - artifacts/toe_affine_plane_interaction_dictionary.json
  - artifacts/toe_affine_plane_interaction_dictionary.md
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


Triad = Tuple[int, int, int]


def _triad_key(t: Sequence[int]) -> Triad:
    if len(t) != 3:
        raise ValueError("Expected length-3 triad")
    a, b, c = (int(t[0]), int(t[1]), int(t[2]))
    out = tuple(sorted((a, b, c)))
    if len(set(out)) != 3:
        raise ValueError("Triad must have 3 distinct vertices")
    return out  # type: ignore[return-value]


def main(argv: Sequence[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--duality-json",
        type=Path,
        default=ROOT / "artifacts" / "toe_affine_plane_duality.json",
    )
    p.add_argument(
        "--sm-json",
        type=Path,
        default=ROOT / "artifacts" / "toe_sm_decomposition_27.json",
    )
    p.add_argument(
        "--atlas-json",
        type=Path,
        default=ROOT / "artifacts" / "toe_three_generation_coupling_atlas.json",
    )
    p.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "toe_affine_plane_interaction_dictionary.json",
    )
    p.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "artifacts" / "toe_affine_plane_interaction_dictionary.md",
    )
    args = p.parse_args(list(argv) if argv is not None else None)

    dual = _load_json(args.duality_json)
    sm = _load_json(args.sm_json)
    atlas = _load_json(args.atlas_json)

    # Field labels.
    per_v = sm.get("per_vertex")
    if not isinstance(per_v, list) or len(per_v) != 27:
        raise RuntimeError("Invalid toe_sm_decomposition_27.json: per_vertex")
    field_by: Dict[int, str] = {
        int(r["i"]): str(r["field"]) for r in per_v if isinstance(r, dict)
    }
    if len(field_by) != 27:
        raise RuntimeError("Expected 27 field labels")

    # Coupling atlas: each triad appears 36 times (1620/45).
    recs = atlas.get("records")
    if not isinstance(recs, list):
        raise RuntimeError("Invalid toe_three_generation_coupling_atlas.json: records")
    couplings_by_triad: Dict[Triad, List[Dict[str, object]]] = defaultdict(list)
    for r in recs:
        if not isinstance(r, dict):
            continue
        t = _triad_key(r["triad"])
        couplings_by_triad[t].append(r)
    if len(couplings_by_triad) != 45:
        raise RuntimeError(
            f"Expected 45 triads in coupling atlas, got {len(couplings_by_triad)}"
        )
    if set(len(v) for v in couplings_by_triad.values()) != {36}:
        raise RuntimeError(
            "Expected each triad to appear exactly 36 times in coupling atlas"
        )

    # Firewall blocks (bad triads) and affine lines.
    fw = dual.get("firewall", {})
    if not isinstance(fw, dict):
        raise RuntimeError("Invalid toe_affine_plane_duality.json: firewall")
    bad_raw = fw.get("bad_triads")
    if not isinstance(bad_raw, list) or len(bad_raw) != 9:
        raise RuntimeError("Invalid toe_affine_plane_duality.json: firewall.bad_triads")
    bad_triads: List[Triad] = [_triad_key(t) for t in bad_raw]
    bad_triads = sorted(bad_triads)
    if len(set(bad_triads)) != 9:
        raise RuntimeError("Bad triads should be distinct")
    bad_set = set(bad_triads)

    aff = dual.get("affine_plane", {})
    if not isinstance(aff, dict):
        raise RuntimeError("Invalid toe_affine_plane_duality.json: affine_plane")
    lines_raw = aff.get("lines")
    if not isinstance(lines_raw, list) or len(lines_raw) != 12:
        raise RuntimeError("Invalid toe_affine_plane_duality.json: affine_plane.lines")
    affine_lines = [tuple(sorted(int(x) for x in row)) for row in lines_raw]
    if any(len(l) != 3 for l in affine_lines):
        raise RuntimeError("Expected each affine line to be 3 block ids")
    affine_lines = sorted(set(affine_lines))
    if len(affine_lines) != 12:
        raise RuntimeError("Expected 12 distinct affine lines")

    # Map each allowed triad to its line (via duality_by_line).
    dbl = dual.get("duality_by_line")
    if not isinstance(dbl, list) or len(dbl) != 12:
        raise RuntimeError("Invalid toe_affine_plane_duality.json: duality_by_line")

    line_entries = []
    triad_to_line: Dict[Triad, int] = {}
    allowed_triads_all: List[Triad] = []

    for lid, row in enumerate(dbl):
        if not isinstance(row, dict):
            raise RuntimeError("Invalid duality_by_line row")
        line_blocks = tuple(sorted(int(x) for x in row["line_blocks"]))
        if len(line_blocks) != 3:
            raise RuntimeError("Expected 3 line_blocks")
        tri_cycle = [_triad_key(t) for t in row["allowed_triads_cycle"]]
        if len(tri_cycle) != 3:
            raise RuntimeError("Expected 3 allowed triads per line")
        ds_cycle = row.get("double_sixes_cycle")
        if not isinstance(ds_cycle, list) or len(ds_cycle) != 3:
            raise RuntimeError("Expected 3 double-sixes per line")

        for t in tri_cycle:
            if t in bad_set:
                raise RuntimeError(
                    "Allowed triad cycle unexpectedly contains a bad triad"
                )
            if t in triad_to_line:
                raise RuntimeError("Allowed triad appears in multiple lines")
            triad_to_line[t] = int(lid)
            allowed_triads_all.append(t)

        # Block (point) metadata for this line.
        blocks = []
        for b in line_blocks:
            tri = bad_triads[b]
            blocks.append(
                {
                    "block_id": int(b),
                    "triad": list(tri),
                    "fields": sorted([field_by[i] for i in tri]),
                }
            )

        # Allowed triad metadata.
        allowed = []
        per_orbit_pair = Counter()
        per_gen_pair = Counter()
        per_triad_fields = Counter()
        for t in tri_cycle:
            fields = tuple(sorted(field_by[i] for i in t))
            per_triad_fields[fields] += 1
            coupl = couplings_by_triad.get(t, [])
            for r in coupl:
                per_orbit_pair[(int(r["oa"]), int(r["ob"]), int(r["ocbar"]))] += 1
                per_gen_pair[
                    (int(r["gen_a"]), int(r["gen_b"]), int(r["gen_cbar"]))
                ] += 1
            allowed.append(
                {
                    "triad": list(t),
                    "fields": list(fields),
                    "couplings_total": int(len(coupl)),
                    "couplings_by_orbit_pair": [
                        {
                            "oa": a,
                            "ob": b,
                            "ocbar": c,
                            "count": int(per_orbit_pair[(a, b, c)]),
                        }
                        for (a, b, c) in sorted(
                            {
                                (int(r["oa"]), int(r["ob"]), int(r["ocbar"]))
                                for r in coupl
                            }
                        )
                    ],
                }
            )

        # Double-six metadata: field multiset on A∪B.
        double_sixes = []
        for ds in ds_cycle:
            if not isinstance(ds, dict) or "A" not in ds or "B" not in ds:
                raise RuntimeError("Invalid double-six entry")
            A = [int(x) for x in ds["A"]]
            B = [int(x) for x in ds["B"]]
            if len(A) != 6 or len(B) != 6 or len(set(A) | set(B)) != 12:
                raise RuntimeError("Invalid double-six A/B sizes")
            fields = [field_by[i] for i in (A + B)]
            double_sixes.append(
                {
                    "A": A,
                    "B": B,
                    "field_hist": {
                        k: int(v) for k, v in sorted(Counter(fields).items())
                    },
                }
            )

        # Line totals: each triad has 36 couplings, so 3×36=108.
        line_entries.append(
            {
                "line_id": int(lid),
                "line_blocks": list(line_blocks),
                "blocks": blocks,
                "allowed_triads_cycle": allowed,
                "allowed_triad_field_multiset": [
                    {"fields": list(k), "count": int(v)}
                    for k, v in sorted(per_triad_fields.items())
                ],
                "couplings_total": int(
                    sum(len(couplings_by_triad[t]) for t in tri_cycle)
                ),
                "couplings_by_orbit_pair": [
                    {
                        "oa": a,
                        "ob": b,
                        "ocbar": c,
                        "count": int(per_orbit_pair[(a, b, c)]),
                    }
                    for (a, b, c), cnt in sorted(per_orbit_pair.items())
                    if int(cnt) > 0
                ],
                "couplings_by_gen_triplet": [
                    {
                        "gen_a": a,
                        "gen_b": b,
                        "gen_cbar": c,
                        "count": int(per_gen_pair[(a, b, c)]),
                    }
                    for (a, b, c), cnt in sorted(per_gen_pair.items())
                    if int(cnt) > 0
                ],
                "double_sixes_cycle": double_sixes,
                "z3_equivariant_pairing": row.get("z3_equivariant_pairing", []),
            }
        )

    if len(triad_to_line) != 36:
        raise RuntimeError(
            f"Expected 36 allowed triads assigned to lines, got {len(triad_to_line)}"
        )
    if sorted(allowed_triads_all) != sorted(set(allowed_triads_all)):
        raise RuntimeError("Duplicate allowed triads in line assignment")

    # Blocks / points metadata.
    blocks_out = []
    for b, tri in enumerate(bad_triads):
        fields = tuple(sorted(field_by[i] for i in tri))
        coupl = couplings_by_triad.get(tri, [])
        blocks_out.append(
            {
                "block_id": int(b),
                "triad": list(tri),
                "fields": list(fields),
                "couplings_total": int(len(coupl)),
                "couplings_forbidden": int(
                    sum(1 for r in coupl if bool(r.get("forbidden")))
                ),
            }
        )

    # Global type-to-lines map (allowed triads only).
    triad_type_to_lines: Dict[Tuple[str, str, str], List[int]] = defaultdict(list)
    for t, lid in triad_to_line.items():
        fields = tuple(sorted(field_by[i] for i in t))
        triad_type_to_lines[fields].append(int(lid))
    triad_type_summary = [
        {"fields": list(k), "lines": sorted(v), "n_lines": int(len(set(v)))}
        for k, v in sorted(
            triad_type_to_lines.items(), key=lambda kv: (-len(set(kv[1])), kv[0])
        )
    ]

    out: Dict[str, object] = {
        "status": "ok",
        "counts": {
            "blocks": 9,
            "affine_lines": 12,
            "triads_total": 45,
            "triads_forbidden": 9,
            "triads_allowed": 36,
            "couplings_total": int(len(recs)),
            "couplings_per_triad": 36,
            "couplings_per_allowed_line": 108,
        },
        "blocks": blocks_out,
        "lines": line_entries,
        "triad_type_to_lines": triad_type_summary,
    }
    _write_json(args.out_json, out)

    # Markdown report.
    md: List[str] = []
    md.append("# TOE: AG(2,3) Interaction Dictionary")
    md.append("")
    md.append("## Counts")
    for k, v in out["counts"].items():
        md.append(f"- {k}: `{v}`")
    md.append("")
    md.append("## Firewall points (bad triads)")
    for b in blocks_out:
        md.append(f"- P{b['block_id']}: triad {b['triad']} fields {b['fields']}")
    md.append("")
    md.append("## Affine lines (each has 3 allowed triads = Z3 lifts)")
    for row in line_entries:
        md.append(f"### Line L{row['line_id']} blocks={row['line_blocks']}")
        md.append("- point labels:")
        for bb in row["blocks"]:
            md.append(
                f"  - P{bb['block_id']}: fields {bb['fields']} triad {bb['triad']}"
            )
        md.append("- allowed triads (lifts):")
        for trow in row["allowed_triads_cycle"]:
            md.append(f"  - triad {trow['triad']} fields {trow['fields']}")
        md.append(f"- couplings_total: `{row['couplings_total']}`")
        md.append("")
    md.append("## Triad-type to line map (allowed triads only)")
    for row in triad_type_summary:
        md.append(f"- {row['fields']}: lines {row['lines']}")
    md.append("")
    md.append(f"- JSON: `{args.out_json}`")
    _write_md(args.out_md, md)
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
