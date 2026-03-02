#!/usr/bin/env python3
"""Pillar 104 (Part CCIV): 27x10 Heisenberg-Orient Quotient of K-Schreier Graph

The 270 directed K-Schreier edges admit a canonical Z_27 x Z_10 coordinate
system: the first axis indexes the 27 Heisenberg qids (twin-pair orbits of
the 54 K-pockets under the Heisenberg subgroup [K,K]), and the second axis
indexes the 10 oriented half-edges per qid (5 generators x 2 twin-bits).

The 27x10 table exposes structural properties invisible in the raw 54-pocket
or 270-edge presentations.

Theorems:

T1  BIJECTIVITY: The map (u, g) -> (qid[u], orient_index) is a bijection
    from the 270 directed K-Schreier edges to Z_27 x Z_10.  Every (qid,
    orient) pair occurs exactly once.

T2  ORIENT SPLIT: Orient indices 0-4 correspond to twin_bit=0 pockets
    (source pocket of qid) with generators g2,g3,g5,g8,g9 in that order.
    Orient indices 5-9 correspond to twin_bit=1 pockets, same generator
    order.  The 270 = 27*5*2 decomposition is (qid x gen x twin_bit).

T3  FIXED TRIO: Exactly 3 qids (the fixed trio) are fixed by generators
    g8 and g9: both g8 and g9 map each fixed-trio pocket back to its own
    qid (self-loops in the qid graph).  The fixed trio is {13, 14, 26}.
    These match the tritangent-clique qids from Pillar 102.

T4  COCYCLE ASYMMETRY: Generators g8 and g9 from twin_bit=0 pockets have
    ALL trivial cocycle (27 out of 27 edges each), while from twin_bit=1
    pockets they have 6 non-trivial edges each.  In contrast, generators
    g2, g3, g5 have non-trivial cocycles on both twin_bit=0 and twin_bit=1.
    Total non-trivial edges: (g8,tb0)=0, (g9,tb0)=0 vs (g8,tb1)=6,
    (g9,tb1)=6 — a Z2 twin-bit symmetry breaking for the diagonal generators.

T5  SHEET EQUIDISTRIBUTION: All 6 sheets receive exactly 45 = 270/6
    directed edges.  The sheet label is equidistributed across the 270
    (qid, orient) cells.

T6  L-LABEL SPLIT: The L-label (C3 sheet gauge from Pillar 103) of source
    pocket u distributes as {0:13, 1:4, 2:10} for twin_bit=0 pockets and
    {0:4, 1:7, 2:16} for twin_bit=1 pockets.  Their sum {0:17, 1:11, 2:26}
    recovers the global L-distribution of Pillar 103 T1.  The twin_bit=1
    distribution is shifted toward c^2 (label 2), consistent with g3 being
    the unique sheet-rotating generator (s_g[g3]=2 from Pillar 103 T3).
"""

from __future__ import annotations

import csv
import io
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent
BUNDLE_27x10 = ROOT / "TOE_27x10_quotient_v01_20260228_bundle.zip"
BUNDLE_TRANSPORT = ROOT / "TOE_S3_SHEET_TRANSPORT_v01_20260228_bundle.zip"

_C3_MAP = {(0, 1, 2): 0, (1, 2, 0): 1, (2, 0, 1): 2}

GENERATORS = ["g2", "g3", "g5", "g8", "g9"]
FIXED_TRIO_EXPECTED = {13, 14, 26}


def _load_edges() -> List[dict]:
    with zipfile.ZipFile(BUNDLE_27x10) as zf:
        text = zf.read("edges_27x10.csv").decode()
    return list(csv.DictReader(io.StringIO(text)))


def _load_L() -> List[int]:
    with zipfile.ZipFile(BUNDLE_TRANSPORT) as zf:
        L_raw = json.loads(zf.read("L_table.json"))
    return [_C3_MAP[tuple(x)] for x in L_raw]


