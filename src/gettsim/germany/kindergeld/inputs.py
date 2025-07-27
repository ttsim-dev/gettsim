"""Input columns."""

from __future__ import annotations

from gettsim.tt import FKType, policy_input


@policy_input()
def in_ausbildung() -> bool:
    """In education according to Kindergeld definition."""


@policy_input(foreign_key_type=FKType.MAY_POINT_TO_SELF)
def p_id_empfänger() -> int:
    """Identifier of person who receives Kindergeld for the particular child."""
