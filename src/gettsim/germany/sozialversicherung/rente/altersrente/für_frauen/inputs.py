"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(end_date="2017-12-31", unit=TTSIMUnit.YEARS)
def pflichtsbeitragsjahre_ab_alter_40() -> float:
    """Total years of mandatory contributions after age 40."""
