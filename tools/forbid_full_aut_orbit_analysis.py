#!/usr/bin/env python3
"""Full automorphism orbit analysis for candidate forbids using GSp(4,3) action.

- Builds the embedding Schläfli(27) -> W33 lines (re-uses code from
  find_schlafli_embedding_in_w33.py) and obtains a mapping sch -> w (27 -> 40).
- Generates the GSp(4,3) point-permutation group via w33_aut_group_construct.
- Computes the induced permutation action on the 27 Schläfli indices.
- For each candidate triad, computes the orbit, stabilizer size, and a canonical
  representative (default: lexicographically smallest element of orbit intersection).
- Writes artifacts/forbid_full_aut_orbit_analysis.json and a markdown report.

Usage: python tools/forbid_full_aut_orbit_analysis.py --cands 0-18-25,0-20-23
"""
from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path
from typing import Dict, List, Sequence, Set, Tuple

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
REPORTS = ROOT / "reports"
ART.mkdir(exist_ok=True)
REPORTS.mkdir(exist_ok=True)

# Reuse helpers from existing script
from tools.find_schlafli_embedding_in_w33 import (
    build_schlafli_adj,
    compute_w33_lines,
    compute_we6_orbits,
    construct_e8_roots,
    construct_w33_points,
)
from tools.w33_aut_group_construct import generate_group


def build_schlafli_mapping() -> Tuple[Dict[int, int], List[Tuple[int, ...]]]:
    """Return mapping sch -> w (sch index -> w33 line index) and wlines list.
    Attempts to find an induced embedding of the 27-Schläfli graph inside
    the 40-line disjointness graph of W33.
    """
    roots = construct_e8_roots()
    orbits = compute_we6_orbits(roots)
    o27 = next(o for o in orbits if len(o) == 27)
    sch_adj = build_schlafli_adj(roots, o27)
    G_sch = nx.Graph()
    G_sch.add_nodes_from(range(27))
    for i in range(27):
        for j in range(i + 1, 27):
            if sch_adj[i, j]:
                G_sch.add_edge(i, j)

    wpts = construct_w33_points()
    wlines = compute_w33_lines(wpts)
    G_lines = nx.Graph()
    G_lines.add_nodes_from(range(len(wlines)))
    for i in range(len(wlines)):
        for j in range(i + 1, len(wlines)):
            if set(wlines[i]).isdisjoint(set(wlines[j])):
                G_lines.add_edge(i, j)

    GM = nx.algorithms.isomorphism.GraphMatcher(G_lines, G_sch)
    mapping = None
    for iso in GM.subgraph_isomorphisms_iter():
        mapping = iso
        break

    if mapping is None:
        raise RuntimeError(
            "No Schläfli embedding found inside W33 line-disjointness graph."
        )

    # mapping: keys = w_index, values = sch_index -> invert to sch->w
    sch_to_w = {sch_i: int(w_i) for w_i, sch_i in mapping.items()}
    return sch_to_w, wlines


def induce_27_action(sch_to_w: Dict[int, int], wlines: List[Tuple[int, ...]]):
    """Return list of permutations on 27 nodes induced by group acting on 40 points.
    Each permutation is a tuple p where p[sch_idx] = new_sch_idx.
    """
    points = None
    G_point_perms, _ = generate_group(construct_w33_points())

    # build wline -> sch mapping
    w_to_sch = {w: s for s, w in sch_to_w.items()}

    perms_27 = []
    for p in G_point_perms:
        ok = True
        perm27 = [-1] * 27
        for sch_idx in range(27):
            w_idx = sch_to_w[sch_idx]
            line = wlines[w_idx]
            # apply point permutation p to each point in line
            mapped_line = tuple(sorted(p[i] for i in line))
            # find index of mapped_line in wlines
            try:
                new_w_idx = wlines.index(mapped_line)
            except ValueError:
                ok = False
                break
            # map back to sch index
            if new_w_idx not in w_to_sch:
                ok = False
                break
            perm27[sch_idx] = w_to_sch[new_w_idx]
        if ok:
            perms_27.append(tuple(perm27))
    return perms_27


