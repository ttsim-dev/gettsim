"""Pathway for the long-term insured."""

from __future__ import annotations

from gettsim.tt import ConsecutiveIntLookupTableParamValue, policy_function


@policy_function(
    start_date="1989-12-18",
    leaf_name="altersgrenze",
)
def altersgrenze_gestaffelt_ab_1989(
    geburtsjahr: int,
    geburtsmonat: int,
    altersgrenze_gestaffelt: ConsecutiveIntLookupTableParamValue,
) -> float:
    """
    Full retirement age (FRA) for long term insured.

    Calculate the age, at which a long term insured person (at least 35 years) is
    eligible to claim the full pension (without deductions). This pension scheme allows
    for early retirement (e.g. age 63) with deductions. Hence this threshold is needed
    as reference for calculating the zugangsfaktor.

    Does not check for eligibility for this pathway into retirement.
    """
    birth_month_since_ad = geburtsjahr * 12 + (geburtsmonat - 1)
    return altersgrenze_gestaffelt.look_up(birth_month_since_ad)


@policy_function(
    start_date="1989-12-18",
    end_date="1996-09-26",
    leaf_name="altersgrenze_vorzeitig",
)
def altersgrenze_vorzeitig_gestaffelt_ab_1989_bis_1996(
    geburtsjahr: int,
    altersgrenze_vorzeitig_gestaffelt: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Early retirement age (ERA) for Renten für langjährig Versicherte.

    Does not check for eligibility for this pathway into retirement.
    """
    return altersgrenze_vorzeitig_gestaffelt.look_up(geburtsjahr)


@policy_function()
def grundsätzlich_anspruchsberechtigt(
    sozialversicherung__rente__wartezeit_35_jahre_erfüllt: bool,
) -> bool:
    """Determining the eligibility for Altersrente für langjährig
    Versicherte (pension for long-term insured). Wartezeit 35 years and
    crossing the age threshold.
    """
    return sozialversicherung__rente__wartezeit_35_jahre_erfüllt
