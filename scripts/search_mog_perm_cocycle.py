"""Find MOG column/row permutations that maximize cocycle pass rate.

Search space: column permutations (4!) × intra-column reorderings (3!^4 ≈ 1296)
Total ≈ 24 * 1296 = 31104 — quick to evaluate.

Outputs best permutation and its cocycle pass rate; writes `artifacts/mog_perm_best.json`.
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

random.seed(1)

# columns as used in THE_EXACT_MAP
columns = [[0, 4, 8], [1, 5, 9], [2, 6, 10], [3, 7, 11]]


# scoring re-implementation (same logic as tune_line_reps)
def score_for_current_mapping():
    sample = random.sample(exact.weight_6, 50)
    cocycle_pass = 0
    cocycle_fail = 0
    for a in sample[:15]:
        for b in sample[:15]:
            for c in sample[:15]:
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


best = {
    "pass": -1,
    "fail": 0,
    "rate": 0.0,
    "mapping": None,
    "col_perm": None,
    "intra_choice": None,
}
col_perms = list(permutations(range(4)))
# precompute all intra-column permutations (list of 4-tuples of permutations)
intra_perms = list(product(*[list(permutations(col)) for col in columns]))

print(
    f"Searching {len(col_perms) * len(intra_perms):,} MOG permutations (columns × intra-column orders)..."
)
count = 0
for col_perm in col_perms:
    for intra_choice in intra_perms:
        # build perm_map: old_pos -> new_pos
        perm_map = {}
        for new_col_idx, old_col_idx in enumerate(col_perm):
            new_col = columns[new_col_idx]
            old_col = list(intra_choice[old_col_idx])
            for new_row_idx in range(3):
                old_pos = old_col[new_row_idx]
                new_pos = new_col[new_row_idx]
                perm_map[old_pos] = new_pos

        # build permuted pos_to_line mapping
        pos_to_line_perm = {i: exact.pos_to_line_mog[perm_map[i]] for i in range(12)}
        # monkeypatch module mapping
        exact.pos_to_line_mog = pos_to_line_perm

        p, f = score_for_current_mapping()
        total = p + f
        rate = p / total if total else 0.0
        if p > best["pass"] or (p == best["pass"] and rate > best["rate"]):
            best.update(
                {
                    "pass": p,
                    "fail": f,
                    "rate": rate,
                    "mapping": [pos_to_line_perm[i] for i in range(12)],
                    "col_perm": col_perm,
                    "intra_choice": [[int(x) for x in tup] for tup in intra_choice],
                }
            )
        count += 1

# restore original mapping
exact.pos_to_line_mog = exact.build_mog_map()

print("\nSearch finished.")
print(
    f"Best pass: {best['pass']} / {best['pass']+best['fail']} => {best['rate']*100:.2f}%"
)
print("col_perm:", best["col_perm"])
print("intra_choice (per column):", best["intra_choice"])
print("mapping (0..11 -> line):", best["mapping"])

Path("artifacts").mkdir(exist_ok=True)
Path("artifacts/mog_perm_best.json").write_text(json.dumps(best, indent=2))
print("\nWrote artifacts/mog_perm_best.json")
