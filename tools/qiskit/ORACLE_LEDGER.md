# Qiskit Bridge Oracle Ledger

This is the compact live ledger for the theorem-backed local Qiskit bridge
search stack.

## Current Stack

| Oracle | Script | Exact Search Space | Qubits | Marked Count | Best Verified Operating Point |
|---|---|---:|---:|---:|---|
| Support hierarchy | `toe_support_hierarchy_search.py` | `120` | `7` | `2` | `6` iterations, mean target-hit `0.9973958333333334` on seeds `5,6,7` |
| Support diagnostic | `toe_support_diagnostic_search.py` | `120` | `7` | `2` | `6` iterations, mean target-hit `0.99609375` on seeds `7,8` |
| Support diagnostic relaxation | `toe_support_diagnostic_relaxation_search.py` | `120` | `7` | `2/20/12/120` | two-seed family: `6 / 1 / 2 / 0` iterations for exact / interleaving / core-order / both |
| Support enhancement relaxation | `toe_support_enhancement_relaxation_search.py` | `360` | `9` | `2/20/12/120` | representative formal-completion two-seed family: `12 / 3 / 5 / 1` iterations for exact / interleaving / core-order / both; exact mode-conjugacy across the 3 enhancement labels |
| Double interleaving shadow | `toe_double_interleaving_shadow_search.py` | `100` | `7` | `10/100` | two-seed exact study: `2` iterations gives mean target-hit `0.97265625`; fully relaxed shell peaks at `0` iterations |
| Product state | `toe_bridge_product_search.py` | `28800` | `15` | `20` | `31` iterations, mean target-hit `1.0` on seeds `7,8` |
| Line factor | `toe_bridge_line_factor_search.py` | `57600` | `16` | `20` | `44` iterations, mean target-hit `1.0` on seeds `7,8` |
| Joint weight filter | `toe_bridge_weight_filter_search.py` | `115200` | `17` | `20` | `63` iterations, mean target-hit `1.0` on seeds `7,8` |
| Split weight filter | `toe_bridge_split_weight_filter_search.py` | `230400` | `18` | `20` | seeded `90`-iteration verification exact in both modes; local formal probe `89/90/91` plateau on seed `7` |
| Diagnostic order | `toe_bridge_diagnostic_order_search.py` | `230400` | `18` | `20` | seeded `90`-iteration verification exact in both modes |
| Diagnostic relaxation | `toe_bridge_diagnostic_relaxation_search.py` | `57600` | `16` | `20/40/120/240` | representative formal-completion two-seed family: `45 / 32 / 18 / 13` iterations for exact / exceptional / hyperbolic / both |
| Diagnostic enhancement relaxation | `toe_bridge_diagnostic_enhancement_relaxation_search.py` | `86400` | `17` | `20/40/120/240` | representative formal-completion-avatar two-seed family: `64 / 45 / 26 / 18` iterations for exact / exceptional / hyperbolic / both; exact mode-conjugacy across the 3 enhancement labels |
| Enhancement factor | `toe_bridge_enhancement_factor_search.py` | `345600` | `19` | `20` | seeded `127`-iteration verification exact in all three enhancement modes |
| Cocycle compatibility wall | `toe_bridge_cocycle_compatibility_search.py` | `345600` | `19` | `60/40` | seeded exact wall checks: `74` iterations gives target-hit `1.0` on the all-compatible wall, `90` gives `1.0` on the nonzero-compatible wall |

## Exact Diagnostic Meaning

- `support hierarchy`: forces `head_line < U1 < transport_avatar`
- `support diagnostic`: factorizes the same `5!` support shell into:
  - `10` support interleavings
  - `6` line/plane/avatar core orders
  - `2` free local-context tail orders
- `support diagnostic relaxation`: keeps that same factorized `120`-state support shell
  fixed and relaxes the exact support interleaving theorem and the exact
  line/plane/avatar core-order theorem one sector at a time:
  - `exact`: marked count `2`
  - `interleaving-relaxed`: marked count `20`
  - `core-order-relaxed`: marked count `12`
  - `both-relaxed`: marked count `120`
