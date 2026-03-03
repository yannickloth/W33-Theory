#!/usr/bin/env python3
"""Build a unified CKM/absolute-mass frontier report from stage-2 and stage-3 artifacts."""

from __future__ import annotations

import glob
import json
import time
from pathlib import Path
from typing import Any

import numpy as np

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from yukawa_mass_ratio_analysis import build_yukawa_tensor, singular_value_ratios, yukawa_from_vev

PDG_UP = np.array([0.00216, 1.2730, 172.57], dtype=float)  # u, c, t
PDG_DN = np.array([0.00470, 0.0935, 4.1830], dtype=float)  # d, s, b
R_UP = (float(PDG_UP[1] / PDG_UP[2]), float(PDG_UP[0] / PDG_UP[1]))
R_DN = (float(PDG_DN[1] / PDG_DN[2]), float(PDG_DN[0] / PDG_DN[1]))


def fit_scale(model: np.ndarray, target: np.ndarray) -> float:
    den = float(np.dot(model, model))
    if den <= 1e-18:
        return 0.0
    return float(np.dot(model, target) / den)


def ratio_err(r: tuple[float, float], t: tuple[float, float]) -> float:
    return float(np.log(r[0] / t[0]) ** 2 + np.log(r[1] / t[1]) ** 2)


def build_active_basis(tensor: np.ndarray) -> tuple[int, np.ndarray]:
    t_mat = tensor.reshape(9, 27)
    _, svals, vh = np.linalg.svd(t_mat, full_matrices=False)
    rank = int(np.sum(svals > 1e-10))
    return rank, vh[:rank, :].conj().T


def unpack(params: list[float], v_active: np.ndarray, rank: int) -> tuple[np.ndarray, np.ndarray]:
    x = np.asarray(params, dtype=float)
    a_up = x[:rank] + 1j * x[rank : 2 * rank]
    a_dn = x[2 * rank : 3 * rank] + 1j * x[3 * rank : 4 * rank]
    v_up = v_active @ a_up
    v_dn = v_active @ a_dn
    return v_up / np.linalg.norm(v_up), v_dn / np.linalg.norm(v_dn)


def compute_point_metrics(
    params: list[float],
    ckm_err: float,
    tensor: np.ndarray,
    v_active: np.ndarray,
    rank: int,
) -> dict[str, Any]:
    v_up, v_dn = unpack(params, v_active, rank)
    y_up = yukawa_from_vev(tensor, v_up)
    y_dn = yukawa_from_vev(tensor, v_dn)
    sv_up, r_up = singular_value_ratios(y_up)
    sv_dn, r_dn = singular_value_ratios(y_dn)

    m_up_model = np.array([sv_up[2], sv_up[1], sv_up[0]], dtype=float)
    m_dn_model = np.array([sv_dn[2], sv_dn[1], sv_dn[0]], dtype=float)
    k_up = fit_scale(m_up_model, PDG_UP)
    k_dn = fit_scale(m_dn_model, PDG_DN)
    k_ratio = float(k_up / k_dn) if k_dn > 1e-18 else 0.0

    p_up = k_up * m_up_model
    p_dn = k_dn * m_dn_model
    rel_up = np.abs(p_up - PDG_UP) / PDG_UP
    rel_dn = np.abs(p_dn - PDG_DN) / PDG_DN
    rel_rms = float(np.sqrt(np.mean(np.concatenate([rel_up, rel_dn]) ** 2)))

    abs_up = float(np.sum(np.log(np.clip(p_up, 1e-18, None) / PDG_UP) ** 2))
    abs_dn = float(np.sum(np.log(np.clip(p_dn, 1e-18, None) / PDG_DN) ** 2))
    abs_err = abs_up + abs_dn

    r_up_t = (float(r_up[0]), float(r_up[1]))
    r_dn_t = (float(r_dn[0]), float(r_dn[1]))
    ratio_total = ratio_err(r_up_t, R_UP) + ratio_err(r_dn_t, R_DN)

    return {
        "ckm_err": float(ckm_err),
        "abs_mass_err": float(abs_err),
        "rel_rms": rel_rms,
        "ratio_total_err": float(ratio_total),
        "ratios_up": [r_up_t[0], r_up_t[1]],
        "ratios_dn": [r_dn_t[0], r_dn_t[1]],
        "k_up": float(k_up),
        "k_dn": float(k_dn),
        "k_ratio": float(k_ratio),
    }


