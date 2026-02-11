# Vogel Rational Dimension Theorem (Arithmetic Form)

- Identity: `Delta(D)=D^2+244D+484=(D+122)^2-120^2`
- Factorization: `(D+122-r)(D+122+r)=14400 with r=sqrt(Delta(D))`
- Consequence: integer dimensions with rational non-degenerate exceptional-line roots are finite.
- Positive hit dimensions (`21` total): `[1, 3, 8, 14, 28, 47, 52, 78, 96, 119, 133, 190, 248, 287, 336, 484, 603, 782, 1081, 1680, 3479]`
- Window hits `[200, 1000]`: `[248, 287, 336, 484, 603, 782]`
- Target checks: `{'728': {'in_positive_hit_dims': False, 'nondeg_rational_roots': []}, '486': {'in_positive_hit_dims': False, 'nondeg_rational_roots': []}, '242': {'in_positive_hit_dims': False, 'nondeg_rational_roots': []}}`

Dimension | sqrt(Delta) | Non-degenerate rational roots
--- | --- | ---
1 | 27 | -12/5, -3/2
3 | 35 | -5/2, -4/3
8 | 50 | -8/3, -1
14 | 64 | -14/5, -2/3
28 | 90 | -3, 0
47 | 119 | -19/6, 4/5
52 | 126 | -16/5, 1
78 | 160 | -10/3, 2
96 | 182 | -17/5, 8/3
119 | 209 | -52/15, 7/2
133 | 225 | -7/2, 4
190 | 288 | -18/5, 6
248 | 350 | -11/3, 8
287 | 391 | -37/10, 28/3
336 | 442 | -56/15, 11
484 | 594 | -19/5, 16
603 | 715 | -23/6, 20
782 | 896 | -58/15, 26
1081 | 1197 | -39/10, 36
1680 | 1798 | -59/15, 56
3479 | 3599 | -119/30, 116

- Verification (`factorization_matches_bruteforce`): `True`
