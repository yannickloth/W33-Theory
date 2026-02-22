# Core Motif Orbit Polarization

- Statement: classify orbit-size polarization of nontrivial-core motifs in minimal-certificate representative datasets.
- Core motif count: `13`

Dataset | reps | overlap reps | overlap rate | overlap orbit hist
--- | --- | --- | --- | ---
agl_exact_full | 7 | 0 | 0.000 | {}
hessian_exact_full | 79 | 18 | 0.228 | {'1296': 2, '2592': 16}
hessian_exhaustive2 | 256 | 30 | 0.117 | {'1296': 4, '2592': 26}

## x:1-1-0 motif

Dataset | support | orbit_1296 | orbit_2592 | precision_2592
--- | --- | --- | --- | ---
hessian_exact_full | 16 | 1 | 15 | 0.938
hessian_exhaustive2 | 20 | 1 | 19 | 0.950
hessian_combined | 36 | 2 | 34 | 0.944

- Theorem flags: `{'agl_exact_zero_overlap': True, 'hessian_exact_positive_overlap': True, 'hessian_exhaustive_positive_overlap': True, 'x110_precision_ge_0p90_in_hessian_exact': True, 'x110_precision_ge_0p90_in_hessian_exhaustive': True, 'x110_combined_precision_ge_0p90_in_hessian': True}`
