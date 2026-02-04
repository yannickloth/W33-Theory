#!/usr/bin/env python3
"""
TOE: Generation-level coupling tensors from the 3-generation coupling atlas.

This turns the 1620 coupling records into compact generation-selection rules.

Key idea:
  Each record is an oriented map (field_a, field_b) -> field_out,
  labeled by (gen_a, gen_b, gen_out) ∈ {0,1,2}^3 and a firewall flag.

Outputs:
  - artifacts/toe_generation_coupling_tensors.json
  - artifacts/toe_generation_coupling_tensors.md
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
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


def _sig_key(in_fields: List[str], out_field: str) -> str:
    if len(in_fields) != 2:
        raise ValueError("in_fields must have length 2")
    return f"{in_fields[0]},{in_fields[1]} -> {out_field}"


def main() -> None:
    atlas_path = ROOT / "artifacts" / "toe_three_generation_coupling_atlas.json"
    atlas = _load_json(atlas_path)
    if atlas.get("status") != "ok":
        raise RuntimeError("toe_three_generation_coupling_atlas.json status != ok")

    recs = atlas.get("records", [])
    if not (isinstance(recs, list) and len(recs) == 1620):
        raise RuntimeError("Expected 1620 coupling records")

    # Signature -> counts and generation triple histogram.
    sig_counts: Dict[str, Counter] = defaultdict(Counter)
    sig_triples_allowed: Dict[str, Counter] = defaultdict(Counter)
    sig_triples_forbidden: Dict[str, Counter] = defaultdict(Counter)
    sig_triples_all: Dict[str, Counter] = defaultdict(Counter)

    all_triples = Counter()
    all_oriented_sigs = Counter()

    for r in recs:
        in_fields = list(r["in"]["fields"])
        out_field = str(r["out"]["field"])
        sig = _sig_key(in_fields, out_field)

        ga = int(r["gen_a"])
        gb = int(r["gen_b"])
        gc = int(r["gen_cbar"])
        tri = (ga, gb, gc)

        forbidden = bool(r["forbidden"])

        all_oriented_sigs[sig] += 1
        all_triples[tri] += 1

        sig_counts[sig]["total"] += 1
        sig_triples_all[sig][tri] += 1
        if forbidden:
            sig_counts[sig]["forbidden"] += 1
            sig_triples_forbidden[sig][tri] += 1
        else:
            sig_counts[sig]["allowed"] += 1
            sig_triples_allowed[sig][tri] += 1

    # Global generation selection rule: only 6 triples appear.
    global_triples = sorted(all_triples.items(), key=lambda kv: (-kv[1], kv[0]))
    if len(global_triples) != 6:
        raise RuntimeError(
            f"Expected exactly 6 generation triples globally, got {len(global_triples)}"
        )
    if set(v for _, v in global_triples) != {270}:
        raise RuntimeError("Expected each global triple to have count 270")

    # Extract the induced commutative fusion rule on unordered pairs {a,b} (a!=b).
    pair_to_c: Dict[Tuple[int, int], int] = {}
    for (a, b, c), _n in all_triples.items():
        if a == b:
            raise RuntimeError("Unexpected a=b generation triple in atlas")
        key = (min(a, b), max(a, b))
        if key in pair_to_c and pair_to_c[key] != c:
            raise RuntimeError(
                "Non-functional map from unordered pair to output generation"
            )
        pair_to_c[key] = c
    if set(pair_to_c.keys()) != {(0, 1), (0, 2), (1, 2)}:
        raise RuntimeError(f"Unexpected unordered pair keys: {pair_to_c.keys()}")

    # Per-signature: check the same 6 triples appear (with smaller counts).
    per_sig_summaries = []
    for sig, counts in sorted(
        sig_counts.items(), key=lambda kv: (-kv[1]["total"], kv[0])
    ):
        triple_hist = sig_triples_all[sig]
        triples = sorted(triple_hist.items(), key=lambda kv: (-kv[1], kv[0]))
        # Most signatures will have 6 triples; some may have fewer if a field never appears in some gen pairing.
        per_sig_summaries.append(
            {
                "signature": sig,
                "counts": {k: int(v) for k, v in counts.items()},
                "gen_triples": [
                    {"triple": list(t), "count": int(n)} for t, n in triples
                ],
                "gen_triples_allowed": [
                    {"triple": list(t), "count": int(n)}
                    for t, n in sorted(
                        sig_triples_allowed[sig].items(), key=lambda kv: (-kv[1], kv[0])
                    )
                ],
                "gen_triples_forbidden": [
                    {"triple": list(t), "count": int(n)}
                    for t, n in sorted(
                        sig_triples_forbidden[sig].items(),
                        key=lambda kv: (-kv[1], kv[0]),
                    )
                ],
            }
        )

    out = {
        "status": "ok",
        "sources": {"toe_three_generation_coupling_atlas": str(atlas_path)},
        "counts": {
            "records": 1620,
            "oriented_signatures": int(len(all_oriented_sigs)),
            "global_generation_triples": 6,
        },
        "global_generation_triples": [
            {"triple": list(t), "count": int(n)} for t, n in global_triples
        ],
        "generation_fusion_rule_unordered_pairs": {
            f"{a},{b}": int(c) for (a, b), c in sorted(pair_to_c.items())
        },
        "oriented_signature_summaries": per_sig_summaries,
        "note": (
            "The atlas only realizes 6 generation triples (ga,gb,gout) out of 27. "
            "This encodes a generation-selection law at the level of the E6 cubic product 27×27→27̄."
        ),
    }

    json_path = ROOT / "artifacts" / "toe_generation_coupling_tensors.json"
    md_path = ROOT / "artifacts" / "toe_generation_coupling_tensors.md"
    _write_json(json_path, out)

    md = []
    md.append("# TOE generation-level coupling tensors")
    md.append("")
    md.append("## Global generation triples")
    for row in out["global_generation_triples"]:
        md.append(f"- {row['triple']}: {row['count']}")
    md.append("")
    md.append("## Unordered-pair fusion rule")
    md.append(str(out["generation_fusion_rule_unordered_pairs"]))
    md.append("")
    md.append("## Top oriented signatures")
    for row in out["oriented_signature_summaries"][:10]:
        md.append(f"- {row['signature']}: {row['counts']}")
    _write_md(md_path, "\n".join(md) + "\n")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
