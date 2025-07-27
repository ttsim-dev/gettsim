"""Priority and favorability checks of transfers against each other."""

from __future__ import annotations

from gettsim.germany import WARNING_MSG_FOR_GETTSIM_BG_ID_WTHH_ID_ETC
from gettsim.tt import policy_function


@policy_function(warn_msg_if_included=WARNING_MSG_FOR_GETTSIM_BG_ID_WTHH_ID_ETC)
def wohngeld_kinderzuschlag_vorrangig_oder_günstiger(
    arbeitslosengeld_2__regelbedarf_m_bg: float,
    arbeitslosengeld_2__anzurechnendes_einkommen_m_bg: float,
    kinderzuschlag__anspruchshöhe_m_bg: float,
    wohngeld__anspruchshöhe_m_wthh: float,
) -> bool:
    """
    Wohngeld and Kinderzuschlag has priority or is more favorable than Arbeitslosengeld
    II.

    Note that this check assumes WTHH=BG; it will not work in more complex situations.
    When calculating `wthh_id` and `bg_id` using the serious implementation in [link],
    you will need to replace this function, too.
    """
    return (
        arbeitslosengeld_2__anzurechnendes_einkommen_m_bg
        + wohngeld__anspruchshöhe_m_wthh
        + kinderzuschlag__anspruchshöhe_m_bg
        >= arbeitslosengeld_2__regelbedarf_m_bg
    )
