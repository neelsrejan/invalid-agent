"""Hosted MAUDE table, cache, and read-only questions.

Synthetic scenarios do not import this package on the CI path except through
``load_frame``, which returns the seeded generator when the case says so.
"""

from invalid_agent.data.frame import DataUnavailable, load_frame

__all__ = ["DataUnavailable", "load_frame"]
