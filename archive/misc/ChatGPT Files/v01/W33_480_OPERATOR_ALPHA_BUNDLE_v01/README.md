
# W33 480-Operator + Alpha Hinge (v01)

This bundle turns the "mysterious" denominator in the SRG alpha formula into a **forced operator identity**.

## What you get

1) **W(3,3) reconstruction** (`build_w33.py`)
   - Builds the 40-vertex collinearity graph of GQ(3,3) using the symplectic orthogonality rule.
   - Verifies SRG(40,12,2,4) and saves `w33_adjacency.npy`.

2) **480 directed-edge carrier + non-backtracking operator** (`nonbacktracking_480.py`)
   - Builds the 480 directed edges (2m) and the Hashimoto non-backtracking operator `B`.
   - Verifies each row has outdegree `k-1 = 11` and saves:
     - `w33_directed_edges.npy`
     - `w33_nonbacktracking_B.npz`

3) **Ihara–Bass determinant identity verification** (`ihara_bass_verify.py`)
   - Numerically checks:
     `det(I - u B) = (1 - u^2)^(m-n) det(I - u A + u^2 (k-1) I)`
   - Confirms (k−1) is a *forced* structural factor of the 480-state dynamics.

4) **The Alpha Hinge (the missing connection)** (`alpha_from_operator.py`)
   - Defines the vertex-space operator:
     `M := (k-1)((A - λI)^2 + I)`
   - Proves the exact identity:
     `1^T M^{-1} 1 = v / [(k-1)((k-λ)^2 + 1)]`
   - For W(3,3): `v=40,k=12,λ=2` ⇒ `40/1111 = 0.036003600360...`
   - Therefore:
     `α^{-1} = (k^2 - 2μ + 1) + 1^T M^{-1} 1 = 137 + 40/1111`

## Run

```bash
python build_w33.py
python nonbacktracking_480.py
python ihara_bass_verify.py
python alpha_from_operator.py
```

## Why this matters

Your original alpha correction term used:

`v / [(k-1)((k-λ)^2+1)]`

This bundle shows that fraction is **exactly** the quadratic form of the inverse
of a canonical graph operator acting on the all-ones mode. It is *not* an arbitrary denominator.

What's still open (physics, not math):
- interpreting `M` as a gauge/EM propagator (or a piece of an effective action)
  and fixing the normalization so α emerges as a true prediction rather than a structural invariant.
