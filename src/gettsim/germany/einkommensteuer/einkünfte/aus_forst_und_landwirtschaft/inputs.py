"""Input columns."""

from __future__ import annotations

from gettsim.tt import Unit, policy_input


@policy_input(unit=Unit.CURRENCY.PER_YEAR)
def betrag_y() -> float:
    """Yearly income from forestry and agriculture."""
