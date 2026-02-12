"""Search only intra-column reorderings (3!^4 = 1296) for best cocycle score.
Faster than full column+intra search; good first pass.
"""

import json
import random
import sys
from itertools import permutations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import THE_EXACT_MAP as exact

random.seed(2)

columns = [[0, 4, 8], [1, 5, 9], [2, 6, 10], [3, 7, 11]]

# scoring


def score_current():
    sample = random.sample(exact.weight_6, 40)
    cocycle_pass = 0
    cocycle_fail = 0
    for a in sample[:12]:
        for b in sample[:12]:
            for c in sample[:12]:
                if a != b and b != c and a != c:
                    bc = exact.add(b, c)
                    ca = exact.add(c, a)
                    ab = exact.add(a, b)
                    if bc != exact.zero and ca != exact.zero and ab != exact.zero:
                        s1 = exact.symplectic_sign(a, bc) * exact.symplectic_sign(b, c)
                        s2 = exact.symplectic_sign(b, ca) * exact.symplectic_sign(c, a)
                        s3 = exact.symplectic_sign(c, ab) * exact.symplectic_sign(a, b)
                        if s1 == s2 == s3:
                            cocycle_pass += 1
                        else:
                            cocycle_fail += 1
    return cocycle_pass, cocycle_fail


best = {"pass": -1, "fail": 0, "mapping": None, "intra_choice": None}
all_intra = list(product(*[list(permutations(col)) for col in columns]))
print(f"Testing {len(all_intra)} intra-column permutations...")
for intra_choice in all_intra:
    perm_map = {}
    # only identity column ordering
    for col_idx, old_col in enumerate(intra_choice):
        new_col = columns[col_idx]
        for row_idx in range(3):
            old_pos = old_col[row_idx]
            new_pos = new_col[row_idx]
            perm_map[old_pos] = new_pos
    pos_to_line_perm = {i: exact.pos_to_line_mog[perm_map[i]] for i in range(12)}
    exact.pos_to_line_mog = pos_to_line_perm
    p, f = score_current()
    if p > best["pass"]:
        best.update(
            {
                "pass": p,
                "fail": f,
                "mapping": [pos_to_line_perm[i] for i in range(12)],
                "intra_choice": [[int(x) for x in tup] for tup in intra_choice],
            }
        )

# restore
exact.pos_to_line_mog = exact.build_mog_map()
print("\nDone. Best:")
print(
    f"  pass: {best['pass']} / {best['pass']+best['fail']} => {best['pass']/(best['pass']+best['fail'])*100:.2f}%"
)
print("intra_choice:", best["intra_choice"])
print("mapping:", best["mapping"])

Path("artifacts").mkdir(exist_ok=True)
Path("artifacts/mog_intra_best.json").write_text(json.dumps(best, indent=2))
print("\nWrote artifacts/mog_intra_best.json")
