"""A fake clock so retry/backoff code runs instantly in the browser.

The harness installs it before every run: `time.sleep(n)` records `n` and
advances a virtual offset instead of blocking, and `time.time()` /
`time.monotonic()` include that offset. Learner code keeps using the real
`time` module API, so it works unchanged outside the course.
"""

import time as _time

_real_time = _time.time
_real_monotonic = _time.monotonic
_real_sleep = _time.sleep

sleeps = []      # every requested sleep, in seconds
_offset = 0.0


def reset():
    global _offset
    sleeps.clear()
    _offset = 0.0


def advance(seconds):
    """Move virtual time forward without recording a sleep (used by simulators)."""
    global _offset
    _offset += seconds


def _sleep(seconds):
    if seconds < 0:
        raise ValueError("sleep length must be non-negative")
    sleeps.append(seconds)
    advance(seconds)


def _now():
    return _real_time() + _offset


def _monotonic():
    return _real_monotonic() + _offset


def install():
    _time.sleep = _sleep
    _time.time = _now
    _time.monotonic = _monotonic
