# March 2026 Frontier Note

## Scope

This note records the current exact, reproducible frontier of the project. It is deliberately narrower than the full historical site. Claims below are split by evidence level:

- `Verified`: directly reproduced by scripts, artifacts, and targeted tests in this repo.
- `Conjectural`: physics interpretation that fits the verified structure but is not yet a theorem.
- `Historical`: older broad project claims preserved elsewhere in the repo and site archive.

## New synthesis

The strongest repo-native closure is best described as a **finite spectral-exceptional skeleton**, not yet a finished continuum-dynamical TOE. The cleanest reading is a three-shell reading: bare/internal formulas such as `1/4` or `3/8`, dressed/projective formulas such as `3/13`, and global/spectral formulas such as `137 + 40/1111`, `122`, or shell-dependent Euler counts should not be conflated.

## Verified

### Geometry and linear-algebra backbone

The finite geometry layer remains stable:

- `W(3,3)` point graph is `SRG(40,12,2,4)`.
- The collinearity graph has `240` edges and `160` filled triangles.
- The triangle-filled complex has first Betti number `b1 = 81`.
- The `L1` spectrum splits as `0^81 4^120 10^24 16^15`.
- The `E8` `Z3` grading fingerprint is `86 + 81 + 81 = 248`, with the `81` sector matching the `27 x 3` matter split.

These are historical core invariants of the repo and remain part of the live program.

### Exact PMNS cyclotomic route

The exact PMNS formulas currently promoted at verified status are the cyclotomic ones in [PMNS_CYCLOTOMIC.py](./PMNS_CYCLOTOMIC.py):

- `sin^2(theta_12) = (q+1)/Phi_3 = 4/13`
- `sin^2(theta_23) = Phi_6/Phi_3 = 7/13`
- `sin^2(theta_13) = (q-1)/(Phi_3 Phi_6) = 2/91`

with

- `q = 3`
- `lambda = q - 1 = 2`
- `mu = q + 1 = 4`
- `Phi_3(q) = q^2 + q + 1 = 13`
- `Phi_6(q) = q^2 - q + 1 = 7`

The numerators are therefore not arbitrary:

- `4` comes from the SRG/GQ parameter `mu = q + 1`
- `2` comes from the SRG/GQ parameter `lambda = q - 1`
- `7` comes from the cyclotomic partner `Phi_6(3)`

The angle-only Jarlskog magnitude is

- `J_max ~= 0.03336`

but the physical invariant remains phase-dependent:

- `J = J_max sin(delta)`

So `0.03336` should be read as `J_max`, not as a phase-independent prediction for `J`.

### PMNS incidence-theorem derivation (Phase LVI)

The cyclotomic PMNS formulas above now have a direct incidence-geometry derivation from `W(3,3)` (62 tests, T801–T815):

- **Cyclotomic decomposition**: `Phi_3 = mu + Phi_6 + lambda`, i.e., `(q+1) + (q^2-q+1) + (q-1) = q^2+q+1`. This is an algebraic identity for all `q`.
- **Three-sector partition**: At `q=3`, the 13 points of `PG(2,3)` split into collinear (`mu=4`), transversal (`Phi_6=7`), and tangent (`lambda=2`) sectors.
- **Mixing angles as sector ratios**: `sin^2(theta_ij)` is the sector fraction of `PG(2,3)`.
- **Hierarchy mechanism**: `theta_13` is second-order because the tangent sector (`lambda=2`) couples through the transversal, introducing a `1/Phi_6` suppression.
- **Three-flavor sum rule**: `s12 + s23 + s13*Phi_6 = 1`, equivalent to sector completeness. Holds for all `q >= 2`.
- **Cyclotomic tower**: Level-1 denominators = `Phi_3 = 13`, Level-2 = `Phi_3*Phi_6 = 91 = Phi_3(q^2)`.
- **GQ(3,3) spread structure**: 10 disjoint lines of 4 points partition all 40. Spread overlap matrix `R/(q+1)` is doubly stochastic. Line-adjacency within a spread is uniform: `4*(J_10 - I_10)`.
- **Unified mixing picture**: Weinberg angle `sin^2(theta_W) = g/v = 3/8` and PMNS angles are all W(3,3) incidence ratios.

### Exact CE2 / L-infinity frontier

