#!/usr/bin/env python3
"""
Construct an E6 cubic sign assignment using Vavilov's distance-parity rule and compare to cocycle signs.

Reference (distance rule for the 27 of E6 / cubic form signs):
  A.V. Vavilov, E6 and E7 in the theory of cubics.
  (See the "Signs for triads" paragraph in the PDF.)

We:
  1) Build the 27 E6 weights as E6-projections of one SU(3)=3 color orbit in E8.
  2) Build the E6 weight-diagram graph: connect weights differing by a simple E6 root.
  3) Enumerate the 45 "triads" (tritangent planes) as meet-graph triangles.
  4) Choose a deterministic model triad t0 and define a sign on each triad by parity of
     half the sum of graph distances between corresponding entries.
  5) Compare this sign pattern to the cocycle-derived sign solution in
     `artifacts/e6_cubic_sign_gauge_solution.json`, up to variable sign flips.

Outputs:
  artifacts/e6_cubic_vavilov_signs.json
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter, deque
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


SU3_ALPHA = np.array([1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
SU3_BETA = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0])


def k2(r: np.ndarray) -> Tuple[int, ...]:
    return tuple(int(round(2 * float(x))) for x in r.tolist())


def sign_to_bit(s: int) -> int:
    return 1 if s == -1 else 0


def bit_to_sign(b: int) -> int:
    return -1 if b else 1


def su3_weight(r: np.ndarray) -> Tuple[int, int]:
    return (
        int(round(float(np.dot(r, SU3_ALPHA)))),
        int(round(float(np.dot(r, SU3_BETA)))),
    )


def proj_to_su3(r: np.ndarray) -> np.ndarray:
    A = np.stack([SU3_ALPHA, SU3_BETA], axis=1)
    G = A.T @ A
    coeffs = np.linalg.solve(G, A.T @ r)
    return A @ coeffs


def e6_vec(r: np.ndarray) -> np.ndarray:
    return r - proj_to_su3(r)


def build_e6id_data():
    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    orbit_sizes = [len(o) for o in orbits]
    assert sorted(orbit_sizes) == [1, 1, 1, 1, 1, 1, 27, 27, 27, 27, 27, 27, 72]

    mix_orbs = [oi for oi, sz in enumerate(orbit_sizes) if sz == 27]
    weights = {oi: su3_weight(roots[orbits[oi][0]]) for oi in mix_orbs}
    weights_3 = {(1, 0), (-1, 1), (0, -1)}
    color_orbs = sorted(
        [oi for oi in mix_orbs if weights[oi] in weights_3], key=lambda x: weights[x]
    )
    assert len(color_orbs) == 3

    # E6 ids by projection equality across three color orbits.
    e6_groups: Dict[Tuple[int, ...], int] = {}
    root_to_e6id: Dict[int, int] = {}
    for oi in color_orbs:
        for ridx in orbits[oi]:
            k = tuple(int(round(2 * float(x))) for x in e6_vec(roots[ridx]).tolist())
            if k not in e6_groups:
                e6_groups[k] = len(e6_groups)
            root_to_e6id[ridx] = e6_groups[k]
    assert len(e6_groups) == 27

    # Pick representatives from the first color orbit for each e6id.
    reps = [-1] * 27
    base_orb = color_orbs[0]
    for ridx in orbits[base_orb]:
        reps[root_to_e6id[ridx]] = ridx
    if any(x == -1 for x in reps):
        raise RuntimeError("Missing representative for some e6id")

    e6weights = np.array([e6_vec(roots[ridx]) for ridx in reps])
    return roots, orbits, color_orbs, weights, root_to_e6id, reps, e6weights


def build_weight_graph(e6weights: np.ndarray) -> List[List[int]]:
    # Edges when weight difference is ± a simple E6 root.
    e6_simple = cds.E6_SIMPLE_ROOTS
    simple_k2 = [k2(a) for a in e6_simple]

    keys = [tuple(int(round(2 * float(x))) for x in w.tolist()) for w in e6weights]
    key_to_id = {k: i for i, k in enumerate(keys)}

    adj: List[List[int]] = [[] for _ in range(27)]
    for i, ki in enumerate(keys):
        for a in simple_k2:
            kp = tuple(ki[t] + a[t] for t in range(8))
            km = tuple(ki[t] - a[t] for t in range(8))
            j = key_to_id.get(kp)
            if j is not None:
                adj[i].append(j)
            j = key_to_id.get(km)
            if j is not None:
                adj[i].append(j)
    # Dedup
    adj = [sorted(set(nbrs)) for nbrs in adj]
    return adj


def all_pairs_dist(adj: List[List[int]]) -> List[List[int]]:
    n = len(adj)
    dist = [[10**9] * n for _ in range(n)]
    for s in range(n):
        dist[s][s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if dist[s][v] > dist[s][u] + 1:
                    dist[s][v] = dist[s][u] + 1
                    q.append(v)
    return dist


def triads_from_meet_graph(
    roots: np.ndarray, orbits: List[List[int]], reps: List[int]
) -> List[Tuple[int, int, int]]:
    # Use the base orbit induced by the chosen reps: these are root indices.
    base_roots = roots[reps]
    gram = np.rint(base_roots @ base_roots.T).astype(int)
    meet = gram == 0
    np.fill_diagonal(meet, False)
    triads = []
    for i in range(27):
        for j in range(i + 1, 27):
            if not meet[i, j]:
                continue
            for k in range(j + 1, 27):
                if meet[i, k] and meet[j, k]:
                    triads.append((i, j, k))
    if len(triads) != 45:
        raise RuntimeError(f"Expected 45 triads, got {len(triads)}")
    return sorted(triads)


def vavilov_signs(
    triads: List[Tuple[int, int, int]], dist: List[List[int]]
) -> Dict[Tuple[int, int, int], int]:
    raise RuntimeError("Use vavilov_signs_unordered")


def vavilov_signs_unordered(
    triads: List[Tuple[int, int, int]],
    dist: List[List[int]],
    model_ordered: Tuple[int, int, int],
) -> Tuple[Dict[Tuple[int, int, int], int], Dict[str, int]]:
    """
    Apply a robust "unordered" variant:
      for each triad t (unordered), consider the 6 ways to match its 3 vertices to (a0,b0,c0).
      If all 6 matchings give the same parity of (dist sum)/2 (and the sum is always even),
      define the sign by that parity; otherwise count it as ambiguous.
    """

    from itertools import permutations

    a0, b0, c0 = model_ordered
    out: Dict[Tuple[int, int, int], int] = {}
    ambiguous = 0
    odd = 0
    for t in triads:
        parities = set()
        for a, b, c in permutations(t):
            s = dist[a][a0] + dist[b][b0] + dist[c][c0]
            if s % 2 != 0:
                odd += 1
                continue
            parities.add((s // 2) & 1)
        if len(parities) != 1:
            ambiguous += 1
            continue
        out[t] = -1 if (next(iter(parities)) == 1) else 1
    stats = {"ambiguous": ambiguous, "odd_sums": odd, "defined": len(out)}
    return out, stats


def solve_variable_flip_between_sign_patterns(
    triads: List[Tuple[int, int, int]],
    d1: Dict[Tuple[int, int, int], int],
    d2: Dict[Tuple[int, int, int], int],
) -> Tuple[bool, Dict[str, object]]:
    """
    Solve for bits s_i and global bit g such that:
      d2(t) = (-1)^g * (-1)^{s_i+s_j+s_k} d1(t)
    for all triads t=(i,j,k).
    """

    # 28 variables: 27 vertex flips + global.
    nvars = 28

    rows: List[Tuple[int, int]] = []
    for i, j, k in triads:
        mask = 0
        mask ^= 1 << i
        mask ^= 1 << j
        mask ^= 1 << k
        mask ^= 1 << 27  # global
        rhs = sign_to_bit(d2[(i, j, k)]) ^ sign_to_bit(d1[(i, j, k)])
        rows.append((mask, rhs))

    pivots: Dict[int, Tuple[int, int]] = {}
    for mask, rhs in rows:
        m = mask
        r = rhs
        while m:
            p = m.bit_length() - 1
            if p in pivots:
                pm, pr = pivots[p]
                m ^= pm
                r ^= pr
            else:
                pivots[p] = (m, r)
                break
        if m == 0 and r == 1:
            return False, {"ok": False, "rank": len(pivots)}

    sol = [0] * nvars
    for p in sorted(pivots.keys(), reverse=True):
        m, r = pivots[p]
        rest = m & ~(1 << p)
        val = r
        while rest:
            q = rest & -rest
            idx = q.bit_length() - 1
            val ^= sol[idx]
            rest ^= q
        sol[p] = val

    # Verify
    for i, j, k in triads:
        lhs = sign_to_bit(d2[(i, j, k)])
        rhs = sign_to_bit(d1[(i, j, k)]) ^ sol[i] ^ sol[j] ^ sol[k] ^ sol[27]
        if lhs != rhs:
            return False, {"ok": False, "rank": len(pivots), "verify_failed": True}

    return True, {"ok": True, "rank": len(pivots), "s_bits": sol[:27], "g_bit": sol[27]}


def load_cocycle_signs() -> Dict[Tuple[int, int, int], int]:
    data = json.loads(
        (ROOT / "artifacts" / "e6_cubic_sign_gauge_solution.json").read_text(
            encoding="utf-8"
        )
    )
    d: Dict[Tuple[int, int, int], int] = {}
    for ent in data["solution"]["d_triples"]:
        t = tuple(sorted(int(x) for x in ent["triple"]))
        d[t] = int(ent["sign"])
    if len(d) != 45:
        raise RuntimeError("Expected 45 cocycle d-triples")
    return d


def main() -> None:
    roots, orbits, _color_orbs, _weights, _root_to_e6id, reps, e6weights = (
        build_e6id_data()
    )
    adj = build_weight_graph(e6weights)
    dist = all_pairs_dist(adj)
    triads = triads_from_meet_graph(roots, orbits, reps)
    d_coc = load_cocycle_signs()

    # Search over model triad choice and its 6 orderings.
    from itertools import permutations

    best = None
    best_entry = None
    best_defined = -1
    best_partial = None
    best_partial_entry = None
    for t0 in triads:
        for model in permutations(t0):
            d_vav, stats = vavilov_signs_unordered(triads, dist, model)
            if stats["defined"] > best_defined:
                best_defined = stats["defined"]
                best_partial = d_vav
                best_partial_entry = {
                    "model_triad_ordered": list(model),
                    "stats": stats,
                    "vavilov_sign_distribution": dict(Counter(d_vav.values())),
                    "flip_solution_exists": False,
                    "flip": None,
                }

            if stats["defined"] != 45:
                continue

            ok_flip, flip = solve_variable_flip_between_sign_patterns(
                triads, d_vav, d_coc
            )
            entry = {
                "model_triad_ordered": list(model),
                "stats": stats,
                "vavilov_sign_distribution": dict(Counter(d_vav.values())),
                "flip_solution_exists": bool(ok_flip),
                "flip": flip,
            }
            if ok_flip:
                best = d_vav
                best_entry = entry
                break
        if best_entry is not None:
            break

    if best_entry is None:
        # No model produced a fully-defined 45/45 assignment under the unordered parity-stability rule.
        # Report the best partial coverage found.
        best_entry = best_partial_entry

    out = {
        "status": "ok",
        "counts": {
            "triads": 45,
            "cocycle_sign_distribution": dict(Counter(d_coc.values())),
        },
        "best_vavilov_fit": best_entry,
    }

    out_path = ROOT / "artifacts" / "e6_cubic_vavilov_signs.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote", out_path)
    print(
        "Flip solution exists?",
        bool(best_entry and best_entry.get("flip_solution_exists")),
    )


if __name__ == "__main__":
    main()
