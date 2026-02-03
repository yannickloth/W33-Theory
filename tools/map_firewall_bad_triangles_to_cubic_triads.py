#!/usr/bin/env python3
"""
Map the W33 firewall "bad triangles" (9 disjoint 3-cycles on H27) to the 45 cubic-surface triads
on a fixed Schläfli 27-line model.

Pipeline:
  1) Build W33 from F3^4 (40 vertices, SRG(40,12,2,4)).
  2) For v0=0, form H12 = neighbors(v0), H27 = non-neighbors(v0).
  3) For each non-orth pair {u,v} in H27 (i.e. u--v is a non-edge of W33):
       witness = N(u) ∩ N(v)  (size 4 by SRG parameters)
       bad(u,v) iff witness ⊂ H12.
     This yields 27 bad edges on the 27 vertices; they form 9 triangles.
  4) Define kernel graph K on H27 with edges = GOOD non-orth pairs; K is SRG(27,16,10,8).
  5) Build a Schläfli SRG(27,16,10,8) from one E8 W(E6) 27-orbit (the same orbit used by
     artifacts/we6_signed_action_on_27.json).
  6) Find an explicit isomorphism f: K -> Schläfli by matching a double-six structure.
  7) Push the 9 bad triangles through f, obtaining 9 of the 45 meet-graph triangles (= cubic triads)
     in the Schläfli model.
  8) Cross-tabulate those 9 triads against the selection parity report.

Writes:
  artifacts/firewall_bad_triads_mapping.json
  artifacts/firewall_bad_triads_mapping.md
"""

from __future__ import annotations

import importlib.util
import itertools
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


cds = _load_module(ROOT / "tools" / "compute_double_sixes.py", "compute_double_sixes")
canon = _load_module(
    ROOT / "tools" / "solve_canonical_su3_gauge_and_cubic.py",
    "solve_canonical_su3_gauge_and_cubic",
)


def _pairs_from_adj(adj: np.ndarray) -> set[tuple[int, int]]:
    n = adj.shape[0]
    out = set()
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i, j]:
                out.add((i, j))
    return out


def _triangles_from_edges(
    n: int, edges: set[tuple[int, int]]
) -> list[tuple[int, int, int]]:
    nbr = [set() for _ in range(n)]
    for u, v in edges:
        nbr[u].add(v)
        nbr[v].add(u)
    tri = []
    for a in range(n):
        for b in sorted(x for x in nbr[a] if x > a):
            common = nbr[a] & nbr[b]
            for c in sorted(x for x in common if x > b):
                tri.append((a, b, c))
    return tri


def _canonical_double_six_labeling(
    adj: np.ndarray, ds: tuple[tuple[int, ...], tuple[int, ...], dict[int, int]]
):
    """
    Given adj on n=27 and one double-six ds=(A,B,match) as returned by cds.find_double_sixes,
    produce:
      - A_pos: list of vertices in A ordered canonically (ascending)
      - B_pos: list of vertices in B ordered by the matching of A_pos
      - rem_by_duad: map (i,j) with 0<=i<j<=5 -> vertex outside the double-six
    Duad label of a remaining vertex is determined by which TWO A-vertices it is NON-adjacent to.
    """
    A, B, match = ds
    A_pos = sorted(A)
    B_pos = [int(match[a]) for a in A_pos]
    A_set = set(A_pos)
    B_set = set(B_pos)
    rem = [v for v in range(adj.shape[0]) if v not in A_set and v not in B_set]
    if len(rem) != 15:
        raise RuntimeError("Expected 15 remaining vertices")

    a_index = {a: i for i, a in enumerate(A_pos)}
    rem_by_duad: Dict[tuple[int, int], int] = {}
    for v in rem:
        nonA = [a_index[a] for a in A_pos if not adj[v, a]]
        if len(nonA) != 2:
            raise RuntimeError("Remaining vertex does not have 2 non-neighbors in A")
        i, j = sorted(nonA)
        key = (i, j)
        if key in rem_by_duad:
            raise RuntimeError("Duad label collision")
        rem_by_duad[key] = v
    if len(rem_by_duad) != 15:
        raise RuntimeError("Expected 15 duads")
    return A_pos, B_pos, rem_by_duad


