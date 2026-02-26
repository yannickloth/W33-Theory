"""
CE2 Tag Update Formula

This module attempts to express the tag-update rule for the CE2 kernel axis-swap/growth as an explicit algebraic formula.
If a closed-form formula is not possible, it falls back to lookup.
"""


from scripts.ce2_kernel_action import build_kernel_tables, tag_list, pattern_list

# Unpack kernel tables
pattern_index, tag_index, action1, action2 = build_kernel_tables()
tags = tag_list()
patterns = pattern_list()

def tag_update_formula(tag_idx, pattern_idx, axis_swap):
    """
    Given tag index, pattern index, and axis_swap (0 or 1),
    return the next tag index according to the transition table.
    If a closed-form formula is found, replace this logic.
    """
    # Fallback: lookup from action tables
    if axis_swap == 0:
        return action1[tag_idx][pattern_idx]
    else:
        return action2[tag_idx][pattern_idx]

# TODO: Attempt to derive closed-form formula for tag update
# If possible, replace tag_update_formula with explicit algebraic rule

if __name__ == "__main__":
    # Demo: print all tag transitions for axis_swap=0
    for tag_idx in range(len(tags)):
        for pattern_idx in range(len(patterns)):
            next_tag = tag_update_formula(tag_idx, pattern_idx, 0)
            print(f"tag {tag_idx} + pattern {pattern_idx} (swap=0) -> {next_tag}")
