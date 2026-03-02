#!/usr/bin/env python3
"""Generate explicit 54-sheet coordinate model and lift to tomotope flags.

This script reads:
  * edges_270_transport.csv (contains u,qid,twin_bit and block_guess)
  * K54_node_labels_L.csv (L values for pockets)
  * block_to_pockets.json (mapping of 48 axis blocks to pocket lists)
  * axis bundle blocks48_r0r3.json (flags in each of 48 blocks)

It produces:
  * K54_54sheet_coords.csv  -- one row per pocket with (qid,twin,L,...)
  * pocket_to_flags.json    -- lists of candidate tomotope flags for each pocket
  * canonical_flag_block.csv-- canonical flag and block for each pocket
  * SUMMARY_54sheet.json     -- counts and diagnostics

Bundle: TOE_54sheet_model_v01_20260228_bundle.zip
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parent

CSV_270 = ROOT / "edges_270_transport.csv"
CSV_L = ROOT / "K54_node_labels_L.csv"
BLOCK2POCKET = ROOT / "block_to_pockets.json"
AXIS_BLOCKS = ROOT / "axis_bundle_content" / "TOE_tomotope_axis_block_twist_v02_20260228" / "blocks48_r0r3.json"

OUT_COORD = ROOT / "K54_54sheet_coords.csv"
OUT_FLAGMAP = ROOT / "pocket_to_flags.json"
OUT_CANON = ROOT / "canonical_flag_block.csv"
OUT_SUM = ROOT / "SUMMARY_54sheet.json"
BUNDLE = "TOE_54sheet_model_v01_20260228_bundle.zip"


def load_L():
    L = []
    with open(CSV_L) as f:
        for r in csv.DictReader(f):
            L.append(int(r["L"]))
    return L


def load_270():
    payload = {}
    guesses = defaultdict(list)
    with open(CSV_270) as f:
        for r in csv.DictReader(f):
            u = int(r["u"])
            payload.setdefault(u, {})
            payload[u]["qid"] = int(r["qid"])
            payload[u]["twin_bit"] = int(r["twin_bit"])
            gu = int(r.get("block_guess", -1))
            guesses[u].append(gu)
    # turn guesses into sorted unique list
    for u,gl in guesses.items():
        guesses[u] = sorted(set(gl))
    return payload, guesses


def invert_block_map():
    b2p = json.load(open(BLOCK2POCKET))
    p2b = defaultdict(list)
    for b,pl in b2p.items():
        bi = int(b)
        for p in pl:
            p2b[p].append(bi)
    return p2b


def make_flag_map(p2b):
    data = json.load(open(AXIS_BLOCKS))
    orbits = data["orbits"]
    # pocket -> set(flags)
    p2f = defaultdict(list)
    for bi,flags in enumerate(orbits):
        for f in flags:
            # assign this flag to every pocket in block bi
            for p in p2b.get(bi, []):
                p2f[p].append(f)
    # deduplicate and sort
    for p,fl in list(p2f.items()):
        p2f[p] = sorted(set(fl))
    return p2f, orbits


def main():
    L = load_L()
    coords, guesses = load_270()
    p2b = invert_block_map()
    p2f, orbits = make_flag_map(p2b)

    entries = []
    diagnostics = {
        "missing_L": [],
        "missing_coords": [],
        "blocks_per_pocket": {},
        "guesses_not_in_actual": {},
        "guess_to_actual_flag_counts": {}
    }
    for u in range(54):
        if u not in coords:
            diagnostics["missing_coords"].append(u)
            continue
        q = coords[u]["qid"]
        t = coords[u]["twin_bit"]
        Lu = L[u] if u < len(L) else None
        if Lu is None:
            diagnostics["missing_L"].append(u)
        actual_blocks = sorted(p2b.get(u, []))
        diagnostics["blocks_per_pocket"][u] = actual_blocks
        guess_list = guesses.get(u, [])
        # check if all guesses appear in actual_blocks
        not_in = [g for g in guess_list if g not in actual_blocks]
        if not_in:
            diagnostics["guesses_not_in_actual"][u] = not_in
        flags = p2f.get(u, [])
        cannon = min(flags) if flags else None
        canblock = None
        if cannon is not None:
            # determine which block contains this flag
            for bi,fl in enumerate(orbits):
                if cannon in fl:
                    canblock = bi
                    break
        # record mapping from each guess to this canonical flag if guess is actual
        for g in guess_list:
            if g in actual_blocks and cannon is not None:
                diagnostics["guess_to_actual_flag_counts"].setdefault(str(g), []).append(cannon)
        entries.append({
            "pocket": u,
            "qid": q,
            "twin_bit": t,
            "L": Lu,
            "canonical_flag": cannon,
            "canonical_block": canblock,
            "actual_blocks": ";".join(str(b) for b in actual_blocks),
            "block_guesses": ";".join(str(g) for g in guess_list)
        })
    # write outputs
    with open(OUT_COORD, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=entries[0].keys())
        w.writeheader(); w.writerows(entries)
    with open(OUT_FLAGMAP, "w") as f:
        json.dump(p2f, f, indent=2)
    with open(OUT_CANON, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["pocket","flag","block"])
        for e in entries:
            w.writerow([e["pocket"], e["canonical_flag"], e["canonical_block"]])
    # compute t^4 cycles on canonical flags and correlate with L phases
    try:
        import zipfile
        zf = zipfile.ZipFile(ROOT / "TOE_tomotope_true_flag_model_v02_20260228_bundle.zip")
        rgens = json.loads(zf.read("tomotope_r_generators_192.json"))
        r1 = tuple(rgens["r1"]); r2 = tuple(rgens["r2"])
        def comp(p,q): return tuple(p[q[i]] for i in range(len(p)))
        t = comp(r1, r2)
        n = 192
        idn = tuple(range(n))
        cur = idn
        for _ in range(4): cur = comp(t, cur)
        t4 = cur
        # build flag->pocket map from entries
        f2p = {e["canonical_flag"]: e["pocket"] for e in entries if e["canonical_flag"] is not None}
        cycle_counts = {}
        for e in entries:
            f = e["canonical_flag"]
            if f is None: continue
            length = 1
            x = f
            while True:
                x = t4[x]
                if x == f: break
                length += 1
            key = (length, e["L"])
            cycle_counts[key] = cycle_counts.get(key, 0) + 1
        # convert tuple keys to strings for JSON serialization
        diagnostics["canonical_flag_t4_cycle_vs_L"] = {f"{k}": v for k,v in cycle_counts.items()}
    except Exception as exc:
        diagnostics["canonical_flag_t4_cycle_vs_L"] = {"error": str(exc)}

    with open(OUT_SUM, "w") as f:
        # convert lists to counts for guess map
        for k,v in diagnostics["guess_to_actual_flag_counts"].items():
            diagnostics["guess_to_actual_flag_counts"][k] = {
                "count": len(v),
                "flags": sorted(set(v))
            }
        json.dump(diagnostics, f, indent=2)
    # bundle
    import zipfile
    with zipfile.ZipFile(BUNDLE, "w") as bz:
        for fn in (OUT_COORD, OUT_FLAGMAP, OUT_CANON, OUT_SUM):
            bz.write(str(fn), fn.name)
    print("wrote 54-sheet model and bundle", BUNDLE)

if __name__ == '__main__':
    main()
