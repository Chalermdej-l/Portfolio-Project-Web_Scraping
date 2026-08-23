"""Tests for the sharding math used by the worker launcher."""

from src.runner import compute_ranges


def test_even_split():
    assert compute_ranges(100, 10) == [
        (0, 10),
        (10, 20),
        (20, 30),
        (30, 40),
        (40, 50),
        (50, 60),
        (60, 70),
        (70, 80),
        (80, 90),
        (90, 100),
    ]


def test_uneven_split_gives_remainder_to_last_node():
    assert compute_ranges(10, 3) == [(0, 3), (3, 6), (6, 10)]


def test_single_node():
    assert compute_ranges(5, 1) == [(0, 5)]


def test_more_nodes_than_records():
    assert compute_ranges(1, 10) == [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 1)]


def test_ranges_are_contiguous():
    for total in (1, 7, 99, 100, 101, 1973):
        for nodes in (1, 2, 3, 10, 20):
            ranges = compute_ranges(total, nodes)
            assert len(ranges) == nodes
            assert ranges[0][0] == 0
            assert ranges[-1][1] == total
            for (start_a, end_a), (start_b, end_b) in zip(ranges, ranges[1:]):
                assert end_a == start_b


def test_degenerate_tail_shard_when_nodes_exceed_records():
    # Original algorithm: round(7/10) = 1 per node, so the tail shard is (9, 7).
    # Python slicing treats that as an empty range, so no URLs are lost.
    assert compute_ranges(7, 10) == [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 7)]
