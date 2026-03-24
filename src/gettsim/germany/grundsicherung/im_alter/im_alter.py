"""Grundsicherung im Alter."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gettsim.germany.arbeitslosengeld_2.regelbedarf import (
        Regelbedarfsstufen,
    )

from gettsim.tt import policy_function

# --- EG-level pooled entitlement (used by horizontal method) ---


@policy_function(end_date="2022-12-31", leaf_name="anspruchshöhe_m_eg")
def anspruchshöhe_m_eg_bis_2022(
    arbeitslosengeld_2__regelbedarf_m_eg: float,
    mehrbedarf_schwerbehinderung_g_m_eg: float,
    kindergeld__betrag_m_eg: float,
    unterhalt__tatsächlich_erhaltener_betrag_m_eg: float,
    unterhaltsvorschuss__betrag_m_eg: float,
    einkommen_m_eg: float,
    vermögen_eg: float,
    vermögensfreibetrag_eg: float,
) -> float:
    """Pooled EG-level entitlement for Grundsicherung im Alter.

    Reference: § 41 ff. SGB XII
    """
    if vermögen_eg >= vermögensfreibetrag_eg:
        out = 0.0
    else:
        out = (
            arbeitslosengeld_2__regelbedarf_m_eg
            + mehrbedarf_schwerbehinderung_g_m_eg
            - einkommen_m_eg
            - unterhalt__tatsächlich_erhaltener_betrag_m_eg
            - unterhaltsvorschuss__betrag_m_eg
            - kindergeld__betrag_m_eg
        )

    return max(out, 0.0)


@policy_function(start_date="2023-01-01", leaf_name="anspruchshöhe_m_eg")
def anspruchshöhe_m_eg_ab_2023(
    bürgergeld__regelbedarf_m_eg: float,
    mehrbedarf_schwerbehinderung_g_m_eg: float,
    kindergeld__betrag_m_eg: float,
    unterhalt__tatsächlich_erhaltener_betrag_m_eg: float,
    unterhaltsvorschuss__betrag_m_eg: float,
    einkommen_m_eg: float,
    vermögen_eg: float,
    vermögensfreibetrag_eg: float,
) -> float:
    """Pooled EG-level entitlement for Grundsicherung im Alter.

    Reference: § 41 ff. SGB XII
    """
    if vermögen_eg >= vermögensfreibetrag_eg:
        out = 0.0
    else:
        out = (
            bürgergeld__regelbedarf_m_eg
            + mehrbedarf_schwerbehinderung_g_m_eg
            - einkommen_m_eg
            - unterhalt__tatsächlich_erhaltener_betrag_m_eg
            - unterhaltsvorschuss__betrag_m_eg
            - kindergeld__betrag_m_eg
        )

    return max(out, 0.0)


# --- Eligible member's Bedarf (for proportional distribution) ---


@policy_function(end_date="2022-12-31", leaf_name="bedarf_berechtigter_m")
def bedarf_berechtigter_m_bis_2022(
    arbeitslosengeld_2__regelbedarf_m: float,
    mehrbedarf_schwerbehinderung_g_m: float,
    über_regelaltersgrenze: bool,
    sozialversicherung__rente__bezieht_rente: bool,
) -> float:
    """Bedarf of persons eligible for Grundsicherung (im Alter or bei Erwerbsminderung).

    Zero for persons who are not eligible (e.g. children, erwerbsfähig adults).
    Auto-aggregated to _eg level for use as denominator in proportional distribution.
    """
    if über_regelaltersgrenze or sozialversicherung__rente__bezieht_rente:
        out = arbeitslosengeld_2__regelbedarf_m + mehrbedarf_schwerbehinderung_g_m
    else:
        out = 0.0

    return out


@policy_function(start_date="2023-01-01", leaf_name="bedarf_berechtigter_m")
def bedarf_berechtigter_m_ab_2023(
    bürgergeld__regelbedarf_m: float,
    mehrbedarf_schwerbehinderung_g_m: float,
    über_regelaltersgrenze: bool,
    sozialversicherung__rente__bezieht_rente: bool,
) -> float:
    """Bedarf of persons eligible for Grundsicherung (im Alter or bei Erwerbsminderung).

    Zero for persons who are not eligible (e.g. children, erwerbsfähig adults).
    Auto-aggregated to _eg level for use as denominator in proportional distribution.
    """
    if über_regelaltersgrenze or sozialversicherung__rente__bezieht_rente:
        out = bürgergeld__regelbedarf_m + mehrbedarf_schwerbehinderung_g_m
    else:
        out = 0.0

    return out


# --- Horizontal method (normal EG) ---


@policy_function(end_date="2022-12-31", leaf_name="anspruchshöhe_nach_bedarfsanteil_m")
def anspruchshöhe_nach_bedarfsanteil_m_bis_2022(
    arbeitslosengeld_2__regelbedarf_m: float,
    mehrbedarf_schwerbehinderung_g_m: float,
    bedarf_berechtigter_m_eg: float,
    anspruchshöhe_m_eg: float,
) -> float:
    """Individual share of EG entitlement, proportional to Bedarf.

    Only eligible members' Bedarf counts for the proportional distribution, so that
    the sum of individual shares equals the EG-level entitlement.

    Reference: § 27 Abs. 2 SGB XII
    """
    bedarf_m = arbeitslosengeld_2__regelbedarf_m + mehrbedarf_schwerbehinderung_g_m

    if bedarf_berechtigter_m_eg > 0.0:
        return (bedarf_m / bedarf_berechtigter_m_eg) * anspruchshöhe_m_eg
    else:
        return 0.0


@policy_function(
    start_date="2023-01-01", leaf_name="anspruchshöhe_nach_bedarfsanteil_m"
)
def anspruchshöhe_nach_bedarfsanteil_m_ab_2023(
    bürgergeld__regelbedarf_m: float,
    mehrbedarf_schwerbehinderung_g_m: float,
    bedarf_berechtigter_m_eg: float,
    anspruchshöhe_m_eg: float,
) -> float:
    """Individual share of EG entitlement, proportional to Bedarf.

    Only eligible members' Bedarf counts for the proportional distribution, so that
    the sum of individual shares equals the EG-level entitlement.

    Reference: § 27 Abs. 2 SGB XII
    """
    bedarf_m = bürgergeld__regelbedarf_m + mehrbedarf_schwerbehinderung_g_m

    if bedarf_berechtigter_m_eg > 0.0:
        return (bedarf_m / bedarf_berechtigter_m_eg) * anspruchshöhe_m_eg
    else:
        return 0.0


# --- Vertical method (mixed BG) ---


@policy_function(
    end_date="2022-12-31", leaf_name="anspruchshöhe_nach_vertikalmethode_m"
)
def anspruchshöhe_nach_vertikalmethode_m_bis_2022(
    arbeitslosengeld_2__regelbedarf_m: float,
    mehrbedarf_schwerbehinderung_g_m: float,
    einkommen_m: float,
    kindergeld__betrag_m: float,
    unterhalt__tatsächlich_erhaltener_betrag_m: float,
    unterhaltsvorschuss__betrag_m: float,
    vermögen_eg: float,
    vermögensfreibetrag_eg: float,
) -> float:
    """Individual entitlement using own Bedarf and income only.

    Vertical method for gemischte Bedarfsgemeinschaften.

    Reference: BSG B 14 AS 89/20 R (11.11.2021)
    """
    if vermögen_eg >= vermögensfreibetrag_eg:
        out = 0.0
    else:
        out = max(
            0.0,
            arbeitslosengeld_2__regelbedarf_m
            + mehrbedarf_schwerbehinderung_g_m
            - einkommen_m
            - unterhalt__tatsächlich_erhaltener_betrag_m
            - unterhaltsvorschuss__betrag_m
            - kindergeld__betrag_m,
        )

    return out


@policy_function(
    start_date="2023-01-01", leaf_name="anspruchshöhe_nach_vertikalmethode_m"
)
def anspruchshöhe_nach_vertikalmethode_m_ab_2023(
    bürgergeld__regelbedarf_m: float,
    mehrbedarf_schwerbehinderung_g_m: float,
    einkommen_m: float,
    kindergeld__betrag_m: float,
    unterhalt__tatsächlich_erhaltener_betrag_m: float,
    unterhaltsvorschuss__betrag_m: float,
    vermögen_eg: float,
    vermögensfreibetrag_eg: float,
) -> float:
    """Individual entitlement using own Bedarf and income only.

    Vertical method for gemischte Bedarfsgemeinschaften.

    Reference: BSG B 14 AS 89/20 R (11.11.2021)
    """
    if vermögen_eg >= vermögensfreibetrag_eg:
        out = 0.0
    else:
        out = max(
            0.0,
            bürgergeld__regelbedarf_m
            + mehrbedarf_schwerbehinderung_g_m
            - einkommen_m
            - unterhalt__tatsächlich_erhaltener_betrag_m
            - unterhaltsvorschuss__betrag_m
            - kindergeld__betrag_m,
        )

    return out


# --- Final benefit with gating ---


@policy_function(start_date="2005-01-01")
def betrag_m(
    anspruchshöhe_nach_bedarfsanteil_m: float,
    anspruchshöhe_nach_vertikalmethode_m: float,
    ist_gemischte_bg: bool,
    über_regelaltersgrenze: bool,
    sozialversicherung__rente__bezieht_rente: bool,
    familie__anzahl_kinder_eg: int,
    familie__anzahl_personen_eg: int,
) -> float:
    """Final monthly Grundsicherung benefit per person.

    Eligible persons are those who have reached the Regelaltersgrenze (§ 41 Abs. 1 SGB
    XII) or who receive a pension (Grundsicherung bei Erwerbsminderung, § 41 Abs. 3 SGB
    XII). In a gemischte BG, the vertical method is used; otherwise the horizontal method.
    """
    if (
        not über_regelaltersgrenze and not sozialversicherung__rente__bezieht_rente
    ) or familie__anzahl_kinder_eg == familie__anzahl_personen_eg:
        out = 0.0
    elif ist_gemischte_bg:
        out = anspruchshöhe_nach_vertikalmethode_m
    else:
        out = anspruchshöhe_nach_bedarfsanteil_m

    return out


# --- Mehrbedarf and wealth exemptions ---


@policy_function(start_date="2011-01-01")
def mehrbedarf_schwerbehinderung_g_m(
    schwerbehindert_grad_g: bool,
    familie__anzahl_erwachsene_eg: int,
    mehrbedarf_bei_schwerbehinderungsgrad_g: float,
    grundsicherung__regelbedarfsstufen: Regelbedarfsstufen,
) -> float:
    """Additional allowance for individuals with disabled person's pass G.

    Reference: § 30 Abs. 1 SGB XII
    """
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
