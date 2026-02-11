#!/usr/bin/env python3
"""Classify orbit polarization of nontrivial-core motifs in min-cert census.

This links:
- global nontrivial-core motifs from `nontrivial_core_rulebook`, and
- canonical minimal-certificate representatives with orbit sizes.

Key output: which motifs (especially x:1-1-0) are enriched in 2592-orbit
representatives versus 1296-orbit representatives in Hessian datasets.
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


def _rep_triplets(rep_rows: Sequence[Dict[str, Any]]) -> Set[Motif]:
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


def _motif_key(motif: Motif) -> str:
    line_type, trip = motif
    return f"{line_type}:{trip[0]}-{trip[1]}-{trip[2]}"


def _dataset_profile(path: Path, core_motifs: Set[Motif]) -> Dict[str, Any]:
    payload = _load_json(path)
    reps = payload.get("representatives", [])

    orbit_hist_total: Dict[str, int] = {}
    overlap_orbit_hist: Dict[str, int] = {}
    motif_orbit_hist: Dict[str, Dict[str, int]] = {}
    overlap_reps = 0
    overlap_idx_samples: List[int] = []

    for idx, rep in enumerate(reps):
        orbit = str(int(rep.get("orbit_size", -1)))
        orbit_hist_total[orbit] = orbit_hist_total.get(orbit, 0) + 1

        overlap = _rep_triplets(rep.get("canonical_repr", [])).intersection(core_motifs)
        if not overlap:
            continue

        overlap_reps += 1
        overlap_orbit_hist[orbit] = overlap_orbit_hist.get(orbit, 0) + 1
        if len(overlap_idx_samples) < 12:
            overlap_idx_samples.append(int(idx))

        for motif in sorted(overlap):
            key = _motif_key(motif)
            hist = motif_orbit_hist.setdefault(key, {})
            hist[orbit] = hist.get(orbit, 0) + 1

    motif_stats: List[Dict[str, Any]] = []
    for key, orbit_hist in motif_orbit_hist.items():
        c1296 = int(orbit_hist.get("1296", 0))
        c2592 = int(orbit_hist.get("2592", 0))
        support = c1296 + c2592
        precision_2592 = (float(c2592) / float(support)) if support else 0.0
        motif_stats.append(
            {
                "motif": key,
                "support": int(support),
                "orbit_1296_count": c1296,
                "orbit_2592_count": c2592,
                "precision_2592": precision_2592,
            }
        )
    motif_stats.sort(key=lambda row: (-row["support"], row["motif"]))

    total_reps = len(reps)
    return {
        "dataset": str(path),
        "k_min": payload.get("k_min"),
        "distinct_representatives": int(total_reps),
        "orbit_hist_total": orbit_hist_total,
        "overlap_representatives": int(overlap_reps),
        "overlap_orbit_hist": overlap_orbit_hist,
        "overlap_rate": (
            (float(overlap_reps) / float(total_reps)) if total_reps else 0.0
        ),
        "motif_stats": motif_stats,
        "overlap_index_samples": overlap_idx_samples,
    }


def _find_motif_stat(
    stats: Sequence[Dict[str, Any]], motif_key: str
) -> Dict[str, Any] | None:
    for row in stats:
        if row["motif"] == motif_key:
            return row
    return None


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

    dataset_summary: Dict[str, Dict[str, Any]] = {}
    missing_datasets: Dict[str, str] = {}
    for name, path in datasets.items():
        if not path.exists():
            missing_datasets[name] = str(path)
            continue
        dataset_summary[name] = _dataset_profile(path, core_motifs)

    x110_key = "x:1-1-0"
    x110_by_dataset: Dict[str, Dict[str, Any]] = {}
    for name, row in dataset_summary.items():
        x110_row = _find_motif_stat(row["motif_stats"], x110_key)
        if x110_row is not None:
            x110_by_dataset[name] = x110_row

    combined_1296 = int(
        sum(
            x110_by_dataset[name]["orbit_1296_count"]
            for name in x110_by_dataset
            if "hessian" in name
        )
    )
    combined_2592 = int(
        sum(
            x110_by_dataset[name]["orbit_2592_count"]
            for name in x110_by_dataset
            if "hessian" in name
        )
    )
    combined_support = combined_1296 + combined_2592
    combined_precision = (
        float(combined_2592) / float(combined_support) if combined_support else 0.0
    )

    theorem_flags = {
        "agl_exact_zero_overlap": (
            "agl_exact_full" in dataset_summary
            and dataset_summary["agl_exact_full"]["overlap_representatives"] == 0
        ),
        "hessian_exact_positive_overlap": (
            "hessian_exact_full" in dataset_summary
            and dataset_summary["hessian_exact_full"]["overlap_representatives"] > 0
        ),
        "hessian_exhaustive_positive_overlap": (
            "hessian_exhaustive2" in dataset_summary
            and dataset_summary["hessian_exhaustive2"]["overlap_representatives"] > 0
        ),
        "x110_precision_ge_0p90_in_hessian_exact": (
            "hessian_exact_full" in x110_by_dataset
            and float(x110_by_dataset["hessian_exact_full"]["precision_2592"]) >= 0.90
        ),
        "x110_precision_ge_0p90_in_hessian_exhaustive": (
            "hessian_exhaustive2" in x110_by_dataset
            and float(x110_by_dataset["hessian_exhaustive2"]["precision_2592"]) >= 0.90
        ),
        "x110_combined_precision_ge_0p90_in_hessian": combined_precision >= 0.90,
    }

    return {
        "status": "ok",
        "rulebook_source": str(rulebook_json),
        "core_motif_count": int(len(core_motifs)),
        "dataset_summary": dataset_summary,
        "x110_by_dataset": x110_by_dataset,
        "x110_hessian_combined": {
            "orbit_1296_count": combined_1296,
            "orbit_2592_count": combined_2592,
            "support": int(combined_support),
            "precision_2592": combined_precision,
        },
        "missing_datasets": missing_datasets,
        "theorem_flags": theorem_flags,
        "notes": (
            "Quantifies how nontrivial-core motifs polarize across orbit sizes "
            "in canonical minimal-certificate representatives."
        ),
    }


def render_md(payload: Dict[str, Any]) -> str:
    lines: List[str] = ["# Core Motif Orbit Polarization", ""]
    lines.append(
        "- Statement: classify orbit-size polarization of nontrivial-core motifs in minimal-certificate representative datasets."
    )
    lines.append(f"- Core motif count: `{payload['core_motif_count']}`")
    lines.append("")
    lines.append("Dataset | reps | overlap reps | overlap rate | overlap orbit hist")
    lines.append("--- | --- | --- | --- | ---")
    for name, row in payload["dataset_summary"].items():
        lines.append(
            f"{name} | {row['distinct_representatives']} | "
            f"{row['overlap_representatives']} | {row['overlap_rate']:.3f} | "
            f"{row['overlap_orbit_hist']}"
        )

    lines.append("")
    lines.append("## x:1-1-0 motif")
    lines.append("")
    lines.append("Dataset | support | orbit_1296 | orbit_2592 | precision_2592")
    lines.append("--- | --- | --- | --- | ---")
    for name, row in payload["x110_by_dataset"].items():
        lines.append(
            f"{name} | {row['support']} | {row['orbit_1296_count']} | "
            f"{row['orbit_2592_count']} | {row['precision_2592']:.3f}"
        )
    combo = payload["x110_hessian_combined"]
    lines.append(
        f"hessian_combined | {combo['support']} | {combo['orbit_1296_count']} | "
        f"{combo['orbit_2592_count']} | {combo['precision_2592']:.3f}"
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
        default=Path("artifacts/core_motif_orbit_polarization_2026_02_11.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("docs/CORE_MOTIF_ORBIT_POLARIZATION_2026_02_11.md"),
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
