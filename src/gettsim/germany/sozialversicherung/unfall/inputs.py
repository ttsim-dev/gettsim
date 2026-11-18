"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def verletztengeld_m() -> float:
    """Verletztengeld of the statutory accident insurance."""
