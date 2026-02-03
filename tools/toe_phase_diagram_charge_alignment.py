#!/usr/bin/env python3
"""
Analyze the phase diagram's emergent conserved-charge direction and align it to
canonical E6/SM U(1) directions.

Inputs:
  - artifacts/toe_phase_diagram_summary.json
  - (optional) artifacts/toe_phase_diagram_v5_summary.json

We treat each best_charge coefficient vector c (in the canonical E6 Cartan basis h_i)
as defining an emergent U(1): H = Σ c_i h_i. We then compare it to canonical
charge directions expressed in the same basis:
  - Y  : SU(5) hypercharge direction used by `tools/toe_sm_cubic_firewall_analysis.py`
  - Qψ : E6→SO(10)×U(1)_ψ fundamental coweight ω0^∨ (up to scaling)
  - Qχ : a second standard U(1) along the SU(5) chain (ω3^∨, up to scaling)
  - T3 : SU(2)_L Cartan (node 6 in our 0-based indexing: index 5)

Outputs:
  - artifacts/toe_phase_diagram_charge_alignment.json
  - artifacts/toe_phase_diagram_charge_alignment.md
  - optional PPM heatmap of best-aligned label (no matplotlib dependency)
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

E6_CARTAN: np.ndarray = np.array(
    [
        [2, -1, 0, 0, 0, 0],
        [-1, 2, -1, 0, 0, 0],
        [0, -1, 2, -1, -1, 0],
        [0, 0, -1, 2, 0, 0],
        [0, 0, -1, 0, 2, -1],
        [0, 0, 0, 0, -1, 2],
    ],
    dtype=float,
)


def _load_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _normalize(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    if n == 0.0:
        return v
    return v / n


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _write_ppm_label_map(
    path: Path, labels: np.ndarray, palette: List[Tuple[int, int, int]]
) -> None:
    """Write a color PPM (P3) map for integer labels."""
    if labels.ndim != 2:
        raise ValueError("Expected 2D label grid")
    h, w = labels.shape
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="ascii") as f:
        f.write(f"P3\n{w} {h}\n255\n")
        for i in range(h):
            row = []
            for j in range(w):
                k = int(labels[i, j])
                if k < 0 or k >= len(palette):
                    rgb = (0, 0, 0)
                else:
                    rgb = palette[k]
                row.append(f"{rgb[0]} {rgb[1]} {rgb[2]}")
            f.write(" ".join(row) + "\n")


@dataclass(frozen=True)
class ChargeDir:
    name: str
    coeffs: np.ndarray  # shape (6,)


def _fundamental_coweight(idx: int) -> np.ndarray:
    """Return ω_idx^∨ coefficients in the simple-coroot basis (float)."""
    e = np.zeros(6, dtype=float)
    e[int(idx)] = 1.0
    # Solve C^T t = e
    t = np.linalg.solve(E6_CARTAN.T, e)
    return t.astype(float)


def main(argv: Sequence[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--phase-json",
        type=Path,
        default=ROOT / "artifacts" / "toe_phase_diagram_summary.json",
    )
    p.add_argument(
        "--v5-json",
        type=Path,
        default=ROOT / "artifacts" / "toe_phase_diagram_v5_summary.json",
    )
    p.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "toe_phase_diagram_charge_alignment.json",
    )
    p.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "artifacts" / "toe_phase_diagram_charge_alignment.md",
    )
    p.add_argument("--write-ppm", action="store_true")
    args = p.parse_args(list(argv) if argv is not None else None)

    phase = _load_json(args.phase_json)
    fw_vals = [float(x) for x in phase["grid"]["firewall_strength"]]
    sig_vals = [float(x) for x in phase["grid"]["phase_noise_sigma"]]
    cells = phase["cells"]
    if not (isinstance(cells, list) and cells and isinstance(cells[0], list)):
        raise RuntimeError("Invalid phase diagram JSON: missing cells grid")

    # Canonical charge directions (coefficients on the canonical Cartan h_i basis).
    # Hypercharge direction used in `tools/toe_sm_cubic_firewall_analysis.py`:
    # y = (0, 1/3, 2/3, 0, 1, 1/2) acting on Dynkin labels.
    y = np.array([0.0, 1.0 / 3.0, 2.0 / 3.0, 0.0, 1.0, 1.0 / 2.0], dtype=float)
    qpsi = _fundamental_coweight(0)  # ω0^∨
    qchi = _fundamental_coweight(3)  # ω3^∨
    t3 = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 1.0], dtype=float)  # SU(2) node

    dirs = [
        ChargeDir("Y", _normalize(y)),
        ChargeDir("Qpsi", _normalize(qpsi)),
        ChargeDir("Qchi", _normalize(qchi)),
        ChargeDir("T3", _normalize(t3)),
    ]

    n_fw = len(fw_vals)
    n_sig = len(sig_vals)
    best_label = np.zeros((n_fw, n_sig), dtype=int)
    best_sim = np.zeros((n_fw, n_sig), dtype=float)
    sims_by_dir = {d.name: np.zeros((n_fw, n_sig), dtype=float) for d in dirs}

    # Analyze alignment per cell.
    for i in range(n_fw):
        row = cells[i]
        for j in range(n_sig):
            cell = row[j]
            coeffs = np.array(cell["best_charge"]["coeffs"], dtype=float)
            coeffs = _normalize(coeffs)
            sims = [abs(_cosine(coeffs, d.coeffs)) for d in dirs]
            for k, d in enumerate(dirs):
                sims_by_dir[d.name][i, j] = float(sims[k])
            kbest = int(np.argmax(np.array(sims, dtype=float)))
            best_label[i, j] = kbest
            best_sim[i, j] = float(sims[kbest])

    # Summary counts.
    counts = {d.name: int(np.sum(best_label == k)) for k, d in enumerate(dirs)}

    # Ordered/disordered split (same heuristic as v5): drift <= median AND holonomy <= median.
    drift = np.zeros((n_fw, n_sig), dtype=float)
    hol = np.zeros((n_fw, n_sig), dtype=float)
    for i in range(n_fw):
        row = cells[i]
        for j in range(n_sig):
            cell = row[j]
            drift[i, j] = float(cell["best_charge"]["mean_drift"])
            hol[i, j] = float(cell["holonomy"]["union_weighted_entropy_nats"])
    drift_med = float(np.median(drift))
    hol_med = float(np.median(hol))
    ordered = np.logical_and(drift <= drift_med, hol <= hol_med)
    counts_ordered = {
        d.name: int(np.sum(np.logical_and(best_label == k, ordered)))
        for k, d in enumerate(dirs)
    }
    counts_disordered = {
        d.name: int(np.sum(np.logical_and(best_label == k, ~ordered)))
        for k, d in enumerate(dirs)
    }

    # Optional compare to v5 critical boundary.
    v5 = None
    if args.v5_json.exists():
        v5 = _load_json(args.v5_json)

    out: Dict[str, object] = {
        "status": "ok",
        "grid": {"firewall_strength": fw_vals, "phase_noise_sigma": sig_vals},
        "charge_dirs": {
            d.name: {"coeffs": [float(x) for x in d.coeffs.tolist()]} for d in dirs
        },
        "counts_best_label": counts,
        "thresholds": {"drift_median": drift_med, "holonomy_entropy_median": hol_med},
        "counts_best_label_ordered": counts_ordered,
        "counts_best_label_disordered": counts_disordered,
        "cells": [
            [
                {
                    "fw": float(fw_vals[i]),
                    "sigma": float(sig_vals[j]),
                    "best": {
                        "label": dirs[int(best_label[i, j])].name,
                        "sim": float(best_sim[i, j]),
                    },
                    "sims": {
                        name: float(sims_by_dir[name][i, j]) for name in sims_by_dir
                    },
                }
                for j in range(n_sig)
            ]
            for i in range(n_fw)
        ],
    }
    if v5 is not None:
        out["v5"] = v5

    _write_json(args.out_json, out)

    # Human-readable report.
    lines: List[str] = []
    lines.append("# TOE Phase Diagram: Emergent Charge Alignment")
    lines.append("")
    lines.append(
        "For each (firewall_strength, phase_noise_sigma) cell, we compare the optimized"
    )
    lines.append(
        "best conserved Cartan direction `c` to canonical charge directions in the same"
    )
    lines.append(
        "E6 Cartan basis: Y, Qψ, Qχ, and T3. Similarity is `|cosine(c, dir)|`."
    )
    lines.append("")
    lines.append("## Best-aligned label counts")
    for d in dirs:
        lines.append(f"- {d.name}: `{counts[d.name]}` cells")
    lines.append("")
    lines.append("## Best-aligned label counts by phase (ordered vs disordered)")
    lines.append(
        f"- ordered criterion: drift ≤ `{drift_med:.4e}` AND holonomy ≤ `{hol_med:.4e}`"
    )
    for d in dirs:
        lines.append(
            f"- {d.name}: ordered `{counts_ordered[d.name]}`  disordered `{counts_disordered[d.name]}`"
        )
    lines.append("")
    lines.append("## Sanity checks at corners")
    corners = [(0, 0), (0, n_sig - 1), (n_fw - 1, 0), (n_fw - 1, n_sig - 1)]
    for i, j in corners:
        lab = dirs[int(best_label[i, j])].name
        sim = float(best_sim[i, j])
        lines.append(
            f"- fw={fw_vals[i]:.2f}, sigma={sig_vals[j]:.2f}: best `{lab}` (sim `{sim:.3f}`)"
        )
    lines.append("")
    if v5 is not None and isinstance(v5, dict):
        thr = v5.get("thresholds", {})
        if isinstance(thr, dict):
            lines.append("## v5 thresholds (reference)")
            lines.append(f"- drift_median: `{float(thr.get('drift_median', 0.0)):.4e}`")
            lines.append(
                f"- holonomy_entropy_median: `{float(thr.get('holonomy_entropy_median', 0.0)):.4e}`"
            )
            lines.append("")
    lines.append("## Outputs")
    lines.append(f"- JSON: `{args.out_json}`")
    if args.write_ppm:
        lines.append(
            f"- label heatmap (PPM): `artifacts/toe_phase_diagram_charge_alignment_labels.ppm`"
        )
    _write_md(args.out_md, lines)
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")

    if args.write_ppm:
        # Palette: Y=yellow, Qpsi=cyan, Qchi=magenta, T3=green
        palette = [
            (240, 220, 0),
            (0, 200, 200),
            (220, 0, 220),
            (0, 200, 0),
        ]
        _write_ppm_label_map(
            ROOT / "artifacts" / "toe_phase_diagram_charge_alignment_labels.ppm",
            best_label,
            palette,
        )


if __name__ == "__main__":
    main()
