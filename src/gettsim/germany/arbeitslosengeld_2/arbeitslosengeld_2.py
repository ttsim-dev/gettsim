"""Arbeitslosengeld II (unemployment benefit II)."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function(start_date="2005-01-01", end_date="2022-12-31")
def betrag_m_bg(
    anspruchshöhe_m_bg: float,
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
        out = anspruchshöhe_m_bg

    return out


@policy_function(start_date="2005-01-01", end_date="2022-12-31")
def anspruchshöhe_m_bg(
    regelbedarf_m_bg: float,
    anzurechnendes_einkommen_m_bg: float,
    vermögen_bg: float,
    vermögensfreibetrag_bg: float,
) -> float:
    """Potential basic subsistence (after income deduction and wealth check)."""
    if vermögen_bg > vermögensfreibetrag_bg:
        out = 0.0
    else:
        out = max(
            0.0,
            regelbedarf_m_bg - anzurechnendes_einkommen_m_bg,
        )

    return out
