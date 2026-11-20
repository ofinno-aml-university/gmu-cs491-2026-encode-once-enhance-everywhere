"""Tests for the frame, segment, and bitrate math."""

from fractions import Fraction

import pytest

from packager import frame_math


def test_parse_frame_rate_fraction_and_whole_number():
    assert frame_math.parse_frame_rate("30000/1001") == Fraction(30000, 1001)
    assert frame_math.parse_frame_rate("25") == Fraction(25)


@pytest.mark.parametrize("bad", ["0/0", "abc", "0", "-24"])
def test_parse_frame_rate_rejects_bad_input(bad):
    with pytest.raises(ValueError):
        frame_math.parse_frame_rate(bad)


@pytest.mark.parametrize(
    "rate, expected",
    [("30000/1001", 60), ("25", 50), ("24", 48), ("24000/1001", 48), ("60", 120)],
)
def test_gop_frames_is_two_seconds_rounded(rate, expected):
    rate = frame_math.parse_frame_rate(rate)
    assert frame_math.gop_frames(rate, 2) == expected


def test_gop_frames_rejects_zero_seconds():
    with pytest.raises(ValueError):
        frame_math.gop_frames(Fraction(24), 0)


def test_segment_ranges_exact_multiple():
    assert frame_math.segment_ranges(120, 60) == [(0, 59), (60, 119)]


def test_segment_ranges_short_last_segment():
    assert frame_math.segment_ranges(130, 60) == [(0, 59), (60, 119), (120, 129)]


def test_segment_ranges_cover_every_frame_once():
    ranges = frame_math.segment_ranges(301, 50)
    frames = [frame for start, end in ranges for frame in range(start, end + 1)]
    assert frames == list(range(301))


@pytest.mark.parametrize("total, size", [(0, 60), (10, 0), (-5, 10)])
def test_segment_ranges_rejects_bad_input(total, size):
    with pytest.raises(ValueError):
        frame_math.segment_ranges(total, size)


def test_bitrate_kbps():
    # 750,000 bytes over 10 seconds is 600 kbps.
    assert frame_math.bitrate_kbps(750_000, 10) == pytest.approx(600)


def test_bitrate_kbps_rejects_zero_duration():
    with pytest.raises(ValueError):
        frame_math.bitrate_kbps(1000, 0)


def test_within_tolerance():
    assert frame_math.within_tolerance(620, 600, 0.05)
    assert frame_math.within_tolerance(570, 600, 0.05)
    assert not frame_math.within_tolerance(640, 600, 0.05)
