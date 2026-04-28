"""Grundsicherung im Alter.

For an explanation of how income is distributed in SGB II and SGB XII see:

Kulle, Thomas: „Der Einkommenseinsatz nach den diversen Berechnungsmethoden im Rahmen
des SGB II und des SGB XII", in: Deutsche Verwaltungspraxis (DVP), 63. Jahrgang, Heft
5/2012, S. 178-188.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gettsim.germany.arbeitslosengeld_2.regelbedarf import (
        Regelbedarfsstufen,
        RegelsatzAnteilsbasiert,
    )

from gettsim.tt import AggType, agg_by_p_id_function, policy_function


@policy_function(start_date="2005-01-01")
def betrag_m(
    anspruchshöhe_m: float,
    vorrangprüfungen__wohngeld_kinderzuschlag_vorrangig_oder_günstiger: bool,
    hat_kind_mit_einkommen_über_einkommensgrenze: bool,
) -> float:
    """Grundsicherung im Alter after Vorrangprüfung and 100k-children exclusion.

    §43 SGB XII (BGBl. I 2003 S. 3022): Persons are excluded from Grundsicherung im
    Alter if any first-degree descendant has annual Gesamteinkommen (§16 SGB IV)
    exceeding the threshold.
    §2 Abs. 1 SGB XII: Vorrangprüfung.
    """
    if (
        hat_kind_mit_einkommen_über_einkommensgrenze
        or vorrangprüfungen__wohngeld_kinderzuschlag_vorrangig_oder_günstiger
    ):
        return 0.0
    else:
        return anspruchshöhe_m


@policy_function(end_date="2022-12-31", leaf_name="anspruchshöhe_m")
def anspruchshöhe_m_bis_2022(
    individueller_restbedarf_m: float,
    individueller_restbedarf_m_eg: float,
    bedarf_m_eg: float,
    einkommen_zur_verteilung_m_eg: float,
    arbeitslosengeld_2__überschusseinkommen_m_eg: float,
    grundsicherung__hilfe_zum_lebensunterhalt__überschusseinkommen_m_eg: float,
    vermögensgrenze_unterschritten_eg: bool,
) -> float:
    """Grundsicherung im Alter per person using the Verhältnislösung.

    Each person's income covers their own Bedarf first ('Vertikalmethode'). Only the
    Überschuss is distributed proportionally to the individueller Restbedarf of the
    hilfebedürftigen members.

    Reference: §19 Abs. 2 Satz 1 i.V.m. §43 Abs. 1 SGB XII, §27 Abs. 2 SGB XII
    """
    # TODO (@MImmesberger): Grundsicherung bei Erwerbsminderung (§41 Abs. 3 SGB XII) is
    # not yet implemented. Persons who are dauerhaft voll erwerbsgemindert should also
    # be eligible for this benefit, independently of the Regelaltersgrenze.
    # https://github.com/ttsim-dev/gettsim/issues/1145
    total_income_m_eg = (
        einkommen_zur_verteilung_m_eg
        + arbeitslosengeld_2__überschusseinkommen_m_eg
        + grundsicherung__hilfe_zum_lebensunterhalt__überschusseinkommen_m_eg
    )
    anspruch_m_eg = max(0.0, bedarf_m_eg - total_income_m_eg)

    if individueller_restbedarf_m_eg == 0.0 or not vermögensgrenze_unterschritten_eg:
        return 0.0
    else:
        return (
            individueller_restbedarf_m / individueller_restbedarf_m_eg
        ) * anspruch_m_eg


@policy_function(start_date="2023-01-01", leaf_name="anspruchshöhe_m")
def anspruchshöhe_m_ab_2023(
    individueller_restbedarf_m: float,
    individueller_restbedarf_m_eg: float,
    bedarf_m_eg: float,
    einkommen_zur_verteilung_m_eg: float,
    bürgergeld__überschusseinkommen_m_eg: float,
    grundsicherung__hilfe_zum_lebensunterhalt__überschusseinkommen_m_eg: float,
    vermögensgrenze_unterschritten_eg: bool,
) -> float:
    """Grundsicherung im Alter per person using the Verhältnislösung.

    Each person's income covers their own Bedarf first ('Vertikalmethode'). Only the
    Überschuss is distributed proportionally to the individueller Restbedarf of the
    hilfebedürftigen members.

    Reference: §19 Abs. 2 Satz 1 i.V.m. §43 Abs. 1 SGB XII, §27 Abs. 2 SGB XII
    """
    # TODO (@MImmesberger): Grundsicherung bei Erwerbsminderung (§41 Abs. 3 SGB XII) is
    # not yet implemented. Persons who are dauerhaft voll erwerbsgemindert should also
    # be eligible for this benefit, independently of the Regelaltersgrenze.
    # https://github.com/ttsim-dev/gettsim/issues/1145
    total_income_m_eg = (
        einkommen_zur_verteilung_m_eg
        + bürgergeld__überschusseinkommen_m_eg
        + grundsicherung__hilfe_zum_lebensunterhalt__überschusseinkommen_m_eg
    )
    anspruch_m_eg = max(0.0, bedarf_m_eg - total_income_m_eg)

    if individueller_restbedarf_m_eg == 0.0 or not vermögensgrenze_unterschritten_eg:
        return 0.0
    else:
        return (
            individueller_restbedarf_m / individueller_restbedarf_m_eg
        ) * anspruch_m_eg


@policy_function(start_date="2005-01-01")
def individueller_restbedarf_m(
    bedarf_m: float,
    einkommen_zur_verteilung_m: float,
) -> float:
    """Remaining need after own income (§19 Abs. 2 i.V.m. §43 Abs. 1 SGB XII).

    In the SGB XII Verhältnislösung, each person's income covers their own Bedarf
    first ('Vertikalmethode').
    """
    return max(0.0, bedarf_m - einkommen_zur_verteilung_m)


@policy_function(end_date="2022-12-31", leaf_name="bedarf_m")
def bedarf_m_bis_2022(
    arbeitslosengeld_2__regelbedarf_m: float,
    mehrbedarf_schwerbehinderung_g_m: float,
    sozialversicherung__rente__altersrente__hat_regelaltersgrenze_erreicht: bool,
) -> float:
    """Total Bedarf for Grundsicherung im Alter (§42 SGB XII)."""
    # TODO (@MImmesberger): Grundsicherung bei Erwerbsminderung (§41 Abs. 3 SGB XII) is
    # not yet implemented. Persons who are dauerhaft voll erwerbsgemindert should also
    # be eligible for this benefit, independently of the Regelaltersgrenze.
    # https://github.com/ttsim-dev/gettsim/issues/1145
    if not sozialversicherung__rente__altersrente__hat_regelaltersgrenze_erreicht:
        # Bedarf not considered for Grunds. im Alter ('Vertikalmethode') because
        # eligible for different program.
        return 0.0
    else:
        return arbeitslosengeld_2__regelbedarf_m + mehrbedarf_schwerbehinderung_g_m


@policy_function(start_date="2023-01-01", leaf_name="bedarf_m")
def bedarf_m_ab_2023(
    bürgergeld__regelbedarf_m: float,
    mehrbedarf_schwerbehinderung_g_m: float,
    sozialversicherung__rente__altersrente__hat_regelaltersgrenze_erreicht: bool,
) -> float:
    """Total Bedarf for Grundsicherung im Alter (§42 SGB XII)."""
    # TODO (@MImmesberger): Grundsicherung bei Erwerbsminderung (§41 Abs. 3 SGB XII) is
    # not yet implemented. Persons who are dauerhaft voll erwerbsgemindert should also
    # be eligible for this benefit, independently of the Regelaltersgrenze.
    # https://github.com/ttsim-dev/gettsim/issues/1145
    if not sozialversicherung__rente__altersrente__hat_regelaltersgrenze_erreicht:
        # Bedarf not considered for Grunds. im Alter ('Vertikalmethode') because
        # eligible for different program.
        return 0.0
    else:
        return bürgergeld__regelbedarf_m + mehrbedarf_schwerbehinderung_g_m


@policy_function(start_date="2005-01-01")
def einkommen_zur_verteilung_m(
    einkommen_m: float,
    sozialversicherung__rente__altersrente__hat_regelaltersgrenze_erreicht: bool,
) -> float:
    """Total countable SGB XII income (§82 ff. SGB XII).

    Returns 0 for persons who have not reached the Regelaltersgrenze.
    """
    if not sozialversicherung__rente__altersrente__hat_regelaltersgrenze_erreicht:
        return 0.0
    else:
        return einkommen_m


@policy_function(start_date="2005-01-01")
def überschusseinkommen_m_eg(
    einkommen_zur_verteilung_m_eg: float,
    bedarf_m_eg: float,
) -> float:
    """Net EG excess after internal Verhältnislösung redistribution.

    Only the EG-level surplus (total income > total Bedarf) flows to the SGB II
    partner.

    Reference: BSG B 14 AS 89/20 R
    """
    return max(0.0, einkommen_zur_verteilung_m_eg - bedarf_m_eg)


@policy_function(end_date="2010-12-31", leaf_name="mehrbedarf_schwerbehinderung_g_m")
def mehrbedarf_schwerbehinderung_g_m_vor_2011(
    schwerbehindert_grad_g: bool,
    familie__anzahl_erwachsene_eg: int,
    arbeitslosengeld_2__regelsatz_anteilsbasiert: RegelsatzAnteilsbasiert,
    mehrbedarf_bei_schwerbehinderungsgrad_g: float,
) -> float:
    """Additional allowance for individuals with disabled person's pass G."""
    if (schwerbehindert_grad_g) and (familie__anzahl_erwachsene_eg == 1):
        out = (
            arbeitslosengeld_2__regelsatz_anteilsbasiert.basissatz
            * mehrbedarf_bei_schwerbehinderungsgrad_g
        )
    elif (schwerbehindert_grad_g) and (familie__anzahl_erwachsene_eg > 1):
        out = (
            arbeitslosengeld_2__regelsatz_anteilsbasiert.basissatz
            * arbeitslosengeld_2__regelsatz_anteilsbasiert.erwachsen.je_erwachsener_ab_drei_erwachsene
            * mehrbedarf_bei_schwerbehinderungsgrad_g
        )
    else:
        out = 0.0

    return out


