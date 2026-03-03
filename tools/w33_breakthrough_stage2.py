#!/usr/bin/env python3
"""Stage-2 constrained search for W33 CKM + mass closure.

Focus:
- enforce a CKM ceiling (hard via penalty)
- prioritize down-sector first ratio (m_s/m_b-like channel)
- keep other ratio channels controlled
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

PDG_MASS = {
    "u": 0.00216,
    "d": 0.00470,
    "s": 0.0935,
    "c": 1.2730,
    "b": 4.1830,
    "t": 172.57,
}


def get_targets(name: str) -> tuple[tuple[float, float], tuple[float, float]]:
    if name == "pdg":
        up = (PDG_MASS["c"] / PDG_MASS["t"], PDG_MASS["u"] / PDG_MASS["c"])
        dn = (PDG_MASS["s"] / PDG_MASS["b"], PDG_MASS["d"] / PDG_MASS["s"])
        return up, dn
    if name == "legacy":
        return (1 / 500, 500 / 85000), (1 / 20, 1 / 40)
    raise ValueError(f"unknown targets: {name}")


def build_active_basis(T: np.ndarray) -> tuple[int, np.ndarray]:
    Tm = T.reshape(9, 27)
    _, s, vh = np.linalg.svd(Tm, full_matrices=False)
    rank = int(np.sum(s > 1e-10))
    return rank, vh[:rank, :].conj().T


def koide_q(vals: np.ndarray) -> float:
    x = np.clip(np.asarray(vals, dtype=float), 1e-18, None)
    return float(np.sum(x) / (np.sum(np.sqrt(x)) ** 2))


def unpack_vevs(x: np.ndarray, v_active: np.ndarray, rank: int) -> tuple[np.ndarray, np.ndarray]:
    a1 = x[:rank] + 1j * x[rank : 2 * rank]
    a2 = x[2 * rank : 3 * rank] + 1j * x[3 * rank : 4 * rank]
    v1 = v_active @ a1
    v2 = v_active @ a2
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    if n1 < 1e-14 or n2 < 1e-14:
        raise ValueError("degenerate VEV")
    return v1 / n1, v2 / n2


def diagnostics(
    x: np.ndarray,
    T: np.ndarray,
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
            "ratios_up": (0.0, 0.0),
            "ratios_dn": (0.0, 0.0),
            "ratio_errs": (1e9, 1e9, 1e9, 1e9),
            "koide_up": 0.0,
            "koide_dn": 0.0,
        }

    Yu = yukawa_from_vev(T, v_up)
    Yd = yukawa_from_vev(T, v_dn)
    svu, ru = singular_value_ratios(Yu)
    svd, rd = singular_value_ratios(Yd)
    try:
        V, J = compute_ckm_and_jarlskog(Yu, Yd)
        ckm_err = float(np.linalg.norm(np.abs(V) - V_CKM_EXP, "fro"))
        vabs = np.abs(V)
        jcp = float(np.real(J))
    except Exception:
        ckm_err = 1e9
        vabs = np.zeros((3, 3))
        jcp = 0.0

    e_up1 = float(np.log(ru[0] / up_target[0]) ** 2)
    e_up2 = float(np.log(ru[1] / up_target[1]) ** 2)
    e_dn1 = float(np.log(rd[0] / dn_target[0]) ** 2)
    e_dn2 = float(np.log(rd[1] / dn_target[1]) ** 2)

    return {
        "ok": True,
        "ckm_err": ckm_err,
        "ratios_up": (float(ru[0]), float(ru[1])),
        "ratios_dn": (float(rd[0]), float(rd[1])),
        "ratio_errs": (e_up1, e_up2, e_dn1, e_dn2),
        "sv_up": [float(x) for x in svu.tolist()],
        "sv_dn": [float(x) for x in svd.tolist()],
        "koide_up": koide_q(svu),
        "koide_dn": koide_q(svd),
        "v_ckm_abs": vabs.tolist(),
        "jarlskog": jcp,
    }


def objective(
    x: np.ndarray,
    T: np.ndarray,
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
    koide_weight: float,
    koide_target: float,
) -> float:
    d = diagnostics(x, T, v_active, rank, up_target, dn_target)
    e_up1, e_up2, e_dn1, e_dn2 = d["ratio_errs"]
    mass_obj = w_up1 * e_up1 + w_up2 * e_up2 + w_dn1 * e_dn1 + w_dn2 * e_dn2
    ckm_err = float(d["ckm_err"])
    ckm_cap_pen = ckm_cap_weight * max(0.0, ckm_err - ckm_cap) ** 2
    koide_pen = koide_weight * (float(d["koide_dn"]) - koide_target) ** 2
    return mass_obj + ckm_soft_weight * ckm_err + ckm_cap_pen + koide_pen


def run_once(
    seed: int,
    T: np.ndarray,
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
    koide_weight: float,
    koide_target: float,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    cand = []
    for _ in range(samples):
        x = rng.normal(size=4 * rank)
        score = objective(
            x,
            T,
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
            koide_weight,
            koide_target,
        )
        cand.append((score, x))
    cand.sort(key=lambda t: t[0])

    n_ref = min(len(cand), max(1, refine))
    best_score = float("inf")
    best_x: np.ndarray | None = None
    for i in range(n_ref):
        x0 = cand[i][1]
        res = minimize(
            objective,
            x0,
            args=(
                T,
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
                koide_weight,
                koide_target,
            ),
            method="L-BFGS-B",
            options={"maxiter": 2500, "ftol": 1e-12},
        )
        if res.fun < best_score:
            best_score = float(res.fun)
            best_x = res.x.copy()

    assert best_x is not None
    d = diagnostics(best_x, T, v_active, rank, up_target, dn_target)
    e_up1, e_up2, e_dn1, e_dn2 = d["ratio_errs"]
    result = {
        "seed": int(seed),
        "objective": float(best_score),
        "ckm_err": float(d["ckm_err"]),
        "ratio_errs": {
            "up1": float(e_up1),
            "up2": float(e_up2),
            "dn1": float(e_dn1),
            "dn2": float(e_dn2),
        },
        "ratios_up": [float(d["ratios_up"][0]), float(d["ratios_up"][1])],
        "ratios_dn": [float(d["ratios_dn"][0]), float(d["ratios_dn"][1])],
        "koide_up": float(d["koide_up"]),
        "koide_dn": float(d["koide_dn"]),
        "jarlskog": float(d["jarlskog"]),
        "v_ckm_abs": d["v_ckm_abs"],
        "params": [float(v) for v in best_x.tolist()],
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", choices=["pdg", "legacy"], default="pdg")
    parser.add_argument("--samples", type=int, default=3000)
    parser.add_argument("--refine", type=int, default=16)
    parser.add_argument("--seed-start", type=int, default=11)
    parser.add_argument("--seeds", type=int, default=6, help="number of seeds to scan")
    parser.add_argument("--ckm-cap", type=float, default=0.08)
    parser.add_argument("--ckm-cap-weight", type=float, default=1200.0)
    parser.add_argument("--ckm-soft-weight", type=float, default=0.25)
    parser.add_argument("--w-up1", type=float, default=0.8)
    parser.add_argument("--w-up2", type=float, default=0.8)
    parser.add_argument("--w-dn1", type=float, default=3.5, help="focus channel")
    parser.add_argument("--w-dn2", type=float, default=1.0)
    parser.add_argument("--koide-weight", type=float, default=0.0)
    parser.add_argument("--koide-target", type=float, default=2.0 / 3.0)
    args = parser.parse_args()

    t0 = time.time()
    print("=" * 76)
    print("W33 STAGE-2 BREAKTHROUGH SEARCH (CKM-CAPPED, DOWN1-FOCUSED)")
    print("=" * 76)
    print(
        f"targets={args.targets} samples={args.samples} refine={args.refine} "
        f"ckm_cap={args.ckm_cap} seeds={args.seeds} seed_start={args.seed_start}"
    )

    up_target, dn_target = get_targets(args.targets)
    print(f"up target={up_target}")
    print(f"dn target={dn_target}")

    print("\nBuilding tensor and active subspace...")
    T = build_yukawa_tensor()
    rank, v_active = build_active_basis(T)
    print(f"active rank={rank}")

    runs = []
    for k in range(args.seeds):
        seed = args.seed_start + 2 * k
        r = run_once(
            seed,
            T,
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
            args.koide_weight,
            args.koide_target,
        )
        runs.append(r)
        print(
            f"seed={seed} obj={r['objective']:.6f} ckm={r['ckm_err']:.6f} "
            f"dn1={r['ratios_dn'][0]:.6f} dn2={r['ratios_dn'][1]:.6f}"
        )

    # choose best feasible by ckm cap first, then objective
    feasible = [r for r in runs if r["ckm_err"] <= args.ckm_cap]
    if feasible:
        best = min(feasible, key=lambda r: r["objective"])
        feasible_count = len(feasible)
        mode = "best_feasible"
    else:
        best = min(runs, key=lambda r: r["objective"])
        feasible_count = 0
        mode = "best_overall_no_feasible"

    print("\nSelected candidate:")
    print(f"mode={mode}, feasible_count={feasible_count}/{len(runs)}")
    print(f"objective={best['objective']:.6f}")
    print(f"ckm_err={best['ckm_err']:.6f}")
    print(f"up_ratios={tuple(best['ratios_up'])}")
    print(f"dn_ratios={tuple(best['ratios_dn'])}")
    print(f"koide(up/down)=({best['koide_up']:.6f}, {best['koide_dn']:.6f})")

    ts_ms = int(time.time() * 1000)
    out = {
        "timestamp_ms": ts_ms,
        "targets": args.targets,
        "target_ratios": {"up": [float(up_target[0]), float(up_target[1])], "down": [float(dn_target[0]), float(dn_target[1])]},
        "settings": {
            "samples": int(args.samples),
            "refine": int(args.refine),
            "seed_start": int(args.seed_start),
            "seeds": int(args.seeds),
            "ckm_cap": float(args.ckm_cap),
            "ckm_cap_weight": float(args.ckm_cap_weight),
            "ckm_soft_weight": float(args.ckm_soft_weight),
            "weights": {
                "up1": float(args.w_up1),
                "up2": float(args.w_up2),
                "dn1": float(args.w_dn1),
                "dn2": float(args.w_dn2),
            },
            "koide_weight": float(args.koide_weight),
            "koide_target": float(args.koide_target),
            "active_rank": int(rank),
        },
        "selection_mode": mode,
        "feasible_count": int(feasible_count),
        "all_runs": runs,
        "best": best,
        "elapsed_s": float(time.time() - t0),
    }
    out_path = ROOT / "artifacts" / f"w33_breakthrough_stage2_{args.targets}_{ts_ms}.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
