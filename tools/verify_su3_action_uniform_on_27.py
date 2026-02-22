#!/usr/bin/env python3
"""
Verify the A2 (=SU3) action on the (27,3) mixed roots is *uniform* across all 27 E6 weights,
after fixing the color gauge from singleton ladders.

After loading `phase_bits` from `artifacts/su3_color_gauge_from_singletons.json`, we:
  - Enumerate all 6 singleton roots (the A2 root system).
  - For each singleton root ρ and each color c, determine if ρ maps color c -> color c' (on any weight i).
  - For every weight i where the action exists, compute the normalized ladder coefficient sign:
        s_norm = sign([e_ρ, e_{(c,i)}] -> e_{(c',i)}) ⊕ phase_c(i) ⊕ phase_c'(i)
    and check it is constant across i.

This produces an explicit, consistent SU3 ladder-sign table (a monomial 3-representation)
that is the same for all 27 weights, i.e. we truly have 27 copies of the SU(3) fundamental.

Output:
  artifacts/su3_action_uniform_on_27.json
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter, defaultdict
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


def load_phases() -> List[List[int]]:
    data = json.loads(
        (ROOT / "artifacts" / "su3_color_gauge_from_singletons.json").read_text(
            encoding="utf-8"
        )
    )
    if not data["solve"]["solvable"]:
        raise RuntimeError("SU3 gauge artifact not solvable")
    return data["solution"]["phase_bits"]


def main() -> None:
    phase = load_phases()

    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    orbit_sizes = [len(o) for o in orbits]
    idx_orb: Dict[int, int] = {}
    for oi, orb in enumerate(orbits):
        for v in orb:
            idx_orb[v] = oi

    root_index = {k2(roots[i]): i for i in range(len(roots))}

    # Identify singleton A2 roots.
    singleton_idxs = [orbits[oi][0] for oi, sz in enumerate(orbit_sizes) if sz == 1]
    singleton_roots = [k2(roots[i]) for i in singleton_idxs]

    # Identify color orbits.
    mix_orbs = [oi for oi, sz in enumerate(orbit_sizes) if sz == 27]
    weights = {oi: su3_weight(roots[orbits[oi][0]]) for oi in mix_orbs}
    weights_3 = {(1, 0), (-1, 1), (0, -1)}
    color_orbs = sorted(
        [oi for oi in mix_orbs if weights[oi] in weights_3], key=lambda x: weights[x]
    )
    if len(color_orbs) != 3:
        raise RuntimeError("Failed to identify three SU3=3 color orbits")

    # E6 ids by projection.
    e6_groups: Dict[Tuple[int, ...], int] = {}
    root_to_e6id: Dict[int, int] = {}
    for oi in color_orbs:
        for ridx in orbits[oi]:
            k = e6_key(roots[ridx])
            if k not in e6_groups:
                e6_groups[k] = len(e6_groups)
            root_to_e6id[ridx] = e6_groups[k]
    if len(e6_groups) != 27:
        raise RuntimeError("Expected 27 E6 ids")

    # (color,e6id)->root index
    color_root_by_e6id = [[-1] * 27 for _ in range(3)]
    for c, oi in enumerate(color_orbs):
        for ridx in orbits[oi]:
            color_root_by_e6id[c][root_to_e6id[ridx]] = ridx
    if any(x == -1 for row in color_root_by_e6id for x in row):
        raise RuntimeError("Missing root for some (color,e6id)")

    # For each singleton root, record uniformity statistics.
    reports = []
    failures = 0

    for rho in singleton_roots:
        # For each color, determine destination (if any) and check sign uniformity.
        for c, oi in enumerate(color_orbs):
            dest_color = None
            sign_values = []
            for i in range(27):
                src_idx = color_root_by_e6id[c][i]
                src = k2(roots[src_idx])
                tgt = tuple(src[t] + rho[t] for t in range(8))
                tgt_idx = root_index.get(tgt)
                if tgt_idx is None:
                    continue
                dest_orb = idx_orb[tgt_idx]
                if dest_orb not in color_orbs:
                    raise RuntimeError("A2 action left color orbits (unexpected)")
                dc = color_orbs.index(dest_orb)
                if root_to_e6id[tgt_idx] != i:
                    raise RuntimeError("A2 action changed E6 id (unexpected)")
                n = N(rho, src, root_index)
                if abs(n) != 1:
                    raise RuntimeError("Expected |N|=1 for A2 action")
                s_norm = sign_to_bit(int(np.sign(n))) ^ phase[c][i] ^ phase[dc][i]
                sign_values.append(s_norm)
                if dest_color is None:
                    dest_color = dc
                elif dest_color != dc:
                    raise RuntimeError(
                        "Singleton root mapped one color to multiple colors"
                    )

            if not sign_values:
                continue  # zero action from this color
            dist = Counter(sign_values)
            uniform = len(dist) == 1
            if not uniform:
                failures += 1
            reports.append(
                {
                    "rho": list(rho),
                    "from_color": int(c),
                    "to_color": int(dest_color),
                    "count": int(len(sign_values)),
                    "uniform": bool(uniform),
                    "value_distribution": {str(k): int(v) for k, v in dist.items()},
                }
            )

    out = {
        "status": "ok",
        "counts": {"reports": len(reports), "nonuniform_reports": int(failures)},
        "reports": reports,
    }
    out_path = ROOT / "artifacts" / "su3_action_uniform_on_27.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("PASS" if failures == 0 else "FAIL", "SU3 action uniformity check.")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
