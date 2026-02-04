#!/usr/bin/env python3
"""
Certificate: the E6 cubic triads form an affine-line system in the Heisenberg model on H27.

Inputs (repo-native):
  - artifacts/canonical_su3_gauge_and_cubic.json            (45 signed cubic triads on labels 0..26)
  - artifacts/sage_h27_to_schlafli_effective_triads_conjugacy.json
        (canonical identification of W33 local H27 indices with Schläfli/E6 ids)
  - artifacts/firewall_bad_triads_mapping.json              (the 9 forbidden triads for v0=0)

We:
  1) Build W33 as the symplectic orthogonality graph on PG(3,3) (40 points).
  2) For v0=0, compute the Heisenberg coordinates (u in F3^2, z in Z3) on H27.
  3) Transport that coordinate system onto the Schläfli/E6-id labeling via the Sage conjugacy map.
  4) Verify:
       - exactly 9 cubic triads have constant u  (the Z3-center cosets / firewall-forbidden triads)
       - the remaining 36 triads have u's collinear in F3^2 (affine lines), with 12 distinct u-lines
         and 3 Z3-lifts per u-line
       - the 9 constant-u triads match the firewall bad-triad set exactly.

Outputs:
  - artifacts/e6_cubic_affine_heisenberg_model.json
  - artifacts/e6_cubic_affine_heisenberg_model.md
"""

from __future__ import annotations

import json
from collections import defaultdict
from itertools import product
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

IN_CUBIC = ROOT / "artifacts" / "canonical_su3_gauge_and_cubic.json"
IN_CONJ = ROOT / "artifacts" / "sage_h27_to_schlafli_effective_triads_conjugacy.json"
IN_FW = ROOT / "artifacts" / "firewall_bad_triads_mapping.json"

OUT_JSON = ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json"
OUT_MD = ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.md"


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _construct_w33_adj() -> np.ndarray:
    """
    Build W33 as the symplectic polar graph on PG(3,3):
      vertices = 1D subspaces of F3^4  (40 points)
      edge(i,j)=1 iff omega(v_i, v_j)=0 (symplectic orthogonality)
    """
    F3 = [0, 1, 2]
    vectors = [v for v in product(F3, repeat=4) if any(x != 0 for x in v)]
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

    n = len(proj_points)
    if n != 40:
        raise RuntimeError(f"Expected 40 projective points, got {n}")

    def omega(x, y):
        return (x[0] * y[2] - x[2] * y[0] + x[1] * y[3] - x[3] * y[1]) % 3

    adj = np.zeros((n, n), dtype=np.int8)
    for i in range(n):
        for j in range(i + 1, n):
            if omega(proj_points[i], proj_points[j]) == 0:
                adj[i, j] = adj[j, i] = 1
    return adj


def _h12_triangles(adj: np.ndarray, v0: int) -> List[Tuple[int, int, int]]:
    """Connected components among neighbors of v0 (they form 4 disjoint triangles)."""
    nbrs = [i for i in range(adj.shape[0]) if adj[v0, i] == 1]
    visited: set[int] = set()
    comps: List[Tuple[int, int, int]] = []
    for start in nbrs:
        if start in visited:
            continue
        stack = [start]
        comp: List[int] = []
        while stack:
            v = stack.pop()
            if v in visited:
                continue
            visited.add(v)
            comp.append(v)
            for u in nbrs:
                if u not in visited and adj[v, u]:
                    stack.append(u)
        comp = sorted(comp)
        if len(comp) != 3:
            raise RuntimeError(
                f"Expected H12 components to be triangles, got size {len(comp)}"
            )
        comps.append((comp[0], comp[1], comp[2]))
    comps = sorted(comps)
    if len(comps) != 4:
        raise RuntimeError(f"Expected 4 H12 triangles, got {len(comps)}")
    return comps


