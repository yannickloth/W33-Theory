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
- The first `a = (0,0,2)` witness package is now promoted into the dual predictor:
  - `((22,0),(1,0),(16,1)) -> W = -E_(16,0) / 54`
  - `((22,0),(1,1),(16,0)) -> V = -E_(1,0) / 54`
  - `((22,0),(1,1),(23,0)) -> U = -g1(15,2) / 108`, `V = E_(1,2) / 108`
  - `((22,0),(1,2),(23,0)) -> U = g1(15,1) / 108`, `V = E_(1,2) / 108`
  - `((22,0),(4,0),(13,1)) -> W = E_(13,0) / 54`

The current first unresolved anchor is now:

- `a = (0,0,2)` / basis `(22,*)`

Representative rows already promoted from that anchor:

- `((22,0),(1,0),(16,1)) -> W = -E_(16,0) / 54`
- `((22,0),(1,1),(23,0)) -> U = -g1(15,2) / 108`, `V = E_(1,2) / 108`
- `((22,0),(4,0),(13,1)) -> W = E_(13,0) / 54`

Remaining uncovered rows still begin on that same `a = (0,0,2)` anchor; this is a genuine narrowing, not full closure.

The certified coefficient hierarchy still looks layered rather than random:

- `1/54`: transport line branch
- `1/108`: overlap / phase branch
- `1/12`: transport-plus-gauge companion
- `1/18`: diagonal / source compensation
- `1/6`: large reflected transport branch

### Exact Yukawa nonlinear frontier

The Yukawa frontier is now compressed further than “one unknown last packet”:

- On the replicated diagonal `l6` seed, the exact bottleneck is `response rank = 9`, `augmented rank = 10`.
- Inside the native unit `A2` mixed-seed family, the minimal exact rank-lift seeds are `[8,246]`, `[8,247]`, `[9,246]`, `[9,247]`; these raise the ranks to `11` and `12`.
- The minimal full-activation seeds are the two fans `[8,9]` and `[246,247]`; one exact nonlinear closure step turns each fan into a full `3x3`-support mixed seed with a slotwise isotropic off-diagonal shell.
- After the exact `V4`, unipotent, Kronecker, and Gram reductions, the remaining nontrivial packet is already a finite `240^2`-shell problem: exact scalar channels `169`, `275`, `323`, plus residual blocks `[[367,-55],[-55,175]]` and `[[323,275],[275,659]]`.
- Equivalently, the unresolved base spectrum is exactly two radical pairs with trace/determinant data `(542, 61200)` and `(982, 137232)`.

The strongest conservative read is therefore:

- the remaining Yukawa packet is not currently a missing linear `l6` mode;
- it is the remaining nonlinear internal spectral data carried by those reduced blocks.

### Exact Yukawa generation flag

The reduced generation algebra now has a cleaner exact finite structure too:

- The two universal generation matrices have nilpotent parts of rank `2`, share the same rank-`1` square, and satisfy `N^3 = 0`.
- That common square defines a shared exact flag in `C^3`:
  - line `L = span(1,1,0)`
  - plane `P = {x = y} = span((1,1,0),(0,0,1))`
- Both universal generation matrices preserve that line and that plane exactly.

So the repo-native finite side already carries a common `1 ⊂ 2 ⊂ 3` flag before any continuum family model is chosen.

### Exact finite family normal form

The exact family packet is now sharper than just “there is a flag”:

- The six ordered `l6` generation-transfer modes are the complete oriented three-generation graph.
- On the replicated seed, the active quartet is exactly the star at generation `2`:
  - `[0,2]`, `[2,0]`, `[1,2]`, `[2,1]`
- The dormant pair is the opposite bidirectional edge:
  - `[0,1]`, `[1,0]`
- In the exact basis
  - `u = (1,1,0)`
  - `v = (0,0,1)`
  - `w = (1,-1,0)`
  the two universal generation matrices become
  - `C_(+-) = [[1,1,-2],[0,1,2],[0,0,1]]`
  - `C_(-+) = [[1,-1,-2],[0,1,-2],[0,0,1]]`
- Their nilpotent parts have the same nonzero square:
  - `N_(+-)^2 = N_(-+)^2 = 2 E_13`

So the current exact family/Yukawa packet already has a canonical one-versus-two upper-unitriangular normal form before any continuum orbit language is added.

### Exact quadratic shadow

The same normal form now gives a sharper nonlinear statement too:

