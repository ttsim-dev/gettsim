"""Grundsicherung im Alter."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function(start_date="2005-01-01")
def betrag_m(
    anspruchshöhe_nach_bedarfsanteil_m: float,
    anspruchshöhe_nach_vertikalmethode_m: float,
    ist_gemischte_bg: bool,
    über_regelaltersgrenze: bool,
) -> float:
    """Final monthly Grundsicherung benefit per person.

    Eligible persons are those who have reached the Regelaltersgrenze (§ 41 Abs. 1 SGB
    XII). In a gemischte BG, the vertical method is used; otherwise the horizontal
    method.
    """
    if not über_regelaltersgrenze:
        return 0.0
    elif ist_gemischte_bg:
        return anspruchshöhe_nach_vertikalmethode_m
    else:
        return anspruchshöhe_nach_bedarfsanteil_m


@policy_function(start_date="2005-01-01")
def anspruchshöhe_nach_bedarfsanteil_m(
    bedarf_m: float,
    bedarf_m_eg: float,
    einkommen_m_eg: float,
    kindergeld__betrag_m_eg: float,
    unterhalt__tatsächlich_erhaltener_betrag_m_eg: float,
    unterhaltsvorschuss__betrag_m_eg: float,
    vermögen_eg: float,
    vermögensfreibetrag_eg: float,
) -> float:
    """Individual share of EG entitlement, proportional to Bedarf.

    Horizontal method for EGs without members eligible for SGB II.

    Reference: § 41 ff. SGB XII
    """
    anspruch_m_eg = max(
        0.0,
        bedarf_m_eg
        - einkommen_m_eg
        - unterhalt__tatsächlich_erhaltener_betrag_m_eg
        - unterhaltsvorschuss__betrag_m_eg
        - kindergeld__betrag_m_eg,
    )

    if vermögen_eg >= vermögensfreibetrag_eg:
        return 0.0
    else:
        return (bedarf_m / bedarf_m_eg) * anspruch_m_eg


@policy_function(start_date="2005-01-01")
def anspruchshöhe_nach_vertikalmethode_m(
    bedarf_m: float,
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
        return 0.0
    else:
        return max(
            0.0,
            bedarf_m
            - einkommen_m
            - unterhalt__tatsächlich_erhaltener_betrag_m
            - unterhaltsvorschuss__betrag_m
            - kindergeld__betrag_m,
        )


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