def _h27_heisenberg_coords_v0(
    adj: np.ndarray, *, v0: int
) -> Tuple[List[int], Dict[int, Tuple[Tuple[int, int], int]]]:
    """
    Return (H27_global_list, labeling_global) for the chosen v0, where:
      labeling_global[vertex] = ((u1,u2), z) with u in F3^2 and z in Z3.

    Notes:
      - This is the same constructive procedure used in tools/h27_heisenberg_model.py.
      - The (u1,u2) coordinate assignment is a fixed convention (a gauge); different valid
        conventions are related by GL(2,3) and z-shifts.
    """
    if v0 < 0 or v0 >= adj.shape[0]:
        raise ValueError("invalid v0")

    h12_tris = _h12_triangles(adj, v0)
    tri_index = [{v: i for i, v in enumerate(tri)} for tri in h12_tris]
    h27 = [i for i in range(adj.shape[0]) if i != v0 and adj[v0, i] == 0]

    # 4-tuple signature: which vertex in each H12 triangle does u see?
    tuple_map: Dict[int, Tuple[int, int, int, int]] = {}
    for u in h27:
        sig: List[int] = []
        for t in range(4):
            found = None
            for v in h12_tris[t]:
                if adj[u, v]:
                    found = tri_index[t][v]
                    break
            sig.append(found if found is not None else -1)
        tuple_map[u] = tuple(sig)  # type: ignore[assignment]

    # 9 fibers keyed by signature
    fibers: Dict[Tuple[int, int, int, int], List[int]] = defaultdict(list)
    for u in h27:
        fibers[tuple_map[u]].append(u)
    for k in fibers:
        fibers[k].sort()
    fiber_keys = sorted(fibers.keys())
    if len(fiber_keys) != 9 or any(len(fibers[k]) != 3 for k in fiber_keys):
        raise RuntimeError("Expected 9 fibers of size 3 for H27")

    # Fixed coordinate gauge for the 9 signatures (matches tools/h27_heisenberg_model.py).
    coords: Dict[Tuple[int, int, int, int], Tuple[int, int]] = {
        (0, 0, 0, 0): (0, 0),
        (0, 1, 1, 1): (1, 0),
        (0, 2, 2, 2): (2, 0),
        (1, 0, 1, 2): (0, 1),
        (1, 1, 2, 0): (1, 1),
        (1, 2, 0, 1): (2, 1),
        (2, 0, 2, 1): (0, 2),
        (2, 1, 0, 2): (1, 2),
        (2, 2, 1, 0): (2, 2),
    }
    if set(coords.keys()) != set(fiber_keys):
        raise RuntimeError("Fiber signature set mismatch vs fixed coordinate gauge")

    # For each ordered pair of fibers (A,B), adjacency gives a permutation of the 3 elements.
    P: List[List[Tuple[int, int, int] | None]] = [[None] * 9 for _ in range(9)]
    for i, ka in enumerate(fiber_keys):
        for j, kb in enumerate(fiber_keys):
            if i == j:
                continue
            perm: List[int] = []
            for va in fibers[ka]:
                match = None
                for jb, vb in enumerate(fibers[kb]):
                    if adj[va, vb]:
                        match = jb
                        break
                if match is None:
                    raise RuntimeError("Expected unique adjacency match between fibers")
                perm.append(match)
            P[i][j] = (perm[0], perm[1], perm[2])

    s3 = [
        (0, 1, 2),
        (0, 2, 1),
        (1, 0, 2),
        (1, 2, 0),
        (2, 0, 1),
        (2, 1, 0),
    ]
    c3 = {(0, 1, 2), (1, 2, 0), (2, 0, 1)}

    def perm_compose(
        p: Tuple[int, int, int], q: Tuple[int, int, int]
    ) -> Tuple[int, int, int]:
        return (p[q[0]], p[q[1]], p[q[2]])

    def perm_inverse(p: Tuple[int, int, int]) -> Tuple[int, int, int]:
        inv = [0, 0, 0]
        for i, j in enumerate(p):
            inv[j] = i
        return (inv[0], inv[1], inv[2])

    assignments: Dict[int, Tuple[int, int, int]] = {0: (0, 1, 2)}
    order = list(range(1, 9))

    def ok_with(i: int, perm_i: Tuple[int, int, int]) -> bool:
        for j, perm_j in assignments.items():
            Pji = P[j][i]
            if Pji is None:
                continue
            eff = perm_compose(perm_inverse(perm_i), perm_compose(Pji, perm_j))
            if eff not in c3:
                return False
        return True

    def backtrack(k: int) -> bool:
        if k == len(order):
            return True
        i = order[k]
        for perm in s3:
            if ok_with(i, perm):
                assignments[i] = perm
                if backtrack(k + 1):
                    return True
                del assignments[i]
        return False

    if not backtrack(0):
        raise RuntimeError("Failed to solve fiber Z3 assignment")

    # vertex -> ((u1,u2), z)
    labeling: Dict[int, Tuple[Tuple[int, int], int]] = {}
    for i, key in enumerate(fiber_keys):
        perm = assignments[i]
        for pos, v in enumerate(fibers[key]):
            labeling[v] = (coords[key], int(perm[pos]))
    return sorted(h27), labeling


