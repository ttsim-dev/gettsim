"""Midijob."""

from __future__ import annotations

from gettsim.tt import param_function, policy_function


@policy_function(start_date="2003-04-01")
def in_gleitzone(
    einnahmen__bruttolohn_m: float,
    geringfügig_beschäftigt: bool,
    midijobgrenze: float,
) -> bool:
    """Individual's income is in Midijob range.

    Employed people with their wage in the range of Gleitzone pay reduced social
    insurance contributions.

    Legal reference: § 20 Abs. 2 SGB IV

    """
    return (einnahmen__bruttolohn_m <= midijobgrenze) and (not geringfügig_beschäftigt)


@policy_function()
def beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m(
    einnahmen__bruttolohn_m: float,
    minijobgrenze: float,
    midijobgrenze: float,
) -> float:
    """Income subject to employee social insurance contributions for Bruttolöhne in
    Gleitzone.

    Legal reference: § 20 SGB IV ("Gesonderte beitragspflichtige Einnahmen")
    """
    quotient = midijobgrenze / (midijobgrenze - minijobgrenze)
    einkommen_diff = einnahmen__bruttolohn_m - minijobgrenze

    return quotient * einkommen_diff


@param_function(
    start_date="2003-04-01",
    end_date="2004-12-31",
    leaf_name="midijob_faktor_f",
)
def midijob_faktor_f_mit_minijob_steuerpauschale_bis_2004(
    kranken__beitrag__beitragssatz_arbeitnehmer_midijob: float,
    kranken__beitrag__beitragssatz_arbeitgeber_midijob: float,
    rente__beitrag__beitragssatz_jahresanfang: float,
    arbeitslosen__beitrag__beitragssatz_jahresanfang: float,
    pflege__beitrag__beitragssatz_jahresanfang: float,
    lohnsteuer__minijob_arbeitgeberpauschale: float,
    kranken__beitrag__minijob_arbeitgeberpauschale: float,
    rente__beitrag__minijob_arbeitgeberpauschale: float,
) -> float:
    """Midijob Faktor F until December 2004.

    Legal reference: § 163 Abs. 10 SGB VI
    """
    # First calculate the factor F from the formula in § 163 (10) SGB VI
    # Therefore sum the contributions which are the same for employee and employer
    allg_sozialv_beitr = (
        rente__beitrag__beitragssatz_jahresanfang / 2
        + arbeitslosen__beitrag__beitragssatz_jahresanfang / 2
        + pflege__beitrag__beitragssatz_jahresanfang / 2
    )

    # Then calculate specific shares
    an_anteil = allg_sozialv_beitr + kranken__beitrag__beitragssatz_arbeitnehmer_midijob
    ag_anteil = allg_sozialv_beitr + kranken__beitrag__beitragssatz_arbeitgeber_midijob

    # Sum over the shares which are specific for midijobs.
    pausch_mini = (
        kranken__beitrag__minijob_arbeitgeberpauschale
        + rente__beitrag__minijob_arbeitgeberpauschale
        + lohnsteuer__minijob_arbeitgeberpauschale
    )

    # Midijob Faktor F is rounded to 4 decimal places.
    return round(pausch_mini / (an_anteil + ag_anteil), ndigits=4)


@param_function(
    start_date="2005-01-01",
    end_date="2022-09-30",
    leaf_name="midijob_faktor_f",
)
def midijob_faktor_f_mit_minijob_steuerpauschale_ab_2005_bis_2022_09(
    kranken__beitrag__beitragssatz_arbeitnehmer_midijob: float,
    kranken__beitrag__beitragssatz_arbeitgeber_midijob: float,
    rente__beitrag__beitragssatz_jahresanfang: float,
    arbeitslosen__beitrag__beitragssatz_jahresanfang: float,
    pflege__beitrag__beitragssatz_nach_kinderzahl_jahresanfang: dict[str, float],
    lohnsteuer__minijob_arbeitgeberpauschale: float,
    kranken__beitrag__minijob_arbeitgeberpauschale: float,
    rente__beitrag__minijob_arbeitgeberpauschale: float,
) -> float:
    """Midijob Faktor F between 2005 and September 2025.

    Legal reference: § 163 Abs. 10 SGB VI

    """
    # First calculate the factor F from the formula in § 163 (10) SGB VI
    # Therefore sum the contributions which are the same for employee and employer
    allg_sozialv_beitr = (
        rente__beitrag__beitragssatz_jahresanfang / 2
        + arbeitslosen__beitrag__beitragssatz_jahresanfang / 2
        + pflege__beitrag__beitragssatz_nach_kinderzahl_jahresanfang["standard"] / 2
    )

    an_anteil = allg_sozialv_beitr + kranken__beitrag__beitragssatz_arbeitnehmer_midijob
    ag_anteil = allg_sozialv_beitr + kranken__beitrag__beitragssatz_arbeitgeber_midijob

    # Sum over the shares which are specific for midijobs.
    pausch_mini = (
        kranken__beitrag__minijob_arbeitgeberpauschale
        + rente__beitrag__minijob_arbeitgeberpauschale
        + lohnsteuer__minijob_arbeitgeberpauschale
    )

    # Midijob Faktor F is rounded to 4 decimal places.
    return round(pausch_mini / (an_anteil + ag_anteil), ndigits=4)


