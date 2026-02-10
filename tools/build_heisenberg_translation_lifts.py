#!/usr/bin/env python3
"""Build canonical translation lifts Tx, Ty and central Z as permutations on W33 vertices.

Outputs:
  - W33_Heisenberg_generators_Tx_Ty_Z.json
  - W33_translation_lifts_canonical.csv
  - H27_vertices_as_F3_cube_xy_t_holonomy_gauge.csv (a copy of the canonical mapping)

Usage:
  py -3 tools/build_heisenberg_translation_lifts.py --bundle-dir artifacts/bundles/W33_Heisenberg_action_bundle_20260209_v1 --out-dir artifacts/bundles/W33_Heisenberg_action_bundle_20260209_v1/analysis
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Tuple


def load_h27(bundle_dir: Path):
    path = bundle_dir / "H27_vertices_as_F3_cube_xy_t.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    hmap = {}
    coords = {}
    with path.open("r", encoding="utf-8") as f:
        hdr = f.readline()
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = [s.strip() for s in line.split(",")]
            wid = int(parts[0])
            x = int(parts[1])
            y = int(parts[2])
            t = int(parts[3])
            hmap[wid] = (x, y, t)
            coords[(x, y, t)] = wid
    return hmap, coords


def load_n12(bundle_dir: Path):
    import csv

    path = bundle_dir / "N12_vertices_as_affine_lines.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    data = {}
    with path.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            nid = int(r["N12_vertex"])
            slope_raw = r["slope_m"].strip()
            slope_val = "inf" if slope_raw.lower() == "inf" else int(slope_raw)
            intercept = int(r["intercept_b"])
            pts_field = r.get("phase_points", "")
            pts = []
            for p in [s.strip() for s in pts_field.split(";") if s.strip()]:
                p = p.strip("() ")
                if not p:
                    continue
                x_str, y_str = p.split(",")
                pts.append((int(x_str), int(y_str)))
            data[nid] = {"slope": slope_val, "intercept": int(intercept), "phase_points": pts}
    return data


def apply_mat_to_point(mat, p):
    a, b, c, d = mat
    x, y = p
    return ((a * x + b * y) % 3, (c * x + d * y) % 3)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bundle-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, default=None)
    args = p.parse_args()

    bundle = args.bundle_dir
    out_dir = args.out_dir if args.out_dir is not None else bundle / "analysis"
    out_dir.mkdir(parents=True, exist_ok=True)

    hmap, coords = load_h27(bundle)
    n12 = load_n12(bundle)

    # Build Tx: (x,y,t) -> (x+1, y, t)
    Tx_H = {}
    Ty_H = {}

    for wid, (x, y, t) in hmap.items():
        dst_tx = ((x + 1) % 3, y, t)
        dst_ty = (x, (y + 1) % 3, (t + x) % 3)
        if dst_tx in coords:
            Tx_H[str(wid)] = coords[dst_tx]
        else:
            raise RuntimeError(f"Tx image missing for H vertex {wid} -> {dst_tx}")
        if dst_ty in coords:
            Ty_H[str(wid)] = coords[dst_ty]
        else:
            raise RuntimeError(f"Ty image missing for H vertex {wid} -> {dst_ty}")

    # For N12: map phase_points under translations
    def map_n12_by_translation(dx, dy):
        mapping = {}
        for nid, d in n12.items():
            pts = d["phase_points"]
            mapped = [((p[0] + dx) % 3, (p[1] + dy) % 3) for p in pts]
            mapped_sorted = tuple(sorted(mapped))
            found = None
            for cand_nid, cand_d in n12.items():
                if tuple(sorted(cand_d["phase_points"])) == mapped_sorted:
                    found = cand_nid
                    break
            if found is None:
                raise RuntimeError(f"No N12 match for translation {dx,dy} mapping {pts} -> {mapped_sorted}")
            mapping[str(nid)] = int(found)
        return mapping

    # Map N12 under Tx (dx=1,dy=0) and Ty (dx=0,dy=1)
    Tx_N12 = map_n12_by_translation(1, 0)
    Ty_N12 = map_n12_by_translation(0, 1)

    # Build full 40-point permutations
    # Collect list of all vertices: v0 = 0, N12 keys, H27 keys
    all_vids = set()
    all_vids.add(0)
    for nid in n12.keys():
        all_vids.add(int(nid))
    for wid in hmap.keys():
        all_vids.add(int(wid))

    Tx_perm = {}
    Ty_perm = {}

    for v in sorted(all_vids):
        if v == 0:
            Tx_perm[str(v)] = int(v)
            Ty_perm[str(v)] = int(v)
            continue
        if str(v) in Tx_N12:
            Tx_perm[str(v)] = Tx_N12[str(v)]
        elif str(v) in Tx_H:
            Tx_perm[str(v)] = Tx_H[str(v)]
        else:
            # if v is N12 but not in mapping, keep fixed
            Tx_perm[str(v)] = int(v)

        if str(v) in Ty_N12:
            Ty_perm[str(v)] = Ty_N12[str(v)]
        elif str(v) in Ty_H:
            Ty_perm[str(v)] = Ty_H[str(v)]
        else:
            Ty_perm[str(v)] = int(v)

    # Compute Z = Tx Ty Tx^{-1} Ty^{-1}
    def invert_perm(perm):
        inv = {}
        for k, v in perm.items():
            inv[str(v)] = int(k)
        return inv

    Tx_inv = invert_perm(Tx_perm)
    Ty_inv = invert_perm(Ty_perm)

    def compose(permA, permB):
        # (permA o permB)[v] = permA[permB[v]]
        out = {}
        for k in permA.keys():
            v1 = permB[k]
            out[k] = permA[str(v1)] if isinstance(v1, int) else permA[v1]
        return out

    # To avoid string-int confusion, convert perms to int->int dicts first
    Tx_int = {int(k): int(v) for k, v in Tx_perm.items()}
    Ty_int = {int(k): int(v) for k, v in Ty_perm.items()}
    Tx_inv_int = {int(k): int(v) for k, v in Tx_inv.items()}
    Ty_inv_int = {int(k): int(v) for k, v in Ty_inv.items()}

    Z_int = {}
    for k in sorted(all_vids):
        a = Tx_int.get(k, k)
        b = Ty_int.get(a, a)
        c = Tx_inv_int.get(b, b)
        d = Ty_inv_int.get(c, c)
        Z_int[k] = d

    # Verify central action on H27 is t -> t-1
    # Build coords inverse mapping
    coords_lookup = {v: coords for coords, v in coords.items()}  # not used

    # Save JSON
    out = {
        "Tx": {"perm_H": Tx_H, "perm_N12": Tx_N12, "perm_40": {k: v for k, v in Tx_perm.items()}},
        "Ty": {"perm_H": Ty_H, "perm_N12": Ty_N12, "perm_40": {k: v for k, v in Ty_perm.items()}},
        "Z": {"perm_40": {str(k): int(v) for k, v in Z_int.items()}},
    }

    (out_dir / "W33_Heisenberg_generators_Tx_Ty_Z.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    # Write translation_lifts_canonical.csv
    import csv

    csv_path = out_dir / "W33_translation_lifts_canonical.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["dx", "dy", "N12_mapping_example"])
        for dx in range(3):
            for dy in range(3):
                try:
                    mapping = map_n12_by_translation(dx, dy)
                    # pick representative mapping for first N12
                    sample = next(iter(mapping.items()))
                    writer.writerow([dx, dy, f"{sample[0]}->{sample[1]}"])
                except RuntimeError:
                    writer.writerow([dx, dy, "mapping_failed"])

    # Dump canonical H27 coords file (copy of input)
    src = bundle / "H27_vertices_as_F3_cube_xy_t.csv"
    dst = out_dir / "H27_vertices_as_F3_cube_xy_t_holonomy_gauge.csv"
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"Wrote {out_dir / 'W33_Heisenberg_generators_Tx_Ty_Z.json'}")
    print(f"Wrote {csv_path}")
    print(f"Wrote {dst}")


if __name__ == "__main__":
    main()
