#!/usr/bin/env python3
"""Pillar 105 (Part CCV): Tomotope-Axis Complementary Block Duality

Both the tomotope (f-vector 4,12,16,8) and the axis-192 model (f-vector
1,16,12,4) share the SAME 48 blocks: the orbits of <r0,r3> on the 192
flags, each of size 4.  The two models partition these 48 blocks into
edge-groups and face-groups in a complementary (dual) fashion.

Theorems:

T1  COMMON SKELETON: The 48 <r0,r3>-orbits are blocks of size 4 common
    to both the tomotope and axis flag models.  They equal the 48
    (tomotope-edge, tomotope-face) incidence pairs.  The block partition
    is independent of the r1,r2 generators.

T2  COMPLEMENTARY PARTITION NUMBERS:
      Tomotope: 12 edges x 4 blocks/edge, 16 faces x 3 blocks/face
      Axis:     16 edges x 3 blocks/edge, 12 faces x 4 blocks/face
    The number of blocks per edge in one model equals the number of
    edge-features in the other model, and vice versa.  This is an exact
    complementary duality: (12,4,16,3) <-> (16,3,12,4).

T3  TOMOTOPE-EDGE PARTITION: Each of the 12 tomotope edges contains
    exactly 4 blocks.  The 12 x 4 = 48 partition is exact (no block
    appears in two tomotope edges).

T4  TOMOTOPE-FACE PARTITION: Each of the 16 tomotope faces contains
    exactly 3 blocks.  The 16 x 3 = 48 partition is exact.

T5  AXIS-EDGE PARTITION: Each of the 16 axis edges contains exactly
    3 blocks.  The 16 x 3 = 48 partition is exact.

T6  AXIS-FACE PARTITION: Each of the 12 axis faces contains exactly
    4 blocks.  The 12 x 4 = 48 partition is exact.
"""

from __future__ import annotations

import csv
import io
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set

ROOT = Path(__file__).resolve().parent
BUNDLE = ROOT / "TOE_tomotope_axis_block_twist_v02_20260228_bundle.zip"
BDIR = "TOE_tomotope_axis_block_twist_v02_20260228/"


def _load_bundle() -> dict:
    with zipfile.ZipFile(BUNDLE) as zf:
        summary = json.loads(zf.read(BDIR + "SUMMARY.json"))
        bpt_e = json.loads(zf.read(BDIR + "blocks_per_tomotope_edge.json"))
        bpt_f = json.loads(zf.read(BDIR + "blocks_per_tomotope_face.json"))
        bpa_e = json.loads(zf.read(BDIR + "blocks_per_axis_edge16.json"))
        bpa_f = json.loads(zf.read(BDIR + "blocks_per_axis_face12.json"))
        blocks_txt = zf.read(BDIR + "blocks48_labeled_by_tomotope_edge_face.csv").decode()
        flags_txt = zf.read(BDIR + "flag_coordinates_tomotope_vs_axis.csv").decode()
    return {
        "summary": summary,
        "bpt_e": bpt_e,
        "bpt_f": bpt_f,
        "bpa_e": bpa_e,
        "bpa_f": bpa_f,
        "blocks48": list(csv.DictReader(io.StringIO(blocks_txt))),
        "flags192": list(csv.DictReader(io.StringIO(flags_txt))),
    }


def _check_partition(partition: Dict[str, List[int]], expected_size: int) -> dict:
    """Verify a partition of the 48 blocks."""
    n_parts = len(partition)
    sizes = [len(v) for v in partition.values()]
    size_dist = dict(sorted(Counter(sizes).items()))
    all_blocks = [b for v in partition.values() for b in v]
    all_blocks_set = set(all_blocks)
    covers_all = all_blocks_set == set(range(48))
    disjoint = len(all_blocks) == len(all_blocks_set)
    exact = all(s == expected_size for s in sizes)
    return {
        "n_parts": n_parts,
        "size_dist": size_dist,
        "covers_all_48": covers_all,
        "disjoint": disjoint,
        "exact_size": exact,
        "expected_size": expected_size,
    }