@param_function(
    start_date="2022-10-01",
    leaf_name="midijob_faktor_f",
)
def midijob_faktor_f_ohne_minijob_steuerpauschale(
    kranken__beitrag__beitragssatz_arbeitnehmer_midijob: float,
    kranken__beitrag__beitragssatz_arbeitgeber_midijob: float,
    rente__beitrag__beitragssatz_jahresanfang: float,
    pflege__beitrag__beitragssatz_nach_kinderzahl_jahresanfang: dict[str, float],
    arbeitslosen__beitrag__beitragssatz_jahresanfang: float,
    kranken__beitrag__minijob_arbeitgeberpauschale: float,
    rente__beitrag__minijob_arbeitgeberpauschale: float,
) -> float:
    """Midijob Faktor F since October 2022.

    Legal reference: § 163 Abs. 10 SGB VI
    """
    # Calculate the Gesamtsozialversicherungsbeitragssatz by summing social
    # insurance contributions for employer and employee and
    # adding the mean Zusatzbeitrag
    # First calculate the factor F from the formula in § 163 (10) SGB VI
    # Therefore sum the contributions which are the same for employee and employer
    allg_sozialv_beitr = (
        rente__beitrag__beitragssatz_jahresanfang / 2
        + pflege__beitrag__beitragssatz_nach_kinderzahl_jahresanfang["standard"] / 2
        + arbeitslosen__beitrag__beitragssatz_jahresanfang / 2
    )

    # Then calculate specific shares
    an_anteil = allg_sozialv_beitr + kranken__beitrag__beitragssatz_arbeitnehmer_midijob
    ag_anteil = allg_sozialv_beitr + kranken__beitrag__beitragssatz_arbeitgeber_midijob

    # Sum over the shares which are specific for midijobs.
    # New formula only inludes the lump-sum contributions to health care
    # and pension insurance
    pausch_mini = (
        kranken__beitrag__minijob_arbeitgeberpauschale
        + rente__beitrag__minijob_arbeitgeberpauschale
    )

    # Midijob Faktor F is rounded to 4 decimal places.
    return round(pausch_mini / (an_anteil + ag_anteil), ndigits=4)


@policy_function(
    start_date="2003-04-01",
    end_date="2022-09-30",
    leaf_name="midijob_bemessungsentgelt_m",
)
def midijob_bemessungsentgelt_m_bis_09_2022(
    einnahmen__bruttolohn_m: float,
    midijob_faktor_f: float,
    minijobgrenze: float,
    midijobgrenze: float,
) -> float:
    """Income subject to social insurance contributions for midijob until September
    2022.

    Bemessungsgeld (Gleitzonenentgelt) is the reference income for midijobs subject to
    social insurance contribution.

    Legal reference: § 163 Abs. 10 SGB VI

    """
    # Now use the factor to calculate the overall bemessungsentgelt
    minijob_anteil = midijob_faktor_f * minijobgrenze
    lohn_über_mini = einnahmen__bruttolohn_m - minijobgrenze
    gewichtete_midijob_rate = (midijobgrenze / (midijobgrenze - minijobgrenze)) - (
        minijobgrenze / (midijobgrenze - minijobgrenze) * midijob_faktor_f
    )

    return minijob_anteil + lohn_über_mini * gewichtete_midijob_rate


@policy_function(start_date="2022-10-01", leaf_name="midijob_bemessungsentgelt_m")
def midijob_bemessungsentgelt_m_ab_10_2022(
    einnahmen__bruttolohn_m: float,
    midijob_faktor_f: float,
    minijobgrenze: float,
    midijobgrenze: float,
) -> float:
    """Total income subject to social insurance contributions for midijobs since October
    2022.

    In the law, the considered income is referred to as "beitragspflichtige Einnahme".

    Beitragspflichtige Einnahme is the reference income for midijobs subject to employer
    and employee social insurance contribution.

    Legal reference: Changes in § 20 SGB IV from 01.10.2022

    """
    quotient1 = (midijobgrenze) / (midijobgrenze - minijobgrenze)
    quotient2 = (minijobgrenze) / (midijobgrenze - minijobgrenze)
    einkommen_diff = einnahmen__bruttolohn_m - minijobgrenze

    faktor1 = midijob_faktor_f * minijobgrenze
    faktor2 = (quotient1 - quotient2 * midijob_faktor_f) * einkommen_diff

    return faktor1 + faktor2
