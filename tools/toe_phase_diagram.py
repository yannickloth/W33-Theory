#!/usr/bin/env python3
"""
TOE phase diagram sweep (firewall_strength × phase_noise) on the 27-state sector.

This is a deterministic, dependency-free replacement for the reported-but-missing
"v4 phase diagram" notebooks mentioned in `More New Work/*v3p47.zip` (not present
in the repo drop). It builds on `tools/toe_dynamics.py`.

Grid point (fw, sigma):
  - Build phases on Schläfli + bad edges with Gaussian jitter (sigma)
  - Build U = exp(i dt M) with bad-edge weight (1-fw)
  - Random-search a best conserved Cartan charge H = Σ c_i h_i (true E6 Cartan)
  - Record: best score, drift, commutator norm, eigenspace split, holonomy entropy

Outputs:
  - artifacts/toe_phase_diagram_summary.json
  - artifacts/toe_phase_diagram_report.md
  - optional .ppm heatmaps (no matplotlib/PIL dependency)
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from dataclasses import asdict
from math import log
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to import {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


toe_dynamics = _load_module(ROOT / "tools" / "toe_dynamics.py", "toe_dynamics")


def _linspace(a: float, b: float, n: int) -> List[float]:
    if n <= 1:
        return [float(a)]
    return [float(a + (b - a) * i / (n - 1)) for i in range(n)]


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _entropy_from_weighted_hist(hist: Dict[int, float]) -> float:
    total = float(sum(hist.values()))
    if total <= 0.0:
        return 0.0
    ent = 0.0
    for w in hist.values():
        if w > 0.0:
            p = w / total
            ent -= p * log(p)
    return float(ent)


def _triangles_in_union_graph(
    good_adj: np.ndarray, bad_edges: Sequence[Tuple[int, int]]
) -> List[Tuple[int, int, int]]:
    n = good_adj.shape[0]
    bad_adj = np.zeros((n, n), dtype=bool)
    for u, v in bad_edges:
        bad_adj[u, v] = True
        bad_adj[v, u] = True
    union = np.logical_or(good_adj, bad_adj)
    return toe_dynamics.triangles_in_graph(union)


def _write_ppm_heatmap(path: Path, grid: np.ndarray, *, invert: bool = False) -> None:
    """Write a simple grayscale PPM (P3) heatmap for a 2D array."""
    if grid.ndim != 2:
        raise ValueError("Expected 2D grid")
    h, w = grid.shape
    finite = grid[np.isfinite(grid)]
    if finite.size == 0:
        vmin, vmax = 0.0, 1.0
    else:
        vmin = float(np.min(finite))
        vmax = float(np.max(finite))
    denom = (vmax - vmin) if vmax > vmin else 1.0

    def scale(x: float) -> int:
        if not np.isfinite(x):
            return 0
        t = (float(x) - vmin) / denom
        if invert:
            t = 1.0 - t
        t = min(1.0, max(0.0, t))
        return int(round(255 * t))

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="ascii") as f:
        f.write(f"P3\n{w} {h}\n255\n")
        for i in range(h):
            row = []
            for j in range(w):
                g = scale(float(grid[i, j]))
                row.append(f"{g} {g} {g}")
            f.write(" ".join(row) + "\n")


def main(argv: Sequence[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fw-n", type=int, default=11)
    p.add_argument("--sigma-n", type=int, default=11)
    p.add_argument("--sigma-max", type=float, default=0.60)
    p.add_argument("--dt", type=float, default=0.35)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument(
        "--phase-source",
        choices=["random", "w33_clock"],
        default="random",
        help="Edge phase source: seeded random Z6 or deterministic W33 holonomy-derived clock.",
    )
    p.add_argument("--charge-samples", type=int, default=250)
    p.add_argument("--charge-steps", type=int, default=30)
    p.add_argument("--comm-weight", type=float, default=0.05)
    p.add_argument("--write-ppm", action="store_true")
    p.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "toe_phase_diagram_summary.json",
    )
    p.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "artifacts" / "toe_phase_diagram_report.md",
    )
    args = p.parse_args(list(argv) if argv is not None else None)

    fw_vals = _linspace(0.0, 1.0, int(args.fw_n))
    sig_vals = _linspace(0.0, float(args.sigma_max), int(args.sigma_n))

    skew, meet = toe_dynamics.load_schlafli_graph()
    fw = toe_dynamics.load_firewall_bad_edges()
    cartan = toe_dynamics.load_e6_cartan()
    cartan_diag = np.array(
        [np.real(np.diag(cartan[i])).astype(float) for i in range(6)], dtype=float
    )

    good_edges = toe_dynamics.edge_list_from_adj(skew)
    all_edges = good_edges + sorted(fw.bad_edges)

    # Precompute triangles for both "pure Schläfli" and union graph.
    tris_schlafli = toe_dynamics.triangles_in_graph(skew)
    tris_union = _triangles_in_union_graph(skew, sorted(fw.bad_edges))

    # Cache whether an undirected edge is "bad".
    bad_set = set(fw.bad_edges)

    results: List[List[Dict[str, object]]] = []

    # Heatmap grids (fw index major, sigma index minor)
    grid_score = np.zeros((len(fw_vals), len(sig_vals)), dtype=float)
    grid_drift = np.zeros_like(grid_score)
    grid_comm = np.zeros_like(grid_score)
    grid_hol = np.zeros_like(grid_score)
    grid_edges = np.zeros_like(grid_score)

    best_global = None

    for i_fw, fw_strength in enumerate(fw_vals):
        row: List[Dict[str, object]] = []
        for j_sig, sigma in enumerate(sig_vals):
            phase_seed = int(args.seed)
            theta = toe_dynamics.build_edge_phases(
                all_edges,
                seed=phase_seed,
                noise_sigma=float(sigma),
                phase_mod=6,
                source=str(args.phase_source),
            )
            m = toe_dynamics.build_hamiltonian(
                good_adj=skew,
                bad_edges=fw.bad_edges,
                theta=theta,
                firewall_strength=float(fw_strength),
            )
            u = toe_dynamics.unitary_from_hermitian(m, dt=float(args.dt))

            charge_seed = int(args.seed) + 1_000_003 * i_fw + 10_007 * j_sig + 123
            best = toe_dynamics.best_conserved_charge(
                u=u,
                cartan=cartan,
                n_samples=int(args.charge_samples),
                seed=charge_seed,
                steps=int(args.charge_steps),
                comm_weight=float(args.comm_weight),
            )

            # Evaluate the 6 canonical Cartan directions individually on the same trajectory/initial state.
            rng = np.random.default_rng(charge_seed)
            psi0 = rng.normal(size=27) + 1j * rng.normal(size=27)
            psi0 = psi0 / np.linalg.norm(psi0)
            probs = np.zeros((int(args.charge_steps) + 1, 27), dtype=float)
            psi = psi0
            probs[0] = np.abs(psi) ** 2
            for t in range(1, int(args.charge_steps) + 1):
                psi = u @ psi
                probs[t] = np.abs(psi) ** 2
            abs_u2 = np.abs(u) ** 2

            basis_scores = []
            best_basis = None
            for ii in range(6):
                diag = cartan_diag[ii]
                diff = diag[:, None] - diag[None, :]
                comm_n = float(np.sqrt(np.sum((diff * diff) * abs_u2)))
                exps = probs @ diag
                deltas = np.abs(np.diff(exps))
                mean_d = float(np.mean(deltas)) if deltas.size else 0.0
                max_d = float(np.max(deltas)) if deltas.size else 0.0
                score = float(mean_d + float(args.comm_weight) * comm_n)
                dims = {
                    "plus": int(np.sum(diag > 1e-9)),
                    "minus": int(np.sum(diag < -1e-9)),
                    "zero": int(np.sum(np.abs(diag) <= 1e-9)),
                }
                brow = {
                    "i": ii + 1,
                    "score": score,
                    "mean_drift": mean_d,
                    "max_drift": max_d,
                    "comm_norm": comm_n,
                    "dims": dims,
                }
                basis_scores.append(brow)
                if best_basis is None or brow["score"] < best_basis["score"]:
                    best_basis = brow

            # Holonomy entropy:
            # - base holonomy: Schläfli triangles only (independent of fw)
            # - weighted holonomy on union triangles, where each bad edge contributes a factor (1-fw)
            hist_s, ent_s = toe_dynamics.holonomy_histogram(
                triangles=tris_schlafli, theta=theta, bins=24
            )
            bad_w = 1.0 - float(fw_strength)
            hist_u: Dict[int, float] = {k: 0.0 for k in range(24)}
            two_pi = float(2.0 * np.pi)
            for a, b, c in tris_union:
                ang = float(theta[a, b] + theta[b, c] + theta[c, a])
                x = (ang / two_pi) * 24
                bin_ = int(np.floor(x + 0.5)) % 24
                n_bad = (
                    int(((min(a, b), max(a, b)) in bad_set))
                    + int(((min(b, c), max(b, c)) in bad_set))
                    + int(((min(c, a), max(c, a)) in bad_set))
                )
                w_tri = bad_w**n_bad
                hist_u[bin_] += float(w_tri)
            ent_u = _entropy_from_weighted_hist(hist_u)

            eff_edges = 216.0 + 27.0 * (1.0 - float(fw_strength))

            cell = {
                "fw": float(fw_strength),
                "sigma": float(sigma),
                "effective_allowed_edges": eff_edges,
                "holonomy": {
                    "schlafli_entropy_nats": float(ent_s),
                    "union_weighted_entropy_nats": float(ent_u),
                },
                "best_charge": asdict(best),
                "best_basis_charge": best_basis,
                "basis_charges": basis_scores,
            }
            row.append(cell)

            grid_score[i_fw, j_sig] = float(best.score)
            grid_drift[i_fw, j_sig] = float(best.mean_drift)
            grid_comm[i_fw, j_sig] = float(best.comm_norm)
            grid_hol[i_fw, j_sig] = float(ent_u)
            grid_edges[i_fw, j_sig] = float(eff_edges)

            if best_global is None or best.score < best_global["best_charge"]["score"]:
                best_global = {
                    "fw": float(fw_strength),
                    "sigma": float(sigma),
                    "best_charge": asdict(best),
                }

        results.append(row)

    out = {
        "params": {
            "dt": float(args.dt),
            "seed": int(args.seed),
            "charge_samples": int(args.charge_samples),
            "charge_steps": int(args.charge_steps),
            "comm_weight": float(args.comm_weight),
            "bins": 24,
        },
        "grid": {"firewall_strength": fw_vals, "phase_noise_sigma": sig_vals},
        "graph": {
            "good_edges": len(good_edges),
            "bad_edges": len(fw.bad_edges),
            "schlafli_triangles": len(tris_schlafli),
            "union_triangles": len(tris_union),
        },
        "best_overall": best_global,
        "cells": results,
    }
    _write_json(args.out_json, out)

    # Markdown report (compact, no plots).
    lines: List[str] = []
    lines.append("# TOE phase diagram (27-state sector)")
    lines.append("")
    lines.append("## Parameters")
    lines.append(f"- dt: `{args.dt}`")
    lines.append(f"- firewall_strength grid: `{len(fw_vals)}` values in [0,1]")
    lines.append(
        f"- phase_noise σ grid: `{len(sig_vals)}` values in [0,{args.sigma_max}]"
    )
    lines.append(
        f"- charge search: `{args.charge_samples}` samples, `{args.charge_steps}` steps, comm_weight `{args.comm_weight}`"
    )
    lines.append("")
    lines.append("## Best point (lowest score)")
    if best_global is not None:
        lines.append(f"- fw: `{best_global['fw']}`")
        lines.append(f"- sigma: `{best_global['sigma']}`")
        lines.append(f"- score: `{best_global['best_charge']['score']}`")
        lines.append(f"- mean_drift: `{best_global['best_charge']['mean_drift']}`")
        lines.append(f"- comm_norm: `{best_global['best_charge']['comm_norm']}`")
        lines.append(f"- dims: `{best_global['best_charge']['dims']}`")
    lines.append("")
    winners = Counter()
    for row in results:
        for cell in row:
            bb = cell.get("best_basis_charge")
            if isinstance(bb, dict) and "i" in bb:
                winners[int(bb["i"])] += 1
    lines.append("## Best Single-Direction Cartan (argmin over {h_i})")
    lines.append(f"- counts: `{dict(sorted(winners.items()))}`")
    lines.append("")
    lines.append(f"- JSON: `{args.out_json}`")
    lines.append(f"- Heatmaps (PPM): set `--write-ppm`")
    _write_md(args.out_md, lines)

    if args.write_ppm:
        out_dir = args.out_json.parent
        _write_ppm_heatmap(out_dir / "phase_diagram_score.ppm", grid_score, invert=True)
        _write_ppm_heatmap(out_dir / "phase_diagram_drift.ppm", grid_drift, invert=True)
        _write_ppm_heatmap(out_dir / "phase_diagram_comm.ppm", grid_comm, invert=True)
        _write_ppm_heatmap(
            out_dir / "phase_diagram_hol_entropy.ppm", grid_hol, invert=True
        )
        _write_ppm_heatmap(
            out_dir / "phase_diagram_edgecount.ppm", grid_edges, invert=False
        )

    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
