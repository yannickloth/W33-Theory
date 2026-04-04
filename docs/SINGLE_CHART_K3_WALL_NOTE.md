# Single-Chart K3 Wall Note

## New compression step

This note records one further conservative compression of the current K3 mixed-plane frontier.
It does **not** claim a finished continuum theorem. It does sharpen the open wall.

## Promoted ingredients already on master

The current frontier already fixes the following exact data:

1. The external carrier package is rigid:
   - the head-compatible image line,
   - the canonical plane `U1`,
   - the ordered shell `81 -> 162 -> 81`,
   - the existing tail-to-head `81x81` slot.

2. The missing non-split datum is the unique nonzero ternary cocycle / glue orbit.

3. The mixed-plane transport wall has already been localized to the off-diagonal curvature block.

4. Every supported row of that off-diagonal block is one-sparse.

5. The block has `45` columns total and exactly `36` active columns.

6. Every active column already carries:
   - both row components,
   - both nonzero `F3` values,
   - supported row entries.

7. Exact K3 tail realization is already equivalent to a nonzero row-entry witness in any fixed supported curvature column.

## Consequence

Those seven facts imply a sharper local statement:

> Fix any one active curvature column `c*`.
> Then exact K3 tail realization is equivalent to existence of one support-preserving
> nonzero one-sparse row-entry witness in that single fixed column `c*` on the current mixed-plane host.

So the external wall no longer needs to be phrased as a search over:

- all `36` active columns,
- all supported rows,
- or both nonzero field values separately.

The active-column universality theorem removes the column choice, and the `F3`
 gauge equivalence of the two nonzero nilpotent increments removes the field-value choice.

## Single-chart local transvection criterion

The cleanest conservative formulation is therefore:

\[
\boxed{
\text{Exact K3 tail realization}
\iff
\text{one nonzero one-sparse row-entry witness in one fixed active chart}
}
\]

Equivalently, the remaining K3 wall is one local support-preserving transvection problem.

## Why this is genuinely sharper

Before this compression, the live wall could still be read as a broad nonzero-witness problem on the whole rank-`36` active block.
After combining the already-promoted theorems, the wall is smaller:

- not a `36`-chart search,
- not a full-row search,
- not a value-selection problem over `F3*`,
- but one local nilpotent-increment class in one chosen active chart.

## Honest boundary

This note does **not** prove the existence of that witness on the K3 side.
It only shows that the remaining existence problem is even more localized than the current frontier note states explicitly.

So the honest strongest reading is:

- the finite/spectral side is already fixed,
- the carrier package is already fixed,
- the nonzero orbit is already unique,
- and the external wall now reduces to one single-chart local transvection witness.
