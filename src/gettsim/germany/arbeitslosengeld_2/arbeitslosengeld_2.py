"""Arbeitslosengeld II (unemployment benefit II)."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function(start_date="2005-01-01", end_date="2022-12-31")
def betrag_m(
    anspruchshöhe_m: float,
    vorrangprüfungen__wohngeld_kinderzuschlag_vorrangig_oder_günstiger: bool,
    volljährige_alle_rentenbezieher_hh: bool,
) -> float:
    """Final monthly subsistence payment on household level."""
    # TODO (@MImmesberger): No interaction between Wohngeld/ALG2 and Grundsicherung im
    # Alter (SGB XII) is implemented yet. We assume for now that households with only
    # retirees are eligible for Grundsicherung im Alter but not for ALG2/Wohngeld. All
    # other households are not eligible for SGB XII, but SGB II / Wohngeld. Once this is
    # resolved, remove the `volljährige_alle_rentenbezieher_hh` condition.
    # https://github.com/ttsim-dev/gettsim/issues/703
    if (
        vorrangprüfungen__wohngeld_kinderzuschlag_vorrangig_oder_günstiger
        or volljährige_alle_rentenbezieher_hh
    ):
        out = 0.0
    else:
        out = anspruchshöhe_m

    return out


@policy_function(start_date="2005-01-01", end_date="2022-12-31")
def anspruchshöhe_m(
    ungedeckter_bedarf_m: float,
    ungedeckter_bedarf_m_bg: float,
    einkommen_zur_verteilung_m_bg: float,
    vermögen_bg: float,
    vermögensfreibetrag_bg: float,
) -> float:
    """Individual share of BG entitlement using the Bedarfsanteilsmethode.

    Adults' pooled income is distributed proportionally by each person's share of
    ungedeckter Bedarf.

    Reference: § 9 Abs. 2 Satz 3 SGB II, § 11 Abs. 1 Satz 5 SGB II
    """
    anspruch_m_bg = max(0.0, ungedeckter_bedarf_m_bg - einkommen_zur_verteilung_m_bg)

    if vermögen_bg > vermögensfreibetrag_bg:
        return 0.0
    else:
        return (ungedeckter_bedarf_m / ungedeckter_bedarf_m_bg) * anspruch_m_bg


@policy_function(start_date="2005-01-01", end_date="2022-12-31")
def ungedeckter_bedarf_m(
    regelbedarf_m: float,
    anzurechnendes_einkommen_m: float,
    familie__ist_kind_in_bedarfsgemeinschaft: bool,
) -> float:
    """Bedarf after netting child's own income.

    For children in the BG, own income (mainly Kindergeld) is first netted against
    their own Bedarf per § 11 Abs. 1 Satz 5 SGB II. For adults, Bedarf is unchanged —
    their income enters the pool for proportional distribution.

    Reference: § 9 Abs. 2 Satz 3 SGB II
    """
    if familie__ist_kind_in_bedarfsgemeinschaft:
        return max(0.0, regelbedarf_m - anzurechnendes_einkommen_m)
    else:
        return regelbedarf_m


@policy_function(start_date="2005-01-01", end_date="2022-12-31")
def einkommen_zur_verteilung_m(
    regelbedarf_m: float,
    anzurechnendes_einkommen_m: float,
    familie__ist_kind_in_bedarfsgemeinschaft: bool,
) -> float:
    """Income available for proportional distribution across BG.

    Adults' full income enters the pool. For children, only excess income beyond own
    Bedarf enters the pool; the rest was already netted in ungedeckter_bedarf_m.

    Reference: § 9 Abs. 2 Satz 3 SGB II
    """
    if familie__ist_kind_in_bedarfsgemeinschaft:
        return max(0.0, anzurechnendes_einkommen_m - regelbedarf_m)
    else:
        return anzurechnendes_einkommen_m
