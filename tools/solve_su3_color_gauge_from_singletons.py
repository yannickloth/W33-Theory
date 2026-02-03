#!/usr/bin/env python3
"""
Solve a global SU(3) (A2) color gauge from the singleton-root ladder action.

We are in the E8 -> E6 ⊕ A2 decomposition, where:
  - there are 3 "color" 27-orbits (the SU3=3 weights),
  - there are 6 singleton roots forming the A2 root system.

For each E6-weight id i (0..26), there is exactly one mixed root in each color orbit,
so the (27,3) sector is literally 27 copies of the 3-dimensional SU(3) module.

We fix a **canonical relative phase between the three color basis vectors** by requiring
the A2 ladder operators (simple roots) to act with coefficient +1 on every i.

Concretely:
  - Choose A2 simple roots α,β (these are explicit E8 roots orthogonal to E6).
  - For each i and each ladder step (color_c --α--> color_c'), compute the raw bracket sign
        [e_α, e_{(c,i)}] = s * e_{(c',i)}.
  - Solve for bits phase_c(i) so that after rephasing f_{c,i} = (-1)^{phase_c(i)} e_{(c,i)},
    the ladder coefficient becomes +1:
        phase_c(i) ⊕ phase_c'(i) = signbit(s).

Outputs:
  artifacts/su3_color_gauge_from_singletons.json
"""

from __future__ import annotations

import importlib.util
import json
import sys
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


def cheva_abs_N(
    alpha_k2: Tuple[int, ...],
    beta_k2: Tuple[int, ...],
    root_index: Dict[Tuple[int, ...], int],
) -> int:
    p = 0
    while True:
        cand = tuple(beta_k2[i] - (p + 1) * alpha_k2[i] for i in range(8))
        if cand in root_index:
            p += 1
            continue
        break
    return p + 1


