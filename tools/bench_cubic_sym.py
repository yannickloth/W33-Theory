from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np


def _measure(func, args=(), warmup=10, iters=100):
    for _ in range(warmup):
        func(*args)
    t0 = time.perf_counter()
    for _ in range(iters):
        func(*args)
    t1 = time.perf_counter()
    return (t1 - t0) / iters


def main():
    parser = argparse.ArgumentParser(description="Benchmark cubic_sym variants")
    parser.add_argument("--iters", type=int, default=200)
    parser.add_argument("--warmup", type=int, default=10)
    parser.add_argument(
        "--mode", choices=("all", "numpy", "fast", "numba"), default="all"
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    tool = __import__("tools.toe_e8_z3graded_bracket_jacobi", fromlist=["*"])

    basis_path = repo_root / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    if not basis_path.exists():
        raise SystemExit(
            "Missing E6 basis export; run build_e6_27rep_minuscule.py --export-basis78"
        )
    e6_basis = np.load(basis_path).astype(np.complex128)

    triads = tool._load_signed_cubic_triads()
    proj = tool.E6Projector(e6_basis)

    rng = np.random.default_rng(args.seed)
    u = (rng.standard_normal(27) + 1j * rng.standard_normal(27)).astype(np.complex128)
    v = (rng.standard_normal(27) + 1j * rng.standard_normal(27)).astype(np.complex128)

    results = {}

    if args.mode in ("all", "numpy"):
        br = tool.E8Z3Bracket(e6_projector=proj, cubic_triads=triads, use_numba=False)
        t = _measure(
            lambda: br.cubic_sym(u, v, scale=1.0), warmup=args.warmup, iters=args.iters
        )
        results["numpy"] = t
        print(f"numpy (np.add.at) : {t*1e6:.2f} µs / call")

    if args.mode in ("all", "fast"):
        br_fast = tool.E8Z3Bracket(
            e6_projector=proj, cubic_triads=triads, use_numba=False
        )
        # enable fast-numpy via env var for reproducibility
        import os

        os.environ["TOE_USE_FAST_CUBIC_SYM"] = "1"
        br_fast._use_fast_numpy = True
        t = _measure(
            lambda: br_fast.cubic_sym(u, v, scale=1.0),
            warmup=args.warmup,
            iters=args.iters,
        )
        results["fast_numpy"] = t
        print(f"fast numpy (bincount) : {t*1e6:.2f} µs / call")

    if args.mode in ("all", "numba"):
        try:
            import numba  # type: ignore

            br_numba = tool.E8Z3Bracket(
                e6_projector=proj, cubic_triads=triads, use_numba=True
            )
            # first call to compile
            br_numba.cubic_sym(u, v, scale=1.0)
            t = _measure(
                lambda: br_numba.cubic_sym(u, v, scale=1.0),
                warmup=args.warmup,
                iters=args.iters,
            )
            results["numba"] = t
            print(f"numba (njit loop) : {t*1e6:.2f} µs / call")
        except Exception:
            print("numba not available; skipping numba benchmark")

    if "numpy" in results and "numba" in results:
        print(f"speedup (numba / numpy) = {results['numpy'] / results['numba']:.2f}x")

    if "fast_numpy" in results and "numba" in results:
        print(
            f"speedup (numba / fast_numpy) = {results['fast_numpy'] / results['numba']:.2f}x"
        )


if __name__ == "__main__":
    main()
