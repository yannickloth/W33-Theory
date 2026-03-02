import THE_EXACT_MAP as exact
from tests.test_mini_mog import row_counts_mod3, tetracode_words

bad = []
for h in exact.hexads:
    rc = row_counts_mod3(h)
    if rc not in tetracode_words():
        bad.append((h, rc))

print("bad count:", len(bad))
for h, rc in bad:
    print(h, rc)
print("\ntetracode sample:", list(tetracode_words())[:6])
