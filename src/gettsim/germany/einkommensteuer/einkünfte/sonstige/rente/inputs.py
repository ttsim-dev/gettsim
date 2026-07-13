"""Inputs for Renteneinkünfte."""

from __future__ import annotations

from gettsim.tt import Unit, policy_input


@policy_input(unit=Unit.YEARS)
def alter_beginn_leistungsbezug_sonstige_private_vorsorge() -> int:
    """Age at which pension from `sonstige_private_vorsorge_m` commenced."""


@policy_input(end_date="2004-12-31", unit=Unit.YEARS)
def alter_beginn_leistungsbezug_berufsständische_altersvorsorge() -> int:
    """Age at which pension `aus_berufsständischen_versicherungen_m` commenced."""


@policy_input(end_date="2004-12-31", unit=Unit.YEARS)
def alter_beginn_leistungsbezug_betriebliche_altersvorsorge() -> int:
    """Age at which pension from `betriebliche_altersvorsorge_m` commenced."""
