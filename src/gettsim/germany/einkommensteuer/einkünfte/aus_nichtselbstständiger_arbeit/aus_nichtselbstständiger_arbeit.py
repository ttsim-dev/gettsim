"""Einkünfte aus nichtselbstständiger Arbeit."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, param_function, policy_function


@policy_function(
    end_date="1999-03-31", leaf_name="betrag_y", unit=TTSIMUnit.CURRENCY.PER_YEAR
)
def betrag_y_bis_03_1999(
    einnahmen_nach_abzug_werbungskosten_y: float,
) -> float:
    """Taxable income from dependent employment.

    Reference: § 2 Abs. 2 Nr. 2 EStG idF B. v. 07.09.1990 BGBl. I S. 1898
    """
    return einnahmen_nach_abzug_werbungskosten_y


@policy_function(
    start_date="1999-04-01", leaf_name="betrag_y", unit=TTSIMUnit.CURRENCY.PER_YEAR
)
def betrag_y_ab_04_1999(
    sozialversicherung__geringfügig_beschäftigt: bool,
    steuerbefreite_einnahmen_y: float,
    einnahmen_nach_abzug_werbungskosten_y: float,
) -> float:
    """Taxable income from dependent employment.

    Special rules for marginal employment have been introduced in April 1999 as part of
    the '630 Mark' job introduction.

    Reference: § 3 Nr. 39 EStG idF Art. 10 G. v. 24.03.1999 BGBl. I S. 388
    """
    if sozialversicherung__geringfügig_beschäftigt:
        return 0.0
    else:
        return max(
            einnahmen_nach_abzug_werbungskosten_y - steuerbefreite_einnahmen_y,
            0.0,
        )


@policy_function(unit=TTSIMUnit.CURRENCY.PER_YEAR)
def einnahmen_nach_abzug_werbungskosten_y(
    einnahmen__bruttolohn_y: float,
    werbungskosten_y: float,
) -> float:
    """Take gross wage and deduct Werbungskosten.

    Reference: § 2 Abs. 2 Nr. 2 EStG idF B. v. 16.04.1997 BGBl. I S. 821
    """
    return max(einnahmen__bruttolohn_y - werbungskosten_y, 0.0)


@policy_function(unit=TTSIMUnit.CURRENCY.PER_YEAR)
def werbungskosten_y(
    tatsächliche_werbungskosten_y: float,
    arbeitnehmerpauschbetrag: float,
    einnahmen__bruttolohn_y: float,
    anteil_steuerfälliger_einnahmen: float,
) -> float:
    """Werbungskosten nach Berücksichtung des Arbeitnehmer-Pauschbetrags.

    Actual Werbungskosten that relate to both taxable and tax-free income are split
    proportionally (§ 3c Abs. 1 EStG). The Arbeitnehmer-Pauschbetrag applies in full —
    without proportional reduction — even when tax-exempt income is present.

    Reference: § 9a Satz 1 Nr. 1 EStG idF Art. 1 G. v. 19.12.2000 BGBl. I S. 1790
    """
    if einnahmen__bruttolohn_y > 0.0:
        anrechenbare_werbungskosten = (
            tatsächliche_werbungskosten_y * anteil_steuerfälliger_einnahmen
        )
    else:
        anrechenbare_werbungskosten = 0.0

    return max(anrechenbare_werbungskosten, arbeitnehmerpauschbetrag)


@policy_function(unit=TTSIMUnit.DIMENSIONLESS)
def anteil_steuerfälliger_einnahmen(
    einnahmen__bruttolohn_y: float,
    steuerbefreite_einnahmen_y: float,
) -> float:
    """Anteil steuerfälliger Einnahmen an Einnahmen aus nichtselbstständiger Arbeit.

    Reference: § 3c Abs. 1 EStG idF Art. 1 G. v. 23.10.2000 BGBl. I S. 1433
    """
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


@param_function(
    end_date="2025-12-31",
    leaf_name="steuerbefreite_einnahmen_y",
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def steuerbefreite_einnahmen_y_bis_2025() -> float:
    """Steuerbefreite Einnahmen aus abhängiger Beschäftigung.

    Not implemented yet. Encompasses mainly Übungsleiterpauschalen, Ehrenamtspauschale,
    etc (see § 3 Nr. 26 EStG).
    """
    return 0.0


@policy_function(
    start_date="2026-01-01",
    leaf_name="steuerbefreite_einnahmen_y",
    unit=TTSIMUnit.CURRENCY.PER_YEAR,
)
def steuerbefreite_einnahmen_y_ab_2026(
    anspruchshöhe_steuerfreibetrag_aktivrente_y: float,
) -> float:
    """Steuerbefreite Einnahmen aus abhängiger Beschäftigung.

    Since 2026, this includes the Aktivrente (§ 3 Nr. 21 EStG).

    Reference: § 3 Nr. 21 Satz 1 EStG idF Art. 1 G. v. 22.12.2025 BGBl. 2025 I Nr. 361
    """
    return anspruchshöhe_steuerfreibetrag_aktivrente_y


@policy_function(start_date="2026-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def anspruchshöhe_steuerfreibetrag_aktivrente_m(
    einnahmen__bruttolohn_m: float,
    sozialversicherung__rente__beitrag__betrag_arbeitgeber_m: float,
    sozialversicherung__geringfügig_beschäftigt: bool,
    steuerfreibetrag_aktivrente_m: float,
    sozialversicherung__rente__altersrente__älter_als_regelaltersgrenze: bool,
) -> float:
    """Steuerfreibetrag 'Aktivrente' nach Anspruchsprüfung.

    The Aktivrente is a special tax deduction for wages earned past the
    Regelaltersgrenze from an employment for which the employer owes pension insurance
    contributions. This includes the isolated employer share for versicherungsfreie
    Vollrentner (§ 172 Abs. 1 SGB VI) but not Minijobs, whose employer contributions
    fall under norms § 3 Nr. 21 EStG does not list (§ 168 Abs. 1 Nr. 1b, § 172 Abs. 3
    SGB VI).

    GETTSIM does not yet model employments without employer pension contributions
    other than Minijobs (e.g. Beamte, Vorstände, kurzfristig Beschäftigte), see
    https://github.com/ttsim-dev/gettsim/issues/1114. These individuals are treated
    as eligible unless `sozialversicherung__rente__beitrag__betrag_arbeitgeber_m` is
    set to zero.

    The Steuerfreibetrag is deducted on a **monthly** basis, i.e. it is not possible to
    to accumulate the Steuerfreibetrag in case one earns less than it in one month and
    then apply a higher Steuerfreibetrag in another month. The claim cannot exceed the
    monthly wage.

    If you want to calculate taxes with income that varies by month, pass the correct
    Aktivrente deduction as an input when calling GETTSIM.

    Reference: § 3 Nr. 21 Satz 1 EStG idF Art. 1 G. v. 22.12.2025 BGBl. 2025 I Nr. 361
    """

    # Past the Regelaltersgrenze, every employment except Minijobs yields a positive
    # employer contribution in GETTSIM: § 168 Abs. 1 Nr. 1 SGB VI if the employee is
    # pflichtversichert, § 172 Abs. 1 SGB VI if versicherungsfrei. The check mirrors
    # the wording of § 3 Nr. 21 EStG and lets users exclude employments without
    # employer contributions by overriding `betrag_arbeitgeber_m`.
    if (
        sozialversicherung__rente__altersrente__älter_als_regelaltersgrenze
        and sozialversicherung__rente__beitrag__betrag_arbeitgeber_m > 0.0
        and not sozialversicherung__geringfügig_beschäftigt
    ):
        return min(einnahmen__bruttolohn_m, steuerfreibetrag_aktivrente_m)
    else:
        return 0.0