@policy_function(start_date="2011-01-01", leaf_name="mehrbedarf_schwerbehinderung_g_m")
def mehrbedarf_schwerbehinderung_g_m_ab_2011(
    schwerbehindert_grad_g: bool,
    familie__anzahl_erwachsene_eg: int,
    grundsicherung__regelbedarfsstufen: Regelbedarfsstufen,
    mehrbedarf_bei_schwerbehinderungsgrad_g: float,
) -> float:
    """Additional allowance for individuals with disabled person's pass G.

    Mehrbedarf is based on Regelbedarfsstufen starting in 2011 (via Gesetz vom
    24.03.2011 - BGBl. I 2011, Nr. 12 vom 29.03.2011, S. 453).
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
def vermögensgrenze_unterschritten_eg(
    vermögen_eg: float,
    vermögensfreibetrag_eg: float,
) -> bool:
    """Wealth is below the eligibility threshold (§ 90 SGB XII)."""
    return vermögen_eg < vermögensfreibetrag_eg


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


@policy_function(start_date="2005-01-01")
def hat_gesamteinkommen_über_kindeseinkommensgrenze(
    einkommensteuer__gesamteinkommen_y: float,
    einkommensgrenze_kinder: float,
) -> bool:
    """Whether a person's Gesamteinkommen exceeds the children's income threshold.

    Used to determine if a child's income excludes a parent from Grundsicherung im
    Alter.

    Reference: § 43 SGB XII (BGBl. I 2003 S. 3022)
    """
    return einkommensteuer__gesamteinkommen_y >= einkommensgrenze_kinder


@agg_by_p_id_function(agg_type=AggType.SUM)
def anzahl_kinder_mit_einkommen_über_einkommensgrenze_über_elternteil_1(
    hat_gesamteinkommen_über_kindeseinkommensgrenze: bool,
    familie__p_id_elternteil_1: int,
    p_id: int,
) -> int:
    pass


@agg_by_p_id_function(agg_type=AggType.SUM)
def anzahl_kinder_mit_einkommen_über_einkommensgrenze_über_elternteil_2(
    hat_gesamteinkommen_über_kindeseinkommensgrenze: bool,
    familie__p_id_elternteil_2: int,
    p_id: int,
) -> int:
    pass


@policy_function(start_date="2005-01-01")
def hat_kind_mit_einkommen_über_einkommensgrenze(
    anzahl_kinder_mit_einkommen_über_einkommensgrenze_über_elternteil_1: int,
    anzahl_kinder_mit_einkommen_über_einkommensgrenze_über_elternteil_2: int,
) -> bool:
    """Whether any first-degree child has income above the threshold.

    Both parent pointers are checked because a child may point to either parent via
    p_id_elternteil_1 or p_id_elternteil_2.

    Reference: § 43 SGB XII (BGBl. I 2003 S. 3022)
    """
    return (
        anzahl_kinder_mit_einkommen_über_einkommensgrenze_über_elternteil_1
        + anzahl_kinder_mit_einkommen_über_einkommensgrenze_über_elternteil_2
    ) > 0
