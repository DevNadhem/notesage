import pytest

from notesage.calibrate import suggest_threshold


def test_suggests_midpoint_of_the_gap():
    low, high, mid = suggest_threshold([0.4, 0.3], [0.1, 0.15])
    assert (low, high) == (0.3, 0.15)
    assert mid == pytest.approx(0.225)


def test_overlapping_ranges_are_still_reported():
    low, high, _ = suggest_threshold([0.2, 0.5], [0.3])
    assert low < high


def test_empty_scores_raise():
    with pytest.raises(ValueError):
        suggest_threshold([], [0.1])
    with pytest.raises(ValueError):
        suggest_threshold([0.4], [])