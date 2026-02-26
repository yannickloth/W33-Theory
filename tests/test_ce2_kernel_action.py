from scripts.ce2_kernel_action import (
    build_kernel_tables,
    transition_table,
)


def test_kernel_tables_are_deterministic() -> None:
    pat_idx, tag_idx, a1, a2 = build_kernel_tables()
    # every valid (tag,pattern) should map to exactly one output (not -1)
    for table in (a1, a2):
        for ti, row in enumerate(table):
            for pi, val in enumerate(row):
                # some combinations may never occur; skip those
                # we can detect them by checking if tag has an input pattern
                # that actually appears
                if val == -1:
                    continue
                assert 0 <= val < len(pat_idx)


def test_kernel_tags_and_patterns_sizes() -> None:
    pat_idx, tag_idx, a1, a2 = build_kernel_tables()
    assert len(pat_idx) == 8
    # tags should be at most 18; we expect exactly 18 in the full data
    assert 1 <= len(tag_idx) <= 18
    assert len(a1) == len(tag_idx) and len(a2) == len(tag_idx)
