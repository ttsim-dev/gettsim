"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(unit=TTSIMUnit.DIMENSIONLESS)
def teilweise_erwerbsgemindert() -> bool:
    """Able to provide at least 3 but no more than 6 hours of market labor per day."""


@policy_input(unit=TTSIMUnit.DIMENSIONLESS)
def voll_erwerbsgemindert() -> bool:
    """Unable to provide more than 3 hours of market labor per day.."""
