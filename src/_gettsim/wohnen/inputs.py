"""Input columns."""

from __future__ import annotations

from gettsim.tt import policy_input


@policy_input(end_date="2008-12-31")
def baujahr_immobilie_hh() -> int:
    """Year of construction of the household dwelling."""


@policy_input(start_date="2005-01-01")
def bewohnt_eigentum_hh() -> bool:
    """Owner-occupied housing."""


@policy_input()
def bruttokaltmiete_m_hh() -> float:
    """Rent expenses excluding utilities."""


@policy_input(start_date="2005-01-01")
def heizkosten_m_hh() -> float:
    """Heating expenses."""


@policy_input(start_date="2005-01-01")
def wohnfläche_hh() -> float:
    """Size of household dwelling in square meters."""
