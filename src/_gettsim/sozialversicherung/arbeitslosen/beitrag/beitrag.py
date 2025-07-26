"""Contributions to the unemployment insurance."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function(end_date="1999-03-31", leaf_name="betrag_versicherter_m")
def betrag_versicherter_m_bis_03_1999(
    sozialversicherung__rente__beitrag__einkommen_m: float,
    beitragssatz: float,
) -> float:
    """Unemployment insurance contributions paid by the insured person."""
    return sozialversicherung__rente__beitrag__einkommen_m * beitragssatz / 2


@policy_function(
    start_date="1999-04-01", end_date="2003-03-31", leaf_name="betrag_versicherter_m"
)
def betrag_versicherter_m_ohne_midijob(
    sozialversicherung__geringfügig_beschäftigt: bool,
    sozialversicherung__rente__beitrag__einkommen_m: float,
    beitragssatz: float,
) -> float:
    """Unemployment insurance contributions paid by the insured person.

    Special rules for marginal employment have been introduced in April 1999 as part of
    the '630 Mark' job introduction.
    """
    if sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = sozialversicherung__rente__beitrag__einkommen_m * beitragssatz / 2

    return out


@policy_function(start_date="2003-04-01", leaf_name="betrag_versicherter_m")
def betrag_versicherter_m_mit_midijob(
    sozialversicherung__geringfügig_beschäftigt: bool,
    sozialversicherung__in_gleitzone: bool,
    betrag_versicherter_in_gleitzone_m: float,
    sozialversicherung__rente__beitrag__einkommen_m: float,
    beitragssatz: float,
) -> float:
    """Unemployment insurance contributions paid by the insured person."""
    if sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    elif sozialversicherung__in_gleitzone:
        out = betrag_versicherter_in_gleitzone_m
    else:
        out = sozialversicherung__rente__beitrag__einkommen_m * beitragssatz / 2

    return out


@policy_function(end_date="1999-03-31", leaf_name="betrag_arbeitgeber_m")
def betrag_arbeitgeber_m_bis_03_1999(
    sozialversicherung__rente__beitrag__einkommen_m: float,
    beitragssatz: float,
) -> float:
    """Employer's unemployment insurance contribution."""
    return sozialversicherung__rente__beitrag__einkommen_m * beitragssatz / 2


@policy_function(
    start_date="1999-04-01", end_date="2003-03-31", leaf_name="betrag_arbeitgeber_m"
)
def betrag_arbeitgeber_m_ohne_midijob(
    sozialversicherung__geringfügig_beschäftigt: bool,
    sozialversicherung__rente__beitrag__einkommen_m: float,
    beitragssatz: float,
) -> float:
    """Employer's unemployment insurance contribution until March 2003.

    Special rules for marginal employment have been introduced in April 1999 as part of
    the '630 Mark' job introduction.
    """
    if sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = sozialversicherung__rente__beitrag__einkommen_m * beitragssatz / 2

    return out


@policy_function(start_date="2003-04-01", leaf_name="betrag_arbeitgeber_m")
def betrag_arbeitgeber_m_mit_midijob(
    sozialversicherung__geringfügig_beschäftigt: bool,
    sozialversicherung__in_gleitzone: bool,
    betrag_arbeitgeber_in_gleitzone_m: float,
    sozialversicherung__rente__beitrag__einkommen_m: float,
    beitragssatz: float,
) -> float:
    """Employer's unemployment insurance contribution since April 2003."""
    if sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    elif sozialversicherung__in_gleitzone:
        out = betrag_arbeitgeber_in_gleitzone_m
    else:
        out = sozialversicherung__rente__beitrag__einkommen_m * beitragssatz / 2

    return out


@policy_function(start_date="2003-04-01")
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
)
def betrag_arbeitgeber_in_gleitzone_m_anteil_bruttolohn(
    einnahmen__bruttolohn_m: float,
    beitragssatz: float,
) -> float:
    """Employers' unemployment insurance contribution for Midijobs until September
    2022.
    """
    return einnahmen__bruttolohn_m * beitragssatz / 2


@policy_function(start_date="2022-10-01", leaf_name="betrag_arbeitgeber_in_gleitzone_m")
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
