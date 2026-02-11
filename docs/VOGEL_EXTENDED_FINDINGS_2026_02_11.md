# Vogel Extended Findings (2026-02-11)

Summary of an extended rational search for Vogel exceptional-line parameter `m` such that
Vogel universal dimension (`alpha=-2`, `beta=m+4`, `gamma=2m+4`) equals target dimensions.

Targets checked: `728`, `486`, `242`.
Search method: exact rational-root search for the induced cubic condition.

## Target results

- `D=728`: no non-degenerate rational exceptional-line `m`.
- `D=486`: no non-degenerate rational exceptional-line `m`.
- `D=242`: no non-degenerate rational exceptional-line `m`.

The only universal rational root that appears uniformly in the cubic form is the
always-degenerate `m=-2`, which is excluded because it zeroes Vogel denominators.

## Additional sweep (range check)

We also scanned dimensions `D` in `[200,1000]` with denominator cap `500`.
This larger scan is **not empty**: rational non-degenerate hits occur at
`D in {248, 287, 336, 484, 603, 782}`.

So the correct statement is:
- s12 dimensions (`728`, `486`, `242`) still have no rational non-degenerate hits,
- but the broader range does contain isolated rational-hit dimensions.

See artifacts:
- `artifacts/vogel_rational_cubic_search_2026_02_11.json`
- `artifacts/vogel_rational_sweep.json`
- `artifacts/vogel_rational_sweep.md`
- `artifacts/vogel_rational_hit_catalog_2026_02_11.json`
- `docs/VOGEL_RATIONAL_HIT_CATALOG_2026_02_11.md`
- `artifacts/vogel_rational_dimension_theorem_2026_02_11.json`
- `docs/VOGEL_RATIONAL_DIMENSION_THEOREM_2026_02_11.md`
- `artifacts/vogel_rational_hit_crosswalk_2026_02_11.json`
- `docs/VOGEL_RATIONAL_HIT_CROSSWALK_2026_02_11.md`

## Closed-form note

After factoring the always-degenerate `(m+2)` factor, non-degenerate roots satisfy:

`30*m^2 + (118-D)*m + (112-4D) = 0`

so rational non-degenerate roots are controlled by the discriminant

`Delta(D) = D^2 + 244*D + 484`.

For s12 dimensions:
- `Delta(242)=118096` (not a square)
- `Delta(486)=355264` (not a square)
- `Delta(728)=708100` (not a square)

This gives a compact arithmetic obstruction certificate for rational-hit absence
at the current s12 target dimensions.

Using
`Delta(D)=(D+122)^2-120^2`,
the square-discriminant condition is equivalent to
`(D+122-r)(D+122+r)=14400`, so integer-dimensional hits are an exact finite
divisor-pair classification problem.

The complete positive non-degenerate hit set is:
`{1,3,8,14,28,47,52,78,96,119,133,190,248,287,336,484,603,782,1081,1680,3479}`.

Crosswalk classification of this finite set:
- classical-family hits: `{3,8,28,78,190,1081,1680}`
- direct-table hits: `{8,14,28,52,78,133,248}`
- arithmetic-only hits: `{1,47,96,119,287,336,484,603,782,3479}`
