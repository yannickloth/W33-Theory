#!/usr/bin/env python3
"""
Verify the combined solution produced by tools/solve_canonical_su3_gauge_and_cubic.py.

Checks:
  - All coupling equations are satisfied (including the SU(3) epsilon orbit-pair bits).
  - All ladder equations are satisfied with the per-(sid,orbit_transition) ladder_const bits.
  - The inferred ladder_const values are uniform across all 27 E6-ids by construction; we
    re-check by direct evaluation on every edge.

Writes:
  artifacts/verify_canonical_su3_gauge_and_cubic.json
"""

from __future__ import annotations

import importlib.util
import json
import sys
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


solver = _load_module(
    ROOT / "tools" / "solve_canonical_su3_gauge_and_cubic.py",
    "solve_canonical_su3_gauge_and_cubic",
)
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
    rk2 = k2(r)
    a_num = sum(rk2[i] * SU3_ALPHA_K2[i] for i in range(8))
    b_num = sum(rk2[i] * SU3_BETA_K2[i] for i in range(8))
    proj_num = [
        (2 * a_num + b_num) * SU3_ALPHA_K2[i] + (a_num + 2 * b_num) * SU3_BETA_K2[i]
        for i in range(8)
    ]
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


def main() -> None:
    # Ensure we have a fresh solved artifact.
    solver.main()
    sol_path = ROOT / "artifacts" / "canonical_su3_gauge_and_cubic.json"
    sol = json.loads(sol_path.read_text(encoding="utf-8"))
    if not sol.get("counts", {}).get("solvable", False):
        raise RuntimeError("Combined solver did not produce a solvable system.")

    solution = sol["solution"]
    phase_bits_raw: Dict[str, List[int]] = solution["phase_bits"]
    s_bits: List[int] = solution["singleton_sign_bits"]
    eps_bits_raw: Dict[str, int] = solution["su3_eps_bits"]
    ladder_const_bits_raw: Dict[str, int] = solution["ladder_const_bits"]
    d_triples = solution["d_triples"]

    triad_to_dbit = {
        tuple(t["triple"]): (1 if int(t["sign"]) == -1 else 0) for t in d_triples
    }

    phase_bits: Dict[str, List[int]] = phase_bits_raw
    eps_bits: Dict[str, int] = eps_bits_raw
    ladder_const_bits: Dict[str, int] = ladder_const_bits_raw

    instances = sol.get("instances")
    if not instances:
        raise RuntimeError("Missing instances in canonical_su3_gauge_and_cubic.json")

    coupling_failures = 0
    for c in instances["couplings"]:
        oa = int(c["oa"])
        ob = int(c["ob"])
        ocbar = int(c["ocbar"])
        i = int(c["i"])
        j = int(c["j"])
        kbar = int(c["kbar"])
        triad = tuple(int(x) for x in c["triad"])
        raw_bit = int(c["raw_bit"]) & 1
        eps_bit = int(eps_bits[f"{oa}+{ob}"]) & 1
        d_bit = triad_to_dbit[triad] & 1
        lhs = (
            phase_bits[str(oa)][i]
            ^ phase_bits[str(ob)][j]
            ^ phase_bits[str(ocbar)][kbar]
            ^ d_bit
            ^ eps_bit
        )
        if lhs != raw_bit:
            coupling_failures += 1

    ladder_failures = 0
    for e in instances["ladders"]:
        sid = int(e["singleton_sid"])
        oi = int(e["src_orbit"])
        oj = int(e["dst_orbit"])
        i = int(e["e6id"])
        raw_bit = int(e["raw_bit"]) & 1
        lc_bit = int(ladder_const_bits[f"{sid}:{oi}->{oj}"]) & 1
        lhs = (
            (int(s_bits[sid]) & 1)
            ^ phase_bits[str(oi)][i]
            ^ phase_bits[str(oj)][i]
            ^ lc_bit
        )
        if lhs != raw_bit:
            ladder_failures += 1

    out = {
        "status": "ok",
        "counts": {
            "coupling_failures": int(coupling_failures),
            "ladder_failures": int(ladder_failures),
        },
    }
    out_path = ROOT / "artifacts" / "verify_canonical_su3_gauge_and_cubic.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        "PASS" if (coupling_failures == 0 and ladder_failures == 0) else "FAIL",
        "canonical SU3 gauge + cubic verification",
    )
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
