"""Input columns."""

from __future__ import annotations

from gettsim.tt import policy_input


@policy_input()
def bruttolohn_m() -> float:
    """Monthly wage."""
