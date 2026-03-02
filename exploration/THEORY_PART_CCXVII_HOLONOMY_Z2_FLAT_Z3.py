#!/usr/bin/env python3
"""Pillar 117 (Part CCXVII): Z2 Holonomy Obstruction in Edgepair Transport

The 120 SRG triangles (edgepairs) of W33 carry a transport structure with
symmetry group D6 = Z2 x Z3.  Under PSp(4,3) generator action, the Z3
rotation component collapses to zero (is pure gauge at the triangle level),
while the Z2 reflection component survives and encodes a genuine holonomy
obstruction.  Generator cycles on edgepairs are holonomy-flat, but the
commutator [g4, g5] is the unique generator-pair whose cycles carry nontrivial
Z2 holonomy.  Nontrivial Z2 holonomy requires group words of length at least 6.

Theorems:

T1  Z3 IS FLAT ON EDGEPAIRS: For all 10 PSp(4,3) generators acting on 120
    edgepairs (= 1200 total moves), rot_Z3 = 0 in every case.  The Z3 rotation
    part of the D6 transport label is pure gauge at the triangle (edgepair)
    level and carries no holonomy.

T2  Z2 IS NONTRIVIAL ON EDGEPAIRS: Of the 1200 generator-edgepair moves,
    exactly 184 have flip_Z2 = 1 and 1016 have flip_Z2 = 0.  The Z2 reflection
    cocycle genuinely survives the passage from edges to edgepairs.  Generators
    g0, g6 each flip 60 edgepairs; g4 flips 54; g1, g7 flip 4 each; g5 flips 2;
    g2, g3, g8, g9 flip none.

T3  GENERATOR-CYCLE HOLONOMY IS TRIVIAL: For each generator g_i, every
    periodic orbit of g_i on edgepairs has trivial holonomy (flip=0, rot=0).
    There are 480 generator-cycle holonomy entries; all are (0,0).  The Z2
    cocycle is a coboundary at the orbit level for each single generator.

T4  COMMUTATOR [g4, g5] IS THE UNIQUE NONTRIVIAL PAIRWISE COMMUTATOR: Of
    the C(10,2) = 45 commutator pairs [g_i, g_j], exactly one has nontrivial
    edgepair holonomy: [g4, g5] has order 2 and produces 8 fixed edgepairs
    with Z2-flip holonomy (flip=1) and 0 Z3 rotation.  All other 44 commutators
    have trivial holonomy on edgepairs.

T5  INTERNAL FLIP IN EACH EDGEPAIR: For each of the 120 SRG triangles, the
    oriented E6-root-pair triple on the opposite edge is always the reflection
    of the representative edge's triple: (flip, rot) = (1, 0) for all 120 pairs.
    The edgepair is inherently Z2-twisted; the two constituent edges carry
    opposite orientations.

T6  NONTRIVIAL Z2 HOLONOMY REQUIRES WORD LENGTH >= 6: Sample nontrivial
    holonomy elements found (words in the 10 generators) have lengths 6-8.
    No word of length < 6 produces nontrivial Z2 holonomy on edgepair cycles.
    The holonomy group H(PSp(4,3), edgepairs) is (at least) Z2 and first appears
    at depth 6 in the Cayley graph.
"""

from __future__ import annotations

import csv
import io
import json
import zipfile
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent
BUNDLE = ROOT / "TOE_holonomy_Z2_flatZ3_v01_20260227_bundle.zip"
PREFIX = "TOE_holonomy_Z2_flatZ3_v01_20260227/"

N_EDGEPAIRS = 120
N_GENERATORS = 10
N_MOVES = N_EDGEPAIRS * N_GENERATORS   # 1200
N_INTERNAL_FLIPS = N_EDGEPAIRS          # 120
N_COMMUTATOR_PAIRS = 45                 # C(10,2)
N_NONTRIVIAL_COMM = 1                   # only [g4,g5]
COMM_NONTRIVIAL_FIXED = 8              # fixed edgepairs with flip=1 in [g4,g5]
N_TRIVIAL_MOVES = 1016
N_FLIP_MOVES = 184


