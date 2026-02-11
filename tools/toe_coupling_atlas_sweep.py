#!/usr/bin/env python3
"""Sweep ChatGPT 'NewestWork' bundles for coupling atlas summaries.

For each subdirectory of artifacts/more_new_work_extracted that contains
either `toe_backbone_coset_coupling_map_v2_exact.json` or
`toe_coupling_strengths_v3.json`, produce a small summary JSON and a
collective summary file `artifacts/toe_coupling_atlas_sweep.json`.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
BUNDLES = ROOT / "artifacts" / "more_new_work_extracted"
OUT = ROOT / "artifacts"
OUT.mkdir(parents=True, exist_ok=True)


def summarize_bundle(bundle_dir: Path):
    # prefer exact backbone/coset map if present
    candidates = [
        bundle_dir / "toe_backbone_coset_coupling_map_v2_exact.json",
        bundle_dir / "toe_coupling_strengths_v3.json",
        bundle_dir / "toe_backbone_coset_coupling_map_v2.json",
    ]
    used = None
    data = None
    for c in candidates:
        if c.exists():
            used = c
            try:
                data = json.loads(open(c, encoding="utf-8").read())
            except Exception as e:
                return {"bundle": bundle_dir.name, "error": f"failed to load {c}: {e}"}
            break
    if data is None:
        return {"bundle": bundle_dir.name, "error": "no relevant coupling file found"}

    couplings = data.get("couplings") or []
    total = len(couplings)

    # try to use summary counts if available
    summary_counts = data.get("summary", {}).get("counts", {})
    backbone_major = summary_counts.get("backbone_major")
    coset_major = summary_counts.get("coset_major")
    mixed = summary_counts.get("mixed")

    # fall back to per-coupling classification
    b = c_ = m = 0
    backbone_fracs = []
    coset_fracs = []
    overlaps = []
    firewall_blocked = 0
    schlafli_edges = 0
    z12 = Counter()

    for cpl in couplings:
        # firewall
        if cpl.get("firewall_blocked"):
            firewall_blocked += 1
        if cpl.get("schlafli_edge"):
            schlafli_edges += 1

        # overlap
        if cpl.get("overlap") is not None:
            overlaps.append(float(cpl.get("overlap")))

        # phases
        if cpl.get("phase_Z12") is not None:
            z12[int(cpl.get("phase_Z12"))] += 1

        d = cpl.get("decomp")
        if d and isinstance(d, dict):
            bf = float(d.get("backbone_frac", 0.0))
            cf = float(d.get("coset_frac", 0.0))
            backbone_fracs.append(bf)
            coset_fracs.append(cf)
            if bf > 0.7:
                b += 1
            elif cf > 0.7:
                c_ += 1
            else:
                m += 1

    if backbone_major is None:
        backbone_major = b
    if coset_major is None:
        coset_major = c_
    if mixed is None:
        mixed = m

    avg_backbone = mean(backbone_fracs) if backbone_fracs else None
    avg_coset = mean(coset_fracs) if coset_fracs else None
    avg_overlap = mean(overlaps) if overlaps else None

    res = {
        "bundle": bundle_dir.name,
        "file_used": str(used) if used is not None else None,
        "total_couplings": total,
        "backbone_major": backbone_major,
        "coset_major": coset_major,
        "mixed": mixed,
        "firewall_blocked_count": firewall_blocked,
        "schlafli_edges": schlafli_edges,
        "phase_Z12_counts": dict(z12),
        "avg_backbone_frac": avg_backbone,
        "avg_coset_frac": avg_coset,
        "avg_overlap": avg_overlap,
    }
    return res


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bundles-dir", default=str(BUNDLES))
    args = p.parse_args()

    bundles_root = Path(args.bundles_dir)
    entries = []
    for d in sorted(bundles_root.iterdir() if bundles_root.exists() else []):
        if not d.is_dir():
            continue
        s = summarize_bundle(d)
        entries.append(s)
        # per-bundle write
        outp = OUT / f"toe_coupling_atlas_summary_{d.name}.json"
        from utils.json_safe import dump_json

        dump_json(s, outp, indent=2)
        print("Wrote", outp)

    # aggregate
    agg = {"bundles": entries}
    from utils.json_safe import dump_json

    dump_json(agg, OUT / "toe_coupling_atlas_sweep.json", indent=2)
    print("Wrote", OUT / "toe_coupling_atlas_sweep.json")

    # print table
    print("\nSUMMARY TABLE")
    print(
        "bundle\ttotal\tbackbone_major\tcoset_major\tmixed\tfirewall_blocked\tschlafli_edges"
    )
    for e in entries:
        print(
            f"{e.get('bundle')}\t{e.get('total_couplings')}\t{e.get('backbone_major')}\t{e.get('coset_major')}\t{e.get('mixed')}\t{e.get('firewall_blocked_count')}\t{e.get('schlafli_edges')}"
        )


if __name__ == "__main__":
    main()
