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
    bedarf_m: float,
    einkommen_zur_verteilung_m: float,
    arbeitslosengeld_2__überschusseinkommen_m_eg: float,
    grundsicherung__hilfe_zum_lebensunterhalt__überschusseinkommen_m_eg: float,
    vermögen_eg: float,
    vermögensfreibetrag_eg: float,
) -> float:
    """Grundsicherung im Alter per person (§41 ff. SGB XII).

    In mixed BGs, the SGB II partner's excess income above their Bedarf is subtracted.

    Reference: §41 Abs. 1 SGB XII, BSG B 14 AS 89/20 R

    # TODO (@MImmesberger): Grundsicherung bei Erwerbsminderung (§41 Abs. 3 SGB XII) is
    # not yet implemented. Persons who are dauerhaft voll erwerbsgemindert should also
    # be eligible for this benefit, independently of the Regelaltersgrenze.
    # https://github.com/ttsim-dev/gettsim/issues/1145
    """
    if vermögen_eg >= vermögensfreibetrag_eg:
        return 0.0
    else:
        return max(
            0.0,
            bedarf_m
            - einkommen_zur_verteilung_m
            - arbeitslosengeld_2__überschusseinkommen_m_eg
            - grundsicherung__hilfe_zum_lebensunterhalt__überschusseinkommen_m_eg,
        )


@policy_function(start_date="2023-01-01", leaf_name="betrag_m")
def betrag_m_ab_2023(
    bedarf_m: float,
    einkommen_zur_verteilung_m: float,
    bürgergeld__überschusseinkommen_m_eg: float,
    grundsicherung__hilfe_zum_lebensunterhalt__überschusseinkommen_m_eg: float,
    vermögen_eg: float,
    vermögensfreibetrag_eg: float,
) -> float:
    """Grundsicherung im Alter per person (§41 ff. SGB XII).

    In mixed BGs, the SGB II partner's excess income above their Bedarf is subtracted.

    Reference: §41 Abs. 1 SGB XII, BSG B 14 AS 89/20 R

    # TODO (@MImmesberger): Grundsicherung bei Erwerbsminderung (§41 Abs. 3 SGB XII) is
    # not yet implemented. Persons who are dauerhaft voll erwerbsgemindert should also be
    # eligible for this benefit, independently of the Regelaltersgrenze.
    # https://github.com/ttsim-dev/gettsim/issues/1145
    """
    if vermögen_eg >= vermögensfreibetrag_eg:
        return 0.0
    else:
        return max(
            0.0,
            bedarf_m
            - einkommen_zur_verteilung_m
            - bürgergeld__überschusseinkommen_m_eg
            - grundsicherung__hilfe_zum_lebensunterhalt__überschusseinkommen_m_eg,
        )


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
def überschusseinkommen_m(
    einkommen_zur_verteilung_m: float,
    bedarf_m: float,
) -> float:
    """Excess SGB XII income above own Bedarf, flowing to the SGB II partner.

    Reference: BSG B 14 AS 89/20 R
    """
    return max(0.0, einkommen_zur_verteilung_m - bedarf_m)


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