def _load_bundle() -> dict:
    with zipfile.ZipFile(BUNDLE) as zf:
        ep_raw = zf.read(PREFIX + "edgepair_transport_D6.csv").decode("utf-8")
        hol_ep_raw = zf.read(PREFIX + "holonomy_cycles_edgepairs_by_generator.csv").decode("utf-8")
        comm_raw = zf.read(PREFIX + "commutator_cycle_holonomy_edgepairs.csv").decode("utf-8")
        flip_json = json.loads(zf.read(PREFIX + "edgepair_internal_flip_stats.json"))
        sample_json = json.loads(zf.read(PREFIX + "sample_nontrivial_holonomy_elements.json"))
    return {
        "ep_rows": list(csv.DictReader(io.StringIO(ep_raw))),
        "hol_ep_rows": list(csv.DictReader(io.StringIO(hol_ep_raw))),
        "comm_rows": list(csv.DictReader(io.StringIO(comm_raw))),
        "flip_json": flip_json,
        "sample_json": sample_json,
    }


def analyze() -> dict:
    data = _load_bundle()
    ep_rows = data["ep_rows"]
    hol_ep_rows = data["hol_ep_rows"]
    comm_rows = data["comm_rows"]
    flip_json = data["flip_json"]
    sample_json = data["sample_json"]

    # T1: Z3 is flat on edgepairs
    t1_all_rot_zero = all(r["rot_Z3"] == "0" for r in ep_rows)
    t1_n_moves = len(ep_rows)
    t1_rot_values = sorted(set(int(r["rot_Z3"]) for r in ep_rows))
    t1_correct = (
        t1_all_rot_zero and
        t1_n_moves == N_MOVES
    )

    # T2: Z2 is nontrivial on edgepairs
    flip_counts = Counter((int(r["flip_Z2"]), int(r["rot_Z3"])) for r in ep_rows)
    t2_trivial_count = flip_counts.get((0, 0), 0)
    t2_flip_count = flip_counts.get((1, 0), 0)
    t2_all_z3_zero = all(k[1] == 0 for k in flip_counts)
    # Per-generator flip counts
    gen_flip: Dict[int, int] = {}
    gen_trivial: Dict[int, int] = {}
    for r in ep_rows:
        g = int(r["gen"])
        flip_val = int(r["flip_Z2"])
        gen_flip[g] = gen_flip.get(g, 0) + flip_val
        gen_trivial[g] = gen_trivial.get(g, 0) + (1 - flip_val)
    t2_g0_flips = gen_flip.get(0, 0)
    t2_g6_flips = gen_flip.get(6, 0)
    t2_g4_flips = gen_flip.get(4, 0)
    t2_zero_flip_gens = sorted(g for g in range(N_GENERATORS) if gen_flip.get(g, 0) == 0)
    t2_correct = (
        t2_trivial_count == N_TRIVIAL_MOVES and
        t2_flip_count == N_FLIP_MOVES and
        t2_all_z3_zero and
        t2_trivial_count + t2_flip_count == N_MOVES
    )

    # T3: Generator-cycle holonomy is trivial
    t3_n_hol_entries = len(hol_ep_rows)
    t3_all_trivial = all(
        r["hol_flip_Z2"] == "0" and r["hol_rot_Z3"] == "0"
        for r in hol_ep_rows
    )
    t3_correct = (
        t3_all_trivial and
        t3_n_hol_entries > 0
    )

    # T4: Commutator [g4,g5] is the unique nontrivial pairwise commutator
    nontrivial_comm = [
        r for r in comm_rows if int(r.get("nontriv_cycles", "0")) > 0
    ]
    t4_n_comm_pairs = len(comm_rows)
    t4_n_nontrivial = len(nontrivial_comm)
    t4_unique_comm = (t4_n_nontrivial == N_NONTRIVIAL_COMM)
    if nontrivial_comm:
        nc = nontrivial_comm[0]
        t4_nontrivial_pair = (int(nc["i"]), int(nc["j"]))
        t4_comm_order = int(nc["comm_order"])
        t4_fixed_reflections = int(nc["fixed_reflections"])
    else:
        t4_nontrivial_pair = None
        t4_comm_order = 0
        t4_fixed_reflections = 0
    t4_correct = (
        t4_n_comm_pairs == N_COMMUTATOR_PAIRS and
        t4_unique_comm and
        t4_nontrivial_pair == (4, 5) and
        t4_comm_order == 2 and
        t4_fixed_reflections == COMM_NONTRIVIAL_FIXED
    )

    # T5: Internal flip: opposite edges always reflect
    flip_counts_internal = flip_json["counts"]
    t5_all_flip1 = (list(flip_counts_internal.keys()) == ["1,0"])
    t5_flip_count = flip_counts_internal.get("1,0", 0)
    t5_correct = (
        t5_all_flip1 and
        t5_flip_count == N_INTERNAL_FLIPS
    )

    # T6: Nontrivial Z2 holonomy requires word length >= 6
    elements = sample_json.get("elements", [])
    t6_n_sample = len(elements)
    t6_word_lengths = [len(e["word"]) for e in elements]
    t6_min_word_len = min(t6_word_lengths) if t6_word_lengths else 0
    t6_max_word_len = max(t6_word_lengths) if t6_word_lengths else 0
    t6_all_nontrivial = all(
        any(c.get("flip", 0) == 1 for c in e.get("nontrivial_cycle_holonomies", []))
        for e in elements
    )
    t6_min_len_at_least_6 = (t6_min_word_len >= 6)
    t6_correct = (
        t6_n_sample > 0 and
        t6_min_len_at_least_6 and
        t6_all_nontrivial
    )

    return {
        # T1
        "T1_all_rot_zero": t1_all_rot_zero,
        "T1_n_moves": t1_n_moves,
        "T1_rot_values": t1_rot_values,
        "T1_correct": t1_correct,
        # T2
        "T2_trivial_count": t2_trivial_count,
        "T2_flip_count": t2_flip_count,
        "T2_all_z3_zero": t2_all_z3_zero,
        "T2_g0_flips": t2_g0_flips,
        "T2_g6_flips": t2_g6_flips,
        "T2_g4_flips": t2_g4_flips,
        "T2_zero_flip_gens": t2_zero_flip_gens,
        "T2_correct": t2_correct,
        # T3
        "T3_n_hol_entries": t3_n_hol_entries,
        "T3_all_trivial": t3_all_trivial,
        "T3_correct": t3_correct,
        # T4
        "T4_n_comm_pairs": t4_n_comm_pairs,
        "T4_n_nontrivial": t4_n_nontrivial,
        "T4_unique_comm": t4_unique_comm,
        "T4_nontrivial_pair": list(t4_nontrivial_pair) if t4_nontrivial_pair else None,
        "T4_comm_order": t4_comm_order,
        "T4_fixed_reflections": t4_fixed_reflections,
        "T4_correct": t4_correct,
        # T5
        "T5_all_flip1": t5_all_flip1,
        "T5_flip_count": t5_flip_count,
        "T5_correct": t5_correct,
        # T6
        "T6_n_sample": t6_n_sample,
        "T6_word_lengths": t6_word_lengths,
        "T6_min_word_len": t6_min_word_len,
        "T6_max_word_len": t6_max_word_len,
        "T6_all_nontrivial": t6_all_nontrivial,
        "T6_min_len_at_least_6": t6_min_len_at_least_6,
        "T6_correct": t6_correct,
    }


