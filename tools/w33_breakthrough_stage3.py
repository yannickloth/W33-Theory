#!/usr/bin/env python3
"""Stage-3 constrained search for CKM + ratio + absolute-mass closure.

This extends stage-2 by adding:
1. Absolute PDG mass matching (up/down) with analytic best-fit scales.
2. Optional integer-structure priors on the fitted scales:
   - k_dn ~ 45
   - k_up / k_dn ~ target (e.g., 40 or 45)
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import minimize

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from w33_ckm_from_vev import compute_ckm_and_jarlskog
from yukawa_mass_ratio_analysis import build_yukawa_tensor, singular_value_ratios, yukawa_from_vev

V_CKM_EXP = np.array(
    [
        [0.97373, 0.2243, 0.00382],
        [0.2210, 0.9870, 0.0410],
        [0.0080, 0.0388, 1.0130],
    ],
    dtype=float,
)

# PDG central values in GeV.
PDG_UP = np.array([0.00216, 1.2730, 172.57], dtype=float)  # u, c, t
PDG_DN = np.array([0.00470, 0.0935, 4.1830], dtype=float)  # d, s, b


def get_ratio_targets(name: str) -> tuple[tuple[float, float], tuple[float, float]]:
    if name == "pdg":
        up = (PDG_UP[1] / PDG_UP[2], PDG_UP[0] / PDG_UP[1])
        dn = (PDG_DN[1] / PDG_DN[2], PDG_DN[0] / PDG_DN[1])
        return up, dn
    if name == "legacy":
        return (1.0 / 500.0, 500.0 / 85000.0), (1.0 / 20.0, 1.0 / 40.0)
    raise ValueError(f"unknown targets: {name}")


def build_active_basis(tensor: np.ndarray) -> tuple[int, np.ndarray]:
    t_mat = tensor.reshape(9, 27)
    _, svals, vh = np.linalg.svd(t_mat, full_matrices=False)
    rank = int(np.sum(svals > 1e-10))
    return rank, vh[:rank, :].conj().T


def unpack_vevs(x: np.ndarray, v_active: np.ndarray, rank: int) -> tuple[np.ndarray, np.ndarray]:
    a_up = x[:rank] + 1j * x[rank : 2 * rank]
    a_dn = x[2 * rank : 3 * rank] + 1j * x[3 * rank : 4 * rank]
    v_up = v_active @ a_up
    v_dn = v_active @ a_dn
    n_up = np.linalg.norm(v_up)
    n_dn = np.linalg.norm(v_dn)
    if n_up < 1e-14 or n_dn < 1e-14:
        raise ValueError("degenerate VEV")
    return v_up / n_up, v_dn / n_dn


def koide_q(vals: np.ndarray) -> float:
    x = np.clip(np.asarray(vals, dtype=float), 1e-18, None)
    return float(np.sum(x) / (np.sum(np.sqrt(x)) ** 2))


def fit_scale(model_vals: np.ndarray, target_vals: np.ndarray) -> float:
    num = float(np.dot(model_vals, target_vals))
    den = float(np.dot(model_vals, model_vals))
    if den <= 1e-18:
        return 0.0
    return num / den


def diagnostics(
    x: np.ndarray,
    tensor: np.ndarray,
    v_active: np.ndarray,
    rank: int,
    up_target: tuple[float, float],
    dn_target: tuple[float, float],
) -> dict[str, Any]:
    try:
        v_up, v_dn = unpack_vevs(x, v_active, rank)
    except ValueError:
        return {
            "ok": False,
            "ckm_err": 1e9,
            "ratio_errs": (1e9, 1e9, 1e9, 1e9),
            "abs_mass_err": 1e9,
            "k_up": 0.0,
            "k_dn": 0.0,
            "k_ratio": 0.0,
            "koide_up": 0.0,
            "koide_dn": 0.0,
        }

    y_up = yukawa_from_vev(tensor, v_up)
    y_dn = yukawa_from_vev(tensor, v_dn)
    sv_up, r_up = singular_value_ratios(y_up)
    sv_dn, r_dn = singular_value_ratios(y_dn)

    try:
        v_ckm, jcp = compute_ckm_and_jarlskog(y_up, y_dn)
        ckm_err = float(np.linalg.norm(np.abs(v_ckm) - V_CKM_EXP, "fro"))
        v_abs = np.abs(v_ckm)
        jarlskog = float(np.real(jcp))
    except Exception:
        ckm_err = 1e9
        v_abs = np.zeros((3, 3), dtype=float)
        jarlskog = 0.0

    e_up1 = float(np.log(r_up[0] / up_target[0]) ** 2)
    e_up2 = float(np.log(r_up[1] / up_target[1]) ** 2)
    e_dn1 = float(np.log(r_dn[0] / dn_target[0]) ** 2)
    e_dn2 = float(np.log(r_dn[1] / dn_target[1]) ** 2)

    # Convert descending singular values [heavy, mid, light] to [light, mid, heavy].
    m_up_model = np.array([sv_up[2], sv_up[1], sv_up[0]], dtype=float)
    m_dn_model = np.array([sv_dn[2], sv_dn[1], sv_dn[0]], dtype=float)

    k_up = fit_scale(m_up_model, PDG_UP)
    k_dn = fit_scale(m_dn_model, PDG_DN)
    pred_up = k_up * m_up_model
    pred_dn = k_dn * m_dn_model

    # Log-space absolute mass error is scale-robust and aligns with hierarchy use.
    abs_up_err = float(np.sum(np.log(np.clip(pred_up, 1e-18, None) / PDG_UP) ** 2))
    abs_dn_err = float(np.sum(np.log(np.clip(pred_dn, 1e-18, None) / PDG_DN) ** 2))
    abs_mass_err = abs_up_err + abs_dn_err

    rel_up = np.abs(pred_up - PDG_UP) / PDG_UP
    rel_dn = np.abs(pred_dn - PDG_DN) / PDG_DN
    rel_rms = float(np.sqrt(np.mean(np.concatenate([rel_up, rel_dn]) ** 2)))

    k_ratio = float(k_up / k_dn) if k_dn > 1e-18 else 0.0

    return {
        "ok": True,
        "ckm_err": ckm_err,
        "ratio_errs": (e_up1, e_up2, e_dn1, e_dn2),
        "ratios_up": (float(r_up[0]), float(r_up[1])),
        "ratios_dn": (float(r_dn[0]), float(r_dn[1])),
        "sv_up": [float(x) for x in sv_up.tolist()],
        "sv_dn": [float(x) for x in sv_dn.tolist()],
        "koide_up": koide_q(sv_up),
        "koide_dn": koide_q(sv_dn),
        "k_up": float(k_up),
        "k_dn": float(k_dn),
        "k_ratio": k_ratio,
        "pred_masses_up": [float(x) for x in pred_up.tolist()],
        "pred_masses_dn": [float(x) for x in pred_dn.tolist()],
        "rel_errors_up": [float(x) for x in rel_up.tolist()],
        "rel_errors_dn": [float(x) for x in rel_dn.tolist()],
        "rel_rms": rel_rms,
        "abs_mass_err": float(abs_mass_err),
        "v_ckm_abs": v_abs.tolist(),
        "jarlskog": jarlskog,
    }


def objective(
    x: np.ndarray,
    tensor: np.ndarray,
    v_active: np.ndarray,
    rank: int,
    up_target: tuple[float, float],
    dn_target: tuple[float, float],
    ckm_cap: float,
    ckm_cap_weight: float,
    ckm_soft_weight: float,
    w_up1: float,
    w_up2: float,
    w_dn1: float,
    w_dn2: float,
    abs_weight: float,
    koide_weight: float,
    koide_target: float,
    k_dn_target: float,
    k_dn_prior_weight: float,
    k_ratio_target: float,
    k_ratio_prior_weight: float,
) -> float:
    d = diagnostics(x, tensor, v_active, rank, up_target, dn_target)

    e_up1, e_up2, e_dn1, e_dn2 = d["ratio_errs"]
    ratio_obj = w_up1 * e_up1 + w_up2 * e_up2 + w_dn1 * e_dn1 + w_dn2 * e_dn2
    ckm_err = float(d["ckm_err"])
    abs_obj = abs_weight * float(d["abs_mass_err"])

    ckm_cap_pen = ckm_cap_weight * max(0.0, ckm_err - ckm_cap) ** 2
    koide_pen = koide_weight * (float(d["koide_dn"]) - koide_target) ** 2

    k_dn_pen = 0.0
    if k_dn_prior_weight > 0.0:
        k_dn_pen = k_dn_prior_weight * (float(d["k_dn"]) - k_dn_target) ** 2

    k_ratio_pen = 0.0
    if k_ratio_prior_weight > 0.0:
        k_ratio_pen = k_ratio_prior_weight * (float(d["k_ratio"]) - k_ratio_target) ** 2

    return ratio_obj + abs_obj + ckm_soft_weight * ckm_err + ckm_cap_pen + koide_pen + k_dn_pen + k_ratio_pen


def run_once(
    seed: int,
    tensor: np.ndarray,
    v_active: np.ndarray,
    rank: int,
    up_target: tuple[float, float],
    dn_target: tuple[float, float],
    samples: int,
    refine: int,
    ckm_cap: float,
    ckm_cap_weight: float,
    ckm_soft_weight: float,
    w_up1: float,
    w_up2: float,
    w_dn1: float,
    w_dn2: float,
    abs_weight: float,
    koide_weight: float,
    koide_target: float,
    k_dn_target: float,
    k_dn_prior_weight: float,
    k_ratio_target: float,
    k_ratio_prior_weight: float,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    candidates = []
    for _ in range(samples):
        x = rng.normal(size=4 * rank)
        score = objective(
            x,
            tensor,
            v_active,
            rank,
            up_target,
            dn_target,
            ckm_cap,
            ckm_cap_weight,
            ckm_soft_weight,
            w_up1,
            w_up2,
            w_dn1,
            w_dn2,
            abs_weight,
            koide_weight,
            koide_target,
            k_dn_target,
            k_dn_prior_weight,
            k_ratio_target,
            k_ratio_prior_weight,
        )
        candidates.append((score, x))
    candidates.sort(key=lambda t: t[0])

    n_ref = min(len(candidates), max(1, refine))
    best_score = float("inf")
    best_x: np.ndarray | None = None

    for i in range(n_ref):
        x0 = candidates[i][1]
        res = minimize(
            objective,
            x0,
            args=(
                tensor,
                v_active,
                rank,
                up_target,
                dn_target,
                ckm_cap,
                ckm_cap_weight,
                ckm_soft_weight,
                w_up1,
                w_up2,
                w_dn1,
                w_dn2,
                abs_weight,
                koide_weight,
                koide_target,
                k_dn_target,
                k_dn_prior_weight,
                k_ratio_target,
                k_ratio_prior_weight,
            ),
            method="L-BFGS-B",
            options={"maxiter": 3000, "ftol": 1e-12},
        )
        if res.fun < best_score:
            best_score = float(res.fun)
            best_x = res.x.copy()

    assert best_x is not None
    d = diagnostics(best_x, tensor, v_active, rank, up_target, dn_target)
    e_up1, e_up2, e_dn1, e_dn2 = d["ratio_errs"]

    return {
        "seed": int(seed),
        "objective": float(best_score),
        "ckm_err": float(d["ckm_err"]),
        "abs_mass_err": float(d["abs_mass_err"]),
        "rel_rms": float(d["rel_rms"]),
        "ratio_errs": {
            "up1": float(e_up1),
            "up2": float(e_up2),
            "dn1": float(e_dn1),
            "dn2": float(e_dn2),
        },
        "ratios_up": [float(d["ratios_up"][0]), float(d["ratios_up"][1])],
        "ratios_dn": [float(d["ratios_dn"][0]), float(d["ratios_dn"][1])],
        "k_up": float(d["k_up"]),
        "k_dn": float(d["k_dn"]),
        "k_ratio": float(d["k_ratio"]),
        "pred_masses_up": d["pred_masses_up"],
        "pred_masses_dn": d["pred_masses_dn"],
        "rel_errors_up": d["rel_errors_up"],
        "rel_errors_dn": d["rel_errors_dn"],
        "koide_up": float(d["koide_up"]),
        "koide_dn": float(d["koide_dn"]),
        "jarlskog": float(d["jarlskog"]),
        "v_ckm_abs": d["v_ckm_abs"],
        "params": [float(v) for v in best_x.tolist()],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", choices=["pdg", "legacy"], default="pdg")
    parser.add_argument("--samples", type=int, default=2400)
    parser.add_argument("--refine", type=int, default=12)
    parser.add_argument("--seed-start", type=int, default=31)
    parser.add_argument("--seeds", type=int, default=10)
    parser.add_argument("--ckm-cap", type=float, default=0.03)
    parser.add_argument("--ckm-cap-weight", type=float, default=2400.0)
    parser.add_argument("--ckm-soft-weight", type=float, default=0.12)
    parser.add_argument("--w-up1", type=float, default=0.8)
    parser.add_argument("--w-up2", type=float, default=0.8)
    parser.add_argument("--w-dn1", type=float, default=4.2)
    parser.add_argument("--w-dn2", type=float, default=1.0)
    parser.add_argument("--abs-weight", type=float, default=1.0)
    parser.add_argument("--koide-weight", type=float, default=0.0)
    parser.add_argument("--koide-target", type=float, default=2.0 / 3.0)
    parser.add_argument("--k-dn-target", type=float, default=45.0)
    parser.add_argument("--k-dn-prior-weight", type=float, default=0.0)
    parser.add_argument("--k-ratio-target", type=float, default=40.0)
    parser.add_argument("--k-ratio-prior-weight", type=float, default=0.0)
    args = parser.parse_args()

    t0 = time.time()
    print("=" * 78)
    print("W33 STAGE-3 BREAKTHROUGH SEARCH (CKM + RATIO + ABS MASS + SCALE PRIORS)")
    print("=" * 78)
    print(
        f"targets={args.targets} samples={args.samples} refine={args.refine} "
        f"seeds={args.seeds} seed_start={args.seed_start} ckm_cap={args.ckm_cap}"
    )
    print(
        f"weights: ratio(up1,up2,dn1,dn2)=({args.w_up1},{args.w_up2},{args.w_dn1},{args.w_dn2}) "
        f"abs={args.abs_weight} ckm_soft={args.ckm_soft_weight}"
    )
    print(
        f"scale priors: k_dn~{args.k_dn_target} (w={args.k_dn_prior_weight}), "
        f"k_ratio~{args.k_ratio_target} (w={args.k_ratio_prior_weight})"
    )

    up_target, dn_target = get_ratio_targets(args.targets)
    print(f"ratio targets up={up_target} down={dn_target}")

    print("\nBuilding tensor and active basis...")
    tensor = build_yukawa_tensor()
    rank, v_active = build_active_basis(tensor)
    print(f"active rank={rank}")

    runs: list[dict[str, Any]] = []
    for k in range(args.seeds):
        seed = args.seed_start + 2 * k
        out = run_once(
            seed,
            tensor,
            v_active,
            rank,
            up_target,
            dn_target,
            args.samples,
            args.refine,
            args.ckm_cap,
            args.ckm_cap_weight,
            args.ckm_soft_weight,
            args.w_up1,
            args.w_up2,
            args.w_dn1,
            args.w_dn2,
            args.abs_weight,
            args.koide_weight,
            args.koide_target,
            args.k_dn_target,
            args.k_dn_prior_weight,
            args.k_ratio_target,
            args.k_ratio_prior_weight,
        )
        runs.append(out)
        print(
            f"seed={seed} obj={out['objective']:.6f} ckm={out['ckm_err']:.6f} "
            f"abs={out['abs_mass_err']:.6e} rel_rms={out['rel_rms']:.6e} "
            f"k_dn={out['k_dn']:.4f} k_ratio={out['k_ratio']:.4f}"
        )

    feasible = [r for r in runs if r["ckm_err"] <= args.ckm_cap]
    if feasible:
        best = min(feasible, key=lambda r: r["objective"])
        selection_mode = "best_feasible"
    else:
        best = min(runs, key=lambda r: r["objective"])
        selection_mode = "best_overall_no_feasible"

    print("\nSelected candidate:")
    print(f"mode={selection_mode} feasible={len(feasible)}/{len(runs)}")
    print(
        f"objective={best['objective']:.6f} ckm={best['ckm_err']:.6f} "
        f"abs_mass_err={best['abs_mass_err']:.6e} rel_rms={best['rel_rms']:.6e}"
    )
    print(
        f"k_up={best['k_up']:.6f} k_dn={best['k_dn']:.6f} "
        f"k_ratio={best['k_ratio']:.6f}"
    )
    print(f"up_ratios={tuple(best['ratios_up'])}")
    print(f"dn_ratios={tuple(best['ratios_dn'])}")

    ts_ms = int(time.time() * 1000)
    out = {
        "timestamp_ms": ts_ms,
        "targets": args.targets,
        "ratio_targets": {"up": [float(up_target[0]), float(up_target[1])], "down": [float(dn_target[0]), float(dn_target[1])]},
        "pdg_mass_targets_gev": {"up": PDG_UP.tolist(), "down": PDG_DN.tolist()},
        "settings": {
            "samples": int(args.samples),
            "refine": int(args.refine),
            "seed_start": int(args.seed_start),
            "seeds": int(args.seeds),
            "ckm_cap": float(args.ckm_cap),
            "ckm_cap_weight": float(args.ckm_cap_weight),
            "ckm_soft_weight": float(args.ckm_soft_weight),
            "ratio_weights": {
                "up1": float(args.w_up1),
                "up2": float(args.w_up2),
                "dn1": float(args.w_dn1),
                "dn2": float(args.w_dn2),
            },
            "abs_weight": float(args.abs_weight),
            "koide_weight": float(args.koide_weight),
            "koide_target": float(args.koide_target),
            "k_dn_target": float(args.k_dn_target),
            "k_dn_prior_weight": float(args.k_dn_prior_weight),
            "k_ratio_target": float(args.k_ratio_target),
            "k_ratio_prior_weight": float(args.k_ratio_prior_weight),
            "active_rank": int(rank),
        },
        "selection_mode": selection_mode,
        "feasible_count": int(len(feasible)),
        "all_runs": runs,
        "best": best,
        "elapsed_s": float(time.time() - t0),
    }

    ratio_tag = str(args.k_ratio_target).replace(".", "p")
    w_ratio_tag = str(args.k_ratio_prior_weight).replace(".", "p")
    w_dn_tag = str(args.k_dn_prior_weight).replace(".", "p")
    out_path = (
        ROOT
        / "artifacts"
        / f"w33_breakthrough_stage3_{args.targets}_rt{ratio_tag}_wr{w_ratio_tag}_wd{w_dn_tag}_{ts_ms}.json"
    )
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
