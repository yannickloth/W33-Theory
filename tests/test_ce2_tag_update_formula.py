"""
Test suite for CE2 Tag Update Formula
Validates tag_update_formula against the transition table.
"""

import pytest
from ce2_tag_update_formula import tag_update_formula
from scripts.ce2_kernel_action import build_kernel_tables, tag_list, pattern_list

pattern_index, tag_index, action1, action2 = build_kernel_tables()
tags = tag_list()
patterns = pattern_list()

@pytest.mark.parametrize("axis_swap", [0, 1])
def test_tag_update_formula(axis_swap):
    for tag_idx in range(len(tags)):
        for pattern_idx in range(len(patterns)):
            if axis_swap == 0:
                expected = action1[tag_idx][pattern_idx]
            else:
                expected = action2[tag_idx][pattern_idx]
            actual = tag_update_formula(tag_idx, pattern_idx, axis_swap)
            assert actual == expected, f"Mismatch: tag {tag_idx}, pattern {pattern_idx}, swap {axis_swap}"
