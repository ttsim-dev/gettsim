"""Eligibility checks for housing benefits (Wohngeld)."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, cast_ttsim_unit, policy_function


@policy_function(
    start_date="2005-01-01",
    end_date="2008-12-31",
    leaf_name="grundsätzlich_anspruchsberechtigt_wthh",
    unit=TTSIMUnit.DIMENSIONLESS.PER_WTHH,
)
def grundsätzlich_anspruchsberechtigt_wthh_ohne_vermögensprüfung(
    mindesteinkommen_erreicht_wthh: bool,
) -> bool:
    """Check whether the household meets the conditions for Wohngeld.

    Before 2009, high wealth is no reason for exclusion from Wohngeld.

    Reference: none (technical helper)
    """
    return mindesteinkommen_erreicht_wthh


@policy_function(
    start_date="2009-01-01",
    leaf_name="grundsätzlich_anspruchsberechtigt_wthh",
    unit=TTSIMUnit.DIMENSIONLESS.PER_WTHH,
)
def grundsätzlich_anspruchsberechtigt_wthh_mit_vermögensprüfung(
    mindesteinkommen_erreicht_wthh: bool,
    vermögensgrenze_unterschritten_wthh: bool,
) -> bool:
    """Household meets the conditions for Wohngeld.

    Reference: § 21 Nr. 3 WoGG idF Art. 1 G. v. 24.09.2008 BGBl. I S. 1856
    """
    return mindesteinkommen_erreicht_wthh and vermögensgrenze_unterschritten_wthh


@policy_function(start_date="2009-01-01", unit=TTSIMUnit.DIMENSIONLESS.PER_WTHH)
def vermögensgrenze_unterschritten_wthh(
    vermögen_wthh: float,
    anzahl_personen_wthh: int,
    parameter_vermögensfreibetrag: dict[str, float],
) -> bool:
    """Wealth is below the eligibility threshold for housing benefits.

    The thresholds are set by the Wohngeld-Verwaltungsvorschrift (Nr. 21.37), which
    interprets "erhebliches Vermögen" in § 21 Nr. 3 WoGG.

    Reference: § 21 Nr. 3 WoGG idF Art. 1 G. v. 24.09.2008 BGBl. I S. 1856
    """
    vermögensfreibetrag = parameter_vermögensfreibetrag[
        "grundfreibetrag"
    ] + parameter_vermögensfreibetrag["je_weitere_person"] * (
        anzahl_personen_wthh - cast_ttsim_unit(1, unit=TTSIMUnit.COUNT.PER_WTHH)
    )

    return vermögen_wthh <= vermögensfreibetrag


@policy_function(
    leaf_name="mindesteinkommen_erreicht_wthh",
    start_date="2005-01-01",
    end_date="2022-12-31",
    unit=TTSIMUnit.DIMENSIONLESS.PER_WTHH,
)
def mindesteinkommen_erreicht_wthh_bis_2022(
    arbeitslosengeld_2__regelbedarf_m_wthh: float,
    einkommen_für_mindesteinkommen_m_wthh: float,
) -> bool:
    """Minimum income requirement for housing benefits is met.

    Note: The Wohngeldstelle can make a discretionary judgment if the applicant does not
    meet the Mindesteinkommen:

    1. Savings may partly cover the Regelbedarf, making the applicant eligible again.
    2. The Wohngeldstelle may reduce the Regelsatz by 20% (but not KdU or private
        insurance contributions).

    The allowance for discretionary judgment is ignored here.

    Reference:
        - § 11 Abs. 1 WoGG idF Art. 5 G. v. 22.12.1999 BGBl. I S. 2671
        - § 15 Abs. 1 WoGG idF Art. 1 G. v. 24.09.2008 BGBl. I S. 1856
    """
    return (
        einkommen_für_mindesteinkommen_m_wthh >= arbeitslosengeld_2__regelbedarf_m_wthh
    )


@policy_function(
    leaf_name="mindesteinkommen_erreicht_wthh",
    start_date="2023-01-01",
    unit=TTSIMUnit.DIMENSIONLESS.PER_WTHH,
)
def mindesteinkommen_erreicht_wthh_ab_2023(
    bürgergeld__regelbedarf_m_wthh: float,
    einkommen_für_mindesteinkommen_m_wthh: float,
) -> bool:
    """Minimum income requirement for housing benefits is met.

    Note: The Wohngeldstelle can make a discretionary judgment if the applicant does not
    meet the Mindesteinkommen:

    1. Savings may partly cover the Regelbedarf, making the applicant eligible again.
    2. The Wohngeldstelle may reduce the Regelsatz by 20% (but not KdU or private
        insurance contributions).

    The allowance for discretionary judgment is ignored here.

    Reference: § 15 Abs. 1 WoGG idF Art. 1 G. v. 24.09.2008 BGBl. I S. 1856
    """
    return einkommen_für_mindesteinkommen_m_wthh >= bürgergeld__regelbedarf_m_wthh


@policy_function(
    leaf_name="einkommen_für_mindesteinkommen_m_wthh",
    start_date="2005-01-01",
    end_date="2022-12-31",
    unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_WTHH,
)
def einkommen_für_mindesteinkommen_m_wthh_bis_2022(
    arbeitslosengeld_2__nettoeinkommen_vor_abzug_freibetrag_m_wthh: float,
    unterhalt__tatsächlich_erhaltener_betrag_m_wthh: float,
    unterhaltsvorschuss__betrag_m_wthh: float,
    kindergeld__betrag_m_wthh: float,
    kinderzuschlag__anspruchshöhe_m_wthh: float,
    basisbetrag_m_wthh: float,
) -> float:
    """Income for the Mindesteinkommen check.

    Minimum income is defined via VwV 15.01 ff § 15 WoGG. Per VwV 15.22, the check
    compares household income *including the anticipated Wohngeld* against the
    ALG2/Bürgergeld-Regelbedarf.

    According to BMI Erlass of 11.03.2020, Unterhaltsvorschuss, Kinderzuschlag and
    Kindergeld count as income for this check.

    Reference:
        - § 11 Abs. 1 WoGG idF Art. 5 G. v. 22.12.1999 BGBl. I S. 2671
        - § 15 Abs. 1 WoGG idF Art. 1 G. v. 24.09.2008 BGBl. I S. 1856
    """
    return (
        arbeitslosengeld_2__nettoeinkommen_vor_abzug_freibetrag_m_wthh
        + unterhalt__tatsächlich_erhaltener_betrag_m_wthh
        + unterhaltsvorschuss__betrag_m_wthh
        + kindergeld__betrag_m_wthh
        + kinderzuschlag__anspruchshöhe_m_wthh
        + basisbetrag_m_wthh
    )


@policy_function(
    leaf_name="einkommen_für_mindesteinkommen_m_wthh",
    start_date="2023-01-01",
    unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_WTHH,
)
def einkommen_für_mindesteinkommen_m_wthh_ab_2023(
    bürgergeld__nettoeinkommen_vor_abzug_freibetrag_m_wthh: float,
    unterhalt__tatsächlich_erhaltener_betrag_m_wthh: float,
    unterhaltsvorschuss__betrag_m_wthh: float,
    kindergeld__betrag_m_wthh: float,
    kinderzuschlag__anspruchshöhe_m_wthh: float,
    basisbetrag_m_wthh: float,
) -> float:
    """Income for the Mindesteinkommen check.

    Minimum income is defined via VwV 15.01 ff § 15 WoGG. Per VwV 15.22, the check
    compares household income *including the anticipated Wohngeld* against the
    ALG2/Bürgergeld-Regelbedarf.

    According to BMI Erlass of 11.03.2020, Unterhaltsvorschuss, Kinderzuschlag and
    Kindergeld count as income for this check.

    Reference: § 15 Abs. 1 WoGG idF Art. 1 G. v. 24.09.2008 BGBl. I S. 1856
    """
    return (
        bürgergeld__nettoeinkommen_vor_abzug_freibetrag_m_wthh
        + unterhalt__tatsächlich_erhaltener_betrag_m_wthh
        + unterhaltsvorschuss__betrag_m_wthh
        + kindergeld__betrag_m_wthh
        + kinderzuschlag__anspruchshöhe_m_wthh
        + basisbetrag_m_wthh
    )
