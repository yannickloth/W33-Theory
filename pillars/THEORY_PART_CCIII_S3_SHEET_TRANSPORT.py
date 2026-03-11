#!/usr/bin/env python3
"""Pillar 103 (Part CCIII): S3 Sheet Transport Law on K-Schreier Graph

The S3-sheet transport bundle augments each of the 54 K-pockets with a cyclic
label L[u] in C3 = Z3, encoding the sheet-of-sheets gauge degree of freedom
that is invisible in the pure pocket / twin-pair decomposition.  The central
result is an exact abelian transport law governing how these labels propagate
along every one of the 270 directed K-Schreier edges.

Theorems:

T1  The label assignment L: {0,...,53} -> Z3 distributes as
    {0:17, 1:11, 2:26} (identity 0, cyclic-shift-1, cyclic-shift-2).
    The assignment is uniquely determined (up to global rotation) by the
    requirement that T2 holds.

T2  EXACT TRANSPORT LAW (0 errors out of 270): for every directed
    K-Schreier edge (u -> v, generator g, cocycle exponent e):
        L[v] = (s_g[g] + L[u] + e) mod 3
    where s_g: {g2,g3,g5,g8,g9} -> Z3 is the generator shift table.

T3  Only generator g3 has a non-trivial shift: s_g[g3] = 2 (= c2 in C3).
    All other generators g2, g5, g8, g9 have s_g = 0 (identity shift).
    This singles out g3 as the unique sheet-rotating generator.

T4  The 54 pockets form 6 sheets of 9 pockets each.  Within each sheet
    the L-distribution varies: sheets 0-1 are identity-dominated (6 out
    of 9), while sheets 3-5 are c2-dominated.  No sheet is homogeneous
    in L.

T5  Among the 27 Heisenberg qids (twin-pairs), 9 have the same L-label
    on both twin_bit=0 and twin_bit=1 pockets; 18 have differing labels.
    The most common inter-bit transition is id -> c2, appearing in 8 qids.

T6  The cocycle exponent distribution {0:201, 1:33, 2:36} (Pillar 83) is
    exactly reflected in the L-transport: the 69 non-trivial cocycle edges
    (33 with e=1 and 36 with e=2) account for all sheet transitions not
    explained by the generator shift alone.  In particular, the formula
    L[v] - L[u] - s_g[g] = e (mod 3) recovers the cocycle exponent for
    each edge with no exceptions.
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
_ARCHIVE_ZIP = ROOT.parent / "archive" / "zip"
BUNDLE = ROOT / "TOE_S3_SHEET_TRANSPORT_v01_20260228_bundle.zip"
WELD_BUNDLE = ROOT / "TOE_tomotope_triality_weld_v01_20260228_bundle.zip"
TRANSPORT_BUNDLE = ROOT / "TOE_270_TRANSPORT_v01_20260228_bundle.zip"

_C3_MAP = {(0, 1, 2): 0, (1, 2, 0): 1, (2, 0, 1): 2}


def _resolve_bundle(path: Path) -> Path:
    candidates = (
        path,
        _ARCHIVE_ZIP / path.name,
    )
    resolved = next((candidate for candidate in candidates if candidate.exists()), None)
    if resolved is None:
        raise FileNotFoundError(f"Could not locate bundle {path.name} in pillars/ or archive/zip/.")
    return resolved


def _load_bundle():
    with zipfile.ZipFile(_resolve_bundle(BUNDLE)) as zf:
        L_raw = json.loads(zf.read("L_table.json"))
        s_g_raw = json.loads(zf.read("s_g.json"))
        silent = json.loads(zf.read("silent_sheet.json"))
    L = [_C3_MAP[tuple(x)] for x in L_raw]
    s_g = {k: _C3_MAP[tuple(v)] for k, v in s_g_raw.items()}
    return L, s_g, silent


def _load_schreier_edges() -> List[Tuple[int, int, str, int]]:
    with zipfile.ZipFile(_resolve_bundle(WELD_BUNDLE)) as wz:
        text = wz.read(
            "TOE_tomotope_triality_weld_v01_20260228/K_schreier_edges_voltage_Z3.csv"
        ).decode()
    return [
        (int(r["u"]), int(r["v"]), r["gen"], int(r["cocycle_Z3_exp"]))
        for r in csv.DictReader(io.StringIO(text))
    ]


def _load_transport_edges() -> List[dict]:
    with zipfile.ZipFile(_resolve_bundle(TRANSPORT_BUNDLE)) as zf:
        edges_txt = zf.read("edges_270_transport.csv").decode()
    return list(csv.DictReader(io.StringIO(edges_txt)))


def analyze() -> dict:
    L, s_g, silent = _load_bundle()
    schreier = _load_schreier_edges()
    transport = _load_transport_edges()

    # T1: L distribution
    L_dist = dict(sorted(Counter(L).items()))

    # T2: Verify transport law
    ok = fail = 0
    recovered_e: List[Tuple[int, int, str, int, int]] = []
    for u, v, g, e in schreier:
        expected = (s_g[g] + L[u] + e) % 3
        if L[v] == expected:
            ok += 1
        else:
            fail += 1
        # T6: recover cocycle from L
        rec_e = (L[v] - L[u] - s_g[g]) % 3
        recovered_e.append((u, v, g, e, rec_e))

    # T3: s_g table
    s_g_out = dict(sorted(s_g.items()))

    # T4: Sheet structure
    by_sheet: Dict[int, List[int]] = defaultdict(list)
    for s in silent:
        by_sheet[int(s["sheet_id"])].append(int(s["orbit_idx"]))
    sheet_L_dist: Dict[int, dict] = {}
    for sh, pockets in sorted(by_sheet.items()):
        sheet_L_dist[sh] = dict(sorted(Counter(L[p] for p in pockets).items()))

    # T5: Twin-pair L analysis
    qid_pockets: Dict[int, Dict[int, int]] = {}
    for e in transport:
        qid = int(e["qid"])
        pocket = int(e["u"])
        twin = int(e["twin_bit"])
        if qid not in qid_pockets:
            qid_pockets[qid] = {}
        qid_pockets[qid][twin] = pocket

    same_L = diff_L = 0
    L_pairs: List[Tuple[int, int]] = []
    for qid in sorted(qid_pockets.keys()):
        p0 = qid_pockets[qid].get(0)
        p1 = qid_pockets[qid].get(1)
        if p0 is not None and p1 is not None:
            l0, l1 = L[p0], L[p1]
            L_pairs.append((l0, l1))
            if l0 == l1:
                same_L += 1
            else:
                diff_L += 1
    L_pair_dist = {str(k): v for k, v in Counter(L_pairs).items()}

    # T6: recovered cocycle vs actual cocycle
    cocycle_match = sum(1 for _, _, _, e, rec in recovered_e if e == rec)
    cocycle_dist = dict(sorted(Counter(e for _, _, _, e, _ in recovered_e).items()))

    return {
        "T1_L_distribution": L_dist,
        "T1_num_pockets": len(L),
        "T2_edge_check_ok": ok,
        "T2_edge_check_fail": fail,
        "T2_transport_law_exact": fail == 0,
        "T3_generator_shifts": s_g_out,
        "T3_nonzero_generators": [g for g, v in s_g.items() if v != 0],
        "T4_num_sheets": len(by_sheet),
        "T4_pockets_per_sheet": len(list(by_sheet.values())[0]),
        "T4_sheet_L_distributions": {str(k): v for k, v in sheet_L_dist.items()},
        "T5_qid_same_L": same_L,
        "T5_qid_diff_L": diff_L,
        "T5_L_pair_distribution": L_pair_dist,
        "T6_cocycle_recovered_exact": cocycle_match == len(recovered_e),
        "T6_cocycle_dist": cocycle_dist,
        "T6_nontrivial_edges": sum(v for k, v in cocycle_dist.items() if k > 0),
    }


def main():
    summary = analyze()
    (ROOT / "data" / "w33_s3_sheet_transport.json").write_text(
        json.dumps(summary, indent=2)
    )
    with open(ROOT / "s3_sheet_transport_report.md", "w", encoding="utf-8") as f:
        f.write("# S3 Sheet Transport Report\n\n")
        f.write(json.dumps(summary, indent=2))
    print("T2 transport law exact:", summary["T2_transport_law_exact"])
    print("T3 nonzero generators:", summary["T3_nonzero_generators"])
    print("T5 twin L same/diff:", summary["T5_qid_same_L"], "/", summary["T5_qid_diff_L"])
    print("T6 cocycle recovery exact:", summary["T6_cocycle_recovered_exact"])
    print("wrote data/w33_s3_sheet_transport.json")


if __name__ == "__main__":
    main()