- `support enhancement relaxation`: tensors that same support-relaxation shell
  with the exact 3-state external enhancement hierarchy:
  - `current_k3_zero_orbit`
  - `minimal_external_enhancement`
  - `formal_completion_avatar`
  - exact factorization:
    `Marked(relaxation, mode) = Marked_support(relaxation) x {enhancement(mode)}`
  - the three enhancement modes are exact basis-conjugates on the same
    padded `9`-qubit shell
- `double interleaving shadow`: isolates the two exact `10`-state
  interleaving layers already present in the repo:
  - support-core interleavings
  - hyperbolic-factor interleavings
  - both are exact copies of `J(5,3)`
  - the joint shadow has size `100 = 10 * 10`
  - the current bridge freezes one support interleaving while leaving the
    factor copy free
- `product state`: adds the split-vs-formal glue factor
- `line factor`: forces the head-compatible line inside `U1`
- `joint weight filter`: forces the current concentration theorem as one bit
- `split weight filter`: separates hyperbolic and exceptional dominance bits
- `diagnostic order`: separates the five-factor ordering into:
  - hyperbolic order on `U1/U2/U3`
  - exceptional order on `E8_1/E8_2`
  - interleaving pattern of the two sectors
- `diagnostic relaxation`: keeps the corrected pass/pass diagnostic shell
  fixed and relaxes the exact hyperbolic and exceptional order theorems one
  sector at a time:
  - `exact`: marked count `20`
  - `exceptional-order-relaxed`: marked count `40`
  - `hyperbolic-order-relaxed`: marked count `120`
  - `both-orders-relaxed`: marked count `240`
- `diagnostic enhancement relaxation`: tensors that corrected diagnostic shell
  with the exact 3-state enhancement hierarchy:
  - `current_k3_zero_orbit`
  - `minimal_external_enhancement`
  - `formal_completion_avatar`
  - exact factorization:
    `Marked_diagnostic_relaxation(relaxation) x {enhancement(mode)}`
  - the three enhancement modes are exact basis-conjugates on the same
    padded `17`-qubit shell
- `enhancement factor`: replaces the old glue dichotomy by the exact three-state
  external enhancement hierarchy:
  - `current_k3_zero_orbit`
  - `minimal_external_enhancement`
  - `formal_completion_avatar`
- `cocycle compatibility wall`: replaces that free 3-label axis by the exact
  `3 x 2 = 6` compatibility factor
  - wall layers:
    `current_refined_k3_object`, `slot_replacement_datum`,
    `formal_completion_object`
  - orbit states:
    `zero_orbit`, `unique_nonzero_orbit`
  - admissible wall states:
    - `current_refined_k3_object x zero_orbit`
    - `slot_replacement_datum x unique_nonzero_orbit`
    - `formal_completion_object x unique_nonzero_orbit`
  - nonzero-compatible wall states:
    - `slot_replacement_datum x unique_nonzero_orbit`
    - `formal_completion_object x unique_nonzero_orbit`

The diagnostic-order oracle does **not** change the five-factor state count.
It reconstructs the exact `120`-state factor sector as:

`10 interleavings * 6 hyperbolic orders * 2 exceptional orders = 120`.

That makes order failures localizable by theorem sector rather than only by one
combined five-factor permutation.

The diagnostic-relaxation oracle keeps the pass/pass diagnostic shell fixed, so
the theorem selectivity factors become explicit inside that corrected bridge
space:

- exceptional order contributes the exact binary factor
- hyperbolic order contributes the exact 6-fold factor
- interleaving is already free in the diagnostic-order oracle

The diagnostic-enhancement relaxation oracle sits one level above that shell:
it preserves the same order-selectivity profile across the exact three-state
enhancement hierarchy while shifting the padded-shell Grover windows from
`57600 -> 65536` to `86400 -> 131072`.

