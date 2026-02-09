#!/usr/bin/env python3
"""
Build qutrit Clifford (metaplectic) lifts for SL(2,3) generators S and T,
verify conjugation action on Weyl operators, and compute induced permutations
and central Z3 phases on H27 and N12.

Usage:
  py -3 tools/build_qutrit_clifford_lift.py --bundle-dir artifacts/bundles/W33_Heisenberg_action_bundle_20260209_v1 --out-dir artifacts/bundles/W33_Heisenberg_action_bundle_20260209_v1/analysis

Outputs:
  - clifford_lift_on_H27_and_N12.json
  - clifford_lift_report.md

Notes:
  - Uses single-qutrit Weyl operators X,Z with D(p,q)=X^p Z^q.
  - Generators implemented: S=[[0,-1],[1,0]] -> Fourier F; T=[[1,1],[0,1]] -> diag(omega^{(1/2) x^2})
"""
from __future__ import annotations

import argparse
import cmath
import json
import math
from csv import DictReader
from io import TextIOWrapper
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

ROOT: Path = Path(__file__).resolve().parents[1]
ART: Path = ROOT / "artifacts"


def omega() -> complex:
    return cmath.exp(2j * cmath.pi / 3.0)


def build_XZ() -> Tuple[np.ndarray, np.ndarray]:
    # qutrit X shift and Z phase
    X = np.zeros((3, 3), dtype=complex)
    for j in range(3):
        X[(j + 1) % 3, j] = 1.0 + 0.0j
    w = omega()
    Z = np.diag([1.0 + 0.0j, w, w**2])
    return X, Z


def D(p: int, q: int, X: np.ndarray, Z: np.ndarray) -> np.ndarray:
    p = int(p) % 3
    q = int(q) % 3
    # D = X^p Z^q
    M = np.linalg.matrix_power(X, p) @ np.linalg.matrix_power(Z, q)
    return M


def fourier_matrix() -> np.ndarray:
    w = omega()
    F = np.zeros((3, 3), dtype=complex)
    s = 1.0 / math.sqrt(3.0)
    for j in range(3):
        for k in range(3):
            F[j, k] = s * (w ** (j * k))
    return F


def quadratic_phase_matrix() -> np.ndarray:
    # diagonal with entries omega^{(1/2) x^2}; inverse of 2 in F3 is 2
    w = omega()
    P = np.zeros((3, 3), dtype=complex)
    inv2 = 2
    for x in range(3):
        exp = (inv2 * (x * x)) % 3
        P[x, x] = w**exp
    return P


def apply_mat_to_point(
    mat: Tuple[int, int, int, int], p: Tuple[int, int]
) -> Tuple[int, int]:
    a, b, c, d = mat
    x, y = p
    nx: int = (a * x + b * y) % 3
    ny: int = (c * x + d * y) % 3
    return (nx, ny)


def load_h27(bundle_dir: Path) -> Dict[Tuple[int, int, int], int]:
    path = bundle_dir / "H27_vertices_as_F3_cube_xy_t.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    out = {}
    with path.open("r", encoding="utf-8") as f:
        hdr = f.readline()
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = [s.strip() for s in line.split(",")]
            wid = int(parts[0])
            x = int(parts[1])
            y = int(parts[2])
            t = int(parts[3])
            out[(x, y, t)] = wid
    return out


def load_n12(bundle_dir: Path) -> Dict[int, Dict]:
    import csv

    path = bundle_dir / "N12_vertices_as_affine_lines.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    data = {}
    with path.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            nid = int(r["N12_vertex"])
            slope_raw = r["slope_m"].strip()
            slope_val = "inf" if slope_raw.lower() == "inf" else int(slope_raw)
            intercept = int(r["intercept_b"])
            pts_field = r.get("phase_points", "")
            pts = []
            for p in [s.strip() for s in pts_field.split(";") if s.strip()]:
                p = p.strip("() ")
                if not p:
                    continue
                x_str, y_str = p.split(",")
                pts.append((int(x_str), int(y_str)))
            data[nid] = {
                "slope": slope_val,
                "intercept": int(intercept),
                "phase_points": pts,
            }
    return data


def compute_phase_scalar(M1: np.ndarray, D_target: np.ndarray) -> complex:
    # s = (1/3) * trace(D_target^* M1)
    s = np.trace(D_target.conj().T @ M1) / 3.0
    return complex(s)


