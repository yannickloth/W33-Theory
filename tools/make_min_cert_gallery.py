#!/usr/bin/env python3
"""Generate a small gallery of canonical minimal-certificate representatives.

Usage:
  py -3 tools/make_min_cert_gallery.py --in-json artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2_with_geotypes.json artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_20k_with_geotypes.json artifacts/e6_f3_trilinear_min_cert_enumeration_agl_20k_with_geotypes.json --out-md docs/MIN_CERT_REPRESENTATIVE_GALLERY_2026_02_10.md --out-dir reports/min_cert_census/gallery --per-dataset 9 --selection diverse

Outputs:
 - Markdown gallery at `--out-md` that includes embedded PNG thumbnails per representative
 - PNG images in `--out-dir/figures/`
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load_payload(path: Path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    reps = payload.get("representatives", [])
    return reps


def select_reps(reps, per_dataset: int, selection: str = "diverse"):
    if not reps:
        return []
    # attach computed keys
    rows = []
    for i, r in enumerate(reps):
        ge = r.get("geotype", {})
        rows.append(
            {
                "idx": i,
                "orbit_size": int(r.get("orbit_size", 0) or 0),
                "unique_lines_count": int(ge.get("unique_lines_count", 0) or 0),
                "lines_multi": int(ge.get("lines_with_multiple_z_count", 0) or 0),
                "has_full": bool(ge.get("has_full_z_line", False)),
                "r": r,
            }
        )
    if selection == "top-orbit":
        rows.sort(key=lambda x: (-x["orbit_size"], x["unique_lines_count"]))
        return [r["r"] for r in rows[:per_dataset]]

    # "diverse": group by (unique_lines_count, lines_multi, has_full) and pick representative from each group
    groups = defaultdict(list)
    for r in rows:
        key = (r["unique_lines_count"], r["lines_multi"], r["has_full"])
        groups[key].append(r)
    # sort groups by size desc to pick from largest groups first
    keys = sorted(groups.keys(), key=lambda k: (-len(groups[k]), k))
    selected = []
    gi = 0
    while len(selected) < per_dataset and keys:
        key = keys[gi % len(keys)]
        bucket = groups[key]
        # pick highest-orbit in bucket not yet selected
        bucket.sort(key=lambda x: -x["orbit_size"])
        candidate = bucket.pop(0)
        selected.append(candidate["r"])
        if not bucket:
            keys.remove(key)
        gi += 1
    return selected


def render_rep_image(rep, out_path: Path, dpi: int = 150):
    # rep: dict with 'canonical_repr' (list of witness dicts) and 'geotype' and 'orbit_size'
    try:
        import matplotlib.pyplot as plt
    except Exception:
        raise RuntimeError("matplotlib required to render images")

    z_colors = {0: "tab:blue", 1: "tab:orange", 2: "tab:green"}

    fig, ax = plt.subplots(figsize=(3, 3), dpi=dpi)
    ax.set_xlim(-0.5, 2.5)
    ax.set_ylim(-0.5, 2.5)
    ax.set_xticks([0, 1, 2])
    ax.set_yticks([0, 1, 2])
    ax.set_aspect("equal")
    ax.grid(True, linestyle=":", color="#dddddd")

    canon = rep.get("canonical_repr", [])
    # draw each witness (line: 3 points), color by z, linestyle by sign
    for w in canon:
        line = w.get("line", [])
        z = int(w.get("z", 0))
        sign = int(w.get("sign", w.get("sign_pm1", 1)))
        xs = [p[0] for p in line]
        ys = [p[1] for p in line]
        color = z_colors.get(z, "black")
        ls = "-" if sign >= 0 else "--"
        # draw extended line by connecting min to max of coordinates for a clean segment
        ax.plot(xs, ys, color=color, linewidth=4, linestyle=ls, solid_capstyle="round")
        # draw points
        ax.scatter(xs, ys, color=color, edgecolor="black", zorder=3, s=40)
        # annotate small z
        for x, y in zip(xs, ys):
            ax.text(x + 0.05, y + 0.05, f"z={z}", fontsize=6, color="black")
    # caption
    ge = rep.get("geotype", {})
    orbit = rep.get("orbit_size", 0)
    caption = f"orbit={orbit}, lines={ge.get('unique_lines_count')}, lines_multi={ge.get('lines_with_multiple_z_count')}, full_z={ge.get('has_full_z_line') or False}"
    ax.set_title(caption, fontsize=8)
    # save
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def write_gallery_md(
    dataset_name: str, selected_reps: list, out_md: Path, out_dir: Path
):
    lines = [f"## {dataset_name}", ""]
    for i, rep in enumerate(selected_reps, 1):
        img_name = f"{dataset_name}_rep_{i}.png"
        img_path = out_dir / "figures" / img_name
        # make sure img exists
        if not img_path.exists():
            continue
        rel = os.path.relpath(str(img_path), start=str(Path.cwd())).replace("\\\\", "/")
        lines.append(f"### Representative {i}")
        lines.append(f"![{img_name}]({rel})")
        ge = rep.get("geotype", {})
        orbit = rep.get("orbit_size", 0)
        lines.append("")
        lines.append(f"- orbit_size: **{orbit}**")
        lines.append(
            f"- unique_lines_count: **{ge.get('unique_lines_count')}**, lines_with_multiple_z_count: **{ge.get('lines_with_multiple_z_count')}**, has_full_z_line: **{ge.get('has_full_z_line')}**"
        )
        # add a short canonical repr snippet
        canon = rep.get("canonical_repr", [])
        snippet = json.dumps(canon, indent=2)
        lines.append("```json")
        # only include first 500 chars limited
        lines.extend(snippet.splitlines()[:20])
        lines.append("```")
        lines.append("")
    out_md.parent.mkdir(parents=True, exist_ok=True)
    # append to file
    with out_md.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Appended gallery for {dataset_name} to {out_md}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--in-json",
        type=Path,
        nargs="*",
        default=[
            ROOT
            / "artifacts"
            / "e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2_with_geotypes.json",
            ROOT
            / "artifacts"
            / "e6_f3_trilinear_min_cert_enumeration_hessian_20k_with_geotypes.json",
            ROOT
            / "artifacts"
            / "e6_f3_trilinear_min_cert_enumeration_agl_20k_with_geotypes.json",
        ],
    )
    p.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "docs" / "MIN_CERT_REPRESENTATIVE_GALLERY_2026_02_10.md",
    )
    p.add_argument(
        "--out-dir", type=Path, default=ROOT / "reports" / "min_cert_census" / "gallery"
    )
    p.add_argument("--per-dataset", type=int, default=9)
    p.add_argument(
        "--selection", type=str, choices=("diverse", "top-orbit"), default="diverse"
    )
    args = p.parse_args()

    out_dir = args.out_dir
    out_md = args.out_md

    # start fresh gallery
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(
        "# Minimal-certificate representative gallery\n\n", encoding="utf-8"
    )

    for pth in args.in_json:
        if not pth.exists():
            print(f"Skipping missing artifact: {pth}")
            continue
        name = pth.stem.replace("e6_f3_trilinear_min_cert_enumeration_", "")
        reps = load_payload(pth)
        selected = select_reps(reps, args.per_dataset, selection=args.selection)
        # render images
        for i, rep in enumerate(selected, 1):
            img_name = f"{name}_rep_{i}.png"
            img_path = out_dir / "figures" / img_name
            try:
                render_rep_image(rep, img_path)
            except Exception as e:
                print(f"Warning: failed to render {name} rep {i}: {e}")
        write_gallery_md(name, selected, out_md, out_dir)

    print(f"Wrote gallery {out_md} and images under {out_dir}/figures")


if __name__ == "__main__":
    main()
