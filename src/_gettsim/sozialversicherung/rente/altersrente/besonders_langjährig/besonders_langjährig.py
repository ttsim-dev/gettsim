"""Pathway for the very long-term insured."""

from __future__ import annotations

from gettsim.tt import ConsecutiveIntLookupTableParamValue, policy_function


@policy_function(
    start_date="2014-06-23",
    end_date="2028-12-31",
)
def altersgrenze(
    geburtsjahr: int,
    altersgrenze_gestaffelt: ConsecutiveIntLookupTableParamValue,
) -> float:
    """
    Full retirement age (FRA) for very long term insured.

    FRA depends on birth year and month.

    Calculate the threshold from which very long term insured people (at least 45
    years) can claim their full pension without deductions.

    Does not check for eligibility for this pathway into retirement.
    """
    return altersgrenze_gestaffelt.look_up(geburtsjahr)


@policy_function(start_date="2012-01-01")
def grundsätzlich_anspruchsberechtigt(
    sozialversicherung__rente__wartezeit_45_jahre_erfüllt: bool,
) -> bool:
    """Determining the eligibility for Altersrente für besonders langjährig Versicherte
    (pension for very long-term insured). Wartezeit 45 years. aka "Rente mit 63".
    """
    return sozialversicherung__rente__wartezeit_45_jahre_erfüllt
