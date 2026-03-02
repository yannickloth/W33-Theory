#!/usr/bin/env python3
"""Pillar 88 (Part CXCIV): 27x10 Heisenberg-Quotient of the K-Schreier Graph

Six theorems characterising the 27x10 quotient of the 270-edge K-Schreier
directed graph by the 27 Heisenberg twin-pairs, and its sheet distribution:

  T1  The 270 directed K-Schreier edges form a 27x10 array: 27 Heisenberg
      twin-pair rows (qid 0..26) x 10 oriented edge-types.  Orient-indices
      0..4 are outgoing from the twin_bit=0 pocket of each pair via generators
      g2,g3,g5,g8,g9; indices 5..9 are outgoing from twin_bit=1.  Every qid
      contributes exactly 10 edges; every orient-index has exactly 27 edges.
      Each of the 54 pockets appears as a source exactly 5 times.

  T2  All 5 generators are pair-stable on the Heisenberg twin-pairs:
      for every generator g and every qid, both twin_bit=0 and twin_bit=1
      pockets of the pair map to pockets in the SAME target twin-pair.
      Consequently each generator descends to a well-defined map on the
      27-node Heisenberg quotient graph.

  T3  Twin-bit flip pattern (outgoing from twin_bit=0):
      g2 never flips twin_bit (27/27 edges have target_twin=0);
      g3 and g5 each flip twin_bit in exactly 6 of 27 pairs;
      g8 and g9 each flip twin_bit in exactly 15 of 27 pairs.

  T4  Cocycle Z3 nontriviality splits by orientation: outgoing from
      twin_bit=0 pockets yields 24/135 nontrivial edges;
      outgoing from twin_bit=1 pockets yields 45/135 nontrivial.
      The total 69/270 nontrivial edges is thus unevenly distributed
      across the two twin orientations (24 vs 45 = ratio 8:15).

  T5  Generators g8 and g9 each produce exactly 6 self-loops in the
      quotient graph (12 total): these are twin-pair -> same twin-pair
      edges.  The 27-node quotient graph (closed-neighborhood, including
      self if a self-loop exists) has degree distribution {5:9, 6:6, 7:12}
      (weighted sum = 9*5+6*6+12*7 = 165).  The 6 pocket-sheets each
      contain exactly 9 of the 54 pockets (uniform distribution).

  T6  Twin-pair sheet assignment: exactly 7 of the 27 Heisenberg twin-
      pairs have both pockets on the SAME sheet (intra-sheet pairs);
      the remaining 20 pairs have their two pockets on DIFFERENT sheets
      (inter-sheet pairs).  This 7+20 = 27 partition is exact.
"""
from __future__ import annotations

import csv
import io
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT         = Path(__file__).resolve().parent
Q27_BUNDLE   = ROOT / "TOE_27x10_quotient_v01_20260228_bundle.zip"


