"""Regular pathway."""

from __future__ import annotations

from gettsim.tt import ConsecutiveIntLookupTableParamValue, TTSIMUnit, policy_function


@policy_function(start_date="2007-04-20", end_date="2030-12-31", unit=TTSIMUnit.YEARS)
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

    Reference: § 235 Abs. 2 SGB VI idF Art. 1 G. v. 20.04.2007 BGBl. I S. 554
    """
    return altersgrenze_gestaffelt.look_up(geburtsjahr)


@policy_function(unit=TTSIMUnit.DIMENSIONLESS)
def grundsätzlich_anspruchsberechtigt(
    sozialversicherung__rente__mindestwartezeit_erfüllt: bool,
) -> bool:
    """Determining the eligibility for the Regelaltersrente.

    Reference:
        - § 1248 Abs. 1 RVO idF Art. 1 G. v. 23.02.1957 BGBl. I S. 45
        - § 1248 Abs. 5 RVO idF Art. 1 G. v. 16.10.1972 BGBl. I S. 1965
        - § 35 SGB VI idF Art. 1 G. v. 18.12.1989 BGBl. I S. 2261
        - § 35 Satz 1 SGB VI idF Art. 1 G. v. 20.04.2007 BGBl. I S. 554
    """
    return sozialversicherung__rente__mindestwartezeit_erfüllt
