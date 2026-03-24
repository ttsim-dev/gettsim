"""Bürgergeld."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function(start_date="2023-01-01")
def betrag_m(
    anspruchshöhe_nach_bedarfsanteil_m: float,
    anspruchshöhe_nach_vertikalmethode_m: float,
    ist_gemischte_bg: bool,
    über_regelaltersgrenze: bool,
    vorrangprüfungen__wohngeld_kinderzuschlag_vorrangig_oder_günstiger: bool,
) -> float:
    """Final monthly Bürgergeld benefit per person.

    Persons past the Regelaltersgrenze receive Grundsicherung im Alter (SGB XII) instead.
    In a gemischte BG, the vertical method is used; otherwise the horizontal method.

    Reference: § 19 Abs. 1 Satz 2 SGB II, § 7 Abs. 3 SGB II
    """
    if (
        über_regelaltersgrenze
        or vorrangprüfungen__wohngeld_kinderzuschlag_vorrangig_oder_günstiger
    ):
        out = 0.0
    elif ist_gemischte_bg:
        out = anspruchshöhe_nach_vertikalmethode_m
    else:
        out = anspruchshöhe_nach_bedarfsanteil_m

    return out


@policy_function(start_date="2023-01-01")
def anspruchshöhe_nach_bedarfsanteil_m(
    regelbedarf_m: float,
    regelbedarf_m_bg: float,
    anzurechnendes_einkommen_m_bg: float,
    vermögen_bg: float,
    vermögensfreibetrag_bg: float,
) -> float:
    """Individual share of BG entitlement, proportional to Bedarf.

    Horizontal method (Bedarfsanteilsmethode) for normal BGs where all members are
    SGB II eligible.

    Reference: § 9 Abs. 2 Satz 3 SGB II, BSG B 14 AS 55/07 R (18.06.2008)
    """
    anspruch_m_bg = max(0.0, regelbedarf_m_bg - anzurechnendes_einkommen_m_bg)

    if vermögen_bg > vermögensfreibetrag_bg:
        return 0.0
    else:
        return (regelbedarf_m / regelbedarf_m_bg) * anspruch_m_bg


@policy_function(start_date="2023-01-01")
def anspruchshöhe_nach_vertikalmethode_m(
    regelbedarf_m: float,
    anzurechnendes_einkommen_m: float,
    vermögen_bg: float,
    vermögensfreibetrag_bg: float,
) -> float:
    """Individual entitlement using own Bedarf and income only.

    Vertical method for gemischte Bedarfsgemeinschaften where the SGB XII partner's
    needs and income are excluded from the SGB II computation.

    Reference: BSG B 14 AS 89/20 R (11.11.2021)
    """
    if vermögen_bg > vermögensfreibetrag_bg:
        return 0.0
    else:
        return max(0.0, regelbedarf_m - anzurechnendes_einkommen_m)
