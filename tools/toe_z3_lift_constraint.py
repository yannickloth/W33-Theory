#!/usr/bin/env python3
"""
Discover and certify the hidden Z3 "lift constraint" behind the 3 lifts per affine line.

We model the 27 Schläfli(E6-id) vertices as:
  (block ∈ {0..8}) × (t ∈ Z3),
where blocks are the 9 firewall bad triads, and t is the position inside the
kernel Z3 cycle (the element that cycles each bad triad).

Empirically, the 36 allowed triads (the ones not firewall-forbidden) satisfy a
simple Z3 conservation law after a *block-dependent gauge shift*:

  For every allowed triad (u,v,w) with blocks (b_u,b_v,b_w),
      t'(u) + t'(v) + t'(w) ≡ 0 (mod 3),
  where t'(x) = t(x) + offset[b_x] (mod 3).

The 9 forbidden triads are within a single block and satisfy the same law
automatically since 0+1+2 ≡ 0 (mod 3).

This script solves for such offsets (a linear system over F3), verifies the law
on all 45 cubic triads, and exports a certificate bundle.

Inputs:
  - artifacts/toe_affine_plane_duality.json  (kernel Z3 element + allowed triads)
  - artifacts/toe_sm_decomposition_27.json   (optional, only for nicer reporting)

Outputs:
  - artifacts/toe_z3_lift_constraint.json
  - artifacts/toe_z3_lift_constraint.md
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

Triad = Tuple[int, int, int]


def _load_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _triad_key(t: Sequence[int]) -> Triad:
    if len(t) != 3:
        raise ValueError("Expected length-3 triad")
    a, b, c = (int(t[0]), int(t[1]), int(t[2]))
    out = tuple(sorted((a, b, c)))
    if len(set(out)) != 3:
        raise ValueError("Triad must have 3 distinct vertices")
    return out  # type: ignore[return-value]


def _cycles_from_perm(perm: Sequence[int]) -> List[Tuple[int, ...]]:
    if len(perm) != 27:
        raise ValueError("Expected perm length 27")
    seen = [False] * 27
    cycles: List[Tuple[int, ...]] = []
    for i in range(27):
        if seen[i]:
            continue
        if int(perm[i]) == i:
            seen[i] = True
            continue
        cyc: List[int] = []
        j = i
        while not seen[j]:
            seen[j] = True
            cyc.append(j)
            j = int(perm[j])
        if len(cyc) > 1:
            cycles.append(tuple(cyc))
    return sorted(cycles, key=len, reverse=True)


def _solve_mod3_linear(A: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, int]:
    """Solve A x = b over F3, returning one solution and rank. Raises if inconsistent."""
    A = np.array(A, dtype=int) % 3
    b = np.array(b, dtype=int) % 3
    if A.ndim != 2 or b.ndim != 1:
        raise ValueError("Bad shapes for linear solve")
    n_eq, n_var = A.shape
    if b.shape[0] != n_eq:
        raise ValueError("Mismatched A/b rows")
    aug = np.concatenate([A, b[:, None]], axis=1) % 3

    row = 0
    pivots: List[int] = []
    inv = {1: 1, 2: 2}
    for col in range(n_var):
        pivot = None
        for r in range(row, n_eq):
            if int(aug[r, col]) % 3 != 0:
                pivot = r
                break
        if pivot is None:
            continue
        if pivot != row:
            aug[[row, pivot]] = aug[[pivot, row]]
        # normalize pivot to 1
        pv = int(aug[row, col]) % 3
        aug[row, :] = (aug[row, :] * inv[pv]) % 3
        # eliminate
        for r in range(n_eq):
            if r == row:
                continue
            factor = int(aug[r, col]) % 3
            if factor != 0:
                aug[r, :] = (aug[r, :] - factor * aug[row, :]) % 3
        pivots.append(col)
        row += 1
        if row >= n_eq:
            break

    # check consistency: 0 = c (c!=0)
    for r in range(n_eq):
        if np.all(aug[r, :n_var] % 3 == 0) and int(aug[r, n_var]) % 3 != 0:
            raise RuntimeError("Inconsistent linear system over F3")

    # choose one solution by setting free vars to 0
    x = np.zeros(n_var, dtype=int)
    for r, col in enumerate(pivots):
        x[col] = int(aug[r, n_var]) % 3
    return x % 3, len(pivots)


def main(argv: Sequence[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--duality-json",
        type=Path,
        default=ROOT / "artifacts" / "toe_affine_plane_duality.json",
    )
    p.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "toe_z3_lift_constraint.json",
    )
    p.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "artifacts" / "toe_z3_lift_constraint.md",
    )
    args = p.parse_args(list(argv) if argv is not None else None)

    dual = _load_json(args.duality_json)
    if dual.get("status") != "ok":
        raise RuntimeError("toe_affine_plane_duality.json status != ok")

    bad_triads_raw = (
        dual.get("firewall", {}).get("bad_triads")
        if isinstance(dual.get("firewall"), dict)
        else None
    )
    if not isinstance(bad_triads_raw, list) or len(bad_triads_raw) != 9:
        raise RuntimeError("Invalid toe_affine_plane_duality.json: firewall.bad_triads")
    bad_triads: List[Triad] = [_triad_key(t) for t in bad_triads_raw]
    cover = [v for t in bad_triads for v in t]
    if len(cover) != 27 or len(set(cover)) != 27:
        raise RuntimeError("Bad triads do not partition 27")

    kernel = dual.get("kernel_z3", {})
    if not isinstance(kernel, dict):
        raise RuntimeError("Invalid toe_affine_plane_duality.json: kernel_z3")
    perm = kernel.get("element")
    if not isinstance(perm, list) or len(perm) != 27:
        raise RuntimeError("Invalid toe_affine_plane_duality.json: kernel_z3.element")
    perm_t = [int(x) for x in perm]
    cycles = _cycles_from_perm(perm_t)
    if sorted(len(c) for c in cycles) != [3] * 9:
        raise RuntimeError("Expected kernel to decompose into 9 disjoint 3-cycles")

    # Map vertex -> block id.
    block_of: Dict[int, int] = {}
    for bi, t in enumerate(bad_triads):
        for v in t:
            block_of[v] = int(bi)
    if len(block_of) != 27:
        raise RuntimeError("Missing vertex in block map")

    # Define t(v) by kernel cycle order, per vertex.
    t_raw: Dict[int, int] = {}
    for cyc in cycles:
        for t, v in enumerate(cyc):
            t_raw[int(v)] = int(t) % 3
    if len(t_raw) != 27:
        raise RuntimeError("Missing vertex in t_raw map")

    # Gather all 45 triads (allowed + bad) from duality_by_line (allowed triads) plus bad triads.
    allowed_triads: List[Triad] = []
    dbl = dual.get("duality_by_line")
    if not isinstance(dbl, list) or len(dbl) != 12:
        raise RuntimeError("Invalid toe_affine_plane_duality.json: duality_by_line")
    for row in dbl:
        if not isinstance(row, dict):
            raise RuntimeError("Invalid duality_by_line row")
        tri_cycle = row.get("allowed_triads_cycle")
        if not isinstance(tri_cycle, list) or len(tri_cycle) != 3:
            raise RuntimeError("Expected 3 allowed triads per line")
        for t in tri_cycle:
            allowed_triads.append(_triad_key(t))
    if len(allowed_triads) != 36 or len(set(allowed_triads)) != 36:
        raise RuntimeError("Expected 36 distinct allowed triads")
    all_triads = sorted(set(allowed_triads) | set(bad_triads))
    if len(all_triads) != 45:
        raise RuntimeError(f"Expected 45 total triads, got {len(all_triads)}")

    # Solve for offsets o_b in Z3 such that for every allowed triad:
    #   (t(u)+o_bu) + (t(v)+o_bv) + (t(w)+o_bw) == 0 mod 3
    # This is linear in offsets.
    A = []
    rhs = []
    for u, v, w in allowed_triads:
        bu, bv, bw = (block_of[u], block_of[v], block_of[w])
        row = [0] * 9
        row[bu] = (row[bu] + 1) % 3
        row[bv] = (row[bv] + 1) % 3
        row[bw] = (row[bw] + 1) % 3
        A.append(row)
        rhs.append((-(t_raw[u] + t_raw[v] + t_raw[w])) % 3)
    offsets, rank = _solve_mod3_linear(np.array(A, dtype=int), np.array(rhs, dtype=int))
    off = [int(x) for x in offsets.tolist()]

    # Verify on all 45 triads.
    def t_shifted(x: int) -> int:
        return int((t_raw[x] + off[block_of[x]]) % 3)

    viol = []
    for t in all_triads:
        s = sum(t_shifted(x) for x in t) % 3
        if s != 0:
            viol.append((t, s))
    if viol:
        raise RuntimeError(f"Z3 lift constraint failed for {len(viol)} triads")

    # Optional: label by SM fields for reporting.
    field_by: Dict[int, str] = {}
    sm_path = ROOT / "artifacts" / "toe_sm_decomposition_27.json"
    if sm_path.exists():
        sm = _load_json(sm_path)
        per_v = sm.get("per_vertex")
        if isinstance(per_v, list):
            for r in per_v:
                if isinstance(r, dict) and "i" in r and "field" in r:
                    field_by[int(r["i"])] = str(r["field"])

    triad_examples = []
    for t in sorted(all_triads)[:20]:
        triad_examples.append(
            {
                "triad": list(t),
                "blocks": [block_of[x] for x in t],
                "t_raw": [t_raw[x] for x in t],
                "t_shifted": [t_shifted(x) for x in t],
                "fields": [field_by.get(x, "?") for x in t] if field_by else None,
            }
        )

    out: Dict[str, object] = {
        "status": "ok",
        "kernel": {
            "perm": perm_t,
            "cycle_decomposition": [list(c) for c in cycles],
        },
        "blocks": {
            "bad_triads": [list(t) for t in bad_triads],
            "offsets_z3": off,
            "rank": int(rank),
            "free_vars": int(9 - rank),
        },
        "vertices": [
            {
                "v": v,
                "block": int(block_of[v]),
                "t_raw": int(t_raw[v]),
                "t_shifted": int(t_shifted(v)),
                "field": field_by.get(v) if field_by else None,
            }
            for v in range(27)
        ],
        "triads": {
            "total": 45,
            "allowed": 36,
            "forbidden": 9,
            "constraint": "t'(u)+t'(v)+t'(w)=0 mod 3 where t'(x)=t_raw(x)+offset[block(x)]",
            "examples": triad_examples,
        },
    }
    _write_json(args.out_json, out)

    md: List[str] = []
    md.append("# TOE: Z3 Lift Constraint Certificate")
    md.append("")
    md.append(
        "We label each vertex as (block,t), where `block` is the firewall bad-triad block and"
    )
    md.append(
        "`t` is the index in the kernel Z3 cycle. There exists a block-dependent offset"
    )
    md.append("`offset[block] ∈ Z3` such that every cubic triad satisfies:")
    md.append("")
    md.append(
        "`t'(u)+t'(v)+t'(w) ≡ 0 (mod 3)` where `t'(x)=t_raw(x)+offset[block(x)]`."
    )
    md.append("")
    md.append("## Solution")
    md.append(f"- rank over F3: `{rank}`  free vars: `{9-rank}`")
    md.append(f"- offsets_z3 (block 0..8): `{off}`")
    md.append("")
    md.append("## Bad-triad blocks (points)")
    for bi, tri in enumerate(bad_triads):
        labs = (
            [field_by.get(v, str(v)) for v in tri]
            if field_by
            else [str(v) for v in tri]
        )
        md.append(
            f"- P{bi}: triad {list(tri)} offset `{off[bi]}` fields {sorted(labs)}"
        )
    md.append("")
    md.append("## Sample triads (showing t_raw and t_shifted)")
    for ex in triad_examples[:12]:
        md.append(
            f"- triad {ex['triad']} blocks {ex['blocks']} t_raw {ex['t_raw']} t' {ex['t_shifted']}"
        )
    md.append("")
    md.append(f"- JSON: `{args.out_json}`")
    _write_md(args.out_md, md)
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
