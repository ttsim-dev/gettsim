"""Priority and favorability checks of transfers against each other."""

from __future__ import annotations

from gettsim.germany import WARNING_MSG_FOR_GETTSIM_BG_ID_WTHH_ID_ETC
from gettsim.tt import policy_function


@policy_function(
    leaf_name="wohngeld_kinderzuschlag_vorrangig_oder_günstiger",
    end_date="2022-12-31",
    warn_msg_if_included=WARNING_MSG_FOR_GETTSIM_BG_ID_WTHH_ID_ETC,
)
def wohngeld_kinderzuschlag_vorrangig_oder_günstiger_bis_2022(
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


@policy_function(
    leaf_name="wohngeld_kinderzuschlag_vorrangig_oder_günstiger",
    start_date="2023-01-01",
    warn_msg_if_included=WARNING_MSG_FOR_GETTSIM_BG_ID_WTHH_ID_ETC,
)
def wohngeld_kinderzuschlag_vorrangig_oder_günstiger_ab_2023(
    bürgergeld__regelbedarf_m_bg: float,
    bürgergeld__anzurechnendes_einkommen_m_bg: float,
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
        bürgergeld__anzurechnendes_einkommen_m_bg
        + wohngeld__anspruchshöhe_m_wthh
        + kinderzuschlag__anspruchshöhe_m_bg
        >= bürgergeld__regelbedarf_m_bg
    )
