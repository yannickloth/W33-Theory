#!/usr/bin/env python3
"""
Generate a compact "physics-facing" selection table:
  - For each E6 simple generator g, classify each of the 45 cubic triads as:
      preserved: d(p(t)) = d(t)
      flipped:   d(p(t)) = -d(t)
    (equivalently, in bits: effect_bit = d(p(t)) XOR d(t)).
  - Cross-tabulate these sets against the firewall-forbidden 9 triads.

Inputs (artifacts):
  - artifacts/selection_rules_report.json
  - artifacts/firewall_bad_triads_mapping.json
  - artifacts/canonical_su3_gauge_and_cubic.json  (for d_t signs)

Outputs:
  - artifacts/physics_selection_table.json
  - artifacts/physics_selection_table.md
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]


def _triad_key(t: List[int] | Tuple[int, int, int]) -> Tuple[int, int, int]:
    a, b, c = (int(x) for x in t)
    return tuple(sorted((a, b, c)))


def _key_str(t: Tuple[int, int, int]) -> str:
    return f"{t[0]},{t[1]},{t[2]}"


def main() -> None:
    sel = json.loads(
        (ROOT / "artifacts" / "selection_rules_report.json").read_text(encoding="utf-8")
    )
    fw = json.loads(
        (ROOT / "artifacts" / "firewall_bad_triads_mapping.json").read_text(
            encoding="utf-8"
        )
    )
    canon = json.loads(
        (ROOT / "artifacts" / "canonical_su3_gauge_and_cubic.json").read_text(
            encoding="utf-8"
        )
    )

    if sel.get("status") != "ok":
        raise RuntimeError("selection_rules_report.json missing or invalid")
    if fw.get("status") != "ok":
        raise RuntimeError("firewall_bad_triads_mapping.json missing or invalid")
    if not canon.get("counts", {}).get("solvable", False):
        raise RuntimeError("canonical_su3_gauge_and_cubic.json missing or unsolved")

    bad_triads = {_triad_key(t) for t in fw["bad_triangles_Schlafli_e6id"]}
    if len(bad_triads) != 9:
        raise RuntimeError("Expected 9 firewall bad triads")

    d_bits: Dict[Tuple[int, int, int], int] = {}
    for t in canon["solution"]["d_triples"]:
        triad = _triad_key(t["triple"])
        d_bits[triad] = 1 if int(t["sign"]) == -1 else 0
    if len(d_bits) != 45:
        raise RuntimeError("Expected 45 d_triples")

    triads = sorted(d_bits.keys())
    triad_set = set(triads)
    if not bad_triads <= triad_set:
        raise RuntimeError("Some firewall bad triads not present in 45 triads")

    generators_out = []
    for g in sel["generators"]:
        name = g["name"]
        global_scale = int(g["global_scale"])
        if global_scale not in (-1, 1):
            raise RuntimeError("Unexpected global_scale")

        # selection_rules_report already computed parity on each triad (±1):
        # parity = s_i s_j s_k, and effect_bit = d(p(t)) XOR d(t) = (parity==-1) XOR (global_scale==-1).
        parity_map = {
            tuple(int(x) for x in k.split(",")): int(v)
            for k, v in g["triad_parity"].items()
        }

        preserved = []
        flipped = []
        preserved_bad = []
        flipped_bad = []

        for t in triads:
            parity = parity_map[t]
            if parity not in (-1, 1):
                raise RuntimeError("Bad parity value")
            effect_bit = (1 if parity == -1 else 0) ^ (1 if global_scale == -1 else 0)
            if effect_bit == 0:
                preserved.append(t)
                if t in bad_triads:
                    preserved_bad.append(t)
            else:
                flipped.append(t)
                if t in bad_triads:
                    flipped_bad.append(t)

        generators_out.append(
            {
                "name": name,
                "global_scale": global_scale,
                "counts": {
                    "preserved": len(preserved),
                    "flipped": len(flipped),
                    "preserved_bad": len(preserved_bad),
                    "flipped_bad": len(flipped_bad),
                },
                "preserved_triads": [list(t) for t in preserved],
                "flipped_triads": [list(t) for t in flipped],
                "preserved_bad_triads": [list(t) for t in preserved_bad],
                "flipped_bad_triads": [list(t) for t in flipped_bad],
            }
        )

    out = {
        "status": "ok",
        "counts": {
            "generators": len(generators_out),
            "triads_total": 45,
            "firewall_bad_triads": 9,
        },
        "firewall_bad_triads": [list(t) for t in sorted(bad_triads)],
        "generators": generators_out,
    }

    out_json = ROOT / "artifacts" / "physics_selection_table.json"
    out_json.write_text(json.dumps(out, indent=2, default=int), encoding="utf-8")

    # Markdown summary (short + scannable).
    md = []
    md.append("# Physics-facing selection table (triads preserved vs flipped)")
    md.append("")
    md.append(f"- total triads: {out['counts']['triads_total']}")
    md.append(f"- firewall-bad triads: {out['counts']['firewall_bad_triads']}")
    md.append("")
    md.append("## Firewall-bad triads (E6-id)")
    for t in sorted(bad_triads):
        md.append(f"- {t}")
    md.append("")
    md.append("## Per-generator summary")
    for g in generators_out:
        c = g["counts"]
        md.append(
            f"- {g['name']}: preserved={c['preserved']} flipped={c['flipped']} | bad: preserved={c['preserved_bad']} flipped={c['flipped_bad']}"
        )
    md.append("")

    out_md = ROOT / "artifacts" / "physics_selection_table.md"
    out_md.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
