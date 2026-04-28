"""Einkünfte aus nichtselbstständiger Arbeit."""

from __future__ import annotations

from gettsim.tt import param_function, policy_function


@policy_function(end_date="1999-03-31", leaf_name="betrag_y")
def betrag_y_bis_03_1999(
    einnahmen_nach_abzug_werbungskosten_y: float,
) -> float:
    """Taxable income from dependent employment."""
    return einnahmen_nach_abzug_werbungskosten_y


@policy_function(start_date="1999-04-01", leaf_name="betrag_y")
def betrag_y_ab_04_1999(
    sozialversicherung__geringfügig_beschäftigt: bool,
    steuerbefreite_einnahmen_y: float,
    einnahmen_nach_abzug_werbungskosten_y: float,
) -> float:
    """Taxable income from dependent employment.

    Special rules for marginal employment have been introduced in April 1999 as part of
    the '630 Mark' job introduction.
    """
    if sozialversicherung__geringfügig_beschäftigt:
        return 0.0
    else:
        return max(
            einnahmen_nach_abzug_werbungskosten_y - steuerbefreite_einnahmen_y,
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
def werbungskosten_y(
    tatsächliche_werbungskosten_y: float,
    arbeitnehmerpauschbetrag: float,
    einnahmen__bruttolohn_y: float,
    anteil_steuerfälliger_einnahmen_y: float,
) -> float:
    """Werbungskosten nach Berücksichtung des Arbeitnehmer-Pauschbetrags.

    Actual Werbungskosten that relate to both taxable and tax-free income are split
    proportionally (§ 3c Abs. 1 EStG). The Arbeitnehmer-Pauschbetrag applies in full —
    without proportional reduction — even when tax-exempt income is present.
    """
    if einnahmen__bruttolohn_y > 0.0:
        anrechenbare_werbungskosten = (
            tatsächliche_werbungskosten_y * anteil_steuerfälliger_einnahmen_y
        )
    else:
        anrechenbare_werbungskosten = 0.0

    return max(anrechenbare_werbungskosten, arbeitnehmerpauschbetrag)


@policy_function()
def anteil_steuerfälliger_einnahmen_y(
    einnahmen__bruttolohn_y: float,
    steuerbefreite_einnahmen_y: float,
) -> float:
    """Anteil steuerfälliger Einnahmen an Einnahmen aus nichtselbstständiger Arbeit."""
    if einnahmen__bruttolohn_y > 0.0:
        return (
            max(
                einnahmen__bruttolohn_y - steuerbefreite_einnahmen_y,
                0.0,
            )
            / einnahmen__bruttolohn_y
        )
    else:
        return 0.0


@param_function(end_date="2025-12-31", leaf_name="steuerbefreite_einnahmen_y")
def steuerbefreite_einnahmen_y_bis_2025() -> float:
    """Steuerbefreite Einnahmen aus abhängiger Beschäftigung.

    Not implemented yet. Encompasses mainly Übungsleiterpauschalen, Ehrenamtspauschale,
    etc (see § 3 Nr. 26 EStG).
    """
    return 0.0


@policy_function(start_date="2026-01-01", leaf_name="steuerbefreite_einnahmen_y")
def steuerbefreite_einnahmen_y_ab_2026(
    anspruchshöhe_steuerfreibetrag_aktivrente_y: float,
) -> float:
    """Steuerbefreite Einnahmen aus abhängiger Beschäftigung.

    Since 2026, this includes the Aktivrente (§ 3 Abs. 21 EStG).
    """
    return anspruchshöhe_steuerfreibetrag_aktivrente_y


@policy_function(start_date="2026-01-01")
def anspruchshöhe_steuerfreibetrag_aktivrente_m(
    sozialversicherung__rente__beitrag__betrag_versicherter_m: float,
    steuerfreibetrag_aktivrente_m: float,
    sozialversicherung__rente__altersrente__älter_als_regelaltersgrenze: bool,
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
    if (
        sozialversicherung__rente__altersrente__älter_als_regelaltersgrenze
        and pays_contributions_to_pension_insurance
    ):
        return steuerfreibetrag_aktivrente_m
    else:
        return 0.0
