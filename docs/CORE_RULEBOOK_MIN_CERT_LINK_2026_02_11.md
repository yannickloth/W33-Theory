# Core Rulebook x Minimal-Certificate Census Link

- Statement: detect overlap between nontrivial global-core motifs and canonical minimal-certificate representative triplets.
- Core motif count: `13`

Dataset | distinct reps | reps with parallel triplet | reps with core overlap | overlap rate
--- | --- | --- | --- | ---
agl_exact_full | 7 | 4 | 0 | 0.000
hessian_exact_full | 79 | 47 | 18 | 0.228
hessian_exhaustive2 | 256 | 142 | 30 | 0.117

- Theorem flags: `{'agl_exact_has_zero_core_overlap': True, 'hessian_exact_has_positive_core_overlap': True, 'hessian_exhaustive_has_positive_core_overlap': True, 'dominant_overlap_motif_is_x_110': True}`

## agl_exact_full

- source: `artifacts\e6_f3_trilinear_min_cert_exact_agl_full_with_geotypes.json`
- overlap orbit histogram: `{}`
- top overlap motifs: `[]`
- representative index samples: `[]`

## hessian_exact_full

- source: `artifacts\e6_f3_trilinear_min_cert_exact_hessian_full_with_geotypes.json`
- overlap orbit histogram: `{'1296': 2, '2592': 16}`
- top overlap motifs: `[{'motif': 'x:1-1-0', 'count': 16}, {'motif': 'x:1-1-1', 'count': 1}, {'motif': 'x:2-2-1', 'count': 1}]`
- representative index samples: `[1, 7, 29, 34, 35, 36, 37, 38, 39, 40]`

## hessian_exhaustive2

- source: `artifacts\e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2_with_geotypes.json`
- overlap orbit histogram: `{'1296': 4, '2592': 26}`
- top overlap motifs: `[{'motif': 'x:1-1-0', 'count': 20}, {'motif': 'x:1-1-1', 'count': 5}, {'motif': 'y=1x:1-1-2', 'count': 2}, {'motif': 'x:2-2-1', 'count': 1}, {'motif': 'y:0-0-0', 'count': 1}, {'motif': 'y=2x:1-1-2', 'count': 1}]`
- representative index samples: `[1, 17, 21, 22, 25, 28, 29, 31, 35, 36]`
