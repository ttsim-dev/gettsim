from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.tt import policy_function

if TYPE_CHECKING:
    from gettsim.germany.arbeitslosengeld_2.regelbedarf import (
        Regelbedarfsstufen,
    )


@policy_function(end_date="2022-12-31", leaf_name="bedarf_m")
def bedarf_m_bis_2022(
    arbeitslosengeld_2__regelbedarf_m: float,
    mehrbedarf_schwerbehinderung_g_m: float,
) -> float:
    """Individual Bedarf for Grundsicherung im Alter.

    Reference: § 42 SGB XII
    """
    return arbeitslosengeld_2__regelbedarf_m + mehrbedarf_schwerbehinderung_g_m


@policy_function(start_date="2023-01-01", leaf_name="bedarf_m")
def bedarf_m_ab_2023(
    bürgergeld__regelbedarf_m: float,
    mehrbedarf_schwerbehinderung_g_m: float,
) -> float:
    """Individual Bedarf for Grundsicherung im Alter.

    Reference: § 42 SGB XII
    """
    return bürgergeld__regelbedarf_m + mehrbedarf_schwerbehinderung_g_m


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
