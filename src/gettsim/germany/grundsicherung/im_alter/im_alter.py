"""Grundsicherung im Alter."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gettsim.germany.arbeitslosengeld_2.regelbedarf import (
        Regelbedarfsstufen,
    )

from gettsim.tt import policy_function


@policy_function(end_date="2022-12-31", leaf_name="betrag_m_eg")
def betrag_m_eg_bis_2022(
    arbeitslosengeld_2__regelbedarf_m_bg: float,
    mehrbedarf_schwerbehinderung_g_m_eg: float,
    kindergeld__betrag_m_eg: float,
    unterhalt__tatsächlich_erhaltener_betrag_m_eg: float,
    unterhaltsvorschuss__betrag_m_eg: float,
    einkommen_m_eg: float,
    volljährige_alle_rentenbezieher_hh: bool,
    vermögen_eg: float,
    vermögensfreibetrag_eg: float,
    familie__anzahl_kinder_eg: int,
    familie__anzahl_personen_eg: int,
) -> float:
    """Calculate Grundsicherung im Alter on household level.

    # ToDo: There is no check for Wohngeld included as Wohngeld is
    # ToDo: currently not implemented for retirees.

    """
    # TODO(@ChristianZimpelmann): Treatment of Bedarfsgemeinschaften with both retirees
    # and unemployed job seekers probably incorrect
    # https://github.com/ttsim-dev/gettsim/issues/703

    # TODO(@MImmesberger): Check which variable is the correct Regelbedarf in place of
    # `arbeitslosengeld_2__regelbedarf_m_bg`
    # https://github.com/ttsim-dev/gettsim/issues/702

    # TODO (@MImmesberger): Remove `familie__anzahl_kinder_eg ==
    # familie__anzahl_personen_eg` condition once
    # `volljährige_alle_rentenbezieher_hh`` is replaced by a more accurate
    # variable.
    # https://github.com/ttsim-dev/gettsim/issues/696

    # Wealth check
    # Only pay Grundsicherung im Alter if all adults are retired (see docstring)
    if (
        (vermögen_eg >= vermögensfreibetrag_eg)
        or (not volljährige_alle_rentenbezieher_hh)
        or (familie__anzahl_kinder_eg == familie__anzahl_personen_eg)
    ):
        out = 0.0
    else:
        # Subtract income
        out = (
            arbeitslosengeld_2__regelbedarf_m_bg
            + mehrbedarf_schwerbehinderung_g_m_eg
            - einkommen_m_eg
            - unterhalt__tatsächlich_erhaltener_betrag_m_eg
            - unterhaltsvorschuss__betrag_m_eg
            - kindergeld__betrag_m_eg
        )

    return max(out, 0.0)


@policy_function(start_date="2023-01-01", leaf_name="betrag_m_eg")
def betrag_m_eg_ab_2023(
    bürgergeld__regelbedarf_m_bg: float,
    mehrbedarf_schwerbehinderung_g_m_eg: float,
    kindergeld__betrag_m_eg: float,
    unterhalt__tatsächlich_erhaltener_betrag_m_eg: float,
    unterhaltsvorschuss__betrag_m_eg: float,
    einkommen_m_eg: float,
    volljährige_alle_rentenbezieher_hh: bool,
    vermögen_eg: float,
    vermögensfreibetrag_eg: float,
    familie__anzahl_kinder_eg: int,
    familie__anzahl_personen_eg: int,
) -> float:
    """Calculate Grundsicherung im Alter on household level.

    # ToDo: There is no check for Wohngeld included as Wohngeld is
    # ToDo: currently not implemented for retirees.

    """
    # TODO(@ChristianZimpelmann): Treatment of Bedarfsgemeinschaften with both retirees
    # and unemployed job seekers probably incorrect
    # https://github.com/ttsim-dev/gettsim/issues/703

    # TODO(@MImmesberger): Check which variable is the correct Regelbedarf in place of
    # `bürgergeld__regelbedarf_m_bg`
    # https://github.com/ttsim-dev/gettsim/issues/702

    # TODO (@MImmesberger): Remove `familie__anzahl_kinder_eg ==
    # familie__anzahl_personen_eg` condition once
    # `volljährige_alle_rentenbezieher_hh`` is replaced by a more accurate
    # variable.
    # https://github.com/ttsim-dev/gettsim/issues/696

    # Wealth check
    # Only pay Grundsicherung im Alter if all adults are retired (see docstring)
    if (
        (vermögen_eg >= vermögensfreibetrag_eg)
        or (not volljährige_alle_rentenbezieher_hh)
        or (familie__anzahl_kinder_eg == familie__anzahl_personen_eg)
    ):
        out = 0.0
    else:
        # Subtract income
        out = (
            bürgergeld__regelbedarf_m_bg
            + mehrbedarf_schwerbehinderung_g_m_eg
            - einkommen_m_eg
            - unterhalt__tatsächlich_erhaltener_betrag_m_eg
            - unterhaltsvorschuss__betrag_m_eg
            - kindergeld__betrag_m_eg
        )

    return max(out, 0.0)


@policy_function(start_date="2011-01-01")
def mehrbedarf_schwerbehinderung_g_m(
    schwerbehindert_grad_g: bool,
    familie__anzahl_erwachsene_eg: int,
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

    if (schwerbehindert_grad_g) and (familie__anzahl_erwachsene_eg == 1):
        out = mehrbedarf_single
    elif (schwerbehindert_grad_g) and (familie__anzahl_erwachsene_eg > 1):
        out = mehrbedarf_in_couple
    else:
        out = 0.0

    return out


@policy_function(start_date="2005-01-01")
def vermögensfreibetrag_eg(
    familie__anzahl_kinder_fg: int,
    familie__anzahl_erwachsene_fg: int,
    parameter_vermögensfreibetrag: dict[str, float],
) -> float:
    """Calculate wealth not considered for Grundsicherung im Alter on household
    level."""
    return (
        parameter_vermögensfreibetrag["erwachsene"] * familie__anzahl_erwachsene_fg
        + parameter_vermögensfreibetrag["kinder"] * familie__anzahl_kinder_fg
    )
