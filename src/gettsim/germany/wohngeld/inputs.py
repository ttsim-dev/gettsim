"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(unit=TTSIMUnit.DIMENSIONLESS.PER_HH)
def mietstufe_hh() -> int:
    """Municipality's rent classification."""
