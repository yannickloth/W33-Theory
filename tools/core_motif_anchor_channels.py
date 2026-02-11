#!/usr/bin/env python3
"""Discover high-precision anchor motif channels for orbit classes.

Uses combined Hessian motif statistics to extract:
- full-orbit anchors (high precision_2592, enough support),
- reduced-orbit anchors (low precision_2592, enough support),
then evaluates a simple anchor classifier with abstention.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze
import tools.core_motif_enrichment_stats as enrich

Motif = Tuple[str, Tuple[int, int, int]]


def _motif_from_key(key: str) -> Motif:
    line_type, enc = key.split(":")
    a, b, c = enc.split("-")
    return (line_type, (int(a), int(b), int(c)))


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
            out.add(f"{line_type}:{motif[1][0]}-{motif[1][1]}-{motif[1][2]}")
    return out


def _evaluate_anchor_classifier(
    *,
    reps: Sequence[Dict[str, Any]],
    core_motifs: Set[Motif],
    full_anchors: Set[str],
    reduced_anchors: Set[str],
) -> Dict[str, Any]:
    fired = 0
    correct = 0
    conflict = 0
    pred_full = 0
    pred_reduced = 0
    true_full = 0
    true_reduced = 0
    correct_full = 0
    correct_reduced = 0

    for rep in reps:
        y_full = int(rep.get("orbit_size", -1) == 2592)
        if y_full:
            true_full += 1
        else:
            true_reduced += 1

        motifs = _rep_core_motifs(rep.get("canonical_repr", []), core_motifs)
        hit_full = any(m in full_anchors for m in motifs)
        hit_reduced = any(m in reduced_anchors for m in motifs)
        if not hit_full and not hit_reduced:
            continue

        fired += 1
        if hit_full and hit_reduced:
            conflict += 1
            continue

        if hit_full:
            pred_full += 1
            if y_full:
                correct += 1
                correct_full += 1
        else:
            pred_reduced += 1
            if not y_full:
                correct += 1
                correct_reduced += 1

    precision_when_fired = (float(correct) / float(fired)) if fired else 0.0
    coverage = (float(fired) / float(len(reps))) if reps else 0.0
    recall_full = (float(correct_full) / float(true_full)) if true_full else 0.0
    recall_reduced = (
        float(correct_reduced) / float(true_reduced) if true_reduced else 0.0
    )
    return {
        "representative_count": int(len(reps)),
        "fired_count": int(fired),
        "coverage": coverage,
        "correct_when_fired": int(correct),
        "precision_when_fired": precision_when_fired,
        "conflict_count": int(conflict),
        "pred_full_count": int(pred_full),
        "pred_reduced_count": int(pred_reduced),
        "true_full_count": int(true_full),
        "true_reduced_count": int(true_reduced),
        "full_recall": recall_full,
        "reduced_recall": recall_reduced,
    }


def build_report(
    *,
    rulebook_json: Path = Path("artifacts/nontrivial_core_rulebook_2026_02_11.json"),
    full_precision_min: float = 0.90,
    full_support_min: int = 10,
    reduced_precision_max: float = 0.10,
    reduced_support_min: int = 2,
) -> Dict[str, Any]:
    enrichment = enrich.build_report(rulebook_json=rulebook_json)
    hessian = enrichment["hessian_combined"]
    stats = hessian["motif_stats"]

    full_anchors = sorted(
        [
            str(row["motif"])
            for row in stats
            if float(row["precision_2592"]) >= float(full_precision_min)
            and int(row["support"]) >= int(full_support_min)
        ]
    )
    reduced_anchors = sorted(
        [
            str(row["motif"])
            for row in stats
            if float(row["precision_2592"]) <= float(reduced_precision_max)
            and int(row["support"]) >= int(reduced_support_min)
        ]
    )

    # Build core motif set from enrichment input path.
    rb = json.loads(Path(rulebook_json).read_text(encoding="utf-8"))
    core_motifs = enrich._core_motif_set(rb)

    datasets = {
        "hessian_exact_full": Path(
            "artifacts/e6_f3_trilinear_min_cert_exact_hessian_full_with_geotypes.json"
        ),
        "hessian_exhaustive2": Path(
            "artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2_with_geotypes.json"
        ),
    }
    evals: Dict[str, Dict[str, Any]] = {}
    merged_reps: List[Dict[str, Any]] = []
    for name, path in datasets.items():
        if not path.exists():
            continue
        reps = json.loads(path.read_text(encoding="utf-8")).get("representatives", [])
        evals[name] = _evaluate_anchor_classifier(
            reps=reps,
            core_motifs=core_motifs,
            full_anchors=set(full_anchors),
            reduced_anchors=set(reduced_anchors),
        )
        merged_reps.extend(reps)
    evals["hessian_combined"] = _evaluate_anchor_classifier(
        reps=merged_reps,
        core_motifs=core_motifs,
        full_anchors=set(full_anchors),
        reduced_anchors=set(reduced_anchors),
    )

    theorem_flags = {
        "full_anchor_contains_x110": "x:1-1-0" in set(full_anchors),
        "reduced_anchor_contains_x221": "x:2-2-1" in set(reduced_anchors),
        "combined_precision_when_fired_ge_0p90": (
            float(evals["hessian_combined"]["precision_when_fired"]) >= 0.90
        ),
        "combined_conflict_count_zero": int(evals["hessian_combined"]["conflict_count"])
        == 0,
    }

    return {
        "status": "ok",
        "rulebook_source": str(rulebook_json),
        "anchor_thresholds": {
            "full_precision_min": float(full_precision_min),
            "full_support_min": int(full_support_min),
            "reduced_precision_max": float(reduced_precision_max),
            "reduced_support_min": int(reduced_support_min),
        },
        "full_anchors": full_anchors,
        "reduced_anchors": reduced_anchors,
        "anchor_evaluation": evals,
        "theorem_flags": theorem_flags,
        "notes": (
            "Anchor classifier with abstention over core motifs in Hessian "
            "representatives."
        ),
    }


def render_md(payload: Dict[str, Any]) -> str:
    lines: List[str] = ["# Core Motif Anchor Channels", ""]
    lines.append(
        "- Statement: derive high-precision anchor motifs and evaluate an abstaining classifier for orbit class."
    )
    lines.append(f"- full anchors: `{payload['full_anchors']}`")
    lines.append(f"- reduced anchors: `{payload['reduced_anchors']}`")
    lines.append("")
    lines.append(
        "Dataset | reps | fired | coverage | precision_when_fired | full_recall | reduced_recall"
    )
    lines.append("--- | --- | --- | --- | --- | --- | ---")
    for name, row in payload["anchor_evaluation"].items():
        lines.append(
            f"{name} | {row['representative_count']} | {row['fired_count']} | "
            f"{row['coverage']:.3f} | {row['precision_when_fired']:.3f} | "
            f"{row['full_recall']:.3f} | {row['reduced_recall']:.3f}"
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
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("artifacts/core_motif_anchor_channels_2026_02_11.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("docs/CORE_MOTIF_ANCHOR_CHANNELS_2026_02_11.md"),
    )
    args = parser.parse_args()

    payload = build_report(rulebook_json=args.rulebook_json)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_md(payload), encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