def _find_isomorphism_via_double_sixes(
    adj1: np.ndarray, adj2: np.ndarray
) -> Dict[int, int]:
    """
    Find an isomorphism f: V1->V2 between two SRG(27,16,10,8) graphs by matching double-sixes and
    allowing all 6! permutations of A-labels plus optional A/B swaps.
    """
    k6_1 = cds.find_k_cliques(adj1, 6)
    ds_1 = cds.find_double_sixes(adj1, k6_1)
    k6_2 = cds.find_k_cliques(adj2, 6)
    ds_2 = cds.find_double_sixes(adj2, k6_2)
    if len(ds_1) != 36 or len(ds_2) != 36:
        raise RuntimeError("Expected 36 double-sixes in each graph")

    perms = list(itertools.permutations(range(6)))

    def is_iso(f: Dict[int, int]) -> bool:
        n = adj1.shape[0]
        for i in range(n):
            fi = f[i]
            for j in range(i + 1, n):
                if adj1[i, j] != adj2[fi, f[j]]:
                    return False
        return True

    for ds1 in ds_1:
        for swap1 in (False, True):
            A1, B1, m1 = ds1
            if swap1:
                inv = {v: k for k, v in m1.items()}
                A1, B1, m1 = B1, A1, inv
            A1_pos, B1_pos, rem1 = _canonical_double_six_labeling(adj1, (A1, B1, m1))

            for ds2 in ds_2[
                :1
            ]:  # fix a single target double-six; automorphisms cover the rest
                for swap2 in (False, True):
                    A2, B2, m2 = ds2
                    if swap2:
                        inv2 = {v: k for k, v in m2.items()}
                        A2, B2, m2 = B2, A2, inv2
                    A2_pos_raw, B2_pos_raw, rem2_raw = _canonical_double_six_labeling(
                        adj2, (A2, B2, m2)
                    )

                    for pi in perms:
                        # relabel the A positions of graph2 by perm pi
                        A2_pos = [A2_pos_raw[pi[i]] for i in range(6)]
                        B2_pos = [B2_pos_raw[pi[i]] for i in range(6)]
                        # rem2 duads permute accordingly
                        rem2: Dict[tuple[int, int], int] = {}
                        for (i, j), v in rem2_raw.items():
                            ii, jj = sorted((pi[i], pi[j]))
                            rem2[(ii, jj)] = v

                        f: Dict[int, int] = {}
                        for i in range(6):
                            f[A1_pos[i]] = A2_pos[i]
                            f[B1_pos[i]] = B2_pos[i]
                        for key, v1 in rem1.items():
                            f[v1] = rem2[key]

                        if len(f) != 27:
                            continue
                        if is_iso(f):
                            return f

    raise RuntimeError("Failed to find graph isomorphism via double-sixes")


