#!/usr/bin/env python3
"""Audit triad Bargmann triple phases vs recorded ray-holonomy table.

Reads a triad table like bundles/.../w33_four_center_triads_with_ray_holonomy.csv
and recomputes the Bargmann triple product using our corrected MUB CSV for N12.
Reports match fraction for hol_mod12 values (3 -> +i, 9 -> -i).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import List, Tuple

import numpy as np


def parse_mub_csv(path: Path):
    out = {}
    with path.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            nid = int(r["N12_vertex"])
            vecs = r["state_vector"].strip()
            vecs = vecs.strip()[1:-1]
            comps = [s.strip() for s in vecs.split(",")]
            v = np.array([complex(c) for c in comps], dtype=complex)
            v = v / np.linalg.norm(v)
            out[nid] = v
    return out


def phase_triangle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> complex:
    prod = np.vdot(a, b) * np.vdot(b, c) * np.vdot(c, a)
    if abs(prod) < 1e-12:
        return 0 + 0j
    return prod / abs(prod)


def map_to_mod12(ph: complex) -> int:
    # Map to nearest of +i or -i => 3 or 9 (mod 12)
    targets = {3: 1j, 9: -1j}
    best_k = None
    best_d = float('inf')
    for k, t in targets.items():
        d = abs(ph - t)
        if d < best_d:
            best_d = d
            best_k = k
    # fallback: if neither close, return 0 meaning no assigned
    if best_d > 1e-3:
        return 0
    return int(best_k)


def parse_rays_csv(path: Path):
    out = {}
    with path.open('r', encoding='utf-8') as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            pid = int(r['point_id'])
            comps = [complex(str(r[c]).replace('i', 'j')) for c in ('v0', 'v1', 'v2', 'v3')]
            v = np.array(comps, dtype=complex)
            v = v / np.linalg.norm(v)
            out[pid] = v
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--triad-csv", type=Path, required=True)
    p.add_argument("--bundle-dir", type=Path, required=True)
    p.add_argument("--mub-phase-csv", type=Path, default=None)
    p.add_argument("--rays-csv", type=Path, default=None)
    p.add_argument("--out-json", type=Path, default=Path("analysis/triad_bargmann_vs_record.json"))
    args = p.parse_args()

    triad_csv = args.triad_csv
    bundle_dir = args.bundle_dir
    mub_csv = args.mub_phase_csv if args.mub_phase_csv else bundle_dir / "analysis" / "qutrit_MUB_state_vectors_for_N12_vertices_phase_corrected.csv"
    mub = parse_mub_csv(mub_csv) if args.rays_csv is None else {}
    rays = parse_rays_csv(args.rays_csv) if args.rays_csv else None

    total = 0
    matches = 0
    mismatches = []
    with triad_csv.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            # support either 'triad' column ("i j k") or separate a,b,c columns
            if r.get("triad"):
                try:
                    a, b, c = [int(x) for x in r["triad"].split()]
                except Exception:
                    continue
            else:
                a = int(r["a"])
                b = int(r["b"])
                c = int(r["c"])

            # accept either hol_mod12 or holonomy_z12 naming
            if r.get("hol_mod12"):
                rec = int(r["hol_mod12"])
            elif r.get("holonomy_z12"):
                rec = int(r["holonomy_z12"])
            else:
                rec = 0

            # pick vectors from rays (if provided) or from MUB CSV
            if rays is not None:
                if a not in rays or b not in rays or c not in rays:
                    continue
                va = rays[a]
                vb = rays[b]
                vc = rays[c]
            else:
                if a not in mub or b not in mub or c not in mub:
                    continue
                va = mub[a]
                vb = mub[b]
                vc = mub[c]

            ph = phase_triangle(va, vb, vc)
            if abs(ph) < 1e-12:
                # degenerate triple
                continue
            k = map_to_mod12(ph)
            total += 1
            if k == rec:
                matches += 1
            else:
                mismatches.append({"triad": (a, b, c), "recorded": rec, "bargmann_k": k, "bargmann_phase": [round(ph.real, 6), round(ph.imag, 6)]})

    out = {"total_triads": total, "matches": matches, "match_fraction": matches / total if total else None, "mismatches_sample": mismatches[:30]}
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
