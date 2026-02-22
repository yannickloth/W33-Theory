# Core Motif Enrichment Stats

- Statement: quantify enrichment of core motifs for orbit `2592` versus baseline prevalence.
- Core motif count: `13`

Dataset | reps | baseline_2592
--- | --- | ---
agl_exact_full | 7 | 1.000
hessian_exact_full | 79 | 0.861
hessian_exhaustive2 | 256 | 0.785

## Hessian Combined Focus Motifs

Motif | support | precision_2592 | lift_2592 | p_enrich_2592 | p_enrich_1296
--- | --- | --- | --- | --- | ---
x:1-1-0 | 36 | 0.944 | 1.176 | 0.013550 | 0.997494
x:2-2-1 | 2 | 0.000 | 0.000 | 1.000000 | 0.038341

- Theorem flags: `{'hessian_combined_has_x110': True, 'x110_support_ge_30': True, 'x110_precision_ge_0p90': True, 'x110_enrichment_pvalue_le_0p05': True, 'x221_exists_and_is_pure_1296': True}`
