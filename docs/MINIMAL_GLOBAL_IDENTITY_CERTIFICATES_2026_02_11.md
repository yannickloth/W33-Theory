# Minimal Global Identity Certificates

- Statement: for z-map `(1,0)`, compute smallest witness sets of `(line,z)` constraints that isolate the unique global stabilizer.

Mode | Candidates | Minimal certificate size | Number of minimal certificates
--- | --- | --- | ---
all_agl | 864 | 6 | 688
hessian216 | 432 | 5 | 33

- Theorem flags: `{'all_agl_min_size_6': True, 'hessian216_min_size_5': True, 'hessian_strictly_smaller_than_agl': True, 'all_agl_count_688': True, 'hessian216_count_33': True}`

## all_agl

- target candidate: `{'A': [1, 0, 0, 1], 'det': 1, 'shift': [0, 0], 'eps': 1}` (unique full match count `1`)
- top constraints by frequency in minimal certificates:
  - idx `16`: freq `425` (0.618) -> `{'line': [[0, 1], [1, 1], [2, 1]], 'line_type': 'y', 'abc': [0, 1, 1], 'z': 1}`
  - idx `14`: freq `234` (0.340) -> `{'line': [[0, 1], [1, 0], [2, 2]], 'line_type': 'y=2x', 'abc': [1, 1, 1], 'z': 2}`
  - idx `6`: freq `214` (0.311) -> `{'line': [[0, 0], [1, 1], [2, 2]], 'line_type': 'y=1x', 'abc': [1, 2, 0], 'z': 0}`
  - idx `9`: freq `211` (0.307) -> `{'line': [[0, 0], [1, 2], [2, 1]], 'line_type': 'y=2x', 'abc': [1, 1, 0], 'z': 0}`
  - idx `22`: freq `207` (0.301) -> `{'line': [[0, 2], [1, 0], [2, 1]], 'line_type': 'y=1x', 'abc': [1, 2, 1], 'z': 1}`
  - idx `27`: freq `206` (0.299) -> `{'line': [[0, 2], [1, 2], [2, 2]], 'line_type': 'y', 'abc': [0, 1, 2], 'z': 0}`
  - idx `18`: freq `203` (0.295) -> `{'line': [[0, 1], [1, 2], [2, 0]], 'line_type': 'y=1x', 'abc': [1, 2, 2], 'z': 0}`
  - idx `20`: freq `192` (0.279) -> `{'line': [[0, 1], [1, 2], [2, 0]], 'line_type': 'y=1x', 'abc': [1, 2, 2], 'z': 2}`
- first sample certificate:
  - `{'constraint_indices': [0, 1, 5, 7, 9, 16], 'constraints': [{'line': [[0, 0], [0, 1], [0, 2]], 'line_type': 'x', 'abc': [1, 0, 0], 'z': 0}, {'line': [[0, 0], [0, 1], [0, 2]], 'line_type': 'x', 'abc': [1, 0, 0], 'z': 1}, {'line': [[0, 0], [1, 0], [2, 0]], 'line_type': 'y', 'abc': [0, 1, 0], 'z': 2}, {'line': [[0, 0], [1, 1], [2, 2]], 'line_type': 'y=1x', 'abc': [1, 2, 0], 'z': 1}, {'line': [[0, 0], [1, 2], [2, 1]], 'line_type': 'y=2x', 'abc': [1, 1, 0], 'z': 0}, {'line': [[0, 1], [1, 1], [2, 1]], 'line_type': 'y', 'abc': [0, 1, 1], 'z': 1}]}`

## hessian216

- target candidate: `{'A': [1, 0, 0, 1], 'det': 1, 'shift': [0, 0], 'eps': 1}` (unique full match count `1`)
- top constraints by frequency in minimal certificates:
  - idx `6`: freq `19` (0.576) -> `{'line': [[0, 0], [1, 1], [2, 2]], 'line_type': 'y=1x', 'abc': [1, 2, 0], 'z': 0}`
  - idx `16`: freq `19` (0.576) -> `{'line': [[0, 1], [1, 1], [2, 1]], 'line_type': 'y', 'abc': [0, 1, 1], 'z': 1}`
  - idx `19`: freq `12` (0.364) -> `{'line': [[0, 1], [1, 2], [2, 0]], 'line_type': 'y=1x', 'abc': [1, 2, 2], 'z': 1}`
  - idx `22`: freq `11` (0.333) -> `{'line': [[0, 2], [1, 0], [2, 1]], 'line_type': 'y=1x', 'abc': [1, 2, 1], 'z': 1}`
  - idx `28`: freq `11` (0.333) -> `{'line': [[0, 2], [1, 2], [2, 2]], 'line_type': 'y', 'abc': [0, 1, 2], 'z': 1}`
  - idx `31`: freq `10` (0.303) -> `{'line': [[1, 0], [1, 1], [1, 2]], 'line_type': 'x', 'abc': [1, 0, 1], 'z': 1}`
  - idx `14`: freq `8` (0.242) -> `{'line': [[0, 1], [1, 0], [2, 2]], 'line_type': 'y=2x', 'abc': [1, 1, 1], 'z': 2}`
  - idx `12`: freq `7` (0.212) -> `{'line': [[0, 1], [1, 0], [2, 2]], 'line_type': 'y=2x', 'abc': [1, 1, 1], 'z': 0}`
- first sample certificate:
  - `{'constraint_indices': [0, 4, 6, 16, 19], 'constraints': [{'line': [[0, 0], [0, 1], [0, 2]], 'line_type': 'x', 'abc': [1, 0, 0], 'z': 0}, {'line': [[0, 0], [1, 0], [2, 0]], 'line_type': 'y', 'abc': [0, 1, 0], 'z': 1}, {'line': [[0, 0], [1, 1], [2, 2]], 'line_type': 'y=1x', 'abc': [1, 2, 0], 'z': 0}, {'line': [[0, 1], [1, 1], [2, 1]], 'line_type': 'y', 'abc': [0, 1, 1], 'z': 1}, {'line': [[0, 1], [1, 2], [2, 0]], 'line_type': 'y=1x', 'abc': [1, 2, 2], 'z': 1}]}`
