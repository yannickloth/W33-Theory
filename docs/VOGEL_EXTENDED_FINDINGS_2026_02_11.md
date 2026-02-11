# Vogel Extended Findings (2026-02-11)

Summary of an extended rational search for Vogel exceptional-line parameter `m` such that
Vogel universal dimension (alpha=-2, beta=m+4, gamma=2m+4) equals target dimensions.

Targets checked: 728, 486, 242
Search method: exact rational-root search of the induced cubic polynomial using rational-root theorem (exact integer coefficients); denominators capped at 500.

Results:

- 728: no non-degenerate rational exceptional-line `m` found with denominator <= 500 (the only rational root `m=-2` is degenerate and makes Vogel denominator zero, so it is discarded).
- 486: no non-degenerate rational exceptional-line `m` found with denominator <= 500.
- 242: no non-degenerate rational exceptional-line `m` found with denominator <= 500.

Interpretation:

- The earlier observed hit for 728 being `A26 (sl_27)` remains the only classical-family match.
- The absence of rational exceptional-line hits for 486 and 242 up to reasonably large denominators suggests these dimensions are not realized by Vogel's standard exceptional-line rational parameterization (within the tested rational range). This supports the hypothesis that the s12 dimensions (486,242) lie outside the exceptional-line family and are likely not explained by a simple Vogel rational parameter.

Scripts / artifacts used:
- `tools/vogel_rational_cubic_search.py` (rational cubic root finder)
- `artifacts/vogel_rational_cubic_search_2026_02_11.json` (raw results)

Next steps:
- If desired, expand rational search denominator cap further (careful with runtime) or search for algebraic (irrational) solutions via algebraic number field factoring.
- Cross-check with weight-system kernel constraints (Khudoteplov et al., 2024) and recent Vogel deformation papers (Mironov et al., 2025; Isaev, 2026) for other non-rational universality mechanisms.

## Algebraic root analysis (numeric)

- D = 486: cubic roots (approx) = [16.0673377849, -3.80067111827, -2.0 (degenerate)].
- D = 242: cubic roots (approx) = [7.79418309566, -3.66084976233, -2.0 (degenerate)].

None of the non-degenerate real roots above are rational with denominator <= 500 (see `artifacts/vogel_rational_cubic_search_2026_02_11.json`). These algebraic roots are natural candidates for algebraic-number-field analysis (minimal polynomials and Galois structure) and could be consistent with refined or deformed Vogel universality mechanisms (e.g., Macdonald/Vogel deformations).

Additional sweep: we performed a broad rational-cubic sweep across `D` in `[200,1000]` with denominator cap `500` and found no non-degenerate rational exceptional-line solutions in this larger range. See `artifacts/vogel_rational_sweep.json` and `artifacts/vogel_rational_sweep.md` for full results and per-dimension detail."}EOF