- Write the active simple-root packet as
  - `A_(+-) = E_12 + 2 E_23`
  - `A_(-+) = -E_12 - 2 E_23`
- Then the first nonlinear closure is exact:
  - `A_(+-)^2 = A_(-+)^2 = 2 E_13`
  - equivalently `2 E_13 = [E_12, 2 E_23]`
- The universal generation nilpotents are exactly
  - `N_(+-) = A_(+-) - 2 E_13`
  - `N_(-+) = A_(-+) - 2 E_13`

So the first nonlinear family packet is not an independent extra mode. It is the exact quadratic central shadow of the active simple-root packet already present in the finite family normal form.

### Exact A4 entry point

The local product-heat bridge also sharpens the continuum bottleneck:

- `A0 = 81 a0`
- `A2 = -459 a0 + 81 a2`
- so both `A0` and `A2` are family-blind
- the first family correction is
  - `ΔA4 = 81 ε^2 a0 = 1209 a0 / 9194`

So the honest continuum wall is now more specific than “derive gravity somehow”:

- the remaining family/continuum problem is the refined `A4` density
- not the leading `Λ^4` or `Λ^2` coefficients

### Exact two-channel refined action

The refined continuum side now compresses one step further too:

- On both `CP2_9` and `K3_16` refinement towers,
  - `A0_density(n) = fixed + C20/20^n + C120/120^n`
- The first family-sensitive density is not a new external mode:
  - `ΔA4_density(n) = ε^2 A0_density(n)`
  - `ε^2 = 403/248238`
- So `ΔA4_density` inherits exactly the same `20^-n` and `120^-n` modes as `A0_density`.

Equivalently, through first family order the refined truncated action is still only a two-channel external packet:

- `S_n = (2 f4 Λ^4 + ε^2 f0) A0_density(n) + 2 f2 Λ^2 A2_density(n)`

So the first family-sensitive step renormalizes the geometric `A0` channel rather than creating a third external refinement channel.

### Exact local A4 normalization

The local bridge packet is now normalized sharply enough to state a stronger conservative theorem:

- The relevant product heat coefficient is exactly
  - `A4*B0 + A2*B2 + A0*B4`
- Explicit 4D Euclidean gamma matrices give the universal twisted-Dirac gauge factor
  - `a4_gauge(x) = (4 pi)^(-2) * (1/12) Tr(F_{mu nu} F^{mu nu})`
- For the twisted Dirac gauge endomorphism,
  - `tr_S(E_F) = 0`
- So this packet does not shift the `A2` / Einstein-Hilbert channel; it is purely an `A4` packet.
- On a self-dual branch that universal factor becomes
  - `1 / (96 pi^2)` per curved copy
- The exact repo-native A4-entry theorem already fixes the finite multiplier:
  - `Delta A4 = 81 epsilon^2 a0 = 1209 a0 / 9194`
- Rank-1 external branches kill the packet automatically, while rank-2 activation is quartic:
  - `C -> t C` gives scaling `t^4`
- So before the already-isolated universal rank-2 factor `2`, the reduced local prefactor is
  - `27 / (32 pi^2)`
- And after that factor `2`, the reduced local prefactor is
  - `27 / (16 pi^2)`

So the honest open step is no longer the local coefficient. It is the global branch-counting / orientation theorem over the actual refinement tower.

### Exact external exceptional quanta

The promoted residue dictionary now fixes the external exceptional quanta too:

- Internal exceptional ranks are already promoted as
  - `(40, 6, 8)`
- The continuum coefficients are already exact on the live surface:
  - `c_EH = 320 = 40 * 8`
  - `c_6 = 12480`
  - `a2 = 2240`
- So the external quanta are forced:
  - `Q_curv = c_6 / (40 * 6) = 52`
  - `Q_top = a2 / 40 = 56`
- The same data satisfy the promoted ratio locks:
  - `9 c_EH / c_6 = 3 / 13`
  - `a2 / c_EH = 7`

So the remaining ambiguity is not the local external normalization. It is which primitive external branches actually activate, with what sign and multiplicity, on the refined tower.

### Selected-point q-cyclotomic master lock

The promoted finite and curved packages now compress one step further at the selected point `q = 3`:

- Internal blocks align as
  - `81 = q^4`
  - `6 = 2q`
  - `8 = q^2 - 1`
  - `86 = q^4 + 2q - 1`
  - `248 = 3q^4 + 2q - 1`
