"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def krankengeld_m() -> float:
    """Krankengeld received."""


@policy_input(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def mutterschaftsgeld_m() -> float:
    """Mutterschaftsgeld including the Zuschuss zum Mutterschaftsgeld."""
