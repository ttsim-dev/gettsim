"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(start_date="2021-01-01", unit=TTSIMUnit.MONTHS)
def bewertungszeiten_monate() -> int:
    """Number of months determining amount of Grundrente."""


@policy_input(start_date="2021-01-01", unit=TTSIMUnit.MONTHS)
def grundrentenzeiten_monate() -> int:
    """Number of months determining eligibility for Grundrente."""


@policy_input(start_date="2021-01-01", unit=TTSIMUnit.DIMENSIONLESS)
def mean_entgeltpunkte() -> float:
    """Mean Entgeltpunkte during Bewertungszeiten."""


@policy_input(start_date="2021-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_EHE)
def einkommen_vorvorjahr_m_ehe() -> float:
    """Income of the couple relevant for the Grundrentenzuschlag (§ 97a SGB VI).

    The sum of the zu versteuerndes Einkommen, the steuerfreier Teil of pensions, and
    the capital income subject to the Abgeltungsteuer of the person and their spouse
    in the calendar year before the previous one (vorvergangenes Kalenderjahr), as a
    monthly amount. If no tax assessment exists for that year, the statute uses the
    year before it instead (§ 97a Abs. 2 S. 3 SGB VI).

    GETTSIM can calculate this input based on the data of that calendar year using the
    target `('sozialversicherung', 'rente', 'grundrente',
    'einkommen_für_einkommensanrechnung_im_übernächsten_jahr_m_ehe')`.

    Reference: § 97a Abs. 2 S. 1-3 SGB VI
    """
