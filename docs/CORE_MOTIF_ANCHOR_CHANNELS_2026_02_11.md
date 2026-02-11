# Core Motif Anchor Channels

- Statement: derive high-precision anchor motifs and evaluate an abstaining classifier for orbit class.
- full anchors: `['x:1-1-0']`
- reduced anchors: `['x:2-2-1']`

Dataset | reps | fired | coverage | precision_when_fired | full_recall | reduced_recall
--- | --- | --- | --- | --- | --- | ---
hessian_exact_full | 79 | 17 | 0.215 | 0.941 | 0.221 | 0.091
hessian_exhaustive2 | 256 | 21 | 0.082 | 0.952 | 0.095 | 0.018
hessian_combined | 335 | 38 | 0.113 | 0.947 | 0.126 | 0.030

- Theorem flags: `{'full_anchor_contains_x110': True, 'reduced_anchor_contains_x221': True, 'combined_precision_when_fired_ge_0p90': True, 'combined_conflict_count_zero': True}`