def main() -> None:
    out: dict = {"status": "ok"}

    # ------------------------------------------------------------------ load
    with zipfile.ZipFile(Q27_BUNDLE) as zf:
        edges_csv = zf.read("edges_27x10.csv").decode("utf-8")
        table     = json.loads(zf.read("27x10_table.json"))

    edges = list(csv.DictReader(io.StringIO(edges_csv)))
    int_fields = ["u","qid","twin_bit","cocycle_Z3_exp","orient_index",
                  "target_qid","target_twin","v","sheet_id"]
    for e in edges:
        for k in int_fields:
            e[k] = int(e[k])

    # ==================================================================
    # T1: 27x10 table — 270 edges, 27 qids x 10 orient-indices each
    # ==================================================================
    assert len(edges) == 270, f"Total edges = {len(edges)}, expected 270"
    assert len(table) == 27, f"Table qid count = {len(table)}, expected 27"

    qid_counts = Counter(e["qid"] for e in edges)
    assert all(v == 10 for v in qid_counts.values()), (
        f"Not all qids have 10 edges: {dict(qid_counts)}"
    )
    orient_counts = Counter(e["orient_index"] for e in edges)
    assert all(v == 27 for v in orient_counts.values()), (
        f"Not all orient-indices have 27 edges: {dict(orient_counts)}"
    )
    # Each pocket appears as source exactly 5 times
    pocket_source_counts = Counter(e["u"] for e in edges)
    assert all(v == 5 for v in pocket_source_counts.values()), (
        "Not all pockets appear 5 times as source"
    )
    assert len(pocket_source_counts) == 54

    # Orient 0..4 are from twin_bit=0; 5..9 from twin_bit=1
    for oi in range(5):
        tbs = Counter(e["twin_bit"] for e in edges if e["orient_index"] == oi)
        assert set(tbs.keys()) == {0}, f"orient {oi} not all from twin_bit=0"
    for oi in range(5, 10):
        tbs = Counter(e["twin_bit"] for e in edges if e["orient_index"] == oi)
        assert set(tbs.keys()) == {1}, f"orient {oi} not all from twin_bit=1"

    out["T1_total_edges"]          = 270
    out["T1_qid_count"]            = 27
    out["T1_orient_count"]         = 10
    out["T1_edges_per_qid"]        = 10
    out["T1_edges_per_orient"]     = 27
    out["T1_sources_per_pocket"]   = 5
    out["T1_orient_0_4_from_twin0"] = True
    out["T1_orient_5_9_from_twin1"] = True
    print("T1: 27x10 table: 270 edges = 27 qids x 10 orient-indices; each pocket source 5x  OK")

    # ==================================================================
    # T2: All 5 generators are pair-stable
    # ==================================================================
    gen_names = ["g2", "g3", "g5", "g8", "g9"]
    gen_stable: dict = {}
    for g in gen_names:
        g_edges = [e for e in edges if e["gen"] == g]
        by_qid: dict[int, set] = defaultdict(set)
        for e in g_edges:
            by_qid[e["qid"]].add(e["target_qid"])
        all_stable = all(len(v) == 1 for v in by_qid.values())
        gen_stable[g] = all_stable
        assert all_stable, f"Generator {g} is NOT pair-stable!"

    assert all(gen_stable.values())

    out["T2_all_generators_pair_stable"] = True
    out["T2_gen_stable"]                 = gen_stable
    print("T2: All 5 generators (g2,g3,g5,g8,g9) are pair-stable on 27 Heisenberg pairs  OK")

    # ==================================================================
    # T3: Twin-bit flip pattern (outgoing from twin_bit=0)
    # ==================================================================
    flip_counts: dict = {}
    for g in gen_names:
        g_out = [e for e in edges if e["gen"] == g and e["orient_index"] < 5]
        assert len(g_out) == 27, f"{g} outgoing count = {len(g_out)}"
        flips = sum(1 for e in g_out if e["twin_bit"] != e["target_twin"])
        flip_counts[g] = flips

    assert flip_counts["g2"] == 0,  f"g2 flips = {flip_counts['g2']}, expected 0"
    assert flip_counts["g3"] == 6,  f"g3 flips = {flip_counts['g3']}, expected 6"
    assert flip_counts["g5"] == 6,  f"g5 flips = {flip_counts['g5']}, expected 6"
    assert flip_counts["g8"] == 15, f"g8 flips = {flip_counts['g8']}, expected 15"
    assert flip_counts["g9"] == 15, f"g9 flips = {flip_counts['g9']}, expected 15"

    out["T3_flip_counts"] = flip_counts
    out["T3_g2_no_flip"]  = True
    out["T3_g3_g5_flip_6"] = True
    out["T3_g8_g9_flip_15"] = True
    print(
        "T3: Twin-bit flips (outgoing): g2=0, g3=6, g5=6, g8=15, g9=15 (of 27 each)  OK"
    )

    # ==================================================================
    # T4: Cocycle nontriviality split by orientation (twin_bit=0 vs 1)
    # ==================================================================
    out_edges = [e for e in edges if e["orient_index"] < 5]    # twin_bit=0 outgoing
    in_edges  = [e for e in edges if e["orient_index"] >= 5]   # twin_bit=1 outgoing

    out0_nontriv = sum(1 for e in out_edges if e["cocycle_Z3_exp"] != 0)
    out1_nontriv = sum(1 for e in in_edges  if e["cocycle_Z3_exp"] != 0)
    total_nontriv = out0_nontriv + out1_nontriv

    assert out0_nontriv == 24, f"twin_bit=0 nontrivial = {out0_nontriv}, expected 24"
    assert out1_nontriv == 45, f"twin_bit=1 nontrivial = {out1_nontriv}, expected 45"
    assert total_nontriv == 69

    out["T4_twin0_nontriv"] = 24
    out["T4_twin1_nontriv"] = 45
    out["T4_total_nontriv"] = 69
    out["T4_twin0_edges"]   = 135
    out["T4_twin1_edges"]   = 135
    out["T4_ratio_note"]    = "24:45 = 8:15 split between twin_bit=0 and twin_bit=1"
    print(
        f"T4: Nontrivial cocycle: twin_bit=0 gives 24/135; twin_bit=1 gives 45/135; total 69/270  OK"
    )

    # ==================================================================
    # T5: Self-loops from g8,g9; quotient degree distribution; sheets
    # ==================================================================
    # Count self-loops (qid == target_qid)
    self_loops = [e for e in edges if e["qid"] == e["target_qid"]]
    assert len(self_loops) == 12, f"Self-loop count = {len(self_loops)}, expected 12"
    sl_by_gen = Counter(e["gen"] for e in self_loops)
    assert sl_by_gen["g8"] == 6, f"g8 self-loops = {sl_by_gen['g8']}"
    assert sl_by_gen["g9"] == 6, f"g9 self-loops = {sl_by_gen['g9']}"

    # Closed-neighborhood degree (including self when self-loop exists)
    qid_nbrs: dict[int, set] = defaultdict(set)
    for e in edges:
        qid_nbrs[e["qid"]].add(e["target_qid"])
        qid_nbrs[e["target_qid"]].add(e["qid"])

    degree_dist = Counter(len(nbrs) for nbrs in qid_nbrs.values())
    assert degree_dist == {5: 9, 6: 6, 7: 12}, (
        f"Quotient graph closed-nbr degree distribution = {dict(degree_dist)}"
    )
    weighted_sum = sum(d * c for d, c in degree_dist.items())
    assert weighted_sum == 165, f"Weighted degree sum = {weighted_sum}"

    # 6 sheets, each with 9 pockets
    pocket_sheet: dict[int, int] = {}
    for e in edges:
        pocket_sheet[e["u"]] = e["sheet_id"]
    sheet_dist = Counter(pocket_sheet.values())
    assert set(sheet_dist.values()) == {9}, f"Sheets don't all have 9 pockets: {dict(sheet_dist)}"
    assert len(sheet_dist) == 6

    out["T5_self_loop_count"]              = 12
    out["T5_g8_self_loops"]                = 6
    out["T5_g9_self_loops"]                = 6
    out["T5_quotient_degree_distribution"] = {str(k): v for k, v in sorted(degree_dist.items())}
    out["T5_weighted_degree_sum"]          = weighted_sum
    out["T5_sheet_count"]                  = 6
    out["T5_pockets_per_sheet"]            = 9
    out["T5_uniform_sheets"]               = True
    print(
        "T5: 12 self-loops (g8=6, g9=6); degree dist {5:9,6:6,7:12} (sum=165); 6x9 sheets  OK"
    )

    # ==================================================================
    # T6: Twin-pair sheet assignment — 7 intra-sheet, 20 inter-sheet
    # ==================================================================
    # Get sheet for each pocket (from source side)
    qid_tb_pockets: dict[int, dict] = defaultdict(dict)
    for e in edges:
        qid_tb_pockets[e["qid"]][e["twin_bit"]] = e["u"]

    same_sheet_count = 0
    diff_sheet_count = 0
    for qid in range(27):
        tb_map = qid_tb_pockets[qid]
        assert set(tb_map.keys()) == {0, 1}, f"qid {qid} missing twin_bit: {tb_map}"
        s0 = pocket_sheet[tb_map[0]]
        s1 = pocket_sheet[tb_map[1]]
        if s0 == s1:
            same_sheet_count += 1
        else:
            diff_sheet_count += 1

    assert same_sheet_count == 7,  f"Same-sheet pairs = {same_sheet_count}, expected 7"
    assert diff_sheet_count == 20, f"Diff-sheet pairs = {diff_sheet_count}, expected 20"
    assert same_sheet_count + diff_sheet_count == 27

    out["T6_same_sheet_pairs"] = 7
    out["T6_diff_sheet_pairs"] = 20
    out["T6_total_pairs"]      = 27
    out["T6_partition_exact"]  = True
    print("T6: Twin-pair sheet: 7 intra-sheet + 20 inter-sheet = 27 pairs  OK")

    # Summary
    out["summary"] = {
        "table_structure": (
            "270 edges = 27 qids x 10 orient-indices; "
            "orient 0-4 from twin_bit=0, orient 5-9 from twin_bit=1"
        ),
        "pair_stability": (
            "All 5 generators (g2,g3,g5,g8,g9) map both twins of each pair to same target qid"
        ),
        "twin_flip_pattern": (
            "g2: 0 flips; g3,g5: 6 flips each; g8,g9: 15 flips each (of 27)"
        ),
        "cocycle_split": (
            "twin_bit=0: 24/135 nontrivial; twin_bit=1: 45/135 nontrivial; total 69/270"
        ),
        "quotient_graph": (
            "27-node quotient: degree dist {5:9, 6:6, 7:12}; 6 sheets x 9 pockets"
        ),
        "sheet_assignment": (
            "7/27 twin-pairs intra-sheet; 20/27 inter-sheet"
        ),
    }

    out_path = ROOT / "data" / "w33_27x10_quotient.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print("All theorems verified OK")


if __name__ == "__main__":
    main()
