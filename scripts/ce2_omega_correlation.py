"""Utilities for comparing CE2 simple-family sign map with symplectic omega values."""
from __future__ import annotations

import sys
from pathlib import Path

from collections import defaultdict
from typing import Dict, Tuple

# ensure workspace root and scripts directory are on sys.path (same pattern used elsewhere)
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from scripts.ce2_global_cocycle import _heisenberg_vec_maps, _simple_family_sign_map
from scripts.grade_weil_phase import omega


def compute_omega_distribution() -> Dict[int, int]:
    """Return histogram of omega(um, uo) values over the simple-family CE2 data."""
    e6id_to_vec, _ = _heisenberg_vec_maps()
    sign_map = _simple_family_sign_map()

    hist: dict[int, int] = {0: 0, 1: 0, 2: 0}
    for (_, m_i, o_i), _ in sign_map.items():
        um = tuple(e6id_to_vec[m_i][:2])
        uo = tuple(e6id_to_vec[o_i][:2])
        hist[omega(um, uo)] += 1
    return hist


def compute_sign_vs_omega_stats() -> Dict[int, Dict[int, int]]:
    """Return counts of CE2 sign values partitioned by omega value in {1,2}."""
    e6id_to_vec, _ = _heisenberg_vec_maps()
    sign_map = _simple_family_sign_map()

    stats: dict[int, dict[int, int]] = {1: defaultdict(int), 2: defaultdict(int)}
    for (_, m_i, o_i), sign in sign_map.items():
        um = tuple(e6id_to_vec[m_i][:2])
        uo = tuple(e6id_to_vec[o_i][:2])
        w = omega(um, uo)
        if w in (1, 2):
            stats[w][sign] += 1
    return stats


def main() -> None:
    """Simple command-line report."""
    dist = compute_omega_distribution()
    stats = compute_sign_vs_omega_stats()
    print("omega histogram:", dist)
    print("sign vs omega stats:")
    for w in sorted(stats):
        print(f"  omega={w}: {stats[w]}")


if __name__ == "__main__":
    main()
