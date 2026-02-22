#!/usr/bin/env python3
"""
TOE: Compile the firewall coupling mask from the AG(2,3)+Z3 connection.

Goal:
  Produce a *minimal* reproducible object that does not depend on any higher-level
  "coupling atlas" heuristics:

    forbidden triads (9) + allowed triads (36)

  compiled purely from:
    - toe_affine_plane_z3_connection.json  (block coords + Z3 lift laws)
    - toe_affine_plane_duality.json        (block kernel cycles + reference line blocks)

Then, as a consistency check, compare to:
    - toe_three_generation_coupling_atlas.json (counts only; no reinterpretation)

Outputs:
  - artifacts/toe_compiled_coupling_mask.json
  - artifacts/toe_compiled_coupling_mask.md
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _mod3(x: int) -> int:
    return int(x) % 3


def main() -> None:
    conn_path = ROOT / "artifacts" / "toe_affine_plane_z3_connection.json"
    dual_path = ROOT / "artifacts" / "toe_affine_plane_duality.json"
    atlas_path = ROOT / "artifacts" / "toe_three_generation_coupling_atlas.json"

    conn = _load_json(conn_path)
    dual = _load_json(dual_path)
    atlas = _load_json(atlas_path) if atlas_path.exists() else None

    if conn.get("status") != "ok":
        raise RuntimeError("toe_affine_plane_z3_connection.json status != ok")
    if dual.get("status") != "ok":
        raise RuntimeError("toe_affine_plane_duality.json status != ok")

    # Build block->(t_shifted->vertex)
    v_by_block_t: Dict[int, Dict[int, int]] = {}
    for b in conn["blocks"]:
        bid = int(b["id"])
        mp: Dict[int, int] = {}
        for rec in b["vertices"]:
            mp[int(rec["t_shifted"])] = int(rec["v"])
        if set(mp.keys()) != {0, 1, 2}:
            raise RuntimeError("Each block must have all 3 t_shifted labels")
        v_by_block_t[bid] = mp

    # Forbidden triads come directly from the duality artifact (firewall partition).
    forbidden_triads = [
        tuple(sorted(int(x) for x in tri)) for tri in dual["firewall"]["bad_triads"]
    ]
    forbidden_set = set(forbidden_triads)
    if len(forbidden_set) != 9:
        raise RuntimeError("Expected 9 distinct forbidden triads")

    # Compile allowed triads using the fitted lambda laws and per-line ordered blocks.
    allowed_set = set()
    for line in conn["lines"]:
        eq = line["equation"]
        ordered_blocks = [int(x) for x in line["ordered_blocks"]]

        if eq["type"] == "y=mx+c":
            fam_key = str(("y=mx+c", int(eq["m"])))
        else:
            fam_key = str((str(eq["type"]), None))
        law = conn["lambda_laws_f3"][fam_key]
        c = int(eq.get("c", 0))
        lam = _mod3(int(law["a"]) * c + int(law["b"]))

        for k in range(3):
            tvals = [_mod3(k + i * lam) for i in range(3)]
            tri = tuple(
                sorted(v_by_block_t[b][t] for b, t in zip(ordered_blocks, tvals))
            )
            if tri in forbidden_set:
                raise RuntimeError("Compiled an explicitly forbidden triad as allowed")
            allowed_set.add(tri)

    if len(allowed_set) != 36:
        raise RuntimeError(f"Expected 36 allowed triads, got {len(allowed_set)}")

    all_triads = sorted(forbidden_set | allowed_set)
    if len(all_triads) != 45:
        raise RuntimeError("Expected 45 total triads")
    if len(set(all_triads)) != 45:
        raise RuntimeError("Triads not unique")

    # Compare to coupling atlas counts (purely numerical consistency).
    atlas_counts = None
    if isinstance(atlas, dict) and atlas.get("status") == "ok":
        counts = atlas.get("counts", {})
        # In the atlas construction each triad corresponds to 36 couplings (a 6x6 matching)
        atlas_counts = {
            "couplings_total": int(counts["couplings_total"]),
            "couplings_forbidden": int(counts["couplings_forbidden"]),
            "couplings_allowed": int(counts["couplings_allowed"]),
        }
        compiled_counts = {
            "triads_total": 45,
            "triads_forbidden": 9,
            "triads_allowed": 36,
            "couplings_total": 45 * 36,
            "couplings_forbidden": 9 * 36,
            "couplings_allowed": 36 * 36,
        }
        if atlas_counts["couplings_total"] != compiled_counts["couplings_total"]:
            raise RuntimeError("Atlas couplings_total mismatch vs compiled triads×36")
        if (
            atlas_counts["couplings_forbidden"]
            != compiled_counts["couplings_forbidden"]
        ):
            raise RuntimeError(
                "Atlas couplings_forbidden mismatch vs compiled forbidden triads×36"
            )
        if atlas_counts["couplings_allowed"] != compiled_counts["couplings_allowed"]:
            raise RuntimeError(
                "Atlas couplings_allowed mismatch vs compiled allowed triads×36"
            )

    # Quick structural histograms for documentation.
    block_of_v = {}
    # infer block-of-vertex from conn blocks
    for b in conn["blocks"]:
        bid = int(b["id"])
        for rec in b["vertices"]:
            block_of_v[int(rec["v"])] = bid
    line_hist = Counter()
    for tri in allowed_set:
        ids = tuple(sorted(block_of_v[v] for v in tri))
        line_hist[ids] += 1

    out = {
        "status": "ok",
        "sources": {
            "toe_affine_plane_z3_connection": str(conn_path),
            "toe_affine_plane_duality": str(dual_path),
            "toe_three_generation_coupling_atlas": (
                str(atlas_path) if atlas_path.exists() else None
            ),
        },
        "counts": {
            "triads_total": 45,
            "triads_forbidden": 9,
            "triads_allowed": 36,
            "couplings_per_triad": 36,
            "couplings_total": 45 * 36,
            "couplings_forbidden": 9 * 36,
            "couplings_allowed": 36 * 36,
        },
        "atlas_counts": atlas_counts,
        "forbidden_triads": [list(t) for t in sorted(forbidden_set)],
        "allowed_triads": [list(t) for t in sorted(allowed_set)],
        "affine_line_block_triples": [list(k) for k in sorted(line_hist)],
        "affine_line_lifts_per_line": sorted(set(line_hist.values())),
    }

    json_path = ROOT / "artifacts" / "toe_compiled_coupling_mask.json"
    md_path = ROOT / "artifacts" / "toe_compiled_coupling_mask.md"
    _write_json(json_path, out)

    md = []
    md.append("# TOE compiled coupling mask (AG(2,3)+Z3)")
    md.append("")
    md.append("## Counts")
    for k, v in out["counts"].items():
        md.append(f"- {k}: {v}")
    md.append("")
    md.append("## Affine-plane structure checks")
    md.append(
        f"- distinct affine lines (block triples): {len(out['affine_line_block_triples'])}"
    )
    md.append(f"- lifts per line: {out['affine_line_lifts_per_line']}")
    if atlas_counts:
        md.append("")
        md.append("## Coupling-atlas cross-check")
        md.append(f"- atlas_counts: {atlas_counts}")
    _write_md(md_path, "\n".join(md) + "\n")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