- Curved coefficients align as
  - `320 = v(q) (q^2 - 1)` with `v(q) = (q+1)(q^2+1)`
  - `2240 = Phi_6(q) * 320`
  - `12480 = q Phi_3(q) * 320`
- So the promoted curved Weinberg lock is a direct corollary:
  - `9 c_EH / c_6 = q / Phi_3(q) = 3 / 13`

This is a selected-point master theorem, not yet a proof that the whole global bridge is finished. But it does mean the live `81 / 6 / 8`, `320 / 2240 / 12480`, and `3/13` package is now best read as one `q = 3` cyclotomic dictionary rather than three unrelated residue facts.

### Balanced rank-2 bridge selector

There is now also a clean exact selector on the active `2x2` bridge branch:

- For singular-value squares `x, y >= 0`,
  - `tr(C^* C) = x + y`
  - `|det C|^2 = x y`
  - `4 |det C|^2 = tr(C^* C)^2 - (x - y)^2 <= tr(C^* C)^2`
- Equality holds iff the two singular-value squares agree:
  - `x = y`
- So at fixed branch radius the quartic bridge packet is uniquely maximized on the balanced rank-2 branch.
- In the reduced branch action
  - `V(C) = -mu tr(C^* C) + u tr(C^* C)^2 - v A |det C|^2`
  the shape dependence rewrites exactly as
  - `V = -mu r^2 + (u - A v / 4) r^4 + (A v / 4) (x - y)^2`
  with `r^2 = x + y`
- The nonzero stationary point is therefore forced to be balanced:
  - `x = y = mu / (4u - vA)`
- The Hessian at that point is exact:
  - `H = [[2u, 2u-vA], [2u-vA, 2u]]`
  - radial eigenvalue `lambda_radial = 4u - vA` on `(1,1)`
  - shape eigenvalue `lambda_shape = vA` on `(1,-1)`
- Hence if `mu > 0` and `4u > Av`, the nonzero balanced stationary radius is
  - `r_*^2 = 2 mu / (4u - A v)`

This does **not** finish the bridge theorem. The checked local `V29_output_q_stiffness/summary.json` is numerically near-isotropic at quadratic order (`diag_cv ~= 0.024`, `offdiag_rms_ratio ~= 0.0077`, `eig_std_ratio ~= 0.088`), and the companion `V29_output_q_stiffness_validate/summary.json` keeps the finite-difference mean relative error near `0.017`, which is consistent with the reduced selector picture, but only as observation. The exact open step is still the actual branch-realization / orientation theorem on the refinement tower.

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

The local `w33_followup_deliverable_v19.zip` and `w33_followup_deliverable_v20.zip` bundles are structurally suggestive in this same direction. `v19` reproduces the diagonal `9 -> 10` bottleneck in a toy `CP^2`-wired `3x3` Hermitian model by appending a wedge scalar; `v20` sharpens that toy picture to a light-plane / heavy-line flag variable. That is closer to the repo's current exact finite story, because the reduced generation algebra itself now carries a common exact line-plane flag. But those bundle-level continuum interpretations are still not promoted here, because they have not yet been identified with the repo's exact `V4` / Kronecker / `240^2` Yukawa packet as a finished theorem.

## Not yet proved

- ~~A direct subgroup-chain or incidence-theorem derivation of the PMNS cyclotomic formulas from `W(3,3)` alone.~~
  **Resolved (Phase LVI, T801–T815, 62 tests).** The incidence-theorem derivation is the cyclotomic decomposition identity `Φ₃ = μ + Φ₆ + λ`, which partitions the 13 points of `PG(2,3)` into three natural sectors (collinear `μ=4`, transversal `Φ₆=7`, tangent `λ=2`). The PMNS mixing angles are sector-size ratios: `sin²θ₁₂ = μ/Φ₃ = 4/13`, `sin²θ₂₃ = Φ₆/Φ₃ = 7/13`, `sin²θ₁₃ = λ/(Φ₃·Φ₆) = 2/91`. The `θ₁₃` hierarchy arises from second-order `1/Φ₆` suppression. A three-flavor sum rule `s₁₂ + s₂₃ + s₁₃·Φ₆ = 1` holds for all `q`. Verified via explicit `W(3,3)` construction, spread overlap doubly stochastic matrices, and uniform line-adjacency `4(J₁₀ − I₁₀)`.
- A global closed-form transport law replacing every remaining dual CE2 anchor table.
- A finished theorem that turns the full historical TOE narrative into a single exact construction.