def _det2(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    """det([a;b]) in F3."""
    return (a[0] * b[1] - a[1] * b[0]) % 3


def _collinear(u: Tuple[int, int], v: Tuple[int, int], w: Tuple[int, int]) -> bool:
    """Affine collinearity in F3^2: det(v-u, w-u) == 0."""
    vu = ((v[0] - u[0]) % 3, (v[1] - u[1]) % 3)
    wu = ((w[0] - u[0]) % 3, (w[1] - u[1]) % 3)
    return _det2(vu, wu) == 0


def _triad_key(tri: Iterable[int]) -> Tuple[int, int, int]:
    a, b, c = sorted(int(x) for x in tri)
    return (a, b, c)


def main() -> None:
    cubic = _load_json(IN_CUBIC)
    conj = _load_json(IN_CONJ)
    fw = _load_json(IN_FW)

    triads: List[List[int]] = list(cubic["triads"])
    if len(triads) != 45:
        raise RuntimeError(
            "Expected 45 cubic triads in canonical_su3_gauge_and_cubic.json"
        )

    # local index -> e6id, and H27 global list for v0=0
    loc2e6: List[int] = [int(x) for x in conj["h27_local_to_schlafli_e6id"]]
    h27_global_expected: List[int] = [int(x) for x in conj["w33"]["H27_global"]]

    # Build Heisenberg coords on H27 (global vertex ids)
    adj = _construct_w33_adj()
    v0 = int(conj["w33"]["v0"])
    h27_global, labeling_global = _h27_heisenberg_coords_v0(adj, v0=v0)
    if h27_global != h27_global_expected:
        raise RuntimeError(
            "H27_global mismatch: expected Sage/Python ordering alignment"
        )

    # local index -> ((u1,u2), z)
    loc2hz: Dict[int, Tuple[Tuple[int, int], int]] = {}
    for loc, gv in enumerate(h27_global):
        loc2hz[loc] = labeling_global[gv]

    # e6id -> ((u1,u2), z)
    e6_to_hz: Dict[int, Tuple[Tuple[int, int], int]] = {}
    for loc, e6id in enumerate(loc2e6):
        e6_to_hz[int(e6id)] = loc2hz[loc]
    if set(e6_to_hz.keys()) != set(range(27)):
        raise RuntimeError("Expected e6 ids 0..26 to all appear exactly once")

    # firewall bad triads (in e6id labels)
    fw_bad = {_triad_key(t) for t in fw["bad_triangles_Schlafli_e6id"]}
    if len(fw_bad) != 9:
        raise RuntimeError("Expected 9 firewall bad triads")

    # classify cubic triads by u-geometry
    fiber_triads: List[Tuple[int, int, int]] = []
    line_triads: List[Tuple[int, int, int]] = []
    other: List[Tuple[int, int, int]] = []

    uline_to_triads: Dict[
        Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]],
        List[Tuple[int, int, int]],
    ] = defaultdict(list)

    for t in triads:
        key = _triad_key(t)
        hz = [e6_to_hz[i] for i in key]
        us = [p[0] for p in hz]
        if us[0] == us[1] == us[2]:
            fiber_triads.append(key)
            continue
        if _collinear(us[0], us[1], us[2]):
            line_triads.append(key)
            uline = tuple(sorted(set(us)))  # type: ignore[assignment]
            if len(uline) != 3:
                raise RuntimeError("Unexpected uline size")
            uline_to_triads[uline].append(key)
            continue
        other.append(key)

    fiber_triads.sort()
    line_triads.sort()
    other.sort()

    # checks
    if len(fiber_triads) != 9:
        raise RuntimeError(f"Expected 9 constant-u triads, got {len(fiber_triads)}")
    if len(line_triads) != 36:
        raise RuntimeError(f"Expected 36 collinear-u triads, got {len(line_triads)}")
    if other:
        raise RuntimeError(f"Unexpected non-affine triads: {other[:5]}")

    # every affine u-line should have exactly 3 Z3 lifts (= 3 triads)
    uline_sizes = sorted(len(v) for v in uline_to_triads.values())
    if len(uline_to_triads) != 12 or uline_sizes != [3] * 12:
        raise RuntimeError(
            f"Expected 12 distinct u-lines with 3 lifts each; got {len(uline_to_triads)} with sizes {uline_sizes}"
        )

    # firewall bad triads should match the constant-u triads exactly
    if set(fiber_triads) != fw_bad:
        missing = sorted(fw_bad - set(fiber_triads))
        extra = sorted(set(fiber_triads) - fw_bad)
        raise RuntimeError(
            "Firewall bad triads do not match constant-u triads.\n"
            f"missing_from_constant_u={missing}\n"
            f"extra_in_constant_u={extra}\n"
        )

    # produce JSON
    e6_to_hz_json = {
        str(i): {
            "u": [int(e6_to_hz[i][0][0]), int(e6_to_hz[i][0][1])],
            "z": int(e6_to_hz[i][1]),
        }
        for i in range(27)
    }

    # uline -> its three lifts (triads)
    uline_items = []
    for uline in sorted(uline_to_triads.keys()):
        uline_items.append(
            {
                "u_line": [[int(a), int(b)] for (a, b) in uline],
                "triads": [list(t) for t in sorted(uline_to_triads[uline])],
            }
        )

    out = {
        "status": "ok",
        "w33": {"v0": v0, "H27_global": h27_global},
        "counts": {
            "cubic_triads_total": 45,
            "fiber_triads": len(fiber_triads),
            "affine_line_triads": len(line_triads),
            "distinct_u_lines": len(uline_to_triads),
        },
        "e6id_to_heisenberg": e6_to_hz_json,
        "fiber_triads_e6id": [list(t) for t in fiber_triads],
        "affine_u_lines": uline_items,
        "cross_checks": {
            "firewall_bad_triads_match_fiber_triads": True,
        },
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")

    # produce MD summary
    md: List[str] = []
    md.append("# E6 cubic triads = affine lines in the H27 Heisenberg model")
    md.append("")
    md.append(f"- v0: `{v0}`")
    md.append(f"- cubic triads: `{out['counts']['cubic_triads_total']}`")
    md.append(
        f"- constant-u triads (Z3-center cosets / firewall-forbidden): `{out['counts']['fiber_triads']}`"
    )
    md.append(
        f"- collinear-u triads (affine lines): `{out['counts']['affine_line_triads']}`"
    )
    md.append(
        f"- distinct u-lines: `{out['counts']['distinct_u_lines']}` (each has 3 Z3 lifts)"
    )
    md.append("")
    md.append("## Firewall match")
    md.append("- The 9 firewall-bad triads match exactly the 9 constant-u triads.")
    md.append("")
    md.append("## Interpretation (finite-geometry)")
    md.append("- Identify H27 with `F3^2 × Z3` via the Heisenberg labeling `(u,z)`.")
    md.append("- Then the 45 cubic triads are exactly:")
    md.append("  - the 9 fibers `{u}×Z3` (constant-u, forbidden by firewall), and")
    md.append("  - the 36 lifted affine lines in `F3^2` (12 u-lines × 3 Z3 lifts).")
    md.append("")
    md.append(f"Wrote `{OUT_JSON}`")
    md.append(f"Wrote `{OUT_MD}`")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
