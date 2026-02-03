#!/usr/bin/env python3
"""
Solve a *combined* canonical SU(3) (A2) gauge + symmetric E6 cubic tensor from E8 data.

Problem we hit:
  - If you only solve the 270 coupling equations, you can find per-(color,weight) signs and
    a symmetric 45-term tensor d_t.
  - If you only solve SU(3) ladder-normalization using fixed singleton root vectors, you can
    make A2 action uniform, but the resulting gauge can be incompatible with the coupling normalization.

Key fix:
  Chevalley bases allow independent sign choices for the *simple root vectors* (and hence for all
  root vectors in the A2 factor). Our earlier "canonical SU3 gauge" implicitly fixed those singleton
  signs, which overconstrains the system.

Here we solve everything together over GF(2) with unknowns:
  - phase_{orb}(i) for mixed basis vectors (6 mixed orbits; i=0..26 E6 ids) -> 162 bits
  - d_t for 45 unordered triads (E6 cubic tensor signs)                 -> 45 bits
  - s_rho for each of the 6 A2 singleton roots ρ (root-vector sign)     -> 6 bits
  - su3_eps(oa,ob) for ordered orbit-pairs in the 3 triangle            -> 6 bits
  - ladder_const(sid, orbit_transition)                                 -> inferred (typically 12 bits)

Constraints:
  (A) 270 mixed couplings for each ordered pair of distinct color orbits in the SU(3)=3 triangle:
        phase_oa(i) + phase_ob(j) + phase_ocbar(kbar) + d_{ {i,j,k} } = raw_couple(i,j,kbar)
      where:
        - oa,ob are 27-orbits with SU(3) weights in the 3,
        - ocbar is the unique 27-orbit in the 3̄ with (root in oa) + (root in ob) landing in ocbar,
        - k is the E6-id dual to kbar (E6 weight negation: 27̄ ↔ 27),
        - raw_couple is signbit( ε(α,β) ) for the ordered pair (α in oa, β in ob).
      IMPORTANT: raw_couple is *antisymmetric* under swapping inputs (it is the Lie bracket sign),
      while d_{ijk} is symmetric. The missing antisymmetry is carried by the SU(3) epsilon tensor,
      modeled here as an additional orbit-pair sign su3_eps(oa,ob) (one bit per ordered pair oa!=ob):

        phase_oa(i) + phase_ob(j) + phase_ocbar(kbar) + d_{ {i,j,k} } + su3_eps(oa,ob) = raw_couple(i,j,kbar)

      with constraints su3_eps(oa,ob) + su3_eps(ob,oa) = 1 for each unordered pair {oa,ob}.

  (B) SU(3) ladder normalization for each singleton root ρ and each nonzero ladder edge
      (orbit o, e6id i) -> (orbit o', e6id i) when ρ + β(o,i) is a root:
        s_rho + phase_o(i) + phase_o'(i) + ladder_const(sid,o→o') = raw_ladder(ρ,o,i)
      This enforces **uniformity across all 27 E6-ids** for a given (sid,o→o') transition, but does
      not force the uniform value to be +1.

Gauge-fix:
  - phase_(first 3-orbit)(0) = 0
  - s_rho0 = 0 for the lexicographically smallest singleton root (arbitrary reference)
  - ladder_const for the first observed (sid,o→o') transition is 0 (arbitrary reference)

Outputs:
  artifacts/canonical_su3_gauge_and_cubic.json
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
SU3_ALPHA_K2 = (2, -2, 0, 0, 0, 0, 0, 0)
SU3_BETA_K2 = (0, 2, 0, 0, 0, 0, 0, -2)


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
    rk2 = k2(r)
    a_num = sum(rk2[i] * SU3_ALPHA_K2[i] for i in range(8))
    b_num = sum(rk2[i] * SU3_BETA_K2[i] for i in range(8))
    if (a_num % 4) != 0 or (b_num % 4) != 0:
        raise RuntimeError(
            "Non-integral SU(3) weight detected (unexpected for E8 roots)"
        )
    return (a_num // 4, b_num // 4)


def e6_key(r: np.ndarray) -> Tuple[int, ...]:
    # Exact projection using the SU(3) Gram inverse:
    #   G = [[2,-1],[-1,2]],  G^{-1} = (1/3)*[[2,1],[1,2]]
    # Work in k2-coordinates to stay integral throughout.
    rk2 = k2(r)
    a_num = sum(rk2[i] * SU3_ALPHA_K2[i] for i in range(8))  # = 4*<r,alpha>
    b_num = sum(rk2[i] * SU3_BETA_K2[i] for i in range(8))  # = 4*<r,beta>
    proj_num = [
        (2 * a_num + b_num) * SU3_ALPHA_K2[i] + (a_num + 2 * b_num) * SU3_BETA_K2[i]
        for i in range(8)
    ]  # = 12 * proj_k2
    # Keep the *integer numerator* of the E6 projection in k2-coordinates:
    #   e6_num = 12 * (rk2 - proj_k2)
    # This avoids any divisibility assumptions while remaining fully canonical.
    e6_num = [12 * rk2[i] - proj_num[i] for i in range(8)]
    return tuple(int(x) for x in e6_num)


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
    rows: List[Tuple[int, int, int]]

    def solve(self) -> Tuple[bool, List[int], int, Dict[str, object] | None]:
        # XOR-basis elimination (keeps column-reduced form for pivots).
        basis_mask = [0] * self.nvars
        basis_rhs = [0] * self.nvars
        basis_src = [0] * self.nvars

        for mask, rhs, src in self.rows:
            m = mask
            r = rhs & 1
            comb = src
            while m:
                p = m.bit_length() - 1
                if basis_mask[p] == 0:
                    # New pivot at p. Eliminate this pivot from all higher-pivot rows to keep
                    # the pivot column reduced (unique 1 in that column).
                    basis_mask[p] = m
                    basis_rhs[p] = r
                    basis_src[p] = comb
                    for q in range(p + 1, self.nvars):
                        if basis_mask[q] and ((basis_mask[q] >> p) & 1):
                            basis_mask[q] ^= m
                            basis_rhs[q] ^= r
                            basis_src[q] ^= comb
                    break
                m ^= basis_mask[p]
                r ^= basis_rhs[p]
                comb ^= basis_src[p]
            if m == 0 and r == 1:
                witness_idxs = [i for i in range(comb.bit_length()) if (comb >> i) & 1]
                rank = sum(1 for x in basis_mask if x)
                return False, [0] * self.nvars, rank, {"equation_indices": witness_idxs}

        sol = [0] * self.nvars
        # With the basis kept column-reduced, each pivot row only references lower indices.
        for p in range(self.nvars):
            if basis_mask[p] == 0:
                sol[p] = 0
                continue
            m = basis_mask[p]
            r = basis_rhs[p] & 1
            lower = m & ((1 << p) - 1)
            val = r
            while lower:
                lsb = lower & -lower
                idx = lsb.bit_length() - 1
                val ^= sol[idx]
                lower ^= lsb
            sol[p] = val

        rank = sum(1 for x in basis_mask if x)
        return True, sol, rank, None


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

    # A2 singleton roots (6 of them).
    singleton_idxs = [orbits[oi][0] for oi, sz in enumerate(orbit_sizes) if sz == 1]
    singleton_k2 = sorted([k2(roots[i]) for i in singleton_idxs])
    singleton_to_sid = {r: si for si, r in enumerate(singleton_k2)}

    # Identify the 3 and 3bar triangles of mixed orbits.
    mix_orbs = [oi for oi, sz in enumerate(orbit_sizes) if sz == 27]
    weights = {oi: su3_weight(roots[orbits[oi][0]]) for oi in mix_orbs}
    weights_3 = {(1, 0), (-1, 1), (0, -1)}
    weights_3bar = {(-1, 0), (1, -1), (0, 1)}
    orbs_3 = sorted(
        [oi for oi in mix_orbs if weights[oi] in weights_3], key=lambda x: weights[x]
    )
    orbs_3bar = sorted(
        [oi for oi in mix_orbs if weights[oi] in weights_3bar], key=lambda x: weights[x]
    )
    if len(orbs_3) != 3 or len(orbs_3bar) != 3:
        raise RuntimeError("Failed to locate 3 and 3bar mixed orbit triangles")

    # E6 ids: 27 and 27bar are distinct. Make IDs deterministic by sorting the E6 keys lexicographically.
    e6_keys_27_set = {e6_key(roots[ridx]) for oi in orbs_3 for ridx in orbits[oi]}
    e6_keys_27bar_set = {e6_key(roots[ridx]) for oi in orbs_3bar for ridx in orbits[oi]}
    if len(e6_keys_27_set) != 27 or len(e6_keys_27bar_set) != 27:
        raise RuntimeError("Expected 27 E6-keys for 27 and 27bar")

    e6_keys_27_list = sorted(e6_keys_27_set)
    e6_keys_27bar_list = sorted(e6_keys_27bar_set)
    e6_keys_27: Dict[Tuple[int, ...], int] = {
        k: i for i, k in enumerate(e6_keys_27_list)
    }
    e6_keys_27bar: Dict[Tuple[int, ...], int] = {
        k: i for i, k in enumerate(e6_keys_27bar_list)
    }

    root_to_e6id27: Dict[int, int] = {
        ridx: e6_keys_27[e6_key(roots[ridx])] for oi in orbs_3 for ridx in orbits[oi]
    }
    root_to_e6id27bar: Dict[int, int] = {
        ridx: e6_keys_27bar[e6_key(roots[ridx])]
        for oi in orbs_3bar
        for ridx in orbits[oi]
    }

    # Duality: 27bar weight should be the negation of 27 weight in the E6 component.
    dual_27_to_27bar: Dict[int, int] = {}
    for k, i in e6_keys_27.items():
        nk = tuple(-x for x in k)
        j = e6_keys_27bar.get(nk)
        if j is None:
            raise RuntimeError("Failed to match 27 key to 27bar by negation")
        dual_27_to_27bar[i] = j
    dual_27bar_to_27: Dict[int, int] = {v: k for k, v in dual_27_to_27bar.items()}
    if len(dual_27bar_to_27) != 27:
        raise RuntimeError("27<->27bar dual map not bijective")

    # Map (orbit,e6id)->root index for all 6 mixed orbits.
    orb_root_by_e6id: Dict[int, List[int]] = {}
    for oi in orbs_3:
        arr = [-1] * 27
        for ridx in orbits[oi]:
            arr[root_to_e6id27[ridx]] = ridx
        if any(v == -1 for v in arr):
            raise RuntimeError("Missing mixed root in 3 triangle")
        orb_root_by_e6id[oi] = arr
    for oi in orbs_3bar:
        arr = [-1] * 27
        for ridx in orbits[oi]:
            arr[root_to_e6id27bar[ridx]] = ridx
        if any(v == -1 for v in arr):
            raise RuntimeError("Missing mixed root in 3bar triangle")
        orb_root_by_e6id[oi] = arr

    # Determine, for each ordered pair of distinct 3-orbits (oa,ob), which 3bar orbit ocbar they land in via sums.
    sum_target: Dict[Tuple[int, int], int] = {}
    for oa in orbs_3:
        for ob in orbs_3:
            if oa == ob:
                continue
            tgt_counts: Dict[int, int] = {}
            for a_root in orbits[oa]:
                ka = k2(roots[a_root])
                for b_root in orbits[ob]:
                    kb = k2(roots[b_root])
                    s = tuple(ka[t] + kb[t] for t in range(8))
                    c_root = root_index.get(s)
                    if c_root is None:
                        continue
                    oc = idx_orb[c_root]
                    if oc in orbs_3bar:
                        tgt_counts[oc] = tgt_counts.get(oc, 0) + 1
            if len(tgt_counts) != 1 or next(iter(tgt_counts.values())) != 270:
                raise RuntimeError("Unexpected sum-target counts for mixed orbits")
            sum_target[(oa, ob)] = next(iter(tgt_counts.keys()))

    # Enumerate couplings across the 3 triangle into 3bar, producing the 45 triads on the 27 indices.
    couplings: List[Tuple[int, int, int, int, int, int, Tuple[int, int, int]]] = (
        []
    )  # (oa,ob,i,j,kbar, raw_bit, triad)
    triad_set = set()
    for oa in orbs_3:
        for ob in orbs_3:
            if oa == ob:
                continue
            ocbar = sum_target[(oa, ob)]
            for a_root in orbits[oa]:
                ka = k2(roots[a_root])
                i = root_to_e6id27[a_root]
                for b_root in orbits[ob]:
                    kb = k2(roots[b_root])
                    j = root_to_e6id27[b_root]
                    s = tuple(ka[t] + kb[t] for t in range(8))
                    c_root = root_index.get(s)
                    if c_root is None or idx_orb[c_root] != ocbar:
                        continue
                    kbar = root_to_e6id27bar[c_root]
                    k = dual_27bar_to_27[kbar]
                    triad = tuple(sorted((i, j, k)))
                    triad_set.add(triad)
                    raw_bit = sign_to_bit(int(cocycle.epsilon_e8(ka, kb)))
                    couplings.append((oa, ob, i, j, kbar, raw_bit, triad))
    if len(triad_set) != 45:
        raise RuntimeError(f"Expected 45 triads; got {len(triad_set)}")
    triads = sorted(triad_set)
    triad_index = {t: idx for idx, t in enumerate(triads)}

    # Enumerate ladder edges for all singleton roots.
    ladder_edges = []  # (sid, oi, i, oj, raw_bit)
    for rho in singleton_k2:
        sid = singleton_to_sid[rho]
        for oi in orbs_3 + orbs_3bar:
            for i in range(27):
                ridx = orb_root_by_e6id[oi][i]
                src = k2(roots[ridx])
                tgt = tuple(src[t] + rho[t] for t in range(8))
                tgt_idx = root_index.get(tgt)
                if tgt_idx is None:
                    continue
                dest_orb = idx_orb[tgt_idx]
                if dest_orb not in (orbs_3 + orbs_3bar):
                    raise RuntimeError(
                        "A2 ladder left mixed-orbit triangles (unexpected)"
                    )
                # Ladder should preserve E6 id within 27 (or within 27bar).
                if oi in orbs_3:
                    if dest_orb not in orbs_3:
                        raise RuntimeError("A2 ladder crossed 3 -> 3bar (unexpected)")
                    if root_to_e6id27[tgt_idx] != i:
                        raise RuntimeError(
                            "A2 ladder changed E6 id in 3 triangle (unexpected)"
                        )
                else:
                    if dest_orb not in orbs_3bar:
                        raise RuntimeError("A2 ladder crossed 3bar -> 3 (unexpected)")
                    if root_to_e6id27bar[tgt_idx] != i:
                        raise RuntimeError(
                            "A2 ladder changed E6 id in 3bar triangle (unexpected)"
                        )
                n = N(rho, src, root_index)
                if abs(n) != 1:
                    raise RuntimeError("Expected |N|=1 for A2 ladder action")
                ladder_edges.append(
                    (sid, oi, i, dest_orb, sign_to_bit(int(np.sign(n))))
                )

    # Variables: phase(162) + d(45) + s_rho(6) + su3_eps(6)
    all_mixed_orbs = orbs_3 + orbs_3bar
    orb_to_vid = {oi: idx for idx, oi in enumerate(all_mixed_orbs)}

    def var_phase(oi: int, i: int) -> int:
        return orb_to_vid[oi] * 27 + i

    def var_d(t: Tuple[int, int, int]) -> int:
        return 162 + triad_index[t]

    def var_s(sid: int) -> int:
        return 162 + 45 + sid

    pair_list = [(oa, ob) for oa in orbs_3 for ob in orbs_3 if oa != ob]
    pair_to_pid = {p: idx for idx, p in enumerate(pair_list)}

    def var_eps(oa: int, ob: int) -> int:
        return 162 + 45 + 6 + pair_to_pid[(oa, ob)]

    ladder_keys = sorted({(sid, oi, oj) for (sid, oi, _i, oj, _raw) in ladder_edges})
    ladder_to_lid = {k: idx for idx, k in enumerate(ladder_keys)}

    def var_lconst(sid: int, oi: int, oj: int) -> int:
        return 162 + 45 + 6 + 6 + ladder_to_lid[(sid, oi, oj)]

    nvars = 162 + 45 + 6 + 6 + len(ladder_keys)
    rows: List[Tuple[int, int, int]] = []
    row_meta: List[Dict[str, object]] = []

    # (A) Coupling equations.
    for oa, ob, i, j, kbar, raw, t in couplings:
        ocbar = sum_target[(oa, ob)]
        mask = 0
        mask ^= 1 << var_phase(oa, i)
        mask ^= 1 << var_phase(ob, j)
        mask ^= 1 << var_phase(ocbar, kbar)
        mask ^= 1 << var_d(t)
        mask ^= 1 << var_eps(oa, ob)
        rows.append((mask, raw, 1 << len(row_meta)))
        row_meta.append(
            {
                "type": "coupling",
                "oa": int(oa),
                "ob": int(ob),
                "ocbar": int(ocbar),
                "i": int(i),
                "j": int(j),
                "kbar": int(kbar),
                "triad": list(t),
            }
        )

    # (A2) SU(3) epsilon antisymmetry constraints on the 3 triangle.
    for oa in orbs_3:
        for ob in orbs_3:
            if oa >= ob:
                continue
            mask = (1 << var_eps(oa, ob)) ^ (1 << var_eps(ob, oa))
            rows.append((mask, 1, 1 << len(row_meta)))
            row_meta.append({"type": "su3_eps_antisym", "oa": int(oa), "ob": int(ob)})

    # (B) Ladder equations.
    for sid, oi, i, oj, raw in ladder_edges:
        mask = 0
        mask ^= 1 << var_s(sid)
        mask ^= 1 << var_phase(oi, i)
        mask ^= 1 << var_phase(oj, i)
        mask ^= 1 << var_lconst(sid, oi, oj)
        rows.append((mask, raw, 1 << len(row_meta)))
        row_meta.append(
            {
                "type": "ladder",
                "singleton_sid": int(sid),
                "src_orbit": int(oi),
                "dst_orbit": int(oj),
                "e6id": int(i),
            }
        )

    # Gauge fixes.
    rows.append((1 << var_phase(orbs_3[0], 0), 0, 1 << len(row_meta)))
    row_meta.append(
        {
            "type": "gauge_fix",
            "var": "phase",
            "orbit": int(orbs_3[0]),
            "e6id": 0,
            "value": 0,
        }
    )
    rows.append((1 << var_s(0), 0, 1 << len(row_meta)))
    row_meta.append(
        {"type": "gauge_fix", "var": "s_rho", "singleton_sid": 0, "value": 0}
    )
    rows.append((1 << var_eps(pair_list[0][0], pair_list[0][1]), 0, 1 << len(row_meta)))
    row_meta.append(
        {
            "type": "gauge_fix",
            "var": "su3_eps",
            "oa": int(pair_list[0][0]),
            "ob": int(pair_list[0][1]),
            "value": 0,
        }
    )
    rows.append((1 << var_lconst(*ladder_keys[0]), 0, 1 << len(row_meta)))
    row_meta.append(
        {
            "type": "gauge_fix",
            "var": "ladder_const",
            "key": [int(x) for x in ladder_keys[0]],
            "value": 0,
        }
    )

    ok, sol, rank, witness = LinearSystemGF2(nvars=nvars, rows=rows).solve()
    if ok:
        # Sanity-check: the computed solution must satisfy every equation row.
        failures = 0
        for mask, rhs, _src in rows:
            m = mask
            val = 0
            while m:
                lsb = m & -m
                idx = lsb.bit_length() - 1
                val ^= sol[idx]
                m ^= lsb
            if (val & 1) != (rhs & 1):
                failures += 1
                if failures >= 10:
                    break
        if failures:
            ok = False
            witness = {"equation_indices": [], "internal_check_failures": int(failures)}

    out: Dict[str, object] = {
        "status": "ok",
        "counts": {
            "variables": nvars,
            "equations": len(rows),
            "rank": int(rank),
            "solvable": bool(ok),
            "couplings": int(sum(1 for m in row_meta if m["type"] == "coupling")),
            "triads": 45,
            "ladder_edges": int(len(ladder_edges)),
            "su3_eps_vars": 6,
            "ladder_const_vars": int(len(ladder_keys)),
        },
        "orbits_3": [
            {"orbit": int(oi), "su3_weight": list(weights[oi])} for oi in orbs_3
        ],
        "orbits_3bar": [
            {"orbit": int(oi), "su3_weight": list(weights[oi])} for oi in orbs_3bar
        ],
        "sum_targets_3x3_to_3bar": {
            f"{int(oa)}+{int(ob)}": int(sum_target[(oa, ob)])
            for (oa, ob) in sorted(sum_target)
        },
        "singleton_roots_k2": [list(r) for r in singleton_k2],
        "e6_keys_27_k2": [list(k) for k in e6_keys_27_list],
        "e6_keys_27bar_k2": [list(k) for k in e6_keys_27bar_list],
        "triads": [list(t) for t in triads],
        "instances": {
            "couplings": [
                {
                    "oa": int(oa),
                    "ob": int(ob),
                    "ocbar": int(sum_target[(oa, ob)]),
                    "i": int(i),
                    "j": int(j),
                    "kbar": int(kbar),
                    "triad": list(t),
                    "raw_bit": int(raw),
                }
                for (oa, ob, i, j, kbar, raw, t) in couplings
            ],
            "ladders": [
                {
                    "singleton_sid": int(sid),
                    "src_orbit": int(oi),
                    "dst_orbit": int(oj),
                    "e6id": int(i),
                    "raw_bit": int(raw),
                }
                for (sid, oi, i, oj, raw) in ladder_edges
            ],
        },
    }

    if witness is not None:
        out["inconsistency_witness"] = {
            "equation_indices": witness["equation_indices"],
            "equations": [row_meta[i] for i in witness["equation_indices"]],
        }

    if ok:
        phases = {
            str(int(oi)): [sol[var_phase(oi, i)] for i in range(27)]
            for oi in all_mixed_orbs
        }
        d_bits = [sol[162 + t] for t in range(45)]
        s_bits = [sol[162 + 45 + sid] for sid in range(6)]
        eps_bits = {
            f"{int(oa)}+{int(ob)}": int(sol[var_eps(oa, ob)]) for (oa, ob) in pair_list
        }
        lconst_bits = {
            f"{int(sid)}:{int(oi)}->{int(oj)}": int(sol[var_lconst(sid, oi, oj)])
            for (sid, oi, oj) in ladder_keys
        }
        d_signs = [bit_to_sign(b) for b in d_bits]
        out["solution"] = {
            "phase_bits": phases,
            "singleton_sign_bits": s_bits,
            "su3_eps_bits": eps_bits,
            "ladder_const_bits": lconst_bits,
            "d_triples": [
                {"triple": list(triads[idx]), "sign": int(d_signs[idx])}
                for idx in range(45)
            ],
            "d_sign_distribution": {
                "-1": int(sum(1 for s in d_signs if s == -1)),
                "1": int(sum(1 for s in d_signs if s == 1)),
            },
        }

    out_path = ROOT / "artifacts" / "canonical_su3_gauge_and_cubic.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("PASS" if ok else "FAIL", "Combined SU3 ladder + cubic coupling solve.")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
