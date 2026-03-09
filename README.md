# W(3,3)-E8 Research Program

[![Tests](https://github.com/wilcompute/W33-Theory/actions/workflows/ci.yml/badge.svg)](https://github.com/wilcompute/W33-Theory/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Pages](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://wilcompute.github.io/W33-Theory/)

This repo studies whether the finite symplectic geometry `W(3,3)` and its `E6/E8` structures support an exact algebraic route toward Standard Model data. The live program is narrower than the historical site narrative: the current source of truth is the exact geometry, the exact PMNS cyclotomic formulas, and the CE2 / `L_infinity` closure machinery.

- Live paper: [GitHub Pages](https://wilcompute.github.io/W33-Theory/)
- Frontier note: [docs/march_2026_frontier_note.md](docs/march_2026_frontier_note.md)
- Colleague email memo: [docs/pmns_colleague_email.md](docs/pmns_colleague_email.md)

## Verified Frontier

- `W(3,3)` point graph remains `SRG(40,12,2,4)` with `240` edges and `160` filled triangles.
- The triangle-filled complex has `b1 = 81`, and the `L1` spectrum remains `0^81 4^120 10^24 16^15`.
- The `E8` `Z3` grading fingerprint remains `86 + 81 + 81 = 248`, with `81 = 27 x 3`.
- The exact PMNS cyclotomic route in [PMNS_CYCLOTOMIC.py](PMNS_CYCLOTOMIC.py) is the only PMNS formula layer currently promoted at verified status:
  - `sin^2(theta_12) = 4/13`
  - `sin^2(theta_23) = 7/13`
  - `sin^2(theta_13) = 2/91`
- The correct Jarlskog wording is:
  - `J_max ~= 0.03336` from the angles alone
  - `J = J_max sin(delta)` for the physical invariant
- The live algebra frontier is the dual `g1,g2,g2` CE2 / `L_infinity` closure in [scripts/ce2_global_cocycle.py](scripts/ce2_global_cocycle.py) and [tools/build_linfty_firewall_extension.py](tools/build_linfty_firewall_extension.py).
- In this pass the predictor now closes:
  - the full `a = (0,1,0)` anchor
  - the full `a = (0,0,1)` anchor
- The current first unresolved anchor is now `a = (0,0,2)` / basis `(22,*)`.
- Representative live witnesses on that anchor are:
  - `((22,0),(1,0),(16,1)) -> W = -E_(16,0) / 54`
  - `((22,0),(1,1),(23,0)) -> U = -g1(15,2) / 108`, `V = E_(1,2) / 108`

## Physics Interpretation (Conjectural)

- The CE2 data still looks staged rather than random: transport terms first, then gauge companions, then diagonal/source coherence.
- The SRG formulas for exceptional dimensions and electroweak quantities may be shadows of a deeper Jordan / Freudenthal / TKK / projector mechanism.
- None of that is yet a finished proof of a full physical theory. The exact closure program remains the primary frontier.

## Historical Archive

The repo and Pages site preserve older broad claims, pillar catalogs, and speculative bridges. They remain useful context, but they are not all promoted at the same evidence level as the exact frontier above. Historical PMNS approximations and numerical optimization tracks are preserved as archive material, not as the primary exact derivation.

## Reproduce

Install the core Python dependencies:

```powershell
pip install numpy sympy networkx pytest
```

Run the exact PMNS path:

```powershell
$env:PYTHONUTF8='1'
py -3 .\PMNS_CYCLOTOMIC.py
py -3 -m pytest tests\test_master_derivation.py -k "p20_pmns_theta12 or p21_pmns_theta23 or p22_pmns_theta13" -q
py -3 -m pytest tests\test_tower_generation_rules.py -k "pmns_theta12 or pmns_theta23 or pmns_theta13 or jarlskog_invariant" -q
```

Run the current CE2 frontier checks:

```powershell
py -3 -m py_compile scripts\ce2_global_cocycle.py tests\test_ce2_explanations.py tests\test_ce2_global_predictor_integration.py
py -3 -m pytest tests\test_ce2_explanations.py -k "anchor_001_line_families or anchor_001_overlap_families or dual_" -q
py -3 -m pytest tests\test_ce2_global_predictor_integration.py -k "anchor_001_line_families or anchor_001_overlap_families" -q
```

Publish the Pages site from the HTML source:

```powershell
py -3 docs\build_site.py
```

## Repository Layout

```text
W33-Theory/
|- scripts/   core symbolic and computational derivations
|- tools/     geometry and L_infinity utilities
|- tests/     targeted and regression checks
|- artifacts/ generated exact data and exported bases
|- docs/      Pages source, notes, and colleague-facing material
|- archive/   historical artifacts and older project material
```
