"""Eligibility checks for housing benefits (Wohngeld)."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function(
    start_date="2005-01-01",
    end_date="2008-12-31",
    leaf_name="grundsätzlich_anspruchsberechtigt_wthh",
)
def grundsätzlich_anspruchsberechtigt_wthh_ohne_vermögensprüfung(
    mindesteinkommen_erreicht_wthh: bool,
) -> bool:
    """Check whether the household meets the conditions for Wohngeld.

    This target is used to calculate the actual Wohngeld of all Bedarfsgemeinschaften
    that passed the priority check against Arbeitslosengeld II / Bürgergeld.

    """
    return mindesteinkommen_erreicht_wthh


@policy_function(
    start_date="2009-01-01",
    leaf_name="grundsätzlich_anspruchsberechtigt_wthh",
)
def grundsätzlich_anspruchsberechtigt_wthh_mit_vermögensprüfung(
    mindesteinkommen_erreicht_wthh: bool,
    vermögensgrenze_unterschritten_wthh: bool,
) -> bool:
    """Check whether the household meets the conditions for Wohngeld.

    This target is used to calculate the actual Wohngeld of all Bedarfsgemeinschaften
    that passed the priority check against Arbeitslosengeld II / Bürgergeld.

    """
    return mindesteinkommen_erreicht_wthh and vermögensgrenze_unterschritten_wthh


@policy_function(
    start_date="2005-01-01",
    end_date="2008-12-31",
    leaf_name="grundsätzlich_anspruchsberechtigt_bg",
)
def grundsätzlich_anspruchsberechtigt_bg_ohne_vermögensprüfung(
    mindesteinkommen_erreicht_bg: bool,
) -> bool:
    """Check whether the household meets the conditions for Wohngeld.

    This target is used for the priority check calculation against Arbeitslosengeld II /
    Bürgergeld on the Bedarfsgemeinschaft level.

    """
    return mindesteinkommen_erreicht_bg


@policy_function(
    start_date="2009-01-01",
    leaf_name="grundsätzlich_anspruchsberechtigt_bg",
)
def grundsätzlich_anspruchsberechtigt_bg_mit_vermögensprüfung(
    mindesteinkommen_erreicht_bg: bool,
    vermögensgrenze_unterschritten_bg: bool,
) -> bool:
    """Check whether the household meets the conditions for Wohngeld.

    This target is used for the priority check calculation against Arbeitslosengeld II /
    Bürgergeld on the Bedarfsgemeinschaft level.

    """
    return mindesteinkommen_erreicht_bg and vermögensgrenze_unterschritten_bg


@policy_function(start_date="2009-01-01")
def vermögensgrenze_unterschritten_wthh(
    vermögen_wthh: float,
    anzahl_personen_wthh: int,
    parameter_vermögensfreibetrag: dict[str, float],
) -> bool:
    """Wealth is below the eligibility threshold for housing benefits."""
    vermögensfreibetrag = parameter_vermögensfreibetrag[
        "grundfreibetrag"
    ] + parameter_vermögensfreibetrag["je_weitere_person"] * (anzahl_personen_wthh - 1)

    return vermögen_wthh <= vermögensfreibetrag


@policy_function(start_date="2009-01-01")
def vermögensgrenze_unterschritten_bg(
    vermögen_bg: float,
    arbeitslosengeld_2__anzahl_personen_bg: int,
    parameter_vermögensfreibetrag: dict[str, float],
) -> bool:
    """Wealth is below the eligibility threshold for housing benefits."""
    vermögensfreibetrag = parameter_vermögensfreibetrag[
        "grundfreibetrag"
    ] + parameter_vermögensfreibetrag["je_weitere_person"] * (
        arbeitslosengeld_2__anzahl_personen_bg - 1
    )

    return vermögen_bg <= vermögensfreibetrag


@policy_function(start_date="2005-01-01")
def mindesteinkommen_erreicht_wthh(
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

    """
    return (
        einkommen_für_mindesteinkommen_m_wthh >= arbeitslosengeld_2__regelbedarf_m_wthh
    )


@policy_function(start_date="2005-01-01")
def mindesteinkommen_erreicht_bg(
    arbeitslosengeld_2__regelbedarf_m_bg: float,
    einkommen_für_mindesteinkommen_m_bg: float,
) -> bool:
    """Minimum income requirement for housing benefits is met.

    Note: The Wohngeldstelle can make a discretionary judgment if the applicant does not
    meet the Mindesteinkommen:

    1. Savings may partly cover the Regelbedarf, making the applicant eligible again.
    2. The Wohngeldstelle may reduce the Regelsatz by 20% (but not KdU or private
        insurance contributions).

    The allowance for discretionary judgment is ignored here.

    """
    return einkommen_für_mindesteinkommen_m_bg >= arbeitslosengeld_2__regelbedarf_m_bg


@policy_function(start_date="2005-01-01")
def einkommen_für_mindesteinkommen_m(
    arbeitslosengeld_2__nettoeinkommen_vor_abzug_freibetrag_m: float,
    unterhalt__tatsächlich_erhaltener_betrag_m: float,
    unterhaltsvorschuss__betrag_m: float,
    kindergeld__betrag_m: float,
    kinderzuschlag__anspruchshöhe_m: float,
) -> float:
    """Income for the Mindesteinkommen check.

    Minimum income is defined via VwV 15.01 ff § 15 WoGG.

    According to BMI Erlass of 11.03.2020, Unterhaltsvorschuss, Kinderzuschlag and
    Kindergeld count as income for this check.

    """
    return (
        arbeitslosengeld_2__nettoeinkommen_vor_abzug_freibetrag_m
        + unterhalt__tatsächlich_erhaltener_betrag_m
        + unterhaltsvorschuss__betrag_m
        + kindergeld__betrag_m
        + kinderzuschlag__anspruchshöhe_m
    )
