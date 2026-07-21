from __future__ import annotations

from gettsim.tt import TTSIMUnit, cast_ttsim_unit, policy_function


@policy_function(unit=TTSIMUnit.DIMENSIONLESS)
def alter_bis_24(alter: int) -> bool:
    """Age is 24 years at most.

    Trivial, but necessary in order to use the target for aggregation.
    """
    return alter <= cast_ttsim_unit(24, TTSIMUnit.YEARS)