def find_omega_k(s: complex) -> Tuple[int, float]:
    if abs(s) < 1e-12:
        return (0, float("nan"))
    s_unit = s / abs(s)
    w = omega()
    best_k = 0
    best_d = abs(s_unit - 1)
    for k in [0, 1, 2]:
        d = abs(s_unit - (w**k))
        if d < best_d:
            best_d = d
            best_k = k
    return best_k, best_d


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--bundle-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, default=None)
    args: argparse.Namespace = p.parse_args()

    bundle_dir = args.bundle_dir
    out_dir = args.out_dir if args.out_dir is not None else bundle_dir / "analysis"
    out_dir.mkdir(parents=True, exist_ok=True)

    hmap = load_h27(bundle_dir)
    n12 = load_n12(bundle_dir)

    X, Z = build_XZ()
    F = fourier_matrix()
    P = quadratic_phase_matrix()

    gens = [
        ("S", (0, 2, 1, 0), F),  # S = [[0,-1],[1,0]] -> F
        ("T", (1, 0, 1, 1), P),  # T = [[1,0],[1,1]] -> quadratic phase
    ]

    gen_out = []
    for name, mat, U in gens:
        perm_H = {}
        perm_N12 = {}
        failures = []
        # verify for all (p,q)
        for pxy in [(i, j) for i in range(3) for j in range(3)]:
            p, q = pxy
            Dpq = D(p, q, X, Z)
            M1 = U @ Dpq @ U.conj().T
            # image in phase-space under SL2 matrix
            p2 = apply_mat_to_point(mat, pxy)
            Dtarget = D(p2[0], p2[1], X, Z)
            s = compute_phase_scalar(M1, Dtarget)
            k, d = find_omega_k(s)
            # verify closeness: ||M1 - omega^k * Dtarget|| small
            s_unit = omega() ** k
            err = np.linalg.norm(M1 - s_unit * Dtarget)
            if err > 1e-8:
                failures.append({"p": pxy, "err": float(err), "s": s})
            # record phase shift phi = k for mapping on (x,y,t)
            phi = int(k % 3)
            # map H vertices (for t in 0,1,2)
            for t in range(3):
                src = (p, q, t)
                dst = (p2[0], p2[1], (t + phi) % 3)
                if src in hmap and dst in hmap:
                    perm_H[str(hmap[src])] = int(hmap[dst])
                else:
                    # fail to map - should not happen
                    failures.append({"mapping_failed": (src, dst)})
        # map N12 by phase point images
        for nid, d in n12.items():
            pts = d["phase_points"]
            mapped: List[Tuple[int]] = [apply_mat_to_point(mat, p) for p in pts]
            mapped_sorted: Tuple[Tuple[int]] = tuple(sorted(mapped))
            found = None
            for cand_nid, cand_d in n12.items():
                if tuple(sorted(cand_d["phase_points"])) == mapped_sorted:
                    found: int = cand_nid
                    break
            if found is None:
                failures.append(
                    {"n12_map_failed": {"nid": nid, "mapped": mapped_sorted}}
                )
            else:
                perm_N12[str(nid)] = int(found)

        # Prepare JSON-serializable unitary (re/im) and normalize failures
        unitary_serial: List[List[Dict[str, float]]] = [
            [{"re": float(np.real(v)), "im": float(np.imag(v))} for v in row]
            for row in U.tolist()
        ]
        failures_serial = []
        for f in failures:
            f2 = {}
            for kf, vf in f.items():
                if isinstance(vf, complex):
                    f2[kf] = {"re": float(vf.real), "im": float(vf.imag)}
                else:
                    f2[kf] = vf
            failures_serial.append(f2)
        verified: bool = len(failures) == 0
        gen_out.append(
            {
                "name": name,
                "matrix": list(mat),
                "unitary": unitary_serial,
                "perm_H": perm_H,
                "perm_N12": perm_N12,
                "failures": failures_serial,
                "verified": bool(verified),
            }
        )

    out = {"status": "ok", "generators": gen_out}
    (out_dir / "clifford_lift_on_H27_and_N12.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )

    md = []
    md.append("# Clifford (qutrit) lift on H27/N12")
    md.append("")
    for g in gen_out:
        md.append(f"Generator: {g['name']}")
        md.append(f" - failures: {len(g['failures'])}")
    (out_dir / "clifford_lift_report.md").write_text("\n".join(md), encoding="utf-8")

    print(f"Wrote {(out_dir / 'clifford_lift_on_H27_and_N12.json')}")
    print(f"Wrote {(out_dir / 'clifford_lift_report.md')} ")


if __name__ == "__main__":
    main()
