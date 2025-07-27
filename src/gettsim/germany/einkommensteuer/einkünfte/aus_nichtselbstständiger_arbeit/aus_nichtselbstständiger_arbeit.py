"""Einkünfte aus nichtselbstständiger Arbeit."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function(end_date="1999-03-31", leaf_name="betrag_y")
def betrag_y_bis_03_1999(
    einnahmen_nach_abzug_werbungskosten_y: float,
) -> float:
    """Taxable income from dependent employment."""
    return einnahmen_nach_abzug_werbungskosten_y


@policy_function(start_date="1999-04-01", leaf_name="betrag_y")
def betrag_y_ab_04_1999(
    einnahmen_nach_abzug_werbungskosten_y: float,
    sozialversicherung__geringfügig_beschäftigt: bool,
) -> float:
    """Taxable income from dependent employment.

    Special rules for marginal employment have been introduced in April 1999 as part of
    the '630 Mark' job introduction.
    """
    if sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = einnahmen_nach_abzug_werbungskosten_y

    return out


@policy_function()
def einnahmen_nach_abzug_werbungskosten_y(
    einnahmen__bruttolohn_y: float,
    werbungskosten_y: float,
) -> float:
    """Take gross wage and deduct Werbungskosten."""
    return max(einnahmen__bruttolohn_y - werbungskosten_y, 0.0)


@policy_function()
def werbungskosten_y(arbeitnehmerpauschbetrag: float) -> float:
    """Arbeitnehmerpauschbetrag."""
    return arbeitnehmerpauschbetrag
