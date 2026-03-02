# SP43 → WE6_TRUE Breakthrough Certificate (PSp(4,3) level)

This bundle constructs an explicit isomorphism from the repo’s `sp43_edgepair_generators.json` action (degree 120, order 25920) into the **true** WE6-even action on E8 roots/lines from `we6_true_action.json`.

Key facts verified:
- |G_sp43| = 25920; |G_we6_even_on_lines| = 25920.
- Element-order spectrum matches exactly (same counts for orders 1,2,3,4,5,6,9,12).
- Each mapped generator’s induced E8-root permutation preserves antipodes and the full dot-product matrix (so it is a genuine E8 root-system isometry).
- The induced line-level sign cocycle (with canonical line reps) is trivial for these 10 generators (so the lift is consistent).

Files:
- `sp43_to_we6even_word_map.json`: each sp43 generator as a word in WE6-even generators (+ inverses).
- `sp43_root_perms_fixed.json`: the resulting 240-root permutations (0-based).
- `sp43_line_perms_fixed.json`, `sp43_line_eps_fixed.json`: induced 120-line perms and per-line epsilon signs.
- `verification_summary.json`: checks and counts.