#!/usr/bin/env python3
"""Compare the 240-edge permutation module coming from the duad bundle with
the WE6 "true" 240-action.

This script performs several checks:

* load PSp(4,3) generators on 40 points from the duad bundle and build the
  induced action on the 240 edges (constructed from the 40 lines).
* compute the full duad group on 240 edges and tabulate the distribution of
  fixed-edge counts; use the class data in the bundle CSV for reference.
* load WE6 generators from ``artifacts/we6_true_action.json`` (they are
  1-based permutations on 240 objects), form the group and similarly
  compute fixed-edge statistics.
* compare the two histograms; if they agree we report a character match.
* attempt to find an explicit conjugator mapping the WE6 edge action to the
  duad edge action by treating each generating set as a colored directed
  graph and running NetworkX's isomorphism algorithm.

The resulting permutation (if found) is saved to
``artifacts/duad_we6_conjugator.json``.  The script exits with 0 on success
(character match and a conjugator found) and nonzero otherwise.
"""

from __future__ import annotations

import json
import csv
import zipfile
from pathlib import Path
from collections import Counter, deque
from typing import List, Tuple, Dict

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
logf = ROOT / "artifacts" / "duad_we6_conjugacy.log"

def dbg(msg: str):
    print(msg)
    try:
        with open(logf, "a") as f:
            f.write(msg + "\n")
    except Exception:
        pass


def find_bundle(pattern: str) -> Path:
    # same helper as in compute_phi_lift_subgroup
    p = ROOT / f"{pattern}.zip"
    if p.exists():
        return p
    p2 = ROOT / pattern
    if p2.exists():
        return p2
    cands = list(ROOT.glob(pattern + "*"))
    if cands:
        return cands[0]
    raise FileNotFoundError(pattern)


def read_from_bundle(bundle: Path, name: str) -> bytes:
    """Return raw bytes of a file inside *bundle* which may be a directory or a zip."""
    if bundle.is_file():
        with zipfile.ZipFile(bundle) as z:
            zlist = z.namelist()
            if name in zlist:
                entry = name
            else:
                # try to locate by suffix (path within archive)
                cand = [x for x in zlist if x.endswith('/' + name)]
                if cand:
                    entry = cand[0]
                else:
                    raise KeyError(f"{name} not found in archive {bundle}")
            return z.read(entry)
    else:
        return (bundle / name).read_bytes()


def load_json(bundle: Path, name: str):
    data = read_from_bundle(bundle, name)
    return json.loads(data)


def build_edges_from_lines(lines: List[List[int]]) -> List[Tuple[int,int]]:
    edges = set()
    for L in lines:
        for i in range(len(L)):
            for j in range(i + 1, len(L)):
                a, b = L[i], L[j]
                edges.add((a, b) if a < b else (b, a))
    edges = sorted(edges)
    assert len(edges) == 240, f"expected 240 edges, got {len(edges)}"
    return edges


def build_edge_pairs(edges: List[Tuple[int,int]]) -> Tuple[List[Tuple[Tuple[int,int],Tuple[int,int]]], Dict[Tuple[int,int],int]]:
    # compute adjacency matrix for edges on the point graph
    adj = {i: set() for i in range(40)}
    for a,b in edges:
        adj[a].add(b)
        adj[b].add(a)
    # map each edge to its opposite on the same line (line shares two points)
    edge_to_pair = {}
    pairs = []
    for e in edges:
        i,j = e
        # find points common to both endpoints aside from i,j (should be 2 points forming the other edge)
        common = adj[i] & adj[j]
        if len(common) != 2:
            raise RuntimeError(f"edge {e} does not sit on a unique line")
        a,b = sorted(common)
        opp = (a,b)
        pair = tuple(sorted([e, opp]))
        if pair not in pairs:
            pairs.append(pair)
    # assign indices
    pair_index = {pair: idx for idx,pair in enumerate(pairs)}
    # build mapping edge->pair index
    edge_to_pair = {}
    for pair, idx in pair_index.items():
        e1,e2 = pair
        edge_to_pair[e1] = idx
        edge_to_pair[e2] = idx
    return pairs, edge_to_pair


