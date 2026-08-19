"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(end_date="2008-12-31", unit=TTSIMUnit.CALENDAR_YEAR.PER_HH)
def baujahr_immobilie_hh() -> int:
    """Year of construction of the household dwelling."""


@policy_input(start_date="2005-01-01", unit=TTSIMUnit.DIMENSIONLESS.PER_HH)
def bewohnt_eigentum_hh() -> bool:
    """Owner-occupied housing."""


@policy_input(unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_HH)
def bruttokaltmiete_m_hh() -> float:
    """Rent expenses excluding utilities."""


@policy_input(start_date="2005-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_HH)
def heizkosten_m_hh() -> float:
    """Heating expenses."""


@policy_input(start_date="2005-01-01", unit=TTSIMUnit.SQUARE_METER.PER_HH)
def wohnfläche_hh() -> float:
    """Size of household dwelling in square meters."""
