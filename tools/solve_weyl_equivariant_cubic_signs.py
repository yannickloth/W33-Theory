#!/usr/bin/env python3
"""
Solve a Weyl-equivariant sign gauge for the E6 cubic tensor inside the E8→E6×A2 model.

We set up one combined GF(2) linear system whose unknowns are:
  - phase_c(i) for the (27,3) basis vectors (c=0,1,2 colors; i=0..26 E6 weights): 81 bits
  - d_t for the 45 unordered E6 triads t: 45 bits
  - global_g[gen] for each of 6 E6 simple reflections: 6 bits

Constraints:
  (A) 270 coupling equations (for ordered triples across the three SU(3)=3 orbits):
      phase_0(i) + phase_1(j) + phase_2(k) + d_{ {i,j,k} } = raw_sign(i,j,k)
      where raw_sign(i,j,k) is computed from the fixed lattice cocycle ε on E8 roots.

  (B) Weyl-equivariance for the cubic under each E6 simple reflection generator:
      d_{p(t)} = d_t + (phase_0(i)+phase_0(p(i))) + (phase_1(j)+phase_1(p(j)))
                     + (phase_2(k)+phase_2(p(k))) + global_g[gen]
      for all 45 triads t=(i,j,k).

If the system is consistent, the resulting d is (by construction) Weyl-equivariant up to
overall generator-dependent sign (which is allowed because the invariant cubic is only
defined up to scale).

Outputs:
  artifacts/e6_cubic_weyl_equivariant_signs.json
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import defaultdict
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


def e6_key(r: np.ndarray) -> Tuple[int, ...]:
    re6 = r - proj_to_su3(r)
    return tuple(int(round(2 * float(x))) for x in re6.tolist())


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


def build_data():
    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    orbit_sizes = [len(o) for o in orbits]
    assert sorted(orbit_sizes) == [1, 1, 1, 1, 1, 1, 27, 27, 27, 27, 27, 27, 72]

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
    assert len(color_orbs) == 3
    oa, ob, oc = color_orbs

    # E6 id by projection across 3 color orbits.
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

    # Ordered couplings (i,j,k) from orbit sums.
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
            raw = cocycle.epsilon_e8(ka, kb)  # ±1
            couplings.append((i, j, k, sign_to_bit(int(raw))))
    assert len(couplings) == 270

    # 45 triads
    triads = sorted({tuple(sorted((i, j, k))) for (i, j, k, _) in couplings})
    assert len(triads) == 45
    triad_index = {t: idx for idx, t in enumerate(triads)}

    # Generator perms on e6ids (using base color orbit).
    base_orb = oa
    rep_root_by_e6id = [-1] * 27
    for ridx in orbits[base_orb]:
        rep_root_by_e6id[root_to_e6id[ridx]] = ridx
    if any(x == -1 for x in rep_root_by_e6id):
        raise RuntimeError("Missing representative per e6id")

    gen_perms: List[Tuple[int, ...]] = []
    for alpha in cds.E6_SIMPLE_ROOTS:
        perm = []
        for i in range(27):
            r = roots[rep_root_by_e6id[i]]
            img = cds.weyl_reflect(r, alpha)
            kk = tuple(int(round(2 * float(x))) for x in cds.snap_to_lattice(img))
            img_idx = root_index.get(kk)
            if img_idx is None or idx_orb[img_idx] != base_orb:
                raise RuntimeError("Reflection moved out of base orb (unexpected)")
            perm.append(root_to_e6id[img_idx])
        if sorted(perm) != list(range(27)):
            raise RuntimeError("Bad generator permutation")
        gen_perms.append(tuple(perm))

    return couplings, triads, triad_index, gen_perms


def main() -> None:
    couplings, triads, triad_index, gen_perms = build_data()

    # Variable layout:
    # phase(color,i): 3*27
    # d(triad): 45
    # g(gen): 6
    def var_phase(c: int, i: int) -> int:
        return c * 27 + i

    def var_d(t: Tuple[int, int, int]) -> int:
        return 81 + triad_index[t]

    def var_g(gen: int) -> int:
        return 81 + 45 + gen

    nvars = 81 + 45 + 6

    rows: List[Tuple[int, int]] = []

    # (A) Coupling equations
    for i, j, k, raw_bit in couplings:
        t = tuple(sorted((i, j, k)))
        mask = 0
        mask ^= 1 << var_phase(0, i)
        mask ^= 1 << var_phase(1, j)
        mask ^= 1 << var_phase(2, k)
        mask ^= 1 << var_d(t)
        rows.append((mask, raw_bit))

    # (B) Equivariance equations for each generator
    for gen, p in enumerate(gen_perms):
        for i, j, k in triads:
            tp = tuple(sorted((p[i], p[j], p[k])))
            mask = 0
            mask ^= 1 << var_d(tp)
            mask ^= 1 << var_d((i, j, k))
            mask ^= 1 << var_phase(0, i)
            mask ^= 1 << var_phase(0, p[i])
            mask ^= 1 << var_phase(1, j)
            mask ^= 1 << var_phase(1, p[j])
            mask ^= 1 << var_phase(2, k)
            mask ^= 1 << var_phase(2, p[k])
            mask ^= 1 << var_g(gen)
            rows.append((mask, 0))

    ok, sol, rank = LinearSystemGF2(nvars=nvars, rows=rows).solve()

    out: Dict[str, object] = {
        "status": "ok",
        "counts": {
            "variables": nvars,
            "equations": len(rows),
            "rank": rank,
            "solvable": ok,
        },
    }
    if ok:
        phases = [[sol[var_phase(c, i)] for i in range(27)] for c in range(3)]
        d_bits = [sol[81 + t] for t in range(45)]
        g_bits = [sol[var_g(gen)] for gen in range(6)]

        d_map = {triads[idx]: bit_to_sign(d_bits[idx]) for idx in range(45)}
        out["solution"] = {
            "phase_bits": phases,
            "d_triples": [{"triple": list(t), "sign": int(d_map[t])} for t in triads],
            "g_bits": g_bits,
            "d_sign_distribution": dict(defaultdict(int, Counter(d_map.values()))),
        }

    out_path = ROOT / "artifacts" / "e6_cubic_weyl_equivariant_signs.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("PASS" if ok else "FAIL", "Weyl-equivariant cubic sign system.")
    print("Wrote", out_path)


if __name__ == "__main__":
    main()
