#!/usr/bin/env python3
"""Search anchor motif sets for high-precision orbit classification.

This extends fixed-anchor channels by exhaustively scanning small anchor sets
over core motifs and selecting a best abstaining classifier under a precision
constraint.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze
import tools.core_motif_enrichment_stats as enrich

Motif = Tuple[str, Tuple[int, int, int]]


def _motif_key(motif: Motif) -> str:
    line_type, trip = motif
    return f"{line_type}:{trip[0]}-{trip[1]}-{trip[2]}"


def _rep_core_motifs(
    rep_rows: Sequence[Dict[str, Any]], core_motifs: Set[Motif]
) -> Set[str]:
    by_type: Dict[str, Dict[int, int]] = {}
    for row in rep_rows:
        line = tuple(tuple(int(v) for v in p) for p in row["line"])
        line_type, offset = analyze._line_equation_type(line)
        by_type.setdefault(str(line_type), {})[int(offset)] = int(row["z"])

    out: Set[str] = set()
    for line_type, z_by_offset in by_type.items():
        if set(z_by_offset.keys()) != {0, 1, 2}:
            continue
        motif = (
            line_type,
            (int(z_by_offset[0]), int(z_by_offset[1]), int(z_by_offset[2])),
        )
        if motif in core_motifs:
            out.add(_motif_key(motif))
    return out


def _load_hessian_reps() -> List[Dict[str, Any]]:
    paths = [
        Path(
            "artifacts/e6_f3_trilinear_min_cert_exact_hessian_full_with_geotypes.json"
        ),
        Path(
            "artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2_with_geotypes.json"
        ),
    ]
    reps: List[Dict[str, Any]] = []
    for path in paths:
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        reps.extend(payload.get("representatives", []))
    return reps


def _evaluate(
    *,
    rep_rows: Sequence[Tuple[int, Set[str]]],
    full_anchors: Set[str],
    reduced_anchors: Set[str],
) -> Dict[str, Any]:
    fired = 0
    correct = 0
    conflicts = 0
    pred_full = 0
    pred_reduced = 0
    true_full = 0
    true_reduced = 0
    correct_full = 0
    correct_reduced = 0

    for y_full, motifs in rep_rows:
        if y_full:
            true_full += 1
        else:
            true_reduced += 1

        hit_full = any(m in full_anchors for m in motifs)
        hit_reduced = any(m in reduced_anchors for m in motifs)
        if not hit_full and not hit_reduced:
            continue

        fired += 1
        if hit_full and hit_reduced:
            conflicts += 1
            continue

        pred = 1 if hit_full else 0
        if pred:
            pred_full += 1
        else:
            pred_reduced += 1
        if pred == y_full:
            correct += 1
            if pred:
                correct_full += 1
            else:
                correct_reduced += 1

    n = len(rep_rows)
    precision = (float(correct) / float(fired)) if fired else 0.0
    coverage = (float(fired) / float(n)) if n else 0.0
    full_recall = (float(correct_full) / float(true_full)) if true_full else 0.0
    reduced_recall = (
        float(correct_reduced) / float(true_reduced) if true_reduced else 0.0
    )
    return {
        "representative_count": int(n),
        "fired_count": int(fired),
        "coverage": coverage,
        "precision_when_fired": precision,
        "conflict_count": int(conflicts),
        "pred_full_count": int(pred_full),
        "pred_reduced_count": int(pred_reduced),
        "full_recall": full_recall,
        "reduced_recall": reduced_recall,
        "utility_score": precision * coverage,
    }


def _candidate_anchor_keys(
    motif_stats: Sequence[Dict[str, Any]],
    *,
    support_min: int,
) -> List[str]:
    return sorted(
        [
            str(row["motif"])
            for row in motif_stats
            if int(row.get("support", 0)) >= int(support_min)
        ]
    )


def build_report(
    *,
    rulebook_json: Path = Path("artifacts/nontrivial_core_rulebook_2026_02_11.json"),
    max_full_anchors: int = 3,
    max_reduced_anchors: int = 3,
    precision_min: float = 0.90,
    support_min: int = 1,
    top_k: int = 12,
) -> Dict[str, Any]:
    rb = json.loads(rulebook_json.read_text(encoding="utf-8"))
    core_motifs = enrich._core_motif_set(rb)
    reps = _load_hessian_reps()
    rep_rows: List[Tuple[int, Set[str]]] = [
        (
            1 if int(rep.get("orbit_size", -1)) == 2592 else 0,
            _rep_core_motifs(rep.get("canonical_repr", []), core_motifs),
        )
        for rep in reps
    ]

    base = enrich.build_report(rulebook_json=rulebook_json)
    motif_stats = list(base.get("hessian_combined", {}).get("motif_stats", []))
    motif_keys = _candidate_anchor_keys(motif_stats, support_min=int(support_min))

    candidates: List[Dict[str, Any]] = []
    for nf in range(1, int(max_full_anchors) + 1):
        for nr in range(1, int(max_reduced_anchors) + 1):
            for full_set in itertools.combinations(motif_keys, nf):
                full_keys = set(full_set)
                remainder = [k for k in motif_keys if k not in full_keys]
                for reduced_set in itertools.combinations(remainder, nr):
                    reduced_keys = set(reduced_set)
                    metrics = _evaluate(
                        rep_rows=rep_rows,
                        full_anchors=full_keys,
                        reduced_anchors=reduced_keys,
                    )
                    if int(metrics["conflict_count"]) != 0:
                        continue
                    if float(metrics["precision_when_fired"]) < float(precision_min):
                        continue
                    candidates.append(
                        {
                            "full_anchors": sorted(full_keys),
                            "reduced_anchors": sorted(reduced_keys),
                            "metrics": metrics,
                        }
                    )

    # Rank by coverage first (under precision constraint), then precision, then utility.
    candidates.sort(
        key=lambda row: (
            -float(row["metrics"]["coverage"]),
            -float(row["metrics"]["precision_when_fired"]),
            -float(row["metrics"]["utility_score"]),
            len(row["full_anchors"]) + len(row["reduced_anchors"]),
            row["full_anchors"],
            row["reduced_anchors"],
        )
    )
    best = candidates[0] if candidates else None

    fixed_anchor = {
        "full_anchors": ["x:1-1-0"],
        "reduced_anchors": ["x:2-2-1"],
    }
    fixed_anchor["metrics"] = _evaluate(
        rep_rows=rep_rows,
        full_anchors=set(fixed_anchor["full_anchors"]),
        reduced_anchors=set(fixed_anchor["reduced_anchors"]),
    )

    theorem_flags = {
        "has_feasible_candidate": best is not None,
        "best_coverage_ge_fixed_coverage": (
            best is not None
            and float(best["metrics"]["coverage"])
            >= float(fixed_anchor["metrics"]["coverage"])
        ),
        "best_precision_ge_precision_min": (
            best is not None
            and float(best["metrics"]["precision_when_fired"]) >= float(precision_min)
        ),
        "best_contains_x110": (
            best is not None and "x:1-1-0" in set(best["full_anchors"])
        ),
        "best_contains_x221": (
            best is not None and "x:2-2-1" in set(best["reduced_anchors"])
        ),
    }

    return {
        "status": "ok",
        "rulebook_source": str(rulebook_json),
        "search_space": {
            "motif_key_count": int(len(motif_keys)),
            "motif_keys": motif_keys,
            "max_full_anchors": int(max_full_anchors),
            "max_reduced_anchors": int(max_reduced_anchors),
            "precision_min": float(precision_min),
            "support_min": int(support_min),
        },
        "fixed_anchor_baseline": fixed_anchor,
        "best_candidate": best,
        "top_candidates": candidates[: int(top_k)],
        "candidate_count": int(len(candidates)),
        "theorem_flags": theorem_flags,
        "notes": (
            "Exhaustive small-anchor-set search under a precision constraint "
            "for abstaining orbit-class classifiers."
        ),
    }


def render_md(payload: Dict[str, Any]) -> str:
    lines: List[str] = ["# Core Motif Anchor Search", ""]
    lines.append(
        "- Statement: search small anchor sets maximizing coverage under a precision floor."
    )
    lines.append(f"- Search space: `{payload['search_space']}`")
    lines.append("")
    baseline = payload["fixed_anchor_baseline"]
    lines.append("## Fixed Baseline")
    lines.append("")
    lines.append(f"- full anchors: `{baseline['full_anchors']}`")
    lines.append(f"- reduced anchors: `{baseline['reduced_anchors']}`")
    lines.append(f"- metrics: `{baseline['metrics']}`")

    if payload["best_candidate"] is not None:
        best = payload["best_candidate"]
        lines.append("")
        lines.append("## Best Candidate")
        lines.append("")
        lines.append(f"- full anchors: `{best['full_anchors']}`")
        lines.append(f"- reduced anchors: `{best['reduced_anchors']}`")
        lines.append(f"- metrics: `{best['metrics']}`")

    lines.append("")
    lines.append("## Top Candidates")
    lines.append("")
    lines.append("Rank | coverage | precision | full anchors | reduced anchors")
    lines.append("--- | --- | --- | --- | ---")
    for i, row in enumerate(payload["top_candidates"], start=1):
        m = row["metrics"]
        lines.append(
            f"{i} | {m['coverage']:.3f} | {m['precision_when_fired']:.3f} | "
            f"`{row['full_anchors']}` | `{row['reduced_anchors']}`"
        )
    lines.append("")
    lines.append(f"- Theorem flags: `{payload['theorem_flags']}`")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rulebook-json",
        type=Path,
        default=Path("artifacts/nontrivial_core_rulebook_2026_02_11.json"),
    )
    parser.add_argument("--max-full-anchors", type=int, default=3)
    parser.add_argument("--max-reduced-anchors", type=int, default=3)
    parser.add_argument("--precision-min", type=float, default=0.90)
    parser.add_argument("--support-min", type=int, default=1)
    parser.add_argument("--top-k", type=int, default=12)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("artifacts/core_motif_anchor_search_2026_02_11.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("docs/CORE_MOTIF_ANCHOR_SEARCH_2026_02_11.md"),
    )
    args = parser.parse_args()

    payload = build_report(
        rulebook_json=args.rulebook_json,
        max_full_anchors=args.max_full_anchors,
        max_reduced_anchors=args.max_reduced_anchors,
        precision_min=args.precision_min,
        support_min=args.support_min,
        top_k=args.top_k,
    )
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_md(payload), encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
