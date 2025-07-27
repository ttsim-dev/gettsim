"""Public pension insurance contributions."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function(end_date="1999-03-31", leaf_name="betrag_versicherter_m")
def betrag_versicherter_m_bis_03_1999(
    betrag_versicherter_regulärer_beitragssatz: float,
) -> float:
    """Public pension insurance contributions paid by the insured person."""
    return betrag_versicherter_regulärer_beitragssatz


@policy_function(
    start_date="1999-04-01", end_date="2003-03-31", leaf_name="betrag_versicherter_m"
)
def betrag_versicherter_m_ohne_midijob(
    sozialversicherung__geringfügig_beschäftigt: bool,
    betrag_versicherter_regulärer_beitragssatz: float,
) -> float:
    """Public pension insurance contributions paid by the insured person.

    Special rules for marginal employment have been introduced in April 1999 as part of
    the '630 Mark' job introduction.
    """
    if sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = betrag_versicherter_regulärer_beitragssatz

    return out


@policy_function(start_date="2003-04-01", leaf_name="betrag_versicherter_m")
def betrag_versicherter_m_mit_midijob(
    sozialversicherung__geringfügig_beschäftigt: bool,
    betrag_in_gleitzone_arbeitnehmer_m: float,
    betrag_versicherter_regulärer_beitragssatz: float,
    sozialversicherung__in_gleitzone: bool,
) -> float:
    """Public pension insurance contributions paid by the insured person.

    After Midijob introduction in April 2003.
    """
    if sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    elif sozialversicherung__in_gleitzone:
        out = betrag_in_gleitzone_arbeitnehmer_m
    else:
        out = betrag_versicherter_regulärer_beitragssatz

    return out


@policy_function()
def betrag_versicherter_regulärer_beitragssatz(
    einkommen_m: float,
    beitragssatz: float,
) -> float:
    """Public pension insurance contributions paid by the insured person."""
    return einkommen_m * beitragssatz / 2


@policy_function(
    end_date="1999-03-31",
    leaf_name="betrag_arbeitgeber_m",
)
def betrag_arbeitgeber_m_ohne_arbeitgeberpauschale(
    betrag_versicherter_regulärer_beitragssatz: float,
) -> float:
    """Employer's public pension insurance contribution.

    Before Minijobs were subject to pension contributions.
    """
    return betrag_versicherter_regulärer_beitragssatz


@policy_function(
    start_date="1999-04-01",
    end_date="2003-03-31",
    leaf_name="betrag_arbeitgeber_m",
)
def betrag_arbeitgeber_m_mit_arbeitgeberpauschale(
    sozialversicherung__geringfügig_beschäftigt: bool,
    betrag_versicherter_regulärer_beitragssatz: float,
    einnahmen__bruttolohn_m: float,
    minijob_arbeitgeberpauschale: float,
) -> float:
    """Employer's public pension insurance contribution.

    Special rules for marginal employment have been introduced in April 1999 as part of
    the '630 Mark' job introduction.
    """
    if sozialversicherung__geringfügig_beschäftigt:
        out = einnahmen__bruttolohn_m * minijob_arbeitgeberpauschale
    else:
        out = betrag_versicherter_regulärer_beitragssatz

    return out


@policy_function(start_date="2003-04-01", leaf_name="betrag_arbeitgeber_m")
def betrag_arbeitgeber_m_mit_midijob(
    sozialversicherung__geringfügig_beschäftigt: bool,
    betrag_in_gleitzone_arbeitgeber_m: float,
    betrag_versicherter_regulärer_beitragssatz: float,
    sozialversicherung__in_gleitzone: bool,
    einnahmen__bruttolohn_m: float,
    minijob_arbeitgeberpauschale: float,
) -> float:
    """Employer's public pension insurance contribution.

    After Midijob introduction in April 2003.
    """
    if sozialversicherung__geringfügig_beschäftigt:
        out = einnahmen__bruttolohn_m * minijob_arbeitgeberpauschale
    elif sozialversicherung__in_gleitzone:
        out = betrag_in_gleitzone_arbeitgeber_m
    else:
        out = betrag_versicherter_regulärer_beitragssatz

    return out


@policy_function()
def einkommen_m(
    einnahmen__bruttolohn_m: float,
    beitragsbemessungsgrenze_m: float,
) -> float:
    """Wage subject to pension and unemployment insurance contributions."""
    return min(
        einnahmen__bruttolohn_m,
        beitragsbemessungsgrenze_m,
    )


@policy_function(
    start_date="1990-01-01",
    end_date="2024-12-31",
    leaf_name="beitragsbemessungsgrenze_m",
)
def beitragsbemessungsgrenze_m_nach_wohnort(
    wohnort_ost_hh: bool,
    parameter_beitragsbemessungsgrenze_nach_wohnort: dict[str, float],
) -> float:
    """Income threshold up to which pension insurance payments apply."""
    return (
        parameter_beitragsbemessungsgrenze_nach_wohnort["ost"]
        if wohnort_ost_hh
        else parameter_beitragsbemessungsgrenze_nach_wohnort["west"]
    )


@policy_function(start_date="2003-04-01")
def betrag_in_gleitzone_gesamt_m(
    sozialversicherung__midijob_bemessungsentgelt_m: float,
    beitragssatz: float,
) -> float:
    """Sum of employer and employee pension insurance contribution for midijobs.
    Midijobs were introduced in April 2003.
    """
    return sozialversicherung__midijob_bemessungsentgelt_m * beitragssatz


@policy_function(
    start_date="2003-04-01",
    end_date="2022-09-30",
    leaf_name="betrag_in_gleitzone_arbeitgeber_m",
)
def betrag_in_gleitzone_arbeitgeber_m_mit_festem_beitragssatz(
    einnahmen__bruttolohn_m: float,
    beitragssatz: float,
) -> float:
    """Employer's unemployment insurance contribution until September 2022."""
    return einnahmen__bruttolohn_m * beitragssatz / 2


@policy_function(start_date="2022-10-01", leaf_name="betrag_in_gleitzone_arbeitgeber_m")
def betrag_in_gleitzone_arbeitgeber_m_als_differenz_von_gesamt_und_arbeitnehmerbeitrag(
    betrag_in_gleitzone_gesamt_m: float,
    betrag_in_gleitzone_arbeitnehmer_m: float,
) -> float:
    """Employer's unemployment insurance contribution since October 2022."""
    return betrag_in_gleitzone_gesamt_m - betrag_in_gleitzone_arbeitnehmer_m


@policy_function(
    start_date="2003-04-01",
    end_date="2022-09-30",
    leaf_name="betrag_in_gleitzone_arbeitnehmer_m",
)
def betrag_in_gleitzone_arbeitnehmer_m_als_differenz_von_gesamt_und_arbeitgeberbeitrag(
    betrag_in_gleitzone_arbeitgeber_m: float,
    betrag_in_gleitzone_gesamt_m: float,
) -> float:
    """Employee's unemployment insurance contribution for midijobs until September 2022."""
    return betrag_in_gleitzone_gesamt_m - betrag_in_gleitzone_arbeitgeber_m


@policy_function(
    start_date="2022-10-01",
    leaf_name="betrag_in_gleitzone_arbeitnehmer_m",
)
def betrag_in_gleitzone_arbeitnehmer_m_mit_festem_beitragssatz(
    sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m: float,
    beitragssatz: float,
) -> float:
    """Employee's unemployment insurance contribution for midijobs since October 2022."""
    return (
        sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m
        * beitragssatz
        / 2
    )
