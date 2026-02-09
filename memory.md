# MEMORY — Snapshot (2026-02-08)

## Quick summary
- **Pillars added:** 15 (Three Generations), 16 (Universal Mixing).
- **Tests:** 104 computational tests passing (was 96); new test classes `TestThreeGenerations` and `TestUniversalMixing` added.
- **New scripts:** `scripts/w33_three_generations.py`, `scripts/w33_ckm_mixing.py`, `scripts/w33_democratic_mixing.py`.

## Core findings
- E8 Z3 grading (n7 mod 3) gives g = 78 + 81 + 81; sub-grading (n8 mod 3) splits g1(81) into three 27-dim eigenspaces: **81 = 27 + 27 + 27**.
- All **800 order-3 elements** of PSp(4,3) act with character 0 on the 81-dim harmonic space and split it into three 27s (three conjugacy classes: 80, 240, 480 elements).
- Exact projectors for an order-3 generator R:  P_k = (I + ω^{-k} R + ω^{-2k} R²)/3, each Tr(P_k)=27 and P_0+P_1+P_2 = I (up to numerical precision).
- **Universal mixing matrix** between non-commuting generation bases:

  M = (1/81) * [[25, 28, 28], [28, 25, 28], [28, 28, 25]]

  - Doubly stochastic (rows & columns sum to 1), circulant; eigenvalues: **1** and **-1/27**.
- Topological protection: for every vertex v, b0(link(v)) = 4 (link(v) consists of 4 disjoint triangles/lines); triangle regularity λ = 2.
- Spectral geometry: heat kernel K(t) = 81 + 120 e^{-4t} + 24 e^{-10t} + 15 e^{-16t} and spectral zeta ζ(s) = 120·4^{-s} + 24·10^{-s} + 15·16^{-s}.

## Artifacts & housekeeping
- Scripts added: `scripts/w33_three_generations.py`, `scripts/w33_ckm_mixing.py`, `scripts/w33_democratic_mixing.py`.
- Archived **132** transient `_tmp_*` files into `checks/archive/`; archive log: `checks/PART_CVII_repo_cleanup_log_1770596593.json`.
- Commit(s): recent automated registration created canonical `committed_artifacts/PART_CVII_dd_pair_obstruction_*.json` artifacts for reproducible (50,51) and other pairs.

## Next steps
1. Monitor the background full test run and report results; iterate if any failures appear.
2. Finalize README and memory review, then push commits when ready (watcher will refuse to auto-push if `README.md` or `memory.md` are modified in the working tree — we commit both so push is safe after review).
3. Research directions to pursue: Dirac-operator spectrum (mass estimates), explicit SU(5)/GUT embedding tests, Weinberg-angle derivation, and improved CP-SAT heuristics for shrink reproducibility.

---
*Generated automatically by the analysis workflow on 2026-02-08.*