def analyze() -> dict:
    rows = _load_edges()
    L = _load_L()

    # T1: Bijectivity
    pairs = [(int(r["qid"]), int(r["orient_index"])) for r in rows]
    pair_set = set(pairs)
    t1_total = len(pairs)
    t1_unique = len(pair_set)
    t1_expected = set((q, o) for q in range(27) for o in range(10))
    t1_bijective = pair_set == t1_expected

    # T2: Orient split
    orient_twin = {}
    orient_gen = {}
    for r in rows:
        o = int(r["orient_index"])
        orient_twin[o] = int(r["twin_bit"])
        orient_gen[o] = r["gen"]
    # check consistency
    orient_twin_consistent = all(
        orient_twin[int(r["orient_index"])] == int(r["twin_bit"]) for r in rows
    )
    orient_gen_consistent = all(
        orient_gen[int(r["orient_index"])] == r["gen"] for r in rows
    )
    t2_tb0_orients = sorted(o for o, tb in orient_twin.items() if tb == 0)
    t2_tb1_orients = sorted(o for o, tb in orient_twin.items() if tb == 1)
    t2_gen_order_tb0 = [orient_gen[o] for o in t2_tb0_orients]
    t2_gen_order_tb1 = [orient_gen[o] for o in t2_tb1_orients]

    # T3: Fixed trio — qids fixed by both g8 and g9
    self_loop_qids: Dict[int, set] = defaultdict(set)
    for r in rows:
        if r["qid"] == r["target_qid"]:
            self_loop_qids[int(r["qid"])].add(r["gen"])
    fixed_trio = {
        qid for qid, gens in self_loop_qids.items()
        if "g8" in gens and "g9" in gens
    }
    t3_fixed_trio_correct = fixed_trio == FIXED_TRIO_EXPECTED
    t3_self_loop_count = sum(1 for r in rows if r["qid"] == r["target_qid"])
    t3_self_loop_gen_dist = dict(
        sorted(Counter(r["gen"] for r in rows if r["qid"] == r["target_qid"]).items())
    )

    # T4: Cocycle asymmetry per (gen, twin_bit)
    gen_twin_nontrivial: Dict[Tuple[str, int], int] = {}
    gen_twin_dist: Dict[Tuple[str, int], dict] = {}
    for gen in GENERATORS:
        for tb in (0, 1):
            subset = [r for r in rows if r["gen"] == gen and int(r["twin_bit"]) == tb]
            cocycles = Counter(int(r["cocycle_Z3_exp"]) for r in subset)
            gen_twin_nontrivial[(gen, tb)] = sum(v for k, v in cocycles.items() if k != 0)
            gen_twin_dist[(gen, tb)] = dict(sorted(cocycles.items()))
    t4_g8_tb0_all_trivial = gen_twin_nontrivial[("g8", 0)] == 0
    t4_g9_tb0_all_trivial = gen_twin_nontrivial[("g9", 0)] == 0
    t4_g8_tb1_nontrivial = gen_twin_nontrivial[("g8", 1)]
    t4_g9_tb1_nontrivial = gen_twin_nontrivial[("g9", 1)]
    # Serialize with string keys for JSON
    t4_gen_twin_nontrivial = {
        f"{gen}_tb{tb}": v for (gen, tb), v in gen_twin_nontrivial.items()
    }
    t4_gen_twin_dist = {
        f"{gen}_tb{tb}": d for (gen, tb), d in gen_twin_dist.items()
    }

    # T5: Sheet equidistribution
    sheet_dist = dict(sorted(Counter(r["sheet_id"] for r in rows).items()))
    t5_sheets = set(sheet_dist.values())
    t5_equidistributed = len(t5_sheets) == 1 and 45 in t5_sheets

    # T6: L-label split by twin_bit
    L_dist_tb0 = dict(
        sorted(Counter(L[int(r["u"])] for r in rows if int(r["twin_bit"]) == 0 and int(r["orient_index"]) == 0).items())
    )
    L_dist_tb1 = dict(
        sorted(Counter(L[int(r["u"])] for r in rows if int(r["twin_bit"]) == 1 and int(r["orient_index"]) == 5).items())
    )
    # Merge: should recover {0:17, 1:11, 2:26}
    merged = Counter(L_dist_tb0) + Counter(L_dist_tb1)
    merged_dict = dict(sorted(merged.items()))
    t6_sum_recovers_pillar103 = merged_dict == {0: 17, 1: 11, 2: 26}

    return {
        "T1_total_edges": t1_total,
        "T1_unique_qid_orient_pairs": t1_unique,
        "T1_bijective": t1_bijective,
        "T2_orient_split_consistent": orient_twin_consistent and orient_gen_consistent,
        "T2_tb0_orient_indices": t2_tb0_orients,
        "T2_tb1_orient_indices": t2_tb1_orients,
        "T2_gen_order_tb0": t2_gen_order_tb0,
        "T2_gen_order_tb1": t2_gen_order_tb1,
        "T3_fixed_trio": sorted(fixed_trio),
        "T3_fixed_trio_correct": t3_fixed_trio_correct,
        "T3_self_loop_count": t3_self_loop_count,
        "T3_self_loop_gen_dist": t3_self_loop_gen_dist,
        "T4_g8_tb0_all_trivial": t4_g8_tb0_all_trivial,
        "T4_g9_tb0_all_trivial": t4_g9_tb0_all_trivial,
        "T4_g8_tb1_nontrivial": t4_g8_tb1_nontrivial,
        "T4_g9_tb1_nontrivial": t4_g9_tb1_nontrivial,
        "T4_gen_twin_nontrivial": t4_gen_twin_nontrivial,
        "T5_sheet_dist": sheet_dist,
        "T5_edges_per_sheet": 45,
        "T5_equidistributed": t5_equidistributed,
        "T6_L_dist_tb0": L_dist_tb0,
        "T6_L_dist_tb1": L_dist_tb1,
        "T6_L_merged": merged_dict,
        "T6_sum_recovers_pillar103": t6_sum_recovers_pillar103,
    }


def main():
    summary = analyze()
    out_path = ROOT / "data" / "w33_27x10_quotient.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print("T1 bijective:", summary["T1_bijective"])
    print("T3 fixed trio:", summary["T3_fixed_trio"], "correct:", summary["T3_fixed_trio_correct"])
    print("T4 g8/g9 tb0 all trivial:", summary["T4_g8_tb0_all_trivial"], summary["T4_g9_tb0_all_trivial"])
    print("T5 equidistributed:", summary["T5_equidistributed"])
    print("T6 sum recovers pillar103:", summary["T6_sum_recovers_pillar103"])
    print("wrote data/w33_27x10_quotient.json")


if __name__ == "__main__":
    main()