def main() -> None:
    # (1) W33
    pts, w33_adj = cds.build_w33_f3()
    if w33_adj.shape != (40, 40):
        raise RuntimeError("W33 adjacency wrong shape")

    v0 = 0
    H12 = set(int(x) for x in np.nonzero(w33_adj[v0])[0])
    H27 = sorted(set(range(40)) - H12 - {v0})
    if len(H12) != 12 or len(H27) != 27:
        raise RuntimeError("Unexpected H12/H27 sizes")

    # (2) bad/good pairs in H27
    bad_edges_global = []
    good_edges_global = []
    for a in range(len(H27)):
        for b in range(a + 1, len(H27)):
            u = H27[a]
            v = H27[b]
            # firewall applies to non-orth pairs: u,v are non-edges of W33
            if w33_adj[u, v]:
                continue
            Nu = set(int(x) for x in np.nonzero(w33_adj[u])[0])
            Nv = set(int(x) for x in np.nonzero(w33_adj[v])[0])
            common = Nu & Nv
            if common <= H12:
                bad_edges_global.append((u, v))
            else:
                good_edges_global.append((u, v))

    if len(bad_edges_global) != 27 or len(good_edges_global) != 216:
        raise RuntimeError("Unexpected firewall split counts")

    # Build kernel adjacency on local indices 0..26 for H27.
    idx = {u: i for i, u in enumerate(H27)}
    kernel_adj = np.zeros((27, 27), dtype=bool)
    bad_edges = set()
    for u, v in good_edges_global:
        i, j = idx[u], idx[v]
        kernel_adj[i, j] = kernel_adj[j, i] = True
    for u, v in bad_edges_global:
        i, j = idx[u], idx[v]
        bad_edges.add((min(i, j), max(i, j)))

    # bad triangles on H27 (local)
    bad_tris = _triangles_from_edges(27, bad_edges)
    bad_tris = [tuple(sorted(t)) for t in bad_tris]
    bad_tris = sorted(set(bad_tris))
    if len(bad_tris) != 9:
        raise RuntimeError(f"Expected 9 bad triangles, got {len(bad_tris)}")

    # (3) Schläfli graph from the same orbit used in signed action artifacts.
    act = json.loads(
        (ROOT / "artifacts" / "we6_signed_action_on_27.json").read_text(
            encoding="utf-8"
        )
    )
    oi_ref = int(act["reference_orbit"]["orbit_index"])
    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    o27 = orbits[oi_ref]
    schlafli_adj, _ = cds.build_schlafli_adjacency(roots, o27)

    # (4) Find isomorphism kernel -> schlafli
    f = _find_isomorphism_via_double_sixes(kernel_adj, schlafli_adj)

    # (5) Map bad triangles to Schläfli indices
    mapped_bad_tris = [tuple(sorted((f[a], f[b], f[c]))) for (a, b, c) in bad_tris]
    mapped_bad_tris = sorted(set(mapped_bad_tris))
    if len(mapped_bad_tris) != 9:
        raise RuntimeError("Bad triangle mapping produced duplicates")

    # Convert Schläfli *orbit-local* indices to the canonical E6-id indexing used by selection_rules_report.
    canon_data = json.loads(
        (ROOT / "artifacts" / "canonical_su3_gauge_and_cubic.json").read_text(
            encoding="utf-8"
        )
    )
    e6_keys_27 = [tuple(int(x) for x in k) for k in canon_data["e6_keys_27_k2"]]
    key_to_e6id = {k: i for i, k in enumerate(e6_keys_27)}
    pos_to_e6id = []
    for pos, ridx in enumerate(o27):
        kk = canon.e6_key(roots[ridx])
        eid = key_to_e6id.get(tuple(int(x) for x in kk))
        if eid is None:
            raise RuntimeError("Failed to map orbit vertex to canonical E6 id")
        pos_to_e6id.append(int(eid))

    mapped_bad_triads_e6id = [
        tuple(sorted((pos_to_e6id[a], pos_to_e6id[b], pos_to_e6id[c])))
        for (a, b, c) in mapped_bad_tris
    ]
    mapped_bad_triads_e6id = sorted(set(mapped_bad_triads_e6id))
    if len(mapped_bad_triads_e6id) != 9:
        raise RuntimeError("E6-id bad triads collapsed unexpectedly")

    # Compute the 45 meet-graph triangles in the Schläfli model.
    meet = (~schlafli_adj) & (~np.eye(27, dtype=bool))
    triads = []
    for a in range(27):
        for b in range(a + 1, 27):
            if not meet[a, b]:
                continue
            for c in range(b + 1, 27):
                if meet[a, c] and meet[b, c]:
                    triads.append((a, b, c))
    triads = sorted(triads)
    triad_set = set(triads)
    if len(triads) != 45:
        raise RuntimeError(f"Expected 45 meet triangles, got {len(triads)}")
    if any(t not in triad_set for t in mapped_bad_tris):
        raise RuntimeError("Some mapped bad triangles are not meet-graph triads")

    # Cross-tabulate against selection report (parity under each generator).
    sel = json.loads(
        (ROOT / "artifacts" / "selection_rules_report.json").read_text(encoding="utf-8")
    )
    by_gen = {}
    for g in sel["generators"]:
        name = g["name"]
        parity_map = g["triad_parity"]  # dict "i,j,k" -> ±1
        bad_parities = [int(parity_map["%d,%d,%d" % t]) for t in mapped_bad_triads_e6id]
        by_gen[name] = {
            "bad_triads_parity_hist": {
                str(k): int(v) for k, v in sorted(Counter(bad_parities).items())
            },
            "bad_triads": [
                {"triad": list(t), "parity": int(parity_map["%d,%d,%d" % t])}
                for t in mapped_bad_triads_e6id
            ],
        }

    out = {
        "status": "ok",
        "w33": {"v0": int(v0), "H12": sorted(H12), "H27": H27},
        "counts": {
            "bad_edges": int(len(bad_edges_global)),
            "good_edges": int(len(good_edges_global)),
            "bad_triangles": 9,
            "triads_total": 45,
        },
        "bad_triangles_H27_local": [list(t) for t in bad_tris],
        "bad_triangles_Schlafli_orbit_index": [list(t) for t in mapped_bad_tris],
        "bad_triangles_Schlafli_e6id": [list(t) for t in mapped_bad_triads_e6id],
        "selection_parity_on_bad_triads": by_gen,
    }

    out_json = ROOT / "artifacts" / "firewall_bad_triads_mapping.json"
    out_json.write_text(json.dumps(out, indent=2, default=int), encoding="utf-8")

    # Minimal markdown summary.
    md = []
    md.append("# Firewall bad triangles mapped to cubic triads")
    md.append("")
    md.append(f"- v0 = {v0}")
    md.append(f"- bad edges: {out['counts']['bad_edges']} (should be 27)")
    md.append(f"- bad triangles: {out['counts']['bad_triangles']} (should be 9)")
    md.append("")
    md.append("## Bad triads (Schläfli indices)")
    for t in mapped_bad_triads_e6id:
        md.append(f"- {t}")
    md.append("")
    md.append("## Parity histograms on bad triads")
    for name, info in by_gen.items():
        md.append(f"- {name}: {info['bad_triads_parity_hist']}")
    out_md = ROOT / "artifacts" / "firewall_bad_triads_mapping.md"
    out_md.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