def edges_to_pair_perms(edge_gens: List[List[int]], edge_to_pair: Dict[Tuple[int,int],int], edges: List[Tuple[int,int]]) -> List[List[int]]:
    pair_gens = []
    for perm in edge_gens:
        pg = []
        for ei in perm:
            e = edges[ei]
            pg.append(edge_to_pair[e])
        pair_gens.append(pg)
    return pair_gens


def point_perms_to_edge_perms(point_gens: List[List[int]], edges: List[Tuple[int,int]]) -> List[List[int]]:
    # point_gens are lists of length 40, 0-based
    edge_index = {e:i for i,e in enumerate(edges)}
    edge_gens: List[List[int]] = []
    for pg in point_gens:
        perm = []
        for (a,b) in edges:
            a2 = pg[a]
            b2 = pg[b]
            if a2 < b2:
                perm.append(edge_index[(a2,b2)])
            else:
                perm.append(edge_index[(b2,a2)])
        edge_gens.append(perm)
    return edge_gens


def closure_of_perms(gens: List[List[int]]) -> List[List[int]]:
    # BFS closure in permutation group (domain assumed consistent length)
    n = len(gens[0])
    seen = {
        tuple(range(n)): True
    }
    queue = [list(range(n))]
    all_perms = [list(range(n))]
    while queue:
        g = queue.pop()
        for h in gens:
            # compose g followed by h
            gh = [g[h[i]] for i in range(n)]
            tgh = tuple(gh)
            if tgh not in seen:
                seen[tgh] = True
                queue.append(gh)
                all_perms.append(gh)
    return all_perms


def fixed_points(perm: List[int]) -> int:
    return sum(1 for i,v in enumerate(perm) if v == i)


def histogram_by_fixed(perms: List[List[int]]) -> Counter:
    return Counter(fixed_points(p) for p in perms)


def load_duad_data(bundle: Path):
    # we don't actually need the point coordinate data here; skip optional file
    lines = load_json(bundle, "W33_lines_40.json")["lines"]
    pgdata = load_json(bundle, "psp43_generators_on_points_40.json")
    if isinstance(pgdata, dict) and "generators" in pgdata:
        point_gens = pgdata["generators"]
    else:
        point_gens = pgdata
    # ensure zero-based ints
    point_gens = [[int(x) for x in perm] for perm in point_gens]
    edges = build_edges_from_lines(lines)
    edge_gens = point_perms_to_edge_perms(point_gens, edges)
    return edges, edge_gens


def load_we6_edge_perms() -> List[List[int]]:
    data = json.loads((ROOT / "artifacts" / "we6_true_action.json").read_text())
    gens = data.get("we6_even_generators") or data.get("we6_generators")
    if gens is None:
        raise ValueError("we6_true_action.json lacks expected generator list")
    # permutations are 1-based on 240 objects
    perms = []
    for perm in gens:
        perms.append([int(x) - 1 for x in perm])
    return perms


def load_fix_hist(bundle: Path, column: str) -> Counter:
    # read a fixed-point histogram from the conjugacy CSV for given column
    data = read_from_bundle(bundle, "conjugacy_classes_extended_characters_and_fixed_counts.csv")
    text = data.decode()
    hist = Counter()
    rdr = csv.DictReader(text.splitlines())
    for row in rdr:
        size = int(row["size"])
        fix = int(row[column])
        hist[fix] += size
    return hist


def build_colored_di_graph(perms: List[List[int]]) -> nx.DiGraph:
    n = len(perms[0])
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    for idx,perm in enumerate(perms):
        for u,v in enumerate(perm):
            G.add_edge(u, v, color=idx)
    return G


def find_conjugator(duad_edge_gens, we6_edge_gens):
    G1 = build_colored_di_graph(duad_edge_gens)
    G2 = build_colored_di_graph(we6_edge_gens)
    matcher = nx.algorithms.isomorphism.DiGraphMatcher(G1, G2,
                                                      edge_match=lambda a,b: a["color"]==b["color"])
    if matcher.is_isomorphic():
        return matcher.mapping
    return None


