# Core Motif Anchor Search

- Statement: search small anchor sets maximizing coverage under a precision floor.
- Search space: `{'motif_key_count': 6, 'motif_keys': ['x:1-1-0', 'x:1-1-1', 'x:2-2-1', 'y:0-0-0', 'y=1x:1-1-2', 'y=2x:1-1-2'], 'max_full_anchors': 3, 'max_reduced_anchors': 3, 'precision_min': 0.9, 'support_min': 1}`

## Fixed Baseline

- full anchors: `['x:1-1-0']`
- reduced anchors: `['x:2-2-1']`
- metrics: `{'representative_count': 335, 'fired_count': 38, 'coverage': 0.11343283582089553, 'precision_when_fired': 0.9473684210526315, 'conflict_count': 0, 'pred_full_count': 36, 'pred_reduced_count': 2, 'full_recall': 0.12639405204460966, 'reduced_recall': 0.030303030303030304, 'utility_score': 0.10746268656716418}`

## Best Candidate

- full anchors: `['x:1-1-0', 'x:1-1-1', 'y=1x:1-1-2']`
- reduced anchors: `['x:2-2-1', 'y:0-0-0', 'y=2x:1-1-2']`
- metrics: `{'representative_count': 335, 'fired_count': 48, 'coverage': 0.14328358208955225, 'precision_when_fired': 0.9166666666666666, 'conflict_count': 0, 'pred_full_count': 44, 'pred_reduced_count': 4, 'full_recall': 0.1524163568773234, 'reduced_recall': 0.045454545454545456, 'utility_score': 0.13134328358208955}`

## Top Candidates

Rank | coverage | precision | full anchors | reduced anchors
--- | --- | --- | --- | ---
1 | 0.143 | 0.917 | `['x:1-1-0', 'x:1-1-1', 'y=1x:1-1-2']` | `['x:2-2-1', 'y:0-0-0', 'y=2x:1-1-2']`
2 | 0.140 | 0.936 | `['x:1-1-0', 'x:1-1-1', 'y=1x:1-1-2']` | `['x:2-2-1', 'y:0-0-0']`
3 | 0.140 | 0.915 | `['x:1-1-0', 'x:1-1-1', 'y=1x:1-1-2']` | `['x:2-2-1', 'y=2x:1-1-2']`
4 | 0.137 | 0.935 | `['x:1-1-0', 'x:1-1-1', 'y=1x:1-1-2']` | `['x:2-2-1']`
5 | 0.137 | 0.935 | `['x:1-1-0', 'x:1-1-1', 'y=2x:1-1-2']` | `['x:2-2-1', 'y:0-0-0']`
6 | 0.137 | 0.913 | `['x:1-1-0', 'x:1-1-1']` | `['x:2-2-1', 'y:0-0-0', 'y=2x:1-1-2']`
7 | 0.137 | 0.913 | `['x:1-1-0', 'x:1-1-1', 'y=1x:1-1-2']` | `['y:0-0-0', 'y=2x:1-1-2']`
8 | 0.134 | 0.933 | `['x:1-1-0', 'x:1-1-1']` | `['x:2-2-1', 'y:0-0-0']`
9 | 0.134 | 0.933 | `['x:1-1-0', 'x:1-1-1', 'y=1x:1-1-2']` | `['y:0-0-0']`
10 | 0.134 | 0.933 | `['x:1-1-0', 'x:1-1-1', 'y=2x:1-1-2']` | `['x:2-2-1']`
11 | 0.134 | 0.911 | `['x:1-1-0', 'x:1-1-1']` | `['x:2-2-1', 'y=2x:1-1-2']`
12 | 0.134 | 0.911 | `['x:1-1-0', 'x:1-1-1', 'y:0-0-0']` | `['x:2-2-1']`

- Theorem flags: `{'has_feasible_candidate': True, 'best_coverage_ge_fixed_coverage': True, 'best_precision_ge_precision_min': True, 'best_contains_x110': True, 'best_contains_x221': True}`
