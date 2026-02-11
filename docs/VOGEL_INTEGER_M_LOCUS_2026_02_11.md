# Vogel Integer-m Locus (Exceptional Line)

- Identity: `D=2*(3m+7)*(5m+8)/(m+4)=30*(m+4)-122+120/(m+4)`
- Criterion: `For integer m != -4, D is integer iff (m+4) divides 120`
- Positive dimensions from integer m: `[8, 28, 52, 78, 133, 190, 248, 336, 484, 603, 782, 1081, 1680, 3479]`
- Target checks: `{'728': {'is_integer_m_hit': False, 'integer_m_values': []}, '486': {'is_integer_m_hit': False, 'integer_m_values': []}, '242': {'is_integer_m_hit': False, 'integer_m_values': []}}`

n=m+4 | m | D(m)
--- | --- | ---
3 | -1 | 8
1 | -3 | 28
4 | 0 | 28
5 | 1 | 52
6 | 2 | 78
8 | 4 | 133
10 | 6 | 190
12 | 8 | 248
15 | 11 | 336
20 | 16 | 484
24 | 20 | 603
30 | 26 | 782
40 | 36 | 1081
60 | 56 | 1680
120 | 116 | 3479

- Verification mismatch count in scan range `[-300, 300]`: `0`
