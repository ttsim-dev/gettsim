"""Regular pathway."""

from __future__ import annotations

from gettsim.tt import ConsecutiveIntLookupTableParamValue, policy_function


@policy_function(start_date="2007-04-20", end_date="2030-12-31")
def altersgrenze(
    geburtsjahr: int,
    altersgrenze_gestaffelt: ConsecutiveIntLookupTableParamValue,
) -> float:
    """Normal retirement age (NRA) during the phase-in period.

    Just a parameter otherwise.

    The Regelaltersrente cannot be claimed earlier than at the NRA, i.e. the NRA does
    not serve as reference for calculating deductions. However, it serves as reference
    for calculating gains in the Zugangsfakor in case of later retirement.

    Does not check for eligibility for this pathway into retirement.
    """
    return altersgrenze_gestaffelt.look_up(geburtsjahr)


@policy_function()
def grundsätzlich_anspruchsberechtigt(
    sozialversicherung__rente__mindestwartezeit_erfüllt: bool,
) -> bool:
    """Determining the eligibility for the Regelaltersrente."""
    return sozialversicherung__rente__mindestwartezeit_erfüllt
