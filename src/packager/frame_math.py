"""Frame, segment, and bitrate math for the packager. No FFmpeg in here."""

from fractions import Fraction


def parse_frame_rate(text):
    """Turn a frame rate like "30000/1001" or "25" into an exact fraction."""
    try:
        rate = Fraction(text)
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError(f"Bad frame rate: {text!r}") from error
    if rate <= 0:
        raise ValueError(f"Frame rate must be positive, got {text!r}")
    return rate


def gop_frames(frame_rate, gop_seconds):
    """Return the GOP length in frames: gop_seconds of video, rounded.

    30000/1001 fps with a 2 second GOP gives 60 (about 2.002 seconds).
    """
    if gop_seconds <= 0:
        raise ValueError(f"gop_seconds must be positive, got {gop_seconds}")
    return max(1, round(frame_rate * gop_seconds))


def segment_ranges(total_frames, segment_frames):
    """Split a clip into (start_frame, end_frame) pairs, both ends included.

    The last segment is shorter when the clip is not an exact multiple.
    """
    if total_frames <= 0:
        raise ValueError(f"total_frames must be positive, got {total_frames}")
    if segment_frames <= 0:
        raise ValueError(f"segment_frames must be positive, got {segment_frames}")
    ranges = []
    for start in range(0, total_frames, segment_frames):
        end = min(start + segment_frames, total_frames) - 1
        ranges.append((start, end))
    return ranges


def bitrate_kbps(size_bytes, duration_s):
    """Return the average bitrate in kilobits per second."""
    if duration_s <= 0:
        raise ValueError(f"duration_s must be positive, got {duration_s}")
    return size_bytes * 8 / duration_s / 1000


def within_tolerance(achieved_kbps, target_kbps, tolerance):
    """Say whether the achieved bitrate is within tolerance of the target.

    tolerance is a fraction, so 0.05 means 5 percent.
    """
    if target_kbps <= 0:
        raise ValueError(f"target_kbps must be positive, got {target_kbps}")
    return abs(achieved_kbps - target_kbps) / target_kbps <= tolerance