The live algebra frontier is the dual `g1,g2,g2` closure in [scripts/ce2_global_cocycle.py](./scripts/ce2_global_cocycle.py) and [tools/build_linfty_firewall_extension.py](../tools/build_linfty_firewall_extension.py).

Verified in this pass:

- The `a = (0,1,0)` anchor is fully closed.
- The `a = (0,0,1)` anchor is fully closed.
- The dual predictor now cancels the whole `(21,*)` anchor orbit through explicit sparse `1/54` line families and `1/108` overlap families.

The current first unresolved anchor is now:

- `a = (0,0,2)` / basis `(22,*)`

Representative unresolved rows:

- `((22,0),(1,0),(16,1)) -> W = -E_(16,0) / 54`
- `((22,0),(1,1),(23,0)) -> U = -g1(15,2) / 108`, `V = E_(1,2) / 108`
- `((22,0),(4,0),(13,1)) -> W = E_(13,0) / 54`

The certified coefficient hierarchy still looks layered rather than random:

- `1/54`: transport line branch
- `1/108`: overlap / phase branch
- `1/12`: transport-plus-gauge companion
- `1/18`: diagonal / source compensation
- `1/6`: large reflected transport branch

## Reproduce

### PMNS

```powershell
$env:PYTHONUTF8='1'
py -3 .\PMNS_CYCLOTOMIC.py
py -3 -m pytest tests\test_master_derivation.py -k "p20_pmns_theta12 or p21_pmns_theta23 or p22_pmns_theta13" -q
py -3 -m pytest tests\test_tower_generation_rules.py -k "pmns_theta12 or pmns_theta23 or pmns_theta13 or jarlskog_invariant" -q
```

### CE2 / L-infinity

```powershell
py -3 -m py_compile scripts\ce2_global_cocycle.py tests\test_ce2_explanations.py tests\test_ce2_global_predictor_integration.py
py -3 -m pytest tests\test_ce2_explanations.py -k "anchor_001_line_families or anchor_001_overlap_families or dual_" -q
py -3 -m pytest tests\test_ce2_global_predictor_integration.py -k "anchor_001_line_families or anchor_001_overlap_families" -q
```

Focused frontier checks used in this pass:

- `(20,0)`, `(20,1)`, `(20,2)` scan clean
- `(21,0)`, `(21,1)`, `(21,2)` scan clean
- `(22,0)`, `(22,1)`, `(22,2)` still have unresolved witnesses

## Conjectural physics reading

The exact CE2 data continues to look like staged closure:

1. matter transport on affine / Hessian lines
2. gauge compensation on the same orbit slice
3. diagonal or source coherence only after the transport branch is fixed

That is suggestive, but still interpretive. It is not yet a proof that the full physical theory closes in the same way.

Likewise, the SRG formulas for exceptional dimensions and electroweak quantities look real, but the strongest current reading is that they are shadows of a more fundamental Jordan / Freudenthal / TKK / projector mechanism, not standalone proofs by coincidence.

## Not yet proved

- ~~A direct subgroup-chain or incidence-theorem derivation of the PMNS cyclotomic formulas from `W(3,3)` alone.~~
  **Resolved (Phase LVI, T801–T815, 62 tests).** The incidence-theorem derivation is the cyclotomic decomposition identity `Φ₃ = μ + Φ₆ + λ`, which partitions the 13 points of `PG(2,3)` into three natural sectors (collinear `μ=4`, transversal `Φ₆=7`, tangent `λ=2`). The PMNS mixing angles are sector-size ratios: `sin²θ₁₂ = μ/Φ₃ = 4/13`, `sin²θ₂₃ = Φ₆/Φ₃ = 7/13`, `sin²θ₁₃ = λ/(Φ₃·Φ₆) = 2/91`. The `θ₁₃` hierarchy arises from second-order `1/Φ₆` suppression. A three-flavor sum rule `s₁₂ + s₂₃ + s₁₃·Φ₆ = 1` holds for all `q`. Verified via explicit `W(3,3)` construction, spread overlap doubly stochastic matrices, and uniform line-adjacency `4(J₁₀ − I₁₀)`.
- A global closed-form transport law replacing every remaining dual CE2 anchor table.
- A finished theorem that turns the full historical TOE narrative into a single exact construction.
