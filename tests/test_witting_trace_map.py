import collections

import pytest

from tools import witting_trace_map_pg32_full as wtm


def test_witting_trace_map_full_counts():
    vertices = wtm.build_vertices()
    assert len(vertices) == 240

    images = [wtm.trace_map(v) for v in vertices]
    counts = collections.Counter(images)

    # Marcelis claim / our empirical result: 15 unique GF(2) projective images
    assert len(counts) == 15

    # each image should appear exactly 16 times (240/15)
    assert all(c == 16 for c in counts.values())
