#!/usr/bin/env python3
"""Apply Sp(4,3)->W(E6) generator mapping to canonical BFS words to build a candidate
edge->root bijection and verify triangle constraints.

The script:
 - loads canonical edge labels (`artifacts/edge_root_bijection_canonical.json`)
 - loads generator permutations (`artifacts/sp43_we6_generator_map_full_we6.json`)
 - applies BFS words to the base root to predict a root index for every edge
 - checks bijectivity and triangle constraints
 - writes summary to `checks/PART_CVII_e8_embedding_coset_match.json`
 - writes seed JSON `checks/PART_CVII_e8_embedding_coset_match_seed.json` suitable for
   `scripts/local_repair_matching.py` or `scripts/backtrack_candidate_search.py`

Use this before invoking local repair or backtracking.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def invert_perm(perm: List[int]) -> List[int]:
    n = len(perm)
    inv = [0] * n
    for i, v in enumerate(perm):
        inv[v] = i
    return inv


def build_w33_edges() -> List[Tuple[int, int]]:
    # same construction as other scripts
    F3 = [0, 1, 2]
    vectors = [v for v in __import__("itertools").product(F3, repeat=4) if any(x != 0 for x in v)]

    proj_points = []
    seen = set()
    for v in vectors:
        v = list(v)
        for i in range(4):
            if v[i] != 0:
                inv = 1 if v[i] == 1 else 2
                v = tuple((x * inv) % 3 for x in v)
                break
        if v not in seen:
            seen.add(v)
            proj_points.append(v)

    def omega(x, y):
        return (x[0] * y[2] - x[2] * y[0] + x[1] * y[3] - x[3] * y[1]) % 3

    edges = []
    for i in range(len(proj_points)):
        for j in range(i + 1, len(proj_points)):
            if omega(proj_points[i], proj_points[j]) == 0:
                edges.append((i, j))
    return edges


import argparse

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--base-root", type=int, default=None, help="override base root index to use (default from canonical mapping)")
    args = p.parse_args()

    # Load canonical file
    canonical_path = ROOT / "artifacts" / "edge_root_bijection_canonical.json"
    if not canonical_path.exists():
        raise SystemExit(f"Missing {canonical_path}; run the canonical bijection generator first")
    canonical = load_json(canonical_path)

    # Build mapping edge_index -> entry
    edge_entries: Dict[int, dict] = {int(e["edge_index"]): e for e in canonical}

    # Find base edge (word == [])
    base_entries = [e for e in edge_entries.values() if not e.get("word")]
    if not base_entries:
        raise SystemExit("No base edge with empty word found in canonical bijection")
    base_entry = base_entries[0]
    base_edge_index = int(base_entry["edge_index"])
    base_root_idx = int(base_entry["root_index"])
    if args.base_root is not None:
        base_root_idx = int(args.base_root)
    print(f"Base edge {base_edge_index} -> base root {base_root_idx}")

    # Load generator permutations
    gen_map_path = ROOT / "artifacts" / "sp43_we6_generator_map_full_we6.json"
    if not gen_map_path.exists():
        raise SystemExit(f"Missing {gen_map_path}; need generator map artifact")
    gen_data = load_json(gen_map_path)
    gens = gen_data.get("generators")
    if not gens:
        raise SystemExit("No generators found in generator map artifact")
    n_gens = len(gens)
    print(f"Loaded {n_gens} generators (each acts on 240 elements)")

    # Precompute inverses
    inv_gens = [invert_perm(g) for g in gens]

    # Apply words
    predicted = {}
    for eidx, entry in edge_entries.items():
        word: List[int] = entry.get("word", []) or []
        p = base_root_idx
        for tok in word:
            # tokens should be integers; positive -> forward, negative -> inverse (-g-1)
            if tok >= 0:
                if tok >= n_gens:
                    raise RuntimeError(f"Generator index {tok} out of range (n_gens={n_gens}) for edge {eidx}")
                p = gens[tok][p]
            else:
                idx = -tok - 1
                if idx >= n_gens:
                    raise RuntimeError(f"Inverse generator index {idx} out of range for edge {eidx}")
                p = inv_gens[idx][p]
        predicted[eidx] = int(p)

    # Validate bijectivity
    roots_used = list(predicted.values())
    uniq_roots = set(roots_used)
    bijective = len(uniq_roots) == len(predicted)
    duplicates = len(predicted) - len(uniq_roots)

    # Prepare seed JSON (seed_edges format)
    seed_edges = []
    for eidx, root_idx in sorted(predicted.items()):
        ent = edge_entries[eidx]
        seed_edges.append({
            "edge_index": int(eidx),
            "edge": ent.get("edge") or [int(ent.get("v_i", 0)), int(ent.get("v_j", 0))],
            "root_index": int(root_idx),
        })

    seed_json_path = ROOT / "checks" / "PART_CVII_e8_embedding_coset_match_seed.json"
    seed_json_path.parent.mkdir(parents=True, exist_ok=True)
    seed_json = {"seed_edges": seed_edges}
    seed_json_path.write_text(json.dumps(seed_json, indent=2), encoding="utf-8")
    print(f"Wrote seed JSON {seed_json_path} entries={len(seed_edges)}")

    # Load root coords (via compute_double_sixes)
    try:
        cds_spec = __import__("importlib.util").util.spec_from_file_location("compute_double_sixes", str(ROOT / "tools" / "compute_double_sixes.py"))
        cds = __import__("importlib.util").module_from_spec(cds_spec)
        cds_spec.loader.exec_module(cds)
        roots = cds.construct_e8_roots()
    except Exception:
        # fallback: try load explicit decomposition artifact
        decomp_path = ROOT / "artifacts" / "explicit_bijection_decomposition.json"
        if decomp_path.exists():
            dd = load_json(decomp_path)
            roots = dd.get("root_coords", [])
        else:
            raise

    # Build triangles
    from itertools import combinations

    # Reconstruct W33 edges (vertex labels) to determine triangle edge indices
    w33_edges = build_w33_edges()
    # Build mapping edge_index -> pair
    edge_to_pair = {int(eidx): tuple(map(int, edge_entries[eidx].get("edge", w33_edges[int(eidx)]))) for eidx in edge_entries}

    # Build triangle list (triples of edge indices) like other scripts
    # Map vertex pair to edge index
    pair_to_edge = {tuple(sorted(v)): k for k, v in edge_to_pair.items()}
    nverts = 40
    # Reconstruct adjacency
    adj = {i: set() for i in range(nverts)}
    for (i, j) in edge_to_pair.values():
        adj[i].add(j)
        adj[j].add(i)

    triangles = []
    for a in range(nverts):
        for b in sorted(adj[a]):
            if b <= a:
                continue
            for c in sorted(adj[b]):
                if c <= b:
                    continue
                if a in adj[c]:
                    e_ab = pair_to_edge[(a, b)]
                    e_bc = pair_to_edge[(b, c)]
                    e_ac = pair_to_edge[(a, c)]
                    triangles.append((e_ab, e_bc, e_ac))

    # Count triangle satisfactions
    tri_ok = 0
    tri_bad = []
    for (e1, e2, e3) in triangles:
        r1 = roots[predicted[e1]]
        r2 = roots[predicted[e2]]
        r3 = roots[predicted[e3]]
        # require r1 + r2 == r3
        ok = all(int(r1[i] + r2[i]) == int(r3[i]) for i in range(8))
        if ok:
            tri_ok += 1
        else:
            tri_bad.append((e1, e2, e3))

    tri_total = len(triangles)

    out = {
        "bijective": bool(bijective),
        "duplicates": int(duplicates),
        "n_edges": len(predicted),
        "triangles_total": tri_total,
        "triangles_ok": tri_ok,
        "triangles_frac": float(tri_ok) / float(tri_total) if tri_total else 0.0,
    }

    out_path = ROOT / "checks" / "PART_CVII_e8_embedding_coset_match.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")

    # If bijective & all triangles satisfied, export a verified embedding artifact
    if bijective and tri_ok == tri_total:
        verified = {
            "found": True,
            "method": "coset_generator_mapping",
            "base_edge": int(base_edge_index),
            "base_root": int(base_root_idx),
            "notes": "All triangles satisfied by generator-induced mapping",
        }
        verified_path = ROOT / "checks" / "PART_CVII_e8_embedding_coset_match_verified.json"
        verified_path.write_text(json.dumps(verified, indent=2), encoding="utf-8")
        print(f"Full embedding verified and wrote {verified_path}")

    # Also write a simple edge->root mapping artifact
    map_art = ROOT / "artifacts" / "edge_root_bijection_coset_match.json"
    map_list = []
    for eidx in sorted(predicted.keys()):
        ent = edge_entries[eidx]
        r = int(predicted[eidx])
        map_list.append({
            "edge_index": int(eidx),
            "edge": ent.get("edge", []),
            "root_index": r,
            "root_coords": roots[r],
        })
    map_art.write_text(json.dumps(map_list, indent=2), encoding="utf-8")
    print(f"Wrote mapping artifact {map_art}")


if __name__ == "__main__":
    main()
