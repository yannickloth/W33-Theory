# V17 — Define l5 from δL4 (sampled patch) and probe the n=6 layer via δL5

We continue the cochain-tower strategy:
- V15 defined **l4** to cancel the n=4 residual.
- V16 measured the next obstruction **δL4** (n=5 layer) and found it sparse and single-term.

## 1) Build an l5 patch from δL4 (sample)
- sampled 5-tuples for δL4: 1000000
- δL4 stats: {'zero': 996508, 'nonzero': 3492, 'single': 3492} (all nonzero were single-term)
- constructed l5 records (sample supports): 3425
- l5 support size (distinct outputs): 234

## 2) Probe the n=6 obstruction candidate δL5 (sample)
- sampled 6-tuples: 300000
- δL5 stats: {'zero': 299928, 'nonzero': 72, 'single': 72} (all nonzero single-term)
- δL5 support size: 66
- coeff histogram top: [(-1, 26), (1, 14), (-2, 10), (2, 10), (-3, 5), (3, 5), (4, 1), (-5, 1)]
- output grade histogram: {'g1': 29, 'g2': 19, 'g0': 24}

## 3) Closure behavior
- H3 support (from l5 outputs) starts at 234 and closes to 248=248 under g1 action in one step: [{'iter': 0, 'added': 14, 'added_cartan': 8, 'added_grade_hist': {'g2': 2, 'g0': 2, 'g1': 2}}, {'iter': 1, 'added': 0}]

### Interpretation
- The tower remains **sparse and single-term** at the next layer: δL5 nonzero rate ~0.024% on random g1^6.
- This is an *approximate* V17 because l5 was patched only on sampled δL4 supports; expanding l5 coverage should reduce δL5 further.
- Next: increase l5 coverage or find a structured enumeration of δL4 supports, then define l6 from δL5 supports.
