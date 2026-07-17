"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(end_date="2022-12-31", unit=TTSIMUnit.CURRENCY.PER_YEAR)
def höchster_bruttolohn_letzte_15_jahre_vor_rente_y() -> float:
    """Highest gross income from regular employment in the last 15 years before pension
    benefit claiming. Relevant to determine pension benefit deductions for retirees in
    early retirement.
    """