def triad_orbit(triad: Tuple[int, int, int], perms27: Sequence[Tuple[int, ...]]):
    """Return sorted set of triads in the orbit of triad under perms27."""
    s = set()
    a, b, c = triad
    for perm in perms27:
        t = tuple(sorted((perm[a], perm[b], perm[c])))
        s.add(t)
    return sorted(s)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cands", type=str, default="0-18-25,0-20-23")
    parser.add_argument(
        "--pick", type=str, default="lex_min", help="pick rule: lex_min|max_stab"
    )
    args = parser.parse_args()

    cands = [tuple(sorted(int(x) for x in s.split("-"))) for s in args.cands.split(",")]

    print("Building Schläfli embedding and W33 lines mapping...")
    sch_to_w, wlines = build_schlafli_mapping()
    print("Found Schläfli -> W mapping; computing induced 27-action from GSp(4,3)...")

    perms27 = induce_27_action(sch_to_w, wlines)
    print(
        f"Induced permutations on 27 nodes: {len(perms27)} elements (should be group size)"
    )

    # compute orbits
    orbits = {cand: triad_orbit(cand, perms27) for cand in cands}

    intersect = (
        set(orbits[cands[0]]).intersection(set(orbits[cands[1]]))
        if len(cands) > 1
        else set()
    )

    # stabilizer sizes
    def stab_size(tri: Tuple[int, int, int]) -> int:
        count = 0
        tri_s = set(tri)
        for perm in perms27:
            if set(perm[i] for i in tri) == tri_s:
                count += 1
        return count

    stab = {cand: stab_size(cand) for cand in cands}

    # pick canonical representative
    canonical = None
    if intersect:
        if args.pick == "lex_min":
            canonical = sorted(intersect)[0]
        elif args.pick == "max_stab":
            # pick element in intersection with max stabilizer
            best = None
            best_sz = -1
            for t in intersect:
                s = stab_size(t)
                if s > best_sz:
                    best_sz = s
                    best = t
            canonical = best
    else:
        # pick lex min of union of orbits as fallback
        union = set()
        for v in orbits.values():
            union.update(v)
        canonical = sorted(union)[0] if union else None

    out = {
        "candidates": {"->".join(map(str, c)): orbits[c] for c in cands},
        "intersection_nonempty": len(intersect) > 0,
        "intersection": sorted(list(intersect)),
        "canonical_pick_rule": args.pick,
        "canonical": canonical,
        "stabilizer_sizes": {"->".join(map(str, c)): stab[c] for c in cands},
        "perms27_count": len(perms27),
    }

    (ART / "forbid_full_aut_orbit_analysis.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )

    # md report
    lines = ["# Full Aut(W33) forbid orbit analysis", ""]
    lines.append(f"Group induced permutations on 27 nodes: {len(perms27)}")
    lines.append("")
    for k, v in out["candidates"].items():
        lines.append(f"- Candidate {k}: orbit size = {len(v)}")
        lines.append(f"  - sample orbit members: {v[:8]}")
    lines.append("")
    if out["intersection_nonempty"]:
        lines.append(
            "Candidates are in the SAME Aut(W33) orbit intersection (non-empty)."
        )
        lines.append(f"Intersection sample: {out['intersection'][:8]}")
        lines.append(
            f"Chosen canonical representative ({args.pick}): {out['canonical']}"
        )
    else:
        lines.append("Candidates do NOT intersect under full Aut(W33).")
        lines.append(f"Fallback canonical representative: {out['canonical']}")

    (REPORTS / "forbid_full_aut_orbit_analysis.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    print(
        "Wrote artifacts/forbid_full_aut_orbit_analysis.json and reports/forbid_full_aut_orbit_analysis.md"
    )


if __name__ == "__main__":
    main()
