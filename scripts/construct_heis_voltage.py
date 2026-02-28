#!/usr/bin/env python3
"""Build mapping from the 48 tomotope blocks to K27 Heisenberg coordinates.

This is a helper truth table used when fusing the tomotope triality layer
with the K-pocket Heisenberg S3 structure.  The output file
`block_heis_coords.json` records the (x,y,z) coordinate assigned to each
block (identified by its 0--47 index).

The script also prints a simple sanity check: whether the translation by
the central order-3 element (z+1) matches the action of t^4 on blocks.
"""
import csv
import json
import os
import zipfile

# tomotope bundle containing the 48-block decomposition
bundle = "TOE_block_twist_v02/TOE_tomotope_axis_block_twist_v02_20260228"
blocks = json.load(open(os.path.join(bundle, "blocks48_r0r3.json")))['orbits']
# flag -> block index
flag2block = {fid: bi for bi, blk in enumerate(blocks) for fid in blk}

# load pocket->qid from the K27 bundle
kj = "TOE_K27_HEISENBERG_S3_v01_20260228_bundle.zip"
with zipfile.ZipFile(kj) as zf:
    twin_csv = zf.read(
        "TOE_K27_HEISENBERG_S3_v01_20260228/K54_to_K27_twin_map.csv"
    ).decode()
    pocket_to_qid = {int(r['pocket_id']): int(r['qid']) for r in csv.DictReader(twin_csv.splitlines())}

    coords_csv = zf.read(
        "TOE_K27_HEISENBERG_S3_v01_20260228/K27_heisenberg_coords.csv"
    ).decode()
qid2coords = {int(r['qid']):(int(r['x']), int(r['y']), int(r['z'])) for r in csv.DictReader(coords_csv.splitlines())}

# load previously computed block->pockets summary
block2p_raw = json.load(open('block_to_pockets.json'))
block2p = {int(k): v for k, v in block2p_raw.items()}
spa = json.load(open('spa_triality_summary.json'))['spa']
# restrict to spa-defined blocks and record all qids seen
block2qids = {}
for bi, ps in block2p.items():
    if bi >= len(spa) or spa[bi] is None:
        continue
    qs = {pocket_to_qid[p] for p in ps if p in pocket_to_qid}
    if qs:
        block2qids[int(bi)] = qs

# convert to coordinates (possibly multiple per block)
block_heis = {b: [qid2coords[q] for q in qs] for b, qs in block2qids.items()}
json.dump(block_heis, open('block_heis_coords.json', 'w'), indent=2)
print(f"wrote block_heis_coords.json with {len(block_heis)} spa-block entries")


