from __future__ import annotations

from gettsim.tt import Unit, cast_unit, policy_function


@policy_function(unit=Unit.DIMENSIONLESS)
def alter_bis_24(alter: int) -> bool:
    """Age is 24 years at most.

    Trivial, but necessary in order to use the target for aggregation.
    """
    return cast_unit(alter, Unit.DIMENSIONLESS) <= 24  # noqa: PLR2004
