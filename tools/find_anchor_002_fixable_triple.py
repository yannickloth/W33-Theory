"""Find a g1,g1,g2 triple with a=(0,0,2) that is fixed by the global CE2 predictor."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# Ensure the repository root is on sys.path so `tools` can be imported.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build_linfty_firewall_extension import LInftyE8Extension, _load_bad9, _load_bracket_tool
from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1, basis_elem_g2


def max_abs(e):
    return float(
        max(
            0.0 if e.e6.size == 0 else np.max(np.abs(e.e6)),
            0.0 if e.sl3.size == 0 else np.max(np.abs(e.sl3)),
            0.0 if e.g1.size == 0 else np.max(np.abs(e.g1)),
            0.0 if e.g2.size == 0 else np.max(np.abs(e.g2)),
        )
    )


def main():
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    a = (22, 0)  # anchor (0,0,2)
    for b in range(81):
        for c in range(81):
            linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)
            x = basis_elem_g1(toe, a)
            y = basis_elem_g1(toe, (b // 3, b % 3))
            z = basis_elem_g2(toe, (c // 3, c % 3))
            baseline = linfty.homotopy_jacobi(x, y, z)
            if max_abs(baseline) < 1e-10:
                continue
            linfty.enable_ce2_global_predictor()
            repaired = linfty.homotopy_jacobi(x, y, z)
            if max_abs(repaired) < 1e-10:
                print("Found fixable triple:", a, (b // 3, b % 3), (c // 3, c % 3))
                return
    print("No fixable triple found in scan")


if __name__ == "__main__":
    main()
