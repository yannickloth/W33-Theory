#!/usr/bin/env python3
"""Compute minimal positive certificates for the global identity cell.

For z-map z=(1,0), both `all_agl` and `hessian216` have exactly one global
full-sign stabilizer candidate (the identity with eps=+1). This script finds:

1) the smallest number of (line, z) constraints needed to isolate that unique
   candidate among all affine+eps candidates, and
2) how many minimal certificates of that size exist.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.minimal_global_full_sign_cores as cores

Z_MAP: Tuple[int, int] = (1, 0)
MODES: List[str] = ["all_agl", "hessian216"]


def _target_index(masks: Sequence[int], candidate_count: int) -> Tuple[int, int]:
    full = (1 << candidate_count) - 1
    live = full
    for m in masks:
        live &= m
    return live.bit_count(), (live & -live).bit_length() - 1


def _reject_masks(
    masks: Sequence[int], candidate_count: int, target_idx: int
) -> Tuple[List[int], int]:
    all_bits = (1 << candidate_count) - 1
    target_bit = 1 << target_idx
    reject: List[int] = []

    # Compact non-target candidate indices by deleting target bit position.
    for sat_mask in masks:
        fail = (all_bits ^ sat_mask) & (all_bits ^ target_bit)
        lower = fail & (target_bit - 1)
        upper = fail >> (target_idx + 1)
        compact = lower | (upper << target_idx)
        reject.append(compact)

    universe = (1 << (candidate_count - 1)) - 1
    return reject, universe


def _covers_all(
    comb: Sequence[int], reject_masks: Sequence[int], universe: int
) -> bool:
    covered = 0
    for j in comb:
        covered |= reject_masks[j]
        if covered == universe:
            return True
    return covered == universe


def _minimal_size(reject_masks: Sequence[int], universe: int) -> int:
    m = len(reject_masks)
    for k in range(1, m + 1):
        for comb in itertools.combinations(range(m), k):
            if _covers_all(comb, reject_masks, universe):
                return k
    raise RuntimeError("No certificate found; this should be impossible.")


def _summarize_mode(mode: str, max_examples: int, top_k: int) -> Dict[str, Any]:
    constraints = cores._constraints()
    signs = cores._sign_table(constraints)
    candidates = cores._candidate_pool(mode)
    masks = cores._sat_masks(constraints, candidates, Z_MAP, signs)

    target_count, target_idx = _target_index(masks, len(candidates))
    if target_count != 1:
        raise RuntimeError(
            f"Expected unique global match at z={Z_MAP}, got {target_count} in mode={mode}"
        )

    reject_masks, universe = _reject_masks(masks, len(candidates), target_idx)
    min_size = _minimal_size(reject_masks, universe)

    cert_count = 0
    frequencies = [0 for _ in constraints]
    sample_indices: List[List[int]] = []
    for comb in itertools.combinations(range(len(constraints)), min_size):
        if _covers_all(comb, reject_masks, universe):
            cert_count += 1
            for j in comb:
                frequencies[j] += 1
            if len(sample_indices) < max_examples:
                sample_indices.append(list(comb))

    freq_ranked = sorted(enumerate(frequencies), key=lambda t: (-t[1], t[0]))[
        : max(1, top_k)
    ]
    top_constraints = [
        {
            "constraint_index": int(idx),
            "frequency": int(freq),
            "frequency_ratio": float(freq / cert_count) if cert_count else 0.0,
            "constraint": cores._constraint_json(constraints[idx]),
        }
        for idx, freq in freq_ranked
        if freq > 0
    ]

    return {
        "mode": mode,
        "z_map": [int(Z_MAP[0]), int(Z_MAP[1])],
        "candidate_count": int(len(candidates)),
        "target_match_count": int(target_count),
        "target_candidate": cores._candidate_json(candidates[target_idx]),
        "minimal_certificate_size": int(min_size),
        "minimal_certificate_count": int(cert_count),
        "sample_certificates": [
            {
                "constraint_indices": [int(j) for j in comb],
                "constraints": [cores._constraint_json(constraints[j]) for j in comb],
            }
            for comb in sample_indices
        ],
        "top_constraints": top_constraints,
    }


def build_report(max_examples: int = 5, top_k: int = 8) -> Dict[str, Any]:
    results = {
        mode: _summarize_mode(mode=mode, max_examples=max_examples, top_k=top_k)
        for mode in MODES
    }
    flags = {
        "all_agl_min_size_6": results["all_agl"]["minimal_certificate_size"] == 6,
        "hessian216_min_size_5": results["hessian216"]["minimal_certificate_size"] == 5,
        "hessian_strictly_smaller_than_agl": results["hessian216"][
            "minimal_certificate_size"
        ]
        < results["all_agl"]["minimal_certificate_size"],
        "all_agl_count_688": results["all_agl"]["minimal_certificate_count"] == 688,
        "hessian216_count_33": results["hessian216"]["minimal_certificate_count"] == 33,
    }
    return {
        "status": "ok",
        "z_map": [int(Z_MAP[0]), int(Z_MAP[1])],
        "constraint_count": 36,
        "modes": MODES,
        "mode_results": results,
        "theorem_flags": flags,
        "notes": (
            "Positive identity certificates are exact minimal hitting sets over the "
            "finite non-identity candidate universe."
        ),
    }


def render_md(payload: Dict[str, Any]) -> str:
    lines: List[str] = ["# Minimal Global Identity Certificates", ""]
    lines.append(
        "- Statement: for z-map `(1,0)`, compute smallest witness sets of `(line,z)` constraints that isolate the unique global stabilizer."
    )
    lines.append("")
    lines.append(
        "Mode | Candidates | Minimal certificate size | Number of minimal certificates"
    )
    lines.append("--- | --- | --- | ---")
    for mode in MODES:
        row = payload["mode_results"][mode]
        lines.append(
            f"{mode} | {row['candidate_count']} | {row['minimal_certificate_size']} | {row['minimal_certificate_count']}"
        )
    lines.append("")
    lines.append(f"- Theorem flags: `{payload['theorem_flags']}`")
    lines.append("")

    for mode in MODES:
        row = payload["mode_results"][mode]
        lines.append(f"## {mode}")
        lines.append("")
        lines.append(
            f"- target candidate: `{row['target_candidate']}` (unique full match count `{row['target_match_count']}`)"
        )
        lines.append("- top constraints by frequency in minimal certificates:")
        for item in row["top_constraints"]:
            lines.append(
                f"  - idx `{item['constraint_index']}`: freq `{item['frequency']}` ({item['frequency_ratio']:.3f}) -> `{item['constraint']}`"
            )
        if row["sample_certificates"]:
            lines.append("- first sample certificate:")
            lines.append(f"  - `{row['sample_certificates'][0]}`")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("artifacts/minimal_global_identity_certificates_2026_02_11.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("docs/MINIMAL_GLOBAL_IDENTITY_CERTIFICATES_2026_02_11.md"),
    )
    parser.add_argument("--max-examples", type=int, default=5)
    parser.add_argument("--top-k", type=int, default=8)
    args = parser.parse_args()

    payload = build_report(max_examples=args.max_examples, top_k=args.top_k)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_md(payload), encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
