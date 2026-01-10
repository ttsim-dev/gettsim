"""Einkünfte aus nichtselbstständiger Arbeit."""

from __future__ import annotations

from ttsim.unit_converters import m_to_y, y_to_m

from gettsim.tt import policy_function


@policy_function(end_date="1999-03-31", leaf_name="betrag_y")
def betrag_y_bis_03_1999(
    einnahmen_nach_abzug_werbungskosten_y: float,
) -> float:
    """Taxable income from dependent employment."""
    return einnahmen_nach_abzug_werbungskosten_y


@policy_function(start_date="1999-04-01", end_date="2025-12-31", leaf_name="betrag_y")
def betrag_y_ab_04_1999_bis_2025(
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


@policy_function(start_date="2026-01-01", leaf_name="betrag_y")
def betrag_y_ab_01_2026(
    sozialversicherung__geringfügig_beschäftigt: bool,
    anspruchshöhe_steuerfreibetrag_aktivrente_y: float,
    einnahmen_nach_abzug_werbungskosten_y: float,
) -> float:
    """Taxable income from dependent employment."""
    if sozialversicherung__geringfügig_beschäftigt:
        return 0.0
    else:
        return max(
            einnahmen_nach_abzug_werbungskosten_y
            - anspruchshöhe_steuerfreibetrag_aktivrente_y,
            0.0,
        )


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


@policy_function(start_date="2026-01-01")
def anspruchshöhe_steuerfreibetrag_aktivrente_m(
    sozialversicherung__rente__beitrag__betrag_versicherter_m: float,
    alter_monate: int,
    sozialversicherung__rente__altersrente__regelaltersrente__altersgrenze: float,
    steuerfreibetrag_aktivrente_m: float,
) -> float:
    """Steuerfreibetrag 'Aktivrente' nach Anspruchsprüfung.

    The Aktivrente is a special tax deduction for workers who are
        - older than the Normal Retirement Age
        - the source of income is a 'rentenversicherungspflichtiges
          Beschäftigungsverhältnis'

    The Steuerfreibetrag is deducted on a **monthly** basis, i.e. it is not possible to
    to accumulate the Steuerfreibetrag in case one earns less than it in one month and
    then apply a higher Steuerfreibetrag in another month.

    If you want to calculate taxes with income that varies by month, pass the correct
    Aktivrente deduction as an input when calling GETTSIM.

    Reference: § 3 Abs. 21 EStG.
    """
    pays_contributions_to_pension_insurance = (
        sozialversicherung__rente__beitrag__betrag_versicherter_m > 0.0
    )
    older_than_regelaltersgrenze = (
        alter_monate > y_to_m(sozialversicherung__rente__altersrente__regelaltersrente__altersgrenze)
    )
    if older_than_regelaltersgrenze and pays_contributions_to_pension_insurance:
        return steuerfreibetrag_aktivrente_m
    else:
        return 0.0
