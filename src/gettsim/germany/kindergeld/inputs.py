"""Input columns."""

from __future__ import annotations

from gettsim.tt import FKType, TTSIMUnit, policy_input


@policy_input(unit=TTSIMUnit.DIMENSIONLESS)
def in_ausbildung() -> bool:
    """In education according to Kindergeld definition."""


@policy_input(foreign_key_type=FKType.MAY_POINT_TO_SELF, unit=TTSIMUnit.DIMENSIONLESS)
def p_id_empfänger() -> int:
    """Identifier of person who receives Kindergeld for the particular child."""
