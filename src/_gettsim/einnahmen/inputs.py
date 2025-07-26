"""Input columns."""

from __future__ import annotations

from gettsim.tt import policy_input


@policy_input()
def bruttolohn_m() -> float:
    """Income (Einnahmen) from non-self-employment."""


@policy_input()
def kapitalerträge_y() -> float:
    """Income (Einnahmen) from capital income."""
