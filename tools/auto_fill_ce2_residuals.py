"""Automatically fill remaining CE2 predictor gaps by adding local solutions.

This script scans g1,g1,g2 triples and, whenever it finds a triple where the
homotopy Jacobi is nonzero and the CE2 global predictor does not fix it,
it computes a local CE2 solution and appends it to the sparse artifact.

It stops after adding a configurable number of entries.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

# Ensure repo root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build_linfty_firewall_extension import LInftyE8Extension, _load_bad9, _load_bracket_tool
from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1, basis_elem_g2

SPARSE_PATH = ROOT / "committed_artifacts" / "ce2_sparse_local_solutions.json"

MAX_ADDITIONS = 10
THRESHOLD = 1e-10


def max_abs(e):
    return float(
        max(
            0.0 if e.e6.size == 0 else np.max(np.abs(e.e6)),
            0.0 if e.sl3.size == 0 else np.max(np.abs(e.sl3)),
            0.0 if e.g1.size == 0 else np.max(np.abs(e.g1)),
            0.0 if e.g2.size == 0 else np.max(np.abs(e.g2)),
        )
    )


def load_sparse():
    with SPARSE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_sparse(data):
    with SPARSE_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def sparse_has_key(data, key):
    return any(rec.get("k") == key for rec in data.get("entries", []))


def add_sparse_entry(data, entry):
    data.setdefault("entries", []).append(entry)


def compute_local_entry(triple):
    a, b, c = triple
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(np.complex128)
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, a)
    y = basis_elem_g1(toe, b)
    z = basis_elem_g2(toe, c)

    res = linfty.compute_local_ce2_alpha_for_triple(
        x, y, z, return_uv=True, rationalize_uv=True, max_den=720
    )
    if res is None:
        return None

    _, _, _, U_rats, V_rats = res

    def to_sparse(rats):
        out = []
        for idx, val in enumerate(rats):
            if val is None or val == "None" or val == "0":
                continue
            out.append([idx, str(val)])
        return out

    return {
        "k": f"{a[0]},{a[1]}:{b[0]},{b[1]}:{c[0]},{c[1]}",
        "a": [a[0], a[1]],
        "b": [b[0], b[1]],
        "c": [c[0], c[1]],
        "U": to_sparse(U_rats),
        "V": to_sparse(V_rats),
    }


def main():
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(np.complex128)
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    sparse = load_sparse()
    added = 0

    # scan g1,g1,g2 triples
    for a in range(81):
        for b in range(81):
            for c in range(81):
                x = basis_elem_g1(toe, (a // 3, a % 3))
                y = basis_elem_g1(toe, (b // 3, b % 3))
                z = basis_elem_g2(toe, (c // 3, c % 3))

                baseline = linfty.homotopy_jacobi(x, y, z)
                if max_abs(baseline) < THRESHOLD:
                    continue

                linfty.enable_ce2_global_predictor()
                repaired = linfty.homotopy_jacobi(x, y, z)
                if max_abs(repaired) > THRESHOLD:
                    key = f"{a // 3},{a % 3}:{b // 3},{b % 3}:{c // 3},{c % 3}"
                    if sparse_has_key(sparse, key):
                        continue
                    entry = compute_local_entry(((a // 3, a % 3), (b // 3, b % 3), (c // 3, c % 3)))
                    if entry is None:
                        print("Failed to compute local CE2 for", key)
                        continue
                    add_sparse_entry(sparse, entry)
                    added += 1
                    print("Added missing CE2 for", key)
                    if added >= MAX_ADDITIONS:
                        save_sparse(sparse)
                        print(f"Added {added} entries; stopping.")
                        return

    save_sparse(sparse)
    print(f"Scan complete. Added {added} new entries.")


if __name__ == "__main__":
    main()
