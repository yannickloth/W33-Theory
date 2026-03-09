
# W33 Closure Ladder

## Minimal forcing chain
1. **Input data**: finite field `F_3`, symplectic form `ω`, and isotropic geometry `W(3,3)`.
2. **Graph layer**: unique collinearity graph `SRG(40,12,2,4)` with eigenvalues `12, 2, -4`.
3. **Chain/Hodge layer**:
   - `C^0` exact sector
   - `C^1 = im(d_0) ⊕ H^1 ⊕ im(d_1^T) = 39 + 81 + 120`
   - `C^2` / triangle sector with `160` triangles
4. **Exceptional layer**:
   - `H^1 ≅ 27 ⊕ 27 ⊕ 27`
   - `g_0 = E_6 ⊕ A_2`
   - `E_8 = g_0(86) ⊕ g_1(81) ⊕ g_2(81)`
5. **Interaction layer**:
   - `l_3` supplies antisymmetric Yukawa-like couplings
   - `l_4` supplies self-energy / association-scheme mass matrix
   - `l_5, l_6` enforce exact `Z/3` generation selection
6. **Spectral-action layer**:
   - `D^2` spectrum `{0^122, 4^240, 10^48, 16^30}`
   - non-backtracking Hashimoto/Ihara-Bass identity fixes the `k-1` factor
7. **Observable layer**:
   - bare/local numbers from SRG ratios
   - dressed/projective numbers from `PG(2,3)` and cyclotomic bridges
   - global/spectral numbers from determinant, propagator, heat-kernel, and zeta identities

## New synthesis
The file behaves less like one equation and more like a **three-shell renormalization machine**:

### Shell A — local SRG shell
Uses direct ratios of `(v,k,λ,μ)`:
- `Δ = μ = 4`
- `N_c = k/μ = 3`
- `sin^2 θ_W = μ/(k+μ) = 1/4`
- dimensions `4+8=12`

### Shell B — projective/cyclotomic shell
Uses `q=3`, `|PG(2,3)| = 13`, and bridge primes `7,13`:
- `sin^2 θ_W(M_Z) = 3/13`
- `θ_C = arctan(3/13)`
- PMNS angles over denominators `13` and `91`
- `v_EW = q^5 + q = 246`

### Shell C — global spectral shell
Uses the full graph operators, directed-edge carrier space, and Hodge data:
- `α^{-1} = 137 + 40/1111`
- `β_0+β_1+β_2 = 122`
- `χ = -40`
- `Tr(ghost)=Tr(YM)=480`
- `Q = (41/160) I_120`

## Closure claim
A viable closure is obtained only if observables are assigned to the correct shell.
Many apparent duplicate formulas in the file are not contradictions if interpreted as:
- **bare** value,
- **GUT-normalized** value,
- **IR dressed** value.

## Remaining bridge obligations
1. Explicit continuum limit for `Shell C -> QFT/GR`.
2. Unit/normalization map for Planck scale and baryon fraction variants.
3. A first-principles map from `H^1` and `l_n` brackets to actual fermion masses.