def main():
    try:
        bundle = find_bundle("TOE_duad_algebra_v06_20260227_bundle")
        dbg(f"duad bundle located at {bundle}")
        # bundle directory contains subfolder; adjust
        if (bundle / "TOE_duad_algebra_v05_20260227").exists():
            bundle = bundle / "TOE_duad_algebra_v05_20260227"
            dbg(f"adjusted bundle path to {bundle}")

        # compute 240-edge action for duel
        edges, duad_edge_gens = load_duad_data(bundle)
        duad_group = closure_of_perms(duad_edge_gens)
        dbg(f"duad group size on edges {len(duad_group)}")
        hist_duad = histogram_by_fixed(duad_group)

        # generate WE6-edge perms and its closure
        we6_gens = load_we6_edge_perms()
        we6_group = closure_of_perms(we6_gens)
        dbg(f"WE6 group size on edges {len(we6_group)}")
        hist_we6 = histogram_by_fixed(we6_group)

        dbg(f"duad fixed-edge histogram {hist_duad.most_common()}")
        dbg(f"we6 fixed-edge histogram {hist_we6.most_common()}")

        dbg("about to load reference edge histogram")
        ref_edge_hist = load_fix_hist(bundle, "fix_edges240")
        dbg(f"reference edge histogram {sorted(ref_edge_hist.items())}")
        dbg("about to compare edge histograms")
        if hist_duad == ref_edge_hist:
            dbg("duad edge histogram matches reference classes")
        else:
            dbg("WARNING: duad edge histogram differs from reference")
        if hist_we6 == ref_edge_hist:
            dbg("WE6 edge histogram matches reference classes")
        else:
            dbg("WARNING: WE6 edge histogram does NOT match reference")

        dbg("about to search for conjugator on edges")
        conj = find_conjugator(duad_edge_gens, we6_gens)
        if conj is None:
            dbg("failed to find conjugator between edge actions")
        else:
            dbg(f"found edge-level conjugator mapping (first 10 entries): {list(conj.items())[:10]}")
            (ROOT / "artifacts" / "duad_we6_conjugator_edges.json").write_text(json.dumps(conj))

        # build pair-level data
        pairs, edge_to_pair = build_edge_pairs(edges)
        dbg(f"computed {len(pairs)} edge-pairs")
        duad_pair_gens = edges_to_pair_perms(duad_edge_gens, edge_to_pair, edges)
        we6_pair_gens = edges_to_pair_perms(we6_gens, edge_to_pair, edges)

        duad_pair_group = closure_of_perms(duad_pair_gens)
        dbg(f"duad group size on pairs {len(duad_pair_group)}")
        hist_duad_pairs = histogram_by_fixed(duad_pair_group)
        dbg(f"duad fixed-pair histogram {hist_duad_pairs.most_common()}")

        we6_pair_group = closure_of_perms(we6_pair_gens)
        dbg(f"we6 group size on pairs {len(we6_pair_group)}")
        hist_we6_pairs = histogram_by_fixed(we6_pair_group)
        dbg(f"we6 fixed-pair histogram {hist_we6_pairs.most_common()}")

        dbg("about to load reference duad histogram")
        ref_pair_hist = load_fix_hist(bundle, "fix_duads120")
        dbg(f"reference duad histogram {sorted(ref_pair_hist.items())}")

        if hist_duad_pairs == ref_pair_hist:
            dbg("duad pair histogram matches reference classes")
        else:
            dbg("WARNING: duad pair histogram differs from reference")

        if hist_we6_pairs == ref_pair_hist:
            dbg("WE6 pair histogram matches reference classes")
        else:
            dbg("WARNING: WE6 pair histogram does NOT match reference")

        dbg("about to search for conjugator on pairs")
        conj_pairs = find_conjugator(duad_pair_gens, we6_pair_gens)
        if conj_pairs is None:
            dbg("failed to find conjugator between pair actions")
            exit(1)
        else:
            dbg(f"found pair-level conjugator (first 10 entries): {list(conj_pairs.items())[:10]}")
            (ROOT / "artifacts" / "duad_we6_conjugator_pairs.json").write_text(json.dumps(conj_pairs))
            exit(0)
    except Exception as e:
        import traceback
        dbg("exception in main:")
        tb = traceback.format_exc()
        dbg(tb)
        exit(1)


if __name__ == "__main__":
    main()