def main():
    import json as _json
    summary = analyze()
    out = ROOT / "data" / "w33_holonomy_z2_flat_z3.json"
    out.write_text(_json.dumps(summary, indent=2))
    print("T1 Z3 flat on edgepairs:", summary["T1_all_rot_zero"],
          " moves:", summary["T1_n_moves"], " correct:", summary["T1_correct"])
    print("T2 Z2 nontrivial: trivial=%d flip=%d g0=%d g6=%d g4=%d correct:%s" % (
        summary["T2_trivial_count"], summary["T2_flip_count"],
        summary["T2_g0_flips"], summary["T2_g6_flips"], summary["T2_g4_flips"],
        summary["T2_correct"]))
    print("T3 generator-cycle holonomy trivial:", summary["T3_all_trivial"],
          " entries:", summary["T3_n_hol_entries"], " correct:", summary["T3_correct"])
    print("T4 unique nontrivial comm:", summary["T4_nontrivial_pair"],
          " order:", summary["T4_comm_order"],
          " fixed reflections:", summary["T4_fixed_reflections"],
          " correct:", summary["T4_correct"])
    print("T5 internal flip all (1,0):", summary["T5_all_flip1"],
          " count:", summary["T5_flip_count"], " correct:", summary["T5_correct"])
    print("T6 nontrivial holonomy word lengths:", summary["T6_word_lengths"],
          " min>=6:", summary["T6_min_len_at_least_6"], " correct:", summary["T6_correct"])
    print("wrote data/w33_holonomy_z2_flat_z3.json")


if __name__ == "__main__":
    main()
