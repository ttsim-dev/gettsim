"""Bürgergeld.

For an explanation of how income is distributed in SGB II and SGB XII see:

Kulle, Thomas: „Der Einkommenseinsatz nach den diversen Berechnungsmethoden im Rahmen
des SGB II und des SGB XII", in: Deutsche Verwaltungspraxis (DVP), 63. Jahrgang, Heft
5/2012, S. 178-188.
"""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, cast_unit, policy_function


@policy_function(start_date="2023-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def betrag_m(
    anspruchshöhe_m: float,
    vorrangprüfungen__wohngeld_kinderzuschlag_vorrangig_oder_günstiger: bool,
) -> float:
    """Final monthly Bürgergeld payment per person.

    Reference: §19 Abs. 1 SGB II
    """
    if vorrangprüfungen__wohngeld_kinderzuschlag_vorrangig_oder_günstiger:
        return 0.0
    else:
        return anspruchshöhe_m


@policy_function(start_date="2023-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def anspruchshöhe_m(
    ungedeckter_bedarf_m: float,
    ungedeckter_bedarf_m_bg: float,
    einkommen_zur_verteilung_m_bg: float,
    grundsicherung__im_alter__überschusseinkommen_m_eg: float,
    vermögen_bg: float,
    vermögensfreibetrag_bg: float,
) -> float:
    """Individual share of BG entitlement using the Bedarfsanteilsmethode.

    In gemischten Bedarfsgemeinschaften, the SGB XII partner's needs and income are
    excluded from the pool ('Vertikalmethode', BSG B 14 AS 89/20 R).

    Reference: §9 Abs. 2 Satz 3 SGB II
    """
    # Deliberate cross-level summation: the EG's Überschusseinkommen is transferred
    # into the BG's income pool, so re-tag it from the EG to the BG level.
    total_income_m_bg = einkommen_zur_verteilung_m_bg + cast_unit(
        grundsicherung__im_alter__überschusseinkommen_m_eg,
        TTSIMUnit.CURRENCY.PER_MONTH.PER_BG,
    )
    anspruch_m_bg = max(0.0, ungedeckter_bedarf_m_bg - total_income_m_bg)

    if ungedeckter_bedarf_m_bg == 0.0 or vermögen_bg > vermögensfreibetrag_bg:
        return 0.0
    else:
        return (ungedeckter_bedarf_m / ungedeckter_bedarf_m_bg) * anspruch_m_bg


@policy_function(start_date="2023-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def ungedeckter_bedarf_m(
    regelbedarf_m: float,
    anzurechnendes_einkommen_m: float,
    familie__ist_kind_in_bedarfsgemeinschaft: bool,
    sozialversicherung__rente__altersrente__hat_regelaltersgrenze_erreicht: bool,
) -> float:
    """Bedarf after netting child's own income.

    In gemischten Bedarfsgemeinschaften, persons past the Regelaltersgrenze are
    excluded from the Bedarfsanteilsmethode ('Vertikalmethode', BSG B 14 AS 89/20 R).

    Reference: §9 Abs. 2 Satz 3 SGB II
    """
    if sozialversicherung__rente__altersrente__hat_regelaltersgrenze_erreicht:
        return 0.0
    elif familie__ist_kind_in_bedarfsgemeinschaft:
        # Children's income is counted against the children's own needs first
        # (vertikal-horizontale Methode).
        return max(0.0, regelbedarf_m - anzurechnendes_einkommen_m)
    else:
        return regelbedarf_m


@policy_function(start_date="2023-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def einkommen_zur_verteilung_m(
    regelbedarf_m: float,
    anzurechnendes_einkommen_m: float,
    familie__ist_kind_in_bedarfsgemeinschaft: bool,
    sozialversicherung__rente__altersrente__hat_regelaltersgrenze_erreicht: bool,
) -> float:
    """Income available for proportional distribution across BG.

    In gemischten Bedarfsgemeinschaften, persons past the Regelaltersgrenze are
    excluded from the Bedarfsanteilsmethode ('Vertikalmethode', BSG B 14 AS 89/20 R).

    Reference: §9 Abs. 2 Satz 3 SGB II
    """
    if sozialversicherung__rente__altersrente__hat_regelaltersgrenze_erreicht:
        return 0.0
    elif familie__ist_kind_in_bedarfsgemeinschaft:
        # Children's income is counted against the children's own needs first. Only the
        # remaining income is counted against the BG's needs (vertikal-horizontale
        # Methode).
        return max(0.0, anzurechnendes_einkommen_m - regelbedarf_m)
    else:
        return anzurechnendes_einkommen_m


@policy_function(start_date="2023-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def überschusseinkommen_m_bg(
    einkommen_zur_verteilung_m_bg: float,
    ungedeckter_bedarf_m_bg: float,
) -> float:
    """SGB II excess income that flows to the SGB XII partner.

    In gemischten Bedarfsgemeinschaften (one partner is SGB II eligible, the other
    one SGB XII), if the SGB II members' total income exceeds their total Bedarf, the
    surplus is counted as income for the SGB XII partner's Grundsicherung calculation.

    Reference: BSG B 14 AS 89/20 R
    """
    return max(0.0, einkommen_zur_verteilung_m_bg - ungedeckter_bedarf_m_bg)
