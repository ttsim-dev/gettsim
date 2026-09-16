"""Contributions to the unemployment insurance."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_function


@policy_function(
    end_date="1999-03-31",
    leaf_name="betrag_versicherter_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_versicherter_m_bis_03_1999(
    sozialversicherung__rente__altersrente__älter_als_regelaltersgrenze: bool,
    sozialversicherung__rente__beitrag__einkommen_m: float,
    beitragssatz: float,
) -> float:
    """Unemployment insurance contributions paid by the insured person.

    Reaching the Regelaltersgrenze exempts from unemployment insurance regardless of
    whether a pension is drawn (§ 28 Abs. 1 Nr. 1 SGB III).
    """
    if sozialversicherung__rente__altersrente__älter_als_regelaltersgrenze:
        out = 0.0
    else:
        out = sozialversicherung__rente__beitrag__einkommen_m * beitragssatz / 2

    return out


@policy_function(
    start_date="1999-04-01",
    end_date="2003-03-31",
    leaf_name="betrag_versicherter_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_versicherter_m_ohne_midijob(
    sozialversicherung__geringfügig_beschäftigt: bool,
    sozialversicherung__rente__altersrente__älter_als_regelaltersgrenze: bool,
    sozialversicherung__rente__beitrag__einkommen_m: float,
    beitragssatz: float,
) -> float:
    """Unemployment insurance contributions paid by the insured person.

    Special rules for marginal employment have been introduced in April 1999 as part of
    the '630 Mark' job introduction.

    Reaching the Regelaltersgrenze exempts from unemployment insurance regardless of
    whether a pension is drawn (§ 28 Abs. 1 Nr. 1 SGB III).
    """
    if (
        sozialversicherung__geringfügig_beschäftigt
        or sozialversicherung__rente__altersrente__älter_als_regelaltersgrenze
    ):
        out = 0.0
    else:
        out = sozialversicherung__rente__beitrag__einkommen_m * beitragssatz / 2

    return out


@policy_function(
    start_date="2003-04-01",
    leaf_name="betrag_versicherter_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_versicherter_m_mit_midijob(
    sozialversicherung__geringfügig_beschäftigt: bool,
    sozialversicherung__rente__altersrente__älter_als_regelaltersgrenze: bool,
    sozialversicherung__in_gleitzone: bool,
    betrag_versicherter_in_gleitzone_m: float,
    sozialversicherung__rente__beitrag__einkommen_m: float,
    beitragssatz: float,
) -> float:
    """Unemployment insurance contributions paid by the insured person.

    Reaching the Regelaltersgrenze exempts from unemployment insurance regardless of
    whether a pension is drawn (§ 28 Abs. 1 Nr. 1 SGB III).
    """
    if (
        sozialversicherung__geringfügig_beschäftigt
        or sozialversicherung__rente__altersrente__älter_als_regelaltersgrenze
    ):
        out = 0.0
    elif sozialversicherung__in_gleitzone:
        out = betrag_versicherter_in_gleitzone_m
    else:
        out = sozialversicherung__rente__beitrag__einkommen_m * beitragssatz / 2

    return out


@policy_function(
    end_date="1999-03-31",
    leaf_name="betrag_arbeitgeber_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_arbeitgeber_m_bis_03_1999(
    sozialversicherung__rente__beitrag__einkommen_m: float,
    beitragssatz: float,
) -> float:
    """Employer's unemployment insurance contribution.

    Employees exempt because of age need no separate branch: the employer owes half
    of the contribution either way (§ 346 Abs. 3 S. 1 SGB III).
    """
    return sozialversicherung__rente__beitrag__einkommen_m * beitragssatz / 2


@policy_function(
    start_date="1999-04-01",
    end_date="2003-03-31",
    leaf_name="betrag_arbeitgeber_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_arbeitgeber_m_ohne_midijob(
    sozialversicherung__geringfügig_beschäftigt: bool,
    sozialversicherung__rente__beitrag__einkommen_m: float,
    beitragssatz: float,
) -> float:
    """Employer's unemployment insurance contribution until March 2003.

    Special rules for marginal employment have been introduced in April 1999 as part of
    the '630 Mark' job introduction.

    Employees exempt because of age need no separate branch: the employer owes half
    of the contribution either way (§ 346 Abs. 3 S. 1 SGB III).
    """
    if sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = sozialversicherung__rente__beitrag__einkommen_m * beitragssatz / 2

    return out


@policy_function(
    start_date="2003-04-01",
    end_date="2016-12-31",
    leaf_name="betrag_arbeitgeber_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_arbeitgeber_m_mit_midijob(
    sozialversicherung__geringfügig_beschäftigt: bool,
    sozialversicherung__rente__altersrente__älter_als_regelaltersgrenze: bool,
    sozialversicherung__in_gleitzone: bool,
    betrag_gesamt_in_gleitzone_m: float,
    betrag_arbeitgeber_in_gleitzone_m: float,
    sozialversicherung__rente__beitrag__einkommen_m: float,
    beitragssatz: float,
) -> float:
    """Employer's unemployment insurance contribution since April 2003.

    For an employee exempt because of age the employer owes half of the contribution
    that mandatory coverage would trigger (§ 346 Abs. 3 S. 1 SGB III). The asymmetric
    split of the Übergangsbereich is confined to versicherungspflichtige Beschäftigte
    (§ 346 Abs. 1a SGB III), so half of the Gesamtbeitrag applies there, too.
    """
    if sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    elif (
        sozialversicherung__rente__altersrente__älter_als_regelaltersgrenze
        and sozialversicherung__in_gleitzone
    ):
        out = betrag_gesamt_in_gleitzone_m / 2
    elif sozialversicherung__in_gleitzone:
        out = betrag_arbeitgeber_in_gleitzone_m
    else:
        out = sozialversicherung__rente__beitrag__einkommen_m * beitragssatz / 2

    return out


@policy_function(
    start_date="2017-01-01",
    end_date="2021-12-31",
    leaf_name="betrag_arbeitgeber_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_arbeitgeber_m_ohne_beitrag_für_versicherungsfreie(
    sozialversicherung__geringfügig_beschäftigt: bool,
    sozialversicherung__rente__altersrente__älter_als_regelaltersgrenze: bool,
    sozialversicherung__in_gleitzone: bool,
    betrag_arbeitgeber_in_gleitzone_m: float,
    sozialversicherung__rente__beitrag__einkommen_m: float,
    beitragssatz: float,
) -> float:
    """Employer's unemployment insurance contribution while the Beitrag is suspended.

    The Flexirentengesetz suspended the employer's contribution for employees exempt
    because of age through the end of 2021 (§ 346 Abs. 3 S. 3 SGB III).
    """
    if (
        sozialversicherung__geringfügig_beschäftigt
        or sozialversicherung__rente__altersrente__älter_als_regelaltersgrenze
    ):
        out = 0.0
    elif sozialversicherung__in_gleitzone:
        out = betrag_arbeitgeber_in_gleitzone_m
    else:
        out = sozialversicherung__rente__beitrag__einkommen_m * beitragssatz / 2

    return out


@policy_function(
    start_date="2022-01-01",
    leaf_name="betrag_arbeitgeber_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_arbeitgeber_m_mit_beitrag_für_versicherungsfreie(
    sozialversicherung__geringfügig_beschäftigt: bool,
    sozialversicherung__rente__altersrente__älter_als_regelaltersgrenze: bool,
    sozialversicherung__in_gleitzone: bool,
    betrag_gesamt_in_gleitzone_m: float,
    betrag_arbeitgeber_in_gleitzone_m: float,
    sozialversicherung__rente__beitrag__einkommen_m: float,
    beitragssatz: float,
) -> float:
    """Employer's unemployment insurance contribution since the suspension expired.

    For an employee exempt because of age the employer owes half of the contribution
    that mandatory coverage would trigger (§ 346 Abs. 3 S. 1 SGB III). The asymmetric
    split of the Übergangsbereich is confined to versicherungspflichtige Beschäftigte
    (§ 346 Abs. 1a SGB III), so half of the Gesamtbeitrag applies there, too.
    """
    if sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    elif (
        sozialversicherung__rente__altersrente__älter_als_regelaltersgrenze
        and sozialversicherung__in_gleitzone
    ):
        out = betrag_gesamt_in_gleitzone_m / 2
    elif sozialversicherung__in_gleitzone:
        out = betrag_arbeitgeber_in_gleitzone_m
    else:
        out = sozialversicherung__rente__beitrag__einkommen_m * beitragssatz / 2

    return out


@policy_function(start_date="2003-04-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def betrag_gesamt_in_gleitzone_m(
    sozialversicherung__midijob_bemessungsentgelt_m: float,
    beitragssatz: float,
) -> float:
    """Sum of employee's and employer's unemployment insurance contribution
    for Midijobs.
    """
    return sozialversicherung__midijob_bemessungsentgelt_m * beitragssatz


@policy_function(
    start_date="2003-04-01",
    end_date="2022-09-30",
    leaf_name="betrag_arbeitgeber_in_gleitzone_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_arbeitgeber_in_gleitzone_m_anteil_bruttolohn(
    einnahmen__bruttolohn_m: float,
    beitragssatz: float,
) -> float:
    """Employers' unemployment insurance contribution for Midijobs until September
    2022.
    """
    return einnahmen__bruttolohn_m * beitragssatz / 2


@policy_function(
    start_date="2022-10-01",
    leaf_name="betrag_arbeitgeber_in_gleitzone_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_arbeitgeber_in_gleitzone_m_als_differenz_von_gesamt_und_versichertenbeitrag(
    betrag_gesamt_in_gleitzone_m: float,
    betrag_versicherter_in_gleitzone_m: float,
) -> float:
    """Employer's unemployment insurance contribution since October 2022."""
    return betrag_gesamt_in_gleitzone_m - betrag_versicherter_in_gleitzone_m


@policy_function(
    start_date="2003-04-01",
    end_date="2022-09-30",
    leaf_name="betrag_versicherter_in_gleitzone_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_versicherter_in_gleitzone_m_als_differenz_von_gesamt_und_arbeitgeberbeitrag(
    betrag_gesamt_in_gleitzone_m: float,
    betrag_arbeitgeber_in_gleitzone_m: float,
) -> float:
    """Employee's unemployment insurance contribution for Midijobs until September
    2022.
    """
    return betrag_gesamt_in_gleitzone_m - betrag_arbeitgeber_in_gleitzone_m


@policy_function(
    start_date="2022-10-01",
    leaf_name="betrag_versicherter_in_gleitzone_m",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_versicherter_in_gleitzone_m_mit_festem_beitragssatz(
    sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m: float,
    beitragssatz: float,
) -> float:
    """Employee's unemployment insurance contribution since October 2022."""
    return (
        sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m
        * beitragssatz
        / 2
    )
