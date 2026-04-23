"""Inputs for Renteneinkünfte."""

from __future__ import annotations

from gettsim.tt import policy_input


@policy_input()
def alter_beginn_leistungsbezug_sonstige_private_vorsorge_ertragsanteil_besteuert() -> (
    int
):
    """Age at which benefits from private pensions taxed via Ertragsanteil commenced.

    Applies to Private Rentenversicherung and annuitized Kapitallebensversicherung.
    Determines the Ertragsanteil per § 22 Nr. 1 Satz 3 Buchst. a Doppelbuchst. bb EStG.
    """


@policy_input(end_date="2004-12-31")
def alter_beginn_leistungsbezug_berufsständische_altersvorsorge() -> int:
    """Age at which benefits from the professional pension scheme commenced."""


@policy_input(end_date="2004-12-31")
def alter_beginn_leistungsbezug_betriebliche_altersvorsorge() -> int:
    """Age at which benefits from the occupational pension scheme commenced."""
