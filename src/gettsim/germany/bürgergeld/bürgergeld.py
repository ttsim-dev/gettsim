"""Bürgergeld."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function(start_date="2023-01-01")
def betrag_m(
    anspruchshöhe_m: float,
    vorrangprüfungen__wohngeld_kinderzuschlag_vorrangig_oder_günstiger: bool,
) -> float:
    """Final monthly Bürgergeld payment per person.

    Reference: §19 Abs. 1 SGB II
    """
    if vorrangprüfungen__wohngeld_kinderzuschlag_vorrangig_oder_günstiger:
        out = 0.0
    else:
        out = anspruchshöhe_m

    return out


@policy_function(start_date="2023-01-01")
def anspruchshöhe_m(
    ungedeckter_bedarf_m: float,
    ungedeckter_bedarf_m_bg: float,
    einkommen_zur_verteilung_m_bg: float,
    grundsicherung__im_alter__überschusseinkommen_m_bg: float,
    vermögen_bg: float,
    vermögensfreibetrag_bg: float,
) -> float:
    """Individual share of BG entitlement using the Bedarfsanteilsmethode.

    In mixed BGs (gemischte Bedarfsgemeinschaften), the SGB XII partner's needs and
    income are excluded from the pool (vertical method, BSG B 14 AS 89/20 R). Their
    excess income above own Bedarf flows into the SGB II income pool.

    Reference: §9 Abs. 2 Satz 3 SGB II
    """
    total_income = (
        einkommen_zur_verteilung_m_bg
        + grundsicherung__im_alter__überschusseinkommen_m_bg
    )
    anspruch_m_bg = max(0.0, ungedeckter_bedarf_m_bg - total_income)

    if ungedeckter_bedarf_m_bg == 0.0 or vermögen_bg > vermögensfreibetrag_bg:
        out = 0.0
    else:
        out = (ungedeckter_bedarf_m / ungedeckter_bedarf_m_bg) * anspruch_m_bg

    return out


@policy_function(start_date="2023-01-01")
def ungedeckter_bedarf_m(
    regelbedarf_m: float,
    anzurechnendes_einkommen_m: float,
    familie__ist_kind_in_bedarfsgemeinschaft: bool,
    hat_regelaltersgrenze_erreicht: bool,
) -> float:
    """Bedarf after netting child's own income. 0 for SGB XII partners.

    In mixed BGs, persons past the Regelaltersgrenze are excluded from the
    Bedarfsanteilsmethode (vertical method, BSG B 14 AS 89/20 R).

    Reference: §9 Abs. 2 Satz 3 SGB II
    """
    if hat_regelaltersgrenze_erreicht:
        out = 0.0
    elif familie__ist_kind_in_bedarfsgemeinschaft:
        out = max(0.0, regelbedarf_m - anzurechnendes_einkommen_m)
    else:
        out = regelbedarf_m

    return out


@policy_function(start_date="2023-01-01")
def einkommen_zur_verteilung_m(
    regelbedarf_m: float,
    anzurechnendes_einkommen_m: float,
    familie__ist_kind_in_bedarfsgemeinschaft: bool,
    hat_regelaltersgrenze_erreicht: bool,
) -> float:
    """Income available for proportional distribution across BG. 0 for SGB XII partners.

    In mixed BGs, persons past the Regelaltersgrenze are excluded from the
    Bedarfsanteilsmethode (vertical method, BSG B 14 AS 89/20 R).

    Reference: §9 Abs. 2 Satz 3 SGB II
    """
    if hat_regelaltersgrenze_erreicht:
        out = 0.0
    elif familie__ist_kind_in_bedarfsgemeinschaft:
        out = max(0.0, anzurechnendes_einkommen_m - regelbedarf_m)
    else:
        out = anzurechnendes_einkommen_m

    return out


@policy_function(start_date="2023-01-01")
def überschusseinkommen_m(
    einkommen_zur_verteilung_m_bg: float,
    ungedeckter_bedarf_m_bg: float,
) -> float:
    """SGB II sub-BG excess income that flows to the SGB XII partner.

    In mixed BGs, if the SGB II members' total income exceeds their total Bedarf, the
    surplus is counted as income for the SGB XII partner's Grundsicherung calculation.

    Reference: BSG B 14 AS 89/20 R
    """
    return max(0.0, einkommen_zur_verteilung_m_bg - ungedeckter_bedarf_m_bg)
