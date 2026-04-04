# Canonical Anchor-Chart K3 Wall Note

## New exact corollary

This note records one more conservative compression of the mixed-plane K3 wall.
It does **not** prove existence of the missing witness. It does show that the
remaining wall can be pinned to one canonical local chart.

## Inputs already proved on `master`

The current bridge stack already proves:

1. Exact K3 tail realization is equivalent to a support-preserving nonzero
   row-entry witness in **any fixed supported curvature column**.

2. Exactly `36` of the `45` curvature columns are active.

3. The fan-adjacent active sector splits exactly as
   - anchor `1`,
   - spokes `3`,
   - outer shell `20`.

4. The anchor shell is the single active column
   - `0`
   and it has full rank `1`.

## Corollary

Since the wall is already column-universal, we may choose the simplest active
column as the fixed chart. The fan-shell theorem identifies that simplest chart
canonically as column `0`.

So the live external wall can be reformulated as:

\[
\boxed{
\text{Exact K3 tail realization}
\iff
\text{one support-preserving nonzero row-entry witness in the single canonical anchor column }0
}
\]

## Why this is sharper

Before this corollary, the wall had already been reduced to:

- a nonzero row-entry witness,
- in any fixed active column.

After choosing the canonical rank-`1` anchor chart, the remaining wall is no
longer only “single-chart” in principle. It is pinned to one distinguished
chart:

- not any of the `36` active columns,
- not only one fixed active chart chosen arbitrarily,
- but the canonical least-complexity active chart `0`.

## Honest boundary

This note does **not** prove that the missing witness actually appears in column
`0` on the current K3 host.

It proves something narrower and still useful:

- if exact K3 tail realization exists at all, then by the already-promoted
  column-universality theorem it is equivalent to realizing the witness in
  column `0`;
- and column `0` is the canonical minimal exact chart because it is the unique
  rank-`1` anchor shell.

So the live wall is now best read as a **canonical anchor-chart transvection
criterion** on the fixed mixed-plane host.
