#!/usr/bin/env python3
"""Monster selection by *information + structure*: surprisal of signature pairs.

This script treats the class-algebra probabilities from the 2×3 scan as a
probability distribution over order-p classes (Ogg primes).  It then compares:

  - best-by-mass pair (max total probability into order-p classes), vs
  - best-by-structure pair (a pair whose r_p := n/p lands in a cofactor
    permutation degree / irrep degree set).

The emergent pattern is that the "structure" pair can be *much rarer* than the
mass pair (high surprisal), yet it is the one that lands on a recognizable
cofactor action (e.g. 11A: r_11=144 ∈ perm-deg(M12)).

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_monster_surprisal_selection.py
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def _safe_log10(x: float) -> float:
    if x <= 0.0:
        return float("inf")
    return float(math.log10(x))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max-q-exp",
        type=int,
        default=3,
        help="q-exp truncation used in prime replicability checks (pipeline only)",
    )
    args = parser.parse_args()

    from scripts.w33_monster_ogg_pipeline import analyze

    rep = analyze(max_q_exp=int(args.max_q_exp))
    if rep.get("available") is not True:
        raise SystemExit(str(rep.get("reason") or "analysis unavailable"))

    results = rep.get("results", [])
    if not isinstance(results, list):
        raise SystemExit("Unexpected pipeline payload.")

    print("=" * 78)
    print("MONSTER SURPRISAL: best-by-mass vs best-by-structure (perm/irrep hits)")
    print("=" * 78)
    print(f"Primes: {rep.get('scan_primes')}")
    print()

    for rec in results:
        if not isinstance(rec, dict):
            continue

        p = int(rec.get("p", 0) or 0)
        best = str(rec.get("best_pair") or "?")
        perm = rec.get("recommended_pair_perm_hit")
        irrep = rec.get("recommended_pair_nontrivial_irrep_hit")
        masses = rec.get("mass_by_pair", {})
        if not isinstance(masses, dict):
            continue

        m_best = float(masses.get(best, {}).get("float", 0.0) or 0.0)
        m_perm = (
            float(masses.get(str(perm), {}).get("float", 0.0) or 0.0)
            if isinstance(perm, str)
            else 0.0
        )
        m_irrep = (
            float(masses.get(str(irrep), {}).get("float", 0.0) or 0.0)
            if isinstance(irrep, str)
            else 0.0
        )

        ratio_perm = (m_best / m_perm) if (m_best > 0 and m_perm > 0) else float("inf")
        ratio_irrep = (m_best / m_irrep) if (m_best > 0 and m_irrep > 0) else float("inf")

        tag = ""
        if isinstance(perm, str) and perm and perm != best:
            tag = "  <-- structure != mass"

        print(f"p={p:2d}: best={best:6s} mass={m_best:.6g}")
        if isinstance(perm, str) and perm:
            print(
                f"      perm-hit={perm:6s} mass={m_perm:.6g}  ratio={ratio_perm:.3g}  -log10(mass)={- _safe_log10(m_perm):.3g}"
            )
        if isinstance(irrep, str) and irrep and irrep != perm:
            print(
                f"      irrep-hit={irrep:6s} mass={m_irrep:.6g}  ratio={ratio_irrep:.3g}  -log10(mass)={- _safe_log10(m_irrep):.3g}"
            )

        # If cofactor evidence is attached, summarize the first cofactor group.
        cof = rec.get("cofactor_perm_hits", {})
        if isinstance(cof, dict):
            for cls_name, info in cof.items():
                if not isinstance(cls_name, str) or not isinstance(info, dict):
                    continue
                grp = info.get("cofactor_group_recognized")
                if isinstance(grp, str) and grp:
                    print(f"      class {cls_name}: H={grp}")
        print(tag)
        print()


if __name__ == "__main__":
    main()

