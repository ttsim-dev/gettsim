"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(unit=TTSIMUnit.DIMENSIONLESS)
def steuerklasse() -> int:
    """Tax Bracket (1 to 5) for withholding tax."""
