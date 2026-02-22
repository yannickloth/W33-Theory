#!/usr/bin/env python3
"""Cross-link nontrivial-core rulebook motifs with minimal-certificate reps.

This script ties together:
- global nontrivial core motifs (size-3 UNSAT core triplet patterns), and
- canonical minimal-certificate representative datasets from enumeration/census.

It reports whether each representative contains a full parallel-class triplet
whose `(line_type, z0,z1,z2)` pattern matches the nontrivial-core motif set.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze

Motif = Tuple[str, Tuple[int, int, int]]


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _core_motif_set(rulebook_payload: Dict[str, Any]) -> Set[Motif]:
    motifs: Set[Motif] = set()
    for mode_row in rulebook_payload["matrix"].values():
        for cell in mode_row.values():
            for d, d_payload in cell["directions"].items():
                for trip in d_payload["triples"]:
                    motifs.add((str(d), (int(trip[0]), int(trip[1]), int(trip[2]))))
    return motifs


def _rep_parallel_triplets(rep_rows: Sequence[Dict[str, Any]]) -> Set[Motif]:
    by_type: Dict[str, Dict[int, int]] = {}
    for row in rep_rows:
        line = tuple(tuple(int(v) for v in p) for p in row["line"])
        line_type, offset = analyze._line_equation_type(line)
        by_type.setdefault(str(line_type), {})[int(offset)] = int(row["z"])

    out: Set[Motif] = set()
    for line_type, z_by_offset in by_type.items():
        if set(z_by_offset.keys()) == {0, 1, 2}:
            out.add(
                (
                    line_type,
                    (int(z_by_offset[0]), int(z_by_offset[1]), int(z_by_offset[2])),
                )
            )
    return out


def _dataset_summary(path: Path, core_motifs: Set[Motif]) -> Dict[str, Any]:
    payload = _load_json(path)
    reps = payload.get("representatives", [])

    total_reps = len(reps)
    total_weight = int(sum(int(r.get("hit_count", 1)) for r in reps))

    reps_with_parallel_triplet = 0
    reps_with_core_overlap = 0
    weight_with_core_overlap = 0

    overlap_motif_counts: Dict[str, int] = {}
    overlap_orbit_hist: Dict[str, int] = {}

    for idx, rep in enumerate(reps):
        rows = rep.get("canonical_repr", [])
        weight = int(rep.get("hit_count", 1))
        orbit_size = int(rep.get("orbit_size", -1))

        motifs = _rep_parallel_triplets(rows)
        if motifs:
            reps_with_parallel_triplet += 1

        overlap = motifs.intersection(core_motifs)
        if not overlap:
            continue

        reps_with_core_overlap += 1
        weight_with_core_overlap += weight
        overlap_orbit_hist[str(orbit_size)] = (
            overlap_orbit_hist.get(str(orbit_size), 0) + 1
        )

        for line_type, trip in sorted(overlap):
            key = f"{line_type}:{trip[0]}-{trip[1]}-{trip[2]}"
            overlap_motif_counts[key] = overlap_motif_counts.get(key, 0) + 1

    top_motifs = sorted(
        ({"motif": k, "count": int(v)} for (k, v) in overlap_motif_counts.items()),
        key=lambda row: (-row["count"], row["motif"]),
    )[:8]

    return {
        "dataset": str(path),
        "k_min": payload.get("k_min"),
        "distinct_representatives": int(total_reps),
        "total_weight": int(total_weight),
        "reps_with_parallel_triplet": int(reps_with_parallel_triplet),
        "reps_with_core_overlap": int(reps_with_core_overlap),
        "weight_with_core_overlap": int(weight_with_core_overlap),
        "overlap_rate": (
            float(reps_with_core_overlap) / float(total_reps) if total_reps else 0.0
        ),
        "overlap_orbit_hist": overlap_orbit_hist,
        "top_overlap_motifs": top_motifs,
        "representative_index_samples": [
            int(i)
            for i, rep in enumerate(reps)
            if _rep_parallel_triplets(rep.get("canonical_repr", [])).intersection(
                core_motifs
            )
        ][:10],
    }


def _iter_top_motifs(summary: Dict[str, Dict[str, Any]]) -> Iterable[str]:
    for row in summary.values():
        for motif in row["top_overlap_motifs"]:
            yield str(motif["motif"])


def build_report(
    *,
    rulebook_json: Path = Path("artifacts/nontrivial_core_rulebook_2026_02_11.json"),
    datasets: Dict[str, Path] | None = None,
) -> Dict[str, Any]:
    if datasets is None:
        datasets = {
            "agl_exact_full": Path(
                "artifacts/e6_f3_trilinear_min_cert_exact_agl_full_with_geotypes.json"
            ),
            "hessian_exact_full": Path(
                "artifacts/e6_f3_trilinear_min_cert_exact_hessian_full_with_geotypes.json"
            ),
            "hessian_exhaustive2": Path(
                "artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2_with_geotypes.json"
            ),
        }

    rulebook_payload = _load_json(rulebook_json)
    core_motifs = _core_motif_set(rulebook_payload)

    summary: Dict[str, Dict[str, Any]] = {}
    missing_datasets: Dict[str, str] = {}
    for name, path in datasets.items():
        if not path.exists():
            missing_datasets[name] = str(path)
            continue
        summary[name] = _dataset_summary(path, core_motifs)

    theorem_flags = {
        "agl_exact_has_zero_core_overlap": (
            "agl_exact_full" in summary
            and int(summary["agl_exact_full"]["reps_with_core_overlap"]) == 0
        ),
        "hessian_exact_has_positive_core_overlap": (
            "hessian_exact_full" in summary
            and int(summary["hessian_exact_full"]["reps_with_core_overlap"]) > 0
        ),
        "hessian_exhaustive_has_positive_core_overlap": (
            "hessian_exhaustive2" in summary
            and int(summary["hessian_exhaustive2"]["reps_with_core_overlap"]) > 0
        ),
        "dominant_overlap_motif_is_x_110": any(
            motif == "x:1-1-0" for motif in _iter_top_motifs(summary)
        ),
    }

    return {
        "status": "ok",
        "rulebook_source": str(rulebook_json),
        "core_motif_count": int(len(core_motifs)),
        "core_motifs_sorted": [
            [line_type, [int(t[0]), int(t[1]), int(t[2])]]
            for (line_type, t) in sorted(core_motifs)
        ],
        "dataset_summary": summary,
        "missing_datasets": missing_datasets,
        "theorem_flags": theorem_flags,
        "notes": (
            "Cross-links global nontrivial-core motifs with minimal-certificate "
            "canonical representatives from enumerator/census artifacts."
        ),
    }


def render_md(payload: Dict[str, Any]) -> str:
    lines: List[str] = ["# Core Rulebook x Minimal-Certificate Census Link", ""]
    lines.append(
        "- Statement: detect overlap between nontrivial global-core motifs and canonical minimal-certificate representative triplets."
    )
    lines.append(f"- Core motif count: `{payload['core_motif_count']}`")
    lines.append("")
    lines.append(
        "Dataset | distinct reps | reps with parallel triplet | reps with core overlap | overlap rate"
    )
    lines.append("--- | --- | --- | --- | ---")
    for name, row in payload["dataset_summary"].items():
        lines.append(
            f"{name} | {row['distinct_representatives']} | "
            f"{row['reps_with_parallel_triplet']} | "
            f"{row['reps_with_core_overlap']} | "
            f"{row['overlap_rate']:.3f}"
        )
    lines.append("")
    lines.append(f"- Theorem flags: `{payload['theorem_flags']}`")

    for name, row in payload["dataset_summary"].items():
        lines.append("")
        lines.append(f"## {name}")
        lines.append("")
        lines.append(f"- source: `{row['dataset']}`")
        lines.append(f"- overlap orbit histogram: `{row['overlap_orbit_hist']}`")
        lines.append(f"- top overlap motifs: `{row['top_overlap_motifs']}`")
        lines.append(
            f"- representative index samples: `{row['representative_index_samples']}`"
        )

    if payload["missing_datasets"]:
        lines.append("")
        lines.append("## Missing datasets")
        lines.append("")
        lines.append(f"- `{payload['missing_datasets']}`")

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
        default=Path("artifacts/core_rulebook_min_cert_link_2026_02_11.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("docs/CORE_RULEBOOK_MIN_CERT_LINK_2026_02_11.md"),
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
