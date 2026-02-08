#!/usr/bin/env python3
"""Run a campaign of hybrid-SA bijection optimizations and collect the best result.

This script repeatedly invokes the hybrid optimizer (`optimize`) with different
random seeds and parameters, collects per-trial artifacts, and writes a summary
and a best-candidate bijection to `checks/`.

Usage:
    python -X utf8 scripts/run_bijection_campaign.py --trials 6 --time 5 --iters 2000 --alpha 0.7 --beta 0.3

Outputs (in checks/):
    PART_CVII_e8_bijection_campaign_summary_{ts}.json
    PART_CVII_e8_bijection_campaign_best_{ts}.json
    PART_CVII_e8_bijection_trial_{ts}_s{seed}.json   (one per trial)
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from e8_embedding_group_theoretic import build_w33, generate_e8_roots
from optimize_bijection_cocycle import load_bijection, optimize


def run_campaign(
    inpath: Path,
    outdir: Path,
    trials: int = 6,
    time_per: float = 5.0,
    iters: int = 2000,
    alpha: float = 0.7,
    beta: float = 0.3,
    temp: float = 0.01,
    seeds: List[int] | None = None,
    restrict_sector: bool = True,
) -> Dict[str, Any]:
    outdir.mkdir(parents=True, exist_ok=True)

    bij_init, _raw = load_bijection(inpath)

    n, vertices, adj, edges = build_w33()
    roots = generate_e8_roots()

    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    trials_results = []
    best_overall = None

    for i in range(trials):
        seed = seeds[i] if seeds is not None else (int(time.time() * 1e6) % 2**31) + i
        print(
            f"Trial {i+1}/{trials} (seed={seed}): running optimize (time={time_per}s, iters={iters})"
        )
        t0 = time.time()
        res = optimize(
            bij_init,
            edges,
            adj,
            roots,
            iterations=iters,
            time_limit=time_per,
            seed=seed,
            restrict_sector=restrict_sector,
            alpha=alpha,
            beta=beta,
            temp0=temp,
        )
        runtime = time.time() - t0

        trial_obj = {
            "trial": i,
            "seed": seed,
            "runtime_seconds": runtime,
            "best_score": float(res.get("best_score", 0.0)),
            "best_exact": int(res.get("best_exact", 0)),
            "initial_exact": int(res.get("initial_exact", 0)),
            "best_pref_counts": res.get("best_pref_counts", {}),
            "iterations": int(res.get("iterations", 0)),
            "verification": res.get("verification", {}),
        }

        # write per-trial artifact
        trial_path = outdir / f"PART_CVII_e8_bijection_trial_{ts}_s{seed}.json"
        out = {
            "trial": trial_obj,
            "bijection": {str(k): int(v) for k, v in res["best_bij"].items()},
        }
        trial_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(
            f"  Wrote trial artifact: {trial_path} (best_score={trial_obj['best_score']}, best_exact={trial_obj['best_exact']})"
        )

        trials_results.append(trial_obj)

        if best_overall is None or trial_obj["best_score"] > best_overall["best_score"]:
            best_overall = trial_obj.copy()
            best_bij = res["best_bij"].copy()
            best_ver = res.get("verification", {})

    summary = {
        "timestamp": ts,
        "trials": len(trials_results),
        "trials_results": trials_results,
        "best_overall": best_overall,
    }

    # write summary
    summary_path = outdir / f"PART_CVII_e8_bijection_campaign_summary_{ts}.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # write best bijection artifact
    best_path = outdir / f"PART_CVII_e8_bijection_campaign_best_{ts}.json"
    best_out = {
        "bijection": {str(k): int(v) for k, v in best_bij.items()},
        "verification": best_ver,
        "summary_path": str(summary_path),
    }
    best_path.write_text(json.dumps(best_out, indent=2), encoding="utf-8")

    print(
        f"Campaign complete: {summary_path} (best_score={best_overall['best_score']})"
    )
    return {
        "summary": summary,
        "summary_path": str(summary_path),
        "best_path": str(best_path),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--in", dest="inpath", default="checks/PART_CVII_e8_bijection.json"
    )
    parser.add_argument("--outdir", dest="outdir", default="checks")
    parser.add_argument("--trials", type=int, default=6)
    parser.add_argument("--time", type=float, default=5.0)
    parser.add_argument("--iters", type=int, default=2000)
    parser.add_argument("--alpha", type=float, default=0.7)
    parser.add_argument("--beta", type=float, default=0.3)
    parser.add_argument("--temp", type=float, default=0.01)
    parser.add_argument("--seed-start", type=int, default=42)
    parser.add_argument("--no-sector", dest="restrict_sector", action="store_false")
    args = parser.parse_args()

    inpath = Path(args.inpath)
    outdir = Path(args.outdir)
    seeds = [args.seed_start + i for i in range(args.trials)]

    run_campaign(
        inpath=inpath,
        outdir=outdir,
        trials=args.trials,
        time_per=args.time,
        iters=args.iters,
        alpha=args.alpha,
        beta=args.beta,
        temp=args.temp,
        seeds=seeds,
        restrict_sector=args.restrict_sector,
    )


if __name__ == "__main__":
    main()
