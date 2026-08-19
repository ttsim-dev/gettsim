"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(unit=TTSIMUnit.CURRENCY.PER_YEAR)
def betrag_y() -> float:
    """Yearly rental income net of deductions."""
