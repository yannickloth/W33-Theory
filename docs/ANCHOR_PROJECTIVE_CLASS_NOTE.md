# Anchor Projective-Class K3 Wall Note

## New conservative compression

This note sharpens the canonical anchor-chart formulation one more step.
It does **not** prove existence of the missing K3 witness. It shows that once the
wall is pinned to the canonical anchor chart, there is no remaining linear
freedom on that shell beyond a single projective nonzero class.

## Inputs already promoted on `master`

The current bridge stack already proves:

1. Exact K3 tail realization is equivalent to a support-preserving nonzero
   row-entry witness in any fixed active curvature column.

2. The fan-adjacent active sector splits exactly as
   - anchor `1`,
   - spokes `3`,
   - outer shell `20`.

3. The anchor shell is the single active column `0`.

4. The anchor shell has rank `1`.

5. The local field is `F3`, so the nonzero scalars are exactly `1` and `2`.

## Corollary

From the canonical anchor-chart note, the live wall can already be written as:

\[
\text{Exact K3 tail realization}
\iff
\text{one support-preserving nonzero row-entry witness in column }0.
\]

Because the anchor shell has rank `1`, every nonzero anchor-shell witness lies
on the same one-dimensional line. Passing from linear representatives to
projective class removes the residual `F3* = {1,2}` scaling ambiguity.

So the external wall may be sharpened further to:

\[
\boxed{
\text{Exact K3 tail realization}
\iff
\text{one nonzero support-preserving witness in the unique projective class of anchor column }0
}
\]

## Meaning

The anchor side is no longer a matrix-valued search problem and not even a
multi-parameter column problem. Once restricted to the canonical anchor chart,
only one projective rank-`1` witness class remains.

Equivalently, the open K3 wall on the anchor side is now:

- one fixed chart (`0`),
- one fixed shell (anchor),
- one fixed rank (`1`),
- one nonzero projective class.

## Honest boundary

This note does **not** prove that the current K3 host realizes that class.
It proves only that the anchor-side wall has no further exact linear moduli once
it is expressed on the canonical anchor shell.

So the strongest conservative reading is:

> the mixed-plane K3 wall has been reduced from a 45-column curvature problem to
> one canonical rank-1 projective transvection class on anchor column `0`.
