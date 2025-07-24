"""Priority and favorability checks of transfers against each other."""

from __future__ import annotations

from gettsim.tt import policy_function


@policy_function()
def wohngeld_kinderzuschlag_vorrangig_oder_günstiger(
    arbeitslosengeld_2__regelbedarf_m_bg: float,
    arbeitslosengeld_2__anzurechnendes_einkommen_m_bg: float,
    kinderzuschlag__anspruchshöhe_m_bg: float,
    wohngeld__anspruchshöhe_m_wthh: float,
) -> bool:
    """
    Wohngeld and Kinderzuschlag has priority or is more favorable than Arbeitslosengeld
    II.

    Note that this check is a simplified version of the actual priority and favorability
    check by assuming that WTHH = BG. In case this is not sufficient for your use case,
    see the more sophisticated implementation in [link eventually].

    Reference: § 19 WoGG Abs. 2 Satz 1 Nr. 1
    """
    return (
        arbeitslosengeld_2__anzurechnendes_einkommen_m_bg
        + wohngeld__anspruchshöhe_m_wthh
        + kinderzuschlag__anspruchshöhe_m_bg
        >= arbeitslosengeld_2__regelbedarf_m_bg
    )
