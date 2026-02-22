#!/usr/bin/env python3
"""Enumerate conjugates of the C2xS6 30-line block and test each 27-subset for Schlaefli SRG.
Writes artifacts/c2s6_all_blocks_scan.json with summary and any candidates.
"""
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path
from time import time

ROOT = Path(__file__).resolve().parent
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

from tools.find_schlafli_embedding_in_w33 import compute_w33_lines, construct_w33_points
from tools.w33_aut_group_construct import build_points, generate_group


def build_line_bitmasks(lines):
    n = len(lines)
    idx = {tuple(sorted(l)): i for i, l in enumerate(lines)}
    masks = [0] * n
    for i in range(n):
        m = 0
        si = set(lines[i])
        for j in range(n):
            if i == j:
                continue
            if si.isdisjoint(lines[j]):
                m |= 1 << j
        masks[i] = m
    return masks


def is_srg_mask(mask, nodes, masks):
    # mask: int bitmask of selected 27 nodes (bits in 0..39)
    # nodes: list of node indices for the subset (length 27)
    # masks: list of bitmasks per node
    # check degree 16
    for v in nodes:
        d = (masks[v] & mask).bit_count()
        if d != 16:
            return False
    lam = None
    mu = None
    L = len(nodes)
    for i in range(L):
        vi = nodes[i]
        for j in range(i + 1, L):
            vj = nodes[j]
            common = (masks[vi] & masks[vj] & mask).bit_count()
            if (masks[vi] >> vj) & 1:  # adjacent
                if lam is None:
                    lam = common
                elif lam != common:
                    return False
            else:
                if mu is None:
                    mu = common
                elif mu != common:
                    return False
    return lam == 10 and mu == 8


def main():
    # load the representative 30-block
    orbits = json.loads(
        (ROOT / "artifacts" / "sage_c2s6_line_orbits.json").read_text(encoding="utf-8")
    )["orbits"]
    block30 = orbits[0]

    pts = construct_w33_points()
    lines = compute_w33_lines(pts)
    n = len(lines)

    masks = build_line_bitmasks(lines)

    # build full automorphism group (permutations on points)
    _, point_perms = generate_group(build_points())

    # build induced line permutation for each group element and collect conjugate blocks
    seen_blocks = set()
    blocks = []
    for perm in point_perms:
        # image of block30
        img = tuple(
            sorted(
                next(
                    i
                    for i, L in enumerate(lines)
                    if tuple(sorted(perm[p] for p in L)) == tuple(sorted(L))
                )
                for L in (lines[idx] for idx in block30)
            )
        )
        key = tuple(sorted(img))
        if key not in seen_blocks:
            seen_blocks.add(key)
            blocks.append(list(key))

    print("Found", len(blocks), "distinct conjugate 30-blocks")

    results = {"n_blocks": len(blocks), "checked_subsets": 0, "found": []}
    start = time()
    for bi, block in enumerate(blocks):
        print("Checking block", bi + 1, "of", len(blocks))
        # enumerate 27-subsets
        for subset in combinations(block, 27):
            results["checked_subsets"] += 1
            mask = 0
            for v in subset:
                mask |= 1 << v
            if is_srg_mask(mask, list(subset), masks):
                results["found"].append({"block_index": bi, "subset": list(subset)})
                print("Found candidate in block", bi)
                (ART / "c2s6_all_blocks_scan.json").write_text(
                    json.dumps(results, indent=2), encoding="utf-8"
                )
                return
    results["time_seconds"] = time() - start
    (ART / "c2s6_all_blocks_scan.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    print("Done. no candidates found; checked subsets:", results["checked_subsets"])


if __name__ == "__main__":
    main()
