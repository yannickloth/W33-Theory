#!/usr/bin/env python3
"""Compute enrichment statistics for core motifs vs orbit classes.

We treat orbit class 2592 as the positive class and compute, per motif:
- support and precision in each dataset,
- lift over baseline prevalence,
- one-sided hypergeometric enrichment p-value.

This sharpens motif overlap counts into a statistical enrichment profile.
"""

from __future__ import annotations

import argparse
import json
import math
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


def _hypergeom_tail(N: int, K: int, n: int, x: int) -> float:
    """P[X >= x] for X ~ Hypergeometric(N, K, n)."""
    if n < 0 or K < 0 or N <= 0 or n > N or K > N:
        raise ValueError("invalid hypergeometric parameters")
    lo = max(0, n - (N - K))
    hi = min(n, K)
    if x <= lo:
        return 1.0
    if x > hi:
        return 0.0
    den = math.comb(N, n)
    total = 0
    for i in range(x, hi + 1):
        total += math.comb(K, i) * math.comb(N - K, n - i)
    return float(total) / float(den)


def _dataset_motif_stats(path: Path, core_motifs: Set[Motif]) -> Dict[str, Any]:
    payload = _load_json(path)
    reps = payload.get("representatives", [])
    N = len(reps)
    K = sum(1 for rep in reps if int(rep.get("orbit_size", -1)) == 2592)
    baseline_2592 = (float(K) / float(N)) if N else 0.0

    motif_counts: Dict[str, Dict[str, int]] = {}

    for rep in reps:
        y2592 = int(rep.get("orbit_size", -1) == 2592)
        overlap = _rep_triplets(rep.get("canonical_repr", [])).intersection(core_motifs)
        for motif in overlap:
            key = _motif_key(motif)
            row = motif_counts.setdefault(key, {"support": 0, "orbit_2592_count": 0})
            row["support"] += 1
            row["orbit_2592_count"] += y2592

    motif_stats: List[Dict[str, Any]] = []
    for key, row in motif_counts.items():
        n = int(row["support"])
        x = int(row["orbit_2592_count"])
        precision = (float(x) / float(n)) if n else 0.0
        lift = (precision / baseline_2592) if baseline_2592 > 0 else 0.0
        p_enrich_2592 = _hypergeom_tail(N, K, n, x) if n else 1.0
        # Also report reduced-class enrichment (orbit 1296) as complement.
        p_enrich_1296 = _hypergeom_tail(N, N - K, n, n - x) if n else 1.0
        motif_stats.append(
            {
                "motif": key,
                "support": n,
                "orbit_2592_count": x,
                "orbit_1296_count": int(n - x),
                "precision_2592": precision,
                "baseline_2592": baseline_2592,
                "lift_2592": lift,
                "pvalue_enrich_2592": p_enrich_2592,
                "pvalue_enrich_1296": p_enrich_1296,
            }
        )
    motif_stats.sort(key=lambda r: (-r["support"], r["motif"]))

    return {
        "dataset": str(path),
        "k_min": payload.get("k_min"),
        "distinct_representatives": int(N),
        "orbit_2592_total": int(K),
        "orbit_1296_total": int(N - K),
        "baseline_2592": baseline_2592,
        "motif_stats": motif_stats,
    }


