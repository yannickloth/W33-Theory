#!/usr/bin/env python3
"""
TOE: Firewall affine-plane (AG(2,3)) quotient geometry and the 36↔36 duality.

In the canonical Schläfli (27-line) sector (E6-id labeling):
  - The firewall "bad edges" form 9 vertex-disjoint meet-triangles (bad triads),
    partitioning the 27 vertices.
  - The remaining 36 meet-triangles (cubic triads) split as:
      12 distinct triples of bad-triad blocks (these are the 12 affine lines of AG(2,3)),
      each with 3 lifts (a Z3 kernel element cycles the lifts).
  - Independently, the 36 double-sixes also split by the same 12 affine lines:
      each double-six uses exactly 6 of the 9 blocks (2 vertices per block) and
      omits exactly 3 blocks forming an affine line; again 3 lifts per line.

This script:
  1) Constructs the AG(2,3) structure on the 9 bad blocks.
  2) Confirms that allowed triads are exactly 12 lines × 3 lifts.
  3) Confirms that double-sixes are exactly complements of those 12 lines × 3 lifts.
  4) Extracts the kernel Z3 element (order 3) from the W(E6) action on the 27 that
     fixes blocks and cycles inside each block, and uses it to align the 3 lifts per line.

Outputs:
  - artifacts/toe_affine_plane_duality.json
  - artifacts/toe_affine_plane_duality.md
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter, deque
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to import {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


toe_dynamics = _load_module(ROOT / "tools" / "toe_dynamics.py", "toe_dynamics")


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _compose_perm(p: Tuple[int, ...], q: Tuple[int, ...]) -> Tuple[int, ...]:
    """Return composition p∘q (apply q first, then p)."""
    return tuple(p[i] for i in q)


def _cycle_decomposition(perm: Tuple[int, ...]) -> List[Tuple[int, ...]]:
    n = len(perm)
    seen = [False] * n
    cycles: List[Tuple[int, ...]] = []
    for i in range(n):
        if seen[i]:
            continue
        if perm[i] == i:
            seen[i] = True
            continue
        cyc: List[int] = []
        j = i
        while not seen[j]:
            seen[j] = True
            cyc.append(j)
            j = perm[j]
        if len(cyc) > 1:
            cycles.append(tuple(cyc))
    return sorted(cycles, key=len, reverse=True)


def _act_on_triads(
    perm: Tuple[int, ...], triads: Iterable[Tuple[int, int, int]]
) -> Tuple[Tuple[int, int, int], ...]:
    out = []
    for a, b, c in triads:
        out.append(tuple(sorted((perm[a], perm[b], perm[c]))))
    return tuple(sorted(out))


def _act_on_triad(
    perm: Tuple[int, ...], triad: Tuple[int, int, int]
) -> Tuple[int, int, int]:
    a, b, c = triad
    return tuple(sorted((perm[a], perm[b], perm[c])))


def _act_on_double_six(
    perm: Tuple[int, ...], ds: Tuple[Tuple[int, ...], Tuple[int, ...]]
) -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
    A, B = ds
    A2 = tuple(sorted(perm[i] for i in A))
    B2 = tuple(sorted(perm[i] for i in B))
    return (A2, B2) if A2 <= B2 else (B2, A2)


def _find_k_cliques(adj: np.ndarray, k: int) -> List[Tuple[int, ...]]:
    n = adj.shape[0]
    nbr = [set(np.nonzero(adj[i])[0].tolist()) for i in range(n)]
    out: List[Tuple[int, ...]] = []

    def backtrack(clique: List[int], candidates: set[int]) -> None:
        if len(clique) == k:
            out.append(tuple(clique))
            return
        if len(clique) + len(candidates) < k:
            return
        cand_list = sorted(candidates)
        while cand_list:
            v = cand_list.pop(0)
            new_cand = candidates & nbr[v]
            backtrack(clique + [v], new_cand)
            candidates.remove(v)

    for v in range(n):
        backtrack([v], set(range(v + 1, n)) & nbr[v])
    return out


def _find_double_sixes(
    skew_adj: np.ndarray,
) -> List[Tuple[Tuple[int, ...], Tuple[int, ...]]]:
    k6s = _find_k_cliques(skew_adj, 6)
    used: set[Tuple[int, ...]] = set()
    out: List[Tuple[Tuple[int, ...], Tuple[int, ...]]] = []
    for A in k6s:
        if A in used:
            continue
        Aset = set(A)
        for B in k6s:
            if B in used or B == A:
                continue
            Bset = set(B)
            if Aset & Bset:
                continue
            ok = True
            inv: set[int] = set()
            for a in A:
                neigh = [b for b in B if bool(skew_adj[a, b])]
                if len(neigh) != 1 or neigh[0] in inv:
                    ok = False
                    break
                inv.add(neigh[0])
            if ok:
                A2 = tuple(sorted(A))
                B2 = tuple(sorted(B))
                out.append((A2, B2) if A2 <= B2 else (B2, A2))
                used.add(A)
                used.add(B)
                break
    out = sorted(out)
    if len(out) != 36:
        raise RuntimeError(f"Expected 36 double-sixes, got {len(out)}")
    return out


def _cycle3_under(k: Tuple[int, ...], x0: object, act) -> List[object]:
    x1 = act(k, x0)
    x2 = act(k, x1)
    if act(k, x2) != x0:
        raise RuntimeError("Expected order-3 kernel action")
    if x0 == x1 or x0 == x2 or x1 == x2:
        raise RuntimeError("Expected 3 distinct lifts")
    return [x0, x1, x2]


def main(argv: Sequence[str] | None = None) -> None:
    out_json = ROOT / "artifacts" / "toe_affine_plane_duality.json"
    out_md = ROOT / "artifacts" / "toe_affine_plane_duality.md"

    skew, meet = toe_dynamics.load_schlafli_graph()
    fw = toe_dynamics.load_firewall_bad_edges()
    bad_triads = tuple(sorted(tuple(sorted(t)) for t in fw.triangles))
    if len(bad_triads) != 9:
        raise RuntimeError("Expected 9 firewall bad triads")
    cover = [v for t in bad_triads for v in t]
    if len(cover) != 27 or len(set(cover)) != 27:
        raise RuntimeError("Bad triads must partition the 27 vertices")

    # All meet-triangles.
    triads = set()
    for a in range(27):
        for b in range(a + 1, 27):
            if not bool(meet[a, b]):
                continue
            for c in range(b + 1, 27):
                if bool(meet[a, c]) and bool(meet[b, c]):
                    triads.add((a, b, c))
    if len(triads) != 45:
        raise RuntimeError(f"Expected 45 meet-triangles, got {len(triads)}")
    allowed_triads = sorted(triads - set(bad_triads))
    if len(allowed_triads) != 36:
        raise RuntimeError(f"Expected 36 allowed triads, got {len(allowed_triads)}")

    # Block map (vertex -> bad-triad block id).
    block_of: Dict[int, int] = {}
    for bi, t in enumerate(bad_triads):
        for v in t:
            block_of[v] = bi

    # Affine lines are the 12 distinct block-triples induced by allowed triads.
    line_to_allowed: Dict[Tuple[int, int, int], List[Tuple[int, int, int]]] = {}
    for t in allowed_triads:
        ids = tuple(sorted(block_of[v] for v in t))
        if len(set(ids)) != 3:
            raise RuntimeError("Allowed triad should pick 3 distinct blocks")
        line_to_allowed.setdefault(ids, []).append(t)
    if len(line_to_allowed) != 12:
        raise RuntimeError(f"Expected 12 affine lines, got {len(line_to_allowed)}")
    if any(len(v) != 3 for v in line_to_allowed.values()):
        raise RuntimeError("Expected exactly 3 allowed triads per affine line")

    # Verify affine-plane axiom: every pair of points lies on exactly one line.
    pair_hist = Counter()
    for ids in line_to_allowed:
        i, j, k = ids
        for a, b in [(i, j), (i, k), (j, k)]:
            pair_hist[(min(a, b), max(a, b))] += 1
    if len(pair_hist) != 36 or set(pair_hist.values()) != {1}:
        raise RuntimeError("Block-triples do not satisfy affine-plane axiom (AG(2,3))")

    # Double-sixes and their omitted-block line.
    double_sixes = _find_double_sixes(skew)
    line_to_ds: Dict[
        Tuple[int, int, int], List[Tuple[Tuple[int, ...], Tuple[int, ...]]]
    ] = {}
    for A, B in double_sixes:
        S = set(A) | set(B)
        used_blocks = {block_of[v] for v in S}
        if len(used_blocks) != 6:
            raise RuntimeError("Expected each double-six to use exactly 6 blocks")
        omitted = tuple(sorted(set(range(9)) - used_blocks))
        if omitted not in line_to_allowed:
            raise RuntimeError("Double-six omitted blocks should be an affine line")
        line_to_ds.setdefault(omitted, []).append((A, B))
    if len(line_to_ds) != 12 or any(len(v) != 3 for v in line_to_ds.values()):
        raise RuntimeError("Expected exactly 3 double-sixes per omitted affine line")

    # Kernel Z3 element from the W(E6) action on 27 that fixes blocks setwise.
    action = _load_json(ROOT / "artifacts" / "we6_signed_action_on_27.json")
    if not isinstance(action, dict):
        raise RuntimeError("Invalid we6_signed_action_on_27.json")
    gen_list = action.get("generators")
    if not (isinstance(gen_list, list) and len(gen_list) == 6):
        raise RuntimeError(
            "Invalid we6_signed_action_on_27.json: expected 6 generators"
        )
    gens = [tuple(int(x) for x in g["permutation"]) for g in gen_list]

    def induced_on_blocks(perm: Tuple[int, ...]) -> Tuple[int, ...] | None:
        img = [None] * 9
        for b, tri in enumerate(bad_triads):
            mapped = {block_of[perm[v]] for v in tri}
            if len(mapped) != 1:
                return None
            img[b] = next(iter(mapped))
        return tuple(int(x) for x in img)  # type: ignore[arg-type]

    id_perm = tuple(range(27))
    seen = {id_perm}
    q = deque([id_perm])
    H: List[Tuple[int, ...]] = []
    while q:
        cur = q.popleft()
        if _act_on_triads(cur, bad_triads) == bad_triads:
            H.append(cur)
        for g in gens:
            nxt = _compose_perm(g, cur)
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    if len(seen) != 51840:
        raise RuntimeError(f"Expected |W(E6)|=51840, got {len(seen)}")
    if len(H) != 1296:
        raise RuntimeError(f"Expected stabilizer size 1296, got {len(H)}")

    kernel = [h for h in H if induced_on_blocks(h) == tuple(range(9))]
    if len(kernel) != 3:
        raise RuntimeError(f"Expected Z3 kernel size 3, got {len(kernel)}")
    nontrivial = sorted([k for k in kernel if k != id_perm])
    k = nontrivial[0]
    k_cycles = _cycle_decomposition(k)

    # Build cycles per line, aligned by repeated application of k.
    line_records = []
    for line in sorted(line_to_allowed):
        triads_line = sorted(line_to_allowed[line])
        ds_line = sorted(line_to_ds[line])

        tri_cycle = _cycle3_under(k, triads_line[0], _act_on_triad)
        ds_cycle = _cycle3_under(k, ds_line[0], _act_on_double_six)

        # sanity: k permutes within each line class
        if set(tri_cycle) != set(triads_line):
            raise RuntimeError("Kernel does not cycle allowed triads within line")
        if set(ds_cycle) != set(ds_line):
            raise RuntimeError("Kernel does not cycle double-sixes within line")

        mapping = [
            {"triad": list(t), "double_six": {"A": list(ds[0]), "B": list(ds[1])}}
            for t, ds in zip(tri_cycle, ds_cycle)
        ]
        line_records.append(
            {
                "line_blocks": list(line),
                "allowed_triads_cycle": [list(t) for t in tri_cycle],
                "double_sixes_cycle": [
                    {"A": list(ds[0]), "B": list(ds[1])} for ds in ds_cycle
                ],
                "z3_equivariant_pairing": mapping,
            }
        )

    out: Dict[str, object] = {
        "status": "ok",
        "counts": {
            "bad_triads": 9,
            "triads_total": 45,
            "triads_allowed": 36,
            "double_sixes": 36,
            "affine_points": 9,
            "affine_lines": 12,
            "z3_lifts_per_line": 3,
        },
        "firewall": {"bad_triads": [list(t) for t in bad_triads]},
        "affine_plane": {"lines": [list(k) for k in sorted(line_to_allowed)]},
        "kernel_z3": {
            "element": list(k),
            "cycle_decomposition": [[int(x) for x in cyc] for cyc in k_cycles],
            "stabilizer_size": 1296,
        },
        "duality_by_line": line_records,
    }

    _write_json(out_json, out)

    lines: List[str] = []
    lines.append("# TOE: Firewall Affine Plane Duality (AG(2,3))")
    lines.append("")
    lines.append("## Counts")
    for k2, v2 in out["counts"].items():  # type: ignore[union-attr]
        lines.append(f"- {k2}: `{v2}`")
    lines.append("")
    lines.append("## Key Structure")
    lines.append("- 9 bad triads partition the 27 (firewall points)")
    lines.append("- 36 allowed cubic triads = 12 affine lines × 3 Z3 lifts")
    lines.append(
        "- 36 double-sixes = complements of the same 12 affine lines × 3 Z3 lifts"
    )
    lines.append("")
    lines.append("## Affine Lines (block triples)")
    for L in sorted(line_to_allowed):
        lines.append(f"- {list(L)}")
    lines.append("")
    lines.append(f"- JSON: `{out_json}`")
    _write_md(out_md, lines)

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