def analyze() -> dict:
    data = _load_bundle()
    summary = data["summary"]
    bpt_e = data["bpt_e"]
    bpt_f = data["bpt_f"]
    bpa_e = data["bpa_e"]
    bpa_f = data["bpa_f"]
    blocks48 = data["blocks48"]
    flags192 = data["flags192"]

    # T1: Common skeleton — verify 48 blocks of size 4
    block_sizes = Counter(int(b["size"]) for b in blocks48)
    t1_num_blocks = len(blocks48)
    t1_block_size_dist = dict(sorted(block_sizes.items()))
    t1_all_size_4 = all(int(b["size"]) == 4 for b in blocks48)

    # Check blocks are labeled by (tE, tF) pairs = incidence pairs
    te_tf_pairs = [(int(b["tE"]), int(b["tF"])) for b in blocks48]
    t1_all_pairs_unique = len(set(te_tf_pairs)) == 48

    # T2: Summary of complementary duality
    tomo_e_count = len(bpt_e)   # 12
    tomo_e_size = len(list(bpt_e.values())[0])   # 4
    tomo_f_count = len(bpt_f)   # 16
    tomo_f_size = len(list(bpt_f.values())[0])   # 3
    axis_e_count = len(bpa_e)   # 16
    axis_e_size = len(list(bpa_e.values())[0])   # 3
    axis_f_count = len(bpa_f)   # 12
    axis_f_size = len(list(bpa_f.values())[0])   # 4
    t2_complementary = (
        tomo_e_size == axis_f_size and tomo_f_size == axis_e_size
        and tomo_e_count == axis_f_count and tomo_f_count == axis_e_count
    )

    # T3: Tomotope-edge partition
    t3 = _check_partition(bpt_e, expected_size=4)

    # T4: Tomotope-face partition
    t4 = _check_partition(bpt_f, expected_size=3)

    # T5: Axis-edge partition
    t5 = _check_partition(bpa_e, expected_size=3)

    # T6: Axis-face partition
    t6 = _check_partition(bpa_f, expected_size=4)

    # Cross-check: block membership
    # Each block should appear in exactly one tomotope edge and one tomotope face
    block_in_te: Dict[int, List[int]] = defaultdict(list)
    block_in_tf: Dict[int, List[int]] = defaultdict(list)
    for te, blocks in bpt_e.items():
        for b in blocks:
            block_in_te[b].append(int(te))
    for tf, blocks in bpt_f.items():
        for b in blocks:
            block_in_tf[b].append(int(tf))
    te_membership = all(len(v) == 1 for v in block_in_te.values())
    tf_membership = all(len(v) == 1 for v in block_in_tf.values())

    # f-vectors from summary
    tomo_fvec = summary["tomotope_counts"]
    axis_fvec = summary["axis_counts"]

    return {
        "T1_num_blocks": t1_num_blocks,
        "T1_block_size_dist": t1_block_size_dist,
        "T1_all_size_4": t1_all_size_4,
        "T1_all_incidence_pairs_unique": t1_all_pairs_unique,
        "T2_tomotope_fvec": tomo_fvec,
        "T2_axis_fvec": axis_fvec,
        "T2_complementary_duality": t2_complementary,
        "T2_tomo_edges_times_blocks": tomo_e_count * tomo_e_size,
        "T2_tomo_faces_times_blocks": tomo_f_count * tomo_f_size,
        "T2_axis_edges_times_blocks": axis_e_count * axis_e_size,
        "T2_axis_faces_times_blocks": axis_f_count * axis_f_size,
        "T3_tomotope_edge_partition": t3,
        "T4_tomotope_face_partition": t4,
        "T5_axis_edge_partition": t5,
        "T6_axis_face_partition": t6,
        "cross_check_te_membership_unique": te_membership,
        "cross_check_tf_membership_unique": tf_membership,
    }


def main():
    summary = analyze()
    out = ROOT / "data" / "w33_axis_tomotope_block_duality.json"
    out.write_text(json.dumps(summary, indent=2))
    print("T1 all blocks size 4:", summary["T1_all_size_4"])
    print("T2 complementary duality:", summary["T2_complementary_duality"])
    print("T3 tomotope-edge exact:", summary["T3_tomotope_edge_partition"]["exact_size"])
    print("T4 tomotope-face exact:", summary["T4_tomotope_face_partition"]["exact_size"])
    print("T5 axis-edge exact:", summary["T5_axis_edge_partition"]["exact_size"])
    print("T6 axis-face exact:", summary["T6_axis_face_partition"]["exact_size"])
    print("wrote data/w33_axis_tomotope_block_duality.json")


if __name__ == "__main__":
    main()
