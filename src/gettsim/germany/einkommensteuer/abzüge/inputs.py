"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def beitrag_private_rentenversicherung_m() -> float:
    pass


@policy_input(unit=TTSIMUnit.CURRENCY.PER_MONTH)
def kinderbetreuungskosten_m() -> float:
    """Monthly childcare expenses for a particular child under the age of 14."""


@policy_input(unit=TTSIMUnit.DIMENSIONLESS)
def p_id_kinderbetreuungskostenträger() -> int:
    """Identifier of the person who paid childcare expenses."""
