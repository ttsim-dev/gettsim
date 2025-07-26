"""Input columns."""

from __future__ import annotations

from gettsim.tt import policy_input


@policy_input()
def kapitalerträge_m() -> float:
    """Income (Einnahmen) from capital income."""