def pareto_front(points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(points, key=lambda p: (p["ckm_err"], p["abs_mass_err"]))
    out: list[dict[str, Any]] = []
    best_abs = float("inf")
    for p in ordered:
        if p["abs_mass_err"] < best_abs:
            out.append(p)
            best_abs = p["abs_mass_err"]
    return out


def summarize(points: list[dict[str, Any]]) -> dict[str, Any]:
    arr_ckm = np.array([p["ckm_err"] for p in points], dtype=float)
    arr_abs = np.array([p["abs_mass_err"] for p in points], dtype=float)
    arr_rel = np.array([p["rel_rms"] for p in points], dtype=float)
    arr_ratio = np.array([p["ratio_total_err"] for p in points], dtype=float)
    arr_kdn = np.array([p["k_dn"] for p in points], dtype=float)
    arr_kr = np.array([p["k_ratio"] for p in points], dtype=float)
    return {
        "count": int(len(points)),
        "ckm_min_mean_max": [float(arr_ckm.min()), float(arr_ckm.mean()), float(arr_ckm.max())],
        "abs_min_mean_max": [float(arr_abs.min()), float(arr_abs.mean()), float(arr_abs.max())],
        "rel_rms_min_mean_max": [float(arr_rel.min()), float(arr_rel.mean()), float(arr_rel.max())],
        "ratio_total_min_mean_max": [float(arr_ratio.min()), float(arr_ratio.mean()), float(arr_ratio.max())],
        "k_dn_min_mean_max": [float(arr_kdn.min()), float(arr_kdn.mean()), float(arr_kdn.max())],
        "k_ratio_min_mean_max": [float(arr_kr.min()), float(arr_kr.mean()), float(arr_kr.max())],
    }


def main() -> None:
    t0 = time.time()
    print("Building Yukawa tensor and active basis...")
    tensor = build_yukawa_tensor()
    rank, v_active = build_active_basis(tensor)
    print(f"active rank={rank}")

    stage2_files = sorted(glob.glob(str(ROOT / "artifacts" / "w33_breakthrough_stage2_pdg_*.json")))
    stage3_files = sorted(glob.glob(str(ROOT / "artifacts" / "w33_breakthrough_stage3_pdg_*.json")))
    print(f"stage2 files={len(stage2_files)} stage3 files={len(stage3_files)}")

    points: list[dict[str, Any]] = []

    for path in stage2_files + stage3_files:
        p = Path(path)
        data = json.loads(p.read_text(encoding="utf-8"))
        source = "stage2" if "stage2" in p.name else "stage3"
        for run in data.get("all_runs", []):
            m = compute_point_metrics(run["params"], float(run["ckm_err"]), tensor, v_active, rank)
            m["artifact"] = p.name
            m["source"] = source
            m["seed"] = int(run["seed"])
            points.append(m)

    if not points:
        raise RuntimeError("no stage2/stage3 points found")

    # Keep physically tight points and build the Pareto set on that subset.
    tight = [p for p in points if p["ratio_total_err"] <= 1e-2]
    frontier = pareto_front(tight)

    # Scale-ratio branches observed empirically.
    low_ckm = [p for p in tight if p["ckm_err"] <= 0.03]
    branch_a = [p for p in low_ckm if p["k_ratio"] < 43.0]
    branch_b = [p for p in low_ckm if p["k_ratio"] >= 43.0]

    # Useful selections for the report.
    best_ckm_tight = min(tight, key=lambda p: p["ckm_err"])
    best_abs_tight = min(tight, key=lambda p: p["abs_mass_err"])
    hybrid = [p for p in tight if p["abs_mass_err"] <= 1e-4]
    best_ckm_hybrid = min(hybrid, key=lambda p: p["ckm_err"]) if hybrid else None

    report = {
        "timestamp_ms": int(time.time() * 1000),
        "files": {"stage2": [Path(p).name for p in stage2_files], "stage3": [Path(p).name for p in stage3_files]},
        "totals": {
            "all_points": int(len(points)),
            "tight_points": int(len(tight)),
            "pareto_points": int(len(frontier)),
            "low_ckm_points": int(len(low_ckm)),
        },
        "summary_all": summarize(points),
        "summary_tight": summarize(tight),
        "branches_low_ckm_tight": {
            "threshold_k_ratio": 43.0,
            "branch_a_k_ratio_lt_43": summarize(branch_a) if branch_a else {"count": 0},
            "branch_b_k_ratio_ge_43": summarize(branch_b) if branch_b else {"count": 0},
        },
        "best_ckm_tight": best_ckm_tight,
        "best_abs_tight": best_abs_tight,
        "best_ckm_with_abs_le_1e-4": best_ckm_hybrid,
        "pareto_frontier_tight": frontier,
        "elapsed_s": float(time.time() - t0),
    }

    ts = report["timestamp_ms"]
    out_json = ROOT / "artifacts" / f"w33_breakthrough_frontier_report_{ts}.json"
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Compact markdown companion.
    md_lines = [
        f"# W33 Breakthrough Frontier Report ({ts})",
        "",
        f"- Stage-2 files: {len(stage2_files)}",
        f"- Stage-3 files: {len(stage3_files)}",
        f"- Total points: {len(points)}",
        f"- Tight points (ratio_total_err <= 1e-2): {len(tight)}",
        f"- Pareto points (tight set): {len(frontier)}",
        "",
        "## Best Tight Points",
        "",
        f"- Best CKM: `{best_ckm_tight['ckm_err']:.6f}` | abs_err `{best_ckm_tight['abs_mass_err']:.3e}` | "
        f"k_dn `{best_ckm_tight['k_dn']:.4f}` | k_ratio `{best_ckm_tight['k_ratio']:.4f}` | "
        f"{best_ckm_tight['artifact']} seed {best_ckm_tight['seed']}",
        f"- Best absolute mass: `{best_abs_tight['abs_mass_err']:.3e}` | ckm `{best_abs_tight['ckm_err']:.6f}` | "
        f"k_dn `{best_abs_tight['k_dn']:.4f}` | k_ratio `{best_abs_tight['k_ratio']:.4f}` | "
        f"{best_abs_tight['artifact']} seed {best_abs_tight['seed']}",
    ]
    if best_ckm_hybrid is not None:
        md_lines += [
            f"- Best CKM with abs_err <= 1e-4: `{best_ckm_hybrid['ckm_err']:.6f}` | "
            f"abs_err `{best_ckm_hybrid['abs_mass_err']:.3e}` | k_dn `{best_ckm_hybrid['k_dn']:.4f}` | "
            f"k_ratio `{best_ckm_hybrid['k_ratio']:.4f}` | "
            f"{best_ckm_hybrid['artifact']} seed {best_ckm_hybrid['seed']}",
        ]

    md_lines += [
        "",
        "## Branch Statistics (Low-CKM Tight Set)",
        "",
        f"- Branch split threshold: `k_ratio = 43.0`",
        f"- Branch A (`k_ratio < 43`): {len(branch_a)} points",
        f"- Branch B (`k_ratio >= 43`): {len(branch_b)} points",
        "",
        "## Top Pareto Points (first 12)",
        "",
    ]

    for p in frontier[:12]:
        md_lines.append(
            f"- ckm `{p['ckm_err']:.6f}` | abs `{p['abs_mass_err']:.3e}` | rel_rms `{p['rel_rms']:.3e}` | "
            f"k_dn `{p['k_dn']:.4f}` | k_ratio `{p['k_ratio']:.4f}` | {p['artifact']} seed {p['seed']}"
        )

    out_md = ROOT / "artifacts" / f"w33_breakthrough_frontier_report_{ts}.md"
    out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
