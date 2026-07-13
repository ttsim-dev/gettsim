"""Input columns."""

from __future__ import annotations

from gettsim.tt import FKType, Unit, policy_input


@policy_input(unit=Unit.DIMENSIONLESS)
def in_ausbildung() -> bool:
    """In education according to Kindergeld definition."""


@policy_input(foreign_key_type=FKType.MAY_POINT_TO_SELF, unit=Unit.DIMENSIONLESS)
def p_id_empfänger() -> int:
    """Identifier of person who receives Kindergeld for the particular child."""