def _merge_hessian_tables(rows: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    total_N = 0
    total_K = 0
    merged: Dict[str, Dict[str, int]] = {}

    for row in rows:
        N = int(row["distinct_representatives"])
        K = int(row["orbit_2592_total"])
        total_N += N
        total_K += K
        for m in row["motif_stats"]:
            key = str(m["motif"])
            r = merged.setdefault(key, {"support": 0, "orbit_2592_count": 0})
            r["support"] += int(m["support"])
            r["orbit_2592_count"] += int(m["orbit_2592_count"])

    baseline = (float(total_K) / float(total_N)) if total_N else 0.0
    out_rows: List[Dict[str, Any]] = []
    for key, r in merged.items():
        n = int(r["support"])
        x = int(r["orbit_2592_count"])
        precision = (float(x) / float(n)) if n else 0.0
        lift = (precision / baseline) if baseline > 0 else 0.0
        out_rows.append(
            {
                "motif": key,
                "support": n,
                "orbit_2592_count": x,
                "orbit_1296_count": int(n - x),
                "precision_2592": precision,
                "baseline_2592": baseline,
                "lift_2592": lift,
                "pvalue_enrich_2592": (
                    _hypergeom_tail(total_N, total_K, n, x) if n else 1.0
                ),
                "pvalue_enrich_1296": (
                    _hypergeom_tail(total_N, total_N - total_K, n, n - x) if n else 1.0
                ),
            }
        )
    out_rows.sort(key=lambda r: (-r["support"], r["motif"]))
    return {
        "distinct_representatives": int(total_N),
        "orbit_2592_total": int(total_K),
        "orbit_1296_total": int(total_N - total_K),
        "baseline_2592": baseline,
        "motif_stats": out_rows,
    }


def _find_motif(
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
        dataset_summary[name] = _dataset_motif_stats(path, core_motifs)

    hessian_rows = [
        dataset_summary[name]
        for name in ["hessian_exact_full", "hessian_exhaustive2"]
        if name in dataset_summary
    ]
    hessian_combined = _merge_hessian_tables(hessian_rows) if hessian_rows else {}

    x110 = _find_motif(hessian_combined.get("motif_stats", []), "x:1-1-0")
    x221 = _find_motif(hessian_combined.get("motif_stats", []), "x:2-2-1")

    theorem_flags = {
        "hessian_combined_has_x110": x110 is not None,
        "x110_support_ge_30": (x110 is not None and int(x110["support"]) >= 30),
        "x110_precision_ge_0p90": (
            x110 is not None and float(x110["precision_2592"]) >= 0.90
        ),
        "x110_enrichment_pvalue_le_0p05": (
            x110 is not None and float(x110["pvalue_enrich_2592"]) <= 0.05
        ),
        "x221_exists_and_is_pure_1296": (
            x221 is not None
            and int(x221["support"]) >= 2
            and int(x221["orbit_2592_count"]) == 0
        ),
    }

    return {
        "status": "ok",
        "rulebook_source": str(rulebook_json),
        "core_motif_count": int(len(core_motifs)),
        "dataset_summary": dataset_summary,
        "hessian_combined": hessian_combined,
        "focus_motifs": {
            "x_1_1_0": x110,
            "x_2_2_1": x221,
        },
        "missing_datasets": missing_datasets,
        "theorem_flags": theorem_flags,
        "notes": (
            "Provides enrichment/lift/pvalue diagnostics for core motifs vs "
            "orbit class, emphasizing Hessian combined behavior."
        ),
    }


def render_md(payload: Dict[str, Any]) -> str:
    lines: List[str] = ["# Core Motif Enrichment Stats", ""]
    lines.append(
        "- Statement: quantify enrichment of core motifs for orbit `2592` versus baseline prevalence."
    )
    lines.append(f"- Core motif count: `{payload['core_motif_count']}`")
    lines.append("")
    lines.append("Dataset | reps | baseline_2592")
    lines.append("--- | --- | ---")
    for name, row in payload["dataset_summary"].items():
        lines.append(
            f"{name} | {row['distinct_representatives']} | {row['baseline_2592']:.3f}"
        )

    lines.append("")
    lines.append("## Hessian Combined Focus Motifs")
    lines.append("")
    lines.append(
        "Motif | support | precision_2592 | lift_2592 | p_enrich_2592 | p_enrich_1296"
    )
    lines.append("--- | --- | --- | --- | --- | ---")
    for key in ["x_1_1_0", "x_2_2_1"]:
        row = payload["focus_motifs"].get(key)
        if not row:
            continue
        lines.append(
            f"{row['motif']} | {row['support']} | {row['precision_2592']:.3f} | "
            f"{row['lift_2592']:.3f} | {row['pvalue_enrich_2592']:.6f} | "
            f"{row['pvalue_enrich_1296']:.6f}"
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
        default=Path("artifacts/core_motif_enrichment_stats_2026_02_11.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("docs/CORE_MOTIF_ENRICHMENT_STATS_2026_02_11.md"),
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
