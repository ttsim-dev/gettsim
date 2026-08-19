"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def bruttolohn_m() -> float:
    """Income (Einnahmen) from non-self-employment."""


@policy_input(unit=TTSIMUnit.CURRENCY.PER_YEAR)
def kapitalerträge_y() -> float:
    """Income (Einnahmen) from capital income."""