The enhancement-factor oracle resolves a different wall: it keeps the theorem
shell fixed and separates the current refined K3 object, the exact minimal new
datum, and the resulting formal completion object inside one discrete state
space.

The support-enhancement relaxation oracle sits strictly below that larger wall:
it proves that the exact support-selectivity profile survives unchanged across
the 3-state enhancement hierarchy, while the clean Grover windows shift because
`360` states pad to `512`. Most sharply, the fully relaxed support sector moves
from a `0`-step optimum on the bare `120`-state shell to a `1`-step optimum on
the enlarged shell.

The double-interleaving shadow is a bounded exact side result rather than a new
physics claim. It shows that the support and factor interleaving sectors are
two canonical copies of the same `10`-vertex Johnson object `J(5,3)`, and that
the current bridge asymmetry is precise: the support theorem freezes one copy
while the factor copy remains free.

The cocycle-compatibility wall is the stronger replacement for the old
enhancement-factor interpretation. The wall is no longer just a free 3-label
mode family. It is an exact compatibility theorem with forbidden corners on a
`6`-state factor, and the live nonzero wall is the `2`-state subset given by
the slot-replacement datum and the formal completion object, both paired with
the unique nonzero orbit.

## Reproduce

```bash
qiskit-python tools/qiskit/toe_bridge_oracle_iteration_study.py \
  --target support-diagnostic \
  --iterations 5 6 7 \
  --seeds 7 8 \
  --shots 256 \
  --top 6
```

```bash
qiskit-python tools/qiskit/toe_support_diagnostic_relaxation_search.py \
  --relaxation exact \
  --shots 256 \
  --seed 7 \
  --top 8
```

```bash
qiskit-python tools/qiskit/toe_bridge_oracle_iteration_study.py \
  --target support-enhancement-exact \
  --iterations 12 13 14 \
  --seeds 7 8 \
  --shots 256 \
  --top 6
```

```bash
qiskit-python tools/qiskit/toe_bridge_oracle_iteration_study.py \
  --target support-enhancement-both \
  --iterations 0 1 2 \
  --seeds 7 8 \
  --shots 256 \
  --top 4
```

```bash
qiskit-python tools/qiskit/toe_bridge_oracle_iteration_study.py \
  --target line-factor \
  --iterations 44 45 46 \
  --seeds 7 8 \
  --shots 256 \
  --top 6
```

```bash
qiskit-python tools/qiskit/toe_bridge_oracle_iteration_study.py \
  --target weight-filter \
  --iterations 63 64 65 \
  --seeds 7 8 \
  --shots 256 \
  --top 6
```

```bash
qiskit-python tools/qiskit/toe_bridge_oracle_iteration_study.py \
  --target double-interleaving-exact \
  --iterations 1 2 3 \
  --seeds 7 8 \
  --shots 256 \
  --top 6
```

```bash
qiskit-python tools/qiskit/toe_bridge_diagnostic_order_search.py \
  --mode formal-completion \
  --shots 256 \
  --seed 7 \
  --top 8
```

```bash
qiskit-python tools/qiskit/toe_bridge_oracle_iteration_study.py \
  --target diagnostic-relaxation-exact \
  --iterations 44 45 46 \
  --seeds 7 8 \
  --shots 256 \
  --top 6
```

```bash
qiskit-python tools/qiskit/toe_bridge_oracle_iteration_study.py \
  --target diagnostic-enhancement-exact \
  --iterations 63 64 65 \
  --seeds 7 8 \
  --shots 256 \
  --top 6
```

```bash
qiskit-python tools/qiskit/toe_bridge_cocycle_compatibility_search.py \
  --focus nonzero-compatible \
  --iterations 90 \
  --shots 256 \
  --seed 7 \
  --top 8
```

```bash
qiskit-python tools/qiskit/toe_bridge_enhancement_factor_search.py \
  --mode formal-completion-avatar \
  --shots 256 \
  --seed 7 \
  --top 8
```
