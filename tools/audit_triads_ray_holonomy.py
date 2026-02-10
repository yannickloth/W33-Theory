#!/usr/bin/env python3
"""Audit triad holonomy computed from quantized pairwise inner products of N12 MUB vectors.

This replicates the approach in bundles' scripts_recompute_w33_ray_holonomy.py but restricted
to the N12 vertex set (the triad table uses only N12 triples).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Dict, Tuple

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


def quantize_phase(z: complex) -> int:
    ang = math.atan2(z.imag, z.real)
    if ang < 0:
        ang += 2 * math.pi
    return int(round(ang / (2 * math.pi / 12))) % 12


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--triad-csv", type=Path, required=True)
    p.add_argument("--bundle-dir", type=Path, required=True)
    p.add_argument("--mub-phase-csv", type=Path, default=None)
    p.add_argument("--out-json", type=Path, default=Path("analysis/triad_ray_holonomy_vs_record.json"))
    args = p.parse_args()

    triad_csv = args.triad_csv
    bundle_dir = args.bundle_dir
    mub_csv = args.mub_phase_csv if args.mub_phase_csv else bundle_dir / "analysis" / "qutrit_MUB_state_vectors_for_N12_vertices_phase_corrected.csv"
    mub = parse_mub_csv(mub_csv)

    # compute k_edge for all unordered pairs among N12 vertices present in 'mub'
    k_edge: Dict[Tuple[int,int], int] = {}
    nids = sorted(mub.keys())
    for i in range(len(nids)):
        for j in range(i+1, len(nids)):
            a = nids[i]
            b = nids[j]
            ip = np.vdot(mub[a], mub[b])
            k = quantize_phase(ip)
            k_edge[(a,b)] = k
            k_edge[(b,a)] = (-k) % 12  # orientation might flip sign

    total = 0
    matches = 0
    mismatches = []
    with triad_csv.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            a = int(r["a"])
            b = int(r["b"])
            c = int(r["c"])
            rec = int(r["hol_mod12"]) if r.get("hol_mod12") else 0
            if (a not in mub) or (b not in mub) or (c not in mub):
                continue
            kab = k_edge.get((a,b))
            kbc = k_edge.get((b,c))
            kca = k_edge.get((c,a))
            if kab is None or kbc is None or kca is None:
                continue
            hol = (kab + kbc + kca) % 12
            total += 1
            if hol == rec:
                matches += 1
            else:
                mismatches.append({"triad": (a,b,c), "recorded": rec, "computed": int(hol), "kvals": (int(kab), int(kbc), int(kca))})

    out = {"total_triads": total, "matches": matches, "match_fraction": matches / total if total else None, "mismatches_sample": mismatches[:30]}
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
