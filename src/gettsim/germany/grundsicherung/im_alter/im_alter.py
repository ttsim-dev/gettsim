"""Grundsicherung im Alter."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gettsim.germany.arbeitslosengeld_2.regelbedarf import (
        Regelbedarfsstufen,
    )

from gettsim.tt import policy_function


@policy_function(end_date="2022-12-31", leaf_name="betrag_m_sg")
def betrag_m_sg_bis_2022(
    arbeitslosengeld_2__regelbedarf_m_bg: float,
    mehrbedarf_schwerbehinderung_g_m_sg: float,
    kindergeld__betrag_m_sg: float,
    unterhalt__tatsächlich_erhaltener_betrag_m_sg: float,
    unterhaltsvorschuss__betrag_m_sg: float,
    einkommen_m_sg: float,
    volljährige_alle_rentenbezieher_hh: bool,
    vermögen_sg: float,
    vermögensfreibetrag_sg: float,
    familie__anzahl_kinder_sg: int,
    familie__anzahl_personen_sg: int,
) -> float:
    """Calculate Grundsicherung im Alter on Sozialhilfegemeinschaft level.

    # ToDo: There is no check for Wohngeld included as Wohngeld is
    # ToDo: currently not implemented for retirees.

    """
    # TODO(@ChristianZimpelmann): Treatment of Bedarfsgemeinschaften with both retirees
    # and unemployed job seekers probably incorrect
    # https://github.com/ttsim-dev/gettsim/issues/703

    # TODO(@MImmesberger): Check which variable is the correct Regelbedarf in place of
    # `arbeitslosengeld_2__regelbedarf_m_bg`
    # https://github.com/ttsim-dev/gettsim/issues/702

    # TODO (@MImmesberger): Remove `familie__anzahl_kinder_sg ==
    # familie__anzahl_personen_sg` condition once
    # `volljährige_alle_rentenbezieher_hh`` is replaced by a more accurate
    # variable.
    # https://github.com/ttsim-dev/gettsim/issues/696

    # Wealth check
    # Only pay Grundsicherung im Alter if all adults are retired (see docstring)
    if (
        (vermögen_sg >= vermögensfreibetrag_sg)
        or (not volljährige_alle_rentenbezieher_hh)
        or (familie__anzahl_kinder_sg == familie__anzahl_personen_sg)
    ):
        out = 0.0
    else:
        # Subtract income
        out = (
            arbeitslosengeld_2__regelbedarf_m_bg
            + mehrbedarf_schwerbehinderung_g_m_sg
            - einkommen_m_sg
            - unterhalt__tatsächlich_erhaltener_betrag_m_sg
            - unterhaltsvorschuss__betrag_m_sg
            - kindergeld__betrag_m_sg
        )

    return max(out, 0.0)


@policy_function(start_date="2023-01-01", leaf_name="betrag_m_sg")
def betrag_m_sg_ab_2023(
    bürgergeld__regelbedarf_m_bg: float,
    mehrbedarf_schwerbehinderung_g_m_sg: float,
    kindergeld__betrag_m_sg: float,
    unterhalt__tatsächlich_erhaltener_betrag_m_sg: float,
    unterhaltsvorschuss__betrag_m_sg: float,
    einkommen_m_sg: float,
    volljährige_alle_rentenbezieher_hh: bool,
    vermögen_sg: float,
    vermögensfreibetrag_sg: float,
    familie__anzahl_kinder_sg: int,
    familie__anzahl_personen_sg: int,
) -> float:
    """Calculate Grundsicherung im Alter on Sozialhilfegemeinschaft level.

    # ToDo: There is no check for Wohngeld included as Wohngeld is
    # ToDo: currently not implemented for retirees.

    """
    # TODO(@ChristianZimpelmann): Treatment of Bedarfsgemeinschaften with both retirees
    # and unemployed job seekers probably incorrect
    # https://github.com/ttsim-dev/gettsim/issues/703

    # TODO(@MImmesberger): Check which variable is the correct Regelbedarf in place of
    # `bürgergeld__regelbedarf_m_bg`
    # https://github.com/ttsim-dev/gettsim/issues/702

    # TODO (@MImmesberger): Remove `familie__anzahl_kinder_sg ==
    # familie__anzahl_personen_sg` condition once
    # `volljährige_alle_rentenbezieher_hh`` is replaced by a more accurate
    # variable.
    # https://github.com/ttsim-dev/gettsim/issues/696

    # Wealth check
    # Only pay Grundsicherung im Alter if all adults are retired (see docstring)
    if (
        (vermögen_sg >= vermögensfreibetrag_sg)
        or (not volljährige_alle_rentenbezieher_hh)
        or (familie__anzahl_kinder_sg == familie__anzahl_personen_sg)
    ):
        out = 0.0
    else:
        # Subtract income
        out = (
            bürgergeld__regelbedarf_m_bg
            + mehrbedarf_schwerbehinderung_g_m_sg
            - einkommen_m_sg
            - unterhalt__tatsächlich_erhaltener_betrag_m_sg
            - unterhaltsvorschuss__betrag_m_sg
            - kindergeld__betrag_m_sg
        )

    return max(out, 0.0)


@policy_function(start_date="2011-01-01")
def mehrbedarf_schwerbehinderung_g_m(
    schwerbehindert_grad_g: bool,
    familie__anzahl_erwachsene_sg: int,
    mehrbedarf_bei_schwerbehinderungsgrad_g: float,
    grundsicherung__regelbedarfsstufen: Regelbedarfsstufen,
) -> float:
    """Calculate additional allowance for individuals with disabled person's pass G."""
    mehrbedarf_single = (
        grundsicherung__regelbedarfsstufen.rbs_1
    ) * mehrbedarf_bei_schwerbehinderungsgrad_g
    mehrbedarf_in_couple = (
        grundsicherung__regelbedarfsstufen.rbs_2
    ) * mehrbedarf_bei_schwerbehinderungsgrad_g

    if (schwerbehindert_grad_g) and (familie__anzahl_erwachsene_sg == 1):
        out = mehrbedarf_single
    elif (schwerbehindert_grad_g) and (familie__anzahl_erwachsene_sg > 1):
        out = mehrbedarf_in_couple
    else:
        out = 0.0

    return out


@policy_function(start_date="2005-01-01")
def vermögensfreibetrag_sg(
    familie__anzahl_kinder_sg: int,
    familie__anzahl_erwachsene_sg: int,
    parameter_vermögensfreibetrag: dict[str, float],
) -> float:
    """Calculate wealth not considered for Grundsicherung im Alter on
    Sozialhilfegemeinschaft level.
    """
    return (
        parameter_vermögensfreibetrag["erwachsene"] * familie__anzahl_erwachsene_sg
        + parameter_vermögensfreibetrag["kinder"] * familie__anzahl_kinder_sg
    )
