"""Input columns."""

from __future__ import annotations

from gettsim.tt import policy_input


@policy_input()
def beitrag_private_rentenversicherung_m() -> float:
    pass


@policy_input()
def kinderbetreuungskosten_m() -> float:
    """Monthly childcare expenses for a particular child under the age of 14."""


@policy_input()
def p_id_kinderbetreuungskostenträger() -> int:
    """Identifier of the person who paid childcare expenses."""
