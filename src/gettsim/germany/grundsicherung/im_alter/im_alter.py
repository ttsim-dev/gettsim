"""Grundsicherung im Alter."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gettsim.germany.arbeitslosengeld_2.regelbedarf import (
        Regelbedarfsstufen,
    )

from gettsim.tt import policy_function


@policy_function(end_date="2022-12-31", leaf_name="betrag_m")
def betrag_m_bis_2022(
    arbeitslosengeld_2__regelbedarf_m: float,
    mehrbedarf_schwerbehinderung_g_m: float,
    einkommen_m: float,
    kindergeld__betrag_m: float,
    unterhalt__tatsächlich_erhaltener_betrag_m: float,
    unterhaltsvorschuss__betrag_m: float,
    arbeitslosengeld_2__überschusseinkommen_m: float,
    hat_regelaltersgrenze_erreicht: bool,
    vermögen_eg: float,
    vermögensfreibetrag_eg: float,
) -> float:
    """Grundsicherung im Alter per person (§41 ff. SGB XII).

    Only persons who have reached the Regelaltersgrenze are eligible. In mixed BGs, the
    SGB II partner's excess income above their Bedarf is subtracted.

    Reference: §41 Abs. 1 SGB XII, BSG B 14 AS 89/20 R

    # TODO (@MImmesberger): Grundsicherung bei Erwerbsminderung (§41 Abs. 3 SGB XII) is
    # not yet implemented. Persons who are dauerhaft voll erwerbsgemindert should also be
    # eligible for this benefit, independently of the Regelaltersgrenze.
    # https://github.com/ttsim-dev/gettsim/issues/1145
    """
    if not hat_regelaltersgrenze_erreicht or vermögen_eg >= vermögensfreibetrag_eg:
        out = 0.0
    else:
        out = (
            arbeitslosengeld_2__regelbedarf_m
            + mehrbedarf_schwerbehinderung_g_m
            - einkommen_m
            - kindergeld__betrag_m
            - unterhalt__tatsächlich_erhaltener_betrag_m
            - unterhaltsvorschuss__betrag_m
            - arbeitslosengeld_2__überschusseinkommen_m
        )

    return max(out, 0.0)


@policy_function(start_date="2023-01-01", leaf_name="betrag_m")
def betrag_m_ab_2023(
    bürgergeld__regelbedarf_m: float,
    mehrbedarf_schwerbehinderung_g_m: float,
    einkommen_m: float,
    kindergeld__betrag_m: float,
    unterhalt__tatsächlich_erhaltener_betrag_m: float,
    unterhaltsvorschuss__betrag_m: float,
    bürgergeld__überschusseinkommen_m: float,
    hat_regelaltersgrenze_erreicht: bool,
    vermögen_eg: float,
    vermögensfreibetrag_eg: float,
) -> float:
    """Grundsicherung im Alter per person (§41 ff. SGB XII).

    Only persons who have reached the Regelaltersgrenze are eligible. In mixed BGs, the
    SGB II partner's excess income above their Bedarf is subtracted.

    Reference: §41 Abs. 1 SGB XII, BSG B 14 AS 89/20 R

    # TODO (@MImmesberger): Grundsicherung bei Erwerbsminderung (§41 Abs. 3 SGB XII) is
    # not yet implemented. Persons who are dauerhaft voll erwerbsgemindert should also be
    # eligible for this benefit, independently of the Regelaltersgrenze.
    # https://github.com/ttsim-dev/gettsim/issues/1145
    """
    if not hat_regelaltersgrenze_erreicht or vermögen_eg >= vermögensfreibetrag_eg:
        out = 0.0
    else:
        out = (
            bürgergeld__regelbedarf_m
            + mehrbedarf_schwerbehinderung_g_m
            - einkommen_m
            - kindergeld__betrag_m
            - unterhalt__tatsächlich_erhaltener_betrag_m
            - unterhaltsvorschuss__betrag_m
            - bürgergeld__überschusseinkommen_m
        )

    return max(out, 0.0)


@policy_function(end_date="2022-12-31", leaf_name="überschusseinkommen_m")
def überschusseinkommen_m_bis_2022(
    arbeitslosengeld_2__regelbedarf_m: float,
    mehrbedarf_schwerbehinderung_g_m: float,
    einkommen_m: float,
    kindergeld__betrag_m: float,
    unterhalt__tatsächlich_erhaltener_betrag_m: float,
    unterhaltsvorschuss__betrag_m: float,
    hat_regelaltersgrenze_erreicht: bool,
) -> float:
    """Excess SGB XII income above own Bedarf, flowing to the SGB II partner.

    Reference: BSG B 14 AS 89/20 R
    """
    if not hat_regelaltersgrenze_erreicht:
        out = 0.0
    else:
        out = max(
            0.0,
            einkommen_m
            + kindergeld__betrag_m
            + unterhalt__tatsächlich_erhaltener_betrag_m
            + unterhaltsvorschuss__betrag_m
            - arbeitslosengeld_2__regelbedarf_m
            - mehrbedarf_schwerbehinderung_g_m,
        )

    return out


@policy_function(start_date="2023-01-01", leaf_name="überschusseinkommen_m")
def überschusseinkommen_m_ab_2023(
    bürgergeld__regelbedarf_m: float,
    mehrbedarf_schwerbehinderung_g_m: float,
    einkommen_m: float,
    kindergeld__betrag_m: float,
    unterhalt__tatsächlich_erhaltener_betrag_m: float,
    unterhaltsvorschuss__betrag_m: float,
    hat_regelaltersgrenze_erreicht: bool,
) -> float:
    """Excess SGB XII income above own Bedarf, flowing to the SGB II partner.

    Reference: BSG B 14 AS 89/20 R
    """
    if not hat_regelaltersgrenze_erreicht:
        out = 0.0
    else:
        out = max(
            0.0,
            einkommen_m
            + kindergeld__betrag_m
            + unterhalt__tatsächlich_erhaltener_betrag_m
            + unterhaltsvorschuss__betrag_m
            - bürgergeld__regelbedarf_m
            - mehrbedarf_schwerbehinderung_g_m,
        )

    return out


@policy_function(start_date="2011-01-01")
def mehrbedarf_schwerbehinderung_g_m(
    schwerbehindert_grad_g: bool,
    familie__anzahl_erwachsene_eg: int,
    mehrbedarf_bei_schwerbehinderungsgrad_g: float,
    grundsicherung__regelbedarfsstufen: Regelbedarfsstufen,
) -> float:
    """Additional allowance for individuals with disabled person's pass G."""
    mehrbedarf_single = (
        grundsicherung__regelbedarfsstufen.rbs_1
    ) * mehrbedarf_bei_schwerbehinderungsgrad_g
    mehrbedarf_in_couple = (
        grundsicherung__regelbedarfsstufen.rbs_2
    ) * mehrbedarf_bei_schwerbehinderungsgrad_g

    if (schwerbehindert_grad_g) and (familie__anzahl_erwachsene_eg == 1):
        out = mehrbedarf_single
    elif (schwerbehindert_grad_g) and (familie__anzahl_erwachsene_eg > 1):
        out = mehrbedarf_in_couple
    else:
        out = 0.0

    return out


@policy_function(start_date="2005-01-01")
def vermögensfreibetrag_eg(
    familie__anzahl_kinder_eg: int,
    familie__anzahl_erwachsene_eg: int,
    parameter_vermögensfreibetrag: dict[str, float],
) -> float:
    """Wealth not considered for Grundsicherung im Alter."""
    return (
        parameter_vermögensfreibetrag["erwachsene"] * familie__anzahl_erwachsene_eg
        + parameter_vermögensfreibetrag["kinder"] * familie__anzahl_kinder_eg
    )
