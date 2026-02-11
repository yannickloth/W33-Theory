# Vogel Rational Hit Crosswalk

- Positive hit dimensions (`21`): `[1, 3, 8, 14, 28, 47, 52, 78, 96, 119, 133, 190, 248, 287, 336, 484, 603, 782, 1081, 1680, 3479]`
- Classical hit dimensions: `[3, 8, 28, 78, 190, 1081, 1680]`
- Direct-table hit dimensions: `[8, 14, 28, 52, 78, 133, 248]`
- Arithmetic-only hit dimensions: `[1, 47, 96, 119, 287, 336, 484, 603, 782, 3479]`
- Integral-root hit dimensions: `[8, 28, 52, 78, 133, 190, 248, 336, 484, 603, 782, 1081, 1680, 3479]`
- Target dimensions checked: `[728, 486, 242]`

Dimension | Roots | Classical hits | Direct-table hits | Category
--- | --- | --- | --- | ---
1 | -12/5, -3/2 | - | - | arithmetic-only
3 | -5/2, -4/3 | A:[1] | - | classical-only
8 | -8/3, -1 | A:[2] | A2 | classical+direct
14 | -14/5, -2/3 | - | G2 | direct-only
28 | -3, 0 | D:[4] | D4 | classical+direct
47 | -19/6, 4/5 | - | - | arithmetic-only
52 | -16/5, 1 | - | F4 | direct-only
78 | -10/3, 2 | B:[6], C:[6] | E6 | classical+direct
96 | -17/5, 8/3 | - | - | arithmetic-only
119 | -52/15, 7/2 | - | - | arithmetic-only
133 | -7/2, 4 | - | E7 | direct-only
190 | -18/5, 6 | D:[10] | - | classical-only
248 | -11/3, 8 | - | E8 | direct-only
287 | -37/10, 28/3 | - | - | arithmetic-only
336 | -56/15, 11 | - | - | arithmetic-only
484 | -19/5, 16 | - | - | arithmetic-only
603 | -23/6, 20 | - | - | arithmetic-only
782 | -58/15, 26 | - | - | arithmetic-only
1081 | -39/10, 36 | B:[23], C:[23] | - | classical-only
1680 | -59/15, 56 | A:[40] | - | classical-only
3479 | -119/30, 116 | - | - | arithmetic-only

## Target Checks

- `D=728` in hit set: `False`; nearest hit: `{'nearest_dims': [782], 'distance': 54}`
- `D=486` in hit set: `False`; nearest hit: `{'nearest_dims': [484], 'distance': 2}`
- `D=242` in hit set: `False`; nearest hit: `{'nearest_dims': [248], 'distance': 6}`
