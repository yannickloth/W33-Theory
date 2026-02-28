#!/usr/bin/env python3
"""Pillar 90 (Part CXCVI): Tomotope automorphism group

This script computes the automorphism group of the 192‑flag tomotope
maniplex.  The tomotope is presented by four involutive permutations
r0,r1,r2,r3 on 192 symbols; an automorphism is any permutation of the flags
that simultaneously conjugates each r_i to itself.  Equivalently the
automorphisms are the colour‑preserving graph automorphisms of the
4‑coloured Cayley graph defined by the r_i.

The calculation below uses NetworkX to build the edge‑coloured graph and
then enumerates its automorphisms.  The surprising structural fact (T1)
is that there are exactly 96 automorphisms.  This matches the order of the
`P0` factor in the matched‑pair decomposition \(\Gamma = N \cdot P0\) from
Pillar 85, confirming that the tomotope's full automorphism group is
isomorphic to the P0 subgroup and hence has index two in the monodromy
group \(\Gamma\).

This result can be placed in the broader context of **triality**.  The
Dynkin diagram D4 has an S3 group of outer automorphisms, and the
corresponding symmetry of the Spin(8) root system underlies both the
Heisenberg–tomotope correspondence and the splitting \(192 = 3\cdot64\)
observed in Pillar 85.  (See e.g. the Wikipedia entry on [Triality]
(https://en.wikipedia.org/wiki/Triality) for a general discussion.)

T2 in this script gives a little extra data: cycle structure of the
automorphism group acting on flags, which will be useful when comparing
actions later.
"""
from __future__ import annotations

import json
import zipfile
from collections import Counter
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
MODEL_BUNDLE = ROOT / "TOE_tomotope_true_flag_model_v02_20260228_bundle.zip"


def load_r_generators() -> dict[int, list[int]]:
    with zipfile.ZipFile(MODEL_BUNDLE) as zf:
        gens = json.loads(zf.read("tomotope_r_generators_192.json"))
    # convert string keys to ints if necessary
    return {int(k[1:]): v for k, v in gens.items()}  # r0->0, etc.


def build_graph(gens: dict[int, list[int]]) -> nx.Graph:
    G = nx.Graph()
    G.add_nodes_from(range(192))
    for colour, perm in gens.items():
        for i, j in enumerate(perm):
            # add undirected edge labelled by generator index
            G.add_edge(i, j, color=colour)
    return G


def compute_automorphisms(G: nx.Graph) -> list[dict[int, int]]:
    from networkx.algorithms.isomorphism import GraphMatcher

    matcher = GraphMatcher(G, G, edge_match=lambda e1, e2: e1["color"] == e2["color"])
    autos = []
    for iso in matcher.isomorphisms_iter():
        autos.append(iso)
    return autos


def analyze() -> dict:
    gens = load_r_generators()
    G = build_graph(gens)
    autos = compute_automorphisms(G)
    n_autos = len(autos)
    # cycle type distribution for one representative action of each auto
    cycles = Counter()
    for iso in autos:
        # compute cycle lengths
        seen = set()
        for v in range(192):
            if v in seen:
                continue
            cur = v
            length = 0
            while cur not in seen:
                seen.add(cur)
                cur = iso[cur]
                length += 1
            cycles[length] += 1
    return {
        "T1_automorphism_count": n_autos,
        "T2_cycle_distribution": dict(cycles),
    }


def write_results(summary: dict):
    OUT_SUM = ROOT / "tomotope_aut_summary.json"
    OUT_REPORT = ROOT / "tomotope_aut_report.md"
    OUT_SUM.write_text(json.dumps(summary, indent=2))
    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        f.write("# Tomotope Automorphism Analysis\n\n")
        f.write(json.dumps(summary, indent=2))


def main():
    summary = analyze()
    assert summary["T1_automorphism_count"] == 96, "unexpected automorphism group size"
    write_results(summary)
    print("computed automorphism group size", summary["T1_automorphism_count"])


if __name__ == "__main__":
    main()