def N(
    alpha_k2: Tuple[int, ...],
    beta_k2: Tuple[int, ...],
    root_index: Dict[Tuple[int, ...], int],
) -> int:
    s = tuple(alpha_k2[i] + beta_k2[i] for i in range(8))
    if s not in root_index:
        return 0
    return int(
        cocycle.epsilon_e8(alpha_k2, beta_k2)
        * cheva_abs_N(alpha_k2, beta_k2, root_index)
    )


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
    assert sorted(orbit_sizes) == [1, 1, 1, 1, 1, 1, 27, 27, 27, 27, 27, 27, 72]

    idx_orb: Dict[int, int] = {}
    for oi, orb in enumerate(orbits):
        for v in orb:
            idx_orb[v] = oi

    root_index = {k2(roots[i]): i for i in range(len(roots))}

    # Identify the 3 color orbits (SU3=3).
    mix_orbs = [oi for oi, sz in enumerate(orbit_sizes) if sz == 27]
    weights = {oi: su3_weight(roots[orbits[oi][0]]) for oi in mix_orbs}
    weights_3 = {(1, 0), (-1, 1), (0, -1)}
    color_orbs = sorted(
        [oi for oi in mix_orbs if weights[oi] in weights_3], key=lambda x: weights[x]
    )
    assert len(color_orbs) == 3
    oa, ob, oc = color_orbs

    # E6 ids by projection equality.
    e6_groups: Dict[Tuple[int, ...], int] = {}
    root_to_e6id: Dict[int, int] = {}
    for oi in color_orbs:
        for ridx in orbits[oi]:
            k = e6_key(roots[ridx])
            if k not in e6_groups:
                e6_groups[k] = len(e6_groups)
            root_to_e6id[ridx] = e6_groups[k]
    assert len(e6_groups) == 27

    # Map (color,e6id)->root index
    color_root_by_e6id: List[List[int]] = [[-1] * 27 for _ in range(3)]
    for c, oi in enumerate(color_orbs):
        for ridx in orbits[oi]:
            color_root_by_e6id[c][root_to_e6id[ridx]] = ridx
    if any(x == -1 for row in color_root_by_e6id for x in row):
        raise RuntimeError("Missing root for some (color,e6id)")

    # Pick explicit A2 simple roots and find their singleton indices.
    alpha_k2 = k2(SU3_ALPHA)
    beta_k2 = k2(SU3_BETA)
    if alpha_k2 not in root_index or beta_k2 not in root_index:
        raise RuntimeError("SU3_ALPHA or SU3_BETA not found among E8 roots")
    alpha_idx = root_index[alpha_k2]
    beta_idx = root_index[beta_k2]
    if len(orbits[idx_orb[alpha_idx]]) != 1 or len(orbits[idx_orb[beta_idx]]) != 1:
        raise RuntimeError("Chosen SU3 simple roots are not singleton orbits")

    # Determine how α and β map color orbits (must preserve E6 id).
    # For each color orbit, pick a sample i and compute α + root(c,i).
    def ladder_map(
        simple_k2: Tuple[int, ...]
    ) -> Tuple[List[int], List[List[int]], List[Tuple[int, int]]]:
        """
        For each color c and weight i, the A2 ladder action may be zero.

        Returns:
          - dest_color[c] in {0,1,2} if this ladder maps color c -> that color on some weights,
            else -1 if it never acts from color c.
          - sign_bits[c][i] (only meaningful when action exists)
          - edges: list of (c, i) pairs where action exists (so we should constrain phases)
        """

        dest = [-1, -1, -1]
        sign_bits: List[List[int]] = [[0] * 27 for _ in range(3)]
        edges: List[Tuple[int, int]] = []

        for c, oi in enumerate(color_orbs):
            found_dest = None
            for i in range(27):
                ridx = color_root_by_e6id[c][i]
                src = k2(roots[ridx])
                tgt_k2 = tuple(src[t] + simple_k2[t] for t in range(8))
                tgt_idx = root_index.get(tgt_k2)
                if tgt_idx is None:
                    continue  # ladder kills this vector
                dest_orb = idx_orb[tgt_idx]
                if dest_orb not in color_orbs:
                    raise RuntimeError(
                        "A2 ladder landed outside color orbits (unexpected)"
                    )
                dc = color_orbs.index(dest_orb)
                if root_to_e6id[tgt_idx] != i:
                    raise RuntimeError("A2 ladder changed E6 id (unexpected)")
                n = N(simple_k2, src, root_index)
                if abs(n) != 1:
                    raise RuntimeError("Expected |N|=1 for nonzero A2 ladder action")
                sign_bits[c][i] = sign_to_bit(int(np.sign(n)))
                edges.append((c, i))
                if found_dest is None:
                    found_dest = dc
                elif found_dest != dc:
                    raise RuntimeError(
                        "A2 ladder from a fixed color hits multiple colors (unexpected)"
                    )

            dest[c] = -1 if found_dest is None else int(found_dest)

        return dest, sign_bits, edges

    alpha_dest, alpha_sign, alpha_edges = ladder_map(alpha_k2)
    beta_dest, beta_sign, beta_edges = ladder_map(beta_k2)

    # Solve phases phase_c(i) so that ladder coefficients become +1:
    # phase_c(i) ⊕ phase_dest(c)(i) = signbit
    # Also fix gauge by setting phase_0(0)=0.
    def var_phase(c: int, i: int) -> int:
        return c * 27 + i

    rows: List[Tuple[int, int]] = []
    for c, i in alpha_edges:
        dc = alpha_dest[c]
        mask = (1 << var_phase(c, i)) ^ (1 << var_phase(dc, i))
        rows.append((mask, alpha_sign[c][i]))
    for c, i in beta_edges:
        dc = beta_dest[c]
        mask = (1 << var_phase(c, i)) ^ (1 << var_phase(dc, i))
        rows.append((mask, beta_sign[c][i]))
    # gauge fix
    rows.append((1 << var_phase(0, 0), 0))

    ok, sol, rank = LinearSystemGF2(nvars=81, rows=rows).solve()

    out: Dict[str, object] = {
        "status": "ok",
        "a2_simple_roots": {
            "alpha": SU3_ALPHA.tolist(),
            "beta": SU3_BETA.tolist(),
            "alpha_index": int(alpha_idx),
            "beta_index": int(beta_idx),
        },
        "color_orbits": [
            {"orbit": int(oi), "su3_weight": list(weights[oi])} for oi in color_orbs
        ],
        "ladders": {
            "alpha_dest_color": alpha_dest,
            "beta_dest_color": beta_dest,
            "alpha_edges": int(len(alpha_edges)),
            "beta_edges": int(len(beta_edges)),
        },
        "solve": {"solvable": bool(ok), "rank": int(rank), "equations": int(len(rows))},
    }
    if ok:
        phases = [[sol[var_phase(c, i)] for i in range(27)] for c in range(3)]
        out["solution"] = {"phase_bits": phases}

    out_path = ROOT / "artifacts" / "su3_color_gauge_from_singletons.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("PASS" if ok else "FAIL", "Solved SU3 color gauge from singleton ladders.")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
