#!/usr/bin/env python3
"""
Recover a symmetric E6 cubic tensor d_{ijk} from the 270 ordered E8 mixed triples.

We have 270 ordered triples (i,j,k) of E6-ids coming from E8 root triples
  α in orbit oa, β in ob, γ in oc, with α+β+γ=0,
and a raw sign bit s(i,j,k) given by the E8 cocycle bracket coefficient N_{α,β}.

Representation theory says these 270 couplings should factor as:
  s(i,j,k) = parity(i,j,k; {u,v,w}) ⊕ d_{u,v,w} ⊕ (gauge on i,j,k),
where:
  - {u,v,w} is the underlying unordered E6 triad (tritangent plane),
  - d_{u,v,w} is the symmetric E6 cubic tensor coefficient (45 of them),
  - parity(...) accounts for the antisymmetry coming from the SU(3) epsilon when you
    permute which E6 weight lands in which SU(3) weight slot,
  - gauge is independent sign flips on the 81 basis vectors (3 colors × 27 weights).

We implement parity as the permutation parity taking the canonical ordered triple
  (u,v,w) = sorted(u,v,w)
to the observed ordered triple (i,j,k).

Outputs:
  artifacts/e6_cubic_symmetric_from_270.json
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from dataclasses import dataclass
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
cocycle = _load_module(ROOT / "tools" / "e8_lattice_cocycle.py", "e8_lattice_cocycle")

SU3_ALPHA = np.array([1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
SU3_BETA = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0])


def k2(r: np.ndarray) -> Tuple[int, ...]:
    return tuple(int(round(2 * float(x))) for x in r.tolist())


def sign_to_bit(s: int) -> int:
    if s not in (-1, 1):
        raise ValueError("Expected ±1")
    return 1 if s == -1 else 0


def bit_to_sign(b: int) -> int:
    if b not in (0, 1):
        raise ValueError("Expected bit 0/1")
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


def e6_key(r: np.ndarray) -> Tuple[int, ...]:
    re6 = r - proj_to_su3(r)
    return tuple(int(round(2 * float(x))) for x in re6.tolist())


def perm_parity(
    from_triple: Tuple[int, int, int], to_triple: Tuple[int, int, int]
) -> int:
    """
    Parity bit (0 even, 1 odd) of the unique permutation mapping from_triple -> to_triple.
    Assumes all entries are distinct.
    """

    a, b, c = from_triple
    x, y, z = to_triple
    pos = {a: 0, b: 1, c: 2}
    p = [pos[x], pos[y], pos[z]]
    inv = 0
    for i in range(3):
        for j in range(i + 1, 3):
            if p[i] > p[j]:
                inv ^= 1
    return inv


@dataclass(frozen=True)
class LinearSystemGF2:
    nvars: int
    rows: List[Tuple[int, int]]

    def solve(self) -> Tuple[bool, List[int], int]:
        pivots: Dict[int, Tuple[int, int]] = {}
        for mask, rhs in self.rows:
            m = mask
            r = rhs & 1
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
                return False, [0] * self.nvars, len(pivots)

        sol = [0] * self.nvars
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
        return True, sol, len(pivots)


def main() -> None:
    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    orbit_sizes = [len(o) for o in orbits]
    idx_orb: Dict[int, int] = {}
    for oi, orb in enumerate(orbits):
        for v in orb:
            idx_orb[v] = oi

    root_index = {k2(roots[i]): i for i in range(len(roots))}

    mix_orbs = [oi for oi, sz in enumerate(orbit_sizes) if sz == 27]
    weights = {oi: su3_weight(roots[orbits[oi][0]]) for oi in mix_orbs}
    weights_3 = {(1, 0), (-1, 1), (0, -1)}
    color_orbs = sorted(
        [oi for oi in mix_orbs if weights[oi] in weights_3], key=lambda x: weights[x]
    )
    oa, ob, oc = color_orbs

    # E6 ids by projection across three color orbits.
    e6_groups: Dict[Tuple[int, ...], int] = {}
    root_to_e6id: Dict[int, int] = {}
    for oi in color_orbs:
        for ridx in orbits[oi]:
            k = e6_key(roots[ridx])
            if k not in e6_groups:
                e6_groups[k] = len(e6_groups)
            root_to_e6id[ridx] = e6_groups[k]
    assert len(e6_groups) == 27

    # Build the 270 ordered couplings and their raw bits.
    couplings: List[Tuple[int, int, int, int]] = []
    for a_root in orbits[oa]:
        ka = k2(roots[a_root])
        i = root_to_e6id[a_root]
        for b_root in orbits[ob]:
            kb = k2(roots[b_root])
            j = root_to_e6id[b_root]
            need = tuple(-(ka[t] + kb[t]) for t in range(8))
            c_root = root_index.get(need)
            if c_root is None or idx_orb[c_root] != oc:
                continue
            k = root_to_e6id[c_root]
            raw = sign_to_bit(int(cocycle.epsilon_e8(ka, kb)))
            couplings.append((i, j, k, raw))
    assert len(couplings) == 270

    # Underlying unordered triads.
    triads = sorted({tuple(sorted((i, j, k))) for (i, j, k, _) in couplings})
    assert len(triads) == 45
    triad_index = {t: idx for idx, t in enumerate(triads)}

    # Variable layout: phase(81) + d(45)
    def var_phase(color: int, idx: int) -> int:
        return color * 27 + idx

    def var_d(t: Tuple[int, int, int]) -> int:
        return 81 + triad_index[t]

    nvars = 81 + 45
    rows: List[Tuple[int, int]] = []

    # Equations
    for i, j, k, raw in couplings:
        t = tuple(sorted((i, j, k)))
        canon = t  # canonical ordering = sorted
        parity = perm_parity(canon, (i, j, k))
        mask = 0
        mask ^= 1 << var_phase(0, i)
        mask ^= 1 << var_phase(1, j)
        mask ^= 1 << var_phase(2, k)
        mask ^= 1 << var_d(t)
        rhs = raw ^ parity
        rows.append((mask, rhs))

    ok, sol, rank = LinearSystemGF2(nvars=nvars, rows=rows).solve()
    out: Dict[str, object] = {
        "status": "ok",
        "counts": {
            "variables": nvars,
            "equations": len(rows),
            "rank": int(rank),
            "solvable": bool(ok),
        },
    }
    if ok:
        phases = [[sol[var_phase(c, i)] for i in range(27)] for c in range(3)]
        d_bits = [sol[81 + t] for t in range(45)]
        d_signs = [bit_to_sign(b) for b in d_bits]
        out["solution"] = {
            "phase_bits": phases,
            "d_triples": [
                {"triple": list(t), "sign": int(d_signs[triad_index[t]])}
                for t in triads
            ],
            "d_sign_distribution": dict(Counter(d_signs)),
        }

    out_path = ROOT / "artifacts" / "e6_cubic_symmetric_from_270.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("PASS" if ok else "FAIL", "Recovered symmetric cubic from 270 (with parity).")
    print("Wrote", out_path)


if __name__ == "__main__":
    main()
