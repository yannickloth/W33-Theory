#!/usr/bin/env python3
"""Summarize minimal-certificate canonical-rep geotypes and orbits and produce a short markdown report + figures.

Usage:
  py -3 tools/report_min_cert_census.py --in-json artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_20k_with_geotypes.json artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2_with_geotypes.json artifacts/e6_f3_trilinear_min_cert_enumeration_agl_20k_with_geotypes.json --out-md docs/MIN_CERT_ORBIT_CENSUS_2026_02_10.md --out-dir reports/min_cert_census

The script writes:
  - a markdown report (`--out-md`)
  - figure PNGs to `--out-dir/figures`
  - a JSON summary `--out-dir/min_cert_census_summary.json`
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load_classified(path: Path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    reps = payload.get("representatives", [])
    out = []
    for r in reps:
        geotype = r.get("geotype", {})
        orbit_size = int(r.get("orbit_size", 0) or 0)
        ulines = int(geotype.get("unique_lines_count", 0) or 0)
        lines_multi = int(geotype.get("lines_with_multiple_z_count", 0) or 0)
        has_full = bool(geotype.get("has_full_z_line", False))
        unique_points = int(geotype.get("unique_points_covered", 0) or 0)
        z_hist = {
            int(k): int(v) for k, v in (geotype.get("z_histogram", {}) or {}).items()
        }
        sign_hist = {
            int(k): int(v) for k, v in (geotype.get("sign_histogram", {}) or {}).items()
        }
        out.append(
            {
                "orbit_size": orbit_size,
                "unique_lines_count": ulines,
                "lines_with_multiple_z_count": lines_multi,
                "has_full_z_line": has_full,
                "unique_points_covered": unique_points,
                "z_hist": z_hist,
                "sign_hist": sign_hist,
            }
        )
    return out


def summarize(dataset_name: str, rows: list[dict]):
    n = len(rows)
    if n == 0:
        return {"n": 0}
    orbit_sizes = [r["orbit_size"] for r in rows]
    ulines = [r["unique_lines_count"] for r in rows]
    lines_multi = [r["lines_with_multiple_z_count"] for r in rows]
    has_full = sum(1 for r in rows if r["has_full_z_line"])
    unique_points = [r["unique_points_covered"] for r in rows]

    z_agg = Counter()
    sign_agg = Counter()
    for r in rows:
        z_agg.update(r.get("z_hist", {}))
        sign_agg.update(r.get("sign_hist", {}))

    def stats(xs):
        return {
            "min": min(xs),
            "max": max(xs),
            "mean": statistics.mean(xs),
            "median": statistics.median(xs),
            "stdev": statistics.pstdev(xs) if len(xs) > 1 else 0.0,
        }

    return {
        "n": n,
        "orbit_stats": stats(orbit_sizes),
        "unique_lines_hist": dict(Counter(ulines)),
        "lines_with_multiple_z_hist": dict(Counter(lines_multi)),
        "has_full_z_line_count": int(has_full),
        "unique_points_stats": stats(unique_points),
        "z_aggregated": dict(z_agg),
        "sign_aggregated": dict(sign_agg),
    }


def make_plots(datasets: dict[str, list[dict]], out_dir: Path):
    try:
        import matplotlib.pyplot as plt
    except Exception as e:
        print("Matplotlib required for plots; skipping plot generation:", e)
        return []

    figs = []
    # Orbit size histograms
    plt.figure()
    for name, rows in datasets.items():
        orbit = [r["orbit_size"] for r in rows]
        if orbit:
            plt.hist(orbit, bins=30, alpha=0.5, label=f"{name} (n={len(orbit)})")
    plt.legend()
    plt.xlabel("orbit_size")
    plt.ylabel("count")
    plt.title("Orbit size distributions")
    out1 = out_dir / "figures" / "orbit_size_hist.png"
    out1.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out1)
    figs.append(out1)
    plt.close()

    # unique_lines_count hist
    plt.figure()
    for name, rows in datasets.items():
        u = [r["unique_lines_count"] for r in rows]
        if u:
            plt.hist(u, bins=range(1, 8), alpha=0.5, label=f"{name} (n={len(u)})")
    plt.legend()
    plt.xlabel("unique_lines_count")
    plt.ylabel("count")
    plt.title("Unique-lines count distribution")
    out2 = out_dir / "figures" / "unique_lines_count_hist.png"
    plt.savefig(out2)
    figs.append(out2)
    plt.close()

    # has_full_z_line bar chart
    plt.figure()
    names = []
    yes = []
    no = []
    for name, rows in datasets.items():
        names.append(name)
        yes.append(sum(1 for r in rows if r["has_full_z_line"]))
        no.append(len(rows) - yes[-1])
    x = range(len(names))
    plt.bar([i - 0.2 for i in x], yes, width=0.4, label="has_full_z_line")
    plt.bar([i + 0.2 for i in x], no, width=0.4, label="no_full_z_line")
    plt.xticks(x, names)
    plt.ylabel("count")
    plt.title("Presence of full z-lines in canonical reps")
    plt.legend()
    out3 = out_dir / "figures" / "has_full_z_line.png"
    plt.savefig(out3)
    figs.append(out3)
    plt.close()

    # Scatter orbit_size vs unique_lines
    plt.figure(figsize=(6, 4))
    for name, rows in datasets.items():
        xs = [r["unique_lines_count"] for r in rows]
        ys = [r["orbit_size"] for r in rows]
        if xs and ys:
            plt.scatter(xs, ys, alpha=0.6, label=f"{name}")
    plt.xlabel("unique_lines_count")
    plt.ylabel("orbit_size")
    plt.title("orbit_size vs unique_lines_count")
    plt.legend()
    out4 = out_dir / "figures" / "orbit_vs_lines_scatter.png"
    plt.savefig(out4)
    figs.append(out4)
    plt.close()

    return figs


def write_md_report(
    summary_by_name: dict[str, dict], figures: list[Path], out_md: Path
):
    lines = [
        "# Minimal-certificate canonical-representative census",
        "",
        "Generated programmatically.",
        "",
    ]

    for name, s in summary_by_name.items():
        lines.append(f"## {name}")
        if s.get("n", 0) == 0:
            lines.append("(no representatives)")
            lines.append("")
            continue
        lines.append(f"- distinct canonical representatives: **{s['n']}**")
        os = s["orbit_stats"]
        lines.append(
            f"- orbit_size: min={os['min']}, median={os['median']:.1f}, mean={os['mean']:.1f}, max={os['max']}"
        )
        lines.append(f"- unique_lines_count histogram: {s['unique_lines_hist']}")
        lines.append(
            f"- lines_with_multiple_z_count histogram: {s['lines_with_multiple_z_hist']}"
        )
        lines.append(
            f"- has_full_z_line count: {s['has_full_z_line_count']} (of {s['n']})"
        )
        lines.append(
            f"- unique_points_covered stats: min={s['unique_points_stats']['min']}, median={s['unique_points_stats']['median']}, mean={s['unique_points_stats']['mean']:.1f}, max={s['unique_points_stats']['max']}"
        )
        lines.append("")

    if figures:
        import os

        lines.append("## Figures")
        for f in figures:
            try:
                rel_path = os.path.relpath(str(f), start=str(Path.cwd()))
            except Exception:
                rel_path = str(f)
            # convert to forward slashes for markdown on all platforms
            rel_path = rel_path.replace("\\\\", "/")
            lines.append(f"![{f.name}]({rel_path})")
        lines.append("")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_md}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--in-json",
        type=Path,
        nargs="*",
        default=[
            ROOT
            / "artifacts"
            / "e6_f3_trilinear_min_cert_enumeration_hessian_20k_with_geotypes.json",
            ROOT
            / "artifacts"
            / "e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2_with_geotypes.json",
            ROOT
            / "artifacts"
            / "e6_f3_trilinear_min_cert_enumeration_agl_20k_with_geotypes.json",
        ],
    )
    p.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "docs" / "MIN_CERT_ORBIT_CENSUS_2026_02_10.md",
    )
    p.add_argument("--out-dir", type=Path, default=ROOT / "reports" / "min_cert_census")
    args = p.parse_args()

    datasets = {}
    for pth in args.in_json:
        if not pth.exists():
            print(f"Warning: input missing, skipping: {pth}")
            continue
        name = pth.stem.replace("e6_f3_trilinear_min_cert_enumeration_", "")
        rows = load_classified(pth)
        datasets[name] = rows

    summary_by_name = {n: summarize(n, r) for n, r in datasets.items()}

    args.out_dir.mkdir(parents=True, exist_ok=True)
    figs = make_plots(datasets, args.out_dir)

    # write JSON summary
    args.out_dir.joinpath("min_cert_census_summary.json").write_text(
        json.dumps(summary_by_name, indent=2), encoding="utf-8"
    )

    write_md_report(summary_by_name, figs, args.out_md)


if __name__ == "__main__":
    main()
