from __future__ import annotations

import math

__all__ = ["BDError", "N_RUNGS", "bdrate", "bdrint", "pchipend", "is_monotone"]

N_RUNGS = 4


class BDError(ValueError):
    """Raised when a BD-rate cannot be computed from the given samples."""


def _sorted_by_dist(rate, dist, label: str) -> tuple[list[float], list[float]]:
    """Return (rate, dist) as floats sorted by strictly increasing dist.
    """
    rate = [float(r) for r in rate]
    dist = [float(d) for d in dist]

    if len(rate) != len(dist):
        raise BDError(f"{label}: rate and dist must have the same length")
    if len(rate) != N_RUNGS:
        raise BDError(
            f"{label}: the sponsor template is hard-wired to {N_RUNGS} rate "
            f"rungs, got {len(rate)}"
        )
    if any(not math.isfinite(v) for v in rate + dist):
        raise BDError(f"{label}: samples contain NaN or inf")
    if any(r <= 0 for r in rate):
        raise BDError(f"{label}: bitrates must be positive (log10 is taken)")

    pairs = sorted(zip(dist, rate))
    dist_sorted = [d for d, _ in pairs]
    rate_sorted = [r for _, r in pairs]

    if any(b - a <= 0 for a, b in zip(dist_sorted, dist_sorted[1:])):
        raise BDError(
            f"{label}: quality values must be distinct; duplicate scores mean "
            "two rungs landed on the same metric value"
        )
    return rate_sorted, dist_sorted